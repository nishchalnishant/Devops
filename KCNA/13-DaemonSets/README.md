# 13 — DaemonSets

## 1. Learning Objectives

By the end of this chapter you will be able to:

- Explain why some workloads need "exactly one Pod per node" instead of a floating replica count.
- Explain how a DaemonSet differs from a Deployment/ReplicaSet in scheduling behavior.
- Read and write a complete DaemonSet manifest, including node selection and tolerations.
- Explain common real-world DaemonSet use cases: logging, monitoring, networking agents.
- Explain how DaemonSets handle node addition/removal and rolling updates.

**KCNA objectives covered:** Kubernetes Fundamentals domain — the node-scoped workload controller, contrasted with the replica-scoped controllers from Chapters 11-12.

---

## 2. Historical Background

Some infrastructure-level software — log collectors, monitoring agents, network plugins — needs to run on **every single node** in a cluster, not a fixed, arbitrary count decided by a user. Before Kubernetes, cluster administrators handled this with configuration management tools (Ansible, Chapter 11 in this repo's DevOps track) that installed an agent as a system service on every machine, or manual per-node setup scripts. As clusters became more dynamic — nodes added and removed automatically by autoscalers — this static approach couldn't keep up. Kubernetes introduced the **DaemonSet** to guarantee an agent Pod is automatically placed on every (or every matching) node, including new ones as they join.

---

## 3. Motivation: Why Do DaemonSets Exist?

**Analogy — The Building's Smoke Detector:**
A large apartment building doesn't install "3 smoke detectors somewhere in the building" — it installs **exactly one per apartment**, no matter how many apartments the building has, and it automatically installs one in every newly built unit. A **DaemonSet** works the same way: instead of saying "run 3 replicas" (which is meaningless for a per-node agent), it says "run exactly one copy of this Pod on every node that matches this criteria" — and when a new node joins the cluster, Kubernetes automatically places a copy there too.

### 3.1 How Was This Solved Before Kubernetes?

Provisioning scripts, configuration management tools, or golden VM images baked the agent into every node at boot time — meaning updating the agent required re-provisioning or re-imaging every node, and there was no cluster-aware controller ensuring coverage as nodes changed.

### 3.2 How Kubernetes Solves It

A DaemonSet's controller watches the cluster's node list and ensures exactly one matching Pod is scheduled on each node satisfying its node selector/affinity/tolerations — automatically adding a Pod to new nodes and removing it from nodes that are deleted, with no manual intervention.

---

## 4. Core Concepts

### 4.1 What Is a DaemonSet? (Formal Definition)

**Definition:** A DaemonSet ensures that all (or a filtered subset of) nodes run exactly one copy of a specified Pod, automatically adding Pods to new nodes as they join the cluster and removing them from nodes as they leave.

### 4.2 DaemonSet vs Deployment — the Key Scheduling Difference

| Aspect | Deployment/ReplicaSet | DaemonSet |
|---|---|---|
| Replica count | User-specified number (`replicas: 3`) | Determined by node count — one per matching node |
| Scheduling | kube-scheduler picks any suitable node(s) | Effectively one Pod scheduled per matching node |
| Scaling with cluster size | Doesn't automatically scale with node count | Automatically scales with node count |

### 4.3 Restricting Which Nodes Get a Pod

By default a DaemonSet targets **all** nodes, but this can be restricted with:

| Mechanism | Purpose |
|---|---|
| `nodeSelector` | Only run on nodes matching specific labels (e.g., `disktype: ssd`) |
| Node affinity | More expressive version of `nodeSelector` with `required`/`preferred` rules |
| Tolerations | Allow scheduling onto nodes with matching **taints** (Chapter 20 covers taints/tolerations in depth) — commonly needed to run a DaemonSet Pod even on control plane nodes, which are normally tainted to repel regular workloads |

### 4.4 Rolling Updates for DaemonSets

DaemonSets support `RollingUpdate` (default) and `OnDelete` update strategies:

| Strategy | Behavior |
|---|---|
| `RollingUpdate` | Old Pods are automatically terminated and replaced with updated ones, node by node, controlled by `maxUnavailable` |
| `OnDelete` | Updated Pods are only created after you manually delete the old Pod on each node — gives full manual control over update timing |

---

## 5. Internal Working

```
1. A DaemonSet object is submitted, with an optional nodeSelector/
   affinity/toleration
        ↓
2. DaemonSet controller (kube-controller-manager, Chapter 07 Section
   4.4) lists all nodes in the cluster
        ↓
3. For each node matching the DaemonSet's criteria, controller checks:
   does this node already have a matching Pod?
        ↓
4a. No matching Pod → create one, bound directly to that node
4b. Matching Pod exists → do nothing
4c. Node no longer matches (or was removed) → delete the Pod there
        ↓
5. When a NEW node joins the cluster and matches criteria, the
   controller immediately creates a Pod there too — no user action needed
```

---

## 6. Architecture

```
   Node 1                Node 2                Node 3 (new!)
┌─────────┐         ┌─────────┐         ┌─────────┐
│ log-agent   │         │ log-agent   │         │ log-agent   │ ← automatically
│    Pod          │         │    Pod          │         │    Pod          │   added when
└─────────┘         └─────────┘         └─────────┘   Node 3 joined

        All three Pods created and managed by ONE DaemonSet object:
        `kind: DaemonSet, name: log-agent`
```

---

## 7. Component Breakdown

| Piece | Role |
|---|---|
| DaemonSet object | Declares the Pod template and node-targeting rules |
| DaemonSet controller | Watches node list and ensures exactly one matching Pod per matching node |
| nodeSelector/affinity | Filters which nodes should get a Pod |
| Tolerations | Allow the DaemonSet's Pods to be scheduled on tainted nodes (e.g., control plane nodes) |

---

## 8. Important Terminology

| Term | Meaning |
|---|---|
| DaemonSet | Controller ensuring one Pod copy per matching node |
| Taint | A marker on a node that repels Pods unless they tolerate it (full detail in Chapter 20) |
| Toleration | A Pod-side declaration allowing it to be scheduled despite a matching taint |
| OnDelete strategy | Update strategy requiring manual Pod deletion to trigger replacement |

---

## 9. YAML Deep Dive

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: log-agent
spec:
  selector:
    matchLabels:
      app: log-agent
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
  template:
    metadata:
      labels:
        app: log-agent
    spec:
      tolerations:
        - key: node-role.kubernetes.io/control-plane
          effect: NoSchedule
      containers:
        - name: log-agent
          image: fluent-bit
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
```

The `tolerations` block is what allows this DaemonSet's Pods to also run on control-plane nodes, which are normally off-limits to regular workloads (Chapter 20 covers this taint/toleration mechanism fully).

---

## 10. kubectl Commands

| Command | Purpose | Example |
|---|---|---|
| `kubectl get ds` | List DaemonSets and their node coverage | `kubectl get ds -A` |
| `kubectl describe ds <name>` | Show detailed status, including desired/current/ready counts per node | `kubectl describe ds log-agent` |
| `kubectl rollout status ds/<name>` | Watch a DaemonSet rollout | `kubectl rollout status ds/log-agent` |
| `kubectl delete ds <name>` | Delete a DaemonSet (and its Pods) | `kubectl delete ds log-agent` |

---

## 11. Hands-on Examples

**Lab 1 — Confirm one Pod per node:**
```bash
kubectl apply -f log-agent-ds.yaml
kubectl get pods -l app=log-agent -o wide
# Exactly one Pod per node appears, each with a different NODE column
```

**Lab 2 — Watch coverage extend to a new node (in a cluster with autoscaling or manually added nodes):**
```bash
# after a new node joins the cluster
kubectl get pods -l app=log-agent -o wide
# A new Pod appears automatically bound to the new node — no manual action taken
```

**Lab 3 — Trigger a DaemonSet rolling update:**
```bash
kubectl set image ds/log-agent log-agent=fluent-bit:2.0
kubectl rollout status ds/log-agent
# Pods are replaced one node at a time, respecting maxUnavailable
```

---

## 12. Internal Flow

See Section 5's 5-step flow — note the key contrast with Chapter 11's ReplicaSet flow: instead of reconciling against a fixed `replicas` number, the DaemonSet controller reconciles against the **live node list**, recalculating "desired" every time nodes are added or removed.

---

## 13. Real-World Examples

1. **Log collection agents** (Fluentd, Fluent Bit, Filebeat) are the single most common DaemonSet use case — one instance per node collects and forwards logs from all Pods on that node.
2. **Node-level monitoring agents** (Prometheus Node Exporter, Datadog Agent) run as DaemonSets to expose per-node hardware/OS metrics (Chapter 22 Observability).
3. **CNI networking plugins** (Calico, Cilium, Chapter 18) run their core networking agent as a DaemonSet, since every node needs exactly one copy to participate in the cluster's pod network.
4. **Storage plugins (CSI node plugins)** run as DaemonSets because every node needs its own local agent to handle volume mount/unmount operations for Pods scheduled there (Chapter 19).
5. **Security/compliance agents** (like Falco, Chapter 14 DevSecOps) run as DaemonSets to monitor system calls and runtime behavior on every node in the cluster.

---

## 14. Best Practices

- Set conservative resource requests/limits on DaemonSet Pods — since they run on every node, an oversized request can meaningfully reduce allocatable capacity cluster-wide.
- Use tolerations deliberately and only when a DaemonSet genuinely needs to run on tainted nodes (e.g., control-plane nodes for a cluster-wide monitoring agent) — don't tolerate taints unnecessarily.
- Prefer `RollingUpdate` with a sensible `maxUnavailable` for most cases; use `OnDelete` only when you need precise manual control over per-node update timing (e.g., extremely sensitive infrastructure agents).
- Use `nodeSelector`/affinity to scope a DaemonSet to only the node types that need it (e.g., only GPU nodes for a GPU-monitoring agent), rather than running unnecessary Pods everywhere.

---

## 15. Common Mistakes

- Trying to set a `replicas` field on a DaemonSet — this field doesn't exist for DaemonSets since the count is implicitly determined by the node list.
- Forgetting tolerations, then being confused why a monitoring/logging DaemonSet doesn't have a Pod running on control-plane nodes.
- Running resource-heavy DaemonSet Pods without requests/limits, causing unpredictable resource pressure across every node in the cluster simultaneously.
- Assuming a DaemonSet Pod will get rescheduled elsewhere if its node fails — it won't; a DaemonSet Pod is tied to a specific node and only reappears if/when that same node becomes available again (or a replacement Pod is created if the node object is deleted and re-added).

---

## 16. Troubleshooting

| Symptom | Likely Cause | Debugging Commands | Fix |
|---|---|---|---|
| DaemonSet Pod missing on some nodes | Node doesn't match `nodeSelector`/affinity, or has a taint without a matching toleration | `kubectl describe ds`, `kubectl describe node` | Adjust selector/affinity or add the needed toleration |
| DaemonSet Pod missing on control-plane nodes specifically | No toleration for the control-plane taint | `kubectl describe node <control-plane-node>` (check Taints) | Add matching toleration to the Pod template |
| Rolling update stuck | A new Pod is failing readiness on one node | `kubectl describe pod`, `kubectl logs` | Fix the app issue; check `maxUnavailable` isn't blocking progress |
| Desired count doesn't match actual node count | Some nodes are excluded by scheduling constraints (as above) | `kubectl get ds -o wide` (compare Desired/Current/Ready columns) | Confirm intended targeting is correct |

---

## 17. Comparison Tables

**DaemonSet vs Deployment vs ReplicaSet:**

| Aspect | Deployment/ReplicaSet | DaemonSet |
|---|---|---|
| Replica count basis | Fixed number you specify | One per matching node |
| Grows automatically with cluster size | No | Yes |
| Typical use case | Stateless application workloads | Per-node infrastructure agents |

---

## 18. Memory Tricks

- **"DaemonSet = smoke detector in every apartment"** — one per unit, automatically installed in new units, no "replica count" concept.
- **"No `replicas` field — the node list IS the replica count."**
- Remember the three DaemonSet-typical workloads: **"LMS" — Logging, Monitoring, Storage/networking (CSI/CNI) agents.**

---

## 19. Interview Questions

**Easy:**
1. What is the defining behavior of a DaemonSet?
   *Expected answer:* It ensures exactly one copy of a specified Pod runs on every node (or every node matching a selector/affinity/toleration), automatically adding Pods to new nodes and removing them from nodes that leave the cluster — unlike a Deployment/ReplicaSet, which maintains a fixed, user-specified replica count regardless of node count.

**Medium:**
2. Why would a DaemonSet need a toleration to run on control-plane nodes?
   *Expected answer:* Control-plane nodes are typically tainted by default to repel ordinary workloads, keeping them dedicated to control-plane components. A DaemonSet Pod, like any other Pod, is subject to this taint and won't be scheduled there unless its Pod spec includes a matching toleration explicitly allowing it — this is commonly needed for cluster-wide monitoring or logging agents that must cover every node, including control-plane ones.

**Hard:**
3. A team observes their DaemonSet has "5 desired, 4 ready" Pods persistently, even though the cluster has exactly 5 nodes and no visible taints on any of them. How would you investigate?
   *Expected answer:* "Desired" reflects nodes matching the DaemonSet's selector/affinity criteria, while "ready" reflects Pods that have actually passed their readiness checks. Since taints aren't the issue here, investigate the one node whose Pod isn't ready: `kubectl get pods -l <selector> -o wide` to identify which node's Pod is missing/not-ready, then `kubectl describe pod` on that specific Pod for probe failures or scheduling errors, and `kubectl logs` for application-level issues. Possible causes include a resource shortage on that specific node (insufficient allocatable CPU/memory per Chapter 08 Section 4.4), a failing readiness probe, or a node-specific issue like a disk problem preventing the container from starting properly.

---

## 20. KCNA Practice Questions

**Q1.** What is the defining scheduling behavior of a DaemonSet?
A. It schedules a fixed number of replicas anywhere in the cluster
B. It ensures one Pod copy runs on every node matching its criteria
C. It only runs a single Pod total, regardless of cluster size
D. It requires manual scheduling by an administrator for every node

**Correct answer: B**
*Explanation:* A DaemonSet's Pod count is tied directly to matching nodes, not a fixed number — this is its defining difference from ReplicaSets/Deployments. A describes ReplicaSet/Deployment behavior instead. C and D are incorrect.

---

**Q2.** Why might a DaemonSet's Pod fail to be scheduled on a specific node even though the DaemonSet targets all nodes?
A. DaemonSets can never run on more than 3 nodes
B. The node has a taint that the DaemonSet's Pod template does not tolerate
C. DaemonSets require nodes to be manually pre-approved
D. The node's IP address is incompatible with DaemonSets

**Correct answer: B**
*Explanation:* Taints repel Pods unless a matching toleration is present in the Pod spec — this is the standard reason a DaemonSet Pod is missing from an otherwise-matching node, commonly seen with control-plane node taints. A, C, and D are factually incorrect.

---

**Q3.** What happens to DaemonSet Pod coverage when a new node joins the cluster?
A. Nothing; an administrator must manually create a Pod on the new node
B. The DaemonSet controller automatically creates a matching Pod on the new node if it satisfies the targeting criteria
C. The DaemonSet is automatically deleted and recreated
D. The new node is automatically tainted to prevent any Pods from running

**Correct answer: B**
*Explanation:* This automatic coverage of new nodes is a core reason DaemonSets exist — no manual provisioning step is required. A, C, and D describe behaviors that don't occur.

---

**Q4.** Which of the following is a typical real-world DaemonSet use case?
A. Running a stateless web application that needs to scale based on traffic
B. Running a per-node log collection agent
C. Running a one-time database migration script
D. Running a batch data processing job that completes and exits

**Correct answer: B**
*Explanation:* Per-node log/monitoring/networking agents are the textbook DaemonSet use case, since they need exactly one instance per node. A fits a Deployment better (traffic-based scaling), while C and D describe Job-like one-shot workloads (Chapter 15), not per-node daemons.

---

**Q5.** Which field is notably ABSENT from a DaemonSet spec, unlike a Deployment or ReplicaSet spec?
A. `selector`
B. `template`
C. `replicas`
D. `metadata`

**Correct answer: C**
*Explanation:* DaemonSets have no `replicas` field because their Pod count is implicitly determined by the number of matching nodes, not a user-specified number. `selector` (A), `template` (B), and `metadata` (D) are all still present in a DaemonSet spec, just like in ReplicaSets/Deployments.

---

**Q6.** What happens to a DaemonSet's Pod on a node when that node is removed from the cluster?
A. The Pod is automatically rescheduled onto a different, existing node
B. The Pod is deleted along with the node, since DaemonSet Pods are tied to a specific node and are not rescheduled elsewhere
C. The entire DaemonSet is deleted
D. The Pod continues running indefinitely, orphaned from any node

**Correct answer: B**
*Explanation:* A DaemonSet Pod is bound to a specific node and is never rescheduled onto a different node — when its node leaves the cluster, its Pod goes with it, and coverage is only restored if a new matching node joins. A contradicts the node-scoped nature of DaemonSets. C and D are incorrect.

---

**Q7.** What is the purpose of the `OnDelete` update strategy for a DaemonSet?
A. It automatically deletes the DaemonSet after every update
B. Updated Pods are only created after a user manually deletes the existing Pod on each node, giving full manual control over update timing
C. It deletes all Pods immediately on any spec change, with no replacement
D. It is identical in behavior to `RollingUpdate`

**Correct answer: B**
*Explanation:* `OnDelete` requires explicit, per-node manual action to trigger a Pod replacement — useful for sensitive infrastructure agents where automatic rollout timing is undesirable. A, C, and D misdescribe the strategy.

---

**Q8.** Why is it important to set conservative resource requests/limits on DaemonSet Pods specifically?
A. DaemonSet Pods are exempt from resource limits by design
B. Since a copy runs on every node, an oversized resource request reduces allocatable capacity for other workloads across the entire cluster, not just one node
C. Resource requests only matter for Deployments, not DaemonSets
D. DaemonSets automatically cap their own resource usage without configuration

**Correct answer: B**
*Explanation:* Because DaemonSet Pods multiply across every node, an oversized request has a cluster-wide multiplying effect on reserved capacity — this is a documented best practice (Section 14). A, C, and D are false.

---

**Q9.** A cluster administrator wants a monitoring agent to run on GPU nodes only, not on every node in the cluster. What is the correct approach?
A. This is impossible; DaemonSets always target every node
B. Use `nodeSelector` or node affinity in the DaemonSet's Pod template to restrict targeting to nodes with a matching label (e.g., a GPU label)
C. Manually delete the Pods on non-GPU nodes after they're created
D. Create a separate Deployment instead, since DaemonSets cannot be restricted

**Correct answer: B**
*Explanation:* `nodeSelector`/affinity is exactly the mechanism for scoping a DaemonSet to a subset of nodes matching specific labels, as covered in Section 4.3 and Best Practices. A and D are false — restriction is a first-class DaemonSet feature. C is a manual workaround that the reconciliation loop would undo.

---

**Q10.** How does the DaemonSet controller's reconciliation differ fundamentally from the ReplicaSet controller's reconciliation (Chapter 11)?
A. They are identical in every respect
B. The DaemonSet controller reconciles against the live node list (recalculating "desired" as nodes change), while the ReplicaSet controller reconciles against a fixed, user-specified `replicas` number
C. The ReplicaSet controller reconciles against the node list instead
D. Neither controller performs any reconciliation

**Correct answer: B**
*Explanation:* This is the key architectural distinction highlighted in Section 12: DaemonSets derive "desired count" dynamically from cluster topology, while ReplicaSets use a static number set by the user. A, C, and D are incorrect.

---

**Q11.** Why can't "replicas: 3" be a meaningful concept for a DaemonSet the way it is for a ReplicaSet?
A. It could be meaningful, but Kubernetes simply forgot to implement it
B. A DaemonSet's purpose is exactly one Pod per matching node — an arbitrary fixed count would conflict with that per-node guarantee as the cluster scales up or down
C. DaemonSets always have exactly 3 Pods by convention
D. `replicas` is reserved exclusively for StatefulSets

**Correct answer: B**
*Explanation:* The entire value proposition of a DaemonSet is "one per node, however many nodes there are" — a static replica count would break that guarantee the moment the cluster's node count changed. A, C, and D are incorrect.

---

**Q12.** A DaemonSet targets all nodes, and the cluster has 5 nodes, none tainted. `kubectl get ds` shows "DESIRED: 5, CURRENT: 5, READY: 3." What does this most likely indicate?
A. Only 3 nodes exist in the cluster
B. 2 of the created Pods exist but are failing their readiness checks
C. The DaemonSet definition is invalid and must be recreated
D. This is normal, healthy behavior requiring no investigation

**Correct answer: B**
*Explanation:* CURRENT counts created Pods while READY counts Pods that have passed readiness checks — a gap between them (5 vs 3) points to 2 Pods being unhealthy, not missing. A contradicts DESIRED/CURRENT both being 5. C and D ignore the diagnostic signal.

---

**Q13.** Which Chapter 20 concept is most directly required to let a DaemonSet Pod run on a tainted control-plane node?
A. Resource quotas
B. Tolerations
C. Horizontal Pod Autoscaling
D. Network policies

**Correct answer: B**
*Explanation:* Tolerations are the Pod-side mechanism that permits scheduling despite a matching node taint, as explained in Sections 4.3 and 9. A, C, and D are unrelated mechanisms covered in different chapters.

---

**Q14.** Why do CNI networking plugins (e.g., Calico, Cilium) typically run as DaemonSets rather than Deployments?
A. CNI plugins require no scheduling at all
B. Every node needs exactly one instance of the networking agent to participate in the cluster's Pod network — a per-node guarantee that only a DaemonSet provides
C. Deployments cannot run networking software under any circumstances
D. CNI plugins are stateless and thus incompatible with DaemonSets

**Correct answer: B**
*Explanation:* Cluster networking requires each node to run its own agent participating in the overlay/underlay network — exactly the one-per-node guarantee a DaemonSet is designed for, unlike a Deployment's arbitrary replica placement. A, C, and D are incorrect.

---

**Q15.** What is the risk of forgetting to set a toleration when deploying a cluster-wide logging DaemonSet in a cluster where control-plane nodes are tainted?
A. The entire cluster will crash
B. The logging agent simply won't run on control-plane nodes, creating a monitoring blind spot for those nodes specifically
C. All worker node Pods will also be silently skipped
D. The DaemonSet will fail to be created at all

**Correct answer: B**
*Explanation:* Missing a needed toleration doesn't break the DaemonSet — it simply means control-plane nodes are excluded from coverage, a subtle gap noted as a common mistake (Section 15) and troubleshooting symptom (Section 16). A, C, and D overstate or misstate the impact.

---

**Q16.** In the update strategy comparison, what is the main trade-off of choosing `OnDelete` over `RollingUpdate`?
A. `OnDelete` is strictly faster in every case
B. `OnDelete` trades automation for precise manual control — updates only happen when an operator explicitly deletes each old Pod
C. `OnDelete` automatically respects `maxUnavailable` just like `RollingUpdate`
D. There is no meaningful trade-off; they are interchangeable

**Correct answer: B**
*Explanation:* `RollingUpdate` automates node-by-node replacement respecting `maxUnavailable`; `OnDelete` sacrifices that automation entirely in exchange for an operator deciding exactly when each node's Pod is replaced. A, C, and D misstate the comparison.

---

**Q17.** Why is a CSI storage plugin's node component commonly deployed as a DaemonSet rather than a Deployment?
A. CSI plugins do not support Deployments as an object type
B. Every node needs its own local agent to handle volume mount/unmount operations for Pods scheduled specifically on that node
C. DaemonSets are required for all storage-related workloads by Kubernetes API validation
D. CSI node plugins have no relationship to node-local operations

**Correct answer: B**
*Explanation:* Volume mount/unmount is inherently node-local work — a Pod's volume must be mounted on the exact node where the Pod runs, making the one-per-node DaemonSet model a natural fit, as described in Section 13. A, C, and D are incorrect.

---

**Q18.** Which memory trick from Section 18 captures the three most common DaemonSet workload categories?
A. "CPU, Memory, Disk"
B. "LMS — Logging, Monitoring, Storage/networking (CSI/CNI) agents"
C. "Create, Update, Delete"
D. "Small, Medium, Large"

**Correct answer: B**
*Explanation:* Section 18 explicitly gives "LMS" as the mnemonic for Logging, Monitoring, and Storage/networking agents — the three canonical DaemonSet use cases. A, C, and D are unrelated fabricated mnemonics.

---

**Q19.** A DaemonSet's rolling update appears stuck with only 1 of 5 nodes updated. What is a plausible cause consistent with this chapter's troubleshooting guidance?
A. DaemonSets cannot perform rolling updates at all
B. A newly created Pod on one node is failing its readiness check, and `maxUnavailable` is blocking further progress until it recovers
C. The cluster has been reduced to 1 node
D. `OnDelete` strategy was silently substituted for `RollingUpdate`

**Correct answer: B**
*Explanation:* This mirrors the Deployment rollout-stuck pattern (Chapter 12) applied to DaemonSets: a failing readiness probe on the new Pod version halts progression, respecting `maxUnavailable`, per Section 16's troubleshooting table. A is false — DaemonSets do support rolling updates. C and D are unsupported assumptions.

---

**Q20.** Conceptually, how does a DaemonSet's "automatic scaling with cluster size" compare to a Deployment's scaling behavior?
A. Both scale automatically and identically with node count
B. A DaemonSet's Pod count grows/shrinks automatically as nodes join/leave, while a Deployment's replica count stays fixed unless explicitly changed or an autoscaler (e.g., HPA) is configured
C. Neither controller's Pod count is ever affected by node count
D. A Deployment's replica count is always tied to the number of nodes by default

**Correct answer: B**
*Explanation:* This is the fundamental architectural distinction from Section 4.2/17: DaemonSets are inherently node-count-driven, while Deployments require an explicit `replicas` value or a separate autoscaling mechanism to change their Pod count. A, C, and D misstate this comparison.

---

## 21. Chapter Summary (One-Page Revision Sheet)

- A **DaemonSet** ensures exactly one Pod runs on every node (or every matching node), scaling automatically with the cluster's node count — no `replicas` field.
- Use **`nodeSelector`/affinity** to restrict which nodes get a Pod, and **tolerations** to allow scheduling on tainted nodes (e.g., control-plane nodes).
- Update strategies: **`RollingUpdate`** (automatic, node-by-node) and **`OnDelete`** (fully manual per-node control).
- Classic use cases: **logging agents, monitoring agents, CNI/CSI node plugins, security agents** — anything needing exactly one instance per node.

---

### Chapter Completion Checklist

1. **Topics covered:** DaemonSet definition, scheduling model, node targeting, update strategies, real-world infrastructure agent use cases.
2. **KCNA objectives completed:** The node-scoped workload controller, contrasting with the replica-count-based controllers from Chapters 11-12.
3. **Remaining objectives:** Stateful workloads needing stable identity and storage — StatefulSets (Chapter 14).
4. **Suggested revision checklist:** Explain why DaemonSets have no `replicas` field; name the three classic DaemonSet workload categories; explain the toleration requirement for control-plane node coverage.
5. **Suggested hands-on exercises:** Complete Lab 1 and inspect the `NODE` column in `kubectl get pods -o wide` output to see the one-Pod-per-node guarantee directly.
6. **Related chapters:** Previous: [12-Deployments](../12-Deployments/README.md). Next: [14-StatefulSets](../14-StatefulSets/README.md) — workloads that need stable network identity and persistent per-replica storage.
