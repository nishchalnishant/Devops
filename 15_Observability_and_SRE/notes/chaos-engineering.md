# Chaos Engineering & Resilience Testing

Chaos Engineering is the practice of deliberately injecting faults into a system to discover weaknesses before they manifest as real incidents. It transforms reliability from a reactive to a proactive discipline.

***

## 1. The Chaos Engineering Mindset

```
Traditional testing: "Does it work when everything is correct?"
Chaos Engineering: "Does it still work when things go wrong?"

Chaos Engineering = Experimentation, not random destruction

Steps:
  1. Define Steady State (what does "healthy" look like?)
  2. Form a Hypothesis ("if X fails, we expect Y behavior")
  3. Inject the failure in a controlled way
  4. Observe the system
  5. Draw conclusions and file action items
```

***

## 2. The Chaos Maturity Model

| Level | Scope | Frequency | Automation |
|:---|:---|:---|:---|
| **0 — Game Days** | Manual, controlled environment | Quarterly | None |
| **1 — Automated Staging** | Scheduled experiments in staging | Weekly | Semi-automated |
| **2 — Automated Production** | Controlled blast radius in prod | Daily | Fully automated |
| **3 — Continuous Chaos** | Chaos runs as a CI gate | Every deploy | Integrated |

Most organizations operate at Level 0-1. Netflix, Amazon, and Google operate at Level 2-3.

***

## 3. Steady State Hypothesis

Before injecting chaos, define what "healthy" looks like with measurable SLIs:

```yaml
# Example steady state for a payment service
steady_state:
  - metric: http_requests_success_rate
    threshold: "> 99.5%"
    measurement_window: "1m"
  - metric: http_p99_latency_ms
    threshold: "< 500"
  - metric: kafka_consumer_lag
    threshold: "< 1000"
  - metric: error_rate_5xx
    threshold: "< 0.5%"

# Chaos experiment: kill 1 of 3 payment service pods
hypothesis: "Removing 1 pod should not break steady state for more than 30 seconds"
```

***

## 4. Chaos Experiments — Taxonomy

### Infrastructure Level
| Experiment | Tests | Tool |
|:---|:---|:---|
| Kill a pod randomly | Kubernetes self-healing, PDB effectiveness | Chaos Mesh, Chaos Monkey |
| Drain a Kubernetes node | Cluster autoscaler, pod scheduling | `kubectl drain` + automation |
| Cordon a node | Eviction, rescheduling | `kubectl cordon` |
| Exhaust node CPU | HPA responsiveness, noisy neighbor | Chaos Mesh CPU stressor |
| Fill node disk | Log rotation, disk pressure handling | Chaos Mesh IO stressor |
| Kill the cluster autoscaler | Manual scaling, operator awareness | Pod deletion |

### Network Level
| Experiment | Tests | Tool |
|:---|:---|:---|
| Inject 200ms network latency | Timeout config, retry storms, P99 impact | Chaos Mesh NetworkChaos |
| Inject 5% packet loss | Retry behavior, connection pooling | tc netem (Linux) |
| Partition service A from service B | Circuit breaker, fallback response | NetworkChaos |
| Block DNS resolution | DNS caching, fallback resolution | Chaos Mesh DNSChaos |
| Throttle bandwidth to 1Mbps | Large payload handling, timeouts | NetworkChaos |

### Application Level
| Experiment | Tests | Tool |
|:---|:---|:---|
| Return HTTP 503 from a dependency | Retry policy, circuit breaker | Envoy fault injection, Istio |
| Inject 1-second delay in responses | Cascading timeout, upstream propagation | Istio VirtualService fault |
| Kill the database primary | Failover time, reconnection logic | Cloud provider failover |
| Exhaust connection pool | Queuing, backpressure behavior | Artillery load + real DB limit |
| Delete a Kubernetes Secret | Error handling for missing config | `kubectl delete secret` |

### State Level
| Experiment | Tests | Tool |
|:---|:---|:---|
| Corrupt a cache entry in Redis | Cache invalidation, fallback to DB | Redis CLI |
| Simulate stale data from a feature store | Model serving degradation handling | Custom script |
| Kill Kafka broker | Consumer rebalancing, producer retry | Kafka broker stop |

***

## 5. Chaos Mesh — Kubernetes-Native Chaos

Chaos Mesh runs in-cluster and provides CRDs for all experiment types:

### Pod Chaos
```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: PodChaos
metadata:
  name: kill-payment-pod
spec:
  action: pod-kill
  mode: one               # Kill one random pod from the selector
  selector:
    namespaces: [payment]
    labelSelectors:
      app: payment-api
  scheduler:
    cron: "@every 10m"    # Run every 10 minutes
```

### Network Chaos — Inject Latency
```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: NetworkChaos
metadata:
  name: payment-latency
spec:
  action: delay
  mode: all
  selector:
    namespaces: [payment]
    labelSelectors:
      app: payment-api
  delay:
    latency: "200ms"
    correlation: "25"       # 25% correlation with previous packet
    jitter: "50ms"
  direction: to             # Affect outgoing traffic from payment pods
  target:
    selector:
      namespaces: [database]
```

### HTTP Chaos — Inject Errors
```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: HTTPChaos
metadata:
  name: payment-upstream-error
spec:
  mode: all
  target: Response
  port: 8080
  abort: true               # Drop responses (simulate timeout)
  # OR
  delay: "500ms"            # Add latency to responses
  # OR
  replace:
    code: 503               # Return 503 instead of real response
  selector:
    namespaces: [payment]
```

***

## 6. GameDay Planning Template

```
GameDay: [Service Name] Resilience Assessment
Date: [Date]
Duration: 2 hours
Scope: [Environment] only
Observers: SRE, On-Call Engineer, Service Owner

PRE-GAME (30 min before):
  □ Verify current steady state is healthy
  □ Confirm monitoring dashboards are working
  □ Have rollback procedures documented
  □ Notify stakeholders (if production scope)
  □ Confirm on-call is aware and available

EXPERIMENTS:
  1. [10:00] Kill random pod — observe self-healing
  2. [10:15] Inject 200ms latency to downstream — observe circuit breaker
  3. [10:35] Kill all pods of a non-critical dependency — observe fallback
  4. [11:00] Node drain — observe pod rescheduling

POST-GAME:
  □ Review steady state metrics during each experiment
  □ Document findings: what held, what failed
  □ Create action items with owners and deadlines
  □ Schedule follow-up game day after fixes are applied
```

***

## 7. Guardrails — Production Chaos Safety

```yaml
# Guardrails configuration (Chaos Mesh Workflow)
spec:
  templates:
    - name: abort-on-slo-breach
      type: Task
      task:
        # Query Prometheus: if error rate > 1%, abort the experiment
        container:
          image: prom/prometheus:v2.48.0
          command:
          - sh
          - -c
          - |
            RATE=$(curl -s 'http://prometheus:9090/api/v1/query?query=rate(http_errors_total[1m])' \
              | jq .data.result[0].value[1])
            if [ $(echo "$RATE > 0.01" | bc) -eq 1 ]; then
              echo "SLO breach detected — aborting experiment"
              exit 1
            fi
```

**Key guardrails to implement:**
1. **SLO gate:** If error budget burn rate exceeds threshold, auto-abort
2. **Blast radius cap:** Never affect more than 10% of pods simultaneously in production
3. **Business hours only:** Schedule automated chaos during off-peak (after 10pm, before 8am) OR only with on-call present
4. **Rollback hook:** Every experiment has a documented 30-second rollback procedure
5. **Progressive scope:** Run in staging → canary → production (not production first)

***

## 8. Common Findings from Chaos Experiments

| Finding | Root Cause | Fix |
|:---|:---|:---|
| Request failures spike for 90s after pod kill | Connection pool not detecting closed connections | Add health check probes; enable TCP keepalive |
| Circuit breaker trips when injecting 500ms latency | Circuit breaker threshold too aggressive (200ms) | Increase CB threshold to match P99 SLO (500ms) |
| Database failover takes 45 seconds | Application retry window too short; reconnect backoff too fast | Implement exponential backoff; increase connection retry timeout |
| Latency injection causes retry storm | Every microservice retries independently → 10x amplification | Add jitter to retries; implement retry budgets |
| DNS injection causes full service failure | Application caches DNS for 0 seconds (TTL ignored) | Implement DNS caching with 30-60s TTL |
| Node drain causes pod scheduling delay | Cluster Autoscaler slow to provision new nodes | Enable Karpenter; use node disruption budgets |
