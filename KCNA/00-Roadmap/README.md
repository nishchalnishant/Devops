# 00 — Roadmap: How To Use This KCNA Repository

Welcome. This is a complete, from-scratch study system for the **Kubernetes and Cloud Native Associate (KCNA)** certification, offered by the CNCF (Cloud Native Computing Foundation) and the Linux Foundation.

This chapter is your map. Read it fully before touching Chapter 01. It will save you weeks of confusion.

---

## 1. What Is KCNA, Really?

Let's start with the honest picture, not the marketing one.

KCNA is an **entry-level, multiple-choice exam**. It does not test you in a live terminal (unlike CKA/CKAD/CKS, which are hands-on). It tests **understanding of concepts** — architecture, terminology, and "what does this thing do."

Think of it like a **driving theory test** before you're allowed to take the practical driving test (which would be CKA later). You don't drive the car yet. But you must know:

- What a clutch does
- What a traffic light means
- What "give way" means
- Why speed limits exist

KCNA is that, but for Kubernetes and the cloud native ecosystem.

**Exam facts (verify against the official CNCF page before booking, as these can change):**

| Attribute | Detail |
|---|---|
| Format | Multiple choice, proctored, online |
| Duration | 90 minutes |
| Number of questions | ~60 |
| Passing score | Approximately 75% (CNCF uses scaled scoring, so this is a guide, not a guarantee) |
| Validity | 2 years |
| Prerequisites | None — genuinely beginner-friendly |
| Cost | Check CNCF training portal (often bundled with a free retake) |

---

## 2. Why Does This Certification Exist? (Motivation First)

Before Kubernetes existed, "cloud knowledge" was scattered. Someone could be excellent at Docker but know nothing about orchestration. Someone could know AWS deeply but never have touched a container.

The CNCF needed a **common baseline** — a way to say "this person understands the vocabulary and mental model of cloud native systems," the same way a "Network+ " certification proves basic networking literacy before you specialize in Cisco or firewalls.

KCNA exists to:

1. Give beginners a structured on-ramp into Kubernetes (which has a notoriously steep learning curve).
2. Give employers a signal that a candidate understands cloud native fundamentals, even if they haven't run production clusters yet.
3. Act as the **foundation** for harder certifications: CKAD (Application Developer), CKA (Administrator), CKS (Security Specialist), and now also KCSA (Security Associate) and PCA (Prometheus Certified Associate).

---

## 3. The Official KCNA Domains (What You're Actually Tested On)

CNCF publishes an exam curriculum with weighted domains. Approximate weights (always confirm current weights on the CNCF site, they are occasionally revised):

| Domain | Weight | What it covers |
|---|---|---|
| Kubernetes Fundamentals | 46% | Architecture, objects, API, control plane, worker nodes, scheduling |
| Container Orchestration | 22% | Container fundamentals, runtimes, orchestration concepts, network/storage/scaling concepts |
| Cloud Native Architecture | 16% | Autoscaling, serverless, service mesh, community/governance |
| Cloud Native Observability | 8% | Telemetry, Prometheus, cost visibility |
| Cloud Native Application Delivery | 8% | CI/CD, GitOps, IaC |

Notice **Kubernetes Fundamentals is nearly half the exam**. This is why our repo dedicates chapters 06–20 almost entirely to Kubernetes internals — that's where your study time has the highest return.

---

## 4. How This Repository Is Organized

```
KCNA/
├── 00-Roadmap                          ← you are here
├── 01-Introduction-to-Cloud-Native
├── 02-Linux-Basics-for-Kubernetes
├── 03-Networking-Basics
├── 04-Containers
├── 05-Container-Runtimes
├── 06-Kubernetes-Architecture
├── 07-Control-Plane
├── 08-Worker-Nodes
├── 09-Kubernetes-Objects
├── 10-Pods
├── 11-ReplicaSets
├── 12-Deployments
├── 13-DaemonSets
├── 14-StatefulSets
├── 15-Jobs-and-CronJobs
├── 16-Services
├── 17-Ingress-and-Gateway-API
├── 18-Networking
├── 19-Storage
├── 20-Scheduling
├── 21-Security
├── 22-Observability
├── 23-Service-Mesh
├── 24-GitOps
├── 25-Serverless
├── 26-CNCF-Landscape
├── 27-Production-Best-Practices
├── 28-Exam-Preparation
├── 29-Cheat-Sheets
├── 30-Flashcards
├── 31-Practice-Questions
├── 32-Mock-Exams
└── 33-Interview-Questions
```

Each numbered chapter folder contains a `README.md` with the full 21-section deep-dive treatment: motivation, internals, architecture, YAML, commands, labs, comparisons, mistakes, interview Qs, and 20 KCNA-style MCQs.

**Read chapters in order the first time through.** Concepts stack — Chapter 12 (Deployments) assumes you understand Chapter 11 (ReplicaSets), which assumes Chapter 10 (Pods).

---

## 5. Suggested Study Timeline

You have two realistic paths depending on your background.

### Path A — True Beginner (6 weeks, ~1 hour/day)

| Week | Chapters | Focus |
|---|---|---|
| 1 | 00–05 | Cloud native concepts, Linux, networking, containers |
| 2 | 06–09 | Kubernetes architecture, control plane, worker nodes, objects |
| 3 | 10–15 | Workload objects: Pods → CronJobs |
| 4 | 16–20 | Services, Ingress, networking, storage, scheduling |
| 5 | 21–26 | Security, observability, service mesh, GitOps, serverless, CNCF landscape |
| 6 | 27–33 | Best practices, exam prep, cheat sheets, flashcards, mock exams |

### Path B — Already Know Docker/Basic Linux (3 weeks)

| Week | Chapters | Focus |
|---|---|---|
| 1 | 06–15 | Kubernetes architecture + all workload objects |
| 2 | 16–26 | Networking, storage, security, observability, ecosystem |
| 3 | 27–33 | Review, practice questions, 5 mock exams (one every other day) |

---

## 6. How To Actually Study Each Chapter (Method)

This is the single most important section in this roadmap. Follow this method or the repo's depth will overwhelm you.

**Step 1 — Read the motivation section first, always.**
Do not jump to YAML or commands before understanding *why* the object exists. If you memorize `kind: Deployment` without knowing why Deployments exist, you'll forget it in a week.

**Step 2 — Re-explain the concept out loud, in your own words, using an analogy.**
If you can't explain a Pod using the "apartment" analogy (coming in Chapter 10) without looking at your notes, you don't understand it yet — you've only read it.

**Step 3 — Do the hands-on lab.**
Even though KCNA itself is multiple-choice, running the actual `kubectl` commands cements the mental model permanently. Reading about a ReplicaSet healing itself is not the same as watching `kubectl delete pod` and seeing a new one appear in real time.

**Step 4 — Answer the chapter's 20 MCQs *before* checking answers.**
Write down your answer and your confidence (High/Medium/Guess) for each question. This tells you which topics need a second pass.

**Step 5 — Add wrong answers to your personal weak-spot list.**
Keep a running note (in `28-Exam-Preparation`) of every concept you got wrong. Review this list the night before the exam instead of re-reading everything.

**Step 6 — Revisit flashcards (Chapter 30) every 2–3 days.**
Use spaced repetition. Concepts fade fast if not revisited.

---

## 7. Tools You Should Install (Optional But Recommended)

You do not need a Kubernetes cluster to pass KCNA, but hands-on practice massively improves retention.

| Tool | Purpose | Install |
|---|---|---|
| `kubectl` | CLI to talk to a cluster | `brew install kubectl` / package manager |
| `minikube` or `kind` | Local single-node/multi-node cluster | `brew install minikube` or `brew install kind` |
| Docker Desktop / Podman | Container runtime for local dev | Official installers |
| `k9s` | Terminal UI for exploring clusters (optional, very helpful visually) | `brew install k9s` |
| killercoda.com / labs.play-with-k8s.com | Free browser-based Kubernetes sandboxes, no install needed | Just a browser |

If you don't want to install anything, killercoda.com gives you a free, disposable, browser-based cluster — perfect for the hands-on labs in each chapter.

---

## 8. How To Read the Analogies In This Repo

Every hard concept in this repo is explained twice:

1. **Analogy version** — using something you already understand (restaurant, airport, apartment building, post office, hospital, school, library, traffic system, warehouse, factory).
2. **Technical version** — the real Kubernetes terminology, mapped 1:1 onto the analogy.

Example of the pattern you'll see repeatedly:

> **Analogy:** A Pod is like a hotel room. The room can have multiple guests (containers) sharing the same address (IP), same bathroom (network namespace), and same shared table (storage volume). You don't book "a guest," you book "a room."
>
> **Technical:** A Pod is the smallest deployable unit in Kubernetes. It wraps one or more containers that share the same network namespace and can share storage volumes.

Once the analogy clicks, the technical definition becomes obvious rather than something to memorize.

---

## 9. Common Beginner Mistakes (Meta-Level)

These are mistakes people make while **studying** for KCNA, not while using Kubernetes:

1. **Jumping straight to YAML memorization.** KCNA rewards conceptual understanding, not YAML syntax recall (that's more of a CKAD thing). Understand *why* a field exists before memorizing it.
2. **Skipping the "why" and going straight to "what."** This repo is structured to prevent this — don't skip sections even if they feel slow.
3. **Ignoring the non-Kubernetes domains.** Container Orchestration, Cloud Native Architecture, Observability, and App Delivery together are more than half the exam. Don't over-invest 100% of your time in pure Kubernetes objects.
4. **Not doing hands-on labs "because it's multiple choice anyway."** Muscle memory from typing commands creates stronger recall than passive reading, even for a theory exam.
5. **Cramming the week before.** Cloud native concepts interlock. Spaced study across weeks beats a 3-day cram every time.

---

## 10. Chapter Completion Checklist Template

Copy this into your notes for every chapter:

```
Chapter: ___
[ ] Read motivation + historical background
[ ] Explained core concept out loud using an analogy
[ ] Reviewed architecture diagram until I could redraw it from memory
[ ] Completed hands-on lab
[ ] Answered all 20 KCNA-style MCQs (recorded confidence level)
[ ] Reviewed wrong answers and logged weak spots
[ ] Reviewed flashcards for this chapter
```

---

## 11. What's Next

Proceed to **[01-Introduction-to-Cloud-Native](../01-Introduction-to-Cloud-Native/README.md)**. That chapter answers the very first and most important question: *what does "cloud native" even mean, and why did the entire industry shift toward it?*

---

## Chapter Summary (One-Page Revision Sheet)

- KCNA = entry-level, multiple-choice, 90 minutes, ~60 questions, no hands-on terminal component.
- 5 domains: Kubernetes Fundamentals (46%), Container Orchestration (22%), Cloud Native Architecture (16%), Observability (8%), App Delivery (8%).
- This repo has 34 chapters (00–33) covering theory, YAML, commands, labs, comparisons, mistakes, interview Qs, and MCQs for each topic.
- Study method: motivation → analogy → hands-on lab → MCQs → weak-spot list → spaced flashcard review.
- Optional tools: `kubectl`, `minikube`/`kind`, Docker/Podman, `k9s`, or just use killercoda.com for a zero-install sandbox.
- Biggest beginner mistake: over-focusing on Kubernetes YAML syntax while neglecting Observability, App Delivery, and Cloud Native Architecture domains.
