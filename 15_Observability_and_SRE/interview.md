# Observability & SRE — Interview Questions

All difficulty levels combined.

---

## Easy

**1. What is the difference between monitoring and observability?**

Monitoring watches for pre-defined problems — it tells you _that_ something is wrong using dashboards and threshold alerts. Observability is about having enough telemetry data to debug novel, previously unseen problems — it lets you ask arbitrary questions about system internals to figure out _why_ something is wrong.

**2. What are the three pillars of observability?**

Metrics (numerical time-series data: request count, CPU usage, error rate), Logs (timestamped records of discrete events), and Traces (records of a request's journey through a distributed system showing latency at each hop). Together they provide the signals to understand a system's internal state from its external outputs.

**3. What is Prometheus and how does it collect metrics?**

Prometheus is an open-source monitoring and alerting toolkit using a pull model — it periodically scrapes HTTP `/metrics` endpoints exposed by applications and infrastructure components. Scraped data is stored in its local time-series database and evaluated against alerting rules. Exporters (node_exporter, blackbox_exporter) expose metrics from systems that don't natively support Prometheus.

**4. What is Grafana used for?**

Grafana is a visualization and dashboarding platform. It connects to data sources (Prometheus, Loki, Elasticsearch, Tempo, Azure Monitor, CloudWatch) and renders time-series graphs, heatmaps, and alert panels. It's the standard UI layer for observability stacks.

**5. What is the ELK stack?**

ELK stands for Elasticsearch, Logstash, and Kibana. Filebeat or Logstash ship logs to Elasticsearch, which indexes and stores them. Kibana provides a web UI for searching, filtering, and visualizing logs. The modern variant often replaces Logstash with Fluent Bit for lower overhead.

**6. What is an SLI and an SLO?**

- **SLI (Service Level Indicator):** A quantitative measurement of service behavior — e.g., the ratio of successful HTTP requests to total requests over a 1-minute window.
- **SLO (Service Level Objective):** A target threshold for an SLI over a defined period — e.g., "99.9% of requests succeed over a rolling 30-day window."

**7. What is distributed tracing?**

Distributed tracing tracks a single request as it flows through all the services it touches, assigning a unique trace ID and creating a "span" for each service hop. The collected spans provide a full call graph showing exactly where time was spent, enabling pinpointing of latency bottlenecks and error sources across microservices.

**8. What is a health check or liveness probe in Kubernetes?**

A liveness probe is a check the Kubelet performs periodically to determine if a container is still running. If the probe fails (HTTP 5xx, TCP timeout, exit code non-zero), the Kubelet kills and restarts the container. Readiness probes control whether traffic is sent to the pod; startup probes handle slow-starting containers.

---

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

---

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
