# Progressive Delivery & GitOps at Scale

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
