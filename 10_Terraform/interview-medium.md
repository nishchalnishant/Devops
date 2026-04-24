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

---

