# Routing, Subnetting, and Network Design

## Subnetting and CIDR

### What is a Subnet?

A **subnet** (subnetwork) is a smaller network inside a larger network. Subnetting makes network routing more efficient and improves security by segmenting networks.

**Why subnet?**
- Efficient routing (smaller routing tables)
- Security isolation (segment sensitive systems)
- Broadcast domain control (reduce broadcast traffic)
- Easier maintenance (smaller networks are simpler to manage)

**Example:** A Class A network has 2^24 = 16,777,214 hosts. Maintaining such a large network is challenging. Subnetting divides it into manageable sections.

---

### CIDR Notation

**CIDR** (Classless Inter-Domain Routing) is a method for allocating IP addresses and routing traffic. It replaced the old class-based system (A, B, C).

**Format:** `IP_address/prefix_length`
- Example: `10.10.1.16/32` or `192.168.1.0/24`

**Prefix Length:**
- Indicates how many bits are used for the network portion
- Remaining bits are for hosts
- Example: `/24` = 24 network bits, 8 host bits

### CIDR Quick Reference Table

| CIDR | Subnet Mask | Total Addresses | Usable Hosts | Common Use |
|------|-------------|-----------------|--------------|------------|
| /8 | 255.0.0.0 | 16,777,216 | 16,777,214 | Large ISP, Class A |
| /12 | 255.240.0.0 | 1,048,576 | 1,048,574 | Large organizations |
| /16 | 255.255.0.0 | 65,536 | 65,534 | Large org, VPC CIDR |
| /20 | 255.255.240.0 | 4,096 | 4,094 | Cloud subnet block |
| /24 | 255.255.255.0 | 256 | 254 | Standard LAN segment |
| /25 | 255.255.255.128 | 128 | 126 | Split /24 in half |
| /26 | 255.255.255.192 | 64 | 62 | Smaller segment |
| /27 | 255.255.255.224 | 32 | 30 | Small subnet |
| /28 | 255.255.255.240 | 16 | 14 | Small cloud subnet |
| /29 | 255.255.255.248 | 8 | 6 | Very small subnet |
| /30 | 255.255.255.252 | 4 | 2 | Point-to-point links |
| /31 | 255.255.255.254 | 2 | 2 | P2P (RFC 3021, no broadcast) |
| /32 | 255.255.255.255 | 1 | 1 | Single host route |

---

### How CIDR Makes Subnetting Easier

**Before CIDR:**
- Fixed class boundaries (/8, /16, /24)
- Wasteful address allocation
- Subnet masks with all zeros or all ones couldn't be used

**With CIDR:**
- Flexible prefix lengths
- Efficient address allocation
- Can use any prefix length (e.g., /27, /29, /31)

**Moving bits from host to network:**
- More network bits = more subnets, fewer hosts per subnet
- More host bits = fewer subnets, more hosts per subnet

---

### Subnetting Math

**Key Formulas:**
```
Number of subnets = 2^(bits borrowed from host portion)
Hosts per subnet = 2^(remaining host bits) - 2
```

**Why subtract 2?**
- Network address (all host bits = 0)
- Broadcast address (all host bits = 1)

---

### Worked Example: Divide 10.0.0.0/24 into 4 Subnets

**Given:** `10.0.0.0/24` (256 addresses, 254 usable)

**Goal:** Create 4 equal subnets

**Steps:**
1. Borrow 2 bits from host portion (2^2 = 4 subnets)
2. New prefix: /24 + 2 = /26
3. Each subnet has 2^(32-26) = 2^6 = 64 addresses (62 usable)

**Result:**
| Subnet | Network | Usable Range | Broadcast |
|--------|---------|--------------|-----------|
| 1 | 10.0.0.0/26 | 10.0.0.1 – 10.0.0.62 | 10.0.0.63 |
| 2 | 10.0.0.64/26 | 10.0.0.65 – 10.0.0.126 | 10.0.0.127 |
| 3 | 10.0.0.128/26 | 10.0.0.129 – 10.0.0.190 | 10.0.0.191 |
| 4 | 10.0.0.192/26 | 10.0.0.193 – 10.0.0.254 | 10.0.0.255 |

---

### VPC CIDR Design Considerations

**Important:** VPC CIDR design is permanent in most clouds. You cannot change it after creation.

**Best Practices:**
| Consideration | Recommendation |
|---------------|----------------|
| **Size** | Use /16 for VPC (65,536 IPs) to allow growth |
| **Subnet sizing** | Carve /24 subnets from /16 VPC |
| **Kubernetes** | Plan for 5x expected pod count (each pod gets an IP) |
| **Overlapping** | Never use overlapping CIDRs (blocks VPC peering) |
| **Future-proofing** | Consider M&A, multi-region, hybrid connectivity |

**Common Mistake:** Using /16 for everything leads to overlapping IP ranges when peering VPCs (e.g., merging companies or connecting to vendors).

---

## Routing Fundamentals

### What is Routing?

**Routing** is the process of selecting a path for data to travel from source to destination.

**Router:** A networking device that forwards packets using information from the packet header and routing table.

**OSI Layer:** Network Layer (Layer 3)

**TCP/IP Layer:** Internet Layer

---

### How Routing Works

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Source  │───>│ Router 1 │───>│ Router 2 │───>│Destination│
│  Host    │    │          │    │          │    │  Host    │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
                     │                 │
               Routing Table     Routing Table
               ┌───────────┐     ┌───────────┐
               │ Dest  │ Next│     │ Dest  │ Next│
               │ 10.0.0  │ eth0│     │ 192.168│ eth1│
               │ 172.16  │ eth1│     │ 10.0.0 │ eth0│
               └───────────┘     └───────────┘
```

### Routing Metrics

Routing algorithms use **metrics** to determine the best path:

| Metric | Description |
|--------|-------------|
| **Hop count** | Number of routers to cross |
| **Bandwidth** | Available capacity of the link |
| **Latency** | Time delay for packet traversal |
| **Load** | Current traffic on the channel |
| **Reliability** | Error rate of the link |
| **Cost** | Administrative value assigned to link |

---

## Types of Routing

### Static Routing (Non-Adaptive)

**Description:** Administrator manually configures routes in the routing table.

**Characteristics:**
- Routes are manually entered
- Does not adapt to network changes
- Packets follow the pre-configured path
- No routing decisions based on network conditions

**Pros:**
- Simple to configure for small networks
- No CPU overhead for routing protocols
- Predictable behavior

**Cons:**
- Doesn't adapt to failures
- Manual intervention required for changes
- Doesn't scale well

**Commands:**
```bash
# Linux - View routing table
ip route show
route -n

# Add static route
ip route add 10.0.0.0/24 via 192.168.1.1
route add -net 10.0.0.0/24 gw 192.168.1.1

# Delete route
ip route del 10.0.0.0/24 via 192.168.1.1
```

---

### Default Routing

**Description:** A catch-all route used when no specific route matches the destination.

**Use Cases:**
- Networks with a single exit point (e.g., home network → ISP)
- When many networks must send data to the same next-hop device
- Stub networks (only one path out)

**Configuration:**
```bash
# Set default gateway
ip route add default via 192.168.1.1
route add default gw 192.168.1.1

# View default route
ip route show | grep default
```

**Priority:** Specific routes take precedence over the default route.

---

### Dynamic Routing (Adaptive)

**Description:** Router automatically creates/updates routes based on network state and topology changes.

**Characteristics:**
- Uses routing protocols (RIP, OSPF, BGP, EIGRP)
- Automatically adjusts to network changes
- If a path fails, automatically finds alternate route

**Pros:**
- Automatic failover
- Scales to large networks
- Adapts to topology changes

**Cons:**
- CPU and bandwidth overhead
- More complex configuration
- Potential for routing loops during convergence

**Protocols:**
| Protocol | Type | Use Case |
|----------|------|----------|
| **RIP** | Distance Vector | Small networks (legacy) |
| **OSPF** | Link State | Enterprise networks |
| **EIGRP** | Hybrid | Cisco environments |
| **BGP** | Path Vector | Internet routing, multi-cloud |

---

## Routing Algorithms

### Distance Vector Routing

**How it works:**
- All routers regularly communicate with neighbors
- Each router transmits its current cost estimate to all known destinations
- Routers update their tables based on neighbor information
- Eventually, all routers find optimal paths

**Characteristics:**
- Periodic updates (even if no changes)
- Slow convergence
- prone to routing loops (solved by split horizon, poison reverse)

**Protocols:** RIP, IGRP

**Bellman-Ford Equation:**
```
D_x(y) = min_v { c(x,v) + D_v(y) }
```
Where:
- `D_x(y)` = cost from x to y
- `c(x,v)` = cost from x to neighbor v
- `D_v(y)` = cost from v to y (as reported by v)

---

### Link State Routing

**How it works:**
- Every router discovers all other routers in the network
- Each router builds a complete map (topology) of the network
- Uses Dijkstra's algorithm to compute shortest path tree

**Process:**
1. Discover neighbors and measure link costs
2. Create Link State Packet (LSP) with this information
3. Flood LSP to all routers
4. Build complete topology map (LSDB - Link State Database)
5. Run Dijkstra's SPF algorithm to compute shortest paths

**Characteristics:**
- Fast convergence
- Only sends updates when topology changes
- More CPU/memory intensive than distance vector

**Protocols:** OSPF, IS-IS

**Dijkstra's Algorithm:**
```
1. Initialize: Set source node distance to 0, all others to infinity
2. Select node with minimum tentative distance
3. Update distances to neighbors: if shorter path found, update
4. Mark node as visited
5. Repeat until all nodes visited
```

---

### Comparison: Distance Vector vs Link State

| Feature | Distance Vector | Link State |
|---------|-----------------|------------|
| **Knowledge** | Knows only neighbors | Knows entire topology |
| **Updates** | Periodic, full table | Event-triggered, LSP only |
| **Convergence** | Slow (count-to-infinity) | Fast |
| **CPU Usage** | Low | High (SPF calculation) |
| **Memory** | Low | High (topology map) |
| **Routing Loops** | Possible | Rare |
| **Example** | RIP | OSPF |

---

## Routing Protocols in Detail

### OSPF (Open Shortest Path First)

**Type:** Link State IGP (Interior Gateway Protocol)

**Algorithm:** Dijkstra's SPF

**Metric:** Cost (based on bandwidth)

**How OSPF Works:**
1. Routers discover neighbors via Hello packets
2. Establish adjacencies with neighbors
3. Flood Link State Advertisements (LSAs)
4. Build identical Link State Database (LSDB)
5. Run SPF algorithm to compute shortest path tree
6. Populate routing table

**OSPF Areas:**
- Used to limit LSA flooding scope
- **Area 0:** Backbone area (all areas must connect to it)
- **Non-zero areas:** Connect to Area 0 via ABR (Area Border Router)
- Reduces routing table size and SPF computation

**OSPF Packet Types:**
| Type | Name | Purpose |
|------|------|---------|
| 1 | Hello | Discover/maintain neighbors |
| 2 | DBD | Database Description |
| 3 | LSR | Link State Request |
| 4 | LSU | Link State Update |
| 5 | LSAck | Link State Acknowledgment |

---

### BGP (Border Gateway Protocol)

**Type:** Path Vector EGP (Exterior Gateway Protocol)

**Purpose:** Inter-AS (Autonomous System) routing

**The protocol that holds the Internet together**

**Key Concepts:**

| Term | Description |
|------|-------------|
| **AS (Autonomous System)** | Network under single administrative control |
| **ASN** | AS Number (16-bit: 1-65535, 32-bit extensions) |
| **eBGP** | BGP between different ASes |
| **iBGP** | BGP within the same AS |

**BGP Path Selection (in order):**
1. Highest **Weight** (Cisco proprietary, local to router)
2. Highest **LOCAL_PREF** (default 100)
3. Locally originated routes preferred
4. Shortest **AS_PATH**
5. Lowest **ORIGIN** (IGP < EGP < Incomplete)
6. Lowest **MED** (Multi-Exit Discriminator)
7. **eBGP over iBGP**
8. Lowest IGP metric to BGP next-hop
9. Lowest BGP router ID (tiebreaker)

**BGP in DevOps:**
- **AWS Direct Connect:** On-prem to AWS via BGP
- **Azure ExpressRoute:** On-prem to Azure via BGP
- **GCP Cloud Interconnect:** On-prem to GCP via BGP
- **Kubernetes (Calico/Cilium):** Advertise pod CIDR via BGP

---

## Network Topologies

### Physical vs Logical Topology

| Type | Description |
|------|-------------|
| **Physical Topology** | Actual physical arrangement of cables, devices, and network components |
| **Logical Topology** | How data actually flows through the network (signal path) |

---

### Bus Topology

```
[Server]====[PC1]====[PC2]====[PC3]====[PC4]
              |        |        |        |
           (All connected to single backbone cable)
```

**Characteristics:**
- Single cable (backbone) links all components
- Linear design with two endpoints
- Terminators required at ends

| Pros | Cons |
|------|------|
| Simple, inexpensive | Single point of failure |
| Easy to extend | Difficult to troubleshoot |
| Minimal cabling | Performance degrades with load |

---

### Ring Topology

```
       [PC1]
      /     \
   [PC4]     [PC2]
      \     /
       [PC3]
```

**Characteristics:**
- Each device has exactly two neighbors
- Forms a closed loop
- Uses token passing for transmission
- All messages travel in same direction

| Pros | Cons |
|------|------|
| No collisions | Single break disables network |
| Predictable performance | Difficult to add/remove devices |
| Equal access | Troubleshooting is difficult |

---

### Star Topology

```
         [Hub/Switch]
        /    |    |    \
     [PC1] [PC2] [PC3] [PC4]
```

**Characteristics:**
- All machines linked to central hub/switch
- Most common for LANs

| Pros | Cons |
|------|------|
| Easy to set up and manage | Central hub is SPOF |
| One failure doesn't bring down network | Requires more cabling |
| Easy troubleshooting | Hub/switch cost |
| Cheap | |

---

### Tree Topology

```
          [Root Switch]
         /           \
    [Switch A]    [Switch B]
    /   |   \      /   |   \
  [PC1][PC2][PC3][PC4][PC5][PC6]
```

**Characteristics:**
- Base node connects all other nodes in hierarchy
- Also called "hierarchy geometry"
- Combines multiple star topologies (Star Bus)

| Pros | Cons |
|------|------|
| Scalable | Complex design |
| Easy fault isolation | Dependent on root |
| Point-to-point wiring | Requires more cabling |

---

### Mesh Topology

```
[PC1]──[PC2]
  │ \  /  │
  │  \/   │
  │  /\   │
  │ /  \  │
[PC3]──[PC4]
```

**Characteristics:**
- Every device connects to every other device
- Point-to-point links between all devices
- Full mesh: n(n-1)/2 links for n devices

| Pros | Cons |
|------|------|
| Maximum redundancy | Very expensive |
| Multiple paths | Complex cabling |
| No single point of failure | Difficult to manage |
| High reliability | |

---

### Hybrid Topology

```
[Star Network]=====[Ring Network]
        |
     [Mesh Network]
```

**Characteristics:**
- Combines two or more different topologies
- Resulting network doesn't follow conventional topology

| Pros | Cons |
|------|------|
| Flexible | Complex design |
| Scalable | Expensive |
| Reliable | Requires intelligent hardware |

---

## Practical Subnetting Examples

### Example 1: Design Subnets for a Company

**Requirements:**
- Network: 192.168.0.0/16
- Need subnets for: HQ (500 hosts), Branch1 (100 hosts), Branch2 (50 hosts), IT Lab (20 hosts)

**Solution:**

| Department | Hosts Needed | CIDR | Subnet Mask | Address Range |
|------------|--------------|------|-------------|---------------|
| HQ | 500 | /23 | 255.255.254.0 | 192.168.0.0 – 192.168.1.255 |
| Branch1 | 100 | /25 | 255.255.255.128 | 192.168.2.0 – 192.168.2.127 |
| Branch2 | 50 | /26 | 255.255.255.192 | 192.168.2.128 – 192.168.2.191 |
| IT Lab | 20 | /27 | 255.255.255.224 | 192.168.2.192 – 192.168.2.223 |

---

### Example 2: VPC Subnet Design for AWS

**VPC CIDR:** 10.0.0.0/16 (65,536 IPs)

**Subnet Design (per Availability Zone):**

| Subnet Type | CIDR | Usable IPs | Purpose |
|-------------|------|------------|---------|
| Public Subnet A | 10.0.0.0/24 | 254 | Load balancers, bastion |
| Private Subnet A | 10.0.1.0/24 | 254 | Application servers |
| Database Subnet A | 10.0.2.0/24 | 254 | RDS, databases |
| Public Subnet B | 10.0.3.0/24 | 254 | Multi-AZ redundancy |
| Private Subnet B | 10.0.4.0/24 | 254 | Multi-AZ redundancy |
| Database Subnet B | 10.0.5.0/24 | 254 | Multi-AZ redundancy |

**Remaining:** 10.0.6.0/24 – 10.0.255.0/24 for future expansion

---

## Summary: Key Takeaways

| Concept | Key Point |
|---------|-----------|
| **Subnetting** | Divides large network into smaller, manageable sections |
| **CIDR** | Flexible prefix notation (e.g., /24, /26, /30) |
| **Static Routing** | Manual, doesn't adapt, simple |
| **Dynamic Routing** | Automatic, adapts to changes, complex |
| **Distance Vector** | RIP, periodic updates, slow convergence |
| **Link State** | OSPF, topology map, fast convergence |
| **BGP** | Inter-AS routing, path vector, Internet backbone |
| **OSPF** | Intra-AS routing, link state, Dijkstra's algorithm |
| **Bus Topology** | Single backbone, simple but fragile |
| **Ring Topology** | Closed loop, token passing |
| **Star Topology** | Central hub, most common for LANs |
| **Mesh Topology** | Full redundancy, expensive |
| **Tree Topology** | Hierarchical, scalable |
| **Hybrid Topology** | Combination of multiple topologies |
