# 20 — Scheduling

## 1. Learning Objectives

By the end of this chapter you will be able to:

- Explain the role of kube-scheduler and its two-phase decision process (filtering and scoring).
- Explain node affinity/anti-affinity, Pod affinity/anti-affinity, taints and tolerations, and resource requests/limits as scheduling inputs.
- Explain how a Pod can be left `Pending` due to scheduling constraints.
- Read and write scheduling-related fields in a Pod manifest.

**KCNA objectives covered:** Cloud Native Architecture domain — Kubernetes scheduling internals.

---

## 2. Historical Background

Before container orchestration, placing workloads onto specific machines was largely a manual or script-driven task — an operator decided which server ran which application, often based on tribal knowledge of capacity and hardware quirks. As clusters grew to hundreds or thousands of nodes running many workloads with varying resource needs, manual placement became impossible to do well — humans could not track real-time resource availability, workload constraints, and failure-domain spreading across that many machines. Kubernetes introduced **kube-scheduler**, a control plane component (first introduced in Chapter 07) dedicated entirely to automatically and continuously deciding the best node for each new Pod.

---

## 3. Motivation: Why Does Kubernetes Need a Scheduler?

**Analogy — The Airport Gate Assignment System:**
Imagine an airport with hundreds of incoming flights and dozens of gates, each with different characteristics (size, proximity to customs, availability). Manually assigning gates would be slow and error-prone — you'd need someone tracking every gate's status in real time. Airports instead use automated gate-assignment systems that continuously match flights to the best available gate based on rules (aircraft size, connection times, terminal proximity). Kubernetes's **kube-scheduler** does the same for Pods: it continuously matches unscheduled Pods to the best available node based on rules (available resources, affinity/anti-affinity, taints/tolerations) — without a human manually picking a machine for every workload.

### 3.1 How Was This Solved Before Kubernetes?

Operators manually chose which physical or virtual machine ran a given application, or used simple, static rules (e.g., round-robin) without accounting for real-time resource availability or workload-specific placement needs.

### 3.2 Why Was That Insufficient?

Manual or static placement doesn't scale to large, dynamic clusters where node capacity, Pod resource needs, and constraints (e.g., "these two Pods must not share a node," "this Pod needs a GPU node") change constantly — it wastes capacity, risks overloading nodes, and can't be done fast enough at scale.

### 3.3 How Kubernetes Solves It

Kubernetes's **kube-scheduler** watches for newly created Pods with no assigned node, and for each one, runs a **filtering** phase (eliminating nodes that can't run the Pod) followed by a **scoring** phase (ranking remaining nodes to pick the best one) — fully automated, continuous, and based on declarative rules the user or platform team defines.

---

## 4. Core Concepts

### 4.1 The Two-Phase Scheduling Decision

| Phase | Purpose |
|---|---|
| Filtering (Predicates) | Eliminate nodes that cannot run the Pod at all (insufficient resources, taint without matching toleration, node selector mismatch, etc.) |
| Scoring (Priorities) | Rank the remaining feasible nodes and pick the highest-scoring one (e.g., preferring nodes with more free resources, or better affinity match) |

### 4.2 Resource Requests and Limits

**Definition:** Each container can declare `resources.requests` (the minimum CPU/memory it needs — used by the scheduler to filter nodes with insufficient capacity) and `resources.limits` (the maximum it's allowed to use — enforced at runtime, not used for scheduling decisions).

### 4.3 Node Affinity / Anti-Affinity

**Definition:** Rules that attract (affinity) or repel (anti-affinity) Pod placement relative to **node labels** (e.g., "schedule only on nodes labeled `disktype=ssd`"). Comes in `requiredDuringSchedulingIgnoredDuringExecution` (hard rule) and `preferredDuringSchedulingIgnoredDuringExecution` (soft preference) variants.

### 4.4 Pod Affinity / Anti-Affinity

**Definition:** Rules that attract or repel Pod placement relative to **other Pods'** labels (e.g., "schedule this Pod on the same node as Pods labeled `app=cache`" for affinity, or "never schedule two Pods labeled `app=web` on the same node" for anti-affinity — useful for spreading replicas across failure domains).

### 4.5 Taints and Tolerations

**Definition:** A **taint** applied to a node repels Pods from being scheduled there unless the Pod has a matching **toleration**. This is the inverse mechanism of affinity — instead of Pods attracting to nodes, nodes actively repel Pods by default. Commonly used to dedicate nodes to specific workloads (e.g., GPU nodes tainted so only GPU-requiring Pods tolerate and land there).

---

## 5. Internal Working

```
1. A new Pod is created with no assigned node (spec.nodeName is empty)
        ↓
2. kube-scheduler notices the unscheduled Pod (via watch on the API server)
        ↓
3. Filtering phase: kube-scheduler evaluates every node against the
   Pod's requirements — resource requests, node selectors/affinity,
   taints/tolerations, port availability — discarding infeasible nodes
        ↓
4. Scoring phase: remaining feasible nodes are scored using multiple
   weighted priority functions (e.g., least resource usage after
   placement, spreading across zones, affinity preference match)
        ↓
5. The highest-scoring node is selected; kube-scheduler writes the
   binding (sets Pod's spec.nodeName) via the API server
        ↓
6. The kubelet on that node observes the newly bound Pod and starts it
   (Chapter 08)
```

---

## 6. Architecture

```
                     ┌────────────────────┐
                     │   kube-scheduler     │
                     └──────────┬──────────┘
                                │  watches for unscheduled Pods
                                ▼
                     ┌────────────────────┐
                     │   API Server (etcd)  │
                     └──────────┬──────────┘
                                │
              ┌─────────────────┼─────────────────┐
              ▼                                        ▼
     ┌─────────────────┐                    ┌─────────────────┐
     │  Node A (feasible) │                    │  Node B (tainted,  │
     │  Filtering: PASS    │                    │  no toleration)     │
     │  Scoring: 8/10       │                    │  Filtering: FAIL     │
     └─────────────────┘                    └─────────────────┘
              │
              ▼  (highest score among feasible nodes)
       Pod bound to Node A
```

---

## 7. Component Breakdown

| Component | Role |
|---|---|
| kube-scheduler | Control plane component that assigns Pods to nodes (Chapter 07) |
| Filtering plugins | Eliminate infeasible nodes |
| Scoring plugins | Rank feasible nodes to pick the best one |
| kubelet | Starts the Pod on the node once bound (Chapter 08) |

---

## 8. Important Terminology

| Term | Meaning |
|---|---|
| kube-scheduler | Control plane component deciding Pod-to-node placement |
| Node Affinity | Rule attracting/repelling Pods based on node labels |
| Pod Affinity/Anti-Affinity | Rule attracting/repelling Pods based on other Pods' labels |
| Taint | A node-level repellent requiring a matching toleration to schedule there |
| Toleration | A Pod-level declaration allowing it to be scheduled on a tainted node |
| Resource Requests | Minimum resources a container needs — used for scheduling decisions |
| Resource Limits | Maximum resources a container may use — enforced at runtime |
| Node Selector | Simplest node-matching mechanism — exact-match label requirement |

---

## 9. YAML Deep Dive

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: scheduled-example
  labels:
    app: web
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
          - matchExpressions:
              - key: disktype
                operator: In
                values: ["ssd"]
    podAntiAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        - labelSelector:
            matchLabels:
              app: web
          topologyKey: kubernetes.io/hostname
  tolerations:
    - key: "dedicated"
      operator: "Equal"
      value: "gpu"
      effect: "NoSchedule"
  containers:
    - name: app
      image: nginx:1.27
      resources:
        requests:
          cpu: "250m"
          memory: "256Mi"
        limits:
          cpu: "500m"
          memory: "512Mi"
```

This Pod requires an SSD-labeled node, refuses to co-locate with other `app: web` Pods on the same node (spreading replicas), and tolerates the `dedicated=gpu:NoSchedule` taint (though it doesn't require a GPU node — it's just permitted to land there if otherwise scheduled).

---

## 10. kubectl Commands

| Command | Purpose | Example |
|---|---|---|
| `kubectl get pods -o wide` | Show which node each Pod landed on | `kubectl get pods -o wide` |
| `kubectl describe pod <name>` | Show scheduling events/failures | `kubectl describe pod scheduled-example` |
| `kubectl taint nodes <node> key=value:effect` | Apply a taint to a node | `kubectl taint nodes node1 dedicated=gpu:NoSchedule` |
| `kubectl label nodes <node> key=value` | Label a node (used by affinity/selectors) | `kubectl label nodes node1 disktype=ssd` |
| `kubectl get nodes --show-labels` | Show node labels | `kubectl get nodes --show-labels` |

---

## 11. Hands-on Examples

**Lab 1 — Label a node and confirm nodeAffinity places a Pod there:**
```bash
kubectl label nodes node1 disktype=ssd
kubectl apply -f scheduled-example.yaml
kubectl get pod scheduled-example -o wide
# NODE column shows node1
```

**Lab 2 — Taint a node and confirm a non-tolerating Pod is never scheduled there:**
```bash
kubectl taint nodes node2 dedicated=gpu:NoSchedule
kubectl run plain-pod --image=nginx
kubectl get pod plain-pod -o wide
# NODE column never shows node2
```

**Lab 3 — Request more resources than any node can provide, observe `Pending`:**
```bash
kubectl run huge-pod --image=nginx --requests='cpu=1000,memory=1000Gi'
kubectl describe pod huge-pod
# Events show "0/N nodes are available: insufficient memory"
```

---

## 12. Internal Flow

See Section 5 — scheduling is a two-phase, continuously repeated decision process per unscheduled Pod: **filtering** narrows the field to feasible nodes, **scoring** picks the best of those. Every scheduling input covered in this chapter (resource requests, affinity/anti-affinity, taints/tolerations, node selectors) plugs into one or both of those phases.

---

## 13. Real-World Examples

1. **High-availability deployments** use Pod anti-affinity to spread replicas across nodes/zones, ensuring a single node/zone failure doesn't take down every replica.
2. **GPU workloads** (ML training, Chapter 17 MLOps preview) use taints on GPU nodes plus tolerations on GPU-requiring Pods, keeping regular workloads off expensive specialized hardware.
3. **Data locality optimization** uses Pod affinity to co-locate application Pods with cache Pods on the same node, reducing network latency.
4. **Multi-tenant clusters** use node taints/tolerations to dedicate specific nodes to specific teams or workloads, alongside NetworkPolicies (Chapter 18) for traffic isolation.
5. **Cost optimization** uses node affinity to prefer cheaper spot/preemptible node pools for fault-tolerant, interruption-friendly workloads.

---

## 14. Best Practices

- Always set **resource requests** on production workloads — the scheduler cannot make good placement decisions without them, and Pods without requests get lowest scheduling/eviction priority.
- Prefer **preferred** (soft) affinity rules over **required** (hard) ones unless the constraint is truly non-negotiable — hard rules can leave Pods permanently `Pending` if no node satisfies them.
- Use Pod anti-affinity with `topologyKey: topology.kubernetes.io/zone` (not just hostname) for true zone-level high availability.
- Combine taints/tolerations (repel by default, opt in) with node affinity (attract) when you want a truly dedicated node pool — taints alone don't stop the Pod from landing on non-tainted nodes too.

---

## 15. Common Mistakes

- Forgetting that a toleration only **permits** scheduling on a tainted node — it does not **require** it; the Pod may still land elsewhere unless paired with node affinity.
- Setting overly strict `requiredDuringSchedulingIgnoredDuringExecution` rules that leave Pods stuck `Pending` because no node satisfies every hard constraint simultaneously.
- Omitting resource requests/limits entirely, leading to poor scheduling decisions and unpredictable node overcommitment.
- Confusing node affinity (matches node labels) with Pod affinity (matches other Pods' labels) — they solve different placement problems.

---

## 16. Troubleshooting

| Symptom | Likely Cause | Debugging Commands | Fix |
|---|---|---|---|
| Pod stuck in `Pending` | No node satisfies resource requests, affinity rules, or taints/tolerations | `kubectl describe pod <name>` (check Events) | Relax constraints, add capacity, or fix taint/toleration mismatch |
| Pod always lands on the same few nodes | Missing anti-affinity/topology spread rules | `kubectl get pods -o wide` | Add Pod anti-affinity or topology spread constraints |
| Pod scheduled onto an unintended tainted node | Toleration too broad (e.g., tolerates all taints) | `kubectl describe pod <name>`, check tolerations | Scope tolerations to exact key/value/effect needed |
| Node never receives any Pods | Taint applied without any workloads tolerating it | `kubectl describe node <name>` | Add matching tolerations to intended workloads, or remove the taint |

---

## 17. Comparison Tables

| Mechanism | Direction | Matches Against |
|---|---|---|
| Node Affinity | Pod attracted to matching nodes | Node labels |
| Pod Affinity/Anti-Affinity | Pod attracted/repelled relative to other Pods | Other Pods' labels |
| Taints/Tolerations | Node repels Pods by default | Node taint vs Pod toleration |
| Node Selector | Simple exact-match required node label | Node labels (no soft/preferred option) |

| Rule Strength | Behavior |
|---|---|
| `requiredDuringSchedulingIgnoredDuringExecution` | Hard constraint — Pod stays `Pending` if unsatisfiable |
| `preferredDuringSchedulingIgnoredDuringExecution` | Soft constraint — best-effort, Pod still schedules if unsatisfiable |

---

## 18. Memory Tricks

- **"Airport gate assignment"** — filter out infeasible gates, then score and pick the best of what's left.
- **"Affinity attracts, taints repel, tolerations forgive."**
- **"Required = hard rule, risk of Pending. Preferred = soft rule, always still lands somewhere."**

---

## 19. Interview Questions

**Easy:**
1. What are the two phases of kube-scheduler's decision process?
   *Expected answer:* Filtering (eliminating nodes that cannot run the Pod at all, based on resources, taints/tolerations, node selectors, etc.) followed by Scoring (ranking the remaining feasible nodes and selecting the highest-scoring one).

**Medium:**
2. What is the difference between node affinity and Pod affinity?
   *Expected answer:* Node affinity attracts or repels Pod placement based on **node labels** (e.g., schedule only on SSD-labeled nodes). Pod affinity/anti-affinity attracts or repels Pod placement based on **other Pods' labels** already running in the cluster (e.g., co-locate with cache Pods, or never co-locate two replicas of the same app on one node). They solve different placement problems — one is about node characteristics, the other about Pod-to-Pod relationships.

**Hard:**
3. A team tolerates a GPU node's taint on their ML training Pods, expecting them to always run on GPU nodes, but later finds some training Pods running on regular, non-GPU nodes instead. Explain why, and how to actually guarantee GPU-only placement.
   *Expected answer:* A toleration only permits a Pod to be scheduled on a tainted node — it does not require or prefer that placement. Since the training Pods only had a toleration and no node affinity/selector actually requiring GPU-labeled nodes, the scheduler was free to place them on any untainted node that was otherwise feasible, which is exactly what happened. To guarantee GPU-only placement, the team needs to pair the toleration (permission to land on the tainted GPU nodes) with a `requiredDuringSchedulingIgnoredDuringExecution` node affinity rule (or a node selector) matching a label present only on GPU nodes — the toleration alone only removes the repulsion, it doesn't add attraction.

---

## 20. KCNA Practice Questions

**Q1.** What is the role of kube-scheduler in a Kubernetes cluster?
A. To run containers on nodes
B. To decide which node a new, unscheduled Pod should run on
C. To store cluster state
D. To enforce NetworkPolicies

**Correct answer: B**
*Explanation:* kube-scheduler assigns Pods to nodes via filtering and scoring. A describes the container runtime/kubelet. C describes etcd. D describes NetworkPolicy enforcement by the CNI plugin (Chapter 18).

---

**Q2.** What does a taint on a node do by default?
A. Attracts all Pods to that node
B. Repels Pods from being scheduled on that node, unless they have a matching toleration
C. Deletes all Pods currently on that node
D. Prevents the node from joining the cluster

**Correct answer: B**
*Explanation:* Taints repel Pods unless a matching toleration is present — the inverse of affinity's attraction mechanism. A misdescribes affinity. C and D are unrelated effects.

---

**Q3.** Which scheduling input is used by kube-scheduler specifically during the filtering phase to eliminate nodes without enough capacity?
A. Resource limits
B. Resource requests
C. Liveness probes
D. Service selectors

**Correct answer: B**
*Explanation:* Resource requests represent the minimum a container needs and are what the scheduler uses to filter out nodes lacking sufficient capacity. Resource limits (A) are enforced at runtime, not used in scheduling decisions. C and D are unrelated to scheduling.

---

**Q4.** What is the effect of a `preferredDuringSchedulingIgnoredDuringExecution` affinity rule if no node satisfies it?
A. The Pod remains `Pending` indefinitely
B. The Pod is scheduled anyway, on a best-effort basis, ignoring the unsatisfied preference
C. The Pod is deleted automatically
D. The scheduler retries indefinitely without ever placing the Pod

**Correct answer: B**
*Explanation:* "Preferred" rules are soft constraints — the scheduler does its best but still schedules the Pod even if the preference can't be met. A describes "required" rule behavior instead. C and D do not reflect actual scheduler behavior.

---

**Q5.** What is the primary use case for Pod anti-affinity?
A. Attracting Pods to nodes with specific hardware
B. Spreading replicas across nodes/zones to improve availability
C. Restricting network traffic between Pods
D. Allocating persistent storage

**Correct answer: B**
*Explanation:* Pod anti-affinity is commonly used to prevent replicas of the same application from landing on the same node/zone, improving fault tolerance. A describes node affinity. C describes NetworkPolicy (Chapter 18). D describes PersistentVolumes (Chapter 19).

---

**Q6.** In the "Airport gate assignment" analogy used in this chapter, what does the filtering phase correspond to?
A. Assigning the final gate to a flight
B. Eliminating gates that cannot possibly accommodate the flight
C. Boarding passengers onto the plane
D. Scheduling the flight's departure time

**Correct answer: B**
*Explanation:* Filtering eliminates infeasible options first (gates/nodes that cannot work at all), mirroring how kube-scheduler discards nodes lacking capacity or matching taints/selectors before scoring. A describes the outcome of scoring. C and D are unrelated to the analogy.

---

**Q7.** Which of the following is the simplest, exact-match-only mechanism for constraining which node a Pod can be scheduled on?
A. Pod affinity
B. nodeSelector
C. Taint
D. Resource limit

**Correct answer: B**
*Explanation:* `nodeSelector` is the simplest node-matching mechanism, requiring an exact label match with no soft/preferred option, unlike node affinity which supports both required and preferred variants. A matches against other Pods, not nodes. C repels rather than selects. D is unrelated to placement.

---

**Q8.** What happens to a Pod's `spec.nodeName` field once kube-scheduler makes a placement decision?
A. It remains empty forever
B. kube-scheduler writes the chosen node's name into it via the API server
C. The kubelet sets it before the Pod is created
D. It is deleted from the Pod spec

**Correct answer: B**
*Explanation:* Per the Internal Working flow, after scoring picks the best node, kube-scheduler writes the binding by setting `spec.nodeName` through the API server. A contradicts the scheduling flow. C reverses the order — kubelet only acts after binding. D is incorrect.

---

**Q9.** Which taint effect immediately evicts already-running Pods that do not tolerate it, in addition to preventing new ones from scheduling there?
A. NoSchedule
B. PreferNoSchedule
C. NoExecute
D. PreferNoExecute

**Correct answer: C**
*Explanation:* `NoExecute` evicts existing non-tolerating Pods and prevents new ones from scheduling. `NoSchedule` (A) only blocks new scheduling without evicting running Pods. `PreferNoSchedule` (B) is a soft version of NoSchedule. `PreferNoExecute` (D) does not exist as a taint effect.

---

**Q10.** According to this chapter's Best Practices, why should production workloads always set resource requests?
A. Requests are required for container images to build correctly
B. Without them, the scheduler cannot make good placement decisions and Pods get lowest scheduling/eviction priority
C. Requests are mandatory for enabling liveness probes
D. Requests replace the need for resource limits entirely

**Correct answer: B**
*Explanation:* Resource requests are the scheduler's primary filtering input; omitting them leads to poor placement decisions and low priority during eviction. A and C describe unrelated concerns. D is false — requests and limits serve different purposes (Section 4.2).

---

**Q11.** In the chapter's Architecture diagram, why does Node B fail the filtering phase?
A. It has insufficient CPU
B. It is tainted and the Pod has no matching toleration
C. It lacks the required node label
D. It has too many Pods already running

**Correct answer: B**
*Explanation:* The diagram shows Node B failing filtering specifically due to a taint with no matching toleration on the Pod. A, C, and D are plausible general filtering reasons but not what the diagram depicts for Node B.

---

**Q12.** What is the key difference between a toleration and a node affinity rule requiring a specific node label?
A. They are functionally identical
B. A toleration only permits scheduling on a tainted node; node affinity actively requires/prefers placement on nodes with matching labels
C. Node affinity is enforced at runtime; tolerations are enforced at scheduling time only
D. Tolerations apply to nodes; node affinity applies to Pods

**Correct answer: B**
*Explanation:* This is the crux of the hard interview question in this chapter — a toleration removes repulsion (permission) without adding attraction (requirement), while node affinity actively steers placement toward matching nodes. C and D mischaracterize where and how each mechanism is defined and enforced.

---

**Q13.** Which topologyKey should be used in Pod anti-affinity rules to achieve true zone-level high availability, rather than just per-node spreading?
A. kubernetes.io/hostname
B. topology.kubernetes.io/zone
C. kubernetes.io/os
D. node.kubernetes.io/instance-type

**Correct answer: B**
*Explanation:* Per Best Practices, `topology.kubernetes.io/zone` spreads replicas across zones for true HA. `kubernetes.io/hostname` (A) only spreads across individual nodes, not zones. C and D are unrelated topology keys.

---

**Q14.** A Pod has a `requiredDuringSchedulingIgnoredDuringExecution` node affinity rule requiring a label that no node in the cluster currently has. What happens?
A. The Pod is scheduled on a random node anyway
B. The Pod remains stuck in `Pending` indefinitely until a matching node exists
C. The scheduler removes the affinity rule automatically
D. The API server rejects the Pod creation request

**Correct answer: B**
*Explanation:* Hard (`required...`) rules are non-negotiable — if unsatisfiable, the Pod stays `Pending`, as noted in Common Mistakes and the Memory Tricks section. A describes "preferred" rule behavior instead. C and D do not reflect actual behavior.

---

**Q15.** In Lab 3 of this chapter, requesting far more resources (`cpu=1000,memory=1000Gi`) than any node can provide results in which observable outcome?
A. The Pod is immediately deleted
B. The Pod starts on the node with the most free capacity regardless
C. The Pod stays `Pending`, with Events showing "0/N nodes are available: insufficient memory"
D. The API server throws a validation error at creation time

**Correct answer: C**
*Explanation:* This is the exact observed behavior in Lab 3 — filtering eliminates every node for insufficient capacity, leaving the Pod `Pending` with a descriptive Event. A, B, and D do not match kube-scheduler's actual behavior.

---

**Q16.** Why do multi-tenant clusters commonly combine taints/tolerations with NetworkPolicies (Chapter 18)?
A. Taints control network traffic directly, making NetworkPolicies redundant
B. Taints/tolerations dedicate nodes to specific teams/workloads, while NetworkPolicies isolate traffic between them — together providing placement and network isolation
C. NetworkPolicies are required before any taint can be applied
D. They serve the exact same purpose and are interchangeable

**Correct answer: B**
*Explanation:* Per Real-World Examples, taints/tolerations handle node-level workload dedication while NetworkPolicies handle traffic isolation — complementary, not redundant or interchangeable mechanisms (A, D). C invents a dependency that doesn't exist.

---

**Q17.** Which scheduling mechanism would best support a cost-optimization strategy that prefers cheaper spot/preemptible node pools for fault-tolerant workloads?
A. Pod anti-affinity
B. Node affinity (preferred variant) toward spot-pool-labeled nodes
C. NoExecute taints on all nodes
D. Resource limits set very low

**Correct answer: B**
*Explanation:* Per Real-World Examples, node affinity is used to prefer cheaper spot/preemptible pools for interruption-tolerant workloads. A solves a different problem (replica spreading). C would evict everything indiscriminately. D does not influence node selection.

---

**Q18.** A Pod's toleration matches a taint's key and value but not its effect. What is the result?
A. The toleration still works because key/value matching is sufficient
B. The toleration does not match, and the taint's effect is fully enforced against the Pod
C. The scheduler prompts the user to fix the mismatch
D. The Pod is scheduled with a warning event only

**Correct answer: B**
*Explanation:* A toleration must match a taint's key, value (if specified), and effect to be considered a match; a mismatched effect means the toleration doesn't apply and the taint's repulsion (or eviction, for NoExecute) is fully enforced. A incorrectly assumes partial matching suffices. C and D do not reflect actual scheduler behavior.

---

**Q19.** Why does this chapter recommend combining taints/tolerations with node affinity when a truly dedicated node pool is required?
A. Taints alone guarantee dedicated placement
B. Taints only repel non-tolerating Pods from a node — they don't stop a tolerating Pod from also landing on non-tainted nodes; affinity is needed to require placement on the dedicated nodes specifically
C. Node affinity alone can taint nodes automatically
D. This combination is only cosmetic and has no functional effect

**Correct answer: B**
*Explanation:* This directly restates the Best Practices guidance and the hard interview scenario: tolerations open the door to tainted nodes but don't close the door to untainted ones, so affinity must be added to require the dedicated nodes specifically. A, C, and D misstate the mechanisms.

---

**Q20.** Following the chapter's Troubleshooting table, if a node never receives any Pods despite being healthy and part of the cluster, what is the most likely cause?
A. The node's kubelet is not running
B. A taint was applied to the node with no workloads tolerating it
C. The node has no labels at all
D. The API server has blacklisted the node

**Correct answer: B**
*Explanation:* Per the Troubleshooting table, a node receiving zero Pods despite being healthy commonly means a taint was applied without any matching tolerations among current workloads. A would show the node as NotReady, not merely Pod-less. C and D are not listed causes and don't reflect actual scheduler/API-server behavior.

---

## 21. Chapter Summary (One-Page Revision Sheet)

- **kube-scheduler** assigns each new, unscheduled Pod to a node via a two-phase process: **filtering** (eliminate infeasible nodes) then **scoring** (rank and pick the best feasible node).
- **Resource requests** drive filtering; **resource limits** are enforced at runtime, not used for scheduling.
- **Node affinity/anti-affinity** matches against node labels; **Pod affinity/anti-affinity** matches against other Pods' labels; both support hard (`required...`) and soft (`preferred...`) variants.
- **Taints** repel Pods from a node by default; **tolerations** permit (but do not require) a Pod to land there — pair with node affinity for a true dedicated-node guarantee.

---

### Chapter Completion Checklist

1. **Topics covered:** kube-scheduler's filtering/scoring phases, resource requests/limits, node affinity/anti-affinity, Pod affinity/anti-affinity, taints and tolerations.
2. **KCNA objectives completed:** Kubernetes scheduling internals.
3. **Remaining objectives:** Security — RBAC, ServiceAccounts, Pod Security Standards, Secrets (Chapter 21).
4. **Suggested revision checklist:** Explain the two-phase scheduling process from memory; explain why a toleration alone doesn't guarantee placement on a tainted node; recite the difference between required and preferred affinity rules.
5. **Suggested hands-on exercises:** Complete Lab 3 (oversized resource request causing `Pending`) — the clearest demonstration of the filtering phase in action.
6. **Related chapters:** Previous: [19-Storage](../19-Storage/README.md). Next: [21-Security](../21-Security/README.md) — how Kubernetes secures workloads and cluster access.
