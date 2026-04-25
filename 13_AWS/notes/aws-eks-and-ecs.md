---
description: AWS EKS architecture, ECS vs EKS decision framework, Fargate, node groups, and container orchestration patterns.
---

# AWS — EKS, ECS & Container Orchestration

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
