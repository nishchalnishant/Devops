# Terraform — Deep Dive Notes

## State Internals

Terraform state is a JSON document that maps each `resource "type" "name"` block to a real-world object via its provider-assigned ID plus all current attributes.

```json
{
  "version": 4,
  "terraform_version": "1.7.0",
  "resources": [
    {
      "mode": "managed",
      "type": "aws_instance",
      "name": "web",
      "provider": "provider[\"registry.terraform.io/hashicorp/aws\"]",
      "instances": [
        {
          "schema_version": 1,
          "attributes": {
            "id": "i-0abc123def456",
            "instance_type": "t3.medium",
            "tags": {"Name": "web", "Env": "prod"}
          }
        }
      ]
    }
  ]
}
```

Key facts:
- State is the source of truth for what Terraform manages — not the cloud API
- `terraform plan` reads state, calls provider's `Read` RPC to get current attributes, diffs against config
- `sensitive = true` marks a value to be redacted from terminal output — the value is still in state in plaintext
- State version is incremented on every `apply` — S3 versioning enables rollback

## Remote Backend Deep Dive

### S3 + DynamoDB locking mechanism

1. Terraform writes a lock record to DynamoDB (`PutItem` with `ConditionExpression: attribute_not_exists(LockID)`)
2. Downloads the state JSON from S3
3. Computes plan, waits for approval, executes apply
4. Uploads new state JSON to S3 (atomic overwrite)
5. Deletes the DynamoDB lock record

If the process dies between steps 4 and 5, the lock remains. `terraform force-unlock <ID>` deletes the DynamoDB item.

### State file access pattern

```
CI Role  →  s3:GetObject / s3:PutObject on state bucket
         →  dynamodb:GetItem / PutItem / DeleteItem on lock table
```

Minimal IAM policy for a Terraform runner:
```json
{
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject", "s3:ListBucket"],
      "Resource": [
        "arn:aws:s3:::my-tf-state",
        "arn:aws:s3:::my-tf-state/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": ["dynamodb:GetItem", "dynamodb:PutItem", "dynamodb:DeleteItem"],
      "Resource": "arn:aws:dynamodb:us-east-1:123456789:table/terraform-lock"
    }
  ]
}
```

## Provider Internals

Providers are gRPC plugins. Terraform core communicates with them via the `terraform-plugin-framework` or `terraform-plugin-sdk` protocol:
- `PlanResourceChange`: provider computes the expected new state given current state + config
- `ApplyResourceChange`: provider calls the cloud API and returns real state
- `ReadResource`: provider fetches current real state (used during refresh)
- `ImportResourceState`: maps a real-resource ID to state attributes (used by `terraform import`)

Provider version resolution:
1. `required_providers` in `terraform {}` block defines allowed range
2. `.terraform.lock.hcl` records the exact version and SHA256 checksums that were installed
3. `terraform init -upgrade` moves to the newest allowed version and updates the lock file

Always commit `.terraform.lock.hcl` — it guarantees reproducible provider behaviour across machines.

## Module Design Patterns

### Composition over inheritance

Good modules are narrow, single-purpose, and composable. Avoid "mega-modules" that provision 20 resource types — they create tight coupling and impossible-to-predict destroy blast radius.

```
modules/
  vpc/          # subnets, route tables, IGW, NAT GW only
  security-group/
  eks-cluster/  # control plane only
  eks-nodegroup/
  rds/
```

### Module outputs and inter-module wiring

```hcl
# modules/vpc/outputs.tf
output "private_subnet_ids" {
  value = aws_subnet.private[*].id
}

# root/main.tf
module "vpc" { source = "./modules/vpc" }

module "eks" {
  source     = "./modules/eks-cluster"
  subnet_ids = module.vpc.private_subnet_ids  # explicit dependency
}
```

### Versioning strategy

| Constraint | Meaning | Recommendation |
|-----------|---------|----------------|
| `= 1.2.3` | Exact pin | Maximum stability, no auto-updates |
| `~> 1.2` | `>= 1.2, < 2.0` | Allows patches/minors | Use for trusted modules |
| `>= 1.0` | Any version ≥ 1.0 | Dangerous — catches breaking majors |

For internal modules in a Git repo:
```hcl
source = "git::https://github.com/org/tf-modules.git//vpc?ref=v3.2.1"
```

## Dynamic Blocks

Dynamic blocks generate repeated nested blocks from a collection — equivalent to `for_each` but for nested configuration blocks (not top-level resources):

```hcl
variable "ingress_rules" {
  type = list(object({
    port        = number
    protocol    = string
    cidr_blocks = list(string)
  }))
}

resource "aws_security_group" "web" {
  name = "web-sg"

  dynamic "ingress" {
    for_each = var.ingress_rules
    content {
      from_port   = ingress.value.port
      to_port     = ingress.value.port
      protocol    = ingress.value.protocol
      cidr_blocks = ingress.value.cidr_blocks
    }
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

`ingress.key` is the collection index/key; `ingress.value` is the element.

## templatefile() and External Data

```hcl
# Render a shell script with Terraform variables
resource "aws_launch_template" "app" {
  user_data = base64encode(templatefile("${path.module}/user_data.sh.tpl", {
    db_host       = aws_db_instance.main.address
    cluster_name  = var.cluster_name
    region        = var.aws_region
  }))
}
```

`user_data.sh.tpl`:
```bash
#!/bin/bash
echo "DB_HOST=${db_host}" >> /etc/environment
aws eks update-kubeconfig --region ${region} --name ${cluster_name}
```

`path.module` — path of the module directory (use this, not `path.cwd`)
`path.root` — path of the root module
`path.cwd` — current working directory (avoid — it's fragile)

## Import Block (Terraform >= 1.5)

Declarative import: Terraform generates configuration from existing resources.

```hcl
import {
  to = aws_security_group.legacy
  id = "sg-0abc123"
}

import {
  to = aws_s3_bucket.this["logs"]
  id = "my-logs-bucket"
}
```

Then:
```bash
terraform plan -generate-config-out=generated.tf  # generates HCL from imported resource
terraform apply                                     # imports into state
```

Review `generated.tf`, move relevant parts into your module, delete the `import` block after apply.

## Moved Block Patterns

```hcl
# Rename resource
moved {
  from = aws_instance.web
  to   = aws_instance.web_server
}

# Move resource into a module
moved {
  from = aws_instance.app
  to   = module.app.aws_instance.this
}

# Move for_each resource to a new key
moved {
  from = aws_s3_bucket.this["old-key"]
  to   = aws_s3_bucket.this["new-key"]
}
```

`moved` blocks are idempotent and safe to leave in the code (they're no-ops after the state is updated). Remove them when the rename is complete and everyone has applied.

## Provider Aliases (Multi-Region / Multi-Account)

```hcl
provider "aws" {
  region = "us-east-1"
}

provider "aws" {
  alias  = "us_west"
  region = "us-west-2"
}

provider "aws" {
  alias  = "prod_account"
  region = "us-east-1"
  assume_role {
    role_arn = "arn:aws:iam::PROD_ACCOUNT_ID:role/TerraformRole"
  }
}

resource "aws_s3_bucket" "primary" {
  bucket = "my-bucket-east"
  # uses default provider
}

resource "aws_s3_bucket" "replica" {
  provider = aws.us_west
  bucket   = "my-bucket-west"
}

module "prod_vpc" {
  source = "./modules/vpc"
  providers = {
    aws = aws.prod_account
  }
}
```

## Atlantis — GitOps for Terraform

Atlantis is a self-hosted automation tool that runs Terraform in response to pull request comments:

```
Developer opens PR → Atlantis runs terraform plan → posts plan output as PR comment
Reviewer approves → Developer comments "atlantis apply" → Atlantis runs apply and merges
```

`atlantis.yaml` (per-repo):
```yaml
version: 3
projects:
  - name: prod-vpc
    dir: environments/prod/vpc
    workspace: default
    autoplan:
      when_modified: ["*.tf", "../../../modules/vpc/**/*.tf"]
    apply_requirements: [approved, mergeable]
```

Benefits vs direct CI: state locking is centralized, plans are visible in PRs, apply only runs after human approval.

## Terraform Cloud / Enterprise Remote Execution

With the `cloud` backend (or `remote` backend for older versions):

```hcl
terraform {
  cloud {
    organization = "my-org"
    workspaces {
      name = "prod-api"
    }
  }
}
```

- Plan and apply run on TFC agents (remote execution), not the local machine or CI runner
- State is stored and encrypted in TFC
- Policy checks (Sentinel or OPA) run between plan and apply
- Variable sets allow sharing secrets across workspaces without duplication
- Run tasks integrate external tools (Snyk, Infracost, custom HTTP endpoints) into the run pipeline

## Testing Pyramid

```
                    ┌─────────────────┐
                    │  Terratest      │  Integration tests
                    │  (Go, real AWS) │  Slowest, costs money
                    └────────┬────────┘
                    ┌────────┴────────┐
                    │terraform test   │  Unit tests (TF 1.6+)
                    │(.tftest.hcl)    │  Mock providers, fast
                    └────────┬────────┘
              ┌──────────────┴──────────────┐
              │  tflint  checkov  tfsec      │  Static analysis
              │  terraform validate/fmt      │  Seconds, no cloud
              └─────────────────────────────┘
```

### terraform test (.tftest.hcl)
```hcl
# tests/vpc.tftest.hcl
variables {
  cidr_block = "10.0.0.0/16"
  az_count   = 2
}

run "creates_correct_number_of_subnets" {
  command = plan

  assert {
    condition     = length(aws_subnet.private) == 2
    error_message = "Expected 2 private subnets"
  }
}

run "apply_and_verify" {
  command = apply

  assert {
    condition     = aws_vpc.this.enable_dns_support == true
    error_message = "DNS support must be enabled"
  }
}
```

### Terratest (Go)
```go
func TestVpcModule(t *testing.T) {
    t.Parallel()
    opts := &terraform.Options{
        TerraformDir: "../examples/complete",
        Vars: map[string]interface{}{
            "cidr_block": "10.0.0.0/16",
        },
    }
    defer terraform.Destroy(t, opts)
    terraform.InitAndApply(t, opts)

    vpcID := terraform.Output(t, opts, "vpc_id")
    assert.NotEmpty(t, vpcID)
}
```

## Dependency Graph Mechanics

Terraform builds a DAG (Directed Acyclic Graph) where:
- Nodes are resources, data sources, outputs, locals, variables
- Edges represent dependencies (explicit via references, implicit via `depends_on`)
- Independent nodes are walked in parallel (controlled by `-parallelism=N`, default 10)
- Cycles cause `Error: Cycle detected` — fix by introducing an intermediate data source or restructuring

```bash
terraform graph | dot -Tsvg > graph.svg     # requires graphviz
terraform graph -type=plan | dot -Tpng > plan_graph.png
```

Graph node types:
- `provider["..."]` — provider configuration
- `[root] aws_instance.web` — managed resource
- `[root] data.aws_vpc.main` — data source
- `[root] output.vpc_id` — output

## Sentinel Policy as Code

Sentinel evaluates the Terraform plan JSON before apply. Three enforcement levels:

```python
# sentinel/require-tags.sentinel
import "tfplan/v2" as tfplan

required_tags = ["Environment", "Team", "CostCenter"]

# Get all managed resources
resources = filter tfplan.resource_changes as _, rc {
    rc.mode is "managed" and
    rc.change.actions is not ["delete"]
}

# Check each has required tags
violations = filter resources as _, rc {
    any required_tags as tag {
        not (tag in keys(rc.change.after.tags_all))
    }
}

main = rule { length(violations) is 0 }
```

Policy set configuration in TFC:
- `advisory`: always passes, logs violation
- `soft-mandatory`: blocks apply, but a TFC operator can override
- `hard-mandatory`: blocks apply unconditionally

OPA/Conftest equivalent (free, no TFC required):
```bash
terraform show -json plan.tfplan > plan.json
conftest test plan.json --policy policies/
```

## Common Functions Reference

```hcl
# String
format("%-10s %s", "name", var.name)
replace(var.name, "-", "_")
split(",", "a,b,c")        # ["a", "b", "c"]
join(", ", ["a", "b"])     # "a, b"
trimspace("  hello  ")
startswith(var.env, "prod")
endswith(var.name, "-blue")
regexall("[0-9]+", var.version)  # list of all matches

# Numeric
min(3, 1, 4)
max(3, 1, 4)
ceil(1.2)     # 2
floor(1.9)    # 1
abs(-5)       # 5

# Collections
length(var.list)
contains(["a", "b"], "a")   # true
index(["a", "b", "c"], "b") # 1
element(var.list, 2)         # circular index
slice(var.list, 1, 3)        # sublist [1, 3)
compact(["a", "", "b"])      # removes empty strings: ["a", "b"]
distinct(["a", "a", "b"])    # ["a", "b"]
flatten([["a"], ["b", "c"]]) # ["a", "b", "c"]
zipmap(["a", "b"], [1, 2])   # {a=1, b=2}

# Type conversion
tostring(42)
tonumber("3.14")
tobool("true")
toset(["a", "b", "a"])
tolist(toset(var.names))    # converts set to list (arbitrary order)

# Encoding
base64encode("hello")
base64decode("aGVsbG8=")
jsonencode({key = "value"})
jsondecode(data.http.config.body)
yamlencode({key = "value"})
yamldecode(file("config.yaml"))
```

## Advanced Patterns

### Conditional resource creation
```hcl
# count-based toggle
resource "aws_cloudwatch_log_group" "this" {
  count = var.enable_logging ? 1 : 0
  name  = "/aws/lambda/${var.function_name}"
}

# Reference: use one() to safely dereference a count=0..1 resource
locals {
  log_group_arn = one(aws_cloudwatch_log_group.this[*].arn)
}
```

### Cross-module data sharing via remote state
```hcl
# In consuming module
data "terraform_remote_state" "vpc" {
  backend = "s3"
  config = {
    bucket = "my-tf-state"
    key    = "prod/vpc/terraform.tfstate"
    region = "us-east-1"
  }
}

locals {
  vpc_id     = data.terraform_remote_state.vpc.outputs.vpc_id
  subnet_ids = data.terraform_remote_state.vpc.outputs.private_subnet_ids
}
```

Alternative: use SSM Parameter Store as a loose-coupling bus:
```hcl
# VPC module writes
resource "aws_ssm_parameter" "vpc_id" {
  name  = "/infra/prod/vpc/id"
  type  = "String"
  value = aws_vpc.this.id
}

# EKS module reads
data "aws_ssm_parameter" "vpc_id" {
  name = "/infra/prod/vpc/id"
}
```

### Null resource and triggers
```hcl
resource "null_resource" "db_migration" {
  triggers = {
    migration_hash = filemd5("${path.module}/migrations/001.sql")
    db_endpoint    = aws_db_instance.main.address
  }

  provisioner "local-exec" {
    command = "psql ${aws_db_instance.main.address} -f migrations/001.sql"
  }
}
```

The resource re-runs its provisioner when any `triggers` value changes — useful for running one-time scripts tied to Terraform state.
