# Kubernetes — Cheatsheet

## Aliases (add to ~/.zshrc or ~/.bashrc)

```bash
alias k='kubectl'
alias kgp='kubectl get pods'
alias kgpa='kubectl get pods -A'
alias kgs='kubectl get svc'
alias kgn='kubectl get nodes'
alias kd='kubectl describe'
alias kdp='kubectl describe pod'
alias kl='kubectl logs'
alias kex='kubectl exec -it'
alias kaf='kubectl apply -f'
alias kdf='kubectl delete -f'
alias kctx='kubectl config use-context'
alias kns='kubectl config set-context --current --namespace'
alias kgpw='kubectl get pods -w'  # watch
alias kgpwide='kubectl get pods -o wide'
```

---

## Context and Namespace Management

```bash
# List all contexts
kubectl config get-contexts

# Switch context
kubectl config use-context <context-name>
kubectl config use-context arn:aws:eks:us-east-1:123456789:cluster/prod

# Set current namespace
kubectl config set-context --current --namespace=production

# View current context
kubectl config current-context

# View full kubeconfig
kubectl config view --minify

# Rename a context
kubectl config rename-context old-name new-name

# Delete a context
kubectl config delete-context old-name

# kubectx / kubens (krew plugin) — faster switching
kubectx prod-cluster
kubens production
```

---

## Getting Resources

```bash
# Get resources — basic
kubectl get pods
kubectl get pods -A                          # all namespaces
kubectl get pods -n production
kubectl get pods -o wide                     # show node and IP
kubectl get pods --show-labels
kubectl get pods -l app=frontend             # label selector
kubectl get pods -l 'app in (frontend,api)'
kubectl get pods --field-selector=status.phase=Running

# Get all resource types at once
kubectl get all -n production

# Get with custom columns
kubectl get pods -o custom-columns=\
  NAME:.metadata.name,\
  STATUS:.status.phase,\
  NODE:.spec.nodeName,\
  IP:.status.podIP

# Watch for changes
kubectl get pods -w
kubectl get events -w -n production

# Sort by field
kubectl get pods --sort-by=.metadata.creationTimestamp
kubectl get events --sort-by=.lastTimestamp
kubectl top pods --sort-by=memory

# Get raw JSON
kubectl get pod my-pod -o json
kubectl get pod my-pod -o yaml

# Get specific field
kubectl get pod my-pod -o jsonpath='{.status.podIP}'
kubectl get pod my-pod -o jsonpath='{.spec.containers[0].image}'
kubectl get pod my-pod -o jsonpath='{.status.containerStatuses[0].restartCount}'
```

---

## JSONPath Queries

```bash
# List all pod names
kubectl get pods -o jsonpath='{.items[*].metadata.name}'

# Pod + node pairs
kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.nodeName}{"\n"}{end}'

# Images in a deployment
kubectl get deploy my-app -o jsonpath='{.spec.template.spec.containers[*].image}'

# All pods with their QoS class
kubectl get pods -A -o jsonpath='{range .items[*]}{.metadata.namespace}/{.metadata.name}{"\t"}{.status.qosClass}{"\n"}{end}'

# All pods without resource requests (grep empty objects)
kubectl get pods -A -o jsonpath='{range .items[*]}{.metadata.namespace}/{.metadata.name}{"\t"}{.spec.containers[*].resources.requests}{"\n"}{end}' | grep -v cpu

# Nodes with their allocatable CPU/memory
kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.allocatable.cpu}{"\t"}{.status.allocatable.memory}{"\n"}{end}'

# Services with external IPs
kubectl get svc -A -o jsonpath='{range .items[*]}{.metadata.namespace}/{.metadata.name}{"\t"}{.status.loadBalancer.ingress[0].ip}{"\n"}{end}' | grep -v "^$"

# Secrets older than a certain name (sorted by creation)
kubectl get secrets -A --sort-by=.metadata.creationTimestamp -o jsonpath='{range .items[*]}{.metadata.namespace}/{.metadata.name}{"\t"}{.metadata.creationTimestamp}{"\n"}{end}'
```

---

## Describe

```bash
kubectl describe pod <pod>
kubectl describe pod <pod> -n production
kubectl describe node <node>
kubectl describe deployment <deploy>
kubectl describe svc <svc>
kubectl describe pvc <pvc>
kubectl describe hpa <hpa>
kubectl describe ingress <ingress>

# Focus on events from describe
kubectl describe pod <pod> | grep -A 20 Events
kubectl describe node <node> | grep -A 10 Conditions
kubectl describe node <node> | grep -A 10 "Allocated resources"
```

---

## Logs

```bash
# Basic logs
kubectl logs <pod>
kubectl logs <pod> -n production
kubectl logs <pod> -c <container>     # multi-container pod

# Previous container instance (after crash)
kubectl logs <pod> --previous
kubectl logs <pod> -c <container> --previous

# Stream (follow)
kubectl logs -f <pod>
kubectl logs -f <pod> --tail=100

# Logs from all pods matching a label (requires stern or manual loop)
kubectl logs -l app=frontend --all-containers=true

# Stern (krew plugin) — multi-pod tail with colors
stern -n production app=frontend
stern --since 5m -n production ".*"    # all pods last 5 min

# Timestamps
kubectl logs <pod> --timestamps=true
```

---

## Exec and Debug

```bash
# Shell into a running container
kubectl exec -it <pod> -- /bin/sh
kubectl exec -it <pod> -c <container> -- bash

# Run a one-off command
kubectl exec <pod> -- env
kubectl exec <pod> -- cat /etc/resolv.conf
kubectl exec <pod> -- curl -s http://backend-svc:8080/health

# Ephemeral debug container (K8s 1.23+)
kubectl debug -it <pod> --image=busybox:latest --target=<container>
kubectl debug -it <pod> --image=nicolaka/netshoot --share-processes

# Debug a node (root shell on node)
kubectl debug node/<node-name> -it --image=busybox

# Run a temporary debug pod
kubectl run -it --rm debug --image=busybox --restart=Never -- sh
kubectl run -it --rm debug --image=nicolaka/netshoot --restart=Never -- sh

# Copy files into/out of a pod
kubectl cp <pod>:/path/to/file ./local-file
kubectl cp ./local-file <pod>:/path/to/dest
```

---

## Apply, Create, Delete

```bash
# Declarative (preferred)
kubectl apply -f manifest.yaml
kubectl apply -f ./manifests/          # directory
kubectl apply -k ./kustomization/      # kustomize
kubectl apply -f https://raw.githubusercontent.com/...

# Server-side apply (recommended for GitOps — avoids field ownership conflicts)
kubectl apply --server-side -f manifest.yaml
kubectl apply --server-side --force-conflicts -f manifest.yaml

# Diff before apply
kubectl diff -f manifest.yaml

# Dry run (client-side)
kubectl apply -f manifest.yaml --dry-run=client
# Dry run (server-side — validates against admission controllers)
kubectl apply -f manifest.yaml --dry-run=server

# Delete
kubectl delete -f manifest.yaml
kubectl delete pod <pod>
kubectl delete pod <pod> --grace-period=0 --force    # Emergency only
kubectl delete pods -l app=old-version
kubectl delete pod --all -n staging

# Create resources imperatively
kubectl create deployment nginx --image=nginx:1.25 --replicas=3
kubectl create service clusterip nginx --tcp=80:80
kubectl create configmap app-config --from-literal=ENV=prod --from-file=config.properties
kubectl create secret generic db-creds --from-literal=password=hunter2
kubectl create secret docker-registry registry-cred \
  --docker-server=myregistry.io \
  --docker-username=admin \
  --docker-password=secret
kubectl create namespace production
kubectl create serviceaccount ci-bot
kubectl create job myjob --image=busybox -- /bin/sh -c "echo hello"
kubectl create cronjob mycron --image=busybox --schedule="*/5 * * * *" -- date
```

---

## Rollout and Scaling

```bash
# Deployment rollout
kubectl rollout status deployment/<name>
kubectl rollout history deployment/<name>
kubectl rollout history deployment/<name> --revision=3
kubectl rollout undo deployment/<name>
kubectl rollout undo deployment/<name> --to-revision=2
kubectl rollout pause deployment/<name>
kubectl rollout resume deployment/<name>
kubectl rollout restart deployment/<name>  # Triggers rolling restart

# Scale
kubectl scale deployment <name> --replicas=5
kubectl scale statefulset <name> --replicas=3

# Autoscale (imperative HPA)
kubectl autoscale deployment <name> --min=2 --max=10 --cpu-percent=60

# Update image
kubectl set image deployment/<name> <container>=<image>:<tag>
kubectl set image deployment/frontend web=nginx:1.26 --record  # --record deprecated

# Resource update
kubectl set resources deployment/<name> --limits=cpu=500m,memory=512Mi --requests=cpu=250m,memory=256Mi
```

---

## Labels, Annotations, and Patches

```bash
# Label
kubectl label pod <pod> env=production
kubectl label node <node> disktype=ssd
kubectl label namespace staging env=staging

# Remove label
kubectl label pod <pod> env-

# Annotate
kubectl annotate pod <pod> description="debugging run"
kubectl annotate deployment <name> kubernetes.io/change-cause="v2 release"

# Patch (JSON merge patch)
kubectl patch deployment <name> -p '{"spec":{"replicas":5}}'

# Patch (strategic merge patch)
kubectl patch deployment <name> --patch '
spec:
  template:
    spec:
      containers:
      - name: app
        resources:
          limits:
            memory: 1Gi
'

# Patch (JSON patch — precise)
kubectl patch pod <pod> --type=json -p='[{"op":"replace","path":"/spec/containers/0/image","value":"nginx:1.26"}]'
```

---

## Port-forward and Proxy

```bash
# Port-forward to a pod
kubectl port-forward pod/<pod> 8080:80
kubectl port-forward pod/<pod> 8080:80 -n production

# Port-forward to a service
kubectl port-forward svc/<svc> 8080:80

# Port-forward to a deployment (picks a healthy pod)
kubectl port-forward deploy/<name> 8080:80

# Listen on all interfaces (expose to LAN)
kubectl port-forward svc/<svc> 8080:80 --address=0.0.0.0

# kubectl proxy — exposes API server locally
kubectl proxy --port=8001
# Then: curl http://localhost:8001/api/v1/namespaces/production/pods
```

---

## Top / Resource Usage

```bash
# Node resource usage
kubectl top nodes
kubectl top nodes --sort-by=cpu

# Pod resource usage
kubectl top pods -n production
kubectl top pods -A
kubectl top pods -A --sort-by=memory
kubectl top pods <pod> --containers    # per-container breakdown

# Check resource requests/limits
kubectl describe node <node> | grep -A 10 "Allocated resources"
kubectl get pods -A -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{range .spec.containers[*]}{.resources}{"\n"}{end}{end}'
```

---

## Events

```bash
# Events in a namespace (sorted by time)
kubectl get events -n production --sort-by=.lastTimestamp

# Events for a specific object
kubectl get events --field-selector involvedObject.name=<pod-name>
kubectl get events --field-selector involvedObject.kind=Node

# Warning events only
kubectl get events -A --field-selector type=Warning

# Watch events in real time
kubectl get events -n production -w
```

---

## Node Operations

```bash
# Cordon (prevent new pods from scheduling)
kubectl cordon <node>
kubectl uncordon <node>

# Drain (evict all pods, then cordon)
kubectl drain <node> --ignore-daemonsets --delete-emptydir-data
kubectl drain <node> --ignore-daemonsets --delete-emptydir-data --grace-period=60
kubectl drain <node> --ignore-daemonsets --delete-emptydir-data --force  # Evicts pods with no controller

# Show node labels
kubectl get nodes --show-labels
kubectl get nodes -L disktype,zone,instanceType

# Get node conditions
kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{range .status.conditions[*]}{.type}={.status}{" "}{end}{"\n"}{end}'
```

---

## Explain (API Reference)

```bash
kubectl explain pod
kubectl explain pod.spec
kubectl explain pod.spec.containers
kubectl explain pod.spec.containers.livenessProbe
kubectl explain deployment.spec.strategy
kubectl explain hpa.spec.metrics
```

---

## Imperative Resource Creation Flags

```bash
# pod
kubectl run nginx --image=nginx:1.25 --port=80 --env="ENV=prod" --labels="app=nginx"

# Expose a pod as a service
kubectl expose pod nginx --port=80 --target-port=80 --type=ClusterIP

# Expose a deployment
kubectl expose deployment frontend --port=80 --target-port=8080 --type=LoadBalancer

# Generate YAML without creating (useful for scaffolding)
kubectl run nginx --image=nginx --dry-run=client -o yaml > pod.yaml
kubectl create deployment nginx --image=nginx --dry-run=client -o yaml > deploy.yaml
kubectl expose deployment nginx --port=80 --dry-run=client -o yaml > svc.yaml

# ConfigMap flags
kubectl create configmap myconfig \
  --from-literal=key1=value1 \
  --from-literal=key2=value2 \
  --from-file=config.ini \
  --from-env-file=.env

# Secret flags
kubectl create secret generic mysecret \
  --from-literal=username=admin \
  --from-literal=password='S3cr3t!' \
  --from-file=tls.crt \
  --from-file=tls.key
```

---

## Useful kubectl Plugins (krew)

```bash
# Install krew
(
  set -x; cd "$(mktemp -d)" &&
  OS="$(uname | tr '[:upper:]' '[:lower:]')" &&
  ARCH="$(uname -m | sed -e 's/x86_64/amd64/' -e 's/arm.*$/arm/' -e 's/aarch64$/arm64/')" &&
  curl -fsSLO "https://github.com/kubernetes-sigs/krew/releases/latest/download/krew-${OS}_${ARCH}.tar.gz" &&
  tar zxvf "./krew-${OS}_${ARCH}.tar.gz" &&
  KREW=./krew-${OS}_${ARCH} && "$KREW" install krew
)

# Essential plugins
kubectl krew install ctx          # kubectx — context switching
kubectl krew install ns           # kubens — namespace switching
kubectl krew install stern        # multi-pod log tailing
kubectl krew install neat         # clean YAML output (removes managed fields)
kubectl krew install tree         # show owner references tree
kubectl krew install resource-capacity  # node capacity overview
kubectl krew install who-can      # check RBAC permissions for a verb+resource
kubectl krew install outdated     # find pods with outdated images
kubectl krew install images       # list all images in cluster

# k9s — terminal UI (install separately)
brew install k9s   # or: https://k9scli.io/

# Usage examples
kubectl neat get pod <pod> -o yaml    # strip clutter
kubectl tree deployment <name>        # see ReplicaSet → Pod ownership
kubectl who-can get secrets -n production
kubectl resource-capacity --sort cpu.limit
```

---

## Cluster Health Quick Checks

```bash
# Control plane health
kubectl get componentstatuses  # Deprecated but still works on some distributions
kubectl get nodes
kubectl get pods -n kube-system

# Check API server
kubectl cluster-info

# Check etcd (self-managed clusters)
ETCDCTL_API=3 etcdctl \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  endpoint status --write-out=table

# Pods not Running
kubectl get pods -A | grep -v Running | grep -v Completed

# Recent warning events
kubectl get events -A --field-selector type=Warning --sort-by=.lastTimestamp | tail -30

# Resource usage overview
kubectl top nodes
kubectl top pods -A --sort-by=memory | head -20

# PVCs not bound
kubectl get pvc -A | grep -v Bound
```
# Content from k8_interview_cheat_sheet.pdf

## Page 1

K8s Interview Questions and Answers 
 
1. Can you please explain the architecture of Kubernetes. 
Ans: According to the Architecture of kubernetes, there are some components that 
exist on master and worker node as well. Such as Kube Controller Manager, Kube 
API Server, Kube-Scheduler and ETCD on master node. And there are three 
components on worker node which is Container Engine, such as Docker, Kubelet 
and Kube Proxy.  
So If we want to give a brief about each of the component. The first one Kube 
Controller. It make sure that if your pod has some problem it has been failed due to 
some reason or if your node goes down. So to control those kind of things kube 
controller will be used. 
1. KubeAPI Server – that exposes the Kubernetes API. So this is the API server 
where your worker nodes will be communicating with. So whenever you run. 
Kubectl get nodes 
Kubectl get pods 
 
All of those commands first reach the KubeAPI server. So this is like a gateway or 
the entrypoint for the entire kubernetes cluster. 
  
2. ETCD – It is a key value pair which is used to store cluster related information. 
Such as What nodes exist in the cluster, what pods should be running, which 
nodes they are running on. 
 
So whenever you create something with kubectl create / kubectl run will create 
an entry in the ETCD. 
 
3. Kube Scheduler – That watches newly created pods that have no node assigned, 
and it selects nodes for them to run. 
  
 
 
 


---

## Page 2

ON Worker Node 
1. Kubelet – It is like an agent that runs on each node in the cluster. It makes sure 
that containers are running in a pod. 
2. Kube Proxy – It is basically to have communication like, for example if you have 
multiple machines and you will have some networking solutions installed right 
such as Calico or Flannel. So to have proper communications between pods 
kube-proxy is responsible. 
3. Container Engine – Which is responsible for running containers.  
Such as Docker. 
What is Ingress? 
Ans:  
Ingress is a resource of kubernetes, it allows us to access the multiple services from 
over the internet using single load balancer. 
 
Let's say if you deployed 10 services and you are going to exposed 10 services as 
LoadBalancer so what will happen it will create 10 load balancer in cloud environment 
so it would be very costly, but if you have deployed ingress controller on kubernetes, 
so you can create ingress resource and access multiple services using single load 
balancer. 
Ingress can provide features like Load Balancing, SSL Termination, Namebased 
virtual hosting,   
 
1. Name based virtual hosting – it is used to access multiple services or websites 
at the same IP Address. 


---

## Page 3

 
You must have an ingress controller to satisfy an Ingress. Only creating an Ingress 
resource has no effect. 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 


---

## Page 4

The following Ingress tells the backing load balancer to route requests based on the 
Host header. 
 
For example: If you specify the website01.example.com, so the request should 
forwarded to service1. 
And if you specify the website02.example.com then request should be forwarded to 
service2. 
2. SSL Termination – you can secure your ingress controller by implementing SSL 
termination from HTTP to HTTPs. If you want to implement it on ingress 
resource then you need to first create the secret with TLS keys. And that secret 
you will specify in ingress resource, where you will write the parameters like tls, 
hosts, host header name for example : https://website01.example.com 
And secret name that you have created using TLS certificate.     
 


---

## Page 5

 
 
3. Explain kubeconfig file of Kubernetes? 
Ans: In the kubeconfig file there are three primary fields. 
1. Cluster field – In the Cluster Field has details related to the URL of your 
Kubernetes Cluster and it’s associated information. In the first section of the 
cluster has information of your kubernetes master and name of the cluster. There 
can be two fields also. Certificate-authority-data, OR insecure-skip-tls-
verify:true which means the TLS certificate for this cluster will not be verify. 
  
2. Context Field – Context basically groups all the information together  
3. Users Field – User field contains authentication specific information like 
username, passwords. 
There can be different type of authentication mechanism such as username, 
password, certificates and tokens. 
So in order for your kubectl to connect to your cluster it will need to authenticate 
to it. So your kubectl takes the information associated with the cluster. Takes the 
information related to the authentication. And then authenticates with one of the 
cluster. 
 


---

## Page 6

What is the difference between Readyness probe and Liveness probe. 
Readyness Probe – is used to determine whether pod is ready to accept the traffic or 
not 
Liveness probe checks the status of the container (whether it is running or not). If the 
liveness probe fails, then automatically container move on with its restart policy. 
 
 
 


---

## Page 7

 
 
What is the difference between Deployments and StatefulSets. 
Statefulsets is used for Stateful applications such as databases MongoDB, MySQL, each 
replica of the pod will be using its own Volume, If you are deleting the statefulsets it will 
not delete the volumes associated with the Statefulsets. Basically it is used when an 
application need a stable pod hostname (instead of podname-randomstring). 
For Example: podname-0, podname-1, podname-2. (And when a pod gets rescheduled 
it will keep that identity). 
Deployment is a resource to deploy a stateless application like frontend, backend, if 
using a PVC, all replicas will be using the same Volume. 
What is Daemon Sets? 
DaemonSet is a controller similar to ReplicaSet that ensures that the pod runs on all the 
nodes of the cluster. If a node is added/removed from a cluster, DaemonSet 
automatically adds/deletes the pod. 


---

## Page 8

What is Autoscaling? 
The Horizontal Pod Autoscaler automatically scales the number of Pods in replica set or 
based on observed CPU utilization. 
 


---

## Page 9

 
Explain EndPoints? 
Endpoint tracks the IP Address of the pod, so that service can send traffic to the pod. 
When we create the service the endpoints will also be created automatically. When a 
service selector matches a pod label, that IP Address is added to your endpoints. 
 
 
What is the difference between ConfigMaps and Secrets. 
Confimaps is used to store application configuration like environment variables, 
configuration files. We can mount configmaps as volume. 
 
 


---

## Page 10

Below is the command to create configmap from literal. 
 
Create a file as per below and create configmap of this files. 
File name: dev.properties 
app.env=dev 
app.mem=2048m 
app.properties=dev.env.url 
 
How to mount configmaps as volume. 
 


---

## Page 11

 
 
What is Secrets? 
Secret is used to store sensitive information in an encrypted format. like password, 
token, keys. 
What are the types of secrets we can create? 
1. Generic 
!) File (--from-file) 
!!) Directory 
!!!) Literal Value 
2. Docker Registry 
3. TLS 
Create generic secrets. 
 


---

## Page 12

 
 
 
Create secrets from file. 
Create a file credentials.txt and write the db password into this file. 
# echo “dbpassword” > credentials.txt 
Now create secrets from this file. 
 
 
 
 


---

## Page 13

Create a secret using yaml file. 
 
 
Create secrets using string data, if you create secrets using stringdata the value of 
username and password will be encoded automatically you don’t need to encode it and 
put in yaml. 


---

## Page 14

 
 
 
 
What is Taint and Tolerations? 
Taints are used to repel the pods from a specific node. If you applied taints on a node 
you cannot schedule pods on that node unless it has a matching toleration. 
kubectl taint nodes node1 mysize=large:NoSchedule      to apply the taints. 
kubectl taint nodes node1 mysize=large:NoSchedule-     to remove the taints. 
 


---

## Page 15

 
 
You can see here pod5 has been deployed on worker01, because it has matching 
tolerations. 
What is NoExecute in Taint and Tolerations? 
When you apply the taint NoExecute, on node, pods those are already running on that 
node will be terminated. And you can not schedule pods on that node.  
kubectl taint nodes worker02 mysize=small:NoExecute      to apply the taints. 
 
 
 
When you apply the below configurations, pod will tolerate the node till 60 seconds 
only, after 60 seconds it will be in terminated. 


---

## Page 16

 
 
Which are the deployment strategies available in Kubernetes? 
1) Recreate  
2) Rolling Update 
3) Blue/Green 
4) Canary 
Recreate: In the Recreate Strategy, if you are deploying version2 application, it will 
delete version1 pods first, then it will create pods of version2. 
RollingUpdate: Rolling update is used when you want to deploy your new version 
without having downtime to your application. 
For example: When we deploy new instance of the applications, a new pod will be 
created and the existing pod will be destroyed, after the new pod up and running and 
this happens for every ReplicaSet. 
maxUnavailable: 0 (How many pods you want to unavailable of the version1 while 
deploying version2. 
 
 


---

## Page 17

What is Role? 
Role is used to grant access to resources within a single namespace.  
What is Role Binding? 
And role binding is used to grant the permissions defined in a role to a user or set of 
users. 
Practicle: 
 
We can see in above screenshot that user zeal not able to get the pods in teama 
namespace. 
So let’s create the role that will grant access to user zeal to create pods in teama 
namespace. 
 
 


---

## Page 18

 
 
 
 
Now try to access the pods using zeal user. 
 
 
 
 
 
 


---

## Page 19

Cluster Role and Cluster Role Binding 
What is Cluster Role? 
Cluster Role and ClusterRoleBinding is used to grant permssions at the cluster level 
resources like pods, secrets, service, and in all the namespaces. 
Practicle: 
Try to access pods at cluster level using zeal user you will get forbidden. 
 
Now create clusterrole and clusterrolebinding to access pods in all the namespaces of 
cluster. 
# vim clusterrole.yaml 
 
# kubectl apply –f clusterrole.yaml 
 
 
 
 
 
 
 


---

## Page 20

# vim clusterrolebinding.yaml  
 
# kubectl apply –f clusterrolebinding.yaml 
Now try to access pods in all the namespace. 
 
You can see above zeal user can access the pods in all the namespaces. 
 
 
 
 
 
 


---

## Page 21

What is Resource Quota? 
There are two types of Resource Quota. 
1. Compute Resources 
2. Object Count 
Compute Resources quota is used to set limit of CPU and memory on a namespace 
level. 
Object Count is used to set limit of objects to be deploy within a namespace.   
 
 
Practicle: 
 


---

## Page 22

 


---

## Page 23

 
 


---

## Page 24

What is Resource Limit? 
Resource Limit is used to set cpu and memory limit to pods. When we create a pod by 
default it uses the whole cpu and memory, so to apply limit on pod we can use resource 
limit. 
Practicle: 
 
 
 
 
 
 
 
 
 
 
 


---

## Page 25

What is the difference between PV and PVC. 
PersistentVolume (PV) is a piece of storage and it is also a cluster resource that has been 
provisioned by an administrator or dynamically provisioned using storage class. 
PersistentVolumeClaim (PVC) is a request for storage by a user for the application to use 
10GB. 
In real life scenario, PV is whole cake and PVC is piece of cake (But you can have a whole 
cake if there are no other people to eat (just like if there are no other application to use 
you can use whole PV )). 
 
 
 


---

## Page 26

What are the different types of Volumes? 
EBS 
OpenEBS 
NFS 
GlusterFS 
Cinder 
What is Storage Class? 
Storageclass is a Kubernetes object that stores information about creating a persistent 
volume for your pod. With a storageclass, we don’t need to create a persistent volume 
separately before claiming it. 
Below are the storage classes available. 
AWS EBS 
Azure Disk 
OpenStack Cinder 
GCE PD 
NFS 
OpenEBS 
Local 
 
 
 
 
 
 
 
 


---

## Page 27

What is Security Context? 
When you run a container, it runs with the UID 0, means root user, In-case of container 
breakouts, attacker can get root privileges to your entire system. So to avoid this we can 
use security context which allows us to run container as non-root user. 
 
 
 


---

## Page 28

KUBERNETES TROUBLESHOOTING 
1. OOMKilled 
 
 
When a pod reaches its memory limit it restarts. You can see the restart count when 
you run the describe command. The obvious solution is to increase the memory 
setting. This can be done by running kubectl edit deployment myDeployment -n 
mynamespace and editing the memory limit. 
 


---

## Page 29

2. Sudden Jumps in Load / Scale 
If the application traffic is suddenly increases. You can scale your replicas by executing a 
command. 
# kubectl scale deployment myDeployment –replicas=5 
If you use an autoscaler (e.g. Horizontal Pod Autoscaler) then this process can be 
automated. 
3. Rollbacks 
 
If you deployed a version 2 on cluster, and there is issue with version2 and you want to 
rollback to previous version that time you can rollback your deployment.  
You can check the history of deployment by executing. 
kubectl rollout history deployment myDeployment 
 


---

## Page 30

 
4. Logs 
You can check the logs of pod. 
CrashloopBackoff 
When the problem is CrashLoopBackOff (your pod is starting, crashing, starting 
again, and then crashing again)  
 
There can be many reasons for this error. 


---

## Page 31

1. Your Dockerfile doesn’t have a Command (CMD), so your pod will 
immediately exit after starting. 
2. You have used the same port for two containers inside the same pod. All 
containers inside the same pod have the same ip address; they are not permitted 
to use the same ports. You need a separate port for every container within your 
pod.  
3. Kubernetes can’t pull the image you have specified, and therefore keeps 
crashing. 
4. Run kubectl logs podName to get more information about what caused the 
error. 
 
Issues 
I have deployed Jenkins on cluster, container was trying to create a file in 
/var/Jenkins_home/ copy_reference_file.log. And it is getting permission denied. 
[mohammed@db-test-k8master ~]$ kubectl logs -f jenkins-5cdc87888f-988ws   -n 
corestack-test 
touch: cannot touch '/var/jenkins_home/copy_reference_file.log': Permission 
denied 
Can not write to /var/jenkins_home/copy_reference_file.log. Wrong volume 
permissions? 
[mohammed@db-test-k8master ~]$ 
I am getting this issue because of Jenkins is running as Jenkins user when I change 
the user from Jenkins to root in deployment file issues has been fixed. I added the 
below parameters in deployment file. 
      securityContext: 
          runAsUser: 0     
          runAsGroup: 0 
          fsGroup: 0 
 


---

## Page 32

 
Worker Node Failure Reason. 
OutOfDisk -> You can check the Disk size if it full please increase. 
MemoryPressure -> You can check the memory if it is full. 
DiskPressure -> You can check the disk space 
PIDPressure 
You can check the kubelet service by executing. 
Journalctl –u kubelet 
Also you can check the certitficates of worker node if it is expired by executing below 
command. 
Openssl x509 –in  /var/lib/kubelet/worker-1.crt  -text 
 


---

