# Enterprise Kubernetes Architecture & Fleet Management

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
