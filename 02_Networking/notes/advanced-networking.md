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
1. `[HARD]` [Advanced Protocols & Forensics](./interview-hard.md)
2. `[SCENARIO]` [High-Scale Troubleshooting Drills](./scenarios.md)
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

### What is eBPF?

eBPF (Extended Berkeley Packet Filter) is a programmable kernel subsystem. Programs are compiled to eBPF bytecode, verified for safety by the kernel verifier, and JIT-compiled to native machine code. Programs attach to kernel hooks (network events, syscalls, tracepoints) and execute in-kernel without context switching to userspace.

### eBPF for Networking

eBPF programs can attach at various points in the kernel networking stack:

```
NIC Driver
    ↓
XDP (eXpress Data Path)  ← earliest hook, before sk_buff allocation
    ↓
TC (Traffic Control) ingress hook
    ↓
Netfilter / iptables
    ↓
Socket layer
    ↓
Application
```

**XDP (eXpress Data Path):** Processes packets at the driver level before the kernel allocates sk_buff. Can PASS, DROP, TX (reflect back), or REDIRECT. Used for DDoS mitigation, load balancing (Cloudflare, Facebook), and packet steering.

**BPF Maps:** Shared memory data structures between eBPF programs and userspace. Types: hash maps, arrays, per-CPU maps, LRU maps, ring buffers. Used to store state (e.g., connection tracking, routing tables).

### Cilium — eBPF-Native Kubernetes Networking

Cilium replaces iptables with eBPF programs for all Kubernetes networking:

**Service load balancing (kube-proxy replacement):**
- Iptables: O(n) rule traversal per packet — a 10,000-service cluster traverses 10,000 rules per packet
- Cilium: O(1) BPF hash map lookup — constant time regardless of cluster size
- 50–70% reduction in CPU overhead on large clusters

**Identity-based network policy:** Instead of IP-based rules (which change as pods restart), Cilium assigns each workload a cryptographic identity based on its Kubernetes labels. Network policy is enforced based on identity — survives pod IP changes.

**Hubble:** Cilium's observability layer. Provides per-flow visibility (Layer 3–7), service dependency maps, and Prometheus metrics — all from eBPF without application changes.

### DPDK (Data Plane Development Kit)

Kernel bypass networking for extreme performance. Applications access NIC hardware directly from userspace. No system calls, no interrupts. Used by telco, trading, and high-frequency workloads. Not suitable for typical DevOps workloads.

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
