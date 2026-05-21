# Enterprise Kubernetes Architecture & Fleet Management

```
Enterprise Kubernetes Architecture
├── The Four Enterprise Challenges
│   ├── Scale — 100+ clusters; multi-region, multi-cloud
│   ├── Governance — security policies, quotas, compliance across all clusters
│   ├── Standardization — consistent networking, observability, configs
│   └── Operations — upgrades, disaster recovery, SLA maintenance
├── Control Plane Internals
│   ├── kube-apiserver — REST+gRPC frontend; AuthN→AuthZ→Mutating→Validating→etcd
│   ├── etcd (Raft cluster)
│   │   ├── All state under /registry/<group>/<resource>/<ns>/<name>
│   │   ├── Protocol Buffers (not JSON) for wire efficiency
│   │   ├── Default quota 2GB → cluster read-only if exceeded
│   │   └── Operations: snapshot save / compact / defrag / endpoint health
│   ├── kube-scheduler — Filter → Score → Bind; pluggable via Scheduling Framework
│   ├── kube-controller-manager — ~30 controllers; List+Watch → reconcile
│   └── cloud-controller-manager — Node/Route/Service controllers; talks to cloud API
├── API Priority and Fairness (APF)
│   ├── Replaces --max-requests-inflight with fine-grained flow queuing
│   ├── PriorityLevelConfiguration — nominalConcurrencyShares + queue settings
│   ├── FlowSchema — maps subjects/resources to priority levels
│   └── Goal: kubelet heartbeats never starved by CI bots doing bulk LISTs
├── Cluster API (CAPI) — Clusters-as-Code
│   ├── Management cluster provisions Workload clusters via K8s YAML
│   ├── clusterctl init / cluster.yaml apply / clusterctl describe
│   ├── KubeadmControlPlane (KCP) — handles rolling CP upgrades (maxSurge)
│   └── AWSCluster / AWSMachineTemplate — infra-specific providers
├── vcluster — Virtual Clusters (Hard Multi-Tenancy)
│   ├── Full K8s control plane inside a namespace (virtual API server + SQLite)
│   ├── Tenant gets cluster-admin inside vcluster; host enforces resource limits
│   ├── vcluster syncer translates virtual pods to real pods on host nodes
│   └── Host node pool must be sized to include ALL vcluster pod overhead
├── Multi-Tenancy RBAC Patterns
│   ├── Namespace-scoped Role + RoleBinding (not ClusterRoleBinding)
│   ├── OIDC group binding — subjects: kind: Group; name: matches OIDC claim
│   └── ResourceQuota + LimitRange per namespace per team
├── Cluster Upgrades
│   ├── Pre-check: pluto detect deprecated APIs in manifests + live cluster
│   ├── Control plane first (kubeadm upgrade apply)
│   ├── Cordon → drain → upgrade kubelet/kubectl → uncordon (per node)
│   └── Constraint: no skipping minor versions; node kubelet ≤ control plane version
└── Network Policy Production Patterns
    ├── default-deny-all (both Ingress + Egress) per namespace
    ├── allow-ingress-controller — namespaceSelector: ingress-nginx namespace
    └── allow-dns — egress UDP:53 to kube-system (mandatory or pods can't resolve DNS)
```

## First Principles

- You have 100+ clusters to manage — treat clusters as **cattle, not pets**; Cluster API applies the same declarative desired-state model to cluster lifecycle that Kubernetes applies to pod lifecycle.
- Cluster API servers can be overwhelmed by bulk clients — **API Priority and Fairness** assigns explicit capacity shares so high-frequency CI bots cannot starve low-frequency but critical kubelet heartbeats.
- Hard multi-tenancy requires isolated control planes, not just namespaces — **vcluster** gives tenants full API server isolation without the cost of a dedicated physical cluster; the host cluster still enforces resource and network limits.
- Config and secrets externalised — resource quotas and limit ranges at the namespace level enforce **resource isolation as code**; no team can monopolise cluster capacity without a deliberate quota increase.
- Zero-downtime cluster upgrades — **KubeadmControlPlane rolling upgrades** (maxSurge: 1) create a new control plane node before deleting the old one, keeping the API server HA throughout the upgrade.

## Why Enterprise Kubernetes is Different

Running Kubernetes in production at scale introduces challenges that don't exist in development or single-cluster setups:

**The Four Enterprise Challenges:**

1. **Scale:** Managing 100+ clusters across multiple regions, clouds, and environments
2. **Governance:** Enforcing security policies, resource quotas, and compliance requirements across all clusters
3. **Standardization:** Ensuring consistent configurations, networking, and observability stacks
4. **Operations:** Upgrading control planes, handling disasters, and maintaining SLAs

This document covers the architectural patterns and tools needed to solve these challenges.

***

## Control Plane Internals

```
kube-apiserver
    │  REST + gRPC frontend for all cluster operations
    │  Validates objects, handles auth/authz, persists to etcd
    │  Webhook chain: AuthN → AuthZ → Admission Mutating → Admission Validating
    │
etcd (Raft cluster)
    │  All cluster state: Pods, Services, ConfigMaps, Secrets, CRDs
    │  Key format: /registry/<group>/<resource>/<namespace>/<name>
    │  Storage: Protocol Buffers (not JSON) for efficiency
    │  Compaction: old revisions accumulate until compacted
    │
kube-scheduler
    │  Watches for Pods with no nodeName
    │  Filtering (feasible nodes) → Scoring (best node) → Binding
    │  Extensibility: scheduler extenders, custom scheduler, scheduling plugins
    │
kube-controller-manager
    │  ~30 controllers in one process (Deployment, ReplicaSet, Node, Job...)
    │  Each controller: List+Watch → reconcile desired vs actual
    │
cloud-controller-manager (separate)
    │  Node, Route, Service (LoadBalancer) controllers
    │  Talks to cloud provider API (AWS, Azure, GCP)
```

### etcd operations

```bash
# Health check
etcdctl --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  endpoint health

# Check etcd DB size (must be < 8GB by default)
etcdctl endpoint status --write-out=table

# Compact + defrag (recover disk space)
REV=$(etcdctl endpoint status --write-out=json | jq '.[0].Status.header.revision')
etcdctl compact $REV
etcdctl defrag

# Change DB quota (default 2GiB, max 8GiB)
# etcd flag: --quota-backend-bytes=8589934592

# Backup
ETCDCTL_API=3 etcdctl snapshot save /backup/etcd-$(date +%Y%m%d).db
etcdctl snapshot status /backup/etcd-$(date +%Y%m%d).db --write-out=table
```

***

## Kubernetes Operators, Custom Controllers & Reconcilers

Kubernetes is built on the declarative reconciliation model: you state the desired state, and active control loops continuously drive the system toward that state. An **Operator** packages this operational intelligence by combining Custom Resource Definitions (CRDs) with custom controller logic.

### 1. `controller-runtime` & Reconciler Architecture
Most modern operators use the Go `controller-runtime` library (underlying Kubebuilder and Operator SDK). Understanding the internal event flow is critical for avoiding race conditions, memory leaks, and CPU exhaustion.

```
                    Kubernetes controller-runtime Event Architecture
                                                                 
  ┌────────────────────────────────────────────────────────────────────────┐
  │                            Kubernetes API Server                       │
  └───────────────────▲──────────────────────────────────▲─────────────────┘
                      │ List / Watch                     │ Write Updates
                      │ (Chunked HTTP Streams)           │ (Status / Scale)
  ┌───────────────────┼──────────────────────────────────┼─────────────────┐
  │ Operator Process  │                                  │                 │
  │                   ▼                                  │                 │
  │            ┌─────────────┐                           │                 │
  │            │  Reflector  │                           │                 │
  │            └──────┬──────┘                           │                 │
  │                   │ Pushes events                    │                 │
  │            ┌──────▼──────┐                           │                 │
  │            │  DeltaFIFO  │                           │                 │
  │            └──────┬──────┘                           │                 │
  │                   │ Pop                              │                 │
  │            ┌──────▼──────┐                           │                 │
  │            │  Informer   ├───────────┐               │                 │
  │            └──────┬──────┘           ▼               │                 │
  │                   │ Write      ┌───────────┐         │                 │
  │                   ▼            │  Lister   │         │                 │
  │            ┌─────────────┐     │  (Cache)  │         │                 │
  │            │ EventHandlers     └─────▲─────┘         │                 │
  │            └──────┬──────┘           │ Read          │                 │
  │                   │ Enqueue          │               │                 │
  │                   ▼                  │               │                 │
  │            ┌─────────────┐           │               │                 │
  │            │  Workqueue  │           │               │                 │
  │            └──────┬──────┘           │               │                 │
  │                   │ Pop Key          │               │                 │
  │                   ▼                  │               │                 │
  │            ┌─────────────┐           │               │                 │
  │            │ Reconcile() ├───────────┘               │                 │
  │            │  (Worker)   ├───────────────────────────┘                 │
  │            └─────────────┘                                             │
  └────────────────────────────────────────────────────────────────────────┘
```

1. **Reflector**: Establishes a long-lived HTTP `LIST` + `WATCH` connection to the `kube-apiserver` for designated resource types (e.g., your CRD and standard Pods).
2. **DeltaFIFO**: As events occur in the API server (Create, Update, Delete), the Reflector captures them and places them into a delta queue.
3. **Informer**: Consumes the DeltaFIFO queue. It performs two critical functions:
   * **Cache Sync**: Updates a local, thread-safe memory storage cache (`Lister`) of the cluster's current state. This ensures subsequent read queries inside the operator bypass `kube-apiserver`, protecting the API control plane from CPU exhaustion.
   * **Event Handlers**: Triggers callback actions (e.g., `OnAdd`, `OnUpdate`, `OnDelete`) based on changes.
4. **Workqueue**: The Event Handlers map these raw callbacks to a unique resource identifier key (`namespace/name`) and enqueue it into a rate-limiting, deduplicating Workqueue. 
5. **Reconciler**: A pool of concurrent worker threads pops keys from the Workqueue and executes the `Reconcile(ctx, req)` method.

---

### 2. Resilient Reconciler Design Guidelines

#### A. Level-Triggered vs. Edge-Triggered Logic
* **Edge-Triggered**: Reacts only to an state change event transition (e.g., "Pod scaled up"). If the operator crashes or loses connection during the event, the state change is permanently missed.
* **Level-Triggered (Kubernetes Way)**: Operates by continuously assessing the *current* state of the world relative to the *desired* state during every reconcile cycle.
* **Guideline**: Do not assume the reconcile loop was triggered by a specific event. Always read the entire state of the custom resource and its dependencies from the Lister cache, compare them, and perform necessary corrections.

#### B. Idempotence & Reentrancy
* A reconciler must be **idempotent**: running the reconcile loop 1 time or 1,000 times on the same object state must produce the exact same final system state.
* **Guideline**: Guard all mutation actions (e.g., creating a child service or updating a status field). Check if the child resource already exists before calling a creation API:
  ```go
  err := r.Get(ctx, req.NamespacedName, &existingService)
  if errors.IsNotFound(err) {
      // Create new service
  } else if err != nil {
      return ctrl.Result{}, err
  }
  // Service already exists, verify properties match and continue...
  ```

#### C. Handling Status and Spec Separation
* Updating an object's `Spec` triggers another reconcile loop because the object's generation changes.
* **Structural Schemas & Status Subresource**: Always define a `/status` subresource in your CRD. By dividing the CRD schema, you can update status fields without modifying the resource version generation (`metadata.generation`), preventing infinite reconciliation loops:
  ```go
  // Update status only, avoiding triggering another reconcile execution
  err := r.Status().Update(ctx, &customResource)
  ```

#### D. Workqueue Rate Limiting & Requeue
* If a reconcile step fails due to external dependency bottlenecks (e.g., cloud API throttling or database connection failure), return an error or return a requeue delay.
* The Workqueue implements exponential backoff (e.g., `DefaultControllerRateLimiter` scales from millisecond retries up to 1,000 seconds) to prevent hammering the Kubernetes API server during outage events.
  ```go
  // Requeue request after 30 seconds for an external system readiness check
  return ctrl.Result{RequeueAfter: 30 * time.Second}, nil
  ```

---

## Admission Controllers: Mutating & Validating Webhooks

Admission webhooks are HTTP callouts intercepting requests to the `kube-apiserver` before they are written to `etcd`. They act as a programmable firewall for the cluster control plane.

```
                           API Request Admission Pipeline
 Request ──► [ AuthN & AuthZ ] ──► [ Mutating Webhooks ] ──► [ Schema Validation ] ──► [ Validating Webhooks ] ──► persisted to etcd
```

### 1. Webhook Lifecycles
* **Phase 1: Mutating Webhooks**: Invoked first. They can modify incoming resource payloads to inject defaults, enforce sidecars, or rewrite configurations (e.g., injecting an Envoy sidecar proxy into a Pod, or adding mandatory default security labels to a namespace).
* **Phase 2: Schema Validation**: Validates the payload structure against structural schemas (built-in objects or CRD definitions).
* **Phase 3: Validating Webhooks**: Invoked last. They evaluate the fully resolved object (including changes made by mutating webhooks) and issue a binary decision (`Allowed: true` or `false` with a rejection message). They cannot modify the resource.

---

### 2. High-Risk Webhook Pitfalls: Control Plane Bricking
Webhooks introduce tight, synchronous coupling into the API control plane. A misconfigured webhook can completely disable cluster operations.

```yaml
# A High-Risk ValidatingWebhookConfiguration
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingWebhookConfiguration
metadata:
  name: security-policy-webhook
webhooks:
  - name: policy.enterprise.io
    rules:
      - apiGroups: [""]
        apiVersions: ["v1"]
        operations: ["CREATE", "UPDATE"]
        resources: ["pods", "namespaces"] # Intercepts core system resources!
    failurePolicy: Fail                    # <-- CRITICAL FAILURE RISK!
    timeoutSeconds: 10                     # <-- Too high for critical paths
    clientConfig:
      service:
        name: policy-webhook-svc
        namespace: security-system
        path: "/validate"
```

#### A. The `failurePolicy: Fail` Threat
* **The Risk**: If the webhook service is down (due to node failure, network partition, or code crash), setting `failurePolicy: Fail` causes `kube-apiserver` to reject **all** matching API requests.
* **Cascading Failure**: If your webhook intercepts core resources (`pods`, `namespaces`) with `FailurePolicy: Fail`, you will be unable to launch any new pods. If the webhook pods crash, Kubernetes cannot deploy rescheduled replacements because the webhook endpoint is unreachable. The cluster becomes locked out and requires manual control-plane surgery (deleting the webhook configuration from the master nodes).
* **Mitigation**: 
  1. Set `failurePolicy: Ignore` for less critical enforcement, allowing traffic to flow if the webhook is unreachable.
  2. If `Fail` is mandatory, strictly scope the hook using **Namespace Selectors** or **Object Selectors** to exclude the `kube-system` namespace. This guarantees core controllers can spin up infrastructure pods regardless of webhook health:
     ```yaml
     namespaceSelector:
       matchExpressions:
         - key: kubernetes.io/metadata.name
           operator: NotIn
           values: ["kube-system", "security-system"]
     ```

#### B. Timeout Tuning
* The default webhook timeout is **10 seconds**, which is far too high. If a webhook hangs, a cluster deployment controller making concurrent resource requests can exhaust the API server's connection pool, leading to cluster-wide timeouts.
* **Mitigation**: Keep timeouts low (e.g., `timeoutSeconds: 1` or `2`). The webhook must respond immediately.

---

### 3. Production Performance & HA Patterns
To run admission webhooks safely at enterprise scale:

1. **High Availability (Replica Sets)**: Deploy at least 3 webhook backend replicas. Spread them across multiple nodes using **Pod Anti-Affinity** to survive node outages:
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
2. **Dedicated Node Pools & Priority**: Run webhooks on high-priority node pools with a high-priority class (`system-cluster-critical`) to prevent them from being evicted under memory or CPU pressure.
3. **Internal Caching**: Do not perform synchronous external network queries (e.g., querying active users from an external LDAP directory) inside the webhook execution path. Cache all lookup data in memory, or query a fast local data store to keep webhook response times under 50 milliseconds.
4. **Mutating Webhook Convergence**: Ensure mutating webhooks are **idempotent**. If the mutation logic changes the object on subsequent calls, it can trigger infinite mutating webhook re-evaluation loops in `kube-apiserver`.

***

## API Priority and Fairness (APF)

APF replaces the old `--max-requests-inflight` with fine-grained request queuing. Prevents one client (e.g., CI bots) from starving others (kubelet health beats).

```yaml
# PriorityLevelConfiguration
apiVersion: flowcontrol.apiserver.k8s.io/v1beta3
kind: PriorityLevelConfiguration
metadata:
  name: ci-bots
spec:
  type: Limited
  limited:
    nominalConcurrencyShares: 5    # small share of API server capacity
    limitResponse:
      type: Queue
      queuing:
        queues: 16
        handSize: 4
        queueLengthLimit: 50
***
apiVersion: flowcontrol.apiserver.k8s.io/v1beta3
kind: FlowSchema
metadata:
  name: ci-bot-requests
spec:
  priorityLevelConfiguration:
    name: ci-bots
  matchingPrecedence: 900
  rules:
  - subjects:
    - kind: ServiceAccount
      serviceAccount:
        name: ci-bot
        namespace: ci
    resourceRules:
    - verbs: [list, get, watch]
      resources: [pods, deployments]
      apiGroups: ['']
```

```bash
# Monitor APF
kubectl get --raw /metrics | grep apiserver_flowcontrol_request_execution_seconds
kubectl get apf                     # FlowSchemas
kubectl get prioritylevelconfiguration
```

***

## Cluster API (CAPI)

```bash
# Bootstrap management cluster (uses kind locally)
clusterctl init --infrastructure aws

# Define a workload cluster
cat > cluster.yaml <<EOF
apiVersion: cluster.x-k8s.io/v1beta1
kind: Cluster
metadata:
  name: prod-us-east-1
  namespace: clusters
spec:
  clusterNetwork:
    pods:
      cidrBlocks: ["10.128.0.0/16"]
  infrastructureRef:
    apiVersion: infrastructure.cluster.x-k8s.io/v1beta2
    kind: AWSCluster
    name: prod-us-east-1
  controlPlaneRef:
    apiVersion: controlplane.cluster.x-k8s.io/v1beta1
    kind: KubeadmControlPlane
    name: prod-us-east-1-cp
EOF

kubectl apply -f cluster.yaml

# Watch cluster provisioning
clusterctl describe cluster prod-us-east-1

# Get kubeconfig for workload cluster
clusterctl get kubeconfig prod-us-east-1 > prod-us-east-1.kubeconfig
```

**KubeadmControlPlane** (KCP) — manages control plane rolling upgrades:
```yaml
apiVersion: controlplane.cluster.x-k8s.io/v1beta1
kind: KubeadmControlPlane
metadata:
  name: prod-us-east-1-cp
spec:
  replicas: 3
  version: v1.30.0
  rolloutStrategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1    # create new CP node, then delete old
  machineTemplate:
    infrastructureRef:
      apiVersion: infrastructure.cluster.x-k8s.io/v1beta2
      kind: AWSMachineTemplate
      name: prod-us-east-1-cp
  kubeadmConfigSpec:
    clusterConfiguration:
      apiServer:
        extraArgs:
          audit-log-path: /var/log/kubernetes/audit.log
          audit-log-maxbackup: "10"
```

***

## vcluster — Virtual Clusters

```bash
# Install vcluster CLI
curl -L -o vcluster "https://github.com/loft-sh/vcluster/releases/latest/download/vcluster-linux-amd64"
chmod +x vcluster

# Create a vcluster in a namespace
vcluster create tenant-a --namespace tenant-a \
  --set storage.size=5Gi \
  --set sync.nodes.enabled=true

# Connect to the vcluster
vcluster connect tenant-a --namespace tenant-a -- kubectl get pods

# List vclusters
vcluster list
```

```yaml
# vcluster Helm values for production hardening
vcluster:
  storage:
    persistence: true
    size: 10Gi

syncer:
  extraArgs:
  - --sync-all-nodes=false          # only sync nodes that have pods
  - --node-selector=team=tenant-a   # restrict to dedicated node pool

resourceQuota:
  enabled: true
  quota:
    requests.cpu: "20"
    requests.memory: "40Gi"
    count/pods: "200"

networkPolicy:
  enabled: true
  outgoingConnections:
    ipBlock:
      cidr: 10.0.0.0/8              # allow internal only
```

***

## Multi-Tenancy — RBAC Patterns

```yaml
# Namespace-scoped developer role
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: developer
  namespace: team-payments
rules:
- apiGroups: [""]
  resources: [pods, pods/log, pods/exec]
  verbs: [get, list, watch, create, delete]
- apiGroups: [apps]
  resources: [deployments, replicasets]
  verbs: [get, list, watch, patch, update]
- apiGroups: [""]
  resources: [secrets]
  verbs: []    # no access to secrets
***
# Bind to an OIDC group
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: payments-developers
  namespace: team-payments
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: developer
subjects:
- apiGroup: rbac.authorization.k8s.io
  kind: Group
  name: payments-engineers   # matches OIDC group claim
```

### ResourceQuota + LimitRange

```yaml
# ResourceQuota — namespace-level limits
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-quota
  namespace: team-payments
spec:
  hard:
    requests.cpu: "10"
    requests.memory: 20Gi
    limits.cpu: "20"
    limits.memory: 40Gi
    count/pods: "50"
    count/services.loadbalancers: "2"
    persistentvolumeclaims: "10"
    requests.storage: 200Gi
***
# LimitRange — defaults for containers without explicit requests
apiVersion: v1
kind: LimitRange
metadata:
  name: container-limits
  namespace: team-payments
spec:
  limits:
  - type: Container
    default:
      cpu: "500m"
      memory: "512Mi"
    defaultRequest:
      cpu: "100m"
      memory: "128Mi"
    max:
      cpu: "4"
      memory: "8Gi"
```

***

## Cluster Upgrades — Safe Procedure

```bash
# Pre-upgrade checklist
kubectl get nodes -o wide                    # current versions
kubectl get pods -A | grep -v Running        # any unhealthy pods?
kubectl api-versions | grep deprecated       # deprecated APIs in use?

# Check deprecated API usage (before upgrading)
pluto detect-all-in-cluster                  # pluto tool scans live cluster
pluto detect -d ./manifests                  # scan local manifests

# Upgrade control plane (managed: EKS/AKS does this for you)
# Self-hosted with kubeadm:
kubeadm upgrade plan
kubeadm upgrade apply v1.30.0

# Upgrade each node
kubectl cordon <node>
kubectl drain <node> --ignore-daemonsets --delete-emptydir-data --grace-period=60
# On the node:
apt-get update && apt-get install -y kubelet=1.30.0-00 kubectl=1.30.0-00
systemctl restart kubelet
# Back on control plane:
kubectl uncordon <node>

# Verify
kubectl get nodes   # all should show new version
kubectl get pods -A | grep -v Running   # check for any disrupted pods
```

***

## Network Policy — Production Patterns

```yaml
# Default deny all ingress and egress in a namespace
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: production
spec:
  podSelector: {}      # select all pods
  policyTypes: [Ingress, Egress]

# Allow ingress from ingress controller only
***
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-ingress-controller
  namespace: production
spec:
  podSelector:
    matchLabels:
      tier: web
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8080

# Allow DNS egress (required for pod name resolution)
***
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns
  namespace: production
spec:
  podSelector: {}
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: kube-system
    ports:
    - protocol: UDP
      port: 53
```

***

## Key Gotchas

| Gotcha | Detail |
|--------|--------|
| etcd 2GB default quota | When exceeded, cluster enters read-only mode — monitor `etcd_mvcc_db_total_size_in_bytes` |
| Control plane must be upgraded before nodes | Node kubelet must be ≤ control plane version; skip-version upgrades unsupported |
| CAPI doesn't manage existing clusters | CAPI manages clusters it provisioned; importing an existing cluster requires manual `clusterctl move` |
| vcluster pod scheduling uses host node pool | `vcluster` syncer creates "shadow" pods on host cluster — host node pool sizing must account for all vclusters |
| NetworkPolicy requires a CNI that enforces it | Flannel does NOT enforce NetworkPolicy; need Calico, Cilium, or Weave |
| `kubectl drain` respects PDBs | A PDB with `minAvailable: 1` on a single-replica deployment will block drain indefinitely |
| APF misconfiguration can lock out all users | Test APF changes on non-prod; a wrong FlowSchema can put all requests in the `catch-all` limited queue |
| ResourceQuota applies at request time | A pod without CPU/memory requests will be rejected if the namespace has a ResourceQuota (LimitRange provides defaults) |

## System Design Perspective

- **CAPI management cluster — the meta-cluster problem:** The management cluster running CAPI is itself a Kubernetes cluster that needs to be managed. If the management cluster goes down, you lose the ability to create or modify workload clusters (but existing workload clusters keep running). The management cluster needs its own HA design, backup strategy, and upgrade procedure — it's the highest-severity cluster in the fleet.
- **APF FlowSchema precedence conflict risk:** APF FlowSchemas have a `matchingPrecedence` field (lower = higher priority). If two FlowSchemas match the same request, the lower precedence number wins. A misconfigured low-precedence FlowSchema that matches all requests can reclassify kubelet heartbeats into a low-priority queue, causing cascading node NotReady events. Test every APF change against a production-like load profile on a staging cluster.
- **vcluster isolation boundary is the host NetworkPolicy:** vcluster tenants can install CRDs and create any in-cluster objects, but their pods ultimately run on host nodes. If the host cluster does not have NetworkPolicy enforced (e.g., Flannel CNI), a malicious tenant pod can communicate with other tenants' pods. vcluster hard multi-tenancy requires: (1) CNI with NetworkPolicy enforcement, (2) ResourceQuota on the vcluster namespace, (3) node pool isolation via taints if needed.
- **ResourceQuota + LimitRange interaction:** ResourceQuota enforces aggregate namespace limits. LimitRange provides per-container defaults. If ResourceQuota exists but LimitRange does not, a pod without explicit requests/limits is rejected (quota has no way to account for it). Always deploy LimitRange alongside ResourceQuota so pods without explicit requests still get default values and pass quota validation.
- **Upgrade skip-version risk — why it's unsupported:** Kubernetes maintains backward compatibility across only two minor versions. An API removed in 1.26 (e.g., `policy/v1beta1 PodSecurityPolicy`) that was still in use before a 1.24→1.26 skip would break workloads silently (objects in etcd using the old apiVersion). Single-version upgrades allow a compatibility check window. Use `pluto detect-all-in-cluster` before every upgrade to catch deprecated API usage.
