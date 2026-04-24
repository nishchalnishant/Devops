# GitHub Actions Cheatsheet

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
