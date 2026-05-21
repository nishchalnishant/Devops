# ArgoCD and GitOps — Cheatsheet

```
ArgoCD Cheatsheet Topics
├── argocd CLI
│   ├── Auth: login, logout, context switching
│   ├── App management: create, sync, diff, rollback, patch, delete
│   ├── App inspection: get, list, history, logs, events
│   ├── Repo management: add, list, remove (HTTP/SSH/TLS/GitHub App)
│   ├── Cluster management: add, list, rm (kubeconfig context-based)
│   ├── Project management: create, list, get, edit, delete
│   └── Admin commands: export, import, settings, cluster-sharding
│
├── ApplicationSet Generators (YAML patterns)
│   ├── cluster: one Application per registered ArgoCD cluster + label selector
│   ├── git (directories): one Application per matching directory glob
│   ├── matrix: cross-product of two generators (apps × clusters)
│   ├── pullRequest: one Application per open PR (ephemeral Review App)
│   └── merge: overlay multiple generators with merge key
│
├── Argo Rollouts
│   ├── Rollout CRD: replaces Deployment for progressive delivery
│   ├── Canary strategy: steps (setWeight, pause, analysis), traffic routing
│   ├── Blue-green strategy: active/preview services, autoPromotionEnabled
│   ├── AnalysisTemplate: Prometheus SLI queries with successCondition/failureLimit
│   └── kubectl argo rollouts: get, promote, pause, abort, undo, status, history
│
├── Sync Options Reference
│   ├── CreateNamespace=true — create destination namespace if missing
│   ├── ServerSideApply=true — use server-side apply (for large/CRD-heavy resources)
│   ├── ApplyOutOfSyncOnly=true — only apply changed resources (skip unchanged)
│   ├── PrunePropagationPolicy=foreground — wait for child resources before deleting
│   └── PruneLast=true — delete resources only after all other resources are healthy
│
├── Health & Sync Status
│   ├── Sync: Synced | OutOfSync | Unknown
│   └── Health: Healthy | Progressing | Degraded | Suspended | Missing | Unknown
│
├── Notification Annotations
│   ├── notifications.argoproj.io/subscribe.on-sync-failed.slack: channel-name
│   ├── notifications.argoproj.io/subscribe.on-health-degraded.pagerduty: service-id
│   └── Trigger + Template pattern in argocd-notifications-cm ConfigMap
│
├── ignoreDifferences Patterns
│   ├── jsonPointers: /spec/replicas (autoscaler-managed), /spec/clusterIP
│   ├── jqPathExpressions: sidecar injection annotations, Prometheus scrape annotations
│   └── CRD caBundle: injected by cert-manager webhook
│
└── Useful Combined Commands
    ├── argocd app diff + kubectl describe — compare desired vs live state
    ├── argocd app list --sync-status OutOfSync — find drifted apps
    ├── kubectl get applications -n argocd — raw CRD inspection
    └── argocd admin export > backup.yaml — full state backup
```

## First Principles

- A cheatsheet is reference-on-demand — commands are exact, copy-paste ready. Pattern sections show structure, not paragraphs.
- `argocd app sync` is the imperative escape hatch for GitOps. Use it for debugging; rely on automated sync for production.
- `ignoreDifferences` is the contract between ArgoCD and controllers that mutate resources post-apply (HPA modifies replicas, cert-manager injects caBundle, service mesh injects sidecars). Without it, ArgoCD will fight these controllers in an infinite sync loop.
- Argo Rollouts' AnalysisTemplate turns an SLI into a deployment gate. The Prometheus query is the acceptance criterion; `successCondition` and `failureLimit` define the threshold. This makes rollout criteria auditable in Git, not locked in a human's head.
- `PruneLast=true` is the safest prune mode: all new resources come up before anything is deleted. This prevents downtime when renaming a resource (old name deleted only after new name is healthy).

## argocd CLI Quick Reference

### Authentication

```bash
argocd login argocd.example.com                    # Interactive login
argocd login argocd.example.com --sso              # SSO login (opens browser)
argocd login argocd.example.com \
  --username admin \
  --password <password> \
  --insecure                                        # Skip TLS (dev only)
argocd logout argocd.example.com
argocd account get-user-info
argocd account update-password
argocd account list                                 # List all accounts
argocd account get --account my-ci-bot
```

### App Management

```bash
# Create application
argocd app create my-app \
  --repo https://github.com/org/repo \
  --path helm/my-app \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace production \
  --revision main \
  --sync-policy automated \
  --auto-prune \
  --self-heal

# Create with Helm values
argocd app create my-app \
  --repo https://github.com/org/repo \
  --path helm/my-app \
  --helm-values values-production.yaml \
  --helm-set image.tag=v2.3.0 \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace production

# Get app details and status
argocd app get my-app
argocd app get my-app --show-operation          # Show last sync operation details
argocd app list
argocd app list -p my-project                   # Filter by project
argocd app list --selector env=production       # Filter by label
argocd app list --sync-status OutOfSync         # Only out-of-sync apps
argocd app list --health-status Degraded        # Only degraded apps
argocd app list --output json | jq '.[].metadata.name'
argocd app list --output wide                   # Extra columns

# Sync
argocd app sync my-app                          # Trigger sync
argocd app sync my-app --async                  # Don't wait for completion
argocd app sync my-app --dry-run                # Preview only
argocd app sync my-app --force                  # Force apply
argocd app sync my-app --prune                  # Also delete removed resources
argocd app sync my-app --resource apps:Deployment:my-deploy  # Sync one resource
argocd app sync my-app --revision v2.3.0        # Sync specific git ref
argocd app sync my-app --replace                # Use kubectl replace (caution!)

# Diff
argocd app diff my-app                          # vs. live state
argocd app diff my-app --refresh                # Force re-fetch from Git first
argocd app diff my-app --local ./manifests      # Diff against local files
argocd app diff my-app --server-side-generate   # Use server-side generation

# Rollback
argocd app history my-app                       # Show deployment history
argocd app rollback my-app 5                    # Roll back to history ID 5

# Patch and update
argocd app set my-app --sync-policy automated
argocd app set my-app --revision v2.3.0
argocd app set my-app --helm-set image.tag=v2.3.0
argocd app patch my-app \
  --patch '{"spec":{"syncPolicy":{"automated":{"selfHeal":true}}}}'

# Disable automated sync (for emergency manual intervention)
argocd app patch my-app \
  --patch '{"spec":{"syncPolicy":null}}'

# Delete
argocd app delete my-app                        # Delete App CR only (keeps K8s resources)
argocd app delete my-app --cascade              # Also delete K8s resources

# Terminate ongoing sync operation
argocd app terminate-op my-app
```

### Logs, Events, and Debugging

```bash
argocd app logs my-app
argocd app logs my-app --container my-container
argocd app logs my-app --since-seconds 3600
argocd app events my-app                        # Kubernetes events for the app
argocd app resources my-app                     # List all managed resources
argocd app resources my-app --kind Deployment   # Filter by kind
argocd app wait my-app --health                 # Wait until healthy
argocd app wait my-app --sync                   # Wait until synced
argocd app wait my-app --timeout 300
```

### Repository Management

```bash
# HTTPS with token
argocd repo add https://github.com/org/repo \
  --username my-user \
  --password my-token

# SSH key
argocd repo add git@github.com:org/private-repo \
  --ssh-private-key-path ~/.ssh/id_rsa

# OCI Helm registry
argocd repo add oci://registry.example.com/charts \
  --type helm \
  --name my-registry

argocd repo list
argocd repo rm https://github.com/org/old-repo
argocd repo get https://github.com/org/repo
```

### Cluster Management

```bash
# Register clusters
argocd cluster add <kubectl-context-name>
argocd cluster add prod-eu-context \
  --name prod-eu \
  --label environment=production \
  --label region=eu-west-1

argocd cluster list
argocd cluster get prod-eu
argocd cluster rm https://prod-eu.k8s.example.com
argocd cluster rotate-auth https://prod-eu.k8s.example.com
```

### Project Management

```bash
argocd proj create my-project \
  --description "Payment team project" \
  --src https://github.com/org/payments \
  --dest https://kubernetes.default.svc,production \
  --allow-cluster-resource /namespaces

argocd proj list
argocd proj get my-project
argocd proj add-source my-project https://github.com/org/another-repo
argocd proj add-destination my-project https://kubernetes.default.svc staging
argocd proj allow-cluster-resource my-project "" ClusterRole
argocd proj deny-namespace-resource my-project "" ResourceQuota
argocd proj windows add my-project \
  --kind deny \
  --schedule "0 0 * * 5" \
  --duration 48h
argocd proj delete my-project
```

### Admin Commands

```bash
# Backup and restore
argocd admin export > argocd-backup.yaml
argocd admin import < argocd-backup.yaml

# Initial admin password
argocd admin initial-password -n argocd

# Notifications
argocd admin notifications template list
argocd admin notifications trigger list
argocd admin notifications template get app-deployed
argocd admin notifications trigger run on-sync-failed my-app

# Settings validation
argocd admin settings validate --argocd-cm-path ./argocd-cm.yaml

# App spec generation
argocd admin app generate-spec my-app

# Reset admin password
kubectl patch secret -n argocd argocd-secret \
  -p '{"stringData":{"admin.password":"'$(htpasswd -nbBC 10 "" newpassword | tr -d ':\n' | sed 's/$2y/$2a/')'"}}' 
```

***

## ApplicationSet YAML Templates

### Cluster Generator

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: nginx-ingress-fleet
  namespace: argocd
spec:
  generators:
    - cluster:
        selector:
          matchLabels:
            environment: production
        values:
          replicaCount: "3"
  template:
    metadata:
      name: "nginx-ingress-{{name}}"
    spec:
      project: platform
      source:
        repoURL: https://github.com/org/platform-config
        targetRevision: HEAD
        path: "apps/nginx-ingress/overlays/{{metadata.labels.region}}"
        helm:
          parameters:
            - name: replicaCount
              value: "{{values.replicaCount}}"
      destination:
        server: "{{server}}"
        namespace: ingress-nginx
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
        syncOptions:
          - CreateNamespace=true
          - ServerSideApply=true
```

### Git Directory Generator

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: services-monorepo
  namespace: argocd
spec:
  generators:
    - git:
        repoURL: https://github.com/org/services
        revision: HEAD
        directories:
          - path: "services/*"
          - path: "services/legacy-*"
            exclude: true             # Exclude legacy services
  template:
    metadata:
      name: "{{path.basename}}"
    spec:
      project: services
      source:
        repoURL: https://github.com/org/services
        path: "{{path}}"
        targetRevision: HEAD
      destination:
        server: https://kubernetes.default.svc
        namespace: "{{path.basename}}"
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
        syncOptions:
          - CreateNamespace=true
```

### Matrix Generator (apps × environments)

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: microservices-all-envs
  namespace: argocd
spec:
  generators:
    - matrix:
        generators:
          - git:
              repoURL: https://github.com/org/services
              revision: HEAD
              directories:
                - path: "services/*"
          - cluster:
              selector:
                matchExpressions:
                  - key: environment
                    operator: In
                    values: [staging, production]
  template:
    metadata:
      name: "{{path.basename}}-{{metadata.labels.environment}}"
    spec:
      source:
        repoURL: https://github.com/org/services
        path: "{{path}}/overlays/{{metadata.labels.environment}}"
        targetRevision: HEAD
      destination:
        server: "{{server}}"
        namespace: "{{path.basename}}"
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
```

### Pull Request Generator (preview environments)

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: preview-environments
  namespace: argocd
spec:
  generators:
    - pullRequest:
        github:
          owner: org
          repo: app-repo
          tokenRef:
            secretName: github-token
            key: token
          labels:
            - preview
        requeueAfterSeconds: 30
  template:
    metadata:
      name: "preview-{{number}}"
    spec:
      project: previews
      source:
        repoURL: https://github.com/org/app-repo
        targetRevision: "{{head_sha}}"
        path: helm/app
        helm:
          values: |
            image.tag: "pr-{{number}}"
            ingress.host: "pr-{{number}}.preview.example.com"
            resources.requests.cpu: "100m"
            resources.requests.memory: "128Mi"
      destination:
        server: https://staging.k8s.example.com
        namespace: "preview-{{number}}"
      syncPolicy:
        automated:
          prune: true
        syncOptions:
          - CreateNamespace=true
```

### Merge Generator (per-cluster overrides)

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: platform-stack
  namespace: argocd
spec:
  generators:
    - merge:
        mergeKeys:
          - server
        generators:
          - cluster:
              selector:
                matchLabels:
                  environment: production
              values:
                replicaCount: "3"
                logLevel: "info"
          - list:
              elements:
                - server: https://prod-us-heavy.k8s.example.com
                  values.replicaCount: "10"
                  values.logLevel: "warn"
  template:
    metadata:
      name: "platform-{{name}}"
    spec:
      source:
        repoURL: https://github.com/org/platform
        path: helm/platform
        targetRevision: HEAD
        helm:
          parameters:
            - name: replicaCount
              value: "{{values.replicaCount}}"
            - name: logLevel
              value: "{{values.logLevel}}"
      destination:
        server: "{{server}}"
        namespace: platform
```

***

## Argo Rollouts YAML Patterns

### Canary with Nginx Traffic Split

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: my-service
  namespace: production
spec:
  replicas: 20
  selector:
    matchLabels:
      app: my-service
  template:
    metadata:
      labels:
        app: my-service
    spec:
      containers:
        - name: app
          image: my-service:v2.0.0
          ports:
            - containerPort: 8080
  strategy:
    canary:
      canaryService: my-service-canary
      stableService: my-service-stable
      trafficRouting:
        nginx:
          stableIngress: my-service-ingress
      steps:
        - setWeight: 5
        - pause: {duration: 2m}
        - analysis:
            templates:
              - templateName: http-success-rate
            args:
              - name: service-name
                value: my-service-canary
        - setWeight: 25
        - pause: {duration: 5m}
        - analysis:
            templates:
              - templateName: http-success-rate
        - setWeight: 50
        - pause: {duration: 5m}
        - setWeight: 100
      maxSurge: "25%"
      maxUnavailable: 0
      abortScaleDownDelaySeconds: 30
```

### Blue-Green with Pre-Promotion Analysis

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: my-service
spec:
  replicas: 5
  strategy:
    blueGreen:
      activeService: my-service-active
      previewService: my-service-preview
      autoPromotionEnabled: false
      prePromotionAnalysis:
        templates:
          - templateName: http-success-rate
        args:
          - name: service-name
            value: my-service-preview
      postPromotionAnalysis:
        templates:
          - templateName: http-success-rate
        args:
          - name: service-name
            value: my-service-active
      scaleDownDelaySeconds: 600
      previewReplicaCount: 2
```

### AnalysisTemplate with Prometheus

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: http-success-rate
spec:
  args:
    - name: service-name
  metrics:
    - name: success-rate
      interval: 1m
      count: 5
      successCondition: result[0] >= 0.99
      failureLimit: 2
      inconclusiveLimit: 1
      provider:
        prometheus:
          address: http://prometheus.monitoring:9090
          query: |
            sum(rate(http_requests_total{
              service="{{args.service-name}}",
              status!~"5.."}[5m]))
            /
            sum(rate(http_requests_total{
              service="{{args.service-name}}"}[5m]))
    - name: latency-p99
      interval: 1m
      count: 5
      successCondition: result[0] <= 0.3
      provider:
        prometheus:
          address: http://prometheus.monitoring:9090
          query: |
            histogram_quantile(0.99,
              sum(rate(http_request_duration_seconds_bucket{
                service="{{args.service-name}}"}[5m])) by (le))
```

### kubectl argo rollouts Commands

```bash
# Status
kubectl argo rollouts version
kubectl argo rollouts get rollout my-service -n production --watch
kubectl argo rollouts list rollouts -n production

# Promotion and control
kubectl argo rollouts promote my-service -n production           # Advance one step
kubectl argo rollouts promote my-service -n production --full    # Skip all steps
kubectl argo rollouts abort my-service -n production             # Abort and rollback
kubectl argo rollouts retry rollout my-service -n production     # Retry after abort
kubectl argo rollouts pause my-service -n production             # Pause at current step
kubectl argo rollouts resume my-service -n production

# Image update (triggers new rollout)
kubectl argo rollouts set image my-service app=my-service:v2.1.0 -n production

# History
kubectl argo rollouts history rollout my-service -n production
kubectl argo rollouts undo my-service -n production              # Roll back one revision
```

***

## Sync Options Reference

```yaml
syncOptions:
  - CreateNamespace=true               # Create destination namespace if missing
  - ServerSideApply=true               # Use SSA instead of client-side apply
  - ApplyOutOfSyncOnly=true            # Skip already-synced resources (faster)
  - PrunePropagationPolicy=foreground  # Wait for owned resources to delete first
  - PruneLast=true                     # Delete old resources after new ones healthy
  - RespectIgnoreDifferences=true      # Apply ignoreDifferences rules during sync
  - Validate=false                     # Skip kubectl schema validation (use sparingly)
  - Replace=true                       # Use kubectl replace instead of apply
  - Force=true                         # Force apply (overwrites field manager conflicts)
```

## App Health Status Meanings

| Status | Meaning |
|---|---|
| `Healthy` | All managed resources are healthy |
| `Progressing` | Resources are being updated (Deployment rolling, Job running) |
| `Degraded` | A resource is in a failed or error state |
| `Suspended` | Rollout or Deployment is suspended/paused |
| `Missing` | Resource is defined but does not exist in the cluster |
| `Unknown` | ArgoCD cannot determine health (no health check defined) |

## Sync Status Meanings

| Status | Meaning |
|---|---|
| `Synced` | Live state matches desired state in Git |
| `OutOfSync` | Live state differs from Git state |
| `Unknown` | Cannot determine sync status (cluster unreachable, etc.) |

***

## Notification Annotations

```yaml
metadata:
  annotations:
    notifications.argoproj.io/subscribe.on-sync-succeeded.slack: deployments
    notifications.argoproj.io/subscribe.on-sync-failed.pagerduty: ops-team
    notifications.argoproj.io/subscribe.on-health-degraded.slack: alerts
    notifications.argoproj.io/subscribe.on-deployed.teams: releases
    notifications.argoproj.io/subscribe.on-sync-running.slack: deployments
```

***

## Useful kubectl + argocd Combos

```bash
# Find all ArgoCD-managed apps that are OutOfSync
argocd app list --output json | \
  jq -r '.[] | select(.status.sync.status == "OutOfSync") | .metadata.name'

# Sync all OutOfSync apps in a project
argocd app list -p platform --output name | \
  xargs -P5 -I{} argocd app sync {} --async

# Check which clusters are failing
argocd cluster list --output json | \
  jq -r '.[] | select(.connectionState.status != "Successful") | 
  "\(.name) \(.connectionState.status) \(.connectionState.message)"'

# Force self-heal for all apps in a namespace
kubectl get applications -n argocd -o name | xargs -I{} \
  kubectl patch {} -n argocd \
  --type=merge -p '{"spec":{"syncPolicy":{"automated":{"selfHeal":true}}}}'

# List all resources managed by an app
argocd app resources my-app --output json | \
  jq -r '.[] | "\(.kind)/\(.name)"'

# Check which application manages a specific resource
kubectl get deploy my-deploy -n production -o yaml | \
  grep "argocd.argoproj.io/app-name"

# Get detailed diff with server-side generation
argocd app diff my-app --server-side-generate

# Watch all apps for health changes
watch -n5 'argocd app list --output wide | grep -v Healthy'

# Export all applications as YAML
argocd app list --output name | xargs -I{} \
  argocd app get {} --output yaml

# Check ArgoCD component health
kubectl get pods -n argocd
kubectl top pods -n argocd
kubectl logs -n argocd deploy/argocd-application-controller --tail=50 | grep -i error
```

***

## ignoreDifferences Patterns

```yaml
spec:
  ignoreDifferences:
    # Ignore HPA-managed replica count
    - group: apps
      kind: Deployment
      jsonPointers:
        - /spec/replicas

    # Ignore service mesh injected annotations
    - group: apps
      kind: Deployment
      jqPathExpressions:
        - '.metadata.annotations["sidecar.istio.io/inject"]'
        - '.spec.template.metadata.annotations["prometheus.io/scrape"]'

    # Ignore cloud-assigned values on Services
    - group: ""
      kind: Service
      jsonPointers:
        - /spec/clusterIP
        - /spec/clusterIPs

    # Ignore CRD fields added by controllers
    - group: apiextensions.k8s.io
      kind: CustomResourceDefinition
      jsonPointers:
        - /spec/conversion/webhook/clientConfig/caBundle

    # Ignore last-applied-configuration annotation (client-side apply artifact)
    - group: apps
      kind: Deployment
      jsonPointers:
        - /metadata/annotations/kubectl.kubernetes.io~1last-applied-configuration
```

***

## System Design Perspective

**ignoreDifferences as a controller contract**

Every Kubernetes controller that modifies a resource post-apply creates a potential sync loop with ArgoCD. Common patterns: HPA modifies `spec.replicas` (ArgoCD wants 3, HPA sets 5 → OutOfSync → sync resets to 3 → HPA scales back to 5 → repeat). The fix is `ignoreDifferences: jsonPointers: [/spec/replicas]`. Similarly, cert-manager injects `caBundle` into webhook configurations; service mesh controllers inject sidecar annotations. Audit all controllers running in your cluster and add `ignoreDifferences` entries for every field they mutate.

**ApplicationSet template design**

The ApplicationSet template section uses Go templating with `{{.metadata.name}}` and `{{.values.*}}` placeholders. Generator outputs become template variables. Design principle: put cluster-specific values (namespace, resource limits, replica counts) in the generator (cluster labels or Git-based config files), not in the template. The template should be generic; the generator provides the parametrization. This allows a single ApplicationSet to correctly configure 50 clusters with different resource profiles.

**Sync strategy selection**

Automated sync with `selfHeal: true` is the default for production GitOps. `selfHeal` detects drift and corrects within the reconciliation interval (default 3 minutes). Without `selfHeal`, direct `kubectl` changes persist until the next manual sync. `prune: true` deletes resources removed from Git — required for full GitOps but dangerous if mis-scoped. Safe rollout: enable automated sync first, operate for a week to build confidence, then enable `prune: true`, then `selfHeal: true`.

**CLI patterns for fleet operations**

For 200-cluster fleets: `argocd app list --sync-status OutOfSync -o json | jq '[.[] | {name: .metadata.name, cluster: .spec.destination.server}]'` identifies drifted apps across all clusters. Pipe to a script that pages on-call for production-tier clusters (matched by cluster label). `argocd admin export` + S3 upload in a CronJob provides daily backup of all Application/AppProject state. The import path (`argocd admin import < backup.yaml`) restores the control plane without needing to re-register clusters from scratch.
