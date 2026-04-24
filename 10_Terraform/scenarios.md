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
