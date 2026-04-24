## Easy

**1. What is Kubernetes and what problem does it solve?**

Kubernetes is a container orchestration platform that automates deployment, scaling, self-healing, and management of containerized workloads across a cluster of machines.

**2. What is a Pod?**

A Pod is the smallest deployable unit in Kubernetes — it wraps one or more containers that share the same network namespace, IP address, and storage volumes.

**3. What is a Deployment?**

A Deployment manages a ReplicaSet and provides declarative updates, rolling upgrades, and rollback for a set of identical Pods.

**4. What is a Service and why is it needed?**

A Service provides a stable DNS name and IP address for a set of Pods (selected via labels). Pods are ephemeral and change IPs on restart — a Service decouples the consumer from the actual Pod IPs.

**5. What are the types of Kubernetes Services?**

- `ClusterIP`: internal-only, accessible within the cluster.
- `NodePort`: exposes the service on a port of every node.
- `LoadBalancer`: provisions a cloud load balancer with an external IP.
- `ExternalName`: maps the service to an external DNS name.

**6. What is a Namespace?**

A namespace is a virtual cluster within a Kubernetes cluster — it provides scope for names and allows resource isolation between teams or environments.

**7. What is a ConfigMap vs. a Secret?**

ConfigMap stores non-sensitive configuration as key-value pairs. Secret stores sensitive data (passwords, tokens) encoded in base64. Secrets can be mounted as volumes or injected as environment variables; they can be sealed and access-controlled with RBAC.

**8. What is `kubectl apply` vs. `kubectl create`?**

`kubectl create` creates a resource — fails if it already exists. `kubectl apply` creates or updates a resource using server-side merge — idempotent, preferred for GitOps and automation.

**9. What is a liveness probe vs. a readiness probe?**

- **Liveness probe:** Checks if the container is alive. If it fails, Kubernetes restarts the container.
- **Readiness probe:** Checks if the container is ready to serve traffic. If it fails, the container is removed from the Service's endpoints but not restarted.

**10. What is a DaemonSet?**

A DaemonSet ensures that exactly one Pod runs on every node (or a subset). Used for node-level agents like log collectors (Fluent Bit), monitoring agents (Datadog), or CNI plugins.

**11. What is a StatefulSet and when do you use it?**

A StatefulSet manages stateful applications — it provides stable, ordered Pod names (pod-0, pod-1), persistent volume claims per Pod, and ordered startup/shutdown. Used for databases, Kafka, Zookeeper.

**12. What is a PersistentVolume (PV) and PersistentVolumeClaim (PVC)?**

A PV is a piece of storage provisioned in the cluster. A PVC is a request for storage by a Pod. Kubernetes binds a PVC to a matching PV based on size and access modes.

**13. What is Helm and what problem does it solve?**

Helm is a package manager for Kubernetes. It bundles Kubernetes manifests into reusable Charts with templating, versioning, and release management. `helm install` and `helm upgrade` manage the full lifecycle of an application deployment.

**14. What is a Helm values file?**

A `values.yaml` file provides default configuration for a Helm Chart. Users can override values with `helm install --set key=value` or `-f custom-values.yaml` without modifying the chart templates.

**15. What is a Node taint and what is a toleration?**

A taint on a node repels Pods that don't explicitly tolerate it. A toleration in a Pod spec allows it to be scheduled on nodes with matching taints. Used to dedicate nodes for specific workloads (e.g., GPU nodes only for ML workloads).

**16. What is `kubectl port-forward` used for?**

It creates a tunnel from your local machine's port to a port on a Pod, allowing local access to a service running inside the cluster without exposing it externally. Used for debugging.

---

