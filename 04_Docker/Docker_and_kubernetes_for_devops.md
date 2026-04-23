# Content from Docker_and_kubernetes_for_devops.pdf

## Page 1



---

## Page 2

1
Table of Contents 
1. Introduction 
2. Understanding Containers and
Docker 
3. Setting Up Docker 
4. Docker Basics 
5. Advanced Docker Usage 
6. Introduction to Kubernetes 
7. Kubernetes Architecture 
8. Setting Up a Kubernetes Cluster 
9. Deploying Applications on
Kubernetes 
10.
11.
12.
13.
14.
15.
16.
17.
18. 
Kubernetes Networking
Kubernetes Storage
Managing Kubernetes Workloads
Monitoring and Logging
Security Best Practices
CI/CD with Docker and Kubernetes
Troubleshooting and Debugging
Cheat Sheets and Useful Commands
Conclusion 


---

## Page 3

: Docker containers can run on any platform that supports Docker, 
including cloud environments. 
: Each container runs in its isolated environment, preventing conflicts 
between applications. 
: Docker allows for easy scaling of applications by running multiple 
instances of containers. 
: Containers share the host system’s kernel, making them more efficient 
than virtual machines. 
Docker is the most popular containerization platform and has become synonymous with
containers. It provides an easy-to-use interface for creating, managing, and running
containers. Docker simplifies the process of packaging an application with all its
dependencies into a standardized unit for software development. With Docker, developers
can create a container image that can be shared with others and run on any machine that has
Docker installed. 
Key Benefits of Docker: 
DevOps, a portmanteau of "development" and "operations," represents a set of
practices aimed at bridging the gap between software development and IT
operations. The goal of DevOps is to shorten the systems development life cycle
while delivering features, fixes, and updates frequently in close alignment with
business objectives. The advent of DevOps has brought about significant changes
in how software is developed, tested, and deployed. Key practices include
continuous integration (CI), continuous deployment (CD), and infrastructure as
code (IaC). 
Welcome to "Docker and Kubernetes for DevOps," a comprehensive guide designed to equip
you with the knowledge and skills necessary to effectively use Docker and Kubernetes in
your DevOps practices. In this chapter, we will set the stage by exploring the importance of
these technologies in the modern software development landscape, the objectives of this
book, and a brief overview of what you will learn in the subsequent chapters. 
Containers have revolutionized the way we think about software deployment. Unlike
traditional virtual machines, containers are lightweight and provide a consistent environment
for applications, making them ideal for both development and production. Containers
encapsulate an application and its dependencies, ensuring that it runs reliably regardless of
where it is deployed. This eliminates the classic "works on my machine" problem, providing
a seamless transition from development to production. 
2
•
• 
Portability
Isolation
•
• 
Scalability
Efficiency
Chapter 1:Introduction 
Overview 
Why Docker? 
The Role of Containers 
The Evolution of DevOps 


---

## Page 4

This book is intended for: 
• Developers: Who want to learn how to containerize their applications and deploy 
them using Kubernetes. 
• DevOps Engineers: Who are looking to implement CI/CD pipelines and manage 
containerized applications. 
• System Administrators: Who need to maintain and troubleshoot containerized 
applications in a Kubernetes environment. 
• IT Professionals: Who want to stay up-to-date with the latest trends in 
containerization and orchestration technologies. 
 
: Kubernetes automates the deployment and scaling of 
containers. 
Self-Healing: Kubernetes automatically replaces failed containers and reschedules 
them to healthy nodes. 
ServiceDiscoveryandLoadBalancing: Kubernetes provides built-in mechanisms 
for service discovery and load balancing. 
: Kubernetes optimizes resource utilization by managing 
container scheduling and scaling based on demand. 
This book aims to provide a practical guide for using Docker and Kubernetes in DevOps. By
the end of this book, you will: 
1. Understand the fundamental concepts of Docker and Kubernetes. 
2. Learn how to install and configure Docker and Kubernetes. 
3. Master the basics and advanced features of Docker. 
4. Gain proficiency in deploying and managing applications on Kubernetes. 
5. Implement best practices for security, monitoring, and scaling. 
6. Utilize cheat sheets and commands for efficient workflow management. 
While Docker excels at managing individual containers, Kubernetes is designed to manage
containerized applications at scale. Kubernetes is an open-source orchestration platform that
automates the deployment, scaling, and management of containerized applications. It
provides the tools needed to ensure that your applications run smoothly and reliably across
different environments. 
Key Benefits of Kubernetes: 
3
Why Kubernetes? 
Who This Book Is For 
Objectives of This Book 
•
• 
AutomatedDeployment
• 
• ResourceManagement


---

## Page 5

4
The book is divided into several chapters, each focusing on a specific aspect of Docker and
Kubernetes: 
1. Understanding Containers and Docker: Introduction to containers, Docker, and 
their benefits. 
2. Setting Up Docker: Step-by-step instructions on installing and configuring Docker. 
3. Docker Basics: Basic Docker commands and concepts. 
4. Advanced Docker Usage: Advanced topics in Docker, including networking and 
Docker Compose. 
5. Introduction to Kubernetes: Overview of Kubernetes, its history, and core concepts. 
6. Kubernetes Architecture: Detailed look at the architecture of Kubernetes. 
7. Setting Up a Kubernetes Cluster: Instructions for setting up Kubernetes locally and 
in the cloud. 
8. Deploying Applications on Kubernetes: Guidelines and commands for deploying 
applications on Kubernetes. 
9. Kubernetes Networking: Exploration of Kubernetes networking, including service 
discovery and network policies. 
10. Kubernetes Storage: Details on Kubernetes storage options. 
11. Managing Kubernetes Workloads: Managing different types of workloads in 
Kubernetes. 
12. Monitoring and Logging: Setting up monitoring and logging for Kubernetes clusters. 
13. Security Best Practices: Best practices for securing Docker and Kubernetes 
environments. 
14. CI/CD with Docker and Kubernetes: Implementing continuous integration and 
deployment pipelines. 
15. Troubleshooting and Debugging: Techniques and tools for troubleshooting and 
debugging. 
16. Cheat Sheets and Useful Commands: A collection of cheat sheets and essential 
commands. 
17. Conclusion: Summary and next steps for further learning. 
Structure of the Book 


---

## Page 6

To get the most out of this book: 
• 
• 
•• 
Practice: Follow along with the examples and practice on your local machine or a 
cloud environment. 
Experiment: Try out different configurations and setups to see how they work. 
Join the Community: Engage with the Docker and Kubernetes communities to stay 
updated and get support. 
Keep Learning: The technologies covered in this book are constantly evolving, so 
make a habit of continuous learning. 
This book is designed to be both a learning resource and a reference guide. You
can read it from start to finish to build a solid foundation in Docker and Kubernetes,
or you can jump to specific chapters to find information on particular topics. The
cheat sheets and command references at the end of the book provide quick access
to commonly used commands and configurations. 
Docker and Kubernetes are powerful tools that can greatly enhance your DevOps practices.
By mastering these technologies, you will be well-equipped to build, deploy, and manage
modern applications efficiently and effectively. Let's get started on this exciting journey into
the world of Docker and Kubernetes for DevOps. 
5
Final Thoughts 
How to Use This Book 
 
Getting the Most Out of This Book 


---

## Page 7

Containers streamline CI/CD pipelines by ensuring consistent environments from
development to production. 
Case Study: Spotify Spotify uses Docker to manage their microservices architecture, 
enabling quick deployment and scaling of services. This has significantly reduced their 
deployment times and increased overall efficiency. 
Containers are lightweight, portable units that package an application and its dependencies
together. Unlike traditional virtual machines (VMs), containers share the host system's
kernel, making them more efficient and faster to start. 
Benefits of Containers 
 
: The core component that includes Docker Daemon, REST API, and 
CLI. 
DockerDaemon: Runs on the host machine, manages Docker objects (images, 
containers, networks, volumes). 
: Command-line interface for interacting with Docker Daemon. 
: A text document that contains instructions for building a Docker image. 
Docker is an open-source platform that automates the deployment, scaling, and management
of containerized applications. It simplifies the process of creating and managing containers. 
Docker Architecture 
6
: Containers can run anywhere—on a developer's laptop, in on-premises 
data centers, or in the cloud. 
: Containers use fewer resources compared to VMs since they share the 
host OS kernel. 
: Containers ensure that an application runs the same, regardless of where 
it's deployed. 
: Containers can be easily scaled up or down based on demand. 
In this chapter, we will dive into the fundamentals of containers and Docker, understand their
benefits, and explore their real-world applications. 
What are Containers? 
Chapter 2: Understanding Containers and Docker 
Overview 
•
•
• 
Portability
Efficiency
Consistency
• 
Scalability
What is Docker? 
•
• 
DockerEngine
• 
• 
DockerCLI
Dockerfile
Real-World Example: Continuous Integration/Continuous Deployment (CI/CD) 


---

## Page 8

1
.
2
.
3
.
1
.
2
.
3
.
1. 
2. 
3. 
4. 
1. 
 
non-root user. 
sudo systemctl enable docker
sudo usermod -aG docker $USER
: Docker Desktop for Windows 
: Follow the installation wizard. 
: Ensure Docker is running from the system tray. 
: Docker Desktop for Mac 
: Drag the Docker icon to the Applications folder. 
: Launch Docker from the Applications folder. 
This chapter provides step-by-step instructions for installing and configuring Docker on
various operating systems. We will also run our first Docker container. 
: Ensure Docker is set to start on boot and manage Docker as a 
7
Chapter 3: Setting Up Docker 
On Linux 
Overview 
On macOS 
Installing Docker
On Windows 
 
Configuring Docker 
Running Your First Docker Container 
Start Docker: 
sudo systemctl start docker 
Pull an Image: 
docker pull hello-world 
Install Docker: 
sudo apt-get install docker-ce docker-ce-cli containerd.io 
Verify Installation: 
Basic Configuration
Download Docker Desktop
Install Docker Desktop
Start Docker Desktop
Download Docker Desktop
Install Docker Desktop
Start Docker Desktop
Update Your Package Index: 
sudo apt-get update 
docker --version 
•


---

## Page 9

2. 
Developers can use Docker to set up a consistent development environment. For instance, a
Python development environment can be set up using a Dockerfile. 
Dockerfile
# Use an official Python runtime as a parent image 
FROM python:3.8-slim 
# Set the working directory in the container 
WORKDIR /app 
# Copy the current directory contents into the container at /app 
COPY . /app 
# Install any needed packages specified in requirements.txt 
RUN pip install --trusted-host pypi.python.org -r requirements.txt 
# Make port 80 available to the world outside this container 
EXPOSE 80 
# Define environment variable 
ENV NAME World 
# Run app.py when the container launches 
CMD ["python", "app.py"] 
8
Run the Container: 
docker run hello-world 
Real-World Example: Setting Up a Development Environment 


---

## Page 10

: Start a new container. 
: View all downloaded images. 
: Stop a running container. 
: Download images from Docker Hub. 
: View running and stopped containers. 
: A script containing instructions for building an image. 
This chapter covers the basic concepts and commands needed to work with Docker, including
images, containers, and Dockerfiles. 
Working with Images 
9
Chapter 4: Docker Basics 
Overview 
Listing Images
• 
Pulling Images
Creating Docker Images 
• 
Dockerfile
Building an Image: 
docker build -t myapp.
Listing Containers
docker ps -a 
Managing Containers 
• 
Running Containers
Stopping Containers
•
•
•
•
docker images 
docker run -d <image> 
Dockerfile
FROM ubuntu:18.04 
COPY . /app 
RUN make /app 
CMD python /app/app.py 
docker pull <image_name> 
docker stop <container_id> 


---

## Page 11

Deploy a simple web application using Docker. For instance, a Node.js application: 
Dockerfile
FROM node:14 
WORKDIR /usr/src/app 
COPY package*.json ./ 
RUN npm install 
COPY . . 
EXPOSE 8080 
CMD ["node", "app.js"] 
10
Real-World Example: Web Application Deployment 


---

## Page 12

1. 
2. 
3. 
4. 
5. 
6. 
1
.
2
.
3
.
4
.
5
.
6
.
7
.
: Removes an image. 
: Removes a container. 
: Lists running containers. 
: Stops a running container. 
: Pulls an image from a registry. 
: Create a container from an image using 
: Start a stopped container using 
: Pause a running container using 
: Unpause a paused container using 
: Stop a running container using 
: Restart a container using
: Remove a container using 
. 
: Runs a container based on a Docker image. 
1. Image: A lightweight, standalone, executable package that includes everything 
needed to run a piece of software, including the code, runtime, libraries, and
dependencies. 
2. Container: An instance of a Docker image that runs a specific application.
3. Dockerfile: A text file that contains instructions for building a Docker image.
4. Docker Engine: The software responsible for building, running, and managing 
Docker containers. 
11
Chapter 5: Advanced Docker Usage 
Key Concepts 
 
Container Lifecycle 
Basic Docker Commands 
Create
Start
Pause
Unpause
Stop
Restart
Delete
docker ps
docker rm
docker run
docker rmi
docker pull
docker stop
docker ps 
dockerrmi <image_id> 
docker rm <container_id> 
docker pull ubuntu:latest 
docker stop <container_id> 
docker run -it ubuntu:latest /bin/bash 
docker run. 
docker start. 
docker pause. 
docker unpause. 
dockerstop. 
dockerrestart. 
docker rm


---

## Page 13

2. 
Let's create a simple Flask web application and containerize it with Docker. 
1. Create a Flask App: 
A Dockerfile is a text file that contains instructions for building a Docker image. Here's an
example of a simple Dockerfile for a Node.js application: 
Dockerfile
# Use the official Node.js 14 image as a base 
FROM node:14 
# Set the working directory in the container 
WORKDIR /app 
# Copy package.json and package-lock.json to the working directory 
COPY package*.json ./ 
# Install dependencies 
RUN npm install 
# Copy the rest of the application code 
COPY . . 
# Expose port 3000 
EXPOSE 3000 
# Define the command to run the application 
CMD ["node", "index.js"] 
Real-World Example: Building a Flask Web Application 
12
Building Docker Images with Dockerfile 
python
# app.py 
from flask import Flask 
app = Flask(__name__) 
@app.route('/') 
def hello_world(): 
return 'Hello, Docker!' 
if __name__ == '__main__': 
app.run(debug=True, host='0.0.0.0') 
Dockerfile
# Use the official Python image as a base 
FROM python:3.9 
# Set the working directory in the container 
WORKDIR /app 
# Copy the dependencies file to the working directory 
COPY requirements.txt . 
Dockerfile: 


---

## Page 14

3. 
4. 
5. 
This chapter has provided an introduction to Docker, covering its key concepts, basic
commands, container lifecycle, and how to build Docker images using Dockerfiles. Docker
simplifies the process of developing and deploying applications by encapsulating them into
portable containers, making it easier to maintain consistency across different environments. 
13
makefile
Flask==2.0.1 
docker build -t flask-app.
docker run -d -p 5000:5000 flask-app 
Lua
+---------------------------------------- +
|
|
|+------------------------------------+|
DockerHost 
|
|
|| 
DockerEngine 
||
||+--------------------------------+||
||| 
DockerContainers 
|||
||+--------------------------------+||
| |
| |
| | + - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - + | |
||| 
DockerImages 
|||
||+--------------------------------+||
| |
| |
| | + - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - + | |
||| 
Dockerfile 
|||
||+--------------------------------+||
| |
| |
| + - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - + |
+ - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  +
#InstallFlask
RUNpipinstall -r requirements.txt 
#Copythecontent of the local src directory to the working 
directory
COPY . .
#Specifythe command to run on container start 
CMD["python", "./app.py"] 
requirements.txt: 
Build the Docker Image: 
Run the Docker Container: 
Diagram: Docker Workflow


---

## Page 15

Kubernetes, often referred to as K8s, is an open-source platform designed to automate the
deployment, scaling, and operation of application containers. Originally developed by
Google, Kubernetes has become the de facto standard for container orchestration. In this
chapter, we'll introduce Kubernetes, its key features, and why it has become so integral to
modern DevOps practices. We will also cover the basic concepts and components of
Kubernetes, supported by commands, setup guides, examples, and diagrams. 
Kubernetes is an open-source system for automating the deployment, scaling, and
management of containerized applications. It groups containers that make up an application
into logical units for easy management and discovery. 
1. Cluster: A set of nodes (physical or virtual machines) that run containerized 
applications managed by Kubernetes. 
2. Node: A worker machine in Kubernetes, which can be either a virtual or a physical 
machine. 
3. Pod: The smallest and simplest Kubernetes object. A Pod represents a set of running 
containers on your cluster. 
4. Service: An abstraction which defines a logical set of Pods and a policy by which to 
access them. 
5. Namespace: A way to divide cluster resources between multiple users (via resource 
quota). 
1. Automated Rollouts and Rollbacks: Kubernetes automates the rollout and rollback 
of your application, ensuring updates happen without downtime. 
2. Service Discovery and Load Balancing: Kubernetes can expose a container using a 
DNS name or their own IP address. If traffic to a container is high, Kubernetes can
load balance and distribute the network traffic to ensure the deployment is stable. 
3. Storage Orchestration: Kubernetes allows you to automatically mount the storage
system of your choice, such as local storage, public cloud providers, and more.
4. Self-healing: Restarts containers that fail, replaces containers, kills containers that 
don’t respond to your user-defined health check, and doesn’t advertise them to clients
until they are ready to serve. 
5. Secret and Configuration Management: Kubernetes lets you store and manage 
sensitive information, such as passwords, OAuth tokens, and ssh keys. 
14
Chapter 6: Introduction to Kubernetes 
Overview 
Key Features 
Basic Concepts 
What is Kubernetes? 


---

## Page 16

2. 
3. 
4. 
5. 
 
: Download the Minikube installer from the Minikube GitHub 
release page and follow the installation instructions. 
: 
Tip: Ensure you have a hypervisor like VirtualBox or Hyper-V installed. Minikube
supports multiple drivers like Docker, KVM, Hyperkit, and more. 
Verify Minikube Setup: 
kubectl get nodes 
 
: Manages the Kubernetes cluster. It is responsible for maintaining the 
desired state of the cluster. 
o
o
o
o 
: Exposes the Kubernetes API. 
: Stores all cluster data. 
: Schedules pods to nodes. 
: Runs controllers to regulate the state of the 
system. 
: Runs the containerized applications. 
o
o 
: Ensures that containers are running in a pod. 
: Maintains network rules. 
Minikube is a tool that makes it easy to run Kubernetes locally. Minikube runs a single-node
Kubernetes cluster inside a virtual machine on your laptop. 
1. Install Minikube: 
o On Linux: 
15
Kubernetes Components 
Setting Up a Local Kubernetes Cluster with Minikube 
•
•
 On macOS: 
o OnWindows
Start Minikube
Access the Application: 
minikube service hello-minikube 
Deploy a Sample Application: 
kubectl create deployment hello-minikube --
image=k8s.gcr.io/echoserver:1.4
kubectl expose deployment hello-minikube --type=NodePort --port=8080 
 MasterNode
kube-apiserver
etcd
kube-scheduler
kube-controller-manager
 WorkerNode
kubelet
kube-proxy
o
brew install minikube 
minikube start --driver=virtualbox 
curl -LO
https://storage.googleapis.com/minikube/releases/latest/minikub
e-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube 


---

## Page 17

2. 
3. 
4. 
Deploying applications in Kubernetes involves defining the desired state using YAML files
and applying these configurations using kubectl. 
1. Create a Deployment: 
16
Deploying Applications with Kubernetes 
kubectl get pods 
kubectl get service nginx-service 
yaml
apiVersion: apps/v1 
kind: Deployment 
metadata: 
name: nginx-deployment 
spec: 
replicas: 3 
selector: 
matchLabels: 
app: nginx 
template: 
metadata: 
labels: 
app: nginx 
spec: 
containers: 
- name: nginx 
image: nginx:1.14.2 
ports: 
- containerPort: 80 
RUN: 
kubectl apply -f nginx-deployment.yaml 
kubectl expose deployment nginx-deployment --type=LoadBalancer --
name=nginx-service 
Get Service Details: 
Expose the Deployment: 
Check the Status of Pods: 


---

## Page 18

2. 
Consider a web application with a frontend, backend, and database. You can use Kubernetes
to manage the deployment, scaling, and communication between these components. 
1. Deploy the Frontend: 
17
Real-World Example: Multi-Tier Application Deployment 
Deploy the Backend: 
yaml
apiVersion: apps/v1 
kind: Deployment 
metadata: 
name: backend-deployment 
spec: 
replicas: 2 
selector: 
matchLabels: 
app: backend 
template: 
metadata: 
labels: 
app: backend 
spec: 
containers: 
- name: backend 
image: backend:latest 
ports: 
- containerPort: 8080 
RUN: 
kubectl apply -f backend-deployment.yaml 
yaml
apiVersion: apps/v1 
kind: Deployment 
metadata: 
name: frontend-deployment 
spec: 
replicas: 2 
selector: 
matchLabels: 
app: frontend 
template: 
metadata: 
labels: 
app: frontend 
spec: 
containers: 
- name: frontend 
image: frontend:latest 
ports: 
- containerPort: 80 
RUN: 
kubectl apply -f frontend-deployment.yaml 


---

## Page 19

3. 
4. 
18
Deploy the Database: 
yaml
apiVersion: apps/v1 
kind: Deployment 
metadata: 
Service Definitions: 
o 
Frontend Service: 
yaml
apiVersion: v1 
kind: Service 
metadata: 
name: db-deployment 
spec: 
replicas: 1 
selector: 
matchLabels: 
app: database 
template: 
metadata: 
labels: 
app: database 
spec: 
containers: 
- name: database 
image: mysql:5.7 
env: 
- name: MYSQL_ROOT_PASSWORD 
value: "password" 
RUN: 
kubectl apply -f db-deployment.yaml 
name: frontend-service 
spec: 
selector: 
app: frontend 
ports: 
- protocol: TCP 
port: 80 
targetPort: 80 
type: LoadBalancer 
RUN: 
kubectl apply -f frontend-service.yaml 


---

## Page 20

19
o 
o 
yaml
apiVersion: v1 
kind: Service 
metadata: 
name: db-service 
spec: 
selector: 
app: database 
ports: 
- protocol: TCP 
port: 3306 
targetPort: 3306 
type: ClusterIP 
RUN: 
kubectl apply -f db-service.yaml 
yaml
apiVersion: v1 
kind: Service 
metadata: 
name: backend-service 
spec: 
selector: 
app: backend 
ports: 
- protocol: TCP 
port: 8080 
targetPort: 8080 
type: ClusterIP 
RUN: 
kubectl apply -f backend-service.yaml 
Backend Service: 
Database Service: 


---

## Page 21

This chapter has introduced the foundational concepts of Kubernetes, its architecture, and its
components. We've also provided practical examples and commands to get started with
Kubernetes using Minikube. Understanding these basics is essential for effectively deploying
and managing containerized applications in a Kubernetes environment. 
20
Pokémon GO uses Kubernetes to handle its massive user base. The architecture ensures high
availability and scalability, enabling millions of users to play the game without interruptions. 
Case Study: Pokémon GO 
Diagram: Kubernetes Deployment and Service 
lua
+------------------------------------- +
|
|
|+-----------------+ +------------+|
Kubernetes 
|
|
| | Frontend Pod
|| (nginx) 
| | Backend Pod | |
| |(app) 
||
|| +-----------+ | +-----------+||
|| |Container| | |Container|||
|| +-----------+ | +-----------+||
|+-----------------+ +------------+ |
|
|
|
|
|
|+---------------------------+ 
|| 
Service(LoadBalancer) 
|
|+---------------------------+
|
|
|
|
+
-
-
-
-
-
-
-
-
-
-
-
-
-
+
 
+
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
+
|
||DBPod
||(mysql) 
| |MoreBackend
| |Pods(app) 
||
||
|+-------------+ +----------------+|
|
|
|
|
|
+
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
+
|| 
Service(ClusterIP) 
||
|+----------------------------------+|
+------------------------------------- +


---

## Page 22

2. 
3. 
The control plane is responsible for maintaining the desired state of the cluster, such as which
applications are running and their configurations. 
1. kube-apiserver 
o 
Function: Exposes the Kubernetes API. 
o Command to interact: 
21
Kubernetes, often abbreviated as K8s, is an open-source container orchestration platform that
automates the deployment, scaling, and management of containerized applications.
Understanding its architecture is essential to effectively use and manage Kubernetes. In this
chapter, we will explore the key components of Kubernetes architecture, including the
control plane, nodes, and networking. We will also provide diagrams, real-world examples,
and commands to help you grasp the architecture comprehensively. 
The Kubernetes architecture consists of several components that work together to manage the
containerized applications in a cluster. 
1. Control Plane: Manages the Kubernetes cluster. 
o 
o 
o 
kube-apiserver: Serves the Kubernetes API. 
etcd: Stores the cluster data. 
kube-scheduler: Assigns work to nodes. 
o kube-controller-manager: Manages controllers (e.g., deployment controller). 
o cloud-controller-manager: Manages cloud-specific controllers. 
2. Nodes: Worker machines where containers run. 
o 
kubelet: Ensures containers are running on nodes. 
o kube-proxy: Manages network rules on nodes. 
o Container Runtime: Software that runs containers (e.g., Docker). 
: Consistent and highly-available key-value store used as Kubernetes' 
backing store for all cluster data. 
: Cluster configuration data, state, and metadata. 
: Watches for newly created pods with no assigned node and selects 
a node for them to run on. 
Overview 
etcd 
o
Control Plane Components 
 Function
o Exampleofstoreddata
kube-scheduler
o 
Function
Chapter 7: Kubernetes Architecture 
Kubernetes Components 
Kubernetes Architecture Diagram 
kubectl get nodes 


---

## Page 23

4. 
5. 
2. 
3. 
Worker nodes run the containerized applications and are managed by the control plane. 
1. kubelet 
o 
Function: Ensures that containers are running in a pod. 
o Command to check status: 
Spotify uses Kubernetes to manage its microservices architecture, handling everything from
music streaming to user playlists. By leveraging Kubernetes' robust architecture, Spotify
ensures a seamless user experience despite the large scale of operations. 
 
Function: Maintains network rules on nodes. 
: Forwards traffic to the appropriate pod based on 
service IP. 
: Runs containers. 
: Docker, containerd, CRI-O. 
: 
Consider deploying a multi-tier application consisting of a frontend, backend, and database.
Kubernetes will use the control plane to manage the deployment, scaling, and connectivity
between these components, ensuring high availability and fault tolerance. 
 
: Ensures that a pod is scheduled on a node with enough 
resources. 
: Runs controllers to regulate the state of the system. 
: 
▪ 
: Manages node operations. 
▪ 
: Ensures the specified number of pod replicas 
are running. 
EndpointsController
▪ 
: Populates Endpoints objects. 
: Runs cloud provider-specific controller loops. 
: Manages load balancers and storage volumes in cloud 
environments. 
22
systemctl status kubelet 
sudo apt-get install -y docker.io 
Node Components 
Case Study: Spotify 
kube-proxy
o 
o Exampleofnetworkrule
ContainerRuntime
o 
o Popularruntimes
o Dockerinstallationcommand
Function
o Schedulingexample
kube-controller-manager
o 
o 
Function
Typesofcontrollers
Node Controller
Replication Controller
cloud-controller-manager
o 
o Example
Function
Real-World Example: Multi-Tier Application Deployment 


---

## Page 24

3. 
:Controls the communication between pods. 
: 
23
Kubernetes networking is crucial for communication between components within the cluster. 
1. Cluster Networking 
o Function: Allows all pods to communicate with each other without NAT. 
o Example: A pod on Node A can communicate with a pod on Node B using its 
IP address. 
2. Service Networking 
o Function: Provides stable IP addresses and DNS names for pods. 
o 
o 
Service types: ClusterIP, NodePort, LoadBalancer. 
Creating a ClusterIP service: 
yaml
apiVersion: v1 
kind: Service 
metadata: 
Networking in Kubernetes 
Network Policies 
o 
o Exampleofanetworkpolicy
Function 
name: my-service 
spec: 
selector: 
app: MyApp 
ports: 
- protocol: TCP 
port: 80 
targetPort: 9376 
yaml
apiVersion: networking.k8s.io/v1 
kind: NetworkPolicy 
metadata: 
name: example-policy 
spec: 
podSelector: 
matchLabels: 
role: db 
policyTypes: 
- Ingress 
ingress: 
- from: 
- podSelector: 
matchLabels: 
role: frontend 


---

## Page 25

2. 
3. 
4. 
5. 
6. 
24
Describe a pod: 
kubectl describe pod <pod-name> 
Check pod status: 
kubectl get pods 
Apply a network policy: 
kubectl apply -f network-policy.yaml 
Command Summary 
1. Check nodes in the cluster: 
Deploy a sample application: 
kubectl create deployment nginx --image=nginx 
Expose the application via a service: 
kubectl expose deployment nginx --port=80 --type=NodePort 
Diagram: Kubernetes Network Components 
lua
+--------------------------------- +
kubectl get nodes 
| 
KubernetesCluster
|
|
|
|
|
|
|
|
|
|
|
|
|
|
|
|
|
+--------------------------------- +
| +----------------------------+
| | 
NodeA
| | | +------------------------
+| | | | | | | | | | 
PodA
||
||
||
| | +------------------------+|
| +----------------------------+
| +----------------------------+
+----------------+
| ContainerA
|
| | 
NodeB
|
| | +------------------------+|
| | |
| | |
| | |
| | +------------------------+|
| +----------------------------+
PodB
||
||
||
+----------------+
| ContainerB
|


---

## Page 26

Consider deploying a highly available web application that consists of multiple replicas
across different nodes. Kubernetes ensures that the application remains available even if
some nodes fail. This is achieved by distributing the pods across multiple nodes and using
services to load balance thetraffic. 
Case Study: Pokémon GO
Pokémon GO uses Kubernetes to handle its massive user base. The architecture ensures high
availability and scalability, enabling millions of users to play the game without interruptions. 
25
Real-World Example: High Availability Deployment 


---

## Page 27

2. 
4. 
 
: Download the Minikube installer from the Minikube GitHub 
release page and follow the installation instructions. 
:
Minikube is a tool that runs a single-node Kubernetes cluster on your local machine, making
it an excellent choice for learning and development. 
1. Install Minikube: 
o On Linux: 
Tip: Ensure you have a hypervisor like VirtualBoxor Hyper-V installed. Minikube supports
multiple drivers like Docker, KVM, Hyperkit, andmore. 
3. Verify Minikube Setup: 
kubectl get nodes 
 
Deploy a Sample Application:
 
kubectl create deploymenthello-minikube --
image=k8s.gcr.io/echoserver:1.4 
kubectl expose deployment hello-minikube --type=NodePort --port=8080 
26
 
Setting upaKubernetes cluster is a crucial step in leveraging Kubernetes for container
orchestration. In this chapter, we will cover both local and cloud setups, providing step-by-
step instructions for setting up a Kubernetes cluster using Minikube for local development
and Google Kubernetes Engine (GKE) for cloud deployment. We'll also discuss the setup of
kubeadm for a production-ready cluster. Real-world examples, diagrams, and commands will
be provided to ensure a smooth setup process. 
Overview
 On macOS: 
o OnWindows
Start Minikube
 
minikube start
Chapter 8: Setting Up a Kubernetes Cluster 
Local Setup with Minikube 
o
brew install minikube 
--driver=virtualbox
curl -LO
https://storage.googleapis.com/minikube/releases/latest/minikub
e-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube 


---

## Page 28

5. 
2. 
3.
4.
5. 
6. 
7. 
8. 
Access the application using the external IP address. 
GKE is a managed Kubernetes service provided by Google Cloud Platform (GCP) that
simplifies cluster management and scaling. 
1. Install Google Cloud SDK: 
27
Get the External IP: 
kubectl get services hello-gke 
 
Verify Cluster Setup: 
kubectl get nodes 
 
Create a GKE Cluster: 
gcloud container clusters create my-cluster --num-nodes=3 --zone=us-
central1-a 
Access the Application: 
minikube service hello-minikube 
Authenticate with GCP: 
gcloud auth login
gcloud config set project [YOUR_PROJECT_ID] 
Get Cluster Credentials: 
gcloud container clusters get-credentials my-cluster --zone=us-
central1-a 
Production Setup with kubeadm 
Deploy a Sample Application: 
kubectl create deployment hello-gke --image=gcr.io/google-
samples/hello-app:1.0
kubectl expose deployment hello-gke --type=LoadBalancer --port 80 --
target-port 8080 
Enable Kubernetes Engine API:
 
gcloudservicesenable container.googleapis.com 
Cloud Setup with Google Kubernetes Engine (GKE) 
curl https://sdk.cloud.google.com | bash
exec -l $SHELL 
gcloud init 


---

## Page 29

2. 
3. 
4. 
Configure kubectl for the current user: 
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config 
Install a Pod network add-on (e.g., Flannel): 
kubectl apply -f
https://raw.githubusercontent.com/coreos/flannel/master/Documen
tation/kube-flannel.yml 
: On each worker node, run the join command provided by 
on the master node: 
kubeadm is a tool that helps initialize a production-grade Kubernetes cluster. This setup
requires a minimum of two nodes: one master and one worker. 
1. Prepare the Nodes: 
o 
Install Docker: 
sudo apt-get update
sudo apt-get install -y docker.io 
28
Join Worker Nodes
 
Disable Swap: 
sudo swapoff -a 
Verify Cluster Setup: 
kubectl get nodes 
Initialize the Master Node: 
sudo kubeadm init --pod-network-cidr=10.244.0.0/16 
Install kubeadm, kubelet, and kubectl: 
sudo apt-get update && sudo apt-get install -y apt-transport-
https curl
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg|
sudo apt-key add -
cat <<EOF | sudo tee /etc/apt/sources.list.d/kubernetes.list
deb https://apt.kubernetes.io/ kubernetes-xenial main
EOF
sudo apt-get update
sudo apt-get install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl 
Real-World Example: Enterprise Application Deployment 
o 
o 
o 
o 
kubeadm init
 
sudo kubeadm join <master-ip>:6443 --token <token> --discovery-token-
ca-cert-hash sha256:<hash> 


---

## Page 30

This chapter provides detailed instructions for setting up a Kubernetes cluster in various
environments, ensuring that readers can choose the setup that best suits their needs. Each
section includes practical commands, setup guides, examples, and tips for a smooth
installation process. 
Here is a simplified diagram showing the components of a Kubernetes cluster set up with
kubeadm: 
CERN uses Kubernetes to manage its large-scale scientific computing workloads, ensuring
efficient use of resources and scalability across its infrastructure. 
Diagram: Kubernetes Cluster Setup 
Imagine deploying an enterprise-grade microservices application. By setting up a Kubernetes
cluster using kubeadm, you can manage a scalable and resilient environment for your
application. 
Case Study: CERN 
29
lua
+---------------------------------- +
| | | +----------------------------+
| | | | | | | | | | | 
KubernetesCluster 
|
|
MasterNode 
| |
| |
-kube-controller-manager| |
-kube-scheduler
-etcd 
-kube-apiserver 
| |
| |
| +----------------------------+ |
|
|
|
 
+
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
+
 
|
| | |
| | |
| | 
WorkerNode 
| |
| |
| |
| |
| +----------------------------+ |
-kubelet
-kube-proxy
-Pod 
|
 
|
 
+
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
+
 
|
 
|
 
|
 
|
 
|
|
 
|
 
|
 
|
 
WorkerNode 
| |
| |
| |
| |
+----------------------------+ |
|
+---------------------------------- +
-kubelet
-kube-proxy
-Pod 
|
|


---

## Page 31

2. Apply the deployment using 
A Kubernetes Deployment provides declarative updates to applications. It ensures that a
specified number of pod replicas are running at any given time. Deployments are the most
commonly used resource for managing stateless applications in Kubernetes. 
Key Concepts: 
• 
• 
ReplicaSet: Ensures a specified number of pod replicas are running at any time. 
Pod: The smallest deployable unit in Kubernetes, which can run one or more 
containers. 
Creating a Deployment: 
1. Create a deployment YAML file, 
: 
In this chapter, we will explore how to deploy applications on Kubernetes. We will cover
deployments, services, and configurations necessary to run a scalable and reliable application
in a Kubernetes cluster. Additionally, we will provide step-by-step commands, setup guides,
examples, and real-world scenarios. 
30
Chapter 9: Deploying Applications on Kubernetes 
Overview 
Deployments 
kubectl: 
kubectl apply -f deployment.yaml 
deploymen t.yaml
yaml 
apiVersion: apps/v1 
kind: Deployment 
metadata: 
name: nginx-deployment 
spec: 
replicas: 3 
selector: 
matchLabels: 
app: nginx 
template: 
metadata: 
labels: 
app: nginx 
spec: 
containers: 
- name: nginx 
image: nginx:1.14.2 
ports: 
- containerPort: 80 


---

## Page 32

3. Verify the service: 
3. Verify the deployment: 
2. Apply the service using 
31
Real-World Example: Web Server Deployment: Imagine you need to deploy a web server
that serves static content for a company. Using the above YAML file, you can deploy an
NGINX server that will handle the web traffic. 
Case Study: Medium: Medium uses Kubernetes to manage its web servers, ensuring high 
availability and scalability. By leveraging deployments, Medium can update its server images 
seamlessly without downtime. 
Services in Kubernetes define a logical set of pods and a policy by which to access them.
Services are used to expose applications running on a set of pods. 
Types of Services: 
• 
• 
• 
ClusterIP: Exposes the service on an internal IP in the cluster. 
NodePort: Exposes the service on each Node’s IP at a static port. 
LoadBalancer: Exposes the service externally using a cloud provider’s load balancer. 
Creating a Service: 
1. Create a service YAML file, service.yaml: 
kubectl get services 
yaml
apiVersion: v1
kind: Service
metadata:
name: nginx-service
spec:
selector:
app: nginx
ports:
- protocol: TCP
port: 
80
targetPort: 
80
type: LoadBalancer
kubectl get deployments
kubectl get pods 
kubectl: 
kubectl apply -f service.yaml 
Services 


---

## Page 33

2. Apply the ConfigMap: 
ConfigMaps: ConfigMaps are used to decouple configuration artifacts from image content,
allowing you to keep your containerized applications portable. 
Creating a ConfigMap: 
1. Create a ConfigMap YAML file, 
: 
Real-World Example: E-Commerce Backend: In an e-commerce application, different
services like user authentication, product catalog, and payment gateway can be exposed using
Kubernetes Services. This ensures that each microservice is accessible via a stable endpoint. 
Case Study: Uber: Uber uses Kubernetes services to expose its various microservices, 
ensuring that each service can be accessed reliably within the cluster and externally as 
needed. 
32
Using a ConfigMap in a Pod: 
yaml
```yaml
ConfigMaps and Secrets 
apiVersion: v1
kind: 
Pod
metadata:
name: example-pod 
spec:
containers:
- name:example-container
image:example-image
env:
-name:DATABASE_URL 
valueFrom:
configMapKeyRef: 
name: example-config
key: database_url
- name: DATABASE_NAME
valueFrom:
configMapKeyRef:
name: example-config
key: database_name
kubectl apply -f configmap.yaml 
configmap.yaml
yaml 
apiVersion: v1 
kind: ConfigMap 
metadata: 
name: example-config 
data: 
database_url: "mongodb://example-mongo:27017" 
database_name: "exampledb" 
 
``` 


---

## Page 34

2. Apply the Secret: 
Secrets: Secrets are similar to ConfigMaps but are intended to hold sensitive information,
such as passwords or API keys. 
Creating a Secret: 
1. Create a Secret YAML file, 
: 
Real-World Example: Database Credentials: In a production environment, database
credentials should not be hardcoded in the application code. Instead, they should be stored
securely using Kubernetes Secrets. 
Case Study: Netflix: Netflix uses Kubernetes Secrets to manage sensitive information like 
API keys and database credentials, ensuring that these secrets are securely stored and 
accessed only by authorized pods. 
33
Using a Secret in a Pod: 
yaml
```yaml
apiVersion: v1
kind: Pod
metadata:
name: example-pod 
spec:
containers:
- name:example-container 
image:example-image 
env:
-name:USERNAME 
valueFrom:
secretKeyRef: 
name:
key:
example-secret 
username 
-name:PASSWORD 
valueFrom:
secretKeyRef: 
name:
key:
example-secret 
password 
kubectl apply -f secret.yaml 
secret.yaml
yaml 
apiVersion: v1 
kind: Secret 
metadata: 
name: example-secret 
type: Opaque 
data: 
username: YWRtaW4= # Base64 encoded 
password: MWYyZDFlMmU2N2Rm # Base64 encoded 
 
``` 


---

## Page 35

2. Apply the StatefulSet: 
3. Verify the StatefulSet: 
StatefulSets are used for managing stateful applications, such as databases or distributed
systems, where each instance has a unique identity and stable storage. 
Creating a StatefulSet: 
1. Create a StatefulSet YAML file, 
: 
Ingress is used to expose HTTP and HTTPS routes to services within a cluster, providing
load balancing, SSL termination, and name-based virtual hosting. 
Creating an Ingress Resource: 
Real-World Example: Database Clustering: StatefulSets are ideal for deploying clustered
databases like MySQL or Cassandra, where each node needs a stable network identity and
storage. 
Case Study: Shopify: Shopify uses StatefulSets to manage its database clusters, ensuring 
high availability and reliable data storage for millions of transactions. 
34
Ingress 
StatefulSets 
kubectl get statefulsets
kubectl get pods 
kubectl apply -f statefulset.yaml 
state fulset.yaml
yaml 
apiVersion: apps/v1 
kind: StatefulSet 
metadata: 
name: web 
spec: 
serviceName: "nginx" 
replicas: 3 
selector: 
matchLabels: 
app: nginx 
template: 
metadata: 
labels: 
app: nginx 
spec: 
containers: 
- name: nginx 
image: nginx 
ports: 
- containerPort: 80 


---

## Page 36

1. 
3. Verify the Ingress: 
 
2. Add a Helm repository: 
2. Apply the Ingress resource: 
Create an Ingress YAML file, 
yaml 
apiVersion: networking.k8s.io/v1 
kind: Ingress 
metadata: 
Helm is a package manager for Kubernetes, providing a way to define, install, and upgrade
applications. 
Installing Helm: 
1. Download and install Helm: 
Real-World Example: Web Traffic Routing: In a production environment, Ingress is used
to manage incoming web traffic, routing it to various services based on the URL path. 
Case Study: Airbnb: Airbnb uses Kubernetes Ingress to route traffic to its microservices, 
ensuring efficient load balancing and simplified traffic management. 
35
kubectl get ingress 
kubectl apply -f ingress.yaml 
ingress.yaml: 
name: example-ingress 
spec: 
rules: 
- host: example.com 
http: 
paths: 
- path: / 
pathType: Prefix 
backend: 
service: 
name: example-service 
port: 
number: 80 
helm repo add stable https://charts.helm.sh/stable 
curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-
helm-3 | bash 
Helm 


---

## Page 37

1
.
2
.
Search for a chart: 
helmsearchrepo nginx 
Install a chart: 
helm install my-nginx stable/nginx 
3. Verify the installation: 
Real-World Example: Application Deployment and Management: Helm simplifies the
deployment and management of complex applications by using Helm charts, which
encapsulate Kubernetes resources and configurations. 
Case Study: GitLab: GitLab uses Helm to manage its Kubernetes deployments, enabling 
seamless updates and rollback capabilities for its CI/CD platform. 
36
Deploying an Application with Helm: 
helm list 


---

## Page 38

1.
2.
3.
4
.
5
.
1.
2.
3.
1. 
 
Create a 
yaml 
global: 
 configuration file: 
Prometheus is a popular open-source monitoring and alerting toolkit, while Grafana is an
open-source platform for monitoring and observability that integrates with Prometheus to
provide visual dashboards. 
 
: Identify and resolve issues before they impact users. 
: Optimize resource usage and plan capacity. 
: Ensure applications perform optimally. 
: Track and audit activities for security and compliance 
: Diagnose and resolve issues quickly. 
: CPU, memory, disk, and network usage. 
: Resource utilization, restarts, and errors. 
: Scheduler performance, controller health, and API server metrics. 
37
Monitoring and logging are crucial components in maintaining the health and performance of
a Kubernetes cluster. Effective monitoring helps in identifying issues proactively, while
robust logging enables detailed troubleshooting and auditing. In this chapter, we'll explore
various tools and techniques for monitoring and logging in Kubernetes. We will cover setup
guides, commands, examples, diagrams, and real-world scenarios to provide a comprehensiv
understanding. 
 Node Metrics
 Pod Metrics
 Cluster Metrics
InstallPrometheus: 
o 
 Proactive IssueDetection
 Resource Management
 Performance Optimization
 Security and Compliance
purposes.
Troubleshooting
Chapter 10: Monitoring and Logging in Kubernetes 
 
Overview 
Monitoring Kubernetes
Key Metrics to Monitor 
Prometheus and Grafana 
Setting Up Prometheus and Grafana 
Why Monitoring and Logging are Important 
prometheus.yml
scrape_interval: 15s 
scrape_configs: 
- job_name: 'kubernetes-apiservers' 
kubernetes_sd_configs: 
- role: endpoints 
scheme: https 
tls_config: 
ca_file: 
/var/run/secrets/kubernetes.io/serviceaccount/ca.crt 


---

## Page 39

2. 
3. 
4. 
Forward the Grafana port: 
kubectl port-forward service/grafana 3000:80 
 
: 
Deploy Grafana using Helm: 
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
helm install grafana grafana/grafana 
Open your browser and go to
and the retrieved password. 
In Grafana, go to 
Click
URL (
, select 
Deploy Prometheus using Helm: 
helm repo add prometheus-community https://prometheus-
community.github.io/helm-charts 
helm repo update 
helm install prometheus prometheus-community/prometheus 
 
: 
Get the Grafana admin password: 
kubectl get secret --namespace default grafana -o
jsonpath="{.data.admin-password}" | base64 --decode ; echo 
 and log in with 
. 
, and enter the Prometheus server 
). 
38
o 
o 
o 
http://localhost:3000
 
insecure_skip_verify: true 
bearer_token_file: 
/var/run/secrets/kubernetes.io/serviceaccount/token
 
relabel_configs: 
- source_labels: [__meta_kubernetes_namespace,
__meta_kubernetes_service_name,
__meta_kubernetes_endpoint_port_name] 
action: keep
regex: default;kubernetes;https 
- job_name: 'kubernetes-nodes' 
kubernetes_sd_configs: 
- role: node
relabel_configs: 
- action: labelmap 
regex: __meta_kubernetes_node_label_(.+) 
- target_label: __address__ 
replacement: kubernetes.default.svc:443 
- source_labels: [__meta_kubernetes_node_name] 
regex: (.+) 
target_label: kubernetes_node 
http://prometheus-server.default.svc.cluster.local:80
admin 
InstallGrafana
o 
Access Grafana
o 
Add PrometheusDataSourceinGrafana: 
o
o 
Configuration > Data Sources
Adddatasource
Prometheus


---

## Page 40

5. 
1
.
2
.
3
.
1. 
cluster. 
 
: 
Deploy Elasticsearch using Helm: 
helm repo add elastic https://helm.elastic.co
helm repo update
helm install elasticsearch elastic/elasticsearch 
: Logs collected and stored by individual nodes.
: Centralized logging for the entire cluster. 
: Logs generated by the applications running in the 
 
: 
Create dashboards to visualize metrics like CPU usage, memory usage, and
pod health. 
The EFK stack is a popular logging solution for Kubernetes, consisting of Elasticsearch for
storage, Fluentd for log collection and forwarding, and Kibana for log visualization. 
39
CreateDashboards
o 
Install Elasticsearch
o 
Node Level Logging
Cluster Level Logging
Application Level Logging
 
lua
+---------------------------------------------------- +
|
|
|+------------+ 
KubernetesCluster 
|
|
+---------+|
+-------------+ 
|| Prometheus|<-->|Grafana 
|<-->|Users 
||
|+------------+
|
|+------------+
||NodeExporter|
|+------------+
|
|+------------+
||KubeState | 
+-------------+ 
+---------+|
|
|
|
|
|
|
|
|
|| Metrics 
| 
|+------------+
+---------------------------------------------------- +
Logging in Kubernetes
Key Logging Strategies 
|
Setting Up EFK Stack 
Diagram:MonitoringSetup
EFK Stack (Elasticsearch, Fluentd, Kibana) 


---

## Page 41

2. 
3. 
4. 
 
: 
Forward the Kibana port: 
kubectl port-forward service/kibana 5601:5601 
 
: 
Deploy Kibana using Helm: 
helm install kibana elastic/kibana 
Open your browser and go to 
Apply the Fluentd DaemonSet: 
kubectl apply -f fluentd-daemonset.yaml 
 
: 
Deploy Fluentd with Kubernetes DaemonSet: 
apiVersion: apps/v1
kind: DaemonSet
metadata: 
40
InstallKibana
o 
InstallFluentd
o 
Access Kibana
o 
o 
o 
http://localhost:5601. 
name: fluentd
namespace: kube-system 
spec: 
selector: 
matchLabels: 
name: fluentd 
template: 
metadata:
labels: 
name: fluentd 
spec: 
containers:
- name: fluentd 
image: fluent/fluentd-kubernetes-daemonset:v1-debian-
elasticsearch-1 
env:
- name: FLUENT_ELASTICSEARCH_HOST 
value: "elasticsearch.default.svc.cluster.local" 
- name: FLUENT_ELASTICSEARCH_PORT 
value: "9200" 
volumeMounts:
- name: varlog 
mountPath: /var/log 
- name: varlibdockercontainers 
mountPath: /var/lib/docker/containers
readOnly: true 
volumes: 
- name: varlog 
hostPath: 
path: /var/log 
- name: varlibdockercontainers 
hostPath: 
path: /var/lib/docker/containers 


---

## Page 42

Consider a web application with multiple microservices running in a Kubernetes cluster.
Implementing monitoring and logging using the Prometheus-Grafana stack for monitoring
and the EFK stack for logging provides comprehensive insights into the application's health
and performance. 
1. Setup Monitoring: 
o Deploy Prometheus and Grafana. 
o Create dashboards to monitor key metrics like response times, error rates, and 
resource usage. 
2. Setup Logging: 
o 
Deploy Elasticsearch, Fluentd, and Kibana. 
o Configure Fluentd to collect logs from all microservices and forward them to 
Elasticsearch. 
Use Kibana to create visualizations and dashboards for log analysis. 
o 
3. Alerting: 
o Configure Prometheus to send alerts based on predefined thresholds, such as 
high CPU usage or increased error rates. 
o Integrate with alerting systems like PagerDuty or Slack for real-time 
notifications. 
Monitoring and logging are vital for maintaining the reliability, performance, and security of
your Kubernetes clusters. By using tools like Prometheus, Grafana, Elasticsearch, Fluentd,
and Kibana, you can gain valuable insights into your system's behavior and quickly respond
to issues. This chapter has provided a comprehensive guide to setting up and using these
tools, ensuring you are well-equipped to manage your Kubernetes environments effectively. 
41
Summary 
Diagram: EFK Stack 
lua
+-------------------------------------------------- +
Real-World Example: Monitoring and Logging for a Web Application 
|
|
|+-------------+ 
KubernetesCluster 
|
|
+---------+|
+------------+ 
||Elasticsearch|<--|Fluentd 
|<--|Pods 
||
|+-------------+ |
| 
| | | +----------------------------------------------
---- +
+------------+ 
+---------+|
|
+------------+ 
|
|
|
| Kibana 
|
+------------+ 
|


---

## Page 43

1.
2.
3.
4.
1
.
2
.
3
.
1. 
2. 
 
: 
Create an HPA YAML file (
yaml 
apiVersion: autoscaling/v1 
kind: HorizontalPodAutoscaler 
metadata: 
): 
: 
Ensure the metrics server is running in your cluster: 
kubectl apply -f https://github.com/kubernetes-sigs/metrics-
server/releases/latest/download/components.yaml 
 
: Ensure your application can handle more users or data. 
: Scale down resources during low demand to save costs. 
: Improve fault tolerance and application availability. 
: Maintain optimal performance by balancing the load. 
 Horizontal Scaling: Adding or removing instances of an application (pods). 
Vertical Scaling: Adding more resources (CPU, memory) to a single instance.
Autoscaling: Automatically adjusting the number of instances based on metrics like
CPU utilization or custom metrics. 
The Horizontal Pod Autoscaler automatically scales the number of pods in a deployment or
replica set based on observed CPU utilization or other select metrics. 
42
One of Kubernetes' most powerful features is its ability to scale applications seamlessly. This
chapter will cover how to scale applications in Kubernetes, both manually and automatically,
to handle varying loads efficiently. We will explore key concepts, commands, setup guides,
examples, diagrams, and real-world scenarios to provide a comprehensive understanding of
scaling in Kubernetes. 
Prerequisites
o 
Define an HPA
o 
 HandlingIncreasedLoad
 Cost Efficiency
 Resilience
 PerformanceOptimization
Chapter 11: Scaling Applications in Kubernetes 
 
Overview 
Key Concepts 
Setting Up HPA 
Why Scaling is Important 
Horizontal Pod Autoscaler (HPA) 
hpa.yaml
name: my-app-hpa 
spec: 
scaleTargetRef: 
apiVersion: apps/v1 
kind: Deployment 
name: my-app 


---

## Page 44

3. 
2. 
Apply the deployment: 
kubectl apply -f deployment.yaml 
 
Create an HPA YAML file (
yaml 
 
: 
Check the status of the HPA: 
kubectl get hpa my-app-hpa 
Apply the HPA configuration: 
kubectl apply -f hpa.yaml 
): 
Consider a web application running in a Kubernetes cluster. The application experiences
varying loads throughout the day. Using HPA, you can automatically adjust the number of
pods based on CPU utilization. 
1. Deploy the Web Application: 
o Create a deployment YAML file (
): 
43
o 
o 
minReplicas: 2
maxReplicas: 10
targetCPUUtilizationPercentage: 50 
hpa-web-app.yaml
deployment.ya ml
yaml 
apiVersion: apps/v1 
kind: Deployment 
metadata: 
name: web-app 
spec: 
replicas: 2 
selector: 
matchLabels: 
app: web-app 
template: 
metadata: 
labels: 
app: web-app 
spec: 
containers: 
- name: web-app 
image: my-web-app:latest 
ports: 
- containerPort: 80 
resources: 
requests: 
cpu: "100m" 
limits: 
cpu: "200m" 
Verify HPA
o 
Set UpHPAfortheWebApplication: 
o 
Real-World Example: Scaling a Web Application 


---

## Page 45

1. 
2. 
 
: 
Create a VPA YAML file (
yaml 
 
: 
Apply the VPA components: 
kubectl apply -f
https://github.com/kubernetes/autoscaler/releases/latest/downlo
ad/vertical-pod-autoscaler.yaml 
Apply the HPA configuration: 
kubectl apply -f hpa-web-app.yaml 
): 
The Vertical Pod Autoscaler automatically adjusts the resource limits and requests for
containers to optimize resource utilization. 
44
o 
vpa.yaml
apiVersion: autoscaling/v1
kind: HorizontalPodAutoscaler
metadata: 
name: web-app-hpa 
spec: 
scaleTargetRef: 
apiVersion: apps/v1
kind: Deployment
name: web-app 
minReplicas: 2
maxReplicas: 10
targetCPUUtilizationPercentage: 60 
 
lua
+--------------------------------------------------- +
|
|
|+------------------+ 
KubernetesCluster 
|
|
+----------------------+ |
|HorizontalPod
|Autoscaler(HPA)
+---------+------------+ |
||
|| 
Metrics
Server 
|
|
|+--------+---------+ 
| |
| |
|
|
|
v
|
v
|
|
|
| +-------+------+ 
+--------+--------+ 
| | 
CPUUsage | 
|
| 
AdjustNumber |
| 
|
|
| | 
Metrics 
| 
ofPods 
| +-------+------+ 
+--------+--------+ 
|
|
|
|
|
|
|
v
|
v
| +-------+-------+ 
+---------+---------+ 
| | | | | +---------
-------+ 
Application | 
| 
ScaledPods 
|
+---------------------+ 
|
|
Deployment 
| 
|
+--------------------------------------------------------- +
Vertical Pod Autoscaler (VPA) 
Setting Up VPA 
Diagram:HPAWorkflow
InstallVPA
o 
Define a VPA
o 


---

## Page 46

3. 
 
: 
Check the status of the VPA: 
kubectl get vpa my-app-vpa 
Real-World Example: Scaling a Database Service 
Consider a database service running in a Kubernetes cluster. The service requires more CPU
and memory during peak hours. Using VPA, you can automatically adjust the resource
requests and limits for the database pods. 
Apply the VPA configuration: 
kubectl apply -f vpa.yaml 
1. Deploy the Database Service: 
o Create a deployment YAML file (
): 
45
o 
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata: 
name: my-app-vpa 
spec: 
targetRef: 
apiVersion: "apps/v1" 
kind:
name: 
Deployment
my-app 
updatePolicy: 
updateMode: "Auto" 
db-deployment .y aml
yaml 
apiVersion: apps/v1
kind: Deployment
metadata:
name:db-service
spec:
replicas: 1
selector:
matchLabels:
app: db-service
template:
metadata:
labels:
app: db-service
spec:
containers:
- name: db-service
image: my-db-service:latest 
resources:
requests:
memory: "1Gi"
cpu: "500m"
limits:
memory: "2Gi"
cpu: "1"
Verify VPA
o 


---

## Page 47

2. 
2. 
Apply the deployment: 
kubectl apply -f db-deployment.yaml 
 
Create a VPA YAML file (
yaml 
apiVersion: autoscaling.k8s.io/v1 
kind: VerticalPodAutoscaler 
metadata: 
Apply the VPA configuration: 
kubectl apply -f vpa-db-service.yaml 
): 
Sometimes, you may need to manually scale your applications. Kubernetes makes it easy to
scale deployments up or down with a simple command. 
1. Scale Up: 
Scaling is a fundamental aspect of managing applications in Kubernetes. Whether you are
scaling horizontally by adding more pods or vertically by increasing resource limits,
Kubernetes provides robust tools to ensure your applications can handle varying loads
efficiently. This chapter has covered both manual and automatic scaling methods, including
Horizontal Pod Autoscaler and Vertical Pod Autoscaler, along with practical examples and
setups. Understanding these concepts and tools will help you maintain optimal performance
and reliability for your applications in Kubernetes. 
46
o 
o 
kubectl scale deployment my-app --replicas=5 
kubectl scale deployment my-app --replicas=2 
vpa-db-service.yaml
name: db-service-vpa 
spec: 
targetRef: 
apiVersion: "apps/v1" 
kind: 
name: 
Deployment 
db-service 
updatePolicy: 
updateMode: "Auto" 
Scale Down: 
Set UpVPAfortheDatabaseService: 
o 
Summary 
Manual Scaling 


---

## Page 48

1.
2.
3.
4.
1.
2.
3
.
4
.5.
 
vulnerabilities. 
: Safeguard sensitive data from unauthorized access. 
: Meet regulatory and compliance requirements. 
: Ensure the integrity and availability of your applications. 
: Reduce the risk of attacks and breaches. 
 
: Verify and control access to the cluster. 
: Define rules for pod communication. 
: Securely manage sensitive information like passwords and
: Enforce security standards for pod specifications. 
: Ensure that container images are secure and free from 
Role-Based Access Control (RBAC) is a method for regulating access to resources based on
the roles of individual users within your Kubernetes cluster. 
1. Define Roles and RoleBindings: 
o Create a role YAML file (
): 
Security is a crucial aspect of managing any system, and Kubernetes is no exception.
Ensuring that your Kubernetes cluster is secure involves multiple layers, from securing the
cluster nodes to securing the applications running within the cluster. This chapter will cover
various security best practices, setup guides, commands, examples, diagrams, and real-world
scenarios to help you secure your Kubernetes cluster effectively. 
47
 Data Protection
 Compliance
 Reliability
 Risk Mitigation
 AuthenticationandAuthorization
 Network Policies
 Secrets Management
keys.
Pod Security Policies
 ImageSecurity
Chapter 12: Securing Your Kubernetes Cluster 
 
Overview 
Key Concepts 
Why Security is Important 
Authentication and Authorization
Setting Up Role-Based Access Control (RBAC) 
role.yaml
yaml 
apiVersion: rbac.authorization.k8s.io/v1 
kind: Role 
metadata: 
namespace: default 
name: pod-reader 
rules: 
- apiGroups: [""] 
resources: ["pods"] 
verbs: ["get", "list", "watch"] 


---

## Page 49

1. 
Apply the configurations: 
kubectl apply -f role.yaml
kubectl apply -f rolebinding.yaml 
Create a RoleBinding YAML file (
yaml 
apiVersion: rbac.authorization.k8s.io/v1 
kind: RoleBinding 
metadata: 
 
: 
Create a network policy YAML file (
yaml 
apiVersion: networking.k8s.io/v1 
kind: NetworkPolicy 
metadata: 
): 
): 
Network policies in Kubernetes allow you to control the communication between pods and
services within your cluster. 
48
o 
o 
 
lua
+-------------------------------------------------- +
|
|
|+-------------------+ 
KubernetesCluster 
|
|
+----------------------+|
| 
| -read-pods 
+----------------------+|
|
|
|
|
|
+-------------------------------------------------- +
Network Policies 
|| 
|| -pod-reader 
Roles 
| 
| 
|+-------------------+ 
|
|+-------------------+ 
RoleBindings 
||
||
|| 
Users 
|
| 
|+-------------------+ 
|| -jane 
rolebinding.ya ml
name: read-pods 
namespace: default 
subjects: 
- kind: User 
name: jane 
apiGroup: rbac.authorization.k8s.io 
roleRef: 
kind: Role 
name: pod-reader 
apiGroup: rbac.authorization.k8s.io 
networkpolic y.yaml
name: allow-ingress 
namespace: default 
spec: 
podSelector: 
matchLabels: 
Diagram:RBAC Setup
Setting Up Network Policies 
Define a Network Policy
o 


---

## Page 50

1. 
2. 
Apply the secret: 
kubectl apply -f secret.yaml 
Apply the network policy: 
kubectl apply -f networkpolicy.yaml 
 
: 
Create a secret YAML file (
yaml 
apiVersion: v1 
kind: Secret 
metadata: 
): 
 
: 
Create a pod YAML file that uses the secret (
yaml 
Managing sensitive data such as passwords, tokens, and keys securely is essential in any
system. 
): 
49
o 
o 
role:
db
policyTypes:
- Ingress
ingress:
- from:
-podSelector: 
matchLabels: 
role: frontend 
lua
+-------------------------------------------------- +
|
|
|+-----------+ 
KubernetesCluster 
|
|
|
|
|
|
|
|
|
|
|
+-------------------------------------------------- +
Secrets Management 
+-----------+
|
|
+-----------+ 
|| PodA 
|<---->| PodB 
||(frontend)|
|+-----------+
| |+-----------
+ 
|(db) 
|| PodC
||(other) 
|X
|
|+-----------+ 
pod-using-secret.yaml
secret.yaml
name: db-secret 
type: Opaque 
data: 
username: YWRtaW4= # base64 encoded 'admin' 
password: MWYyZDFlMmU2N2Rm # base64 encoded '1f2d1e2e67df' 
Diagram:NetworkPolicy
Using Kubernetes Secrets 
Create a Secret
o 
Use theSecretinaPod
o 


---

## Page 51

1. 
 
: 
Create a PSP YAML file (
yaml 
apiVersion: policy/v1beta1 
kind: PodSecurityPolicy 
metadata: 
Apply the pod configuration: 
kubectl apply -f pod-using-secret.yaml 
): 
Pod Security Policies (PSP) are cluster-level resources that control the security-related
attributes of pod creation. 
50
o 
apiVersion: v1
kind: 
Pod
metadata: 
name: mypod 
spec: 
containers:
- name: mycontainer 
image: nginx
env:
- name: DB_USERNAME
 
 
 
 
 
 
 
valueFrom: 
secretKeyRef:
name: db-secret
key: username
- name: DB_PASSWORD
valueFrom: 
secretKeyRef:
name: db-secret
key: password
psp.yaml
name: restricted 
 
lua
+-------------------------------------------------- +
|
|
|+----------------------+ 
KubernetesCluster 
|
|
|
|
|
|
|
|
|
|
|
|
|
|
+-------------------------------------------------- +
Pod Security Policies 
|| 
Secrets 
|
|
|+----------------------+
|
|+----------------------+ 
|| -db-secret 
|| 
Pods 
|
| 
| 
| 
| 
|+----------------------+ 
|| -mypod 
|| -uses: 
|| 
|| 
-DB_USERNAME 
-DB_PASSWORD 
Diagram:SecretsManagement
Setting Up Pod Security Policies 
Define a Pod Security Policy
o 


---

## Page 52

2. 
Apply the PSP: 
kubectl apply -f psp.yaml 
Create a role binding (
yaml 
apiVersion: rbac.authorization.k8s.io/v1 
kind: RoleBinding 
metadata: 
Apply the role and role binding: 
kubectl apply -f role-psp.yaml
kubectl apply -f rolebinding-psp.yaml 
 
: 
Create a role and role binding YAML file (
yaml 
apiVersion: rbac.authorization.k8s.io/v1 
kind: Role 
metadata: 
): 
): 
51
o 
o 
o 
spec: 
privileged: 
false
volumes: - 'emptyDir'
- 
'hostPath' 
-
'secret'
allowedCapabilities:
- 
'NET_ADMIN'
hostNetwork: 
false
hostIPC: 
false
hostPID: 
false
runAsUser: 
rule: 'MustRunAsNonRoot' 
rolebinding-psp.yaml
name: psp-rolebinding 
namespace: default 
subjects: 
- kind: Group 
name: system:serviceaccounts 
apiGroup: rbac.authorization.k8s.io 
roleRef: 
kind: Role 
name: psp-role 
apiGroup: rbac.authorization.k8s.io 
role-psp .yaml
name: psp-role 
namespace: default 
rules: 
- apiGroups: ['policy'] 
resources: ['podsecuritypolicies'] 
verbs: ['use'] 
resourceNames: ['restricted'] 
Bind thePSPtoaRole
o 


---

## Page 53

1
.
2
.1
.
2
.
3. 
 
: 
Follow the installation instructions from the Trivy GitHub repository. 
: 
Scan a Docker image: 
trivy image nginx:latest 
Ensuring that your container images are secure and free from vulnerabilities is critical. 
Clair: Clair is an open-source project for the static analysis of vulnerabilities in
application containers (currently including OCI and Docker).
Trivy: Trivy is a simple and comprehensive vulnerability scanner for containers. 
 
: 
Add a step in your CI/CD pipeline to scan images before deploying them. 
Securing a Kubernetes cluster involves multiple layers of security practices and tools. By
implementing authentication and authorization through RBAC, defining network policies,
managing secrets securely, enforcing pod security policies, and ensuring image security, you
can create a robust and secure Kubernetes environment. This chapter has provided detailed
steps, commands, and examples to help you secure your Kubernetes cluster effectively 
Consider a web application running in a Kubernetes cluster. Implementing security measures
involves: 
1. RBAC: Define roles and bindings to control access. 
2. Network Policies: Restrict communication between pods. 
3. Secrets Management: Securely manage database credentials and API keys. 
4. Pod Security Policies: Enforce security standards for pods. 
5. Image Scanning: Scan images for vulnerabilities before deployment. 
52
Summary 
Image Security 
Example: Using Trivy 
Using Image Scanning Tools 
Real-World Example: Securing a Web Application 
Install Trivy
o
Scan anImage
o
Integrate Trivy with CI/CD
o 


---

## Page 54

1.
2.
3.
4.
1
.
2
.
3
.
1. 
Install Grafana: 
helm install grafana grafana/grafana 
Install Prometheus: 
helm install prometheus prometheus-community/prometheus 
 
Add the Helm repositories: 
helm repo add prometheus-community https://prometheus-
community.github.io/helm-charts 
helm repo add grafana https://grafana.github.io/helm-charts 
helm repo update 
 Monitoring: Tracking the health and performance metrics of your cluster and 
applications.
Logging: Capturing and storing logs generated by applications and system
components.
Alerting: Setting up alerts to notify you of critical events. 
 
: Identify and address issues before they impact users. 
: Monitor resource usage and optimize performance. 
: Detect and respond to security incidents. 
: Maintain logs for compliance and auditing purposes. 
Prometheus is an open-source monitoring system and time series database, while Grafana is
an open-source analytics and monitoring platform. Together, they provide a powerful
solution for monitoring Kubernetes clusters. 
Effective monitoring and logging are essential for maintaining the health and performance of
your Kubernetes cluster and the applications running within it. This chapter will cover how to
set up and use monitoring and logging tools, commands, setup guides, examples, diagrams,
and real-world scenarios to ensure you can keep a close eye on your cluster's operations. 
53
 ProactiveIssueDetection
 PerformanceOptimization
 Security
 ComplianceandAuditing
InstallPrometheusandGrafanausing Helm: 
o 
Chapter 13: Monitoring and Logging in Kubernetes 
Overview 
Key Concepts 
Setting Up Prometheus and Grafana 
Monitoring with Prometheus and Grafana 
Why Monitoring and Logging are Important 
o 
o 


---

## Page 55

2. 
3. 
4. 
Forward the Grafana port to access the dashboard: 
kubectl port-forward --namespace default svc/grafana 3000:80 
Access Grafana at http://localhost:3000 and log in with the default
username admin and the retrieved password. 
: 
In Grafana, go to Configuration > Data Sources.
Add a new data source and select Prometheus.
Enter the URL for Prometheus (e.g., http://prometheus-
server.default.svc.cluster.local:80). 
Save and test the data source. 
Consider a web application deployed in your Kubernetes cluster. You want to monitor the
application’s response times and error rates. 
1. Deploy the Web Application with Prometheus Exporter: 
o Create a deployment YAML file (web-app-deployment.yaml): 
 
: 
Ensure Prometheus is scraping metrics from your Kubernetes cluster. This is
typically configured automatically, but you can verify the configuration in the 
prometheus.yaml file. 
: 
Retrieve the Grafana admin password: 
kubectl get secret --namespace default grafana -o
jsonpath="{.data.admin-password}" | base64 --decode ; echo 
54
Configure Prometheus
o 
Access GrafanaDashboard
o 
Add PrometheusasaDataSourceinGrafana
o 
o 
o
o
o
o
yaml
apiVersion: apps/v1 
kind: Deployment 
metadata: 
name: web-app 
spec: 
 
lua
+----------------------+ 
+----------------------+
| | 
| 
| 
| 
|-
Nodes 
|-
Pods 
|-
Services | |
| | | | 
Kubernetes
Cluster 
| 
| 
| 
|<--|-
Dashboards 
Grafana 
|
|
| -VisualizesMetrics|
|
+----------------------+
|
|
|
| 
+-------------+
|Prometheus |<--|-->|
| -Scrapes 
+----------------------+
|
|
|
+----------------------+
Applications 
|
|
+-------------+ 
|
|
| 
|
| -Exporters 
| 
Metrics 
+----------------------+
Example: Monitoring a Web Application 
Diagram:Prometheusand GrafanaSetup


---

## Page 56

2. 
1. 
Install Kibana: 
helm install kibana elastic/kibana 
Install Elasticsearch: 
helm install elasticsearch elastic/elasticsearch 
Apply the deployment: 
kubectl apply -f web-app-deployment.yaml 
 
Add the Helm repositories: 
helm repo add elastic https://helm.elastic.co
helm repo update 
The EFK stack (Elasticsearch, Fluentd, and Kibana) provides a comprehensive logging
solution for Kubernetes. 
 
: 
In Grafana, create a new dashboard and add a panel.
Select Prometheus as the data source and enter a PromQL query to fetch the
metrics (e.g., http_requests_total for total requests).
Configure the panel to visualize response times and error rates. 
55
o 
o
o
o
o 
o 
replicas: 3
selector:
matchLabels:
app: web-app
template:
metadata:
labels:
app: web-app
spec:
containers:
- name: web-app
image: ports:
-containerPort:
env: 
- 
name:
PROMETHEUS_SCRAPE
my-web-app:latest 
80 
value: "true"
- name: PROMETHEUS_PORT
value: "8080"
CreateaGrafanaDashboard
InstallElasticsearch,Fluentd,and Kibana using Helm: 
o 
Setting Up EFK Stack 
Logging with Elasticsearch, Fluentd, and Kibana (EFK) 


---

## Page 57

2. 
3. 
4. 
Install Fluentd: 
helm repo add fluent https://fluent.github.io/helm-charts
helm repo update
helm install fluentd fluent/fluentd 
Access Kibana at http://localhost:5601. 
: 
In Kibana, configure an index pattern to start visualizing logs.
Go to Management > Index Patterns and create a new index pattern (e.g., 
fluentd-*). 
Consider a web application deployed in your Kubernetes cluster. You want to capture and
analyze logs from the application. 
1. Deploy the Web Application with Logging: 
o Create a deployment YAML file (web-app-logging-deployment.yaml): 
 
: 
Ensure Fluentd is collecting logs from your Kubernetes cluster and forwarding
them to Elasticsearch. This is typically configured automatically, but you can
verify the configuration in the Fluentd configuration file. 
: 
Forward the Kibana port to access the dashboard: 
kubectl port-forward svc/kibana-kibana 5601:5601 
56
o 
o
o
yaml
apiVersion: apps/v1 
kind: Deployment 
metadata: 
name: web-app 
spec: 
replicas: 3 
selector: 
matchLabels: 
 
lua
+----------------------+ 
+----------------------+
| | | -VisualizesLogs 
| 
| 
| 
|-
Nodes |- Pods
|- Services |
| | | | | 
Kubernetes
Cluster 
| 
| 
| 
|<--|-
Dashboards 
Kibana 
|
|
|
|
+----------------------+
|
|
|
| 
+-------------+ 
+----------------------+
|
|
|
+----------------------+
|Fluentd 
|<--|-->|
|
| -StoresLogs 
Elasticsearch 
| -Collects | 
|
|
| 
|
+-------------+ 
Logs 
| 
+----------------------+
Example: Logging a Web Application 
o
ConfigureKibana
Configure Fluentd
o 
Access KibanaDashboard
o 
Diagram:EFKStackSetup


---

## Page 58

2. 
1. 
2. 
Apply the deployment: 
kubectl apply -f web-app-logging-deployment.yaml 
 
: 
Install Alertmanager using Helm: 
helm install alertmanager prometheus-community/alertmanager 
 
: 
Create an Alertmanager configuration file (
yaml 
global: 
): 
Prometheus Alertmanager handles alerts sent by client applications such as Prometheus and
manages those alerts, including silencing, inhibition, aggregation, and sending out
notifications. 
 
: 
In Kibana, create a new dashboard and add a visualization.
Select the index pattern (e.g., fluentd-*) and create visualizations to analyze
log data (e.g., error rates, request logs). 
57
o 
o
o 
app: web-app
template:
metadata:
labels:
app: web-app
spec:
containers:
- name: web-app
image:
ports:
-containerPort:
env:
- name: LOGGING
value: "true"
my-web-app:latest 
80 
alertma nager.yaml
resolve_timeout: 5m 
route: 
receiver: 'default' 
receivers: 
- name: 'default' 
email_configs: 
- to: 'your-email@example.com' 
from: 'alertmanager@example.com' 
smarthost: 'smtp.example.com:587' 
Install Alertmanager
o 
Configure Alertmanager
o 
CreateaKibanaDashboard
Setting Up Prometheus Alertmanager 
Alerting with Prometheus Alertmanager 


---

## Page 59

3. 
1. 
2. 
Apply the alerting rule: 
kubectl apply -f alert-rules.yaml 
Apply the configuration: 
kubectl create configmap alertmanager-config --from-
file=alertmanager.yaml 
kubectl apply -f alertmanager-deployment.yaml 
 
: 
Create an alerting rule YAML file (
yaml 
groups: 
- name: example 
Apply the Prometheus configuration: 
kubectl apply -f prometheus.yaml 
 
: 
Update Prometheus configuration to use Alertmanager (
yaml
alerting: 
): 
 
: 
Check the Alertmanager dashboard to see active alerts and notifications. 
): 
58
o 
o 
o 
alertmanagers: 
- static_configs: 
- targets: 
- alertmanager:9093 
auth_username: 'alertmanager@example.com'
auth_password: 'yourpassword' 
prometheus.yaml
alert-rules.yaml
rules: 
- alert: HighCPUUsage 
expr: node_cpu_seconds_total{mode="idle"} < 20 
for: 2m 
labels: 
severity: critical 
annotations: 
summary: "High CPU usage detected on {{ $labels.instance
description: "CPU usage is above 80% on {{ 
}}" 
$labels.instance }} for more than 2 minutes." 
Verify Alerts in Alertmanager
o 
Create a Prometheus Alerting Rule
o 
Integrate Prometheus with Alertmanager
o 
Example: Alerting on High CPU Usage 


---

## Page 60

Monitoring and logging are vital components of managing a Kubernetes cluster. Using tools
like Prometheus, Grafana, Elasticsearch, Fluentd, Kibana, and Alertmanager, you can
effectively monitor the health and performance of your cluster, capture and analyze logs, and
set up alerts for critical events. This chapter has provided detailed steps, commands,
examples, and diagrams to help you implement comprehensive monitoring and logging
solutions for your Kubernetes environment. 
59
Summary 


---

## Page 61

1
.
2
.
3
.
4
.
1
.
2
.
3
.
 Simplifies Deployment: Streamlines the deployment process with reusable Helm 
charts.
Manages Complexity: Handles the complexities of Kubernetes applications with
ease.
Version Control: Allows versioning of applications and rollbacks to previous
versions.
Consistent Environment: Ensures consistent application environments across
different clusters. 
Charts: Helm packages that contain all the resource definitions necessary to run an
application.
Releases: Instances of charts running in a Kubernetes cluster.
Repositories: Collections of Helm charts. 
60
Helm is a powerful package manager for Kubernetes, which simplifies the deployment and
management of applications. Helm uses charts to define, install, and upgrade even the most
complex Kubernetes applications. This chapter will cover the basics of Helm, its architecture,
commands, setup guides, examples, diagrams, and real-world scenarios to help you master
Helm and manage your Kubernetes applications effectively. 
Chapter 14: Helm and Kubernetes Package Management 
Overview 
Key Concepts 
Why Helm is Important 
Helm Architecture
Diagram: Helm Architecture 
sql
+-------------------------------------+ 
| | | +-----------------------------+ |
| | | | | | +---------------------------
--+ | +---------------------------------
----+ 
Helm Client 
|
|
|
|
|
|
|
| 
Command Line Tool
(install, 
upgrade,
rollback, delete) 
|
|
| 
|
v 
+-------------------------------------+ 
| | | +---------------------------
--+ 
Helm Library 
|
|
|
|
| 
| |
| +-----------------------------+ 
Helm API 
| 


---

## Page 62

1. 
2. 
1. 
2. 
For Linux: 
curl
https://raw.githubusercontent.com/helm/helm/main/scripts/get -
helm-3 | bash 
 
For macOS: 
brew install helm 
For Windows: 
choco install kubernetes-helm 
Update repositories: 
helm repo update 
 
: 
Search for a chart in a repository: 
 
helm search repo stable 
 
: 
Add the official Helm stable repository: 
helm repo add stable https://charts.helm.sh/stable 
61
o 
o 
o 
helm version 
Setting Up Helm in Kubernetes 
| 
|
+-------------------------------------+ 
|
v 
+-------------------------------------+ 
| | | +---------------------------
--+ 
Kubernetes API Server 
|
|
|
|
|
|
+-------------------------------------+ 
| | 
Processes Helm Requests |
| +-----------------------------+
| 
Installing Helm
Installing Helm on Your Local Machine 
Search for Charts
o 
Verify Installation: 
Add HelmRepositories
o 
DownloadandInstall Helm: 
o 


---

## Page 63

1. 
2. 
1. 
2. 
3. 
 
Edit 
 to set NGINX configuration: 
: Contains metadata about the chart. 
: Default configuration values for the chart. 
: Directory containing Kubernetes resource templates. 
62
Helm Basics
Creating a Helm Chart 
 
Diagram: Helm Chart Structure 
bash
 
mychart/ 
Example: Basic Helm Chart for NGINX 
Chart Structure: 
Deploy the Chart: 
helm install my-nginx ./nginx 
CustomizeValues: 
o 
Create a New Chart: 
helm create mychart 
Create NGINX Chart: 
helm create nginx 
o
o
o 
Chart.yaml
values.yaml
templates/
values.yaml
yaml 
replicaCount: 2 
image: 
repository: nginx 
tag: stable 
pullPolicy: IfNotPresent 
service: 
type: LoadBalancer 
port: 80 
Chart.yaml 
# A YAML file containing information about the chart
# The default configuration values for this chart # A
directory containing any charts upon which this # A
directory of templates that, when combined with
 values.yaml
charts/
chart depends 
templates/ 
values, will generate valid Kubernetes manifest files 
templates/tests/ # A directory containing test files 


---

## Page 64

1. 
2. 
3. 
4. 
5. 
6. 
1. 
2. 
 
: 
Customize 
yaml 
replicaCount: 3 
image: 
 
: 
Create a chart for the web application: 
helm create webapp 
 for the application: 
Consider deploying a web application using Helm. The web application consists of a front-
end service, a back-end service, and a database. 
63
Helm Commands 
Step-by-Step Guide 
Real-World Example: Deploying a Web Application 
List Releases: 
helm list 
Define Values
o 
Install a Chart: 
helm install <release-name> <chart-name> 
Upgrade a Release: 
helm upgrade <release-name> <chart-name> 
Rollback a Release: 
helm rollback <release-name> <revision> 
Uninstall a Release: 
helm uninstall <release-name> 
Get Release History: 
helm history <release-name> 
Create Helm Chart
o 
values.yaml
repository: my-webapp 
tag: latest 
pullPolicy: IfNotPresent 


---

## Page 65

3. 
4. 
5. 
6. 
7. 
 
Modify 
yaml 
replicaCount: 5 
 
List the releases: 
helm list 
Upgrade the release: 
helm upgrade my-webapp ./webapp 
Get the status of a release: 
helm status my-webapp 
 
: 
Rollback to a previous version if issues arise: 
helm rollback my-webapp1
 
: 
Define the templates for the front-end, back-end, and database in the
templates/ directory.
: 
 to update configurations (e.g., increase replicas): 
64
sql 
o 
o 
values.yaml
helm install my-webapp ./webapp 
service: 
type: LoadBalancer
port: 80 
backend: 
image: 
repository: my-backend
tag: latest 
pullPolicy: IfNotPresent
  
service: 
port: 8080 
database: 
image: 
repository: postgres 
tag: latest 
pullPolicy: IfNotPresent 
service: 
port: 5432 
DeploytheChart
Create Templates
o 
Rollback if Needed
o 
UpgradetheChart: 
o
MonitortheDeployment: 
o 
 
Diagram: Helm Release Lifecycle 


---

## Page 66

1.
2.
3.
4.
5.
 
: Follow semantic versioning for your charts to manage 
updates and rollbacks effectively. 
: Use values files to customize deployments for different 
environments (e.g., development, staging, production). 
: Ensure sensitive data is managed securely, using tools like 
helm-secrets to manage secrets. 
: Use Helm’s test framework to validate your charts before 
deploying them in production. 
: Integrate Helm with your CI/CD pipeline to automate 
deployments and updates. 
Helm is a powerful tool for managing Kubernetes applications, providing a robust and
flexible framework for defining, installing, and upgrading applications. By understanding
Helm’s architecture, mastering its commands, and following best practices, you can
streamline the deployment and management of your Kubernetes applications. This chapter
has provided detailed steps, commands, examples, and diagrams to help you effectively use
Helm in your Kubernetes environment. 
65
+--------------------+ 
+-------------------+
|
+-------------------+ 
| 
Create Chart 
| -> | 
Install Chart 
+--------------------+ 
|
v 
|
v 
+--------------------+ 
+-------------------+
|
+-------------------+ 
| Update Values 
| -> | 
Upgrade 
+--------------------+ 
|
v 
|
v 
+--------------------+ 
+-------------------+
|
+-------------------+ 
|
+--------------------+ 
Monitor 
| -> | 
Rollback 
Summary 
Best Practices for Helm 
 UseSemanticVersioning
 LeverageValuesFiles
 SecureYourCharts
 TestYourCharts
 AutomatewithCI/CD


---

## Page 67

1.
2.
3.
4.
1
.
2
.
3
.
1. 
2. 
3. 
Jenkins is a widely-used open-source automation server that facilitates CI/CD. 
Continuous Integration and Continuous Deployment (CI/CD) are essential practices for
modern software development, enabling teams to deliver high-quality software at a rapid
pace. In this chapter, we will explore how to set up a CI/CD pipeline for Kubernetes using
popular tools such as Jenkins, GitLab CI, and Argo CD. We will provide detailed steps,
commands, setup guides, examples, diagrams, and real-world scenarios to help you
implement an efficient CI/CD pipeline for your Kubernetes applications. 
 Continuous Integration (CI): The practice of integrating code changes into a shared 
repository frequently and automatically building and testing the code.
Continuous Deployment (CD): The practice of automatically deploying code
changes to production after they pass the CI pipeline.
Pipelines: Automated workflows that define the steps required to build, test, and
deploy applications. 
: Automates the process of building, testing, and deploying applications.
: Ensures consistent and reliable application deployments. 
: Speeds up the delivery of new features and bug fixes. 
: Provides rapid feedback to developers on code changes. 
66
 Automation
 Consistency
 Speed
 Feedback
Install Jenkins Using Helm: 
helm install jenkins jenkins/jenkins --namespace jenkins 
Create a Namespace for Jenkins: 
kubectl create namespace jenkins 
Add the Jenkins Helm Repository: 
helm repo add jenkins https://charts.jenkins.io
helm repo update 
Chapter 15: Continuous Integration andContinuous Deployment (CI/CD) with
Kubernetes 
 
Overview 
Key Concepts 
Why CI/CD is Important 
Installing Jenkins on Kubernetes 
Setting Up Jenkins for CI/CD with Kubernetes 


---

## Page 68

4. 
5. 
1
.
2
.
3. 
Access Jenkins at
credentials. 
 
: 
Forward the Jenkins port to access the dashboard: 
kubectl port-forward --namespace jenkins svc/jenkins 8080:8080 
 
: 
In Jenkins, create a new item and select "Pipeline". 
: 
Define the pipeline script using a Jenkinsfile: 
 and log in with the admin 
 
: 
Ensure Jenkins has access to the Docker registry and Kubernetes cluster.
Configure credentials in Jenkins for Docker and Kubernetes. 
67
Configure Credentials
o 
Access Jenkins Dashboard
o 
Create a New Pipeline Job
o
Configure the Pipeline Script
o
Retrieve Jenkins Admin Password: 
kubectl get secret --namespace jenkins jenkins -o
jsonpath="{.data.jenkins-admin-password}" | base64 --decode 
o 
http://localhost:8080
groovy
pipeline {
agent any
stages {
stage('Build'){
steps {
script {
sh'docker build -t my-app:latest .' 
}
}
}
stage('Test'){
steps {
script {
sh'docker run my-app:latest ./run-
tests.sh'
}
}
}
stage('Deploy'){
steps {
script {
kubectlapply -f k8s/deployment.yaml 
}
}
 
} 
} 
} 
Setting Up a Jenkins Pipeline for Kubernetes 


---

## Page 69

1. 
2. 
3. 
 
: 
On your GitLab instance, register a runner: 
sudo gitlab-runner register 
 
.gitlab-ci.yml File: 
Define the CI/CD pipeline in your repository: 
yaml
stages: 
 
: 
Use the following configuration for Kubernetes executor: 
yaml
concurrent = 4 
check_interval = 0 
[[runners]] 
GitLab CI is an integrated part of GitLab, providing powerful CI/CD capabilities. 
68
Setting Up GitLab Runner 
Setting Up GitLab CI for Kubernetes 
Create a
o 
ConfiguretheRunner
o 
Register a GitLab Runner
o 
name = "k8s-runner" 
url = "https://gitlab.com/" 
token = "YOUR_REGISTRATION_TOKEN" 
executor = "kubernetes" 
[runners.kubernetes] 
namespace = "gitlab-runner" 
image = "alpine:latest" 
privileged = true 
pull_policy = "always" 
- build 
- test 
- deploy 
build: 
stage: build 
script: 
- docker build -t my-app:latest . 
test: 
stage: test 
script: 
- docker run my-app:latest ./run-tests.sh 
deploy: 
stage: deploy 
script: 
- kubectl apply -f k8s/deployment.yaml 


---

## Page 70

1. 
2. 
3. 
4. 
1
.
2
.
3. 
4. 
Access Argo CD at 
 
: 
Forward the Argo CD server port: 
kubectl port-forward svc/argocd-server -n argocd 8080:443 
Argo CD is a declarative, GitOps continuous delivery tool for Kubernetes. 
 
: 
Ensure your Kubernetes manifests are stored in a Git repository. 
: 
In the Argo CD dashboard, add a new application and link it to your Git
repository. 
: 
Define the target cluster and namespace.
Set the path to the Kubernetes manifests within the repository. 
: 
Sync the application to deploy it to the Kubernetes cluster. 
69
Installing Argo CD 
Diagram: Argo CD Workflow 
diff
+--------------------+ 
Setting Up Argo CD for Kubernetes 
Deploying Applications with Argo CD 
SynctheApplication
o
ConfiguretheApplication
Access Argo CD Dashboard
o 
Install Argo CD Using kubectl: 
kubectl 
apply 
-n 
argocd 
-f
https://raw.githubusercontent.com/argoproj/argo
- cd/stable/manifests/install.yaml 
Create a Namespace for Argo CD: 
kubectl create namespace argocd 
o 
RetrieveArgoCDAdminPassword: 
kubectl get secret argocd-initial-admin-secret -n argocd -o
jsonpath="{.data.password}" | base64 --decode 
Create a Git Repository for Your Application
o
Add theGitRepositorytoArgoCD
o
o
o
https://localhost:8080. 
| 
| 
Git Repository | 
| 
| - Kubernetes Manifests 
| - Argo CD Configs | 
+--------------------+ 
| 


---

## Page 71

1.
2.
3. 
4. 
 
: 
Define the microservices in separate repositories or directories. 
: 
Create Jenkins pipelines for each microservice to build, test, and deploy them
independently. 
: 
Use Argo CD to manage the deployment of the entire application stack.
Define an Argo CD application for each microservice.
: 
Use Jenkins to trigger Argo CD syncs after each successful build and test
stage.
Example Jenkins pipeline step to trigger Argo CD sync: 
70
Consider a microservices application with multiple services, each managed independently but
deployed as part of a single CI/CD pipeline. 
 
v 
+--------------------+ 
| | | - Watches Git
Repos| 
| 
- 
Syncs
Manifests | +----------
----------+ 
Argo CD 
|
| 
|
v 
+--------------------+
| Kubernetes Cluster| 
|
| - Deploys Apps 
|
| 
+--------------------+ 
 
} 
} 
o
o
o
groovy
stage('DeploytoStaging') { 
steps {
script {
sh'argocd app sync my-microservice' 
}
Step-by-Step Guide 
Real-World Example: CI/CD Pipeline for a Microservices Application 
Integrate Jenkins with Argo CD
o
 DefineMicroservices
o
 CreateJenkinsPipelinesforEachService
o
ConfigureArgoCD to ManageDeployments


---

## Page 72

71
Implementing CI/CD with Kubernetes using tools like Jenkins, GitLab CI, and Argo CD can
significantly enhance your development and deployment processes. By automating the build,
test, and deployment steps, you can ensure consistent and reliable application releases. This
chapter has provided detailed steps, commands, examples, and diagrams to help you set up
and manage a robust CI/CD pipeline for your Kubernetes applications. 
Summary 
Diagram: CI/CD Pipeline for Microservices 
diff
+----------------------+ 
| Git Repository |
| - Service A Code
| - Service B Code 
|
|
|
|
| - Kubernetes Manifests
+----------------------+ 
|
v 
+----------------------+ 
| 
| 
| 
- 
Builds
Services 
| 
- 
Runs
Tests | - Triggers
Argo CD 
Jenkins 
|
|
|
|
|
+----------------------+ 
|
v 
+----------------------+ 
| 
| 
| - Syncs Manifests
| - Deploys to K8s 
Argo CD 
| 
| 
|
|
+----------------------+ 
|
v 
+----------------------+ 
| Kubernetes Cluster
| 
|
|
| - Runs Microservices |
+----------------------+ 


---

## Page 73

1.
2.
3.
4.
1
.
2
.
3
.
4
.
5
.
1. 
2. 
services. 
 
: 
Define a role with specific permissions (
yaml 
apiVersion: rbac.authorization.k8s.io/v1 
kind: Role 
metadata: 
): 
Securing Kubernetes clusters is critical for protecting your applications and data from
unauthorized access and potential threats. This chapter will cover various aspects of
Kubernetes security, including authentication and authorization, network policies, secrets
management, and best practices. Detailed steps, commands, setup guides, examples,
diagrams, and real-world scenarios will help you secure your Kubernetes environment
effectively. 
: Ensures sensitive data is protected from unauthorized access. 
: Helps meet regulatory requirements and industry standards. 
: Reduces the risk of attacks and vulnerabilities. 
: Maintains the integrity and availability of applications and 
 Authentication: Verifying the identity of users and services accessing the cluster. 
Authorization: Controlling access to resources based on user roles and permissions.
Network Policies: Defining rules for traffic flow between pods and services.
Secrets Management: Securely storing and managing sensitive information such as
passwords and API keys.
Pod Security Policies: Enforcing security standards at the pod level. 
72
Create a Role
o 
 Data Protection
 Compliance
 Threat Mitigation
 OperationalIntegrity
Create a Service Account: 
kubectl create serviceaccount <service-account-name> --namespace
<namespace> 
Chapter 16: SecuringKubernetes Clusters 
Overview 
Key Concepts 
Why Kubernetes Security is Important 
Authentication and Authorization
Setting Up Role-Based Access Control (RBAC) 
role.yaml
namespace: <namespace> 
name: <role-name> 
rules: 
- apiGroups: [""] 
resources: ["pods"] 


---

## Page 74

3. 
Apply the role: 
kubectl apply -f role.yaml 
 
Create a role binding (
yaml 
apiVersion: rbac.authorization.k8s.io/v1 
kind: RoleBinding 
metadata: 
Apply the role binding: 
kubectl apply -f role-binding.yaml 
): 
73
o 
o 
verbs: ["get", "list", "watch"] 
role-binding.yaml
name: <role-binding-name> 
namespace: <namespace> 
subjects: 
- kind: ServiceAccount 
name: <service-account-name> 
namespace: <namespace> 
roleRef: 
kind: Role 
name: <role-name> 
apiGroup: rbac.authorization.k8s.io 
 
sql
+-------------------+ 
|
| 
User/Service
(Authenticated) 
|
|
+-------------------+ 
|
v 
+-------------------+ 
|
| 
Service
Account 
|
| 
+-------------------+ 
|
v 
+-------------------+ 
|
| (Permissions) 
Role 
|
|
+-------------------+ 
|
v 
+-------------------+ 
|
| 
Kubernetes API 
|
|
+-------------------+ 
Server 
Bind theRoletotheServiceAccount: 
o 
Diagram:RBAC Workflow


---

## Page 75

1. 
Apply the network policy: 
kubectl apply -f network-policy.yaml 
 
 
: 
Example policy to allow traffic from a specific namespace (
): 
Network policies control the traffic flow between pods and services within the cluster. 
74
Network Policies 
Creating a Network Policy 
Diagram: Network Policy Flow 
lua
+-------------------+ 
Define a Network Policy
o 
o 
policy.yaml
yaml 
apiVersion: networking.k8s.io/v1 
kind: NetworkPolicy 
metadata: 
name: allow-namespace 
namespace: <namespace> 
spec: 
podSelector: 
matchLabels: 
app: <app-label> 
policyTypes: 
- Ingress 
- Egress 
ingress: 
- from: 
- namespaceSelector: 
matchLabels: 
name: <allowed-namespace> 
egress: 
- to: 
- namespaceSelector: 
matchLabels: 
name: <allowed-namespace> 
network-
+-------------------+
|
+-------------------+ 
| 
Namespace A 
|
+-------------------+ 
Namespace B 
| 
| +-----------+ 
| 
| +-----------+
|
| +-----------+ 
|
|
| 
| | Pod A1 
|<--+----------|->| Pod B1 
| +-----------+
+-------------------+ 
| 
+-------------------+ 
|
v 
|
v 
+-------------------+ 
+-------------------+
| Namespace Policy | |
+-------------------+ 
|
| 
Network Policy | 
(Allow B1) 
|
+-------------------+ 
| 


---

## Page 76

1. 
2. 
 
: 
Define a secret (
yaml 
apiVersion: v1 
kind: Secret 
metadata: 
Apply the secret: 
kubectl apply -f secret.yaml 
Apply the pod configuration: 
kubectl apply -f pod-with-secret.yaml 
): 
 :
Define a pod that uses the secret (
yaml
apiVersion: v1 
kind: Pod 
metadata: 
): 
Managing sensitive data securely is crucial for protecting application integrity. 
75
Secrets Management 
Using Kubernetes Secrets 
Create a Secret
o 
Access Secret in a Pod
o 
o 
o 
name: my-pod 
namespace: <namespace> 
spec: 
containers: 
- name: my-container
 
   
 
 
 
 
 
image: my-image
env: 
- name: USERNAME
valueFrom: 
secretKeyRef:
name: my-secret
key: username
- name: PASSWORD
valueFrom: 
secretKeyRef:
name: my-secret
key: password
secret.yaml
name: my-secret 
namespace: <namespace> 
data: 
username: <base64-encoded-username>
password: <base64-encoded-password>
 
pod-with-secret.yaml


---

## Page 77

1. 
 
Example PSP (
yaml 
apiVersion: policy/v1beta1 
kind: PodSecurityPolicy 
metadata: 
): 
Pod Security Policies (PSPs) enforce security standards for pod configurations. 
76
Pod Security Policies 
Creating a Pod Security Policy 
 
Diagram: Secret Management 
lua
+-------------------+ 
psp.yaml
name: restricted 
spec: 
privileged: false 
allowPrivilegeEscalation: false 
requiredDropCapabilities: 
- ALL 
volumes: 
- 'configMap' 
- 'emptyDir' 
- 'secret' 
hostNetwork: false 
hostIPC: false 
hostPID: false 
runAsUser: 
rule: 'MustRunAsNonRoot' 
seLinux: 
rule: 'MustRunAs' 
| | | +-----------+ |
| my-secret | | +-----
------+ +-------------
------+ 
Secret Store 
|
|
|
|
| 
|
v 
+-------------------+
| Kubernetes API 
|
|
+-------------------+ 
| 
Server 
|
v 
+-------------------+ 
| 
Pod 
|
|
|
| 
| 
| 
+-------------------+ 
| +-----------+ |
| Container | |
+-----------+ 
| | Env Vars | 
| +-----------+ 
DefineaPodSecurityPolicy: 
o 


---

## Page 78

2. 
Apply the PSP: 
kubectl apply -f psp.yaml 
 
: 
Create a role binding (
yaml 
apiVersion: rbac.authorization.k8s.io/v1 
kind: RoleBinding 
metadata: 
Apply the role binding: 
kubectl apply -f psp-role-binding.yaml 
): 
77
 
diff
+-------------------+ 
| Pod Security |
Policy (PSP) 
|
|
+-------------------+ 
|
v 
+-------------------+ 
| Kubernetes API
| Server 
|
|
+-------------------+ 
|
v 
+-------------------+ 
|
| 
Pod Admission | 
Controller 
|
+-------------------+ 
o 
o 
seLinuxOptions:
type: 'spc_t'
supplementalGroups:
rule: 'MustRunAs'
ranges:
-min: 1 
max: 65535 
fsGroup: 
rule: 'MustRunAs'
ranges:
-min: 1 
max: 65535 
psp-role-binding.yaml
name: psp:restricted 
namespace: <namespace> 
roleRef: 
kind: Role 
name: psp:restricted 
apiGroup: rbac.authorization.k8s.io 
subjects: 
- kind: ServiceAccount 
name: <service-account-name> 
namespace: <namespace> 
Bind thePSPtoaRole
o 
Diagram:PodSecurityPolicyEnforcement 


---

## Page 79

1. 
2. 
Apply the secret: 
kubectl apply -f db-secret.yaml 
 
: 
Create a secret for database credentials (
yaml 
apiVersion: v1 
kind: Secret 
metadata: 
): 
Consider deploying a secure web application using Kubernetes. The application requires: 
• 
• 
• 
Secure access to a database using secrets. 
Restricted network access. 
Enforcement of security policies at the pod level. 
78
o 
 
|
v 
+-------------------+
| 
Secured Pod
|
+-------------------+
kubectl create namespace secure-app 
db-secret. yaml
name: db-secret 
namespace: secure-app 
data: 
username: <base64-encoded-username> 
password: <base64-encoded-password> 
Step-by-Step Guide 
Real-World Example: Secure Deployment of a Web Application 
Set UpSecrets
o 
Create a Namespace: 


---

## Page 80

3. 
4. 
 
: 
Define and apply a PSP (
yaml 
apiVersion: policy/v1beta1 
kind: PodSecurityPolicy 
metadata: 
Apply the network policy: 
kubectl apply -f network-policy.yaml 
): 
 
: 
Create a network policy to restrict traffic (
yaml
apiVersion: networking.k8s.io/v1 
kind: NetworkPolicy 
metadata: 
): 
79
Define Network Policies
o 
Create a Pod Security Policy
o 
o 
name: db-policy 
namespace: secure-app 
spec: 
podSelector: 
matchLabels: 
app: database 
policyTypes: 
- Ingress 
- Egress 
ingress: 
- from: 
- podSelector: 
matchLabels: 
app: web 
egress: 
- to: 
- podSelector: 
matchLabels: 
app: web 
psp.yaml
name: restricted 
spec: 
privileged: false 
allowPrivilegeEscalation: false 
requiredDropCapabilities: 
- ALL 
volumes: 
- 'configMap' 
- 'emptyDir' 
- 'secret' 
hostNetwork: false 
hostIPC: false 
hostPID: false 
runAsUser: 
rule: 'MustRunAsNonRoot' 
seLinux: 
rule: 'MustRunAs' 
seLinuxOptions: 
type: 'spc_t' 
network-policy.yaml


---

## Page 81

5. 
Apply the PSP: 
kubectl apply -f psp.yaml 
Apply the deployment: 
kubectl apply -f web-deployment.yaml 
 
Define and deploy the web application (
yaml 
apiVersion: apps/v1 
kind: Deployment 
metadata: 
: 
): 
80
o 
o 
supplementalGroups:
rule: 'MustRunAs'
ranges:
-min: 1 
max: 65535 
fsGroup: 
rule: 'MustRunAs'
ranges:
-min: 1 
max: 65535 
web-deploy ment.yaml
name: web-app 
namespace: secure-app 
spec: 
replicas: 2 
selector: 
matchLabels: 
app: web 
template: 
metadata: 
labels: 
app: web 
spec: 
containers: 
- name: web 
image: my-web-app:latest 
ports: 
- containerPort: 80 
env: 
- name: DB_USERNAME 
valueFrom: 
secretKeyRef: 
name: db-secret 
key: username 
- name: DB_PASSWORD 
valueFrom: 
secretKeyRef: 
name: db-secret 
key: password 
securityContext: 
runAsUser: 1000 
runAsGroup: 3000 
fsGroup: 2000 
Deploy the Application
o 


---

## Page 82

81
Securing Kubernetes clusters involves multiple layers of security, including authentication
and authorization, network policies, secrets management, and pod security policies. By
following best practices and implementing these security measures, you can protect your
applications and data from potential threats. This chapter has provided detailed steps,
commands, examples, diagrams, and real-world scenarios to help you secure your Kubernetes
environment effectively. 
Summary 
Diagram: Secure Deployment Workflow 
sql
+-------------------+ 
|
|
| 
Kubernetes
Namespace
secure-app 
|
|
|
+-------------------+ 
|
v 
+-------------------+ 
+-------------------+ 
|
| 
Pod Security
Policy (PSP) 
|
|
+-------------------+ 
|
| 
Network Policy
db-policy 
|
|
+-------------------+ 
|
v 
|
v 
+-------------------+ 
+-------------------+ 
|
| 
Pod Admission
Controller 
|
|
+-------------------+ 
|
| 
Restricted
Network Access 
|
|
+-------------------+ 
|
v 
|
v 
+-------------------+ 
+-------------------+
|
+-------------------+ 
| 
Secure Pods 
|<-------->| 
Database Pods 
+-------------------+ 
|
v 
+-------------------+ 
|
| 
Web Application
with Secrets 
|
|
+-------------------+ 


---

## Page 83

1.
2.
3.
4.
1.
2.
3.
4.
1. 
2. 
3. 
and modifications. 
 OperationalInsight
cluster. 
: Quantitative data about the system performance and resource usage. 
: Records of events that happen in the system. 
: Notifications about anomalies or critical events. 
: Graphical representation of data for easier analysis. 
: Identifies issues before they become critical. 
: Helps in tuning the system for better performance. 
: Ensures compliance with security policies by tracking access 
: Provides insights into the operation and utilization of the 
82
Effective monitoring and logging are crucial for maintaining the health, performance, and
reliability of Kubernetes clusters. This chapter will cover the essential tools and techniques
for monitoring and logging in Kubernetes, including Prometheus, Grafana, and Elasticsearch,
Fluentd, Kibana (EFK) stack. Detailed steps, commands, setup guides, examples, diagrams,
and real-world scenarios will be provided to help you implement robust monitoring and
logging solutions. 
 Metrics
 Logs
 Alerting
 Visualization
Verify Installation: 
kubectl get pods -n monitoring 
Create a Namespace: 
kubectl create namespace monitoring 
 Proactive Issue Detection
 Performance Optimization
 Security Compliance
Install Prometheus using Helm: 
helm repo add prometheus-community https://prometheus-
community.github.io/helm-charts
helm repo update
helm install prometheus prometheus-community/prometheus --namespace
monitoring 
Chapter 17: Monitoring and Logging in Kubernetes 
 
Overview 
Key Concepts 
Importance of Monitoring and Logging 
Monitoring with Prometheus and Grafana
Setting Up Prometheus 


---

## Page 84

1. 
2. 
3. 
1. 
2. 
 
: 
Get the Grafana admin password: 
kubectl get secret --namespace monitoring grafana -o
jsonpath="{.data.admin-password}" | base64 --decode ; echo 
Port forward to access Grafana UI: 
kubectl port-forward --namespace monitoring svc/grafana 3000:80 
 
: 
Login to Grafana (default user: admin, password obtained above). 
Navigate to 
> 
> Add data source. 
Select Prometheus and set the URL to http://prometheus-
server.monitoring.svc.cluster.local. 
83
Setting Up Grafana 
Logging with EFK Stack
Setting Up Elasticsearch 
Diagram: Prometheus and Grafana Architecture 
lua
+-------------------+ 
Access Grafana
o 
Create a Namespace: 
kubectl create namespace logging 
Install Grafana using Helm: 
helm install grafana grafana/grafana --namespace monitoring 
Install Elasticsearch using Helm: 
helm repo add elastic https://helm.elastic.co
helm install elasticsearch elastic/elasticsearch --namespace logging 
Add PrometheusasaDataSourceinGrafana
Configuration DataSources
o 
o
o
o 
+-------------------+
|
| 
Kubernetes
Cluster 
|
|
+-------------------+
| +-------------+ | 
| | +----------------
---+
Grafana
|
(Visualization)|
| +-------------+
|
|
+-------------------+
| | Prometheus |<----------->| | 
Dashboards
|
|
| | (Metrics) 
| |
+-------------------+ 
| +-------------+
 
|
v 
+-------------------+ 
| 
Alertmanager 
|
+-------------------+ 


---

## Page 85

1. 
2. 
1. 
2. 
 
: 
Port forward to access Kibana UI: 
kubectl port-forward --namespace logging svc/kibana 5601:5601 
 
 
: 
Edit Fluentd configuration to include Elasticsearch output: 
yaml
<match **> 
84
Setting Up Kibana 
Setting Up Fluentd 
Diagram: EFK Stack Architecture 
lua
+-------------------+
-------+ 
Access Kibana
o 
Install Kibana using Helm: 
helm install kibana elastic/kibana --namespace logging 
Install Fluentd using Helm: 
helm repo add fluent https://fluent.github.io/helm-charts
helm install fluentd fluent/fluentd --namespace logging
Configure Fluentd to send logs to Elasticsearch
o 
@type elasticsearch
host elasticsearch.logging.svc.cluster.local
port 9200
logstash_format true 
</match> 
+-------------------+ 
+------------
|
|
| 
Kubernetes
Cluster 
|
| 
| | +-----------------
--+ 
Elasticsearch
(Storage) 
|
| 
| | +--------
---- | +-----
----
Kibana
(Visualization) |
+-------------------+
-------+
| +-------------+ |
----+ |
| | Fluentd 
| 
| 
|<----------->| +-------------+ |<----------->| 
Dashboards | | 
| | (Logs) 
----+ |
+-------------------+
-------+ 
| | 
| | Indices 
+-------------------+ 
| | 
| +---------
+------------


---

## Page 86

1. 
2. 
3. 
 
: 
Create an alerting rule (
yaml
groups:
Apply the configuration: 
kubectl apply -f alertmanager-config.yaml 
 
: 
Create a configuration file (
yaml 
global: 
): 
 
: 
Update Prometheus configuration to include Alertmanager: 
yaml
alerting: 
): 
85
Setting Up Alerts
Prometheus Alertmanager 
Define Alerting Rules
o 
Configure Alertmanager
o 
Integrate Alertmanager with Prometheus
o 
o 
alertmanagers: 
- static_configs: 
- targets: 
- alertmanager.monitoring.svc:9093 
alertmanager-config.yaml
resolve_timeout: 5m 
route: 
receiver: 'team-X-mails' 
receivers: 
- name: 'team-X-mails' 
email_configs: 
- to: 'team@example.com' 
from: 'alertmanager@example.com' 
smarthost: 'smtp.example.com:587' 
auth_username: 'alertmanager' 
auth_password: 'password' 
alert-rules.yaml
- name:example 
rules:
-alert:
HighCPUUsage 
expr:instance:node_cpu_utilisation:rate1m > 0.9 
for: 5m
labels:
severity: critical 
annotations: 
summary: "Instance {{ $labels.instance }} CPU usageis
description: "CPU usage is above 90% for more than5
high"
minutes."


---

## Page 87

1. 
2. 
3. 
4. 
Apply the alerting rule: 
kubectl apply -f alert-rules.yaml 
An e-commerce application running on a Kubernetes cluster requires comprehensive
monitoring and logging to ensure high availability and performance. The application stack
includes multiple microservices, a database, and a web frontend. 
 
: 
Install Prometheus and Grafana in the ecommerce namespace following the
steps outlined in the earlier sections. 
: 
Install Elasticsearch, Fluentd, and Kibana in the ecommerce namespace
following the steps outlined in the earlier sections. 
: 
Example deployment for the web frontend (
yaml 
apiVersion: apps/v1 
kind: Deployment 
metadata: 
): 
86
o 
kubectl create namespace ecommerce 
web-dep loyment.yaml
name: web-frontend 
namespace: ecommerce 
spec: 
replicas: 3 
selector: 
matchLabels: 
app: web 
template: 
metadata: 
labels: 
app: web 
spec: 
containers: 
- name: web 
image: my-web-frontend:latest 
ports: 
- containerPort: 80 
- name: fluentd 
image: fluent/fluentd:v1.11 
env: 
- name: FLUENT_ELASTICSEARCH_HOST 
value: "elasticsearch.logging.svc" 
- name: FLUENT_ELASTICSEARCH_PORT 
value: "9200" 
Step-by-Step Guide 
Real-World Example: Monitoring and Logging Setup for an E-commerce Application
Scenario 
Create a Namespace: 
Set UpPrometheusandGrafana
o 
Configure Logging with EFK Stack
o 
Deploy Application with Sidecar Containers for Logging
o 


---

## Page 88

5. 
Apply the deployment: 
kubectl apply -f web-deployment.yaml 
 
: 
Configure Prometheus Alertmanager and define alerting rules for critical
metrics. 
In this chapter, we've covered the essential tools and techniques for monitoring and logging
in Kubernetes. By leveraging Prometheus, Grafana, and the EFK stack, you can gain deep
insights into your Kubernetes cluster's performance, health, and operations. This
comprehensive guide, complete with commands, setup guides, examples, diagrams, and real-
world scenarios, will help you implement robust monitoring and logging solutions, ensuring
your applications run smoothly and efficiently. 
87
o 
 
lua
+-------------------+ 
| Kubernetes
| Namespace:
| ecommerce 
|
|
|
+-------------------+
| +---------------+ | 
+-------------------+
|
(Visualization)|
+-------------------+
+-------------------+
|
|
+-------------------+
+-------------------+
| | Prometheus
| | (Metrics) 
|<---------->| 
Grafana
| |
| +---------------+ | 
| 
| 
|
| +---------------+ | 
| | Fluentd
| | (Logs) 
|<---------->| Elasticsearch
| |
| +---------------+ | 
| 
(Storage)
| 
|
| +---------------+ | 
|
|<---------->| 
Kibana
(Visualization)| +---
----------------+
|
| | Application
| | Containers 
| |
| +---------------+ |
+-------------------+ 
Set UpAlerting
o
Summary 
Diagram:MonitoringandLoggingSetupforE-commerceApplication 


---

## Page 89

1. 
2. 
3. 
4. 
5. 
6. 
7. 
As we wrap up this comprehensive guide on Docker and Kubernetes for DevOps, it's
essential to summarize the key takeaways, reinforce the concepts learned, and provide
guidance on the next steps you can take to continue your journey in containerization and
orchestration. 
 
: 
Containers offer a lightweight, consistent, and efficient way to run
applications across different environments.
Docker is a popular containerization platform that simplifies the process of
building, shipping, and running containers. 
: 
Kubernetes automates the deployment, scaling, and management of
containerized applications.
Core components of Kubernetes include nodes, pods, deployments, services,
and the control plane. 
: 
Kubernetes networking enables communication between containers within a
pod, between pods, and with the outside world.
Tools like CNI plugins, Ingress controllers, and Service Meshes enhance
Kubernetes networking capabilities. 
: 
Persistent storage in Kubernetes is managed using Persistent Volumes (PVs)
and Persistent Volume Claims (PVCs).
Stateful applications can leverage various storage solutions like NFS, Ceph,
and cloud storage options. 
: 
Security in Kubernetes involves multiple layers including authentication,
authorization, network policies, and secrets management.
Tools like Pod Security Policies (PSPs) and network policies ensure a secure
Kubernetes environment. 
: 
Monitoring and logging are crucial for maintaining the health and
performance of Kubernetes clusters.
Prometheus, Grafana, and the EFK stack (Elasticsearch, Fluentd, Kibana) are
popular tools for monitoring and logging. 
: 
Continuous Integration and Continuous Deployment (CI/CD) pipelines
automate the process of testing and deploying applications.
Tools like Jenkins, Argo CD, and GitLab CI integrate seamlessly with
Kubernetes to streamline CI/CD workflows. 
88
Storage in Kubernetes
o
Security in Kubernetes
o
CI/CD with Kubernetes
o
Monitoring and Logging
o
Networking in Kubernetes
o
UnderstandingContainers
o
Container Orchestration with Kubernetes
o
Chapter 18: Conclusion and Next Steps 
 
Overview 
Key Takeaways 
o
o
o
o
o
o
o


---

## Page 90

1. 
2. 
3. 
4. 
5. 
A fictional e-commerce company, ShopEase, wants to modernize its infrastructure by
migrating to a containerized environment using Docker and Kubernetes. The platform
consists of multiple microservices, a frontend web application, and a database. 
Let's revisit a practical example of an e-commerce platform to illustrate how Docker and
Kubernetes are used in a real-world scenario. 
 
: 
Each microservice is containerized using Docker.
Dockerfiles are created for building container images, and images are pushed
to a private Docker registry. 
: 
A Kubernetes cluster is set up on a cloud provider (e.g., AWS, GCP, or
Azure).
Cluster setup includes nodes, control plane components, and networking
configurations. 
: 
Microservices are deployed using Kubernetes Deployments.
Services are created to expose microservices, enabling internal and external
communication. 
Implementing CI/CD Pipeline: 
A CI/CD pipeline is set up using Jenkins.
Jenkins is configured to build, test, and deploy Docker images to the
Kubernetes cluster.
: 
Prometheus and Grafana are deployed for monitoring.
The EFK stack is set up for logging, allowing real-time log analysis and
troubleshooting. 
89
Solution 
Scenario 
Real-World Use Case: E-commerce Platform 
Monitoring and Logging
Deploying the Application
Containerizing the Application
Setting Up Kubernetes Cluster
o
o
o 
o
o
o 
o
o 
o
o 


---

## Page 91

1. 
90
Commands and Setup Guides
Deploying ShopEase Microservices 
Diagram: ShopEase E-commerce Platform on Kubernetes 
lua
+----------------------------------------- +
| | | +----------
-+ | |Frontend | 
KubernetesCluster 
|
|
|
|
|
|
|
|
|
|
|
|
|
|
|
|
|
|
|
|
|
|
|
|
|
+----------------------------------------- +
+-----------+
| 
Backend 
|
|Service 
1|
+-----------+ 
| |Service 
|
| +-----------+ 
|
|
|
v
|
 
+
-
-
-
-
-
-
-
-
-
-
-
+
 
|
v
+-----------+
| Backend | |
+-----------+
+-----------+
| Monitor | |
+-----------+ 
| | 
Web 
|
|
| +-----------+
|
| +-----------+
| | Database|
| | Service |
| +-----------+ 
| | Pod 
Pod 
| 
Pods 
| 
|
|
|
v
|
 
+
-
-
-
-
-
-
-
-
-
-
-
+
 
|
v
+-----------+
|Prometheus|
+-----------+ 
| | DBPod | +----
-------+ | | |
| 
|Grafana 
|
+-----------+ 
dockerfile
#Use an official Python runtime as a parent image 
FROM python:3.8-slim 
#Set the working directory in the container 
WORKDIR /app 
#Copy the current directory contents into the container at /app 
COPY . /app 
Dockerfile Example for Backend Service: 


---

## Page 92

2. 
3. 
4. 
91
yaml 
groovy 
yaml
apiVersion: v1
kind: Service
metadata:
name: backend-service
namespace: shopease
spec:
selector:
app: backend
ports:
- protocol: TCP
port: 80
targetPort: 80
apiVersion: apps/v1
kind: Deployment
metadata: 
name: backend-service
namespace: shopease 
spec: 
replicas: 3
selector: 
matchLabels: 
app: backend 
template: 
metadata:
labels: 
app: backend 
spec: 
containers:
- name: backend 
image: shopease/backend:latest
ports:
- containerPort: 80 
# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt 
# Make port 80 available to the world outside this container 
EXPOSE 80 
# Define environment variable 
ENV NAME World 
# Run app.py when the container launches 
CMD ["python", "app.py"] 
CI/CD Pipeline Example (Jenkinsfile): 
Service Example for Exposing Backend Service: 
Kubernetes Deployment Example for Backend Service: 


---

## Page 93

1. 
2. 
3. 
4. 
 
: 
Explore advanced Kubernetes topics such as Operators, Custom Resource
Definitions (CRDs), and Helm charts.
Learn about service mesh technologies like Istio and Linkerd for managing
microservices. 
: 
Consider obtaining certifications like Certified Kubernetes Administrator
(CKA) and Certified Kubernetes Application Developer (CKAD) to validate
your skills. 
: 
Participate in Kubernetes forums, attend meetups, and contribute to open-
source projects to stay updated with the latest trends and best practices. 
: 
Experiment with other container orchestration tools like OpenShift and
Docker Swarm.
Explore different CI/CD tools and monitoring solutions to find what works
best for your environment. 
92
o
o
pipeline {
agent any
stages {
stage('Build') {
steps {
sh'dockerbuild -t shopease/backend .' 
}
}
stage('Test') {
steps {
sh'dockerrun --rm shopease/backend pytest' 
}
}
stage('Push') {
steps {
withCredentials([string(credentialsId: 'docker-hub-
password',variable:'DOCKER_HUB_PASSWORD')]) { 
sh'docker login -u shopease -p 
$DOCKER_HUB_PASSWORD'
sh'docker push shopease/backend:latest' 
}
}
}
stage('Deploy') {
steps {
kubernetesDeploy(configs: 'k8s/backend-
deployment.yaml',kubeconfigId: 'kubeconfig') 
}
}
}
 
} 
Next Steps 
Get Certified
o
Join theCommunity
o
Deepen Your Knowledge
o
Experiment with New Tools
o


---

## Page 94

In this final chapter, we've summarized the key concepts covered throughout the book and
provided a real-world use case to illustrate the practical application of Docker and
Kubernetes. We've also outlined the next steps to further your knowledge and career in
containerization and orchestration. By continuously learning and experimenting, you'll be
well-equipped to handle the challenges and opportunities in the dynamic world of DevOps. 
This concludes our comprehensive guide on Docker and Kubernetes for DevOps. Thank you
for joining us on this journey, and we wish you the best in your future endeavors in the
exciting field of containerization and orchestration. 
93
Summary 


---

## Page 95

Elasticsearch Official Documentation
Fluentd Official Documentation
Kibana Official Documentation 
: 
Helm Official Documentation 
Prometheus Helm Chart 
Grafana Helm Chart 
: 
Jenkins Official Documentation 
Jenkins Kubernetes Plugin 
: 
Kubernetes Security Documentation 
Kubernetes Network Policies 
: 
CNI Plugin Documentation 
Kubernetes Ingress Documentation 
Below is the list of all references and links used in this eBook: 
: 
Docker Official Documentation 
Dockerfile Reference 
: 
Kubernetes Official Documentation 
Kubernetes API Reference 
: 
Prometheus Official Documentation 
Grafana Official Documentation 
: 
94
Reference Page 
• HelmCharts
• JenkinsandCI/CD
• SecurityinKubernetes
• DockerDocumentation
• KubernetesNetworking
• PrometheusandGrafana
• KubernetesDocumentation
• Elasticsearch,Fluentd,andKibana(EFK)Stack
•
• 
•
• 
•
• 
•
•
• 
•
•
• 
•
• 
•
• 
•
• 


---

