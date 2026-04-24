# Infrastructure as Code (Terraform)

Terraform is the world's most popular Infrastructure as Code (IaC) tool. It allows you to define your data center infrastructure in a declarative configuration language (HCL) and manage its lifecycle across any cloud provider.

#### 1. Why Terraform?
*   **Declarative:** You describe the "Desired State" (e.g., "I want 3 servers"), and Terraform figures out how to make it happen.
*   **Cloud Agnostic:** You can use the same tool to manage AWS, Azure, GCP, and even local resources like Docker or VMware.
*   **Immutable Infrastructure:** Instead of logging into a server and changing its config, you change the code and Terraform replaces the server with a new one.

#### 2. The Core Workflow
1.  **Write:** Write your infrastructure code in `.tf` files using HCL (HashiCorp Configuration Language).
2.  **Init:** Run `terraform init` to download the "Providers" (plugins) needed to talk to your cloud.
3.  **Plan:** Run `terraform plan` to see what changes Terraform *would* make without actually doing them.
4.  **Apply:** Run `terraform apply` to create or update your infrastructure.

#### 3. State: The Source of Truth
Terraform keeps track of everything it creates in a file called `terraform.tfstate`.
*   **Why it's critical:** Terraform compares your code to this state file to decide what needs to be added, changed, or deleted.
*   **Remote State:** In a team, you **must** store this state file in a central location (like an S3 bucket) with **State Locking** (using DynamoDB) to prevent two people from making changes at the same time.

#### 4. Modules: Reusable Infrastructure
Instead of copy-pasting code for every environment, you create **Modules**. A module is a container for multiple resources that are used together. For example, a "VPC Module" could create a network, subnets, and routing tables all at once.

***

