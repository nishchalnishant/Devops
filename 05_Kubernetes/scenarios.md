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

# Content from cluster_health_checklist.pdf

## Page 1

30 checks. Zero theory.
Built for teams who own uptime and cost.
30-Point
Kubernetes Cluster
Health Checklist


---

## Page 2

Scheduling Rules
Node Pressure Signals
Workload Hygiene Gaps
Autoscaling Logic Failures
Cost Surface Leaks
Control Plane Drift
Clusters don’t explode randomly.
They decay slowly — then fail loud at 3am.
These 30 checks are built to catch silent failures
before they wreck your uptime or spike your cloud bill.
Each section in this checklist
maps to one of these layers.
Top layers = most likely to
cause real incidents.
Run monthly (Infra360 default cadence)
Copy commands directly
Flag check owner
How This Checklist Works
Why Monthly?
Kubernetes Fails in
Layers
How to Use It


---

## Page 3

01—06: Scheduling & Survival
01
02
03
04
05
06
No.
Mechanism
Exact Check
(Pods that live vs die)
Pods without resource
requests
QoS class distribution
(BestEffort present in prod
= red flag)
Requests > node
allocatable
Critical workloads not
Guaranteed QoS
Over-replication “just in
case”
DaemonSets not included
in capacity math
kubectl get pod -A -
o=jsonpath='{range .items[]}
{.metadata.namespace}/{.metadat
a.name}{"\t"}
{.spec.containers[].resources}
{"\n"}{end}' | grep -v requests
kubectl get pod -A -o custom-
columns=NS:.metadata.namespac
e,NAME:.metadata.name,QOS:.stat
us.qosClass
kubectl describe node | grep -A5
Allocated
same QoS command + service
tiering
kubectl get deploy -A -o custom-
columns=NS:.metadata.namespac
e,NAME:.metadata.name,REPLICA
S:.spec.replicas
kubectl get ds -A -o custom-
columns=NS:.metadata.namespac
e,NAME:.metadata.name,REQ:.spe
c.template.spec.containers[*].reso
urces.requests


---

## Page 4

07—11: Node Reality Checks
07
08
09
10
11
No.
Mechanism
Exact Check
(What kubelet is screaming quietly)
MemoryPressure /
DiskPressure ignored
Evictions happening
quietly
ImageFS filling up
PID exhaustion risk
Uneven pod distribution
across nodes
kubectl describe node | egrep
"MemoryPressure|DiskPressure|PI
DPressure"
kubectl describe node | grep -i
eviction
df -h /var/lib/containerd
/var/lib/docker
kubectl describe node | grep -i pid
kubectl get pod -A -o wide


---

## Page 5

12
13
14
15
16
No.
12—16: Workload Hygiene 
Mechanism
Exact Check
(Things that rot slowly)
CrashLoopBackOff
masking startup/config
bugs
InitContainers failing but
ignored
Old ReplicaSets piling up
Deployments with no
liveness/readiness probes
Probes too aggressive
(self-DDOS)
kubectl get pod -A | grep
CrashLoopBackOff
kubectl logs <pod> --previous
kubectl get pod -A | grep Init
kubectl get rs -A | wc -l
Fix: revisionHistoryLimit
kubectl get deploy -A -
o=jsonpath='{range .items[]}
{.metadata.namespace}/{.metadat
a.name}{"\t"}
{.spec.template.spec.containers[].l
ivenessProbe}{"\n"}{end}'
probe configs vs startup time


---

## Page 6

17
18
19
20
No.
17—20: Autoscaling Illusions 
Mechanism
Exact Check
HPA scaling on CPU for
non-CPU workloads
HPA maxReplicas never hit
(means it’s useless)
VPA running without
guardrails
Cluster Autoscaler fighting
PDBs
kubectl get hpa -A
kubectl describe hpa
kubectl get vpa -A
kubectl get pdb -A


---

## Page 7

21
22
23
24
25
No.
21—25: Networking & Cloud
Cost Bleeds
Mechanism
Exact Check
Zombie namespaces
Orphaned LoadBalancer
services
Idle node pools kept alive
by 1 pod
Ingress controllers over-
provisioned
Unused PVCs still
attached
kubectl get ns --sort-
by=.metadata.creationTimestamp
kubectl get svc -A | grep
LoadBalancer
kubectl get pod -A -o wide
kubectl get deploy -n ingress-
nginx
kubectl get pvc -A


---

## Page 8

26
27
28
29
30
No.
26—30: Control Plane & Signal
Hygiene
Mechanism
Exact Check
API server event spam
ignored
Excessive watch/list traffic
(client abuse)
RBAC drift (old service
accounts still live)
Secrets never rotated
No human ownership per
namespace
kubectl get events -A --sort-
by=.lastTimestamp | tail -50
API server metrics / audit logs
kubectl get sa -A
kubectl get secret -A --sort-
by=.metadata.creationTimestamp
kubectl get ns --show-labels
Look for owner=


---

# Kubernetes Troubleshooting Runbook

A senior engineer approaches every Kubernetes failure with a systematic **command → evidence → hypothesis → fix** loop. Never guess a root cause. Gather evidence first.

---

## Golden Rule: The First 60 Seconds

Before touching anything, run this triage sequence:

```bash
# 1. What is failing?
kubectl get pods -A | grep -v Running | grep -v Completed

# 2. When did it start? Any recent changes?
kubectl get events -A --sort-by=.lastTimestamp | tail -30

# 3. Is it just one pod or widespread?
kubectl top nodes
kubectl top pods -A --sort-by=memory
```

---

## Scenario 1: CrashLoopBackOff

The container starts, crashes, and Kubernetes keeps restarting it. The backoff timer grows exponentially (10s → 20s → 40s → ... → 5m).

### Root Cause Decision Tree

**Step 1 — Read the most recent crash logs:**
```bash
kubectl logs <pod> --previous
kubectl logs <pod> -c <container> --previous
```

**Step 2 — Read the pod events:**
```bash
kubectl describe pod <pod>
# Focus on: Events section, Exit Code, Last State
```

**Exit Code → Root Cause Mapping:**

| Exit Code | Meaning | Likely Cause |
|---|---|---|
| `0` | Clean exit | Entrypoint ran to completion — not a server process |
| `1` | General error | Application crash — check logs |
| `2` | Misuse of shell builtins | Bad script syntax |
| `137` (`SIGKILL`) | OOMKilled | Memory limit exceeded |
| `139` (`SIGSEGV`) | Segmentation fault | Native code bug, dependency ABI mismatch |
| `143` (`SIGTERM`) | Graceful shutdown terminated | Readiness probe failing repeatedly |

### Fix Paths

**OOMKilled (`Exit Code 137`):**
```bash
# Confirm OOM
kubectl describe pod <pod> | grep -A5 "Last State"
# Output: Reason: OOMKilled

# Fix: Increase memory limit
kubectl set resources deployment <name> --limits=memory=1Gi
# Or edit the deployment YAML and increase spec.containers[].resources.limits.memory
```

**Bad Entrypoint / Missing Config:**
```bash
# Override the entrypoint temporarily to get a shell
kubectl debug <pod> -it --image=busybox --target=<container>
# Or patch the deployment command to sleep
kubectl patch deployment <name> --patch '{"spec":{"template":{"spec":{"containers":[{"name":"<container>","command":["sleep","3600"]}]}}}}'
kubectl exec -it <pod> -- sh
# Now manually run the original entrypoint and read the error
```

**Missing Secret or ConfigMap:**
```bash
# Check if the referenced secret/configmap exists
kubectl get secret <secret-name> -n <namespace>
kubectl get configmap <cm-name> -n <namespace>
# If missing, create it or fix the reference in the pod spec
```

**Bad Probe Configuration (killing healthy pods):**
```bash
kubectl describe pod <pod> | grep -A10 "Liveness\|Readiness"
# If initialDelaySeconds is too short for a slow-starting app, add a startupProbe
```

---

## Scenario 2: OOMKilled (deep dive)

### Detection
```bash
kubectl describe pod <pod> | grep -A5 "Last State"
# Reason: OOMKilled

# Check current usage vs limits
kubectl top pod <pod> --containers
kubectl describe pod <pod> | grep -A4 "Limits\|Requests"
```

### JVM-specific (Java OOM)
Java OOM is almost never the heap alone. Non-heap eats significant memory:
- **Metaspace** → Class metadata
- **Thread stacks** → Each thread ~512KB–1MB
- **Native memory** → JIT compiler, JNI, off-heap buffers

```bash
# Rule of thumb: container memory limit = -Xmx + 25-50% overhead
# Example: -Xmx2g → set limit to 3–3.5Gi

# Enable container-aware JVM
JAVA_OPTS="-XX:+UseContainerSupport -XX:MaxRAMPercentage=75.0"
```

### Fix Checklist
1. Increase `resources.limits.memory` in the Deployment spec.
2. Add a `VerticalPodAutoscaler` resource (VPA) to auto-right-size over time.
3. Profile the application: confirm whether the OOM is a memory leak or genuinely undersized limits.

---

## Scenario 3: Pod Stuck in Pending / FailedScheduling

### Systematic Inspection
```bash
kubectl describe pod <pod>
# Focus: Events → "FailedScheduling"
# The scheduler prints the exact reason
```

### Common Reasons and Fixes

**Insufficient resources:**
```bash
# Events will show: "Insufficient cpu" or "Insufficient memory"
kubectl describe nodes | grep -A10 "Allocated resources"
# Fix: Scale out the node pool, or reduce pod requests
```

**Taint mismatch:**
```bash
kubectl describe nodes | grep Taint
# If node has: node.kubernetes.io/not-ready:NoSchedule
# And pod has no matching toleration → pod stays Pending
# Fix: Add toleration to pod spec OR remove the taint if you own the node
```

**NodeSelector / NodeAffinity mismatch:**
```bash
kubectl get nodes --show-labels
kubectl describe pod <pod> | grep -A10 "Node-Selectors\|Affinity"
# Fix: Ensure label exists on at least one node, or relax affinity rules
```

**PVC zone binding mismatch:**
```bash
kubectl get pvc <pvc-name>
kubectl describe pvc <pvc-name>
# If PVC is bound to us-east-1a but pod is scheduled to us-east-1b:
# Fix: Use WaitForFirstConsumer volumeBindingMode in StorageClass
```

**Resource Quota exhaustion:**
```bash
kubectl describe quota -n <namespace>
# Fix: Increase quota limits or reduce pod requests
```

---

## Scenario 4: Node NotReady

A node transitions to `NotReady` — pods on that node get evicted after `pod-eviction-timeout` (default: 5 minutes).

### Triage
```bash
kubectl describe node <node-name>
# Focus: Conditions section — look for:
# MemoryPressure, DiskPressure, PIDPressure, NetworkUnavailable, Ready=False

# Check the kubelet log on the node itself
journalctl -u kubelet -f --since "5 minutes ago"
```

### Root Causes

**Disk pressure:**
```bash
# On the node (via SSH or kubectl debug node)
df -h /var/lib/kubelet
df -h /var/lib/docker  # or /var/lib/containerd

# Fix: Clean up unused images
crictl rmi --prune
# Or expand the disk backing the node
```

**Memory pressure:**
```bash
free -m
# Fix: Evict low-priority pods or add nodes. Set proper requests/limits
# to prevent noisy neighbours exhausting node memory.
```

**CNI plugin failure (NetworkUnavailable=True):**
```bash
kubectl get pods -n kube-system | grep -i 'calico\|flannel\|cilium\|cni'
kubectl logs -n kube-system <cni-pod>
# Fix: Restart the CNI DaemonSet, or re-apply the CNI manifest
```

**Kubelet cannot reach the API server:**
```bash
# On the node
curl -k https://<api-server-ip>:6443/healthz
# If failing → check firewall rules, NSG, security groups between node and control plane
```

---

## Scenario 5: DNS Failures

DNS failures in Kubernetes are deceptive — pods exist and are Running, but service-to-service calls fail with `NXDOMAIN` or `connection refused`.

### Triage Sequence
```bash
# 1. Test DNS from inside a pod
kubectl run dnstest --image=busybox --restart=Never --rm -it -- nslookup kubernetes.default

# 2. Check if CoreDNS pods are healthy
kubectl get pods -n kube-system -l k8s-app=kube-dns
kubectl logs -n kube-system -l k8s-app=kube-dns

# 3. Check CoreDNS ConfigMap for misconfigurations
kubectl get configmap coredns -n kube-system -o yaml
```

### Common Root Causes

**`ndots:5` causing slow resolution:**

By default, Kubernetes sets `ndots: 5` in `/etc/resolv.conf` inside every pod. This means a query for `payment-api.production.svc.cluster.local` causes 5 internal FQDN lookups before the external lookup. Under high query volume, this creates CoreDNS saturation.

```bash
# Fix: Override ndots in pod spec
spec:
  dnsConfig:
    options:
    - name: ndots
      value: "1"
```

**CoreDNS forwarding loop:**
```bash
kubectl logs -n kube-system <coredns-pod> | grep loop
# If you see "Loop detected" errors, the CoreDNS upstream is forwarding back to itself.
# Fix: Edit coredns ConfigMap and set a specific upstream (e.g., 8.8.8.8) instead of /etc/resolv.conf
```

**NetworkPolicy blocking port 53:**
```bash
kubectl get networkpolicies -A
# If a policy restricts egress from app namespace, UDP/TCP port 53 to kube-system must be explicitly allowed
```

---

## Scenario 6: ImagePullBackOff

```bash
kubectl describe pod <pod>
# Events: "Failed to pull image ... unauthorized / manifest unknown / not found"
```

| Error | Root Cause | Fix |
|---|---|---|
| `unauthorized` | No `imagePullSecret` or wrong credentials | Create/attach the correct `imagePullSecret` |
| `manifest unknown` | Tag doesn't exist in the registry | Verify tag with `docker manifest inspect` or registry UI |
| `not found` | Wrong registry URL or private registry unreachable | Check `image:` field for typos; verify network egress from node |
| `x509: certificate signed by unknown authority` | Self-signed registry cert not trusted by containerd | Add cert to containerd trusted CAs |

**Creating an imagePullSecret for Azure Container Registry:**
```bash
kubectl create secret docker-registry acr-secret \
  --docker-server=<myregistry>.azurecr.io \
  --docker-username=<SP-app-id> \
  --docker-password=<SP-password> \
  -n <namespace>
```

---

## Scenario 7: HPA Not Scaling

```bash
kubectl describe hpa <hpa-name>
# Check: "unable to get metrics for resource cpu" or "metrics not available"
```

**Root Cause 1: metrics-server not installed:**
```bash
kubectl top pods  # If this fails, metrics-server is missing
kubectl get deployment metrics-server -n kube-system
# Fix: Install metrics-server
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

**Root Cause 2: Custom metrics API not registered:**
```bash
kubectl get apiservice v1beta1.custom.metrics.k8s.io
# If missing, the HPA cannot use custom metrics (e.g., RPS from Prometheus)
# Fix: Deploy Prometheus Adapter and register the APIService
```

**Root Cause 3: Pods at limits but HPA not triggering:**
```bash
kubectl describe hpa <name>
# Check: Current vs. Desired replicas, and the "Conditions" section
# "ScalingActive=False: FailedGetResourceMetric" → resource requests not set on the pod
# Fix: Ensure containers have resources.requests.cpu set — HPA uses this as the denominator
```

---

## Scenario 8: Service Mesh 503 Errors (Istio)

```bash
# Check Envoy proxy access logs
kubectl logs <pod> -c istio-proxy | grep "503\|UF\|NR"

# UF = Upstream connection failure
# NR = No route found (DestinationRule missing)
```

**mTLS mode mismatch (most common):**
```bash
kubectl get peerauthentication -A
kubectl get destinationrule -A
# If one service is in STRICT mTLS mode but the caller has no sidecar (or DISABLE mode):
# Fix: Add sidecar injection to the calling namespace, or set PERMISSIVE mode temporarily
```

**Circuit breaker tripped:**
```bash
kubectl describe destinationrule <name>
# Check outlierDetection settings — if too aggressive, healthy pods get ejected
```

---

## Scenario 9: etcd High Latency / Leader Elections

```bash
# On the control plane node
ETCDCTL_API=3 etcdctl \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  endpoint status --write-out=table

# Check for: "db size", "raft term", "leader"
# If db size > 2GB, run defragmentation
etcdctl defrag --endpoints=https://127.0.0.1:2379 <certs>

# Compact old revisions to free space
REV=$(etcdctl endpoint status --write-out="json" | egrep -o '"revision":[0-9]*' | egrep -o '[0-9]*' | head -1)
etcdctl compact $REV
```

**Leader elections (split brain indicator):**
- If the leader keeps changing in a 3-node cluster, look for network partitions between control plane nodes.
- Check disk I/O latency on etcd nodes — etcd is extremely sensitive to disk latency (requires < 10ms fsync).
# Content from kubernetes_scenario_based_questions.pdf

## Page 1

SRE Kubernetes Scenario-Based 
Questions and Answers 
1. 500 Errors from Kubernetes-hosted API 
• 
- Step 1: Identify affected pods via logs: 
kubectl logs -l app=my-api --tail=100 
• 
- Step 2: Check pod health and events: 
kubectl describe pod <pod-name> 
• 
- Step 3: Inspect service and ingress: 
kubectl get svc,ingress -n <namespace> 
• 
- Step 4: Correlate with Prometheus/Grafana for spikes. 
• 
- Remediation: Fix code/config bug, rollout patch: 
kubectl rollout restart deployment my-api 
2. Job Failed Silently 
• 
- Add observability: 
• 
- Use Kubernetes CronJob with .spec.successfulJobsHistoryLimit 
• 
- Add alerting via Prometheus + Alertmanager: 
• 
- alert: JobFailed 
expr: kube_job_status_failed > 0 
for: 5m 
labels: 
severity: critical 
• 
- Log to centralized system (e.g., Loki/ELK). 
3. OOMKilled Pods 
• 
- Check OOM events: 
kubectl get events --field-selector reason=OOMKilling 


---

## Page 2

• 
- Right-size limits using metrics from kubectl top pod or Prometheus: 
resources: 
requests: 
memory: "256Mi" 
limits: 
memory: "512Mi" 
• 
- Use VPA (Vertical Pod Autoscaler) and monitor with kube-state-metrics. 
4. Safe Deployment Strategies 
• 
- Implement: 
• 
- RollingUpdate with pause: 
strategy: 
type: RollingUpdate 
rollingUpdate: 
maxUnavailable: 1 
maxSurge: 1 
• 
- Canary using Flagger or Argo Rollouts 
• 
- Manual promotion pipeline in CI/CD (e.g., GitHub Actions, Azure DevOps). 
5. Increased Latency Between Microservices 
• 
- Tools: 
• 
- Istio/Linkerd metrics 
• 
- Prometheus + Grafana dashboard 
• 
- kubectl exec with curl and time for latency 
• 
- Check: 
• 
- Service discovery 
• 
- DNS latency 
• 
- Network policies 
• 
- Resource pressure on nodes 
6. Multi-Region DR for Stateful Workload 
• 
- Steps: 


---

## Page 3

• 
- Use etcd backups or storage replication (e.g., Portworx, Velero) 
• 
- Deploy to second region with same manifests 
• 
- Test failover with simulated outages 
• 
- Test DR: 
kubectl cordon node && kubectl drain node --ignore-daemonsets 
7. Node Flapping Ready/NotReady 
• 
- Investigate: 
kubectl describe node <node-name> 
journalctl -u kubelet 
• 
- Common causes: 
• 
- Resource exhaustion 
• 
- Kubelet crash 
• 
- CNI issues 
• 
- Prevent: 
• 
- Use node auto-replacement with autoscaler 
• 
- Monitor node health 
8. Custom Resource Reconcile Failure 
• 
- Check: 
kubectl get crd 
kubectl describe <custom-resource> 
kubectl logs -l name=<operator-name> 
• 
- Fix: 
• 
- Validate CRD versions 
• 
- Restart operator or reconcile manually 
9. Pod Evictions in Node Pool 
• 
- Check: 
kubectl get events | grep Evicted 
• 
- Investigate node pressure (kubectl describe node) 
• 
- Causes: 
• 
- Disk pressure 


---

## Page 4

• 
- Memory shortage 
• 
- Prevent: 
• 
- Taints and tolerations 
• 
- Resource requests/limits 
• 
- Monitor with kubelet exporter 
10. DNS Failures (CoreDNS) 
• 
- Debug: 
kubectl logs -n kube-system -l k8s-app=kube-dns 
kubectl exec -it <pod> -- nslookup <svc-name> 
• 
- Tune: 
• 
- Increase CoreDNS replicas 
• 
- Cache TTL 
• 
- Monitor: 
Use CoreDNS metrics plugin + Prometheus 
11. Prometheus Scrape Intermittent 
• 
- Check targets: 
http://<prometheus>:9090/targets 
• 
- HA setup: 
Use Thanos or Cortex 
• 
- Fix: 
Adjust scrape_interval, service monitor timeout 
12. Prometheus vs App Metrics Discrepancy 
• 
- Validate app endpoint manually: 
curl http://<pod-ip>:<port>/metrics 
• 
- Check exporter logic or label mismatch 
• 
- Prometheus relabel config validation 


---

## Page 5

13. Pod in ImagePullBackOff 
• 
- Advanced checks: 
kubectl describe pod <pod> 
docker pull <image> on node (if accessible) 
• 
- Check: 
• 
- Image secret 
• 
- Network/DNS 
• 
- Tag existence 
14. Audit Kubernetes for SRE Compliance 
• 
- Focus Areas: 
• 
- RBAC policies 
• 
- Resource limits 
• 
- Network Policies 
• 
- Pod disruption budgets 
• 
- Logging and monitoring presence 
• 
- CI/CD pipelines 
15. Scaling But Dropped Traffic 
• 
- Check: 
• 
- HPA status 
• 
- Service endpoints: kubectl get ep 
• 
- Load balancer capacity 
• 
- Fix: 
• 
- Pre-warming 
• 
- Use Istio gateway load testing 
16. CPU Throttling Alerts 
• 
- Check metrics: 
container_cpu_cfs_throttled_seconds_total 
• 
- Fix: 
• 
- Increase CPU limits 
• 
- Use guaranteed QoS class (request = limit) 


---

## Page 6

17. Network Policy Blocked Services 
• 
- Detect: 
• 
- Use Calico or Cilium observability 
• 
- kubectl get networkpolicy 
• 
- Prevent: 
• 
- Alert on blocked connections 
• 
- Canary policy testing 
18. Ingress Route DNS Issues 
• 
- Debug: 
kubectl describe ingress 
nslookup <domain> 
dig +trace <domain> 
• 
- Check: 
• 
- DNS propagation 
• 
- TLS certs 
19. PVC Stuck in Pending 
• 
- Check: 
kubectl describe pvc <name> 
kubectl get storageclass 
• 
- Fix: 
• 
- Ensure provisioner is installed 
• 
- Permissions correct 
20. High API Server Latency 
• 
- Check metrics: 
apiserver_request_duration_seconds 
• 
- Scale: 
• 
- Add control plane nodes (in self-managed) 
• 
- Tune etcd and kube-apiserver flags 
• 
- Offload controller load 


---


---

## Level 4: Control Plane & Architecture (Architect Level)

### Scenario 15: etcd "Request Time Too Long"
**Symptom:** `kubectl` commands are slow, API server logs show `etcdserver: request stack is taking too long`.
**Diagnosis:** High disk latency on the etcd nodes. etcd is extremely sensitive to disk I/O.
**Fix:** 
- Move etcd to **Local SSDs** or Provisioned IOPS (io2) volumes.
- Check for high snapshotting frequency.
- Separate etcd for events (`--etcd-servers-overrides="/events#..."`) if event volume is huge.

### Scenario 16: API Server OOM during "Watch" Storm
**Symptom:** Kubernetes control plane crashes when a large node pool is scaled up.
**Diagnosis:** Too many clients (controllers, kubelets) are performing "watch" operations on a large set of resources. Each watch consumes memory in the API server.
**Fix:** 
- Implement **API Priority and Fairness (APF)** to throttle low-priority requests.
- Optimize controllers to use **Informers** with proper resync periods instead of raw watches.

### Scenario 17: Mutating Webhook causing "Deployment Deadlock"
**Symptom:** You try to scale a deployment, but no new pods are created. No errors in the deployment controller.
**Diagnosis:** A **MutatingAdmissionWebhook** (like Istio sidecar injector) is failing or timing out. The API server cannot validate/mutate the pod, so it rejects the creation.
**Fix:** 
1. Check webhook health: `kubectl get mutatingwebhookconfigurations`.
2. Review logs of the webhook server.
3. If critical: Set `failurePolicy: Ignore` temporarily (risky, but unblocks deployment).

### Scenario 18: PodDisruptionBudget (PDB) Blocking Maintenance
**Symptom:** `kubectl drain node-x` hangs indefinitely.
**Diagnosis:** A PDB is set to `minAvailable: 1` but there is only 1 pod running. Kubernetes refuses to evict that last pod.
**Fix:** 
- Temporarily increase the replica count of the deployment.
- Or, delete the PDB temporarily to allow the drain.

### Scenario 19: Vertical Pod Autoscaler (VPA) fighting HPA
**Symptom:** Pods are constantly restarting or changing size and count rapidly.
**Diagnosis:** VPA and HPA are both scaling on CPU. VPA increases CPU request, HPA sees lower % usage and scales down count. VPA sees high % and scales up size.
**Fix:** NEVER use VPA and HPA on the same resource (CPU/Memory) simultaneously. Use VPA for sizing (recommendation mode) and HPA for scaling (count).

### Scenario 20: PersistentVolume (PV) Node Affinity Conflict
**Symptom:** Pod is `Pending` with `1 node(s) had volume node affinity conflict`.
**Diagnosis:** The PV is a Local Volume or EBS volume bound to `us-east-1a`, but the pod is being scheduled on a node in `us-east-1b`.
**Fix:** 
- Delete the pod and let it reschedule (if it can).
- If the node is full, you must move the data or add nodes to that specific AZ.

### Scenario 21: Zombie "Terminating" Namespaces
**Symptom:** You delete a namespace, but it stays in `Terminating` for hours.
**Diagnosis:** A "Finalizer" is stuck. Usually a resource (like a Custom Resource) in that namespace cannot be deleted because its controller is down.
**Fix:** 
- Identify the resource with a stuck finalizer: `kubectl get all -n <namespace>`.
- Manually remove the finalizer from the resource metadata (use with caution): `kubectl patch crd <name> -p '{"metadata":{"finalizers":[]}}' --type=merge`.

### Scenario 22: Service Mesh mTLS "Protocol Error"
**Symptom:** App A can talk to App B via IP, but fails with `503` or `404` when going through the Service name.
**Diagnosis:** Istio is expecting mTLS (HTTP/2 with certs), but App A is sending raw HTTP. Or, the sidecar is not injected into one of the pods.
**Fix:** 
- Check injection status: `kubectl get pod -L istio-injection`.
- Verify PeerAuthentication policy: `kubectl get peerauthentication -A`.

### Scenario 23: Secret / ConfigMap "Atomic Update" delay
**Symptom:** You updated a ConfigMap, but the pod is still seeing old values.
**Diagnosis:** Kubelet syncs ConfigMaps every 60s (default). If the ConfigMap is mounted as a volume, it takes time to propagate. If it's an Environment Variable, the pod **must** be restarted.
**Fix:** 
- For Env Vars: Restart pods: `kubectl rollout restart deployment <name>`.
- For Volumes: Wait for sync or use a tool like **Reloader** to auto-restart pods on config changes.

### Scenario 24: "Too Many Requests" (429) from Cloud Provider
**Symptom:** Kubernetes fails to create LoadBalancers or attach EBS volumes. Logs show "Rate Limit Exceeded".
**Diagnosis:** The Kubernetes Cloud Controller Manager (CCM) is making too many API calls to AWS/GCP.
**Fix:** 
- Increase the API rate limits in your Cloud Account.
- Reduce the number of `Service` type `LoadBalancer` objects by using an Ingress Controller (Shared LB).


### Scenario 25: Node-to-Node MTU mismatch (VXLAN)
**Symptom:** Pods on Node A can talk to Pods on Node A, but Pods on Node A cannot talk to Pods on Node B.
**Diagnosis:** The CNI (Calico/Flannel) is using VXLAN, which adds 50 bytes of overhead. If the physical network MTU is 1500, the pod MTU must be 1450.
**Fix:** Update the CNI config to set the correct MTU.

### Scenario 26: Kubelet "ImageGCManager" deleting active images
**Symptom:** Pods fail to start because the image was deleted right after being pulled.
**Diagnosis:** The disk is near `ImageGCHighThresholdPercent`, causing the kubelet to aggressively prune images.
**Fix:** Increase the disk size or lower the `ImageGCLowThresholdPercent`.
