## Medium

**12. How do Docker layers work and why does layer ordering matter for build performance?**

Each Dockerfile instruction creates an immutable layer. Layers are cached — if an instruction's content and all preceding layers are unchanged, Docker reuses the cached layer. Ordering matters: put instructions that change frequently (e.g., `COPY app.py`) after instructions that change rarely (e.g., `RUN pip install -r requirements.txt`). This way, the expensive dependency installation is cached on most rebuilds.

**13. How do you reduce a Docker image from 800MB to 50MB?**

1. **Multi-stage build:** Use a build stage with full tooling; copy only the compiled binary into `FROM scratch` or `FROM alpine`.
2. **Minimal base:** Switch from `ubuntu:22.04` to `alpine:3.18` or Google's `distroless`.
3. **Remove build artifacts:** In the same RUN instruction, delete caches: `apt-get clean && rm -rf /var/lib/apt/lists/*`.
4. **Combine RUN instructions:** Each `RUN` creates a layer — combining them avoids intermediate layer bloat.
5. **`.dockerignore`:** Exclude unnecessary files from the build context.

**14. How do you handle secrets in Docker images?**

Never include secrets in a Dockerfile or image layer — they persist in the layer history even if deleted in a later layer. Options:
- **Build-time secrets (Docker BuildKit):** `RUN --mount=type=secret,id=api_key cat /run/secrets/api_key`. The secret is not stored in any layer.
- **Runtime injection:** Pass secrets as environment variables at `docker run` or mount them as files from a secrets manager.
- **Vault agent sidecar:** Container fetches its own secrets from HashiCorp Vault at startup.

**15. What is containerd and how does it relate to Docker?**

Containerd is a container runtime that manages the container lifecycle: image pulling, storage, and container execution. Docker is built on top of containerd — it adds the Docker CLI, image building, networking management, and Compose. Kubernetes uses containerd directly via the CRI (Container Runtime Interface), bypassing the Docker daemon layer. Docker Desktop still wraps containerd.

**16. What are the security risks of running containers as root and how do you prevent it?**

Running as root means a container escape gives the attacker full root on the host. Prevention:
- Set `USER nonroot` in the Dockerfile.
- Use `securityContext.runAsNonRoot: true` and `runAsUser: 1000` in Kubernetes Pod spec.
- Use `securityContext.readOnlyRootFilesystem: true` to prevent writes to the container filesystem.
- Drop Linux capabilities: `securityContext.capabilities.drop: ["ALL"]` and add back only what is needed.
- Use rootless containers (Podman, or Docker with rootless mode).

**17. How does Docker networking work with bridge mode in detail?**

When Docker starts, it creates a `docker0` virtual bridge interface on the host. Each container gets a `veth` pair: one end (`eth0`) in the container's network namespace, the other end attached to `docker0`. Containers on the same bridge can communicate via IP. Docker manages iptables NAT rules to allow containers to reach the internet (MASQUERADE). Port publishing (`-p 8080:80`) adds a DNAT iptables rule to redirect host port 8080 to the container's port 80.

---

