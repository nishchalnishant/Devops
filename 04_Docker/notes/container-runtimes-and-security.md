# Container Runtimes & Security

## The Container Runtime Landscape

For most of Docker's history, "Docker" meant one thing: the Docker daemon (`dockerd`) that built and ran containers. But Kubernetes needed a standardized interface, and security requirements demanded new isolation models.

**The Modern Runtime Stack:**

```
Application Layer (what you interact with):
  docker CLI | nerdctl | crictl | kubectl
       │
       ▼
High-Level Runtime (manages images, containers):
  containerd | CRI-O | Docker Engine
       │
       ▼
Low-Level Runtime (creates namespaces, cgroups):
  runc | crun | Kata Containers | gVisor
       │
       ▼
Linux Kernel (namespaces, cgroups, seccomp, AppArmor)
```

**Why the split matters:**
- **Kubernetes doesn't need Docker** — it only needs a CRI-compatible runtime (containerd, CRI-O)
- **Security runtimes** (gVisor, Kata) swap in at the low level without changing your workflow
- **Debugging** requires knowing which layer is responsible: image issues (high-level) vs. isolation issues (low-level)

This document covers runtime architecture, security hardening, and supply chain security for containerized workloads.

***

## Container Runtime Architecture

```
kubectl apply (Pod spec)
    │
    ▼
kube-apiserver → stores in etcd
    │
    ▼
kubelet on node
    │  implements CRI (Container Runtime Interface) — gRPC
    ▼
High-level runtime (containerd or CRI-O)
    │  pulls images, manages snapshots, sets up networking via CNI
    ▼
containerd-shim-runc-v2 (per-container process)
    │  keeps container running even if containerd restarts
    ▼
runc (OCI runtime)
    │  creates namespaces, cgroups, pivot_root
    ▼
Container process (PID 1 in new namespaces)
```

### Linux primitives under the hood

| Primitive | What it isolates |
|-----------|-----------------|
| `pid` namespace | Process IDs (container can't see host PIDs) |
| `net` namespace | Network interfaces, routing, iptables |
| `mnt` namespace | Filesystem mount points |
| `uts` namespace | Hostname and domain name |
| `ipc` namespace | SysV IPC, POSIX message queues |
| `user` namespace | UID/GID mapping (rootless containers) |
| `cgroup` namespace | cgroup hierarchy visibility |
| **cgroups v2** | Resource limits: CPU, memory, blkio, pids |

```bash
# See namespaces of a running container
PID=$(docker inspect --format '{{.State.Pid}}' mycontainer)
ls -la /proc/$PID/ns/

# Inspect cgroup limits
cat /sys/fs/cgroup/system.slice/docker-<id>.scope/memory.max
cat /sys/fs/cgroup/system.slice/docker-<id>.scope/cpu.max

# Run runc directly (what Docker/containerd call internally)
runc spec > config.json   # generate OCI runtime spec
runc run mycontainer      # launch from bundle
```

***

## containerd — Internals

```bash
# containerd CLI (lower level than docker)
ctr images pull docker.io/library/ubuntu:22.04
ctr containers create docker.io/library/ubuntu:22.04 my-container
ctr tasks start my-container
ctr tasks exec --exec-id debug --tty my-container /bin/bash
ctr tasks kill my-container
ctr containers delete my-container

# nerdctl — Docker-compatible CLI for containerd
nerdctl run --rm -it ubuntu:22.04 bash
nerdctl build -t myapp:latest .
nerdctl push myregistry.io/myapp:latest

# crictl — CRI-level debugging (what kubelet sees)
crictl pods                          # list pod sandboxes
crictl images                        # list images on node
crictl inspect <container-id>        # full container spec
crictl logs <container-id>
crictl exec -it <container-id> bash
```

### Image layers and snapshots

```bash
# containerd stores images as snapshots (overlayfs layers)
# Layer: an immutable, content-addressed tarball (OCI image spec)
# Snapshot: an active overlay mount for a running container

# View image layers
docker image inspect myapp:latest --format '{{.RootFS.Layers}}'

# Inspect overlay filesystem for a running container
docker inspect --format '{{.GraphDriver.Data}}' mycontainer
# Shows: LowerDir (read-only layers) + UpperDir (writable) + MergedDir

# Manual overlay mount (what containerd does)
mount -t overlay overlay \
  -o lowerdir=/layer3:/layer2:/layer1,\
     upperdir=/container/upper,\
     workdir=/container/work \
  /container/merged
```

***

## Secure Sandboxing — gVisor and Kata

### gVisor

```
Application
    │  syscall
    ▼
Sentry (gVisor user-space kernel, written in Go)
    │  intercepts + validates syscall
    │  implements ~200 of ~400+ Linux syscalls
    ▼  (only safe, filtered syscalls reach host)
Host Linux kernel
    │  minimal attack surface
    ▼
Hardware
```

```yaml
# RuntimeClass for gVisor
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  name: gvisor
handler: runsc     # runsc = gVisor's OCI runtime
***
# Use gVisor for untrusted workloads
apiVersion: v1
kind: Pod
spec:
  runtimeClassName: gvisor
  containers:
  - name: untrusted-workload
    image: user-submitted-code:latest
```

**gVisor gotchas:** Not all syscalls are implemented. Some applications (certain JVM versions, FUSE mounts, raw sockets) fail inside gVisor. Test your workloads.

### Kata Containers

```
Container → OCI runtime (kata-runtime)
                │ creates lightweight VM (QEMU/firecracker)
                ▼
            Guest kernel (minimal Linux, ~4MB)
                │ container process runs inside VM
                ▼ virtio device drivers
            Host kernel
                │ VM isolation = true hardware boundary
                ▼
            Hardware
```

```yaml
# RuntimeClass for Kata with Firecracker (AWS) for production
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  name: kata-fc
handler: kata-fc

overhead:
  podFixed:
    memory: "256Mi"    # VM overhead per pod
    cpu: "250m"
```

***

## Image Security — Distroless and Minimal Images

### Multi-stage build with distroless final stage

```dockerfile
# Stage 1: build (has tools, compilers, etc.)
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --target /app/deps
COPY src/ .

# Stage 2: minimal runtime (distroless — no shell, no package manager)
FROM gcr.io/distroless/python3-debian12:nonroot
WORKDIR /app
COPY --from=builder /app /app
COPY --from=builder /app/deps /app/deps
ENV PYTHONPATH=/app/deps
USER nonroot
ENTRYPOINT ["python3", "main.py"]
```

```dockerfile
# Go: fully static binary in scratch
FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags='-w -s' -o server ./cmd/server

FROM scratch
COPY --from=builder /app/server /server
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
USER 65534   # nobody
ENTRYPOINT ["/server"]
```

### Chainguard Wolfi-based images

```dockerfile
# Chainguard images have near-zero CVE count (daily package updates)
FROM cgr.dev/chainguard/python:3.12-dev AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

FROM cgr.dev/chainguard/python:3.12
COPY --from=builder /app /app
CMD ["python", "/app/main.py"]
```

***

## securityContext — Hardening Reference

```yaml
apiVersion: v1
kind: Pod
spec:
  # Pod-level security context
  securityContext:
    runAsNonRoot: true          # reject if image USER is root
    runAsUser: 1000
    runAsGroup: 3000
    fsGroup: 2000               # volume mounts owned by this GID
    fsGroupChangePolicy: OnRootMismatch  # faster; only chown if needed
    seccompProfile:
      type: RuntimeDefault      # apply default seccomp profile (Linux syscall filter)
    supplementalGroups: [4000]

  containers:
  - name: app
    image: myapp:latest
    # Container-level (overrides pod-level)
    securityContext:
      allowPrivilegeEscalation: false   # no sudo, no setuid escalation
      readOnlyRootFilesystem: true       # container can't write to its own FS
      capabilities:
        drop: [ALL]
        add: [NET_BIND_SERVICE]          # only if binding port < 1024
      seccompProfile:
        type: Localhost
        localhostProfile: profiles/my-app.json   # custom seccomp profile
    
    # Writable scratch areas for readOnlyRootFilesystem
    volumeMounts:
    - name: tmp
      mountPath: /tmp
    - name: cache
      mountPath: /app/cache

  volumes:
  - name: tmp
    emptyDir: {}
  - name: cache
    emptyDir:
      medium: Memory   # RAM-backed — faster, destroyed on pod termination
      sizeLimit: 256Mi
```

### Pod Security Standards (replaced PSP)

```yaml
# Label namespace to enforce pod security level
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    pod-security.kubernetes.io/enforce: restricted   # enforce restricted profile
    pod-security.kubernetes.io/warn: restricted       # warn on restricted violations
    pod-security.kubernetes.io/audit: restricted      # audit log violations

# restricted profile requires:
# - non-root user
# - allowPrivilegeEscalation: false
# - readOnlyRootFilesystem: true (in restricted)
# - ALL capabilities dropped
# - seccompProfile set
# - no hostPath volumes, no host networking, no host PIDs
```

***

## Image Scanning in CI/CD

```bash
# Trivy — comprehensive scanner
trivy image myapp:latest \
  --severity HIGH,CRITICAL \
  --exit-code 1 \
  --ignore-unfixed \
  --format sarif \
  --output trivy-results.sarif

# Scan during build (before push)
trivy image --input myapp.tar \
  --severity CRITICAL \
  --exit-code 1

# Generate SBOM and scan it separately
trivy image myapp:latest --format spdx-json -o sbom.json
grype sbom:./sbom.json --fail-on high

# Trivy plugin for Kubernetes (scan running workloads)
trivy k8s --report summary cluster
trivy k8s -n production --scanners vuln,config,secret all
```

### Dockerfile best practices scanner

```bash
# Hadolint — Dockerfile linter
hadolint Dockerfile
docker run --rm -i hadolint/hadolint < Dockerfile

# Common violations:
# DL3008: Pin versions in apt-get install
# DL3009: Delete apt-get lists after install
# DL4006: Set SHELL option -o pipefail with RUN commands using pipe
# SC2086: Double quote to prevent globbing (shell lint)
```

***

## Rootless Docker and Podman

```bash
# Rootless Docker — Docker daemon runs as non-root user
dockerd-rootless-setuptool.sh install
export DOCKER_HOST=unix://$XDG_RUNTIME_DIR/docker.sock
docker run --rm hello-world

# Podman — daemonless, rootless by default
podman run --rm -it ubuntu:22.04 bash
podman build -t myapp:latest .
podman generate kube mycontainer > pod.yaml   # generate Kubernetes YAML from container
podman play kube pod.yaml                     # run Kubernetes YAML with Podman

# Buildah — OCI image builder (no daemon, rootless)
buildah from ubuntu:22.04
buildah run mycontainer -- apt-get update
buildah copy mycontainer ./app /app
buildah config --entrypoint '["/app/start.sh"]' mycontainer
buildah commit mycontainer myapp:latest
buildah push myapp:latest docker://myregistry.io/myapp:latest
```

***

## Key Gotchas

| Gotcha | Detail |
|--------|--------|
| `USER` in Dockerfile vs `runAsUser` in Pod spec | Pod spec overrides the Dockerfile USER — `runAsNonRoot: true` catches this mismatch |
| `readOnlyRootFilesystem` breaks apps writing to /tmp | Always add an `emptyDir` volume mounted at `/tmp` and wherever else the app writes |
| capabilities `drop: ALL` breaks network tools | Removing ALL includes `NET_RAW`; tools like `ping` stop working — acceptable in production |
| gVisor doesn't support all syscalls | `io_uring`, `perf_event_open`, certain memory-mapped operations fail — test your workload |
| Kata requires nested virtualization | Running Kata inside a VM (like EC2) requires `metal` instances or nested virt support |
| distroless images have no shell | `kubectl exec` and `docker exec` fail — use ephemeral debug containers: `kubectl debug -it <pod> --image=busybox` |
| `fsGroup` chowns entire volume on mount | On large volumes, this adds startup latency — use `fsGroupChangePolicy: OnRootMismatch` |
| Multi-stage `COPY --from` only copies specified paths | Unlike `docker cp`, you must explicitly enumerate every path to copy from builder stage |
| Overlay disk space is on the host | Container layer writes go to `overlayfs` on the node — heavy write workloads fill node disks |
