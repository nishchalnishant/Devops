---
description: Hard interview questions for GitLab CI architecture, runner scaling, compliance, and enterprise patterns.
---

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
