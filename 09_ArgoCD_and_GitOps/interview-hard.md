---
description: Hard interview questions for ArgoCD, GitOps architecture, and fleet management at scale.
---

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
