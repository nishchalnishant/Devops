# Advanced DevOps Deep-Dive: eBPF & Service Mesh at Scale

> [!IMPORTANT]
> eBPF and service mesh architecture are Staff-level topics. If you can discuss eBPF internals and service mesh trade-offs beyond "Istio adds mTLS," you will stand out in any senior infrastructure interview. This file covers the depth interviewers expect at the 7+ YOE level.

**Companion files:**
- [Interview Questions (Hard)](interview-questions-hard.md)
- [GitOps & FinOps at Scale](gitops-at-scale-and-finops.md)
- [K8s Architecture](../03_Containers_and_Orchestration/Kubernetes/enterprise-kubernetes-architecture.md)

---

## Part 1: eBPF — Extended Berkeley Packet Filter

### What eBPF Actually Is

eBPF is a sandboxed virtual machine inside the Linux kernel that allows running custom programs at kernel events — without modifying kernel source code or loading kernel modules.

> [!TIP]
> The interview click moment: eBPF is not "a tracing tool." It is a **kernel programmability layer** that happens to power observability tools, CNI plugins, security engines, and network accelerators. The tool names (Cilium, Falco, Pixie) are the applications. eBPF is the substrate.

```
┌──────────────────────────────────────────────────────────────┐
│                    LINUX KERNEL                               │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │              eBPF VIRTUAL MACHINE                      │  │
│  │                                                        │  │
│  │  eBPF Program (bytecode)  ◄── Compiled from C or Rust  │  │
│  │         │                                              │  │
│  │         │  Verified by eBPF Verifier                  │  │
│  │         │  (no loops that don't terminate,            │  │
│  │         │   no bad memory access, no crashes)         │  │
│  │         │                                              │  │
│  │         ▼                                              │  │
│  │    JIT Compiled → Native CPU Instructions              │  │
│  └────────────────────────────────────────────────────────┘  │
│                         │                                    │
│         Attached to kernel hook points:                      │
│                         │                                    │
│  ┌──────────┐  ┌────────┴──────┐  ┌──────────────────────┐  │
│  │ kprobes  │  │  tracepoints  │  │   XDP (eXpress Data  │  │
│  │(function │  │ (predefined   │  │    Path) - network   │  │
│  │  entry/  │  │  kernel hooks)│  │    driver level)     │  │
│  │  return) │  └───────────────┘  └──────────────────────┘  │
│  └──────────┘                                                │
│                                                              │
│  eBPF Maps: shared memory between eBPF programs and          │
│  user-space (hash maps, arrays, ring buffers, LRU)           │
└──────────────────────────────────────────────────────────────┘
```

### eBPF Hook Types and Use Cases

| Hook Point | When It Fires | Use Case |
|---|---|---|
| **kprobe** | Entry/exit of any kernel function | Deep kernel instrumentation, not stable across kernel versions |
| **tracepoint** | Predefined, stable kernel event points | Preferred for production tracing (stable API) |
| **uprobe** | Entry/exit of userspace function | Application-level tracing without code changes |
| **XDP** (eXpress Data Path) | At NIC driver level, before sk_buff allocation | Highest performance packet processing, DDoS mitigation |
| **tc (Traffic Control)** | After sk_buff creation, before routing | Network policy enforcement, load balancing |
| **socket** filters | Per-socket packet filtering | Network monitoring, selective capture |
| **LSM** (Linux Security Module) | Security decision points | Runtime security enforcement |

### eBPF Map Types

eBPF programs use maps to communicate with each other and with user-space:

```c
// eBPF map definition (in C, compiled to BPF bytecode)
struct {
    __uint(type, BPF_MAP_TYPE_HASH);    // Hash map
    __uint(max_entries, 65536);
    __type(key, u32);                    // Key: PID
    __type(value, u64);                  // Value: syscall count
} syscall_counts SEC(".maps");

// In eBPF program (attached to tracepoint):
SEC("tracepoint/syscalls/sys_enter_execve")
int trace_execve(struct trace_event_raw_sys_enter *ctx) {
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    u64 *count = bpf_map_lookup_elem(&syscall_counts, &pid);
    if (count) {
        (*count)++;
    } else {
        u64 initial = 1;
        bpf_map_update_elem(&syscall_counts, &pid, &initial, BPF_ANY);
    }
    return 0;
}
```

```python
# Reading eBPF map from user-space (using bcc Python bindings)
from bcc import BPF

bpf_program = """
#include <linux/sched.h>

BPF_HASH(syscall_counts, u32, u64);

TRACEPOINT_PROBE(syscalls, sys_enter_execve) {
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    u64 zero = 0, *count = syscall_counts.lookup_or_init(&pid, &zero);
    (*count)++;
    return 0;
}
"""

b = BPF(text=bpf_program)
# Read aggregated data from eBPF hash map
for k, v in b["syscall_counts"].items():
    print(f"PID {k.value}: {v.value} execve calls")
```

---

## Part 2: Cilium — eBPF-Powered CNI

Cilium replaces iptables/IPVS with eBPF programs for Kubernetes networking. This is the most important eBPF-in-production topic for DevOps interviews.

### Why Cilium Over Flannel/Calico/kube-proxy

| Dimension | kube-proxy (iptables) | Calico | Cilium (eBPF) |
|---|---|---|---|
| **Service routing** | iptables rules (O(n) lookup) | iptables or eBPF | eBPF maps (O(1) lookup) |
| **Network policy** | iptables | iptables | eBPF — identity-based (not IP-based) |
| **Load balancing** | iptables DNAT | iptables | eBPF XDP/tc — kernel bypass |
| **Observability** | None native | Limited | Full: flows, DNS, HTTP/gRPC |
| **mTLS** | No | No | Yes (WireGuard or Cilium mesh) |
| **Scale** | Degrades > 5,000 rules | Good | Linear — eBPF maps scale to millions of entries |
| **Network policy scope** | L3/L4 only | L3/L4 | L3/L4/L7 (HTTP path, gRPC method) |

### Cilium Identity-Based Security

Cilium does not use IP addresses for security policy enforcement. Instead, it uses **identity labels** — cryptographic identities derived from Pod labels. This means:

- Policies survive Pod restarts (IP changes, identity stays)
- Policies are enforced even during IP reuse windows
- Multi-cluster policies work without IP coordination

```yaml
# Cilium NetworkPolicy: L7-aware HTTP policy
# Allow GET /api/v1/health from frontend pods only, block everything else
apiVersion: "cilium.io/v2"
kind: CiliumNetworkPolicy
metadata:
  name: backend-api-policy
spec:
  endpointSelector:
    matchLabels:
      app: backend-api
  ingress:
    - fromEndpoints:
        - matchLabels:
            app: frontend          # Identity-based: any pod with this label
      toPorts:
        - ports:
            - port: "8080"
              protocol: TCP
          rules:
            http:
              - method: "GET"
                path: "/api/v1/health"   # L7: only this specific path
    - fromEndpoints:
        - matchLabels:
            app: internal-service
      toPorts:
        - ports:
            - port: "8080"
              protocol: TCP
          rules:
            http:
              - method: "GET"
              - method: "POST"
                path: "/api/v1/.*"       # Regex path matching
```

### Hubble: Cilium's Observability Layer

Hubble is the observability component of Cilium, providing network flow visibility with zero application instrumentation.

```bash
# Install Cilium with Hubble enabled
cilium install --set hubble.enabled=true --set hubble.relay.enabled=true --set hubble.ui.enabled=true

# Check Cilium status
cilium status

# Real-time network flow observation
hubble observe \
  --namespace production \
  --pod backend-api-7f8b9c \
  --follow \
  --output json

# Filter: show only dropped flows (debug network policy issues)
hubble observe \
  --namespace production \
  --verdict DROPPED \
  --follow

# DNS query observation
hubble observe \
  --namespace production \
  --protocol DNS \
  --follow

# HTTP flow observation with status codes
hubble observe \
  --namespace production \
  --protocol http \
  --http-status-code 5xx \
  --follow
```

---

## Part 3: Service Mesh Architecture at Scale

### Sidecar Mesh vs. Ambient Mesh

This is a critical architectural shift happening in the Istio ecosystem. Know both models.

#### Sidecar Mesh (Traditional Istio)

```
Pod A:                          Pod B:
┌────────────────────────┐      ┌────────────────────────┐
│  ┌──────────────────┐  │      │  ┌──────────────────┐  │
│  │  App Container   │  │      │  │  App Container   │  │
│  └────────┬─────────┘  │      │  └────────┬─────────┘  │
│           │ loopback   │      │           │ loopback   │
│  ┌────────▼─────────┐  │      │  ┌────────▼─────────┐  │
│  │  Envoy Sidecar   │◄─┼──mTLS┼─►│  Envoy Sidecar   │  │
│  │  (proxy all      │  │      │  │                  │  │
│  │   traffic)       │  │      │  │                  │  │
│  └──────────────────┘  │      │  └──────────────────┘  │
└────────────────────────┘      └────────────────────────┘
```

**Sidecar trade-offs:**
- ✅ Strong isolation: each pod's proxy is independent
- ✅ Per-pod configuration possible
- ❌ Resource overhead: every pod pays ~50-200MB RAM + CPU for a sidecar
- ❌ Slow rollout: mesh adoption requires pod restart per service
- ❌ Operational complexity: N sidecars to upgrade across a large cluster

#### Ambient Mesh (Istio 1.18+)

```
Node 1:
┌──────────────────────────────────────────────────┐
│  Pod A (app only, no sidecar)                    │
│  Pod B (app only, no sidecar)                    │
│  Pod C (app only, no sidecar)                    │
│                                                  │
│  ┌────────────────────────────────────────────┐  │
│  │  ztunnel (DaemonSet — one per node)        │  │
│  │  Layer 4: mTLS, telemetry, auth policy     │  │
│  └────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘

For L7 (HTTP routing, retries, circuit breaking):
Waypoint Proxy deployed per namespace or service account
(only if L7 features needed — opt-in)
```

**Ambient mesh trade-offs:**
- ✅ No sidecar overhead — apps get mTLS and L4 observability for free
- ✅ Instant adoption — no pod restart required
- ✅ Simpler operations — upgrade ztunnel DaemonSet, not thousands of sidecars
- ❌ Newer, less production-proven than sidecar model
- ❌ L7 features require waypoint proxy (additional complexity)
- ❌ Less isolation between pods sharing a ztunnel

> [!TIP]
> Interview signal: When asked to compare sidecar and ambient mesh, lead with the resource overhead numbers: "In a cluster with 2,000 pods, a sidecar mesh adds roughly 2,000 Envoy processes consuming an estimated 100GB+ of combined RAM. Ambient mesh replaces that with one ztunnel per node — typically 30-50 nodes — dramatically reducing the control plane footprint."

---

### Istio Multi-Cluster Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                 ISTIO MULTI-CLUSTER TOPOLOGY                     │
│                                                                  │
│  Cluster 1 (Primary)              Cluster 2 (Remote)            │
│  ┌─────────────────────┐          ┌─────────────────────┐       │
│  │  Istiod (control    │          │  Istiod (remote     │       │
│  │  plane)             │◄─────────│  watcher only)      │       │
│  │                     │          │                     │       │
│  │  East-West Gateway  │◄─mTLS───►│  East-West Gateway  │       │
│  │  (exposes services  │          │  (exposes services  │       │
│  │   to other clusters)│          │   to other clusters)│       │
│  │                     │          │                     │       │
│  │  Service: checkout  │          │  Service: inventory │       │
│  └─────────────────────┘          └─────────────────────┘       │
│                                                                  │
│  Traffic: checkout → inventory                                   │
│  Resolution: DNS → east-west gateway → remote cluster            │
│  Security: mTLS across clusters (shared root CA)                 │
└──────────────────────────────────────────────────────────────────┘
```

**Istio multi-cluster setup (primary-remote model):**

```bash
# Cluster 1: Install Istio as primary
istioctl install --set profile=default \
  --set values.pilot.env.EXTERNAL_ISTIOD=true

# Create a remote secret so Cluster 1 can access Cluster 2's API server
istioctl create-remote-secret \
  --context=cluster2 \
  --name=cluster2 | kubectl apply -f - --context=cluster1

# Cluster 2: Install Istio pointing to Cluster 1's control plane
istioctl install --set profile=remote \
  --set values.global.remotePilotAddress=<cluster1-istiod-ip>

# Verify multi-cluster service discovery
kubectl get serviceentries --all-namespaces --context=cluster1
```

**VirtualService for cross-cluster routing:**

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: inventory-routing
spec:
  hosts:
    - inventory.production.svc.cluster.local
  http:
    - match:
        - headers:
            x-region:
              exact: "us-east"
      route:
        - destination:
            host: inventory.production.svc.cluster.local
            subset: cluster1-inventory
    - route:
        # Default: load balance across both clusters
        - destination:
            host: inventory.production.svc.cluster.local
            subset: cluster1-inventory
          weight: 50
        - destination:
            host: inventory.production.svc.cluster.local
            subset: cluster2-inventory
          weight: 50
```

---

## Part 4: Falco — Runtime Security with eBPF

Falco uses eBPF to detect runtime security threats. Know how it works mechanically.

```
┌─────────────────────────────────────────────────────────────────┐
│              FALCO RUNTIME SECURITY                             │
│                                                                 │
│  Container (any)                                                │
│  └── Process makes system call (e.g., execve, open, connect)   │
│                │                                                │
│                ▼                                                │
│  eBPF Probe (attached to syscall tracepoints in kernel)         │
│                │                                                │
│                ▼                                                │
│  Event stream: {pid, comm, syscall, args, container_id, k8s}   │
│                │                                                │
│                ▼                                                │
│  Falco Rule Engine                                              │
│  ┌─────────────────────────────────────────────────────┐       │
│  │  rule: Shell spawned in container                   │       │
│  │  condition: evt.type = execve AND container.id != ∅  │       │
│  │             AND proc.name in (bash, sh, zsh)         │       │
│  │  output: "Shell spawned: %proc.name (user=%user.name)│       │
│  │           container=%container.id k8s=%k8s.pod.name" │       │
│  │  priority: WARNING                                  │       │
│  └─────────────────────────────────────────────────────┘       │
│                │                                                │
│                ▼                                                │
│  Alert: stdout / syslog / webhook / Falcosidekick              │
│         → Slack, PagerDuty, Elasticsearch, Kubernetes audit    │
└─────────────────────────────────────────────────────────────────┘
```

**High-value Falco rules:**

```yaml
# falco_rules.yaml

# Detect sensitive file reads
- rule: Read sensitive file by non-privileged process
  desc: Detects reading /etc/shadow or /etc/sudoers outside of expected processes
  condition: >
    open_read
    and sensitive_files
    and not proc.name in (sshd, sudo, su, pam*)
    and not container.image.repository = "security-scanner"
  output: >
    Sensitive file opened for reading (user=%user.name command=%proc.cmdline
    file=%fd.name container=%container.id image=%container.image.repository)
  priority: WARNING

# Detect outbound connection from a container that should be isolated
- rule: Unexpected outbound network connection
  desc: Container making outbound connection to unexpected destination
  condition: >
    outbound
    and container
    and not fd.sip in (allowed_ips)
    and container.image.repository = "backend-processor"
  output: >
    Unexpected outbound connection (command=%proc.cmdline connection=%fd.name
    container=%container.id)
  priority: CRITICAL

# Detect privilege escalation
- rule: Privilege escalation via setuid binary
  desc: Process executing a setuid binary
  condition: >
    evt.type = execve
    and proc.is_suid_exe = true
    and not proc.name in (sudo, su, passwd)
  output: >
    Setuid binary executed (user=%user.name binary=%proc.name
    container=%container.id)
  priority: ERROR
```

**Falco on Kubernetes:**

```bash
# Install Falco via Helm with eBPF driver
helm repo add falcosecurity https://falcosecurity.github.io/charts
helm install falco falcosecurity/falco \
  --set driver.kind=ebpf \                    # Use eBPF (not kernel module)
  --set falcosidekick.enabled=true \           # Forward alerts to other systems
  --set falcosidekick.config.slack.webhookurl=$SLACK_WEBHOOK \
  --namespace falco --create-namespace

# Check Falco pod health
kubectl get pods -n falco
kubectl logs -n falco -l app=falco --tail=50

# Test: trigger a rule intentionally
kubectl exec -it <some-pod> -- bash   # Should trigger "shell spawned in container"
kubectl logs -n falco -l app=falco --tail=10 | grep "shell"
```

---

## Interview Q&A Bank

### Easy

**Q1: What is eBPF and why is it considered safer than writing kernel modules?**

eBPF is a technology that allows running sandboxed programs in the Linux kernel without modifying the kernel source or loading kernel modules. It is safer than kernel modules because every eBPF program must pass a kernel-internal verifier before execution. The verifier statically analyzes the program and rejects any code that might crash the kernel — including unbounded loops, invalid memory access, or programs that exceed the complexity limit. A kernel module has no such protection: a bug in a kernel module can kernel panic the entire host. An eBPF program that passes the verifier is guaranteed to terminate and will not crash the kernel.

**Q2: What is a service mesh and what four problems does it solve that Kubernetes does not natively provide?**

A service mesh is an infrastructure layer that manages all service-to-service communication in a microservices architecture. The four problems it solves that are not native to Kubernetes:

1. **Mutual TLS (mTLS)** — encrypts and mutually authenticates all inter-service traffic. Kubernetes provides network connectivity but no built-in encryption between pods.
2. **Traffic management** — fine-grained routing, weighted traffic splits, retries, timeouts, and circuit breaking. Kubernetes Services are round-robin load balancers with no traffic shaping.
3. **Observability** — automatic telemetry (request rates, latency histograms, error rates) for all inter-service calls without code changes.
4. **Access policy** — define which service is allowed to call which other service, at the HTTP method or gRPC service level. Kubernetes NetworkPolicy operates at L3/L4 (IP and port) only.

---

### Medium

**Q3: A Kubernetes cluster with 3,000 pods is showing degraded Service response times. Monitoring shows normal CPU and memory. What eBPF-based tool would you use and what would you look for?**

With 3,000 pods and no CPU/memory pressure, the likely culprit is kube-proxy iptables rule processing overhead. In large clusters, kube-proxy creates tens of thousands of iptables rules for Service routing. Every packet traverses a linear chain of iptables rules — latency increases with the number of rules.

I would use **Hubble** (if Cilium is deployed) or install **Pixie** for immediate cluster-wide visibility:

```bash
# With Cilium/Hubble: check for packet drops and retransmissions
hubble observe --namespace production --verdict DROPPED --follow

# Check iptables rule count on a node (symptom confirmation)
kubectl exec -it <node-debug-pod> -- iptables-save | wc -l
# > 20,000 rules indicates the iptables scaling problem

# With Pixie: trace HTTP latency without instrumentation
px run px/http_data_filtered -- -start_time='-5m' -namespace='production'
```

The long-term fix is to replace kube-proxy with Cilium's eBPF-based data plane, which uses O(1) hash map lookups instead of O(n) iptables chain traversal.

**Q4: What is the difference between Istio's sidecar model and ambient mesh? When would you choose ambient?**

In the sidecar model, Istio injects an Envoy proxy container into every Pod. The proxy intercepts all network traffic for that pod. This provides strong per-pod isolation and L7 features for every service, but at significant cost: memory overhead of ~100-200MB per pod, slow mesh adoption requiring pod restarts, and the operational burden of upgrading thousands of sidecar proxies.

Ambient mesh replaces per-pod sidecars with a per-node ztunnel DaemonSet that handles L4 features (mTLS, authorization, observability) for all pods on the node, plus optional per-namespace waypoint proxies for L7 features. No pod restart is required for mesh adoption.

Choose ambient when: you have a large cluster where sidecar overhead is significant, you want rapid mesh adoption without redeployment, or most of your traffic only needs L4 features (encryption, basic authorization) rather than L7 routing. Choose sidecar when: you need per-pod isolation guarantees, you need L7 features for most services, or you are in a regulated environment where the ambient model's shared ztunnel per node conflicts with isolation requirements.

---

### Hard

**Q5: Design a zero-trust network architecture for a Kubernetes cluster serving a financial application with strict compliance requirements.**

Zero-trust means: verify every request, trust no network path, enforce least-privilege access.

**Layer 1 — Identity (not IP):**
Deploy Cilium as the CNI. Cilium's identity-based policy uses cryptographic pod identities derived from labels, not IP addresses. Policies survive pod restarts and IP recycling.

**Layer 2 — Mutual Authentication:**
Deploy Istio (or Cilium mesh) to enforce mTLS for all inter-pod communication. Every service connection is authenticated at both ends using SPIFFE/SPIRE-issued X.509 certificates. No service can communicate without a valid, cluster-issued certificate.

**Layer 3 — Authorization Policy:**
```yaml
# Istio AuthorizationPolicy: explicit allow-list only
# Default: deny all (configured at mesh level)
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: payments-service-policy
  namespace: production
spec:
  selector:
    matchLabels:
      app: payments-service
  action: ALLOW
  rules:
    - from:
        - source:
            principals:             # SPIFFE identity — not IP
              - "cluster.local/ns/production/sa/checkout-service"
      to:
        - operation:
            methods: ["POST"]
            paths: ["/api/v1/charge"]
```

**Layer 4 — Runtime Threat Detection:**
Deploy Falco with eBPF driver. Rules: alert on any shell execution in a financial container, any unexpected outbound connection, any sensitive file read outside of approved processes. Forward alerts to SIEM.

**Layer 5 — Egress Control:**
Restrict all outbound internet traffic through a managed egress gateway. Only approved external domains (payment processors, banks) are reachable. All other egress is blocked by a Cilium `CiliumNetworkPolicy` with default-deny egress.

**Layer 6 — Audit:**
Enable Kubernetes audit logs, Istio access logs, and Hubble flow logs. Ship all to a SIEM with tamper-proof retention (S3 + Object Lock or equivalent).

**Q6: A Cilium upgrade on a 500-node cluster causes 15% of pods to lose network connectivity. Walk through your incident response and rollback strategy.**

**Immediate actions (T+0 to T+5):**

```bash
# Confirm blast radius
kubectl get pods --all-namespaces | grep -v Running | grep -v Completed
# How many pods affected? Which namespaces?

# Check Cilium agent health
kubectl get pods -n kube-system -l k8s-app=cilium
kubectl logs -n kube-system -l k8s-app=cilium --tail=100 | grep -i error

# Check Cilium connectivity
cilium connectivity test
cilium status --all-nodes

# Is the problem on specific nodes?
kubectl get nodes
kubectl describe node <affected-node> | grep -A 20 "Events:"
```

**Diagnosis:**

Cilium upgrades can fail when the new eBPF programs are incompatible with the current kernel version on some nodes. The 15% affected likely corresponds to nodes with a different kernel version.

```bash
# Check kernel versions across nodes
kubectl get nodes -o custom-columns='NAME:.metadata.name,KERNEL:.status.nodeInfo.kernelVersion'

# Check if Cilium agent pods are crashing on affected nodes
kubectl get pods -n kube-system -l k8s-app=cilium -o wide
# Correlate crashing cilium pods with affected application pods
```

**Rollback strategy:**

Cilium upgrades cannot simply be reverted by redeploying the old DaemonSet image — the eBPF programs must be replaced atomically.

```bash
# Step 1: Identify the old Cilium version from Helm history
helm history cilium -n kube-system

# Step 2: Rollback via Helm (this redeploys the previous DaemonSet version)
helm rollback cilium <previous-revision> -n kube-system

# Step 3: Force restart Cilium agents on affected nodes
kubectl rollout restart daemonset/cilium -n kube-system

# Step 4: Verify connectivity is restored
cilium connectivity test
kubectl get pods --all-namespaces | grep -v Running

# Step 5: For pods that still have no connectivity after cilium restart
# Delete and let them reschedule — Cilium will inject fresh eBPF rules
kubectl delete pod <affected-pod> -n <namespace>
```

**Prevention:** Implement a staged Cilium upgrade: upgrade one node pool at a time using node taints to prevent scheduling during upgrade, validate connectivity after each pool before proceeding to the next.

---

## Key Terms Cheat Sheet

| Term | One-Line Definition |
|---|---|
| eBPF | Kernel-level programmability: run sandboxed programs at kernel events without kernel module |
| eBPF Verifier | Kernel component that statically checks every eBPF program for safety before loading |
| XDP | eXpress Data Path — eBPF hook at NIC driver level, bypasses sk_buff for maximum throughput |
| kprobe | eBPF hook on any kernel function entry/exit — powerful but not stable across kernel versions |
| tracepoint | Predefined, stable kernel hook points — preferred for production eBPF programs |
| eBPF Map | Shared data structure between eBPF programs and user-space (hash, array, ring buffer) |
| Cilium | eBPF-based CNI: replaces iptables/kube-proxy with O(1) eBPF map-based networking |
| Hubble | Cilium's observability layer — network flows, DNS, HTTP visibility with zero app changes |
| Identity-based policy | Security policy keyed on Pod labels/SPIFFE identity, not IP addresses |
| Sidecar mesh | Istio model: Envoy proxy injected into every Pod — strong isolation, high resource overhead |
| Ambient mesh | Istio 1.18+ model: shared ztunnel DaemonSet per node — lower overhead, no pod restart |
| ztunnel | Per-node proxy in Istio ambient mesh handling L4 mTLS and observability |
| Waypoint proxy | Per-namespace/SA proxy in Istio ambient mesh providing L7 features |
| SPIFFE | Standard for workload identity: "I am service X in namespace Y in cluster Z" |
| Falco | Runtime security engine using eBPF to detect threats via syscall monitoring |
| Falcosidekick | Falco alert router — fans alerts out to Slack, PagerDuty, Elasticsearch |
| Service mesh | Infrastructure layer managing inter-service communication: mTLS, routing, observability |
| East-West traffic | Traffic between services inside the cluster (vs. North-South: user → cluster) |
| mTLS | Mutual TLS — both client and server authenticate each other with certificates |
