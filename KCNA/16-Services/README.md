# 16 — Services

## 1. Learning Objectives

By the end of this chapter you will be able to:

- Explain why Pod IPs alone are insufficient for reliable networking.
- Explain how a Service provides a stable virtual IP and DNS name in front of a changing set of Pods.
- Differentiate the four Service types: ClusterIP, NodePort, LoadBalancer, ExternalName.
- Explain how `kube-proxy` implements Service traffic routing.
- Read and write complete Service manifests and connect them to label selectors.

**KCNA objectives covered:** Cloud Native Architecture / Kubernetes Fundamentals domain — Service discovery and networking abstraction, the mechanism that makes ephemeral Pods usable as reliable network endpoints.

---

## 2. Historical Background

Every controller covered so far (Chapters 10-15) solves the problem of **running** Pods reliably. But none of them solve a separate, equally critical problem: Pods are ephemeral — they get created, destroyed, and rescheduled constantly, and each time, they get a **new IP address**. If a frontend Pod needs to talk to a backend, hardcoding the backend Pod's IP would break the moment that Pod was rescheduled. Traditional infrastructure solved "which server do I talk to" with static IPs, DNS entries manually updated by ops teams, or hardware load balancers manually reconfigured — none of which could keep up with Kubernetes's constant Pod churn. Kubernetes introduced the **Service** object specifically to give a stable network identity to a dynamic, changing set of Pods.

---

## 3. Motivation: Why Do Services Exist?

**Analogy — The Restaurant's Order Counter:**
Imagine a restaurant kitchen where chefs (Pods) rotate in and out constantly — one goes on break, a new one steps in, someone gets reassigned. If customers had to shout their order directly at a specific chef by name, the moment that chef left, the system would break. Instead, restaurants use an **order counter**: customers always order at the same counter, and the counter staff routes the order to *whichever* chef is currently available. The counter's location never changes, even though the chefs behind it constantly do. A Kubernetes **Service** is that order counter: a stable address that always routes traffic to whichever healthy Pods currently match its selector — regardless of how often those Pods change.

### 3.1 How Was This Solved Before Kubernetes?

Traditional environments relied on static server IPs, manually maintained DNS records, or dedicated hardware/software load balancers reconfigured by hand whenever backend servers changed — a slow, error-prone, manual process entirely unsuited to Kubernetes's automatic, frequent Pod rescheduling.

### 3.2 How Kubernetes Solves It

A **Service** is assigned a **stable virtual IP (ClusterIP)** and **DNS name** that never changes for the Service's lifetime. It uses a **label selector** (Chapter 09) to continuously discover the current, live set of matching Pods, and transparently load-balances traffic across them — Pods can be created, destroyed, and replaced freely without any client ever needing to know or care.

---

## 4. Core Concepts

### 4.1 The Service-to-Pod Connection: Label Selectors

A Service does not point to specific Pods by name — it uses a **label selector** (exactly like ReplicaSets, Chapter 11) to dynamically match whichever Pods currently carry matching labels. The list of matching Pod IPs is tracked automatically via **Endpoints** (or the newer **EndpointSlice**) objects, updated continuously as Pods come and go.

### 4.2 The Four Service Types

| Type | Exposure Scope | Typical Use Case |
|---|---|---|
| `ClusterIP` (default) | Internal-only virtual IP, reachable only from inside the cluster | Internal microservice-to-microservice communication |
| `NodePort` | Opens a static port (30000-32767) on **every** node's IP, in addition to a ClusterIP | Simple external access for dev/test, or as a building block for external load balancers |
| `LoadBalancer` | Provisions an external cloud load balancer (via cloud provider integration) pointing at the Service | Production external access in a cloud environment |
| `ExternalName` | Maps the Service DNS name to an external DNS name via a CNAME record (no proxying, no selector) | Referring to an external database or third-party API by an internal, consistent name |

### 4.3 How kube-proxy Implements Services

**Definition:** `kube-proxy` (Chapter 08 Section 4.3) runs on every node and is the component that actually implements Service traffic routing — watching the API server for Service and Endpoints changes, and programming the node's networking rules (via `iptables`, `IPVS`, or `nftables`, depending on mode) to transparently redirect traffic sent to a Service's ClusterIP toward one of its healthy backing Pods.

### 4.4 DNS for Services

Every Service automatically gets a predictable DNS name via cluster DNS (CoreDNS, previewed in Chapter 07):

```
<service-name>.<namespace>.svc.cluster.local
```

Within the same namespace, Pods can simply use `<service-name>` as a shorthand.

---

## 5. Internal Working

```
1. A Service object with selector: app=backend is created
        ↓
2. The Endpoints/EndpointSlice controller continuously watches for
   Pods matching that selector and maintains an up-to-date list of
   their IPs
        ↓
3. kube-proxy on every node watches the Service and its Endpoints,
   and programs local networking rules (iptables/IPVS) mapping the
   Service's ClusterIP:port to the current healthy Pod IPs
        ↓
4. A client sends traffic to the stable ClusterIP (or DNS name)
        ↓
5. The node's networking rules transparently redirect that traffic
   to one of the currently matching, healthy Pods — load-balanced
   across all of them
        ↓
6. If a Pod is replaced, its Endpoint entry is removed/added
   automatically — clients never notice, since they only ever
   address the stable Service, never a Pod IP directly
```

---

## 6. Architecture

```
                     Client Pod
                          │
                          │  request to backend-svc.default.svc.cluster.local
                          ▼
        ┌───────────────────────────────┐
        │  Service: backend-svc                │
        │  ClusterIP: 10.96.10.5 (stable)       │
        │  selector: app=backend                │
        └───────────────┬───────────────┘
                          │  kube-proxy routes to a matching, healthy Pod
        ┌────────────────┼────────────────┐
        ▼                    ▼                    ▼
   ┌─────────┐         ┌─────────┐         ┌─────────┐
   │ Pod A       │         │ Pod B       │         │ Pod C       │
   │ app=backend │         │ app=backend │         │ app=backend │
   └─────────┘         └─────────┘         └─────────┘
   (IPs change freely as Pods are replaced — Service address never does)
```

---

## 7. Component Breakdown

| Piece | Role |
|---|---|
| Service object | Declares a stable virtual IP/DNS name and a label selector |
| Endpoints / EndpointSlice | Tracks the live list of matching, healthy Pod IPs |
| kube-proxy | Programs per-node network rules implementing the actual traffic routing |
| CoreDNS | Provides the predictable DNS name resolving to the Service's ClusterIP |

---

## 8. Important Terminology

| Term | Meaning |
|---|---|
| Service | Stable virtual IP/DNS abstraction in front of a dynamic set of Pods |
| ClusterIP | The default, internal-only stable virtual IP type |
| NodePort | Exposes a Service on a static port across every node |
| LoadBalancer | Provisions an external cloud load balancer for a Service |
| ExternalName | Maps a Service name to an external DNS name via CNAME, no proxying |
| Endpoints / EndpointSlice | Live-tracked list of Pod IPs currently matching a Service's selector |
| kube-proxy | Node component implementing Service traffic routing rules |

---

## 9. YAML Deep Dive

```yaml
apiVersion: v1
kind: Service
metadata:
  name: backend-svc
spec:
  type: ClusterIP
  selector:
    app: backend
  ports:
    - port: 80          # port the Service listens on
      targetPort: 8080  # port on the Pod to forward to
---
apiVersion: v1
kind: Service
metadata:
  name: backend-nodeport
spec:
  type: NodePort
  selector:
    app: backend
  ports:
    - port: 80
      targetPort: 8080
      nodePort: 30080   # optional; auto-assigned from 30000-32767 if omitted
---
apiVersion: v1
kind: Service
metadata:
  name: frontend-lb
spec:
  type: LoadBalancer
  selector:
    app: frontend
  ports:
    - port: 443
      targetPort: 8443
```

---

## 10. kubectl Commands

| Command | Purpose | Example |
|---|---|---|
| `kubectl get svc` | List Services | `kubectl get svc` |
| `kubectl describe svc <name>` | Show a Service's selector, endpoints, and ports | `kubectl describe svc backend-svc` |
| `kubectl get endpoints <name>` | Show the current live Pod IPs backing a Service | `kubectl get endpoints backend-svc` |
| `kubectl expose deployment <name>` | Quickly create a Service for an existing Deployment | `kubectl expose deployment backend --port=80 --target-port=8080` |
| `kubectl port-forward svc/<name> <local>:<remote>` | Forward a local port to a Service for local testing | `kubectl port-forward svc/backend-svc 8080:80` |

---

## 11. Hands-on Examples

**Lab 1 — Create a ClusterIP Service and verify DNS resolution:**
```bash
kubectl apply -f backend-svc.yaml
kubectl run tmp --rm -it --image=busybox -- nslookup backend-svc
# Resolves to the stable ClusterIP, regardless of which Pods back it
```

**Lab 2 — Prove the Service survives Pod replacement:**
```bash
kubectl get endpoints backend-svc     # note current Pod IPs
kubectl delete pod -l app=backend --all
kubectl get endpoints backend-svc -w  # new Pod IPs appear automatically
# The Service's ClusterIP never changed throughout
```

**Lab 3 — Expose a Service externally via NodePort:**
```bash
kubectl apply -f backend-nodeport.yaml
kubectl get svc backend-nodeport
# Note the assigned nodePort; access via <any-node-ip>:<nodePort>
```

---

## 12. Internal Flow

See Section 5 — Services combine three moving parts: continuous **label-selector-based Pod discovery** (Chapter 09's mechanism, reused from ReplicaSets), a **stable virtual IP/DNS identity** layer, and **kube-proxy's per-node traffic redirection rules** that turn "send traffic to this stable address" into "actually deliver it to one specific, currently-healthy Pod."

---

## 13. Real-World Examples

1. **Internal microservice communication** — a frontend Service calls a backend Service by stable DNS name (`backend-svc`), never needing to track individual backend Pod IPs.
2. **Exposing a web application externally** in a cloud environment via a `LoadBalancer` Service, provisioning a cloud load balancer automatically.
3. **Database access within a cluster** — a headless Service (Chapter 14 Section 4.2) used alongside a StatefulSet to address specific database replica Pods individually.
4. **Referring to an external, third-party API** via an `ExternalName` Service, giving internal code a consistent internal name regardless of the actual external endpoint.
5. **Development/testing access** to a Service via `NodePort` or `kubectl port-forward`, without needing a full cloud load balancer.

---

## 14. Best Practices

- Default to `ClusterIP` unless external access is genuinely required — minimizes exposed attack surface.
- Use `LoadBalancer` for production external access in cloud environments; reserve `NodePort` for development/testing or as a manual building block.
- Always double-check that a Service's `selector` labels actually match the target Pods' labels — this is one of the most common sources of "Service has no endpoints" issues.
- Name Services descriptively and consistently, since their DNS name becomes a permanent part of how other services address them.

---

## 15. Common Mistakes

- Mismatched `selector` labels between the Service and the Pod template, resulting in a Service with zero Endpoints — traffic goes nowhere.
- Confusing `port` (what the Service listens on) with `targetPort` (what the Pod actually listens on) — traffic sent to the Service port must actually match a `targetPort` the Pod is listening on.
- Using `LoadBalancer` type for every internal Service unnecessarily, incurring real cloud costs and needless external exposure.
- Assuming a Service load-balances at the individual request level for all traffic types — actual behavior depends on `kube-proxy` mode and protocol (e.g., long-lived connections may "stick" to one Pod).

---

## 16. Troubleshooting

| Symptom | Likely Cause | Debugging Commands | Fix |
|---|---|---|---|
| Service has no traffic reaching Pods | Selector doesn't match Pod labels | `kubectl describe svc`, `kubectl get endpoints` | Fix selector or Pod labels to match |
| `kubectl get endpoints` shows empty list | No Pods currently match selector, or Pods aren't Ready | `kubectl get pods --show-labels`, `kubectl describe pod` | Fix labels or Pod readiness |
| NodePort not reachable externally | Firewall/security group blocking the NodePort range | Cloud provider firewall rules | Open the relevant port range |
| DNS name doesn't resolve | CoreDNS issue, or querying from wrong namespace | `kubectl get pods -n kube-system -l k8s-app=kube-dns` | Use fully-qualified name or verify CoreDNS health |

---

## 17. Comparison Tables

**Service Types:**

| Type | Internal Access | External Access | Extra Infra Required |
|---|---|---|---|
| ClusterIP | Yes | No | None |
| NodePort | Yes | Yes (via node IP + port) | None |
| LoadBalancer | Yes | Yes (via cloud LB) | Cloud provider integration |
| ExternalName | N/A (DNS alias only) | N/A | None |

**Service vs Ingress (preview of Chapter 17):** A Service load-balances at L4 (TCP/UDP) for one set of Pods; an Ingress provides L7 (HTTP) routing rules across multiple Services, typically sitting in front of them.

---

## 18. Memory Tricks

- **"Service = restaurant order counter"** — stable address, changing staff behind it.
- Type mnemonic, narrowest to widest: **"Cluster → Node → Load-balancer"** (ClusterIP internal-only → NodePort per-node → LoadBalancer fully external).
- **"port is the counter's number, targetPort is the chef's station"** — don't confuse the two.

---

## 19. Interview Questions

**Easy:**
1. Why can't clients reliably talk directly to a Pod's IP address in Kubernetes?
   *Expected answer:* Pod IPs are not stable — Pods are ephemeral and get a new IP every time they are recreated or rescheduled (Chapter 10). A Service solves this by providing a stable virtual IP and DNS name that remains constant regardless of which specific Pods are currently backing it.

**Medium:**
2. Explain the difference between a Service's `port` and `targetPort` fields.
   *Expected answer:* `port` is the port the Service itself listens on and that clients connect to; `targetPort` is the port on the backing Pods that traffic is actually forwarded to. They can differ — e.g., a Service can expose port 80 externally while forwarding to port 8080 on the actual container — which is common when the container's application listens on a non-standard port.

**Hard:**
3. A team deploys a new version of their backend Pods with an updated set of labels, but forgets to update the Service's `selector` to match. What symptom will they observe, and how would you diagnose and fix it?
   *Expected answer:* The Service's selector will no longer match any of the new Pods, so `kubectl get endpoints <service>` will show an empty list — the Service exists and has a stable ClusterIP, but there are no healthy backends to route traffic to, so all requests will fail or time out even though the Pods themselves are running fine. Diagnosis: `kubectl describe svc` to check the selector, `kubectl get pods --show-labels` to check actual Pod labels, and `kubectl get endpoints` to confirm zero matches. Fix: update either the Service's selector or the Pod template's labels so they match again — once they do, the Endpoints controller will automatically populate the Endpoints list and traffic will start flowing without any other changes needed.

---

## 20. KCNA Practice Questions

**Q1.** What is the primary purpose of a Kubernetes Service?
A. To run a single Pod per node
B. To provide a stable virtual IP and DNS name in front of a changing set of Pods
C. To schedule Pods at a recurring time interval
D. To manage persistent storage for Pods

**Correct answer: B**
*Explanation:* A Service exists to give ephemeral, IP-changing Pods a stable, reliable network identity. A describes a DaemonSet (Chapter 13). C describes a CronJob (Chapter 15). D describes storage-related objects (Chapter 19).

---

**Q2.** Which Service type is reachable only from within the cluster by default?
A. NodePort
B. LoadBalancer
C. ClusterIP
D. ExternalName

**Correct answer: C**
*Explanation:* `ClusterIP` is the default type and is internal-only. NodePort (A) and LoadBalancer (B) both provide external reachability. ExternalName (D) is a DNS alias mechanism, not an internal-only proxy type.

---

**Q3.** What Kubernetes component is responsible for actually implementing a Service's traffic-routing rules on each node?
A. kube-scheduler
B. kube-proxy
C. kubelet
D. etcd

**Correct answer: B**
*Explanation:* `kube-proxy` runs on every node and programs the actual networking rules (iptables/IPVS/nftables) that route Service traffic to backing Pods. kube-scheduler (A) assigns Pods to nodes (Chapter 07). kubelet (C) manages Pod lifecycle on a node (Chapter 08). etcd (D) is the cluster's data store (Chapter 07).

---

**Q4.** How does a Service determine which Pods should receive its traffic?
A. By a fixed list of Pod IPs specified manually in the Service spec
B. By a label selector that is continuously matched against live Pods
C. By the Pod's creation timestamp
D. By the node the Pod is running on

**Correct answer: B**
*Explanation:* Services use label selectors (like ReplicaSets, Chapter 11) to dynamically and continuously discover matching Pods via Endpoints/EndpointSlice objects. A, C, and D do not describe how Service-to-Pod matching works.

---

**Q5.** A Service of type `NodePort` is created. Which statement is true?
A. It is only reachable from inside the cluster, like ClusterIP
B. It opens a static port on every node's IP in addition to providing a ClusterIP
C. It automatically provisions an external cloud load balancer
D. It creates a CNAME record pointing to an external DNS name

**Correct answer: B**
*Explanation:* NodePort exposes the Service on a static port (30000-32767) across every node's IP, while still also getting a ClusterIP. A describes ClusterIP behavior only. C describes LoadBalancer. D describes ExternalName.

---

**Q6.** What is the purpose of an `ExternalName` Service?
A. To load-balance traffic across Pods using a selector
B. To map a Service's DNS name to an external DNS name via a CNAME record, with no proxying or selector involved
C. To expose a static port on every node
D. To provision a cloud load balancer

**Correct answer: B**
*Explanation:* `ExternalName` is purely a DNS-level alias to an external name — no selector, no proxying, no Endpoints tracking (Section 4.2). A describes ClusterIP/NodePort/LoadBalancer's selector-based model. C describes NodePort. D describes LoadBalancer.

---

**Q7.** What object tracks the live, current list of Pod IPs matching a Service's selector?
A. ReplicaSet
B. Endpoints / EndpointSlice
C. ConfigMap
D. PersistentVolumeClaim

**Correct answer: B**
*Explanation:* Per Section 4.1 and 7, Endpoints (or the newer EndpointSlice) objects are continuously updated to reflect the current healthy Pods matching a Service's selector. A, C, and D are unrelated objects that don't track Service backend membership.

---

**Q8.** What DNS name format does every Service automatically receive via cluster DNS?
A. `<namespace>.<service-name>.pod.cluster.local`
B. `<service-name>.<namespace>.svc.cluster.local`
C. `<service-name>.cluster.svc.local`
D. Services do not get automatic DNS names; they must be manually registered

**Correct answer: B**
*Explanation:* Section 4.4 defines the standard predictable format `<service-name>.<namespace>.svc.cluster.local`, resolved automatically by CoreDNS. A and C scramble the field order. D is false — this is automatic, not manual.

---

**Q9.** Why does a mismatched `selector` between a Service and its target Pods cause requests to fail, even though the Pods show as `Running`?
A. Because `Running` Pods are automatically firewalled from all Services
B. Because the Service's Endpoints list will be empty — no Pods match the selector, so there are zero valid backends to route traffic to
C. Because mismatched selectors cause the Pods to crash
D. Because the Service will automatically delete itself

**Correct answer: B**
*Explanation:* This is the classic troubleshooting scenario (Sections 15, 16, 19's interview Q3) — the Service and ClusterIP still exist, but with no matching Pods, Endpoints is empty and there's nowhere to route traffic. A, C, and D describe behaviors that do not occur.

---

**Q10.** What is the difference between a Service's `port` and `targetPort` fields?
A. They must always be identical
B. `port` is what the Service listens on; `targetPort` is the port on the backing Pod that traffic is forwarded to — they can differ
C. `port` applies only to NodePort Services; `targetPort` applies only to ClusterIP
D. `targetPort` specifies which node the Pod runs on

**Correct answer: B**
*Explanation:* Per Section 15's common mistakes and interview Q2, these are independent and frequently differ (e.g., Service port 80 forwarding to container port 8080). A is a common but incorrect assumption. C and D misstate their scope/meaning.

---

**Q11.** Which statement about `kube-proxy` is TRUE?
A. It runs only on the control plane, not on worker nodes
B. It runs on every node and programs local network rules (iptables/IPVS/nftables) that implement Service traffic routing
C. It is responsible for scheduling Pods to nodes
D. It replaces the need for a Service object entirely

**Correct answer: B**
*Explanation:* Per Section 4.3, `kube-proxy` runs on every node, watching Services/Endpoints and programming the actual routing rules. A is false — it runs on every node, not just control plane. C describes kube-scheduler. D is false; kube-proxy implements Services, it doesn't replace them.

---

**Q12.** A LoadBalancer-type Service is created in a cluster with no cloud provider integration (e.g., a bare-metal or local cluster without a supporting controller). What is the most likely observed behavior?
A. The Service works identically to a fully external cloud load balancer
B. The Service's external IP remains `<pending>` indefinitely, since there is no cloud controller to provision an actual load balancer
C. Kubernetes automatically falls back to ClusterIP behavior with no external access at all
D. The API server rejects the Service creation outright

**Correct answer: B**
*Explanation:* `LoadBalancer` type relies on a cloud provider's integration/controller to actually provision an external LB; without one, the external IP field stays `<pending>` forever. A is false — no cloud, no LB. C is close but incorrect — the Service is still created as specified, just without external IP provisioning. D is false; the object is accepted, just never fully provisioned.

---

**Q13.** Why should `ClusterIP` be preferred by default over `LoadBalancer` for purely internal microservice-to-microservice communication?
A. `ClusterIP` provides better encryption
B. `LoadBalancer` incurs real cloud costs and unnecessary external exposure for traffic that never needs to leave the cluster
C. `ClusterIP` is the only type that supports label selectors
D. `LoadBalancer` cannot route to more than one Pod

**Correct answer: B**
*Explanation:* Per Section 14's best practices, minimizing exposed attack surface and cloud spend is the rationale — internal traffic doesn't need external exposure. A is not a real distinction. C is false — all selector-based types support selectors. D is false; LoadBalancer load-balances across all matching Pods just like the others.

---

**Q14.** In the chapter's restaurant analogy (Section 3), what do the individual Pods represent?
A. The stable order counter
B. The chefs, who rotate in and out while the counter (Service) address stays constant
C. The customers placing orders
D. The restaurant's fixed street address

**Correct answer: B**
*Explanation:* The analogy explicitly maps Pods to chefs who come and go, while the Service is the unchanging order counter routing to whichever chef is currently available. A and D describe the Service itself. C represents clients, not Pods.

---

**Q15.** What is the KCNA-relevant distinction between a Service and an Ingress (previewed in Section 17)?
A. They are functionally identical and interchangeable
B. A Service load-balances at L4 (TCP/UDP) for one set of Pods; an Ingress provides L7 (HTTP) routing rules typically sitting in front of multiple Services
C. An Ingress replaces the need for kube-proxy
D. A Service can only be used with StatefulSets, while Ingress is used with Deployments

**Correct answer: B**
*Explanation:* This is the explicit distinction drawn in Section 17's comparison table, foreshadowing Chapter 17's deeper coverage. A is false — they operate at different layers with different purposes. C and D misstate their relationship and scope.

---

**Q16.** A Service's `targetPort` is set to 8080, but the actual container inside the matching Pods listens on port 9090. What happens?
A. Kubernetes automatically detects and corrects the mismatch
B. Traffic forwarded to port 8080 will fail to reach the application, since the container isn't actually listening there
C. The Service silently falls back to `port` instead of `targetPort`
D. The Pod's container is automatically reconfigured to listen on 8080

**Correct answer: B**
*Explanation:* `targetPort` must match the port the container actually listens on (Section 15's common mistakes) — a mismatch here means traffic reaches the Pod's network namespace but finds nothing listening on that port. A, C, and D describe automatic-correction behaviors that do not exist.

---

**Q17.** Why is a headless Service (mentioned in Section 13, and detailed in Chapter 14) NOT assigned a ClusterIP?
A. Because headless Services are deprecated and no longer functional
B. Because its purpose is to provide direct, individual per-Pod DNS resolution rather than a single load-balanced virtual IP, which is what StatefulSets need for stable peer addressing
C. Because ClusterIPs are reserved exclusively for NodePort Services
D. Because headless Services do not support label selectors

**Correct answer: B**
*Explanation:* As covered in Chapter 14, `clusterIP: None` deliberately opts out of the single-VIP abstraction to instead expose individual Pod DNS entries — needed when clients must address a specific Pod. A is false — headless Services are a standard, supported feature. C and D are incorrect statements.

---

**Q18.** Using the chapter's type-scope memory trick ("Cluster → Node → Load-balancer," Section 18), which ordering correctly reflects narrowest to widest exposure scope?
A. LoadBalancer → NodePort → ClusterIP
B. ClusterIP (internal-only) → NodePort (per-node external) → LoadBalancer (fully external)
C. NodePort → ClusterIP → LoadBalancer
D. All three types have identical exposure scope

**Correct answer: B**
*Explanation:* This is the exact mnemonic ordering given in Section 18, moving from most restricted (internal-only) to most exposed (full external cloud LB). A reverses the order. C scrambles it. D contradicts the entire comparison table in Section 17.

---

**Q19.** A long-lived TCP connection to a ClusterIP Service appears to "stick" to a single backing Pod rather than being re-balanced across all matching Pods on every new packet. Why?
A. This indicates the Service is broken and must be recreated
B. Depending on kube-proxy mode and connection type, existing long-lived connections are typically routed to one Pod for the connection's duration rather than being rebalanced mid-connection — this is expected, not a bug
C. ClusterIP Services do not support long-lived connections at all
D. This only happens with ExternalName Services

**Correct answer: B**
*Explanation:* Per Section 15's common mistakes, load-balancing granularity depends on protocol and kube-proxy mode — connection-level "stickiness" for long-lived connections is expected behavior, not a malfunction. A and C are incorrect — this is normal, documented behavior. D misapplies the scenario to the wrong Service type (ExternalName has no proxying at all).

---

**Q20.** A team wants Pod A to always be able to reach "the database" using a fixed internal name, regardless of whether the database runs inside the cluster or is an external managed service that might migrate providers later. Which Service type best supports this abstraction if the database is external?
A. ClusterIP, pointed at a selector matching internal Pods
B. ExternalName, providing a consistent internal DNS alias regardless of the actual external endpoint
C. NodePort, opened on every node
D. LoadBalancer, provisioning a new cloud load balancer

**Correct answer: B**
*Explanation:* Per Section 13's real-world examples, `ExternalName` is precisely designed for this use case — a stable internal name aliasing to an external target that can change without affecting client configuration. A requires the database to run as cluster Pods, which contradicts the scenario. C and D are for exposing internal Pods externally, the opposite direction of this use case.

---

## 21. Chapter Summary (One-Page Revision Sheet)

- A **Service** gives a stable virtual IP and DNS name to a dynamic, changing set of Pods, discovered continuously via **label selectors** and tracked in **Endpoints/EndpointSlice** objects.
- Four Service types: **ClusterIP** (internal-only, default), **NodePort** (static port on every node), **LoadBalancer** (external cloud LB), **ExternalName** (DNS alias, no proxying).
- **kube-proxy** on every node implements the actual traffic-routing rules (iptables/IPVS/nftables).
- Common pitfall: mismatched selector labels between Service and Pods → empty Endpoints → no traffic reaches any Pod, even though everything looks "Running."

---

### Chapter Completion Checklist

1. **Topics covered:** Service abstraction and motivation, four Service types, label-selector-based discovery, kube-proxy's role, DNS naming.
2. **KCNA objectives completed:** Service discovery and stable networking abstraction over ephemeral Pods.
3. **Remaining objectives:** L7 routing and external access patterns — Ingress and the Gateway API (Chapter 17).
4. **Suggested revision checklist:** Recite all four Service types and their exposure scope from memory; explain the port vs targetPort distinction; explain why mismatched selectors cause empty Endpoints.
5. **Suggested hands-on exercises:** Complete Lab 2 (Service survives Pod replacement) — this is the single clearest demonstration of *why* Services exist at all.
6. **Related chapters:** Previous: [15-Jobs-and-CronJobs](../15-Jobs-and-CronJobs/README.md). Next: [17-Ingress-and-Gateway-API](../17-Ingress-and-Gateway-API/README.md) — HTTP-aware routing built on top of Services.
