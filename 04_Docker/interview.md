# Docker — Interview Questions

All difficulty levels combined.

---

## Easy

**1. What is a Docker image vs. a container?**

A Docker image is a read-only template containing the application code, dependencies, and OS layers. A container is a running instance of an image — it adds a writable layer on top.

**2. What is a Dockerfile?**

A Dockerfile is a text file containing a sequence of instructions to build a Docker image. Each instruction creates a layer in the image.

**3. What does `COPY` vs `ADD` do in a Dockerfile?**

`COPY` copies local files into the image. `ADD` does the same but additionally can extract tar archives and fetch URLs. Prefer `COPY` for clarity — use `ADD` only when you need extraction.

**4. What is the difference between `CMD` and `ENTRYPOINT`?**

`ENTRYPOINT` defines the main executable that always runs. `CMD` provides default arguments. When used together, `CMD` can be overridden at `docker run` while `ENTRYPOINT` stays fixed.

**5. What is a Docker volume and why is it used?**

Volumes provide persistent storage outside the container's writable layer. Container data written to a volume persists after the container stops or is removed.

**6. What is Docker Compose?**

Docker Compose uses a YAML file (`docker-compose.yml`) to define and run multi-container applications. `docker compose up` starts all services defined in the file with correct networking and dependencies.

**7. What is the difference between `docker stop` and `docker kill`?**

`docker stop` sends SIGTERM, allowing the process to shut down gracefully. `docker kill` sends SIGKILL, which immediately terminates the process.

**8. What is a multi-stage build and why is it used?**

A multi-stage Dockerfile uses multiple `FROM` instructions. Early stages compile or build the application; the final stage copies only the built artifact into a minimal base image. This produces small, lean production images without build tools.

**9. What is a Docker network and what are the default types?**

Docker networking connects containers. Default types: `bridge` (containers on the same host can communicate via a virtual bridge), `host` (container shares the host's network namespace), `none` (no networking).

**10. What is the `.dockerignore` file?**

It specifies files and directories to exclude from the build context sent to the Docker daemon. Excluding `.git`, `node_modules`, and logs reduces build time and prevents secrets from being baked into the image.

**11. What is a base image and what makes a good one for production?**

A base image is the starting point for your Docker image (`FROM ubuntu:22.04`). For production: prefer small images (`alpine`, `distroless`, `debian-slim`) to reduce attack surface, minimize image size, and speed up pulls.

---

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
