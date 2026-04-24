## Medium

**6. How does OIDC authentication work in GitHub Actions and why is it preferred over long-lived secrets?**

OIDC allows GitHub Actions to request short-lived tokens from a cloud provider (AWS, Azure, GCP) without storing any static credentials in the repository. The CI job presents a JWT token signed by GitHub's OIDC provider, and the cloud IAM service verifies it against a pre-configured trust relationship, issuing a short-lived access token. Benefits: no secrets to rotate or leak, tokens expire automatically within minutes, access is scoped to the specific repository and branch by claims embedded in the JWT.

**7. What is a reusable workflow in GitHub Actions?**

A reusable workflow is a workflow file that can be called from other workflows using `uses: org/repo/.github/workflows/workflow.yml@ref`. The calling workflow passes inputs and secrets; the reusable workflow runs in its own context. Used to share standardized pipeline logic — security scans, build steps, deployment processes — across many repositories without duplication.

**8. How do you handle secrets in GitHub Actions securely?**

Secrets are stored in repository or organization settings and injected into workflow steps as environment variables (`${{ secrets.MY_SECRET }}`). GitHub masks secret values in log output. Best practices:
- For cloud access, prefer OIDC over static secrets — no secrets to store at all.
- Never print secrets with `echo` or pass them between jobs unless strictly necessary.
- Use `environment` protection rules to restrict which branches can access environment-scoped secrets.

**9. What is a matrix strategy in GitHub Actions?**

The `strategy.matrix` key runs a job multiple times with different variable combinations:

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest]
    python: ["3.10", "3.11", "3.12"]
jobs:
  test:
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python }}
```

This produces 6 parallel jobs (2 OS × 3 Python versions). Used for cross-platform and cross-version testing.

**10. How do you cache dependencies in GitHub Actions to speed up workflows?**

Use `actions/cache` with a key derived from a lockfile hash:

```yaml
- uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

On cache hit, the step restores the cached directory; on cache miss, the job runs normally and saves the directory at the end. This eliminates redundant package downloads when dependencies haven't changed.

**11. What is the difference between `pull_request` and `pull_request_target` event triggers?**

`pull_request` runs workflows in the context of the PR's head branch, without access to secrets — this is the safe default for external contributors. `pull_request_target` runs in the context of the base branch and does have access to secrets. Never use `pull_request_target` with code from the forked PR directly — it creates a secret exfiltration risk. Use it only for trusted collaborators or for workflows that don't execute untrusted code (e.g., labeling a PR based on its metadata).

**12. What is "paved road" CI/CD and how do reusable workflows enable it?**

A paved road is a standardized, opinionated CI/CD path that builds in mandatory security, testing, and compliance steps, while letting developers focus on their application. With reusable workflows, the platform team owns a central workflow that includes non-negotiable steps (SAST, SBOM generation, image signing). Teams include the workflow with a single `uses:` line and provide application-specific parameters. The platform team can update all pipelines centrally by updating the shared workflow.

---

