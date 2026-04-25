---
description: Medium-difficulty interview questions for Docker networking, security, and production patterns.
---

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
