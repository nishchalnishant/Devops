# GitHub Actions

GitHub Actions is the native CI/CD platform built into GitHub. Workflows are defined as YAML files in `.github/workflows/` and triggered by repository events (push, pull_request, schedule, workflow_dispatch, etc.).

## Key Concepts

| Concept | Description |
|---------|-------------|
| **Workflow** | YAML file defining the automation; triggered by events |
| **Job** | Group of steps that run on the same runner; jobs run in parallel by default |
| **Step** | Individual task within a job (run a command or use an action) |
| **Action** | Reusable unit of automation (`uses: actions/checkout@v4`) |
| **Runner** | Machine (GitHub-hosted or self-hosted) that executes jobs |
| **Event** | Trigger that starts a workflow (`push`, `pull_request`, `schedule`, `workflow_dispatch`) |
| **Context** | Objects exposing runtime data (`github`, `env`, `secrets`, `needs`, `matrix`) |
| **Expression** | `${{ }}` syntax for dynamic values in YAML |

## Directory Contents

| File | Purpose |
|------|---------|
| `notes/notes.md` | Core concepts, OIDC, reusable workflows, matrix strategy |
| `cheatsheet.md` | Quick-reference syntax, common patterns, context cheatsheet |
| `interview-easy.md` | Junior/mid-level interview questions |
| `interview-medium.md` | Senior-level interview questions |
| `interview-hard.md` | Staff/architect-level interview questions |
| `scenarios.md` | Real-world troubleshooting scenarios |

## When to Use GitHub Actions vs Alternatives

- **GitHub Actions**: Primary choice when code is on GitHub; tight GitHub integration (PR checks, deploy environments, CODEOWNERS)
- **Jenkins**: When you need complex shared library logic, on-prem runners with hardware access, or existing Jenkins investment
- **GitLab CI**: When code is on GitLab; built-in container registry, environments, DAST/SAST
- **ArgoCD**: For Kubernetes GitOps (not CI — ArgoCD is CD only)
