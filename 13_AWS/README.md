# Cloud Services (AWS)

Amazon Web Services (AWS) is the pioneer of cloud computing. For a DevOps engineer, AWS is not just a place to host servers; it is a giant API that provides compute, storage, networking, and managed services on demand.

#### 1. The Global Infrastructure
*   **Regions:** Physical locations around the world (e.g., `us-east-1`). Each region is independent.
*   **Availability Zones (AZs):** Isolated data centers within a region. Deploying across multiple AZs is the key to **High Availability**.
*   **Edge Locations:** Content Delivery Network (CloudFront) sites that cache data closer to users for lower latency.

#### 2. The Core "Big Four" Services
1.  **EC2 (Elastic Compute Cloud):** Virtual servers in the cloud.
2.  **S3 (Simple Storage Service):** Object storage for files, backups, and static websites. "Infinite" scale and 99.999999999% (11 nines) durability.
3.  **VPC (Virtual Private Cloud):** Your private slice of the AWS network. You control the IP range, subnets, and routing.
4.  **IAM (Identity and Access Management):** The security gatekeeper. It controls who can access what.

#### 3. Security & The Shared Responsibility Model
*   **AWS Responsibility:** Security **of** the Cloud (Hardware, physical security, global infrastructure).
*   **Your Responsibility:** Security **in** the Cloud (Your data, OS patching, IAM policies, network firewalls).

#### 4. Managed Services (PaaS)
Instead of managing your own databases or queues, AWS provides managed versions:
*   **RDS (Relational Database Service):** Managed SQL (Postgres, MySQL, Aurora). Handles backups and patching for you.
*   **Lambda:** "Serverless" computing. Run code without managing a single server.
*   **EKS (Elastic Kubernetes Service):** Managed Kubernetes control plane.

***

