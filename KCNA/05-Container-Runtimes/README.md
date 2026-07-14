# 05 — Container Runtimes

## 1. Learning Objectives

By the end of this chapter you will be able to:

- Explain what a container runtime actually does, distinguishing it from the image/build tooling covered in Chapter 04.
- Explain the difference between high-level and low-level runtimes.
- Explain the CRI (Container Runtime Interface) and why Kubernetes needed it.
- Name and compare the major runtimes: containerd, CRI-O, runc, and sandboxed alternatives (gVisor, Kata Containers).
- Understand why Dockershim was removed from Kubernetes and what replaced it — a very commonly tested, often-misunderstood historical event.

**KCNA objectives covered:** Container Orchestration domain — runtime architecture and the CRI are explicitly named in the official curriculum.

---

## 2. Historical Background

- **2015:** Docker, Inc. donated its runtime code to found the **OCI (Open Container Initiative)**, which produced two key specs: the **image-spec** (how images are structured — Chapter 04) and the **runtime-spec** (how a container is actually run: process creation, namespaces, cgroups). `runc` became the OCI's reference implementation of the runtime-spec.
- **2016:** Kubernetes introduced the **CRI (Container Runtime Interface)** — a plugin API so Kubernetes' kubelet could talk to *any* compliant container runtime, not just Docker. Before CRI existed, kubelet had Docker-specific code hardwired into it.
- **2016-2017:** **containerd** was extracted from Docker as a standalone, minimal daemon focused purely on running containers (pulling images, managing container lifecycle) — later donated to the CNCF.
- **2016:** **CRI-O** was created specifically to be a minimal, Kubernetes-native implementation of the CRI, with no extra features beyond what Kubernetes needs.
- **2020-2022:** Kubernetes announced deprecation and eventual removal of **Dockershim** (the compatibility shim that let kubelet talk to Docker Engine despite Docker not natively speaking CRI). Dockershim was fully removed in **Kubernetes 1.24 (2022)**. This caused significant community concern/confusion ("Kubernetes is dropping Docker support!") — but it's important to understand precisely what changed (Section 4.5).

**Why this matters:** This history explains *why* Kubernetes today talks to containerd or CRI-O directly rather than Docker Engine, and why that's actually a simplification, not a regression.

---

## 3. Motivation: Why Do We Need a Separate "Runtime" Concept At All?

**Analogy — The Restaurant Kitchen:**
Chapter 04 was about the **recipe and ingredients** (the image). This chapter is about the **kitchen staff who actually cook the meal** (the runtime). You can have the best recipe in the world, but someone still has to actually turn on the stove, combine the ingredients in the right order, and plate the food. That "someone" — the entity that actually creates namespaces, sets up cgroups, and starts the process — is the container runtime.

### 3.1 The Problem Before CRI Existed

In early Kubernetes, the kubelet (the per-node Kubernetes agent — full detail Chapter 08) had **Docker-specific code baked directly into it**. If you wanted Kubernetes to support a different runtime (say, rkt, or a future runtime), someone had to modify Kubernetes' own core codebase. This tightly coupled Kubernetes to one vendor's specific implementation — a classic case of **tight coupling limiting extensibility**.

### 3.2 How CRI Solves It

The **Container Runtime Interface (CRI)** defines a standard gRPC API that any runtime can implement. Kubernetes' kubelet now only needs to speak this one standard API — it doesn't care *which* runtime is underneath, as long as that runtime is CRI-compliant. This is the same "standardize the interface, let implementations vary" pattern you'll see repeated later with the CNI (Container Network Interface, Chapter 18) and CSI (Container Storage Interface, Chapter 19) — a core architectural theme of Kubernetes worth recognizing as a pattern, not memorizing three separate times.

```
Before CRI:                          After CRI:
┌─────────┐                          ┌─────────┐
│ kubelet   │                          │ kubelet   │
│ (Docker-  │                          │ (CRI       │
│  specific │                          │  client)   │
│  code)    │                          └─────────┘
└─────────┘                                │  CRI (gRPC)
     │ hardcoded                          ▼
     ▼                          ┌──────────────────┐
┌─────────┐                  │ Any CRI-compliant  │
│  Docker   │                  │ runtime: containerd,│
└─────────┘                  │ CRI-O, etc.          │
                              └──────────────────┘
```

---

## 4. Core Concepts

### 4.1 High-Level vs Low-Level Runtimes

This distinction is one of the most commonly confused (and tested) topics in this chapter.

**Low-level runtime:** Does the actual, literal work of creating namespaces, setting up cgroups, and executing the container process. It operates directly against the Linux kernel. Example: **runc** (the OCI reference implementation).

**High-level runtime:** Manages the broader container lifecycle — pulling images, managing storage, handling the CRI API, managing container metadata — and **delegates** the actual "create namespaces and run the process" work down to a low-level runtime underneath it. Examples: **containerd**, **CRI-O**.

**Analogy — The Restaurant, Continued:**
The high-level runtime is like the **head chef** who manages the whole kitchen: receiving orders (CRI API calls from kubelet), fetching ingredients from the pantry (pulling images), and deciding what needs cooking. The low-level runtime is like the **line cook** who does the literal, mechanical act of putting the pan on the stove and cooking (creating the namespaces/cgroups and exec'ing the process). The head chef doesn't personally touch every pan — they delegate that mechanical step to the line cook, every single time.

```
┌───────────────────────────────────────────────┐
│                     kubelet                       │
└───────────────────────────────────────────────┘
                      │ CRI (gRPC API)
                      ▼
┌───────────────────────────────────────────────┐
│      High-level runtime (containerd / CRI-O)      │
│  - Image pulling, storage, CRI API implementation │
└───────────────────────────────────────────────┘
                      │ OCI runtime-spec
                      ▼
┌───────────────────────────────────────────────┐
│         Low-level runtime (runc, etc.)             │
│  - Creates namespaces, cgroups, execs the process │
└───────────────────────────────────────────────┘
                      │
                      ▼
┌───────────────────────────────────────────────┐
│                  Linux Kernel                      │
└───────────────────────────────────────────────┘
```

### 4.2 containerd

**Definition:** A high-level, CNCF-graduated container runtime, originally extracted from Docker, focused specifically on container lifecycle management: image transfer/storage, container execution/supervision, and network attachment — implemented as a daemon (`containerd`) with a CRI plugin built in.

Used by default in most modern Kubernetes distributions (EKS, GKE, AKS, kubeadm-based clusters) since the Dockershim removal.

### 4.3 CRI-O

**Definition:** A high-level container runtime built **specifically and only** for Kubernetes, implementing exactly the CRI spec with no extra unrelated features. Originally created by Red Hat, and is the default runtime in OpenShift.

**containerd vs CRI-O — key distinction:** containerd is a general-purpose runtime usable outside Kubernetes too (it also powers plain `nerdctl`/Docker-adjacent workflows); CRI-O exists purely to satisfy Kubernetes' CRI, nothing more, nothing less — a deliberately minimal, single-purpose design.

### 4.4 runc and the OCI Runtime Spec

**Definition:** `runc` is the reference implementation of the OCI runtime-spec — a low-level command-line tool that takes a fully-prepared container "bundle" (config + root filesystem) and does the literal work: creating namespaces, configuring cgroups, and executing the container's process. Both containerd and CRI-O use `runc` (or an alternative low-level runtime) underneath by default.

### 4.5 Sandboxed / Alternative Low-Level Runtimes

For workloads needing stronger isolation than standard `runc` containers provide (recall Chapter 04, Section 4.2 — containers share the kernel, which is a weaker isolation boundary than VMs):

| Runtime | Approach | Isolation Level |
|---|---|---|
| `runc` (standard) | Direct namespaces/cgroups on the host kernel | Standard — shares host kernel |
| **gVisor** (`runsc`) | Intercepts syscalls in a user-space kernel proxy, sandboxing what the container can actually do to the real kernel | Stronger — extra syscall interception layer |
| **Kata Containers** | Runs each container inside a lightweight, dedicated micro-VM | Strongest — actual separate kernel per container, VM-level isolation |

**Why this matters:** This directly closes the "containers vs VMs security" gap from Chapter 04 — for genuinely hostile multi-tenant workloads, you can choose a runtime like Kata Containers to get VM-grade isolation while keeping a container-like developer experience (still scheduled by Kubernetes, still using OCI images).

### 4.6 The Dockershim Removal (Kubernetes 1.24) — What Actually Changed

This is one of the most misunderstood events in Kubernetes history, and it is exam-relevant.

**What people feared:** "Docker images won't work in Kubernetes anymore."

**What actually happened:** Dockershim was a *translation shim* inside kubelet that let it talk to Docker Engine (which does not natively implement CRI) as if it did. Kubernetes removed this shim to reduce maintenance burden and encourage direct use of CRI-native runtimes (containerd, CRI-O).

**What did NOT change:** Docker-built images are **OCI-compliant** (Section 2 — Docker helped create the OCI image-spec). Any OCI-compliant image, regardless of whether it was built with `docker build`, still runs perfectly fine on containerd or CRI-O. **Only the runtime *underneath* kubelet changed** — the images you build and push are completely unaffected.

**Exam-critical distinction:** "Docker the image-builder/CLI tool" (still totally fine to use) vs. "Docker Engine as a Kubernetes node's container runtime" (removed, replaced by direct containerd/CRI-O usage) are two entirely different things being conflated in that community panic.

---

## 5. Internal Working: Full Flow From kubelet to Running Process

```
1. kubelet decides a new container must start (instructed by the
   control plane — full detail in Chapter 07-08)
        ↓
2. kubelet calls the CRI gRPC API exposed by the high-level runtime
   (containerd or CRI-O) — "please run this container"
        ↓
3. High-level runtime pulls the required image layers if not cached
   (Chapter 04, Section 4.3)
        ↓
4. High-level runtime prepares an OCI-spec-compliant "bundle"
   (root filesystem + config.json describing namespaces, cgroups,
   mounts, etc.)
        ↓
5. High-level runtime invokes the low-level runtime (runc/gVisor/
   Kata), handing it the bundle
        ↓
6. Low-level runtime creates the actual namespaces and cgroups,
   mounts the OverlayFS root filesystem, and execs the container's
   entrypoint process
        ↓
7. Low-level runtime typically exits after starting the process;
   the high-level runtime keeps supervising/monitoring it going
   forward (restart policies, status reporting back to kubelet)
```

---

## 6. Architecture

```
┌──────────────────────────────────────────────────────────┐
│                          kubelet                              │
└──────────────────────────────────────────────────────────┘
                        │ CRI (gRPC)
                        ▼
┌──────────────────────────────────────────────────────────┐
│              High-Level Runtime (containerd / CRI-O)         │
│   Image management │ CRI API │ Storage │ Networking hooks    │
└──────────────────────────────────────────────────────────┘
                        │ OCI runtime-spec
                        ▼
┌──────────────────────────────────────────────────────────┐
│         Low-Level Runtime (runc / gVisor / Kata)              │
│   Namespaces, cgroups, process execution                      │
└──────────────────────────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────┐
│                     Linux Kernel / Hardware                    │
└──────────────────────────────────────────────────────────┘
```

---

## 7. Component Breakdown

| Component | Layer | Purpose | Failure Scenario |
|---|---|---|---|
| CRI | Interface/spec | Standard gRPC API between kubelet and any runtime | If a runtime isn't CRI-compliant, kubelet cannot use it at all |
| containerd | High-level runtime | Image pulls, container lifecycle, CRI implementation | Daemon crash prevents any new containers from starting on that node |
| CRI-O | High-level runtime | Kubernetes-only, minimal CRI implementation | Same failure mode as containerd, but scoped to Kubernetes use only |
| runc | Low-level runtime | Actually creates namespaces/cgroups, execs process | Bug here can affect container startup across every high-level runtime using it |
| gVisor / Kata | Alternative low-level runtimes | Stronger isolation for untrusted/multi-tenant workloads | Higher overhead/latency tradeoff versus standard runc |

---

## 8. Important Terminology

| Term | Meaning |
|---|---|
| CRI (Container Runtime Interface) | gRPC API standard letting kubelet use any compliant runtime |
| High-level runtime | Manages full container lifecycle, implements CRI, delegates execution |
| Low-level runtime | Does the literal namespace/cgroup/process creation work |
| OCI (Open Container Initiative) | Standards body defining image-spec and runtime-spec |
| runc | Reference low-level OCI runtime implementation |
| containerd | CNCF-graduated, general-purpose high-level runtime |
| CRI-O | Kubernetes-only, minimal high-level runtime |
| Dockershim | Removed compatibility layer that let kubelet use Docker Engine before CRI-native runtimes existed |
| gVisor | Sandboxed low-level runtime using a user-space kernel proxy |
| Kata Containers | Low-level runtime running each container in a lightweight micro-VM |

---

## 9. YAML Deep Dive

Runtime selection is configured at the **node/cluster level**, not typically per-Pod YAML — but Kubernetes does expose a `RuntimeClass` object for selecting alternative runtimes (like Kata/gVisor) on a per-Pod basis:

```yaml
# Preview — RuntimeClass lets a Pod request a specific low-level runtime
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  name: kata-containers
handler: kata     # maps to a runtime configured on the node

---
# Then a Pod can opt into it:
apiVersion: v1
kind: Pod
metadata:
  name: untrusted-workload
spec:
  runtimeClassName: kata-containers   # this Pod gets VM-level isolation
  containers:
  - name: app
    image: myapp:1.0
```

---

## 10. Commands

| Command | Purpose | Example |
|---|---|---|
| `crictl` | CRI-compatible CLI for debugging containers/images at the node level (runtime-agnostic) | `crictl ps` |
| `crictl images` | List images visible to the runtime | `crictl images` |
| `systemctl status containerd` | Check containerd daemon status on a node | `systemctl status containerd` |
| `ctr` | Low-level containerd-specific CLI (mostly for debugging, not daily use) | `ctr images ls` |

---

## 11. Hands-on Examples

**Lab 1 — Inspect the runtime a node is using:**
```bash
kubectl get nodes -o wide
# Look at the CONTAINER-RUNTIME column — e.g., containerd://1.7.0
```

**Lab 2 — Use crictl to inspect containers directly on a node (requires node access, e.g., via minikube ssh or kind exec):**
```bash
crictl ps
crictl inspect <container-id>
```

**Lab 3 — Conceptual exercise:** Draw the four-layer diagram from Section 6 from memory, labeling which box represents "the thing kubelet directly talks to via a standard API" versus "the thing that actually calls into the Linux kernel."

---

## 12. Internal Flow

See Section 5 for the complete kubelet → CRI → high-level runtime → low-level runtime → kernel flow.

---

## 13. Real-World Examples

1. **EKS, GKE, and AKS** all default to **containerd** as the node container runtime in current managed Kubernetes offerings.
2. **OpenShift** (Red Hat's Kubernetes distribution) defaults to **CRI-O**, reflecting its origins as a Red-Hat-driven, Kubernetes-only runtime project.
3. **Google's gVisor** is used internally at Google Cloud (e.g., for Cloud Run) to sandbox untrusted customer workloads with stronger isolation than standard containers.
4. **Kata Containers** is used by cloud providers and platform teams that need to run genuinely untrusted, multi-tenant code (e.g., CI/CD build workloads from external contributors) with VM-grade isolation while keeping Kubernetes-native scheduling.
5. **The Kubernetes 1.24 Dockershim removal** (2022) prompted major cloud providers and distros to proactively migrate their default node images to containerd well ahead of time, demonstrating how a CRI-level architectural decision cascades through the entire ecosystem.

---

## 14. Best Practices

- Use `crictl`, not `docker`, to debug container issues directly on Kubernetes nodes — `docker` may not even be installed on modern nodes, since it's no longer required.
- For genuinely untrusted or multi-tenant workloads, consider `RuntimeClass` with gVisor or Kata Containers instead of assuming standard `runc` isolation is sufficient.
- Understand that changing a node's underlying runtime (e.g., containerd to CRI-O) does not require rebuilding any of your OCI-compliant images.
- Keep runtime versions patched — vulnerabilities in the low-level runtime (namespace/cgroup handling) have historically been a real container-escape attack vector.

---

## 15. Common Mistakes

- Believing the Dockershim removal meant "Docker images stopped working in Kubernetes" — only the node-level runtime implementation changed; OCI images are unaffected.
- Confusing containerd/CRI-O (high-level) with runc (low-level) — they operate at different layers and are not interchangeable concepts.
- Assuming all containers get equal isolation strength — standard `runc` containers share the kernel; only alternative runtimes like Kata provide VM-grade separation.
- Forgetting that CRI is just an *interface* — multiple different runtimes can satisfy it, which is the entire point of its existence.

---

## 16. Troubleshooting

| Symptom | Possible Cause | Debugging Commands | Fix |
|---|---|---|---|
| Pods stuck in `ContainerCreating` | Runtime daemon (containerd/CRI-O) not running or misconfigured on the node | `systemctl status containerd`, `crictl info` | Restart/repair the runtime daemon |
| "Failed to pull image" at the node level | Registry auth issue, network problem, or runtime-level image store corruption | `crictl pull <image>` manually | Verify registry credentials/connectivity, clear corrupted image cache if needed |
| Node shows unexpected/old runtime version | Node image not updated after a cluster upgrade migrating away from Dockershim | `kubectl get nodes -o wide` | Upgrade/replace node images to a supported CRI-native runtime |

---

## 17. Comparison Tables

**containerd vs CRI-O:**

| Aspect | containerd | CRI-O |
|---|---|---|
| Scope | General-purpose, usable beyond Kubernetes | Kubernetes-only, minimal by design |
| Origin | Extracted from Docker | Built from scratch by Red Hat specifically for CRI |
| Common usage | Default in most managed Kubernetes (EKS, GKE, AKS) | Default in OpenShift |

**High-level vs low-level runtime:** see Section 4.1 table/diagram.

**runc vs gVisor vs Kata Containers:** see Section 4.5 table.

---

## 18. Memory Tricks

- **"CRI is the waiter, not the cook"** — it's the standard interface (order-taking protocol) between kubelet and whichever kitchen (runtime) is actually cooking.
- **"High-level manages, low-level executes."** Head chef vs. line cook (Section 4.1).
- **"Dockershim removal ≠ Docker images removed."** The shim was a translator for kubelet, not a requirement for image compatibility.
- **Isolation strength ladder:** runc (shares kernel) < gVisor (syscall sandboxing) < Kata (dedicated micro-VM per container) — increasing isolation, increasing overhead.

---

## 19. Interview Questions

**Easy:**
1. What is the difference between a high-level and a low-level container runtime?
   *Expected answer:* A high-level runtime (containerd, CRI-O) manages the broader container lifecycle — image pulling, storage, implementing the CRI API — and delegates the actual namespace/cgroup creation and process execution to a low-level runtime (runc) underneath it.

**Medium:**
2. What problem did the CRI (Container Runtime Interface) solve, and why was it introduced?
   *Expected answer:* Before CRI, kubelet had Docker-specific code hardcoded into it, tightly coupling Kubernetes to one runtime implementation. CRI introduced a standard gRPC API so kubelet could work with any compliant runtime, decoupling Kubernetes from any single vendor's implementation and allowing runtimes like containerd and CRI-O to be used interchangeably.

**Hard:**
3. Explain precisely what changed and what did NOT change when Kubernetes removed Dockershim in version 1.24, and why the community reaction ("Docker images won't work anymore") was a misunderstanding.
   *Expected answer:* Dockershim was a translation layer inside kubelet that allowed it to communicate with Docker Engine (which doesn't natively speak CRI) as though it did. Removing it meant kubelet could no longer talk to Docker Engine directly — nodes needed to run a CRI-native runtime like containerd or CRI-O instead. What did NOT change: container images built by Docker are OCI-compliant, and OCI-compliant images run identically on containerd/CRI-O. The confusion conflated "Docker Engine as a node's runtime" (removed) with "Docker as an image-building tool producing OCI images" (completely unaffected and still universally usable).

---

## 20. KCNA Practice Questions

**Q1.** What is the primary purpose of the Container Runtime Interface (CRI)?
A. To build container images from a Dockerfile
B. To provide a standard API so kubelet can work with any compliant container runtime
C. To replace the Linux kernel with a container-specific kernel
D. To manage Kubernetes Service networking

**Correct answer: B**
*Explanation:* CRI is a gRPC API standard decoupling kubelet from any single runtime implementation, allowing interchangeable use of containerd, CRI-O, or others. A describes a build tool's job (Chapter 04), C is not a real concept, and D describes kube-proxy/Services (Chapter 16).

---

**Q2.** Which of the following is an example of a low-level container runtime?
A. containerd
B. CRI-O
C. runc
D. kubelet

**Correct answer: C**
*Explanation:* `runc` is the OCI reference low-level runtime, directly responsible for creating namespaces/cgroups and executing the container process. containerd (A) and CRI-O (B) are high-level runtimes that delegate to a low-level runtime like runc. kubelet (D) is the Kubernetes node agent, an entirely different component (Chapter 08).

---

**Q3.** What actually happened when Kubernetes removed Dockershim in version 1.24?
A. Docker-built container images stopped being usable in Kubernetes entirely
B. Kubernetes removed the compatibility layer letting kubelet talk to Docker Engine directly; OCI-compliant images (including those built with Docker) remained fully usable via containerd/CRI-O
C. Kubernetes replaced YAML with a new configuration format
D. Kubernetes stopped supporting the OCI image specification

**Correct answer: B**
*Explanation:* Only the node-level runtime communication path changed — Dockershim's removal meant kubelet could no longer use Docker Engine directly, requiring a CRI-native runtime instead. Since Docker produces standard OCI images, those images continued working without any changes. A, C, and D are common but incorrect interpretations of this event.

---

**Q4.** Which runtime provides the strongest isolation by running each container inside a dedicated lightweight micro-VM?
A. runc
B. containerd
C. Kata Containers
D. CRI-O

**Correct answer: C**
*Explanation:* Kata Containers runs each container in its own lightweight VM, providing a separate kernel per container and the strongest isolation among the listed options. runc (A) shares the host kernel directly. containerd (B) and CRI-O (D) are high-level runtimes, not isolation mechanisms themselves.

---

**Q5.** Which organization/standard defines both the container image format and the container runtime specification used across the industry?
A. CNCF
B. OCI (Open Container Initiative)
C. IETF
D. W3C

**Correct answer: B**
*Explanation:* The OCI, founded in 2015 (with Docker's donated code as a starting point), defines the image-spec and runtime-spec that containerd, CRI-O, runc, and others all implement. The CNCF (A) hosts many cloud native projects (including containerd itself) but is not the body that defines these specific specs. IETF (C) and W3C (D) govern unrelated internet/web standards.

---

**Q6.** What is the main architectural difference between containerd and CRI-O?
A. containerd only runs on Windows; CRI-O only runs on Linux
B. containerd is a general-purpose runtime usable beyond Kubernetes, while CRI-O is built specifically and only for Kubernetes' CRI
C. CRI-O does not support pulling container images
D. containerd cannot be used with Kubernetes at all

**Correct answer: B**
*Explanation:* containerd was extracted from Docker and serves general container use cases beyond just Kubernetes, while CRI-O was purpose-built by Red Hat solely to satisfy the CRI with no additional scope. A is a false claim about OS support, C is false (CRI-O does pull images, just as part of implementing CRI), and D is false — containerd is in fact the default runtime for many managed Kubernetes offerings.

---

**Q7.** Why might a platform team choose gVisor or Kata Containers instead of the default runc for certain workloads?
A. To reduce container image size
B. To achieve stronger isolation for untrusted or multi-tenant workloads, at the cost of some performance overhead
C. To eliminate the need for a container registry
D. To bypass the CRI entirely

**Correct answer: B**
*Explanation:* gVisor and Kata Containers exist specifically to provide stronger isolation than standard runc containers (which share the host kernel), useful when running untrusted code from multiple tenants — at some performance cost due to the extra sandboxing/virtualization layer. A and C are unrelated concerns (Chapter 04's domain), and D is false — these alternatives still integrate through the CRI via RuntimeClass.

---

**Q8.** In the runtime architecture, what does the high-level runtime hand off to the low-level runtime?
A. A raw Dockerfile
B. An OCI-spec-compliant bundle (root filesystem plus configuration) describing how to run the container
C. A kubectl command
D. A DNS resolution request

**Correct answer: B**
*Explanation:* The high-level runtime prepares a bundle following the OCI runtime-spec (root filesystem + config.json) and passes it to the low-level runtime, which then performs the actual namespace/cgroup setup and process execution. A describes a build-time artifact (Chapter 04), C and D are unrelated to this handoff.

---

**Q9.** Which tool is the CRI-compatible command-line utility commonly used to debug containers directly on a Kubernetes node, regardless of which specific CRI runtime is installed?
A. docker
B. crictl
C. kubectl
D. helm

**Correct answer: B**
*Explanation:* `crictl` is specifically designed to work against any CRI-compliant runtime, making it the standard node-level debugging tool in modern Kubernetes. `docker` (A) may not even be installed on nodes post-Dockershim. `kubectl` (C) operates at the cluster API level, not directly against the node runtime. `helm` (D) is a package manager for Kubernetes applications, unrelated to runtime debugging.

---

**Q10.** A Pod needs to run genuinely untrusted third-party code with the strongest practical isolation while still being scheduled normally by Kubernetes. Which Kubernetes feature would be used to request this?
A. A Deployment with more replicas
B. A `RuntimeClass` specifying a sandboxed runtime like Kata Containers
C. A NetworkPolicy
D. A larger resource `limit` in the container spec

**Correct answer: B**
*Explanation:* `RuntimeClass` lets a specific Pod opt into an alternative low-level runtime (like Kata Containers or gVisor) for stronger isolation, while still being scheduled and managed like any other Kubernetes Pod. A (replica count) affects availability, not isolation. C (NetworkPolicy, Chapter 21) controls network traffic, not runtime isolation. D (resource limits) affects resource allocation via cgroups, not isolation boundary strength.

---

**Q11.** Why was CRI introduced instead of continuing to let kubelet call Docker Engine directly?
A. Docker Engine was discontinued
B. Hardcoding one runtime into kubelet tightly coupled Kubernetes to that vendor's implementation, blocking alternative runtimes
C. CRI made Kubernetes faster at scheduling Pods
D. CRI was required for Kubernetes to support Windows nodes

**Correct answer: B**
*Explanation:* Before CRI, kubelet had Docker-specific logic built in, meaning any alternative runtime would have needed its own kubelet fork or hacks. CRI's standard API let any compliant runtime plug in, ending that vendor lock-in. A is false (Docker Engine still exists), C and D are unrelated to CRI's actual motivation.

---

**Q12.** What does `crictl ps` show when run on a Kubernetes node?
A. A list of Kubernetes Deployments
B. A list of containers as seen directly by the CRI runtime, independent of which specific runtime is installed
C. A list of DNS records
D. A list of PersistentVolumes

**Correct answer: B**
*Explanation:* `crictl` talks directly to whichever CRI-compliant runtime is running on the node, showing containers at that lower level — useful for debugging when `kubectl` (which operates at the API-server/cluster level) doesn't show enough detail.

---

**Q13.** Which best describes the relationship between containerd and runc?
A. containerd is a low-level runtime that runc depends on
B. containerd is a high-level runtime that shells out to runc (a low-level runtime) to actually create and start containers
C. They are two names for the exact same component
D. runc manages image pulling while containerd only executes processes

**Correct answer: B**
*Explanation:* containerd handles the broader lifecycle (image management, storage, CRI API) and delegates the actual namespace/cgroup/process-execution work to runc — the standard high-level/low-level runtime split explained in this chapter.

---

**Q14.** A cluster administrator wants to run one specific untrusted workload with VM-level isolation while leaving all other workloads on the default runtime. What is the correct mechanism?
A. Set a global cluster-wide flag disabling runc entirely
B. Define a `RuntimeClass` for the sandboxed runtime and reference it only in that workload's Pod spec
C. Manually SSH into nodes and reconfigure containerd for all Pods
D. This is not possible; runtime choice is cluster-wide only

**Correct answer: B**
*Explanation:* `RuntimeClass` is designed for exactly this per-workload granularity — most Pods use the default runtime, while specific Pods opt into an alternative (e.g., Kata Containers) via `spec.runtimeClassName`, without affecting the rest of the cluster.

---

**Q15.** What is a key performance tradeoff of using gVisor compared to runc?
A. gVisor has no performance impact whatsoever
B. gVisor intercepts and mediates syscalls in user space for stronger isolation, which adds some overhead compared to runc's direct kernel access
C. gVisor eliminates the need for a kernel entirely
D. gVisor only works with Windows containers

**Correct answer: B**
*Explanation:* gVisor's user-space kernel intercepts syscalls to sandbox them, providing much stronger isolation than plain runc — but that interception layer adds latency/overhead compared to runc's direct pass-through to the host kernel.

---

**Q16.** Before Dockershim's removal, what specific problem did Dockershim solve for kubelet?
A. It provided GPU scheduling support
B. It translated between kubelet's CRI calls and Docker Engine's non-CRI-native API
C. It replaced etcd as the cluster's state store
D. It managed Ingress routing rules

**Correct answer: B**
*Explanation:* Docker Engine predates CRI and doesn't natively speak the CRI gRPC protocol, so Dockershim existed purely as a translation shim inside kubelet to bridge that gap — once CRI-native runtimes became standard, this shim was no longer needed and was removed.

---

**Q17.** Which of the following runtimes was purpose-built specifically and only to satisfy Kubernetes' CRI, with no broader general-purpose use case?
A. containerd
B. Docker Engine
C. CRI-O
D. runc

**Correct answer: C**
*Explanation:* CRI-O was designed from the outset solely to implement CRI for Kubernetes, with no ambition to serve non-Kubernetes use cases — unlike containerd (A), which serves broader container use cases, or Docker Engine (B), which predates and extends beyond Kubernetes entirely.

---

**Q18.** What does the OCI runtime-spec define, as distinct from the OCI image-spec?
A. How container images are tagged in a registry
B. How a bundle (root filesystem + configuration) should be structured so any compliant low-level runtime can execute it consistently
C. The format of Kubernetes YAML manifests
D. The gRPC methods used by CRI

**Correct answer: B**
*Explanation:* The runtime-spec standardizes how a runtime should consume a prepared bundle to actually launch a container, ensuring any OCI-compliant low-level runtime (runc, crun, etc.) behaves consistently — distinct from the image-spec (Chapter 04), which standardizes image layer/manifest format, and distinct from CRI (D), which is a separate gRPC-level standard.

---

**Q19.** Why is it inaccurate to say "Kubernetes no longer supports Docker" after Dockershim's removal?
A. Because Docker Engine can still be used as a CRI runtime with no changes
B. Because Docker-built OCI images remain fully compatible with CRI-native runtimes; only direct kubelet-to-Docker-Engine communication was removed
C. Because Dockershim was never actually removed
D. Because Kubernetes reintroduced Dockershim in a later release

**Correct answer: B**
*Explanation:* This is the precise, commonly-confused distinction: "Docker" as an image-building/development tool producing OCI images is entirely unaffected; only using Docker Engine itself as the node's CRI runtime was removed, since Docker Engine isn't CRI-native without the now-removed shim.

---

**Q20.** Which statement correctly ranks the isolation strength (weakest to strongest) of runc, gVisor, and Kata Containers?
A. Kata Containers < gVisor < runc
B. gVisor < runc < Kata Containers
C. runc < gVisor < Kata Containers
D. All three provide identical isolation strength

**Correct answer: C**
*Explanation:* runc shares the host kernel directly (weakest isolation among the three); gVisor adds a user-space syscall interception layer (stronger isolation, some overhead); Kata Containers runs each container in its own lightweight VM with a separate kernel (strongest isolation, most overhead) — the isolation ladder emphasized throughout this chapter.

---

## 21. Chapter Summary (One-Page Revision Sheet)

- The **OCI** defines two key specs: **image-spec** (Chapter 04) and **runtime-spec** (this chapter); `runc` is the OCI's reference low-level runtime implementation.
- **CRI (Container Runtime Interface)** is the standard gRPC API letting kubelet use any compliant runtime — decoupling Kubernetes from any single vendor's implementation, the same "standardized interface" pattern later reused by CNI (Ch. 18) and CSI (Ch. 19).
- **High-level runtimes** (containerd, CRI-O) manage image pulling, storage, and the CRI API, then **delegate** actual process/namespace/cgroup creation to a **low-level runtime** (runc, gVisor, Kata) underneath.
- **containerd** = general-purpose, extracted from Docker, default in most managed Kubernetes (EKS/GKE/AKS). **CRI-O** = Kubernetes-only, minimal, default in OpenShift.
- **Dockershim removal (Kubernetes 1.24, 2022):** only removed kubelet's Docker-Engine-specific translation layer — **OCI images (including Docker-built ones) are completely unaffected** and still run fine on containerd/CRI-O. A frequently misunderstood, frequently tested historical fact.
- **Isolation ladder:** `runc` (shares host kernel) < **gVisor** (user-space syscall sandbox) < **Kata Containers** (dedicated micro-VM per container) — selectable per-Pod via `RuntimeClass`.

---

### Chapter Completion Checklist

1. **Topics covered:** CRI motivation/history, high-level vs low-level runtimes, containerd, CRI-O, runc, gVisor, Kata Containers, Dockershim removal.
2. **KCNA objectives completed:** Container Orchestration domain — runtime architecture.
3. **Remaining objectives:** Full Kubernetes control plane and worker node architecture — Chapters 06-08.
4. **Suggested revision checklist:** Redraw the four-layer runtime architecture diagram from memory; explain the Dockershim removal correctly without conflating image compatibility with runtime compatibility; list which of containerd/CRI-O/runc/gVisor/Kata is high-level vs low-level.
5. **Suggested hands-on exercises:** Run `kubectl get nodes -o wide` on any available cluster (minikube/kind) and identify the CONTAINER-RUNTIME column; try `crictl ps` if node access is available.
6. **Related chapters:** Previous: [04-Containers](../04-Containers/README.md). Next: [06-Kubernetes-Architecture](../06-Kubernetes-Architecture/README.md) — introduces the full control plane and worker node picture, showing exactly where kubelet and the runtime from this chapter fit into the bigger Kubernetes system.
