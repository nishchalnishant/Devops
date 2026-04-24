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

***

**Q: What is the role of the kubelet?**

The kubelet is the node agent that runs on every worker node. It watches the API server for Pods scheduled to its node, instructs the container runtime (via CRI) to start/stop containers, reports node and pod status back to the control plane, and executes liveness/readiness/startup probes. It does NOT manage containers it didn't create via the API server (static pods are an exception).

**Q: What is a ServiceAccount and why would a Pod need one?**

A ServiceAccount provides a Pod with an identity within the cluster. The API server automatically mounts a JWT token into Pods at `/var/run/secrets/kubernetes.io/serviceaccount/token`. Pods use this token to authenticate with the API server when making in-cluster API calls (e.g., an operator reading CRDs, Prometheus scraping the metrics API). Best practice: create dedicated ServiceAccounts per workload rather than using `default`.

**Q: What is the difference between a Job and a CronJob?**

A Job creates one or more Pods and ensures a specified number complete successfully. It's for one-shot tasks (database migrations, batch processing). A CronJob creates Jobs on a schedule (cron syntax). Key Job parameters: `completions` (total successful pods needed), `parallelism` (concurrent pods), `backoffLimit` (retry limit), `activeDeadlineSeconds` (global timeout). CronJob adds `schedule`, `concurrencyPolicy` (Allow/Forbid/Replace), `startingDeadlineSeconds`.

**Q: What are the phases of a Pod's lifecycle?**

`Pending` → scheduler hasn't placed it or images are pulling. `Running` → at least one container is running. `Succeeded` → all containers exited 0 (terminal, for Jobs). `Failed` → all containers exited and at least one exited non-zero (terminal). `Unknown` → API server can't reach the node. Within Running, individual containers have states: Waiting, Running, Terminated.

**Q: How do you pass configuration to a Pod from a ConfigMap?**

Three methods: (1) `envFrom: configMapRef` — inject all keys as env vars. (2) `env.valueFrom.configMapKeyRef` — inject a single key as a named env var. (3) `volumes.configMap` + `volumeMounts` — mount as files in a directory. File mounts support live updates (kubelet syncs changes within the `syncPeriod`, typically 60s); env vars do not — the pod must restart to pick up new values.

**Q: What is the difference between a Secret and a ConfigMap?**

Both store key-value data, but Secrets are base64-encoded and intended for sensitive data (passwords, tokens, TLS certs). base64 is NOT encryption — Secrets are stored in etcd in plaintext by default unless encryption at rest is configured. Kubernetes RBAC can limit Secret access separately from ConfigMap access. Secrets support types (`Opaque`, `kubernetes.io/tls`, `kubernetes.io/dockerconfigjson`, etc.) that trigger validation.

**Q: What is an Ingress and what does an Ingress Controller do?**

An Ingress is a Kubernetes API object that defines HTTP/HTTPS routing rules (host-based and path-based) to backend Services. An Ingress Controller is a separate deployment (NGINX, Traefik, HAProxy, AWS ALB, etc.) that watches Ingress objects and programs an actual reverse proxy. Without a controller, Ingress objects do nothing. One cluster typically has one controller but can have multiple using `IngressClass`.

**Q: What is the difference between a label and an annotation?**

Labels are key-value pairs used for selection and grouping — Services, Deployments, and NetworkPolicies use label selectors to target Pods. Annotations are key-value pairs for non-identifying metadata (build info, tool config, human notes). Annotations cannot be used in selectors. Labels have strict syntax constraints; annotation values can be arbitrary strings (including JSON blobs).

**Q: What happens when you run `kubectl drain <node>`?**

`kubectl drain` does two things: (1) cordons the node (marks it `SchedulingDisabled` so no new Pods are scheduled there), (2) evicts all non-DaemonSet Pods from the node via the Eviction API, respecting PodDisruptionBudgets. If a Pod has no controller, drain fails by default (use `--force` to delete it). Use before maintenance to safely empty a node. After maintenance, `kubectl uncordon <node>` re-enables scheduling.

**Q: What is a PersistentVolumeClaim (PVC) and how does it relate to a PersistentVolume (PV)?**

A PV is a cluster-level storage resource provisioned by an admin or dynamically by a StorageClass. A PVC is a namespace-level request for storage (size, access mode, StorageClass). Kubernetes binds a PVC to a matching PV. Pods mount PVCs. This decouples "I need 10Gi RWO storage" (PVC) from "here is an AWS EBS volume" (PV). Dynamic provisioning: if a StorageClass has a provisioner, creating a PVC auto-creates a PV.

**Q: What are the three PersistentVolume access modes?**

`ReadWriteOnce (RWO)` — mounted read-write by a single node (most block storage: EBS, Azure Disk). `ReadOnlyMany (ROX)` — mounted read-only by many nodes simultaneously. `ReadWriteMany (RWX)` — mounted read-write by many nodes simultaneously (requires network storage: NFS, CephFS, EFS, Azure Files). Note: access modes are enforced by Kubernetes scheduling/binding, not the underlying storage.

**Q: How does `kubectl rollout undo` work?**

It rolls back a Deployment to the previous revision. Kubernetes stores Deployment revision history in ReplicaSets (controlled by `revisionHistoryLimit`, default 10). `kubectl rollout history deployment/<name>` lists revisions. `kubectl rollout undo deployment/<name> --to-revision=3` rolls back to a specific revision. Under the hood, it scales up the old ReplicaSet and scales down the current one using the same rolling update strategy.

**Q: What is the difference between `kubectl delete pod` and eviction?**

`kubectl delete pod` sends a DELETE request to the API server, which sets a deletion timestamp and gives the pod `terminationGracePeriodSeconds` to shut down gracefully (SIGTERM, then SIGKILL). The eviction API (used by drain, the node's eviction manager, and cluster autoscaler) is a separate sub-resource that respects PodDisruptionBudgets before proceeding — a DELETE does not check PDBs.

**Q: What is a namespace and what does it scope?**

Namespaces provide a virtual cluster within a physical cluster for multi-team isolation. They scope: most API resources (Pods, Services, Deployments, ConfigMaps, Secrets, PVCs, ServiceAccounts, Roles, RoleBindings). Cluster-scoped resources are NOT namespaced: Nodes, PersistentVolumes, StorageClasses, ClusterRoles, ClusterRoleBindings, Namespaces themselves. NetworkPolicies and RBAC are namespace-scoped, making namespaces the primary isolation boundary.

**Q: What is the purpose of `kubectl get events --sort-by='.lastTimestamp'`?**

Events are the first thing to check when a Pod is stuck in Pending/CrashLoopBackOff/ImagePullBackOff. They record: scheduler decisions ("Insufficient cpu"), image pull failures, probe failures, OOMKills, volume mount errors. Events are namespaced, short-lived (1 hour TTL by default), and aggregated (count + lastTimestamp). Always check `kubectl describe pod <name>` which surfaces events inline.

