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

