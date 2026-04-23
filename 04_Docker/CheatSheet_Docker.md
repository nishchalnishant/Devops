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


---

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


---

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


---

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


---

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


---

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


---

