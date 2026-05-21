# Cloud Services (AWS)

```
AWS Cloud Services
├── Core Mental Model
│   ├── Every resource has an ARN (Amazon Resource Name)
│   ├── IAM: Principal + Action + Resource + Condition
│   ├── Everything is a programmable API (CLI/SDK/CloudFormation/Terraform)
│   └── Shared Responsibility: AWS manages "of the cloud", you manage "in the cloud"
├── Identity & Access (IAM)
│   ├── Users (long-term credentials, avoid for applications)
│   ├── Roles (temporary credentials, assumed by services/EC2/Lambda/pods)
│   ├── Policies (identity-based, resource-based, SCPs, permissions boundaries)
│   ├── IRSA (IAM Roles for Service Accounts — OIDC federation for EKS pods)
│   ├── Policy evaluation: Explicit Deny → SCP → Allow → Implicit Deny
│   └── AWS Organizations + SCPs (max permissions ceiling per account/OU)
├── Compute
│   ├── EC2 (VMs: On-Demand / Reserved / Spot / Savings Plans)
│   ├── Lambda (serverless FaaS, cold starts, Provisioned Concurrency)
│   ├── ECS (managed container orchestration, proprietary, Fargate/EC2 launch types)
│   └── EKS (managed Kubernetes, $0.10/hr control plane, IRSA, VPC CNI)
├── Storage
│   ├── S3 (object storage, 11 nines durability, storage classes lifecycle)
│   ├── EBS (block storage, AZ-locked, gp3 default)
│   ├── EFS (managed NFS, multi-AZ)
│   └── S3 Glacier (archive: Instant / Flexible / Deep Archive)
├── Networking
│   ├── VPC (isolated network, CIDR, subnets, route tables)
│   ├── Public subnet (route to IGW) vs Private subnet (route to NAT GW)
│   ├── Security Groups (stateful, instance-level) vs NACLs (stateless, subnet-level)
│   ├── VPC Peering (one-to-one, non-transitive)
│   ├── Transit Gateway (hub-and-spoke, transitive, thousands of VPCs)
│   ├── VPC Endpoints (Gateway: S3/DynamoDB free; Interface: PrivateLink, costs)
│   ├── NAT Gateway (outbound egress from private subnets)
│   ├── ALB (L7, content-based routing) vs NLB (L4, static IPs, extreme throughput)
│   └── Route 53 (DNS, health checks, failover routing)
├── Security
│   ├── IAM policies + SCPs + permissions boundaries
│   ├── CloudTrail (API audit log, immutable)
│   ├── GuardDuty (threat detection, ML-based)
│   ├── AWS Config (resource compliance)
│   ├── Secrets Manager (secret rotation) vs SSM Parameter Store
│   └── IMDSv2 (token-required metadata; blocks SSRF on EC2)
├── Observability
│   ├── CloudWatch (metrics, logs, alarms, dashboards, Events/EventBridge)
│   ├── CloudWatch Logs Insights (query language)
│   ├── X-Ray (distributed tracing)
│   └── Container Insights (EKS/ECS metrics and logs)
├── Multi-Account Architecture
│   ├── AWS Organizations (Management Account → OUs → Member Accounts)
│   ├── Control Tower (landing zone automation)
│   ├── Security OU (Log Archive + Security Tooling accounts)
│   ├── Infrastructure OU (Network + Tooling accounts)
│   └── Workloads OU (Prod OU + Non-Prod OU + Sandbox OU)
├── Disaster Recovery
│   ├── Backup & Restore (RTO hours, lowest cost)
│   ├── Pilot Light (minimal standby, RTO ~30min)
│   ├── Warm Standby (reduced-scale always-on, RTO minutes)
│   └── Active-Active Multi-Region (RTO ~0, highest cost)
└── Cost Management
    ├── Reserved Instances / Savings Plans / Spot Instances
    ├── Karpenter (right-size nodes automatically)
    ├── S3 Lifecycle policies (auto-tier objects to cheaper storage)
    └── VPC Endpoints (eliminate NAT Gateway charges for S3/DynamoDB)
```

## First Principles

AWS is a collection of primitives: compute (EC2/Lambda), storage (S3/EBS), network (VPC), IAM. EKS = Kubernetes control plane managed by AWS. IAM Roles for Service Accounts (IRSA) solves the pod identity problem without long-lived credentials. Multi-account = blast radius control.

Amazon Web Services is the world's leading cloud platform. For DevOps/SRE engineers, AWS is a programmable infrastructure API — every service can be provisioned, configured, and managed through code (CLI, SDKs, CloudFormation, Terraform).

***

## What Is in This Module

| File | Purpose |
|:---|:---|
| `notes/notes.md` | Core services: EC2, S3, VPC, IAM, RDS, EKS |
| `notes/aws-networking.md` | VPC design, subnets, NACLs, Transit Gateway, PrivateLink |
| `notes/aws-iam-and-security.md` | IAM policies, roles, SCPs, security tools (GuardDuty, Inspector) |
| `notes/aws-containers.md` | EKS, ECS, ECR, Fargate, IRSA patterns |
| `notes/aws-serverless.md` | Lambda, API Gateway, EventBridge, Step Functions |
| `cheatsheet.md` | CLI one-liners, service quick reference, IAM policy patterns |
| `tips-and-tricks.md` | NAT Gateway cost traps, IMDSv2, IAM simulator, JMESPath filtering |
| `interview.md` | Consolidated Interview Questions: Easy, Medium, and Hard levels |
| `scenarios.md` | Real-world troubleshooting and architecture design scenarios |

***

## The Mental Model: AWS is an API

```
Everything in AWS is a resource with an ARN (Amazon Resource Name):
  arn:aws:s3:::my-bucket
  arn:aws:iam::123456789:role/my-role
  arn:aws:ec2:us-east-1:123456789:instance/i-abc123

Operations on resources go through IAM (authentication + authorization):
  Principal (who?) + Action (what?) + Resource (on what?) + Condition (when?)
  └── Allow or Deny
```

***

## Key Services by Category

### Compute
| Service | Purpose |
|:---|:---|
| **EC2** | Virtual machines; full OS control |
| **Lambda** | Serverless functions (up to 15 min execution) |
| **ECS** | Docker container orchestration (AWS-native) |
| **EKS** | Managed Kubernetes control plane |
| **Fargate** | Serverless compute for ECS/EKS pods |
| **Batch** | Managed batch computing jobs |

### Storage & Databases
| Service | Purpose |
|:---|:---|
| **S3** | Object storage (11 nines durability, unlimited scale) |
| **EBS** | Block storage attached to EC2 (like a hard drive) |
| **EFS** | Shared file system (NFS, multi-AZ) |
| **RDS** | Managed relational databases (Postgres, MySQL, Aurora) |
| **DynamoDB** | Serverless NoSQL at any scale |
| **ElastiCache** | Managed Redis/Memcached |

### Networking
| Service | Purpose |
|:---|:---|
| **VPC** | Private network; subnets, route tables, security groups |
| **ALB/NLB** | Load balancers (L7 HTTP vs L4 TCP) |
| **Route 53** | DNS and health checking |
| **CloudFront** | CDN and edge caching |
| **Transit Gateway** | Hub-and-spoke multi-VPC connectivity |
| **PrivateLink** | Private connectivity to services (no internet) |

### Security & Identity
| Service | Purpose |
|:---|:---|
| **IAM** | Access control for all AWS resources |
| **AWS Organizations / SCPs** | Multi-account policy governance |
| **Secrets Manager** | Managed secret storage with auto-rotation |
| **KMS** | Key management for encryption at rest |
| **GuardDuty** | Threat detection (anomalous API calls, network patterns) |
| **Security Hub** | Centralized security findings aggregation |

***

## Interview Focus Areas

| Difficulty | Key Topics |
|:---|:---|
| **Easy** | Shared responsibility model, IAM roles vs users, security groups vs NACLs, S3 storage classes, AZs vs Regions, CloudWatch |
| **Medium** | IAM policy evaluation logic, IRSA for EKS, VPC peering vs Transit Gateway, Lambda cold starts, ECS vs EKS, SCPs |
| **Hard** | Multi-account Landing Zone (Control Tower), disaster recovery (RTO/RPO by strategy), cross-region architectures, cost optimization at scale, Well-Architected Framework |

***

## Multi-Account Architecture (Landing Zone)

```
AWS Organizations
├── Root OU
│   ├── Management Account (billing only)
│   ├── Security OU
│   │   ├── Log Archive Account (CloudTrail, Config, Flow Logs)
│   │   └── Security Tooling Account (GuardDuty, SecurityHub aggregator)
│   ├── Infrastructure OU
│   │   ├── Shared Services Account (DNS, artifact registries, Transit Gateway)
│   │   └── Network Account (VPC, Direct Connect, firewall)
│   └── Workloads OU
│       ├── Dev Account
│       ├── Staging Account
│       └── Production Account  ← Strictest SCPs here
```

**Why separate accounts?** Hard blast-radius boundary (IAM in one account cannot affect another), separate billing visibility, separate SCPs, and compliance isolation.

***

## Disaster Recovery Strategies (RTO vs Cost)

| Strategy | RTO | RPO | Cost | Description |
|:---|:---|:---|:---|:---|
| **Backup & Restore** | Hours | Hours | $ | Restore from S3/RDS snapshots |
| **Pilot Light** | Minutes | Minutes | $$ | Core infra always-on; scale out on disaster |
| **Warm Standby** | Seconds-Minutes | Near-zero | $$$ | Reduced capacity always-on in DR region |
| **Multi-Site Active/Active** | Near-zero | Near-zero | $$$$ | Full capacity in both regions; instant failover |

## System Design Perspective

**VPC Peering vs Transit Gateway:** VPC Peering is direct, non-transitive, and suited for 2-5 VPCs with non-overlapping CIDRs. Transit Gateway is a managed cloud router that enables transitive routing, scales to thousands of VPCs, supports VPN and Direct Connect attachments, and allows inter-region peering. Cost: TGW charges per attachment plus per GB processed; use VPC Endpoints alongside TGW to keep S3/DynamoDB traffic off the TGW.

**Identity Federation (OIDC/SAML):** IRSA (IAM Roles for Service Accounts) uses OIDC federation — the EKS cluster's OIDC issuer is registered in IAM, and pods exchange a projected ServiceAccount JWT for temporary STS credentials via sts:AssumeRoleWithWebIdentity. GitHub Actions and GitLab CI use the same pattern to assume IAM roles without storing access keys. SAML 2.0 is used for AWS SSO federation with enterprise IdPs (Okta, Azure AD).

**Cross-Region DR:** Strategy selection depends on RTO/RPO targets. Backup and Restore (hours RTO, cheapest) uses S3 CRR plus RDS snapshots. Pilot Light (30 min RTO) keeps minimal standby infra running. Warm Standby (minutes RTO) runs a reduced-scale active stack. Active-Active (near-zero RTO) uses Route 53 latency routing plus Aurora Global Database with less than 1s replication lag. All strategies require IaC — without it, failover cannot meet aggressive RTOs.

**Cost Allocation Tagging Strategy:** Enforce mandatory tags (Environment, Team, CostCenter, Owner) via AWS Config Rules or SCPs requiring tags on resource creation. Use AWS Cost Explorer grouped by tag to produce per-team cost reports. Activate cost allocation tags in the Billing Console. Use Tag Policies in AWS Organizations to standardize tag key formats across accounts.

**Managed Identity vs Service Principals (AWS context):** IAM Roles are the equivalent of Managed Identities — they provide temporary credentials without stored secrets. Long-term access keys (equivalent to Service Principals with secrets) should only exist for external systems that cannot assume roles. IRSA and ECS task roles are the pod/task-level equivalent of Azure Workload Identity.

**AWS Organizations SCPs vs Azure Policy:** SCPs define the maximum permissions ceiling per OU/account — they cannot grant permissions, act before IAM evaluation, and even the root user cannot exceed them. Azure Policy enforces at the ARM API layer with richer effects (Deny, Audit, DeployIfNotExists, Modify). Both use hierarchical policy inheritance but differ in execution layer: SCPs block at the IAM authorization step; Azure Policy intercepts at the resource provider level and supports auto-remediation.