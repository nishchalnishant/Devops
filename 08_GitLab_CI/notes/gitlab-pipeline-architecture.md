---
description: GitLab CI pipeline architecture internals, runner configuration, DAGs, and enterprise patterns for senior engineers.
---

# GitLab CI/CD — Pipeline Architecture & Runner Deep Dive

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
