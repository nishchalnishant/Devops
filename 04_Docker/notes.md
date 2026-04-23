# Docker — Conceptual Notes

## Docker Architecture

Docker uses a **client-server architecture** with three main components:

| Component | Role |
|-----------|------|
| Docker Client (`docker` CLI) | Translates commands into REST API calls sent to `dockerd` |
| Docker Daemon (`dockerd`) | Listens on a Unix socket or TCP; manages images, containers, networks, volumes |
| Registry (Docker Hub / private) | Stores and distributes image layers |

Communication flow:
```
docker build/run/pull
       ↓ REST API (unix:///var/run/docker.sock or tcp)
    dockerd
       ↓ OCI calls
   containerd → runc → Linux kernel (namespaces + cgroups)
```

The daemon can be managed remotely (`DOCKER_HOST` env var or `--host` flag), which is how CI/CD systems and orchestrators interact with Docker engines.

---

## Images vs. Containers

| Concept | Description |
|---------|-------------|
| **Image** | Read-only, immutable template composed of ordered layers |
| **Container** | Runnable instance of an image; adds a thin writable layer on top |

An image is a DAG of layers; containers share all read-only layers and diverge only in their writable layer. Deleting a container discards only its writable layer — the image layers remain.

```
Image Layer N  (read-only)   ← RUN apt-get install nginx
Image Layer N-1 (read-only)  ← COPY . /app
Image Layer 1  (read-only)   ← FROM ubuntu:22.04
─────────────────────────────────────────────────────
Container writable layer     ← runtime writes (logs, temp files)
```

---

## Layered Filesystem: overlay2

Docker's default storage driver on Linux is **overlay2**, backed by the kernel OverlayFS.

```
Upper dir  (container writable layer)
Lower dirs (image layers, stacked read-only)
Merged dir (unified view presented to container)
Work dir   (OverlayFS internal use)
```

Key behaviors:
- **Copy-on-Write (CoW):** When a container modifies a file from a lower layer, it is copied to the upper directory first, then modified. The lower layer remains unchanged.
- Layer deduplication: Multiple containers sharing the same image base share the same on-disk lower dirs — no duplication.
- `docker inspect <image>` → `GraphDriver.Data` shows the actual overlay paths.

---

## Linux Namespaces

Namespaces provide **isolation** — each container gets its own view of the OS:

| Namespace | Isolates |
|-----------|----------|
| `pid` | Process tree — PID 1 inside container is isolated from host PIDs |
| `net` | Network stack — each container gets its own `eth0`, routing table, iptables |
| `mnt` | Filesystem mount points |
| `uts` | Hostname and NIS domain name |
| `ipc` | System V IPC, POSIX message queues |
| `user` | UID/GID mapping (rootless Docker) |

Verify: `ls -la /proc/<container-pid>/ns/`

---

## cgroups (Control Groups)

Cgroups provide **resource limitation** — namespaces provide isolation, cgroups enforce limits:

```bash
# Limit container to 512 MB RAM and 0.5 CPU
docker run -m 512m --cpus="0.5" nginx
```

| cgroup subsystem | Controls |
|------------------|----------|
| `memory` | RAM and swap limits, OOM killer behavior |
| `cpu` / `cpuset` | CPU shares, quotas, pinning to cores |
| `blkio` | Block I/O throttling |
| `pids` | Maximum number of processes |

Docker writes cgroup config under `/sys/fs/cgroup/`. `docker stats` reads live values from there.

---

## Networking Modes

### Bridge (default)
Docker creates a virtual Ethernet bridge (`docker0`) on the host. Each container gets a `veth` pair; one end attaches to the bridge, the other to the container's `eth0`. NAT rules (iptables MASQUERADE) allow outbound traffic.

```bash
docker run --network bridge nginx           # default
docker network create my-net               # custom bridge
docker run --network my-net nginx
```

Custom bridges support **automatic DNS resolution by container name** — the default `docker0` bridge does not.

### Host
Container shares the host's network stack. No isolation, no NAT — best throughput, no port mapping needed. Useful for performance-critical workloads.

```bash
docker run --network host nginx
```

### None
No network interfaces (except loopback). Full network isolation.

```bash
docker run --network none alpine
```

### Overlay
Multi-host networking for Docker Swarm or Kubernetes. Uses VXLAN encapsulation (UDP port 4789) to tunnel packets between hosts. Each overlay network has its own subnet.

```bash
docker network create --driver overlay --attachable my-overlay
```

### Macvlan
Assigns a real MAC address to the container, making it appear as a physical device on the network. Useful for legacy apps that expect to be on the LAN directly.

---

## Volumes

Volumes are the preferred mechanism for persisting data outside the container lifecycle.

| Type | Description |
|------|-------------|
| **Named volume** | Managed by Docker (`/var/lib/docker/volumes/`); survives container deletion |
| **Bind mount** | Maps a specific host path into the container |
| **tmpfs mount** | In-memory only; useful for secrets/temp data |

```bash
# Named volume
docker volume create pgdata
docker run -v pgdata:/var/lib/postgresql/data postgres

# Bind mount
docker run -v /host/path:/container/path nginx

# tmpfs
docker run --tmpfs /tmp:rw,size=64m alpine
```

Volumes are not included in `docker commit` snapshots — data stored in volumes is decoupled from image layers.

---

## Multi-Stage Builds

Multi-stage builds reduce final image size by discarding build-time dependencies:

```dockerfile
# Stage 1: build
FROM golang:1.22 AS builder
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o /bin/app ./cmd/app

# Stage 2: runtime
FROM gcr.io/distroless/static-debian12
COPY --from=builder /bin/app /app
ENTRYPOINT ["/app"]
```

Result: final image contains only the compiled binary — no Go toolchain, no source code, no shell.

Target a specific stage with `docker build --target builder .` for debugging.

---

## BuildKit

BuildKit is Docker's next-generation build engine (default since Docker 23.0, opt-in with `DOCKER_BUILDKIT=1` on older versions).

Key improvements over classic builder:

| Feature | Benefit |
|---------|---------|
| Parallel stage execution | Independent stages build concurrently |
| Cache mounts | `--mount=type=cache` persists package caches between builds |
| Secret mounts | `--mount=type=secret` injects secrets at build time without baking them into layers |
| SSH mounts | `--mount=type=ssh` forwards SSH agent for private repos |
| Inline cache | `--cache-from` / `--cache-to` for registry-backed build caches |

```dockerfile
# Cache apt packages across builds
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && apt-get install -y curl

# Use a secret at build time (never appears in layers)
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc \
    npm install
```

Build with secret:
```bash
docker build --secret id=npmrc,src=$HOME/.npmrc .
```

---

## Dockerfile Instructions Reference

| Instruction | Notes |
|-------------|-------|
| `FROM` | Base image; every Dockerfile starts here. `FROM scratch` = empty base |
| `RUN` | Executes command and creates a new layer |
| `COPY` | Copies files from build context into image |
| `ADD` | Like `COPY` but also handles URLs and auto-extracts tar archives |
| `CMD` | Default command; overridden by `docker run <image> <cmd>` |
| `ENTRYPOINT` | Fixed executable; `CMD` becomes its arguments |
| `ENV` | Persists into running container environment |
| `ARG` | Build-time variable only; not available at runtime |
| `EXPOSE` | Documents which port; does not publish — use `-p` at runtime |
| `VOLUME` | Declares a mount point; Docker auto-creates a named volume if none is provided |
| `WORKDIR` | Sets working directory for subsequent instructions |
| `USER` | Sets UID/GID for subsequent instructions and container runtime |
| `HEALTHCHECK` | Defines a command Docker uses to test container health |
| `LABEL` | Metadata key-value pairs attached to the image |

CMD vs ENTRYPOINT behavior:

```dockerfile
ENTRYPOINT ["nginx"]
CMD ["-g", "daemon off;"]
# → runs: nginx -g "daemon off;"
# docker run <image> -t → runs: nginx -t  (CMD overridden, ENTRYPOINT kept)
```
