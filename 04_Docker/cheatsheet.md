# Docker — Commands Cheat Sheet

## Build

```bash
docker build -t myapp:latest .                         # build from Dockerfile in current dir
docker build -t myapp:latest -f path/Dockerfile .      # specify Dockerfile path
docker build --no-cache -t myapp:latest .              # ignore all cached layers
docker build --target builder -t myapp:dev .           # stop at named stage
docker build --build-arg ENV=prod -t myapp:prod .      # pass build-arg
docker build --secret id=npmrc,src=~/.npmrc .          # BuildKit secret mount
docker build --ssh default -t myapp .                  # forward SSH agent (BuildKit)
docker build --platform linux/amd64,linux/arm64 .      # multi-arch (requires buildx)
docker build --pull -t myapp .                         # always pull base image

# BuildKit cache export/import (CI cache sharing)
docker build \
  --cache-from type=registry,ref=myrepo/myapp:buildcache \
  --cache-to   type=registry,ref=myrepo/myapp:buildcache,mode=max \
  -t myapp:latest .

# Multi-platform with buildx
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --push \
  -t myrepo/myapp:latest .
```

***

## Run

```bash
docker run nginx                                       # foreground, attached
docker run -d nginx                                    # detached (background)
docker run -d -p 8080:80 nginx                         # map host:8080 → container:80
docker run -d -P nginx                                 # publish all EXPOSE'd ports to random host ports
docker run --name mycontainer nginx                    # assign name
docker run --rm alpine echo hello                      # remove container on exit
docker run -it ubuntu bash                             # interactive TTY
docker run -e KEY=value nginx                          # set env var
docker run --env-file .env nginx                       # load env from file
docker run -v myvolume:/data nginx                     # named volume
docker run -v /host/path:/container/path nginx         # bind mount
docker run -v /host/path:/container/path:ro nginx      # bind mount read-only
docker run --tmpfs /tmp:rw,size=64m nginx              # in-memory tmpfs
docker run --network mynet nginx                       # custom network
docker run --network host nginx                        # host network (Linux only)
docker run --network none alpine                       # no network
docker run -m 512m --cpus="1.5" nginx                  # memory + CPU limits
docker run --memory-swap 1g nginx                      # total memory + swap limit
docker run --cpu-shares=512 nginx                      # relative CPU weight (default 1024)
docker run --cpuset-cpus="0,1" nginx                   # pin to specific CPU cores
docker run --pids-limit=100 nginx                      # max processes in container
docker run --read-only nginx                           # read-only root filesystem
docker run --read-only --tmpfs /tmp nginx              # read-only + writable /tmp
docker run --user 1000:1000 nginx                      # run as non-root UID:GID
docker run --cap-drop ALL --cap-add NET_BIND_SERVICE nginx  # Linux capabilities
docker run --security-opt no-new-privileges nginx      # prevent privilege escalation
docker run --security-opt seccomp=profile.json nginx   # custom seccomp profile
docker run --security-opt apparmor=my-profile nginx    # custom AppArmor profile
docker run --restart unless-stopped nginx              # restart policy
docker run --restart on-failure:3 nginx                # restart on failure, max 3 times
docker run --health-cmd="curl -f http://localhost/" \
           --health-interval=30s \
           --health-timeout=5s \
           --health-retries=3 \
           --health-start-period=10s nginx
docker run --init nginx                                # use tini as PID 1 (signal forwarding)
docker run --hostname myhostname nginx                 # set container hostname
docker run --add-host db:192.168.1.10 nginx            # add /etc/hosts entry
docker run --dns 8.8.8.8 nginx                         # custom DNS
docker run --link other-container:alias nginx          # legacy link (avoid — use networks)
docker run --privileged nginx                          # all capabilities + all devices (avoid)
docker run --ipc=host nginx                            # share host IPC namespace
docker run --pid=host nginx                            # share host PID namespace
```

***

## Container Lifecycle

```bash
docker ps                           # list running containers
docker ps -a                        # list all containers (including stopped)
docker ps -q                        # list only container IDs
docker ps -qa                       # all container IDs
docker ps --filter status=exited    # filter by status
docker ps --filter name=web         # filter by name pattern
docker ps --filter ancestor=nginx   # containers using nginx image
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

docker start <container>            # start stopped container
docker stop <container>             # SIGTERM, then SIGKILL after 10s
docker stop -t 30 <container>       # custom grace period (seconds)
docker kill <container>             # SIGKILL immediately
docker kill -s SIGUSR1 <container>  # send custom signal
docker restart <container>
docker restart -t 5 <container>     # restart with 5s stop timeout

docker pause <container>            # freeze all processes (SIGSTOP via cgroup freezer)
docker unpause <container>

docker rm <container>               # remove stopped container
docker rm -f <container>            # force remove running container
docker rm -v <container>            # also remove anonymous volumes
docker rm $(docker ps -aq)          # remove all stopped containers
docker container prune              # remove all stopped containers (with confirmation)
docker container prune -f           # remove all stopped containers (no confirmation)
```

***

## Exec & Inspect

```bash
docker exec <container> <cmd>                  # run command in running container
docker exec -it <container> bash               # interactive bash shell
docker exec -it <container> sh                 # interactive sh (alpine/slim images)
docker exec -u root <container> bash           # override user
docker exec -w /tmp <container> ls             # set working directory
docker exec -e KEY=val <container> env         # set env var for exec

docker attach <container>                      # attach to PID 1 stdin/stdout (not a new shell)

docker inspect <container>                     # full JSON metadata
docker inspect <container> | jq '.[0].State'   # container state
docker inspect -f '{{.NetworkSettings.IPAddress}}' <container>   # IP address
docker inspect -f '{{.State.ExitCode}}' <container>              # exit code
docker inspect -f '{{.State.OOMKilled}}' <container>             # OOM killed?
docker inspect --format '{{json .Config.Env}}' <container> | jq  # env vars as JSON

docker top <container>                         # show processes inside container
docker stats                                   # live resource usage (all containers)
docker stats <container>                       # single container stats
docker stats --no-stream                       # one-shot snapshot
docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"

docker diff <container>                        # show filesystem changes vs image
                                               # A=added, C=changed, D=deleted
docker port <container>                        # show port mappings
docker cp <container>:/path /host/path         # copy from container to host
docker cp /host/path <container>:/path         # copy from host to container
docker commit <container> myimage:mytag        # create image from container state
docker export <container> | gzip > export.tar.gz  # export container rootfs
```

***

## Logs

```bash
docker logs <container>                    # all logs since start
docker logs -f <container>                 # follow (like tail -f)
docker logs --tail 100 <container>         # last 100 lines
docker logs --tail 0 -f <container>        # follow from now (no history)
docker logs --since 1h <container>         # logs from last 1 hour
docker logs --since 2024-01-01T00:00:00 <container>
docker logs --until 2024-01-01T12:00:00 <container>
docker logs -t <container>                 # include timestamps
docker logs 2>&1 <container> | grep ERROR  # stderr+stdout, pipe to grep
```

***

## Image Management

```bash
docker images                              # list local images
docker images -a                           # include intermediate layers
docker images --filter dangling=true       # untagged/unreferenced images
docker images --format "{{.Repository}}:{{.Tag}}\t{{.Size}}"

docker pull nginx                          # pull latest
docker pull nginx:1.27-alpine             # specific tag
docker pull --platform linux/arm64 nginx   # specific platform
docker pull --all-tags nginx               # pull all tags

docker tag myapp:latest myrepo/myapp:v1.2.3
docker rmi myapp:latest                    # remove image tag
docker rmi -f <image-id>                   # force remove (even if tagged)
docker rmi $(docker images -q)             # remove all images

docker image prune                         # remove dangling images
docker image prune -a                      # remove all unused images
docker image prune -a --filter "until=24h" # unused images older than 24h

docker save myapp:latest | gzip > myapp.tar.gz          # export image to tar
docker load < myapp.tar.gz                               # import image from tar
docker save myapp:latest | ssh user@host docker load     # transfer to remote host

docker history myapp:latest                              # show layer history + sizes
docker history --no-trunc myapp:latest                   # full commands
docker image inspect myapp:latest                        # full image metadata
docker manifest inspect nginx:latest                     # inspect multi-platform manifest
```

***

## Registry Operations

```bash
docker login                               # Docker Hub (prompts for credentials)
docker login registry.example.com          # private registry
docker login -u myuser -p mypass registry.example.com   # non-interactive (CI)
docker logout
docker logout registry.example.com

docker push myrepo/myapp:v1.2.3
docker push --all-tags myrepo/myapp        # push all local tags

docker search nginx                        # search Docker Hub
docker search --filter is-official=true nginx
docker search --filter stars=100 nginx
docker search --format "table {{.Name}}\t{{.StarCount}}\t{{.Official}}" nginx
```

***

## Network Commands

```bash
docker network ls                           # list networks
docker network ls --filter driver=bridge    # filter by driver
docker network inspect bridge              # inspect network (shows connected containers)
docker network inspect mynet | jq '.[0].Containers'

docker network create mynet                # create custom bridge
docker network create \
  --driver bridge \
  --subnet 192.168.100.0/24 \
  --gateway 192.168.100.1 \
  --opt com.docker.network.bridge.name=mybr0 \
  mynet
docker network create --driver overlay --attachable mynet   # overlay
docker network create -d macvlan \
  --subnet=192.168.1.0/24 \
  --gateway=192.168.1.1 \
  -o parent=eth0 mymacvlan

docker network connect mynet <container>    # attach running container
docker network connect --ip 192.168.100.10 mynet <container>   # with static IP
docker network disconnect mynet <container>
docker network rm mynet
docker network prune                        # remove all unused networks
docker network prune -f                     # without confirmation
```

***

## Volume Commands

```bash
docker volume ls
docker volume ls --filter dangling=true     # volumes not attached to any container
docker volume create myvolume
docker volume create --driver local \
  --opt type=nfs \
  --opt o=addr=192.168.1.100,rw \
  --opt device=:/nfs/share \
  nfs-volume
docker volume inspect myvolume
docker volume rm myvolume
docker volume prune                         # remove unused volumes
docker volume prune -a                      # remove all volumes (including named)
docker volume prune -f                      # without confirmation
```

***

## Docker Compose

```bash
docker compose up                           # create and start all services
docker compose up -d                        # detached
docker compose up --build                   # rebuild images before starting
docker compose up --force-recreate          # recreate containers even if config unchanged
docker compose up --scale web=3             # scale service to 3 replicas
docker compose up --no-deps web             # start only 'web' without dependencies

docker compose down                         # stop and remove containers + networks
docker compose down -v                      # also remove volumes
docker compose down --rmi all               # also remove images

docker compose stop                         # stop without removing containers
docker compose start                        # start stopped containers
docker compose restart
docker compose restart web                  # restart specific service

docker compose ps                           # list running services
docker compose ps -a                        # all services including stopped
docker compose top                          # processes in all services
docker compose port web 80                  # show published port for service

docker compose logs                         # all service logs
docker compose logs -f web                  # follow specific service logs
docker compose logs --tail=50 web
docker compose logs --since 1h

docker compose exec web bash               # shell into running service
docker compose exec -u root web bash       # as root
docker compose run --rm web pytest         # one-off command in new container
docker compose run --no-deps --rm web sh   # without starting dependencies

docker compose build                        # build/rebuild all services
docker compose build web                    # build specific service
docker compose build --no-cache            # ignore cache
docker compose pull                         # pull latest images
docker compose config                       # validate and print resolved config
docker compose config --services            # list service names
docker compose events                       # real-time events
```

***

## System & Cleanup

```bash
docker system df                            # disk usage: images, containers, volumes, cache
docker system df -v                         # verbose: per-item breakdown
docker system prune                         # remove stopped containers, dangling images, unused networks
docker system prune -a                      # also remove all unused images (not just dangling)
docker system prune -a --volumes            # also remove unused volumes
docker system prune -a --volumes -f         # no confirmation prompt

docker system info                          # daemon info: runtime, storage driver, OS, CPUs, memory
docker system info --format '{{.Driver}}'   # storage driver only
docker system events                        # real-time event stream from daemon
docker system events --filter type=container --filter event=die
docker system events --since 1h --until 0m
```

***

## Dockerfile Instructions Quick Reference

| Instruction | Example | Notes |
|-------------|---------|-------|
| `FROM` | `FROM node:20-alpine AS base` | Must be first; `FROM scratch` = empty base |
| `RUN` | `RUN apt-get update && apt-get install -y curl` | Creates filesystem layer; combine to reduce layers |
| `COPY` | `COPY --chown=1000:1000 src/ /app/src/` | Copies from build context; no URL support |
| `COPY --from` | `COPY --from=builder /bin/app /app` | Copy from another stage or external image |
| `ADD` | `ADD app.tar.gz /app/` | Like COPY but auto-extracts tar + supports URLs; prefer COPY |
| `CMD` | `CMD ["node", "server.js"]` | Default args; overridden by `docker run <image> <cmd>` |
| `ENTRYPOINT` | `ENTRYPOINT ["nginx", "-g", "daemon off;"]` | Fixed executable; CMD provides default args |
| `ENV` | `ENV NODE_ENV=production PORT=3000` | Persists into container runtime |
| `ARG` | `ARG VERSION=1.0` | Build-time only; not available at runtime |
| `EXPOSE` | `EXPOSE 8080/tcp` | Documentation only; use `-p` at runtime to publish |
| `VOLUME` | `VOLUME ["/data"]` | Declares mount point; Docker creates named volume if none provided |
| `WORKDIR` | `WORKDIR /app` | Sets working dir; creates if not exists |
| `USER` | `USER 1000:1000` | Sets UID:GID for subsequent instructions and runtime |
| `HEALTHCHECK` | `HEALTHCHECK --interval=30s --timeout=5s CMD curl -f http://localhost/health` | Container health probe |
| `LABEL` | `LABEL org.opencontainers.image.version="1.2.3"` | OCI-standard metadata |
| `ONBUILD` | `ONBUILD COPY . /app` | Triggers when used as base image in child build |
| `STOPSIGNAL` | `STOPSIGNAL SIGQUIT` | Override default SIGTERM for graceful shutdown |
| `SHELL` | `SHELL ["/bin/bash", "-o", "pipefail", "-c"]` | Override default shell for RUN |

**CMD vs ENTRYPOINT:**
```dockerfile
ENTRYPOINT ["nginx"]
CMD ["-g", "daemon off;"]
# → default: nginx -g "daemon off;"
# → docker run <img> -t   → nginx -t  (CMD overridden, ENTRYPOINT kept)
# → docker run --entrypoint="" <img> bash  → bash (ENTRYPOINT overridden)
```

***

## BuildKit Advanced Flags

```dockerfile
# Cache mounts — persistent cache across builds
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    apt-get update && apt-get install -y curl

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

RUN --mount=type=cache,target=/root/go/pkg/mod \
    --mount=type=cache,target=/root/.cache/go-build \
    go build -o /bin/app ./cmd/app

# Secret mounts — never stored in any layer
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc \
    npm install

# SSH mounts — forward SSH agent
RUN --mount=type=ssh \
    git clone git@github.com:org/private.git

# Bind mounts — use host file without copying (read-only)
RUN --mount=type=bind,source=./scripts,target=/scripts \
    /scripts/setup.sh
```

```bash
# Build with secrets
docker build --secret id=npmrc,src=$HOME/.npmrc .
docker build --secret id=db_pass,env=DB_PASSWORD .

# SSH agent forwarding
eval $(ssh-agent)
ssh-add ~/.ssh/id_rsa
docker build --ssh default .
```

***

## Docker Scout (Security Scanning)

```bash
docker scout quickview myapp:latest        # CVE summary overview
docker scout cves myapp:latest             # full CVE list with severity
docker scout cves --format sarif myapp:latest > results.sarif
docker scout recommendations myapp:latest  # base image upgrade suggestions
docker scout compare myapp:v1 myapp:v2     # diff CVEs between two images
docker scout sbom myapp:latest             # generate SBOM
docker scout attestation add \
  --predicate sbom.json myapp:latest       # attach SBOM attestation
```

***

## Useful One-Liners

```bash
# Remove all stopped containers
docker container prune -f

# Remove all unused images (not just dangling)
docker image prune -af

# Remove everything unused at once
docker system prune -af --volumes

# Kill all running containers
docker kill $(docker ps -q)

# Get container IP addresses
docker inspect -f '{{.Name}} {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' \
  $(docker ps -q)

# Follow logs for all containers matching a name pattern
docker ps --filter name=web -q | xargs docker logs -f --tail=50

# Resource usage snapshot
docker stats --no-stream --format \
  "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"

# Export all running container logs
for c in $(docker ps -q); do
  docker logs $c > /tmp/$(docker inspect $c --format '{{.Name}}').log 2>&1
done

# Pull, tag, and push to private registry in one chain
docker pull nginx:latest && \
  docker tag nginx:latest registry.example.com/nginx:latest && \
  docker push registry.example.com/nginx:latest

# Interactively debug a failing build stage
docker build --target builder -t myapp:debug . && \
  docker run --rm -it myapp:debug sh

# Check which containers use an image
docker ps -a --filter ancestor=nginx --format "{{.Names}}"

# Find large layers in an image
docker history --no-trunc myapp:latest | sort -k4 -h | tail -20

# Get the image digest (content hash)
docker inspect --format='{{index .RepoDigests 0}}' nginx:latest

# Run a one-off container with host networking for debugging
docker run --rm --network host --pid host --privileged \
  nicolaka/netshoot tcpdump -i eth0 port 80
```

***

## Docker Context (Remote Builds)

```bash
# Create context for remote Docker daemon
docker context create remote \
  --docker "host=ssh://user@remote-host"

docker context ls
docker context use remote

# Build on remote host
docker build -t myapp:latest .

# Switch back
docker context use default

# Remove context
docker context rm remote
```

***

## Registry Mirror Setup

```json
// /etc/docker/daemon.json
{
  "registry-mirrors": [
    "https://mirror.example.com"
  ],
  "insecure-registries": [],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

```bash
sudo systemctl reload docker
docker info | grep -A5 "Registry Mirrors"
```
# Content from CheatSheet_Docker.pdf

## Page 1

Command
Description
docker run <image>
Create and run a new container
docker run -d <image>
Run a container in the background
docker run -p 8080:80 <image>
Publish container port 80 to host port 8080
docker run -v <host>:<container> <image>
Mount a host directory to a container
docker ps
List currently running containers
docker ps --all
List all containers (running or stopped)
docker logs <container name>
Fetch the logs of a container
docker logs -f <container name>
Fetch and follow the logs of a container
dockerstop <container name>
Stop a running container
dockerstart <container name>
Start a stopped container
docker rm <container name>
Remove a container
Shubham
TrainWith
Shubham
TrainWith
Docker_CheatSheet
Cheatsheet for DevOps Engineers
Installation & Account Setup :
Docker (Linux): https://docs.docker.com/engine/install/
Docker Desktop (Linux, Windows, Mac): https://docs.docker.com/desktop/
Docker container commands:


***

## Page 2

Command
Description
docker run <image>
Create and run a new container
docker run -d <image>
Run a container in the background
docker run -p 8080:80 <image>
Publish container port 80 to host port 8080
docker run -v <host>:<container> <image>
Mount a host directory to a container
docker ps
List currently running containers
docker ps --all
List all containers (running or stopped)
docker logs <container name>
Fetch the logs of a container
docker logs -f <container name>
Fetch and follow the logs of a container
dockerstop <container name>
Stop a running container
dockerstart <container name>
Start a stopped container
docker rm <container name>
Remove a container
Shubham
TrainWith
Docker container commands:
Executing commands in a Docker container:
Command
Description
docker exec <container name> <command>
Execute a command in a running container
docker exec -it <container name> bash
Open a shell in a running container
Shubham
TrainWith


***

## Page 3

Docker container registry commands:
Command
Description
 docker login
Login to Docker Hub
docker logout
Logout of Docker Hub
docker login <server>
Login to another container registry
docker logout <server>
Logout of another container registry
docker push <image>
Upload an image to a registry
dockersearch <image>
Search Docker Hub for images
docker pull <image>
Download an image from a registry
Docker image commands:
Command
Description
docker build -t <image> .
Build a new image from the Dockerfile in
the current directory and tag it
docker images
List local images
docker rmi <image>
Remove an image
Shubham
TrainWith
Docker system commands:
Command
Description
docker system df
Show Docker disk usage
docker system prune
Pull changes from the remote repository
docker system prune -a
Remove all unused data


***

## Page 4

Command
Description
docker compose up
Create and start containers
docker compose up -d
Create and start containers in background
docker compose up --build
Rebuild images before starting containers
docker compose stop
Stop services
docker compose down
Stop and remove containers and networks
docker compose ps
List running containers
docker compose logs
View the logs of all containers
docker compose logs <service>
View the logs of a specific service
docker compose logs -f
View and follow the logs
docker compose build
Build or rebuild services
docker compose pull
Pull the latest images
docker compose build --pull
Pull latest images before building
Shubham
TrainWith
Docker compose:
Shubham
TrainWith


***

## Page 5

Command
Description
docker network create –driver <driver name> <network name>
Create docker network
with custom bridge
docker network connect <network-name> <container-name or id>
Connect a running Docker
Container to an existing
Network
docker network inspect <network-name>
Get details of a Docker
Network
docker network ls
List all the Docker
Networks
docker network disconnect <network-name> <container-name>
Remove a Container from
the Network
docker network rm <network-name>
Remove a Docker
Network
docker network prune
Remove all the unused
Docker Networks
Docker networking commands:
Dockerfile instructions:
Command
Description
FROM <image>
Set the base image
FROM <image> AS <name>
Set the base image and name the build stage
RUN <command>
Execute a command as part of the build process
RUN ["exec", "param1", "param2"]
Execute a command as part of the build process
CMD ["exec", "param1", "param2"]
Execute a command when the container starts
ENTRYPOINT ["exec", "param1"]
Configure the container to run as an executable
Shubham
TrainWith


***

## Page 6

Command
Description
docker scout
Command-line tool for Docker Scout
docker scout quickview
Quick overview of an image
docker scout compare
Compare two images and display
differences
docker scout recommendations
Display available base image updates and
remediation recommendations
docker scout recommendations
<image_name>
Display base image update
recommendations
docker scout compare --to <image_name>:latest
<image_name>:v1.2.3-pre
Compare an image to the latest tag
Docker Scout:
Command
Description
ENV <key>=<value>
Set an environment variable
EXPOSE <port>
Expose a port
COPY <src> <dest>
Copy files from source to destination
COPY --from=<name> <src> <dest>
Copy files from a build stage to destination
WORKDIR <path>
Set the working directory
VOLUME <path>
Create a mount point
USER <user>
Set the user
ARG <name>
Define a build argument
ARG <name>=<default>
Define a build argument with a default value
LABEL <key>=<value>
Set a metadata label
HEALTHCHECK <command>
Set a healthcheck command
Shubham
TrainWith


***

