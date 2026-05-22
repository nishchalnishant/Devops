# ArgoCD and GitOps — Interview Prep

---
description: Easy, Medium, and Hard interview questions for ArgoCD, GitOps, and progressive delivery.
---

```
ArgoCD Interview Topics Map
├── GitOps Fundamentals
│   ├── GitOps: Git as single source of truth for declarative desired state
│   ├── Push-based: CI pipeline holds kubeconfig, pushes kubectl apply
│   ├── Pull-based: ArgoCD agent inside cluster polls Git, applies on drift
│   └── 4 Properties: Declarative | Versioned | Pulled | Continuously Reconciled
│
├── ArgoCD Core Concepts
│   ├── Application CRD: source (repo+path+revision) + destination (cluster+namespace)
│   ├── Sync status: Synced | OutOfSync | Unknown
│   ├── Health status: Healthy | Progressing | Degraded | Suspended | Missing | Unknown
│   ├── Automated sync: selfHeal (corrects drift) + prune (removes deleted resources)
│   └── ignoreDifferences: exclude controller-managed fields from diff
│
├── Kustomize vs Helm in ArgoCD
│   ├── Kustomize: patch overlays on base YAML — no templating, no release lifecycle
│   ├── Helm: ArgoCD uses helm template (not helm install), owns lifecycle
│   └── ArgoCD renders to plain YAML before applying — same result either way
│
├── Secret Management
│   ├── Sealed Secrets: kubeseal encrypts with controller public key, safe to commit
│   ├── External Secrets Operator: ExternalSecret CRD → fetches from Vault/AWS SM
│   └── SOPS + CMP: encrypted files in Git; CMP plugin decrypts at render time
│
├── ApplicationSet
│   ├── Template + generator = N Applications
│   ├── Generators: list | cluster | git (dirs/files) | matrix | merge | pullRequest | scmProvider
│   └── Use case: deploy same app to 50 clusters, or per-service in monorepo
│
├── ArgoCD vs Flux
│   ├── ArgoCD: centralized, UI-rich, Application CRD, multi-tenant Projects
│   └── Flux: modular controllers, no UI, CLI/Git-driven, lighter weight
│
├── Progressive Delivery
│   ├── Blue-green: binary 0%/100% traffic switch with rollback
│   ├── Canary: gradual 5%→20%→50%→100% with metric-gated promotion
│   ├── Argo Rollouts: Rollout CRD, AnalysisTemplate, kubectl argo rollouts CLI
│   └── Flagger: watches Deployment, configures mesh VirtualService automatically
│
├── Multi-Cluster & Fleet
│   ├── Hub-and-spoke: one ArgoCD control plane → N spoke clusters via cluster secrets
│   ├── ApplicationSet cluster generator: auto-creates Application per cluster
│   ├── Ring-based upgrades: Ring 0 (canary) → Ring 1 → Ring 2 → Ring 3 (all)
│   └── Controller sharding: ARGOCD_CONTROLLER_REPLICAS for 200+ clusters
│
├── App of Apps Pattern
│   ├── Root Application points to directory of Application manifests
│   ├── Child Applications manage actual workloads
│   └── Bootstrap: create root Application once; everything else self-manages
│
└── Sync Waves & Hooks
    ├── argocd.argoproj.io/sync-wave: "N" — ascending wave order
    ├── PreSync: before sync (CRD install, schema migrations)
    ├── PostSync: after all healthy (smoke tests, notifications)
    └── SyncFail: on failure (alerts, rollback triggers)
```

### First Principles

- GitOps is a deployment model where the cluster is always trying to reach Git state. The operator never stops running; it reconciles continuously. This is different from CI/CD where deployment is a discrete event.
- Pull-based deployment inverts the security model: the cluster has Git credentials, not the CI server. A compromised CI pipeline cannot push to the cluster — it can only corrupt Git history, which is detectable and reversible.
- ArgoCD's `Application` CRD is a declarative deployment target: desired state (Git source) + deployment destination (cluster + namespace) + sync policy. Everything else (health, drift, history) is derived from these three inputs.
- `ignoreDifferences` is not a workaround — it is the correct way to model fields that are owned by other controllers. ArgoCD should only control what it declared; controllers that mutate post-apply own those fields.
- The App of Apps pattern makes ArgoCD self-managing: the root Application definition is the only thing that needs to exist before ArgoCD can bootstrap an entire cluster.
- Progressive delivery extends GitOps from "deploy this version" to "promote this version safely." The Rollout spec in Git is the desired delivery strategy; the controller executes it step by step with automated rollback on failure.

## Easy

**1. What is GitOps?**

GitOps is an operating model that uses Git as the single source of truth for declarative infrastructure and application configuration. Every desired state is committed to Git; an automated system continuously reconciles the actual state with what is in Git.

**2. What is the difference between push-based and pull-based CI/CD?**

In a push model, a CI pipeline is given cluster credentials and pushes changes by running `kubectl apply` or `helm upgrade` after a build. In a pull model, an agent (ArgoCD, Flux) runs inside the cluster and continuously polls a Git repository. When it detects drift between Git state and cluster state, it pulls and applies the changes. Credentials never leave the cluster.

**3. What is ArgoCD?**

ArgoCD is a declarative GitOps continuous delivery tool for Kubernetes. It monitors Git repositories for changes to Kubernetes manifests and automatically (or on demand) applies them to the cluster. It provides a UI and CLI showing sync status, drift detection, and rollback capability.

**4. What is an ArgoCD Application?**

An `Application` is an ArgoCD custom resource that defines a source (Git repo + path + revision) and a destination (cluster + namespace). ArgoCD continuously compares the desired state in the source to the live state in the destination and reports sync status.

**5. What manifest formats does ArgoCD support?**

ArgoCD natively supports: raw Kubernetes YAML/JSON, Helm charts, Kustomize overlays, and Jsonnet. It also supports custom config management plugins for other templating tools.

**6. What is drift detection in ArgoCD?**

Drift occurs when the live cluster state diverges from the state declared in Git — usually caused by manual `kubectl` edits. ArgoCD continuously compares live and desired state; when they differ, the Application shows as `OutOfSync`. ArgoCD can be configured to alert or auto-sync to correct drift.

**7. What is the difference between `Synced` and `Healthy` in ArgoCD?**

`Synced` means the live cluster state matches what is defined in Git. `Healthy` means the deployed resources are actually functioning correctly (pods running, deployments at desired replica count, etc.). An application can be `Synced` but `Degraded` — for example, the manifests were applied but a pod is in a CrashLoopBackOff state.

**8. How do you manually trigger a sync in ArgoCD?**

Via the UI (click Sync on the Application), via CLI (`argocd app sync my-app`), or via the API. You can also set `syncPolicy.automated: {}` to enable automatic syncing whenever ArgoCD detects a drift.

**9. What is a sync wave in ArgoCD?**

A sync wave is an annotation (`argocd.argoproj.io/sync-wave: "N"`) that controls the order in which resources are applied during a sync. Resources in wave `-1` are applied before wave `0`, which applies before wave `1`. This allows ordered dependency management — e.g., apply CRDs (wave 0) before Custom Resources (wave 1), or apply a database migration job (wave 1) before the application Deployment (wave 2).

**10. What is a sync hook in ArgoCD?**

A sync hook is a Job or Pod that runs at a specific phase of the sync lifecycle: `PreSync` (before resources are applied), `Sync` (during the sync), `PostSync` (after sync succeeds), or `SyncFail` (if sync fails). Common use cases: run database migrations in PreSync, run smoke tests in PostSync, send alerts in SyncFail.

**11. What is the App-of-Apps pattern?**

App-of-Apps uses a root ArgoCD Application whose source directory contains other ArgoCD Application manifests. When the root syncs, it creates all child Applications, which then sync their own resources. This bootstraps an entire environment from a single application — useful for cluster bootstrapping and managing many apps in a structured, versioned way.

**12. What is `argocd app diff`?**

`argocd app diff my-app` shows the difference between the desired state (from Git/Helm) and the current live state in the cluster, similar to `terraform plan`. Useful for reviewing changes before syncing or for debugging OutOfSync states.

***

## Medium

**13. What is an ArgoCD ApplicationSet and when would you use it?**

An ApplicationSet is a controller that generates multiple ArgoCD Applications from a single template, using generators such as List, Git, Matrix, or Cluster. Use it when deploying the same application across multiple clusters or environments without defining a separate Application resource for each. Example: a cluster generator automatically creates an Application per registered cluster, deploying a base monitoring stack to all 200 clusters.

**14. Compare ArgoCD and Flux. What are the key architectural differences?**

- **ArgoCD:** More centralized and opinionated. Has a comprehensive UI, and the `Application` CRD is the central concept. Better for multi-tenant GitOps platforms with rich self-service.
- **Flux:** More modular, following the Unix philosophy. It's a collection of specialized controllers (for sourcing from Git, applying manifests, handling Helm releases) composed together. Lighter weight, no built-in UI, better for organizations that prefer CLI- and Git-driven workflows.

**15. How do you manage secrets in a GitOps workflow where manifests are in a Git repository?**

Use Sealed Secrets or External Secrets Operator:

- **Sealed Secrets (Bitnami):** A controller in the cluster holds a private key. Developers encrypt Secrets with `kubeseal` using the controller's public key. The resulting `SealedSecret` is safe to commit. The controller decrypts it into a real Secret at apply time.
- **External Secrets Operator:** `ExternalSecret` resources reference secrets in Vault, AWS Secrets Manager, or Azure Key Vault by path. The controller fetches and syncs secret values into Kubernetes Secrets. No encrypted data stored in Git.

**16. What is Flagger and how does it enable progressive delivery on top of a service mesh?**

Flagger is a progressive delivery operator that automates canary, A/B, and blue-green deployments:

1. Flagger watches for changes to a `Deployment`.
2. When it sees a new version, it creates a canary Deployment and configures the service mesh (Istio `VirtualService`) to send a small traffic percentage to it.
3. It runs an automated analysis loop querying Prometheus SLIs.
4. If metrics are healthy, it gradually increases traffic to the canary. If not, it automatically rolls back.

**17. What is progressive delivery and how does it improve on blue-green deployments?**

Blue-green is binary: 0% or 100% traffic on the new version. Progressive delivery introduces gradual traffic shifting with automated metric-gated promotion:
- **Canary releases:** 5% → 20% → 50% → 100% with automated promotion criteria.
- **Feature flags:** Enable for 1% of users, then internal employees, then geographic regions.
- **Traffic mirroring:** Copy 100% of live traffic to the new version without serving real responses — test under production load with zero risk.

**18. What is Kustomize and how does it differ from Helm?**

Kustomize applies patch overlays to a base set of Kubernetes YAML files without templating. It uses `kustomization.yaml` to reference a base and layer environment-specific patches on top. Helm is a full package manager with Go templating, versioned charts, and a release lifecycle (`install`, `upgrade`, `rollback`). Kustomize is lighter and better for simple per-environment customization; Helm is better for distributing complex applications with many configurable parameters.

**19. How do you handle RBAC and multi-tenancy in ArgoCD?**

ArgoCD Projects (`AppProject`) define RBAC boundaries for teams:
- **Source repos:** Which Git repositories a project can deploy from.
- **Destination clusters/namespaces:** Which clusters and namespaces the project can deploy to.
- **Cluster resource whitelist:** Which cluster-scoped resources (CRDs, ClusterRoles) are allowed.

Combined with ArgoCD RBAC (`argocd-rbac-cm` ConfigMap), roles like `admin`, `readonly`, or `deploy-only` are assigned to SSO groups. A team can only see and sync their own project's applications.

**20. How does ArgoCD handle Helm chart deployments?**

ArgoCD can deploy Helm charts directly — it renders the chart with `helm template` (not `helm install`) and applies the resulting YAML. This means: ArgoCD owns the lifecycle (not Helm), release secrets are not created in the cluster, and upgrades go through ArgoCD's sync process. To pass values, use the `helm.values` or `helm.parameters` fields in the Application spec, or reference a `values.yaml` override file in a separate Git path.

**21. What are the pros and cons of storing Helm values files in the same repo vs a separate config repo?**

**Monorepo (chart + values together):**
- Pro: Single PR changes both code and config simultaneously, easy traceability
- Con: Application developers need access to deploy config; hard to separate concerns at scale

**Separate config repo:**
- Pro: Clear separation of concerns — chart authors and ops team manage different repos; deploy config changes don't trigger a full rebuild
- Con: Tracing a feature from code to deployment requires cross-repo lookups

Most mature orgs use separate repos: `app-code` triggers image builds, the image tag is pinned in `app-config` repo, ArgoCD watches `app-config`.

***

## Hard

**22. How would you implement multi-cluster fleet management with ArgoCD at a company with 200 Kubernetes clusters?**

Hub-and-spoke with ApplicationSets:

1. **Cluster registration:** Each cluster registers itself via `argocd cluster add` with environment, region, and tier labels stored in the ArgoCD cluster secret.
2. **ApplicationSet generators:** Use `cluster` generator filtered by labels to target specific tiers. Matrix generator crosses apps (from Git directory generator) × clusters (from cluster generator) automatically.
3. **Cluster fleet metadata:** Store cluster properties (team, cost-center, compliance-tier) in a Git-managed cluster registry YAML consumed by ApplicationSets as a `list` generator.
4. **Drift at scale:** Run `argocd app list --sync-status OutOfSync -o json` in a cron job to detect drift, report to Slack, and page on-call for production clusters with `SyncFailed` status.
5. **Ring-based upgrades:** Organize clusters into rings 0-3. Canary a Helm chart version to Ring 0 for 48 hours before promoting to Ring 1, using ArgoCD `helm.parameters` overrides per cluster.
6. **Scale:** ArgoCD sharding with multiple application-controller replicas to handle 200 clusters within API rate limits.

**23. How do you design a GitOps workflow for infrastructure (Terraform) alongside application manifests?**

Separate repositories or separate paths:
- `infra-gitops/` repo: Terraform modules and root modules per environment, applied by Atlantis or a CI pipeline on PR merge. Terraform writes output values (cluster endpoint, database URL) to a parameter store or Vault.
- `app-gitops/` repo: Kubernetes manifests managed by ArgoCD. ExternalSecret resources reference infrastructure outputs from Vault.

The boundary: Terraform manages infrastructure lifecycle (create/update/destroy); ArgoCD manages Kubernetes application state. Changes to infrastructure trigger downstream updates via ExternalSecrets — no manual propagation.

**24. What is the GitOps reconciliation loop and how does ArgoCD handle resource pruning?**

The reconciliation loop: ArgoCD's application-controller periodically compares desired state (rendered from Git) to live state (queried from the Kubernetes API). On divergence, it computes a diff and applies the delta.

**Pruning:** When a resource exists in the cluster but is no longer in Git, ArgoCD marks it as `extraneous`. Pruning is opt-in — `syncPolicy.syncOptions: [Prune=true]` deletes extraneous resources on sync. Without it, deleted-from-Git resources remain in the cluster. Automated sync with pruning enabled provides full GitOps: the cluster always reflects exactly what is in Git.

**25. How do you prevent configuration drift in a team where developers have kubectl access?**

1. **RBAC restriction:** Remove `kubectl apply/delete/patch` permissions from developer RBAC roles. Developers can `get`, `list`, `describe` — but not mutate production resources.
2. **ArgoCD auto-sync + self-heal:** `syncPolicy.automated.selfHeal: true` detects and reverses any direct cluster edits within seconds.
3. **Admission policy:** OPA Gatekeeper or Kyverno blocks changes to resources owned by ArgoCD (`app.kubernetes.io/managed-by: argocd`) from any source other than the ArgoCD service account.
4. **Audit logging:** Kubernetes audit logs stream to a SIEM. Direct `kubectl` mutations to production generate a PagerDuty alert.
5. **Break-glass procedure:** Emergency access via a time-limited, approval-gated role, with all actions session-recorded.

**26. How do you handle Sync Wave deadlocks in ArgoCD?**

A deadlock occurs when a PostSync hook in wave N creates a resource that wave N+1 depends on, but wave N+1 must complete for the PostSync hook to be marked successful. Diagnosis:

1. Run `argocd app get my-app --hard-refresh` and inspect the sync operation status.
2. Look for hooks stuck in `Running` or resources in `Progressing` state that cannot resolve.

Resolution strategies:
- Break the circular dependency by splitting the Application into two (one provisions the dependency, the other consumes it).
- Use `Sync` hooks instead of `PostSync` for resources that future waves depend on.
- Set `argocd.argoproj.io/hook-delete-policy: HookSucceeded` to clean up hooks so they don't block future syncs.
- Increase `timeout.reconciliation` if resources legitimately take longer to become healthy.

**27. What is ApplicationSet's Matrix generator and what are its use cases?**

The Matrix generator combines two other generators — every combination of their outputs generates one Application. Example:

```yaml
generators:
  - matrix:
      generators:
        - git:
            repoURL: https://github.com/org/apps
            directories: [{path: "apps/*"}]     # generates: frontend, backend, worker
        - clusters:
            selector:
              matchLabels:
                environment: production         # generates: us-east, eu-west, ap-south
```

This creates 9 Applications (3 apps × 3 regions). The Matrix generator is powerful for fleet-wide deployments but must be used carefully — a poorly scoped generator can accidentally create hundreds of unintended Applications.

***

### System Design Perspective

**ArgoCD reconciliation loop internals**

The application-controller runs a reconciliation loop for each Application. Loop iteration: (1) fetch desired state from repo-server (which renders manifests and caches in Redis); (2) fetch live state from Kubernetes API; (3) compute diff; (4) if OutOfSync and automated sync is enabled, apply the diff. The loop runs on a configurable interval (default: 3 minutes for refresh, immediate on Git webhook). Redis caching means the repo-server doesn't re-clone on every reconcile cycle — only on cache miss or forced refresh (`argocd app get --hard-refresh`).

**Multi-cluster scaling design**

At 200 clusters, a single application-controller becomes the bottleneck: each Application costs ~100ms of reconciliation time, and 200 clusters × 50 apps per cluster = 10,000 Applications. With one controller, full reconciliation takes ~1000 seconds. Sharding splits Applications across N controller replicas based on a consistent hash of the Application name. Each shard handles 1/N of the Applications, reducing reconciliation time proportionally. Cluster registration (cluster secrets) lives in the `argocd` namespace; adding a new cluster requires only creating the cluster secret — the ApplicationSet cluster generator discovers it automatically.

**Drift detection vs. self-healing**

Drift detection (`OutOfSync` status) is always on. Self-healing (`selfHeal: true`) is the automated response to detected drift. Without `selfHeal`, ArgoCD alerts on drift but requires a human to run `argocd app sync`. With `selfHeal`, ArgoCD corrects drift automatically within the reconciliation interval. The distinction matters for operations: `selfHeal: false` is useful during incident investigation (prevent ArgoCD from overwriting emergency changes while debugging); `selfHeal: true` is the default for steady-state production (no manual changes survive).

---
description: Medium-difficulty interview questions for ArgoCD, GitOps, and progressive delivery.
---

```
ArgoCD Medium Interview Topics
├── ApplicationSet
│   ├── Generates N Applications from one template + generator
│   ├── Generators: list | cluster | git (dirs) | git (files) | matrix | merge | pullRequest
│   └── Use case: same app to 200 clusters, or per-service monorepo, or per-PR Review App
│
├── ArgoCD vs Flux
│   ├── ArgoCD: centralized UI, Application CRD, multi-tenant Projects, GitLab integration
│   ├── Flux: modular controllers (source, kustomize, helm), no UI, lighter, per-cluster model
│   └── Flux multi-tenancy: targetNamespace + serviceAccountName per team Kustomization
│
├── Secret Management in GitOps
│   ├── Sealed Secrets: controller holds private key, developer encrypts with kubeseal
│   ├── External Secrets Operator: ExternalSecret → Vault/AWS SM/Azure KV → real Secret
│   └── SOPS + CMP: encrypted YAML in Git, CMP plugin decrypts at render time
│
├── Flagger & Progressive Delivery
│   ├── Flagger watches Deployment for new versions
│   ├── Creates canary Deployment, configures mesh VirtualService traffic split
│   ├── Queries Prometheus SLIs on configurable interval
│   └── Promotes or rolls back automatically based on metric thresholds
│
├── Progressive Delivery vs Blue-Green
│   ├── Blue-green: binary switch 0%/100% — instant, all-or-nothing
│   ├── Canary: gradual 5%→20%→50%→100% — metric-gated, lower blast radius
│   └── Traffic mirroring: copy 100% of traffic to new version without serving responses
│
├── Kustomize vs Helm in ArgoCD
│   ├── Kustomize: patch overlays, no templating, per-environment patches in overlay dirs
│   ├── Helm: Go templating, versioned charts, ArgoCD uses helm template (not helm install)
│   └── ArgoCD renders both to plain YAML before applying — same execution path
│
├── AppProject RBAC & Multi-Tenancy
│   ├── AppProject: sourceRepos + destinations + clusterResourceWhitelist
│   ├── argocd-rbac-cm: role → resource/action/object policy lines
│   └── SSO groups mapped to ArgoCD roles via argocd-cm
│
├── Helm Chart Deployments via ArgoCD
│   ├── ArgoCD renders with helm template — no helm install, no release secrets
│   ├── Values: helm.values (inline) | helm.parameters (key=value) | values file in Git
│   └── Lifecycle owned by ArgoCD: sync = apply rendered YAML
│
└── Config Repo Patterns
    ├── Monorepo: chart + values together — single PR for code + config change
    ├── Separate config repo: ops team manages config; image tag updates in config repo
    └── Mature pattern: app-code triggers image build → image tag pinned in app-config repo
```

### First Principles

- ApplicationSet is a force multiplier: one ApplicationSet definition replaces 200 individual Application manifests. The generator is the input space; the template is the Application structure. New cluster registered → new Application created automatically.
- External Secrets Operator decouples secret lifecycle from manifest lifecycle. The ExternalSecret CRD is safe to commit to Git; it contains only a reference path, not a value. The controller fetches the actual value from the secret store at runtime and rotates it on the configured interval.
- Flagger makes the deployment controller observable: it instruments the Deployment, creates a canary copy, and queries Prometheus for SLIs that define "this canary is healthy." The SLI thresholds in the Flagger CRD are the deployment acceptance criteria — auditable, versionable, reviewable in Git.
- Kustomize and Helm answer the same question (how do I deploy differently to staging vs. production?) from different philosophical positions: Kustomize applies patches (mutation-based); Helm uses templates with values (generation-based). ArgoCD is agnostic — it renders both to YAML.
- A separate config repo creates a clean separation between "what the app does" (code repo) and "how it's deployed" (config repo). The image tag update (a deployment decision) doesn't touch the application code repo.

## Medium

**7. What is an ArgoCD ApplicationSet and when would you use it?**

An ApplicationSet is a controller that generates multiple ArgoCD Applications from a single template, using generators such as List, Git, Matrix, or Cluster. Use it when deploying the same application across multiple clusters or environments without defining a separate Application resource for each. Example: a cluster generator automatically creates an Application per registered cluster, deploying a base monitoring stack to all 200 clusters.

**8. Compare ArgoCD and Flux. What are the key architectural differences?**

- **ArgoCD:** More centralized and opinionated. Has a comprehensive UI, and the `Application` CRD is the central concept. Better for multi-tenant GitOps platforms with rich self-service.
- **Flux:** More modular, following the Unix philosophy. It's a collection of specialized controllers (for sourcing from Git, applying manifests, handling Helm releases) composed together. Lighter weight, no built-in UI, better for organizations that prefer CLI- and Git-driven workflows.

**9. How do you manage secrets in a GitOps workflow where manifests are in a Git repository?**

Use Sealed Secrets or External Secrets Operator:

- **Sealed Secrets (Bitnami):** A controller in the cluster holds a private key. Developers encrypt Secrets with `kubeseal` using the controller's public key. The resulting `SealedSecret` is safe to commit. The controller decrypts it into a real Secret at apply time.
- **External Secrets Operator:** `ExternalSecret` resources reference secrets in Vault, AWS Secrets Manager, or Azure Key Vault by path. The controller fetches and syncs secret values into Kubernetes Secrets. No encrypted data stored in Git.

**10. What is Flagger and how does it enable progressive delivery on top of a service mesh?**

Flagger is a progressive delivery operator that automates canary, A/B, and blue-green deployments:

1. Flagger watches for changes to a `Deployment`.
2. When it sees a new version, it creates a canary Deployment and configures the service mesh (Istio `VirtualService`) to send a small traffic percentage to it.
3. It runs an automated analysis loop querying Prometheus SLIs.
4. If metrics are healthy, it gradually increases traffic to the canary. If not, it automatically rolls back.

**11. What is progressive delivery and how does it improve on blue-green deployments?**

Blue-green is binary: 0% or 100% traffic on the new version. Progressive delivery introduces gradual traffic shifting with automated metric-gated promotion:
- **Canary releases:** 5% → 20% → 50% → 100% with automated promotion criteria.
- **Feature flags:** Enable for 1% of users, then internal employees, then geographic regions.
- **Traffic mirroring:** Copy 100% of live traffic to the new version without serving real responses — test under production load with zero risk.

**12. What is Kustomize and how does it differ from Helm?**

Kustomize applies patch overlays to a base set of Kubernetes YAML files without templating. It uses `kustomization.yaml` to reference a base and layer environment-specific patches on top. Helm is a full package manager with Go templating, versioned charts, and a release lifecycle (`install`, `upgrade`, `rollback`). Kustomize is lighter and better for simple per-environment customization; Helm is better for distributing complex applications with many configurable parameters.

**13. How do you handle RBAC and multi-tenancy in ArgoCD?**

ArgoCD Projects (`AppProject`) define RBAC boundaries for teams:
- **Source repos:** Which Git repositories a project can deploy from.
- **Destination clusters/namespaces:** Which clusters and namespaces the project can deploy to.
- **Cluster resource whitelist:** Which cluster-scoped resources (CRDs, ClusterRoles) are allowed.

Combined with ArgoCD RBAC (`argocd-rbac-cm` ConfigMap), roles like `admin`, `readonly`, or `deploy-only` are assigned to SSO groups. A team can only see and sync their own project's applications.

**14. How does ArgoCD handle Helm chart deployments?**

ArgoCD can deploy Helm charts directly — it renders the chart with `helm template` (not `helm install`) and applies the resulting YAML. This means: ArgoCD owns the lifecycle (not Helm), release secrets are not created in the cluster, and upgrades go through ArgoCD's sync process. To pass values, use the `helm.values` or `helm.parameters` fields in the Application spec, or reference a `values.yaml` override file in a separate Git path.

**15. What are the pros and cons of storing Helm values files in the same repo vs a separate config repo?**

**Monorepo (chart + values together):**
- Pro: Single PR changes both code and config simultaneously, easy traceability
- Con: Application developers need access to deploy config; hard to separate concerns at scale

**Separate config repo:**
- Pro: Clear separation of concerns — chart authors and ops team manage different repos; deploy config changes don't trigger a full rebuild
- Con: Tracing a feature from code to deployment requires cross-repo lookups

Most mature orgs use separate repos: `app-code` triggers image builds, the image tag is pinned in `app-config` repo, ArgoCD watches `app-config`.

***

### System Design Perspective

**ApplicationSet generator safety**

The Matrix generator can create O(m×n) Applications in one operation. A `cluster` generator matching all registered clusters (200) crossed with a `git` generator matching all directories (50) creates 10,000 Applications — likely unintended. Safety practices: (1) scope cluster generators with `matchLabels` to specific tiers; (2) test generator output with `--dry-run`; (3) use the `template.metadata.labels` to tag generated Applications for easy bulk deletion if misconfigured. The ApplicationSet controller processes deletions when a generator removes an entry — Applications are deleted cascade (workloads removed from cluster) unless `preserveResourcesOnDeletion: true`.

**External Secrets Operator rotation design**

ESO's `ExternalSecret` has a `refreshInterval` field that controls how often the controller re-fetches the secret from the external store. Setting `refreshInterval: 1h` means the Kubernetes Secret is at most 1 hour stale. For rotation: update the secret in Vault/AWS SM; within `refreshInterval`, ESO creates a new version of the Kubernetes Secret. For zero-downtime rotation, applications must watch for Secret changes and reload (restarting Pods picks up the new Secret). The `reloader` sidecar pattern (Stakater Reloader) watches for Secret changes and triggers rolling restarts automatically.

**Helm values file architecture in GitOps**

Three patterns: (1) values in the Application `helm.values` inline YAML — easy but mixes config into ArgoCD CRDs; (2) values file in the same Git repo as the chart — single PR for chart + values change, but gives developers access to deploy config; (3) values file in a separate config repo referenced by `helm.valueFiles` pointing to an external file path — clean separation but requires ArgoCD to read from two repos (configure the config repo as an additional source using multi-source Applications in ArgoCD 2.6+).

---
description: Hard interview questions for ArgoCD, GitOps architecture, and fleet management at scale.
---

```
ArgoCD Hard Interview Topics
├── Multi-Cluster Fleet (200 clusters)
│   ├── Hub-and-spoke: one ArgoCD control plane, N clusters registered via cluster secrets
│   ├── Cluster labels: environment, region, tier stored in cluster secret metadata
│   ├── ApplicationSet cluster generator: filtered by labels — scoped auto-deploy
│   ├── Ring-based upgrades: Ring 0 (canary) → Ring 1 (5%) → Ring 2 (25%) → Ring 3 (all)
│   └── Controller sharding: ARGOCD_CONTROLLER_REPLICAS to distribute reconciliation
│
├── GitOps for Terraform
│   ├── Separate repos: infra-gitops (Terraform + Atlantis) and app-gitops (ArgoCD)
│   ├── Boundary: Terraform manages infrastructure lifecycle; ArgoCD manages K8s state
│   └── Integration: Terraform outputs → Vault/Parameter Store → ExternalSecret → K8s Secret
│
├── Reconciliation Loop & Pruning
│   ├── Loop: compare desired (Git) vs live (K8s API) → compute diff → apply delta
│   ├── Pruning: resource in cluster but not in Git → marked extraneous
│   ├── prune: true — deletes extraneous resources on sync (opt-in)
│   └── Without prune: deleted-from-Git resources remain in cluster indefinitely
│
├── Drift Prevention
│   ├── RBAC restriction: developers get get/list/describe, not apply/delete/patch
│   ├── selfHeal: true — detects and reverts direct cluster edits within seconds
│   ├── Admission policy: Gatekeeper/Kyverno blocks changes to ArgoCD-managed resources
│   ├── Audit logging: direct kubectl mutations → PagerDuty alert
│   └── Break-glass: time-limited approval-gated role with session recording
│
├── Sync Wave Deadlocks
│   ├── Cause: PostSync hook in wave N creates resource that wave N+1 depends on
│   ├── Diagnosis: argocd app get --hard-refresh; look for Progressing hooks
│   ├── Fix: split Application into two; use Sync hooks instead of PostSync for deps
│   └── Prevention: hook-delete-policy: HookSucceeded to clean up completed hooks
│
├── Matrix Generator
│   ├── Cross-product of two generators: apps × clusters = N*M Applications
│   ├── Example: 3 apps × 3 regions = 9 Applications in one ApplicationSet
│   └── Risk: poorly scoped generator creates hundreds of unintended Applications
│
├── GitOps Canary Without Service Mesh
│   ├── Dual-Deployment: app-stable (9 replicas) + app-canary (1 replica), shared selector
│   ├── Argo Rollouts: Rollout CRD + canary strategy + NGINX/ALB traffic routing
│   └── Flagger + NGINX: canary.nginx annotation-based traffic weight shifting
│
└── ArgoCD HA Architecture
    ├── argocd-server: 3+ replicas, stateless, horizontal load balancer
    ├── argocd-repo-server: 3+ replicas, CPU-bound, autoscale on CPU
    ├── argocd-application-controller: sharded with ARGOCD_CONTROLLER_REPLICAS
    ├── Redis: Redis Sentinel or managed Redis for HA
    └── Multi-region: ArgoCD per region, hub manages regional instances via App-of-Apps
```

### First Principles

- Multi-cluster fleet management is a fan-out problem. ApplicationSet solves it by turning "one Application definition" into "N Applications via generator." Adding a cluster to the fleet is a data operation (register cluster + add label), not a code operation (write new Application manifests).
- GitOps for Terraform draws a hard boundary: Terraform owns infrastructure lifecycle (create/destroy), ArgoCD owns Kubernetes application state. Crossing this boundary (ArgoCD deploying Terraform, or Terraform deploying K8s resources directly) creates operational complexity without corresponding benefit.
- Pruning is opt-in because the blast radius of accidental deletion is high. The GitOps contract is: when you're confident Git is the complete desired state and no controller is legitimately creating cluster-only resources, enable pruning to enforce the contract.
- Sync wave deadlocks arise from circular temporal dependencies between hooks and waves. The fix is always the same: find the cycle, break it by splitting the Application at the cycle boundary or by using a different hook phase that resolves before the dependent wave starts.
- HA ArgoCD must address four failure domains independently: API server (stateless, trivially horizontal), repo server (CPU-bound, scale on CPU), application controller (sharded, scale by controller replica count), and Redis (single point of failure without Sentinel/managed Redis).

## Hard

**16. How would you implement multi-cluster fleet management with ArgoCD at a company with 200 Kubernetes clusters?**

Hub-and-spoke with ApplicationSets:

1. **Cluster registration:** Each cluster registers itself via `argocd cluster add` with environment, region, and tier labels stored in the ArgoCD cluster secret.
2. **ApplicationSet generators:** Use `cluster` generator filtered by labels to target specific tiers. Matrix generator crosses apps (from Git directory generator) × clusters (from cluster generator) automatically.
3. **Cluster fleet metadata:** Store cluster properties (team, cost-center, compliance-tier) in a Git-managed cluster registry YAML consumed by ApplicationSets as a `list` generator.
4. **Drift at scale:** Run `argocd app list --sync-status OutOfSync -o json` in a cron job to detect drift, report to Slack, and page on-call for production clusters with `SyncFailed` status.
5. **Ring-based upgrades:** Organize clusters into rings 0-3. Canary a Helm chart version to Ring 0 for 48 hours before promoting to Ring 1, using ArgoCD `helm.parameters` overrides per cluster.
6. **Scale:** ArgoCD sharding with multiple application-controller replicas to handle 200 clusters within API rate limits.

**17. How do you design a GitOps workflow for infrastructure (Terraform) alongside application manifests?**

Separate repositories or separate paths:
- `infra-gitops/` repo: Terraform modules and root modules per environment, applied by Atlantis or a CI pipeline on PR merge. Terraform writes output values (cluster endpoint, database URL) to a parameter store or Vault.
- `app-gitops/` repo: Kubernetes manifests managed by ArgoCD. ExternalSecret resources reference infrastructure outputs from Vault.

The boundary: Terraform manages infrastructure lifecycle (create/update/destroy); ArgoCD manages Kubernetes application state. Changes to infrastructure trigger downstream updates via ExternalSecrets — no manual propagation.

**18. What is the GitOps reconciliation loop and how does ArgoCD handle resource pruning?**

The reconciliation loop: ArgoCD's application-controller periodically compares desired state (rendered from Git) to live state (queried from the Kubernetes API). On divergence, it computes a diff and applies the delta.

**Pruning:** When a resource exists in the cluster but is no longer in Git, ArgoCD marks it as `extraneous`. Pruning is opt-in — `syncPolicy.syncOptions: [Prune=true]` deletes extraneous resources on sync. Without it, deleted-from-Git resources remain in the cluster. Automated sync with pruning enabled provides full GitOps: the cluster always reflects exactly what is in Git.

**19. How do you prevent configuration drift in a team where developers have kubectl access?**

1. **RBAC restriction:** Remove `kubectl apply/delete/patch` permissions from developer RBAC roles. Developers can `get`, `list`, `describe` — but not mutate production resources.
2. **ArgoCD auto-sync + self-heal:** `syncPolicy.automated.selfHeal: true` detects and reverses any direct cluster edits within seconds.
3. **Admission policy:** OPA Gatekeeper or Kyverno blocks changes to resources owned by ArgoCD (`app.kubernetes.io/managed-by: argocd`) from any source other than the ArgoCD service account.
4. **Audit logging:** Kubernetes audit logs stream to a SIEM. Direct `kubectl` mutations to production generate a PagerDuty alert.
5. **Break-glass procedure:** Emergency access via a time-limited, approval-gated role, with all actions session-recorded.

**20. How do you handle Sync Wave deadlocks in ArgoCD?**

A deadlock occurs when a PostSync hook in wave N creates a resource that wave N+1 depends on, but wave N+1 must complete for the PostSync hook to be marked successful. Diagnosis:

1. Run `argocd app get my-app --hard-refresh` and inspect the sync operation status.
2. Look for hooks stuck in `Running` or resources in `Progressing` state that cannot resolve.

Resolution strategies:
- Break the circular dependency by splitting the Application into two (one provisions the dependency, the other consumes it).
- Use `Sync` hooks instead of `PostSync` for resources that future waves depend on.
- Set `argocd.argoproj.io/hook-delete-policy: HookSucceeded` to clean up hooks so they don't block future syncs.
- Increase `timeout.reconciliation` if resources legitimately take longer to become healthy.

**21. What is ApplicationSet's Matrix generator and what are its use cases?**

The Matrix generator combines two other generators — every combination of their outputs generates one Application. Example:

```yaml
generators:
  - matrix:
      generators:
        - git:
            repoURL: https://github.com/org/apps
            directories: [{path: "apps/*"}]     # generates: frontend, backend, worker
        - clusters:
            selector:
              matchLabels:
                environment: production         # generates: us-east, eu-west, ap-south
```

This creates 9 Applications (3 apps × 3 regions). The Matrix generator is powerful for fleet-wide deployments but must be used carefully — a poorly scoped generator can accidentally create hundreds of unintended Applications.

**22. How do you implement GitOps-native canary deployments without a service mesh?**

Without Istio/Linkerd, use Kubernetes-native approaches:

1. **Dual-Deployment canary:** Run two Deployments (`app-stable` with 9 replicas, `app-canary` with 1 replica). Both match the same Service selector via a shared label. Traffic is split 90/10 by replica count.
2. **Argo Rollouts (preferred):** Install the Argo Rollouts controller. Define a `Rollout` resource instead of a `Deployment` with `strategy.canary`. The controller manages traffic splitting via NGINX Ingress annotations or AWS ALB weighted target groups — no service mesh required.
3. **Flagger with NGINX Ingress:** Flagger supports NGINX as a traffic provider, using `canary.nginx.stable.nginx.org/weight` annotations to shift traffic percentages.

ArgoCD manages the Rollout YAML in Git; Argo Rollouts handles the progressive traffic shift and automated analysis.

**23. How would you design the ArgoCD deployment architecture for high availability?**

Production ArgoCD HA setup:

- **application-controller:** Multiple replicas with sharding (`ARGOCD_CONTROLLER_REPLICAS`). Each shard handles a subset of Applications, preventing a single controller from becoming the bottleneck at 1000+ apps.
- **argocd-server:** Stateless, horizontally scalable behind a load balancer. 3+ replicas.
- **argocd-repo-server:** Renders manifests from Git; CPU-bound for large Helm charts. 3+ replicas with CPU limits tuned.
- **Redis:** ArgoCD uses Redis for caching. Use Redis Sentinel or a managed Redis service for HA.
- **etcd (via Kubernetes):** ArgoCD state is stored in Kubernetes CRDs — inherits Kubernetes HA.
- **Multi-region:** Deploy an ArgoCD instance per region. Use `cluster` generators scoped to regional clusters. The hub ArgoCD instance manages regional instances via the App-of-Apps pattern.

***

### System Design Perspective

**Fleet upgrade ring design**

Ring 0: 1-2 non-production clusters; validate new Helm chart version for 48 hours — look for CrashLoopBackOff, failed AnalysisTemplates, and Prometheus alert spikes. Ring 1: 5% of production clusters (select by cluster label `ring: 1`); validate for 24 hours. Ring 2: 25% of production. Ring 3: all remaining. ArgoCD ApplicationSet implements rings via `helm.parameters` overrides per cluster: `image.tag: v2.1.0` in Ring 0 clusters, `image.tag: v2.0.5` in Ring 3 clusters until promoted. The promotion operation is a Git commit changing the helm parameter for the next ring's clusters — fully auditable.

**Terraform + GitOps boundary enforcement**

The anti-pattern is bidirectional coupling: ArgoCD triggering Terraform, or Terraform creating Kubernetes resources. The clean boundary: Terraform creates the Kubernetes cluster and writes output values (cluster endpoint, OIDC issuer, database URLs) to Vault or AWS Parameter Store. ArgoCD is then bootstrapped on the new cluster (via cluster registration script in CI). ExternalSecret resources in the ArgoCD Applications reference the Vault/SSM paths — the coupling is data-only, not control-plane. No ArgoCD Application ever runs `terraform apply`; no Terraform resource creates a Kubernetes Deployment.

**Admission webhook + ArgoCD conflict**

OPA Gatekeeper and Kyverno policies can conflict with ArgoCD sync if the policies reject resources that ArgoCD is trying to apply. Common failure: Gatekeeper requires all Deployments to have resource limits, but ArgoCD is trying to sync a Deployment without them — the webhook rejects the apply, ArgoCD reports SyncFailed, and the Application stays OutOfSync forever. Diagnosis: `argocd app get my-app --hard-refresh` shows SyncFailed; `kubectl describe deploy` or webhook logs show admission denial. Fix: either add resource limits to the manifest (correct fix) or add a Gatekeeper exclusion for the ArgoCD service account (workaround). The ArgoCD service account itself should be excluded from policies that target developer RBAC (e.g., "developers cannot create ClusterRoles") since ArgoCD often applies cluster-scoped resources legitimately.

---

## Hard (continued) — Argo Rollouts, ApplicationSets, Secrets & Custom Health

**Q: Explain how Argo Rollouts implements a canary deployment with automated analysis. Walk through the full lifecycle: traffic splitting, AnalysisTemplate, promotion, and rollback.**

**A:**

Argo Rollouts extends Kubernetes with a `Rollout` CRD that replaces `Deployment` for progressive delivery. A canary strategy splits traffic between a stable version and a new canary version, then uses automated analysis to decide whether to promote or abort.

**Rollout resource with canary + analysis:**

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: checkout-service
spec:
  replicas: 10
  strategy:
    canary:
      canaryService: checkout-service-canary    # separate Service for canary pods
      stableService: checkout-service-stable    # separate Service for stable pods
      trafficRouting:
        nginx:
          stableIngress: checkout-ingress       # NGINX Ingress splits traffic by weight
      steps:
      - setWeight: 10          # step 1: send 10% to canary
      - analysis:              # step 2: run analysis for 10 min at 10%
          templates:
          - templateName: success-rate
          args:
          - name: service-name
            value: checkout-service-canary
      - setWeight: 30          # step 3: if analysis passed, increase to 30%
      - pause: {duration: 5m}  # step 4: pause 5 min (optional human review gate)
      - setWeight: 60
      - setWeight: 100         # step 5: full promotion
```

**AnalysisTemplate — defines what "healthy" means:**

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: success-rate
spec:
  args:
  - name: service-name
  metrics:
  - name: success-rate
    interval: 60s          # query every 60 seconds
    count: 10              # run 10 measurements
    successCondition: result[0] >= 0.95   # 95% success rate required
    failureLimit: 2        # allow 2 failures before aborting
    provider:
      prometheus:
        address: http://prometheus:9090
        query: |
          sum(rate(http_requests_total{
            service="{{args.service-name}}",
            status=~"2.."
          }[5m])) /
          sum(rate(http_requests_total{
            service="{{args.service-name}}"
          }[5m]))
```

**Traffic splitting mechanics (NGINX):**

Argo Rollouts controller patches the Ingress resource's annotation to adjust traffic weights:
```yaml
nginx.ingress.kubernetes.io/canary: "true"
nginx.ingress.kubernetes.io/canary-weight: "10"
```

At step `setWeight: 10`, 10% of Ingress traffic is routed to `checkout-service-canary` (canary pods), 90% to `checkout-service-stable` (stable pods). The actual weight is implemented in NGINX as upstream weighted balancing.

**Full lifecycle:**

```
1. kubectl argo rollouts set image checkout-service \
       checkout-service=myrepo/checkout:v2.1.0

2. Controller creates canary ReplicaSet (1 pod = 10% of 10)
3. NGINX weight patched to 10% canary / 90% stable
4. AnalysisRun created — Prometheus queried every 60s for 10 min
5a. All 10 measurements ≥ 0.95 → analysis succeeds → setWeight: 30
5b. 3 measurements < 0.95 → analysis fails → automatic rollback:
     - canary ReplicaSet scaled to 0
     - NGINX weight reset to 0% canary / 100% stable
     - Rollout status: Degraded
6. If promotion completes: stable ReplicaSet updated to v2.1.0
   canary ReplicaSet deleted
```

**Rollback commands:**

```bash
# Manual abort (triggers rollback)
kubectl argo rollouts abort checkout-service

# Undo (jump back to previous stable)
kubectl argo rollouts undo checkout-service

# Watch rollout progress
kubectl argo rollouts get rollout checkout-service --watch
```

**Key insight for interviews:** The AnalysisTemplate is reusable across many Rollouts. Centralize metric definitions in a shared AnalysisTemplate library (e.g., `success-rate`, `p99-latency`, `error-budget-burn`). Teams reference the template by name — they don't write Prometheus queries per service.

---

**Q: Explain ArgoCD's ApplicationSet controller. Compare the cluster generator, git generator, and matrix generator. What safety measures exist to prevent mass-deleting applications?**

**A:**

The ApplicationSet controller generates multiple `Application` CRDs from a single `ApplicationSet` template, eliminating repetitive Application definitions for multi-cluster or multi-environment deployments.

**Cluster Generator — one Application per registered cluster:**

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: guestbook-all-clusters
  namespace: argocd
spec:
  generators:
  - clusters:
      selector:
        matchLabels:
          environment: production   # only production clusters
  template:
    metadata:
      name: '{{name}}-guestbook'   # {{name}} = cluster name from ArgoCD secret
    spec:
      project: default
      source:
        repoURL: https://github.com/myorg/gitops-repo
        targetRevision: HEAD
        path: apps/guestbook
      destination:
        server: '{{server}}'        # cluster API URL from ArgoCD secret
        namespace: guestbook
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
```

When a new cluster is registered in ArgoCD with label `environment: production`, the ApplicationSet controller automatically creates a new `guestbook-<cluster-name>` Application. When a cluster is removed, the Application is deleted.

**Git Generator — one Application per directory:**

```yaml
generators:
- git:
    repoURL: https://github.com/myorg/gitops-repo
    revision: HEAD
    directories:
    - path: apps/*/          # matches apps/auth/, apps/payments/, etc.
```

Each directory becomes a separate Application. Adding a new directory to the repo automatically creates a new Application — no ApplicationSet modification needed.

**Git Generator with config files:**

```yaml
generators:
- git:
    repoURL: https://github.com/myorg/gitops-repo
    revision: HEAD
    files:
    - path: "clusters/**/config.json"  # each JSON file = one Application
```

`clusters/eu-west-1/config.json`:
```json
{
  "cluster": {"name": "eu-west-1", "server": "https://k8s.eu-west-1.example.com"},
  "environment": "production",
  "region": "eu-west-1"
}
```

Template uses `{{cluster.name}}`, `{{environment}}`, `{{region}}` as variables.

**Matrix Generator — combine two generators:**

```yaml
generators:
- matrix:
    generators:
    - clusters:
        selector:
          matchLabels:
            environment: production
    - git:
        repoURL: https://github.com/myorg/gitops-repo
        revision: HEAD
        directories:
        - path: apps/*/
```

Produces: `N_clusters × M_apps` Applications. 10 clusters × 5 apps = 50 Applications from one ApplicationSet. The risk: a bad commit to the git repo (e.g., deleting an `apps/` directory) can trigger deletion of all 10 Applications for that service simultaneously.

**Safety measures against mass deletion:**

1. **`preserveResourcesOnDeletion: true`** — when an Application is deleted by the ApplicationSet controller, Kubernetes resources are NOT pruned:
```yaml
spec:
  syncPolicy:
    preserveResourcesOnDeletion: true
```

2. **`ignoreApplicationDeletion: true`** (ApplicationSet-level) — ApplicationSet controller will not delete Applications even if the generator no longer produces them. Requires manual cleanup:
```yaml
spec:
  ignoreApplicationDeletion: true
```

3. **Git branch protection** — require PR review before merging directory deletions. The ApplicationSet's git generator picks up changes only from the target revision — a PR gate prevents accidental mass-delete from reaching HEAD.

4. **Separate ApplicationSets per generator type** — don't combine cluster + git in a matrix if the git repo is high-churn. Matrix amplifies the impact of any single generator change.

5. **Dry-run / review phase in CI** — before merging, run `argocd appset generate <appset.yaml>` in CI to preview which Applications would be created/modified/deleted:
```bash
argocd appset generate applicationset.yaml
```

---

**Q: How do you manage secrets in a GitOps workflow? Compare Sealed Secrets, External Secrets Operator, and SOPS. When would you choose each?**

**A:**

In GitOps, everything is committed to Git — including secret references. But plaintext secrets in Git are a catastrophic security failure. Three patterns solve this at different layers:

**1. Sealed Secrets (Bitnami)**

Encrypts Kubernetes Secrets in-cluster using a controller-held key pair. The SealedSecret CRD is safe to commit to Git; the controller decrypts it to a regular Secret.

```bash
# Seal a secret (requires cluster connectivity)
kubectl create secret generic db-password \
  --from-literal=password=supersecret \
  --dry-run=client -o yaml | \
  kubeseal --controller-namespace sealed-secrets \
           --format yaml > db-password-sealed.yaml

# Commit db-password-sealed.yaml to Git (safe — encrypted)
```

```yaml
# db-password-sealed.yaml (in Git)
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  name: db-password
  namespace: production
spec:
  encryptedData:
    password: AgBy3i4OJSWK+PiTySYZZA==...   # asymmetrically encrypted
```

**Advantages:** Simple, no external dependency, cluster-native.
**Disadvantages:** Tied to a single cluster's key pair. Key rotation requires re-sealing all secrets. No dynamic rotation (secrets are static once sealed). Key backup is critical — lose the key, lose access to all sealed secrets.

**2. External Secrets Operator (ESO)**

Syncs secrets from an external secret store (AWS SSM, AWS Secrets Manager, HashiCorp Vault, GCP Secret Manager, Azure Key Vault) into Kubernetes Secrets. Git only contains the ExternalSecret CRD (a reference, not the value).

```yaml
# In Git — safe, no secret values
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: db-password
  namespace: production
spec:
  refreshInterval: 1h             # re-sync from source every hour
  secretStoreRef:
    name: aws-secrets-manager
    kind: ClusterSecretStore
  target:
    name: db-password             # creates this K8s Secret
  data:
  - secretKey: password           # key in K8s Secret
    remoteRef:
      key: production/db/password # path in AWS Secrets Manager
      version: AWSCURRENT
```

**SecretStore (cluster-level, references AWS):**
```yaml
apiVersion: external-secrets.io/v1beta1
kind: ClusterSecretStore
metadata:
  name: aws-secrets-manager
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-east-1
      auth:
        jwt:                        # uses IRSA / Workload Identity
          serviceAccountRef:
            name: external-secrets
            namespace: external-secrets
```

**Advantages:** Supports rotation (ESO re-syncs on `refreshInterval`). Source of truth is the external store, not Git. Multi-cluster: same secret in AWS Secrets Manager accessed from all clusters. Access controlled via IAM/Vault policies.
**Disadvantages:** Requires external secret store (operational dependency). Secret values not in Git (some teams want full auditability of secret values — use Vault audit log instead).

**3. SOPS (Mozilla)**

Encrypts secret files directly using age, PGP, or AWS KMS. The encrypted file is committed to Git. Decryption happens at deploy time (in CI or by the GitOps operator).

```bash
# Encrypt a values file with AWS KMS
sops --kms arn:aws:kms:us-east-1:123456789:key/abc-def \
     --encrypt secrets/production.yaml > secrets/production.enc.yaml

# Decrypt in CI (using IAM role)
sops --decrypt secrets/production.enc.yaml | kubectl apply -f -
```

ArgoCD integration via `argocd-vault-plugin` or Helm secrets plugin:
```yaml
# values.yaml.enc (committed to Git)
database:
  password: ENC[AES256_GCM,data:abc...==,tag:xyz==,type:str]
```

**Advantages:** Works offline — no cluster connectivity needed to seal/unseal (unlike Sealed Secrets). Supports any file format (YAML, JSON, env files). Granular: only encrypted values are opaque; keys are visible in Git.
**Disadvantages:** Decryption key access must be managed carefully. No dynamic rotation — secrets are static snapshots.

**Decision matrix:**

| Factor | Sealed Secrets | ESO | SOPS |
|--------|----------------|-----|------|
| External dependency | None | Secret store required | KMS/age key |
| Rotation support | Manual (re-seal) | Automatic (refreshInterval) | Manual |
| Multi-cluster | Hard (key per cluster) | Easy (shared store) | Easy |
| Offline use | No (needs controller) | No (needs store) | Yes |
| Secret audit trail | Git history | External store log | Git history (encrypted) |
| Setup complexity | Low | Medium | Low–Medium |
| **Best for** | Small clusters, simple secrets | Enterprise multi-cluster | Air-gapped, audit-heavy |

**Most common production pattern:** ESO for live clusters (rotation, multi-cluster), SOPS for bootstrap secrets (before the cluster or ESO is ready).

---

**Q: How does ArgoCD's health assessment system work? How do you write a custom health check for a CRD? Give an example for a database provisioning CRD.**

**A:**

ArgoCD assesses application health by evaluating each managed Kubernetes resource. Built-in health checks exist for standard resources (Deployment, StatefulSet, DaemonSet, PVC, Ingress, etc.). For CRDs, you must write Lua-based custom health checks.

**Built-in health logic (example — Deployment):**

ArgoCD considers a Deployment healthy when:
- `status.updatedReplicas == spec.replicas`
- `status.availableReplicas == spec.replicas`
- No ongoing rollout (`status.observedGeneration == metadata.generation`)

If any condition fails, the Application is `Progressing` or `Degraded`.

**Custom health check in Lua:**

Configured in `argocd-cm` ConfigMap:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-cm
  namespace: argocd
data:
  resource.customizations.health.database.mycompany.com_DatabaseCluster: |
    hs = {}
    hs.status = "Progressing"
    hs.message = "Waiting for database to be ready"
    
    if obj.status == nil then
      return hs
    end
    
    -- Check provisioning phase
    if obj.status.phase == "Failed" then
      hs.status = "Degraded"
      hs.message = obj.status.message or "Database provisioning failed"
      return hs
    end
    
    if obj.status.phase == "Ready" then
      -- Also verify all replicas are up
      if obj.status.readyReplicas ~= nil and obj.status.replicas ~= nil then
        if obj.status.readyReplicas < obj.status.replicas then
          hs.status = "Progressing"
          hs.message = string.format("Ready: %d/%d replicas", 
            obj.status.readyReplicas, obj.status.replicas)
          return hs
        end
      end
      hs.status = "Healthy"
      hs.message = "Database cluster is ready"
      return hs
    end
    
    -- All other phases (Provisioning, Configuring, etc.) = Progressing
    hs.message = string.format("Phase: %s", obj.status.phase or "Unknown")
    return hs
```

**Example DatabaseCluster CRD status:**

```yaml
status:
  phase: Ready              # or: Provisioning, Configuring, Failed
  replicas: 3
  readyReplicas: 3
  endpoint: "postgres://my-db.internal:5432"
  message: ""
```

**Health check key format:**

`resource.customizations.health.<group>_<kind>`

Where `group` uses underscores instead of dots: `database.mycompany.com` → `database_mycompany_com`.

**ignoreDifferences for CRDs:**

CRDs often have fields that change at runtime (e.g., `status`, `lastTransitionTime`) that ArgoCD shouldn't track as drift:

```yaml
spec:
  ignoreDifferences:
  - group: database.mycompany.com
    kind: DatabaseCluster
    jsonPointers:
    - /status                          # ignore status subresource
    - /metadata/resourceVersion
  - group: apps
    kind: Deployment
    jsonPointers:
    - /spec/replicas                   # ignore if HPA manages replicas
  - group: ""
    kind: Secret
    jsonPointers:
    - /data                            # ignore Secret data (managed externally by ESO)
```

**Testing custom health checks:**

```bash
# ArgoCD provides a CLI tool to test Lua scripts
argocd admin settings resource-overrides health \
  database.mycompany.com/DatabaseCluster \
  --yaml-input - <<EOF
status:
  phase: Ready
  replicas: 3
  readyReplicas: 3
EOF
# Expected output: status=Healthy
```

---

**Q: How does ArgoCD's sync wave and sync hook system work? Design a deployment ordering for: namespace → CRDs → database → application → smoke test → notification.**

**A:**

Sync waves and hooks give precise control over resource application order within a single ArgoCD sync operation.

**Sync waves (ordering by annotation):**

Resources with lower wave numbers are applied first. ArgoCD waits for all resources in wave N to be Healthy before applying wave N+1.

```yaml
# Wave -1: Namespace (must exist before everything)
apiVersion: v1
kind: Namespace
metadata:
  name: payments
  annotations:
    argocd.argoproj.io/sync-wave: "-1"

# Wave 0: CRDs (must exist before controllers that use them)
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: databaseclusters.database.mycompany.com
  annotations:
    argocd.argoproj.io/sync-wave: "0"

# Wave 1: Database
apiVersion: database.mycompany.com/v1
kind: DatabaseCluster
metadata:
  name: payments-db
  annotations:
    argocd.argoproj.io/sync-wave: "1"

# Wave 2: Application (waits for DB to be Healthy)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payments-service
  annotations:
    argocd.argoproj.io/sync-wave: "2"
```

**Sync hooks (jobs that run at specific phases):**

```yaml
# PreSync hook: run database migrations before any resource changes
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
      restartPolicy: Never
      containers:
      - name: migrate
        image: myrepo/payments:v2.1.0
        command: ["./migrate.sh"]
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-password
              key: url

# PostSync hook: smoke test after all resources are applied
apiVersion: batch/v1
kind: Job
metadata:
  name: smoke-test
  annotations:
    argocd.argoproj.io/hook: PostSync
    argocd.argoproj.io/hook-delete-policy: HookSucceeded
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: test
        image: myrepo/smoke-tests:latest
        command: ["./run-smoke-tests.sh"]
        env:
        - name: BASE_URL
          value: https://payments.example.com

# SyncFail hook: notify Slack if sync fails
apiVersion: batch/v1
kind: Job
metadata:
  name: notify-failure
  annotations:
    argocd.argoproj.io/hook: SyncFail
    argocd.argoproj.io/hook-delete-policy: HookFailed
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: notify
        image: curlimages/curl
        command:
        - sh
        - -c
        - |
          curl -X POST $SLACK_WEBHOOK \
            -d '{"text":"Sync failed for payments-service"}'
```

**Complete ordering for the interview scenario:**

```
Phase 1: PreSync hooks
  - db-migrate Job (runs migrations against current DB)

Phase 2: Sync — Wave -1
  - Namespace "payments" applied and healthy

Phase 3: Sync — Wave 0
  - DatabaseCluster CRD applied

Phase 4: Sync — Wave 1
  - DatabaseCluster "payments-db" applied → health check: wait for phase=Ready

Phase 5: Sync — Wave 2
  - Deployment "payments-service" applied → wait for availableReplicas == replicas

Phase 6: PostSync hooks
  - smoke-test Job → runs HTTP checks against the service endpoint
  → If smoke-test Job succeeds: sync completes as Healthy
  → If smoke-test Job fails: sync completes as Failed → SyncFail hook fires

Phase 7: SyncFail hook (only if any phase failed)
  - notify-failure Job → Slack alert
```

**Hook delete policies:**

| Policy | When hook resource is deleted |
|--------|-------------------------------|
| `HookSucceeded` | After the hook Job/Pod succeeds |
| `HookFailed` | After the hook Job/Pod fails |
| `BeforeHookCreation` | Before creating the hook on next sync |

Use `HookSucceeded` for migration jobs (clean up after success). Use `BeforeHookCreation` for notification jobs you want to keep for debugging.

**Sync wave deadlock — diagnosis:**

A deadlock occurs when a resource in wave N never becomes Healthy (e.g., a Deployment waiting for a Secret that is in wave N+1, or a Job that depends on an external system that hasn't been provisioned yet). ArgoCD will wait indefinitely.

Diagnosis:
```bash
argocd app get my-app --hard-refresh
# Look for resources stuck in "Progressing" with no forward movement

kubectl describe job db-migrate -n payments
# Check for ImagePullBackOff, OOM, connection refused to DB
```

Resolution: restructure wave ordering so dependencies are always in lower waves, or add a `readinessGate` to the waiting resource pointing at a ConfigMap that the dependency populates.

---

**Q: How do you implement multi-tenancy in ArgoCD? Explain AppProjects, RBAC, and namespace isolation. How do you prevent one team from accessing or modifying another team's applications?**

**A:**

ArgoCD multi-tenancy is enforced through AppProjects, RBAC policies, and namespace scoping. Without these controls, any user with ArgoCD access can sync arbitrary manifests to any cluster.

**AppProject — the tenancy boundary:**

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: payments-team
  namespace: argocd
spec:
  description: "Payments team - production and staging"
  
  # Which Git repos this project can deploy from
  sourceRepos:
  - https://github.com/myorg/payments-gitops
  - https://github.com/myorg/shared-charts   # allowed shared chart repo
  
  # Which clusters and namespaces this project can deploy to
  destinations:
  - namespace: payments-*      # wildcard: payments-prod, payments-staging
    server: https://prod-cluster.example.com
  - namespace: payments-*
    server: https://staging-cluster.example.com
  
  # Which Kubernetes resource types are allowed
  clusterResourceWhitelist: []   # no cluster-scoped resources (no ClusterRole, no CRD)
  namespaceResourceBlacklist:
  - group: ""
    kind: ResourceQuota           # team cannot modify their own quotas
  
  # Deny all capabilities by default; grant specific ones
  roles:
  - name: deploy
    description: "Can sync and create apps in this project"
    policies:
    - p, proj:payments-team:deploy, applications, create, payments-team/*, allow
    - p, proj:payments-team:deploy, applications, sync, payments-team/*, allow
    - p, proj:payments-team:deploy, applications, get, payments-team/*, allow
    groups:
    - payments-engineers   # SSO group name (from Dex/LDAP)
  
  - name: readonly
    policies:
    - p, proj:payments-team:readonly, applications, get, payments-team/*, allow
    groups:
    - payments-stakeholders
```

**Global ArgoCD RBAC (argocd-rbac-cm):**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-rbac-cm
  namespace: argocd
data:
  policy.default: role:readonly           # default: read-only for all users
  policy.csv: |
    # Platform team: full admin
    g, platform-engineers, role:admin

    # Payments team: can only act within payments-team project
    p, role:payments-deploy, applications, *, payments-team/*, allow
    p, role:payments-deploy, projects, get, payments-team, allow
    g, payments-engineers, role:payments-deploy
    
    # Security team: read-only across all
    p, role:security-readonly, applications, get, */*, allow
    g, security-team, role:security-readonly
```

**Namespace isolation in the cluster:**

AppProject alone only controls what ArgoCD will deploy — it doesn't prevent an attacker who already has `kubectl` access from deploying to other namespaces. Enforce at the Kubernetes RBAC layer:

```yaml
# payments-engineers can only manage resources in payments-* namespaces
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: payments-team-binding
  namespace: payments-prod
subjects:
- kind: Group
  name: payments-engineers
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: edit               # can create/update/delete pods, services, etc.
  apiGroup: rbac.authorization.k8s.io
```

```yaml
# NetworkPolicy: payments pods cannot communicate with auth pods
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: isolate-payments
  namespace: payments-prod
spec:
  podSelector: {}   # applies to all pods in namespace
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          team: payments   # only allow ingress from payments namespaces
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          team: payments
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: kube-system  # DNS
```

**Preventing cross-project Application creation:**

An ArgoCD user with create permission on their project can only create Applications within that project. The AppProject's `destinations` field enforces where those Applications can deploy — a payments-team member cannot create an Application targeting `auth-*` namespaces.

**Audit and observability:**

```bash
# ArgoCD audit log — who synced what
kubectl logs -n argocd -l app.kubernetes.io/name=argocd-server | \
  grep '"action":"sync"' | jq '{user: .user, app: .app, project: .proj}'

# List all apps a specific project owns
argocd app list --project payments-team
```

**vCluster for stronger isolation:**

For teams requiring full cluster-admin within their tenant (custom CRDs, ClusterRoles), deploy virtual clusters (vCluster) instead of namespace-based isolation. Each team gets a dedicated vCluster with full control, while the host cluster admin retains control of the underlying nodes. ArgoCD manages vCluster-scoped Applications through a separate ArgoCD instance or cluster secret pointing to the vCluster API server.
