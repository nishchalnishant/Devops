# Docker Networking — Deep Dive

## Why Docker Networking Exists

By default, containers are isolated processes. Without networking, they cannot communicate with each other, the host, or the outside world. Docker's networking layer provides **connectivity**, **isolation**, and **service discovery** — three pillars essential for microservices architectures.

Docker uses **Linux namespaces** (specifically the network namespace) to give each container its own isolated network stack: interfaces, routing tables, and firewall rules. The Docker daemon acts as a virtual switch, connecting containers to networks.

***

## Types of Docker Networks

### 1. Default Bridge Network (`bridge`)

The default network driver. When you run a container without specifying `--network`, it connects to `bridge`.

**Characteristics:**
- Creates a private virtual network on the host (`docker0` interface, typically `172.17.0.0/16`)
- Containers can communicate via **container names** (Docker's embedded DNS resolves names to IPs)
- Outbound internet access works by default (NAT through host)
- **Inbound** connections require port publishing (`-p 8080:80`)
- Containers on the default bridge **cannot** communicate by name unless explicitly linked (legacy) or on a user-defined bridge

**When to use:**
- Development and testing
- Single-host deployments
- Containers that don't need DNS-based service discovery

```bash
docker run --network=bridge nginx
docker network ls              # List networks
docker network inspect bridge  # See subnet, gateway, connected containers
```

**Architecture:**
```
┌─────────────────────────────────────────┐
│              Host Machine               │
│  ┌──────────┐     ┌──────────┐         │
│  │Container │─────│Container │         │
│  │   :80    │     │   :8080  │         │
│  └────┬─────┘     └────┬─────┘         │
│       │                │                │
│       └──────┬─────────┘                │
│              │ docker0 (172.17.0.1)     │
│              │ Bridge Interface         │
│              │                          │
│       ┌──────┴──────┐                   │
│       │   iptables  │  ← NAT rules      │
│       │  (masquerade)│   for outbound   │
│       └──────┬──────┘                   │
│              │ eth0 (host NIC)          │
└──────────────┼──────────────────────────┘
               │
         Internet
```

***

### 2. User-Defined Bridge Network

A custom bridge network you create. Superior to the default bridge in every way.

**Advantages over default bridge:**
- **Automatic DNS resolution** — containers resolve each other by name
- **Better isolation** — only containers on the same network can communicate
- **Dynamic attachment** — connect/disconnect containers without restarting
- **Scoping** — limit network access to specific containers

**When to use:**
- Multi-container applications (web app + database + cache)
- When you need container-to-container communication by name
- Production single-host deployments

```bash
# Create a user-defined bridge
docker network create --driver bridge --subnet 10.0.1.0/24 myapp-network

# Connect containers
docker run -d --name web --network myapp-network nginx
docker run -d --name db --network myapp-network postgres

# Containers can now ping each other by name:
docker exec web ping db   # Resolves to 10.0.1.x

# Connect a running container to a network
docker network connect myapp-network redis-container
```

***

### 3. Host Network

Containers share the host's network namespace directly. No network isolation.

**Characteristics:**
- Container uses the host's IP address — no NAT, no port mapping
- **No port publishing needed** — `docker run -p` is ignored
- **No network isolation** — container sees all host network interfaces
- Slightly better performance (no NAT overhead)
- Cannot run two containers on the same port

**When to use:**
- Performance-critical workloads (high-frequency trading, real-time streaming)
- When the container needs to bind to specific host interfaces
- Debugging network issues from inside the container

**Trade-offs:**
- ⚠️ **Security risk** — container can bind to any port, see all traffic
- ⚠️ **Port conflicts** — host and container ports must not collide
- ⚠️ **No isolation** — defeats a key container security boundary

```bash
docker run --network=host nginx
# Nginx is now accessible on host's port 80 directly
```

**Use case example:** A monitoring agent that needs to see all network traffic on the host for packet capture.

***

### 4. Overlay Network

Multi-host networking for Docker Swarm clusters. Uses **VXLAN** encapsulation.

**How it works:**
- VXLAN encapsulates Layer 2 Ethernet frames inside UDP packets (port 4789)
- Creates a virtual "flat" network across multiple physical hosts
- Containers on different hosts communicate as if on the same LAN
- Built-in service discovery via Swarm's DNS

**When to use:**
- Docker Swarm clusters
- Multi-host container communication
- When you need containers on different hosts to share a subnet

**Architecture:**
```
Host A (192.168.1.10)              Host B (192.168.1.20)
┌─────────────────────┐           ┌─────────────────────┐
│  Container A        │           │  Container B        │
│  10.0.0.2           │           │  10.0.0.3           │
│    │                │           │    │                │
│    ▼                │           │    ▼                │
│  VXLAN Tunnel       │◄─────────►│  VXLAN Tunnel       │
│  (UDP 4789)         │  Physical │  (UDP 4789)         │
│    │                │  Network  │    │                │
│  docker_gwbridge    │           │  docker_gwbridge    │
└─────────────────────┘           └─────────────────────┘
```

```bash
# Initialize Swarm (required for overlay)
docker swarm init

# Create overlay network
docker network create --driver overlay --attachable my-overlay

# Deploy service across swarm
docker service create --name web --network my-overlay -p 80:80 nginx
```

**Performance note:** VXLAN adds ~50 bytes overhead per packet (14 Ethernet + 20 IP + 8 UDP + 8 VXLAN header). On a 1500 MTU link, effective MTU becomes 1450 bytes.

***

### 5. Macvlan Network

Connects containers directly to the physical network. Containers get MAC addresses and appear as physical devices.

**Characteristics:**
- Container gets an IP from the **physical network's subnet** (not Docker's private ranges)
- Container has its own **MAC address** — visible to routers, firewalls, and other physical devices
- No NAT — direct Layer 2 connectivity
- Bypasses Docker's built-in port publishing and NAT

**When to use:**
- Legacy applications that expect to be on the physical network
- When containers need to be visible to external systems (printers, legacy servers)
- High-performance workloads that need direct network access
- Compliance scenarios requiring MAC-based ACLs

**Limitations:**
- ⚠️ Containers cannot communicate with the Docker host by default (requires a macvlan sub-interface on host)
- ⚠️ Requires network administrator coordination (IP allocation, switch port config)
- ⚠️ No built-in service discovery

```bash
# Create macvlan network
docker network create -d macvlan \
  --subnet 192.168.1.0/24 \
  --gateway 192.168.1.1 \
  -o parent=eth0 \
  my-macvlan

# Run container with physical network access
docker run --network my-macvlan --ip 192.168.1.50 nginx
```

**Security consideration:** Since containers are on the physical network, they're subject to the same network policies and monitoring as physical servers. Ensure firewall rules account for container IPs.

***

### 6. None Network

Complete network isolation. The container has only a loopback interface (`lo`).

**Characteristics:**
- No network interfaces except `lo` (127.0.0.1)
- No internet access, no container communication
- Maximum network isolation

**When to use:**
- Batch processing jobs that don't need network access
- Security-sensitive workloads (cryptographic operations, secret processing)
- Compliance requirements mandating air-gapped execution
- Testing applications that must fail gracefully without network

```bash
docker run --network=none backup-job
```

***

## Network Comparison Table

| Network Type | Isolation | DNS Resolution | Multi-Host | Performance | Use Case |
|--------------|-----------|----------------|------------|-------------|----------|
| **Bridge (default)** | Medium | No (unless linked) | No | Good | Dev/test, simple apps |
| **User-defined Bridge** | High | Yes | No | Good | Multi-container apps |
| **Host** | None | N/A | No | Best (no NAT) | Performance-critical |
| **Overlay** | High | Yes | Yes | Moderate (VXLAN overhead) | Swarm clusters |
| **Macvlan** | Low (physical network) | No | Yes (physical) | Best (direct) | Legacy/physical integration |
| **None** | Maximum | No | No | N/A | Air-gapped workloads |

***

## Troubleshooting Docker Networking

```bash
# List all networks
docker network ls

# Inspect network details (subnet, gateway, containers)
docker network inspect my-network

# Check which network a container is on
docker inspect -f '{{json .NetworkSettings.Networks}}' container-name | jq

# Test connectivity between containers
docker exec web ping db
docker exec web nslookup db

# View container's network namespace
docker exec -it container ip addr
docker exec -it container ip route
docker exec -it container cat /etc/resolv.conf

# Check Docker's iptables rules
iptables -t nat -L DOCKER -n -v
iptables -t filter -L DOCKER -n -v

# Capture packets inside a container
docker exec -it container tcpdump -i eth0 port 80
```

***

## Security Best Practices

1. **Use user-defined bridges** — isolate applications from each other
2. **Avoid host network** — except for specific performance/security monitoring use cases
3. **Limit exposed ports** — only publish ports that must be externally accessible
4. **Use internal networks** — `docker network create --internal` for backend services (database, cache) that shouldn't have internet access
5. **Enable Docker's built-in firewall** — don't disable iptables integration
6. **Audit network configurations** — regularly review `docker network inspect` output

***

## Summary

Docker networking provides a spectrum of isolation levels:

- **Maximum isolation** → `none` network
- **High isolation** → user-defined bridge, overlay
- **Moderate isolation** → default bridge
- **No isolation** → host network, macvlan

Choose based on your requirements for **security**, **performance**, and **connectivity**. For most production microservices, user-defined bridge networks (single host) or overlay networks (Swarm clusters) provide the right balance.
