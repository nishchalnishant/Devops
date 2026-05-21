---
description: Terraform remote backends, state locking, state operations, and disaster recovery patterns.
---

# Terraform — Backends, State & Disaster Recovery

```
Terraform State & Backends
├── What is State?
│   ├── JSON file mapping .tf resource blocks → real-world objects
│   ├── Stores: resource type, name, provider, attribute snapshot
│   ├── serial number incremented on every write
│   └── Without state: every plan looks like "create everything"
├── Backend Types
│   ├── local (default)     → single-user, not team-safe
│   ├── s3 + dynamodb       → AWS standard; versioned + locked
│   ├── azurerm             → Azure Blob with native locking
│   ├── gcs                 → Google Cloud Storage
│   └── terraform cloud     → managed state + remote execution
├── S3 + DynamoDB Backend
│   ├── bucket: stores state file (enable versioning + KMS encryption)
│   ├── dynamodb_table: stores lock record (LockID as hash key)
│   ├── Locking: conditional PutItem → fails if lock exists
│   └── Unlock: terraform force-unlock <LOCK_ID>
├── State Operations
│   ├── state list    → list all resource addresses
│   ├── state show    → show attributes of one resource
│   ├── state mv      → rename resource (prefer moved {} block)
│   ├── state rm      → remove from state without deleting real resource
│   ├── state pull    → dump state JSON to stdout
│   └── state push    → upload local state to remote (dangerous)
├── Drift Detection
│   ├── plan -refresh-only → show divergence, propose no resource changes
│   └── apply -refresh-only → sync state with reality, no infra changes
├── Disaster Recovery
│   ├── S3 versioning → restore previous state version
│   ├── state push → restore from backup after corruption
│   └── terraform import → re-adopt resources orphaned from state
├── Sensitive Values in State
│   ├── sensitive = true → hides from CLI output only
│   ├── State stores value in plaintext JSON regardless
│   └── Mitigation: KMS-encrypted S3, least-privilege IAM on state bucket
└── Logic & Trickiness
    ├── Backend config cannot use variables (literals or -backend-config flags)
    ├── terraform refresh deprecated (use plan -refresh-only)
    ├── state push with wrong state = silent data loss
    └── Deleting DynamoDB lock record = potential concurrent write corruption
```

## First Principles

- State is Terraform's source of truth about what it manages. It is not a backup of cloud configuration — it is a mapping from HCL resource addresses to cloud resource IDs and their last-known attribute values.
- Locking is a mutual exclusion mechanism. DynamoDB's `ConditionExpression` on `PutItem` ensures only one process holds the lock at a time. This is the same pattern as a database row lock, applied to a JSON file.
- `sensitive = true` is a display filter. It tells the CLI not to print the value. It does not affect what is written to the state file. Security of sensitive values requires access control on the state backend, not the `sensitive` attribute.
- `plan -refresh-only` separates "what changed outside Terraform" from "what does my code want to change." Running them together (`plan`) conflates drift correction with intentional changes, making plans harder to review.
- S3 versioning is free disaster recovery for state. A corrupt or accidentally-pushed state can be recovered by downloading the previous S3 object version and pushing it back.

## What is Terraform State?

Terraform state is a JSON mapping between your `.tf` resource blocks and the real-world infrastructure objects they represent. Without state, Terraform cannot know what already exists.

```json
{
  "version": 4,
  "terraform_version": "1.7.0",
  "resources": [
    {
      "mode": "managed",
      "type": "aws_instance",
      "name": "web",
      "instances": [{
        "attributes": {
          "id": "i-0a1b2c3d4e5f6g7h8",
          "ami": "ami-0abcdef1234567890",
          "instance_type": "t3.micro",
          "public_ip": "54.32.10.1"
        }
      }]
    }
  ]
}
```

***

## S3 Remote Backend with DynamoDB Locking

```hcl
terraform {
  backend "s3" {
    bucket         = "my-company-terraform-state"
    key            = "production/eks/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true       # Encrypt state at rest with SSE-S3
    kms_key_id     = "arn:aws:kms:..."  # Use KMS for stronger encryption
    
    # State locking — prevents concurrent applies
    dynamodb_table = "terraform-state-lock"
    
    # Required for versioning / rollback
    # Enable versioning on the S3 bucket separately
  }
}
```

**DynamoDB table requirements:**
- Partition key: `LockID` (String)
- No sort key needed
- On-demand billing class is fine (low write volume)

### How Locking Works

```
Engineer A: terraform apply
    ├── Writes lock item to DynamoDB {LockID: "state-key", Info: "..."}
    └── Proceeds with apply

Engineer B: terraform apply (concurrent)
    ├── Tries to write lock item → DynamoDB conditional put fails (item exists)
    └── Error: "Error acquiring the state lock"
         Info: "ID: xxx, Who: engineer-a@company.com, Created: ..."
         
Engineer A completes:
    └── Deletes lock item from DynamoDB
```

***

## State Operations — The Dangerous Commands

### `terraform state list` — Safe
```bash
terraform state list
# aws_instance.web
# aws_security_group.web
# module.vpc.aws_vpc.main
```

### `terraform state show` — Safe
```bash
terraform state show aws_instance.web
# Shows all attributes of the resource in state
```

### `terraform state mv` — Risky (rename resources without destroy)
```bash
# Rename a resource without destroying it
terraform state mv aws_instance.web aws_instance.web_server
# Use case: code refactoring, moving to modules
```

### `terraform state rm` — Dangerous (orphan resource)
```bash
# Remove from state WITHOUT destroying the resource
terraform state rm aws_instance.web
# The real instance still exists in AWS, but Terraform forgets it
# Use case: handing off a resource to another team/state
```

### `terraform import` — Adopt existing resources
```bash
# Bring an existing resource under Terraform management
terraform import aws_instance.web i-0a1b2c3d4e5f6g7h8

# Then run plan to verify no unintended changes
terraform plan
```

***

## State Drift & `terraform refresh`

```bash
# Detect drift (someone manually changed something in AWS)
terraform plan -refresh-only      # Just show drift, no changes

# Apply the drift detection (update state to match reality)
terraform apply -refresh-only     # Updates state but NOT your infrastructure
                                  # Next apply will reconcile both
```

***

## Disaster Recovery — Broken State

### Scenario: State file is corrupted or accidentally deleted

```bash
# 1. Enable S3 versioning (always do this!)
# Restore previous state version from S3 console

# 2. If state is lost entirely, rebuild with import
terraform import aws_instance.web i-0a1b2c3d4e5f6g7h8
terraform import aws_security_group.web sg-0a1b2c3d4e5

# 3. Verify
terraform plan   # Should show no changes if import was complete
```

### Scenario: Stuck lock (engineer killed terminal mid-apply)

```bash
# Find lock ID from error message or DynamoDB console
terraform force-unlock "LOCK_ID"

# Only do this if you are CERTAIN no apply is running
# Running force-unlock during an active apply = state corruption
```

***

## Sensitive Values in State

State is stored as **plaintext JSON** by default. Any `sensitive = true` value in your provider still ends up in state.

```hcl
resource "aws_db_instance" "main" {
  password = var.db_password   # This WILL be in state in plaintext
}
```

**Mitigations:**
1. **Encrypt the backend** (S3 SSE + KMS)
2. **Restrict access** to the S3 bucket with IAM
3. **Never store state locally** in CI — always use remote backend
4. **Use Vault** or AWS Secrets Manager to inject secrets at apply time, not store them in `.tf` files

***

## Logic & Trickiness Table

| Operation | Risk Level | When to Use |
|:---|:---|:---|
| `terraform state list` | Safe | Any time |
| `terraform state show` | Safe | Inspecting drift |
| `terraform state mv` | Medium | Code refactoring |
| `terraform state rm` | High | Orphaning resources intentionally |
| `terraform import` | Medium | Adopting unmanaged resources |
| `terraform force-unlock` | Very High | Only after confirming no active apply |
| `-refresh-only` | Safe | Drift detection before apply |

***

## System Design Perspective

**State backend selection by organization size:**
- Solo developer / small team: S3 + DynamoDB is sufficient and cheap. Versioning gives recovery. IAM gives access control.
- Medium organization (10-50 engineers): Terraform Cloud free tier or S3 with per-team state paths. Workspace-level RBAC using IAM conditions on the S3 key prefix (`infra/team-payments/*`).
- Large organization (100+ engineers): Terraform Enterprise or Terraform Cloud Business. Audit logging, Sentinel policies, private module registry, SSO, and agent pools for air-gapped environments.

**State splitting strategy:**
- One state file per independently deployable service boundary. Networking team: `network/vpc/terraform.tfstate`. Platform team: `platform/eks/terraform.tfstate`. Application team: `services/payments/terraform.tfstate`.
- Cross-state references via `data "terraform_remote_state"`: the EKS state consumes VPC outputs from the network state. This creates a directed dependency graph between state files — it is not circular.
- When a state file grows past ~1000 resources, plan times increase significantly. Split by extracting self-contained resource groups (IAM roles, S3 buckets, monitoring rules) into their own state files.

**Disaster recovery runbook:**
1. Identify corrupt or missing state: `terraform plan` shows all resources as "to create" when state is empty.
2. Recover from S3 version: `aws s3api list-object-versions --bucket my-tf-state --prefix path/to/terraform.tfstate` → download the last good version.
3. Validate recovered state: `terraform show terraform.tfstate` → check it references known resources.
4. Push recovered state: `terraform state push terraform.tfstate`.
5. Run `terraform plan -refresh-only` to confirm state matches reality before running any apply.
