# Phase 2.5 — GitOps Integration (1–2 Week Deep Dive)

GitOps has moved from nice-to-have to table-stakes in mature DevOps organizations. This phase sits between Phase 2 (CI/CD fundamentals) and Phase 3 (SRE/Observability) because it requires Kubernetes maturity but should be established before you are dealing with production reliability concerns.

## First Principles

**Why GitOps after CI/CD?** Push-based CI/CD (what Phase 2 covers) actively deploys into clusters on a pipeline trigger. Pull-based GitOps has the cluster continuously reconcile its actual state toward the desired state declared in Git. Both are valid; knowing the difference and when each applies is senior-level thinking.

**Why separate from Phase 2?** GitOps requires enough Kubernetes fluency to understand deployment drift, sync status, and self-healing. Engineers who start GitOps before they understand Deployments, Services, and Ingress will misconfigure ArgoCD and not know why.

**What changes operationally:** With push-based CI/CD, a human (or pipeline) decides when to deploy. With GitOps, the cluster continuously decides whether its state matches Git. Rollback is a Git revert. Drift is automatically corrected. Audit trail is the Git log.

## Goal

Understand continuous reconciliation, deployment drift, and multi-environment promotion through a GitOps lens. Be able to explain why GitOps reduces manual deployment risk and design a multi-environment promotion strategy.

## Study Order

1. `../09_ArgoCD_and_GitOps/interview.md` — read the Easy and Medium sections first
2. Install ArgoCD locally (kind cluster): `kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml`
3. Read the Hard section of ArgoCD interview.md after hands-on practice

## What To Master

### GitOps Principles
- Declarative desired state lives in Git — not in pipeline scripts, not in operator knowledge
- Continuous reconciliation: the agent (ArgoCD/Flux) loops indefinitely, comparing actual vs. desired
- Self-healing: if someone `kubectl apply`s a change directly, ArgoCD reverts it on the next sync
- Audit trail: every change to production is a Git commit with author, timestamp, and diff

### ArgoCD Specifics
- Application and AppProject resources
- Sync policy: manual (human approves) vs. automated (ArgoCD syncs on every Git push)
- Auto-pruning: whether ArgoCD deletes Kubernetes resources removed from Git
- App-of-Apps pattern: one root Application that manages all other Applications
- ApplicationSet: generates Applications dynamically from cluster lists or Git directories

### Flux Specifics (for comparison)
- GitRepository and Kustomization resources — more decentralized than ArgoCD
- HelmRelease for Helm-based deployments
- Notification controller for alerting on sync events

### Multi-Environment Promotion
- Branch-per-environment: `main` → dev, `staging` branch → staging, `release/*` → prod
- Directory-per-environment: single branch, `overlays/dev/`, `overlays/prod/` (Kustomize)
- Promotion via pull request: staging sync succeeds → open PR to promote image tag to prod manifest
- Approval gates: branch protection rules require review before merge → before prod sync

## Hands-On Tasks

1. Deploy a simple application to a local Kubernetes cluster using ArgoCD — not `kubectl apply`.
2. Simulate drift: manually edit a Deployment replica count with `kubectl edit`. Observe ArgoCD detect and correct the drift within 3 minutes.
3. Practice rollback: make a bad change, commit it, wait for ArgoCD to sync, then `git revert` and watch ArgoCD re-sync to the previous state.
4. Set up two ArgoCD Applications pointing to `overlays/dev/` and `overlays/prod/` in the same repo. Promote a change from dev to prod by updating the image tag in `overlays/prod/kustomization.yaml` and merging a PR.
5. Compare: deploy the same application using a GitHub Actions push-based workflow. Articulate the operational differences (who decides when to deploy, what happens on drift, how rollback works).

## Exit Criteria

Move to Phase 3 when you can:
- Explain the difference between push-based CI/CD and pull-based GitOps with a concrete example
- Deploy and rollback an application using Git as the sole source of truth
- Detect and explain ArgoCD sync status: `Synced`, `OutOfSync`, `Degraded`
- Design a multi-environment promotion strategy for a team of 10 engineers
- Explain why `--auto-prune` is dangerous for stateful resources (PVCs, CRDs)

## Related Resources

- [ArgoCD and GitOps](../09_ArgoCD_and_GitOps/interview.md)
- [GitHub Actions](../07_GitHub_Actions/interview.md) — compare with push-based pipelines
- [Kubernetes](../05_Kubernetes/interview.md) — prerequisite: understand Deployments and Services first

***

**Previous:** [Phase 2 - Platform and Delivery Core](phase-2-platform-and-delivery.md) | **Next:** [Phase 3 - SRE and Operations](phase-3-sre-and-operations.md)
