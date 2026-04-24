# Observability & Site Reliability Engineering (SRE)

Monitoring tells you *if* a system is failing; Observability tells you *why* it's failing. SRE is the bridge between software engineering and operations, focusing on the stability, reliability, and performance of large-scale systems.

#### 1. The Three Pillars of Observability
1.  **Metrics:** Numerical data over time (e.g., CPU usage, Request Count). Great for dashboards and alerts. (Tool: **Prometheus**).
2.  **Logs:** Text records of events (e.g., "User logged in", "Database connection failed"). Essential for debugging specific errors. (Tool: **ELK Stack / Loki**).
3.  **Traces:** The "Journey" of a request across multiple microservices. Shows where latency is occurring. (Tool: **Jaeger / Tempo**).

#### 2. The Four Golden Signals
Google's SRE handbook identifies these as the most critical signals to monitor:
*   **Latency:** The time it takes to service a request.
*   **Traffic:** How much demand is being placed on the system (e.g., HTTP requests per second).
*   **Errors:** The rate of requests that fail (explicitly or implicitly).
*   **Saturation:** How "full" your service is (e.g., memory usage or disk I/O).

#### 3. SLI, SLO, and SLA
*   **SLI (Service Level Indicator):** A specific metric you measure (e.g., "99% of requests take < 200ms").
*   **SLO (Service Level Objective):** The target goal for that metric (e.g., "We want our SLI to be true 99.9% of the time").
*   **SLA (Service Level Agreement):** A legal contract with a customer. If you miss the SLO, you pay a penalty (e.g., "If we are down for more than 40 minutes a month, we give you a refund").

#### 4. Error Budgets
An Error Budget is the "freedom to fail." If your SLO is 99.9% uptime, you have a 0.1% error budget (about 43 minutes a month).
*   **If the budget is full:** You can push new features and take risks.
*   **If the budget is exhausted:** You stop all feature work and focus 100% on stability and reliability.

***

