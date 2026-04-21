# Monitoring and Observability

This section focuses on maintaining the health, performance, and reliability of your infrastructure and applications.

#### A. Prometheus (The Metrics Collector)

Prometheus is a powerful open-source tool designed for monitoring highly dynamic, containerized environments like Kubernetes.

* Metrics Collection (Pull Model): Unlike many monitoring tools that wait for servers to send data, Prometheus scrapes (pulls) metrics from your applications and infrastructure at regular intervals.
* TSDB (Time Series Database): Prometheus stores data as "Time Series," meaning every piece of information is recorded with a timestamp. This is ideal for tracking trends over time (e.g., CPU usage over 24 hours).
* PromQL: A specialized query language used to slice and dice your data. For example, you can calculate the average response time for only the "Login" page over the last 5 minutes.
* Alerting (Alertmanager): When a metric crosses a dangerous threshold (e.g., Disk Space > 90%), Prometheus sends a signal to the Alertmanager, which then routes notifications to Slack, Email, or PagerDuty.

#### B. Grafana (The Visualization Hub)

While Prometheus collects the data, Grafana turns that raw data into beautiful, actionable dashboards.

* Dashboards and Visualization: Grafana connects to various data sources (Prometheus, CloudWatch, SQL) to create real-time graphs, heatmaps, and tables. It allows you to see the "big picture" of your entire infrastructure in one place.
* k6 Load Testing: k6 is a modern tool for performance testing. In DevOps, you use k6 to simulate thousands of users hitting your app. By integrating k6 with Grafana, you can visualize exactly how your servers' CPU and RAM react under heavy load in real-time.

#### C. ELK Stack (The Logging Engine)

While Prometheus handles Metrics (numbers), the ELK stack handles Logs (text events). It helps you answer the question: _"Exactly what happened when this error occurred?"_

* Elasticsearch (E): The "brain" of the stack. It is a distributed search engine that stores and indexes your logs so they can be searched instantly, even if you have billions of lines of data.
* Logstash (L): The "translator." It collects logs from different sources, cleans them up (filters), and transforms them into a common format before sending them to Elasticsearch.
* Kibana (K): The "interface." This is the web UI where you search through your logs and build visualizations to track things like "Top 10 IP addresses causing 404 errors."

***

#### Summary Table: Metrics vs. Logs

| **Feature** | **Prometheus (Metrics)**     | **ELK Stack (Logs)**               |
| ----------- | ---------------------------- | ---------------------------------- |
| Data Type   | Numbers (CPU, RAM, Requests) | Text (Error messages, Access logs) |
| Focus       | "Is the system healthy?"     | "Why did the system fail?"         |
| Storage     | Very efficient (small size)  | Heavy (requires more disk space)   |
| Search      | High-level trends            | Deep-dive forensic investigation   |

***

This is Section 9: Monitoring & Observability. For a mid-to-senior SRE/DevOps role, this is where you prove you can manage a system's health. It’s no longer about "Is the server up?" but "Is the user experience degraded, and if so, where is the bottleneck?"

In production, you don't want to find out about an issue from a customer tweet. You want to find out from your SLO-based alerts.

***

#### 🔹 1. Improved Notes: Monitoring vs. Observability

**The Three Pillars of Observability**

1. Metrics (Prometheus/Grafana): Numerical data over time. Great for "Is there a problem?" (e.g., CPU is 90%, 5xx errors are spiking).
2. Logs (ELK/EFK Stack): Textual records of events. Great for "What exactly happened?" (e.g., NullPointerException in the Auth service).
3. Traces (Jaeger/Zipkin/OpenTelemetry): Follows a single request through multiple microservices. Great for "Where is the delay?"

**The SRE Framework: The Four Golden Signals**

If you can only monitor four things, monitor these:

* Latency: The time it takes to service a request.
* Traffic: The demand placed on the system (HTTP requests/sec).
* Errors: The rate of requests that fail (explicitly, implicitly, or by policy).
* Saturation: How "full" your service is (e.g., memory usage, disk I/O).

**SRE Metrics: The Math of Reliability**

* SLI (Service Level Indicator): A specific metric (e.g., "HTTP response time").
* SLO (Service Level Objective): The target for an SLI (e.g., "99.9% of requests will be < 200ms").
* SLA (Service Level Agreement): The legal contract with customers (e.g., "If we drop below 99% uptime, we pay you back").
* Error Budget: The amount of "unreliability" you are allowed to have ($$ $1 - SLO$ $$). If you use it all, you stop all new feature releases and focus on stability.

***

#### 🔹 2. Interview View (Q\&A)

Q1: Explain the difference between Push vs. Pull monitoring. Which does Prometheus use?

* Answer: Prometheus uses a Pull-based model. It "scrapes" metrics from applications at regular intervals.
  * _Push:_ The app sends data to the monitor (e.g., StatsD/CloudWatch). Better for short-lived jobs (Lambda).
  * _Pull:_ The monitor fetches data. Better for detecting if a service is down (if you can't scrape it, it's dead) and prevents the monitoring system from being "DDoS'ed" by its own applications.

Q2: What is "High Cardinality" in Prometheus and why is it dangerous?

* Answer: Cardinality refers to the number of unique label combinations. If you add `user_id` as a label to a metric, and you have 1 million users, Prometheus will create 1 million time-series. This leads to TSDB (Time Series Database) explosion, high memory usage, and can crash your monitoring server.
* Follow-up: "How do you avoid it?" -> Never use unique IDs, emails, or timestamps as labels. Use categories (e.g., `region`, `status_code`).

Q3: How do you reduce "Alert Fatigue"?

*   Answer: 1. Only alert on Symptom-based issues (e.g., "User facing 5xx errors") rather than Cause-based (e.g., "One server has high CPU").

    2\. Ensure every alert is Actionable. If an engineer receives an alert and doesn't know what to do, it shouldn't be an alert.

    3\. Route alerts to the correct place (Critical to PagerDuty/Phone; Warning to Slack).

***

#### 🔹 3. Architecture & Design: The Observability Stack

Design Concern: High Availability (HA) for Monitoring

* Prometheus is single-node by design. To scale it for a multi-cluster environment, SREs use Thanos or Cortex. These allow for:
  * Global Query View (one dashboard for all clusters).
  * Long-term storage in S3/GCS.
  * High availability (deduplicating data from multiple Prometheuses).

Failure Scenarios:

* The "Heisenbug": An error that only occurs under specific network conditions. Without Distributed Tracing (Jaeger), you might spend days looking at logs without finding which of the 10 microservices caused the timeout.

***

#### 🔹 4. Commands & Configs (The SRE Pro Toolset)

**PromQL: The "Golden" Query**

To calculate the error rate of an application:

\$$Rate = \frac{\text{sum by (app) (rate(http\\\_requests\\\_total\\{status=\~"5.."\\} \[5m]))\}}{\text{sum by (app) (rate(http\\\_requests\\\_total\[5m]))\}}\$$

**Prometheus Alert Rule Example**

YAML

```
groups:
- name: app_alerts
  rules:
  - alert: HighErrorRate
    expr: job:http_errors:rate5m > 0.05
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "High error rate on {{ $labels.instance }}"
      description: "Error rate is above 5% for more than 2 minutes."
```

***

#### 🔹 5. Troubleshooting & Debugging

Scenario: Grafana shows "No Data" for a specific service.

1. Check Service Discovery: Is Prometheus finding the target? (Check `/targets` page in Prometheus UI).
2. Check the Exporter: Is the `/metrics` endpoint reachable from the Prometheus pod? Use `curl <pod_ip>:8080/metrics`.
3. Check Network Policies: Is there a Kubernetes NetworkPolicy blocking traffic between the Prometheus namespace and the App namespace?
4. Check Scraping Interval: If the app is very fast (e.g., a CronJob), Prometheus might be missing it between scrapes. Use a Pushgateway.

***

#### 🔹 6. Production Best Practices

* Log Sampling: In high-traffic environments, logging _everything_ to Elasticsearch is too expensive. Sample 10% of "200 OK" logs but 100% of "5xx" logs.
* Standardized Labels: Ensure every team uses the same labels (e.g., `env`, `service`, `version`). Without this, you can't build global dashboards.
* Dashboarding Best Practice: Use the "Breadth-first" approach. One high-level dashboard for the whole system, with links to "drill-down" dashboards for specific services.
* Anti-Pattern: Monitoring CPU/RAM as a primary alert. CPUs spike all the time without user impact. Monitor the User Experience (Latency/Errors) first.

***

#### 🔹 Cheat Sheet / Quick Revision

| **Concept**  | **Key SRE Detail**                                                  |
| ------------ | ------------------------------------------------------------------- |
| Prometheus   | Pull-based, TSDB, PromQL, 15-day default retention.                 |
| Alertmanager | Handles grouping, silencing, and routing alerts.                    |
| Exporter     | A "sidecar" that translates app metrics into Prometheus format.     |
| Loki         | "Prometheus for logs"—highly efficient log storage.                 |
| Cardinality  | The unique count of label values. High = Bad.                       |
| MTTR         | Mean Time To Recovery (The goal of observability is to lower this). |

***

This is Section 9: Monitoring & Observability. In a production environment, monitoring is your "eyes and ears." For a senior SRE role, the interviewer wants to see if you can distinguish between "knowing a system is down" and "understanding why a system is behaving poorly."

***

#### 🟢 Easy: Monitoring Foundations

_Focus: Basic terminology and the goals of monitoring._

1. What is the difference between Monitoring and Observability?
   * _Context:_ Monitoring tells you _if_ a system is working; Observability allows you to understand _why_ it isn't working by looking at the internal state.
2. What are the "Four Golden Signals" of monitoring?
   * _Context:_ Latency, Traffic, Errors, and Saturation.
3. Explain the difference between Metrics, Logs, and Traces.
   * _Context:_ The "Three Pillars." Metrics are for trends; Logs are for events; Traces are for request flow across services.
4. What is a "Health Check" (Liveness/Readiness), and why is it important for a Load Balancer?
   * _Context:_ How does the system know to stop sending traffic to a broken instance?

***

#### 🟡 Medium: SRE Principles & Tooling

_Focus: Measuring reliability and managing alerts._

1. Explain the relationship between SLI, SLO, and SLA.
   * _Context:_ \* SLI: What you measure (e.g., Latency).
     * SLO: The target you set (e.g., 99th percentile < 200ms).
     * SLA: The legal agreement (e.g., "If we fail the SLO, we pay you").
2. What is an "Error Budget," and how does it help balance Feature Velocity vs. Reliability?
   * _Context:_ If the budget is exhausted ($$ $1 - SLO$ $$), the team stops new releases and focuses on stability.
3. Does Prometheus use a "Pull" or "Push" model? What are the pros and cons of its approach?
   * _Context:_ Pull is great for service discovery and health; Push is better for short-lived batch jobs (using a Pushgateway).
4. How do you handle "Alert Fatigue" in a large engineering team?
   * _Context:_ Discuss symptom-based alerting vs. cause-based alerting. Every alert must be actionable.
5. What is a "Time Series Database" (TSDB), and why is it preferred over a Relational DB for monitoring?
   * _Context:_ Efficiency in storing and querying data that changes over time.

***

#### 🔴 Hard: Advanced Querying & Scaling

_Focus: PromQL, high cardinality, and distributed systems._

1. What is "High Cardinality" in Prometheus, and why can it crash your monitoring server?
   * _Context:_ Adding labels like `user_id` or `timestamp` creates millions of unique time series, exhausting memory.
2. Write a PromQL query to calculate the "Error Rate Percentage" over the last 5 minutes.
   *   Context: You should be able to explain the logic using LaTeX:

       \$$\text{Error Rate} = \frac{\text{sum(rate(http\\\_requests\\\_total\\{status=\~"5.."\\} \[5m]))\}}{\text{sum(rate(http\\\_requests\\\_total\[5m]))\}} \times 100\$$
3. How do you scale Prometheus for a global, multi-cluster environment?
   * _Context:_ Mention hierarchical federation or tools like Thanos or Cortex for long-term storage and a "Global View."
4. Explain "Distributed Tracing." How does a Trace ID propagate through multiple microservices?
   * _Context:_ Discuss metadata injection into HTTP headers (like `X-Trace-Id`) and how a collector (Jaeger/Zipkin) reassembles the spans.
5. Scenario: Your dashboard shows a spike in "99th Percentile Latency" but the "Average Latency" remains normal. What does this tell you?
   * _Context:_ This indicates a "long tail" issue. A small group of users is experiencing extreme delays, while most are fine. This is often caused by resource contention, garbage collection (GC) pauses, or a specific slow backend node.

***

#### 💡 Pro-Tip for your Interview

When answering monitoring questions, always focus on the User Experience.

* The SRE Answer: "I don't just monitor CPU usage. If CPU is at 90% but the user-facing Latency is low and Success Rate is 100%, I don't page an engineer. I prioritize Symptom-based alerting over Cause-based alerting to ensure we only wake people up for issues that actually impact the business."

---

## 🔷 Advanced Observability (7 YOE)

---

### Section A: Azure Monitor & Application Insights

For engineers operating in the Azure ecosystem, Azure Monitor is the native observability plane that spans all resources.

#### Key Components

| Component | Purpose | Equivalent (Generic) |
|---|---|---|
| **Azure Monitor Metrics** | Numerical time-series from Azure resources | Prometheus |
| **Log Analytics Workspace (LAW)** | Centralised log storage and query engine | Elasticsearch / Loki |
| **Application Insights** | APM — traces, dependencies, exceptions | Jaeger + OpenTelemetry |
| **Azure Monitor Alerts** | Alert rules backed by metrics or KQL queries | Alertmanager |
| **Workbooks** | Interactive, parameterised dashboards | Grafana |

#### KQL (Kusto Query Language) — Essential Patterns

**Find failed requests in Application Insights:**
```kusto
requests
| where success == false
| summarize count() by name, resultCode
| order by count_ desc
```

**Detect slow SQL dependencies (>500ms):**
```kusto
dependencies
| where type == "SQL"
| where duration > 500
| project timestamp, target, data, duration
| order by duration desc
```

**Burn rate calculation (Azure Monitor style):**
```kusto
let slo_target = 0.999;  // 99.9% SLO
let error_budget = 1 - slo_target;
let burn_multiplier = 14.0;  // 14× burn rate = critical
requests
| where timestamp > ago(1h)
| summarize total = count(), failed = countif(success == false)
| extend error_rate = toreal(failed) / toreal(total)
| extend is_burning = error_rate > (burn_multiplier * error_budget)
```

**AKS node memory pressure over last 24h:**
```kusto
Perf
| where ObjectName == "Memory" and CounterName == "Available MBytes"
| where Computer startswith "aks-"
| summarize avg_available_mb = avg(CounterValue) by Computer, bin(TimeGenerated, 30m)
| order by TimeGenerated desc
```

#### Application Insights — Distributed Tracing

Application Insights uses the W3C `traceparent` standard to propagate trace context across HTTP calls. Each SDK auto-instruments:
- HTTP in/out calls
- SQL queries (via ADO.NET / Entity Framework)
- Azure service calls (Service Bus, Blob, CosmosDB)

Key signal: The **Application Map** identifies which dependency is responsible for high latency or failure rates with a call graph view.

---

### Section B: Advanced PromQL — Burn Rate Alerting

Standard threshold alerting (e.g., `error_rate > 5%`) is noisy and lacks context. **Burn Rate Alerting** ties alert severity to the rate at which you consume your error budget.

#### The Multi-Window, Multi-Burn-Rate Pattern

The Google SRE Workbook recommends pairing a short window (high sensitivity) with a long window (high specificity) to avoid false positives:

| Alert Name | Short Window | Long Window | Burn Rate | Urgency |
|---|---|---|---|---|
| `CriticalBurnRate` | 5m | 1h | 14× | Page immediately |
| `HighBurnRate` | 30m | 6h | 3× | Slack alert |

**PromQL — Critical Burn Rate (14×) for 99.9% SLO:**
```promql
# Short window component
(
  sum(rate(http_requests_total{status=~"5.."}[5m]))
  /
  sum(rate(http_requests_total[5m]))
) > (14 * 0.001)

AND

# Long window component (confirmation signal)
(
  sum(rate(http_requests_total{status=~"5.."}[1h]))
  /
  sum(rate(http_requests_total[1h]))
) > (14 * 0.001)
```

#### `irate` vs `rate` — When to Use Which

| Function | Behaviour | Use Case |
|---|---|---|
| `rate(metric[5m])` | Average rate over the full window | Alerting — smooths out spikes |
| `irate(metric[5m])` | Instantaneous rate (last two samples) | Debugging — shows real-time spikes |

**Rule:** Always use `rate` for alert rules. `irate` creates unstable, volatile alert conditions.

#### Recording Rules (Performance Optimisation)

Complex PromQL run thousands of times per minute is expensive. Recording rules pre-compute results at scrape time:

```yaml
groups:
  - name: slo_recording_rules
    interval: 30s
    rules:
      - record: job:http_requests:rate5m
        expr: sum(rate(http_requests_total[5m])) by (job)
      - record: job:http_errors:rate5m
        expr: sum(rate(http_requests_total{status=~"5.."}[5m])) by (job)
      - record: job:http_error_ratio:rate5m
        expr: job:http_errors:rate5m / job:http_requests:rate5m
```

Now alert on `job:http_error_ratio:rate5m > 0.05` — this query runs in microseconds versus seconds for the raw expression.

---

### Section C: OpenTelemetry & eBPF

#### Why OpenTelemetry Is the Industry Standard

Before OpenTelemetry (OTel), every APM vendor had a proprietary SDK (Datadog, New Relic, Dynatrace). Switching vendors meant re-instrumenting all application code.

**OpenTelemetry solves this** with a vendor-neutral standard for traces, metrics, and logs — the three pillars — with a single open protocol: **OTLP (OpenTelemetry Protocol)**.

```
App (OTel SDK) → OTLP → OTel Collector → [Jaeger / Tempo / Datadog / Azure Monitor]
```

The OpenTelemetry Collector (`otelcol`) acts as a pipeline:
- **Receivers:** Accept data (OTLP, Prometheus scrape, Jaeger, Zipkin)
- **Processors:** Transform (sampling, attribute enrichment, batching)
- **Exporters:** Send to backends (Jaeger, Prometheus remote-write, Azure Monitor)

**Kubernetes deployment pattern:**
```yaml
# DaemonSet collector — one per node, collects logs + host metrics
# Sidecar collector — per application pod, collects app traces
# Deployment collector — central gateway for complex routing logic
```

#### eBPF — Zero-Instrumentation Observability

eBPF (extended Berkeley Packet Filter) allows small programs to run inside the Linux kernel without modifying the kernel source or recompiling application code.

**Key capabilities:**
- Intercept every network packet at kernel level → service-to-service golden signals without modifying application code.
- Trace system calls (`execve`, `openat`, `connect`) → security anomaly detection (Falco, Tetragon).
- Generate rich L7 metrics (HTTP, gRPC, DNS) → without any application SDK.

**Tools:**
- **Cilium** — Kubernetes CNI that replaces iptables with eBPF. Enforces NetworkPolicies at kernel speed. Provides Layer 7 visibility.
- **Pixie** — Auto-instrumentation platform. Provides service maps, request traces, and SQL query analysis with zero code changes.
- **Tetragon** — Kubernetes-aware runtime security using eBPF. Replaces Falco for high-performance threat detection.

---

### Section D: Multi-Cluster Observability Design

A single Prometheus instance cannot scale infinitely. When operating multiple Kubernetes clusters (dev, staging, prod, regional clusters), you need a federated observability strategy.

#### Option Comparison

| Solution | Architecture | Best For | Trade-offs |
|---|---|---|---|
| **Thanos** | Prometheus + Sidecar + Object Store (S3/Blob) | Long-term storage, global query view | Operational complexity, multiple components |
| **Cortex** | Multi-tenant Prometheus-as-a-service | Shared platform, per-team tenancy | Very complex to operate self-hosted |
| **VictoriaMetrics** | Drop-in Prometheus replacement | High-performance, low memory footprint | Less ecosystem integration than Thanos |
| **Azure Managed Prometheus** | Fully managed Azure Monitor workspace | Azure-native, zero ops burden | Azure-only, less PromQL flexibility |
| **Grafana Cloud** | SaaS | Small team, managed | Cost at scale, data residency concerns |

#### 7 YOE Recommendation: Thanos Architecture

```
Cluster A                     Object Store (Azure Blob / S3)
┌────────────────┐            ┌─────────────────────────────┐
│ Prometheus A   │──sidecar──>│  Historical data (>14 days) │
└────────────────┘            └─────────────────────────────┘
                                          │
Cluster B                                 │
┌────────────────┐                  Thanos Query
│ Prometheus B   │──sidecar──────>  (Global view)
└────────────────┘                        │
                                    Grafana Dashboard
                              (queries all clusters via single endpoint)
```

Key Thanos components:
- **Sidecar:** Runs alongside each Prometheus. Uploads blocks to object store.
- **Store Gateway:** Serves historical data from object store.
- **Query:** Fan-out query to all sidecars + store gateways. Deduplicates replicas.
- **Compactor:** Downsamples and compacts old blocks for cost efficiency.

#### Azure Managed Prometheus + Grafana (Simplest Enterprise Path)

For Azure-native environments, use:
1. **Azure Monitor workspace** → acts as the managed Prometheus backend.
2. **Azure Managed Grafana** → pre-connected to the Prometheus workspace.
3. **AKS monitoring addon** → automatically deploys and manages the Prometheus scraping agent.

```bash
# Enable managed Prometheus on AKS cluster
az aks update \
  --resource-group <rg> \
  --name <cluster> \
  --enable-azure-monitor-metrics \
  --azure-monitor-workspace-resource-id <workspace-id>
```

This eliminates the need to operate Thanos entirely for Azure-native workloads.
