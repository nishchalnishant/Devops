## Medium

**17. How does the Kubernetes scheduler decide where to place a Pod?**

Two phases:
1. **Filtering:** Removes nodes that don't meet Pod requirements — insufficient CPU/memory, node selectors, affinity/anti-affinity rules, taints the Pod can't tolerate.
2. **Scoring:** Ranks remaining nodes using priority functions — spreads Pods across nodes, prefers nodes with the image already pulled, respects topology spread. Node with the highest score is chosen.

**18. What are Kubernetes Quality of Service (QoS) classes?**

- **Guaranteed:** All containers have `requests == limits` for CPU and memory. Last to be evicted.
- **Burstable:** At least one container has `requests < limits`. Evicted after BestEffort.
- **BestEffort:** No requests or limits set. First to be evicted under node pressure.

**19. What is a ResourceQuota and a LimitRange?**

`ResourceQuota` caps the total resources (CPU, memory, object count) that can be consumed in a namespace. `LimitRange` sets default requests and limits for containers that don't specify them, and enforces min/max bounds.

**20. How do you implement multi-tenancy in Kubernetes for 100 teams without cluster-admin?**

- Namespace per team with RBAC `Role` + `RoleBinding` (full control within namespace, nothing cluster-wide).
- `ResourceQuota` per namespace caps total CPU, memory, and object counts.
- Default-deny `NetworkPolicy` in each namespace with explicit allow rules.
- Gatekeeper (OPA) enforces: no `hostNetwork`, no `privileged`, required labels, approved registries only.
- Hierarchical Namespace Controller (HNC) for teams with sub-teams.
- Kubecost for automatic cost attribution by namespace/team.

**21. What is the Cluster Autoscaler and how does it decide to scale down?**

Cluster Autoscaler scales node groups based on pending Pods (scale up) and underutilized nodes (scale down). Scale-down eligibility: all Pods on the node can be rescheduled elsewhere, the node has been underutilized (sum of pod requests < 50% of capacity) for `scale-down-unneeded-time` (default 10 min). Blockers: Pods with no controller owner, local storage Pods, DaemonSet Pods, or Pods that would violate a PodDisruptionBudget.

**22. What is a Custom Resource Definition (CRD) and how does the Operator pattern work?**

A CRD extends the Kubernetes API with a custom resource type (e.g., `PostgresCluster`). An Operator is a custom controller that watches for instances of that CRD and reconciles the actual state to the desired state — provisioning StatefulSets, Secrets, Services, and performing operational tasks (backups, upgrades) that a human DBA would otherwise do manually.

**23. What is a NetworkPolicy and how does a default-deny policy work?**

A NetworkPolicy is a namespace-scoped resource defining allowed Pod traffic. A default-deny policy with an empty `podSelector` and no `ingress`/`egress` rules denies all traffic to/from every Pod in the namespace:

```yaml
kind: NetworkPolicy
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
```

Subsequent NetworkPolicy rules add explicit allows on top of this deny baseline.

**24. What is Vertical Pod Autoscaler (VPA) and what are its limitations?**

VPA automatically adjusts CPU and memory requests/limits based on observed usage history. Modes: `Off` (recommendations only), `Initial` (sets at pod creation), `Auto` (evicts and recreates pods to apply new recommendations). Limitations:
- Evicts pods to apply changes — causes downtime on single-replica Deployments.
- Cannot run simultaneously with HPA on CPU — they conflict.
- Needs days of usage data before recommendations stabilize.

**25. How does topology-aware volume provisioning work?**

When a Pod needs a new PV, the scheduler delays binding until the CSI driver provisions the volume. The CSI driver reports which availability zones the volume is accessible from; the scheduler places the Pod only on nodes in those zones. This prevents the classic problem of a Pod scheduled to Zone A while its EBS volume is in Zone B.

---

