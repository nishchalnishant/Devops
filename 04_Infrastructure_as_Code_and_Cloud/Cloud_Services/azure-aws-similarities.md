# Azure - AWS similarities

If you already know one cloud provider, the fastest way to prepare for interviews on another provider is to map the same concepts across both platforms.

Here are detailed notes designed to help you translate your Azure knowledge directly to AWS, focusing on the topics a DevOps or SRE engineer would be asked about in an interview.

***

#### ## 🗺️ Azure to AWS Translation Guide for DevOps/SRE

Think of this as a Rosetta Stone for the two biggest cloud platforms. I'll structure this by the core areas you work in, comparing the Azure service you know with its AWS equivalent.

***

#### ## 1. Core Concepts: The Foundation

This is the most important part to get right. It's the basic vocabulary of the cloud platform.

| Azure Service / Concept | AWS Equivalent                           | Key Differences & DevOps/SRE Notes                                                                                                                                                                                                                                                                                                                      |
| ----------------------- | ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Subscription            | AWS Account                              | This is a direct 1:1 mapping. It's the primary boundary for billing and identity.                                                                                                                                                                                                                                                                       |
| Resource Group          | (No Direct Equivalent - Managed by Tags) | 🛑 Critical Interview Point: AWS does not have a mandatory container like a Resource Group. Resources like EC2 instances or S3 buckets exist directly within an Account. You achieve logical grouping and management in AWS by applying Tags (e.g., `Project: A`, `Environment: Prod`). The lifecycle of resources is independent, not tied to a group. |
| Azure AD / RBAC         | AWS IAM (Identity and Access Management) | Both manage user access. IAM consists of Users, Groups, and Roles. Permissions are defined in JSON-based Policies that are attached to these identities. An IAM Role is very similar to a Managed Identity; it's an identity that services (like an EC2 instance or a Lambda function) can "assume" to get temporary credentials.                       |
| Azure Policy            | AWS Organizations SCPs & IAM Policies    | Azure Policy enforces governance rules on resources. The AWS equivalent is a combination of Service Control Policies (SCPs), which act at the organizational (multi-account) level to set guardrails, and fine-grained IAM Policies with `Condition` keys to enforce rules at the resource level.                                                       |
| Management Groups       | AWS Organizations                        | Both are used to group and manage multiple subscriptions/accounts, applying policies and consolidating billing from a central point.                                                                                                                                                                                                                    |

***

#### ## 2. Compute: Running Your Code

| Azure Service / Concept           | AWS Equivalent                         | Key Differences & DevOps/SRE Notes                                                                                                                                                                                                                                                                       |
| --------------------------------- | -------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Virtual Machines (VMs)            | EC2 (Elastic Compute Cloud)            | This is the fundamental IaaS VM service. What you call a VM Image, AWS calls an AMI (Amazon Machine Image). A key interview topic is EC2 purchasing options: On-Demand, Reserved Instances, and especially Spot Instances (interruptible VMs for huge cost savings, great for fault-tolerant workloads). |
| Virtual Machine Scale Sets (VMSS) | EC2 Auto Scaling Groups (ASGs)         | The concept is identical: managing a group of identical VMs and automatically scaling them based on metrics or a schedule.                                                                                                                                                                               |
| Azure App Service                 | AWS Elastic Beanstalk / AWS App Runner | Elastic Beanstalk is the classic equivalent. It's a PaaS that orchestrates underlying AWS resources (EC2, ELB, S3) for you. AWS App Runner is a newer, simpler service that is more directly comparable to App Service for containerized web apps.                                                       |
| Azure Functions                   | AWS Lambda                             | 🚀 This is a direct 1:1 mapping for serverless, event-driven functions. Both are core to serverless architectures. The concept of triggers, bindings, and paying only for execution time is the same.                                                                                                    |

***

#### ## 3. Containers: The Modern Workload

| Azure Service / Concept         | AWS Equivalent                   | Key Differences & DevOps/SRE Notes                                                                                                                                                                                                                         |
| ------------------------------- | -------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Azure Kubernetes Service (AKS)  | EKS (Elastic Kubernetes Service) | Both are managed Kubernetes services. A key difference is that the EKS control plane has an hourly cost, whereas the AKS control plane is free. Both manage the Kubernetes masters for you, while you manage and pay for the worker nodes.                 |
| Azure Container Instances (ACI) | AWS Fargate                      | This is the serverless container engine comparison. Fargate allows you to run containers without managing the underlying EC2 instances. It can be used as a launch type for both EKS (running serverless pods) and ECS (AWS's own container orchestrator). |
| Azure Container Registry (ACR)  | ECR (Elastic Container Registry) | A direct 1:1 mapping. Both are managed, private Docker container registries.                                                                                                                                                                               |

***

#### ## 4. Networking: Connecting and Securing

| Azure Service / Concept         | AWS Equivalent                                         | Key Differences & DevOps/SRE Notes                                                                                                                                                                                                                                                                                                                                                                           |
| ------------------------------- | ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Virtual Network (VNet)          | VPC (Virtual Private Cloud)                            | The fundamental, logically isolated network for your cloud resources. The concept is identical.                                                                                                                                                                                                                                                                                                              |
| Subnet                          | Subnet                                                 | Exactly the same concept: a range of IP addresses within your VNet/VPC.                                                                                                                                                                                                                                                                                                                                      |
| Network Security Group (NSG)    | Security Groups (SGs) & Network ACLs (NACLs)           | 🛑 Critical Interview Point: This is a key difference. An NSG is like a combination of both. • Security Groups are stateful firewalls that are attached to an instance (a VM's NIC). By default, they allow all outbound traffic. • Network ACLs are stateless firewalls that are attached to a subnet. You must define rules for both inbound and outbound traffic. You'll likely be asked to compare them. |
| Azure Load Balancer (Layer 4)   | Network Load Balancer (NLB)                            | Both operate at Layer 4 (TCP/UDP) and are used for high-performance traffic distribution.                                                                                                                                                                                                                                                                                                                    |
| Application Gateway (Layer 7)   | Application Load Balancer (ALB)                        | Both are Layer 7 load balancers that can route traffic based on HTTP/HTTPS properties like hostnames and paths. Both can handle SSL termination and have WAF capabilities.                                                                                                                                                                                                                                   |
| Azure Front Door                | Amazon CloudFront                                      | Both are global services for traffic management and acceleration. CloudFront is primarily a Content Delivery Network (CDN), but with features like Lambda@Edge, it can perform advanced routing. For global traffic management, AWS also has Global Accelerator.                                                                                                                                             |
| Private Endpoint / Private Link | VPC Endpoints                                          | Exactly the same concept: providing secure, private connectivity from your VPC to AWS services or your own services without traversing the public internet.                                                                                                                                                                                                                                                  |
| Azure Bastion                   | EC2 Instance Connect & Systems Manager Session Manager | Both provide secure access to VMs without exposing SSH/RDP ports to the internet. Session Manager is the more powerful and recommended AWS equivalent, providing a secure, auditable shell and CLI access through the browser or CLI.                                                                                                                                                                        |

***

#### ## 5. Storage: Storing Your Data

| Azure Service / Concept | AWS Equivalent              | Key Differences & DevOps/SRE Notes                                                                                                                                                                                                                              |
| ----------------------- | --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Blob Storage            | S3 (Simple Storage Service) | 📦 This is a direct mapping and one of the most fundamental AWS services. What Azure calls a container, S3 calls a bucket. Both are object storage systems. Key S3 concepts to know are Storage Classes (Standard, Intelligent-Tiering, Glacier for archiving). |
| Azure Disk              | EBS (Elastic Block Store)   | Both provide persistent block storage volumes for use with VMs (EC2). The concept of different performance tiers (SSD, Provisioned IOPS) is the same.                                                                                                           |
| Azure Files             | EFS (Elastic File System)   | Both provide a managed, scalable file share using the NFS protocol. EFS is the direct equivalent for Linux-based workloads needing shared file access. For Windows, AWS has FSx for Windows File Server.                                                        |

***

#### ## 6. CI/CD & Developer Tools

| Azure Service / Concept | AWS Equivalent                      | Key Differences & DevOps/SRE Notes                                                                                                                                                                                                                                         |
| ----------------------- | ----------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Azure DevOps (Suite)    | AWS Developer Tools Suite           | Azure DevOps is a single, highly integrated product. AWS provides a suite of smaller, separate services that you compose together.                                                                                                                                         |
| Azure Pipelines         | CodePipeline, CodeBuild, CodeDeploy | This is a key difference. • CodePipeline is the orchestrator, defining the stages of your CI/CD workflow. • CodeBuild is the managed build service that compiles code and runs tests. • CodeDeploy is the service that automates deployments to EC2, Fargate, Lambda, etc. |
| Azure Repos             | AWS CodeCommit                      | A direct 1:1 mapping for managed private Git repositories.                                                                                                                                                                                                                 |
| Azure Artifacts         | AWS CodeArtifact                    | A direct 1:1 mapping for managed package/artifact repositories (npm, Maven, etc.).                                                                                                                                                                                         |

***

#### ## 7. Infrastructure as Code (IaC)

| Azure Service / Concept | AWS Equivalent     | Key Differences & DevOps/SRE Notes                                                                                                                                                                                                                                                                                                                                                                       |
| ----------------------- | ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ARM Templates / Bicep   | AWS CloudFormation | CloudFormation is the native, declarative IaC service for AWS, using JSON or YAML templates. Bicep is to ARM what the AWS CDK (Cloud Development Kit) is to CloudFormation—a higher-level language (like TypeScript or Python) that synthesizes down to the base template language. Be aware that Terraform is extremely popular in the AWS ecosystem, and many companies prefer it over CloudFormation. |

***

#### ## 8. Monitoring & Observability

| Azure Service / Concept  | AWS Equivalent                               | Key Differences & DevOps/SRE Notes                                                                                                                                                                               |
| ------------------------ | -------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Azure Monitor            | Amazon CloudWatch                            | This is the central, unified monitoring service in AWS. CloudWatch collects Metrics, Logs, and allows you to create Alarms. This is a direct conceptual mapping to Azure Monitor.                                |
| Log Analytics Workspace  | CloudWatch Logs                              | The service for ingesting, storing, and searching log files. Instead of KQL, you use a different syntax in CloudWatch Logs Insights.                                                                             |
| Application Insights     | AWS X-Ray & CloudWatch Application Insights  | X-Ray is the dedicated service for distributed tracing, equivalent to the tracing part of App Insights. CloudWatch Application Insights provides APM-like features for discovering and monitoring applications.  |

\## Interview Tips

* Focus on Concepts, Not Just Names: The interviewer will be more impressed if you say, "I've used Azure's VNet, which is the equivalent of an AWS VPC for creating an isolated network," than if you just struggle to remember the name "VPC."
* Be Honest: It's okay to say, "I'm an expert in Azure, and I'm rapidly learning AWS. My understanding is that the AWS equivalent for X is Y." This shows honesty and a proactive learning attitude.
* Highlight the Differences: Showing that you know the key differences (like Resource Groups vs. Tags, or NSGs vs. Security Groups/NACLs) demonstrates a deeper level of understanding than just a 1:1 mapping.
