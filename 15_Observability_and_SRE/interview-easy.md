---
description: Easy interview questions for Observability, SRE, Prometheus, and monitoring fundamentals.
---

## Easy

**1. What is the difference between monitoring, observability, and alerting?**

**Monitoring** is collecting and storing predefined metrics about system behavior. **Observability** is the ability to understand the internal state of a system from its external outputs (metrics, logs, traces) — even for conditions you didn't anticipate. **Alerting** is notifying humans when monitored conditions cross thresholds. Observability is a superset of monitoring: a highly observable system lets you debug novel failures, not just known ones.

**2. What are the three pillars of observability?**

- **Metrics:** Numerical measurements over time (CPU usage, request rate, error count). Efficient for trending and alerting — low storage cost.
- **Logs:** Text records of discrete events (HTTP request received, exception thrown). Rich for debugging specific events but expensive at scale.
- **Traces:** Records of a request's path through multiple services, with timing for each hop. Essential for understanding latency in distributed systems.

**3. What is a SLI, SLO, and SLA?**

- **SLI (Service Level Indicator):** A specific metric measuring service behavior. Example: "the proportion of HTTP requests that return 2xx status codes."
- **SLO (Service Level Objective):** The target for an SLI. Example: "99.9% of requests must succeed over a rolling 30-day window."
- **SLA (Service Level Agreement):** A contractual commitment to customers, usually with financial penalties for violations. The SLO is typically set more conservatively than the SLA to provide a buffer.

**4. What is an error budget?**

An error budget is the allowed amount of failure defined by an SLO. If your SLO is 99.9% availability, your error budget is 0.1% — which equals ~43.8 minutes of downtime per 30-day month. The error budget enables data-driven decisions: when the budget is healthy, teams can take risks (deploy more frequently); when the budget is nearly exhausted, teams focus on stability over features.

**5. What is Prometheus and how does it collect metrics?**

Prometheus is an open-source monitoring system and time series database. It uses a **pull model** — Prometheus periodically scrapes HTTP endpoints (`/metrics`) exposed by targets. Each metric is stored as a time series identified by a metric name and labels. Prometheus also supports a **Pushgateway** for short-lived jobs that can't be scraped. It has a built-in query language (PromQL) for analysis and alerting.

**6. What is a Prometheus exporter?**

A Prometheus exporter is a process that translates metrics from a system that doesn't natively expose Prometheus-format metrics into the `/metrics` HTTP endpoint format. Examples:
- `node_exporter` — exposes Linux OS metrics (CPU, memory, disk, network)
- `postgres_exporter` — exposes PostgreSQL metrics
- `blackbox_exporter` — probes endpoints and exposes success/latency

**7. What is `rate()` in PromQL and why can't you use a counter value directly?**

Counters only ever increase (they reset to 0 on restart). Using a counter's raw value in a graph or alert is meaningless — you need the rate of increase. `rate(http_requests_total[5m])` computes the per-second rate of increase over the last 5 minutes, accounting for counter resets. Always use `rate()` or `increase()` with counters; use raw values only for gauges (memory usage, current connections).

**8. What is an Alertmanager and what does it add on top of Prometheus alerts?**

Alertmanager handles alert routing, deduplication, grouping, silencing, and inhibition. Prometheus evaluates alerting rules and fires alerts to Alertmanager — but Alertmanager decides who gets notified and how. Features:
- **Grouping:** Multiple alerts for the same incident (10 pods down) are grouped into one notification.
- **Routing:** Route to the right team (frontend alerts → frontend Slack, database alerts → DBA PagerDuty).
- **Silencing:** Suppress alerts during planned maintenance.
- **Inhibition:** Suppress low-severity alerts when a high-severity alert is already firing.

**9. What is the difference between Grafana and Prometheus?**

Prometheus collects and stores metrics, evaluates alerting rules, and provides a basic query UI. Grafana is a visualization platform that queries data from multiple sources (Prometheus, Loki, CloudWatch, Elasticsearch) and builds rich dashboards, graphs, and alerts. They are complementary: Prometheus is the data store and alerting engine; Grafana is the visualization layer. Grafana's own alerting can also query Prometheus as an alternative to Alertmanager.

**10. What is distributed tracing and why is it necessary in microservices?**

In a monolith, a slow request can be found by looking at one application's logs. In a microservices architecture, a single user request may touch 10+ services. Distributed tracing tracks the full journey of a request by assigning a trace ID that propagates through all services via HTTP headers. Each service creates a span (a unit of work with start time, duration, and metadata). Tools like Jaeger or Zipkin reconstruct the full call tree, making it possible to identify which service or database query caused the slowdown.

**11. What is a Grafana dashboard and how are they typically managed in production?**

A Grafana dashboard is a collection of panels (graphs, tables, stat cards) visualizing data from a data source. In production, dashboards should be:
- **Version-controlled:** Export as JSON and store in Git, not managed via the UI.
- **Provisioned as code:** Grafana supports dashboard provisioning from YAML config files on startup — no manual import needed.
- **Governed:** Use Grafana Organizations and Teams to restrict edit access; avoid dashboard sprawl.
- **Linked:** Use dashboard variables and links to navigate from a high-level service health view to a detailed pod view.

**12. What is MTTR and MTBF and how are they used in SRE?**

- **MTTR (Mean Time to Recover):** Average time from incident detection to service restoration. A key SRE metric — reducing MTTR requires good runbooks, fast on-call response, and automated rollback capabilities.
- **MTBF (Mean Time Between Failures):** Average time between incidents. A reliability measure — improving MTBF requires better testing, chaos engineering, and reliability investments.

SREs optimize MTTR first (faster recovery = less user impact) before MTBF — it's generally easier to recover fast than to prevent all failures.
