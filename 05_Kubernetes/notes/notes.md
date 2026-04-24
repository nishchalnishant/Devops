# Kubernetes — Deep Theory Notes

## Table of Contents

1. [Control Plane Components](#control-plane-components)
2. [Data Plane Components](#data-plane-components)
3. [Pod Lifecycle](#pod-lifecycle)
4. [Scheduling](#scheduling)
5. [Networking](#networking)
6. [Storage](#storage)
7. [RBAC](#rbac)
8. [Admission Controllers](#admission-controllers)
9. [CRDs and Operators](#crds-and-operators)
10. [Autoscaling](#autoscaling)
11. [Multi-Tenancy Patterns](#multi-tenancy-patterns)

---

## Control Plane Components

### kube-apiserver

The single entry point for all cluster communication. `kubectl`, kubelets, controllers, and external clients all speak to it — nothing else talks to etcd directly.

**Request path for a write operation:**

```
Client → AuthN → AuthZ (RBAC) → Admission Mutating Webhooks
       → Object Schema Validation → Admission Validating Webhooks
       → Persist to etcd → Return 201 Created
```

Key characteristics:
- Horizontally scalable — run 3+ instances behind a load balancer on the same etcd cluster
- API Priority and Fairness (APF) buckets traffic into flow schemas to prevent one consumer starving others (e.g., CI/CD bots vs. kubelet heartbeats)
- Audit logging records every API call with `requestObject`, `responseObject`, user identity, and timestamp

### etcd

Distributed key-value store running the **Raft consensus algorithm**. Raft requires a quorum: 3-node cluster tolerates 1 failure; 5-node tolerates 2.

**Critical operational properties:**

| Property | Value / Implication |
|---|---|
| Disk fsync latency | Must be < 10ms — use NVMe SSDs |
| Default storage limit | 2GB — exceeding it puts cluster in read-only mode |
| Revision history | Grows unboundedly — compact with `etcdctl compact` |
| Defragmentation | Run `etcdctl defrag` after compaction to reclaim disk |
| Backup | `etcdctl snapshot save` — test restores quarterly |

> [!CAUTION]
> etcd is the source of truth. If all etcd members lose data simultaneously and no backup exists, the cluster state is unrecoverable. Automated offsite snapshots are non-negotiable for production.

etcd data layout: all Kubernetes objects are stored under `/registry/<resource-type>/<namespace>/<name>`. Secrets are stored as base64-encoded values. Enable **Encryption at Rest** via `EncryptionConfiguration` on the API server to use AES-GCM or KMS-envelope encryption.

### kube-scheduler

Watches for Pods with `spec.nodeName == ""` and assigns them a node. Two-phase process:

**Phase 1 — Filtering (Predicates):** Eliminates uneligible nodes:
- Insufficient CPU or memory (vs. pod `requests`)
- Taint/toleration mismatch
- `nodeSelector` or node affinity mismatch
- Port conflict on the node
- PVC zone incompatibility (`volumeZonePredicate`)
- Max pods per node exceeded

**Phase 2 — Scoring (Priorities):** Ranks remaining nodes:
- `LeastAllocated` / `MostAllocated` — packs or spreads based on strategy
- `NodeAffinityPriority` — weights preferred affinity matches
- `InterPodAffinityPriority` — co-locates or separates based on pod affinity
- `ImageLocalityPriority` — prefers nodes that already have the container image
- `TopologySpreadConstraint` — enforces maxSkew across topology domains

The scheduler is pluggable via the **Scheduling Framework** — plugins hook into named extension points (`PreFilter`, `Filter`, `PostFilter`, `PreScore`, `Score`, `Bind`).

**Custom Schedulers:** Deploy a separate scheduler process, and set `spec.schedulerName: my-scheduler` in pod specs to opt in. The custom scheduler calls `POST /api/v1/namespaces/<ns>/pods/<name>/binding` to assign a node.

### kube-controller-manager

A single binary running dozens of controllers in a single process. Each controller is an independent reconciliation loop:

| Controller | Function |
|---|---|
| Node Controller | Monitors heartbeats; marks node `NotReady`; evicts pods after `pod-eviction-timeout` (default 5m) |
| ReplicaSet Controller | Ensures desired pod count matches actual |
| Deployment Controller | Manages ReplicaSets for rolling updates and rollbacks |
| Endpoints Controller | Populates `Endpoints` objects for Services |
| Service Account Controller | Creates default ServiceAccount per namespace |
| Job Controller | Tracks completions; retries failures |
| CronJob Controller | Creates Jobs on schedule |
| HPA Controller | Polls Metrics API; adjusts replica count |
| Namespace Controller | Cascading deletion when namespace is deleted |

Controllers communicate exclusively through the API server — never directly with each other.

### cloud-controller-manager

Offloads cloud-provider-specific logic from the core controller-manager. Runs:
- **Node controller** — integrates cloud metadata (instance type, zone, external IP)
- **Route controller** — configures cloud VPC routes for pod CIDRs
- **Service controller** — provisions cloud load balancers for `LoadBalancer` service type

---

## Data Plane Components

### kubelet

Agent on every node. Responsibilities:
1. Registers the node with the API server
2. Watches PodSpecs assigned to its node
3. Calls the CRI (Container Runtime Interface) to pull images and start containers
4. Runs probes and reports `PodStatus` back to the API server
5. Manages pod volumes (mounts PVCs via the CSI driver)
6. Enforces cgroup resource limits

kubelet talks to the container runtime via a gRPC socket (`/run/containerd/containerd.sock`). It does not know about Docker directly — it uses the CRI abstraction.

**Node heartbeat:** kubelet sends a `NodeLease` object update to `kube-node-lease` namespace every 10s (default). If 5 consecutive leases are missed (~40s), the node controller marks the node `Unknown`.

### kube-proxy

Network proxy on every node implementing the Service abstraction:

| Mode | Mechanism | Scale |
|---|---|---|
| `iptables` (default) | Sequential DNAT rules; O(n) per packet | Degrades at 10k+ services |
| `ipvs` | Hash-table lookup; O(1) | Better at high service counts |
| `eBPF` (Cilium) | Kernel-bypass via BPF maps | Fastest; eliminates iptables entirely |

> [!TIP]
> For clusters with more than ~500 services, switch to ipvs mode or deploy Cilium with kube-proxy replacement enabled to avoid iptables rule evaluation overhead.

### Container Runtime Interface (CRI)

gRPC API between kubelet and container runtimes. Current runtimes:

- **containerd** — Default on EKS, AKS, GKE. Manages image pulls, container lifecycle, and snapshots via plugins. The `crictl` CLI is the equivalent of `docker` for containerd.
- **CRI-O** — Lightweight runtime tuned for Kubernetes. Follows OCI spec strictly.
- **dockershim** — Removed in Kubernetes 1.24. Clusters still running Docker must migrate.

Container runtime internals (containerd → runc):
1. kubelet calls containerd via CRI gRPC
2. containerd calls `containerd-shim` to manage lifecycle isolation
3. `containerd-shim` calls `runc` (OCI runtime) to set up namespaces and cgroups and exec the process

**Secure runtimes:** `gVisor` (runs processes in a user-space kernel) and `Kata Containers` (lightweight VM per pod) provide additional isolation for multi-tenant or untrusted workloads. Configured via `RuntimeClass`.

---

## Pod Lifecycle

### Pod Phases

| Phase | Meaning |
|---|---|
| `Pending` | Accepted by API server; scheduler hasn't placed it or images are still pulling |
| `Running` | Node assigned; at least one container is running |
| `Succeeded` | All containers exited with code 0; won't restart |
| `Failed` | All containers terminated; at least one non-zero exit |
| `Unknown` | Node communication lost |

### Container States

`Waiting` → `Running` → `Terminated`

On `Terminated`, examine `exitCode`:
- `0` — Clean exit (entrypoint ran to completion)
- `1` — Application error
- `137` — OOMKilled (SIGKILL from kernel OOM)
- `139` — Segmentation fault (SIGSEGV)
- `143` — SIGTERM (graceful shutdown)

### Probes

**Liveness probe** — Is the container alive? Failure → container restart. Use to recover from deadlock or hung state. Do NOT use for slow startup (use startupProbe instead).

**Readiness probe** — Is the container ready to receive traffic? Failure → remove pod IP from Service endpoints. Container is NOT restarted. Use for apps that take time to warm up or go through temporary backpressure.

**Startup probe** — One-time check on container start. Disables liveness/readiness until it passes. `failureThreshold × periodSeconds` gives the startup budget. Use for legacy apps with unpredictable startup time.

Probe mechanisms: `httpGet`, `tcpSocket`, `exec`, `grpc`

```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
  initialDelaySeconds: 10
  periodSeconds: 10
  failureThreshold: 3

startupProbe:
  httpGet:
    path: /healthz
    port: 8080
  failureThreshold: 30    # 30 × 10s = 5 min startup budget
  periodSeconds: 10
```

### Init Containers

Run sequentially before main containers start. Each must succeed before the next runs. If an init container fails, the pod is restarted (subject to `restartPolicy`).

Use cases:
- Wait for a dependency: `until nslookup db; do sleep 2; done`
- Run DB migrations before app starts
- Pre-populate a shared volume (`emptyDir`) with config
- Set file permissions on a PVC mount (via `chown`)

### Lifecycle Hooks

`postStart` — Runs after container is created. Executes concurrently with the entrypoint (no guarantee of ordering). Use for lightweight registration tasks.

`preStop` — Runs before SIGTERM is sent. Blocks container termination. Use to drain in-flight connections. Kubernetes adds a 30-second grace period (`terminationGracePeriodSeconds`) — preStop + app shutdown must complete within this window or SIGKILL is sent.

```yaml
lifecycle:
  preStop:
    exec:
      command: ["/bin/sh", "-c", "sleep 5"]  # Wait for LB to drain
```

### Restart Policies

| Policy | Used By |
|---|---|
| `Always` (default) | Deployments, StatefulSets, DaemonSets |
| `OnFailure` | Jobs |
| `Never` | One-shot pods, debugging |

### QoS Classes

| Class | Condition | Eviction Order |
|---|---|---|
| `Guaranteed` | requests == limits for ALL containers | Last |
| `Burstable` | At least one container has requests < limits | Middle |
| `BestEffort` | No requests or limits | First |

> [!IMPORTANT]
> Production workloads should target `Guaranteed` QoS. `BestEffort` pods are the first victims of node memory pressure. Set `requests == limits` for latency-sensitive services.

---

## Scheduling

### Topology Spread Constraints

Ensures pods are spread across failure domains (zones, nodes, racks):

```yaml
topologySpreadConstraints:
- maxSkew: 1
  topologyKey: topology.kubernetes.io/zone
  whenUnsatisfiable: DoNotSchedule
  labelSelector:
    matchLabels:
      app: frontend
```

`maxSkew` is the maximum allowed difference between the most and least populated domains. `DoNotSchedule` makes it a hard constraint; `ScheduleAnyway` is a soft preference.

### Taints and Tolerations

```bash
# Taint a node to repel all pods except those that tolerate it
kubectl taint nodes gpu-node-1 dedicated=gpu:NoSchedule

# NoExecute also evicts currently-running pods
kubectl taint nodes spot-node spot=true:NoExecute

# Add toleration to a pod spec
tolerations:
- key: "dedicated"
  operator: "Equal"
  value: "gpu"
  effect: "NoSchedule"

# With tolerationSeconds — pod will be evicted after 60s
- key: "spot"
  operator: "Equal"
  value: "true"
  effect: "NoExecute"
  tolerationSeconds: 60
```

### Node Affinity vs. Pod Affinity

**Node Affinity** — Constrains pod to nodes by node labels:

```yaml
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:  # Hard
      nodeSelectorTerms:
      - matchExpressions:
        - key: disktype
          operator: In
          values: ["ssd"]
    preferredDuringSchedulingIgnoredDuringExecution:  # Soft
    - weight: 100
      preference:
        matchExpressions:
        - key: zone
          operator: In
          values: ["us-east-1a"]
```

**Pod Anti-Affinity** — Spread replicas across nodes:

```yaml
affinity:
  podAntiAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
    - labelSelector:
        matchLabels:
          app: frontend
      topologyKey: kubernetes.io/hostname  # Unique per node
```

---

## Networking

### CNI Model

Every pod gets a unique IP. Pods communicate without NAT — the IP a pod sees itself as is the same IP others use to reach it. CNI plugins implement this:

**Flannel** — VXLAN overlay. Simple, no NetworkPolicy support natively. Encapsulation adds ~50 bytes per packet overhead.

**Calico** — L3 routing via BGP (no encapsulation in native mode). Full NetworkPolicy support. eBPF dataplane available. Best for production bare-metal.

**Cilium** — eBPF-native. Replaces kube-proxy entirely. Supports L7 NetworkPolicy (HTTP method/path filtering). Provides Hubble for network observability. Best for high-performance and zero-trust requirements.

**Weave** — Mesh overlay with encryption. Simple but slower than Calico.

### Services

```
ClusterIP     → Virtual IP (VIP) only reachable within cluster
NodePort      → ClusterIP + port exposed on every node (30000-32767)
LoadBalancer  → NodePort + cloud LB with external IP
ExternalName  → CNAME alias, no proxy
Headless      → clusterIP: None; DNS returns pod IPs directly
```

CoreDNS DNS records:
- Service: `<svc>.<ns>.svc.cluster.local`
- Pod: `<pod-ip-dashes>.<ns>.pod.cluster.local`
- StatefulSet Pod: `<pod-name>.<headless-svc>.<ns>.svc.cluster.local`

**Endpoint slices:** Replaced `Endpoints` objects in modern Kubernetes. Each EndpointSlice holds ≤100 endpoints, reducing API server fan-out when a service has thousands of pods.

### Ingress and Gateway API

**Ingress** — L7 routing rule set. Requires an Ingress Controller (nginx, Traefik, HAProxy, AWS ALB). Supports host-based routing, path-based routing, TLS termination.

```yaml
kind: Ingress
spec:
  tls:
  - hosts: [app.example.com]
    secretName: app-tls
  rules:
  - host: app.example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api-svc
            port:
              number: 80
```

**Gateway API** — Successor to Ingress. Role-separated:
- `GatewayClass` — Infrastructure provider selects implementation
- `Gateway` — Cluster operator defines listener (IP, port, TLS)
- `HTTPRoute` / `GRPCRoute` — Developer attaches routes to a gateway

Supports native traffic splitting (canary weights), header matching, and request mirroring without proprietary annotations.

### CoreDNS

Runs as a Deployment in `kube-system`. Configured via a `ConfigMap` (`coredns`):

```
.:53 {
    errors
    health
    ready
    kubernetes cluster.local in-addr.arpa ip6.arpa {
        pods insecure
        fallthrough in-addr.arpa ip6.arpa
    }
    forward . /etc/resolv.conf   # Upstream DNS
    cache 30
    loop
    reload
    loadbalance
}
```

Default `ndots: 5` in pod `/etc/resolv.conf` means 5 search-domain lookups before external resolution. Override in pod spec:

```yaml
dnsConfig:
  options:
  - name: ndots
    value: "2"
```

### Network Policies

Additive allow rules — a pod with no matching policy accepts all traffic. Default-deny pattern:

```yaml
kind: NetworkPolicy
spec:
  podSelector: {}          # Selects all pods in namespace
  policyTypes: [Ingress, Egress]
  # No ingress/egress rules = deny all
```

Then add explicit allows:

```yaml
kind: NetworkPolicy
spec:
  podSelector:
    matchLabels:
      app: backend
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    - namespaceSelector:
        matchLabels:
          name: monitoring
    ports:
    - protocol: TCP
      port: 8080
```

---

## Storage

### PersistentVolume / PVC / StorageClass

**PV lifecycle:**
1. Admin provisions PV (static) or StorageClass creates it (dynamic)
2. PVC requests storage matching size and access mode
3. Kubernetes binds PVC to the best-matching PV
4. Pod mounts the PVC as a volume

**Access modes:**

| Mode | Shorthand | Multi-node |
|---|---|---|
| ReadWriteOnce | RWO | Single node |
| ReadOnlyMany | ROX | Multiple nodes (read) |
| ReadWriteMany | RWX | Multiple nodes (read-write) |
| ReadWriteOncePod | RWOP | Single pod (K8s 1.22+) |

RWX supported by: NFS, CephFS, AWS EFS, Azure Files, GlusterFS.

**Reclaim policies:**
- `Delete` — PV and underlying storage deleted when PVC deleted (default for cloud disks)
- `Retain` — PV preserved; manually reclaim data then delete PV
- `Recycle` — Deprecated; used `rm -rf` on volume before rebinding

**StorageClass with WaitForFirstConsumer:**

```yaml
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
  encrypted: "true"
volumeBindingMode: WaitForFirstConsumer  # Critical: defer until pod is scheduled
reclaimPolicy: Delete
allowVolumeExpansion: true
```

`WaitForFirstConsumer` prevents the classic zone-mismatch bug where a PV is provisioned in `us-east-1a` but the pod lands in `us-east-1b`.

### CSI (Container Storage Interface)

The standard plugin interface for storage vendors. CSI drivers run as pods in the cluster and implement:
- `CreateVolume` / `DeleteVolume` — lifecycle
- `ControllerPublishVolume` — attach disk to node
- `NodeStageVolume` / `NodePublishVolume` — mount on node/pod

**Volume Snapshots** (CSI feature):

```yaml
# Take a snapshot
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
spec:
  volumeSnapshotClassName: csi-aws-vss
  source:
    persistentVolumeClaimName: db-pvc

# Restore from snapshot
apiVersion: v1
kind: PersistentVolumeClaim
spec:
  dataSource:
    name: db-snapshot
    kind: VolumeSnapshot
    apiGroup: snapshot.storage.k8s.io
  resources:
    requests:
      storage: 100Gi
```

---

## RBAC

Four core objects:

| Object | Scope | Purpose |
|---|---|---|
| `Role` | Namespace | Grants verbs on resources in one namespace |
| `ClusterRole` | Cluster | Grants verbs on cluster-scoped or all-namespace resources |
| `RoleBinding` | Namespace | Binds Role/ClusterRole to subjects within a namespace |
| `ClusterRoleBinding` | Cluster | Binds ClusterRole to subjects cluster-wide |

Subjects: `User` (external auth), `Group`, `ServiceAccount` (in-cluster identity)

```yaml
# Least-privilege example
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: production
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods", "pods/log"]
  verbs: ["get", "list", "watch"]
---
kind: RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  namespace: production
  name: pod-reader-binding
subjects:
- kind: ServiceAccount
  name: monitor-sa
  namespace: monitoring
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

**IRSA / Workload Identity:** Bind a Kubernetes ServiceAccount to a cloud IAM role using OIDC federation. The pod gets short-lived credentials via projected token rather than long-lived access keys.

```bash
# AWS: annotate ServiceAccount with IAM role ARN
kubectl annotate sa my-sa \
  eks.amazonaws.com/role-arn=arn:aws:iam::123456789:role/my-role
```

**Audit RBAC drift:**
```bash
kubectl auth can-i --list --as system:serviceaccount:default:my-sa
kubectl get clusterrolebindings -o json | jq '.items[] | select(.subjects[]?.name=="cluster-admin")'
```

---

## Admission Controllers

Request flow through the API server:

```
AuthN → AuthZ → Mutating Webhooks → Object Validation → Validating Webhooks → etcd
```

**MutatingAdmissionWebhook** — Can modify the object before persistence. Common uses:
- Inject sidecar containers (Istio, Linkerd, Vault agent)
- Set default resource requests/limits
- Add labels or annotations
- Apply pod security context

**ValidatingAdmissionWebhook** — Can only allow or deny. Common uses:
- Enforce required labels (`team`, `env`, `cost-center`)
- Block `latest` image tag
- Require resource requests to be set
- Enforce approved container registries

**Webhook configuration:**

```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingWebhookConfiguration
metadata:
  name: policy-webhook
webhooks:
- name: validate.policies.example.com
  rules:
  - apiGroups: [""]
    apiVersions: ["v1"]
    operations: ["CREATE", "UPDATE"]
    resources: ["pods"]
  clientConfig:
    service:
      name: policy-webhook
      namespace: policy-system
      path: /validate
    caBundle: <base64-ca>
  failurePolicy: Fail    # Fail = block; Ignore = allow through on error
  admissionReviewVersions: ["v1"]
  sideEffects: None
```

> [!CAUTION]
> `failurePolicy: Fail` on a webhook that becomes unavailable will block ALL pod creation. Use `namespaceSelector` to exclude `kube-system` and have a webhook availability SLO.

**OPA Gatekeeper:**
```yaml
# ConstraintTemplate defines the Rego policy
# Constraint instance applies it to resources
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sRequiredLabels
metadata:
  name: require-team-label
spec:
  match:
    kinds:
    - apiGroups: [""]
      kinds: ["Namespace"]
  parameters:
    labels: ["team"]
```

**Kyverno** (YAML-native, no Rego):
```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: disallow-latest-tag
spec:
  validationFailureAction: Enforce
  rules:
  - name: check-image-tag
    match:
      resources:
        kinds: ["Pod"]
    validate:
      message: "Using ':latest' is not allowed"
      pattern:
        spec:
          containers:
          - image: "!*:latest"
```

**Pod Security Admission (PSA)** — Built-in controller replacing PodSecurityPolicy. Apply at the namespace level:

```bash
kubectl label namespace production \
  pod-security.kubernetes.io/enforce=restricted \
  pod-security.kubernetes.io/audit=restricted \
  pod-security.kubernetes.io/warn=restricted
```

Levels: `privileged` (no restrictions) → `baseline` (blocks known privilege escalations) → `restricted` (hardened).

---

## CRDs and Operators

### Custom Resource Definitions

CRDs extend the Kubernetes API with new resource types stored in etcd:

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: postgresclusters.db.example.com
spec:
  group: db.example.com
  versions:
  - name: v1
    served: true
    storage: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              replicas:
                type: integer
              version:
                type: string
  scope: Namespaced
  names:
    plural: postgresclusters
    singular: postgrescluster
    kind: PostgresCluster
```

### Operator Pattern

An Operator is a custom controller implementing domain-specific operational knowledge:

**Reconciliation loop** (controller-runtime):
1. Watch for events on the custom resource (Create, Update, Delete)
2. Read the current state of the world (from API server and external systems)
3. Compute the diff between desired and actual state
4. Act: create/update/delete owned resources (StatefulSets, Services, Secrets)
5. Update the custom resource `status` subresource
6. Re-queue on transient errors with exponential backoff

**Operator maturity levels:**
1. Basic Install — deploys the application
2. Seamless Upgrades — handles version upgrades
3. Full Lifecycle — backup, restore, failure recovery
4. Deep Insights — metrics, alerts, dashboards
5. Auto Pilot — horizontal/vertical scaling, anomaly detection

**Key frameworks:** `controller-runtime` (Go), `Operator SDK`, `Kopf` (Python), `JOSDK` (Java).

---

## Autoscaling

### Horizontal Pod Autoscaler (HPA)

Polls the Metrics API at `--horizontal-pod-autoscaler-sync-period` (default 15s):

```
desiredReplicas = ceil(currentReplicas × (currentMetric / desiredMetric))
```

Example: 3 replicas, CPU usage 80%, target 50%:
`ceil(3 × 80/50) = ceil(4.8) = 5`

Stabilization window (default: 5m scale-down, 0 scale-up) prevents flapping.

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  minReplicas: 2
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 60
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "100"
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Pods
        value: 2
        periodSeconds: 60
```

> [!IMPORTANT]
> HPA requires `resources.requests.cpu` to be set on pods. Without it, the utilization percentage has no denominator and HPA reports `unknown` metrics.

### Vertical Pod Autoscaler (VPA)

Adjusts CPU/memory requests/limits based on historical usage (min 24h of data for stable recommendations):

| Mode | Behavior |
|---|---|
| `Off` | Recommendations only, no changes |
| `Initial` | Sets resources at pod creation only |
| `Auto` | Evicts pods and recreates with new values |

Limitations:
- Requires pod eviction to apply changes (downtime on single-replica deployments)
- Conflicts with HPA on CPU metrics — cannot run both in `Auto` mode simultaneously
- 24+ hours for recommendations to stabilize

### KEDA (Kubernetes Event Driven Autoscaling)

KEDA extends HPA with event-source scalers: Kafka lag, SQS queue depth, Prometheus queries, Redis lists, Azure Service Bus, Cron schedule, etc.

Scales to **zero** when queue is empty (HPA minimum is 1).

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: worker-scaler
spec:
  scaleTargetRef:
    name: worker-deployment
  minReplicaCount: 0     # Scale to zero
  maxReplicaCount: 50
  triggers:
  - type: aws-sqs-queue
    metadata:
      queueURL: https://sqs.us-east-1.amazonaws.com/123/my-queue
      queueLength: "10"       # Target: 10 messages per replica
      awsRegion: us-east-1
```

### Cluster Autoscaler

Scales node groups based on pending pods (scale-up) and underutilized nodes (scale-down).

**Scale-up trigger:** A pod is unschedulable due to resource constraints → CA determines which node group can accommodate it → adds a node.

**Scale-down eligibility:** A node is underutilized (`sum(pod requests) < 50% of allocatable`) for `scale-down-unneeded-time` (default 10m) AND all pods on the node can be rescheduled elsewhere.

**Scale-down blockers:**
- Pod with no controller (standalone pod)
- Pod with local storage
- DaemonSet pod
- Pod violating a PodDisruptionBudget
- Pod with `cluster-autoscaler.kubernetes.io/safe-to-evict: "false"` annotation

### Karpenter

Node provisioner from AWS (also supported on Azure/GCP) as an alternative to Cluster Autoscaler:

- Provisions individual nodes (not fixed node groups) based on exact pod requirements
- **Consolidation** — Proactively replaces underutilized nodes with fewer, better-fitting instances
- Supports diverse instance types and spot/on-demand mix via `NodePool` and `EC2NodeClass`
- Provisions nodes in 30-60s vs. Cluster Autoscaler's 2-5 minutes

```yaml
apiVersion: karpenter.sh/v1beta1
kind: NodePool
metadata:
  name: default
spec:
  template:
    spec:
      requirements:
      - key: karpenter.sh/capacity-type
        operator: In
        values: ["spot", "on-demand"]
      - key: kubernetes.io/arch
        operator: In
        values: ["amd64", "arm64"]
  limits:
    cpu: 1000
  disruption:
    consolidationPolicy: WhenUnderutilized
    consolidateAfter: 30s
```

---

## Multi-Tenancy Patterns

### Soft Multi-Tenancy (Namespace-based)

- Namespace per team with RBAC `Role` + `RoleBinding` (no cluster-wide access)
- `ResourceQuota` caps CPU, memory, and object counts per namespace
- `LimitRange` sets default requests/limits for containers that don't specify them
- Default-deny `NetworkPolicy` in each namespace with explicit allow rules
- `OPA Gatekeeper` / `Kyverno` enforces policy: no `hostNetwork`, no `privileged`, approved registries only
- Hierarchical Namespace Controller (HNC) for teams with sub-teams

### Hard Multi-Tenancy (vcluster)

Virtual Clusters run entire Kubernetes control planes inside a namespace of the host cluster. Each tenant gets isolated API server, etcd (SQLite), and controller-manager.

- Tenant has `cluster-admin` inside their vcluster (can install CRDs)
- The vcluster syncer translates virtual pod creation into real pods on host nodes
- Host cluster still enforces resource limits and network policies

### Cost Attribution

- Label namespaces with `team`, `env`, `cost-center`
- Use **Kubecost** or **OpenCost** to aggregate costs by label
- `ResourceQuota` per namespace prevents a single team from monopolizing the cluster
- Showback reports → chargeback policies

```bash
# Quick resource usage by namespace
kubectl get quota -A
kubectl top pods -A --sort-by=memory | head -20
```

### Cluster API (CAPI) — Clusters-as-Code

Manage Kubernetes cluster lifecycle via Kubernetes-native YAML:

```yaml
apiVersion: cluster.x-k8s.io/v1beta1
kind: Cluster
metadata:
  name: prod-cluster
spec:
  clusterNetwork:
    pods:
      cidrBlocks: ["10.0.0.0/16"]
  infrastructureRef:
    apiVersion: infrastructure.cluster.x-k8s.io/v1beta2
    kind: AWSCluster
    name: prod-cluster
  controlPlaneRef:
    apiVersion: controlplane.cluster.x-k8s.io/v1beta1
    kind: KubeadmControlPlane
    name: prod-cp
```

A Management Cluster provisions and upgrades Workload Clusters. One YAML file = one cluster in any cloud.
# Advanced Networking & Security (7 YOE)

Mid-level engineers configure Ingress resources to expose web apps. Senior engineers replace the entire internal networking stack of Kubernetes to enforce zero-trust, kernel-level fast paths, and global policy controls.

---

## 1. The eBPF Networking Revolution (Cilium)

By default, Kubernetes uses `kube-proxy` combined with Linux `iptables` to route traffic to Services. 
- **The Problem:** `iptables` was designed in the 1990s as a firewall, not a dynamic load balancer. When a cluster has 10,000 services, `kube-proxy` must evaluate massive sequential rule lists for every packet, causing massive CPU overhead and tail latency spikes.

### The Cilium Solution
Cilium is the modern CNI (Container Network Interface) standard replacing `kube-proxy` entirely. It is built on **eBPF (Extended Berkeley Packet Filter)**.
- eBPF allows safe programs to run inside the Linux kernel on network events. 
- Instead of using slow `iptables` routing, Cilium injects a hash-map lookup directly into the kernel's network socket layer. 
- A packet leaving Pod A destined for Pod B does not traverse the host's standard TCP/IP stack; eBPF routes it optimally and instantaneously.

**Security Benefit:** Standard NetworkPolicies only filter at Layer 3/4 (IP/Port). Cilium Network Policies understand Layer 7 (HTTP/gRPC/Kafka). You can create a policy: *“Pod A can only make HTTP GET requests to Pod B on path `/api/data`, and all POST requests are dropped.”*

---

## 2. Ingress vs. Gateway API

The `Ingress` object is dying. It was primarily designed for simple HTTP/HTTPS host path routing and forced vendors to use confusing, non-standard annotations (e.g., `nginx.ingress.kubernetes.io/rewrite-target`) for advanced routing.

### The Kubernetes Gateway API
The Gateway API is the successor to Ingress. It is expressive, extensible, and—most importantly—**Role-Oriented**.

It divorces the management of the infrastructure from the developer routes:
1. **Infrastructure Provider:** Deploys underlying Load Balancers in the Cloud.
2. **Cluster Operator:** Creates the `GatewayClass` (selecting the implementation like Istio/Nginx) and `Gateway` (binding the IP/port).
3. **Application Developer:** Creates an `HTTPRoute` detailing the path matching, traffic splitting (canary weights), and header manipulations. They attach these routes to the central `Gateway`.

---

## 3. The Evolution of the Service Mesh

A Service Mesh provides mutual TLS (mTLS), circuit breaking, and telemetry across all microservices without changing application code. 

### Generation 1: The Sidecar Proxy (Istio / Linkerd)
- The mesh injects a reverse proxy (Envoy) into every single Pod forming the cluster data plane.
- **Problem:** If you have 5,000 pods, you now have 5,000 Envoy proxies continually scraping CPU and RAM. It creates massive operational overhead and drastically impacts cluster startup times.

### Generation 2: Ambient Mesh / Sidecarless (Istio Ambient / Cilium)
Modern multi-tenant architectures are shifting to **Sidecarless** Service Meshes.
- It uses a per-node proxy (a DaemonSet running Envoy) rather than a per-pod sidecar. 
- Traffic leaving a pod is intercepted at the kernel level (via eBPF/ztunnel) and redirected securely to the node-level proxy for L7 telemetry and L4 mTLS encryption.
- **Benefit:** Reduces resource consumption by 70+%. You do not have to restart application pods to inject/upgrade sidecars.

---

## 4. Policy as Code: Admission Controllers

RBAC restricts *who* can create objects in Kubernetes, but **Admission Controllers** restrict *what* can be inside those objects. 

### OPA Gatekeeper vs. Kyverno
Before a resource (like a Pod) is saved to `etcd`, the API Server sends a request to a Mutating/Validating Webhook to ask if the resource complies with company policy.

- **OPA Gatekeeper:** Uses Rego, a declarative query language. Extremely powerful but notoriously complex to write and maintain. 
- **Kyverno:** Kubernetes-native policy management. Policies are written in standard YAML. 

**Senior Engineer Use Cases for Kyverno:**
1. **Validation:** Reject any Pod that runs as `root`.
2. **Mutation:** Automatically inject a sidecar container or specific tolerations into a pod manifest based on its namespace.
3. **Generation:** Whenever a new developer namespace is created, automatically generate standard `NetworkPolicies`, `RoleBindings`, and `ResourceQuotas` explicitly for that namespace.

---

## API Server Mechanics: Watch, List, and Server-Side Apply

### The Watch Cache

The API server maintains an in-memory watch cache populated by etcd watch events. When clients do LIST requests with `resourceVersion=0`, they hit the cache (not etcd directly). This is critical for scale — thousands of informers in a cluster all doing LIST would overwhelm etcd without the cache.

Watch cache is per-resource and stores the last N events (default 1000 per resource type). If a client's `resourceVersion` falls outside the cache window, they get a 410 Gone and must restart their watch from `resourceVersion=0`.

### Server-Side Apply (SSA)

SSA (GA in 1.22) moves the three-way merge logic from kubectl to the API server. The server tracks **field ownership** — each field records which manager last applied it.

```yaml
# Field manager example in managedFields
managedFields:
- manager: kubectl
  operation: Apply
  fieldsV1:
    f:spec:
      f:replicas: {}
- manager: my-operator
  operation: Apply
  fieldsV1:
    f:spec:
      f:template:
        f:spec:
          f:containers:
            k:{"name":"app"}:
              f:image: {}
```

If two managers try to own the same field, SSA returns a conflict error (409). This prevents kubectl and an operator from fighting over the same field. Operators should use SSA with `force: true` for fields they own exclusively.

---

## etcd Internals: Raft Consensus

etcd uses the Raft consensus algorithm. Key properties:

**Leader election**: The node with the most up-to-date log and a majority vote becomes leader. Split votes trigger re-election with randomized timeouts.

**Log replication**: The leader appends entries to its log, sends AppendEntries RPCs to followers, and marks entries committed once a majority acknowledge.

**Quorum requirement**: A 3-node etcd cluster requires 2 nodes for quorum (can tolerate 1 failure). A 5-node cluster requires 3 (can tolerate 2 failures). An even number is NEVER recommended — a 4-node cluster still requires 3 for quorum (can tolerate 1 failure), same as 3 nodes but with more overhead.

**Performance sensitivity**: etcd is sensitive to disk write latency (fsync calls). AWS EBS gp2 is marginal; NVMe/io2 is recommended. `etcd_disk_wal_fsync_duration_seconds_bucket` histogram in Prometheus reveals disk issues.

**DB size management**: etcd compacts old key revisions to prevent unbounded growth. `--auto-compaction-mode=periodic` with `--auto-compaction-retention=8h` is a safe default. After compaction, run `etcdctl defrag` to reclaim space on disk.

---

## kube-proxy Modes: iptables vs IPVS

### iptables Mode (default pre-1.30)
- Every Service creates DNAT rules in the `KUBE-SERVICES` chain
- Random endpoint selection via `statistic` module (probability-based)
- O(N) rule traversal for every packet — scales poorly beyond ~10,000 rules
- Debugging: `iptables-save | grep KUBE`

### IPVS Mode
- Uses Linux IPVS (IP Virtual Server) for load balancing — designed for high-performance L4 LB
- Hash table lookups: O(1) regardless of service count
- Supports additional load balancing algorithms: round-robin, least-connection, source hash, etc.
- Enable: `--proxy-mode=ipvs` in kube-proxy config; requires `ip_vs` kernel modules
- Debugging: `ipvsadm -Ln`

### eBPF/Cilium (no kube-proxy)
- Complete replacement: no iptables, no IPVS
- eBPF maps for O(1) service lookup at the TC hook level
- Enable: deploy Cilium with `kubeProxyReplacement=true`

---

## Secrets Encryption at Rest

By default, Secrets are stored in etcd as base64-encoded plaintext. Anyone with etcd access can read all Secrets.

**Enabling encryption**:
```yaml
# /etc/kubernetes/encryption-config.yaml
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
- resources: [secrets]
  providers:
  - aescbc:
      keys:
      - name: key1
        secret: <base64-encoded-32-byte-key>
  - identity: {}  # fallback: allows reading unencrypted secrets during migration
```

Add to API server: `--encryption-provider-config=/etc/kubernetes/encryption-config.yaml`

After enabling, existing secrets must be re-encrypted:
```bash
kubectl get secrets -A -o json | kubectl replace -f -
```

**Better alternatives**: Use KMS providers (AWS KMS, GCP KMS, Azure Key Vault) — the encryption key is never on the API server node, and key rotation is handled by the KMS.

**Best practice**: Don't store real secrets in Kubernetes Secrets at all. Use External Secrets Operator + HashiCorp Vault or cloud secret managers.

---

## Cluster Autoscaling: Karpenter vs Cluster Autoscaler

### Cluster Autoscaler Internals
CA runs a simulation loop every 10s:
1. Get list of unschedulable pods
2. For each pod, simulate scheduling against each node group's template node
3. If simulation succeeds, scale up that node group
4. Scale-down: find nodes where all pods could fit on other nodes; drain after 10 minutes of underutilization

**Limitations**: Node groups must be pre-defined. Instance type is fixed per node group. Bin-packing is done against node group templates, not actual available instance types.

### Karpenter Architecture
Karpenter watches for `pods.kubernetes.io/scheduling-failure` events. For each unschedulable pod:
1. Evaluates `NodePool` constraints (instance families, zones, capacity types)
2. Calls EC2 Fleet API (or equivalent) to find the cheapest instance that fits
3. Registers the node in Kubernetes BEFORE the instance is running (fast node registration)
4. Schedules the pod to the provisioned node

**Consolidation loop**: Karpenter periodically asks "can I fit all workloads onto fewer nodes?" — simulates removing each node and checks if pods can be rescheduled. If yes, it cordons, drains, and terminates the node.

---

## Observability Stack on Kubernetes

### Prometheus Architecture for Kubernetes

```
Kubernetes API Server
        ↓ (SD: service discovery)
Prometheus → TSDB (local storage)
        ↓
AlertManager → PagerDuty/Slack
        ↓
Grafana (dashboards)
```

Key service discovery configs for Kubernetes:
- `kubernetes_sd_configs` role `pod`: scrapes pods with annotation `prometheus.io/scrape: "true"`
- `kubernetes_sd_configs` role `endpoints`: scrapes service endpoints
- `kubernetes_sd_configs` role `node`: scrapes node exporters via kubelet

**Critical metrics to monitor**:
```
# API server
apiserver_request_duration_seconds_p99
apiserver_current_inflight_requests

# etcd
etcd_server_leader_changes_seen_total (should be ~0)
etcd_disk_wal_fsync_duration_seconds_bucket

# Nodes
node_cpu_utilization
node_memory_MemAvailable_bytes
kubelet_running_pods

# Workloads
kube_deployment_status_replicas_unavailable
kube_pod_container_status_restarts_total
container_oom_events_total
```

### OpenTelemetry on Kubernetes

The OTel Operator manages `OpenTelemetryCollector` CRDs. Sidecar injection mode: annotate pods with `instrumentation.opentelemetry.io/inject-<language>: "true"` for zero-code-change auto-instrumentation.

Collector pipeline: OTLP receive → filter/batch processors → export to Jaeger/Tempo (traces), Prometheus (metrics), Loki (logs).

---

## Advanced Scheduling: Preemption and Gang Scheduling

### Preemption
When a high-priority pod can't be scheduled, the scheduler tries to evict lower-priority pods to make room. Algorithm:
1. Find nodes where evicting lower-priority pods would make the high-priority pod fit
2. Select the node with the fewest evictions and lowest victim priority sum
3. Preempt (evict with `gracePeriod`) the victims

Configure via `PriorityClass`:
```yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: high-priority
value: 1000000
preemptionPolicy: PreemptLowerPriority  # or Never (for priority without preemption)
globalDefault: false
```

### Gang Scheduling
All-or-nothing scheduling: either ALL pods of a group are scheduled, or none are. Critical for ML training jobs — a TensorFlow job that can only run 7 of 8 workers is worthless.

Kubernetes doesn't support this natively. Solutions:
- **Volcano** (CNCF): full batch scheduler with gang scheduling, queue fairness
- **Yunikorn** (Apache): queue-based scheduling with gang scheduling
- **Scheduler Framework Permit phase**: custom plugins can implement gang scheduling by holding all pods in the permit phase until the full group is ready

---

## Operator Pattern: Controller-Runtime Deep Dive

A Kubernetes operator is a controller that understands domain-specific operational knowledge. Built on the controller-runtime library:

```go
// Reconcile is called whenever the watched resource changes
func (r *DatabaseReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    db := &myv1.Database{}
    if err := r.Get(ctx, req.NamespacedName, db); err != nil {
        return ctrl.Result{}, client.IgnoreNotFound(err)
    }
    
    // Reconcile: make actual state match desired state
    if err := r.ensureDeployment(ctx, db); err != nil {
        return ctrl.Result{RequeueAfter: 30 * time.Second}, err
    }
    
    return ctrl.Result{}, nil
}
```

**Key patterns**:
- **Idempotency**: Reconcile is called multiple times; must be safe to call N times
- **Requeue**: Return `RequeueAfter` to check state again; return empty `Result{}` when done
- **Status conditions**: Use `metav1.Condition` slice in status subresource, not free-form fields
- **Owner references**: Set owner reference on child resources so they're garbage collected with the CR
- **Finalizers**: Add a finalizer on creation; remove it after external cleanup in deletion path

**Testing**: Use `envtest` (from controller-runtime) to run a real API server + etcd in tests without a full cluster.
