---
description: Easy interview questions for AWS services, IAM, EC2, S3, and core cloud concepts.
---

## Easy

**1. What is the difference between an IAM Role and an IAM User?**

An IAM User is a permanent identity with long-term credentials (access key + secret key) for a specific person or application. An IAM Role is a temporary identity assumed by AWS services, EC2 instances, Lambda functions, or federated users — it provides short-lived credentials rotated automatically. Best practice: use Roles for everything instead of Users with long-term keys. Roles cannot log into the AWS Console directly; they are assumed.

**2. What is the AWS Shared Responsibility Model?**

AWS is responsible for security "of" the cloud — the physical infrastructure, hardware, managed service software (e.g., the RDS database engine), and the hypervisor. The customer is responsible for security "in" the cloud — IAM policies, data encryption, network configuration (Security Groups, NACLs), OS patching on EC2, and application security. The boundary shifts depending on the service: more customer responsibility for EC2, less for managed services like Lambda or RDS.

**3. What is the difference between a Security Group and a Network ACL?**

A Security Group is a stateful firewall at the instance/resource level — if you allow inbound traffic on port 443, the response traffic is automatically allowed. A Network ACL is a stateless firewall at the subnet level — you must explicitly allow both inbound and outbound rules for each traffic direction. Security Groups support allow rules only; NACLs support both allow and deny. Use Security Groups for per-resource rules; NACLs for subnet-wide blocks (e.g., blocking a malicious IP range).

**4. What is an S3 bucket policy vs an S3 ACL?**

A bucket policy is a JSON resource-based policy attached to the bucket that grants permissions to AWS principals (users, roles, services, other accounts). An S3 ACL is the legacy access control mechanism using predefined grants (private, public-read, etc.). AWS recommends disabling ACLs and using bucket policies exclusively for all new buckets. Bucket policies are more expressive — they support conditions (e.g., `aws:SourceIP`, `aws:SecureTransport`).

**5. What is an Availability Zone (AZ) and why deploy across multiple AZs?**

An AZ is an isolated data center (or cluster of data centers) within an AWS Region. Each AZ has independent power, cooling, and networking. Deploying across multiple AZs protects against AZ-level failures (power outage, hardware issues). Most managed AWS services (ALB, RDS Multi-AZ, EKS) distribute across AZs automatically. Rule of thumb: 3+ AZs for production workloads requiring high availability.

**6. What is the difference between horizontal and vertical scaling on AWS?**

Vertical scaling (scale up): increase the size of an existing instance (from `t3.medium` to `m5.xlarge`). Requires downtime and has limits. Horizontal scaling (scale out): add more instances behind a load balancer. Enables high availability and theoretically unlimited capacity. AWS Auto Scaling Groups provide horizontal scaling based on CloudWatch metrics. Stateless applications scale horizontally easily; stateful applications (databases) typically require vertical scaling or specialized solutions (RDS Read Replicas, Aurora).

**7. What is VPC and what problem does it solve?**

A Virtual Private Cloud (VPC) is a logically isolated section of the AWS cloud where you can launch resources in a virtual network you define. It solves the problem of running cloud resources on a flat, public network — VPCs provide private IP address spaces, subnet isolation, route tables, and gateway control. Without VPCs, all resources would be directly internet-facing. A VPC allows you to replicate a traditional data center network topology in the cloud.

**8. What is the difference between a public and private subnet?**

A public subnet has a route to an Internet Gateway (IGW) — resources with public IPs are directly reachable from the internet. A private subnet has no route to an IGW — resources can only communicate within the VPC or reach the internet via a NAT Gateway (outbound only). Rule of thumb: databases and app servers go in private subnets; load balancers go in public subnets.

**9. What are AWS regions and how do you choose one?**

A region is a geographic cluster of data centers (e.g., `us-east-1` in Virginia, `ap-south-1` in Mumbai). Criteria for choosing:
- **Latency:** Choose the region closest to your users.
- **Data residency:** Some regulations (GDPR) require data to stay in specific geographies.
- **Service availability:** Not all AWS services are available in all regions (check the service endpoints page).
- **Cost:** Pricing varies by region — `us-east-1` is often cheapest.
- **Compliance:** FedRAMP requires govcloud regions.

**10. What is CloudWatch and what can it monitor?**

CloudWatch is AWS's native observability service. It collects:
- **Metrics:** CPU usage, network I/O, custom application metrics (via the CloudWatch Agent or PutMetricData API).
- **Logs:** Application logs via CloudWatch Agent, Lambda logs, VPC Flow Logs, ELB access logs.
- **Alarms:** Trigger actions (Auto Scaling, SNS notifications) when metrics cross thresholds.
- **Dashboards:** Visualize metrics and logs in a single view.
- **Events/EventBridge:** React to state changes (EC2 instance stopped, S3 object uploaded) with automated actions.

**11. What is the difference between S3 Standard, S3-IA, and S3 Glacier?**

| Storage Class | Latency | Use Case | Cost (storage) |
|:---|:---|:---|:---|
| S3 Standard | Milliseconds | Frequently accessed data | ~$0.023/GB |
| S3 Standard-IA | Milliseconds | Infrequent access (monthly) | ~$0.0125/GB + retrieval fee |
| S3 One Zone-IA | Milliseconds | Infrequent, can tolerate AZ loss | ~$0.01/GB |
| S3 Glacier Instant | Milliseconds | Archives accessed a few times/year | ~$0.004/GB |
| S3 Glacier Flexible | Minutes-hours | Long-term archives | ~$0.0036/GB |
| S3 Glacier Deep Archive | 12-48 hours | 7-year compliance retention | ~$0.00099/GB |

Use S3 Lifecycle policies to automatically transition objects between classes as they age.

**12. What is EC2 instance metadata and how do you access it?**

EC2 instance metadata is information about a running instance accessible from within the instance at `http://169.254.169.254/latest/meta-data/`. It includes: instance ID, instance type, public/private IP, IAM role credentials (auto-rotated), security groups, and the user-data script. The metadata endpoint is a common target in SSRF (Server-Side Request Forgery) attacks — IMDSv2 requires a session token to mitigate this.
