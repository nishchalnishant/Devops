# ArgoCD and GitOps — Deep Theory Notes

## 1. GitOps Principles

GitOps is an operational model that uses Git as the single source of truth for all desired state — both applications and infrastructure. Four immutable properties define a GitOps system:

| Principle | Definition | Practical Implication |
|---|---|---|
| **Declarative** | Desired state expressed as files, not imperative scripts | Manifests, Helm values, Kustomize overlays — never `kubectl run` |
| **Versioned and immutable** | Every state transition is a Git commit (author, timestamp, diff) | Git history is the audit log; rollback is `git revert` |
| **Pulled automatically** | Operator inside the cluster polls Git; pipelines never push credentials | Attack surface shrinks: CI server has no cluster access |
| **Continuously reconciled** | Drift between live and desired state is detected and corrected on a configured interval | Self-healing is automatic, not on-demand |

### Push-Based vs. Pull-Based CI/CD

```
Push-Based (Traditional)                Pull-Based (GitOps)
────────────────────────                ──────────────────
CI pipeline holds kubeconfig            Operator holds Git token
Pipeline pushes: kubectl apply          Operator pulls and applies
Audit: pipeline logs                    Audit: Git history
Rollback: re-run old pipeline           Rollback: git revert
Drift detection: none                   Drift detection: automatic
Attack surface: CI server               Attack surface: cluster operator
```

> [!IMPORTANT]
> The GitOps security model is fundamentally different from push-based CI/CD. In GitOps, the cluster reaches out to Git — not the other way around. This means a compromised CI pipeline cannot push arbitrary workloads to production clusters.

---

## 2. ArgoCD Architecture

ArgoCD is deployed inside the Kubernetes cluster and consists of five core components that work together to implement the GitOps reconciliation loop.

### API Server (`argocd-server`)

- Exposes gRPC and REST APIs consumed by the CLI, UI, and external CI/CD integrations
- Enforces RBAC on all application operations (sync, delete, rollback, override)
- Handles SSO/OIDC token validation via Dex or an external identity provider
- Receives and validates webhook events from GitHub, GitLab, and Bitbucket
- Manages the AppProject enforcement: checks sources, destinations, and resource whitelists

### Repository Server (`argocd-repo-server`)

- Clones Git repositories (or fetches from OCI registries for Helm)
- Generates Kubernetes manifests from the source: Helm template, Kustomize build, Jsonnet, plain YAML, or custom Config Management Plugins (CMP)
- Caches rendered manifests in Redis; a cache miss triggers fresh clone + render
- Runs in a sandboxed process for CMP isolation — critical for multi-tenant security
- Responsible for the "desired state" half of the diff

### Application Controller (`argocd-application-controller`)

- Implements the core GitOps reconciliation loop (watches `Application` CRs)
- Compares desired state (from repo server) against live state (Kubernetes API)
- Computes sync status (`Synced` / `OutOfSync`) and health status (`Healthy` / `Degraded` / `Progressing` / `Suspended` / `Missing`)
- Executes sync operations: resource ordering by sync wave, running pre/post hooks
- Respects sync policies (`automated`, `prune`, `selfHeal`)
- Can be sharded across multiple replicas for large fleets (via `ARGOCD_CONTROLLER_REPLICAS`)

### Redis

- Caches rendered manifests from the repo server (cache key = repo URL + revision + path)
- Stores application state for fast UI reads
- Not a persistence layer — all canonical state lives in etcd (Kubernetes secrets/CRDs)

### Dex (optional, `argocd-dex-server`)

- Embedded OIDC provider that federates to external identity providers
- Supports: GitHub OAuth, GitLab, LDAP/AD, SAML 2.0, external OIDC providers
- Can be bypassed by configuring `oidc.config` in `argocd-cm` to point directly at an external IdP (e.g., Azure AD, Okta)

### ApplicationSet Controller (`argocd-applicationset-controller`)

- Separate controller managing `ApplicationSet` CRDs
- Generates ArgoCD `Application` CRs from template + generator combinations
- Enables fleet management: one ApplicationSet → N Applications across N clusters/environments

---

## 3. Application CRD — Key Fields

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: payment-service
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io   # Enables cascade delete
  annotations:
    notifications.argoproj.io/subscribe.on-sync-failed.slack: alerts
spec:
  project: payments-team                         # AppProject for RBAC

  source:
    repoURL: https://github.com/org/payments
    targetRevision: HEAD                         # Branch, tag, or commit SHA
    path: helm/payment-service
    helm:
      releaseName: payment-service
      valueFiles:
        - values-production.yaml
      parameters:
        - name: image.tag
          value: v2.3.1

  destination:
    server: https://kubernetes.default.svc       # In-cluster
    # server: https://prod-eu.k8s.example.com    # Remote cluster
    namespace: production

  syncPolicy:
    automated:
      prune: true                                # Delete resources removed from Git
      selfHeal: true                             # Revert manual cluster changes
      allowEmpty: false                          # Fail if source renders empty
    syncOptions:
      - CreateNamespace=true
      - ServerSideApply=true
      - ApplyOutOfSyncOnly=true
      - PrunePropagationPolicy=foreground
      - PruneLast=true
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m

  ignoreDifferences:
    - group: apps
      kind: Deployment
      jsonPointers:
        - /spec/replicas                         # Ignore HPA-managed replica count
    - group: ""
      kind: Service
      jsonPointers:
        - /spec/clusterIP
        - /spec/clusterIPs

  revisionHistoryLimit: 10
```

---

## 4. Sync Waves and Hooks

### Sync Waves

Sync waves control the **order of resource application** within a single sync operation. Resources are applied in ascending wave order. ArgoCD waits for all resources in wave N to become healthy before applying wave N+1.

```yaml
metadata:
  annotations:
    argocd.argoproj.io/sync-wave: "-1"   # Negative waves run first
```

**Recommended wave ordering:**

| Wave | Resource Types |
|---|---|
| `-2` | CRDs (must be established before CRs can be created) |
| `-1` | Namespaces, ClusterRoles, ClusterRoleBindings |
| `0` | ConfigMaps, Secrets, ServiceAccounts, RoleBindings |
| `1` | PersistentVolumeClaims, Services |
| `2` | Deployments, StatefulSets, DaemonSets |
| `3` | Ingress, HorizontalPodAutoscaler, PodDisruptionBudgets |
| `5` | PostSync validation Jobs |

> [!TIP]
> ArgoCD waits for a resource to be "healthy" before moving to the next wave. For Deployments, this means all replicas are available. For CRDs, it means the CRD status condition `Established=True`. Define custom health checks for your CRDs.

### Resource Hooks

Hooks execute Jobs or Pods at specific lifecycle phases:

```yaml
metadata:
  annotations:
    argocd.argoproj.io/hook: PreSync          # Before any resource is applied
    # argocd.argoproj.io/hook: Sync           # During sync (same lifecycle as wave 0)
    # argocd.argoproj.io/hook: PostSync       # After all resources are healthy
    # argocd.argoproj.io/hook: SyncFail       # Only if sync fails
    # argocd.argoproj.io/hook: Skip           # Exclude from sync entirely
    argocd.argoproj.io/hook-delete-policy: HookSucceeded   # Clean up on success
    # HookFailed    — clean up on failure
    # BeforeHookCreation — delete any previous hook run before creating new one
```

**Common patterns:**

```yaml
# Database migration hook — runs before app is updated
apiVersion: batch/v1
kind: Job
metadata:
  name: db-migrate
  annotations:
    argocd.argoproj.io/hook: PreSync
    argocd.argoproj.io/hook-delete-policy: HookSucceeded
spec:
  template:
    spec:
      containers:
        - name: migrate
          image: my-app:v2.3.1
          command: ["python", "manage.py", "migrate"]
      restartPolicy: OnFailure
```

---

## 5. App of Apps Pattern

The App of Apps pattern bootstraps an ArgoCD installation by having one root `Application` point to a directory of other `Application` manifests. ArgoCD manages the child Applications as Kubernetes resources.

```
gitops-repo/
├── bootstrap/
│   └── root-app.yaml          # The one Application applied manually
└── apps/
    ├── monitoring.yaml        # Application for monitoring stack
    ├── ingress-nginx.yaml     # Application for ingress
    ├── cert-manager.yaml      # Application for cert-manager
    └── payment-service.yaml   # Application for the payment service
```

```yaml
# bootstrap/root-app.yaml — apply once to bootstrap the cluster
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: root-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/org/gitops-repo
    targetRevision: HEAD
    path: apps/
  destination:
    server: https://kubernetes.default.svc
    namespace: argocd
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

> [!IMPORTANT]
> Use `prune: false` for the root app itself in initial bootstrapping, or set `prune: true` carefully — if the `apps/` directory is accidentally emptied, prune would delete all child Applications.

**Delete ordering problem:** When deleting an App of Apps, ArgoCD may try to delete child Applications before their managed resources are cleaned up. Use finalizers:

```yaml
metadata:
  finalizers:
    - resources-finalizer.argocd.argoproj.io  # Cascade delete: removes K8s resources before deleting the Application CR
```

---

## 6. ApplicationSet Controller

ApplicationSets replace manually defining N `Application` objects by generating them from a template and generator.

### Generator Types

| Generator | Use Case | Template Variables Available |
|---|---|---|
| `list` | Static set of hardcoded values | Any key in element |
| `cluster` | Every registered ArgoCD cluster | `name`, `server`, `metadata.labels.*`, `metadata.annotations.*` |
| `git` (directories) | One app per directory in a repo | `path`, `path.basename`, `path.basenameNormalized` |
| `git` (files) | One app per JSON/YAML config file | All keys in the JSON/YAML file |
| `matrix` | Cross-product of two generators | All variables from both generators |
| `merge` | Override defaults per-cluster via a merge key | All variables from base + overrides |
| `pullRequest` | One app per open PR (GitHub/GitLab/Bitbucket) | `number`, `branch`, `head_sha` |
| `scmProvider` | One app per repo in a GitHub/GitLab org | `organization`, `repository`, `url`, `branch`, `sha` |

### Cluster Generator

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: platform-monitoring
  namespace: argocd
spec:
  generators:
    - cluster:
        selector:
          matchLabels:
            environment: production
        values:
          alertmanager_url: "https://alertmanager.monitoring:9093"
  template:
    metadata:
      name: "monitoring-{{name}}"
    spec:
      project: platform
      source:
        repoURL: https://github.com/org/platform
        targetRevision: HEAD
        path: "charts/monitoring/overlays/{{metadata.labels.region}}"
      destination:
        server: "{{server}}"
        namespace: monitoring
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
        syncOptions:
          - CreateNamespace=true
          - ServerSideApply=true
```

### Matrix Generator (cross-product)

```yaml
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
# Template: name = "{{path.basename}}-{{metadata.labels.environment}}"
# Produces: payment-staging, payment-production, auth-staging, auth-production, etc.
```

### Pull Request Generator (ephemeral preview environments)

```yaml
generators:
  - pullRequest:
      github:
        owner: org
        repo: app-repo
        tokenRef:
          secretName: github-token
          key: token
        labels:
          - preview          # Only PRs labeled "preview"
      requeueAfterSeconds: 30  # Poll interval for new/closed PRs
```

> [!CAUTION]
> The pull request generator creates real Kubernetes namespaces and resources for each PR. Implement resource quotas on the preview namespace and set TTL/prune policies to prevent namespace sprawl when PRs are merged or closed.

---

## 7. Project RBAC (AppProject)

AppProjects enforce multi-tenancy in ArgoCD. They restrict which Git sources, cluster destinations, and Kubernetes resource types an Application is allowed to use.

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: payments-team
  namespace: argocd
spec:
  description: "Payment team project"

  # Allowed Git sources
  sourceRepos:
    - https://github.com/org/payments
    - https://github.com/org/shared-charts

  # Allowed destinations (cluster + namespace)
  destinations:
    - server: https://kubernetes.default.svc
      namespace: production
    - server: https://kubernetes.default.svc
      namespace: staging

  # Cluster-scoped resources the project is allowed to create
  clusterResourceWhitelist:
    - group: ""
      kind: Namespace          # Allow creating namespaces

  # Namespace-scoped resources the project is NOT allowed to create
  namespaceResourceBlacklist:
    - group: ""
      kind: ResourceQuota      # Cannot modify quota (platform team responsibility)
    - group: networking.k8s.io
      kind: NetworkPolicy

  # Source namespace restrictions (Kubernetes RBAC)
  sourceNamespaces:
    - argocd

  # Sync windows — restrict automated sync to certain hours
  syncWindows:
    - kind: allow
      schedule: "0 9 * * 1-5"   # Weekdays 9am UTC
      duration: 8h
      applications:
        - "*"
      namespaces:
        - production
    - kind: deny
      schedule: "0 0 * * 5"     # Friday midnight UTC
      duration: 48h              # No production deploys over weekend
      applications:
        - "*"
```

### ArgoCD RBAC Policy

ArgoCD's own RBAC is configured in `argocd-rbac-cm`:

```yaml
# argocd-rbac-cm ConfigMap
data:
  policy.default: role:readonly
  policy.csv: |
    # Developer role: can sync and read, cannot delete
    p, role:developer, applications, sync, */*, allow
    p, role:developer, applications, get, */*, allow
    p, role:developer, logs, get, */*, allow

    # SRE role: full access to all apps
    p, role:sre, applications, *, */*, allow
    p, role:sre, clusters, get, *, allow
    p, role:sre, repositories, *, *, allow

    # Bind roles to SSO groups
    g, org:engineering, role:developer
    g, org:sre-team, role:sre
    g, admin@example.com, role:admin
```

---

## 8. ArgoCD Notifications

ArgoCD Notifications sends alerts to Slack, PagerDuty, email, Teams, and more based on Application events.

```yaml
# Trigger on Application annotation
metadata:
  annotations:
    notifications.argoproj.io/subscribe.on-sync-succeeded.slack: deployments
    notifications.argoproj.io/subscribe.on-sync-failed.pagerduty: ops-team
    notifications.argoproj.io/subscribe.on-health-degraded.slack: alerts
    notifications.argoproj.io/subscribe.on-deployed.teams: releases-channel
```

```yaml
# argocd-notifications-cm — custom template
data:
  template.app-deployed: |
    slack:
      attachments: |
        [{
          "title": "{{ .app.metadata.name }}",
          "title_link": "{{.context.argocdUrl}}/applications/{{.app.metadata.name}}",
          "color": "#18be52",
          "fields": [{
            "title": "Sync Status",
            "value": "{{.app.status.sync.status}}",
            "short": true
          }, {
            "title": "Repository",
            "value": "{{.app.spec.source.repoURL}}",
            "short": true
          }, {
            "title": "Revision",
            "value": "{{.app.status.sync.revision}}",
            "short": true
          }]
        }]
```

---

## 9. ArgoCD Image Updater

ArgoCD Image Updater watches container registries and automatically updates image tags in Git (write-back) or directly patches the Application in ArgoCD.

```yaml
# Annotations on the ArgoCD Application
metadata:
  annotations:
    argocd-image-updater.argoproj.io/image-list: myapp=registry.example.com/my-app
    argocd-image-updater.argoproj.io/myapp.update-strategy: semver
    argocd-image-updater.argoproj.io/myapp.allow-tags: regexp:^v[0-9]+\.[0-9]+\.[0-9]+$
    argocd-image-updater.argoproj.io/write-back-method: git
    argocd-image-updater.argoproj.io/git-branch: main
    argocd-image-updater.argoproj.io/write-back-target: kustomization
```

**Write-back strategies:**
- `git` — commits updated image tag back to the Git repository (full GitOps)
- `argocd` — patches the Application CR directly (state not in Git)

---

## 10. Argo Rollouts — Progressive Delivery

Argo Rollouts extends Kubernetes Deployments with automated canary and blue-green strategies, metric-based promotion/rollback, and traffic management integration.

### Canary Strategy — How It Works

1. A new Rollout revision is created when the image tag changes
2. ArgoCD creates a "canary" ReplicaSet alongside the "stable" ReplicaSet
3. The traffic routing rule (Nginx Ingress / Istio VirtualService / AWS ALB) routes `weight%` to canary, rest to stable
4. At each step: ArgoCD either pauses for a duration, runs an AnalysisRun, or advances weight
5. AnalysisRun queries Prometheus (or Datadog/New Relic/CloudWatch) — if metric condition fails, rollout aborts and traffic returns 100% to stable
6. On promotion: stable ReplicaSet is replaced by canary ReplicaSet; old replicas scaled down

### AnalysisTemplate — Metric Gates

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: composite-health-check
spec:
  args:
    - name: service-name
    - name: namespace
  metrics:
    - name: success-rate
      interval: 1m
      count: 5
      successCondition: result[0] >= 0.99
      failureLimit: 2
      inconclusiveLimit: 1      # Treat missing data as inconclusive, not success
      provider:
        prometheus:
          address: http://prometheus.monitoring:9090
          query: |
            sum(rate(http_requests_total{
              service="{{args.service-name}}",
              namespace="{{args.namespace}}",
              status!~"5.."}[5m]))
            /
            sum(rate(http_requests_total{
              service="{{args.service-name}}",
              namespace="{{args.namespace}}"}[5m]))

    - name: p99-latency-ms
      interval: 1m
      count: 5
      successCondition: result[0] <= 300
      failureLimit: 1
      provider:
        prometheus:
          address: http://prometheus.monitoring:9090
          query: |
            histogram_quantile(0.99,
              sum(rate(http_request_duration_seconds_bucket{
                service="{{args.service-name}}"}[5m])) by (le)) * 1000
```

### Blue-Green Strategy

```yaml
strategy:
  blueGreen:
    activeService: payment-active          # Traffic goes here
    previewService: payment-preview        # New version deployed here first
    autoPromotionEnabled: false            # Require manual `kubectl argo rollouts promote`
    autoPromotionSeconds: 300              # Auto-promote after 5m if not manually promoted
    prePromotionAnalysis:
      templates:
        - templateName: composite-health-check
      args:
        - name: service-name
          value: payment-preview
    postPromotionAnalysis:
      templates:
        - templateName: composite-health-check
      args:
        - name: service-name
          value: payment-active
    scaleDownDelaySeconds: 600             # Keep old version for 10m post-promotion
    previewReplicaCount: 2                 # Reduced replicas for preview (cost control)
    abortScaleDownDelaySeconds: 30
```

---

## 11. Multi-Cluster Management

### Hub-and-Spoke Architecture

One ArgoCD control plane on a management cluster manages N spoke clusters via registered kubeconfig secrets. The hub cluster runs ArgoCD; spoke clusters run only the workloads.

```
Management Cluster
├── argocd (namespace)
│   ├── argocd-application-controller
│   ├── argocd-repo-server
│   ├── argocd-server
│   └── cluster secrets (one per spoke cluster)
│
└── ApplicationSets → generate Applications → target spoke clusters

Spoke Clusters (prod-eu, prod-us, prod-ap, staging)
└── Workloads only — no ArgoCD components
    (ArgoCD connects to spoke cluster API via the cluster secret)
```

**Registration:**

```bash
# Adds an argocd ServiceAccount to the spoke cluster with RBAC
# Creates a cluster secret in the argocd namespace
argocd cluster add prod-eu-context \
  --name prod-eu \
  --label environment=production \
  --label region=eu-west-1 \
  --label tier=critical
```

### Sharding for Scale

When managing 100+ clusters, a single application-controller replica becomes a bottleneck. Enable sharding:

```yaml
# argocd-application-controller StatefulSet env
- name: ARGOCD_CONTROLLER_REPLICAS
  value: "3"               # 3 replicas, clusters distributed across them
```

ArgoCD v2.8+ introduces dynamic sharding — clusters are automatically redistributed when a controller replica fails.

---

## 12. Disaster Recovery

### Backup Strategy

```bash
# Export all ArgoCD config (Applications, Projects, repositories, cluster secrets)
argocd admin export > argocd-backup-$(date +%Y%m%d).yaml

# Automated backup — run as a CronJob or scheduled pipeline
argocd admin export | \
  aws s3 cp - s3://my-argocd-backup/argocd-$(date +%Y%m%d-%H%M).yaml

# Restore
argocd admin import < argocd-backup.yaml
```

### Recovery Procedure

1. **RTO (Recovery Time Objective):** For ArgoCD itself, reinstall via Helm and run `argocd admin import`. Apps reconnect to clusters using cluster secrets from backup.

2. **RPO (Recovery Point Objective):** The Git repository IS the source of truth. If ArgoCD's state is lost but Git is intact, re-bootstrapping with the root Application regenerates all Applications automatically.

3. **Bootstrap from Git only:**
   ```bash
   # Fresh install
   helm install argocd argo/argo-cd -n argocd --create-namespace
   # Apply the root application
   kubectl apply -f bootstrap/root-app.yaml -n argocd
   # ArgoCD self-syncs: all Applications are regenerated from Git
   ```

> [!TIP]
> The real disaster recovery asset is not ArgoCD's internal state — it's the Git repository. Ensure your GitOps repository has branch protections, multiple contributors with push access, and offsite backups if using self-hosted Git.

---

## 13. Secret Management Patterns

### External Secrets Operator (Recommended)

```yaml
# SecretStore — defines connection to secret backend (safe to commit)
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: aws-secrets-manager
  namespace: production
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-east-1
      auth:
        jwt:
          serviceAccountRef:
            name: external-secrets-sa   # IRSA for AWS auth

---
# ExternalSecret — declares which secrets to fetch (safe to commit)
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: db-credentials
  namespace: production
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore
  target:
    name: db-credentials             # Name of the resulting K8s Secret
    creationPolicy: Owner
    deletionPolicy: Retain
  data:
    - secretKey: password
      remoteRef:
        key: prod/db/credentials
        property: password
    - secretKey: username
      remoteRef:
        key: prod/db/credentials
        property: username
```

### SOPS + ArgoCD CMP Plugin

SOPS encrypts secret values in YAML files using age/PGP/AWS KMS. ArgoCD's Config Management Plugin (CMP) decrypts during manifest generation.

```yaml
# .sops.yaml in the repository
creation_rules:
  - path_regex: .*secrets.*\.yaml$
    kms: arn:aws:kms:us-east-1:123456789012:key/my-key-id
    age: age1...
```

### Sealed Secrets

```bash
# Encrypt a secret with the cluster's public key
kubectl create secret generic db-creds \
  --from-literal=password=secret123 \
  --dry-run=client -o yaml | \
  kubeseal --format yaml > sealed-db-creds.yaml
# sealed-db-creds.yaml is safe to commit to Git
```

---

## 14. High Availability ArgoCD Setup

```yaml
# argocd-cm — HA configuration
data:
  # Enable Redis Sentinel for HA Redis
  redis.server: "argocd-redis-ha-haproxy:6379"
  # Application controller sharding
  controller.sharding.algorithm: "consistent-hashing"

# Deploy with HA Helm values
# values-ha.yaml
redis-ha:
  enabled: true
  haproxy:
    enabled: true
    replicas: 3

server:
  replicas: 2
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 5

repoServer:
  replicas: 2
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 4

applicationSet:
  replicas: 2
```

> [!IMPORTANT]
> For production ArgoCD, always run with at least 2 replicas of the API server and repo server. The application-controller is stateful and requires sharding rather than simple replication for scaling.

---

## 15. Resource Tracking: Annotation vs. Label

ArgoCD tracks managed resources to detect drift. Two tracking methods:

| Method | Mechanism | Pros | Cons |
|---|---|---|---|
| **Label** (default) | `app.kubernetes.io/instance: <app-name>` label on all managed resources | Visible, queryable with `kubectl` | Modifies resource metadata; conflicts if resource managed by multiple systems |
| **Annotation** | `argocd.argoproj.io/tracking-id: <app-name>:<group>/<kind>:<namespace>/<name>` | No label conflicts | Less visible in `kubectl get` output |

Configure in `argocd-cm`:
```yaml
data:
  application.resourceTrackingMethod: annotation  # or "label" or "annotation+label"
```

Use `annotation` tracking in environments where label selectors are sensitive (e.g., resources with label-based HPA or PodDisruptionBudgets).
# GitOps at Scale & FinOps Engineering

> [!IMPORTANT]
> This file covers two Staff-level domains that are tested together in principal-level interviews: **GitOps fleet management** (ArgoCD ApplicationSets, Flux multi-tenancy, progressive delivery) and **FinOps Engineering** (Kubecost, Infracost, chargeback automation, FOCUS spec). Neither topic is tested at surface level — interviewers probe the failure modes, not just the happy path.

---

## Part 1: GitOps at Scale

### The Core Problem: Single-Cluster GitOps Does Not Compose

Managing one cluster with ArgoCD or Flux is straightforward. Managing 50 clusters across 3 cloud providers, 12 teams, and 4 environments is an architectural problem. The tools are the same. The design decisions change completely.

```
Single-Cluster GitOps (Solved)          Fleet GitOps (The Real Challenge)
──────────────────────────────          ──────────────────────────────────
1 ArgoCD instance                       Hub-and-spoke: 1 control plane → N agents
1 Git repo                              Monorepo vs. poly-repo debate
1 team owns deployments                 RBAC across 20 teams without collision
Manual app creation                     Templated app generation (ApplicationSets)
Drift in one place                      Drift across 50 clusters simultaneously
```

### ArgoCD Architecture at Scale

#### Hub-and-Spoke: The Only Viable Pattern for 10+ Clusters

```
┌─────────────────────────────────────────────────────────────────┐
│                    MANAGEMENT CLUSTER                            │
│                                                                 │
│  ┌─────────────┐    ┌──────────────┐    ┌──────────────────┐   │
│  │   ArgoCD    │    │  App of Apps │    │  ApplicationSets │   │
│  │  Control    │◄───│   (Bootstrap)│    │  (Fleet Mgmt)    │   │
│  │  Plane      │    └──────────────┘    └──────────────────┘   │
│  └──────┬──────┘                                               │
│         │  Registers clusters via kubeconfig secrets            │
└─────────┼───────────────────────────────────────────────────────┘
          │
    ┌─────┴──────────────────────────────────────┐
    │                                            │
    ▼                                            ▼
┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐
│  Cluster  │  │  Cluster  │  │  Cluster  │  │  Cluster  │
│  prod-eu  │  │  prod-us  │  │  prod-ap  │  │  staging  │
│           │  │           │  │           │  │           │
│  ArgoCD   │  │  ArgoCD   │  │  ArgoCD   │  │  ArgoCD   │
│  Agent    │  │  Agent    │  │  Agent    │  │  Agent    │
└───────────┘  └───────────┘  └───────────┘  └───────────┘
```

**Register a cluster with ArgoCD:**
```bash
# Login to ArgoCD
argocd login argocd.management.example.com --sso

# Add a remote cluster (creates a ServiceAccount in the target cluster)
argocd cluster add prod-eu-context \
  --name prod-eu \
  --label environment=production \
  --label region=eu-west-1

# Verify registration
argocd cluster list
# NAME       SERVER                          VERSION  STATUS  MESSAGE
# prod-eu    https://prod-eu.k8s.example.com 1.28     Synced
# prod-us    https://prod-us.k8s.example.com 1.28     Synced
```

---

### ApplicationSets: The Fleet Management Primitive

ApplicationSets replace manually creating 50 ArgoCD Application objects. They are a template engine that generates Application CRs from a generator.

#### Generator Types and When to Use Each

| Generator | Use Case | Scales To |
|---|---|---|
| `list` | Static set of clusters/envs | <10 targets |
| `cluster` | Every registered cluster | Unlimited |
| `git` | One app per directory in a repo | Monorepo pattern |
| `matrix` | Cross-product of two generators | Clusters × Environments |
| `merge` | Override defaults per cluster | Config exceptions |
| `pull-request` | One app per open PR | Preview environments |
| `scmProvider` | One app per repo in a GitHub org | Org-wide scaffolding |

#### Cluster Generator — Deploy to Every Production Cluster

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
            environment: production    # Only production clusters
  template:
    metadata:
      name: "nginx-ingress-{{name}}"   # name = cluster label
    spec:
      project: platform
      source:
        repoURL: https://github.com/org/platform-config
        targetRevision: HEAD
        path: "apps/nginx-ingress/overlays/{{metadata.labels.region}}"
      destination:
        server: "{{server}}"           # cluster API server URL
        namespace: ingress-nginx
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
        syncOptions:
          - CreateNamespace=true
          - ServerSideApply=true
```

#### Matrix Generator — Cross-Product of Apps × Environments

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
          # First dimension: apps from git directories
          - git:
              repoURL: https://github.com/org/services
              revision: HEAD
              directories:
                - path: "services/*"
          # Second dimension: environments from cluster labels
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

#### Pull Request Generator — Preview Environments per PR

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
            - preview          # Only PRs with "preview" label
  template:
    metadata:
      name: "preview-{{number}}"
    spec:
      source:
        repoURL: https://github.com/org/app-repo
        targetRevision: "{{head_sha}}"
        path: helm/app
        helm:
          values: |
            image.tag: "pr-{{number}}"
            ingress.host: "pr-{{number}}.preview.example.com"
      destination:
        server: https://staging.k8s.example.com
        namespace: "preview-{{number}}"
      syncPolicy:
        automated:
          prune: true
        syncOptions:
          - CreateNamespace=true
```

---

### Flux Multi-Tenancy: The Alternative Fleet Model

Flux takes a different approach: instead of a central control plane, each cluster runs its own Flux instance, and RBAC is enforced via Kustomization service accounts.

```
Flux Architecture (Per-Cluster Model)
──────────────────────────────────────
Git Repository (Source of Truth)
├── clusters/
│   ├── prod-eu/
│   │   ├── flux-system/          # Flux bootstrap components
│   │   └── apps.yaml             # Which app Kustomizations to watch
│   ├── prod-us/
│   └── staging/
├── infrastructure/
│   ├── base/                     # Shared infra (cert-manager, nginx)
│   └── overlays/
│       ├── production/
│       └── staging/
└── apps/
    ├── team-a/                   # Team A owns this path
    └── team-b/                   # Team B owns this path
```

#### Flux Multi-Tenancy Lockdown — Tenant Cannot Escape Their Namespace

```yaml
# In the flux-system Kustomization for a tenant
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: team-a-apps
  namespace: flux-system
spec:
  interval: 5m
  path: ./apps/team-a
  prune: true
  sourceRef:
    kind: GitRepository
    name: fleet-repo
  serviceAccountName: team-a-reconciler    # Limits what Flux can do
  targetNamespace: team-a                   # Forces all resources into this NS
---
# The ServiceAccount has only namespace-scoped permissions
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: team-a-reconciler
  namespace: team-a
subjects:
  - kind: ServiceAccount
    name: team-a-reconciler
    namespace: flux-system
roleRef:
  kind: ClusterRole
  name: cluster-admin   # Scoped to namespace via RoleBinding, not ClusterRoleBinding
  apiGroup: rbac.authorization.k8s.io
```

#### ImageUpdateAutomation — Automated Image Tag Updates

```yaml
# Watch for new image tags matching semver
apiVersion: image.toolkit.fluxcd.io/v1beta2
kind: ImagePolicy
metadata:
  name: app-policy
  namespace: flux-system
spec:
  imageRepositoryRef:
    name: app-repo
  policy:
    semver:
      range: ">=1.0.0 <2.0.0"
---
# Automatically commit the new tag back to Git
apiVersion: image.toolkit.fluxcd.io/v1beta1
kind: ImageUpdateAutomation
metadata:
  name: app-update
  namespace: flux-system
spec:
  interval: 1m
  sourceRef:
    kind: GitRepository
    name: fleet-repo
  git:
    checkout:
      ref:
        branch: main
    commit:
      author:
        email: fluxbot@example.com
        name: Flux Bot
      messageTemplate: "chore: update {{range .Updated.Images}}{{.}}{{end}}"
    push:
      branch: main
  update:
    path: ./apps
    strategy: Setters
```

---

### Progressive Delivery at Fleet Scale

#### Flagger + Istio: Automated Canary with Metric Gates

```yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: payment-service
  namespace: production
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: payment-service
  progressDeadlineSeconds: 60
  service:
    port: 80
    targetPort: 8080
    trafficPolicy:
      tls:
        mode: ISTIO_MUTUAL
  analysis:
    interval: 1m
    threshold: 5             # Max failed checks before rollback
    maxWeight: 50            # Max canary traffic %
    stepWeight: 10           # Increment per successful check
    metrics:
      - name: request-success-rate
        thresholdRange:
          min: 99
        interval: 1m
      - name: request-duration
        thresholdRange:
          max: 500           # P99 latency in ms
        interval: 30s
    webhooks:
      - name: load-test
        url: http://loadtester.test/
        timeout: 5s
        metadata:
          cmd: "hey -z 1m -q 10 -c 2 http://payment-service-canary/"
```

---

### Drift Detection and Remediation at Scale

```bash
# Find all out-of-sync applications across the fleet
argocd app list --output json | \
  jq -r '.[] | select(.status.sync.status != "Synced") | 
  "\(.metadata.name) \(.status.sync.status) \(.status.health.status)"'

# Sync all apps in a specific project that are out of sync
argocd app list -p platform --output name | \
  xargs -I{} argocd app sync {} --async

# Force self-heal for a specific app (override manual drift)
argocd app patch payment-service \
  --patch '{"spec":{"syncPolicy":{"automated":{"selfHeal":true}}}}'

# Diff what ArgoCD would change (dry run)
argocd app diff payment-service --refresh

# Get sync status across all clusters for a specific app
argocd app list --selector app.kubernetes.io/name=nginx-ingress \
  --output wide
```

---

## Part 2: FinOps Engineering

> [!IMPORTANT]
> FinOps in interviews is tested differently from the marketing definition. Staff-level interviews expect you to know the **tooling integrations**, **allocation mechanics**, and **the failure modes of chargeback models** — not just that you "right-size instances."

### The FinOps Lifecycle

```
┌──────────────────────────────────────────────────────────────┐
│                    FINOPS LIFECYCLE                           │
│                                                              │
│   INFORM         OPTIMIZE         OPERATE                    │
│   ───────        ────────         ───────                    │
│   Visibility     Rate optim.      Culture                    │
│   Allocation     Usage optim.     Forecasting                │
│   Benchmarking   Rightsizing      Anomaly alerts             │
│   Tagging        Reservations     Showback/Chargeback         │
│                  Spot instances   Policy enforcement         │
└──────────────────────────────────────────────────────────────┘
```

### Tagging Strategy: The Foundation of Everything

Without consistent tags, no chargeback model works. This is the most common FinOps failure.

```
Required Tag Taxonomy (Non-Negotiable)
──────────────────────────────────────
team:          payments / recommendations / auth
environment:   production / staging / development
cost-center:   CC-4421 / CC-8831
project:       checkout-v3 / ml-serving
owner:         squad-lead-email
managed-by:    terraform / helm / manual  ← identifies tag drift source
```

**Enforce tags via OPA/Gatekeeper (deny untagged resources):**

```yaml
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: RequiredLabels
metadata:
  name: require-cost-labels
spec:
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Namespace"]
      - apiGroups: ["apps"]
        kinds: ["Deployment"]
  parameters:
    labels:
      - key: team
      - key: cost-center
      - key: environment
```

---

### Kubecost: Kubernetes Cost Intelligence

Kubecost provides per-namespace, per-label, per-deployment cost allocation using actual cloud billing data combined with resource utilization metrics.

#### Install Kubecost

```bash
# Install via Helm
helm repo add kubecost https://kubecost.github.io/cost-analyzer/
helm upgrade --install kubecost kubecost/cost-analyzer \
  --namespace kubecost \
  --create-namespace \
  --set kubecostToken="<your-token>" \
  --set global.prometheus.enabled=true \
  --set global.grafana.enabled=false \     # Use existing Grafana
  --set kubecostMetrics.emitPodAnnotations=true

# Expose the UI locally
kubectl port-forward -n kubecost svc/kubecost-cost-analyzer 9090
```

#### Kubecost API — Programmatic Cost Queries

```bash
# Cost by namespace for the last 7 days
curl "http://localhost:9090/model/allocation?window=7d&aggregate=namespace" | \
  jq '.data[0] | to_entries[] | {ns: .key, cost: .value.totalCost}' | \
  sort -t: -k2 -rn

# Cost by label (team) for last 30 days
curl "http://localhost:9090/model/allocation?window=30d&aggregate=label:team" | \
  jq '.data[0] | to_entries[] | "\(.key): $\(.value.totalCost | . * 100 | round / 100)"'

# Efficiency report — find wasteful workloads
curl "http://localhost:9090/model/allocation?window=7d&aggregate=deployment&idle=true" | \
  jq '.data[0] | to_entries[] | 
  select(.value.cpuEfficiency < 0.3 or .value.ramEfficiency < 0.3) |
  {deployment: .key, cpu_eff: .value.cpuEfficiency, ram_eff: .value.ramEfficiency, cost: .value.totalCost}'
```

#### Kubecost Savings Recommendations

```bash
# Get rightsizing recommendations for all deployments
curl "http://localhost:9090/savings/requestSizingV2?window=7d&targetUtilization=0.7" | \
  jq '.recommendations[] | {
    deployment: .controllerName,
    namespace: .namespace,
    currentCpu: .currentEfficiency.cpuRequest,
    recommendedCpu: .recommendedRequest.cpu,
    savings: .monthlySavings
  }'

# Check for orphaned PVCs (storage not attached to any pod)
kubectl get pvc --all-namespaces --no-headers | \
  awk '$6 == "Bound" {print $1, $2, $4}' | \
  while read ns name size; do
    pods=$(kubectl get pods -n $ns -o json | \
      jq -r ".items[].spec.volumes[]?.persistentVolumeClaim?.claimName // empty" | \
      grep -c "^$name$" || true)
    [[ $pods -eq 0 ]] && echo "ORPHANED: $ns/$name ($size)"
  done
```

---

### Infracost: Shift-Left Cost in CI/CD

Infracost adds cost estimates to pull requests before infrastructure changes are applied. This is the shift-left approach — catch expensive changes at review time, not billing time.

#### GitHub Actions Integration

```yaml
# .github/workflows/infracost.yml
name: Infracost
on:
  pull_request:
    paths:
      - '**.tf'

jobs:
  infracost:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write

    steps:
      - uses: actions/checkout@v4

      - name: Setup Infracost
        uses: infracost/actions/setup@v3
        with:
          api-key: ${{ secrets.INFRACOST_API_KEY }}

      # Baseline: cost of the base branch
      - name: Generate cost estimate for base branch
        run: |
          git checkout ${{ github.base_ref }}
          infracost breakdown --path=./terraform \
            --format=json \
            --out-file=/tmp/infracost-base.json
          git checkout ${{ github.head_ref }}

      # PR branch cost
      - name: Generate cost estimate for PR branch
        run: |
          infracost breakdown --path=./terraform \
            --format=json \
            --out-file=/tmp/infracost-pr.json

      # Post diff as PR comment
      - name: Post Infracost diff comment
        uses: infracost/actions/comment@v3
        with:
          path: /tmp/infracost-pr.json
          compare-to: /tmp/infracost-base.json
          behavior: update   # Update existing comment, don't spam
```

**What this produces in a PR:**

```
Monthly cost estimate change
───────────────────────────────────────────────────────────────
Project: terraform/
  + aws_instance.app_server   +$142.00/mo  (m5.2xlarge → m5.4xlarge)
  ~ aws_db_instance.postgres   +$67.00/mo  (db.t3.medium → db.t3.large)

Total change: +$209.00/mo  (+$2,508/yr)
```

#### Cost Policy Gate — Block Expensive PRs

```yaml
# Block PRs that increase cost by more than $500/mo
- name: Check cost threshold
  run: |
    DIFF=$(infracost diff \
      --path=./terraform \
      --compare-to=/tmp/infracost-base.json \
      --format=json | jq '.diffTotalMonthlyCost | tonumber')
    
    if (( $(echo "$DIFF > 500" | bc -l) )); then
      echo "ERROR: PR increases monthly cost by \$$DIFF (limit: \$500)"
      echo "Requires explicit cost approval — add label 'cost-approved'"
      exit 1
    fi
```

---

### Chargeback vs. Showback

| Model | Definition | Team Accountability | Political Difficulty |
|---|---|---|---|
| **Showback** | Show teams what they cost, but don't bill internally | Low — informational only | Low |
| **Chargeback** | Internally bill teams via budget transfer | High — teams feel the cost | High — requires finance process |
| **Hybrid** | Showback today, chargeback in 6 months | Medium | Medium |

> [!TIP]
> Start with showback. The act of showing teams their cost without charging them still produces 20-40% waste reduction (the "visibility effect"). Chargeback adds political overhead — implement it only after teams have been educated on cost for 2+ quarters.

#### Automated Chargeback Report (Kubecost API + Python)

```python
import requests
import pandas as pd
from datetime import datetime

KUBECOST_URL = "http://kubecost.monitoring:9090"

def generate_monthly_chargeback(month: str) -> pd.DataFrame:
    """Generate chargeback report for finance team."""
    resp = requests.get(
        f"{KUBECOST_URL}/model/allocation",
        params={
            "window": month,           # e.g., "2026-03"
            "aggregate": "label:cost-center,label:team",
            "accumulate": "true",
            "shareIdle": "true",       # Distribute idle cost proportionally
            "shareSplit": "weighted",
        }
    )
    resp.raise_for_status()
    
    allocations = resp.json()["data"][0]
    
    rows = []
    for key, alloc in allocations.items():
        cost_center, team = key.split("/") if "/" in key else (key, "unknown")
        rows.append({
            "cost_center": cost_center.replace("cost-center=", ""),
            "team": team.replace("team=", ""),
            "compute_cost": round(alloc.get("cpuCost", 0) + alloc.get("ramCost", 0), 2),
            "storage_cost": round(alloc.get("pvCost", 0), 2),
            "network_cost": round(alloc.get("networkCost", 0), 2),
            "total_cost": round(alloc.get("totalCost", 0), 2),
            "efficiency": round(alloc.get("efficiency", 0) * 100, 1),
        })
    
    df = pd.DataFrame(rows).sort_values("total_cost", ascending=False)
    df.to_csv(f"chargeback-{month}.csv", index=False)
    return df

if __name__ == "__main__":
    report = generate_monthly_chargeback("2026-03")
    print(report.to_string())
```

---

### Spot / Preemptible Instance Strategy

#### Node Pool Architecture for Cost Optimization

```
Workload Classification for Spot Strategy
───────────────────────────────────────────
NEVER on spot:          etcd, control plane, stateful databases, 
                        payment processing, auth services

GOOD on spot:           ML training jobs, batch data processing,
                        CI runners, dev/staging workloads

BEST on spot:           Fault-tolerant stateless services with
                        graceful shutdown + fast restart

ARCHITECTURE PATTERN:
  On-Demand Pool        → System-critical + stateful (min size: 3)
  Spot Pool (Diverse)   → Batch + training + stateless (auto-scale)
  Spot Pool (GPU)       → ML training only (terminate on preemption)
```

#### Kubernetes Node Affinity for Spot Routing

```yaml
# Tolerations and affinity to route ML training to spot GPU nodes
apiVersion: batch/v1
kind: Job
metadata:
  name: ml-training-job
spec:
  template:
    spec:
      tolerations:
        - key: "cloud.google.com/gke-spot"
          operator: "Equal"
          value: "true"
          effect: "NoSchedule"
        - key: "nvidia.com/gpu"
          operator: "Exists"
          effect: "NoSchedule"
      affinity:
        nodeAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              preference:
                matchExpressions:
                  - key: cloud.google.com/gke-spot
                    operator: In
                    values: ["true"]
      containers:
        - name: trainer
          image: training:v1.2
          resources:
            limits:
              nvidia.com/gpu: "1"
      restartPolicy: OnFailure
```

---

### FOCUS Spec — Cloud Cost Data Standardization

> [!NOTE]
> FOCUS (FinOps Open Cost and Usage Specification) is an emerging standard that normalizes cloud billing data across AWS, Azure, and GCP into a common schema. Staff-level FinOps interviews increasingly test awareness of this.

**Problem it solves:** AWS CUR, Azure Cost Details, and GCP Billing Export have completely different schemas. Multi-cloud cost analysis requires ETL to normalize them.

**FOCUS standardizes:**
- `BilledCost` — what you actually pay
- `EffectiveCost` — amortized cost (reservations spread over period)
- `ResourceType` — normalized resource kind
- `ServiceName` — normalized service name
- `ChargeCategory` — Usage / Tax / Adjustment / Purchase

```python
# Query FOCUS-normalized billing data (Athena / BigQuery / Synapse)
FOCUS_QUERY = """
SELECT
    BillingPeriodStartDate,
    SubAccountName AS team_account,
    ServiceName,
    ResourceType,
    SUM(BilledCost) AS total_billed,
    SUM(EffectiveCost) AS total_effective
FROM focus_billing_export
WHERE 
    BillingPeriodStartDate >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1' MONTH)
    AND ChargeCategory = 'Usage'
GROUP BY 1, 2, 3, 4
ORDER BY total_effective DESC
LIMIT 100
"""
```

---

### Cost Anomaly Detection

#### Prometheus Rules for Spend Spike Alerts

```yaml
# prometheus/rules/finops.yml
groups:
  - name: finops
    rules:
      # Alert if namespace cost increases > 30% week-over-week
      - alert: NamespaceCostSpike
        expr: |
          (
            kubecost_namespace_total_cost offset 0d
            /
            kubecost_namespace_total_cost offset 7d
          ) > 1.3
        for: 1h
        labels:
          severity: warning
          team: "{{ $labels.namespace }}"
        annotations:
          summary: "Cost spike in namespace {{ $labels.namespace }}"
          description: >
            Namespace {{ $labels.namespace }} cost increased by
            {{ $value | humanizePercentage }} vs last week.
            Check for new deployments, traffic increases, or misconfigured HPA.

      # Alert if cluster idle cost exceeds 40% of total
      - alert: HighClusterIdleCost
        expr: |
          kubecost_cluster_idle_cost / kubecost_cluster_total_cost > 0.4
        for: 6h
        labels:
          severity: warning
        annotations:
          summary: "Cluster idle cost is {{ $value | humanizePercentage }}"
          description: >
            More than 40% of cluster cost is idle (unused requests).
            Consider rightsizing or reducing resource requests.
```

---

### Reserved Instance / Committed Use Coverage

```bash
# AWS: Check RI coverage for EC2
aws ce get-reservation-coverage \
  --time-period Start=2026-03-01,End=2026-03-31 \
  --granularity MONTHLY \
  --group-by Type=DIMENSION,Key=INSTANCE_TYPE \
  --query 'CoveragesByTime[0].Groups[*].[Attributes.INSTANCE_TYPE, Coverage.CoverageHours.CoverageHoursPercentage]' \
  --output table

# Target: >80% RI/SP coverage for predictable workloads
# Anything below 60% is wasted on-demand spend

# GCP: Check Committed Use Discount coverage
gcloud compute commitments list --format="table(name,region,status,endTimestamp)"

# Azure: Reservation utilization
az consumption reservation detail list \
  --reservation-order-id <order-id> \
  --start-date 2026-03-01 \
  --end-date 2026-03-31 \
  --query "[].{ResourceType:reservationType, Util:utilizationPercentage}" \
  --output table
```

---

### The GitOps × FinOps Integration

The highest-value intersection: use GitOps to enforce cost policy.

```
GitOps + FinOps = Cost Policy as Code
──────────────────────────────────────
Developer submits PR with new Deployment
         │
         ▼
Infracost runs in CI → cost delta comment added to PR
         │
         ▼
OPA/Gatekeeper blocks Deployments without resource limits
         │
         ▼
ArgoCD syncs approved config to cluster
         │
         ▼
Kubecost tracks actual spend vs. forecast
         │
         ▼
Prometheus alerts on anomalous spend
         │
         ▼
Monthly chargeback report sent to finance
```

**OPA Policy — Block Deployments Without Resource Limits:**

```rego
# opa/policies/require-resource-limits.rego
package kubernetes.admission

deny[msg] {
  input.request.kind.kind == "Deployment"
  container := input.request.object.spec.template.spec.containers[_]
  not container.resources.limits.cpu
  msg := sprintf(
    "Deployment '%v' container '%v' must set cpu limits (FinOps policy)",
    [input.request.object.metadata.name, container.name]
  )
}

deny[msg] {
  input.request.kind.kind == "Deployment"
  container := input.request.object.spec.template.spec.containers[_]
  not container.resources.limits.memory
  msg := sprintf(
    "Deployment '%v' container '%v' must set memory limits (FinOps policy)",
    [input.request.object.metadata.name, container.name]
  )
}
```

---

## Three-Pillar Interview Question Bank

### Easy — Junior/Mid-Level (0-3 YOE)

**Q1: What is GitOps and how does it differ from traditional push-based deployment?**

GitOps is a deployment model where Git is the single source of truth for both application and infrastructure state. A GitOps operator (ArgoCD or Flux) runs inside the cluster and continuously reconciles the live cluster state against the desired state declared in Git.

Traditional push-based deployment: CI pipeline runs `kubectl apply` or `helm upgrade` directly — the pipeline has cluster credentials and pushes changes.

GitOps pull-based: The cluster pulls from Git. The pipeline has no cluster credentials. It only writes to Git. The operator handles the apply.

Key differences:
- **Audit trail**: Every change is a Git commit with author, timestamp, and diff
- **Rollback**: `git revert` is the rollback mechanism — no manual `kubectl` needed
- **Drift detection**: The operator alerts when live state diverges from Git state
- **Credentials**: Pipeline has no cluster access — attack surface reduced

**Q2: What is Kubecost and what problem does it solve?**

Kubernetes clusters have a fundamental cost visibility problem: cloud bills show you spending on nodes, but not which team, application, or feature is responsible for that spend. A single node runs dozens of pods from different teams.

Kubecost solves this by:
1. Querying resource usage metrics from the Kubernetes metrics API and Prometheus
2. Mapping resource usage to cloud billing rates (from the cloud provider's pricing API or your actual cloud bill via CUR/Cost Details integration)
3. Allocating costs to namespaces, labels, deployments, and teams based on their actual resource consumption

The output is: "Team A's payment service cost $2,340 last month. It was 38% efficient — $1,450 was idle resource reservation waste."

---

### Medium — Senior-Level (3-6 YOE)

**Q3: A team is complaining that ArgoCD is reverting their manual changes. How do you handle this operationally and architecturally?**

This is expected GitOps behavior, not a bug. ArgoCD's self-heal feature is doing exactly what it should. But the team's complaint reveals a cultural and process gap.

**Immediate diagnosis:**
```bash
# See what ArgoCD keeps reverting
argocd app history payment-service
argocd app diff payment-service

# Check if self-heal is enabled
argocd app get payment-service | grep selfHeal
```

**Short-term options:**
1. **Disable self-heal temporarily** if the team has a legitimate emergency change that hasn't been committed to Git yet — this is the correct escape hatch for production incidents
2. **`argocd app patch payment-service --patch '{"spec":{"syncPolicy":null}}'`** — removes automated sync entirely, requires manual sync

**Architectural response:**
- The team is working around the process because their Git-to-production feedback loop is too slow
- Reduce this by setting up branch-based preview environments so they can test changes in Git before production
- Add a fast-path: a `hotfix/` branch that gets accelerated review and deploys to production within 15 minutes
- Never disable self-heal permanently — it's the core value of GitOps for drift detection

**Q4: How do you implement a chargeback model for a 20-team organization using Kubernetes?**

Three-phase approach:

**Phase 1 — Visibility (Month 1-2):**
- Deploy Kubecost with a standardized label taxonomy enforced via OPA Gatekeeper
- Required labels: `team`, `cost-center`, `environment`, `project`
- Send weekly showback reports per team — email or Slack with cost by service
- No financial consequences yet

**Phase 2 — Optimization (Month 3-4):**
- Set resource efficiency targets: >70% CPU and memory utilization
- Kubecost savings recommendations → create Jira tickets per team for rightsizing
- Teams with <50% efficiency get mandatory resource review

**Phase 3 — Chargeback (Month 5+):**
- Pull monthly cost data via Kubecost API, broken down by `cost-center` label
- Submit internal budget transfers via finance system API
- Share idle cost proportionally (weighted by usage, not equally split — equal split disincentivizes efficiency)
- Keep a 10% buffer for untaggable shared infrastructure (DNS, ingress controllers, monitoring stack)

Failure modes to anticipate:
- Teams game labels to move cost to shared pools → audit label changes in Git history
- Shared services get blamed for consumer team costs → track ingress and egress separately

---

### Hard — Staff/Architect-Level (7+ YOE)

**Q5: Design a FinOps platform for a 50-team organization running in multi-cloud (AWS + GCP + Azure). What are the hardest problems and how do you solve them?**

The hardest problems are not tool selection — they are data normalization, allocation methodology, and organizational behavior change.

**Data Normalization:**
Three clouds, three billing schemas. Solution: adopt FOCUS spec as the internal standard. Build an ETL pipeline:
```
AWS CUR (S3) ──┐
GCP BigQuery ──┼──► FOCUS normalizer ──► Central data lake (Iceberg/Delta) ──► Kubecost + Looker
Azure Export ──┘
```
FOCUS fields that matter most: `EffectiveCost` (amortized reservations), `SubAccountName` (team-level account), `ServiceName` (normalized), `ResourceType`.

**Allocation Challenges:**
- Kubernetes costs are cluster-level; cloud bills are account-level. You need Kubecost (or equivalent) to do sub-account allocation within clusters.
- Network egress costs are hard to allocate: use flow logs + destination IP to map to consuming services
- Shared services (DNS, monitoring, load balancers) — use weighted proportional allocation based on request volume, not flat split

**Reservation Strategy:**
- AWS: Savings Plans (compute, not EC2 — more flexible) for 60-70% of baseline
- GCP: Committed Use Discounts at project level, auto-apply when possible
- Azure: Reserved Instances at subscription level for predictable VM types
- Problem: reservations are billed to payer account, consumed by many teams. Finance must amortize commitment across consumers — typically monthly, using `EffectiveCost` from FOCUS

**Organization Change (The Hard Part):**
- Engineers don't care about cost until they're accountable for it
- Start showback + efficiency leaderboards (public, positive-sum)
- Set cost per-unit-of-business-value targets ("cost per 1M API calls") not absolute cost — this prevents penalizing teams for growth
- Have SREs own the FinOps platform, not finance — finance can access reports but should not drive engineering decisions

**Q6: Your GitOps fleet has 60 clusters. During a major Kubernetes version upgrade (1.27 → 1.28), a CRD schema change breaks all ArgoCD Application CRs in 15 clusters simultaneously. How do you respond and what architectural changes prevent this?**

**Immediate Response (first 30 minutes):**

```bash
# Identify affected clusters
argocd cluster list --output json | \
  jq -r '.[] | select(.connectionState.status == "Failed") | .name'

# Check what the CRD change broke
kubectl get crds | grep argoproj.io
kubectl explain application.spec --api-version=argoproj.io/v1alpha1

# On affected clusters: check ArgoCD controller logs
kubectl logs -n argocd deploy/argocd-application-controller --tail=100 | \
  grep -i "error\|failed\|invalid"

# Emergency: pause sync on all affected clusters to prevent cascading failures
argocd app list --output name | xargs -P10 -I{} \
  argocd app patch {} --patch '{"operation":null}' --grpc-web
```

**Recovery path:**
1. If CRD is backwards-compatible: update ArgoCD version on hub cluster first, let it propagate the schema update to spoke clusters
2. If not backwards-compatible: use `kubectl convert` to migrate existing Application CRs before upgrading the CRD

**Architectural Lessons (prevent recurrence):**

1. **Ring-based rollout for platform upgrades** — never upgrade all 60 clusters simultaneously:
   ```
   Ring 0: 1 canary cluster (non-critical workloads)
   Ring 1: 5% of production clusters
   Ring 2: 25% of production clusters
   Ring 3: Remaining production clusters
   Minimum wait between rings: 24 hours with passing health checks
   ```

2. **ApplicationSet canary for platform components:**
   ```yaml
   # First generator: canary clusters only
   - cluster:
       selector:
         matchLabels:
           upgrade-ring: "0"
   # Second generator (different ApplicationSet): ring-1 etc.
   ```

3. **Pre-upgrade CRD compatibility check in CI:**
   ```bash
   # Before upgrading K8s or ArgoCD, validate CRD compatibility
   kubectl-convert -f application.yaml --output-version argoproj.io/v1alpha1
   # Fails if existing objects can't be represented in new schema
   ```

4. **Separate the fleet control plane from the workload clusters** — ArgoCD hub cluster runs K8s N-2 (conservative), spoke clusters can run N. Hub cluster Kubernetes upgrade is the highest-risk operation in the fleet.

---

## Key Concepts Summary

| Concept | One-Line Definition | Interview Signal |
|---|---|---|
| ApplicationSet | ArgoCD template that generates N Applications from a generator | Name all 7 generator types |
| Hub-and-spoke | One ArgoCD control plane managing many clusters via agent | Know why it beats N separate ArgoCD instances |
| Flux multi-tenancy | Per-namespace ServiceAccounts limiting what each team's reconciler can touch | Know the `targetNamespace` + `serviceAccountName` pattern |
| Showback | Cost visibility without internal billing | Know why to start here before chargeback |
| Chargeback | Internal budget transfer based on resource consumption | Know the failure modes (label gaming, shared cost allocation) |
| Kubecost | K8s cost allocation tool using metrics + cloud billing | Know the efficiency metric and API query pattern |
| Infracost | Pre-apply cost estimate in CI/CD PRs | Know how to gate PRs on cost delta |
| FOCUS spec | Cross-cloud billing schema normalization standard | Know `EffectiveCost` vs. `BilledCost` distinction |
| Ring-based rollout | Staged cluster upgrade: canary → small% → full fleet | Know the ring structure and gate criteria |
| Drift detection | ArgoCD/Flux alerting when live state ≠ Git state | Know the difference between drift and intended manual changes |

---

*See also: [Interview Hub](README.md) | [DevOps Hard Questions](interview-questions-hard.md) | [Platform Engineering & FinOps](../06_Advanced_DevOps_and_Architecture/Platform_Engineering_and_FinOps.md) | [eBPF & Service Mesh](advanced-ebpf-and-service-mesh.md)*
