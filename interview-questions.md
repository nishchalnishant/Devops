# Interview questions

Let’s begin. You are in the final round of an interview for a Senior SRE role. I am the Lead SRE, and our team is currently dealing with a critical production issue. We need your expertise to help us stabilize the platform.

***

#### 🚨 The Scenario: "The Flash Sale Meltdown"

The Environment: Our company runs a high-traffic e-commerce platform on Kubernetes (EKS) across multiple Availability Zones. We use Terraform for IaC and Prometheus/Grafana for observability.

The Situation:

Ten minutes ago, we launched a massive 50% off "Flash Sale." Our traffic jumped from 10k requests per second (RPS) to 150k RPS.

The Symptoms:

1. Users: Reporting intermittent 504 Gateway Timeouts and slow page loads.
2. Grafana: Shows a massive spike in p99 latency (from 200ms to 8s) and a 15% error rate on the `checkout-service`.
3. Infrastructure: Our Horizontal Pod Autoscaler (HPA) has successfully scaled the `checkout-service` pods from 10 to 100 replicas.
4. Database: The RDS Postgres instance shows CPU is at 40%—so the DB seems healthy.

***

#### 🎙️ My First Question to You:

"Our HPA has already scaled the pods to the maximum limit of 100, and the database isn't breaking a sweat, yet we are still seeing 504 timeouts.

Walk me through your investigation. What are the first three things you are going to check using `kubectl`, and what specific networking or OS-level bottlenecks are you looking for?"

***

#### 💡 How to respond:

* Tell me exactly which commands you would run.
* Tell me what metrics you are looking for in the logs or dashboards.
* Hypothesize why we are seeing 504s if the DB is fine and pods are scaled up.

I'm listening. How do we save this sale?



In a high-pressure interview, the "I don't know" is fine, but as your AI thought partner, let’s walk through the Senior SRE logic.

The fact that the Database is at 40% CPU and Pods are scaled to 100 is a distraction. If the app is slow (8s latency) and timing out (504), the "pipe" is clogged somewhere else.

Here are the three things a Senior SRE would check immediately:

***

#### 1. Check for CPU Throttling (The "Invisible" Killer)

Command: `kubectl top pods` and looking at Prometheus for Container CPU Throttling metrics.

* The Logic: Even if CPU _usage_ looks okay, if you set your Kubernetes CPU Limits too low, the Linux Kernel will "throttle" the process to stay under that limit.
* The Result: The app doesn't crash, but it slows down to a crawl, causing the 504 timeouts at the gateway. You might need to increase the `limits` in your Deployment YAML.

#### 2. Check for Connection Pool Exhaustion

Command: `kubectl logs -l app=checkout-service | grep -i "pool"`

* The Logic: Your database CPU is low because the requests aren't even reaching it! Most apps use a "Connection Pool" (like Hikari or SQLAlchemy). If the pool is set to 20 connections and you have thousands of users, the 21st user has to wait in a queue.
* The Result: Eventually, the queue times out, the user gets a 504, and the DB stays idle because it’s not receiving the traffic.

#### 3. Check for "Conntrack" Table Saturation (The Networking Deep-Dive)

Command: `kubectl exec <pod_name> -- cat /proc/sys/net/netfilter/nf_conntrack_count`

* The Logic: In Linux, the kernel tracks every single network connection in a table called `conntrack`. If you have a massive spike in traffic (10k to 150k RPS), this table can fill up.
* The Result: When the table is full, the OS starts dropping packets. The Load Balancer tries to talk to the pod, the packet is dropped, the LB waits, and eventually returns a 504.

***

#### 🛠️ The "Senior" Solution: How to Fix It

If I were the SRE in this scenario, here is how I would respond to the Lead:

> "Since our Pods are at max scale and the DB is idle, we aren't hitting a capacity limit; we are hitting a concurrency or networking bottleneck.
>
> 1. I'm going to check for CPU Throttling; we might be 'limit-clamping' our own performance.
> 2. I'll check the Application Logs for connection pool timeouts.
> 3. I'll check the Node-level dmesg to see if we're hitting `nf_conntrack` limits.
>
> To stabilize immediately, I'll update the Terraform code to increase the HPA Max Replicas beyond 100 (if the nodes can take it) and increase the DB Connection Pool size in our ConfigMap."

***

#### 🎯 Final Interview Question for You:

"You've increased the HPA limit and fixed the connection pool. The 504s are gone, but now the RDS Database CPU has jumped to 98% and the site is slow again. You can't scale the DB any larger without a 5-minute maintenance window.

What SRE 'Emergency' tactic do you use to save the database without restarting it or losing data?"

(Hint: Think about Section 9 - Traffic Management)

In this scenario, you are facing a "Death Spiral." If the database hits 100% CPU and stays there, it will eventually stop responding to health checks, the cloud provider might mark it as "unhealthy," and you could face a total outage.

Since you can't scale up (vertical scaling) without a maintenance window, you must use Traffic Engineering to protect the database.

***

#### 🛡️ The "Emergency" SRE Answer: Load Shedding & Circuit Breaking

When a system is overloaded, the goal is to save some requests rather than failing all of them.

**1. Rate Limiting / Load Shedding (The Blunt Force Fix)**

You immediately apply a rate limit at the Ingress (Nginx/Istio) level.

* The Logic: If the DB can only handle 100k RPS and you are sending 150k, you intentionally drop 50k requests with a 429 Too Many Requests error.
* The Result: It’s better for 30% of users to see a "Please wait" page than for 100% of users to see a "504 Gateway Timeout" because the whole system crashed.

**2. Circuit Breaking / Feature Degradation (The Surgical Fix)**

You identify "expensive" but non-essential database queries and turn them off using Feature Flags or Circuit Breakers.

* The Example: During a flash sale, the "Check-out" flow is critical. However, the "Recommended for You" or "Product Reviews" sections are secondary.
* The Action: You disable the "Recommendations" service. This stops thousands of complex `JOIN` queries hitting the DB every second, freeing up CPU for the actual "Buy Now" transactions.

**3. Read Replicas (The Quick Win)**

If you have Read Replicas configured but the app is still sending all traffic to the "Primary" (Writer) instance, you can do a hot-config change to move all "GET" requests (browsing products) to the Read Replicas.

* The Result: This offloads the majority of the read pressure, leaving the Primary instance available only for "POST/PUT" (actual purchases).

***

#### 📝 How to say it in the Interview:

> "In an emergency where the DB is at 98% CPU and scaling isn't an option, I would implement Load Shedding. I’d configure the Ingress controller to return a 429 (Too Many Requests) for a percentage of traffic to prevent a total database crash.
>
> Simultaneously, I would trigger a Circuit Breaker to disable non-critical features—like 'Search' or 'Product Recommendations'—to reduce the query load on the RDS instance. This keeps the 'Golden Path' (the Checkout flow) alive until the traffic spike subsides."

***

#### 🏆 Mock Interview Debrief

You have now navigated a full-scale production incident!

1. Section 5/6 (Linux/K8s): You looked for CPU throttling and kernel limits.
2. Section 3 (Networking): You identified the 504 Gateway Timeout source.
3. Section 9 (Monitoring): You used metrics (p99 latency vs CPU) to find the bottleneck.
4. Traffic Management: You used Rate Limiting to protect the core business.

You are officially ready for the "hot seat." Would you like to do a final summary of your strengths/weaknesses based on these sections, or is there a specific technology (like Terraform or Kubernetes) you'd like to do one last deep-dive on?
