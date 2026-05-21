# Kubernetes (K8s)

```
Kubernetes (K8s)
├── Control Plane ("The Brain")
│   ├── API Server — single entry point; validates, persists to etcd
│   ├── etcd — key-value source of truth; stores all cluster state
│   ├── Scheduler — places Pods on Nodes (filter → score → bind)
│   └── Controller Manager — ~30 reconciliation loops (Deployment, ReplicaSet, Node…)
├── Worker Nodes ("The Muscle")
│   ├── Kubelet — node agent; runs probes; reports PodStatus
│   ├── Kube-proxy — iptables/IPVS/eBPF rules for Service routing
│   └── Container Runtime — containerd/CRI-O; executes via OCI runc
├── Core Objects
│   ├── Pod — smallest deployable unit; shared network + storage
│   ├── Deployment — manages ReplicaSets; rolling updates + rollback
│   ├── Service — stable ClusterIP/DNS for ephemeral Pod IPs
│   │   ├── ClusterIP (internal)
│   │   ├── NodePort (per-node port)
│   │   └── LoadBalancer (cloud LB)
│   ├── ConfigMap — non-sensitive config
│   └── Secret — sensitive data (base64-encoded, encrypt at rest)
├── Workload Controllers
│   ├── StatefulSet — ordered, stable names + PVCs per pod (databases)
│   ├── DaemonSet — one pod per node (log agents, CNI, monitoring)
│   ├── Job — run-to-completion batch task
│   └── CronJob — scheduled Job
├── Networking
│   ├── Flat pod network — every pod gets unique IP, no NAT
│   ├── CNI plugin — implements pod networking (Calico, Cilium, Flannel)
│   ├── CoreDNS — internal DNS; <svc>.<ns>.svc.cluster.local
│   └── Ingress — L7 HTTP routing; requires Ingress Controller
├── Scheduling Controls
│   ├── Taints & Tolerations — repel/allow pods on nodes
│   ├── Node/Pod Affinity — prefer or require co-location/separation
│   ├── HPA — scale replicas on CPU/memory/custom metrics
│   └── Topology Spread — distribute across zones/nodes
├── Production Best Practices
│   ├── Resource requests + limits (QoS classes)
│   ├── Liveness + Readiness probes
│   └── RBAC least privilege
└── Troubleshooting
    ├── kubectl describe pod / kubectl get events
    ├── ImagePullBackOff — check image name, tag, imagePullSecrets
    └── Pending — insufficient CPU/RAM, taint mismatch, PVC zone issue
```

## First Principles

- You have many containers to run across many machines — you need a **scheduler** to place them based on available resources.
- Machines fail — the **controller manager** continuously reconciles desired state vs. actual state, restarting and rescheduling pods automatically.
- Pods get new IPs on restart — you need a **Service abstraction** with a stable DNS name and virtual IP to decouple consumers from pod IPs.
- Config and secrets must not be baked into images — **ConfigMaps and Secrets** externalise them; change config without rebuilding.
- You need to deploy new versions without downtime — **Deployments** with declarative desired state + rolling update controllers (maxUnavailable/maxSurge) achieve zero-downtime rollouts and instant rollbacks.
- One monolithic orchestrator would be a single point of failure — every component talks only through the **API server**; the scheduler, controllers, and kubelets are decoupled, independently scalable, and replaceable.

Kubernetes is the "Operating System of the Cloud." It is an orchestration platform that manages the lifecycle of containers across a cluster of machines, providing scaling, self-healing, and service discovery.

#### 1. The Control Plane vs. Worker Nodes
*   **Control Plane:** The "Brain." It makes global decisions (e.g., scheduling) and detects/responds to cluster events.
    *   **API Server:** The entry point for all commands.
    *   **etcd:** The cluster's "Source of Truth" (Key-Value store).
    *   **Scheduler:** Decides which Node a Pod should run on.
    *   **Controller Manager:** Ensures the actual state matches the desired state.
*   **Worker Nodes:** The "Muscle." They run the applications.
    *   **Kubelet:** The agent that talks to the API server and manages containers on the node.
    *   **Kube-proxy:** Handles networking (load balancing) between pods.

#### 2. Core Objects (The Building Blocks)
1.  **Pod:** The smallest deployable unit (contains one or more containers).
2.  **Deployment:** Manages the state of Pods (scaling, rolling updates).
3.  **Service:** Provides a stable IP/DNS name to access a group of Pods.
4.  **ConfigMap / Secret:** Injects configuration and sensitive data into containers.

#### 3. Kubernetes Networking
K8s networking is "flat." Every Pod gets its own IP address and can talk to any other Pod in the cluster without NAT, regardless of which Node they are on.

***

#### 🔹 1. Improved Notes: Advanced Scheduling
*   **Taints & Tolerations:** Nodes can "Taint" themselves to repel certain pods. Pods need a "Toleration" to be scheduled there (e.g., keeping production pods off of staging nodes).
*   **Affinity & Anti-Affinity:** Rules that suggest or require pods to be placed together (for latency) or apart (for high availability).
*   **HPA (Horizontal Pod Autoscaler):** Automatically scales the number of pods based on CPU/RAM usage.

#### 🔹 2. Interview View (Q&A)
*   **Q:** What happens when a Node fails in K8s?
*   **A:** The Control Plane detects the failure. After a timeout, it marks the node as unreachable and schedules the Pods that were on that node onto other healthy nodes.
*   **Q:** What is the difference between a `ReplicaSet` and a `Deployment`?
*   **A:** A `ReplicaSet` ensures a specific number of pods are running. A `Deployment` is a higher-level object that manages `ReplicaSets` to allow for zero-downtime rolling updates.

***

#### 🔹 3. Architecture & Design: Service Discovery
Kubernetes uses an internal DNS service (CoreDNS). When you create a Service named `my-web`, other pods can reach it simply by using the hostname `my-web`. K8s handles the load balancing to the healthy pods behind the scenes.

***

#### 🔹 4. Commands & Configs (Power User)
```bash
# Get everything in the cluster
kubectl get all -A

# Debug a pod with a temporary shell
kubectl exec -it <pod_name> -- /bin/sh

# View the real-time events of the cluster (Best for debugging "Pending" pods)
kubectl get events --sort-by='.lastTimestamp'
```

***

#### 🔹 5. Troubleshooting & Debugging
*   **Scenario:** A Pod is in `ImagePullBackOff`.
*   **Fix:** Check if the image name is correct, if the tag exists, and if the cluster has the correct `imagePullSecrets` to talk to your private registry.

***

#### 🔹 6. Production Best Practices
*   **Resource Limits:** Always set `requests` and `limits` for CPU and Memory. Without them, one "noisy neighbor" pod can crash an entire node.
*   **Liveness & Readiness Probes:**
    *   **Liveness:** Restarts the pod if the app crashes.
    *   **Readiness:** Stops traffic to the pod if the app is still warming up.
*   **RBAC (Role-Based Access Control):** Never give "ClusterAdmin" to a user or service. Follow the principle of least privilege.

***

#### 🔹 Cheat Sheet / Quick Revision
| **Concept** | **Key Detail** | **SRE Context** |
| :--- | :--- | :--- |
| `Namespace` | Logical isolation | Dividing the cluster into Dev, Staging, and Prod. |
| `Ingress` | External access | Routing internet traffic (HTTP) to internal services. |
| `StatefulSet` | Persistent apps | Used for Databases (Mongo, Postgres) where order matters. |
| `Helm` | Package Manager | Standard way to share and deploy complex K8s apps. |

***

This is Section 5: Kubernetes. For a senior role, you should focus on **Custom Resource Definitions (CRDs)**, **Operators**, and **Service Meshes (Istio/Linkerd)**.

## System Design Perspective

- **etcd consistency trade-off:** etcd uses Raft — every write must be acknowledged by a quorum (n/2+1 nodes). This provides linearizable consistency at the cost of write latency. If etcd disk fsync is slow (>10ms), leader election storms occur. Choose NVMe/SSDs; monitor `etcd_disk_wal_fsync_duration_seconds`.
- **Control plane HA design:** Run 3 or 5 API server replicas behind a load balancer. Each API server is stateless — all state lives in etcd. An odd number of etcd nodes is required (3 tolerates 1 failure, 5 tolerates 2). An even number (4) gives no additional fault tolerance over 3.
- **Why the flat pod network:** NAT breaks distributed-system assumptions (address visibility, distributed tracing, peer-to-peer protocols). The flat model where a pod's IP is universally routable eliminates an entire class of networking bugs at the cost of requiring a CNI overlay (VXLAN) or BGP-based routing.
- **PodDisruptionBudget (PDB) — why it matters:** Without PDBs, `kubectl drain` (node maintenance) or Cluster Autoscaler scale-down can simultaneously evict all replicas of a service, causing an outage. PDBs enforce that at least N pods remain available during voluntary disruptions. This is the bridge between infrastructure operations and application SLAs.
- **Topology spread vs. anti-affinity:** Hard anti-affinity (`requiredDuringScheduling`) blocks scale-out once a topology domain is full (scheduler rejects new pods). Topology spread with `maxSkew` is a softer constraint that allows controlled imbalance and composes better with HPA.
- **Why not put workloads in `default` namespace:** Namespace is the primary RBAC and NetworkPolicy boundary. A policy mistake in `default` can expose all unrelated workloads. Namespace-per-team is the minimum viable isolation unit for multi-tenant clusters.