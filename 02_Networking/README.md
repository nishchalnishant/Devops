# Networking



This section focuses on the connectivity and security protocols required to manage modern infrastructure.

#### The OSI Model

The Open Systems Interconnection (OSI) model is a theoretical framework used to understand how data moves across a network through seven distinct layers.

* Why it matters for DevOps: It helps in pinpointing where a failure is occurring (e.g., is it a physical cable issue at Layer 1, or an application error at Layer 7?).

#### Network Protocols (TCP/IP, HTTP, etc.)

Protocols are the "languages" devices use to talk to each other.

* TCP/IP: The foundation of the internet. TCP ensures data is delivered reliably and in the correct order.
* HTTP/HTTPS: The protocol for transferring web data.
* UDP: A faster, "fire-and-forget" protocol used for streaming or DNS where perfect delivery isn't as critical as speed.

#### Subnets / CIDR

This involves IP addressing and network segmentation.

* Subnetting: Dividing a large network into smaller, manageable pieces to improve security and performance.
* CIDR (Classless Inter-Domain Routing): A method for allocating IP addresses and routing. For example, a range like `10.0.0.0/16` defines how many internal IPs are available in your cloud environment (VPC).

#### SSH / SCP

Tools for Secure remote access and file transfer.

* SSH (Secure Shell): The standard way to log into a remote Linux server securely via the command line.
* SCP (Secure Copy Protocol): Used to securely move files between a local host and a remote host.

#### SSL / HTTPS

Focused on encryption and secure web traffic.

* SSL/TLS: Cryptographic protocols that provide communications security over a computer network.
* HTTPS: The secure version of HTTP. In DevOps, you will often manage "Certificates" to ensure that data between your users and your servers is encrypted.

#### DNS (Domain Name System)

Often called the "phonebook of the internet."

* Function: It translates human-readable domain names (like `google.com`) into machine-readable IP addresses (like `142.250.190.46`).
* DevOps Context: You’ll use DNS for service discovery and routing traffic to different environments (Load Balancers, Cloudfront, etc.).

#### Network Troubleshooting

The process of diagnosing connectivity issues when services cannot talk to each other.

* Common Tools:
  * `ping`: To check if a server is reachable.
  * `traceroute`: To see the path data takes to reach a destination.
  * `nslookup/dig`: To troubleshoot DNS record issues.
  * `curl`: To test if an application/API is responding correctly over HTTP.



This is Section 3: Networking for DevOps & SRE. For a mid-to-senior role, networking is rarely about crimping cables; it is about Software Defined Networking (SDN), traffic engineering, and debugging the "invisible" layers between microservices.

In production, networking is often the culprit behind "flaky" systems. Your goal is to move from understanding _how_ it works to _how it fails at scale_.

***

#### 🔹 1. Improved Notes: The SRE’s Network Stack

**Layer 4 (Transport) vs. Layer 7 (Application)**

* L4 (TCP/UDP): SREs care about the Three-Way Handshake and Connection States. In high-traffic environments, you will face "Socket Exhaustion" where the system runs out of ephemeral ports.
* L7 (HTTP/gRPC/TLS): This is where business logic lives. You must understand TLS Termination—where the encrypted traffic is decrypted (at the Load Balancer or the Pod?) and how that impacts CPU overhead.

**The Modern DNS Pipeline**

* TTL (Time to Live): A double-edged sword. Low TTL allows for fast failover but increases load on DNS servers. High TTL reduces latency but makes "emergency migrations" impossible.
* Split-Horizon DNS: Providing different IP addresses for the same domain depending on whether the request comes from inside or outside the VPC.

**Subnetting & CIDR in Cloud**

* In AWS/GCP/Azure, your VPC design is permanent. If you pick a CIDR block that is too small (e.g., `/24`), you will run out of IPs as your Kubernetes cluster scales, leading to Pod Scheduling failures.

***

#### 🔹 2. Interview View (Q\&A)

Q1: A user reports a "Connection Refused" error. A different user reports a "Connection Timeout." What is the difference from a networking perspective?

* Answer: \* Connection Refused: The packet reached the server, but the server sent a `RST` (Reset) packet back. This usually means the process (like Nginx) is not running or not listening on that port.
  * Connection Timeout: The packet was likely dropped by a firewall (Security Group/IPTables) or lost in transit. The client waited for an `ACK` that never came.

Q2: How does MTU (Maximum Transmission Unit) affect VPN or Tunnel performance?

* Answer: Standard Ethernet MTU is 1500 bytes. When using VPNs (IPsec/Gre), headers add overhead. If the packet size exceeds the MTU, it leads to IP Fragmentation or being dropped, causing massive performance degradation or broken SSH sessions. SREs fix this by adjusting the MSS (Maximum Segment Size).

Q3: Explain "DNS Latency" in a Kubernetes environment.

* Answer: By default, K8s pods use `ndots:5` in `/etc/resolv.conf`. This means for a query like `google.com`, the internal resolver first tries `google.com.default.svc.cluster.local`, then `google.com.svc.cluster.local`, etc., before trying the external name. This can result in 5+ DNS queries for a single request, doubling latency.

***

#### 🔹 3. Architecture & Design: The Cloud Network

VPC Design Trade-offs:

* Public vs. Private Subnets: Databases should _always_ be in private subnets. Access should only be via a Bastion Host or a VPN/Direct Connect.
* NAT Gateway vs. NAT Instance: NAT Gateways are managed and scale automatically but are expensive. NAT Instances are cheaper but become a bottleneck and a SPOF (Single Point of Failure).

Service Mesh (The L7 Network):

* When you have 100+ microservices, managing networking via "Load Balancers" for every service is expensive and slow. A Service Mesh (Istio/Linkerd) uses "Sidecar Proxies" (Envoy) to handle retries, timeouts, and mTLS (mutual TLS) between services.

***

#### 🔹 4. Commands & Configs (Advanced Debugging)

**Tracing the Path**

`ping` tells you if a host is up. `mtr` (My Traceroute) tells you _where_ the packet is being dropped or slowed down across multiple hops.

Bash

```
# Run mtr to see packet loss at each hop
mtr -rw google.com
```

**Deep Packet Inspection**

When "the logs say everything is fine" but the app is failing, use `tcpdump`.

Bash

```
# Capture traffic on port 80 and save to a file for Wireshark analysis
tcpdump -i eth0 port 80 -w traffic.pcap

# Check for specific HTTP headers in real-time
tcpdump -A -i eth0 'tcp port 80 and (((ip[2:2] - ((ip[0]&0xf)<<2)) - ((tcp[12]&0xf0)>>2)) != 0)'
```

**Nginx Reverse Proxy Config (Best Practice)**

Nginx

```
upstream backend_servers {
    server 10.0.1.5:8080 max_fails=3 fail_timeout=30s;
    keepalive 32; # Keep connections open to reduce handshake overhead
}
```

***

#### 🔹 5. Troubleshooting & Debugging

Scenario: Intermittent 502 Bad Gateway from a Load Balancer.

1. Check Backend Health: Is the application crashing/restarting? (Check `uptime` or K8s restarts).
2. Check Keep-Alive Timeouts: If the Load Balancer's idle timeout is _longer_ than the application's (e.g., Gunicorn/Node.js) timeout, the app will close a connection that the LB thinks is still open.
3. Check Security Groups: Is the LB allowed to talk to the backend on the specific port?
4. Check IP Exhaustion: If using a NAT Gateway, check if you are hitting the "64k concurrent connections" limit.

***

#### 🔹 6. Production Best Practices

* Zero Trust Architecture: Do not trust traffic just because it is "inside the network." Use mTLS to verify service-to-service communication.
* Infrastructure as Code (IaC): Never manually create a route table or a VPC. One manual change can break an entire region's connectivity.
* Monitoring VPC Flow Logs: Use Flow Logs to analyze rejected traffic. It is the fastest way to find misconfigured firewalls.
* Anti-Pattern: Using `/16` for everything. It leads to overlapping IP ranges when you try to peer VPCs (e.g., merging two companies or connecting to a vendor).

***

#### 🔹 Cheat Sheet / Quick Revision

| **Concept**    | **Key SRE Detail**                                                                                    |
| -------------- | ----------------------------------------------------------------------------------------------------- |
| DNS            | Recursive = Lookup for you; Authoritative = Holds the truth.                                          |
| TCP            | SYN -> SYN-ACK -> ACK. `TIME_WAIT` means the server is waiting to ensure the client got the last ACK. |
| HTTP Codes     | 4xx = Client Error (Bad request); 5xx = Server Error (Your fault).                                    |
| Load Balancing | Round Robin (Simple), Least Connections (Better for long tasks).                                      |
| CIDR           | `/32` = 1 IP; `/24` = 256 IPs; `/16` = 65,536 IPs.                                                    |

***

This is Section 3: Networking. For a DevOps/SRE, networking is the "plumbing" of the cloud. You don't need to be a CCIE, but you must understand how data moves between services, how to debug "Connection Refused" errors, and how to design secure, private networks.

***

#### 🟢 Easy: Core Connectivity

_Focus: Fundamentals of ports, protocols, and addressing._

1. What is the difference between an IP address and a MAC address?
   * _Context:_ Mention that IP works at Layer 3 (logical/routing) while MAC works at Layer 2 (physical/hardware identifier).
2. Explain the purpose of DNS (Domain Name System).
   * _Context:_ It’s the "phonebook" of the internet, translating human-readable names (`google.com`) into machine-readable IPs.
3. Name the default ports for the following protocols: HTTP, HTTPS, SSH, DNS, and MySQL.
   * _Context:_ 80, 443, 22, 53, and 3306.
4. What is a "Ping" and what protocol does it use?
   * _Context:_ It checks reachability of a host using ICMP (Internet Control Message Protocol).

***

#### 🟡 Medium: Transport & Routing

_Focus: Traffic flow, performance, and basic troubleshooting._

1. Explain the difference between TCP and UDP. When would you use one over the other?
   * _Context:_ TCP is connection-oriented/reliable (e.g., Web, SSH); UDP is connectionless/fast (e.g., Video streaming, DNS, Gaming).
2. What is a Load Balancer? Describe the difference between a Layer 4 (L4) and a Layer 7 (L7) Load Balancer.
   * _Context:_ L4 works at the Transport layer (TCP/UDP IPs and ports). L7 works at the Application layer (HTTP headers, cookies, URL paths).
3. Explain the concept of CIDR (Classless Inter-Domain Routing). What does `/24` mean?
   * _Context:_ It defines a range of IP addresses. `/24` means the first 24 bits are for the network, leaving 8 bits for hosts (256 addresses).
4. Walk me through the "Recursive DNS Resolution" process.
   * _Context:_ Explain the path: Browser → Recursive Resolver → Root Server → TLD Server → Authoritative Server.

***

#### 🔴 Hard: Advanced Architecture & Deep Troubleshooting

_Focus: Complex failures, security, and internal packet flow._

1. Explain the TCP 3-Way Handshake and the 4-Way Termination.
   * _Context:_ SYN → SYN-ACK → ACK for connection; FIN → ACK → FIN → ACK for termination. Mention why the "TIME\_WAIT" state exists.
2. What is MTU (Maximum Transmission Unit)? How can a "Path MTU Discovery" failure cause performance issues?
   * _Context:_ If a packet is larger than the MTU of a hop in the path, it must be fragmented or dropped. This is a common cause of "Connection hanging" after the initial handshake.
3. Scenario: A user reports that an application is "slow." You suspect a networking bottleneck. What tools and steps do you use to diagnose this?
   * _Context:_ Mention `mtr` (My Traceroute) for latency/packet loss, `tcpdump` or `wireshark` for packet analysis, and `netstat/ss` to check for socket saturation.
4. Explain NAT (Network Address Translation) and why a "NAT Gateway" is needed for private subnets in AWS/GCP.
   * _Context:_ Private IPs are not routable on the public internet. A NAT Gateway allows outbound traffic for updates/API calls while keeping the instances hidden from inbound public traffic.

***

***

#### 💡 Pro-Tip for your Interview

When asked "What happens when you type `google.com` in your browser?", don't just say "It opens the page."

* The SRE Answer: Start with the Local Cache, move to DNS resolution, mention the TCP Handshake, the TLS Handshake (SSL certificate exchange), the HTTP GET request, and finally how the Load Balancer routes the request to a healthy backend pod. This shows "full-stack" networking knowledge.

---

## 🔷 Enterprise Networking & Performance Tuning (7 YOE)

If you are interviewing for a Senior or Staff position, knowing basic OSI layers is insufficient. You will be evaluated on your ability to design global traffic engineering and understand protocol internals.

**Continue your preparation with this advanced module:**

1. `[NEW]` [Enterprise Networking & Advanced Protocols](./enterprise-networking-and-protocols.md): BGP/Anycast architecture, HTTP/3 (QUIC) internals, gRPC frame multiplexing, P99 tail latency optimization, and network forensics.
