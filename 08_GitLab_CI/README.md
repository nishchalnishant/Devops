# GitLab CI/CD

Comprehensive reference for GitLab CI/CD pipelines, runner management, security scanning,
and enterprise-scale pipeline governance.

***

## What Is in This Module

| File | Purpose |
|:---|:---|
| `cheatsheet.md` | `.gitlab-ci.yml` syntax reference, CLI commands, API |
| `interview-easy.md` | Foundational questions: runners, jobs, stages, artifacts |
| `interview-medium.md` | Intermediate: DAG, environments, caching, templates |
| `interview-hard.md` | Advanced: autoscaling, compliance governance, migration, monorepos |
| `scenarios.md` | Real-world troubleshooting scenarios |
| `notes/gitlab-pipeline-architecture.md` | Deep dive into GitLab CI architecture |

***

## Core Concepts Map

```
GitLab Repository
    │
    ├── .gitlab-ci.yml ──────────────────────► Pipeline
    │                                              │
    ├── include: templates ──────────────────►    ├── Stage 1 (build)
    │                                              │       ├── job-a (runner A)
    └── CI/CD Variables ──────────────────────►    │       └── job-b (runner B)
                                                   │
                                                   ├── Stage 2 (test)
                                                   │       └── unit-test
                                                   │
                                                   └── Stage 3 (deploy)
                                                           └── deploy-staging (environment)
```

***

## Interview Focus Areas

| Difficulty | Key Topics |
|:---|:---|
| **Easy** | `.gitlab-ci.yml` structure, runners, stages vs jobs, artifacts vs cache, environments |
| **Medium** | DAG with `needs:`, rules vs only/except, includes, multi-project pipelines, secrets |
| **Hard** | Runner autoscaling (K8s/EC2), compliance governance (500+ teams), Jenkins migration, monorepo selective CI, CI Components |

***

## Key Differentiators from GitHub Actions

| Feature | GitLab CI | GitHub Actions |
|:---|:---|:---|
| **Built-in Container Registry** | Yes — free, included | GitHub Packages (free with limits) |
| **Built-in security scanning** | SAST, DAST, SCA, secret detection built-in | 3rd-party actions required |
| **Self-hosted control** | Full control with GitLab self-managed | GitHub Enterprise |
| **DAG pipelines** | `needs:` keyword | No native DAG — stage-based only |
| **Merge request integration** | Deep (security findings in MR widget) | Check runs only |
| **Compliance frameworks** | GitLab Compliance Pipelines | Required Workflows (Enterprise only) |

***

## Quick Reference — Most Useful Keywords

```yaml
# Conditional execution (modern, preferred)
rules:
  - if: $CI_COMMIT_BRANCH == "main"
  - if: $CI_PIPELINE_SOURCE == "merge_request_event"
  - changes: [src/**/*]

# Skip stage ordering — run as soon as dependencies are ready
needs: [build-frontend]

# Control retry behavior
retry:
  max: 2
  when: [runner_system_failure, stuck_or_timeout_failure]

# Manual deployment gate
when: manual
environment: production

# Import shared templates (DRY pipelines)
include:
  - project: 'platform/ci-templates'
    ref: 'v1.0'
    file: '/templates/docker-build.yml'
  - template: 'Security/SAST.gitlab-ci.yml'
```
