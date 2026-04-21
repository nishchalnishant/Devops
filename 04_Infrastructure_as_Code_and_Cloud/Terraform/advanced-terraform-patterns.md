# Advanced Terraform Patterns & State Manipulation (7 YOE)

At the senior and staff levels, writing standard HCL code is a minimum expectation. Real engineering deals with multi-account scaling, avoiding state file corruption, and executing zero-downtime refactors of live infrastructure.

---

## 1. Multi-Environment Architecture: Terragrunt vs. Workspaces

Terraform Workspaces allow you to use the same directory of code for multiple environments (e.g., `terraform workspace new dev`). However, virtually all senior engineers avoid them for large-scale production in favor of directory-based isolation or Wrappers like **Terragrunt**.

### Why Workspaces Fail at Scale
- A single typo affects all environments simultaneously.
- You cannot use different provider versions across environments.
- State access controls are extremely difficult to implement per-workspace via IAM.

### The Terragrunt Directory Pattern
Terragrunt keeps your code DRY (Don't Repeat Yourself) while maintaining hard directory isolation.

```text
├── modules/
│   └── vpc/
│       ├── main.tf
│       └── variables.tf
└── live/
    ├── terragrunt.hcl          # Global backend & provider config
    ├── _envcommon/             # Shared variables for all environments
    │   └── vpc.hcl
    ├── dev/
    │   └── us-east-1/
    │       └── vpc/
    │           └── terragrunt.hcl # Includes common vpc config + sets dev inputs
    └── prod/
        └── us-east-1/
            └── vpc/
                └── terragrunt.hcl # Includes common vpc config + sets prod inputs
```

**Benefits:** Hard boundaries. To ruin production, you must explicitly run `apply` inside the `prod/` directory. Backend configurations are dynamically generated.

---

## 2. Advanced State Manipulation (Zero-Downtime Refactoring)

If an infrastructure component needs to move from a monolithic state file to a modular state file, you *cannot* just cut-and-paste the code. Doing so forces Terraform to `destroy` the live resource and `create` it in the new module. 

A 7 YOE engineer manipulates the state file directly.

### Relocating a Resource into a Module (`state mv`)
You wrote an `aws_s3_bucket` natively, but now you want to move it inside a custom `module.storage`.

```bash
# Code change:
# 1. Update the .tf code to use the module.
# 2. DO NOT run terraform plan or apply yet.

# Move the state:
terraform state mv aws_s3_bucket.app_data module.storage.aws_s3_bucket.this

# Verify:
terraform plan # Should show "No changes"
```

### Decoupling State Files (`state rm` and `import`)
A single `monolith.tfstate` is locking up your entire team. You need to split the VPC components off from the App components.

```bash
# 1. Backup the state
terraform state pull > monolith.tfstate.backup

# 2. Remove the VPC network from the current state file 
# (This does NOT destroy the cloud infrastructure)
terraform state rm module.vpc

# 3. In a new folder (Network_IaC), initialize a fresh Terraform workspace
# 4. Import the live VPC into the new state file
terraform import module.vpc.aws_vpc.main vpc-0a1b2c3d4e5f6g7h8

# 5. Run plan in both directories. Both should say "No changes".
```

---

## 3. Advanced HCL Concepts

### Dynamic Blocks
Often you need to conditionally generate nested blocks (like `ingress` blocks in a Security Group) based on an input list.

```hcl
resource "aws_security_group" "web" {
  name        = "web-sg"
  description = "Allow web traffic"
  vpc_id      = var.vpc_id

  dynamic "ingress" {
    for_each = var.allowed_ports
    content {
      from_port   = ingress.value
      to_port     = ingress.value
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
    }
  }
}
```

### Variable Validation & Custom Errors
Failing fast locally is better than failing 10 minutes deep into a cloud API request. Enforce strict types.

```hcl
variable "instance_type" {
  type        = string
  description = "The EC2 instance type to deploy"

  validation {
    condition     = can(regex("^t3\\.|^m5\\.", var.instance_type))
    error_message = "The instance type must be a t3 or m5 series VM."
  }
}
```

### Preconditions and Postconditions (Terraform 1.2+)
Validating variables is great, but sometimes you need to validate the *result* of a Data Source or a Resource creation.

```hcl
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]

  lifecycle {
    postcondition {
      condition     = self.creation_date > timeadd(timestamp(), "-8760h") # 1 year
      error_message = "The selected AMI is more than 1 year old and poses a security risk."
    }
  }
}
```
