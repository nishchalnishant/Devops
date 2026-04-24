# Production Scenarios & Troubleshooting Drills (Senior Level)

### Scenario 1: The "Manual Change" Disaster
**Problem:** Someone deleted a resource in the AWS console.
**Fix:** `terraform plan` will detect the drift. `terraform apply` will recreate it.

### Scenario 2: The Stuck State Lock
**Problem:** "Error acquiring the state lock".
**Fix:** Find the Lock ID and run `terraform force-unlock <ID>`.

### Scenario 3: Module Versioning Breakage
**Problem:** A team updated a common module, and now your deployment fails.
**Fix:** Always pin module versions: `source = "git::...//modules/vpc?ref=v1.2.0"`.

### Scenario 4: State Management across Multi-Account AWS
**Problem:** You have 50 AWS accounts and 1 Terraform repo. State is a mess.
**Fix:** Use **Terraform Workspaces** or **Terragrunt**. Map each environment to a separate state path in S3 (e.g., `s3://my-state/prod/terraform.tfstate`).

***

## Scenario 5: State Lock Stuck After Pipeline Crash

**Situation**: A CI pipeline job was killed mid-apply (OOM, timeout, or manual cancellation). Every subsequent `terraform plan` fails with: `Error acquiring the state lock: ConditionalCheckFailedException`.

**Root cause**: The DynamoDB lock record was written when the apply started but never released because the process was killed rather than completing normally.

**Diagnosis**:
```bash
# Find the Lock ID from the error message, or query DynamoDB directly
aws dynamodb get-item \
  --table-name terraform-lock \
  --key '{"LockID": {"S": "my-bucket/prod/terraform.tfstate"}}' \
  --query 'Item'

# Output includes: LockID, Info (who locked it), Created timestamp
```

**Resolution**:
```bash
# Release the lock — only do this if you're certain no apply is actually running
terraform force-unlock <LOCK_ID>

# Verify: re-run plan to confirm lock is cleared
terraform plan
```

**Prevention**:
- Set `timeout-minutes` in CI jobs so the runner cleans up rather than being OOM-killed
- In GitHub Actions, use `cancel-in-progress: true` with concurrency groups and ensure Terraform runs in a `try/finally`-equivalent (not directly possible in shell, but add a `terraform force-unlock` step with `if: always()`)
- For Atlantis: it handles lock release automatically on job completion/cancellation

***

## Scenario 6: Accidental `terraform destroy` in Production

**Situation**: An engineer ran `terraform destroy` in the wrong terminal tab — the one pointed at the prod backend, not the staging backend.

**Immediate response**:
1. If caught before confirmation: `Ctrl+C`
2. If already running: do not stop mid-destroy — a half-destroyed state is worse. Let it complete, then restore from backup.
3. If completed: restore from the last good state backup in S3 versioning, then re-apply

**Prevention**:
```hcl
# On critical resources
lifecycle {
  prevent_destroy = true
}
```

```bash
# S3 versioning on state bucket — enables point-in-time restore
aws s3api put-bucket-versioning \
  --bucket my-tf-state \
  --versioning-configuration Status=Enabled

# Restore previous state version
aws s3 cp s3://my-tf-state/prod/terraform.tfstate \
  s3://my-tf-state/prod/terraform.tfstate \
  --version-id <VERSION_ID>
```

**Structural safeguards**:
- Separate AWS accounts per environment — `prod` credentials never live on dev machines
- Require `-target` flag confirmation for destroys in prod (enforce via Atlantis policy or CI gate)
- OPA/Sentinel policy: block `destroy` in prod workspaces except via approved change window

***

## Scenario 7: Module Update Breaks All Environments

**Situation**: The platform team published `v2.0.0` of the shared VPC module with a breaking interface change (renamed variable `enable_nat` → `enable_nat_gateway`). All teams using `version = "~> 1.0"` were unaffected, but two teams who pinned `version = ">= 1.0"` got auto-upgraded and their pipelines broke.

**Root cause**: Unpinned or too-broad module version constraint (`>= 1.0` matches `2.0.0`).

**Fix for consumers**:
```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 1.5"   # allows 1.5.x, blocks 2.x
  # or exact pin:
  version = "1.5.3"
}
```

**Fix for module publishers**:
- Follow semantic versioning strictly: breaking interface changes MUST be a major version bump
- Maintain a `CHANGELOG.md` with migration guides between major versions
- Test the module against all published major interface versions in CI before releasing

**Migration pattern for callers**:
```hcl
# Before (v1)
module "vpc" {
  enable_nat = true
}

# After (v2)
module "vpc" {
  enable_nat_gateway = true
}
```
Run `terraform plan` after bumping — the rename of a resource vs a variable is surfaced as a diff.

***

## Scenario 8: Multi-Account State Management at Scale

**Situation**: Organisation has 40 AWS accounts (dev/staging/prod × 13 services + shared-services, logging, security). A single flat Terraform repo with workspaces is causing state conflicts, cross-team blast radius, and slow plans (state file > 10 MB).

**Root cause**: Workspaces share a backend config and code path. At scale, a single monolithic state file is a mutex bottleneck and a blast radius problem.

**Resolution — Terragrunt with per-account state isolation**:
```
live/
  _envcommon/
    vpc.hcl          # shared inputs: cidr ranges, az count
    eks.hcl
  dev/
    account.hcl      # dev AWS account ID, region
    us-east-1/
      vpc/
        terragrunt.hcl   # include _envcommon/vpc.hcl + dev overrides
      eks/
        terragrunt.hcl
  prod/
    account.hcl
    us-east-1/
      vpc/
        terragrunt.hcl
```

`terragrunt.hcl` (root):
```hcl
remote_state {
  backend = "s3"
  generate = {
    path      = "backend.tf"
    if_exists = "overwrite_terragrunt"
  }
  config = {
    bucket         = "tf-state-${local.account_id}"
    key            = "${path_relative_to_include()}/terraform.tfstate"
    region         = local.aws_region
    dynamodb_table = "terraform-lock"
    encrypt        = true
  }
}
```

Each module gets its own state file: `prod/us-east-1/eks/terraform.tfstate` in the prod account's S3 bucket. Cross-module references use `dependency` blocks:
```hcl
dependency "vpc" {
  config_path = "../vpc"
}

inputs = {
  vpc_id     = dependency.vpc.outputs.vpc_id
  subnet_ids = dependency.vpc.outputs.private_subnets
}
```

Apply an entire environment in dependency order:
```bash
terragrunt run-all apply --terragrunt-working-dir live/prod/us-east-1
```

***

## Scenario 9: Terraform Plan Shows Unexpected Destroy on every Run

**Situation**: `terraform plan` always shows `~` update or `-/+` destroy-recreate on a resource that hasn't changed in configuration, but the plan output differs from the actual resource state.

**Common causes and fixes**:

**Cause 1 — Auto-managed attribute**: AWS modifies a tag, EKS adds node labels, auto-scaling changes `desired_count`. Terraform sees a drift it wants to revert.
```hcl
lifecycle {
  ignore_changes = [tags["LastModified"], desired_count]
}
```

**Cause 2 — Computed attribute in `for_each` key**: If a `for_each` key depends on a resource attribute not known until apply, Terraform can't build the map until after apply.
```
Error: Invalid for_each argument — The "for_each" value depends on resource attributes
that cannot be determined until apply
```
Fix: use a static map or `locals` with explicit keys, not resource-computed values.

**Cause 3 — Provider version drift**: Provider was upgraded; new provider normalizes an attribute (e.g., strips trailing dot from DNS names). Result: perpetual diff.
Fix: pin provider version in `.terraform.lock.hcl` and `required_providers`.

**Cause 4 — State drift from manual change**: Someone changed the resource in the console.
```bash
terraform plan -refresh-only   # see what changed
terraform apply -refresh-only  # accept the drift into state (without changing infra)
```

***

## Scenario 10: Sensitive Data Exposed in Terraform State

**Situation**: A security audit finds that RDS master passwords, private key PEM data, and API tokens are stored in plain text in the S3 state bucket, visible to anyone with `s3:GetObject` on the bucket.

**Why it happens**: Terraform stores all resource attributes in state, including `sensitive = true` outputs and `secret` provider fields. `sensitive = true` only redacts plan/apply output — it does not remove the value from state.

**Remediation**:
1. **Encrypt state at rest**: S3 SSE with KMS (already in backend config with `encrypt = true` + `kms_key_id`)
2. **Restrict state access**: S3 bucket policy — only CI role and approved IAM roles get `s3:GetObject`; deny all others including account root
3. **Don't store secrets in Terraform at all**:
```hcl
# WRONG: generates password and stores it in state
resource "random_password" "db" { length = 24 }
resource "aws_db_instance" "this" {
  password = random_password.db.result  # in state as plaintext
}

# RIGHT: Terraform creates the secret slot; secret value managed externally
resource "aws_secretsmanager_secret" "db_password" {
  name = "prod/db/master-password"
}
# Secret value rotated by AWS Secrets Manager rotation Lambda
# App retrieves at runtime via SDK — Terraform never touches the value
```
4. **Audit state for secrets**:
```bash
terraform state pull | jq 'recurse | strings | select(length > 20)' | sort -u
```
Look for patterns matching passwords, keys, tokens.


***

## Scenario 1: State Lock Contention
**Symptom:** `terraform plan` fails with `Error: Error acquiring the state lock`.
**Diagnosis:** Another user or CI job is currently running Terraform, or a previous run crashed without releasing the lock (e.g., in DynamoDB).
**Fix:** 
1. Check who holds the lock.
2. If safe, force unlock: `terraform force-unlock <LOCK_ID>`.

## Scenario 2: The "Ghost" Resource (Manual Deletion)
**Symptom:** `terraform apply` fails because a resource it tries to modify doesn't exist in AWS.
**Diagnosis:** Someone deleted the resource manually via the AWS Console. Terraform's state is now out of sync.
**Fix:** Run `terraform refresh` or `terraform plan` to detect the drift. Terraform will propose recreating the resource.

## Scenario 3: Circular Dependency in Modules
**Symptom:** Terraform fails with `Cycle: module.vpc.aws_vpc.main, module.app.aws_instance.web`.
**Diagnosis:** Module A depends on an output from Module B, and Module B depends on an output from Module A.
**Fix:** Break the cycle by moving shared resources (like Security Groups) into a third module or using data sources instead of direct references.


### Scenario 4: Terraform "Provider Drift"
**Symptom:** `terraform plan` shows changes to 100 resources even though you changed nothing.
**Diagnosis:** You updated the Provider version (e.g., `aws` 4.x to 5.x) and the new version changed the default behavior or attribute mapping.
**Fix:** Pin provider versions: `version = "~> 4.0"`. Review the provider migration guide.

### Scenario 5: Large State Performance Bottleneck
**Symptom:** `terraform plan` takes 20 minutes for a single VPC.
**Diagnosis:** The state file is monolithic and contains thousands of resources. Terraform has to refresh every single one.
**Fix:** Split the infrastructure into smaller "State Buckets" using **Terragrunt** or multiple workspaces.

***

## Scenario 6: for_each Resource Destroyed on Map Key Rename
**Symptom:** Renaming a key in a `for_each` map causes Terraform to plan a destroy of the old resource and create of the new one — a full replacement. For an RDS instance, this means data loss.

**Diagnosis:**
```bash
# Run plan and look for destroy+create pairs
terraform plan 2>&1 | grep -A3 "# aws_db_instance\."

# Example output showing the problem:
# - aws_db_instance.this["mysql-primary"]  will be destroyed
# + aws_db_instance.this["rds-primary"]    will be created
```

**Root Causes and Fixes:**

1. **`for_each` keys are the resource address in state** — Renaming a map key changes the resource address. Terraform interprets this as delete-old + create-new, not rename.

2. **Fix: use a `moved` block** — Tell Terraform the resource moved to the new address without touching the real infrastructure.
```hcl
moved {
  from = aws_db_instance.this["mysql-primary"]
  to   = aws_db_instance.this["rds-primary"]
}
```
After `terraform apply` updates the state, remove the `moved` block.

3. **Fix: `terraform state mv` for immediate remediation** — If you can't add a `moved` block (e.g., the rename already happened in a shared module):
```bash
terraform state mv \
  'aws_db_instance.this["mysql-primary"]' \
  'aws_db_instance.this["rds-primary"]'
# Then re-run plan to confirm 0 changes
terraform plan
```

**Prevention:** Treat `for_each` map keys as permanent identifiers — change them only with an accompanying `moved` block. Enforce this in code review: any PR that modifies a `for_each` map key must include a `moved` block or explicit justification for the replacement.

***

## Scenario 7: Terraform Apply Succeeds but Resource Is Non-Functional
**Symptom:** `terraform apply` exits 0 and all resources show as created. But the application can't connect to the RDS instance — the security group rule is missing.

**Diagnosis:**
```bash
# Confirm what Terraform thinks it created
terraform state show aws_security_group_rule.allow_app

# Compare against what actually exists in AWS
aws ec2 describe-security-groups --group-ids sg-abc123 \
  --query 'SecurityGroups[0].IpPermissions'

# Check if there was a race between SG creation and rule attachment
terraform plan -refresh-only   # will show if state diverged from reality
```

**Root Causes and Fixes:**

1. **Resource created but association silently failed** — Some AWS resources return success on the create API call before the association is fully propagated. The Terraform provider may not detect this.

2. **Dependency not captured — resource created in wrong order** — If `aws_security_group_rule` doesn't explicitly reference the SG resource, it may apply before the SG exists.
```hcl
resource "aws_security_group_rule" "allow_app" {
  type              = "ingress"
  from_port         = 5432
  to_port           = 5432
  protocol          = "tcp"
  security_group_id = aws_security_group.rds.id   # explicit reference = dependency edge
  cidr_blocks       = [aws_vpc.main.cidr_block]
}
```

3. **`ignore_changes` hiding a permanent drift** — A previous engineer added `ignore_changes = [ingress]` to the security group to prevent Ansible from being reverted. This silently ignores all SG rule changes made via Terraform too.
```hcl
lifecycle {
  ignore_changes = [ingress]  # DANGEROUS — Terraform won't notice missing rules
}
```
Remove `ignore_changes` and manage all rules via `aws_security_group_rule` resources instead.

4. **Run `-refresh-only` as a post-apply verification step in CI:**
```bash
terraform apply plan.tfplan
terraform plan -refresh-only   # should show: No changes. Your infrastructure matches the configuration.
```

**Prevention:** Add a smoke test after `terraform apply` that validates functional connectivity (e.g., `nc -zv rds-endpoint 5432`), not just that the Terraform exit code was 0.

***

## Scenario 8: Workspace Variable Leakage Between Environments
**Symptom:** A `terraform apply` in the `staging` workspace accidentally uses production database credentials. The `TF_VAR_db_password` environment variable was set from a previous terminal session targeting prod.

**Diagnosis:**
```bash
# Check current workspace
terraform workspace show

# Check which env vars are set
env | grep TF_VAR

# Check variable precedence in the plan output
terraform plan -var="db_password=REDACTED" 2>&1 | grep db_password
```

**Root Causes and Fixes:**

1. **`TF_VAR_*` env vars persist in shell sessions** — If an engineer runs a prod deployment and then switches to a staging directory without clearing vars, prod secrets bleed into the staging apply.

2. **Use separate shell sessions or `direnv` per environment:**
```bash
# .envrc (direnv) — auto-loads/unloads when entering the directory
export TF_VAR_db_password="$(aws secretsmanager get-secret-value \
  --secret-id staging/db_password --query SecretString -o text)"
export AWS_PROFILE=staging
```
`direnv allow` activates this automatically when `cd`-ing into the directory and unsets it on `cd` out.

3. **Use `-var-file` instead of environment variables for secrets:**
```bash
terraform apply \
  -var-file="environments/staging/secrets.tfvars"  # pulled from vault at CI time, not env vars
```

4. **CI: source credentials fresh per run:**
```bash
# GitHub Actions — separate jobs for staging and prod
jobs:
  deploy-staging:
    environment: staging    # separate GitHub environment with its own secrets
    steps:
      - run: terraform apply
        env:
          TF_VAR_db_password: ${{ secrets.STAGING_DB_PASSWORD }}
```

**Prevention:** Never set `TF_VAR_*` in global shell profiles (`.bashrc`, `.zshrc`). Treat them like loaded weapons — set them per-command or per-session with `direnv`.

***

## Scenario 9: terraform init Fails After Module Source Change
**Symptom:** After updating a module `source` from a public registry to a private Git URL, `terraform init` fails with `Failed to install module; could not download module from source`.

**Diagnosis:**
```bash
# Run init with verbose output
TF_LOG=DEBUG terraform init 2>&1 | grep -i "module\|error\|git"

# Test git connectivity directly
git ls-remote https://github.com/myorg/tf-modules.git

# Check if SSH vs HTTPS is the issue
git ls-remote git@github.com:myorg/tf-modules.git

# Check if the ref exists
git ls-remote https://github.com/myorg/tf-modules.git refs/tags/v3.2.1
```

**Root Causes and Fixes:**

1. **Authentication not configured for private repo** — Terraform uses system Git for module downloads. The CI runner has no credential configured for the private registry.
```bash
# Configure Git credential helper for CI
git config --global url."https://oauth2:$GITHUB_TOKEN@github.com".insteadOf "https://github.com"

# Or use SSH with a deploy key
git config --global url."git@github.com:".insteadOf "https://github.com/"
```

2. **Ref doesn't exist (tag not pushed)** — The source points to `?ref=v3.2.1` but that tag was never pushed to the remote.
```bash
# In the module repo
git tag v3.2.1
git push origin v3.2.1
```

3. **`.terraform.lock.hcl` contains cached hash for old module source** — After changing the source URL, the lock file's module hash is invalid. Delete the module cache and reinitialize.
```bash
rm -rf .terraform/modules/
terraform init
```

4. **Relative path source used outside module directory** — `source = "../../modules/vpc"` only works when the consuming code is in the expected relative position. Use absolute Git URLs for shared modules.

**Prevention:** Test `terraform init` in CI on every PR that changes `source` or `version` in any module block. Cache `.terraform/` between runs using a cache key based on the hash of all `.tf` files.

***

## Scenario 10: Partial Apply Leaves Infrastructure in Inconsistent State
**Symptom:** A `terraform apply` was interrupted mid-run (CI timeout, network drop). Some resources were created, others weren't. The next `terraform plan` shows unexpected changes and some resources have dependency errors.

**Diagnosis:**
```bash
# Check what's currently in state vs what was planned
terraform state list

# Look for resources that are in state but may be partially configured
terraform state show aws_eks_cluster.main

# Check if the state file itself is corrupted
terraform state pull | jq . > /dev/null && echo "State JSON is valid"

# Run a refresh-only plan to see real vs state
terraform plan -refresh-only
```

**Root Causes and Fixes:**

1. **Terraform state is transactional per resource, not per apply** — If an apply creates 10 resources and is killed after 6, the state contains the 6 completed resources. The remaining 4 must be re-applied.

2. **Simply re-run `terraform apply`** — Terraform is designed for this. Resources already in state are compared against config; only missing/drifted ones are re-created.
```bash
terraform apply plan.tfplan   # re-apply the saved plan — only creates what's missing
```
If no saved plan: `terraform apply` re-plans and applies only the diff.

3. **Resources created but not registered in state (rare)** — If the Terraform process is killed between the API call and the state write, a resource exists in AWS but not in state. Detect with:
```bash
terraform plan   # shows resource as "to create" even though it exists
# Fix: import the existing resource
terraform import aws_subnet.private_a subnet-abc123
```

4. **Increase CI timeout and use `-parallelism`** to control the blast radius of a partial apply:
```bash
terraform apply -parallelism=5   # default is 10; lower = slower but fewer orphans on timeout
```

**Prevention:** Always save plans with `-out=plan.tfplan` in CI. Store the plan artifact. If the apply job is re-triggered, apply the same saved plan — this is idempotent and picks up where it left off.
