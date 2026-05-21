# Advanced Networking and Performance

```
Advanced Networking and Performance
├── eBPF / XDP
│   ├── XDP — eBPF at NIC driver, bypasses kernel stack entirely
│   ├── BPF maps — O(1) hash lookups for routing, conntrack, policy
│   ├── Hooks — XDP, TC, Netfilter, Socket, kprobes
│   └── DPDK — userspace NIC access, zero system calls (telco/HFT)
├── Cilium
│   ├── Replaces kube-proxy iptables with eBPF (80% CPU reduction)
│   ├── Identity-based NetworkPolicy (label, not IP)
│   ├── Hubble — per-flow observability without tcpdump overhead
│   └── Transparent encryption — WireGuard or IPsec for pod-to-pod
├── HTTP/3 and QUIC
│   ├── UDP-based — avoids TCP HOL blocking at transport layer
│   ├── 0-RTT — send data in first packet on repeat connections
│   ├── Connection migration — survives IP change (mobile handoff)
│   └── TLS 1.3 built-in — no separate handshake
├── HTTP/2
│   ├── Multiplexing — many streams over one TCP connection
│   ├── HPACK — static table + dynamic table + Huffman compression
│   ├── Server push — proactively send assets before request
│   └── TCP HOL still exists — one dropped packet stalls all streams
├── gRPC
│   ├── Binary Protobuf framing over HTTP/2
│   ├── Bidirectional streaming, long-lived connections
│   ├── L4 LB pins all calls to one pod — requires headless or L7 proxy
│   └── MaxConnectionAge — forces reconnect for rebalancing
├── BGP in Cloud / Hybrid
│   ├── Direct Connect / ExpressRoute / Cloud Interconnect
│   ├── Path selection — LOCAL_PREF → AS_PATH → MED
│   ├── RPKI — cryptographic route origin validation
│   └── K8s BGP mode (Calico/Cilium) — pods routable without overlay
├── VXLAN
│   ├── L2 over UDP (port 4789), 50-byte header overhead
│   ├── VNI — 24-bit segment ID, 16M segments
│   ├── VTEP — encap/decap point (node or ToR switch)
│   └── BGP EVPN — distributed VTEP learning, no flooding
├── Kernel Tuning (sysctl)
│   ├── net.core.somaxconn — listen queue depth
│   ├── net.ipv4.tcp_tw_reuse — reuse TIME_WAIT sockets
│   ├── net.ipv4.tcp_congestion_control=bbr — BBR vs CUBIC
│   └── net.ipv4.ip_local_port_range — ephemeral port range
├── TCP Congestion Control
│   ├── CUBIC — loss-based, backs off on every drop
│   ├── BBR — model-based, estimates bandwidth and RTT
│   ├── BBR advantage — long-fat-pipe and lossy links
│   └── BBR unfairness — can crowd out CUBIC flows on shared links
├── Advanced Traffic Engineering
│   ├── Anycast — same IP, BGP-routed to nearest instance
│   ├── DSR (Direct Server Return) — backend replies bypass LB
│   ├── Tail latency — P99 > P50, bufferbloat, BBR smooths queue
│   └── MTU/MSS clamping — VPN/VXLAN require MSS ≤ 1410
└── CNI Comparison
    ├── Flannel — simple VXLAN overlay, no NetworkPolicy
    ├── Calico — BGP mode or VXLAN, full NetworkPolicy
    ├── Cilium — eBPF, identity-based policy, Hubble observability
    └── Weave — VXLAN + encryption, moderate resource use
```

## First Principles

- The Linux kernel's network stack runs in interrupt context — every packet traversal through iptables chains burns CPU. **eBPF** moves packet processing into small in-kernel programs that execute at the data path, eliminating context switches between userspace and kernel for every packet.
- TCP was designed when the internet was wired and reliable — **QUIC/HTTP/3** replaces TCP with a UDP-based protocol because UDP does not serialize streams. One dropped packet in HTTP/2 blocks all multiplexed streams on the same TCP connection; QUIC limits the stall to the affected stream only.
- HTTP headers are redundant across requests — every `Content-Type: application/json` sent repeatedly is wasted bandwidth. **HPACK** uses a shared static/dynamic table so common headers are sent as index numbers (1-2 bytes) instead of full strings.
- gRPC's long-lived HTTP/2 connections are pinned to one backend by an L4 load balancer — all RPCs go to one pod. This is not a gRPC bug; it is a **load balancer layer mismatch**. L7 load balancers understand HTTP/2 streams and can distribute per-RPC.
- BGP selects paths based on policy, not just distance — an operator can force all traffic through a specific datacenter by setting **LOCAL_PREF** higher on that path. This is the mechanism behind traffic engineering in hybrid cloud and multi-cloud setups.
- Default kernel TCP settings (128-connection listen queue, 28,000 ephemeral ports) were sized for 1990s server loads. Modern high-throughput services require explicit **sysctl tuning** — these are not optimizations, they are correctness fixes for modern workloads.

### 🔷 Advanced Networking & Performance (6-10 YOE)

#### 1. eBPF (Extended Berkeley Packet Filter) & XDP
At 6+ YOE, you should understand how networking is moving from the kernel stack to **eBPF**.
- **XDP (eXpress Data Path):** Runs eBPF programs at the earliest point in the NIC driver. It bypasses the entire kernel network stack for high-performance packet processing (DDoS protection, load balancing).
- **Cilium:** The leading K8s CNI that uses eBPF to replace `kube-proxy` (iptables), reducing CPU overhead by up to 80% at scale.

#### 2. HTTP/3 and QUIC (Quick UDP Internet Connections)
- **Zero Round-Trip Time (0-RTT):** QUIC allows clients to send data immediately in the first packet if they have previously connected to the server.
- **Solving Head-of-Line Blocking:** Unlike HTTP/2 (where one lost packet stalls the entire TCP connection), QUIC (UDP-based) allows other streams to continue even if one stream loses a packet.

#### 3. Kernel Performance Tuning (`sysctl`)
For high-traffic servers, default kernel settings are bottlenecks.
- `net.core.somaxconn`: The listen queue limit for incoming connections. Increase to `4096` or higher for high-load apps.
- `net.ipv4.tcp_tw_reuse`: Allows reusing sockets in `TIME_WAIT` state for new connections. Crucial for avoiding socket exhaustion.
- `net.ipv4.tcp_congestion_control=bbr`: Google's BBR algorithm. Significantly improves throughput on long-haul or lossy links compared to CUBIC.

#### 4. Advanced Traffic Engineering
- **Anycast IP:** Assigning the same IP to multiple servers worldwide. Routers automatically send traffic to the "closest" instance (BGP-based). Used by Cloudflare and AWS Global Accelerator.
- **DSR (Direct Server Return):** A load balancing technique where the LB only handles incoming packets; the backend server responds directly to the client, bypassing the LB and doubling throughput.

***

#### 💡 Senior Interview Strategy: "The packet's journey"
When asked about network latency, discuss:
1. **Serialization Latency:** Time to push bits onto the wire.
2. **Propagation Latency:** Speed of light in fiber (~200,000 km/s).
3. **Queuing Latency:** Packets waiting in router buffers (Bufferbloat).
4. **Handling Latency:** OS context switches and application processing.

***

**Continue your preparation with these specialized deep-dives:**
1. `[HARD]` [Advanced Protocols & Forensics](../interview.md)
2. `[SCENARIO]` [High-Scale Troubleshooting Drills](../scenarios.md)
# Advanced Networking & Enterprise Protocols

## Global Traffic Engineering & Routing

### BGP (Border Gateway Protocol) in the Cloud

BGP is the "glue" of the internet. In cloud environments, it's used for **Hybrid Connectivity**.

**Use Case:** Connecting your On-Premise Data Center to AWS (Direct Connect) or Azure (ExpressRoute).

**ASN (Autonomous System Number):** You must manage private ASNs to ensure your internal routes don't conflict with the public internet.

**Dynamic Routing:** Unlike static routes, BGP allows for automatic failover. If one Direct Connect link fails, BGP automatically re-advertises the routes through the backup link.

**BGP Path Selection (decision process in order):**
1. Highest **Weight** (Cisco proprietary, local to router)
2. Highest **LOCAL_PREF** (prefer routes within AS) — default 100
3. Locally originated routes preferred
4. Shortest **AS_PATH** (fewer ASes = preferred)
5. Lowest **ORIGIN** (IGP < EGP < Incomplete)
6. Lowest **MED** (Multi-Exit Discriminator — hint to neighboring AS)
7. **eBGP over iBGP**
8. Lowest IGP metric to BGP next-hop
9. Lowest BGP router ID (tiebreaker)

**Cloud Hybrid Connectivity:**
- **AWS Direct Connect:** On-prem router peers with AWS VGW via eBGP over a dedicated physical line
- **Azure ExpressRoute:** Same pattern — private BGP peering to Microsoft edge routers
- **GCP Cloud Interconnect:** BGP session over dedicated or partner interconnect

**RPKI (Resource Public Key Infrastructure):** Cryptographically validates that an AS is authorized to originate specific prefixes. Prevents BGP hijacking.

**BGP in Kubernetes (Calico/Cilium BGP mode):** Each node peers with physical routers and announces its pod CIDR. External clients reach pods directly via the physical network's routing tables — no overlay encapsulation needed.

### Anycast Networking

**What it is:** Multiple servers across the globe share the *same* IP address. The network (BGP) routes the user to the "closest" server.

**DevOps Context:** Used by CDNs (CloudFront, Cloudflare) and Global Load Balancers (Azure Front Door). Provides single-IP global reachability and massive DDoS protection.

***

## Deep Dive: Modern Protocols

### gRPC (Google Remote Procedure Call)

The standard for internal microservice communication.

**Binary Framing:** Unlike REST (text-based JSON), gRPC uses Protocol Buffers (Protobuf), which is binary. This results in significantly smaller payloads and faster serialization.

**Multiplexing:** gRPC runs over HTTP/2. It allows many requests to be sent over a single TCP connection simultaneously, eliminating the "Head-of-Line Blocking" problem of HTTP/1.1.

**Bidirectional Streaming:** Client and server can stream in both directions simultaneously.

**SRE Tip:** Standard Load Balancers often fail at balancing gRPC because they balance *connections*, not *requests*. Since gRPC maintains long-lived connections, backends can become unbalanced. Requires a "gRPC-aware" proxy (like Envoy or Nginx with specific settings).

### HTTP/3 (QUIC)

The future of the web.

**The Protocol:** HTTP/3 moves away from TCP and uses **UDP** for the transport layer.

**Why?** TCP handshakes are slow. QUIC integrates the cryptographic handshake (TLS 1.3) into the transport handshake, reducing wait time for the user.

**Resilience:** If a user switches from Wi-Fi to 4G, a TCP connection breaks and must be re-established. QUIC uses a "Connection ID," allowing the session to stay alive even if the IP address changes.

**0-RTT (early data):** Client can send application data on the first flight. The server can process it without waiting for the full handshake. Risk: early data is not protected against replay attacks — must only be used for idempotent requests.

### HTTP/2

Binary framing over a single TCP connection.

- **Multiplexing:** Multiple independent streams over one connection — eliminates HTTP-level HOL blocking
- **Header compression (HPACK):** Eliminates redundant headers across requests
- **Server Push:** Server proactively sends resources the client hasn't requested
- **Stream prioritization:** Weight-based prioritization
- **Limitation:** TCP-level HOL blocking remains — one lost packet stalls all streams in the connection

***

## Network Performance & Latency Optimization

### The "Tail Latency" Problem (P99)

In networking, the "average" latency (P50) is irrelevant. High-scale systems are judged by their **P99 latency** (the latency experienced by the slowest 1% of users).

**Causes:** Packet loss, TCP retransmissions, or "Bufferbloat" (where network equipment buffers too many packets, causing spikes).

**SRE Fix:** Tuning the **TCP Congestion Control** algorithm. Moving from standard `Cubic` to Google's `BBR` (Bottleneck Bandwidth and RTT) can significantly improve throughput on lossy networks.

### MTU (Maximum Transmission Unit) & MSS

**The VPN Trap:** Standard MTU is 1500. When you add VPN headers (IPsec), the usable space drops. If your server still sends 1500-byte packets, they will be fragmented by the network, causing a 50% performance drop.

**Senior Solution:** Clamp the **MSS (Maximum Segment Size)** at the firewall or router to ensure packets fit inside the tunnel without fragmentation.

### TCP Congestion Control Algorithms

| Algorithm | Description | Use Case |
|-----------|-------------|----------|
| **Cubic** | Default in Linux, Windows | General purpose, high bandwidth |
| **BBR** | Google's model-based algorithm | Lossy networks, high latency links |
| **Reno** | Classic TCP congestion control | Legacy systems |
| **Vegas** | RTT-based, proactive | Low latency networks |

***

## Network Forensics & Security

### Deep Packet Inspection (DPI)

When a system is under attack or experiencing "ghost" errors, simple logs aren't enough.

**C2 Traffic Analysis:** Identifying "Command and Control" traffic (malware heartbeats) by analyzing the timing and size of small, encrypted packets leaving the network.

**Encrypted Client Hello (ECH):** A new standard to prevent ISP/Firewall eavesdropping by encrypting the hostname (SNI) during the TLS handshake.

### TLS Handshake Analysis

```bash
# Inspect TLS certificate
openssl s_client -connect example.com:443 -servername example.com

# Check cert expiry
openssl s_client -connect example.com:443 </dev/null 2>/dev/null \
  | openssl x509 -noout -dates

# Show full certificate chain
openssl s_client -connect example.com:443 -showcerts

# Test specific TLS version
openssl s_client -connect example.com:443 -tls1_3
```

***

## Software Defined Networking (SDN) & Overlays

### VXLAN (Virtual Extensible LAN)

How Kubernetes creates a "flat" network where Pod A on Node 1 can talk to Pod B on Node 5.

**VXLAN encapsulates Layer 2 Ethernet frames inside UDP (port 4789).** Each VXLAN segment is identified by a 24-bit VNI (VXLAN Network Identifier) — up to 16 million segments vs. 4094 for VLANs.

**VXLAN packet structure:**
```
[Outer Ethernet | Outer IP | Outer UDP (4789) | VXLAN Header (8 bytes) | Inner Ethernet | Inner IP | Payload]
```

**VTEP (VXLAN Tunnel Endpoint):** The entity (typically a Linux kernel interface or hardware NIC) that encapsulates/decapsulates VXLAN traffic. In Kubernetes, each node has a VTEP.

**Overhead:** 50 bytes (14 Ethernet + 20 IP + 8 UDP + 8 VXLAN). On a 1500-byte MTU link, inner MTU must be set to 1450 bytes.

### The CNI (Container Network Interface)

Why choosing the right CNI (Calico for BGP-based routing vs. Flannel for simple VXLAN) is a massive architectural decision.

| Plugin | Approach | Encryption | NetworkPolicy | Use Case |
|--------|----------|------------|---------------|----------|
| Flannel | VXLAN overlay (default) | No | No (needs separate) | Simple, small clusters |
| Calico | BGP routing or VXLAN | Yes (WireGuard) | Yes (native) | Production, BGP integration |
| Cilium | eBPF — no iptables | Yes (WireGuard) | Yes (L7 aware) | Performance, observability |
| Weave | VXLAN + mesh encryption | Yes | Yes | Simplicity + encryption |
| Canal | Flannel + Calico policy | No | Yes | Flannel's simplicity + policies |

### Geneve

Geneve (Generic Network Virtualization Encapsulation) is the successor to VXLAN and STT. Variable-length header allows arbitrary metadata. Used by OVN, OpenStack, and VMware NSX-T. Transport: UDP port 6081.

***

## eBPF Networking

### A. What is eBPF?
eBPF (Extended Berkeley Packet Filter) is a revolutionary kernel technology that allows developers to run sandboxed programs directly inside the Linux kernel space without modifying the kernel source code or loading dynamic kernel modules.

```
                  eBPF Kernel Architecture
  ┌─────────────────────────────────────────────────────────┐
  │                       Linux Kernel                      │
  │                                                         │
  │  Kernel Hook Points (XDP, TC, Socket, kprobes)          │
  │        │                                                │
  │        ▼ eBPF Bytecode                                  │
  │  ┌───────────┐    Safety Pass    ┌───────────────────┐  │
  │  │ Verifier  │──────────────────►│ JIT Compiler      │  │
  │  └───────────┘                   │ (JIT to x86/ARM)  │  │
  │                                  └─────────┬─────────┘  │
  │                                            │            │
  │                                  ┌─────────▼─────────┐  │
  │                                  │ Native Machine    │  │
  │                                  │ Code Execution    │  │
  │                                  └─────────┬─────────┘  │
  │                                            │            │
  │  ┌───────────┐ Read / Write State ┌────────▼─────────┐  │
  │  │ BPF Maps  │◄──────────────────►│ Helper Functions │  │
  │  └─────▲─────┘                    └──────────────────┘  │
  └────────┼────────────────────────────────────────────────┘
           │
           ▼ User / Kernel Interprocess Communication (IPC)
  ┌─────────────────────────────────────────────────────────┐
  │                    Userspace Daemon                     │
  │             (e.g., Cilium Agent / Hubble)               │
  └─────────────────────────────────────────────────────────┘
```

1. **Bytecode Verification**: The kernel verifier ensures the program is safe to run. It guarantees the program does not dereference invalid memory, contains no infinite loops (via loop termination limits), cannot crash the kernel, and executes within a restricted instruction limit.
2. **JIT Compilation**: Once verified, the eBPF bytecode is JIT (Just-In-Time) compiled into native CPU assembly instructions (x86_64, ARM64) to run at bare-metal speed.
3. **Painless Upgrades**: eBPF programs can be dynamically loaded and unloaded from active kernel hooks on-the-fly without system reboots or service disruption.

---

### B. eBPF Networking Hooks & Program Types

eBPF programs hook into specific trigger points along the Linux kernel network datapath.

```
       Packet Journey & eBPF Hook Stages
       ┌───────────────────────────────┐
       │     Physical Network Card     │
       └───────────────┬───────────────┘
                       │ [Raw Packet Stream]
       ┌───────────────▼───────────────┐
       │     XDP (eXpress Data Path)   │  <-- Hooked at network driver level. Bypasses socket buffers.
       └───────────────┬───────────────┘
                       │ [Allocate sk_buff]
       ┌───────────────▼───────────────┐
       │      TC (Traffic Control)     │  <-- Ingress hook. Performs L3/L4 filters.
       └───────────────┬───────────────┘
                       │ [TCP/IP Stack Traversal]
       ┌───────────────▼───────────────┐
       │      Socket Layer (sockops)   │  <-- Intercepts system calls. Bypasses TCP loopback!
       └───────────────┬───────────────┘
                       │ [Delivered to App]
       ┌───────────────▼───────────────┐
       │       Application Space       │
       └───────────────────────────────┘
```

#### 1. XDP (eXpress Data Path)
XDP attaches an eBPF program directly at the network interface card (NIC) driver layer, *before* NGINX or Linux allocates socket buffers (`sk_buff`) or performs costly memory allocations.
- **Actions**: `XDP_DROP` (DDoS mitigation), `XDP_TX` (packet bounce-back for load balancing), `XDP_REDIRECT` (bypass kernel to send straight to another interface/CPU).
- **Advantage**: Handles millions of requests/second per CPU core without incurring context-switching overhead.

#### 2. TC (Traffic Control)
Attaches to the network queueing system (ingress/egress).
- **Advantage**: Accesses parsed packet structures (`sk_buff`), allowing modification of L3/L4 headers, connection tracking metadata, and traffic policing.

#### 3. Socket Programs (`sockops` & `sockmap`)
Attaches directly to socket lifecycle events (connect, send, active state).
- **Socket Redirection (TCP Loopback Bypass)**: In standard Kubernetes architectures, pod-to-pod or pod-to-sidecar (Envoy) traffic traverses the full TCP/IP loopback network stack (parsing TCP state machine, checksum calculations, IP routes). eBPF utilizes `sockmap` to map socket file descriptors directly. When Pod A sends data to its sidecar, eBPF intercepts the socket write and injects it directly into the sidecar's read queue, bypassing the entire TCP/IP layer and achieving a ~4x reduction in local loopback latency!

---

### C. The Power of eBPF Maps
eBPF programs are stateless by default. **BPF Maps** are key-value data structures in the kernel that allow eBPF programs to maintain state and share data with userspace processes (like the Cilium Agent).

* **Hash Maps (`BPF_MAP_TYPE_HASH`)**: Fast $O(1)$ lookups for large connection tracking (`conntrack`) tables.
* **Arrays (`BPF_MAP_TYPE_ARRAY`)**: Indexed storage for static routing paths and network policies.
* **Ring Buffers (`BPF_MAP_TYPE_RINGBUF`)**: Lockless, high-performance queues for streaming kernel event telemetry (e.g. connections closed, packet drop traces) to userspace.
* **Program Arrays (`BPF_MAP_TYPE_PROG_ARRAY`)**: Maps holding file descriptors to other eBPF programs, enabling modular execution chains ("Tail Calls").

---

### D. Cilium CNI: eBPF-Native Kubernetes Orchestration

Cilium completely replaces `kube-proxy` (which manages services via `iptables`) with an eBPF-native routing engine, solving massive scaling bottlenecks.

#### 1. O(1) Service Load Balancing vs. kube-proxy O(N)
* **The `kube-proxy` Bottleneck**: `kube-proxy` maintains rules using `iptables`. Every incoming connection must traverse these rules sequentially ($O(N)$). In a cluster with 5,000 services and 15,000 endpoints, a packet might traverse tens of thousands of iptables chains. This introduces significant CPU cycles, route delays, and packet drop risks.
* **The Cilium eBPF Solution**: Cilium loads a single eBPF program onto node interfaces and maintains a BPF map of Services and Endpoints. Incoming packets trigger an $O(1)$ constant-time lookup in the BPF map. Scalability remains perfectly flat, regardless of service count.

```
   Service Lookup Performance Scaling (Latency vs Services)
    Latency (ms)
     ▲
     │                                    / [kube-proxy (iptables) O(N)]
     │                                   /
     │                                  /
     │                                 /
     │                                /
     │───────────────────────────────/────────► [Cilium (eBPF) O(1) Constant]
     │
     └────────────────────────────────────────►
                                         Service Count
```

#### 2. Identity-Based Security Policies
- **Traditional CNI**: Enforces network policies using IP address tables. In dynamic Kubernetes environments, pods scale and IPs churn constantly, forcing nodes to continuously write and reconcile firewall rules.
- **Cilium CNI**: Cilium assigns an integer **workload identity** based on pod labels (e.g., identity `104` represents `app=frontend`). Cilium encapsulates this identity header inside the overlay packet (via VXLAN/Geneve or direct routing). Nodes evaluate inbound traffic strictly by comparing this security identity flag in BPF maps. Policy evaluations are completely decoupled from IP addresses.

#### 3. Hubble: Deep Cluster Observability
Hubble leverages the lockless eBPF Ring Buffer to stream real-time flow events without modifying container workloads or injecting heavy logging agents.
- **Layer 7 Inspection**: Attaches parser filters (HTTP methods, response codes, DNS queries, gRPC paths) directly at socket events.
- **Service Dependency Mapping**: Emits raw telemetry data to assemble visual dependency graphs and highlight connectivity failures.
- **Prometheus Metrics**: Exposes golden SRE signals (network latency percentiles, error counts, packet retransmission metrics) from the kernel.

---

### E. CNI Comparison: Architectural Deep-Dive

| Metric | Flannel CNI | Calico CNI (Standard) | Cilium CNI |
| :--- | :--- | :--- | :--- |
| **Data Path** | Linux Bridge / VXLAN | standard Linux IP Routing | **eBPF Kernel Datapath** |
| **Service Proxy** | `kube-proxy` (iptables) | `kube-proxy` (iptables) | **eBPF Maps (Bypasses kube-proxy)** |
| **Performance Scale** | Poor (Low throughput) | Medium (Degrades at high scale) | **Excellent ($O(1)$ constant latency)** |
| **NetworkPolicy** | No (Needs Canal) | Yes (via iptables rules) | **Yes (Identity-based, L3/L4/L7)** |
| **Observability** | None | Basic (IP packet counters) | **Deep Flow Telemetry (Hubble)** |
| **Sidecar Speed** | Standard Loopback path | Standard Loopback path | **Socket Loopback Bypass (sockmap)** |

***

### F. DPDK (Data Plane Development Kit) vs. eBPF

While eBPF runs inside the Linux kernel safely, DPDK is a **kernel-bypass framework** where userspace applications gain direct control of the network interface card (NIC).
- **How DPDK Works**: It uses poll-mode drivers (PMDs) to continuously poll the NIC, consuming 100% of a CPU core to completely eliminate interrupt-handling latency. It completely bypasses all OS buffers and kernel routing logic.
- **Comparison**:
  - **DPDK**: Extreme throughput (telecom networks, high-frequency trading), but requires rewriting applications to use DPDK libraries, loses all Linux diagnostic tools, and drains CPU resources.
  - **eBPF**: Safe, integrates seamlessly with standard Linux networking tools, preserves kernel network protection layers, and is highly recommended for DevOps and Kubernetes environments.


***

## Summary: Key Takeaways

| Concept | Key Point |
|---------|-----------|
| BGP | Inter-AS routing, hybrid cloud connectivity |
| gRPC | HTTP/2-based, binary framing, multiplexing |
| HTTP/3 | UDP-based (QUIC), 0-RTT, connection migration |
| Tail Latency | P99 matters more than P50 |
| MTU/MSS | VPN overhead requires MSS clamping |
| VXLAN | L2 overlay, 50-byte overhead, 16M segments |
| eBPF | In-kernel programs, O(1) lookups, identity-based policy |
| CNI Choice | Calico for BGP, Cilium for eBPF, Flannel for simplicity |

***

## System Design Perspective

**Scalability**
- eBPF BPF maps scale to millions of entries with O(1) lookup cost. iptables scales linearly — doubling service count doubles per-packet processing time. For clusters above 500 services, eBPF-based networking is not a performance optimization but a scalability requirement.
- QUIC connection migration allows a mobile client to switch from WiFi to LTE without a new handshake. For long-lived gRPC streams (e.g., watch API calls in Kubernetes), this prevents stream interruption during network transitions. HTTP/2 over TCP would require a full TLS+TCP reconnect.
- BBR's bandwidth estimation allows it to fill long-fat-network pipes that CUBIC under-utilizes due to premature backoff on shallow packet loss. For cross-region data pipelines (AWS us-east-1 to ap-southeast-1), enabling BBR can increase throughput 3-10x without any application changes.

**Failure Modes**
- VXLAN MTU misconfiguration (inner MTU not reduced from 1500 to 1450) is a silent failure: SSH connects because control-plane packets are small, but `kubectl cp` or large config maps stall indefinitely because 1500-byte payloads exceed the path MTU after VXLAN encapsulation.
- BBR on a shared bottleneck link can be unfair to CUBIC flows: BBR probes at full bandwidth, causing CUBIC connections to back off further. In environments with mixed kernel versions (some nodes running BBR, others CUBIC), one workload can starve another. Standardize congestion control per cluster.
- eBPF program verification failures are silent at runtime — if a BPF program fails the kernel verifier, Cilium falls back to iptables mode. This fallback is logged but not alarmed by default, meaning a failed Cilium upgrade may silently revert to O(n) iptables without operators noticing.

**Trade-offs**
- Cilium eBPF vs Calico BGP: Cilium provides identity-based policy (no IP dependency), Hubble observability, and O(1) forwarding. Calico BGP provides native routing without encapsulation and is simpler to integrate with existing router infrastructure. The trade-off is observability depth vs operational simplicity.
- VXLAN overlay vs BGP underlay: VXLAN adds 50 bytes overhead and requires decapsulation CPU on each node. BGP underlay eliminates overhead but requires ToR switch BGP peering — possible in bare-metal, impractical in most cloud environments. Cloud networking forces overlay; bare metal should evaluate BGP mode.
- gRPC MaxConnectionAge vs connection stability: forcing reconnects (e.g., every 30 minutes) allows the L7 proxy or headless service DNS to rebalance traffic after pod scaling events. Without it, long-lived connections accumulate on pods that were up longest. The trade-off is connection churn vs load imbalance.
