# Kubernetes — Interview Prep

```
Kubernetes Easy Interview Questions
├── Core Concepts
│   ├── What is Kubernetes? — container orchestration; scheduling, self-healing, scaling
│   ├── Pod — smallest unit; shared network namespace + IP + storage
│   ├── Deployment — manages ReplicaSets; rolling updates; rollback via revision history
│   ├── Service — stable DNS/VIP for ephemeral pod IPs
│   │   ├── ClusterIP (internal)
│   │   ├── NodePort (per-node port 30000-32767)
│   │   ├── LoadBalancer (cloud LB + external IP)
│   │   └── ExternalName (DNS alias, no proxy)
│   └── Namespace — virtual cluster; scopes names, RBAC, NetworkPolicy
├── Configuration & Storage
│   ├── ConfigMap vs Secret — non-sensitive vs sensitive data; base64 ≠ encryption
│   │   ├── Injection: envFrom, env.valueFrom, or volumeMount
│   │   └── Volume mount: supports live refresh; env vars require pod restart
│   ├── PersistentVolume (PV) — cluster storage resource
│   ├── PersistentVolumeClaim (PVC) — pod's storage request; binds to matching PV
│   └── Access modes: RWO / ROX / RWX
├── Workload Controllers
│   ├── DaemonSet — one pod per node; log agents, monitoring, CNI plugins
│   ├── StatefulSet — ordered names, stable net IDs, per-pod PVCs; for databases
│   ├── Job — run-to-completion; completions / parallelism / backoffLimit
│   └── CronJob — scheduled Jobs; concurrencyPolicy (Allow/Forbid/Replace)
├── Scheduling & Operations
│   ├── Taints — repel pods from nodes; NoSchedule / PreferNoSchedule / NoExecute
│   ├── Tolerations — allow pods onto tainted nodes
│   ├── kubectl apply vs create — idempotent (apply) vs fails-if-exists (create)
│   └── kubectl drain — cordon node + evict pods via Eviction API (respects PDBs)
├── Observability & Probes
│   ├── Liveness probe — failure → container restart (for deadlocks)
│   ├── Readiness probe — failure → remove from Service endpoints (no restart)
│   └── kubectl get events — first stop for Pending/CrashLoopBackOff/ImagePullBackOff
├── Identity & Access
│   ├── ServiceAccount — in-cluster pod identity; JWT auto-mounted token
│   └── Helm — K8s package manager; Charts + values.yaml for templated releases
└── Networking
    ├── Ingress — L7 HTTP routing rules; requires Ingress Controller
    ├── Labels — selectable key-value pairs; used by Services, Deployments, NetPol
    ├── Annotations — non-selectable metadata; arbitrary strings
    └── port-forward — local tunnel to pod port for debugging (no external exposure)
```

### First Principles

- You have many containers to run — you need a **scheduler** to place them on available machines.
- Machines fail — you need **automatic restart and rescheduling** (controller manager's reconciliation loop).
- Traffic must reach containers wherever they run — you need a **Service abstraction** (stable DNS + VIP).
- Config and secrets must not be baked into images — **externalise them** (ConfigMap / Secret).
- You need zero-downtime rollouts — **Deployment** with declarative desired state drives rolling updates; revision history enables instant rollback.

## Easy

**1. What is Kubernetes and what problem does it solve?**

Kubernetes is a container orchestration platform that automates deployment, scaling, self-healing, and management of containerized workloads across a cluster of machines.

**2. What is a Pod?**

A Pod is the smallest deployable unit in Kubernetes — it wraps one or more containers that share the same network namespace, IP address, and storage volumes.

**3. What is a Deployment?**

A Deployment manages a ReplicaSet and provides declarative updates, rolling upgrades, and rollback for a set of identical Pods.

**4. What is a Service and why is it needed?**

A Service provides a stable DNS name and IP address for a set of Pods (selected via labels). Pods are ephemeral and change IPs on restart — a Service decouples the consumer from the actual Pod IPs.

**5. What are the types of Kubernetes Services?**

- `ClusterIP`: internal-only, accessible within the cluster.
- `NodePort`: exposes the service on a port of every node.
- `LoadBalancer`: provisions a cloud load balancer with an external IP.
- `ExternalName`: maps the service to an external DNS name.

**6. What is a Namespace?**

A namespace is a virtual cluster within a Kubernetes cluster — it provides scope for names and allows resource isolation between teams or environments.

**7. What is a ConfigMap vs. a Secret?**

ConfigMap stores non-sensitive configuration as key-value pairs. Secret stores sensitive data (passwords, tokens) encoded in base64. Secrets can be mounted as volumes or injected as environment variables; they can be sealed and access-controlled with RBAC.

**8. What is `kubectl apply` vs. `kubectl create`?**

`kubectl create` creates a resource — fails if it already exists. `kubectl apply` creates or updates a resource using server-side merge — idempotent, preferred for GitOps and automation.

**9. What is a liveness probe vs. a readiness probe?**

- **Liveness probe:** Checks if the container is alive. If it fails, Kubernetes restarts the container.
- **Readiness probe:** Checks if the container is ready to serve traffic. If it fails, the container is removed from the Service's endpoints but not restarted.

**10. What is a DaemonSet?**

A DaemonSet ensures that exactly one Pod runs on every node (or a subset). Used for node-level agents like log collectors (Fluent Bit), monitoring agents (Datadog), or CNI plugins.

**11. What is a StatefulSet and when do you use it?**

A StatefulSet manages stateful applications — it provides stable, ordered Pod names (pod-0, pod-1), persistent volume claims per Pod, and ordered startup/shutdown. Used for databases, Kafka, Zookeeper.

**12. What is a PersistentVolume (PV) and PersistentVolumeClaim (PVC)?**

A PV is a piece of storage provisioned in the cluster. A PVC is a request for storage by a Pod. Kubernetes binds a PVC to a matching PV based on size and access modes.

**13. What is Helm and what problem does it solve?**

Helm is a package manager for Kubernetes. It bundles Kubernetes manifests into reusable Charts with templating, versioning, and release management. `helm install` and `helm upgrade` manage the full lifecycle of an application deployment.

**14. What is a Helm values file?**

A `values.yaml` file provides default configuration for a Helm Chart. Users can override values with `helm install --set key=value` or `-f custom-values.yaml` without modifying the chart templates.

**15. What is a Node taint and what is a toleration?**

A taint on a node repels Pods that don't explicitly tolerate it. A toleration in a Pod spec allows it to be scheduled on nodes with matching taints. Used to dedicate nodes for specific workloads (e.g., GPU nodes only for ML workloads).

**16. What is `kubectl port-forward` used for?**

It creates a tunnel from your local machine's port to a port on a Pod, allowing local access to a service running inside the cluster without exposing it externally. Used for debugging.

***

**Q: What is the role of the kubelet?**

The kubelet is the node agent that runs on every worker node. It watches the API server for Pods scheduled to its node, instructs the container runtime (via CRI) to start/stop containers, reports node and pod status back to the control plane, and executes liveness/readiness/startup probes. It does NOT manage containers it didn't create via the API server (static pods are an exception).

**Q: What is a ServiceAccount and why would a Pod need one?**

A ServiceAccount provides a Pod with an identity within the cluster. The API server automatically mounts a JWT token into Pods at `/var/run/secrets/kubernetes.io/serviceaccount/token`. Pods use this token to authenticate with the API server when making in-cluster API calls (e.g., an operator reading CRDs, Prometheus scraping the metrics API). Best practice: create dedicated ServiceAccounts per workload rather than using `default`.

**Q: What is the difference between a Job and a CronJob?**

A Job creates one or more Pods and ensures a specified number complete successfully. It's for one-shot tasks (database migrations, batch processing). A CronJob creates Jobs on a schedule (cron syntax). Key Job parameters: `completions` (total successful pods needed), `parallelism` (concurrent pods), `backoffLimit` (retry limit), `activeDeadlineSeconds` (global timeout). CronJob adds `schedule`, `concurrencyPolicy` (Allow/Forbid/Replace), `startingDeadlineSeconds`.

**Q: What are the phases of a Pod's lifecycle?**

`Pending` → scheduler hasn't placed it or images are pulling. `Running` → at least one container is running. `Succeeded` → all containers exited 0 (terminal, for Jobs). `Failed` → all containers exited and at least one exited non-zero (terminal). `Unknown` → API server can't reach the node. Within Running, individual containers have states: Waiting, Running, Terminated.

**Q: How do you pass configuration to a Pod from a ConfigMap?**

Three methods: (1) `envFrom: configMapRef` — inject all keys as env vars. (2) `env.valueFrom.configMapKeyRef` — inject a single key as a named env var. (3) `volumes.configMap` + `volumeMounts` — mount as files in a directory. File mounts support live updates (kubelet syncs changes within the `syncPeriod`, typically 60s); env vars do not — the pod must restart to pick up new values.

**Q: What is the difference between a Secret and a ConfigMap?**

Both store key-value data, but Secrets are base64-encoded and intended for sensitive data (passwords, tokens, TLS certs). base64 is NOT encryption — Secrets are stored in etcd in plaintext by default unless encryption at rest is configured. Kubernetes RBAC can limit Secret access separately from ConfigMap access. Secrets support types (`Opaque`, `kubernetes.io/tls`, `kubernetes.io/dockerconfigjson`, etc.) that trigger validation.

**Q: What is an Ingress and what does an Ingress Controller do?**

An Ingress is a Kubernetes API object that defines HTTP/HTTPS routing rules (host-based and path-based) to backend Services. An Ingress Controller is a separate deployment (NGINX, Traefik, HAProxy, AWS ALB, etc.) that watches Ingress objects and programs an actual reverse proxy. Without a controller, Ingress objects do nothing. One cluster typically has one controller but can have multiple using `IngressClass`.

**Q: What is the difference between a label and an annotation?**

Labels are key-value pairs used for selection and grouping — Services, Deployments, and NetworkPolicies use label selectors to target Pods. Annotations are key-value pairs for non-identifying metadata (build info, tool config, human notes). Annotations cannot be used in selectors. Labels have strict syntax constraints; annotation values can be arbitrary strings (including JSON blobs).

**Q: What happens when you run `kubectl drain <node>`?**

`kubectl drain` does two things: (1) cordons the node (marks it `SchedulingDisabled` so no new Pods are scheduled there), (2) evicts all non-DaemonSet Pods from the node via the Eviction API, respecting PodDisruptionBudgets. If a Pod has no controller, drain fails by default (use `--force` to delete it). Use before maintenance to safely empty a node. After maintenance, `kubectl uncordon <node>` re-enables scheduling.

**Q: What is a PersistentVolumeClaim (PVC) and how does it relate to a PersistentVolume (PV)?**

A PV is a cluster-level storage resource provisioned by an admin or dynamically by a StorageClass. A PVC is a namespace-level request for storage (size, access mode, StorageClass). Kubernetes binds a PVC to a matching PV. Pods mount PVCs. This decouples "I need 10Gi RWO storage" (PVC) from "here is an AWS EBS volume" (PV). Dynamic provisioning: if a StorageClass has a provisioner, creating a PVC auto-creates a PV.

**Q: What are the three PersistentVolume access modes?**

`ReadWriteOnce (RWO)` — mounted read-write by a single node (most block storage: EBS, Azure Disk). `ReadOnlyMany (ROX)` — mounted read-only by many nodes simultaneously. `ReadWriteMany (RWX)` — mounted read-write by many nodes simultaneously (requires network storage: NFS, CephFS, EFS, Azure Files). Note: access modes are enforced by Kubernetes scheduling/binding, not the underlying storage.

**Q: How does `kubectl rollout undo` work?**

It rolls back a Deployment to the previous revision. Kubernetes stores Deployment revision history in ReplicaSets (controlled by `revisionHistoryLimit`, default 10). `kubectl rollout history deployment/<name>` lists revisions. `kubectl rollout undo deployment/<name> --to-revision=3` rolls back to a specific revision. Under the hood, it scales up the old ReplicaSet and scales down the current one using the same rolling update strategy.

**Q: What is the difference between `kubectl delete pod` and eviction?**

`kubectl delete pod` sends a DELETE request to the API server, which sets a deletion timestamp and gives the pod `terminationGracePeriodSeconds` to shut down gracefully (SIGTERM, then SIGKILL). The eviction API (used by drain, the node's eviction manager, and cluster autoscaler) is a separate sub-resource that respects PodDisruptionBudgets before proceeding — a DELETE does not check PDBs.

**Q: What is a namespace and what does it scope?**

Namespaces provide a virtual cluster within a physical cluster for multi-team isolation. They scope: most API resources (Pods, Services, Deployments, ConfigMaps, Secrets, PVCs, ServiceAccounts, Roles, RoleBindings). Cluster-scoped resources are NOT namespaced: Nodes, PersistentVolumes, StorageClasses, ClusterRoles, ClusterRoleBindings, Namespaces themselves. NetworkPolicies and RBAC are namespace-scoped, making namespaces the primary isolation boundary.

**Q: What is the purpose of `kubectl get events --sort-by='.lastTimestamp'`?**

Events are the first thing to check when a Pod is stuck in Pending/CrashLoopBackOff/ImagePullBackOff. They record: scheduler decisions ("Insufficient cpu"), image pull failures, probe failures, OOMKills, volume mount errors. Events are namespaced, short-lived (1 hour TTL by default), and aggregated (count + lastTimestamp). Always check `kubectl describe pod <name>` which surfaces events inline.


```
Kubernetes Medium Interview Questions
├── Scheduling & Placement
│   ├── Scheduler two-phase: Filter (predicates) → Score (priorities)
│   │   ├── Filter: CPU/RAM, taints, nodeSelector, affinity, port conflicts, PVC zone
│   │   └── Score: LeastAllocated, NodeAffinity, ImageLocality, TopologySpread
│   ├── Taints (NoSchedule / PreferNoSchedule / NoExecute) + Tolerations
│   ├── Node Affinity (hard/soft) — requires or prefers node labels
│   ├── Pod Anti-Affinity — spread replicas across nodes/zones (HA)
│   └── Topology Spread Constraints — maxSkew across zones
├── Autoscaling
│   ├── HPA — scales replicas; polls Metrics API every 15s
│   │   ├── Formula: ceil(current × currentMetric / desiredMetric)
│   │   ├── Requires: resources.requests.cpu on pods
│   │   └── Stabilization window: 5m scale-down, 0 scale-up (anti-flap)
│   ├── VPA — adjusts requests/limits; requires pod eviction to apply
│   │   ├── Modes: Off / Initial / Auto
│   │   └── Cannot run with HPA on CPU metrics simultaneously
│   ├── Cluster Autoscaler — adds/removes nodes for pending pods
│   │   └── Scale-down blocked by: PDB, local storage, DaemonSet, standalone pods
│   └── KEDA — event-driven HPA; scales to zero; Kafka/SQS/Prometheus/Cron
├── Storage Deep Dive
│   ├── StorageClass — provisioner + parameters + reclaimPolicy + volumeBindingMode
│   │   └── WaitForFirstConsumer — defer PV creation until pod is scheduled (AZ fix)
│   ├── PV lifecycle: Provision → Bind → Use → Release → Reclaim (Delete/Retain)
│   ├── StatefulSet VolumeClaimTemplates — unique PVC per pod-ordinal; survives reschedule
│   └── CSI driver — standard plugin interface; CreateVolume / NodePublishVolume
├── Networking Internals
│   ├── kube-proxy modes: iptables (O(n)) → IPVS (O(1)) → eBPF/Cilium (bypass)
│   ├── EndpointSlices — replace Endpoints; ≤100 endpoints each (scalability)
│   ├── CoreDNS ndots:5 — 5 search-domain lookups before external DNS
│   └── Headless Service (clusterIP: None) — DNS returns pod IPs directly
├── RBAC & Security
│   ├── Role/ClusterRole + RoleBinding/ClusterRoleBinding — four objects
│   ├── ServiceAccount IRSA/Workload Identity — OIDC federation to IAM roles
│   ├── Pod Security Standards (PSS) — privileged / baseline / restricted
│   ├── Admission webhooks — MutatingAdmissionWebhook / ValidatingAdmissionWebhook
│   └── OPA Gatekeeper / Kyverno — policy as code; validate/mutate/generate
├── Workload Patterns
│   ├── Init containers — sequential pre-conditions before main container starts
│   ├── Sidecar pattern — logging (Fluentbit), proxy (Envoy), secret agent (Vault)
│   ├── PodDisruptionBudget — minAvailable/maxUnavailable during voluntary disruptions
│   └── Deployment rolling update — maxUnavailable + maxSurge; revision history
├── Observability
│   ├── QoS classes: Guaranteed (req==lim) / Burstable / BestEffort
│   │   └── Eviction order: BestEffort first → Burstable → Guaranteed last
│   ├── Resource requests vs limits — scheduler uses requests; OOMKill on limit breach
│   └── kubectl top / VPA recommendations — measure before setting limits
└── Advanced Architecture
    ├── CRDs + Operators — extend API; custom reconciliation loops
    ├── Server-side Apply — field ownership tracking; prevents operator/kubectl conflicts
    └── API Priority and Fairness (APF) — prevents CI bots from starving kubelet heartbeats
```

### First Principles

- You have many containers — the **scheduler** places them using a two-phase filter+score algorithm driven by resource requests and constraints.
- Machines fail — **autoscalers** (HPA/VPA/CA/KEDA) adjust replica counts and node counts to maintain capacity without manual intervention.
- Traffic reaches containers — **kube-proxy** (or Cilium eBPF) translates ClusterIPs to pod IPs; EndpointSlices track which pods are ready.
- Config and secrets externalised — **admission webhooks** enforce policy at creation time; PSS prevents privilege escalation at admission.
- Zero-downtime rollouts — **PodDisruptionBudgets** protect against simultaneous evictions during node maintenance or rolling updates.

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

***

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

### System Design Perspective

- **HPA formula denominator is the requests value — not the limit:** The utilization percentage is `currentUsage / requests`. If requests are set too low (e.g., 100m CPU but the app routinely uses 300m), HPA will perpetually over-scale. Conversely, if requests are too high, HPA under-scales. VPA recommendations provide the correct baseline; run VPA in `Off` mode first to gather recommendations before enabling HPA.
- **WaitForFirstConsumer binding mode — why it exists:** Without it, the cloud provisioner creates the EBS/Azure Disk volume in whatever AZ the PV controller runs in (typically random). The pod may then be scheduled to a different AZ, and the volume cannot attach cross-AZ. `WaitForFirstConsumer` waits until the pod's node is selected, then provisions the volume in the same AZ. This eliminates an entire class of pod scheduling failures in multi-AZ clusters.
- **Admission webhook availability is a cluster availability risk:** A `ValidatingWebhook` with `failurePolicy: Fail` that becomes unavailable blocks all pod creation cluster-wide. The webhook service must have its own HA (2+ replicas, PDB), must exclude `kube-system` via `namespaceSelector`, and must have a lower SLA than the cluster itself. A webhook outage is worse than a policy bypass.
- **Server-side apply and operator conflicts:** If both `kubectl apply` (client-side) and an operator manage the same Deployment fields, they fight: kubectl adds the `last-applied-configuration` annotation, operator patches the field, kubectl reverts it on next apply. Server-side apply solves this with field ownership — each field records its manager. Operators should use SSA with `force: true` for fields they exclusively own.
- **IRSA/Workload Identity — why not environment variable credentials:** Long-lived AWS access keys in pod environment variables are a secret rotation nightmare (requires pod restart) and a blast radius nightmare (any code execution in the pod extracts the key). OIDC-based short-lived tokens (IRSA on EKS) are automatically rotated by the kubelet, scoped to the ServiceAccount, and expire within hours. The trade-off: requires IAM + OIDC provider configuration overhead.


```
Kubernetes Hard Interview Questions
├── CNI & Networking Internals
│   ├── Flannel — VXLAN overlay; no NetworkPolicy; simple; +50B overhead
│   ├── Calico — BGP routing or VXLAN; full NetworkPolicy; eBPF dataplane
│   ├── Cilium — eBPF-native; L7 NetworkPolicy; replaces kube-proxy; Hubble observability
│   ├── kube-proxy modes: iptables O(n) → IPVS O(1) → eBPF O(1) socket-level
│   └── MTU: VXLAN adds 50B; pod MTU must be 1450 on 1500-MTU networks
├── Control Plane Deep Dive
│   ├── etcd (Raft)
│   │   ├── Quorum: 3-node=1 failure, 5-node=2 failures; odd numbers only
│   │   ├── fsync latency <10ms; NVMe SSDs required for production
│   │   ├── Default DB quota 2GB → 8GB max; exceeding = read-only cluster
│   │   └── Compact + defrag cycle to reclaim space; automated offsite snapshots
│   ├── kube-apiserver
│   │   ├── Horizontally scalable; stateless; all state in etcd
│   │   ├── API Priority and Fairness (APF) — FlowSchema + PriorityLevel buckets
│   │   ├── Watch cache — in-memory; LIST with resourceVersion=0 hits cache not etcd
│   │   └── Webhook chain: AuthN → AuthZ → MutatingWebhook → Validate → ValidatingWebhook → etcd
│   └── kube-scheduler
│       ├── Filter phase: CPU/RAM/taints/affinity/PVC zone/port conflicts
│       ├── Score phase: LeastAllocated/NodeAffinity/TopologySpread/ImageLocality
│       ├── Preemption — evict lower-priority pods to schedule high-priority
│       ├── Gang scheduling — all-or-nothing (Volcano/Yunikorn); ML training jobs
│       └── Custom scheduler — spec.schedulerName; calls POST /binding
├── Advanced Scheduling
│   ├── Topology Spread Constraints — maxSkew across zones/nodes
│   ├── Taints NoExecute + tolerationSeconds — evict after N seconds
│   ├── PriorityClass — preemption order for critical workloads
│   └── Scheduling Framework plugins — PreFilter/Filter/Score/Bind extension points
├── Autoscaling Architecture
│   ├── HPA — Metrics API → desiredReplicas formula → stabilization window
│   ├── VPA — 24h data for recommendations; evicts pods to apply; conflicts with HPA CPU
│   ├── Cluster Autoscaler — 10s loop; simulates pending pods; 2-5 min node provision
│   └── Karpenter — EC2 Fleet API; 30-60s provision; consolidation loop; spot/OD mix
├── Security Architecture
│   ├── RBAC — allow-only; no Deny rules; implicit deny on unmatched requests
│   ├── Pod Security Admission — privileged/baseline/restricted at namespace level
│   ├── OPA Gatekeeper — Rego policies; ConstraintTemplate + Constraint CRDs
│   ├── Kyverno — YAML-native; validate/mutate/generate policies
│   ├── Sigstore/Cosign — cryptographic image signing; Admission webhook verification
│   └── IRSA/Workload Identity — OIDC federation; short-lived tokens; no long-lived keys
├── CRDs & Operators
│   ├── CRD — extends K8s API; objects stored in etcd; versioned schema validation
│   ├── Operator pattern — custom reconciliation loop; domain-specific operational knowledge
│   ├── controller-runtime — Reconcile() function; idempotent; RequeueAfter; finalizers
│   └── Maturity levels: Install → Upgrade → Lifecycle → Insights → AutoPilot
├── Multi-Tenancy
│   ├── Soft: Namespace + RBAC + ResourceQuota + NetworkPolicy + OPA
│   └── Hard: vcluster — virtual control plane per tenant inside namespace
├── Storage Advanced
│   ├── CSI: CreateVolume/NodeStageVolume/NodePublishVolume
│   ├── VolumeSnapshots — snapshot + restore from PVC via CRD
│   └── WaitForFirstConsumer — defer provisioning until pod scheduled (AZ alignment)
├── Observability
│   ├── Prometheus — kubernetes_sd_configs; scrape pods/nodes/endpoints
│   ├── etcd metrics — etcd_server_leader_changes_seen_total; WAL fsync latency
│   └── OpenTelemetry Operator — auto-instrumentation via pod annotation injection
└── GitOps & API Mechanics
    ├── Server-side Apply — field ownership; conflict on shared fields (409)
    ├── Watch cache — 410 Gone if resourceVersion falls outside cache window
    └── ArgoCD drift detection — spec vs live state; sync waves for ordering
```

### First Principles

- You have many containers across many machines — **etcd** stores all desired state as the single source of truth; its consistency (Raft quorum) is what makes the entire system reliable.
- Machines fail — **preemption, PriorityClass, and PodDisruptionBudgets** ensure critical workloads survive node failures without taking down the entire application tier.
- Traffic must reach containers wherever they run — **eBPF/Cilium** replaces iptables with kernel-level O(1) packet routing; L7 NetworkPolicy extends this to HTTP method/path filtering.
- Config and secrets externalised — **IRSA/Workload Identity** eliminates long-lived credentials from pods entirely; the OIDC token is auto-rotated and pod-scoped.
- Zero-downtime rollouts at scale — **Operators** encode domain-specific operational knowledge (DB failover, backup, schema migration) into reconciliation loops, making complex stateful applications as manageable as stateless ones.

## Hard

**26. Explain the difference between Calico and Flannel CNI plugins.**

- **Flannel:** Overlay network using VXLAN encapsulation. Simple setup, works anywhere, no Network Policy support out of box. Encapsulation adds overhead.
- **Calico:** Pure L3 routing using BGP — no encapsulation overhead. Full Network Policy support, eBPF dataplane option, ideal for production with high-performance requirements. More complex setup, requires BGP-capable underlying network.

**27. How do you design a highly available multi-master Kubernetes cluster on-prem?**

1. **etcd:** 3 or 5 external etcd nodes (not stacked on control plane) for HA — quorum survives single node loss.
2. **Control plane:** 3+ master nodes each running `apiserver`, `scheduler`, `controller-manager`.
3. **Load balancer:** HAProxy/F5 in front of port 6443 of all masters. All kubelets and clients use the LB virtual IP.
4. **etcd backups:** Scheduled `etcdctl snapshot` to object storage. Test restores quarterly.

**28. What is CPU throttling in Kubernetes and how does it affect latency-sensitive apps?**
When a container's CPU usage exceeds its `limit`, the Linux CFS scheduler throttles it — the process is paused for a period. An app with low average CPU but short bursts can be throttled even with headroom available. A 100ms burst above the limit can cause 1 second of pause time. Detection: monitor `container_cpu_cfs_throttled_periods_total` in Prometheus. Fix: raise CPU limits or leave CPU limits unset (relying on `requests` for scheduling). Never apply this blindly — nodes can be overloaded if all pods burst simultaneously.

**29. How do you debug a Java application that is OOMKilled even though `-Xmx` is well below the container limit?**

The container memory limit applies to the entire JVM process, not just the heap. Non-heap memory includes:
- **Metaspace:** class metadata.
- **Thread stacks:** each thread gets its own stack (default 512KB-1MB).
- **Native memory:** JVM internals, JIT compiler, native libraries.
- **DirectByteBuffer:** off-heap memory used by NIO.

Fix: use `-XX:+UseContainerSupport` (sets JVM to respect cgroup limits). Profile RSS with `pmap <pid>` or async-profiler. Set the container memory limit 25-50% higher than `-Xmx` to account for non-heap overhead.

**30. How would you write and deploy a custom Kubernetes scheduler?**

1. Write an application (Go) that watches the API server for Pods with `spec.schedulerName: my-scheduler` where `spec.nodeName` is empty.
2. Implement filtering (feasibility) and scoring (priority) logic.
3. Bind the Pod: `POST /api/v1/namespaces/<ns>/pods/<name>/binding` with the chosen node name.
4. Deploy as a Kubernetes Deployment. Pods opt in via `spec.schedulerName`.

Use cases: custom hardware affinity (FPGAs, specific GPU models), cost-aware scheduling, or topology-sensitive placement for ML workloads.

**31. How do Kubernetes Volume Snapshots enable a database backup and restore strategy?**

- **Backup:** Quiesce the database → create `VolumeSnapshot` YAML pointing to the PVC → CSI driver creates the snapshot → unquiesce.
- **Restore:** Create a new PVC with `dataSource: kind: VolumeSnapshot` pointing to the snapshot → CSI driver provisions a volume with the snapshotted data → attach to a new database Pod.

Volume snapshots are crash-consistent (instant) at the storage layer. For application consistency, quiescence (flush + lock) is needed before taking the snapshot.

**32. How does the Kubernetes Horizontal Pod Autoscaler work with custom metrics?**

HPA polls the Metrics API (metrics-server for CPU/memory, or the Custom Metrics API for external sources). For custom metrics, you register a Custom Metrics API provider (KEDA, Prometheus Adapter) that exposes metrics in the `custom.metrics.k8s.io` API. HPA computes: `desiredReplicas = ceil(currentReplicas × currentMetricValue / desiredMetricValue)`. KEDA extends this by polling event sources (SQS, Kafka queue depth) directly and scaling to zero when queues are empty.

**33. What is MIG (Multi-Instance GPU) and how does it affect Kubernetes scheduling?**

MIG (NVIDIA A100/H100) partitions a single physical GPU into isolated slices, each with dedicated memory and compute. Each slice appears as a separate schedulable resource in Kubernetes (e.g., `nvidia.com/mig-1g.5gb`). Multiple Pods can share a GPU with hardware isolation — no memory or compute interference. Kubernetes schedules each slice independently. Useful for right-sizing inference workloads that don't need a full A100 (80GB), reducing GPU cost per workload.

**34. Explain the execution architecture of `controller-runtime` reconciler loops. How do you design operators to be reentrant, idempotent, and resilient under massive API pressure?**

**Answer:**

### 1. Reconciler Runtime Loop Architecture
Most custom operators utilize the Go `controller-runtime` framework. The event-handling datapath is structured to decouple raw API client requests from reconciler execution, preventing API server CPU starvation:

```
[kube-apiserver]
       │ LIST / WATCH (Chunked HTTP Stream)
       ▼
  [Reflector] ────► [DeltaFIFO] ────► [Informer] ────► [Lister (In-Memory Cache)]
                                         │
                                         ▼ (Trigger Event)
                                  [Event Handlers]
                                         │ (Enqueue key: namespace/name)
                                         ▼
                                    [Workqueue] (Deduplicating & Rate-limiting)
                                         │
                                         ▼ (Pop key)
                                 [Reconcile Workers] ──► Query Lister Cache
```

1. **Reflector**: Establishes a persistent `LIST` + `WATCH` stream to the `kube-apiserver` for the target CRD and associated resources.
2. **DeltaFIFO**: Tracks state deltas (Create, Update, Delete) in a queue.
3. **Informer**: Pops deltas from DeltaFIFO. It updates the local, thread-safe memory database (**Lister cache**) and fires registering callback hooks.
4. **Event Handlers**: Maps events to the resource's namespace/name keys.
5. **Workqueue**: A rate-limiting, deduplicating work queue. If key `default/app-v1` is enqueued 5 times in rapid succession, the deduplication engine merges them into a single entry, protecting the system from redundant reconciles.
6. **Reconcile Worker Pool**: Concurrent workers pop keys from the Workqueue and execute the custom `Reconcile(ctx, req)` loop.

### 2. Design Patterns for Resilient Reconcilers

#### A. True Level-Triggered Execution
Reconcilers must operate on a **Level-Triggered** model. Never assume a reconcile cycle is associated with a specific event (e.g., "Pod added"). The reconciler must:
1. Query the Lister cache for the current state of the Custom Resource (`CR`).
2. Query the Lister cache for the current state of all child resources (e.g., Pods, Services).
3. Compute the delta: "Desired state (Spec) minus Actual state."
4. Execute mutations to drive actual state toward desired.

#### B. Idempotence & Reentrancy
A reconcile worker can be interrupted, throttled, or restarted at any millisecond. Thus, `Reconcile()` must be entirely reentrant and idempotent:
* **Guard Mutations**: Always check if a resource already exists before trying to create it:
  ```go
  err := r.Get(ctx, req.NamespacedName, &service)
  if errors.IsNotFound(err) {
      // Safe to create
      return r.Create(ctx, &newService)
  }
  ```
* **Avoid Generation Loops**: If you update the resource's `Spec` from within the reconcile loop, you will trigger an infinite cascade of reconcile cycles. **Define a `/status` subresource in the CRD schema**. Use `r.Status().Update()` to record runtime states without incrementing the resource's `metadata.generation` sequence.
* **Avoid External API Side-effects**: If the reconciler provisions external hardware (e.g., an AWS RDS database), ensure you generate deterministic names (e.g., hash of the CR UID and namespace) and check if the database exists in AWS before initiating creation calls.

#### C. Handling API Server Pressure
* **Query the Cache, Not the API**: Never use raw API client GET/LIST calls inside the reconciler. Always query the Informer's `Lister` cache. Direct API queries under massive scale will choke the API server.
* **Rate-limiting Backoff**: If an external API call fails, do not panic or loop infinitely. Return the error so the Workqueue applies its exponential rate-limiter (e.g., backing off from 5ms to 10s retries), allowing downstream dependencies time to recover.

---

**35. What are the operational risks of deploying Mutating and Validating Admission Webhooks with a `failurePolicy: Fail`? How do you design a high-throughput, zero-downtime, resilient webhook system?**

**Answer:**

### 1. The Operational Risk: Cluster Lockout & Bricking
When an admission webhook is registered with `failurePolicy: Fail`, any `kube-apiserver` request that matches the webhook rules **will be rejected** if the webhook endpoint is unreachable, slow, or returning errors.

```
                    Cascading Failure Loop (FailurePolicy: Fail)
Webhooks Down ──► Pods Evicted ──► Reschedule Fails (API rejects Pod creations) ──► Cluster Deadlock
```

* **Cascading Death Spiral**: If your webhook intercepts core resources (`pods`, `namespaces`, `services`) and the webhook server crashes (e.g., due to an OOMKill or a node network partition):
  1. The API server cannot launch new pods, scale deployments, or provision network endpoints.
  2. If the cluster tries to reschedule the crashed webhook pods on another node, the API server blocks the Pod creation request because the webhook service is down.
  3. The cluster enters a **permanent deadlock (bricked control plane)** that can only be fixed by manually SSHing into the master control-plane nodes and running `kubectl delete validatingwebhookconfiguration` directly.
* **API Server Resource Starvation**: A webhook timeout of 10s combined with `FailurePolicy: Fail` under high concurrency will exhaust the API server's HTTP connection pool, causing cluster-wide latency spikes and timeout failures.

### 2. High-Availability Webhook Design Patterns

#### A. Strict Namespace & Object Selectors (Deadlock Prevention)
Never apply a `failurePolicy: Fail` webhook globally without exemptions. Scrape and exempt system namespaces:
```yaml
namespaceSelector:
  matchExpressions:
    - key: kubernetes.io/metadata.name
      operator: NotIn
      values: ["kube-system", "security-system", "monitoring"]
```
This guarantees core control plane controllers (e.g., kube-system kubelet loops, CoreDNS) can scale, recover, and provision pods regardless of webhook health.

#### B. Low Timeout Tuning
Change the default `timeoutSeconds` from 10 seconds to **1 or 2 seconds**:
```yaml
timeoutSeconds: 1
```
If the webhook takes longer than 1-2s, it is throttled. This prevents a slow webhook from back-pressuring and locking the `kube-apiserver` connection pool.

#### C. High Availability & Node Anti-Affinity
Run a minimum of 3 webhook backend replicas. To protect against node outages, enforce **Topology Spread Constraints** or **Pod Anti-Affinity** to ensure replicas are scheduled on different physical nodes and availability zones:
```yaml
affinity:
  podAntiAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      - labelSelector:
          matchExpressions:
            - key: app
              operator: In
              values: ["policy-webhook"]
        topologyKey: "kubernetes.io/hostname"
```

#### D. Priority Class allocation
Webhooks are part of the cluster's critical control plane. Set their `priorityClassName` to `system-cluster-critical` or `system-node-critical` to prevent them from being evicted under host memory/CPU resource pressure.

#### E. Sub-50ms Memory Profiling
* **Caching**: The webhook must execute in <50ms. Never make synchronous HTTP calls to external systems (e.g., querying active users in Okta or scanning files in S3) inside the webhook handler. 
* **Worker Queue**: If external validation is required, perform it asynchronously. The admission webhook should validate the structural labels, check a local memory cache of allowed entities, and immediately return `allowed: true`. A separate asynchronous background controller can later reconcile and delete non-compliant resources.

***
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 


***

### Page 2

I. Kubernetes Fundamentals and Architecture 
1. What is Kubernetes and why is it used? 
o Answer: Kubernetes (K8s) is an open-source container orchestration 
platform that automates the deployment, scaling, and management of 
containerized applications. It solves the challenges of managing large, 
distributed applications across multiple servers by providing features like 
automated scheduling, self-healing, rolling updates, and service 
discovery. 
2. Explain the core components of Kubernetes architecture. 
o Answer: Kubernetes architecture consists of two main parts:  
▪ 
Control Plane (Master Node):  
▪ 
Kube-apiserver: The front-end of the Kubernetes control 
plane, exposing the Kubernetes API. All communication 
with the cluster goes through the API server. 
▪ 
etcd: A highly available, distributed key-value store that 
stores all cluster data (configurations, state, metadata). 
▪ 
Kube-scheduler: Selects a node for newly created Pods 
based on resource requirements, constraints, and other 
policies. 
▪ 
Kube-controller-manager: Runs controller processes that 
regulate the cluster's state (e.g., Node Controller, 
Replication Controller, Endpoints Controller, Service 
Account & Token Controllers). 
▪ 
Worker Nodes:  
▪ 
Kubelet: An agent that runs on each node in the cluster, 
ensuring containers are running in a Pod. It communicates 
with the control plane. 
▪ 
Kube-proxy: A network proxy that runs on each node, 
maintaining network rules on nodes and enabling network 
communication to your Pods from inside or outside of the 
cluster. 
▪ 
Container Runtime (e.g., containerd, CRI-O, Docker): The 
software responsible for running containers. 
3. What is a Pod in Kubernetes? Why is it the smallest deployable unit? 


***

### Page 3

o Answer: A Pod is the smallest deployable unit in Kubernetes. It 
represents a single instance of a running process in your cluster. It's the 
smallest unit because containers within a Pod share the same network 
namespace, IP address, and storage, making them tightly coupled and 
allowing them to communicate via localhost. 
4. What is the relationship between Kubernetes and Docker? 
o Answer: Docker is a containerization platform that enables you to 
package and run applications in isolated environments called containers. 
Kubernetes is a container orchestration platform that manages and 
automates the deployment, scaling, and operation of Docker containers 
(or any other OCI-compliant container runtime) across a cluster of 
machines. Docker builds the house (container), Kubernetes manages the 
neighborhood (cluster). 
5. Explain Namespaces in Kubernetes. When would you use them? 
o Answer: Namespaces provide a mechanism for isolating groups of 
resources within a single Kubernetes cluster. They are essentially virtual 
clusters within a physical cluster. You would use them for:  
▪ 
Resource isolation: Separating resources for different teams, 
projects, or environments (e.g., dev, staging, prod). 
▪ 
Access control: Applying RBAC policies at a namespace level to 
restrict user access. 
▪ 
Resource quotas: Setting resource limits (CPU, memory) per 
namespace. 
6. What are Labels and Selectors in Kubernetes? 
o Answer:  
▪ 
Labels: Key-value pairs that are attached to Kubernetes objects 
(e.g., Pods, Services, Deployments). They are used to organize, 
identify, and categorize objects. 
▪ 
Selectors: Used to filter objects based on their labels. Services 
use selectors to identify the Pods they should route traffic to, and 
Deployments use them to manage their associated Pods. 
7. What is a Service in Kubernetes? Why is it needed? 
o Answer: A Service is an abstraction that defines a logical set of Pods and 
a policy by which to access them. It provides a stable network endpoint (a 
fixed IP address and DNS name) for a group of Pods, even as Pods are 


***

### Page 4

created, deleted, or rescheduled. This is crucial because Pods are 
ephemeral and their IP addresses can change. 
8. Differentiate between ClusterIP, NodePort, and LoadBalancer Service types. 
o Answer:  
▪ 
ClusterIP: Exposes the Service on an internal IP in the cluster. It's 
only reachable from within the cluster. Default type. 
▪ 
NodePort: Exposes the Service on each Node's IP at a static port 
(the NodePort). Makes the Service accessible from outside the 
cluster by NodeIP:NodePort. 
▪ 
LoadBalancer: Exposes the Service externally using a cloud 
provider's load balancer. This type automatically provisions a load 
balancer and routes external traffic to your Service. (Requires 
cloud provider integration). 
▪ 
ExternalName: Maps the Service to a DNS name, not a cluster IP 
or NodePort. Used for services external to the cluster. 
9. What is a Deployment in Kubernetes? 
o Answer: A Deployment is a higher-level abstraction that manages the 
lifecycle of Pods and ReplicaSets. It provides declarative updates to Pods, 
ensuring that the desired number of replicas are running and facilitating 
features like rolling updates, rollbacks, and self-healing. 
10. Explain the difference between a ReplicaSet and a Deployment. 
o Answer:  
▪ 
ReplicaSet: Ensures a specified number of identical Pod replicas 
are running at all times. It's a low-level controller primarily used by 
Deployments. 
▪ 
Deployment: A higher-level object that manages ReplicaSets. It 
provides declarative updates to Pods and supports features like 
rolling updates, rollbacks, and versioning, making it the preferred 
way to manage stateless applications. 
11. What is a StatefulSet and when would you use it? 
o Answer: A StatefulSet is a workload API object used to manage stateful 
applications. Unlike Deployments, StatefulSets provide:  
▪ 
Stable, unique network identifiers: Each Pod gets a stable 
hostname. 


***

### Page 5

▪ 
Stable, persistent storage: PersistentVolumes are provisioned for 
each Pod. 
▪ 
Ordered, graceful deployment and scaling: Pods are created and 
terminated in a defined order. 
▪ 
Ordered, graceful deletion: Pods are deleted in reverse ordinal 
order. 
o You'd use StatefulSets for applications requiring persistent storage, stable 
network identities, or ordered scaling, such as databases (e.g., MySQL, 
PostgreSQL), message queues (e.g., Kafka), or other stateful services. 
12. What is a DaemonSet and when would you use it? 
o Answer: A DaemonSet ensures that a copy of a Pod runs on all (or a 
subset of) nodes in a cluster. They are typically used for cluster-level 
functionalities like:  
▪ 
Logging agents: (e.g., Fluentd, Logstash) 
▪ 
Monitoring agents: (e.g., Prometheus Node Exporter) 
▪ 
Storage daemon: (e.g., Ceph) 
13. Explain ConfigMaps and Secrets. What's the difference? 
o Answer:  
▪ 
ConfigMaps: Used to store non-sensitive configuration data as 
key-value pairs. They allow you to decouple configuration from 
application code, making it easier to manage and update. 
▪ 
Secrets: Similar to ConfigMaps but designed for storing sensitive 
data like passwords, API keys, and tokens. Kubernetes handles 
Secrets more securely by encoding them (Base64) and providing 
mechanisms for secure distribution and access. 
o Difference: Sensitivity of data and how they are handled securely. 
14. What is Ingress in Kubernetes? How does it differ from a LoadBalancer 
Service? 
o Answer:  
▪ 
Ingress: An API object that manages external access to services 
within the cluster, typically HTTP/HTTPS traffic. It provides features 
like URL-based routing, name-based virtual hosting, and SSL/TLS 


***

### Page 6

termination. An Ingress resource requires an Ingress Controller 
(e.g., Nginx Ingress Controller, Traefik) to function. 
▪ 
LoadBalancer Service: Provisions a cloud provider's load 
balancer to expose a Service. It works at the TCP/UDP layer. 
o Difference: Ingress operates at Layer 7 (Application Layer) and offers 
more advanced routing rules based on hostname and path, while a 
LoadBalancer Service operates at Layer 4 (Transport Layer) and provides 
a simple way to expose a Service externally. 
15. How does Kubernetes handle storage orchestration? 
o Answer: Kubernetes provides a flexible storage orchestration framework 
using:  
▪ 
PersistentVolume (PV): A cluster-wide resource representing a 
piece of networked storage provisioned by an administrator or 
dynamically provisioned. 
▪ 
PersistentVolumeClaim (PVC): A request for storage by a user, 
specifying the size and access mode. Kubernetes matches PVCs 
to available PVs. 
▪ 
StorageClass: Defines different classes of storage (e.g., "fast", 
"slow") and their provisioner. This allows for dynamic provisioning 
of PVs when a PVC requests a specific StorageClass. 
 
II. Networking in Kubernetes 
16. Explain the Kubernetes networking model. 
o Answer: Kubernetes enforces a "flat" networking model where:  
▪ 
All Pods can communicate with all other Pods without NAT. 
▪ 
All Nodes can communicate with all Pods without NAT. 
▪ 
The IP that a Pod sees itself as is the same IP that others see it as. 
o This model relies on a Container Network Interface (CNI) plugin (e.g., 
Calico, Flannel, Cilium) to implement the actual network fabric. 
17. How does Pod-to-Pod communication work within the same node? 
o Answer: Pods on the same node communicate via the CNI bridge. The 
CNI plugin creates a virtual Ethernet pair for each Pod, with one end in the 


***

### Page 7

Pod's network namespace and the other connected to a bridge on the 
node. 
18. How does Pod-to-Pod communication work across different nodes? 
o Answer: Pods across different nodes communicate via the overlay 
network created by the CNI plugin. The CNI plugin encapsulates Pod 
traffic (e.g., using VXLAN, IPIP) and routes it between nodes. 
19. What are Network Policies in Kubernetes? When would you use them? 
o Answer: Network Policies are Kubernetes resources that define rules for 
how Pods are allowed to communicate with each other and with other 
network endpoints. They provide network segmentation and security by 
restricting traffic flow. You'd use them for:  
▪ 
Isolating different application tiers (e.g., frontend, backend, 
database). 
▪ 
Restricting access to sensitive services. 
▪ 
Implementing micro-segmentation within your cluster. 
20. How does Kubernetes handle DNS for services and pods? 
o Answer: Kubernetes uses an internal DNS service (typically CoreDNS) to 
provide service discovery.  
▪ 
Pods: Each Pod gets a DNS A record in the form pod-ip-
address.namespace.pod.cluster.local. 
▪ 
Services: Each Service gets a DNS A record in the form service-
name.namespace.svc.cluster.local. Headless services also get A 
records for their individual Pods. 
 
III. Deployment and Scaling 
21. Describe the process of a rolling update in Kubernetes. 
o Answer: A rolling update gradually updates application instances with a 
new version without downtime. When you update a Deployment, 
Kubernetes creates new Pods with the new image, waits for them to 
become healthy, and then slowly terminates old Pods. This ensures 
continuous availability during the update. 
22. How do you perform a rollback of a Deployment? 


***

### Page 8

o Answer: You can use kubectl rollout undo deployment <deployment-
name>. You can also specify a specific revision to roll back to using --to-
revision=<revision-number>. 
23. What is Horizontal Pod Autoscaling (HPA)? How does it work? 
o Answer: HPA automatically scales the number of Pod replicas in a 
Deployment or ReplicaSet based on observed CPU utilization, memory 
utilization, or custom metrics. It periodically checks the metrics and 
adjusts the replicas field of the target resource. 
24. What is Vertical Pod Autoscaling (VPA)? 
o Answer: VPA automatically adjusts the CPU and memory requests and 
limits for containers in a Pod based on historical usage. It helps optimize 
resource allocation and prevent over-provisioning or under-provisioning. 
(Note: VPA is still in beta and has implications for Pod rescheduling.) 
25. What is Cluster Autoscaler? 
o Answer: Cluster Autoscaler automatically adjusts the number of nodes in 
your Kubernetes cluster based on resource requests and actual usage. If 
Pods cannot be scheduled due to insufficient resources, it adds new 
nodes. If nodes are underutilized, it removes them. 
26. How would you troubleshoot a failed Deployment? 
o Answer:  
1. kubectl get deployments (check status) 
2. kubectl describe deployment <deployment-name> (check events, 
conditions, replica status) 
3. kubectl get replicasets (check associated ReplicaSets) 
4. kubectl get pods -l app=<label> (check Pod status) 
5. kubectl describe pod <pod-name> (check events, container 
status, volumes) 
6. kubectl logs <pod-name> (check application logs) 
7. kubectl exec -it <pod-name> -- /bin/sh (debug inside the container) 
8. Check kube-apiserver and kube-scheduler logs if no Pods are 
scheduling. 
9. Check kubelet logs on the node if Pods are stuck in a pending 
state. 


***

### Page 9

27. Explain Liveness and Readiness Probes. Why are they important? 
o Answer:  
▪ 
Liveness Probe: Determines if a container is running and healthy. 
If the liveness probe fails, Kubernetes will restart the container. 
This prevents deadlocked containers from perpetually consuming 
resources. 
▪ 
Readiness Probe: Determines if a container is ready to serve 
traffic. If the readiness probe fails, Kubernetes will remove the 
Pod's IP from the Service endpoints, preventing traffic from being 
routed to an unready Pod. This ensures no traffic is sent to 
applications that are still starting up or experiencing issues. 
o Importance: They enable Kubernetes to self-heal and manage 
application availability and reliability. 
28. What is a CronJob in Kubernetes? Give an example use case. 
o Answer: A CronJob creates Jobs on a repeating schedule. They are used 
for performing scheduled tasks. 
o Example Use Case: Running a daily database backup, generating weekly 
reports, or cleaning up old logs. 
 
IV. Security and Access Control 
29. Explain Role-Based Access Control (RBAC) in Kubernetes. 
o Answer: RBAC is a mechanism that allows you to define who (Subjects: 
Users, Groups, Service Accounts) can do what (Verbs: get, list, create, 
delete) to which resources (Resources: Pods, Deployments, Services) in 
which namespaces. 
o Key components:  
▪ 
Role: Defines permissions within a specific namespace. 
▪ 
ClusterRole: Defines permissions across the entire cluster. 
▪ 
RoleBinding: Grants the permissions defined in a Role to a 
Subject within a namespace. 
▪ 
ClusterRoleBinding: Grants the permissions defined in a 
ClusterRole to a Subject across the entire cluster. 
30. What are Service Accounts? How are they used? 


***

### Page 10

o Answer: Service Accounts provide an identity for processes that run in 
Pods. When a Pod makes API calls to the Kubernetes API server, it 
authenticates using the credentials of its Service Account. They are used 
for:  
▪ 
Allowing Pods to interact with the Kubernetes API. 
▪ 
Controlling access to resources within the cluster. 
▪ 
Integrating with external systems that need to authenticate to 
Kubernetes. 
31. How do you secure access to the Kubernetes API server? 
o Answer:  
▪ 
Authentication: Using client certificates, tokens, or integrated 
cloud provider authentication. 
▪ 
Authorization (RBAC): Defining granular permissions. 
▪ 
Admission Controllers: Enforcing policies before objects are 
created or modified. 
▪ 
Network Policies: Restricting network access to the API server. 
▪ 
Encryption in transit: Using TLS for all communication. 
32. What are Pod Security Standards (PSS) and why are they important? 
o Answer: PSS define a set of security best practices for Pods in 
Kubernetes. They are divided into three levels:  
▪ 
Privileged: Unrestricted capabilities, used for highly privileged 
workloads. 
▪ 
Baseline: Minimally restrictive, prevents known privilege 
escalations. 
▪ 
Restricted: Highly restrictive, enforces hardening best practices. 
o They are important for improving the security posture of your cluster by 
preventing common security vulnerabilities in Pods. 
 
V. Monitoring and Logging 
33. How do you monitor a Kubernetes cluster? What tools are commonly used? 


***

### Page 11

o Answer: Monitoring a Kubernetes cluster involves collecting metrics, 
logs, and events. Commonly used tools include:  
▪ 
Metrics: Prometheus (for scraping metrics) and Grafana (for 
visualization). 
▪ 
Logging: Fluentd/Fluent Bit, Logstash, Elasticsearch, Kibana (ELK 
stack). 
▪ 
Tracing: Jaeger, Zipkin. 
▪ 
Built-in tools: kubectl top, kubectl describe, Kubernetes 
Dashboard (though often not used in production). 
▪ 
Cloud-native solutions: Google Cloud Monitoring, AWS 
CloudWatch Container Insights, Azure Monitor for Containers. 
34. How do you collect logs from applications running in Kubernetes? 
o Answer:  
▪ 
Standard output/error: Applications should write logs to stdout 
and stderr. 
▪ 
Logging agents: Deploy a logging agent (like Fluentd, Fluent Bit, or 
Logstash) as a DaemonSet on each node to collect logs from 
container runtimes and forward them to a centralized logging 
system (e.g., Elasticsearch, cloud logging services). 
▪ 
Sidecar containers: For applications that can't write to 
stdout/stderr, a sidecar container can be deployed in the same 
Pod to tail logs from a shared volume and forward them. 
35. What is the role of Prometheus in Kubernetes monitoring? 
o Answer: Prometheus is a popular open-source monitoring system that 
scrapes metrics from configured targets (like Kubernetes components, 
nodes, and applications) and stores them in a time-series database. It's 
often used with Grafana for dashboards and alerts. 
 
VI. Advanced Topics and Troubleshooting Scenarios 
36. Describe a scenario where you would use a Custom Resource Definition 
(CRD) and a Custom Controller/Operator. 


***

### Page 12

o Answer: You would use CRDs and Operators to extend Kubernetes's 
functionality for managing complex, stateful applications that have 
specific operational knowledge. 
o Scenario: Managing a distributed database like Cassandra or MongoDB. 
A CRD would define the desired state of your database cluster (e.g., 
number of nodes, version, backup schedule). An Operator (Custom 
Controller) would then watch for changes to this CRD, understand the 
operational complexities of Cassandra, and automate tasks like 
provisioning new nodes, handling upgrades, performing backups, and 
recovering from failures. 
37. Explain the concept of Taints and Tolerations. 
o Answer:  
▪ 
Taints: Applied to nodes to prevent Pods from being scheduled on 
them unless those Pods explicitly "tolerate" the taint. They mark a 
node as undesirable for scheduling. 
▪ 
Tolerations: Applied to Pods, allowing them to be scheduled on 
nodes that have matching taints. They allow (but don't require) a 
Pod to be scheduled on a tainted node. 
o Use cases: Dedicated nodes for specific workloads, preventing certain 
Pods from running on unhealthy nodes, isolating critical workloads. 
38. What are Node Affinity and Anti-Affinity? 
o Answer:  
▪ 
Node Affinity: Forces Pods to be scheduled on nodes with specific 
labels. It's a "pull" mechanism where Pods "attract" nodes.  
▪ 
requiredDuringSchedulingIgnoredDuringExecution: Must 
meet the rule, but ignored if node labels change later. 
▪ 
preferredDuringSchedulingIgnoredDuringExecution: 
Kubernetes tries to meet the rule but doesn't guarantee it. 
▪ 
Node Anti-Affinity: Prevents Pods from being scheduled on nodes 
with specific labels, often to spread Pods across different nodes 
for high availability. 
o Use cases: Ensuring performance, compliance, or high availability. 
39. How would you debug a Pod that is stuck in a Pending state? 
o Answer:  


***

### Page 13

1. 
kubectl describe pod <pod-name>: Check the Events section for reasons like:  
▪ 
Insufficient CPU/Memory: The cluster doesn't have 
enough resources. 
▪ 
Node Selector/Taints/Tolerations: The Pod has a node 
selector or toleration that doesn't match any available 
nodes. 
▪ 
Volume Issues: PersistentVolumeClaim cannot be bound 
to a PersistentVolume. 
▪ 
Networking Issues: CNI plugin not working correctly on 
nodes. 
2. 
kubectl get events --field-selector involvedObject.name=<pod-name>: More 
granular events. 
3. 
Check kube-scheduler logs for scheduling decisions. 
4. 
Check node resources: kubectl top nodes (if metrics server is running). 
40. How would you troubleshoot an application that is unreachable from 
outside the cluster? 
o Answer:  
1. 
Check Service type: Is it NodePort or LoadBalancer? If ClusterIP, it's not 
exposed externally. 
2. 
Verify Service endpoints: kubectl describe service <service-name>. Ensure it 
has healthy Pods as endpoints. 
3. 
Check Pod status: kubectl get pods -l app=<service-selector>. Are the Pods 
running and healthy (Readiness Probes passing)? 
4. 
Check Ingress (if used): kubectl describe ingress <ingress-name>. Verify rules, 
backend services, and events. 
5. 
Check Ingress Controller: Ensure the Ingress Controller Pods are running and 
healthy. Check their logs. 
6. 
Network Firewall/Security Groups: For NodePort or LoadBalancer, ensure 
external firewalls allow traffic to the NodePorts or the LoadBalancer IP. 
7. 
DNS resolution: If using a custom domain with Ingress, verify DNS records are 
correctly pointing to the Ingress Controller's external IP/hostname. 
8. 
kube-proxy: Ensure kube-proxy is running on all nodes and check its logs. 


***

### Page 14

41. What is a Helm chart? Why is it useful? 
o Answer: Helm is the package manager for Kubernetes. A Helm chart is a 
collection of files that describe a related set of Kubernetes resources. It's 
useful for:  
▪ 
Packaging: Bundling all Kubernetes resources for an application 
into a single, versionable unit. 
▪ 
Deployment: Easily deploying complex applications with a single 
command. 
▪ 
Templating: Parameterizing configurations for different 
environments. 
▪ 
Management: Managing releases, upgrades, and rollbacks of 
applications. 
42. How does Kubernetes handle self-healing? 
o Answer: Kubernetes self-healing capabilities include:  
▪ 
Restarting failed containers: Liveness probes detect unhealthy 
containers and restart them. 
▪ 
Rescheduling Pods on failed nodes: If a node goes down, the 
controller manager detects it and reschedules its Pods to healthy 
nodes. 
▪ 
Maintaining desired replicas: ReplicaSets and Deployments 
ensure the specified number of Pod replicas are always running. 
▪ 
Rolling back failed deployments: If a new deployment fails, it can 
automatically roll back to the previous stable version. 
43. What is a Pod Disruption Budget (PDB)? When would you use it? 
o Answer: A PDB is a Kubernetes API object that specifies the minimum 
number or percentage of Pods that must be available at all times during 
voluntary disruptions (e.g., node drain, cluster upgrade, scaling down). It 
ensures high availability for critical applications. You'd use it for stateful 
applications or mission-critical services that require a certain number of 
replicas to be running. 
44. Explain how kubectl exec works. 
o Answer: kubectl exec allows you to execute commands inside a 
container running in a Pod. It establishes a secure, bidirectional stream 


***

### Page 15

(similar to SSH) between your local machine and the container, enabling 
you to interact with the container's shell or run specific commands. 
45. What is GitOps and how does it relate to Kubernetes? 
o Answer: GitOps is an operational framework that uses Git as the single 
source of truth for declarative infrastructure and applications. In 
Kubernetes, this means:  
▪ 
All desired states of your cluster (Kubernetes manifests, Helm 
charts) are stored in Git. 
▪ 
Changes to the cluster are made by creating pull requests to the 
Git repository. 
▪ 
An automated agent (e.g., Flux, Argo CD) continuously observes 
the Git repository and applies any discrepancies to the cluster, 
ensuring the cluster's actual state matches the desired state in 
Git. 
o Benefits: Auditable deployments, faster disaster recovery, improved 
collaboration, and higher reliability. 
 
VII. Real-World Scenarios and Troubleshooting 
46. Scenario: Your application's Pods are constantly restarting. How do you 
investigate? 
o Answer:  
1. kubectl get pods: Check the RESTARTS column. 
2. kubectl describe pod <pod-name>: Look at the Events section for 
clues (e.g., OOMKilled, CrashLoopBackOff, failed 
liveness/readiness probes). 
3. kubectl logs <pod-name>: Check the application logs for errors or 
exceptions. 
4. kubectl logs <pod-name> -p: Check logs from the previous 
container instance if it's restarting. 
5. Check resource limits and requests in the Pod definition. Is the 
container running out of memory or CPU? 
6. Examine the application code for bugs or misconfigurations. 


***

### Page 16

47. Scenario: You need to deploy a new version of your application with zero 
downtime. How would you achieve this? 
o Answer: Use a Kubernetes Deployment with a rollingUpdate strategy. 
Ensure your Pods have properly configured Liveness and Readiness 
Probes. The rollingUpdate strategy will gracefully replace old Pods with 
new ones, ensuring continuous availability. Consider using 
maxUnavailable and maxSurge to control the rollout speed and resource 
consumption during the update. 
48. Scenario: A new application deployment is failing, and the Pods are stuck in 
ImagePullBackOff. What's wrong? 
o Answer: ImagePullBackOff indicates that Kubernetes is unable to pull the 
container image. Common causes:  
▪ 
Incorrect image name or tag: Double-check the image name and 
tag in the Pod/Deployment manifest. 
▪ 
Private registry authentication: If using a private registry, ensure 
imagePullSecrets are correctly configured in the Pod and linked to 
a Secret with valid credentials. 
▪ 
Network issues: Node cannot reach the image registry (firewall, 
DNS, proxy). 
▪ 
Image doesn't exist: The image might have been deleted from the 
registry. 
49. Scenario: You have a database running as a StatefulSet, and you need to 
scale it down. What considerations do you need to make? 
o Answer: StatefulSets scale down gracefully by terminating Pods in 
reverse ordinal order (e.g., db-2, db-1, db-0). Before scaling down, ensure:  
▪ 
Data integrity: The database is designed for graceful shutdown 
and data consistency during scale-down (e.g., by performing 
graceful shutdowns of database instances). 
▪ 
Data migration/rebalancing: If the database sharded data, 
ensure data is rebalanced or migrated off the terminating 
instances. 
▪ 
PersistentVolumeClaims: Understand that scaling down a 
StatefulSet does not automatically delete the associated PVCs. 
You'll need to manually delete them if the data is no longer 
needed. 


***

### Page 17

▪ 
Quorum: Ensure you don't scale down below the minimum 
required replicas for your database to maintain quorum and 
availability. 
50. Scenario: You want to ensure that a critical application always has at least 3 
Pods running, even during node maintenance. How would you configure 
this? 
o Answer: Implement a Pod Disruption Budget (PDB) for your application 
with minAvailable: 3 (or minAvailable: 100% if you want all of them). This 
will tell Kubernetes that it should try to keep at least 3 Pods of that 
application running during voluntary disruptions like kubectl drain. 
51. Scenario: You notice high CPU utilization on one of your worker nodes. How 
would you investigate and resolve it? 
o Answer:  
1. kubectl top nodes: Identify which node has high CPU. 
2. kubectl describe node <node-name>: Check resource usage and 
events. 
3. kubectl top pods --all-namespaces --sort-by='cpu': Identify which 
Pods on that node are consuming the most CPU. 
4. kubectl logs <pod-name>: Check logs of the high-CPU Pod for 
application issues. 
5. kubectl exec -it <pod-name> -- top: Go inside the container to see 
process-level CPU usage. 
6. Resolution:  
▪ 
Scale Pods: If the application can be scaled horizontally, 
increase the replica count of the high-CPU Pod's 
Deployment/StatefulSet. 
▪ 
Resource Limits/Requests: Adjust CPU limits and 
requests for the Pods to better fit the workload. 
▪ 
Optimize Application: Profile the application for 
performance bottlenecks. 
▪ 
Node Autoscaling: If the overall cluster is consistently high 
on CPU, consider configuring Cluster Autoscaler to add 
more nodes. 


***

### Page 18

▪ 
Taints/Tolerations/Affinity: Use these to ensure critical 
workloads get dedicated resources or are spread across 
nodes. 
52. Scenario: Your development team wants to deploy a new service, but they 
need to access a database running in a different namespace. How would you 
enable this communication securely? 
o Answer:  
▪ 
Service Discovery: The database service can be accessed using 
its fully qualified domain name (FQDN): database-service-
name.database-namespace.svc.cluster.local. 
▪ 
Network Policies: Implement Network Policies to explicitly allow 
ingress traffic from the application's namespace to the database 
service's Pods in the database namespace. This ensures only 
authorized communication is allowed. 
▪ 
Service Accounts & RBAC: If the application needs to interact 
with the Kubernetes API to discover the database (less common 
for direct database access), ensure the application's Service 
Account has the necessary RBAC permissions. 
 
VIII. Ecosystem and CNCF Projects (for 2 years experience, some familiarity 
expected) 
53. What is the Cloud Native Computing Foundation (CNCF)? 
o Answer: The CNCF is an open-source foundation that hosts and 
promotes cloud-native technologies, including Kubernetes, Prometheus, 
Envoy, Helm, and many others. Its goal is to make cloud-native computing 
ubiquitous. 
54. Briefly explain the purpose of some popular CNCF projects related to 
Kubernetes (e.g., Prometheus, Grafana, Helm, Istio, Envoy, Cilium). 
o Answer:  
▪ 
Prometheus: Open-source monitoring and alerting toolkit 
designed for reliability and scalability. 
▪ 
Grafana: Open-source platform for analytics and interactive 
visualization. Often used with Prometheus to create dashboards. 


***

### Page 19

▪ 
Helm: The package manager for Kubernetes, used to define, 
install, and upgrade complex Kubernetes applications. 
▪ 
Istio: An open-source service mesh that provides traffic 
management, security, and observability for microservices. 
▪ 
Envoy: An open-source edge and service proxy designed for cloud-
native applications. Used as a sidecar proxy in service meshes like 
Istio. 
▪ 
Cilium: A networking and security solution for Kubernetes that 
uses eBPF to provide high-performance networking, security 
policies, and observability. 
55. Have you worked with any CI/CD pipelines for Kubernetes? If so, describe 
your experience. 
o Answer: (Focus on your actual experience here)  
▪ 
Example: "Yes, I've worked with GitLab CI/CD for deploying 
applications to Kubernetes. We used a pipeline that involved 
stages for building Docker images, pushing them to a registry, and 
then using Helm charts to deploy and update our applications in 
different environments (dev, staging, prod). We leveraged kubectl 
commands within the pipeline scripts for specific tasks like 
checking deployment status and performing rollbacks." 
▪ 
Mention tools like Jenkins, Argo CD, Flux CD, CircleCI, GitHub 
Actions, etc., if you have experience. 
56. What are some challenges you've faced working with Kubernetes in a 
production environment? 
o Answer: (Be honest and show problem-solving skills)  
▪ 
Networking complexities: Troubleshooting NetworkPolicy issues 
or CNI plugin problems. 
▪ 
Resource management: Optimizing CPU/memory requests and 
limits, dealing with OOMKilled Pods. 
▪ 
Stateful application management: Handling persistent storage 
and data integrity for databases. 
▪ 
Security: Implementing RBAC, managing secrets, and 
understanding Pod Security Standards. 


***

### Page 20

▪ 
Debugging: Identifying root causes of issues in a distributed 
system. 
▪ 
Learning curve: The initial complexity of Kubernetes. 
▪ 
Upgrades: Performing cluster upgrades with minimal disruption. 
 
IX. Deeper Dive into Kubernetes Concepts 
57. Explain the lifecycle of a Pod. 
o Answer: A Pod goes through several phases:  
▪ 
Pending: The Pod has been accepted by Kubernetes but one or 
more container images have not been created. 
▪ 
Running: All containers in the Pod have been created and at least 
one container is running, or is in the process of starting or 
restarting. 
▪ 
Succeeded: All containers in the Pod have terminated 
successfully, and will not be restarted. 
▪ 
Failed: All containers in the Pod have terminated, and at least one 
container has terminated in failure (e.g., non-zero exit code or by 
system). 
▪ 
Unknown: The state of the Pod could not be determined. 
58. What are Init Containers and when are they useful? 
o Answer: Init Containers are special containers that run to completion 
before the main application containers in a Pod start. They are useful for:  
▪ 
Setup/Pre-checks: Performing setup tasks like database 
migrations, waiting for a service to be ready, or cloning a Git 
repository. 
▪ 
Configuration: Populating configuration files before the main 
application starts. 
▪ 
Permissions: Setting correct file permissions for volumes. 
▪ 
Ensuring prerequisites: Guaranteeing that external dependencies 
are met before the main application runs. 
59. Explain resource requests and limits in Kubernetes. 
o Answer:  


***

### Page 21

▪ 
Requests: The minimum amount of resources (CPU and memory) 
a container requires. The scheduler uses requests to determine 
which node a Pod can run on. 
▪ 
Limits: The maximum amount of resources a container can 
consume. If a container exceeds its memory limit, it will be 
OOMKilled (Out Of Memory Killed). If it exceeds its CPU limit, it will 
be throttled. 
o Importance: Proper configuration of requests and limits is crucial for 
resource allocation, scheduling efficiency, and preventing resource 
contention. 
60. What is a ReadWriteMany PersistentVolume access mode, and what storage 
solutions support it? 
o Answer: ReadWriteMany allows a volume to be mounted as read-write by 
many nodes simultaneously. This is typically supported by network file 
systems (NFS) or distributed file systems (e.g., CephFS, GlusterFS). Cloud 
providers often offer managed file storage services (e.g., AWS EFS, Azure 
Files, Google Filestore) that support this mode. 
61. How do you perform application-level load balancing within a Kubernetes 
cluster (without using cloud provider load balancers)? 
o Answer:  
▪ 
Service (ClusterIP): The default Service type provides basic 
round-robin load balancing among healthy Pods. 
▪ 
Ingress: For HTTP/HTTPS traffic, an Ingress controller acts as a 
reverse proxy, distributing traffic based on hostnames and paths to 
different Services. 
▪ 
Service Mesh (e.g., Istio, Linkerd): Provides advanced traffic 
management features like intelligent routing, canary deployments, 
A/B testing, circuit breaking, and more granular load balancing 
policies at the application level. 
62. What is the difference between an emptyDir volume and a hostPath volume? 
When would you use each? 
o Answer:  
▪ 
emptyDir: A volume that is created when a Pod is first assigned to 
a node and exists as long as that Pod is running on that node. It's 


***

### Page 22

initially empty and data is lost when the Pod is removed from the 
node.  
▪ 
Use case: Temporary storage for scratch space, caching, or 
inter-container communication within a Pod. 
▪ 
hostPath: Mounts a file or directory from the host node's 
filesystem into a Pod. Data persists across Pod restarts but is tied 
to the specific node.  
▪ 
Use case: Accessing node-level data (e.g., logs, monitoring 
agents), or for applications that need to interact directly 
with the host filesystem (though generally discouraged for 
application data due to portability and persistence issues). 
63. How would you troubleshoot an issue where a Service is not routing traffic to 
any Pods? 
o Answer:  
1. 
kubectl describe service <service-name>: Check the Endpoints field. If it's 
empty, no Pods are matching the Service's selector. 
2. 
kubectl get pods -l <service-selector>: Verify that Pods with the correct labels 
exist and are in a Running state with healthy readiness probes. 
3. 
Check the targetPort in the Service definition and containerPort in the Pod 
definition to ensure they match. 
4. 
Verify network connectivity between the Pods and the Service's cluster IP (e.g., 
kubectl exec into a Pod and try to curl the service IP/port). 
5. 
Check kube-proxy logs on the node where the Service is being accessed for any 
errors. 
64. What is a headless Service? When is it used? 
o Answer: A headless Service does not have a ClusterIP. Instead of acting 
as a load balancer, it provides direct access to the Pod IPs via DNS. When 
you query the DNS name of a headless service, it returns the IP addresses 
of the Pods selected by the service. 
o Use cases:  
▪ 
Stateful applications that need stable network identities for each 
replica (e.g., peer discovery in a distributed database like 
Cassandra). 


***

### Page 23

▪ 
When you want to control load balancing yourself within your 
application. 
65. Explain tolerations and nodeSelector in Pod scheduling. 
o Answer:  
▪ 
nodeSelector: A simple way to constrain Pods to nodes with 
specific labels. The Pod will only be scheduled on nodes that have 
all the specified labels. It's a hard requirement. 
▪ 
tolerations: Works with taints. A Pod with tolerations can be 
scheduled on a node that has a matching taint. Without the 
toleration, the Pod would not be scheduled on that tainted node. 
It's about allowing scheduling on tainted nodes, not forcing it. 
 
X. Scenario-Based Questions (for 2 years experience, focus on practical 
application) 
66. You have a legacy application that requires a specific kernel module to be 
loaded on the host. How would you deploy this application in Kubernetes? 
o Answer: This is a tricky one as Kubernetes abstracts away the host OS.  
▪ 
Option 1 (Not ideal for production): Use a hostPath volume to 
mount the kernel module directory into the Pod, and potentially 
run an initContainer to load the module (if allowed by security 
policies). This ties the Pod to specific nodes. 
▪ 
Option 2 (Better): Re-architect the application to not require host 
kernel modules if possible, or deploy it on bare metal/VMs outside 
Kubernetes. 
▪ 
Option 3 (Advanced/Specific): If the kernel module is part of a 
standard distribution and can be enabled, use DaemonSets to 
ensure the module is loaded on all relevant nodes. For more 
complex scenarios, consider using a Kubernetes Operator that can 
manage node-level configurations. 
▪ 
Most practical for a legacy app: Deploy the application on 
dedicated nodes with the necessary kernel module pre-loaded, 
and use nodeSelector or nodeAffinity to schedule the Pods on 
those nodes. 
67. Your company is moving from a monolithic application to microservices on 
Kubernetes. What are some key design considerations for this migration? 


***

### Page 24

o Answer:  
▪ 
Containerization: Ensuring all services are properly containerized 
(Dockerfiles, optimized images). 
▪ 
Service Decomposition: Breaking down the monolith into 
manageable, independent microservices. 
▪ 
API Design: Defining clear API contracts between microservices. 
▪ 
Service Discovery: Leveraging Kubernetes Services for inter-
service communication. 
▪ 
Configuration Management: Using ConfigMaps and Secrets for 
dynamic configuration. 
▪ 
State Management: Identifying stateful components and using 
StatefulSets or external databases. 
▪ 
Networking: Designing appropriate network policies for security. 
▪ 
Logging and Monitoring: Implementing centralized logging and 
monitoring for distributed services. 
▪ 
CI/CD Pipeline: Automating deployments with tools like Helm and 
GitOps. 
▪ 
Scalability: Designing services to be horizontally scalable. 
▪ 
Resilience: Implementing liveness/readiness probes, retries, 
circuit breakers (potentially with a service mesh). 
▪ 
Security: Implementing RBAC, Pod Security Standards, and image 
scanning. 
68. You need to restrict network access to a sensitive database Pod, allowing 
only specific application Pods to connect to it. How would you achieve this? 
o Answer: Use Kubernetes Network Policies.  
1. 
Define a NetworkPolicy in the database's namespace. 
2. 
Use podSelector to target the database Pods. 
3. 
Specify ingress rules with from clauses that use podSelector (and optionally 
namespaceSelector) to allow traffic only from the specific application Pods. 
4. 
Ensure your CNI plugin supports Network Policies (e.g., Calico, Cilium). 
69. How would you handle application configuration that differs between 
development, staging, and production environments in Kubernetes? 


***

### Page 25

o Answer:  
▪ 
ConfigMaps and Secrets: Store environment-specific 
configuration in separate ConfigMaps and Secrets. 
▪ 
Helm Charts: Use Helm charts with values.yaml files. Create 
separate values.yaml files (e.g., values-dev.yaml, values-
staging.yaml, values-prod.yaml) for each environment. When 
deploying with Helm, specify the appropriate values file (helm 
install -f values-prod.yaml ...). 
▪ 
Kustomize: A native Kubernetes configuration management tool 
that allows you to customize raw YAML files without templating. 
You can define a base manifest and then create overlays for each 
environment to patch specific values. 
▪ 
Environment Variables: Inject environment-specific values as 
environment variables into containers. 
70. A developer reports that their Pod cannot write to its mounted volume. What 
steps would you take to diagnose this? 
o Answer:  
1. 
Check Pod events: kubectl describe pod <pod-name> for any volume mount 
errors. 
2. 
Check PVC/PV status: kubectl get pvc <pvc-name> and kubectl describe pvc 
<pvc-name>, then check the associated kubectl describe pv <pv-name>. Ensure the 
PVC is Bound to a PV and the PV is available. 
3. 
Check StorageClass: If dynamic provisioning is used, ensure the StorageClass 
is correctly defined and the provisioner is working. 
4. 
Check underlying storage: Verify the actual storage (e.g., NFS server, cloud 
disk) is healthy and accessible from the node. 
5. 
Check node logs: On the node where the Pod is running, check kubelet logs for 
volume mounting issues. 
6. 
Permissions within the container: kubectl exec -it <pod-name> -- ls -ld 
/path/to/mount. Check the permissions of the mounted directory inside the container. 
The application might not have write permissions. You might need to adjust the 
securityContext in the Pod definition (e.g., fsGroup, runAsUser). 
7. 
Selinux/AppArmor (on host): If present, these security modules on the node 
might be preventing access. 


***

### Page 26

 
XI. Advanced Kubernetes Concepts 
71. What is an Admission Controller in Kubernetes? Give an example. 
o Answer: Admission controllers are plugins that intercept requests to the 
Kubernetes API server after authentication and authorization but before 
the object is persisted in etcd. They can mutate (change) or validate 
requests. 
o Example:  
▪ 
LimitRanger: Enforces resource limits on Pods within a 
namespace. 
▪ 
ResourceQuota: Ensures that namespaces don't exceed their 
allocated resource quotas. 
▪ 
PodSecurityPolicy (deprecated, replaced by PSS): Used to 
enforce security policies on Pods. 
▪ 
MutatingAdmissionWebhook/ValidatingAdmissionWebhook: 
Allows you to define custom admission controllers using 
webhooks. 
72. How do you manage certificates and TLS in Kubernetes? 
o Answer:  
▪ 
Kubernetes Secrets: You can store TLS certificates as Kubernetes 
Secrets of type kubernetes.io/tls. 
▪ 
Ingress: Ingress resources can use these TLS Secrets to terminate 
SSL/TLS at the Ingress Controller. 
▪ 
Cert-manager: A popular open-source tool that automates the 
issuance and renewal of TLS certificates from various issuing 
sources (e.g., Let's Encrypt) within Kubernetes. It integrates with 
Ingress and creates/manages TLS Secrets. 
▪ 
Service Mesh (e.g., Istio): Service meshes can manage mTLS 
(mutual TLS) between services, providing strong identity and 
encryption. 
73. Explain Kubernetes Operators in more detail. What problems do they solve? 
o Answer: Kubernetes Operators are a method of packaging, deploying, 
and managing a Kubernetes application. They extend the Kubernetes API 


***

### Page 27

to manage complex stateful applications. An Operator is essentially a 
Custom Controller that understands the domain-specific knowledge of 
an application (like a database or a message queue) and automates its 
operational tasks. 
o Problems they solve: Automating day-2 operations for complex 
applications, including:  
▪ 
Deployment and upgrades 
▪ 
Scaling 
▪ 
Backup and restore 
▪ 
Failure recovery 
▪ 
Cluster rebalancing 
▪ 
Applying security patches 
▪ 
Handling application-specific configurations 
74. What is kubeconfig and how is it used? 
o Answer: kubeconfig is a YAML file that contains information about your 
Kubernetes clusters, users, and contexts. It allows kubectl (and other 
Kubernetes clients) to connect to and authenticate with different 
Kubernetes clusters. It typically resides at ~/.kube/config. 
75. How does Kubernetes handle garbage collection? 
o Answer: Kubernetes performs garbage collection to clean up resources 
that are no longer needed. This includes:  
▪ 
Finished Pods/Jobs: Deleting Pods associated with completed 
Jobs. 
▪ 
Orphaned Objects: Deleting objects that are no longer referenced 
by their owners (e.g., a ReplicaSet deleting Pods that no longer 
match its selector). 
▪ 
Unused images and containers: kubelet regularly cleans up old 
images and containers on the nodes. 
▪ 
kube-controller-manager: Contains a garbage collector that 
cleans up various objects. 
76. What is a Multi-Cluster Kubernetes setup? Why would you need one? 


***

### Page 28

o Answer: A multi-cluster Kubernetes setup involves managing multiple 
independent Kubernetes clusters. 
o Reasons for using it:  
▪ 
High Availability/Disaster Recovery: Distributing workloads 
across different geographical regions or cloud providers to ensure 
business continuity. 
▪ 
Geographical Proximity/Latency: Deploying applications closer 
to users in different regions. 
▪ 
Regulatory Compliance/Data Sovereignty: Meeting data 
residency requirements. 
▪ 
Isolation: Providing strong isolation for different teams or sensitive 
workloads. 
▪ 
Hybrid Cloud: Running workloads across on-premise and cloud 
environments. 
▪ 
Resource Limits: Overcoming the scaling limits of a single cluster. 
77. What is etcd in Kubernetes? What are its key characteristics? 
o Answer: etcd is a distributed, consistent, and highly available key-value 
store used by Kubernetes as its primary datastore. It stores all cluster 
state, configuration data, and metadata (e.g., Pod definitions, Service 
definitions, ConfigMaps, Secrets). 
o Key characteristics:  
▪ 
Consistency: Uses the Raft consensus algorithm to ensure data 
consistency across all members. 
▪ 
High Availability: Designed to be highly available with multiple 
instances. 
▪ 
Distributed: Can run across multiple machines. 
▪ 
Key-value store: Simple API for storing and retrieving data. 
▪ 
Watches: Allows clients to watch for changes to keys, enabling 
Kubernetes components to react to state changes. 
78. How does the Kubernetes Scheduler work? What factors does it consider? 
o Answer: The Kube-scheduler is responsible for assigning newly created 
Pods to available nodes. It considers various factors during the 
scheduling process:  


***

### Page 29

▪ 
Resource requirements: CPU, memory, GPU, etc., requested by 
the Pod. 
▪ 
Node capacity: Available resources on each node. 
▪ 
Node selectors, taints, tolerations: Constraints defined on Pods 
and nodes. 
▪ 
Node affinity/anti-affinity: Preferences for scheduling Pods on 
specific nodes or avoiding certain nodes. 
▪ 
Pod affinity/anti-affinity: Preferences for co-locating or 
separating Pods from other Pods. 
▪ 
Quality of Service (QoS) classes: Ensuring critical Pods get 
priority. 
▪ 
Volume requirements: Availability of suitable PersistentVolumes. 
▪ 
Port conflicts: Avoiding port conflicts on a node. 
 
XII. Miscellaneous and Best Practices 
79. What are some best practices for writing Dockerfiles for Kubernetes 
applications? 
o Answer:  
▪ 
Use a minimal base image: (e.g., alpine, distroless) to reduce 
image size and attack surface. 
▪ 
Multi-stage builds: Separate build dependencies from runtime 
dependencies to create smaller final images. 
▪ 
Cache layers effectively: Place frequently changing instructions 
later in the Dockerfile. 
▪ 
Don't run as root: Use USER instruction to run as a non-root user. 
▪ 
Copy only necessary files: Use .dockerignore to exclude 
irrelevant files. 
▪ 
Expose ports: Use EXPOSE instruction. 
▪ 
CMD/ENTRYPOINT: Define how the application starts. 
▪ 
Environment variables: Use for dynamic configuration. 


***

### Page 30

▪ 
Scan images for vulnerabilities: Integrate image scanning into 
CI/CD. 
80. How do you secure your Kubernetes cluster at the image level? 
o Answer:  
▪ 
Image scanning: Use tools (e.g., Trivy, Clair, Anchore) to scan 
container images for known vulnerabilities. 
▪ 
Trusted registries: Use private, trusted container registries. 
▪ 
Image signing and verification: Ensure images come from trusted 
sources and haven't been tampered with. 
▪ 
Least privilege: Build images with minimal necessary privileges. 
81. What is the significance of the targetPort and port fields in a Kubernetes 
Service? 
o Answer:  
▪ 
port: The port that the Service itself exposes within the cluster. 
Other services or external clients will connect to this port. 
▪ 
targetPort: The port on the Pod(s) that the Service will forward 
traffic to. This is the port your application within the container is 
listening on. 
o Significance: port allows the Service to have a stable external port, while 
targetPort allows flexibility in how the application inside the Pod is 
configured, decoupling the service port from the actual container port. 
82. How do you effectively manage secrets in Kubernetes? 
o Answer:  
▪ 
Use Kubernetes Secrets: For storing sensitive data. 
▪ 
Avoid storing secrets in Git: Never commit plain text secrets to 
version control. 
▪ 
External Secret Management: Integrate with external secret 
management systems (e.g., HashiCorp Vault, AWS Secrets 
Manager, Azure Key Vault, Google Secret Manager) using tools like 
ExternalSecrets Operator or Secrets Store CSI Driver. 
▪ 
RBAC: Restrict access to Secrets using RBAC policies. 


***

### Page 31

▪ 
Encryption at rest and in transit: Ensure etcd is encrypted and all 
communication is TLS-encrypted. 
▪ 
Rotate secrets regularly. 
▪ 
Pod Security Standards: Apply PSS to restrict how Pods can 
access secrets. 
83. What is kube-proxy and what are its modes of operation? 
o Answer: kube-proxy is a network proxy that runs on each node in the 
cluster. It's responsible for implementing the Kubernetes Service 
abstraction by maintaining network rules on nodes and enabling network 
communication to Pods from inside or outside of the cluster. 
o Modes of operation:  
▪ 
iptables (default): Uses iptables rules to perform load balancing 
and network address translation (NAT). Efficient for a large number 
of services. 
▪ 
ipvs: Uses IP Virtual Server (IPVS) for load balancing, which offers 
better performance for high-traffic services. 
▪ 
userspace (deprecated): The oldest and slowest mode, which 
involves kube-proxy acting as a proxy in userspace. 
84. Explain the concept of Immutable fields in Kubernetes API objects. 
o Answer: Certain fields in Kubernetes API objects are immutable after 
creation. This means once the object is created, you cannot change the 
value of these fields directly. If you need to change an immutable field, 
you typically have to delete and recreate the object (e.g., changing the 
selector on a Service, or the volumeMounts on a Pod). This is done to 
maintain consistency and prevent unexpected behavior. 
85. What is kubectl drain used for? 
o Answer: kubectl drain is used to gracefully evict all Pods from a node, 
preparing it for maintenance (e.g., kernel upgrade, hardware 
replacement). It marks the node as unschedulable and then evicts Pods, 
respecting any Pod Disruption Budgets (PDBs). 
86. How would you troubleshoot network latency issues between Pods in a 
Kubernetes cluster? 
o Answer:  
1. 
Identify affected Pods/Services: Is it all traffic, or specific services? 


***

### Page 32

2. 
Check CNI plugin: Verify the health and logs of your CNI plugin (e.g., Calico, 
Flannel). Are there any errors or warnings? 
3. 
Node network health: Check network interface statistics, CPU utilization, and 
general network performance on the affected nodes. 
4. 
Underlying network infrastructure: Is there any latency at the host or cloud 
provider network level? 
5. 
Service Mesh (if applicable): If using a service mesh, check its components 
and configuration for any issues. 
6. 
iperf or netperf: Deploy temporary Pods with network benchmarking tools to 
measure latency and bandwidth between them. 
7. 
tcpdump: Use kubectl debug or kubectl exec to run tcpdump inside Pods to 
inspect network traffic. 
8. 
DNS resolution: Is DNS lookup adding latency? 
9. 
Application issues: Is the latency caused by the application itself (e.g., 
inefficient database queries, excessive logging)? 
87. What are PreStop hooks and PostStart hooks in a container lifecycle? 
o Answer:  
▪ 
PreStop hook: Executed immediately before a container is 
terminated due to an API request or a management event (e.g., 
graceful shutdown, resource contention). It's a blocking call, 
meaning the container will not be terminated until the hook 
completes. Useful for graceful shutdowns, flushing logs, or 
completing in-flight requests. 
▪ 
PostStart hook: Executed immediately after a container is 
created. It's a non-blocking call. Useful for initial setup tasks that 
need to run after the container starts but before the main 
application logic takes over (e.g., registering with a service 
registry). 
88. How does Kubernetes handle resource limits and requests on a Pod with 
multiple containers? 
o Answer: Resource requests and limits are defined per container within a 
Pod. The scheduler sums up the requests of all containers in a Pod to find 
a node with sufficient aggregate resources. Limits are also applied per 
container. If one container exceeds its limit, only that specific container is 
affected (throttled or killed), not the entire Pod. 


***

### Page 33

89. What is a mutating webhook and a validating webhook? 
o Answer: These are types of Admission Webhooks that allow you to extend 
the Kubernetes API with custom logic.  
▪ 
MutatingAdmissionWebhook: Can modify or "mutate" the 
objects before they are stored in etcd. For example, injecting 
sidecar containers, adding labels, or setting default values. 
▪ 
ValidatingAdmissionWebhook: Can only validate requests and 
either allow or deny them. It cannot change the objects. For 
example, enforcing specific security policies or preventing certain 
configurations. 
90. Explain the concept of VolumeClaimTemplates in StatefulSets. 
o Answer: VolumeClaimTemplates are used in StatefulSets to 
automatically provision PersistentVolumeClaims for each replica of the 
StatefulSet. Each Pod managed by the StatefulSet will get its own unique 
PVC based on the template. This ensures that each stateful Pod has its 
own dedicated, persistent storage. 
91. What is the difference between a Job and a CronJob? 
o Answer:  
▪ 
Job: Creates one or more Pods and ensures that a specified 
number of them successfully terminate. Jobs are used for batch 
processing or one-off tasks. 
▪ 
CronJob: Manages Jobs on a repeating, time-based schedule (like 
cron on a Linux system). It creates Job objects at specified 
intervals. 
92. How can you ensure high availability of the Kubernetes control plane? 
o Answer:  
▪ 
Multiple Master Nodes: Run multiple kube-apiserver instances 
behind a load balancer. 
▪ 
Distributed etcd: Run etcd in a highly available, clustered 
configuration (e.g., 3 or 5 members). 
▪ 
Redundant Controllers/Schedulers: kube-controller-manager 
and kube-scheduler can be run as multiple instances, with only 
one active at a time (leader election). 
▪ 
Backup and Restore: Regularly back up etcd data. 


***

### Page 34

▪ 
Cloud Provider Managed Services: Utilize managed Kubernetes 
services (EKS, GKE, AKS) where the cloud provider manages 
control plane HA. 
93. What is kubeadm? 
o Answer: kubeadm is a tool that helps you bootstrap a minimum viable 
Kubernetes cluster. It handles the provisioning of control plane 
components, certificates, and setting up worker nodes to join the cluster. 
It's not a complete cluster lifecycle manager but a good starting point for 
self-managed clusters. 
94. Describe a situation where you would use a ServiceAccount and a 
ClusterRoleBinding together. 
o Answer:  
▪ 
Scenario: You have an application running in a Pod that needs to 
list all Nodes in the cluster for monitoring purposes. 
▪ 
Solution:  
1. Create a ServiceAccount for your application Pod. 
2. Create a ClusterRole that defines permissions to get and 
list the nodes resource. 
3. Create a ClusterRoleBinding that binds this ClusterRole to 
your ServiceAccount. 
▪ 
By using a ClusterRoleBinding, you grant the 
ServiceAccount permissions across the entire cluster, 
allowing it to see all nodes, regardless of the namespace 
the application Pod runs in. 
95. What is kubectl diff? 
o Answer: kubectl diff shows a diff between the current live configuration of 
a Kubernetes object and a potential new configuration from a local file. 
It's a useful tool for previewing changes before applying them, helping to 
prevent unintended modifications. 
96. How would you secure a Kubernetes cluster from a network perspective 
(beyond Network Policies)? 
o Answer:  


***

### Page 35

▪ 
Firewalls/Security Groups: Configure network firewalls (e.g., 
cloud provider security groups) to restrict ingress/egress traffic 
to/from nodes and control plane components. 
▪ 
Private Endpoints for API Server: Access the Kubernetes API 
server only through private network endpoints if available. 
▪ 
VPC Peering/VPN: Securely connect Kubernetes clusters to other 
private networks. 
▪ 
Egress Network Policies: Control outbound traffic from Pods. 
▪ 
Service Mesh: Implement mTLS and granular traffic control. 
▪ 
IDS/IPS: Deploy intrusion detection/prevention systems at the 
network edge. 
97. What is the containerRuntimeInterface (CRI)? 
o Answer: CRI is a plugin interface that enables Kubernetes to use different 
container runtimes (like containerd, CRI-O, Docker's dockershim - now 
deprecated) to run containers. It provides a gRPC API for the kubelet to 
interact with the container runtime. This abstraction allows Kubernetes to 
be independent of the specific container runtime used. 
98. How would you implement blue/green deployments in Kubernetes? 
o Answer:  
1. 
Two Deployments: Have two separate Deployments: "blue" (current version) 
and "green" (new version), each with its own set of Pods. 
2. 
Service: A single Kubernetes Service points to the "blue" deployment. 
3. 
Switch Traffic: To switch to "green," update the Service's selector to point to the 
"green" deployment's labels. 
4. 
Rollback: If issues arise with "green," simply revert the Service's selector back to 
"blue." 
▪ 
This approach offers zero downtime and an immediate rollback 
capability, but it doubles resource consumption during the switch. 
99. How would you implement canary deployments in Kubernetes? 
o Answer:  
1. 
Two Deployments: One for the stable version (main) and another for the canary 
(new version). 


***

### Page 36

2. 
Ingress/Service Mesh: Use an Ingress controller or a service mesh (e.g., Istio, 
Linkerd) to manage traffic routing. 
3. 
Gradual Traffic Shifting: Configure the Ingress/Service Mesh to gradually shift a 
small percentage of traffic (e.g., 5-10%) to the canary deployment. 
4. 
Monitoring: Closely monitor metrics (errors, latency, performance) for the 
canary version. 
5. 
Increase Traffic/Rollout: If the canary performs well, gradually increase the 
traffic to the canary until 100%. Then, the old stable deployment can be scaled down 
and removed. 
6. 
Rollback: If issues are detected, immediately revert the traffic split to 0% to the 
canary. 
100. 
What is the kubectl debug command? When would you use it? 
• 
Answer: kubectl debug is a beta command in kubectl (as of recent versions) that 
allows you to create an ephemeral debug container in an existing Pod or create a 
new debug Pod from an existing Pod or node. 
• 
Use cases:  
o Troubleshooting running Pods: Attach a debugger or run diagnostic tools 
without restarting the main application container. 
o Inspecting a crashlooping container: Get a shell into a container that's 
constantly restarting. 
o Debugging nodes: Create a debug Pod on a specific node to inspect its 
filesystem or processes. 
o Running network diagnostics: Use tools like tcpdump inside a debug 
container. 
 


***

# Kubernetes — Easy Interview Questions

15+ foundational questions covering core concepts every Kubernetes practitioner must know.

***

**1. What is Kubernetes and what problem does it solve?**

Kubernetes is an open-source container orchestration platform that automates the deployment, scaling, self-healing, and management of containerized workloads across a cluster of machines.

Without Kubernetes, running containers in production requires manual intervention for: restarting crashed containers, distributing containers across machines, scaling up/down based on traffic, and rolling out new versions without downtime. Kubernetes automates all of this via a declarative model — you describe the desired state, and the control plane continuously reconciles actual state to match it.

***

**2. What is a Pod, and why is it the smallest deployable unit?**

A Pod is the smallest deployable unit in Kubernetes — it wraps one or more containers that share the same:
- Network namespace (same IP address, communicate via `localhost`)
- Storage (shared volumes)
- Process namespace (optionally)

It is the smallest unit because Kubernetes manages _groups_ of co-located, co-scheduled containers as a unit. You cannot schedule a single container independently — it must live inside a Pod.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
  - name: web
    image: nginx:1.25
    ports:
    - containerPort: 80
```

***

**3. What is the difference between a Deployment and a bare Pod?**

| Aspect | Pod | Deployment |
|---|---|---|
| Self-healing | No — if Pod dies, it's gone | Yes — ReplicaSet recreates the Pod |
| Rolling updates | No | Yes — controlled rollout and rollback |
| Scaling | Manual only | Declarative via `replicas` field |
| Use in production | Almost never directly | Always for stateless workloads |

A Deployment manages a ReplicaSet, which in turn manages Pods. The Deployment controller watches for drift and reconciles.

***

**4. What is a Service, and why is it needed?**

A Service provides a stable DNS name and virtual IP for a set of Pods selected by labels. Pods are ephemeral — they get new IPs when restarted or rescheduled. A Service decouples consumers from the transient Pod IPs.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: backend
spec:
  selector:
    app: backend         # matches pods with this label
  ports:
  - port: 80
    targetPort: 8080
```

DNS: `backend.production.svc.cluster.local`

***

**5. What are the four types of Kubernetes Services?**

| Type | Reachability | Use Case |
|---|---|---|
| `ClusterIP` (default) | Within cluster only | Internal service-to-service |
| `NodePort` | External via `<NodeIP>:<NodePort>` (30000-32767) | Dev/testing, on-prem without LB |
| `LoadBalancer` | External via cloud LB IP | Production external services |
| `ExternalName` | CNAME redirect to external DNS | Integrate external services into cluster DNS |

***

**6. What is a Namespace, and when do you use one?**

A Namespace is a virtual cluster within a Kubernetes cluster — it provides scope for resource names and enables isolation between teams or environments.

Common uses:
- Environment separation: `dev`, `staging`, `production`
- Team isolation: `team-payments`, `team-search`
- Applying RBAC policies per team
- Setting ResourceQuotas per team

Default namespaces: `default`, `kube-system` (control plane), `kube-public`, `kube-node-lease`.

```bash
kubectl create namespace production
kubectl get pods -n production
kubectl config set-context --current --namespace=production
```

***

**7. What is the difference between a ConfigMap and a Secret?**

| Aspect | ConfigMap | Secret |
|---|---|---|
| Data type | Non-sensitive config | Sensitive data (passwords, tokens, certs) |
| Storage | Plain text in etcd | Base64-encoded in etcd (encrypt-at-rest recommended) |
| Usage | Env vars, volume files | Env vars, volume files, imagePullSecrets |

```yaml
# ConfigMap
kubectl create configmap app-config --from-literal=DB_HOST=postgres

# Secret
kubectl create secret generic db-creds --from-literal=password=secret123
```

> [!CAUTION]
> Base64 is encoding, not encryption. Enable etcd encryption-at-rest and use external secret managers (Vault, AWS Secrets Manager) for production.

***

**8. What is `kubectl apply` vs. `kubectl create`?**

| Command | Behavior |
|---|---|
| `kubectl create` | Creates a resource; fails if it already exists |
| `kubectl apply` | Creates or updates a resource; idempotent |

`apply` tracks the last applied configuration via the `kubectl.kubernetes.io/last-applied-configuration` annotation and computes a three-way merge. Use `apply` for GitOps workflows where you re-apply the same manifests repeatedly.

```bash
kubectl apply -f deployment.yaml           # idempotent
kubectl apply --server-side -f deployment.yaml  # server-side apply (recommended)
```

***

**9. What is a liveness probe vs. a readiness probe?**

**Liveness probe** — "Is the container alive?" If it fails, kubelet restarts the container. Use to detect deadlocks or hung processes.

**Readiness probe** — "Is the container ready to serve traffic?" If it fails, the Pod's IP is removed from the Service endpoints. The container is NOT restarted. Use for slow-starting apps or temporary backpressure.

**Startup probe** — One-time check during startup. Prevents liveness from killing a slow-starting app. Disables liveness/readiness until it succeeds.

```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
  initialDelaySeconds: 10
  periodSeconds: 10
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  periodSeconds: 5

startupProbe:
  httpGet:
    path: /healthz
    port: 8080
  failureThreshold: 30    # 30 × 10s = 5 min budget
  periodSeconds: 10
```

***

**10. What is a DaemonSet?**

A DaemonSet ensures exactly one Pod runs on every node (or a defined subset). When a new node joins the cluster, the DaemonSet automatically starts the Pod on it. When a node is removed, the Pod is garbage-collected.

Common uses:
- Log shippers: Fluent Bit, Fluentd
- Monitoring exporters: Prometheus Node Exporter, Datadog agent
- CNI plugins: Calico, Cilium
- Security agents: Falco, Sysdig

```yaml
kind: DaemonSet
spec:
  selector:
    matchLabels:
      app: node-exporter
  template:
    spec:
      containers:
      - name: node-exporter
        image: prom/node-exporter:v1.7.0
```

***

**11. What is a StatefulSet, and when do you use it over a Deployment?**

| Feature | Deployment | StatefulSet |
|---|---|---|
| Pod names | Random suffix: `app-7d8c4f` | Ordered: `app-0`, `app-1`, `app-2` |
| Storage | Pods share one PVC (or none) | Each pod gets its own PVC via `volumeClaimTemplates` |
| Scaling order | Parallel | Sequential (0→N up, N→0 down) |
| DNS | Single Service | Headless Service: `app-0.svc.ns.svc.cluster.local` |

Use StatefulSets for: databases (MySQL, PostgreSQL, MongoDB, Cassandra), message brokers (Kafka, RabbitMQ), any workload that needs stable identity and per-pod storage.

***

**12. What is a PersistentVolume (PV) and PersistentVolumeClaim (PVC)?**

**PV (PersistentVolume)** — A piece of storage provisioned by an admin or dynamically by a StorageClass. Cluster-scoped.

**PVC (PersistentVolumeClaim)** — A request for storage by a Pod. Namespace-scoped. Kubernetes binds the PVC to the best-matching PV.

**StorageClass** — Defines the provisioner, parameters, and binding mode. Enables dynamic provisioning — no need to pre-create PVs.

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: db-storage
spec:
  accessModes: [ReadWriteOnce]
  storageClassName: fast-ssd
  resources:
    requests:
      storage: 50Gi
```

***

**13. What are resource requests and limits?**

**Requests** — The minimum guaranteed amount of CPU/memory a container needs. The scheduler uses requests to find a node with enough capacity.

**Limits** — The maximum a container can consume. Exceeding CPU limit → throttling. Exceeding memory limit → OOMKill (exit code 137).

```yaml
resources:
  requests:
    cpu: "250m"       # 250 millicores
    memory: "256Mi"
  limits:
    cpu: "1"
    memory: "512Mi"
```

QoS implications:
- `requests == limits` → `Guaranteed` QoS (highest priority, last evicted)
- `requests < limits` → `Burstable`
- No requests or limits → `BestEffort` (first evicted)

***

**14. What is a rolling update strategy, and how do `maxUnavailable` and `maxSurge` work?**

A rolling update replaces old Pods with new ones incrementally — no downtime.

- `maxUnavailable` — Maximum number (or %) of Pods that can be unavailable during the update. Default: `25%`.
- `maxSurge` — Maximum number (or %) of extra Pods that can exist above the desired replica count. Default: `25%`.

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxUnavailable: 1
    maxSurge: 1
```

With 4 replicas: at most 3 Pods unavailable at once; at most 5 Pods running at once.

***

**15. What is `kubectl port-forward`, and when do you use it?**

`port-forward` creates a tunnel from your local machine's port to a port on a Pod or Service inside the cluster — without exposing the service publicly.

```bash
kubectl port-forward pod/my-pod 8080:80
kubectl port-forward svc/my-service 5432:5432 -n production
```

Use cases:
- Debug a Pod's HTTP endpoint locally
- Access a database inside the cluster without a NodePort/LoadBalancer
- Test an internal service from your laptop

***

**16. What are Node taints and Pod tolerations?**

A **taint** on a node repels Pods that don't explicitly tolerate it. A **toleration** on a Pod allows it to be scheduled on nodes with matching taints.

```bash
# Taint a node (dedicated to GPU workloads)
kubectl taint nodes gpu-node-1 dedicated=gpu:NoSchedule

# Pod toleration
tolerations:
- key: "dedicated"
  operator: "Equal"
  value: "gpu"
  effect: "NoSchedule"
```

Taint effects:
- `NoSchedule` — New pods without the toleration are not scheduled
- `PreferNoSchedule` — Soft version of NoSchedule
- `NoExecute` — Also evicts running pods that don't tolerate it

***

**17. What happens internally when you run `kubectl apply -f deployment.yaml`?**

1. `kubectl` reads the YAML and sends a `PATCH` (or `PUT`) request to the API server
2. API server authenticates and authorizes the request (RBAC)
3. Mutating admission webhooks can modify the object (e.g., inject sidecar, set defaults)
4. Schema validation runs against the OpenAPI spec
5. Validating admission webhooks check policy compliance
6. API server persists the desired state to etcd
7. The Deployment Controller detects a new/changed Deployment → creates/updates a ReplicaSet
8. The ReplicaSet Controller detects it needs N pods → creates Pod objects
9. The Scheduler sees unscheduled pods → selects nodes → updates `pod.spec.nodeName`
10. kubelet on the selected node sees the pod assignment → pulls the image via containerd → starts the container
# Kubernetes — Medium Interview Questions

15+ intermediate questions covering operational patterns, autoscaling, RBAC, networking, and stateful workloads.

***

**1. How does the Kubernetes scheduler decide where to place a Pod?**

Two-phase process:

**Phase 1 — Filtering (Predicates):** Eliminates nodes that cannot run the pod:
- Insufficient CPU or memory (vs. pod `requests`)
- Taint/toleration mismatch
- `nodeSelector` or node affinity mismatch
- Port conflict on the target node
- PVC zone incompatibility
- Node not in `Ready` state

**Phase 2 — Scoring (Priorities):** Ranks remaining nodes. Default scoring functions:
- `LeastAllocated` — Prefer nodes with most free resources (spreads workloads)
- `NodeAffinityPriority` — Weights preferred affinity matches
- `ImageLocality` — Prefer nodes already holding the container image
- `InterPodAffinity` — Co-locate or spread based on pod affinity rules
- `TopologySpreadConstraint` — Balance across failure domains

Node with the highest aggregate score is selected. On a tie, a random node is chosen.

***

**2. What are Kubernetes QoS classes, and how do they affect eviction?**

QoS class is automatically derived from resource configuration:

| QoS Class | Condition | Eviction Priority |
|---|---|---|
| `Guaranteed` | All containers have `requests == limits` for both CPU and memory | Last — never evicted under resource pressure |
| `Burstable` | At least one container has `requests < limits` or only memory/CPU set | Evicted under memory pressure if over their request |
| `BestEffort` | No requests or limits set | First evicted |

The kubelet evicts pods in BestEffort → Burstable (sorted by how far over request) → Guaranteed order when the node is under memory pressure.

> [!IMPORTANT]
> For latency-sensitive production workloads, set `requests == limits` (Guaranteed). This also prevents CPU throttling because CPU limit equals what the CFS scheduler guarantees.

***

**3. What is a ResourceQuota, and what is a LimitRange?**

**ResourceQuota** — Caps the total amount of resources that can be consumed in a namespace:

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: production-quota
  namespace: production
spec:
  hard:
    requests.cpu: "10"
    requests.memory: 20Gi
    limits.cpu: "20"
    limits.memory: 40Gi
    pods: "50"
    services: "10"
    persistentvolumeclaims: "20"
```

**LimitRange** — Sets default requests/limits for containers that don't specify them, and enforces min/max bounds:

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: default-limits
  namespace: production
spec:
  limits:
  - type: Container
    default:
      cpu: "500m"
      memory: "256Mi"
    defaultRequest:
      cpu: "100m"
      memory: "128Mi"
    max:
      cpu: "4"
      memory: "4Gi"
    min:
      cpu: "50m"
      memory: "64Mi"
```

If a namespace has a ResourceQuota, every pod MUST have requests set (LimitRange provides them when not specified).

***

**4. How does Horizontal Pod Autoscaling (HPA) work?**

HPA polls the Metrics API every 15s (default) and computes:

```
desiredReplicas = ceil(currentReplicas × (currentMetricValue / desiredMetricValue))
```

Example: 3 replicas, current CPU utilization 80%, target 50%:
`ceil(3 × 80/50) = ceil(4.8) = 5`

Requirements:
- `metrics-server` must be installed for CPU/memory metrics
- Pods must have `resources.requests.cpu` set (HPA uses it as the denominator)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api
  minReplicas: 2
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 60
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300  # Prevent flapping
```

***

**5. What is the difference between RBAC Roles and ClusterRoles?**

| Object | Scope | Can grant access to |
|---|---|---|
| `Role` | Single namespace | Resources in that namespace only |
| `ClusterRole` | Cluster-wide | Cluster-scoped resources (nodes, PVs, CRDs) OR resources in any namespace |
| `RoleBinding` | Namespace | Binds a Role or ClusterRole to subjects within the namespace |
| `ClusterRoleBinding` | Cluster | Binds a ClusterRole to subjects globally |

Common pattern — grant read-only access to pods in one namespace:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: production
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods", "pods/log"]
  verbs: ["get", "list", "watch"]
***
kind: RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: dev-pod-reader
  namespace: production
subjects:
- kind: User
  name: alice
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

***

**6. What are Ingress Controllers, and how does Ingress routing work?**

An **Ingress resource** defines L7 routing rules (host/path → service). An **Ingress Controller** is a pod that watches Ingress resources and configures the underlying proxy (nginx, Traefik, HAProxy, AWS ALB).

```yaml
kind: Ingress
metadata:
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  tls:
  - hosts: [api.example.com]
    secretName: api-tls
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /v1
        pathType: Prefix
        backend:
          service:
            name: api-v1
            port:
              number: 80
      - path: /v2
        pathType: Prefix
        backend:
          service:
            name: api-v2
            port:
              number: 80
```

A single Ingress Controller with one cloud load balancer can route to hundreds of services, compared to provisioning a new cloud LB per service.

***

**7. What are PVC access modes, and which storage solutions support ReadWriteMany?**

| Access Mode | Shorthand | Semantics |
|---|---|---|
| ReadWriteOnce | RWO | Single node mounts read-write |
| ReadOnlyMany | ROX | Multiple nodes mount read-only |
| ReadWriteMany | RWX | Multiple nodes mount read-write |
| ReadWriteOncePod | RWOP | Single pod mounts read-write (K8s 1.22+) |

RWX-capable storage: NFS, CephFS, GlusterFS, AWS EFS (via `efs.csi.aws.com`), Azure Files (via `file.csi.azure.com`), Google Filestore.

> [!TIP]
> Cloud-managed block disks (EBS, Azure Disk, GCP Persistent Disk) are RWO only — they can attach to exactly one node at a time. For RWX, use a managed file service.

***

**8. What are Init Containers, and how do they differ from regular containers?**

Init containers run sequentially before the main containers start. Each must exit successfully (exit code 0) before the next begins.

Differences from regular containers:
- No probes (liveness, readiness, startup)
- Run to completion — not long-lived processes
- Different resource limits from main containers
- Each init container must succeed before the next runs

```yaml
initContainers:
- name: wait-for-db
  image: busybox
  command: ['sh', '-c', 'until nslookup postgres; do sleep 2; done']
- name: run-migrations
  image: myapp:v2
  command: ['python', 'manage.py', 'migrate']
containers:
- name: app
  image: myapp:v2
```

Use cases: waiting for dependencies, DB migrations, pre-populating volumes, setting permissions on PVC mounts.

***

**9. What is a Pod Disruption Budget (PDB), and when is it critical?**

A PDB guarantees a minimum number of Pods remain available during voluntary disruptions (node drain, cluster upgrades, Cluster Autoscaler scale-down):

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: api-pdb
spec:
  minAvailable: 2        # always keep at least 2 pods running
  # OR: maxUnavailable: 1
  selector:
    matchLabels:
      app: api
```

A `kubectl drain` will wait or fail if evicting a Pod would violate the PDB.

Critical scenarios:
- 3-replica deployment with `minAvailable: 2` → only 1 pod can be drained at a time
- StatefulSet Kafka cluster — must not drain the leader without a safe replacement
- `maxUnavailable: 0` prevents any voluntary disruption (use only if the app cannot tolerate even momentary pod loss)

***

**10. What are NetworkPolicies, and how do you implement a default-deny posture?**

NetworkPolicies restrict pod-to-pod and pod-to-external traffic. Require a CNI that supports them (Calico, Cilium, Weave).

Default-deny all traffic in a namespace:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: production
spec:
  podSelector: {}          # Selects all pods
  policyTypes: [Ingress, Egress]
  # No ingress/egress rules → deny all
```

Then add specific allows:

```yaml
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-api
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: api
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - port: 8080
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - port: 5432
  - ports:
    - port: 53        # Allow DNS (UDP + TCP)
    - protocol: UDP
      port: 53
```

***

**11. What is the difference between a StatefulSet and a Deployment?**

| Feature | Deployment | StatefulSet |
|---|---|---|
| Pod identity | Random suffix (`app-7d8c4f-xyz`) | Stable ordinal (`app-0`, `app-1`) |
| Storage | Shared PVC (or none) | Per-pod PVC via `volumeClaimTemplates` |
| Scaling order | Parallel | Sequential (ordered up/down) |
| Pod DNS | None per pod | `<pod>.<headless-svc>.<ns>.svc.cluster.local` |
| PVC on delete | N/A | PVCs are NOT deleted when StatefulSet is deleted |
| Use case | Stateless web apps, APIs | Databases, Kafka, etcd |

A StatefulSet also requires a **headless service** (`clusterIP: None`) to provide stable per-pod DNS.

***

**12. What is Vertical Pod Autoscaler (VPA) and what are its limitations?**

VPA recommends and optionally auto-sets CPU/memory requests based on observed usage history.

Modes:
- `Off` — Recommendations only (read `kubectl describe vpa <name>`)
- `Initial` — Sets at pod creation; no updates to running pods
- `Auto` — Evicts pods and recreates with updated values

Limitations:
- Requires **pod eviction** to apply changes → downtime on single-replica deployments
- Cannot run in `Auto` mode simultaneously with HPA on CPU (they conflict)
- Needs 24+ hours of data before recommendations stabilize
- Does not work with all workload types (Jobs, standalone Pods)

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: api-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api
  updatePolicy:
    updateMode: "Initial"    # Safe for stateless apps
  resourcePolicy:
    containerPolicies:
    - containerName: api
      minAllowed:
        cpu: 50m
        memory: 64Mi
      maxAllowed:
        cpu: "4"
        memory: 4Gi
```

***

**13. How do admission webhooks work, and what is the risk of `failurePolicy: Fail`?**

Admission webhooks are HTTP endpoints called by the API server during object creation/update:

1. **MutatingAdmissionWebhook** — called first; can modify the object
2. **ValidatingAdmissionWebhook** — called second; can allow or deny

`failurePolicy` controls what happens if the webhook is unreachable:
- `Fail` — Reject the request (safe but risky if webhook has availability issues)
- `Ignore` — Allow the request through (unsafe but resilient to webhook outages)

> [!CAUTION]
> A `failurePolicy: Fail` webhook with no PodDisruptionBudget or high-availability deployment can block ALL pod creation in a cluster if the webhook pod crashes. Always run webhook deployments with `minAvailable: 1` PDB and configure `namespaceSelector` to exclude `kube-system`.

***

**14. How does topology-aware volume provisioning work?**

Without `WaitForFirstConsumer`, a PVC bound to a PV in zone `us-east-1a` may be scheduled to a pod in `us-east-1b`, causing the pod to remain Pending forever.

With `WaitForFirstConsumer` binding mode:
1. PVC is created but remains `Pending` (not bound immediately)
2. A pod claiming the PVC is scheduled to a node (based on other constraints)
3. The CSI driver provisions the volume in the same zone as the scheduled node
4. The PVC binds to the newly provisioned PV

```yaml
kind: StorageClass
spec:
  volumeBindingMode: WaitForFirstConsumer
```

***

**15. What is custom metrics scaling with HPA and KEDA?**

**Custom Metrics HPA (via Prometheus Adapter):**

```yaml
metrics:
- type: Pods
  pods:
    metric:
      name: http_requests_per_second
    target:
      type: AverageValue
      averageValue: "100"
```

Requires: Prometheus Adapter installed and `APIService v1beta1.custom.metrics.k8s.io` registered.

**KEDA** (Kubernetes Event Driven Autoscaling) goes further:
- Polls event sources directly (SQS, Kafka, Redis, Azure Service Bus, Cron)
- Scales to **zero** (not possible with native HPA which has minReplicas: 1 effectively)
- No need to expose custom metrics through the Kubernetes metrics API

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
spec:
  scaleTargetRef:
    name: worker
  minReplicaCount: 0
  maxReplicaCount: 30
  triggers:
  - type: kafka
    metadata:
      bootstrapServers: kafka:9092
      consumerGroup: my-group
      topic: orders
      lagThreshold: "50"   # Scale: 1 replica per 50 messages of lag
```

***

**16. What is a headless Service and when is it used?**

A headless Service has `clusterIP: None`. Instead of a virtual IP, DNS returns the individual pod IP addresses directly.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: postgres-headless
spec:
  clusterIP: None
  selector:
    app: postgres
  ports:
  - port: 5432
```

`nslookup postgres-headless.production.svc.cluster.local` returns all pod IPs (A records).

Use cases:
- StatefulSet peer discovery (`postgres-0.postgres-headless.ns.svc.cluster.local`)
- Applications that manage their own load balancing (Cassandra, Kafka, etcd)
- Client-side load balancing with gRPC (which uses long-lived connections)

***

### Advanced Architecture Questions (Staff/Principal Level)

**Q: How does eBPF change the Kubernetes networking and observability model compared to iptables-based approaches?**

Traditional kube-proxy uses iptables for service load balancing: every Service creates O(N×M) iptables rules (N services × M endpoints). At 10,000 services with 10 endpoints each, that's 100,000+ rules processed linearly for every packet. Performance degrades nonlinearly.

eBPF (extended Berkeley Packet Filter) runs sandboxed programs in the kernel at hook points (XDP, TC ingress/egress, socket, tracepoints). Cilium replaces kube-proxy entirely with eBPF maps (hash tables with O(1) lookups) for service load balancing. Benefits:

**Networking**: Identity-based policies (cryptographic workload identity, not IP-based), L7 policies at kernel level, direct endpoint routing (bypass iptables NAT entirely), transparent encryption via WireGuard at kernel level.

**Observability**: Cilium Hubble intercepts every packet at kernel level without any changes to application code or sidecars. Full L3-L7 visibility, DNS requests, HTTP headers — zero overhead because it's kernel-level, not userspace sidecar proxy.

**Tradeoffs**: Requires kernel ≥5.4 (ideally 5.10+), more complex debugging (bpftool, bpftrace instead of iptables-save), CNI-specific — can't mix with other CNIs.

For CKA/CKAD: understand that Cilium = eBPF CNI. For architecture interviews: the key insight is that eBPF moves enforcement to the kernel data path, making it both faster and more observable than userspace proxies (Envoy sidecars) for L3/L4 policies.

***

**Q: What is the Kubernetes Gateway API and how does it improve on Ingress?**

Ingress has fundamental limitations: it only defines HTTP host/path routing; all other capabilities (TLS passthrough, TCP routing, header manipulation, traffic splitting) are implemented via non-standard annotations that differ between controllers. An NGINX Ingress annotation doesn't work on Traefik.

Gateway API (GA in 1.28) introduces a role-oriented, expressive API:

```
GatewayClass (cluster-scoped) → Gateway (namespace, provisions LB) → HTTPRoute/TCPRoute/GRPCRoute (attach to Gateway)
```

**Role separation**: Infrastructure admin manages GatewayClass and Gateway. Application developer manages Routes. This maps to real organizations: platform team owns the load balancer; dev teams own their routing rules.

**Expressiveness built-in** (no annotations needed):
- `HTTPRoute`: header matching, URL rewriting, traffic splitting by weight (canary), request mirroring
- `TCPRoute`: L4 TCP routing
- `GRPCRoute`: gRPC-aware routing
- `TLSRoute`: TLS passthrough

**Multi-tenant**: Multiple teams can attach routes to a shared Gateway via `parentRefs` with namespace restrictions defined in the Gateway's `allowedRoutes`.

Migration path: Ingress still works and won't be removed. New deployments should use Gateway API. Major controllers (NGINX, Traefik, Istio, Envoy Gateway, GKE NEG) all support it.

***

**Q: Explain how you would design a multi-cluster Kubernetes architecture for a global SaaS application. What components are needed and what are the failure modes?**

**Architecture layers**:

1. **Cluster topology**: Region-per-cluster (us-east-1, eu-west-1, ap-southeast-1). Active-active, not active-passive — traffic is routed to the nearest region. Control plane HA within each cluster (3 control plane nodes per region).

2. **Global traffic routing**: DNS-based (Route 53 latency routing, Cloudflare Load Balancer) or Anycast. Health checks at the edge detect cluster unavailability.

3. **Multi-cluster service discovery**: 
   - Option A: Istio multi-cluster with shared control plane or replicated control planes — services in cluster A can reach services in cluster B via the mesh
   - Option B: Submariner (CNCF) — cross-cluster service discovery and network connectivity
   - Option C: Pure DNS federation — each cluster exposes services via external DNS, other clusters call the DNS name

4. **Configuration management**: Cluster API (CAPI) for cluster lifecycle. ArgoCD Hub-Spoke pattern: one ArgoCD instance manages all clusters via ApplicationSets with cluster generators. GitOps is the only sane way to manage N clusters.

5. **Data layer** (hardest part):
   - Stateless services: easy, deploy everywhere
   - Databases: regional write primaries with cross-region async replication (Postgres with pglogical, CockroachDB, YugabyteDB for multi-primary)
   - Global cache: Redis with regional instances, eventual consistency accepted

**Failure modes**:
- Split-brain: region becomes isolated but thinks it's primary — use fencing (STONITH equivalent) and design for AP (accept availability, tolerate partition) vs CP (accept downtime)
- Configuration drift: clusters diverge without GitOps enforcement — ArgoCD auto-sync with prune+self-heal
- Network partitions during cross-cluster calls: circuit breakers via Istio (Envoy `outlierDetection`)
- etcd quorum loss: 3-node control plane requires 2 nodes for quorum — a zone failure with 2 nodes in one zone is catastrophic

**Interview answer key**: Mention CAPI for fleet management, ArgoCD ApplicationSet for GitOps at scale, the data layer complexity, and that you prefer regional clusters over a single global mega-cluster for blast radius containment.

***

**Q: How does the Kubernetes scheduler framework work and how would you write a custom scheduler plugin?**

The scheduler framework (GA in 1.19) replaces the old predicates/priorities model with a lifecycle of extension points. Every scheduling decision passes through phases:

```
PreFilter → Filter → PostFilter → PreScore → Score → Reserve → Permit → PreBind → Bind → PostBind
```

**Key phases**:
- `Filter`: eliminates nodes that can't run the pod (node affinity, resource fit, taints). All filter plugins must pass.
- `Score`: ranks remaining nodes 0-100. Multiple plugins run and scores are weighted-summed.
- `Reserve`: optimistically claims resources before binding (prevents race conditions in multi-scheduler setups).
- `Permit`: can delay or reject binding (used for gang scheduling — wait until all pods of a job can be scheduled simultaneously).

**Writing a custom plugin**:
```go
type MyPlugin struct{}

func (pl *MyPlugin) Name() string { return "MyPlugin" }

func (pl *MyPlugin) Score(ctx context.Context, state *framework.CycleState, p *v1.Pod, nodeName string) (int64, *framework.Status) {
    // score this node for this pod
    // return 0-100
    return 50, nil
}

func (pl *MyPlugin) ScoreExtensions() framework.ScoreExtensions { return nil }

// Register it:
func New(obj runtime.Object, h framework.Handle) (framework.Plugin, error) {
    return &MyPlugin{}, nil
}
```

Deploy as a separate scheduler binary (not a webhook — it's compiled in). Configure pods to use it via `schedulerName: my-scheduler` in PodSpec.

**Real use cases**: GPU topology-aware scheduling (place pods on nodes where their GPUs share NVLink), cost-aware scheduling (prefer spot nodes, fallback to on-demand), gang scheduling for ML jobs (Volcano, YuniKorn use this).

***

**Q: Explain API Priority and Fairness (APF) and how it prevents API server overload.**

Before APF (pre-1.18), the API server had a single queue. A single client hammering the API server (e.g., a buggy controller doing 10,000 LIST pods/second) could starve legitimate traffic.

APF introduces two concepts:
- `PriorityLevelConfiguration`: defines queue parameters (queue count, queue length, concurrency shares)
- `FlowSchema`: classifies requests into priority levels based on user, group, namespace, verb, resource

**Built-in priority levels** (highest to lowest):
1. `exempt`: system:masters, exempted from all queuing
2. `leader-election`: leader election requests (high priority to prevent HA disruption)
3. `workload-high`: controller manager, scheduler
4. `workload-low`: default for most authenticated requests
5. `global-default`: catch-all
6. `catch-all`: last resort

**Fair queuing within a priority level**: requests from different flows (different users/namespaces) are served in a round-robin fashion to prevent one flow from starving others.

**When it matters**: A namespace with a broken operator doing constant LIST operations gets rate-limited at the `workload-low` level without affecting system components or other namespaces. The API server becomes multi-tenant at the request scheduling level.

**Debugging**: `kubectl get flowschema`, `kubectl get prioritylevelconfiguration`. Metrics: `apiserver_flowcontrol_rejected_requests_total`, `apiserver_flowcontrol_current_inqueue_requests`.

***

**Q: What is Karpenter and how does it differ from Cluster Autoscaler? When would you choose each?**

**Cluster Autoscaler (CA)**:
- Watches for unschedulable Pods, finds a Node Group that could fit them, scales that Node Group up
- Scale-down: identifies underutilized nodes and cordon/drains them
- Works with pre-defined Node Groups (AWS ASGs, Azure VMSSs). Each node group is a specific instance type.
- Limitation: you must pre-create node groups for every instance type you might want. Bin-packing is basic.

**Karpenter** (now a CNCF project):
- Watches for unschedulable Pods and directly provisions EC2 instances (or Azure VMs in AKS) via cloud provider APIs — no Node Groups needed
- Selects instance type based on Pod requirements (CPU, memory, GPU, architecture) — bin-packs optimally
- Consolidation: proactively terminates underutilized nodes and repacks workloads onto fewer, cheaper instances
- Supports Spot interruption handling natively
- `NodePool` (formerly Provisioner) defines constraints (instance families, zones, taints, labels) rather than specific instance types

**When to use CA**: You need Node Groups for compliance/cost reasons, or you're on a cloud provider Karpenter doesn't support yet (GKE has its own equivalent in Autopilot).

**When to use Karpenter**: AWS (most mature implementation), you want instance-type flexibility, you want automatic Spot-to-on-demand fallback, or you want consolidation to reduce costs.

**Key Karpenter concepts for interviews**: `NodePool` (node constraints), `EC2NodeClass` (AWS-specific config: AMI, subnet, security groups), disruption budget (how aggressively to consolidate).

***

**Q: How does Pod Security Admission work in Kubernetes 1.25+ and what replaced PodSecurityPolicy?**

PodSecurityPolicy was deprecated in 1.21 and removed in 1.25. It had fatal flaws: it required RBAC to USE a PSP (not just have it exist), leading to privilege escalation via the `use` verb; the admission model was confusing.

**Pod Security Admission (PSA)** is the built-in replacement. Three policy levels:
- `privileged`: unrestricted (used for infrastructure workloads like CNI, CSI drivers)
- `baseline`: prevents known privilege escalation (no privileged containers, no host namespaces, limited volume types)
- `restricted`: heavily hardened (no root, read-only root FS required, seccomp required, all capabilities dropped)

Applied per namespace via labels:
```yaml
metadata:
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/warn: restricted
    pod-security.kubernetes.io/audit: restricted
```

Three modes: `enforce` (reject), `warn` (allow but show warning), `audit` (allow but log).

**Limitations of PSA**: Not granular enough for complex environments (can't say "team A gets baseline, service account B gets privileged in the same namespace"). For fine-grained policies, use **OPA/Gatekeeper** or **Kyverno** (policy as code, can write arbitrary validation logic).

**Interview answer**: PSA for standard security baselines, Kyverno/Gatekeeper for custom policies (e.g., "all images must come from our private registry", "all deployments must have resource limits set").

***

**Q: Explain how Sigstore/Cosign can be used to enforce image supply chain security in Kubernetes.**

The supply chain problem: anyone with registry push access can push any image. How do you verify that the image running in your cluster was actually built by your CI pipeline and not tampered with?

**Sigstore components**:
- `Cosign`: signs container images (attaches signature as a separate OCI artifact in the same registry)
- `Fulcio`: keyless signing CA — issues short-lived certificates tied to OIDC identity (GitHub Actions, Google SA, etc.) so you don't manage long-lived signing keys
- `Rekor`: immutable transparency log — all signatures are recorded; you can prove a signature existed at a point in time

**Workflow**:
```bash
# In CI (GitHub Actions) — keyless signing via OIDC
cosign sign --yes ghcr.io/myorg/myapp:sha-abc123

# Sign with SBOMs attached
cosign attest --yes --predicate sbom.json --type spdxjson ghcr.io/myorg/myapp:sha-abc123
```

**Enforcement in Kubernetes**:
- **Policy Controller** (from Sigstore project): admission webhook that verifies signatures before pod admission
- **Kyverno**: `verifyImages` rule checks cosign signatures
- **Connaisseur**: dedicated admission controller for image trust

```yaml
# Kyverno policy
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: verify-image
spec:
  rules:
  - name: check-image-signature
    match:
      resources: {kinds: [Pod]}
    verifyImages:
    - imageReferences: ["ghcr.io/myorg/*"]
      attestors:
      - entries:
        - keyless:
            subject: "https://github.com/myorg/myapp/.github/workflows/build.yml@refs/heads/main"
            issuer: "https://token.actions.githubusercontent.com"
```

**What this achieves**: Only images signed by your specific GitHub Actions workflow can run in the cluster. Tampering with the image changes its digest, invalidating the signature.

***

**Q: Walk through debugging a scenario where the API server is experiencing high latency (>500ms p99) and some requests are timing out.**

**Immediate triage** (first 5 minutes):

```bash
# 1. API server metrics (if accessible)
kubectl get --raw /metrics | grep apiserver_request_duration_seconds

# 2. Check API server pod resource usage
kubectl top pod -n kube-system -l component=kube-apiserver

# 3. Check etcd latency (API server depends on etcd for reads/writes)
kubectl get --raw /metrics | grep etcd_request_duration_seconds

# 4. Check request inflight
kubectl get --raw /metrics | grep apiserver_current_inflight_requests
```

**Systematic investigation**:

```bash
# 5. Enable audit logging if not already (requires API server restart)
# Check: --audit-log-path, --audit-policy-file in API server flags

# 6. Identify which request types are slow
kubectl get --raw /metrics | grep 'apiserver_request_duration_seconds_bucket{.*le="0.5"'
# Look for verbs+resources with high latency (LIST operations are most common offender)

# 7. Check for expensive LIST operations
kubectl get events -A --sort-by=.lastTimestamp | grep "List"

# 8. Check for watch cache starvation
kubectl get --raw /metrics | grep watch_cache
```

**Common root causes**:

| Symptom | Root Cause | Fix |
|---------|-----------|-----|
| etcd p99 >100ms | etcd disk I/O saturation | Move etcd to NVMe SSD; separate etcd disk from OS |
| High LIST latency | Unparameterized LIST without label selectors | Add `--label-selector` to controller; enable pagination |
| OOM on API server pod | Large watch cache consuming all memory | Set `--watch-cache-sizes` limits; add memory to node |
| `apiserver_current_inflight_requests` at limit | Too many concurrent requests | Tune APF priority levels; investigate misbehaving controllers |
| Slow webhook responses | Admission webhook timing out | Optimize webhook or increase timeout; set `failurePolicy: Ignore` for non-critical |

**Long-term fixes**: Enable APF fine-tuning; ensure etcd has dedicated fast disk; set up API server horizontal scaling (in managed clusters this is automatic); implement client-side caching in controllers (use informers, not direct API calls).

***

**Q: How would you implement zero-downtime migration of a stateful application (PostgreSQL primary) from one Kubernetes cluster to another?**

This is a distributed systems problem: you must avoid data loss AND avoid downtime simultaneously.

**Phase 1: Setup dual-cluster** (no traffic change yet)
1. Deploy PostgreSQL in the new cluster with streaming replication FROM the source cluster's primary
2. Source = primary (writes), Target = streaming replica (reads only)
3. Verify replication lag is consistently <1s: `SELECT pg_last_wal_receive_lsn()` vs source's `pg_current_wal_lsn()`

**Phase 2: Application preparation**
1. Add connection string configuration support (app must be able to point to either cluster)
2. Deploy app to new cluster in read-only mode, connecting to source DB
3. This validates new cluster networking, compute, and app config

**Phase 3: Cutover** (the tricky part)
1. Set application maintenance page / feature flag to pause writes
2. Verify replication lag reaches 0 (`pg_last_wal_receive_lsn() = pg_current_wal_lsn()`)
3. Promote replica in new cluster to primary: `pg_promote()`
4. Update DNS/connection strings to point to new cluster's PostgreSQL
5. Remove maintenance mode

**Phase 4: Validation and cleanup**
1. Monitor error rates, query latency, replication metrics
2. Keep old cluster running in standby for 24-48 hours
3. After confidence, decommission old cluster

**Downtime window**: Step 3 is the only true downtime — typically <30 seconds for DNS TTL and connection drain.

**Tools**: Patroni for automated failover, PgBouncer for connection pooling with transparent failover, Velero for backup before cutover.

**Key insight for interview**: Never do a big-bang migration. Always set up replication first, validate in parallel, then do a planned, reversible cutover with a short maintenance window.

### System Design Perspective

- **etcd quorum vs availability trade-off:** etcd prioritises CP (Consistency + Partition tolerance) in CAP terms. During a network partition, the minority partition refuses writes to avoid split-brain. This means a 3-node etcd cluster that loses 2 nodes becomes completely read-only — existing pods keep running (kubelet caches state locally) but no control plane operations work. Design HA control planes with 5 nodes in 3 AZs: 2+2+1 distribution tolerates a full AZ loss without losing quorum.
- **API Priority and Fairness — the design intent:** Without APF, a single client doing bulk LIST operations (CI pipeline listing all pods across all namespaces) can starve kubelet heartbeats, causing cascading node NotReady events and pod evictions. APF is a multi-level queue with explicit shares per client category — kubelet heartbeats get a high-priority, guaranteed share that CI bots cannot starve. Misconfigured APF can lock out all users; always test on non-prod.
- **Operator maturity and the Greenfield vs Brownfield gap:** An Operator at maturity level 1 (Basic Install) is easy to build but provides no value over Helm. Maturity level 3 (Full Lifecycle: backup/restore/failure recovery) is where Operators justify their complexity cost. The build-vs-buy decision: use a community Operator (CloudNativePG, MongoDB Operator, Strimzi) for standard components; build custom Operators only for truly proprietary operational knowledge.
- **Karpenter consolidation and the spot instance risk:** Karpenter's consolidation feature can terminate a node that becomes underutilized — even if it was provisioned on-demand. For spot instances, consolidation + spot interruption can create a cascade: spot interruption drains pods to a new node, which then triggers further consolidation. Set `disruption.consolidationPolicy: WhenEmpty` (not `WhenUnderutilized`) for critical workloads, and use `karpenter.sh/do-not-disrupt` annotation for pods that should never be consolidated away.
- **Gang scheduling and the deadlock risk:** Naive gang scheduling can deadlock: if cluster resources are partially allocated and two jobs each need 8 GPUs but only 7 are available, both jobs wait forever. Volcano solves this with a queue-based preemption system and a DRF (Dominant Resource Fairness) algorithm. The fundamental insight: gang scheduling requires a global view of pending demand, not a greedy per-pod placement.
- **Zero-downtime DB migration — the schema versioning constraint:** The application cutover window is only safe if the new schema is backward-compatible with the old app version. If you're running a blue-green app deployment alongside the migration, both app versions must read from the same database at the same time during the traffic switch. This forces an "expand/contract" schema migration pattern: add columns (never remove), deploy app that reads both old and new columns, then remove old columns in a subsequent migration after rollout is complete.

---

## Hard (continued) — Autoscaling, Admission Control, CRDs & Multi-Tenancy

**Q: Compare Karpenter and Cluster Autoscaler. When would you choose each? Cover consolidation, provisioning time, and bin-packing.**

**A:**

Cluster Autoscaler (CA) runs a 10-second reconcile loop on the control plane: it identifies pending pods, simulates schedulability against existing and hypothetical nodes, then calls the cloud provider API to add nodes. Scale-down marks nodes unneeded when CPU+memory falls below a threshold and drains them. CA is cloud-agnostic via a provider abstraction layer.

Karpenter is an event-driven CRD-based operator. When a pod becomes Unschedulable, Karpenter immediately batches pending pods and calls the cloud fleet API (e.g., EC2 Fleet) to provision in one API call — 30–60 s vs CA's 2–5 min.

**Consolidation:**

CA's scale-down is node-centric: identify underutilized nodes, drain, terminate. If any pod has no schedulable alternative (anti-affinity, local storage), the whole node is blocked from scale-down.

Karpenter uses pod-centric consolidation: simulate moving all pods off an underutilized node; if the simulation succeeds, evict and terminate. It also supports `ttlSecondsUntilExpired` (force-recycle nodes on a schedule), which amortizes instance type drift — when a cheaper instance type appears, Karpenter replaces old nodes proactively.

**Bin-packing:**

CA prefers nodes with the most available capacity (spread first, bin-pack second). Karpenter uses a cost-aware consolidation policy: it may choose one larger instance over two medium ones when that's cheaper (fewer hypervisor overheads).

**Decision framework:**

| Scenario | Choose |
|----------|--------|
| Batch / data workloads (5 min latency OK) | Cluster Autoscaler |
| Real-time serving requiring <2 min provision | Karpenter |
| Spot-heavy workloads needing price-chasing | Karpenter |
| Managed K8s (GKE Autopilot, EKS pre-configured) | Cluster Autoscaler |
| Strict compliance (minimal API calls/audit logs) | Cluster Autoscaler |

**Karpenter pitfall:** consolidation + spot interruption can cascade. Set `disruption.consolidationPolicy: WhenEmpty` (not `WhenUnderutilized`) for critical workloads, and annotate stateful pods with `karpenter.sh/do-not-disrupt: "true"`.

---

**Q: Walk through the Kubernetes admission control pipeline. How do ValidatingWebhookConfiguration and MutatingWebhookConfiguration work? What happens if a webhook is unavailable?**

**A:**

Every API Server request passes through a series of admission controllers before the object is persisted to etcd. The order is:

```
kubectl apply
  → Authentication (who are you?)
  → Authorization (RBAC: can you do this?)
  → Mutating Admission (modify the object)
  → Schema Validation
  → Validating Admission (accept or reject)
  → etcd persist
```

**Mutating Webhooks (MutatingWebhookConfiguration):**

Mutating webhooks can modify the incoming object (add labels, inject sidecars, set default values). Common examples:
- Istio's sidecar injector: intercepts Pod create, adds `istio-proxy` container to the spec
- OPA Gatekeeper's mutation: adds security context defaults

```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: MutatingWebhookConfiguration
metadata:
  name: sidecar-injector
webhooks:
- name: inject.istio.io
  rules:
  - apiGroups: [""]
    apiVersions: ["v1"]
    resources: ["pods"]
    operations: ["CREATE"]
  clientConfig:
    service:
      name: istiod
      namespace: istio-system
      path: /inject
    caBundle: <base64-ca-cert>
  admissionReviewVersions: ["v1"]
  sideEffects: None
  failurePolicy: Fail     # Reject if webhook unreachable
  namespaceSelector:
    matchLabels:
      istio-injection: enabled
```

**Validating Webhooks (ValidatingWebhookConfiguration):**

Validating webhooks can only accept or reject; they cannot modify. Common examples:
- OPA Gatekeeper: enforce policy (no images without digest, no privileged containers)
- cert-manager webhook: validate Certificate and Issuer resources

**Webhook unavailability — `failurePolicy`:**

The `failurePolicy` field controls behavior when the webhook server is unreachable or times out:
- `Fail` (default): The API request is rejected. Mutations/validations are enforced. If the webhook pod crashes, no Pods can be created in the targeted namespaces — **cluster-wide outage risk**.
- `Ignore`: The API request proceeds as if the webhook approved it. Policies are not enforced during downtime.

**Production best practice:**

```yaml
# For security-critical webhooks (OPA Gatekeeper):
failurePolicy: Fail      # Enforce even at cost of availability
timeoutSeconds: 10       # Fast timeout; keep webhook pods fast

# For non-critical mutating webhooks:
failurePolicy: Ignore    # Availability over policy during outage

# Always exempt the webhook namespace itself:
namespaceSelector:
  matchExpressions:
  - key: kubernetes.io/metadata.name
    operator: NotIn
    values: ["gatekeeper-system", "kube-system"]
```

Exempting `kube-system` from the webhook prevents a cascading failure: if the webhook pod crashes, Kubernetes cannot restart it without first being able to create pods in `kube-system`.

**Webhook debugging:**

```bash
# See all webhook configs
kubectl get mutatingwebhookconfigurations,validatingwebhookconfigurations

# Check if a webhook is the cause of a failed create
kubectl create deployment test --image=nginx --dry-run=server -v=8 2>&1 | grep webhook

# Check webhook pod logs (e.g., Gatekeeper)
kubectl logs -n gatekeeper-system -l control-plane=controller-manager --tail=50
```

---

**Q: Explain the Kubernetes Operator pattern. What is the reconciliation loop? When should you build a custom Operator vs use Helm? Describe a real operator implementation using controller-runtime.**

**A:**

An Operator is a Kubernetes controller that encodes domain-specific operational knowledge as code. It extends the Kubernetes API with Custom Resource Definitions (CRDs) and implements a **reconciliation loop** that continuously drives actual cluster state toward desired state declared in a CR.

**Reconciliation Loop:**

```
User creates/updates CustomResource (CR)
  → controller-runtime detects change (via informer/watch)
  → Reconcile() is called with the CR's namespace/name
  → Reconcile() reads current state (from cluster)
  → Reconcile() computes delta (desired - current)
  → Reconcile() applies changes (create/update/delete resources)
  → If error: re-queue with exponential backoff
  → If success: re-queue after resync period (or wait for next event)
```

The key property: **Reconcile() must be idempotent**. It can be called 100 times for the same object and must produce the same result. This handles retries, restarts, and partial failures safely.

**Controller-runtime example (Go):**

```go
package controllers

import (
    "context"
    appsv1 "k8s.io/api/apps/v1"
    corev1 "k8s.io/api/core/v1"
    "k8s.io/apimachinery/pkg/api/errors"
    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
    ctrl "sigs.k8s.io/controller-runtime"
    "sigs.k8s.io/controller-runtime/pkg/client"
    
    myv1alpha1 "github.com/myorg/my-operator/api/v1alpha1"
)

type WebAppReconciler struct {
    client.Client
}

func (r *WebAppReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    // 1. Fetch the CR
    webapp := &myv1alpha1.WebApp{}
    if err := r.Get(ctx, req.NamespacedName, webapp); err != nil {
        if errors.IsNotFound(err) {
            return ctrl.Result{}, nil  // CR deleted; nothing to do
        }
        return ctrl.Result{}, err
    }
    
    // 2. Check if Deployment exists
    dep := &appsv1.Deployment{}
    err := r.Get(ctx, req.NamespacedName, dep)
    
    if errors.IsNotFound(err) {
        // 3. Create Deployment
        dep = r.deploymentForWebApp(webapp)
        if err := r.Create(ctx, dep); err != nil {
            return ctrl.Result{}, err
        }
        return ctrl.Result{Requeue: true}, nil
    }
    
    // 4. Update if replica count drifted
    if *dep.Spec.Replicas != webapp.Spec.Replicas {
        dep.Spec.Replicas = &webapp.Spec.Replicas
        if err := r.Update(ctx, dep); err != nil {
            return ctrl.Result{}, err
        }
    }
    
    // 5. Update status
    webapp.Status.ReadyReplicas = dep.Status.ReadyReplicas
    r.Status().Update(ctx, webapp)
    
    return ctrl.Result{}, nil
}
```

**Operator vs Helm decision:**

| Situation | Use Helm | Use Operator |
|-----------|----------|--------------|
| Install/upgrade/delete a static set of K8s resources | ✓ | |
| Operational knowledge that runs continuously (backup at 3am, self-healing) | | ✓ |
| Multi-step lifecycle (provision → seed → promote) | | ✓ |
| No ongoing reconciliation needed | ✓ | |
| Managing a database cluster (failover, replica promotion) | | ✓ |
| Simple app with fixed manifests | ✓ | |

**Operator maturity levels (OperatorHub model):**
1. **Basic Install** — deploys the application (same as Helm)
2. **Seamless Upgrades** — handles version upgrades without downtime
3. **Full Lifecycle** — backup, restore, failure recovery
4. **Deep Insights** — exposes metrics, alerts, dashboards via CR
5. **Auto-Pilot** — self-tunes based on workload (horizontal/vertical autoscaling)

Build a custom Operator only when you reach level 3+. For levels 1–2, Helm is simpler and more maintainable.

---

**Q: Explain PodTopologySpread constraints in detail. How do they differ from pod anti-affinity? Design a topology spread policy for a 3-AZ cluster with 30 replicas of a critical service.**

**A:**

PodTopologySpread constraints (introduced GA in K8s 1.19) give fine-grained control over how pods are distributed across topology domains — zones, nodes, racks — based on a `maxSkew` property.

**Anatomy of a constraint:**

```yaml
topologySpreadConstraints:
- maxSkew: 1                      # max allowed difference between domains
  topologyKey: topology.kubernetes.io/zone  # the grouping dimension
  whenUnsatisfiable: DoNotSchedule          # or ScheduleAnyway
  labelSelector:
    matchLabels:
      app: my-service
  minDomains: 3                   # require at least 3 zones to exist (K8s 1.25+)
  matchLabelKeys:                 # match rolling deployment's ReplicaSet pods only (K8s 1.27+)
  - pod-template-hash
```

**maxSkew explained:**

If zone A has 10 pods, zone B has 10 pods, zone C has 9 pods — skew is 1 (10-9=1). With `maxSkew: 1`, a new pod will be scheduled in zone C. With `maxSkew: 2`, it could go anywhere.

**Difference from pod anti-affinity:**

| Feature | Pod Anti-Affinity | TopologySpread |
|---------|------------------|----------------|
| Goal | Prevent co-location | Balance distribution |
| Expression | Boolean (allowed or not) | Numeric (maxSkew tolerance) |
| Scope | Per-node by default | Any topology key |
| Performance | O(n²) at scheduling (all pod pairs) | O(n) |
| Granularity | All or nothing | Allows some imbalance |
| Rolling update | Does not account for old pods | `matchLabelKeys` scopes to current RS |

Anti-affinity says "don't put two of my pods on the same node." TopologySpread says "keep the count per zone within 1 of each other." They can be combined.

**Design for 30 replicas across 3 AZs:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: critical-service
spec:
  replicas: 30
  template:
    spec:
      topologySpreadConstraints:
      # Zone-level spread: max 1 pod difference between AZs
      - maxSkew: 1
        topologyKey: topology.kubernetes.io/zone
        whenUnsatisfiable: DoNotSchedule
        labelSelector:
          matchLabels:
            app: critical-service
        minDomains: 3
        matchLabelKeys:
        - pod-template-hash   # only count current ReplicaSet's pods
      
      # Node-level spread: no more than 2 pods per node
      - maxSkew: 2
        topologyKey: kubernetes.io/hostname
        whenUnsatisfiable: ScheduleAnyway   # soft constraint
        labelSelector:
          matchLabels:
            app: critical-service
      
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              topologyKey: kubernetes.io/hostname
              labelSelector:
                matchLabels:
                  app: critical-service
```

**What this achieves:**
- 30 replicas → 10 per zone (±1 allowed) — hard constraint
- No more than ~2 per node (soft constraint; scheduler tries but won't block if nodes are limited)
- Pod anti-affinity adds a preference to spread across nodes within each zone

**`whenUnsatisfiable: DoNotSchedule` vs `ScheduleAnyway`:**

Use `DoNotSchedule` for zone-level spread (losing a zone with imbalanced pods is risky). Use `ScheduleAnyway` for node-level spread (some node concentration is acceptable, blocking is not). Mix them as shown above for defense-in-depth.

**`minDomains` (K8s 1.25+):**

Without `minDomains: 3`, if a zone is temporarily unavailable and only 2 zones exist, the scheduler relaxes the zone constraint and allows uneven distribution. With `minDomains: 3`, pods will be Pending until all 3 zones are present. Use this only for strict HA requirements where 2-zone operation is unacceptable.

---

**Q: Describe how cert-manager issues and rotates TLS certificates in Kubernetes. What happens when a certificate nears expiry? How do you handle rotation for a high-traffic service without downtime?**

**A:**

cert-manager is a Kubernetes Operator that automates TLS certificate issuance and renewal. It introduces four CRDs: `Issuer`, `ClusterIssuer`, `Certificate`, and `CertificateRequest`.

**Certificate lifecycle:**

```
1. Create Certificate CR
2. cert-manager creates CertificateRequest CR
3. cert-manager contacts Issuer (Let's Encrypt ACME, Vault PKI, self-signed CA)
4. ACME: DNS-01 or HTTP-01 challenge to prove domain ownership
5. CA signs and returns certificate
6. cert-manager stores cert+key in a Kubernetes Secret
7. Pod/Ingress references the Secret
8. cert-manager watches for expiry: renews at renewBefore threshold (default: 30 days before expiry)
```

**Example Certificate CR:**

```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: my-service-tls
  namespace: production
spec:
  secretName: my-service-tls-secret   # cert+key stored here
  duration: 2160h                      # 90 days (Let's Encrypt max)
  renewBefore: 720h                    # renew 30 days before expiry
  dnsNames:
  - my-service.example.com
  - my-service-internal.example.com
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
```

**Renewal process:**

cert-manager watches `Certificate` objects. When `notAfter - renewBefore ≤ now`, it:
1. Creates a new `CertificateRequest`
2. Gets a fresh certificate from the Issuer
3. **Atomically updates the Secret** (single write, all fields updated at once)
4. Kubernetes propagates the updated Secret to mounted volumes within ~60s (kubelet's sync period)

**Zero-downtime rotation for high-traffic services:**

The key concern is the gap between secret update and pod reload.

**Option 1: Volume-mounted secrets (recommended)**
```yaml
volumes:
- name: tls
  secret:
    secretName: my-service-tls-secret

containers:
- name: app
  volumeMounts:
  - name: tls
    mountPath: /etc/tls
    readOnly: true
```

When the Secret is updated, the kubelet syncs the mount within `syncFrequency` (default 60s). The application must:
- Watch the cert file for changes (`inotify` or periodic `stat`)
- Reload TLS config without dropping connections (using `crypto/tls` `Config.GetCertificate` callback in Go, which is called per-connection — no reload needed)

**Go pattern for zero-downtime TLS rotation:**
```go
cert, err := tls.LoadX509KeyPair(certFile, keyFile)

tlsConfig := &tls.Config{
    GetCertificate: func(*tls.ClientHelloInfo) (*tls.Certificate, error) {
        // Re-read from disk on each new TLS handshake
        // (reads cached in OS page cache — negligible overhead)
        return tls.LoadX509KeyPair(certFile, keyFile)
    },
}

listener := tls.NewListener(ln, tlsConfig)
```

Every new TLS connection reads the latest cert from disk. No server restart required.

**Option 2: cert-manager's `tls.alpha.cert-manager.io/certificate-name` annotation on Ingress**
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - my-service.example.com
    secretName: my-service-tls-secret
```

cert-manager automatically creates the Certificate and manages rotation. NGINX Ingress Controller reloads its TLS config when the secret changes (one NGINX reload, typically <100ms impact on in-flight connections).

**Debugging certificate issues:**
```bash
# Check certificate status
kubectl describe certificate my-service-tls -n production

# Check events for ACME challenge failures
kubectl get events -n cert-manager --field-selector reason=Failed

# Manually trigger renewal
kubectl cert-manager renew my-service-tls -n production

# Check if secret has the right cert
kubectl get secret my-service-tls-secret -n production -o jsonpath='{.data.tls\.crt}' \
  | base64 -d | openssl x509 -noout -dates
```

---

**Q: How does the Kubernetes scheduler work internally? Walk through the scheduling cycle for a single pod, including the Filter and Score phases. How does scheduler extenders and the scheduling framework differ?**

**A:**

The Kubernetes scheduler is a control-plane component that watches for Unschedulable pods and assigns them to nodes. It processes pods one at a time (single-threaded scheduling cycle) but runs multiple pods through the cycle concurrently using separate goroutines for binding.

**Scheduling cycle for a single pod:**

```
1. Pod enters scheduling queue (activeQ, priority-sorted by PriorityClass)
2. Scheduler pops highest-priority pod
3. PreFilter plugins (validate pod can be scheduled at all — e.g., check PVC exists)
4. Filter phase (eliminate nodes that cannot run the pod)
5. PostFilter (if no nodes pass Filter: preemption — evict lower-priority pods)
6. PreScore (setup for scoring)
7. Score phase (rank remaining nodes 0-100)
8. NormalizeScore (scale all scores to 0-100 per plugin)
9. Reserve (lock resources — no two pods claim same resources)
10. Permit (hold scheduling for gang scheduling — wait for N pods before binding)
11. Bind (write pod.spec.nodeName to API server)
12. Node's kubelet picks up the pod and creates containers
```

**Filter plugins (eliminates nodes):**

| Plugin | Eliminates nodes where... |
|--------|--------------------------|
| NodeResourcesFit | Resources (CPU/memory) insufficient |
| NodeAffinity | Node labels don't match requiredDuringScheduling |
| PodTopologySpread | maxSkew would be violated |
| TaintToleration | Node has unmatched Taint |
| InterPodAffinity | Anti-affinity rules violated |
| VolumeBinding | No node has the PV's zone/storage class |

**Score plugins (ranks surviving nodes):**

| Plugin | Scores higher when... |
|--------|----------------------|
| NodeResourcesBalancedAllocation | CPU/memory usage is balanced (prevents hot nodes) |
| ImageLocality | The pod's image is already pulled on the node |
| InterPodAffinity | Other preferred pods are nearby |
| NodeAffinity | preferredDuringScheduling labels match |
| TaintToleration | Fewer taints to tolerate |

**Scheduling Framework (K8s 1.19 GA) vs Scheduler Extenders:**

Scheduler Extenders were the original extension mechanism: the scheduler calls an external HTTP webhook at Filter and Score phases. Problems: network round-trip per pod per node, no access to scheduler's internal cache, difficult to share state.

The **Scheduling Framework** allows in-process plugins written in Go, compiled into the scheduler binary. Plugins implement interfaces (`FilterPlugin`, `ScorePlugin`, `ReservePlugin`, etc.) and run in the same process — no network overhead.

```go
// Custom score plugin: prefer nodes with GPU
type GPUScorePlugin struct{}

func (g *GPUScorePlugin) Score(ctx context.Context, state *framework.CycleState, 
    pod *v1.Pod, nodeName string) (int64, *framework.Status) {
    
    nodeInfo, _ := state.Read(nodeName)
    // Score 100 if node has GPU, 0 otherwise
    if nodeInfo.Allocatable.ScalarResources["nvidia.com/gpu"] > 0 {
        return 100, nil
    }
    return 0, nil
}
```

Custom schedulers: deploy a separate scheduler pod and set `pod.spec.schedulerName: my-custom-scheduler`. Used for specialized workloads (ML training with gang scheduling requirements) without modifying the default scheduler.
