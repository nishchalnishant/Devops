---
description: Prometheus internals, PromQL, alerting rules, Alertmanager routing, and production observability patterns.
---

# Observability — Prometheus & Alerting Deep Dive

```
Prometheus & Alerting Deep Dive
├── Prometheus Architecture
│   ├── Service Discovery (K8s, Consul, EC2) → Scrape Engine → TSDB on disk
│   ├── Rule Engine evaluates recording + alerting rules every 15s
│   └── Alertmanager: routes, deduplicates, silences → PagerDuty / Slack / Email
├── PromQL — Labels and Selectors
│   ├── Exact match: {job="api", namespace="production"}
│   ├── Regex match: {status=~"5.."}; negative regex: {status!~"2.."}
│   └── rate() / increase() / irate() for counters; deriv() / delta() for gauges
├── RED and USE Methods
│   ├── RED (services): Rate = rate(requests[5m]); Errors = error ratio; Duration = p95 latency
│   └── USE (infra): Utilization = CPU% ; Saturation = load avg / CPU count; Errors = disk IO errors
├── Recording Rules
│   ├── Pre-compute expensive queries on interval override (60s)
│   ├── job:http_requests:rate5m = sum by (job) (rate(http_requests_total[5m]))
│   └── job:http_request_duration_p95 = histogram_quantile(0.95, ...) per job
├── Alerting Rules
│   ├── expr + for: (avoid flapping) + labels (severity, team) + annotations (runbook_url)
│   ├── Use recording rules in alert exprs: job:http_request_duration_p95 > 1.0
│   └── group_wait: 0s for critical pages; default 30s
├── Alertmanager Routing
│   ├── global → route (group_by, group_wait, group_interval, repeat_interval) → routes
│   ├── match severity=critical → pagerduty (group_wait: 0s)
│   ├── match team=backend → slack-backend
│   └── inhibit_rules: suppress warning if critical fires for same alertname + job
└── Logic & Trickiness Table
    ├── Counters: always use rate() or increase() — never raw counter value
    ├── Cardinality: every unique label value = new time series; user_id → OOM
    ├── Flapping: always use for: clause; alerts without for: are noisy
    ├── Histogram vs Summary: histogram aggregates across replicas; summary does not
    └── Recording rules: mandatory for high-cardinality dashboard queries
```

## First Principles

Observability is not monitoring — monitoring tells you a system is down; observability tells you why. The three pillars (metrics, logs, traces) are complementary: metrics alert you, logs explain what happened, traces show where time was spent. SLOs are contracts with users — error budgets make reliability a shared engineering problem, not a ops problem. Toil is the enemy of reliability: every repetitive manual action is a reliability debt that compounds.

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

## System Design Perspective

**Cardinality Enforcement at Scale:** Label cardinality is the primary Prometheus performance failure mode. Design a cardinality budget: define a per-job series limit in the Prometheus `scrape_config` with `sample_limit: 10000` — scrapes exceeding this limit are rejected entirely, preventing a single misbehaving service from degrading the entire Prometheus instance. For enforcement in the CI pipeline, run `promtool check metrics` against a test endpoint and use `curl /metrics | promtool check metrics 2>&1 | grep -c WARN` as a gate — more than zero cardinality warnings fail the build. The OTel Collector `filter` processor can drop high-cardinality attributes before they reach Prometheus remote_write.

**Alertmanager Routing Tree as Code:** Route trees have a failure mode: misrouted alerts (a Sev-1 going to Slack instead of PagerDuty). Test routing decisions in CI: `amtool config routes test --config.file alertmanager.yml --verify.receivers pagerduty severity=critical,team=payments`. The routing tree should follow: global catch-all (default receiver) at the bottom, team-based routing in the middle, severity-based routing at the top. Use `continue: true` on team routes when an alert should notify both the team Slack channel AND trigger a PagerDuty escalation — without `continue: true`, the first matching route terminates the routing tree.

**Recording Rules as the Observability Contract:** Recording rules are not just a performance optimization — they are the stable interface between metric instrumentation and alerting/dashboards. When a service renames a metric (e.g., `http_requests_total` → `http_server_requests_total`), the recording rule absorbs the change: update the recording rule expression, and every alert and dashboard that references `job:http_requests:rate5m` continues working unchanged. Enforce: no alert expression or dashboard query should reference raw metric names directly — all must go through recording rules defined in the `slo.rules` group.
| **Alert routing** | One catch-all receiver | Route by team/severity; use inhibit rules to avoid alert storms |

## System Design Perspective

**VPC Peering vs Transit Gateway:** VPC Peering is direct, non-transitive, and suited for 2-5 VPCs with non-overlapping CIDRs. Transit Gateway is a managed cloud router that enables transitive routing, scales to thousands of VPCs, supports VPN and Direct Connect attachments, and allows inter-region peering. Cost: TGW charges per attachment plus per GB processed; use VPC Endpoints alongside TGW to keep S3/DynamoDB traffic off the TGW.

**Identity Federation (OIDC/SAML):** IRSA (IAM Roles for Service Accounts) uses OIDC federation — the EKS cluster's OIDC issuer is registered in IAM, and pods exchange a projected ServiceAccount JWT for temporary STS credentials via sts:AssumeRoleWithWebIdentity. GitHub Actions and GitLab CI use the same pattern to assume IAM roles without storing access keys. SAML 2.0 is used for AWS SSO federation with enterprise IdPs (Okta, Azure AD).

**Cross-Region DR:** Strategy selection depends on RTO/RPO targets. Backup and Restore (hours RTO, cheapest) uses S3 CRR plus RDS snapshots. Pilot Light (30 min RTO) keeps minimal standby infra running. Warm Standby (minutes RTO) runs a reduced-scale active stack. Active-Active (near-zero RTO) uses Route 53 latency routing plus Aurora Global Database with less than 1s replication lag. All strategies require IaC — without it, failover cannot meet aggressive RTOs.

**Cost Allocation Tagging Strategy:** Enforce mandatory tags (Environment, Team, CostCenter, Owner) via AWS Config Rules or SCPs requiring tags on resource creation. Use AWS Cost Explorer grouped by tag to produce per-team cost reports. Activate cost allocation tags in the Billing Console. Use Tag Policies in AWS Organizations to standardize tag key formats across accounts.

**Managed Identity vs Service Principals (AWS context):** IAM Roles are the equivalent of Managed Identities — they provide temporary credentials without stored secrets. Long-term access keys (equivalent to Service Principals with secrets) should only exist for external systems that cannot assume roles. IRSA and ECS task roles are the pod/task-level equivalent of Azure Workload Identity.

**AWS Organizations SCPs vs Azure Policy:** SCPs define the maximum permissions ceiling per OU/account — they cannot grant permissions, act before IAM evaluation, and even the root user cannot exceed them. Azure Policy enforces at the ARM API layer with richer effects (Deny, Audit, DeployIfNotExists, Modify). Both use hierarchical policy inheritance but differ in execution layer: SCPs block at the IAM authorization step; Azure Policy intercepts at the resource provider level and supports auto-remediation.
