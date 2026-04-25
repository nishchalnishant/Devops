---
description: Prometheus internals, PromQL, alerting rules, Alertmanager routing, and production observability patterns.
---

# Observability — Prometheus & Alerting Deep Dive

## Prometheus Architecture

```
┌────────────────────────────────────────────┐
│              Prometheus Server              │
│                                            │
│  ┌──────────┐    ┌──────────────────────┐  │
│  │  Scrape  │◄───│   Service Discovery   │  │
│  │  Engine  │    │ (K8s, Consul, EC2...) │  │
│  └────┬─────┘    └──────────────────────┘  │
│       │  Pulls metrics every scrape_interval│
│       ▼                                    │
│  ┌──────────────────────┐                  │
│  │  TSDB (Time Series   │                  │
│  │  Database) on disk   │                  │
│  └──────────┬───────────┘                  │
│             │                              │
│  ┌──────────▼───────────┐                  │
│  │   Rule Engine        │  ← Evaluates     │
│  │   (recording +       │    alerting rules │
│  │    alerting rules)   │    every 15s     │
│  └──────────┬───────────┘                  │
└─────────────┼──────────────────────────────┘
              │ Fires alert
              ▼
      Alertmanager
              │ Routes, deduplicates, silences
              ▼
      PagerDuty / Slack / Email
```

***

## PromQL — The Query Language

### Labels and Selectors

```promql
# All HTTP requests for service "api" in production namespace
http_requests_total{job="api", namespace="production"}

# Regex match — all 5xx errors
http_requests_total{status=~"5.."}

# Exclude — everything except 2xx
http_requests_total{status!~"2.."}
```

### Rate and Increase

```promql
# rate() — per-second average rate over 5 minutes (for counters)
rate(http_requests_total{job="api"}[5m])

# increase() — total increase over a time window
increase(http_requests_total[1h])

# irate() — instant rate (last two samples only) — good for spikes
irate(http_requests_total[5m])
```

### Aggregations

```promql
# Sum across all pods, keep only namespace label
sum by (namespace) (rate(http_requests_total[5m]))

# 95th percentile latency (with histogram)
histogram_quantile(0.95,
  sum by (le, job) (
    rate(http_request_duration_seconds_bucket[5m])
  )
)

# Top 5 pods by CPU usage
topk(5, rate(container_cpu_usage_seconds_total[5m]))
```

***

## The RED and USE Methods in PromQL

### RED (for services)

```promql
# Rate — requests per second
rate(http_requests_total[5m])

# Errors — error rate
rate(http_requests_total{status=~"5.."}[5m]) /
rate(http_requests_total[5m])

# Duration — p95 latency
histogram_quantile(0.95,
  rate(http_request_duration_seconds_bucket[5m])
)
```

### USE (for infrastructure)

```promql
# Utilization: CPU
1 - avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m]))

# Saturation: Load average vs CPU count
node_load1 / count by (instance) (node_cpu_seconds_total{mode="idle"})

# Errors: Disk errors
rate(node_disk_io_time_seconds_total[5m])
```

***

## Recording Rules — Pre-computing Expensive Queries

```yaml
# prometheus/rules/recording_rules.yml
groups:
  - name: api_performance
    interval: 60s   # Override global evaluation_interval
    rules:
      # Pre-compute per-job request rate
      - record: job:http_requests:rate5m
        expr: sum by (job) (rate(http_requests_total[5m]))

      # Pre-compute p95 latency per job
      - record: job:http_request_duration_p95
        expr: |
          histogram_quantile(0.95,
            sum by (job, le) (
              rate(http_request_duration_seconds_bucket[5m])
            )
          )
```

***

## Alerting Rules

```yaml
groups:
  - name: api_alerts
    rules:
      - alert: HighErrorRate
        expr: |
          (
            rate(http_requests_total{status=~"5.."}[5m])
            /
            rate(http_requests_total[5m])
          ) > 0.05
        for: 5m      # Must be true for 5 min before firing (avoids flapping)
        labels:
          severity: critical
          team: backend
        annotations:
          summary: "High error rate on {{ $labels.job }}"
          description: "Error rate is {{ $value | humanizePercentage }} for {{ $labels.job }}"
          runbook_url: "https://wiki.company.com/runbooks/high-error-rate"

      - alert: HighLatency
        expr: job:http_request_duration_p95 > 1.0   # Uses recording rule!
        for: 10m
        labels:
          severity: warning
```

***

## Alertmanager — Routing & Silencing

```yaml
# alertmanager.yml
global:
  slack_api_url: 'https://hooks.slack.com/...'

route:
  receiver: 'default'
  group_by: ['alertname', 'job']
  group_wait: 30s      # Wait before sending first notification
  group_interval: 5m   # Wait before sending subsequent group notifications
  repeat_interval: 4h  # How often to re-send unresolved alerts

  routes:
    - match:
        severity: critical
      receiver: pagerduty
      group_wait: 0s     # Page immediately for critical

    - match:
        team: backend
      receiver: slack-backend

receivers:
  - name: default
    slack_configs:
      - channel: '#alerts'

  - name: pagerduty
    pagerduty_configs:
      - service_key: 'PAGERDUTY_KEY'

  - name: slack-backend
    slack_configs:
      - channel: '#backend-alerts'
        text: '{{ .CommonAnnotations.description }}'

inhibit_rules:
  # If critical fires, suppress warning for same job
  - source_match:
      severity: critical
    target_match:
      severity: warning
    equal: ['alertname', 'job']
```

***

## Logic & Trickiness Table

| Concept | Junior Mistake | Senior Understanding |
|:---|:---|:---|
| **Counters** | Use `counter{job="api"}` directly | Counters always increase; use `rate()` or `increase()` |
| **Cardinality** | Add `user_id` as a label | Every unique label value = new time series; can OOM Prometheus |
| **Flapping alerts** | No `for:` clause | Use `for: 5m` to avoid noisy transient alerts |
| **Histogram accuracy** | Use `summary` for latency | `histogram_quantile()` aggregates across instances; `summary` does not |
| **Recording rules** | Skip them | Pre-compute expensive queries; dashboards and alerts load instantly |
| **Alert routing** | One catch-all receiver | Route by team/severity; use inhibit rules to avoid alert storms |
