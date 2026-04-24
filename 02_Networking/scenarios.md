# Networking Troubleshooting Scenarios

Real-world production scenarios and systematic debugging approaches.

---

## Scenario 1: Intermittent 502 Bad Gateway from Load Balancer

### Symptoms
- Users report occasional 502 errors
- Error rate: ~5% of requests
- More frequent during traffic spikes
- Application logs show no errors

### Investigation Steps

**1. Check Backend Health**
```bash
# AWS ALB target group health
aws elbv2 describe-target-health --target-group-arn <arn>

# Check application status
kubectl get pods -l app=backend
kubectl describe pod <pod-name> | grep -A5 "State:"
kubectl get pod <pod-name> -o jsonpath='{.status.containerStatuses[*].restartCount}'
```

**2. Check Keep-Alive Timeout Mismatch**
```
Common issue: LB idle timeout > backend timeout

AWS ALB default idle timeout: 60 seconds
Nginx default keepalive_timeout: 75 seconds
Gunicorn default timeout: 30 seconds
```

If backend closes connection at 30s but LB thinks it's valid until 60s:
- LB sends request on "dead" connection
- Backend rejects → 502

**Fix:**
```nginx
# Nginx upstream config
upstream backend {
    server 10.0.1.5:8080;
    keepalive_timeout 55s;  # Must be < LB timeout
}
```

```python
# Gunicorn config
timeout = 120  # Must be > LB timeout
keepalive = 5  # Seconds
```

**3. Check Security Groups**
```bash
# Verify LB can reach backend
aws ec2 describe-security-groups --group-ids <backend-sg-id>
aws ec2 describe-security-groups --group-ids <lb-sg-id>

# Look for:
# - Inbound rule allowing LB security group on backend port
# - Outbound rule allowing LB to reach backend
```

**4. Check NAT Gateway Limits**
```bash
# NAT Gateway connection limit: ~64k concurrent connections per IP
# Check if you're hitting the limit

# On backend, check connection count
ss -tn | grep ESTAB | wc -l

# Check for TIME_WAIT accumulation
ss -tn | grep TIME_WAIT | wc -l

# AWS CloudWatch: NAT Gateway metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/NatGateway \
  --metric-name ActiveConnectionCount \
  --dimensions Name=NatGatewayId,Values=<nat-gw-id>
```

### Resolution

| Root Cause | Fix |
|------------|-----|
| Backend crashes | Fix application bug, add health checks |
| Keep-alive mismatch | Align timeouts: backend > LB |
| Security group | Allow LB → backend on port |
| NAT exhaustion | Add NAT Gateway, use VPC endpoints |

---

## Scenario 2: Pod Cannot Reach Service by DNS Name

### Symptoms
- Pod A cannot connect to `service-b.default.svc.cluster.local`
- Direct IP connection works: `curl 10.96.100.50:8080` ✓
- DNS lookup fails or times out

### Investigation Steps

**1. Check CoreDNS Status**
```bash
kubectl get pods -n kube-system -l k8s-app=kube-dns
kubectl logs -n kube-system -l k8s-app=kube-dns

# Look for:
# - CrashLoopBackOff
# - "no endpoints available"
# - High latency in DNS responses
```

**2. Test DNS Resolution from Pod**
```bash
kubectl exec -it <pod-a> -- nslookup service-b.default.svc.cluster.local

# Expected:
# Name:   service-b.default.svc.cluster.local
# Address: 10.96.100.50

# If NXDOMAIN: Service doesn't exist or CoreDNS not synced
# If timeout: CoreDNS unreachable
```

**3. Check resolv.conf Configuration**
```bash
kubectl exec -it <pod-a> -- cat /etc/resolv.conf

# Default (problematic):
nameserver 10.96.0.10
search default.svc.cluster.local svc.cluster.local cluster.local
options ndots:5

# ndots:5 means "google.com" triggers 5 DNS queries before FQDN!
```

**4. Check CoreDNS ConfigMap**
```bash
kubectl get configmap coredns -n kube-system -o yaml

# Look for:
# - Upstream DNS servers (should be reliable)
# - Cache settings (too aggressive = stale records)
# - Loop plugin (detects forwarding loops)
```

**5. Check NetworkPolicy**
```bash
kubectl get networkpolicy -n default
kubectl describe networkpolicy <policy-name>

# Ensure pods can reach kube-dns (port 53 UDP/TCP)
```

**6. Check Endpoint Slices**
```bash
kubectl get endpointslices -l kubernetes.io/service-name=service-b
kubectl describe endpointslice <name>

# Should show Pod IPs as endpoints
# If empty: Service selector doesn't match any Pods
```

### Common Causes

| Issue | Symptom | Fix |
|-------|---------|-----|
| CoreDNS down | All DNS fails | Restart CoreDNS, check resources |
| Wrong ndots | Slow external DNS | Reduce ndots to 2, use FQDN with dot |
| NetworkPolicy blocks | Timeout to CoreDNS | Allow egress to kube-dns |
| Service selector mismatch | NXDOMAIN for service | Fix label selectors |
| Endpoint not ready | DNS resolves but no connection | Check Pod readiness probes |

### Resolution

**Fix ndots issue:**
```yaml
# Pod spec
spec:
  dnsConfig:
    options:
    - name: ndots
      value: "2"
```

**Or use FQDN in application:**
```python
# Instead of:
requests.get("http://service-b:8080")

# Use:
requests.get("http://service-b.default.svc.cluster.local.:8080")
# Note the trailing dot - forces FQDN resolution
```

---

## Scenario 3: Connection Refused vs Connection Timeout

### Understanding the Difference

| Error | What Happened | Likely Cause |
|-------|---------------|--------------|
| **Connection Refused** | Packet reached server, server sent RST | Service not running, wrong port, firewall on host |
| **Connection Timeout** | Packet never got ACK | Firewall dropped packet, routing issue, security group |

### Debugging Connection Refused

```bash
# 1. Is service listening?
ss -tlnp | grep :8080
netstat -tlnp | grep :8080

# 2. Is it listening on correct interface?
# 0.0.0.0:8080 = all interfaces
# 127.0.0.1:8080 = localhost only (not reachable externally!)
# 10.0.1.5:8080 = specific interface

# 3. Check service status
systemctl status myapp
kubectl get pods -l app=myapp

# 4. Check if process crashed
journalctl -u myapp -n 50
kubectl logs <pod-name>
```

**Common causes:**
- Application crashed
- Listening on localhost only
- Wrong port in client configuration
- Container not started

### Debugging Connection Timeout

```bash
# 1. Can you ping the host?
ping <destination-ip>

# 2. Can you reach the port?
nc -zv <destination-ip> <port>
telnet <destination-ip> <port>

# 3. Trace the route
mtr -rw <destination-ip>
traceroute <destination-ip>

# 4. Check security groups / firewalls
aws ec2 describe-security-groups
iptables -L -n -v

# 5. Check routing
ip route get <destination-ip>
kubectl get routes

# 6. Capture packets
tcpdump -i eth0 host <destination-ip> and port <port>
```

**Common causes:**
- Security group blocking inbound/outbound
- NACL denying traffic
- iptables DROP rule
- No route to destination
- Intermediate firewall

### Decision Tree

```
Connection Error
       │
       ├─ Refused (RST received)
       │   ├─ Is service running? → Start it
       │   ├─ Is it listening on correct interface? → Bind to 0.0.0.0
       │   └─ Is port correct? → Fix client config
       │
       └─ Timeout (no response)
           ├─ Can you ping? → L3 works
           │   ├─ Yes → Check L4 (firewall, security group)
           │   └─ No → Check routing, physical connectivity
           ├─ Security group allows port? → Add rule
           ├─ NACL allows traffic? → Add rule
           └─ iptables dropping? → Fix rules
```

---

## Scenario 4: High Latency in Cross-Region Communication

### Symptoms
- P99 latency spiked from 50ms to 500ms
- Affects cross-region traffic only
- Same-region latency normal

### Investigation Steps

**1. Identify the Traffic Path**
```bash
# From source pod
kubectl exec <pod> -- mtr -rw <destination>

# Look for:
# - Which hop introduces latency
# - Packet loss at specific routers
# - Asymmetric routing (different paths each way)
```

**2. Check DNS Resolution**
```bash
# Ensure resolving to correct region's IP
kubectl exec <pod> -- dig +short <service>

# Should return regional endpoint IP
# If returning wrong region: check split-horizon DNS config
```

**3. Check for Cross-Region Data Transfer**
```bash
# AWS: Check if traffic is going over public internet vs Direct Connect
aws cloudwatch get-metric-statistics \
  --namespace AWS/DirectConnect \
  --metric-name ConnectionBpsIngress \
  --dimensions Name=ConnectionId,Values=<dx-conn-id>
```

**4. Check for Bandwidth Saturation**
```bash
# CloudWatch: NAT Gateway, Transit Gateway metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/NatGateway \
  --metric-name BytesOutToDestination \
  --dimensions Name=NatGatewayId,Values=<nat-gw-id>

# If near bandwidth limit: congestion → latency
```

**5. Check for MTU Issues**
```bash
# Large packets may be fragmented or dropped
# Test with different sizes

ping -M do -s 1472 <destination>  # Should work
ping -M do -s 1473 <destination>  # May fail if path MTU < 1500

# If fragmentation required: latency increase
```

### Common Causes

| Cause | Symptom | Fix |
|-------|---------|-----|
| Public internet routing | High, variable latency | Use Direct Connect, Transit Gateway |
| Bandwidth saturation | Latency correlates with traffic | Increase bandwidth, add QoS |
| MTU mismatch | Large transfers slow, small OK | Fix MTU, enable MSS clamping |
| DNS misconfiguration | Resolving to wrong region | Fix Route53 geolocation routing |
| Cross-AZ traffic | Moderate latency increase | Use regional endpoints |

### Resolution

**Use Private Connectivity:**
```
Instead of:
Pod → Internet → Regional LB → Backend

Use:
Pod → VPC Peering → Backend VPC
or
Pod → Transit Gateway → Backend VPC
```

**Configure Geolocation Routing:**
```yaml
# Route53 Health Check + Geolocation
# Users in us-east-1 → us-east-1 endpoint
# Users in us-west-2 → us-west-2 endpoint
# Failover: health check triggers DNS change
```

**Enable TCP BBR:**
```bash
# On Linux nodes
sysctl -w net.ipv4.tcp_congestion_control=bbr

# Better performance on lossy/congested links
```

---

## Scenario 5: NAT Gateway Connection Exhaustion

### Symptoms
- Intermittent connection failures to external services
- Error: "no buffer space available" or "cannot assign requested address"
- Affects pods in private subnets
- Coincides with high outbound traffic

### Root Cause

NAT Gateway limits:
- **64,000 concurrent connections per NAT Gateway**
- Each connection = 1 entry in NAT table
- When exhausted: new connections fail

### Investigation

**1. Check NAT Gateway Metrics**
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/NatGateway \
  --metric-name ActiveConnectionCount \
  --dimensions Name=NatGatewayId,Values=<nat-gw-id> \
  --statistics Maximum \
  --period 60

# If consistently near 64k: you're hitting the limit
```

**2. Check Connection Count from Pods**
```bash
kubectl exec <pod> -- ss -tn | wc -l

# Multiply by number of pods in private subnet
# If total > 64k: NAT is bottleneck
```

**3. Identify Connection-Heavy Workloads**
```bash
# Check which pods have most connections
for pod in $(kubectl get pods -o jsonpath='{.items[*].metadata.name}'); do
  count=$(kubectl exec $pod -- ss -tn 2>/dev/null | wc -l)
  echo "$pod: $count connections"
done | sort -t: -k2 -rn | head -10
```

**4. Check for Connection Leaks**
```bash
# Look for excessive TIME_WAIT or CLOSE_WAIT
kubectl exec <pod> -- ss -tn | grep -c TIME_WAIT
kubectl exec <pod> -- ss -tn | grep -c CLOSE_WAIT

# CLOSE_WAIT indicates application not closing connections
```

### Solutions

| Solution | Cost | Complexity | Capacity |
|----------|------|------------|----------|
| Add NAT Gateway | $$$ | Low | +64k per GW |
| Use VPC Endpoints | $ | Low | Effectively unlimited |
| Connection Pooling | $ | Medium | Reduces connections 10-100x |
| Use HTTP/2 | $ | Medium | Multiplexing reduces connections |
| Deploy egress proxy | $$ | High | Centralized connection management |

**VPC Endpoints (Best for AWS Services):**
```bash
# Instead of: Pod → NAT Gateway → S3 public endpoint
# Use: Pod → VPC Endpoint → S3 (private)

aws ec2 create-vpc-endpoint \
  --vpc-id vpc-123 \
  --service-name com.amazonaws.us-east-1.s3 \
  --vpc-endpoint-type Gateway
```

**Connection Pooling (Application Fix):**
```python
# Without pooling: new connection per request
for url in urls:
    response = requests.get(url)  # New TCP handshake each time

# With pooling: reuse connections
session = requests.Session()
adapter = requests.adapters.HTTPAdapter(
    pool_connections=10,
    pool_maxsize=100,
    pool_block=False
)
session.mount('http://', adapter)
for url in urls:
    response = session.get(url)  # Reuse from pool
```

**Reduce TIME_WAIT:**
```bash
# Enable port reuse
sysctl -w net.ipv4.tcp_tw_reuse=1

# Reduce TIME_WAIT duration
sysctl -w net.ipv4.tcp_fin_timeout=30

# Increase local port range
sysctl -w net.ipv4.ip_local_port_range="1024 65535"
```

---

## Scenario 6: Kubernetes Service Not Reachable

### Symptoms
- Service ClusterIP doesn't respond
- `curl <cluster-ip>:<port>` hangs or fails
- Pods are running and healthy

### Investigation Steps

**1. Verify Service Configuration**
```bash
kubectl get svc <service-name>
kubectl describe svc <service-name>

# Check:
# - ClusterIP assigned (not None unless headless)
# - Port and targetPort correct
# - Selector matches Pod labels
```

**2. Check Endpoints**
```bash
kubectl get endpoints <service-name>
kubectl describe endpoints <service-name>

# Should show Pod IPs:
# Subsets:
#   Addresses: 10.244.1.5, 10.244.2.10
#   Ports: 8080

# If empty: Selector doesn't match any Pods
```

**3. Check Pod Labels**
```bash
kubectl get pods -l <service-selector>

# Service selector:
#   app: api
#   tier: backend

# Pod labels must match exactly:
kubectl get pods --show-labels
```

**4. Check kube-proxy**
```bash
kubectl get pods -n kube-system -l k8s-app=kube-proxy
kubectl logs -n kube-system -l k8s-app=kube-proxy

# Look for:
# - "syncing iptables rules"
# - Errors creating iptables rules
```

**5. Check iptables Rules**
```bash
# On any node
iptables-save | grep <service-cluster-ip>
iptables-save | grep <service-name>

# Should see DNAT rules redirecting ClusterIP to Pod IPs
```

**6. Test from Different Locations**
```bash
# From a Pod in same namespace
kubectl exec <pod> -- curl -v <service-name>:<port>

# From a Pod in different namespace
kubectl exec <pod> -n other -- curl -v <service-name>.default.svc.cluster.local:<port>

# From host network
curl <cluster-ip>:<port>
```

### Common Causes

| Issue | Diagnosis | Fix |
|-------|-----------|-----|
| Selector mismatch | `kubectl get endpoints` empty | Fix service selector or pod labels |
| Pod not ready | Endpoints missing Pod IPs | Fix readiness probe |
| kube-proxy crashed | No iptables rules | Restart kube-proxy |
| NetworkPolicy blocks | Connection times out | Allow service traffic |
| CNI issue | No pod-to-pod routing | Restart CNI pods |

---

## Scenario 7: TLS Certificate Expiry Causing Outage

### Symptoms
- HTTPS connections failing with "certificate expired" or "unknown CA"
- Monitoring didn't catch expiry
- Affects external-facing services

### Investigation

**1. Check Certificate Expiry**
```bash
# Remote check
echo | openssl s_client -connect example.com:443 2>/dev/null \
  | openssl x509 -noout -dates

# Check full chain
echo | openssl s_client -connect example.com:443 -showcerts 2>/dev/null \
  | openssl x509 -noout -dates

# Check all certs in chain
echo | openssl s_client -connect example.com:443 2>/dev/null \
  | awk '/BEGIN CERTIFICATE/,/END CERTIFICATE/{print}' \
  | openssl x509 -noout -enddate
```

**2. Check Certificate in Kubernetes Secret**
```bash
kubectl get secret tls-secret -o jsonpath='{.data.tls\.crt}' \
  | base64 -d | openssl x509 -noout -dates

# Check all TLS secrets
for ns in $(kubectl get ns -o jsonpath='{.items[*].metadata.name}'); do
  for secret in $(kubectl get secret -n $ns -o jsonpath='{.items[*].metadata.name}'); do
    kubectl get secret $secret -n $ns -o jsonpath='{.data.tls\.crt}' 2>/dev/null \
      | base64 -d | openssl x509 -noout -enddate 2>/dev/null \
      && echo "  ^-- $ns/$secret"
  done
done
```

**3. Check Ingress Configuration**
```bash
kubectl get ingress -A
kubectl describe ingress <name> -n <namespace>

# Verify TLS secret reference
```

### Prevention

**Monitoring:**
```yaml
# Prometheus alert
- alert: TLSCertExpiry
  expr: probe_ssl_earliest_cert_expiry - time() < 86400 * 30
  for: 1h
  labels:
    severity: warning
  annotations:
    summary: "TLS certificate expires in 30 days"
```

**Automated Renewal (cert-manager):**
```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: example-com
spec:
  secretName: example-com-tls
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  dnsNames:
  - example.com
  - www.example.com
  renewBefore: 720h  # Renew 30 days before expiry
```

**Certificate Inventory:**
```bash
# Regular audit script
#!/bin/bash
for domain in $(cat domains.txt); do
  expiry=$(echo | openssl s_client -connect $domain:443 2>/dev/null \
    | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)
  echo "$domain expires: $expiry"
done
```

---

## Scenario 8: Pod Cannot Access External API

### Symptoms
- Pod can ping external hosts
- Pod can curl public websites
- Specific external API fails (timeout or SSL error)

### Investigation

**1. Check if NAT Gateway Exists**
```bash
# Private subnets need NAT Gateway for outbound
aws ec2 describe-nat-gateways --filter "Name=vpc-id,Values=<vpc-id>"

# Check route table
aws ec2 describe-route-tables --filters "Name=vpc-id,Values=<vpc-id>"

# Private subnet should have:
# 0.0.0.0/0 → nat-xxxxx
```

**2. Check Security Group Outbound Rules**
```bash
aws ec2 describe-security-groups --group-ids <pod-node-sg-id>

# Need outbound rule allowing HTTPS (443)
# Default: allow all outbound
```

**3. Check for SSL Inspection / Corporate Proxy**
```bash
kubectl exec <pod> -- curl -v https://api.example.com

# If "unknown CA": corporate MITM proxy
# Fix: Mount CA cert in pod

# If using proxy:
export HTTPS_PROXY=http://proxy.company.com:8080
curl https://api.example.com
```

**4. Check DNS Resolution**
```bash
kubectl exec <pod> -- dig api.example.com

# Ensure resolving to correct IP
# If internal DNS: check split-horizon config
```

**5. Check for NetworkPolicy**
```bash
kubectl get networkpolicy -n <namespace>
kubectl describe networkpolicy <name>

# Must allow egress to external IPs
```

### Resolution

**For Corporate Proxy:**
```yaml
# Pod spec
spec:
  containers:
  - name: app
    env:
    - name: HTTPS_PROXY
      value: "http://proxy.company.com:8080"
    - name: NO_PROXY
      value: "localhost,127.0.0.1,.svc.cluster.local"
    volumeMounts:
    - name: ca-certs
      mountPath: /etc/ssl/certs/company-ca.pem
      subPath: company-ca.pem
  volumes:
  - name: ca-certs
    configMap:
      name: company-ca-certs
```

**For VPC Endpoints:**
```bash
# If API supports VPC Endpoint (S3, DynamoDB, etc.)
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-123 \
  --service-name com.amazonaws.us-east-1.s3 \
  --vpc-endpoint-type Gateway
```

---

## Troubleshooting Command Reference

### Quick Diagnostics

```bash
# Is it down?
kubectl get pods -l app=<name>

# Can it reach?
kubectl exec <pod> -- curl -v http://<destination>

# Is DNS working?
kubectl exec <pod> -- nslookup <service>

# What's the latency?
kubectl exec <pod> -- mtr -rw <destination>

# Are connections established?
kubectl exec <pod> -- ss -tn | grep ESTAB

# Any dropped packets?
kubectl exec <pod> -- netstat -i

# Certificate status
echo | openssl s_client -connect <host>:443 2>/dev/null | openssl x509 -noout -dates
```

### Packet Capture in Kubernetes

```bash
# Using ephemeral debug container
kubectl debug -it <pod> --image=nicolaka/netshoot --target=<container>

# Or run tcpdump in existing pod (if image has it)
kubectl exec <pod> -- tcpdump -i eth0 -w /tmp/capture.pcap

# Copy out for analysis
kubectl cp <pod>:/tmp/capture.pcap ./capture.pcap

# Analyze in Wireshark
wireshark capture.pcap
```

### Log Analysis

```bash
# Application logs
kubectl logs <pod> -f

# Previous instance (if crashed)
kubectl logs <pod> --previous

# Multiple containers
kubectl logs <pod> -c <container-name>

# With timestamps
kubectl logs <pod> --timestamps=true

# Last N lines
kubectl logs <pod> --tail=100

# Since time
kubectl logs <pod> --since=1h

# Grep for errors
kubectl logs <pod> | grep -i error
```

---

# Document: Record root cause and resolution for future

---

## Scenario 9: gRPC Load Balancing Issues (The "Sticky Connection" Problem)

### Symptoms
- You have 10 pods for a gRPC service.
- One pod has 90% CPU usage; others have 5% usage.
- Standard Kubernetes `Service` (L4) is used for load balancing.

### Root Cause
gRPC uses **HTTP/2**, which maintains **long-lived TCP connections**. 
- A client establishes a connection to a Pod and keeps it open for thousands of requests.
- Kubernetes Service (iptables/ipvs) only balances the *connection initiation*.
- Once the connection is open, all traffic from that client stays on that specific Pod.

### Investigation
```bash
# Check connection distribution
for pod in $(kubectl get pods -l app=grpc-service -o name); do
  echo -n "$pod: "
  kubectl exec $pod -- ss -tn | grep :8080 | grep ESTAB | wc -l
done
```

### Resolution
1. **Client-Side Load Balancing:** The client gets the list of all Pod IPs (via a Headless Service) and manages the pool itself.
2. **L7 Proxy (Envoy/Istio):** Use a service mesh or an Ingress controller that understands gRPC. The proxy breaks the connection and re-balances *individual frames/requests* to different backends.
3. **Max Connection Age:** Set a limit in the gRPC server (e.g., `MaxConnectionAge = 30s`) to force clients to reconnect and re-balance naturally.

---

## Scenario 10: Asymmetric Routing in Hybrid Cloud (VPN/Direct Connect)

### Symptoms
- You can ping a server in your On-Prem data center from AWS, but you cannot establish a TCP connection.
- `traceroute` works one way but not the other.
- Firewalls on both ends show "Session Not Found" or "Illegal State."

### Root Cause: Asymmetric Routing
Packets take **Path A** from AWS to On-Prem, but the return packets take **Path B** from On-Prem to AWS.
- If Path B passes through a **stateful firewall** that never saw the initial `SYN` packet on Path A, the firewall drops the return `SYN-ACK` as an illegal state.

### Investigation
```bash
# On AWS Instance
tcpdump -n -i eth0 icmp or tcp port 80

# On On-Prem Server
tcpdump -n -i eth0 icmp or tcp port 80
```
Compare the source/destination IPs and MAC addresses to see if they match the expected ingress/egress points.

### Resolution
1. **Force Symmetric Routing:** Adjust BGP weights or Static Routes to ensure the same path is used for both directions.
2. **Source NAT (SNAT):** Use SNAT at the gateway so the return traffic *must* go back to the NAT IP, forcing it through the same path.
3. **VPC Ingress Routing:** (AWS specific) Use Ingress Routing tables to force traffic through a specific Appliance (Firewall) regardless of the route.

---

## Summary: Systematic Approach

1. **Define the problem:** What exactly is failing? When did it start?
2. **Reproduce:** Can you trigger it consistently?
3. **Isolate:** Is it L3 (ping), L4 (port), L7 (application)?
4. **Compare:** What changed? What's different between working and failing cases?
5. **Measure:** Collect metrics, logs, packet captures
6. **Hypothesize:** Form theory based on evidence
7. **Test:** Try fix, verify it resolves the issue
8. **Document:** Record root cause and resolution for future
