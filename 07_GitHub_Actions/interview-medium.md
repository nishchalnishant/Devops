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


**13. How do you implement a dynamic matrix build where the matrix values are generated at runtime?**

Generate the matrix JSON in a prior job and pass it via outputs:

```yaml
jobs:
  compute-matrix:
    runs-on: ubuntu-latest
    outputs:
      matrix: ${{ steps.set.outputs.matrix }}
    steps:
    - id: set
      run: |
        SERVICES=$(ls services/ | jq -R -s -c 'split("\n")[:-1]')
        echo "matrix={\"service\":$SERVICES}" >> $GITHUB_OUTPUT

  test:
    needs: compute-matrix
    strategy:
      matrix: ${{ fromJson(needs.compute-matrix.outputs.matrix) }}
    runs-on: ubuntu-latest
    steps:
    - run: pytest services/${{ matrix.service }}/
```

Useful for monorepos where the list of services changes over time — no manual matrix updates needed.

**14. What is the difference between `secrets` and `vars` in GitHub Actions?**

`secrets` are encrypted at rest and masked in logs — values are never visible after being stored. `vars` (repository/environment variables) are plain-text, visible to anyone with read access to the repo settings. Use `secrets` for credentials, tokens, API keys. Use `vars` for non-sensitive configuration that differs between environments (URLs, feature flags, region names).

Access: `${{ secrets.MY_SECRET }}` and `${{ vars.MY_VAR }}`.

**15. How do you prevent a workflow from being triggered by bot commits?**

```yaml
on:
  push:
    branches: [main]

jobs:
  build:
    if: github.actor != 'dependabot[bot]' && github.actor != 'github-actions[bot]'
```

Or skip at the commit level by including `[skip ci]` in the commit message — GitHub Actions honors this by default.

**16. How do you implement rollback in a GitHub Actions deployment workflow?**

Pattern: deploy and verify, then rollback on failure:

```yaml
- name: Deploy
  id: deploy
  run: helm upgrade --install myapp ./chart --set image.tag=${{ env.IMAGE_TAG }}

- name: Verify
  id: verify
  run: ./scripts/smoke-test.sh
  
- name: Rollback on failure
  if: failure() && steps.deploy.outcome == 'success'
  run: helm rollback myapp
```

For Kubernetes: `kubectl rollout undo deployment/myapp` as the rollback step. The `if: failure()` condition means this step only runs if a previous step failed.

**17. How does GitHub Actions handle workflow permissions in a fork?**

Workflows triggered by `pull_request` from a fork run without access to secrets. The `GITHUB_TOKEN` is read-only. This protects against secret exfiltration from malicious forks. For workflows that need secrets (e.g., to post a comment with test results), use `pull_request_target` combined with an environment protection rule requiring reviewer approval before the job runs.

**18. What are composite actions and when would you use them over reusable workflows?**

| | Composite Action | Reusable Workflow |
|---|---|---|
| Unit | Steps | Jobs |
| Outputs | Step outputs | Job outputs |
| Secrets | Via inputs | Via `secrets:` block |
| Parallelism | Sequential steps | Can have parallel jobs |
| Use case | Encapsulate a sequence of steps | Encapsulate an entire pipeline |

Use composite actions for small reusable step sequences (setup, build, test). Use reusable workflows when you need multiple jobs with dependencies, environments, or matrix builds.
