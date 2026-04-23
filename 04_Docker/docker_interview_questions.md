# Docker Interview Mastery (Senior Level)

This guide distills the core technical requirements and high-stakes scenario drills for Docker, optimized for Senior DevOps (4+ YOE) candidates. It moves beyond basic commands into architectural trade-offs and runtime security.

---

## 🏗️ Core Architecture & Fundamentals

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

---

## 🛠️ Practical Operations & Lifecycle

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

---

## 🚀 Advanced Scenarios & Troubleshooting

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

---

## 📦 Docker Compose & Orchestration

### 7. What is Docker Compose?
A tool for defining and running multi-container Docker applications using a `YAML` file. It allows you to manage the entire stack (web, db, cache) with a single command: `docker-compose up`.

### 8. Docker Swarm vs. Kubernetes
- **Docker Swarm:** Native clustering, easy to set up, suitable for smaller workloads.
- **Kubernetes:** More complex, highly extensible, the industry standard for enterprise-scale orchestration.

---

## 🎯 Quick Fire Interview Tips
- **Image Optimization:** Always mention multi-stage builds to reduce image size.
- **Security:** Run containers as non-root users.
- **Networking:** Understand the difference between `bridge`, `host`, and `none` drivers.
of load balancing across containers and hosts? How does it work?


---

