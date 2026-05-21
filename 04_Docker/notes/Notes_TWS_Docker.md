# Content from Notes_TWS_Docker.pdf

```
Docker — TWS Notes
├── History & Basics
│   ├── Created March 2013 by Solomon Hykes and Sebastien Paul
│   ├── Written in Go; OS-level virtualization (containerization)
│   └── Solves "works on my machine" problem via consistent container environments
├── Advantages
│   ├── No pre-allocation of RAM (lightweight vs VMs)
│   ├── CI efficiency — same image used across all deployment stages
│   ├── Reusable images and layers
│   └── Runs on physical, virtual, or cloud hardware
├── Disadvantages
│   ├── No rich GUI support
│   ├── Hard to manage large numbers of containers without orchestration
│   ├── No cross-platform compatibility (Windows vs Linux kernel)
│   └── No built-in data recovery/backup
├── Docker Architecture
│   ├── Docker Daemon (dockerd) — runs on host OS, manages containers/images/networks
│   ├── Docker Client — CLI + REST API → communicates with daemon
│   ├── Docker Host — provides environment (daemon + images + containers + networks + storage)
│   └── Docker Registry — stores images (Docker Hub = public; private registry for enterprise)
├── Docker Image
│   ├── Read-only binary template with all dependencies
│   ├── Created from: Docker Hub pull / Dockerfile build / commit from container
│   └── Image becomes container when run on Docker engine
├── Dockerfile Instructions
│   ├── FROM — base image (must be first)
│   ├── RUN — execute commands; creates new layer
│   ├── COPY — copy from local context (no internet)
│   ├── ADD — like COPY + download from URL + extract tar
│   ├── EXPOSE — document port (does not publish)
│   ├── WORKDIR — set working directory
│   ├── CMD — default command; overridable at docker run
│   ├── ENTRYPOINT — fixed entrypoint; higher priority than CMD
│   ├── ENV — environment variables (persists into container)
│   └── ARG — build-time variables only (not available after build)
├── Docker Volumes
│   ├── Volume = directory inside container declared at creation time
│   ├── Persists after container stop/delete
│   ├── Share across containers (Container ↔ Container) or host (Host ↔ Container)
│   └── Benefits: decoupling storage, shared data, lifecycle independence
└── Key Commands
    ├── docker images / docker pull / docker search
    ├── docker run --name / docker start / docker stop / docker rm
    ├── docker ps / docker ps -a
    ├── docker exec -it / docker attach
    ├── docker build -t / docker commit
    └── docker diff (see layer changes vs base image)
```

## First Principles

- **Why did Docker solve the "works on my machine" problem?** Before Docker, applications depended on OS-level libraries and environment variables that differed between machines. A container packages the app with all its dependencies, making the execution environment identical on any host that runs Docker — developer laptop, CI server, or production VM.
- **Why is Docker written in Go?** Go produces statically linked binaries with no runtime dependencies, enabling Docker to ship a single binary. Its goroutine concurrency model suits the daemon's need to manage many containers and network connections simultaneously.
- **Why no RAM pre-allocation?** Containers share the host kernel and use cgroups for memory limits. A container only consumes the RAM its process actually uses, unlike VMs which reserve a fixed block of RAM at boot. This makes containers far more density-efficient on a host.
- **Why does EXPOSE not publish ports?** `EXPOSE` is documentation metadata inside the image — it tells operators which ports the app listens on. Actual port binding requires `-p host:container` at `docker run`, which creates iptables DNAT rules. Separation of declaration from binding allows the same image to be deployed with different port mappings.
- **Why use `docker exec` instead of `docker attach`?** `docker attach` connects to PID 1's stdin/stdout — if you exit, you send SIGTERM and can stop the container. `docker exec` spawns a new process in the container's namespaces, so exiting the exec session leaves the container and PID 1 running unaffected.

## Page 1

Docker Short
notes
F O R  D E V O P S  E N G I N E E R S
Train
Train
Shubham
Shubham
With
With


***

## Page 2

Docker Short Notes
Basics of Docker
Docker was first released in March 2013. It is developed by Solomon Hykes and
Sebastien paul.
Docker is an open-source centralized platform designed to create deploy and
run applications.
Docker uses the container on the host O.S to run applications. It allows
applications to use the same Linux Kernel as a system on the host computer,
rather than creating a whole virtual O.S.
We can install Docker on any O.S but the Docker engine runs natively on Linux
distribution.
Docker is written in the ‘GO’ language.
Docker is a tool that performs OS-level virtualization, also known as
containerization.
Before Docker, many users face the problem that a particular code runs in the
developer’s system but not in the user’s system.
Train
Train
Shubham
Shubham
With
With
Advantages of Docker
No pre-allocation of RAM.
CI Efficiency → Docker enables you to build a container image and use. that
same image across every step of the deployment process.
Less Cost.
It is light in weight.
It can run on physical Hardware, Virtual Hardware, or on Cloud.
You can re-use the image.
It took very less time to create the container.


***

## Page 3

Disadvantages of Docker
Docker is not a good solution for application that requires a rich GUI.
Difficult to manage a large number of containers.
Docker does not provide cross-platform compatibility means if an application is
designed to run in a docker container on windows, then it can’t run on Linux or
vice-versa.
Docker is suitable when the development O.S and testing O.S are the same, if
the O.S is different, we should use Virtual Machine.
No solution for Data Recovery & Backup.
When Image is running we can say container, When we send a container or not-
runnable state we can say Image.
Train
Train
Shubham
Shubham
With
With
Note
Architecture of Docker


***

## Page 4

Components of Docker
Docker daemon runs on the Host O.S.
It is responsible for running containers, and managing docker services.
Docker daemons can communicate with other daemons.
Train
Train
Shubham
Shubham
With
With
Docker Daemon
Docker users can interact with the docker daemon through a client.
Docker client uses commands and Rest API to communicate with the docker
daemon.
When a client runs any server command on the docker client terminal, the
client terminal sends the docker commands to the docker daemon.
Docker clients can communicate with more than one daemon.
Docker Client
Docker Host is used to providing an environment to execute and run
applications. It contains the docker daemon, images, containers, networks,
and storage.
Docker Host
Docker registry manages and stores the docker images.
There are two types of registries in the docker.
1) Public Registry → Public registry also called Docker Hub.
2) Private Registry → It is used to share images within the enterprise.
Docker Hub/Registry
Docker images are the read-only binary templates used to create docker
containers. or, a single file with all dependencies and configurations
required to run a program.
Docker Images


***

## Page 5

Take an image from Docker Hub.
→ Ways to create an images
1.
   2.Create an image from Docker File.
   3.Create an image from existing docker containers.
Train
Train
Shubham
Shubham
With
With
The container holds the entire package that is needed to run the application.
or,
In other words, we can say that the image is a template and the container is
a copy of that template.
container is like virtualization when they run on the Docker engine.
Images become containers when they run on the docker engine.
Docker Container
Docker Installation and important commands

Create a machine on AWS with Docker installed AMI, and install Docker if
not installed. yum install docker
 To see all images present in your local.

 To find out images in the docker hub.

 To download an image from docker-hub to a local machine.


***

## Page 6

Train
Train
Shubham
Shubham
With
With

 To give a name to the container and run.

 To check, whether the service is starting or not.

 To start the service.

 To start/stop the container.

 To go inside the container.

 To see all the containers.

 To see only running containers.


***

## Page 7

Train
Train
Shubham
Shubham
With
With

 To stop the container.

 To delete the container.

 Exiting from the docker container.

 To delete images.
Dockerfile Creation
Docker image creation using existing docker file

 We have to create a container from our image, therefore create one
container first —



***

## Page 8

Train
Train
Shubham
Shubham
With
With

 Now create one file inside this tmp directory

 Now if you want to see the difference between the base image & changes on it
then —

 Now create an image of this container


 Now create a container from this image.


***

## Page 9

Train
Train
Shubham
Shubham
With
With
Dockerfile Creation using Dockerfile
Dockerfile
Dockerfile is a text file it contains some set of instruction
Automation of docker image creation
FROM
For the base image. This command must be on top of the docker file.
RUN
To execute commands, it will create a layer in the image.
MAINTAINER
Author/Owner/Description
COPY
Copy files from the local system (dockerVM) we need to provide a source,
and destination. (We can’t download the file from the internet and any
remote repo)
ADD
Similar to copy, it provides a feature to download files from the internet,
also we extract the file from the docker image side.
EXPOSE
To expose ports such as port 8080 for tomcat, port 80 for Nginx, etc…
WORKDIR
To set a working directory for a container.
CMD
Execute commands but during container creation.


***

## Page 10

Train
Train
Shubham
Shubham
With
With
ENTRYPOINT
Similar to CMD, but has higher priority over CMD, the first commands will be
executed by ENTRYPOINT only.
ENV
Environment Variables.
ARG
To define the name of a parameter and its default value, the difference
between ENV and ARG is that after you set on env. using ARG, you will not
be able to access that late on when you try to run the Docker container.
Creation of Dockerfile
Create a file named Dockerfile
Add instructions in Dockerfile
Build dockerfile to create an image
Run image to create the container
1.
2.
3.
4.


 To create an image out of Dockerfile

 Check process state


***

## Page 11

 See images
 To create a container from the above image
No need to create a new Dockerfile we will just update the Dockerfile.
 Ex. Command for next image creation
Train
Train
Shubham
Shubham
With
With



Open Dockerfile with vi remove all and this code
We have to create a testfile, test, and test.tar.gz
Then build the image
Then create the image


***

## Page 12

 All about Docker Volume
Train
Train
Shubham
Shubham
With
With
Volume is simply a directory inside our container.
Firstly, we have to declare this directory as a volume and then share the
volume.
Even if we stop the container, still we can access volume.
The volume will be created in one container.
You can declare a directory as a volume only while creating the container.
You can’t create volume from the existing container.
You can share one volume across any number of containers.
The volume will not be included when you update an image.
We can map volume in two ways —
Container ← → Container
Host ← → Container
1.
2.
Benefits of Volume
Decoupling container from storage.
Share volume among different containers.
Attach the volume to containers
On deleting the container, the volume does not delete.


***

## Page 13

Creating volume from Dockerfile
Train
Train
Shubham
Shubham
With
With
 Create a Dockerfile and write

 Then create an image from this Dockerfile.

 Now create a container from this image & run

 Now do ls, you can see myvolume1

 Now share volume with another container [Container ← → Container]
Now after creating container2, myvolume1 is visible, whatever you do in
one volume, can be seen from another volume.


***

## Page 14

Create volume by using the command
Train
Train
Shubham
Shubham
With
With
 create volume by using the command

 Now create one more container and save volume

Now you are inside the container; do ls, and you can see your volume
Now create one file inside this volume and then check in containers, you
can see that file.
Then do ls and change directory to your volume
 Volumes [Host ← → Container]
Verify files in /home/ec2-user
Create volumes in host and container and mapped them

Now check in ec2, you can see the files.


***

## Page 15

Some other commands
Train
Train
Shubham
Shubham
With
With
 To see all created volumes

To create docker volume (normal)

To delete volume

To remove all unused docker volumes

To get volume details

To get container details



***

## Page 16

Some other imp. Terms
Train
Train
Shubham
Shubham
With
With
The difference between docker attach and docker exec
Docker exec creates a new process in the container’s environment while
docker attaches just connect the standard I/O of the main process inside
the container to the corresponding standard I/O error of the current
terminal.
docker exec is especially for running new things in an already started
container, be it a shell or some other process.
The difference between expose and publish a docker
Neither specifies expose nor -p
Only specify expose
Specify expose and -p
We have three options:
1.
2.
3.
Explain
If we specify neither expose nor -p the service in the container will only
be accessible from inside the container itself.
If we expose a port, the service in the container is not accessible from
outside docker, but from inside other docker containers, so this is good
for inter-container communication.
If we expose and -p a port, the service in the container is accessible from
anywhere, even outside docker.
If we do -p but do not expose, docker does an implicit expose. This is
because, if a port is open to the public, it is automatically also open to the
other docker containers.
Note


***

## Page 17

Train
Train
Shubham
Shubham
With
With
Thank You Dosto


