---
description: ArgoCD architecture internals, App of Apps pattern, ApplicationSets, and multi-cluster GitOps at scale.
---

# ArgoCD — Architecture & GitOps at Scale

## Core Architecture

```
                    Git Repository
                    (Source of Truth)
                          │
                    ┌─────▼──────┐
                    │  ArgoCD    │
                    │  Server    │ ← API server, UI, gRPC
                    └─────┬──────┘
                          │
              ┌───────────┼───────────┐
              │           │           │
        ┌─────▼─────┐ ┌───▼────┐ ┌───▼─────────┐
        │Application│ │ Repo   │ │   App       │
        │Controller │ │Server  │ │ Controller  │
        │(reconcile)│ │(git)   │ │ (health)    │
        └─────┬─────┘ └────────┘ └─────────────┘
              │
        ┌─────▼────────────────────┐
        │  Target Kubernetes       │
        │  Cluster(s)              │
        └──────────────────────────┘
```

**Key Components:**
- **Application Controller:** Continuously compares desired state (Git) with live state (K8s). Triggers sync when drift is detected.
- **Repo Server:** Clones and renders manifests (Helm, Kustomize, plain YAML). Caches rendered output.
- **API Server:** Serves the UI, CLI (`argocd` binary), and gRPC for automation.
- **ApplicationSet Controller:** Manages fleets of Applications via generators.

***

## Sync Strategies & Options

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/org/gitops-repo
    targetRevision: HEAD
    path: apps/my-app/overlays/production
  destination:
    server: https://kubernetes.default.svc
    namespace: production

  syncPolicy:
    automated:
      prune: true        # Delete resources removed from Git
      selfHeal: true     # Revert manual changes in cluster
    syncOptions:
      - CreateNamespace=true        # Create namespace if missing
      - PrunePropagationPolicy=foreground
      - RespectIgnoreDifferences=true
    retry:
      limit: 5
      backoff:
        duration: 5s
        maxDuration: 3m
        factor: 2        # Exponential backoff
```

***

## App of Apps Pattern

The **App of Apps** pattern uses one "root" ArgoCD Application that deploys other ArgoCD Applications. This is the foundation for managing many services as a single unit.

```
argocd/
  root-app.yaml           ← The "root" app (points to apps/ folder)
  apps/
    frontend-app.yaml     ← ArgoCD Application for frontend
    backend-app.yaml      ← ArgoCD Application for backend
    postgres-app.yaml     ← ArgoCD Application for database
```

**Root Application:**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: root
  namespace: argocd
spec:
  source:
    repoURL: https://github.com/org/gitops-repo
    targetRevision: HEAD
    path: argocd/apps        # Points to the directory of child apps
  destination:
    server: https://kubernetes.default.svc
    namespace: argocd        # Child apps are created IN argocd namespace
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

***

## ApplicationSet — Managing 100 Apps at Once

ApplicationSets generate `Application` objects dynamically from generators. This is the enterprise pattern for multi-environment or multi-cluster deployments.

### List Generator (Different Environments)

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: guestbook
spec:
  generators:
    - list:
        elements:
          - cluster: production
            url: https://prod.k8s.company.com
          - cluster: staging
            url: https://staging.k8s.company.com
  template:
    metadata:
      name: '{{cluster}}-guestbook'
    spec:
      source:
        repoURL: https://github.com/org/gitops
        targetRevision: HEAD
        path: 'apps/guestbook/overlays/{{cluster}}'
      destination:
        server: '{{url}}'
        namespace: guestbook
```

### Git Generator (One App per Directory)

```yaml
generators:
  - git:
      repoURL: https://github.com/org/gitops
      revision: HEAD
      directories:
        - path: "services/*"     # Creates an App for every folder under services/
```

***

## Sync Waves — Ordered Deployment

Use annotations to control the order of resource deployment within a single sync operation.

```yaml
# 1. Deploy CRDs first (wave -1)
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  annotations:
    argocd.argoproj.io/sync-wave: "-1"

# 2. Deploy the database (wave 0)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  annotations:
    argocd.argoproj.io/sync-wave: "0"

# 3. Deploy the application (wave 1 — after DB is ready)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-server
  annotations:
    argocd.argoproj.io/sync-wave: "1"
```

***

## Logic & Trickiness Table

| Concept | Junior Thinking | Senior Thinking |
|:---|:---|:---|
| **selfHeal** | "Always enable it" | Disable if manual hotfixes are needed in prod emergencies |
| **prune: true** | "Always enable it" | Test in staging first — it deletes resources not in Git |
| **App of Apps vs ApplicationSet** | Use App of Apps for everything | Use ApplicationSet for templated, fleet-scale deployments |
| **Multi-cluster** | One ArgoCD per cluster | One central ArgoCD managing many clusters via kubeconfig secrets |
| **Secrets in Git** | Store base64-encoded secrets | Use Sealed Secrets, SOPS, or Vault Agent for real encryption |
