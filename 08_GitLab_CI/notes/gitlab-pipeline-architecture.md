---
description: GitLab CI pipeline architecture internals, runner configuration, DAGs, and enterprise patterns for senior engineers.
---

# GitLab CI/CD — Pipeline Architecture & Runner Deep Dive

```
Pipeline Architecture & Runner Deep Dive
├── Pipeline Anatomy
│   ├── .gitlab-ci.yml → GitLab Server → Job Queue → Runner Poll → Execute
│   ├── Stages: ordered execution phases (build → test → deploy)
│   ├── Jobs: units of work within stages; parallel within same stage
│   └── Artifacts: files passed downstream between jobs in the same pipeline
│
├── DAG Pipelines (needs:)
│   ├── Default: stage N blocked until all jobs in stage N-1 finish
│   ├── needs: [job-name] — job starts when specific dependency is ready
│   ├── needs: [{job, artifacts: false}] — dependency without artifact download
│   └── Effect: converts serial chain into parallel execution graph
│
├── Runner Architecture
│   ├── GitLab Server: coordinator — stores job queue, state, artifacts, variables
│   ├── Runner: decoupled executor — polls server via long-polling, claims jobs
│   ├── Communication: HTTPS from runner to server (runner initiates, not server)
│   └── Scale: runners scale independently from GitLab server
│
├── Executor Types
│   ├── docker: fresh container per job, isolation via Docker engine
│   │   ├── image: job-level or default override
│   │   ├── services: sidecar containers (postgres:14 linked via hostname)
│   │   └── privileged: required for docker-in-docker; security risk
│   ├── kubernetes: pod per job, ephemeral, scales with cluster autoscaler
│   │   ├── config.toml: image, cpu_request, memory_limit, service_account
│   │   └── No privileged needed if using Kaniko for image builds
│   ├── shell: runs on host — fast, no isolation, state persists between jobs
│   └── custom: user-defined provisioning hooks (provision + run + cleanup)
│
├── config.toml Key Settings
│   ├── concurrent: max parallel jobs across all registered runners on this instance
│   ├── [runners.docker]: image, privileged, volumes, pull_policy
│   ├── [runners.kubernetes]: namespace, image, cpu/memory limits per job tag
│   └── [runners.cache]: Type (s3/gcs), Shared (true for distributed cache)
│
├── Cache vs Artifacts
│   ├── cache: speed optimization, cross-pipeline, runner-local or S3 backend
│   │   ├── key: cache invalidation key (branch, commit, file hash)
│   │   ├── paths: directories to persist
│   │   └── policy: pull-push (default) | pull (read-only) | push (write-only)
│   └── artifacts: correctness, same-pipeline job-to-job, stored on GitLab server
│       ├── paths: files to archive
│       ├── expire_in: TTL before deletion
│       └── reports: junit, coverage, security — special structured artifacts
│
├── Environment-Specific Deployments
│   ├── environment: name — links job to deployment target
│   ├── Environment-scoped variables: injected only when job targets that environment
│   ├── Protected environments: restrict who can trigger the deployment
│   └── on_stop: cleanup job triggered when environment is stopped
│
└── Logic & Trickiness
    ├── needs: bypasses stage order — job can start before its own stage
    ├── cache is not guaranteed — jobs must handle cache miss gracefully
    ├── CI_JOB_TOKEN scope (GitLab 16+) — cross-project access needs allowlist
    ├── strategy: depend required — without it trigger jobs succeed immediately
    └── Protected branch ≠ protected variable — each configured separately
```

## First Principles

- Runners poll GitLab Server — the server never pushes jobs to runners. This pull model means runners can be behind firewalls and NAT without inbound rules, and they scale horizontally by simply registering more instances.
- The Docker executor provides job isolation by running each job in a fresh container that is destroyed after the job finishes. State that must persist across jobs must be explicitly declared as an artifact; state that accumulates between runs for speed is a cache.
- DAG with `needs:` is a graph execution engine sitting on top of a stage-ordered scheduler. When `needs:` is present, the stage label becomes metadata for grouping only — the actual execution order is determined by dependency readiness.
- `config.toml: concurrent` is a hard limit on simultaneous jobs. Setting it too low causes queue buildup on a runner that has idle CPU. Setting it too high causes resource contention where jobs compete for memory and disk, causing slower execution than sequential processing would.

## Pipeline Anatomy

```
.gitlab-ci.yml defines:
  ┌─────────────────────────────────┐
  │  stages: [build, test, deploy]  │ ← Ordered execution stages
  └────────────┬────────────────────┘
               │
       ┌───────▼───────┐
       │  Job: build   │ ← Runs in Stage 1 (parallel with other build jobs)
       │  image: node  │
       │  script: ...  │
       └───────┬───────┘
               │ artifact passed downstream
       ┌───────▼───────┐
       │  Job: test    │ ← Runs in Stage 2
       └───────┬───────┘
               │
       ┌───────▼───────┐
       │  Job: deploy  │ ← Runs in Stage 3 (manual gate optional)
       └───────────────┘
```

***

## DAG — Directed Acyclic Graph Pipelines

By default, GitLab requires all jobs in Stage N to complete before Stage N+1 starts. DAGs (`needs:`) break this constraint.

```yaml
# Without DAG: deploy-frontend waits for ALL test jobs to finish
# With DAG: deploy-frontend only waits for build-frontend

stages: [build, test, deploy]

build-frontend:
  stage: build
  script: npm run build

build-backend:
  stage: build
  script: go build ./...

test-frontend:
  stage: test
  needs: [build-frontend]   # ← Only depends on frontend build
  script: npm test

deploy-frontend:
  stage: deploy
  needs: [test-frontend]    # ← Skips waiting for backend test
  script: kubectl apply -f frontend/
```

**Benefit:** Deploy frontend 10 minutes earlier while backend tests are still running.

***

## Runner Architecture & Executor Types

```
GitLab Server (coordinator)
    │
    ├── Job queue (per tag, per project)
    │
    └── Runners (poll every N seconds via long-polling)
            │
            ├── Shell Executor     → Runs directly on host (fast, insecure)
            ├── Docker Executor    → Creates container per job (clean, portable)
            ├── Kubernetes Executor→ Creates pod per job (scalable, cloud-native)
            └── Custom Executor    → Your own provisioning logic
```

### Docker Executor Configuration

```toml
# /etc/gitlab-runner/config.toml
[[runners]]
  name = "docker-runner-prod"
  url = "https://gitlab.com"
  token = "RUNNER_TOKEN"
  executor = "docker"
  limit = 20   # Max concurrent jobs on this runner
  
  [runners.docker]
    image = "alpine:latest"     # Default image if job doesn't specify
    privileged = false          # NEVER enable in production
    disable_entrypoint_overwrite = false
    volumes = ["/cache"]        # Persistent cache volume
    shm_size = 0
```

### Kubernetes Executor Configuration

```toml
[[runners]]
  name = "k8s-runner"
  executor = "kubernetes"
  
  [runners.kubernetes]
    host = ""                          # In-cluster config (auto-detected)
    namespace = "gitlab-runners"
    poll_interval = 5
    
    [runners.kubernetes.pod_annotations]
      "cluster-autoscaler.kubernetes.io/safe-to-evict" = "false"
    
    [[runners.kubernetes.volumes.host_path]]
      name = "docker-sock"
      mount_path = "/var/run/docker.sock"  # For DinD use cases
```

***

## Caching vs. Artifacts

| Feature | Cache | Artifact |
|:---|:---|:---|
| **Purpose** | Speed up future jobs (same pipeline or across pipelines) | Pass files between stages in the same pipeline |
| **Storage** | Runner-local or distributed (S3) | GitLab server |
| **Expiry** | Configurable (default: 7 days) | Configurable (default: 30 days) |
| **Cross-pipeline** | Yes | No (by default) |

```yaml
build:
  cache:
    key: $CI_COMMIT_REF_SLUG   # Cache per branch
    paths:
      - node_modules/
  artifacts:
    paths:
      - dist/
    expire_in: 1 hour          # Only needed by deploy job
  script:
    - npm ci
    - npm run build
```

***

## Environment-Specific Deployments with Protected Branches

```yaml
deploy-staging:
  stage: deploy
  environment:
    name: staging
    url: https://staging.myapp.com
  script: ./deploy.sh staging
  rules:
    - if: $CI_COMMIT_BRANCH == "main"

deploy-production:
  stage: deploy
  environment:
    name: production
    url: https://myapp.com
  script: ./deploy.sh production
  when: manual                 # Requires human click
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
```

***

## Logic & Trickiness Table

| Pattern | Junior Approach | Senior Approach |
|:---|:---|:---|
| **Pipeline speed** | All jobs in stages (sequential) | Use `needs:` DAG to run jobs in parallel |
| **Runner security** | Privileged Docker executor | Kubernetes executor with pod-level isolation |
| **Secrets** | Variables in pipeline UI | Protected + masked variables, Vault integration |
| **Cache invalidation** | Fixed cache key | `key: "$CI_COMMIT_REF_SLUG-$CACHE_VERSION"` |
| **Large monorepos** | Run all tests on every push | Use `rules: changes:` to run only affected jobs |
| **Auto DevOps** | Enable blindly | Customize templates in `gitlab-ci-templates` |

***

## System Design Perspective

**Coordinator-runner separation at scale**

GitLab Server is the coordinator: it receives pipeline events, stores job definitions, enforces RBAC, and serves artifacts. Runners are stateless executors that poll for work. This separation means you can scale runner capacity independently — add runners during business hours, scale to zero overnight. The coordinator does not need to know about runner topology; runners self-register with tags that describe their capabilities.

**Executor selection decision tree**

Use Kubernetes executor when: you're already on K8s, want ephemeral jobs, need GPU or specialized node types, and want cluster autoscaling to handle burst capacity. Use Docker executor when: you have dedicated VMs, need predictable job startup time (no pod scheduling delay), and want simple configuration. Use shell executor only for: legacy compatibility, local development machines, or performance-critical jobs where container overhead is unacceptable — never for untrusted code.

**Cache architecture for distributed runner pools**

When runners run on multiple hosts (EC2 autoscaling, K8s nodes), runner-local cache creates unpredictable cache hits — a job on runner-1 misses the cache populated by runner-2. Solution: S3 distributed cache in `config.toml`. The cache manager uploads after job completion and downloads at job start. Keys design matters: `key: files: [package-lock.json]` means the cache is always valid when the lockfile is unchanged, busted when it changes. Per-branch keys (`key: $CI_COMMIT_REF_SLUG`) prevent different branches from sharing potentially incompatible caches.

**Environment-scoped variable injection mechanics**

When a job declares `environment: name: production`, GitLab Server filters the variable injection: only variables scoped to `production` (or `*`) are included in the job's environment. Variables scoped to `staging` are literally absent from the environment — the runner never receives them. This is enforced server-side before the job payload is sent to the runner; the runner has no ability to request variables for environments it's not targeting.
