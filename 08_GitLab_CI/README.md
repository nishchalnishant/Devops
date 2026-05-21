# GitLab CI/CD

```
GitLab CI/CD
├── Core Platform
│   ├── Single platform: code, CI/CD, registry, deployments in one system
│   ├── .gitlab-ci.yml: pipeline defined as code at repo root
│   ├── GitLab Server: coordinator — stores jobs, artifacts, variables, state
│   └── Runners: decoupled executors — poll server for jobs via long-polling
│
├── Pipeline Structure
│   ├── stages: ordered execution phases (build → test → security → deploy)
│   ├── jobs: units of work assigned to a stage; parallel within same stage
│   ├── workflow: controls which events create a pipeline at all
│   ├── default: global defaults applied to all jobs
│   └── DAG (needs:): bypasses stage order — job starts when deps are ready
│
├── Job Keywords
│   ├── rules: conditional execution (if, changes, when) — top-down match
│   ├── only/except: legacy; cannot mix with rules
│   ├── artifacts: files passed between jobs in same pipeline (stored on server)
│   ├── cache: deps persisted across pipeline runs (stored on runner or S3)
│   ├── services: sidecar containers (postgres, redis)
│   ├── needs: DAG dependency list — skip stage ordering
│   ├── when: always | on_success | on_failure | manual | never
│   ├── retry: max retries + trigger conditions
│   ├── timeout: per-job override
│   └── interruptible: allow newer pipeline to cancel this one
│
├── Runners
│   ├── Types: shared (GitLab-managed) | group | project-specific
│   ├── Executors
│   │   ├── docker: fresh container per job — most common
│   │   ├── kubernetes: pod per job — ephemeral, cloud-native
│   │   ├── shell: runs on host — fast but no isolation
│   │   └── custom: user-defined provisioning
│   ├── config.toml: concurrent, image, privileged, cache settings
│   ├── Tags: route jobs to specific runners
│   └── Autoscaling: K8s executor (node autoscaler) or EC2 autoscale
│
├── Variables & Secrets
│   ├── Predefined: CI_COMMIT_SHA, CI_PIPELINE_SOURCE, CI_REGISTRY_IMAGE, …
│   ├── Scopes: instance → group → project → environment-scoped
│   ├── Protected: only on protected branches/tags
│   ├── Masked: redacted from logs (≥8 chars, no whitespace)
│   ├── File-type: content written to temp file; var = path
│   └── Precedence: trigger > job-level > pipeline-level > project > group > instance
│
├── Templates & Reuse
│   ├── include: local | project | template | remote
│   ├── extends: inherit job config within same file
│   ├── CI Components (GitLab 16.x): versioned, typed-input, catalogued
│   └── Parent-child pipelines: trigger:include: + strategy:depend
│
├── Environments & Deployments
│   ├── environment: tracks deployments, DORA metrics, deploy history
│   ├── Protected environments: require approvers for production
│   ├── when:manual: human gate before deploy proceeds
│   ├── on_stop: cleanup job when environment is stopped
│   └── Review Apps: ephemeral env per MR, auto_stop_in
│
├── Security Scanning (Auto DevOps)
│   ├── SAST: source code static analysis (Semgrep, Bandit, …)
│   ├── Secret Detection: Gitleaks on every diff
│   ├── Dependency Scanning: SCA — known CVEs in libraries
│   ├── Container Scanning: Trivy/Grype against built image
│   └── DAST: runtime scan against deployed staging URL
│
├── Multi-Project & Monorepo
│   ├── trigger:project: kick off pipeline in another repo
│   ├── rules:changes: run job only when specific paths change
│   ├── Dynamic child pipelines: generate YAML at runtime via artifact
│   └── strategy:depend: parent waits for child pipeline result
│
├── Container Registry (Built-in)
│   ├── CI_REGISTRY_IMAGE: auto-set to full image path
│   ├── CI_JOB_TOKEN: no-rotation auth for same-project registry
│   └── Dependency Proxy: pull-through cache for Docker Hub (rate limit fix)
│
└── Enterprise Patterns
    ├── Compliance Pipelines: enforce mandatory stages across all projects
    ├── DORA metrics: deployment frequency, lead time, CFR, MTTR
    ├── Merge Trains: ordered MR queue — prevents green-then-broken merges
    └── GitLab CI Components Catalog: discoverable, versioned shared components
```

## First Principles

- Code, CI, registry, and deployment tracking in one platform removes tool sprawl — no Jenkins + external registry + separate secret manager wiring.
- Pipelines defined as `.gitlab-ci.yml` give code-first pipeline management: pipeline changes go through review like any other code change.
- Runners are decoupled executors — they poll for jobs over long-polling. This means you scale runners independently of GitLab and can place them anywhere (on-prem, cloud, K8s).
- Stage ordering is sequential by default; `needs:` breaks this into a DAG so unrelated work runs in parallel — directly cuts pipeline duration.
- `rules:` evaluates top-down, first match wins. `only/except` cannot express the same logic without combining multiple jobs — `rules:` replaces it entirely.
- `artifacts` are correctness guarantees (files passed between jobs in one pipeline); `cache` is a speed optimization (dependencies reused across runs). Never confuse them.
- Environment-scoped variables mean the same pipeline YAML can target staging vs. production secrets without branching logic.
- Parent-child pipelines with `strategy: depend` let monorepos trigger per-service pipelines conditionally — only what changed gets built.

Comprehensive reference for GitLab CI/CD pipelines, runner management, security scanning,
and enterprise-scale pipeline governance.

***

## What Is in This Module

| File | Purpose |
|:---|:---|
| `cheatsheet.md` | `.gitlab-ci.yml` syntax reference, CLI commands, API |
| `interview.md` | Consolidated Interview Questions: Easy, Medium, and Hard levels |
| `scenarios.md` | Real-world troubleshooting scenarios |
| `notes/gitlab-pipeline-architecture.md` | Deep dive into GitLab CI architecture |

***

## Core Concepts Map

```
GitLab Repository
    │
    ├── .gitlab-ci.yml ──────────────────────► Pipeline
    │                                              │
    ├── include: templates ──────────────────►    ├── Stage 1 (build)
    │                                              │       ├── job-a (runner A)
    └── CI/CD Variables ──────────────────────►    │       └── job-b (runner B)
                                                   │
                                                   ├── Stage 2 (test)
                                                   │       └── unit-test
                                                   │
                                                   └── Stage 3 (deploy)
                                                           └── deploy-staging (environment)
```

***

## Interview Focus Areas

| Difficulty | Key Topics |
|:---|:---|
| **Easy** | `.gitlab-ci.yml` structure, runners, stages vs jobs, artifacts vs cache, environments |
| **Medium** | DAG with `needs:`, rules vs only/except, includes, multi-project pipelines, secrets |
| **Hard** | Runner autoscaling (K8s/EC2), compliance governance (500+ teams), Jenkins migration, monorepo selective CI, CI Components |

***

## Key Differentiators from GitHub Actions

| Feature | GitLab CI | GitHub Actions |
|:---|:---|:---|
| **Built-in Container Registry** | Yes — free, included | GitHub Packages (free with limits) |
| **Built-in security scanning** | SAST, DAST, SCA, secret detection built-in | 3rd-party actions required |
| **Self-hosted control** | Full control with GitLab self-managed | GitHub Enterprise |
| **DAG pipelines** | `needs:` keyword | No native DAG — stage-based only |
| **Merge request integration** | Deep (security findings in MR widget) | Check runs only |
| **Compliance frameworks** | GitLab Compliance Pipelines | Required Workflows (Enterprise only) |

***

## Quick Reference — Most Useful Keywords

```yaml
# Conditional execution (modern, preferred)
rules:
  - if: $CI_COMMIT_BRANCH == "main"
  - if: $CI_PIPELINE_SOURCE == "merge_request_event"
  - changes: [src/**/*]

# Skip stage ordering — run as soon as dependencies are ready
needs: [build-frontend]

# Control retry behavior
retry:
  max: 2
  when: [runner_system_failure, stuck_or_timeout_failure]

# Manual deployment gate
when: manual
environment: production

# Import shared templates (DRY pipelines)
include:
  - project: 'platform/ci-templates'
    ref: 'v1.0'
    file: '/templates/docker-build.yml'
  - template: 'Security/SAST.gitlab-ci.yml'
```

***

## System Design Perspective

**Runner autoscaling architecture**

For spiky CI workloads: the Kubernetes executor is the modern approach — a runner manager pod schedules one pod per CI job, and cluster node autoscaling (Karpenter or Cluster Autoscaler) handles capacity. For EC2-based runners, a small always-on manager instance orchestrates spot fleet expansion via `[runners.autoscale]` in `config.toml`. Key tuning knobs: `concurrent` (max parallel jobs per runner), `IdleCount` (0 = no idle capacity, lowest cost but cold-start latency), `IdleScaleFactor` (keep N% of recent peak warm).

**Pipeline caching architecture**

Cache is a distributed systems problem: runner-local cache breaks when jobs land on different runners; distributed cache (S3 backend via `[runners.cache]` in config.toml) solves this at the cost of network round-trips. Key-based invalidation (`key.files: [package-lock.json]`) ensures cache busts only on dependency changes. `policy: pull` on test jobs (read-only) reduces write contention; only build jobs use `pull-push`.

**Multi-project pipeline topology**

Three patterns compose to handle any org structure: (1) trigger-by-project kicks a pipeline in a separate repo; (2) parent-child with `trigger:include:local` runs sibling pipelines within the same repo; (3) dynamic child pipelines generate YAML at runtime (a script reads changed paths, emits a YAML artifact, `trigger:include:artifact` executes it). `strategy: depend` makes all three synchronous from the parent's perspective — parent status reflects child outcome.

**Compliance pipeline enforcement**

At 500+ teams, push-based template adoption fails. GitLab Compliance Pipelines (configured at the group level) inject mandatory stages into every project's pipeline unconditionally — teams cannot opt out or override compliance jobs. Combined with protected environments (required approvers list, prevent pushes from unprotected branches), this creates a two-layer gate: policy enforced at the pipeline level, approval enforced at the deployment level.

**Security scanning pipeline design**

Layer scans by speed and blocking severity: SAST and Secret Detection run first (fast, no infra required, block on new critical findings); Dependency Scanning runs in parallel (SCA, blocks on CVSS ≥ 9.0); Container Scanning runs after image build (Trivy, blocks on OS package CVEs); DAST runs last against a live staging environment (slowest, no block by default — findings go to MR widget for review). GitLab Security Policies (MR approval policies) require security team sign-off when new critical findings appear — this is enforced even if the CI job itself passes.

**Merge Train mechanics**

A Merge Train queues MRs in order and tests each one combined with all queued MRs ahead of it. If MR-A and MR-B are both queued, the train tests [main+A] then [main+A+B] simultaneously. If [main+A] fails, MR-A is dropped and MR-B is retested against main alone. This eliminates the "passes in isolation, breaks main" problem but increases pipeline consumption proportionally to queue depth. Suitable for high-volume teams on a shared main branch.