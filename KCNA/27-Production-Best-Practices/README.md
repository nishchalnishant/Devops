# 27 — Production Best Practices

## 1. Learning Objectives

By the end of this chapter you will be able to:

- Explain resource requests/limits and namespace resource quotas for multi-tenant capacity planning.
- Explain Kubernetes version skew policy and safe upgrade strategies.
- Explain Pod Disruption Budgets and their role during voluntary disruptions.
- Explain multi-zone/multi-region high-availability patterns.
- Describe a checklist for hardening a cluster before production use.

**KCNA objectives covered:** Cloud Native Architecture domain — Production Best Practices; synthesizes concepts from Chapters 06-26.

---

## 2. Historical Background

Early Kubernetes adopters frequently ran into painful lessons in production: clusters without resource limits where one noisy Pod starved its neighbors, upgrades that broke compatibility because control plane and node versions drifted too far apart, and rolling restarts that took down every replica of a service simultaneously because nothing protected against too many voluntary disruptions at once. Over time, the community and Kubernetes itself formalized guardrails — **ResourceQuotas**, a strict **version skew policy**, **Pod Disruption Budgets (PDBs)**, and standard **multi-zone HA topologies** — turning hard-won operational lessons into built-in, reusable safety mechanisms.

---

## 3. Motivation: Why Do Production Clusters Need Extra Guardrails Beyond Basic Kubernetes Objects?

**Analogy — The Apartment Building's House Rules:**
A single-family home doesn't need formal house rules — but a large apartment building with many independent tenants (teams/namespaces) absolutely does: rules about how much water/electricity each unit can use (resource quotas), how renovations must be scheduled so not every unit loses power at once (Pod Disruption Budgets), and safety inspections before any major structural change (upgrade policies). Kubernetes production best practices are exactly these building-wide house rules — necessary once you have multiple tenants and real operational stakes, even though they weren't needed when experimenting with a single Pod on a laptop.

### 3.1 How Was This Solved Before These Practices Were Formalized?

Early clusters often ran without resource quotas, without disruption budgets, and with ad-hoc, untested upgrade procedures — relying on tribal knowledge and manual care rather than built-in guardrails.

### 3.2 Why Was That Insufficient?

Without guardrails, a single misbehaving workload could starve an entire multi-tenant cluster's resources, routine node maintenance could take down every replica of a critical service simultaneously, and version-mismatched upgrades could silently break API compatibility.

### 3.3 How Kubernetes Solves It

Kubernetes provides built-in mechanisms — **ResourceQuotas/LimitRanges** for multi-tenant fairness, **PodDisruptionBudgets** to cap simultaneous voluntary disruptions, and a documented **version skew policy** to keep upgrades safe — turning what used to be manual operational discipline into enforceable, declarative cluster configuration.

---

## 4. Core Concepts

### 4.1 Capacity Planning: Requests, Limits, Quotas

| Mechanism | Scope | Purpose |
|---|---|---|
| Resource requests/limits (Chapter 20) | Per-container | Used for scheduling (requests) and runtime enforcement (limits) |
| LimitRange | Per-namespace | Sets default/min/max requests-limits for containers in a namespace |
| ResourceQuota | Per-namespace | Caps total aggregate resource consumption (CPU, memory, object counts) for a namespace |

### 4.2 Pod Disruption Budgets (PDB)

**Definition:** A **PodDisruptionBudget** limits how many Pods of a given application can be voluntarily disrupted (e.g., during a node drain for maintenance) at the same time, ensuring a minimum number/percentage of replicas always remain available.

### 4.3 Version Skew Policy

Kubernetes officially supports a limited version skew between components — e.g., kubelet may be up to a few minor versions behind the API server, but must never be newer than it. Upgrades should proceed one minor version at a time, following the control-plane-first, then-nodes upgrade order.

### 4.4 Multi-Zone/Multi-Region High Availability

Spreading nodes and control plane components across multiple availability zones (or regions) protects against a single zone's failure taking down the whole cluster, typically combined with Pod anti-affinity (Chapter 20) to spread replicas across zones.

---

## 5. Internal Working

```
1. Namespace admin defines a ResourceQuota capping total CPU/memory/
   object counts for the namespace, and a LimitRange setting sane
   per-container defaults
        ↓
2. Application teams deploy workloads; the API server rejects any
   Pod creation that would exceed the namespace's ResourceQuota
        ↓
3. Application owners define a PodDisruptionBudget for critical
   Deployments, capping simultaneous voluntary disruptions
        ↓
4. During a node drain (e.g., for OS patching), the eviction API
   checks the PDB before evicting each Pod — refusing eviction if
   it would violate the budget, until enough replacement replicas
   are healthy elsewhere
        ↓
5. Cluster upgrades proceed control-plane-first, one minor version
   at a time, respecting the documented version skew policy between
   kube-apiserver, kubelet, and other components
```

---

## 6. Architecture

```
┌─────────────────────────────┐
│           Namespace: team-a           │
│  ┌─────────┐  ┌─────────────┐│
│  │ ResourceQuota │  │ LimitRange       ││
│  │ (aggregate caps)│  │ (per-container    ││
│  └─────────┘  │  defaults/limits) ││
│                                  └─────────────┘│
│  ┌─────────────────────────┐│
│  │ Deployment + PodDisruptionBudget  ││
│  │ (min available during drains)     ││
│  └─────────────────────────┘│
└─────────────────────────────┘
         Nodes spread across multiple zones (HA)
```

---

## 7. Component Breakdown

| Component | Role |
|---|---|
| ResourceQuota | Caps aggregate namespace resource/object consumption |
| LimitRange | Sets default/min/max per-container resource values in a namespace |
| PodDisruptionBudget (PDB) | Limits simultaneous voluntary Pod disruptions for an application |
| Eviction API | Checks PDBs before allowing voluntary Pod eviction (e.g., node drain) |
| Version skew policy | Documented compatibility rules between Kubernetes component versions |

---

## 8. Important Terminology

| Term | Meaning |
|---|---|
| ResourceQuota | Namespace-scoped cap on aggregate resource/object consumption |
| LimitRange | Namespace-scoped default/min/max resource constraints per container |
| PodDisruptionBudget (PDB) | Object capping simultaneous voluntary disruptions for a set of Pods |
| Voluntary Disruption | A disruption initiated deliberately (e.g., node drain, Deployment update) as opposed to an involuntary failure |
| Version Skew | The version difference tolerated between different Kubernetes components |
| Multi-zone HA | Spreading nodes/workloads across multiple availability zones for resilience |

---

## 9. YAML Deep Dive

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: team-a-quota
  namespace: team-a
spec:
  hard:
    requests.cpu: "10"
    requests.memory: 20Gi
    limits.cpu: "20"
    limits.memory: 40Gi
    pods: "50"
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: web-pdb
  namespace: team-a
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: web
```

The `ResourceQuota` caps `team-a`'s total resource and Pod-count consumption; the `PodDisruptionBudget` guarantees at least 2 `app: web` Pods remain available at all times during voluntary disruptions like node drains.

---

## 10. kubectl Commands

| Command | Purpose | Example |
|---|---|---|
| `kubectl describe resourcequota` | Inspect current quota usage in a namespace | `kubectl describe resourcequota team-a-quota -n team-a` |
| `kubectl get pdb` | List Pod Disruption Budgets | `kubectl get pdb -n team-a` |
| `kubectl drain <node>` | Safely evict Pods from a node, respecting PDBs | `kubectl drain node-1 --ignore-daemonsets` |
| `kubectl version` | Check API server and client version skew | `kubectl version --short` |
| `kubectl get nodes -o wide` | Check node distribution across zones (via labels) | `kubectl get nodes -o wide --show-labels` |

---

## 11. Hands-on Examples

**Lab 1 — Apply a ResourceQuota and observe a rejected Pod creation:**
```bash
kubectl apply -f team-a-quota.yaml
kubectl run oversized --image=nginx --requests=cpu=15 -n team-a
# Rejected: exceeds the namespace's requests.cpu quota
```

**Lab 2 — Apply a PDB and observe a blocked node drain:**
```bash
kubectl apply -f web-pdb.yaml
kubectl drain node-1 --ignore-daemonsets
# If draining would violate minAvailable, eviction is blocked until
# the Deployment's other replicas are rescheduled and healthy
```

**Lab 3 — Check version skew before an upgrade:**
```bash
kubectl version --short
# Confirm kubelet versions across nodes are within the supported
# skew range of the control plane's version before upgrading further
```

---

## 12. Internal Flow

See Section 5 — production guardrails work by intercepting **specific risky moments**: object creation (ResourceQuota), voluntary eviction (PDB), and version transitions (skew policy) — each mechanism activates exactly at the point where an uncontrolled action could otherwise cause an outage or resource-starvation incident.

---

## 13. Real-World Examples

1. **Multi-tenant platform teams** use per-namespace ResourceQuotas to prevent one team's runaway workload from starving other teams sharing the same cluster.
2. **Critical payment services** define a strict PDB (`minAvailable: 90%`) to ensure node maintenance never drops available capacity below a safe threshold.
3. **Large-scale Kubernetes upgrades** (e.g., across a fleet of clusters) follow strict one-minor-version-at-a-time upgrade order to stay within the supported version skew policy.
4. **Multi-zone deployments** combine node anti-affinity (Chapter 20) with topology spread constraints to guarantee replicas survive a single zone outage.
5. **Cluster hardening audits** before a production launch typically check RBAC least-privilege (Chapter 21), Pod Security Standards (Chapter 21), resource quotas, and PDBs as a standard pre-launch checklist.

---

## 14. Best Practices

- Set **ResourceQuotas and LimitRanges** on every shared/multi-tenant namespace from day one, not reactively after an incident.
- Define a **PodDisruptionBudget** for every production-critical Deployment/StatefulSet, sized to your actual availability requirements.
- Always upgrade the **control plane before worker nodes**, one minor version at a time, verifying version skew compatibility at each step.
- Spread critical workloads across **multiple availability zones**, combined with anti-affinity/topology spread constraints, to survive zone-level failures.
- Regularly review and **right-size resource requests/limits** based on actual observed usage (Chapter 22 metrics) rather than guesswork.

---

## 15. Common Mistakes

- Running a shared cluster with no ResourceQuotas, allowing one team's misconfigured workload to starve every other tenant.
- Skipping PodDisruptionBudgets on critical services, allowing a routine node drain to accidentally take down all replicas simultaneously.
- Attempting to skip multiple minor versions in a single upgrade step, violating the version skew policy and risking undefined behavior.
- Deploying all replicas of a critical service into a single availability zone, creating an unnecessary single point of failure.
- Setting resource requests far higher than actual usage "just to be safe," wasting cluster capacity and increasing cost without real benefit.

---

## 16. Troubleshooting

| Symptom | Likely Cause | Debugging Commands | Fix |
|---|---|---|---|
| Pod creation rejected with a quota error | Namespace ResourceQuota exceeded | `kubectl describe resourcequota -n <ns>` | Reduce request, or increase quota if justified |
| Node drain hangs indefinitely | PDB prevents eviction below `minAvailable` | `kubectl get pdb -n <ns>` | Wait for replacement Pods to become healthy, or temporarily adjust the PDB if truly necessary |
| Upgrade fails or components behave unexpectedly | Version skew policy violated | `kubectl version --short` on all components | Upgrade incrementally, one minor version at a time, in the correct component order |
| Zone outage causes full service downtime | All replicas scheduled in a single zone | `kubectl get pods -o wide` (check node/zone distribution) | Add topology spread constraints/anti-affinity across zones |

---

## 17. Comparison Tables

| Mechanism | Protects Against |
|---|---|
| ResourceQuota | Namespace-level resource exhaustion by any single tenant |
| LimitRange | Missing/unbounded per-container resource specifications |
| PodDisruptionBudget | Excessive simultaneous voluntary disruption of a critical app |
| Version skew policy | Incompatible component versions during/after upgrades |
| Multi-zone HA | Single availability zone failure taking down an entire service |

---

## 18. Memory Tricks

- **"Apartment building house rules"** — quotas (utility caps), PDBs (renovation scheduling), version skew (safety inspections before structural changes).
- **"Control plane first, one minor version at a time."**
- **"PDB = minimum survivors during planned disruption."**

---

## 19. Interview Questions

**Easy:**
1. What is the purpose of a PodDisruptionBudget?
   *Expected answer:* A PodDisruptionBudget limits how many Pods of an application can be voluntarily disrupted at the same time (e.g., during a node drain), ensuring a minimum number or percentage of replicas remain available throughout the disruption.

**Medium:**
2. What is the difference between a ResourceQuota and a LimitRange?
   *Expected answer:* A ResourceQuota caps the total aggregate resource (and object count) consumption across an entire namespace. A LimitRange instead sets default, minimum, and maximum resource values for individual containers within a namespace, ensuring every container has sane resource specifications even if the developer doesn't explicitly set them.

**Hard:**
3. A platform team upgrades their Kubernetes control plane by three minor versions in a single step to "save time," and afterward several nodes' kubelets start reporting compatibility errors and workloads begin failing unpredictably. Explain what went wrong and how the upgrade should have been performed.
   *Expected answer:* Kubernetes's version skew policy only guarantees compatibility within a limited version range between components (e.g., kubelet can typically be a small number of minor versions behind the API server, but not further, and never ahead of it). Jumping three minor versions in the control plane at once pushes the node kubelets far outside this supported skew range, causing undefined and unpredictable compatibility failures. The correct approach is to upgrade **one minor version at a time**, starting with the control plane and then the nodes, fully validating cluster health at each step before proceeding to the next version — turning a single risky three-version jump into three smaller, well-tested, policy-compliant upgrade steps.

---

## 20. KCNA Practice Questions

**Q1.** What does a PodDisruptionBudget primarily protect against?
A. Involuntary node hardware failures
B. Excessive simultaneous voluntary disruptions, such as during a node drain
C. Network partition between zones
D. Unauthorized access to Secrets

**Correct answer: B**
*Explanation:* PDBs specifically govern voluntary disruptions (e.g., planned maintenance), not involuntary failures (A), network issues (C), or access control (D, which is RBAC's role — Chapter 21).

---

**Q2.** What is the purpose of a ResourceQuota?
A. To limit a single container's CPU usage
B. To cap the aggregate resource and object consumption across an entire namespace
C. To define which nodes a Pod can be scheduled on
D. To encrypt Secrets at rest

**Correct answer: B**
*Explanation:* ResourceQuota operates at the namespace level, capping total consumption. A describes per-container limits (Chapter 20), C describes node affinity (Chapter 20), and D describes etcd encryption (Chapter 21).

---

**Q3.** According to Kubernetes's version skew policy, what is the recommended order for cluster upgrades?
A. Upgrade worker nodes first, then the control plane
B. Upgrade the control plane first, then worker nodes, one minor version at a time
C. Upgrade all components simultaneously regardless of version gap
D. Upgrade etcd last, after all other components

**Correct answer: B**
*Explanation:* The safe, documented order is control-plane-first, then nodes, proceeding one minor version at a time to stay within supported version skew. A, C, and D describe unsafe or incorrect orderings.

---

**Q4.** Why might a production team spread replicas of a critical service across multiple availability zones?
A. To reduce the total number of replicas needed
B. To survive the failure of a single zone without full service downtime
C. To bypass the need for resource requests/limits
D. To avoid needing a Service object

**Correct answer: B**
*Explanation:* Multi-zone spread protects against a single zone's failure taking down the whole service. A, C, and D are unrelated or incorrect claims about multi-zone deployment's purpose.

---

**Q5.** What happens when a Pod creation request would exceed its namespace's ResourceQuota?
A. The Pod is created but throttled at runtime
B. The API server rejects the Pod creation request
C. The Pod is created in a different namespace automatically
D. The request succeeds, but a warning event is logged with no other effect

**Correct answer: B**
*Explanation:* ResourceQuota enforcement happens at admission time — the API server rejects requests that would exceed the quota, rather than allowing creation and throttling later. A, C, and D misdescribe actual quota enforcement behavior.

---

**Q6.** What is the purpose of a LimitRange, as distinct from a ResourceQuota?
A. It caps the total aggregate resource consumption of an entire namespace
B. It sets default, minimum, and maximum resource values for individual containers within a namespace
C. It limits how many nodes can join a cluster
D. It defines RBAC role bindings for a namespace

**Correct answer: B**
*Explanation:* LimitRange operates per-container, providing sane defaults/bounds, unlike ResourceQuota's namespace-wide aggregate cap (A). C and D describe unrelated cluster/RBAC concerns.

---

**Q7.** In the YAML deep dive's PodDisruptionBudget example, what does `minAvailable: 2` guarantee?
A. At least 2 nodes must always be schedulable
B. At least 2 `app: web` Pods must remain available at all times during voluntary disruptions
C. Exactly 2 replicas will ever be created
D. At least 2 namespaces must exist in the cluster

**Correct answer: B**
*Explanation:* `minAvailable: 2` on the PDB ensures a floor of 2 available matching Pods during voluntary disruptions like node drains. A, C, and D misapply the field to unrelated scopes.

---

**Q8.** Which Kubernetes API component checks a PodDisruptionBudget before evicting a Pod during a node drain?
A. The scheduler
B. The eviction API
C. CoreDNS
D. The CNI plugin

**Correct answer: B**
*Explanation:* The eviction API consults the relevant PDB before allowing a voluntary Pod eviction, refusing it if it would breach `minAvailable`. A, C, and D play no role in disruption-budget enforcement.

---

**Q9.** Per Kubernetes's version skew policy, which relationship between kubelet and kube-apiserver versions is supported?
A. kubelet may be a limited number of minor versions behind the API server, but never newer than it
B. kubelet must always be newer than the API server
C. kubelet and API server versions are always required to match exactly
D. There is no supported version relationship; any combination works

**Correct answer: A**
*Explanation:* The documented skew policy allows kubelet to lag the API server by a small number of minor versions, but never to be ahead. B, C, and D all misstate the actual supported skew rules.

---

**Q10.** What analogy does this chapter use to explain why production clusters need extra guardrails?
A. A single-family home needing no rules at all
B. An apartment building's house rules — utility caps, renovation scheduling, safety inspections
C. A racetrack with no speed limits
D. A museum with unrestricted access

**Correct answer: B**
*Explanation:* Section 3's analogy compares multi-tenant cluster guardrails to an apartment building's house rules (quotas, PDBs, upgrade policies). A, C, and D are not analogies used in this chapter.

---

**Q11.** Which of the following is listed as a common mistake in this chapter?
A. Defining a PodDisruptionBudget for every critical Deployment
B. Skipping PodDisruptionBudgets on critical services, allowing a routine node drain to take down all replicas simultaneously
C. Setting ResourceQuotas on every shared namespace
D. Upgrading one minor version at a time

**Correct answer: B**
*Explanation:* Section 15 explicitly lists skipping PDBs on critical services as a common mistake. A, C, and D are actually recommended best practices (Section 14), not mistakes.

---

**Q12.** A team wants their critical payment service to tolerate node maintenance without dropping below 90% capacity. Which mechanism, as described in this chapter's real-world examples, addresses this directly?
A. A LimitRange with a high maximum
B. A PodDisruptionBudget with `minAvailable: 90%`
C. A ResourceQuota capping pod count
D. Upgrading the API server

**Correct answer: B**
*Explanation:* Section 13 describes exactly this pattern — a strict PDB with `minAvailable: 90%` for critical payment services. A, C, and D don't address voluntary-disruption availability guarantees.

---

**Q13.** What is a "voluntary disruption" in the context of PodDisruptionBudgets?
A. A hardware failure that crashes a node unexpectedly
B. A deliberately-initiated disruption, such as a node drain or Deployment update
C. A network partition between availability zones
D. An OOMKilled event caused by exceeding memory limits

**Correct answer: B**
*Explanation:* Voluntary disruptions are deliberate actions (node drains, rolling updates) as opposed to involuntary failures like crashes or OOM kills. A, C, and D describe involuntary failure scenarios instead.

---

**Q14.** Per this chapter's troubleshooting table, what is the likely cause when a node drain hangs indefinitely?
A. The namespace's ResourceQuota has been exceeded
B. A PodDisruptionBudget is preventing eviction below its `minAvailable` threshold
C. The API server is down
D. The node has too many taints

**Correct answer: B**
*Explanation:* A PDB blocking eviction below its configured minimum is the documented cause of a hanging drain; the fix is to wait for replacement Pods or adjust the PDB if truly necessary. A, C, and D are unrelated symptoms/causes.

---

**Q15.** Why does this chapter recommend regularly right-sizing resource requests/limits based on observed usage rather than guesswork?
A. To intentionally waste cluster capacity as a safety margin
B. To avoid wasting cluster capacity and unnecessary cost while still meeting real workload needs
C. Because Kubernetes requires exact requests to equal limits
D. Because ResourceQuotas are recalculated automatically otherwise

**Correct answer: B**
*Explanation:* Section 14 recommends right-sizing based on actual observed usage (Chapter 22 metrics) to avoid overprovisioning waste while still meeting real needs. A contradicts the goal, and C/D are fabricated mechanics.

---

**Q16.** Which chapter's concepts does this chapter combine with multi-zone spread to guarantee replicas survive a zone outage?
A. Chapter 20 (Scheduling) — anti-affinity/topology spread constraints
B. Chapter 05 (Container Runtimes)
C. Chapter 08 (GitLab CI)
D. Chapter 03 (Git and Version Control)

**Correct answer: A**
*Explanation:* Section 13 and Section 4.4 describe combining multi-zone deployment with Pod anti-affinity/topology spread constraints from Chapter 20. B, C, and D are unrelated chapters.

---

**Q17.** What does this chapter's memory trick "Control plane first, one minor version at a time" summarize?
A. The order and pace for safe Kubernetes cluster upgrades
B. The order in which ResourceQuotas should be applied
C. The scheduling order for Pod eviction during a drain
D. The order in which namespaces should be created

**Correct answer: A**
*Explanation:* This memory trick captures the safe upgrade order (control plane before nodes) and pace (one minor version at a time) from the version skew policy. B, C, and D are unrelated processes.

---

**Q18.** According to Real-world Examples, what should a cluster-hardening audit before a production launch typically check?
A. Only the number of nodes in the cluster
B. RBAC least-privilege, Pod Security Standards, resource quotas, and PDBs
C. Only the container image registry URL
D. Only the CNCF maturity level of installed tools

**Correct answer: B**
*Explanation:* Section 13 lists RBAC least-privilege and Pod Security Standards (Chapter 21) alongside resource quotas and PDBs as a standard pre-launch hardening checklist. A, C, and D are incomplete or irrelevant checks.

---

**Q19.** A team attempts to skip multiple Kubernetes minor versions in a single upgrade step. What risk does this chapter say this creates?
A. No risk — Kubernetes supports arbitrary version jumps
B. Violating the version skew policy, risking undefined and unpredictable behavior
C. Automatic rollback to the previous version
D. Immediate cluster-wide data loss in etcd

**Correct answer: B**
*Explanation:* Section 15 and the Hard interview question both describe skipping versions as violating the skew policy, risking undefined compatibility failures. A, C, and D misstate the actual consequence.

---

**Q20.** Which combination of mechanisms from this chapter would best protect a critical, multi-tenant production Deployment against both resource starvation and a disruptive node drain?
A. ResourceQuota only, with no PDB
B. A ResourceQuota/LimitRange for fair resource allocation, combined with a PodDisruptionBudget for the Deployment
C. Only upgrading Kubernetes more frequently
D. Only spreading replicas across zones, with no quotas or PDB

**Correct answer: B**
*Explanation:* Resource quotas/limit ranges address multi-tenant starvation while a PDB addresses disruption safety during drains — together covering both risks described in this chapter. A and D each address only one risk, and C is unrelated to either concern.

---

## 21. Chapter Summary (One-Page Revision Sheet)

- **ResourceQuotas** cap aggregate namespace resource/object consumption; **LimitRanges** set sane per-container defaults — both are essential in multi-tenant clusters.
- **PodDisruptionBudgets (PDBs)** guarantee a minimum number/percentage of Pods remain available during voluntary disruptions like node drains, checked by the eviction API before allowing eviction.
- Kubernetes's **version skew policy** requires upgrading the **control plane before nodes**, one minor version at a time, to stay within supported compatibility ranges.
- **Multi-zone/multi-region HA**, combined with anti-affinity/topology spread (Chapter 20), protects against single-zone failures taking down an entire service.
- Together, these mechanisms turn hard-won early Kubernetes operational lessons into enforceable, declarative production guardrails.

---

### Chapter Completion Checklist

1. **Topics covered:** ResourceQuotas, LimitRanges, PodDisruptionBudgets, version skew policy and upgrade order, multi-zone HA patterns.
2. **KCNA objectives completed:** Cloud Native Architecture — Production Best Practices.
3. **Remaining objectives:** Exam Preparation — study strategy, exam format, time management (Chapter 28).
4. **Suggested revision checklist:** Explain ResourceQuota vs LimitRange from memory; explain PDB's role during node drains; explain the safe cluster upgrade order.
5. **Suggested hands-on exercises:** Complete Lab 2 (apply a PDB and attempt a node drain) — the clearest demonstration of PDB-enforced availability guarantees.
6. **Related chapters:** Previous: [26-CNCF-Landscape](../26-CNCF-Landscape/README.md). Next: [28-Exam-Preparation](../28-Exam-Preparation/README.md) — KCNA exam format, strategy, and study planning.
