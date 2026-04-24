# Docker Networking Internals

## Network Driver Architecture

```
Container process
    │
    ▼
veth pair (virtual ethernet, one end in container netns, one end on host)
    │
    ▼
docker0 bridge (Linux bridge, default 172.17.0.0/16)
    │
    ▼  iptables NAT (MASQUERADE rule for outbound traffic)
Host physical NIC
    │
    ▼
External network
```

Docker's networking model: each container gets its own network namespace with a loopback `lo` and one or more virtual ethernet interfaces. The host end of each veth pair plugs into a Linux bridge.

```bash
# See the veth pair for a running container
docker inspect --format '{{.NetworkSettings.SandboxKey}}' mycontainer
# /var/run/docker/netns/<id>

# Enter the container's network namespace
PID=$(docker inspect --format '{{.State.Pid}}' mycontainer)
nsenter -t $PID -n ip addr       # see container's interfaces
nsenter -t $PID -n ip route      # see container's routing table
nsenter -t $PID -n ss -tlnp      # listening sockets

# On the host: find the veth pair index
ip link | grep veth
# bridge link shows which veth attaches to docker0
bridge link show docker0
```

---

## Network Drivers

### bridge (default)

User-defined bridge vs. the default `docker0` bridge — important distinction:

| Feature | Default `docker0` | User-defined bridge |
|---------|-------------------|---------------------|
| DNS resolution | No (IP only) | Yes (container name → IP) |
| Network isolation | All containers share it | Scoped to bridge |
| `--link` required | Yes (deprecated) | No |
| Can be removed | No | Yes |

```bash
# Create user-defined bridge
docker network create \
  --driver bridge \
  --subnet 192.168.100.0/24 \
  --gateway 192.168.100.1 \
  --opt com.docker.network.bridge.name=mybridge \
  mynet

docker run --rm --network mynet --name app1 ubuntu sleep 600 &
docker run --rm --network mynet alpine ping app1   # DNS works

# Inspect bridge internals
docker network inspect mynet
ip addr show mybridge      # host side of the bridge
```

**iptables rules Docker manages:**

```bash
# View Docker's iptables rules
iptables -t nat -L -n --line-numbers    # MASQUERADE + DNAT for port mapping
iptables -L DOCKER -n --line-numbers    # per-container allow rules
iptables -L DOCKER-ISOLATION-STAGE-1 -n  # inter-network isolation

# Port mapping example: -p 8080:80
# Docker adds: -A DOCKER ! -i docker0 -p tcp --dport 8080 -j DNAT --to 172.17.0.2:80
```

### host

Container shares the host network namespace — no veth, no NAT, no port mapping needed.

```bash
docker run --rm --network host nginx
# nginx listens on host port 80 directly
# No -p flag needed or allowed
```

Use cases: performance-critical workloads where NAT overhead matters, raw socket access (network monitoring tools). Risk: container can bind any port, sees all host interfaces.

### none

Container gets a network namespace with only loopback (`lo`). No external connectivity.

```bash
docker run --rm --network none ubuntu ip addr
# 1: lo: <LOOPBACK,UP>
```

Use for offline batch jobs, security-sensitive workloads, hermetic builds (`docker build --network=none`).

### overlay (Swarm / multi-host)

VXLAN-based L2 overlay across Docker hosts. Each overlay network creates a VXLAN tunnel between hosts.

```bash
# Requires Swarm mode or external key-value store
docker swarm init
docker network create --driver overlay --attachable myoverlay
docker service create --network myoverlay --replicas 3 myapp
```

VXLAN VNI assigned per overlay network. Traffic path: container → veth → br0 (inside netns sandbox) → VXLAN → host NIC → remote host → reverse.

### macvlan

Assigns a MAC address directly to the container — container appears as a physical device on the LAN. No NATting, no bridge.

```bash
# Parent interface must be in promiscuous mode
ip link set eth0 promisc on

docker network create -d macvlan \
  --subnet=192.168.1.0/24 \
  --gateway=192.168.1.1 \
  --opt parent=eth0 \
  macvlan_net

docker run --rm --network macvlan_net \
  --ip 192.168.1.200 \
  ubuntu ip addr
# Container has 192.168.1.200, reachable from physical LAN

# Limitation: host cannot directly talk to macvlan containers (NIC split-horizon)
# Fix: create macvlan interface on host in same network
ip link add macvlan-host link eth0 type macvlan mode bridge
ip addr add 192.168.1.201/24 dev macvlan-host
ip link set macvlan-host up
```

**macvlan vs ipvlan:**

| Feature | macvlan | ipvlan (L2) | ipvlan (L3) |
|---------|---------|-------------|-------------|
| MAC per container | Yes | No (shares host MAC) | No |
| Works with switches filtering MACs | No | Yes | Yes |
| Routing | L2 (switches) | L2 | L3 (kernel routes) |
| Use case | Legacy app needs own MAC | Constrained environments | Router-on-a-stick setups |

---

## Container DNS

Docker runs an embedded DNS server at `127.0.0.11:53` inside each container's network namespace.

```
Container DNS query
    │
    ▼ 127.0.0.11:53 (Docker's embedded DNS)
    ├── Matches another container name on same user-defined bridge → return container IP
    ├── Matches a service alias → return virtual IP
    └── No match → forward to host's /etc/resolv.conf upstream
```

```bash
# Verify embedded DNS in container
docker run --rm --network mynet alpine cat /etc/resolv.conf
# nameserver 127.0.0.11
# options ndots:0

# DNS aliases (same network, multiple names)
docker run --rm --network mynet --network-alias api ubuntu sleep 600

# Connect container to additional networks (adds interfaces)
docker network connect mynet2 mycontainer
docker inspect --format '{{range .NetworkSettings.Networks}}{{.IPAddress}} {{end}}' mycontainer
```

---

## Port Mapping Internals

When you run `-p 8080:80`, Docker:

1. Adds a DNAT rule in `iptables -t nat -A DOCKER` to forward `<host-ip>:8080 → <container-ip>:80`
2. Adds a MASQUERADE rule so replies route back correctly
3. Allocates from the host's ephemeral port range for hairpin NAT

```bash
# Port-published container
docker run -d -p 8080:80 nginx
iptables -t nat -L DOCKER -n
# DNAT  tcp  --  !docker0  *  0.0.0.0/0  0.0.0.0/0  tcp dpt:8080 to:172.17.0.2:80

# Bind to specific host IP (prevent global exposure)
docker run -d -p 127.0.0.1:8080:80 nginx

# UDP port mapping
docker run -d -p 5353:53/udp my-dns-server

# Publish all exposed ports to random host ports
docker run -d -P nginx          # EXPOSE 80 → random ephemeral port
docker port <container>         # Show host:port → container:port mapping
```

---

## Network Troubleshooting

```bash
# Packet capture inside container
PID=$(docker inspect --format '{{.State.Pid}}' mycontainer)
nsenter -t $PID -n tcpdump -i eth0 -w /tmp/capture.pcap

# Or use a debug container sharing the network namespace
docker run --rm --net=container:mycontainer \
  nicolaka/netshoot \
  tcpdump -i eth0 -nn

# Test connectivity
docker run --rm --net=container:mycontainer \
  nicolaka/netshoot \
  curl -v http://other-container:8080

# DNS resolution debug
docker run --rm --network mynet \
  nicolaka/netshoot \
  dig app1.mynet @127.0.0.11

# MTU check (overlay networks reduce effective MTU)
docker run --rm alpine ip link show eth0
# Default MTU 1500; overlay reduces to ~1450 due to VXLAN overhead (50 bytes)

# Set MTU for VXLAN-based networks
docker network create \
  --driver overlay \
  --opt com.docker.network.driver.mtu=1450 \
  overlay-net

# Bandwidth test between containers
docker run --rm --network mynet -d --name iperf-server networkstatic/iperf3 -s
docker run --rm --network mynet networkstatic/iperf3 -c iperf-server
```

---

## Network Security

### Inter-container isolation

```bash
# Disable ICC (inter-container communication) on default bridge
# In /etc/docker/daemon.json:
{
  "icc": false,
  "iptables": true
}

# Containers on different user-defined bridges cannot communicate (iptables DOCKER-ISOLATION)
# Only containers on the SAME user-defined bridge can reach each other
```

### Exposing services safely

```bash
# Never expose ports to 0.0.0.0 in production — bind to specific interfaces
docker run -d -p 127.0.0.1:8080:80 nginx         # localhost only
docker run -d -p 10.0.0.1:8080:80 nginx          # specific internal IP

# Use userland proxy vs. direct iptables (performance tradeoff)
# /etc/docker/daemon.json: {"userland-proxy": false}
# With userland-proxy=false: iptables handles port mapping directly (faster)
# Risk: loopback traffic from host won't be forwarded — containers accessible from external only

# Outbound traffic control: block container internet access
docker network create --internal isolated-net
# --internal: no routing to external networks, no gateway
docker run --rm --network isolated-net ubuntu curl https://example.com
# curl: (6) Could not resolve host: example.com
```

### Rootless Docker networking

```bash
# Rootless Docker uses slirp4netns instead of iptables (can't modify host netfilter as non-root)
# Port forwarding limited: ports <1024 require additional config
# /etc/sysctl.d/90-rootless.conf: net.ipv4.ip_unprivileged_port_start=80
```

---

## docker-compose Networking

Docker Compose creates a dedicated bridge network per project by default.

```yaml
# docker-compose.yml
services:
  web:
    image: nginx
    networks:
      - frontend
    ports:
      - "80:80"

  api:
    image: myapi:latest
    networks:
      - frontend
      - backend

  db:
    image: postgres:16
    networks:
      - backend           # only reachable from api, not from web
    environment:
      POSTGRES_PASSWORD: secret

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true        # no external connectivity for DB network
```

```bash
# The project name prefixes all network and container names
# Default: <directory>_<network-name> e.g., myapp_frontend
docker network ls | grep myapp

# Custom project name
docker compose -p prod up -d

# Connect external container to compose network
docker run --rm --network myapp_frontend alpine wget -qO- http://web
```

---

## Key Gotchas

| Gotcha | Detail |
|--------|--------|
| Default bridge has no DNS | Containers on `docker0` can only reach each other by IP; use user-defined bridges for DNS |
| `--link` is deprecated | Legacy; creates aliases and env vars but doesn't work across user-defined networks |
| Overlay requires Swarm or external KV | Can't use overlay driver in standalone Docker without `--attachable` and Swarm mode |
| macvlan host isolation | Host can't talk to macvlan containers without creating a macvlan interface on the host itself |
| MTU mismatch with overlay/VPN | VXLAN adds 50-byte overhead; inner MTU must be 1450 or packets are silently fragmented |
| `icc=false` only affects default bridge | User-defined bridges always isolate from each other regardless of ICC setting |
| `--internal` flag blocks gateway | An internal network has no gateway route; containers can talk to each other but not exit |
| Port binding and `userland-proxy=false` | Disabling userland proxy means loopback traffic (from host to `127.0.0.1:PORT`) bypasses container |
| Rootless Docker can't use iptables | Uses `slirp4netns`; performance lower, port < 1024 requires sysctls |
| `docker network connect` adds a new interface | Container gets a second `eth1`; its routing table doesn't change — outbound still uses the original default gateway |
