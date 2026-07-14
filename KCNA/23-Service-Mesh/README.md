# 23 — Service Mesh

## 1. Learning Objectives

By the end of this chapter you will be able to:

- Explain what problem a service mesh solves and why it emerged.
- Explain the sidecar proxy pattern and the data plane / control plane split.
- Explain mTLS, traffic splitting (canary), retries, and circuit breaking as mesh features.
- Compare Istio and Linkerd at a high level.
- Read a basic mesh traffic-splitting configuration.

**KCNA objectives covered:** Cloud Native Architecture domain — Service Mesh.

---

## 2. Historical Background

As microservice architectures grew, every service team ended up reimplementing the same cross-cutting networking concerns — retries, timeouts, load balancing, encryption, authentication between services, and observability — usually as libraries baked into each application, often in different languages, with inconsistent behavior. Netflix's early "fat client" libraries (like Hystrix) were one attempt at standardizing this per-language, but it still required every team to adopt and update the same library. The **service mesh** pattern emerged (led by Linkerd and Istio around 2016-2017) to move all of this logic out of application code entirely and into the infrastructure layer, via a network proxy deployed alongside every service instance.

---

## 3. Motivation: Why Do We Need a Service Mesh on Top of Kubernetes Networking?

**Analogy — The Building's Security and Concierge Staff:**
Imagine an apartment building where, without a mesh, every single resident (application) would need to personally install their own door locks, personally verify every visitor's ID, and personally track who came and went. A **service mesh** is like the building hiring a dedicated staff — security guards and concierges stationed at every door (a **sidecar proxy** next to every Pod) — who handle ID verification (mTLS), visitor logging (observability), and even redirect visitors to a different unit temporarily during renovations (traffic splitting), all without residents having to do any of that themselves.

### 3.1 How Was This Solved Before Service Meshes?

Cross-cutting concerns (retries, encryption, observability, load balancing) were implemented as per-application libraries, requiring every team to adopt, configure, and keep the same library updated across every language in use.

### 3.2 Why Was That Insufficient?

Library-based approaches don't work across polyglot microservice fleets (different languages need different library implementations), are hard to upgrade consistently across many teams, and mix business logic with networking logic inside the application itself.

### 3.3 How Kubernetes/Service Meshes Solve It

A service mesh injects a lightweight **sidecar proxy** container (e.g., Envoy) into every Pod, transparently intercepting all inbound/outbound traffic; a centralized **control plane** configures every sidecar's behavior uniformly, regardless of what language the application itself is written in — moving retries, mTLS, traffic shaping, and telemetry entirely out of application code.

---

## 4. Core Concepts

### 4.1 Data Plane vs Control Plane

| Layer | Role | Example |
|---|---|---|
| Data Plane | The sidecar proxies actually handling every request (intercept, encrypt, route, retry) | Envoy proxy in Istio; linkerd2-proxy in Linkerd |
| Control Plane | Centralized component configuring and managing all sidecars | Istiod (Istio); Linkerd's control plane |

### 4.2 Sidecar Proxy Pattern

**Definition:** A **sidecar proxy** is a separate container injected into the same Pod as the application container, transparently intercepting all network traffic to/from the application — the application is unaware the proxy exists.

### 4.3 Key Mesh Features

| Feature | What It Does |
|---|---|
| mTLS (mutual TLS) | Automatically encrypts and authenticates traffic between services, without app code changes |
| Traffic splitting / canary | Routes a percentage of traffic to a new version for gradual rollout |
| Retries & timeouts | Automatically retries failed requests per configurable policy |
| Circuit breaking | Stops sending traffic to an unhealthy service instance to prevent cascading failure |
| Observability | Automatic metrics/traces for every request, without app instrumentation |

---

## 5. Internal Working

```
1. Mesh control plane injects a sidecar proxy container into every
   Pod annotated/labeled for mesh membership
        ↓
2. All inbound/outbound traffic for the app container is transparently
   redirected through its local sidecar proxy (via iptables rules)
        ↓
3. Outbound request: sidecar proxy applies mTLS, load-balancing,
   retry, and timeout policy before forwarding to the destination
   Pod's sidecar
        ↓
4. Destination sidecar proxy receives the request, verifies mTLS
   identity, forwards to the local app container
        ↓
5. Every request's metrics/traces are emitted by the sidecars
   automatically, without any application code changes
```

---

## 6. Architecture

```
        ┌──────────────────────────┐
        │        Control Plane         │
        │   (Istiod / Linkerd control)  │
        └─────────────┬─────────────┘
              configures sidecars
     ┌───────────────┼───────────────┐
     ▼                              ▼
┌─────────┐                  ┌─────────┐
│   Pod A     │                  │   Pod B     │
│┌─────────┐│                  │┌─────────┐│
││  App        ││ ←intercept→ ││ Sidecar    ││
││ container   ││                  ││ Proxy      ││
│└─────────┘│                  │└─────────┘│
│┌─────────┐│    mTLS traffic    │             │
││ Sidecar    ││ ◄──────────────► │             │
││ Proxy      ││                  │             │
│└─────────┘│                  │             │
└─────────┘                  └─────────┘
```

---

## 7. Component Breakdown

| Component | Role |
|---|---|
| Sidecar proxy | Data-plane component handling every request in/out of a Pod |
| Control plane (Istiod, Linkerd control) | Configures and manages all sidecar proxies cluster-wide |
| VirtualService / TrafficSplit | Custom resource defining traffic routing rules (Istio / SMI-style) |
| PeerAuthentication / mTLS policy | Custom resource defining mesh-wide or namespace-wide mTLS requirements |

---

## 8. Important Terminology

| Term | Meaning |
|---|---|
| Service Mesh | Infrastructure layer handling service-to-service communication via sidecar proxies |
| Sidecar Proxy | Per-Pod proxy container transparently intercepting all network traffic |
| Data Plane | The collective sidecar proxies actually forwarding traffic |
| Control Plane | Centralized component configuring the data plane |
| mTLS | Mutual TLS — both sides of a connection authenticate each other |
| Canary Deployment | Gradually shifting traffic to a new version to limit blast radius |
| Circuit Breaking | Temporarily stopping traffic to an unhealthy destination to prevent cascading failure |

---

## 9. YAML Deep Dive

```yaml
# Istio VirtualService: split traffic 90/10 between two versions
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: reviews-route
spec:
  hosts:
    - reviews
  http:
    - route:
        - destination:
            host: reviews
            subset: v1
          weight: 90
        - destination:
            host: reviews
            subset: v2
          weight: 10
---
# Istio PeerAuthentication: enforce strict mTLS in a namespace
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: production
spec:
  mtls:
    mode: STRICT
```

The `VirtualService` sends 10% of traffic to `v2` for canary testing; the `PeerAuthentication` resource forces every Pod in the `production` namespace to only accept mTLS-encrypted connections.

---

## 10. kubectl Commands

| Command | Purpose | Example |
|---|---|---|
| `kubectl label namespace <ns> istio-injection=enabled` | Enable automatic sidecar injection for a namespace | `kubectl label namespace production istio-injection=enabled` |
| `kubectl get pods -o jsonpath` | Confirm sidecar container is present | `kubectl get pod myapp -o jsonpath='{.spec.containers[*].name}'` |
| `kubectl get virtualservice` | List Istio traffic-routing rules | `kubectl get virtualservice -n production` |
| `kubectl get peerauthentication` | List mTLS policies | `kubectl get peerauthentication -n production` |
| `istioctl proxy-status` | Check sidecar proxy sync status (Istio CLI) | `istioctl proxy-status` |

---

## 11. Hands-on Examples

**Lab 1 — Enable sidecar injection and confirm two containers per Pod:**
```bash
kubectl label namespace production istio-injection=enabled
kubectl rollout restart deployment myapp -n production
kubectl get pod -n production -o jsonpath='{.items[0].spec.containers[*].name}'
# Output includes both "myapp" and "istio-proxy"
```

**Lab 2 — Apply a canary traffic split and observe distribution:**
```bash
kubectl apply -f reviews-virtualservice.yaml
for i in $(seq 1 20); do curl -s reviews.production/version; done
# Roughly 18 requests hit v1, 2 hit v2
```

**Lab 3 — Enforce strict mTLS and confirm plaintext traffic is rejected:**
```bash
kubectl apply -f strict-mtls-peerauthentication.yaml
kubectl exec plain-client -- curl -v reviews.production
# Connection rejected/refused for non-mesh (non-mTLS) clients
```

---

## 12. Internal Flow

See Section 5 — the defining characteristic of a service mesh is that all of this (encryption, retries, routing, telemetry) happens **transparently at the proxy layer**, entirely outside application code, configured centrally by the control plane rather than per-application.

---

## 13. Real-World Examples

1. **Canary releases** use weighted traffic splitting to send a small percentage of production traffic to a new version before a full rollout.
2. **Zero-trust security** postures use mesh-wide strict mTLS to guarantee every service-to-service connection is encrypted and mutually authenticated, regardless of application-level TLS support.
3. **Multi-language microservice fleets** (Go, Java, Python services in one cluster) get uniform retry/timeout/observability behavior without each language needing its own networking library.
4. **Fault-injection testing** (chaos engineering) uses mesh capabilities to deliberately inject latency or errors into specific service calls to test resilience.
5. **Circuit breaking** in a mesh automatically stops routing traffic to an overloaded backend instance, preventing a single slow dependency from cascading into a fleet-wide outage.

---

## 14. Best Practices

- Start with a **subset** of namespaces/services when adopting a mesh — a mesh-wide rollout on day one adds risk and operational complexity before the team has experience with it.
- Use **STRICT mTLS mode** only after confirming all clients within the mesh are also mesh members — otherwise legitimate non-mesh traffic will be rejected.
- Monitor the **resource overhead** sidecars add to every Pod (extra CPU/memory per Pod) — meshes are not free.
- Use traffic splitting for **gradual canary rollouts** rather than instantly cutting all traffic to a new version.

---

## 15. Common Mistakes

- Adopting a full mesh cluster-wide before understanding its operational overhead (extra debugging complexity, sidecar resource cost, added latency per hop).
- Enabling strict mTLS before all relevant clients are mesh members, causing unexpected connection failures.
- Assuming a service mesh replaces the need for Kubernetes NetworkPolicies (Chapter 18) — they solve different problems (mesh: application-layer traffic management/mTLS; NetworkPolicy: network-layer segmentation) and are often used together.
- Forgetting that sidecar injection typically requires a Pod restart to take effect on already-running workloads.

---

## 16. Troubleshooting

| Symptom | Likely Cause | Debugging Commands | Fix |
|---|---|---|---|
| Traffic still hitting old version despite VirtualService update | Config not yet propagated, or subset labels don't match Pod labels | `istioctl proxy-status`, `kubectl get pods --show-labels` | Confirm subset labels match; wait for/verify config sync |
| Connections rejected after enabling strict mTLS | Client is not a mesh member (no sidecar) | `kubectl get pod -o jsonpath` for sidecar presence | Enable sidecar injection for the client namespace, or use PERMISSIVE mode during migration |
| No sidecar container present after labeling namespace | Existing Pods weren't restarted after injection was enabled | `kubectl get pod -o jsonpath` | `kubectl rollout restart deployment <name>` |
| High latency after mesh adoption | Extra proxy hop overhead, or misconfigured retries/timeouts | Check mesh dashboards (Kiali/Grafana) | Tune retry/timeout policy; verify proxy resource limits are adequate |

---

## 17. Comparison Tables

| Aspect | Istio | Linkerd |
|---|---|---|
| Proxy | Envoy (general-purpose, feature-rich) | linkerd2-proxy (lightweight, Rust-based) |
| Complexity | Higher — more features, steeper learning curve | Lower — simpler, opinionated defaults |
| Best for | Complex traffic management needs, large feature surface | Simplicity, lower resource overhead |

| Concern | Service Mesh | NetworkPolicy (Chapter 18) |
|---|---|---|
| Layer | Application (L7) | Network (L3/L4) |
| Solves | mTLS, retries, traffic splitting, observability | IP/port-based traffic segmentation |
| Relationship | Complementary — often used together | Complementary — often used together |

---

## 18. Memory Tricks

- **"Building security/concierge staff"** — sidecars handle security and routing so residents (apps) don't have to.
- **"Data plane does the work, control plane gives the orders."**
- **"Mesh talks app-layer (L7), NetworkPolicy talks network-layer (L3/L4) — different jobs, same team."**

---

## 19. Interview Questions

**Easy:**
1. What is a sidecar proxy in the context of a service mesh?
   *Expected answer:* A sidecar proxy is a separate proxy container injected into the same Pod as an application container, transparently intercepting all inbound/outbound network traffic for that application without requiring any changes to the application's code.

**Medium:**
2. What is the difference between the data plane and control plane in a service mesh?
   *Expected answer:* The data plane consists of all the sidecar proxies actually handling traffic (encryption, routing, retries) for every service instance. The control plane is the centralized component (e.g., Istiod) that configures and manages the behavior of every sidecar proxy across the mesh, without itself handling any application traffic directly.

**Hard:**
3. A team enables `STRICT` mTLS mode across their entire mesh-enabled namespace and immediately sees connection failures from a legacy service that has not yet been onboarded onto the mesh. Explain why this happened and how the team could roll out strict mTLS more safely.
   *Expected answer:* STRICT mTLS mode requires every connection to be mutually authenticated via TLS between mesh sidecars; a legacy service without a sidecar cannot participate in mTLS handshakes, so its plaintext connections are rejected outright. A safer rollout uses **PERMISSIVE mode** first, which accepts both plaintext and mTLS traffic simultaneously, allowing legacy/non-mesh services to keep working while mesh adoption is gradually completed; only once all relevant clients are confirmed to be mesh members should the team switch to STRICT mode to fully enforce mTLS.

---

## 20. KCNA Practice Questions

**Q1.** What is the primary purpose of a service mesh's sidecar proxy?
A. To store persistent application data
B. To transparently intercept and manage all network traffic in/out of a Pod
C. To schedule Pods onto nodes
D. To provide DNS resolution for the cluster

**Correct answer: B**
*Explanation:* Sidecar proxies transparently handle traffic (encryption, routing, retries, telemetry) for the Pod they're attached to. A describes storage (Chapter 19), C describes the scheduler (Chapter 20), and D describes CoreDNS (Chapter 18).

---

**Q2.** In a service mesh, what does the control plane do?
A. It handles every individual application request directly
B. It centrally configures and manages the behavior of all data-plane sidecar proxies
C. It replaces the Kubernetes API server
D. It stores container images

**Correct answer: B**
*Explanation:* The control plane configures sidecars cluster-wide; it does not itself forward application traffic (that's the data plane's job, A is wrong). C and D are unrelated to service mesh control planes.

---

**Q3.** What does mTLS provide in a service mesh context?
A. One-way encryption only, with no authentication
B. Mutual authentication and encryption between both sides of a connection
C. DNS-based service discovery
D. Traffic splitting between application versions

**Correct answer: B**
*Explanation:* mTLS (mutual TLS) means both the client and server authenticate each other and encrypt traffic between them. A understates it (mTLS is two-way, not one-way). C and D describe unrelated mesh/cluster features.

---

**Q4.** Why might a team choose PERMISSIVE mTLS mode over STRICT mode during a mesh migration?
A. PERMISSIVE mode is faster at forwarding packets
B. PERMISSIVE mode accepts both plaintext and mTLS traffic, allowing gradual onboarding of non-mesh clients
C. PERMISSIVE mode disables all encryption for better performance
D. STRICT mode is deprecated and no longer supported

**Correct answer: B**
*Explanation:* PERMISSIVE mode allows a mixed environment of mesh and non-mesh clients during migration, avoiding broken connections. A and C misdescribe PERMISSIVE mode's actual purpose, and D is false.

---

**Q5.** What problem does traffic splitting (canary routing) in a service mesh primarily address?
A. Encrypting traffic between services
B. Gradually shifting a percentage of traffic to a new service version to limit the blast radius of a bad release
C. Assigning Pods to specific nodes
D. Resolving Service DNS names to Pod IPs

**Correct answer: B**
*Explanation:* Traffic splitting enables gradual, controlled rollouts of new versions. A describes mTLS, C describes scheduling (Chapter 20), and D describes CoreDNS (Chapter 18).

---

**Q6.** Using the building analogy from this chapter, what does the sidecar proxy correspond to?
A. The building's residents
B. The security guards/concierge staff stationed at every door
C. The building's architectural blueprint
D. The building's power grid

**Correct answer: B**
*Explanation:* The sidecar proxy handles ID verification, visitor logging, and routing on behalf of the "resident" (application), just as security/concierge staff handle these tasks for building occupants. A represents the application itself, and C and D are unrelated.

---

**Q7.** What was a key limitation of pre-mesh approaches like Netflix's Hystrix "fat client" libraries?
A. They only worked in Kubernetes
B. Every team had to adopt and keep the same per-language library updated
C. They provided no retry functionality at all
D. They required no code changes

**Correct answer: B**
*Explanation:* Library-based approaches required every team, across every language, to adopt and maintain the same library — a coordination burden that service meshes eliminate by moving logic into infrastructure. A, C, and D misdescribe these libraries.

---

**Q8.** How is traffic transparently redirected through a Pod's sidecar proxy?
A. Via manual application code changes
B. Via iptables rules configured during sidecar injection
C. Via a separate Kubernetes Service object per Pod
D. Via DNS overrides only

**Correct answer: B**
*Explanation:* Per the Internal Working flow, iptables rules transparently redirect inbound/outbound traffic through the local sidecar without any application awareness. A contradicts the transparency of the pattern; C and D are not the mechanism used.

---

**Q9.** What does a `VirtualService` resource define in Istio?
A. A namespace-wide mTLS enforcement policy
B. Traffic routing rules, such as weighted splits between service versions
C. A container image registry mirror
D. A Pod's resource requests and limits

**Correct answer: B**
*Explanation:* `VirtualService` defines routing rules like the 90/10 weighted split shown in the YAML Deep Dive. A describes `PeerAuthentication` instead; C and D are unrelated to Istio traffic routing.

---

**Q10.** In the YAML Deep Dive's `PeerAuthentication` example, what does `mode: STRICT` enforce?
A. Only plaintext connections are accepted
B. Every Pod in the `production` namespace only accepts mTLS-encrypted connections
C. All traffic is routed to version v2 only
D. Sidecar injection is disabled

**Correct answer: B**
*Explanation:* STRICT mode forces mTLS-only connections within the namespace, rejecting any plaintext traffic. A is the opposite of STRICT's effect; C and D are unrelated to `PeerAuthentication`.

---

**Q11.** Per the Architecture diagram, who configures the sidecar proxies in Pods A and B?
A. Each Pod configures its own sidecar independently
B. The centralized control plane (Istiod/Linkerd control)
C. The Kubernetes scheduler
D. The etcd cluster directly

**Correct answer: B**
*Explanation:* The diagram shows the control plane centrally configuring sidecars across all Pods — a defining characteristic of the mesh's centralized management model. A contradicts this centralization; C and D play no role in mesh configuration.

---

**Q12.** Per the Troubleshooting table, what is the likely cause when traffic still hits the old version despite a `VirtualService` update?
A. The control plane has crashed
B. Config not yet propagated, or subset labels don't match Pod labels
C. mTLS is misconfigured
D. The sidecar proxy was never injected

**Correct answer: B**
*Explanation:* This is the table's listed cause for that specific symptom — either sync delay or a labeling mismatch between the `VirtualService` subset and actual Pod labels. A, C, and D map to different symptoms in the same table.

---

**Q13.** Why is it a common mistake to assume a service mesh replaces the need for Kubernetes NetworkPolicies?
A. NetworkPolicies are deprecated in favor of meshes
B. They solve different problems — mesh handles L7 application-layer concerns, NetworkPolicy handles L3/L4 segmentation
C. Meshes cannot enforce any security controls
D. NetworkPolicies only work outside Kubernetes

**Correct answer: B**
*Explanation:* As the Comparison Table shows, mesh and NetworkPolicy operate at different layers and are complementary, not substitutes for one another. A, C, and D are false claims contradicted by the chapter content.

---

**Q14.** What operational cost should teams monitor when adopting a service mesh, per the Best Practices section?
A. The additional CPU/memory overhead sidecars add to every Pod
B. The cost of Kubernetes licensing
C. The cost of etcd storage
D. The cost of container image registries

**Correct answer: A**
*Explanation:* Sidecars are not free — they consume extra per-Pod resources, which the Best Practices section explicitly calls out as something to monitor. B, C, and D are unrelated cost concerns.

---

**Q15.** In Lab 3, what happens when a non-mesh (no sidecar) client tries to connect to a service under strict mTLS enforcement?
A. The connection succeeds normally
B. The connection is rejected/refused
C. The client is automatically injected with a sidecar
D. The request is silently dropped with no error

**Correct answer: B**
*Explanation:* Strict mTLS requires mutual authentication that a non-mesh client cannot perform, so its connection attempt is rejected/refused — directly demonstrating why PERMISSIVE mode is safer during migration. A, C, and D misdescribe the lab's actual observed outcome.

---

**Q16.** Why does sidecar injection typically require a Pod restart to take effect on already-running workloads?
A. Kubernetes forbids modifying running Pods' containers, so a new Pod (with the sidecar) must be created via restart
B. The control plane cannot reach running Pods
C. mTLS certificates expire after restart
D. Sidecar injection is disabled by default

**Correct answer: A**
*Explanation:* Since a Pod's container spec is effectively immutable once running, adding the sidecar container requires creating a new Pod instance — hence the Common Mistakes note about needing a restart. B, C, and D are incorrect explanations.

---

**Q17.** Which mesh feature is used for chaos-engineering-style fault injection, per the Real-World Examples?
A. mTLS enforcement
B. Mesh capabilities that deliberately inject latency or errors into specific service calls
C. Circuit breaking only
D. DNS-based service discovery

**Correct answer: B**
*Explanation:* The Real-World Examples section describes using mesh fault-injection capabilities for chaos engineering to test resilience. A, C, and D describe other, unrelated mesh features.

---

**Q18.** What distinguishes Linkerd's proxy from Istio's, per the Comparison Table?
A. Linkerd uses Envoy; Istio uses a Rust-based proxy
B. Linkerd uses a lightweight, Rust-based proxy (linkerd2-proxy); Istio uses the general-purpose, feature-rich Envoy proxy
C. Linkerd has no data plane at all
D. Istio has no control plane at all

**Correct answer: B**
*Explanation:* The table specifically distinguishes linkerd2-proxy (lightweight, Rust-based, simpler) from Envoy (general-purpose, more feature-rich, more complex) in Istio. A reverses the pairing; C and D are false.

---

**Q19.** What is the effect of circuit breaking in a service mesh?
A. It permanently deletes the unhealthy service
B. It temporarily stops sending traffic to an unhealthy destination to prevent cascading failure
C. It encrypts traffic to unhealthy destinations only
D. It automatically scales up the unhealthy Pod

**Correct answer: B**
*Explanation:* Circuit breaking protects the overall system by cutting off traffic to a failing dependency, preventing a single slow/broken service from cascading into a fleet-wide outage. A, C, and D misdescribe this mechanism.

---

**Q20.** Per the memory tricks in this chapter, which phrase best captures the data plane/control plane relationship?
A. "Mesh talks app-layer (L7), NetworkPolicy talks network-layer (L3/L4)"
B. "Data plane does the work, control plane gives the orders"
C. "Building security/concierge staff"
D. "STRICT trusts nobody, PERMISSIVE trusts everybody"

**Correct answer: B**
*Explanation:* This mnemonic directly captures the split tested throughout this chapter: the data plane (sidecars) executes traffic handling, while the control plane centrally issues configuration. A contrasts mesh vs NetworkPolicy, C is the general mesh analogy, and D is not a phrase listed in this chapter's Memory Tricks.

---

## 21. Chapter Summary (One-Page Revision Sheet)

- A **service mesh** moves cross-cutting networking concerns (mTLS, retries, traffic splitting, observability) out of application code and into a **sidecar proxy** deployed alongside every Pod.
- The mesh splits into a **data plane** (the sidecar proxies actually handling traffic) and a **control plane** (centrally configuring all sidecars — e.g., Istiod).
- Key features: **mTLS** (mutual authentication + encryption), **traffic splitting/canary** (gradual rollout), **retries/timeouts**, and **circuit breaking**.
- **Istio** (Envoy-based, feature-rich) and **Linkerd** (lightweight, Rust-based) are the two leading meshes, with different complexity/overhead trade-offs.
- A service mesh is **complementary to, not a replacement for**, Kubernetes NetworkPolicies — mesh handles L7 application concerns, NetworkPolicy handles L3/L4 network segmentation.

---

### Chapter Completion Checklist

1. **Topics covered:** Sidecar proxy pattern, data plane/control plane split, mTLS, traffic splitting/canary, circuit breaking, Istio vs Linkerd.
2. **KCNA objectives completed:** Cloud Native Architecture — Service Mesh.
3. **Remaining objectives:** GitOps — declarative, Git-driven continuous delivery (Chapter 24).
4. **Suggested revision checklist:** Explain the sidecar pattern from memory; explain data plane vs control plane; explain PERMISSIVE vs STRICT mTLS.
5. **Suggested hands-on exercises:** Complete Lab 2 (apply a canary traffic split and observe the distribution) — the clearest demonstration of mesh-driven traffic management.
6. **Related chapters:** Previous: [22-Observability](../22-Observability/README.md). Next: [24-GitOps](../24-GitOps/README.md) — declarative, Git-driven continuous delivery.
