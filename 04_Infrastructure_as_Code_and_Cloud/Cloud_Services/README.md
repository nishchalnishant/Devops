# 4. Cloud Services

This section focuses on mastering major cloud providers (AWS, Azure, GCP), architecting for high availability, and managing infrastructure securely at scale.

***

### 4. Cloud Services

Cloud engineering is the foundational layer upon which modern DevOps operates. It's the transition from managing fragile physical hardware to building software-defined, globally distributed infrastructure.

#### A. Compute Services

* Virtual Machines (EC2 / Azure VMs): The base unit of compute. While containers are the modern standard, VMs are crucial for understanding legacy lift-and-shift, databases, or workloads requiring kernel-level access.
* Auto Scaling (ASG / VMSS): Systems designed to automatically increase or decrease compute capacity based on live traffic metrics (CPU, memory, or custom SLIs).
* Serverless (Lambda / Azure Functions): Event-driven compute where you pay only for the milliseconds your code runs. Ideal for automation glue and event processing.

#### B. Networking (VPC / VNet)

The backbone of cloud security and isolation.
* Subnets: Dividing a large network into smaller, logical segments (e.g., Public subnets for Load Balancers, Private subnets for Databases).
* Routing & NAT: Ensuring instances without public IPs can still pull updates securely via Network Address Translation.
* Security Groups & Network ACLs: Software-defined firewalls acting at the instance level (Stateful) or the subnet level (Stateless).

#### C. Managed Databases & Storage

* Object Storage (S3 / Azure Blob): Infinitely scalable storage for backups, static assets, and Terraform state files.
* Relational Databases (RDS / Azure SQL): Managed instances of PostgreSQL, MySQL, etc., where the cloud provider handles backups, patching, and Multi-AZ failover.
* NoSQL (DynamoDB / CosmosDB): Highly scalable, single-digit millisecond latency databases used for session stores and hyper-scale applications.

#### D. Identity and Access Management (IAM / RBAC)

The true perimeter of cloud security is no longer the network firewall; it is Identity.
* Policies / Roles: Attaching permissions directly to compute instances so they can access databases or storage without hardcoded passwords.
* Least Privilege: The principle of giving an entity exactly the permissions it needs to do its job, and nothing more.

***

This is Section 4: Cloud Services. For a mid-to-senior DevOps/SRE role, you are rarely asked how to "launch an instance." You are asked how to design a Highly Available, Fault-Tolerant, and Cost-Optimized architecture that spans multiple geographic regions.

***

#### 🔹 1. Improved Notes: Cloud Architecture Principles

**The Shared Responsibility Model**
* The cloud provider is responsible for the security *OF* the cloud (physical data centers, hypervisors, networking hardware).
* You are responsible for security *IN* the cloud (OS patching, IAM roles, opening port 22 to the world).

**Availability vs. Fault Tolerance**
* High Availability (HA): The system might experience a brief blip, but it will recover quickly across multiple Availability Zones (AZs).
* Fault Tolerance: Zero downtime. Built with massive redundancy so a failure is completely invisible to the user (much more expensive to build).

**Stateless vs. Stateful**
* SREs love Stateless applications. If an EC2 instance dies, an Auto Scaling group replaces it, and no user data is lost because the session state is stored in an external database (Redis/DynamoDB).

***

#### 🔹 2. Interview View (Q\&A)

Q1: What happens under the hood when you type a URL, but the focus is entirely on Cloud Infrastructure?
* Answer: Route53 (DNS) resolves the domain to an Application Load Balancer (ALB) public IP. The ALB terminates the SSL certificate and securely routes the HTTP request to an ASG of private EC2 instances across multiple AZs. The instance queries a Multi-AZ RDS database securely within the private subnet, returning the data.

Q2: How do you allow a private EC2 instance to download a package from the internet without exposing it to inbound traffic?
* Answer: You place a NAT Gateway (or NAT Gateway instance) in a Public Subnet and update the Private Subnet's Route Table to point `0.0.0.0/0` (internet-bound traffic) to the NAT. This allows outbound traffic but blocks inbound initiation.

Q3: An application's compute costs are spiraling out of control. How do you optimize it?
* Answer: 
  1. Identify idle or oversized resources (Right-sizing).
  2. Implement Auto Scaling to scale down during off-peak hours.
  3. Move stateless, fault-tolerant workloads to Spot Instances (up to 90% cheaper).
  4. Purchase Savings Plans or Reserved Instances for predictable baseline loads.

***

#### 🔹 3. Architecture & Design: Multi-Tier VPC

The "Classic 3-Tier Web Architecture"
* Public Tier: Application Load Balancers, NAT Gateways, Bastion Hosts.
* App/Compute Tier (Private): EC2 Instances / EKS Nodes running the application logic. Placed in multiple Availability Zones.
* Database Tier (Private, deeply isolated): RDS Instances. Security Groups here only allow inbound traffic on port 3306/5432 from the App Tier's Security Group (not an IP range).

Multi-Region Disaster Recovery (DR)
* Active-Active: Both regions serve traffic. Extremely complex (handling DB replication latency).
* Pilot Light: Core DB is constantly replicated to Region B. Compute is scaled down to zero until disaster strikes.

***

#### 🔹 4. Commands & Configs (Cloud CLI)

As a Senior DevOps engineer, you frequently use the CLI for scripting or fast checks.

**AWS CLI: Find untagged instances**
`aws ec2 describe-instances --query "Reservations[*].Instances[?Tags == null].InstanceId" --output text`

**AWS CLI: Assume an IAM Role for cross-account access**
`aws sts assume-role --role-arn arn:aws:iam::1234567890:role/DevOpsRole --role-session-name MySession`

***

#### 🔹 5. Troubleshooting & Debugging

Scenario: You cannot SSH into your EC2 instance in a private subnet.
1. Check Route Table: Does the public subnet housing your Bastion Host have an Internet Gateway attached?
2. Check Security Groups: Does the Bastion SG allow your IP? Does the Private EC2 SG allow inbound port 22 *specifically* from the Bastion SG?
3. Check Network ACLs: Is the subnet's stateless NACL accidentally blocking outbound ephemeral ports (1024-65535)?
4. Are you using Session Manager (SSM) instead? (The modern, highly-secure SRE alternative to SSH bastion hosts).

Scenario: S3 Bucket Access Denied.
1. Check IAM Policies: Does the user/role have `s3:GetObject`?
2. Check Bucket Policies: Is there an explicit `Deny` blocking your IP or user? (Explicit Denys always override Allows).
3. Check Object ACLs: Was the object uploaded by a different account prohibiting access?

***

#### 🔹 6. Production Best Practices

* Infrastructure as Code Only: Disable "ClickOps" for engineers in production. All cloud changes must go through Terraform/CI.
* Mandatory Tagging Policies: Use AWS Config or Azure Policies to enforce tags like `Environment`, `Owner`, and `CostCenter`. Untagged resources are rogue resources.
* Secrets Management: Never store DB passwords in EC2 user data. Use Jenkins/Ansible to inject them at runtime via AWS Secrets Manager or HashiCorp Vault.
* Immutability: Do not SSH into production servers to run `apt-get upgrade`. Bake a new AMI (using Packer), update the Auto Scaling Group Launch Template, and roll the instances automatically.

***

#### 🔹 Cheat Sheet / Quick Revision

| **Concept** | **AWS Equivalent** | **Azure Equivalent** | **SRE Focus** |
| :--- | :--- | :--- | :--- |
| Compute | EC2 | Virtual Machines | Immutable infrastructure, ASGs. |
| Object Storage | S3 | Blob Storage | Logs, Backups, Terraform Remote State. |
| DNS | Route 53 | Azure DNS | Latency/Geo-routing, Health checks. |
| IaC Limit | CloudFormation | ARM Templates | Often bypassed in favor of Terraform. |
| Serverless | Lambda | Azure Functions | Event-driven architecture, low cost. |

***

This is Section 4: Cloud Services. For senior roles, never rattle off definitions. Talk about *why* you choose specific services, focusing heavily on operational overhead and cost optimization.

***

#### 🟢 Easy: Cloud Basics

*Focus: Understanding core cloud concepts.*

1. What is the difference between IaaS, PaaS, and SaaS?
   * *Context:* IaaS (EC2/VMs - you manage the OS), PaaS (RDS/Heroku - you manage the app and data), SaaS (Gmail/Salesforce - you just consume).
2. What is an Availability Zone (AZ) vs. a Region?
   * *Context:* A Region is a physical geographic location (e.g., us-east-1). An AZ is one or more discrete data centers within that region, with redundant power and networking.
3. How do you secure data at rest vs. data in transit?
   * *Context:* At rest: KMS Encryption, encrypted volumes. In transit: HTTPS/TLS, SSL certificates.

***

#### 🟡 Medium: Services, Storage & Networking

*Focus: Connecting resources securely and managing scale.*

1. What is the difference between a Security Group and a Network ACL?
   * *Context:* SGs are tied to instances and are stateful (if you allow inbound, outbound is automatically allowed). NACLs are tied to subnets and are stateless (you must explicitly allow both inbound and outbound).
2. Explain the difference between EBS and S3 (or Azure Disk vs Blob).
   * *Context:* EBS is Block storage attached to a specific instance (OS drives, fast DB volumes). S3 is Object storage accessed via HTTP APIs (images, backups).
3. What is a NAT Gateway and why do private networks need it?
   * *Context:* It allows instances without public IP addresses to access the internet (to download patches, contact GitHub) without being reachable from the outside.

***

#### 🔴 Hard: Architecture, DR & Advanced IAM

*Focus: Multi-region design, complex networking, and strict security.*

1. Describe how you would design a highly available, self-healing web application across 3 Availability Zones.
   * *Context:* Discuss Route 53 -> ALB across 3 AZs -> Target Group tied to an ASG spanning 3 public subnets (or private subnets via NAT) -> Backend RDS Multi-AZ. Include health checks at the ALB level terminating unhealthy instances.
2. How do you implement Cross-Account IAM access?
   * *Context:* Discuss the `sts:AssumeRole` mechanism. Account A creates a Role trusting Account B. A user in Account B calls AssumeRole, receives temporary STS credentials, and acts inside Account A. This is heavily tested for senior DevSecOps.
3. Your database is experiencing extreme read contention during peak hours, crashing the frontend. How do you resolve this at the cloud architecture level?
   * *Context:* 1. Vertical scaling (last resort). 2. Implement Read Replicas (if the app logic can be updated to split reads/writes). 3. Add an in-memory caching layer like ElastiCache (Redis/Memcached) before the RDS instance.
4. Explain the difference between an Application Load Balancer (ALB) and a Network Load Balancer (NLB).
   * *Context:* ALB operates at Layer 7 (HTTP/HTTPS) and can route based on paths (`/api` vs `/web`). NLB operates at Layer 4 (TCP/UDP) and handles millions of requests per second for extreme performance or non-HTTP traffic.

***

#### 💡 Pro-Tip for your Interview

When answering cloud architecture questions, always introduce the "Well-Architected Framework":

* *The SRE Answer:* "When designing this VPC, I looked at it through the lens of Security and Reliability. I opted for 3 AZs instead of 2 to ensure we survive a full AZ failure with only a 33% capacity loss, and I isolated the data layer entirely from public subnets, using Security Group referencing to ensure only the app layer can communicate with the database."
