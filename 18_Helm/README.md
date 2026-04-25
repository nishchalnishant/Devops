# Helm — Kubernetes Package Manager

Helm is the de facto package manager for Kubernetes. It bundles Kubernetes manifests into "charts" — versioned, distributable packages with templating and lifecycle management. Every Kubernetes engineer needs to understand Helm to deploy and manage production workloads.

***

## What Is in This Module

| File | Purpose |
|:---|:---|
| `notes/helm-fundamentals.md` | Charts, templates, values, releases, repositories |
| `cheatsheet.md` | CLI reference, template functions, value override patterns |
| `interview-easy.md` | Foundational: what is Helm, charts, releases, values |
| `interview-medium.md` | Intermediate: lifecycle, hooks, subcharts, OCI registry |
| `interview-hard.md` | Advanced: operators vs Helm, chart testing, Helmfile, production patterns |
| `scenarios.md` | Real-world troubleshooting and chart design scenarios |

***

## The Core Mental Model

```
Helm Chart (blueprint)
    ├── Chart.yaml          ← Metadata (name, version, description)
    ├── values.yaml         ← Default configuration values
    ├── templates/          ← Go-templated Kubernetes YAML
    │   ├── deployment.yaml
    │   ├── service.yaml
    │   ├── ingress.yaml
    │   └── _helpers.tpl    ← Reusable template snippets
    └── charts/             ← Subcharts (dependencies)

         +   values.yaml overrides (per-environment)

         ↓   helm install / helm upgrade

Kubernetes Release (running instance)
    ├── Deployment (3 replicas)
    ├── Service
    └── Ingress
    
    Helm tracks this in a Secret in the namespace (release history)
```

***

## Key Concepts

| Concept | Definition |
|:---|:---|
| **Chart** | Package containing templates + default values |
| **Release** | A chart installed into a cluster (has a name and namespace) |
| **Revision** | Version of a release (increments on each upgrade) |
| **Values** | Configuration injected into templates at render time |
| **Repository** | Collection of charts (artifact hub, OCI registry) |
| **Hook** | Kubernetes Job running at specific lifecycle events (pre-install, post-upgrade) |
| **Subchart** | A dependency chart bundled inside a parent chart |

***

## Interview Focus Areas

| Difficulty | Key Topics |
|:---|:---|
| **Easy** | Charts vs releases, `helm install/upgrade/rollback`, values override, `--dry-run` |
| **Medium** | Hooks and their use cases, subchart dependencies, OCI chart registries, `helm test` |
| **Hard** | Helmfile for multi-chart orchestration, chart library patterns, ArgoCD + Helm integration, Helm vs Operators |

***

## Helm vs Kustomize — Decision Guide

| Aspect | Helm | Kustomize |
|:---|:---|:---|
| **Paradigm** | Templating (Go templates) | Patching (YAML overlays) |
| **Packaging** | Yes — versioned, distributable charts | No — directory-based, not a registry concept |
| **Lifecycle** | Full (install, upgrade, rollback, test) | None (apply only; ArgoCD handles lifecycle) |
| **Learning curve** | Moderate (Go templates, values merging) | Low (pure YAML patches) |
| **Best for** | Distributing apps as packages; many config options | Simple env-specific customization; thin wrapper over raw YAML |
| **ArgoCD support** | Yes (renders with `helm template`) | Yes (native support) |

**Rule of thumb:** Use Helm when distributing a complex application with many configurable parameters. Use Kustomize when applying minor per-environment patches to a base set of manifests you own.
