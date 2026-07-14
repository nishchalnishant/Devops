# 02 — Linux Basics for Kubernetes

## 1. Learning Objectives

By the end of this chapter you will be able to:

- Explain why Kubernetes and containers are fundamentally Linux kernel technologies.
- Explain processes, the Linux filesystem hierarchy, and permissions well enough to reason about container behavior.
- Explain **namespaces** and **cgroups** — the two kernel features containers are built on (deep technical detail continues in Chapter 04).
- Read and reason about basic Linux commands you'll see inside troubleshooting scenarios and exam questions.
- Understand init systems and systemd, since `kubelet` itself runs as a systemd service on worker nodes.

**KCNA objectives covered:** Supports Container Orchestration and Kubernetes Fundamentals domains — Linux is the substrate everything else in this repo sits on. Not a heavily-weighted standalone domain, but foundational vocabulary appears throughout the exam.

---

## 2. Historical Background

Kubernetes doesn't run on some special "container operating system." It runs on plain Linux, using kernel features that have existed for years, wired together cleverly.

- **1960s–1970s:** Unix introduced the process model — the idea that a running program is a distinct, isolated unit of execution with its own memory, tracked by the kernel.
- **2002:** Linux introduced **namespaces**, starting with the mount namespace — a way to make a process see a different, isolated view of some system resource (starting with the filesystem).
- **2007:** Google contributed **cgroups** (control groups) to the Linux kernel — a way to limit and account for the resources (CPU, memory, I/O) a group of processes can use.
- **2008:** LXC (Linux Containers) combined namespaces + cgroups into the first practical "container" tooling, years before Docker existed.
- **2013:** Docker made containers easy and popular by wrapping LXC-like primitives (later its own `libcontainer`) with a friendly CLI, image format, and registry model.
- **2014+:** Kubernetes orchestrates these Linux-native containers across many machines.

**The critical exam-relevant insight:** Docker and Kubernetes did **not** invent process isolation. They packaged decades-old Linux kernel primitives into a usable product. Understanding namespaces and cgroups is understanding what a "container" *actually is* underneath the marketing term.

---

## 3. Motivation: Why Do You Need to Know Linux for a Kubernetes Exam?

Because every Kubernetes worker node **is a Linux machine**, every Pod **is Linux processes**, every container image **is a Linux filesystem layout**, and the `kubelet` that manages Pods **is a Linux systemd service**.

If someone asks "why does a container use so little memory to boot compared to a VM," the honest answer is entirely a Linux kernel answer — there is no "Kubernetes magic," only "Linux namespaces + cgroups, cleverly orchestrated."

**Analogy — The Apartment Building (revisited from Chapter 01):**
Recall containers are like desks in a shared coworking space, all sharing the building's plumbing/electricity (the host's Linux kernel). This chapter explains **how a single kernel can make each desk feel like a private room** — that trick is namespaces (each desk gets its own *view* of the world) and cgroups (each desk gets a strict *budget* of shared resources it isn't allowed to exceed).

---

## 4. Core Concepts (From Absolute Beginner Level)

### 4.1 What Is a Process?

**Definition:** A process is a running instance of a program — code loaded into memory, with its own execution state, tracked by the kernel via a unique **Process ID (PID)**.

**Analogy — The Library:**
A program on disk (like `/usr/bin/nginx`) is like a **recipe book sitting on a library shelf** — inert, not doing anything. A process is what happens when someone actually **checks out the book and starts cooking from it** — an active, running instance, with its own state (what step they're on, what ingredients they're using).

Every process has:

| Attribute | Meaning |
|---|---|
| PID | Unique numeric identifier for the process |
| PPID | Parent Process ID — the process that created it |
| UID/GID | User/Group ID the process runs as (determines permissions) |
| State | Running, Sleeping, Stopped, Zombie, etc. |
| File descriptors | Open files, sockets, pipes the process is using |

**PID 1** is special: it's the very first process the kernel starts at boot, and it becomes the ancestor of every other process. On a normal Linux machine this is usually `systemd`. **Inside a container, PID 1 is whatever process the container was started with** (often your application itself) — this matters because PID 1 has special signal-handling responsibilities (it must reap "zombie" child processes; if your containerized app ignores signals like `SIGTERM`, `kubectl delete pod` can hang until a timeout).

### 4.2 The Linux Filesystem Hierarchy

Everything in Linux is represented as a file, organized in a single tree starting at `/` (root) — unlike Windows' `C:\`, `D:\` drive letters.

| Path | Purpose |
|---|---|
| `/bin`, `/usr/bin` | Executable programs |
| `/etc` | Configuration files |
| `/var` | Variable data — logs, caches, runtime state (`/var/log`, `/var/lib`) |
| `/home` | User home directories |
| `/proc` | A **virtual** filesystem exposing live kernel/process info (not real files on disk — generated on the fly) |
| `/sys` | A **virtual** filesystem exposing kernel/device/cgroup info |
| `/tmp` | Temporary files, often cleared on reboot |
| `/dev` | Device files (e.g., `/dev/null`, `/dev/sda`) |

**Why `/proc` and `/sys` matter for Kubernetes:** cgroups are configured and inspected through **files under `/sys/fs/cgroup`**. When `kubelet` enforces a container's CPU/memory limits, it's ultimately writing numbers into cgroup files under `/sys`. This isn't abstract — it's literally text files with numbers in them.

### 4.3 Users, Groups, and Permissions

Every file has an owner (user), a group, and a set of permissions for three categories: **owner**, **group**, and **others**. Each category can have **r**ead, **w**rite, and e**x**ecute permissions.

```
-rwxr-xr--  1 alice  developers  1024  Jan 10  app.sh
 │└┬┘└┬┘└┬┘
 │ │  │  └── others: r-- (read only)
 │ │  └───── group:  r-x (read + execute)
 │ └──────── owner:  rwx (read + write + execute)
 └────────── file type: - (regular file), d (directory), l (symlink)
```

Numeric (octal) shorthand: r=4, w=2, x=1. So `rwxr-xr--` = owner 7, group 5, other 4 → `754`.

**Why this matters for Kubernetes/exam:** Pod Security concepts (Chapter 21) — like running containers as a non-root user, or setting a `runAsUser`/`fsGroup` in a Pod's `securityContext` — are directly built on this exact Linux permission model. A container "running as root" means UID 0 inside that container's namespace, which is a real Linux security concern (if a container escapes its isolation, UID 0 has full power on the host).

### 4.4 Linux Namespaces — The Isolation Mechanism

**Definition:** A namespace is a Linux kernel feature that wraps a global system resource in an abstraction, so that processes within a namespace see what looks like their own isolated instance of that resource, while processes outside cannot see or affect it.

**Analogy — Hotel Room Numbering:**
Imagine a hotel where every room, if you're inside it, believes it is "Room 1" — the room number itself is relative to who's asking. Person in room 204 sees "Room 1" on their door; person in room 517 also sees "Room 1" on theirs. They're not conflicting because each person's *view* is isolated, even though the hotel (the kernel) knows the true global room numbers. This is exactly what a **PID namespace** does: a process might be PID 47 on the actual host, but *inside its own PID namespace*, it sees itself as PID 1.

**The 7 (KCNA-relevant) Linux namespace types:**

| Namespace | Isolates | Container Effect |
|---|---|---|
| PID | Process IDs | Container sees only its own processes, starting from PID 1 |
| Network (net) | Network interfaces, IP addresses, ports, routing tables | Container gets its own virtual network stack (its own "eth0," IP, routes) |
| Mount (mnt) | Filesystem mount points | Container sees its own root filesystem, unaware of the host's real filesystem |
| UTS | Hostname and domain name | Container can have its own hostname, independent of the host machine's hostname |
| IPC | Inter-process communication (shared memory, semaphores, message queues) | Container's IPC mechanisms isolated from host and other containers |
| User | User and group IDs | A process can be "root" (UID 0) inside its namespace but map to an unprivileged UID on the host (rootless containers) |
| Cgroup | View of the cgroup hierarchy itself | Container sees a cgroup root scoped to itself, not the whole host's cgroup tree |

**Crucially — a Kubernetes Pod is built by sharing SOME of these namespaces across containers.** All containers in the same Pod share the same **network namespace** (hence "same IP address, must coordinate ports") and often the same **IPC namespace**, but typically get **separate mount namespaces** (each container has its own filesystem/image). This single fact — "Pods share network namespace, not mount namespace, across their containers" — is one of the most important underlying truths behind Chapter 10 (Pods) and is frequently the basis for exam questions phrased as "why do containers in the same Pod share an IP address?"

### 4.5 Control Groups (cgroups) — The Resource-Limiting Mechanism

**Definition:** cgroups are a Linux kernel feature that limits, accounts for, and isolates the resource usage (CPU, memory, disk I/O, network bandwidth) of a group of processes.

**Analogy — The Electricity Meter and Circuit Breaker:**
Namespaces are about *what you can see*. Cgroups are about *how much you're allowed to use*. Think of cgroups as the **circuit breaker box** in an apartment building: each apartment (container) is wired to a breaker that trips if it tries to draw more electricity (CPU/memory) than its contracted limit — even though electricity itself (the physical resource) is shared infrastructure from the whole building (the host kernel).

**Two cgroup versions matter for the exam:**

| Version | Key trait |
|---|---|
| cgroups v1 | Older, one hierarchy per resource controller (separate trees for CPU, memory, etc.) |
| cgroups v2 | Newer, unified single hierarchy, adopted as default by modern Linux distros and required by newer Kubernetes versions for full feature support |

**What Kubernetes maps onto cgroups:** When you set a Pod's container `resources.requests` and `resources.limits` (CPU/memory) — covered fully in Chapter 20 (Scheduling) — the `kubelet`, via the container runtime, ultimately configures cgroup limits on the underlying Linux processes. A Pod's "CPU limit of 500m" is not a Kubernetes-invented enforcement mechanism; it becomes a real cgroup CPU quota file on the host.

### 4.6 Union/Overlay Filesystems (Preview — full detail in Chapter 04)

Container images are built from **layers**. Linux supports this through **union filesystems** (most commonly **OverlayFS** today), which let multiple filesystem layers be stacked and presented as one merged view, with a writable layer on top. This is *also* a Linux kernel feature, not a Docker invention — Docker just popularized using it for image layering.

### 4.7 Init Systems and systemd

**Definition:** An init system is the first process (PID 1) started by the Linux kernel at boot, responsible for starting and supervising all other system services.

Historically, Linux used simple sequential init scripts (SysV init). Modern distributions use **systemd**, which starts services in parallel where possible, tracks dependencies between them, and can automatically restart failed services.

**Why this matters for Kubernetes:** On every Kubernetes node, the `kubelet` (the agent that manages Pods on that node — full detail in Chapter 08) itself runs as **a systemd-managed service**. If `kubelet` crashes, systemd is what restarts it. So there are actually **two layers of "self-healing"** in a Kubernetes cluster: systemd keeps `kubelet` alive on each node, and `kubelet`/the control plane keeps your Pods alive on top of that. Common troubleshooting command: `systemctl status kubelet` and `journalctl -u kubelet` — these appear in real troubleshooting scenarios and occasionally in exam-style questions about diagnosing node problems.

---

## 5. Internal Working: How a "Container" Actually Starts (Step by Step)

This is the real sequence of kernel-level events that happens when a container runtime (Chapter 05) starts a container — understanding this demystifies the entire stack above it.

```
1. Container runtime reads the image (layered filesystem, via OverlayFS)
        ↓
2. Runtime calls Linux kernel syscalls: clone() with namespace flags
   (CLONE_NEWPID, CLONE_NEWNET, CLONE_NEWNS, CLONE_NEWUTS, CLONE_NEWIPC, CLONE_NEWUSER)
        ↓
3. Kernel creates a new process that has its OWN isolated view of:
   process tree, network stack, mounted filesystem, hostname, IPC, and UID mapping
        ↓
4. Runtime creates a cgroup for the process, writing resource limits
   (e.g., memory.max, cpu.max) into files under /sys/fs/cgroup/...
        ↓
5. Runtime mounts the merged OverlayFS root filesystem as the
   container's root (via the mount namespace, invisible to the host's real root)
        ↓
6. Kernel executes the container's entrypoint process as PID 1
   (within its own PID namespace — but it has a different, real PID on the host)
        ↓
7. The "container" is now just an ordinary Linux process, isolated by
   namespaces and constrained by cgroups — nothing more exotic than that
```

The exam-relevant takeaway sentence: **"A container is just a regular Linux process with restricted visibility (namespaces) and restricted resource usage (cgroups)."** There is no separate "container kernel" — it's the same kernel as the host, the whole time.

---

## 6. Architecture

```
┌───────────────────────────────────────────────────────────┐
│                     Linux Kernel (single, shared)           │
│                                                               │
│   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐       │
│   │  Namespaces  │   │   cgroups    │   │  OverlayFS   │       │
│   │ (WHAT you    │   │ (HOW MUCH    │   │ (image layer │       │
│   │  can see)    │   │  you can use)│   │  stacking)   │       │
│   └──────┬───────┘   └──────┬───────┘   └──────┬───────┘       │
│          └──────────────────┼──────────────────┘                │
│                             ▼                                   │
│                  "Container" = isolated,                        │
│                   resource-limited Linux process                │
└───────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴────────────────┐
              ▼                                ▼
      ┌───────────────┐               ┌────────────────┐
      │  Container A   │               │  Container B    │
      │ (PID ns, net ns│               │ (own PID ns,    │
      │  mnt ns, etc.) │               │  own mnt ns)    │
      └───────────────┘               └────────────────┘
              (if in the SAME Pod, both share the SAME network namespace)
```

---

## 7. Component Breakdown

| Component | Purpose | Failure Scenario | Common Mistake |
|---|---|---|---|
| PID namespace | Process isolation, own PID 1 per container | If PID 1 doesn't handle SIGTERM, `kubectl delete pod` hangs until forced kill | Running a shell script as PID 1 that doesn't forward signals to child processes |
| Network namespace | Own IP/interfaces per Pod | Misconfigured CNI can leave Pods without connectivity | Assuming each *container* (not each Pod) gets a separate IP — it's per-Pod, not per-container |
| Mount namespace | Isolated filesystem view | Wrong volume mounts cause containers to see unexpected/missing files | Confusing `hostPath` volumes (deliberately breaking mount isolation) with normal isolated mounts |
| cgroups | Resource limiting/accounting | No limits set → one container can starve others of CPU/memory on the same node ("noisy neighbor") | Not setting `resources.limits`, assuming Kubernetes enforces fairness automatically without config |
| systemd | Supervises `kubelet` and other node services | If systemd fails to restart a crashed `kubelet`, the node stops reporting status (`NotReady`) | Forgetting to check `systemctl status kubelet` / `journalctl -u kubelet` when a node misbehaves |
| OverlayFS | Layered image filesystem | Disk pressure from too many unused image layers | Not cleaning up unused images (`docker/crictl image prune`), causing node disk pressure evictions |

---

## 8. Important Terminology

| Term | Meaning | Why Important |
|---|---|---|
| Process | A running instance of a program, tracked by PID | Base unit containers are built from |
| PID 1 | The first process in a PID namespace (or on the whole machine) | Special signal-handling responsibilities; relevant to container shutdown behavior |
| Namespace | Kernel feature isolating a process's *view* of a resource | Foundation of container isolation |
| cgroup | Kernel feature limiting/accounting a process group's *resource usage* | Foundation of container resource limits/requests |
| UID/GID | Numeric user/group identity | Basis of container security context and root vs non-root risk |
| OverlayFS | Union filesystem merging read-only image layers with a writable layer | Basis of container image layering |
| systemd | Modern Linux init system, PID 1 on the host, manages services | Manages `kubelet` itself on every node |
| `/proc`, `/sys` | Virtual filesystems exposing live kernel/process/cgroup state | Where resource limits and process info actually live as files |
| Rootless containers | Containers run without real root privileges, using user namespaces to map a container's "root" to an unprivileged host user | Security best practice, reduces blast radius of container escape |

---

## 9. YAML Deep Dive

Not yet applicable — no Kubernetes objects introduced. However, it's worth previewing the field that maps directly onto this chapter's concepts, since you'll meet it formally in Chapter 21 (Security):

```yaml
securityContext:
  runAsNonRoot: true       # Refuses to start the container if it would run as UID 0 (root)
  runAsUser: 1000          # Sets the specific UID (Linux concept from Section 4.3)
  fsGroup: 2000            # Sets the GID applied to mounted volumes
```

Every one of these fields is a direct pass-through configuration of the Linux user/group and namespace concepts from Section 4.3 and 4.4 — Kubernetes doesn't invent new security primitives here, it configures Linux's existing ones.

---

## 10. kubectl Commands

Not yet introduced (Chapter 06+). This chapter's "commands" are plain Linux commands you should be comfortable with before or alongside learning `kubectl`:

| Command | Purpose | Example |
|---|---|---|
| `ps aux` | List all running processes | `ps aux \| grep nginx` |
| `top` / `htop` | Live view of process resource usage | `top` |
| `ls -l` | List files with permissions | `ls -l /etc` |
| `chmod` | Change file permissions | `chmod 750 app.sh` |
| `chown` | Change file owner/group | `chown alice:developers app.sh` |
| `cat /proc/[pid]/status` | Inspect a specific process's live kernel info | `cat /proc/1/status` |
| `systemctl status <service>` | Check a systemd service's status | `systemctl status kubelet` |
| `journalctl -u <service>` | View a systemd service's logs | `journalctl -u kubelet -f` |
| `mount` | List or create filesystem mounts | `mount \| grep overlay` |
| `cat /sys/fs/cgroup/...` | Inspect live cgroup limits | `cat /sys/fs/cgroup/memory.max` |

---

## 11. Hands-on Examples

**Lab 1 — See PID namespace isolation yourself (requires Docker):**
```bash
docker run --rm -it alpine sh
# Inside the container:
ps aux
# Notice your shell is PID 1 INSIDE the container
```
Then, from a separate terminal on the host:
```bash
docker inspect --format '{{.State.Pid}}' <container_id>
# This prints the REAL host PID — a different, larger number
```
This proves the "same process, different PID depending on which namespace you're viewing from" concept from Section 4.4.

**Lab 2 — See cgroup limits as literal files:**
```bash
docker run --rm -it --memory="100m" alpine sh
cat /sys/fs/cgroup/memory.max   # (cgroups v2) or memory.limit_in_bytes (v1)
```
You'll see the number `104857600` (100 MB in bytes) — proof that "resource limits" are just numbers written into kernel-exposed files.

**Lab 3 — Watch systemd manage kubelet (requires a real or local cluster node, e.g., via minikube --driver=none on Linux, or any Linux VM with kubelet installed):**
```bash
systemctl status kubelet
journalctl -u kubelet --since "10 minutes ago"
```

---

## 12. Internal Flow

```
docker run --memory=100m --name myapp alpine sleep 3600
        ↓
Runtime parses the request
        ↓
clone() syscall creates new namespaces (PID, net, mnt, UTS, IPC)
        ↓
cgroup created, memory.max written = 104857600
        ↓
OverlayFS root mounted from alpine image layers
        ↓
sleep process executed as PID 1 (inside its new PID namespace)
        ↓
Host sees this as an ordinary process with a real host PID,
just wrapped in restricted namespaces + a cgroup
```

---

## 13. Real-World Examples

1. **Kubernetes' own `kubelet`** runs as a systemd unit on every node — if it crashes, systemd restarts it automatically, which is why `systemctl status kubelet` is one of the first commands any Kubernetes operator runs when a node goes `NotReady`.
2. **"Noisy neighbor" incidents** at companies running shared Kubernetes clusters are almost always a cgroups story: a team forgot to set `resources.limits`, and their Pod consumed unbounded CPU/memory, starving other teams' Pods on the same node.
3. **Rootless container adoption** (e.g., Podman's rootless mode, gVisor, Kata Containers) is a direct response to security concerns about containers running as real root — using Linux user namespaces to map a container's root to an unprivileged host UID.
4. **Disk pressure node evictions** in production clusters are frequently caused by unused OverlayFS image layers piling up on a node's disk, eventually triggering `kubelet`'s disk-pressure eviction logic (Chapter 20).
5. **Distroless/minimal container images** (e.g., Google's `distroless` images) are popular precisely because a smaller root filesystem (fewer OverlayFS layers, fewer binaries) reduces attack surface — since anything present in the image is reachable if a container is compromised.

---

## 14. Best Practices

- Always set `resources.requests` and `resources.limits` on containers — this is literally how you configure cgroups through Kubernetes; skipping it invites noisy-neighbor problems.
- Avoid running containers as root (UID 0) unless absolutely necessary; use `runAsNonRoot: true` and specific `runAsUser` values.
- Design your container's entrypoint (PID 1) to properly handle and forward signals (`SIGTERM`), or use an init wrapper like `tini`, so Pod termination is fast and clean instead of waiting for the grace period timeout.
- Regularly prune unused images on nodes to avoid OverlayFS-related disk pressure.
- Use `journalctl -u kubelet` as a first-line diagnostic whenever a node reports `NotReady` — the problem is often below Kubernetes, at the systemd/OS layer.

---

## 15. Common Mistakes

- Believing containers run a different, special "container kernel" — they share the exact same Linux kernel as the host.
- Assuming each *container* gets its own IP address — in Kubernetes, the **Pod** gets the IP, because all containers in a Pod share one network namespace.
- Forgetting that PID 1 inside a container has special signal-handling duties, leading to slow/ungraceful shutdowns.
- Treating resource "requests/limits" as a Kubernetes-only abstraction rather than understanding they translate directly into Linux cgroup configuration.
- Confusing cgroups (resource limiting) with namespaces (visibility isolation) — they solve different problems and both are required to make a "container."

---

## 16. Troubleshooting

| Symptom | Possible Cause | Debugging Commands | Fix |
|---|---|---|---|
| Node shows `NotReady` | `kubelet` crashed or not running | `systemctl status kubelet`, `journalctl -u kubelet` | Restart/fix `kubelet`, check its config |
| Pod OOMKilled | cgroup memory limit exceeded | `kubectl describe pod`, check `resources.limits.memory` | Raise the memory limit or fix the app's memory usage |
| Pod shutdown takes exactly the grace period every time | PID 1 not handling SIGTERM | Check the container's entrypoint/signal handling | Use an init process like `tini`, or handle signals in the app |
| Node has disk pressure | Too many unused image layers (OverlayFS) filling disk | `df -h`, `crictl images`, `journalctl` for eviction events | Prune unused images, increase disk, or set image GC thresholds |
| One Pod starves others on the same node | Missing `resources.limits` | `kubectl top pod`, `kubectl describe node` | Set explicit CPU/memory limits |

---

## 17. Comparison Tables

**Namespaces vs cgroups:**

| Aspect | Namespaces | cgroups |
|---|---|---|
| Purpose | Isolate what a process can *see* | Limit/account for what a process can *use* |
| Analogy | Hotel room numbering (relative view) | Circuit breaker (usage cap) |
| Example | PID namespace hides other processes | Memory cgroup caps RAM usage |
| Kubernetes mapping | Pod network namespace sharing | `resources.requests` / `resources.limits` |

**cgroups v1 vs v2:**

| Aspect | v1 | v2 |
|---|---|---|
| Hierarchy | Separate tree per controller | Single unified tree |
| Adoption | Older, legacy | Default on modern distros; required for some newer K8s features |

---

## 18. Memory Tricks

- **"Namespaces = What you SEE, cgroups = What you GET."** Rhyme it to keep the two straight instantly.
- **PID 1 = "The Responsible Adult."** It must clean up after its children (reap zombies) and respond properly when told to leave (SIGTERM) — a lazy PID 1 makes the whole household (Pod) slow to shut down.
- **"A container is a process wearing a namespace costume, on a cgroup diet."**

---

## 19. Interview Questions

**Easy:**
1. What are the two main Linux kernel features that make containers possible?
   *Expected answer:* Namespaces (isolate what a process can see: PID, network, mounts, etc.) and cgroups (limit/account for resource usage like CPU and memory).

**Medium:**
2. Why do all containers within the same Kubernetes Pod share the same IP address?
   *Expected answer:* Because all containers in a Pod share the same network namespace — the Pod, not the individual container, is the unit that gets a network identity.

**Hard:**
3. A container's application takes a full 30 seconds to terminate every time a Pod is deleted, hitting Kubernetes' default grace period. Using Linux process concepts, explain the likely root cause and fix.
   *Expected answer:* The application is likely running as PID 1 and not properly handling/forwarding the SIGTERM signal Kubernetes sends on deletion, so Kubernetes waits out the full terminationGracePeriodSeconds before sending SIGKILL. Fix: ensure the app handles SIGTERM directly, or wrap it with a minimal init process (like `tini`) that correctly forwards signals and reaps zombie processes.

---

## 20. KCNA Practice Questions

**Q1.** Which two Linux kernel features are primarily responsible for making "containers" possible?
A. Hypervisors and virtual disks
B. Namespaces and cgroups
C. Systemd and GRUB
D. SELinux and AppArmor only

**Correct answer: B**
*Explanation:* Namespaces provide isolation (what a process can see), and cgroups provide resource limiting (what a process can use) — together these two kernel features are the actual technical foundation of containers. A describes VM technology, not containers. C and D name real Linux subsystems, but they are not the core mechanism containers are built from.

---

**Q2.** Inside a container, a process appears as PID 1. On the host machine, what is true about this same process?
A. It does not actually exist on the host
B. It has a different, real PID as seen from the host's own PID namespace
C. It is always PID 1 on the host as well
D. It runs in a separate kernel from the host

**Correct answer: B**
*Explanation:* PID namespaces give a relative view — the same physical process can be PID 1 inside its own namespace, while having an entirely different real PID visible from the host. C is the classic misconception this chapter corrects. D is false; there's only one shared kernel.

---

**Q3.** Which Linux kernel feature is directly responsible for enforcing a Kubernetes Pod's `resources.limits.memory` setting?
A. Namespaces
B. cgroups
C. OverlayFS
D. systemd

**Correct answer: B**
*Explanation:* cgroups (control groups) are the kernel mechanism for limiting and accounting for resource usage like memory and CPU. Namespaces (A) handle visibility, not resource limits. OverlayFS (C) handles image layering. systemd (D) is an init system managing services like kubelet, unrelated to per-container resource enforcement.

---

**Q4.** Why do all containers within a single Kubernetes Pod share the same IP address?
A. Kubernetes assigns IPs randomly to any container
B. All containers in a Pod share the same network namespace
C. Containers do not have IP addresses, only Nodes do
D. Each container gets its own IP, but they are always identical by coincidence

**Correct answer: B**
*Explanation:* Sharing the network namespace is precisely what makes containers within a Pod share one IP, one set of ports, and one network interface view. C is false — Pods do have IPs. D is a nonsensical distractor.

---

**Q5.** What is the role of systemd in relation to `kubelet` on a Kubernetes worker node?
A. systemd replaces the need for kubelet entirely
B. systemd is a container runtime used to run Pods
C. systemd manages kubelet as a supervised service, restarting it if it crashes
D. systemd is only used for network namespace creation

**Correct answer: C**
*Explanation:* kubelet runs as a systemd-managed service on the node; if it crashes, systemd is responsible for restarting it, providing a layer of self-healing below Kubernetes' own Pod-level self-healing. A, B, and D misattribute systemd's actual role.

---

**Q6.** What is the main risk of running a container as root (UID 0) without additional isolation like user namespace remapping?
A. The container will run slower
B. If the container is compromised or escapes isolation, the attacker may have root-level privileges on the host
C. Root containers cannot access the network
D. There is no risk; root inside a container is identical to root nowhere else

**Correct answer: B**
*Explanation:* Because containers share the host kernel, a container running as UID 0 that escapes its namespace isolation could exercise real root privileges on the host — this is why `runAsNonRoot` and rootless container techniques exist as security best practices.

---

**Q7.** What Linux feature allows container images to be built from stacked, reusable layers with one writable layer on top?
A. cgroups
B. PID namespace
C. OverlayFS (a union filesystem)
D. systemd

**Correct answer: C**
*Explanation:* Union/overlay filesystems (like OverlayFS) merge multiple read-only layers plus a writable layer into a single presented filesystem view — this is the real mechanism behind container image layering, independent of any specific container tool.

---

**Q8.** A node in a Kubernetes cluster reports status `NotReady`. What is a reasonable first Linux-level diagnostic step?
A. Delete the node object immediately
B. Check `systemctl status kubelet` and `journalctl -u kubelet` on that node
C. Re-image the entire cluster
D. Increase the Pod's memory limit

**Correct answer: B**
*Explanation:* Since kubelet runs as a systemd service, checking its systemd status and logs is the standard first diagnostic step for a `NotReady` node — the root cause is often below Kubernetes, at the OS/process level. A, C, and D are drastic or irrelevant actions for this symptom.

---

**Q9.** What is the primary difference between cgroups v1 and cgroups v2?
A. v1 supports containers, v2 does not
B. v1 uses separate hierarchies per resource controller; v2 uses one unified hierarchy
C. v2 is only used for networking
D. There is no meaningful difference

**Correct answer: B**
*Explanation:* This is the key structural distinction tested. cgroups v1 has separate trees per controller (CPU, memory, etc.), while v2 unifies everything into a single hierarchy, and is now the default on modern Linux distributions.

---

**Q10.** Which best explains why a container's shutdown might take the full termination grace period every time it's deleted?
A. Kubernetes always waits the full grace period regardless of application behavior
B. The container's PID 1 process is not properly handling or forwarding the SIGTERM signal
C. The node is out of disk space
D. The container has no network namespace

**Correct answer: B**
*Explanation:* If PID 1 ignores or mishandles SIGTERM, Kubernetes has no way to signal a fast, graceful exit, and must wait out the full `terminationGracePeriodSeconds` before force-killing with SIGKILL. A is false — a well-behaved PID 1 can exit immediately upon SIGTERM, well before the grace period ends.

---

**Q11.** Which Linux namespace type prevents a process inside a container from seeing or signaling processes in other containers?
A. Mount namespace
B. PID namespace
C. UTS namespace
D. IPC namespace

**Correct answer: B**
*Explanation:* The PID namespace gives each container its own isolated process ID tree, so processes in one container cannot see or send signals to processes in another. Mount (A) isolates filesystem views, UTS (C) isolates hostname, IPC (D) isolates inter-process communication primitives — all real, but not the one governing process visibility.

---

**Q12.** What does the mount namespace isolate?
A. Network interfaces and routing tables
B. The set of filesystem mount points visible to a process
C. Process IDs
D. Hostname and domain name

**Correct answer: B**
*Explanation:* The mount namespace gives each container its own view of mounted filesystems, so a container can have `/` point to its image layers without affecting the host's or other containers' mount tables. The other options describe different namespace types (network, PID, UTS respectively).

---

**Q13.** Which command would you use on a Linux host to inspect the cgroup hierarchy limiting a specific container's CPU?
A. `iptables -L`
B. `cat /sys/fs/cgroup/.../cpu.max` (or equivalent cgroup path)
C. `ip route show`
D. `mount -t overlay`

**Correct answer: B**
*Explanation:* cgroup limits are exposed as pseudo-files under `/sys/fs/cgroup/`, and reading the relevant controller file (e.g., `cpu.max` in cgroups v2) shows the actual enforced limit. The other commands relate to networking or filesystem mounts, not resource limits.

---

**Q14.** Why is `chroot` alone considered insufficient container isolation compared to full namespace + cgroup isolation?
A. `chroot` isolates the filesystem root view but does nothing to isolate process IDs, network, or resource usage
B. `chroot` is slower than namespaces
C. `chroot` cannot be used on Linux
D. `chroot` requires a hypervisor

**Correct answer: A**
*Explanation:* `chroot` only changes the apparent filesystem root for a process — it does not isolate PIDs, network, users, or limit resources, all of which containers rely on namespaces and cgroups to provide. This is why modern containers layer many kernel primitives together rather than relying on `chroot` alone.

---

**Q15.** A process is consuming more memory than its cgroup's configured limit allows. What does the Linux kernel do?
A. Nothing; cgroup memory limits are advisory only
B. The kernel's OOM (out-of-memory) killer terminates a process in that cgroup to enforce the limit
C. The kernel automatically increases the limit
D. The process is paused indefinitely

**Correct answer: B**
*Explanation:* When a cgroup's memory limit is exceeded, the kernel's OOM killer intervenes within that cgroup's scope, terminating a process to bring usage back under the limit — this is the actual mechanism behind a Pod being reported as `OOMKilled`.

---

**Q16.** What is the relationship between `runc` and Linux namespaces/cgroups?
A. `runc` is a Linux namespace itself
B. `runc` is a low-level tool that directly invokes namespace and cgroup kernel APIs to actually create and start a container
C. `runc` replaces the need for a kernel entirely
D. `runc` only manages container images, not running containers

**Correct answer: B**
*Explanation:* `runc` is the OCI-compliant low-level runtime that does the actual work of calling into the kernel to set up namespaces, cgroups, and start the container process — it sits below higher-level runtimes like containerd. It is not a namespace itself, doesn't replace the kernel, and does handle running containers, not just images.

---

**Q17.** Which Linux capability model allows granting a container a narrow, specific kernel privilege (e.g., binding to a low-numbered port) without granting full root?
A. SELinux enforcing mode
B. Linux capabilities (e.g., `CAP_NET_BIND_SERVICE`)
C. cgroups v2 unified hierarchy
D. OverlayFS

**Correct answer: B**
*Explanation:* Linux capabilities break up the traditionally all-or-nothing root privilege into discrete units (like binding privileged ports), letting a container gain exactly one privilege without full root — a key principle behind Kubernetes' `securityContext.capabilities` field.

---

**Q18.** A Kubernetes node's `journalctl -u kubelet` shows repeated "failed to create pod sandbox" errors. What Linux-level area should you investigate first?
A. DNS records for the cluster
B. The container runtime's health and its ability to create network namespaces/sandboxes on that node
C. The Kubernetes API server's RBAC policy
D. The etcd cluster's disk usage

**Correct answer: B**
*Explanation:* "Pod sandbox" creation is a container-runtime-level (e.g., containerd/CRI-O) operation involving setting up namespaces and the pause container; failures here point to the runtime or its dependencies on that specific node, not to API-server-level or cluster-wide etcd concerns.

---

**Q19.** Why does Kubernetes use a small "pause" container in each Pod's sandbox on Linux?
A. To run the main application logic
B. To hold open the shared network namespace so other containers in the Pod can join it, even if they restart
C. To provide DNS resolution
D. To enforce cgroup memory limits

**Correct answer: B**
*Explanation:* The pause container's only job is to hold the Pod's shared Linux namespaces (especially network) open for the Pod's lifetime, so that application containers can restart independently without losing the shared network identity. It runs no application logic (A), doesn't do DNS (C) or enforce limits (D) itself.

---

**Q20.** Which statement correctly distinguishes Linux namespaces from cgroups?
A. Namespaces limit resource usage; cgroups provide isolation of what a process can see
B. Namespaces provide isolation of what a process can see; cgroups limit how much of a resource a process can use
C. They are two names for the exact same kernel mechanism
D. Namespaces only apply to networking; cgroups only apply to memory

**Correct answer: B**
*Explanation:* This is the foundational distinction for this entire chapter: namespaces control visibility/isolation (PID, network, mount, etc.), while cgroups control resource accounting and limits (CPU, memory, I/O). D incorrectly narrows both concepts to a single resource type each.

---

## 21. Chapter Summary (One-Page Revision Sheet)

- Kubernetes and containers run on plain Linux — there is no special "container kernel."
- **Namespaces** isolate what a process can *see* (PID, network, mount, UTS, IPC, user, cgroup namespaces).
- **cgroups** limit/account for what a process can *use* (CPU, memory, I/O) — this is what Kubernetes `resources.requests/limits` ultimately configure.
- **OverlayFS** (a union filesystem) stacks read-only image layers with a writable layer on top — the real mechanism behind container image layering.
- **A Pod** = one or more containers sharing the same network namespace (and often IPC namespace), but usually separate mount namespaces — this is why containers in a Pod share an IP but have separate filesystems.
- **PID 1** inside a container has special signal-handling responsibilities; mishandling SIGTERM causes slow Pod termination.
- **systemd** manages `kubelet` as a supervised service on every node — check `systemctl status kubelet` / `journalctl -u kubelet` first when a node is `NotReady`.
- File permissions (`rwx`, UID/GID) directly underlie Kubernetes' `securityContext` fields like `runAsUser`, `runAsNonRoot`, `fsGroup`.
- Memory trick: **"Namespaces = what you SEE, cgroups = what you GET."**

---

### Chapter Completion Checklist

1. **Topics covered:** Processes and PID 1, Linux filesystem hierarchy, users/groups/permissions, namespaces (all 7 types), cgroups (v1 vs v2), OverlayFS, systemd and its relationship to kubelet.
2. **KCNA objectives completed:** Foundational Linux vocabulary underlying Container Orchestration and Kubernetes Fundamentals domains.
3. **Remaining objectives:** Container image format/OCI, container runtimes (CRI, containerd, CRI-O) — covered next in Chapters 04–05.
4. **Suggested revision checklist:** Explain namespaces vs cgroups out loud using the hotel/circuit-breaker analogies without notes; redraw the "container startup" internal flow (Section 5) from memory; retake all 10 MCQs after 48 hours.
5. **Suggested hands-on exercises:** Complete all three labs in Section 11 (requires Docker installed, or use killercoda.com's free sandbox).
6. **Related chapters:** Previous: [01-Introduction-to-Cloud-Native](../01-Introduction-to-Cloud-Native/README.md). Next: [03-Networking-Basics](../03-Networking-Basics/README.md) — the network namespace concepts here are the direct foundation for understanding Pod networking.
