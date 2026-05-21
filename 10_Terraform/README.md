# Infrastructure as Code (Terraform)

```
Terraform IaC
├── Core Philosophy
│   ├── Declare desired state in HCL (.tf files)
│   ├── Plan: compute diff between desired and actual
│   ├── Apply: make reality match desired state
│   └── State: JSON mapping of resource → real object
├── Core Workflow
│   ├── terraform init   → download providers, set up backend
│   ├── terraform plan   → show what will change (no write)
│   ├── terraform apply  → execute changes
│   └── terraform destroy → tear down managed resources
├── Key Concepts
│   ├── Provider       → plugin that calls cloud API (AWS, Azure, GCP)
│   ├── Resource       → infrastructure object managed by Terraform
│   ├── Data Source    → read-only reference to existing resource
│   ├── Module         → reusable, parameterized group of resources
│   ├── Variable       → input to a module or root config
│   ├── Output         → value exported from a module
│   ├── Local          → computed expression for readability
│   └── Backend        → where state is stored (local, S3, Azure Blob)
├── State Management
│   ├── Remote backend  → S3+DynamoDB, Azure Blob, GCS, Terraform Cloud
│   ├── State locking   → DynamoDB prevents concurrent apply
│   ├── State commands  → list, show, mv, rm, pull, push
│   └── Drift detection → plan -refresh-only
├── Interview Focus Areas
│   ├── Easy   → init/plan/apply, providers, modules, data sources, workspaces
│   ├── Medium → remote backend, for_each vs count, moved block, Terragrunt, testing
│   └── Hard   → state refactoring, large-scale multi-team, custom providers, Sentinel
├── Common Production Mistakes
│   ├── count + list reordering → cascading destroy (use for_each)
│   ├── sensitive output still in state plaintext
│   ├── depends_on on module → forces full sequential plan
│   ├── terraform apply without saved plan (re-plans)
│   └── workspace ≠ environment isolation
└── Alternatives
    ├── Pulumi     → same model but general-purpose languages (Python, Go, TS)
    ├── CDK/CDK-TF → AWS-native or Terraform-backed imperative IaC
    └── Ansible    → configuration management (complementary, not competing)
```

## First Principles

- Infrastructure has **state** — Terraform must know which real object corresponds to which resource block. Without state, every plan looks like "create everything."
- Click-ops is not reproducible. Declaring desired state in version-controlled HCL makes infra auditable and reviewable as code.
- The plan/apply split creates a **review gate**: you see the diff before any change reaches production.
- State must live in a **central, locked store** (S3+DynamoDB) so concurrent runs don't corrupt it. Local state only works for solo developers.
- Modules prevent copy-paste HCL. A `module "vpc"` call is a typed, versioned API contract — changing it triggers a plan diff, not silent drift.
- Providers speak gRPC to the Terraform Core. Any cloud with an API can have a provider — Terraform is not AWS-specific.

Terraform is the industry-standard IaC tool for provisioning and managing cloud infrastructure declaratively across any provider. This module covers Terraform from fundamentals to advanced enterprise patterns.

***

## What Is in This Module

| File | Purpose |
|:---|:---|
| `notes/terraform-core.md` | State management, providers, workspaces, backends |
| `notes/terraform-advanced.md` | Modules, meta-arguments, dynamic blocks, functions |
| `notes/terraform-ci-cd.md` | Atlantis, Terragrunt, CI/CD patterns, Infracost |
| `cheatsheet.md` | HCL syntax, CLI commands, resource patterns, expressions |
| `tips-and-tricks.md` | Production gotchas: `for_each` vs `count`, state, security, debugging |
| `interview.md` | Consolidated Interview Questions: Easy, Medium, and Hard levels |
| `scenarios.md` | Real-world troubleshooting and architectural scenarios |

***

## The Core Workflow

```
1. Write   →  Define desired state in .tf files using HCL
2. Init    →  terraform init   (downloads providers, configures backend)
3. Plan    →  terraform plan   (shows diff: current vs desired state)
4. Apply   →  terraform apply  (creates/modifies/deletes resources)
5. Destroy →  terraform destroy (cleans up all managed resources)
```

**The #1 rule:** Always review `plan` output before `apply`. In CI/CD: `plan -out=plan.tfplan` → save plan artifact → `apply plan.tfplan` (never re-plan on apply).

***

## Key Concepts Reference

| Concept | Purpose | Example |
|:---|:---|:---|
| **Provider** | Plugin to communicate with an API | `provider "aws" { region = "us-east-1" }` |
| **Resource** | Infrastructure object to manage | `resource "aws_vpc" "main" { ... }` |
| **Data Source** | Read-only query of existing infra | `data "aws_ami" "latest" { ... }` |
| **Variable** | Input to a module or configuration | `variable "environment" { type = string }` |
| **Output** | Exported value from a module | `output "vpc_id" { value = aws_vpc.main.id }` |
| **Local** | Computed expression within a module | `locals { full_name = "${var.project}-${var.env}" }` |
| **Module** | Reusable group of resources | `module "vpc" { source = "./modules/vpc" }` |
| **State** | Record of managed resources | `terraform.tfstate` (always use remote!) |
| **Backend** | Where state is stored | S3 + DynamoDB (AWS), GCS (GCP) |
| **Workspace** | Separate state per environment | `terraform workspace select staging` |

***

## Interview Focus Areas

| Difficulty | Key Topics |
|:---|:---|
| **Easy** | Plan/apply/destroy lifecycle, state purpose, variables vs locals vs outputs, backend |
| **Medium** | Remote state + locking, modules, `for_each` vs `count`, `depends_on`, data sources |
| **Hard** | Terragrunt DRY patterns, Atlantis PR-based workflow, module versioning strategy, `moved` block, drift detection, `check` blocks |

***

## Most Common Production Mistakes

```hcl
# 1. count vs for_each — ALWAYS use for_each for collections
# count: removing "alice" from the middle shifts indices → bob gets deleted and recreated
# for_each: removing "alice" only affects alice's resource

# 2. Sensitive outputs still in state
output "db_password" { sensitive = true }  # Hidden from CLI, NOT from state file
# → Encrypt state at rest with S3 + KMS

# 3. Mutable module version refs in production
module "vpc" { source = "terraform-aws-modules/vpc/aws" version = "~> 5.0" }
# → Use exact version: version = "5.5.2"

# 4. terraform apply without -out in CI
# Re-planning on apply means the approved plan may differ from what actually runs
# → Always: plan -out=plan.tfplan && apply plan.tfplan
```

***

## Terraform vs Alternatives

| Tool | Paradigm | Best For |
|:---|:---|:---|
| **Terraform** | Declarative HCL, provider ecosystem | Multi-cloud, team IaC, established pattern |
| **OpenTofu** | Open-source Terraform fork (post-BSL) | When avoiding HashiCorp license |
| **Pulumi** | Declarative using real languages (Python, Go, TS) | Developer-heavy teams; testing IaC with unit tests |
| **AWS CDK** | Imperative using code → CloudFormation | AWS-only shops with heavy development background |
| **Crossplane** | Kubernetes CRDs for cloud resources | K8s-native self-service infrastructure |
| **Ansible** | Procedural, agentless | Config management inside servers (complementary to TF) |

***

## System Design Perspective

**State storage trade-offs:**
- S3 + DynamoDB: most common for AWS. S3 versioning gives free state history. DynamoDB provides conditional-write locking (one writer at a time). KMS encrypts state at rest.
- Terraform Cloud/Enterprise: managed state + locking + RBAC + audit log + Sentinel policy as code. Higher cost but zero ops overhead.
- Azure Blob + native locking: equivalent to S3+DynamoDB for Azure workloads.

**Workspace vs. directory layout:**
- Workspaces share backend config and all code — easy to drift silently between environments. Only appropriate for truly identical environments (e.g., feature-branch infra with identical topology).
- Separate state paths per environment (directory or Terragrunt approach) gives hard isolation: a broken prod state cannot affect staging.

**At scale (50+ engineers, 100+ modules):**
- Atlantis: GitOps for Terraform. PR triggers `plan`, merge triggers `apply`. Audit log lives in PR comments. No shared CLI credentials.
- Terraform Cloud/Enterprise: VCS integration, remote execution, cost estimation, Sentinel policies, team-level RBAC on workspaces.
- State splitting: one state file per service boundary (VPC, EKS, RDS) rather than one monolith. Smaller state = faster plans, smaller blast radius.
- Remote state data source: `data "terraform_remote_state"` allows the EKS module to consume VPC outputs without being in the same state file — loose coupling between teams.

**Security at scale:**
- Never store secrets in tfvars. Fetch from SSM Parameter Store or HashiCorp Vault at runtime using data sources.
- OIDC-based authentication in CI (GitHub Actions → AWS) eliminates long-lived access keys entirely.
- `prevent_destroy` + branch protection + required Sentinel policy creates defense in depth against accidental deletion of production databases.