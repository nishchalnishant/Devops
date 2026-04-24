## Easy

**1. What is Terraform and how does it differ from Ansible?**

Terraform is an Infrastructure as Code tool for provisioning and managing the lifecycle of infrastructure resources. Ansible is a configuration management tool for configuring software on that infrastructure. Terraform provisions the house; Ansible furnishes it. Terraform is declarative; Ansible is more procedural.

**2. What is the Terraform state file and why is it important?**

The state file (`terraform.tfstate`) tracks all resources Terraform manages, mapping configuration to real-world resources with their IDs and current attributes. It is essential for planning and applying future changes — without it, Terraform cannot determine what exists and what to create, update, or destroy.

**3. What does `terraform plan` do?**

It creates an execution plan — compares the desired state in your configuration with the current state in the state file and shows exactly what will be created, updated, or destroyed if you run `terraform apply`. No changes are made.

**4. What does `terraform init` do?**

It initializes the working directory: downloads required provider plugins, sets up the backend for state file storage, and installs any required modules. Always run it first in a new Terraform project or after changing the backend or providers.

**5. What is a Terraform provider?**

A provider is a plugin that allows Terraform to interact with a specific API — a cloud platform like AWS or Azure, a SaaS provider like Cloudflare, or on-premises technology like VMware vSphere. Each provider must be declared and configured in the Terraform configuration.

**6. Why is it important to keep the Terraform state file secure?**

The state file can contain sensitive data in plain text — database passwords, private keys, and API credentials. Store it in a secure, encrypted, access-controlled remote backend (S3 bucket with SSE + DynamoDB locking, Azure Blob Storage with encryption).

**7. What is a Terraform module?**

A module is a container for multiple Terraform resources that are used together. Every Terraform configuration is a module. You call child modules to encapsulate and reuse infrastructure patterns — a VPC module, an EKS cluster module — with input variables and output values.

**8. What is the `terraform import` command?**

`terraform import` brings an existing real-world resource under Terraform management without recreating it. It populates state with the resource's current attributes. Used when infrastructure was created manually and needs to be managed as code going forward.

---

