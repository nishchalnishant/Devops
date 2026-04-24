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
