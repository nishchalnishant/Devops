---
description: Easy, Medium, and Hard interview questions for ArgoCD, GitOps, and progressive delivery.
---

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
