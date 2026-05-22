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

---

## Hard (continued) — Prometheus Internals, Tail Sampling, Multi-Region SLOs, Runbook Automation & Multi-Tenant Metrics

---

**Q: Prometheus TSDB is consuming 80 GB RAM and queries take 30 seconds. Diagnose a cardinality explosion and remediate without data loss.**

Cardinality is the count of unique label combinations (time series). Each series consumes ~3 KB of memory in the TSDB head block. At 80 GB, you likely have 20+ million active series.

**Diagnosis:**

```promql
# Total active series
prometheus_tsdb_head_series

# Top 20 metrics by cardinality
topk(20, count by(__name__)({__name__=~".+"}))

# Cardinality per label value for a specific metric — identify the runaway label
count by(path)(http_request_duration_seconds_bucket)
# If this returns 500k series, "path" contains unbounded values like /user/123/posts/456
```

```bash
# Prometheus admin API — per-label cardinality (Prometheus 2.24+)
curl http://localhost:9090/api/v1/label/__name__/values | jq '.data | length'

# Top series contributing to head size
curl http://localhost:9090/api/v1/query?query=topk(10,count+by(__name__)({__name__=~".+"})) \
  | jq '.data.result[] | {metric: .metric.__name__, count: .value[1]}'
```

**Common Root Causes:**
- `path` or `url` label containing raw user IDs or UUIDs: `/user/12345/order/67890`
- `instance` label containing ephemeral pod IPs instead of stable pod names
- `trace_id` or `request_id` injected into metric labels (correct solution: use exemplars)

**Remediation — Drop the Label at Scrape Time:**

```yaml
# prometheus.yml
scrape_configs:
  - job_name: api-service
    static_configs:
      - targets: ['api:8080']
    metric_relabel_configs:
      # Normalize path parameter: /user/123/orders → /user/{id}/orders
      - source_labels: [path]
        regex: "^(/user/)[^/]+(/.*)$"
        replacement: "${1}{id}${2}"
        target_label: path

      # Drop the label entirely if normalization isn't feasible
      - action: labeldrop
        regex: "path"

      # Hard cap: drop any series exceeding cardinality threshold
      # (Prometheus 2.40+)
    series_limit: 50000
```

**Without Losing Existing Data:** Existing series persist in on-disk TSDB blocks until they age past retention. Reducing retention temporarily flushes old blocks faster:

```bash
prometheus --storage.tsdb.retention.time=48h  # Reduce from 15d temporarily
```

After the offending scrape job is fixed, series stop being written. They age out of the head block (2h default) and compact into blocks, then expire from disk per retention.

**Long-Term Prevention:**

```yaml
# Alert before explosion reaches critical levels
alert: HighCardinalityMetric
expr: count by(__name__)({__name__=~".+"}) > 100000
for: 10m
labels:
  severity: warning
annotations:
  summary: "Metric {{ $labels.__name__ }} has {{ $value }} series — investigate label cardinality"
  runbook: "https://wiki/prometheus-cardinality-runbook"
```

Use **recording rules** to pre-aggregate high-cardinality metrics before they reach dashboards:

```yaml
groups:
  - name: api.aggregated
    interval: 30s
    rules:
      # Replace per-path histogram with aggregated (drops path label)
      - record: api:request_duration:p99:5m
        expr: histogram_quantile(0.99, sum by(job, status)(rate(http_request_duration_seconds_bucket[5m])))
```

---

**Q: Design a tail-based sampling strategy for a payment system processing 50k traces/sec. Explain the trade-offs vs head sampling.**

**Head vs Tail Sampling:**

| | Head Sampling | Tail Sampling |
|---|---|---|
| Decision point | Request start | After all spans received |
| Memory cost | Negligible | All in-flight traces buffered |
| Can capture all errors | No (random miss) | Yes (inspect final status) |
| Can capture slow traces | No | Yes (inspect final latency) |
| Collector required | No (SDK only) | Yes (OTel Collector) |
| Latency to backend | Minimal | decision_wait delay (30–60s) |

**Recommended Hybrid Architecture for 50k traces/sec:**

```
Services (SDK) → Head sample at 10% → OTel Collector fleet → Tail sample to 1%
Net result: capture all errors + 0.1% of successes = representative sample
```

**OTel Collector — Tail Sampling Configuration:**

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317

processors:
  memory_limiter:
    check_interval: 1s
    limit_mib: 4096          # Hard cap; drops oldest spans if exceeded
    spike_limit_mib: 512

  tail_sampling:
    decision_wait: 30s         # Wait 30s for all spans of a trace to arrive
    num_traces: 500000         # Max traces buffered in memory (50k/s × 30s reserve)
    expected_new_traces_per_sec: 50000
    policies:
      # Always keep traces with errors
      - name: errors
        type: status_code
        status_code:
          status_codes: [ERROR, UNSET]

      # Always keep traces > 1s latency (P99 SLO concern)
      - name: high_latency
        type: latency
        latency:
          threshold_ms: 1000

      # Always keep traces for critical endpoints regardless of outcome
      - name: payment_endpoints
        type: and
        and:
          and_sub_policy:
            - name: payment_span
              type: span_name
              span_name:
                span_names: ["/payment/process", "/order/checkout", "/refund/initiate"]

      # Probabilistic fallback: keep 1% of everything else
      - name: probabilistic_fallback
        type: probabilistic
        probabilistic:
          sampling_percentage: 1

  batch:
    send_batch_size: 500
    timeout: 5s

exporters:
  otlp/jaeger:
    endpoint: jaeger-collector:4317
    tls:
      insecure: false

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, tail_sampling, batch]
      exporters: [otlp/jaeger]
```

**Failure Modes and Mitigations:**

1. **OOM on traffic spike:** `memory_limiter` drops oldest buffered traces. Result: some traces lost, but Collector stays alive. Monitor `otelcol_processor_tail_sampling_sampling_trace_dropped_count`.

2. **Incomplete traces (spans arrive after decision_wait):** Collector decides "keep/drop" based on incomplete data, then receives remaining spans. Those orphaned spans are exported without a matching trace decision — they appear in Jaeger as partial traces. Mitigation: increase `decision_wait` to 60s for async payment flows with long-running spans.

3. **Hot sharding:** All spans for a trace must land on the same Collector instance (consistent hashing by trace ID). Without this, tail sampling breaks — spans for the same trace are on different Collectors with different buffers. Use a **load balancer processor** in front:

```yaml
# Tier 1 Collector: routes spans by trace ID hash
processors:
  routing:
    from_attribute: traceID
    table:
      - value: "0-7"
        exporters: [otlp/collector-1]
      - value: "8-f"
        exporters: [otlp/collector-2]
```

**Exemplars — Linking Metrics to Traces Without Label Cardinality Cost:**

```python
# Instead of: http_requests_total{trace_id="abc123"} 1  ← BAD (cardinality explosion)
# Use exemplars:
from opentelemetry import trace
from prometheus_client import Histogram

REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'Latency')

def handle_request():
    span = trace.get_current_span()
    with REQUEST_LATENCY.time() as timer:
        timer.exemplar = {  # Prometheus 2.26+ native exemplars
            'traceID': format(span.get_span_context().trace_id, '032x')
        }
        do_work()
```

Query:
```promql
# Returns metric value + exemplar with trace ID for P99 slowest request
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))
```

---

**Q: Design a multi-region SLO with error budget allocation that survives a regional failover without triggering SLA breach.**

**Two-Level SLO Model:**

Define SLOs at both regional and global scopes:
- **Regional SLO:** 99.95% per region (21.6 min/month error budget)
- **Global SLO:** 99.9% globally (43.2 min/month) — more lenient because regional failover is expected

The global SLO is what customers are contractually promised. Regional SLOs are internal engineering targets.

**Error Budget Allocation:**

```
Global budget: 43.2 min/month

Traffic distribution:
  US-East: 50% → 21.6 min budget
  EU-West: 30% → 12.96 min budget
  AP-SE:   20% → 8.64 min budget

Emergency reserve: 10% of global budget for failover surge = 4.32 min
Operational budget per region: above minus 10% reserve
```

**PromQL SLO Burn Rate Alerts (Multi-Window):**

```yaml
# Global error ratio
- record: global:error_ratio:rate5m
  expr: >
    sum(rate(http_requests_total{status=~"5.."}[5m]))
    /
    sum(rate(http_requests_total[5m]))

# Per-region error ratio
- record: region:error_ratio:rate5m
  expr: >
    sum by(region)(rate(http_requests_total{status=~"5.."}[5m]))
    /
    sum by(region)(rate(http_requests_total[5m]))

# Multi-window burn rate alert (burns > 14.4x → exhausts monthly budget in 2h)
- alert: GlobalSLOCritical
  expr: >
    (global:error_ratio:rate5m > (14.4 * 0.001))
    and
    (global:error_ratio:rate1h > (14.4 * 0.001))
  labels:
    severity: critical
  annotations:
    summary: "Global SLO burning 14.4x rate — budget exhausted in < 2h"

- alert: GlobalSLOWarning
  expr: >
    (global:error_ratio:rate30m > (6 * 0.001))
    and
    (global:error_ratio:rate6h > (6 * 0.001))
  labels:
    severity: warning
  annotations:
    summary: "Global SLO burning 6x rate — budget exhausted in < 5 days"
```

**Handling Regional Failover:**

When US-East goes down, US-West and AP-SE absorb traffic. Two problems:
1. The failed region's errors should charge against its regional budget, not the healthy regions'
2. Failover traffic may overwhelm healthy regions (latency increase → SLO pressure)

**Implementation:**

```yaml
# Tag requests with region_served (not region_of_origin)
# When US-East fails, US-West processes US-East traffic:
# - These requests count toward US-West's SLI
# - US-West SLO budget burns faster during failover

# Mitigation: Widen SLO window during declared incident
- alert: RegionalFailoverActive
  expr: up{job="us-east-api"} == 0
  for: 2m
  annotations:
    action: "Silence US-East regional SLO alert; extend global SLO window"

# Use Alertmanager inhibition to suppress regional alerts during active failover
inhibit_rules:
  - source_match:
      alertname: RegionalFailoverActive
      region: us-east
    target_match:
      region: us-east
    equal: ['environment']
```

**Deployment Gating on Budget Exhaustion:**

```python
# Pre-deployment check (run in CI/CD pipeline)
import requests

def check_error_budget_before_deploy(service: str, env: str) -> bool:
    resp = requests.get(
        'http://prometheus:9090/api/v1/query',
        params={'query': f'1 - (sum(increase(http_requests_total{{job="{service}",status!~"5.."}}[30d])) / sum(increase(http_requests_total{{job="{service}"}}[30d])))'}
    )
    error_budget_remaining = float(resp.json()['data']['result'][0]['value'][1])
    if error_budget_remaining < 0.05:  # < 5% remaining
        print(f"ERROR: Less than 5% error budget remaining for {service}. Deployment blocked.")
        return False
    return True
```

---

**Q: Design a runbook automation framework for on-call that balances automated remediation with human judgment gates.**

**Runbook Maturity Model:**

```
Level 0: Ad-hoc (no runbook)
Level 1: Manual procedure document (Markdown in wiki)
Level 2: Semi-automated (runbook executes safe steps, human approves risky steps)
Level 3: Fully automated (human only notified after resolution or on failure)
```

Target Level 2 for most production incidents; Level 3 only for well-understood, idempotent remediations.

**Runbook Manifest:**

```yaml
# runbooks/high-api-latency.yaml
apiVersion: runbook.example.com/v1
kind: Runbook
metadata:
  name: high-api-latency
  severity: p2
spec:
  trigger:
    alert: APILatencyP99High
    threshold: 5m
  
  diagnostics:
    - name: check-failed-pods
      command: kubectl get pods -n api --field-selector=status.phase=Failed -o json
      timeout: 30s
      output_var: failed_pods
    
    - name: check-db-connections
      command: curl -s http://api-metrics:8080/db/connections
      timeout: 10s
      output_var: db_connections
  
  remediation:
    - name: scale-up-replicas
      condition: "len(failed_pods) > 2"
      command: kubectl scale deployment api --replicas=10 -n api
      approval_required: false       # Safe, reversible
      timeout: 60s
      on_failure: escalate
    
    - name: drain-connection-pool
      condition: "db_connections > 950"
      command: curl -X POST http://api:8080/admin/drain-connections
      approval_required: true        # Could drop in-flight requests
      approval_timeout: 300s         # If no response in 5 min, escalate
      timeout: 30s
      on_failure: alert
    
    - name: rollback-deployment
      condition: "recent_deploy_within_30m and error_rate_delta > 0.2"
      command: kubectl rollout undo deployment/api -n api
      approval_required: true        # Destructive
      timeout: 120s
      on_failure: escalate
  
  verification:
    - metric: histogram_quantile(0.99, rate(http_request_duration_seconds_bucket{job="api"}[5m]))
      threshold: "< 0.5"
      duration: 5m                   # Must hold for 5 minutes
  
  escalation:
    on_automation_failure: page_on_call_manager
    on_verification_failure: page_incident_commander
    total_timeout: 30m
```

**Approval Mechanism (Slack Bot):**

```python
from slack_sdk import WebClient

def request_approval(runbook_id: str, step: str, command: str, channel: str) -> str:
    client = WebClient(token=SLACK_BOT_TOKEN)
    resp = client.chat_postMessage(
        channel=channel,
        blocks=[
            {"type": "section", "text": {"type": "mrkdwn",
                "text": f"*Runbook approval required*\nStep: `{step}`\nCommand: `{command}`"}},
            {"type": "actions", "elements": [
                {"type": "button", "text": {"type": "plain_text", "text": "Approve"},
                 "action_id": "approve", "value": runbook_id, "style": "primary"},
                {"type": "button", "text": {"type": "plain_text", "text": "Reject"},
                 "action_id": "reject", "value": runbook_id, "style": "danger"},
            ]}
        ]
    )
    return resp['ts']  # Message timestamp for tracking
```

**Human Judgment Framework:**

- **Auto-approve** (no gate): Scale replicas up, restart a single unhealthy pod, flush caches
- **Require approval**: Drain connection pool, disable a feature flag, change rate limits
- **Never automate**: Database schema changes, secret rotation, infrastructure deletion, network policy changes
- **Escalate immediately**: Novel failure mode with no matching runbook, cascading failures across 3+ services

All executions logged to audit trail (Datadog/Splunk) with: `alert_name`, `step_executed`, `approved_by`, `duration`, `outcome`. Weekly review: steps that are always approved → remove gate. Steps that always fail → fix the automation.

---

**Q: Design a multi-tenant Prometheus/Mimir deployment. How do you enforce cardinality quotas per team without impacting other tenants?**

**Architecture: Mimir with Tenant Isolation**

```
Teams → Remote Write → Mimir Distributor (per-tenant rate limits)
                            │
                    ┌───────┴───────┐
                    │               │
              Mimir Ingester    Mimir Ruler
              (in-memory)      (per-tenant rules)
                    │               │
              Mimir Store-GW   Alertmanager
              (long-term S3)   (per-tenant routing)
```

**Mimir Per-Tenant Configuration:**

```yaml
# mimir.yaml
limits:
  # Global defaults
  ingestion_rate: 10000           # samples/sec per tenant
  ingestion_burst_size: 200000
  max_global_series_per_user: 500000
  max_global_series_per_metric: 50000
  max_label_names_per_series: 30
  max_label_value_length: 2048
  
  # Per-tenant overrides (in Mimir runtime config or per-tenant config file)
  # team-payment gets higher limits (large service, known cardinality)
  team-payment:
    ingestion_rate: 50000
    max_global_series_per_user: 2000000
  
  # team-sandbox is untrusted; hard limits
  team-sandbox:
    ingestion_rate: 1000
    max_global_series_per_user: 10000
```

**Tenant-Aware Remote Write (from each team's Prometheus):**

```yaml
# team-payment Prometheus remote_write
remote_write:
  - url: https://mimir.platform.example.com/api/v1/push
    headers:
      X-Scope-OrgID: team-payment        # Mimir tenant header
    queue_config:
      capacity: 10000
      max_shards: 30
      min_shards: 2
      max_samples_per_send: 2000
    tls_config:
      cert_file: /etc/tls/client.crt
      key_file: /etc/tls/client.key
```

**Query Isolation (Grafana per-Org):**

```yaml
# Grafana provisioning — each team gets their own Org
# Mimir datasource configured with team's X-Scope-OrgID
apiVersion: 1
datasources:
  - name: Mimir (team-payment)
    type: prometheus
    url: https://mimir.platform.example.com/prometheus
    jsonData:
      httpHeaderName1: "X-Scope-OrgID"
    secureJsonData:
      httpHeaderValue1: "team-payment"
```

Grafana sends `X-Scope-OrgID: team-payment` on every query, so Mimir only returns that tenant's series. Cross-tenant queries are impossible from Grafana.

**Cardinality Enforcement — Rejection at Ingestion:**

When `team-sandbox` exceeds 10k series, Mimir returns HTTP 429 to their Prometheus remote_write:

```
level=warn component=remote_write msg="Failed to send batch, will retry"
err="server returned HTTP status 429 Too Many Requests: user 'team-sandbox' has reached the limit of 10000 in-memory series"
```

Their Prometheus queues the samples and retries. New unique series are rejected; existing series continue writing. This gives teams immediate feedback (unlike silent data loss) and doesn't impact other tenants.

**Platform Cardinality Dashboard (cross-tenant, platform team only):**

```promql
# Platform-level recording rule (evaluated with admin tenant)
# Total series per tenant
- record: platform:series_per_tenant
  expr: sum by(user)(cortex_ingester_memory_series_created_total{cluster="mimir-prod"})

# Alert platform team when any tenant approaches their limit
- alert: TenantNearCardinityLimit
  expr: >
    (platform:series_per_tenant / on(user) group_left()
     mimir_limits_max_global_series_per_user) > 0.8
  annotations:
    summary: "Tenant {{ $labels.user }} at {{ $value | humanizePercentage }} of cardinality limit"
    action: "Contact team to review label usage before limit is hit"
```
