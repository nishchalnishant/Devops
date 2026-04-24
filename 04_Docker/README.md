# Docker & Containerization

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
