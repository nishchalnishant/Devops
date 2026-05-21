# Observability & SRE — Deep Dive Notes

```
Observability & SRE — Deep Dive Notes
├── Three Pillars Internals
│   ├── Metrics (Prometheus): scrape → TSDB (2h chunks + WAL) → Counter / Gauge / Histogram / Summary
│   ├── Histogram vs Summary: histogram aggregates across replicas; summary is client-side only
│   ├── Logs (Loki): Promtail → Distributor → Ingester → Object Store (S3/GCS); label-only index
│   └── Traces (OpenTelemetry): Trace = tree of spans; spanId + parentSpanId; BatchSpanProcessor + OTLP
├── SLO / SLI / Error Budget
│   ├── SLI: measurable indicator (e.g., % requests < 200ms)
│   ├── SLO: target for the SLI (e.g., 99.9% over 30d)
│   ├── Error Budget: 100% - SLO = allowed failure envelope (43.8 min/month at 99.9%)
│   └── Burn Rate: 14.4x = depletes 30d budget in 2d → page; 6x → page; 3x → ticket
├── Multi-Window Multi-Burn-Rate Alerting
│   ├── Critical (14.4x): 1h + 5m windows → page immediately
│   ├── High (6x): 6h + 30m windows → page
│   └── Medium (3x): 3d + 6h windows → ticket
├── PromQL Advanced Patterns
│   ├── rate() / irate() / increase() for counters
│   ├── histogram_quantile(0.99, sum by (le, service) (rate(..._bucket[5m])))
│   ├── predict_linear for disk exhaustion
│   ├── subquery: max_over_time((rate(...)[1h:5m]))
│   └── recording rules: pre-compute to reduce dashboard query load
├── Prometheus Operator / kube-prometheus-stack
│   ├── ServiceMonitor: selector → endpoints → metricRelabelings (drop Go runtime metrics)
│   └── PrometheusRule: alerting rules as CRD with release label matching
├── Alertmanager Routing
│   ├── group_by, group_wait, group_interval, repeat_interval
│   ├── routes: match severity=page → pagerduty; match_re team → slack
│   └── inhibit_rules: silence warning if page fires for same alert
├── Distributed Tracing Sampling
│   ├── Head-based: decision at trace start; misses rare errors
│   ├── Tail-based: decision after completion; keeps slow/errored; requires buffering
│   └── OTel Collector tail_sampling: errors-policy + slow-policy + probabilistic fallback
├── eBPF Observability
│   ├── Zero-instrumentation: hooks into kprobes/tracepoints → BPF map → user-space daemon
│   ├── Cilium: eBPF CNI + no kube-proxy; Hubble: per-flow network visibility
│   ├── Pixie: auto HTTP/gRPC/MySQL/Redis tracing via eBPF
│   └── Parca: continuous CPU profiling; Tetragon: runtime security enforcement
├── Chaos Engineering Maturity
│   ├── Level 1-5: manual → semi-automated → staging → production canary → auto-abort on SLO breach
│   └── Chaos Mesh: PodChaos, NetworkChaos with cron schedule and SLO-linked abort
├── Incident Response
│   ├── SEV1: revenue impact → immediate page; SEV2: degraded → team lead; SEV3 → ticket
│   ├── Lifecycle: Detect → Triage → Mitigate → Resolve → Blameless Post-mortem (48-72h)
│   └── Toil < 50%: count manual pages, runbook steps, resolution time for automatable alerts
└── Key Gotchas
    ├── rate() on gauge → garbage (use deriv() or delta())
    ├── Label cardinality: user_id as label kills Prometheus
    ├── histogram_quantile: +Inf bucket unreliable; bucket boundaries fixed at instrumentation
    ├── for: clause resets on flap → flapping alerts never page
    └── Loki without JSON: regex at query time is slow and brittle
```

## First Principles

Observability is not monitoring — monitoring tells you a system is down; observability tells you why. The three pillars (metrics, logs, traces) are complementary: metrics alert you, logs explain what happened, traces show where time was spent. SLOs are contracts with users — error budgets make reliability a shared engineering problem, not a ops problem. Toil is the enemy of reliability: every repetitive manual action is a reliability debt that compounds.

## The Three Pillars — Internals

### Metrics (Prometheus)

```
Application / Node
    │
    ├── Exposes /metrics endpoint (text format)
    │       # HELP http_requests_total Total HTTP requests
    │       # TYPE http_requests_total counter
    │       http_requests_total{method="GET",status="200"} 1234
    │
Prometheus Server
    │
    ├── Scrapes every scrape_interval (default 15s)
    ├── Stores as time series: (metric_name + labels) → (timestamp, float64)
    ├── TSDB: chunks of 2h in memory, compacted to blocks on disk
    │       Block: dir with chunks/, index/, meta.json, tombstones
    ├── Retention: --storage.tsdb.retention.time (default 15d)
    └── WAL (Write-Ahead Log): prevents data loss on crash
```

**Metric types:**

| Type | Description | Example |
|------|-------------|---------|
| Counter | Monotonically increasing | `http_requests_total` |
| Gauge | Can go up or down | `memory_usage_bytes` |
| Histogram | Bucketed observations + sum + count | `http_duration_seconds_bucket{le="0.1"}` |
| Summary | Pre-calculated quantiles (client-side) | `rpc_duration_seconds{quantile="0.99"}` |

**Why Histogram > Summary for SLOs:**
- Summary quantiles are calculated in the application — you can't aggregate across replicas.
- Histogram buckets can be aggregated with `sum()` and quantile calculated server-side with `histogram_quantile()`.

### Logs (Loki / ELK)

```
Loki Architecture:
Application → Promtail (log shipper) → Loki Distributor
                                            │
                                      Hash ring (consistent hashing)
                                            │
                                       Ingester (writes chunks to memory)
                                            │
                                       Object Store (S3/GCS) — chunks + index
                                            │
                                       Querier → Grafana
```

**Loki key difference from Elasticsearch:** Loki only indexes labels (like Prometheus), not the full log line content. This means:
- Storage is 10-100x cheaper
- Queries are slower for full-text search (reads raw chunks)
- Best for logs you can filter by labels first (pod, namespace, app)

### Traces (OpenTelemetry / Jaeger / Tempo)

```
Request spans:
[Frontend        100ms                                              ]
    [API Gateway  80ms                                             ]
        [Auth service  15ms]
        [Backend       60ms                        ]
            [DB query   45ms                  ]
                [slow!]

Trace = tree of spans
Span = {traceId, spanId, parentSpanId, operation, start, duration, tags, logs}
```

**OpenTelemetry SDK instrumentation:**
```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

provider = TracerProvider()
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint="otel-collector:4317")))
trace.set_tracer_provider(provider)

tracer = trace.get_tracer("my-service")

with tracer.start_as_current_span("process-order") as span:
    span.set_attribute("order.id", order_id)
    span.set_attribute("order.amount", amount)
    result = process(order_id)
    span.set_attribute("order.status", result.status)
```

***

## SLO / SLI / Error Budget — Mechanics

```
SLI (Service Level Indicator): a metric that measures service behavior
    e.g., "proportion of HTTP requests completing in < 200ms"

SLO (Service Level Objective): the target for the SLI
    e.g., "99.9% of requests must complete in < 200ms over 30 days"

Error Budget: 100% - SLO = 0.1% = 43.8 minutes/month allowed downtime

Error Budget Burn Rate: how fast you're consuming the error budget
    1x = consuming at exactly SLO rate (sustainable)
    14.4x = consuming 14.4x faster → depletes 30-day budget in 2 days
```

### Multi-window multi-burn-rate alerting (Google's approach)

Alert when error budget is burning too fast to survive:

| Severity | Burn rate | Window 1 | Window 2 | Budget consumed in |
|----------|-----------|----------|----------|--------------------|
| Page (critical) | 14.4x | 1h | 5m | 2 days |
| Page (high) | 6x | 6h | 30m | 5 days |
| Ticket (medium) | 3x | 3d | 6h | 10 days |
| Ticket (low) | 1x | — | — | 30 days (no alert) |

```yaml
# Prometheus alert for 14.4x burn rate (critical SLO burn)
- alert: SLOBurnRateCritical
  expr: |
    (
      sum(rate(http_requests_total{status=~"5.."}[1h])) /
      sum(rate(http_requests_total[1h]))
    ) > 14.4 * 0.001   # 14.4x * error_rate_target (0.1%)
    and
    (
      sum(rate(http_requests_total{status=~"5.."}[5m])) /
      sum(rate(http_requests_total[5m]))
    ) > 14.4 * 0.001
  for: 2m
  labels:
    severity: page
  annotations:
    summary: "SLO burn rate critical — error budget depletes in 2 days"
```

***

## PromQL — Advanced Patterns

```promql
# Request rate with 5-minute window
rate(http_requests_total[5m])

# Error ratio
sum(rate(http_requests_total{status=~"5.."}[5m]))
/ sum(rate(http_requests_total[5m]))

# P99 latency (requires histogram metric)
histogram_quantile(0.99,
  sum by (le, service) (
    rate(http_request_duration_seconds_bucket[5m])
  )
)

# Aggregation — top 5 services by request rate
topk(5,
  sum by (service) (
    rate(http_requests_total[5m])
  )
)

# Memory usage percent
(
  (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes)
  / node_memory_MemTotal_bytes
) * 100

# Predict disk exhaustion in 4 hours using linear regression
predict_linear(node_filesystem_avail_bytes{mountpoint="/"}[1h], 4*3600) < 0

# Subquery: evaluate a range query over a window
max_over_time(
  (rate(http_requests_total[5m]))[1h:5m]
)

# Recording rule (pre-compute for dashboard performance)
- record: job:http_requests:rate5m
  expr: sum by (job) (rate(http_requests_total[5m]))
```

***

## Prometheus Operator / kube-prometheus-stack

```yaml
# ServiceMonitor — tells Prometheus how to scrape a Service
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: my-app
  namespace: monitoring
  labels:
    release: prometheus   # must match Prometheus selector
spec:
  selector:
    matchLabels:
      app: my-app
  namespaceSelector:
    matchNames: [production]
  endpoints:
  - port: metrics
    path: /metrics
    interval: 15s
    scrapeTimeout: 10s
    honorLabels: false
    metricRelabelings:
    - sourceLabels: [__name__]
      regex: 'go_.*'       # drop Go runtime metrics
      action: drop

# PrometheusRule — alerting rules as CRD
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: my-app-alerts
  labels:
    release: prometheus
spec:
  groups:
  - name: my-app.rules
    interval: 30s
    rules:
    - alert: HighErrorRate
      expr: |
        sum(rate(http_requests_total{job="my-app",status=~"5.."}[5m])) /
        sum(rate(http_requests_total{job="my-app"}[5m])) > 0.01
      for: 5m
      labels:
        severity: warning
        team: backend
```

***

## Alertmanager — Routing and Silencing

```yaml
# alertmanager.yml
global:
  slack_api_url: 'https://hooks.slack.com/...'

route:
  group_by: ['alertname', 'cluster', 'namespace']
  group_wait: 30s        # wait before sending first alert in a group
  group_interval: 5m     # wait before sending updates
  repeat_interval: 3h    # re-notify if still firing
  receiver: default
  routes:
  - match:
      severity: page
    receiver: pagerduty
    continue: false      # stop routing after match
  - match_re:
      team: (backend|api)
    receiver: slack-backend

receivers:
- name: default
  slack_configs:
  - channel: '#alerts'
    text: '{{ template "slack.message" . }}'

- name: pagerduty
  pagerduty_configs:
  - service_key: '$PD_SERVICE_KEY'
    description: '{{ .GroupLabels.alertname }}'

inhibit_rules:
- source_match:
    severity: page
  target_match:
    severity: warning
  equal: [alertname, cluster, namespace]  # warning silenced if page fires for same alert
```

***

## Distributed Tracing — Sampling Strategies

| Strategy | Description | Trade-off |
|----------|-------------|-----------|
| Head-based (probabilistic) | Decision at trace start; e.g., 1% sampling | Misses rare errors |
| Tail-based | Decision after trace completes; keep slow/errored traces | Needs buffering (Tempo, Jaeger) |
| Rate limiting | N traces/sec per service | Even sampling regardless of load |

**Tail-based sampling with OpenTelemetry Collector:**
```yaml
processors:
  tail_sampling:
    decision_wait: 10s
    num_traces: 100000
    policies:
    - name: errors-policy
      type: status_code
      status_code: {status_codes: [ERROR]}
    - name: slow-policy
      type: latency
      latency: {threshold_ms: 1000}
    - name: probabilistic-policy
      type: probabilistic
      probabilistic: {sampling_percentage: 5}
```

***

## eBPF Observability

eBPF programs run in the Linux kernel without modifying application code. They hook into kernel events (syscalls, network stack, scheduler) and emit structured data.

```
Application (any language, no instrumentation)
    │
    ▼ syscall (read, write, connect, accept...)
Linux Kernel
    │
    ├── eBPF program (attached to kprobe/tracepoint)
    │       ├── Reads context: PID, comm, fd, args
    │       ├── Writes to BPF map (ring buffer)
    │       └── Returns in nanoseconds
    │
BPF Map → User-space daemon (Cilium, Pixie, Parca)
    │
    └── Emits metrics/traces to Prometheus/OTLP
```

**Tools:**

| Tool | Purpose |
|------|---------|
| **Cilium** | eBPF-based CNI with L7-aware network policies, no kube-proxy |
| **Hubble** | Cilium's observability layer — per-flow network visibility |
| **Pixie** | Auto-instrumentation via eBPF: request tracing for HTTP, gRPC, Redis |
| **Parca** | Continuous profiling — CPU flame graphs without code changes |
| **Tetragon** | Runtime security enforcement (Falco alternative with enforcement) |

```bash
# Install Pixie and get instant HTTP traces
px deploy
px run px/http_data            # all HTTP requests with latency by pod
px run px/mysql_data           # MySQL queries with duration
px run px/net_flow_graph       # service dependency map from network data
```

***

## Chaos Engineering

```
Chaos Maturity Model:
1. Manual chaos (GameDay: inject failure manually)
2. Semi-automated (runbooks + manual trigger)
3. Automated chaos in staging
4. Automated chaos in production (canary population only)
5. Fully automated with automatic abort on SLO breach
```

```yaml
# Chaos Mesh — inject pod failure
apiVersion: chaos-mesh.org/v1alpha1
kind: PodChaos
metadata:
  name: pod-failure-example
spec:
  action: pod-failure     # pod-failure, pod-kill, container-kill
  mode: fixed-percent
  value: "25"             # affect 25% of selected pods
  selector:
    namespaces: [production]
    labelSelectors:
      app: checkout
  duration: 5m
  scheduler:
    cron: "@every 30m"   # run every 30 minutes

# Network chaos: 100ms latency + 10% jitter between services
apiVersion: chaos-mesh.org/v1alpha1
kind: NetworkChaos
metadata:
  name: network-delay
spec:
  action: delay
  mode: all
  selector:
    namespaces: [production]
    labelSelectors:
      app: payment-service
  delay:
    latency: 100ms
    jitter: 10ms
    correlation: "25"
  direction: to
  target:
    selector:
      namespaces: [production]
      labelSelectors:
        app: database
  duration: 10m
```

**Abort conditions:** Always define an SLO-linked abort. In Chaos Mesh, use `Workflow` with conditions that query Prometheus and abort if error rate exceeds SLO threshold.

***

## Incident Response and SRE Practice

```
Incident lifecycle:
Detect (alert fires)
    │
    ▼
Triage (severity classification)
    │  SEV1: revenue impact / full outage → page on-call immediately
    │  SEV2: degraded service / partial outage → page team lead
    │  SEV3: minor impact / single user → ticket
    │
    ▼
Mitigate (stop the bleeding)
    │  Prefer rollback over forward-fix under pressure
    │  Feature flags to disable bad code path
    │
    ▼
Resolve (service restored to SLO)
    │
    ▼
Post-mortem (blameless, within 48-72h)
    │  Timeline, contributing factors, action items with owners + dates
    │  No blame, no "human error" as root cause
```

**Toil quantification:**
```
Toil = work that is manual, repetitive, automatable, tactical, lacking enduring value
SRE principle: toil should be < 50% of a team's time

Measure toil:
- Count on-call pages that required manual action (not auto-resolved)
- Time spent on runbook steps vs. actual engineering work
- Alert → resolution time for alerts with documented runbooks (fully automatable)
```

***

## Key Gotchas

| Gotcha | Detail |
|--------|--------|
| `rate()` requires counter | Applying `rate()` to a gauge returns garbage; use `deriv()` or `delta()` for gauges |
| Label cardinality explosion | Adding `user_id` as a Prometheus label creates millions of time series — kills Prometheus |
| Histogram bucket boundaries | Buckets must be defined at instrumentation time; changing them loses historical comparability |
| `histogram_quantile` accuracy | Only accurate if most values fall within bucket boundaries; last bucket is `+Inf` — don't rely on it |
| `by` vs `without` in aggregation | `sum by (job)` keeps only `job` label; `sum without (pod)` keeps all labels except `pod` |
| Recording rules for dashboards | Grafana dashboards on raw high-cardinality metrics cause query timeouts — always pre-record |
| Alertmanager `group_wait` | First alert in a group waits `group_wait` before sending — not appropriate for critical pages |
| `for:` clause resets on flap | If an alert fires and recovers before `for:` completes, the timer resets — flapping alerts never page |
| Trace sampling before SLO baseline | Don't implement tail sampling until you have enough data to know your normal latency distribution |
| Loki without structured logging | Unstructured logs (no JSON) require regex extraction at query time — slow and brittle |

## System Design Perspective

**Prometheus at Scale — Thanos / Cortex:** A single Prometheus instance retains ~15 days and handles ~1-5M active series before query degradation. At scale: Thanos Sidecar uploads blocks to S3 every 2h (matches TSDB block interval), Thanos Query federates across multiple Prometheus instances with deduplication. The critical config decision is `external_labels` — every Prometheus instance needs unique labels (e.g., `replica`, `cluster`) so Thanos can deduplicate overlapping scrapes from HA pairs. Without this, Thanos Query returns duplicate data points in range queries.

**eBPF Observability vs Instrumentation — When to Use Each:** eBPF (Pixie, Cilium Hubble) provides zero-instrumentation network and system visibility — ideal for third-party services, legacy apps, and network-level tracing. But eBPF cannot capture business context (user IDs, order amounts, feature flags). The design pattern: eBPF for infrastructure-layer observability (pod-to-pod latency, DNS failures, TCP retransmits), OTel SDK for application-layer observability (checkout latency by product category, fraud check duration). Use both layers, not one or the other.

**Toil Reduction as a Metric:** Track toil as a first-class metric: expose `oncall_pages_requiring_manual_action_total` (a counter incremented by the on-call bot when an alert requires human action vs auto-resolves). Alert when weekly manual action rate exceeds SLO threshold. Create a Grafana dashboard tracking toil percentage over rolling 4-week windows per team. This makes toil reduction a measurable engineering goal rather than a subjective complaint — and provides the data needed to justify automation investment to engineering leadership.

## System Design Perspective

**VPC Peering vs Transit Gateway:** VPC Peering is direct, non-transitive, and suited for 2-5 VPCs with non-overlapping CIDRs. Transit Gateway is a managed cloud router that enables transitive routing, scales to thousands of VPCs, supports VPN and Direct Connect attachments, and allows inter-region peering. Cost: TGW charges per attachment plus per GB processed; use VPC Endpoints alongside TGW to keep S3/DynamoDB traffic off the TGW.

**Identity Federation (OIDC/SAML):** IRSA (IAM Roles for Service Accounts) uses OIDC federation — the EKS cluster's OIDC issuer is registered in IAM, and pods exchange a projected ServiceAccount JWT for temporary STS credentials via sts:AssumeRoleWithWebIdentity. GitHub Actions and GitLab CI use the same pattern to assume IAM roles without storing access keys. SAML 2.0 is used for AWS SSO federation with enterprise IdPs (Okta, Azure AD).

**Cross-Region DR:** Strategy selection depends on RTO/RPO targets. Backup and Restore (hours RTO, cheapest) uses S3 CRR plus RDS snapshots. Pilot Light (30 min RTO) keeps minimal standby infra running. Warm Standby (minutes RTO) runs a reduced-scale active stack. Active-Active (near-zero RTO) uses Route 53 latency routing plus Aurora Global Database with less than 1s replication lag. All strategies require IaC — without it, failover cannot meet aggressive RTOs.

**Cost Allocation Tagging Strategy:** Enforce mandatory tags (Environment, Team, CostCenter, Owner) via AWS Config Rules or SCPs requiring tags on resource creation. Use AWS Cost Explorer grouped by tag to produce per-team cost reports. Activate cost allocation tags in the Billing Console. Use Tag Policies in AWS Organizations to standardize tag key formats across accounts.

**Managed Identity vs Service Principals (AWS context):** IAM Roles are the equivalent of Managed Identities — they provide temporary credentials without stored secrets. Long-term access keys (equivalent to Service Principals with secrets) should only exist for external systems that cannot assume roles. IRSA and ECS task roles are the pod/task-level equivalent of Azure Workload Identity.

**AWS Organizations SCPs vs Azure Policy:** SCPs define the maximum permissions ceiling per OU/account — they cannot grant permissions, act before IAM evaluation, and even the root user cannot exceed them. Azure Policy enforces at the ARM API layer with richer effects (Deny, Audit, DeployIfNotExists, Modify). Both use hierarchical policy inheritance but differ in execution layer: SCPs block at the IAM authorization step; Azure Policy intercepts at the resource provider level and supports auto-remediation.
