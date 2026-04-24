# GitHub Actions & Modern CI/CD

GitHub Actions has redefined CI/CD by bringing automation directly into the repository. It is event-driven, allowing you to trigger workflows on almost any GitHub event.

#### 1. The Architecture
*   **Workflows:** The top-level YAML file in `.github/workflows`.
*   **Events:** Triggers like `push`, `pull_request`, `schedule` (cron), or `workflow_dispatch` (manual).
*   **Jobs:** A set of steps that run on the same runner. Jobs run in parallel by default.
*   **Steps:** Individual tasks (shell scripts or "Actions").
*   **Runners:** The servers that run the jobs. GitHub-hosted runners are clean VMs, while Self-hosted runners allow you to use your own infrastructure.

#### 2. Advanced Features
*   **Matrix Builds:** Running the same job across multiple versions of an OS or language (e.g., testing on Node 16, 18, and 20 simultaneously).
*   **Environments:** Provide protection rules (like manual approvals) and secret management for specific deployment targets (Dev, Prod).
*   **Reusable Workflows:** DRY (Don't Repeat Yourself) principle. Define a workflow once and call it from other repositories.
*   **Custom Actions:** Write your own automation logic in JavaScript or Docker and share it on the Marketplace.

#### 3. Security & Best Practices
*   **OIDC (OpenID Connect):** Connect GitHub Actions to AWS/Azure without using long-lived secrets/keys.
*   **GitHub Token:** Use the automatic `${{ secrets.GITHUB_TOKEN }}` for repo operations, but always restrict its permissions to `contents: read` unless more is needed.
*   **Caching:** Use `actions/cache` to speed up builds by caching dependencies like `node_modules` or `~/.m2`.
***

## Workflow Syntax Deep Dive

### Event Filters

```yaml
on:
  push:
    branches: [main, 'release/**']
    paths-ignore: ['**.md', 'docs/**']
  pull_request:
    types: [opened, synchronize, reopened]
    branches: [main]
  schedule:
    - cron: '0 2 * * 1-5'   # 2 AM UTC weekdays
  workflow_dispatch:
    inputs:
      environment:
        type: choice
        options: [dev, staging, prod]
        required: true
```

`paths` / `paths-ignore`: avoid triggering builds on doc-only changes. `types`: filter PR events — `synchronize` fires on new commits to an open PR.

### Job Dependencies and Outputs

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      image-tag: ${{ steps.tag.outputs.tag }}
    steps:
    - id: tag
      run: echo "tag=sha-${GITHUB_SHA::8}" >> $GITHUB_OUTPUT

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
    - run: echo "Deploying ${{ needs.build.outputs.image-tag }}"
```

`needs` creates a dependency DAG. `outputs` passes data between jobs via `GITHUB_OUTPUT`. Data is strings only — use JSON for structured data: `echo "matrix=$(jq -cn '...')" >> $GITHUB_OUTPUT`.

### Concurrency Control

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

Prevents multiple workflow runs for the same branch running simultaneously. `cancel-in-progress: true` cancels older runs when a new push arrives — saves minutes on rapid commits. For production deploys, set `cancel-in-progress: false` so a running deploy isn't interrupted.

***

## OIDC: Keyless Cloud Authentication

OIDC lets GitHub Actions authenticate to AWS/Azure/GCP without storing long-lived credentials as secrets. GitHub acts as an OIDC identity provider; the cloud provider trusts tokens from GitHub for specific subjects.

### AWS Setup

```yaml
permissions:
  id-token: write   # required to request OIDC token
  contents: read

steps:
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::123456789:role/GitHubActionsRole
    aws-region: us-east-1
```

AWS IAM trust policy:
```json
{
  "Effect": "Allow",
  "Principal": {"Federated": "arn:aws:iam::123456789:oidc-provider/token.actions.githubusercontent.com"},
  "Action": "sts:AssumeRoleWithWebIdentity",
  "Condition": {
    "StringEquals": {
      "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
      "token.actions.githubusercontent.com:sub": "repo:myorg/myrepo:ref:refs/heads/main"
    }
  }
}
```

The `sub` claim can be scoped to: specific repo, branch, tag, environment, or PR. This limits which workflows can assume the role.

### Azure Setup

```yaml
- uses: azure/login@v2
  with:
    client-id: ${{ secrets.AZURE_CLIENT_ID }}
    tenant-id: ${{ secrets.AZURE_TENANT_ID }}
    subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
```

Configure a Federated Credential on the Azure App Registration pointing to the GitHub OIDC subject.

***

## Reusable Workflows

Define once, call from many repos. Reduces duplication of CI boilerplate across an organization.

**Called workflow** (`.github/workflows/deploy.yml` in `myorg/shared-workflows`):
```yaml
on:
  workflow_call:
    inputs:
      environment:
        type: string
        required: true
    secrets:
      DEPLOY_TOKEN:
        required: true

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}
    steps:
    - run: ./deploy.sh ${{ inputs.environment }}
      env:
        TOKEN: ${{ secrets.DEPLOY_TOKEN }}
```

**Caller workflow**:
```yaml
jobs:
  deploy-prod:
    uses: myorg/shared-workflows/.github/workflows/deploy.yml@v1
    with:
      environment: production
    secrets:
      DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}
```

> [!IMPORTANT]
> Secrets are NOT automatically inherited by reusable workflows — they must be explicitly passed via `secrets:` or use `secrets: inherit` (passes all caller secrets).

***

## Matrix Strategy

Run jobs across multiple dimensions simultaneously:

```yaml
strategy:
  fail-fast: false     # don't cancel other matrix jobs if one fails
  max-parallel: 4      # limit concurrent jobs (protect downstream resources)
  matrix:
    os: [ubuntu-latest, windows-latest, macos-latest]
    node: ['18', '20', '22']
    exclude:
    - os: windows-latest
      node: '18'       # skip this combination
    include:
    - os: ubuntu-latest
      node: '20'
      experimental: true   # add extra variables to a specific combination
```

**Dynamic matrix** (from a previous job's output):
```yaml
jobs:
  generate-matrix:
    outputs:
      matrix: ${{ steps.set.outputs.matrix }}
    steps:
    - id: set
      run: |
        SERVICES=$(ls services/ | jq -R -s -c 'split("\n")[:-1]')
        echo "matrix={\"service\":$SERVICES}" >> $GITHUB_OUTPUT

  test:
    needs: generate-matrix
    strategy:
      matrix: ${{ fromJson(needs.generate-matrix.outputs.matrix) }}
    steps:
    - run: pytest services/${{ matrix.service }}/tests/
```

***

## Custom Actions

Three types of actions:

### Composite Action
Reuse steps without JavaScript or Docker:
```yaml
# action.yml in a repo
name: Setup and Build
inputs:
  node-version:
    default: '20'
runs:
  using: composite
  steps:
  - uses: actions/setup-node@v4
    with:
      node-version: ${{ inputs.node-version }}
  - run: npm ci
    shell: bash
  - run: npm run build
    shell: bash
```

### JavaScript Action
Fast (no container spin-up), cross-platform:
```yaml
runs:
  using: node20
  main: dist/index.js
```

### Docker Action
Full environment control, slower startup:
```yaml
runs:
  using: docker
  image: Dockerfile
```

***

## Caching

```yaml
- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-node-
```

Cache hit: restores cache, skips expensive install. Cache miss: runs install, saves cache at end of job. `restore-keys` provides fallback prefix matches for partial cache hits.

**Language-specific caching built into setup actions**:
```yaml
- uses: actions/setup-node@v4
  with:
    node-version: '20'
    cache: 'npm'        # built-in cache — no separate cache step needed
```

***

## Environments and Protection Rules

Environments add approval gates and environment-specific secrets:

```yaml
jobs:
  deploy:
    environment:
      name: production
      url: https://myapp.com   # shown in GitHub UI
    runs-on: ubuntu-latest
    steps:
    - run: ./deploy.sh
      env:
        API_KEY: ${{ secrets.PROD_API_KEY }}  # env-scoped secret
```

Environment protection rules (configured in GitHub UI):
- **Required reviewers**: named users/teams must approve before job runs
- **Wait timer**: delay between trigger and execution (e.g., 10-minute window to cancel)
- **Deployment branches**: only specific branches can deploy to this environment
- **Deployment protection rules** (custom): call a webhook to external approval system

***

## Security Hardening

### Minimal Permissions
```yaml
permissions: read-all   # deny all by default at workflow level

jobs:
  build:
    permissions:
      contents: read
      packages: write   # only what this job needs
```

### Pin Actions to SHA
```yaml
# BAD — tag can be moved to a malicious commit
- uses: actions/checkout@v4

# GOOD — SHA is immutable
- uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2
```

Use Dependabot or Renovate to keep pinned SHAs up to date automatically.

### Prevent Script Injection
```yaml
# BAD — attacker can inject via PR title
- run: echo "${{ github.event.pull_request.title }}"

# GOOD — pass via environment variable (not interpolated into shell)
- env:
    PR_TITLE: ${{ github.event.pull_request.title }}
  run: echo "$PR_TITLE"
```

### Restrict GITHUB_TOKEN
```yaml
permissions:
  contents: read    # minimal: only read repo
  # don't grant write permissions unless the job specifically needs them
```

***

## Self-Hosted Runners

### Runner Architecture

```
GitHub Actions service (cloud)
    │  webhook: job queued
    ▼
Runner process (on-prem or cloud VM)
    │  polls GitHub API for jobs matching its labels
    │  downloads workflow steps + actions
    ▼
Job execution (subprocess or container)
    │  streams logs back to GitHub
    ▼
GitHub Actions service
    │  stores logs, artifacts
```

```bash
# Install runner on a Linux VM
mkdir actions-runner && cd actions-runner
curl -o actions-runner-linux-x64-2.319.0.tar.gz -L \
  https://github.com/actions/runner/releases/download/v2.319.0/actions-runner-linux-x64-2.319.0.tar.gz
tar xzf ./actions-runner-linux-x64-2.319.0.tar.gz

# Configure (get token from GitHub repo/org Settings > Actions > Runners)
./config.sh --url https://github.com/myorg --token <TOKEN> \
  --labels self-hosted,linux,x64,gpu \
  --name prod-runner-01 \
  --runnergroup "production"

# Install as systemd service
sudo ./svc.sh install
sudo ./svc.sh start

# Check status
sudo ./svc.sh status
journalctl -u actions.runner.myorg.prod-runner-01 -f
```

### Kubernetes-Based Runners (Actions Runner Controller)

ARC (Actions Runner Controller) provisions ephemeral Kubernetes pods as runners:

```yaml
# RunnerDeployment — persistent runner pods
apiVersion: actions.summerwind.dev/v1alpha1
kind: RunnerDeployment
metadata:
  name: myorg-runners
spec:
  replicas: 3
  template:
    spec:
      organization: myorg
      labels: [self-hosted, linux, k8s]
      image: summerwind/actions-runner:latest
      resources:
        limits: {cpu: "2", memory: "4Gi"}
        requests: {cpu: "500m", memory: "1Gi"}
---
# HorizontalRunnerAutoscaler — scale based on queue depth
apiVersion: actions.summerwind.dev/v1alpha1
kind: HorizontalRunnerAutoscaler
metadata:
  name: myorg-runners-autoscaler
spec:
  scaleTargetRef:
    name: myorg-runners
  minReplicas: 1
  maxReplicas: 20
  metrics:
  - type: TotalNumberOfQueuedAndInProgressWorkflowRuns
    repositoryNames: [myorg/myrepo]
```

**Use self-hosted for:** GPU workloads, access to internal resources (VPC databases, private registries), build caching on fast local storage, cost control on long builds.

**Security isolation:** Each job should run in a fresh pod/container. Never share a runner across untrusted repos — a malicious PR can exfiltrate runner credentials.

```yaml
# Always use ephemeral runners for untrusted input (PRs from forks)
runs-on: [self-hosted, ephemeral]

# In ARC, set ephemeral: true to delete runner after each job
spec:
  ephemeral: true
```

***

## Larger GitHub-Hosted Runners

GitHub offers larger runners (2–64 cores, up to 256 GB RAM) for high-compute jobs:

```yaml
jobs:
  build:
    runs-on: ubuntu-latest-16-cores   # 16-core GitHub-hosted runner
    # or: ubuntu-latest-4-cores, ubuntu-latest-8-cores, ubuntu-latest-64-cores
```

Runners can be assigned to a runner group for access control. Configured in org/repo Settings → Actions → Runners.

***

## Workflow Expressions and Context

```yaml
# Contexts available in workflows
${{ github.sha }}              # full commit SHA
${{ github.ref }}              # refs/heads/main or refs/tags/v1.0
${{ github.ref_name }}         # main or v1.0 (short name)
${{ github.event_name }}       # push, pull_request, etc.
${{ github.actor }}            # username who triggered
${{ runner.os }}               # Linux, Windows, macOS
${{ env.MY_VAR }}              # env var set in this job
${{ secrets.MY_SECRET }}       # org/repo secret
${{ vars.MY_VAR }}             # org/repo variable (non-secret)

# Conditional expressions
if: github.ref == 'refs/heads/main'
if: contains(github.event.pull_request.labels.*.name, 'hotfix')
if: failure() && github.ref == 'refs/heads/main'   # only notify on main branch failure
if: always()   # run even if previous steps failed

# fromJson / toJson
- run: echo "${{ toJson(github.event) }}"
- env:
    MATRIX: ${{ toJson(matrix) }}
```

### Setting outputs and env vars

```yaml
steps:
- id: compute
  run: |
    VERSION=$(cat version.txt)
    echo "version=$VERSION" >> $GITHUB_OUTPUT
    echo "DEPLOY_ENV=staging" >> $GITHUB_ENV    # available to subsequent steps
    echo "::add-mask::$SECRET_VALUE"            # mask value from logs

- run: echo "Deploying ${{ steps.compute.outputs.version }} to $DEPLOY_ENV"
```

### Multiline strings

```yaml
- run: |
    echo "line 1"
    echo "line 2"

# Folded scalar for long single-line values
- run: >-
    aws s3 sync ./dist
    s3://my-bucket/
    --delete
    --cache-control "max-age=31536000"
```

***

## Debugging Workflows

```yaml
# Enable debug logging: set secret ACTIONS_STEP_DEBUG=true
# Or trigger with debug flag:
- name: Enable debug
  run: echo "::debug::This is a debug message"

# Group log output
- run: |
    echo "::group::Install dependencies"
    npm ci
    echo "::endgroup::"

# Add warning/error annotations
- run: |
    echo "::warning file=app.js,line=12::Deprecated API used"
    echo "::error file=app.js,line=45::Null pointer exception"

# Re-run failed jobs with debug logging (GitHub UI: Re-run jobs > Enable debug logging)
```

```bash
# Local testing with act (https://github.com/nektos/act)
act push                              # simulate push event
act pull_request -e event.json        # simulate PR with custom event payload
act -j build --secret-file .secrets   # run specific job with secrets file
act --list                            # list available workflows and jobs
```

***

## Artifact Management

```yaml
# Upload build artifacts
- uses: actions/upload-artifact@v4
  with:
    name: dist-${{ github.sha }}
    path: dist/
    retention-days: 7       # default 90 days; reduce to save storage
    if-no-files-found: error

# Download in another job
- uses: actions/download-artifact@v4
  with:
    name: dist-${{ github.sha }}
    path: ./dist

# Upload to GitHub releases
- uses: softprops/action-gh-release@v2
  with:
    files: |
      dist/myapp-linux-amd64
      dist/myapp-darwin-arm64
    generate_release_notes: true
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

***

## Key Gotchas

| Gotcha | Detail |
|--------|--------|
| `$GITHUB_OUTPUT` vs `set-output` | `set-output` command is deprecated; must use `echo "key=value" >> $GITHUB_OUTPUT` |
| Secrets not available in fork PRs | `pull_request` from forks doesn't have access to secrets — use `pull_request_target` carefully (security risk) |
| `pull_request_target` context is the base branch | The workflow runs in the context of the target branch, not the PR branch — `${{ github.sha }}` is the base commit |
| Reusable workflows don't inherit secrets | Must pass explicitly with `secrets:` or use `secrets: inherit`; not automatically passed |
| Matrix strategy `fail-fast: true` by default | One failed matrix job cancels all others; set `fail-fast: false` for independent dimensions |
| `actions/cache` only saves on cache miss | Cache is saved at end of job only if there was a cache miss; a cache hit doesn't re-save |
| Environment protection rules block all branches by default | After adding a required reviewer, all deployments need approval including automated ones |
| `concurrency: cancel-in-progress: true` on deploys | Can interrupt a running deploy mid-flight — use `cancel-in-progress: false` for production deployments |
| Self-hosted runner labels are additive | A job `runs-on: [self-hosted, linux]` matches any runner with ALL those labels, not just one |
| SHA-pinned actions need Dependabot | Pin to immutable SHA but keep a comment with the version; set up `dependabot.yml` to keep SHAs current |
