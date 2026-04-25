# Observability & SRE Cheatsheet

Quick reference for Prometheus, Grafana, logging, tracing, alerting, and SRE practices.

***

## Prometheus

```bash
# Query API (direct HTTP)
curl 'http://prometheus:9090/api/v1/query?query=up'
curl 'http://prometheus:9090/api/v1/query_range?query=rate(http_requests_total[5m])&start=2024-01-01T00:00:00Z&end=2024-01-01T01:00:00Z&step=60'

# Target health
curl 'http://prometheus:9090/api/v1/targets' | jq '.data.activeTargets[] | {job: .labels.job, health: .health}'

# Reload config (if --web.enable-lifecycle enabled)
curl -X POST http://prometheus:9090/-/reload

# Check config validity
promtool check config prometheus.yml

# Check rules
promtool check rules rules/*.yml

# Test rules against data
promtool test rules tests/*.yml
```

### Key PromQL Patterns

```promql
# === COUNTERS (always use rate() or increase()) ===
rate(http_requests_total[5m])                           # Per-second rate
increase(http_requests_total[1h])                       # Total increase
irate(http_requests_total[5m])                          # Instant rate

# === GAUGES (use directly) ===
node_memory_MemAvailable_bytes
container_memory_working_set_bytes

# === HISTOGRAMS ===
histogram_quantile(0.95, rate(http_duration_seconds_bucket[5m]))   # p95
histogram_quantile(0.99, sum by (le, service) (rate(http_duration_seconds_bucket[5m])))  # p99 per service

# === AGGREGATIONS ===
sum by (namespace) (rate(http_requests_total[5m]))      # Sum by label
avg by (instance) (node_cpu_seconds_total)              # Average
topk(5, rate(http_requests_total[5m]))                  # Top 5
bottomk(3, container_memory_usage_bytes)                # Bottom 3
count by (job) (up)                                     # Count targets

# === ERROR RATE ===
rate(http_requests_total{status=~"5.."}[5m]) /
rate(http_requests_total[5m]) * 100

# === LATENCY ===
histogram_quantile(0.95,
  sum by (le, service) (
    rate(http_request_duration_seconds_bucket[5m])
  )
)

# === SLO BURN RATE ===
# Error budget burn rate — 1 = burning at exactly the right rate
(
  rate(http_requests_total{status=~"5.."}[1h]) /
  rate(http_requests_total[1h])
) / 0.001  # 0.1% error budget

# === KUBERNETES ===
# Pod CPU usage %
sum(rate(container_cpu_usage_seconds_total{container!=""}[5m])) by (pod) /
sum(kube_pod_container_resource_limits{resource="cpu"}) by (pod)

# Node memory pressure
1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)

# PVC usage %
kubelet_volume_stats_used_bytes / kubelet_volume_stats_capacity_bytes * 100

# Deployment replica mismatch
kube_deployment_spec_replicas != kube_deployment_status_ready_replicas
```

***

## Alertmanager

```bash
# API operations
curl http://alertmanager:9093/api/v2/alerts              # List active alerts
curl http://alertmanager:9093/api/v2/silences             # List silences

# Create silence (via API)
curl -X POST http://alertmanager:9093/api/v2/silences \
  -H "Content-Type: application/json" \
  -d '{
    "matchers": [{"name": "alertname", "value": "HighErrorRate", "isRegex": false}],
    "startsAt": "2024-01-01T00:00:00Z",
    "endsAt": "2024-01-01T02:00:00Z",
    "comment": "Planned maintenance",
    "createdBy": "ops-team"
  }'

# amtool (CLI)
amtool alert                                             # List active alerts
amtool alert query alertname=HighCPU                    # Filter alerts
amtool silence add alertname=HighCPU --duration=2h --comment="maintenance"
amtool silence list                                      # List silences
amtool silence expire <silence-id>                       # Remove silence
amtool config routes show                                # Show routing tree
amtool config routes test --verify-receivers alertname=HighCPU  # Test routing
```

***

## Grafana

```bash
# Grafana API
GRAFANA_URL="http://grafana:3000"
AUTH="admin:admin"

# Dashboards
curl -s "$GRAFANA_URL/api/dashboards/home" -u $AUTH
curl -s "$GRAFANA_URL/api/search?type=dash-db" -u $AUTH | jq '.[].title'
curl -s "$GRAFANA_URL/api/dashboards/uid/my-dashboard" -u $AUTH  # Get by UID

# Import dashboard
curl -X POST "$GRAFANA_URL/api/dashboards/import" \
  -H "Content-Type: application/json" \
  -u $AUTH \
  -d @dashboard.json

# Data sources
curl -s "$GRAFANA_URL/api/datasources" -u $AUTH | jq '.[].name'

# Users
curl -s "$GRAFANA_URL/api/users" -u $AUTH | jq '.[].login'
```

***

## Logging — Loki

```bash
# LogQL queries
{namespace="production"} |= "error"                     # Contains "error"
{job="nginx"} != "healthz"                              # Exclude healthz
{app="api"} | json | level="error"                      # Parse JSON, filter level
{app="api"} | json | duration > 1s                      # Slow requests
{app="api"} | logfmt | status_code="500"               # logfmt parsing

# Count errors per minute
count_over_time({namespace="production"} |= "error" [1m])

# Rate of log lines
rate({namespace="production"}[5m])

# LogCLI
logcli query '{app="api"} |= "ERROR"'
logcli query '{app="api"}' --since=1h
logcli query '{app="api"}' --from="2024-01-01T00:00:00Z" --to="2024-01-01T01:00:00Z"
logcli labels                                            # List all labels
logcli labels app                                        # List values for label
```

***

## Tracing — Jaeger / Tempo

```bash
# Jaeger API
curl "http://jaeger:16686/api/services"                  # List services
curl "http://jaeger:16686/api/traces?service=api-server&limit=20"  # Recent traces
curl "http://jaeger:16686/api/traces?service=api-server&minDuration=1s"  # Slow traces
curl "http://jaeger:16686/api/traces/{traceID}"          # Get specific trace

# Tempo (via Grafana HTTP API)
curl "http://tempo:3200/api/traces/{traceID}"
curl "http://tempo:3200/api/search?service=api-server&limit=20"
curl "http://tempo:3200/api/search/tag/http.status_code/values"  # Tag values

# OpenTelemetry collector health
curl http://otel-collector:13133/                        # Health check
curl http://otel-collector:8888/metrics                  # Collector self-metrics
```

***

## Node Exporter — Key Metrics

```promql
# CPU usage per core
1 - avg by (cpu) (rate(node_cpu_seconds_total{mode="idle"}[5m]))

# Memory usage %
1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)

# Disk I/O wait
rate(node_disk_io_time_seconds_total[5m])

# Disk reads/writes per second
rate(node_disk_reads_completed_total[5m])
rate(node_disk_writes_completed_total[5m])

# Network traffic
rate(node_network_receive_bytes_total{device!="lo"}[5m])
rate(node_network_transmit_bytes_total{device!="lo"}[5m])

# Open file descriptors
node_filefd_allocated / node_filefd_maximum

# Disk space
(node_filesystem_size_bytes - node_filesystem_free_bytes) /
node_filesystem_size_bytes * 100

# Load average vs CPU count
node_load1 / count without(cpu,mode) (node_cpu_seconds_total{mode="idle"})
```

***

## SRE Practices

### SLI / SLO / Error Budget

```
SLI (Service Level Indicator) — the metric
  "Ratio of successful HTTP requests in the last 30 days"

SLO (Service Level Objective) — the target
  "99.9% of requests must be successful"

Error Budget — the allowed failures
  "0.1% = 43.8 minutes of downtime per month"

Burn Rate — how fast you're spending the budget
  1.0 = spending exactly on track
  2.0 = double the spend → budget exhausted in 15 days
  14.4 = budget exhausted in 2 hours → page immediately
```

### Incident Severity Levels

| Level | Definition | Response |
|:---|:---|:---|
| **P0** | Complete outage — no users served | Immediate page, all hands |
| **P1** | Major degradation — >25% users impacted | Page on-call, 15 min response |
| **P2** | Partial impact — specific feature/region | Notify on-call, 1 hour response |
| **P3** | Minor / no user impact | Ticket, fix in next sprint |

### MTTR Calculation

```
MTTR = (Total downtime) / (Number of incidents)

Example:
  3 incidents in a month
  Downtime: 10 min + 25 min + 5 min = 40 min
  MTTR = 40 / 3 = 13.3 minutes
```

***

## On-Call Runbook Checklist

```
1. DETECT
   □ What alert fired? What is the user impact?
   □ When did it start?
   □ Check: kubectl get pods -A | grep -v Running
   □ Check: kubectl get events -A --sort-by=.lastTimestamp | tail -20

2. TRIAGE
   □ Is it getting worse, stable, or improving?
   □ Which component? (infra, app, dependency)
   □ Any recent deployments? (check ArgoCD, git log)

3. MITIGATE (reduce impact first)
   □ Can you roll back? kubectl rollout undo deployment/<name>
   □ Can you scale up? kubectl scale deployment/<name> --replicas=10
   □ Can you redirect traffic? (feature flag, LB weight)

4. INVESTIGATE
   □ Logs: kubectl logs <pod> --previous
   □ Metrics: Grafana → check at incident start time
   □ Traces: Jaeger → find slow/erroring traces

5. RESOLVE
   □ Apply fix (with peer review if time allows)
   □ Verify fix: watch the error rate drop in Grafana
   □ Update status page

6. FOLLOW-UP (within 48 hours)
   □ Write blameless post-mortem
   □ Document timeline
   □ 3-5 action items with owners and due dates
```

***

## `kubectl top` & Metrics Server

```bash
# Resource usage
kubectl top nodes                                        # Node CPU/memory
kubectl top pods -A                                      # All pods
kubectl top pods -A --sort-by=cpu                       # Sort by CPU
kubectl top pods -A --sort-by=memory                    # Sort by memory
kubectl top pods -n production --containers              # Per-container breakdown

# Requests vs Limits vs Actual
kubectl get pods -A -o custom-columns=\
  NAMESPACE:.metadata.namespace,\
  NAME:.metadata.name,\
  CPU_REQ:.spec.containers[0].resources.requests.cpu,\
  MEM_REQ:.spec.containers[0].resources.requests.memory,\
  CPU_LIM:.spec.containers[0].resources.limits.cpu,\
  MEM_LIM:.spec.containers[0].resources.limits.memory
```

***

## curl — HTTP Testing

```bash
# Response time breakdown
curl -w "\n\nDNS:%{time_namelookup}s TCP:%{time_connect}s TLS:%{time_appconnect}s TTFB:%{time_starttransfer}s Total:%{time_total}s\n" \
  -o /dev/null -s https://api.company.com/health

# Test headers
curl -I https://api.company.com                          # Headers only
curl -v https://api.company.com                          # Verbose (full handshake)
curl -H "Authorization: Bearer $TOKEN" https://api.company.com/data

# POST with JSON
curl -X POST https://api.company.com/events \
  -H "Content-Type: application/json" \
  -d '{"event": "deploy", "version": "v1.2.3"}'

# Follow redirects + show final URL
curl -L -w "%{url_effective}\n" https://short.link/abc
```
