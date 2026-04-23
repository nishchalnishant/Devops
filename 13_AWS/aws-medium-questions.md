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
