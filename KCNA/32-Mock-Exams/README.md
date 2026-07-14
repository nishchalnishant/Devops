# 32 — Mock Exams

## 1. Learning Objectives

By the end of this chapter you will be able to:

- Simulate full KCNA exam conditions using five independent 60-question mock exams.
- Measure readiness objectively via domain-weighted scoring aligned to the real exam (Chapter 28, Section 4.2).
- Apply the three-pass time-management strategy (Chapter 28, Section 6) under realistic conditions.

**KCNA objectives covered:** Meta-chapter — full-length simulated assessment across all domains (Chapters 01-27).

---

## 2. Historical Background

Full-length mock exams are standard practice across every major certification industry — pilots train in simulators, medical boards use practice board exams, and IT certifications are no different. The value isn't just content review; it's calibrating time management, stamina, and question-reading speed under conditions matching the real thing, which isolated practice questions (Chapter 31) cannot fully replicate.

---

## 3. Motivation: Why Five Separate Full Exams Instead of One Large Question Bank?

**Analogy — Five Practice Marathons Before Race Day:**
A marathon runner doesn't run one long practice mile repeated 26 times — they run several full practice races at increasing readiness. Five independent mock exams let you track improvement across attempts (Exam 1 as a cold baseline, Exam 5 as a final readiness check), rather than only ever seeing the same fixed question set once.

---

## 4. Core Concepts: How to Use These Mock Exams

- Each exam has **60 questions**, weighted to match real KCNA domain proportions (Chapter 28, Section 4.2): ~28 Fundamentals, ~13 Orchestration, ~10 Architecture, ~5 Observability, ~5 Delivery (nearest whole-question rounding).
- Take each exam in one **90-minute** sitting, without notes, using the three-pass strategy (Chapter 28, Section 6).
- Score each exam, then review only the **missed questions'** explanations before moving to the next exam.
- Recommended order: Exam 1 (cold baseline) → targeted review → Exam 2 → ... → Exam 5 (final readiness gate, ideally 48-72 hours before the real exam).

---

## 5-12. (Not Applicable Sections)

This chapter's substance is the exam question banks themselves; Internal Working, Architecture, Component Breakdown, YAML Deep Dive, kubectl Commands, and Internal Flow sections are not applicable as standalone content here (each exam question already embeds relevant YAML/kubectl context where needed, consistent with Chapter 31's format).

---

## 13. Mock Exam 1 (Baseline)

*Instructions: 60 questions, 90 minutes, no notes. Answers and explanations follow the full question set.*

1. Which control plane component is the only one that communicates directly with etcd?
A. kubelet B. kube-scheduler C. kube-apiserver D. kube-proxy

2. What object maintains a stable network identity and per-replica storage across rescheduling?
A. Deployment B. StatefulSet C. DaemonSet D. Job

3. Which Service type provisions an external cloud load balancer?
A. ClusterIP B. NodePort C. LoadBalancer D. ExternalName

4. What does a readiness probe failure do to a Pod?
A. Restarts the container B. Removes it from Service Endpoints without restarting C. Deletes the Pod D. Cordons the node

5. What is the purpose of a PodDisruptionBudget?
A. Cap CPU usage B. Guarantee minimum available Pods during voluntary disruption C. Enforce RBAC D. Encrypt Secrets

6. Which CNCF maturity level indicates the most proven adoption and governance?
A. Sandbox B. Incubating C. Graduated D. Archived

7. What does the CSI interface standardize?
A. Container runtimes B. Storage drivers C. Network policies D. DNS resolution

8. In GitOps, what reverts manual cluster drift back to Git's declared state in ArgoCD?
A. prune B. selfHeal C. rollback D. sync-window

9. What is a "cold start" in a serverless/Knative context?
A. A node reboot B. Latency incurred scaling up from zero replicas C. A failed liveness probe D. A DNS cache miss

10. Which object grants cluster-wide (not namespace-scoped) RBAC permissions?
A. Role B. RoleBinding C. ClusterRole D. ServiceAccount

11. What is the role of kube-proxy?
A. Schedules Pods B. Implements Service networking rules on each node C. Stores cluster state D. Runs containers

12. What guarantees exactly one Pod per matching node?
A. Deployment B. DaemonSet C. StatefulSet D. ReplicaSet

13. What is the effect of a taint on a node without a matching toleration on a Pod?
A. The Pod is preferentially scheduled there B. The Pod is repelled from that node C. The node is drained D. The Pod is restarted

14. What is the primary function of Ingress?
A. L3/L4 firewalling B. L7 HTTP(S) routing to Services C. Storage provisioning D. DNS caching

15. What does a Kubernetes Secret provide by default?
A. Full encryption at rest B. Base64 encoding only, unless encryption at rest is configured C. Automatic rotation D. Namespace-wide sharing

16. What is the sidecar proxy pattern used for in a service mesh?
A. Storage snapshotting B. Transparent per-Pod traffic interception C. Node autoscaling D. DNS resolution

17. What are the three pillars of observability?
A. CPU, memory, disk B. Logs, metrics, traces C. Alerts, dashboards, reports D. Requests, errors, duration only

18. What does `minScale: "0"` on a Knative Service enable?
A. Guaranteed one warm replica B. Scale-to-zero when idle C. Unlimited maximum replicas D. Disabling autoscaling

19. What is the safe order for cluster upgrades per version skew policy?
A. Nodes first, then control plane B. Control plane first, then nodes, one minor version at a time C. All components simultaneously D. etcd last

20. What object type runs a task to completion with retry on failure?
A. Deployment B. Job C. DaemonSet D. Service

21. What does a NetworkPolicy's default-deny behavior mean once a Pod is selected by any policy?
A. All traffic is still allowed B. Only explicitly allowed traffic is permitted C. The Pod is deleted D. DNS is disabled

22. What is the relationship between a PVC and a PV?
A. PVC is cluster-scoped, PV is namespace-scoped B. PVC is a namespace-scoped request matching a PV C. They are unrelated D. PV requires no provisioning

23. What is etcd's role in the cluster?
A. Runs containers B. Distributed key-value store; source of truth for cluster state C. Schedules Pods D. Implements Service networking

24. What triggers a Horizontal Pod Autoscaler to add replicas?
A. Node taints B. Observed metrics (e.g., CPU) exceeding a target threshold C. PodDisruptionBudget violations D. RBAC changes

25. What does a liveness probe failure cause?
A. Removal from Endpoints only B. Container restart C. Node cordon D. Namespace deletion

26. What does the CNCF's TOC (Technical Oversight Committee) do?
A. Writes application code for projects B. Reviews/approves project maturity level progression C. Manages billing D. Hosts conferences only

27. What is a key difference between Istio and Linkerd?
A. Istio is lightweight and Rust-based; Linkerd is Envoy-based and feature-rich B. Istio is Envoy-based and feature-rich; Linkerd is lightweight and Rust-based C. They are identical in architecture D. Neither supports mTLS

28. What does ArgoCD's `prune` setting do?
A. Reverts manual changes B. Removes resources deleted from Git C. Restarts failed Pods D. Encrypts Secrets

29. What is the purpose of a LimitRange?
A. Caps total namespace resource consumption B. Sets default/min/max per-container resource values in a namespace C. Grants RBAC permissions D. Defines Ingress rules

30. What does a StorageClass enable?
A. Manual PV creation only B. Dynamic PV provisioning C. RBAC binding D. NetworkPolicy enforcement

31. What does the Gateway API's `HTTPRoute` object do that a plain Ingress object cannot express as cleanly?
A. L3 firewalling B. Fine-grained header/weight-based HTTP routing rules decoupled from the Gateway itself C. DNS caching D. Node scheduling

32. Which cluster component resolves internal Service names to ClusterIPs?
A. kube-proxy B. CoreDNS C. etcd D. kube-scheduler

33. What uniquely identifies Pods created by a CronJob's scheduled runs?
A. They share one Pod across runs B. Each scheduled run creates a new Job, which creates its own Pod(s) C. CronJobs cannot create Pods directly D. They reuse the previous run's Pod

34. What does Pod anti-affinity typically accomplish?
A. Forces all replicas onto one node B. Spreads replicas across different nodes/zones to reduce correlated-failure risk C. Grants RBAC permissions D. Encrypts inter-Pod traffic

35. What is the default identity a Pod uses to authenticate to the Kubernetes API server from inside the cluster?
A. The node's kubelet certificate B. Its mounted ServiceAccount token C. The cluster admin's kubeconfig D. No identity is required

36. Under the "restricted" Pod Security Standard, which of the following is disallowed by default?
A. Read-only root filesystems B. Running as a non-root user C. Running as privileged with host namespace access D. Setting resource requests

37. In distributed tracing, what does a single "span" represent?
A. An entire distributed trace B. One timed unit of work within a larger trace (e.g., one service call) C. A log aggregation rule D. A metrics scrape interval

38. What is the practical difference between a service mesh's PERMISSIVE and STRICT mTLS modes?
A. PERMISSIVE blocks all plaintext; STRICT allows it B. PERMISSIVE accepts both plaintext and mTLS traffic; STRICT requires mTLS only C. They are functionally identical D. STRICT disables encryption entirely

39. What does Knative Eventing primarily add on top of Knative Serving?
A. Autoscaling of HTTP services B. A standardized way to route event-driven traffic (e.g., from brokers/triggers) to services, not just direct HTTP calls C. Node provisioning D. Persistent storage provisioning

40. In the CNCF landscape, which category would a container runtime like containerd or CRI-O fall under?
A. Application definition B. Runtime C. Observability D. Provisioning

41. When performing a Kubernetes upgrade, what is the maximum supported version skew between the API server and kubelet in most supported releases?
A. Any number of minor versions B. Up to a small number of minor versions behind the API server (per the project's official skew policy) C. kubelet must always be newer D. No skew is ever permitted

42. What does `kubectl explain <resource>` do?
A. Applies a resource B. Shows a resource's field documentation and schema C. Deletes a resource D. Scales a resource

43. Which field on a container spec sets a hard ceiling that, if exceeded for CPU, results in throttling rather than termination?
A. `requests.cpu` B. `limits.cpu` C. `requests.memory` D. `limits.memory`

44. What is the effect of exceeding a container's `limits.memory`?
A. CPU throttling only B. The container is OOMKilled C. The Pod is silently rescheduled D. Nothing; memory limits are advisory

45. What does a Kubernetes `Namespace` primarily provide?
A. Node-level isolation B. A logical scope for resource names, quotas, and RBAC within one cluster C. Network encryption D. Storage provisioning

46. Which object would you use to guarantee a Pod only runs on nodes labeled with SSD-backed storage?
A. A PodDisruptionBudget B. A nodeSelector or node affinity rule matching that label C. A NetworkPolicy D. A LimitRange

47. What is the purpose of an admission controller in the API request lifecycle?
A. Encrypts etcd data at rest B. Intercepts and can mutate or validate requests after authentication/authorization, before persistence C. Schedules Pods to nodes D. Resolves DNS queries

48. Why is running containers as root inside a Pod considered risky even with namespace isolation?
A. It has no real risk B. A container breakout could gain root-equivalent access to the underlying node C. It only affects logging D. It disables networking

49. What does `kubectl rollout undo deployment/<name>` do?
A. Deletes the Deployment B. Reverts to the previous ReplicaSet revision C. Scales the Deployment to zero D. Pauses future rollouts permanently

50. What is the main advantage of a Horizontal Pod Autoscaler over manually running `kubectl scale`?
A. It only works once B. It continuously and automatically adjusts replica count based on live metrics, without manual intervention C. It changes node count D. It only affects StatefulSets

51. Which Kubernetes object is best suited for running a log-collection agent on every node, including newly added ones?
A. Deployment B. DaemonSet C. StatefulSet D. Job

52. What does "GitOps drift" refer to?
A. A network latency spike B. A divergence between the live cluster state and the state declared in Git C. A DNS resolution failure D. A scheduler bug

53. Why do many production clusters run three or five etcd members rather than one?
A. For load balancing HTTP traffic B. To maintain a quorum-based majority for fault tolerance if a member fails C. To increase Pod scheduling speed D. etcd requires an odd node count for licensing reasons

54. What does the `imagePullPolicy: IfNotPresent` setting do?
A. Always re-pulls the image B. Uses a locally cached image if present, pulling only if missing C. Never pulls images D. Pulls only from a private registry

55. In a service mesh, what does a "circuit breaker" policy protect against?
A. TLS certificate expiry B. Cascading failure from repeatedly calling an already-failing downstream service C. DNS misconfiguration D. Node disk pressure

56. What is the primary purpose of a Kubernetes `Namespace`-scoped `ResourceQuota`?
A. Grants network access B. Caps the total aggregate resource consumption (CPU, memory, object counts) within a namespace C. Grants RBAC permissions D. Defines Ingress hostnames

57. Why might a CI/CD pipeline holding long-lived cluster credentials be considered a larger security risk than a pull-based GitOps agent?
A. Pipelines cannot authenticate at all B. A compromised pipeline with standing cluster credentials widens the blast radius, whereas a pull-based in-cluster agent needs no external credentials C. GitOps agents are always less secure D. There is no meaningful difference

58. What does the `kubectl top pods` command require to function?
A. Nothing extra B. The metrics-server (or equivalent metrics pipeline) to be installed in the cluster C. A ServiceAccount token D. A running Ingress controller

59. Which of the following best distinguishes a Kubernetes `Job` from a `CronJob`?
A. A Job runs on a repeating schedule; a CronJob runs once B. A Job runs a task to completion once (or a fixed count); a CronJob wraps Jobs with a recurring schedule C. They are functionally identical D. CronJobs cannot retry on failure

60. What is the recommended remediation when a mock exam score is consistently below 75% in one specific domain?
A. Immediately retake the same mock exam repeatedly B. Return to full chapter review for that weak domain before further mock attempts C. Skip that domain entirely on the real exam D. Increase exam time limits

### Mock Exam 1 — Answer Key (Q1-60)

1-C, 2-B, 3-C, 4-B, 5-B, 6-C, 7-B, 8-B, 9-B, 10-C, 11-B, 12-B, 13-B, 14-B, 15-B, 16-B, 17-B, 18-B, 19-B, 20-B, 21-B, 22-B, 23-B, 24-B, 25-B, 26-B, 27-B, 28-B, 29-B, 30-B, 31-B, 32-B, 33-B, 34-B, 35-B, 36-C, 37-B, 38-B, 39-B, 40-B, 41-B, 42-B, 43-B, 44-B, 45-B, 46-B, 47-B, 48-B, 49-B, 50-B, 51-B, 52-B, 53-B, 54-B, 55-B, 56-B, 57-B, 58-B, 59-B, 60-B

*(Note on Q27: the correct answer is B — Istio is the Envoy-based, more feature-rich and complex mesh; Linkerd is the lightweight, Rust-based alternative, per Chapter 23, Section 17. Note on Q36: the correct answer is C — the "restricted" Pod Security Standard explicitly disallows privileged containers and host namespace access; the other options are all permitted/encouraged under "restricted.")*

---

## 14. Mock Exam 2 (Independent Set)

*Instructions: 60 questions, 90 minutes, no notes. Independent from Exam 1 — do not cross-reference answers.*

1. What is the smallest deployable unit in Kubernetes?
A. Container B. Pod C. Node D. Namespace

2. Which control plane component makes scheduling decisions about which node a Pod runs on?
A. kube-controller-manager B. kube-scheduler C. cloud-controller-manager D. kubelet

3. What does the kubelet do on each node?
A. Stores cluster state B. Ensures containers described in PodSpecs are running and healthy C. Routes Service traffic D. Issues TLS certificates

4. Which object type is best for a stateless web application that needs rolling updates?
A. StatefulSet B. Deployment C. DaemonSet D. Job

5. What is a ReplicaSet's job?
A. Route traffic B. Maintain a specified number of identical Pod replicas C. Store persistent data D. Enforce network policy

6. What happens when you delete a Pod managed by a Deployment?
A. The Deployment is deleted too B. A new Pod is created to maintain the desired replica count C. Nothing happens D. The node is cordoned

7. What is the purpose of labels in Kubernetes?
A. Encrypt data B. Key-value metadata used to select and organize objects (e.g., via selectors) C. Set resource limits D. Define network routes

8. What does a Kubernetes `Namespace` NOT provide?
A. Scoped resource names B. Strong node-level kernel isolation between namespaces C. RBAC scoping D. ResourceQuota scoping

9. Which field on a Pod spec restarts a crashed container automatically by default?
A. `restartPolicy: Always` (the default) B. `restartPolicy: Never` C. `restartPolicy: OnFailure` only D. There is no such field

10. What is the purpose of `kubectl get events`?
A. Lists cluster nodes B. Shows recent cluster events (e.g., scheduling failures, image pull errors) for troubleshooting C. Lists all Secrets D. Applies a manifest

11. What is the difference between `kubectl apply` and `kubectl create`?
A. They are identical B. `apply` is declarative and can update existing objects; `create` is imperative and fails if the object exists C. `create` supports YAML, `apply` does not D. `apply` only works on Pods

12. What does a ConfigMap store?
A. Sensitive credentials only B. Non-sensitive configuration data as key-value pairs, injectable into Pods C. Persistent volumes D. Node metadata

13. Why should Secrets not be treated as fully secure by default?
A. They cannot be mounted into Pods B. They are only base64-encoded by default, not encrypted, unless encryption at rest is enabled C. They expire after one hour D. They are always encrypted natively

14. What is the primary difference between a Pod's `requests` and `limits`?
A. They are identical B. `requests` is what the scheduler reserves; `limits` is the hard ceiling enforced at runtime C. `limits` is used for scheduling only D. `requests` is enforced at runtime only

15. What object exposes a stable virtual IP in front of a set of Pods?
A. Ingress B. Service C. ConfigMap D. Namespace

16. Which Service type is only reachable from within the cluster by default?
A. NodePort B. LoadBalancer C. ClusterIP D. ExternalName

17. What is the role of a Container Network Interface (CNI) plugin?
A. Schedules Pods B. Provisions Pod networking and IP address assignment C. Stores cluster state D. Manages Secrets

18. What does `kubectl port-forward` do?
A. Permanently exposes a Service externally B. Temporarily tunnels a local port to a Pod/Service for debugging C. Creates an Ingress rule D. Modifies a NetworkPolicy

19. What is a DaemonSet best suited for?
A. Stateless web apps B. Running exactly one Pod per (or per matching) node, e.g., log/metrics agents C. Batch jobs D. Databases needing stable identity

20. What does `kubectl describe pod <name>` show that `kubectl get pod <name>` does not?
A. Nothing extra B. Detailed events, conditions, and recent state transitions for troubleshooting C. Only the Pod's IP D. Only the Pod's labels

21. What triggers a Pod to be evicted under node memory pressure?
A. RBAC violation B. The kubelet reclaiming resources by evicting lower-priority/over-limit Pods C. A failed readiness probe D. A NetworkPolicy violation

22. What is the function of the `kube-controller-manager`?
A. Routes Service traffic B. Runs core reconciliation control loops (e.g., ReplicaSet, Node controllers) C. Resolves DNS D. Encrypts etcd

23. What does a StatefulSet guarantee that a Deployment does not?
A. Faster rollouts B. Stable, ordered Pod names and stable per-replica storage across rescheduling C. Higher availability D. Lower resource usage

24. What is the purpose of an `initContainer`?
A. Runs alongside the main container forever B. Runs to completion before the main container(s) start, for setup tasks C. Replaces the main container D. Only used for logging

25. What does `kubectl rollout status deployment/<name>` report?
A. Node health B. Live progress of an ongoing rolling update C. RBAC bindings D. PersistentVolume capacity

26. What is the effect of setting `replicas: 0` on a Deployment?
A. Deletes the Deployment B. Scales all Pods down to zero while keeping the Deployment object and history C. Pauses the API server D. Removes the associated Service

27. Which object type is designed to run a task exactly once (or a fixed number of times) and then stop?
A. Deployment B. Job C. DaemonSet D. StatefulSet

28. What is the purpose of a `PriorityClass`?
A. Sets CPU limits B. Influences scheduling and eviction order by assigning relative Pod priority C. Grants RBAC permissions D. Defines a Service's port

29. What does `kubectl cordon <node>` do?
A. Deletes the node B. Marks the node unschedulable for new Pods without evicting existing ones C. Restarts the kubelet D. Removes the node from etcd

30. What is the difference between `cordon` and `drain`?
A. They are identical B. `cordon` blocks new scheduling only; `drain` also evicts existing Pods after cordoning C. `drain` blocks new scheduling only D. Neither affects scheduling

31. What does Ingress use to determine which backend Service handles a request?
A. Only the source IP B. Host and/or path-matching rules defined in the Ingress resource C. Node labels D. Pod age

32. What is the Gateway API generally considered relative to Ingress?
A. A deprecated predecessor B. A more expressive, role-oriented successor supporting richer routing C. Unrelated to routing D. A storage API

33. What does CoreDNS provide inside a cluster?
A. Node provisioning B. DNS resolution for Services and Pods C. RBAC enforcement D. Image pulling

34. What does a NetworkPolicy do in the absence of any CNI support for it?
A. Still enforces rules at the API server B. Has no effect — enforcement requires a CNI plugin that implements NetworkPolicy C. Blocks all traffic by default D. Encrypts all traffic

35. What is the purpose of a PersistentVolume (PV)?
A. A namespace-scoped storage request B. A cluster-level storage resource, provisioned statically or dynamically, that PVCs bind to C. A ConfigMap alternative D. A network policy object

36. What does `accessModes: ReadWriteOnce` mean for a PersistentVolume?
A. Many nodes can mount it read-write simultaneously B. It can be mounted read-write by a single node at a time C. It is read-only forever D. It cannot be mounted at all

37. What does the CSI (Container Storage Interface) enable?
A. A standard plugin interface so storage vendors can integrate without core Kubernetes code changes B. Container image building C. Network policy enforcement D. DNS resolution

38. What does a Pod's `nodeSelector` field do?
A. Sets resource limits B. Constrains scheduling to nodes matching specified labels C. Grants RBAC permissions D. Defines storage class

39. What is the purpose of taints and tolerations together?
A. Grant network access B. Taints repel Pods from a node unless the Pod has a matching toleration C. Encrypt Pod traffic D. Bind PVCs to PVs

40. What does a `Role` (as opposed to a `ClusterRole`) scope permissions to?
A. The entire cluster B. A single namespace C. A single node D. A single Pod

41. What authenticates a Pod's outbound requests to the Kubernetes API server by default?
A. The node's SSH key B. Its mounted ServiceAccount token C. A shared cluster password D. No authentication is needed

42. What is the purpose of the Pod Security Standards' "baseline" level?
A. The most permissive; minimal restrictions B. A moderate policy blocking known privilege escalations while remaining broadly compatible C. Identical to "restricted" D. Only applies to system namespaces

43. What is etcd's consistency model built on?
A. Eventual consistency only B. The Raft consensus algorithm, requiring a quorum of members to agree C. No consistency guarantees D. Manual conflict resolution

44. What does horizontal scaling mean in a Kubernetes context?
A. Increasing a single Pod's resource limits B. Adding more Pod replicas to handle increased load C. Adding more etcd members D. Increasing node disk size

45. Why is direct write access to etcd by arbitrary cluster components avoided?
A. etcd cannot be written to at all B. Centralizing writes through the API server enforces consistent validation, authorization, and admission control C. etcd only supports reads D. It would improve performance

46. What are the three pillars of observability?
A. CPU, memory, disk B. Logs, metrics, traces C. Alerts, dashboards, uptime D. Requests, errors, retries only

47. What does a Prometheus "scrape" do?
A. Deletes old metrics B. Pulls current metric values from a target's exposed metrics endpoint at an interval C. Pushes logs to a database D. Restarts unhealthy Pods

48. What is the difference between a metric and a trace?
A. They are identical concepts B. A metric is an aggregated numeric measurement over time; a trace follows one request's path across services C. A trace is a type of log D. A metric always requires tracing infrastructure

49. What is the main risk of a liveness probe that checks an external dependency instead of local process health?
A. No risk; it's best practice B. It can cause cascading restart storms across unrelated Pods during an unrelated downstream outage C. It improves failure detection with no downside D. It disables the readiness probe

50. What is the purpose of a service mesh's mTLS?
A. One-way TLS from client to server only B. Mutual authentication and encryption between both communicating parties C. DNS encryption only D. Encrypting only external ingress traffic

51. What does GitOps use as the single source of truth for desired cluster state?
A. A shared Slack channel B. A Git repository C. The live cluster state itself D. A spreadsheet

52. What is the key difference between a push-based CI/CD deployment and a pull-based GitOps deployment?
A. They are identical in security posture B. Push requires the pipeline to hold cluster credentials; pull uses an in-cluster agent needing no external credentials C. Pull-based deployments cannot be automated D. Push-based deployments cannot use Git

53. What does ArgoCD's `sync-window` feature control?
A. Encryption schedules B. Time windows during which automated syncs are allowed or blocked C. RBAC bindings D. Node maintenance windows

54. What is a "cold start" in the context of scale-to-zero serverless platforms like Knative?
A. A node reboot after a crash B. The latency incurred when scaling up from zero replicas to serve a new request C. A DNS cache expiry D. A failed liveness probe

55. What does `minScale` control on a Knative Service?
A. Maximum allowed replicas B. The minimum number of warm replicas kept running to reduce cold starts C. CPU limits D. RBAC scope

56. In the CNCF landscape, which maturity level is typically assigned to a brand-new, early-stage project?
A. Graduated B. Sandbox C. Incubating D. Archived

57. What does the CNCF's Technical Oversight Committee (TOC) primarily do?
A. Writes production code for member projects B. Reviews and approves projects' maturity level progression C. Manages cloud billing for companies D. Only organizes conferences

58. What is the recommended safe order for a Kubernetes cluster upgrade?
A. Nodes first, then control plane, any version gap B. Control plane components first, then nodes, one minor version at a time C. All components simultaneously D. Data plane only, control plane never upgraded

59. What is the purpose of a PodDisruptionBudget during a voluntary node drain?
A. Prevents all node maintenance permanently B. Guarantees a minimum number/percentage of Pods remain available during the disruption C. Encrypts Pod traffic during drain D. Grants RBAC permissions during drain

60. What is the recommended cadence for taking the final mock exam before a real certification attempt?
A. Same day, minutes before the exam B. 48-72 hours before the real exam, leaving time to address any remaining weak domain C. Immediately after the first mock exam, back-to-back D. Only after passing the exam

### Mock Exam 2 — Answer Key (Q1-60)

1-B, 2-B, 3-B, 4-B, 5-B, 6-B, 7-B, 8-B, 9-A, 10-B, 11-B, 12-B, 13-B, 14-B, 15-B, 16-C, 17-B, 18-B, 19-B, 20-B, 21-B, 22-B, 23-B, 24-B, 25-B, 26-B, 27-B, 28-B, 29-B, 30-B, 31-B, 32-B, 33-B, 34-B, 35-B, 36-B, 37-A, 38-B, 39-B, 40-B, 41-B, 42-B, 43-B, 44-B, 45-B, 46-B, 47-B, 48-B, 49-B, 50-B, 51-B, 52-B, 53-B, 54-B, 55-B, 56-B, 57-B, 58-B, 59-B, 60-B

---

## 14A. Mock Exam 3 (Independent Set)

*Instructions: 60 questions, 90 minutes, no notes. Independent from Exams 1-2 — do not cross-reference answers.*

1. What is the primary purpose of the Kubernetes API server?
A. Runs containers directly B. The central entry point validating and processing all cluster API requests C. Stores logs D. Resolves DNS

2. Which component watches the API server and reconciles actual state toward desired state for core objects?
A. kubelet only B. kube-controller-manager C. etcd D. CoreDNS

3. What does "declarative configuration" mean in Kubernetes?
A. You script exact step-by-step commands B. You describe the desired end state, and the system works to achieve/maintain it C. Configuration cannot be version-controlled D. Only imperative commands are supported

4. What is the smallest unit the Kubernetes scheduler assigns to a node?
A. A container B. A Pod C. A Deployment D. A Namespace

5. What happens to a Pod's IP address if the Pod is rescheduled to a different node?
A. It stays the same B. It typically changes, which is why Services provide a stable abstraction C. It is reserved forever D. It becomes the node's IP

6. What is the purpose of an Owner Reference on a Kubernetes object?
A. Sets RBAC permissions B. Links a dependent object to its controller/owner for garbage collection C. Defines network policy D. Sets resource limits

7. What is the effect of deleting a Deployment (not just scaling to zero)?
A. Only the Pods are deleted, ReplicaSets remain B. The Deployment, its ReplicaSets, and its Pods are all deleted via garbage collection C. Nothing is deleted D. Only the Service is deleted

8. Which field would you change to perform a manual rolling update image change?
A. `spec.replicas` B. `spec.template.spec.containers[].image` C. `metadata.labels` D. `spec.selector`

9. What does `maxUnavailable` control during a Deployment rolling update?
A. Maximum new Pods created at once B. Maximum number/percentage of Pods that can be unavailable during the update C. Maximum node count D. Maximum Service endpoints

10. What does `maxSurge` control during a Deployment rolling update?
A. Maximum Pods that can be down B. Maximum number/percentage of extra Pods created above the desired count during the update C. Maximum node CPU D. Maximum Secrets mounted

11. What is a common reason a Pod stays in `Pending` state?
A. It passed all probes B. Insufficient matching node resources or unsatisfied scheduling constraints (taints, affinity) C. It has too many labels D. Its image was already pulled

12. What does `kubectl get pods -o wide` add over the default output?
A. Nothing B. Node name, Pod IP, and additional columns C. Only container logs D. Only RBAC info

13. Why does Kubernetes prefer a control loop model over one-time imperative scripts for managing infrastructure?
A. Scripts are always faster B. Control loops continuously detect and correct drift automatically, including after unexpected failures C. Control loops require less code D. There is no meaningful difference

14. What is a "Finalizer" in Kubernetes?
A. A scheduling hint B. A pre-delete hook that blocks object removal until cleanup logic completes C. A type of probe D. A resource limit

15. What does `kubectl exec -it <pod> -- /bin/sh` do?
A. Deletes the Pod B. Opens an interactive shell session inside a running container C. Restarts the Pod D. Scales the Deployment

16. What is the difference between a Pod's `command` and `args` fields?
A. They are identical B. `command` overrides the container's entrypoint; `args` overrides its default arguments C. `args` overrides the entrypoint D. Neither can be overridden

17. What object would you use to run a one-time database migration during a deployment?
A. DaemonSet B. Job C. StatefulSet D. Service

18. What does `kubectl logs -f <pod>` do?
A. Deletes logs B. Streams live logs from the Pod's container C. Forces a restart D. Forwards a port

19. What does a Pod's `terminationGracePeriodSeconds` control?
A. How long before scheduling B. How long the Pod is given to shut down gracefully before a SIGKILL C. How long probes wait D. How long images are cached

20. What is the purpose of a `preStop` lifecycle hook?
A. Runs after container start B. Runs before a container is terminated, for graceful cleanup C. Runs during scheduling D. Runs on liveness failure only

21. What does a Service's `selector` field determine?
A. Which nodes it runs on B. Which Pods (by matching labels) receive traffic routed through the Service C. Which namespace it belongs to D. Its DNS name only

22. What is the purpose of a headless Service (`clusterIP: None`)?
A. Disables the Service entirely B. Returns individual Pod IPs directly via DNS instead of a single virtual IP, useful for StatefulSets C. Only works with Ingress D. Encrypts traffic

23. What does an Ingress controller do that the Ingress resource alone does not?
A. Nothing; Ingress works without a controller B. Actually implements/enforces the routing rules defined in Ingress resources C. Only handles DNS D. Only handles storage

24. What is the purpose of a NetworkPolicy's `podSelector` field?
A. Selects which nodes to apply to B. Selects which Pods the policy's rules apply to C. Selects which namespaces exist D. Selects which Services are exposed

25. What does "egress" refer to in a NetworkPolicy?
A. Incoming traffic to a Pod B. Outgoing traffic from a Pod C. Traffic between nodes only D. DNS traffic only

26. What is the purpose of a Gateway API `Gateway` resource?
A. Defines routing rules directly B. Represents the actual listener/entry point that `HTTPRoute` and similar resources attach to C. Stores Secrets D. Defines Pod scheduling

27. What does CoreDNS's `Corefile` configure?
A. Node scheduling rules B. DNS server plugins and behavior (e.g., caching, forwarding) C. RBAC bindings D. Storage classes

28. What is the difference between a StatefulSet Pod's ordinal-indexed name (e.g., `web-0`) and a Deployment Pod's generated name?
A. No difference B. StatefulSet names are stable and predictable across restarts; Deployment Pod names are arbitrary and regenerated C. Deployment names are also stable D. Neither has predictable naming

29. What is a "volume" in Kubernetes Pod terminology?
A. Always tied to node-local disk only B. An abstraction for storage made available to containers in a Pod, backed by various types (emptyDir, PVC, ConfigMap, etc.) C. A network policy object D. A scheduling constraint

30. What is the purpose of an `emptyDir` volume?
A. Persists data across Pod restarts on any node B. Provides temporary storage tied to the Pod's lifetime, cleared when the Pod is removed C. Provisions cloud storage D. Encrypts Secrets

31. What does a StorageClass's `reclaimPolicy` of `Retain` do?
A. Deletes the underlying storage when the PVC is deleted B. Keeps the underlying storage after the PVC is deleted, requiring manual cleanup C. Automatically re-provisions a new PV D. Encrypts the volume

32. What does `volumeBindingMode: WaitForFirstConsumer` on a StorageClass achieve?
A. Immediately binds a PV on PVC creation B. Delays volume binding/provisioning until a Pod using the PVC is actually scheduled, improving topology-aware placement C. Prevents any binding D. Only applies to ConfigMaps

33. What is a taint's `effect` of `NoSchedule` versus `NoExecute`?
A. They are identical B. `NoSchedule` blocks new Pods from scheduling; `NoExecute` also evicts already-running Pods lacking the toleration C. `NoExecute` only blocks new Pods D. Neither affects running Pods

34. What does Pod affinity (as opposed to anti-affinity) typically accomplish?
A. Spreads Pods across failure domains B. Co-locates Pods on the same node/zone as other specified Pods, e.g., for latency-sensitive pairs C. Grants RBAC permissions D. Encrypts traffic between Pods

35. What is the purpose of a `ServiceAccount`'s associated token?
A. Authenticates human users B. Provides a workload identity Pods use to authenticate to the API server C. Encrypts etcd D. Grants node SSH access

36. What does `automountServiceAccountToken: false` on a Pod spec do?
A. Deletes the ServiceAccount B. Prevents the ServiceAccount token from being automatically mounted into the Pod, reducing attack surface C. Disables the Pod entirely D. Forces use of a different Namespace

37. What is the least-privilege principle as applied to RBAC?
A. Grant all permissions by default and revoke as needed B. Grant only the minimum permissions necessary for a subject to perform its function C. Grant cluster-admin to all ServiceAccounts D. RBAC has no relation to least privilege

38. What does a `RoleBinding` referencing a `ClusterRole` (rather than a `Role`) accomplish?
A. Always grants cluster-wide access regardless of binding B. Grants the ClusterRole's permissions scoped only to the RoleBinding's namespace C. Has no effect D. Is not a valid combination

39. What is the purpose of Open Policy Agent (OPA) / Gatekeeper in a Kubernetes cluster?
A. Replaces etcd B. Enforces custom admission-time policy constraints beyond built-in RBAC C. Replaces the scheduler D. Provides DNS resolution

40. What does "supply chain security" in a Kubernetes/cloud native context primarily address?
A. Only network firewall rules B. Risks introduced across the software build/dependency/deployment pipeline (e.g., compromised images, dependencies) C. Only node hardware security D. Only user password policies

41. What is the purpose of image signing (e.g., via Sigstore/cosign)?
A. Compresses images B. Cryptographically verifies an image's origin and integrity before deployment C. Encrypts traffic between Pods D. Replaces RBAC

42. What does an SBOM (Software Bill of Materials) provide?
A. A billing invoice B. A manifest of all components/dependencies in a software artifact, aiding vulnerability tracking C. A Kubernetes resource quota D. A network topology diagram

43. What is the purpose of a metrics pipeline like Prometheus in cloud native observability?
A. Stores container images B. Collects, stores, and queries time-series numeric measurements for monitoring and alerting C. Routes Service traffic D. Manages RBAC

44. What is the difference between a log and a metric?
A. They are the same thing B. A log is a discrete, often unstructured event record; a metric is a numeric measurement aggregated over time C. Metrics cannot be time-series D. Logs cannot be structured

45. What is the purpose of a distributed tracing system like Jaeger or Tempo?
A. Stores container images B. Reconstructs a request's full path and timing across multiple services C. Replaces metrics entirely D. Manages RBAC bindings

46. What does an Alertmanager (in the Prometheus ecosystem) do?
A. Collects metrics directly B. Routes, groups, deduplicates, and silences alerts fired from alerting rules C. Runs containers D. Schedules Pods

47. What is a "golden signal" in SRE-style observability (e.g., latency, traffic, errors, saturation)?
A. A type of Kubernetes object B. A key high-level metric category used to assess service health C. A security scanning tool D. A GitOps sync strategy

48. What is the purpose of a service mesh's traffic-shifting/canary capability?
A. Deletes old versions immediately B. Gradually shifts a percentage of traffic to a new version to validate it safely before full rollout C. Only affects DNS D. Only affects storage

49. What is the difference between Istio's and Linkerd's typical complexity/resource footprint?
A. They are identical B. Istio (Envoy-based) is generally more feature-rich and heavier; Linkerd (Rust-based) is lighter and simpler C. Linkerd is Envoy-based and heavier D. Neither supports traffic splitting

50. What does "GitOps" fundamentally change compared to traditional imperative deployment scripts?
A. Nothing meaningful B. Git becomes the single source of truth, with an automated agent reconciling the live state to match it C. It removes the need for version control D. It requires manual SSH access to every node

51. What does Flux's (or ArgoCD's) reconciliation loop do if the live cluster state diverges from Git?
A. Ignores the divergence permanently B. Detects the drift and (if auto-sync/selfHeal is enabled) reverts the cluster back to match Git C. Deletes the Git repository D. Always requires a human to intervene first

52. What is a canary deployment strategy?
A. Deploying to all users simultaneously B. Gradually rolling out a change to a small subset of users/traffic before full rollout C. Rolling back automatically after every deploy D. Only used for database migrations

53. What is a blue-green deployment strategy?
A. Identical to canary B. Running two full environments (old and new) and switching traffic over at once when the new one is validated C. Only applicable to StatefulSets D. Requires no downtime tooling at all

54. What does Knative Serving primarily provide on top of raw Kubernetes Deployments?
A. Persistent storage B. Request-driven autoscaling, including scale-to-zero, with automatic revision management C. RBAC enforcement D. DNS resolution

55. What does a Knative `Revision` represent?
A. A mutable, ever-changing object B. An immutable snapshot of code and configuration at a point in time, enabling safe rollback C. A node image D. A NetworkPolicy version

56. In the CNCF landscape, which category would Prometheus and Grafana generally fall under?
A. Runtime B. Observability and analysis C. Provisioning D. Application definition

57. What is the purpose of the CNCF's "Graduated" maturity tier?
A. The earliest, most experimental stage B. Signals a project has demonstrated thriving adoption, broad governance, and long-term production sustainability C. A tier reserved only for Kubernetes itself D. A deprecated/archived tier

58. What is the recommended version-skew-safe order when upgrading a multi-node cluster?
A. Data plane first, one node at a time, control plane last B. Control plane components upgraded first, then worker nodes, one minor version at a time C. Randomly, since order doesn't matter D. All nodes and control plane simultaneously

59. Why is reviewing only missed questions (rather than all questions) recommended after each mock exam?
A. It saves time with no learning trade-off, focusing limited review time on genuine weak points rather than re-reading already-mastered material B. It is discouraged; all questions should always be reviewed C. Missed questions should never be reviewed D. Only correct answers should be reviewed

60. What is the purpose of tracking a score-by-domain breakdown across multiple mock exam attempts?
A. It has no practical use B. It reveals whether specific weak domains are actually improving between attempts, rather than relying on one aggregate score C. It only matters for the final exam attempt D. Domain breakdowns are not meaningful in KCNA scoring

### Mock Exam 3 — Answer Key (Q1-60)

1-B, 2-B, 3-B, 4-B, 5-B, 6-B, 7-B, 8-B, 9-B, 10-B, 11-B, 12-B, 13-B, 14-B, 15-B, 16-B, 17-B, 18-B, 19-B, 20-B, 21-B, 22-B, 23-B, 24-B, 25-B, 26-B, 27-B, 28-B, 29-B, 30-B, 31-B, 32-B, 33-B, 34-B, 35-B, 36-B, 37-B, 38-B, 39-B, 40-B, 41-B, 42-B, 43-B, 44-B, 45-B, 46-B, 47-B, 48-B, 49-B, 50-B, 51-B, 52-B, 53-B, 54-B, 55-B, 56-B, 57-B, 58-B, 59-A, 60-B

---

## 14B. Mock Exam 4 (Independent Set)

*Instructions: 60 questions, 90 minutes, no notes. Independent from Exams 1-3 — do not cross-reference answers.*

1. What does "cloud native" fundamentally describe about an application's design?
A. It must run only on a single public cloud B. It is designed to exploit cloud computing's elasticity, resilience, and automation (containers, microservices, dynamic orchestration) C. It must avoid containers entirely D. It requires a proprietary vendor stack

2. Which CNCF project was the founding, flagship project that the foundation was built around?
A. Prometheus B. Kubernetes C. Envoy D. Helm

3. What is a microservices architecture's core organizing principle?
A. One large monolithic deployable unit B. Decomposing an application into small, independently deployable services, each owning a bounded responsibility C. Avoiding APIs between components D. Requiring a single shared database for all services

4. What is the role of the cloud-controller-manager?
A. Schedules all Pods B. Integrates cluster management with cloud-provider-specific APIs (e.g., load balancers, node lifecycle) C. Stores cluster state D. Implements Service networking rules

5. What is the purpose of a Kubernetes "manifest" file?
A. A binary compiled artifact B. A YAML/JSON declaration of desired object state applied to the cluster C. A container image layer D. A log output file

6. What does `kubectl diff -f <file>` do?
A. Applies the file immediately B. Shows the difference between the file's desired state and the live cluster state without applying it C. Deletes the resource D. Rolls back a Deployment

7. What is the effect of a missing `resources.requests` on a container in a cluster using bin-packing-aware scheduling?
A. The Pod cannot be scheduled at all B. The scheduler has less information to make optimal placement decisions, risking node resource contention C. The container automatically gets unlimited resources reserved D. It has no effect on scheduling

8. What is a "sidecar" container within a Pod?
A. The only container allowed to run B. A secondary container running alongside the main container to provide supporting functionality (e.g., a proxy or log shipper) C. A replacement for initContainers D. A container that only runs during scheduling

9. What is the purpose of `kubectl scale deployment/<name> --replicas=5`?
A. Deletes the Deployment B. Imperatively sets the desired replica count to 5 C. Creates a new Deployment D. Pauses the Deployment

10. What does `kubectl rollout pause deployment/<name>` allow you to do?
A. Immediately roll back B. Stage multiple template changes before resuming a single combined rollout C. Delete the Deployment safely D. Scale to zero permanently

11. What is a "control loop" in Kubernetes controller design?
A. A one-time script execution B. A continuous watch-compare-act cycle reconciling actual state toward desired state C. A manual approval workflow D. A CI/CD pipeline stage

12. What does the term "desired state" mean in Kubernetes?
A. The state a Pod happened to start in B. The state declared in a manifest that controllers continuously work to achieve and maintain C. A deprecated concept D. Only relevant to StatefulSets

13. What is the purpose of `kubectl get all -n <namespace>`?
A. Lists cluster-wide RBAC only B. Lists most common namespaced object types (Pods, Services, Deployments, etc.) in that namespace C. Lists only Secrets D. Lists only PersistentVolumes

14. Why might a Pod remain in `ContainerCreating` for an extended period?
A. It has already started successfully B. Common causes include slow image pulls, volume mount issues, or missing ConfigMap/Secret references C. It indicates a passed liveness probe D. It indicates a successful rollout

15. What is the purpose of `kubectl apply --dry-run=client -f <file>`?
A. Actually applies the change B. Validates and previews the change locally without sending it to the API server for persistence C. Deletes the resource D. Forces an immediate rollout

16. What does a Deployment's `revisionHistoryLimit` field control?
A. How many replicas run B. How many old ReplicaSet revisions are retained for potential rollback C. How long Pods run D. How many nodes are used

17. What is the purpose of `kubectl taint nodes <node> key=value:NoSchedule`?
A. Removes a node from the cluster B. Applies a taint so only Pods with a matching toleration can be newly scheduled there C. Deletes all Pods on that node D. Grants RBAC permissions on that node

18. What does a Service's `targetPort` refer to?
A. The port exposed externally always B. The port on the backend Pod that traffic is forwarded to C. The node's SSH port D. The etcd client port

19. What is the difference between `NodePort` and `LoadBalancer` Service types?
A. They are identical B. NodePort exposes a static port on every node's IP; LoadBalancer additionally provisions an external cloud load balancer (and typically uses a NodePort internally) C. LoadBalancer never uses a NodePort D. NodePort works only in cloud environments

20. What is an `ExternalName` Service used for?
A. Load balancing across Pods B. Mapping a Service name to an external DNS name via a CNAME-like record, with no proxying C. Encrypting Pod traffic D. Storage provisioning

21. What does a CNI plugin like Calico additionally provide beyond basic pod networking?
A. Nothing beyond basic connectivity B. NetworkPolicy enforcement in many implementations C. DNS resolution only D. Storage provisioning

22. What is the purpose of `kubectl get networkpolicy -A`?
A. Lists all Pods B. Lists all NetworkPolicy objects across all namespaces C. Lists all Services D. Lists all Nodes

23. What happens to existing established connections when a NetworkPolicy is applied to newly restrict traffic?
A. They are always immediately terminated B. Behavior depends on the CNI's implementation; some enforce policy on new connections going forward C. NetworkPolicies never affect existing connections D. All connections are automatically encrypted

24. What is a "Service mesh data plane" typically composed of?
A. The control plane's configuration API only B. The set of sidecar proxies actually handling and observing traffic between services C. Only the Ingress controller D. Only the CNI plugin

25. What does a service mesh's control plane typically manage?
A. Raw packet forwarding B. Configuration distribution, certificate issuance, and policy management for the data plane's proxies C. Node provisioning D. Container image builds

26. What is the purpose of a `VolumeSnapshot` object?
A. Creates a new empty volume B. Captures a point-in-time snapshot of a PVC's data for backup or cloning C. Deletes a PV D. Grants RBAC to a volume

27. What does "dynamic provisioning" of storage mean?
A. An administrator manually creates each PV in advance B. A StorageClass automatically provisions a new PV on demand when a matching PVC is created C. Storage cannot be provisioned automatically D. Only applies to ConfigMaps

28. What is the purpose of a `Pod Topology Spread Constraint`?
A. Grants RBAC across topologies B. Controls how evenly Pods are distributed across topology domains like zones or nodes C. Encrypts cross-zone traffic D. Defines storage replication

29. What is the effect of setting `tolerations` on a Pod without any corresponding taint on the target node?
A. The Pod is rejected B. The toleration simply has no effect, since no matching taint exists to tolerate C. The Pod gains cluster-admin access D. It forces scheduling to that node

30. What does `kubectl get pv,pvc` commonly help diagnose?
A. RBAC misconfigurations only B. Storage binding issues, such as a PVC stuck in Pending due to no matching PV or StorageClass C. Networking issues only D. Node scheduling issues only

31. What is the purpose of a `Secret` of type `kubernetes.io/tls`?
A. Stores arbitrary config data B. Stores a TLS certificate and private key in a standardized format for use by Ingress or other TLS-terminating components C. Stores container images D. Stores RBAC bindings

32. What does `kubectl create secret generic` allow you to do?
A. Only creates TLS secrets B. Creates an arbitrary key-value Secret from literals or files C. Only creates ServiceAccounts D. Only creates ConfigMaps

33. What does Pod Security Admission (the built-in successor to PodSecurityPolicy) enforce?
A. Nothing by default B. Namespace-labeled Pod Security Standards levels (privileged/baseline/restricted) at admission time C. Only image scanning D. Only network policy

34. What is the purpose of `seccompProfile` on a Pod/container spec?
A. Grants extra syscalls unconditionally B. Restricts the set of syscalls a container process is allowed to make, reducing kernel attack surface C. Encrypts container traffic D. Defines resource limits

35. What is the purpose of `readOnlyRootFilesystem: true` in a container's securityContext?
A. Prevents the container from starting B. Mounts the container's root filesystem as read-only, reducing the impact of a runtime compromise C. Disables all volumes D. Forces use of emptyDir only

36. What does image vulnerability scanning (e.g., Trivy, Grype) primarily check for?
A. YAML syntax errors B. Known CVEs in an image's OS packages and application dependencies C. RBAC misconfigurations D. Network latency

37. What is the purpose of "shift-left" security in a DevSecOps pipeline?
A. Moving security checks to run only in production B. Moving security checks earlier in the development/CI pipeline, before deployment C. Removing security checks entirely D. Only applies to network security

38. What does SLSA (Supply-chain Levels for Software Artifacts) primarily provide?
A. A billing framework B. A framework of increasing levels of supply chain integrity guarantees for build provenance C. A container runtime D. A Kubernetes distribution

39. What is the purpose of Falco in a cloud native security stack?
A. Provisions storage B. Runtime security monitoring, detecting anomalous syscall-level behavior in running containers C. Manages DNS D. Manages RBAC bindings only

40. What does "least privilege" mean when applied to a Pod's securityContext?
A. Running as root with all capabilities by default B. Dropping unnecessary Linux capabilities and running as a non-root user unless a specific need is justified C. Disabling all security controls for simplicity D. Only applies to Namespaces, not Pods

41. What is the purpose of a `LimitRange` object in a namespace lacking explicit per-container resource requests?
A. Blocks all Pod creation B. Applies default request/limit values automatically so scheduling and eviction behavior remains predictable C. Grants RBAC permissions D. Defines Ingress rules

42. What does a `ResourceQuota` violation cause when a new Pod is created?
A. The Pod is silently throttled B. The API server rejects the Pod creation request C. The oldest Pod is automatically deleted D. The Namespace is deleted

43. What is the purpose of the Horizontal Pod Autoscaler's `stabilizationWindowSeconds` setting?
A. Sets a hard replica ceiling B. Reduces flapping by requiring a stable observation window before scaling actions are taken C. Sets CPU limits D. Sets RBAC scope

44. What does the Vertical Pod Autoscaler (VPA) adjust, as opposed to the Horizontal Pod Autoscaler (HPA)?
A. Replica count B. A Pod's resource requests/limits based on observed usage C. Node count D. Namespace quotas

45. What is a common risk of running HPA and VPA simultaneously on the same workload without careful configuration?
A. No risk; they always work seamlessly together B. They can conflict, since VPA resizing Pods and HPA changing replica counts can fight over the same signals C. VPA disables HPA automatically D. HPA disables VPA automatically

46. What does a Prometheus "alerting rule" define?
A. A dashboard panel B. A condition over metric data that, when true for a defined duration, fires an alert C. A log retention policy D. A scheduling constraint

47. What is the purpose of a "runbook" linked from an alert?
A. Deletes the affected resource automatically B. Documents step-by-step diagnostic and remediation guidance for responders C. Replaces on-call entirely D. Only used for post-mortems

48. What does "cardinality" refer to in a metrics/observability context?
A. The number of dashboards B. The number of unique label-value combinations for a metric, which impacts storage/query cost C. The number of nodes in a cluster D. The number of Namespaces

49. What is a common cause of "high cardinality" metrics problems?
A. Too few metrics collected B. Using highly unique values (e.g., user IDs, request IDs) as metric labels C. Scraping too infrequently D. Using too few dashboards

50. What is the purpose of OpenTelemetry in the cloud native observability landscape?
A. Replaces Kubernetes entirely B. Provides a vendor-neutral standard/SDK for generating and exporting traces, metrics, and logs C. Only handles container image builds D. Only handles DNS

51. What does a progressive delivery tool like Flagger or Argo Rollouts add on top of a plain Deployment?
A. Nothing beyond standard rolling updates B. Automated canary/blue-green analysis using live metrics to gate promotion or trigger rollback C. Only affects storage D. Only affects RBAC

52. What is the purpose of an ApplicationSet in ArgoCD?
A. Defines a single static Application only B. Templates and generates multiple ArgoCD Applications automatically from a defined generator (e.g., per cluster or per directory) C. Replaces Git entirely D. Manages RBAC only

53. What does "app of apps" refer to in ArgoCD usage patterns?
A. A single flat list of unrelated resources B. A parent Argo Application that manages a set of child Applications, enabling hierarchical GitOps management C. A deprecated anti-pattern with no valid use D. A Helm-only feature

54. What does Knative's `Service` object bundle together for the user?
A. Only a raw Deployment B. Configuration and Revision management plus automatic routing and autoscaling in one abstraction C. Only a NetworkPolicy D. Only a PersistentVolumeClaim

55. What is the purpose of a "broker" in Knative Eventing?
A. Stores container images B. Acts as an event mesh that receives events and routes them to interested triggers/subscribers C. Replaces the API server D. Manages RBAC bindings

56. In the CNCF landscape's "Provisioning" category, which type of tool would typically be listed?
A. Metrics dashboards B. Infrastructure automation/configuration tools (e.g., IaC, key management) C. Service meshes only D. Log aggregators only

57. What is the purpose of the CNCF's "Archived" project status?
A. Indicates the most mature, widely adopted status B. Indicates a project is no longer actively maintained/has been retired from active development C. Is a prerequisite before Sandbox D. Only applies to Kubernetes itself

58. Why does the official Kubernetes version skew policy restrict how far behind kubelets can be relative to the API server?
A. It has no technical rationale B. To bound the compatibility surface the API server and kubelet must support simultaneously, reducing upgrade risk C. To force all upgrades to happen instantly D. It only applies to etcd

59. What is the benefit of taking mock exams under strict, unaided 90-minute time limits rather than open-book?
A. It has no benefit over open-book study B. It produces a realistic readiness signal by also calibrating time pressure and recall speed, not just content knowledge C. It only tests typing speed D. It replaces the need for chapter review entirely

60. What is the purpose of using Exam 5 specifically as the final readiness gate rather than any earlier exam?
A. Earlier exams are more reliable B. Taken last, after the most cumulative review, it best reflects true final readiness shortly before the real exam C. It is the easiest exam by design D. It replaces the need to take Exams 1-4

### Mock Exam 4 — Answer Key (Q1-60)

1-B, 2-B, 3-B, 4-B, 5-B, 6-B, 7-B, 8-B, 9-B, 10-B, 11-B, 12-B, 13-B, 14-B, 15-B, 16-B, 17-B, 18-B, 19-B, 20-B, 21-B, 22-B, 23-B, 24-B, 25-B, 26-B, 27-B, 28-B, 29-B, 30-B, 31-B, 32-B, 33-B, 34-B, 35-B, 36-B, 37-B, 38-B, 39-B, 40-B, 41-B, 42-B, 43-B, 44-B, 45-B, 46-B, 47-B, 48-B, 49-B, 50-B, 51-B, 52-B, 53-B, 54-B, 55-B, 56-B, 57-B, 58-B, 59-B, 60-B

---

## 14C. Mock Exam 5 (Final Readiness Gate)

*Instructions: 60 questions, 90 minutes, no notes. Independent from Exams 1-4 — take this as the final go/no-go check, ideally 48-72 hours before the real exam.*

1. What is the relationship between containers and Pods?
A. A container can span multiple Pods B. A Pod wraps one or more containers sharing network and storage namespaces C. Pods run inside containers D. They are the same concept

2. What does the container runtime (e.g., containerd, CRI-O) actually do?
A. Schedules Pods to nodes B. Pulls images and runs/manages the container process lifecycle on a node C. Stores cluster state D. Implements Service networking

3. What is the Container Runtime Interface (CRI)?
A. A storage plugin standard B. A standardized API letting kubelet talk to different container runtimes interchangeably C. A network policy standard D. A DNS standard

4. What does `kubectl config use-context <name>` do?
A. Deletes a cluster B. Switches the active cluster/user/namespace context for subsequent kubectl commands C. Creates a new Namespace D. Applies a manifest

5. What is stored in a kubeconfig file?
A. Container images B. Cluster connection details, credentials, and context definitions for kubectl C. Pod logs D. Metrics data

6. What is the purpose of `kubectl api-resources`?
A. Lists running Pods only B. Lists all API resource types the cluster supports, with their shortnames and scope C. Lists nodes only D. Lists Namespaces only

7. What does "self-healing" mean in the context of Kubernetes controllers?
A. Manual intervention is always required B. Controllers automatically detect and correct deviations from desired state (e.g., replacing a crashed Pod) without human action C. Only applies to Node failures D. Only applies to Secrets

8. What happens when a node becomes `NotReady`?
A. Nothing changes for existing Pods B. After a grace period, the control plane may reschedule the node's Pods elsewhere C. The node is deleted immediately D. All cluster Namespaces are deleted

9. What is the purpose of `kubectl get componentstatuses` (or equivalent health checks) historically used for?
A. Checking core control plane component health B. Listing all Deployments C. Listing all NetworkPolicies D. Listing PersistentVolumes

10. What does a Deployment's `strategy.type: Recreate` do differently from `RollingUpdate`?
A. Gradually replaces Pods B. Terminates all old Pods before creating any new ones, causing brief downtime C. Never terminates old Pods D. Only applies to StatefulSets

11. What is the purpose of `kubectl label pod <name> key=value`?
A. Sets a resource limit B. Adds/updates a label on a live object without editing the full manifest C. Deletes the Pod D. Creates a new Deployment

12. What is the purpose of `kubectl annotate`?
A. Identical to labeling for selectors B. Attaches non-identifying metadata to an object, often used by tooling rather than selectors C. Deletes annotations only D. Only applies to Nodes

13. What does a Deployment's `spec.selector` need to match?
A. Node labels B. The labels on `spec.template.metadata.labels`, so the Deployment can identify its own Pods C. Namespace name D. ServiceAccount name

14. What is the purpose of `kubectl get rs` (ReplicaSets)?
A. Lists raw containers B. Lists ReplicaSet objects, useful for seeing Deployment revision history C. Lists Nodes D. Lists PersistentVolumes

15. What causes a Pod to show `CrashLoopBackOff`?
A. A passed liveness probe B. The container repeatedly crashing shortly after start, with Kubernetes applying an increasing backoff delay between restarts C. A pending PVC D. A missing label

16. What is the purpose of `kubectl get events --sort-by=.metadata.creationTimestamp`?
A. Lists Pods by age B. Lists cluster events ordered chronologically, useful for reconstructing an incident timeline C. Lists Nodes by capacity D. Lists Services by port

17. What does a Service's `sessionAffinity: ClientIP` setting do?
A. Randomly load-balances every request B. Routes repeated requests from the same client IP to the same backend Pod C. Blocks the client entirely D. Encrypts client traffic

18. What is the purpose of an Ingress `TLS` block?
A. Defines backend Service ports only B. Specifies which Secret holds the TLS certificate for terminating HTTPS at the Ingress C. Defines NetworkPolicy rules D. Defines RBAC bindings

19. What is a "multi-cluster Service" pattern typically used for?
A. Running unrelated apps in one cluster B. Exposing and discovering Services across multiple clusters, e.g., for failover or geo-distribution C. Only for single-node clusters D. Only for storage replication

20. What does `externalTrafficPolicy: Local` on a Service do?
A. Load-balances evenly across all nodes regardless of Pod location B. Routes traffic only to nodes with a local Pod, preserving client source IP but risking uneven load C. Disables external traffic entirely D. Forces traffic through Ingress only

21. What is the purpose of a Web Application Firewall (WAF) often integrated at the Ingress/Gateway layer?
A. Replaces RBAC B. Filters and blocks malicious L7 HTTP traffic patterns (e.g., SQLi, XSS) before reaching backend Services C. Replaces TLS termination D. Manages DNS records only

22. What does "topology-aware routing" in Kubernetes Services attempt to optimize?
A. RBAC scope B. Preferring to route traffic to endpoints in the same zone/region to reduce cross-zone latency and cost C. Storage replication D. Image pull speed

23. What is the difference between a PersistentVolume's `Bound` and `Available` phase?
A. They are identical B. `Available` means unclaimed and ready to bind; `Bound` means it is currently claimed by a PVC C. `Bound` means unclaimed D. `Available` means deleted

24. What does a `StatefulSet`'s `volumeClaimTemplates` field provide?
A. A single shared PVC for all replicas B. A unique, stable PVC automatically provisioned per replica ordinal C. No storage at all D. Only ConfigMap mounts

25. What is the purpose of a CSI "driver" versus a CSI "sidecar"?
A. They are the same component B. The driver implements storage-vendor-specific logic; sidecars (provisioner, attacher, etc.) are common Kubernetes-integration helpers around it C. Sidecars replace the driver entirely D. Neither is required for CSI

26. What is the purpose of `kubectl get pvc -o yaml` when diagnosing a stuck claim?
A. Deletes the PVC B. Reveals detailed status/conditions/events explaining why binding hasn't occurred C. Restarts the storage provisioner D. Grants RBAC to the PVC

27. What does node affinity's `requiredDuringSchedulingIgnoredDuringExecution` mean?
A. A soft preference only B. A hard scheduling requirement that is not re-evaluated/enforced after the Pod is already running C. Applies only after scheduling D. Has no effect on scheduling

28. What does `preferredDuringSchedulingIgnoredDuringExecution` mean for affinity rules?
A. A hard requirement B. A soft, best-effort preference the scheduler tries to satisfy but won't block scheduling over C. Blocks scheduling entirely if unmet D. Only applies to anti-affinity

29. What is the purpose of Pod Overhead accounting for certain runtimes (e.g., Kata Containers)?
A. Ignores runtime overhead entirely B. Accounts for the extra resource cost of the runtime sandbox itself, beyond the container's own requests C. Only applies to network overhead D. Only applies to storage overhead

30. What does a `RuntimeClass` object let you specify?
A. A Namespace's quota B. Which container runtime configuration (e.g., a sandboxed runtime like gVisor) a Pod should use C. A Service's load balancer type D. A PersistentVolume's reclaim policy

31. What is a common reason to use a sandboxed runtime like gVisor or Kata Containers?
A. To improve raw performance above all else B. To provide stronger workload isolation for untrusted or multi-tenant workloads C. To disable networking D. To bypass RBAC checks

32. What is the purpose of `kubectl auth can-i --list`?
A. Lists all cluster nodes B. Lists the actions the current user/ServiceAccount is permitted to perform C. Lists all Secrets in plaintext D. Lists all NetworkPolicies

33. What does a `ClusterRoleBinding` (as opposed to a `RoleBinding`) grant?
A. Namespace-scoped permissions only B. Cluster-wide permissions across all namespaces to the bound subject C. No permissions until also bound per-namespace D. Only node-level SSH access

34. What is the purpose of `kubectl create token <serviceaccount>`?
A. Deletes the ServiceAccount B. Requests a short-lived, bound authentication token for that ServiceAccount C. Grants cluster-admin permanently D. Rotates all cluster certificates

35. What does an `imagePullSecret` provide?
A. Encrypts the image at rest B. Supplies registry credentials so the kubelet can pull images from a private registry C. Grants RBAC permissions D. Defines a NetworkPolicy

36. What is the purpose of admission webhooks (validating/mutating)?
A. Only used for logging B. Allow custom validation or mutation logic to run against API requests during admission, beyond built-in controllers C. Replace the scheduler D. Replace etcd

37. What is a risk of a slow or unavailable validating admission webhook configured with `failurePolicy: Fail`?
A. No risk; requests always succeed B. It can block all matching API requests cluster-wide until the webhook responds or times out C. It only affects that one webhook's own Pod D. It automatically disables itself after one failure

38. What does "zero trust" networking philosophy assume by default?
A. All internal traffic is inherently trusted B. No implicit trust is granted based on network location alone; every request must be authenticated/authorized C. Only external traffic needs verification D. Firewalls alone are sufficient

39. What is the purpose of encrypting etcd data at rest?
A. Encrypts Pod-to-Pod traffic B. Protects sensitive data (e.g., Secrets) stored in etcd's on-disk files from being read if the underlying storage is compromised C. Replaces RBAC D. Replaces NetworkPolicy

40. What does a "break-glass" access procedure typically provide?
A. Permanent elevated access for daily use B. A tightly controlled, audited emergency-access path for exceptional situations, bypassing normal approval flow C. A way to disable all RBAC permanently D. A CI/CD deployment strategy

41. What is the purpose of a Prometheus "recording rule"?
A. Deletes old metrics B. Pre-computes and stores frequently-used or expensive query expressions as new time series for faster dashboards/alerts C. Defines RBAC scope D. Defines NetworkPolicy rules

42. What is the purpose of exemplars in modern metrics systems (linking metrics to traces)?
A. Replace logs entirely B. Let you jump from a metric spike directly to a specific representative trace for root-cause investigation C. Only used for billing D. Only used for RBAC audits

43. What does "SLO burn rate" measure?
A. CPU consumption rate B. How quickly an error budget is being consumed relative to its allotted period, used to drive alerting urgency C. Disk I/O rate D. Node join rate

44. What is the relationship between an SLI, SLO, and error budget?
A. They are unrelated concepts B. An SLI is the measured indicator; an SLO is the target threshold for that SLI; the error budget is the allowed margin of failure before breaching the SLO C. SLO measures raw uptime only D. Error budget is a billing term

45. What is the purpose of chaos engineering practices (e.g., Chaos Mesh, Litmus) in a Kubernetes context?
A. To intentionally cause production outages with no controls B. To proactively inject controlled failure (Pod kills, network delay) to validate resilience assumptions before real incidents C. To replace monitoring entirely D. To replace RBAC testing

46. What does "blast radius" refer to in incident/resilience discussions?
A. The physical size of a data center B. The scope of impact a given failure or compromise could cause C. The number of dashboards affected D. The number of log lines generated

47. What is the purpose of a feature flag system in progressive delivery?
A. Replaces GitOps entirely B. Decouples code deployment from feature exposure, allowing gradual or targeted enablement without a new deploy C. Only used for security patches D. Only used for database migrations

48. What does "config drift" between environments (e.g., staging vs. production) typically cause?
A. No practical impact B. Inconsistent behavior and hard-to-reproduce bugs, since environments no longer match their intended declared state C. Faster deployments D. Automatic self-healing

49. What is the purpose of a platform engineering "Internal Developer Platform" (IDP)?
A. Replaces Kubernetes entirely B. Provides self-service, golden-path tooling/abstractions so developers can deploy without needing deep infra expertise C. Only used for billing D. Only used for security scanning

50. What does DORA's "deployment frequency" metric measure?
A. Number of Pods running B. How often an organization successfully deploys to production C. Number of Namespaces D. Number of Nodes

51. What does DORA's "change failure rate" metric measure?
A. CPU utilization B. The percentage of deployments causing a failure in production requiring remediation C. Node failure rate D. DNS failure rate

52. What is the purpose of FinOps practices in a cloud native/Kubernetes context?
A. Replaces observability entirely B. Aligns engineering, finance, and business teams to optimize and make trade-offs around cloud cost C. Only applies to on-premises infrastructure D. Replaces RBAC

53. What is a common technique for reducing Kubernetes cluster cost via workload scheduling?
A. Disabling autoscaling entirely B. Bin-packing workloads efficiently and using spot/preemptible nodes for fault-tolerant workloads C. Running every Pod on a dedicated node D. Removing all resource limits

54. What does Crossplane primarily add to a Kubernetes control plane?
A. Only container runtime management B. The ability to provision and manage external cloud infrastructure (e.g., databases, buckets) via Kubernetes-native CRDs C. Only DNS resolution D. Only RBAC management

55. What is the purpose of Backstage (or similar developer portals) in platform engineering?
A. Replaces CI/CD pipelines entirely B. Provides a unified catalog and self-service UI for discovering services, templates, and documentation C. Only used for billing dashboards D. Only used for log storage

56. In continuous training (CT) MLOps pipelines, what triggers a model retrain?
A. Never; models are static once deployed B. Signals like data drift, performance degradation, or scheduled intervals C. Only manual requests D. Only Kubernetes version upgrades

57. What is the purpose of a feature store in MLOps?
A. Stores container images B. Provides a centralized, consistent source of engineered features for both training and serving C. Replaces the model registry D. Replaces GitOps

58. What is a key difference between online and offline model serving?
A. They are identical B. Online serving responds to real-time individual requests with low latency; offline (batch) serving processes large datasets on a schedule C. Offline serving is always faster D. Online serving never uses Kubernetes

59. What is the primary purpose of taking a full 5-exam mock sequence rather than just one?
A. Repetition alone guarantees passing B. It tracks genuine trend improvement across independent attempts, revealing whether weak domains are actually closing before the real exam C. Only the last exam's score matters D. Earlier exams should be ignored entirely

60. What should you do if Mock Exam 5's domain breakdown still shows one weak area 48-72 hours before the real exam?
A. Ignore it and take the exam anyway B. Concentrate remaining study time on that specific weak domain's source chapters before the exam C. Retake Mock Exam 5 immediately with no further review D. Postpone indefinitely with no plan

### Mock Exam 5 — Answer Key (Q1-60)

1-B, 2-B, 3-B, 4-B, 5-B, 6-B, 7-B, 8-B, 9-A, 10-B, 11-B, 12-B, 13-B, 14-B, 15-B, 16-B, 17-B, 18-B, 19-B, 20-B, 21-B, 22-B, 23-B, 24-B, 25-B, 26-B, 27-B, 28-B, 29-B, 30-B, 31-B, 32-B, 33-B, 34-B, 35-B, 36-B, 37-B, 38-B, 39-B, 40-B, 41-B, 42-B, 43-B, 44-B, 45-B, 46-B, 47-B, 48-B, 49-B, 50-B, 51-B, 52-B, 53-B, 54-B, 55-B, 56-B, 57-B, 58-B, 59-B, 60-B

---

## 15. Best Practices

- Take each mock exam in **one uninterrupted 90-minute sitting** — splitting it across multiple sessions defeats stamina/time-management calibration.
- Review **only missed questions'** explanations immediately after each exam — don't re-read questions you already got right.
- Track a **score-by-domain breakdown** for every exam attempt to see whether weak areas are improving between attempts.
- Take **Exam 5 as the final readiness gate**, ideally 48-72 hours before the real exam, leaving time to address any remaining weak domain.

---

## 16. Common Mistakes

- Taking a mock exam with notes or unlimited time, producing an inflated, unrealistic readiness signal.
- Re-reading correct answers extensively instead of focusing review time on missed questions.
- Taking all five mock exams back-to-back in one day without real review time between them.
- Treating a single high score on one exam as proof of full readiness, without checking domain-level consistency across multiple attempts.

---

## 17. Troubleshooting

| Symptom | Fix |
|---|---|
| Consistently scoring below 75% across exams | Return to full chapter review (Chapters 06-27) for the weakest-scoring domain before further mock exams |
| Running out of time before finishing 60 questions | Redrill Chapter 28's three-pass time-management strategy specifically |
| Score varies wildly between attempts | Likely inconsistent review discipline between exams — ensure missed-question review happens every time before the next attempt |

---

## 18. Memory Tricks

- **"Baseline, four checks, final gate."** — the five-exam structure (Section 14 table).
- **"Review misses only."** — the core post-exam discipline.

---

## 19-20. Scoring Guide

| Score | Interpretation |
|---|---|
| ≥ 90% | Strong readiness; focus remaining time on any single weak domain |
| 75-89% | Passing-range; target specific weak domains before the real exam |
| < 75% | Not yet exam-ready; return to full chapter review for weak domains before retaking |

---

## 21. Chapter Summary (One-Page Revision Sheet)

- Chapter 32 provides **five full, independent 60-question mock exams** (Mock Exams 1-5), each domain-weighted to mirror the real KCNA blueprint and each with its own complete answer key — no question reuse across exams.
- **Mock Exam 1** is the cold-baseline assessment; **Mock Exams 2-4** provide repeated independent practice at full exam length and difficulty; **Mock Exam 5** is the final readiness gate.
- Core discipline: **one uninterrupted 90-minute sitting per exam**, review only missed questions, track domain-level score trends across all five attempts, and use Exam 5 as the final go/no-go readiness gate 48-72 hours before the real exam.

---

### Chapter Completion Checklist

1. **Topics covered:** Five full, independent 60-question mock exams (Mock Exams 1-5), each with its own answer key, spanning all five KCNA domains at blueprint-matched weightings.
2. **KCNA objectives completed:** Meta-chapter — five full-length simulated assessments across all domains.
3. **Remaining objectives:** Interview Questions compilation (Chapter 33) — the final chapter.
4. **Suggested revision checklist:** Complete all five mock exams with a rising or stable score trend before the real exam date.
5. **Suggested hands-on exercises:** Take Mock Exam 1 (Section 13) today, cold, under full 90-minute exam conditions; then Exams 2-4 (Sections 14, 14A, 14B) on separate days; finish with Exam 5 (Section 14C) as the final readiness gate.
6. **Related chapters:** Previous: [31-Practice-Questions](../31-Practice-Questions/README.md). Next: [33-Interview-Questions](../33-Interview-Questions/README.md) — consolidated interview-style Q&A across all domains.
