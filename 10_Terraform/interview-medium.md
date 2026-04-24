## Medium

**9. Why use a remote backend and state locking in Terraform?**

Remote state supports team collaboration, durability, and access control. State locking (via DynamoDB for S3, or native for Azure/GCS) prevents two people or pipelines from running `terraform apply` simultaneously and corrupting the state file.

**10. Why is `for_each` often safer than `count`?**

`for_each` keys resources by stable string names (from a map or set), which prevents accidental churn when list order changes. `count` is index-based — if an element is removed from the middle of a list, all subsequent resources are renamed, causing unexpected destroy-and-recreate operations.

**11. What is the `terraform moved` block?**

The `moved` block (Terraform >= 1.1) allows renaming a resource address in configuration without destroying and recreating the underlying infrastructure:

```hcl
moved {
  from = aws_instance.web
  to   = aws_instance.web_server
}
```

Terraform updates the state to reflect the new address without touching the real resource. Also used when refactoring a standalone resource into a `module` block.

**12. How do you handle secrets in Terraform without storing them in state?**

Use data sources to retrieve secrets at apply time from HashiCorp Vault or a cloud secret manager (`data "vault_generic_secret"`, `data "aws_secretsmanager_secret_version"`). Mark outputs `sensitive = true` to redact them from plan/apply output. Encrypt state at rest. The cleanest pattern: Terraform provisions the secret container; the secret value is stored and rotated externally by Vault or AWS Secrets Manager.

**13. What is the difference between `terraform plan -out=plan.tfplan` and running plan without `-out`?**

Without `-out`, the plan is displayed but not saved — running `terraform apply` will recompute the plan. With `-out=plan.tfplan`, the exact plan is saved to a binary file. `terraform apply plan.tfplan` executes that exact plan with no recomputation. This is the correct CI/CD pattern: plan in one step, apply the saved plan in a subsequent approved step — guaranteeing what was reviewed is what runs.

**14. What is infrastructure drift and how do you detect and correct it?**

Drift occurs when real infrastructure no longer matches the Terraform configuration — typically caused by manual console changes. Detection: `terraform plan` reports unexpected diffs. Correction: import the changed state with `terraform import` then update configuration, or run `terraform apply` to revert the manual change. Prevention: restrict IAM/RBAC so engineers cannot make direct changes outside of Terraform, and run scheduled drift detection pipelines.

**15. What is `prevent_destroy` and when do you use it?**

`prevent_destroy` is a lifecycle meta-argument that causes Terraform to error if a plan would destroy the resource:

```hcl
lifecycle {
  prevent_destroy = true
}
```

Apply to critical, hard-to-recover resources: production databases, foundational networking, stateful storage. It forces a deliberate deletion workflow instead of accidental removal from a misconfigured plan.

**16. What is Terragrunt and what problems does it solve?**

Terragrunt is a thin wrapper around Terraform that adds: DRY configuration (keep backend configuration, provider versions, and common inputs in a root `terragrunt.hcl`), dependency management between Terraform modules, environment-specific configuration inheritance, and parallelized multi-module operations. It solves the boilerplate problem in large Terraform monorepos with many environments and modules.

***


**17. How do you structure a Terraform project for multiple environments (dev/staging/prod)?**

Two common patterns:

**Pattern A — Directory per environment** (simple, explicit):
```
environments/
  dev/
    main.tf       # calls shared modules with dev-specific vars
    terraform.tfvars
  staging/
    main.tf
  prod/
    main.tf
modules/
  vpc/
  eks/
  rds/
```
Each environment directory has its own backend config and state. Apply per-directory: `cd environments/prod && terraform apply`.

**Pattern B — Terragrunt** (DRY, scales to many accounts/regions):
```
live/
  dev/us-east-1/
    vpc/terragrunt.hcl
    eks/terragrunt.hcl
  prod/us-east-1/
    vpc/terragrunt.hcl
terragrunt.hcl   # root: common backend, provider, inputs
```
Terragrunt generates backend config and inherits shared inputs. Run `terragrunt run-all apply` to apply an entire environment in dependency order.

**17. How does Terraform handle resource dependencies?**

Terraform builds a directed acyclic graph (DAG) of resources. Dependencies are inferred automatically when one resource references another's attribute (`resource "aws_subnet" "x" { vpc_id = aws_vpc.main.id }`). Unrelated resources are created in parallel. `depends_on` adds explicit edges when there's no attribute reference. `terraform graph | dot -Tsvg > graph.svg` generates a visual dependency graph.

**18. What is the `lifecycle` block and what are its options?**

```hcl
lifecycle {
  create_before_destroy = true   # create replacement before destroying old (zero-downtime)
  prevent_destroy       = true   # error if plan would destroy this resource
  ignore_changes        = [tags] # don't diff these attributes (useful for auto-managed tags)
  replace_triggered_by  = [aws_launch_template.app.latest_version] # force replace when this changes
}
```

`create_before_destroy` is critical for resources that don't allow in-place updates (SSL certs, Launch Templates) — without it, Terraform destroys first (causing downtime). `ignore_changes` prevents Terraform from reverting auto-scaling-managed `desired_count` or EKS-managed node labels.

**19. Explain Terraform's `for_each` with a map and when you'd use `toset()` with it.**

`for_each` with a map creates one resource per map entry, keyed by the map key:
```hcl
variable "buckets" {
  default = {
    logs    = "us-east-1"
    backups = "eu-west-1"
  }
}

resource "aws_s3_bucket" "this" {
  for_each = var.buckets
  bucket   = each.key
  region   = each.value
}
# Creates: aws_s3_bucket.this["logs"], aws_s3_bucket.this["backups"]
```

`toset()` converts a list to a set (deduped, unordered) for use with `for_each` when you only need the key (no value):
```hcl
resource "aws_iam_user" "devs" {
  for_each = toset(["alice", "bob", "carol"])
  name     = each.key
}
```
Advantage over `count`: removing "bob" from the list only destroys `aws_iam_user.devs["bob"]`, not alice and carol.

**20. What is a Terraform backend and what backends are available?**

The backend determines where state is stored and how operations are executed. Types:
- `local` (default): state in `terraform.tfstate` on disk — only for solo development
- `s3`: AWS S3 bucket with optional DynamoDB locking — most common for AWS
- `azurerm`: Azure Blob Storage with native locking
- `gcs`: Google Cloud Storage
- `http`: generic HTTP endpoint
- `terraform cloud` / `remote`: Terraform Cloud/Enterprise (state + remote execution + policy)

Backend config is in the `terraform` block and cannot use variables (must be literal or passed via `-backend-config`):
```hcl
terraform {
  backend "s3" {
    bucket         = "my-tf-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-lock"
    encrypt        = true
  }
}
```

**21. How do you test Terraform code?**

Testing pyramid for Terraform:

1. **Static analysis** (fast, no cloud): `terraform validate`, `terraform fmt -check`, `tflint` (lint rules), `checkov`/`tfsec` (security misconfig scanning), `terrascan`
2. **Unit tests** (Terraform 1.6+ native): `terraform test` command runs `.tftest.hcl` files that call modules with mock providers — no real cloud resources created
3. **Integration tests** (slow, costs money): Terratest (Go library) — provisions real resources, runs assertions, destroys. Runs against a sandbox account.

CI pipeline: static → unit tests on PR; integration tests nightly or on merge to main.

**22. What is Sentinel policy as code in Terraform Enterprise/Cloud?**

Sentinel is HashiCorp's policy-as-code framework embedded in Terraform Enterprise/Cloud. It evaluates policies against the Terraform plan before apply. Enforcement levels: `advisory` (log only), `soft-mandatory` (override allowed with justification), `hard-mandatory` (cannot be overridden).

Example policy: prevent production resources without cost center tags, require approved AMI IDs, block resources outside approved regions. Sentinel policies run in the plan → policy check → apply pipeline stage and block non-compliant infrastructure before it's ever created.

Open-source alternative: OPA/Conftest evaluates Terraform plan JSON against Rego policies (same concept, no Enterprise license required).
