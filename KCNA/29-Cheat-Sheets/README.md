# 29 — Cheat Sheets

## 1. Learning Objectives

By the end of this chapter you will be able to:

- Use a single condensed reference for every major KCNA domain without re-reading full chapters.
- Quickly recall key `kubectl` commands, object kinds, and comparison facts during final review.
- Identify, at a glance, which chapter to revisit for deeper explanation of any topic.

**KCNA objectives covered:** Meta-chapter — condensed reference across all domains (Chapters 01-27).

---

## 2. Historical Background

Cheat sheets emerged from a simple operational reality: even experts who deeply understand a system can't hold every command flag, object field, or comparison table in working memory. Kubernetes' own documentation popularized single-page `kubectl` cheat sheets early on precisely because the CLI surface area grew too large to memorize. This chapter distills the entire guide into one compact, non-narrative reference for rapid final-review scanning.

---

## 3. Motivation: Why Have a Dedicated Cheat-Sheet Chapter?

**Analogy — The Pilot's Pre-Flight Checklist:**
A pilot who deeply understands aerodynamics still uses a physical checklist before takeoff — not because they don't know the material, but because a compact reference eliminates reliance on memory under time pressure. This chapter is that checklist: not for first-time learning (use Chapters 01-27 for that), but for rapid recall in the final days before the exam.

---

## 4. Core Concepts — Condensed Domain Reference

### 4.1 Kubernetes Architecture (Ch. 06-08)

| Component | Location | Role |
|---|---|---|
| kube-apiserver | Control plane | Front door for all cluster operations; validates and persists to etcd |
| etcd | Control plane | Distributed key-value store; single source of truth for cluster state |
| kube-scheduler | Control plane | Assigns unscheduled Pods to nodes |
| kube-controller-manager | Control plane | Runs reconciliation loops (Deployment, Node, etc. controllers) |
| cloud-controller-manager | Control plane | Integrates with cloud provider APIs (LBs, volumes, nodes) |
| kubelet | Worker node | Ensures containers described in PodSpecs are running and healthy |
| kube-proxy | Worker node | Implements Service networking rules on each node |
| Container runtime | Worker node | Actually runs containers (containerd, CRI-O) via CRI |

### 4.2 Core Workload Objects (Ch. 09-15)

| Object | Use Case | Key Trait |
|---|---|---|
| Pod | Smallest deployable unit | One or more containers sharing network/storage |
| ReplicaSet | Maintain N identical Pod replicas | Rarely used directly; managed by Deployments |
| Deployment | Stateless apps | Rolling updates, rollback, declarative desired state |
| DaemonSet | One Pod per (matching) node | Node-level agents (log shippers, CNI plugins) |
| StatefulSet | Stateful apps | Stable network identity + stable storage per replica |
| Job | Run-to-completion task | Guarantees successful completion N times |
| CronJob | Scheduled Job | Runs Jobs on a cron schedule |

### 4.3 Networking (Ch. 16-18)

| Object/Concept | Purpose |
|---|---|
| Service (ClusterIP) | Stable internal virtual IP for a set of Pods |
| Service (NodePort) | Exposes a Service on a static port on every node |
| Service (LoadBalancer) | Provisions an external cloud load balancer |
| Ingress | L7 HTTP(S) routing rules to Services |
| Gateway API | Newer, more expressive successor to Ingress |
| NetworkPolicy | L3/L4 firewall rules between Pods |
| CNI | Standard plugin interface for Pod networking |
| CoreDNS | Cluster-internal DNS resolution for Services/Pods |

### 4.4 Storage (Ch. 19)

| Object | Role |
|---|---|
| Volume | Pod-scoped storage, lifecycle tied to Pod |
| PersistentVolume (PV) | Cluster-scoped piece of storage, provisioned or dynamic |
| PersistentVolumeClaim (PVC) | Namespace-scoped request for storage matching a PV |
| StorageClass | Template for dynamic PV provisioning |
| CSI | Standard plugin interface for storage drivers |

### 4.5 Scheduling (Ch. 20)

| Concept | Effect |
|---|---|
| Node Affinity | Attracts Pods toward matching nodes |
| Pod Affinity/Anti-Affinity | Attracts/repels Pods relative to other Pods |
| Taints (on nodes) | Repel Pods unless tolerated |
| Tolerations (on Pods) | Allow scheduling onto tainted nodes |
| Resource requests | Used by scheduler for placement decisions |
| Resource limits | Enforced at runtime; can trigger throttling/OOMKill |

### 4.6 Security (Ch. 21)

| Concept | Role |
|---|---|
| RBAC (Role/RoleBinding) | Namespace-scoped permission grants |
| RBAC (ClusterRole/ClusterRoleBinding) | Cluster-scoped permission grants |
| ServiceAccount | Identity for Pods to authenticate to the API server |
| Secret | Base64-encoded sensitive data (not encrypted by default at rest) |
| Pod Security Standards | Baseline/Restricted/Privileged Pod security profiles |
| NetworkPolicy | Also a security boundary (traffic isolation) |

### 4.7 Observability, Mesh, GitOps, Serverless (Ch. 22-25)

| Domain | Key Tool/Concept |
|---|---|
| Metrics | Prometheus (pull-based `/metrics` scraping) |
| Logs | Centralized logging (e.g., EFK/Loki stack) |
| Traces | OpenTelemetry, spans |
| Service Mesh | Istio/Linkerd, sidecar proxies, mTLS |
| GitOps | ArgoCD/Flux, reconciliation loop, Git as source of truth |
| Serverless | Knative, scale-to-zero, cold start |

### 4.8 CNCF Landscape (Ch. 26)

| Maturity Level | Meaning |
|---|---|
| Sandbox | Early-stage, experimental |
| Incubating | Demonstrated adoption |
| Graduated | Proven, most mature governance |

---

## 5. Internal Working

Not applicable in the traditional sense — this chapter has no single mechanism of its own; it is a condensed index into the mechanisms already explained in Chapters 06-27.

---

## 6. Architecture

```
┌───────────────────────────────────────────┐
│                Cheat Sheet Navigation                 │
│  Architecture → §4.1   Workloads → §4.2       │
│  Networking → §4.3     Storage → §4.4          │
│  Scheduling → §4.5     Security → §4.6         │
│  Observability/Mesh/GitOps/Serverless → §4.7   │
│  CNCF Landscape → §4.8                          │
└───────────────────────────────────────────┘
```

---

## 7. Component Breakdown

Not applicable as a distinct section — see Section 4's per-domain tables, which double as this chapter's component breakdown.

---

## 8. Important Terminology — Quick-Reference Glossary

| Term | One-Line Definition |
|---|---|
| Reconciliation loop | Controller pattern: observe actual state, compare to desired state, act to correct drift |
| Label selector | Mechanism for objects (Services, Deployments) to target Pods by label match |
| Admission control | API server stage that can mutate/validate requests before persistence |
| Idempotency | Property where repeating an operation has the same effect as doing it once |
| Drift | Divergence between actual cluster state and declared/desired state |

---

## 9. YAML Deep Dive — Minimal Skeletons

```yaml
# Deployment skeleton
apiVersion: apps/v1
kind: Deployment
metadata: {name: app}
spec:
  replicas: 3
  selector: {matchLabels: {app: app}}
  template:
    metadata: {labels: {app: app}}
    spec:
      containers:
      - name: app
        image: app:1.0
        resources:
          requests: {cpu: "100m", memory: "128Mi"}
          limits: {cpu: "200m", memory: "256Mi"}
---
# Service skeleton
apiVersion: v1
kind: Service
metadata: {name: app-svc}
spec:
  selector: {app: app}
  ports: [{port: 80, targetPort: 8080}]
---
# Ingress skeleton
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata: {name: app-ing}
spec:
  rules:
  - host: app.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend: {service: {name: app-svc, port: {number: 80}}}
```

---

## 10. kubectl Commands — Fast Reference

| Task | Command |
|---|---|
| List Pods (all namespaces) | `kubectl get pods -A` |
| Describe object | `kubectl describe <kind> <name>` |
| Apply manifest | `kubectl apply -f file.yaml` |
| Delete object | `kubectl delete <kind> <name>` |
| View logs | `kubectl logs <pod> [-c container]` |
| Exec into container | `kubectl exec -it <pod> -- sh` |
| Port-forward | `kubectl port-forward <pod> 8080:80` |
| Scale a Deployment | `kubectl scale deployment/<name> --replicas=N` |
| Rollout status | `kubectl rollout status deployment/<name>` |
| Rollout undo | `kubectl rollout undo deployment/<name>` |
| Drain a node | `kubectl drain <node> --ignore-daemonsets` |
| Check contexts | `kubectl config get-contexts` |
| Check RBAC permission | `kubectl auth can-i <verb> <resource>` |

---

## 11. Hands-on Examples

**Lab 1 — Speed drill:** Set a 10-minute timer and, from memory, write out the skeleton YAML for a Deployment, Service, and Ingress (Section 9), then check against this chapter.

**Lab 2 — Command recall drill:** Cover the right column of Section 10's table and recall each `kubectl` command from the task description alone.

**Lab 3 — Domain-mapping drill:** Given a random KCNA-style question, identify which of Section 4's subsections it maps to within 10 seconds.

---

## 12. Internal Flow

Not applicable — this chapter is a static reference, not a process with a flow of its own.

---

## 13. Real-World Examples

1. A candidate reviews Section 4.1's architecture table the morning of the exam instead of re-reading all of Chapter 06.
2. A candidate uses Section 10's kubectl table to quickly settle a doubt about `rollout undo` syntax during practice questions.
3. A candidate uses Section 9's YAML skeletons as a starting template when writing practice manifests from scratch.
4. A team lead prints Section 4 as an onboarding quick-reference for new engineers before they read the full guide.
5. A candidate uses Section 8's glossary to refresh precise definitions of "reconciliation loop" and "drift" right before the exam.

---

## 14. Best Practices

- Use this chapter **only for review**, not first-time learning — full chapters provide necessary context this reference omits.
- Time yourself on recall drills (Section 11) to build exam-day speed, not just accuracy.
- Revisit this chapter multiple times in the final week rather than once — repetition strengthens recall more than a single pass.

---

## 15. Common Mistakes

- Trying to learn a new topic from this chapter alone without ever having read the full corresponding chapter.
- Treating cheat-sheet review as a substitute for practice questions and mock exams rather than a complement to them.
- Memorizing tables without understanding *why* (e.g., memorizing that Deployments use ReplicaSets without understanding the reconciliation loop from Chapter 06).

---

## 16. Troubleshooting

| Symptom | Fix |
|---|---|
| A cheat-sheet term feels unfamiliar | Jump to the referenced chapter's Section 8 (Terminology) for the full explanation |
| Command recall is slow | Repeat Lab 2 daily during the final week |
| Confusing two similar objects (e.g., PV vs PVC) | Re-read Chapter 19's comparison table, then retest with Section 4.4 |

---

## 17. Comparison Tables

See Section 4 throughout — every subsection is itself a condensed comparison table by design.

---

## 18. Memory Tricks

- **"Control plane decides, worker nodes do."**
- **"Deployment → ReplicaSet → Pod"** (ownership chain).
- **"PV is the supply, PVC is the demand."**
- **"Taint repels, toleration permits."**

---

## 19. Interview Questions

**Easy:**
1. What is the purpose of a cheat sheet in exam preparation?
   *Expected answer:* A cheat sheet condenses previously-learned material into a fast, scannable reference for final review and recall practice — it supports retention and speed, not first-time learning.

**Medium:**
2. Why should cheat sheets be used only after reading the full chapters, not instead of them?
   *Expected answer:* Cheat sheets strip away the motivation, internal working, and context that make facts memorable and correctly understood; using them for first-time learning risks shallow, easily-confused knowledge (e.g., memorizing that Deployments manage ReplicaSets without understanding the reconciliation loop that makes this true).

**Hard:**
3. A candidate has memorized every table in this chapter perfectly but still struggles with KCNA practice questions that describe real-world scenarios. What is the likely gap, and how should they address it?
   *Expected answer:* Memorizing condensed facts builds recall speed but not applied understanding — KCNA scenario questions require reasoning about *why* a mechanism behaves a certain way (e.g., why a Service continues routing to a Pod that fails its liveness probe differently than one failing readiness). The candidate should return to the full chapters' Motivation and Internal Working sections, and practice with scenario-based Practice Questions (Chapter 31) and Mock Exams (Chapter 32) rather than relying on table memorization alone.

---

## 20. KCNA Practice Questions

**Q1.** What is the primary purpose of this Cheat Sheets chapter?
A. To replace the need to read Chapters 01-27
B. To provide a condensed, fast-reference summary for final review
C. To introduce entirely new KCNA content not covered elsewhere
D. To serve as the official CNCF exam blueprint

**Correct answer: B**
*Explanation:* This chapter condenses prior material for review speed; it is not a substitute for full learning (A), does not introduce new content (C), and is not an official CNCF document (D).

---

**Q2.** According to the architecture cheat sheet, which component is responsible for assigning unscheduled Pods to nodes?
A. kubelet
B. kube-proxy
C. kube-scheduler
D. etcd

**Correct answer: C**
*Explanation:* kube-scheduler assigns Pods to nodes. kubelet (A) runs containers on an assigned node, kube-proxy (B) handles Service networking rules, and etcd (D) stores cluster state.

---

**Q3.** Per the storage cheat sheet, what is the relationship between a PersistentVolumeClaim (PVC) and a PersistentVolume (PV)?
A. A PVC is cluster-scoped; a PV is namespace-scoped
B. A PVC is a namespace-scoped request for storage matching a PV
C. A PV cannot exist without a StorageClass
D. A PVC directly mounts host storage, bypassing PVs

**Correct answer: B**
*Explanation:* The PVC is the namespace-scoped request that binds to a matching PV, per Chapter 19. A reverses the actual scoping; C and D misstate the relationship.

---

**Q4.** Per the security cheat sheet, what is the scope difference between a Role and a ClusterRole?
A. Role is namespace-scoped; ClusterRole is cluster-scoped
B. Role and ClusterRole have identical scope
C. Role is cluster-scoped; ClusterRole is namespace-scoped
D. Neither has any defined scope

**Correct answer: A**
*Explanation:* Roles grant namespace-scoped permissions, while ClusterRoles grant cluster-wide permissions (Chapter 21). B, C, and D misstate this distinction.

---

**Q5.** According to the CNCF landscape cheat sheet, which maturity level indicates the most proven governance and adoption?
A. Sandbox
B. Incubating
C. Graduated
D. Archived

**Correct answer: C**
*Explanation:* Graduated is the highest CNCF maturity level, indicating proven adoption and the strictest governance (Chapter 26). Sandbox (A) is earliest-stage, Incubating (B) is intermediate, and "Archived" (D) is not one of the three maturity levels.

---

**Q6.** Per the workload objects cheat sheet (Section 4.2), which object is rarely used directly and is instead typically managed by a Deployment?
A. StatefulSet
B. ReplicaSet
C. DaemonSet
D. CronJob

**Correct answer: B**
*Explanation:* A ReplicaSet is normally created and managed by a Deployment rather than authored directly (Chapter 09). StatefulSet (A), DaemonSet (C), and CronJob (D) are each used directly for their own distinct use cases.

---

**Q7.** According to the networking cheat sheet (Section 4.3), which Service type provisions an external cloud load balancer?
A. ClusterIP
B. NodePort
C. LoadBalancer
D. ExternalName

**Correct answer: C**
*Explanation:* A LoadBalancer Service provisions a cloud provider load balancer (Chapter 16). ClusterIP (A) is internal-only, NodePort (B) exposes a static port on every node without provisioning a cloud LB, and ExternalName (D) is not listed in this cheat sheet's Service types.

---

**Q8.** Per the YAML skeleton in Section 9, which field on a container specifies the enforced upper bound on CPU/memory usage, as opposed to the value used for scheduling decisions?
A. `requests`
B. `limits`
C. `selector`
D. `matchLabels`

**Correct answer: B**
*Explanation:* `limits` is enforced at runtime as the upper bound; `requests` (A) is what the scheduler uses for placement, per Section 4.5 and Chapter 20. `selector` (C) and `matchLabels` (D) are unrelated to resource sizing.

---

**Q9.** Which `kubectl` command from Section 10's fast-reference table checks whether the current user is permitted to perform a given verb on a resource?
A. `kubectl config get-contexts`
B. `kubectl auth can-i <verb> <resource>`
C. `kubectl describe <kind> <name>`
D. `kubectl rollout status deployment/<name>`

**Correct answer: B**
*Explanation:* `kubectl auth can-i` checks RBAC permissions for the current identity. `get-contexts` (A) lists kubeconfig contexts, `describe` (C) shows object details, and `rollout status` (D) reports Deployment rollout progress.

---

**Q10.** Per the glossary in Section 8, what is "drift" in Kubernetes terminology?
A. The delay between scheduling and container start
B. Divergence between actual cluster state and declared/desired state
C. The network latency between two Pods on different nodes
D. The version skew between kubelet and kube-apiserver

**Correct answer: B**
*Explanation:* Drift describes actual state diverging from desired state, which a reconciliation loop corrects. A, C, and D describe unrelated concepts not defined as "drift" in this glossary.

---

**Q11.** According to Section 4.7, which tool is associated with implementing mutual TLS (mTLS) between services via sidecar proxies?
A. Prometheus
B. ArgoCD
C. Service Mesh (Istio/Linkerd)
D. Knative

**Correct answer: C**
*Explanation:* Service mesh tools like Istio/Linkerd inject sidecar proxies that can enforce mTLS between services (Chapter 24). Prometheus (A) is a metrics tool, ArgoCD (B) is a GitOps tool, and Knative (D) is a serverless platform.

---

**Q12.** Per Section 4.7, which principle underlies GitOps tools such as ArgoCD or Flux?
A. Git is treated as the source of truth, with continuous reconciliation against cluster state
B. Manual `kubectl apply` commands issued by operators against a shared cluster
C. Container images are treated as the sole source of truth
D. Metrics scraping determines the desired cluster state

**Correct answer: A**
*Explanation:* GitOps tools continuously reconcile live cluster state against a Git repository treated as the source of truth (Chapter 24). B describes a non-GitOps manual workflow; C and D misdescribe GitOps's actual mechanism.

---

**Q13.** Which memory trick from Section 18 correctly encodes the ownership chain for a typical stateless workload?
A. "PV is the supply, PVC is the demand."
B. "Taint repels, toleration permits."
C. "Deployment → ReplicaSet → Pod"
D. "Control plane decides, worker nodes do."

**Correct answer: C**
*Explanation:* "Deployment → ReplicaSet → Pod" encodes the ownership/management chain for stateless workloads (Chapter 09). A concerns storage, B concerns scheduling, and D concerns the control-plane/node split — all correct facts, but not the ownership chain.

---

**Q14.** Per Section 4.4's storage table, what is the role of a StorageClass?
A. A namespace-scoped request for storage
B. A template for dynamic PersistentVolume provisioning
C. A plugin interface standard for storage drivers
D. A cluster-scoped, already-provisioned piece of storage

**Correct answer: B**
*Explanation:* A StorageClass defines parameters used to dynamically provision PersistentVolumes on demand (Chapter 19). A describes a PVC, C describes CSI, and D describes a PV.

---

**Q15.** According to Section 4.6's security table, what does a NetworkPolicy provide, beyond pure network configuration?
A. A cluster-scoped RBAC permission grant
B. Base64 encoding of sensitive data
C. A security boundary via traffic isolation between Pods
D. A Pod-level security profile such as Baseline or Restricted

**Correct answer: C**
*Explanation:* NetworkPolicy is listed under Section 4.6 specifically because, beyond routing, it also acts as a security boundary by isolating traffic between Pods (Chapter 21). A describes ClusterRole/ClusterRoleBinding, B describes Secrets, and D describes Pod Security Standards.

---

**Q16.** Per Section 11's Lab 3 (Domain-mapping drill), what skill is this exercise specifically designed to build?
A. Writing YAML from memory under a time limit
B. Recalling exact `kubectl` command syntax
C. Quickly identifying which Section 4 subsection a random KCNA-style question maps to
D. Memorizing the CNCF maturity levels in order

**Correct answer: C**
*Explanation:* Lab 3 is explicitly a domain-mapping drill for rapid topic identification. A describes Lab 1, B describes Lab 2, and D is not one of the three labs in Section 11.

---

**Q17.** Per Section 15 (Common Mistakes), what is the risk of memorizing this chapter's tables without understanding the underlying "why"?
A. It causes YAML syntax errors during the exam
B. It produces shallow knowledge, such as memorizing that Deployments use ReplicaSets without understanding the reconciliation loop
C. It is explicitly forbidden by the CNCF exam terms
D. It slows down `kubectl` command execution

**Correct answer: B**
*Explanation:* Section 15 warns that table memorization without conceptual grounding produces shallow, easily-confused knowledge. A, C, and D are not mistakes this section identifies.

---

**Q18.** According to Section 16 (Troubleshooting), what should a candidate do if a cheat-sheet term feels unfamiliar during review?
A. Skip it, since cheat-sheet terms are not exam-relevant
B. Jump to the referenced chapter's Terminology section (Section 8) for the full explanation
C. Guess based on the term's similarity to another term
D. Wait until after the exam to look it up

**Correct answer: B**
*Explanation:* Section 16 directs candidates back to the source chapter's own Section 8 (Terminology) for full context. A, C, and D contradict the chapter's explicit review guidance.

---

**Q19.** Per Section 4.1, which control-plane component integrates with a cloud provider's APIs to manage load balancers, volumes, and nodes?
A. kube-controller-manager
B. cloud-controller-manager
C. kube-apiserver
D. etcd

**Correct answer: B**
*Explanation:* The cloud-controller-manager specifically handles cloud-provider integrations such as LBs, volumes, and nodes (Chapter 07). kube-controller-manager (A) runs generic reconciliation loops, kube-apiserver (C) is the front door for API requests, and etcd (D) stores cluster state.

---

**Q20.** Per this chapter's own Chapter Completion Checklist, which chapters remain to complete the KCNA exam-preparation sequence after Cheat Sheets?
A. Only Mock Exams (Chapter 32)
B. Flashcards, Practice Questions, Mock Exams, and Interview Questions compilation (Chapters 30-33)
C. Only re-reading Chapters 01-27 again
D. Nothing; Cheat Sheets is the final chapter

**Correct answer: B**
*Explanation:* The checklist explicitly lists Flashcards (30), Practice Questions (31), Mock Exams (32), and Interview Questions (33) as remaining objectives. A and D understate the remaining scope, and C contradicts the chapter's own guidance to use this chapter for review, not re-reading.

---

## 21. Chapter Summary (One-Page Revision Sheet)

- This chapter condenses **Chapters 06-27** into per-domain quick-reference tables: architecture, workloads, networking, storage, scheduling, security, observability/mesh/GitOps/serverless, and CNCF landscape.
- Includes minimal **YAML skeletons** for Deployment/Service/Ingress and a fast **kubectl command table** for exam-day recall.
- Intended for **review only** — always pair with the full chapters for context, and with Practice Questions/Mock Exams for applied reasoning practice.

---

### Chapter Completion Checklist

1. **Topics covered:** Condensed cross-domain reference tables, YAML skeletons, kubectl fast reference.
2. **KCNA objectives completed:** Meta-chapter spanning all domains for review purposes.
3. **Remaining objectives:** Flashcards (Chapter 30), Practice Questions (Chapter 31), Mock Exams (Chapter 32), Interview Questions compilation (Chapter 33).
4. **Suggested revision checklist:** Complete all three recall drills in Section 11 with a timer.
5. **Suggested hands-on exercises:** Repeat Lab 1 (YAML skeleton recall) until all three skeletons can be written correctly from memory in under 5 minutes.
6. **Related chapters:** Previous: [28-Exam-Preparation](../28-Exam-Preparation/README.md). Next: [30-Flashcards](../30-Flashcards/README.md) — active-recall flashcard sets per domain.
