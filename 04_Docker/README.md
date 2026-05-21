# Docker & Containerization

```
Docker & Containerization
├── Container vs VM
│   ├── VM — virtualizes hardware (full OS per VM, GBs, seconds to start)
│   └── Container — virtualizes OS (shared kernel, MBs, milliseconds to start)
├── Docker Architecture
│   ├── docker CLI → dockerd (daemon) via REST on /var/run/docker.sock
│   ├── dockerd → containerd via gRPC
│   ├── containerd → containerd-shim → runc
│   └── runc → Linux kernel (namespaces + cgroups)
├── Core Concepts
│   ├── Dockerfile — instructions to build an image layer by layer
│   ├── Image — read-only layered filesystem snapshot (OCI image spec)
│   └── Container — running instance: image + writable layer + process
├── Linux Primitives
│   ├── Namespaces — isolation (pid, net, mnt, uts, ipc, user, cgroup)
│   └── cgroups — resource limits (memory, CPU, PIDs, blkio)
├── Image Engineering
│   ├── Layer caching — stable layers first, volatile layers last
│   ├── Multi-stage builds — build in full image, ship minimal runtime
│   ├── Distroless / scratch — minimal attack surface, no shell
│   └── .dockerignore — exclude .git, node_modules, __pycache__
├── Networking
│   ├── bridge (default docker0, no DNS) / user-defined bridge (DNS)
│   ├── host (no isolation, no NAT, highest performance)
│   ├── overlay (VXLAN multi-host, Swarm)
│   └── none (loopback only, air-gapped)
├── Storage
│   ├── Named volumes — Docker-managed, persist after container rm
│   └── Bind mounts — host path, dev hot-reload use case
├── Power User Commands
│   ├── docker stats, docker top, docker diff, docker events
│   └── docker system prune, docker buildx
├── Security
│   ├── Non-root USER, --read-only, --cap-drop ALL
│   ├── Vulnerability scanning (trivy, docker scout, grype)
│   └── Image signing (Cosign / Sigstore)
└── Best Practices
    ├── Immutable tags (no :latest in production)
    ├── HEALTHCHECK + restart policies
    └── PID 1 signal handling (exec form CMD, tini/dumb-init)
```

## First Principles

- **Why containers instead of VMs?** VMs boot a full OS kernel — GBs of disk, seconds of startup. Containers share the host kernel — only the application and its user-space libraries are packaged. This enables millisecond startup, MB-sized images, and running thousands of containers on a single host.
- **Why namespaces for isolation?** Without isolation, two containers would share PID numbers (process A in container 1 could kill process B in container 2), network interfaces, and filesystems. Namespaces give each container its own view of these resources — they believe they're the only process on the machine.
- **Why cgroups for resource limits?** A misbehaving container could consume all CPU or RAM and starve other containers. cgroups let the kernel enforce hard limits — when a container exceeds its memory limit, the kernel's OOM killer terminates it rather than letting it take down the host.
- **Why layers in Docker images?** Layers enable two things: (1) caching — if your dependencies didn't change, Docker reuses the cached layer; (2) sharing — if 10 containers use the same base image, those layers are stored once on disk, not 10 times.
- **Why multi-stage builds?** A Go compiler is 400MB but a compiled Go binary can be 10MB in a scratch image. Without multi-stage, the compiler lives in your production image — a massive, unnecessary attack surface. Multi-stage separates "what you need to build" from "what you need to run."
- **Why exec form CMD vs shell form?** Shell form wraps your command in `/bin/sh -c`. When Docker sends SIGTERM to PID 1 (the shell), the shell does not forward it to your app — the app dies via SIGKILL after the timeout. Exec form makes your app PID 1 directly, receiving SIGTERM for graceful shutdown.

Docker revolutionized DevOps by solving the "works on my machine" problem. It allows you to package an application with all its dependencies into a single, immutable artifact.

#### 1. Container vs. Virtual Machine
*   **Virtual Machine (VM):** Virtualizes the hardware. Each VM includes a full Operating System (Kernel + User Space). Slow, heavy, and resource-intensive.
*   **Container:** Virtualizes the Operating System. Shares the host's Kernel and only includes the application and its libraries. Fast, light, and portable.

#### 2. The Docker Architecture
Docker uses a client-server architecture:
*   **Docker CLI:** The tool you interact with.
*   **Docker Daemon (dockerd):** The background service that manages images and containers.
*   **Docker Hub/Registry:** The "store" where images are saved and shared.

#### 3. Core Concepts (The Big Three)
1.  **Dockerfile:** The "recipe" or build instructions for your image.
2.  **Image:** The "frozen" or read-only snapshot of your application.
3.  **Container:** The "running" instance of an image.

#### 4. The "Magic" Behind Containers
Docker doesn't use magic; it uses two Linux Kernel features:
*   **Namespaces:** Provide **Isolation**. They make the container think it's the only process on the machine (PID, Network, Mount namespaces).
*   **Control Groups (Cgroups):** Provide **Resource Limits**. They ensure a single container doesn't eat all the CPU or RAM on the host.

***

#### 🔹 1. Improved Notes: Image Engineering
*   **Layering:** Every instruction in a Dockerfile creates a "layer." Docker caches these layers to make builds lightning fast.
*   **Distroless & Scratch:** Senior engineers use minimal images like `alpine` or `distroless` to reduce the "attack surface" and keep image sizes under 50MB.
*   **Multi-Stage Builds:** A technique to separate the "Build" environment (with compilers and tools) from the "Runtime" environment (just the app binary).

#### 🔹 2. Interview View (Q&A)
*   **Q:** What is the difference between `CMD` and `ENTRYPOINT`?
*   **A:** `ENTRYPOINT` is the fixed command that the container runs. `CMD` provides default arguments that can be overridden by the user.
*   **Q:** How do you persist data in a container?
*   **A:** Use **Volumes**. Containers are ephemeral (they die and lose data), but Volumes are stored on the host's disk and survive container restarts.

***

#### 🔹 3. Architecture & Design: The Container Lifecycle
1.  **Build:** Create the image from a Dockerfile.
2.  **Ship:** Push the image to a registry.
3.  **Run:** Pull and start the container on any environment.

***

#### 🔹 4. Commands & Configs (Power User)
```bash
# Clean up everything (Stopped containers, unused images, networks)
docker system prune -a --volumes

# Look inside a running container to debug
docker exec -it <container_id> /bin/bash

# Check the resource usage of all containers
docker stats
```

***

#### 🔹 5. Troubleshooting & Debugging
*   **Scenario:** Your container starts but immediately exits.
*   **Fix:** Check the logs using `docker logs <container_id>`. Usually, it's because the "foreground" process finished or crashed. A container only stays alive as long as its PID 1 process is running.

***

#### 🔹 6. Production Best Practices
*   **Immutable Tags:** Never use `latest` in production. Always use specific version tags (e.g., `v1.2.3`) or image digests.
*   **Non-Root User:** By default, containers run as root. Always add a `USER` instruction to your Dockerfile to run as a low-privileged user for security.
*   **Scan for Vulnerabilities:** Use tools like `trivy` or `snyk` to scan your images for security holes before deploying.

***

#### 🔹 Cheat Sheet / Quick Revision
| **Command** | **Purpose** | **DevOps Context** |
| :--- | :--- | :--- |
| `docker build` | Create an image | The core step in a CI pipeline. |
| `docker-compose` | Manage multi-container apps | Great for local development (App + DB + Redis). |
| `docker inspect` | Show low-level info | Used to find the IP address or volume mounts. |
| `docker cp` | Copy files to/from container | Useful for extracting logs or config files. |

***

This is Section 4: Docker & Containerization. At a senior level, you should focus on **BuildKit** optimizations, **Rootless Docker**, and **OCI (Open Container Initiative)** standards.