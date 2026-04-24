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
# AWS Easy Questions

#### ## AWS Fundamentals & Core Concepts

**1. What is an AWS Account?**

An AWS Account is the primary container for all your AWS resources. It provides a security boundary, billing boundary, and management boundary. Each account has a unique ID and is completely isolated from other AWS accounts.

**2. What is the relationship between an AWS Account, Region, and Availability Zone?**

* AWS Account: Your top-level container that owns all resources.
* Region: A geographic area with multiple isolated locations (e.g., "us-east-1", "eu-west-1"). Resources are region-specific.
* Availability Zone (AZ): One or more discrete data centers within a region with independent power, cooling, and networking. Using multiple AZs provides high availability.

**3. What is the AWS Management Console?**

The AWS Management Console is a web-based unified console that provides a graphical user interface to manage your AWS resources. You can access it via web browser using your account credentials.

**4. What is AWS IAM?**

AWS Identity and Access Management (IAM) is a web service that helps you securely control access to AWS resources. You use IAM to control who is authenticated (signed in) and authorized (has permissions) to use resources.

**5. What is an IAM User?**

An IAM User is an entity that you create in AWS to represent a person or application that uses it to interact with AWS. A user consists of a name and credentials (password or access keys).

**6. What is an IAM Role?**

An IAM Role is an IAM identity that you can create in your account that has specific permissions. Unlike a user, a role is not associated with one person. It can be assumed by anyone who needs it, including AWS services, applications, or users from other accounts.

**7. What is an IAM Policy?**

An IAM Policy is a JSON document that defines permissions for AWS resources. Policies specify what actions are allowed or denied on which resources under what conditions.

**8. What is the AWS CLI?**

The AWS Command Line Interface (CLI) is a unified tool to manage your AWS services. With just one tool to download and configure, you can control multiple AWS services from the command line and automate them through scripts.

**9. What are AWS Organizations?**

AWS Organizations is an account management service that enables you to consolidate multiple AWS accounts into an organization that you create and centrally manage. You can organize accounts into groups and attach policies to groups or accounts.

**10. What is the purpose of tags in AWS?**

Tags are metadata labels that you can assign to AWS resources. Each tag consists of a key and an optional value. Tags are used for cost allocation, organization, automation, access control, and resource management.

**11. What is AWS CloudTrail?**

AWS CloudTrail is a service that enables governance, compliance, operational auditing, and risk auditing of your AWS account. It records AWS API calls for your account and delivers log files containing API calls made via the console, CLI, SDKs, or other AWS services.

**12. What is AWS Trusted Advisor?**

AWS Trusted Advisor is an online tool that provides real-time guidance to help you provision your resources following AWS best practices. It checks for cost optimization, performance, security, and fault tolerance.

**13. What is the AWS Marketplace?**

AWS Marketplace is a digital catalog with thousands of software listings from independent software vendors that make it easy to find, test, buy, and deploy software that runs on AWS.

**14. What is AWS Cost Explorer?**

AWS Cost Explorer is a tool that enables you to view and analyze your AWS costs and usage. You can explore your usage and costs using an intuitive user interface or API.

**15. What is Amazon CloudWatch?**

Amazon CloudWatch is a monitoring and observability service built for DevOps engineers, developers, site reliability engineers (SREs), and IT managers. It provides data and actionable insights to monitor your applications, respond to system-wide performance changes, optimize resource utilization, and get a unified view of operational health.

***

#### ## AWS Compute

**16. What is Amazon EC2?**

Amazon Elastic Compute Cloud (EC2) is a web service that provides resizable compute capacity in the cloud. It is designed to make web-scale cloud computing easier for developers by providing virtual machines (instances) on demand.

**17. What is an Amazon Machine Image (AMI)?**

An Amazon Machine Image (AMI) is a supported and maintained image provided by AWS that provides the information required to launch an instance. It includes the operating system, application server, and applications.

**18. What is an EC2 Instance Type?**

Instance types are combinations of CPU, memory, storage, and networking capacity that give you the flexibility to choose the appropriate mix of resources for your applications.

**19. What is Amazon EC2 Auto Scaling?**

Auto Scaling helps you maintain application availability and allows you to automatically add or remove EC2 instances according to conditions you define. It works with Amazon EC2 to automatically launch or terminate instances.

**20. What are EC2 Reserved Instances?**

Reserved Instances provide you with a significant discount (up to 75%) compared to On-Demand Instance pricing. In exchange, you commit to paying for the instance for a one-year or three-year term.

**21. What are EC2 Spot Instances?**

Spot Instances allow you to bid on spare Amazon EC2 computing capacity at a discount compared to On-Demand pricing. AWS can reclaim the capacity with two minutes' notice if the spot price exceeds your bid or capacity is needed.

**22. What is AWS Lambda?**

AWS Lambda is a serverless compute service that lets you run code without provisioning or managing servers. You pay only for the compute time you consume - there is no charge when your code is not running.

**23. When would you use Lambda instead of EC2?**

Use Lambda for short, event-driven tasks that run for seconds or minutes. Use EC2 for long-running applications, complex workloads, or when you need full control over the environment.

**24. What is AWS Elastic Beanstalk?**

AWS Elastic Beanstalk is an easy-to-use service for deploying and scaling web applications and services developed with Java, .NET, PHP, Node.js, Python, Ruby, Go, and Docker on familiar servers such as Apache, Nginx, Passenger, and IIS.

**25. What is AWS Fargate?**

AWS Fargate is a serverless compute engine for containers that works with both Amazon Elastic Container Service (ECS) and Amazon Elastic Kubernetes Service (EKS). It removes the need to provision and manage servers.

**26. What is AWS Batch?**

AWS Batch enables you to run batch computing workloads on the AWS Cloud. It dynamically provisions the optimal quantity and type of compute resources based on the volume and specific resource requirements of the batch jobs submitted.

**27. What is the difference between rebooting and stopping an EC2 instance?**

* Reboot: The instance keeps running on the same host. Data in instance store is preserved. No billing interruption.
* Stop: The instance is shut down. EBS-backed instances can be stopped. The instance is not billed when stopped, but storage is. When started, it may run on different hardware.

**28. What is an EC2 Security Group?**

A security group acts as a virtual firewall for your EC2 instances to control incoming and outgoing traffic. It is stateful - if you allow inbound traffic, the return traffic is automatically allowed.

**29. What is a Key Pair in AWS?**

A key pair consists of a public key that AWS stores and a private key file that you store. Together, they allow you to connect to your instance securely using SSH (Linux) or decrypt the Windows administrator password.

**30. What is the AWS Nitro System?**

The AWS Nitro System is the underlying platform for AWS EC2 instances that enables faster innovation, enhanced security, and better performance by offloading virtualization functions to dedicated hardware and software.

***

#### ## AWS Storage

**31. What is Amazon S3?**

Amazon Simple Storage Service (S3) is an object storage service that offers industry-leading scalability, data availability, security, and performance. It stores data as objects within buckets.

**32. What is an S3 Bucket?**

An S3 bucket is a container for objects stored in Amazon S3. Every object is contained in a bucket. Buckets are region-specific and must have globally unique names.

**33. What are the different S3 storage classes?**

* S3 Standard: For frequently accessed data
* S3 Intelligent-Tiering: Automatically moves data between tiers based on access patterns
* S3 Standard-IA (Infrequent Access): For less frequently accessed data
* S3 One Zone-IA: For infrequently accessed data in a single AZ
* S3 Glacier: For archival data with retrieval times of minutes to hours
* S3 Glacier Deep Archive: For long-term archive with lowest cost

**34. What is the difference between S3 and EBS?**

* S3 (Simple Storage Service): Object storage accessed via HTTP/HTTPS. Ideal for storing files, images, backups, and static websites. Unlimited storage.
* EBS (Elastic Block Store): Block storage attached to EC2 instances like a hard drive. Used for databases and applications requiring a file system.

**35. What is Amazon EBS?**

Amazon Elastic Block Store (EBS) provides block level storage volumes for use with EC2 instances. EBS volumes are network-attached and persist independently from the life of an instance.

**36. What are EBS volume types?**

* gp3/gp2 (General Purpose SSD): Balanced price and performance for most workloads
* io2/io1 (Provisioned IOPS SSD): High performance for mission-critical applications
* st1 (Throughput Optimized HDD): Low-cost HDD for frequently accessed, throughput-intensive workloads
* sc1 (Cold HDD): Lowest cost HDD for less frequently accessed data

**37. What is an EBS Snapshot?**

An EBS snapshot is a point-in-time backup of an EBS volume. It is stored in Amazon S3 and can be used to create new EBS volumes or restore existing ones.

**38. What is Amazon EFS?**

Amazon Elastic File System (EFS) provides a simple, scalable, fully managed elastic NFS file system for use with AWS Cloud services and on-premises resources. Multiple EC2 instances can access EFS simultaneously.

**39. What is Amazon FSx?**

Amazon FSx provides fully managed third-party file systems optimized for specific workloads like Windows File Server, Lustre (high-performance computing), or NetApp ONTAP.

**40. What is S3 Versioning?**

Versioning in S3 allows you to preserve, retrieve, and restore every version of every object stored in your buckets. It protects against accidental deletion and overwrites.

***

#### ## AWS Networking

**41. What is Amazon VPC?**

Amazon Virtual Private Cloud (VPC) lets you provision a logically isolated section of the AWS Cloud where you can launch AWS resources in a virtual network that you define. You have complete control over your virtual networking environment.

**42. What is a Subnet in AWS?**

A subnet is a range of IP addresses in your VPC. You can launch AWS resources into a subnet that you select. Each subnet must reside entirely within one Availability Zone.

**43. What is an Internet Gateway?**

An internet gateway is a horizontally scaled, redundant, and highly available VPC component that allows communication between instances in your VPC and the internet.

**44. What is a NAT Gateway?**

A NAT Gateway allows instances in a private subnet to connect to the internet or other AWS services, but prevents the internet from initiating a connection with those instances.

**45. What is an Elastic IP?**

An Elastic IP address is a static IPv4 address designed for dynamic cloud computing. Unlike traditional static IP addresses, an Elastic IP address can be remapped to any instance in your account to mask instance failures.

**46. What is an Elastic Load Balancer (ELB)?**

Elastic Load Balancing automatically distributes incoming application traffic across multiple targets, such as EC2 instances, containers, IP addresses, and Lambda functions. Types include Application Load Balancer (ALB), Network Load Balancer (NLB), and Gateway Load Balancer.

**47. What is the difference between ALB and NLB?**

* Application Load Balancer (ALB): Layer 7 (HTTP/HTTPS). Content-based routing, SSL termination, WebSocket support.
* Network Load Balancer (NLB): Layer 4 (TCP/UDP). Ultra-low latency, handles millions of requests per second, preserves client IP.

**48. What is Amazon Route 53?**

Amazon Route 53 is a highly available and scalable cloud Domain Name System (DNS) web service. It is designed to give developers and businesses an extremely reliable and cost-effective way to route end users to Internet applications.

**49. What is a VPC Peering Connection?**

A VPC peering connection is a networking connection between two VPCs that enables you to route traffic between them using private IP addresses. Instances in either VPC can communicate as if they are within the same network.

**50. What is AWS Direct Connect?**

AWS Direct Connect is a cloud service solution that makes it easy to establish a dedicated network connection from your premises to AWS. Using Direct Connect, you can establish private connectivity between AWS and your datacenter, office, or colocation environment.

**51. What is AWS VPN?**

AWS VPN enables you to establish secure connections between your on-premises networks and your Amazon VPCs. It includes Site-to-Site VPN and Client VPN.

**52. What is a VPC Endpoint?**

A VPC endpoint enables you to privately connect your VPC to supported AWS services and VPC endpoint services powered by PrivateLink without requiring an internet gateway, NAT device, VPN connection, or AWS Direct Connect connection.

**53. What is AWS PrivateLink?**

AWS PrivateLink provides private connectivity between VPCs, AWS services, and your on-premises networks without exposing your traffic to the public internet.

**54. What is AWS Transit Gateway?**

AWS Transit Gateway connects VPCs and on-premises networks through a central hub. This simplifies your network and puts an end to complex peering relationships. It acts as a cloud router.

**55. What is AWS App Mesh?**

AWS App Mesh is a service mesh that provides application-level networking to make it easy for your services to communicate with each other across multiple types of compute infrastructure.

***

#### ## AWS Containers

**56. What is Amazon ECS?**

Amazon Elastic Container Service (ECS) is a fully managed container orchestration service that helps you easily deploy, manage, and scale containerized applications using Docker containers.

**57. What is Amazon EKS?**

Amazon Elastic Kubernetes Service (EKS) is a managed service that makes it easy for you to run Kubernetes on AWS without needing to install and operate your own Kubernetes control plane.

**58. What is Amazon ECR?**

Amazon Elastic Container Registry (ECR) is a fully managed container registry that makes it easy to store, manage, share, and deploy your container images securely.

**59. What is the difference between ECS and EKS?**

* ECS: AWS-native container orchestration. Simpler, integrated with AWS ecosystem. Uses AWS-specific concepts (task definitions, services).
* EKS: Managed Kubernetes. More complex but portable. Uses standard Kubernetes APIs and concepts.

**60. What is an ECS Task Definition?**

A task definition is a blueprint that describes how a container should launch. It contains parameters like which Docker image to use, CPU/memory allocation, networking mode, and IAM role.

**61. What is an ECS Service?**

An ECS service allows you to run and maintain a specified number of instances of a task definition simultaneously in an ECS cluster. If any of your tasks fail or stop, the service scheduler launches another instance.

**62. What is AWS App Runner?**

AWS App Runner is a fully managed service that makes it easy for developers to quickly deploy containerized web applications and APIs, at scale and with no prior infrastructure experience required.

**63. What is an EKS Node Group?**

A node group is a group of EC2 instances (nodes) that have the same configuration and run your Kubernetes pods in EKS. EKS supports managed node groups and self-managed nodes.

**64. How do you scale applications in ECS?**

You can scale applications in ECS by:
* Changing the desired count of tasks in a service
* Using Application Auto Scaling to automatically adjust task count based on CloudWatch metrics
* Using the Cluster Auto Scaling with ECS capacity providers

**65. What is the EKS control plane?**

The EKS control plane consists of the Kubernetes master nodes (API server, etcd, scheduler) that AWS manages for you at no additional cost beyond the worker nodes you run.

***

#### ## AWS Database

**66. What is Amazon RDS?**

Amazon Relational Database Service (RDS) makes it easy to set up, operate, and scale a relational database in the cloud. It provides cost-efficient and resizable capacity while automating time-consuming administration tasks.

**67. What database engines does RDS support?**

RDS supports Amazon Aurora, MySQL, MariaDB, PostgreSQL, Oracle, and Microsoft SQL Server.

**68. What is Amazon Aurora?**

Amazon Aurora is a MySQL and PostgreSQL-compatible relational database built for the cloud. It provides up to five times better performance than MySQL and three times better performance than PostgreSQL at a lower cost.

**69. What is Amazon DynamoDB?**

Amazon DynamoDB is a fully managed NoSQL database service that provides fast and predictable performance with seamless scalability. It supports both key-value and document data models.

**70. What is DynamoDB on-demand capacity?**

On-demand capacity mode for DynamoDB allows you to pay per request for the read and write requests you make, without having to specify or plan capacity in advance.

**71. What is Amazon ElastiCache?**

Amazon ElastiCache is a fully managed in-memory caching service that supports Redis and Memcached. It helps improve application performance by retrieving data from fast, managed, in-memory caches.

**72. What is Amazon Redshift?**

Amazon Redshift is a fully managed, petabyte-scale data warehouse service in the cloud. You can start with just a few hundred gigabytes of data and scale to a petabyte or more.

**73. What is Amazon DocumentDB?**

Amazon DocumentDB (with MongoDB compatibility) is a fast, scalable, highly available, and fully managed document database service that supports MongoDB workloads.

**74. What is Amazon Neptune?**

Amazon Neptune is a fast, reliable, fully managed graph database service that makes it easy to build and run applications that work with highly connected datasets.

**75. What is Amazon Keyspaces?**

Amazon Keyspaces (for Apache Cassandra) is a scalable, highly available, and managed Apache Cassandra-compatible database service.

***

#### ## AWS Security

**76. What is AWS KMS?**

AWS Key Management Service (KMS) makes it easy for you to create and manage cryptographic keys and control their use across a wide range of AWS services and in your applications.

**77. What is AWS Secrets Manager?**

AWS Secrets Manager helps you protect secrets needed to access applications, services, and IT resources. The service enables you to easily rotate, manage, and retrieve database credentials, API keys, and other secrets throughout their lifecycle.

**78. What is AWS Certificate Manager?**

AWS Certificate Manager (ACM) makes it easy to provision, manage, and deploy public and private SSL/TLS certificates for use with AWS services and your internal connected resources.

**79. What is AWS WAF?**

AWS WAF is a web application firewall that helps protect your web applications or APIs against common web exploits and bots that may affect availability, compromise security, or consume excessive resources.

**80. What is AWS Shield?**

AWS Shield is a managed Distributed Denial of Service (DDoS) protection service that safeguards applications running on AWS. Shield Standard is automatically enabled, while Shield Advanced provides additional protections and 24/7 DDoS response team support.

**81. What is Amazon GuardDuty?**

Amazon GuardDuty is a threat detection service that continuously monitors for malicious activity and unauthorized behavior to protect your AWS accounts, workloads, and data stored in Amazon S3.

**82. What is Amazon Inspector?**

Amazon Inspector is an automated security assessment service that helps improve the security and compliance of applications deployed on AWS by assessing them for vulnerabilities and deviations from best practices.

**83. What is AWS Config?**

AWS Config is a service that enables you to assess, audit, and evaluate the configurations of your AWS resources. Config continuously monitors and records your AWS resource configurations and allows you to automate the evaluation of recorded configurations against desired configurations.

**84. What is AWS Systems Manager?**

AWS Systems Manager gives you visibility and control of your infrastructure on AWS. It provides a unified interface so you can view operational data from multiple AWS services and automate tasks across your AWS resources.

**85. What is AWS Service Catalog?**

AWS Service Catalog allows organizations to create and manage catalogs of IT services that are approved for use on AWS. These IT services can include everything from virtual machine images, servers, software, and databases to complete multi-tier application architectures.

***

#### ## AWS Deployment & Management

**86. What is AWS CloudFormation?**

AWS CloudFormation is a service that helps you model and set up your AWS resources so that you can spend less time managing those resources and more time focusing on your applications. You create a template that describes all the AWS resources you want.

**87. What is AWS CodeCommit?**

AWS CodeCommit is a fully managed source control service that hosts secure Git-based repositories. It makes it easy for teams to collaborate on code in a secure and highly scalable ecosystem.

**88. What is AWS CodeBuild?**

AWS CodeBuild is a fully managed continuous integration service that compiles source code, runs tests, and produces software packages that are ready to deploy.

**89. What is AWS CodeDeploy?**

AWS CodeDeploy is a fully managed deployment service that automates software deployments to a variety of compute services such as Amazon EC2, AWS Fargate, AWS Lambda, and your on-premises servers.

**90. What is AWS CodePipeline?**

AWS CodePipeline is a fully managed continuous delivery service that helps you automate your release pipelines for fast and reliable application and infrastructure updates.

**91. What is AWS Elastic Beanstalk?**

AWS Elastic Beanstalk is an easy-to-use service for deploying and scaling web applications and services. You simply upload your code and Elastic Beanstalk automatically handles the deployment, load balancing, scaling, and health monitoring.

**92. What is AWS OpsWorks?**

AWS OpsWorks is a configuration management service that provides managed instances of Chef and Puppet. It gives you the ability to use code to automate the configurations of your servers.

**93. What is Amazon CloudFront?**

Amazon CloudFront is a fast content delivery network (CDN) service that securely delivers data, videos, applications, and APIs to customers globally with low latency and high transfer speeds.

**94. What is AWS Cloud9?**

AWS Cloud9 is a cloud-based integrated development environment (IDE) that lets you write, run, and debug your code with just a browser. It includes a code editor, debugger, and terminal.

**95. What is AWS X-Ray?**

AWS X-Ray helps developers analyze and debug production, distributed applications, such as those built using a microservices architecture. With X-Ray, you can understand how your application and its underlying services are performing.

***

#### ## AWS Monitoring & Logging

**96. What is Amazon CloudWatch Logs?**

CloudWatch Logs enables you to centralize the logs from all of your systems, applications, and AWS services that you use, in a single, highly scalable service.

**97. What is CloudWatch Alarms?**

CloudWatch Alarms watches a single metric over a time period you specify and performs one or more actions based on the value of the metric relative to a given threshold over a number of time periods.

**98. What is Amazon SNS?**

Amazon Simple Notification Service (SNS) is a fully managed messaging service for both application-to-application (A2A) and application-to-person (A2P) communication. It can send notifications via email, SMS, mobile push, or to SQS queues.

**99. What is Amazon SQS?**

Amazon Simple Queue Service (SQS) is a fully managed message queuing service that enables you to decouple and scale microservices, distributed systems, and serverless applications.

**100. What is AWS CloudFormation Drift Detection?**

Drift detection enables you to detect whether a stack's actual configuration differs, or has drifted, from its expected configuration. This helps you identify resource changes made outside of CloudFormation.
# AWS Medium Questions

These medium-difficulty AWS questions target DevOps and SRE interviews where the expectation is practical understanding rather than simple memorization.

***

#### ## AWS Core Concepts & IAM

**1. Compare and contrast IAM Users, IAM Roles, and IAM Groups.**

* IAM Users: Represent individual people or applications with long-term credentials (passwords or access keys). Best for human users needing console access.
* IAM Roles: Temporary credentials that can be assumed by users, services, or applications. Best for AWS service-to-service access and cross-account access.
* IAM Groups: Collections of IAM users. You assign permissions to groups, and users inherit those permissions. You cannot assign a role to a group.

**2. What is the difference between Resource-Based Policies and Identity-Based Policies?**

* Identity-Based Policies: Attached to IAM users, groups, or roles. Specify what the identity can do to resources.
* Resource-Based Policies: Attached directly to a resource (like S3 bucket, SQS queue, KMS key). Specify who can access the resource and what they can do. S3 bucket policies are a common example.

**3. How does IAM Policy Evaluation work when multiple policies apply?**

By default, all requests are denied. An explicit allow overrides the default deny. An explicit deny overrides any allows. AWS evaluates all applicable policies - identity policies, resource policies, permission boundaries, and SCPs. The final decision is "deny" unless there is an explicit allow and no explicit deny.

**4. What is an IAM Permissions Boundary?**

Permissions boundaries are an advanced feature in which you set the maximum permissions that an identity-based policy can grant to an IAM entity. The entity can only perform actions allowed by both its identity policies and its permissions boundaries.

**5. How would you securely provide credentials to an EC2 instance so it can access S3?**

Use an IAM Role attached to the EC2 instance (via an instance profile). This eliminates the need to store access keys on the instance. The AWS SDK and CLI automatically retrieve temporary credentials from the EC2 metadata service.

**6. What is AWS STS and what are common use cases?**

AWS Security Token Service (STS) creates temporary credentials for IAM users or federated users. Common use cases:
* Cross-account access
* Identity federation (SAML, OIDC)
* AWS service access from on-premises
* Temporary elevated privileges

**7. How does IAM Role Chaining work and why should you avoid it?**

Role chaining occurs when you use a role to assume a second role, and potentially a third. AWS does not store credentials for more than one role at a time. You should avoid it because:
* It makes troubleshooting harder
* It can hit the 1-hour session limit for roles assumed by roles
* It complicates auditing and access tracking

**8. What is AWS Organizations SCP and how does it differ from IAM policies?**

Service Control Policies (SCPs) are IAM policies attached to AWS Organizations entities (root, OU, or account). They specify the maximum available permissions for entities within member accounts. Unlike IAM policies, SCPs never grant permissions - they only limit what permissions can be used.

**9. How would you implement a least-privilege access strategy across multiple AWS accounts?**

1. Use AWS Organizations with SCPs to set guardrails at the organizational level
2. Create custom IAM roles for specific job functions
3. Use IAM Access Analyzer to identify unused permissions
4. Implement regular access reviews
5. Use permission boundaries for delegated administration
6. Enable CloudTrail for auditing all API calls

**10. What is IAM Access Analyzer and how does it help with security?**

IAM Access Analyzer analyzes resource policies to help identify resources shared with external entities. It helps you identify:
* S3 buckets accessible from outside your account
* KMS keys shared with other accounts
* Roles that can be assumed by external principals
* Unused permissions and access keys

***

#### ## AWS Networking & Security

**11. Explain the difference between Security Groups and NACLs.**

* Security Groups: Stateful, operate at the instance level, act as virtual firewalls for EC2 instances. Return traffic is automatically allowed. You can only create "allow" rules.
* NACLs (Network Access Control Lists): Stateless, operate at the subnet level, evaluate rules in order. You must explicitly allow return traffic. You can create both "allow" and "deny" rules.

**12. How does VPC Flow Logs work and what can you use them for?**

VPC Flow Logs capture information about IP traffic going to and from network interfaces in your VPC. They can be published to CloudWatch Logs or S3. Use cases:
* Troubleshooting connectivity issues
* Security analysis and anomaly detection
* Compliance auditing
* Understanding traffic patterns

**13. What is the difference between VPC Peering, Transit Gateway, and PrivateLink?**

* VPC Peering: Direct connection between two VPCs. Simple but doesn't scale well (n(n-1)/2 connections needed).
* Transit Gateway: Central hub connecting multiple VPCs and on-premises networks. Scales well, supports transitive routing.
* PrivateLink: Provides private connectivity to services across VPCs and accounts without peering or internet gateways. Uses VPC endpoints.

**14. How would you design a multi-account network architecture with centralized egress inspection?**

Use AWS Transit Gateway with a centralized VPC (shared services):
1. All spoke VPCs attach to Transit Gateway
2. Route all internet-bound traffic (0.0.0.0/0) from spokes through TGW to the centralized egress VPC
3. In the egress VPC, deploy NAT Gateways and/or proxy/firewall appliances
4. Apply security controls at the centralized egress point
5. Use Transit Gateway route tables for traffic segmentation

**15. What are the limitations of VPC Peering?**

* No transitive routing (VPC A peered with B and C cannot route between B and C)
* No overlapping CIDR blocks allowed
* Maximum of 125 peering connections per VPC (soft limit)
* No support for edge-to-edge routing (you can't use a gateway in a peered VPC)

**16. How does Amazon Route 53 handle DNS failover?**

Route 53 can perform health checks on endpoints and automatically route traffic away from failed endpoints. You can configure:
* Active-active failover: All resources are active, traffic routed to healthy ones
* Active-passive failover: Primary is active, secondary only receives traffic when primary fails
* Latency-based routing: Route to the region with lowest latency
* Geolocation routing: Route based on user location

**17. What is AWS Certificate Manager (ACM) and what are its limitations?**

ACM provisions, manages, and deploys public and private SSL/TLS certificates. Limitations:
* ACM certificates can only be deployed on AWS-managed services (ELB, CloudFront, API Gateway)
* Cannot export public certificates with private keys for use on EC2
* Private certificates require Private CA which has additional costs
* Certificates are region-specific (except CloudFront which uses us-east-1)

**18. How would you securely expose an internal application to the internet?**

Architecture:
1. Application runs in private subnets behind an Application Load Balancer
2. ALB is in public subnets
3. Security groups restrict access: ALB allows 443 from internet, application only allows traffic from ALB security group
4. AWS WAF attached to ALB for DDoS and OWASP protection
5. AWS Shield Advanced for additional DDoS protection
6. AWS Certificate Manager provides SSL/TLS certificate
7. CloudFront as CDN/WAF frontend (optional but recommended)

**19. What is AWS Private Certificate Authority (PCA)?**

AWS Private Certificate Authority is a managed private CA service that helps you securely issue and manage private certificates for your internal resources. Use cases:
* Mutual TLS (mTLS) authentication
* Code signing
* VPN authentication
* Private service mesh identity

**20. How do you implement network segmentation in AWS VPC?**

1. Subnets: Create separate subnets for different tiers (web, app, database)
2. Security Groups: Application-tier SGs only allow traffic from web-tier SGs
3. NACLs: Add additional layer of protection at subnet level
4. Transit Gateway Route Tables: Segment traffic between different business units
5. VPC Endpoints: Keep traffic to AWS services on AWS network

***

#### ## AWS Compute & EC2

**21. What are the different EC2 purchasing options and when would you use each?**

* On-Demand: Pay by hour/second with no commitment. Use for short-term, irregular workloads.
* Reserved Instances: 1-3 year commitment, up to 72% discount. Use for steady-state, predictable workloads.
* Spot Instances: Up to 90% discount, can be interrupted. Use for fault-tolerant, flexible workloads.
* Savings Plans: Flexible commitment to compute usage, similar discounts to RIs. Use for dynamic workloads.
* Dedicated Hosts: Physical server dedicated to you. Use for compliance or licensing requirements.

**22. How does EC2 Auto Scaling work with target tracking policies?**

Target tracking scaling policies automatically scale capacity to maintain a specified metric at a target value. For example:
* Keep average CPU utilization at 50%
* Keep request count per target at 1000
ASG automatically adds/removes instances to maintain the target. It uses CloudWatch alarms internally and handles metric math automatically.

**23. What is an EC2 Launch Template vs Launch Configuration?**

* Launch Templates: Newer, recommended. Versioned, support multiple versions, can combine multiple instance types, and can be used with Spot Fleet. Support more features like T2/T3 Unlimited.
* Launch Configuration: Older, simpler. Not versioned, single configuration, deprecated for some features.

**24. How would you handle secrets in EC2 User Data scripts?**

Best practices:
1. Never hardcode secrets in user data
2. Use IAM roles for AWS API access
3. Fetch secrets from AWS Secrets Manager or Parameter Store using IAM role
4. Use AWS Systems Manager Run Command instead of user data for configuration
5. Encrypt sensitive data in user data using KMS
6. Clear secrets from instance metadata after retrieval

**25. What is EC2 Instance Metadata Service (IMDS) and why is IMDSv2 more secure?**

IMDS provides data about instances via a local API (169.254.169.254).
* IMDSv1: Simple GET request, vulnerable to SSRF attacks
* IMDSv2: Session-based authentication requiring:
  1. PUT request to get a token
  2. Subsequent requests must include the token
  3. Token has TTL (time-to-live)
  4. Requires PUT support which many SSRF vulnerabilities lack

**26. How do you implement blue-green deployments with EC2?**

1. Have two identical Auto Scaling Groups (blue and green)
2. Initially, blue ASG is active behind the load balancer
3. Deploy new version to green ASG
4. Test green ASG (canary or full validation)
5. Switch load balancer target to green ASG
6. Keep blue ASG for quick rollback if needed
7. Terminate blue ASG after validation period

**27. What is an EC2 Spot Instance interruption and how do you handle it?**

AWS can reclaim Spot Instances with 2-minute warning. Handling strategies:
1. Use Spot Instance interruption notices via EC2 metadata
2. Configure Spot Fleets with On-Demand fallback (mixed instances policy)
3. Design applications to be stateless and fault-tolerant
4. Use checkpointing for long-running workloads
5. Implement automated draining and graceful shutdown

**28. What are the different tenancy options for EC2 instances?**

* Shared (default): Multiple AWS accounts may share the same physical hardware
* Dedicated Instance: Your instances run on single-tenant hardware
* Dedicated Host: Physical server fully dedicated to your use, provides visibility into sockets/cores

**29. How does AWS Systems Manager Session Manager improve security over SSH?**

Advantages over SSH:
* No inbound ports required (no SSH key management)
* Centralized access control via IAM policies
* Auditable session logging to S3 or CloudWatch
* Can restrict commands users can run
* Works across VPCs, regions, and hybrid environments
* No bastion hosts needed

**30. What is EC2 Hibernate and when would you use it?**

Hibernate saves the contents of instance RAM to the root EBS volume. When started again:
* Root volume is restored to previous state
* RAM contents are reloaded
* Previously running processes resume
* Instance ID and EBS volumes preserved
Use cases: long-running processes, stopping/resuming workflows, maintaining pre-warmed caches

***

#### ## AWS Storage

**31. What is the difference between S3 Strong Consistency and Eventual Consistency?**

As of December 2020, S3 provides strong read-after-write consistency for PUT and DELETE requests of objects in your Amazon S3 bucket in all AWS Regions. Previously, there was eventual consistency for overwrite PUTs and DELETEs. Now:
* Read-after-write consistency for PUT of new objects
* Strong consistency for overwrite PUTs and DELETEs
* No additional cost or configuration required

**32. How does S3 Cross-Region Replication (CRR) work?**

CRR automatically replicates objects across buckets in different AWS Regions:
1. Enable versioning on both source and destination buckets
2. Configure replication rules specifying source and destination
3. Optionally use IAM role for replication permissions
4. Can replicate to multiple destination buckets
5. Can filter by object prefix or tags
6. Supports delete marker replication (optional)
7. Does NOT replicate existing objects by default (requires batch replication)

**33. What is S3 Transfer Acceleration?**

Transfer Acceleration uses CloudFront's globally distributed edge locations to accelerate uploads to S3. Users upload to the nearest edge location, and AWS optimizes the path from edge to S3 bucket. Benefits:
* Faster long-distance uploads
* No proprietary protocols or client software
* Works with standard S3 APIs
* Additional cost per GB transferred

**34. How would you secure an S3 bucket?**

Best practices:
1. Block all public access (account and bucket level)
2. Use bucket policies to grant minimal necessary access
3. Enable encryption (SSE-S3, SSE-KMS, or SSE-C)
4. Enable access logging and CloudTrail
5. Enable versioning for recovery
6. Use S3 Object Lock for compliance
7. Configure VPC endpoints for private access
8. Regularly audit with S3 Block Public Access and IAM Access Analyzer

**35. What is the difference between S3 Select and Athena?**

* S3 Select: Retrieves only a subset of data from an object using simple SQL queries. Works on single objects, reduces data transfer.
* Athena: Serverless query service for analyzing data in S3 using standard SQL. Can query multiple files, supports complex queries, joins, and partitioned data. Uses Presto under the hood.

**36. How do you optimize S3 costs for infrequently accessed data?**

Strategies:
1. Use S3 Intelligent-Tiering for automatic cost optimization
2. Set up Lifecycle Policies to move data to cheaper storage classes
3. Use S3 Glacier for archival data
4. Delete incomplete multipart uploads
5. Compress data before upload
6. Use S3 Batch Operations for large-scale changes

**37. What are EBS Multi-Attach and when would you use it?**

EBS Multi-Attach allows an EBS volume to be attached to multiple EC2 instances in the same Availability Zone simultaneously. Requirements:
* Only supported on io1 and io2 volumes
* Must use a cluster-aware file system (not ext4/xfs)
* Applications must manage write coordination
Use cases: clustered databases, high-availability applications requiring concurrent access

**38. How do you optimize EBS performance?**

1. Right-size volumes for IOPS/throughput needs
2. Use gp3 for better price-performance than gp2
3. Use io2 Block Express for highest performance
4. Enable EBS-optimized instances
5. RAID 0 multiple volumes for higher throughput
6. Pre-warm volumes by reading all blocks (for new volumes)
7. Use larger volume sizes to get more baseline IOPS (gp2)

**39. What is the difference between EFS Standard and EFS IA?**

* EFS Standard: Multi-AZ, low-latency, higher cost. For frequently accessed data.
* EFS IA (Infrequent Access): Lower cost for files not accessed frequently. Automatic lifecycle management moves files based on last access time.
* EFS Archive: Lowest cost for rarely accessed files.

**40. What is Amazon S3 Object Lock?**

Object Lock prevents objects from being deleted or overwritten for a fixed amount of time or indefinitely. Modes:
* Governance mode: Users can't overwrite or delete unless they have special permissions
* Compliance mode: No one (including root) can overwrite or delete during retention period
Use cases: regulatory compliance, legal hold, data retention policies

***

#### ## AWS Containers

**41. What is the difference between ECS Service Discovery and Load Balancing?**

* Service Discovery: Uses AWS Cloud Map to register tasks with DNS names. Clients look up service location via DNS. Good for service-to-service communication.
* Load Balancing: Uses Application Load Balancer or Network Load Balancer to distribute traffic. Clients connect to load balancer endpoint. Good for external-facing services.

**42. How does ECS Capacity Providers work?**

Capacity Providers allow you to define the infrastructure (compute) on which your tasks run:
* FARGATE/FARGATE_SPOT: Serverless compute
* Auto Scaling Groups: EC2 instances
You can mix capacity providers in a cluster and define the strategy (base, weight) for task placement. Enables seamless mixing of On-Demand and Spot capacity.

**43. What is the difference between ECS Task Role and Task Execution Role?**

* Task Role: Permissions that the application code inside the container needs (e.g., accessing DynamoDB, S3)
* Task Execution Role: Permissions that the ECS agent and Docker daemon needs (e.g., pulling images from ECR, publishing logs to CloudWatch)

**44. How do you implement rolling deployments in ECS?**

ECS rolling deployments update tasks gradually:
1. Define minimum healthy percent and maximum percent in service
2. ECS starts new task definitions while keeping old ones running
3. Once new tasks are healthy, old tasks are stopped
4. Continues until all tasks are updated
5. Can configure deployment circuit breaker to rollback on failure

**45. What is Amazon EKS IRSA (IAM Roles for Service Accounts)?**

IRSA allows you to map a Kubernetes service account to an IAM role:
1. Create IAM OIDC identity provider for your EKS cluster
2. Create IAM role with trust policy allowing specific service account
3. Annotate Kubernetes service account with IAM role ARN
4. Pods using that service account get temporary credentials via STS
Benefits: Fine-grained permissions per pod, no node-level permissions needed

**46. How does EKS Cluster Autoscaler work?**

The Kubernetes Cluster Autoscaler:
1. Watches for pods in Pending state due to insufficient resources
2. Calculates required node capacity
3. Calls AWS APIs to add nodes to Auto Scaling Group
4. Also removes underutilized nodes (respects PDBs)
Requirements: Tagged ASGs, proper IAM permissions, resource requests set on pods

**47. What is EKS Fargate and when would you use it?**

EKS Fargate allows running Kubernetes pods without managing nodes:
* AWS provisions compute on-demand per pod
* No node management, patching, or capacity planning
* Each pod runs in isolated environment
* Pay per pod resource usage
Use cases: Variable workloads, batch jobs, isolation requirements, reducing operational overhead

**48. How do you secure container images in ECR?**

1. Use image scanning (basic or enhanced with Amazon Inspector)
2. Enable image tag immutability to prevent overwrites
3. Use IAM policies for repository access control
4. Enable encryption at rest using KMS
5. Configure lifecycle policies to remove old images
6. Use private endpoints (VPC endpoints) for ECR access
7. Enable cross-region replication for disaster recovery

**49. What is the difference between EKS Managed Node Groups and Self-Managed Nodes?**

* Managed Node Groups:
  * AWS manages node provisioning and lifecycle
  * Automatic updates and patching
  * Integrated with EKS console and APIs
  * Less flexibility in AMI customization

* Self-Managed Nodes:
  * You manage Auto Scaling Groups directly
  * Full control over AMI, user data, instance types
  * Manual updates and patching
  * More operational overhead

**50. How would you implement service mesh on EKS?**

Options:
1. AWS App Mesh: Native AWS service, integrates with ECS, EKS, EC2
2. Istio: Open-source, feature-rich, runs as sidecar proxies
3. Linkerd: Lightweight service mesh, CNCF graduated project
Implementation typically involves:
* Installing control plane
* Injecting sidecar proxies (automatic or manual)
* Configuring traffic policies, mTLS, circuit breaking
* Setting up observability (metrics, tracing)

***

#### ## AWS Database

**51. What is Amazon Aurora and how does it differ from standard RDS?**

Aurora is a cloud-native relational database compatible with MySQL and PostgreSQL:
* Storage automatically scales up to 128TB
* Replicates data across 3 AZs (6 copies)
* Automatic failover typically under 30 seconds
* Up to 15 read replicas with minimal lag
* Storage and compute are separate (can scale independently)
* Shared storage architecture vs replication for standard RDS

**52. How does RDS Multi-AZ work?**

Multi-AZ provides high availability:
1. Synchronous replication to standby in different AZ
2. Automatic failover to standby if primary fails (typically 60-120 seconds)
3. Same DNS endpoint, applications reconnect automatically
4. Standby cannot serve read traffic (unlike read replicas)
5. Automatic backups taken from standby to reduce I/O impact

**53. What is the difference between RDS Read Replicas and Multi-AZ?**

* Read Replicas:
  * Asynchronous replication
  * Can serve read traffic
  * Can be in same or different regions
  * Can promote to standalone database
  * Used for scaling read workload

* Multi-AZ:
  * Synchronous replication
  * Standby cannot serve reads
  * Same region only
  * Automatic failover
  * Used for high availability

**54. How do you optimize DynamoDB costs?**

1. Use On-Demand for unpredictable workloads, Provisioned for predictable
2. Enable Auto Scaling on provisioned tables
3. Use reserved capacity for predictable throughput
4. Implement caching with DAX (DynamoDB Accelerator)
5. Use Global Tables only when needed (multi-region)
6. Efficient data modeling (item size, access patterns)
7. Use TTL to automatically delete expired items
8. Consider S3 for large objects with references in DynamoDB

**55. What is DynamoDB Global Tables?**

Global Tables provide multi-region, multi-active replication:
* Tables in multiple regions stay in sync
* Applications can read/write to any region
* Conflict resolution is last-writer-wins
* Built-in fault tolerance and high availability
* Replicates to all participating regions automatically

**56. What is Amazon ElastiCache for Redis vs Memcached?**

* Redis:
  * Supports data persistence (RDB, AOF)
  * Data structures (lists, sets, sorted sets, hashes)
  * Pub/sub messaging
  * Transactions
  * Lua scripting
  * Cluster mode for horizontal scaling

* Memcached:
  * Simple key-value only
  * No persistence
  * Multithreaded architecture
  * Auto-discovery
  * Generally lower latency for simple caching

**57. How do you handle connection management for RDS?**

Strategies:
1. Use RDS Proxy for connection pooling (serverless too)
2. Implement application-level connection pooling (HikariCP, pgbouncer)
3. Close connections properly in application code
4. Monitor max_connections parameter
5. Use IAM authentication for temporary credentials
6. Implement exponential backoff for connection retries

**58. What is Amazon DocumentDB vs DynamoDB?**

* DocumentDB:
  * MongoDB-compatible
  * Document model with flexible schema
  * ACID transactions
  * Similar to MongoDB API

* DynamoDB:
  * AWS-proprietary
  * Key-value and document
  * Fully serverless
  * Consistent performance at any scale
  * Different API and data model

**59. What is RDS Proxy?**

RDS Proxy is a fully managed, highly available database proxy for RDS and Aurora:
* Connection pooling reduces database load
* Faster failover for Aurora (up to 66% faster)
* IAM authentication and Secrets Manager integration
* Enhanced security (no direct DB access)
* Supports serverless applications

**60. How does Aurora Serverless work?**

Aurora Serverless automatically scales database capacity:
* ACU (Aurora Capacity Units) scale up/down based on actual usage
* No capacity planning needed
* Pay per second of actual usage
* Good for variable, unpredictable workloads
* Aurora Serverless v2 provides finer granularity and faster scaling

***

#### ## AWS CI/CD & DevOps

**61. What is the difference between AWS CodeDeploy In-Place and Blue/Green deployments?**

* In-Place: Updates instances while they're running. Instances go temporarily offline during deployment. Faster but no rollback.
* Blue/Green: Deploys new version to new instances (green), then switches traffic. Original instances (blue) kept for quick rollback. Zero downtime but requires double capacity.

**62. How does CodePipeline handle artifacts between stages?**

1. Source stage outputs artifact to S3 bucket
2. Build stage downloads artifact, processes, outputs new artifact
3. Subsequent stages receive artifact via S3
Artifacts are encrypted and versioned. Cross-region pipelines replicate artifacts to target region buckets.

**63. What is the difference between CodeBuild and CodeDeploy?**

* CodeBuild: Compiles source code, runs tests, produces build artifacts. Managed build service.
* CodeDeploy: Deploys code to compute platforms (EC2, Lambda, ECS, on-prem). Managed deployment service.
* Relationship: CodeBuild often feeds artifacts to CodeDeploy

**64. How do you implement approval gates in CodePipeline?**

Add a manual approval action to a stage:
1. Create an approval action in the pipeline stage
2. Configure SNS topic to notify approvers
3. Approver receives notification and reviews
4. Approver approves or rejects via console, CLI, or email
5. Pipeline continues or stops based on decision
Can also use Lambda for automated approvals based on custom logic.

**65. What is AWS CloudFormation StackSets?**

StackSets allow you to create, update, or delete CloudFormation stacks across multiple accounts and regions from a single template:
* Administrator account manages the StackSet
* Target accounts receive stack instances
* Can deploy to OU (Organizational Unit)
* Supports automatic deployment to new accounts
* Drift detection across all stack instances

**66. How does CloudFormation Drift Detection work?**

Drift detection identifies when stack resources have changed outside of CloudFormation:
1. Initiate drift detection on stack
2. CloudFormation compares actual resource state with expected state
3. Reports drifted resources and property changes
4. Can detect drift at the stack or resource level
Note: Does NOT automatically remediate drift

**67. What is AWS Systems Manager Parameter Store vs Secrets Manager?**

* Parameter Store:
  * Store configuration data, plaintext or SecureString
  * No automatic rotation
  * Free for standard parameters
  * Hierarchy support (/app/prod/db/password)
  * Integration with CloudFormation, EC2, ECS

* Secrets Manager:
  * Specifically for secrets (passwords, API keys)
  * Automatic rotation built-in
  * Cross-region replication
  * Costs for storage and API calls
  * Better for compliance requirements

**68. How do you automate AMI creation?**

Use EC2 Image Builder:
1. Create Image Builder pipeline
2. Define base AMI and components (packages, software)
3. Set up infrastructure configuration (instance type, VPC, IAM)
4. Schedule builds or trigger manually
5. Distribute to target regions and accounts
6. Automatically deprecate old AMIs
Alternative: Use Packer with AWS builder

**69. What is AWS Proton?**

AWS Proton is a fully managed delivery service for container and serverless applications:
* Platform teams define infrastructure templates
* Developers deploy using those templates
* Enforces consistency across deployments
* Integrated with CI/CD pipelines
* Tracks deployments and drift

**70. How do you implement Infrastructure as Code governance?**

Strategies:
1. Use CloudFormation Hooks for pre-deployment validation
2. Implement SCPs to restrict allowed services
3. Use Config Rules for compliance checking
4. Implement manual approvals in pipelines
5. Use Terraform Cloud/Enterprise with policy as code (Sentinel)
6. Run linting and security scanning (cfn-lint, cfn-nag)
7. Require code reviews for infrastructure changes

***

#### ## AWS Monitoring & Observability

**71. How do you create custom CloudWatch metrics?**

Three ways:
1. PutMetricData API: Directly publish metrics from application
2. CloudWatch Agent: Collect system-level metrics from EC2
3. Embedded Metric Format (EMF): JSON format for Lambda and containerized applications
Custom metrics are stored in CloudWatch and can be used for dashboards and alarms.

**72. What is CloudWatch Logs Insights?**

Logs Insights is a fully managed service for querying CloudWatch Logs:
* Purpose-built query language
* Auto-discovery of fields from JSON logs
* Aggregation functions (stats, sort, limit)
* Visualizations of query results
* Saved queries for reuse
* Integration with CloudWatch dashboards

**73. What is AWS X-Ray and how does distributed tracing work?**

X-Ray provides request tracing across distributed systems:
1. Instrument applications with X-Ray SDK
2. X-Ray daemon collects trace data
3. Service map visualizes application topology
4. Traces show latency of each component
5. Annotations and metadata add context
Integration with: Lambda, API Gateway, ELB, ECS, EKS, and custom applications

**74. How do you implement centralized logging in AWS?**

Architecture:
1. Applications send logs to CloudWatch Logs or Firehose
2. Firehose can deliver to S3, Elasticsearch, or third-party
3. Lambda can process/transform logs
4. S3 stores archived logs
5. Athena queries S3 logs ad-hoc
6. OpenSearch/Elasticsearch for real-time analysis
7. Grafana or Kibana for visualization

**75. What is CloudWatch Anomaly Detection?**

CloudWatch Anomaly Detection uses machine learning to:
* Automatically create baselines for metrics
* Detect unusual patterns
* Account for seasonality and trends
* Generate anomaly detection alarms
* Reduce false positives compared to static thresholds

**76. How do you monitor containerized applications?**

Tools and approaches:
1. CloudWatch Container Insights: Native monitoring for ECS/EKS
2. Prometheus + Grafana: Open-source monitoring
3. AWS Distro for OpenTelemetry: Collect traces and metrics
4. Fluent Bit: Log aggregation from containers
5. AWS X-Ray: Distributed tracing
6. Amazon Managed Service for Prometheus/Grafana: Managed open-source tools

**77. What is AWS CloudTrail Insights?**

CloudTrail Insights automatically detects unusual API activity:
* Analyzes CloudTrail management events
* Uses ML to establish baseline
* Alerts on anomalies (like spikes in API calls)
* Helps detect security incidents and operational issues
* Separate cost from standard CloudTrail

**78. How do you implement SLO-based alerting?**

1. Define SLIs (Service Level Indicators): Error rate, latency
2. Set SLO targets: 99.9% availability
3. Calculate error budgets: 1 - SLO = acceptable errors
4. Configure burn rate alerts:
   * Fast burn: Alert if error budget will exhaust in 2 days
   * Slow burn: Alert if error budget will exhaust in 30 days
5. Use CloudWatch math expressions for calculations
6. Create actionable alerts with runbook links

**79. What is Amazon DevOps Guru?**

Amazon DevOps Guru is an ML-powered service that:
* Analyzes operational data from CloudWatch, X-Ray, Config, etc.
* Detects anomalous behavior
* Provides insights and recommendations
* Identifies probable root causes
* Suggests remediation steps
* Reduces mean time to resolution (MTTR)

**80. How do you implement log retention and archival?**

Strategies:
1. CloudWatch Logs retention settings per log group
2. Export to S3 for long-term storage
3. Use lifecycle policies to move to Glacier
4. Kinesis Firehose for streaming to S3
5. VPC Flow Logs to S3 with partitioning
6. Query archived logs with Athena
7. Delete old logs per compliance requirements

***

#### ## AWS Security & Compliance

**81. What is AWS Security Hub?**

Security Hub is a centralized security management service that:
* Aggregates findings from GuardDuty, Inspector, Macie, etc.
* Provides security score and compliance status
* Implements CIS AWS Foundations and other standards
* Automates response with EventBridge rules
* Shows security trends over time

**82. How does AWS KMS envelope encryption work?**

1. Data key is generated for encryption
2. Data is encrypted with data key (envelope encryption)
3. Data key is encrypted with KMS key
4. Encrypted data key is stored with encrypted data
5. To decrypt: Decrypt data key with KMS, then decrypt data with data key
Benefits: Performance (symmetric encryption), key rotation, audit trail

**83. What is the difference between AWS KMS and CloudHSM?**

* AWS KMS:
  * Managed service, shared hardware
  * Automatic key rotation
  * AWS manages availability
  * Integrated with AWS services
  * Lower cost

* CloudHSM:
  * Dedicated hardware security module
  * Customer manages keys exclusively
  * FIPS 140-2 Level 3
  * Customer manages availability across AZs
  * Higher cost, more control

**84. What is AWS Nitro Enclaves?**

Nitro Enclaves allow you to create isolated compute environments:
* Process sensitive data in isolated environment
* Separate from parent EC2 instance
* No persistent storage, no interactive access
* Cryptographic attestation for identity
* Use cases: PCI DSS, private key protection, data processing

**85. How do you implement DDoS protection in AWS?**

Multi-layer approach:
1. AWS Shield Standard: Automatic for all customers (L3/L4)
2. AWS Shield Advanced: Enhanced protection, 24/7 DRT, cost protection
3. AWS WAF: Application layer protection (L7)
4. CloudFront: Edge caching and DDoS absorption
5. Route 53: DNS protection
6. Auto Scaling: Absorb traffic spikes
7. VPC Flow Logs: Monitor for attacks

**86. What is AWS Firewall Manager?**

Firewall Manager simplifies security management across accounts:
* Centrally configure WAF rules, Shield Advanced, Security Groups
* Apply policies across entire organization
* Auto-remediate non-compliant resources
* Works with Organizations
* Integrates with Config for compliance monitoring

**87. How do you implement secrets rotation in AWS?**

Using AWS Secrets Manager:
1. Store secret (database password, API key)
2. Configure rotation schedule
3. Use built-in Lambda functions for common databases (RDS, DocumentDB)
4. Or create custom Lambda rotation function
5. Secret is rotated automatically on schedule
6. Applications retrieve current version via API

**88. What is Amazon Macie?**

Amazon Macie is a fully managed data security and data privacy service that uses machine learning and pattern matching to discover and protect sensitive data in S3:
* Automatically discovers sensitive data (PII, financial data)
* Provides visibility into data security posture
* Detects anomalous access patterns
* Alerts on data security risks
* Generates detailed findings

**89. How does AWS Config conformance packs work?**

Conformance packs are collections of Config rules and remediation actions:
* Pre-built packs for compliance frameworks (PCI DSS, HIPAA)
* Custom packs for organizational standards
* Deployed across accounts and regions
* Compliance dashboard shows compliance status
* Drift detection identifies non-compliant resources

**90. What is VPC Traffic Mirroring?**

VPC Traffic Mirroring allows you to copy network traffic from an elastic network interface:
* Send traffic to security appliances for inspection
* Capture packets for analysis
* Filter traffic to reduce volume
* Deliver to NLB or EC2 instance
* Use cases: security monitoring, troubleshooting, compliance

***

#### ## AWS Serverless

**91. What are Lambda execution models and limits?**

Execution models:
* Synchronous: Request waits for response (API Gateway)
* Asynchronous: Event queued, immediate 202 response (S3 events)
* Poll-based: Lambda polls service (SQS, Kinesis, DynamoDB Streams)

Limits:
* 15-minute maximum execution time
* 10GB memory maximum
* 6MB payload (sync), 256KB (async)
* 1000 concurrent executions default (adjustable)
* 75GB deployment package size (container images)

**92. How does Lambda concurrency work?**

* Reserved Concurrency: Guarantees maximum instances for a function, also limits maximum
* Provisioned Concurrency: Pre-initialized execution environments, eliminates cold starts
* Unreserved Concurrency: Shared pool for functions without reserved concurrency
* Account limit: Total concurrent executions across all functions in a region

**93. What is the difference between Lambda destinations and dead-letter queues?**

* Dead Letter Queues (DLQ): Send failed async invocations to SQS or SNS for retry
* Destinations: More flexible, can send success AND failure results to:
  * SQS (for queue processing)
  * SNS (for notifications)
  * Lambda (for chaining)
  * EventBridge (for event routing)
* Destinations only work with async invocations

**94. How do you optimize Lambda cold starts?**

Strategies:
1. Use Provisioned Concurrency
2. Optimize deployment package size
3. Use appropriate memory allocation (more memory = more CPU)
4. Use Lambda layers for dependencies
5. Initialize outside handler (reuse connections)
6. Choose appropriate runtime (compiled languages have higher cold start)
7. Use SnapStart for Java functions

**95. What is AWS Step Functions?**

Step Functions is a workflow orchestration service:
* Visual workflow designer
* Coordinate multiple Lambda functions and AWS services
* Error handling, retries, and parallel execution
* State machines define workflow logic
* Express workflows for high-volume, short-duration
* Standard workflows for long-running, audit trail

**96. How do you secure API Gateway?**

1. Use IAM authentication for internal APIs
2. Cognito User Pools for user authentication
3. Lambda Authorizers (custom auth logic)
4. API Keys for throttling and metering
5. WAF integration for DDoS and OWASP protection
6. Mutual TLS (mTLS) for certificate-based auth
7. Resource policies for IP restrictions
8. CloudWatch logging for audit trail

**97. What is the difference between API Gateway REST API and HTTP API?**

* REST API:
  * Full feature set
  * Request/response transformation
  * WAF integration
  * AWS IAM auth
  * Caching capabilities
  * Higher cost

* HTTP API:
  * Lower latency and cost
  * Basic JWT/OAuth support
  * No transformation
  * No caching
  * Good for proxying to Lambda/HTTP backends

**98. What is Amazon EventBridge?**

EventBridge is a serverless event bus service:
* Event bus receives events from AWS services, SaaS apps, custom apps
* Rules match events and route to targets
* Schema registry for event discovery
* Archive and replay events
* Replace CloudWatch Events (superset)
* Cross-region event routing

**99. How does Lambda@Edge work?**

Lambda@Edge runs Lambda functions at CloudFront edge locations:
* Triggered by CloudFront events (viewer request, origin request, origin response, viewer response)
* Modify requests/responses at the edge
* Customize content based on user location, device, etc.
* Reduce latency by processing closer to users
* Limitations: Smaller deployment package, limited runtime, shorter timeout (5-30 seconds)

**100. What is AWS AppSync?**

AWS AppSync is a managed GraphQL service:
* Real-time data with GraphQL subscriptions
* Offline data synchronization
* Connects to DynamoDB, Lambda, HTTP, RDS
* Automatic authorization and authentication
* Built-in conflict resolution
* Scales automatically
