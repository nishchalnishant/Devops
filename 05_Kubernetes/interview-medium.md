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

**Q: Explain how Horizontal Pod Autoscaler calculates the desired replica count.**

The HPA controller runs a control loop (default every 15s). For CPU:
```
desiredReplicas = ceil(currentReplicas × (currentMetricValue / desiredMetricValue))
```
Example: 3 replicas at 90% CPU average, target 50% → `ceil(3 × 90/50)` = `ceil(5.4)` = 6 replicas.

Scale-up: immediate if metric exceeds target. Scale-down: default 5-minute stabilization window to prevent flapping (`--horizontal-pod-autoscaler-downscale-stabilization`). HPA v2 supports custom metrics (Prometheus via custom metrics API) and external metrics. It cannot scale below `minReplicas` or above `maxReplicas`. HPA and VPA should not target the same resource (conflicts on CPU/memory — use VPA in Off or Initial mode with HPA for custom metrics).

**Q: What is RBAC aggregation and when would you use it?**

ClusterRole aggregation uses label selectors to combine multiple ClusterRoles into one automatically. The aggregated ClusterRole grows as new ClusterRoles with matching labels are created. Built-in example: `admin`, `edit`, `view` roles are aggregated — CRD operators that add new resources create ClusterRoles labeled `rbac.authorization.k8s.io/aggregate-to-view: "true"` so view users automatically get read access to the new resource without manual role updates. Use it when you have many CRD-based operators each needing their own RBAC and want the built-in roles to auto-extend.

**Q: What is the difference between an init container, a sidecar container, and an ephemeral container?**

`Init containers`: run sequentially before app containers, must complete successfully. Used for: waiting for dependencies, running migrations, seeding shared volumes. Each has its own image and resource limits.

`Sidecar containers` (KEP-753, GA in 1.29): declared in `initContainers` with `restartPolicy: Always`. They start with init containers but continue running alongside app containers. Used for: log shipping, service mesh proxies (Envoy/Linkerd), secrets rotation. Unlike init containers, they don't block app startup after they're ready.

`Ephemeral containers`: injected into a running pod post-hoc via `kubectl debug`. They cannot have ports, probes, or resource requests. Used exclusively for debugging distroless/scratch images that lack shells. They share the pod's network and PID namespaces.

**Q: What is a PodDisruptionBudget and why is it critical for zero-downtime maintenance?**

A PDB defines the minimum available (`minAvailable`) or maximum unavailable (`maxUnavailable`) Pods during voluntary disruptions (drain, cluster upgrades, eviction). Example: `minAvailable: 2` for a 3-replica Deployment means only 1 can be evicted at a time. Cluster operations check PDBs via the Eviction API before proceeding — if evicting a pod would violate the PDB, the eviction is rejected (429). This protects against accidentally taking down quorum of a 3-node database or all replicas of a critical service. PDBs do NOT protect against involuntary disruptions (node failure, OOMKill).

**Q: Explain how admission webhooks work in Kubernetes.**

Admission webhooks intercept API server requests after authentication/authorization but before persistence. Two types:

1. `MutatingAdmissionWebhook`: can modify objects (inject sidecars, set defaults, add labels)
2. `ValidatingAdmissionWebhook`: can accept or reject (enforce policies, validate resource limits)

Flow: `kubectl apply` → authn → authz → mutation webhooks (in parallel) → object schema validation → validation webhooks (in parallel) → etcd write.

Webhooks are HTTP servers registered via `MutatingWebhookConfiguration`/`ValidatingWebhookConfiguration`. They receive an `AdmissionReview` JSON and return `allowed: true/false` plus optional patches. Failures: `failurePolicy: Fail` (rejects if webhook unreachable) vs `Ignore` (allows through if webhook unreachable). Critical: webhook servers must be HA and exempt from their own webhook (or you get a deadlock).

**Q: How does a headless Service enable StatefulSet Pod DNS?**

A headless Service has `clusterIP: None`. Instead of a single virtual IP, CoreDNS creates individual A records for each ready endpoint: `<pod-name>.<service-name>.<namespace>.svc.cluster.local`. For StatefulSets, this gives each Pod a stable, predictable DNS name (e.g., `mysql-0.mysql.default.svc.cluster.local`, `mysql-1.mysql.default.svc.cluster.local`). This is how clients can target specific replicas (primary vs replica in a Galera cluster) or how Pods discover peers (Elasticsearch cluster formation). The Pod name is stable because StatefulSets use ordinal indices, not random suffixes.

**Q: What is the difference between Helm and Kustomize?**

`Helm`: templating engine + package manager. Charts are parameterized YAML templates with `values.yaml`. Supports: hooks (pre/post install), chart dependencies, versioned releases tracked in a Secret. Con: Go template syntax is complex; YAML inside templates is fragile.

`Kustomize`: overlay/patch system built into kubectl (`kubectl apply -k`). No templating — patches are applied on top of base YAML using strategic merge patches or JSON patches. Pro: base YAML is always valid Kubernetes YAML. Con: no package registry, no hooks, complex transformations require multiple patches.

Choice: Helm for distributing software to others (operator charts, vendor software). Kustomize for managing environment-specific overlays (dev/staging/prod) on your own configs. Many teams use both: Helm charts + Kustomize overlays.

**Q: Explain topology spread constraints and when you'd use them over pod anti-affinity.**

Topology spread constraints distribute Pods across topology domains (zones, nodes, racks) with fine-grained control:

```yaml
topologySpreadConstraints:
- maxSkew: 1
  topologyKey: topology.kubernetes.io/zone
  whenUnsatisfiable: DoNotSchedule
  labelSelector:
    matchLabels: {app: web}
```

`maxSkew` = maximum allowed difference in pod count between any two domains. `DoNotSchedule` (hard) vs `ScheduleAnyway` (soft).

Advantages over pod anti-affinity:
- Works correctly with dynamic node counts (anti-affinity with `requiredDuringScheduling` can block pods when a zone has fewer nodes)
- Supports multiple topology levels simultaneously
- MinDomains field ensures spread across a minimum number of zones

Use when: zone-aware HA for stateless services, rack-aware distribution in bare metal clusters.

**Q: What is CoreDNS ndots and how does it cause DNS lookup latency?**

`ndots:5` (default Kubernetes Pod resolv.conf) means: if a hostname has fewer than 5 dots, try appending search domains before trying it as-is. Search path: `<namespace>.svc.cluster.local`, `svc.cluster.local`, `cluster.local`, then bare hostname.

Problem: querying `api.example.com` (3 dots) triggers 4 failed lookups before the correct one:
1. `api.example.com.<namespace>.svc.cluster.local` → NXDOMAIN
2. `api.example.com.svc.cluster.local` → NXDOMAIN
3. `api.example.com.cluster.local` → NXDOMAIN
4. `api.example.com` → success

Fix: use FQDN with trailing dot (`api.example.com.`) to bypass search domains. Or reduce `ndots: 1` in Pod dnsConfig for services that primarily call external APIs. Or use `dnsPolicy: None` with custom dnsConfig.

**Q: What is a node's eviction threshold and how does it relate to QoS classes?**

The kubelet evicts Pods when node resources are under pressure (memory, disk). Eviction order follows QoS class:

1. `BestEffort` — no `requests` or `limits` set. Evicted first.
2. `Burstable` — `requests` set but not equal to `limits`, OR only one of them set. Evicted by usage above request.
3. `Guaranteed` — `requests` == `limits` for ALL containers (CPU and memory). Evicted last, only when node is critically low.

Hard eviction: immediate pod termination (e.g., memory < 100Mi). Soft eviction: grace period before eviction (e.g., memory < 200Mi for 2 minutes). Eviction manager first tries BestEffort pods, then Burstable pods with highest usage-above-request ratio. OOMKill is different — it's the kernel killing a process, not the kubelet evicting a pod — but kubelet restarts the container afterward.

**Q: What is EndpointSlice and how does it improve on Endpoints?**

The original `Endpoints` object stored all Pod IPs for a Service in a single object — at 1000 pods, this is a 200KB+ object that every kube-proxy instance must download completely on every change. `EndpointSlices` shard endpoints into chunks of 100 (configurable). Benefits:

- Incremental updates: only changed slices are distributed
- Scales to tens of thousands of endpoints
- Richer metadata: topology hints for traffic locality, serving/terminating states, dual-stack addresses

kube-proxy switched to EndpointSlice controller by default in 1.21. Services still have an Endpoints object for backwards compatibility, but it's now maintained as a mirror by a separate controller.

**Q: Explain Kubernetes finalizers and their role in garbage collection.**

Finalizers are keys in `metadata.finalizers` that block object deletion. When you DELETE an object with finalizers, Kubernetes sets `deletionTimestamp` but doesn't remove the object. The controller responsible for that finalizer does cleanup work, then removes its finalizer key via a PATCH. When all finalizers are removed, Kubernetes deletes the object.

Common use cases: `kubernetes.io/pvc-protection` (prevents deleting PVCs while in use by Pods), CSI volume finalizers (ensures cloud volume is deleted), custom operators (ensures dependent external resources are cleaned up before the CR is removed).

Owner references + garbage collection: setting `ownerReferences` on an object means it gets garbage collected when the owner is deleted. This is how ReplicaSets clean up Pods, and how StatefulSets clean up PVCs via cascade deletion.

**Q: What is the difference between `kubectl apply` and `kubectl create`?**

`kubectl create`: imperative, creates only — fails if resource exists. `kubectl apply`: declarative, creates or updates using server-side or client-side apply logic. Client-side apply stores the "last applied configuration" in `kubectl.kubernetes.io/last-applied-configuration` annotation and computes a three-way merge (last applied + current state + new config) to determine what to patch. Server-side apply (SSA, `--server-side`): the server computes the merge and tracks field ownership — multiple managers can own different fields of the same object without stepping on each other. Recommended for GitOps and operator-managed resources.

**Q: How do you perform a blue-green deployment in Kubernetes without a service mesh?**

Blue-green using Service label switching:
1. Deploy "green" Deployment alongside running "blue" Deployment
2. Both share the same labels structure but use different version labels (e.g., `version: blue`, `version: green`)
3. Service selector currently points to `version: blue`
4. Validate green is healthy
5. `kubectl patch svc <name> -p '{"spec":{"selector":{"version":"green"}}}'` — atomic cutover
6. Keep blue running for instant rollback; delete after confidence period

Limitation: no traffic splitting, no gradual shift. For that, use Ingress weights (NGINX annotation), Argo Rollouts, or a service mesh. This approach requires the Service to not have both blue and green in its selector simultaneously.

