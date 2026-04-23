# GitLab CI — Interview Questions

All difficulty levels combined.

---

## Easy

**1. What is the `.gitlab-ci.yml` file?**

It is the core of GitLab CI/CD — a YAML file in the root of a repository that defines pipeline structure: the stages, jobs, and conditions under which they run. GitLab detects this file automatically and creates a pipeline on each push.

**2. What is a GitLab Runner?**

A GitLab Runner is a worker process that executes CI/CD jobs. Like Jenkins agents, runners separate execution from orchestration, enabling parallel runs and isolated build environments. Runners can be shared across projects or dedicated to a group or project, and they poll GitLab for pending jobs.

**3. How do you manage secrets in GitLab CI?**

Use GitLab CI/CD variables (masked and protected) in project or group settings. Masked variables are redacted from job logs. For advanced needs, integrate with HashiCorp Vault or cloud secret managers via the Vault JWT Auth method. Never hardcode secrets in `.gitlab-ci.yml`.

**4. What is a GitLab stage and how does job ordering work?**

Stages define the execution order of jobs. All jobs in the same stage run in parallel; the next stage starts only after all jobs in the current stage succeed. Stages are declared in the top-level `stages:` list and referenced by each job's `stage:` key.

**5. What is the `only` / `rules` directive in GitLab CI?**

`only`/`except` (legacy) and `rules` (current) control when a job runs. `rules` supports more complex conditions:

```yaml
job:
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
      when: always
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
      when: manual
    - when: never
```

**6. What are GitLab CI artifacts?**

Artifacts are files or directories produced by a job and stored by GitLab so subsequent jobs (even in later stages) can download and use them. Defined with `artifacts.paths`. They persist for a configurable number of days.

**7. What is `cache` in GitLab CI and how does it differ from artifacts?**

`cache` stores files between pipeline runs on the same runner to speed up jobs (e.g., `node_modules`, `.m2/repository`). Artifacts pass files between jobs within the same pipeline. Cache is a best-effort optimization; artifacts are reliable handoffs.

---

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

---

## Hard

**15. How do you govern a multi-tenant GitLab CI environment where hundreds of teams create their own pipelines?**

1. **Pipeline templates:** Disable classic CI and mandate that all pipelines use `extends:` or `include:` to inherit from central templates. Ensure mandatory security scans (credential scanning, SAST, container scanning) run on every pipeline.
2. **GitLab Environments with protected environments:** Require environment declarations for all production deployments. Protected environments restrict which roles can trigger deploys and require designated approvers.
3. **DORA Metrics:** GitLab's built-in DORA metrics (deployment frequency, change failure rate, lead time, MTTR) are tracked automatically per project. Used to measure platform health across teams.
4. **Runner isolation:** Use dedicated GitLab Runners with appropriate tags for different workloads (GPU runners for ML, high-memory for builds). Prevent privilege escalation with `--security-opt=no-new-privileges` on Docker executors.

**16. How do you migrate 100 Jenkins pipelines to GitLab CI?**

A big-bang migration is too risky. Phased approach:

1. **Categorize:** Group the 100 pipelines by complexity and pattern. Identify 5-10 representative pilots.
2. **Pilot:** Convert pilots to `.gitlab-ci.yml`. Create GitLab CI `include:` templates that replicate Jenkins Shared Library functions.
3. **Tooling and documentation:** Build a conversion guide mapping `Jenkinsfile` constructs to GitLab CI equivalents. Run workshops for developers.
4. **Phased rollout:** Onboard teams in waves, simplest pipelines first. New projects start on GitLab CI only.
5. **Decommission:** Archive Jenkins data, shut down servers after all pipelines are migrated and validated.

**17. How do you design a security scanning pipeline that blocks vulnerable code from reaching production?**

Multi-layer approach using GitLab's built-in security features:

1. **SAST:** Runs on every MR, scans source code for vulnerability patterns. Results appear in the MR widget.
2. **SCA / Dependency Scanning:** Detects known CVEs in third-party libraries. Fail the pipeline if a critical severity CVE is found.
3. **Container scanning:** Scans the built Docker image against Trivy or Grype. Blocks promotion if high/critical CVEs present in OS packages.
4. **Secret detection:** Gitleaks scans the diff for committed secrets on every push.
5. **DAST:** Runs against a deployed staging environment for runtime vulnerability detection.
6. **Policy gates:** GitLab Security Policies (MR approval policies) require security team sign-off when scanning reports new critical findings.

**18. What is GitLab's Dependency Proxy and why is it useful in CI pipelines?**

The Dependency Proxy is GitLab's pull-through cache for Docker Hub images. Instead of each CI job pulling `python:3.11` from Docker Hub (subject to rate limits and slow external pulls), jobs pull from `registry.gitlab.com/group/dependency_proxy/containers/python:3.11`. GitLab caches the image internally. Benefits: eliminates Docker Hub rate limit failures in CI, reduces external network egress, and speeds up job startup time.
