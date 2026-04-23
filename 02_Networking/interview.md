# Networking — Interview Questions

All difficulty levels combined.

---

## Easy

**1. What is the OSI model?**

A 7-layer reference model for network communication: Physical, Data Link, Network, Transport, Session, Presentation, Application. TCP/IP maps roughly to 4 layers.

**2. What is the difference between TCP and UDP?**

TCP is connection-oriented with handshaking, ordering, and retransmission guarantees. UDP is connectionless, faster, and has no delivery guarantee. Use TCP for HTTP/databases; UDP for DNS/gaming/video streaming.

**3. What is a subnet mask?**

A subnet mask defines which portion of an IP address is the network and which is the host. Example: `255.255.255.0` (`/24`) means the first 24 bits are the network.

**4. What is a CIDR block?**

Classless Inter-Domain Routing notation compresses IP and mask: `10.0.0.0/16` means 16 bits for the network, 16 bits for hosts (65,536 addresses).

**5. What is NAT?**

Network Address Translation maps private IP addresses to a public IP (or set of ports), allowing many hosts to share one public IP. Used in home routers and cloud VPC gateways.

**6. What is DNS and how does resolution work?**

DNS maps domain names to IP addresses. Resolution: client asks local resolver → recursive resolver → root nameserver → TLD nameserver → authoritative nameserver → returns the IP.

**7. What is the difference between HTTP and HTTPS?**

HTTP is plaintext. HTTPS wraps HTTP in TLS, providing encryption, integrity, and authentication of the server via certificate.

**8. What is a load balancer and what are the types?**

A load balancer distributes traffic across multiple servers. Layer 4 (TCP/UDP) balancers route based on IP/port. Layer 7 (HTTP) balancers can route based on URL path, headers, or hostname.

**9. What is a firewall and what does it filter on?**

A firewall controls which network traffic is allowed or denied based on rules. Stateless firewalls filter on IP/port per packet. Stateful firewalls track connection state and can allow replies automatically.

**10. What is the purpose of the `traceroute` command?**

It shows the path packets take to a destination, listing each hop (router) with its IP and round-trip latency. Useful for diagnosing where packet loss or high latency occurs.

**11. What is a VPN?**

A Virtual Private Network encrypts traffic between two endpoints over a public network, making remote hosts appear to be on the same private network.

**12. What is a CDN?**

A Content Delivery Network caches content at geographically distributed edge nodes, serving users from the nearest point to reduce latency.

**13. What is a proxy vs reverse proxy?**

A forward proxy sits between clients and the internet — the client knows about it. A reverse proxy sits in front of backend servers — the client thinks it's talking directly to the server.

---

## Medium

**14. Explain the TCP three-way handshake.**

1. Client sends SYN (synchronize) with an initial sequence number.
2. Server responds with SYN-ACK (acknowledges client's SYN, sends its own SYN).
3. Client sends ACK to acknowledge the server's SYN.

The connection is now established. Both sides have agreed on sequence numbers for ordered, reliable delivery.

**15. What is the difference between a VLAN and a VPC?**

A VLAN is a Layer 2 network segmentation technology — it isolates broadcast domains on the same physical switch. A VPC (Virtual Private Cloud) is a logically isolated network in a cloud provider, built on software-defined networking with its own IP range, subnets, route tables, and internet gateways.

**16. How does BGP work and where is it used in DevOps?**

BGP (Border Gateway Protocol) is the routing protocol used between autonomous systems on the internet. In DevOps: Calico and Cilium in BGP mode use it to advertise pod CIDR routes to physical routers (no overlay needed). On-premises to cloud connectivity via ExpressRoute/Direct Connect uses BGP for route exchange. Multi-cloud or multi-region failover routing is controlled via BGP route manipulation.

**17. What happens when you type `curl https://example.com` and press enter?**

1. DNS resolution: OS resolves `example.com` to an IP.
2. TCP connection to port 443.
3. TLS handshake: server presents cert, client validates, both negotiate cipher suite and exchange keys.
4. HTTP GET request is sent over the encrypted tunnel.
5. Server responds with HTTP 200 and HTML body.
6. TCP connection is closed (or kept alive for reuse).

**18. Explain network namespaces in Linux and how Kubernetes uses them.**

A network namespace is a Linux kernel feature that provides an isolated view of the network stack — its own interfaces, routing table, iptables rules, and sockets. Each Kubernetes Pod gets its own network namespace. The CNI plugin creates a `veth` pair: one end in the Pod's namespace, the other in the host's root namespace. The Pod's namespace has `eth0`; the host side is connected to a bridge or directly routed. Containers within the same Pod share a network namespace (they can communicate via localhost).

**19. What is MTU and what is MTU mismatch?**

MTU (Maximum Transmission Unit) is the largest packet a network link can carry without fragmentation (default Ethernet: 1500 bytes). MTU mismatch occurs when two hosts or network segments have different MTUs — packets larger than the path MTU are fragmented or dropped (if DF bit is set). In Kubernetes with overlay networks (VXLAN), the encapsulation header adds overhead — the inner MTU must be reduced (typically to 1450 bytes) to avoid fragmentation.

**20. How does iptables work and how is it used in Kubernetes?**

`iptables` is a Linux firewall and packet manipulation tool using chains and rules evaluated in order. Kubernetes uses iptables (via kube-proxy) to implement Service load balancing: for each Service, kube-proxy writes DNAT rules in the PREROUTING chain that redirect traffic from the ClusterIP to one of the backing Pod IPs using probability-based selection. On large clusters this creates O(n) rule traversal per packet — a reason CNI plugins like Cilium replace iptables with eBPF maps.

**21. What is service discovery and how does Kubernetes implement it?**

Service discovery is the mechanism by which services find each other without hardcoded IPs. Kubernetes uses:
- **DNS:** CoreDNS resolves `<service>.<namespace>.svc.cluster.local` to the Service ClusterIP.
- **Environment variables:** Kubernetes injects `<SERVICE>_SERVICE_HOST` and `<SERVICE>_SERVICE_PORT` env vars into every Pod at creation time.

**22. What is a network policy in Kubernetes?**

A NetworkPolicy is a namespaced Kubernetes resource that defines firewall rules for Pod traffic. It specifies: which Pods the policy applies to (`podSelector`), ingress rules (allowed inbound traffic sources), and egress rules (allowed outbound traffic destinations). NetworkPolicies are enforced by the CNI plugin (Calico, Cilium). If no NetworkPolicy applies to a Pod, all ingress/egress is allowed.

**23. What is a Service mesh and why is it used?**

A service mesh is an infrastructure layer for service-to-service communication. Each service gets a sidecar proxy (Envoy in Istio/Linkerd). The mesh provides: mTLS between services (encryption + identity), traffic management (retries, timeouts, canary splitting), observability (per-request traces, metrics), and policy enforcement — all without changing application code.

---

## Hard

**24. Explain the data plane vs. control plane architecture of Istio.**

- **Control Plane (Istiod):** Doesn't touch packets. Manages and configures sidecar proxies. Translates high-level routing rules (`VirtualService`, `DestinationRule`) into Envoy xDS configuration and pushes it to proxies via gRPC.
- **Data Plane (Envoy sidecars):** Intercepts all in/out traffic for each Pod via iptables REDIRECT rules. Executes rules from Istiod: mTLS encryption, traffic splitting for canaries, telemetry collection, circuit breaking.

**25. How does Cilium replace kube-proxy and what performance benefit does it provide?**

Cilium uses eBPF programs in the kernel's network path to implement Service load balancing as O(1) hash map lookups, replacing iptables O(n) rule traversal. On a 10,000-service cluster, every packet avoids traversing 10,000 iptables rules. This reduces per-packet CPU overhead by 50-70% and achieves single-digit microsecond processing. Cilium also provides identity-based network policies using cryptographic identities rather than IP addresses.

**26. What is BGP in Kubernetes networking and when does it matter?**

BGP is used when Calico or Cilium is configured in BGP mode — each node peers with physical routers and announces its pod subnet. External clients reach pods directly via the physical network's routing tables without any overlay encapsulation. This matters in: bare-metal deployments where VXLAN overhead is unacceptable, environments with existing BGP infrastructure, and high-throughput scenarios where encapsulation latency is unacceptable.

**27. How do you design a multi-cluster service mesh for active-active failover across two regions?**

- Deploy Istio on both clusters with a shared root CA.
- Use `ServiceEntry` to register east-west gateway endpoints from the remote cluster.
- Configure `DestinationRule` with locality-aware load balancing: primary traffic goes to local cluster, failover triggers when local pod availability drops below threshold.
- East-west gateways in each cluster receive cross-cluster traffic over mTLS.
- Use AWS Route53 or Azure Traffic Manager for global DNS routing to nearest healthy cluster.
- For stateful services: active-passive database with read replicas in each region; mesh handles request failover but writes must go to the primary.

**28. What is a split-brain scenario in multi-cluster networking and how is it prevented?**

Split-brain occurs when network connectivity between clusters is lost and each cluster acts as the sole authority. This leads to inconsistent configs and routing failures. Prevention:
1. Configure mesh with clear failover logic — `DestinationRule` outlier detection routes to local instances when cross-cluster endpoints are unreachable.
2. Active health checks on cross-cluster endpoints — remove unreachable endpoints from the load-balancing pool.
3. Redundant control planes with a primary/failover designation.

**29. How does VXLAN work and what overhead does it add?**

VXLAN (Virtual Extensible LAN) encapsulates Layer 2 Ethernet frames inside UDP packets. A VTEP (VXLAN Tunnel Endpoint) on each node encapsulates outgoing packets and decapsulates incoming ones. The overhead: VXLAN adds a 50-byte header (UDP + VXLAN + outer IP + outer Ethernet). On a standard 1500-byte MTU network, the effective inner MTU is 1450 bytes — CNI plugins must configure this reduced MTU to avoid fragmentation.
