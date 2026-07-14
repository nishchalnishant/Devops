# 18 — Networking

## 1. Learning Objectives

By the end of this chapter you will be able to:

- Explain the four fundamental Kubernetes networking requirements ("the Kubernetes networking model").
- Explain the role of the Container Network Interface (CNI) and how CNI plugins implement Pod networking.
- Explain how cluster DNS (CoreDNS) resolves Service and Pod names.
- Explain how NetworkPolicies restrict traffic between Pods.
- Read and write a basic NetworkPolicy manifest.

**KCNA objectives covered:** Cloud Native Architecture domain — the underlying cluster networking model that Services (Chapter 16) and Ingress/Gateway API (Chapter 17) are built on top of.

---

## 2. Historical Background

Container networking before Kubernetes was fragmented — different container runtimes and orchestrators each invented their own incompatible ways of wiring up container network interfaces, making it hard to mix networking vendors or reuse networking code across tools. The **Container Network Interface (CNI)** specification emerged (originally from CoreOS, later adopted by the CNCF) to standardize how container runtimes and orchestrators hand off network setup to pluggable providers. Kubernetes adopted CNI as its standard networking plugin interface, and layered its own consistent **networking model** (Section 4.1) on top, along with **NetworkPolicies** for traffic restriction and **CoreDNS** for name resolution.

---

## 3. Motivation: Why Does Kubernetes Need a Defined Networking Model?

**Analogy — The City's Postal System:**
Imagine a city where every building had a completely different, incompatible addressing scheme — some numbered by street, some by GPS coordinates, some with no consistent system at all. Mail delivery would be chaos. Real cities standardize: every address is reachable by a consistent scheme, and anyone can find anyone else without needing building-specific knowledge. Kubernetes networking is that citywide postal standard: **every Pod gets its own IP, and every Pod can reach every other Pod's IP directly, without NAT** — a simple, consistent, city-wide addressing rule that all networking plugins must honor, regardless of which specific "postal company" (CNI plugin) is running the roads underneath.

### 3.1 How Was This Solved Before Kubernetes?

Various container platforms wired up container networking in incompatible, often manually-scripted ways (e.g., custom Docker bridge/NAT configurations), making networking behavior inconsistent and difficult to reason about or swap between environments.

### 3.2 How Kubernetes Solves It

Kubernetes defines a strict, simple **networking model** (Section 4.1) that any CNI plugin must implement, guaranteeing all cluster networking behaves consistently regardless of the underlying plugin (Calico, Cilium, Flannel, etc.). **NetworkPolicies** then let cluster operators layer restrictions on top of this otherwise fully-open-by-default model, and **CoreDNS** provides consistent name resolution across the whole model.

---

## 4. Core Concepts

### 4.1 The Kubernetes Networking Model (Four Fundamental Rules)

| Rule | Meaning |
|---|---|
| Every Pod gets its own IP address | No shared IP with the host node; each Pod is a fully addressable network entity |
| Pods can communicate with all other Pods without NAT | Pod-to-Pod traffic across nodes must work exactly like Pod-to-Pod traffic on the same node — no address translation in between |
| Nodes can communicate with all Pods without NAT | Node-level agents (e.g., kubelet) can reach any Pod IP directly |
| The IP a Pod sees itself as is the same IP others see it as | No hidden internal-vs-external IP confusion — consistent addressing from every viewpoint |

### 4.2 CNI (Container Network Interface)

**Definition:** CNI is a specification and set of libraries for configuring network interfaces in Linux containers. When a Pod is created, the **kubelet** (Chapter 08) invokes the configured **CNI plugin**, which allocates an IP address, creates the necessary virtual network interfaces, and wires the Pod into the cluster's overall network — implementing the four rules in Section 4.1.

| Popular CNI Plugin | Notable Characteristic |
|---|---|
| Flannel | Simple overlay network, easy to set up |
| Calico | Supports NetworkPolicy enforcement, BGP-based routing option |
| Cilium | eBPF-based, high performance, deep observability and security features |

### 4.3 NetworkPolicy

**Definition:** By default, Kubernetes networking is **fully open** — any Pod can talk to any other Pod, cluster-wide, with no restriction. A **NetworkPolicy** is a namespaced object that restricts this by defining allowed ingress/egress traffic rules for a selected set of Pods, based on label selectors, namespaces, or IP blocks. NetworkPolicies require a CNI plugin that actually supports enforcing them (not all do — e.g., Flannel alone does not, while Calico and Cilium do).

### 4.4 Cluster DNS (CoreDNS)

CoreDNS runs as a cluster add-on (typically as a Deployment in `kube-system`) providing:
- Service DNS names (`<service>.<namespace>.svc.cluster.local`), as introduced in Chapter 16 Section 4.4.
- Optional per-Pod DNS names for Headless Services (Chapter 14 Section 4.2).
- Resolution of external DNS names, typically forwarding upstream to outside resolvers.

---

## 5. Internal Working

```
1. A new Pod is scheduled onto a node
        ↓
2. kubelet invokes the node's configured CNI plugin (e.g., Calico)
   to set up the Pod's network namespace
        ↓
3. The CNI plugin allocates a Pod IP from the cluster's Pod CIDR
   range, creates a virtual ethernet pair connecting the Pod's
   network namespace to the node, and configures routing so this
   Pod is reachable from any other Pod/node in the cluster
        ↓
4. If NetworkPolicies exist matching this Pod's labels, the CNI
   plugin's policy engine programs the necessary rules (e.g., via
   eBPF or iptables) to enforce allowed/denied traffic
        ↓
5. CoreDNS resolves any Service or Pod DNS name lookups this Pod
   performs, returning the appropriate ClusterIP or Pod IP
```

---

## 6. Architecture

```
   Node A                                    Node B
┌────────────────────┐             ┌────────────────────┐
│  Pod A (10.244.1.5) │             │  Pod C (10.244.2.7) │
│  Pod B (10.244.1.6) │             │  Pod D (10.244.2.8) │
└──────────┬──────────┘             └──────────┬──────────┘
           │                                          │
           └─────────── CNI-managed overlay/routed ───┘
                     network (no NAT, flat L3 reachability)

        Every Pod IP reachable from every other Pod IP,
             regardless of which node hosts them

                  ┌────────────────────┐
                  │  CoreDNS (kube-system)  │
                  │  resolves Service/Pod   │
                  │  DNS names for all Pods  │
                  └────────────────────┘
```

---

## 7. Component Breakdown

| Piece | Role |
|---|---|
| CNI plugin | Implements the actual Pod networking (IP allocation, routing, NAT-free reachability) |
| NetworkPolicy | Namespaced object restricting allowed traffic between Pods |
| CoreDNS | Cluster DNS add-on resolving Service/Pod names |
| kubelet | Invokes the CNI plugin when a Pod is created (Chapter 08) |

---

## 8. Important Terminology

| Term | Meaning |
|---|---|
| CNI (Container Network Interface) | Specification for pluggable container network configuration |
| Pod CIDR | The IP address range Pods are allocated from |
| NetworkPolicy | Object restricting allowed ingress/egress traffic for selected Pods |
| CoreDNS | Cluster DNS add-on providing Service/Pod name resolution |
| Overlay network | A virtual network layered on top of physical networking (e.g., via VXLAN) used by some CNI plugins |

---

## 9. YAML Deep Dive

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-backend
  namespace: default
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
    - Ingress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: frontend
      ports:
        - protocol: TCP
          port: 8080
```

This policy: selects Pods labeled `app: backend`, and allows **only** ingress traffic from Pods labeled `app: frontend` on TCP port 8080 — all other ingress traffic to `backend` Pods is denied once any NetworkPolicy selects them.

---

## 10. kubectl Commands

| Command | Purpose | Example |
|---|---|---|
| `kubectl get networkpolicy` | List NetworkPolicies | `kubectl get networkpolicy` |
| `kubectl describe networkpolicy <name>` | Show policy rules in detail | `kubectl describe networkpolicy allow-frontend-to-backend` |
| `kubectl get pods -o wide` | Show Pod IPs and the node they're on | `kubectl get pods -o wide` |
| `kubectl exec <pod> -- nslookup <service>` | Test DNS resolution from inside a Pod | `kubectl exec frontend-0 -- nslookup backend-svc` |
| `kubectl get pods -n kube-system -l k8s-app=kube-dns` | Check CoreDNS Pod health | `kubectl get pods -n kube-system -l k8s-app=kube-dns` |

---

## 11. Hands-on Examples

**Lab 1 — Confirm default open networking (no policy applied yet):**
```bash
kubectl exec frontend-pod -- curl backend-svc:8080
# Succeeds — by default, all Pods can reach all other Pods
```

**Lab 2 — Apply a NetworkPolicy and observe traffic restriction:**
```bash
kubectl apply -f allow-frontend-to-backend.yaml
kubectl exec frontend-pod -- curl backend-svc:8080   # still succeeds
kubectl exec other-pod -- curl backend-svc:8080      # now blocked/times out
```

**Lab 3 — Test DNS resolution for a Service:**
```bash
kubectl exec frontend-pod -- nslookup backend-svc.default.svc.cluster.local
# Resolves to the Service's stable ClusterIP (Chapter 16)
```

---

## 12. Internal Flow

See Section 5 — Kubernetes networking layers three concerns: a **baseline, NAT-free, flat Pod-to-Pod reachability model** implemented by the CNI plugin; an **optional restriction layer** (NetworkPolicy) that the same CNI plugin enforces if it supports it; and a **naming layer** (CoreDNS) that resolves human-friendly Service/Pod names into the IPs this whole model makes reachable.

---

## 13. Real-World Examples

1. **Cloud-managed Kubernetes clusters** (EKS, AKS, GKE) each ship a default CNI plugin (or integrate with the cloud's native VPC networking) implementing the four-rule model automatically.
2. **Zero-trust security postures** use NetworkPolicies extensively to enforce "default deny" between namespaces, only explicitly allowing known, required traffic paths.
3. **Multi-tenant clusters** use NetworkPolicies to isolate tenant namespaces from each other, preventing one tenant's Pods from ever reaching another's.
4. **Service meshes** (Chapter 23) build additional L7 traffic control, mTLS, and observability on top of the baseline CNI networking model described here.
5. **eBPF-based CNI plugins** (Cilium) provide deep network observability and highly efficient policy enforcement without traditional iptables overhead, popular in large-scale, performance-sensitive clusters.

---

## 14. Best Practices

- Apply a **default-deny** NetworkPolicy per namespace, then explicitly allow only required traffic — safer than an allow-list built reactively after incidents.
- Choose a CNI plugin that supports NetworkPolicy enforcement if security segmentation matters (not all plugins do).
- Keep Pod CIDR ranges large enough to avoid IP exhaustion as the cluster scales — resizing after the fact is disruptive.
- Regularly test DNS resolution and NetworkPolicy behavior as part of cluster health checks — networking issues are often silent until they cause outages.

---

## 15. Common Mistakes

- Assuming NetworkPolicies are enforced by Kubernetes itself — enforcement actually depends entirely on the CNI plugin supporting it; a policy applied with a non-enforcing CNI plugin silently does nothing.
- Forgetting that once **any** NetworkPolicy selects a Pod for a given traffic direction (ingress/egress), all traffic in that direction is denied by default except what's explicitly allowed — a common source of unexpected outages when adding a policy.
- Not accounting for DNS traffic in a NetworkPolicy's egress rules, breaking a Pod's ability to resolve names at all.
- Confusing Pod CIDR (Pod IP range) with Service CIDR (ClusterIP range) — they are separate address spaces.

---

## 16. Troubleshooting

| Symptom | Likely Cause | Debugging Commands | Fix |
|---|---|---|---|
| Pods across nodes can't reach each other | CNI plugin misconfigured or not running | `kubectl get pods -n kube-system`, check CNI plugin Pods | Fix/restart CNI plugin |
| NetworkPolicy has no effect | CNI plugin doesn't support NetworkPolicy enforcement | Check CNI plugin documentation/capabilities | Switch to an enforcing CNI plugin (e.g., Calico, Cilium) |
| DNS lookups fail from within Pods | CoreDNS Pods unhealthy, or egress NetworkPolicy blocking DNS | `kubectl get pods -n kube-system -l k8s-app=kube-dns`, `kubectl logs` | Fix CoreDNS Pods; allow DNS (port 53) in NetworkPolicy egress rules |
| Traffic unexpectedly blocked after applying a policy | Default-deny behavior triggered by selecting Pods without allowing all needed traffic | `kubectl describe networkpolicy` | Add explicit allow rules for all legitimately required traffic |

---

## 17. Comparison Tables

**CNI Plugins (recap of Section 4.2):**

| Plugin | NetworkPolicy Support | Notable Trait |
|---|---|---|
| Flannel | No (by itself) | Simplicity |
| Calico | Yes | BGP routing option, mature policy engine |
| Cilium | Yes | eBPF-based, high performance, deep observability |

**NetworkPolicy default-deny behavior:**

| State | Effect |
|---|---|
| No NetworkPolicy selects a Pod | All traffic allowed (open by default) |
| At least one NetworkPolicy selects a Pod for ingress | Only explicitly allowed ingress traffic permitted; rest denied |
| At least one NetworkPolicy selects a Pod for egress | Only explicitly allowed egress traffic permitted; rest denied |

---

## 18. Memory Tricks

- **"Networking model = citywide postal standard"** — every Pod has its own address, reachable directly, no translation games.
- **"CNI plugs in the pipes, NetworkPolicy adds the locks, CoreDNS prints the phonebook."**
- NetworkPolicy mnemonic: **"Selected = default deny."** The moment a Pod is selected by any policy in a direction, that direction switches from open to allow-listed.

---

## 19. Interview Questions

**Easy:**
1. What are the four fundamental rules of the Kubernetes networking model?
   *Expected answer:* (1) Every Pod gets its own IP address. (2) Pods can communicate with all other Pods without NAT. (3) Nodes can communicate with all Pods without NAT. (4) The IP a Pod sees itself as is the same IP others see it as — consistent addressing from every viewpoint.

**Medium:**
2. Why doesn't applying a NetworkPolicy always restrict traffic as expected?
   *Expected answer:* NetworkPolicy enforcement is not implemented by Kubernetes itself — it depends entirely on the cluster's CNI plugin supporting and enforcing NetworkPolicy objects. Some CNI plugins (like plain Flannel) do not enforce NetworkPolicies at all, meaning applying one has no actual effect on traffic even though the object is accepted by the API server. Confirming the CNI plugin's NetworkPolicy support is a required first troubleshooting step.

**Hard:**
3. A team applies a NetworkPolicy to their `backend` Pods intending only to allow traffic from `frontend` Pods on port 8080. Shortly after, they notice their backend Pods can no longer resolve any DNS names, breaking unrelated functionality. Explain what likely happened and how to fix it.
   *Expected answer:* The moment a NetworkPolicy selects a Pod for a traffic direction — in this case, if the policy included egress rules (or a `policyTypes` list including `Egress`) — all egress traffic from that Pod becomes denied by default except what is explicitly allowed. If the policy didn't explicitly allow outbound traffic to CoreDNS (typically UDP/TCP port 53), the backend Pods would lose the ability to perform any DNS resolution, breaking name-based lookups for both internal Services and external hosts alike. The fix is to add an explicit egress rule allowing traffic to the CoreDNS Pods (or the `kube-dns` Service) on port 53, alongside the intended ingress-restriction rule — remembering that ingress and egress restrictions are independent, and DNS is easy to overlook since it's not part of the "obvious" application traffic being restricted.

---

## 20. KCNA Practice Questions

**Q1.** Which of the following is one of Kubernetes's four fundamental networking model rules?
A. Pods share the same IP address as their host node
B. Pods can communicate with all other Pods without NAT
C. Only Pods in the same namespace can communicate
D. All traffic must pass through an Ingress Controller

**Correct answer: B**
*Explanation:* NAT-free Pod-to-Pod reachability is one of the four core rules. A is false — every Pod gets its own IP, distinct from the node's. C is false — by default, all Pods across all namespaces can communicate freely. D describes Ingress (Chapter 17), unrelated to the base networking model.

---

**Q2.** What is the role of a CNI plugin in Kubernetes?
A. To schedule Pods onto nodes
B. To implement Pod networking, including IP allocation and NAT-free reachability
C. To store cluster configuration data
D. To manage container image builds

**Correct answer: B**
*Explanation:* CNI plugins implement the actual networking rules described in the Kubernetes networking model. A describes kube-scheduler (Chapter 07). C describes etcd (Chapter 07). D is unrelated to networking entirely.

---

**Q3.** By default, before any NetworkPolicy is applied, how is traffic between Pods in a Kubernetes cluster?
A. Fully blocked
B. Fully open — any Pod can reach any other Pod
C. Restricted to same-namespace communication only
D. Restricted to same-node communication only

**Correct answer: B**
*Explanation:* Kubernetes networking is open by default; NetworkPolicies are an opt-in restriction layer. A, C, and D all misdescribe the default (fully open) behavior.

---

**Q4.** What must be true for a NetworkPolicy to actually take effect?
A. Nothing extra — Kubernetes enforces all NetworkPolicies natively
B. The cluster's CNI plugin must support NetworkPolicy enforcement
C. An Ingress Controller must be installed
D. The Pods must be part of a StatefulSet

**Correct answer: B**
*Explanation:* NetworkPolicy enforcement depends on CNI plugin support (e.g., Calico, Cilium); Kubernetes itself does not enforce it natively. A is false. C and D are unrelated prerequisites.

---

**Q5.** What component provides DNS resolution for Kubernetes Service and Pod names?
A. kube-proxy
B. CoreDNS
C. etcd
D. kubelet

**Correct answer: B**
*Explanation:* CoreDNS is the cluster DNS add-on resolving Service/Pod names. kube-proxy (A) implements Service traffic routing (Chapter 16), not DNS. etcd (C) is the cluster data store (Chapter 07). kubelet (D) manages Pod lifecycle on a node (Chapter 08).

---

**Q6.** Which of the four Kubernetes networking model rules ensures no "internal vs. external IP" confusion?
A. Every Pod gets its own IP address
B. The IP a Pod sees itself as is the same IP others see it as
C. Nodes can communicate with all Pods without NAT
D. Pods can communicate with all other Pods without NAT

**Correct answer: B**
*Explanation:* Per Section 4.1, this specific rule guarantees consistent addressing from every viewpoint, with no hidden translation. A, C, and D are the other three rules, addressing different aspects of the model.

---

**Q7.** What does the kubelet do when a new Pod is scheduled onto a node, per the Internal Working flow (Section 5)?
A. It directly assigns the Pod's IP itself, without involving any other component
B. It invokes the node's configured CNI plugin to set up the Pod's network namespace
C. It creates a NetworkPolicy automatically for the new Pod
D. It updates CoreDNS records manually

**Correct answer: B**
*Explanation:* Per Section 5, kubelet delegates the actual network setup work to the CNI plugin. A is false — the CNI plugin allocates the IP, not kubelet directly. C and D are not part of this handoff.

---

**Q8.** Which CNI plugin is described as eBPF-based, offering high performance and deep observability?
A. Flannel
B. Calico
C. Cilium
D. CoreDNS

**Correct answer: C**
*Explanation:* Section 4.2's table specifically attributes eBPF-based high performance and observability to Cilium. A is a simple overlay network. B supports NetworkPolicy and BGP routing but isn't described as eBPF-based here. D is unrelated — it's the DNS add-on, not a CNI plugin.

---

**Q9.** In the YAML Deep Dive example (Section 9), what traffic does the `allow-frontend-to-backend` NetworkPolicy permit?
A. All egress traffic from `backend` Pods to anywhere
B. Only ingress traffic from Pods labeled `app: frontend` to `backend` Pods on TCP port 8080
C. All ingress traffic to any Pod in the `default` namespace
D. Only traffic between nodes, not Pods

**Correct answer: B**
*Explanation:* The policy's `podSelector` targets `app: backend`, and its single ingress rule allows only `app: frontend` sources on port 8080 — all other ingress to `backend` Pods is denied once selected. A misdescribes the direction (this policy only defines `Ingress`, no egress rule). C is far broader than the actual selector. D misdescribes the scope entirely.

---

**Q10.** Why is Pod CIDR exhaustion a real operational risk mentioned in Best Practices (Section 14)?
A. Because resizing the Pod CIDR range after cluster creation is disruptive, so it should be sized generously upfront
B. Because Pod CIDR ranges automatically double every time a new node joins
C. Because Kubernetes automatically deletes the oldest Pods when the range is exhausted
D. Because Pod CIDR is irrelevant to cluster scaling

**Correct answer: A**
*Explanation:* Section 14 explicitly calls out sizing the Pod CIDR generously upfront since resizing after the fact is disruptive as the cluster scales. B, C, and D describe behaviors that do not occur.

---

**Q11.** What is an "overlay network," as defined in the chapter's terminology (Section 8)?
A. A physical, dedicated network cable installed for each Pod
B. A virtual network layered on top of physical networking (e.g., via VXLAN), used by some CNI plugins
C. A synonym for NetworkPolicy
D. The DNS resolution layer provided by CoreDNS

**Correct answer: B**
*Explanation:* Section 8 defines overlay networks precisely this way — a virtual layer atop physical infrastructure, as used by plugins like Flannel. A is physically nonsensical for this context. C and D confuse unrelated concepts.

---

**Q12.** A zero-trust security posture (Section 13) typically uses NetworkPolicies in which way?
A. To enforce "default deny" between namespaces, explicitly allowing only required traffic paths
B. To disable all networking entirely
C. To replace CoreDNS
D. To allow all traffic between all namespaces without restriction

**Correct answer: A**
*Explanation:* Section 13 explicitly describes this real-world use case — layering deny-by-default segmentation and only opening explicitly required paths. B, C, and D contradict both the concept of zero-trust and how NetworkPolicies function.

---

**Q13.** What is the relationship between Service meshes (Chapter 23) and the baseline CNI networking model described in this chapter, per Section 13?
A. Service meshes replace CNI plugins entirely
B. Service meshes build additional L7 traffic control, mTLS, and observability on top of the baseline CNI networking model
C. Service meshes are a type of CNI plugin
D. Service meshes are unrelated to networking

**Correct answer: B**
*Explanation:* Section 13 positions service meshes as an additional layer atop the base CNI model, not a replacement for it. A and C conflate distinct layers. D is directly contradicted by the chapter's own text.

---

**Q14.** Why does confusing Pod CIDR with Service CIDR (Section 15's common mistakes) cause problems?
A. They are actually the same address space, so confusing them has no real effect
B. They are separate address spaces (Pod IPs vs ClusterIPs), and conflating them leads to networking misconfigurations and troubleshooting confusion
C. Service CIDR only applies to StatefulSets
D. Pod CIDR only applies to Ingress objects

**Correct answer: B**
*Explanation:* Section 15 explicitly warns these are distinct, separately allocated address ranges — mixing them up is a common source of misdiagnosis. A is false — they are deliberately separate. C and D misattribute these concepts to unrelated objects.

---

**Q15.** A Pod can no longer resolve any DNS names shortly after a NetworkPolicy with egress rules is applied to it. Per the troubleshooting table (Section 16) and hard interview Q3, what is the most likely fix?
A. Delete CoreDNS entirely
B. Add an explicit egress rule allowing traffic to CoreDNS (or the `kube-dns` Service) on port 53
C. Switch the Pod to use a different Pod CIDR
D. Convert the NetworkPolicy into an Ingress object

**Correct answer: B**
*Explanation:* Once a policy selects a Pod for egress, only explicitly allowed egress traffic is permitted — DNS (port 53) is easy to forget and must be explicitly allowed. A would make DNS resolution impossible cluster-wide, the opposite of a fix. C and D are irrelevant to this symptom.

---

**Q16.** Per the comparison table in Section 17, which CNI plugin(s) support NetworkPolicy enforcement?
A. Flannel only
B. Calico and Cilium
C. None of the listed plugins support it
D. All three listed plugins support it equally well, including Flannel

**Correct answer: B**
*Explanation:* Section 17's table marks Calico and Cilium as supporting NetworkPolicy enforcement, while Flannel (by itself) does not. A, C, and D all misstate the table's actual content.

---

**Q17.** Using the memory trick "CNI plugs in the pipes, NetworkPolicy adds the locks, CoreDNS prints the phonebook" (Section 18), which analogy corresponds to name resolution?
A. Pipes (CNI)
B. Locks (NetworkPolicy)
C. Phonebook (CoreDNS)
D. None of the above — DNS isn't covered by this mnemonic

**Correct answer: C**
*Explanation:* The mnemonic explicitly maps CoreDNS to "prints the phonebook" — i.e., name-to-address resolution. A maps to raw connectivity (CNI). B maps to traffic restriction (NetworkPolicy). D is false; the mnemonic does cover all three.

---

**Q18.** Following the "Selected = default deny" mnemonic (Section 18), what happens to a Pod's ingress traffic the moment ANY NetworkPolicy selects it for ingress?
A. Nothing changes until a second policy is applied
B. All ingress traffic to that Pod becomes denied by default except what is explicitly allowed by a matching rule
C. All ingress traffic is permanently blocked with no way to allow any of it
D. The Pod is automatically deleted

**Correct answer: B**
*Explanation:* This is the exact default-deny-once-selected behavior described in Sections 15, 17, and 18 — selection switches the default from open to allow-listed, not to a total, permanent block. A, C, and D misstate this mechanism.

---

**Q19.** In the postal system analogy (Section 3), what does "every address is reachable by a consistent scheme, and anyone can find anyone else without needing building-specific knowledge" map to in Kubernetes?
A. NetworkPolicy's default-deny behavior
B. The Kubernetes networking model's consistent, NAT-free Pod addressing that all CNI plugins must honor
C. CoreDNS's upstream forwarding for external names
D. The Ingress Controller's host/path routing rules

**Correct answer: B**
*Explanation:* The analogy is explicitly introduced to explain why Kubernetes enforces one consistent addressing model regardless of the underlying CNI plugin. A, C, and D describe different, unrelated mechanisms covered elsewhere in the chapter.

---

**Q20.** A cluster administrator wants to verify whether NetworkPolicy enforcement is actually working after installing a new CNI plugin. Which best practice from Section 14 supports this?
A. Assume enforcement works automatically since the NetworkPolicy object was accepted by the API server
B. Regularly test DNS resolution and NetworkPolicy behavior as part of cluster health checks, since networking issues are often silent until they cause outages
C. Deploy a Service mesh instead of testing directly
D. Skip testing since all CNI plugins behave identically

**Correct answer: B**
*Explanation:* Section 14 explicitly recommends ongoing testing of DNS and NetworkPolicy behavior, since a non-enforcing CNI plugin will silently accept but ignore NetworkPolicy objects. A is precisely the false assumption Section 15 warns against. C and D are irrelevant or false alternatives.

---

## 21. Chapter Summary (One-Page Revision Sheet)

- Kubernetes defines a strict **networking model**: every Pod gets its own IP, and Pod-to-Pod / Node-to-Pod communication works without NAT, with consistent addressing from every viewpoint.
- **CNI plugins** (Flannel, Calico, Cilium) implement this model; different plugins offer different tradeoffs (simplicity vs NetworkPolicy support vs performance/observability).
- Networking is **open by default**; **NetworkPolicy** objects add opt-in traffic restriction — but only if the CNI plugin supports enforcing them, and once a Pod is selected in a direction, unlisted traffic in that direction is denied (easy to accidentally break DNS).
- **CoreDNS** resolves Service and Pod DNS names cluster-wide.

---

### Chapter Completion Checklist

1. **Topics covered:** The four-rule Kubernetes networking model, CNI plugins, NetworkPolicy default-deny behavior, CoreDNS.
2. **KCNA objectives completed:** Cluster networking fundamentals underpinning Services and Ingress/Gateway API.
3. **Remaining objectives:** Storage — volumes, PersistentVolumes, PersistentVolumeClaims, StorageClasses (Chapter 19).
4. **Suggested revision checklist:** Recite the four networking model rules from memory; explain why NetworkPolicy enforcement depends on the CNI plugin; explain the "selected = default deny" NetworkPolicy behavior.
5. **Suggested hands-on exercises:** Complete Lab 2 (apply a NetworkPolicy and observe restriction) — directly demonstrates default-deny-once-selected behavior.
6. **Related chapters:** Previous: [17-Ingress-and-Gateway-API](../17-Ingress-and-Gateway-API/README.md). Next: [19-Storage](../19-Storage/README.md) — how Pods get durable, persistent storage.
