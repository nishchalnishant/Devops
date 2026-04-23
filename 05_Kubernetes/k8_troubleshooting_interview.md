# Content from k8_troubleshooting_interview.pdf

## Page 1

TROUBLESHOOTING TECHNIQUES 
IN K8S 
CRASHLOOPBACKOFF: it error indicates that will automatically starting, 
crash and then restart the pod again repeatedly. 
1. check the logs of the pods : kubectl logs pod-name 
2. describe the pod : kubectl describe pod pod-name 
3. ENSURE THAT THE POD CONFIGURATIONS AND ENVIRONMENT 
VARIABLES ARE CORRECTLY SET. 
4. Verify the entrypoint of a container 
5. Ensure that there are no resource limitations preventing the pod from 
running. 
 
IMAGEPULLBACKOFF: this error occurs when k8s cant able to pull image 
from registry (Dockerhub, ECR) 
1. describe the pod : kubectl describe pod pod-name 
2. Check The imagename of pod config file (YAML) 
3. Check the secrets : kubectl get secret 
 
PENDINGPODS: This error will occurs when a pod is in pending state when 
it is unable to schedule on to a node 
10 pods (worker : t2.micro) 
11th pod pending 
if any pod was deleted from that 10 pods, then 11th pod will be created 
 
1. describe the pod : kubectl describe pod pod-name 
2. check the nodes : kubectl get no 


---

## Page 2

NODENOTREADY: A node is in a NoTReady State when its unable to 
participate in the cluster 
1. describe the node : kubectl describe node node-name 
2. Review the node logs : kubectl logs node node-id 
 
UNAUTHORIZED ERROR: This error indicates a failure in API 
Authentication 
1. Check your credentials 
2. describe the resource : kubectl describe resource resource-name 
3. Check the RBAC policies 
4. Check the service account tokens are valid or not 
5. check the kubeconfig file configured correctly or not 
 
FailedScheduling: This error occurs when the scheduler cant find any 
suitable node for a pod. 
1. describe the pod : kubectl describe pod pod-name 
2. check the resources of a pod (CPU, Memory) 
 
OOMKILLED : This error will occur when a pod was killed itself because it 
exceeds the memory limits. 
1. check the resources of pods 
2. describe the pod 
3. increase the pod memory limit 
4. optimising the app to use less memory 
 
ERROR CREATING LOADBALANCER: it error will occurs when k8s cant 
communicate with cloud provider. 


---

## Page 3

1. describe the service : kubectl describe service service-name 
2. check the IAM permissions on AWS account 
3. Check the cloud provider integration configuration is successfully 
configured or not 
4. Verify the service file annotations (YAML) 
 
ContainerCreatingerror: this error will occurs when we didnt pass correct 
container configurations on yaml file 
1. describe the pod : kubectl describe pod pod-name 
2. check the container configurations on YAML file 
3. Imagepull Issue check 
4. Verify the node has sumcient resources or not 
5. Ensure that there are no networking issues. 


---

## Page 4

 
DEPLOYMENT 
STRATEGY IN 
K8S 


---

## Page 5

 
 
 
1. 
Canary Deployment 
 
 
2. 
Recreate Deployment. 
 
 
 
WHAT IS DEPLOYMENT STRATEGY 
These are the techniques which 
are used to manage the rollout 
and scaling of applications 
within a Kubernetes cluster 
3. 
Rolling update 
 
 
4. 
Blue-Green Deployment 


---

## Page 6

 
1. CANARY DEPLOYMENT 
 
 
 
A Canary Deployment involves rolling out a new version of your application to a 
subset of your pods or a percentage of your traffic to test it before deploying it to 
the entire application in production. 


---

## Page 7

 


---

## Page 8

2. RECREATE  DEPLOYMENT: 
 
 
 
In this strategy, the existing version of the application is terminated completely, and a new 
version is deployed in its place. This approach is simple but may cause downtime during the 
update. 


---

## Page 9

3. Rolling Update 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
create new pods 
It starts by creating a few 
pods of the new version 
Monitor Pods 
It monitors the new pods 
to make sure they are 
healthy and working well. 
Route traffic 
If the new pods are 
working fine, Kubernetes 
gradually increases their 
number while reducing 
the old pods. 
Delete old pods 
This process continues 
until all pods are running 
the new version, and the 
old version has been 
phased out. 
 
pod 
 
pod 


---

## Page 10

create a deployment file 
 
execute this file : kubectl create -f deployment.yml 
Check the deployments now : kubectl get deployment 
Check the RS : kubectl get rs 
 
 
 
 
 
 
 
 
 
 
 


---

## Page 11

Now update the image: kubectl set image deployment/nginx-deployment nginx=shaikmustafa/cycle 
Check the RS : kubectl get rs 
 
 
 
 
 
Now we can observe, old pods from RS-1 was completely deleted and RS-2 created new pods for 
version-2 it contains some downtime, To avoid this we will use Rolling Updates 


---

## Page 12

create a deployment file with strategy: 
execute this file : kubectl create -f deployment.yml 
Check the deployments now : kubectl get deployment 
Check the RS : kubectl get rs 
 
 
 
 
 
 maxSurge specifies how many new Pods can be 
created by the Deployment controller in a “roll” in 
addition to the number of DESIRED 
 maxUnavailable refers to how many old Pods can be 
deleted by the Deployment controller in a “rolling” 


---

## Page 13

Now update the image: kubectl set image deployment/nginx-deployment nginx=shaikmustafa/cycle 
Check the RS : kubectl get rs 
 
 
 
 
 
 
 
 
 
So we have 3 Pod copies, then the controller will always ensure that at least 2 Pods are available 
during the “rolling update” process, and at most only 4 Pods exist in the cluster at the same time. 
This strategy is a field of the Deployment object, named RollingUpdateStrategy 


---

## Page 14

4. BLUE-GREEN  DEPLOYMENT 
 
 
version-1 
version-2 
 
 
 
 
A Blue/Green deployment is a way of accomplishing a zero-downtime upgrade to an existing 
application. The “Blue” version is the currently running copy of the application and the “Green” 
version is the new version. Once the green version is ready, traffic is rerouted to the new version 


---

## Page 15

Step 1: Create Blue Deployment 
Step 2: Create Green Deployment 
 
 
create same deployment with same 
image but change names and env of 
the deployment. 
 
 
 
Now execute both the deployments 
 
kubectl create -f blue.yml 
kubectl create -f green.yml 


---

## Page 16

Step 3: Create a Service 
 
 
Now execute the service file 
 
kubectl create -f svc.yml 
 
 
 
 
 
Now verify that nginx image is running in the browser or not. 
That means we can see the application running in the blue 
environment. 


---

## Page 17

Step 5: Perform Blue-Green Deployment 
 
Now that we have both blue and green deployments running, we can perform the Blue-Green 
Deployment by routing traffic from the blue deployment to the green deployment. 
 
Now update the image in green-deployment file 
from nginx to httpd 
 
 
 
 
kubectl apply -f green.yml 
 
 
 
 
 
 


---

## Page 18

Now update the service - to route 
traffic to the green deployment. To do 
this, update the label selector in the 
service manifest to select the green 
deployment. 
 
 
 
 
kubectl apply -f svc.yml 


---

## Page 19

 
 
 


---

## Page 20

 
 
Finally, we need to verify that the deployment was successful 


---

