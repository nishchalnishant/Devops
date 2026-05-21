# Terraform Tips & Tricks

```
Terraform Production Tips & Gotchas
├── State Management
│   ├── Always plan -out then apply saved plan (no re-plan in CI)
│   ├── terraform refresh deprecated → use plan -refresh-only
│   ├── -target is a smell → breaks dependent resources, use sparingly
│   └── moved {} block → rename without destroy (tracked in code)
├── Performance & Scale
│   ├── -parallelism=20 → increase concurrent operations (watch rate limits)
│   ├── Partial backend config → -backend-config flags, not hardcoded values
│   └── TF_LOG=DEBUG + TF_LOG_PATH → diagnose provider issues
├── for_each vs count
│   ├── count with list → index-based, reordering causes cascading destroy
│   ├── for_each with toset() → key-based, safe deletion of any element
│   └── Rule: always for_each for collections of real resources
├── Security
│   ├── sensitive = true → hides from CLI, NOT from state file
│   ├── State encryption → S3 + KMS, restrict s3:GetObject
│   ├── prevent_destroy → lifecycle guard on production resources
│   └── Secrets → fetch from SSM/Vault at runtime, never in tfvars
├── Module Design
│   ├── Version-pin sources → exact version in production (not ~> 5.0)
│   ├── Expose all outputs → IDs, ARNs, endpoints, SG IDs
│   └── locals for expressions, variables for inputs (clear separation)
├── CI/CD Best Practices
│   ├── Commit .terraform.lock.hcl → reproducible provider versions
│   ├── Plan on PR, apply on merge (never both in one step)
│   └── Scheduled drift detection → daily plan -refresh-only
└── Debugging
    ├── terraform state list | grep → find resource addresses
    ├── terraform plan 2>&1 | grep "must be replaced" → find replacement cause
    ├── -detailed-exitcode → exit 2 = changes, 0 = no changes (CI scripting)
    ├── force-unlock <LOCK_ID> → release stuck DynamoDB lock
    └── terraform console -var-file= → test expressions interactively
```

## First Principles

- The plan/apply split only works as a safety gate if the plan is deterministic. Running `apply` without a saved plan file means a second plan executes at apply time — the reviewed diff may not match what runs. Save plans with `-out`, store the artifact, apply the artifact.
- `sensitive = true` is UX polish, not security. Anyone with read access to the state file (S3 object, TF Cloud API) can read the value. Security lives in IAM, KMS, and access controls on the state backend.
- `for_each` with a map/set creates a stable addressing scheme. `count` creates positional addressing. In infrastructure, stability of identity is critical — you don't want a list reordering to cascade into destroying 10 load balancer target group attachments.
- Committing `.terraform.lock.hcl` is the equivalent of committing `package-lock.json`. Without it, `init` may resolve `~> 5.0` to `5.0.1` today and `5.3.2` tomorrow — same constraint, different behavior.

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

***

## System Design Perspective

**The plan artifact as a compliance artifact:** In SOC 2 or ISO 27001 audits, you need evidence that changes were reviewed before execution. A saved `plan.tfplan` artifact stored in S3 (with the PR link and approver) is that evidence. Every apply is traceable to a reviewed, approved plan.

**Lock file as reproducibility guarantee:** `.terraform.lock.hcl` stores provider checksums. If a provider binary's hash doesn't match the lock file, `init` fails. This prevents supply-chain attacks where a compromised provider version is silently pulled in. Always commit this file.

**Module version pinning prevents surprise upgrades:** Using `~> 5.0` in production means a provider minor release can change behavior. An exact pin (`5.5.2`) means you consciously chose to upgrade. For a team applying to production multiple times a day, silent provider upgrades are a major risk.

**Scheduled drift detection as operational hygiene:**
- Run `terraform plan -refresh-only` nightly across all environments. Parse the exit code: 0 = no drift, 2 = drift detected.
- Alert on drift rather than auto-applying. Drift may indicate a security incident (someone created an IAM role manually) or an operational shortcut that should be formalized in Terraform.
- After investigating and understanding the drift, `apply -refresh-only` to sync state, then add the resource to Terraform code to prevent future drift.
