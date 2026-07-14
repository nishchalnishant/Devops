# 07 — The Control Plane (Deep Dive)

## 1. Learning Objectives

By the end of this chapter you will be able to:

- Explain in depth what kube-apiserver, etcd, kube-scheduler, and kube-controller-manager each do, and how they interact.
- Describe the watch/event mechanism that lets every component react to changes without polling.
- Explain etcd's consistency model (Raft) at a conceptual level and why it matters for cluster reliability.
- Explain how the scheduler picks a node using filtering and scoring.
- Name the built-in controllers running inside kube-controller-manager and what each reconciles.
- Understand high-availability (HA) control plane topology.

**KCNA objectives covered:** Kubernetes Fundamentals domain — this is the detailed follow-up to Chapter 06's high-level architecture.

---

## 2. Historical Background

Chapter 06 established that Kubernetes' control plane concept traces back to Borg's centralized "brain." Each individual control plane component has its own smaller history worth knowing:

- **etcd** was created by CoreOS in 2013, originally for their own container-focused Linux distribution, as a distributed, strongly-consistent key-value store. Kubernetes adopted it early on specifically because Kubernetes needed a reliable, distributed "single source of truth" — building a custom one from scratch would have been reinventing a hard, already-solved distributed-systems problem.
- **kube-apiserver** was designed from Kubernetes' earliest versions as a RESTful, resource-oriented API — a deliberate design choice so that literally everything (users via kubectl, controllers, kubelet, third-party tools) talks to the cluster through one uniform, well-documented interface, rather than each component needing custom integration logic.
- **kube-scheduler** and **kube-controller-manager** were split into separate binaries/processes specifically so that each can fail, restart, or scale independently — a reflection of Kubernetes' general design philosophy of small, single-responsibility components communicating through the shared API server/etcd state, rather than one large monolithic "master process."

---

## 3. Motivation: Why Does Each Component Need to Exist Separately?

**Analogy — The Hospital:**
Think of a hospital. The **medical records system** (etcd) holds every patient's chart — the definitive truth about who is where and what treatment they need. The **front desk** (kube-apiserver) is the only official channel through which anyone — doctors, nurses, insurance companies — reads or updates those records; nobody walks directly into the records room. The **bed assignment coordinator** (kube-scheduler) decides which specific room and bed a new patient should go to, based on availability and needs. Numerous **specialist teams** (the controllers inside kube-controller-manager) each watch for a *specific* kind of situation — one team watches for patients who need a follow-up visit scheduled, another watches for expired prescriptions needing renewal — each team focused narrowly on its own responsibility, all reading/writing through the same front desk and records system.

### 3.1 How Was This Solved Before Kubernetes (or in cruder systems)?

Earlier or simpler orchestration approaches often bundled scheduling, state storage, and reconciliation logic together in monolithic or ad hoc ways, or relied on external, less consistent state stores. This made components harder to scale, upgrade, or reason about independently, and increased the blast radius of any single bug.

### 3.2 How Kubernetes Solves It

Kubernetes cleanly separates **storage** (etcd), **the single API gateway** (kube-apiserver), **placement decisions** (kube-scheduler), and **ongoing reconciliation logic** (kube-controller-manager) into independent processes that only communicate by reading/writing objects through the API server. This separation of concerns is what lets each piece be independently replaced, scaled, restarted, or even swapped for an alternative implementation without the others needing to know or care.

---

## 4. Core Concepts

### 4.1 kube-apiserver — The Front Door

**Definition:** kube-apiserver is a RESTful HTTP(S) server that is the single entry point for all reads and writes to the cluster's state. Every other component — kubectl, kubelet, the scheduler, controllers, even other control plane components — communicates exclusively through it. Nothing is allowed to talk to etcd directly except the API server itself.

Responsibilities:
- **Authentication** — who are you? (certificates, tokens, OIDC, etc.)
- **Authorization** — are you allowed to do this? (commonly RBAC — full detail in Chapter 21)
- **Admission Control** — should this specific request be allowed/mutated, even if authorized? (e.g., validating webhooks, default value injection)
- **Validation** — is this object syntactically and semantically valid?
- **Persistence** — write the validated object to etcd
- **Watch/Notify** — notify any component that has subscribed ("is watching") for changes to relevant objects

### 4.2 etcd — The Single Source of Truth

**Definition:** etcd is a distributed, strongly consistent key-value store that holds the complete state of the cluster — every object's desired and last-known-actual state.

**Why strong consistency matters:** Imagine two schedulers both believing a given node has free capacity and both assigning a Pod to it simultaneously, because they read stale/conflicting data — you'd get resource oversubscription and outages. etcd solves this using the **Raft consensus algorithm**, ensuring that even when etcd itself runs as multiple replicas (typically 3 or 5 for HA), all replicas agree on a single, consistent view of the data at all times, with a single elected "leader" replica handling writes at any given moment.

**Analogy — The Bank Ledger:** Multiple bank branches (etcd replicas) must always agree on your exact account balance; if one branch had a slightly different, stale number, you could withdraw the same money twice. Raft is the strict, majority-agreement process that keeps every branch's ledger identical.

### 4.3 kube-scheduler — Placement Decisions

**Definition:** kube-scheduler watches for Pods that have been created but not yet assigned to a node (`nodeName` is empty), and assigns each one to a suitable node.

**Two-phase scheduling process:**

1. **Filtering (Predicates):** Eliminate nodes that *cannot* run this Pod at all — e.g., insufficient CPU/memory, a `NodeSelector`/`nodeAffinity` mismatch, a taint the Pod doesn't tolerate (Chapter 20 goes deep on taints/tolerations).
2. **Scoring (Priorities):** Among the remaining valid nodes, score each one — e.g., preferring nodes with more free resources, spreading Pods across failure domains for availability — and pick the highest-scoring node.

```
   All Nodes
       │
       ▼
 ┌──────────┐   Remove nodes that fail hard requirements
 │ Filtering  │   (insufficient resources, taints, etc.)
 └──────────┘
       │
       ▼
 ┌──────────┐   Score remaining valid nodes
 │  Scoring   │   (prefer balanced resource usage, spreading, etc.)
 └──────────┘
       │
       ▼
  Highest-scoring node selected → Pod's nodeName is set
```

### 4.4 kube-controller-manager — The Reconciliation Engine

**Definition:** kube-controller-manager runs many individual **controllers**, each implementing one instance of the reconciliation loop from Chapter 06, Section 4.5, watching one specific type of resource.

| Built-in Controller | What It Reconciles |
|---|---|
| Node Controller | Detects when nodes become unreachable and marks them accordingly, evicting Pods if needed |
| Replication/ReplicaSet Controller | Ensures the correct number of Pod replicas exist (Chapter 11) |
| Deployment Controller | Manages rolling updates/rollbacks via ReplicaSets (Chapter 12) |
| Job Controller | Ensures batch Jobs run to completion (Chapter 15) |
| Endpoints/EndpointSlice Controller | Keeps track of which Pods back a given Service (Chapter 16) |
| Namespace Controller | Handles namespace lifecycle, including cleanup on deletion |
| Service Account Controller | Creates default ServiceAccounts and their tokens |

All of these controllers run inside the single `kube-controller-manager` binary/process for operational simplicity, but are logically independent loops.

### 4.5 The Watch Mechanism (How Components Avoid Constant Polling)

Rather than every component repeatedly asking "has anything changed yet?" (wasteful polling), Kubernetes components open a long-lived **watch** connection to the API server, and the API server *pushes* change notifications the instant something relevant changes. This is why reconciliation reacts within milliseconds of a change rather than on some fixed polling interval — a critical detail for both performance and the "instant self-healing" behavior demonstrated in Chapter 06's Lab 2.

---

## 5. Internal Working

```
1. kubectl (or any client) sends an HTTPS request to kube-apiserver
        ↓
2. kube-apiserver: Authenticate → Authorize → Admission Control → Validate
        ↓
3. kube-apiserver writes the object to etcd (via the Raft-backed etcd cluster)
        ↓
4. etcd confirms the write is committed (majority of replicas agree)
        ↓
5. kube-apiserver sends a "watch" notification to every subscribed component
   (scheduler, relevant controllers, kubelet on relevant nodes)
        ↓
6. Each subscribed component reacts: scheduler assigns unscheduled Pods,
   controllers reconcile their specific resource type, kubelet starts containers
        ↓
7. Each component reports resulting status changes back through kube-apiserver,
   which persists them to etcd — closing the loop
```

---

## 6. Architecture

```
┌───────────────────────────────────────────────────────────────┐
│                         CONTROL PLANE                             │
│                                                                      │
│   ┌────────────┐        watch/write         ┌──────────────┐  │
│   │   Clients    │ ──────────────────────► │ kube-apiserver │  │
│   │ (kubectl,     │ ◄────────────────────── │ (auth, admission,│  │
│   │  kubelet, etc)│      notify/response      │  validation)     │  │
│   └────────────┘                            └──────┬───────┘  │
│                                                        │ read/write   │
│                                                        ▼              │
│                                               ┌──────────────┐    │
│                                               │      etcd        │    │
│                                               │ (Raft-consistent, │    │
│                                               │  3 or 5 replicas)  │    │
│                                               └──────────────┘    │
│                                                        ▲              │
│                                          watch          │              │
│                    ┌───────────────────────┼──────────────┐   │
│                    │                                │               │   │
│           ┌──────────────┐              ┌──────────────┐   │
│           │ kube-scheduler │              │kube-controller-│   │
│           │ (filter+score) │              │    manager      │   │
│           │                │              │ (Node, RS, Job, │   │
│           │                │              │  Deployment...) │   │
│           └──────────────┘              └──────────────┘   │
└───────────────────────────────────────────────────────────────┘
```

---

## 7. Component Breakdown

| Component | Reads From | Writes To | Talks Directly To etcd? |
|---|---|---|---|
| kube-apiserver | Client requests | etcd | Yes — the only component allowed to |
| etcd | kube-apiserver only | Itself (replicated via Raft) | N/A |
| kube-scheduler | kube-apiserver (watch) | kube-apiserver (Pod binding) | No |
| kube-controller-manager | kube-apiserver (watch) | kube-apiserver (object updates) | No |

---

## 8. Important Terminology

| Term | Meaning |
|---|---|
| RESTful API | An API structured around resources (nouns) and standard HTTP verbs (GET, POST, PUT, DELETE) |
| Admission Controller | A plugin in kube-apiserver's request pipeline that can validate or mutate objects before they're persisted |
| Raft | A consensus algorithm ensuring distributed replicas (like etcd's) agree on a single consistent state |
| Watch | A long-lived connection where the API server pushes change notifications instead of clients polling |
| Predicate (Filtering) | A hard scheduling requirement a node must satisfy to be eligible for a Pod |
| Priority (Scoring) | A soft scheduling preference used to rank eligible nodes |
| Controller | A control loop that watches one resource type and reconciles actual state toward desired state |
| Leader election | The process by which HA control plane components agree on a single active instance to avoid conflicting actions |

---

## 9. YAML Deep Dive

Still no new user-facing object type — but it's worth seeing what a **raw API request** looks like, since this is literally what kubectl generates and sends to kube-apiserver under the hood:

```
POST /api/v1/namespaces/default/pods
Content-Type: application/json
Authorization: Bearer <token>

{
  "apiVersion": "v1",
  "kind": "Pod",
  "metadata": { "name": "demo-pod" },
  "spec": { "containers": [{ "name": "nginx", "image": "nginx" }] }
}
```

This is the literal HTTP call underlying every `kubectl apply -f pod.yaml` — YAML is simply converted to this JSON request form before being sent.

---

## 10. kubectl Commands

| Command | Purpose | Example |
|---|---|---|
| `kubectl get pods -v=8` | Show verbose HTTP request/response to kube-apiserver | `kubectl get pods -v=8` |
| `kubectl get events` | Show cluster events, often generated by controllers | `kubectl get events --sort-by=.lastTimestamp` |
| `kubectl describe node <node>` | Inspect node conditions/capacity used by the scheduler | `kubectl describe node worker-1` |
| `kubectl get pods -o wide` | Show which node each Pod was scheduled to | `kubectl get pods -o wide` |
| `kubectl api-resources` | List every resource type kube-apiserver understands | `kubectl api-resources` |

---

## 11. Hands-on Examples

**Lab 1 — Observe the scheduler's decision:**
```bash
kubectl run test-pod --image=nginx
kubectl get pod test-pod -o wide
# Note the NODE column — that's kube-scheduler's decision
kubectl describe pod test-pod
# Look at the Events section: "Successfully assigned default/test-pod to <node>"
```

**Lab 2 — Force a scheduling failure and observe the Events:**
```bash
kubectl run big-pod --image=nginx --requests='memory=10000Gi'
kubectl describe pod big-pod
# Events will show: "0/N nodes are available: insufficient memory"
# — this is the Filtering phase (Section 4.3) rejecting every node
```

**Lab 3 — Watch a controller react:**
```bash
kubectl create deployment demo --image=nginx --replicas=2
kubectl get events --watch
# In another terminal: kubectl delete pod <one-of-the-pods>
# Watch events stream: a new Pod is created almost instantly —
# this is the ReplicaSet controller's reconciliation loop reacting
# to the watch notification described in Section 4.5
```

---

## 12. Internal Flow

See Section 5's full 7-step flow — this is the detailed version of Chapter 06 Section 5, now naming exactly which sub-mechanism (auth/admission/etcd Raft commit/watch) handles each step.

---

## 13. Real-World Examples

1. **Large enterprises running multi-region clusters** run etcd across 5 replicas instead of 3, trading slightly higher write latency for greater fault tolerance (can survive 2 replica failures instead of 1).
2. **Admission controllers** are how tools like **OPA Gatekeeper** and **Kyverno** (Chapter 14/21) enforce organizational policy (e.g., "no container may run as root") — they plug directly into kube-apiserver's admission pipeline described in Section 4.1.
3. **Cloud providers' managed Kubernetes offerings** (GKE, EKS, AKS) fully manage etcd and the API server for you specifically because etcd operations (backup, Raft health, disk I/O tuning) are notoriously operationally demanding — a major selling point of managed control planes.
4. **Custom schedulers** are used by some large-scale ML platforms to implement specialized scoring logic (e.g., GPU topology awareness) beyond the built-in kube-scheduler's priorities, using the exact filtering/scoring extension points described in Section 4.3.
5. **etcd data loss incidents** are among the most feared outages in Kubernetes operations — several public postmortems (e.g., from companies running self-managed clusters) describe multi-hour recovery efforts, reinforcing why Section 14's etcd backup best practice is non-negotiable in production.

---

## 14. Best Practices

- Run an odd number of etcd replicas (3 or 5) — Raft requires a majority to agree, and odd numbers avoid tie-vote scenarios.
- Take regular etcd snapshots/backups and periodically test restoring from them — an untested backup is not a real backup.
- Use admission control (validating/mutating webhooks) to enforce organizational policies at the point of entry, rather than after the fact.
- Run multiple replicas of kube-apiserver and kube-controller-manager/kube-scheduler behind leader election for high availability in production.
- Monitor etcd latency and disk I/O closely — etcd is highly sensitive to slow disks, since every write must be durably committed via Raft before being acknowledged.

---

## 15. Common Mistakes

- Allowing any component other than kube-apiserver to talk to etcd directly — this bypasses authentication, authorization, and validation entirely and is a serious security/consistency risk.
- Running etcd on slow or shared disks, causing Raft commit latency spikes that can destabilize the entire cluster.
- Assuming the scheduler considers only CPU/memory — forgetting taints, affinity/anti-affinity, and topology spread constraints (Chapter 20) can lead to confusing "why won't this Pod schedule" situations.
- Treating kube-controller-manager as "one thing" rather than understanding it hosts many independent controllers, each with its own specific responsibility and potential failure mode.

---

## 16. Troubleshooting

| Symptom | Likely Cause | Debugging Commands | Fix |
|---|---|---|---|
| Pod stuck `Pending` with "0/N nodes available" | Scheduler filtering rejected every node | `kubectl describe pod <name>` | Check resource requests, taints/tolerations, node affinity |
| `kubectl` requests time out | kube-apiserver unreachable or overloaded | `kubectl cluster-info`, check API server logs | Scale/restart API server, check network path |
| Cluster-wide slowness on writes | etcd disk I/O or Raft leader election churn | Check etcd metrics/logs directly | Improve etcd disk performance, check network between etcd replicas |
| Crashed Pods not replaced | Relevant controller (e.g., ReplicaSet controller) not running/stalled | `kubectl get pods`, check controller-manager logs | Restart/investigate controller-manager |

---

## 17. Comparison Tables

**Filtering vs Scoring (Scheduler):**

| Aspect | Filtering (Predicates) | Scoring (Priorities) |
|---|---|---|
| Question answered | "Can this node run the Pod at all?" | "Which eligible node is the *best* fit?" |
| Type of requirement | Hard (pass/fail) | Soft (ranked preference) |
| Example | Node lacks required CPU → excluded | Node has more free resources → scores higher |

**kube-apiserver vs etcd:**

| Aspect | kube-apiserver | etcd |
|---|---|---|
| Role | Gatekeeper: auth, validation, admission | Storage: durable, consistent state |
| Talks to clients? | Yes | No — only kube-apiserver |
| Stateless? | Yes (can run many replicas easily) | No — stateful, replicated via Raft |

---

## 18. Memory Tricks

- **"etcd is the ledger, API server is the teller — customers never touch the vault directly."**
- **Scheduler = "filter, then score."** Two words, two phases, in that order.
- **"Watch, don't poll"** — the API server pushes; components don't ask repeatedly.
- Controllers inside kube-controller-manager: think of it as **one office building housing many independent specialist teams**, each watching their own inbox.

---

## 19. Interview Questions

**Easy:**
1. What is the only control plane component allowed to communicate directly with etcd?
   *Expected answer:* kube-apiserver. All other components — including the scheduler, controller manager, and kubelet — interact with cluster state exclusively through the API server, never directly with etcd.

**Medium:**
2. Describe the two phases kube-scheduler uses to assign a Pod to a node.
   *Expected answer:* First, Filtering eliminates nodes that cannot run the Pod at all due to hard constraints like insufficient resources, taints without matching tolerations, or node affinity mismatches. Second, Scoring ranks the remaining eligible nodes based on soft preferences such as balanced resource utilization or topology spreading, and the highest-scoring node is selected.

**Hard:**
3. Why does etcd use the Raft consensus algorithm, and what specific problem would occur if it didn't?
   *Expected answer:* etcd typically runs as multiple replicas for fault tolerance, but without a consensus mechanism, different replicas could end up with divergent, conflicting views of cluster state — for example, two replicas both believing they hold the authoritative value for a given key after concurrent writes. Raft solves this by requiring a majority of replicas to agree on every write before it's considered committed, and by electing a single leader to sequence writes, guaranteeing all replicas converge to one consistent, ordered history of state changes. Without it, Kubernetes could suffer from split-brain scenarios such as double-scheduling a Pod onto conflicting resources based on stale data.

---

## 20. KCNA Practice Questions

**Q1.** Which control plane component is the only one permitted to communicate directly with etcd?
A. kube-scheduler
B. kubelet
C. kube-apiserver
D. kube-controller-manager

**Correct answer: C**
*Explanation:* kube-apiserver is the sole gatekeeper to etcd, enforcing authentication, authorization, admission control, and validation before any write. B and D interact with cluster state only through the API server. A also only communicates via the API server, never with etcd directly.

---

**Q2.** What consensus algorithm does etcd use to maintain consistency across its replicas?
A. Paxos
B. Raft
C. Two-Phase Commit
D. Gossip Protocol

**Correct answer: B**
*Explanation:* etcd uses Raft specifically to ensure all replicas agree on a single consistent ordering of state changes via majority agreement and leader election. Paxos (A) is a related but different consensus family not used by etcd. Two-Phase Commit (C) and Gossip Protocols (D) are different distributed-systems techniques not used as etcd's core consensus mechanism.

---

**Q3.** During scheduling, what is the purpose of the "Filtering" phase?
A. To rank eligible nodes from best to worst
B. To eliminate nodes that cannot run the Pod due to hard constraints
C. To assign a priority label to the Pod itself
D. To validate the Pod's YAML syntax

**Correct answer: B**
*Explanation:* Filtering removes nodes that fail hard requirements like insufficient resources or unmet taints/tolerations, leaving only nodes capable of running the Pod at all. Ranking eligible nodes (A) is the Scoring phase, not Filtering. C is not a real scheduling concept. YAML validation (D) happens earlier, in kube-apiserver's own request pipeline, not during scheduling.

---

**Q4.** Why does Kubernetes use a "watch" mechanism instead of having components repeatedly poll the API server?
A. Watching uses less code to implement
B. Polling is not supported by any HTTP server
C. Watch allows the API server to push change notifications instantly, enabling faster reactions and less wasted overhead
D. Watch is required for etcd's Raft algorithm to function

**Correct answer: C**
*Explanation:* The watch mechanism lets subscribed components receive change notifications the moment something relevant changes, rather than wastefully asking repeatedly on a fixed interval — this is directly why Kubernetes reacts to changes (like a crashed Pod) almost instantly. A is not the primary motivation. B is false — polling is technically possible over HTTP. D is unrelated; Raft governs etcd's internal consistency, not the API server's client notification mechanism.

---

**Q5.** Which of the following is a responsibility of kube-apiserver's request-handling pipeline?
A. Deciding which node a Pod should run on
B. Running the reconciliation loop for Deployments
C. Authentication, authorization, admission control, and validation of incoming requests
D. Physically starting containers on a worker node

**Correct answer: C**
*Explanation:* kube-apiserver's pipeline handles authn/authz/admission/validation before persisting any object. A describes kube-scheduler's job. B describes kube-controller-manager. D describes the container runtime managed by kubelet.

---

**Q6.** What does an admission controller do within kube-apiserver's pipeline?
A. Stores the final object permanently in etcd
B. Validates or mutates a request after authentication/authorization but before persistence
C. Assigns the object to a specific worker node
D. Encrypts all traffic between kubelet and the API server

**Correct answer: B**
*Explanation:* Admission controllers run after authn/authz, and can both validate (reject) and mutate (modify) requests before the object is ever persisted to etcd — this is the exact mechanism policy engines like OPA Gatekeeper use. A describes etcd's own role. C describes the scheduler. D describes TLS, an unrelated transport-security mechanism.

---

**Q7.** Which built-in controller is responsible for detecting unreachable nodes and evicting their Pods if necessary?
A. Job Controller
B. Node Controller
C. Namespace Controller
D. Service Account Controller

**Correct answer: B**
*Explanation:* The Node Controller specifically watches node health/reachability and takes action (like marking nodes as unhealthy and evicting Pods) when a node becomes unreachable. A manages batch Job completion, C manages namespace lifecycle, and D manages default ServiceAccount creation — none handle node reachability.

---

**Q8.** In a highly available control plane, why is it common to run 3 or 5 etcd replicas rather than, say, 4?
A. Even numbers of replicas are not supported by any software
B. Odd numbers avoid tie-vote scenarios and still allow majority-based consensus decisions
C. 4 replicas would exceed etcd's maximum supported cluster size
D. Odd numbers reduce network bandwidth usage

**Correct answer: B**
*Explanation:* Raft-based consensus requires a majority vote; odd-numbered clusters (3, 5, 7) avoid the possibility of a tied vote that an even number could produce, while still tolerating some replica failures. A and C are factually incorrect — even-sized clusters are technically possible but simply offer worse fault-tolerance-per-node than the next odd size. D is not a genuine motivation for this practice.

---

**Q9.** If kube-controller-manager stops running entirely, what is the most likely observable impact on the cluster?
A. All currently running Pods immediately terminate
B. New Pods can no longer be scheduled to nodes at all
C. Self-healing reconciliation (e.g., replacing crashed Pods) stops occurring, though already-running Pods are unaffected
D. etcd immediately loses all stored data

**Correct answer: C**
*Explanation:* kube-controller-manager hosts the reconciliation loops (like the ReplicaSet controller) responsible for corrective actions such as replacing crashed Pods; without it, that self-healing stops, but already-running workloads keep running via kubelet independently. A is false per Chapter 06's control-plane-outage behavior. B describes a scheduler outage, not a controller-manager outage — scheduling and reconciliation are separate responsibilities. D is unrelated and false.

---

**Q10.** A Pod remains stuck in `Pending` state, and `kubectl describe pod` shows the event "0/5 nodes are available: insufficient memory." Which scheduling phase caused this outcome?
A. Scoring — all nodes were ranked equally low
B. Filtering — all nodes failed the hard resource requirement check
C. Admission control rejected the Pod
D. The Node Controller marked all nodes as unreachable

**Correct answer: B**
*Explanation:* This message indicates every node failed a hard requirement (available memory) during the Filtering phase, so none advanced to Scoring at all. A is incorrect because Scoring only ranks nodes that already passed Filtering. C would produce a rejection message at request time, not a scheduling-specific "0/5 nodes available" message. D would show nodes as `NotReady` in `kubectl get nodes`, a different and distinguishable symptom.

---

**Q11.** Which control plane component would you check first if newly created objects are being rejected with a validation error before ever reaching etcd?
A. kube-scheduler
B. kube-apiserver's admission/validation pipeline
C. kubelet
D. Node Controller

**Correct answer: B**
*Explanation:* Validation of incoming requests, including schema and admission-policy checks, happens inside kube-apiserver's pipeline before anything is persisted to etcd. kube-scheduler (A) only runs after an object is already persisted and needs node assignment. kubelet (C) runs on worker nodes and never validates API requests. The Node Controller (D) only manages node health/reachability.

---

**Q12.** Why must every control plane component other than kube-apiserver avoid talking to etcd directly?
A. etcd does not support concurrent connections
B. To centralize authentication, authorization, and validation in a single component, preserving data integrity and a consistent access-control boundary
C. Because etcd only accepts read-only queries
D. Because kube-apiserver physically hosts etcd's storage disks

**Correct answer: B**
*Explanation:* Funneling every read/write through kube-apiserver ensures a single, consistent enforcement point for authn/authz/admission — if other components wrote to etcd directly, that safety boundary would be bypassed entirely. A and C are factually false, and D describes no real architectural constraint.

---

**Q13.** What is the role of the Endpoint/EndpointSlice controller within kube-controller-manager?
A. Scheduling Pods onto nodes based on resource availability
B. Keeping the set of ready Pod IPs backing a Service continuously up to date
C. Issuing TLS certificates for API server traffic
D. Electing the Raft leader among etcd replicas

**Correct answer: B**
*Explanation:* This controller watches Pods matching a Service's selector and keeps the Endpoints/EndpointSlice objects synced with their current ready IPs, which kube-proxy then uses for traffic routing. A is kube-scheduler's job, C is unrelated to controller-manager, and D is an etcd-internal process, not a Kubernetes controller.

---

**Q14.** In a highly available control plane with multiple kube-scheduler and kube-controller-manager instances, how is it ensured that only one instance of each is actively making decisions at a time?
A. All instances act simultaneously with no coordination
B. A leader-election mechanism using the API server ensures only one instance is active while the others remain on standby
C. etcd assigns permanent primary/secondary roles at install time
D. Kubernetes disallows running more than one replica of these components

**Correct answer: B**
*Explanation:* kube-scheduler and kube-controller-manager use a leader-election lease stored via the API server; only the elected leader acts, while standby replicas wait to take over if the leader fails — avoiding conflicting simultaneous decisions (ruling out A) without requiring fixed roles (C) or a single-replica restriction (D).

---

**Q15.** Which scenario is a direct consequence of etcd losing quorum (majority of replicas unavailable)?
A. Existing Pods immediately stop running
B. The cluster can no longer accept new writes to cluster state, though already-scheduled workloads continue running via kubelet
C. kube-proxy stops routing any existing traffic
D. All worker nodes reboot automatically

**Correct answer: B**
*Explanation:* Without quorum, etcd cannot commit new writes under Raft, so the API server can't persist changes — meaning no new scheduling or state changes, but nodes/kubelet continue running already-assigned workloads independently, consistent with Chapter 06's control-plane-outage behavior. A, C, and D describe effects with no direct causal link to etcd losing quorum.

---

**Q16.** What distinguishes a mutating admission webhook from a validating admission webhook?
A. Mutating webhooks can modify the request object; validating webhooks can only accept or reject it
B. Validating webhooks run before authentication; mutating webhooks run after
C. There is no functional difference, only naming
D. Mutating webhooks only apply to Namespace objects

**Correct answer: A**
*Explanation:* Mutating webhooks can inject or alter fields in the incoming object (e.g., adding a default sidecar container), and always run before validating webhooks, which can only allow or deny the request as-is without changing it. B reverses the actual ordering relative to authentication. C and D are false.

---

**Q17.** Why does kube-scheduler use a Scoring phase after Filtering rather than just picking the first node that passes Filtering?
A. Scoring is not actually used in modern Kubernetes
B. Scoring allows the scheduler to choose the best-fit node among several valid candidates based on soft preferences like resource balance or topology spread
C. Scoring exists purely for logging purposes
D. Filtering already guarantees only one node remains

**Correct answer: B**
*Explanation:* Multiple nodes commonly pass Filtering; Scoring ranks them by soft preferences (e.g., least-utilized node, spreading across zones) to pick an optimal placement rather than an arbitrary one. A and C are false, and D is incorrect — Filtering often leaves many eligible nodes.

---

**Q18.** A cluster operator notices that deleting a Namespace also eventually removes all objects within it. Which control plane component drives this cascading cleanup?
A. kube-scheduler
B. Namespace Controller, as part of kube-controller-manager
C. kubelet on each affected node
D. etcd's built-in garbage collector

**Correct answer: B**
*Explanation:* The Namespace Controller specifically watches for Namespace deletions and orchestrates cleanup of all resources within that namespace before finalizing its removal. A is unrelated to lifecycle cleanup, C only manages Pods on its own node, and D does not exist as described — etcd has no Kubernetes-object-aware garbage collector of its own.

---

**Q19.** What would most likely happen if kube-apiserver became completely unavailable, but etcd, kube-scheduler, kube-controller-manager, and all kubelets kept running?
A. All running Pods would crash instantly
B. No new objects could be created/updated and no new scheduling or reconciliation could occur, since all components rely on the API server as their single access path, though already-running Pods continue
C. etcd would automatically take over the API server's role
D. kube-scheduler would begin talking to etcd directly to bypass the outage

**Correct answer: B**
*Explanation:* Since every other component — including the scheduler and controller-manager — reaches etcd exclusively through kube-apiserver, its unavailability halts all new state changes cluster-wide, even though already-scheduled Pods keep running via kubelet's local state. A is false, and both C and D contradict the architecture's strict single-access-path design.

---

**Q20.** Which best explains why Raft's leader-election process matters for etcd's write availability?
A. Only the elected leader can sequence and commit writes, so a leaderless cluster (e.g., during an election) temporarily cannot accept new writes
B. The leader only handles read requests, not writes
C. Raft has no concept of leader election
D. Every replica can independently commit writes without coordination

**Correct answer: A**
*Explanation:* Raft designates a single leader to order and commit all writes; during leader election (e.g., after a leader failure), the cluster briefly cannot commit new writes until a new leader is chosen, which is why etcd cluster stability directly affects write availability. B, C, and D all misstate Raft's actual design.

---

## 21. Chapter Summary (One-Page Revision Sheet)

- **kube-apiserver**: the only gatekeeper to etcd; handles authentication, authorization, admission control, validation, and the watch/notify mechanism.
- **etcd**: the distributed, Raft-consistent key-value store holding all cluster state; typically run with 3 or 5 replicas for HA.
- **kube-scheduler**: assigns unscheduled Pods to nodes via **Filtering** (hard requirements) then **Scoring** (soft preferences).
- **kube-controller-manager**: hosts many independent controllers (Node, ReplicaSet, Deployment, Job, Endpoints, Namespace, ServiceAccount), each running its own reconciliation loop.
- The **watch mechanism** lets components react to changes instantly via push notifications rather than wasteful polling.
- Production clusters run control plane components with multiple replicas and leader election for high availability, and require rigorous etcd backup practices given etcd's role as the single source of truth.

---

### Chapter Completion Checklist

1. **Topics covered:** kube-apiserver's request pipeline, etcd's Raft consistency model, scheduler's filter/score process, built-in controllers inside kube-controller-manager, the watch mechanism.
2. **KCNA objectives completed:** Deep architectural understanding of every control plane component, extending Chapter 06.
3. **Remaining objectives:** Worker node components in depth (Chapter 08).
4. **Suggested revision checklist:** Explain the full request lifecycle from `kubectl apply` through etcd commit and watch notification without notes; explain why Raft's majority requirement matters; list at least 4 built-in controllers and what each reconciles.
5. **Suggested hands-on exercises:** Complete Lab 2 (force a scheduling failure) and read the resulting Pod Events output carefully — this is the most common real-world troubleshooting scenario for this chapter's content.
6. **Related chapters:** Previous: [06-Kubernetes-Architecture](../06-Kubernetes-Architecture/README.md). Next: [08-Worker-Nodes](../08-Worker-Nodes/README.md) — deep-dives into kubelet, kube-proxy, and the container runtime interaction on each node.
