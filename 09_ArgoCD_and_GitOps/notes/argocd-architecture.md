---
description: ArgoCD architecture internals, App of Apps pattern, ApplicationSets, and multi-cluster GitOps at scale.
---

# ArgoCD — Architecture & GitOps at Scale

```
ArgoCD Architecture & GitOps at Scale
├── Core Architecture
│   ├── argocd-server: API Server — gRPC/REST, UI, webhook receiver, RBAC enforcement
│   ├── argocd-repo-server: renders manifests (Helm, Kustomize, Jsonnet, plain YAML, CMP)
│   ├── argocd-application-controller: reconciliation loop per Application, computes diff
│   ├── Redis: caches rendered manifests — avoids re-clone/re-render on every reconcile
│   └── Dex (optional): OIDC bridge for SSO (GitHub, LDAP, SAML)
│
├── Sync Strategies & Options
│   ├── Manual sync: human triggers argocd app sync or UI click
│   ├── Automated sync: syncPolicy.automated triggers on Git change detection
│   ├── selfHeal: true — reverts direct cluster edits within reconcile interval
│   ├── prune: true — deletes resources removed from Git (opt-in, test in staging first)
│   └── syncOptions: CreateNamespace | ServerSideApply | ApplyOutOfSyncOnly | PruneLast
│
├── App of Apps Pattern
│   ├── Root Application points to directory of Application manifests
│   ├── Each Application YAML defines source (Git path) + destination (cluster+namespace)
│   ├── Add new service: commit Application manifest to the directory
│   └── Bootstrap: create root Application once; everything else self-manages
│
├── ApplicationSet Generators
│   ├── list: explicit items → one Application per item
│   ├── cluster: one Application per registered cluster (filter by labels)
│   ├── git (directories): one Application per matching directory glob
│   ├── git (files): one Application per matching config file in Git
│   └── matrix: cross-product of two generators (apps × clusters)
│
├── Sync Waves (Ordered Deployment)
│   ├── argocd.argoproj.io/sync-wave: "N" — ascending wave order
│   ├── Wave 0: namespaces, CRDs — must exist before resources in later waves
│   ├── Wave 1: infrastructure (cert-manager, ingress controller)
│   ├── Wave 2: platform services (external-secrets, prometheus)
│   └── Wave 3+: application workloads
│
└── Logic & Trickiness
    ├── selfHeal — disable during incident investigation; re-enable after
    ├── prune: true — test in staging; deletes cluster resources removed from Git
    ├── App of Apps vs ApplicationSet — use ApplicationSet for templated fleet scale
    ├── Multi-cluster — one central ArgoCD via cluster secrets, not one per cluster
    └── Secrets in Git — Sealed Secrets / SOPS / Vault, never base64-encoded plaintext
```

## First Principles

- ArgoCD's value is the continuous reconciliation loop: every few minutes (or on webhook), it asks "does the cluster match Git?" and corrects the answer if no. This is fundamentally different from CI/CD which asks "was the deploy job triggered?"
- The repo-server is the CPU-intensive component: it clones repos, runs `helm template`, runs `kustomize build`, executes CMP plugins. Redis caches the output so subsequent reconciliation loops don't re-clone. Scale repo-server horizontally for large Helm charts or many repositories.
- App of Apps is a bootstrapping pattern, not a management pattern. Once bootstrapped, each child Application is independent. ApplicationSet is the management pattern: it generates and lifecycle-manages Applications from a template.
- Sync waves solve resource ordering without imperative scripts. The wave number is a deployment phase annotation — it expresses "this resource must exist and be healthy before the next wave starts."

## Push vs. Pull GitOps Models

Understanding the architectural shift from traditional push-based CI/CD pipelines to pull-based GitOps reconciliation models is key to mastering ArgoCD.

```mermaid
flowchart TD
    subgraph PushModel["1. Traditional Push-Based Model"]
        direction LR
        DevPush["Developer"] -->|1. Commit & Push| RepoPush["Git Repository"]
        RepoPush -->|2. Webhook Event| CIPipeline["CI Pipeline (e.g., Jenkins/GHA)"]
        CIPipeline -->|3. Push Deploy (kubectl apply) <br/>Requires high-privilege credentials stored in CI| ClusterPush["Target Kubernetes Cluster"]
    end

    subgraph PullModel["2. GitOps Pull-Based Model (ArgoCD)"]
        direction LR
        DevPull["Developer"] -->|1. Commit & Push| RepoPull["Git Repository"]
        ArgoCD["ArgoCD Controller (In-Cluster)"] -->|2. Poll / Webhook (Read Only)| RepoPull
        ArgoCD -->|3. Reconcile Loop & Live Diff| ClusterPull["Target Kubernetes Cluster"]
        ClusterPull -.->|State Drift| ArgoCD
    end

    classDef pushStyle fill:#ffebeb,stroke:#ffb3b3,stroke-width:2px,color:#000;
    classDef pullStyle fill:#ebf5ff,stroke:#adc8ff,stroke-width:2px,color:#000;
    class PushModel pushStyle;
    class PullModel pullStyle;
```

### Architectural Trade-offs

| Attribute | Push-Based Model (Traditional CI) | Pull-Based Model (ArgoCD GitOps) |
| :--- | :--- | :--- |
| **Credential Boundary** | **Externalized**: High-privilege kubeconfig/keys are stored outside the cluster (e.g., in CI runner secrets). | **Internalized**: Credentials remain local to the cluster (ArgoCD uses local ServiceAccounts/IRSA). |
| **Drift Detection** | **None**: If someone manually edits a resource using kubectl, the CI system has no awareness until the next execution. | **Continuous**: ArgoCD tracks active cluster state and flags any differences as "OutOfSync" within minutes. |
| **Self-Healing** | **Manual Intervention**: Requires manually triggering a pipeline rerun or repairing the resource. | **Automated**: If `selfHeal: true` is enabled, ArgoCD automatically overwrites cluster changes to match Git. |
| **Security Auditing** | **Pipeline Logs**: Audits are scattered across CI system runner histories and build logs. | **Git History**: Complete audit trail of cluster state is naturally maintained in Git commit logs. |

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

***

## System Design Perspective

**Application controller sharding mechanics**

The application-controller maintains an in-memory cache of all Application states and runs reconciliation loops. At 1000+ Applications across 100+ clusters, a single controller instance exhausts memory and falls behind on reconciliation SLAs. Sharding (`ARGOCD_CONTROLLER_REPLICAS=N`) uses a consistent hash of the Application name to assign each Application to one controller shard. Each shard only reconciles its assigned Applications — memory and CPU scale linearly with shard count. The argocd-server is stateless and routes API requests to the correct shard via cluster metadata stored in the `argocd` namespace.

**App of Apps vs ApplicationSet selection guide**

Use App of Apps when: you need a bootstrap mechanism, each Application has unique non-templatable configuration, or you have a small static set of Applications that rarely change. Use ApplicationSet when: you're deploying the same application to many clusters, you have a dynamic set of targets (new clusters are added regularly), or you want automatic Application lifecycle management (create on new cluster registration, delete on cluster deregistration). The key difference: App of Apps requires a human to commit an Application manifest for each new target; ApplicationSet creates Applications automatically when the generator discovers new targets.

**Webhook event processing**

ArgoCD receives webhook events at `/api/webhook`. On receiving a push event, it marks affected repositories as "stale" and triggers an immediate reconciliation cycle for Applications that use that repository. Without webhooks, the reconciliation cycle runs on `timeout.reconciliation` (default 3 minutes). For organizations with many small commits (feature branch workflows), webhooks are essential — a 3-minute reconciliation lag means staging environments are consistently 3 minutes behind commits. Webhook secret validation uses HMAC-SHA256; a mismatch causes silent rejection (event ignored, no error logged at warning level).
