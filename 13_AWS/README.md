# Cloud Services (AWS)

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
| `interview-easy.md` | Foundational: IAM, EC2, S3, VPC, CloudWatch, SLAs |
| `interview-medium.md` | Intermediate: IRSA, SCP, Transit Gateway, ECS vs EKS, Lambda cold starts |
| `interview-hard.md` | Advanced: multi-account architecture, cost optimization, disaster recovery |
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
