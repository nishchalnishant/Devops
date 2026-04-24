# GitLab CI/CD — Deep Dive Notes

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
