# 06 — Kubernetes Architecture

## 1. Learning Objectives

By the end of this chapter you will be able to:

- Explain what Kubernetes actually is and the specific orchestration problems it solves.
- Explain the high-level split between the control plane and worker nodes, and why that split exists.
- Name every major control plane and node component at a high level (each gets its own deep-dive chapter next).
- Explain the declarative, desired-state model and the reconciliation loop pattern that underlies everything in Kubernetes.
- Understand Kubernetes' origin from Google's internal Borg system.

**KCNA objectives covered:** Kubernetes Fundamentals domain (46% weight) — this chapter is the architectural spine the entire rest of the exam hangs on.

---

## 2. Historical Background

- **2003-2004:** Google builds **Borg**, an internal cluster management system running virtually all of Google's workloads (Search, Gmail, etc.) across massive fleets of machines. Borg pioneered many ideas Kubernetes later adopted: declarative configuration, a central scheduler, and self-healing workloads.
- **2013:** Docker popularizes containers (Chapter 04), but there was no widely-available, production-grade way to orchestrate containers *across many machines* — scheduling, networking, scaling, and healing had to be solved manually or with early, less mature tools (e.g., early Mesos-based schedulers).
- **2014:** Google open-sources **Kubernetes** (Greek for "helmsman/pilot" — the person who steers a ship, a deliberate naming choice), built by engineers who had direct experience with Borg, effectively bringing over a decade of Google's internal orchestration lessons into a public, vendor-neutral project. The "K8s" abbreviation comes from "K" + 8 letters + "s."
- **2015:** Kubernetes 1.0 released; Google donates it to the newly-formed **CNCF (Cloud Native Computing Foundation)**, ensuring no single vendor controls its direction.
- **2015-present:** Kubernetes wins the "container orchestration wars" against competitors like Docker Swarm and Apache Mesos, becoming the de facto standard — largely because of its robust declarative model, extensibility (CRDs, operators), and vendor-neutral governance under the CNCF.

**Why this matters:** Kubernetes is not a totally novel invention — it's the public, refined descendant of over a decade of Google's private operational experience running containers at massive scale. Understanding it as "Borg's lessons, made public and vendor-neutral" explains many of its design choices.

---

## 3. Motivation: Why Does Kubernetes Exist?

**Analogy — The Air Traffic Control Tower:**
Imagine an airport with hundreds of planes (containers) needing to land, take off, be refueled, and be repaired constantly, spread across dozens of runways and gates (servers/nodes). A single human trying to manually track every plane's location, fuel level, and schedule would be overwhelmed instantly and make constant mistakes. An air traffic control tower (Kubernetes) instead **continuously watches** every plane's actual status, compares it against the flight schedule (the desired state), and automatically directs planes to open gates, reroutes around problems, and never sleeps.

### 3.1 How Was This Solved Before Kubernetes?

Chapter 04 established that containers solve "it works on my machine." But once you have **hundreds of containers across many physical machines**, entirely new problems appear that a single Docker host cannot solve alone:

- **Which physical machine should run which container?** (scheduling)
- **What happens when a container crashes?** (self-healing)
- **What happens when a whole machine dies?** (rescheduling elsewhere)
- **How do containers find and talk to each other reliably as they move between machines?** (service discovery — Chapter 03's DNS concepts, automated)
- **How do you scale from 3 replicas to 30 during a traffic spike, and back down after?** (autoscaling)
- **How do you roll out a new version without downtime, and roll back if it's broken?** (deployment strategies)

Early approaches were largely manual scripts, custom in-house tooling (like early Borg itself, privately, at Google), or immature early orchestrators — none broadly production-proven and standardized.

### 3.2 How Kubernetes Solves It

Kubernetes solves all of the above with one unifying idea: **you declare what you want (desired state) in YAML, and Kubernetes continuously works to make reality match that declaration — forever, automatically, without further human intervention.** This single idea, called the **reconciliation loop**, is the deepest and most important concept in this entire repository — nearly every chapter from here on is really just "here's another object type that participates in this same loop."

```
   You declare:                Kubernetes continuously:
"I want 3 replicas    ───►    1. Observes actual state (currently 2 running)
 of this container      2. Detects the difference (need 1 more)
 running, always"        3. Takes action (schedules 1 more container)
                          4. Repeats this forever, watching for any drift
```

---

## 4. Core Concepts

### 4.1 What Is Kubernetes? (Formal Definition)

**Definition:** Kubernetes is an open-source container orchestration platform that automates the deployment, scaling, networking, and management of containerized applications across a cluster of machines, using a declarative, desired-state model.

### 4.2 The Cluster: Control Plane + Worker Nodes

**Analogy — The Restaurant, Full Picture:**
A Kubernetes **cluster** is an entire restaurant. The **control plane** is the restaurant's management office: the head chef planning menus (scheduler deciding what goes where), the manager tracking orders and inventory (API server and etcd storing all state), and quality control checking everything matches what was ordered (controller manager). The **worker nodes** are the actual kitchen stations where food (containers) is physically cooked and served — each station has a station chef (kubelet) following instructions from management, and a line cook (container runtime, Chapter 05) doing the literal cooking.

```
┌─────────────────────────────────────────────────────────────┐
│                          CLUSTER                                │
│                                                                    │
│   ┌───────────────────────────────────────────────────┐   │
│   │                  CONTROL PLANE                          │   │
│   │  (the "brain" — decides what should happen)             │   │
│   │                                                            │   │
│   │  ┌───────────┐ ┌──────┐ ┌───────────┐ ┌──────────┐ │   │
│   │  │API Server  │ │etcd   │ │Scheduler   │ │Controller │ │   │
│   │  │            │ │       │ │            │ │Manager     │ │   │
│   │  └───────────┘ └──────┘ └───────────┘ └──────────┘ │   │
│   └───────────────────────────────────────────────────┘   │
│                                                                    │
│   ┌────────────────────┐  ┌────────────────────┐         │
│   │     WORKER NODE 1      │  │     WORKER NODE 2      │         │
│   │  (the "hands" — does     │  │  (the "hands" — does     │         │
│   │   the actual work)         │  │   the actual work)         │         │
│   │  ┌────────┐ ┌────────┐ │  │  ┌────────┐ ┌────────┐ │         │
│   │  │kubelet  │ │kube-    │ │  │  │kubelet  │ │kube-    │ │         │
│   │  │         │ │proxy    │ │  │  │         │ │proxy    │ │         │
│   │  └────────┘ └────────┘ │  │  └────────┘ └────────┘ │         │
│   │  ┌────────────────┐   │  │  ┌────────────────┐   │         │
│   │  │Container Runtime  │   │  │  │Container Runtime  │   │         │
│   │  │(containerd, etc.)  │   │  │  │(containerd, etc.)  │   │         │
│   │  └────────────────┘   │  │  └────────────────┘   │         │
│   │  ┌────┐ ┌────┐ ┌────┐│  │  ┌────┐ ┌────┐        │         │
│   │  │Pod  │ │Pod  │ │Pod  ││  │  │Pod  │ │Pod  │        │         │
│   │  └────┘ └────┘ └────┘│  │  └────┘ └────┘        │         │
│   └────────────────────┘  └────────────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### 4.3 Control Plane Components (High-Level Preview — each gets a full chapter)

| Component | One-Line Role | Deep-Dive Chapter |
|---|---|---|
| **kube-apiserver** | The front door — all communication (kubectl, controllers, kubelet) goes through it; validates and stores requests | Chapter 07 |
| **etcd** | A distributed, consistent key-value store holding the entire cluster's actual and desired state | Chapter 07 |
| **kube-scheduler** | Decides *which node* a new Pod should run on, based on resources and constraints | Chapter 07, Chapter 20 |
| **kube-controller-manager** | Runs the many reconciliation loops (controllers) that continuously drive actual state toward desired state | Chapter 07 |
| **cloud-controller-manager** | Integrates with cloud-provider-specific APIs (load balancers, storage, node lifecycle) — only present in cloud-hosted clusters | Chapter 07 |

### 4.4 Worker Node Components (High-Level Preview)

| Component | One-Line Role | Deep-Dive Chapter |
|---|---|---|
| **kubelet** | The node's agent — talks to the API server, ensures the containers described in assigned Pods are actually running | Chapter 08 |
| **kube-proxy** | Maintains network rules on each node so traffic can reach the correct Pods, implementing Service networking | Chapter 08, Chapter 16 |
| **Container runtime** | Actually runs the containers (containerd/CRI-O — full detail Chapter 05) | Chapter 05, Chapter 08 |

### 4.5 The Declarative Model and Reconciliation Loop (The Single Most Important Concept in Kubernetes)

**Imperative vs Declarative — the foundational distinction:**

| Approach | How it works | Example |
|---|---|---|
| Imperative | You specify the exact *steps* to reach a goal | "Run this container. Now run a second one. Now check if one died and restart it manually." |
| Declarative | You specify only the *desired end state*; the system figures out the steps | "I want 3 replicas of this container running, always." |

Kubernetes is built entirely around the **declarative** model. You write YAML describing what you *want* — you never write a script telling Kubernetes the step-by-step actions to take.

**The Reconciliation Loop (a.k.a. the Control Loop):**

```
        ┌──────────────────────────────────────────┐
        │                                              │
        ▼                                              │
 1. Observe actual state (query etcd/API server)          │
        │                                              │
        ▼                                              │
 2. Compare actual state vs desired state                  │
        │                                              │
        ▼                                              │
 3. Difference found? → Take action to reconcile           │
        │                                              │
        ▼                                              │
 4. Wait briefly, then repeat forever ─────────────────────┘
```

Every controller in Kubernetes (ReplicaSet controller, Deployment controller, Node controller, and dozens more) runs its own instance of this exact loop, each watching a different piece of desired vs actual state. This is why Kubernetes **self-heals**: if a Pod crashes, actual state now differs from desired state, and the very next loop iteration notices and fixes it — no human, no alert, no manual restart needed. This single pattern will reappear, unchanged in shape, in every workload chapter from Chapter 10 onward.

---

## 5. Internal Working: What Happens When You Run `kubectl apply -f deployment.yaml`

```
1. kubectl sends the YAML (converted to JSON) as an HTTPS request
   to the kube-apiserver
        ↓
2. kube-apiserver authenticates and authorizes the request,
   validates the object schema, and writes the desired state to etcd
        ↓
3. kube-scheduler (watching the API server) notices new unscheduled
   Pods and assigns each one to a specific worker node
        ↓
4. kube-controller-manager's relevant controllers (e.g., the
   Deployment/ReplicaSet controllers) notice the new desired state
   and create the actual Pod objects needed to satisfy it
        ↓
5. kubelet on the assigned node (watching the API server) notices
   a Pod has been scheduled to it
        ↓
6. kubelet instructs the container runtime (Chapter 05) to pull
   images and start containers per the Pod spec
        ↓
7. kubelet continuously reports actual status back to the API
   server, which updates etcd — closing the reconciliation loop
```

---

## 6. Architecture

See Section 4.2's full diagram — this is the canonical Kubernetes architecture diagram you should be able to redraw from memory before moving to Chapter 07.

---

## 7. Component Breakdown

| Component | Plane | Purpose | Failure Scenario |
|---|---|---|---|
| kube-apiserver | Control | Front door for all cluster communication | If down, no new changes can be made cluster-wide (though running workloads keep running) |
| etcd | Control | Stores all cluster state, the single source of truth | If lost/corrupted without backup, cluster state is unrecoverable |
| kube-scheduler | Control | Assigns Pods to nodes | If down, new Pods stay stuck in `Pending`, but existing Pods keep running |
| kube-controller-manager | Control | Runs reconciliation loops | If down, self-healing stops (crashed Pods won't be replaced), but existing state is untouched |
| kubelet | Node | Ensures assigned Pods actually run | If down, that node's Pods aren't managed/reported, may eventually be marked `NotReady` |
| kube-proxy | Node | Implements Service network rules | If down, Service traffic routing on that node breaks |
| Container runtime | Node | Actually runs containers | If down, no containers can start/run on that node |

---

## 8. Important Terminology

| Term | Meaning |
|---|---|
| Cluster | The full set of machines (control plane + worker nodes) running Kubernetes together |
| Control plane | The set of components making global cluster decisions (scheduling, state storage, reconciliation) |
| Worker node | A machine that actually runs application containers |
| Declarative model | Specifying desired end-state rather than step-by-step instructions |
| Reconciliation loop | The continuous observe-compare-act cycle that drives actual state toward desired state |
| Self-healing | Automatic recovery from failures, a direct result of the reconciliation loop |
| Borg | Google's internal predecessor system that directly inspired Kubernetes' design |
| CNCF | The vendor-neutral foundation now governing Kubernetes' development |

---

## 9. YAML Deep Dive

No new object type introduced yet — this chapter is architectural. Every YAML manifest you'll write starting in Chapter 09 (Kubernetes Objects) is simply "a declaration of desired state," which the API server stores and every relevant controller reconciles toward, exactly as described in Section 4.5.

---

## 10. kubectl Commands (First Introduction)

| Command | Purpose | Example |
|---|---|---|
| `kubectl cluster-info` | Show control plane endpoint info | `kubectl cluster-info` |
| `kubectl get nodes` | List all nodes and their status | `kubectl get nodes` |
| `kubectl get componentstatuses` | (Deprecated in newer versions, but conceptually) show control plane component health | `kubectl get componentstatuses` |
| `kubectl version` | Show client/server Kubernetes versions | `kubectl version` |
| `kubectl config view` | Show current cluster/context configuration | `kubectl config view` |

---

## 11. Hands-on Examples

**Lab 1 — Stand up a local cluster and inspect its architecture:**
```bash
minikube start
kubectl get nodes -o wide
# Observe: a single-node cluster still separates control plane and
# worker responsibilities logically, even if running on one machine
```

**Lab 2 — Watch the reconciliation loop happen live:**
```bash
kubectl create deployment demo --image=nginx --replicas=3
kubectl get pods -w
# In another terminal, delete one Pod:
kubectl delete pod <one-of-the-three-pod-names>
# Watch the first terminal — a replacement Pod appears automatically,
# proving the reconciliation loop in action, live
```

**Lab 3 — Trace a request:**
Run `kubectl get pods -v=8` (high verbosity) to literally see the HTTP request kubectl sends to the kube-apiserver, connecting the CLI tool to Section 5's request flow.

---

## 12. Internal Flow

See Section 5 for the full `kubectl apply` → API server → scheduler → controller manager → kubelet → runtime flow.

---

## 13. Real-World Examples

1. **Google Kubernetes Engine (GKE)** is, fittingly, Google's own managed Kubernetes offering — built by many of the same engineers who worked on Borg, closing the historical loop from Section 2.
2. **Netflix, Spotify, and Airbnb** all run large portions of their infrastructure on Kubernetes, relying on its self-healing reconciliation model to survive constant partial failures at scale without manual intervention.
3. **CERN** (the physics research organization behind the Large Hadron Collider) uses Kubernetes to orchestrate massive scientific computing workloads across thousands of nodes.
4. **Banks and financial institutions** (e.g., Capital One) use Kubernetes' declarative model specifically because it provides an auditable, version-controllable description of infrastructure state (tying directly into GitOps, Chapter 24).
5. **The CNCF's own survey data** consistently shows Kubernetes as the most widely adopted container orchestration platform globally, having decisively won against Docker Swarm and Mesos in real-world adoption.

---

## 14. Best Practices

- Always think in terms of desired state — write YAML describing the end goal, never a sequence of manual `kubectl` commands as your source of truth.
- Understand which control plane component is responsible before troubleshooting — e.g., Pods stuck `Pending` point to the scheduler, not the controller manager.
- In production, always run multiple control plane replicas (especially etcd and kube-apiserver) for high availability — a single control plane node is a single point of failure.
- Back up etcd regularly — it is the literal single source of truth for your entire cluster's state.

---

## 15. Common Mistakes

- Believing the control plane "runs your applications" — it only makes decisions; worker nodes actually run application containers.
- Assuming Kubernetes is imperative because you use CLI commands like `kubectl create deployment` — under the hood, this still generates a declarative object stored in etcd, reconciled continuously.
- Forgetting that if the control plane goes down temporarily, already-running workloads on worker nodes generally keep running — only *new changes* and *self-healing* are affected until the control plane recovers.
- Treating etcd as "just another data store" rather than recognizing it as the literal single source of truth requiring serious backup/HA planning.

---

## 16. Troubleshooting

| Symptom | Possible Cause | Debugging Commands | Fix |
|---|---|---|---|
| New Pods stuck `Pending` | Scheduler down, or no node satisfies resource/constraint requirements | `kubectl describe pod <name>`, `kubectl get nodes` | Check scheduler health, check node capacity/taints (Chapter 20) |
| Crashed Pods not being replaced | Controller manager down or the specific controller loop stalled | `kubectl get pods`, check controller-manager logs | Restart/investigate controller manager |
| `kubectl` commands hang or fail entirely | API server unreachable | `kubectl cluster-info`, check network/API server health | Restore API server availability |
| Cluster state appears lost/corrupted | etcd data loss or corruption | Check etcd cluster health directly (advanced, node-level) | Restore from etcd backup |

---

## 17. Comparison Tables

**Control Plane vs Worker Node:**

| Aspect | Control Plane | Worker Node |
|---|---|---|
| Role | Decides *what should happen* | Does the *actual work* |
| Key components | API server, etcd, scheduler, controller manager | kubelet, kube-proxy, container runtime |
| Runs application containers? | No (in typical production setups) | Yes |
| Failure impact | New changes/self-healing pause; existing workloads often keep running | That specific node's Pods are affected |

**Imperative vs Declarative:** see Section 4.5 table.

---

## 18. Memory Tricks

- **"Control plane = brain, worker node = hands."**
- **Kubernetes = "Borg, made public."** Remembering the Borg lineage explains *why* Kubernetes looks the way it does.
- **Reconciliation loop = "observe, compare, act, repeat — forever."** Picture a thermostat: it doesn't "turn on the heat once," it continuously checks the actual temperature against your desired setting, forever.
- **"K8s" = K + 8 letters ("ubernete") + s.**

---

## 19. Interview Questions

**Easy:**
1. What is the difference between the control plane and worker nodes in Kubernetes?
   *Expected answer:* The control plane makes global decisions about the cluster (scheduling, state storage, reconciliation) but does not typically run application workloads itself. Worker nodes are the machines that actually run the containerized applications, managed by an agent (kubelet) that follows instructions from the control plane.

**Medium:**
2. Explain the reconciliation loop and why it's the reason Kubernetes self-heals.
   *Expected answer:* The reconciliation loop continuously observes the actual state of the cluster, compares it to the declared desired state, and takes corrective action whenever they differ, then repeats indefinitely. Because this loop runs continuously and automatically, if a Pod crashes (actual state now differs from desired state), the very next loop iteration detects the difference and creates a replacement — with no human intervention required, which is the mechanism behind Kubernetes' self-healing behavior.

**Hard:**
3. If the entire Kubernetes control plane becomes unreachable for 10 minutes, what happens to already-running application Pods on worker nodes, and what stops working during that window?
   *Expected answer:* Already-running Pods generally continue running uninterrupted, because kubelet on each worker node maintains its own local view of what should be running and the container runtime keeps those containers alive independent of control plane reachability. However, during the outage: no new Pods can be scheduled, no `kubectl` changes can be applied, and critically, self-healing stops — if a Pod crashes during this window, the controller manager cannot detect and replace it until control plane connectivity is restored, since the reconciliation loop itself depends on control plane components being reachable.

---

## 20. KCNA Practice Questions

**Q1.** What is the primary function of the Kubernetes control plane?
A. To run application containers directly
B. To make global decisions about the cluster and drive actual state toward desired state
C. To provide persistent storage for application data
D. To execute container images pulled from a registry

**Correct answer: B**
*Explanation:* The control plane's role is decision-making — scheduling, state storage, and reconciliation — not running application workloads directly. A and D describe worker node responsibilities. C describes storage subsystems (Chapter 19), unrelated to the control plane's core function.

---

**Q2.** Kubernetes was directly influenced by which prior internal Google system?
A. Spanner
B. Borg
C. BigQuery
D. TensorFlow

**Correct answer: B**
*Explanation:* Borg was Google's internal cluster management system, and its lessons (declarative configuration, centralized scheduling, self-healing) directly shaped Kubernetes' design when Google open-sourced it in 2014. Spanner (A) is Google's distributed database, BigQuery (C) is Google's data warehouse, and TensorFlow (D) is Google's ML framework — none are orchestration predecessors to Kubernetes.

---

**Q3.** In the declarative model used by Kubernetes, what does a user primarily specify?
A. The exact sequence of steps to reach a goal
B. Only the desired end state, letting Kubernetes determine the steps
C. A shell script of kubectl commands to run in order
D. The specific CPU instructions the scheduler should execute

**Correct answer: B**
*Explanation:* Declarative configuration means specifying the desired outcome (e.g., "3 replicas running"), not the imperative steps to get there. A and C describe an imperative approach, which Kubernetes does not fundamentally rely on. D is not a real concept in this context.

---

**Q4.** Which control plane component is responsible for deciding which worker node a new Pod should run on?
A. etcd
B. kube-scheduler
C. kubelet
D. kube-proxy

**Correct answer: B**
*Explanation:* kube-scheduler evaluates resource availability and constraints to assign Pods to specific nodes. etcd (A) only stores state, kubelet (C) and kube-proxy (D) are worker node components responsible for running and networking Pods after they've already been scheduled.

---

**Q5.** What is etcd's role within the Kubernetes control plane?
A. It schedules Pods onto nodes
B. It is a distributed key-value store holding the cluster's entire state
C. It runs application containers
D. It manages network routing between Pods

**Correct answer: B**
*Explanation:* etcd is the single source of truth for all cluster state (desired and actual), which every other control plane component reads from and writes to. A describes kube-scheduler, C describes worker nodes/container runtimes, and D describes kube-proxy/CNI responsibilities (Chapter 18).

---

**Q6.** What happens to already-running Pods if the Kubernetes control plane becomes temporarily unreachable?
A. All Pods immediately stop
B. Pods generally continue running, but new scheduling and self-healing pause until connectivity is restored
C. All Pods are automatically migrated to a backup cluster
D. Worker nodes shut down automatically for safety

**Correct answer: B**
*Explanation:* kubelet and the container runtime on each worker node maintain already-running containers independently of control plane availability; only new changes and reconciliation-driven self-healing are paused during an outage. A, C, and D describe behaviors Kubernetes does not have.

---

**Q7.** Which of the following best describes the reconciliation loop pattern used throughout Kubernetes?
A. A one-time setup script executed at cluster creation
B. A continuous cycle of observing actual state, comparing it to desired state, and taking corrective action
C. A manual process requiring an administrator to approve every change
D. A backup mechanism for etcd only

**Correct answer: B**
*Explanation:* The reconciliation loop runs continuously and automatically for every controller in Kubernetes, which is the mechanism enabling self-healing. A, C, and D mischaracterize it as a one-time, manual, or storage-specific process.

---

**Q8.** Which worker node component ensures that containers described in Pods assigned to that node are actually running?
A. kube-scheduler
B. kube-controller-manager
C. kubelet
D. kube-apiserver

**Correct answer: C**
*Explanation:* kubelet is the per-node agent that watches for Pods assigned to its node and ensures the container runtime actually runs them, reporting status back to the control plane. A, B, and D are all control plane components, not worker node components.

---

**Q9.** Why was Kubernetes donated to the CNCF shortly after its 1.0 release?
A. To reduce Google's own operating costs
B. To ensure vendor-neutral governance rather than control by a single company
C. Because Google no longer wanted to use Kubernetes internally
D. To comply with a government regulation

**Correct answer: B**
*Explanation:* Donating Kubernetes to the CNCF established neutral, multi-vendor governance, encouraging broad industry adoption and contribution rather than dependence on one company's roadmap — a major factor in its long-term success against competitors. A, C, and D are not accurate reasons for this decision.

---

**Q10.** A new Deployment YAML is applied, but the assigned Pods remain stuck in `Pending` status. Which component is the most likely first place to investigate?
A. etcd
B. kube-scheduler
C. kube-proxy
D. Container registry authentication

**Correct answer: B**
*Explanation:* Pods stuck in `Pending` have not yet been assigned to a node, which is specifically the scheduler's responsibility — pointing to scheduler health or insufficient node resources/constraints as the likely cause. etcd (A) issues would typically cause broader cluster-wide failures, not just scheduling-specific symptoms. kube-proxy (C) issues manifest as networking problems for already-running Pods, not pending scheduling. Registry auth issues (D) would typically show as `ImagePullBackOff`, a different and more specific symptom than `Pending`.

---

**Q11.** Which statement best describes why Kubernetes' architecture separates "decision-making" from "execution"?
A. It is an arbitrary historical accident with no design benefit
B. It allows the control plane to make cluster-wide decisions while worker nodes independently execute and maintain workloads, improving resilience and scalability
C. It was required by early cloud providers' billing models
D. It eliminates the need for any state storage

**Correct answer: B**
*Explanation:* Separating the "brain" (control plane) from the "hands" (worker nodes) lets each worker node keep running its assigned workloads independently even during control plane disruptions, and lets the control plane scale its decision-making logic independently of the number of worker nodes — a deliberate resilience and scalability design choice, not an accident.

---

**Q12.** In the declarative model, if a user manually deletes a Pod created by a Deployment, what happens next?
A. Nothing; the Deployment does not notice
B. The Deployment's reconciliation loop detects the actual replica count is below desired and creates a replacement Pod
C. The entire Deployment is deleted
D. Kubernetes requires manual re-creation of the exact same Pod

**Correct answer: B**
*Explanation:* This is the reconciliation loop in action: the Deployment continuously ensures actual state matches desired replica count, so deleting a Pod is detected on the next loop iteration and a replacement is automatically created — no manual re-creation (D) is needed, and the Deployment object itself is unaffected (not deleted, contradicting C).

---

**Q13.** Which of the following is NOT a standard Kubernetes control plane component?
A. kube-apiserver
B. kube-scheduler
C. kubelet
D. kube-controller-manager

**Correct answer: C**
*Explanation:* kubelet runs on worker nodes, not the control plane — it is the node-level agent that carries out instructions from the control plane. The other three (kube-apiserver, kube-scheduler, kube-controller-manager) are all control plane components.

---

**Q14.** Why is etcd described as "the single source of truth" for a Kubernetes cluster?
A. Because it runs application workloads directly
B. Because every other component's view of cluster state ultimately derives from what is stored in etcd via the API server
C. Because it replaces the need for a scheduler
D. Because it is the only component that can be replicated

**Correct answer: B**
*Explanation:* All cluster state — desired specs and observed status — is persisted in etcd, accessed exclusively through the API server; every other component's understanding of "what should exist" and "what currently exists" is ultimately backed by etcd's data, making it the authoritative record.

---

**Q15.** A cluster administrator wants to know why Kubernetes is often described as "self-healing." Which mechanism directly enables this property?
A. Manual administrator intervention scripts
B. The continuous reconciliation loop that detects and corrects drift between actual and desired state without human involvement
C. A nightly batch job that restarts all Pods
D. The container registry automatically restarting failed pulls

**Correct answer: B**
*Explanation:* Self-healing is a direct consequence of the reconciliation loop running continuously and automatically for every controller — there is no separate "self-healing feature," it emerges naturally from this one repeated pattern.

---

**Q16.** What is the practical significance of Kubernetes being donated to a vendor-neutral foundation (the CNCF) rather than remaining solely under Google's control?
A. It had no practical significance; adoption would have been identical either way
B. It reassured competing cloud providers and enterprises that no single company could unilaterally control the project's direction, encouraging broader multi-vendor investment and adoption
C. It transferred all of Google's patents to the public domain
D. It required Google to stop using Kubernetes internally

**Correct answer: B**
*Explanation:* Vendor-neutral governance was a strategic trust-building move — competitors like AWS, Microsoft, and Red Hat were far more willing to invest engineering effort into a foundation-governed project than one solely controlled by a rival cloud provider.

---

**Q17.** During a brief control plane outage, a worker node's kubelet loses connectivity to the API server. What does kubelet do with the Pods it is already running on that node?
A. Immediately terminates all Pods for safety
B. Continues managing and keeping those already-assigned Pods running, based on its last-known local state
C. Automatically migrates the Pods to another node
D. Waits indefinitely doing nothing until connectivity returns

**Correct answer: B**
*Explanation:* kubelet retains a local cache of the Pods it's responsible for and keeps them running independent of API server reachability — this is exactly why already-running workloads survive brief control plane outages, even though new scheduling and reconciliation-driven corrections pause.

---

**Q18.** Which best characterizes the relationship between Google's Borg and Kubernetes?
A. Borg is Kubernetes' current production runtime at Google
B. Kubernetes is an open-source reimplementation informed by lessons learned from Borg's internal design, not a direct code fork
C. Borg was built using Kubernetes as its foundation
D. They are unrelated systems built independently

**Correct answer: B**
*Explanation:* Kubernetes was not literally Borg's source code released publicly — it was designed by former Borg engineers who applied years of operational lessons (declarative APIs, centralized scheduling, self-healing) into a new, open-source system.

---

**Q19.** Which scenario would most likely indicate a kube-scheduler problem rather than a kubelet problem?
A. A running Pod's container keeps crashing and restarting
B. Newly created Pods remain stuck in `Pending` and are never assigned to any node
C. A node reports stale status information
D. A container fails its liveness probe repeatedly

**Correct answer: B**
*Explanation:* Assignment to a node is exclusively the scheduler's job — Pods stuck in `Pending` have not been scheduled yet, pointing upstream to the scheduler (or resource/constraint issues it's evaluating), not to kubelet, which only manages Pods after they've already been assigned to its node.

---

**Q20.** What is the core idea behind Kubernetes' "declarative" configuration model, as opposed to an "imperative" one?
A. You describe the exact commands to run in sequence, and Kubernetes executes them literally
B. You describe the desired end state, and Kubernetes continuously works to make actual state match it, regardless of the starting point or intervening disruptions
C. Declarative and imperative are two names for the same underlying model in Kubernetes
D. Declarative configuration only applies to networking objects

**Correct answer: B**
*Explanation:* This is the foundational distinction of this chapter: declarative means Kubernetes owns the "how," continuously working toward your stated "what," even recovering from unexpected disruptions — a fundamentally different and more resilient model than an imperative script that only runs its steps once.

---

## 21. Chapter Summary (One-Page Revision Sheet)

- Kubernetes descends directly from Google's internal **Borg** system; open-sourced in 2014, donated to the **CNCF** in 2015 for vendor-neutral governance.
- A cluster = **control plane** (the brain: decides what should happen) + **worker nodes** (the hands: actually run containers).
- Control plane components: **kube-apiserver** (front door), **etcd** (state store/source of truth), **kube-scheduler** (assigns Pods to nodes), **kube-controller-manager** (runs reconciliation loops), optionally **cloud-controller-manager**.
- Worker node components: **kubelet** (node agent, ensures Pods run), **kube-proxy** (Service networking rules), **container runtime** (Chapter 05).
- Kubernetes uses a **declarative model**: you specify desired state; Kubernetes figures out and continuously maintains the steps.
- The **reconciliation loop** (observe → compare → act → repeat forever) is the single pattern underlying every controller and every self-healing behavior in Kubernetes — expect to see this exact loop shape reused in every subsequent workload chapter.
- If the control plane goes down temporarily, already-running Pods generally keep running; only new scheduling and self-healing pause.

---

### Chapter Completion Checklist

1. **Topics covered:** Kubernetes history/Borg origins, control plane vs worker node split, all major component names at a high level, declarative model, reconciliation loop.
2. **KCNA objectives completed:** Core Kubernetes Fundamentals architectural foundation.
3. **Remaining objectives:** Deep dives into each control plane component (Ch. 07) and each worker node component (Ch. 08).
4. **Suggested revision checklist:** Redraw the full cluster architecture diagram (Section 4.2) from memory, including every named component in its correct plane; explain the reconciliation loop out loud without notes; explain what does and does not keep working during a control plane outage.
5. **Suggested hands-on exercises:** Complete Lab 2 (watch a deleted Pod get automatically replaced) — this is the single most important "aha" moment for understanding Kubernetes conceptually.
6. **Related chapters:** Previous: [05-Container-Runtimes](../05-Container-Runtimes/README.md). Next: [07-Control-Plane](../07-Control-Plane/README.md) — deep-dives into kube-apiserver, etcd, kube-scheduler, and kube-controller-manager individually.
