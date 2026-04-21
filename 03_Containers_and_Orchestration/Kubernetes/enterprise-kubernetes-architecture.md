# Enterprise Kubernetes Architecture & Fleet Management (7 YOE)

A mid-level engineer commands a single Kubernetes cluster. A Senior Engineer or Platform Architect manages a "Fleet" of clusters across multiple clouds and regions.

---

## 1. Fleet Management & Cluster API (CAPI)

In a large enterprise, you do not manually run `eksctl` or click through the Azure Portal to create clusters. You treat clusters as infrastructure-as-code objects.

### Cluster API (CAPI)
CAPI uses Kubernetes itself to provision, upgrade, and operate *other* Kubernetes clusters. You deploy a "Management Cluster" whose sole job is to manage the lifecycle of "Workload Clusters".

**How it works:**
1. You apply a YAML manifest of kind `Cluster` to the Management Cluster.
2. The CAPI Controller intercepts this and calls the Azure/AWS API to provision the underlying raw VMs, networking, and load balancers.
3. CAPI installs `kubeadm` on the VMs and bootstraps the control plane and worker nodes.
4. A single declarative YAML file now defines a physical cluster in AWS `us-east-1` and another in Azure `westeurope`.

---

## 2. Multi-Tenancy Architecture (vcluster)

When 50 different engineering teams need Kubernetes, creating 50 physical clusters results in massive "Control Plane Tax" (thousands of dollars wasted on underutilized AWS EKS / Azure AKS control plane fees) and extreme operational overhead.

### Soft Multi-Tenancy (Namespaces)
- Teams are isolated via `Namespaces`, `NetworkPolicies`, and `RBAC`.
- **Limitation:** They share the same Control Plane. A malicious or misconfigured team can exhaust the API Server or create Custom Resource Definitions (CRDs) that conflict with other teams.

### Hard Multi-Tenancy (`vcluster`)
Virtual Clusters (`vcluster`) are entire Kubernetes control planes running *inside* a namespace of an underlying host cluster.
- Each tenant gets their own isolated API Server, etcd (as sqllite), and Controller Manager.
- The tenant has `cluster-admin` access to their vcluster (can install their own CRDs and cluster-scoped resources) without affecting the host cluster.
- The `vcluster` syncer intercepts Pod creation requests from the virtual API Server and translates them into physical Pods on the underlying host nodes.

**The Hybrid Approach:** Use namespace isolation for closely related microservices, and `vcluster` for entirely separate business units or external customers.

---

## 3. Control Plane Scaling and etcd Optimization

Managed Kubernetes services (EKS, AKS, GKE) hide the control plane, but Senior SREs must understand its failure modes when operating self-hosted or heavily congested managed clusters.

### The `etcd` Bottleneck
`etcd` is the distributed key-value store holding the cluster state. It runs the Raft consensus algorithm.
- **Latency Sensitivity:** `etcd` disk sync latency must remain below 10ms. If disk I/O degrades, leader elections fail, and the cluster API becomes completely unresponsive. Always use ultra-fast Premium NVMe SSDs for etcd instances.
- **Space Exhaustion:** `etcd` has a hard storage limit of 2GB by default. If exceeded, the cluster goes into read-only mode.
  - **Mitigation:** Run `etcdctl defrag` forcefully and compact revision history aggressively using `kube-apiserver` flags.

### Controller Manager & API Server Throttling
In massive clusters (5000+ nodes), thousands of agents continuously hit the API Server.
- Use **Priority and Fairness (APF)** to categorize traffic. Prevent CI/CD pipeline bots from starving Kubelet node-status updates.
- If using large config maps / secrets, ensure controllers heavily utilize "Informers" (in-memory caches) instead of directly querying the API Server continuously.

---

## 4. Upgrades and Availability

### Cluster Upgrades (The N-1 Rule)
Kubernetes deprecates APIs rapidly (e.g., standardizing `v1beta1` to `v1`).
- Never skip a minor version (e.g., upgrading from 1.25 directly to 1.27 is prohibited).
- **The N-1 Node Upgrade Strategy:** Cordon/Drain a node -> Upgrade Kubelet -> Uncordon. The Control Plane must always be ahead of or identical to the version of the worker nodes.

### High Availability Design
A production control plane must have **3 or 5 master nodes** spread across Availability Zones to maintain Raft consensus. A load balancer provides the abstraction layer for worker nodes communicating with the masters.
