# Networking Interview Questions — Hard

Advanced concepts for senior/staff DevOps and SRE roles.

***

## 1. Explain the data plane vs. control plane architecture of Istio.

**Answer:**

Istio follows a **control plane / data plane** separation, a common pattern in software-defined networking.

### Control Plane (Istiod)

**Does NOT touch packets.** Manages and configures the proxies.

**Components:**
| Component | Responsibility |
|-----------|----------------|
| **Pilot** | Translates high-level rules (`VirtualService`, `DestinationRule`) into Envoy xDS configuration; pushes via gRPC |
| **Citadel** | Certificate Authority; issues short-lived X.509 certs to each Envoy; encodes SPIFFE identity |
| **Galley** | Config validation and distribution |

**xDS APIs (pushed to Envoy):**
- **LDS** (Listener Discovery): What ports to listen on
- **RDS** (Route Discovery): How to route requests
- **CDS** (Cluster Discovery): Backend cluster definitions
- **EDS** (Endpoint Discovery): Healthy endpoint IPs

### Data Plane (Envoy Sidecars)

**Intercepts and processes all traffic.**

**How traffic flows:**
```
Incoming Packet
       ↓
iptables REDIRECT (prerouting)
       ↓
Envoy sidecar (listening on 15001)
       ↓
┌─────────────────────────────────────┐
│  Envoy Filter Chain                 │
│  1. RBAC check (is request allowed?)│
│  2. mTLS decryption                 │
│  3. Route lookup (VirtualService)   │
│  4. Apply retries/timeouts          │
│  5. Record metrics (counters)       │
│  6. Forward to upstream             │
└─────────────────────────────────────┘
       ↓
Destination Pod's Envoy
       ↓
Application Container
```

### Key Design Decisions

**Why sidecar over daemonset?**
- Per-pod isolation (different policies per service)
- Co-located with application (same network namespace)
- Independent scaling

**Why iptables REDIRECT?**
- Transparent to application (no code changes)
- All traffic intercepted without app awareness
- Works with any language/framework

**Trade-offs:**
| Aspect | Benefit | Cost |
|--------|---------|------|
| Transparency | No app changes | iptables complexity, debugging difficulty |
| Per-request routing | Fine-grained traffic control | Increased latency (~5-10ms per hop) |
| mTLS everywhere | Zero-trust security | CPU overhead for encryption |
| Centralized config | Consistent policies | Control plane is critical (SPOF if not HA) |

### Debugging Istio Issues

```bash
# Check proxy config
istioctl proxy-config listeners <pod>
istioctl proxy-config routes <pod>
istioctl proxy-config clusters <pod>
istioctl proxy-config endpoints <pod>

# Verify mTLS
istioctl authn tls-check <pod>

# Analyze config
istioctl analyze

# Access logs
istioctl accesslog <pod>
```

***

## 2. How does Cilium replace kube-proxy and what performance benefit does it provide?

**Answer:**

### The Problem: iptables Scaling

kube-proxy uses iptables for Service load balancing:

```
# For each Service, iptables has rules like:
-A KUBE-SVC-XXX -m statistic --mode random --probability 0.33 -j KUBE-SEP-1
-A KUBE-SVC-XXX -m statistic --mode random --probability 0.50 -j KUBE-SEP-2
-A KUBE-SVC-XXX -j KUBE-SEP-3
```

**Scaling Issue:**
- O(n) rule traversal per packet
- 10,000 services = 10,000+ rules per packet
- Each rule = memory access + CPU cycles
- At 100k packets/sec, this adds up to significant CPU overhead

### Cilium's eBPF Solution

Cilium uses **eBPF programs** in the kernel's network path:

```
Packet arrives at NIC
       ↓
XDP Hook (earliest possible point)
       ↓
eBPF Program: Hash map lookup
       ↓
O(1) decision: Forward to Pod IP
       ↓
Direct delivery (no iptables traversal)
```

**How it works:**
1. Cilium compiles Service definitions into eBPF bytecode
2. eBPF program loaded into kernel at XDP/TC hook
3. BPF map (hash table) contains Service → Pod mappings
4. Each packet does single hash lookup → gets destination
5. No rule traversal, no context switch to userspace

### Performance Comparison

| Metric | iptables (kube-proxy) | Cilium eBPF |
|--------|----------------------|-------------|
| Lookup complexity | O(n) | O(1) |
| 10,000 services | ~10,000 rule checks | 1 hash lookup |
| CPU overhead | High (scales with services) | Constant |
| Latency | 50-100μs per packet | 5-10μs per packet |
| Context switches | Multiple (kernel↔userspace) | Zero (all in-kernel) |

**Benchmarks (Cilium team):**
- 50-70% reduction in CPU overhead at 10k services
- Single-digit microsecond processing vs. 50-100μs
- 4x higher throughput before saturation

### Additional Benefits

**Identity-based NetworkPolicy:**
- iptables: IP-based rules (fragile, IPs change)
- Cilium: Cryptographic identity based on Kubernetes labels
- Policy survives pod IP changes

**Observability (Hubble):**
```bash
# Real-time flow visibility
hubble observe --follow

# Service dependency map
hubble observe --graph

# HTTP-level visibility (L7)
hubble observe --protocol http
```

**When to use Cilium:**
- Clusters with 1000+ services
- Need L7 network policies
- Require per-flow observability
- Bare-metal performance requirements

***

## 3. How do you design a multi-cluster service mesh for active-active failover?

**Answer:**

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Global DNS (Route53)                     │
│          Routes users to nearest healthy cluster            │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        ↓                         ↓
┌───────────────────┐   ┌───────────────────┐
│   Cluster East    │   │   Cluster West    │
│   (us-east-1)     │   │   (us-west-2)     │
├───────────────────┤   ├───────────────────┤
│ ┌───────────────┐ │   │ ┌───────────────┐ │
│ │  Istiod (CP)  │ │   │ │  Istiod (CP)  │ │
│ └───────┬───────┘ │   │ └───────┬───────┘ │
│         │         │   │         │         │
│ ┌───────▼───────┐ │   │ ┌───────▼───────┐ │
│ │ East-West GW  │ │   │ │ East-West GW  │ │
│ │ (mTLS ingress)│ │   │ │ (mTLS ingress)│ │
│ └───────┬───────┘ │   │ └───────┬───────┘ │
│         │         │   │         │         │
│ ┌───────▼───────┐ │   │ ┌───────▼───────┐ │
│ │ api (local)   │ │   │ │ api (local)   │ │
│ │ api (remote)──┼─┼───┼─→ api (local)   │ │
│ │               │ │   │ │               │ │
│ └───────────────┘ │   │ └───────────────┘ │
└───────────────────┘   └───────────────────┘
        ↑                         ↑
        └────────────┬────────────┘
                     │
              Shared Root CA
         (for cross-cluster mTLS)
```

### Configuration Steps

**1. Shared Certificate Authority**
```yaml
# Both clusters must trust the same root CA
# Option A: Use Istio's multi-cluster shared root
# Option B: Integrate with external CA (Vault, SPIRE)
```

**2. ServiceEntry (Register Remote Service)**
```yaml
apiVersion: networking.istio.io/v1beta1
kind: ServiceEntry
metadata:
  name: api-remote
spec:
  hosts:
  - api.remote.global
  location: MESH_INTERNAL
  ports:
  - number: 80
    name: http
    protocol: HTTP
  resolution: DNS
  endpoints:
  - address: east-west-gw.west.example.com
    ports:
      http: 15443
    labels:
      topology.istio.io/network: west
```

**3. DestinationRule (Load Balancing Policy)**
```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: api-global
spec:
  host: api.global
  trafficPolicy:
    connectionPool:
      http:
        h2UpgradePolicy: UPGRADE
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
    loadBalancer:
      policy: LOCALITY_FAILOVER
      localityLbSetting:
        distribute:
        - from: us-east-1/zone1
          to:
            "us-east-1/zone1": 80
            "us-west-2/zone1": 20
```

**4. VirtualService (Traffic Splitting)**
```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: api-global
spec:
  hosts:
  - api.global
  http:
  - route:
    - destination:
        host: api.local
        port:
          number: 80
      weight: 80
    - destination:
        host: api.remote.global
        port:
          number: 80
      weight: 20
```

**5. Global DNS Routing**
```yaml
# Route53 Health Check + Failover
# Primary: us-east-1 ELB
# Secondary: us-west-2 ELB
# Failover trigger: Health check failures
```

### Split-Brain Prevention

**Problem:** Network partition between clusters → both think they're primary.

**Solutions:**

| Mechanism | Implementation |
|-----------|----------------|
| **Clear failover logic** | `DestinationRule` with locality failover + outlier detection |
| **Health checks** | Active probing of cross-cluster endpoints; remove unhealthy from pool |
| **Quorum-based decisions** | Use external consensus (etcd, Consul) for primary election |
| **Lease-based leadership** | Kubernetes Lease API for primary designation |
| **Database constraints** | For stateful services: single primary DB with read replicas |

### Testing Failover

```bash
# Simulate cluster failure
kubectl scale deployment api --replicas=0 -n east

# Monitor traffic shift
hubble observe --follow | grep api

# Check endpoint health
istioctl proxy-config endpoints <pod> | grep api

# Verify DNS failover
dig +short api.global @8.8.8.8
```

***

## 4. What is a split-brain scenario in multi-cluster networking and how is it prevented?

**Answer:**

### What is Split-Brain?

**Split-brain** occurs when network connectivity between clusters is lost, and each cluster acts as the sole authority, leading to:
- Inconsistent configurations
- Duplicate resource creation
- Routing failures
- Data corruption (for stateful services)

### Example Scenario

```
Before Partition:
┌─────────────┐         ┌─────────────┐
│  Cluster A  │◄───────►│  Cluster B  │
│  Primary    │  Sync   │  Secondary  │
└─────────────┘         └─────────────┘

After Partition:
┌─────────────┐         ┌─────────────┐
│  Cluster A  │         │  Cluster B  │
│  "I'm primary"│       │"I'm primary"│
│  Accepts writes│      │ Accepts writes│
└─────────────┘         └─────────────┘
       │                       │
       └───────────┬───────────┘
                   ↓
          Data inconsistency!
```

### Prevention Strategies

**1. Quorum-Based Consensus**
```
Cluster A (3 nodes)    Cluster B (2 nodes)
      ●                     ●
     / \                   /
    ●   ●                 ●

Total: 5 nodes
Quorum: 3 nodes required

After partition:
- Cluster A: 3 nodes = has quorum = remains primary
- Cluster B: 2 nodes = no quorum = becomes read-only
```

**Implementation:** etcd, Consul, ZooKeeper

**2. Lease-Based Leadership**
```yaml
# Kubernetes Lease API
apiVersion: coordination.k8s.io/v1
kind: Lease
metadata:
  name: primary-lease
spec:
  leaseDurationSeconds: 15
  renewTime: 2024-01-15T10:00:00Z  # Must renew before expiry
```

**Behavior:**
- Primary must renew lease every N seconds
- If partitioned, lease expires
- Other cluster sees expired lease → takes over
- Original cluster can't renew (no quorum) → steps down

**3. Database-Level Protection**
| Database | Split-Brain Prevention |
|----------|------------------------|
| PostgreSQL | Single primary, synchronous replication |
| MySQL | Group Replication with consensus |
| MongoDB | Replica set with odd number of voting members |
| CockroachDB | Raft consensus across regions |

**4. Mesh-Level Protection**
```yaml
# DestinationRule with strict outlier detection
outlierDetection:
  consecutive5xxErrors: 3
  interval: 10s
  baseEjectionTime: 60s
  maxEjectionPercent: 100  # Eject ALL unhealthy endpoints
```

**5. External Arbitration**
```
┌─────────────┐
│   Cloud     │
│  Provider   │
│  (AWS/GCP)  │
└──────┬──────┘
       │ Health check
       ↓
┌─────────────┐         ┌─────────────┐
│  Cluster A  │         │  Cluster B  │
│  Active     │         │  Standby    │
└─────────────┘         └─────────────┘
```

Use cloud load balancer health checks as external arbiter.

### Detection and Recovery

**Detection:**
```bash
# Monitor cross-cluster connectivity
mtr --report west-gw.east.example.com

# Check lease status
kubectl get lease primary-lease -o jsonpath='{.spec.renewTime}'

# Verify database replication lag
psql -c "SELECT pg_last_wal_receive_lag();"
```

**Recovery:**
1. Restore network connectivity
2. Reconcile data conflicts (application-specific)
3. Re-establish primary/secondary relationship
4. Resync data from authoritative source
5. Gradually restore traffic

***

## 5. How does VXLAN work and what overhead does it add?

**Answer:**

### VXLAN Fundamentals

**VXLAN (Virtual Extensible LAN)** encapsulates Layer 2 Ethernet frames inside Layer 4 UDP packets.

**Purpose:**
- Extend Layer 2 segments across Layer 3 boundaries
- Overcome 4094 VLAN limit (VXLAN: 16 million segments)
- Enable multi-tenant cloud networking

### Packet Structure

```
┌─────────────────────────────────────────────────────────────┐
│ Original Frame (from Pod/VM)                                │
│ ┌──────────┬──────────┬──────────┬──────────┬───────────┐   │
│ │Dst MAC   │Src MAC   │EtherType │Payload  │FCS        │   │
│ └──────────┴──────────┴──────────┴──────────┴───────────┘   │
└─────────────────────────────────────────────────────────────┘
                          ↓ Encapsulation
┌─────────────────────────────────────────────────────────────┐
│ VXLAN Packet (on wire)                                      │
├──────────────┬──────────────┬──────────────┬───────────────┤
│Outer Ethernet│Outer IP (UDP)│VXLAN Header  │Inner Frame    │
│(14 bytes)    │(20+8 bytes)  │(8 bytes)     │(Original)     │
└──────────────┴──────────────┴──────────────┴───────────────┘
```

### VXLAN Header (8 bytes)

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
│R|R|R|R|I|R|R|R|            Reserved                           │
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
│                VXLAN Network Identifier (VNI)                 │
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
│                    Reserved                                   │
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

**VNI (24 bits):** Identifies the VXLAN segment (16 million possible)

### Overhead Calculation

| Layer | Size |
|-------|------|
| Outer Ethernet Header | 14 bytes |
| Outer IP Header | 20 bytes |
| Outer UDP Header | 8 bytes |
| VXLAN Header | 8 bytes |
| **Total Overhead** | **50 bytes** |

**Impact:**
- Standard Ethernet MTU: 1500 bytes
- Effective inner MTU: 1500 - 50 = **1450 bytes**
- CNI plugins must configure reduced MTU on Pod interfaces

### VTEP (VXLAN Tunnel Endpoint)

**Role:** Encapsulates/decapsulates VXLAN traffic.

**Location:**
- Linux kernel (vxlan module)
- SmartNIC (hardware offload)
- Physical switch (VXLAN gateway)

**Learning Modes:**

| Mode | How it works | Use case |
|------|--------------|----------|
| **Multicast** | Unknown destinations flooded to multicast group | Simple, requires multicast underlay |
| **Unicast with learning** | VTEPs learn MAC→VTEP mapping from traffic | Small clusters |
| **BGP EVPN** | VTEPs advertise MAC/IP via BGP | Production data centers |

### VXLAN in Kubernetes

**Flannel (VXLAN backend):**
```
Pod A (Node 1) → Pod B (Node 2)
     ↓
flannel.1 interface (VTEP)
     ↓
Encapsulate: Inner Ethernet + VXLAN + UDP + IP
     ↓
Physical network (underlay)
     ↓
Node 2 flannel.1 (VTEP)
     ↓
Decapsulate → Pod B
```

**Cilium (VXLAN vs BGP):**
- VXLAN: Works everywhere, 50-byte overhead
- BGP: No encapsulation, requires BGP-capable underlay

### Troubleshooting VXLAN

```bash
# Check VXLAN interface
ip -d link show flannel.1

# View VXLAN forwarding table
bridge fdb show dev flannel.1

# Capture VXLAN traffic
tcpdump -i eth0 -n udp port 4789

# Check MTU mismatch
ip link show | grep mtu
# Pod should show mtu 1450 if physical is 1500

# Test with different packet sizes
ping -M do -s 1422 <pod-ip>  # Should work (1422 + 28 = 1450)
ping -M do -s 1450 <pod-ip>  # May fail if physical MTU is 1500
```

### VXLAN vs Alternatives

| Protocol | Overhead | Encryption | Use Case |
|----------|----------|------------|----------|
| VXLAN | 50 bytes | No (add IPsec) | Kubernetes, VMware NSX |
| Geneve | Variable (min 50) | No | OVN, OpenStack |
| GRE | 24 bytes | No (add IPsec) | Simple tunnels |
| WireGuard | 60 bytes | Yes (built-in) | Modern VPN |
| IPsec Tunnel | 50-70 bytes | Yes | Site-to-site VPN |

***

## 6. Design a zero-trust network architecture for a microservices platform.

**Answer:**

### Zero Trust Principles

1. **Never trust, always verify** — No implicit trust based on network location
2. **Least privilege access** — Minimum necessary permissions
3. **Assume breach** — Minimize blast radius

### Architecture Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Identity Layer                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │   SPIRE     │  │   Vault     │  │  OPA        │          │
│  │  (Workload  │  │  (Secrets   │  │  (Policy    │          │
│  │   Identity) │  │   Mgmt)     │  │   Engine)   │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                   Data Plane (Mesh)                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │  Pod A   │  │  Pod B   │  │  Pod C   │  │  Pod D   │     │
│  │ ┌──────┐ │  │ ┌──────┐ │  │ ┌──────┐ │  │ ┌──────┐ │     │
│  │ │ App  │ │  │ │ App  │ │  │ │ App  │ │  │ │ App  │ │     │
│  │ └──┬───┘ │  │ └──┬───┘ │  │ └──┬───┘ │  │ └──┬───┘ │     │
│  │ ┌──▼───┐ │  │ ┌──▼───┐ │  │ ┌──▼───┐ │  │ ┌──▼───┐ │     │
│  │ │Envoy │ │  │ │Envoy │ │  │ │Envoy │ │  │ │Envoy │ │     │
│  │ │Sidecar│ │  │ │Sidecar│ │  │ │Sidecar│ │  │ │Sidecar│ │    │
│  │ └──────┘ │  │ └──────┘ │  │ └──────┘ │  │ └──────┘ │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
│         mTLS for all service-to-service communication       │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                   Perimeter Layer                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │   WAF       │  │  API GW     │  │  DDoS       │          │
│  │ (ModSecurity│  │  (Kong/     │  │  Protection │          │
│  │  + OWASP)   │  │   Apigee)   │  │  (Cloudflare│          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

### Implementation Details

**1. Workload Identity (SPIFFE/SPIRE)**
```
# Each Pod gets a SPIFFE ID
spiffe://cluster.local/ns/default/sa/frontend
spiffe://cluster.local/ns/default/sa/backend
spiffe://cluster.local/ns/db/sa/postgres
```

**SPIRE Server:**
- Issues short-lived X.509 certificates (1 hour TTL)
- Cert encodes SPIFFE ID in URI SAN
- Attestation proves workload identity

**2. mTLS Configuration (Istio)**
```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: default
spec:
  mtls:
    mode: STRICT  # Reject non-mTLS traffic
***
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: frontend-allow-backend
spec:
  selector:
    matchLabels:
      app: frontend
  action: ALLOW
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/default/sa/backend"]
    to:
    - operation:
        paths: ["/api/*"]
        methods: ["GET", "POST"]
```

**3. Network Segmentation**
```yaml
# Kubernetes NetworkPolicy
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: database-isolation
spec:
  podSelector:
    matchLabels:
      app: postgres
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: backend
    - podSelector:
        matchLabels:
          app: api
    ports:
    - protocol: TCP
      port: 5432
```

**4. Secret Management (Vault)**
```yaml
# Dynamic database credentials
apiVersion: secrets.hashicorp.com/v1
kind: VaultStaticSecret
metadata:
  name: db-credentials
spec:
  type: kv-v2
  mount: secret
  path: database/prod
  destination:
    name: db-credentials
    keys:
    - username
    - password
```

**5. Policy Enforcement (OPA)**
```rego
# Example OPA policy for Kubernetes
package kubernetes.admission

deny[msg] {
  input.request.kind.kind == "Pod"
  not input.request.object.spec.securityContext.runAsNonRoot
  msg := "Pods must run as non-root"
}

deny[msg] {
  input.request.kind.kind == "Deployment"
  not input.request.object.spec.template.spec.containers[_].resources.limits.cpu
  msg := "CPU limits are required"
}
```

### Observability

```bash
# Service-to-service dependency map
hubble observe --graph

# Failed mTLS connections
hubble observe --verdict DROPPED

# Policy violations
kubectl logs -n istio-system -l app=istiod | grep "denied"

# Audit trail
vault audit enable file file_path=/var/log/vault/audit.log
```

### Key Metrics

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| mTLS coverage | 100% | <99% |
| Certificate expiry | >7 days | <24 hours |
| Policy violations | 0 | >0 |
| Secret rotation | Automated | Manual intervention |

***

## Quick Reference: Advanced Troubleshooting

```bash
# eBPF packet inspection
cilium monitor --type drop

# Istio configuration dump
istioctl proxy-config all <pod> -o json

# Connection tracking at scale
conntrack -L | wc -l
sysctl net.netfilter.nf_conntrack_count

# BGP peering status (Calico)
calicoctl node status

# VXLAN tunnel health
ip -s link show vxlan0

# DNS latency breakdown
kubectl exec <pod> -- time nslookup <service>

# TLS handshake analysis
openssl s_client -connect <host>:443 -tls1_3 -msg
```

***

## 7. Explain HTTP/2 HPACK and how it solves the overhead of HTTP/1.1 headers.

**Answer:**

### The Problem: Verbose Headers
In HTTP/1.1, headers are sent as plain text with every request. For small API calls, the headers (Cookie, User-Agent, etc.) are often larger than the payload itself, wasting bandwidth and increasing latency.

### The Solution: HPACK Compression
HTTP/2 uses **HPACK**, a specialized compression algorithm for headers.

**How it works:**
1. **Static Table:** Both client and server start with a pre-defined table of common headers (e.g., `:method: GET`, `:status: 200`).
2. **Dynamic Table:** As headers are sent, they are added to a dynamic table. If a header is repeated (e.g., a session cookie), only its **index** in the table is sent.
3. **Huffman Encoding:** String values that are not in the table are compressed using a custom Huffman code optimized for HTTP headers.

**Performance Impact:**
- Reduces header overhead by **85-95%**.
- A 500-byte header block can be reduced to ~20 bytes.
- Crucial for mobile networks and high-concurrency gRPC streams.

***

## 8. What is TCP BBR and why is it superior to CUBIC for high-bandwidth, long-haul links?

**Answer:**

### CUBIC (Loss-Based)
Most OS kernels use TCP CUBIC. It assumes that **packet loss = congestion**. When a packet is lost, it cuts the congestion window (CWND) by half.
- **Problem:** On modern high-speed links (fiber), packet loss often happens due to noise or transient errors, not actual congestion. CUBIC unnecessarily throttles speed.

### BBR (Model-Based)
BBR (Bottleneck Bandwidth and Round-trip time) was developed by Google. It ignores packet loss as a primary signal.
- **How it works:** It constantly probes the network to estimate the **Max Bandwidth** and **Min RTT**.
- **The Model:** It sends data at a rate that exactly fills the "pipe" without creating a queue in the routers.
- **Result:** It maintains high throughput even in the face of 10-20% packet loss.

**When to use:**
- Cross-region database replication.
- Streaming video delivery.
- Large file transfers (CI/CD artifact uploads).

***

## 9. Explain the "Thundering Herd" problem in networking and how to mitigate it.

**Answer:**

### The Scenario
A backend service goes down. Thousands of clients or internal workers are waiting. The moment the service comes back online, all thousands of clients reconnect and request data simultaneously.

### The Result
The service is immediately overwhelmed and crashes again. This is a **Thundering Herd** or **Retry Storm**.

### Mitigation Strategies:
1. **Exponential Backoff:** Clients wait longer between each retry (1s, 2s, 4s, 8s...).
2. **Jitter:** Add a random delay to the backoff (e.g., 4s + a random 0-500ms). This prevents "synchronized" retries.
3. **Circuit Breaking:** Use a service mesh (Istio) to "open" the circuit and return an error immediately when a service is failing, giving it room to recover.
4. **Queue Leveling:** Place a message queue (Kafka/SQS) in front of the service to buffer the spike.

***
