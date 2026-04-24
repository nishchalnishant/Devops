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

