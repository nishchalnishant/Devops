# 17 — Ingress and Gateway API

## 1. Learning Objectives

By the end of this chapter you will be able to:

- Explain why L4 Services (Chapter 16) alone are insufficient for HTTP-based routing at scale.
- Explain how an Ingress routes HTTP(S) traffic to multiple Services based on host/path rules.
- Explain the role of an Ingress Controller in actually implementing Ingress rules.
- Explain why the Gateway API was created and how it improves on Ingress.
- Read and write Ingress and Gateway API manifests.

**KCNA objectives covered:** Kubernetes Fundamentals / Cloud Native Architecture domain — L7 HTTP routing and the modern Gateway API, building directly on the Service abstraction (Chapter 16).

---

## 2. Historical Background

Services (Chapter 16) solve L4 (TCP/UDP) exposure well, but a `LoadBalancer` Service per application gets expensive and unwieldy fast — every application needing external HTTP access would need its **own** cloud load balancer, with no shared, HTTP-aware routing (like path-based or host-based rules) between them. Kubernetes introduced **Ingress** as an API object to describe HTTP(S) routing rules — "route requests for `api.example.com` to the API Service, and `app.example.com` to the frontend Service" — all through a single shared entry point. However, Ingress's design turned out to have real limitations (Section 4.4), leading the community to design a successor: the **Gateway API**.

---

## 3. Motivation: Why Do Ingress and Gateway API Exist?

**Analogy — The Apartment Building's Front Desk:**
Imagine an apartment building where every single tenant needed their own private street entrance and doorman — wildly expensive and impractical. Instead, real buildings have **one shared front desk**: visitors arrive at one address, tell the desk who they're visiting, and the desk directs them to the right apartment. An **Ingress** is that shared front desk for HTTP traffic: one external entry point (often backed by one cloud load balancer) that reads the incoming request's hostname and URL path, then routes it to the correct internal Service — instead of every application needing its own dedicated `LoadBalancer` Service.

### 3.1 How Was This Solved Before Kubernetes?

HTTP routing across many backend applications was handled by dedicated reverse proxies or hardware load balancers (like an on-prem F5 or a hand-configured NGINX), manually configured by ops teams whenever routing rules changed — again, a slow, manual process poorly suited to Kubernetes's dynamic environment.

### 3.2 How Kubernetes Solves It

An **Ingress** object declares HTTP(S) routing rules (host + path → Service) as Kubernetes-native, version-controlled configuration. An **Ingress Controller** (a separate, pluggable component — Kubernetes ships no built-in one) watches Ingress objects and actually implements the routing, typically by configuring a reverse proxy (like NGINX, Traefik, or HAProxy) or a cloud load balancer. The newer **Gateway API** re-designs this space with a more expressive, role-oriented, and extensible model (Section 4.4).

---

## 4. Core Concepts

### 4.1 Ingress Resource Basics

An Ingress defines rules matching incoming HTTP requests by **host** (e.g., `api.example.com`) and/or **path** (e.g., `/orders`), directing matched traffic to a specific backend Service and port.

### 4.2 Ingress Controller

**Definition:** The Ingress Controller is the actual software that watches Ingress objects via the API server and configures a real proxy/load balancer to enforce those rules. **Kubernetes does not ship a default Ingress Controller** — a cluster with Ingress objects but no controller installed will simply have no effect. Popular controllers include NGINX Ingress Controller, Traefik, HAProxy Ingress, and cloud-managed controllers (e.g., AWS Load Balancer Controller, GKE Ingress).

### 4.3 TLS Termination

Ingress supports specifying a TLS secret (containing a certificate and key) per host, allowing the Ingress Controller to terminate HTTPS at the entry point and forward plain HTTP internally — centralizing certificate management instead of requiring every backend to handle TLS itself.

### 4.4 Why the Gateway API Was Created

| Ingress Limitation | Gateway API Improvement |
|---|---|
| Single flat resource mixing infrastructure and routing concerns, awkward for shared multi-team clusters | Splits roles: `GatewayClass`/`Gateway` (infra, managed by platform teams) vs `HTTPRoute` (routing rules, managed by app teams) |
| Limited expressiveness — annotations needed for anything beyond basic host/path rules, and annotations are controller-specific (non-portable) | Rich, portable, structured fields for header matching, traffic splitting/weighting, redirects, and more — no vendor-specific annotations needed |
| HTTP-only, awkward extension to other protocols | Designed to be extensible across protocols (HTTP, gRPC, TCP, TLS passthrough) |

**Definition:** The **Gateway API** is a newer, more expressive Kubernetes API for traffic routing, designed to eventually supersede Ingress. It introduces `GatewayClass` (defines a type of load balancer implementation, analogous to `StorageClass`), `Gateway` (an actual instance of listeners/entry points), and `HTTPRoute` (routing rules attached to a Gateway) as separate, role-scoped resources.

---

## 5. Internal Working

```
1. An Ingress object defines: host "api.example.com", path "/v1" →
   Service "api-svc" port 80
        ↓
2. The Ingress Controller (e.g., NGINX Ingress Controller), running
   as Pods in the cluster, watches the API server for Ingress
   objects
        ↓
3. On detecting the new/updated Ingress, the controller reconfigures
   its underlying proxy (e.g., regenerates an NGINX config and
   reloads it)
        ↓
4. External traffic arrives at the Ingress Controller's own exposed
   entry point (often itself a LoadBalancer Service)
        ↓
5. The controller inspects the request's Host header and path,
   matches it against the configured rules, and forwards it to the
   correct backend Service — which then routes to a Pod exactly as
   in Chapter 16
```

---

## 6. Architecture

```
                        External Traffic
                              │
                              ▼
                ┌─────────────────────────┐
                │  Ingress Controller           │
                │  (e.g., NGINX), exposed via   │
                │  one LoadBalancer Service      │
                └─────────────┬─────────────┘
                              │  reads Ingress rules:
                              │  api.example.com/*  → api-svc
                              │  app.example.com/*  → frontend-svc
                ┌─────────────┼─────────────┐
                ▼                                ▼
        ┌───────────────┐              ┌───────────────┐
        │ Service: api-svc      │              │ Service: frontend-svc│
        └───────┬───────┘              └───────┬───────┘
                ▼                                ▼
           API Pods                        Frontend Pods
```

---

## 7. Component Breakdown

| Piece | Role |
|---|---|
| Ingress object | Declares host/path → Service HTTP routing rules |
| Ingress Controller | Separately-installed component that implements Ingress rules via a real proxy/load balancer |
| Gateway API: GatewayClass | Defines a type/implementation of traffic-handling infrastructure |
| Gateway API: Gateway | An actual instance of listeners (ports, protocols, TLS) |
| Gateway API: HTTPRoute | Routing rules attached to a Gateway, owned by application teams |

---

## 8. Important Terminology

| Term | Meaning |
|---|---|
| Ingress | API object declaring HTTP(S) host/path routing rules |
| Ingress Controller | Component that implements Ingress rules via a real proxy/LB |
| Gateway API | Newer, more expressive, role-split successor to Ingress |
| GatewayClass | Defines an implementation/type of Gateway infrastructure |
| Gateway | An instance of traffic-handling listeners |
| HTTPRoute | Routing rules attached to a Gateway |

---

## 9. YAML Deep Dive

**Ingress:**
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: example-ingress
spec:
  ingressClassName: nginx
  tls:
    - hosts: ["api.example.com"]
      secretName: api-tls-secret
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /v1
            pathType: Prefix
            backend:
              service:
                name: api-svc
                port:
                  number: 80
```

**Gateway API:**
```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: example-gateway
spec:
  gatewayClassName: nginx
  listeners:
    - name: http
      protocol: HTTP
      port: 80
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: api-route
spec:
  parentRefs:
    - name: example-gateway
  hostnames: ["api.example.com"]
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /v1
      backendRefs:
        - name: api-svc
          port: 80
```

---

## 10. kubectl Commands

| Command | Purpose | Example |
|---|---|---|
| `kubectl get ingress` | List Ingress objects | `kubectl get ingress` |
| `kubectl describe ingress <name>` | Show rules and backend status | `kubectl describe ingress example-ingress` |
| `kubectl get gatewayclass` | List available GatewayClasses | `kubectl get gatewayclass` |
| `kubectl get gateway` | List Gateway objects | `kubectl get gateway` |
| `kubectl get httproute` | List HTTPRoute objects | `kubectl get httproute` |

---

## 11. Hands-on Examples

**Lab 1 — Deploy an Ingress Controller and a basic Ingress:**
```bash
# Assumes an Ingress Controller (e.g., NGINX) is already installed
kubectl apply -f example-ingress.yaml
kubectl get ingress example-ingress
curl -H "Host: api.example.com" http://<ingress-controller-ip>/v1
```

**Lab 2 — Add a second host rule and verify routing:**
```bash
kubectl edit ingress example-ingress
# add a second rule: host: app.example.com → frontend-svc
curl -H "Host: app.example.com" http://<ingress-controller-ip>/
curl -H "Host: api.example.com" http://<ingress-controller-ip>/v1
# Confirm each host routes to its own distinct Service
```

**Lab 3 — Deploy the same routing via Gateway API:**
```bash
kubectl apply -f example-gateway.yaml
kubectl apply -f api-httproute.yaml
kubectl get gateway example-gateway
kubectl get httproute api-route
```

---

## 12. Internal Flow

See Section 5 — Ingress (and Gateway API) add an **L7-aware routing layer** on top of the L4 Service abstraction (Chapter 16): instead of clients connecting directly to a Service's stable IP, they connect to a shared entry point that inspects HTTP-level details (Host header, path) before deciding *which* Service to forward to — multiplying one external entry point across many internal applications.

---

## 13. Real-World Examples

1. **Multi-tenant clusters** use one Ingress Controller and many host-based Ingress rules (`tenant-a.example.com`, `tenant-b.example.com`) to serve many applications through a single shared external load balancer.
2. **API versioning** uses path-based Ingress rules (`/v1`, `/v2`) to route different API versions to different backend Services.
3. **Centralized TLS management** — teams terminate HTTPS once at the Ingress Controller using a wildcard certificate, rather than configuring TLS in every individual application.
4. **Canary/traffic-splitting rollouts** are increasingly done via Gateway API's `HTTPRoute` weighted backend references, giving portable, no-annotation traffic splitting.
5. **Platform teams standardizing infrastructure** use Gateway API's `GatewayClass`/`Gateway` split to let a central team own load-balancer infrastructure while application teams independently own their own `HTTPRoute` rules.

---

## 14. Best Practices

- Always confirm an Ingress Controller is actually installed before troubleshooting "why doesn't my Ingress work" — Ingress objects with no controller do nothing.
- Centralize TLS certificate management at the Ingress/Gateway layer rather than in every individual application.
- Prefer the Gateway API for new projects requiring advanced routing (traffic splitting, header matching) or clean role separation between platform and application teams.
- Use `pathType: Prefix` deliberately and test path-matching behavior carefully — subtle path-matching bugs are a common source of misrouted traffic.

---

## 15. Common Mistakes

- Creating an Ingress object without installing any Ingress Controller, then being confused when nothing happens.
- Relying on controller-specific annotations for advanced routing behavior (e.g., NGINX-specific rewrite annotations), which breaks portability if the Ingress Controller is ever swapped.
- Forgetting to reference the correct `ingressClassName` in multi-controller clusters, causing rules to be picked up by the wrong controller or none at all.
- Assuming Ingress can do non-HTTP (raw TCP/UDP) routing — it's fundamentally an HTTP(S)-focused API (Gateway API extends further into TCP/TLS passthrough).

---

## 16. Troubleshooting

| Symptom | Likely Cause | Debugging Commands | Fix |
|---|---|---|---|
| Ingress rules have no effect at all | No Ingress Controller installed | `kubectl get pods -A \| grep ingress` | Install an Ingress Controller |
| 404 or default backend response | Host/path rule doesn't match request, or `ingressClassName` mismatch | `kubectl describe ingress` | Correct host/path rules or ingressClassName |
| TLS handshake fails | Missing or misconfigured TLS secret | `kubectl describe ingress`, `kubectl get secret` | Ensure the referenced TLS secret exists and is valid |
| HTTPRoute has no effect | Not correctly attached via `parentRefs`, or Gateway not Ready | `kubectl describe httproute`, `kubectl describe gateway` | Fix `parentRefs`; verify Gateway status |

---

## 17. Comparison Tables

**Service vs Ingress vs Gateway API:**

| Aspect | Service | Ingress | Gateway API |
|---|---|---|---|
| Layer | L4 (TCP/UDP) | L7 (HTTP/HTTPS) | L4-L7, extensible |
| Routing granularity | Whole Service | Host/path rules | Rich: host/path/header/weight |
| Role separation | None | Minimal | Explicit (GatewayClass/Gateway vs HTTPRoute) |
| Requires extra component | No (kube-proxy is built-in) | Yes (Ingress Controller) | Yes (Gateway API controller) |

---

## 18. Memory Tricks

- **"Ingress/Gateway = the apartment building's front desk"** — one shared entry point routing visitors (requests) by who they're asking for (host/path).
- **"No controller, no Ingress"** — remember Ingress objects are inert config without an installed controller.
- Gateway API role mnemonic: **"GatewayClass/Gateway = landlord's infrastructure, HTTPRoute = tenant's own routing rules."**

---

## 19. Interview Questions

**Easy:**
1. What problem does Ingress solve that a plain Service does not?
   *Expected answer:* A Service only provides L4 (TCP/UDP) exposure to one set of Pods; giving every application its own external `LoadBalancer` Service to get HTTP access is expensive and lacks HTTP-aware routing. Ingress adds an L7-aware layer that can route HTTP(S) traffic to many different Services based on hostname and URL path, all through one shared external entry point.

**Medium:**
2. Why does installing an Ingress object alone often "not work," and what else is required?
   *Expected answer:* Kubernetes does not ship a built-in Ingress Controller — the Ingress object itself is just declarative configuration describing desired routing rules. Without a separately installed Ingress Controller (e.g., NGINX Ingress Controller, Traefik) actually watching for and implementing those rules against a real proxy or cloud load balancer, the Ingress object has no effect on traffic at all.

**Hard:**
3. A platform team wants application teams to be able to independently manage their own HTTP routing rules without being able to modify shared load-balancer infrastructure settings (like listener ports or TLS certificate stores). Explain why Ingress makes this hard and how the Gateway API addresses it.
   *Expected answer:* Ingress is a single, flat resource that mixes infrastructure-level configuration (e.g., annotations controlling the underlying load balancer/proxy behavior) with application-level routing rules in the same object and often the same YAML file — there's no clean, RBAC-friendly way to let application teams edit routing without also being able to touch infrastructure-sensitive settings. The Gateway API explicitly splits these concerns into separate resources with separate ownership: `GatewayClass` and `Gateway` (infrastructure — listeners, TLS, load balancer type) are typically owned and managed by the platform team, while `HTTPRoute` (routing rules — host/path matching, backend references, traffic splitting) is owned by application teams and simply attaches to an existing Gateway via `parentRefs`. This allows RBAC to be scoped precisely: application teams get write access to HTTPRoutes only, while platform teams retain sole control over Gateway/GatewayClass infrastructure.

---

## 20. KCNA Practice Questions

**Q1.** What is the primary purpose of an Ingress object?
A. To provide a stable virtual IP for a single set of Pods
B. To declare HTTP(S) routing rules based on host and path, directing traffic to different Services
C. To run Pods to completion
D. To manage persistent storage across Pod restarts

**Correct answer: B**
*Explanation:* Ingress adds L7 HTTP-aware routing on top of Services. A describes a Service (Chapter 16). C describes a Job (Chapter 15). D describes storage-related objects (Chapter 19).

---

**Q2.** What must be installed separately for an Ingress object to actually have any effect on traffic?
A. Nothing — Kubernetes ships a default Ingress Controller
B. An Ingress Controller
C. A CNI plugin
D. A CSI driver

**Correct answer: B**
*Explanation:* Kubernetes does not ship a built-in Ingress Controller; one must be installed separately to implement Ingress rules. A is false. C (Chapter 18) and D (Chapter 19) are unrelated components.

---

**Q3.** Which Gateway API resource is analogous to routing rules that application teams would typically own?
A. GatewayClass
B. Gateway
C. HTTPRoute
D. IngressClass

**Correct answer: C**
*Explanation:* `HTTPRoute` holds routing rules and is designed to be owned by application teams, attaching to an existing Gateway. GatewayClass (A) and Gateway (B) represent infrastructure typically owned by platform teams. IngressClass (D) belongs to the older Ingress API, not Gateway API.

---

**Q4.** What is a key advantage of the Gateway API over the original Ingress API?
A. It removes the need for any routing rules entirely
B. It provides richer, portable routing capabilities (e.g., header matching, traffic splitting) without vendor-specific annotations
C. It eliminates the need for Services entirely
D. It only works with one specific cloud provider

**Correct answer: B**
*Explanation:* Gateway API was designed specifically to add expressive, portable routing features as structured API fields, avoiding the annotation-based, vendor-specific workarounds Ingress often required. A, C, and D misstate what Gateway API actually changes.

---

**Q5.** In an Ingress rule, what does `pathType: Prefix` control?
A. Which TLS certificate to use
B. How the specified path should be matched against incoming request paths
C. Which Ingress Controller implementation to use
D. The priority order of multiple Ingress objects

**Correct answer: B**
*Explanation:* `pathType` (e.g., `Prefix`, `Exact`, `ImplementationSpecific`) determines how the `path` field is matched against the actual request path. A, C, and D describe unrelated Ingress configuration concerns.

---

**Q6.** Why did every application needing external HTTP access with only `LoadBalancer` Services become expensive and unwieldy?
A. Because `LoadBalancer` Services cannot route HTTP traffic at all
B. Because each application would need its own dedicated cloud load balancer, with no shared host/path-aware routing between them
C. Because `LoadBalancer` Services are limited to a single Pod
D. Because Kubernetes charges a licensing fee per LoadBalancer Service

**Correct answer: B**
*Explanation:* Per Section 2, one `LoadBalancer` Service per app means one real cloud load balancer per app — costly and lacking any shared HTTP-aware routing. A is false — LoadBalancer can carry HTTP traffic, just without L7 awareness. C is false; LoadBalancer routes across all matching Pods. D is not a real Kubernetes concept.

---

**Q7.** In the apartment building analogy (Section 3), what does the shared front desk represent?
A. An individual Pod
B. The Ingress — one shared external entry point that reads the request and routes to the correct internal Service
C. A NetworkPolicy
D. The etcd datastore

**Correct answer: B**
*Explanation:* The front desk maps directly to the Ingress: one entry point that reads "who are you visiting" (Host/path) and directs accordingly. A, C, and D are unrelated to this analogy.

---

**Q8.** What does an Ingress Controller do with a TLS Secret referenced in an Ingress object?
A. It ignores it — TLS is handled entirely by the client
B. It uses the certificate and key to terminate HTTPS at the entry point, then forwards plain HTTP internally
C. It deletes the Secret after first use
D. It forwards the encrypted traffic unmodified all the way to the Pod

**Correct answer: B**
*Explanation:* Per Section 4.3, centralizing TLS termination at the Ingress Controller avoids requiring every backend application to handle HTTPS itself. A, C, and D misstate this behavior.

---

**Q9.** Which Gateway API resource is most analogous to a `StorageClass` in how it defines an implementation/type rather than an instance?
A. HTTPRoute
B. GatewayClass
C. Gateway
D. Service

**Correct answer: B**
*Explanation:* Section 4.4 explicitly draws this comparison — `GatewayClass` defines a type of load-balancer implementation, just as `StorageClass` defines a type of storage provisioner. A and C are instance/rule-level resources, not implementation-type definitions. D is unrelated.

---

**Q10.** Which of the following is a routing capability that Gateway API supports natively via structured fields, without needing vendor-specific annotations?
A. Basic host-only routing
B. Traffic splitting/weighting across backends
C. TLS certificate storage
D. Node selection for Pods

**Correct answer: B**
*Explanation:* Per Section 4.4's comparison table, Gateway API adds rich, portable fields for traffic splitting/weighting, header matching, and redirects — capabilities Ingress could only achieve via non-portable, controller-specific annotations. A is available in both APIs. C and D are unrelated concerns.

---

**Q11.** What happens when external traffic first arrives at a cluster using Ingress, per the Internal Working flow (Section 5)?
A. It goes directly to a specific Pod's IP address
B. It arrives at the Ingress Controller's own exposed entry point (often itself a LoadBalancer Service), which then inspects Host/path and forwards to the correct Service
C. It is dropped unless a NetworkPolicy explicitly allows it
D. It bypasses the Ingress Controller and goes straight to etcd

**Correct answer: B**
*Explanation:* Step 4-5 of Section 5 describes traffic hitting the controller's own exposed entry point first, which then does the Host/path matching before forwarding onward. A, C, and D misdescribe this flow.

---

**Q12.** According to the chapter's Architecture diagram (Section 6), what sits between the Ingress Controller and the actual Pods?
A. Nothing — the controller connects directly to Pod IPs, bypassing Services
B. The relevant backend Services (e.g., `api-svc`, `frontend-svc`), which then route to their respective Pods
C. A second Ingress Controller
D. A ConfigMap

**Correct answer: B**
*Explanation:* Per Section 6, the Ingress Controller routes matched traffic to a Service, which then handles the final Service→Pod routing exactly as in Chapter 16. A is false — Services remain in the path. C and D are not part of this architecture.

---

**Q13.** Why is relying on Ingress Controller-specific annotations (e.g., NGINX rewrite annotations) for advanced routing considered a common mistake?
A. Annotations are not supported by the Kubernetes API at all
B. It breaks portability — if the Ingress Controller is ever swapped for a different implementation, those controller-specific annotations stop working
C. Annotations cause the Ingress object to be rejected by the API server
D. It causes TLS termination to fail

**Correct answer: B**
*Explanation:* Section 15 flags this exact portability risk — controller-specific annotations tie routing behavior to one implementation. A and C are false; annotations are valid API metadata. D is unrelated.

---

**Q14.** A cluster runs multiple Ingress Controllers simultaneously. What field must be correctly set on an Ingress object to ensure the right controller picks it up?
A. `apiVersion`
B. `ingressClassName`
C. `metadata.labels`
D. `spec.tls`

**Correct answer: B**
*Explanation:* Per Section 15's common mistakes and the YAML in Section 9, `ingressClassName` determines which installed controller implements a given Ingress in a multi-controller cluster. A is a fixed schema field. C and D serve different purposes.

---

**Q15.** What is the most likely root cause if `kubectl get pods -A | grep ingress` returns no results and an Ingress object is having no effect?
A. The Service selector doesn't match any Pods
B. No Ingress Controller is installed in the cluster
C. The TLS Secret is missing
D. The `pathType` field is misconfigured

**Correct answer: B**
*Explanation:* Per the troubleshooting table (Section 16), an empty result for Ingress Controller Pods directly indicates none is installed — matching the "no controller, no effect" rule. A relates to Service troubleshooting (Chapter 16). C and D would cause narrower, different symptoms (TLS handshake failure, path-matching issues) rather than total inertness.

---

**Q16.** Comparing Service, Ingress, and Gateway API per the chapter's comparison table (Section 17), which correctly matches layer to object?
A. Service = L7, Ingress = L4, Gateway API = L4 only
B. Service = L4, Ingress = L7, Gateway API = L4-L7 extensible
C. All three operate exclusively at L7
D. All three operate exclusively at L4

**Correct answer: B**
*Explanation:* Section 17's table is explicit: Service is L4 (TCP/UDP), Ingress is L7 (HTTP/HTTPS), and Gateway API is designed to be extensible across L4-L7. A reverses Service/Ingress. C and D collapse the distinction the table exists to teach.

---

**Q17.** Per the Gateway API role-split mnemonic (Section 18), who owns HTTPRoute objects?
A. The platform/infrastructure team exclusively
B. Application teams, since HTTPRoute holds routing rules rather than shared infrastructure
C. Only the cluster's cloud provider
D. No one — HTTPRoute is deprecated

**Correct answer: B**
*Explanation:* The mnemonic explicitly assigns "GatewayClass/Gateway = landlord's infrastructure, HTTPRoute = tenant's own routing rules" — application teams own HTTPRoute. A describes GatewayClass/Gateway ownership instead. C and D are incorrect.

---

**Q18.** A canary rollout needs to send 10% of traffic to a new backend version and 90% to the stable version, using portable, no-annotation configuration. Which approach fits best, per Section 13's real-world examples?
A. Two separate Ingress objects with no coordination
B. Gateway API's `HTTPRoute` with weighted `backendRefs`
C. A single Service with two selectors
D. A NetworkPolicy limiting traffic by percentage

**Correct answer: B**
*Explanation:* Section 13 explicitly calls out Gateway API's weighted backend references as the modern, portable way to do traffic-splitting canary rollouts. A doesn't provide weighting. C is not how Services work — a Service selector matches a set of Pods, not a percentage split. D is not what NetworkPolicies do (Chapter 18 covers them for traffic *permission*, not weighting).

---

**Q19.** What is the correct troubleshooting step if an `HTTPRoute` appears to have no effect on traffic?
A. Delete and recreate the entire cluster
B. Check that `parentRefs` correctly attaches the HTTPRoute to a Gateway, and confirm the Gateway itself is in a Ready state
C. Restart kube-proxy
D. Convert the HTTPRoute into an Ingress object

**Correct answer: B**
*Explanation:* Per the troubleshooting table (Section 16), a non-functional HTTPRoute is commonly caused by an incorrect `parentRefs` attachment or a Gateway that isn't Ready — both are directly checkable via `kubectl describe`. A is extreme and unrelated. C affects Service-level L4 routing, not Gateway API's L7 routing. D is not a meaningful operation.

---

**Q20.** Why does Gateway API's split between `GatewayClass`/`Gateway` and `HTTPRoute` make RBAC scoping easier for multi-team clusters, per interview Q3 (Section 19)?
A. Because Gateway API disables RBAC entirely for simplicity
B. Because platform teams can retain sole write access to Gateway/GatewayClass (infrastructure) while granting app teams write access only to HTTPRoute (routing), unlike Ingress's single flat mixed-concern resource
C. Because HTTPRoute objects cannot be created by anyone, including admins
D. Because Gateway API requires all teams to share one combined ClusterRole with no distinctions

**Correct answer: B**
*Explanation:* This is the exact reasoning given in the hard interview question — separate resources for separate concerns allow precise, resource-scoped RBAC policies that Ingress's single mixed object cannot cleanly support. A, C, and D contradict the stated purpose and mechanics of the split.

---

## 21. Chapter Summary (One-Page Revision Sheet)

- **Ingress** declares HTTP(S) host/path routing rules to multiple Services through one shared external entry point — but requires a separately installed **Ingress Controller** to have any actual effect.
- Ingress supports centralized **TLS termination** via referenced Secrets.
- The **Gateway API** is the modern successor, splitting concerns into **GatewayClass**/**Gateway** (infrastructure, platform-team-owned) and **HTTPRoute** (routing rules, application-team-owned), with richer, more portable routing features than Ingress annotations ever provided.
- Both sit at L7, layered on top of the L4 Service abstraction (Chapter 16) — Ingress/Gateway API route to Services, Services route to Pods.

---

### Chapter Completion Checklist

1. **Topics covered:** Ingress rules and Ingress Controllers, TLS termination, Gateway API's GatewayClass/Gateway/HTTPRoute model and its advantages over Ingress.
2. **KCNA objectives completed:** L7 HTTP routing and modern traffic-management APIs, completing the external-access layer on top of Services.
3. **Remaining objectives:** Broader cluster networking concepts — CNI, Network Policies, DNS (Chapter 18).
4. **Suggested revision checklist:** Recite why "Ingress object without a controller does nothing"; explain the Gateway API's three-resource role split from memory; compare Service vs Ingress vs Gateway API layers.
5. **Suggested hands-on exercises:** Complete Lab 2 (adding a second host rule) — directly demonstrates the "one entry point, many backends" value proposition.
6. **Related chapters:** Previous: [16-Services](../16-Services/README.md). Next: [18-Networking](../18-Networking/README.md) — the broader cluster networking model (CNI, Network Policies, DNS) underneath Services and Ingress.
