# Core Networking Fundamentals

## Why Networking Matters for DevOps

### Key Responsibilities

**Infrastructure Design**
- Design and implement infrastructure supporting software development and deployment
- Set up networks, configure routers and firewalls
- Ensure servers and devices are properly connected
- Understanding networking protocols and infrastructure design principles is essential for efficient and scalable infrastructure

**Application Deployment**
- Deploy applications to production environments
- Set up and configure servers, load balancers, and network components
- Ensure application runs smoothly and reliably
- Configure network components and resolve network-related issues during deployment

**Automation**
- Automate processes to improve efficiency and reduce errors
- Use networking automation tools (Ansible, Puppet) to automate network device configuration
- Understanding networking protocols and automation tools is essential

**Monitoring**
- Monitor and maintain infrastructure and applications
- Monitor network traffic, identify bottlenecks and performance issues
- Troubleshoot network-related problems
- Understanding networking protocols and tools is essential for timely issue resolution

---

## The OSI Model

The OSI (Open Systems Interconnection) model is a conceptual framework for understanding how data is transmitted across a network. It consists of **7 layers**:

| Layer | Name | PDU | Key Protocols | Devices | Primary Functions |
|-------|------|-----|---------------|---------|-------------------|
| 7 | Application | Data | HTTP, HTTPS, DNS, FTP, SMTP, SSH | - | User-facing services, network interface to applications |
| 6 | Presentation | Data | TLS, SSL, JPEG, MPEG, ASCII | - | Data translation, encryption, compression |
| 5 | Session | Data | NetBIOS, RPC, SIP | - | Session management, dialog control, synchronization |
| 4 | Transport | Segment/Datagram | TCP, UDP, SCTP | - | End-to-end delivery, flow control, error control, segmentation |
| 3 | Network | Packet | IP, ICMP, ARP, BGP, OSPF | Router | Logical addressing, routing, congestion control |
| 2 | Data Link | Frame | Ethernet, 802.11, 802.1Q (VLAN) | Switch, Bridge | Physical addressing (MAC), framing, error detection, access control |
| 1 | Physical | Bits | Copper, Fiber, Radio | Hub, NIC, Repeater | Physical transmission, voltage levels, bit synchronization |

**Mnemonic (Top → Bottom):** **A**ll **P**eople **S**eem **T**o **N**eed **D**ata **P**rocessing

**Mnemonic (Bottom → Top):** **P**lease **D**o **N**ot **T**hrow **S**ausage **P**izza **A**way

---

### Layer Functions in Detail

#### Layer 1: Physical Layer

Handles the physical characteristics of network connections:
- Physical characteristics of interfaces and media
- Representation of bits (encoding schemes)
- Data rate control
- Synchronization of bits
- Line configuration (point-to-point or multi-point)
- Transmission mode (simplex, half-duplex, full-duplex)
- Physical topology (bus, star, ring, mesh)

**Devices:** Hubs, repeaters, network adapters, cables (Cat5e/Cat6/fiber)

#### Layer 2: Data Link Layer

Provides node-to-node data transfer on the same network segment:
- Framing (encapsulating packets into frames)
- Physical addressing (MAC addresses)
- Error control (CRC checksums)
- Flow control (PAUSE frames)
- Access control (CSMA/CD for Ethernet)

**Sublayers:**
- **LLC (Logical Link Control):** Interfaces with network layer
- **MAC (Media Access Control):** Controls access to physical medium

**Devices:** Switches, bridges, network interface cards

#### Layer 3: Network Layer

Handles routing across multiple networks:
- Routing (determining optimal paths)
- Logical addressing (IP addresses)
- Congestion control
- Billing/accounting for network usage
- Fragmentation and reassembly

**Devices:** Routers, Layer 3 switches

#### Layer 4: Transport Layer

Provides end-to-end communication between applications:
- Service point addressing (port numbers)
- Segmentation and reassembly of data
- Flow control (sliding window)
- Error control (retransmission, ACKs)
- Connection-oriented (TCP) or connectionless (UDP) service

#### Layer 5: Session Layer

Manages sessions between applications:
- Dialog control (simplex, half-duplex, full-duplex)
- Synchronization (checkpoints for long transfers)
- Session establishment, maintenance, and termination

#### Layer 6: Presentation Layer

Handles data representation and security:
- Data encoding (ASCII, UTF-8, Base64)
- Encryption/decryption (TLS, SSL)
- Compression/decompression
- Data translation between application and network formats

#### Layer 7: Application Layer

Provides network services directly to applications:
- File transfer (FTP, TFTP, SCP)
- Mail services (SMTP, POP3, IMAP)
- Directory services (LDAP, DNS)
- Remote access (SSH, Telnet)
- Web services (HTTP, HTTPS)

---

## TCP/IP Reference Model

The TCP/IP model is the actual deployed protocol suite powering the internet. It compresses the 7 OSI layers into **4 layers**:

| TCP/IP Layer | OSI Equivalent | Key Protocols |
|--------------|----------------|---------------|
| Application | L5 + L6 + L7 | HTTP, HTTPS, DNS, FTP, SMTP, SSH, TLS |
| Transport | L4 | TCP, UDP, SCTP, DCCP |
| Internet | L3 | IPv4, IPv6, ICMP, ICMPv6, ARP |
| Network Access | L1 + L2 | Ethernet, 802.11 Wi-Fi, PPP, SLIP |

### TCP/IP vs OSI Model Comparison

```
OSI Model                    TCP/IP Model
┌─────────────────┐         ┌─────────────────┐
│  Application    │         │                 │
│  Presentation   │  ────→  │   Application   │
│  Session        │         │                 │
├─────────────────┤         ├─────────────────┤
│  Transport      │         │   Transport     │
├─────────────────┤         ├─────────────────┤
│  Network        │         │   Internet      │
├─────────────────┤         ├─────────────────┤
│  Data Link      │  ────→  │  Network Access │
│  Physical       │         │                 │
└─────────────────┘         └─────────────────┘
```

---

## The IP Protocol

### Overview

At the network layer, the Internet can be viewed as a collection of subnetworks or **Autonomous Systems (AS)** connected together. The network layer protocol used for the Internet is **Internet Protocol (IP)**.

**Key Characteristics:**
- Best-effort delivery (no guarantees)
- Connectionless (each packet routed independently)
- No inherent error recovery (relies on upper layers)

### How IP Communication Works

1. Datagram received from Transport layer
2. Transmitted through the Internet
3. Possibly fragmented into smaller units as it traverses networks
4. When all pieces reach the destination, they are reassembled by the network layer into the original datagram

### IP Datagram Structure

An IP datagram is a variable-length packet (up to 65,535 bytes) consisting of two parts:

```
┌─────────────────────────────────────────────────────────┐
│                      HEADER                             │
│              (20-60 bytes, contains routing             │
│               and delivery information)                 │
├─────────────────────────────────────────────────────────┤
│                      DATA                               │
│              (payload from upper layers)                │
└─────────────────────────────────────────────────────────┘
```

---

## IPv4 Header Fields

| Field | Size | Purpose |
|-------|------|---------|
| **Version** | 4 bits | IP version number (4=IPv4, binary 0100) |
| **Header Length (IHL)** | 4 bits | Header length in 32-bit word multiples (0-15 × 4 = max 60 bytes) |
| **Service Type / DSCP** | 8 bits | Priority and type of service (throughput, reliability, delay) |
| **Total Length** | 16 bits | Total datagram length (header + data), max 65,535 bytes |
| **Identification** | 16 bits | Fragment identification for reassembly |
| **Flags** | 3 bits | Fragmentation control (DF, MF bits) |
| **Fragment Offset** | 13 bits | Position of fragment in original datagram |
| **Time to Live (TTL)** | 8 bits | Hop count before discard; each router decrements by 1 |
| **Protocol** | 8 bits | Upper-layer protocol (1=ICMP, 6=TCP, 17=UDP) |
| **Header Checksum** | 16 bits | Header integrity check only (not data) |
| **Source Address** | 32 bits | Sender's IP address |
| **Destination Address** | 32 bits | Receiver's IP address |
| **Options** | Variable | Control, routing, timing, management, alignment |
| **Padding** | Variable | Ensures header ends on 32-bit boundary |

### Field Deep-Dives

**Time to Live (TTL)**
- Prevents datagrams from circulating forever
- Source sets initial value (commonly 64, 128, or 255)
- Each router decrements by 1
- When TTL = 0, datagram is discarded and ICMP "Time Exceeded" sent to source

**Protocol Field Values**
| Value | Protocol |
|-------|----------|
| 1 | ICMP |
| 2 | IGMP |
| 6 | TCP |
| 17 | UDP |
| 41 | IPv6 (tunneling) |
| 47 | GRE |
| 50 | ESP (IPsec) |
| 51 | AH (IPsec) |
| 89 | OSPF |

---

## IP Addressing

### IPv4 Address Structure

An IPv4 address is a **32-bit** number, typically written in dotted-decimal notation:
- Example: `192.168.1.10`
- Each octet ranges from 0-255

### IPv4 Address Classes

| Class | Leading Bits | First Octet | Network/Host Split | Default Mask | Networks | Hosts/Network |
|-------|--------------|-------------|--------------------|--------------|----------|---------------|
| **A** | 0 | 1-126 | 8/24 | 255.0.0.0 (/8) | 126 | 16,777,214 |
| **B** | 10 | 128-191 | 16/16 | 255.255.0.0 (/16) | 16,384 | 65,534 |
| **C** | 110 | 192-223 | 24/8 | 255.255.255.0 (/24) | 2,097,152 | 254 |
| **D** | 1110 | 224-239 | N/A | N/A | Multicast |
| **E** | 1111 | 240-255 | N/A | N/A | Reserved (future use) |

**Special Addresses:**
- `127.0.0.0/8` — Loopback (localhost)
- `0.0.0.0` — Unspecified / default route
- `255.255.255.255` — Limited broadcast (never routed)
- `169.254.0.0/16` — APIPA / link-local (DHCP failure)
- `224.0.0.0/4` — Multicast range

### Private Address Ranges (RFC 1918)

| Range | CIDR | Common Use |
|-------|------|------------|
| 10.0.0.0 – 10.255.255.255 | 10.0.0.0/8 | Large corporate networks, VPCs |
| 172.16.0.0 – 172.31.255.255 | 172.16.0.0/12 | Docker default, mid-size networks |
| 192.168.0.0 – 192.168.255.255 | 192.168.0.0/16 | Home networks, small offices |

---

## MAC Address Fundamentals

### What is a MAC Address?

A **Media Access Control (MAC)** address is a 48-bit hardware identifier burned into a Network Interface Card (NIC) by the manufacturer.

**Characteristics:**
- Also known as: Physical Address, Hardware Address, BIA (Burned In Address)
- Worldwide unique — no two devices should have the same MAC
- Displayed in hexadecimal notation: `aa:bb:cc:dd:ee:ff`
- Structure: 48 bits = 12 hex digits
  - First 24 bits: **OUI** (Organizationally Unique Identifier) — manufacturer code
  - Last 24 bits: NIC/vendor-specific serial number
- Works at the Data Link Layer (Layer 2) of the OSI model
- Provided by manufacturer, embedded in NIC

### Types of MAC Addresses

| Type | LSB of First Octet | Description | Use Case |
|------|--------------------|-------------|----------|
| **Unicast** | 0 | Sent to one specific NIC | Normal point-to-point communication |
| **Multicast** | 1 | Sent to a group of NICs | Video streaming, group communication |
| **Broadcast** | All 1s (`ff:ff:ff:ff:ff:ff`) | Sent to all devices on segment | ARP requests, DHCP discovery |

**Unicast MAC Address**
- Identifies a specific network NIC
- Packet is received only by the intended interface
- Source MAC is always unicast

**Multicast MAC Address**
- Allows one-to-many communication
- First 3 bits of first octet set to 1
- Remaining 24 bits identify the multicast group

**Broadcast MAC Address**
- Received by all devices on the LAN segment
- Used for ARP requests, DHCP discovery
- Format: `FF-FF-FF-FF-FF-FF`

---

## Address Resolution Protocol (ARP)

### Purpose

ARP associates an IP address with a physical (MAC) address on a local network.

### How ARP Works

```
┌─────────┐                              ┌─────────┐
│  Host A │                              │  Host B │
│ 192.168.1.10                            │ 192.168.1.20
│ MAC: AA:BB:CC:DD:EE:01                  │ MAC: AA:BB:CC:DD:EE:02
└────┬────┘                              └────┬────┘
     │                                        │
     │  1. ARP Request (Broadcast)            │
     │  "Who has 192.168.1.20?"               │
     │  "Tell 192.168.1.10"                   │
     │───────────────────────────────────────>│
     │                                        │
     │  2. ARP Reply (Unicast)                │
     │  "192.168.1.20 is at AA:BB:CC:DD:EE:02"│
     │<───────────────────────────────────────│
     │                                        │
     │  3. Cache updated                      │
     │  Now can send data directly            │
     │                                        │
```

**Steps:**
1. Host needs to send to an IP on the same network
2. Checks ARP cache for MAC mapping
3. If not found, broadcasts ARP Request: "Who has X.X.X.X? Tell Y.Y.Y.Y"
4. Every host receives and processes the ARP packet
5. Only the intended recipient recognizes its IP and sends back its MAC
6. Sender updates ARP cache and sends the datagram

### ARP Commands

```bash
# View ARP cache
arp -a
ip neigh show

# Add static ARP entry
arp -s 192.168.1.20 aa:bb:cc:dd:ee:ff

# Delete ARP entry
arp -d 192.168.1.20

# Clear entire ARP cache
arp -a -d
```

### ARP Variants

**Gratuitous ARP**
- Host broadcasts its own IP-to-MAC mapping without being asked
- Used to:
  - Announce MAC change after NIC replacement
  - Implement failover (VRRP/keepalived VIP handoff)
  - Detect IP conflicts

**Proxy ARP**
- Router responds to ARP requests on behalf of hosts in different subnets
- Allows hosts without default gateway to reach remote hosts
- Mostly legacy now

**ARP Spoofing (MITM Attack)**
- Attacker sends forged ARP replies to poison caches
- Traffic is redirected through attacker
- Defense: Dynamic ARP Inspection (DAI) on enterprise switches

---

## Reverse ARP (RARP)

### Purpose

RARP allows a host to discover its IP address when it knows only its MAC address.

### Why RARP Exists

- Diskless workstations know their MAC but not IP
- IP address not stored locally
- RARP server maintains mapping of MAC → IP

### How RARP Works

1. Host broadcasts RARP query: "Who knows the IP for MAC AA:BB:CC:DD:EE:01?"
2. RARP server receives the query
3. Server looks up MAC in its table
4. Server responds with the IP address
5. Host configures itself with the received IP

**Note:** RARP is obsolete, replaced by **BOOTP** and **DHCP**.

---

## Internet Control Message Protocol (ICMP)

### Purpose

ICMP is used by hosts and routers to send notification of datagram problems back to the sender.

**Key Points:**
- IP is unreliable and connectionless
- ICMP allows IP to inform sender if a datagram is undeliverable
- Reports problems, does not correct them
- Can only send messages to the source (not intermediate routers)

### Common ICMP Messages

| Type | Name | Description |
|------|------|-------------|
| 0 | Echo Reply | Response to ping |
| 3 | Destination Unreachable | Network, host, port, or protocol unreachable |
| 5 | Redirect | Suggest better route |
| 8 | Echo Request | Ping request |
| 11 | Time Exceeded | TTL expired (used by traceroute) |
| 12 | Parameter Problem | Invalid IP header |

### ICMP in Practice

```bash
# Ping (uses ICMP Echo Request/Reply)
ping google.com

# Traceroute (uses ICMP Time Exceeded)
traceroute google.com
tracepath google.com

# Combined tool
mtr google.com
```

---

## Network Topologies

### Physical vs Logical Topology

| Type | Description |
|------|-------------|
| **Physical** | Actual physical arrangement of cables and devices |
| **Logical** | How data flows through the network (signal path) |

### Physical Topology Types

#### 1. Bus Topology
- Single cable (backbone) links all components
- Server is one of the computers in the network
- Linear design with two endpoints
- **Pros:** Simple, inexpensive
- **Cons:** Single point of failure, difficult to troubleshoot

#### 2. Ring Topology
- Each device has exactly two neighbors
- Forms a closed loop
- Uses token passing for transmission
- All messages travel in same direction
- **Pros:** No collisions, predictable performance
- **Cons:** Single break disables entire network

#### 3. Star Topology
- All machines linked to a central hub/switch
- Most common for LANs
- **Pros:** Easy to set up, one failure doesn't bring down network
- **Cons:** Central hub is single point of failure

#### 4. Tree Topology
- Base node connects all other nodes in hierarchy
- Also called "hierarchy geometry"
- Combines multiple star topologies (Star Bus)
- **Pros:** Scalable, easy fault isolation
- **Cons:** Complex, dependent on root

#### 5. Mesh Topology
- Every computer communicates with every other computer
- Point-to-point links between all devices
- **Pros:** High redundancy, multiple paths
- **Cons:** Expensive, complex cabling

#### 6. Hybrid Topology
- Combines two or more different topologies
- Example: Star + Mesh in different sections
- **Pros:** Flexible, scalable
- **Cons:** Complex design and management

---

## Summary: Key Takeaways

| Concept | Key Point |
|---------|-----------|
| OSI Model | 7 layers for understanding network communication |
| TCP/IP | 4-layer model actually used on the internet |
| IP Datagram | Header (20-60 bytes) + Data (up to 65,535 bytes total) |
| IPv4 Classes | A (large), B (medium), C (small), D (multicast), E (reserved) |
| MAC Address | 48-bit hardware identifier, globally unique |
| ARP | Maps IP → MAC on local network |
| RARP | Maps MAC → IP (obsolete, replaced by DHCP) |
| ICMP | Error reporting and diagnostics (ping, traceroute) |
| Topologies | Bus, Ring, Star, Tree, Mesh, Hybrid |
