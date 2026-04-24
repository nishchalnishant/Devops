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

