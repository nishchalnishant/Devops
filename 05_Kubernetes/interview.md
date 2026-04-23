# Kubernetes — Interview Questions

All difficulty levels combined.

---

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

---

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
