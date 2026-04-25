---
description: Easy interview questions for Docker fundamentals, images, and containers.
---

## Easy

**1. What is the difference between a Docker image and a container?**

An image is a read-only, layered filesystem snapshot — the blueprint. A container is a running instance of an image — it adds a writable layer on top and starts a process. Multiple containers can run from the same image simultaneously, each with their own isolated writable layer. Deleting a container does not delete its image.

**2. What is a Dockerfile?**

A Dockerfile is a text file containing a sequence of instructions that Docker uses to build an image, layer by layer. Each instruction (`FROM`, `COPY`, `RUN`, `CMD`, etc.) creates a new layer. Docker caches each layer — if the instruction and its inputs haven't changed, the cached layer is reused, making subsequent builds faster.

**3. What is the difference between `CMD` and `ENTRYPOINT`?**

`CMD` specifies default arguments that can be overridden at `docker run`. `ENTRYPOINT` specifies the command that always runs — it's the main process. When both are set, `CMD` provides default arguments to `ENTRYPOINT`. Use `ENTRYPOINT ["python"]` + `CMD ["app.py"]` to allow `docker run my-image other_script.py` to override the script while always using Python.

**4. What is the difference between `COPY` and `ADD` in a Dockerfile?**

`COPY` copies files from the build context to the image — straightforward and predictable. `ADD` has implicit behaviors: it auto-extracts `.tar.gz` archives and can fetch files from URLs. `ADD` is considered a gotcha because of these implicit side effects. Prefer `COPY` for all regular file copying; use `ADD` only when you specifically need its tar-extraction behavior. For downloading files, prefer `RUN curl` + `RUN tar` for explicit control.

**5. What is a Docker volume and why use it instead of the container's writable layer?**

A volume is a Docker-managed storage area outside the container's writable layer. Volumes persist after the container is deleted, can be shared between containers, and offer better I/O performance because they bypass the copy-on-write filesystem. The container's writable layer is ephemeral — data written there is lost when the container is removed. Use volumes for databases, logs, and any data that must survive container restarts.

**6. What is the difference between `docker stop` and `docker kill`?**

`docker stop` sends `SIGTERM` to the container's main process (PID 1), giving it time to clean up gracefully. After a timeout (default 10 seconds), it sends `SIGKILL`. `docker kill` sends `SIGKILL` immediately — no cleanup. Always prefer `docker stop` for databases and stateful applications; use `docker kill` only when a container is stuck and not responding to SIGTERM.

**7. What does `docker ps -a` show vs `docker ps`?**

`docker ps` lists only running containers. `docker ps -a` (or `--all`) lists all containers including stopped and exited ones. Useful for debugging — an exited container retains its logs and filesystem until removed with `docker rm`. `docker ps -q` outputs only container IDs (useful for scripting: `docker rm $(docker ps -aq)` removes all stopped containers).

**8. What is a multi-stage Dockerfile and why is it valuable?**

A multi-stage Dockerfile uses multiple `FROM` statements. Earlier stages can contain build tools (compilers, package managers); only the final stage (which becomes the actual image) copies the built artifacts. Result: the production image contains only the runtime — no build tools, no source code, dramatically smaller and more secure. Example: a Go binary built with the `golang` image but shipped in `scratch` (empty) is only ~10MB vs 800MB.

**9. How does Docker networking work by default between containers?**

Containers on the same Docker bridge network can communicate using each other's container name as a hostname (Docker's built-in DNS). Containers on the default `bridge` network cannot resolve names — only IP addresses work, which change on every restart. Use `docker network create my-net` and `--network my-net` to get DNS-based discovery. Containers on different custom networks are isolated from each other.

**10. What is `.dockerignore` and why does it matter?**

`.dockerignore` lists files and directories to exclude from the build context sent to the Docker daemon. Without it, Docker sends everything in the directory — including `.git/` (potentially hundreds of MB), `node_modules/`, and test files. This wastes time and can accidentally leak sensitive data into the image. Always add `**/__pycache__`, `.git`, `node_modules`, `*.log`, `.env` to `.dockerignore`.

**11. What is the difference between `docker run -d` and `docker run`?**

`docker run` (without `-d`) runs the container in the foreground — terminal is attached to the container's stdout/stderr. `docker run -d` (detached) starts the container in the background and immediately returns the container ID. Use `-d` for long-running services (web servers, databases); use the foreground mode for one-off commands or interactive sessions (`docker run -it ubuntu bash`).

**12. How do you inspect a running container's environment and logs?**

```bash
docker logs my-container              # Print stdout/stderr
docker logs -f my-container           # Follow (tail -f equivalent)
docker logs --tail=100 my-container   # Last 100 lines
docker exec my-container env          # Print environment variables
docker exec -it my-container bash     # Interactive shell
docker inspect my-container           # Full JSON metadata (mounts, network, env)
```
