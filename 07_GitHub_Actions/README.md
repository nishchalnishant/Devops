# GitHub Actions

```
GitHub Actions
├── Core Model
│   ├── Workflow — YAML in .github/workflows/, triggered by events
│   ├── Job — group of steps on one runner, parallel by default
│   ├── Step — individual task: uses: (action) or run: (shell)
│   └── Action — reusable automation unit (composite/JS/Docker)
├── Triggers (on:)
│   ├── push / pull_request — code events
│   ├── pull_request_target — PR with base repo permissions (dangerous)
│   ├── schedule — cron
│   ├── workflow_dispatch — manual trigger
│   ├── workflow_call — reusable workflow trigger
│   ├── release — GitHub Release events
│   ├── repository_dispatch — external API call
│   └── workflow_run — after another workflow completes
├── Runners
│   ├── GitHub-hosted — ubuntu, windows, macOS, larger runners
│   ├── Self-hosted — on-prem, private VPC, custom hardware
│   └── ARC — Actions Runner Controller on Kubernetes (ephemeral pods)
├── Key Concepts
│   ├── Context — ${{ github.sha }}, ${{ secrets.* }}, ${{ needs.* }}
│   ├── Expression — ${{ env.MY_VAR }}, functions: hashFiles, fromJSON
│   ├── OIDC — JWT from GitHub → AWS/Azure/GCP IAM (no static secrets)
│   └── Reusable workflow — uses: org/repo/.github/workflows/build.yml@main
├── Security
│   ├── Minimal permissions — principle of least privilege
│   ├── SHA pinning — actions pinned to commit hash not mutable tag
│   ├── Script injection — always use env vars, never interpolate in run:
│   └── Fork policy — secrets unavailable in pull_request from forks
├── Interview Focus
│   ├── Easy — workflow structure, triggers, jobs vs steps, secrets, artifacts
│   ├── Medium — reusable workflows, OIDC, caching, matrix, environments
│   └── Hard — ARC architecture, enterprise governance, attack vectors, monorepo CI
└── When to Use
    ├── GHA — code on GitHub, tight PR integration, OIDC, reusable workflows
    ├── GitLab CI — built-in SAST/DAST/SCA, MR integration
    ├── Jenkins — complex shared libraries, on-prem, existing investment
    └── Tekton/Argo — K8s-native, complex DAG task graphs
```

## First Principles

- CI/CD must live where the code lives. A separate CI server creates friction: separate authentication, separate configuration, separate failure domain. GitHub Actions is native — the pipeline and the code share the same repo, the same PR, the same auth.
- Every commit is an event. Events in the repo should automatically trigger work. The `on:` block maps repo events to pipeline executions — this is push-based automation rather than polling.
- Reusable units of work prevent duplication. A "build Docker image" step written in 50 workflows creates 50 places to update. Actions (composite, JavaScript, Docker) let you write it once and use it everywhere.
- Secrets must never be in code. GitHub's encrypted secrets store injects values at runtime into the runner's environment, masked from logs, unavailable in fork PRs. The secret never touches the repository.
- Keyless cloud auth (OIDC) eliminates the worst class of secret: long-lived cloud credentials. GitHub issues a short-lived JWT per job; the cloud provider validates the JWT claims against an IAM trust policy. No key to leak, no key to rotate.
- Runners are ephemeral by design. GitHub-hosted runners are fresh VMs per job. Self-hosted runners should be configured the same way (especially ARC ephemeral runners) to prevent state accumulation between jobs.

GitHub Actions is the native CI/CD and automation platform built directly into GitHub. Workflows are YAML files stored in `.github/workflows/` that are triggered by repository events and run on GitHub-hosted or self-hosted runners.

***

## What Is in This Module

| File | Purpose |
|:---|:---|
| `notes/notes.md` | Core concepts, OIDC, reusable workflows, matrix strategy, composite actions |
| `cheatsheet.md` | Quick-reference YAML syntax, contexts, expressions, security hardening |
| `tips-and-tricks.md` | Production gotchas, OIDC internals, monorepo CI, attack vector table |
| `interview.md` | Consolidated Interview Questions: Easy, Medium, and Hard levels |
| `scenarios.md` | Real-world troubleshooting scenarios |

***

## Core Architecture

```
GitHub Repository
    │
    └── .github/workflows/ci.yml ──────────► Workflow (triggered by event)
                                                    │
                                             ┌──────┴──────┐
                                             │             │
                                           Job A         Job B
                                        (build)        (lint)
                                        runs on        runs on
                                        ubuntu-24.04   ubuntu-24.04
                                             │
                                         ┌───┴───┐
                                         │       │
                                      Step 1  Step 2
                                      (uses:)  (run:)
```

**Parallelism model:**
- Jobs in the same workflow run **in parallel** by default
- Use `needs: [job-name]` to create sequential dependencies
- Steps within a job run **sequentially**

***

## Key Concepts Reference

| Concept | Description | Example |
|:---|:---|:---|
| **Workflow** | YAML file defining automation, triggered by events | `.github/workflows/ci.yml` |
| **Job** | Group of steps running on the same runner | `jobs: build:` |
| **Step** | Individual task within a job | `- uses: actions/checkout@v4` |
| **Action** | Reusable automation unit | `uses: actions/setup-python@v5` |
| **Runner** | Machine executing jobs | `runs-on: ubuntu-24.04` |
| **Event** | Trigger starting a workflow | `on: push, pull_request, schedule` |
| **Context** | Runtime data objects | `${{ github.sha }}`, `${{ secrets.TOKEN }}` |
| **Expression** | Dynamic value syntax | `${{ env.MY_VAR }}` |
| **OIDC** | Keyless cloud auth via JWT | `id-token: write` + `aws-actions/configure-aws-credentials` |
| **Reusable workflow** | Call one workflow from another | `uses: org/repo/.github/workflows/build.yml@main` |

***

## Interview Focus Areas

| Difficulty | Key Topics |
|:---|:---|
| **Easy** | Workflow structure, triggers, jobs vs steps, runners, secrets vs env vars, artifacts, matrix |
| **Medium** | Reusable workflows, composite actions, OIDC, caching strategies, environments, concurrency |
| **Hard** | Self-hosted runner architecture (ARC), security attack vectors, enterprise governance (Required Workflows), OIDC scoping, monorepo selective CI |

***

## Security Quick Reference

```yaml
# Minimal permissions — principle of least privilege
permissions:
  contents: read    # Only what this workflow actually needs

jobs:
  deploy:
    permissions:
      id-token: write   # OIDC — no stored secrets
      contents: read

# Pin actions to commit SHA (not mutable tags)
- uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2

# Never interpolate untrusted input directly in run:
# BAD:  run: echo "${{ github.event.pull_request.title }}"
# GOOD:
- env:
    PR_TITLE: ${{ github.event.pull_request.title }}
  run: echo "$PR_TITLE"
```

***

## When to Use GitHub Actions vs Alternatives

| Tool | Use When |
|:---|:---|
| **GitHub Actions** | Code on GitHub; tight PR integration; OIDC cloud auth; reusable workflows across org |
| **GitLab CI** | Code on GitLab; need built-in SAST/DAST/SCA; deep MR integration; compliance pipelines |
| **Jenkins** | Complex shared library logic; on-prem hardware; existing Jenkins investment |
| **Tekton / Argo Workflows** | Kubernetes-native pipelines; complex DAG task graphs |
| **ArgoCD / Flux** | Kubernetes GitOps CD (not CI — complementary, not competing) |

## System Design Perspective

**Pipeline scalability:**
- GitHub-hosted runners scale automatically — GitHub provisions new VMs for each job. There is no runner pool to manage. For large organizations, concurrency limits apply per plan (e.g., 20 concurrent jobs on Free, higher on paid).
- Self-hosted runners via ARC (Actions Runner Controller) on Kubernetes scale to zero when idle and to N ephemeral pods under load. `HorizontalRunnerAutoscaler` watches the GitHub API for queued runs and scales runner pods accordingly.
- Matrix strategy multiplies jobs: `python-version: ['3.10', '3.11', '3.12'] × os: [ubuntu, windows]` = 6 parallel jobs. Each job gets its own runner. This is horizontal scaling of CI workloads with no additional configuration.

**Agent/runner architecture trade-offs:**

| Runner Type | Pros | Cons |
|:---|:---|:---|
| GitHub-hosted | Zero management, fresh VM, multiple OS | No access to private VPC, egress costs, concurrency limits |
| Self-hosted persistent | Fast start, private network access | State accumulation, security risk, management overhead |
| Self-hosted ARC ephemeral | Clean per job, K8s-native, auto-scales | Requires K8s cluster, pod startup latency |
| Larger GitHub-hosted | More CPU/memory (ubuntu-latest-16-cores) | Higher per-minute cost |

**Failure recovery:**
- Workflows are stateless by definition. A failed job can be re-run from the GitHub UI without re-running successful jobs (re-run failed jobs only). Artifacts from the successful jobs persist.
- OIDC token expiry in long-running jobs: use `role-duration-seconds` to extend the assumed-role session, or split the pipeline into multiple jobs that each request their own fresh OIDC token.
- `concurrency: cancel-in-progress: false` for production deploys ensures a deployment in progress is never cancelled by a new push — preventing a half-deployed state.

**Caching strategies:**
- `actions/cache` with `hashFiles('**/package-lock.json')` as the key creates a deterministic cache that busts when dependencies change. `restore-keys` provides a fallback to a partial match.
- Built-in caching in `setup-node`, `setup-python`, `setup-go` — these actions cache the entire dependency directory automatically when `cache: 'npm'` is specified. Prefer these over manual `actions/cache` for standard languages.
- Cache is scoped per branch and per OS. A cache warm in `main` is available to feature branches via `restore-keys`. Cross-OS cache hits are not possible.

**Security boundaries:**
- `permissions: {}` (empty object) disables all GITHUB_TOKEN permissions. Start from zero and add only what the specific job needs (`contents: read`, `id-token: write`).
- Fork PRs never have access to secrets. `pull_request` from a fork runs with read-only GITHUB_TOKEN and no secrets. This is a non-negotiable GitHub security boundary.
- OIDC scoping via `job_workflow_ref` claim: an IAM role can be restricted to only the specific workflow file (not just the repo) that is allowed to assume it — preventing a compromised workflow from escalating to production credentials.