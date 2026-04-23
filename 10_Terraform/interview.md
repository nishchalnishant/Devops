# Terraform — Interview Questions

All difficulty levels combined.

---

## Easy

**1. What is Terraform and how does it differ from Ansible?**

Terraform is an Infrastructure as Code tool for provisioning and managing the lifecycle of infrastructure resources. Ansible is a configuration management tool for configuring software on that infrastructure. Terraform provisions the house; Ansible furnishes it. Terraform is declarative; Ansible is more procedural.

**2. What is the Terraform state file and why is it important?**

The state file (`terraform.tfstate`) tracks all resources Terraform manages, mapping configuration to real-world resources with their IDs and current attributes. It is essential for planning and applying future changes — without it, Terraform cannot determine what exists and what to create, update, or destroy.

**3. What does `terraform plan` do?**

It creates an execution plan — compares the desired state in your configuration with the current state in the state file and shows exactly what will be created, updated, or destroyed if you run `terraform apply`. No changes are made.

**4. What does `terraform init` do?**

It initializes the working directory: downloads required provider plugins, sets up the backend for state file storage, and installs any required modules. Always run it first in a new Terraform project or after changing the backend or providers.

**5. What is a Terraform provider?**

A provider is a plugin that allows Terraform to interact with a specific API — a cloud platform like AWS or Azure, a SaaS provider like Cloudflare, or on-premises technology like VMware vSphere. Each provider must be declared and configured in the Terraform configuration.

**6. Why is it important to keep the Terraform state file secure?**

The state file can contain sensitive data in plain text — database passwords, private keys, and API credentials. Store it in a secure, encrypted, access-controlled remote backend (S3 bucket with SSE + DynamoDB locking, Azure Blob Storage with encryption).

**7. What is a Terraform module?**

A module is a container for multiple Terraform resources that are used together. Every Terraform configuration is a module. You call child modules to encapsulate and reuse infrastructure patterns — a VPC module, an EKS cluster module — with input variables and output values.

**8. What is the `terraform import` command?**

`terraform import` brings an existing real-world resource under Terraform management without recreating it. It populates state with the resource's current attributes. Used when infrastructure was created manually and needs to be managed as code going forward.

---

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

## Hard

**17. Your Terraform state file is very large and slow to process. How do you refactor it?**

A large state file indicates a monolithic infrastructure definition. Split it:

1. **By environment:** Separate Terraform configurations (and state files) for dev, staging, and production.
2. **By component:** Within an environment, separate states: one for core networking (VPC), one for the Kubernetes cluster, and separate states for application-layer resources.
3. **`terraform_remote_state`:** Allow separate configurations to share outputs. The application config reads the Kubernetes cluster endpoint from its remote state data source.
4. **Terragrunt:** Manages multiple small root modules and their state files with dependency ordering and DRY configuration.

**18. How do you manage a breaking change in a widely used Terraform module?**

1. **Versioning:** The module follows SemVer. The breaking change requires a new `MAJOR` version (`v1.5.0` → `v2.0.0`).
2. **Communication:** Announce the upcoming breaking change to all consuming teams with a clear migration deadline.
3. **Migration guide:** Write a detailed upgrade guide with code examples.
4. **Parallel support:** Continue supporting `v1.x` with bug fixes during the transition. No new features on the old version.
5. **Automated detection:** Add linting checks (Conftest/Sentinel) that detect usage of deprecated module versions and warn during CI runs.

**19. A stale Terraform state lock on DynamoDB is blocking the team. How do you safely remove it?**

1. **Identify the lock:** Navigate to the DynamoDB table and find the lock item.
2. **Inspect the metadata:** The lock item contains who created it, when, and from where. Confirm the process is truly dead.
3. **Force unlock:** Run `terraform force-unlock <lock-id>` — Terraform's official unlock path. If the lock ID is unavailable, manually delete the DynamoDB item.
4. **Caution:** Deleting a lock for a still-running process risks state file corruption. Investigation is the critical step.

**20. How do you manage Terraform at scale across 100+ modules and 50 teams?**

- **Module versioning:** All modules published to a private Terraform Registry or Git-tagged releases. Consumers pin to `~> 2.1`. Breaking changes trigger a MAJOR version bump.
- **Module testing pipeline:** Every module has automated tests using `terraform test` (v1.6+) or Terratest — they provision real infrastructure in a sandbox account, validate outputs, then destroy.
- **Policy as Code:** Sentinel or OPA/Conftest validates all Terraform plans in CI — blocks resources that violate security, tagging, or cost policies before they reach `apply`.
- **Drift detection:** A scheduled pipeline runs `terraform plan` on all workspaces daily. If drift is detected, a Jira ticket is opened automatically.
- **Workspace isolation:** Each team manages their own root modules with separate state files and IAM roles, preventing blast radius from cross-team changes.

**21. What are the risks of using `local-exec` and `remote-exec` provisioners?**

- **Not idempotent:** Re-running `terraform apply` re-runs the script, which may have unintended side effects.
- **Untracked state:** Actions performed by scripts are not tracked in the Terraform state file — Terraform doesn't know about them.
- **Tight coupling:** Pipeline behavior depends on script side effects, not infrastructure declarations.

Alternatives: Packer for golden image baking (pre-install software in the image), Ansible for post-provisioning configuration, Cloud-Init user data for startup scripts. Keep Terraform declarative — provision infrastructure, not configuration.

**22. How do you write and deploy a custom Terraform provider?**

1. **Provider schema:** Define the provider's configuration schema (API endpoint, credentials).
2. **Resource schemas:** For each resource, define its schema — attributes, types, required/optional, computed.
3. **CRUD functions:** Implement Create, Read, Update, Delete functions that call the target API.
4. **Go SDK:** Write the provider in Go using the Terraform Plugin Framework or Plugin SDK.
5. **Testing:** Use `tfproviderdocs` for documentation and `resource.Test` with `providertest` for acceptance tests.
6. **Distribution:** Publish to the Terraform Registry or use a local mirror with `filesystem_mirror` in `.terraformrc`.

**23. How do you handle Terraform provider version conflicts in a large monorepo?**

Each root module manages its own provider version constraints in `required_providers`. Conflicts occur when module A requires `>= 3.0` and module B requires `~> 2.9` for the same provider — they can coexist in separate root modules but not when A is called from B's root. Solutions:
- Use separate Terraform workspaces/root modules per team — they install their own provider versions independently.
- Enforce a minimum provider version via OPA policy in CI and communicate an organization-wide upgrade timeline.
- Use Terragrunt or Terramate to manage per-module initialization in isolation.
