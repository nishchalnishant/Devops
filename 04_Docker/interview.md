# Docker — Interview Prep

---
description: Easy interview questions for Docker fundamentals, images, and containers.
---

```
Docker Interview — Easy
├── Core Model
│   ├── Image vs container (blueprint vs running instance)
│   ├── Dockerfile — sequential instructions, each creates a layer
│   └── Multi-stage builds — separate build tools from runtime
├── Dockerfile Instructions
│   ├── CMD vs ENTRYPOINT (overridable defaults vs fixed command)
│   ├── COPY vs ADD (explicit vs implicit tar/URL behavior)
│   ├── EXPOSE vs -p (documentation vs actual port binding)
│   └── .dockerignore — exclude .git, node_modules, __pycache__
├── Storage
│   ├── Named volumes — persist after container rm, Docker-managed
│   └── Container writable layer — ephemeral, lost on rm
├── Lifecycle
│   ├── docker stop (SIGTERM → SIGKILL after timeout)
│   ├── docker kill (SIGKILL immediately)
│   ├── docker ps vs docker ps -a (running vs all)
│   └── docker run -d vs foreground (detached vs attached)
└── Debugging
    ├── docker logs (-f follow, --tail, --since)
    ├── docker exec -it container bash
    └── docker inspect (full JSON metadata)
```

### First Principles

- **Why is an image read-only?** An image is a shared blueprint. Multiple containers run from the same image simultaneously — each adds its own writable layer. If the image were mutable, one container's changes would affect all others. Read-only images enable safe sharing.
- **Why does CMD exist if ENTRYPOINT already runs a command?** ENTRYPOINT fixes the executable (e.g., `python`). CMD provides default arguments that users can override at `docker run`. Together: `docker run myimage other_script.py` runs `python other_script.py`. Without ENTRYPOINT, the whole command would be replaced.
- **Why COPY over ADD?** `ADD` has implicit behaviors: auto-extract `.tar.gz`, fetch from URL. These side effects make Dockerfiles harder to reason about. `COPY` does exactly one thing. Predictability > cleverness.
- **Why volumes over the writable layer?** The writable layer uses the overlay filesystem — writes are slower than native I/O, and the data vanishes when the container is removed. Volumes bypass the copy-on-write filesystem entirely and persist independently of container lifecycle.
- **Why `docker stop` instead of `docker kill`?** `SIGTERM` gives the application time to flush buffers, close database connections, finish in-flight requests. `SIGKILL` is instant and unclean — data loss risk for stateful apps (databases, message queues).

## Easy

**1. What is the difference between a Docker image and a container?**

An image is a read-only, layered filesystem snapshot — the blueprint. A container is a running instance of an image — it adds a writable layer on top and starts a process. Multiple containers can run from the same image simultaneously, each with their own isolated writable layer. Deleting a container does not delete its image.

**2. What is a Dockerfile?**

A Dockerfile is a text file containing a sequence of instructions that Docker uses to build an image, layer by layer. Each instruction (`FROM`, `COPY`, `RUN`, `CMD`, etc.) creates a new layer. Docker caches each layer — if the instruction and its inputs haven't changed, the cached layer is reused, making subsequent builds faster.

**3. What is the difference between `CMD` and `ENTRYPOINT`?**

`CMD` specifies default arguments that can be overridden at `docker run`. `ENTRYPOINT` specifies the command that always runs — it's the main process. When both are set, `CMD` provides default arguments to `ENTRYPOINT`. Use `ENTRYPOINT ["python"]` + `CMD ["app.py"]` to allow `docker run my-image other_script.py` to override the script while always using Python.

**4. What is the difference between `COPY` and `ADD` in a Dockerfile?**

`COPY` copies files from the build context to the image — straightforward and predictable. `ADD` has implicit behaviors: it auto-extracts `.tar.gz` archives and can fetch files from URLs. `ADD` is considered a gotcha because of these implicit side effects. Prefer `COPY` for all regular file copying; use `ADD` only when you specifically need its tar-extraction behavior. For downloading files, prefer `RUN curl` + `RUN tar` for explicit control.

**5. What is a Docker volume and why use it instead of the container's writable layer?**

A volume is a Docker-managed storage area outside the container's writable layer. Volumes persist after the container is deleted, can be shared between containers, and offer better I/O performance because they bypass the copy-on-write filesystem. The container's writable layer is ephemeral — data written there is lost when the container is removed. Use volumes for databases, logs, and any data that must survive container restarts.

**6. What is the difference between `docker stop` and `docker kill`?**

`docker stop` sends `SIGTERM` to the container's main process (PID 1), giving it time to clean up gracefully. After a timeout (default 10 seconds), it sends `SIGKILL`. `docker kill` sends `SIGKILL` immediately — no cleanup. Always prefer `docker stop` for databases and stateful applications; use `docker kill` only when a container is stuck and not responding to SIGTERM.

**7. What does `docker ps -a` show vs `docker ps`?**

`docker ps` lists only running containers. `docker ps -a` (or `--all`) lists all containers including stopped and exited ones. Useful for debugging — an exited container retains its logs and filesystem until removed with `docker rm`. `docker ps -q` outputs only container IDs (useful for scripting: `docker rm $(docker ps -aq)` removes all stopped containers).

**8. What is a multi-stage Dockerfile and why is it valuable?**

A multi-stage Dockerfile uses multiple `FROM` statements. Earlier stages can contain build tools (compilers, package managers); only the final stage (which becomes the actual image) copies the built artifacts. Result: the production image contains only the runtime — no build tools, no source code, dramatically smaller and more secure. Example: a Go binary built with the `golang` image but shipped in `scratch` (empty) is only ~10MB vs 800MB.

**9. How does Docker networking work by default between containers?**

Containers on the same Docker bridge network can communicate using each other's container name as a hostname (Docker's built-in DNS). Containers on the default `bridge` network cannot resolve names — only IP addresses work, which change on every restart. Use `docker network create my-net` and `--network my-net` to get DNS-based discovery. Containers on different custom networks are isolated from each other.

**10. What is `.dockerignore` and why does it matter?**

`.dockerignore` lists files and directories to exclude from the build context sent to the Docker daemon. Without it, Docker sends everything in the directory — including `.git/` (potentially hundreds of MB), `node_modules/`, and test files. This wastes time and can accidentally leak sensitive data into the image. Always add `**/__pycache__`, `.git`, `node_modules`, `*.log`, `.env` to `.dockerignore`.

**11. What is the difference between `docker run -d` and `docker run`?**

`docker run` (without `-d`) runs the container in the foreground — terminal is attached to the container's stdout/stderr. `docker run -d` (detached) starts the container in the background and immediately returns the container ID. Use `-d` for long-running services (web servers, databases); use the foreground mode for one-off commands or interactive sessions (`docker run -it ubuntu bash`).

**12. How do you inspect a running container's environment and logs?**

```bash
docker logs my-container              # Print stdout/stderr
docker logs -f my-container           # Follow (tail -f equivalent)
docker logs --tail=100 my-container   # Last 100 lines
docker exec my-container env          # Print environment variables
docker exec -it my-container bash     # Interactive shell
docker inspect my-container           # Full JSON metadata (mounts, network, env)
```

---
description: Medium-difficulty interview questions for Docker networking, security, and production patterns.
---

```
Docker Interview — Medium
├── Build Optimization
│   ├── Layer caching — cache-friendly instruction ordering
│   │   ├── Copy requirements first, then install, then copy code
│   │   └── Any layer change invalidates all subsequent layers
│   └── BuildKit features
│       ├── Parallel stage execution (independent stages run concurrently)
│       ├── Cache mounts (--mount=type=cache, persist across builds)
│       ├── Secret mounts (--mount=type=secret, zero-trace secrets)
│       └── Remote cache (registry-based CI cache sharing)
├── Image Size Reduction
│   ├── Multi-stage builds (build tools never enter runtime image)
│   ├── Minimal base images (slim vs alpine vs distroless vs scratch)
│   ├── Combine RUN with && + cleanup in same layer
│   ├── .dockerignore (exclude test files, .git, node_modules)
│   └── dive tool (layer inspection for bloat analysis)
├── Docker Compose
│   ├── YAML-defined multi-container apps vs manual docker run
│   ├── Project-scoped network (DNS by service name)
│   └── depends_on + healthcheck for startup ordering
├── Security
│   ├── Running as root risks (UID 0 = host root if container escape)
│   ├── Mitigations: USER 1000, --read-only, --cap-drop ALL, no-new-privileges
│   └── K8s SecurityContext equivalents
├── Networking
│   ├── Overlay (VXLAN multi-host) vs host (no isolation, no NAT)
│   └── Port publishing internals (iptables DNAT)
├── Storage
│   └── Volumes (Docker-managed, portable) vs bind mounts (host path)
├── Observability
│   ├── docker stats (CPU%, MEM, NET I/O, BLOCK I/O, PIDs)
│   └── docker stats --no-stream (snapshot for scripts)
└── Distroless Images
    ├── No shell, no package manager = minimal attack surface
    └── Debugging: kubectl debug / docker debug variant
```

### First Principles

- **Why does layer ordering matter so much?** Docker cache invalidation is cascading — changing layer N invalidates N+1, N+2, ... to the end. If you copy application code before installing dependencies, a one-line code change forces a full `pip install`. Reordering (deps first, code second) means `pip install` is cached on 99% of builds.
- **Why does BuildKit's cache mount differ from layer cache?** Layer cache is tied to the Dockerfile instruction string. If you add one package, the entire `pip install` re-runs. Cache mount persists the pip download cache on the host — pip still re-installs, but downloads are skipped. Faster even on cache misses.
- **Why is running as root dangerous even inside a container?** Containers provide isolation via namespaces, not a true security boundary. If a container escape vulnerability exists (runc, kernel exploit), a root container immediately gains host root. A non-root container gains only the mapped UID on the host — far less damage potential.
- **Why distroless for production?** Attack surface = installed software. A distroless image has no shell, no package manager, no coreutils — nothing for an attacker to leverage even if they gain code execution inside the container. Fewer packages = fewer CVEs in vulnerability scans.
- **Why does `--cap-drop ALL` break some apps?** Docker gives containers a default capability set (e.g., `CHOWN`, `DAC_OVERRIDE`, `FOWNER`). Dropping all removes even these. Apps that bind ports <1024 need `NET_BIND_SERVICE`. Apps that change file ownership need `CHOWN`. Add back only the minimum required.

## Medium

**13. How does Docker layer caching work and how do you optimize for it?**

Every Dockerfile instruction creates a layer. Docker checks if the instruction and its inputs have changed; if not, it uses the cached layer. Cache is invalidated for a layer when the instruction changes OR when any preceding layer is invalidated.

Optimization: place instructions that change rarely at the top (base image, system packages) and frequently-changing instructions at the bottom (app code). Specifically:
```dockerfile
# WRONG: changes to requirements.txt invalidate the COPY . layer, 
# but then reinstalling packages also gets invalidated
COPY . /app
RUN pip install -r /app/requirements.txt

# CORRECT: requirements layer is cached independently
COPY requirements.txt .
RUN pip install -r requirements.txt   # cached unless requirements.txt changes
COPY src/ ./src/                      # rebuilds only this and below
```

**14. What is Docker Compose and how does it differ from running containers manually?**

Docker Compose defines multi-container applications in a YAML file (`docker-compose.yml`). Instead of running `docker run` with many flags for each service, `docker-compose up` starts all services with correct networking, volumes, and environment variables. Compose creates a project-scoped network, so services can reference each other by service name. It also manages startup order (`depends_on`), scaling, and provides `logs` across all services.

**15. What are the security risks of running containers as root and how do you mitigate them?**

Root in a container (UID 0) maps to root on the host if the container breaks out of its namespace. Risks: a process exploit can potentially escape the container and access the host filesystem or other containers.

Mitigations:
1. `USER 1000:1000` in Dockerfile to run as non-root.
2. `--read-only` flag makes the filesystem immutable at runtime (with `--tmpfs /tmp` for writable temp).
3. `--cap-drop ALL --cap-add NET_BIND_SERVICE` drops all Linux capabilities except what's needed.
4. `--security-opt no-new-privileges` prevents privilege escalation via setuid binaries.
5. In Kubernetes: `runAsNonRoot: true`, `allowPrivilegeEscalation: false`, `readOnlyRootFilesystem: true` in the SecurityContext.

**16. What is the difference between Docker overlay networks and host networking?**

**Overlay network:** Creates a virtual network spanning multiple hosts (Docker Swarm or custom). Containers on different hosts communicate as if on the same LAN. Uses VXLAN encapsulation. Good for multi-host setups.

**Bridge network (default on single host):** Virtual network within a single host. Containers get private IPs; traffic to/from the host goes through iptables NAT rules.

**Host network (`--network host`):** Container shares the host's network namespace — no network isolation. Container binds directly to host ports without NAT. Pro: zero overhead, highest performance. Con: no isolation — a port conflict crashes either the container or the host service. Not supported on macOS/Windows Docker Desktop (Linux only).

**17. How do Docker volumes differ from bind mounts?**

| | Volumes | Bind Mounts |
|:---|:---|:---|
| **Managed by** | Docker daemon | Host OS |
| **Path** | `/var/lib/docker/volumes/name/` | Any host path |
| **Portability** | Portable across environments | Ties container to specific host path |
| **Backup** | `docker volume inspect` + copy | Direct filesystem access |
| **Performance** | Slightly better (native drivers) | Direct host filesystem |
| **Use case** | Persistent data (databases) | Development (code hot-reloading) |

**18. What is Docker BuildKit and what improvements does it add?**

BuildKit is the modern build engine introduced in Docker 18.09, replacing the legacy builder. Key features:
- **Parallel stage execution:** Multi-stage builds run independent stages in parallel.
- **Cache mounts:** `RUN --mount=type=cache,target=/root/.cache/pip pip install ...` persists the pip cache across builds on the same host without polluting the image.
- **Secret mounts:** `RUN --mount=type=secret,id=ssh_key` injects secrets (SSH keys, tokens) into a build step without including them in any layer.
- **Faster:** Only rebuilds what changed; supports remote cache backends (GitHub Actions cache, AWS ECR).

Enable: `DOCKER_BUILDKIT=1 docker build .` or set in `daemon.json`.

**19. How do you reduce Docker image size?**

1. **Multi-stage builds:** Compile in a full image; copy only the binary/artifact to a minimal runtime image (`alpine`, `distroless`, `scratch`).
2. **Minimal base images:** `python:3.11-slim` (150MB) vs `python:3.11` (900MB) vs `python:3.11-alpine` (50MB — but musl libc may cause compatibility issues).
3. **Combine RUN commands:** Each `RUN` creates a layer; chaining with `&&` keeps cleanup in the same layer:
   ```dockerfile
   RUN apt-get update && apt-get install -y --no-install-recommends curl \
       && rm -rf /var/lib/apt/lists/*
   ```
4. **`.dockerignore`:** Don't send unnecessary files to the build context.
5. **`--no-install-recommends`:** Prevents apt from installing optional dependencies.
6. **Dive:** Use `dive my-image` to inspect layers and find what's bloating the image.

**20. What is `docker stats` and what metrics does it provide?**

`docker stats` streams live resource usage for running containers:
- **CPU %:** Percentage of available CPU used (can exceed 100% with multiple cores).
- **MEM USAGE / LIMIT:** Current memory usage vs the container's memory limit.
- **MEM %:** Memory usage as a percentage of the limit.
- **NET I/O:** Network bytes received/transmitted by the container.
- **BLOCK I/O:** Disk reads/writes.
- **PIDs:** Number of processes in the container.

`docker stats --no-stream` gets a single snapshot (useful in scripts). To set memory limits: `docker run --memory=512m --memory-swap=512m my-image` (setting swap equal to memory disables swap).

**21. What are distroless images and when should you use them?**

Distroless images (Google-maintained) contain only the application and its runtime dependencies — no shell, no package manager, no system utilities. Example: `gcr.io/distroless/python3` or `gcr.io/distroless/base`.

Benefits: dramatically reduced attack surface (no shell = no shell injection), smaller size, fewer CVEs (no system packages to patch).

Tradeoffs: debugging is much harder — you can't `docker exec -it container bash` because there's no bash. Use a debug variant (`gcr.io/distroless/python3:debug`) with a BusyBox shell for troubleshooting, or use ephemeral debug containers (`kubectl debug`).

```
Docker Interview — Hard
├── Debugging CrashLoopBackOff
│   ├── kubectl describe pod (Events: OOMKilled, probe failure, mount error)
│   ├── kubectl logs --previous (crash logs before restart)
│   ├── Override entrypoint: command: ["sleep", "3600"] for manual debug
│   └── kubectl debug (ephemeral container sharing PID namespace)
├── Ephemeral Containers vs kubectl exec
│   ├── kubectl exec — runs in existing container (needs shell + tools)
│   ├── kubectl debug -it pod --image=busybox --target=app — shares namespaces
│   └── Use case: distroless images with no shell
├── Container Runtime Interface (CRI)
│   ├── CRI = gRPC API between kubelet and high-level runtime
│   ├── High-level runtimes: containerd, CRI-O (implement CRI)
│   ├── Low-level runtimes: runc, gVisor (runsc), Kata (kata-runtime)
│   ├── Kubernetes uses CRI directly — dockershim removed in K8s 1.24
│   └── Debugging on nodes: crictl ps / crictl logs / crictl exec
├── Image Signing (Cosign / Sigstore)
│   ├── Keyless signing (OIDC-based, CI-native)
│   ├── cosign sign / cosign verify
│   ├── SBOM attestation (spdx-json, cyclonedx)
│   └── Admission enforcement: Kyverno verifyImages / OPA Gatekeeper
├── Docker Architecture Deep Dive
│   ├── Client-server: CLI → dockerd → containerd → shim → runc
│   ├── Namespace types: pid, net, mnt, uts, ipc, user, cgroup
│   └── Docker Compose vs Swarm vs Kubernetes trade-offs
└── Easy/Medium Coverage (also in this file)
    ├── Container vs VM fundamentals
    ├── Image lifecycle (build/ship/run)
    └── Medium: layer caching, BuildKit, networking modes, HEALTHCHECK, secrets
```

### First Principles

- **Why is CrashLoopBackOff so hard to debug?** The container crashes before your logging infrastructure can capture output. The challenge is accessing state that existed only during the crash. `--previous` logs capture the last run. Overriding the entrypoint to `sleep` keeps the container alive for manual inspection.
- **Why ephemeral containers?** Distroless images have no shell — `kubectl exec bash` fails. Ephemeral containers inject a debug sidecar (e.g., busybox) into the pod's namespace at runtime, with access to the same processes, network, and filesystem — without requiring the image to have debug tools.
- **Why did Kubernetes remove dockershim?** Docker was never designed as a Kubernetes dependency — dockershim was an adapter that translated CRI calls to Docker API calls. It added a translation layer with bugs and maintenance burden. Direct containerd via CRI eliminates the indirection.
- **Why keyless signing with Sigstore?** Traditional signing requires managing private keys — HSMs, rotation, revocation. Sigstore Cosign with OIDC uses short-lived signing certificates tied to your CI pipeline's identity (GitHub Actions OIDC token). No keys to store or rotate. Transparency log (Rekor) provides auditability.
- **Why admission controller for image verification?** Signing an image proves it hasn't been tampered with since signing. But signatures aren't enforced at deployment without an admission controller. Kyverno's `verifyImages` policy blocks unsigned or improperly signed images from being scheduled — the enforcement completes the supply chain security loop.

## Hard

**18. A Kubernetes Pod is in `CrashLoopBackOff`. `kubectl logs` is empty because the container crashes before logging. How do you debug?**

1. `kubectl describe pod <name>` — check the `Events` section for `OOMKilled`, failed volume mount, or liveness probe failure.
2. Override the entrypoint: set `command: ["sleep", "3600"]` in the Pod spec. The container stays alive.
3. `kubectl exec -it <pod> -- /bin/sh` — get a shell inside the running container.
4. Manually run the original command to see the immediate stdout/stderr error.
5. Check `kubectl get events --field-selector involvedObject.name=<pod>` for node-level events.

**19. What are ephemeral containers and when are they superior to `kubectl exec`?**

Ephemeral containers are temporary containers injected into an existing Pod's namespaces. They are superior when the main container is crashing (so `kubectl exec` can't reach it) or when the image lacks debugging tools. `kubectl debug -it <pod> --image=busybox --target=<container>` attaches an ephemeral container that shares the Pod's network and PID namespace, allowing use of tools like `strace`, `tcpdump`, or `gdb` even when the primary container is unstable.

**20. Explain the difference between the Container Runtime Interface (CRI) and a high-level runtime like Docker.**

The CRI is an API that allows `kubelet` to communicate with different container runtimes.
- **Low-level runtimes** (`runc`, `crun`) create and run containers using Linux namespaces and cgroups (OCI standard).
- **High-level runtimes** (`containerd`, `CRI-O`) implement CRI — they pull images, manage storage, and delegate to `runc` for execution.

Docker is a monolithic platform that bundles a high-level runtime, CLI, and build tooling. Kubernetes via CRI talks directly to containerd/CRI-O, bypassing much of the Docker tooling layer.

**21. What is image signing and how does it enforce supply chain security?**

Image signing uses cryptographic signatures (Sigstore/Cosign) to attest that an image was produced by a trusted build system. Workflow:
1. CI builds image, pushes to registry.
2. `cosign sign --key cosign.key registry.io/app:sha256-abc123` — signature stored in registry.
3. Kubernetes admission controller (Kyverno, Gatekeeper) verifies signature before allowing Pod creation. If the signature is absent or invalid, the Pod is rejected.
This prevents running unsigned or tampered images even if someone pushes directly to the registry.
# Docker Interview Mastery (Senior Level)

This guide distills the core technical requirements and high-stakes scenario drills for Docker, optimized for Senior DevOps (4+ YOE) candidates. It moves beyond basic commands into architectural trade-offs and runtime security.

***

### 🏗️ Core Architecture & Fundamentals

### 1. Explain the Docker Client-Server Architecture
Docker uses a **client-server architecture**.
- **Docker Client:** The CLI tool where you run commands. It translates commands into REST API calls.
- **Docker Host (Daemon):** The `dockerd` process that listens for API requests and manages Docker objects (images, containers, networks, volumes).
- **Registry:** A stateless, highly scalable server side application that stores and lets you distribute Docker images.

> [!TIP]
> In interviews, emphasize the **REST API** aspect. It's how tools like Kubernetes or CI/CD pipelines interact with the Docker Daemon remotely.

### 2. Docker Images vs. Containers
- **Docker Image:** A read-only template with instructions for creating a Docker container. It is composed of multiple layers.
- **Docker Container:** A runnable instance of an image. It adds a "writable layer" on top of the static image layers.

> [!IMPORTANT]
> **Click Moment:** Always mention that containers are *isolated processes* in user space, sharing the host OS kernel. This is the fundamental difference from Virtual Machines.

***

### 🛠️ Practical Operations & Lifecycle

### 3. Explain the Container Lifecycle
1. **Create:** Container is created but not started.
2. **Run:** Container is started (combined `create` + `start`).
3. **Pause/Unpause:** Suspend/Resume all processes in the container.
4. **Stop:** Send `SIGTERM` (graceful) followed by `SIGKILL` (forced).
5. **Kill:** Send `SIGKILL` immediately.
6. **Restart:** Stop and Start again.

### 4. How do you access a running container?
Use the `exec` command:
```bash
docker exec -it <container_id> bash
```
> [!NOTE]
> The `-it` flag stands for **interactive** and **TTY**, allowing you to interact with the shell.

***

### 🚀 Advanced Scenarios & Troubleshooting

### 5. Will you lose data when a container exits?
**No.** Data written to the container's writable layer persists until the container is *deleted* (`docker rm`). However, for production persistence, **Volumes** or **Bind Mounts** are mandatory to decoupled data from the container lifecycle.

### 6. Application Isolation & Namespaces
Docker achieves isolation using **Linux Namespaces**:
- **PID:** Process isolation.
- **NET:** Network stack isolation.
- **IPC:** Inter-process communication isolation.
- **MNT:** Mount point isolation.
- **UTS:** Hostname and NIS domain name isolation.

> [!CAUTION]
> If an interviewer asks about security, mention that namespaces provide *isolation*, while **Cgroups** provide *resource limitation* (CPU/Memory). Both are required for a secure environment.

***

### 📦 Docker Compose & Orchestration

### 7. What is Docker Compose?
A tool for defining and running multi-container Docker applications using a `YAML` file. It allows you to manage the entire stack (web, db, cache) with a single command: `docker-compose up`.

### 8. Docker Swarm vs. Kubernetes
- **Docker Swarm:** Native clustering, easy to set up, suitable for smaller workloads.
- **Kubernetes:** More complex, highly extensible, the industry standard for enterprise-scale orchestration.

***

### 🎯 Quick Fire Interview Tips
- **Image Optimization:** Always mention multi-stage builds to reduce image size.
- **Security:** Run containers as non-root users.
- **Networking:** Understand the difference between `bridge`, `host`, and `none` drivers.
of load balancing across containers and hosts? How does it work?


***

# Docker — Easy Interview Questions

***

**1. What is a container and how does it differ from a virtual machine?**

A container is an isolated process running on the host's Linux kernel, packaged with its application and dependencies. It uses Linux namespaces for isolation and cgroups for resource limits.

A VM includes a full guest OS and runs on a hypervisor. Key differences:

| Dimension | Container | VM |
|-----------|-----------|-----|
| Kernel | Shares host kernel | Own guest kernel |
| Start time | Milliseconds | Seconds–minutes |
| Size | MBs | GBs |
| Isolation | Namespace-based (softer) | Hypervisor-based (harder) |
| Overhead | Near zero | Fixed guest OS memory |

***

**2. What is a Docker image vs. a container?**

A Docker image is a read-only, immutable template made of ordered layers. A container is a running instance of an image — it adds a thin writable layer on top of all the image's read-only layers.

```
Image layers (read-only):
  Layer 2: COPY app.py /app
  Layer 1: RUN pip install flask
  Layer 0: FROM python:3.12-slim
─────────────────────────────────
Container writable layer (ephemeral — lost on docker rm)
```

Multiple containers from the same image share the same underlying layers — no duplication on disk.

***

**3. What is a Dockerfile and what are its most commonly used instructions?**

A Dockerfile is a text file containing instructions that Docker executes sequentially to build an image. Each instruction creates a new layer.

| Instruction | Purpose |
|-------------|---------|
| `FROM` | Base image — every Dockerfile starts here |
| `RUN` | Execute command during build; creates a layer |
| `COPY` | Copy files from build context into image |
| `CMD` | Default command/args when container starts |
| `ENTRYPOINT` | Fixed executable for the container |
| `ENV` | Set environment variables (persists at runtime) |
| `EXPOSE` | Document which port the container listens on |
| `WORKDIR` | Set working directory for subsequent instructions |
| `USER` | Set UID/GID for subsequent instructions and runtime |
| `ARG` | Build-time variable (not available at runtime) |
| `VOLUME` | Declare a mount point |
| `HEALTHCHECK` | Define a health probe command |
| `LABEL` | Attach metadata key-value pairs |

***

**4. What is the difference between `CMD` and `ENTRYPOINT`?**

`ENTRYPOINT` defines the main executable that always runs. `CMD` provides default arguments to it. When used together, `CMD` can be overridden at `docker run` while `ENTRYPOINT` stays fixed unless explicitly overridden with `--entrypoint`.

```dockerfile
ENTRYPOINT ["nginx"]
CMD ["-g", "daemon off;"]
```

```bash
docker run myimg               # → nginx -g "daemon off;"
docker run myimg -t            # → nginx -t    (CMD replaced)
docker run --entrypoint sh myimg  # → sh (ENTRYPOINT replaced)
```

> [!TIP]
> Always use the exec form (`["executable", "arg"]`) for both CMD and ENTRYPOINT so signals are delivered directly to your process, not to a shell wrapper that might swallow them.

***

**5. What does `COPY` do vs `ADD` in a Dockerfile?**

`COPY` copies files and directories from the build context into the image. It does exactly that — nothing more.

`ADD` does the same but additionally:
- Auto-extracts local `.tar` archives into the destination
- Can fetch remote URLs (but does not extract them)

Best practice: use `COPY` for all file copying. Use `ADD` only when you specifically need tar extraction. Using `ADD` with a URL is discouraged — use `RUN curl` instead so the download is explicit in the layer cache.

***

**6. What is a Docker volume and why is it used?**

A volume provides persistent storage outside the container's writable layer. Data written to a volume persists after the container stops or is removed.

```bash
# Named volume (recommended)
docker volume create mydata
docker run -v mydata:/app/data myapp

# Bind mount (maps a specific host path)
docker run -v /host/path:/container/path myapp

# Anonymous volume
docker run -v /data myapp   # Docker auto-generates a volume name
```

Volumes are not affected by `docker commit` — image snapshots do not include volume data.

***

**7. What are named vs anonymous volumes?**

| Type | How created | Name | Survives `docker rm` |
|------|-------------|------|----------------------|
| **Named** | `docker volume create myv` or `-v myv:/path` | User-defined | Yes |
| **Anonymous** | `-v /path` or `VOLUME` without a name binding | Auto-generated hash | No (removed with `--rm` containers) |

Named volumes are always preferred in production because they can be referenced by name for backup, inspection, and sharing across containers.

***

**8. How do you run a container in the background and check its status?**

```bash
# Run detached
docker run -d --name web nginx

# Check running containers
docker ps

# Check all containers (including stopped)
docker ps -a

# Check logs
docker logs web
docker logs -f web   # follow
```

***

**9. What does `-p 8080:80` mean in a docker run command?**

It publishes port 80 of the container to port 8080 on the host. Traffic arriving at `host:8080` is DNAT'd (by iptables) to the container's port 80.

```
Host port 8080 → [iptables DNAT] → Container port 80
```

You can also:
- `-p 80` — publish container port 80 to a random host port
- `-P` — publish all `EXPOSE`d ports to random host ports
- `-p 127.0.0.1:8080:80` — bind only on localhost (not all interfaces)

***

**10. How do you pass environment variables into a container?**

```bash
# Single variable
docker run -e NODE_ENV=production myapp

# Multiple variables
docker run -e NODE_ENV=production -e PORT=3000 myapp

# From a file
docker run --env-file .env myapp
```

In Docker Compose:
```yaml
services:
  web:
    image: myapp
    environment:
      - NODE_ENV=production
      - PORT=3000
    env_file:
      - .env
```

> [!CAUTION]
> Environment variables set via `-e` are visible in `docker inspect`. Never pass secrets (passwords, API keys) as environment variables in production — use secret management tools (Vault, AWS Secrets Manager) or Docker/Kubernetes secrets.

***

**11. What is `.dockerignore` and why is it important?**

`.dockerignore` specifies files and directories to exclude from the build context that gets sent to the Docker daemon. This:

1. Speeds up builds — less data transferred to the daemon
2. Reduces image size — prevents unnecessary files entering layers
3. Improves security — prevents secrets, keys, and `.git` history from being baked into images

```
# .dockerignore
.git
.env
*.log
node_modules
__pycache__
.pytest_cache
dist
coverage
*.md
Dockerfile*
docker-compose*
```

***

**12. What is Docker Compose and what problem does it solve?**

Docker Compose uses a `docker-compose.yml` (or `compose.yaml`) YAML file to define and run multi-container applications. Instead of running multiple `docker run` commands manually and wiring up networking and volumes, Compose handles all of it declaratively.

```yaml
services:
  web:
    build: .
    ports:
      - "8080:80"
    depends_on:
      - db
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb

  db:
    image: postgres:16
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD=pass

volumes:
  pgdata:
```

```bash
docker compose up -d      # start all services
docker compose down       # stop and remove containers + networks
docker compose logs -f    # follow logs
```

***

**13. What is the difference between `docker stop` and `docker kill`?**

`docker stop` sends `SIGTERM` to the container's PID 1, giving it time to shut down gracefully. After a timeout (default 10 seconds), it sends `SIGKILL`.

`docker kill` sends `SIGKILL` immediately (or a custom signal with `-s`), bypassing graceful shutdown.

```bash
docker stop -t 30 mycontainer   # 30-second grace period
docker kill mycontainer          # immediate termination
docker kill -s SIGUSR1 mycontainer  # send custom signal
```

***

**14. What are restart policies and when would you use each one?**

| Policy | Behavior |
|--------|----------|
| `no` | Never restart (default) |
| `on-failure` | Restart if exit code is non-zero |
| `on-failure:3` | Same, but max 3 attempts |
| `always` | Always restart, including when Docker daemon starts |
| `unless-stopped` | Always restart, except if manually stopped |

```bash
docker run --restart unless-stopped nginx   # production services
docker run --restart on-failure:3 worker    # batch jobs that should retry
```

***

**15. What is a base image and what makes a good one for production?**

A base image is the starting point (`FROM <image>`) for your Docker image. For production:

| Base | Size | Use case |
|------|------|----------|
| `ubuntu:22.04` | ~29 MB | General; lots of tools available |
| `debian:bookworm-slim` | ~74 MB | Good balance, glibc |
| `alpine:3.19` | ~7 MB | Minimal; uses musl libc (can cause issues with C-bound languages) |
| `gcr.io/distroless/static` | ~2 MB | No shell, no package manager — maximum security |
| `gcr.io/distroless/python3` | ~50 MB | Python without shell |
| `scratch` | 0 B | For statically compiled Go/Rust binaries |

> [!IMPORTANT]
> Smaller base images have fewer packages, which means fewer potential CVEs. Always prefer `distroless` or `scratch` for production containers when possible.

***

**16. What does `docker exec` do and how is it different from `docker attach`?**

`docker exec` creates a **new process** inside the running container. The container's PID 1 keeps running unaffected.

`docker attach` connects your terminal to the container's **PID 1** stdin/stdout. Pressing `Ctrl+C` sends `SIGINT` to PID 1, which may kill the container.

```bash
docker exec -it mycontainer bash    # new process — safe for debugging
docker attach mycontainer           # attaches to PID 1 — be careful with Ctrl+C
```

***

**17. How do you share data between two containers?**

**Option 1: Named volume (recommended)**
```bash
docker volume create shared
docker run -v shared:/data --name producer myapp
docker run -v shared:/data:ro --name consumer reader
```

**Option 2: `--volumes-from`**
```bash
docker run --name producer -v /data myapp
docker run --volumes-from producer --name consumer reader
```

**Option 3: Bind mount to host path**
```bash
docker run -v /host/shared:/data producer
docker run -v /host/shared:/data:ro consumer
```
# Docker — Medium Interview Questions

***

**1. How do Docker layers work and why does layer ordering matter for build performance?**

Each Dockerfile instruction that modifies the filesystem creates an immutable, content-addressed layer (a compressed tar diff). The build cache computes a key based on:

1. The parent layer digest (all previous layers must match)
2. The instruction string (for `RUN`)
3. The file checksums (for `COPY`/`ADD`)

If all inputs match, Docker reuses the cached layer without executing the instruction. Invalidating one layer invalidates all subsequent layers — this cascade makes ordering critical.

```dockerfile
# BAD: every code change invalidates pip install
FROM python:3.12-slim
COPY . /app
RUN pip install -r /app/requirements.txt   # reinstalls every time

# GOOD: pip install cached unless requirements.txt changes
FROM python:3.12-slim
COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt   # cached most of the time
COPY . /app                                # changes here don't affect pip layer
```

**Rule:** Put instructions that change rarely near the top; frequently-changing content near the bottom.

***

**2. Explain multi-stage builds and how you would use one to reduce a Go image from 800 MB to under 10 MB.**

Multi-stage builds use multiple `FROM` instructions. Each stage starts fresh and can copy artifacts from earlier stages. Only the final stage is included in the output image.

```dockerfile
# Stage 1: build (has Go toolchain — ~800 MB)
FROM golang:1.22-alpine AS builder
WORKDIR /src
COPY go.mod go.sum ./
RUN --mount=type=cache,target=/root/go/pkg/mod go mod download
COPY . .
RUN --mount=type=cache,target=/root/.cache/go-build \
    CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o /bin/app ./cmd/app

# Stage 2: runtime (just the binary — ~3 MB)
FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=builder /bin/app /app
USER nonroot:nonroot
ENTRYPOINT ["/app"]
```

The Go toolchain, source code, and module cache never appear in the final image. `-ldflags="-s -w"` strips debug symbols, further reducing binary size.

***

**3. How does Docker's build cache work with BuildKit and how would you configure registry-based caching for CI?**

Classic Docker uses a local layer cache. BuildKit uses a content-addressed cache and supports exporting/importing cache from a registry, which allows CI runners (which are ephemeral) to share build cache.

```bash
# In CI: import cache from registry, export updated cache after build
docker buildx build \
  --cache-from type=registry,ref=myrepo/myapp:buildcache \
  --cache-to   type=registry,ref=myrepo/myapp:buildcache,mode=max \
  --push \
  -t myrepo/myapp:$CI_COMMIT_SHA .
```

`mode=max` exports all intermediate layer caches (not just the final image's layers), giving maximum cache hit rate on subsequent builds.

BuildKit also supports `--mount=type=cache` in Dockerfile instructions for persistent package manager caches:

```dockerfile
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt
```

This cache persists between builds on the same builder instance, independently of the layer cache.

***

**4. What are the Docker networking modes and when would you use each one?**

| Mode | Isolation | Use case |
|------|-----------|----------|
| `bridge` (default) | Container-level, NAT for external | General single-host workloads |
| Custom bridge | Same, but with container DNS | Multi-container apps on same host |
| `host` | None — shares host network stack | High-throughput, no NAT needed |
| `none` | Full — only loopback | Batch jobs, fully isolated workloads |
| `overlay` | VXLAN-encapsulated multi-host | Docker Swarm, multi-host networking |
| `macvlan` | Container appears as physical NIC | Legacy apps needing LAN IP |
| `ipvlan` | Shares host MAC, unique IPs | Large deployments, no ARP storms |

```bash
# Custom bridge — enables container name DNS resolution
docker network create mynet
docker run --network mynet --name web nginx
docker run --network mynet --name app myapp
# app can curl http://web:80

# Host — no port mapping needed or possible
docker run --network host nginx   # nginx binds port 80 directly on host

# None — no network access
docker run --network none python script.py
```

***

**5. What is a HEALTHCHECK and how does it interact with Docker Compose `depends_on`?**

`HEALTHCHECK` defines a probe that Docker runs periodically to determine if the container is healthy. The container transitions between states: `starting` → `healthy` / `unhealthy`.

```dockerfile
HEALTHCHECK \
  --interval=30s \
  --timeout=5s \
  --start-period=15s \
  --retries=3 \
  CMD curl -f http://localhost/health || exit 1
```

```bash
docker inspect mycontainer | jq '.[0].State.Health'
```

In Docker Compose, `depends_on` with `condition: service_healthy` waits until the dependency is healthy before starting the dependent service:

```yaml
services:
  api:
    image: myapi
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
```

> [!IMPORTANT]
> Without `condition: service_healthy`, `depends_on` only waits for the container to start (not for the application inside to be ready). This is a common source of race conditions.

***

**6. How do you enforce resource limits on containers and what happens when a container exceeds its memory limit?**

```bash
docker run \
  -m 512m \               # hard memory limit (RAM)
  --memory-swap 1g \      # total: RAM + swap (set equal to -m to disable swap)
  --memory-reservation 256m \  # soft limit (scheduling hint)
  --cpus="1.5" \          # 1.5 CPU cores (CFS quota: 150ms/100ms period)
  --cpu-shares=512 \      # relative weight when contention (default 1024)
  --pids-limit=100 \      # max processes (prevents fork bomb)
  --blkio-weight=400 \    # I/O weight (default 500)
  myapp

# Update limits on running container
docker update -m 1g --cpus="2" mycontainer
```

When a container exceeds its memory limit, the Linux kernel OOM killer sends `SIGKILL` to a process in the container (usually PID 1). The container exits with code `137`. Docker records this as `OOMKilled: true`:

```bash
docker inspect mycontainer | jq '.[0].State | {OOMKilled, ExitCode}'
```

The container does not restart unless a restart policy is configured. In Kubernetes, this surfaces as `OOMKilled` reason in `kubectl describe pod`.

***

**7. What is the difference between `EXPOSE` and publishing a port (`-p`)?**

| Mechanism | What it does |
|-----------|-------------|
| `EXPOSE 80` | Documentation only — signals intent; no actual firewall rule |
| `-p 8080:80` | Creates an iptables DNAT rule: host:8080 → container:80 |
| `-P` | Auto-publishes all EXPOSE'd ports to random host ports |
| Neither | Port only accessible within container itself |

```
If expose only (no -p):   accessible from other containers on same Docker network
If -p (with or without EXPOSE):  accessible from host and external traffic
```

The practical rule: `EXPOSE` is for documentation and Docker tooling (e.g., `-P`). Port publishing (`-p`) is what actually opens traffic.

***

**8. How do you handle secrets in Docker images and builds?**

> [!CAUTION]
> A secret added in one `RUN` layer and deleted in a later `RUN` layer is still present in the intermediate layer and visible via `docker history` or layer inspection. Never put secrets in Dockerfile instructions.

**Build-time secrets (BuildKit — no layer trace):**
```dockerfile
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc \
    npm install --ignore-scripts
```
```bash
docker build --secret id=npmrc,src=$HOME/.npmrc .
```

**Runtime secrets (environment variables — visible in inspect):**
```bash
docker run -e API_KEY="$API_KEY" myapp   # avoid for sensitive values
```

**Runtime secrets (Docker secrets in Swarm):**
```bash
echo "mysecretvalue" | docker secret create my_secret -
docker service create \
  --secret my_secret \
  --name myapp myimage
# Secret available at /run/secrets/my_secret inside container
```

**Best practice in production:** Use a secrets manager (HashiCorp Vault, AWS Secrets Manager, Azure Key Vault) with a sidecar or init container that fetches secrets at startup and injects them as files into a tmpfs mount.

***

**9. What is containerd and how does it relate to Docker?**

containerd is a high-level container runtime — it manages the full container lifecycle: image pull/push/store, container execution via shims, and snapshotting (overlay2).

```
Docker CLI → dockerd → containerd → containerd-shim → runc → container process
                                         ↑
Kubernetes kubelet → CRI → containerd → (no dockerd involved)
```

Docker is built on top of containerd. When Docker builds and runs a container, it delegates to containerd for execution. Kubernetes, since version 1.24 (dockershim removal), talks to containerd directly via the Container Runtime Interface (CRI), bypassing the Docker daemon entirely.

You can interact with containerd directly using `ctr`:
```bash
ctr images ls
ctr containers ls
ctr tasks ls
```

Or via the CRI with `crictl` (useful on Kubernetes nodes):
```bash
crictl ps
crictl images
crictl inspect <container-id>
```

***

**10. How do Docker Compose override files work?**

Compose merges a base file with one or more override files. Values from the override take precedence.

```yaml
# docker-compose.yml (base — production defaults)
services:
  web:
    image: myapp:latest
    restart: unless-stopped
    environment:
      - NODE_ENV=production

# docker-compose.override.yml (development overrides — loaded automatically)
services:
  web:
    build: .           # build locally instead of pulling
    volumes:
      - ./src:/app/src # live code reload
    environment:
      - NODE_ENV=development
    ports:
      - "3000:3000"
```

```bash
# Loads both files automatically (default)
docker compose up

# Specify explicit files
docker compose -f docker-compose.yml -f docker-compose.staging.yml up

# View merged config
docker compose config
```

This pattern is standard: base file for production, `override.yml` for development, explicit `-f` flags for staging/CI.

***

**11. How does bridge networking use iptables under the hood?**

When Docker starts, it creates:

1. A `docker0` virtual bridge interface on the host (`172.17.0.1/16`)
2. A `veth` (virtual ethernet) pair per container — one end in the container's network namespace (`eth0`), one end attached to `docker0`
3. iptables rules:

```bash
# NAT table — outbound from containers (MASQUERADE = SNAT with dynamic IP)
iptables -t nat -A POSTROUTING -s 172.17.0.0/16 ! -o docker0 -j MASQUERADE

# Port publishing DNAT (for -p 8080:80)
iptables -t nat -A DOCKER -p tcp --dport 8080 -j DNAT --to-destination 172.17.0.2:80

# Forward table — allow container-to-container traffic
iptables -A FORWARD -i docker0 -o docker0 -j ACCEPT
```

```bash
# View Docker's iptables rules
iptables -t nat -L DOCKER -n -v
iptables -L DOCKER-USER -n -v
```

> [!TIP]
> The `DOCKER-USER` chain is where you can add custom iptables rules that Docker will not overwrite on daemon restart.

***

**12. What is image scanning and how would you integrate it into a CI pipeline?**

Image scanning analyzes image layers for known CVEs (Common Vulnerabilities and Exposures) in OS packages and language dependencies.

**Tools:**
- `trivy` — fast, comprehensive, open source
- `docker scout` — built into Docker CLI
- `grype` — Anchore's scanner
- `snyk` — commercial, deep license analysis

```bash
# Trivy in CI (fail on CRITICAL CVEs)
trivy image \
  --exit-code 1 \
  --severity CRITICAL,HIGH \
  --ignore-unfixed \
  myrepo/myapp:$CI_COMMIT_SHA

# Generate SBOM
trivy image --format cyclonedx --output sbom.json myrepo/myapp:latest

# Docker Scout
docker scout cves --exit-code myrepo/myapp:latest
docker scout recommendations myrepo/myapp:latest
```

**CI integration pattern (GitHub Actions):**
```yaml
- name: Scan image
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: myrepo/myapp:${{ github.sha }}
    format: sarif
    output: trivy-results.sarif
    severity: CRITICAL,HIGH
    exit-code: 1

- name: Upload SARIF
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: trivy-results.sarif
```

***

**13. What is the difference between `docker cp`, bind mounts, and volumes for development workflows?**

| Method | Use case | Persistence | Live reload |
|--------|----------|-------------|-------------|
| `docker cp` | One-time file transfer | No | No |
| Bind mount | Development — source code | Host filesystem | Yes |
| Named volume | Production data persistence | Volume | Not typically |

```bash
# docker cp — copy a config file into a running container (one-off)
docker cp ./nginx.conf mycontainer:/etc/nginx/nginx.conf
docker exec mycontainer nginx -s reload

# Bind mount — development with live reload
docker run -d \
  -v $(pwd)/src:/app/src \   # source code — changes reflected immediately
  -v $(pwd)/config:/app/config:ro \
  -p 3000:3000 \
  myapp:dev

# Named volume — production database
docker run -d \
  -v pgdata:/var/lib/postgresql/data \
  postgres:16
```

***

**14. How do Docker Compose `profiles` work?**

Profiles allow you to selectively start services. Services without a profile always start; services with a profile only start when that profile is activated.

```yaml
services:
  web:
    image: myapp        # always starts

  db:
    image: postgres     # always starts

  adminer:
    image: adminer
    profiles: [debug]   # only when debug profile is active

  prometheus:
    image: prom/prometheus
    profiles: [monitoring]
```

```bash
docker compose --profile debug up        # starts web, db, adminer
docker compose --profile monitoring up   # starts web, db, prometheus
docker compose up                        # starts web, db only
```

***

**15. How would you reduce a Docker image from 800 MB to 50 MB for a Node.js application?**

1. **Multi-stage build** — separate build deps from runtime deps
2. **Minimal base** — use `node:20-alpine` instead of `node:20` (saves ~700 MB)
3. **Production deps only** — `npm ci --only=production`
4. **Layer hygiene** — combine `RUN` instructions, clean caches in the same layer

```dockerfile
# Stage 1: install all deps and build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm ci
COPY . .
RUN npm run build

# Stage 2: production image
FROM node:20-alpine AS production
WORKDIR /app
COPY package*.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm ci --only=production && npm cache clean --force
COPY --from=builder /app/dist ./dist
USER node
CMD ["node", "dist/index.js"]
```

Additional tricks:
- Use `--ignore-scripts` to skip postinstall hooks that bloat the image
- Use `.dockerignore` to exclude `node_modules`, test files, docs
- Use `docker history` to identify which layers are largest
- Use `dive` to interactively inspect layer contents
