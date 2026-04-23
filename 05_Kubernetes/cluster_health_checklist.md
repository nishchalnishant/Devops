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

