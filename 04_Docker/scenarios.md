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
