---
description: AWS EKS architecture, ECS vs EKS decision framework, Fargate, node groups, and container orchestration patterns.
---

# AWS — EKS, ECS & Container Orchestration

```
EKS, ECS & Container Orchestration
├── ECS vs EKS Decision Framework
│   ├── ECS: AWS-managed proprietary, low learning curve, AWS-only ecosystem, no control plane fee
│   ├── EKS: AWS-managed Kubernetes, CNCF ecosystem (Helm, ArgoCD, Istio), $0.10/hr control plane
│   ├── Choose ECS: AWS-native team, simple containerization, minimal K8s expertise
│   └── Choose EKS: multi-cloud portability, K8s ecosystem tools, existing expertise
├── EKS Architecture
│   ├── Control Plane (AWS-managed): API Server, etcd (KMS-encrypted), Controller Manager, Scheduler
│   ├── Worker Nodes (your VPC): Managed Node Groups / Self-Managed / Fargate Profiles
│   └── Cross-plane communication: nodes → API server (public endpoint or private via VPC endpoint)
├── EKS Access Control — Two Layers
│   ├── Layer 1 — AWS IAM: eks:DescribeCluster, eks:CreateCluster (who can call AWS API)
│   ├── Layer 2 — Kubernetes RBAC: what the IAM identity can do inside the cluster
│   └── aws-auth ConfigMap: maps IAM roles to K8s RBAC users/groups
├── Node Types
│   ├── Managed Node Groups (recommended): AWS manages EC2 lifecycle, respects PDBs during upgrade
│   ├── Fargate Profiles (serverless): no DaemonSets, no privileged, no hostNetwork, max 4vCPU/30GB
│   └── Self-Managed: full control, full ops burden
├── ECS Architecture
│   ├── Cluster → Service (desired count, LB, auto-scaling) → Tasks (container groups)
│   ├── Launch types: Fargate (serverless) or EC2 (self-managed)
│   ├── Task Definition: networkMode=awsvpc (one ENI per task, own SG)
│   ├── executionRoleArn (ECS agent pulls image, writes logs)
│   └── taskRoleArn (application permissions — S3, DynamoDB, etc.)
├── ECS Networking
│   ├── awsvpc mode: each task gets own ENI + Security Group (preferred in production)
│   ├── bridge mode: shared EC2 host networking (legacy, avoid)
│   └── Secrets: inject from Secrets Manager / SSM via "secrets" in task def (not env vars)
└── Logic & Trickiness Table
    ├── EKS auth: IAM gets you to cluster API; RBAC controls what you can do inside
    ├── aws-auth: edit via eksctl or Terraform aws-auth module (not kubectl manually)
    ├── Fargate: no DaemonSets means no Fluentd/Datadog agent pattern
    ├── EKS upgrades: control plane → add-ons (VPC CNI first) → node groups
    └── ECS secrets: Secrets Manager integration preferred over plaintext env vars
```

## First Principles

AWS is a collection of primitives: compute (EC2/Lambda), storage (S3/EBS), network (VPC), IAM. EKS = Kubernetes control plane managed by AWS. IAM Roles for Service Accounts (IRSA) solves the pod identity problem without long-lived credentials. Multi-account = blast radius control.

## ECS vs EKS — The Decision Framework

| Dimension | ECS | EKS |
|:---|:---|:---|
| **Control Plane** | AWS-managed, opaque | AWS-managed Kubernetes |
| **Learning Curve** | Low (AWS-native) | High (K8s + AWS) |
| **Portability** | AWS-only | Multi-cloud / on-prem |
| **Ecosystem** | AWS ecosystem only | CNCF ecosystem (Helm, Istio, ArgoCD) |
| **Cost** | No control plane fee | $0.10/hr per cluster |
| **Complexity** | Lower | Higher |
| **Best for** | AWS-native shops, simple workloads | Complex orchestration, existing K8s expertise |

> **Senior Insight:** ECS is often the right choice for teams without K8s expertise. EKS adds significant operational complexity — only choose it if you need multi-cloud portability, complex scheduling, or existing K8s tooling.

***

## EKS Architecture

```
AWS-Managed Control Plane (free from you to manage)
    ├── API Server (highly available)
    ├── etcd (AWS-managed, encrypted)
    ├── Controller Manager
    └── Scheduler
            │
            │ ENI-based communication
            ▼
Your AWS Account — Worker Nodes
    ├── Managed Node Group (AWS manages EC2 lifecycle)
    ├── Self-Managed Node Group (you manage EC2)
    └── Fargate Profiles (serverless nodes)
```

### EKS Access Control — The Dual Layer

**Layer 1 — AWS IAM:** Controls who can call the EKS API (`eks:DescribeCluster`, `eks:CreateCluster`).

**Layer 2 — Kubernetes RBAC:** Controls what that IAM identity can do inside the cluster.

```bash
# The aws-auth ConfigMap maps IAM roles to K8s RBAC
kubectl edit configmap aws-auth -n kube-system
```

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: aws-auth
  namespace: kube-system
data:
  mapRoles: |
    - rolearn: arn:aws:iam::ACCOUNT_ID:role/EKSNodeRole
      username: system:node:{{EC2PrivateDNSName}}
      groups:
        - system:bootstrappers
        - system:nodes
    
    - rolearn: arn:aws:iam::ACCOUNT_ID:role/DevTeamRole
      username: dev-team
      groups:
        - dev-readonly     # Custom K8s RBAC group
```

***

## Managed Node Groups vs. Self-Managed vs. Fargate

### Managed Node Groups (Recommended for most cases)
```hcl
resource "aws_eks_node_group" "app" {
  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "app-workers"
  node_role_arn   = aws_iam_role.node_role.arn
  subnet_ids      = var.private_subnet_ids

  scaling_config {
    desired_size = 3
    max_size     = 10
    min_size     = 2
  }

  instance_types = ["m5.xlarge"]
  capacity_type  = "ON_DEMAND"   # or "SPOT" for cost savings

  update_config {
    max_unavailable = 1
  }
}
```

### Fargate Profile (Serverless — no node management)
```hcl
resource "aws_eks_fargate_profile" "api" {
  cluster_name           = aws_eks_cluster.main.name
  fargate_profile_name   = "api-services"
  pod_execution_role_arn = aws_iam_role.fargate_role.arn
  subnet_ids             = var.private_subnet_ids

  selector {
    namespace = "production"
    labels = {
      workload-type = "api"   # Only pods with this label use Fargate
    }
  }
}
```

**Fargate Constraints:**
- No DaemonSets
- No privileged containers
- No `hostNetwork`, `hostPID`, `hostIPC`
- Max 4 vCPU, 30GB RAM per pod

***

## ECS Architecture

```
ECS Cluster
    │
    ├── ECS Service (desired count: 3)
    │       │
    │       ├── Task (container group)
    │       │   ├── Container: api (nginx)
    │       │   └── Container: sidecar (datadog-agent)
    │       ├── Task
    │       └── Task
    │
    ├── Launch Type: Fargate (serverless)  or  EC2 (self-managed)
    └── Load Balancer → Target Group → Tasks
```

### Task Definition

```json
{
  "family": "api-service",
  "networkMode": "awsvpc",     // Each task gets its own ENI
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::ACCOUNT:role/apiTaskRole",
  "containerDefinitions": [{
    "name": "api",
    "image": "my-registry/api:v1.2.3",
    "portMappings": [{"containerPort": 8080}],
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group": "/ecs/api-service",
        "awslogs-region": "us-east-1",
        "awslogs-stream-prefix": "api"
      }
    },
    "secrets": [{
      "name": "DATABASE_URL",
      "valueFrom": "arn:aws:secretsmanager:us-east-1:ACCOUNT:secret:prod/db-url"
    }]
  }]
}
```

***

## Logic & Trickiness Table

| Concept | Common Mistake | Senior Understanding |
|:---|:---|:---|
| **EKS auth** | Confuse IAM with K8s RBAC | Two separate layers; IAM gets you to the cluster, RBAC controls what you can do |
| **aws-auth** | Edit manually | Use `eksctl` or `aws-auth` Terraform module to avoid YAML corruption |
| **Fargate vs managed nodes** | Use Fargate for everything | Fargate has no DaemonSets; not suitable for stateful workloads |
| **ECS networking** | Bridge mode | Always use `awsvpc` in production (each task gets its own ENI + SG) |
| **ECS secrets** | Env vars in task def | Use Secrets Manager integration; secrets are injected at task start |
| **EKS upgrades** | Upgrade control plane only | Must also update node groups, add-ons (CoreDNS, kube-proxy, VPC CNI) to match |

## System Design Perspective

**VPC Peering vs Transit Gateway:** VPC Peering is direct, non-transitive, and suited for 2-5 VPCs with non-overlapping CIDRs. Transit Gateway is a managed cloud router that enables transitive routing, scales to thousands of VPCs, supports VPN and Direct Connect attachments, and allows inter-region peering. Cost: TGW charges per attachment plus per GB processed; use VPC Endpoints alongside TGW to keep S3/DynamoDB traffic off the TGW.

**Identity Federation (OIDC/SAML):** IRSA (IAM Roles for Service Accounts) uses OIDC federation — the EKS cluster's OIDC issuer is registered in IAM, and pods exchange a projected ServiceAccount JWT for temporary STS credentials via sts:AssumeRoleWithWebIdentity. GitHub Actions and GitLab CI use the same pattern to assume IAM roles without storing access keys. SAML 2.0 is used for AWS SSO federation with enterprise IdPs (Okta, Azure AD).

**Cross-Region DR:** Strategy selection depends on RTO/RPO targets. Backup and Restore (hours RTO, cheapest) uses S3 CRR plus RDS snapshots. Pilot Light (30 min RTO) keeps minimal standby infra running. Warm Standby (minutes RTO) runs a reduced-scale active stack. Active-Active (near-zero RTO) uses Route 53 latency routing plus Aurora Global Database with less than 1s replication lag. All strategies require IaC — without it, failover cannot meet aggressive RTOs.

**Cost Allocation Tagging Strategy:** Enforce mandatory tags (Environment, Team, CostCenter, Owner) via AWS Config Rules or SCPs requiring tags on resource creation. Use AWS Cost Explorer grouped by tag to produce per-team cost reports. Activate cost allocation tags in the Billing Console. Use Tag Policies in AWS Organizations to standardize tag key formats across accounts.

**Managed Identity vs Service Principals (AWS context):** IAM Roles are the equivalent of Managed Identities — they provide temporary credentials without stored secrets. Long-term access keys (equivalent to Service Principals with secrets) should only exist for external systems that cannot assume roles. IRSA and ECS task roles are the pod/task-level equivalent of Azure Workload Identity.

**AWS Organizations SCPs vs Azure Policy:** SCPs define the maximum permissions ceiling per OU/account — they cannot grant permissions, act before IAM evaluation, and even the root user cannot exceed them. Azure Policy enforces at the ARM API layer with richer effects (Deny, Audit, DeployIfNotExists, Modify). Both use hierarchical policy inheritance but differ in execution layer: SCPs block at the IAM authorization step; Azure Policy intercepts at the resource provider level and supports auto-remediation.
