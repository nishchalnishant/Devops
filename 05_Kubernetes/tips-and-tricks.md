# Kubernetes Tips & Tricks

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
---
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
