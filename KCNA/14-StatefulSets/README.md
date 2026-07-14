# 14 — StatefulSets

## 1. Learning Objectives

By the end of this chapter you will be able to:

- Explain why stateless-style Deployments are insufficient for databases and other stateful applications.
- Explain the three guarantees a StatefulSet provides: stable identity, stable storage, ordered deployment/scaling.
- Explain the role of a Headless Service in giving each Pod a stable DNS name.
- Read and write a complete StatefulSet manifest, including `volumeClaimTemplates`.
- Explain StatefulSet scaling and update order.

**KCNA objectives covered:** Kubernetes Fundamentals domain — the identity-and-storage-stable workload controller, contrasting with the interchangeable Pods of Deployments (Chapter 12).

---

## 2. Historical Background

Deployments (Chapter 12) and ReplicaSets (Chapter 11) were designed around **stateless** applications — any Pod replica is interchangeable with any other, has no persistent local identity, and can be freely replaced with a fresh one. But many real applications — databases, message queues, distributed consensus systems — are the opposite: each instance has a distinct role (e.g., "the primary" vs "replica #2"), its own persistent data, and must be addressable by a stable, predictable name even after being rescheduled. Early Kubernetes had no clean way to express this, forcing users into fragile workarounds. Kubernetes introduced the **StatefulSet** specifically to give Pods stable, unique identities and stable, per-Pod persistent storage across restarts and rescheduling.

---

## 3. Motivation: Why Do StatefulSets Exist?

**Analogy — The Hospital's Numbered Rooms:**
In a hospital, patients aren't randomly reassigned to a different room number every time a nurse shift changes — Room 101 is always Room 101, with its own chart and equipment, even if the patient inside changes over time. Contrast this with a hotel's anonymous room-service staff, who are interchangeable and don't need a "stable identity" (any staff member can serve any room — that's the Deployment model). A **StatefulSet** is the hospital-room model: each replica gets a permanent, predictable name (`db-0`, `db-1`, `db-2`) and its own dedicated storage that follows it specifically, even if the underlying Pod is deleted and recreated.

### 3.1 How Was This Solved Before Kubernetes?

Stateful clustered applications (like databases) were traditionally deployed on fixed, hand-provisioned VMs with static hostnames and dedicated disks — inherently non-elastic and requiring manual intervention to replace a failed instance while preserving its identity and data.

### 3.2 How Kubernetes Solves It

A StatefulSet assigns each Pod a **stable, predictable name** (`<statefulset-name>-<ordinal>`, e.g., `db-0`, `db-1`), a **stable network identity** via a Headless Service (Section 4.2), and **stable, per-Pod persistent storage** via `volumeClaimTemplates`, which follows the same-ordinal Pod even across rescheduling.

---

## 4. Core Concepts

### 4.1 The Three StatefulSet Guarantees

| Guarantee | What It Means |
|---|---|
| **Stable, unique network identity** | Each Pod gets a predictable name (`web-0`, `web-1`, ...) and stable DNS via a Headless Service |
| **Stable, persistent storage** | Each Pod gets its own PersistentVolumeClaim (Chapter 19), which is retained and reattached to the same-ordinal Pod even if it's rescheduled |
| **Ordered deployment and scaling** | Pods are created, scaled, and deleted **one at a time, in strict ordinal order** (0, then 1, then 2...) — not all at once like a ReplicaSet |

### 4.2 Headless Services and Stable DNS

**Definition:** A Headless Service (`clusterIP: None`) doesn't load-balance traffic to a single virtual IP — instead, it enables direct DNS resolution to each individual Pod's own stable DNS name, in the form:

```
<pod-name>.<service-name>.<namespace>.svc.cluster.local
```

For example, `db-0.db-headless.default.svc.cluster.local` always resolves to the specific Pod `db-0`, regardless of which node it's currently running on. This is essential for stateful applications that need to address a specific peer (e.g., "always connect to the primary at `db-0`").

**Why this matters:** Regular Services (Chapter 16) intentionally hide individual Pod identity behind one virtual IP — exactly right for stateless apps, but wrong for stateful apps that need to distinguish between specific, named peers.

### 4.3 `volumeClaimTemplates`

Unlike a Deployment's Pod template (which all replicas share identically), a StatefulSet's `volumeClaimTemplates` causes Kubernetes to create a **separate** PersistentVolumeClaim per Pod ordinal (e.g., `data-db-0`, `data-db-1`) — and critically, if a Pod is deleted and recreated, the **same-ordinal PVC is reattached**, not a fresh empty one. This is how a StatefulSet Pod "keeps its data" across restarts.

### 4.4 Ordered Operations

| Operation | Order |
|---|---|
| Scale up | Pods created in order: 0, then 1, then 2, ... — each must be Running and Ready before the next starts |
| Scale down | Pods deleted in **reverse** order: highest ordinal first |
| Rolling update (default) | Pods updated in reverse ordinal order, one at a time, each must be Ready before the next is updated |

---

## 5. Internal Working

```
1. A StatefulSet object with replicas: 3 and volumeClaimTemplates is
   submitted, alongside a Headless Service
        ↓
2. StatefulSet controller creates Pod "web-0" FIRST, with its own
   PersistentVolumeClaim "data-web-0"
        ↓
3. Controller waits until web-0 is Running AND Ready (via readiness
   probe, Chapter 08 Section 4.2) before proceeding
        ↓
4. Controller creates "web-1" with "data-web-1", waits for Ready
        ↓
5. Controller creates "web-2" with "data-web-2", waits for Ready
        ↓
6. Each Pod gets a stable DNS name via the Headless Service:
   web-0.web-headless, web-1.web-headless, web-2.web-headless
        ↓
7. If web-1 is deleted, only a new web-1 is created (same name), and
   it reattaches to the EXISTING "data-web-1" PVC — not a new empty one
```

---

## 6. Architecture

```
             Headless Service: db-headless (clusterIP: None)
        ┌──────────────┬──────────────┬──────────────┐
        │                    │                    │                    │
        ▼                    ▼                    ▼
   ┌─────────┐         ┌─────────┐         ┌─────────┐
   │  db-0       │         │  db-1       │         │  db-2       │
   │ (created      │         │ (created      │         │ (created      │
   │  first)        │         │  second)      │         │  third)        │
   └────┬────┘         └────┬────┘         └────┬────┘
        │                    │                    │
        ▼                    ▼                    ▼
   data-db-0           data-db-1           data-db-2
   (dedicated PVC,     (dedicated PVC,     (dedicated PVC,
    follows db-0)        follows db-1)        follows db-2)

   DNS: db-0.db-headless.default.svc.cluster.local always → db-0 specifically
```

---

## 7. Component Breakdown

| Piece | Role |
|---|---|
| StatefulSet object | Declares ordered, identity-stable Pod management with per-Pod storage |
| Headless Service | Provides stable, individually-addressable DNS names per Pod |
| volumeClaimTemplates | Creates and re-attaches a dedicated PVC per Pod ordinal |
| Ordinal index | The stable numeric suffix (`-0`, `-1`, `-2`) identifying each Pod's permanent identity |

---

## 8. Important Terminology

| Term | Meaning |
|---|---|
| StatefulSet | Controller providing stable identity, stable storage, and ordered operations for Pods |
| Ordinal | The stable numeric index in a StatefulSet Pod's name (`web-0`, `web-1`) |
| Headless Service | A Service with `clusterIP: None`, enabling direct per-Pod DNS resolution |
| volumeClaimTemplates | Spec section causing per-Pod PersistentVolumeClaims to be created and reused |

---

## 9. YAML Deep Dive

```yaml
apiVersion: v1
kind: Service
metadata:
  name: db-headless
spec:
  clusterIP: None
  selector:
    app: db
  ports:
    - port: 5432
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: db
spec:
  serviceName: db-headless
  replicas: 3
  selector:
    matchLabels:
      app: db
  template:
    metadata:
      labels:
        app: db
    spec:
      containers:
        - name: db
          image: postgres:15
          volumeMounts:
            - name: data
              mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
    - metadata:
        name: data
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 10Gi
```

Note `spec.serviceName` links the StatefulSet to its Headless Service — required for the stable per-Pod DNS names in Section 4.2 to work.

---

## 10. kubectl Commands

| Command | Purpose | Example |
|---|---|---|
| `kubectl get sts` | List StatefulSets | `kubectl get sts` |
| `kubectl get pods -l app=db` | List StatefulSet Pods (note their ordinal names) | `kubectl get pods -l app=db` |
| `kubectl scale sts <name> --replicas=N` | Scale a StatefulSet (ordered) | `kubectl scale sts db --replicas=5` |
| `kubectl get pvc` | List PersistentVolumeClaims, including per-Pod ones | `kubectl get pvc` |
| `kubectl delete sts <name> --cascade=orphan` | Delete the StatefulSet but leave Pods and PVCs intact | `kubectl delete sts db --cascade=orphan` |

---

## 11. Hands-on Examples

**Lab 1 — Observe ordinal Pod names and ordered creation:**
```bash
kubectl apply -f db-statefulset.yaml
kubectl get pods -l app=db -w
# Pods appear one at a time, in order: db-0 (Running+Ready), THEN db-1,
# THEN db-2 — never all at once like a Deployment
```

**Lab 2 — Prove data persists across Pod deletion:**
```bash
kubectl exec db-1 -- psql -c "CREATE TABLE test (id int);"
kubectl delete pod db-1
kubectl get pods -w   # a NEW db-1 appears
kubectl exec db-1 -- psql -c "\dt"
# The "test" table still exists — the new db-1 reattached to the SAME PVC
```

**Lab 3 — Confirm stable per-Pod DNS:**
```bash
kubectl run tmp --rm -it --image=busybox -- nslookup db-1.db-headless
# Resolves to db-1's specific Pod IP, regardless of which node it's on
```

---

## 12. Internal Flow

See Section 5's 7-step flow — this is a specialized reconciliation pattern building on the general controller model (Chapter 06 Section 5), but with strict **ordering** (unlike ReplicaSets, which create/delete Pods in no particular order) and **persistent per-ordinal storage identity** (unlike Deployments, whose Pods share an interchangeable, stateless template).

---

## 13. Real-World Examples

1. **Relational databases** (PostgreSQL, MySQL) deployed in a primary/replica cluster topology rely on StatefulSets so each replica keeps its own data directory and a stable name distinguishing the primary from replicas.
2. **Distributed consensus systems** (etcd itself, Chapter 07 Section 4.2; ZooKeeper; Kafka with KRaft) require each member to have a stable, known identity to participate correctly in leader election and quorum.
3. **Message queue clusters** (Kafka, RabbitMQ) use StatefulSets so each broker retains its own partition data across restarts, addressable by a predictable name.
4. **Elasticsearch clusters** use StatefulSets to give each node stable storage for its shard data and a predictable identity for cluster topology awareness.
5. **Any "scale to zero and back" stateful workload** benefits from StatefulSets' guarantee that scaling back up reattaches existing data rather than starting fresh, unlike a Deployment's interchangeable Pods.

---

## 14. Best Practices

- Only use a StatefulSet when your application genuinely needs stable identity and/or stable per-replica storage — for ordinary stateless apps, a Deployment is simpler and more flexible.
- Always pair a StatefulSet with a Headless Service (matching `serviceName`) if peer-to-peer addressing by name is required.
- Set `podManagementPolicy: Parallel` only when your application doesn't actually require strict ordering — this speeds up scaling but forfeits the ordered guarantee.
- Plan storage class and size carefully in `volumeClaimTemplates` — PVCs created this way are **not** automatically deleted when the StatefulSet is deleted (deliberately, to prevent accidental data loss), so plan cleanup explicitly.

---

## 15. Common Mistakes

- Using a StatefulSet for a genuinely stateless application, adding unnecessary ordering constraints and slower scale-up/rollout behavior for no benefit.
- Forgetting to create the accompanying Headless Service, breaking the stable per-Pod DNS resolution the StatefulSet depends on.
- Assuming deleting a StatefulSet also deletes its PVCs — it does not, by design; leftover PVCs must be cleaned up manually if no longer needed.
- Expecting all Pods to start simultaneously like a Deployment, then being confused when only `db-0` appears before `db-1` even starts.

---

## 16. Troubleshooting

| Symptom | Likely Cause | Debugging Commands | Fix |
|---|---|---|---|
| Only the first Pod (`-0`) ever starts | It's not passing readiness checks, blocking ordered creation of subsequent Pods | `kubectl describe pod <name>-0`, `kubectl logs` | Fix the underlying readiness/startup issue on the first Pod |
| Per-Pod DNS name doesn't resolve | Missing or misconfigured Headless Service, or `serviceName` mismatch | `kubectl get svc`, `kubectl describe sts` | Ensure Headless Service exists and `serviceName` matches |
| New Pod after deletion doesn't have old data | PVC was deleted, or `volumeClaimTemplates` misconfigured | `kubectl get pvc` | Verify PVC still exists and is correctly bound |
| Scaling down doesn't remove PVCs | Expected behavior — PVCs are retained deliberately | `kubectl get pvc` | Manually delete PVCs if data is no longer needed |

---

## 17. Comparison Tables

**StatefulSet vs Deployment:**

| Aspect | Deployment | StatefulSet |
|---|---|---|
| Pod identity | Interchangeable, random suffix | Stable, ordinal-based (`-0`, `-1`, ...) |
| Storage | Typically shared/ephemeral or one shared PVC | Dedicated, per-Pod PVC that follows the same ordinal |
| Creation/scaling order | Unordered, parallel | Strictly ordered, one at a time |
| Typical workload | Stateless web apps | Databases, queues, consensus systems |

---

## 18. Memory Tricks

- **"StatefulSet = hospital room numbers, Deployment = hotel room service."** Rooms (identities) are permanent and specific; hotel staff (Pods in a Deployment) are interchangeable.
- **"Headless Service = phonebook for individuals, regular Service = one shared reception desk."**
- Ordering mnemonic: **"Up in order, down in reverse"** — scale up creates 0,1,2...; scale down deletes highest ordinal first.

---

## 19. Interview Questions

**Easy:**
1. What three guarantees does a StatefulSet provide that a Deployment does not?
   *Expected answer:* Stable, unique network identity (predictable Pod names and DNS via a Headless Service), stable per-Pod persistent storage (via `volumeClaimTemplates`, reattached to the same-ordinal Pod across restarts), and ordered, sequential Pod creation/scaling/deletion.

**Medium:**
2. Why does a StatefulSet need a Headless Service instead of a regular Service?
   *Expected answer:* A regular Service intentionally abstracts away individual Pod identity behind one virtual IP, load-balancing across all matching Pods — appropriate for interchangeable, stateless replicas. A StatefulSet's Pods are NOT interchangeable; each has a distinct role and identity, so applications need to address a *specific* Pod by name (e.g., "always connect to db-0, the primary"). A Headless Service (`clusterIP: None`) enables this by providing direct DNS resolution to each individual Pod's stable name, rather than hiding them behind one shared address.

**Hard:**
3. A team deletes a StatefulSet with `kubectl delete sts db` expecting a completely clean slate, then recreates it with the same manifest — but the new Pods immediately show old data from before. Explain why, and how to actually get a clean slate if that was the real intent.
   *Expected answer:* PersistentVolumeClaims created via `volumeClaimTemplates` are deliberately NOT deleted when the StatefulSet itself is deleted — this is a safety measure to prevent StatefulSets from being able to accidentally destroy valuable stateful data through a simple object deletion. When the StatefulSet is recreated with the same name and the same `volumeClaimTemplates`, Kubernetes reattaches to the existing, matching PVCs (e.g., `data-db-0`), bringing back the old data. To actually get a clean slate, the team must explicitly delete the underlying PVCs (`kubectl delete pvc -l app=db` or by name) in addition to deleting the StatefulSet, then recreate it — at which point fresh, empty PVCs will be provisioned.

---

## 20. KCNA Practice Questions

**Q1.** What is the primary purpose of a StatefulSet?
A. To run exactly one Pod per node in the cluster
B. To provide stable identity, stable storage, and ordered operations for Pods
C. To automatically scale Pods based on CPU usage
D. To manage rolling updates without any ordering guarantees

**Correct answer: B**
*Explanation:* StatefulSets exist specifically to give Pods stable names, stable per-Pod storage, and ordered creation/scaling/deletion — needed for stateful applications like databases. A describes a DaemonSet (Chapter 13). C describes a Horizontal Pod Autoscaler (Chapter 20), not a StatefulSet. D is the opposite of a StatefulSet's defining behavior.

---

**Q2.** Why do StatefulSet Pods require a Headless Service?
A. To disable networking entirely for security
B. To provide each Pod a stable, individually resolvable DNS name instead of one shared load-balanced address
C. To allow Pods to be scheduled on any node without restriction
D. Headless Services are required for all Kubernetes workloads, not just StatefulSets

**Correct answer: B**
*Explanation:* A Headless Service enables direct DNS resolution to individual Pods by name, which stateful applications need to address specific peers. A misdescribes what "headless" means. C is unrelated to Headless Services. D is false — most workloads use regular Services.

---

**Q3.** In what order does a StatefulSet scale down its Pods?
A. Random order
B. Lowest ordinal first (e.g., Pod-0 deleted before Pod-2)
C. Highest ordinal first (e.g., Pod-2 deleted before Pod-0)
D. All Pods are deleted simultaneously

**Correct answer: C**
*Explanation:* StatefulSets scale down in reverse ordinal order, removing the highest-numbered Pod first, preserving the lower, typically more foundational ordinals (like the primary at ordinal 0) as long as possible. A, B, and D misstate this ordering guarantee.

---

**Q4.** What happens to a StatefulSet Pod's PersistentVolumeClaim if the Pod is deleted and recreated by the controller?
A. A brand-new, empty PVC is always created
B. The same PVC is reattached to the new Pod with the same ordinal, preserving its data
C. The PVC is permanently deleted and cannot be recovered
D. The PVC is migrated to a different StatefulSet automatically

**Correct answer: B**
*Explanation:* This PVC-reattachment-by-ordinal behavior is exactly what gives StatefulSet Pods persistent identity-linked storage across restarts. A, C, and D misstate this core StatefulSet guarantee.

---

**Q5.** What happens to a StatefulSet's PersistentVolumeClaims when the StatefulSet itself is deleted?
A. They are automatically and immediately deleted along with the StatefulSet
B. They are retained by default, requiring a separate, explicit deletion step
C. They are automatically transferred to a Deployment
D. They are automatically backed up to external storage

**Correct answer: B**
*Explanation:* PVCs created via `volumeClaimTemplates` are deliberately retained after StatefulSet deletion as a data-safety measure — deleting them requires a separate, explicit action. A, C, and D describe behaviors that do not occur automatically.

---

**Q6.** What naming pattern does a StatefulSet use for its Pods?
A. A random alphanumeric suffix, like a ReplicaSet
B. `<statefulset-name>-<ordinal>`, e.g., `web-0`, `web-1`, `web-2`
C. `<node-name>-<statefulset-name>`
D. A UUID generated fresh on every restart

**Correct answer: B**
*Explanation:* This predictable ordinal-suffix naming is the foundation of a StatefulSet's stable identity guarantee. A describes Deployment/ReplicaSet Pod naming, which is exactly what StatefulSets avoid. C and D are not real Kubernetes naming schemes.

---

**Q7.** During scale-up, what must happen before a StatefulSet controller creates the next ordinal Pod?
A. Nothing — all Pods are created simultaneously
B. The previous ordinal Pod must be Running and Ready
C. The cluster administrator must manually approve it
D. All PersistentVolumes must be pre-provisioned across the entire cluster

**Correct answer: B**
*Explanation:* Ordered scale-up requires each Pod to reach Running+Ready before the next ordinal starts — this is the "ordered deployment" guarantee. A describes Deployment/ReplicaSet behavior. C and D are not part of the StatefulSet mechanism.

---

**Q8.** A StatefulSet named `cache` with `replicas: 4` is scaled down to `replicas: 2`. Which Pods are deleted?
A. `cache-0` and `cache-1`
B. `cache-2` and `cache-3`
C. Two randomly chosen Pods
D. All four Pods are deleted, then two new ones are created

**Correct answer: B**
*Explanation:* Scale-down removes the highest ordinals first (reverse order), so `cache-3` is deleted before `cache-2`, leaving `cache-0` and `cache-1` intact. A, C, and D contradict the reverse-ordinal scale-down guarantee.

---

**Q9.** Why does `volumeClaimTemplates` create a separate PVC per Pod instead of one shared PVC for all replicas?
A. Because Kubernetes does not support shared PVCs at all
B. Because each StatefulSet Pod needs its own independent, dedicated storage tied to its specific identity (e.g., its own database data directory)
C. To reduce total storage cost
D. Because ReadWriteMany volumes are always required for StatefulSets

**Correct answer: B**
*Explanation:* Stateful applications like databases require each replica to have distinct, non-shared data (e.g., `db-1` must not overwrite `db-0`'s data) — hence a dedicated, per-ordinal PVC. A is false — shared PVCs are possible in other contexts. C is not the rationale. D is false; `ReadWriteOnce` is shown in the example (Section 9) and is typical.

---

**Q10.** What does `spec.serviceName` in a StatefulSet manifest do?
A. Sets the container image's registry endpoint
B. Links the StatefulSet to the Headless Service that provides its Pods' stable DNS names
C. Defines the port the application listens on
D. Specifies which node the Pods must run on

**Correct answer: B**
*Explanation:* `serviceName` tells the StatefulSet controller which Headless Service governs the per-Pod DNS domain (Section 9's YAML) — without this link, the stable DNS naming in Section 4.2 would not function correctly. A, C, and D describe unrelated configuration concerns.

---

**Q11.** A team observes that `db-0` is stuck and never becomes Ready, and consequently `db-1` and `db-2` are never created. What StatefulSet behavior explains this?
A. A bug — this should never happen
B. The ordered creation guarantee: each Pod must be Ready before the next ordinal is created, so a stuck first Pod blocks all subsequent ones
C. StatefulSets always create all Pods regardless of readiness
D. `db-1` and `db-2` were deleted by an administrator

**Correct answer: B**
*Explanation:* This is expected StatefulSet behavior (Section 16's troubleshooting table) — the strict ordering guarantee means a failing lower ordinal blocks higher ordinals from being created at all. A mischaracterizes intended behavior as a bug. C contradicts the ordered guarantee. D is an unsupported assumption given the evidence.

---

**Q12.** Which workload is the BEST fit for a StatefulSet rather than a Deployment?
A. A stateless REST API with no local data
B. A three-node etcd cluster requiring stable peer identity for quorum and leader election
C. A static website served from a CDN-backed container
D. A batch job that runs once and exits

**Correct answer: B**
*Explanation:* Distributed consensus systems like etcd (Section 13) fundamentally require stable, known peer identities to function correctly — the core use case for StatefulSets. A and C are ideal Deployment use cases. D is better suited to a Job (Chapter 15).

---

**Q13.** What is `podManagementPolicy: Parallel` used for?
A. To make Pod deletion faster by skipping graceful termination
B. To relax the strict ordered creation/deletion guarantee, allowing Pods to start or stop concurrently when the application doesn't require ordering
C. To evenly distribute Pods across availability zones
D. To enable horizontal autoscaling for a StatefulSet

**Correct answer: B**
*Explanation:* Per Section 14's best practices, `Parallel` should only be set when the application genuinely doesn't need the ordering guarantee, trading it for faster scaling. A misdescribes the setting. C and D describe unrelated features (topology spread constraints and HPA, respectively).

---

**Q14.** Why can't a regular (non-headless) Service be used to give each StatefulSet Pod its own resolvable DNS name?
A. Regular Services don't support DNS at all
B. A regular Service load-balances to one shared virtual IP, deliberately hiding which specific Pod is being reached — the opposite of what per-Pod addressing requires
C. Regular Services only work with Deployments, never with StatefulSets
D. Regular Services require a static IP allocation per Pod, which is cost-prohibitive

**Correct answer: B**
*Explanation:* Section 4.2 explains that a regular Service's abstraction (any of N interchangeable Pods) is precisely backwards for stateful workloads that need to reach a *specific* named peer. A is false — Services do integrate with DNS, just not per-Pod. C is false; regular Services can front StatefulSet Pods too, just without per-Pod resolution. D misstates the actual mechanism (headless DNS, not static IPs).

---

**Q15.** What happens by default during a StatefulSet rolling update?
A. All Pods are replaced simultaneously
B. Pods are updated one at a time, in reverse ordinal order, each becoming Ready before the next is updated
C. Only the Pod with the lowest ordinal is ever updated
D. Updates require manually deleting each Pod one by one with no controller involvement

**Correct answer: B**
*Explanation:* Per Section 4.4's ordered-operations table, the default rolling update strategy mirrors the reverse-order scale-down pattern — highest ordinal updated first, one at a time. A describes `Recreate`/parallel behavior, not the default. C is false — all Pods are eventually updated. D is false; the controller manages this automatically, unlike manual `OnDelete`-style intervention.

---

**Q16.** A StatefulSet's Pod `db-1` is rescheduled to a different node after that node fails. What happens to its identity and storage?
A. It becomes `db-3` on the new node, with fresh empty storage
B. It remains named `db-1`, and reattaches to its existing PVC `data-db-1`, preserving both identity and data
C. It is permanently lost and cannot be recovered
D. Its data is copied to all other StatefulSet Pods automatically

**Correct answer: B**
*Explanation:* This identity-and-storage stability across rescheduling is the central StatefulSet guarantee (Sections 4.1, 4.3). A contradicts stable ordinal naming. C and D describe behaviors that don't occur — no data loss and no automatic replication happens by default.

---

**Q17.** Why are StatefulSet PVCs deliberately NOT deleted when the StatefulSet is deleted?
A. Kubernetes has a technical limitation preventing PVC cleanup
B. To protect against accidental, irreversible data loss from a simple object-deletion command
C. Because PVCs are always shared with other, unrelated StatefulSets
D. Because deleting a PVC requires cluster administrator approval regardless of context

**Correct answer: B**
*Explanation:* This is an explicit safety design choice (Sections 14 and 17's interview Q3) — a StatefulSet holding valuable data shouldn't be irrecoverably destroyed by a single `kubectl delete sts`. A is false; Kubernetes could delete them but deliberately doesn't by default. C and D are incorrect statements about PVC behavior.

---

**Q18.** Comparing a StatefulSet to a Deployment, which statement is TRUE?
A. Both provide identical Pod naming and storage guarantees
B. A StatefulSet's Pods have stable, ordinal-based identity and dedicated storage, while a Deployment's Pods are interchangeable with random suffixes and typically share or don't rely on stable storage
C. A Deployment always creates Pods in strict order, exactly like a StatefulSet
D. Only Deployments support rolling updates; StatefulSets cannot be updated

**Correct answer: B**
*Explanation:* This is the fundamental distinction drawn throughout the chapter and summarized in Section 17's comparison table. A is false — that's precisely what differs between them. C is false; Deployments create Pods in no particular order. D is false — StatefulSets also support rolling updates (Q15), just with different ordering semantics.

---

**Q19.** Using the "hospital rooms vs. hotel room service" memory trick (Section 18), which best matches a Deployment's Pods?
A. Numbered hospital rooms, each with a permanent chart and identity
B. Interchangeable hotel room-service staff, where any staff member can serve any room
C. A dedicated parking spot reserved for one specific car
D. A safe-deposit box accessible only by one specific customer

**Correct answer: B**
*Explanation:* The mnemonic maps Deployment Pods to interchangeable hotel staff — any replica can serve any request, with no persistent individual identity. A, C, and D all describe stable, dedicated identity/storage — the StatefulSet side of the analogy, not the Deployment side.

---

**Q20.** A StatefulSet is deployed without any accompanying Headless Service. What is the most likely observable consequence?
A. The StatefulSet will fail to create any Pods at all
B. Pods will still be created and scaled in order, but per-Pod stable DNS names (e.g., `db-1.db-headless...`) will not resolve correctly
C. All Pods will automatically be converted into a Deployment
D. PersistentVolumeClaims will fail to bind

**Correct answer: B**
*Explanation:* Per Section 16's troubleshooting table, a missing or misconfigured Headless Service breaks per-Pod DNS resolution specifically — but Pod creation, ordering, and storage are governed independently and still function. A overstates the failure mode. C and D describe unrelated failures not caused by a missing Headless Service.

---

## 21. Chapter Summary (One-Page Revision Sheet)

- A **StatefulSet** provides three guarantees a Deployment does not: **stable identity** (ordinal-based Pod names), **stable storage** (per-Pod PVCs via `volumeClaimTemplates`, reattached across restarts), and **ordered operations** (created/updated 0→N, deleted N→0).
- A **Headless Service** (`clusterIP: None`) gives each Pod its own resolvable DNS name — essential for addressing specific peers in a stateful cluster.
- PVCs are **retained** when a StatefulSet is deleted — a deliberate safety measure requiring explicit manual cleanup.
- Classic use cases: **databases, message queues, distributed consensus systems** — anything where each replica has a distinct role and its own persistent data.

---

### Chapter Completion Checklist

1. **Topics covered:** StatefulSet's three guarantees, Headless Services, volumeClaimTemplates, ordered scaling/updates.
2. **KCNA objectives completed:** The identity-and-storage-stable workload controller, completing the trio of major controllers alongside Deployments (Ch.12) and DaemonSets (Ch.13).
3. **Remaining objectives:** Run-to-completion workloads — Jobs and CronJobs (Chapter 15).
4. **Suggested revision checklist:** Recite the three StatefulSet guarantees from memory; explain why a Headless Service is required; explain why PVCs survive StatefulSet deletion.
5. **Suggested hands-on exercises:** Complete Lab 2 (data persists across Pod deletion) — this single exercise makes the "stable storage" guarantee concrete and memorable.
6. **Related chapters:** Previous: [13-DaemonSets](../13-DaemonSets/README.md). Next: [15-Jobs-and-CronJobs](../15-Jobs-and-CronJobs/README.md) — workloads that run to completion instead of running indefinitely.
