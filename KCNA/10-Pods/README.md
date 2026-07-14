# 10 — Pods

## 1. Learning Objectives

By the end of this chapter you will be able to:

- Explain what a Pod is and why Kubernetes doesn't run bare containers directly.
- Explain why Pods, not containers, are the smallest deployable unit in Kubernetes.
- Explain multi-container Pod patterns: sidecar, init container, ambassador, adapter.
- Explain shared networking and storage within a Pod.
- Read and write a complete Pod manifest using the object skeleton from Chapter 09.
- Explain the Pod lifecycle phases and restart policies.

**KCNA objectives covered:** Kubernetes Fundamentals domain — Pods are the first concrete workload object built on Chapter 09's object model.

---

## 2. Historical Background

Early container platforms (plain Docker, Chapter 04) ran one container in total isolation from every other container by default — each with its own network namespace, its own IP, its own everything. But real applications often need tightly-coupled helper processes running *alongside* the main application — for example, a log-shipping process that needs to read the same log files as the main app. Solving this with plain Docker required manual, fragile networking/volume-sharing tricks between separate containers. Kubernetes' designers, again drawing on Borg-era lessons (Chapter 06), introduced the **Pod** as a first-class grouping concept from Kubernetes' very first release — a deliberate abstraction layer between "a single container" and "a full application."

---

## 3. Motivation: Why Do Pods Exist At All?

**Analogy — The Apartment Building:**
Imagine an apartment (a Pod) that can hold one or more roommates (containers). All roommates in the same apartment share the same street address, the same front door buzzer, and the same shared storage closet — anyone can walk to the closet without needing a separate key or a special agreement. But roommates in *different* apartments must go through the building's shared hallways and doors to reach each other — they don't get direct, free access to each other's stuff. This is exactly how Pods work: containers **inside the same Pod** share network (same IP, `localhost` between them) and can share storage volumes trivially; containers in **different Pods** must communicate over the network like separate machines.

### 3.1 How Was This Solved Before Kubernetes?

Tightly-coupled multi-container setups (e.g., an app plus a log shipper) required manually configuring shared Docker networks and shared volume mounts between otherwise-independent containers — brittle, verbose, and not portable across environments.

### 3.2 How Kubernetes Solves It

Kubernetes groups one or more containers into a **Pod**, which is given a single shared network namespace (one IP address for the whole Pod) and can define shared storage volumes mounted into multiple containers at once. This makes tightly-coupled container groups a first-class, portable, declarative concept rather than a manual networking hack.

---

## 4. Core Concepts

### 4.1 What Is a Pod? (Formal Definition)

**Definition:** A Pod is the smallest deployable unit in Kubernetes — a group of one or more containers that share the same network namespace (one IP address), can share storage volumes, and are always scheduled together onto the same node.

**Why not just "the container" as the smallest unit?** Because real applications frequently need helper processes deployed and scaled *together* with the main container, sharing localhost networking and files — a single-container abstraction can't express "these things must always live and move together." The Pod is that "must always live and move together" unit.

### 4.2 Single-Container vs Multi-Container Pods

The vast majority of Pods in practice contain exactly **one** container — this is the common case, and it's easy to forget the Pod wrapper even exists when you're only ever dealing with single-container Pods. Multi-container Pods are the exception, used for specific, well-known patterns:

| Pattern | Purpose | Example |
|---|---|---|
| **Sidecar** | A helper container extending/supporting the main container | A log-shipping agent reading logs written by the main app to a shared volume |
| **Init Container** | Runs to completion *before* the main containers start, for one-time setup | Waiting for a database to be reachable before starting the app; downloading a config file |
| **Ambassador** | A proxy container simplifying network access for the main container | A local proxy that the main app talks to via `localhost`, which forwards to a complex external service |
| **Adapter** | Transforms/standardizes output from the main container for external consumption | Normalizing varied log/metric formats into one standard format before an external system scrapes them |

### 4.3 Init Containers — A Closer Look

**Definition:** Init containers are specified separately from regular containers in a Pod spec and are guaranteed to run to completion, in order, before any regular container starts. If an init container fails, kubelet retries it (subject to the Pod's restart policy) until it succeeds, blocking the rest of the Pod from starting.

**Analogy:** Init containers are like a hotel's housekeeping staff who must finish cleaning and preparing a room completely before any guest (the main container) is allowed to check in.

### 4.4 Pod Networking and Storage Sharing

- **Networking:** All containers in a Pod share one IP address and one port space. Containers within the same Pod reach each other via `localhost`, exactly like processes on the same physical machine. (Full deep dive on how each Pod gets that IP, and how Pods reach each other across nodes, is Chapter 18.)
- **Storage:** A Pod can define one or more **volumes** (Chapter 19 detail) at the Pod level, which any container in that Pod can then mount — enabling patterns like the sidecar log-shipper reading files the main app writes.

### 4.5 Pod Lifecycle Phases

| Phase | Meaning |
|---|---|
| `Pending` | Pod accepted by the cluster, but one or more containers not yet running (commonly: waiting to be scheduled, or images still pulling) |
| `Running` | Pod has been bound to a node and at least one container is running |
| `Succeeded` | All containers terminated successfully and will not be restarted |
| `Failed` | All containers terminated, and at least one terminated in failure |
| `Unknown` | The Pod's state could not be determined, usually due to a communication error with the node |

### 4.6 Restart Policy

`spec.restartPolicy` controls what kubelet does when a container in the Pod exits:

| Value | Behavior | Typical Use |
|---|---|---|
| `Always` (default) | Always restart the container on exit, regardless of exit code | Long-running services (the default and most common case) |
| `OnFailure` | Restart only if the container exits with a non-zero (failure) code | Batch jobs (Chapter 15) that should retry on failure but not on success |
| `Never` | Never restart the container | One-shot tasks where you want to inspect the exact failure state |

---

## 5. Internal Working

```
1. A Pod manifest is submitted (directly, or generated by a Deployment/
   ReplicaSet controller, Chapters 11-12) and follows the standard
   object lifecycle from Chapter 09 Section 5
        ↓
2. kube-scheduler assigns the Pod to a node (Chapter 07 Section 4.3)
        ↓
3. kubelet on that node (Chapter 08 Section 4.1) notices the assignment
        ↓
4. kubelet instructs the container runtime to first create a shared
   "pause"/sandbox container that holds the Pod's network namespace —
   this is what gives every container in the Pod the same IP
        ↓
5. Init containers (if any) run in order, to completion, before proceeding
        ↓
6. Regular containers are started, attached to the same network namespace
   and any shared volumes
        ↓
7. kubelet begins probing (Chapter 08 Section 4.2) and reports Pod phase
   and container statuses back to the API server
```

---

## 6. Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                             POD                                  │
│                    (One shared IP address: 10.244.1.5)             │
│                                                                    │
│   ┌────────────────────┐                                      │
│   │   Init Container      │  runs to completion FIRST             │
│   │  (e.g., wait-for-db)  │                                      │
│   └────────────────────┘                                      │
│                                                                    │
│   ┌────────────────────┐   ┌────────────────────┐         │
│   │  Main Container        │   │  Sidecar Container      │         │
│   │  (e.g., web app)       │   │  (e.g., log shipper)     │         │
│   │  talks via localhost ◄─┼──►│  reads shared volume     │         │
│   └────────────────────┘   └────────────────────┘         │
│                                                                    │
│   ┌────────────────────────────────────────────────┐    │
│   │            Shared Volume (e.g., emptyDir)               │    │
│   └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## 7. Component Breakdown

| Piece | Role |
|---|---|
| Pause/sandbox container | Holds the shared network namespace for the whole Pod (invisible to users, managed by the runtime) |
| Init container(s) | Run to completion, in order, before regular containers start |
| Regular container(s) | The actual application container(s); all run concurrently once init containers finish |
| Volume(s) | Storage shared across containers in the Pod |

---

## 8. Important Terminology

| Term | Meaning |
|---|---|
| Pod | The smallest deployable unit in Kubernetes; one or more containers sharing network and optionally storage |
| Init container | A container that runs to completion before regular containers start |
| Sidecar container | A helper container running alongside the main container for the Pod's lifetime |
| Restart policy | Controls whether/when kubelet restarts containers on exit (`Always`, `OnFailure`, `Never`) |
| Pod phase | The coarse-grained lifecycle status of a Pod (`Pending`, `Running`, `Succeeded`, `Failed`, `Unknown`) |
| Ephemeral | Pods are disposable and replaceable — never rely on a specific Pod instance surviving long-term |

---

## 9. YAML Deep Dive

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: web-with-logger
  labels:
    app: web
spec:
  restartPolicy: Always
  initContainers:
    - name: wait-for-db
      image: busybox
      command: ['sh', '-c', 'until nc -z db-service 5432; do sleep 2; done']
  containers:
    - name: web
      image: myapp:1.0
      volumeMounts:
        - name: shared-logs
          mountPath: /var/log/app
    - name: log-shipper
      image: fluent-bit
      volumeMounts:
        - name: shared-logs
          mountPath: /var/log/app
          readOnly: true
  volumes:
    - name: shared-logs
      emptyDir: {}
```

This single manifest demonstrates: an init container (waits for a dependency), two regular containers sharing a volume (sidecar pattern), and a restart policy — tying together Sections 4.2-4.6 in one example.

---

## 10. kubectl Commands

| Command | Purpose | Example |
|---|---|---|
| `kubectl run <name> --image=<image>` | Quickly create a single-container Pod | `kubectl run nginx --image=nginx` |
| `kubectl get pods` | List Pods and their phase | `kubectl get pods` |
| `kubectl describe pod <name>` | Show detailed Pod info, including init container status and Events | `kubectl describe pod web-with-logger` |
| `kubectl logs <pod> -c <container>` | View logs for a specific container in a multi-container Pod | `kubectl logs web-with-logger -c log-shipper` |
| `kubectl exec -it <pod> -c <container> -- sh` | Open a shell in a specific container | `kubectl exec -it web-with-logger -c web -- sh` |
| `kubectl delete pod <name>` | Delete a Pod | `kubectl delete pod web-with-logger` |

---

## 11. Hands-on Examples

**Lab 1 — Confirm shared networking between containers in a Pod:**
```bash
kubectl apply -f web-with-logger.yaml
kubectl exec -it web-with-logger -c log-shipper -- wget -qO- localhost:8080
# The log-shipper container can reach the web container via localhost —
# proving they share one network namespace (Section 4.4)
```

**Lab 2 — Watch an init container block the main container:**
```bash
kubectl apply -f web-with-logger.yaml
kubectl get pod web-with-logger -w
# Status shows "Init:0/1" until wait-for-db succeeds, THEN transitions
# to "Running" — proving init containers gate regular container startup
```

**Lab 3 — Observe restartPolicy in action:**
```bash
kubectl run oneshot --image=busybox --restart=Never -- sh -c "exit 1"
kubectl get pod oneshot
# Status shows "Error" and stays that way — restartPolicy: Never means
# kubelet does not attempt to restart it, unlike the Always default
```

---

## 12. Internal Flow

See Section 5's full 7-step flow — this refines Chapter 08 Section 5's node-side flow with the specific detail of the shared pause/sandbox container and init container ordering.

---

## 13. Real-World Examples

1. **Service meshes** (Istio, Linkerd — Chapter 23) inject a sidecar proxy container into every application Pod, relying entirely on the shared-network Pod model so the proxy can transparently intercept all traffic to/from the main container via `localhost`.
2. **Log aggregation pipelines** commonly use the sidecar pattern (Section 4.2) to ship application logs to a central system (e.g., Elasticsearch, Loki) without modifying the main application code at all.
3. **Database migration jobs** are a classic init container use case — an init container runs schema migrations to completion before the main application container (which depends on the updated schema) starts.
4. **Certificate/secret injection tools** (like vault-agent) use an init container to fetch and write secrets to a shared volume before the main application container starts and reads them.
5. **Multi-container "ambassador" setups** are used when legacy applications can't be modified to support service discovery directly — an ambassador sidecar handles the complex routing so the legacy app can keep talking to a simple, unchanging `localhost` address.

---

## 14. Best Practices

- Default to single-container Pods unless you have a specific, well-understood reason for a multi-container pattern (sidecar, init, ambassador, adapter).
- Use init containers for genuine one-time setup/dependency-waiting logic, not as a general-purpose scripting workaround.
- Never assume a specific Pod will survive long-term — Pods are ephemeral and disposable by design; use higher-level objects (Deployment, Chapter 12) to manage replacement automatically.
- Keep sidecar containers lightweight — they consume the same node resources and count toward the Pod's total resource footprint.
- Always set resource requests/limits per container, not just per Pod, since scheduling and allocatable calculations (Chapter 08 Section 4.4) work per-container under the hood.

---

## 15. Common Mistakes

- Treating a Pod as if it were a durable, individually-addressable server — restarting/rescheduling a Pod typically gives it a **new IP address**, breaking anything that hardcoded the old one (this is exactly why Services, Chapter 16, exist).
- Forgetting that containers in *different* Pods do NOT share localhost — only containers within the *same* Pod do.
- Using multiple unrelated application containers crammed into one Pod purely to "save resources," rather than scaling them independently — this couples their lifecycle and scaling unnecessarily.
- Not understanding that init container failures block the entire Pod from starting, which can cause confusing "Pod stuck in Init" symptoms if the init logic has a bug.

---

## 16. Troubleshooting

| Symptom | Likely Cause | Debugging Commands | Fix |
|---|---|---|---|
| Pod stuck in `Init:0/1` (or similar) | Init container hasn't completed successfully yet | `kubectl logs <pod> -c <init-container-name>` | Fix the init container's logic/dependency it's waiting on |
| Pod shows `CrashLoopBackOff` | A container keeps exiting and restartPolicy causes repeated restarts | `kubectl logs --previous`, `kubectl describe pod` | Fix the underlying application crash |
| Two containers in the same Pod can't reach each other | Wrong assumption about ports, or app binding to a specific interface instead of all interfaces | `kubectl exec` into containers and test with `curl`/`wget localhost:<port>` | Ensure app binds to `0.0.0.0`, not just `127.0.0.1` inside a specific container's own namespace context |
| Pod's IP changed unexpectedly | Pod was rescheduled/restarted — Pod IPs are not stable | `kubectl get pod -o wide` | Use a Service (Chapter 16) instead of relying on Pod IP directly |

---

## 17. Comparison Tables

**Init Container vs Sidecar Container:**

| Aspect | Init Container | Sidecar Container |
|---|---|---|
| When it runs | Before regular containers start, to completion | Alongside regular containers, for the Pod's whole lifetime |
| Purpose | One-time setup/dependency waiting | Ongoing helper functionality |
| Restart behavior | Retried until success (blocks Pod startup) | Restarted per the Pod's restartPolicy like any regular container |

**Pod vs Container:**

| Aspect | Container | Pod |
|---|---|---|
| Smallest deployable unit in Kubernetes? | No | Yes |
| Has its own IP address? | No (shares the Pod's IP) | Yes (one IP per Pod) |
| Can group multiple processes with shared networking? | No, not natively | Yes, that's its core purpose |

---

## 18. Memory Tricks

- **"Pod = apartment, containers = roommates."** Same address, shared common areas; different apartments need the hallway (network) to reach each other.
- **Init containers run "before the party starts, one at a time, and must finish."**
- **"Pods are cattle, not pets"** — the classic DevOps mantra: never get attached to a specific Pod's identity/IP; expect it to be replaced.
- Restart policy: **Always** (services), **OnFailure** (retry-able jobs), **Never** (one-shot, inspect-the-failure tasks).

---

## 19. Interview Questions

**Easy:**
1. Why is the Pod, not the container, the smallest deployable unit in Kubernetes?
   *Expected answer:* Because real applications often need tightly-coupled helper containers that must share the same network namespace (same IP, localhost access) and sometimes storage volumes, and must always be scheduled and scaled together. The Pod is the abstraction that groups one or more containers to guarantee this shared-fate relationship, which a bare single-container model cannot express.

**Medium:**
2. Explain the difference between an init container and a sidecar container.
   *Expected answer:* An init container runs to completion before any regular container in the Pod starts, and is typically used for one-time setup tasks like waiting for a dependency or running a migration; if it fails, kubelet retries it and blocks the rest of the Pod from starting. A sidecar container, by contrast, runs alongside the main container for the entire lifetime of the Pod, providing ongoing helper functionality like log shipping or proxying, and follows the same restart behavior as any other regular container.

**Hard:**
3. A team hardcodes a Pod's IP address in another service's configuration to avoid "the overhead of a Service." A week later, that Pod crashes and is replaced, and the other service can no longer connect. Explain what went wrong and the correct fix.
   *Expected answer:* Pods are ephemeral by design — whenever a Pod is deleted and recreated (whether due to a crash, a rolling update, or rescheduling), it is typically assigned a brand-new IP address, since the old Pod object and its associated IP no longer exist. Hardcoding a Pod's IP directly creates a fragile dependency on an identity that Kubernetes explicitly does not guarantee to be stable. The correct fix is to front the Pod(s) with a Service (Chapter 16), which provides a stable virtual IP/DNS name and automatically updates its routing to whichever Pods are currently healthy, regardless of how many times the underlying Pods are replaced.

---

## 20. KCNA Practice Questions

**Q1.** What is the smallest deployable unit in Kubernetes?
A. A container
B. A Pod
C. A Node
D. A Deployment

**Correct answer: B**
*Explanation:* The Pod, not the individual container, is Kubernetes' smallest deployable unit, since it's the unit that gets scheduled, given an IP, and managed as a whole. A container alone (A) cannot be independently scheduled in Kubernetes. Node (C) is a machine, not a deployable unit. Deployment (D) is a higher-level controller managing multiple Pods (Chapter 12).

---

**Q2.** How do containers within the same Pod typically communicate with each other?
A. Through an external load balancer
B. Via localhost, since they share the same network namespace
C. Only through a Service object
D. They cannot communicate directly at all

**Correct answer: B**
*Explanation:* All containers in a Pod share one network namespace and IP address, allowing them to reach each other via localhost just like processes on the same machine. A and C describe mechanisms for cross-Pod communication (Chapter 16), not intra-Pod communication. D is incorrect — this direct communication is precisely one of the Pod's defining features.

---

**Q3.** What is the defining behavior of an init container?
A. It runs continuously alongside the main container for the Pod's lifetime
B. It runs to completion before any regular container in the Pod starts
C. It replaces the need for a container runtime
D. It automatically restarts the entire Pod on failure

**Correct answer: B**
*Explanation:* Init containers run sequentially and must complete successfully before regular containers are allowed to start, making them ideal for one-time setup tasks. A describes a sidecar container instead. C and D describe unrelated or nonexistent behaviors.

---

**Q4.** Which restart policy is most appropriate for a batch task that should be retried only if it fails, but not restarted if it completes successfully?
A. Always
B. OnFailure
C. Never
D. Retry

**Correct answer: B**
*Explanation:* `OnFailure` restarts the container specifically when it exits with a failure code, leaving successful completions alone — exactly the behavior described. `Always` (A) would restart even after a successful exit, which is wrong for a one-shot task. `Never` (C) would not retry at all, even on failure. `Retry` (D) is not a valid Kubernetes restartPolicy value.

---

**Q5.** Why should you generally avoid hardcoding a Pod's IP address in another application's configuration?
A. Pod IP addresses are encrypted and cannot be read
B. Pods are ephemeral, and a replaced Pod is typically assigned a new IP address
C. Pod IP addresses change every few seconds automatically
D. Kubernetes does not assign IP addresses to Pods at all

**Correct answer: B**
*Explanation:* Because Pods are disposable and frequently replaced (due to crashes, updates, or rescheduling), their IP addresses are not stable identifiers — a Service should be used instead for stable addressing. A, C, and D are factually incorrect statements about Pod IP behavior.

---

**Q6.** A Pod defines two init containers and one regular container. What happens if the first init container fails?
A. The second init container and the regular container start anyway
B. kubelet retries the failed init container; the second init container and regular container do not start until it succeeds
C. The Pod is immediately deleted permanently
D. Only the regular container is skipped, but the second init container still runs

**Correct answer: B**
*Explanation:* Init containers run strictly in sequence, and kubelet retries a failing one according to the Pod's restart policy — no later init container or regular container starts until every prior init container has completed successfully. A and D violate the sequential/blocking guarantee, and C misdescribes actual behavior — Kubernetes retries rather than deleting the Pod outright.

---

**Q7.** Why do all containers in a Pod share the same IP address?
A. Because Kubernetes assigns IPs per container but hides the extras
B. Because they share a single network namespace, which is the Pod-level abstraction Kubernetes creates and containers join
C. Because only the first container in the list receives an IP
D. Because IP sharing is configured manually per Pod via an annotation

**Correct answer: B**
*Explanation:* The Pod itself owns one network namespace (technically held open by the pause/sandbox container), and every container in the Pod joins that same namespace, which is why they share one IP and can reach each other via localhost. A, C, and D misstate how this sharing is actually implemented.

---

**Q8.** Which use case is the LEAST appropriate reason to add a second container to a Pod?
A. Running a service mesh sidecar proxy that intercepts traffic to/from the main container
B. Running a completely unrelated application, unrelated in lifecycle and scaling needs, just to "save resources"
C. Shipping application logs to a central aggregator via a sidecar
D. Running an init container that waits for a dependent service before the main app starts

**Correct answer: B**
*Explanation:* Bundling unrelated applications into one Pod couples their lifecycle, scaling, and restart behavior unnecessarily — exactly the anti-pattern flagged in Section 15's common mistakes. A, C, and D are all legitimate, well-understood multi-container patterns described in Sections 13-14.

---

**Q9.** A Pod's main container binds only to `127.0.0.1` instead of `0.0.0.0`. What symptom would this most likely cause?
A. The Pod fails to be scheduled at all
B. A sidecar container in the same Pod cannot reach the main container over the network, since binding to `127.0.0.1` restricts it to the container's own loopback rather than the Pod's shared interface
C. The main container's image fails to pull
D. The entire node is marked NotReady

**Correct answer: B**
*Explanation:* Even though Pod containers share a network namespace, an app bound strictly to its own container-local loopback may not accept connections the way expected — this is exactly the troubleshooting entry in Section 16's table about intra-Pod connectivity issues, distinct from scheduling (A), image pulls (C), or node health (D).

---

**Q10.** What does the Pod phase `Succeeded` indicate?
A. The Pod is actively running and healthy
B. All containers in the Pod have terminated successfully and will not be restarted
C. The Pod has failed and needs manual intervention
D. The Pod is waiting to be scheduled

**Correct answer: B**
*Explanation:* `Succeeded` specifically means every container exited with a successful status and, per the Pod's restart policy (typically `Never` or `OnFailure` for such workloads), will not be restarted — common for one-shot batch tasks. A describes `Running`, C describes `Failed`, and D describes `Pending`.

---

**Q11.** Why is it recommended to set resource requests/limits on each container in a multi-container Pod rather than only at the Pod level?
A. Kubernetes does not support Pod-level resource limits at all
B. Scheduling and Allocatable calculations operate per-container under the hood, so per-container requests ensure accurate scheduling and prevent one container from starving another
C. Only the first container's limits are ever enforced
D. Container-level limits are purely cosmetic and have no scheduling effect

**Correct answer: B**
*Explanation:* As Section 14 notes, Kubernetes' scheduling math is fundamentally per-container, so precise per-container requests/limits are what actually inform correct scheduling decisions and prevent resource contention between containers sharing the same Pod. A, C, and D misstate how resource accounting works.

---

**Q12.** A batch Pod is configured with `restartPolicy: Always` but is only meant to run once and then stop. What problem will this most likely cause?
A. The Pod will fail to be created at all
B. After the task completes successfully, kubelet will keep restarting the container indefinitely, since `Always` restarts regardless of exit status
C. The Pod will be stuck in `Pending` forever
D. Nothing — `Always` behaves identically to `Never` for batch tasks

**Correct answer: B**
*Explanation:* `Always` restarts a container on any termination, including a clean success exit, which is exactly the wrong restart policy for a one-shot batch task — `OnFailure` or `Never` should be used instead, as noted in Section 18's memory tricks. A, C, and D misdescribe the actual mismatch.

---

**Q13.** Which statement best explains why "Pods are cattle, not pets" is a common DevOps mantra for Kubernetes?
A. Pods should be named after farm animals for clarity
B. You should not become attached to a specific Pod's identity or IP, since Kubernetes may replace it at any time, and higher-level controllers handle that replacement automatically
C. Pods require daily manual health checks like caring for livestock
D. Pods cannot be deleted once created

**Correct answer: B**
*Explanation:* This mantra captures the ephemeral, disposable nature of Pods — unlike a "pet" you'd carefully nurse back to health, a "cattle" Pod that fails is simply replaced by a controller like a Deployment (Chapter 12), with no attempt to preserve its specific identity. A, C, and D are not the actual meaning of this common phrase.

---

**Q14.** What is the most direct evidence that two containers are running in the same Pod rather than in two separate Pods?
A. They have identical container image names
B. They can reach each other via `localhost` on their respective ports
C. They were created in the same `kubectl apply` command
D. They share the same container ID

**Correct answer: B**
*Explanation:* Shared network namespace (and thus localhost reachability) is the defining, verifiable characteristic of same-Pod containers, exactly as demonstrated in Section 11's Lab 1. A is unrelated to Pod grouping, C is not a technical guarantee (multiple Pods can be created in one apply), and D is false — each container retains its own container ID even within a shared Pod.

---

**Q15.** A Pod has `restartPolicy: Never` and its single container exits with a non-zero status. What is the resulting Pod phase, and will kubelet restart it?
A. `Running`; kubelet restarts it once
B. `Failed`; kubelet does not restart it
C. `Succeeded`; kubelet does not restart it
D. `Pending`; kubelet retries scheduling

**Correct answer: B**
*Explanation:* A non-zero (failure) exit combined with `restartPolicy: Never` results in the Pod phase `Failed`, and per Section 11's Lab 3, kubelet does not attempt any restart under this policy — the Pod simply stays in that failed state for inspection. A, C, and D misstate either the resulting phase or kubelet's behavior.

---

**Q16.** Why are init containers well-suited for tasks like waiting for a database to become reachable before the main application starts?
A. Init containers run in parallel with the main container, providing a race-condition-free check
B. Init containers block the main container from starting until they complete successfully, guaranteeing the dependency is ready first
C. Init containers automatically retry the main container's logic instead
D. Init containers have special network privileges regular containers lack

**Correct answer: B**
*Explanation:* Because init containers run sequentially to completion *before* any regular container starts, using one to poll a dependency guarantees the main application never starts before that dependency is confirmed ready — precisely the "wait-for-db" example in Section 9's YAML. A is factually wrong (they are strictly sequential, not parallel with the main container), and C and D describe capabilities init containers do not have.

---

**Q17.** A certificate-injection init container (like vault-agent) writes a secret to a shared `emptyDir` volume. Why must this volume also be mounted by the main container?
A. It doesn't need to be — Kubernetes automatically copies files between containers regardless of volume mounts
B. Volumes are only visible to containers that explicitly mount them; the main container needs the same volume mounted to read what the init container wrote
C. emptyDir volumes are automatically mounted into every container in the cluster
D. Only init containers can read from emptyDir volumes

**Correct answer: B**
*Explanation:* An `emptyDir` volume is just shared storage scoped to the Pod — it is only accessible to containers that explicitly declare a `volumeMounts` entry for it, which is exactly why both the init container (writer) and main container (reader) must each mount it, as shown in Section 9's YAML pattern. A, C, and D are false.

---

**Q18.** Which best distinguishes a Pod's `Pending` phase from its `Unknown` phase?
A. They are synonyms with no distinction
B. `Pending` means the Pod is accepted but not yet fully scheduled/started; `Unknown` typically means the control plane has lost communication with the node and can't determine the Pod's actual state
C. `Unknown` means the Pod succeeded but with warnings
D. `Pending` only applies to Jobs, never to regular Pods

**Correct answer: B**
*Explanation:* `Pending` is a normal, expected transient phase before scheduling/startup completes, while `Unknown` specifically signals a loss of node communication (e.g., a NotReady or unreachable node) that leaves the control plane unable to confirm the Pod's true status. A, C, and D misstate these two distinct phases.

---

**Q19.** In the "ambassador" multi-container pattern described in Section 13, what problem does the ambassador sidecar solve?
A. It replaces the main application entirely with a newer version
B. It handles complex service discovery/routing on behalf of a legacy application that can only talk to a simple, unchanging local address
C. It encrypts all traffic leaving the node
D. It automatically scales the main container horizontally

**Correct answer: B**
*Explanation:* The ambassador pattern lets an unmodifiable legacy app keep talking to a fixed `localhost` address while the sidecar transparently handles the actual, more complex routing/discovery logic — exactly as described in Section 13's real-world examples. A, C, and D describe unrelated functions not part of the ambassador pattern's purpose.

---

**Q20.** Why does the troubleshooting guidance in Section 16 recommend using a Service instead of a Pod IP when a Pod's IP changes unexpectedly?
A. Services are faster than direct Pod-to-Pod communication in all cases
B. A Service provides a stable virtual IP/DNS name that is automatically kept in sync with whichever Pods are currently healthy, regardless of individual Pod IP churn
C. Services eliminate the need for a container runtime
D. Services prevent Pods from ever being rescheduled

**Correct answer: B**
*Explanation:* This is the core fix reiterated throughout the chapter (Sections 15, 16, 19, 20): a Service abstracts away individual, unstable Pod IPs behind one stable address, with kube-proxy (Chapter 08) keeping the routing current automatically. A is not the primary rationale, and C and D are false — Services have no bearing on the runtime or rescheduling behavior itself.

---

---

**Q6.** What is a "sidecar" container?
A. A container that must finish before the main container starts
B. A helper container that runs alongside the main container for the Pod's entire lifetime, extending its functionality
C. A container running on a completely separate node from the main container
D. A backup copy of the main container used only during failover

**Correct answer: B**
*Explanation:* Sidecars run concurrently with the main container throughout the Pod's lifetime, commonly used for logging, proxying, or monitoring support. A describes an init container. C is impossible — all containers in a Pod run on the same node by definition. D describes a concept unrelated to the sidecar pattern.

---

**Q7.** A Pod's status shows `Init:0/1`. What does this indicate?
A. The Pod has completed successfully with zero containers
B. The Pod's single init container has not yet completed successfully
C. The Pod has zero containers configured at all
D. The Pod failed permanently and will not be retried

**Correct answer: B**
*Explanation:* The `Init:X/Y` notation shows how many of the Pod's init containers have completed out of the total defined; `0/1` means the one defined init container hasn't finished yet, and regular containers are still blocked from starting. A, C, and D misinterpret this specific status notation.

---

**Q8.** Which of the following is shared by all containers within the same Pod by default?
A. CPU limits (all containers must have identical limits)
B. The network namespace (one shared IP address)
C. Their container images
D. Their exact process IDs

**Correct answer: B**
*Explanation:* Pod-level network namespace sharing is the defining trait — one IP for the whole Pod, with localhost communication between containers. CPU limits (A) are set independently per container. Container images (C) are independently specified per container. Process IDs (D) are not automatically shared unless a Pod explicitly enables shared process namespace, a non-default, advanced configuration.

---

**Q9.** Why do Kubernetes engineers commonly say "Pods are cattle, not pets"?
A. Because Pods require constant individual care to stay alive
B. Because Pods are meant to be treated as disposable, interchangeable instances rather than individually cherished, long-lived entities
C. Because Pods must always be created in groups of multiple identical replicas
D. Because Pods cannot be named individually

**Correct answer: B**
*Explanation:* This phrase captures the ephemeral, disposable nature of Pods — you shouldn't become attached to any specific Pod instance's identity, since Kubernetes may replace it at any time; higher-level controllers (Deployments, Chapter 12) manage this replacement automatically. A, C, and D misstate the actual meaning of the phrase.

---

**Q10.** In the YAML example from Section 9, why does the init container use `nc -z db-service 5432` in a loop before the main container starts?
A. To permanently open a network port for the main container to use later
B. To block Pod startup until a required dependency (the database) becomes reachable
C. To install the container runtime before running the main application
D. To generate the Pod's network namespace

**Correct answer: B**
*Explanation:* This is a textbook init container use case: repeatedly checking a dependency's availability and only exiting successfully once it's reachable, ensuring the main application container doesn't start until its required dependency is ready. A, C, and D describe actions unrelated to what this init container script actually does.

---

## 21. Chapter Summary (One-Page Revision Sheet)

- A **Pod** is the smallest deployable unit in Kubernetes: one or more containers sharing one network namespace (one IP, localhost between them) and optionally shared storage volumes.
- **Init containers** run to completion, in order, before regular containers start — ideal for one-time setup/dependency-waiting.
- **Sidecar, ambassador, adapter** are named multi-container patterns for ongoing helper functionality alongside a main container.
- **Pod phases**: `Pending`, `Running`, `Succeeded`, `Failed`, `Unknown`.
- **Restart policies**: `Always` (services), `OnFailure` (retryable jobs), `Never` (one-shot inspection tasks).
- Pods are **ephemeral** — never hardcode a Pod's IP; use a Service (Chapter 16) for stable addressing.

---

### Chapter Completion Checklist

1. **Topics covered:** Pod definition and rationale, single vs multi-container patterns, init containers, shared networking/storage, lifecycle phases, restart policies.
2. **KCNA objectives completed:** The foundational workload object underlying every higher-level controller from Chapter 11 onward.
3. **Remaining objectives:** How Pods are managed at scale via ReplicaSets (Chapter 11) and Deployments (Chapter 12).
4. **Suggested revision checklist:** Explain why Pods, not containers, are the smallest deployable unit; list all four multi-container patterns and one real-world use case for each; recite all three restart policies and when to use each.
5. **Suggested hands-on exercises:** Complete Lab 2 and watch the `Init:0/1` → `Running` transition directly — this is the clearest way to internalize init container blocking behavior.
6. **Related chapters:** Previous: [09-Kubernetes-Objects](../09-Kubernetes-Objects/README.md). Next: [11-ReplicaSets](../11-ReplicaSets/README.md) — how Kubernetes keeps a specified number of identical Pod replicas running.
