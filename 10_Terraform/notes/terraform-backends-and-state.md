---
description: Terraform remote backends, state locking, state operations, and disaster recovery patterns.
---

# Terraform — Backends, State & Disaster Recovery

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
