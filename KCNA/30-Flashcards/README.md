# 30 — Flashcards

## 1. Learning Objectives

By the end of this chapter you will be able to:

- Use question-and-answer flashcard pairs for active-recall practice across every KCNA domain.
- Self-test rapidly without needing the full chapter context.
- Identify which chapter to revisit when a flashcard answer feels shaky.

**KCNA objectives covered:** Meta-chapter — active-recall practice across all domains (Chapters 01-27).

---

## 2. Historical Background

Flashcards trace back to 19th-century rote-learning techniques, but their modern effectiveness is grounded in the **testing effect** — cognitive science research showing that retrieving information from memory (not just re-reading it) is what builds durable, long-term retention. Spaced-repetition flashcard systems (e.g., Anki) formalized this into a study method now standard across technical certification prep, including Kubernetes exams.

---

## 3. Motivation: Why Flashcards, When Chapters Already Explain Everything?

**Analogy — The Gym vs. The Anatomy Textbook:**
Reading an anatomy textbook teaches you which muscles exist and why they matter — but it doesn't build strength. Lifting weights (retrieval practice) does. Chapters 01-27 are the textbook; flashcards are the gym. You already understand *why* a readiness probe removes a Pod from a Service's Endpoints (Chapter 08/16) — flashcards build the *speed and certainty* of recalling that fact cold, under exam time pressure.

### 3.1 How Is This Normally Done Without a Dedicated Chapter?

Learners often rely on re-reading chapters multiple times, mistaking familiarity (recognizing an answer when shown) for true recall (producing the answer unprompted).

### 3.2 Why Is That Insufficient?

Recognition is a much weaker memory signal than recall; multiple-choice exams often test recall indirectly by requiring you to reason from a scenario to the correct term or behavior — familiarity alone frequently fails under that pressure.

### 3.3 How This Chapter Solves It

This chapter provides explicit question/answer flashcard pairs, organized by domain, forcing genuine retrieval practice rather than passive re-reading.

---

## 4. Core Concepts: How to Use These Flashcards

- Cover the **Answer** column, read only the **Question**, and attempt to answer aloud or in writing before revealing the answer.
- Mark any card you get wrong or hesitate on; revisit those specifically the next day (simple spaced repetition).
- Cycle through all domains at least 3 times before the exam, not just once.

---

## 5. Internal Working

Not applicable — this chapter is a static study artifact, not a system with internal mechanics.

---

## 6. Architecture

```
┌───────────────────────────────────────┐
│         Flashcard Domains (§7)                 │
│  Architecture · Workloads · Networking          │
│  Storage · Scheduling · Security                │
│  Observability · Mesh · GitOps · Serverless     │
│  CNCF Landscape · Production Practices          │
└───────────────────────────────────────┘
```

---

## 7. Flashcard Sets by Domain

### 7.1 Kubernetes Architecture (Ch. 06-08)

| Q | A |
|---|---|
| What component is the only one that talks directly to etcd? | kube-apiserver |
| What runs the reconciliation loops for built-in controllers? | kube-controller-manager |
| What component assigns Pods to nodes? | kube-scheduler |
| What agent on each worker node ensures containers are running per PodSpec? | kubelet |
| What implements Service networking rules on each node? | kube-proxy |
| What interface lets kubelet talk to any container runtime? | CRI (Container Runtime Interface) |

### 7.2 Workload Objects (Ch. 09-15)

| Q | A |
|---|---|
| What object directly owns and maintains a set of identical Pods? | ReplicaSet |
| What object manages ReplicaSets to enable rolling updates and rollbacks? | Deployment |
| What object guarantees exactly one Pod per matching node? | DaemonSet |
| What object gives Pods stable network identity and stable per-replica storage? | StatefulSet |
| What object runs a task to completion, retrying on failure? | Job |
| What object runs Jobs on a schedule? | CronJob |

### 7.3 Networking (Ch. 16-18)

| Q | A |
|---|---|
| What Service type exposes a static port on every node? | NodePort |
| What Service type provisions an external cloud load balancer? | LoadBalancer |
| What object provides L7 HTTP routing to Services? | Ingress |
| What is the newer, more expressive successor to Ingress? | Gateway API |
| What object defines L3/L4 firewall rules between Pods? | NetworkPolicy |
| What provides cluster-internal DNS resolution? | CoreDNS |

### 7.4 Storage (Ch. 19)

| Q | A |
|---|---|
| What is a cluster-scoped piece of provisioned storage called? | PersistentVolume (PV) |
| What is a namespace-scoped request for storage called? | PersistentVolumeClaim (PVC) |
| What object is a template for dynamic PV provisioning? | StorageClass |
| What standard interface do storage drivers implement? | CSI (Container Storage Interface) |

### 7.5 Scheduling (Ch. 20)

| Q | A |
|---|---|
| What mechanism repels Pods from a node unless explicitly permitted? | Taint |
| What mechanism on a Pod allows it onto a tainted node? | Toleration |
| What value does the scheduler use for placement decisions? | Resource requests |
| What can happen to a container that exceeds its memory limit? | It gets OOMKilled |

### 7.6 Security (Ch. 21)

| Q | A |
|---|---|
| What object grants namespace-scoped permissions? | Role (+ RoleBinding) |
| What object grants cluster-wide permissions? | ClusterRole (+ ClusterRoleBinding) |
| What gives a Pod an identity to authenticate to the API server? | ServiceAccount |
| Are Kubernetes Secrets encrypted at rest by default? | No — only base64-encoded unless encryption at rest is explicitly configured |

### 7.7 Observability (Ch. 22)

| Q | A |
|---|---|
| What are the three pillars of observability? | Logs, metrics, traces |
| What probe type removes a Pod from Service Endpoints on failure, without restarting it? | Readiness probe |
| What probe type restarts a container on failure? | Liveness probe |
| What probe type delays liveness/readiness checks for slow-starting containers? | Startup probe |
| What is a single unit of work in a distributed trace called? | A span |

### 7.8 Service Mesh (Ch. 23)

| Q | A |
|---|---|
| What pattern intercepts Pod traffic transparently for a service mesh? | Sidecar proxy |
| What plane centrally configures all mesh sidecars? | Control plane |
| What does mTLS provide that plain TLS does not? | Mutual authentication (both sides prove identity) |
| What mesh feature enables gradual canary rollouts? | Weighted traffic splitting |

### 7.9 GitOps (Ch. 24)

| Q | A |
|---|---|
| In GitOps, what holds the cluster credentials — the pipeline or the in-cluster agent? | The in-cluster agent (pull-based) |
| What is divergence between Git and cluster state called? | Drift |
| What ArgoCD setting automatically reverts manual cluster changes? | `syncPolicy.automated.selfHeal` |
| What ArgoCD setting removes resources deleted from Git? | `syncPolicy.automated.prune` |

### 7.10 Serverless (Ch. 25)

| Q | A |
|---|---|
| What Knative behavior reduces idle replicas to zero? | Scale-to-zero |
| What is the latency penalty when scaling up from zero called? | Cold start |
| What Knative component handles autoscaling of HTTP-driven workloads? | Knative Serving |
| What Knative component routes events from sources to services? | Knative Eventing |

### 7.11 CNCF Landscape (Ch. 26)

| Q | A |
|---|---|
| What are the three CNCF project maturity levels, in order? | Sandbox → Incubating → Graduated |
| What foundation hosts the CNCF? | The Linux Foundation |
| What was CNCF's original flagship hosted project? | Kubernetes |

### 7.12 Production Best Practices (Ch. 27)

| Q | A |
|---|---|
| What object caps aggregate namespace resource consumption? | ResourceQuota |
| What object guarantees minimum available Pods during voluntary disruption? | PodDisruptionBudget (PDB) |
| What is the safe cluster upgrade order? | Control plane first, then nodes, one minor version at a time |

---

## 8. Important Terminology

See each domain's flashcard set above — Section 7 doubles as this chapter's terminology reference.

---

## 9. YAML Deep Dive

Not applicable — flashcards are Q/A pairs, not manifests. See Chapter 29 for YAML skeletons.

---

## 10. kubectl Commands

Not applicable — see Chapter 29's kubectl fast-reference table.

---

## 11. Hands-on Examples

**Lab 1 — Full-domain drill:** Go through every table in Section 7 once per day for a week, tracking which cards you miss.

**Lab 2 — Weak-card isolation:** Maintain a running list of missed cards across all sessions; drill only that subset in the final 2 days before the exam.

**Lab 3 — Reverse drill:** Cover the Question column instead, read only the Answer, and try to reconstruct a plausible question — this checks whether you understand the concept generally, not just one fixed phrasing.

---

## 12. Internal Flow

Not applicable — this is a static study artifact.

---

## 13. Real-World Examples

1. A candidate drills the Section 7.3 networking cards daily and stops confusing Ingress with Gateway API on practice exams.
2. A candidate isolates 8 consistently-missed cards across all domains and reviews only those in the final 48 hours.
3. A candidate uses the reverse-drill technique on Section 7.7 and discovers they only memorized the exact phrasing, not the concept — prompting a return to Chapter 22.
4. A study group quizzes each other verbally using Section 7 as a shared question bank.
5. A candidate uses Section 7.9's GitOps cards to nail a scenario question about `selfHeal` reverting a manual `kubectl scale` change.

---

## 14. Best Practices

- Answer **out loud or in writing** before revealing the answer — silently reading both sides defeats the purpose.
- Track **missed cards explicitly** and weight review time toward them.
- Use the **reverse drill** periodically to confirm conceptual understanding, not memorized phrasing.
- Cycle through all 12 domain sets **at least 3 times** before exam day.

---

## 15. Common Mistakes

- Reading question and answer together without attempting recall first — this builds false confidence.
- Only drilling favorite/easy domains and avoiding weak ones.
- Treating a single successful recall as "mastered" instead of retesting after a delay (spaced repetition).

---

## 16. Troubleshooting

| Symptom | Fix |
|---|---|
| Same cards missed repeatedly | Return to the source chapter's Motivation/Internal Working sections, not just the card itself |
| Recall feels shaky under time pressure | Practice with a timer per card (aim for under 10 seconds) |
| Cards feel memorized but scenario questions still fail | Use the reverse drill and revisit Practice Questions (Chapter 31) for applied reasoning |

---

## 17. Comparison Tables

See Section 7 — every card set is implicitly a comparison/definition table by construction.

---

## 18. Memory Tricks

- **"Recall, don't recognize."**
- **"Miss it, mark it, drill it."** — the core spaced-repetition loop for this chapter.

---

## 19. Interview Questions

**Easy:**
1. Why is active recall (flashcards) more effective than re-reading for exam prep?
   *Expected answer:* Active recall forces retrieval of information from memory, which strengthens long-term retention far more than passive re-reading, per the well-established testing effect.

**Medium:**
2. What is the risk of only ever answering a flashcard the same fixed way it's phrased?
   *Expected answer:* You may be memorizing the specific phrasing rather than the underlying concept, which fails when an exam question describes the same concept using different wording or a real-world scenario — the reverse drill (Section 11, Lab 3) helps catch this gap.

**Hard:**
3. A candidate reports 100% accuracy drilling all flashcards in this chapter, yet still misses scenario-based practice questions on the same topics. Diagnose the gap and propose a fix.
   *Expected answer:* Flashcards test isolated fact recall, but KCNA scenario questions require applying that fact within a described situation — e.g., knowing "readiness probe removes a Pod from Endpoints" (a flashcard fact) is different from recognizing, in a scenario where a Service silently stops routing to one replica during a slow dependency call, that a failing readiness probe is the cause. The fix is to pair flashcard drilling with Practice Questions (Chapter 31) and Mock Exams (Chapter 32), which test the same facts in applied, scenario form rather than isolated recall.

---

## 20. KCNA Practice Questions

**Q1.** What cognitive principle makes flashcard-based study more effective than passive re-reading?
A. The recency effect
B. The testing effect (active recall strengthens retention)
C. The primacy effect
D. Spacing has no measurable effect on retention

**Correct answer: B**
*Explanation:* The testing effect is the well-established finding that retrieval practice strengthens memory more than passive review. A, C, and D misstate or dismiss the relevant principle.

---

**Q2.** Per Section 7.1, which component is the only one that communicates directly with etcd?
A. kubelet
B. kube-scheduler
C. kube-apiserver
D. kube-proxy

**Correct answer: C**
*Explanation:* Only kube-apiserver talks directly to etcd (Chapter 07); all other components go through the API server.

---

**Q3.** Per Section 7.7, which probe type removes a Pod from Service Endpoints without restarting the container?
A. Liveness probe
B. Startup probe
C. Readiness probe
D. Volume probe (not a real probe type)

**Correct answer: C**
*Explanation:* Readiness probe failure removes a Pod from Endpoints but does not restart it (Chapter 22). Liveness probe failure (A) restarts the container; startup probe (B) delays other probes; "volume probe" (D) does not exist.

---

**Q4.** Per Section 7.9, what does ArgoCD's `selfHeal` setting do?
A. Automatically deletes resources removed from Git
B. Automatically reverts manual cluster changes back to match Git
C. Automatically restarts failed Pods
D. Automatically scales Deployments based on CPU usage

**Correct answer: B**
*Explanation:* `selfHeal` reverts drift by re-applying the Git-defined state over manual changes (Chapter 24). A describes `prune`, C describes liveness-probe-driven restarts, and D describes the Horizontal Pod Autoscaler.

---

**Q5.** What is the recommended way to use missed flashcards according to this chapter's best practices?
A. Discard them since they are clearly too difficult
B. Re-read them once and move on permanently
C. Track them explicitly and weight review time toward them (spaced repetition)
D. Skip them and focus only on cards already mastered

**Correct answer: C**
*Explanation:* Tracking missed cards and prioritizing their review implements spaced repetition, the core recommended practice in Section 14. A, B, and D all under-invest in genuinely weak areas.

---

**Q6.** Per Section 7.2, which object gives Pods stable network identity and stable per-replica storage?
A. Deployment
B. DaemonSet
C. StatefulSet
D. ReplicaSet

**Correct answer: C**
*Explanation:* StatefulSet provides stable identity and stable storage per replica (Chapter 12). Deployment (A) and ReplicaSet (D) provide neither guarantee, and DaemonSet (B) guarantees one Pod per node, not stable identity/storage.

---

**Q7.** Per Section 7.3, what is the newer, more expressive successor to Ingress?
A. NetworkPolicy
B. Gateway API
C. CoreDNS
D. NodePort

**Correct answer: B**
*Explanation:* Gateway API is the newer, more expressive successor to Ingress (Chapter 17). NetworkPolicy (A) is a firewall mechanism, CoreDNS (C) handles DNS, and NodePort (D) is a Service type.

---

**Q8.** Per Section 7.4, what standard interface do storage drivers implement to integrate with Kubernetes?
A. CRI
B. CNI
C. CSI
D. OCI

**Correct answer: C**
*Explanation:* CSI (Container Storage Interface) is the standard storage driver interface (Chapter 19). CRI (A) is for container runtimes, CNI (B) is for networking plugins, and OCI (D) defines image/runtime specs.

---

**Q9.** Per Section 7.5, what can happen to a container that exceeds its memory limit?
A. It is automatically rescheduled to a larger node
B. It gets OOMKilled
C. It is throttled but never killed
D. Its memory limit is silently raised

**Correct answer: B**
*Explanation:* Exceeding a memory limit results in the container being OOMKilled (Chapter 20). A, C, and D do not describe actual Kubernetes memory-limit enforcement behavior.

---

**Q10.** Per Section 7.6, are Kubernetes Secrets encrypted at rest by default?
A. Yes, always encrypted with AES-256 by default
B. No — only base64-encoded unless encryption at rest is explicitly configured
C. Yes, but only for Secrets larger than 1 MiB
D. No, Secrets cannot be encrypted at rest under any configuration

**Correct answer: B**
*Explanation:* Secrets are base64-encoded, not encrypted, unless encryption at rest is explicitly configured (Chapter 21). A and C invent false defaults; D wrongly claims encryption at rest is impossible.

---

**Q11.** Per Section 7.7, what are the three pillars of observability?
A. Dashboards, alerts, runbooks
B. Logs, metrics, traces
C. CPU, memory, disk
D. Readiness, liveness, startup

**Correct answer: B**
*Explanation:* Logs, metrics, and traces are the three pillars of observability (Chapter 22). A describes tooling artifacts, C describes resource types, and D describes probe types, not observability pillars.

---

**Q12.** Per Section 7.8, what does mTLS provide that plain TLS does not?
A. Faster handshake times
B. Mutual authentication — both sides prove their identity
C. Automatic certificate rotation
D. Compression of traffic payloads

**Correct answer: B**
*Explanation:* mTLS requires both client and server to present certificates, providing mutual authentication (Chapter 23). A, C, and D are not the defining distinction between TLS and mTLS.

---

**Q13.** Per Section 7.9, in a pull-based GitOps model, does the pipeline or the in-cluster agent hold the cluster credentials?
A. The CI/CD pipeline
B. Neither; credentials are not required
C. The in-cluster agent
D. An external secrets manager only

**Correct answer: C**
*Explanation:* Pull-based GitOps keeps cluster credentials inside the cluster with the in-cluster agent (e.g., ArgoCD), rather than exposing them to an external pipeline (Chapter 24). A describes the less secure push-based model; B and D misstate the requirement.

---

**Q14.** Per Section 7.10, what is the latency penalty called when a Knative service scales up from zero replicas?
A. Warm start
B. Scale-to-zero
C. Cold start
D. Revision skew

**Correct answer: C**
*Explanation:* Cold start is the latency penalty of scaling up from zero (Chapter 25). Scale-to-zero (B) is the act of reducing to zero replicas, not the latency penalty itself; "warm start" (A) and "revision skew" (D) are not the terms used.

---

**Q15.** Per Section 7.11, what was CNCF's original flagship hosted project?
A. Prometheus
B. Envoy
C. Kubernetes
D. containerd

**Correct answer: C**
*Explanation:* Kubernetes was CNCF's original flagship hosted project (Chapter 26). Prometheus (A) was the second graduated project, and Envoy (B) and containerd (D) were hosted later.

---

**Q16.** Per Section 7.12, what object guarantees a minimum number of available Pods during voluntary disruptions?
A. ResourceQuota
B. LimitRange
C. PodDisruptionBudget (PDB)
D. NetworkPolicy

**Correct answer: C**
*Explanation:* A PodDisruptionBudget guarantees minimum availability during voluntary disruptions such as node drains (Chapter 27). ResourceQuota (A) caps aggregate resource consumption, LimitRange (B) sets per-object resource defaults/bounds, and NetworkPolicy (D) is unrelated to disruption budgets.

---

**Q17.** Per Section 11's Lab 3 (Reverse drill), what does this exercise specifically test that the standard forward drill does not?
A. Speed of recall under a timer
B. Whether the concept is understood generally, not just one fixed question phrasing
C. Ability to write YAML manifests from memory
D. Knowledge of exact kubectl command syntax

**Correct answer: B**
*Explanation:* The reverse drill covers the Answer and asks the candidate to reconstruct a plausible question, testing conceptual understanding rather than memorized phrasing (Section 11). A describes a different aspect of drilling in general; C and D are unrelated to this chapter's flashcards, which are Q/A pairs, not YAML or CLI drills.

---

**Q18.** Per Section 15 (Common Mistakes), what false confidence trap should candidates avoid?
A. Drilling weak domains too often
B. Reading question and answer together without attempting recall first
C. Using spaced repetition too aggressively
D. Cycling through all 12 domain sets more than 3 times

**Correct answer: B**
*Explanation:* Reading both sides together without attempting recall first builds false confidence, per Section 15. A, C, and D are not identified as mistakes — the chapter explicitly recommends spaced repetition and cycling through all domains at least 3 times.

---

**Q19.** Per Section 16 (Troubleshooting), what should a candidate do if the same flashcard is missed repeatedly?
A. Remove that card from the rotation entirely
B. Return to the source chapter's Motivation/Internal Working sections, not just the card itself
C. Simply memorize the answer text more times
D. Assume the flashcard itself is wrong and skip it

**Correct answer: B**
*Explanation:* Section 16 recommends returning to the source chapter's deeper explanation sections rather than just re-drilling the isolated fact. A, C, and D avoid addressing the underlying conceptual gap.

---

**Q20.** Per the Chapter Summary's best-practice loop, what is the correct sequence for using these flashcards effectively?
A. Drill misses first, then answer before revealing, then mark misses
B. Answer before revealing → mark misses → drill misses with spaced repetition → periodically reverse-drill
C. Reverse-drill first, then answer before revealing, then discard misses
D. Mark misses → discard them → drill only mastered cards

**Correct answer: B**
*Explanation:* This is the exact loop stated in the Chapter Summary (Section 21). A, C, and D scramble or invert the correct order, and D additionally contradicts the guidance to prioritize missed cards rather than discard them.

---

## 21. Chapter Summary (One-Page Revision Sheet)

- Flashcards implement **active recall**, which is more effective than passive re-reading due to the testing effect.
- Twelve domain-organized card sets (Section 7) cover **Architecture through Production Best Practices** (Chapters 06-27).
- Best practice loop: **answer before revealing → mark misses → drill misses with spaced repetition → periodically reverse-drill** to confirm conceptual (not just phrasing) understanding.
- Pair flashcards with **Practice Questions (Chapter 31)** and **Mock Exams (Chapter 32)** for applied, scenario-based reasoning practice.

---

### Chapter Completion Checklist

1. **Topics covered:** Twelve domain flashcard sets spanning Architecture, Workloads, Networking, Storage, Scheduling, Security, Observability, Mesh, GitOps, Serverless, CNCF Landscape, and Production Best Practices.
2. **KCNA objectives completed:** Meta-chapter — active-recall practice across all domains.
3. **Remaining objectives:** Practice Questions (Chapter 31), Mock Exams (Chapter 32), Interview Questions compilation (Chapter 33).
4. **Suggested revision checklist:** Score 100% cold on all 12 card sets, in randomized order, at least once.
5. **Suggested hands-on exercises:** Complete Lab 2 (weak-card isolation) starting one week before the exam.
6. **Related chapters:** Previous: [29-Cheat-Sheets](../29-Cheat-Sheets/README.md). Next: [31-Practice-Questions](../31-Practice-Questions/README.md) — scenario-based practice question sets.
