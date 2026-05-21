# Kubernetes Tips & Tricks

```
Kubernetes Tips & Tricks
├── kubectl Productivity
│   ├── Aliases — k, kgp, kgpa, kd, kl, ke, kwatch
│   ├── --dry-run=client -o yaml — generate YAML for deploy/svc/cm/secret fast
│   ├── JSONPath — extract pod IPs, images, node zones, PVC status
│   └── Custom Columns — NAME, STATUS, NODE, IP in one command
├── Debugging Techniques
│   ├── CrashLoopBackOff
│   │   ├── kubectl describe pod → "Last State" exit code
│   │   ├── kubectl logs --previous — logs from crashed container
│   │   └── kubectl debug --copy-to — override entrypoint to prevent crash
│   ├── Networking In-Cluster
│   │   ├── nicolaka/netshoot — debug pod with net tools (curl, tcpdump, dig)
│   │   ├── busybox nslookup — test DNS resolution
│   │   └── tcpdump on eth0 — packet capture inside pod
│   └── Node-Level Issues
│       ├── kubectl debug node/ — shell on node without SSH; files at /host
│       ├── journalctl -u kubelet — kubelet logs via debug container
│       └── kubectl get events --field-selector reason=OOMKilling
├── Resource Management
│   ├── kubectl top pods/nodes — current usage before setting limits
│   ├── VPA recommendations — kubectl get vpa -o jsonpath
│   └── LimitRange — namespace-level defaults for requests/limits/max
├── RBAC Best Practices
│   ├── Prefer RoleBinding over ClusterRoleBinding (namespace-scoped)
│   ├── ClusterRole + RoleBinding pattern — reuse roles, scope bindings
│   ├── kubectl auth can-i --list — audit ServiceAccount permissions
│   └── Avoid wildcard permissions (*) — use specific resources + verbs
├── Networking Tips
│   ├── NetworkPolicy: default-deny-ingress first, then allow selectively
│   ├── CNI must support NetworkPolicy (Calico/Cilium/Weave — NOT Flannel)
│   └── Service DNS shorthand — <svc> / <svc>.<ns> / FQDN with trailing dot
├── Storage Tips
│   ├── PVC resize — patch spec.resources.requests.storage (if SC allows)
│   └── etcd backup — etcdctl snapshot save with certs; verify with status
├── Upgrade Tips
│   ├── Drain node before upgrade — cordon + evict (respects PDBs)
│   ├── Uncordon after — re-enables scheduling
│   └── Never skip minor versions (1.27 → 1.28 → 1.29, not 1.27 → 1.29)
├── GitOps Patterns
│   ├── kubectl apply for everything in production
│   ├── Imperative: only for debug / queries / emergency rollback
│   ├── kubectl diff -f — detect drift from manifests
│   └── Reconcile imperative changes back to git after incidents
├── Security Tips
│   ├── trivy image — scan before deployment; --exit-code 1 in CI
│   ├── securityContext — runAsNonRoot, readOnlyRootFilesystem, drop ALL caps
│   └── kubeadm certs check-expiration / renew all
├── Performance Tips
│   ├── kubectl get pods -w — watch via server-sent events (not polling loop)
│   ├── kubectl wait --for=condition=Ready — scripting-safe wait
│   └── Use informers / controller-runtime cache in operators (not direct API calls)
└── Common Gotchas
    ├── Never use :latest tag in production (no rollback, no version visibility)
    ├── Real workloads never in default namespace
    ├── HPA + replicas in Deployment spec = GitOps/HPA conflict — remove replicas from manifest
    ├── Secrets not encrypted by default — enable encryption at rest; use ESO/Vault
    ├── ImagePullPolicy Always = registry call on every pod start
    └── terminationGracePeriodSeconds must match preStop hook + drain time
```

## First Principles

- You have many containers to run — you need a **scheduler** that places them based on resource requests.
- Machines fail — controllers **automatically restart and reschedule**; probes detect failure and remove unhealthy pods from traffic.
- Traffic must reach containers wherever they run — **Service DNS** provides stable addresses; NetworkPolicy controls who can reach whom.
- Config and secrets must not be baked into images — **externalise** via ConfigMap/Secret; never use `:latest` so rollback always works.
- You need zero-downtime rollouts — **declarative Deployments** + rolling update strategy; `kubectl rollout undo` as the emergency lever.

> [!TIP]
> These are battle-tested patterns from production Kubernetes operations. Most apply to 1.28+.

## kubectl Productivity

### Aliases and Shell Functions
```bash
alias k=kubectl
alias kgp='kubectl get pods'
alias kgpa='kubectl get pods -A'
alias kd='kubectl describe'
alias kl='kubectl logs'
alias ke='kubectl exec -it'

# Switch namespace permanently
kubens() { kubectl config set-context --current --namespace="$1"; }

# Watch pods with auto-refresh
alias kwatch='kubectl get pods -w'
```

### Use --dry-run to Generate YAML Fast
```bash
kubectl create deployment nginx --image=nginx --replicas=3 --dry-run=client -o yaml > deploy.yaml
kubectl expose deployment nginx --port=80 --type=ClusterIP --dry-run=client -o yaml >> deploy.yaml
kubectl create configmap app-config --from-literal=key=value --dry-run=client -o yaml
kubectl create secret generic db-secret --from-literal=password=s3cr3t --dry-run=client -o yaml
```

### JSONPath for Scripting
```bash
# Get all pod IPs
kubectl get pods -o jsonpath='{.items[*].status.podIP}'

# Get image names for all containers
kubectl get pods -o jsonpath='{.items[*].spec.containers[*].image}'

# Get nodes and their zones
kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.metadata.labels.topology\.kubernetes\.io/zone}{"\n"}{end}'

# Get PVC bound status
kubectl get pvc -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.phase}{"\n"}{end}'
```

### Custom Columns
```bash
kubectl get pods -o custom-columns='NAME:.metadata.name,STATUS:.status.phase,NODE:.spec.nodeName,IP:.status.podIP'
kubectl get nodes -o custom-columns='NAME:.metadata.name,STATUS:.status.conditions[-1].type,VERSION:.status.nodeInfo.kubeletVersion'
```

## Debugging Techniques

### Debug a CrashLoopBackOff Container
```bash
# Check last exit code and reason
kubectl describe pod <pod> | grep -A5 "Last State"

# Get logs from crashed (previous) container
kubectl logs <pod> -c <container> --previous

# Override entrypoint to prevent crash
kubectl debug <pod> -it --copy-to=debug-pod --container=<container> -- /bin/sh
# Or patch the deployment temporarily:
kubectl set env deployment/<name> CRASH_GUARD=1  # if app checks this
```

### Debug Networking In-Cluster
```bash
# Spin up a debug pod with network tools
kubectl run debug --image=nicolaka/netshoot --rm -it --restart=Never -- bash

# Test DNS resolution
kubectl run dnstest --image=busybox --rm -it --restart=Never -- nslookup kubernetes.default

# Test service connectivity
kubectl run curl --image=curlimages/curl --rm -it --restart=Never -- curl http://<service>.<namespace>.svc.cluster.local

# Capture packets on a pod's network interface
kubectl exec -it <pod> -- tcpdump -i eth0 -nn port 80
```

### Debug Node-Level Issues
```bash
# Node shell without SSH
kubectl debug node/<node-name> -it --image=ubuntu -- bash
# Files are at /host inside the debug container

# Check kubelet logs
kubectl debug node/<node> -it --image=ubuntu -- chroot /host journalctl -u kubelet -n 100

# Check system events
kubectl get events --field-selector reason=OOMKilling -A
kubectl get events --field-selector involvedObject.kind=Node -A
```

## Resource Management

### Set Resource Requests/Limits Efficiently
```bash
# Check current resource usage before setting limits
kubectl top pods --sort-by=memory -A
kubectl top nodes

# VPA recommendation (if VPA is installed)
kubectl get vpa <name> -o jsonpath='{.status.recommendation}'
```

> [!IMPORTANT]
> Always set `requests` at minimum. Pods without requests are BestEffort class and will be evicted first under pressure. Setting requests without limits allows burstable behavior — often the right choice for latency-sensitive workloads.

### LimitRange for Namespace Defaults
```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: default-limits
spec:
  limits:
  - type: Container
    default:          # applied when no limits specified
      cpu: "500m"
      memory: "256Mi"
    defaultRequest:   # applied when no requests specified
      cpu: "100m"
      memory: "128Mi"
    max:
      cpu: "4"
      memory: "4Gi"
```

## RBAC Best Practices

### Least Privilege Pattern
```bash
# Always use RoleBindings (namespace-scoped) over ClusterRoleBindings unless truly needed
# Use ClusterRoles but bind them with RoleBinding for namespace-scoped access:
kubectl create clusterrole pod-reader --verb=get,list,watch --resource=pods
kubectl create rolebinding pod-reader-binding --clusterrole=pod-reader --serviceaccount=myns:mysa -n myns

# Audit what a ServiceAccount can do
kubectl auth can-i --list --as=system:serviceaccount:myns:mysa -n myns

# Check if specific action is allowed
kubectl auth can-i get secrets --as=system:serviceaccount:myns:mysa -n myns
```

### Avoid Wildcard Permissions
```yaml
# BAD
rules:
- apiGroups: ["*"]
  resources: ["*"]
  verbs: ["*"]

# GOOD - minimal permissions
rules:
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["get", "list", "watch", "patch"]
- apiGroups: [""]
  resources: ["configmaps"]
  resourceNames: ["my-specific-config"]  # scope to specific resource names
  verbs: ["get"]
```

## Networking Tips

### NetworkPolicy Deny-All Then Allow Pattern
```yaml
# 1. Default deny all ingress in namespace
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
spec:
  podSelector: {}  # selects all pods
  policyTypes: [Ingress]
***
# 2. Allow only what's needed
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-backend
spec:
  podSelector:
    matchLabels: {app: backend}
  ingress:
  - from:
    - podSelector:
        matchLabels: {app: frontend}
    ports:
    - port: 8080
```

> [!CAUTION]
> NetworkPolicies are only enforced if your CNI plugin supports them (Calico, Cilium, Weave). Flannel does NOT enforce NetworkPolicies — creating them silently does nothing.

### Service DNS Shorthand
Within same namespace: `http://myservice` (just the service name)
Cross-namespace: `http://myservice.other-namespace`
Full FQDN: `http://myservice.other-namespace.svc.cluster.local`

For external DNS, use FQDN with trailing dot to skip search domain lookups: `api.example.com.`

## Storage Tips

### Resize a PVC (if StorageClass supports it)
```bash
# Check if StorageClass allows expansion
kubectl get sc <name> -o jsonpath='{.allowVolumeExpansion}'

# Patch the PVC (pod does NOT need to restart for filesystem expansion in 1.24+)
kubectl patch pvc <name> -p '{"spec":{"resources":{"requests":{"storage":"50Gi"}}}}'

# Verify
kubectl get pvc <name> -w
```

### Backup etcd (critical for cluster recovery)
```bash
ETCDCTL_API=3 etcdctl snapshot save /backup/etcd-snapshot.db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key

# Verify
ETCDCTL_API=3 etcdctl snapshot status /backup/etcd-snapshot.db --write-out=table
```

## Upgrade Tips

### Safe Rolling Node Upgrade
```bash
# 1. Check current version skew (no more than 2 minor versions between nodes and control plane)
kubectl get nodes

# 2. Drain the node
kubectl drain <node> --ignore-daemonsets --delete-emptydir-data

# 3. Upgrade kubelet and kubectl on the node
# (distribution-specific: apt/yum/dnf)

# 4. Uncordon
kubectl uncordon <node>

# 5. Verify
kubectl get node <node>
```

> [!IMPORTANT]
> Upgrade control plane first, then workers. Never skip minor versions (1.27 → 1.29 is not supported; do 1.27 → 1.28 → 1.29).

## GitOps Patterns

### Declarative vs Imperative Balance
Use `kubectl apply` for everything in production. Keep imperative commands for:
- Debugging (`kubectl exec`, `kubectl port-forward`, `kubectl debug`)
- One-off queries (`kubectl get`, `kubectl describe`, `kubectl top`)
- Emergency rollbacks in an incident (`kubectl rollout undo`)

Always reconcile imperative changes back to git after an incident.

### Drift Detection
```bash
# Check if live state matches what's in git (rough check)
kubectl diff -f ./manifests/

# ArgoCD sync status
argocd app get <app-name> --refresh
```

## Security Tips

### Scan Images Before Deployment
```bash
# Trivy (most common)
trivy image nginx:latest

# In CI pipeline
trivy image --exit-code 1 --severity HIGH,CRITICAL myapp:$TAG
```

### Force Non-Root in Pod
```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  runAsGroup: 1000
  fsGroup: 1000
  seccompProfile:
    type: RuntimeDefault
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  capabilities:
    drop: [ALL]
```

### Rotate Certificates
```bash
# Check certificate expiry (kubeadm clusters)
kubeadm certs check-expiration

# Renew all certificates
kubeadm certs renew all

# Restart control plane components (they pick up new certs)
kubectl -n kube-system rollout restart deployment/coredns
# Static pods restart automatically when cert files change
```

## Performance Tips

### Watch vs Poll
```bash
# Polling (bad for scripting — hammers API server)
while true; do kubectl get pods; sleep 2; done

# Watch (good — uses server-sent events)
kubectl get pods -w

# Watch with timeout for scripting
kubectl wait --for=condition=Ready pod/<name> --timeout=120s
```

### Use ResourceVersion for Efficient Watches
The API server supports `resourceVersion` to start a watch from a specific point. Kubernetes informers use this internally. When writing operators, use controller-runtime's cache (backed by informers) rather than making direct API calls.

## Common Gotchas

1. **Container images with `latest` tag**: Never use `latest` in production — you lose rollback capability and can't tell what version is running. Always pin to a digest or immutable tag.

2. **Default namespace**: Real workloads should never go in `default`. Create dedicated namespaces.

3. **NodePort range**: Default is 30000-32767. External LoadBalancers are the preferred exposure method in cloud environments.

4. **HPA and replicas in Deployment**: Don't set `replicas` in the Deployment manifest if HPA manages it — every GitOps sync will fight the HPA. Use `kubectl patch` or remove `replicas` from the manifest and let HPA own it.

5. **Secrets are not secret by default**: Enable encryption at rest for etcd. Use external secret managers (HashiCorp Vault, AWS Secrets Manager, Azure Key Vault) with CSI driver or operators (External Secrets Operator) for production secrets.

6. **ImagePullPolicy**: `Always` causes an API call to the registry on every pod start. `IfNotPresent` uses cached image. In production with immutable tags, `IfNotPresent` is fine and faster.

7. **terminationGracePeriodSeconds**: Default 30 seconds. If your app needs longer to drain (e.g., a gRPC server waiting for streams to complete), increase this value. Set to match your `preStop` hook + drain time.

## System Design Perspective

- **Why dry-run first:** `--dry-run=client -o yaml` lets you version-control generated manifests. Server-side dry-run (`--dry-run=server`) additionally runs admission webhooks — catches policy rejections before apply. Use server-side dry-run in CI pipelines.
- **Watch vs. poll at scale:** Each `kubectl get pods` poll is a full LIST request that hits the API server cache. At cluster scale (1000+ pods, frequent scripts), LIST storms degrade API server latency for all clients. `kubectl get pods -w` opens a single watch stream via HTTP/2 server-sent events — one connection, zero polling overhead.
- **NetworkPolicy enforcement gap:** Flannel silently ignores NetworkPolicy objects — they appear valid but have no effect. This is a security design blind spot. Always validate CNI NetworkPolicy enforcement with a test: apply a deny-all policy, then verify traffic is actually blocked. Don't assume "applied" means "enforced."
- **etcd backup strategy:** A single etcd snapshot on the control plane node is not offsite backup. Treat etcd snapshots like database backups: push to S3/GCS/Azure Blob on a schedule, verify restores quarterly, and document the recovery runbook. RPO (recovery point objective) should drive snapshot frequency.
- **terminationGracePeriodSeconds sizing:** This value must be the sum of: (1) `preStop` hook duration + (2) time for the app to drain in-flight requests after SIGTERM + (3) buffer. If SIGKILL fires before drain completes, in-flight requests are aborted. The load balancer also needs time to stop sending new requests — a `preStop: sleep 5` gives the kube-proxy time to remove the pod from endpoints before SIGTERM reaches the app.
- **Certificate rotation operational risk:** Expired certificates cause API server to reject all requests — the cluster effectively becomes read-only (existing pods keep running, but no control plane operations work). Set monitoring alerts on `kubeadm certs check-expiration` output at 60 days and 30 days before expiry.
