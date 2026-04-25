# Terraform Cheatsheet

## Core Workflow

```bash
terraform init                        # initialize: download providers, set up backend
terraform init -upgrade               # upgrade provider versions within constraints
terraform init -backend-config=prod.hcl  # partial backend config (for secrets)

terraform plan                        # show changes (no write)
terraform plan -out=plan.tfplan       # save plan for deterministic apply
terraform plan -target=aws_instance.web  # plan only one resource
terraform plan -destroy               # preview destroy

terraform apply                       # apply (re-plans)
terraform apply plan.tfplan           # apply saved plan (no recompute)
terraform apply -auto-approve         # skip confirmation (CI only)
terraform apply -target=module.vpc    # apply single module

terraform destroy                     # destroy all managed resources
terraform destroy -target=aws_rds_cluster.main  # destroy one resource
```

## State Management

```bash
terraform state list                  # list all resources in state
terraform state show aws_instance.web # show state for one resource
terraform state mv aws_instance.web aws_instance.web_server  # rename (prefer `moved` block)
terraform state rm aws_s3_bucket.legacy  # remove from state without deleting real resource
terraform state pull > state.json     # dump state to stdout
terraform state push state.json       # push local state to remote backend (dangerous)

terraform force-unlock <LOCK_ID>      # release stuck DynamoDB lock
terraform refresh                     # reconcile state with real infra (deprecated in 1.x, use plan -refresh-only)
terraform plan -refresh-only          # show drift without proposing changes
```

## Import

```bash
# Terraform < 1.5 (imperative)
terraform import aws_instance.web i-0abc123def456
terraform import 'aws_s3_bucket.this["logs"]' my-logs-bucket  # for_each resource

# Terraform >= 1.5 (declarative import block)
import {
  to = aws_instance.web
  id = "i-0abc123def456"
}
# then: terraform plan  →  terraform apply
```

## Workspace Commands

```bash
terraform workspace list
terraform workspace new staging
terraform workspace select prod
terraform workspace show              # current workspace name
terraform workspace delete staging
```

Use `${terraform.workspace}` in config to branch on workspace name:
```hcl
locals {
  env = terraform.workspace  # "default", "staging", "prod"
}
```

## Output and Format

```bash
terraform output                      # show all outputs
terraform output -json                # machine-readable
terraform output -raw db_endpoint     # raw string (no quotes)
terraform fmt                         # format all .tf files in place
terraform fmt -check                  # exit 1 if any file needs formatting (CI gate)
terraform fmt -recursive              # format subdirectories too
terraform validate                    # syntax + schema validation (no API calls)
```

## Graph and Debug

```bash
terraform graph | dot -Tsvg > graph.svg   # visual dependency graph (requires graphviz)
TF_LOG=DEBUG terraform apply              # verbose provider + API logs
TF_LOG_PATH=tf.log terraform apply        # write logs to file
```

## Provider Version Pinning

```hcl
terraform {
  required_version = ">= 1.6, < 2.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"   # allows 5.x, blocks 6.x
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "2.27.0"   # exact pin for stability
    }
  }
}
```

Lock file `.terraform.lock.hcl` records exact checksums — commit it to version control.

## Backend Configuration

### S3 + DynamoDB (AWS)
```hcl
terraform {
  backend "s3" {
    bucket         = "my-tf-state-prod"
    key            = "services/api/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-lock"
    encrypt        = true
    kms_key_id     = "arn:aws:kms:us-east-1:123456789:key/abc"
  }
}
```

### Azure Blob
```hcl
terraform {
  backend "azurerm" {
    resource_group_name  = "tfstate-rg"
    storage_account_name = "tfstateprod"
    container_name       = "tfstate"
    key                  = "prod.terraform.tfstate"
  }
}
```

### Partial backend config (avoid hardcoding in code):
```bash
terraform init -backend-config="bucket=my-tf-state" \
               -backend-config="key=prod/api/terraform.tfstate"
```

## Variable Precedence (highest to lowest)

1. `-var` flag: `terraform apply -var="instance_type=t3.large"`
2. `-var-file` flag: `terraform apply -var-file=prod.tfvars`
3. `*.auto.tfvars` files (alphabetical order)
4. `terraform.tfvars`
5. `TF_VAR_<name>` environment variables
6. Variable default values in `variable {}` block

## HCL Quick Reference

### Variable types
```hcl
variable "region" {
  type    = string
  default = "us-east-1"
}

variable "az_count" {
  type        = number
  description = "Number of AZs to use"
  validation {
    condition     = var.az_count >= 2
    error_message = "Must use at least 2 AZs for HA."
  }
}

variable "tags" {
  type = map(string)
  default = {
    Environment = "prod"
    Team        = "platform"
  }
}

variable "allowed_cidr_blocks" {
  type = list(string)
}
```

### Locals
```hcl
locals {
  common_tags = merge(var.tags, {
    ManagedBy = "terraform"
    Workspace = terraform.workspace
  })
  name_prefix = "${var.project}-${var.environment}"
}
```

### Dynamic blocks
```hcl
resource "aws_security_group" "this" {
  name = "web"

  dynamic "ingress" {
    for_each = var.ingress_rules
    content {
      from_port   = ingress.value.from_port
      to_port     = ingress.value.to_port
      protocol    = ingress.value.protocol
      cidr_blocks = ingress.value.cidr_blocks
    }
  }
}
```

### Conditional expressions
```hcl
instance_type = var.environment == "prod" ? "m5.xlarge" : "t3.medium"
count         = var.create_instance ? 1 : 0
```

### String functions
```hcl
lower(var.name)
upper(var.region)
format("%-20s", var.name)
"${var.project}-${var.env}"          # interpolation
templatefile("${path.module}/user_data.sh.tpl", { db_host = var.db_host })
file("${path.module}/scripts/init.sh")
jsonencode({ key = "value" })
```

### Collection functions
```hcl
length(var.subnets)
toset(["a", "b", "a"])               # ["a", "b"] — deduped
tolist(toset(var.names))
merge(local.common_tags, { Name = "web" })
flatten([["a", "b"], ["c"]])         # ["a", "b", "c"]
keys(var.tag_map)
values(var.tag_map)
lookup(var.amis, var.region, "ami-default")
```

### for expressions
```hcl
[for s in var.names : upper(s)]
{for k, v in var.tags : k => lower(v)}
[for s in var.names : s if length(s) > 3]  # filter
```

## Lifecycle Block

```hcl
lifecycle {
  create_before_destroy = true    # zero-downtime replacement
  prevent_destroy       = true    # block accidental destroy
  ignore_changes        = [tags, desired_count]  # skip diff on these attrs
  replace_triggered_by  = [aws_launch_template.app.latest_version]
}
```

## moved Block (Terraform >= 1.1)

```hcl
moved {
  from = aws_instance.web
  to   = aws_instance.web_server
}

moved {
  from = aws_instance.web
  to   = module.web.aws_instance.this
}
```

## Module Patterns

```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.5.2"

  name = "prod-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true
  single_nat_gateway = false  # true in non-prod to save cost
}

# Reference module output
resource "aws_eks_cluster" "this" {
  vpc_config {
    subnet_ids = module.vpc.private_subnets
  }
}
```

## for_each Patterns

```hcl
# Map: key = resource name, value = config
resource "aws_s3_bucket" "this" {
  for_each = {
    logs    = { region = "us-east-1", versioning = true }
    backups = { region = "eu-west-1", versioning = false }
  }
  bucket = "${var.project}-${each.key}"
}

# Set: only key, no value
resource "aws_iam_user" "devs" {
  for_each = toset(["alice", "bob", "carol"])
  name     = each.key
}

# From variable
resource "aws_subnet" "this" {
  for_each          = { for idx, cidr in var.private_cidrs : "subnet-${idx}" => cidr }
  cidr_block        = each.value
  availability_zone = element(var.azs, index(var.private_cidrs, each.value))
}
```

## CI/CD Pipeline Pattern

```bash
# Plan stage (PR open)
terraform init -backend-config=env/${ENV}.hcl
terraform plan -out=plan.tfplan
# Store plan artifact, post summary to PR comment

# Apply stage (after merge/approval)
terraform apply plan.tfplan
# No re-plan — applies exactly what was reviewed
```

## Key Gotchas

| Gotcha | Detail |
|--------|--------|
| Backend config can't use variables | Must be literals or `-backend-config` flags |
| `count` + list reordering | Causes cascading destroy/recreate — use `for_each` |
| `sensitive` outputs still in state | Encryption at rest is the protection, not `sensitive = true` |
| `depends_on` on modules | Forces sequential plan even for unrelated resources — use sparingly |
| `terraform refresh` deprecated | Use `plan -refresh-only` + `apply -refresh-only` |
| Workspace ≠ environment isolation | Shares backend config and code — use separate state paths for strict isolation |
| Provider aliases needed for multi-region | `provider "aws" { alias = "us_west"; region = "us-west-2" }` |
| `terraform import` doesn't generate config | Only populates state — you must write the config manually (or use `import` block in 1.5+) |

***

## Data Sources

```hcl
# Fetch existing resources (read-only)
data "aws_vpc" "default" {
  default = true
}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]   # Canonical
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# Reference
resource "aws_instance" "web" {
  ami               = data.aws_ami.ubuntu.id
  availability_zone = data.aws_availability_zones.available.names[0]
  # ...
}

output "account_id" {
  value = data.aws_caller_identity.current.account_id
}
```

***

## Check Blocks (Terraform >= 1.5)

```hcl
# Validate post-apply conditions
check "health_check" {
  data "http" "my_service" {
    url = "https://${aws_lb.main.dns_name}/health"
  }
  assert {
    condition     = data.http.my_service.status_code == 200
    error_message = "Service health check failed after deployment"
  }
}
```

***

## Preconditions & Postconditions

```hcl
resource "aws_instance" "web" {
  lifecycle {
    precondition {
      condition     = var.instance_type != "t2.micro"
      error_message = "t2.micro is not allowed in production."
    }

    postcondition {
      condition     = self.public_ip != ""
      error_message = "Instance must have a public IP."
    }
  }
}
```

***

## Terragrunt Quick Reference

```bash
# Common commands (mirrors terraform)
terragrunt init
terragrunt plan
terragrunt apply
terragrunt destroy

# Run across all modules
terragrunt run-all plan
terragrunt run-all apply --terragrunt-include-dir "production/**"
terragrunt run-all output

# Run in specific directory
terragrunt plan --terragrunt-working-dir production/vpc/
```

```hcl
# Root terragrunt.hcl
generate "provider" {
  path      = "provider.tf"
  if_exists = "overwrite"
  contents  = <<EOF
provider "aws" {
  region = "us-east-1"
}
EOF
}

remote_state {
  backend = "s3"
  config = {
    bucket = "my-tf-state-${get_aws_account_id()}"
    key    = "${path_relative_to_include()}/terraform.tfstate"
    region = "us-east-1"
    encrypt = true
    dynamodb_table = "terraform-locks"
  }
  generate = {
    path      = "backend.tf"
    if_exists = "overwrite"
  }
}
```

***

## Linting & Security Scanning

```bash
# tflint — linting and provider-specific rules
tflint --init
tflint                                   # Lint current directory
tflint --recursive                       # Lint all modules

# trivy — IaC security scanning
trivy config ./                          # Scan Terraform configs
trivy config --severity HIGH,CRITICAL ./ # Only critical

# checkov — CIS benchmark + best practices
checkov -d .                             # Scan directory
checkov -d . --framework terraform
checkov -d . --check CKV_AWS_20         # Run specific check
checkov -d . --skip-check CKV_AWS_50    # Skip specific check
checkov -d . -o json > checkov.json      # JSON output

# terrascan
terrascan scan -t aws -i terraform

# infracost — cost estimation
infracost breakdown --path .             # Show cost breakdown
infracost diff --path . --compare-to previous-plan.json  # Cost diff
```

***

## Common Errors & Fixes

| Error | Cause | Fix |
|:---|:---|:---|
| `Error acquiring state lock` | Previous run crashed | `terraform force-unlock <LOCK_ID>` |
| `Backend initialization required` | Backend config changed | `terraform init -reconfigure` |
| `Resource already exists` | Resource not in state | `terraform import resource.name <id>` |
| `Cycle detected` | Circular dependencies | Find and break the dependency cycle |
| `Provider produced invalid plan` | Provider bug | Upgrade provider or use `ignore_changes` |
| `Context deadline exceeded` | Slow provider API | Increase timeout in resource config |
| `No changes but state is not empty` | Drift not refreshed | `terraform plan -refresh-only` |
| `Error: Reference to undeclared input variable` | Missing variable | Add `variable "name" {}` block |
