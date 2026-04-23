# AWS — Interview Questions

All difficulty levels combined.

---

## Easy

**1. What is an IAM Role and how does it differ from an IAM User?**

An IAM User has long-lived credentials (access keys) permanently tied to a person or service. An IAM Role has no credentials of its own — it is assumed by trusted entities (EC2 instances, Lambda functions, CI/CD pipelines, other accounts) which receive temporary, auto-rotating credentials via STS. Roles are preferred over users for machine identities because credentials expire automatically and cannot be leaked permanently.

**2. What is the difference between EC2, ECS, and EKS?**

- **EC2:** Raw virtual machines — you manage the OS, patching, and everything above the hypervisor.
- **ECS:** AWS-managed container orchestrator. Runs containers on EC2 (you manage nodes) or Fargate (serverless nodes, AWS manages the underlying infrastructure).
- **EKS:** Managed Kubernetes. AWS manages the control plane; you manage worker nodes (EC2 or Fargate). Best when you need Kubernetes-native tooling and portability.

**3. What is an S3 bucket and what makes it durable?**

S3 is AWS's object storage service. Buckets store objects (files) with 11 nines (99.999999999%) durability — achieved by automatically replicating objects across at least three Availability Zones within the region. S3 is the standard backend for Terraform state, artifact storage, logs, and backups.

**4. What is a VPC and why do you need one?**

A Virtual Private Cloud is a logically isolated network within AWS. It provides complete control over IP address ranges, subnets, route tables, internet gateways, and security groups. Resources in a VPC are isolated from other customers' resources by default — you explicitly control what is public, what is private, and how traffic flows between subnets.

**5. What is the difference between a Security Group and a Network ACL?**

- **Security Group:** A stateful firewall at the instance/ENI level. Return traffic for allowed outbound connections is automatically allowed. Rules are allow-only (no explicit deny).
- **Network ACL (NACL):** A stateless firewall at the subnet level. You must explicitly allow both inbound and outbound traffic for each flow. Supports explicit deny rules. Evaluated before Security Groups.

**6. What is CloudWatch and what can you monitor with it?**

CloudWatch is AWS's observability service. It collects metrics (CPU, memory, disk, network) from AWS services automatically, ingests custom application metrics, aggregates logs via CloudWatch Logs, supports alarms and dashboards, and integrates with SNS for alerting and Lambda for automated remediation.

**7. What is AWS Lambda?**

Lambda is AWS's serverless compute service. Code runs in response to events (API Gateway request, S3 object upload, SQS message, scheduled EventBridge rule) without provisioning servers. You pay only for execution time (milliseconds). Cold starts are the main operational consideration for latency-sensitive workloads.

**8. What is Route 53?**

Route 53 is AWS's highly available DNS service. It handles domain registration, DNS resolution, and health-based routing policies: Simple, Weighted (A/B traffic splits), Latency-based (route to lowest-latency region), Failover (active-passive), and Geolocation routing.

---

## Medium

**9. How does IRSA (IAM Roles for Service Accounts) work in EKS?**

IRSA lets Kubernetes pods assume IAM Roles without static credentials. EKS creates an OIDC identity provider for the cluster. You annotate a Kubernetes ServiceAccount with the IAM Role ARN. When the pod starts, the pod receives a projected service account token that the IAM STS service validates against the cluster's OIDC provider, issuing temporary AWS credentials. Credentials are scoped to the pod and rotate automatically — no access keys stored anywhere.

**10. What is the difference between an ALB and an NLB?**

- **ALB (Application Load Balancer):** Layer 7 — understands HTTP/HTTPS. Routes based on path, hostname, headers, query strings. Supports WebSockets. The right choice for microservices and container workloads.
- **NLB (Network Load Balancer):** Layer 4 — routes TCP/UDP by IP and port. Extremely low latency and handles millions of requests per second. Used for non-HTTP traffic or when preserving client IPs is required.

**11. How do you manage secrets in AWS-native pipelines?**

Use AWS Secrets Manager or AWS Systems Manager Parameter Store (SecureString type). CI/CD pipelines retrieve secrets at runtime using the AWS SDK or CLI with an IAM Role — no secrets stored in code or environment variables. For cross-account access, a resource-based policy on the secret allows a specific IAM Role from another account. Secrets Manager supports automatic rotation for RDS, Redshift, and custom rotation Lambdas.

**12. What is AWS CDK and how does it differ from CloudFormation?**

CloudFormation uses JSON/YAML templates — declarative but verbose and limited in abstraction. AWS CDK (Cloud Development Kit) lets you define infrastructure using real programming languages (TypeScript, Python, Go, Java). CDK synthesizes to CloudFormation, so it benefits from CloudFormation's deployment reliability while enabling reusable constructs, loops, conditions, and unit tests. CDK is preferred for complex infrastructure that benefits from abstraction and testing.

**13. What is Karpenter and how does it improve on the Cluster Autoscaler?**

The Cluster Autoscaler works with pre-defined Auto Scaling Groups and can only scale within the instance types configured in those groups. Karpenter provisions nodes directly via the EC2 Fleet API — it picks the optimal instance type for the workload (based on pod resource requests) from any available family, in any AZ, including Spot. Karpenter also consolidates nodes actively, bin-packing workloads to minimize node count. This reduces cost and improves scaling speed.

**14. What is ECS Fargate and when would you choose it over EC2 launch type?**

Fargate is serverless compute for ECS — AWS manages the underlying hosts, OS patching, and capacity. You define CPU/memory at the task level and pay per second of task execution. Choose Fargate when: you don't want to manage EC2 infrastructure, workloads are variable or bursty, or security isolation per task is required (each Fargate task runs in its own micro-VM). Choose EC2 launch type when you need specific instance types, GPU access, or very high-throughput workloads where EC2 unit economics are better.

**15. How do you implement least-privilege access for a CI/CD pipeline deploying to AWS?**

Use OIDC federation: configure the CI provider (GitHub Actions, GitLab CI) as an OIDC provider in AWS IAM. Create an IAM Role with a trust policy that restricts assumption to the specific repository and branch (via `sub` claim matching). The Role's permission policy grants only the exact permissions the deploy job needs — e.g., `ecr:PutImage` on a specific ECR repo and `ecs:UpdateService` on a specific cluster. No static access keys are stored in the CI system.

**16. What is AWS Systems Manager Session Manager and why use it instead of SSH?**

Session Manager provides shell access to EC2 instances through the AWS console or CLI without opening port 22, without managing SSH keys, and without a bastion host. All sessions are logged to CloudWatch and S3 for audit. IAM controls who can start sessions and on which instances. It's the preferred access method for production instances where direct SSH access creates audit and credential management overhead.

---

## Hard

**17. Design a cost-effective and resilient EKS cluster that primarily uses Spot Instances.**

1. **Diversified node pools:** Use Karpenter with multiple `NodePool` resources targeting diverse instance families (m5, m5a, m5n, c5, c5a) and sizes across all three AZs. Diversification reduces interruption risk — if one instance type's Spot capacity is reclaimed, others are available.
2. **AWS Node Termination Handler:** Deploy as a DaemonSet. It watches for Spot interruption notices from the EC2 metadata service and gracefully cordons and drains the node before the 2-minute reclamation window expires.
3. **Workload design:** Stateless, fault-tolerant workloads (web servers, workers) run on Spot. Stateful workloads (databases, ZooKeeper) use `nodeSelector` or taints to target on-demand node pools.
4. **PodDisruptionBudgets:** Every production Deployment has a PDB ensuring at least one replica is available during node drains.
5. **Baseline on-demand:** Maintain a small on-demand node pool (10-20% of capacity) as a floor so Spot interruptions don't take the cluster below minimum capacity.
6. **Savings Plans:** Purchase Compute Savings Plans covering the on-demand baseline at 30-40% discount.

**18. How do you implement a multi-account AWS organization with security guardrails?**

Multi-account architecture via AWS Organizations:

1. **Account structure:** Separate accounts for each environment (dev, staging, prod) and shared services (network hub, security tooling, artifact repositories). Management account only for billing and Organization policy.
2. **Service Control Policies (SCPs):** Applied at OU level — deny actions like `iam:CreateUser` with access keys, disabling CloudTrail, creating resources outside approved regions, or removing required tags. SCPs are guardrails, not grants.
3. **AWS Control Tower:** Orchestrates multi-account setup, enforces mandatory controls (CloudTrail, Config, GuardDuty), and manages account vending via Account Factory.
4. **Centralized security:** AWS Security Hub aggregates findings across all accounts. GuardDuty and AWS Config rules run in every account, reporting to a central security account.
5. **Cross-account roles:** CI/CD pipelines in a shared tooling account assume deployment roles in target accounts with scoped permissions, without needing credentials in each account.

**19. A production Lambda function is experiencing cold starts affecting P99 latency. How do you diagnose and fix it?**

Diagnosis: CloudWatch X-Ray traces break down invocation time — cold starts appear as `Init Duration` in Lambda logs. Identify frequency and duration of cold starts.

Fixes:
1. **Provisioned Concurrency:** Pre-warms a specified number of execution environments. Cold starts effectively disappear for that concurrency level. Use Application Auto Scaling to adjust provisioned concurrency by time of day.
2. **Memory tuning:** Lambda CPU scales with memory — a Lambda with 512MB often initializes faster than one with 128MB even if memory isn't the bottleneck, because of proportional CPU.
3. **Reduce package size:** Cold start duration correlates with deployment package size. Use Lambda layers for large dependencies, remove unused packages, and use tree-shaking for Node.js.
4. **SnapStart (Java):** For Java Lambdas, SnapStart takes a snapshot after initialization and restores it on subsequent invocations, reducing cold start to milliseconds.
5. **Language choice:** If latency is critical, switch from Java/Python to Node.js/Go which initialize faster.

**20. How do you design a disaster recovery strategy for a multi-region AWS application with RTO < 15 minutes?**

RTO < 15 minutes requires an **active-passive warm standby** or **active-active** pattern:

1. **Data replication:** RDS Multi-AZ for regional HA. For cross-region: Aurora Global Database with sub-second replication — failover promotes the secondary region in < 1 minute. S3 Cross-Region Replication (CRR) for object storage.
2. **Infrastructure as Code:** All infrastructure defined in Terraform/CDK — the secondary region can be fully provisioned in minutes. Maintain the secondary region in a "warm" state with scaled-down compute.
3. **Traffic routing:** Route 53 health checks on primary region endpoints with failover routing policy. When health checks fail, DNS automatically routes to the secondary region within TTL.
4. **Pre-warmed capacity:** Keep EKS nodes and RDS read replicas running in the secondary region (scaled to minimum) to avoid cold provisioning time.
5. **Runbook automation:** EventBridge + Lambda automation to promote RDS replicas, update DNS records, and scale up the secondary cluster — executable in a single CLI command.
6. **Regular DR drills:** Test failover quarterly and measure actual RTO against the target.
