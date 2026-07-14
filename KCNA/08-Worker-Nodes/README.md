# 08 — Worker Nodes (Deep Dive)

## 1. Learning Objectives

By the end of this chapter you will be able to:

- Explain in depth what kubelet and kube-proxy each do, and how they cooperate with the container runtime.
- Describe the kubelet's Pod lifecycle management and health-checking responsibilities.
- Explain the three kubelet probe types (liveness, readiness, startup) and when each is used.
- Describe how kube-proxy implements Service networking at the node level (iptables/IPVS modes).
- Understand node capacity, allocatable resources, and node conditions.
- Explain what happens step-by-step on a worker node from Pod assignment to a running container.

**KCNA objectives covered:** Kubernetes Fundamentals domain — this completes the architecture picture started in Chapter 06 and detailed for the control plane in Chapter 07.

---

## 2. Historical Background

- **kubelet** existed since Kubernetes' earliest versions as the node-level agent, directly inspired by Borg's per-machine agent ("Borglet") that Chapter 06 mentioned as part of Kubernetes' lineage — the same "one agent per machine reporting to a central brain" pattern.
- **kube-proxy** was created to solve a problem that appeared as soon as Kubernetes needed **Services** (Chapter 16): Pods are ephemeral and get new IP addresses whenever recreated, so something had to maintain up-to-date network routing rules on every node reflecting which Pods currently exist. Early kube-proxy implementations used **iptables** (Linux's built-in packet filtering framework); as clusters grew to thousands of Services, iptables' linear rule-matching became a performance bottleneck, motivating the newer **IPVS (IP Virtual Server)** mode, which uses efficient hash-table lookups instead.
- **Probes (liveness/readiness/startup)** were added and refined over time as Kubernetes' health-checking model matured, particularly as the community learned that "is the process running?" (which a container runtime alone can answer) is a much weaker signal than "is the application actually able to serve traffic correctly?" (which only application-aware probing can answer).

---

## 3. Motivation: Why Does the Worker Node Need Its Own Agents?

**Analogy — The Warehouse Floor Supervisor:**
Chapter 07 covered "head office" (the control plane) deciding what should happen. But head office can't be physically present on every warehouse floor (node) supervising every worker (container) in real time. Each warehouse instead has its own **floor supervisor** (kubelet) who receives instructions from head office, makes sure the right workers show up and stay working, and reports back status. The floor supervisor also manages a **directory board** (kube-proxy) at the warehouse entrance so that deliveries (network traffic) headed for "Team B" get routed to wherever Team B's workers currently happen to be standing — even as workers move around.

### 3.1 How Was This Solved Before Kubernetes?

Without a per-node agent, the control plane would need direct, constant, low-level control of every single container on every machine — an approach that doesn't scale, is fragile to network blips between control plane and nodes, and creates a single points-of-failure problem for basic operational tasks.

### 3.2 How Kubernetes Solves It

Kubernetes places **one kubelet per node**, which independently ensures the containers assigned to that node keep running correctly — even during brief control plane unavailability, exactly as established in Chapter 06 Section "internal working." Each node also runs **kube-proxy**, maintaining local networking rules so Service traffic is correctly routed to healthy Pod IPs, wherever they currently live.

---

## 4. Core Concepts

### 4.1 kubelet — The Node's Agent

**Definition:** kubelet is the primary agent running on every worker node. It watches the API server for Pods assigned to its node, and ensures the containers described in each Pod's spec are actually running, healthy, and reported accurately back to the control plane.

**Key responsibilities:**
- **Pod lifecycle management** — start, stop, and restart containers as needed to match the Pod spec
- **Health checking** — run liveness, readiness, and startup probes (Section 4.2)
- **Resource reporting** — report node capacity/usage back to the API server, feeding the scheduler's decisions (Chapter 07 Section 4.3)
- **Volume mounting** — mount volumes into containers as specified (Chapter 19 detail)
- **Talking to the container runtime** — via the **CRI (Container Runtime Interface)**, established in Chapter 05, to actually create/destroy containers

### 4.2 Probes — How kubelet Knows If a Container Is Actually Healthy

A running process is not the same as a *working* application. kubelet uses three probe types to check actual application health:

| Probe Type | Question It Answers | What Happens on Failure |
|---|---|---|
| **Liveness Probe** | "Is this container still working correctly, or has it deadlocked/hung?" | kubelet restarts the container |
| **Readiness Probe** | "Is this container currently able to serve traffic?" | Pod is removed from Service endpoints (Chapter 16) until it passes again — container is NOT restarted |
| **Startup Probe** | "Has this slow-starting container finished its initial startup yet?" | Liveness/readiness probes are held off until startup succeeds, preventing premature restarts of slow-starting apps |

**Analogy — The Restaurant Kitchen (again):** Liveness = "is the cook still conscious and moving?" (if not, replace them). Readiness = "is the cook currently ready to accept a new order right now?" (if not, stop sending them new orders, but don't fire them). Startup = "give the new cook a grace period to set up their station before judging them on the above."

### 4.3 kube-proxy — Node-Level Service Networking

**Definition:** kube-proxy runs on every node and maintains networking rules that implement **Services** (Chapter 16) — enabling traffic sent to a stable Service IP/name to be correctly routed to one of the currently-healthy backing Pods, wherever they are in the cluster.

**Two common modes:**

| Mode | Mechanism | Performance Characteristic |
|---|---|---|
| **iptables** | Uses Linux iptables rules, matched sequentially | Simple, but rule-matching time grows roughly linearly with number of Services — can become a bottleneck at large scale |
| **IPVS** | Uses Linux IPVS, a kernel-level load balancer using hash tables | Near-constant-time lookups regardless of Service count — better for very large clusters |

### 4.4 Node Capacity, Allocatable, and Conditions

- **Capacity** — total physical resources on the node (e.g., 8 CPU, 32Gi memory).
- **Allocatable** — capacity minus resources reserved for the OS and Kubernetes system daemons (kubelet itself, etc.) — this is the real number the scheduler uses when deciding if a Pod fits.
- **Node Conditions** — a set of true/false health signals (e.g., `Ready`, `MemoryPressure`, `DiskPressure`, `PIDPressure`) that kubelet reports, which the Node Controller (Chapter 07 Section 4.4) watches to decide whether to evict Pods from an unhealthy node.

---

## 5. Internal Working: From Pod Assignment to Running Container (Node-Side Detail)

```
1. kube-scheduler has already assigned the Pod to this node
   (Pod object's nodeName is now set, per Chapter 07 Section 4.3)
        ↓
2. kubelet's watch on the API server notices a new Pod assigned to its node
        ↓
3. kubelet calls the container runtime via the CRI (Chapter 05) to:
     a. Pull required container images (if not already cached locally)
     b. Create a sandbox (the shared network/IPC namespace for the Pod)
     c. Start each container defined in the Pod spec
        ↓
4. kubelet mounts any required volumes (Chapter 19) into the containers
        ↓
5. kubelet begins running configured startup/liveness/readiness probes
   on a recurring schedule
        ↓
6. kubelet continuously reports Pod status (Running, Ready, etc.)
   back to the API server
        ↓
7. Meanwhile, kube-proxy (watching Services/Endpoints via the API server)
   updates its local iptables/IPVS rules so that Service traffic can
   now reach this Pod once it's marked Ready
```

---

## 6. Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        WORKER NODE                              │
│                                                                    │
│   ┌────────────────────────────────────────────────────┐   │
│   │                      kubelet                             │   │
│   │  - Watches API server for assigned Pods                   │   │
│   │  - Runs liveness/readiness/startup probes                 │   │
│   │  - Reports node & Pod status back to API server            │   │
│   │  - Talks to runtime via CRI                                │   │
│   └───────────────────────┬────────────────────────────┘   │
│                              │ CRI (gRPC)                        │
│                              ▼                                    │
│   ┌────────────────────────────────────────────────────┐   │
│   │              Container Runtime (containerd, etc.)          │   │
│   │  ┌────────┐   ┌────────┐   ┌────────┐                │   │
│   │  │  Pod A   │   │  Pod B   │   │  Pod C   │                │   │
│   │  │(sandbox+  │   │(sandbox+  │   │(sandbox+  │                │   │
│   │  │containers)│   │containers)│   │containers)│                │   │
│   │  └────────┘   └────────┘   └────────┘                │   │
│   └────────────────────────────────────────────────────┘   │
│                                                                    │
│   ┌────────────────────────────────────────────────────┐   │
│   │                    kube-proxy                            │   │
│   │  - Watches Services/Endpoints via API server               │   │
│   │  - Programs iptables/IPVS rules for Service routing        │   │
│   └────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 7. Component Breakdown

| Component | Talks To | Direction | Purpose |
|---|---|---|---|
| kubelet | kube-apiserver | Watches (in) + Reports (out) | Pod lifecycle, health, resource reporting |
| kubelet | Container runtime | Calls (out), via CRI | Create/destroy containers |
| kube-proxy | kube-apiserver | Watches (in) | Learn current Services/Endpoints |
| kube-proxy | Node's iptables/IPVS | Programs (out) | Route Service traffic to healthy Pods |

---

## 8. Important Terminology

| Term | Meaning |
|---|---|
| kubelet | Per-node agent ensuring assigned Pods are running and healthy |
| kube-proxy | Per-node component implementing Service network routing rules |
| Liveness probe | Health check determining whether a container should be restarted |
| Readiness probe | Health check determining whether a container should receive traffic |
| Startup probe | Health check delaying liveness/readiness checks until slow startup completes |
| Node capacity | Total physical resources available on a node |
| Allocatable resources | Capacity minus resources reserved for system/OS overhead |
| Node condition | A reported health signal like `Ready`, `MemoryPressure`, `DiskPressure` |
| CRI | Container Runtime Interface — the API kubelet uses to talk to any compliant runtime (Chapter 05) |

---

## 9. YAML Deep Dive

Probes are configured directly in a Pod's container spec:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: probe-demo
spec:
  containers:
    - name: app
      image: myapp:1.0
      livenessProbe:
        httpGet:
          path: /healthz
          port: 8080
        initialDelaySeconds: 5
        periodSeconds: 10
      readinessProbe:
        httpGet:
          path: /ready
          port: 8080
        periodSeconds: 5
      startupProbe:
        httpGet:
          path: /startup
          port: 8080
        failureThreshold: 30
        periodSeconds: 2
```

Note how each probe is independently configured — a container can have all three, only some, or none (with real risk implications, covered in Section 15).

---

## 10. kubectl Commands

| Command | Purpose | Example |
|---|---|---|
| `kubectl describe node <node>` | Show capacity, allocatable, and conditions | `kubectl describe node worker-1` |
| `kubectl top node` | Show live resource usage (requires metrics-server) | `kubectl top node` |
| `kubectl get pods -o wide` | Show which node a Pod runs on and its IP | `kubectl get pods -o wide` |
| `kubectl describe pod <pod>` | Show probe configuration and recent probe failures in Events | `kubectl describe pod myapp-xyz` |
| `kubectl logs <pod>` | View container logs, often needed alongside probe failures | `kubectl logs myapp-xyz` |

---

## 11. Hands-on Examples

**Lab 1 — Observe a readiness probe removing a Pod from Service rotation without restarting it:**
```bash
kubectl apply -f probe-demo.yaml  # container serves /ready returning 500 initially
kubectl get endpoints myapp-service
# Pod's IP is absent from Endpoints because readiness probe fails
# but `kubectl get pods` still shows it Running (not restarted)
```

**Lab 2 — Trigger a liveness probe restart:**
```bash
kubectl run crasher --image=myapp:1.0 \
  --overrides='{"spec":{"containers":[{"name":"crasher","image":"myapp:1.0","livenessProbe":{"httpGet":{"path":"/healthz","port":8080}}}]}}'
kubectl get pod crasher -w
# Watch RESTARTS count increase in kubectl get pods once /healthz starts failing
```

**Lab 3 — Inspect node allocatable vs capacity:**
```bash
kubectl describe node worker-1
# Compare the "Capacity" and "Allocatable" sections directly —
# the gap is what's reserved for the OS and Kubernetes system daemons
```

---

## 12. Internal Flow

See Section 5's full 7-step node-side flow, picking up exactly where Chapter 07's control-plane-side flow leaves off (the moment a Pod's `nodeName` is set).

---

## 13. Real-World Examples

1. **Large-scale clusters (thousands of Services)** commonly switch kube-proxy from iptables mode to IPVS mode specifically to avoid the linear rule-matching slowdown described in Section 4.3 — a well-documented scaling milestone many platform teams cross.
2. **Slow-starting JVM-based applications** are a textbook use case for **startup probes** — without one, a slow JVM warmup can be mistaken for a liveness failure, causing a restart loop that never lets the application actually finish starting.
3. **Database-backed services** commonly use readiness probes that check database connectivity, ensuring traffic is only sent to Pods that can actually serve real requests — not just Pods whose process happens to be running.
4. **Managed Kubernetes providers** (EKS, GKE, AKS) tune kubelet's reserved resources (the gap between capacity and allocatable, Section 4.4) differently by instance type, which is why the "same size" VM can show different allocatable memory across cloud providers.
5. **Node problem detectors** (a CNCF-ecosystem tool) extend node condition reporting beyond kubelet's defaults, feeding additional custom conditions (like hardware errors) into the same Node Controller eviction logic described in Chapter 07.

---

## 14. Best Practices

- Always define a readiness probe for any Pod receiving Service traffic — without one, Kubernetes assumes the Pod is ready the instant the container starts, potentially before the application can serve requests.
- Use a startup probe for slow-starting applications instead of setting an artificially long `initialDelaySeconds` on the liveness probe — this is more precise and avoids blind waiting.
- Keep liveness probes simple and cheap (e.g., a lightweight `/healthz` endpoint) — an expensive or dependency-heavy liveness check can cause unnecessary restart loops if a downstream dependency is merely slow.
- Set resource requests/limits accurately so the scheduler's view of allocatable resources reflects real application needs (Chapter 20 detail).
- Prefer IPVS mode for kube-proxy in large clusters with many Services.

---

## 15. Common Mistakes

- Confusing liveness and readiness probes — using the same expensive check for both can cause a slow dependency to trigger unnecessary container restarts (liveness) instead of just a temporary traffic pause (readiness).
- Omitting a readiness probe entirely, causing traffic to be sent to Pods before they're actually able to handle it (especially right after startup).
- Setting liveness probe checks that depend on external services (e.g., a database) — if the database has a blip, all your Pods get restarted simultaneously, which doesn't fix the actual problem and can cause a restart storm.
- Forgetting that `kubectl top node` requires metrics-server to be installed — it's not built into kubelet's default reporting path for CLI display.

---

## 16. Troubleshooting

| Symptom | Likely Cause | Debugging Commands | Fix |
|---|---|---|---|
| Pod never receives traffic despite `Running` status | Readiness probe failing | `kubectl describe pod`, check Events and `/ready` endpoint | Fix the readiness endpoint or its dependencies |
| Pod stuck in a restart loop | Liveness probe failing repeatedly, or app crashing | `kubectl logs --previous`, `kubectl describe pod` | Fix underlying app issue; consider a startup probe if it's just slow to start |
| Node shows `MemoryPressure` or `DiskPressure` condition | Node resource exhaustion | `kubectl describe node` | Free resources, add nodes, adjust resource requests/limits |
| Service traffic not reaching any Pods | kube-proxy rules not updated, or no Pods marked Ready | `kubectl get endpoints`, check kube-proxy logs | Investigate kube-proxy health, verify readiness probes pass |

---

## 17. Comparison Tables

**Liveness vs Readiness vs Startup Probes:**

| Aspect | Liveness | Readiness | Startup |
|---|---|---|---|
| Failure action | Restart container | Remove from Service endpoints | Delay liveness/readiness checks |
| Typical use | Detect hangs/deadlocks | Detect temporary inability to serve traffic | Handle slow application startup |
| Restarts container? | Yes | No | No (but blocks other probes until passed) |

**iptables vs IPVS (kube-proxy modes):**

| Aspect | iptables | IPVS |
|---|---|---|
| Lookup mechanism | Sequential rule matching | Hash-table based |
| Performance at scale | Degrades roughly linearly with Service count | Near-constant time |
| Maturity/default | Long-standing default | Newer, recommended for very large clusters |

---

## 18. Memory Tricks

- **"Liveness = alive or dead. Readiness = ready or busy."** Liveness failure kills the container; readiness failure just pauses traffic.
- **"kubelet talks up to the API server, and down to the runtime via CRI."**
- **kube-proxy = "the node's own directory board,"** always being updated as Pods (workers) move around.
- **Capacity − reserved overhead = Allocatable** — the number that actually matters for scheduling.

---

## 19. Interview Questions

**Easy:**
1. What is the difference between a liveness probe and a readiness probe?
   *Expected answer:* A liveness probe checks whether a container is still functioning correctly; if it fails, kubelet restarts the container. A readiness probe checks whether a container is currently able to serve traffic; if it fails, the Pod is removed from Service load-balancing endpoints, but the container itself is not restarted.

**Medium:**
2. Explain how kube-proxy enables a Service to route traffic to the correct Pods even as Pods are created and destroyed.
   *Expected answer:* kube-proxy watches the API server for Service and Endpoints/EndpointSlice objects, which track which Pod IPs currently back a given Service. Whenever Pods are created, destroyed, or change readiness status, kube-proxy updates its local node-level networking rules (iptables or IPVS) to reflect the current set of healthy backing Pods, ensuring traffic sent to the Service's stable virtual IP is always routed to a currently valid, ready Pod.

**Hard:**
3. A team adds a liveness probe that checks connectivity to an external database, and later experiences a cluster-wide restart storm during a brief database outage. Explain why this happened and how to fix it.
   *Expected answer:* Because the liveness probe's success depended on an external dependency (the database) rather than the container's own internal health, a temporary database outage caused every Pod's liveness probe to fail simultaneously, triggering kubelet to restart all of them at once — even though the containers themselves were healthy and the restarts did nothing to fix the actual database problem, potentially worsening the incident with a thundering-herd of reconnect attempts. The fix is to scope the liveness probe to only the container's own internal health (e.g., process responsiveness), and instead use a readiness probe for the database-dependency check — that way, a database outage correctly pauses traffic to affected Pods without needlessly restarting healthy containers.

---

## 20. KCNA Practice Questions

**Q1.** What is the primary role of kubelet on a worker node?
A. To make global scheduling decisions for the entire cluster
B. To store the cluster's complete state
C. To ensure the containers described in Pods assigned to its node are running and healthy
D. To route Service traffic between nodes

**Correct answer: C**
*Explanation:* kubelet is the per-node agent responsible for Pod lifecycle management and health reporting on its own node. A describes kube-scheduler, B describes etcd, and D describes kube-proxy.

---

**Q2.** Which kubelet probe type, upon failure, causes the container to be restarted?
A. Readiness probe
B. Liveness probe
C. Startup probe
D. Admission probe

**Correct answer: B**
*Explanation:* A failing liveness probe signals that kubelet should restart the container. A failing readiness probe (A) only removes the Pod from Service endpoints without restarting it. Startup probes (C) delay other probes rather than directly causing restarts on failure. "Admission probe" (D) is not a real Kubernetes probe type.

---

**Q3.** What happens when a Pod's readiness probe fails, but its liveness probe continues to pass?
A. The container is restarted immediately
B. The Pod is removed from Service endpoints but the container keeps running
C. The entire node is marked NotReady
D. The Pod is deleted and rescheduled to a different node

**Correct answer: B**
*Explanation:* A readiness failure only affects Service traffic routing — the Pod stops receiving new traffic via Services but the container itself is left running untouched, since liveness (which governs restarts) is unaffected. A, C, and D describe outcomes not caused by a readiness-only failure.

---

**Q4.** Why might a large cluster switch kube-proxy from iptables mode to IPVS mode?
A. IPVS mode supports more container runtimes
B. IPVS provides near-constant-time Service rule lookups, avoiding the linear scaling issues of iptables at large Service counts
C. iptables mode does not support TCP traffic
D. IPVS mode removes the need for kubelet on each node

**Correct answer: B**
*Explanation:* iptables uses sequential rule matching, which can slow down as Service count grows into the thousands, whereas IPVS uses kernel-level hash tables for near-constant-time lookups regardless of scale. A and C are factually false. D is unrelated — IPVS is only a kube-proxy implementation mode and has no bearing on kubelet's necessity.

---

**Q5.** What does the "Allocatable" value on a node represent?
A. The total physical resources installed on the machine
B. The resources available for Pods after subtracting reservations for the OS and system daemons
C. The number of Pods currently running on the node
D. The maximum number of Services the node can route traffic for

**Correct answer: B**
*Explanation:* Allocatable is Capacity minus reserved overhead for the OS and Kubernetes system components like kubelet itself — it's the number the scheduler actually uses for Pod placement decisions. A describes Capacity, a related but distinct value. C and D are unrelated node metrics.

---

**Q6.** Why are startup probes useful for slow-starting applications?
A. They permanently disable liveness and readiness checks for that container
B. They delay liveness and readiness probing until the application finishes its initial startup, preventing premature restarts
C. They automatically scale the application horizontally during startup
D. They replace the need for a container image entirely

**Correct answer: B**
*Explanation:* A startup probe holds off liveness/readiness checks until the application signals it has finished starting, avoiding the scenario where a slow but healthy startup is mistaken for a liveness failure. A is incorrect — startup probes only delay, not permanently disable, the other probes. C and D describe unrelated concepts.

---

**Q7.** Which component is responsible for calling the container runtime to actually start and stop containers on a node?
A. kube-scheduler
B. kube-apiserver
C. kubelet
D. etcd

**Correct answer: C**
*Explanation:* kubelet uses the CRI (Container Runtime Interface, Chapter 05) to instruct the container runtime to create and destroy containers based on assigned Pod specs. A and B are control plane components not directly involved in this node-level runtime interaction; D is a data store with no runtime interaction role at all.

---

**Q8.** A Pod has no readiness probe configured. What is the default behavior regarding when it starts receiving Service traffic?
A. It never receives traffic until a readiness probe is manually added
B. It is considered ready as soon as the container starts, and may receive traffic immediately
C. It waits for the liveness probe to pass first
D. It waits 60 seconds by default before receiving any traffic

**Correct answer: B**
*Explanation:* Without an explicit readiness probe, Kubernetes assumes the container is ready as soon as it starts running, which can result in traffic being sent before the application is actually able to handle it — this is exactly why Section 14 lists defining a readiness probe as a best practice. A, C, and D describe behaviors that do not reflect Kubernetes' actual default.

---

**Q9.** What Node Condition would you expect to see reported if a node is running low on available memory?
A. `DiskPressure`
B. `PIDPressure`
C. `MemoryPressure`
D. `NetworkUnavailable`

**Correct answer: C**
*Explanation:* `MemoryPressure` is the specific node condition kubelet reports when available memory is low, which the Node Controller can act on (e.g., by evicting Pods). `DiskPressure` (A) and `PIDPressure` (B) report different resource constraints (disk space and process ID exhaustion respectively), and `NetworkUnavailable` (D) reports networking configuration issues, not memory.

---

**Q10.** A team configures an expensive, dependency-heavy liveness probe that queries an external database directly. During a brief database outage, what is the most likely negative outcome?
A. Nothing — liveness probes never affect running containers
B. Only the Service's readiness routing is affected, with no container restarts
C. All affected Pods are restarted simultaneously even though their containers were otherwise healthy, worsening the incident
D. The node is automatically cordoned and drained

**Correct answer: C**
*Explanation:* Because liveness probe failure directly triggers a container restart, tying it to an external, temporarily-unavailable dependency causes kubelet to restart every affected Pod simultaneously — even though the containers' own internal health was fine — often worsening an already-degraded situation with a restart storm. A is false given this exact scenario. B describes the correct behavior for a *readiness* probe instead, which is the fix recommended in Section 19's hard interview question. D is not an automatic consequence of liveness probe failures.

---

**Q11.** Which mechanism does kubelet use to report node and Pod status back to the control plane?
A. Direct writes to etcd
B. Periodic updates sent to kube-apiserver, which persists them to etcd
C. A separate dedicated status-reporting daemon unrelated to kubelet
D. SNMP traps sent to kube-scheduler

**Correct answer: B**
*Explanation:* kubelet periodically reports node conditions and Pod statuses to kube-apiserver, which is the only component allowed to write to etcd, consistent with the single-access-path design from Chapter 07. A violates that design directly. C and D describe mechanisms Kubernetes does not use.

---

**Q12.** What is the primary purpose of kube-proxy on a worker node?
A. To schedule Pods onto the node
B. To maintain node-level networking rules that route Service traffic to the correct backing Pods
C. To pull container images from the registry
D. To enforce RBAC policies for API requests

**Correct answer: B**
*Explanation:* kube-proxy's entire job is keeping each node's networking rules (iptables/IPVS) in sync with current Service-to-Pod mappings so Service traffic reaches a healthy backing Pod. A is kube-scheduler's job, C is the container runtime's job via kubelet, and D is enforced by kube-apiserver, not kube-proxy.

---

**Q13.** A Pod's container passes its liveness probe but keeps failing its readiness probe for an extended period. What is the most likely operational impact?
A. The container is repeatedly restarted
B. The Pod never receives Service traffic while the container keeps running, potentially masking a real application problem
C. The node is marked NotReady
D. The Pod is evicted and rescheduled elsewhere

**Correct answer: B**
*Explanation:* Since liveness is passing, no restarts occur, but persistent readiness failure permanently excludes the Pod from Service endpoints — worth investigating, since the app is technically "alive" but never actually serving traffic. A, C, and D describe outcomes not triggered by a readiness-only, ongoing failure.

---

**Q14.** Why does kubelet use the CRI (Container Runtime Interface) rather than calling a specific runtime's proprietary API directly?
A. CRI is faster than any proprietary API
B. CRI decouples kubelet from any single runtime implementation, letting operators swap runtimes without changing kubelet's code (see Chapter 05)
C. CRI is required for etcd compatibility
D. Only CRI supports Linux containers

**Correct answer: B**
*Explanation:* This is the same decoupling rationale from Chapter 05 — a standard interface means kubelet works with containerd, CRI-O, or any CRI-compliant runtime without modification. A, C, and D are false characterizations of CRI's purpose.

---

**Q15.** A node reports the `DiskPressure` condition. What is the most likely automatic response by Kubernetes?
A. The API server shuts down
B. kubelet may begin evicting Pods and garbage-collecting unused images to reclaim disk space
C. All Pods are permanently deleted, and the node is removed from the cluster
D. etcd triggers a leader election

**Correct answer: B**
*Explanation:* `DiskPressure` triggers kubelet's node-level eviction and image garbage collection behaviors to relieve disk pressure, similar to how `MemoryPressure` triggers memory-related eviction. A, C, and D describe unrelated or overly drastic reactions that are not Kubernetes' actual behavior.

---

**Q16.** What is the relationship between a node's Capacity and Allocatable values?
A. They are always identical
B. Allocatable equals Capacity minus resources reserved for the OS and system daemons like kubelet
C. Capacity is calculated only after Pods are scheduled
D. Allocatable is always greater than Capacity

**Correct answer: B**
*Explanation:* This is the exact formula from Section 7/17: Allocatable = Capacity − reserved overhead, and it is the number the scheduler actually uses during Filtering. A and D are false, and C reverses the actual calculation order — Capacity is a static, hardware-derived value.

---

**Q17.** In what order does kubelet typically evaluate startup, readiness, and liveness probes for a slow-starting container?
A. Liveness first, then readiness, then startup
B. Startup probe first (if configured) blocks the other two until it succeeds; then readiness and liveness run independently
C. All three run simultaneously from the moment the container starts, with no ordering
D. Readiness always runs before startup

**Correct answer: B**
*Explanation:* A configured startup probe holds off both liveness and readiness checks until the application signals it has finished initializing, specifically to prevent a slow startup from being mistaken for a liveness failure. A, C, and D misstate this ordering.

---

**Q18.** Which statement correctly distinguishes kube-proxy's role from kubelet's role on the same node?
A. kube-proxy manages container lifecycle; kubelet manages Service traffic routing
B. kubelet manages Pod/container lifecycle and health; kube-proxy manages Service-to-Pod network routing rules
C. They perform identical, redundant functions for fault tolerance
D. kube-proxy replaces the need for a container runtime

**Correct answer: B**
*Explanation:* These are two distinct node-level responsibilities: kubelet owns Pod lifecycle and probes, while kube-proxy owns keeping networking rules in sync with Service endpoints. A reverses their roles, and C and D are false.

---

**Q19.** A Service's backing Pods change frequently due to autoscaling. Which mechanism ensures kube-proxy's routing rules stay current without manual intervention?
A. A nightly cron job that rewrites iptables rules
B. kube-proxy watching Endpoints/EndpointSlice objects via the API server and updating rules automatically on every change
C. Manual `kubectl` commands run by the cluster operator after every scale event
D. The container runtime notifying kube-proxy directly, bypassing the API server

**Correct answer: B**
*Explanation:* kube-proxy uses the same watch mechanism described in Chapter 07 to react to Endpoints/EndpointSlice changes in near real time, keeping routing continuously accurate without manual steps or scheduled jobs. A, C, and D describe mechanisms Kubernetes does not actually use.

---

**Q20.** Why is it considered a best practice to avoid using the same health check logic for both liveness and readiness probes on a container with external dependencies?
A. Kubernetes technically forbids configuring both probe types on one container
B. A shared dependency-based check can cause a liveness failure (and restart storm) for a problem that only warrants pausing traffic via readiness, as illustrated by the database-outage scenario in Section 19
C. Liveness and readiness probes must always use different HTTP ports
D. Readiness probes cannot check external dependencies at all

**Correct answer: B**
*Explanation:* This directly reflects the hard interview question's lesson: scoping liveness to only the container's own internal health, and reserving external-dependency checks for readiness, avoids unnecessary restart storms during transient external outages. A, C, and D are false constraints not present in Kubernetes.

---

## 21. Chapter Summary (One-Page Revision Sheet)

- **kubelet**: per-node agent; ensures assigned Pods run and stay healthy; talks to the API server (watch/report) and to the container runtime (via CRI).
- **Three probe types**: Liveness (restart on failure), Readiness (remove from Service traffic on failure, no restart), Startup (delays the other two for slow-starting apps).
- **kube-proxy**: per-node component maintaining Service routing rules; two modes — iptables (simple, linear scaling) and IPVS (hash-table based, scales better).
- **Capacity vs Allocatable**: Allocatable = Capacity minus reserved OS/system overhead; this is what the scheduler actually uses.
- **Node Conditions** (`Ready`, `MemoryPressure`, `DiskPressure`, `PIDPressure`) feed into the Node Controller's eviction decisions (Chapter 07).
- Node-side Pod startup flow: scheduler assigns → kubelet notices via watch → CRI calls to runtime → volumes mounted → probes begin → status reported back → kube-proxy updates routing once ready.

---

### Chapter Completion Checklist

1. **Topics covered:** kubelet responsibilities, all three probe types and their distinct failure behaviors, kube-proxy's two modes, node capacity/allocatable/conditions.
2. **KCNA objectives completed:** Full architecture picture now complete across Chapters 06-08 (overview → control plane → worker nodes).
3. **Remaining objectives:** Kubernetes Objects and the object model itself (Chapter 09), before diving into individual workload types (Pods onward).
4. **Suggested revision checklist:** Explain the difference between all three probe types without notes; explain why Capacity ≠ Allocatable; describe kube-proxy's two modes and when to prefer each.
5. **Suggested hands-on exercises:** Complete Lab 1 and Lab 2 together and compare `kubectl get endpoints` output against `kubectl get pods` output during each — this contrast is the clearest way to internalize the liveness/readiness distinction.
6. **Related chapters:** Previous: [07-Control-Plane](../07-Control-Plane/README.md). Next: [09-Kubernetes-Objects](../09-Kubernetes-Objects/README.md) — the general object model (API resources, manifests, labels/selectors, namespaces) underlying every workload type covered from Chapter 10 onward.
