#### 🔹 1. Improved Notes: AWS Architecture
*   **Well-Architected Framework:** The 5 pillars: Operational Excellence, Security, Reliability, Performance Efficiency, and Cost Optimization.
*   **Scalability vs. Elasticity:**
    *   **Scalability:** The ability to handle more load (e.g., a bigger server).
    *   **Elasticity:** The ability to scale up *and* down automatically based on demand (e.g., Auto Scaling Groups).
*   **Route 53:** AWS's highly available DNS service. It supports health checks and advanced routing (Latency, Geo-location).

#### 🔹 2. Interview View (Q&A)
*   **Q:** What is the difference between a `Public Subnet` and a `Private Subnet`?
*   **A:** A Public Subnet has a route to an **Internet Gateway**. A Private Subnet does not and typically uses a **NAT Gateway** for outbound-only internet access.
*   **Q:** Explain `IAM Roles` vs. `IAM Users`.
*   **A:** Users are for people. Roles are for services (like an EC2 instance) to securely access other AWS services without hardcoding access keys.

***

#### 🔹 3. Architecture & Design: Three-Tier Web App
A classic, secure cloud design:
1.  **Web Tier:** Public subnet with a Load Balancer.
2.  **App Tier:** Private subnet for the application servers.
3.  **Data Tier:** Private subnet for the Database (not accessible from the internet).

***

#### 🔹 4. Commands & Configs (AWS CLI)
```bash
# List all S3 buckets
aws s3 ls

# Copy a file to S3
aws s3 cp localfile.txt s3://my-bucket/

# Get info about an EC2 instance
aws ec2 describe-instances --instance-ids i-1234567890

# Set up your CLI credentials
aws configure
```

***

#### 🔹 5. Troubleshooting & Debugging
*   **Scenario:** You can't SSH into your EC2 instance.
*   **Fix:** Check the **Security Group** (Is port 22 open?), the **Network ACL**, and ensure the instance has a Public IP and the VPC has an Internet Gateway.
*   **CloudWatch Logs:** The first place to look for application errors or Lambda failures.

***

#### 🔹 6. Production Best Practices
*   **Least Privilege:** Never give a service `AdministratorAccess`. Give exactly the permissions it needs.
*   **Enable MFA:** Multifactor Authentication is mandatory for the Root account and all IAM users.
*   **Tagging:** Use consistent tags (e.g., `Project: XYZ`, `Env: Prod`) for billing and management.
*   **Cost Explorer:** Regularly check for "Zombie Resources" (Elastic IPs or EBS volumes not attached to anything).

***

#### 🔹 Cheat Sheet / Quick Revision
| **Service** | **Category** | **DevOps Use Case** |
| :--- | :--- | :--- |
| `CloudFormation` | IaC | AWS's native version of Terraform. |
| `CloudTrail` | Governance | Auditing "who did what" in the AWS account. |
| `ACM` | Security | Managing SSL/TLS certificates for your websites. |
| `EBS` | Storage | The "hard drive" for your EC2 instances. |

***

This is Section 13: AWS. For a senior role, you should focus on **Direct Connect**, **Transit Gateway**, and **Control Tower** for multi-account management.
