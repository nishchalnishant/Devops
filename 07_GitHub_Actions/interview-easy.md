## Easy

**1. In GitHub Actions, what is the difference between a workflow, a job, and a step?**

- **Workflow:** The entire automated process defined in a YAML file under `.github/workflows/`.
- **Job:** A set of steps that execute on the same runner. A workflow can have multiple jobs running in parallel or sequentially.
- **Step:** An individual task within a job — either a shell command or a pre-built Action called with `uses:`.

**2. What is a GitHub Actions runner?**

A runner is a server that executes jobs in a workflow. GitHub provides hosted runners (Ubuntu, Windows, macOS). Self-hosted runners are registered to a repository or organization for custom hardware, private network access, or cost control at high build volume.

**3. How do you pass data or artifacts from one job to another in GitHub Actions?**

Use `actions/upload-artifact` in the producing job and `actions/download-artifact` in the consuming job. For scalar values between jobs in the same workflow, use job outputs: set `outputs` on the producing job and reference `${{ needs.job-name.outputs.key }}` in the consuming job.

**4. What triggers a GitHub Actions workflow?**

Workflows are triggered by events defined in the `on:` block: `push`, `pull_request`, `schedule` (cron), `workflow_dispatch` (manual), `release`, `workflow_call` (called by another workflow), and many others. Multiple triggers can be specified in the same `on:` block.

**5. What is `workflow_dispatch` and when would you use it?**

`workflow_dispatch` allows a workflow to be triggered manually from the GitHub UI or via the API. It supports defining inputs that the user fills in at trigger time. Used for on-demand deployments, releases, or maintenance tasks.

---


**6. What does `actions/checkout` do and why is it almost always the first step?**

`actions/checkout` clones the repository into the runner's workspace (`$GITHUB_WORKSPACE`). Without it, subsequent steps have no access to the repo's code. By default it checks out the commit that triggered the workflow. Options: `fetch-depth: 0` to get full git history (needed for changelog generation or `git log`), `ref` to check out a specific branch/tag/SHA.

**7. What is `GITHUB_TOKEN` and what can it do?**

`GITHUB_TOKEN` is an automatically generated short-lived token provided by GitHub for each workflow run. It can authenticate against the GitHub API and GitHub Packages within the scope of the repository. Permissions are configurable via the `permissions` key. It expires when the job finishes. It cannot access other repositories or trigger new workflow runs by default (to prevent recursive loops).

**8. How do you run a step only on the `main` branch?**

Use an `if` condition:
```yaml
- run: ./deploy.sh
  if: github.ref == 'refs/heads/main'
```

Or at the job level:
```yaml
jobs:
  deploy:
    if: github.ref == 'refs/heads/main'
```

**9. What is `concurrency` in a GitHub Actions workflow?**

`concurrency` prevents multiple workflow runs from executing the same job simultaneously. Commonly used to prevent overlapping deploys:
```yaml
concurrency:
  group: deploy-${{ github.ref }}
  cancel-in-progress: true
```
`cancel-in-progress: true` cancels the older run when a new one starts. Set `false` for deploys to avoid interrupting a running rollout.

**10. How do environment variables work in GitHub Actions?**

Three scopes: workflow-level (`env:` at the top), job-level (`env:` under the job), step-level (`env:` under the step). Inner scopes override outer. Set dynamic values with `echo "KEY=value" >> $GITHUB_ENV` — available to all subsequent steps in the same job. Access in expressions with `${{ env.KEY }}`.

**11. What is the difference between `uses` and `run` in a step?**

`uses` invokes a pre-built Action (JavaScript, Docker, or composite) from a repository or the Marketplace: `uses: actions/setup-node@v4`. `run` executes shell commands directly on the runner: `run: npm ci`. Both can be combined in the same job.

**12. How do you make one job wait for another in the same workflow?**

Use `needs`:
```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps: [...]

  test:
    needs: build     # waits for build to succeed
    runs-on: ubuntu-latest
```

Multiple dependencies: `needs: [build, lint]` — waits for both. If any dependency fails, the dependent job is skipped by default.
