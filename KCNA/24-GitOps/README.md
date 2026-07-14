# 24 — GitOps

## 1. Learning Objectives

By the end of this chapter you will be able to:

- Explain what GitOps is and the problem it solves versus traditional push-based CI/CD.
- Explain the pull-based reconciliation model used by GitOps tools.
- Compare ArgoCD and Flux at a high level.
- Explain the role of Git as the single source of truth.
- Read a basic ArgoCD Application manifest.

**KCNA objectives covered:** Cloud Native Architecture domain — GitOps.

---

## 2. Historical Background

Traditional CI/CD pipelines are **push-based**: a CI system (Jenkins, GitHub Actions) builds an artifact and then directly pushes changes into the target cluster — typically by running `kubectl apply` or `helm upgrade` from within the pipeline, using credentials the pipeline holds for the cluster. As Kubernetes usage matured, teams recognized a security concern: giving every CI pipeline direct write credentials to production clusters is a broad attack surface, and there was often no single, auditable record of exactly what was deployed and when. **GitOps**, popularized by Weaveworks around 2017, flipped this model — instead of pipelines pushing changes into the cluster, an in-cluster agent continuously pulls the desired state from Git and reconciles the cluster to match it.

---

## 3. Motivation: Why Pull-Based Deployment Instead of Push-Based?

**Analogy — The Restaurant's Standing Recipe Book vs a Chef Calling in Ad-Hoc Orders:**
Imagine a restaurant kitchen (the cluster) where, in the push model, an outside dispatcher (CI pipeline) calls in individual orders directly to the kitchen whenever they feel like it, holding a key to walk in and rearrange things themselves. In the GitOps (pull) model, the kitchen instead has a **standing recipe book** (the Git repository) on the counter, and a **head chef inside the kitchen** (the GitOps agent, e.g., ArgoCD) who continuously checks the book and cooks whatever it currently says — no outsider ever needs a key to the kitchen itself, and the book is always the definitive, auditable record of what should be cooking.

### 3.1 How Was This Solved Before GitOps?

Push-based CI/CD pipelines ran deployment commands directly against the cluster using credentials stored in the CI system, applying changes on every pipeline run.

### 3.2 Why Was That Insufficient?

Push-based pipelines require broad, standing cluster credentials inside external CI systems (a large attack surface), provide no continuous drift detection (someone can manually change the cluster and nothing notices), and don't guarantee Git actually reflects the live cluster state at all times.

### 3.3 How GitOps Solves It

An in-cluster **GitOps agent** (e.g., ArgoCD or Flux) continuously pulls the desired state from a Git repository and reconciles the live cluster to match it — no external system needs cluster-write credentials, Git becomes the enforced single source of truth, and any manual drift is automatically detected (and optionally auto-corrected) since the agent constantly compares live state to Git.

---

## 4. Core Concepts

### 4.1 Push vs Pull Deployment Models

| Model | Who Initiates Changes | Credentials Needed Where |
|---|---|---|
| Push-based CI/CD | External CI pipeline applies changes to the cluster | CI system holds cluster-write credentials |
| GitOps (pull-based) | In-cluster agent pulls from Git and reconciles | Only the in-cluster agent needs cluster-write access; Git holds no cluster credentials |

### 4.2 Reconciliation Loop (ties back to Chapter 06)

**Definition:** The GitOps agent runs a continuous reconciliation loop — read desired state from Git, compare to live cluster state, apply any differences — the same controller pattern Kubernetes itself uses internally (Chapter 06), just applied at the level of "what's in Git" instead of "what's in the API server's stored objects."

### 4.3 Git as Single Source of Truth

Every change to the cluster's desired state must go through a Git commit (typically via a pull request), giving a full audit trail of who changed what, when, and why — and enabling rollback via simple Git revert.

---

## 5. Internal Working

```
1. Developer commits a change (e.g., new image tag) to a Git repo
   holding Kubernetes manifests or Helm charts
        ↓
2. GitOps agent (running inside the cluster) polls/watches the Git
   repo for changes
        ↓
3. Agent compares the new desired state (from Git) against the
   current live cluster state
        ↓
4. Agent detects a diff and applies the necessary changes to
   reconcile the cluster to match Git
        ↓
5. Agent continuously repeats this comparison — if someone manually
   changes the live cluster (drift), the agent detects and can
   auto-revert it back to match Git
```

---

## 6. Architecture

```
┌─────────────┐        pulls/watches        ┌─────────────┐
│  Git Repository │ ◄────────────────────── │  GitOps Agent   │
│ (desired state,  │                              │ (ArgoCD/Flux,    │
│  manifests/Helm)│                              │  runs in-cluster)│
└─────────────┘                              └──────┬──────┘
                                                       │ reconciles
                                                       ▼
                                              ┌─────────────┐
                                              │  Live Cluster    │
                                              │  State           │
                                              └─────────────┘
```

---

## 7. Component Breakdown

| Component | Role |
|---|---|
| Git repository | Single source of truth for desired cluster state |
| GitOps agent (ArgoCD/Flux) | In-cluster controller pulling from Git and reconciling live state |
| Application/Kustomization CR | Custom resource defining what Git path/repo maps to what cluster target |
| Sync/reconciliation loop | Continuous comparison and correction process |

---

## 8. Important Terminology

| Term | Meaning |
|---|---|
| GitOps | Operational model using Git as the source of truth, with pull-based, in-cluster reconciliation |
| Push-based CI/CD | Traditional model where an external pipeline applies changes directly to the cluster |
| Reconciliation | Continuous process of comparing desired vs live state and correcting differences |
| Drift | A live cluster state that no longer matches the desired state in Git |
| ArgoCD | Popular GitOps continuous delivery tool for Kubernetes |
| Flux | Popular GitOps toolkit, often used with Kustomize/Helm |

---

## 9. YAML Deep Dive

```yaml
# ArgoCD Application: define what Git source maps to what cluster target
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/example/my-app-manifests.git
    targetRevision: main
    path: k8s/production
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

`prune: true` removes cluster resources no longer present in Git; `selfHeal: true` automatically reverts manual, out-of-band changes to match Git — this is the auto-drift-correction behavior described in Section 3.3.

---

## 10. kubectl Commands

| Command | Purpose | Example |
|---|---|---|
| `kubectl apply -f application.yaml` | Register a new ArgoCD Application | `kubectl apply -f my-app.yaml -n argocd` |
| `kubectl get applications -n argocd` | List ArgoCD-managed applications | `kubectl get applications -n argocd` |
| `argocd app sync <name>` | Manually trigger a sync (ArgoCD CLI) | `argocd app sync my-app` |
| `argocd app diff <name>` | Show diff between Git and live state (ArgoCD CLI) | `argocd app diff my-app` |
| `flux get kustomizations` | List Flux-managed Kustomizations (Flux CLI) | `flux get kustomizations` |

---

## 11. Hands-on Examples

**Lab 1 — Commit a manifest change and observe automatic sync:**
```bash
# Edit replicas in the Git repo, commit and push
git commit -am "scale to 5 replicas" && git push
argocd app get my-app --refresh
# ArgoCD detects the diff and syncs the cluster to 5 replicas
```

**Lab 2 — Manually change a live resource and observe self-heal correction:**
```bash
kubectl scale deployment my-app --replicas=10 -n production
sleep 30
kubectl get deployment my-app -n production
# Replica count reverts back to what's defined in Git (selfHeal: true)
```

**Lab 3 — Roll back via Git revert:**
```bash
git revert HEAD && git push
argocd app sync my-app
# Cluster state reverts to match the previous Git commit
```

---

## 12. Internal Flow

See Section 5 — the essential distinction from ordinary CI/CD automation is that the **reconciliation direction is inverted**: instead of an external system pushing into the cluster, an in-cluster agent pulls from Git, continuously, forever — not just at deploy time.

---

## 13. Real-World Examples

1. **Multi-cluster fleet management** uses one Git repo (or repo-per-cluster pattern) with ArgoCD/Flux instances in each cluster pulling their respective configs, keeping large fleets consistent.
2. **Compliance-heavy environments** rely on GitOps's full audit trail (every change is a reviewed Git commit) to satisfy change-management requirements.
3. **Disaster recovery** is simplified — rebuilding a cluster from scratch just means pointing a fresh GitOps agent at the same Git repo, and it reconciles the entire desired state automatically.
4. **Progressive delivery** tools (e.g., Argo Rollouts) build on top of GitOps to add canary/blue-green deployment strategies driven by the same Git-based desired state.
5. **Drift correction** in production catches and reverts a well-intentioned but undocumented manual `kubectl edit` before it causes long-term configuration divergence from what's actually tested and reviewed.

---

## 14. Best Practices

- Require **pull requests with review** for any change to the GitOps repo — this is what makes the audit trail meaningful, not just the fact that Git is used.
- Separate **application code repos** from **manifest/config repos** so that image builds and deployment configuration have independent, appropriately-scoped review processes.
- Enable **selfHeal** cautiously — great for catching accidental drift, but be aware it will also revert legitimate emergency `kubectl` hotfixes not yet committed to Git.
- Use **automated sync with pruning** so deleted manifests actually remove the corresponding cluster resources, avoiding orphaned objects.

---

## 15. Common Mistakes

- Continuing to use `kubectl apply` directly against production alongside a GitOps agent — this creates constant, confusing drift that the agent will keep trying to revert (if selfHeal is on) or flag (if it's off).
- Not enabling `prune`, leaving deleted-from-Git resources lingering in the cluster indefinitely.
- Storing secrets in plaintext directly in the Git repo — GitOps still requires a proper secrets-management approach (e.g., sealed secrets or an external secret manager), since Git history is effectively permanent.
- Treating GitOps as purely a tooling choice rather than a process discipline — without enforced code review on the manifest repo, much of GitOps's audit-trail value is lost.

---

## 16. Troubleshooting

| Symptom | Likely Cause | Debugging Commands | Fix |
|---|---|---|---|
| Cluster not syncing despite new Git commit | Agent hasn't polled yet, or webhook not configured | `argocd app get <name> --refresh`, check agent logs | Manually trigger refresh/sync; configure Git webhook for faster detection |
| Manual `kubectl` change keeps reverting | `selfHeal: true` is correcting drift back to Git | `argocd app diff <name>` | Commit the intended change to Git instead of editing the cluster directly |
| Deleted manifest still present in cluster | Pruning not enabled | `argocd app get <name>` (check syncPolicy) | Enable `prune: true` in the Application's syncPolicy |
| Sync fails with permission error | GitOps agent's ServiceAccount lacks RBAC permissions (Chapter 21) for the target resource | Check agent's RBAC bindings | Grant the agent's ServiceAccount the needed Role/ClusterRole permissions |

---

## 17. Comparison Tables

| Aspect | Push-based CI/CD | GitOps (pull-based) |
|---|---|---|
| Who applies changes | External CI pipeline | In-cluster agent |
| Cluster credentials location | External CI system | Only inside the cluster |
| Drift detection | None built-in | Continuous, automatic |
| Audit trail | Depends on pipeline logging | Enforced via Git history |

| Tool | Style | Notes |
|---|---|---|
| ArgoCD | UI-driven, Application CRD, strong visualization | Popular for teams wanting a rich dashboard |
| Flux | CLI/GitOps-toolkit driven, Kustomize-native | Popular for lightweight, composable pipelines |

---

## 18. Memory Tricks

- **"Standing recipe book, not a phone-in order"** — Git is the recipe book; the in-cluster agent is the chef who reads and cooks from it continuously.
- **"Pull, don't push — nobody outside the kitchen needs a key."**
- **"selfHeal reverts drift — don't `kubectl edit` production once GitOps is enabled."**

---

## 19. Interview Questions

**Easy:**
1. What is the core difference between push-based CI/CD and GitOps?
   *Expected answer:* In push-based CI/CD, an external pipeline applies changes directly to the cluster using credentials it holds. In GitOps, an in-cluster agent continuously pulls the desired state from a Git repository and reconciles the cluster to match it — the cluster credentials never need to leave the cluster.

**Medium:**
2. What does "drift" mean in a GitOps context, and how does a GitOps agent handle it?
   *Expected answer:* Drift is when the live cluster state no longer matches the desired state declared in Git — for example, due to a manual `kubectl` change. A GitOps agent continuously compares live state to Git and, depending on configuration (e.g., ArgoCD's `selfHeal`), can either just flag the drift or automatically revert the cluster back to match Git.

**Hard:**
3. A team enables `selfHeal: true` and `prune: true` on their ArgoCD Application. During an incident, an engineer runs `kubectl scale` to quickly add replicas as a stopgap, expecting it to hold until they can properly investigate. Fifteen minutes later, the replica count reverts back to the original value, and the incident worsens. Explain what happened and how the team should handle emergency changes under GitOps.
   *Expected answer:* With `selfHeal: true`, ArgoCD continuously reconciles the live cluster back to whatever is declared in Git; since the emergency `kubectl scale` command was never committed to the Git repo, ArgoCD treated it as unwanted drift and reverted it back to the original (insufficient) replica count, undoing the engineer's stopgap fix. Under GitOps, emergency changes should still go through Git — even a fast, minimally-reviewed emergency commit — so that the GitOps agent reconciles *toward* the fix rather than away from it; alternatively, the team could temporarily pause auto-sync/selfHeal on the affected Application during the incident, make the manual change, and then immediately follow up with a proper Git commit before re-enabling it.

---

## 20. KCNA Practice Questions

**Q1.** What is the defining characteristic of the GitOps deployment model?
A. A CI pipeline pushes changes directly into the cluster using stored credentials
B. An in-cluster agent continuously pulls the desired state from Git and reconciles the cluster to match it
C. Deployments are performed manually via `kubectl apply` by an operator
D. Application code and infrastructure manifests must be stored in the same repository

**Correct answer: B**
*Explanation:* GitOps inverts the traditional push model — an in-cluster agent pulls from Git and continuously reconciles state. A describes traditional push-based CI/CD. C and D are not defining characteristics of GitOps.

---

**Q2.** Why is GitOps considered more secure than traditional push-based CI/CD for cluster credentials?
A. GitOps doesn't require any authentication at all
B. Only the in-cluster agent needs cluster-write credentials; external systems never hold them
C. GitOps encrypts all Git commits automatically
D. GitOps eliminates the need for RBAC

**Correct answer: B**
*Explanation:* Because the reconciliation agent runs inside the cluster, external CI systems never need standing cluster-write credentials, shrinking the attack surface. A, C, and D misdescribe GitOps's actual security properties.

---

**Q3.** What does ArgoCD's `selfHeal: true` setting do?
A. Automatically scales Pods based on CPU usage
B. Automatically reverts manual, out-of-band cluster changes back to match the state declared in Git
C. Automatically restarts crashed containers
D. Automatically encrypts Secrets at rest

**Correct answer: B**
*Explanation:* `selfHeal` corrects drift by reconciling any manual cluster changes back to Git's declared state. A describes autoscaling (unrelated), C describes container restarts (kubelet/liveness probes, Chapter 22), and D describes etcd encryption (Chapter 21).

---

**Q4.** What does `prune: true` accomplish in an ArgoCD Application's sync policy?
A. It removes cluster resources that are no longer present in the Git source
B. It deletes old Git commit history
C. It removes unused container images from nodes
D. It disables automatic sync

**Correct answer: A**
*Explanation:* Pruning ensures cluster resources deleted from Git are also removed from the live cluster, avoiding orphaned objects. B, C, and D describe unrelated behaviors.

---

**Q5.** In GitOps, why is Git considered the "single source of truth"?
A. Because Git is faster than the Kubernetes API server
B. Because every change to desired cluster state is expressed as a Git commit, giving a full auditable history and enabling rollback via Git revert
C. Because Git automatically applies changes to the cluster without any agent
D. Because Kubernetes requires Git to function

**Correct answer: B**
*Explanation:* Git's role as the single source of truth comes from every desired-state change being a reviewable, auditable commit — not from any inherent technical property of Git itself. A, C, and D are incorrect characterizations.

---

**Q6.** Using the restaurant analogy from this chapter, what does the Git repository represent?
A. The outside dispatcher calling in orders
B. The standing recipe book the kitchen continuously consults
C. The head chef inside the kitchen
D. The restaurant's customers

**Correct answer: B**
*Explanation:* Git is the standing recipe book — the definitive, auditable record the in-cluster agent (the "chef") continuously reads from. A represents the old push-based dispatcher model, C represents the GitOps agent, and D is unrelated.

---

**Q7.** What security concern with push-based CI/CD motivated the emergence of GitOps?
A. Push-based pipelines are too slow
B. CI pipelines holding broad, standing cluster-write credentials represent a large attack surface
C. Push-based pipelines cannot use YAML manifests
D. Push-based pipelines require Git entirely

**Correct answer: B**
*Explanation:* Giving every external CI pipeline direct cluster-write credentials broadens the attack surface significantly; GitOps eliminates this by keeping credentials in-cluster only. A, C, and D misstate the actual historical motivation.

---

**Q8.** The GitOps reconciliation loop is described as applying which existing Kubernetes pattern at the level of "what's in Git"?
A. The scheduler's bin-packing algorithm
B. The controller pattern (continuous compare-and-correct loop)
C. The admission control chain
D. The DNS resolution process

**Correct answer: B**
*Explanation:* Section 4.2 explicitly ties the GitOps reconciliation loop back to Kubernetes's own internal controller pattern (Chapter 06) — compare desired vs actual state, then correct. A, C, and D are unrelated Kubernetes mechanisms.

---

**Q9.** Per the Architecture diagram, what is the direction of the "pulls/watches" relationship?
A. The Live Cluster State pulls from the GitOps Agent
B. The GitOps Agent pulls/watches the Git Repository
C. The Git Repository pulls from the Live Cluster State
D. There is no directional relationship; it's fully bidirectional

**Correct answer: B**
*Explanation:* The diagram shows the GitOps agent actively pulling/watching the Git repository, then reconciling that desired state onto the live cluster — the inverse of the traditional push direction. A, C, and D misread the diagram's arrows.

---

**Q10.** Per the Troubleshooting table, what is the likely cause when a sync fails with a permission error?
A. The Git repository is unreachable
B. The GitOps agent's ServiceAccount lacks the necessary RBAC permissions for the target resource
C. `prune` is not enabled
D. `selfHeal` is disabled

**Correct answer: B**
*Explanation:* The table attributes sync permission failures to the agent's ServiceAccount lacking sufficient RBAC (Role/ClusterRole) bindings for the resources it's trying to reconcile. A, C, and D map to other, distinct symptoms in the same table.

---

**Q11.** Why should application code repos typically be separated from manifest/config repos, per Best Practices?
A. Git cannot host more than one file type per repo
B. So image builds and deployment configuration can have independent, appropriately-scoped review processes
C. Because ArgoCD forbids using a single repo for both
D. Because Flux requires exactly one repo per cluster

**Correct answer: B**
*Explanation:* Separating these repos allows each to have review processes scoped appropriately to its own risk/change profile (code changes vs. deployment/config changes). A, C, and D are false constraints not stated anywhere in the chapter.

---

**Q12.** What is a key risk of storing secrets in plaintext directly in a GitOps repository?
A. ArgoCD will refuse to sync the Application
B. Git history is effectively permanent, so plaintext secrets remain exposed even if later removed
C. Flux automatically encrypts all repo contents
D. Kubernetes Secrets objects cannot be created via GitOps

**Correct answer: B**
*Explanation:* Because Git history persists indefinitely, a plaintext secret committed once remains recoverable from history even after a later commit removes it — hence the recommendation to use sealed secrets or an external secret manager. A, C, and D are incorrect.

---

**Q13.** What does the `targetRevision: main` field specify in the ArgoCD Application YAML example?
A. The Kubernetes API version to target
B. The Git branch/ref that ArgoCD should track as the desired state
C. The container image tag to deploy
D. The number of replicas to maintain

**Correct answer: B**
*Explanation:* `targetRevision` tells ArgoCD which Git branch, tag, or commit to treat as the current desired state for the `path` specified. A, C, and D describe unrelated fields not shown in this example.

---

**Q14.** In Lab 3, what is the mechanism used to roll back a GitOps-managed deployment?
A. Manually editing the live Deployment object with `kubectl edit`
B. A Git revert followed by a sync, reconciling the cluster back to the previous state
C. Deleting and recreating the ArgoCD Application
D. Disabling `selfHeal` permanently

**Correct answer: B**
*Explanation:* Because Git is the source of truth, rollback is simply a Git revert (undoing the commit) followed by a sync — the agent then reconciles the cluster back to match. A contradicts GitOps discipline (Common Mistakes), and C and D are unrelated/unnecessary.

---

**Q15.** Per Real-World Examples, how does GitOps simplify disaster recovery?
A. It requires manually reapplying every YAML file in order
B. Rebuilding a cluster means pointing a fresh GitOps agent at the same Git repo, which reconciles the entire desired state automatically
C. It automatically backs up etcd every hour
D. It eliminates the need for a Git repository during recovery

**Correct answer: B**
*Explanation:* Since Git fully describes desired state, disaster recovery is as simple as standing up a new agent against the existing repo — it reconciles everything automatically. A, C, and D misdescribe this benefit.

---

**Q16.** Why is continuing to run `kubectl apply` directly against production alongside a GitOps agent considered a common mistake?
A. `kubectl apply` is deprecated
B. It creates constant drift that the agent will keep reverting (if selfHeal is on) or flagging (if off)
C. It causes the Git repository to be deleted
D. It disables the GitOps agent entirely

**Correct answer: B**
*Explanation:* Manual `kubectl apply` changes bypass Git, so the agent treats them as drift — either reverting them automatically or repeatedly flagging them, creating confusion and churn. A, C, and D are false claims.

---

**Q17.** What distinguishes ArgoCD from Flux, per the Comparison Table?
A. ArgoCD is UI-driven with a rich Application CRD and strong visualization; Flux is CLI/toolkit-driven and Kustomize-native
B. Flux requires a graphical dashboard; ArgoCD is CLI-only
C. ArgoCD cannot integrate with Kustomize at all
D. Flux does not support reconciliation loops

**Correct answer: A**
*Explanation:* The table specifically contrasts ArgoCD's dashboard-centric approach against Flux's lightweight, composable, CLI/toolkit-driven style. B reverses the comparison, and C and D are false.

---

**Q18.** Per the Comparison Table contrasting push-based CI/CD and GitOps, what is true of drift detection under push-based CI/CD?
A. It is continuous and automatic
B. There is no built-in drift detection
C. It only runs once per year
D. It is handled by Git hooks automatically

**Correct answer: B**
*Explanation:* Push-based CI/CD has no inherent mechanism to detect that the live cluster has diverged from what was last pushed — this is precisely the gap GitOps's continuous reconciliation fills. A describes GitOps instead; C and D are fabricated.

---

**Q19.** Per the memory tricks in this chapter, what does "Pull, don't push — nobody outside the kitchen needs a key" emphasize?
A. That GitOps requires two separate Git repositories
B. That external systems never need direct cluster-write credentials under the GitOps model
C. That push-based CI/CD is faster than GitOps
D. That Kubernetes clusters should never be accessed remotely at all

**Correct answer: B**
*Explanation:* This mnemonic reinforces the core security benefit: since the in-cluster agent pulls, no external system (CI pipeline) ever needs a cluster-write "key." A, C, and D are unrelated or false.

---

**Q20.** What follow-up action does the hard interview question in this chapter recommend for handling a genuine production emergency under GitOps with `selfHeal: true` enabled?
A. Permanently disable GitOps for that Application
B. Make the manual fix and commit it to Git (or temporarily pause auto-sync), so the agent reconciles toward the fix rather than away from it
C. Delete the Git repository to stop reconciliation
D. Ignore the revert since it will resolve itself eventually

**Correct answer: B**
*Explanation:* The recommended approach is to either commit the emergency fix to Git so the agent reconciles toward it, or temporarily pause auto-sync/selfHeal while making the manual change — otherwise selfHeal will keep undoing the fix. A, C, and D are impractical or incorrect responses.

---

## 21. Chapter Summary (One-Page Revision Sheet)

- **GitOps** inverts traditional push-based CI/CD: instead of external pipelines pushing changes into the cluster, an **in-cluster agent** continuously pulls the desired state from **Git** and reconciles the live cluster to match it.
- This removes the need for external systems to hold cluster-write credentials, and provides continuous, automatic **drift detection** (and optional auto-correction via features like ArgoCD's `selfHeal`).
- Git becomes the **single source of truth**, with every change reviewable and auditable as a commit, and rollback as simple as a Git revert.
- **ArgoCD** (UI-driven, rich visualization) and **Flux** (CLI/toolkit-driven, Kustomize-native) are the two leading GitOps tools.
- Emergency manual changes under GitOps should still go through Git (or pause auto-sync temporarily) — otherwise `selfHeal` will revert them.

---

### Chapter Completion Checklist

1. **Topics covered:** Push vs pull deployment models, reconciliation/drift, ArgoCD Application manifests, ArgoCD vs Flux, selfHeal/prune behavior.
2. **KCNA objectives completed:** Cloud Native Architecture — GitOps.
3. **Remaining objectives:** Serverless — Knative, FaaS, event-driven architectures (Chapter 25).
4. **Suggested revision checklist:** Explain push vs pull models from memory; explain drift and selfHeal; explain why Git is the "single source of truth."
5. **Suggested hands-on exercises:** Complete Lab 2 (manually scale a Deployment and watch selfHeal revert it) — the clearest demonstration of GitOps's continuous reconciliation.
6. **Related chapters:** Previous: [23-Service-Mesh](../23-Service-Mesh/README.md). Next: [25-Serverless](../25-Serverless/README.md) — event-driven, scale-to-zero compute on Kubernetes.
