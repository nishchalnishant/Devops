# Infrastructure as Code (Terraform)

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
| `interview-easy.md` | Foundational: plan/apply, state, variables, outputs |
| `interview-medium.md` | Intermediate: modules, remote state, workspaces, import |
| `interview-hard.md` | Advanced: Terragrunt, Atlantis, module versioning, drift |
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
