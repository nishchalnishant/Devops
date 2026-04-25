---
description: Hard interview questions for GitHub Actions — self-hosted runners, OIDC, security, and enterprise governance.
---

## Hard

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

**17. How do you architect self-hosted GitHub Actions runners for an enterprise with compliance requirements?**

**Runner architecture for regulated environments:**

1. **Network isolation:** Runners in a private VPC/VNET with no direct internet access. Egress only through a proxy allowlist or VPC endpoints for AWS services.
2. **Ephemeral runners:** Use `actions-runner-controller` (ARC) on Kubernetes. Each job spawns a fresh pod; the runner registers, executes the job, and self-destructs. No runner state persists between jobs — eliminates supply chain risk from runner compromise.
3. **Runner groups:** Separate runner groups for different environments (`production-runners` vs `staging-runners`). Production runners have access to production secrets; dev runners are sandboxed.
4. **Audit:** All runner activity logged to a SIEM via CloudTrail (if on AWS) and GitHub's audit log API.
5. **Image hardening:** Base runner images built from a trusted registry, scanned with Trivy, signed with Cosign. Runner pods run as non-root with minimal capabilities.
6. **Autoscaling:** ARC scales runner pods based on queued workflows — 0 pods when idle (cost-efficient), scale to N on demand.

**18. What are GitHub Actions security attack vectors and how do you mitigate each?**

| Attack Vector | Description | Mitigation |
|:---|:---|:---|
| **Script injection** | `${{ github.event.pull_request.title }}` in `run:` is vulnerable to arbitrary code in PR titles | Always use `env` vars: `env: PR_TITLE: ${{ ... }}` then `echo "$PR_TITLE"` |
| **Malicious action** | Third-party action updated to exfiltrate secrets | Pin all actions to commit SHA, not tags |
| **`pull_request_target` abuse** | Runs with base repo permissions; can access secrets from fork PRs | Never checkout untrusted code in `pull_request_target` |
| **Poisoned pipeline execution (PPE)** | Attacker modifies workflow file in a branch | Protect default branch; require PR reviews for workflow file changes |
| **Token over-permission** | GITHUB_TOKEN has too many permissions | Set `permissions: read-all` at workflow level; grant minimal per-job |
| **Secrets in logs** | Secrets printed to stdout in debug mode | Use `add-mask` for dynamic secrets; never print env vars directly |

**19. How does the GitHub Actions OIDC token work internally and what are the scoping options?**

When a job runs with `id-token: write` permission, GitHub's OIDC provider issues a JWT token for that job. The token contains claims:

```json
{
  "iss": "https://token.actions.githubusercontent.com",
  "sub": "repo:org/repo:ref:refs/heads/main",
  "repository": "org/repo",
  "ref": "refs/heads/main",
  "job_workflow_ref": "org/repo/.github/workflows/deploy.yml@refs/heads/main",
  "environment": "production"
}
```

The AWS IAM role trust policy can match on any of these claims:
```json
"Condition": {
  "StringEquals": {
    "token.actions.githubusercontent.com:sub": "repo:org/repo:ref:refs/heads/main",
    "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
  }
}
```

**Scoping strategies:**
- Most specific: `sub = repo:org/repo:environment:production` — only production environment jobs
- Broad: `sub = repo:org/*` — any repo in the org (too broad)
- By workflow: `job_workflow_ref` claim — only specific workflow files can assume the role

**20. How do you implement GitHub Actions for a monorepo with selective CI (only build what changed)?**

```yaml
# Step 1: Detect changed paths
- uses: dorny/paths-filter@v3
  id: changes
  with:
    filters: |
      frontend:
        - 'packages/frontend/**'
        - 'packages/shared/**'
      backend:
        - 'packages/backend/**'
        - 'packages/shared/**'

# Step 2: Conditionally run jobs
jobs:
  test-frontend:
    needs: detect-changes
    if: needs.detect-changes.outputs.frontend == 'true'
    ...

  test-backend:
    needs: detect-changes
    if: needs.detect-changes.outputs.backend == 'true'
    ...

# Step 3: Matrix for building only changed services
build-services:
  strategy:
    matrix:
      service: ${{ fromJSON(needs.detect-changes.outputs.changed-services) }}
```

Advanced: use Nx affected commands (`nx affected:test`) which understand project dependency graphs — if shared library changes, automatically test all downstream services.
