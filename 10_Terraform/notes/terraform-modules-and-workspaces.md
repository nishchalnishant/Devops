---
description: Terraform modules, workspaces, Terragrunt, and enterprise IaC patterns for senior engineers.
---

# Terraform — Modules, Workspaces & Enterprise Patterns

## Module Architecture

A module is any directory containing `.tf` files. The **root module** is your main configuration; **child modules** are reusable components you call.

```
infrastructure/
├── main.tf                  ← Root module (calls child modules)
├── variables.tf
├── outputs.tf
└── modules/
    ├── vpc/                 ← Child module: VPC
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    ├── eks/                 ← Child module: EKS cluster
    └── rds/                 ← Child module: RDS database
```

### Calling a Module

```hcl
# infrastructure/main.tf

module "vpc" {
  source  = "./modules/vpc"     # Local module
  # source = "terraform-aws-modules/vpc/aws"  # Registry module
  version = "~> 5.0"           # Version constraint (registry only)

  name       = "prod-vpc"
  cidr       = "10.0.0.0/16"
  azs        = ["us-east-1a", "us-east-1b", "us-east-1c"]
  
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true
  single_nat_gateway = false   # HA: one NAT per AZ
}

# Use module outputs
module "eks" {
  source = "./modules/eks"
  vpc_id          = module.vpc.vpc_id
  subnet_ids      = module.vpc.private_subnets
}
```

### Module Output Chaining

```hcl
# modules/vpc/outputs.tf
output "vpc_id" {
  value       = aws_vpc.main.id
  description = "The ID of the VPC"
}

output "private_subnets" {
  value       = aws_subnet.private[*].id
}
```

***

## Workspaces — When (and When NOT) to Use Them

Workspaces create isolated state files within the same backend, sharing the same codebase.

```bash
# Create and switch to a workspace
terraform workspace new staging
terraform workspace new production

# List workspaces
terraform workspace list
# * staging
#   production
#   default

# Apply with workspace-specific values
terraform workspace select production
terraform apply
```

### Using Workspace Name in Configuration

```hcl
locals {
  env = terraform.workspace    # "staging" or "production"
  
  instance_type = {
    staging    = "t3.micro"
    production = "m5.xlarge"
  }
}

resource "aws_instance" "web" {
  instance_type = local.instance_type[local.env]
}
```

### Workspace Limitations — Why Terragrunt is Better at Scale

| Issue | Workspaces | Terragrunt (DRY approach) |
|:---|:---|:---|
| **State isolation** | Same bucket, different key | Separate buckets per env |
| **Variable management** | Same vars.tf, complex locals | Separate `env.hcl` per environment |
| **Code differences** | Hard to have truly different configs | Different module versions per env |
| **Access control** | One set of provider credentials | Separate assume-role per env |

***

## Terragrunt — DRY IaC at Scale

```
infrastructure/
├── terragrunt.hcl           ← Root config (backend, provider)
├── dev/
│   ├── env.hcl              ← Dev environment variables
│   └── vpc/
│       └── terragrunt.hcl
├── staging/
│   └── vpc/
│       └── terragrunt.hcl
└── production/
    └── vpc/
        └── terragrunt.hcl
```

**Root `terragrunt.hcl`:**
```hcl
# Generate the backend config dynamically
remote_state {
  backend = "s3"
  config = {
    bucket = "my-tf-state-${get_aws_account_id()}"
    key    = "${path_relative_to_include()}/terraform.tfstate"
    region = "us-east-1"
    encrypt = true
    dynamodb_table = "terraform-locks"
  }
}
```

**Environment-specific `terragrunt.hcl`:**
```hcl
# production/vpc/terragrunt.hcl
include "root" {
  path = find_in_parent_folders()
}

terraform {
  source = "../../../../modules//vpc"   # // = module root
}

inputs = {
  name = "production-vpc"
  cidr = "10.0.0.0/16"
  enable_nat_gateway = true
}
```

***

## For_each vs Count

```hcl
# COUNT — positional, fragile
resource "aws_iam_user" "users" {
  count = length(var.user_names)
  name  = var.user_names[count.index]
}
# Deleting user at index 0 shifts ALL indices → destroys and recreates users 1..N

# FOR_EACH — key-based, stable
resource "aws_iam_user" "users" {
  for_each = toset(var.user_names)
  name     = each.value
}
# Deleting one user only affects that user's resource
```

***

## Logic & Trickiness Table

| Concept | Junior Thinking | Senior Thinking |
|:---|:---|:---|
| **Modules** | One monolithic main.tf | Separate module per logical component |
| **Workspaces** | Great for multi-env | Use Terragrunt for truly isolated envs |
| **count vs for_each** | Use count always | Use for_each for collections (avoids index shifting) |
| **`terraform import`** | Use when needed | Keep an audit log; always follow up with a data source |
| **`depends_on`** | Rarely use it | Prefer implicit dependency (resource references) |
| **Provider versions** | `version = ">= 4.0"` | `version = "~> 4.67"` for patch-level flexibility only |
