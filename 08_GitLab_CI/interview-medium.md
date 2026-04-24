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

