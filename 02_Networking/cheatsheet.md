# Networking Cheatsheet for DevOps Engineers

```
Networking Cheatsheet
├── Interface Management
│   ├── ip addr — show/add/del IP addresses
│   ├── ip link — bring interfaces up/down, set MTU
│   ├── ip route — show/add/del routes, default gateway
│   ├── ip neigh — ARP/neighbor cache
│   └── ifconfig / route — legacy equivalents (deprecated)
├── Connectivity Testing
│   ├── ping — ICMP reachability check
│   ├── traceroute / tracepath — hop-by-hop path tracing
│   ├── mtr — continuous traceroute + ping, shows packet loss per hop
│   └── hping3 — TCP/UDP/ICMP packet crafting
├── DNS Troubleshooting
│   ├── dig — full detail, trace resolution, query specific server
│   ├── host — simple lookup
│   ├── nslookup — legacy DNS query
│   └── dig +trace — shows full recursive resolution path
├── Network Monitoring
│   ├── ss / netstat — socket state, listening ports, protocol stats
│   ├── iftop / nload — real-time per-interface bandwidth
│   ├── tcpdump — packet capture (filter by host, port, flags)
│   └── vnstat / bwm-ng — historical bandwidth usage
├── Socket & Process Analysis
│   ├── ss -tnp — TCP sockets with process info
│   ├── lsof -i — open network file descriptors
│   └── ss -s — summary: TIME_WAIT count, CLOSE_WAIT count
├── Remote Access
│   ├── ssh — shell, port forwarding (-L/-R/-D), key auth
│   ├── scp — secure file copy (being deprecated, use sftp)
│   └── rsync — delta-efficient sync over SSH
├── HTTP / API Testing
│   ├── curl — GET/POST/PUT, headers, auth, status code only
│   └── wget — download files, recursive fetch
├── Firewall
│   ├── iptables — filter/nat/mangle tables, chains, rules
│   ├── nftables — modern replacement for iptables
│   └── ufw — simplified front-end for iptables
├── Performance Benchmarking
│   ├── iperf3 — TCP/UDP throughput testing
│   ├── ethtool — NIC settings, statistics, speed/duplex
│   └── nicstat — NIC utilization and error rates
├── SSL/TLS Diagnostics
│   ├── openssl s_client — inspect cert, test TLS versions
│   └── nmap --script ssl-enum-ciphers — cipher enumeration
├── Container / Kubernetes
│   ├── docker network — list, inspect networks
│   ├── kubectl get ep / svc / networkpolicy — K8s network resources
│   ├── kubectl exec ... -- curl/nslookup — test from inside pod
│   └── kubectl debug --image=nicolaka/netshoot — debug pod
├── Advanced / eBPF
│   ├── hubble observe — Cilium flow visibility (L3-L7)
│   ├── bpftool — list eBPF programs and maps
│   └── cilium monitor — live eBPF packet monitoring
├── BGP / Anycast
│   ├── vtysh / birdc — BGP routing table inspection
│   └── calicoctl node status — BGP peer health (Calico)
└── System Tuning
    ├── nf_conntrack_max — connection tracking table size
    ├── ip_local_port_range — ephemeral port range
    ├── tcp_tw_reuse — reuse TIME_WAIT sockets
    ├── tcp_fin_timeout — reduce TIME_WAIT duration
    └── tcp_congestion_control=bbr — better throughput on lossy links
```

## First Principles

- A network interface needs an IP address (L3) to route packets and a MAC address (L2) for local delivery — `ip addr` manages both.
- Every path has a gateway: packets destined off-subnet go to the default gateway. If no route exists, the kernel drops the packet silently — `ip route` exposes this.
- DNS is a prerequisite for almost everything: if name resolution is broken, services appear down even when IPs respond. Diagnose DNS first with `dig`, not `ping hostname`.
- A listening socket is useless if the process is dead or bound to loopback-only: `ss -tlnp` reveals what is listening on which address — `0.0.0.0` (all) vs `127.0.0.1` (local only).
- Packet capture is ground truth: logs can lie, but `tcpdump` shows exactly what bytes traversed the wire — use it to confirm whether traffic is actually sent/received before blaming application code.
- TLS certificates have expiry dates; services never send reminders. Proactive monitoring (`openssl s_client`) and automated renewal (`cert-manager`) prevent silent outages.
- sysctl tuning is stateless across reboots unless persisted to `/etc/sysctl.conf` — settings applied at runtime disappear on restart.

Quick reference for network commands, troubleshooting, and common tasks.

***

## Interface Configuration

### Modern `ip` Commands (Recommended)

| Command | Description |
|---------|-------------|
| `ip addr show` | Show all interfaces and IP addresses |
| `ip addr show eth0` | Show IP for specific interface |
| `ip addr add 192.168.1.1/24 dev eth0` | Add IP address to interface |
| `ip addr del 192.168.1.1/24 dev eth0` | Remove IP address |
| `ip link show` | Show all network interfaces |
| `ip link set eth0 up` | Bring interface up |
| `ip link set eth0 down` | Bring interface down |
| `ip link set eth0 mtu 9000` | Set MTU (jumbo frames) |
| `ip route show` | Show routing table |
| `ip route add default via 192.168.1.1` | Add default gateway |
| `ip route add 10.0.0.0/24 via 192.168.1.1` | Add static route |
| `ip route del 10.0.0.0/24 via 192.168.1.1` | Delete route |
| `ip neigh show` | Show ARP/neighbor cache |
| `ip neigh add 192.168.1.100 lladdr aa:bb:cc:dd:ee:ff dev eth0` | Add ARP entry |
| `ip neigh del 192.168.1.100 dev eth0` | Delete ARP entry |
| `ip -s link show eth0` | Show interface statistics |

### Legacy Commands (Still Useful)

| Command | Description |
|---------|-------------|
| `ifconfig` | Show interfaces (deprecated, use `ip addr`) |
| `ifconfig eth0 up` | Activate eth0 |
| `ifconfig eth0 192.168.1.1 netmask 255.255.255.0` | Set IP and mask |
| `route -n` | Show routing table (numeric) |
| `route add default gw 192.168.1.1` | Add default gateway |
| `route flush` | Remove all routes |
| `arp -a` | Show ARP table |
| `arp -n` | Show ARP (numeric, no DNS lookup) |
| `arp -d 192.168.1.100` | Delete ARP entry |
| `arp -s 192.168.1.100 aa:bb:cc:dd:ee:ff` | Add static ARP |
| `iwconfig wlan0` | Show wireless interface info |

***

## Connectivity Testing

| Command | Description |
|---------|-------------|
| `ping google.com` | Test reachability (ICMP echo) |
| `ping -c 4 google.com` | Send 4 packets only |
| `ping -I eth0 google.com` | Ping from specific interface |
| `traceroute google.com` | Trace route to destination |
| `tracepath google.com` | Simplified traceroute (no root needed) |
| `mtr google.com` | Combined ping + traceroute (real-time) |
| `mtr -rw google.com` | MTR in report mode (good for logs) |
| `hping3 -S -p 80 google.com` | SYN scan port 80 |
| `hping3 --flood google.com` | Stress test (use carefully!) |

***

## DNS Troubleshooting

| Command | Description |
|---------|-------------|
| `dig example.com` | DNS lookup (detailed output) |
| `dig example.com ANY` | All record types |
| `dig @8.8.8.8 example.com` | Use specific DNS server |
| `dig +trace example.com` | Show full resolution chain |
| `dig +short example.com` | Brief output (IP only) |
| `host example.com` | Simple DNS lookup |
| `nslookup example.com` | Legacy DNS lookup |
| `dig -x 93.184.216.34` | Reverse DNS lookup |
| `dig soa example.com` | Get SOA record (zone info) |

***

## Network Monitoring

| Command | Description |
|---------|-------------|
| `netstat -tuln` | Show listening TCP/UDP sockets |
| `netstat -r` | Show kernel routing table |
| `netstat -i` | Show interface statistics |
| `netstat -s` | Show per-protocol statistics |
| `ss -tuln` | Socket statistics (modern replacement for netstat) |
| `ss -i` | TCP connection info (RTT, congestion window) |
| `ss -m` | Show memory usage by sockets |
| `iftop -n` | Real-time bandwidth (numeric addresses) |
| `iftop -i eth0` | Monitor specific interface |
| `iftop -P` | Show port numbers |
| `tcpdump -i eth0` | Capture traffic on eth0 |
| `tcpdump -i eth0 -n port 80` | Capture port 80 (no DNS) |
| `tcpdump -i eth0 -w capture.pcap` | Save to file for Wireshark |
| `tcpdump -A -i eth0 'tcp port 80'` | Show HTTP content (ASCII) |
| `tcpdump -X -i eth0` | Hex + ASCII dump |
| `tcpdump -nn -i eth0 host 1.2.3.4` | Filter by host (no resolution) |
| `tcpdump -nn -i eth0 'net 10.0.0.0/8'` | Filter by subnet |
| `tcpdump -nn -i eth0 'tcp[tcpflags] & tcp-syn != 0'` | Show SYN packets only |
| `vnstat` | Bandwidth usage over time |
| `vnstat -l` | Live monitoring |
| `vnstat -d` | Daily statistics |
| `bwm-ng` | Bandwidth monitor (multiple interfaces) |
| `speedometer -r eth0 -t eth0` | Visual bandwidth display |
| `nload eth0` | Real-time traffic graph |
| `iptraf-ng` | Interactive IP traffic monitor |

***

## Socket Analysis

| Command | Description |
|---------|-------------|
| `ss -t` | Show TCP sockets |
| `ss -u` | Show UDP sockets |
| `ss -l` | Show listening sockets |
| `ss -a` | Show all sockets |
| `ss -n` | Numeric output (no DNS) |
| `ss -p` | Show process using socket |
| `ss -tnp` | TCP + numeric + process |
| `ss -tnp | grep :80` | Find what's using port 80 |
| `ss -s` | Socket summary statistics |
| `lsof -i :80` | List open files on port 80 |
| `lsof -i TCP` | All TCP connections |
| `lsof -i @192.168.1.1` | Connections to specific IP |

***

## SSH & Remote Access

| Command | Description |
|---------|-------------|
| `ssh user@hostname` | Connect to remote host |
| `ssh -p 2222 user@hostname` | Specify port |
| `ssh -i ~/.ssh/key user@hostname` | Use specific key |
| `ssh -v user@hostname` | Verbose mode (debug) |
| `ssh -L 8080:localhost:80 user@host` | Local port forwarding |
| `ssh -R 8080:localhost:80 user@host` | Remote port forwarding |
| `ssh -D 1080 user@host` | SOCKS proxy |
| `ssh-copy-id user@hostname` | Copy SSH key to remote |
| `scp file.txt user@remote:/path/` | Upload file |
| `scp user@remote:/path/file.txt .` | Download file |
| `scp -r dir/ user@remote:/path/` | Copy directory |
| `scp -P 2222 file.txt user@remote:/path/` | Specify port |
| `sftp user@hostname` | Interactive secure FTP |
| `rsync -avz file.txt user@remote:/path/` | Efficient sync |
| `rsync -avz --progress src/ user@remote:dest/` | Sync with progress |
| `rsync -avz --delete src/ user@remote:dest/` | Mirror directories |

***

## HTTP/API Testing

| Command | Description |
|---------|-------------|
| `curl https://example.com` | Simple GET request |
| `curl -I https://example.com` | GET headers only |
| `curl -X POST https://api.example.com` | POST request |
| `curl -d "key=value" https://api.example.com` | POST with data |
| `curl -H "Authorization: Bearer TOKEN" https://api.example.com` | With auth header |
| `curl -u user:pass https://example.com` | Basic auth |
| `curl -k https://example.com` | Skip SSL verification |
| `curl -L https://example.com` | Follow redirects |
| `curl -o file.zip https://example.com/file.zip` | Save to file |
| `curl -O https://example.com/file.zip` | Save with original name |
| `curl -s -o /dev/null -w "%{http_code}" https://example.com` | Get status code only |
| `curl -w "@format.txt" https://example.com` | Custom output format |
| `wget https://example.com/file.zip` | Download file |
| `wget -r https://example.com` | Recursive download |
| `wget --limit-rate=100k https://example.com/file.zip` | Rate-limited download |

***

## Firewall (iptables/nftables)

| Command | Description |
|---------|-------------|
| `iptables -L -n` | List all rules |
| `iptables -L -n -v` | Verbose listing with counters |
| `iptables -t nat -L -n` | List NAT rules |
| `iptables -A INPUT -p tcp --dport 22 -j ACCEPT` | Allow SSH |
| `iptables -A INPUT -p tcp --dport 80 -j ACCEPT` | Allow HTTP |
| `iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT` | Allow established |
| `iptables -A INPUT -j DROP` | Drop all other inbound |
| `iptables -D INPUT 1` | Delete first INPUT rule |
| `iptables -F` | Flush all rules |
| `iptables -t nat -F` | Flush NAT rules |
| `iptables-save > /etc/iptables.rules` | Save rules |
| `iptables-restore < /etc/iptables.rules` | Restore rules |
| `nft list ruleset` | List nftables rules |
| `nft flush ruleset` | Flush nftables |
| `ufw status` | Check UFW status |
| `ufw allow 22/tcp` | Allow SSH (UFW) |
| `ufw enable` | Enable UFW |

***

## Connection Tracking

| Command | Description |
|---------|-------------|
| `conntrack -L` | List connection tracking entries |
| `conntrack -L | grep ESTABLISHED` | Show established connections |
| `conntrack -L | wc -l` | Count tracked connections |
| `conntrack -D -s 192.168.1.100` | Delete entries for IP |
| `sysctl net.netfilter.nf_conntrack_count` | Current conntrack count |
| `sysctl net.netfilter.nf_conntrack_max` | Max conntrack entries |
| `echo 3 > /proc/sys/net/netfilter/nf_conntrack_count` | Reset conntrack (dangerous!) |

***

## Network Performance

| Command | Description |
|---------|-------------|
| `iperf3 -s` | Start iperf3 server |
| `iperf3 -c server.example.com` | Connect to iperf3 server |
| `iperf3 -c server -P 4` | Use 4 parallel streams |
| `iperf3 -c server -R` | Reverse mode (server sends) |
| `ethtool eth0` | Show NIC settings |
| `ethtool -S eth0` | NIC statistics |
| `ethtool -A eth0` | Show pause (flow control) settings |
| `ethtool -s eth0 speed 1000 duplex full` | Set speed/duplex |
| `mii-tool eth0` | Check link status (older NICs) |
| `nicstat` | NIC utilization and errors |

***

## Wireless Networks

| Command | Description |
|---------|-------------|
| `iwconfig` | Show wireless interfaces |
| `iwlist wlan0 scan` | Scan for networks |
| `iwlist wlan0 freq` | Show available frequencies |
| `iw dev wlan0 link` | Show connection info |
| `iw dev wlan0 station dump` | Station statistics |
| `nmcli device wifi list` | List WiFi networks (NetworkManager) |
| `nmcli device wifi connect SSID password PASS` | Connect to WiFi |

***

## DHCP

| Command | Description |
|---------|-------------|
| `dhclient -r` | Release DHCP lease |
| `dhclient` | Renew DHCP lease |
| `dhclient -v` | Verbose DHCP |
| `cat /var/lib/dhcp/dhclient.leases` | View lease file (Linux) |
| `ipconfig /release` | Release DHCP (Windows) |
| `ipconfig /renew` | Renew DHCP (Windows) |
| `ipconfig /all` | Show all config (Windows) |

***

## SSL/TLS Diagnostics

| Command | Description |
|---------|-------------|
| `openssl s_client -connect example.com:443` | Connect and show cert |
| `openssl s_client -connect example.com:443 -servername example.com` | With SNI |
| `openssl s_client -connect example.com:443 -showcerts` | Show full chain |
| `openssl s_client -connect example.com:443 -tls1_2` | Test TLS 1.2 |
| `openssl s_client -connect example.com:443 -tls1_3` | Test TLS 1.3 |
| `echo \| openssl s_client -connect example.com:443 2>/dev/null \| openssl x509 -noout -dates` | Check cert expiry |
| `openssl x509 -in cert.pem -text -noout` | View certificate |
| `openssl x509 -in cert.pem -noout -enddate` | Show expiry date |
| `nmap --script ssl-enum-ciphers -p 443 example.com` | Enumerate SSL ciphers |

***

## Container Networking

| Command | Description |
|---------|-------------|
| `docker network ls` | List Docker networks |
| `docker network inspect bridge` | Inspect network |
| `docker inspect <container> \| grep IPAddress` | Get container IP |
| `kubectl get pods -o wide` | Get pods with IPs |
| `kubectl get svc` | Get services |
| `kubectl describe svc <name>` | Service details |
| `kubectl exec <pod> -- curl <service>` | Test connectivity from pod |
| `kubectl run test --rm -it --image=nicolaka/netshoot -- bash` | Debug pod |
| `crictl pods` | List CRI-O/containerd pods |
| `crictl inspectp <pod-id>` | Inspect pod sandbox |

***

## Kubernetes Network Debugging

| Command | Description |
|---------|-------------|
| `kubectl get ep` | Get endpoints |
| `kubectl get networkpolicy` | Get network policies |
| `kubectl describe networkpolicy <name>` | NP details |
| `kubectl debug <pod> -it --image=nicolaka/netshoot --target=<container>` | Ephemeral debug container |
| `kubectl logs <pod> -c <container>` | Container logs |
| `kubectl port-forward <pod> 8080:80` | Forward port to local |
| `kubectl exec <pod> -- cat /etc/resolv.conf` | Check DNS config |
| `kubectl exec <pod> -- nslookup <service>` | Test DNS from pod |
| `kubectl exec <pod> -- wget -qO- http://<service>` | Test HTTP from pod |

***

## Quick Reference: Common Ports

| Port | Service | Protocol |
|------|---------|----------|
| 22 | SSH | TCP |
| 53 | DNS | TCP/UDP |
| 80 | HTTP | TCP |
| 443 | HTTPS | TCP |
| 3306 | MySQL | TCP |
| 5432 | PostgreSQL | TCP |
| 6379 | Redis | TCP |
| 8080 | HTTP Alt | TCP |
| 27017 | MongoDB | TCP |
| 6443 | Kubernetes API | TCP |
| 2379-2380 | etcd | TCP |
| 4789 | VXLAN | UDP |
| 6081 | Geneve | UDP |

***

## Troubleshooting Checklist

```
1. Can you ping the host?
   → No: Check routing, firewall, physical connectivity

2. Can you telnet/nc to the port?
   → No: Check service is running, firewall allows port

3. Does DNS resolve correctly?
   → No: Check /etc/resolv.conf, DNS server, record exists

4. Is the service listening?
   → ss -tlnp | grep :PORT

5. Are connections established?
   → ss -tn | grep ESTAB

6. Any packet loss?
   → mtr -rw <destination>

7. High latency?
   → Check route, congestion, ISP issues

8. Connection timeouts?
   → Firewall dropping packets, check iptables/security groups

9. Connection refused?
   → Service not running or not listening on that port

10. Intermittent failures?
    → Check connection tracking limits, NAT gateway limits
```

***

## Environment Variables

```bash
# Set proxy
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080
export NO_PROXY=localhost,127.0.0.1,.local

# DNS resolution order
cat /etc/nsswitch.conf  # Check "hosts:" line

# DNS servers
cat /etc/resolv.conf

# Default gateway
ip route show | grep default

# Hostname
hostname
hostnamectl  # systemd systems
```

***

## System Tuning

```bash
# Increase connection tracking table
sysctl -w net.netfilter.nf_conntrack_max=262144

# Increase local port range
sysctl -w net.ipv4.ip_local_port_range="1024 65535"

# Reduce TIME_WAIT duration
sysctl -w net.ipv4.tcp_fin_timeout=30

# Enable port reuse
sysctl -w net.ipv4.tcp_tw_reuse=1

# Increase socket buffer sizes
sysctl -w net.core.rmem_max=16777216
sysctl -w net.core.wmem_max=16777216

# Make permanent
echo "net.ipv4.ip_local_port_range=1024 65535" >> /etc/sysctl.conf
sysctl -p
```

***

## Advanced observability (eBPF & Hubble)

| Command | Description |
|---------|-------------|
| `hubble observe --follow` | Real-time flow visibility (Cilium) |
| `hubble observe --protocol http` | L7 HTTP visibility |
| `hubble observe --verdict DROPPED` | Show only dropped packets |
| `hubble status` | Check Hubble health |
| `bpftool prog show` | List loaded eBPF programs |
| `bpftool map show` | List eBPF maps (state) |
| `cilium status` | Check Cilium CNI health |
| `cilium monitor --type drop` | Monitor dropped packets via eBPF |

***

## BGP & Anycast Diagnostics

| Command | Description |
|---------|-------------|
| `calicoctl node status` | Check BGP peering (Calico) |
| `vtysh -c "show ip bgp summary"` | BGP summary (FRR/Quagga) |
| `vtysh -c "show ip bgp"` | View BGP routing table |
| `birdc show protocols` | Check BGP status (BIRD) |
| `dig +short whoami.akamai.net` | Check which Anycast edge you hit |

***

## HTTP/3 & QUIC Inspection

| Command | Description |
|---------|-------------|
| `curl --http3 https://example.com` | Force HTTP/3 request |
| `tshark -V -Y quic` | Deep QUIC packet analysis |
| `tcpdump -nn -i eth0 udp port 443` | Capture QUIC traffic |

***

## System Design Perspective

**Scalability**
- `nf_conntrack_max` is a global kernel limit. On a Kubernetes node running hundreds of pods, each TCP connection occupies a conntrack entry. Default of 65,536 is dangerously low — increase to 1M+ on busy nodes.
- `ip_local_port_range` caps outbound connection concurrency per host. With the default `32768-60999`, a single NAT Gateway IP can only hold ~28k concurrent outbound connections before port exhaustion occurs.
- eBPF-based tools (Hubble, cilium monitor) have near-zero overhead because they run in-kernel — unlike tcpdump which requires a copy of every packet to userspace via a libpcap socket.

**Failure Modes**
- Wireless (`iwconfig`) commands are often absent on server images. Attempting to diagnose a server's "wireless" issue with `iwlist scan` wastes time — check `ip link` to confirm interface type first.
- `iptables-save` output is silently lost on reboot unless written to a file and restored via a systemd unit or `iptables-persistent`. Manual rules are ephemeral.
- BGP sessions (port 179 TCP) are dropped silently by security groups that block all TCP. Verify BGP peer connectivity with `nc -zv peer-ip 179` before blaming the routing protocol.

**Trade-offs**
- `tcpdump` vs `ss`: ss gives socket state at a moment in time (zero overhead); tcpdump captures actual payloads but adds CPU and memory cost proportional to traffic rate.
- Verbose logging (`curl -v`) reveals TLS handshake details and redirect chains but is too noisy for automation — use `-s -o /dev/null -w "%{http_code}"` in scripts instead.
- Connection pooling (HTTP adapters, database pools) reduces TIME_WAIT accumulation dramatically but adds complexity in managing pool lifecycle and connection health checks.

***
