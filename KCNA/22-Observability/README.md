# 22 — Observability

## 1. Learning Objectives

By the end of this chapter you will be able to:

- Explain the three pillars of observability: logs, metrics, and traces.
- Explain liveness, readiness, and startup probes and how they differ.
- Explain how Prometheus-style metrics collection works in Kubernetes.
- Explain distributed tracing's role in microservice troubleshooting.
- Read and write probe configuration in a Pod manifest.

**KCNA objectives covered:** Cloud Native Observability domain.

---

## 2. Historical Background

In traditional, monolithic applications running on a handful of long-lived servers, understanding system health was relatively simple — a few log files and basic server metrics (CPU, memory) usually sufficed, and an operator could often just SSH in and look around. As applications decomposed into many small, distributed microservices running across dynamic, ephemeral Pods (Chapter 10) that could be created, destroyed, and rescheduled at any time, this simple approach broke down completely — there was no single "the server" to SSH into anymore, and a single user request might now pass through a dozen different services. This drove the rise of **observability** as a discipline: structured logging, centralized metrics collection (led by tools like **Prometheus**), and **distributed tracing** to follow a request's journey across many services.

---

## 3. Motivation: Why Does Kubernetes Need Built-in Observability Primitives?

**Analogy — The Hospital's Vital Signs Monitor:**
A hospital doesn't wait for a patient to collapse before checking on them — it continuously monitors vital signs (heart rate, blood pressure, oxygen levels) via bedside monitors, and additionally keeps a written chart (the patient's history) and can order specific diagnostic tests (like tracing exactly which organ is causing a symptom) when something specific needs deeper investigation. Kubernetes needs the same three complementary views into a running system: **metrics** (continuous vital-signs-style numeric measurements), **logs** (the written history of discrete events), and **traces** (a detailed diagnostic path through a specific request), plus its own built-in vital-signs check — **probes** — that continuously verify whether a Pod is alive and ready to serve traffic, without waiting for a human to notice something's wrong.

### 3.1 How Was This Solved Before Kubernetes?

Long-lived servers were monitored with simple, host-centric tools (syslog, basic CPU/memory graphs, manual log-file inspection) that assumed a small, mostly-static set of machines.

### 3.2 Why Was That Insufficient?

Dynamic, ephemeral, distributed microservice environments make host-centric monitoring meaningless — Pods come and go constantly, a single request spans many services, and there's no stable "the server" to manually inspect; understanding system health requires structured, aggregated, and correlated data across the whole distributed system.

### 3.3 How Kubernetes Solves It

Kubernetes builds in **liveness/readiness/startup probes** as automated, continuous health checks that drive restart and traffic-routing decisions, and integrates naturally with the broader cloud native observability ecosystem — **Prometheus** for metrics (pull-based scraping of exposed `/metrics` endpoints), structured **logging** (typically shipped off-Pod to a centralized backend since container logs are ephemeral), and **distributed tracing** (e.g., OpenTelemetry) for following requests across services.

---

## 4. Core Concepts

### 4.1 The Three Pillars of Observability

| Pillar | Answers | Example Tooling |
|---|---|---|
| Logs | What discrete events happened? | Fluentd/Fluent Bit, Loki, ELK stack |
| Metrics | What is the numeric state/trend of the system over time? | Prometheus, Grafana |
| Traces | What was the full path of one specific request across services? | Jaeger, Zipkin, OpenTelemetry |

### 4.2 Probes

**Definition:** A **probe** is a periodic health check the kubelet performs against a container.

| Probe Type | Question Answered | Failure Consequence |
|---|---|---|
| Liveness Probe | Is the container still alive/functioning? | kubelet restarts the container |
| Readiness Probe | Is the container ready to serve traffic? | Pod is removed from Service Endpoints (Chapter 16) until it passes again |
| Startup Probe | Has the container finished its (possibly slow) startup? | Liveness/readiness probes are held off until this succeeds, avoiding premature restarts of slow-starting apps |

### 4.3 Metrics and Prometheus

**Definition:** **Prometheus** is a pull-based metrics system that periodically **scrapes** numeric metrics from applications and cluster components exposing a `/metrics` HTTP endpoint in Prometheus's text format, storing them as time series for querying (via PromQL) and visualization (commonly via Grafana).

### 4.4 Logging

Containers write logs to `stdout`/`stderr`, captured by the container runtime; because Pods are ephemeral, logs must be shipped off-node to a centralized backend (e.g., via a log-forwarding agent like Fluent Bit) to survive Pod deletion and be searchable across the whole cluster.

### 4.5 Distributed Tracing

**Definition:** Distributed tracing instruments a request with a unique trace ID as it flows across multiple services, recording timing and metadata for each "span" (a unit of work within one service) — reassembled into a full trace showing exactly where time was spent and where failures occurred across a multi-service call chain.

---

## 5. Internal Working

```
1. kubelet periodically runs configured probes (HTTP GET, TCP
   socket, or exec command) against each container
        ↓
2a. Liveness probe fails repeatedly → kubelet kills and restarts
    the container
        ↓
2b. Readiness probe fails → Pod is removed from the Service's
    Endpoints/EndpointSlice (Chapter 16) — stops receiving traffic
    without being restarted
        ↓
3. Meanwhile, Prometheus periodically scrapes each instrumented
   Pod/component's /metrics endpoint, storing results as time series
        ↓
4. Application logs stream to stdout/stderr, picked up by a node-level
   log-forwarding agent and shipped to a centralized log backend
        ↓
5. If distributed tracing is instrumented, each request propagates a
   trace ID across service calls, with spans collected centrally for
   full-path visualization
```

---

## 6. Architecture

```
              ┌─────────────┐
              │      Pod       │
              │  (app + /metrics│
              │   + probes)     │
              └──────┬──────┘
       ┌───────────┼───────────┐
       ▼                  ▼                  ▼
┌─────────┐      ┌─────────────┐   ┌─────────────┐
│ kubelet    │      │  Prometheus    │   │ Log-forwarding │
│ (probes)   │      │  (scrapes        │   │ agent            │
│            │      │   /metrics)      │   │ (ships stdout)   │
└─────────┘      └──────┬──────┘   └──────┬──────┘
                                ▼                          ▼
                        ┌─────────────┐          ┌─────────────┐
                        │   Grafana      │          │  Centralized    │
                        │ (dashboards)   │          │  log backend     │
                        └─────────────┘          └─────────────┘
```

---

## 7. Component Breakdown

| Component | Role |
|---|---|
| kubelet | Executes liveness/readiness/startup probes (Chapter 08) |
| Prometheus | Pull-based metrics scraping and time-series storage |
| Grafana | Metrics/log visualization and dashboards |
| Log-forwarding agent | Ships container stdout/stderr logs off-node to a centralized backend |
| Tracing backend (Jaeger/Zipkin) | Collects and visualizes distributed trace spans |

---

## 8. Important Terminology

| Term | Meaning |
|---|---|
| Liveness Probe | Health check determining whether to restart a container |
| Readiness Probe | Health check determining whether a Pod should receive traffic |
| Startup Probe | Health check delaying liveness/readiness checks until slow startup completes |
| Prometheus | Pull-based metrics collection and storage system |
| PromQL | Prometheus's query language for metrics |
| Trace | The full recorded path of one request across multiple services |
| Span | A single unit of work within a trace, scoped to one service/operation |
| OpenTelemetry | Vendor-neutral standard/toolkit for generating traces, metrics, and logs |

---

## 9. YAML Deep Dive

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: observable-app
spec:
  containers:
    - name: app
      image: myapp:1.0
      ports:
        - containerPort: 8080
      startupProbe:
        httpGet:
          path: /healthz
          port: 8080
        failureThreshold: 30
        periodSeconds: 10
      livenessProbe:
        httpGet:
          path: /healthz
          port: 8080
        periodSeconds: 10
        failureThreshold: 3
      readinessProbe:
        httpGet:
          path: /ready
          port: 8080
        periodSeconds: 5
        failureThreshold: 2
```

The `startupProbe` allows up to 300 seconds (`30 × 10s`) for slow initial startup before liveness/readiness probes begin — preventing a slow-starting app from being killed prematurely by an impatient liveness probe.

---

## 10. kubectl Commands

| Command | Purpose | Example |
|---|---|---|
| `kubectl logs <pod>` | View a Pod's container logs | `kubectl logs observable-app` |
| `kubectl logs <pod> --previous` | View logs from a crashed/restarted container's previous run | `kubectl logs observable-app --previous` |
| `kubectl describe pod <pod>` | Show probe failure events | `kubectl describe pod observable-app` |
| `kubectl top pods` | Show live CPU/memory usage (requires metrics-server) | `kubectl top pods` |
| `kubectl port-forward svc/prometheus 9090:9090` | Access Prometheus's UI locally | `kubectl port-forward svc/prometheus 9090:9090` |

---

## 11. Hands-on Examples

**Lab 1 — Observe a failing readiness probe removing a Pod from Service traffic:**
```bash
kubectl apply -f observable-app.yaml
kubectl exec observable-app -- curl -X POST localhost:8080/set-unready
kubectl get endpoints observable-app-svc
# Pod's IP disappears from the Endpoints list, but the Pod keeps running
```

**Lab 2 — Observe a failing liveness probe triggering a restart:**
```bash
kubectl exec observable-app -- curl -X POST localhost:8080/crash-healthz
kubectl get pod observable-app -w
# RESTARTS count increments after failureThreshold is reached
```

**Lab 3 — Query a scraped metric in Prometheus:**
```bash
kubectl port-forward svc/prometheus 9090:9090
# In browser: http://localhost:9090, query: rate(http_requests_total[5m])
```

---

## 12. Internal Flow

See Section 5 — probes are Kubernetes's own **built-in** observability primitive (restart/traffic decisions), while metrics, logs, and traces are the broader **cloud native observability ecosystem** Kubernetes integrates with but does not implement natively — all four combine to answer "is this healthy," "what's the trend," "what specifically happened," and "where exactly did this request go wrong."

---

## 13. Real-World Examples

1. **Zero-downtime deployments** (Chapter 12) rely on readiness probes to ensure traffic is never routed to a new Pod version before it's actually ready to serve.
2. **Slow-starting legacy Java applications** commonly use a generous startup probe to avoid liveness-probe-triggered restart loops during long JVM warm-up.
3. **SRE teams** (Chapter 15 Observability and SRE domain preview) build Grafana dashboards on top of Prometheus metrics to track SLIs/SLOs across services.
4. **Microservice debugging** uses distributed tracing to pinpoint which specific downstream service in a call chain is responsible for elevated latency.
5. **Centralized logging platforms** (e.g., an ELK or Loki stack) aggregate logs from thousands of ephemeral Pods, making them searchable long after the originating Pod has been deleted.

---

## 14. Best Practices

- Always configure both **liveness** and **readiness** probes separately — conflating them (e.g., using the same aggressive check for both) can cause unnecessary restarts when a Pod is merely temporarily busy, not actually broken.
- Use a **startup probe** for any application with meaningfully slow initialization, rather than tuning liveness probe thresholds to compensate.
- Expose a lightweight, dependency-free `/healthz` endpoint for liveness (checking only "is the process alive"), separate from a more thorough `/ready` endpoint for readiness (checking real dependencies like database connectivity).
- Instrument applications with structured logs, labeled metrics, and trace propagation from the start — retrofitting observability after an incident is far harder than building it in from day one.

---

## 15. Common Mistakes

- Making the liveness probe check downstream dependencies (e.g., database connectivity) — a temporary database outage then causes cascading, unnecessary container restarts across every replica, worsening the incident.
- Not configuring a startup probe for slow-starting applications, causing liveness-probe-triggered restart loops before the app ever finishes initializing.
- Relying solely on `kubectl logs` for production debugging — logs disappear when a Pod is deleted, making centralized log aggregation essential.
- Treating metrics, logs, and traces as interchangeable — each answers a different question, and skipping one (especially tracing in a microservice architecture) leaves major diagnostic blind spots.

---

## 16. Troubleshooting

| Symptom | Likely Cause | Debugging Commands | Fix |
|---|---|---|---|
| Pod restarts repeatedly (`CrashLoopBackOff`) | Failing liveness probe, or app crashing on its own | `kubectl describe pod`, `kubectl logs --previous` | Fix underlying app issue, or adjust probe strictness/thresholds |
| Pod running but never receives traffic | Failing readiness probe | `kubectl describe pod`, `kubectl get endpoints` | Fix readiness endpoint/dependency, or adjust probe config |
| Slow-starting app killed before finishing startup | No startup probe, liveness probe too aggressive | `kubectl describe pod` (check restart reason/timing) | Add a startup probe with adequate `failureThreshold`/`periodSeconds` |
| Metrics missing from Prometheus | App doesn't expose `/metrics`, or scrape config missing target | Check Prometheus targets page | Instrument app with a metrics endpoint; fix scrape configuration |

---

## 17. Comparison Tables

| Probe | Failure Action | Typical Check |
|---|---|---|
| Liveness | Restart the container | "Is the process alive/responsive?" |
| Readiness | Remove from Service traffic (no restart) | "Are dependencies OK, ready to serve?" |
| Startup | Delay liveness/readiness checks | "Has slow initialization finished?" |

| Pillar | Data Shape | Best For |
|---|---|---|
| Logs | Discrete, timestamped text events | Root-causing a specific incident |
| Metrics | Numeric time series | Trend/alerting, dashboards |
| Traces | Structured span trees per request | Pinpointing latency/failure across microservices |

---

## 18. Memory Tricks

- **"Hospital vital signs monitor"** — probes are continuous automated checks; logs are the chart; traces are a specific diagnostic test.
- **"Liveness restarts, readiness reroutes."**
- **"Logs = what happened, Metrics = how much/how often, Traces = where exactly."**

---

## 19. Interview Questions

**Easy:**
1. What is the difference between a liveness probe and a readiness probe?
   *Expected answer:* A liveness probe checks whether a container is still alive/functioning; if it fails repeatedly, the kubelet restarts the container. A readiness probe checks whether a container is ready to serve traffic; if it fails, the Pod is removed from the Service's Endpoints (stopping traffic) without being restarted.

**Medium:**
2. Why is Prometheus described as "pull-based," and what does an application need to do to be monitored by it?
   *Expected answer:* Prometheus is pull-based because it actively scrapes metrics from applications on a schedule, rather than applications pushing metrics to it. For an application to be monitored, it must expose an HTTP endpoint (conventionally `/metrics`) returning metrics in Prometheus's text-based exposition format; Prometheus is then configured with a scrape target pointing at that endpoint.

**Hard:**
3. A team configures their application's liveness probe to check `/healthz`, which internally verifies connectivity to the application's database. During a brief database outage, every replica of the application starts restarting repeatedly and the incident visibly worsens. Explain what went wrong and how the team should redesign their probes.
   *Expected answer:* By making the liveness probe depend on an external dependency (the database), a database outage — which the application itself can't fix by restarting — causes the liveness probe to fail across every replica simultaneously, triggering mass unnecessary restarts. Restarting the application does nothing to fix the database outage, so this only adds churn (and potential further load/instability) on top of an already-degraded system. The fix is to separate concerns: the **liveness** probe should only check that the application's own process is alive and responsive (e.g., a lightweight `/healthz` with no external dependency checks), while dependency checks (like database connectivity) belong on the **readiness** probe instead — a readiness failure correctly removes the Pod from traffic without restarting it, and it will automatically become ready again once the database recovers, with no restart storm.

---

## 20. KCNA Practice Questions

**Q1.** What are the three pillars of observability?
A. Logs, Metrics, Traces
B. Logs, Alerts, Dashboards
C. Metrics, Probes, Events
D. Traces, Events, Alerts

**Correct answer: A**
*Explanation:* Logs, Metrics, and Traces are the standard three pillars, each answering a different diagnostic question. The other options substitute unrelated or overlapping terms.

---

**Q2.** What happens when a Pod's readiness probe fails?
A. The container is immediately restarted
B. The Pod is removed from the Service's Endpoints, stopping traffic, without restarting the container
C. The Pod is deleted permanently
D. Nothing — readiness probes are informational only

**Correct answer: B**
*Explanation:* A failing readiness probe removes the Pod from traffic routing without restarting it — that's the liveness probe's job (A). C and D misdescribe actual behavior.

---

**Q3.** What is the purpose of a startup probe?
A. To permanently replace the liveness probe
B. To delay liveness and readiness probe checks until a slow-starting container finishes initializing
C. To check network connectivity between Pods
D. To scrape Prometheus metrics

**Correct answer: B**
*Explanation:* Startup probes hold off liveness/readiness checks during slow initialization, preventing premature restarts. A is false — it works alongside, not instead of, the liveness probe. C and D are unrelated.

---

**Q4.** In distributed tracing, what is a "span"?
A. A complete end-to-end trace across all services
B. A single unit of work within one service, part of a larger trace
C. A Prometheus metric type
D. A Kubernetes networking policy

**Correct answer: B**
*Explanation:* A span represents one unit of work in one service; a full trace is composed of many spans across the services a request traverses. A describes the trace itself, not a span. C and D are unrelated concepts.

---

**Q5.** Why must application logs typically be shipped to a centralized backend rather than relying on `kubectl logs` alone in production?
A. `kubectl logs` doesn't work for running Pods
B. Pods are ephemeral, and their logs are lost once the Pod is deleted
C. Kubernetes doesn't allow reading logs by default
D. `kubectl logs` only shows metrics, not logs

**Correct answer: B**
*Explanation:* Since Pods can be deleted/rescheduled at any time, relying only on `kubectl logs` risks losing history entirely — centralized log aggregation preserves logs beyond any individual Pod's lifecycle. A, C, and D misdescribe `kubectl logs`'s actual behavior and purpose.

---

**Q6.** Using the hospital analogy from this chapter, what does a "trace" correspond to?
A. The continuous bedside vital-signs monitor
B. The written patient chart
C. A specific diagnostic test following one issue through the body
D. The hospital's staff roster

**Correct answer: C**
*Explanation:* A trace follows one specific request end-to-end, like a targeted diagnostic test tracking down a specific symptom's cause. A maps to metrics (continuous monitoring), B maps to logs (a written history), and D is unrelated.

---

**Q7.** Which component actually executes liveness, readiness, and startup probes?
A. Prometheus
B. The kubelet
C. The kube-scheduler
D. Grafana

**Correct answer: B**
*Explanation:* The kubelet on each node periodically runs configured probes against containers on that node. Prometheus (A) scrapes metrics, the scheduler (C) places Pods, and Grafana (D) visualizes data — none execute probes.

---

**Q8.** What three mechanisms can a probe use to check container health?
A. HTTP GET, TCP socket, exec command
B. DNS lookup, ping, traceroute
C. gRPC, REST, SOAP
D. CPU check, memory check, disk check

**Correct answer: A**
*Explanation:* Probes support HTTP GET requests, opening a TCP socket, or running an exec command inside the container. The other option sets are unrelated to Kubernetes probe mechanisms.

---

**Q9.** In the YAML Deep Dive example, why is `failureThreshold: 30` combined with `periodSeconds: 10` on the startup probe significant?
A. It has no real effect on behavior
B. It allows up to 300 seconds for the container to finish starting before liveness/readiness probes begin
C. It restarts the container every 300 seconds
D. It sets the container's total lifetime to 300 seconds

**Correct answer: B**
*Explanation:* `30 × 10s = 300s` of allowed startup time before the startup probe gives up and liveness/readiness checks take over — protecting a slow-starting app from premature restarts. C and D misdescribe what the fields control.

---

**Q10.** Why does Prometheus require an application to expose a `/metrics` HTTP endpoint, rather than the application pushing metrics to Prometheus?
A. Because Prometheus uses a pull-based scraping model
B. Because Kubernetes forbids applications from making outbound connections
C. Because `/metrics` is a reserved Kubernetes API path
D. Because push-based metrics are not numeric

**Correct answer: A**
*Explanation:* Prometheus's architecture is pull-based — it actively scrapes exposed endpoints on a schedule rather than receiving pushed data. B, C, and D are false statements about Kubernetes and Prometheus.

---

**Q11.** According to the Architecture diagram, what are the two downstream destinations fed by Prometheus and the log-forwarding agent respectively?
A. Grafana and the centralized log backend
B. The kubelet and etcd
C. The API server and the scheduler
D. The tracing backend and the kubelet

**Correct answer: A**
*Explanation:* Prometheus feeds Grafana for dashboards, while the log-forwarding agent feeds a centralized log backend for searchable log storage. The other pairings do not reflect the diagram's flow.

---

**Q12.** Per the Troubleshooting table, what is the first thing to check when a Pod is running but never receives any traffic?
A. Whether the readiness probe is failing
B. Whether the liveness probe is failing
C. Whether Prometheus is scraping metrics
D. Whether the startup probe has a failureThreshold set

**Correct answer: A**
*Explanation:* A Pod that's running but excluded from traffic is the classic signature of a failing readiness probe, which removes it from Service Endpoints without restarting it. B causes restarts, not traffic exclusion; C and D are unrelated to this specific symptom.

---

**Q13.** Why is it a common mistake to treat metrics, logs, and traces as interchangeable?
A. They all cost the same amount of storage
B. Each answers a fundamentally different diagnostic question, so skipping one creates blind spots
C. Kubernetes only supports one of the three at a time
D. They must all be collected by the same tool

**Correct answer: B**
*Explanation:* Metrics show trends, logs show discrete events, and traces show per-request paths — omitting any one (especially tracing in microservices) leaves real diagnostic gaps. A, C, and D are false claims.

---

**Q14.** What does OpenTelemetry provide to the observability ecosystem?
A. A vendor-neutral standard/toolkit for generating traces, metrics, and logs
B. A replacement for the kubelet
C. A Kubernetes-native storage backend for etcd
D. A scheduling algorithm for Pod placement

**Correct answer: A**
*Explanation:* OpenTelemetry standardizes instrumentation for traces, metrics, and logs across vendors and tools. B, C, and D describe unrelated Kubernetes components.

---

**Q15.** In Lab 1, after triggering an unready state via `/set-unready`, what happens to the Pod?
A. It is deleted
B. Its IP disappears from the Service's Endpoints, but the Pod keeps running
C. It is restarted immediately
D. It is cordoned and drained

**Correct answer: B**
*Explanation:* This demonstrates the readiness-probe effect precisely: the Pod remains alive and running but is pulled out of traffic routing. A, C, and D describe different, unrelated operations.

---

**Q16.** Why should a liveness probe's `/healthz` endpoint avoid checking external dependencies like a database?
A. External checks are too fast to be useful
B. A shared dependency outage would cause mass simultaneous restarts across all replicas, worsening the incident
C. Kubernetes forbids liveness probes from making network calls
D. Database checks always return HTTP 500

**Correct answer: B**
*Explanation:* As the hard interview question explains, restarting doesn't fix an external outage — it just adds restart churn on top of an already-degraded system. Dependency checks belong on the readiness probe instead. A, C, and D are incorrect claims.

---

**Q17.** Which real-world example relies specifically on readiness probes rather than liveness probes?
A. Slow-starting Java application warm-up
B. Zero-downtime deployments ensuring traffic never reaches an unready new Pod version
C. SRE dashboards built on Prometheus metrics
D. Distributed tracing for latency debugging

**Correct answer: B**
*Explanation:* Zero-downtime rollouts depend on readiness probes gating when a new Pod version starts receiving traffic. A relates to startup probes, C to metrics, and D to tracing.

---

**Q18.** What is the role of a log-forwarding agent such as Fluent Bit?
A. It executes probes against containers
B. It ships container stdout/stderr logs off-node to a centralized backend
C. It scrapes Prometheus metrics endpoints
D. It schedules Pods onto nodes

**Correct answer: B**
*Explanation:* Since Pod logs are ephemeral and tied to the container's lifecycle, a log-forwarding agent captures and ships them off-node so they survive Pod deletion. A, C, and D describe other components (kubelet, Prometheus, scheduler).

---

**Q19.** What symptom in the Troubleshooting table points to "app doesn't expose `/metrics`, or scrape config missing target" as the likely cause?
A. Pod restarts repeatedly
B. Pod never receives traffic
C. Metrics missing from Prometheus
D. Slow-starting app killed before finishing startup

**Correct answer: C**
*Explanation:* Missing metrics in Prometheus points directly to either a missing `/metrics` endpoint on the app or a missing/incorrect scrape target configuration. The other symptoms map to different root causes in the same table (probe failures).

---

**Q20.** Per the memory tricks in this chapter, which phrase best distinguishes the effect of a failing liveness probe from a failing readiness probe?
A. "Logs = what happened, Metrics = how much/how often, Traces = where exactly"
B. "Liveness restarts, readiness reroutes"
C. "Hospital vital signs monitor"
D. "Pull, don't push"

**Correct answer: B**
*Explanation:* This mnemonic directly captures the key distinction tested repeatedly in this chapter: liveness failures cause restarts, readiness failures cause traffic rerouting (removal from Endpoints). A is about the three pillars, C is the observability analogy, and D is not one of this chapter's listed mnemonics.

---

## 21. Chapter Summary (One-Page Revision Sheet)

- Observability rests on three pillars: **Logs** (discrete events), **Metrics** (numeric trends), **Traces** (per-request path across services) — each answers a different question.
- Kubernetes's built-in health-check primitives are **probes**: liveness (restart on failure), readiness (remove from traffic on failure, no restart), and startup (delays the other two during slow initialization).
- **Prometheus** is pull-based, scraping `/metrics` endpoints on a schedule; **Grafana** commonly visualizes the resulting time series.
- Logs must be shipped off-Pod to a centralized backend since Pods are ephemeral; **distributed tracing** (e.g., via OpenTelemetry) is essential for diagnosing latency/failures across microservice call chains.
- Never let a liveness probe depend on external dependencies — that belongs on the readiness probe, to avoid restart storms during unrelated outages.

---

### Chapter Completion Checklist

1. **Topics covered:** Three pillars of observability, liveness/readiness/startup probes, Prometheus metrics scraping, centralized logging, distributed tracing.
2. **KCNA objectives completed:** Cloud Native Observability domain.
3. **Remaining objectives:** Service Mesh — sidecar proxies, mTLS, traffic management (Chapter 23).
4. **Suggested revision checklist:** Explain the three pillars from memory; explain the difference between liveness/readiness/startup probes; explain why liveness probes shouldn't check external dependencies.
5. **Suggested hands-on exercises:** Complete Lab 2 (trigger a liveness probe failure, observe the restart) — the clearest demonstration of probe-driven self-healing.
6. **Related chapters:** Previous: [21-Security](../21-Security/README.md). Next: [23-Service-Mesh](../23-Service-Mesh/README.md) — advanced traffic management, security, and observability via sidecar proxies.
