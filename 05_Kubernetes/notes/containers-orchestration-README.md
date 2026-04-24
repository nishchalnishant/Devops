# Containers and Orchestration

This section represents one of the most transformative shifts in modern software engineering. Containers allow us to package an application with all its dependencies, while Orchestration allows us to manage thousands of those containers across a cluster of servers.

***

### 6A. Docker: The Container Standard

Docker is the tool used to create, ship, and run containers. It ensures that an application works exactly the same on a developer's laptop as it does in production.

#### Dockerfiles, Images, and Containers

* Dockerfile: A text document containing all the commands a user could call on the command line to assemble an image. It’s the "recipe."
* Image: A read-only template used to create containers. Think of it as a "snapshot" of your application environment.
* Container: A running instance of an image. It is an isolated process that shares the host OS kernel but has its own filesystem and networking.

#### Volumes and Networking

* Volumes: By default, data inside a container is deleted when the container stops. Volumes allow you to persist data (like databases) on the host machine so it survives restarts.
* Networks: Docker allows you to create virtual networks so containers can communicate with each other securely (e.g., a Web container talking to a Database container) without exposing them to the public internet.

#### Advanced Docker Tools

* Docker Compose: A tool for defining and running multi-container applications (e.g., using one YAML file to launch an app, a database, and a cache).
* Docker Scout: A modern security tool that analyzes your images for vulnerabilities and provides remediation advice.
* Docker Init: A CLI tool that automatically generates the necessary Dockerfiles and Compose files by scanning your project, making containerization much faster for beginners.

***

### 6B. Kubernetes (K8s): The Orchestrator

If Docker is the "individual musician," Kubernetes is the Conductor of the orchestra. It automates the deployment, scaling, and management of containerized applications.

#### Core Building Blocks

* Pods: The smallest deployable unit in K8s. A pod usually holds one container (but can hold more if they are tightly coupled).
* Deployments: Tells K8s how many copies (replicas) of a pod should be running. If a pod crashes, the Deployment automatically starts a new one (Self-healing).
* Services: Provides a single, stable IP address or DNS name to access a group of pods.
* Ingress: An API object that manages external access to the services in a cluster, typically via HTTP/HTTPS. It acts as a smart "entry point."

#### Storage and Security

* PersistentVolumes (PV) & Claims (PVC): A way to manage "state" in a cluster. A PV is a piece of storage in the cluster, and a PVC is a "request" by a developer for that storage.
* Network Policies: Acts as a firewall for your pods, controlling which pods are allowed to talk to each other.
* RBAC (Role-Based Access Control): Regulates access to the Kubernetes API based on the roles of individual users or services.

#### Package Management & Service Mesh

* Helm: Often called the "apt-get for Kubernetes." It uses Charts (templates) to package complex K8s applications for easy sharing and installation.
* Kustomize: A template-free way to customize K8s manifests (YAML) for different environments (e.g., Dev, Staging, Production).
* Istio: A Service Mesh that adds an extra layer of security, traffic management (like canary deployments), and observability to your microservices without changing a single line of code.



This is Section 6: Containers & Orchestration (Docker & Kubernetes). For a mid-to-senior SRE/DevOps role, this is the most critical section. You must move beyond "how to write a Dockerfile" to "how to manage distributed systems at scale."

In production, you aren't just running containers; you are managing their lifecycle, resource contention, and network connectivity across a cluster of nodes.

***

#### 🔹 1. Improved Notes: Containers vs. Orchestration

**Docker Internals: Namespaces & Cgroups Redux**

A container is NOT a lightweight VM. It is a process isolated by the Linux Kernel.

* Namespaces: Provide the "illusion" of a private OS (UTS for hostname, NET for networking, PID for process IDs).
* Cgroups: Manage resource allocation. If a container hits its memory limit, the Kernel (not Docker) sends the OOM kill signal.
* Union File System (Overlay2): Docker uses layers. If you change one line in your code, only that layer (and subsequent ones) is rebuilt. This is why "Layer Optimization" is key for fast CI/CD.

**Kubernetes (K8s) Architecture: The Brains and the Brawn**

* The Control Plane (The Brains):
  * etcd: The source of truth (Key-Value store). If etcd dies, the cluster configuration is lost.
  * API Server: The only component that talks to etcd. Everything else (kubectl, scheduler) talks to the API Server.
  * Scheduler: Decides which node a Pod should live on based on resources and constraints.
* The Worker Nodes (The Brawn):
  * Kubelet: The "agent" on each node that ensures containers are running in a Pod.
  * Kube-proxy: Handles the networking logic (IPtables/IPVS) so services can talk to each other.
  * Container Runtime: (Docker, containerd, or CRI-O) the engine that actually runs the container.

***

#### 🔹 2. Interview View (Q\&A)

Q1: What happens internally when you run `kubectl apply -f deployment.yaml`?

*   Answer: 1. The API Server validates the YAML and stores the "desired state" in etcd.

    2\. The Deployment Controller notices the new spec and creates a ReplicaSet.

    3\. The ReplicaSet Controller notices it needs $X$ pods and creates Pod objects.

    4\. The Scheduler sees "unassigned" pods and assigns them to nodes with available resources.

    5\. The Kubelet on those nodes sees the assignment and tells the Container Runtime to pull the image and start the container.

Q2: Explain the difference between a Readiness Probe and a Liveness Probe.

* Answer: \* Liveness: "Am I alive?" If it fails, K8s kills the container and restarts it. (Use for deadlocks).
  * Readiness: "Am I ready to handle traffic?" If it fails, K8s stops sending traffic to the pod via the Service but _doesn't_ kill it. (Use for app startup or high load).
* Senior Twist: Mention Startup Probes for slow-starting legacy apps to prevent them from being killed before they even finish booting.

Q3: How do you handle "Stateful" applications (like Databases) in Kubernetes?

* Answer: You use a StatefulSet. Unlike a Deployment, a StatefulSet provides:
  1. Deterministic names (e.g., `db-0`, `db-1`).
  2. Stable network IDs.
  3. Ordered deployment and scaling.
  4. Persistent Volume Claims (PVC) that stay attached to the same pod identity even if it moves nodes.

***

#### 🔹 3. Architecture & Design: Scalability & Reliability

The Service Abstraction:

Pods are ephemeral (they die and get new IPs). A Service provides a stable IP/DNS name.

* ClusterIP: Internal communication.
* NodePort: Exposes a port on every node (Avoid in production).
* LoadBalancer: Integrates with Cloud LBs (AWS ELB/NLB).

Trade-offs: Resource Requests vs. Limits

* Requests: The minimum guaranteed resource. The Scheduler uses this to place pods.
* Limits: The maximum a pod can consume.
* SRE Concern: If `Request == Limit`, the pod is in the Guaranteed QoS class (highest priority). If you don't set limits, a single buggy pod can consume the entire node's memory, causing "Node Pressure" and killing critical system processes.

***

#### 🔹 4. Commands & Configs (The K8s Pro Toolset)

**The "Gold Standard" Pod Spec**

YAML

```
apiVersion: v1
kind: Pod
metadata:
  name: secure-app
spec:
  securityContext:
    runAsNonRoot: true # Security Best Practice
  containers:
  - name: web
    image: myapp:v1.2
    resources:
      requests:
        memory: "64Mi"
        cpu: "250m"
      limits:
        memory: "128Mi"
        cpu: "500m"
    ports:
    - containerPort: 80
```

**Critical CLI Commands**

Bash

```
# Debugging a failing pod
kubectl describe pod <pod-name>
kubectl logs <pod-name> --previous # See logs from a crashed container

# Check resource usage across the cluster (requires Metrics Server)
kubectl top nodes
kubectl top pods

# Forcefully delete a stuck pod (use with caution)
kubectl delete pod <name> --grace-period=0 --force
```

***

#### 🔹 5. Troubleshooting & Debugging

Scenario: A Pod is stuck in `ImagePullBackOff`.

1. Check the name: Did you mistype the image tag?
2. Check the Registry: Is the private registry (DockerHub/ECR) down or unreachable?
3. Check Authentication: Does the K8s namespace have the correct `imagePullSecrets`?

Scenario: A Pod is stuck in `Pending`.

1. Check Resources: Run `kubectl describe pod`. Is there a node with enough CPU/RAM?
2. Check Taints/Tolerations: Does the pod have permission to run on available nodes?
3. Check Persistent Volumes: Is the Pod waiting for a disk that is currently attached to a node in a different Availability Zone?

***

#### 🔹 6. Production Best Practices

* Small Images: Use Multi-stage builds or Distroless images to reduce the attack surface and speed up downloads.
* Never use `:latest`: Always use a specific version or image digest (SHA). This ensures deployments are predictable and rollbacks are possible.
* Anti-Affinity: Use Pod Anti-Affinity to ensure that multiple replicas of your app don't end up on the same physical node (to survive a node failure).
* Horizontal Pod Autoscaler (HPA): Scale pods automatically based on CPU/Memory or custom metrics (like request count).
* Anti-Pattern: Storing secrets in Environment Variables. Use K8s Secrets or, better yet, external secret managers like HashiCorp Vault.

***

#### 🔹 Cheat Sheet / Quick Revision

| **Term**  | **Simple Definition**     | **SRE Importance**                              |
| --------- | ------------------------- | ----------------------------------------------- |
| Pod       | Smallest deployable unit  | Shares Network/Storage for containers.          |
| Sidecar   | Helper container in a Pod | Handles logging, proxying (Envoy), or auth.     |
| Ingress   | L7 Load Balancer          | Routes traffic based on Hostname/Path.          |
| ConfigMap | Decoupled config          | Change app settings without rebuilding images.  |
| Namespace | Logical isolation         | Multi-tenancy and resource quotas.              |
| Helm      | Package manager           | Templates K8s YAMLs for different environments. |

***

This is Section 6: Containers & Orchestration. This is arguably the most "hands-on" part of a DevOps interview. At a senior level, the interviewer wants to know if you understand the low-level isolation of Docker and the distributed logic of Kubernetes.

***

#### 🟢 Easy: Container Fundamentals

_Focus: Docker basics and the "Why" of containers._

1. What is the difference between a Virtual Machine and a Container?
   * _Context:_ Focus on the Shared Kernel vs. Guest OS. Mention that containers are processes, not full machines.
2. Explain what a Docker Image "Layer" is and how it helps with build speed.
   * _Context:_ Discuss the Union File System and how caching works (if a layer doesn't change, Docker skips it).
3. What is a Kubernetes Pod, and why can't we just run a container directly in K8s?
   * _Context:_ A Pod is the smallest unit; it can hold multiple containers that share the same network (localhost) and storage.
4. What is the purpose of the `.dockerignore` file?
   * _Context:_ Similar to `.gitignore`, it prevents large or sensitive files (like `.git` or `node_modules`) from being sent to the Docker daemon, reducing image size.

***

#### 🟡 Medium: Orchestration & Objects

_Focus: Managing workloads, networking, and stability._

1. Explain the difference between a Deployment and a StatefulSet.
   * _Context:_ When would you use each? (e.g., Stateless web app vs. a Database that needs a stable network ID and persistent disk).
2. What are Liveness, Readiness, and Startup Probes? Give an example of when a Pod would fail Readiness but pass Liveness.
   * _Context:_ Liveness kills the pod; Readiness stops traffic. Example: A DB connection is down, so the app can't serve traffic (Readiness fail), but the process is still running fine (Liveness pass).
3. Explain the difference between `requests` and `limits` in a Pod spec.
   * _Context:_ How does the Scheduler use requests? What happens if a container exceeds its memory limit? (OOM Kill).
4. What are the different types of Services in Kubernetes? (ClusterIP, NodePort, LoadBalancer).
   * _Context:_ Focus on which is used for internal communication vs. exposing the app to the internet.

***

#### 🔴 Hard: Architecture & Deep Troubleshooting

_Focus: The "Control Plane," custom logic, and high-pressure failure scenarios._

1. Walk me through the lifecycle of a `kubectl apply` command. What components of the Control Plane are involved and in what order?
   * _Context:_ API Server → Etcd → Controller Manager → Scheduler → Kubelet → Container Runtime.
2. What is the role of `etcd`? What happens to the cluster if `etcd` becomes unavailable or corrupted?
   * _Context:_ It's the source of truth. If it's down, you can't make changes (no new pods, no updates), though existing pods will keep running.
3. Scenario: A Pod is stuck in `Pending` state. List at least 4 different reasons why this might happen.
   * _Context:_ 1. Insufficient CPU/RAM on nodes. 2. Taints/Tolerations mismatch. 3. PVC (Persistent Volume) is in a different AZ. 4. Node affinity rules are too strict.
4. Explain Kubernetes Networking and the role of the CNI (Container Network Interface). How do Pods on different nodes talk to each other?
   * _Context:_ Mention that every Pod gets a unique IP. Discuss how the CNI (like Calico or Flannel) manages the overlay network or routing.
5. What is a "Sidecar Container" pattern? Provide a real-world SRE use case.
   * _Context:_ Example: A Log-forwarder (Fluentbit) or a Service Mesh proxy (Envoy/Istio) running alongside the main app container.

***

#### 💡 Pro-Tip for your Interview

When talking about Kubernetes, always mention "Declarative State."

* The SRE Answer: "Kubernetes is a reconciliation engine. When I apply a YAML, I am defining the Desired State. The Control Plane continuously runs a loop to ensure the Actual State matches my definition. If a node fails, the Scheduler sees the gap and recreates the pods elsewhere to restore that state."

***

## 🔷 Advanced Orchestration & Containers (7 YOE)

If you are interviewing for a Senior or Staff position, answering questions about simple Deployments or standard `Dockerfile`s is no longer enough. You must understand massive fleet scaling, raw kernel security, and cryptography inside the supply chain.

**Continue your preparation with these advanced architectural modules:**

1. `[NEW]` [Container Runtimes & Supply Chain Security](./Docker/container-runtimes-and-security.md): The shift from Docker to `containerd/CRI-O`, secure sandboxes (gVisor/Kata), and cryptographically signing images using Sigstore (SLSA).
2. `[NEW]` [Enterprise Kubernetes Architecture](./Kubernetes/enterprise-kubernetes-architecture.md): Managing clusters-as-code (Cluster API), isolation limits, control plane scaling (etcd/Raft tuning), and Hard Multi-Tenancy via Virtual Clusters (`vcluster`).
3. `[NEW]` [Advanced Networking & Security](./Kubernetes/advanced-networking-and-security.md): The eBPF revolution (replacing `kube-proxy` with Cilium), transitioning from Ingress to the Gateway API, sidecarless Service Meshes (Ambient/Cilium), and admission controllers (Kyverno / OPA Gatekeeper).
