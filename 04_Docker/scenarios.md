# Production Scenarios & Troubleshooting Drills (Senior Level)

## Level 1: Container Lifecycle & Debugging

### Scenario 1: "Too Many Open Files"
**Symptom:** Nginx container fails with `socket: too many open files`.
**Fix:** Increase the `ulimit` in the container runtime:
```yaml
ulimits:
  nofile:
    soft: 65535
    hard: 65535
```

### Scenario 2: The 5GB Image Crisis
**Symptom:** CI pipelines take 15 minutes to pull the image.
**Fix:** 
1. Use **Multi-Stage Builds**.
2. Use `.dockerignore` to exclude `.git` and `node_modules`.
3. Use `python:3.9-slim` instead of `python:3.9`.

### Scenario 3: Container A cannot talk to Container B
**Symptom:** Microservices on the same host can't communicate.
**Diagnosis:** Check if they are on a User-Defined Bridge network. The default `bridge` does not support DNS resolution by container name.
**Fix:** `docker network create my-net` and connect both containers.

## Level 2: Security & Supply Chain

### Scenario 4: Container Escape Protection
**Symptom:** Security audit warns about "Privileged Containers."
**Fix:** 
- Use `--cap-drop=ALL` and only add back exactly what is needed (e.g., `NET_BIND_SERVICE`).
- Use `--read-only` root filesystem.
- Use **User Namespaces** to map the container's root to a non-privileged user on the host.

### Scenario 5: Docker-in-Docker (DinD) Performance
**Symptom:** Jenkins building Docker images inside a container is extremely slow.
**Fix:** Do not use full DinD. Mount the host's Docker socket: `-v /var/run/docker.sock:/var/run/docker.sock`.

### Scenario 6: Image Signing with Sigstore/Cosign
**Symptom:** Need to ensure that only images built in CI run in Production.
**Fix:** Use `cosign sign <image_digest>` in CI. Use a Kubernetes Admission Controller to verify the signature before pulling.

### Scenario 7: BuildKit Optimization
**Symptom:** Docker builds are not using cache even when nothing changed.
**Fix:** Use `DOCKER_BUILDKIT=1` and `RUN --mount=type=cache,target=/root/.npm` to persist package manager caches between builds.

### Scenario 8: Rootless Docker Security
**Symptom:** Running Docker as root is a security risk.
**Fix:** Install `docker-ce-rootless-extras`. This allows the Docker daemon to run under a standard user, preventing container escapes from gaining root on the host.

***

## Level 3: Runtime Operations & SRE

### Scenario 9: The "Zombie" Process Leak (PID 1 Problem)
**Symptom:** Running `ps aux` on the host shows thousands of defunct processes inside a specific container.
**Diagnosis:** The application running as PID 1 in the container does not have a "Reaping" logic to handle child processes that have finished.
**Fix:** Use an init process like **tini** (`--init` flag in Docker or adding `tini` to your Dockerfile).

### Scenario 10: Graceful Shutdown Failure (SIGTERM ignored)
**Symptom:** `docker stop` takes 10 seconds every time before killing the container.
**Diagnosis:** The application is not receiving the `SIGTERM` signal. This usually happens when you use the "Shell form" (`CMD my-app`) instead of "Exec form" (`CMD ["my-app"]`) in the Dockerfile.
**Fix:** Use the Exec form. This ensures your app is PID 1 and receives signals directly from Docker.

### Scenario 11: The "Read-Only" Root FS Breach
**Symptom:** An attacker gained access but cannot modify the application code because you used `--read-only`.
**Diagnosis:** App still needs to write to `/tmp` or `/logs`.
**Fix:** Use **tmpfs** mounts for specific writable paths: `docker run --read-only --tmpfs /tmp --tmpfs /run my-app`.

### Scenario 12: Docker Socket Mounting Security Risk
**Symptom:** A container with access to `/var/run/docker.sock` has been compromised.
**Diagnosis:** The attacker can now control the entire host's Docker daemon, essentially gaining root access to the host.
**Fix:** Never mount the Docker socket unless absolutely necessary (e.g., for Jenkins). Use **Docker Contexts** or **Sysbox** for better isolation.

### Scenario 13: OOM Kill Diagnosis in Containers
**Symptom:** Container restarts with exit code 137.
**Diagnosis:** Check `/sys/fs/cgroup/memory/memory.failcnt` or `docker inspect <id> --format='{{.State.OOMKilled}}'`.
**Fix:** Increase memory limits or profile the application for memory leaks.

### Scenario 14: UID/GID Mismatch in Volume Mounts
**Symptom:** Container cannot write to a mounted volume (`Permission Denied`), even though permissions on the host look correct.
**Diagnosis:** The user inside the container (e.g., `www-data` with UID 33) does not match the owner of the folder on the host.
**Fix:** Use the `--user` flag at runtime or ensure the Dockerfile creates a user with a specific UID that matches the host's volume owner.

### Scenario 15: Log File Disk Exhaustion
**Symptom:** The host's disk is full, and the culprit is `/var/lib/docker/containers/<id>/<id>-json.log`.
**Diagnosis:** The default `json-file` log driver has no size limit.
**Fix:** Configure log rotation in `daemon.json`:
```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

### Scenario 16: Registry Garbage Collection Cleanup
**Symptom:** Your private Docker Registry is using 2TB of storage even though you only have 50 images.
**Diagnosis:** Docker Registry does not automatically delete "orphaned" layers after you push a new version of an image with the same tag.
**Fix:** Run the registry garbage collector: `bin/registry garbage-collect /etc/docker/registry/config.yml`.

### Scenario 17: OverlayFS "Lowerdir" Corruption
**Symptom:** Container fails to start with "error creating overlay mount to /var/lib/docker/overlay2/...: invalid argument".
**Diagnosis:** Corruption in the underlying filesystem or a kernel incompatibility with the Overlay2 driver.
**Fix:** Clean up the overlay storage: `docker system prune -a`. In extreme cases, stop Docker, delete `/var/lib/docker/overlay2`, and restart (Note: this deletes all local images).


### Scenario 18: AppArmor "Permission Denied" on Mount
**Symptom:** `docker run` fails to mount a volume with `permission denied`, even as root.
**Diagnosis:** The default AppArmor profile `docker-default` is blocking the specific mount type.
**Fix:** Create a custom AppArmor profile or use `--security-opt apparmor=unconfined` (only for debugging!).

### Scenario 19: BuildKit "Secret" leak in Metadata
**Symptom:** You used `--mount=type=secret`, but the secret is visible in the image history.
**Diagnosis:** You copied the secret into a file during the build process instead of just using it in the `RUN` command.
**Fix:** Ensure the secret is only accessed via `/run/secrets/` and never written to a layer.

***

## Level 2: Networking & Image Management

### Scenario 4: Container Cannot Reach External Internet

**Prompt:** A newly deployed container on a fresh Docker host can reach other containers on the same network but cannot reach `8.8.8.8` or any external host. `ping google.com` fails with "Name or service not known."

**Diagnosis:**
```bash
# Test from inside the container
docker exec -it mycontainer sh
ping 8.8.8.8         # test IP connectivity
ping google.com      # test DNS

# Check Docker's iptables rules
sudo iptables -t nat -L POSTROUTING -n -v
# Should show: MASQUERADE rule for the docker0 bridge subnet

# Check IP forwarding
cat /proc/sys/net/ipv4/ip_forward   # must be 1

# Check docker daemon config
cat /etc/docker/daemon.json
```

**Root causes:**

1. **IP forwarding disabled:**
```bash
echo 1 > /proc/sys/net/ipv4/ip_forward
sysctl -w net.ipv4.ip_forward=1
echo "net.ipv4.ip_forward=1" >> /etc/sysctl.d/99-docker.conf
```

2. **iptables FORWARD chain default DROP (common after firewalld/ufw install):**
```bash
iptables -A FORWARD -i docker0 -o eth0 -j ACCEPT
iptables -A FORWARD -i eth0 -o docker0 -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables -t nat -A POSTROUTING -s 172.17.0.0/16 ! -o docker0 -j MASQUERADE
# Restart Docker to reapply its iptables rules
systemctl restart docker
```

3. **DNS resolution failing — custom `daemon.json` DNS:**
```json
{
  "dns": ["8.8.8.8", "8.8.4.4"]
}
```

***

### Scenario 5: Docker Image Build Cache Invalidated on Every CI Run

**Prompt:** A Dockerfile builds a Node.js application. On CI, every build runs `npm install` from scratch (2+ minutes) even though `package.json` hasn't changed. The cache is being invalidated unexpectedly.

**Problematic Dockerfile:**
```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY . .               # copies everything including src files
RUN npm install        # cache busted whenever ANY file changes
```

**Fix — separate dependency installation from source copy:**
```dockerfile
FROM node:20-alpine
WORKDIR /app
# Copy ONLY dependency manifests first
COPY package.json package-lock.json ./
# This layer is only invalidated when package.json or lock file changes
RUN npm ci --only=production
# Copy source code after — doesn't bust the npm install cache
COPY src/ ./src/
COPY tsconfig.json ./
RUN npm run build
```

**CI optimization — export and restore Docker layer cache:**
```yaml
# GitHub Actions with Buildx cache
- uses: docker/build-push-action@v5
  with:
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

**Key insight:** Docker cache is invalidated for a layer when the instruction itself changes, any `COPY`/`ADD` source file changes, or any preceding layer's cache is invalidated. Order matters: put the most stable layers first, most volatile (source code) last.

***

### Scenario 6: Container OOM Killed — No Application Error Logs

**Prompt:** A Java service container exits with code 137 every few hours. The application logs show no exceptions or errors before exit. Container events show `OOMKilled: true`.

**Diagnosis:**
```bash
# Confirm OOM kill
docker inspect mycontainer | jq '.[0].State'
# "OOMKilled": true, "ExitCode": 137

# Check kernel OOM events
dmesg | grep -i "oom\|killed process" | tail -20

# Check the current memory limit and usage
docker stats mycontainer --no-stream
docker inspect mycontainer | jq '.[0].HostConfig.Memory'

# For Java specifically — what JVM sees vs. what Docker allows
docker exec -it mycontainer java -XX:+PrintFlagsFinal -version 2>&1 | grep HeapSize
```

**Root cause — JVM unaware of cgroup memory limits (Java < 10):**

Old JVM versions read `/proc/meminfo` (host total memory) to size the heap, ignoring cgroup limits. A container with a 2GB limit on a 64GB host gets a JVM default heap of ~16GB — OOM kill is inevitable.

**Fixes:**

1. **Java 11+ (auto cgroup-aware):** JVM automatically reads cgroup v2 limits. No flags needed.
2. **Java 8u191+ with `-XX:+UseContainerSupport`:**
```dockerfile
ENV JAVA_OPTS="-XX:+UseContainerSupport -XX:MaxRAMPercentage=75.0"
```
3. **Explicit heap — safest:**
```dockerfile
ENV JAVA_OPTS="-Xms512m -Xmx1536m"
# Leave ~25% headroom for off-heap (Metaspace, direct buffers, GC overhead)
```

**Set container memory limit with headroom:**
```bash
docker run -m 2g --memory-swap 2g myapp  # --memory-swap = memory+swap; setting equal disables swap
```

***

### Scenario 7: `docker build` Fails with "No Space Left on Device" but Disk is 60% Full

**Prompt:** `docker build` fails mid-build with "no space left on device." `df -h` shows root partition is 60% full. A colleague's build succeeded on the same machine an hour ago.

**Diagnosis:**
```bash
# Docker uses /var/lib/docker — check it specifically
df -h /var/lib/docker

# Check Docker's internal space accounting
docker system df

# Check inodes (can be exhausted independently of blocks)
df -i /var/lib/docker

# List dangling images (untagged, unreferenced)
docker images -f dangling=true

# List stopped containers consuming layers
docker ps -a --filter status=exited
```

**Root causes:**

1. **Overlay2 storage driver leaking layers:** Each failed build leaves intermediate layers. Clean up:
```bash
docker builder prune -f         # remove build cache
docker image prune -f           # remove dangling images
docker system prune --volumes   # nuclear option — removes all unused resources
```

2. **Inode exhaustion (not block exhaustion):** Overlay2 creates many small files. `df -i` shows 100% inode usage while `df -h` shows free blocks.
```bash
# Find inode hogs
for i in /var/lib/docker/overlay2/*/; do
  find "$i" | wc -l
done | sort -rn | head -5
```
Fix: tune filesystem with larger inode ratio (`mkfs.ext4 -i 4096`) on next rebuild, or migrate to XFS which has dynamic inode allocation.

3. **Build cache growing unbounded in CI:** Add `docker builder prune --keep-storage 10GB -f` as a CI step or cron job.

***

### Scenario 8: Multi-Stage Build Produces Correct Image Locally but Wrong Binary on CI

**Prompt:** A Go application's Docker multi-stage build works locally (produces a Linux binary). On CI (GitHub Actions, ubuntu-latest), the final container crashes with "exec format error" — the binary format doesn't match the container architecture.

**Diagnosis:**
```bash
# Check the binary format
docker run --rm myapp file /app/server
# "ELF 64-bit LSB executable, ARM aarch64" — developer built on M1 Mac
# "ELF 64-bit LSB executable, x86-64" — expected

# Check the platform of the built image
docker inspect myapp | jq '.[0].Architecture'
```

**Root cause:** Developer built on an Apple M1 (arm64). `docker build` without `--platform` flag produces an arm64 image. CI runs on x86_64. Even if the CI machine can run arm64 via emulation, the prod container (x86_64) cannot.

**Fix — explicit platform in Dockerfile and build command:**
```dockerfile
FROM --platform=linux/amd64 golang:1.22-alpine AS builder
WORKDIR /app
COPY . .
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o server ./cmd/server

FROM --platform=linux/amd64 gcr.io/distroless/static:nonroot
COPY --from=builder /app/server /server
ENTRYPOINT ["/server"]
```

```bash
# Build with explicit platform on CI
docker buildx build --platform linux/amd64 -t myapp:latest .
```

**Multi-arch build (produce both amd64 and arm64):**
```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --tag myregistry/myapp:latest \
  --push .
```

***

## Level 3: Production Operations

### Scenario 9: Container Keeps Restarting — CrashLoopBackOff Pattern

**Prompt:** A container restarts every 30 seconds. `docker logs mycontainer` shows the application starts cleanly and then exits with code 1. No error message. The application runs perfectly outside Docker.

**Diagnosis:**
```bash
# Get the last N lines before crash
docker logs --tail 50 mycontainer

# Check the entrypoint and CMD
docker inspect mycontainer | jq '.[0].Config | {Entrypoint, Cmd}'

# Run interactively to debug
docker run -it --entrypoint sh myimage
# Execute the actual command manually
```

**Common causes:**

1. **PID 1 problem — SIGTERM not handled:** Docker stops a container by sending SIGTERM to PID 1. If the entrypoint is a shell script that exec's the process, the process is PID 1 and receives SIGTERM. If it's not handled, it exits immediately (code 143). Use `exec` in shell scripts to replace the shell:
```bash
#!/bin/sh
exec java -jar /app/app.jar "$@"
# NOT: java -jar /app/app.jar "$@" (spawns as PID 2, shell ignores SIGTERM)
```
Or use `tini` as a proper init:
```dockerfile
RUN apk add --no-cache tini
ENTRYPOINT ["/sbin/tini", "--", "/app/entrypoint.sh"]
```

2. **Missing environment variable — silent exit:**
```bash
# Add set -euo pipefail to shell scripts
# Add explicit variable checks
: "${DATABASE_URL:?DATABASE_URL is required}"
```

3. **File permission mismatch — non-root user in distroless image:**
```bash
# Check what user the container runs as
docker inspect mycontainer | jq '.[0].Config.User'
# Verify file ownership matches
docker run --rm myimage ls -la /app/
```

***

### Scenario 10: Docker Compose Services Start Out of Order — Race Condition

**Prompt:** A `docker-compose.yml` defines a web service and a Postgres database. The web service crashes on startup because Postgres isn't ready to accept connections yet, even though `depends_on: db` is specified.

**Root cause:** `depends_on` only waits for the container to *start*, not for the service *inside* the container to be *ready*. The Postgres container starts in milliseconds but the postgres server takes 2-3 seconds to initialize.

**Fix 1 — `depends_on` with `condition: service_healthy`:**
```yaml
services:
  db:
    image: postgres:16
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5
      start_period: 10s

  web:
    image: myapp:latest
    depends_on:
      db:
        condition: service_healthy
```

**Fix 2 — application-level retry with exponential backoff (recommended defense-in-depth):**
```python
import time, psycopg2

def connect_with_retry(dsn, max_retries=10):
    for attempt in range(max_retries):
        try:
            return psycopg2.connect(dsn)
        except psycopg2.OperationalError:
            wait = 2 ** attempt
            print(f"DB not ready, retrying in {wait}s...")
            time.sleep(wait)
    raise RuntimeError("Database never became ready")
```

The application retry is essential even in production — healthcheck handles startup, retry handles transient network issues and rolling restarts.
