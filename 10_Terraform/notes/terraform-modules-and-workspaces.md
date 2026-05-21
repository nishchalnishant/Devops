---
description: Terraform modules, workspaces, Terragrunt, and enterprise IaC patterns for senior engineers.
---

# Terraform — Modules, Workspaces & Enterprise Patterns

```
Terraform Modules, Workspaces & Enterprise Patterns
├── Module Architecture
│   ├── Root module: main config (calls child modules)
│   ├── Child module: reusable component with variable inputs + outputs
│   ├── Source types: local path, Git URL, Terraform Registry
│   ├── version pinning: exact pin in production (version = "5.5.2")
│   └── Output chaining: module A outputs → consumed by module B
├── Module Design
│   ├── Encapsulate a service boundary (VPC, EKS cluster, RDS)
│   ├── Expose outputs: IDs, ARNs, endpoints, SG IDs
│   ├── Use locals for computed values, variables for inputs
│   └── Semantic versioning via Git tags (MAJOR.MINOR.PATCH)
├── Workspaces
│   ├── Create: terraform workspace new staging
│   ├── Switch: terraform workspace select prod
│   ├── Use in HCL: terraform.workspace
│   ├── Limitations: share backend config + code → weak isolation
│   └── When to use: feature-branch infra, truly identical topology only
├── Workspace Limitations
│   ├── All workspaces share provider config
│   ├── Cannot have different backend bucket per workspace (without tricks)
│   └── Production isolation requires separate state paths, not workspaces
├── Terragrunt (DRY Wrapper)
│   ├── Root terragrunt.hcl: shared provider + backend generation
│   ├── Env-specific terragrunt.hcl: inputs override per environment
│   ├── dependency {} block: consume outputs from sibling modules
│   ├── run-all plan/apply: execute across module hierarchy in order
│   └── generate {} blocks: inject provider.tf and backend.tf per module
├── for_each vs count at Module Level
│   ├── count with module: creates module[0], module[1]... (fragile)
│   └── for_each with module: creates module["key"]... (stable identity)
└── Enterprise Patterns
    ├── Private module registry: version-controlled, discoverable
    ├── Atlantis: PR-based plan/apply workflow (GitOps)
    ├── Terraform Cloud workspaces: team RBAC + remote execution
    └── Sentinel: policy-as-code gate between plan and apply
```

## First Principles

- A module is a function: it takes inputs (variables) and returns outputs. The implementation (resources inside) is hidden from the caller. This encapsulation allows refactoring internals without breaking callers, as long as the variable/output interface is preserved.
- Workspaces are isolated state namespaces within the same backend configuration. They are NOT separate environments if your environments differ in topology, account ID, or provider config. For real environment isolation, use separate state paths or separate directories.
- Terragrunt is a thin wrapper that solves the DRY problem: you define provider config and backend config once in a root `terragrunt.hcl`, and every child module inherits it via `include`. Without Terragrunt, you copy-paste backend config into every module directory.
- The `dependency {}` block in Terragrunt creates explicit ordering between modules: EKS depends on VPC, application depends on EKS. `run-all apply` respects this order automatically — no manual sequencing.
- Module versioning via Git tags creates a publishable API. `version = "5.5.2"` pins a specific commit. Upgrading to `5.6.0` is a conscious, reviewable decision — not a silent pull of the latest code.

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

***

## System Design Perspective

**Module registry as an internal platform:** A private Terraform module registry (Terraform Cloud, Artifactory, or a simple Git repo with tags) is an internal platform API. Platform teams publish `module "eks-cluster"`, `module "postgres-rds"`, `module "vpc"`. Application teams consume these modules with version pins — they get compliant infrastructure without needing to know the implementation. This is the IaC analog of a PaaS.

**Workspace anti-pattern at scale:** Imagine 10 environments (dev, staging, perf, prod-us, prod-eu, prod-ap, ...). Using workspaces means one HCL codebase with `terraform.workspace == "prod-us" ? "m5.2xlarge" : "t3.medium"` scattered throughout. This becomes unmaintainable quickly. The Terragrunt directory model (one directory per environment, each calling the same module with different inputs) scales cleanly.

**Terragrunt dependency graph as organizational structure:** The Terragrunt dependency graph mirrors your organizational ownership. VPC (networking team) → EKS (platform team) → services (app teams). `run-all apply` applies in topological order. `run-all destroy` applies in reverse order. The graph is both operational and organizational documentation.

**Breaking changes in modules:**
- MAJOR version: removes or renames an input variable, changes a resource address (causing destroy/recreate), removes an output.
- MINOR version: adds an optional variable with a default, adds an output, adds a new resource that doesn't affect existing ones.
- PATCH version: bug fix that doesn't change the resource plan output.
- Communicate breaking changes in a CHANGELOG. Provide a migration guide (which `moved {}` blocks to add, which variables to rename). Bump the major version tag and let consumers opt in.
