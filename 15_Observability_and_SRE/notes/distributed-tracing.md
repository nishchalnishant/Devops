---
description: Distributed tracing internals, OpenTelemetry, Jaeger, trace analysis, and production observability for senior engineers.
---

# Observability — Distributed Tracing & OpenTelemetry

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
