---
description: Easy interview questions for GitLab CI, pipelines, runners, and merge request workflows.
---

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
