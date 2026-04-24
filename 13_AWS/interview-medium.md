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

