# 31 — Practice Questions

## 1. Learning Objectives

By the end of this chapter you will be able to:

- Apply cross-domain Kubernetes and cloud native knowledge to scenario-style multiple-choice questions.
- Distinguish subtly-wrong distractor answers from the genuinely correct one, the way the real KCNA exam does.
- Identify personal weak domains from question-set performance ahead of full Mock Exams (Chapter 32).

**KCNA objectives covered:** Meta-chapter — scenario-based practice across all domains (Chapters 01-27).

---

## 2. Historical Background

Certification bodies, including the Linux Foundation/CNCF, write exam questions as **applied scenarios** rather than raw definition lookups, because real-world competence means recognizing a concept in context, not just reciting its definition. This chapter's question bank is deliberately written in that same scenario style — building the specific skill of mapping a described situation back to the correct underlying concept, distinct from the isolated recall practiced in Chapter 30's flashcards.

---

## 3. Motivation: Why a Separate Practice-Question Chapter, Beyond Flashcards?

**Analogy — Flight Simulator vs. Flashcard Study of Aircraft Parts:**
Knowing that "the yoke controls pitch" (a flashcard fact) is different from correctly pulling back on the yoke during a simulated engine-out scenario at the right moment. Flashcards (Chapter 30) build fact recall; this chapter is the flight simulator — applying that recalled knowledge inside realistic, scenario-driven questions that mirror the actual KCNA exam's style.

---

## 4. Core Concepts: How This Chapter Is Organized

- Questions are grouped by domain, matching Chapter 29/30's structure, then a **mixed-domain set** at the end that mirrors real exam randomization.
- Every question includes the correct answer plus an explanation of why each distractor is wrong — not just why the correct answer is right.
- Aim to answer each question in **under 90 seconds**, matching real exam pacing (Chapter 28, Section 6).

---

## 5-12. (Not Applicable Sections)

Sections 5 (Internal Working), 6 (Architecture), 7 (Component Breakdown), 9 (YAML Deep Dive beyond what's embedded in questions), 10 (kubectl beyond what's embedded in questions), and 12 (Internal Flow) are not applicable as standalone sections in this chapter — this chapter's substance is the question bank itself (Section 13 area, presented here as Sections 19-20 per the template).

---

## 13-18. Practice Question Bank

### Set A — Kubernetes Architecture & Control Plane (Ch. 06-08)

**A1.** A cluster administrator notices that when the kube-apiserver is temporarily unreachable, existing Pods keep running normally on their nodes, but no new Pods can be scheduled. What does this best demonstrate?
A. etcd has failed and lost all cluster state
B. The control plane and data plane are decoupled — kubelets keep existing Pods running independently of API server availability
C. Worker nodes cannot function without the API server
D. kube-scheduler has crashed permanently

**Correct answer: B**
*Explanation:* Kubelets manage already-assigned Pods locally and don't need constant API server contact to keep them running; only *new* scheduling/API operations require the API server. A assumes an unrelated failure; C contradicts the observed behavior; D is unsupported by the scenario.

**A2.** An engineer wants to change the desired replica count of a running Deployment permanently. Which component ultimately persists this new desired state?
A. kube-scheduler
B. kubelet
C. etcd (via the kube-apiserver)
D. kube-proxy

**Correct answer: C**
*Explanation:* All persistent cluster state, including desired Deployment specs, is stored in etcd, written through the API server. A, B, and D are not state stores.

---

### Set B — Workload Objects (Ch. 09-15)

**B1.** A team needs a workload that runs exactly one Pod on every node in the cluster, including nodes added later, for a log-shipping agent. Which object should they use?
A. Deployment
B. StatefulSet
C. DaemonSet
D. Job

**Correct answer: C**
*Explanation:* DaemonSet guarantees one Pod per matching node automatically, including future nodes. Deployment (A) doesn't tie replica count to node count; StatefulSet (B) is for stable-identity stateful apps; Job (D) runs to completion, not continuously.

**B2.** A batch reporting task must run once per night and must be retried automatically if it fails, but should not run continuously. What combination of objects fits best?
A. Deployment with replicas: 1
B. CronJob (which creates a Job on each scheduled run)
C. DaemonSet
D. StatefulSet

**Correct answer: B**
*Explanation:* CronJob triggers a Job on a schedule, and Jobs natively retry until success or a backoff limit. A deployment would restart the container continuously, which is wrong for a scheduled batch task; C and D solve unrelated problems.

---

### Set C — Networking (Ch. 16-18)

**C1.** A Service's Pods are healthy per `kubectl get pods`, but external users report intermittent connection failures reaching them via an Ingress. Which layer should be investigated first?
A. The container runtime
B. The Ingress controller and its routing rules
C. etcd
D. The kube-scheduler

**Correct answer: B**
*Explanation:* Since Pods report healthy, the issue is likely in L7 routing — Ingress controller configuration, backend registration, or TLS termination. A, C, and D are unrelated to HTTP-layer routing problems.

**C2.** A NetworkPolicy is applied to a namespace allowing ingress only from Pods labeled `role: frontend`. A Pod labeled `role: backend` in the same namespace suddenly cannot reach a Pod in that namespace anymore. What is the most likely explanation?
A. The NetworkPolicy's default-deny behavior now blocks previously-allowed traffic that doesn't match the explicit allow rule
B. NetworkPolicies only affect traffic leaving the cluster
C. The Service object was deleted
D. CoreDNS is down

**Correct answer: A**
*Explanation:* Once any NetworkPolicy selects a Pod, it switches that Pod to default-deny for the specified traffic direction, permitting only explicitly allowed traffic — the backend Pod's traffic isn't covered by the `role: frontend` allow rule. B misdescribes NetworkPolicy scope; C and D are unsupported leaps beyond the given scenario.

---

### Set D — Storage (Ch. 19)

**D1.** A StatefulSet Pod is deleted and rescheduled onto a different node. What happens to its associated PersistentVolumeClaim-backed data?
A. It is lost, since Pods are ephemeral
B. It is preserved and reattached, since the PVC identity is stable across rescheduling
C. It is automatically copied to a new PVC
D. It requires manual PV recreation every time

**Correct answer: B**
*Explanation:* StatefulSets provide stable per-replica storage identity — the same PVC follows the same ordinal replica across rescheduling (Chapter 14/19). A misunderstands StatefulSet storage guarantees; C and D describe unnecessary manual/automatic behaviors that don't occur by default.

---

### Set E — Scheduling (Ch. 20)

**E1.** A Pod remains stuck in `Pending` state, and `kubectl describe pod` shows an event: "0/5 nodes are available: 5 node(s) had taint that the pod didn't tolerate." What is the most direct fix?
A. Delete and recreate the Pod
B. Add a matching toleration to the Pod spec, or remove the taint if inappropriate
C. Increase the Pod's resource limits
D. Restart the kube-scheduler

**Correct answer: B**
*Explanation:* This message directly indicates a taint/toleration mismatch; adding a matching toleration (or removing an unnecessary taint) resolves it. A, C, and D don't address the actual reported cause.

---

### Set F — Security (Ch. 21)

**F1.** A ServiceAccount's associated Role grants `get` and `list` on `pods`, but a Pod using that ServiceAccount fails when attempting to `delete` a Pod via the API. What is the most likely cause?
A. RBAC is disabled cluster-wide
B. The Role does not grant the `delete` verb on `pods`, so the request is denied
C. NetworkPolicy is blocking the request
D. The ServiceAccount token has expired

**Correct answer: B**
*Explanation:* RBAC is additive and explicit — only granted verbs are permitted; `delete` was never granted. A contradicts the fact that `get`/`list` clearly work; C is a networking concern, not an authorization one; D is unsupported by the scenario.

---

### Set G — Observability, Mesh, GitOps, Serverless (Ch. 22-25)

**G1.** A Pod's liveness probe checks a downstream database's health endpoint instead of the Pod's own health. During a database outage, what happens?
A. Nothing — liveness probes ignore downstream dependencies
B. The Pod is repeatedly restarted even though the Pod itself is healthy, worsening an unrelated outage
C. The Pod is removed from Service Endpoints but not restarted
D. The database automatically recovers

**Correct answer: B**
*Explanation:* A liveness probe checking an external dependency will fail during that dependency's outage, triggering needless restarts of an otherwise-healthy Pod — a classic anti-pattern (Chapter 22). C describes readiness-probe behavior, not liveness; A and D are incorrect.

**G2.** In a service mesh with PeerAuthentication set to STRICT mTLS, a legacy Pod without the sidecar proxy injected suddenly cannot communicate with mesh members. Why?
A. STRICT mode rejects any connection not using mutual TLS, which the non-mesh Pod cannot perform
B. STRICT mode only affects logging verbosity
C. The Pod's Service was deleted
D. DNS resolution failed

**Correct answer: A**
*Explanation:* STRICT mTLS requires all connections to be mutually authenticated and encrypted; a Pod without a sidecar cannot participate in mTLS handshakes and is rejected (Chapter 23). B, C, and D are unrelated to mTLS enforcement.

**G3.** An engineer runs `kubectl scale deployment/web --replicas=10` directly on a cluster managed by ArgoCD with `selfHeal: true`, and Git still declares `replicas: 3`. What happens next?
A. The change persists indefinitely since it was applied via kubectl
B. ArgoCD detects the drift and reverts the Deployment back to 3 replicas per Git
C. ArgoCD merges the two values and sets replicas to 6
D. ArgoCD pauses all further syncs until manually resumed

**Correct answer: B**
*Explanation:* `selfHeal` actively reverts manual drift back to the Git-declared state (Chapter 24) — Git remains the single source of truth. A contradicts selfHeal's purpose; C and D describe behaviors ArgoCD does not perform.

**G4.** A customer-facing API deployed as a Knative Service with `minScale: "0"` receives complaints about slow first responses after periods of inactivity. What is the most targeted fix?
A. Abandon Knative entirely and use a standard Deployment
B. Increase `minScale` to keep at least one warm replica available
C. Decrease `maxScale` to reduce load
D. Disable autoscaling entirely

**Correct answer: B**
*Explanation:* Raising `minScale` above 0 keeps a warm replica ready, eliminating cold starts for latency-sensitive traffic while still allowing scale-up under load (Chapter 25). A is an overcorrection; C and D don't address the cold-start cause.

---

### Set H — CNCF Landscape & Production Best Practices (Ch. 26-27)

**H1.** A project has been in CNCF's Sandbox stage for two years with minimal adoption growth. What does this suggest, per the CNCF maturity model?
A. It is guaranteed to graduate soon
B. Sandbox status alone doesn't guarantee eventual graduation — adoption and governance maturity determine progression
C. It has already effectively graduated
D. It will be automatically archived after exactly two years

**Correct answer: B**
*Explanation:* Sandbox is an early, low-barrier stage; progression to Incubating/Graduated depends on demonstrated adoption and governance maturity, not simply time elapsed (Chapter 26). A, C, and D assert guarantees the maturity model does not make.

**H2.** During a node drain for OS patching, `kubectl drain` hangs and does not evict several Pods belonging to a critical Deployment. `kubectl get pdb` shows `minAvailable: 3` matching that Deployment's exactly 3 running replicas. What is happening?
A. The PodDisruptionBudget is correctly blocking eviction because evicting any Pod would drop availability below the required minimum
B. The node is unreachable
C. The Deployment has been deleted
D. RBAC is blocking the drain command

**Correct answer: A**
*Explanation:* With exactly 3 replicas and `minAvailable: 3`, evicting any Pod would violate the PDB, so eviction is correctly blocked until replacement replicas are healthy elsewhere (Chapter 27). B, C, and D are unsupported by the given scenario.

---

### Set I — Mixed-Domain (Exam-Style Random Order)

**I1.** Which object type is the correct choice for a stateless web application requiring rolling updates and rollback capability?
A. StatefulSet  B. DaemonSet  C. Deployment  D. Job
**Correct answer: C** — Deployments provide rolling updates and rollback for stateless apps; the others solve different problems (Chapters 12-15).

**I2.** What is the primary security risk of a Kubernetes Secret by default?
A. It is encrypted with a weak cipher
B. It is only base64-encoded, not encrypted, unless encryption at rest is explicitly configured
C. It cannot be mounted into Pods
D. It is automatically shared across all namespaces
**Correct answer: B** — Chapter 21; A, C, D misstate Secret behavior.

**I3.** What does the CSI standard interface enable?
A. Standardized container runtime swapping
B. Standardized storage driver integration across different providers
C. Standardized network policy enforcement
D. Standardized node autoscaling
**Correct answer: B** — Chapter 19; A describes CRI, C describes NetworkPolicy/CNI enforcement, D is unrelated.

**I4.** A Pod's readiness probe begins failing due to a slow downstream dependency, but its liveness probe continues to pass. What happens to the Pod?
A. It is restarted immediately
B. It is removed from Service Endpoints but keeps running, un-restarted
C. It is deleted and rescheduled to another node
D. Nothing changes; readiness probes only affect logging
**Correct answer: B** — Chapter 22; A describes liveness-probe failure behavior, not readiness; C and D misstate the actual effect of a failing readiness probe.

**I5.** A cluster administrator wants unscheduled Pods to avoid a set of nodes reserved for a specialized workload, without editing every Pod spec that already tolerates nothing. What mechanism achieves this?
A. NetworkPolicy
B. Taints on the reserved nodes
C. ResourceQuota on the namespace
D. PodDisruptionBudget
**Correct answer: B** — Chapter 20; tainting the reserved nodes repels all Pods that lack a matching toleration by default, with no per-Pod edits required. A is a network firewall mechanism, C caps resource consumption, and D governs voluntary disruption — none control node placement.

---

## 19-20. Self-Assessment Scoring Guide

| Score on this chapter's question bank | Interpretation |
|---|---|
| 90-100% | Ready to attempt Mock Exams (Chapter 32) |
| 70-89% | Review flagged domains' chapters before attempting mock exams |
| Below 70% | Return to full chapter review (Chapters 06-27) before further practice testing |

---

## 21. Chapter Summary (One-Page Revision Sheet)

- This chapter provides **scenario-based practice questions** (Sets A-I) mirroring the actual KCNA question style, spanning Architecture, Workloads, Networking, Storage, Scheduling, Security, Observability, Mesh, GitOps, Serverless, CNCF Landscape, and Production Best Practices.
- Every question explains **why each distractor is wrong**, not just why the correct answer is right — critical for building exam-day elimination skill (Chapter 28).
- Use the **self-assessment scoring guide** to decide readiness for full-length Mock Exams (Chapter 32).
- Practice Questions build on Flashcards' (Chapter 30) fact recall by requiring **applied reasoning within a described scenario**.

---

### Chapter Completion Checklist

1. **Topics covered:** Scenario-based multiple-choice questions across all major KCNA domains, with full distractor explanations.
2. **KCNA objectives completed:** Meta-chapter — applied practice across all domains.
3. **Remaining objectives:** Mock Exams (Chapter 32, 5 full 60-question exams), Interview Questions compilation (Chapter 33).
4. **Suggested revision checklist:** Score at least 90% across Sets A-I before attempting Mock Exam 1.
5. **Suggested hands-on exercises:** Retake Set G (Observability/Mesh/GitOps/Serverless) after a delay of several days to test retention, not just immediate recall.
6. **Related chapters:** Previous: [30-Flashcards](../30-Flashcards/README.md). Next: [32-Mock-Exams](../32-Mock-Exams/README.md) — five full-length 60-question mock exams.
