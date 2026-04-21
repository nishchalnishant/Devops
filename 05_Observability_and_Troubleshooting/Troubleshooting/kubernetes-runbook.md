# Kubernetes Troubleshooting Runbook (7 YOE)

A senior engineer approaches every Kubernetes failure with a systematic **command → evidence → hypothesis → fix** loop. Never guess a root cause. Gather evidence first.

---

## Golden Rule: The First 60 Seconds

Before touching anything, run this triage sequence:

```bash
# 1. What is failing?
kubectl get pods -A | grep -v Running | grep -v Completed

# 2. When did it start? Any recent changes?
kubectl get events -A --sort-by=.lastTimestamp | tail -30

# 3. Is it just one pod or widespread?
kubectl top nodes
kubectl top pods -A --sort-by=memory
```

---

## Scenario 1: CrashLoopBackOff

The container starts, crashes, and Kubernetes keeps restarting it. The backoff timer grows exponentially (10s → 20s → 40s → ... → 5m).

### Root Cause Decision Tree

**Step 1 — Read the most recent crash logs:**
```bash
kubectl logs <pod> --previous
kubectl logs <pod> -c <container> --previous
```

**Step 2 — Read the pod events:**
```bash
kubectl describe pod <pod>
# Focus on: Events section, Exit Code, Last State
```

**Exit Code → Root Cause Mapping:**

| Exit Code | Meaning | Likely Cause |
|---|---|---|
| `0` | Clean exit | Entrypoint ran to completion — not a server process |
| `1` | General error | Application crash — check logs |
| `2` | Misuse of shell builtins | Bad script syntax |
| `137` (`SIGKILL`) | OOMKilled | Memory limit exceeded |
| `139` (`SIGSEGV`) | Segmentation fault | Native code bug, dependency ABI mismatch |
| `143` (`SIGTERM`) | Graceful shutdown terminated | Readiness probe failing repeatedly |

### Fix Paths

**OOMKilled (`Exit Code 137`):**
```bash
# Confirm OOM
kubectl describe pod <pod> | grep -A5 "Last State"
# Output: Reason: OOMKilled

# Fix: Increase memory limit
kubectl set resources deployment <name> --limits=memory=1Gi
# Or edit the deployment YAML and increase spec.containers[].resources.limits.memory
```

**Bad Entrypoint / Missing Config:**
```bash
# Override the entrypoint temporarily to get a shell
kubectl debug <pod> -it --image=busybox --target=<container>
# Or patch the deployment command to sleep
kubectl patch deployment <name> --patch '{"spec":{"template":{"spec":{"containers":[{"name":"<container>","command":["sleep","3600"]}]}}}}'
kubectl exec -it <pod> -- sh
# Now manually run the original entrypoint and read the error
```

**Missing Secret or ConfigMap:**
```bash
# Check if the referenced secret/configmap exists
kubectl get secret <secret-name> -n <namespace>
kubectl get configmap <cm-name> -n <namespace>
# If missing, create it or fix the reference in the pod spec
```

**Bad Probe Configuration (killing healthy pods):**
```bash
kubectl describe pod <pod> | grep -A10 "Liveness\|Readiness"
# If initialDelaySeconds is too short for a slow-starting app, add a startupProbe
```

---

## Scenario 2: OOMKilled (deep dive)

### Detection
```bash
kubectl describe pod <pod> | grep -A5 "Last State"
# Reason: OOMKilled

# Check current usage vs limits
kubectl top pod <pod> --containers
kubectl describe pod <pod> | grep -A4 "Limits\|Requests"
```

### JVM-specific (Java OOM)
Java OOM is almost never the heap alone. Non-heap eats significant memory:
- **Metaspace** → Class metadata
- **Thread stacks** → Each thread ~512KB–1MB
- **Native memory** → JIT compiler, JNI, off-heap buffers

```bash
# Rule of thumb: container memory limit = -Xmx + 25-50% overhead
# Example: -Xmx2g → set limit to 3–3.5Gi

# Enable container-aware JVM
JAVA_OPTS="-XX:+UseContainerSupport -XX:MaxRAMPercentage=75.0"
```

### Fix Checklist
1. Increase `resources.limits.memory` in the Deployment spec.
2. Add a `VerticalPodAutoscaler` resource (VPA) to auto-right-size over time.
3. Profile the application: confirm whether the OOM is a memory leak or genuinely undersized limits.

---

## Scenario 3: Pod Stuck in Pending / FailedScheduling

### Systematic Inspection
```bash
kubectl describe pod <pod>
# Focus: Events → "FailedScheduling"
# The scheduler prints the exact reason
```

### Common Reasons and Fixes

**Insufficient resources:**
```bash
# Events will show: "Insufficient cpu" or "Insufficient memory"
kubectl describe nodes | grep -A10 "Allocated resources"
# Fix: Scale out the node pool, or reduce pod requests
```

**Taint mismatch:**
```bash
kubectl describe nodes | grep Taint
# If node has: node.kubernetes.io/not-ready:NoSchedule
# And pod has no matching toleration → pod stays Pending
# Fix: Add toleration to pod spec OR remove the taint if you own the node
```

**NodeSelector / NodeAffinity mismatch:**
```bash
kubectl get nodes --show-labels
kubectl describe pod <pod> | grep -A10 "Node-Selectors\|Affinity"
# Fix: Ensure label exists on at least one node, or relax affinity rules
```

**PVC zone binding mismatch:**
```bash
kubectl get pvc <pvc-name>
kubectl describe pvc <pvc-name>
# If PVC is bound to us-east-1a but pod is scheduled to us-east-1b:
# Fix: Use WaitForFirstConsumer volumeBindingMode in StorageClass
```

**Resource Quota exhaustion:**
```bash
kubectl describe quota -n <namespace>
# Fix: Increase quota limits or reduce pod requests
```

---

## Scenario 4: Node NotReady

A node transitions to `NotReady` — pods on that node get evicted after `pod-eviction-timeout` (default: 5 minutes).

### Triage
```bash
kubectl describe node <node-name>
# Focus: Conditions section — look for:
# MemoryPressure, DiskPressure, PIDPressure, NetworkUnavailable, Ready=False

# Check the kubelet log on the node itself
journalctl -u kubelet -f --since "5 minutes ago"
```

### Root Causes

**Disk pressure:**
```bash
# On the node (via SSH or kubectl debug node)
df -h /var/lib/kubelet
df -h /var/lib/docker  # or /var/lib/containerd

# Fix: Clean up unused images
crictl rmi --prune
# Or expand the disk backing the node
```

**Memory pressure:**
```bash
free -m
# Fix: Evict low-priority pods or add nodes. Set proper requests/limits
# to prevent noisy neighbours exhausting node memory.
```

**CNI plugin failure (NetworkUnavailable=True):**
```bash
kubectl get pods -n kube-system | grep -i 'calico\|flannel\|cilium\|cni'
kubectl logs -n kube-system <cni-pod>
# Fix: Restart the CNI DaemonSet, or re-apply the CNI manifest
```

**Kubelet cannot reach the API server:**
```bash
# On the node
curl -k https://<api-server-ip>:6443/healthz
# If failing → check firewall rules, NSG, security groups between node and control plane
```

---

## Scenario 5: DNS Failures

DNS failures in Kubernetes are deceptive — pods exist and are Running, but service-to-service calls fail with `NXDOMAIN` or `connection refused`.

### Triage Sequence
```bash
# 1. Test DNS from inside a pod
kubectl run dnstest --image=busybox --restart=Never --rm -it -- nslookup kubernetes.default

# 2. Check if CoreDNS pods are healthy
kubectl get pods -n kube-system -l k8s-app=kube-dns
kubectl logs -n kube-system -l k8s-app=kube-dns

# 3. Check CoreDNS ConfigMap for misconfigurations
kubectl get configmap coredns -n kube-system -o yaml
```

### Common Root Causes

**`ndots:5` causing slow resolution:**

By default, Kubernetes sets `ndots: 5` in `/etc/resolv.conf` inside every pod. This means a query for `payment-api.production.svc.cluster.local` causes 5 internal FQDN lookups before the external lookup. Under high query volume, this creates CoreDNS saturation.

```bash
# Fix: Override ndots in pod spec
spec:
  dnsConfig:
    options:
    - name: ndots
      value: "1"
```

**CoreDNS forwarding loop:**
```bash
kubectl logs -n kube-system <coredns-pod> | grep loop
# If you see "Loop detected" errors, the CoreDNS upstream is forwarding back to itself.
# Fix: Edit coredns ConfigMap and set a specific upstream (e.g., 8.8.8.8) instead of /etc/resolv.conf
```

**NetworkPolicy blocking port 53:**
```bash
kubectl get networkpolicies -A
# If a policy restricts egress from app namespace, UDP/TCP port 53 to kube-system must be explicitly allowed
```

---

## Scenario 6: ImagePullBackOff

```bash
kubectl describe pod <pod>
# Events: "Failed to pull image ... unauthorized / manifest unknown / not found"
```

| Error | Root Cause | Fix |
|---|---|---|
| `unauthorized` | No `imagePullSecret` or wrong credentials | Create/attach the correct `imagePullSecret` |
| `manifest unknown` | Tag doesn't exist in the registry | Verify tag with `docker manifest inspect` or registry UI |
| `not found` | Wrong registry URL or private registry unreachable | Check `image:` field for typos; verify network egress from node |
| `x509: certificate signed by unknown authority` | Self-signed registry cert not trusted by containerd | Add cert to containerd trusted CAs |

**Creating an imagePullSecret for Azure Container Registry:**
```bash
kubectl create secret docker-registry acr-secret \
  --docker-server=<myregistry>.azurecr.io \
  --docker-username=<SP-app-id> \
  --docker-password=<SP-password> \
  -n <namespace>
```

---

## Scenario 7: HPA Not Scaling

```bash
kubectl describe hpa <hpa-name>
# Check: "unable to get metrics for resource cpu" or "metrics not available"
```

**Root Cause 1: metrics-server not installed:**
```bash
kubectl top pods  # If this fails, metrics-server is missing
kubectl get deployment metrics-server -n kube-system
# Fix: Install metrics-server
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

**Root Cause 2: Custom metrics API not registered:**
```bash
kubectl get apiservice v1beta1.custom.metrics.k8s.io
# If missing, the HPA cannot use custom metrics (e.g., RPS from Prometheus)
# Fix: Deploy Prometheus Adapter and register the APIService
```

**Root Cause 3: Pods at limits but HPA not triggering:**
```bash
kubectl describe hpa <name>
# Check: Current vs. Desired replicas, and the "Conditions" section
# "ScalingActive=False: FailedGetResourceMetric" → resource requests not set on the pod
# Fix: Ensure containers have resources.requests.cpu set — HPA uses this as the denominator
```

---

## Scenario 8: Service Mesh 503 Errors (Istio)

```bash
# Check Envoy proxy access logs
kubectl logs <pod> -c istio-proxy | grep "503\|UF\|NR"

# UF = Upstream connection failure
# NR = No route found (DestinationRule missing)
```

**mTLS mode mismatch (most common):**
```bash
kubectl get peerauthentication -A
kubectl get destinationrule -A
# If one service is in STRICT mTLS mode but the caller has no sidecar (or DISABLE mode):
# Fix: Add sidecar injection to the calling namespace, or set PERMISSIVE mode temporarily
```

**Circuit breaker tripped:**
```bash
kubectl describe destinationrule <name>
# Check outlierDetection settings — if too aggressive, healthy pods get ejected
```

---

## Scenario 9: etcd High Latency / Leader Elections

```bash
# On the control plane node
ETCDCTL_API=3 etcdctl \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  endpoint status --write-out=table

# Check for: "db size", "raft term", "leader"
# If db size > 2GB, run defragmentation
etcdctl defrag --endpoints=https://127.0.0.1:2379 <certs>

# Compact old revisions to free space
REV=$(etcdctl endpoint status --write-out="json" | egrep -o '"revision":[0-9]*' | egrep -o '[0-9]*' | head -1)
etcdctl compact $REV
```

**Leader elections (split brain indicator):**
- If the leader keeps changing in a 3-node cluster, look for network partitions between control plane nodes.
- Check disk I/O latency on etcd nodes — etcd is extremely sensitive to disk latency (requires < 10ms fsync).
