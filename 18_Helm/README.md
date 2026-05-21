# Helm — Kubernetes Package Manager

```
Helm — Kubernetes Package Manager
├── Core Concepts
│   ├── Chart: versioned package (Chart.yaml + values.yaml + templates/ + charts/)
│   ├── Release: deployed instance of a chart tracked as K8s Secret
│   ├── Revision: increments on each upgrade; rollback restores previous revision
│   ├── Values: default in values.yaml; overridden by --values file or --set flag
│   ├── Repository: classic (index.yaml + tarballs) or OCI (registry protocol)
│   ├── Hook: lifecycle Job (pre-install, post-upgrade, pre-rollback, test)
│   └── Subchart: dependency chart inside parent; values namespaced by chart name
├── Chart Structure
│   ├── Chart.yaml: name, version (SemVer), appVersion, dependencies list
│   ├── values.yaml: default values; merged with user overrides at render time
│   ├── templates/: Go templates + Sprig functions; accessed via .Values, .Release
│   ├── templates/_helpers.tpl: named templates (define/include/template)
│   ├── crds/: raw CRD manifests installed before templates; not upgraded by Helm
│   └── charts/: vendored subchart directories (or pulled via helm dependency update)
├── Values Merging Order (lowest to highest precedence)
│   ├── 1. values.yaml (chart defaults)
│   ├── 2. subchart values (parent.subchart-name.key)
│   ├── 3. --values / -f flags (left to right)
│   └── 4. --set flags (highest precedence; dot-path syntax)
├── Lifecycle Hooks
│   ├── pre-install / post-install: before/after first creation of resources
│   ├── pre-upgrade / post-upgrade: before/after resource updates
│   ├── pre-rollback / post-rollback: before/after rollback to previous revision
│   ├── pre-delete / post-delete: before/after helm uninstall
│   ├── test: run with helm test; validates release health
│   ├── Hook weight: execution order within same phase (ascending integer)
│   └── hook-delete-policy: before-hook-creation, hook-succeeded, hook-failed
├── Templating Engine
│   ├── Go text/template: {{ }}, {{- }} (trim whitespace), range, if/else, with
│   ├── Sprig functions: quote, toYaml, indent, required, default, tpl
│   ├── Named templates: define in _helpers.tpl; include with indent; template without
│   ├── .Values: user/chart values; .Release: name/namespace/revision; .Chart: metadata
│   └── Library charts: type: library in Chart.yaml; no rendered templates, only helpers
├── Repository & OCI
│   ├── Classic: helm repo add + index.yaml; Artifact Hub for discovery
│   ├── OCI: helm push/pull to container registry; no index.yaml needed
│   └── Private: Harbor, AWS ECR, GCR, Azure ACR all support OCI Helm charts
├── GitOps Integration
│   ├── ArgoCD: uses helm template (not helm install); manages release state externally
│   ├── ArgoCD hooks: Argo PreSync/Sync/PostSync replaces Helm hooks in GitOps mode
│   ├── Flux HelmRelease: CRD-driven; values from ConfigMap or Secret
│   └── Helmfile: orchestrate multiple releases with ordering (needs:) and env layering
└── Key CLI Commands
    ├── helm install <name> <chart> --values env.yaml
    ├── helm upgrade --install <name> <chart> --set image.tag=v1.2.3
    ├── helm rollback <name> <revision>
    ├── helm diff upgrade (helm-diff plugin; shows what will change)
    ├── helm template: render locally without cluster; used by ArgoCD
    └── helm test <name>: runs test hooks against deployed release
```

## First Principles

- Kubernetes YAML is repetitive across environments. Helm = templating engine + package manager for K8s. Without Helm, teams copy-paste manifests and manually diff environments — this creates configuration drift.
- Chart = versioned package. Values = environment-specific overrides. Release = deployed instance of a chart. These three concepts map directly to: what (chart), how (values), where (release in a namespace).
- Hooks = lifecycle actions. Hooks enable database migrations, smoke tests, and secret rotation as part of the upgrade — they are Jobs with annotations, not sidecar containers.
- ArgoCD uses `helm template`, not `helm install`. ArgoCD owns the release state; Helm is just the renderer. Helm hooks are ignored — use ArgoCD sync waves and hooks instead.
- OCI is the future of chart distribution. Classic `index.yaml`-based repos are being replaced by OCI registries, which reuse the existing container registry infrastructure.

Helm is the de facto package manager for Kubernetes. It bundles Kubernetes manifests into "charts" — versioned, distributable packages with templating and lifecycle management. Every Kubernetes engineer needs to understand Helm to deploy and manage production workloads.

***

## What Is in This Module

| File | Purpose |
|:---|:---|
| `notes/helm-fundamentals.md` | Charts, templates, values, releases, repositories |
| `cheatsheet.md` | CLI reference, template functions, value override patterns |
| `interview.md` | Consolidated Interview Questions: Easy, Medium, and Hard levels |
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

***

## System Design Perspective

**Multi-Environment Helm Architecture**
- One chart, three value files: `values-dev.yaml`, `values-staging.yaml`, `values-prod.yaml`. CI renders each with `helm template` and applies via `kubectl apply` or ArgoCD Application.
- Secrets: never store in values files. Use External Secrets Operator to inject from Vault/AWS Secrets Manager into K8s Secrets that the chart references by name.
- Release naming convention: `<service>-<env>` (e.g., `payments-prod`) — prevents collision when the same chart is deployed to multiple environments in the same cluster.

**Helmfile for Multi-Chart Platform**
```yaml
# helmfile.yaml — order-controlled multi-release orchestration
releases:
  - name: cert-manager
    chart: jetstack/cert-manager
    namespace: cert-manager
  - name: ingress-nginx
    chart: ingress-nginx/ingress-nginx
    needs: [cert-manager/cert-manager]   # waits for cert-manager to be ready
  - name: my-app
    chart: ./charts/my-app
    needs: [ingress-nginx/ingress-nginx]
    values:
      - values/{{ .Environment.Name }}.yaml
```

**Helm in GitOps (ArgoCD)**
- ArgoCD Application points to a chart + values file in Git. On every commit, ArgoCD runs `helm template` and applies the diff — Helm's release Secret is not used.
- Helm hooks are silently ignored by ArgoCD. Database migrations must be moved to ArgoCD PreSync hooks (a separate Job Sync Wave -1) or init containers.
- CRD upgrade limitation: Helm only installs CRDs on `helm install`, never on `helm upgrade`. For CRD updates, use a separate Job or Flux `HelmRelease` with `crds: CreateReplace`.