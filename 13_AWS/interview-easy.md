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

***

