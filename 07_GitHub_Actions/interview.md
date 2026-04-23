# GitHub Actions — Interview Questions

All difficulty levels combined.

---

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

## Hard

**13. How do you implement SLSA Level 3 in a GitHub Actions pipeline?**

SLSA Level 3 requirements: hermetic, reproducible builds; provenance generated by the build platform itself (not the build script); two-person review for code changes.

```yaml
jobs:
  build:
    permissions:
      id-token: write   # for OIDC provenance signing
      contents: read
    uses: slsa-framework/slsa-github-generator/.github/workflows/generator_generic_slsa3.yml@v1.9.0
    with:
      base64-subjects: ${{ needs.build.outputs.digest }}
```

The SLSA GitHub Generator runs in an isolated GitHub-managed environment, generates provenance (who built what, from which commit, with which inputs), and signs it using Sigstore/Cosign with OIDC from GitHub's OIDC provider. The signed provenance is verified with `slsa-verifier verify-artifact` — ensuring the artifact was built on GitHub Actions from the expected repository and commit, not by a compromised developer machine.

**14. How do you design a pipeline that prevents secret leakage across branches and forks?**

Defense in depth:

- **OIDC for cloud auth:** No static secrets in CI at all — tokens generated per-job using OIDC, expire after the job.
- **Secret masking:** All secrets registered in the CI system are automatically masked in logs. But build artifacts may still contain secrets if code dumps environment variables.
- **Fork policy:** GitHub Actions secrets are never available in `pull_request` workflows from forks. Use `pull_request_target` only for trusted collaborators; require approval for first-time contributors via the "Require approval for all outside collaborators" setting.
- **Pre-commit hooks:** `detect-secrets` or `truffleHog` scan staged changes before commit.
- **Post-commit scanning:** Gitleaks runs in CI on every PR, scanning the full diff and commit history.

**15. Design a CI/CD pipeline for a mission-critical multi-region application with 99.99% uptime requirements.**

1. **Build:** On merge to `main`, build a versioned Docker image, run unit + integration + performance tests. Sign the image with Cosign.
2. **Staging:** Deploy to a production-like staging environment. Run E2E and smoke tests.
3. **Canary — Region 1:** Deploy to the first production region, routing 1% of traffic to the new version via Flagger + Istio VirtualService weights. Monitor P99 latency and error rate SLOs for a set period. Promote: 10% → 50% → 100%.
4. **Canary — Region 2:** Repeat the canary process in the second region after Region 1 is fully promoted and stable.
5. **Automated rollback:** If any SLO threshold is breached during canary (Prometheus query in a GitHub Actions step using `gh workflow run rollback.yml`), automatically revert traffic routing and alert on-call via PagerDuty.
6. **Artifact immutability:** All deployment manifests reference the image by immutable digest, not a mutable tag. The same image promoted through environments — never rebuilt.

**16. How do you govern a GitHub Actions environment for hundreds of teams at scale?**

1. **Reusable workflows as golden paths:** Platform team owns centralized workflows with mandatory security steps (SAST, SCA, image signing). Teams consume via `uses:`, cannot bypass the steps.
2. **Required workflows (Organization-level):** GitHub Enterprise supports Required Workflows — they run on every PR in the organization regardless of what the repo's own workflows do.
3. **Environment protection rules:** Production environments require reviewer approval, specific branches, and have deployment wait times.
4. **OIDC scoping:** IAM role trust policies restrict access to specific repository names and ref patterns (`repo:org/service-a:ref:refs/heads/main`).
5. **Secret scanning + push protection:** Enabled at the org level to block secrets from being committed.
