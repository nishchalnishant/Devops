# GitLab CI/CD — Deep Dive Notes

```
GitLab CI/CD Deep Dive Notes
├── Why GitLab CI Exists
│   ├── Single platform: code + CI + registry + deployments — no tool sprawl
│   ├── Pipeline-as-code: .gitlab-ci.yml reviewed like any other change
│   ├── Auto DevOps: opinionated defaults for common frameworks
│   ├── Review Apps: ephemeral env per MR, visible URL in MR widget
│   └── Security scanning: SAST, DAST, SCA, container scanning built-in
│
├── Architecture Internals
│   ├── Developer pushes → GitLab creates pipeline → jobs queued
│   ├── Runner polls GitLab server → claims job → executes → uploads artifacts
│   └── Status reported back to server → pipeline state updated
│
├── Pipeline Execution Model
│   ├── Pipeline types (CI_PIPELINE_SOURCE values)
│   │   ├── push: git push to any branch
│   │   ├── merge_request_event: MR opened/updated/push
│   │   ├── schedule: cron-triggered via GitLab Schedules
│   │   ├── web: manual UI trigger
│   │   ├── trigger: API token trigger
│   │   └── parent_pipeline: triggered by parent (parent-child)
│   ├── workflow: rules gates which source values create a pipeline at all
│   └── default: global job defaults (image, before_script, retry, timeout)
│
├── Full .gitlab-ci.yml Reference
│   ├── stages: [build, test, security, deploy]
│   ├── Build: docker login + build + push + artifact declaration
│   ├── Test: with needs: [build] — DAG, downloads build artifact
│   ├── Security: Trivy scan, artifact report type: container_scanning
│   └── Deploy: environment: name, when: manual, rules: branch == main
│
├── Runner config.toml
│   ├── Docker executor: concurrent, image, privileged, volumes, pull_policy
│   └── Kubernetes executor: namespace, image, cpu/memory requests+limits
│
├── Executor Comparison
│   ├── docker: isolated, reproducible, ~15s overhead — most common
│   ├── shell: fast, no isolation, state persists — legacy/local only
│   ├── kubernetes: ephemeral pod, scalable, no privileged — cloud-native
│   └── custom: hook-based provisioning for specialized environments
│
├── Cache vs Artifacts (Detailed)
│   ├── cache: speed optimization, cross-pipeline, keyed storage
│   │   ├── key.files: invalidate on specific file changes
│   │   ├── policy: pull-push | pull | push
│   │   └── Not guaranteed — code jobs to handle cache miss
│   └── artifacts: correctness, same-pipeline only, server-stored
│       ├── expire_in: mandatory for pipelines with delayed manual jobs
│       └── reports: structured data (junit, security, coverage)
│
├── Variables Precedence & Scoping
│   ├── Precedence: trigger > job > pipeline > project > group > instance > predefined
│   ├── Protected: injected only on protected branches/tags
│   ├── Masked: redacted in logs (≥8 chars, no whitespace/newlines)
│   ├── File-type: content written to temp file; variable = path
│   └── Environment-scoped: injected only when job targets that environment
│
├── Dynamic Child Pipelines
│   ├── Script generates YAML based on git diff (changed paths → service names)
│   ├── YAML file saved as artifact: paths: [generated-pipeline.yml]
│   └── Trigger job: trigger: include: artifact: generated-pipeline.yml
│
├── MR vs Merged Results vs Merge Trains
│   ├── MR pipeline: tests the source branch as-is
│   ├── Merged results pipeline: tests source merged with target (speculative)
│   └── Merge Train: queues MRs, tests each combined with all queued ahead of it
│
├── Security Scanning Templates
│   ├── include: template: Security/SAST.gitlab-ci.yml
│   ├── include: template: Security/Secret-Detection.gitlab-ci.yml
│   ├── include: template: Security/Dependency-Scanning.gitlab-ci.yml
│   └── include: template: Security/Container-Scanning.gitlab-ci.yml
│
├── Review Apps
│   ├── Dynamic environment name: $CI_COMMIT_REF_SLUG
│   ├── auto_stop_in: 7 days — prevents environment sprawl
│   └── on_stop: job that tears down the environment (helm uninstall)
│
└── Key Gotchas
    ├── only/except is legacy — use rules:
    ├── needs: bypasses stage order — job can start before its own stage
    ├── CI_JOB_TOKEN scope (GitLab 16+) — cross-project needs allowlist
    ├── strategy: depend required for synchronous trigger behavior
    ├── Protected branch ≠ protected variable — configured separately
    └── interruptible: true — set globally to auto-cancel stale MR pipelines
```

## First Principles

- GitLab CI's integration advantage is data locality: pipeline results, security findings, deployment history, and DORA metrics are all in the same database as the code. No webhook fan-out, no API bridging.
- The pipeline execution model is push-to-queue, poll-to-execute. GitLab Server never pushes to runners; runners long-poll for available jobs. This is why runners can be behind firewalls — only outbound HTTPS from runner to server is needed.
- Variable precedence encodes a trust hierarchy: trigger variables (caller-controlled) override everything; predefined variables (GitLab-controlled) are the floor. Understanding this hierarchy prevents the "my variable isn't being used" class of bugs.
- Dynamic child pipelines solve the static pipeline size problem in monorepos. The root pipeline is a code-executing dispatcher; the generated YAML is a data artifact. Separating the dispatch logic (Python/bash script) from the execution definition (YAML) keeps both maintainable.
- Merge Trains eliminate the "tested on branch but broken on main" problem by testing each MR speculatively combined with the MRs queued ahead of it. The tradeoff is pipeline cost proportional to queue depth — only use Merge Trains when the cost of a broken main branch exceeds the cost of extra CI runs.

## Why GitLab CI/CD Exists

GitLab CI/CD was one of the first integrated CI/CD systems in a DevOps platform. Unlike Jenkins (external) or GitHub Actions (newer), GitLab CI has been part of the platform since 2016, making it mature and deeply integrated.

**Key Advantages:**

1. **Single platform:** Code, CI/CD, container registry, and deployment in one system
2. **Powerful DAG execution:** The `needs:` keyword allows complex dependency graphs beyond simple stages
3. **Auto DevOps:** Opinionated pipelines that work out of the box for common frameworks
4. **Review Apps:** Automatic ephemeral environments for every merge request
5. **Security scanning:** Built-in SAST, DAST, dependency scanning, and container scanning

**The Architecture:**

```
Developer pushes code → GitLab creates pipeline → Jobs queued → Runner polls → Job claimed → Job executed → Artifacts uploaded → Status reported
```

**Runner Types:**
- **Shared runners:** GitLab-managed, available to all projects, billed on GitLab.com
- **Group runners:** Shared within a group hierarchy
- **Project runners:** Dedicated to a single project

**Executor Types:**
- **Docker:** Most common — each job runs in a fresh container
- **Shell:** Runs directly on the runner host (faster, but less isolated)
- **Kubernetes:** Each job runs in a Kubernetes pod (ephemeral, scalable)

This document covers pipeline internals, advanced configuration, and enterprise patterns.

***

## Pipeline Architecture Internals

GitLab CI pipelines are defined in `.gitlab-ci.yml` and executed by Runners via a polling mechanism:

```
GitLab Server (coordinator)
    │
    ├── Stores pipeline definitions, job queues, artifacts
    ├── Assigns jobs to available runners via long-polling
    └── Collects logs, artifacts, and status updates

Runner (agent)
    │
    ├── Polls coordinator every few seconds for pending jobs
    ├── Claims a job (acquires a lock)
    ├── Executes using the configured executor
    └── Reports status + uploads artifacts
```

Runner types:
- **Shared runners** — available to all projects in the instance; billed per minute on GitLab.com
- **Group runners** — available to all projects in a group
- **Project runners** — locked to a single project

## Pipeline Execution Model

```
Trigger (push / MR / schedule / API)
    │
    ▼
GitLab creates a Pipeline object
    │
    ▼
Jobs grouped into Stages — stages run sequentially
    │
    ▼
Jobs within a stage run in parallel (up to runner concurrency limit)
    │
    ▼
DAG override: `needs:` keyword breaks stage ordering
    │  Job B can start as soon as Job A finishes, regardless of stage
    ▼
Pipeline completes when all jobs finish (or first failure with allow_failure:false)
```

### Key pipeline types

| Source | `CI_PIPELINE_SOURCE` | Trigger |
|--------|---------------------|---------|
| Push to branch | `push` | `git push` |
| Merge request | `merge_request_event` | MR open / update |
| Merged results | `merge_request_event` | MR with merged results enabled |
| Scheduled | `schedule` | GitLab Schedules UI |
| API | `api` | POST to pipeline API |
| Upstream trigger | `pipeline` | `trigger:` from parent |
| Manual | `web` | "Run pipeline" in UI |

## .gitlab-ci.yml — Full Feature Reference

```yaml
# Top-level defaults applied to all jobs
default:
  image: ubuntu:22.04
  before_script:
    - apt-get update -qq
  retry:
    max: 2
    when:
      - runner_system_failure
      - stuck_or_timeout_failure
  interruptible: true   # cancel old pipeline when new one starts for same ref

# Global variables (lowest precedence)
variables:
  DOCKER_DRIVER: overlay2
  DOCKER_BUILDKIT: "1"
  FF_USE_FASTZIP: "true"   # GitLab feature flags for runner

# Workflow controls which events create a pipeline
workflow:
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
    - if: $CI_COMMIT_TAG
    - when: never

stages:
  - .pre       # always runs before named stages
  - build
  - test
  - security
  - deploy
  - .post      # always runs after named stages

# --- BUILD ---
build-image:
  stage: build
  image: docker:24
  services:
    - docker:24-dind
  variables:
    IMAGE: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_JOB_TOKEN $CI_REGISTRY
    - docker build --cache-from $CI_REGISTRY_IMAGE:latest -t $IMAGE .
    - docker push $IMAGE
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

# --- TEST with DAG (needs) ---
unit-test:
  stage: test
  needs: [build-image]   # starts immediately after build-image, skips stage ordering
  image: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  script:
    - pytest tests/unit/ --junitxml=report.xml
  artifacts:
    reports:
      junit: report.xml
    expire_in: 7 days

integration-test:
  stage: test
  needs: [build-image]
  services:
    - postgres:15
  variables:
    POSTGRES_DB: testdb
    POSTGRES_USER: test
    POSTGRES_PASSWORD: test
  script:
    - pytest tests/integration/
  allow_failure: false

# --- SECURITY ---
trivy-scan:
  stage: security
  needs: [build-image]
  image:
    name: aquasec/trivy:latest
    entrypoint: [""]
  script:
    - trivy image --severity CRITICAL,HIGH --exit-code 1
        --ignore-unfixed $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  allow_failure: false

sast:
  stage: security
  include:
    - template: Security/SAST.gitlab-ci.yml

# --- DEPLOY with environments ---
deploy-staging:
  stage: deploy
  image: bitnami/kubectl:latest
  environment:
    name: staging
    url: https://staging.myapp.com
    on_stop: stop-staging
  script:
    - kubectl set image deployment/myapp app=$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA -n staging
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

deploy-production:
  stage: deploy
  environment:
    name: production
    url: https://myapp.com
  script:
    - kubectl set image deployment/myapp app=$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA -n production
  rules:
    - if: $CI_COMMIT_TAG =~ /^v\d+\.\d+\.\d+$/
  when: manual   # require human approval

stop-staging:
  stage: deploy
  environment:
    name: staging
    action: stop
  script:
    - kubectl delete namespace staging --ignore-not-found
  when: manual
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

## Runner Configuration Deep Dive

### `/etc/gitlab-runner/config.toml`

```toml
concurrent = 10   # global: max simultaneous jobs across all runners on this host

[[runners]]
  name = "docker-runner"
  url = "https://gitlab.mycompany.com"
  token = "RUNNER_TOKEN"
  executor = "docker"
  
  [runners.docker]
    image = "alpine:latest"
    privileged = false          # true only for Docker-in-Docker
    disable_cache = false
    volumes = ["/cache"]
    shm_size = 268435456        # 256MB — important for Chrome/Selenium tests
    pull_policy = ["always"]    # never use stale cached images

  [runners.cache]
    Type = "s3"
    Shared = true
    [runners.cache.s3]
      ServerAddress = "s3.amazonaws.com"
      BucketName = "my-gitlab-cache"
      BucketLocation = "us-east-1"

[[runners]]
  name = "kubernetes-runner"
  executor = "kubernetes"
  
  [runners.kubernetes]
    namespace = "gitlab-runners"
    image = "alpine:latest"
    cpu_request = "100m"
    cpu_limit = "2"
    memory_request = "128Mi"
    memory_limit = "4Gi"
    service_account = "gitlab-runner"
    
    [[runners.kubernetes.node_selector_overrides]]
      key = "node-role"
      value = "ci"
```

### Executor comparison

| Executor | Isolation | Speed | Use Case |
|----------|-----------|-------|----------|
| Shell | None | Fastest | Trusted, simple scripts |
| Docker | Container | Fast | Standard CI workloads |
| Docker+Machine | VM + Container | Slow start | Autoscaling (deprecated) |
| Kubernetes | Pod | Medium | Cloud-native, ephemeral |
| VirtualBox | Full VM | Slowest | Windows, legacy |

## Cache vs. Artifacts

```yaml
# Cache: shared between pipeline runs for the same branch/key
# Restored at job start, uploaded at job end
# Not guaranteed (cache miss is normal)
cache:
  key:
    files:
      - package-lock.json     # cache key includes file hash
    prefix: node-$CI_JOB_NAME
  paths:
    - node_modules/
  policy: pull-push           # default: download + upload
  # policy: pull              # download only (read-only jobs)
  # policy: push              # upload only (seed job)

# Artifacts: passed between jobs in the same pipeline
# Guaranteed to be present for dependent jobs
# Stored on the GitLab server
artifacts:
  paths:
    - dist/
    - coverage/
  reports:
    junit: test-results.xml
    coverage_report:
      coverage_format: cobertura
      path: coverage.xml
  expire_in: 30 days
  when: always    # also upload on failure (for debugging)
```

**Key distinction:** Cache is an optimization (speed). Artifacts are a correctness guarantee (passing build outputs between jobs). Never use cache for security-sensitive files — they can be read by other pipelines sharing the runner.

## Variables — Precedence and Scoping

Variables are resolved in this order (highest wins):

1. Trigger variables (set via API or `trigger:variables:`)
2. Job-level `variables:` block
3. Pipeline-level `variables:` block
4. Project CI/CD Settings → Variables
5. Group CI/CD Settings → Variables
6. Instance CI/CD Settings → Variables
7. Predefined variables (e.g., `$CI_COMMIT_SHA`)

**Protected variables** — only injected into pipelines running on protected branches or tags. Use for production credentials.

**Masked variables** — value is redacted from job logs. Requirements: ≥8 characters, no whitespace or `$` at start.

**File-type variables** — GitLab creates a temporary file with the value and sets the variable to the file path. Ideal for certificates and kubeconfig files.

```yaml
# Using a file-type variable
deploy:
  script:
    - kubectl --kubeconfig=$KUBECONFIG_PROD apply -f manifests/
    # $KUBECONFIG_PROD is the PATH to the temp file, not the content
```

## Dynamic Child Pipelines

Generate pipeline YAML on the fly — useful for monorepos where different services need different pipelines.

```yaml
# Parent pipeline
generate-pipeline:
  stage: .pre
  script:
    - python3 scripts/generate_pipeline.py > generated-pipeline.yml
  artifacts:
    paths:
      - generated-pipeline.yml

trigger-generated:
  stage: build
  trigger:
    include:
      - artifact: generated-pipeline.yml
        job: generate-pipeline
    strategy: depend
```

```python
# scripts/generate_pipeline.py
import yaml, os, subprocess

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD~1"]
).decode().splitlines()

jobs = {}
for svc in ["auth", "payments", "notifications"]:
    if any(f.startswith(f"services/{svc}/") for f in changed):
        jobs[f"build-{svc}"] = {
            "stage": "build",
            "script": [f"cd services/{svc} && docker build ."]
        }

print(yaml.dump({"stages": ["build"], **jobs}))
```

## GitLab Merge Request Pipelines vs. Merged Results Pipelines

```
MR Pipeline:          runs on the source branch tip
Merged Results:       runs on a simulated merge commit (source + target merged)
Merge Trains:         queues MRs, merges them in order, only green ones land
```

**Merge trains** prevent the "order of operations" race: two MRs both green independently, but one breaks the other after merge. With merge trains, each MR is tested against the already-queued merges ahead of it.

```yaml
# Enable in GitLab project settings:
# Settings → Merge Requests → Merge method → Merge trains
```

## Security Scanning Templates

```yaml
include:
  - template: Security/SAST.gitlab-ci.yml
  - template: Security/Secret-Detection.gitlab-ci.yml
  - template: Security/Dependency-Scanning.gitlab-ci.yml
  - template: Security/Container-Scanning.gitlab-ci.yml
  - template: Security/DAST.gitlab-ci.yml

# Override template variables
variables:
  SAST_EXCLUDED_PATHS: "spec,test,tests,tmp,vendor"
  SAST_EXCLUDED_ANALYZERS: "gosec"   # skip if not a Go project
  CS_IMAGE: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  DAST_WEBSITE: https://staging.myapp.com
```

Security findings appear in the MR widget and the Security Dashboard. Set severity thresholds:
```yaml
# Block merge if critical vulnerabilities found (requires Ultimate tier)
# Settings → Security & Compliance → Security Approvals
```

## Review Apps

Ephemeral environments created per MR — spin up a full app stack for each PR and tear it down on merge.

```yaml
review:
  stage: deploy
  script:
    - helm upgrade --install review-$CI_MERGE_REQUEST_IID ./chart
        --namespace review-$CI_MERGE_REQUEST_IID
        --create-namespace
        --set image.tag=$CI_COMMIT_SHA
        --set ingress.host=review-$CI_MERGE_REQUEST_IID.preview.myapp.com
  environment:
    name: review/$CI_MERGE_REQUEST_IID
    url: https://review-$CI_MERGE_REQUEST_IID.preview.myapp.com
    on_stop: stop-review
    auto_stop_in: 3 days
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"

stop-review:
  stage: deploy
  script:
    - helm uninstall review-$CI_MERGE_REQUEST_IID -n review-$CI_MERGE_REQUEST_IID
    - kubectl delete namespace review-$CI_MERGE_REQUEST_IID
  environment:
    name: review/$CI_MERGE_REQUEST_IID
    action: stop
  when: manual
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
```

## Key Gotchas

| Gotcha | Detail |
|--------|--------|
| `only`/`except` is legacy | Use `rules:` — it's evaluated top-down with explicit `when:` control |
| `needs:` bypasses stage order | A job with `needs:` can start before its own stage if dependencies are met |
| Cache is not guaranteed | Always code jobs to handle a cache miss gracefully |
| `CI_JOB_TOKEN` scope | By default, only accesses the current project; enable "Allow CI job token to access" for cross-project |
| Masked variable length | Must be ≥8 chars; values with newlines cannot be masked |
| `strategy: depend` required | Without it, `trigger:` jobs succeed immediately, not when child completes |
| Protected branch ≠ protected variable | Each must be configured separately |
| `interruptible: true` on default | Set globally so MR pushes cancel stale pipelines automatically |

***

## System Design Perspective

**Dynamic pipeline generation at scale**

For monorepos with 50+ services, static `rules: changes:` per service creates a root pipeline with thousands of lines that becomes unmaintainable. The dynamic pattern: one "generator" job uses `git diff --name-only origin/$CI_MERGE_REQUEST_TARGET_BRANCH_NAME` to identify changed paths, maps them to service names via a lookup table (JSON or Python dict), and emits a `generated-pipeline.yml`. The generator job saves this as an artifact; a trigger job executes it with `trigger: include: artifact:`. The root pipeline stays at ~20 lines regardless of service count.

**Merge Train performance characteristics**

At high MR throughput (10+ MRs/hour), Merge Trains consume O(n²) pipeline capacity in the worst case (each new MR tests against all queued MRs). Mitigations: (1) keep pipelines fast — every minute saved reduces quadratic cost; (2) use `interruptible: true` on test jobs so when a train entry ahead fails and the queue resets, running tests are cancelled rather than completing wastefully; (3) consider Merge Trains only for the default branch — feature branch pipelines don't need train semantics.

**Security scanning integration architecture**

Security scan results flow through GitLab's artifact report system: each scanner produces a JSON artifact of type `container_scanning`, `sast`, `dependency_scanning`, etc. GitLab parses these artifacts and surfaces findings in the MR widget, Security Dashboard, and Vulnerability Report. The scanning jobs themselves are just CI jobs — the magic is the structured artifact format. This means you can replace GitLab's default scanners (Trivy, Semgrep) with any tool that produces the same JSON schema.
