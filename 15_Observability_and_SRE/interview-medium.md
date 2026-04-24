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

