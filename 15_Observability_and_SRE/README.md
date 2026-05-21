# Observability & Site Reliability Engineering (SRE)

```
Observability & SRE
├── Three Pillars
│   ├── Metrics — numerical time-series (Prometheus)
│   ├── Logs — event records (Loki, ELK Stack)
│   └── Traces — request journey across services (Jaeger, Tempo)
├── Four Golden Signals
│   ├── Latency — time to serve a request (P99, not average)
│   ├── Traffic — demand on the system (requests/sec)
│   ├── Errors — rate of failing requests (4xx/5xx ratio)
│   └── Saturation — how full the service is (CPU, memory, queues)
├── SLI / SLO / SLA
│   ├── SLI — the measured metric (e.g., 99% of requests < 200ms)
│   ├── SLO — the target (e.g., 99.9% of the time)
│   └── SLA — the legal contract (miss SLO → pay penalty)
└── Error Budgets
    ├── Full budget → ship features, take risks
    └── Exhausted budget → freeze features, focus on reliability
```

## First Principles

You can't fix what you can't see. Three pillars: logs (what happened), metrics (how much/how fast), traces (where time was spent across services). SLOs define acceptable failure rates — alerts fire when burn rate exceeds budget. On-call needs runbooks to act on alerts.

Monitoring tells you *if* a system is failing; Observability tells you *why* it's failing. SRE is the bridge between software engineering and operations, focusing on the stability, reliability, and performance of large-scale systems.

#### 1. The Three Pillars of Observability
1.  **Metrics:** Numerical data over time (e.g., CPU usage, Request Count). Great for dashboards and alerts. (Tool: **Prometheus**).
2.  **Logs:** Text records of events (e.g., "User logged in", "Database connection failed"). Essential for debugging specific errors. (Tool: **ELK Stack / Loki**).
3.  **Traces:** The "Journey" of a request across multiple microservices. Shows where latency is occurring. (Tool: **Jaeger / Tempo**).

#### 2. The Four Golden Signals
Google's SRE handbook identifies these as the most critical signals to monitor:
*   **Latency:** The time it takes to service a request.
*   **Traffic:** How much demand is being placed on the system (e.g., HTTP requests per second).
*   **Errors:** The rate of requests that fail (explicitly or implicitly).
*   **Saturation:** How "full" your service is (e.g., memory usage or disk I/O).

#### 3. SLI, SLO, and SLA
*   **SLI (Service Level Indicator):** A specific metric you measure (e.g., "99% of requests take < 200ms").
*   **SLO (Service Level Objective):** The target goal for that metric (e.g., "We want our SLI to be true 99.9% of the time").
*   **SLA (Service Level Agreement):** A legal contract with a customer. If you miss the SLO, you pay a penalty (e.g., "If we are down for more than 40 minutes a month, we give you a refund").

#### 4. Error Budgets
An Error Budget is the "freedom to fail." If your SLO is 99.9% uptime, you have a 0.1% error budget (about 43 minutes a month).
*   **If the budget is full:** You can push new features and take risks.
*   **If the budget is exhausted:** You stop all feature work and focus 100% on stability and reliability.

***

## System Design Perspective

**Cardinality Challenges in Metrics:** Prometheus stores one time series per unique label combination. Adding a `user_id` or `trace_id` label to a metric explodes cardinality (10M+ series = sluggish Prometheus). Design rule: labels must have bounded cardinality (< 1,000 unique values). Use recording rules to pre-aggregate high-dimensional data; use exemplars to link from a metric data point to the specific trace that caused a spike — without adding trace IDs as metric labels.

**Sampling Strategy in Tracing:** 100% trace collection at scale is cost-prohibitive. Head sampling (decide at request start) is simple but loses error traces. Tail sampling (decide after span collection is complete) is more expensive but captures 100% of errors and high-latency outliers. The OpenTelemetry Collector tail sampling processor is the standard implementation: keep 100% of error traces, 100% of traces above P99 latency, 1% of everything else.

**Log Aggregation at Scale:** Loki's label-based indexing (not full-text index like Elasticsearch) makes it cheap for high-volume logs but requires log filtering at the agent (Promtail/OTel) level before reaching Loki. Drop DEBUG/INFO at the agent for high-volume services; ship only WARN/ERROR. For compliance log retention (90+ days), ship logs to S3/GCS and query with Athena/BigQuery — keep only 7-14 days in Loki for real-time debugging.

**Alerting Fatigue and Alert Routing Design:** The fastest path to on-call burnout is too many alerts that require no action. Design principle: every alert must have a runbook and require human action. Use Alertmanager `inhibit_rules` so cluster-down alerts suppress all downstream service alerts from that cluster. Route Sev-1 alerts (multi-window SLO breach) to PagerDuty; Sev-3 (slow burn) to a Slack channel for async review. Review alert signal-to-noise ratio weekly in postmortems.
