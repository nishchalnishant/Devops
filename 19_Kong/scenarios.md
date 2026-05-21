# Kong Gateway — Scenarios & Troubleshooting

These scenarios outline real-world production incidents, latency bottlenecks, and traffic routing configurations, walking through isolation steps, root causes, and technical resolutions.

---

## Scenario 1: Debugging Data Plane Synchronization Delays in Hybrid Mode

### Incident Overview
A platform team updates a billing route plugin configuration via the Control Plane Admin API. However, client requests targeting the Billing service on the public Data Plane (DP) nodes continue to receive rate-limiting headers based on the *old* configuration. There is a synchronization lag between the Control Plane and Data Plane nodes.

### Troubleshooting Workflow

#### 1. Confirm Control Plane Status and Log Output
Log in to the Control Plane (CP) node and check the CP status and NGINX cluster logs:
```bash
# Check CP configuration liveness
curl -i http://localhost:8100/status

# Look for cluster connection handshake errors in CP logs
tail -n 100 /usr/local/kong/logs/error.log | grep -E "(handshake|cluster|mTLS)"
```
* **Possible Diagnostic**: `CP logs show "SSL handshake failed" or "peer closed connection".`

#### 2. Audit Cluster Connection Ports & Certificates
Hybrid mode communication relies on mutual TLS (mTLS) over port `8005` (Cluster Control) and `8006` (Status).
```bash
# From the Data Plane pod, verify connectivity to CP on port 8005
nc -zv control-plane.internal 8005

# Verify certificate expiration on both planes
openssl x509 -in /etc/kong/certs/cluster.crt -text -noout | grep "Not After"
```
* **Common Cause**:
  * Blocked firewall rules or security groups on port `8005` between the DP subnets and the CP.
  * Expired cluster certs (`cluster.crt` / `cluster.key`) causing TLS negotiation failure.

#### 3. Inspect Data Plane Sync Status from Control Plane
Query the Control Plane's status endpoint to see connection records of all registered DP nodes:
```bash
curl -s http://localhost:8001/clustering/data-planes
```
* **Expected Output**:
  ```json
  {
    "data": [
      {
        "id": "7fa1202e-a3bb-4c2c-88ab-f2187f58a8a4",
        "hostname": "data-plane-pod-9b1",
        "ip": "10.244.3.45",
        "sync_status": "out_of_sync",
        "config_hash": "2f42a1979bca8837bc2cbf25b689aa01"
      }
    ]
  }
  ```
  * Note that `"sync_status": "out_of_sync"` confirms that DP config hashes do not match the CP target hash.

### Resolution Steps
1. **Renew Certificates**: If expired, generate new mTLS certs and distribute them securely via Kubernetes secrets or HashiCorp Vault.
2. **Open Firewall Rules**: Ensure security groups allow bidirectional traffic on port `8005` between Data Plane nodes and Control Plane nodes.
3. **Restart DP Services**: Force DP nodes to establish a fresh connection and reload the configuration hash:
   ```bash
   kong restart
   ```

---

## Scenario 2: Isolating Latency Bottlenecks: Gateway Overhead vs. Slow Backends

### Incident Overview
Users complain of high response latency (exceeding 800ms) on a critical mobile API route. Developers claim the backend microservice responses take under 50ms. The platform team needs to determine whether Kong Gateway or the backend upstream target is causing the delay.

### Troubleshooting Workflow

#### 1. Analyze Latency Headers in Logs
By default, Kong injects latency tracking headers into proxy responses:
* `X-Kong-Proxy-Latency`: Time spent inside Kong processing request plugins (in milliseconds).
* `X-Kong-Upstream-Latency`: Time spent by the backend target responding to Kong (in milliseconds).

Perform a test curl request to extract these values:
```bash
curl -i -X GET https://api.company.com/v1/users/profile -H "Authorization: Bearer <token>"
```
* **Sample Headers**:
  ```
  X-Kong-Proxy-Latency: 755
  X-Kong-Upstream-Latency: 45
  ```
  * **Analysis**: Since `Proxy-Latency` is 755ms and `Upstream-Latency` is 45ms, the bottleneck lives **inside the Kong Gateway layer itself**.

#### 2. Identify the Bottleneck Plugin
If latency is high in the proxy layer, it is typically caused by a synchronous, blocking network call inside a plugin.
* Review global and route-specific plugins:
  ```bash
  curl -s http://localhost:8001/routes/profile-route/plugins
  ```
* Look for:
  * **LDAP or OAuth2 plugins** making synchronous DB requests.
  * **Rate Limiting** using a `redis` policy where the Redis cluster is experiencing network latency or queueing.
  * **Custom Lua plugins** executing blocking I/O calls (e.g. standard Lua socket calls instead of OpenResty’s non-blocking cosockets).

#### 3. Verify CPU Resource Contention
High gateway latency can also stem from resource exhaustion on NGINX worker nodes:
```bash
# Check CPU load on gateway instances
top -b -n 1 | grep -E "(Cpu|nginx)"
```
* If workers are throttled or have high context switching, NGINX is blocked waiting for system resources.

### Resolution Steps
1. **Migrate Rate-Limiting Policy**: If Redis calls are the bottleneck, adjust the plugin's `redis_timeout` down, implement connection pooling, or shift to a `local` (in-memory) policy if exact limits aren't mandatory.
2. **Optimize Custom Plugins**: Rewrite custom Lua plugin operations to use `ngx.socket.tcp` (OpenResty cosockets) to prevent thread-blocking during HTTP/DB operations.
3. **Scale Resources**: Align NGINX worker counts in `kong.conf` (`nginx_worker_processes = auto`) to match CPU allocation, and increase Pod CPU limits if CPU throttling occurs.

---

## Scenario 3: Designing Safe Canary Release Routing with Active Health Checks

### Objective
Design and implement a zero-downtime Canary routing flow to send 90% of traffic to the stable service (`payment-v1`) and 10% of traffic to the new candidate (`payment-v2`). Ensure that if the canary service fails, traffic automatically fails back to the stable instances without manual intervention.

### Implementation Blueprint

```
Client Traffic
      │
      ▼
┌──────────────┐
│ Kong Route   │ (Path: /v2/payments)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Kong Service │ (Host: payment-upstream)
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────────┐
│                Kong Upstream                 │
│              (payment-upstream)              │
│       ┌──────────────────────────────┐       │
│       │                              │       │
│       ▼                              ▼       │
│  ┌──────────┐                   ┌──────────┐ │
│  │ Target 1 │ (v1 stable)       │ Target 2 │ │ (v2 canary)
│  │ IP: 10..5│ Weight: 900       │ IP: 10..6│ │ Weight: 100
│  └──────────┘                   └──────────┘ │
│       │                              │       │
│       ▼                              ▼       │
│ Active checks (Pass)         Active checks (Fail)
│ Keep routing                 Disable Target 2
└──────────────────────────────────────────────┘
```

#### 1. Define the Upstream and Targets with Weights
Configure the load balancer pool with a total weight of 1000 to enable precise 90/10 traffic splits:
```bash
# Create the upstream
curl -X POST http://localhost:8001/upstreams \
  --data name=payment-upstream

# Add Stable Target (v1) with a weight of 900
curl -X POST http://localhost:8001/upstreams/payment-upstream/targets \
  --data target=10.0.0.5:8080 \
  --data weight=900

# Add Canary Target (v2) with a weight of 100
curl -X POST http://localhost:8001/upstreams/payment-upstream/targets \
  --data target=10.0.0.6:8080 \
  --data weight=100
```

#### 2. Configure Active Health Checks for Safe Failover
Configure Kong to poll both backend targets actively. If a target fails to respond with a `200 OK` for three consecutive checks, drop its weight to zero immediately:
```bash
curl -X PATCH http://localhost:8001/upstreams/payment-upstream \
  --data "healthchecks.active.healthy.interval=5" \
  --data "healthchecks.active.healthy.successes=2" \
  --data "healthchecks.active.unhealthy.interval=2" \
  --data "healthchecks.active.unhealthy.http_failures=3" \
  --data "healthchecks.active.http_path=/healthz"
```

#### 3. Map Service and Route to Upstream Host
```bash
# Create Service pointing to the Upstream load balancer name
curl -X POST http://localhost:8001/services \
  --data name=payment-service \
  --data host=payment-upstream

# Map public routing path
curl -X POST http://localhost:8001/services/payment-service/routes \
  --data name=payment-route \
  --data paths[]=/v2/payments
```

### Result and Verification
* **Under Normal Conditions**: Out of every 10 requests, 9 route to `10.0.0.5:8080` (v1 stable) and 1 routes to `10.0.0.6:8080` (v2 canary).
* **Under Failure Conditions**: If `payment-v2` begins crash-looping, Kong's active health checks fail. Within 6 seconds (3 failures × 2s interval), Kong marks `10.0.0.6` as unhealthy and automatically shifts 100% of request traffic to `10.0.0.5`.

***

**Back to Module:** [Overview](README.md) | [Detailed Notes](notes/kong-architecture-and-plugins.md) | [Cheatsheet](cheatsheet.md) | [Interview Questions](interview.md)
