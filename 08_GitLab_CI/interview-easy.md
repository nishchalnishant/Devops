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

***

