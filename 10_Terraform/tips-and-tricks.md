# Terraform Tips & Tricks

Production-tested patterns, anti-patterns, and gotchas for senior engineers.

***

## State Management Gotchas

### Never use `terraform apply` without reviewing `plan` first
```bash
# WRONG in CI — re-plans and may differ from what was reviewed
terraform apply -auto-approve

# CORRECT — apply exactly what was reviewed
terraform plan -out=plan.tfplan    # Save deterministic plan
terraform apply plan.tfplan        # Apply that exact plan (no re-plan)
```

### The `-target` flag is a smell
`terraform apply -target=aws_instance.web` skips updating dependent resources. It's useful for emergencies but leaves state inconsistent. The real fix is to break the module into smaller independently-applicable pieces.

### `terraform refresh` is deprecated — use this instead
```bash
# Old (deprecated in 1.x)
terraform refresh

# Modern — refresh-only plan shows drift without proposing changes
terraform plan -refresh-only

# Apply only the refresh (update state to match reality without any resource changes)
terraform apply -refresh-only
```

### How to safely rename a resource without destroying it
```hcl
# Terraform >= 1.1: use moved block (no destroy/recreate)
moved {
  from = aws_security_group.old_name
  to   = aws_security_group.new_name
}
```
Before `moved` existed, the only option was `terraform state mv` — which requires manual coordination and doesn't track the rename in code.

***

## Performance & Scale

### Speed up large plans with parallelism
```bash
# Default parallelism is 10. Increase for large plans (watch for API rate limits)
terraform apply -parallelism=20

# For AWS: IAM rate limits hit first. Stay below 30.
```

### Partial configuration to avoid credentials in code
```bash
# Never hardcode sensitive backend config in .tf files
# Use -backend-config flags or a backend.hcl file
terraform init \
  -backend-config="bucket=my-state-bucket" \
  -backend-config="key=prod/terraform.tfstate" \
  -backend-config="region=us-east-1"
```

### `TF_LOG` for debugging provider issues
```bash
TF_LOG=DEBUG terraform plan 2>&1 | grep "aws_"   # Filter AWS API calls
TF_LOG_PATH=./debug.log terraform apply           # Write to file (prevents terminal flood)
```

***

## `for_each` vs `count` — Always Prefer `for_each`

```hcl
# WRONG — count with list: reordering the list destroys and recreates resources
resource "aws_iam_user" "devs" {
  count = length(var.users)         # ["alice", "bob", "carol"]
  name  = var.users[count.index]   # Removing "alice" shifts indices → bob becomes alice
}

# CORRECT — for_each with set: identity is the key, not position
resource "aws_iam_user" "devs" {
  for_each = toset(var.users)      # Removing "alice" only affects alice's resource
  name     = each.key
}
```

This is one of the most common production mistakes — it causes cascading resource deletions on a seemingly innocent variable reorder.

***

## Security Patterns

### Sensitive outputs are still in state
```hcl
output "db_password" {
  value     = random_password.main.result
  sensitive = true    # Hides from CLI output — but STILL stored in plaintext in state!
}
```
**Mitigation:** Encrypt state at rest (S3 + KMS) and control who has `s3:GetObject` on the state bucket. State access = secret access.

### Use `prevent_destroy` for production resources
```hcl
resource "aws_rds_cluster" "production" {
  lifecycle {
    prevent_destroy = true   # Terraform errors if plan includes destroying this resource
  }
}
```

### Never store secrets as Terraform variables
```bash
# BAD: secrets in tfvars (committed or passed as flags)
terraform apply -var="db_password=supersecret"

# GOOD: fetch secrets from Vault/SSM at runtime
data "aws_ssm_parameter" "db_password" {
  name            = "/prod/database/password"
  with_decryption = true
}
```

***

## Module Design Principles

### Version-pin module sources
```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.5.2"   # Exact version — not "~> 5.0" in production
}
```

### Expose outputs from every module
Even if the root module doesn't use them today, child module outputs are essential for debugging and for other modules to consume. Always output: IDs, ARNs, endpoint URLs, security group IDs.

### Use `locals` for expressions, `variables` for inputs
```hcl
# BAD: complex expression in a resource
resource "aws_s3_bucket" "this" {
  bucket = "${var.project}-${terraform.workspace}-${var.region}"
}

# GOOD: computed values in locals, easy to read and test
locals {
  bucket_name = "${var.project}-${terraform.workspace}-${var.region}"
}
resource "aws_s3_bucket" "this" {
  bucket = local.bucket_name
}
```

***

## CI/CD Best Practices

### Lock file must be committed
`.terraform.lock.hcl` records the exact provider versions and checksums. Committing it ensures every CI run uses exactly the same provider binary — without it, `~> 5.0` could resolve to a different patch version on different machines.

### Plan on PR, Apply on Merge (never both in one step)
```yaml
# PR stage — show what will change
- terraform plan -out=plan.tfplan
# Post PR comment with plan summary

# Merge stage — apply exactly what was reviewed
- terraform apply plan.tfplan   # Not "terraform apply" (would re-plan!)
```

### Drift detection with scheduled plans
```yaml
# Run daily even with no code changes to detect configuration drift
schedule:
  - cron: '0 9 * * 1-5'  # Weekdays at 9am
```

***

## Common Mistakes & Fixes

| Mistake | Symptom | Fix |
|:---|:---|:---|
| `depends_on` on module | Entire module waits for the dependency even for unrelated resources | Use `depends_on` on specific resources within the module, not the module block |
| Provider without alias in multi-region | `Error: No configuration for provider` | `provider "aws" { alias = "west"; region = "us-west-2" }` + `provider = aws.west` |
| `ignore_changes = [all]` | Terraform never updates the resource | Use specific attribute list: `ignore_changes = [tags, desired_count]` |
| `count = 0` to disable a resource | Creates confusing `resource[0]` references everywhere | Use `for_each = var.enabled ? toset(["this"]) : toset([])` |
| Forgetting `required_version` | Plan works locally but fails on older CI Terraform version | Always declare: `required_version = ">= 1.5, < 2.0"` |

***

## Debugging Tips

```bash
# Show all resource addresses in state
terraform state list | grep module.vpc

# Why is this resource being replaced?
terraform plan 2>&1 | grep -A5 "# aws_instance.web must be replaced"

# What attributes caused the diff?
terraform plan -detailed-exitcode   # Exit 2 = changes present, 0 = no changes

# Unlock a stuck DynamoDB lock
terraform force-unlock <LOCK_ID>    # Get lock ID from the error message

# Test a single expression in a configuration
echo 'output "test" { value = formatlist("subnet-%s", var.azs) }' \
  | terraform console -var-file=prod.tfvars
```
