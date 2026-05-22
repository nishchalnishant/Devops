# Terraform — Interview Prep

```
Terraform Fundamentals (Interview: Easy)
├── What & Why
│   ├── IaC tool: declare infra in HCL, Terraform makes it real
│   ├── Declarative: describe end state, not steps
│   └── Terraform vs Ansible: TF provisions infra; Ansible configures it
├── Core Commands
│   ├── init    → download providers + set up backend
│   ├── plan    → show what would change (no mutation)
│   ├── apply   → make changes (re-plans unless given saved plan)
│   ├── destroy → remove all managed resources
│   └── fmt / validate → format and syntax-check .tf files
├── State
│   ├── JSON file mapping resource → real-world object
│   ├── Local state (default) → single-user only
│   └── Remote state → team-safe (S3, Azure Blob, TF Cloud)
├── Providers & Resources
│   ├── Provider → plugin that calls cloud API (aws, azurerm, google)
│   ├── Resource → infrastructure object (aws_instance, aws_s3_bucket)
│   └── Data source → read-only reference to existing resource
├── Modules
│   ├── Any directory with .tf files is a module
│   ├── Root module → your main config
│   └── Child module → reusable component called with module {}
├── Variables & Outputs
│   ├── variable {}  → input to module/config
│   ├── output {}    → value exported from module
│   └── terraform.tfvars → default values file
├── Workspaces
│   ├── Isolated state within same backend + code
│   └── Not a substitute for per-environment directory isolation
├── import
│   ├── terraform import → bring existing resource under TF control
│   └── Populates state only; does not write .tf config
└── depends_on
    ├── Explicit dependency when implicit reference doesn't exist
    └── Avoid on modules (forces full sequential plan)
```

### First Principles

- Terraform reads `.tf` files, builds a dependency graph, computes the diff against state, and produces a plan. The plan is a list of CRUD operations on cloud resources.
- State is Terraform's memory. Without it, every `plan` would look like "create everything." State must be accurate — drift between state and reality causes incorrect plans.
- Providers are just gRPC plugins. Any cloud API can have a provider. `terraform init` downloads the provider binary specified in `required_providers`.
- `plan` never writes to the cloud. `apply` does. This separation allows human review of infra changes the same way code review gates code changes.
- Modules are functions: they take input variables and produce output values. They encapsulate a group of resources behind a stable interface.

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

***


**9. What is HCL and what are the basic building blocks of a Terraform configuration?**

HCL (HashiCorp Configuration Language) is the declarative language Terraform uses. Core building blocks:
- `resource`: declares a managed infrastructure object (`resource "aws_instance" "web" { ... }`)
- `variable`: declares an input parameter with optional type, default, and validation
- `output`: exposes a value after apply (consumed by other modules or users)
- `data`: reads existing infrastructure not managed by this configuration
- `locals`: defines computed values reused within a module
- `module`: calls a child module with inputs
- `provider`: configures a cloud/API plugin

**10. What is the difference between `terraform.tfvars` and a variable definition?**

A variable is declared in `.tf` files with `variable "name" {}` — it defines the input but gives it no value. `terraform.tfvars` (or `*.auto.tfvars`) provides the actual values for those variables. You can have multiple `.tfvars` files for different environments (dev.tfvars, prod.tfvars) and pass them with `-var-file=prod.tfvars`. Environment variables `TF_VAR_<name>` also set variable values.

**11. What is `terraform destroy` and when would you use it?**

`terraform destroy` creates a plan to delete all resources managed by the current state and prompts for confirmation. Used for: tearing down ephemeral environments (feature branch environments, CI test stacks), decommissioning old infrastructure. For selective deletion, use `terraform destroy -target=resource_type.resource_name`. Always run `plan` first to review what will be deleted.

**12. What are Terraform workspaces?**

Workspaces allow a single Terraform configuration to manage multiple, separate state files. `terraform workspace new staging` creates a new workspace; `terraform workspace select prod` switches to it. Each workspace gets its own `terraform.tfstate`. Useful for lightweight environment separation. Limitation: all workspaces share the same backend configuration and code — for strict environment isolation, separate state paths (via Terragrunt or different backend configs) are more common in production.

**13. What does `terraform fmt` do and why should it be enforced in CI?**

`terraform fmt` rewrites `.tf` files to the canonical HCL formatting style (indentation, alignment, spacing). `terraform fmt -check` exits non-zero if any file would be changed — useful as a CI gate to enforce consistent formatting across the team. Prevents style-related diff noise in code reviews.

**14. What is the `depends_on` meta-argument?**

`depends_on` explicitly declares a dependency between resources when Terraform cannot infer it automatically from reference expressions. Used when one resource depends on the side effects of another (e.g., an IAM policy attachment must complete before an ECS task can start, but there's no direct reference between them). Overuse is a code smell — if you find yourself using it often, reconsider your module structure.

**15. What is a `data` source in Terraform?**

A data source reads existing infrastructure that Terraform doesn't manage and makes its attributes available in configuration:
```hcl
data "aws_vpc" "main" {
  tags = { Name = "main-vpc" }
}

resource "aws_subnet" "app" {
  vpc_id = data.aws_vpc.main.id
}
```
Common uses: look up an AMI ID, fetch a secret from Secrets Manager, reference a VPC or DNS zone created by another Terraform config.

***

### System Design Perspective

**Why remote state matters for teams:** With local state, two engineers running `apply` simultaneously can each read the same state, compute a plan, and then both write back — the second write clobbers the first. Remote state with locking (DynamoDB) makes the second `apply` wait or fail until the first completes.

**Workspaces have limits:** Terraform workspaces share provider config and HCL code. If production needs a different VPC CIDR or instance type than staging, workspace-based logic (`terraform.workspace == "prod" ? ... : ...`) clutters HCL. At that point, separate state-path directories with Terragrunt are cleaner.

**Data sources as cross-team handshakes:** A data source is a read-only query. Team A creates a VPC with Terraform and exports it. Team B's config references the VPC by tag or name via a data source — no copy-pasting IDs, no tight coupling of state files.

```
Terraform Intermediate Concepts (Interview: Medium)
├── Remote Backend & State Locking
│   ├── S3 backend → durable, versioned, encrypted state storage
│   ├── DynamoDB lock → prevents concurrent apply corruption
│   ├── State = source of truth for resource ownership
│   └── plan -refresh-only → detect drift without proposing changes
├── for_each vs count
│   ├── count: index-based → reordering list causes destroy/recreate
│   ├── for_each: key-based → deletion only affects that key
│   └── Rule: always for_each for collections; count only for on/off
├── moved Block (TF ≥ 1.1)
│   ├── Rename resource without destroy/recreate
│   ├── Move resource into/out of module
│   └── Tracked in code → safe refactoring with reviewable PR
├── Secrets & State
│   ├── sensitive = true → hides from CLI output only
│   ├── State still stores value in plaintext JSON
│   └── Mitigation: S3+KMS encryption, restrict s3:GetObject on state
├── Deterministic Apply
│   ├── plan -out=plan.tfplan → saves cryptographically-bound plan
│   └── apply plan.tfplan → no re-plan; executes exactly what was reviewed
├── Drift Detection
│   ├── plan -refresh-only → show divergence from state
│   └── apply -refresh-only → sync state without resource changes
├── prevent_destroy
│   ├── lifecycle block attribute
│   └── Terraform errors rather than destroying the resource
├── Terragrunt
│   ├── DRY wrapper: shared provider + backend config in root HCL
│   ├── run-all plan/apply across module hierarchy
│   └── generate {} blocks inject provider.tf and backend.tf per module
├── Multi-Environment Structure
│   ├── env/ directories with own terragrunt.hcl → strong isolation
│   └── Workspace approach → weak isolation, shared code
├── Dependency Graph
│   ├── Implicit: resource A references resource B's attribute
│   ├── Explicit: depends_on (use sparingly)
│   └── terraform graph | dot -Tsvg → visualize
├── Lifecycle Block
│   ├── create_before_destroy → replacement without downtime
│   ├── ignore_changes        → skip diff on volatile attributes (tags)
│   └── replace_triggered_by  → force replace on external change
├── Testing
│   ├── terraform validate   → syntax only
│   ├── terraform test       → .tftest.hcl files (TF ≥ 1.6)
│   ├── Terratest            → Go integration tests against real infra
│   └── checkov / trivy      → static security scanning
└── Sentinel (TF Enterprise)
    ├── Policy as code: enforce rules on every plan
    ├── soft-mandatory / hard-mandatory / advisory
    └── Example: deny instance types not in approved list
```

### First Principles

- Remote state is a shared database. Locking prevents write conflicts just as a mutex protects a shared memory location in concurrent programming.
- `for_each` assigns a stable identity (the key) to each resource. `count` assigns a position. Positions shift when the collection changes — stable keys don't. Always design for stable identities.
- `sensitive = true` is a display filter, not encryption. The state file is JSON and is readable by anyone with `s3:GetObject` on the bucket. State security = IAM + KMS, not the `sensitive` flag.
- The `moved` block is a rename tracked in version control. It lets you refactor resource addresses without destroying real infrastructure — the diff shows intent clearly in a PR review.
- Drift is inevitable. Humans click in consoles. Auto-scaling events change tags. Scheduled `plan -refresh-only` catches drift before it causes a surprising `plan` output during the next deployment.

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

***

### System Design Perspective

**Locking under the hood:** DynamoDB locking uses a conditional `PutItem`. The lock record stores: lock ID, who holds it, when it was acquired. If the item already exists, the write fails — Terraform reports a lock error. `force-unlock` deletes the record. Safe only when you are certain the previous run is dead (crashed CI job, not a slow provider call).

**State as a team coordination mechanism:** `data "terraform_remote_state"` lets teams consume each other's outputs without sharing code. The VPC team exports `vpc_id` and `subnet_ids`; the EKS team reads them. Each team deploys independently — the only contract is the output names.

**Terragrunt at scale:** With 10 environments and 20 modules, Terragrunt's `run-all apply` applies modules in dependency order. Each module gets its own state file. Destroying a module's state does not affect sibling modules. This is the practical alternative to one giant state file.

**Sentinel as a compliance gate:** In regulated industries, Sentinel policies enforce rules like "no S3 bucket without server-side encryption" or "all RDS instances must have `deletion_protection = true`." These policies run after `plan` but before `apply` — they block non-compliant plans in the pipeline, not after the fact.

```
Terraform Advanced Patterns (Interview: Hard)
├── State Refactoring at Scale
│   ├── Symptoms: plan takes 10+ min, single state file = single blast radius
│   ├── Strategy: split by service boundary (VPC, EKS, RDS separate states)
│   ├── Tool: terraform state mv → move resources between state files
│   ├── Better: moved {} block tracks rename in code + PR review
│   └── Remote state data source → cross-state output consumption
├── Module Versioning & Breaking Changes
│   ├── Semantic versioning for module releases (Git tags)
│   ├── Breaking change = major version bump
│   ├── Consumers pin exact version: version = "2.1.0"
│   └── Changelog + migration guide for major versions
├── State Lock Removal
│   ├── terraform force-unlock <LOCK_ID>
│   ├── Safe only when confirmed no other process is running
│   └── Get LOCK_ID from the error message (not guessable)
├── Terraform at Scale (100+ modules, 50+ teams)
│   ├── Atlantis: PR-triggered plan, merge-triggered apply (GitOps)
│   ├── Terraform Cloud/Enterprise: remote execution, RBAC, Sentinel
│   ├── Terragrunt: DRY config, dependency graph, run-all
│   ├── Module registry: private registry (TF Cloud or Artifactory)
│   └── OIDC: CI assumes AWS role, no long-lived access keys
├── local-exec / remote-exec Risks
│   ├── Breaks idempotency (shell scripts don't have changed_when)
│   ├── Creates dependency on control node environment
│   ├── Prefer: cloud-init, SSM Run Command, or Ansible post-provisioning
│   └── If unavoidable: use triggers={} to control re-execution
├── Custom Provider Development
│   ├── Go SDK: terraform-plugin-sdk or terraform-plugin-framework
│   ├── Implement: CRUD + Read for each resource
│   ├── Schema: defines attributes, types, computed vs required
│   └── Publish: Terraform Registry or private registry
└── Provider Version Conflicts in Monorepo
    ├── Each module can declare its own required_providers version constraint
    ├── Root module aggregates: constraints must be satisfiable intersection
    └── Solution: loosen child module constraints; pin in root module
```

### First Principles

- A monolithic state file is a single point of failure and a serial bottleneck. Splitting by service boundary is like microservices for IaC — each team owns their state, their plan times shrink, and a corrupt state affects only one service.
- Atlantis turns `terraform apply` into a GitOps workflow. The plan output is the PR comment. The merge is the approval. No human needs to run CLI commands from their laptop — the entire workflow is auditable in GitHub/GitLab history.
- `local-exec` is the escape hatch that breaks Terraform's declarative model. It runs a shell command with no idempotency guarantee. Use it as a last resort, and pair it with explicit `triggers` so it doesn't re-run on every apply.
- Custom providers are just gRPC servers implementing the provider protocol. Terraform Core doesn't care what the provider does — it calls `PlanResourceChange`, `ApplyResourceChange`, `ReadResource`. Any system with a CRUD API can be a Terraform provider.
- At 50+ teams, access control becomes the primary concern. Terraform Cloud workspaces + team-level RBAC ensures that the payments team cannot accidentally run `apply` against the identity team's infrastructure.

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
provider "aws" { 
region = "us-west-2" 
} 
 
resource "aws_instance" "example" { 
ami 
= "ami-0c55b159cbfafe1f0" 
instance_type = "t2.micro" 
} 
 
2. What are the main features of Terraform? 
Terraform's main features include Infrastructure as Code (IaC), execution plans, resource graphs, 
change automation, and state management. 
 
Example: 
 
terraform { 
backend "s3" { 
bucket = "my-terraform-state" 
key 
= "global/s3/terraform.tfstate" 
region = "us-west-2" 
} 
} 
 
3. What is the difference between Terraform and other IaC tools like 
Ansible, Puppet, and Chef? 


***

### Page 2

Terraform focuses on infrastructure provisioning, is declarative, and uses HCL. Tools like Ansible, 
Puppet, and Chef focus on configuration management and are procedural. 
 
Example: 
 
resource "aws_instance" "example" { 
ami 
= "ami-0c55b159cbfafe1f0" 
instance_type = "t2.micro" 
} 
 
4. What is a provider in Terraform? 
A provider is a plugin that Terraform uses to manage an external API. Providers define the 
resources and data sources available. 
 
Example: 
 
provider "aws" { 
region = "us-west-2" 
} 
 
5. How does Terraform manage dependencies? 
Terraform uses a dependency graph to manage dependencies between resources. It 
automatically understands the order of operations needed based on resource dependencies. 
Example: 
resource "aws_instance" "web" { 
ami 
= "ami-0c55b159cbfafe1f0" 
instance_type = "t2.micro" 
subnet_id 
= aws_subnet.example.id 
} 
 
resource "aws_subnet" "example" { 
vpc_id 
= aws_vpc.example.id 
cidr_block 
= "10.0.1.0/24" 
} 
 
resource "aws_vpc" "example" { 
cidr_block = "10.0.0.0/16" 
} 
 
6. What is a state file in Terraform? 
A state file is a file that Terraform uses to keep track of the current state of the infrastructure. It 
maps the resources defined in the configuration to the real-world resources. 
 
Example: 
 
terraform show 
 
7. Why is it important to manage the state file in Terraform? 


***

### Page 3

Managing the state file is crucial because it ensures consistency between the infrastructure's real 
state and the configuration. It also enables features like change detection and planning. 
 
Example: 
 
terraform init 
 
8. How can you secure the state file in Terraform? 
State files can be secured by storing them in remote backends with proper access controls and 
encryption, such as AWS S3 with server-side encryption and access control policies. 
 
Example: 
 
terraform { 
backend "s3" { 
bucket = "my-terraform-state" 
key 
= "global/s3/terraform.tfstate" 
region = "us-west-2" 
encrypt = true 
} 
} 
 
9. What are modules in Terraform? 
Modules are reusable packages of Terraform configurations that can be shared and composed to 
manage resources efficiently. 
 
Example: 
 
module "vpc" { 
source = "./modules/vpc" 
} 
 
10. What is the purpose of the terraform init command? 
terraform init initializes a working directory containing Terraform configuration files, 
downloads the necessary provider plugins, and prepares the environment. 
 
Example: 
 
terraform init 
 
11. What does the terraform plan command do? 
terraform plan creates an execution plan, showing what actions Terraform will take to achieve 
the desired state defined in the configuration. 
 
Example: 
 
terraform plan 


***

### Page 4

12. What is the terraform apply command used for? 
terraform apply applies the changes required to reach the desired state of the configuration. 
It executes the plan created by terraform plan. 
 
Example: 
 
terraform apply 
 
13. What is the purpose of the terraform destroy command? 
terraform destroy is used to destroy the infrastructure managed by Terraform. It removes all 
the resources defined in the configuration. 
 
Example: 
 
terraform destroy 
 
14. How do you define and use variables in Terraform? 
Variables in Terraform are defined using the variable block and can be used by referring to 
them with var.<variable_name>. 
 
Example: 
 
variable "instance_type" { 
description = "Type of EC2 instance" 
default 
= "t2.micro" 
} 
 
resource "aws_instance" "example" { 
ami 
= "ami-0c55b159cbfafe1f0" 
instance_type = var.instance_type 
} 
 
15. What are output values in Terraform and how are they used? 
Output values are used to extract information from the resources and make it accessible after 
the apply phase. They can be used to output resource attributes. 
 
Example: 
 
output "instance_id" { 
value = aws_instance.example.id 
} 
 
16. How do you manage different environments (e.g., dev, prod) in 
Terraform? 


***

### Page 5

Different environments can be managed using workspaces or separate directories with different 
variable files and state files. 
 
Example: 
 
terraform workspace new dev 
terraform workspace new prod 
 
17. What is remote state and how do you configure it in Terraform? 
Remote state allows Terraform to store the state file in a remote storage backend, enabling team 
collaboration and secure storage. 
 
Example: 
 
terraform { 
backend "s3" { 
bucket = "my-terraform-state" 
key 
= "global/s3/terraform.tfstate" 
region = "us-west-2" 
} 
} 
 
18. How do you import existing resources into Terraform? 
Existing resources can be imported using the terraform import command, which maps the 
existing resource to a Terraform resource in the state file. 
 
Example: 
 
terraform import aws_instance.example i-1234567890abcdef0 
 
19. What are data sources in Terraform? 
Data sources allow Terraform to fetch data from existing infrastructure or services to use in 
resource definitions. 
 
Example: 
 
data "aws_ami" "example" { 
most_recent = true 
owners 
= ["amazon"] 
 
filter { 
name 
= "name" 
values = ["amzn-ami-hvm-*"] 
} 
} 
 
20. What are provisioners in Terraform? 


***

### Page 6

Provisioners are used to execute scripts or commands on a local or remote machine as part of 
the resource lifecycle. 
 
Example: 
 
resource "aws_instance" "example" { 
ami 
= "ami-0c55b159cbfafe1f0" 
instance_type = "t2.micro" 
 
provisioner "local-exec" { 
command = "echo ${self.public_ip} > ip_address.txt" 
} 
} 
 
21. How do you handle secrets in Terraform? 
Secrets can be managed using environment variables, secure secret management services (e.g., 
AWS Secrets Manager), or Terraform's sensitive attribute. 
 
Example: 
 
resource "aws_secretsmanager_secret" "example" { 
name 
= "example" 
description = "An example secret" 
} 
 
resource "aws_secretsmanager_secret_version" "example" { 
secret_id 
= aws_secretsmanager_secret.example.id 
secret_string = jsonencode({ 
username = "example_user" 
password = "example_password" 
}) 
} 
 
22. What is a backend in Terraform? 
A backend in Terraform defines where and how state is loaded and stored. It can be local or 
remote (e.g., S3, Consul, etc.). 
 
Example: 
 
terraform { 
backend "s3" { 
bucket = "my-terraform-state" 
key 
= "global/s3/terraform.tfstate" 
region = "us-west-2" 
} 
} 
 
23. How do you use conditional expressions in Terraform? 
Conditional expressions in Terraform are used to assign values based on conditions using the 
ternary operator condition ? true_value : false_value. 


***

### Page 7

Example: 
 
variable "environment" { 
default = "dev" 
} 
 
resource "aws_instance" "example" { 
ami 
= "ami-0c55b159cbfafe1f0" 
instance_type = var.environment == "prod" ? "t2.large" : "t2.micro" 
} 
 
24. What is the purpose of the terraform validate command? 
terraform validate is used to validate the syntax and configuration of the Terraform files 
without creating any resources. 
 
Example: 
 
terraform validate 
 
25. How can you format Terraform configuration files? 
Terraform configuration files can be formatted using the terraform fmt command, which 
formats the files according to the 
 
Terraform style guide. 
 
Example: 
 
terraform fmt 
 
26. What is the difference between count and for_each in Terraform? 
count is used to create multiple instances of a resource, while for_each is used to iterate over a 
map or set of values to create multiple instances. 
 
Example (count): 
 
resource "aws_instance" "example" { 
count 
= 3 
ami 
= "ami-0c55b159cbfafe1f0" 
instance_type = "t2.micro" 
} 
Example (for_each): 
 
resource "aws_instance" "example" { 
for_each 
= toset(["instance1", "instance2"]) 
ami 
= "ami-0c55b159cbfafe1f0" 
instance_type = "t2.micro" 
tags = { 
Name = each.key 
} 
} 


***

### Page 8

27. How do you use loops in Terraform? 
Loops in Terraform can be implemented using the count and for_each meta-arguments, as 
well as the for expression in variable assignments. 
 
Example: 
 
variable "instance_names" { 
type = list(string) 
default = ["instance1", "instance2"] 
} 
 
resource "aws_instance" "example" { 
for_each 
= toset(var.instance_names) 
ami 
= "ami-0c55b159cbfafe1f0" 
instance_type = "t2.micro" 
tags = { 
Name = each.key 
} 
} 
 
28. What are locals in Terraform and how do you use them? 
Locals in Terraform are used to define local values that can be reused within a module. They help 
avoid repetition and make configurations more readable. 
 
Example: 
 
locals { 
instance_type = "t2.micro" 
ami_id 
= "ami-0c55b159cbfafe1f0" 
} 
 
resource "aws_instance" "example" { 
ami 
= local.ami_id 
instance_type = local.instance_type 
} 
 
29. What is the purpose of the terraform taint command? 
terraform taint marks a resource for recreation on the next terraform apply. It is useful 
when a resource needs to be replaced due to a manual change or corruption. 
 
Example: 
 
terraform taint aws_instance.example 
 
30. How do you manage module versioning in Terraform? 
Module versioning in Terraform can be managed using the version argument in 
the source attribute of a module block, typically in combination with a registry. 
 
Example: 


***

### Page 9

module "vpc" { 
source = "terraform-aws-modules/vpc/aws" 
version = "2.0.0" 
} 
 
31. What is the Terraform Registry? 
The Terraform Registry is a public repository of Terraform modules and providers that can be 
used to discover and use pre-built modules and providers. 
 
Example: 
 
module "vpc" { 
source = "terraform-aws-modules/vpc/aws" 
version = "2.0.0" 
} 
 
32. How do you perform a dry run in Terraform? 
A dry run in Terraform can be performed using the terraform plan command, which shows 
the execution plan without making any changes. 
 
Example: 
 
terraform plan 
 
33. What is the terraform state command used for? 
The terraform state command is used to manage and manipulate the state file. It provides 
subcommands to move, remove, list, and inspect resources in the state file. 
 
Example: 
 
terraform state list 
 
34. How do you rename a resource in the state file? 
A resource can be renamed in the state file using the terraform state mv command, which 
moves the state of a resource to a new address. 
 
Example: 
 
terraform state mv aws_instance.old_name aws_instance.new_name 
 
35. What is the purpose of the terraform workspace command? 
The terraform workspace command is used to manage multiple workspaces, allowing for 
different states to be associated with the same configuration. 
 
Example: 


***

### Page 10

terraform workspace new dev 
terraform workspace select dev 
 
36. How do you debug Terraform configurations? 
Debugging Terraform configurations can be done using the TF_LOG environment variable to set 
the log level and the terraform console command to interact with the configuration. 
 
Example: 
 
export TF_LOG=DEBUG 
terraform apply 
 
37. What is the difference between local and remote backends in 
Terraform? 
Local backends store the state file on the local filesystem, while remote backends store the state 
file in a remote storage service (e.g., S3, Consul). 
 
Example (local backend): 
 
terraform { 
backend "local" { 
path = "terraform.tfstate" 
} 
} 
Example (remote backend): 
 
terraform { 
backend "s3" { 
bucket = "my-terraform-state" 
key 
= "global/s3/terraform.tfstate" 
region = "us-west-2" 
} 
} 
 
38. How do you handle provider versioning in Terraform? 
Provider versioning in Terraform is managed using the required_providers block in 
the terraform block, specifying the version constraints. 
 
Example: 
 
terraform { 
required_providers { 
aws = { 
source = "hashicorp/aws" 
version = "~> 3.0" 
} 
} 
} 
 
39. What is the purpose of the terraform refresh command? 


***

### Page 11

terraform refresh updates the state file with the current state of the infrastructure without 
making any changes to the configuration. 
 
Example: 
 
terraform refresh 
 
40. How do you generate and view a resource graph in Terraform? 
A resource graph can be generated using the terraform graph command and can be viewed 
using tools like Graphviz. 
 
Example: 
 
terraform graph | dot -Tpng > graph.png 
 
41. What are lifecycle blocks in Terraform? 
lifecycle blocks in Terraform are used to customize the lifecycle of a resource, such as creating 
before destroying, ignoring changes, and preventing deletion. 
 
Example: 
 
resource "aws_instance" "example" { 
ami 
= "ami-0c55b159cbfafe1f0" 
instance_type = "t2.micro" 
 
lifecycle { 
create_before_destroy = true 
} 
} 
 
42. How do you ignore changes to a resource attribute in Terraform? 
Changes to a resource attribute can be ignored using the ignore_changes argument in 
a lifecycle block. 
 
Example: 
 
resource "aws_instance" "example" { 
ami 
= "ami-0c55b159cbfafe1f0" 
instance_type = "t2.micro" 
 
lifecycle { 
ignore_changes = [ami] 
} 
} 
 
43. What is the terraform import command used for? 
terraform import is used to import existing infrastructure into Terraform's state file, mapping 
it to resources defined in the configuration. 


***

### Page 12

Example: 
 
terraform import aws_instance.example i-1234567890abcdef0 
 
44. How do you use output values across different modules in Terraform? 
Output values from one module can be referenced in another module by using the module's 
output attributes. 
 
Example: 
 
module "vpc" { 
source = "./modules/vpc" 
} 
 
output "vpc_id" { 
value = module.vpc.vpc_id 
} 
 
45. What is the difference between terraform output and output values in 
configuration? 
terraform output is a command that displays the output values of a Terraform configuration, 
while output values in configuration are defined using the output block. 
 
Example (command): 
 
terraform output 
Example (configuration): 
 
output "instance_id" { 
value = aws_instance.example.id 
} 
 
46. What are dynamic blocks in Terraform? 
Dynamic blocks in Terraform are used to generate multiple nested blocks within a resource or 
module based on dynamic content. 
 
Example: 
 
resource "aws_security_group" "example" { 
name 
= "example-sg" 
description = "Example security group" 
 
dynamic "ingress" { 
for_each = var.ingress_rules 
content { 
from_port 
= ingress.value.from_port 
to_port 
= ingress.value.to_port 
protocol 
= ingress.value.protocol 
cidr_blocks = ingress.value.cidr_blocks 
} 


***

### Page 13

} 
} 
 
47. How do you define and use maps in Terraform? 
Maps in Terraform are defined using the map type and can be used to store key-value pairs. They 
are accessed using the key. 
 
Example: 
 
variable "ami_ids" { 
type = map(string) 
default = { 
us-east-1 = "ami-0c55b159cbfafe1f0" 
us-west-2 = "ami-0d5eff06f840b45e9" 
} 
} 
 
resource "aws_instance" "example" { 
ami 
= var.ami_ids[var.region] 
instance_type = "t2.micro" 
} 
 
48. What is a count parameter in Terraform? 
The 
 
count parameter in Terraform is used to create multiple instances of a resource based on a 
specified number. 
 
Example: 
 
resource "aws_instance" "example" { 
count 
= 3 
ami 
= "ami-0c55b159cbfafe1f0" 
instance_type = "t2.micro" 
} 
 
49. What are Terraform Cloud and Terraform Enterprise? 
Terraform Cloud and Terraform Enterprise are commercial versions of Terraform that provide 
collaboration, governance, and automation features. 
 
Example: 
 
terraform { 
backend "remote" { 
organization = "my-org" 
workspaces { 
name = "my-workspace" 
} 
} 
} 


***

### Page 14

50. How do you use a Terraform backend? 
A backend is configured using the terraform block in the configuration file, specifying the 
backend type and its configuration. 
 
Example: 
 
terraform { 
backend "s3" { 
bucket = "my-terraform-state" 
key 
= "global/s3/terraform.tfstate" 
region = "us-west-2" 
} 
} 
 
51. What is the terraform fmt command used for? 
terraform fmt formats the configuration files to follow the Terraform style guide, making the 
code consistent and readable. 
 
Example: 
 
terraform fmt 
 
52. How do you use a lock file in Terraform? 
A lock file (.terraform.lock.hcl) is used to lock provider versions, ensuring consistency in 
provider versions across different environments. 
 
Example: 
 
terraform init 
 
53. What is the purpose of the terraform workspace command? 
The terraform workspace command is used to create, select, and manage multiple 
workspaces, allowing different states to be associated with the same configuration. 
 
Example: 
 
terraform workspace new dev 
terraform workspace select dev 
 
54. How do you manage secrets in Terraform? 
Secrets can be managed using environment variables, secure secret management services (e.g., 
AWS Secrets Manager), or Terraform's sensitive attribute. 
 
Example: 


***

### Page 15

resource "aws_secretsmanager_secret" "example" { 
name 
= "example" 
description = "An example secret" 
} 
 
resource "aws_secretsmanager_secret_version" "example" { 
secret_id 
= aws_secretsmanager_secret.example.id 
secret_string = jsonencode({ 
username = "example_user" 
password = "example_password" 
}) 
} 
 
55. What is the terraform console command used for? 
terraform console opens an interactive console for evaluating expressions, testing 
interpolation syntax, and debugging configurations. 
 
Example: 
 
terraform console 
 
56. How do you reference data sources in Terraform? 
Data sources are referenced using the data block and can be used to fetch information about 
existing infrastructure or services. 
 
Example: 
 
data "aws_ami" "example" { 
most_recent = true 
owners 
= ["amazon"] 
 
filter { 
name 
= "name" 
values = ["amzn-ami-hvm-*"] 
} 
} 
 
resource "aws_instance" "example" { 
ami 
= data.aws_ami.example.id 
instance_type = "t2.micro" 
} 
 
57. What is the purpose of the terraform state mv command? 
terraform state mv moves a resource in the state file to a new address, useful for renaming 
resources without recreating them. 
 
Example: 
 
terraform state mv aws_instance.old_name aws_instance.new_name 
 
58. How do you use conditional expressions in Terraform? 


***

### Page 16

Conditional expressions in Terraform are used to assign values based on conditions using the 
ternary operator condition ? true_value : false_value. 
 
Example: 
 
variable "environment" { 
default = "dev" 
} 
 
resource "aws_instance" "example" { 
ami 
= "ami-0c55b159cbfafe1f0" 
instance_type = var.environment == "prod" ? "t2.large" : "t2.micro" 
} 
 
59. What is the terraform taint command used for? 
terraform taint marks a resource for recreation on the next terraform apply. It is useful 
when a resource needs to be replaced due to a manual change or corruption. 
 
Example: 
 
terraform taint aws_instance.example 
 
60. How do you define and use maps in Terraform? 
Maps in Terraform are defined using the map type and can be used to store key-value pairs. They 
are accessed using the key. 
 
Example: 
 
variable "ami_ids" { 
type = map(string) 
default = { 
us-east-1 = "ami-0c55b159cbfafe1f0" 
us-west-2 = "ami-0d5eff06f840b45e9" 
} 
} 
 
resource "aws_instance" "example" { 
ami 
= var.ami_ids[var.region] 
instance_type = "t2.micro" 
} 
 
61. How do you handle provider versioning in Terraform? 
Provider versioning in Terraform is managed using the required_providers block in 
the terraform block, specifying the version constraints. 
 
Example: 
 
terraform { 
required_providers { 
aws = { 


***

### Page 17

source = "hashicorp/aws" 
version = "~> 3.0" 
} 
} 
} 
 
62. What is the purpose of the terraform refresh command? 
terraform refresh updates the state file with the current state of the infrastructure without 
making any changes to the configuration. 
 
Example: 
 
terraform refresh 
 
63. What are lifecycle blocks in Terraform? 
lifecycle blocks in Terraform are used to customize the lifecycle of a resource, such as creating 
before destroying, ignoring changes, and preventing deletion. 
 
Example: 
 
resource "aws_instance" "example" { 
ami 
= "ami-0c55b159cbfafe1f0" 
instance_type = "t2.micro" 
 
lifecycle { 
create_before_destroy = true 
} 
} 
 
64. How do you use loops in Terraform? 
Loops in Terraform can be implemented using the count and for_each meta-arguments, as 
well as the for expression in variable assignments. 
 
Example: 
 
variable "instance_names" { 
type = list(string) 
default = ["instance1", "instance2"] 
} 
 
resource "aws_instance" "example" { 
for_each 
= toset(var.instance_names) 
ami 
= "ami-0c55b159cbfafe1f0" 
instance_type = "t2.micro" 
tags = { 
Name = each.key 
} 
} 
 
65. What is the terraform import command used for? 


***

### Page 18

terraform import is used to import existing infrastructure into Terraform's state file, mapping 
it to resources defined in the configuration. 
 
Example: 
 
terraform import aws_instance.example i-1234567890abcdef0 
 
66. How do you use output values across different modules in Terraform? 
Output values from one module can be referenced in another module by using the module's 
output attributes. 
 
Example: 
 
module "vpc" { 
source = "./modules/vpc" 
} 
 
output "vpc_id" { 
value = module.vpc.vpc_id 
} 
 
67. What is the difference between terraform output and output values in 
configuration? 
terraform output is a command that displays the output values of a Terraform configuration, 
while output values in configuration are defined using the output block. 
 
Example (command): 
 
terraform output 
Example (configuration): 
 
output "instance_id" { 
value = aws_instance.example.id 
} 
 
68. What are dynamic blocks in Terraform? 
Dynamic blocks in Terraform are used to generate multiple nested blocks within a resource or 
module based on dynamic content. 
 
Example: 
 
resource "aws_security_group" "example" { 
name 
= "example-sg" 
description = "Example security group" 
 
dynamic "ingress" { 
for_each = var.ingress_rules 
content { 
from_port 
= ingress.value.from_port 


***

### Page 19

to_port 
= ingress.value.to_port 
protocol 
= ingress.value.protocol 
cidr_blocks = ingress.value.cidr_blocks 
} 
} 
} 
 
69. How do you manage different environments (e.g., dev, prod) in 
Terraform? 
Different environments can be managed using workspaces or separate directories with different 
variable files and state files. 
 
Example: 
 
terraform workspace new dev 
terraform workspace new prod 
 
70. How do you handle secrets in Terraform? 
Secrets can be managed using environment variables, secure secret management services (e.g., 
AWS Secrets Manager), or Terraform's sensitive attribute. 
 
Example: 
 
resource "aws_secretsmanager_secret" "example" { 
name 
= "example" 
description = "An example secret" 
} 
 
resource "aws_secretsmanager_secret_version" "example" { 
secret_id 
= aws_secretsmanager_secret.example.id 
secret_string = jsonencode({ 
username = "example_user" 
password = "example_password" 
}) 
} 
 
71. What is the terraform console command used for? 
terraform console opens an interactive console for evaluating expressions, testing 
interpolation syntax, and debugging 
 
configurations. 
 
Example: 
 
terraform console 
 
72. How do you reference data sources in Terraform? 


***

### Page 20

Data sources are referenced using the data block and can be used to fetch information about 
existing infrastructure or services. 
 
Example: 
 
data "aws_ami" "example" { 
most_recent = true 
owners 
= ["amazon"] 
 
filter { 
name 
= "name" 
values = ["amzn-ami-hvm-*"] 
} 
} 
 
resource "aws_instance" "example" { 
ami 
= data.aws_ami.example.id 
instance_type = "t2.micro" 
} 
 
73. What is the purpose of the terraform state mv command? 
terraform state mv moves a resource in the state file to a new address, useful for renaming 
resources without recreating them. 
 
Example: 
 
terraform state mv aws_instance.old_name aws_instance.new_name 
 
74. What is a backend in Terraform? 
A backend in Terraform defines where and how state is loaded and stored. It can be local or 
remote (e.g., S3, Consul, etc.). 
 
Example: 
 
terraform { 
backend "s3" { 
bucket = "my-terraform-state" 
key 
= "global/s3/terraform.tfstate" 
region = "us-west-2" 
} 
} 
 
75. How do you secure the state file in Terraform? 
State files can be secured by storing them in remote backends with proper access controls and 
encryption, such as AWS S3 with server-side encryption and access control policies. 
 
Example: 
 
terraform { 
backend "s3" { 


***

### Page 21

bucket = "my-terraform-state" 
key 
= "global/s3/terraform.tfstate" 
region = "us-west-2" 
encrypt = true 
} 
} 
 
76. What is the difference between local and remote backends in 
Terraform? 
Local backends store the state file on the local filesystem, while remote backends store the state 
file in a remote storage service (e.g., S3, Consul). 
 
Example (local backend): 
 
terraform { 
backend "local" { 
path = "terraform.tfstate" 
} 
} 
Example (remote backend): 
 
terraform { 
backend "s3" { 
bucket = "my-terraform-state" 
key 
= "global/s3/terraform.tfstate" 
region = "us-west-2" 
} 
} 
 
77. How do you manage module versioning in Terraform? 
Module versioning in Terraform can be managed using the version argument in 
the source attribute of a module block, typically in combination with a registry. 
 
Example: 
 
module "vpc" { 
source = "terraform-aws-modules/vpc/aws" 
version = "2.0.0" 
} 
 
78. What is the Terraform Registry? 
The Terraform Registry is a public repository of Terraform modules and providers that can be 
used to discover and use pre-built modules and providers. 
 
Example: 
 
module "vpc" { 
source = "terraform-aws-modules/vpc/aws" 
version = "2.0.0" 
} 


***

### Page 22

79. How do you generate and view a resource graph in Terraform? 
A resource graph can be generated using the terraform graph command and can be viewed 
using tools like Graphviz. 
 
Example: 
 
terraform graph | dot -Tpng > graph.png 
 
80. What is the purpose of the terraform validate command? 
terraform validate is used to validate the syntax and configuration of the Terraform files 
without creating any resources. 
 
Example: 
 
terraform validate 
 
81. What is the terraform fmt command used for? 
terraform fmt formats the configuration files to follow the Terraform style guide, making the 
code consistent and readable. 
 
Example: 
 
terraform fmt 
 
82. What are locals in Terraform and how do you use them? 
Locals in Terraform are used to define local values that can be reused within a module. They help 
avoid repetition and make configurations more readable. 
 
Example: 
 
locals { 
instance_type = "t2.micro" 
ami_id 
= "ami-0c55b159cbfafe1f0" 
} 
 
resource "aws_instance" "example" { 
ami 
= local.ami_id 
instance_type = local.instance_type 
} 
 
83. How do you handle provider dependencies in Terraform? 
Provider dependencies in Terraform are managed using the required_providers block in 
the terraform block, specifying the version constraints. 
 
Example: 


***

### Page 23

terraform { 
required_providers { 
aws = { 
source = "hashicorp/aws" 
version = "~> 3.0" 
} 
} 
} 
 
84. What is the terraform apply command used for? 
terraform apply applies the changes required to reach the desired state of the configuration. 
It executes the plan created by terraform plan. 
 
Example: 
 
terraform apply 
 
85. What is the terraform destroy command used for? 
terraform destroy is used to destroy the infrastructure managed by Terraform. It removes all 
the resources defined in the configuration. 
 
Example: 
 
terraform destroy 
 
86. What are output values in Terraform and how are they used? 
Output values are used to extract information from the resources and make it accessible after 
the apply phase. They can be used to output resource attributes. 
 
Example: 
 
output "instance_id" { 
value = aws_instance.example.id 
} 
 
87. How do you manage different environments (e.g., dev, prod) in 
Terraform? 
Different environments can be managed using workspaces or separate directories with different 
variable files and state files. 
 
Example: 
 
terraform workspace new dev 
terraform workspace new prod 
 
88. What is the difference between count and for_each in Terraform? 


***

### Page 24

count is used to create multiple instances of a resource, while for_each is used to iterate over a 
map or set of values to create multiple instances. 
 
Example (count): 
 
resource "aws_instance" "example" { 
count 
= 3 
ami 
= "ami-0c55b159cbfafe1f0" 
instance_type = "t2.micro" 
} 
Example (for_each): 
 
resource "aws_instance" "example" { 
for_each 
= toset(["instance1", "instance2"]) 
ami 
= "ami-0c55b159cbfafe1f0" 
instance_type = "t2.micro" 
tags = { 
Name = each.key 
} 
} 
 
89. How do you use loops in Terraform? 
Loops in Terraform can be implemented using the count and for_each meta-arguments, as 
well as the for expression in variable assignments. 
 
Example: 
 
variable "instance_names" { 
type = list(string) 
default = ["instance1", "instance2"] 
} 
 
resource "aws_instance" "example" { 
for_each 
= toset(var.instance_names) 
ami 
= "ami-0c55b159cbfafe1f0" 
instance_type = "t2.micro" 
tags = { 
Name = each.key 
} 
} 
 
90. What is a count parameter in Terraform? 
The count parameter in Terraform is used to create multiple instances of a resource based on a 
specified number. 
 
Example: 
 
resource "aws_instance" "example" { 
count 
= 3 
ami 
= "ami-0c55b159cbfafe1f0" 
instance_type = "t2.micro" 
} 


***

### Page 25

91. What are Terraform Cloud and Terraform Enterprise? 
Terraform Cloud and Terraform Enterprise are commercial versions of Terraform that provide 
collaboration, governance, and automation features. 
 
Example: 
 
terraform { 
backend "remote" { 
organization = "my-org" 
workspaces { 
name = "my-workspace" 
} 
} 
} 
 
92. How do you use a Terraform backend? 
A backend is configured using the terraform block in the configuration file, specifying the 
backend type and its configuration. 
 
Example: 
 
terraform { 
backend "s3" { 
bucket = "my-terraform-state" 
key 
= "global/s3/terraform.tfstate" 
region = "us-west-2" 
} 
} 
 
93. What is the terraform fmt command used for? 
terraform fmt formats the configuration files to follow the Terraform style guide, making the 
code consistent and readable. 
 
Example: 
 
terraform fmt 
 
94. How do you use a lock file in Terraform? 
A lock file (.terraform.lock.hcl) is used to lock provider versions, ensuring consistency in 
provider versions across different environments. 
 
Example: 
 
terraform init 
 
95. What is the purpose of the terraform workspace command? 


***

### Page 26

The terraform workspace command is used to create, select, and manage multiple 
workspaces, allowing different states to be associated with the same configuration. 
 
Example: 
 
terraform workspace new dev 
terraform workspace select dev 
 
96. **How do you manage secrets 
in Terraform?** 
 
Secrets can be managed using environment variables, secure secret management services (e.g., 
AWS Secrets Manager), or Terraform's sensitive attribute. 
 
Example: 
 
resource "aws_secretsmanager_secret" "example" { 
name 
= "example" 
description = "An example secret" 
} 
 
resource "aws_secretsmanager_secret_version" "example" { 
secret_id 
= aws_secretsmanager_secret.example.id 
secret_string = jsonencode({ 
username = "example_user" 
password = "example_password" 
}) 
} 
 
97. What is the terraform console command used for? 
terraform console opens an interactive console for evaluating expressions, testing 
interpolation syntax, and debugging configurations. 
 
Example: 
 
terraform console 
 
98. How do you reference data sources in Terraform? 
Data sources are referenced using the data block and can be used to fetch information about 
existing infrastructure or services. 
 
Example: 
 
data "aws_ami" "example" { 
most_recent = true 
owners 
= ["amazon"] 
 
filter { 
name 
= "name" 
values = ["amzn-ami-hvm-*"] 


***

### Page 27

} 
} 
 
resource "aws_instance" "example" { 
ami 
= data.aws_ami.example.id 
instance_type = "t2.micro" 
} 
 
99. What is the purpose of the terraform state mv command? 
terraform state mv moves a resource in the state file to a new address, useful for renaming 
resources without recreating them. 
 
Example: 
 
terraform state mv aws_instance.old_name aws_instance.new_name 
 
100. What is a backend in Terraform? 
A backend in Terraform defines where and how state is loaded and stored. It can be local or 
remote (e.g., S3, Consul, etc.). 
 
Example: 
 
terraform { 
backend "s3" { 
bucket = "my-terraform-state" 
key 
= "global/s3/terraform.tfstate" 
region = "us-west-2" 
} 
} 
 
101. How do you secure the state file in Terraform? 
State files can be secured by storing them in remote backends with proper access controls and 
encryption, such as AWS S3 with server-side encryption and access control policies. 
 
Example: 
 
terraform { 
backend "s3" { 
bucket = "my-terraform-state" 
key 
= "global/s3/terraform.tfstate" 
region = "us-west-2" 
encrypt = true 
} 
} 
 
102. What is the difference between local and remote backends in 
Terraform? 
Local backends store the state file on the local filesystem, while remote backends store the state 
file in a remote storage service (e.g., S3, Consul). 


***

### Page 28

Example (local backend): 
 
terraform { 
backend "local" { 
path = "terraform.tfstate" 
} 
} 
Example (remote backend): 
 
terraform { 
backend "s3" { 
bucket = "my-terraform-state" 
key 
= "global/s3/terraform.tfstate" 
region = "us-west-2" 
} 
} 
 
103. How do you manage module versioning in Terraform? 
Module versioning in Terraform can be managed using the version argument in 
the source attribute of a module block, typically in combination with a registry. 
 
Example: 
 
module "vpc" { 
source = "terraform-aws-modules/vpc/aws" 
version = "2.0.0" 
} 
 
104. What is the Terraform Registry? 
The Terraform Registry is a public repository of Terraform modules and providers that can be 
used to discover and use pre-built modules and providers. 
 
Example: 
 
module "vpc" { 
source = "terraform-aws-modules/vpc/aws" 
version = "2.0.0" 
} 
 
105. How do you generate and view a resource graph in Terraform? 
A resource graph can be generated using the terraform graph command and can be viewed 
using tools like Graphviz. 
 
Example: 
 
terraform graph | dot -Tpng > graph.png 
 
106. What is the purpose of the terraform validate command? 


***

### Page 29

terraform validate is used to validate the syntax and configuration of the Terraform files 
without creating any resources. 
 
Example: 
 
terraform validate 
 
107. What is the terraform fmt command used for? 
terraform fmt formats the configuration files to follow the Terraform style guide, making the 
code consistent and readable. 
 
Example: 
 
terraform fmt 
 
108. What are locals in Terraform and how do you use them? 
Locals in Terraform are used to define local values that can be reused within a module. They help 
avoid repetition and make configurations more readable. 
 
Example: 
 
locals { 
instance_type = "t2.micro" 
ami_id 
= "ami-0c55b159cbfafe1f0" 
} 
 
resource "aws_instance" "example" { 
ami 
= local.ami_id 
instance_type = local.instance_type 
} 
 
109. How do you handle provider dependencies in Terraform? 
Provider dependencies in Terraform are managed using the required_providers block in 
the terraform block, specifying the version constraints. 
 
Example: 
 
terraform { 
required_providers { 
aws = { 
source = "hashicorp/aws" 
version = "~> 3.0" 
} 
} 
} 
 
110. What is the terraform apply command used for? 


***

### Page 30

terraform apply applies the changes required to reach the desired state of the configuration. 
It executes the plan created by terraform plan. 
 
Example: 
 
terraform apply 
 
111. What is the terraform destroy command used for? 
terraform destroy is used to destroy the infrastructure managed by Terraform. It removes all 
the resources defined in the configuration. 
 
Example: 
 
terraform destroy 
 
112. What are output values in Terraform and how are they used? 
Output values are used to extract information from the resources and make it accessible after 
the apply phase. They can be used to output resource attributes. 
 
Example: 
 
output "instance_id" { 
value = aws_instance.example.id 
} 
 
113. How do you manage different environments (e.g., dev, prod) in 
Terraform? 
Different environments can be managed using workspaces or separate directories with different 
variable files and state files. 
 
Example: 
 
terraform workspace new dev 
terraform workspace new prod 
 
114. What is the difference between count and for_each in Terraform? 
count is used to create multiple instances of a resource, while for_each is used to iterate over a 
map or set of values to create multiple instances. 
 
Example (count): 
 
resource "aws_instance" "example" { 
count 
= 3 
ami 
= "ami-0c55b159cbfafe1f0" 
instance_type = "t2.micro" 
} 


***

### Page 31

Example (for_each): 
 
resource "aws_instance" "example" { 
for_each 
= toset(["instance1", "instance2"]) 
ami 
= "ami-0c55b159cbfafe1f0" 
instance_type = "t2.micro" 
tags = { 
Name = each.key 
} 
} 
 
115. How do you use loops in Terraform? 
Loops in Terraform can be implemented using the count and for_each meta-arguments, as 
well as the for expression in variable assignments. 
 
Example: 
 
variable "instance_names" { 
type = list(string) 
default = ["instance1", "instance2"] 
} 
 
resource "aws_instance" "example" { 
for_each 
= toset(var.instance_names) 
ami 
= "ami-0c55b159cbfafe1f0" 
instance_type = "t2.micro" 
tags = { 
Name = each.key 
} 
} 
 
116. What is a count parameter in Terraform? 
The count parameter in Terraform is used to create multiple instances of a resource based on a 
specified number. 
 
Example: 
 
resource "aws_instance" "example" { 
count 
= 3 
ami 
= "ami-0c55b159cbfafe1f0" 
instance_type = "t2.micro" 
} 
 
117. What are Terraform Cloud and Terraform Enterprise? 
Terraform Cloud and Terraform Enterprise are commercial versions of Terraform that provide 
collaboration, governance, and automation features. 
 
Example: 
 
terraform { 
backend "remote" { 


***

### Page 32

organization = "my-org" 
workspaces { 
name = "my-workspace" 
} 
} 
} 
 
118. How do you use a Terraform backend? 
A backend is configured using the terraform block in the configuration file, specifying the 
backend type and its configuration. 
 
Example: 
 
terraform { 
backend "s3" { 
bucket = "my-terraform-state" 
key 
= "global/s3/terraform.tfstate" 
region = "us-west-2" 
} 
} 
 
119. What is the terraform fmt command used for? 
terraform fmt formats the configuration files 
 
to follow the Terraform style guide, making the code consistent and readable. 
Example: 
terraform fmt 
 
120. How do you use a lock file in Terraform? 
A lock file (.terraform.lock.hcl) is used to lock provider versions, ensuring consistency in 
provider versions across different environments. 
 
Example: 
 
terraform init 
 
121. What is the purpose of the terraform workspace command? 
The terraform workspace command is used to create, select, and manage multiple 
workspaces, allowing different states to be associated with the same configuration. 
 
Example: 
 
terraform workspace new dev 
terraform workspace select dev 


***

### Page 33

122. How do you manage secrets in Terraform? 
Secrets can be managed using environment variables, secure secret management services (e.g., 
AWS Secrets Manager), or Terraform's sensitive attribute. 
 
Example: 
 
resource "aws_secretsmanager_secret" "example" { 
name 
= "example" 
description = "An example secret" 
} 
 
resource "aws_secretsmanager_secret_version" "example" { 
secret_id 
= aws_secretsmanager_secret.example.id 
secret_string = jsonencode({ 
username = "example_user" 
password = "example_password" 
}) 
} 
 
123. What is the terraform console command used for? 
terraform console opens an interactive console for evaluating expressions, testing 
interpolation syntax, and debugging configurations. 
 
Example: 
 
terraform console 
 
124. How do you reference data sources in Terraform? 
Data sources are referenced using the data block and can be used to fetch information about 
existing infrastructure or services. 
 
Example: 
 
data "aws_ami" "example" { 
most_recent = true 
owners 
= ["amazon"] 
 
filter { 
name 
= "name" 
values = ["amzn-ami-hvm-*"] 
} 
} 
 
resource "aws_instance" "example" { 
ami 
= data.aws_ami.example.id 
instance_type = "t2.micro" 
} 
 
125. What is the purpose of the terraform state mv command? 


***

### Page 34

terraform state mv moves a resource in the state file to a new address, useful for renaming 
resources without recreating them. 
 
Example: 
 
terraform state mv aws_instance.old_name aws_instance.new_name 
 
126. What is a backend in Terraform? 
A backend in Terraform defines where and how state is loaded and stored. It can be local or 
remote (e.g., S3, Consul, etc.). 
 
Example: 
 
terraform { 
backend "s3" { 
bucket = "my-terraform-state" 
key 
= "global/s3/terraform.tfstate" 
region = "us-west-2" 
} 
} 
 
127. How do you secure the state file in Terraform? 
State files can be secured by storing them in remote backends with proper access controls and 
encryption, such as AWS S3 with server-side encryption and access control policies. 
 
Example: 
 
terraform { 
backend "s3" { 
bucket = "my-terraform-state" 
key 
= "global/s3/terraform.tfstate" 
region = "us-west-2" 
encrypt = true 
} 
} 
 
128. What is the difference between local and remote backends in 
Terraform? 
Local backends store the state file on the local filesystem, while remote backends store the state 
file in a remote storage service (e.g., S3, Consul). 
 
Example (local backend): 
 
terraform { 
backend "local" { 
path = "terraform.tfstate" 
} 
} 
Example (remote backend): 


***

### Page 35

terraform { 
backend "s3" { 
bucket = "my-terraform-state" 
key 
= "global/s3/terraform.tfstate" 
region = "us-west-2" 
} 
} 
 
129. How do you manage module versioning in Terraform? 
Module versioning in Terraform can be managed using the version argument in 
the source attribute of a module block, typically in combination with a registry. 
 
Example: 
 
module "vpc" { 
source = "terraform-aws-modules/vpc/aws" 
version = "2.0.0" 
} 
 
130. What is the Terraform Registry? 
The Terraform Registry is a public repository of Terraform modules and providers that can be 
used to discover and use pre-built modules and providers. 
 
Example: 
 
module "vpc" { 
source = "terraform-aws-modules/vpc/aws" 
version = "2.0.0" 
} 
 
131. How do you generate and view a resource graph in Terraform? 
A resource graph can be generated using the terraform graph command and can be viewed 
using tools like Graphviz. 
 
Example: 
 
terraform graph | dot -Tpng > graph.png 
 
132. What is the purpose of the terraform validate command? 
terraform validate is used to validate the syntax and configuration of the Terraform files 
without creating any resources. 
 
Example: 
 
terraform validate 
 
133. What is the terraform fmt command used for? 


***

### Page 36

terraform fmt formats the configuration files to follow the Terraform style guide, making the 
code consistent and readable. 
 
Example: 
 
terraform fmt 
 
134. What are locals in Terraform and how do you use them? 
Locals in Terraform are used to define local values that can be reused within a module. They help 
avoid repetition and make configurations more readable. 
 
Example: 
 
locals { 
instance_type = "t2.micro" 
ami_id 
= "ami-0c55b159cbfafe1f0" 
} 
 
resource "aws_instance" "example" { 
ami 
= local.ami_id 
instance_type = local.instance_type 
} 
 
135. How do you handle provider dependencies in Terraform? 
Provider dependencies in Terraform are managed using the required_providers block in 
the terraform block, specifying the version constraints. 
 
Example: 
 
terraform { 
required_providers { 
aws = { 
source = "hashicorp/aws" 
version = "~> 3.0" 
} 
} 
} 
 
136. What is the terraform apply command used for? 
terraform apply applies the changes required to reach the desired state of the configuration. 
It executes the plan created by terraform plan. 
 
Example: 
 
terraform apply 
 
137. What is the terraform destroy command used for? 


***

### Page 37

terraform destroy is used to destroy the infrastructure managed by Terraform. It removes all 
the resources defined in the configuration. 
 
Example: 
 
terraform destroy 
 
138. What are output values in Terraform and how are they used? 
Output values are used to extract information from the resources and make it accessible after 
the apply phase. They can be used to output resource attributes. 
 
Example: 
 
output "instance_id" { 
value = aws_instance.example.id 
} 
 
139. How do you manage different environments (e.g., dev, prod) in 
Terraform? 
Different environments can be managed using workspaces or separate directories with different 
variable files and state files. 
 
Example: 
 
terraform workspace new dev 
terraform workspace new prod 
 
140. What is the difference between count and for_each in Terraform? 
count is used to create multiple instances of a resource, while for_each is used to iterate over a 
map or set of values to create multiple instances. 
 
Example (count): 
 
resource "aws_instance" "example" { 
count 
= 3 
ami 
= "ami-0c55b159cbfafe1f0" 
instance_type = "t2.micro" 
} 
Example (for_each): 
 
resource "aws_instance" "example" { 
for_each 
= toset(["instance1", "instance2"]) 
ami 
= "ami-0c55b159cbfafe1f0" 
instance_type = "t2.micro" 
tags = { 
Name = each.key 
} 
} 


***

### Page 38

143. What are Terraform Cloud and Terraform Enterprise? 
Terraform Cloud and Terraform Enterprise are commercial versions of Terraform that provide 
collaboration, governance, and automation features. 
 
Example: 
 
terraform { 
backend "remote" { 
organization = "my-org" 
workspaces { 
name = "my-workspace" 
} 
} 
} 
 
144. How do you use a Terraform backend? 
A backend is configured using the terraform block in the configuration file, specifying the 
backend type and its configuration. 
 
Example: 
 
terraform { 
backend "s3" { 
bucket = "my-terraform-state" 
key 
= "global/s3/terraform.tfstate" 
region = "us-west-2" 
} 
} 
 
145. What is the terraform fmt command used for? 
terraform fmt formats the configuration files to follow the Terraform style guide, making the 
code consistent and readable. 
 
Example: 
 
terraform fmt 
 
146. How do you use a lock file in Terraform? 
A lock file (.terraform.lock.hcl) is used to lock provider versions, ensuring consistency in 
provider versions across different environments. 
 
Example: 
 
terraform init 
 
147. What is the purpose of the terraform workspace command? 


***

### Page 39

The terraform workspace command is used to create, select, and manage multiple 
workspaces, allowing different states to be associated with the same configuration. 
 
Example: 
 
terraform workspace new dev 
terraform workspace select dev 
 
148. How do you manage secrets in Terraform? 
Secrets can be managed using environment variables, secure secret management services (e.g., 
AWS Secrets Manager), or Terraform's sensitive attribute. 
 
Example: 
 
resource "aws_secretsmanager_secret" "example" { 
name 
= "example" 
description = "An example secret" 
} 
 
resource "aws_secretsmanager_secret_version" "example" { 
secret_id 
= aws_secretsmanager_secret.example.id 
secret_string = jsonencode({ 
username = "example_user" 
password = "example_password" 
}) 
} 
 
149. What is the terraform console command used for? 
terraform console opens an interactive console for evaluating expressions, testing 
interpolation syntax, and debugging configurations. 
 
Example: 
 
terraform console 
 
150. How do you reference data sources in Terraform? 
Data sources are referenced using the data block and can be used to fetch information about 
existing infrastructure or services. 
 
Example: 
 
data "aws_ami" "example" { 
most_recent = true 
owners 
= ["amazon"] 
 
filter { 
name 
= "name" 
values = ["amzn-ami-hvm-*"] 
} 
} 


***

### Page 40

resource "aws_instance" "example" { 
ami 
= data.aws_ami.example.id 
instance_type = "t2.micro" 
} 
 
151. What is the purpose of the terraform state mv command? 
terraform state mv moves a resource in the state file to a new address, useful for renaming 
resources without recreating them. 
 
Example: 
 
terraform state mv aws_instance.old_name aws_instance.new_name 
 
152. What is a backend in Terraform? 
A backend in Terraform defines where and how state is loaded and stored. It can be local or 
remote (e.g., S3, Consul, etc.). 
 
Example: 
 
terraform { 
backend "s3" { 
bucket = "my-terraform-state" 
key 
= "global/s3/terraform.tfstate" 
region = "us-west-2" 
} 
} 
 
153. How do you secure the state file in Terraform? 
State files can be secured by storing them in remote backends with proper access controls and 
encryption, such as AWS S3 with server-side encryption and access control policies. 
 
Example: 
 
terraform { 
backend "s3" { 
bucket = "my-terraform-state" 
key 
= "global/s3/terraform.tfstate" 
region = "us-west-2" 
encrypt = true 
} 
} 
 
154. What is the difference between local and remote backends in 
Terraform? 
Local backends store the state file on the local filesystem, while remote backends store the state 
file in a remote storage service (e.g., S3, Consul). 


***

### Page 41

Example (local backend): 
 
terraform { 
backend "local" { 
path = "terraform.tfstate" 
} 
} 
Example (remote backend): 
 
terraform { 
backend "s3" { 
bucket = "my-terraform-state" 
key 
= "global/s3/terraform.tfstate" 
region = "us-west-2" 
} 
} 
 
155. How do you manage module versioning in Terraform? 
Module versioning in Terraform can be managed using the version argument in 
the source attribute of a module block, typically in combination with a registry. 
 
Example: 
 
module "vpc" { 
source = "terraform-aws-modules/vpc/aws" 
version = "2.0.0" 
} 
 
156. What is the Terraform Registry? 
The Terraform Registry is a public repository of Terraform modules and providers that can be 
used to discover and use pre-built modules and providers. 
 
Example: 
 
module "vpc" { 
source = "terraform-aws-modules/vpc/aws" 
version = "2.0.0" 
} 
 
157. How do you generate and view a resource graph in Terraform? 
A resource graph can be generated using the terraform graph command and can be viewed 
using tools like Graphviz. 
 
Example: 
 
terraform graph | dot -Tpng > graph.png 
 
158. What is the purpose of the terraform validate command? 


***

### Page 42

terraform validate is used to validate the syntax and configuration of the Terraform files 
without creating any resources. 
 
Example: 
 
terraform validate 
 
159. What is the terraform fmt command used for? 
terraform fmt formats the configuration files to follow the Terraform style guide, making the 
code consistent and readable. 
 
Example: 
 
terraform fmt 
 
160. What are locals in Terraform and how do you use them? 
Locals in Terraform are used to define local values that can be reused within a module. They help 
avoid repetition and make configurations more readable. 
 
Example: 
 
locals { 
instance_type = "t2.micro" 
ami_id 
= "ami-0c55b159cbfafe1f0" 
} 
 
resource "aws_instance" "example" { 
ami 
= local.ami_id 
instance_type = local.instance_type 
} 
 
161. How do you handle provider dependencies in Terraform? 
Provider dependencies in Terraform are managed using the required_providers block in 
the terraform block, specifying the version constraints. 
 
Example: 
 
terraform { 
required_providers { 
aws = { 
source = "hashicorp/aws" 
version = "~> 3.0" 
} 
} 
} 
 
162. What is the terraform apply command used for? 


***

### Page 43

terraform apply applies the changes required to reach the desired state of the configuration. 
It executes the plan created by terraform plan. 
 
Example: 
 
terraform apply 
 
163. What is the terraform destroy command used for? 
terraform destroy is used to destroy the infrastructure managed by Terraform. It removes all 
the resources defined in the configuration. 
 
Example: 
 
terraform destroy 
 
164. What are output values in Terraform and how are they used? 
Output values are used to extract information from the resources and make it accessible after 
the apply phase. They can be used to output resource attributes. 
 
Example: 
 
output "instance_id" { 
value = aws_instance.example.id 
} 
 
165. How do you manage different environments (e.g., dev, prod) in 
Terraform? 
Different environments can be managed using workspaces or separate directories with different 
variable files and state files. 
 
Example: 
 
terraform workspace new dev 
terraform workspace new prod 
 
166. What is the difference between count and for_each in Terraform? 
count is used to create multiple instances of a resource, while for_each is used to iterate over a 
map or set of values to create multiple instances. 
 
Example (count): 
 
resource "aws_instance" "example" { 
count 
= 3 
ami 
= "ami-0c55b159cbfafe1f0" 
instance_type = "t2.micro" 
} 


***

### Page 44

Example (for_each): 
 
resource "aws_instance" "example" { 
for_each 
= toset(["instance1", "instance2"]) 
ami 
= "ami-0c55b159cbfafe1f0" 
instance_type = "t2.micro" 
tags = { 
Name = each.key 
} 
} 
 
167. How do you use loops in Terraform? 
Loops in Terraform can be implemented using the count and for_each meta-arguments, as 
well as the for expression in variable assignments. 
 
Example: 
 
variable "instance_names" { 
type = list(string) 
default = ["instance1", "instance2"] 
} 
 
resource " 
 
aws_instance" "example" { 
for_each 
= toset(var.instance_names) 
ami 
= "ami-0c55b159cbfafe1f0" 
instance_type = "t2.micro" 
tags = { 
Name = each.key 
} 
} 
 
168. What is a count parameter in Terraform? 
The count parameter in Terraform is used to create multiple instances of a resource based on a 
specified number. 
 
Example: 
 
resource "aws_instance" "example" { 
count 
= 3 
ami 
= "ami-0c55b159cbfafe1f0" 
instance_type = "t2.micro" 
} 
 
169. What are Terraform Cloud and Terraform Enterprise? 
Terraform Cloud and Terraform Enterprise are commercial versions of Terraform that provide 
collaboration, governance, and automation features. 
 
Example: 


***

### Page 45

terraform { 
backend "remote" { 
organization = "my-org" 
workspaces { 
name = "my-workspace" 
} 
} 
} 
 
170. How do you use a Terraform backend? 
A backend is configured using the terraform block in the configuration file, specifying the 
backend type and its configuration. 
 
Example: 
 
terraform { 
backend "s3" { 
bucket = "my-terraform-state" 
key 
= "global/s3/terraform.tfstate" 
region = "us-west-2" 
} 
} 
 
171. What is the terraform fmt command used for? 
terraform fmt formats the configuration files to follow the Terraform style guide, making the 
code consistent and readable. 
 
Example: 
 
terraform fmt 
 
172. How do you use a lock file in Terraform? 
A lock file (.terraform.lock.hcl) is used to lock provider versions, ensuring consistency in 
provider versions across different environments. 
 
Example: 
 
terraform init 
 
173. What is the purpose of the terraform workspace command? 
The terraform workspace command is used to create, select, and manage multiple 
workspaces, allowing different states to be associated with the same configuration. 
 
Example: 
 
terraform workspace new dev 
terraform workspace select dev 


***

### Page 46

174. How do you manage secrets in Terraform? 
Secrets can be managed using environment variables, secure secret management services (e.g., 
AWS Secrets Manager), or Terraform's sensitive attribute. 
 
Example: 
 
resource "aws_secretsmanager_secret" "example" { 
name 
= "example" 
description = "An example secret" 
} 
 
resource "aws_secretsmanager_secret_version" "example" { 
secret_id 
= aws_secretsmanager_secret.example.id 
secret_string = jsonencode({ 
username = "example_user" 
password = "example_password" 
}) 
} 
 
175. What is the terraform console command used for? 
terraform console opens an interactive console for evaluating expressions, testing 
interpolation syntax, and debugging configurations. 
 
Example: 
 
terraform console 
 
176. How do you reference data sources in Terraform? 
Data sources are referenced using the data block and can be used to fetch information about 
existing infrastructure or services. 
 
Example: 
 
data "aws_ami" "example" { 
most_recent = true 
owners 
= ["amazon"] 
 
filter { 
name 
= "name" 
values = ["amzn-ami-hvm-*"] 
} 
} 
 
resource "aws_instance" "example" { 
ami 
= data.aws_ami.example.id 
instance_type = "t2.micro" 
} 
 
177. What is the purpose of the terraform state mv command? 


***

### Page 47

terraform state mv moves a resource in the state file to a new address, useful for renaming 
resources without recreating them. 
 
Example: 
 
terraform state mv aws_instance.old_name aws_instance.new_name 
 
178. What is a backend in Terraform? 
A backend in Terraform defines where and how state is loaded and stored. It can be local or 
remote (e.g., S3, Consul, etc.). 
 
Example: 
 
terraform { 
backend "s3" { 
bucket = "my-terraform-state" 
key 
= "global/s3/terraform.tfstate" 
region = "us-west-2" 
} 
} 
 
179. How do you secure the state file in Terraform? 
State files can be secured by storing them in remote backends with proper access controls and 
encryption, such as AWS S3 with server-side encryption and access control policies. 
 
Example: 
 
terraform { 
backend "s3" { 
bucket = "my-terraform-state" 
key 
= "global/s3/terraform.tfstate" 
region = "us-west-2" 
encrypt = true 
} 
} 
 
180. What is the difference between local and remote backends in 
Terraform? 
Local backends store the state file on the local filesystem, while remote backends store the state 
file in a remote storage service (e.g., S3, Consul). 
 
Example (local backend): 
 
terraform { 
backend "local" { 
path = "terraform.tfstate" 
} 
} 
Example (remote backend): 


***

### Page 48

terraform { 
backend "s3" { 
bucket = "my-terraform-state" 
key 
= "global/s3/terraform.tfstate" 
region = "us-west-2" 
} 
} 
 
181. How do you manage module versioning in Terraform? 
Module versioning in Terraform can be managed using the version argument in 
the source attribute of a module block, typically in combination with a registry. 
 
Example: 
 
module "vpc" { 
source = "terraform-aws-modules/vpc/aws" 
version = "2.0.0" 
} 
 
182. What is the Terraform Registry? 
The Terraform Registry is a public repository of Terraform modules and providers that can be 
used to discover and use pre-built modules and providers. 
 
Example: 
 
module "vpc" { 
source = "terraform-aws-modules/vpc/aws" 
version = "2.0.0" 
} 
 
183. How do you generate and view a resource graph in Terraform? 
A resource graph can be generated using the terraform graph command and can be viewed 
using tools like Graphviz. 
 
Example: 
 
terraform graph | dot -Tpng > graph.png 
 
184. What is the purpose of the terraform validate command? 
terraform validate is used to validate the syntax and configuration of the Terraform files 
without creating any resources. 
 
Example: 
 
terraform validate 
 
185. What is the terraform fmt command used for? 


***

### Page 49

terraform fmt formats the configuration files to follow the Terraform style guide, making the 
code consistent and readable. 
 
Example: 
 
terraform fmt 
 
186. What are locals in Terraform and how do you use them? 
Locals in Terraform are used to define local values that can be reused within a module. They help 
avoid repetition and make configurations more readable. 
 
Example: 
 
locals { 
instance_type = "t2.micro" 
ami_id 
= "ami-0c55b159cbfafe1f0" 
} 
 
resource "aws_instance" "example" { 
ami 
= local.ami_id 
instance_type = local.instance_type 
} 
 
187. How do you handle provider dependencies in Terraform? 
Provider dependencies in Terraform are managed using the required_providers block in 
the terraform block, specifying the version constraints. 
 
Example: 
 
terraform { 
required_providers { 
aws = { 
source = "hashicorp/aws" 
version = "~> 3.0" 
} 
} 
} 
 
188. What is the terraform apply command used for? 
terraform apply applies the changes required to reach the desired state of the configuration. 
It executes the plan created by terraform plan. 
 
Example: 
 
terraform apply 
 
189. What is the terraform destroy command used for? 


***

### Page 50

terraform destroy is used to destroy the infrastructure managed by Terraform. It removes all 
the resources defined in the configuration. 
 
Example: 
 
terraform destroy 
 
190. What are output values in Terraform and how are they used? 
Output values are used to extract information from the resources and make it accessible after 
the apply phase. They can be used to output resource attributes. 
 
Example: 
 
output "instance_id" { 
value = aws_instance.example.id 
} 
 
191. How do you manage different environments (e.g., dev, prod) in 
Terraform? 
Different environments can be managed using workspaces or separate directories with different 
variable files and state files. 
 
Example: 
 
terraform workspace new dev 
terraform workspace new prod 
 
192. What is the difference between count and for_each in Terraform? 
count is used to create multiple instances of a resource, while for_each is used to iterate over a 
map or set of values to create multiple instances. 
 
Example (count): 
 
resource "aws_instance" "example" { 
count 
= 3 
ami 
= "ami-0c55b159cbfafe1f0" 
instance_type = "t2.micro" 
} 
Example (for 
 
_each): 
 
resource "aws_instance" "example" { 
for_each 
= toset(["instance1", "instance2"]) 
ami 
= "ami-0c55b159cbfafe1f0" 
instance_type = "t2.micro" 
tags = { 
Name = each.key 
} 


***

### Page 51

} 
 
193. How do you use loops in Terraform? 
Loops in Terraform can be implemented using the count and for_each meta-arguments, as 
well as the for expression in variable assignments. 
 
Example: 
 
variable "instance_names" { 
type = list(string) 
default = ["instance1", "instance2"] 
} 
 
resource "aws_instance" "example" { 
for_each 
= toset(var.instance_names) 
ami 
= "ami-0c55b159cbfafe1f0" 
instance_type = "t2.micro" 
tags = { 
Name = each.key 
} 
} 
 
194. What is a count parameter in Terraform? 
The count parameter in Terraform is used to create multiple instances of a resource based on a 
specified number. 
 
Example: 
 
resource "aws_instance" "example" { 
count 
= 3 
ami 
= "ami-0c55b159cbfafe1f0" 
instance_type = "t2.micro" 
} 
 
195. What are Terraform Cloud and Terraform Enterprise? 
Terraform Cloud and Terraform Enterprise are commercial versions of Terraform that provide 
collaboration, governance, and automation features. 
 
Example: 
 
terraform { 
backend "remote" { 
organization = "my-org" 
workspaces { 
name = "my-workspace" 
} 
} 
} 
 
196. How do you use a Terraform backend? 


***

### Page 52

A backend is configured using the terraform block in the configuration file, specifying the 
backend type and its configuration. 
 
Example: 
 
terraform { 
backend "s3" { 
bucket = "my-terraform-state" 
key 
= "global/s3/terraform.tfstate" 
region = "us-west-2" 
} 
} 
 
197. What is the terraform fmt command used for? 
terraform fmt formats the configuration files to follow the Terraform style guide, making the 
code consistent and readable. 
 
Example: 
 
terraform fmt 
 
198. How do you use a lock file in Terraform? 
A lock file (.terraform.lock.hcl) is used to lock provider versions, ensuring consistency in 
provider versions across different environments. 
 
Example: 
 
terraform init 
 
199. What is the purpose of the terraform workspace command? 
The terraform workspace command is used to create, select, and manage multiple 
workspaces, allowing different states to be associated with the same configuration. 
 
Example: 
 
terraform workspace new dev 
terraform workspace select dev 
 
200. How do you manage secrets in Terraform? 
Secrets can be managed using environment variables, secure secret management services (e.g., 
AWS Secrets Manager), or Terraform's sensitive attribute. 
 
Example: 
 
resource "aws_secretsmanager_secret" "example" { 
name 
= "example" 
description = "An example secret" 


***

### Page 53

} 
 
resource "aws_secretsmanager_secret_version" "example" { 
secret_id 
= aws_secretsmanager_secret.example.id 
secret_string = jsonencode({ 
username = "example_user" 
password = "example_password" 
}) 
} 


***

### System Design Perspective

**State refactoring strategy for large organizations:**
- The unit of state should match the unit of ownership. If one team owns networking (VPC, subnets, route tables) and another owns compute (EKS, EC2), these should be separate state files. Cross-team output consumption happens via `data "terraform_remote_state"`.
- Migration path: `terraform state mv` moves resources between state files without destroying them. Wrap with `moved {}` blocks to make the rename reviewable in PRs.

**Atlantis as a GitOps control plane:**
- Atlantis runs as a webhook receiver. On PR open → `plan`; on PR comment `atlantis apply` → `apply`. Every plan output is posted as a PR comment — permanent audit trail in your VCS.
- Atlantis uses repo-level locking: only one apply per Terraform root module at a time. This is stronger than DynamoDB locking alone because it prevents even queuing conflicting plans.

**Terraform Enterprise / Cloud at scale:**
- Workspaces map to environments: `payments-prod`, `payments-staging`, `identity-prod`. Team RBAC controls who can `plan` vs. `apply` per workspace.
- Sentinel policy checks run as a pipeline stage: plan → policy check → apply. Hard-mandatory policies cannot be bypassed by any user, including workspace owners.
- Remote execution means no one has provider credentials on their laptop. The TFE runner assumes the role, executes the plan, and the state stays in TFE's encrypted backend.

**Custom providers in practice:**
- Build custom providers for internal platforms (internal service mesh, internal secret store, proprietary provisioning API). The provider becomes the stable API surface — consumers write `resource "internal_service" {}` rather than calling raw APIs.
- Use `terraform-plugin-framework` (newer) over `terraform-plugin-sdk` (legacy). Framework provides a cleaner attribute model and first-class support for plan modifiers and validators.

**Performance at scale:**
- Increase `TF_CLI_ARGS_apply=-parallelism=30` to parallelize resource operations. Stay under provider API rate limits (AWS IAM is the typical bottleneck).
- Use partial configuration + workspace-scoped IAM roles to ensure each team's apply assumes the least-privilege role for their service boundary.

---

## Hard (continued) — Import Blocks, Testing, CDK, and Provider Development

**Q: Explain Terraform's `import` block (1.5+) vs the older `terraform import` CLI command. What does code generation with `terraform plan -generate-config-out` do, and when is it safe to use?**

**A:**

Before Terraform 1.5, importing an existing resource required two steps:
1. `terraform import <address> <provider-id>` — writes state only, no config
2. Manually write the HCL to match the now-imported state, then `terraform plan` to verify zero diff

This was error-prone: the manual HCL step required reading the provider docs to reproduce every attribute, and mistakes caused `terraform plan` to show unexpected changes.

**Import block (Terraform 1.5+):**

```hcl
# import.tf — declarative, version-controlled import
import {
  to = aws_security_group.legacy_app_sg
  id = "sg-0abc123def456"
}

# The resource block must exist (or be generated) alongside the import block
resource "aws_security_group" "legacy_app_sg" {
  name        = "app-sg-legacy"
  description = "Legacy application security group"
  vpc_id      = "vpc-0xyz789"
  
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

Running `terraform plan` with this import block shows:
```
Plan: 1 to import, 0 to add, 0 to change, 0 to destroy.
```

Running `terraform apply` imports the resource into state. The `import` block is then removed from the code (or left in — it's idempotent; subsequent plans show 0 changes if state matches).

**Advantages over `terraform import` CLI:**
- Version-controlled: the import intent lives in `.tf` files, not someone's terminal history
- Reviewable via PR: the import block + resource block are reviewed together
- Plannable: `terraform plan` shows a preview before any state change — `terraform import` CLI wrote to state immediately with no plan preview

**Code generation with `-generate-config-out`:**

```bash
# Write import block (but don't write the resource block)
cat >> import.tf <<'EOF'
import {
  to = aws_s3_bucket.data_lake
  id = "my-company-data-lake-prod"
}
EOF

# Generate HCL for the resource block
terraform plan -generate-config-out=generated.tf
```

Terraform reads the existing resource from the provider API and synthesizes HCL in `generated.tf`:

```hcl
# generated.tf — auto-generated, review before committing
resource "aws_s3_bucket" "data_lake" {
  bucket        = "my-company-data-lake-prod"
  force_destroy = false
  tags = {
    Environment = "production"
    Team        = "data-platform"
  }
}
```

**Safety caveats for generated code:**
- Generated HCL includes every attribute at its current value, including computed attributes (like `arn`, `hosted_zone_id`) that Terraform normally doesn't need in config (it reads them from state). These must be removed or plan will show perpetual diff.
- Sensitive attributes (passwords, keys) are omitted with `(sensitive)` placeholder — you must add them manually or via variable references.
- Always `terraform plan` after editing `generated.tf` and verify zero diff before committing.
- Generated code is a starting point, not production-ready HCL. Review every attribute: remove computed ones, extract magic strings to variables, apply naming conventions.

**Bulk import workflow (importing 50 existing S3 buckets):**

```hcl
# Use for_each in import block (Terraform 1.7+)
locals {
  existing_buckets = {
    data-lake     = "my-company-data-lake-prod"
    ml-artifacts  = "my-company-ml-artifacts"
    audit-logs    = "my-company-audit-logs-2023"
  }
}

import {
  for_each = local.existing_buckets
  to       = aws_s3_bucket.existing[each.key]
  id       = each.value
}

resource "aws_s3_bucket" "existing" {
  for_each = local.existing_buckets
  bucket   = each.value
}
```

---

**Q: Explain Terraform's `terraform test` framework (1.6+). How does it differ from Terratest? Write a test for a module that creates an S3 bucket with required tags.**

**A:**

Terraform 1.6 introduced a native testing framework using `.tftest.hcl` files. Unlike Terratest (Go-based, external), `terraform test` is built into the CLI, uses HCL syntax, and can test modules without writing Go.

**Module under test: `modules/s3-bucket/main.tf`:**

```hcl
variable "bucket_name" { type = string }
variable "environment" { type = string }
variable "team"        { type = string }

resource "aws_s3_bucket" "this" {
  bucket = var.bucket_name
  tags = {
    Environment = var.environment
    Team        = var.team
    ManagedBy   = "terraform"
  }
}

resource "aws_s3_bucket_versioning" "this" {
  bucket = aws_s3_bucket.this.id
  versioning_configuration {
    status = "Enabled"
  }
}

output "bucket_id"  { value = aws_s3_bucket.this.id }
output "bucket_arn" { value = aws_s3_bucket.this.arn }
```

**Test file: `modules/s3-bucket/s3_bucket.tftest.hcl`:**

```hcl
# Provider configuration for tests
provider "aws" {
  region = "us-east-1"
  # Tests should use a dedicated test account or localstack
}

# Test 1: verify bucket creation and tags
run "creates_bucket_with_required_tags" {
  variables {
    bucket_name = "test-bucket-${run.creates_bucket_with_required_tags.timestamp}"
    environment = "test"
    team        = "platform"
  }

  # Assert on plan output (no actual AWS resources created)
  command = plan   # or "apply" for full integration test

  assert {
    condition     = aws_s3_bucket.this.tags["Environment"] == "test"
    error_message = "Environment tag must be set"
  }

  assert {
    condition     = aws_s3_bucket.this.tags["Team"] == "platform"
    error_message = "Team tag must be set"
  }

  assert {
    condition     = aws_s3_bucket.this.tags["ManagedBy"] == "terraform"
    error_message = "ManagedBy tag must be 'terraform'"
  }
}

# Test 2: verify versioning is enabled (requires apply to read status)
run "versioning_enabled" {
  variables {
    bucket_name = "test-versioned-bucket-unique-123"
    environment = "test"
    team        = "data"
  }

  command = apply   # creates real resources; Terraform destroys after test

  assert {
    condition     = aws_s3_bucket_versioning.this.versioning_configuration[0].status == "Enabled"
    error_message = "Versioning must be Enabled"
  }

  assert {
    condition     = output.bucket_arn != ""
    error_message = "bucket_arn output must be set"
  }
}

# Test 3: invalid input validation
run "rejects_empty_team_tag" {
  variables {
    bucket_name = "test-empty-team"
    environment = "test"
    team        = ""           # should fail validation
  }

  command = plan

  expect_failures = [
    var.team,   # expect this variable validation to fail
  ]
}
```

**Run the tests:**

```bash
# Run all tests in the module directory
terraform test

# Run specific test file
terraform test -filter=s3_bucket.tftest.hcl

# Run with verbose output
terraform test -verbose

# Run only plan-mode tests (no AWS resources created)
terraform test -filter=creates_bucket_with_required_tags
```

**`terraform test` vs Terratest:**

| Factor | `terraform test` | Terratest |
|--------|------------------|-----------|
| Language | HCL | Go |
| Setup overhead | Zero (built into CLI) | Go module + AWS SDK |
| Real resource testing | Yes (`command = apply`) | Yes |
| Plan-only assertions | Yes (`command = plan`) | No (requires apply) |
| Parallelism | Per-file parallel | Configurable with `t.Parallel()` |
| Custom logic | Limited (HCL expressions) | Full Go: HTTP checks, retries, regex |
| CI integration | `terraform test` in any CI | `go test -timeout 30m ./...` |
| **Best for** | Module validation, tag policies | Complex integration tests with external checks |

**Key difference:** `terraform test` with `command = plan` never creates real infrastructure — it validates the generated plan. `command = apply` creates real resources and destroys them after the test block. Use plan-mode for unit tests (fast, free), apply-mode for integration tests (slow, costs money).

**localstack for free integration tests:**

```hcl
provider "aws" {
  region                      = "us-east-1"
  access_key                  = "test"
  secret_key                  = "test"
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  endpoints {
    s3 = "http://localhost:4566"
  }
}
```

---

**Q: Explain Terraform's `moved` block. When would you use it at scale? What happens if you rename a resource without one?**

**A:**

The `moved` block records that a resource has been renamed or moved within the configuration, without destroying and recreating the infrastructure. Terraform updates state to reflect the new address, then continues managing the resource normally.

**Without `moved` block — destructive refactor:**

```hcl
# Before refactor
resource "aws_instance" "app" { ... }

# After rename (WRONG: Terraform plans destroy + create)
resource "aws_instance" "application_server" { ... }
```

```
Plan: 1 to add, 0 to change, 1 to destroy.
```

A production EC2 instance is destroyed and a new one created — downtime, data loss risk.

**With `moved` block — non-destructive refactor:**

```hcl
# main.tf: resource renamed
resource "aws_instance" "application_server" { ... }

# moved.tf: record the rename
moved {
  from = aws_instance.app
  to   = aws_instance.application_server
}
```

```
Plan: 0 to add, 0 to change, 0 to destroy.
  # aws_instance.app has moved to aws_instance.application_server
```

Terraform updates the state file's address from `aws_instance.app` to `aws_instance.application_server`. No API call to AWS; no infrastructure change.

**Moved block for for_each refactors:**

Most impactful use case — converting a single resource to `for_each`:

```hcl
# Before: three separate resource blocks
resource "aws_s3_bucket" "logs"     { bucket = "company-logs" }
resource "aws_s3_bucket" "backups"  { bucket = "company-backups" }
resource "aws_s3_bucket" "artifacts"{ bucket = "company-artifacts" }

# After: for_each
resource "aws_s3_bucket" "this" {
  for_each = toset(["logs", "backups", "artifacts"])
  bucket   = "company-${each.key}"
}

# moved.tf
moved {
  from = aws_s3_bucket.logs
  to   = aws_s3_bucket.this["logs"]
}
moved {
  from = aws_s3_bucket.backups
  to   = aws_s3_bucket.this["backups"]
}
moved {
  from = aws_s3_bucket.artifacts
  to   = aws_s3_bucket.this["artifacts"]
}
```

Without these `moved` blocks, all three buckets would be destroyed and three new ones created.

**Moved block in modules (module refactoring):**

```hcl
# Before: inline resource
resource "aws_security_group" "app" { ... }

# After: moved into a module
module "app_sg" {
  source = "./modules/security-group"
  ...
}

# moved.tf
moved {
  from = aws_security_group.app
  to   = module.app_sg.aws_security_group.this
}
```

**Scale considerations:**

At scale (500+ resources per workspace), `moved` blocks accumulate. After all teams have applied:
1. Old addresses are gone from state — the `moved` block is now a no-op
2. `moved` blocks can be safely deleted in the next release
3. **Never delete a `moved` block before all workspaces have applied** — a workspace that hasn't applied yet still has the old address and will plan a destroy without the `moved` block

Document `moved` block lifecycle in your team's Terraform conventions:
```
1. PR adds moved block + rename
2. All workspaces apply (verified via Terraform Cloud run history)
3. Cleanup PR removes the moved block
```

---

**Q: What is CDK for Terraform (CDKTF)? When would you choose it over HCL? Walk through a CDKTF stack in TypeScript.**

**A:**

CDKTF (CDK for Terraform) lets you define Terraform infrastructure in general-purpose languages (TypeScript, Python, Go, Java, C#) instead of HCL. It synthesizes HCL-compatible JSON that Terraform executes.

**When to choose CDKTF over HCL:**

| Choose CDKTF | Choose HCL |
|--------------|------------|
| Dynamic infrastructure: N identical stacks with programmatic variation | Static infrastructure: predictable, declarative config |
| Complex conditional logic: if/else, loops, map/filter on infrastructure | Simple `count` / `for_each` is enough |
| Type safety matters: IDE autocomplete, compile-time errors | Team is already fluent in HCL |
| Reuse via programming language constructs (classes, inheritance) | Module composition is sufficient |
| Integration with app code (read build artifacts, app config) | Clear separation of app and infra |

**CDKTF stack in TypeScript:**

```bash
# Initialize
cdktf init --template=typescript --providers=aws
npm install @cdktf/provider-aws
```

```typescript
// main.ts
import { App, TerraformStack, TerraformOutput } from "cdktf";
import { AwsProvider } from "@cdktf/provider-aws/lib/provider";
import { S3Bucket } from "@cdktf/provider-aws/lib/s3-bucket";
import { S3BucketVersioningA } from "@cdktf/provider-aws/lib/s3-bucket-versioning";

interface MicroserviceBucketConfig {
  serviceName: string;
  environment: string;
  region: string;
}

// Reusable construct: encapsulates a versioned S3 bucket per service
class MicroserviceBucket extends Construct {
  public readonly bucket: S3Bucket;

  constructor(scope: Construct, id: string, config: MicroserviceBucketConfig) {
    super(scope, id);

    this.bucket = new S3Bucket(this, "bucket", {
      bucket: `${config.serviceName}-${config.environment}-artifacts`,
      tags: {
        Service:     config.serviceName,
        Environment: config.environment,
        ManagedBy:   "cdktf",
      },
    });

    new S3BucketVersioningA(this, "versioning", {
      bucket: this.bucket.id,
      versioningConfiguration: { status: "Enabled" },
    });
  }
}

// Stack: creates buckets for all microservices
class InfraStack extends TerraformStack {
  constructor(scope: App, id: string, environment: string) {
    super(scope, id);

    new AwsProvider(this, "aws", { region: "us-east-1" });

    const services = ["auth", "payments", "orders", "notifications"];

    services.forEach((service) => {
      const svcBucket = new MicroserviceBucket(this, `${service}-bucket`, {
        serviceName: service,
        environment,
        region: "us-east-1",
      });

      new TerraformOutput(this, `${service}-bucket-arn`, {
        value: svcBucket.bucket.arn,
      });
    });
  }
}

// Create stacks per environment
const app = new App();
new InfraStack(app, "infra-staging",    "staging");
new InfraStack(app, "infra-production", "production");
app.synth();
```

**Commands:**

```bash
# Synthesize HCL JSON (review before deploying)
cdktf synth

# Plan
cdktf plan infra-production

# Apply
cdktf deploy infra-production

# Destroy
cdktf destroy infra-staging
```

**Output:** `cdktf.out/stacks/infra-production/cdk.tf.json` — valid Terraform JSON that `terraform apply` can consume directly.

**Key tradeoff:** CDKTF adds a synthesis step, a Node.js/language runtime dependency, and debugging complexity (errors occur in both TypeScript and Terraform layers). For straightforward infrastructure, HCL modules are simpler to read, review, and operate. CDKTF pays off when the infrastructure is genuinely data-driven or when developer ergonomics (type safety, IDE support, unit tests in Jest/pytest) outweigh the added complexity.

