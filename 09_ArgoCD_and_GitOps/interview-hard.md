## Hard

**13. How would you implement multi-cluster fleet management with ArgoCD at a company with 200 Kubernetes clusters?**

Hub-and-spoke with ApplicationSets:

1. **Cluster registration:** Each cluster registers itself via `argocd cluster add` with environment, region, and tier labels stored in the ArgoCD cluster secret.
2. **ApplicationSet generators:** Use `cluster` generator filtered by labels to target specific tiers. Matrix generator crosses apps (from Git directory generator) × clusters (from cluster generator) automatically.
3. **Cluster fleet metadata:** Store cluster properties (team, cost-center, compliance-tier) in a Git-managed cluster registry YAML consumed by ApplicationSets as a `list` generator.
4. **Drift at scale:** Run `argocd app list --sync-status OutOfSync -o json` in a cron job to detect drift, report to Slack, and page on-call for production clusters with `SyncFailed` status.
5. **Ring-based upgrades:** Organize clusters into rings 0-3. Canary a Helm chart version to Ring 0 for 48 hours before promoting to Ring 1, using ArgoCD `helm.parameters` overrides per cluster.
6. **Scale:** ArgoCD sharding with multiple application-controller replicas to handle 200 clusters within API rate limits.

**14. How do you design a GitOps workflow for infrastructure (Terraform) alongside application manifests?**

Separate repositories or separate paths:
- `infra-gitops/` repo: Terraform modules and root modules per environment, applied by Atlantis or a CI pipeline on PR merge. Terraform writes output values (cluster endpoint, database URL) to a parameter store or Vault.
- `app-gitops/` repo: Kubernetes manifests managed by ArgoCD. ExternalSecret resources reference infrastructure outputs from Vault.

The boundary: Terraform manages infrastructure lifecycle (create/update/destroy); ArgoCD manages Kubernetes application state. Changes to infrastructure trigger downstream updates via ExternalSecrets — no manual propagation.

**15. What is the GitOps reconciliation loop and how does ArgoCD handle resource pruning?**

The reconciliation loop: ArgoCD's application-controller periodically compares desired state (rendered from Git) to live state (queried from the Kubernetes API). On divergence, it computes a diff and applies the delta.

**Pruning:** When a resource exists in the cluster but is no longer in Git, ArgoCD marks it as `extraneous`. Pruning is opt-in — `syncPolicy.syncOptions: [Prune=true]` deletes extraneous resources on sync. Without it, deleted-from-Git resources remain in the cluster. Automated sync with pruning enabled provides full GitOps: the cluster always reflects exactly what is in Git.

**16. How do you prevent configuration drift in a team where developers have kubectl access?**

1. **RBAC restriction:** Remove `kubectl apply/delete/patch` permissions from developer RBAC roles. Developers can `get`, `list`, `describe` — but not mutate production resources.
2. **ArgoCD auto-sync + self-heal:** `syncPolicy.automated.selfHeal: true` detects and reverses any direct cluster edits within seconds.
3. **Admission policy:** OPA Gatekeeper or Kyverno blocks changes to resources owned by ArgoCD (`app.kubernetes.io/managed-by: argocd`) from any source other than the ArgoCD service account.
4. **Audit logging:** Kubernetes audit logs stream to a SIEM. Direct `kubectl` mutations to production generate a PagerDuty alert.
5. **Break-glass procedure:** Emergency access via a time-limited, approval-gated role, with all actions session-recorded.
