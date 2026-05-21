---
description: Distributed tracing internals, OpenTelemetry, Jaeger, trace analysis, and production observability for senior engineers.
---

# Observability — Distributed Tracing & OpenTelemetry

```
Distributed Tracing & OpenTelemetry
├── Why Distributed Tracing
│   └── Single request path across 5+ services → find where latency occurs
├── OpenTelemetry Architecture
│   ├── App → OTel SDK (auto-instrument or manual spans)
│   ├── OTel Collector (receive → process/sample → export)
│   └── Backends: Jaeger, Tempo, Zipkin (via OTLP)
├── Trace Anatomy
│   ├── Trace ID (global unique, shared across all services)
│   ├── Span (start_time, duration, attributes, events, status)
│   └── Parent-child hierarchy (child spans form the trace tree)
├── Python Instrumentation
│   ├── Auto: opentelemetry-instrument (Flask, Django, requests)
│   └── Manual: tracer.start_as_current_span("checkout.payment")
├── OTel Collector Configuration
│   ├── Receivers: otlp (gRPC + HTTP)
│   ├── Processors: batch, tail_sampling, filter
│   └── Exporters: otlp (Tempo), jaeger, prometheus
├── Sampling Strategies
│   ├── Head sampling (probabilistic, decided at request start)
│   ├── Tail sampling (decided after full trace collected — keeps errors)
│   └── Rate-limiting (max N traces per second regardless of traffic)
├── Tail Sampling Config (OTel Collector)
│   ├── keep-errors (status_code: ERROR → always keep)
│   ├── high-latency (latency > 2000ms → always keep)
│   └── sample-rest (probabilistic 10%)
└── Logic & Trickiness
    ├── Context propagation: must pass W3C TraceContext headers manually in custom clients
    ├── Sampling: tail keeps errors; head may lose them
    ├── Auto-instrumentation first, manual spans for business logic only
    ├── Trace storage: Jaeger in-memory → Tempo with S3 backend for scale
    ├── Correlation: inject TraceID into log messages (link logs ↔ traces)
    └── Span attributes: high-cardinality OK (doesn't affect Prometheus)
```

## First Principles

You can't fix what you can't see. Three pillars: logs (what happened), metrics (how much/how fast), traces (where time was spent across services). SLOs define acceptable failure rates — alerts fire when burn rate exceeds budget. On-call needs runbooks to act on alerts.

## Why Distributed Tracing

Logs tell you *what* happened on one service. Metrics tell you *how many* times. Traces tell you *why it was slow* across the entire request path.

```
User request: GET /checkout

Without tracing:
  api-gateway:  200 OK in 3.1s   ← Which service was slow?

With tracing:
  api-gateway:     50ms
  ├── auth-service:    30ms
  ├── cart-service:   150ms   ← Slow!
  │   └── postgres:  140ms   ← DB query is the bottleneck
  └── payment-service: 80ms
```

***

## OpenTelemetry — The Universal Standard

OpenTelemetry (OTel) is the vendor-neutral SDK + specification for emitting telemetry (traces, metrics, logs).

```
Application (instrumented with OTel SDK)
        │
        │ Spans, Metrics, Logs (OTLP protocol)
        ▼
OpenTelemetry Collector
        │
        ├── Processor (batch, filter, transform)
        │
        ├── Exporter → Jaeger (traces)
        ├── Exporter → Prometheus (metrics)
        └── Exporter → Loki / Elasticsearch (logs)
```

***

## eBPF-Based Distributed Tracing (Zero-Code Instrumentation)

While the OpenTelemetry SDK provides granular control, it requires code modifications, dependency upgrades, rebuilds, and language-specific runtimes. **eBPF-based distributed tracing** changes this by operating at the OS kernel layer to auto-instrument applications with zero code changes.

```
                    eBPF-Based Distributed Tracing Architecture
┌────────────────────────────────────────────────────────────────────────┐
│                          User Application Space                        │
│                                                                        │
│  [ HTTP / gRPC Client ]                  [ OpenSSL / BoringSSL ]       │
│           │                                         │                  │
│           │ (sys_enter_write / sys_enter_read)      │ (SSL_write/read) │
└───────────┼─────────────────────────────────────────┼──────────────────┘
            │                                         │
┌───────────┼─────────────────────────────────────────┼──────────────────┐
│  Kernel   ▼                                         ▼                  │
│  ┌─────────────────┐                       ┌─────────────────┐         │
│  │   kprobe / TC   │                       │     uprobe      │         │
│  │ (Raw Net Packets)│                       │ (Unencrypted)   │         │
│  └────────┬────────┘                       └────────┬────────┘         │
│           │                                         │                  │
│           └────────────────► eBPF Ring Buffer ◄─────┘                  │
│                                     │                                  │
└─────────────────────────────────────┼──────────────────────────────────┘
                                      ▼
                        ┌───────────────────────────┐
                        │   OTel Beyla / Collector  │ ──► Tempo / Jaeger
                        └───────────────────────────┘
```

### 1. Core Mechanics of eBPF Tracing
eBPF agents automatically discover running processes and intercept application lifecycles using three primary kernel hook types:

* **kprobes (Kernel Probes):** Intercept standard Linux system calls (e.g. `sys_enter_connect`, `sys_enter_write`, `sys_enter_read`, `sys_enter_sendto`). Whenever an application transmits data over a socket, the eBPF program parses the network buffer headers directly.
* **uprobes (Userspace Probes):** Dynamically attach to compiled userspace binaries or shared libraries (e.g., standard HTTP libraries, runtime schedulers). For example, OTel Beyla attaches uprobes to Go's runtime HTTP execution points to track request start and end times natively.
* **Tracepoints:** Static hooks compiled directly into the kernel or glibc. They are highly stable and survive kernel upgrades, offering low-latency entry points for common syscalls.

---

### 2. Solving the HTTPS Encryption Barrier
A major challenge of network packet capture (e.g., using sidecars or standard sniffing) is TLS encryption. When traffic is encrypted, sniffers only see raw ciphertext.
* **The uprobe Solution:** eBPF bypasses this by placing dynamic **uprobes on shared TLS libraries** (like OpenSSL `libssl.so` or BoringSSL).
* **Hook points:** Hooks are attached to the entry and exit points of functions like `SSL_write()` and `SSL_read()`. 
* **Mechanism:** Because these uprobes execute *before* the library encrypts the payload (for writes) or *after* decryption (for reads), the eBPF program reads the **raw, unencrypted HTTP/gRPC headers** directly from the socket arguments in kernel memory with minimal context overhead.

---

### 3. Context Propagation & Correlation
Context propagation (passing Trace IDs across services in W3C `traceparent` headers) is the lifeblood of tracing. eBPF handles this via two patterns:
1. **Dynamic Header Injection (eBPF-TC):** For unencrypted or early-stage HTTP requests, eBPF programs attached to the Traffic Control (tc) queue parse TCP streams on-the-fly and physically **inject the HTTP `traceparent` header** into outbound TCP packets, modifying packet lengths and recalculating IP/TCP checksums in the kernel.
2. **Deterministic Correlation (Kernel State tracking):** When headers cannot be modified safely, the eBPF agent maps sockets to active parent-child executions. By correlating TCP connection handshakes (`SYN`, `SYN-ACK`), source/destination ports, and exact network socket descriptors in shared BPF maps, the agent reconstructs the dependency tree across services without changing packet bytes.

---

### 4. Runtime SDKs vs. eBPF Auto-Tracing

| Metric | OpenTelemetry SDK (Standard) | eBPF Auto-Tracing (Beyla/Pixie) |
| :--- | :--- | :--- |
| **Code Modification** | Required (add packages, init SDK) | **Zero (completely transparent)** |
| **Deployment Model** | Inside application runtime | **DaemonSet / Host Agent** |
| **Language Support** | Separate SDK for Python, Java, Go, etc. | **Language independent (kernel-level)** |
| **TLS/HTTPS Traffic** | Supported natively | **Supported via OpenSSL uprobes** |
| **Telemetry Depth** | High (Business logic, custom spans) | Medium (Network boundaries, HTTP/gRPC) |
| **Performance Overhead** | Moderate (App memory/CPU, garbage collection) | **Extremely Low (kernel JIT compilation)** |
| **Context Propagation** | Robust, fully handles all W3C headers | Challenging (complex for multi-protocol meshes) |

---

### 5. OTel Beyla eBPF Auto-Instrumentation Configuration
Below is a typical production configuration for **OpenTelemetry Beyla**, an eBPF-based auto-instrumentation tool:

```yaml
# beyla-config.yaml
# Beyla runs as a privileged container or host daemon to access kernel hooks.
open_telemetry_exporter:
  interval: 5s
  address: "otel-collector:4317"  # Send spans directly to OTel Collector

# Discover and instrument applications based on port or process name
discovery:
  services:
    - name: ecom-checkout-service
      open_ports: "8080"            # Intercept any HTTP/gRPC process bound to 8080
      executable_name: "checkout"   # Fallback process matching
      namespace: "production"

# Network hook optimization levels
ebpf:
  uprobes_path: "/usr/lib/ssl"      # Custom path for TLS interception
  features:
    - network                       # Capture raw L4 metric bytes
    - application                   # Capture L7 HTTP/gRPC metadata
  wakeup_len: 100                  # Process trace queues in batches of 100 to save CPU
```

***

## Trace Anatomy

```
Trace ID: abc123
│
└── Span: api-gateway (Root Span)
    │   Duration: 3100ms
    │   TraceID: abc123
    │   SpanID: span001
    │   Attributes: {http.method: GET, http.url: /checkout}
    │
    ├── Span: auth-service
    │       Duration: 30ms
    │       ParentSpanID: span001
    │
    ├── Span: cart-service
    │       Duration: 150ms
    │       ParentSpanID: span001
    │       Attributes: {db.system: postgresql}
    │       Events: [{name: "slow query detected", timestamp: ...}]
    │
    │   └── Span: postgresql.query
    │           Duration: 140ms
    │           ParentSpanID: cart-span
    │           Attributes: {db.statement: "SELECT * FROM items WHERE..."}
    │
    └── Span: payment-service
            Duration: 80ms
```

***

## Instrumenting a Service (Python Example)

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# Setup (once at app startup)
provider = TracerProvider()
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="otel-collector:4317"))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

tracer = trace.get_tracer("cart-service")

# In your code
def get_cart_items(user_id: str):
    with tracer.start_as_current_span("get_cart_items") as span:
        span.set_attribute("user.id", user_id)
        
        try:
            items = db.query("SELECT * FROM cart WHERE user_id = ?", user_id)
            span.set_attribute("cart.item_count", len(items))
            return items
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.StatusCode.ERROR)
            raise
```

***

## OpenTelemetry Collector Configuration

```yaml
# otel-collector-config.yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318
  
  # Scrape Prometheus metrics too
  prometheus:
    config:
      scrape_configs:
        - job_name: 'my-app'
          static_configs:
            - targets: ['app:8080']

processors:
  batch:
    timeout: 5s
    send_batch_size: 1024
  
  # Add resource attributes to all telemetry
  resource:
    attributes:
      - action: upsert
        key: deployment.environment
        value: production
  
  # Drop health check spans to reduce noise
  filter:
    spans:
      exclude:
        match_type: strict
        attributes:
          - key: http.url
            value: /healthz

exporters:
  jaeger:
    endpoint: jaeger:14250
    tls:
      insecure: true
  
  prometheus:
    endpoint: "0.0.0.0:8889"
  
  loki:
    endpoint: http://loki:3100/loki/api/v1/push

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch, resource, filter]
      exporters: [jaeger]
    metrics:
      receivers: [otlp, prometheus]
      processors: [batch]
      exporters: [prometheus]
```

***

## Sampling Strategies

Collecting 100% of traces at high traffic is expensive. Sampling reduces volume while preserving important traces.

| Strategy | How It Works | Best For |
|:---|:---|:---|
| **Head Sampling (Probabilistic)** | Decision made at trace start (e.g., sample 10%) | Low-cost, simple |
| **Tail Sampling** | Decision made AFTER trace completes (keep errors, slow traces) | High-value traces, requires Collector |
| **Rate Limiting** | Keep first N traces per second | Preventing Collector overload |

**Tail Sampling Config (in OTel Collector):**
```yaml
processors:
  tail_sampling:
    decision_wait: 10s       # Wait for full trace before deciding
    num_traces: 100000       # Max traces in memory
    policies:
      - name: keep-errors
        type: status_code
        status_code: {status_codes: [ERROR]}
      
      - name: keep-slow-traces
        type: latency
        latency: {threshold_ms: 2000}
      
      - name: sample-rest
        type: probabilistic
        probabilistic: {sampling_percentage: 10}
```

***

## Logic & Trickiness Table

| Concept | Junior Thinking | Senior Thinking |
|:---|:---|:---|
| **Context propagation** | "Tracing just works" | Trace context must be passed in HTTP headers (W3C TraceContext); auto-instrumented libraries do this, but custom HTTP clients need manual setup |
| **Sampling** | 100% or 0% | Tail sampling: keep errors + slow traces, sample the rest |
| **Instrumentation** | Manual spans everywhere | Use auto-instrumentation agents; add manual spans only for business logic |
| **Trace storage** | Jaeger in-memory | Jaeger with S3/GCS backend (Tempo/Thanos for scale) |
| **Correlation** | Traces separate from logs | Inject TraceID into log messages; link from log line to trace in Grafana |
| **Cardinality in spans** | Add `user_id` to span attributes | Span attributes don't affect Prometheus cardinality; safe to add high-cardinality attrs |

## System Design Perspective

**Log Aggregation Integration with Tracing:** The highest value from distributed tracing comes when trace IDs appear in log lines. Inject the active `trace_id` into all log messages as a structured field (OTel SDK provides the current span context). In Grafana, configure a data link from a Tempo trace viewer to Loki that auto-queries `{app="$service"} | json | trace_id = "$traceId"` — this gives one-click navigation from a slow trace to the exact log lines from every service in that trace.

**Sampling Strategy Documentation:** At scale, different services use different sampling strategies (high-traffic services use 1% head sampling; payment service uses 100% tail sampling). Document the sampling contract per service in the service's README. This prevents on-call confusion: "I can't find this trace in Jaeger" might mean it was sampled out, not that the request failed silently.

**Alerting on Trace-Derived Metrics:** OTel Collector's Span Metrics connector generates RED metrics (rate, errors, duration) from trace spans without any application code changes. These metrics feed directly into Prometheus, enabling SLO alerting for services that only emit traces but not explicit Prometheus metrics. This bridges the observability gap for third-party or legacy services.
