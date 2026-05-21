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
