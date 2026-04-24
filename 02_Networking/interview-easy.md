# Networking Interview Questions — Easy

Fundamental concepts for entry-level DevOps networking interviews.

***

## 1. What is the OSI model?

**Answer:**
The OSI (Open Systems Interconnection) model is a 7-layer conceptual framework for understanding how data moves across a network:

| Layer | Name | Key Protocols |
|-------|------|---------------|
| 7 | Application | HTTP, HTTPS, DNS, FTP, SMTP |
| 6 | Presentation | TLS, SSL, JPEG, ASCII |
| 5 | Session | NetBIOS, RPC, SIP |
| 4 | Transport | TCP, UDP |
| 3 | Network | IP, ICMP, ARP |
| 2 | Data Link | Ethernet, 802.11, VLAN |
| 1 | Physical | Copper, Fiber, Radio |

**Mnemonic:** **A**ll **P**eople **S**eem **T**o **N**eed **D**ata **P**rocessing

**Why it matters:** Helps pinpoint where failures occur (e.g., physical cable issue at Layer 1 vs. application error at Layer 7).

***

## 2. What is the difference between TCP and UDP?

**Answer:**

| Feature | TCP | UDP |
|---------|-----|-----|
| Connection | Connection-oriented (3-way handshake) | Connectionless |
| Reliability | Guaranteed delivery + retransmission | Best-effort, no retransmission |
| Ordering | In-order delivery guaranteed | No ordering guarantee |
| Flow control | Yes (sliding window) | No |
| Speed | Slower (overhead for reliability) | Faster (minimal overhead) |
| Header size | 20-60 bytes | 8 bytes |
| Use cases | HTTP, SSH, databases, file transfer | DNS, VoIP, streaming, gaming |

**When to use:**
- **TCP:** Web browsing, email, file transfer, databases (need reliability)
- **UDP:** Video streaming, online gaming, DNS lookups (speed over perfect delivery)

***

## 3. What is a subnet mask?

**Answer:**
A subnet mask defines which portion of an IP address is the **network** and which is the **host**.

**Example:** `255.255.255.0` (or `/24` in CIDR notation)
- First 24 bits = network portion
- Last 8 bits = host portion (254 usable hosts)

**Purpose:**
- Determines if a destination IP is on the same local network or requires routing
- Used by devices to decide whether to send directly or via gateway

***

## 4. What is a CIDR block?

**Answer:**
CIDR (Classless Inter-Domain Routing) notation compresses an IP address and its mask into a single notation.

**Format:** `IP_address/prefix_length`

**Examples:**
| CIDR | Subnet Mask | Addresses | Usable Hosts |
|------|-------------|-----------|--------------|
| 10.0.0.0/8 | 255.0.0.0 | 16,777,216 | 16,777,214 |
| 172.16.0.0/16 | 255.255.0.0 | 65,536 | 65,534 |
| 192.168.1.0/24 | 255.255.255.0 | 256 | 254 |
| 192.168.1.0/26 | 255.255.255.192 | 64 | 62 |

**Why it matters:** Efficient IP allocation and routing table aggregation.

***

## 5. What is NAT?

**Answer:**
NAT (Network Address Translation) maps private IP addresses to a public IP address, allowing multiple devices to share one public IP.

**How it works:**
1. Internal device sends request from private IP (e.g., 192.168.1.100)
2. NAT router replaces source IP with public IP
3. Router tracks the mapping in NAT table
4. Response comes back to public IP
5. Router forwards to original private IP

**Types:**
- **SNAT (Source NAT):** For outbound traffic (private → public)
- **DNAT (Destination NAT):** For inbound traffic (public → private)
- **PAT (Port Address Translation):** Many private IPs share one public IP using different ports

**Use cases:**
- Home routers (multiple devices share one ISP-provided IP)
- Cloud NAT Gateways (private subnets access internet)
- IPv4 address conservation

***

## 6. What is DNS and how does resolution work?

**Answer:**
DNS (Domain Name System) translates human-readable domain names to machine-readable IP addresses.

**Resolution Process:**
```
1. Client checks local cache
2. Query to recursive resolver (ISP/8.8.8.8)
3. Recursive resolver queries Root nameserver
4. Root refers to TLD nameserver (.com, .org, etc.)
5. TLD refers to Authoritative nameserver
6. Authoritative returns the IP address
7. Result cached and returned to client
```

**Record Types:**
| Type | Purpose |
|------|---------|
| A | IPv4 address |
| AAAA | IPv6 address |
| CNAME | Alias |
| MX | Mail server |
| TXT | Text records (SPF, DKIM) |
| NS | Nameserver |

***

## 7. What is the difference between HTTP and HTTPS?

**Answer:**

| Feature | HTTP | HTTPS |
|---------|------|-------|
| Port | 80 | 443 |
| Encryption | None (plaintext) | TLS/SSL encryption |
| Certificate | Not required | Required (from CA) |
| Security | Vulnerable to eavesdropping | Encrypted, authenticated |
| Performance | Faster (no handshake) | Slightly slower (TLS overhead) |
| SEO | Lower ranking | Preferred by search engines |

**HTTPS provides:**
- **Confidentiality:** Data encrypted in transit
- **Integrity:** Data cannot be modified without detection
- **Authentication:** Server identity verified via certificate

***

## 8. What is a load balancer and what are the types?

**Answer:**
A load balancer distributes incoming traffic across multiple backend servers.

**Types:**

| Type | Layer | Routes Based On | Examples |
|------|-------|-----------------|----------|
| **Layer 4** | Transport | IP address + port | AWS NLB, HAProxy (TCP mode) |
| **Layer 7** | Application | URL path, headers, cookies | AWS ALB, Nginx, Traefik |

**L4 vs L7:**
- **L4:** Faster, simpler, no HTTP awareness
- **L7:** Can route `/api/*` to one backend, `/static/*` to another

**Algorithms:**
- Round Robin
- Least Connections
- IP Hash (sticky sessions)
- Weighted (based on server capacity)

***

## 9. What is a firewall and what does it filter on?

**Answer:**
A firewall controls which network traffic is allowed or denied based on rules.

**Types:**

| Type | Characteristics |
|------|-----------------|
| **Stateless** | Filters each packet independently; must allow return traffic explicitly |
| **Stateful** | Tracks connection state; automatically allows replies |
| **NGFW** (Next-Gen) | Layer 7 inspection, application awareness, IPS |

**Filter Criteria:**
- Source/destination IP address
- Source/destination port
- Protocol (TCP, UDP, ICMP)
- Connection state (NEW, ESTABLISHED, RELATED)
- Application (NGFW only)

**Examples:** iptables, security groups (AWS), NSGs (Azure)

***

## 10. What is the purpose of the `traceroute` command?

**Answer:**
`traceroute` shows the path packets take to reach a destination, listing each hop (router) with its IP and round-trip latency.

**How it works:**
1. Sends packets with increasing TTL (Time to Live)
2. First packet: TTL=1, first router decrements to 0, sends "Time Exceeded" ICMP back
3. Second packet: TTL=2, second router responds
4. Continues until destination is reached

**Output:**
```
$ traceroute google.com
1  192.168.1.1 (1 ms)
2  10.0.0.1 (5 ms)
3  72.14.215.85 (12 ms)
4  ...
```

**Use cases:**
- Identify where packet loss occurs
- Find routing issues
- Diagnose high latency at specific hops

**Alternatives:** `tracepath` (no root needed), `mtr` (real-time traceroute + ping)

***

## 11. What is a VPN?

**Answer:**
A VPN (Virtual Private Network) encrypts traffic between two endpoints over a public network, making remote hosts appear to be on the same private network.

**How it works:**
1. Client establishes encrypted tunnel to VPN server
2. All traffic is encapsulated and encrypted
3. VPN server decrypts and forwards to destination
4. Response returns through tunnel

**Types:**
- **Site-to-Site:** Connects entire networks (office to cloud)
- **Remote Access:** Connects individual users (work from home)

**Protocols:**
| Protocol | Characteristics |
|----------|-----------------|
| IPsec | Industry standard, site-to-site |
| WireGuard | Modern, fast, simple |
| OpenVPN | Flexible, widely supported |
| SSL/TLS | Browser-based, no client needed |

**Use cases:**
- Secure remote access to corporate network
- Connecting on-premises to cloud (hybrid cloud)
- Bypassing geographic restrictions

***

## 12. What is a CDN?

**Answer:**
A CDN (Content Delivery Network) caches content at geographically distributed edge nodes, serving users from the nearest location.

**How it works:**
1. Content cached at edge locations worldwide
2. User requests content
3. DNS routes to nearest edge node
4. Edge serves cached content (if available)
5. If not cached, edge fetches from origin

**Benefits:**
- Reduced latency (content closer to users)
- Lower origin server load
- Better availability (distributed infrastructure)
- DDoS mitigation (absorbs traffic spikes)

**Examples:** CloudFront, Akamai, Fastly, Cloudflare

***

## 13. What is a proxy vs reverse proxy?

**Answer:**

| Feature | Forward Proxy | Reverse Proxy |
|---------|---------------|---------------|
| **Position** | Between clients and internet | Between internet and servers |
| **Client knows** | Yes, client configures proxy | No, client thinks it's the server |
| **Purpose** | Client anonymity, access control, caching | Load balancing, SSL termination, caching |
| **Represents** | Clients | Servers |

**Forward Proxy Example:**
```
Client → Proxy → Internet
(used for bypassing restrictions, anonymity)
```

**Reverse Proxy Example:**
```
Internet → Reverse Proxy → Backend Servers
(used for load balancing, SSL termination)
```

**Reverse Proxy Use Cases:**
- Load balancing across multiple backends
- SSL termination (decrypt once at proxy)
- Caching static content
- Hiding backend server identities
- Rate limiting, WAF

**Examples:** Nginx, HAProxy, Envoy

***

## Quick Reference: Default Ports

| Service | Port | Protocol |
|---------|------|----------|
| SSH | 22 | TCP |
| HTTP | 80 | TCP |
| HTTPS | 443 | TCP |
| DNS | 53 | TCP/UDP |
| MySQL | 3306 | TCP |
| PostgreSQL | 5432 | TCP |
| Redis | 6379 | TCP |
| MongoDB | 27017 | TCP |

***

## Common Interview Follow-ups

**Q: "What happens when you type google.com in your browser?"**

Expected flow:
1. Browser cache → OS cache → DNS resolver
2. DNS resolution (recursive query)
3. TCP 3-way handshake
4. TLS handshake (for HTTPS)
5. HTTP GET request
6. Server response
7. TCP connection teardown

**Q: "How do you check if a port is open?"**
```bash
telnet hostname port
nc -zv hostname port
nmap -p port hostname
```

**Q: "What does `ping` use?"**
ICMP (Internet Control Message Protocol) — specifically Echo Request and Echo Reply.
