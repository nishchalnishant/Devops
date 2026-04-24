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

