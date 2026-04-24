# Networking Interview Questions — Medium

Intermediate concepts for mid-level DevOps engineering roles.

***

## 1. Explain the TCP three-way handshake.

**Answer:**

The TCP 3-way handshake establishes a reliable connection between client and server before data transfer.

```
Client                          Server
  |------- SYN (seq=x) -------->|   1. Client sends SYN with initial sequence number
  |<----- SYN-ACK (seq=y) ------|   2. Server acknowledges + sends its own SYN
  |       (ack=x+1) ------------|
  |------- ACK (ack=y+1) ------>|   3. Client acknowledges server's SYN
  |         [ESTABLISHED]       |   Connection ready for data
```

**Why 3 steps?**
- Both sides must agree on initial sequence numbers (ISN) for ordered delivery
- Server must confirm it can receive from client
- Client must confirm it can receive from server

**Sequence Numbers:**
- Random ISN prevents old duplicate packets from being accepted as new
- Enables reassembly of out-of-order packets

**Timing:**
- Typical RTT: 1-100ms depending on network
- HTTPS adds TLS handshake (~1-2 more RTTs with TLS 1.2, ~1 RTT with TLS 1.3)

***

## 2. What is the difference between a VLAN and a VPC?

**Answer:**

| Feature | VLAN | VPC |
|---------|------|-----|
| **Layer** | Layer 2 (Data Link) | Layer 3 (Network) + software-defined |
| **Scope** | Single physical switch/datacenter | Cloud provider's entire infrastructure |
| **Isolation** | Broadcast domain | Logical isolation with IP ranges, subnets, routing |
| **Components** | Ports, tags (802.1Q) | Subnets, route tables, gateways, security groups |
| **Management** | Switch CLI/GUI | Cloud console, API, Terraform |

**VLAN (Virtual Local Area Network):**
- Segments a physical switch into multiple isolated Layer 2 domains
- Uses 802.1Q tagging (4-byte VLAN tag in Ethernet frame)
- 4094 usable VLANs (12-bit VLAN ID)
- Inter-VLAN routing requires Layer 3 device

**VPC (Virtual Private Cloud):**
- Logically isolated network in cloud (AWS, GCP, Azure)
- You define CIDR block, subnets, route tables, gateways
- Includes security groups (stateful firewall) and NACLs (stateless)
- Supports peering, transit gateways, private links

**Analogy:** VLAN is like dividing a building into floors; VPC is like having your own private building in a shared complex.

***

## 3. How does BGP work and where is it used in DevOps?

**Answer:**

**BGP (Border Gateway Protocol)** is the routing protocol that holds the Internet together.

**How BGP Works:**
1. Routers (peers) establish TCP connections (port 179)
2. Exchange routing information (which prefixes they can reach)
3. Apply policies (prefer certain paths, reject others)
4. Select best path based on attributes (AS_PATH, LOCAL_PREF, MED)
5. Advertise selected routes to peers

**BGP Attributes (decision order):**
1. Weight (Cisco-specific, local)
2. LOCAL_PREF (higher = better)
3. Locally originated routes
4. AS_PATH (shorter = better)
5. ORIGIN (IGP < EGP < Incomplete)
6. MED (lower = better)
7. eBGP over iBGP
8. Lowest IGP metric to next-hop

**DevOps Use Cases:**

| Scenario | How BGP is Used |
|----------|-----------------|
| **AWS Direct Connect** | On-prem router peers with AWS VGW via eBGP |
| **Azure ExpressRoute** | BGP peering with Microsoft edge routers |
| **GCP Cloud Interconnect** | BGP over dedicated/partner interconnect |
| **Kubernetes (Calico/Cilium)** | Nodes advertise pod CIDR to physical routers |
| **Multi-cloud failover** | Advertise same prefix from multiple clouds; manipulate AS_PATH for failover |

**Why BGP in Kubernetes?**
- No overlay encapsulation overhead (vs VXLAN)
- Physical network routes directly to pods
- Better performance for bare-metal deployments

***

## 4. What happens when you type `curl https://example.com`?

**Answer:**

This is a classic "full-stack" networking question. Here's the complete flow:

```
1. DNS Resolution
   └─> Check local cache → OS cache → /etc/resolv.conf
   └─> Query recursive resolver (8.8.8.8)
   └─> Root → TLD (.com) → Authoritative NS
   └─> Returns: example.com → 93.184.216.34

2. TCP Connection (3-way handshake)
   └─> SYN → 93.184.216.34:443
   └─> SYN-ACK ←
   └─> ACK →
   └─> Connection ESTABLISHED

3. TLS Handshake (TLS 1.2)
   └─> ClientHello (supported ciphers, TLS version)
   └─> ServerHello + Certificate + ServerKeyExchange
   └─> ClientKeyExchange (pre-master secret)
   └─> ChangeCipherSpec + Finished (both sides)
   └─> Encrypted tunnel ready

4. HTTP Request
   └─> GET / HTTP/1.1
   └─> Host: example.com
   └─> User-Agent: curl/7.x.x
   └─> Accept: */*

5. HTTP Response
   └─> HTTP/1.1 200 OK
   └─> Content-Type: text/html
   └─> [HTML body]

6. Connection Teardown
   └─> FIN/ACK exchange (or kept alive for reuse)
```

**Timing Breakdown:**
- DNS: 10-100ms (cached: <1ms)
- TCP handshake: 1 RTT
- TLS 1.2: 2 RTTs
- TLS 1.3: 1 RTT
- HTTP request/response: 1+ RTT

***

## 5. Explain network namespaces in Linux and how Kubernetes uses them.

**Answer:**

**Network Namespace** is a Linux kernel feature that provides isolated network stacks.

**What's isolated in a namespace:**
- Network interfaces (eth0, lo, etc.)
- IP addresses and routing tables
- iptables rules
- Socket bindings (port 80 in one namespace ≠ port 80 in another)
- ARP cache
- /proc/net contents

**Kubernetes Usage:**

```
┌─────────────────────────────────────────┐
│  Node (Host)                            │
│  ┌─────────────────────────────────┐    │
│  │  Pod Network Namespace          │    │
│  │  ┌─────────┐  ┌─────────┐       │    │
│  │  │Container│  │Container│       │    │
│  │  │   A     │  │   B     │       │    │
│  │  │  eth0   │  │  eth0   │       │    │
│  │  │ 10.0.0.5│  │10.0.0.5 │       │    │
│  │  └────┬────┘  └────┬────┘       │    │
│  │       │           │             │    │
│  │       └─────┬─────┘             │    │
│  │             │ veth pair         │    │
│  └─────────────┼───────────────────┘    │
│                │                        │
│          [CNI Bridge / Routing]         │
└─────────────────────────────────────────┘
```

**How Pod networking works:**
1. kubelet calls CNI plugin when Pod is scheduled
2. CNI creates network namespace for the Pod
3. CNI creates veth pair (virtual ethernet cable)
4. One end (`eth0`) placed in Pod namespace
5. Other end attached to bridge/routed on host
6. Pod IP assigned, routes configured

**Key Point:** All containers in a Pod share the same network namespace — they communicate via `localhost`.

***

## 6. What is MTU and what is MTU mismatch?

**Answer:**

**MTU (Maximum Transmission Unit)** is the largest packet size a network link can carry without fragmentation.

**Standard Values:**
| Network Type | MTU |
|--------------|-----|
| Ethernet | 1500 bytes |
| Jumbo frames | 9000 bytes |
| PPPoE | 1492 bytes |
| VXLAN (inner) | 1450 bytes (1500 - 50 byte overhead) |

**MTU Mismatch Problem:**

```
Host A (MTU 1500) ──── Router (MTU 1400) ──── Host B (MTU 1500)
```

If Host A sends 1500-byte packets:
- Router must fragment (if DF bit not set)
- Router drops + sends "Fragmentation Needed" ICMP (if DF bit set)
- Result: Connection hangs or severe performance degradation

**Symptoms:**
- Small packets work (ping, SSH commands)
- Large transfers fail or stall
- HTTPS handshakes complete but data doesn't flow

**Diagnosis:**
```bash
# Find path MTU
tracepath destination.com

# Test with DF bit set
ping -M do -s 1472 destination.com  # Should work
ping -M do -s 1473 destination.com  # May fail if MTU < 1500
```

**Solutions:**
- Reduce interface MTU on sending host
- Enable TCP MSS clamping on routers/firewalls
- Fix underlay MTU in overlay networks (VXLAN, VPNs)

***

## 7. How does iptables work and how is it used in Kubernetes?

**Answer:**

**iptables** is a Linux firewall and packet manipulation framework using tables and chains.

**Tables:**
| Table | Purpose | Chains |
|-------|---------|--------|
| filter | Packet filtering | INPUT, FORWARD, OUTPUT |
| nat | Address translation | PREROUTING, INPUT, OUTPUT, POSTROUTING |
| mangle | Packet modification | All 5 chains |
| raw | Bypass conntrack | PREROUTING, OUTPUT |

**Chain Flow:**
```
Incoming Packet → PREROUTING → [Routing Decision]
                                      ├─→ INPUT → Local Process
                                      └─→ FORWARD → POSTROUTING → Out

Outgoing Packet → OUTPUT → POSTROUTING → Out
```

**Kubernetes Usage (kube-proxy):**

kube-proxy uses iptables to implement Service load balancing:

```bash
# Simplified example: Service "web" with 2 endpoints
iptables -t nat -A PREROUTING -d 10.96.100.1 -p tcp --dport 80 \
  -j KUBE-SVC-WEB

iptables -t nat -A KUBE-SVC-WEB \
  -m statistic --mode random --probability 0.5 \
  -j KUBE-SEP-1

iptables -t nat -A KUBE-SVC-WEB \
  -j KUBE-SEP-2

iptables -t nat -A KUBE-SEP-1 \
  -j DNAT --to-destination 10.244.1.5:8080

iptables -t nat -A KUBE-SEP-2 \
  -j DNAT --to-destination 10.244.2.10:8080
```

**How it works:**
1. Packet destined for Service ClusterIP arrives
2. PREROUTING DNAT rule redirects to kube-proxy chain
3. Random/statistical rule selects backend Pod
4. Final DNAT rewrites destination to Pod IP
5. Routing delivers to Pod

**Problem:** O(n) rule traversal — a 10,000-service cluster traverses 10,000 rules per packet.

**Solution:** CNI plugins like Cilium replace iptables with eBPF (O(1) hash map lookup).

***

## 8. What is service discovery and how does Kubernetes implement it?

**Answer:**

**Service Discovery** is the mechanism by which services find each other without hardcoded IPs.

**The Problem:**
- Pods are ephemeral (IPs change on restart)
- Scaling creates multiple instances
- Hardcoding IPs is impossible

**Kubernetes Solutions:**

### 1. DNS (CoreDNS)

```
# Service resolution format
<service>.<namespace>.svc.cluster.local

# Examples
web.default.svc.cluster.local      # Same namespace
web.production.svc.cluster.local   # Different namespace
```

**How it works:**
1. CoreDNS watches Kubernetes API for Services
2. Creates A records: `web.default → 10.96.100.1` (ClusterIP)
3. Pods configured to use CoreDNS via /etc/resolv.conf
4. Application does DNS lookup → gets ClusterIP

**Common Issue: ndots:5**
```bash
# Default /etc/resolv.conf in pods
options ndots:5
```
For `google.com` (0 dots), resolver tries:
1. `google.com.default.svc.cluster.local`
2. `google.com.svc.cluster.local`
3. `google.com.cluster.local`
4. `google.com.<search-domain>`
5. `google.com` (finally!)

**Fix:** Append dot for FQDN (`google.com.`) or reduce ndots.

### 2. Environment Variables

Kubernetes injects env vars into every Pod:
```bash
WEB_SERVICE_HOST=10.96.100.1
WEB_SERVICE_PORT=80
WEB_PORT=tcp://10.96.100.1:80
WEB_PORT_80_TCP=tcp://10.96.100.1:80
WEB_PORT_80_TCP_ADDR=10.96.100.1
WEB_PORT_80_TCP_PORT=80
WEB_PORT_80_TCP_PROTO=tcp
```

**Limitation:** Only works for Services created before the Pod.

### 3. Headless Services

For direct Pod IPs (no ClusterIP):
```yaml
apiVersion: v1
kind: Service
metadata:
  name: web
spec:
  clusterIP: None  # Headless
  selector:
    app: web
```

DNS returns all Pod IPs (A records with multiple values).

***

## 9. What is a NetworkPolicy in Kubernetes?

**Answer:**

A **NetworkPolicy** is a namespaced Kubernetes resource that defines firewall rules for Pod traffic.

**Default Behavior:**
- No NetworkPolicy → All ingress/egress allowed
- Any NetworkPolicy applied → Default deny, only allowed traffic permitted

**Example: Deny All Ingress**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all
spec:
  podSelector: {}  # All pods in namespace
  policyTypes:
  - Ingress
  # No ingress rules = deny all
```

**Example: Allow Specific Ingress**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-nginx
spec:
  podSelector:
    matchLabels:
      app: api
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: nginx
    ports:
    - protocol: TCP
      port: 8080
```

**Selectors:**
| Selector | Matches |
|----------|---------|
| `podSelector: {}` | All pods in namespace |
| `podSelector: {app: web}` | Pods with label `app=web` |
| `namespaceSelector: {name: prod}` | All pods in `prod` namespace |
| `ipBlock: {cidr: 10.0.0.0/8}` | IPs in CIDR range |

**Important:** NetworkPolicy is only enforced if CNI supports it (Calico, Cilium, Weave).

***

## 10. What is a service mesh and why is it used?

**Answer:**

A **service mesh** is an infrastructure layer for handling service-to-service communication.

**The Problem:**
- 100+ microservices = complex communication patterns
- Each service needs: retries, timeouts, circuit breaking, mTLS, observability
- Implementing in every service = code duplication, multiple languages

**Service Mesh Solution:**
Deploy a **sidecar proxy** (Envoy, linkerd-proxy) alongside each service.

```
┌─────────────────────────────────────┐
│  Pod                                │
│  ┌─────────────┐  ┌──────────────┐  │
│  │  Application│  │   Sidecar    │  │
│  │   Container │  │    Proxy     │  │
│  │             │  │  (Envoy)     │  │
│  └──────┬──────┘  └──────┬───────┘  │
│         │                │          │
│         └──────┬─────────┘          │
│                │ iptables REDIRECT  │
└─────────────────────────────────────┘
```

**What the Mesh Provides:**

| Feature | Benefit |
|---------|---------|
| **mTLS** | Automatic encryption + identity (no passwords) |
| **Traffic Management** | Retries, timeouts, canary deployments, A/B testing |
| **Observability** | Per-request metrics, traces, service dependency maps |
| **Policy Enforcement** | Rate limiting, access control |
| **Resilience** | Circuit breaking, outlier detection |

**Popular Meshes:**
| Mesh | Proxy | Language | Resource Usage |
|------|-------|----------|----------------|
| Istio | Envoy | Go + C++ | High |
| Linkerd | linkerd-proxy | Rust | Low |
| Consul Connect | Envoy | Go | Medium |

**When to Use:**
- 20+ microservices
- Need consistent cross-cutting concerns
- Multi-language environments
- Zero-trust security requirements

**When NOT to Use:**
- Single-digit services
- Resource-constrained clusters
- Simple applications

***

## Quick Reference: TCP States

| State | Meaning |
|-------|---------|
| LISTEN | Waiting for incoming connections |
| SYN_SENT | Sent SYN, waiting for SYN-ACK |
| SYN_RECEIVED | Received SYN, sent SYN-ACK |
| ESTABLISHED | Normal data transfer |
| FIN_WAIT_1 | Sent FIN, waiting for ACK |
| FIN_WAIT_2 | Received ACK, waiting for FIN |
| CLOSE_WAIT | Remote closed, waiting for local close |
| TIME_WAIT | Local closed, waiting to ensure remote got ACK |
| CLOSED | Connection terminated |

**Common Issues:**
- **CLOSE_WAIT pileup:** Application not calling `close()` — bug
- **TIME_WAIT exhaustion:** High-traffic servers — tune `tcp_tw_reuse`

***

## Troubleshooting Commands

```bash
# Check listening ports
ss -tlnp | grep :8080

# Find established connections
ss -tn | grep ESTAB

# Check for CLOSE_WAIT
ss -tn | grep CLOSE_WAIT

# Packet capture
tcpdump -i eth0 port 8080 -w capture.pcap

# Trace route with packet loss
mtr -rw destination.com

# DNS from inside pod
kubectl exec <pod> -- nslookup <service>

# Test connectivity from pod
kubectl exec <pod> -- curl -v http://<service>:<port>
```
