# GitHub Actions — Interview Prep

```
GitHub Actions Interview — Easy
├── Core Structure
│   ├── Q1 — Workflow vs Job vs Step: YAML file vs runner group vs individual task
│   ├── Q2 — Runners: GitHub-hosted vs self-hosted
│   └── Q3 — Passing data between jobs: upload/download artifact OR job outputs
├── Triggers (on:)
│   ├── Q4 — push, pull_request, schedule, workflow_dispatch syntax
│   └── Q5 — workflow_dispatch: manual trigger with inputs
├── Actions & Steps
│   ├── Q6 — actions/checkout: fetch-depth, ref (PR head SHA)
│   └── Q11 — uses vs run: action vs shell command
├── Security & Secrets
│   ├── Q7 — GITHUB_TOKEN: auto-generated, scope, permissions, expires after job
│   └── Q9 — env vars: three scopes (workflow/job/step), $GITHUB_ENV
├── Flow Control
│   ├── Q8 — if: conditional steps (github.ref, failure(), always())
│   ├── Q10 — concurrency: group key, cancel-in-progress
│   └── Q12 — needs: sequential job dependencies, multiple deps
└── Data Flow
    ├── Q3 — upload-artifact / download-artifact (cross-job files)
    └── Q3 — GITHUB_OUTPUT (cross-step data within same job)
```

### First Principles

- A workflow is a file; a job is a runner; a step is a command. This hierarchy maps to: what to do (workflow) → where to do it (job/runner) → the individual actions (steps).
- Jobs in the same workflow run in parallel by default because there's no reason to serialize independent work. The `needs:` keyword is the explicit opt-in for sequential dependency.
- The GITHUB_TOKEN is auto-generated per job and scoped to the repository. It expires when the job ends — it cannot be used outside the job that received it. This is a security property, not a limitation.
- `actions/checkout` with `fetch-depth: 0` fetches full history, enabling `git log`, `git diff`, and tools that need commit history. Default `fetch-depth: 1` is a shallow clone — faster but no history.
- `if: failure()` runs a step even when previous steps failed. `if: always()` runs regardless of all previous states. Without these, steps after a failed step are skipped — important for cleanup and notification steps.

## Easy

**1. In GitHub Actions, what is the difference between a workflow, a job, and a step?**

- **Workflow:** The entire automated process defined in a YAML file under `.github/workflows/`.
- **Job:** A set of steps that execute on the same runner. A workflow can have multiple jobs running in parallel or sequentially.
- **Step:** An individual task within a job — either a shell command or a pre-built Action called with `uses:`.

**2. What is a GitHub Actions runner?**

A runner is a server that executes jobs in a workflow. GitHub provides hosted runners (Ubuntu, Windows, macOS). Self-hosted runners are registered to a repository or organization for custom hardware, private network access, or cost control at high build volume.

**3. How do you pass data or artifacts from one job to another in GitHub Actions?**

Use `actions/upload-artifact` in the producing job and `actions/download-artifact` in the consuming job. For scalar values between jobs in the same workflow, use job outputs: set `outputs` on the producing job and reference `${{ needs.job-name.outputs.key }}` in the consuming job.

**4. What triggers a GitHub Actions workflow?**

Workflows are triggered by events defined in the `on:` block: `push`, `pull_request`, `schedule` (cron), `workflow_dispatch` (manual), `release`, `workflow_call` (called by another workflow), and many others. Multiple triggers can be specified in the same `on:` block.

**5. What is `workflow_dispatch` and when would you use it?**

`workflow_dispatch` allows a workflow to be triggered manually from the GitHub UI or via the API. It supports defining inputs that the user fills in at trigger time. Used for on-demand deployments, releases, or maintenance tasks.

***


**6. What does `actions/checkout` do and why is it almost always the first step?**

`actions/checkout` clones the repository into the runner's workspace (`$GITHUB_WORKSPACE`). Without it, subsequent steps have no access to the repo's code. By default it checks out the commit that triggered the workflow. Options: `fetch-depth: 0` to get full git history (needed for changelog generation or `git log`), `ref` to check out a specific branch/tag/SHA.

**7. What is `GITHUB_TOKEN` and what can it do?**

`GITHUB_TOKEN` is an automatically generated short-lived token provided by GitHub for each workflow run. It can authenticate against the GitHub API and GitHub Packages within the scope of the repository. Permissions are configurable via the `permissions` key. It expires when the job finishes. It cannot access other repositories or trigger new workflow runs by default (to prevent recursive loops).

**8. How do you run a step only on the `main` branch?**

Use an `if` condition:
```yaml
- run: ./deploy.sh
  if: github.ref == 'refs/heads/main'
```

Or at the job level:
```yaml
jobs:
  deploy:
    if: github.ref == 'refs/heads/main'
```

**9. What is `concurrency` in a GitHub Actions workflow?**

`concurrency` prevents multiple workflow runs from executing the same job simultaneously. Commonly used to prevent overlapping deploys:
```yaml
concurrency:
  group: deploy-${{ github.ref }}
  cancel-in-progress: true
```
`cancel-in-progress: true` cancels the older run when a new one starts. Set `false` for deploys to avoid interrupting a running rollout.

**10. How do environment variables work in GitHub Actions?**

Three scopes: workflow-level (`env:` at the top), job-level (`env:` under the job), step-level (`env:` under the step). Inner scopes override outer. Set dynamic values with `echo "KEY=value" >> $GITHUB_ENV` — available to all subsequent steps in the same job. Access in expressions with `${{ env.KEY }}`.

**11. What is the difference between `uses` and `run` in a step?**

`uses` invokes a pre-built Action (JavaScript, Docker, or composite) from a repository or the Marketplace: `uses: actions/setup-node@v4`. `run` executes shell commands directly on the runner: `run: npm ci`. Both can be combined in the same job.

**12. How do you make one job wait for another in the same workflow?**

Use `needs`:
```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps: [...]

  test:
    needs: build     # waits for build to succeed
    runs-on: ubuntu-latest
```

Multiple dependencies: `needs: [build, lint]` — waits for both. If any dependency fails, the dependent job is skipped by default.

### System Design Perspective

**Pipeline scalability:**
- Jobs in a workflow run in parallel automatically. With 5 independent jobs (lint, unit-test, integration-test, security-scan, build), all 5 start simultaneously. Total pipeline time = duration of the slowest job, not the sum.
- `needs:` creates a DAG (directed acyclic graph) of job dependencies. Design the DAG to minimize the critical path: what is the minimum sequential chain that must complete before you can deploy?
- GitHub plan limits apply to concurrent runners (e.g., 20 simultaneous jobs on free, higher on paid). A matrix job that generates 50 combinations will be throttled to the concurrency limit — excess jobs queue.

**Runner/agent architecture trade-offs:**
- GitHub-hosted runners boot fresh VMs. Cold start is ~10-30 seconds. For jobs that take <60 seconds total, the overhead is significant. Larger GitHub-hosted runners (`ubuntu-latest-16-cores`) reduce this but cost more per minute.
- Self-hosted runners have zero boot overhead. Trade-off: they accumulate state. A secret written to a file by job A may persist and be readable by job B from a different PR. Always clean up in `post:` steps.
- Use `runs-on: [self-hosted, linux, docker]` with label selectors to route jobs to specific self-hosted runner groups. Only jobs matching ALL labels in the array will be dispatched to that runner.

**Failure recovery:**
- A failed step stops subsequent steps in the same job unless `if: always()` or `if: failure()` overrides this. Design cleanup steps with `if: always()` so they run even when earlier steps fail.
- `needs:` job dependency: if a dependency job fails, the dependent job is skipped by default. Use `if: always()` on the dependent job to make it run regardless — useful for notification jobs.
- GitHub UI allows re-running only failed jobs. Jobs that passed do not re-run, and their artifacts persist, allowing the re-run to pick up where it left off.

**Caching strategies:**
- No built-in caching between jobs unless explicitly configured. Each runner starts fresh. Use `actions/cache` or built-in cache in language setup actions (`setup-node cache: npm`) to persist dependencies.
- Artifacts (`upload-artifact` / `download-artifact`) are the correct mechanism for passing binary files between jobs. Job outputs (`GITHUB_OUTPUT`) are for small string values only — not binaries.

**Security boundaries:**
- `GITHUB_TOKEN` permissions can be restricted at the workflow or job level. Restrict to the minimum needed: a lint job only needs `contents: read`, not `packages: write`.
- Secrets are available to all jobs in a workflow by default, but only within the repository that owns them. Environment-scoped secrets (under an environment like `production`) require the job to target that environment and pass any protection rules (approvals, branch checks).

```
GitHub Actions Interview — Medium
├── Authentication & Security
│   ├── Q6 — OIDC: JWT from GitHub → IAM trust → short-lived token (no static creds)
│   ├── Q10 — Secrets handling: environment protection, OIDC preferred, mask dynamic values
│   └── Q15 — Fork permissions: pull_request = no secrets, pull_request_target = full access
├── Reusable Workflows
│   ├── Q7 — uses: org/repo/.github/workflows/build.yml@main
│   ├── Q7 — inputs: / secrets: / outputs: blocks
│   └── Q7 — secrets: inherit vs explicit passing
├── Matrix Strategy
│   ├── Q8 — matrix: os × language = parallel job grid
│   ├── Q8 — fail-fast: false, max-parallel limit
│   └── Q13 — Dynamic matrix: fromJSON from prior job output
├── Caching
│   └── Q9 — actions/cache: hashFiles key, restore-keys fallback, branch scope
├── Triggers & Events
│   └── Q11 — pull_request vs pull_request_target: permissions/security boundary
├── Paved Road CI/CD
│   └── Q12 — Reusable workflows as golden paths: org standardization
├── Secrets vs Variables
│   └── Q14 — secrets: encrypted, masked / vars: non-secret, readable in logs
├── Pipeline Control
│   ├── Q15 — Prevent bot commit triggers: github.actor != 'github-actions[bot]'
│   └── Q16 — Rollback: helm rollback, kubectl rollout undo
└── Composite vs Reusable
    ├── Composite — encapsulates steps, used within a job
    └── Reusable workflow — encapsulates jobs, called as a job
```

### First Principles

- OIDC solves the credential bootstrap problem. To get AWS credentials, you previously needed... AWS credentials. OIDC breaks this circularity: the trust is established by configuration (IAM trust policy), not by a shared secret.
- Reusable workflows (workflow_call) are the GitHub Actions equivalent of Jenkins Shared Libraries at the job level. A platform team publishes them; product teams call them. The platform team controls the mandatory security steps.
- Matrix strategy is declarative parallel scaling. You declare the axes (OS, language version, region); GitHub Actions generates the cross-product of jobs and runs them simultaneously. No manual job duplication.
- `secrets: inherit` in a reusable workflow call passes ALL caller secrets to the called workflow. This is convenient but violates least privilege — the called workflow gets access to secrets it may not need. Explicit secret passing is safer.
- Dynamic matrix (fromJSON from a prior job) enables "build only what changed" patterns: a detect-changes job outputs a JSON array of changed services, and the build job creates one matrix entry per changed service.

## Medium

**6. How does OIDC authentication work in GitHub Actions and why is it preferred over long-lived secrets?**

OIDC allows GitHub Actions to request short-lived tokens from a cloud provider (AWS, Azure, GCP) without storing any static credentials in the repository. The CI job presents a JWT token signed by GitHub's OIDC provider, and the cloud IAM service verifies it against a pre-configured trust relationship, issuing a short-lived access token. Benefits: no secrets to rotate or leak, tokens expire automatically within minutes, access is scoped to the specific repository and branch by claims embedded in the JWT.

**7. What is a reusable workflow in GitHub Actions?**

A reusable workflow is a workflow file that can be called from other workflows using `uses: org/repo/.github/workflows/workflow.yml@ref`. The calling workflow passes inputs and secrets; the reusable workflow runs in its own context. Used to share standardized pipeline logic — security scans, build steps, deployment processes — across many repositories without duplication.

**8. How do you handle secrets in GitHub Actions securely?**

Secrets are stored in repository or organization settings and injected into workflow steps as environment variables (`${{ secrets.MY_SECRET }}`). GitHub masks secret values in log output. Best practices:
- For cloud access, prefer OIDC over static secrets — no secrets to store at all.
- Never print secrets with `echo` or pass them between jobs unless strictly necessary.
- Use `environment` protection rules to restrict which branches can access environment-scoped secrets.

**9. What is a matrix strategy in GitHub Actions?**

The `strategy.matrix` key runs a job multiple times with different variable combinations:

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest]
    python: ["3.10", "3.11", "3.12"]
jobs:
  test:
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python }}
```

This produces 6 parallel jobs (2 OS × 3 Python versions). Used for cross-platform and cross-version testing.

**10. How do you cache dependencies in GitHub Actions to speed up workflows?**

Use `actions/cache` with a key derived from a lockfile hash:

```yaml
- uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

On cache hit, the step restores the cached directory; on cache miss, the job runs normally and saves the directory at the end. This eliminates redundant package downloads when dependencies haven't changed.

**11. What is the difference between `pull_request` and `pull_request_target` event triggers?**

`pull_request` runs workflows in the context of the PR's head branch, without access to secrets — this is the safe default for external contributors. `pull_request_target` runs in the context of the base branch and does have access to secrets. Never use `pull_request_target` with code from the forked PR directly — it creates a secret exfiltration risk. Use it only for trusted collaborators or for workflows that don't execute untrusted code (e.g., labeling a PR based on its metadata).

**12. What is "paved road" CI/CD and how do reusable workflows enable it?**

A paved road is a standardized, opinionated CI/CD path that builds in mandatory security, testing, and compliance steps, while letting developers focus on their application. With reusable workflows, the platform team owns a central workflow that includes non-negotiable steps (SAST, SBOM generation, image signing). Teams include the workflow with a single `uses:` line and provide application-specific parameters. The platform team can update all pipelines centrally by updating the shared workflow.

***


**13. How do you implement a dynamic matrix build where the matrix values are generated at runtime?**

Generate the matrix JSON in a prior job and pass it via outputs:

```yaml
jobs:
  compute-matrix:
    runs-on: ubuntu-latest
    outputs:
      matrix: ${{ steps.set.outputs.matrix }}
    steps:
    - id: set
      run: |
        SERVICES=$(ls services/ | jq -R -s -c 'split("\n")[:-1]')
        echo "matrix={\"service\":$SERVICES}" >> $GITHUB_OUTPUT

  test:
    needs: compute-matrix
    strategy:
      matrix: ${{ fromJson(needs.compute-matrix.outputs.matrix) }}
    runs-on: ubuntu-latest
    steps:
    - run: pytest services/${{ matrix.service }}/
```

Useful for monorepos where the list of services changes over time — no manual matrix updates needed.

**14. What is the difference between `secrets` and `vars` in GitHub Actions?**

`secrets` are encrypted at rest and masked in logs — values are never visible after being stored. `vars` (repository/environment variables) are plain-text, visible to anyone with read access to the repo settings. Use `secrets` for credentials, tokens, API keys. Use `vars` for non-sensitive configuration that differs between environments (URLs, feature flags, region names).

Access: `${{ secrets.MY_SECRET }}` and `${{ vars.MY_VAR }}`.

**15. How do you prevent a workflow from being triggered by bot commits?**

```yaml
on:
  push:
    branches: [main]

jobs:
  build:
    if: github.actor != 'dependabot[bot]' && github.actor != 'github-actions[bot]'
```

Or skip at the commit level by including `[skip ci]` in the commit message — GitHub Actions honors this by default.

**16. How do you implement rollback in a GitHub Actions deployment workflow?**

Pattern: deploy and verify, then rollback on failure:

```yaml
- name: Deploy
  id: deploy
  run: helm upgrade --install myapp ./chart --set image.tag=${{ env.IMAGE_TAG }}

- name: Verify
  id: verify
  run: ./scripts/smoke-test.sh
  
- name: Rollback on failure
  if: failure() && steps.deploy.outcome == 'success'
  run: helm rollback myapp
```

For Kubernetes: `kubectl rollout undo deployment/myapp` as the rollback step. The `if: failure()` condition means this step only runs if a previous step failed.

**17. How does GitHub Actions handle workflow permissions in a fork?**

Workflows triggered by `pull_request` from a fork run without access to secrets. The `GITHUB_TOKEN` is read-only. This protects against secret exfiltration from malicious forks. For workflows that need secrets (e.g., to post a comment with test results), use `pull_request_target` combined with an environment protection rule requiring reviewer approval before the job runs.

**18. What are composite actions and when would you use them over reusable workflows?**

| | Composite Action | Reusable Workflow |
|---|---|---|
| Unit | Steps | Jobs |
| Outputs | Step outputs | Job outputs |
| Secrets | Via inputs | Via `secrets:` block |
| Parallelism | Sequential steps | Can have parallel jobs |
| Use case | Encapsulate a sequence of steps | Encapsulate an entire pipeline |

Use composite actions for small reusable step sequences (setup, build, test). Use reusable workflows when you need multiple jobs with dependencies, environments, or matrix builds.

### System Design Perspective

**Pipeline scalability:**
- Reusable workflows (Q7) are the scalability mechanism for org-wide CI/CD governance. One platform team maintains the workflow; 100 product teams call it. Fixes and improvements propagate to all callers immediately when the called workflow is updated.
- Dynamic matrix (Q13) scales to the number of services that changed. In a monorepo with 50 services, only building changed services via fromJSON matrix reduces CI cost by 90%+ on a typical PR.
- `max-parallel` on a matrix limits simultaneous jobs when downstream systems (staging databases, shared environments) cannot handle parallel load — a correctness control, not just resource management.

**Runner/agent architecture trade-offs:**
- GitHub-hosted runners: no ops burden, fresh VM, ephemeral. Limitation: no private VPC access. For workflows that need to talk to internal services, use self-hosted runners in the private network.
- Self-hosted runners with `runs-on: [self-hosted, production]` runner group scoping: only the production environment job can access the production runner group (enforced by GitHub runner group settings). This is an access control boundary.
- ARC (Actions Runner Controller) on K8s gives ephemeral self-hosted runners at scale. Runners register, pick up one job, then self-destruct. No state accumulation, no residual credentials, no shared mutable state between jobs.

**Failure recovery:**
- Rollback (Q16) via `helm rollback` or `kubectl rollout undo` requires the pipeline to know the previous release state. Store the release name and revision as job outputs or in an artifact for the rollback workflow to reference.
- A failed reusable workflow job fails the calling workflow. The calling workflow can handle this with `if: failure()` steps or by wrapping the reusable workflow call in a job with `continue-on-error: true`.

**Caching strategies:**
- `actions/cache` (Q9) is restored at the start of the job and saved at the end (if the save key doesn't already exist). A partial cache hit via `restore-keys` gives a warm start — better than cold, not as fast as exact match.
- Language setup actions (`setup-node`, `setup-python`) with `cache:` key handle cache automatically. Prefer these over manual `actions/cache` for standard dependency directories.

**Security boundaries:**
- OIDC (Q6) scoping via `sub` claim (`repo:org/repo:ref:refs/heads/main`) means only the main branch of the specific repo can assume the production IAM role. Feature branches cannot deploy to production even if someone tries.
- Environment protection rules (required reviewers, wait timers, deployment branches) add a human approval layer between the automated pipeline and the production deployment. The environment secrets are also only available after approval.

---
description: Hard interview questions for GitHub Actions — self-hosted runners, OIDC, security, and enterprise governance.
---

```
GitHub Actions Interview — Hard
├── Security & Secret Management
│   ├── Q14 — Secret leakage prevention: OIDC, fork policy, gitleaks, detect-secrets
│   └── Q18 — Attack vectors: script injection, malicious action, pull_request_target, PPE, token over-permission
├── Enterprise Architecture
│   ├── Q15 — Multi-region 99.99% pipeline: Cosign, Flagger canary, automated rollback, immutable digests
│   └── Q16 — Enterprise governance: reusable workflows as golden paths, Required Workflows, OIDC scoping
├── Self-Hosted Runners
│   └── Q17 — ARC architecture: network isolation, ephemeral pods, runner groups, audit, image hardening, autoscaling
├── OIDC Deep Dive
│   └── Q19 — JWT claims: iss, sub, repository, ref, job_workflow_ref, environment
│       ├── AWS trust policy: StringEquals sub + aud
│       └── Scoping: environment-specific, workflow-specific, repo-wide
└── Monorepo CI
    └── Q20 — Selective CI: paths-filter, conditional jobs, dynamic matrix fromJSON, Nx affected
```

### First Principles

- Secret leakage is a defense-in-depth problem. No single control is sufficient: OIDC eliminates static secrets, masking prevents log exposure, fork policy prevents cross-repo access, gitleaks catches accidental commits. Layers compound — an attacker must bypass all of them.
- Multi-region 99.99% availability requires automated progressive delivery. Manual deploys cannot achieve the speed and consistency needed. Canary with automated SLO monitoring (Prometheus → Flagger → rollback) is the only scalable pattern.
- Enterprise governance via Required Workflows means the platform team can enforce mandatory security steps (SAST, SCA, image signing) on every PR in the org without relying on individual teams to include them. Teams cannot opt out.
- Self-hosted ARC runners solve the "runner trust" problem: ephemeral pods that self-destruct after each job mean a compromised job cannot contaminate the next job's runner. The runner is destroyed before any attacker can establish persistence.
- OIDC `job_workflow_ref` claim is the most granular scoping option. Rather than "any job in repo X" being able to assume a production role, only "jobs running the specific deploy.yml workflow in repo X" can. A compromised test workflow cannot assume production credentials.

## Hard

**14. How do you design a pipeline that prevents secret leakage across branches and forks?**

Defense in depth:

- **OIDC for cloud auth:** No static secrets in CI at all — tokens generated per-job using OIDC, expire after the job.
- **Secret masking:** All secrets registered in the CI system are automatically masked in logs. But build artifacts may still contain secrets if code dumps environment variables.
- **Fork policy:** GitHub Actions secrets are never available in `pull_request` workflows from forks. Use `pull_request_target` only for trusted collaborators; require approval for first-time contributors via the "Require approval for all outside collaborators" setting.
- **Pre-commit hooks:** `detect-secrets` or `truffleHog` scan staged changes before commit.
- **Post-commit scanning:** Gitleaks runs in CI on every PR, scanning the full diff and commit history.

**15. Design a CI/CD pipeline for a mission-critical multi-region application with 99.99% uptime requirements.**

1. **Build:** On merge to `main`, build a versioned Docker image, run unit + integration + performance tests. Sign the image with Cosign.
2. **Staging:** Deploy to a production-like staging environment. Run E2E and smoke tests.
3. **Canary — Region 1:** Deploy to the first production region, routing 1% of traffic to the new version via Flagger + Istio VirtualService weights. Monitor P99 latency and error rate SLOs for a set period. Promote: 10% → 50% → 100%.
4. **Canary — Region 2:** Repeat the canary process in the second region after Region 1 is fully promoted and stable.
5. **Automated rollback:** If any SLO threshold is breached during canary (Prometheus query in a GitHub Actions step using `gh workflow run rollback.yml`), automatically revert traffic routing and alert on-call via PagerDuty.
6. **Artifact immutability:** All deployment manifests reference the image by immutable digest, not a mutable tag. The same image promoted through environments — never rebuilt.

**16. How do you govern a GitHub Actions environment for hundreds of teams at scale?**

1. **Reusable workflows as golden paths:** Platform team owns centralized workflows with mandatory security steps (SAST, SCA, image signing). Teams consume via `uses:`, cannot bypass the steps.
2. **Required workflows (Organization-level):** GitHub Enterprise supports Required Workflows — they run on every PR in the organization regardless of what the repo's own workflows do.
3. **Environment protection rules:** Production environments require reviewer approval, specific branches, and have deployment wait times.
4. **OIDC scoping:** IAM role trust policies restrict access to specific repository names and ref patterns (`repo:org/service-a:ref:refs/heads/main`).
5. **Secret scanning + push protection:** Enabled at the org level to block secrets from being committed.

**17. How do you architect self-hosted GitHub Actions runners for an enterprise with compliance requirements?**

**Runner architecture for regulated environments:**

1. **Network isolation:** Runners in a private VPC/VNET with no direct internet access. Egress only through a proxy allowlist or VPC endpoints for AWS services.
2. **Ephemeral runners:** Use `actions-runner-controller` (ARC) on Kubernetes. Each job spawns a fresh pod; the runner registers, executes the job, and self-destructs. No runner state persists between jobs — eliminates supply chain risk from runner compromise.
3. **Runner groups:** Separate runner groups for different environments (`production-runners` vs `staging-runners`). Production runners have access to production secrets; dev runners are sandboxed.
4. **Audit:** All runner activity logged to a SIEM via CloudTrail (if on AWS) and GitHub's audit log API.
5. **Image hardening:** Base runner images built from a trusted registry, scanned with Trivy, signed with Cosign. Runner pods run as non-root with minimal capabilities.
6. **Autoscaling:** ARC scales runner pods based on queued workflows — 0 pods when idle (cost-efficient), scale to N on demand.

**18. What are GitHub Actions security attack vectors and how do you mitigate each?**

| Attack Vector | Description | Mitigation |
|:---|:---|:---|
| **Script injection** | `${{ github.event.pull_request.title }}` in `run:` is vulnerable to arbitrary code in PR titles | Always use `env` vars: `env: PR_TITLE: ${{ ... }}` then `echo "$PR_TITLE"` |
| **Malicious action** | Third-party action updated to exfiltrate secrets | Pin all actions to commit SHA, not tags |
| **`pull_request_target` abuse** | Runs with base repo permissions; can access secrets from fork PRs | Never checkout untrusted code in `pull_request_target` |
| **Poisoned pipeline execution (PPE)** | Attacker modifies workflow file in a branch | Protect default branch; require PR reviews for workflow file changes |
| **Token over-permission** | GITHUB_TOKEN has too many permissions | Set `permissions: read-all` at workflow level; grant minimal per-job |
| **Secrets in logs** | Secrets printed to stdout in debug mode | Use `add-mask` for dynamic secrets; never print env vars directly |

**19. How does the GitHub Actions OIDC token work internally and what are the scoping options?**

When a job runs with `id-token: write` permission, GitHub's OIDC provider issues a JWT token for that job. The token contains claims:

```json
{
  "iss": "https://token.actions.githubusercontent.com",
  "sub": "repo:org/repo:ref:refs/heads/main",
  "repository": "org/repo",
  "ref": "refs/heads/main",
  "job_workflow_ref": "org/repo/.github/workflows/deploy.yml@refs/heads/main",
  "environment": "production"
}
```

The AWS IAM role trust policy can match on any of these claims:
```json
"Condition": {
  "StringEquals": {
    "token.actions.githubusercontent.com:sub": "repo:org/repo:ref:refs/heads/main",
    "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
  }
}
```

**Scoping strategies:**
- Most specific: `sub = repo:org/repo:environment:production` — only production environment jobs
- Broad: `sub = repo:org/*` — any repo in the org (too broad)
- By workflow: `job_workflow_ref` claim — only specific workflow files can assume the role

**20. How do you implement GitHub Actions for a monorepo with selective CI (only build what changed)?**

```yaml
# Step 1: Detect changed paths
- uses: dorny/paths-filter@v3
  id: changes
  with:
    filters: |
      frontend:
        - 'packages/frontend/**'
        - 'packages/shared/**'
      backend:
        - 'packages/backend/**'
        - 'packages/shared/**'

# Step 2: Conditionally run jobs
jobs:
  test-frontend:
    needs: detect-changes
    if: needs.detect-changes.outputs.frontend == 'true'
    ...

  test-backend:
    needs: detect-changes
    if: needs.detect-changes.outputs.backend == 'true'
    ...

# Step 3: Matrix for building only changed services
build-services:
  strategy:
    matrix:
      service: ${{ fromJSON(needs.detect-changes.outputs.changed-services) }}
```

Advanced: use Nx affected commands (`nx affected:test`) which understand project dependency graphs — if shared library changes, automatically test all downstream services.
