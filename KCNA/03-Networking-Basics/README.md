# 03 — Networking Basics

## 1. Learning Objectives

By the end of this chapter you will be able to:

- Explain the OSI model and TCP/IP well enough to reason about how a Pod actually communicates.
- Explain IP addresses, CIDR notation, and subnetting — the raw material Kubernetes cluster networking is built from.
- Explain DNS and why service discovery in Kubernetes is fundamentally a DNS problem.
- Explain the difference between TCP and UDP and why it matters for different workload types.
- Understand ports, sockets, and load balancing concepts, since Services and Ingress (Chapters 16–17) are built directly on top of them.

**KCNA objectives covered:** Foundational networking vocabulary supporting the Kubernetes Fundamentals and Container Orchestration domains — this chapter is the prerequisite for Chapter 18 (Kubernetes Networking), Chapter 16 (Services), and Chapter 17 (Ingress and Gateway API).

---

## 2. Historical Background

- **1960s-70s:** ARPANET, the precursor to the internet, was built to let geographically separate computers communicate — the birth of packet-switched networking.
- **1974:** TCP/IP was designed by Vint Cerf and Bob Kahn as a common protocol suite so different networks could interoperate — literally "inter-net."
- **1983:** ARPANET fully switched to TCP/IP, and it has been the foundation of virtually all internet and private networking since.
- **1983:** DNS (Domain Name System) was introduced, because remembering numeric IP addresses for every website was impractical at scale — the same reason Kubernetes needs its own internal DNS (CoreDNS) today.
- **1990s onward:** OSI model formalized as a *teaching/reference* framework (it was never fully implemented as a protocol stack itself — TCP/IP won in practice), but it remains the standard way to reason about network layers in interviews and exams.

**Why this matters for Kubernetes specifically:** Kubernetes did not invent new networking concepts. It **reused** decades-old TCP/IP and DNS, and simply automated their configuration across a dynamic, ever-changing set of containers. Every "Service," "ClusterIP," and "Pod IP" concept later in this repo is just standard IP networking, orchestrated automatically instead of configured by hand.

---

## 3. Motivation: Why Do You Need Deep Networking Knowledge for Kubernetes?

**Analogy — The Postal System:**
Imagine you're running a large apartment complex (a cluster). Every apartment (Pod) needs an address (IP) so mail (network packets) can reach it. But apartments come and go constantly — people move in and out (Pods are created and destroyed) far more often than in a normal postal system. You cannot rely on a paper address book that a human updates by hand; you need an **automatic** system that tracks who lives where right now, and any mail addressed to "the reception desk of building 4" (a Service) gets automatically forwarded to whichever specific apartment can handle it *at this moment*.

This is the entire motivation for Kubernetes networking: containers/Pods are ephemeral (created/destroyed constantly, mostly with changing IPs), so static, manually-configured networking (like you'd do for a single physical server) breaks down immediately. Everything from Chapter 16 (Services) to Chapter 18 (Networking/CNI) exists to solve "how do I reliably reach something whose IP address keeps changing."

---

## 4. Core Concepts (From Absolute Beginner Level)

### 4.1 The OSI Model

**Definition:** A conceptual, 7-layer framework describing how data moves from a physical wire/wireless signal up to the actual application a human uses. It's a reference model, not literal code running on your machine — but the exam expects you to know it and map protocols onto it.

| Layer # | Name | Purpose | Example Protocols/Concepts |
|---|---|---|---|
| 7 | Application | What the user/application actually interacts with | HTTP, HTTPS, DNS, gRPC |
| 6 | Presentation | Data formatting, encryption/decryption, compression | TLS/SSL encryption happens conceptually here |
| 5 | Session | Establishing, managing, tearing down sessions between apps | Session tokens, sockets management |
| 4 | Transport | End-to-end delivery, reliability, ordering | TCP, UDP |
| 3 | Network | Logical addressing and routing between networks | IP, ICMP, routers |
| 2 | Data Link | Physical addressing within a local network segment | Ethernet, MAC addresses, switches |
| 1 | Physical | Actual electrical/optical/radio signal transmission | Cables, fiber, Wi-Fi radio waves |

**Analogy — The Postal System, Mapped to OSI:**
- Physical (1): the actual delivery trucks and roads.
- Data Link (2): the local mail carrier who knows every house on one street (MAC addresses = local-only identifiers).
- Network (3): the country-wide postal routing system that gets a letter from any city to any other city (IP = globally routable address).
- Transport (4): the promise "this package will arrive, in order, undamaged, and I'll confirm receipt" (TCP) vs. "I'll just fire it off and hope for the best, no confirmation" (UDP).
- Application (7): the actual letter's content/language (HTTP request, DNS query).

**Memory trick:** "**A**ll **P**eople **S**eem **T**o **N**eed **D**ata **P**rocessing" — Application, Presentation, Session, Transport, Network, Data Link, Physical (top to bottom).

### 4.2 TCP/IP Model (What Actually Runs in Practice)

The real internet uses a simpler 4-layer model that maps loosely onto OSI:

| TCP/IP Layer | Roughly Equivalent OSI Layers | Examples |
|---|---|---|
| Application | 5, 6, 7 | HTTP, DNS, gRPC |
| Transport | 4 | TCP, UDP |
| Internet | 3 | IP |
| Link | 1, 2 | Ethernet, Wi-Fi |

Exam framing: OSI is the teaching model (7 layers, know them by name and number), TCP/IP is the practical model actually implemented (4 layers). Both are tested — know how to translate between them.

### 4.3 IP Addresses and CIDR Notation

**Definition:** An IP address is a numeric identifier assigned to a device on a network, used for routing traffic to it. IPv4 addresses look like `192.168.1.10` (four 8-bit numbers, 0-255 each).

**CIDR (Classless Inter-Domain Routing) notation** expresses an IP address plus how many bits are the fixed "network" portion, written as `/n`. This is critical for the exam because Kubernetes cluster networking (Pod CIDR ranges, Service CIDR ranges) is configured entirely in this notation.

```
10.244.0.0/16
│           │
│           └── First 16 bits are the fixed network portion
└── Base address

This means addresses from 10.244.0.0 through 10.244.255.255 are
all part of this one network block (2^(32-16) = 65,536 addresses)
```

**Analogy — The Zip Code System:**
A CIDR block is like a **zip code range**. `10.244.0.0/16` is like saying "every address whose zip code starts with 10.244 belongs to this postal region" — regardless of the specific street number (the remaining bits). A `/24` is a "smaller zip code region" (256 addresses) than a `/16` (65,536 addresses) — the smaller the number after the slash... wait, actually **larger `/n` = smaller network** (more bits are "fixed," fewer bits are free for host addresses). This is the single most common point of confusion — memorize it explicitly:

| CIDR | Fixed bits | Available addresses | Relative size |
|---|---|---|---|
| /8 | 8 | 16,777,216 | Huge |
| /16 | 16 | 65,536 | Large |
| /24 | 24 | 256 | Small (a typical single subnet) |
| /32 | 32 | 1 | A single, specific address |

**Why this matters for Kubernetes:** When you install a cluster, you configure a **Pod CIDR** (e.g., `10.244.0.0/16`) and a **Service CIDR** (e.g., `10.96.0.0/12`) — these are just IP address ranges reserved for Pods and Services respectively, so the CNI plugin and kube-proxy know which addresses belong to "cluster-internal" traffic. Full detail in Chapter 18.

**Private IP ranges (memorize — frequently tested):**

| Range | CIDR | Common Use |
|---|---|---|
| 10.0.0.0 – 10.255.255.255 | 10.0.0.0/8 | Large private networks, common in Kubernetes Pod CIDRs |
| 172.16.0.0 – 172.31.255.255 | 172.16.0.0/12 | Private networks, Docker's default bridge often uses this range |
| 192.168.0.0 – 192.168.255.255 | 192.168.0.0/16 | Home/small office networks |

### 4.4 TCP vs UDP

| Aspect | TCP (Transmission Control Protocol) | UDP (User Datagram Protocol) |
|---|---|---|
| Connection | Connection-oriented (handshake required: SYN, SYN-ACK, ACK) | Connectionless, no handshake |
| Reliability | Guaranteed delivery, retransmits lost packets | No delivery guarantee, "fire and forget" |
| Ordering | Guarantees packets arrive in order | No ordering guarantee |
| Speed/Overhead | Slower, more overhead (acknowledgments, retransmission logic) | Faster, minimal overhead |
| Use case | Web traffic (HTTP/HTTPS), APIs, databases — anywhere correctness matters more than raw speed | DNS queries, video/voice streaming, gaming — anywhere speed matters more than occasional lost data |

**Analogy — Registered Mail vs. Postcards:**
TCP is like sending **registered mail**: the sender gets confirmation the letter arrived, and if it doesn't, it's resent. This has overhead (paperwork, waiting for confirmation) but guarantees delivery. UDP is like dropping a **postcard** in a mailbox: fast and cheap, but if it's lost, nobody automatically resends it, and there's no confirmation.

### 4.5 Ports and Sockets

**Definition:** A port is a numeric identifier (0-65535) that lets a single IP address host multiple simultaneous network services, distinguishing "which application on this machine should receive this traffic." A socket is the combination of an IP address + a port + a protocol, uniquely identifying one end of a network connection.

**Analogy — The Apartment Building Mailboxes:**
If an IP address is the building's street address, ports are the **individual mailbox numbers** inside that one building. Mail addressed to "123 Main Street, Mailbox 80" (IP:80, the standard HTTP port) goes to a different recipient than mail to "123 Main Street, Mailbox 443" (IP:443, standard HTTPS port), even though it's the same building.

**Well-known ports (memorize these — extremely commonly tested):**

| Port | Protocol/Service |
|---|---|
| 22 | SSH |
| 53 | DNS |
| 80 | HTTP |
| 443 | HTTPS |
| 3306 | MySQL |
| 5432 | PostgreSQL |
| 6379 | Redis |
| 2379-2380 | etcd client/peer communication (Kubernetes-specific, covered in Ch. 06-07) |
| 6443 | Kubernetes API Server (Kubernetes-specific, covered in Ch. 07) |
| 10250 | kubelet API (Kubernetes-specific, covered in Ch. 08) |

### 4.6 DNS (Domain Name System)

**Definition:** A hierarchical, distributed naming system that translates human-friendly domain names (like `google.com`) into IP addresses that computers actually use for routing.

**Analogy — The Phone Book / Contacts App:**
You don't memorize your friends' phone numbers (IP addresses); you save their name in your Contacts app (DNS) and just tap their name. Behind the scenes, your phone looks up the actual number for you. DNS does exactly this for the internet: humans type `google.com`, DNS resolves it to something like `142.250.premium.113`, and only then does the actual TCP/IP connection happen.

**DNS resolution flow (simplified):**

```
You type "example.com" in a browser
        ↓
Check local DNS cache — found it? Use it. Not found? Continue.
        ↓
Query a DNS resolver (often provided by your ISP or a public one like 8.8.8.8)
        ↓
Resolver queries Root DNS servers → find out who handles ".com"
        ↓
Resolver queries the ".com" TLD (Top-Level Domain) server → find out who handles "example.com"
        ↓
Resolver queries example.com's authoritative name server → get the actual IP
        ↓
IP address returned, browser opens a TCP connection to that IP
```

**Why this matters for Kubernetes:** Kubernetes runs its own internal DNS server, **CoreDNS**, inside the cluster. When one Pod wants to reach a Service by name (e.g., `my-service.my-namespace.svc.cluster.local`), CoreDNS resolves that name to the Service's ClusterIP — this is precisely "service discovery," and it's fundamentally just DNS, applied inside the cluster instead of on the public internet. Full detail in Chapter 18.

### 4.7 Load Balancing (Conceptual Preview)

**Definition:** Distributing incoming network traffic across multiple backend servers/instances, so no single instance is overwhelmed, and so traffic can be rerouted away from failed instances automatically.

**Analogy — The Airport Check-in Counters:**
If there's only one check-in counter (one server) for a Boeing 747 full of passengers, the line would be enormous. An airport opens **many counters** (multiple backend instances) and uses a system (a load balancer) to direct each new passenger (request) to whichever counter is free — and if one counter closes unexpectedly (a server crashes), passengers are simply redirected to the remaining open counters.

Common load balancing algorithms (know these, tested at a conceptual level):

| Algorithm | How it works |
|---|---|
| Round Robin | Requests distributed sequentially, one at a time, to each backend in turn |
| Least Connections | Request sent to whichever backend currently has the fewest active connections |
| IP Hash | Requests from the same client IP consistently routed to the same backend (useful for session stickiness) |

Kubernetes Services (Chapter 16) perform load balancing across Pod replicas essentially automatically, using this exact conceptual model underneath.

---

## 5. Internal Working: A Complete Request Journey

Here is the full journey of "your browser requests a website," tying together every concept above — this pattern repeats (with cluster-internal specifics) when we reach Kubernetes Services in Chapter 16.

```
1. Browser needs to reach "example.com"
        ↓
2. DNS resolution: "example.com" → 93.184.216.34 (an IP address)
        ↓
3. Browser opens a TCP connection to 93.184.216.34:443 (HTTPS port)
   → TCP three-way handshake: SYN, SYN-ACK, ACK
        ↓
4. TLS handshake occurs (encryption negotiated) — "Presentation layer" concept
        ↓
5. HTTP request sent over the encrypted TCP connection (Application layer)
        ↓
6. Traffic likely hits a load balancer first, which picks one of many
   backend servers to actually handle the request
        ↓
7. Backend server processes the request, sends an HTTP response back
        ↓
8. Browser renders the response
```

---

## 6. Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         OSI Model (7 layers)                   │
│  7 Application   → HTTP, DNS, gRPC                              │
│  6 Presentation  → TLS/SSL encryption                            │
│  5 Session       → session establishment/teardown                │
│  4 Transport     → TCP (reliable) / UDP (fast, no guarantee)     │
│  3 Network       → IP addressing & routing                       │
│  2 Data Link     → Ethernet, MAC addresses (local segment only)  │
│  1 Physical      → cables, radio waves, fiber                    │
└─────────────────────────────────────────────────────────────┘
                              │
              maps onto the practical stack:
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       TCP/IP Model (4 layers)                   │
│  Application → Transport → Internet → Link                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
        This is the exact stack every Kubernetes Pod uses
        internally, just automated and namespaced (Ch. 02, 18)
```

---

## 7. Component Breakdown

| Component | Purpose | Failure Scenario | Real-World Relevance |
|---|---|---|---|
| IP Address | Unique network identifier for routing | Wrong subnet/CIDR config causes unreachable hosts | Pod IPs, Service ClusterIPs |
| CIDR Block | Defines a range of IP addresses as one network | Overlapping CIDR ranges between cluster and corporate network cause routing conflicts | Pod CIDR, Service CIDR configuration during cluster setup |
| TCP | Reliable, ordered, connection-oriented transport | Long handshake overhead unsuitable for high-frequency small messages | Web APIs, databases |
| UDP | Fast, connectionless transport | No guarantee of delivery — bad for critical data | DNS queries, video streaming, some service mesh telemetry protocols |
| Port | Distinguishes services on the same IP | Port conflicts prevent two services from binding the same port on one host | Container port mappings, Service `targetPort` |
| DNS | Human-readable name → IP resolution | DNS outage/misconfiguration makes services "unreachable by name" even if IP-reachable | CoreDNS inside Kubernetes clusters |
| Load Balancer | Distributes traffic across backends, reroutes around failures | Misconfigured health checks send traffic to dead backends | Kubernetes Services (Ch. 16), cloud LoadBalancer type |

---

## 8. Important Terminology

| Term | Meaning | Why Important |
|---|---|---|
| OSI Model | 7-layer conceptual networking reference model | Foundational vocabulary, frequently tested by layer number/name |
| TCP/IP Model | 4-layer practically-implemented networking stack | Real-world equivalent of OSI, also tested |
| IP Address | Numeric device identifier for routing | Basis of all cluster networking |
| CIDR | Notation expressing an IP range (`/n` = fixed bits) | Used to define Pod/Service address ranges |
| TCP | Reliable, connection-oriented transport protocol | Most application traffic |
| UDP | Fast, connectionless transport protocol | DNS, streaming, some telemetry |
| Port | Numeric identifier distinguishing services on one IP | Container/Service port mapping |
| Socket | IP + port + protocol combination | Uniquely identifies one end of a connection |
| DNS | Translates domain names to IP addresses | CoreDNS = Kubernetes' internal version of this |
| Load Balancing | Distributing traffic across multiple backends | Core behavior of Kubernetes Services |
| MAC Address | Physical/hardware address for local network segment (Data Link layer) | Distinguish from IP (logical, routable) address |

---

## 9. YAML Deep Dive

Not directly applicable yet — no Kubernetes objects introduced. Preview only: Kubernetes Service definitions (Chapter 16) will directly reference `port`, `targetPort`, and `protocol: TCP/UDP` fields, which are exactly the concepts from Sections 4.4–4.5 of this chapter, just expressed as YAML.

---

## 10. kubectl Commands

Not yet introduced — begins in Chapter 06. This chapter's relevant commands are plain networking diagnostic tools you'll reuse constantly once inside containers/nodes:

| Command | Purpose | Example |
|---|---|---|
| `ping` | Test basic reachability (ICMP) | `ping 8.8.8.8` |
| `curl` | Make an HTTP(S) request from the command line | `curl -v https://example.com` |
| `dig` / `nslookup` | Query DNS directly | `dig example.com` |
| `netstat` / `ss` | Show active network connections/listening ports | `ss -tulnp` |
| `traceroute` | Show the network hops a packet takes to a destination | `traceroute example.com` |
| `ip addr` | Show network interfaces and their IP addresses | `ip addr show` |

---

## 11. Hands-on Examples

**Lab 1 — Watch DNS resolution happen:**
```bash
dig example.com
# Observe the ANSWER SECTION showing the resolved IP address
```

**Lab 2 — Compare TCP vs UDP behavior conceptually:**
```bash
curl -v https://example.com    # Uses TCP (note the TCP handshake happens before TLS)
dig example.com                # Uses UDP by default for the DNS query itself
```

**Lab 3 — Understand CIDR math:**
Given `192.168.1.0/24`, manually calculate: how many usable IP addresses are in this block? (Answer: 2^(32-24) = 256 total addresses, 254 usable after reserving the network address and broadcast address — a very common exam-style calculation.)

---

## 12. Internal Flow

```
Application wants to send data
        ↓
Data handed to Transport layer → wrapped in TCP or UDP segment (adds port info)
        ↓
Handed to Network layer → wrapped in an IP packet (adds source/destination IP)
        ↓
Handed to Data Link layer → wrapped in an Ethernet frame (adds MAC addresses)
        ↓
Handed to Physical layer → converted to electrical/optical/radio signal
        ↓
Reverse process happens at the receiving end, layer by layer, unwrapping each header
```

---

## 13. Real-World Examples

1. **CoreDNS inside every Kubernetes cluster** resolves internal Service names, directly applying DNS concepts from this chapter inside a private, cluster-scoped context.
2. **Cloud load balancers** (AWS ELB/ALB, Azure Load Balancer, GCP Load Balancer) implement the load-balancing algorithms from Section 4.7 at massive scale, often fronting Kubernetes `LoadBalancer`-type Services.
3. **CDNs (Content Delivery Networks)** like Cloudflare use DNS tricks (returning different IPs based on geographic location) to route users to the nearest edge server — a direct real-world application of DNS beyond simple name resolution.
4. **VoIP and video conferencing** (Zoom, Google Meet) deliberately use UDP for the actual audio/video stream (speed matters more than a dropped frame here and there), a direct real-world application of the TCP vs UDP tradeoff.
5. **Corporate VPNs** rely on private IP ranges (Section 4.3's table) and careful CIDR planning to avoid address collisions when connecting to cloud VPCs and Kubernetes clusters over the same network.

---

## 14. Best Practices

- Plan Pod and Service CIDR ranges carefully before cluster creation to avoid overlapping with your corporate network's existing IP ranges (a very common real-world Kubernetes networking incident).
- Prefer TCP for anything requiring correctness/completeness (APIs, databases); use UDP only when occasional data loss is acceptable in exchange for speed.
- Always validate DNS resolution as an early troubleshooting step — "can I resolve the name" is a faster and more informative check than "can I reach the IP directly," since it tells you whether the problem is DNS or actual connectivity.
- Use well-known ports consistently (don't run HTTPS on a random nonstandard port in production without strong reason) to keep firewall rules and mental models simple.

---

## 15. Common Mistakes

- Believing a larger CIDR suffix number (`/24`) means a *bigger* network — it's the opposite; larger suffix = smaller network (fewer available addresses).
- Assuming TCP is "always better" than UDP — the right choice depends entirely on whether reliability or speed matters more for that specific traffic.
- Confusing MAC addresses (Data Link layer, local-segment-only) with IP addresses (Network layer, globally routable).
- Forgetting that DNS resolution is a *separate* step before any TCP connection happens — "the website is down" is sometimes actually "DNS can't resolve the name," a different problem with a different fix.
- Overlapping private IP ranges between on-prem networks and cloud/Kubernetes networks, causing silent routing conflicts.

---

## 16. Troubleshooting

| Symptom | Possible Cause | Debugging Commands | Fix |
|---|---|---|---|
| "Website not loading" | DNS failure vs. actual connectivity failure — must distinguish | `dig`/`nslookup` first, then `ping`/`curl` to the raw IP | If DNS fails but raw IP works: fix DNS. If raw IP also fails: it's a routing/firewall issue |
| Slow application response | Possible TCP retransmissions due to packet loss, or DNS lookup delays | `ss -s` (socket stats), `dig` (check DNS latency) | Investigate network path, consider caching DNS lookups |
| Two services can't both start | Port conflict — both trying to bind the same port on the same IP | `ss -tulnp` to see what's listening on which port | Change one service's port, or use different IPs |
| Intermittent connectivity between two networks | Overlapping CIDR ranges causing ambiguous routing | Review CIDR plans on both networks | Re-IP one of the conflicting ranges |

---

## 17. Comparison Tables

**TCP vs UDP:** see Section 4.4 table.

**OSI vs TCP/IP Model:**

| Aspect | OSI Model | TCP/IP Model |
|---|---|---|
| Layers | 7 | 4 |
| Status | Conceptual/teaching reference | Actually implemented in real networks |
| Granularity | More detailed (splits Application/Presentation/Session) | Simpler (merges those three into one Application layer) |

**IPv4 vs IPv6 (brief, exam-relevant awareness):**

| Aspect | IPv4 | IPv6 |
|---|---|---|
| Address length | 32-bit (e.g., `192.168.1.1`) | 128-bit (e.g., `2001:0db8::1`) |
| Address space | ~4.3 billion addresses | Effectively unlimited for practical purposes |
| Adoption | Still dominant, especially inside private networks (including most Kubernetes clusters by default) | Growing, some clusters now support dual-stack (IPv4 + IPv6) |

---

## 18. Memory Tricks

- **"All People Seem To Need Data Processing"** — OSI layers 7→1 (Application, Presentation, Session, Transport, Network, Data Link, Physical).
- **"TCP = Trustworthy, Careful, Precise" / "UDP = Utterly Doesn't Promise."**
- **CIDR rule: "Bigger slash number, smaller network."** Picture the slash as a knife cutting a smaller and smaller slice as the number grows.
- **DNS = "the Contacts app for the internet."**

---

## 19. Interview Questions

**Easy:**
1. What is the difference between TCP and UDP?
   *Expected answer:* TCP is connection-oriented and reliable (guarantees delivery and order, via a handshake and retransmission), while UDP is connectionless and unreliable but faster, with no delivery guarantees — used where speed matters more than perfect accuracy (DNS, streaming).

**Medium:**
2. What does CIDR notation like `/24` actually mean, and why does a `/16` represent a larger network than a `/24`?
   *Expected answer:* The number after the slash is how many bits are fixed as the "network" portion; the remaining bits are available for host addresses. A `/24` fixes 24 bits, leaving 8 bits (256 addresses) for hosts. A `/16` fixes only 16 bits, leaving 16 bits (65,536 addresses) — so fewer fixed bits means a larger address space, meaning a smaller slash number represents a bigger network.

**Hard:**
3. A company merges two Kubernetes clusters' networks over a VPN, and Pods intermittently fail to reach each other. Using networking concepts from this chapter, what's a likely root cause and how would you investigate it?
   *Expected answer:* Likely cause is overlapping Pod/Service CIDR ranges between the two clusters, causing ambiguous routing (packets destined for one cluster's Pod IP range being misrouted because the other cluster claims the same range). Investigation: compare each cluster's configured Pod CIDR and Service CIDR ranges for overlap, and check routing tables on the VPN gateway.

---

## 20. KCNA Practice Questions

**Q1.** Which OSI layer is responsible for logical addressing and routing between networks?
A. Layer 2 (Data Link)
B. Layer 3 (Network)
C. Layer 4 (Transport)
D. Layer 7 (Application)

**Correct answer: B**
*Explanation:* Layer 3 (Network) handles IP addressing and routing. Layer 2 handles local, physical-segment addressing (MAC addresses). Layer 4 handles end-to-end delivery reliability (TCP/UDP). Layer 7 is where applications like HTTP and DNS operate.

---

**Q2.** Which protocol guarantees ordered, reliable delivery of data through a connection handshake?
A. UDP
B. IP
C. TCP
D. DNS

**Correct answer: C**
*Explanation:* TCP performs a three-way handshake (SYN, SYN-ACK, ACK) and guarantees ordered, reliable delivery via acknowledgments and retransmission. UDP (A) is connectionless with no such guarantees. IP (B) handles addressing/routing, not reliability. DNS (D) is an application-layer name resolution protocol, not a transport protocol.

---

**Q3.** In CIDR notation, which of the following represents the LARGEST network (most available addresses)?
A. 10.0.0.0/8
B. 10.0.0.0/16
C. 10.0.0.0/24
D. 10.0.0.0/30

**Correct answer: A**
*Explanation:* A smaller number after the slash means fewer fixed bits and therefore more available host addresses — `/8` leaves 24 bits free (16,777,216 addresses), the largest of the options listed. `/30` (D) leaves only 2 usable addresses, the smallest.

---

**Q4.** What is the primary purpose of DNS?
A. Encrypting network traffic
B. Translating human-readable domain names into IP addresses
C. Load balancing traffic across multiple servers
D. Assigning MAC addresses to network devices

**Correct answer: B**
*Explanation:* DNS's core function is name-to-IP resolution. Encryption (A) is handled by TLS/SSL. Load balancing (C) is a separate concern (Section 4.7). MAC address assignment (D) is unrelated to DNS and typically hardware-based or DHCP/Data-Link-layer-related.

---

**Q5.** Which well-known port is conventionally used for HTTPS traffic?
A. 22
B. 80
C. 443
D. 3306

**Correct answer: C**
*Explanation:* Port 443 is the standard HTTPS port. Port 22 (A) is SSH, port 80 (B) is plain HTTP, and port 3306 (D) is MySQL's default port.

---

**Q6.** Why is UDP often preferred over TCP for DNS queries and live video streaming?
A. UDP is more secure than TCP
B. UDP has lower overhead and doesn't require a connection handshake, favoring speed over guaranteed delivery
C. UDP guarantees packet ordering better than TCP
D. TCP cannot be used for these purposes at all

**Correct answer: B**
*Explanation:* UDP's lack of handshake and acknowledgment overhead makes it faster, which is preferable when occasional data loss (a dropped video frame, a DNS query that can simply be retried) is an acceptable tradeoff for speed. A and C are false claims — UDP is not inherently more secure nor does it guarantee ordering. D is false; TCP *can* technically be used for these, but UDP is conventionally preferred for the stated reasons.

---

**Q7.** What does a socket represent?
A. Only an IP address
B. Only a port number
C. The combination of an IP address, a port number, and a protocol
D. A physical network cable

**Correct answer: C**
*Explanation:* A socket uniquely identifies one endpoint of a network connection by combining IP address, port, and protocol (TCP or UDP). A and B are each only part of the full definition. D describes physical infrastructure, unrelated to the logical socket concept.

---

**Q8.** In Kubernetes, what internal component performs the role that public DNS servers perform on the broader internet?
A. kube-proxy
B. CoreDNS
C. etcd
D. kubelet

**Correct answer: B**
*Explanation:* CoreDNS is Kubernetes' internal DNS server, resolving Service names to ClusterIPs inside the cluster, directly analogous to how public DNS resolves domain names to internet IPs. kube-proxy (A), etcd (C), and kubelet (D) have entirely different responsibilities, covered in later chapters.

---

**Q9.** A load balancer algorithm that always routes a specific client's requests to the same backend server is best described as:
A. Round robin
B. Least connections
C. IP hash
D. Random selection

**Correct answer: C**
*Explanation:* IP hash routing consistently maps a given client IP to the same backend, providing session stickiness. Round robin (A) cycles sequentially regardless of client identity. Least connections (B) routes based on current backend load, not client identity. D is not a standard named algorithm in this context.

---

**Q10.** Which private IP range is most commonly associated with home and small office networks?
A. 10.0.0.0/8
B. 172.16.0.0/12
C. 192.168.0.0/16
D. 127.0.0.0/8

**Correct answer: C**
*Explanation:* 192.168.0.0/16 is the conventional range for home/small office networks. 10.0.0.0/8 (A) is typically used for large private networks (including many Kubernetes Pod CIDRs). 172.16.0.0/12 (B) is often used by Docker's default bridge network. 127.0.0.0/8 (D) is the loopback range (localhost), not a general private network range.

---

**Q11.** Which layer of the OSI model do MAC addresses belong to?
A. Layer 1 (Physical)
B. Layer 2 (Data Link)
C. Layer 3 (Network)
D. Layer 4 (Transport)

**Correct answer: B**
*Explanation:* MAC addresses are Layer 2 (Data Link) identifiers, used for addressing within a local network segment. Layer 1 (A) is raw physical signaling with no addressing concept. Layer 3 (C) uses IP addresses instead. Layer 4 (D) uses ports, not MAC addresses.

---

**Q12.** What is the purpose of a subnet mask?
A. To encrypt IP traffic
B. To divide an IP address into network and host portions
C. To assign a MAC address to a device
D. To cache DNS records

**Correct answer: B**
*Explanation:* A subnet mask (equivalent information to CIDR notation) marks which bits of an IP address represent the network and which represent the host. It has nothing to do with encryption (A), MAC assignment (C), or DNS caching (D).

---

**Q13.** A client sends a TCP SYN packet to a server. What is the correct next step in the handshake?
A. The server immediately sends application data
B. The server responds with SYN-ACK
C. The connection is already established after just the SYN
D. The client resends the SYN repeatedly until timeout

**Correct answer: B**
*Explanation:* The three-way handshake is SYN → SYN-ACK → ACK. After the client's SYN, the server replies with SYN-ACK, and only after the client's final ACK is the connection considered established — application data (A) doesn't flow until this completes.

---

**Q14.** Which statement about NAT (Network Address Translation) is correct?
A. NAT assigns permanent public IPs to every internal host
B. NAT allows multiple devices on a private network to share a single public IP address for outbound traffic
C. NAT is a replacement for DNS
D. NAT operates only at Layer 7

**Correct answer: B**
*Explanation:* NAT translates private internal IPs to a shared public IP (and back) so multiple internal devices can reach the internet through one external address — a foundational concept behind how home routers and, later, some Kubernetes networking modes work. NAT operates around Layer 3/4, not Layer 7 (D), and is unrelated to DNS's job (C).

---

**Q15.** What does "least connections" load balancing optimize for?
A. Always picking the same backend for a given client
B. Sending each new request to the backend currently handling the fewest active connections
C. Randomly distributing requests with no regard for backend load
D. Sending all traffic to the first backend in a list

**Correct answer: B**
*Explanation:* Least-connections algorithms track active connection counts per backend and route new requests to the least-loaded one, aiming for balanced real-time load rather than simple rotation (round robin) or client stickiness (IP hash).

---

**Q16.** Why can two different Kubernetes clusters using overlapping Pod CIDR ranges cause problems when peered over a VPN?
A. Overlapping ranges cause DNS names to collide
B. Routers cannot unambiguously determine which cluster a destination Pod IP belongs to, causing misrouted or dropped traffic
C. Overlapping CIDRs are automatically merged and cause no issues
D. TCP handshakes fail whenever CIDRs overlap

**Correct answer: B**
*Explanation:* IP routing depends on each address being unique within a routing domain; if both clusters claim the same Pod IP range, routing tables cannot distinguish the true destination, causing ambiguous or dropped packets — this is the exact scenario explored in this chapter's hard interview question.

---

**Q17.** What information does the "protocol" field in a socket definition specify?
A. Whether the connection uses TCP or UDP
B. The physical network cable type
C. The DNS server used
D. The client's geographic location

**Correct answer: A**
*Explanation:* A socket is defined by IP + port + protocol; the protocol field distinguishes, e.g., a TCP connection on port 443 from a UDP "connection" on the same port — these are treated as entirely separate sockets.

---

**Q18.** Which of the following is NOT one of the four layers in the TCP/IP model?
A. Application
B. Transport
C. Presentation
D. Internet

**Correct answer: C**
*Explanation:* "Presentation" is one of the OSI model's seven layers, not part of the four-layer TCP/IP model (Application, Transport, Internet, Link). This distinction — OSI's more granular layering vs. TCP/IP's practical collapsed layering — is a common exam trap.

---

**Q19.** Why is port 53 significant in networking?
A. It is the default HTTPS port
B. It is the standard port used by DNS
C. It is reserved exclusively for Kubernetes' API server
D. It is the default SSH port

**Correct answer: B**
*Explanation:* Port 53 is the conventional port for DNS queries (both UDP and TCP). HTTPS uses 443 (A), the Kubernetes API server conventionally uses 6443 (C), and SSH uses 22 (D).

---

**Q20.** In the CoreDNS-driven Service discovery flow inside a Kubernetes cluster, what does CoreDNS ultimately resolve a Service name to?
A. A Node's MAC address
B. The Service's ClusterIP (or Pod IPs, depending on Service type)
C. A public internet IP address
D. A TCP port number only, with no IP

**Correct answer: B**
*Explanation:* CoreDNS resolves a Service's DNS name (e.g., `my-svc.my-namespace.svc.cluster.local`) to its ClusterIP (or directly to backing Pod IPs for headless Services) — mirroring how public DNS resolves domain names to IPs, but scoped to cluster-internal addressing.

---

## 21. Chapter Summary (One-Page Revision Sheet)

- **OSI model (7 layers):** Application, Presentation, Session, Transport, Network, Data Link, Physical — "All People Seem To Need Data Processing."
- **TCP/IP model (4 layers):** Application, Transport, Internet, Link — the practically implemented equivalent.
- **CIDR notation:** larger slash number = smaller network (fewer available addresses); `/24` = 256 addresses, `/16` = 65,536 addresses.
- **TCP:** connection-oriented, reliable, ordered — used where correctness matters (web, APIs, databases).
- **UDP:** connectionless, unreliable, fast — used where speed matters more than occasional loss (DNS queries, video/voice streaming).
- **Ports:** distinguish multiple services on one IP; memorize 22 (SSH), 53 (DNS), 80 (HTTP), 443 (HTTPS), 6443 (K8s API Server), 10250 (kubelet).
- **DNS:** translates domain names to IPs; **CoreDNS** is Kubernetes' internal equivalent for Service discovery.
- **Load balancing:** distributes traffic across backends using algorithms like round robin, least connections, or IP hash — this is exactly what Kubernetes Services do internally (Chapter 16).
- Private IP ranges to know: `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`.

---

### Chapter Completion Checklist

1. **Topics covered:** OSI model, TCP/IP model, IP addressing, CIDR notation, private IP ranges, TCP vs UDP, ports/sockets, DNS resolution flow, load balancing algorithms.
2. **KCNA objectives completed:** Foundational networking vocabulary required across Kubernetes Fundamentals and Container Orchestration domains.
3. **Remaining objectives:** Kubernetes-specific networking (CNI, Services, Ingress, Network Policies) — covered in Chapters 16-18.
4. **Suggested revision checklist:** Recite OSI layers from memory using the mnemonic; manually calculate available addresses for `/8`, `/16`, `/24`, `/30`; explain the full DNS resolution flow from Section 4.6 without notes.
5. **Suggested hands-on exercises:** Complete all three labs in Section 11 — practice CIDR math by hand until it's automatic, since exam questions often require quick calculation.
6. **Related chapters:** Previous: [02-Linux-Basics-for-Kubernetes](../02-Linux-Basics-for-Kubernetes/README.md). Next: [04-Containers](../04-Containers/README.md) — builds on both Linux namespaces (Ch. 02) and networking (this chapter) to explain container image formats and lifecycle.
