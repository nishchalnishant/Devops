# Observability Tips & Tricks

Production-tested patterns, anti-patterns, and gotchas for metrics, logs, traces, and alerting.

***

## PromQL — Common Anti-Patterns

### Never divide by zero silently
```promql
# BAD: returns empty if denominator is 0
rate(errors_total[5m]) / rate(requests_total[5m])

# GOOD: returns 0 when there are no requests (safe for dashboards and alerts)
rate(errors_total[5m]) / (rate(requests_total[5m]) > 0)

# ALSO GOOD: use "or" to define a fallback
rate(errors_total[5m]) / rate(requests_total[5m]) or vector(0)
```

### `irate` vs `rate` — know when each is appropriate
- `rate()` averages over the entire window — smooth, good for dashboards
- `irate()` uses only the last two samples — spiky, good for alerting on sudden spikes
```promql
# Alert on sudden CPU spike (irate is more responsive)
irate(node_cpu_seconds_total{mode="idle"}[1m])

# Dashboard showing CPU trend (rate is smoother)
1 - avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) by (instance)
```

### Label cardinality is the #1 Prometheus performance killer
```
# BAD: adding high-cardinality labels makes every metric series unique
http_requests_total{url="/api/users/12345"}      # Unique per user ID!
http_requests_total{trace_id="abc123"}            # Unique per request!

# GOOD: use low-cardinality labels only
http_requests_total{route="/api/users/:id", status_code="200"}
```
A Prometheus with 10M time series is sluggish. High-cardinality labels (user IDs, trace IDs) are the primary cause. Use `recording rules` to pre-aggregate, and `exemplars` to link from metrics to traces without cardinality explosion.

### Recording rules — pre-aggregate expensive queries
```yaml
# rules/slo.yml
groups:
  - name: slo.rules
    interval: 30s
    rules:
      # Pre-compute error rate (used in dashboards + alerts)
      - record: job:http_errors:rate5m
        expr: |
          rate(http_requests_total{status=~"5.."}[5m]) /
          rate(http_requests_total[5m])

      # Use the recording rule in alerts (much faster evaluation)
      - alert: HighErrorRate
        expr: job:http_errors:rate5m > 0.01
        for: 5m
```
Never run the same complex PromQL query in multiple dashboards — create a recording rule once and reference it everywhere.

***

## Alerting — Common Mistakes

### Alert on symptoms, not causes
```
BAD alerts (cause-based):
  - "CPU > 90%"             — might be fine if application is happy
  - "Memory > 80%"          — many apps (JVM) intentionally use all memory

GOOD alerts (symptom-based):
  - "P99 latency > 500ms"   — user is actually experiencing slowness
  - "Error rate > 0.1%"     — user is actually receiving errors
  - "Pod restarts > 3 in 10m" — something is actually broken
```

### Multi-window burn rate SLO alerting (Google SRE Book pattern)
```yaml
# Alert when error budget is burning too fast
# Fast burn: 1h window, 14.4x burn rate → paged immediately
- alert: SLOErrorBudgetFastBurn
  expr: |
    (
      job:http_errors:rate1h > (14.4 * 0.001)
    ) and (
      job:http_errors:rate5m > (14.4 * 0.001)
    )
  annotations:
    summary: "Error budget burning 14.4x — will exhaust in 1 hour"

# Slow burn: 6h window, 6x burn rate → urgent ticket
- alert: SLOErrorBudgetSlowBurn
  expr: job:http_errors:rate6h > (6 * 0.001)
  for: 30m
  annotations:
    summary: "Error budget burning 6x — will exhaust in 5 days"
```

### Alert fatigue — the real enemy
Symptoms of alert fatigue:
- On-call engineers silence alerts without investigating
- The same alert fires every night at 2am with no action
- > 5 alerts fire per week that are "expected behavior"

Fixes:
- Every alert must have a runbook link
- Every alert must require action — if the action is "ignore it," delete the alert
- Use `inhibit_rules` in Alertmanager: if a cluster-down alert fires, suppress all downstream service alerts from that cluster

***

## Grafana — Dashboard Quality

### Variable-driven dashboards (avoid duplicating panels)
```
# Instead of one panel per service (20 panels for 20 services):
1. Create a dashboard variable: $service (query Prometheus labels)
2. Use it in panel queries: rate(http_requests_total{service="$service"}[5m])
3. One panel + variable selector = 20 services on demand

# Multi-select variable: show all services simultaneously
options:
  multi: true
  includeAll: true
```

### Link metrics to logs to traces (avoid context-switching)
```
Grafana panel → Data Link:
  URL: /explore?orgId=1&left=["now-1h","now","Loki",{"expr":"{pod=\"${__series.labels.pod}\"}"}]
  Label: "View Logs"

This allows: click a spike on a Grafana metric panel → jump directly to the logs for that pod at that time
```

### Don't hardcode thresholds in dashboards
```
BAD: Panel threshold set to 500ms (static)
GOOD: Panel threshold references a variable $latency_slo_ms — sourced from a config map
      or computed from your SLO definition
```

***

## Loki — LogQL Patterns

### Structured JSON logging is a prerequisite for LogQL power
```
BAD log line (unstructured):
2024-01-01 12:00:00 ERROR user 12345 checkout failed: timeout

GOOD log line (structured JSON):
{"timestamp": "2024-01-01T12:00:00Z", "level": "error", "user_id": "12345",
 "action": "checkout", "error": "timeout", "duration_ms": 5000}

# With structured logs, LogQL can filter by field:
{app="checkout"} | json | level="error" | duration_ms > 3000
```

### High-volume log filtering at the agent level
```yaml
# Promtail: drop DEBUG and INFO before they reach Loki (90% cost reduction)
- pipeline_stages:
  - match:
      selector: '{app="api"}'
      stages:
        - json:
            expressions:
              level: level
        - drop:
            expression: '(level == "debug") or (level == "info")'
```

### Parse and extract metrics from logs (LogQL metric queries)
```logql
# Count errors per minute from logs — no code change needed
rate({app="api"} | json | level="error" [1m])

# P99 response time from access logs
quantile_over_time(0.99, {app="nginx"} | logfmt | duration_ms > 0 | unwrap duration_ms [5m])
```

***

## Distributed Tracing — Common Mistakes

### Propagating trace context across async boundaries
```
HTTP calls: trace context in W3C TraceContext headers (trace-id, span-id) — auto-handled by SDK
Kafka messages: trace context must be manually serialized into message headers
Background jobs: create a new root span with parent context from the triggering event

# The most common distributed tracing bug:
# Job receives a Kafka message → starts processing → logs show a completely
# disconnected trace with no link to the request that created the message
# Fix: extract trace context from Kafka headers in the consumer
```

### Sampling strategy — don't sample uniformly
```
Uniform 1% sampling: catches 1% of errors (most errors are < 1% of traffic)

Better strategy (tail sampling):
  - 100% of traces with errors
  - 100% of traces with latency > P99 threshold
  - 1% of all other traces

# OpenTelemetry Collector tail sampling processor:
processors:
  tail_sampling:
    decision_wait: 10s
    policies:
      - name: errors-policy
        type: status_code
        status_code: {status_codes: [ERROR]}
      - name: high-latency
        type: latency
        latency: {threshold_ms: 1000}
      - name: sample-rest
        type: probabilistic
        probabilistic: {sampling_percentage: 1}
```

***

## On-Call Efficiency

### The 5-minute triage checklist
When a Sev-1 alert fires:
```
1. Is it getting worse, stable, or improving? (trend is more important than current value)
2. What changed recently? (deployment, config, cron job, external dependency)
3. What's the user impact? (put a number on it: X% of users, Y requests/sec failing)
4. Can you mitigate now before you diagnose? (rollback, traffic shift, scale up)
5. Who else needs to know? (stakeholders, other oncalls, customer support)
```

### Postmortem anti-patterns
- **Blame individual humans** — always ask "what system allowed this mistake to happen?"
- **Action items with no owner** — every action item needs a named owner and due date
- **Action items with no verification** — "add monitoring" is not an action item; "add alert for X with test case Y" is
- **Skipping the postmortem** — "we fixed it, no need to document" means the same incident recurs in 3 months

### Golden signals quick reference
| Signal | What to Measure | Alert Condition |
|:---|:---|:---|
| **Latency** | P99 request duration (not average) | > 500ms for 5 minutes |
| **Traffic** | Requests/second | Drop > 30% vs baseline |
| **Errors** | Error rate (4xx/5xx ratio) | > 0.5% for 5 minutes |
| **Saturation** | CPU, memory, disk, connection pool | > 80% of limit |
