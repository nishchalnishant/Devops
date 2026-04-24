# Kubernetes (K8s)

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
