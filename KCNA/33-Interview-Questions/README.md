# 33 — Interview Questions

## 1. Learning Objectives

By the end of this chapter you will be able to:

- Answer consolidated interview-style questions spanning every domain in this guide, at easy/medium/hard difficulty.
- Explain Kubernetes and cloud native concepts in your own words, beyond multiple-choice recognition.
- Connect KCNA-level knowledge to how it's actually probed in real technical interviews.

**KCNA objectives covered:** Meta-chapter — consolidates interview questions already present in each chapter's Section 19 (Chapters 01-27) into one master reference.

---

## 2. Historical Background

Every chapter in this guide (01-27) already ends with its own "Interview Questions" section (easy/medium/hard) tied to that chapter's specific content. This final chapter exists because real interviews rarely stay confined to one topic — an interviewer asking about Deployments will often follow up into scheduling, networking, or failure scenarios. Consolidating all prior interview questions into one cross-referenced master list mirrors how interviews actually flow: topic to topic, building on earlier answers.

---

## 3. Motivation: Why Consolidate Instead of Just Rereading Each Chapter's Section 19?

**Analogy — The Final Oral Exam vs. Individual Class Quizzes:**
Each chapter's quiz (Section 19) tests one topic in isolation, like a weekly class quiz. A final oral exam instead jumps between topics and expects you to connect them — much closer to how a real technical interview unfolds. This chapter is that oral-exam rehearsal: the same underlying questions, but reorganized for cross-topic fluency rather than chapter-by-chapter isolation.

---

## 4. Core Concepts: How This Chapter Is Organized

- **Easy** questions test definitions and basic mechanics — suitable for screening interviews.
- **Medium** questions test the "why," not just the "what" — suitable for mid-level technical rounds.
- **Hard** questions test multi-concept scenario reasoning — suitable for senior/on-call-readiness rounds.
- Each question links back to its source chapter for deeper review if the answer feels shaky.

---

## 5-18. (Not Applicable Sections)

This chapter's content is entirely interview Q&A; Internal Working, Architecture, Component Breakdown, YAML Deep Dive, kubectl Commands, Hands-on Examples, Internal Flow, Real-world Examples, Best Practices, Common Mistakes, Troubleshooting, Comparison Tables, and Memory Tricks are not applicable as standalone sections here — they are the substance of Chapters 01-27 already, which this chapter references rather than repeats.

---

## 19. Consolidated Interview Questions

### Easy — Definitions & Basic Mechanics

1. **What is a Pod, and why is it the smallest deployable unit rather than a container?** *(Ch. 10)* A Pod is one or more containers sharing network namespace and storage; it's the smallest unit because tightly-coupled containers (e.g., app + log shipper) often need to share network/storage, which only a shared wrapper object can provide.
2. **What is the difference between a ReplicaSet and a Deployment?** *(Ch. 11-12)* A ReplicaSet maintains N identical Pods; a Deployment manages ReplicaSets to enable rolling updates and rollback — you almost never create ReplicaSets directly.
3. **What is etcd, and why does only the API server talk to it directly?** *(Ch. 07)* etcd is the distributed key-value store holding all cluster state; centralizing access through the API server enforces consistent validation, authorization, and admission control on every write.
4. **What is the difference between a Service and an Ingress?** *(Ch. 16-17)* A Service provides stable internal (or basic external) access to a set of Pods at L3/L4; Ingress adds L7 HTTP(S) routing rules (host/path-based) in front of one or more Services.
5. **What is a PersistentVolumeClaim?** *(Ch. 19)* A namespace-scoped request for storage that binds to a matching PersistentVolume, decoupling application storage requests from the underlying storage implementation.
6. **What is RBAC, in one sentence?** *(Ch. 21)* A system of Roles/ClusterRoles bound to subjects (users, groups, ServiceAccounts) that grants specific verbs on specific resources, following least-privilege principles.
7. **What are the three pillars of observability?** *(Ch. 22)* Logs, metrics, and traces.

### Medium — The "Why," Not Just the "What"

8. **Why does Kubernetes use a reconciliation loop instead of directly executing user commands?** *(Ch. 06)* Reconciliation continuously compares desired vs. actual state and self-heals drift automatically (e.g., after a crash or manual change), which a one-time imperative command cannot do — it's inherently resilient rather than a single fragile action.
9. **Why does a readiness probe failure not restart a container, while a liveness probe failure does?** *(Ch. 08, 22)* Readiness reflects "can this Pod currently serve traffic" (a temporary, often self-resolving state, e.g., warming a cache); restarting on every readiness dip would cause unnecessary churn. Liveness reflects "is this process fundamentally broken," where a restart is the appropriate remedy.
10. **Why is GitOps (pull-based) considered more secure than a traditional CI/CD push model for cluster deployments?** *(Ch. 24)* In a push model, the CI/CD pipeline must hold cluster credentials, widening the blast radius if the pipeline is compromised. In GitOps, an in-cluster agent pulls changes, so no external system needs standing cluster credentials, and Git becomes an auditable, single source of truth.
11. **Why must a service mesh's STRICT mTLS mode be rolled out carefully rather than enabled all at once?** *(Ch. 23)* STRICT mode rejects any connection that isn't mutually authenticated; if any legacy Pod still lacks a sidecar when STRICT is enabled, it will be locked out of the mesh entirely — a staged PERMISSIVE-then-STRICT rollout avoids this outage.
12. **Why does Knative's scale-to-zero introduce a trade-off, and how is it tuned?** *(Ch. 25)* Scaling to zero saves resources during idle periods but introduces cold-start latency on the next request. Tuning `minScale` above 0 keeps warm replicas ready for latency-sensitive workloads, trading some resource savings for consistent responsiveness.

### Hard — Multi-Concept Scenario Reasoning

13. **A Deployment's rolling update appears stuck at 50% progress, with old and new Pods both present. Walk through your full diagnostic approach.** *(Ch. 08, 12, 22)* First check `kubectl rollout status` and `kubectl describe deployment` for the specific blocking condition. A common cause: new Pods are failing their readiness probe, so the Deployment controller won't proceed further per its `maxUnavailable`/`maxSurge` settings (Ch. 12) — since readiness failures don't crash the Pod (Ch. 22), `kubectl get pods` may show them as "Running" but not "Ready." Check `kubectl logs` and `kubectl describe pod` on the new Pods for the actual application-level failure (e.g., a missing ConfigMap key, a downstream dependency unavailable during startup). Fix the root cause, or `kubectl rollout undo` to revert while investigating further.
14. **You enable ArgoCD's `selfHeal` on a production Deployment, and an on-call engineer's emergency `kubectl scale --replicas=20` during a traffic spike gets silently reverted to 3 within seconds, worsening the incident. What went wrong operationally, and what should change going forward?** *(Ch. 24, 27)* This is expected `selfHeal` behavior — it isn't a bug, but a process gap: emergency scaling should be done by (a) committing the scale change to Git first so GitOps stays authoritative, or (b) temporarily pausing auto-sync/selfHeal during an active incident, with a follow-up to reconcile Git afterward. The fix is a documented incident runbook for GitOps-managed clusters, not disabling selfHeal permanently (which would reintroduce configuration drift risk).
15. **A Pod's liveness probe is configured to check a downstream database's `/health` endpoint. During an unrelated database outage, dozens of unrelated application Pods start restarting in a loop, worsening the incident and paging on-call. Diagnose the anti-pattern and the correct fix.** *(Ch. 22)* The anti-pattern: liveness probes should only check whether the Pod's *own* process is healthy, never an external dependency — checking a downstream service conflates "am I broken" with "is something I depend on broken," and Kubernetes's only remedy for liveness failure (restarting the container) does nothing to fix a downstream outage while adding restart-storm load on an already-struggling system. The fix: change the liveness probe to check only local process health (e.g., an internal `/healthz` that doesn't call the database), and instead use a readiness probe (which removes the Pod from traffic without restarting it) if downstream availability should affect traffic routing at all.
16. **You're asked in an interview: "How would you design a multi-tenant Kubernetes platform for 10 internal teams, covering resource fairness, security isolation, and safe upgrades?" Give a structured answer.** *(Ch. 20-21, 27)* Structure the answer around three pillars: (1) **Resource fairness** — per-namespace ResourceQuotas and LimitRanges (Ch. 27) so no team can starve others, combined with resource requests/limits (Ch. 20) for scheduler-aware placement. (2) **Security isolation** — namespace-scoped RBAC Roles/RoleBindings (Ch. 21) following least privilege, NetworkPolicies (Ch. 18) for L3/L4 traffic isolation between teams' namespaces, and Pod Security Standards to prevent privileged workloads. (3) **Safe upgrades** — PodDisruptionBudgets (Ch. 27) on every team's critical workloads so cluster-wide node maintenance never drops any team below its availability floor, and a documented control-plane-first, one-minor-version-at-a-time upgrade policy respecting version skew (Ch. 27). Tie it together by noting these mechanisms compose — e.g., a ResourceQuota doesn't protect against a bad NetworkPolicy gap, so each pillar must be addressed independently.

---

## 20. Cross-Reference Index (Where Each Topic Was First Taught)

| Topic | Source Chapter |
|---|---|
| Reconciliation loop | 06 |
| Control plane components | 06-07 |
| kubelet, kube-proxy, container runtime | 08 |
| Pods, labels/selectors | 09-10 |
| ReplicaSets, Deployments | 11-12 |
| DaemonSets, StatefulSets | 13-14 |
| Jobs, CronJobs | 15 |
| Services | 16 |
| Ingress, Gateway API | 17 |
| Networking, NetworkPolicy, CNI, CoreDNS | 18 |
| Storage, PV/PVC, CSI | 19 |
| Scheduling, taints/tolerations, affinity | 20 |
| RBAC, Secrets, Pod Security | 21 |
| Observability, probes, tracing | 22 |
| Service mesh, mTLS | 23 |
| GitOps, ArgoCD/Flux | 24 |
| Serverless, Knative | 25 |
| CNCF landscape | 26 |
| Production best practices | 27 |

---

## 21. Chapter Summary (One-Page Revision Sheet) — And Guide Completion

- This chapter consolidates interview questions from across the entire guide into **easy/medium/hard** tiers, emphasizing cross-topic reasoning over isolated recall.
- **Hard-tier questions** (13-16) model realistic interview scenarios requiring you to connect 2-3 chapters' concepts simultaneously — the skill real interviews (and real production incidents) actually test.
- The **cross-reference index** (Section 20) provides a one-page map back to every topic's original teaching chapter for final review.
- **This is the final chapter of the KCNA guide.** The full curriculum spans: `00-Roadmap` through `27-Production-Best-Practices` (core content, Chapters 00-27), followed by exam-readiness tooling — `28-Exam-Preparation`, `29-Cheat-Sheets`, `30-Flashcards`, `31-Practice-Questions`, `32-Mock-Exams`, and this chapter, `33-Interview-Questions`.

---

### Chapter Completion Checklist

1. **Topics covered:** Consolidated easy/medium/hard interview questions spanning all 27 core chapters, plus a full cross-reference index.
2. **KCNA objectives completed:** All KCNA domains — this chapter closes out the guide's final meta-content layer.
3. **Remaining objectives:** None — this is the last chapter in the planned 34-folder structure.
4. **Suggested revision checklist:** Answer all four hard-tier scenario questions (13-16) aloud, unaided, connecting each to its named source chapters.
5. **Suggested hands-on exercises:** Conduct a mock interview with a study partner using Section 19 as the question bank, mixing difficulty tiers unpredictably as a real interviewer would.
6. **Related chapters:** Previous: [32-Mock-Exams](../32-Mock-Exams/README.md). This is the final chapter — for a full curriculum overview, see [00-Roadmap](../00-Roadmap/README.md).
