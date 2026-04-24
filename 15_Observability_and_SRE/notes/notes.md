#### 🔹 1. Improved Notes: Advanced Observability
*   **Cardinality:** High cardinality means you have many unique labels (e.g., tracking metrics by `UserID`). This can crash Prometheus. Always be careful with label names.
*   **Profiling:** Looking at the CPU and Memory usage of individual lines of code in production.
*   **Synthetic Monitoring:** Using scripts to "pretend" to be a user and test critical paths (like "Add to Cart" or "Login") every minute.

#### 🔹 2. Interview View (Q&A)
*   **Q:** What is the difference between Pull and Push monitoring?
*   **A:** Prometheus is **Pull** (it asks your app for metrics). CloudWatch is **Push** (your app sends metrics to AWS). Pull is generally better for service discovery, while Push is better for short-lived tasks (like Lambda).
*   **Q:** What is "MTTR" and "MTTD"?
*   **A:** MTTD (Mean Time to Detect) is how long it takes to find a bug. MTTR (Mean Time to Resolve) is how long it takes to fix it. SREs aim to minimize both.

***

#### 🔹 3. Architecture & Design: The Monitoring Stack
1.  **Exporters:** Small programs that collect metrics from databases or servers.
2.  **Prometheus:** The central server that pulls and stores metrics.
3.  **Grafana:** The "Front-end" that displays beautiful dashboards.
4.  **Alertmanager:** The "Pager" that sends a Slack message or an email when a metric goes over a threshold.

***

#### 🔹 4. Commands & Configs (PromQL)
```promql
# Calculate the request rate over the last 5 minutes
rate(http_requests_total[5m])

# Show only services where memory usage is > 80%
(node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100 < 20

# Find the 99th percentile latency
histogram_quantile(0.99, sum by (le) (rate(http_request_duration_seconds_bucket[5m])))
```

***

#### 🔹 5. Troubleshooting & Debugging
*   **Scenario:** You have a "High CPU" alert, but the app isn't crashing.
*   **Fix:** Check **Context Switching** and **I/O Wait**. If CPU usage is high because of "System" (not "User"), the kernel is likely struggling with too many threads or slow disk access.

***

#### 🔹 6. Production Best Practices
*   **Alert Fatigue:** Don't alert for everything. Only alert on things that require a human to wake up and take action.
*   **Post-Mortems:** After an incident, write a "Blameless Post-Mortem" to figure out *how* it happened and how to prevent it, rather than *who* to blame.
*   **Automated Remediation:** If a disk is 90% full, don't wake up an engineer—write a script that automatically deletes old log files.

***

#### 🔹 Cheat Sheet / Quick Revision
| **Concept** | **Purpose** | **DevOps Context** |
| :--- | :--- | :--- |
| `PromQL` | Query language | Filtering and calculating metrics in Prometheus. |
| `Exporter` | Data collector | `NodeExporter` for Linux, `Blackbox` for URLs. |
| `Toil` | Manual work | Repetitive tasks that should be automated away. |
| `Chaos Engineering` | Testing resilience | Breaking things on purpose to see if the system survives. |

***

This is Section 15: Observability & SRE. For a senior role, you should focus on **eBPF Profiling**, **Distributed Tracing**, and **Service Level Management**.
