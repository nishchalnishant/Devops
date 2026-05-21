# Observability and SRE — Interview Prep

---
description: Easy interview questions for Observability, SRE, Prometheus, and monitoring fundamentals.
---

```
Observability — Easy Interview Topics
├── Core Concepts
│   ├── Monitoring vs Observability vs Alerting
│   ├── Three Pillars: metrics / logs / traces
│   └── SLI / SLO / SLA / Error Budget
├── Prometheus
│   ├── Pull model (scrapes targets at configurable interval)
│   ├── Exporters (node_exporter, kube-state-metrics, JMX)
│   └── rate() on counter vs raw counter value
├── Alertmanager
│   ├── Routing (route rules → receiver)
│   ├── Deduplication (grouping identical alerts)
│   ├── Grouping (batch alerts from same cluster)
│   ├── Silencing (maintenance window)
│   └── Inhibition (suppress downstream when upstream down)
├── Grafana
│   ├── Prometheus as data source (not built-in)
│   └── Dashboard management (JSON, version control, provisioning)
├── Distributed Tracing
│   └── Why needed in microservices (request path across services)
└── SRE Metrics
    ├── MTTR (mean time to recover) — optimize first
    └── MTBF (mean time between failures) — longer-term
```

### First Principles

You can't fix what you can't see. Three pillars: logs (what happened), metrics (how much/how fast), traces (where time was spent across services). SLOs define acceptable failure rates — alerts fire when burn rate exceeds budget. On-call needs runbooks to act on alerts.

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

### System Design Perspective

**Cardinality Challenges in Metrics:** The easy questions cover Prometheus exporters and PromQL basics, but a critical design constraint is label cardinality. Adding labels with unbounded values (user IDs, request IDs, full URLs) creates one time series per unique value — millions of series degrade Prometheus performance severely. Design rule: route parameters belong in trace attributes, not metric labels; use bounded label sets for metrics (status code, method, route template).

**Sampling Strategies in Tracing:** Tracing in microservices is introduced here, but the cost model matters. 100% trace collection at high request rates is expensive. Start with probabilistic head sampling (sample 10% of traces) and evolve to tail sampling (keep 100% of error traces) as tracing infrastructure matures. Document the sampling strategy so developers know which traces are guaranteed to be captured.

**Alerting Fatigue Design:** Alertmanager routing concepts (grouping, inhibition) are introduced here but the design intent is critical: inhibition prevents alert storms from waking on-call for 50 downstream alerts when one upstream cluster is down. Route severity-based: page for SLO breach, Slack ticket for slow burn, email for informational. Every alert must have a runbook link in its annotation.

```
Observability — Medium Interview Topics
├── Four Golden Signals
│   ├── Latency (separate success vs error latency)
│   ├── Traffic (requests/sec, events/sec)
│   ├── Errors (explicit 5xx + implicit wrong content)
│   └── Saturation (CPU, memory, queue depth, connection pool)
├── High-Cardinality Telemetry Problem
│   ├── user_id / trace_id labels → unbounded series in Prometheus
│   └── Solution: exemplars (link metric point → specific trace)
├── Error Budget
│   ├── 99.9% SLO → 43.8 min/month budget
│   └── Exhausted: freeze features, focus on reliability
├── SLI / SLO / SLA Differences
│   └── Design SLOs tighter than SLA (SLO breach ≠ SLA breach)
├── Distributed Tracing + OpenTelemetry
│   ├── OTel SDK instruments apps (auto + manual)
│   ├── OTel Collector (receive → process → export)
│   └── OTLP protocol (vendor-neutral)
├── Prometheus Recording Rules
│   └── Pre-compute expensive PromQL → fast dashboard + alert eval
├── Black-Box vs White-Box Monitoring
│   ├── Black-box: synthetic probes (user perspective)
│   └── White-box: internal metrics (service perspective)
└── Incident Response Sequence
    └── Detect → Communicate → Stabilize → Investigate → Remediate → Post-mortem
```

### First Principles

You can't fix what you can't see. Three pillars: logs (what happened), metrics (how much/how fast), traces (where time was spent across services). SLOs define acceptable failure rates — alerts fire when burn rate exceeds budget. On-call needs runbooks to act on alerts.

## Medium

**9. What are the Four Golden Signals and why do they matter?**

Latency, traffic, errors, and saturation — these four signals, from the Google SRE book, cover the essential health of any service:
- **Latency:** How long requests take (distinguish successful vs. failed request latency separately).
- **Traffic:** Demand on the system (requests/second, messages/second).
- **Errors:** Rate of failed requests (explicit errors, implicit errors like wrong content).
- **Saturation:** How full the system is (CPU, memory, connection pool utilization).

Focusing on these four prevents monitoring sprawl and keeps alerting tied to user-facing impact.

**10. What is high-cardinality telemetry and why is it problematic for Prometheus?**

Cardinality is the number of unique time series — each unique combination of metric name and label key-value pairs is a separate series. A label like `user_id` with millions of unique values creates millions of time series, causing memory explosion and query slowdown in Prometheus. Prometheus is optimized for a predictable, bounded number of series. For high-cardinality event data (user-level traces, request IDs), use distributed tracing or a column-oriented observability backend (Honeycomb, Grafana Tempo).

**11. What is an error budget and what does "burning the error budget" mean?**

An error budget is the allowed downtime derived from an SLO: `error budget = (1 - SLO) × window`. For 99.9% over 30 days: `0.001 × 43,200 minutes = 43.2 minutes`. When an incident causes downtime or elevated errors, those minutes are burned. If the budget is exhausted, the SRE team freezes feature releases and focuses entirely on reliability work. This creates a data-driven conversation between product and engineering about the cost of unreliability.

**12. What is the difference between SLI, SLO, and SLA?**

- **SLI:** A quantitative measure — ratio of successful requests, P99 latency.
- **SLO:** An internal target threshold for an SLI over a time window.
- **SLA:** A contractual commitment with financial penalties for breach. Typically looser than the SLO to provide a buffer.

Design SLOs tighter than your SLA — if the SLA is 99.9%, set the SLO at 99.95% internally so routine SLO policy triggers before the SLA is breached.

**13. What is distributed tracing and what is OpenTelemetry?**

Distributed tracing tracks requests through microservices by propagating a `trace-id` header across all service calls, creating a "span" at each hop. OpenTelemetry (OTel) is a vendor-neutral CNCF standard providing SDKs and APIs for instrumenting applications to emit traces, metrics, and logs in a common format. OTel data is exported to backends like Jaeger, Tempo, Zipkin, Datadog, or Honeycomb without vendor lock-in.

**14. What is a Prometheus recording rule and when do you create one?**

A recording rule pre-computes expensive or frequently-queried PromQL expressions and stores the result as a new time series. Example: computing P99 request latency across all pods is expensive on every dashboard load — a recording rule computes it every 30 seconds and stores it as `job:request_latency_seconds:p99`. Dashboards query the pre-computed series. Also simplifies complex PromQL referenced in alerting rules.

**15. What is black-box vs white-box monitoring?**

- **Black-box:** Tests the system from outside, as a user would — probing external endpoints for availability and correct responses. Catches user-facing outages regardless of internal implementation.
- **White-box:** Instruments application internals — request queue depth, GC pause time, connection pool utilization. Catches degradation early before it becomes user-facing.

Both together give complete visibility: white-box detects problems first; black-box confirms user impact.

**16. What is your incident response sequence when a critical service is failing?**

1. **Detect and triage:** Confirm user impact, quantify scope, open incident channel.
2. **Communicate:** Notify stakeholders and update status page.
3. **Stabilize:** Implement the fastest mitigation (rollback, disable feature flag, increase replicas, redirect traffic) — restore service before root-causing.
4. **Investigate:** Check recent deployments, metric anomalies, log errors, trace sampling.
5. **Remediate:** Apply the root fix.
6. **Post-mortem:** Blameless review within 24-48 hours, action items with owners and due dates.

### System Design Perspective

**Sampling Strategies for High-Traffic Tracing:** The cardinality problem for metrics has a parallel in tracing: 100% trace collection at millions of requests per second is impractical. Design the sampling strategy explicitly: head sampling for low-value transactions (sample 1%), tail sampling for all errors and high-latency outliers (keep 100%). Document which services use head vs tail sampling so on-call engineers know whether a missing trace is a sampling decision or a bug.

**Log Aggregation Cost Model:** Black-box vs white-box monitoring also applies to logging. Black-box log monitoring (external probes that check response content) is cheaper than shipping all application logs. For high-volume services, pre-filter at the log agent: drop DEBUG/INFO logs before they reach Loki; keep WARN/ERROR/CRITICAL. This can reduce log storage cost by 80% while preserving all actionable signals.

**Alerting Fatigue and Routing:** The incident response sequence starts with "Detect" but the quality of detection determines MTTD. Alert routing design: fast-burn SLO alerts → PagerDuty (wake someone up); slow-burn → Slack ticket channel (async); informational → suppressed or routed to weekly review. The Stabilize step (restore before root-cause) is an SRE cultural principle — bake it into runbooks explicitly so on-call engineers don't feel pressure to diagnose before mitigating.

***


```
Observability — Hard Interview Topics
├── SLO Burn Rate Alerting vs Threshold Alerting
│   ├── Fast burn: 14.4x rate for 1h → page immediately
│   └── Slow burn: 6x rate for 6h → ticket
├── Multi-Window Multi-Burn-Rate (Google SRE Book pattern)
│   ├── 1h + 5m windows both breaching → fast burn alert
│   └── 6h window breaching → slow burn alert
├── Alert Fatigue — SRE Principles
│   ├── Symptom-based (P99 latency, not CPU%)
│   ├── SLO-driven (alert only when budget burns)
│   ├── Tiered routing (PagerDuty / Slack / email)
│   └── Weekly alert review: delete noisy, fix firing alerts
├── eBPF & Cloud-Native Observability
│   ├── Cilium (network policy + flow visibility)
│   └── Pixie (auto-instrumented telemetry, no code changes)
├── Distributed Tracing in Async Microservices
│   ├── Context propagation through Kafka/SQS headers
│   ├── follows-from links (not parent-child for async)
│   └── Fan-out: single trace parent → multiple consumer spans
├── Internal Observability Platform Design (hundreds of teams)
│   ├── OTel Collector DaemonSet (standard pipeline)
│   ├── Thanos / Cortex (Prometheus at scale, long retention)
│   ├── Loki / Elasticsearch (log aggregation)
│   ├── Grafana (self-service dashboards via Terraform)
│   ├── Cardinality budgets per team (enforce via recording rules)
│   └── Tail sampling (OTel Collector tail_sampling processor)
├── Prometheus Histogram vs Averages for SLOs
│   └── histogram_quantile(0.99, ...) is the only correct SLO metric
├── Chaos Engineering for Payment Systems
│   ├── Steady state hypothesis → LitmusChaos / Gremlin
│   └── Governance: SLO gate auto-aborts experiment
└── MTTR / MTTD / MTTF / MTBF + Blameless Postmortem
    ├── MTTD + MTTR are primary operational levers
    └── Five Whys → systemic action items (not blame)
```

### First Principles

You can't fix what you can't see. Three pillars: logs (what happened), metrics (how much/how fast), traces (where time was spent across services). SLOs define acceptable failure rates — alerts fire when burn rate exceeds budget. On-call needs runbooks to act on alerts.

## Hard

**17. What is SLO burn rate alerting and why is it superior to threshold-based alerting?**

Traditional threshold alerts (error rate > 5%) are noisy and context-free — a 5% error rate for 30 seconds is fine; for 6 hours it's catastrophic. Burn rate alerting measures how quickly the error budget is being consumed:

- **Fast burn (page immediately):** 14.4x normal error rate for 1 hour means 2% of the 30-day budget is gone in 60 minutes — page on-call.
- **Slow burn (ticket):** 6x normal error rate for 6 hours means 5% of budget is gone — create a ticket, investigate next business day.

This ties every alert to budget impact, eliminating noise while ensuring no silent slow degradation.

**18. How do you implement multi-window multi-burn-rate alerting?**

Use both a short and long evaluation window for each severity tier. Page only when both windows are simultaneously above their threshold — this eliminates single-spike false positives:

```yaml
# Fast burn: page immediately
- alert: HighBurnRateShort
  expr: |
    sum(rate(http_requests_total{status=~"5.."}[1h])) /
    sum(rate(http_requests_total[1h])) > 0.001 * 14.4

# Slow burn: create a ticket
- alert: HighBurnRateLong
  expr: |
    sum(rate(http_requests_total{status=~"5.."}[6h])) /
    sum(rate(http_requests_total[6h])) > 0.001 * 6
```

The 1h/6h pair catches both sudden spikes and gradual degradation. Add a 1h/3d pair for very slow budget erosion that should be addressed this sprint.

**19. How do you address alert fatigue using SRE principles?**

1. **Symptom-based alerts only:** Alert on user-facing impact (high latency, elevated error rate) — not causes (high CPU, disk fill). High CPU that doesn't affect users is a dashboard metric, not a page.
2. **SLO-driven alerting:** Every alert derives from error budget burn rate, not arbitrary thresholds.
3. **Alert tiers:** P1 (wake someone up, user impact), P2 (ticket, investigate next business day), INFO (dashboard only).
4. **Alert consolidation:** Alertmanager groups related alerts — 50 failing pods produce one page, not 50.
5. **Weekly alert review:** Review all pages from the previous week. For each: was it actionable? Was the right person paged? Could a runbook have prevented it? Prune or improve every week.

**20. What is eBPF and how does it revolutionize cloud-native observability?**

eBPF (extended Berkeley Packet Filter) runs sandboxed programs in the Linux kernel without modifying kernel source. The eBPF verifier ensures programs cannot crash or corrupt the kernel.

- **Observability:** Tools like Cilium and Pixie attach eBPF probes to syscalls and network events, capturing every system call, network packet, and function call with near-zero overhead — without requiring application code instrumentation. This enables automatic golden signal collection for any workload, including third-party binaries.
- **Networking:** Cilium implements Kubernetes networking, network policies, and service mesh functionality directly in the kernel via eBPF — replacing iptables chains with efficient hash table lookups, enabling 5-10x lower latency and CPU overhead at scale.

**21. What are the challenges of distributed tracing in asynchronous microservices with message queues?**

Standard tracing propagates a `trace-id` header in synchronous HTTP calls. Queues break this:

- **Context propagation:** When a producer publishes to Kafka or SQS, the trace context must be embedded in message headers. The consumer — which processes the message potentially minutes or hours later — must extract this context and create a new span as a continuation, not a child-of relationship.
- **Broken timelines:** Time in the queue (waiting) is valid observability data but shouldn't be counted as "active processing" time. OpenTelemetry models this as a "follows-from" link rather than a parent-child relationship.
- **Fan-out:** A single message may spawn multiple consumers — traces can have multiple continuations. Use span links (OTel feature) to connect related traces without forcing a strict tree structure.

Solution: Use OpenTelemetry SDK instrumentation libraries for common messaging systems (Kafka, SQS, RabbitMQ) which handle context propagation automatically.

**22. How do you design an internal observability platform for hundreds of developer teams?**

1. **Collection:** Deploy OpenTelemetry Collector as a DaemonSet — receives OTLP traces, scrapes Prometheus metrics, and collects container logs. Provide auto-instrumented OTel libraries for common frameworks that teams include as a dependency.
2. **Backends:** Metrics: Thanos or Cortex for long-term storage and cross-cluster global query. Logs: Loki (log-aggregation) or Elasticsearch. Traces: Grafana Tempo (cost-efficient trace storage) or Jaeger.
3. **Visualization:** Grafana as the unified UI with data source links enabling pivoting from a metric spike → correlated traces → relevant logs in a single click. Provide golden signal dashboard templates teams can copy.
4. **Self-service:** Terraform module to provision a team's alert rules, dashboards, and on-call routing in PagerDuty from code. Teams own their observability as code.
5. **Cost control:** Enforce metric cardinality budgets per namespace. Implement trace sampling (head-based for low-value traffic, tail-based to keep 100% of error traces).

**23. What is a Prometheus histogram and why is it better than averages for latency?**

A histogram samples observations (request latency) into configurable buckets, exposing `_count`, `_sum`, and `_bucket{le="N"}` series. This enables `histogram_quantile()` to calculate P50, P95, P99 latency.

An average hides the distribution. If 99% of requests complete in 50ms and 1% take 15 seconds, the average might be 200ms — acceptable on paper. The histogram reveals the 99th percentile is 15 seconds, which is what actually frustrates users. SLOs should be defined on percentiles (P99 < 500ms), not averages, making histograms essential.

**24. What is Chaos Engineering and how do you design an experiment for a payment system?**

Chaos Engineering injects controlled failure into production-like systems to discover unknown weaknesses before they become real incidents.

For a payment processing system:
1. **Define steady state:** P99 checkout latency < 500ms, zero transaction drops, zero double charges.
2. **Experiment catalog:**
   - Kill payment-service pods one at a time → hypothesis: HPA replaces within 30s, no dropped transactions.
   - Inject 300ms database latency → hypothesis: circuit breaker opens, graceful degradation, no 5xx to users.
   - Force database primary failover → hypothesis: replica promotion < 60s, total downtime < error budget.
   - Drain a full AZ → hypothesis: cross-zone load balancing absorbs traffic within 30s.
3. **Tooling:** LitmusChaos for Kubernetes-native experiments, Gremlin for network-level failure injection.
4. **Governance:** Run prod experiments during off-peak hours. Automatically halt if steady-state SLI drops 20% below baseline. Track every experiment in a catalog with outcomes and action items.

**25. What is the difference between MTTR, MTTD, MTTF, and MTBF?**

- **MTTF (Mean Time to Failure):** Average operating time before a non-repairable component fails. Hardware metric.
- **MTBF (Mean Time Between Failures):** For repairable systems — average time between consecutive failures. Higher is better.
- **MTTD (Mean Time to Detect):** Time between failure occurrence and detection/alerting. Reduced by better monitoring and alert coverage.
- **MTTR (Mean Time to Restore):** Time from detection to service restoration. Reduced by runbooks, automation, blameless culture, and practiced incident response.

In SRE practice, MTTD and MTTR are the primary operational levers — you can't always prevent failures, but you can detect and recover faster.

**26. How do you conduct a blameless postmortem?**

1. **Timeline:** Collaboratively build a factual timeline using deployment events, metric changes, and alert firings. Focus on what happened, not who did it.
2. **Root cause (Five Whys):** Iteratively ask "why did this happen?" to surface systemic failures. Don't stop at "engineer pushed bad config" — ask why the bad config was possible, why tests didn't catch it, why the rollback didn't prevent it.
3. **Action items:** Specific, assigned, with due dates. Goal: make the same class of failure impossible or automatically recoverable.
4. **Blameless language:** "The system allowed a misconfiguration" instead of "engineer X misconfigured." Systems have bugs; people make rational decisions given the information they had.
5. **Share widely:** Publish postmortems — they are learning documents for the entire organization, not performance records.

### System Design Perspective

**Log Aggregation at Scale:** The internal observability platform design covers Loki and Elasticsearch, but the cost model deserves more depth. Loki's per-stream ingestion model means poorly labeled logs (all logs in one stream) cause hot partitions. Design: enforce label cardinality limits on Loki streams (namespace + app + level = 3 labels max); use tenant isolation (`X-Scope-OrgID`) to give teams independent query namespaces; ship logs older than 30 days to S3 with the Loki ruler still alerting on live data.

**Cardinality Budget Enforcement:** At platform scale, individual teams add high-cardinality labels that degrade the shared Prometheus. Enforce cardinality budgets: use the Prometheus `series_count_by_metric_name` recording rule to track per-team cardinality; alert the platform team when a namespace exceeds its budget; block metric ingestion via remote write filtering for teams that consistently violate limits. Thanos Receive or Cortex Distributor can enforce these limits at write time.
