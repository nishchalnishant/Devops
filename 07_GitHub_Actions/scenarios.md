# Production Scenarios & Troubleshooting Drills (Senior Level)

### Scenario 1: OIDC Trust Policy Failure
**Problem:** GitHub Action cannot assume an AWS IAM Role.
**Fix:** The AWS Trust Policy must exactly match the `repo:org/repo` format. Check the `aud` and `sub` claims.

### Scenario 2: Self-hosted Runner Security
**Problem:** A contributor steals a secret via a PR on an open-source project.
**Fix:** Never use `pull_request_target` on untrusted forks. Use Environments with mandatory approvals for secret access.

### Scenario 3: Matrix Build Optimization
**Problem:** You are testing on 10 versions of Node, but if version 1 fails, you want to stop all others immediately to save money.
**Fix:** Set `fail-fast: true` in your matrix strategy.

***

## Scenario 4: Workflow Triggered Too Often — Slowing CI and Burning Minutes

**Situation**: Every push to every branch triggers the full build+test+scan pipeline (15 minutes). Developers pushing 10 times a day consume 150 minutes per person per day.

**Resolution**:
```yaml
on:
  push:
    branches: [main, 'release/**']  # only meaningful branches run full pipeline
    paths-ignore: ['**.md', 'docs/**', '.github/CODEOWNERS']
  pull_request:
    branches: [main]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true   # cancel stale runs on rapid pushes
```

Additionally, split the pipeline: run cheap steps (lint, unit tests) on every push; run expensive steps (integration tests, security scan) only on PR to main.

***

## Scenario 5: Secret Exposed in Workflow Logs

**Situation**: A developer added `run: echo "API_KEY=${{ secrets.API_KEY }}"` for debugging and pushed to main. The secret appeared in the public build log.

**Immediate response**:
1. Rotate the exposed secret immediately
2. Revoke the old value in the external system (API provider, cloud console)
3. Update the secret in GitHub Settings

**Prevention**:
- GitHub masks `${{ secrets.* }}` in logs, but only when referenced directly — string manipulation can bypass masking: `echo ${API_KEY:0:4}` may print unmasked characters
- Never `echo` a secret even temporarily
- Add a branch protection rule requiring PR review so debug commits can't land directly on main
- Use `::add-mask::$VALUE` to mask a dynamically computed value

***

## Scenario 6: Self-Hosted Runner Compromised via Malicious PR

**Situation**: An open-source project used self-hosted runners. A malicious PR modified the workflow to exfiltrate environment variables from the runner.

**Root cause**: The project used `pull_request_target` which runs workflows with base repo secrets, and the workflow checked out the PR's code and ran it.

**Fix**:
- For public repos: use GitHub-hosted runners for untrusted code; self-hosted runners should only run for trusted collaborators
- Never combine `pull_request_target` + `actions/checkout` of the PR head + running untrusted code
- Safe pattern for external PRs needing secrets:
```yaml
on:
  pull_request_target:
    types: [labeled]   # only runs when a maintainer adds a trusted label

jobs:
  test:
    if: contains(github.event.pull_request.labels.*.name, 'safe-to-test')
    environment: external-pr   # requires manual approval
```

***

## Scenario 7: Workflow Fails Due to Expired OIDC Token

**Situation**: A long-running job (30+ minutes) fails with "token has expired" when trying to push to ECR near the end of the job.

**Root cause**: OIDC tokens from GitHub have a short TTL (~10 minutes). If the `configure-aws-credentials` step ran at the start of a long job, the credentials expire mid-job.

**Fix**: Move the cloud authentication step as close as possible to where the credentials are actually needed. Or use `aws-actions/configure-aws-credentials` with `role-duration-seconds` increased (requires the IAM role to allow longer sessions):
```yaml
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: ${{ vars.AWS_ROLE_ARN }}
    aws-region: us-east-1
    role-duration-seconds: 3600   # 1 hour max (IAM role must allow this)
```

Alternatively, split the job: authenticate and push in a separate, short job that runs after the build job.

***

## Scenario 8: Dependabot PRs Failing Because They Can't Access Secrets

**Situation**: Dependabot PRs fail at the "integration test" step because the workflow can't connect to a staging database.

**Root cause**: Dependabot PRs run as fork PRs and don't have access to repository secrets.

**Fix**: Use a separate workflow triggered by `pull_request_target` specifically for Dependabot:
```yaml
on:
  pull_request_target:

jobs:
  test:
    if: github.actor == 'dependabot[bot]'
    environment: dependabot-tests   # environment with required reviewer
    steps:
    - uses: actions/checkout@v4
      with:
        ref: ${{ github.event.pull_request.head.sha }}
    - run: ./integration-test.sh
      env:
        DB_URL: ${{ secrets.STAGING_DB_URL }}
```

> [!CAUTION]
> This is safe only because you're restricting it to `dependabot[bot]` (verified GitHub actor) and using `actions/checkout` of a known commit SHA. Never do this for arbitrary external PRs.

***

## Scenario 1: Self-Hosted Runner Disk Exhaustion
**Symptom:** Workflows fail with `No space left on device`.
**Diagnosis:** Build artifacts, Docker layers, and temp files from previous runs are not being cleaned up on the persistent runner.
**Fix:** 
1. Use a cleanup step: `rm -rf ${{ github.workspace }}/*`.
2. Implement a `cron` job on the runner to run `docker system prune -f`.
3. Switch to **Ephemeral Self-Hosted Runners** using the Action Runner Controller (ARC) on K8s.

## Scenario 2: Workflow Secret Access Denied from Forked PRs
**Symptom:** A PR from a contributor's fork fails because secrets (e.g., `AWS_SECRET_ACCESS_KEY`) are empty.
**Diagnosis:** By default, GHA does not pass secrets to workflows triggered by `pull_request` from forks for security reasons.
**Fix:** 
1. Use the `pull_request_target` event (Use with extreme caution! It runs in the context of the base branch and can be exploited).
2. Manually trigger the workflow after reviewing the code.

## Scenario 3: Marketplace Action Supply Chain Risk
**Symptom:** A minor version update of a 3rd party action (e.g., `actions/setup-node@v3`) introduced a bug or a security vulnerability.
**Diagnosis:** Depending on tags like `@v3` is unstable as they can be moved.
**Fix:** Always pin actions to a specific **commit SHA**: `uses: actions/setup-node@64ed1c7eab4cce33da29d98e940a440156fefd19`.

***

### Scenario 4: Self-Hosted Runner Picks Up Jobs from Wrong Repositories

**Problem:** A self-hosted runner registered at the organization level starts executing jobs from a public fork's pull request. The runner has access to production secrets via environment variables.

**Root cause:** Organization-level runners in GitHub can be configured to run on pull requests from public forks. If the workflow is approved (first-time contributor approval), the fork's workflow runs on your runner with access to organization secrets.

**Fix — restrict runner scope:**
```yaml
# In the workflow file — require environment approval for sensitive jobs
jobs:
  deploy:
    environment: production   # requires manual approval gate
    runs-on: self-hosted
```

**Organization settings hardening:**
1. `Settings → Actions → General → Fork pull request workflows from outside collaborators`: set to `Require approval for all outside collaborators`
2. Use separate runner groups: `Settings → Actions → Runner groups` — create a `production` group with `Allow public repositories: false`
3. Register production runners to the `production` group only; general CI runners to a separate group

**Structural defense:** Never put secrets in runner environment variables at the OS level. Pull secrets from Vault or cloud secrets manager at job runtime, scoped to the specific workflow:
```yaml
- name: Get secret
  id: get-secret
  run: |
    SECRET=$(aws secretsmanager get-secret-value --secret-id prod/api-key --query SecretString --output text)
    echo "::add-mask::$SECRET"
    echo "API_KEY=$SECRET" >> $GITHUB_ENV
```

***

### Scenario 5: Workflow Runs But Skips All Steps — `if` Condition Evaluation Failure

**Problem:** A workflow triggers on push and pull_request. The deploy job has `if: github.ref == 'refs/heads/main'`. On a merge to main via GitHub UI, the job is completely skipped.

**Diagnosis:**
```yaml
# The condition looks correct
jobs:
  deploy:
    if: github.ref == 'refs/heads/main'
```

**Root cause:** When merging via `Squash and merge` or `Rebase and merge`, the triggering event is `push` with `github.ref = refs/heads/main` — this works. But some workflows trigger on both `push` and `pull_request`. On a PR from `main` to another branch, `github.ref` is the base branch. On a PR event, `github.ref` is actually `refs/pull/<number>/merge` — not `refs/heads/main`.

**Correct condition for deploy-only-on-merge:**
```yaml
jobs:
  deploy:
    if: |
      github.event_name == 'push' &&
      github.ref == 'refs/heads/main'
```

**Debug conditions by printing context:**
```yaml
- name: Debug context
  run: |
    echo "event: ${{ github.event_name }}"
    echo "ref: ${{ github.ref }}"
    echo "head_ref: ${{ github.head_ref }}"
    echo "base_ref: ${{ github.base_ref }}"
```

***

### Scenario 6: Concurrency Limit Causes Deployments to Queue Indefinitely

**Problem:** During a busy release day with 20 engineers merging to main, earlier deployment runs are stuck in "Waiting for pending jobs" even after 45 minutes. Recent deployments never get to run.

**Root cause:** No `concurrency` key set. GitHub Actions runs a new deployment workflow for every merge commit. With 20 merges, 20 deployment runs queue. Each takes 10 minutes — the last run must wait 200 minutes.

**Fix — cancel-in-progress with concurrency groups:**
```yaml
concurrency:
  group: deploy-production-${{ github.ref }}
  cancel-in-progress: true   # cancel queued/running jobs when a newer run arrives
```

**Nuance — don't cancel rollbacks:**
```yaml
concurrency:
  group: deploy-${{ github.ref }}-${{ github.workflow }}
  cancel-in-progress: ${{ github.event_name != 'workflow_dispatch' }}
  # Manual dispatches (rollbacks) are never cancelled
```

**For multi-environment pipelines — independent concurrency per environment:**
```yaml
jobs:
  deploy-staging:
    concurrency:
      group: deploy-staging
      cancel-in-progress: true

  deploy-prod:
    concurrency:
      group: deploy-prod
      cancel-in-progress: false   # prod deployments always complete
    needs: deploy-staging
```

***

### Scenario 7: Secrets Accidentally Printed in Workflow Logs

**Problem:** A developer added `run: echo ${{ secrets.API_KEY }}` for debugging. GitHub masks the literal secret value, but a base64-encoded version of it is visible in the logs from a subsequent step.

**Why masking fails:** GitHub Actions masks the exact secret string. If the secret is transformed (base64, URL-encoded, JSON-serialized), the transformed version is not automatically masked.

**Detection:**
```bash
# In the workflow — check logs for suspicious base64 strings
echo "${{ secrets.API_KEY }}" | base64   # This output is NOT masked
```

**Immediate response:**
1. Rotate the exposed secret immediately in the secret store (AWS Secrets Manager, Vault, GitHub Secrets)
2. Update the GitHub Secret with the new value
3. Audit all workflow runs in the past 90 days for the exposed secret pattern using GitHub Audit Log API:
```bash
gh api /orgs/myorg/audit-log \
  --field phrase="secret_scanning_alert" \
  --field per_page=100
```

**Prevention:**

1. **Never use `${{ secrets.X }}` directly in `run` steps** — the expression is evaluated before the shell sees it, making masking unreliable:
```yaml
# UNSAFE
run: curl -H "Authorization: ${{ secrets.API_KEY }}" https://api.example.com

# SAFE — set as env var, GitHub masks env vars at the process boundary
env:
  API_KEY: ${{ secrets.API_KEY }}
run: curl -H "Authorization: $API_KEY" https://api.example.com
```

2. **Mask derived values explicitly:**
```yaml
- run: |
    ENCODED=$(echo "$API_KEY" | base64)
    echo "::add-mask::$ENCODED"
  env:
    API_KEY: ${{ secrets.API_KEY }}
```

3. **Use secret scanning:** Enable GitHub Advanced Security → Secret Scanning to detect accidentally committed secrets.

***

### Scenario 8: Reusable Workflow Can't Access Caller's Secrets

**Problem:** A central reusable workflow (`/.github/workflows/deploy.yml`) deploys the application. When called from a repository's workflow, the deploy step fails with "secret not found" even though the secret exists in the caller's repository.

**Root cause:** Reusable workflows run in the context of the called repository (the one containing the workflow file). They cannot automatically access the caller's secrets.

**Fix — explicitly pass secrets from caller:**

Caller workflow:
```yaml
jobs:
  call-deploy:
    uses: org/central-workflows/.github/workflows/deploy.yml@main
    secrets:
      DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}
      # Or pass all secrets:
      # secrets: inherit   # GitHub Actions 2022+ feature
```

Reusable workflow:
```yaml
on:
  workflow_call:
    secrets:
      DEPLOY_TOKEN:
        required: true

jobs:
  deploy:
    steps:
    - run: deploy.sh
      env:
        DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}
```

**`secrets: inherit` (simpler but less explicit):**
```yaml
# Caller
jobs:
  call-deploy:
    uses: org/central-workflows/.github/workflows/deploy.yml@main
    secrets: inherit   # passes ALL caller secrets to the reusable workflow
```

Use `secrets: inherit` for internal workflows where secret names are consistent. Use explicit passing when the reusable workflow is shared across orgs or when secret names differ.

***

### Scenario 9: GitHub Actions Cache Key Collision Between PRs

**Problem:** Two PRs are open simultaneously, both modifying `package.json`. PR #1 merges first and its cache is saved. PR #2's build uses PR #1's cache (wrong `node_modules`) — integration tests pass on CI but fail in prod because packages are mismatched.

**Root cause:** Both PRs use the same cache key because the key only hashes `package-lock.json`, but both PRs have the same lock file (they both added a package before the lock file was updated).

**Well-designed cache key strategy:**
```yaml
- uses: actions/cache@v4
  with:
    path: node_modules
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
      ${{ runner.os }}-node-
```

**The `restore-keys` fallback mechanism:** If the exact key misses, GitHub tries each restore-key prefix in order. The first matching cache is restored (partial hit). The job then runs, installs missing packages, and saves a new cache with the full key. This prevents cold starts without risking stale exact matches.

**For monorepos — scope cache to the affected package:**
```yaml
key: ${{ runner.os }}-${{ matrix.package }}-${{ hashFiles(format('packages/{0}/package-lock.json', matrix.package)) }}
```
