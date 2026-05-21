# Progressive Delivery & GitOps at Scale

```
Progressive Delivery & GitOps at Scale
├── GitOps Fundamentals
│   ├── 4 Principles: Declarative | Versioned+Immutable | Automated Delivery | Continuous Reconciliation
│   ├── Traditional CI/CD: push-based, kubectl apply from pipeline, drift accumulates
│   └── GitOps: pull-based, operator inside cluster, drift corrected automatically
│
├── ArgoCD Architecture Internals
│   ├── Reconciliation loop: compare desired (Git) vs live (K8s API) → apply delta
│   ├── argocd-repo-server: renders manifests (Helm/Kustomize/plain YAML), cached in Redis
│   ├── argocd-application-controller: owns reconciliation loop per Application
│   └── Webhook: immediate reconcile on Git push (vs 3-min poll without webhook)
│
├── ApplicationSets at Scale
│   ├── cluster generator: one Application per registered cluster, filtered by labels
│   ├── git directory generator: one Application per directory in Git repo
│   └── matrix generator: cross-product (services × clusters)
│
├── App of Apps Pattern
│   ├── Root Application → directory of child Application manifests
│   ├── Add service: commit Application YAML; ArgoCD creates it automatically
│   └── Bootstrap: create root Application once; everything else self-manages
│
├── Argo Rollouts (Progressive Delivery)
│   ├── Rollout CRD: replaces Deployment for traffic-managed deployments
│   ├── Canary steps: setWeight → pause → setWeight → analysis → full promotion
│   ├── AnalysisTemplate: Prometheus SLI query, successCondition, failureLimit
│   └── Traffic providers: Nginx Ingress (weight annotation), Istio VirtualService, AWS ALB
│
├── External Secrets Operator
│   ├── ExternalSecret CRD: references path in Vault/AWS SM/Azure KV
│   ├── Controller fetches value and creates/updates Kubernetes Secret
│   └── refreshInterval: auto-rotation without Pod restart (Reloader for Pod restart)
│
├── ArgoCD Image Updater
│   ├── Watches registry for new image tags
│   ├── updateStrategy: semver | latest | name | digest
│   └── Write-back: commits updated image tag to Git (git or argocd write-back)
│
├── RBAC & Multi-Tenancy (AppProject)
│   ├── sourceRepos: restrict which Git repos a team can deploy from
│   ├── destinations: restrict which clusters + namespaces are accessible
│   └── argocd-rbac-cm: role → resource/action/app-in-project policy
│
└── Key Gotchas
    ├── selfHeal reverts manual kubectl changes — expected, commit to Git instead
    ├── prune: true deletes resources not in Git — test in staging first
    ├── App of Apps vs ApplicationSet — use ApplicationSet for fleet scale
    ├── Secrets must be encrypted — never base64-encoded plaintext in Git
    └── Rollout with Nginx requires Nginx Ingress — ALB needs different provider
```

## First Principles

- Progressive delivery is GitOps applied to the deployment process itself. The Rollout spec in Git is the desired delivery strategy — gradual traffic shift with automated rollback criteria. The controller executes the strategy; no human needs to monitor and manually promote.
- AnalysisTemplate turns SLIs into deployment gates. The Prometheus query defines "what does healthy mean?" The `successCondition` and `failureLimit` define the acceptance threshold. These are auditable, reviewable, and version-controlled — better than a human eyeballing a dashboard.
- External Secrets Operator solves the fundamental GitOps secret problem: you cannot commit secrets to Git in plaintext, but you need secret values to deploy. ESO decouples the secret reference (safe to commit) from the secret value (fetched at runtime from a secret store).
- Image Updater closes the GitOps loop: image builds happen in CI (push-based), but the image tag update to Git is a pull-based write-back. The cluster always runs what Git says; Image Updater ensures Git says the latest validated image.
- AppProject RBAC is namespace-for-deployments, not namespace-for-resources. It restricts which Git repos a team can deploy from and which clusters/namespaces they can deploy to — preventing accidental or malicious cross-team deployments.

## What is GitOps and Why Does It Matter?

**GitOps** is an operational framework that uses Git as the single source of truth for infrastructure and application configuration. It extends Infrastructure as Code (IaC) principles to the entire software delivery lifecycle.

**The Four Principles of GitOps:**

1. **Declarative:** The entire system state is described declaratively (YAML manifests)
2. **Versioned & Immutable:** Git stores every change with full history and audit trail
3. **Automated Delivery:** Changes are automatically applied to match the declared state
4. **Continuous Reconciliation:** Software agents continuously compare actual state with desired state and correct drift

```
Traditional CI/CD:     Git → CI → CD → kubectl apply → (manual kubectl changes) → DRIFT
                       
GitOps:                Git → CI → (commit to config repo) → ArgoCD reconciles → NO DRIFT
                                                                        (auto-corrects)
```

**Why GitOps for Kubernetes?**

- **Audit trail:** Every cluster change is a Git commit with author, timestamp, and PR discussion
- **Rollback:** `git revert` is safer than `kubectl rollout undo`
- **Drift detection:** ArgoCD alerts when someone makes manual `kubectl` changes
- **Multi-cluster:** Deploy the same manifest to 100 clusters with ApplicationSets
- **Separation of concerns:** Developers own app manifests; platform owns cluster config

***

## What is Progressive Delivery?

Progressive delivery is a deployment pattern that reduces risk by gradually shifting traffic to new versions while automatically monitoring for problems.

**Traditional Deployment:**
```
Blue-Green:  100% traffic → Blue → Switch → 100% traffic → Green
             (instant cutover, instant rollback if problems)
```

**Progressive Delivery (Canary):**
```
Step 1:  95% v1 / 5% v2   → monitor metrics
Step 2:  75% v1 / 25% v2  → monitor metrics
Step 3:  50% v1 / 50% v2  → monitor metrics
Step 4:  0% v1 / 100% v2  → complete
```

**Benefits:**
- Catch bugs before they affect all users
- Automatic rollback if error rates spike
- Test with real production traffic (not staging)
- Business metric validation (conversion rates, latency)

***

## ArgoCD Architecture Internals

```
ArgoCD Components (runs in argocd namespace):
┌─────────────────────────────────────────────────────────┐
│  argocd-server (API + gRPC + UI)                        │
│  argocd-application-controller (reconciler)             │
│  argocd-repo-server (Git fetch + manifest rendering)    │
│  argocd-dex-server (OIDC/SSO)                           │
│  argocd-notifications-controller                        │
└─────────────────────────────────────────────────────────┘

Reconciliation loop (application-controller):
    1. Compare desired state (Git) vs. live state (cluster)
    2. If diff found → mark OutOfSync
    3. If auto-sync enabled → apply diff via kubectl apply
    4. Watch for resource health (Deployment rollout, Job completion)
    5. Mark Synced + Healthy or Synced + Degraded
```

**Sync waves:** Control order of resource creation within a sync operation.
```yaml
# Apply CRDs before controllers, controllers before apps
metadata:
  annotations:
    argocd.argoproj.io/sync-wave: "-1"  # CRD first
***
metadata:
  annotations:
    argocd.argoproj.io/sync-wave: "0"   # controller
***
metadata:
  annotations:
    argocd.argoproj.io/sync-wave: "1"   # application resources
```

***

## ApplicationSets — Fleet Management

```yaml
# Cluster Generator — deploy to all clusters in the fleet
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: platform-stack
  namespace: argocd
spec:
  generators:
  - clusters:
      selector:
        matchLabels:
          env: production   # only prod clusters
  template:
    metadata:
      name: '{{name}}-platform'   # {{name}} = cluster name
    spec:
      project: platform
      source:
        repoURL: https://github.com/myorg/platform-config
        targetRevision: HEAD
        path: 'platform/{{metadata.labels.region}}'  # per-region config
      destination:
        server: '{{server}}'   # cluster API URL from ArgoCD cluster registration
        namespace: platform
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
        syncOptions:
        - CreateNamespace=true

# Git Generator — one app per directory in the repo
- git:
    repoURL: https://github.com/myorg/services
    revision: HEAD
    directories:
    - path: "services/*"
    - path: "services/legacy"
      exclude: true
  template:
    metadata:
      name: '{{path.basename}}'   # directory name becomes app name
    spec:
      source:
        path: '{{path}}'

# Matrix Generator — cross product (every app on every cluster)
- matrix:
    generators:
    - clusters: {}
    - git:
        directories:
        - path: "apps/*"
```

***

## App-of-Apps Pattern

```yaml
# Root app — manages all other apps
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: root
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/myorg/gitops
    targetRevision: HEAD
    path: apps/            # directory containing Application manifests
  destination:
    server: https://kubernetes.default.svc
    namespace: argocd
  syncPolicy:
    automated:
      prune: true
      selfHeal: true

# apps/monitoring.yaml — managed by root app
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: monitoring
  namespace: argocd
  finalizers:
  - resources-finalizer.argocd.argoproj.io   # delete resources when app deleted
spec:
  source:
    chart: kube-prometheus-stack
    repoURL: https://prometheus-community.github.io/helm-charts
    targetRevision: "55.5.0"
    helm:
      valuesFiles: [values-prod.yaml]
  destination:
    server: https://kubernetes.default.svc
    namespace: monitoring
```

***

## Argo Rollouts — Progressive Delivery

### Canary with AnalysisTemplate

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: checkout-service
spec:
  replicas: 20
  selector:
    matchLabels:
      app: checkout
  template:
    metadata:
      labels:
        app: checkout
    spec:
      containers:
      - name: checkout
        image: myregistry.io/checkout:v2.1.0
  strategy:
    canary:
      canaryService: checkout-canary
      stableService: checkout-stable
      trafficRouting:
        nginx:
          stableIngress: checkout-ingress
      steps:
      - setWeight: 5      # 5% → canary
      - pause: {duration: 5m}
      - analysis:
          templates:
          - templateName: success-rate
          args:
          - name: service-name
            value: checkout-canary
      - setWeight: 25
      - pause: {duration: 10m}
      - analysis:
          templates:
          - templateName: success-rate
      - setWeight: 50
      - pause: {duration: 10m}
      - setWeight: 100
***
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: success-rate
spec:
  args:
  - name: service-name
  metrics:
  - name: success-rate
    interval: 1m
    successCondition: result[0] >= 0.99
    failureLimit: 3
    provider:
      prometheus:
        address: http://prometheus.monitoring.svc:9090
        query: |
          sum(rate(http_requests_total{service="{{args.service-name}}",status!~"5.."}[5m]))
          /
          sum(rate(http_requests_total{service="{{args.service-name}}"}[5m]))
  - name: latency-p99
    interval: 1m
    successCondition: result[0] <= 0.3
    provider:
      prometheus:
        query: |
          histogram_quantile(0.99,
            sum by (le) (rate(http_request_duration_seconds_bucket{service="{{args.service-name}}"}[5m]))
          )
```

```bash
# Monitor rollout progress
kubectl argo rollouts get rollout checkout-service --watch

# Manual promotion (skip pause)
kubectl argo rollouts promote checkout-service

# Abort and roll back to stable
kubectl argo rollouts abort checkout-service
kubectl argo rollouts undo checkout-service
```

***

## External Secrets Operator (ESO)

```yaml
# ClusterSecretStore — references AWS Secrets Manager
apiVersion: external-secrets.io/v1beta1
kind: ClusterSecretStore
metadata:
  name: aws-secrets
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-east-1
      auth:
        jwt:
          serviceAccountRef:
            name: eso-sa
            namespace: external-secrets
***
# ExternalSecret — what to sync and how
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: db-credentials
  namespace: production
spec:
  refreshInterval: 1h    # re-sync interval
  secretStoreRef:
    name: aws-secrets
    kind: ClusterSecretStore
  target:
    name: db-credentials     # name of the Kubernetes Secret to create
    creationPolicy: Owner    # ESO owns the secret; deletes when ExternalSecret deleted
    template:
      type: kubernetes.io/basic-auth
      data:
        username: "{{ .username }}"
        password: "{{ .password }}"
  data:
  - secretKey: username
    remoteRef:
      key: prod/db/credentials    # AWS Secrets Manager secret name
      property: username          # JSON key within the secret
  - secretKey: password
    remoteRef:
      key: prod/db/credentials
      property: password
```

***

## Image Updater — Automated Image Promotion

```yaml
# ArgoCD Image Updater — watches registry, auto-commits new tags
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
  annotations:
    argocd-image-updater.argoproj.io/image-list: myapp=myregistry.io/myapp
    argocd-image-updater.argoproj.io/myapp.update-strategy: semver
    argocd-image-updater.argoproj.io/myapp.allow-tags: regexp:^v[0-9]+\.[0-9]+\.[0-9]+$
    argocd-image-updater.argoproj.io/write-back-method: git   # commits tag back to repo
    argocd-image-updater.argoproj.io/git-branch: main
```

***

## Crossplane — GitOps for Infrastructure

```yaml
# Define an RDS instance as a Kubernetes resource
apiVersion: database.example.org/v1alpha1
kind: PostgreSQLInstance
metadata:
  name: prod-db
  namespace: production
spec:
  parameters:
    storageGB: 100
    instanceClass: db.r6g.large
    engineVersion: "15"
    multiAZ: true
  compositionRef:
    name: postgresql-aws
  writeConnectionSecretToRef:
    name: prod-db-connection   # ESO-like: Crossplane writes connection info as Secret
```

ArgoCD reconciles the `PostgreSQLInstance` manifest. Crossplane's provider-aws controller calls the AWS RDS API. The database is GitOps-managed end-to-end — no Terraform, no manual Console operations.

***

## ArgoCD RBAC and Projects

```yaml
# AppProject — restrict what an Application can do
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: payments
  namespace: argocd
spec:
  sourceRepos:
  - 'https://github.com/myorg/payments-*'
  destinations:
  - namespace: payments
    server: https://kubernetes.default.svc
  - namespace: payments-*
    server: 'https://prod-cluster.example.com'
  clusterResourceWhitelist: []   # no cluster-scoped resources
  namespaceResourceBlacklist:
  - group: ''
    kind: ResourceQuota
  roles:
  - name: developer
    policies:
    - p, proj:payments:developer, applications, get, payments/*, allow
    - p, proj:payments:developer, applications, sync, payments/*, allow
    groups:
    - payments-engineers
```

```yaml
# argocd-rbac-cm ConfigMap — global RBAC policy
policy.default: role:readonly
policy.csv: |
  p, role:platform-admin, *, *, */*, allow
  p, role:developer, applications, get, */*, allow
  p, role:developer, applications, sync, */*, allow
  g, platform-team, role:platform-admin
  g, developers, role:developer
```

***

## Key Gotchas

| Gotcha | Detail |
|--------|--------|
| `selfHeal: true` reverts manual kubectl changes | ArgoCD will revert any drift — use `argocd.argoproj.io/sync-options: Prune=false` to exempt resources |
| Helm `values.yaml` in a sub-chart is not loaded | Must explicitly reference `valuesFiles` in the Application source |
| ApplicationSet `generators` order matters | Matrix generators can produce very large sets — test with `--dry-run` |
| `syncwave` only applies within a sync operation | Resources in different Applications don't coordinate via waves |
| Image Updater needs Git write access | Requires a deploy key or token with push access to the config repo |
| `prune: true` deletes resources removed from Git | Safe for apps, dangerous for namespace-wide CRDs shared between apps |
| Rollout with `nginx` traffic routing requires Nginx Ingress | Won't work with ALB Ingress Controller without an additional provider plugin |
| Analysis failure rolls back only the current step | Must set `autoPromotionEnabled: false` and configure `failureLimit` carefully |

***

## System Design Perspective

**Argo Rollouts traffic routing architecture**

Argo Rollouts manipulates traffic at the Ingress or service mesh layer — it does not use pod replica count alone. With NGINX Ingress: the controller annotates the Ingress with `nginx.ingress.kubernetes.io/canary-weight: 20` to send 20% of traffic to the canary Deployment's service. With Istio: it configures a VirtualService with weighted route rules. With AWS ALB: it creates weighted target groups. The Rollout controller manages these annotations/resources in sync with canary promotion steps. If the traffic routing resource is deleted externally, the Rollout's analysis may continue but traffic split won't be enforced — the Rollout will show `Healthy` but serve 100% to stable.

**GitOps × FinOps integration**

The GitOps repo is the enforcement point for cost policy. OPA/Kyverno admission policies in the cluster enforce resource requests and limits — ArgoCD syncing a Deployment without resource limits will be rejected by the admission webhook, causing a SyncFailed state. This surfaces the cost policy violation in the ArgoCD UI before the application ever runs. Infracost in the CI pipeline adds a pre-merge cost estimate for Terraform changes. Kubecost aggregates actual spend by ArgoCD `app.kubernetes.io/name` label — enabling per-application cost tracking without modifying application code.

**Crossplane vs Terraform in GitOps**

Crossplane runs inside Kubernetes and manages cloud resources via CRDs — RDS instances, S3 buckets, VPCs are Kubernetes resources that ArgoCD can manage. This eliminates the Terraform/ArgoCD boundary: everything is a Kubernetes resource, everything is managed by ArgoCD, everything is in Git. The tradeoff: Crossplane has less mature state management than Terraform (no plan/apply cycle, no state file), and migrating existing Terraform-managed infrastructure to Crossplane requires careful import. The pattern is complementary: Terraform bootstraps the cluster and core networking; Crossplane manages application-level cloud resources (databases, queues) that lifecycle with the application.
