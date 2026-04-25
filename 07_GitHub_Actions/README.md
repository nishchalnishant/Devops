# GitHub Actions

GitHub Actions is the native CI/CD and automation platform built directly into GitHub. Workflows are YAML files stored in `.github/workflows/` that are triggered by repository events and run on GitHub-hosted or self-hosted runners.

***

## What Is in This Module

| File | Purpose |
|:---|:---|
| `notes/notes.md` | Core concepts, OIDC, reusable workflows, matrix strategy, composite actions |
| `cheatsheet.md` | Quick-reference YAML syntax, contexts, expressions, security hardening |
| `tips-and-tricks.md` | Production gotchas, OIDC internals, monorepo CI, attack vector table |
| `interview-easy.md` | Foundational questions: workflows, jobs, steps, triggers, secrets |
| `interview-medium.md` | Intermediate: reusable workflows, matrix, OIDC, caching, environments |
| `interview-hard.md` | Advanced: self-hosted runners, enterprise governance, security hardening |
| `scenarios.md` | Real-world troubleshooting scenarios |

***

## Core Architecture

```
GitHub Repository
    │
    └── .github/workflows/ci.yml ──────────► Workflow (triggered by event)
                                                    │
                                             ┌──────┴──────┐
                                             │             │
                                           Job A         Job B
                                        (build)        (lint)
                                        runs on        runs on
                                        ubuntu-24.04   ubuntu-24.04
                                             │
                                         ┌───┴───┐
                                         │       │
                                      Step 1  Step 2
                                      (uses:)  (run:)
```

**Parallelism model:**
- Jobs in the same workflow run **in parallel** by default
- Use `needs: [job-name]` to create sequential dependencies
- Steps within a job run **sequentially**

***

## Key Concepts Reference

| Concept | Description | Example |
|:---|:---|:---|
| **Workflow** | YAML file defining automation, triggered by events | `.github/workflows/ci.yml` |
| **Job** | Group of steps running on the same runner | `jobs: build:` |
| **Step** | Individual task within a job | `- uses: actions/checkout@v4` |
| **Action** | Reusable automation unit | `uses: actions/setup-python@v5` |
| **Runner** | Machine executing jobs | `runs-on: ubuntu-24.04` |
| **Event** | Trigger starting a workflow | `on: push, pull_request, schedule` |
| **Context** | Runtime data objects | `${{ github.sha }}`, `${{ secrets.TOKEN }}` |
| **Expression** | Dynamic value syntax | `${{ env.MY_VAR }}` |
| **OIDC** | Keyless cloud auth via JWT | `id-token: write` + `aws-actions/configure-aws-credentials` |
| **Reusable workflow** | Call one workflow from another | `uses: org/repo/.github/workflows/build.yml@main` |

***

## Interview Focus Areas

| Difficulty | Key Topics |
|:---|:---|
| **Easy** | Workflow structure, triggers, jobs vs steps, runners, secrets vs env vars, artifacts, matrix |
| **Medium** | Reusable workflows, composite actions, OIDC, caching strategies, environments, concurrency |
| **Hard** | Self-hosted runner architecture (ARC), security attack vectors, enterprise governance (Required Workflows), OIDC scoping, monorepo selective CI |

***

## Security Quick Reference

```yaml
# Minimal permissions — principle of least privilege
permissions:
  contents: read    # Only what this workflow actually needs

jobs:
  deploy:
    permissions:
      id-token: write   # OIDC — no stored secrets
      contents: read

# Pin actions to commit SHA (not mutable tags)
- uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2

# Never interpolate untrusted input directly in run:
# BAD:  run: echo "${{ github.event.pull_request.title }}"
# GOOD:
- env:
    PR_TITLE: ${{ github.event.pull_request.title }}
  run: echo "$PR_TITLE"
```

***

## When to Use GitHub Actions vs Alternatives

| Tool | Use When |
|:---|:---|
| **GitHub Actions** | Code on GitHub; tight PR integration; OIDC cloud auth; reusable workflows across org |
| **GitLab CI** | Code on GitLab; need built-in SAST/DAST/SCA; deep MR integration; compliance pipelines |
| **Jenkins** | Complex shared library logic; on-prem hardware; existing Jenkins investment |
| **Tekton / Argo Workflows** | Kubernetes-native pipelines; complex DAG task graphs |
| **ArgoCD / Flux** | Kubernetes GitOps CD (not CI — complementary, not competing) |
