# Production Scenarios & Troubleshooting Drills (Senior Level)

### Scenario 1: OIDC Trust Policy Failure
**Problem:** GitHub Action cannot assume an AWS IAM Role.
**Fix:** The AWS Trust Policy must exactly match the `repo:org/repo` format. Check the `aud` and `sub` claims.

### Scenario 2: Self-hosted Runner Security
**Problem:** A contributor steals a secret via a PR on an open-source project.
**Fix:** Never use `pull_request_target` on untrusted forks. Use Environments with mandatory approvals for secret access.

### Scenario 3: Matrix Build Optimization
**Problem:** You are testing on 10 versions of Node, but if version 1 fails, you want to stop all others immediately to save money.
**Fix:** Set `fail-fast: true` in your matrix strategy.
