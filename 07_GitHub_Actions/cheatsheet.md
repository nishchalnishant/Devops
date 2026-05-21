# GitHub Actions Cheatsheet

```
GitHub Actions Cheatsheet
├── Workflow Structure
│   ├── name, on:, permissions:, jobs:
│   └── Skeleton: push+pull_request triggers, contents:read, runs-on, steps
├── Trigger Events
│   ├── push / pull_request / pull_request_target / schedule
│   ├── workflow_dispatch (manual) / workflow_call (reusable)
│   ├── release / repository_dispatch / workflow_run
│   └── filters — branches, paths, types
├── Contexts & Expressions
│   ├── github.sha / github.ref / github.ref_name / github.event_name
│   ├── github.repository / github.actor / github.run_id / github.run_number
│   ├── env.MY_VAR / secrets.MY_SECRET / vars.MY_VAR (non-secret)
│   ├── needs.job-id.outputs.key / matrix.os / runner.os
│   └── Functions: format, join, toJSON, fromJSON, hashFiles, contains, startsWith
├── Common Patterns
│   ├── OIDC to ECR — configure-aws-credentials + ecr-login + docker build/push
│   ├── Cache npm — setup-node with cache: 'npm'
│   ├── Artifacts — upload-artifact / download-artifact, retention-days
│   ├── Matrix — python-version × os, fail-fast: false
│   ├── Manual approval — environment: production (required reviewers)
│   ├── Conditional steps — if: github.ref, failure(), always()
│   ├── Pass data — echo "key=val" >> $GITHUB_OUTPUT / $GITHUB_ENV
│   ├── Reusable workflow call — uses: myorg/workflows/.github/workflows/deploy.yml@main
│   └── Self-hosted runner — runs-on: [self-hosted, linux, x64, gpu]
├── Permissions Reference
│   ├── contents / actions / checks / deployments / id-token / issues
│   ├── packages / pull-requests / security-events / statuses
│   └── Pattern: read-all at workflow, minimal per job
├── OIDC Keyless Auth
│   ├── AWS — configure-aws-credentials with role-to-assume
│   ├── Azure — azure/login with client-id, tenant-id, subscription-id
│   └── GCP — google-github-actions/auth with workload_identity_provider
├── Concurrency
│   ├── group: ${{ github.workflow }}-${{ github.ref }}
│   └── cancel-in-progress: true (PRs) / false (production deploys)
├── Composite Action
│   ├── .github/actions/*/action.yml
│   ├── using: composite, inputs:, steps: (shell: bash required)
│   └── Usage: uses: ./.github/actions/setup-app
├── Debugging
│   ├── ACTIONS_STEP_DEBUG=true / ACTIONS_RUNNER_DEBUG=true (repo secrets)
│   ├── toJSON(github) — print all context
│   └── action-tmate — SSH into runner on failure
├── GitHub CLI in Workflows
│   ├── GH_TOKEN: ${{ github.token }}
│   ├── gh pr comment / gh release create / gh pr view
│   └── gh workflow run / gh run download
├── Security Hardening
│   ├── SHA pinning — actions/checkout@<sha>  # v4.x.x
│   ├── Minimal permissions per job
│   ├── env var injection — never ${{ ... }} in run: directly
│   └── zizmor — static analyzer for GHA (pip install zizmor)
└── Gotchas
    ├── set-output deprecated → $GITHUB_OUTPUT
    ├── Secrets not in forks (pull_request)
    ├── GITHUB_TOKEN expires after job
    ├── pull_request_target + checkout = script injection risk
    └── fail-fast: true default — set false to see all matrix results
```

## First Principles

- Contexts (`${{ github.* }}`) are the runtime data layer. Everything about the triggering event, runner, secrets, and job outputs is accessible via contexts. Understanding which context holds what data is the difference between working and broken expressions.
- OIDC (id-token: write) exists to eliminate the worst class of secret: static cloud credentials. A short-lived JWT proves "this is GitHub Actions job from repo X, branch Y" to the cloud provider's IAM. No secret to store, rotate, or leak.
- `$GITHUB_OUTPUT` (not `set-output`) is the standard for passing data between steps. `$GITHUB_ENV` is for setting env vars available to all subsequent steps. These are append-only files — each step writes, later steps read.
- `concurrency` is a correctness control, not just efficiency. Two deploys running simultaneously can corrupt state. `cancel-in-progress: true` for PRs and `cancel-in-progress: false` for production are the two different semantics needed.
- SHA-pinning actions is a supply chain security control. A mutable tag (`@v4`) can point to different code after a tag update. A commit SHA (`@11bd71901bbe5b1630ceea73d27597364c9af683`) is immutable — the code you audit is the code that runs.

## Workflow Skeleton

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - run: make build
```

## Trigger Events

| Event | When |
|-------|------|
| `push` | Commit pushed to branch |
| `pull_request` | PR opened/updated/closed |
| `pull_request_target` | PR event, runs with base repo permissions |
| `schedule` | Cron schedule |
| `workflow_dispatch` | Manual trigger (UI/API) |
| `workflow_call` | Called by another workflow |
| `release` | GitHub Release created/published |
| `repository_dispatch` | External API call |
| `workflow_run` | After another workflow completes |

## Contexts

```yaml
${{ github.sha }}              # commit SHA
${{ github.ref }}              # refs/heads/main
${{ github.ref_name }}         # main
${{ github.event_name }}       # push / pull_request
${{ github.repository }}       # owner/repo
${{ github.actor }}            # user who triggered
${{ github.run_id }}           # unique run ID
${{ github.run_number }}       # sequential build number
${{ github.workspace }}        # /home/runner/work/repo/repo

${{ env.MY_VAR }}              # workflow env var
${{ secrets.MY_SECRET }}       # repository/org/env secret
${{ vars.MY_VAR }}             # repository/org/env variable (non-secret)
${{ needs.job-id.outputs.key }} # output from upstream job
${{ matrix.os }}               # current matrix value
${{ runner.os }}               # Linux / Windows / macOS
${{ runner.temp }}             # temp directory
```

## Common Patterns

### Build and Push Docker Image (with OIDC to ECR)
```yaml
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: ${{ vars.AWS_ROLE_ARN }}
    aws-region: us-east-1

- uses: aws-actions/amazon-ecr-login@v2

- run: |
    IMAGE="$ECR_REGISTRY/myapp:sha-${GITHUB_SHA::8}"
    docker build -t "$IMAGE" .
    docker push "$IMAGE"
    echo "image=$IMAGE" >> $GITHUB_OUTPUT
  id: build
  env:
    ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
```

### Cache Node Modules
```yaml
- uses: actions/setup-node@v4
  with:
    node-version: '20'
    cache: 'npm'        # or 'yarn' or 'pnpm'
- run: npm ci
```

### Upload and Download Artifacts
```yaml
# Upload (in build job)
- uses: actions/upload-artifact@v4
  with:
    name: dist
    path: dist/
    retention-days: 7

# Download (in later job)
- uses: actions/download-artifact@v4
  with:
    name: dist
    path: dist/
```

### Matrix Build
```yaml
strategy:
  fail-fast: false
  matrix:
    python-version: ['3.10', '3.11', '3.12']
steps:
- uses: actions/setup-python@v5
  with:
    python-version: ${{ matrix.python-version }}
```

### Manual Approval via Environment
```yaml
jobs:
  deploy:
    environment: production   # requires reviewer approval in GitHub settings
    runs-on: ubuntu-latest
```

### Conditional Steps
```yaml
- run: ./deploy.sh
  if: github.ref == 'refs/heads/main' && github.event_name == 'push'

- run: echo "PR only"
  if: github.event_name == 'pull_request'

- run: echo "on failure"
  if: failure()

- run: echo "always"
  if: always()
```

### Pass Data Between Steps
```yaml
- id: compute
  run: echo "value=hello" >> $GITHUB_OUTPUT

- run: echo "${{ steps.compute.outputs.value }}"
```

### Set Environment Variable for Subsequent Steps
```yaml
- run: echo "TAG=sha-${GITHUB_SHA::8}" >> $GITHUB_ENV

- run: docker build -t myapp:$TAG .   # $TAG is available here
```

### Reusable Workflow Call
```yaml
jobs:
  deploy:
    uses: myorg/workflows/.github/workflows/deploy.yml@main
    with:
      environment: production
    secrets: inherit
```

### Self-Hosted Runner
```yaml
runs-on: [self-hosted, linux, x64, gpu]
```

## Permissions Reference

```yaml
permissions:
  actions: read|write|none
  checks: read|write|none
  contents: read|write|none      # repo contents, releases
  deployments: read|write|none
  id-token: write                # required for OIDC
  issues: read|write|none
  packages: read|write|none      # GitHub Packages
  pull-requests: read|write|none
  security-events: write         # upload SARIF results
  statuses: read|write|none
```

Set `permissions: read-all` at workflow level then grant only what each job needs.

## Expressions and Functions

```yaml
${{ format('Hello {0}!', github.actor) }}
${{ join(matrix.os, ', ') }}
${{ toJSON(github) }}
${{ fromJSON(needs.build.outputs.matrix) }}
${{ hashFiles('**/package-lock.json') }}
${{ contains(github.event.pull_request.labels.*.name, 'deploy') }}
${{ startsWith(github.ref, 'refs/tags/') }}
${{ github.event_name == 'push' || github.event_name == 'workflow_dispatch' }}
```

## Key Actions Reference

| Action | Purpose |
|--------|---------|
| `actions/checkout@v4` | Clone repository |
| `actions/setup-node@v4` | Install Node.js |
| `actions/setup-python@v5` | Install Python |
| `actions/setup-java@v4` | Install JDK |
| `actions/setup-go@v5` | Install Go |
| `actions/cache@v4` | Cache directories |
| `actions/upload-artifact@v4` | Save files between jobs |
| `actions/download-artifact@v4` | Retrieve saved files |
| `actions/github-script@v7` | Run JS with Octokit API |
| `docker/setup-buildx-action@v3` | Enable BuildKit/multi-platform |
| `docker/build-push-action@v6` | Build and push Docker images |
| `aws-actions/configure-aws-credentials@v4` | OIDC auth to AWS |
| `azure/login@v2` | OIDC auth to Azure |
| `google-github-actions/auth@v2` | OIDC auth to GCP |

## Gotchas

- **`set-output` is deprecated** — use `echo "key=value" >> $GITHUB_OUTPUT`
- **`save-state` is deprecated** — use `echo "key=value" >> $GITHUB_STATE`
- **`add-mask`** — mask a value: `echo "::add-mask::$SECRET"`
- **Secrets not available in forks** — `pull_request` from a fork has no secrets; use `pull_request_target` carefully (security risk)
- **`GITHUB_TOKEN` expires** — it's valid for the duration of the job only
- **`workflow_run` and `pull_request_target`** — run with base repo permissions; dangerous if checkout + run untrusted code
- **Cache key collision** — use `hashFiles` to bust cache on lockfile changes
- **`fail-fast: true` (default)** — cancels other matrix jobs on first failure; set `false` to see all results

***

## OIDC — Keyless Cloud Auth

```yaml
# AWS — no stored access keys needed
permissions:
  id-token: write
  contents: read

steps:
  - uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-assume: arn:aws:iam::123456789:role/github-actions-role
      aws-region: us-east-1
      # Trust policy must match: repo:ORG/REPO:ref:refs/heads/main

  - run: aws s3 ls   # Authenticated!

# Azure — federated identity
  - uses: azure/login@v2
    with:
      client-id: ${{ secrets.AZURE_CLIENT_ID }}
      tenant-id: ${{ secrets.AZURE_TENANT_ID }}
      subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

# GCP
  - uses: google-github-actions/auth@v2
    with:
      workload_identity_provider: projects/123/locations/global/workloadIdentityPools/pool/providers/github
      service_account: my-sa@project.iam.gserviceaccount.com
```

***

## Concurrency — Cancel Stale Runs

```yaml
# Cancel in-progress runs for the same branch
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

# Per-environment — don't cancel production deploys
concurrency:
  group: deploy-production
  cancel-in-progress: false
```

***

## Composite Action (Reusable Step Group)

```yaml
# .github/actions/setup-app/action.yml
name: 'Setup Application'
description: 'Install deps, configure env'
inputs:
  node-version:
    default: '20'
runs:
  using: composite
  steps:
    - uses: actions/setup-node@v4
      with:
        node-version: ${{ inputs.node-version }}
        cache: npm
    - run: npm ci
      shell: bash
    - run: cp .env.example .env
      shell: bash

# Usage in any workflow:
# - uses: ./.github/actions/setup-app
#   with:
#     node-version: '22'
```

***

## Debugging

```bash
# Enable debug logging — add repository secret:
ACTIONS_STEP_DEBUG=true
ACTIONS_RUNNER_DEBUG=true

# Print all contexts
- run: echo '${{ toJSON(github) }}'
- run: echo '${{ toJSON(env) }}'
- run: echo '${{ toJSON(secrets) }}'   # Shows *** for secret values

# tmate — SSH into a stuck runner
- uses: mxschmitt/action-tmate@v3
  if: failure()   # Only on failure
  with:
    limit-access-to-actor: true
```

***

## GitHub CLI (`gh`) in Workflows

```yaml
# GITHUB_TOKEN is auto-available
env:
  GH_TOKEN: ${{ github.token }}

steps:
  # Comment on PR
  - run: gh pr comment ${{ github.event.number }} --body "Deployed to staging ✅"

  # Create release
  - run: gh release create v${{ github.run_number }} dist/* --title "Release ${{ github.run_number }}"

  # Check PR labels
  - run: gh pr view ${{ github.event.number }} --json labels --jq '.labels[].name'

  # Trigger another workflow
  - run: gh workflow run deploy.yml -f environment=production

  # Download artifact from another run
  - run: gh run download ${{ github.event.workflow_run.id }} --name dist
```

***

## Security Hardening Patterns

```yaml
# 1. Pin actions to commit SHA
- uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2

# 2. Minimal permissions per job
jobs:
  build:
    permissions:
      contents: read
      packages: write

# 3. Prevent script injection — use env vars
- name: Safe input handling
  env:
    PR_TITLE: ${{ github.event.pull_request.title }}
  run: echo "$PR_TITLE"   # NOT: echo "${{ github.event.pull_request.title }}"

# 4. Restrict who can trigger workflow_dispatch
on:
  workflow_dispatch:
    # Additional restriction via branch protection rules in GitHub settings

# 5. Audit third-party actions before use
# Check: does the action request more permissions than needed?
# Check: is it pinned to a tag or SHA?
# Tool: zizmor (GitHub Actions static analyzer)
# pip install zizmor && zizmor .github/workflows/
```

***

## Useful One-Liners

```yaml
# Short git SHA (first 8 chars)
IMAGE_TAG: sha-${{ github.sha[:8] }}    # expression syntax
# OR in shell:
- run: echo "TAG=sha-${GITHUB_SHA::8}" >> $GITHUB_ENV

# Detect if files changed (to skip unnecessary jobs)
- uses: dorny/paths-filter@v3
  id: changes
  with:
    filters: |
      backend:
        - 'src/**'
        - 'requirements.txt'
- run: ./test.sh
  if: steps.changes.outputs.backend == 'true'

# Get PR number in push event (from merge commit)
- run: |
    PR_NUMBER=$(gh pr list --state merged --search "$GITHUB_SHA" --json number --jq '.[0].number')
    echo "PR_NUMBER=$PR_NUMBER" >> $GITHUB_ENV
  env:
    GH_TOKEN: ${{ github.token }}

# Notify Slack on failure
- uses: slackapi/slack-github-action@v1
  if: failure()
  with:
    payload: |
      {"text": "❌ *${{ github.workflow }}* failed on `${{ github.ref_name }}` — <${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}|View Run>"}
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

## System Design Perspective

**Pipeline scalability:**
- GitHub-hosted runners scale automatically with no configuration. Each job gets a fresh VM. Concurrency is limited by your GitHub plan; for large teams, use larger runners or self-hosted ARC runners to remove that ceiling.
- Matrix strategy provides free horizontal scaling. `python-version: [3.10, 3.11, 3.12] × os: [ubuntu, windows, macos]` = 9 parallel jobs, each on its own runner, at zero configuration cost. Total CI time = slowest individual job, not sum.
- `max-parallel` in matrix limits simultaneous jobs when GitHub concurrency limits are a concern or when downstream systems (staging environment, shared database) cannot handle parallel load.

**Agent/runner architecture trade-offs:**
- GitHub-hosted runners: zero ops, fresh VM, multiple OS options. Limitation: no access to private VPC resources (RDS, internal services). Work around with VPN actions or use self-hosted runners in the VPC.
- Self-hosted persistent runners: fast (no VM boot), private network access. Problem: state accumulates between jobs (leftover files, cached credentials, modified tool versions). Requires regular cleanup or re-imaging.
- ARC ephemeral runners: each job creates a fresh K8s pod, which registers as a runner, executes the job, and self-destructs. Best of both worlds: clean environment + private network access.

**Failure recovery:**
- Failed matrix jobs can be re-run individually (GitHub UI: "Re-run failed jobs"). Successful matrix jobs don't re-run — only the failed cells are retried.
- For OIDC-authenticated long jobs, the assumed role session may expire. Set `role-duration-seconds` in `configure-aws-credentials` to extend the session, or structure the workflow to re-authenticate between jobs.
- `concurrency: cancel-in-progress: false` for production deploy jobs ensures a running deployment is never cancelled mid-way. Use a separate concurrency group per environment to queue rather than cancel.

**Caching strategies:**
- `hashFiles('**/package-lock.json')` as cache key ensures a cache miss when any dependency changes — prevents stale caches. The `restore-keys` fallback uses a prefix match to find the most recent partial cache hit.
- Cache is branch-scoped: a cache from `main` is available to feature branches as a restore-key fallback. A cache from a feature branch is NOT available to other branches.
- Docker layer caching in GHA: use `docker/build-push-action` with `cache-from: type=gha` and `cache-to: type=gha,mode=max` — uses GitHub's cache backend, free up to 10GB per repo.

**Security boundaries:**
- `permissions: {}` at the workflow level disables all GITHUB_TOKEN scopes. Job-level `permissions` then grants only what that specific job needs. This applies the principle of least privilege at the finest granularity.
- Fork PRs have no access to secrets and a read-only GITHUB_TOKEN regardless of permissions settings. This is enforced at the GitHub API level, not just in YAML.
- `pull_request_target` runs with the BASE repo's permissions and secrets. If you checkout the PR's code in a `pull_request_target` workflow, that code runs with base repo secrets — a critical injection attack vector. Never combine `pull_request_target` + `actions/checkout` with PR ref.
