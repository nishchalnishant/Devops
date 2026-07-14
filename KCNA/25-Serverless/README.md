# 25 — Serverless

## 1. Learning Objectives

By the end of this chapter you will be able to:

- Explain what "serverless" means and the problem it solves versus always-on Deployments.
- Explain scale-to-zero and event-driven scaling.
- Explain Knative's Serving and Eventing components at a high level.
- Compare FaaS platforms (Knative, OpenFaaS) to standard Kubernetes Deployments.
- Read a basic Knative Service manifest.

**KCNA objectives covered:** Cloud Native Architecture domain — Serverless.

---

## 2. Historical Background

Standard Kubernetes Deployments (Chapter 12) keep a fixed (or autoscaled-within-a-range) number of replicas running continuously, even during periods of zero traffic — appropriate for steady, predictable workloads, but wasteful for bursty, infrequent, or unpredictable ones (e.g., a webhook handler invoked a few times a day). Public clouds popularized "Functions as a Service" (FaaS) offerings (AWS Lambda, 2014) that ran code only in response to events and scaled down to nothing between invocations, charging only for actual execution time. The Kubernetes ecosystem responded with projects like **Knative** (2018, originally Google-led) to bring this same serverless, scale-to-zero, event-driven model onto Kubernetes itself, rather than requiring a proprietary cloud FaaS platform.

---

## 3. Motivation: Why Do We Need Serverless/Scale-to-Zero on Kubernetes?

**Analogy — The Post Office's On-Call Staff vs Always-Staffed Counter:**
A busy post office counter (a standard Deployment) needs staff on duty all day, every day, whether or not anyone walks in — costing money even during quiet hours. A **serverless** setup is more like an on-call courier service: nobody is paid to sit around during idle time, but the moment a package (an incoming request/event) arrives, a courier is summoned within moments, handles it, and then goes home again until the next package arrives. Kubernetes's serverless layer (Knative) brings this same "pay only when there's actual work" model to container workloads.

### 3.1 How Was This Solved Before Serverless on Kubernetes?

Workloads ran as standard Deployments with a minimum replica count of at least 1 (often more, for availability), consuming cluster resources continuously regardless of actual traffic — or teams used a proprietary cloud FaaS product (like AWS Lambda) entirely outside their Kubernetes cluster.

### 3.2 Why Was That Insufficient?

Always-on Deployments waste resources on bursty/infrequent workloads; proprietary cloud FaaS locks workloads into a specific cloud provider and can't be mixed uniformly with the rest of a team's Kubernetes-native workloads and tooling.

### 3.3 How Kubernetes/Knative Solves It

**Knative** adds scale-to-zero and request-driven autoscaling directly on top of standard Kubernetes, automatically scaling a workload's replicas down to zero when there's no traffic and back up (including from zero) the moment a request arrives — giving Lambda-style serverless economics without leaving the Kubernetes ecosystem, and integrating with event sources via **Knative Eventing**.

---

## 4. Core Concepts

### 4.1 Serverless vs Standard Deployment

| Aspect | Standard Deployment (Chapter 12) | Serverless (Knative) |
|---|---|---|
| Minimum replicas | Typically ≥1, always running | Can scale to **zero** when idle |
| Scaling trigger | CPU/memory (HPA) | Incoming request/event concurrency |
| Cold start | None (already running) | Possible, when scaling up from zero |
| Best for | Steady, predictable traffic | Bursty, infrequent, unpredictable traffic |

### 4.2 Knative's Two Main Components

| Component | Role |
|---|---|
| Knative Serving | Manages request-driven workloads: scale-to-zero, automatic scaling, revision management, traffic splitting |
| Knative Eventing | Manages event-driven workloads: routes events from sources (e.g., message queues) to services via a standardized eventing model |

### 4.3 FaaS (Functions as a Service)

**Definition:** FaaS is a model where developers deploy individual functions (not whole applications), and the platform handles all provisioning, scaling (including to zero), and invocation — Knative and OpenFaaS are Kubernetes-native FaaS-style platforms; AWS Lambda/Azure Functions/Google Cloud Functions are proprietary cloud equivalents.

---

## 5. Internal Working

```
1. Knative Service is deployed, initially with zero replicas running
        ↓
2. A request arrives at the Knative-managed ingress
        ↓
3. Knative's autoscaler (KPA - Knative Pod Autoscaler) detects the
   request and scales the workload up from zero (a "cold start")
        ↓
4. Request is routed to the newly-started Pod and served
        ↓
5. If no further requests arrive within a configurable idle window,
   Knative scales the workload back down to zero, freeing resources
        ↓
6. (Eventing path) An event source (e.g., a Kafka topic, a cron
   schedule) emits an event, which Knative Eventing routes to a
   subscribed Service, which may itself scale from zero to handle it
```

---

## 6. Architecture

```
                ┌─────────────┐
                │  Event Source    │
                │ (Kafka, Cron,    │
                │  PubSub, etc.)   │
                └──────┬──────┘
                          │ emits event
                          ▼
                ┌─────────────┐
                │ Knative Eventing │
                │  (Broker/Trigger)│
                └──────┬──────┘
                          │ routes to
                          ▼
┌─────────────┐   scales    ┌─────────────┐
│ Knative Serving  │ ◄────────── │  Knative Service │
│  (Autoscaler,      │             │  (0 → N replicas)│
│   Revisions)        │             └─────────────┘
└─────────────┘
```

---

## 7. Component Breakdown

| Component | Role |
|---|---|
| Knative Service | The top-level resource defining a serverless workload (image, autoscaling config) |
| Revision | An immutable snapshot of a Knative Service at a point in time, enabling traffic splitting/rollback |
| Knative Pod Autoscaler (KPA) | Scales replicas based on request concurrency, including down to zero |
| Broker / Trigger | Knative Eventing objects routing events from sources to subscribed Services |

---

## 8. Important Terminology

| Term | Meaning |
|---|---|
| Serverless | Model where infrastructure scaling (including to zero) is fully automatic and invisible to the developer |
| Scale-to-zero | Scaling a workload's replica count down to zero during idle periods |
| Cold start | The latency incurred when scaling a workload up from zero to serve a new request |
| FaaS | Functions as a Service — deploying individual functions rather than whole applications |
| Knative Serving | Knative's component managing request-driven autoscaling and revisions |
| Knative Eventing | Knative's component managing event-driven routing from sources to services |

---

## 9. YAML Deep Dive

```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: hello-serverless
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "0"
        autoscaling.knative.dev/maxScale: "10"
    spec:
      containers:
        - image: gcr.io/example/hello:v1
          ports:
            - containerPort: 8080
```

`minScale: "0"` explicitly allows scale-to-zero (the serverless default); `maxScale: "10"` caps how far the workload can scale up under load, protecting shared cluster resources.

---

## 10. kubectl Commands

| Command | Purpose | Example |
|---|---|---|
| `kubectl apply -f service.yaml` | Deploy a Knative Service | `kubectl apply -f hello-serverless.yaml` |
| `kubectl get ksvc` | List Knative Services | `kubectl get ksvc` |
| `kubectl get revisions` | List revisions for rollback/traffic-split | `kubectl get revisions` |
| `kn service describe <name>` | Inspect a Knative Service (Knative CLI) | `kn service describe hello-serverless` |
| `kubectl get pods -w` | Watch Pods scale from/to zero | `kubectl get pods -w` |

---

## 11. Hands-on Examples

**Lab 1 — Deploy and observe scale-to-zero after idle period:**
```bash
kubectl apply -f hello-serverless.yaml
kubectl get pods -w
# Pod starts, then after the idle window (default ~30s-60s with no
# traffic) the Pod count drops back to zero
```

**Lab 2 — Trigger a cold start and measure latency:**
```bash
time curl http://hello-serverless.default.example.com
# First request after scale-to-zero incurs cold-start latency;
# subsequent requests (while a Pod is running) are much faster
```

**Lab 3 — Roll out a new revision with traffic split:**
```bash
kubectl apply -f hello-serverless-v2.yaml
kn service update hello-serverless --traffic v1=80,v2=20
# 80% of traffic goes to the old revision, 20% to the new one
```

---

## 12. Internal Flow

See Section 5 — the defining serverless behavior is the **round trip through zero**: a workload with zero replicas is not "down," it's simply idle, and the platform transparently brings it back the moment demand reappears — a fundamentally different operating model from a standard Deployment's steady-state replica count.

---

## 13. Real-world Examples

1. **Webhook receivers** (e.g., handling occasional GitHub webhook events) are ideal for scale-to-zero — no need to keep a Pod running 24/7 for something invoked a few times a day.
2. **Image-processing pipelines** triggered by file uploads use Knative Eventing to react to storage events, scaling processing Pods up only when files actually arrive.
3. **Batch/cron-triggered workloads** use event sources to invoke a Knative Service on a schedule, rather than running a Deployment continuously.
4. **Cost-sensitive dev/staging environments** use scale-to-zero to avoid paying for idle compute outside of active testing hours.
5. **Canary rollouts of new function versions** use Knative's revision-based traffic splitting, similar in spirit to the mesh-based traffic splitting covered in Chapter 23.

---

## 14. Best Practices

- Only apply scale-to-zero to workloads that can **tolerate cold-start latency** — latency-sensitive, high-traffic services are usually better served by a standard Deployment or a `minScale` ≥ 1.
- Set a reasonable **`maxScale`** to protect shared cluster capacity from an unexpected traffic spike.
- Use **revisions and traffic splitting** for safe, gradual rollouts of new function/service versions, rather than replacing a Service outright.
- Combine **Knative Eventing** with existing event sources (message queues, cron, cloud storage events) rather than building custom polling logic in application code.

---

## 15. Common Mistakes

- Applying scale-to-zero to a latency-critical, user-facing service and being surprised by cold-start delays under real traffic.
- Not setting `maxScale`, allowing an unexpected traffic spike to consume far more cluster resources than intended.
- Assuming Knative fully replaces the need for standard Deployments — steady, predictable workloads are often still better served by a plain Deployment with HPA (Chapter 12).
- Ignoring revision cleanup — old, unused revisions can accumulate over time and should be pruned periodically.

---

## 16. Troubleshooting

| Symptom | Likely Cause | Debugging Commands | Fix |
|---|---|---|---|
| First request after idle is very slow | Cold start from scale-to-zero | `kubectl get pods -w` during the request | Expected behavior; set `minScale: 1` if unacceptable for this workload |
| Service never scales down | `minScale` set ≥ 1, or continuous background traffic (e.g., health checks) keeping it "active" | `kn service describe <name>` | Confirm `minScale` value; check for unexpected traffic sources |
| Traffic split not behaving as configured | Incorrect revision tags/percentages in traffic config | `kn service describe <name>` | Correct the traffic split configuration |
| Event source not triggering the Service | Broker/Trigger misconfigured, or event filter doesn't match | Check Trigger's event filter, event source logs | Correct the Trigger's filter criteria or event source configuration |

---

## 17. Comparison Tables

| Aspect | Standard Deployment | Knative Service |
|---|---|---|
| Idle resource usage | Non-zero (at least `minReplicas`) | Can be zero |
| Scaling signal | CPU/memory (HPA) | Request concurrency |
| Best fit | Steady, predictable load | Bursty, infrequent, event-driven load |
| Rollback mechanism | ReplicaSet history (Chapter 12) | Revision-based traffic splitting |

| Platform | Style |
|---|---|
| Knative | Kubernetes-native, request- and event-driven, open-source |
| OpenFaaS | Kubernetes-native FaaS, function-focused |
| AWS Lambda / Azure Functions | Proprietary cloud FaaS, outside Kubernetes |

---

## 18. Memory Tricks

- **"On-call courier, not an always-staffed counter"** — serverless workloads show up only when there's actual work.
- **"Scale to zero isn't down, it's asleep."**
- **"Cold start = the wake-up cost of going from zero."**

---

## 19. Interview Questions

**Easy:**
1. What does "scale-to-zero" mean in the context of serverless Kubernetes workloads?
   *Expected answer:* Scale-to-zero means a workload's replica count is automatically reduced to zero during periods with no incoming traffic/events, freeing cluster resources; the platform automatically scales it back up the moment a new request or event arrives.

**Medium:**
2. What is a "cold start," and why does it matter when deciding whether a workload should use scale-to-zero?
   *Expected answer:* A cold start is the extra latency incurred when a workload scales up from zero replicas to serve a new request — the container has to be scheduled and started before it can respond. This matters because latency-sensitive workloads may find this delay unacceptable, so scale-to-zero (and its cold-start trade-off) is best suited to bursty or infrequent workloads that can tolerate occasional startup delay, rather than services requiring consistently low latency.

**Hard:**
3. A team deploys a customer-facing API as a Knative Service with default settings (`minScale: 0`) to save on idle compute costs. After launch, they receive complaints about intermittent slow responses, especially first thing each morning and after lunch breaks. Explain the likely cause and how to fix it without fully abandoning Knative's cost benefits.
   *Expected answer:* With `minScale: 0`, the Service scales down to zero replicas during quiet periods (overnight, during lunch), so the first request after each idle period triggers a cold start, causing the reported slow responses. Rather than abandoning Knative entirely, the team can set `minScale: 1` (keeping at least one replica warm at all times, eliminating cold starts, at the cost of some idle compute) or use a moderate `minScale` combined with a longer idle-scale-down window tuned to their actual traffic pattern — balancing cost savings against acceptable latency, rather than taking the all-or-nothing extremes of always-on versus always-scale-to-zero.

---

## 20. KCNA Practice Questions

**Q1.** What is the primary benefit of scale-to-zero in a serverless Kubernetes workload?
A. It guarantees zero latency for all requests
B. It eliminates resource consumption during idle periods with no traffic/events
C. It removes the need for container images
D. It disables autoscaling entirely

**Correct answer: B**
*Explanation:* Scale-to-zero frees cluster resources when a workload has no traffic, only scaling up again once demand returns. A is false (cold starts add latency, not remove it), and C/D are unrelated behaviors.

---

**Q2.** What does Knative Eventing primarily provide?
A. A mechanism for routing events from sources to subscribed services
B. A replacement for Kubernetes Deployments
C. A service mesh sidecar proxy
D. A CI/CD pipeline engine

**Correct answer: A**
*Explanation:* Knative Eventing routes events (from sources like message queues or schedulers) to subscribed Services via Brokers/Triggers. B, C, and D describe unrelated components (Deployments are Chapter 12, sidecar proxies are Chapter 23, CI/CD is Chapters 06-08 of the general curriculum).

---

**Q3.** What is a "cold start" in serverless computing?
A. The time it takes to build a container image
B. The latency incurred when scaling a workload up from zero replicas to serve a new request
C. The time it takes etcd to elect a new leader
D. The delay before a NetworkPolicy takes effect

**Correct answer: B**
*Explanation:* A cold start is the startup latency when going from zero to serving, a direct consequence of scale-to-zero. A, C, and D describe unrelated processes.

---

**Q4.** Which type of workload is generally the best fit for Knative's scale-to-zero model?
A. A latency-critical, constantly-trafficked production API
B. A bursty, infrequently-invoked webhook handler
C. A stateful database requiring constant availability
D. A DaemonSet running on every node

**Correct answer: B**
*Explanation:* Bursty, infrequent workloads benefit most from scale-to-zero's cost savings, tolerating occasional cold-start latency. A and C are poor fits due to latency/availability requirements, and D (DaemonSets, Chapter 13) isn't a serverless/Knative concept at all.

---

**Q5.** How does Knative's revision-based traffic splitting compare conceptually to what was covered for service meshes in Chapter 23?
A. They are unrelated; Knative has no traffic-splitting capability
B. Both provide a mechanism to gradually shift traffic between versions for safer rollouts
C. Knative's traffic splitting requires manual DNS changes
D. Service meshes cannot perform traffic splitting

**Correct answer: B**
*Explanation:* Both Knative's revision-based traffic percentages and a service mesh's weighted routing achieve the same conceptual goal — gradual, controlled traffic shifting between versions to reduce rollout risk. A, C, and D misdescribe either technology.

---

**Q6.** In the Knative Service YAML annotation `autoscaling.knative.dev/minScale: "0"`, what does setting this value to `"0"` explicitly allow?
A. The Service to be deleted automatically
B. The workload to scale down to zero replicas during idle periods
C. The container image to be rebuilt on every request
D. The Service to bypass Kubernetes RBAC

**Correct answer: B**
*Explanation:* `minScale: "0"` explicitly permits the workload to scale to zero replicas, which is the serverless default behavior. A, C, and D describe unrelated, non-existent behaviors of this annotation.

---

**Q7.** What is the purpose of the `maxScale` annotation on a Knative Service?
A. To cap how far the workload can scale up, protecting shared cluster resources from an unexpected traffic spike
B. To set the minimum number of always-running replicas
C. To define the container's memory limit
D. To specify the number of revisions retained

**Correct answer: A**
*Explanation:* `maxScale` caps the upper bound of autoscaling, guarding shared cluster capacity. B describes `minScale`, and C/D describe unrelated concepts (resource limits are plain Kubernetes fields; revision retention is a separate concern).

---

**Q8.** Which Knative component is responsible for detecting incoming requests and scaling a workload up from zero replicas?
A. kube-scheduler
B. Knative Pod Autoscaler (KPA)
C. CoreDNS
D. etcd

**Correct answer: B**
*Explanation:* The KPA monitors request concurrency and drives scale-up (including from zero) and scale-down decisions. A, C, and D are unrelated Kubernetes control-plane components (Chapters 18-20).

---

**Q9.** What is a Knative "Revision"?
A. A mutable, live-editable copy of a running Service
B. An immutable snapshot of a Knative Service at a point in time, enabling traffic splitting and rollback
C. A backup of etcd's data store
D. A ReplicaSet's rollout history entry

**Correct answer: B**
*Explanation:* Revisions are immutable snapshots that make traffic splitting and rollback possible. A contradicts the immutability property, C is unrelated to Knative, and D confuses Revisions with a standard Deployment's ReplicaSet history (Chapter 12).

---

**Q10.** In Knative Eventing, what is the role of a "Broker" and "Trigger" together?
A. They compile application source code into container images
B. They route events from a source to one or more subscribed Services, based on a filter
C. They enforce NetworkPolicies between Pods
D. They manage persistent volume provisioning

**Correct answer: B**
*Explanation:* A Broker receives events and a Trigger subscribes a Service to a filtered subset of those events, forming Knative Eventing's routing mechanism. A, C, and D describe unrelated subsystems (CI/CD, NetworkPolicy in Chapter 21, storage in Chapter 15).

---

**Q11.** Why might a Knative Service fail to scale down to zero even though no real user traffic is arriving?
A. Because `maxScale` is set too high
B. Because continuous background traffic, such as health checks, is keeping it "active"
C. Because the container image is too large
D. Because the cluster has too many nodes

**Correct answer: B**
*Explanation:* Unexpected traffic sources (health checks, monitoring probes) can keep request concurrency above zero, preventing scale-down. A, C, and D don't affect whether the Service is considered "idle."

---

**Q12.** According to this chapter's best practices, which type of workload should generally avoid scale-to-zero?
A. A latency-sensitive, high-traffic production service
B. An infrequent webhook receiver
C. A batch job triggered by a cron event source
D. A cost-sensitive staging environment used only during business hours

**Correct answer: A**
*Explanation:* Latency-sensitive, high-traffic services are poor fits for scale-to-zero due to cold-start delays; they're usually better served by a standard Deployment or `minScale` ≥ 1. B, C, and D are the workload types scale-to-zero was designed for.

---

**Q13.** What is the key difference in scaling *trigger* between a standard Kubernetes Deployment with an HPA and a Knative Service?
A. There is no difference; both scale on identical signals
B. HPA scales primarily on CPU/memory metrics, while Knative scales primarily on incoming request concurrency
C. Knative cannot autoscale at all
D. HPA can scale to zero, but Knative cannot

**Correct answer: B**
*Explanation:* HPA (Chapter 12) reacts to resource utilization metrics, while Knative's KPA reacts to request concurrency, including scaling from/to zero. A, C, and D misstate these mechanisms.

---

**Q14.** A team notices old, unused Knative Revisions accumulating in their cluster over time. According to this chapter's common mistakes, what should they do?
A. Nothing — Revisions never need to be cleaned up
B. Periodically prune old, unused revisions
C. Disable revision creation entirely
D. Convert all Revisions into DaemonSets

**Correct answer: B**
*Explanation:* This chapter explicitly calls out ignoring revision cleanup as a common mistake — old revisions should be pruned periodically. A contradicts the stated best practice, and C/D are not meaningful actions in this context.

---

**Q15.** Which of the following is a proprietary cloud FaaS offering, as opposed to a Kubernetes-native FaaS-style platform?
A. Knative
B. OpenFaaS
C. AWS Lambda
D. Kubernetes Deployment

**Correct answer: C**
*Explanation:* AWS Lambda (along with Azure Functions and Google Cloud Functions) is a proprietary cloud FaaS product outside Kubernetes. A and B are Kubernetes-native FaaS-style platforms, and D is not a FaaS concept at all.

---

**Q16.** Using the `kn` CLI, which command inspects a Knative Service's configuration and status?
A. `kn service describe <name>`
B. `kubectl drain <name>`
C. `kubectl taint nodes <name>`
D. `kn service delete <name>`

**Correct answer: A**
*Explanation:* `kn service describe <name>` inspects a Knative Service, including its revisions and traffic split. B and C are node-management commands (Chapter 20), and D deletes rather than inspects the Service.

---

**Q17.** In Lab 3 of this chapter, the command `kn service update hello-serverless --traffic v1=80,v2=20` is run. What does this achieve?
A. It deletes revision v1 entirely
B. It splits traffic 80% to revision v1 and 20% to revision v2
C. It scales v2 to zero replicas
D. It merges v1 and v2 into a single revision

**Correct answer: B**
*Explanation:* The `--traffic` flag assigns percentage weights across named revisions, here sending 80% of traffic to v1 and 20% to v2 for a gradual rollout. A, C, and D misdescribe the command's effect.

---

**Q18.** Which analogy does this chapter use to describe the difference between a standard Deployment and a serverless (Knative) workload?
A. A vault door versus an open window
B. An always-staffed post office counter versus an on-call courier service
C. A highway versus a footpath
D. A library versus a bookstore

**Correct answer: B**
*Explanation:* The chapter's analogy contrasts an always-staffed counter (standard Deployment, paying for idle time) with an on-call courier summoned only when needed (serverless, pay only for actual work). A, C, and D are not analogies used in this chapter.

---

**Q19.** What problem does proprietary cloud FaaS (e.g., AWS Lambda) create for teams that Knative aims to solve?
A. It cannot scale to zero
B. It locks workloads into a specific cloud provider, preventing uniform integration with the rest of a Kubernetes-native toolchain
C. It requires manual server provisioning
D. It cannot process events

**Correct answer: B**
*Explanation:* As covered in Section 3.2, proprietary cloud FaaS ties workloads to a specific vendor and can't mix uniformly with Kubernetes-native tooling — the exact gap Knative fills. A and D describe capabilities cloud FaaS does have, and C is the opposite of how FaaS works.

---

**Q20.** A Knative Service handling image-processing triggered by file uploads (as in this chapter's real-world examples) would most likely rely on which Knative component to react to storage events?
A. Knative Eventing (via a Broker/Trigger subscribed to the storage event source)
B. kube-proxy
C. A StatefulSet's volumeClaimTemplate
D. A NetworkPolicy egress rule

**Correct answer: A**
*Explanation:* Knative Eventing routes events from sources like storage systems to subscribed Services, exactly the pattern described for image-processing pipelines in Section 13. B, C, and D are unrelated Kubernetes primitives.

---

## 21. Chapter Summary (One-Page Revision Sheet)

- **Serverless** on Kubernetes (via **Knative**) automatically scales workloads down to **zero** during idle periods and back up on demand, unlike a standard Deployment's steady-state replica count.
- **Knative Serving** handles request-driven autoscaling and **revisions** (immutable snapshots enabling traffic splitting/rollback); **Knative Eventing** routes events from sources to subscribed Services via Brokers/Triggers.
- The trade-off for scale-to-zero savings is **cold-start latency** — the delay incurred scaling up from zero — making it best suited to bursty, latency-tolerant workloads.
- `minScale`/`maxScale` annotations tune the balance between cost savings (scale-to-zero) and responsiveness (always-warm replicas).
- Knative is complementary to, not a replacement for, standard Deployments — steady, predictable workloads are often still better served by a plain Deployment with HPA.

---

### Chapter Completion Checklist

1. **Topics covered:** Serverless/scale-to-zero model, cold starts, Knative Serving and Eventing, FaaS platforms, revision-based traffic splitting.
2. **KCNA objectives completed:** Cloud Native Architecture — Serverless.
3. **Remaining objectives:** CNCF Landscape — project maturity levels, landscape categories (Chapter 26).
4. **Suggested revision checklist:** Explain scale-to-zero and cold starts from memory; explain Knative Serving vs Eventing; explain when scale-to-zero is (and isn't) appropriate.
5. **Suggested hands-on exercises:** Complete Lab 1 (deploy a Knative Service and observe it scale to zero after idling) — the clearest demonstration of serverless behavior.
6. **Related chapters:** Previous: [24-GitOps](../24-GitOps/README.md). Next: [26-CNCF-Landscape](../26-CNCF-Landscape/README.md) — the CNCF project landscape and maturity levels.
