# 12 — Deployments

## 1. Learning Objectives

By the end of this chapter you will be able to:

- Explain why ReplicaSets alone are insufficient for real-world release management.
- Explain how a Deployment manages ReplicaSets to enable rolling updates and rollbacks.
- Explain the two update strategies: `RollingUpdate` and `Recreate`.
- Read and write a complete Deployment manifest, including `maxSurge`/`maxUnavailable`.
- Perform and undo a rollout using `kubectl`.

**KCNA objectives covered:** Kubernetes Fundamentals domain — the standard, most commonly used workload controller in Kubernetes.

---

## 2. Historical Background

As Chapter 11 established, a ReplicaSet alone can maintain a fixed number of Pods but has no concept of *changing* those Pods safely over time — updating its template has zero effect on already-running Pods. Early Kubernetes users had to manually orchestrate updates: create a new ReplicaSet, scale it up, scale the old one down, watch for errors, and manually roll back if something broke. This was risky and repetitive. Kubernetes introduced the **Deployment** object to formalize and automate this exact dance, making rolling updates and rollbacks a declarative, one-line operation.

---

## 3. Motivation: Why Do Deployments Exist?

**Analogy — The Airport Runway Repaving Project:**
An airport needs to repave a runway used by many flights, but it can never shut down all runways at once — that would halt all air traffic. Instead, the airport repaves one runway at a time, keeping others open, checking each newly repaved runway is safe before moving to the next, and if a repaved runway turns out to be faulty, immediately reopening the old one while investigating. A **Deployment** does exactly this for your application: it replaces old Pods with new ones a few at a time, verifying health along the way, and can revert instantly if something goes wrong — all without ever taking your whole application offline.

### 3.1 How Was This Solved Before Kubernetes?

Rolling updates required custom orchestration scripts or external deployment tools coordinating manual load balancer changes, health checks, and staged server replacement — often bespoke per company, with rollback as a separate, manually-triggered emergency procedure.

### 3.2 How Kubernetes Solves It

A Deployment manages one or more ReplicaSets on your behalf: when you change the Pod template (e.g., a new image), the Deployment creates a **new** ReplicaSet with that template and gradually shifts replica counts from the old ReplicaSet to the new one according to a configurable strategy, while retaining old ReplicaSets (scaled to zero) to enable instant rollback.

---

## 4. Core Concepts

### 4.1 What Is a Deployment? (Formal Definition)

**Definition:** A Deployment is a controller that manages ReplicaSets to provide declarative updates for Pods, including rolling updates, rollbacks, and revision history — built directly on top of the ReplicaSet mechanism from Chapter 11.

### 4.2 Deployment → ReplicaSet → Pod Ownership Chain

A Deployment never manages Pods directly. Instead:

```
Deployment  --owns-->  ReplicaSet  --owns-->  Pods
```

Every rollout creates a brand **new** ReplicaSet (Kubernetes computes a hash of the Pod template to name it, e.g., `web-7d9f8c6b45`); the old ReplicaSet is kept (scaled to 0 replicas) for rollback history, up to `spec.revisionHistoryLimit`.

### 4.3 Update Strategies

| Strategy | Behavior | Downtime |
|---|---|---|
| `RollingUpdate` (default) | Gradually replaces old Pods with new ones, controlled by `maxSurge`/`maxUnavailable` | None, if health checks pass |
| `Recreate` | Terminates ALL old Pods first, then creates all new ones | Yes — a full gap where no Pods are running |

### 4.4 `maxSurge` and `maxUnavailable`

| Field | Meaning | Example |
|---|---|---|
| `maxSurge` | How many *extra* Pods beyond `replicas` can exist temporarily during a rollout | `maxSurge: 1` with `replicas: 3` allows up to 4 Pods briefly |
| `maxUnavailable` | How many Pods can be unavailable during a rollout | `maxUnavailable: 1` with `replicas: 3` allows dropping to 2 briefly |

**Analogy:** `maxSurge` is "how many extra temporary workers can I hire during the transition," and `maxUnavailable` is "how many can I afford to have off duty at once" — together they tune how cautious vs. fast the rollout is.

### 4.5 Rollback

Every successful rollout is recorded as a revision. If a new version turns out to be broken, `kubectl rollout undo` tells the Deployment to scale the previous ReplicaSet back up and the broken one back down — the same rolling mechanism, just running in reverse.

---

## 5. Internal Working

```
1. User changes the Deployment's Pod template (e.g., new image tag)
        ↓
2. Deployment controller (kube-controller-manager, Chapter 07 Section
   4.4) detects the template hash changed
        ↓
3. Controller creates a NEW ReplicaSet with the new template, replicas: 0
        ↓
4. Controller incrementally scales the new ReplicaSet up and the old
   ReplicaSet down, respecting maxSurge/maxUnavailable at each step
        ↓
5. After each step, kubelet's readiness probes (Chapter 08 Section 4.2)
   confirm new Pods are healthy before the next step proceeds
        ↓
6. Once new ReplicaSet reaches full desired replicas and old reaches 0,
   the rollout is complete; old ReplicaSet is kept (scaled to 0) for
   rollback history
```

---

## 6. Architecture

```
┌─────────────────────────────────────────────────────────┐
│                       Deployment (web)                        │
│                  strategy: RollingUpdate                     │
│              maxSurge: 1, maxUnavailable: 0                   │
└─────────────┬───────────────────────┬─────────────────┘
                  │                            │
                  ▼                            ▼
     ┌────────────────────┐   ┌────────────────────┐
     │ ReplicaSet (old, v1)   │   │ ReplicaSet (new, v2)   │
     │  replicas: 3 → 0        │   │  replicas: 0 → 3        │
     └──────────┬─────────┘   └──────────┬─────────┘
                  ▼                            ▼
           Pods (v1) scale down       Pods (v2) scale up
           gradually, one at a time,  gradually, respecting
           as v2 Pods become Ready    maxSurge/maxUnavailable
```

---

## 7. Component Breakdown

| Piece | Role |
|---|---|
| Deployment object | Declares desired Pod template, replica count, and update strategy |
| Deployment controller | Orchestrates creation/scaling of ReplicaSets to realize rollouts |
| Old/new ReplicaSets | Concrete, versioned snapshots of the Pod template, scaled up/down during rollout |
| Revision history | Retained old ReplicaSets enabling `kubectl rollout undo` |

---

## 8. Important Terminology

| Term | Meaning |
|---|---|
| Deployment | Controller managing ReplicaSets to provide rolling updates and rollbacks |
| Rolling update | Gradual replacement of old Pods with new ones |
| Rollback | Reverting to a previous ReplicaSet/revision |
| maxSurge | Max extra Pods allowed beyond desired count during rollout |
| maxUnavailable | Max Pods allowed to be unavailable during rollout |
| Revision | A recorded historical version of the Deployment's Pod template |

---

## 9. YAML Deep Dive

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 3
  revisionHistoryLimit: 5
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
        - name: web
          image: myapp:1.0
          readinessProbe:
            httpGet:
              path: /healthz
              port: 8080
```

Note the readiness probe (Chapter 08 Section 4.2) — the Deployment controller relies on it to know when a newly created Pod is safe to count as "up" before proceeding to the next rollout step.

---

## 10. kubectl Commands

| Command | Purpose | Example |
|---|---|---|
| `kubectl create deployment <name> --image=<image>` | Quickly create a Deployment | `kubectl create deployment web --image=myapp:1.0` |
| `kubectl set image deployment/<name> <container>=<image>` | Trigger a rolling update | `kubectl set image deployment/web web=myapp:2.0` |
| `kubectl rollout status deployment/<name>` | Watch rollout progress | `kubectl rollout status deployment/web` |
| `kubectl rollout history deployment/<name>` | List revision history | `kubectl rollout history deployment/web` |
| `kubectl rollout undo deployment/<name>` | Roll back to the previous revision | `kubectl rollout undo deployment/web` |
| `kubectl rollout undo deployment/<name> --to-revision=N` | Roll back to a specific revision | `kubectl rollout undo deployment/web --to-revision=2` |
| `kubectl scale deployment/<name> --replicas=N` | Change desired replica count | `kubectl scale deployment/web --replicas=5` |

---

## 11. Hands-on Examples

**Lab 1 — Perform a rolling update and watch it progress:**
```bash
kubectl apply -f web-deployment.yaml
kubectl set image deployment/web web=myapp:2.0
kubectl rollout status deployment/web
kubectl get rs
# Two ReplicaSets appear — old scaling to 0, new scaling to 3
```

**Lab 2 — Roll back a bad release:**
```bash
kubectl set image deployment/web web=myapp:broken
kubectl rollout status deployment/web   # notice it hangs/fails readiness
kubectl rollout undo deployment/web
kubectl rollout status deployment/web   # back to the last good version
```

**Lab 3 — Compare RollingUpdate vs Recreate:**
```bash
kubectl patch deployment web -p '{"spec":{"strategy":{"type":"Recreate"}}}'
kubectl set image deployment/web web=myapp:3.0
kubectl get pods -w
# Observe ALL old Pods terminate before ANY new Pod is created —
# a visible gap in availability, unlike RollingUpdate
```

---

## 12. Internal Flow

See Section 5's 6-step flow — this builds directly on the ReplicaSet reconciliation loop from Chapter 11 Section 5, adding an outer layer that manages *which* ReplicaSet is currently being scaled up vs down.

---

## 13. Real-World Examples

1. **Zero-downtime web application releases** are the textbook Deployment use case — `RollingUpdate` with a readiness probe ensures users never hit a broken or not-yet-ready instance.
2. **CI/CD pipelines** (Jenkins, GitHub Actions, GitLab CI — Chapters 06-08) commonly end with a `kubectl set image` or `kubectl apply` step, letting the Deployment's built-in rollout mechanism handle the actual safe transition.
3. **Canary-style testing** can be approximated with careful `maxSurge`/`maxUnavailable` tuning and monitoring rollout status before proceeding, though true canary/progressive delivery is better handled by tools like Argo Rollouts (Chapter 09 GitOps).
4. **Emergency rollback during an incident** — when a bad release causes errors, an on-call engineer's fastest recovery action is often a single `kubectl rollout undo`, reverting to the last known-good ReplicaSet in seconds.
5. **Database schema-compatible rolling deploys** — teams design application changes to be backward-compatible with the previous schema version specifically so that old and new Pods can coexist safely during a `RollingUpdate` window.

---

## 14. Best Practices

- Always define a readiness probe (Chapter 08 Section 4.2) on Deployment-managed Pods — without it, the rollout controller can't reliably tell when a new Pod is actually ready to serve traffic.
- Prefer `RollingUpdate` over `Recreate` unless your application cannot tolerate two versions running simultaneously (e.g., due to an incompatible shared resource).
- Set `maxUnavailable: 0` for user-facing services where you can't tolerate any capacity reduction during rollout (requires `maxSurge` >= 1 to make progress).
- Keep `revisionHistoryLimit` reasonably small (Kubernetes default is 10) to avoid accumulating too many old ReplicaSet objects.
- Use `kubectl rollout status` in CI/CD pipelines to gate subsequent steps on rollout success, not just "the apply command returned."

---

## 15. Common Mistakes

- Forgetting a readiness probe, causing the Deployment to consider Pods "ready" the instant the container process starts, even if the app isn't actually able to serve traffic yet — leading to real user-facing errors during rollout.
- Setting `maxUnavailable` and `maxSurge` both to 0, which makes rollout progress impossible (there's no room to add new Pods or remove old ones).
- Directly editing/deleting a Deployment's underlying ReplicaSet or Pods instead of the Deployment itself — the Deployment controller will fight back and restore its desired state.
- Confusing `kubectl rollout undo` with `kubectl delete` — undo reverts to a previous ReplicaSet/template, it does not delete the Deployment.

---

## 16. Troubleshooting

| Symptom | Likely Cause | Debugging Commands | Fix |
|---|---|---|---|
| Rollout stuck, never completes | New Pods failing readiness probe | `kubectl rollout status`, `kubectl describe pod` | Fix the underlying app issue causing readiness failures |
| Rollout causes a brief outage despite `RollingUpdate` | No readiness probe defined, or `maxUnavailable` too high | `kubectl describe deployment` | Add readiness probe; lower `maxUnavailable` |
| `kubectl rollout undo` doesn't seem to help | Rolled back to a revision that's also broken, or revision history was already pruned | `kubectl rollout history deployment/<name>` | Specify a known-good `--to-revision`, or fix forward |
| Old ReplicaSets accumulating indefinitely | `revisionHistoryLimit` set very high or unset | `kubectl get rs`, check Deployment spec | Set a reasonable `revisionHistoryLimit` |

---

## 17. Comparison Tables

**RollingUpdate vs Recreate:**

| Aspect | RollingUpdate | Recreate |
|---|---|---|
| Downtime | None (with proper readiness probes) | Yes, full gap |
| Two versions run simultaneously | Yes, briefly | Never |
| Use case | Standard web services | Apps that can't tolerate mixed versions |

**ReplicaSet vs Deployment (recap from Chapter 11):**

| Aspect | ReplicaSet | Deployment |
|---|---|---|
| Manages Pod count | Yes | Yes (indirectly, via owned ReplicaSets) |
| Manages rollouts/rollbacks | No | Yes |
| Typical usage | Created automatically by Deployments | Created directly by users |

---

## 18. Memory Tricks

- **"Deployment = the manager, ReplicaSet = the current shift roster, Pod = the worker."** The manager (Deployment) decides when to bring in a new roster (ReplicaSet) and how fast to transition.
- **Runway repaving analogy:** never close all runways (Pods) at once — repave (replace) a little at a time, verify safety (readiness probe), and reopen the old runway (rollback) if something's wrong.
- **maxSurge = "how many extra can I add,"** **maxUnavailable = "how many can I afford to lose"** — both control rollout speed vs. safety.

---

## 19. Interview Questions

**Easy:**
1. What problem does a Deployment solve that a bare ReplicaSet does not?
   *Expected answer:* A ReplicaSet only maintains a fixed replica count and has no way to safely roll out template changes to already-running Pods. A Deployment manages ReplicaSets on your behalf, creating a new one for each template change and gradually shifting traffic from the old to the new, enabling zero-downtime rolling updates and easy rollbacks.

**Medium:**
2. Explain the difference between `maxSurge` and `maxUnavailable`, and how they interact during a rolling update.
   *Expected answer:* `maxSurge` controls how many Pods beyond the desired replica count can exist temporarily during a rollout (extra capacity), while `maxUnavailable` controls how many Pods can be missing/unavailable at once (reduced capacity). Together they determine the rollout's pace and risk profile: a high `maxSurge` with `maxUnavailable: 0` prioritizes zero capacity loss at the cost of temporarily using more resources, while allowing some `maxUnavailable` speeds up rollout but briefly reduces available capacity.

**Hard:**
3. A team's Deployment rollout appears to hang indefinitely at "2 of 3 new Pods ready." Walk through how you'd diagnose and resolve this.
   *Expected answer:* This means one new-version Pod is not passing its readiness probe, so the Deployment controller won't proceed further (it won't scale down more old Pods or consider the rollout complete) — this is a safety feature, not a bug. Diagnosis: `kubectl get pods` to find the not-ready Pod, `kubectl describe pod` to check Events and probe failure details, and `kubectl logs` on that Pod's container to find the actual application error. Common root causes include a missing dependency, a misconfigured readiness probe path/port, or a genuine application bug in the new version. Resolution is either fixing the underlying issue and letting the rollout continue automatically, or issuing `kubectl rollout undo` to revert to the last known-good revision while investigating further.

---

## 20. KCNA Practice Questions

**Q1.** What does a Deployment manage directly?
A. Pods directly, with no intermediate object
B. ReplicaSets, which in turn manage Pods
C. Nodes in the cluster
D. Container images in a registry

**Correct answer: B**
*Explanation:* A Deployment creates and manages ReplicaSets, which then manage the actual Pods — this ownership chain (Deployment → ReplicaSet → Pod) is what enables safe rollouts. A skips the intermediate ReplicaSet layer. C and D are unrelated to what a Deployment manages.

---

**Q2.** What happens when you change the container image in a Deployment's Pod template?
A. Nothing happens until you manually delete the old Pods
B. The Deployment creates a new ReplicaSet and gradually shifts replicas from the old ReplicaSet to the new one
C. The existing ReplicaSet is deleted immediately with no replacement
D. The change is rejected because Deployments are immutable

**Correct answer: B**
*Explanation:* This is the core rolling update mechanism: a new ReplicaSet is created and scaled up while the old one is scaled down, per the configured strategy. A, C, and D misstate this behavior — the Deployment automates the process without immediate deletion or manual intervention.

---

**Q3.** What is the purpose of `maxUnavailable` in a Deployment's rolling update strategy?
A. It limits how many extra Pods can exist temporarily during the rollout
B. It limits how many Pods can be unavailable at once during the rollout
C. It sets the maximum number of replicas the Deployment can ever have
D. It controls how long the rollout can run before timing out

**Correct answer: B**
*Explanation:* `maxUnavailable` caps how much capacity can be missing during a rollout. A describes `maxSurge` instead. C and D describe unrelated, nonexistent controls.

---

**Q4.** How does `kubectl rollout undo` work internally?
A. It deletes the Deployment and recreates it from scratch
B. It scales the previous ReplicaSet back up and the current one back down
C. It restarts all Pods without changing their image
D. It requires manually editing the Deployment YAML file first

**Correct answer: B**
*Explanation:* Rollback reuses the same rolling mechanism in reverse: the previous revision's ReplicaSet is scaled up while the current (broken) one is scaled down. A, C, and D misdescribe the rollback mechanism.

---

**Q5.** Why is a readiness probe important for a Deployment's rolling update?
A. It has no effect on rollouts, only on Services
B. The Deployment controller relies on it to know when a newly created Pod is safe to count as available before proceeding to the next rollout step
C. It determines how many replicas the Deployment will create
D. It is only used during the initial creation of a Deployment, not during updates

**Correct answer: B**
*Explanation:* Without a working readiness probe, the rollout controller can't reliably distinguish "Pod started" from "Pod actually able to serve traffic," risking user-facing errors during rollout. A is false — probes directly affect rollout pacing. C and D misstate the probe's role.

---

**Q6.** How is a new ReplicaSet named when a Deployment triggers a rollout?
A. It reuses the exact same name as the old ReplicaSet
B. Kubernetes computes a hash of the Pod template and appends it to the Deployment name
C. The user must manually name every new ReplicaSet
D. It is named using a sequential integer only, unrelated to the template

**Correct answer: B**
*Explanation:* Kubernetes hashes the Pod template content to generate a suffix (e.g., `web-7d9f8c6b45`), ensuring each distinct template gets a distinct, deterministic ReplicaSet name. A is wrong — reusing the name would collide with the old ReplicaSet. C and D describe naming schemes Kubernetes does not use.

---

**Q7.** What does `revisionHistoryLimit` control?
A. How many rolling updates can run concurrently
B. How many old, scaled-to-zero ReplicaSets are retained for rollback history
C. The maximum number of replicas a Deployment can scale to
D. How long a rollout can take before it is aborted

**Correct answer: B**
*Explanation:* `revisionHistoryLimit` bounds how many old ReplicaSets Kubernetes keeps around (scaled to 0) so `kubectl rollout undo` has revisions to revert to. A, C, and D describe unrelated settings.

---

**Q8.** With `Recreate` strategy, what is the visible behavior during an update?
A. New Pods are created first, then old Pods are terminated, with zero downtime
B. All old Pods are terminated first, then all new Pods are created, causing a full availability gap
C. Old and new Pods run simultaneously indefinitely
D. Only one Pod is ever replaced at a time, regardless of replica count

**Correct answer: B**
*Explanation:* `Recreate` prioritizes never running two versions simultaneously, at the cost of a complete gap in availability while old Pods terminate before new ones start. A describes `RollingUpdate` behavior instead. C and D misdescribe `Recreate`.

---

**Q9.** Why does directly deleting Pods managed by a Deployment fail to permanently remove them?
A. Kubernetes does not allow deleting Pods managed by a Deployment at all
B. The underlying ReplicaSet's reconciliation loop notices the discrepancy and creates replacement Pods to match the desired replica count
C. Deleted Pods are automatically un-deleted by etcd
D. The Deployment must be deleted first before any of its Pods can be removed

**Correct answer: B**
*Explanation:* The ReplicaSet controller (Chapter 11) continuously reconciles actual vs. desired replica count; deleting a Pod it owns just triggers it to create a new one. A is false — deletion is allowed, just not lasting. C and D misstate the mechanism.

---

**Q10.** What is a key limitation of approximating canary releases using only `maxSurge`/`maxUnavailable` tuning, as opposed to a dedicated progressive delivery tool?
A. Deployments cannot perform rolling updates at all
B. Fine-grained traffic-percentage control and automated metric-based promotion/rollback are not natively supported — Deployments only control Pod counts, not traffic splitting
C. `maxSurge` and `maxUnavailable` are deprecated fields
D. Canary releases require a completely different Kubernetes object called a CanarySet

**Correct answer: B**
*Explanation:* A Deployment's rollout mechanism only shifts Pod counts between ReplicaSets — it has no concept of traffic-weighted canary analysis or automated rollback on metric thresholds, which is why tools like Argo Rollouts (Chapter 24 GitOps) exist. A is false. C and D are fabricated.

---

**Q11.** During a rolling update with `maxSurge: 1` and `maxUnavailable: 0` on a Deployment with `replicas: 3`, what is the maximum number of Pods that can exist briefly?
A. 3
B. 4
C. 6
D. 2

**Correct answer: B**
*Explanation:* `maxSurge: 1` allows one extra Pod beyond the desired 3, so up to 4 Pods (3 desired + 1 surge) can exist momentarily while `maxUnavailable: 0` ensures none of the original 3 ever drop below capacity. A ignores the surge allowance. C and D miscalculate the arithmetic.

---

**Q12.** A Deployment's rollout has completed, but the application still throws errors only under production traffic load that wasn't present during readiness checks. What does this reveal about readiness probes?
A. Readiness probes are unnecessary for Deployments
B. A passing readiness probe only confirms the Pod is ready as defined by the probe's specific check — it cannot guarantee correctness under conditions the probe doesn't test
C. This means the Deployment controller is broken
D. Readiness probes always test full production load automatically

**Correct answer: B**
*Explanation:* Readiness probes are only as good as what they check (e.g., an HTTP 200 on `/healthz`) — they cannot catch issues that only manifest under real traffic patterns not exercised by the probe. A is contradicted by the chapter's best practices. C and D are false.

---

**Q13.** Why must application changes rolled out via `RollingUpdate` generally remain backward-compatible with the previous version's data schema?
A. Kubernetes enforces schema compatibility automatically
B. Because old and new Pod versions run simultaneously during the rollout window, both must be able to work correctly with the same underlying data/schema
C. Schema compatibility is unrelated to rollout strategy
D. `RollingUpdate` pauses all database writes until the rollout completes

**Correct answer: B**
*Explanation:* Since `RollingUpdate` intentionally runs mixed versions concurrently, any shared resource (like a database schema) must be compatible with both versions at once, or one version will break. A, C, and D misstate how rollouts interact with external state.

---

**Q14.** What is the effect of setting both `maxSurge: 0` and `maxUnavailable: 0` on a rolling update?
A. The rollout proceeds at maximum speed
B. The rollout cannot make any progress, since there is no room to add new Pods or remove old ones
C. This is the recommended default configuration
D. It forces the Deployment to use the `Recreate` strategy instead

**Correct answer: B**
*Explanation:* With no allowance for extra Pods (`maxSurge: 0`) and no allowance for reduced availability (`maxUnavailable: 0`), the controller has no valid intermediate state to transition through, so the rollout stalls — this is a documented common mistake (Section 15). A, C, and D are incorrect.

---

**Q15.** In the Deployment → ReplicaSet → Pod ownership chain, which object does `kubectl scale deployment/web --replicas=5` directly modify first?
A. The Pods, bypassing the ReplicaSet entirely
B. The Deployment's `spec.replicas` field, which the Deployment controller then propagates to the current ReplicaSet
C. All historical ReplicaSets equally
D. The Node's capacity settings

**Correct answer: B**
*Explanation:* Scaling a Deployment updates its desired replica count, and the Deployment controller then adjusts the currently-active ReplicaSet to match — Pods are only ever affected indirectly through this chain. A skips the ownership chain. C and D are incorrect.

---

**Q16.** Why is `kubectl rollout status` recommended as a CI/CD pipeline gate rather than just checking that `kubectl apply` succeeded?
A. `kubectl apply` always fails if the rollout will fail
B. `kubectl apply` only confirms the manifest was accepted by the API server, not that the actual rollout of new Pods succeeded and became healthy
C. `kubectl rollout status` is required before `kubectl apply` can run
D. They are functionally identical commands

**Correct answer: B**
*Explanation:* `kubectl apply` succeeding just means the API server accepted and stored the new desired state — the actual rollout (creating/health-checking new Pods) happens asynchronously afterward, so pipelines must explicitly wait on `kubectl rollout status` to know if it truly succeeded. A, C, and D are false.

---

**Q17.** What distinguishes a Deployment's revision history from simply keeping old Pods running?
A. Old ReplicaSets are retained (scaled to 0 replicas), not old Pods — Pods themselves are not preserved after scale-down
B. Both old Pods and old ReplicaSets are kept running simultaneously forever
C. Revision history stores only YAML text files on disk, unrelated to any Kubernetes object
D. There is no revision history; every rollback recreates everything from scratch

**Correct answer: A**
*Explanation:* Rollback works by scaling a retained old ReplicaSet back up (which creates fresh Pods from its template) — the original Pods themselves were already terminated during the initial rollout and are not what's "remembered." B, C, and D misstate the mechanism.

---

**Q18.** A Deployment's rollout to a new image version is progressing, but `kubectl get rs` shows the old ReplicaSet still has 2 replicas while the new one has 2 replicas, on a Deployment with `replicas: 3`. What does this indicate?
A. A configuration error — the total should always equal exactly the desired replica count
B. This is expected mid-rollout behavior when `maxSurge` allows temporary extra capacity, since old+new can briefly exceed 3
C. The Deployment has failed and must be deleted
D. Two separate Deployments are being confused with each other

**Correct answer: B**
*Explanation:* Mid-rollout, `maxSurge` permits the combined old+new Pod count to briefly exceed the desired replica count as new Pods come up before old ones are scaled down — this is normal, transient behavior, not an error. A, C, and D misinterpret the transient state.

---

**Q19.** Why does the Deployment controller rely on the kubelet's readiness probe result (Chapter 08) rather than simply checking if the container process has started?
A. Container process start time is a more reliable indicator of application health than readiness checks
B. A container process starting does not guarantee the application inside is actually able to serve traffic correctly — readiness probes test the actual serving condition
C. Kubelet does not report process start status at all
D. The Deployment controller ignores kubelet entirely and uses its own independent health checks

**Correct answer: B**
*Explanation:* Process-start and application-ready are different states — many apps need time to load configuration, warm caches, or connect to dependencies before they can correctly serve requests, which is exactly what a readiness probe verifies. A is backwards. C and D are false.

---

**Q20.** Why is a Deployment described as being "built directly on top of" the ReplicaSet mechanism rather than replacing it?
A. Deployments and ReplicaSets are entirely unrelated, independently-implemented objects
B. A Deployment reuses ReplicaSet's proven replica-count reconciliation logic (Chapter 11) and adds an orchestration layer on top that manages transitions between multiple ReplicaSets over time
C. ReplicaSets are deprecated and only exist for backward compatibility with Deployments
D. A Deployment replaces the need for any ReplicaSet objects to exist in the cluster

**Correct answer: B**
*Explanation:* Rather than reimplementing replica-count management, a Deployment delegates that responsibility to ReplicaSets it creates and owns, focusing its own logic purely on orchestrating rollouts/rollbacks across them — a layered design reusing Chapter 11's mechanism. A, C, and D misstate this relationship.

---

## 21. Chapter Summary (One-Page Revision Sheet)

- A **Deployment** manages ReplicaSets to provide declarative rolling updates and rollbacks, sitting on top of the Deployment → ReplicaSet → Pod ownership chain.
- Every template change creates a **new ReplicaSet**; old ones are kept (scaled to 0) for rollback history.
- **`RollingUpdate`** (default, zero downtime) vs **`Recreate`** (full outage, use only when versions can't coexist).
- **`maxSurge`** = extra Pods allowed; **`maxUnavailable`** = Pods allowed to be missing — both tune rollout speed vs. safety.
- Readiness probes are essential — the rollout controller depends on them to safely pace the update.
- `kubectl rollout undo` reverts to a previous revision using the same rolling mechanism, in reverse.

---

### Chapter Completion Checklist

1. **Topics covered:** Deployment definition, ownership chain, update strategies, maxSurge/maxUnavailable, rollback.
2. **KCNA objectives completed:** The standard, most-used Kubernetes workload controller — builds directly on Chapters 10 (Pods) and 11 (ReplicaSets).
3. **Remaining objectives:** Workloads with different scaling/identity needs — DaemonSets (Chapter 13) and StatefulSets (Chapter 14).
4. **Suggested revision checklist:** Draw the Deployment → ReplicaSet → Pod chain from memory; explain what happens during a template change step by step; explain the role of readiness probes in rollout pacing.
5. **Suggested hands-on exercises:** Complete Lab 2 (rollback) — deliberately deploying a broken image and recovering via `rollout undo` is the single most valuable Deployment exercise for building real incident-response intuition.
6. **Related chapters:** Previous: [11-ReplicaSets](../11-ReplicaSets/README.md). Next: [13-DaemonSets](../13-DaemonSets/README.md) — running exactly one Pod per node instead of a floating replica count.
