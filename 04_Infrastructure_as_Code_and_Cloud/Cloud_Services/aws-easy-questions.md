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
