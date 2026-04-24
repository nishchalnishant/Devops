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


**9. What is HCL and what are the basic building blocks of a Terraform configuration?**

HCL (HashiCorp Configuration Language) is the declarative language Terraform uses. Core building blocks:
- `resource`: declares a managed infrastructure object (`resource "aws_instance" "web" { ... }`)
- `variable`: declares an input parameter with optional type, default, and validation
- `output`: exposes a value after apply (consumed by other modules or users)
- `data`: reads existing infrastructure not managed by this configuration
- `locals`: defines computed values reused within a module
- `module`: calls a child module with inputs
- `provider`: configures a cloud/API plugin

**10. What is the difference between `terraform.tfvars` and a variable definition?**

A variable is declared in `.tf` files with `variable "name" {}` — it defines the input but gives it no value. `terraform.tfvars` (or `*.auto.tfvars`) provides the actual values for those variables. You can have multiple `.tfvars` files for different environments (dev.tfvars, prod.tfvars) and pass them with `-var-file=prod.tfvars`. Environment variables `TF_VAR_<name>` also set variable values.

**11. What is `terraform destroy` and when would you use it?**

`terraform destroy` creates a plan to delete all resources managed by the current state and prompts for confirmation. Used for: tearing down ephemeral environments (feature branch environments, CI test stacks), decommissioning old infrastructure. For selective deletion, use `terraform destroy -target=resource_type.resource_name`. Always run `plan` first to review what will be deleted.

**12. What are Terraform workspaces?**

Workspaces allow a single Terraform configuration to manage multiple, separate state files. `terraform workspace new staging` creates a new workspace; `terraform workspace select prod` switches to it. Each workspace gets its own `terraform.tfstate`. Useful for lightweight environment separation. Limitation: all workspaces share the same backend configuration and code — for strict environment isolation, separate state paths (via Terragrunt or different backend configs) are more common in production.

**13. What does `terraform fmt` do and why should it be enforced in CI?**

`terraform fmt` rewrites `.tf` files to the canonical HCL formatting style (indentation, alignment, spacing). `terraform fmt -check` exits non-zero if any file would be changed — useful as a CI gate to enforce consistent formatting across the team. Prevents style-related diff noise in code reviews.

**14. What is the `depends_on` meta-argument?**

`depends_on` explicitly declares a dependency between resources when Terraform cannot infer it automatically from reference expressions. Used when one resource depends on the side effects of another (e.g., an IAM policy attachment must complete before an ECS task can start, but there's no direct reference between them). Overuse is a code smell — if you find yourself using it often, reconsider your module structure.

**15. What is a `data` source in Terraform?**

A data source reads existing infrastructure that Terraform doesn't manage and makes its attributes available in configuration:
```hcl
data "aws_vpc" "main" {
  tags = { Name = "main-vpc" }
}

resource "aws_subnet" "app" {
  vpc_id = data.aws_vpc.main.id
}
```
Common uses: look up an AMI ID, fetch a secret from Secrets Manager, reference a VPC or DNS zone created by another Terraform config.
