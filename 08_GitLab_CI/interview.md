# GitLab CI — Interview Prep

---
description: Easy interview questions for GitLab CI, pipelines, runners, and merge request workflows.
---

```
GitLab CI Easy Interview Topics
├── .gitlab-ci.yml
│   ├── YAML file at repo root — GitLab auto-detects it on every push
│   ├── Defines stages, jobs, images, scripts
│   └── No file = no pipeline shown for the repo
│
├── GitLab Runner
│   ├── Agent that executes CI/CD jobs
│   ├── Types: shared (GitLab-managed) | group | project-specific
│   └── Executors: shell | docker | kubernetes | ssh | virtualbox
│
├── Stages vs Jobs
│   ├── stages: ordered list of pipeline phases
│   ├── jobs: actual work units — each assigned to a stage
│   ├── Jobs in same stage run in parallel
│   └── needs: keyword bypasses stage ordering (DAG)
│
├── Pipeline Triggers
│   ├── git push, MR open/update, schedule (cron), manual, API call
│   └── workflow: keyword gates when a pipeline is created at all
│
├── only/except vs rules
│   ├── only/except: legacy — branch/tag/event conditions, cannot mix with rules
│   └── rules: modern — if / changes / when, top-down first match wins
│
├── Environments
│   ├── Named deployment target (staging, production)
│   ├── Tracks deployment history, DORA metrics, current version
│   ├── Protected environments: require designated approvers
│   └── Environment-scoped variables: secrets tied to specific environment
│
├── Artifacts vs Cache
│   ├── artifacts: files produced by a job, passed to downstream jobs in same pipeline
│   ├── cache: dependencies persisted across pipeline runs for speed
│   └── Never confuse them: artifacts = correctness; cache = performance
│
├── MR Pipeline vs Branch Pipeline
│   ├── Branch pipeline: runs on every push to a branch
│   ├── MR pipeline: runs in context of a Merge Request, access to MR variables
│   └── Deduplicate with workflow: rules + CI_PIPELINE_SOURCE == "merge_request_event"
│
├── CI/CD Variables
│   ├── Group | project | environment-scoped | file-type
│   ├── Masked: never shown in logs (≥8 chars, no whitespace)
│   ├── Protected: only on protected branches/tags
│   └── File-type: content saved to temp file; variable = file path
│
├── include
│   ├── Splits pipeline across multiple YAML files or imports shared templates
│   └── Types: local | project | template | remote
│
└── Manual Jobs
    ├── when: manual — job shows play button in UI, does not run automatically
    └── allow_failure: true — pipeline continues without waiting for the manual job
```

### First Principles

- A pipeline is a description of work, not the work itself. `.gitlab-ci.yml` is read by GitLab Server; runners perform the actual execution — separation of scheduling from execution is why runners can be anywhere.
- Stages provide ordered correctness (test cannot run before build). Jobs within a stage provide parallel throughput. `needs:` breaks stage ordering when the stage boundary itself adds no value.
- `only/except` is additive exclusion logic — hard to reason about when conditions interact. `rules:` is a match list — first rule that matches determines behavior. Ordered, explicit, composable.
- Artifacts are a delivery mechanism between jobs. Cache is a warming mechanism between runs. Both are keyed storage — artifacts by pipeline/job, cache by a developer-defined key.
- Variables scoped to environments solve the `if branch == main then use PROD_KEY else use STAGING_KEY` anti-pattern. The pipeline YAML stays environment-agnostic; GitLab injects the right secrets based on `environment: name:`.
- A manual job is an explicit human checkpoint in the automation. It does not pause the runner — it pauses the pipeline until a human acts.

## Easy

**1. What is `.gitlab-ci.yml`?**

`.gitlab-ci.yml` is a YAML file at the root of a GitLab repository that defines the CI/CD pipeline. GitLab automatically detects and runs this file on every push. It specifies stages, jobs within each stage, the Docker image to use, and the scripts to execute. If the file doesn't exist, GitLab shows no pipeline for the repository.

**2. What is a GitLab Runner?**

A GitLab Runner is the agent that executes CI/CD jobs. Runners can be shared (managed by GitLab, available to all projects), group-level, or project-specific. Each runner has an executor that determines how jobs run: `shell`, `docker`, `kubernetes`, `ssh`, or `virtualbox`. The `docker` executor runs each job in a fresh container, ensuring isolation between jobs.

**3. What is the difference between `stages` and `jobs` in GitLab CI?**

`stages` defines the ordered list of pipeline phases (e.g., `build`, `test`, `deploy`). `jobs` are the actual units of work — each job belongs to a stage and runs its `script`. Jobs in the same stage run in parallel by default. Jobs in later stages wait for all jobs in previous stages to succeed before running. You can bypass this ordering with `needs:` (DAG pipelines).

**4. What is a pipeline in GitLab and what triggers one?**

A pipeline is a collection of jobs organized into stages. Triggers include: a `git push`, a merge request being opened or updated, a schedule (`cron`-style in CI/CD → Schedules), a manual trigger (`workflow_dispatch` equivalent: a `when: manual` job), or an API call. The `workflow` keyword controls when a pipeline is created at all (e.g., only for MRs or `main` branch).

**5. What does `only/except` do and how does it differ from `rules`?**

`only/except` is the legacy syntax for controlling which branches/tags/events trigger a job. `rules` is the modern replacement — it's more expressive, supports conditions with `if`, `changes`, and `when`, and allows mixing allow/skip logic in a single block. `rules` processes top-down and applies the first matching rule. `only/except` cannot be mixed with `rules` in the same job.

**6. What is a GitLab environment?**

An environment in GitLab represents a deployment target (e.g., `staging`, `production`). When a job declares `environment: staging`, GitLab tracks deployments to that environment — showing a deployment history, the current deployed version, and a link to the environment URL. Protected environments require specific approvers to trigger deployments. Environments also gate secret variables — some CI/CD variables are scoped to specific environments.

**7. What is `artifacts` in GitLab CI and what are they used for?**

Artifacts are files or directories that a job produces and saves to GitLab. Subsequent jobs in the same pipeline can download these artifacts. Example: a build job compiles a binary and saves it as an artifact; the deploy job downloads the binary and pushes it. Artifacts are different from cache — artifacts pass data between jobs, cache speeds up builds by persisting downloaded dependencies.

**8. What is `cache` in GitLab CI?**

Cache saves directories (e.g., `node_modules/`, `.pip-cache/`) to the runner's storage so subsequent pipeline runs don't need to re-download dependencies. Cache is keyed (by branch, commit, or file hash) and has a TTL. Unlike artifacts (job-to-job in one pipeline), cache persists across multiple pipeline runs. Cache is a performance optimization; artifacts are for data handoff between jobs.

**9. What is a merge request pipeline vs a branch pipeline?**

A **branch pipeline** runs on every push to a branch. A **merge request pipeline** runs specifically in the context of a Merge Request — it has access to MR-specific variables (`$CI_MERGE_REQUEST_ID`, `$CI_MERGE_REQUEST_SOURCE_BRANCH_NAME`) and appears in the MR interface. GitLab allows you to deduplicate — run only the MR pipeline, not both — using the `workflow: rules` pattern with `$CI_PIPELINE_SOURCE == "merge_request_event"`.

**10. What are GitLab CI/CD variables and the different scopes?**

Variables are key-value pairs available in job scripts as environment variables. Scopes:
- **Group-level:** Available to all projects in the group.
- **Project-level:** Available to jobs in that project.
- **Environment-scoped:** Only available when the job targets a specific environment (e.g., `PROD_DB_URL` only in `environment: production` jobs).
- **File variables:** Content is saved to a temp file; the variable contains the file path — useful for certificates and config files.
- **Masked:** Never shown in job logs. **Protected:** Only available on protected branches/tags.

**11. What is a GitLab CI include and why is it used?**

`include:` allows you to split your pipeline configuration across multiple YAML files or import shared templates:
```yaml
include:
  - local: '.gitlab/ci/test.yml'
  - project: 'platform/ci-templates'
    ref: 'v1.0'
    file: '/templates/docker-build.yml'
  - template: 'Security/SAST.gitlab-ci.yml'
```
This prevents copy-pasting the same pipeline code across 100 repositories. The platform team maintains shared templates; product teams include them with one line.

**12. How do you trigger a manual job in GitLab CI?**

Set `when: manual` on the job. The job appears in the pipeline UI with a play button — it won't run automatically. To allow the pipeline to continue without waiting for the manual job, set `allow_failure: true`. Manual jobs are commonly used for production deployments that require human approval before proceeding.

***

### System Design Perspective

**Runner executor selection**

The executor is the most consequential runner configuration choice. Docker executor: each job starts in a fresh container — strong isolation, reproducible environment, ~10-30 second startup overhead. Shell executor: runs directly on the host — zero startup overhead but state bleeds between jobs (leftover files, installed packages). Kubernetes executor: one pod per job, ephemeral, scales with cluster node autoscaler — the right choice for cloud-native workloads where you want elastic capacity without managing EC2 fleets.

**Pipeline trigger deduplication**

Without workflow rules, a push to a branch that has an open MR creates two pipelines: a branch pipeline and an MR pipeline. This doubles CI consumption. The standard fix:

```yaml
workflow:
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
    - if: $CI_COMMIT_TAG
```

This creates pipelines only for MRs, the default branch, and tags — eliminating duplicate branch pipelines for open MRs.

**Environment variable injection architecture**

Variables flow into the runner process environment. File-type variables are materialized as temp files — the variable value is the file path, not the content. This is critical for PEM certificates, kubeconfig files, and `.env` files that tools expect to read from disk. The runner creates the temp file before the job script runs and deletes it after — no manual `echo "$VAR" > /tmp/cert.pem` needed.

```
GitLab CI Medium Interview Topics
├── Environments & Deployment Tracking
│   ├── environment: name — creates deployment record on every job run
│   ├── Tracks: current deployed commit, history, who deployed, when
│   ├── DORA metrics: deployment frequency, lead time, CFR, MTTR — auto-computed
│   └── environment-scoped variables: same YAML, different secrets per environment
│
├── Approval Gates
│   ├── when: manual — human clicks play in UI to proceed
│   ├── Protected environments: roles allowed to deploy + required approvers
│   └── Audit log: captures approver identity, timestamp, commit
│
├── GitLab vs GitHub Actions Runners
│   ├── GitLab: runners poll GitLab server (long-polling model)
│   ├── GitHub Actions: runners receive jobs via webhook push
│   └── Both support self-hosted for custom hardware / private networks
│
├── Parent-Child Pipelines
│   ├── trigger: include: local: child.yml — child runs in same repo
│   ├── strategy: depend — parent waits for child; mirrors child status
│   └── Use case: monorepo — trigger per-service pipeline only when that service changes
│
├── extends and include (DRY)
│   ├── extends: — inherit job config within same file (image, rules, script)
│   ├── include: project — import templates from central platform repo
│   └── Composable: project-level include + extends for per-job customization
│
├── AutoDevOps
│   ├── Activates when no .gitlab-ci.yml exists or explicitly enabled
│   ├── Auto-detects language, provides default pipeline: build + test + scan + deploy
│   └── Includes: SAST, DAST, dependency scan, container scan, Kubernetes deploy
│
└── Multi-Project Pipelines
    ├── trigger: project: group/repo — downstream pipeline in another project
    ├── branch: main + strategy: depend — synchronous, parent reflects child status
    └── variables: — inject IMAGE_TAG, DEPLOY_ENV into downstream pipeline
```

### First Principles

- Environments give deployments an identity — without them, pipelines are anonymous script executions with no link to what's running where.
- `when: manual` is a human checkpoint modeled in code. The alternative (informal "ask someone to approve in Slack") is invisible in the audit log and can't be enforced.
- Parent-child pipelines decompose monorepo complexity. The root pipeline is a dispatch table; each child is an autonomous service pipeline. `strategy: depend` makes the dispatch table synchronous — failure in any child fails the parent.
- `extends:` is shallow merge (later keys win); `include:` is file concatenation. Use `extends:` for job-level reuse within a file; use `include:` for cross-repo template sharing.
- AutoDevOps is a convention-over-configuration escape hatch. It works when your app follows common patterns; it becomes a constraint when your build process deviates significantly.

## Medium

**8. What is a GitLab Environment and how does it support deployment tracking?**

A GitLab Environment is a named deployment target (`staging`, `production`). Pipelines that deploy to it set `environment: name: production`, creating an audit trail in GitLab's Deployments view. You can see which commit is deployed where, roll back to a previous deployment, require manual approval with `when: manual`, and attach environment-specific variables. It also powers GitLab's DORA metrics dashboard.

**9. How do you implement approval gates in a GitLab CI pipeline?**

Use `when: manual` on a job — a human must click a button in the GitLab UI to allow that stage to proceed:

```yaml
deploy_production:
  stage: deploy
  environment: production
  when: manual
  script:
    - ./deploy.sh production
```

For regulated environments, combine with protected environments and required approvers so only authorized users can promote to production. The audit log captures who approved, when, and what commit was approved.

**10. What is the difference between GitLab Runners and GitHub Actions runners?**

GitLab Runners poll a GitLab instance for jobs. They can be shared across projects or dedicated to a group or project. GitHub Actions runners receive jobs via a webhook-push model and are registered to a repository or organization. Both support self-hosted options for custom hardware, private network access, or cost control.

**11. How do you implement a parent-child pipeline in GitLab CI?**

A parent pipeline triggers child pipelines using `trigger:` with `include:`:

```yaml
trigger_child:
  trigger:
    include:
      - local: child-pipeline.yml
    strategy: depend
```

`strategy: depend` makes the parent wait for the child to complete and mirrors its status. Used in monorepos to trigger separate pipelines per service only when their code changes.

**12. How do you use `extends` and `include` for DRY pipelines?**

`extends:` inherits configuration from another job in the same file — useful for sharing script blocks, rules, or image definitions. `include:` pulls in external YAML files (local, remote, or from a project template). Together they enable a centralized templates repository that all projects include:

```yaml
include:
  - project: 'platform/ci-templates'
    ref: main
    file: '/templates/docker-build.yml'
```

**13. What is GitLab AutoDevOps?**

AutoDevOps is GitLab's built-in CI/CD configuration that auto-detects the application language and provides a default pipeline including: build (using Heroku buildpacks or Docker), test, code quality scan, SAST, DAST, dependency scanning, container scanning, and deployment to Kubernetes. It activates when no `.gitlab-ci.yml` is present or when explicitly enabled.

**14. How do you handle multi-project pipelines in GitLab?**

Use the `trigger:` keyword with a `project:` reference to start a pipeline in another GitLab project:

```yaml
trigger_downstream:
  trigger:
    project: group/downstream-project
    branch: main
    strategy: depend
```

Used to orchestrate across services — e.g., build a library, then trigger dependent service pipelines automatically.

***

### System Design Perspective

**Pipeline template governance at scale**

For organizations with 50+ projects, copy-paste pipeline YAML becomes a maintenance problem — security scan version upgrades require touching every repo. The solution: a central `platform/ci-templates` project with versioned YAML files. Product teams include a single line: `include: - project: platform/ci-templates ref: v2.1 file: /base.yml`. The platform team cuts a new release tag; teams opt in to upgrades. Compliance Pipelines (group-level setting) go further — they inject jobs unconditionally even if the product team's pipeline would skip them.

**DORA metrics derivation**

GitLab computes DORA metrics from environment data: deployment frequency = count of successful deploy jobs to an environment per time window. Lead time = duration from first commit in the MR to successful production deployment. Change failure rate = % of deployments followed by a rollback or incident-linked deployment within the rollback window. MTTR = average time between a failed deployment and a successful recovery deployment. This requires consistent use of `environment: name: production` in deploy jobs — without it, GitLab has no deployment events to measure.

**Multi-project pipeline token scoping (GitLab 16+)**

Starting GitLab 16.0, `CI_JOB_TOKEN` is scoped to the originating project by default. Cross-project operations (pull artifacts, trigger pipelines, clone repos) require explicit allowlisting in the target project's Settings > CI/CD > Token Access. This is a breaking change from GitLab 15 where the token had broader implicit access. Design pattern: create a dedicated "platform" project that allowlists tokens from all consumer projects, centralizing the permission surface rather than creating a mesh of pairwise allowlists.


---
description: Hard interview questions for GitLab CI architecture, runner scaling, compliance, and enterprise patterns.
---

```
GitLab CI Hard Interview Topics
├── Enterprise Platform Design (500+ teams)
│   ├── Compliance Pipelines: group-level mandatory job injection, cannot be overridden
│   ├── Protected environments: production requires designated approvers
│   ├── DORA metrics: per-project deployment frequency, lead time, CFR, MTTR
│   └── Runner isolation: tags, --security-opt=no-new-privileges, GPU/high-memory tiers
│
├── Jenkins Migration Strategy
│   ├── Categorize 100 pipelines by complexity; identify 5-10 pilots
│   ├── Convert pilots to .gitlab-ci.yml; map Jenkinsfile constructs to GitLab CI equivalents
│   ├── Build include: templates replicating Jenkins Shared Library functions
│   ├── Phased rollout: simplest pipelines first; new projects GitLab CI only
│   └── Decommission: archive Jenkins data after all pipelines migrated and validated
│
├── Security Scanning Pipeline
│   ├── SAST: every MR, source code, results in MR widget
│   ├── SCA / Dependency Scanning: known CVEs; fail on critical severity
│   ├── Container Scanning: Trivy/Grype on built image; block on high/critical OS CVEs
│   ├── Secret Detection: Gitleaks on every push diff
│   ├── DAST: against live staging URL; runtime vulnerability detection
│   └── Policy gates: MR approval policies require security sign-off on new critical findings
│
├── Dependency Proxy
│   ├── Pull-through cache for Docker Hub images
│   ├── Pull from registry.gitlab.com/group/dependency_proxy/containers/<image>
│   └── Benefits: no Docker Hub rate limit failures, reduced egress, faster job startup
│
├── Runner Autoscaling
│   ├── Kubernetes executor: runner manager pod, one pod per CI job, cluster node autoscaler
│   │   ├── concurrent in config.toml: max parallel jobs
│   │   └── K8s pod resource requests/limits per job tag
│   └── EC2 autoscaling: runner manager on small EC2, [runners.autoscale] config
│       ├── IdleCount=0: no idle instances (cost-efficient, cold-start tradeoff)
│       └── IdleScaleFactor: keep N% of recent peak warm
│
├── DAG Pipelines (needs:)
│   ├── Default: stage N waits for all jobs in stage N-1
│   ├── needs: — job starts when specific deps are ready, ignores stage boundaries
│   └── Impact: 45-minute sequential pipeline → 15-minute parallel pipeline
│
├── CI Components (GitLab 16.x)
│   ├── Versioned: semantic version tags, consumer pins to ~1.0 or exact
│   ├── Discoverable: GitLab CI/CD Catalog — searchable by all users
│   ├── Input-parameterized: typed inputs (string, boolean, number) with validation
│   └── include: component: gitlab.com/org/catalog/sast@v1.2.0 + inputs:
│
└── Monorepo Multi-Service CI (50 microservices)
    ├── Root .gitlab-ci.yml: trigger per-service child pipeline on path change
    ├── rules: changes: [services/service-a/**/*] — path-based job filtering
    ├── trigger: include: services/service-a/.gitlab-ci.yml
    └── strategy: depend — parent waits for all triggered child pipelines
```

### First Principles

- Enterprise CI governance is a policy problem, not a pipeline problem. Compliance Pipelines inject mandatory jobs at the group level — teams cannot remove them. This moves security from "encouraged" to "enforced by the platform."
- Jenkins migration is a translation problem compounded by a culture problem. The pipeline syntax converts mechanically; the shared library functions and approval workflows need organizational agreement. Phased migration reduces risk by keeping Jenkins running in parallel until confidence is high.
- Runner autoscaling is a queuing system. The goal is to minimize job wait time (p99 queue depth) while minimizing idle compute cost. `IdleCount=0` minimizes cost; `IdleScaleFactor` balances cost vs. cold-start latency. K8s executor delegates this tradeoff to the cluster autoscaler.
- DAG pipelines convert a linear job chain into a dependency graph. The performance gain is proportional to how much work was previously serialized that had no actual dependency relationship.
- CI Components fix the template sharing problem that `include:` templates only partially solve: components are versioned, discoverable, and typed — consumers can pin versions and validate inputs at YAML parse time rather than at runtime.
- Monorepo CI with path-based triggers means each microservice has its own pipeline, the root pipeline is a dispatcher, and changes to shared libraries propagate correctly by including `shared-libs/**/*` in every service's `changes:` list.

## Hard

**17. How would you design a GitLab CI platform for 500+ development teams with consistent security policies?**

Enterprise GitLab CI architecture:

1. **Pipeline templates:** Disable classic CI and mandate that all pipelines use `extends:` or `include:` to inherit from central templates. Ensure mandatory security scans (credential scanning, SAST, container scanning) run on every pipeline.
2. **GitLab Environments with protected environments:** Require environment declarations for all production deployments. Protected environments restrict which roles can trigger deploys and require designated approvers.
3. **DORA Metrics:** GitLab's built-in DORA metrics (deployment frequency, change failure rate, lead time, MTTR) are tracked automatically per project. Used to measure platform health across teams.
4. **Runner isolation:** Use dedicated GitLab Runners with appropriate tags for different workloads (GPU runners for ML, high-memory for builds). Prevent privilege escalation with `--security-opt=no-new-privileges` on Docker executors.

**18. How do you migrate 100 Jenkins pipelines to GitLab CI?**

A big-bang migration is too risky. Phased approach:

1. **Categorize:** Group the 100 pipelines by complexity and pattern. Identify 5-10 representative pilots.
2. **Pilot:** Convert pilots to `.gitlab-ci.yml`. Create GitLab CI `include:` templates that replicate Jenkins Shared Library functions.
3. **Tooling and documentation:** Build a conversion guide mapping `Jenkinsfile` constructs to GitLab CI equivalents. Run workshops for developers.
4. **Phased rollout:** Onboard teams in waves, simplest pipelines first. New projects start on GitLab CI only.
5. **Decommission:** Archive Jenkins data, shut down servers after all pipelines are migrated and validated.

**19. How do you design a security scanning pipeline that blocks vulnerable code from reaching production?**

Multi-layer approach using GitLab's built-in security features:

1. **SAST:** Runs on every MR, scans source code for vulnerability patterns. Results appear in the MR widget.
2. **SCA / Dependency Scanning:** Detects known CVEs in third-party libraries. Fail the pipeline if a critical severity CVE is found.
3. **Container scanning:** Scans the built Docker image against Trivy or Grype. Blocks promotion if high/critical CVEs present in OS packages.
4. **Secret detection:** Gitleaks scans the diff for committed secrets on every push.
5. **DAST:** Runs against a deployed staging environment for runtime vulnerability detection.
6. **Policy gates:** GitLab Security Policies (MR approval policies) require security team sign-off when scanning reports new critical findings.

**20. What is GitLab's Dependency Proxy and why is it useful in CI pipelines?**

The Dependency Proxy is GitLab's pull-through cache for Docker Hub images. Instead of each CI job pulling `python:3.11` from Docker Hub (subject to rate limits and slow external pulls), jobs pull from `registry.gitlab.com/group/dependency_proxy/containers/python:3.11`. GitLab caches the image internally. Benefits: eliminates Docker Hub rate limit failures in CI, reduces external network egress, and speeds up job startup time.

**21. How do you scale GitLab Runners to handle spiky CI workloads with autoscaling?**

GitLab Runner autoscaling with Docker Machine (legacy) or Kubernetes executor:

**Kubernetes executor (recommended for cloud-native):**
- Runner manager pod runs in K8s. Each CI job spawns a pod using the Kubernetes executor.
- Pod resource requests/limits configured per job tag: `--builds-dir`, `--docker-privileged`, `--cpu-limit`.
- Auto-scaling is handled by the Kubernetes cluster's node autoscaler (Cluster Autoscaler or Karpenter).
- `concurrent` setting in `config.toml` controls max parallel jobs.

**AWS autoscaling with EC2:**
- Runner manager runs on a small always-on EC2 instance.
- `[runners.autoscale]` section configures min/max instances and idle settings.
- `IdleCount=0` means no idle instances (cost-efficient but slower cold start).
- Use `IdleScaleFactor` to keep N% of previous peak capacity warm.

**22. How do GitLab CI DAG pipelines work and what problem do they solve?**

By default, GitLab stages are sequential: all jobs in stage N must finish before stage N+1 starts. With large pipelines, this causes delays — `test-frontend` must wait for `test-backend` even though they're completely independent.

DAG (Directed Acyclic Graph) via `needs:` bypasses stage ordering:
```yaml
test-frontend:
  stage: test
  needs: [build-frontend]     # Starts immediately when build-frontend finishes

deploy-frontend:
  stage: deploy
  needs: [test-frontend]       # No need to wait for test-backend!
```

A job can start as soon as its `needs` are satisfied, regardless of stage. This can dramatically reduce pipeline duration for large monorepo pipelines — from 45 minutes sequential to 15 minutes parallel.

**23. What is a GitLab CI component and how does it improve on `include: template`?**

GitLab CI Components (introduced in GitLab 16.x) are versioned, reusable pipeline building blocks published to the GitLab Catalog. They improve on `include:` templates:
- **Versioned:** Components are versioned with semantic version tags. Consumer projects pin to `~1.0` (minor-compatible) or exact versions.
- **Discoverable:** Published to the GitLab CI/CD Catalog — searchable by all GitLab users.
- **Input-parameterized:** Components accept typed inputs (`string`, `boolean`, `number`) with validation, unlike plain `include:` templates that rely on CI variables.
- **Tested:** Components have their own test pipelines.

```yaml
include:
  - component: gitlab.com/my-org/catalog/sast@v1.2.0
    inputs:
      scanner: semgrep
      severity_threshold: high
```

**24. How do you implement GitLab CI for a multi-project monorepo with 50 microservices?**

Path-based triggering in a monorepo:

```yaml
# .gitlab-ci.yml at root
build-service-A:
  rules:
    - changes:
        - services/service-a/**/*
        - shared-libs/**/*        # Trigger if shared code changes too
  trigger:
    include: services/service-a/.gitlab-ci.yml
    strategy: depend

build-service-B:
  rules:
    - changes:
        - services/service-b/**/*
        - shared-libs/**/*
  trigger:
    include: services/service-b/.gitlab-ci.yml
```

Each service has its own `.gitlab-ci.yml`. The root pipeline conditionally triggers child pipelines based on changed paths. `strategy: depend` makes the parent pipeline wait for child pipeline completion. For 50 services this creates a manageable parent pipeline that only builds what changed.

***

### System Design Perspective

**Runner fleet architecture for heterogeneous workloads**

A single runner pool cannot efficiently serve all workload types. Design a tagged fleet: `docker-standard` (2 vCPU, 4 GB) for test and lint jobs; `docker-build` (8 vCPU, 16 GB) with docker-in-docker for container builds; `k8s-gpu` (GPU nodes) for ML model training; `privileged-false` for untrusted forks. Jobs declare `tags:` to route to the right fleet. The runner manager should have `concurrent` set to the expected peak parallel jobs — setting it too low causes queue buildup even when runners are idle.

**Dynamic child pipeline generation pattern**

For true monorepos with 100+ services, static `rules:changes:` triggers on every service become unwieldy (5000+ lines of root pipeline YAML). The dynamic pattern: a single "dispatch" job runs a script that reads `git diff --name-only` against the target branch, maps changed paths to service names, and emits a `generated-pipeline.yml` as an artifact. The root pipeline then executes `trigger: include: artifact: generated-pipeline.yml`. This keeps the root pipeline small (dispatch job + trigger) regardless of the number of services. The generation script is the only place that encodes the path-to-service mapping.

**Compliance Pipeline architecture**

GitLab Compliance Pipelines are configured at the group level (Compliance Frameworks). Every project in the group inherits a compliance pipeline that runs before and after the project's own pipeline. The compliance pipeline can: enforce SAST must run; enforce container scan results are uploaded; enforce deployment goes through a protected environment gate. Projects cannot disable these jobs or exclude their stages. The compliance pipeline lives in a separate protected repo controlled by the security team — product teams have no write access.

**Merge Train failure isolation**

When a Merge Train entry fails, GitLab resets the train from that MR forward. If MRs A→B→C→D are queued and C fails, D is retested in isolation, then against [main+D] if D passes alone. This means a broken MR only costs the pipeline runs for MRs behind it in the queue, not a full reset of all queued MRs. Design implication: fast-failing pipelines (abort on first error, `retry: 0`) minimize the blast radius when a merge train entry fails.
