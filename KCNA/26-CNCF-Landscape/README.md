# 26 — CNCF Landscape

## 1. Learning Objectives

By the end of this chapter you will be able to:

- Explain what the CNCF is and why it exists.
- Explain the three project maturity levels: Sandbox, Incubating, Graduated.
- Identify major CNCF projects by landscape category (orchestration, observability, service mesh, etc.).
- Explain the relationship between the CNCF, the Linux Foundation, and Kubernetes.
- Recognize graduated projects likely to appear on the KCNA exam.

**KCNA objectives covered:** Cloud Native Architecture domain — CNCF Landscape; ties together concepts from every prior chapter.

---

## 2. Historical Background

Kubernetes was donated by Google to a newly-formed **Cloud Native Computing Foundation (CNCF)** in 2015, under the umbrella of the **Linux Foundation**, specifically to ensure Kubernetes (and the broader cloud native ecosystem growing around it) would be governed neutrally, by a multi-vendor community, rather than controlled by any single company. As the ecosystem exploded — dozens of tools for networking, storage, observability, security, and more, all needing to interoperate with Kubernetes — the CNCF began formally hosting many of these projects, and introduced a **maturity model** (Sandbox → Incubating → Graduated) to signal each project's stability, adoption, and governance maturity to newcomers trying to navigate an increasingly crowded landscape.

---

## 3. Motivation: Why Does the Cloud Native World Need a Neutral Foundation and a Maturity Model?

**Analogy — The School's Accreditation Board:**
Imagine trying to pick a school for your child from thousands of unranked options with no accreditation system — you'd have no quick way to judge which are well-established versus brand new and unproven. The CNCF acts like an **accreditation board** for cloud native projects: it doesn't build the projects itself, but it hosts them under neutral governance and assigns each a maturity level, so newcomers can quickly judge "is this experimental (**Sandbox**), maturing with real adoption (**Incubating**), or a proven, widely-adopted standard (**Graduated**)?"

### 3.1 How Was This Solved Before the CNCF?

Cloud infrastructure tools were typically developed and controlled by single vendors, with unclear governance and no shared, neutral signal of a project's maturity or community backing.

### 3.2 Why Was That Insufficient?

Single-vendor control created risk of vendor lock-in and inconsistent quality signals, making it hard for adopters to judge which of many competing tools were trustworthy, well-governed, and likely to be maintained long-term.

### 3.3 How the CNCF Solves It

The CNCF hosts cloud native projects under **neutral, multi-vendor governance** (part of the Linux Foundation) and assigns each a clear **maturity level**, giving the community a shared, trusted signal of a project's stability and adoption — while donating projects like Kubernetes retain open governance rather than single-company control.

---

## 4. Core Concepts

### 4.1 CNCF Project Maturity Levels

| Level | Meaning | Example Projects |
|---|---|---|
| Sandbox | Early-stage, experimental; minimal requirements to join | Many early-stage projects (varies over time) |
| Incubating | Demonstrated adoption, growing community, meets more rigorous requirements | Argo, OpenTelemetry, Linkerd (at various points) |
| Graduated | Highest maturity — proven, widely adopted, sustainable governance, meets the strictest requirements | Kubernetes, Prometheus, Envoy, containerd, Helm, etcd, CoreDNS, Istio, Argo (varies; check current CNCF landscape for exact current status) |

### 4.2 CNCF Landscape Categories

The CNCF Landscape organizes projects by function — a few categories directly map to chapters already covered in this guide:

| Category | Maps to Chapter | Example Projects |
|---|---|---|
| Orchestration & Scheduling | 06-Kubernetes-Architecture, 20-Scheduling | Kubernetes |
| Container Runtime | 05-Container-Runtimes | containerd, CRI-O |
| Observability | 22-Observability | Prometheus, OpenTelemetry, Fluentd |
| Service Mesh | 23-Service-Mesh | Istio, Linkerd, Envoy |
| Continuous Delivery/GitOps | 24-GitOps | ArgoCD, Flux |
| Serverless | 25-Serverless | Knative |
| Networking | 18-Networking | Cilium, Calico, CoreDNS |
| Storage | 19-Storage | Rook, Longhorn |
| Security | 21-Security | Falco, OPA |

### 4.3 CNCF vs Linux Foundation vs Kubernetes

The **Linux Foundation** is the umbrella non-profit; the **CNCF** is one of its foundations, focused specifically on cloud native technologies; **Kubernetes** is the CNCF's original and flagship graduated project, but the CNCF now hosts well over a hundred additional projects across the landscape.

---

## 5. Internal Working

```
1. A project applies to join the CNCF, typically starting at the
   Sandbox stage (lightweight entry requirements)
        ↓
2. As the project demonstrates growing adoption, a healthy
   multi-vendor contributor base, and meets governance/security
   criteria, it can apply to move to Incubating
        ↓
3. With sustained adoption, broad production usage across multiple
   organizations, and the strictest governance/security/documentation
   requirements met, a project can graduate to Graduated status
        ↓
4. The CNCF Technical Oversight Committee (TOC) reviews and approves
   movement between maturity levels
```

---

## 6. Architecture

```
                 ┌─────────────────┐
                 │  Linux Foundation    │
                 └────────┬────────┘
                           │
                 ┌─────────────────┐
                 │        CNCF            │
                 └────────┬────────┘
     ┌───────────────┼───────────────┐
     ▼                       ▼                       ▼
┌─────────┐        ┌─────────┐        ┌─────────┐
│ Sandbox     │        │ Incubating  │        │ Graduated   │
│ (early-      │        │ (adoption   │        │ (proven,       │
│  stage)       │ ──►  │  growing)    │ ──►  │  widely used)  │
└─────────┘        └─────────┘        └─────────┘
```

---

## 7. Component Breakdown

| Component | Role |
|---|---|
| CNCF | Neutral foundation hosting cloud native projects under the Linux Foundation |
| Technical Oversight Committee (TOC) | Reviews and approves project maturity-level changes |
| CNCF Landscape | Public map/catalog organizing hosted (and broader ecosystem) projects by category |
| Maturity Levels | Sandbox, Incubating, Graduated — signal a project's stability and adoption |

---

## 8. Important Terminology

| Term | Meaning |
|---|---|
| CNCF | Cloud Native Computing Foundation — neutral home for cloud native open-source projects |
| Linux Foundation | Umbrella non-profit organization that the CNCF operates under |
| Sandbox | Earliest CNCF project maturity level |
| Incubating | Middle CNCF project maturity level, demonstrating real adoption |
| Graduated | Highest CNCF project maturity level, proven and widely adopted |
| CNCF Landscape | Categorized visual map of cloud native projects and products |
| TOC (Technical Oversight Committee) | CNCF body overseeing project maturity and technical direction |

---

## 9. YAML Deep Dive

This chapter is conceptual/organizational rather than configuration-driven — there is no single YAML manifest representing "the CNCF landscape." Instead, this section highlights how a project's CNCF status is often referenced in real-world tooling documentation and decision-making, e.g., a note in an internal architecture doc:

```yaml
# Example: internal tooling-decision notes (not a Kubernetes manifest)
decision: "adopt-service-mesh"
candidates:
  - name: Istio
    cncf_status: Graduated
  - name: Linkerd
    cncf_status: Graduated
rationale: >
  Prefer Graduated-status projects for production adoption due to
  proven stability, broad community support, and mature governance.
```

---

## 10. kubectl Commands

Not directly applicable — this chapter concerns ecosystem/foundation structure rather than cluster-level objects. No new `kubectl` commands are introduced here; refer to prior chapters for the specific tool being evaluated (e.g., Chapter 23 for Istio/Linkerd commands, Chapter 24 for ArgoCD/Flux commands).

---

## 11. Hands-on Examples

**Lab 1 — Explore the live CNCF Landscape:**
Visit the CNCF Landscape website and locate the Orchestration & Scheduling, Observability, and Service Mesh categories; identify which projects in each are marked Graduated versus Incubating versus Sandbox.

**Lab 2 — Map this guide's chapters to CNCF landscape categories:**
For each of Chapters 18-25 in this guide, write down which CNCF landscape category it corresponds to (see the table in Section 4.2) and name at least one Graduated project in that category.

**Lab 3 — Trace a project's maturity history:**
Pick one project referenced in this guide (e.g., Argo, Linkerd, or OpenTelemetry) and research its maturity progression (Sandbox → Incubating → Graduated) and approximate dates, to build intuition for how the model works in practice.

---

## 12. Internal Flow

See Section 5 — the maturity model is fundamentally a **trust-signaling pipeline**: projects start with low barriers to entry (Sandbox) and progressively prove sustained adoption and governance rigor to earn higher trust signals (Incubating, then Graduated), reviewed at each stage by the CNCF's TOC.

---

## 13. Real-World Examples

1. **Kubernetes** itself is the CNCF's original graduated project and remains the foundation's flagship.
2. **Prometheus** (Chapter 22) was the CNCF's second graduated project, cementing it as the de facto cloud native metrics standard.
3. **Enterprises evaluating new tooling** often use CNCF maturity level as one practical filter — favoring Graduated projects for production-critical adoption, and being more cautious with Sandbox projects.
4. **containerd and CRI-O** (Chapter 05) are both CNCF-hosted graduated container runtimes, reflecting the ecosystem's move away from single-vendor runtime control.
5. **Envoy** (Chapter 23) graduated as the proxy underlying Istio and other service mesh implementations, demonstrating how landscape categories often interlock (a graduated proxy underlying a graduated/incubating mesh).

---

## 14. Best Practices

- Use **CNCF maturity level as one signal among several** (not the only one) when evaluating a new tool — also consider your team's specific needs, community activity, and documentation quality.
- Regularly check the **live CNCF Landscape**, since maturity levels and categories change over time as projects evolve.
- Recognize that a **Sandbox** project isn't necessarily bad — many started there before becoming today's most widely-used tools — but it does carry more adoption risk.
- When studying for KCNA, focus on knowing the **graduated projects** most likely to be tested (Kubernetes, Prometheus, Envoy, containerd, CoreDNS, etcd, Helm, Argo, Istio) and roughly which category each belongs to.

---

## 15. Common Mistakes

- Assuming CNCF hosting alone implies official Kubernetes endorsement or built-in integration — CNCF projects are independently governed, not bundled into Kubernetes itself.
- Treating maturity level as a strict quality ranking rather than primarily a signal of adoption/governance maturity — a Sandbox project can still be technically excellent.
- Confusing the CNCF (cloud native focus) with the broader Linux Foundation (much broader scope, many unrelated foundations).
- Assuming the landscape is static — projects move between maturity levels, and even archived/retired projects exist; always verify current status rather than relying on memorized snapshots.

---

## 16. Troubleshooting

This chapter is conceptual, so "troubleshooting" here means navigating confusion about ecosystem structure rather than debugging a running system:

| Confusion | Clarification |
|---|---|
| "Is Kubernetes part of the CNCF, or is the CNCF part of Kubernetes?" | Kubernetes is a project hosted by the CNCF, not the reverse — the CNCF is the neutral organizational home. |
| "Does Graduated mean 'the best tool for every use case'?" | No — it signals proven adoption/governance maturity, not that it's the only or best choice for a given need. |
| "Are all service mesh tools CNCF-hosted?" | No — the landscape includes both CNCF-hosted projects and other ecosystem products/tools that are cataloged but not formally hosted. |

---

## 17. Comparison Tables

| Maturity Level | Adoption Bar | Governance Rigor | Risk Profile |
|---|---|---|---|
| Sandbox | Low | Minimal | Higher (early-stage, may not survive) |
| Incubating | Moderate-to-high | Moderate | Medium |
| Graduated | High, broad, sustained | Strictest | Lowest (proven, widely relied upon) |

| Organization | Scope |
|---|---|
| Linux Foundation | Broad umbrella non-profit hosting many unrelated foundations |
| CNCF | Linux Foundation's cloud-native-focused foundation |

---

## 18. Memory Tricks

- **"School accreditation levels"** — Sandbox (new school, unranked), Incubating (accredited, growing), Graduated (established, trusted).
- **"CNCF hosts, it doesn't build."**
- **"Kubernetes, Prometheus, Envoy — the graduated trio most likely on the exam."**

---

## 19. Interview Questions

**Easy:**
1. What are the three CNCF project maturity levels, in order?
   *Expected answer:* Sandbox (earliest, experimental stage), Incubating (demonstrated growing adoption and governance maturity), and Graduated (highest maturity — proven, widely adopted, strictest governance requirements).

**Medium:**
2. What is the relationship between the Linux Foundation, the CNCF, and Kubernetes?
   *Expected answer:* The Linux Foundation is the broad umbrella non-profit organization; the CNCF is one specific foundation under the Linux Foundation, focused on cloud native technologies; Kubernetes is the CNCF's original and flagship graduated project, but the CNCF hosts many other projects across categories like observability, service mesh, and storage.

**Hard:**
3. A team is choosing between two competing open-source tools for a new production workload: one is CNCF Graduated with a smaller but very active community, and the other is CNCF Sandbox with flashier marketing and more GitHub stars. How should the team weigh CNCF maturity level against these other signals?
   *Expected answer:* CNCF maturity level is a useful proxy for adoption breadth and governance rigor, but it shouldn't be the sole deciding factor — Graduated status specifically signals that a project has met strict, vetted criteria around sustained multi-organization adoption, security practices, and neutral governance, which matters a great deal for production risk. However, GitHub stars and marketing visibility are weaker, more easily-gamed signals that don't necessarily reflect production-readiness or long-term maintenance commitment. The team should weigh CNCF maturity level heavily as a risk-reduction signal for production use, while still evaluating the Sandbox project's actual technical fit, documentation quality, and real (not just perceived) community activity — a Sandbox project isn't automatically wrong for production, but it does carry more inherent adoption risk that should be consciously accepted, not overlooked in favor of surface-level popularity metrics.

---

## 20. KCNA Practice Questions

**Q1.** What are the three CNCF project maturity levels?
A. Alpha, Beta, Stable
B. Sandbox, Incubating, Graduated
C. Draft, Review, Released
D. Experimental, Production, Deprecated

**Correct answer: B**
*Explanation:* Sandbox, Incubating, and Graduated are the CNCF's official maturity levels. The other options use plausible-sounding but incorrect terminology.

---

**Q2.** Which organization is the CNCF a part of?
A. The Apache Software Foundation
B. The Linux Foundation
C. The Kubernetes project itself
D. The Open Source Initiative

**Correct answer: B**
*Explanation:* The CNCF operates under the Linux Foundation umbrella. A and D are unrelated foundations, and C is backwards — Kubernetes is hosted by the CNCF, not the other way around.

---

**Q3.** Which of these is a Graduated CNCF project most closely associated with metrics-based observability (Chapter 22)?
A. Envoy
B. Prometheus
C. Argo
D. Falco

**Correct answer: B**
*Explanation:* Prometheus is the CNCF's flagship graduated metrics/observability project. Envoy (A) is a proxy (service mesh, Chapter 23), Argo (C) is GitOps/workflows (Chapter 24), and Falco (D) is runtime security (Chapter 21).

---

**Q4.** What does it mean for a CNCF project to reach "Graduated" status?
A. The project is no longer actively maintained
B. The project has demonstrated broad, sustained adoption and meets the strictest governance/security requirements
C. The project has been merged directly into Kubernetes core
D. The project is only available to CNCF member companies

**Correct answer: B**
*Explanation:* Graduated status reflects proven, sustained adoption and the highest governance bar. A is the opposite of the intended meaning, and C and D misdescribe how CNCF hosting and graduation work.

---

**Q5.** Which of the following best describes the purpose of the CNCF Landscape?
A. A single vendor's product catalog
B. A categorized map of cloud native projects and products to help users navigate the ecosystem
C. A list of deprecated Kubernetes APIs
D. A Kubernetes internal component responsible for scheduling

**Correct answer: B**
*Explanation:* The CNCF Landscape organizes the sprawling cloud native ecosystem into categories, helping adopters navigate available tools. A, C, and D all misdescribe its actual purpose.

---

**Q6.** Which body reviews and approves a CNCF project's movement between maturity levels?
A. The Technical Oversight Committee (TOC)
B. kube-scheduler
C. The etcd quorum
D. A project's individual maintainer, unilaterally

**Correct answer: A**
*Explanation:* The TOC formally reviews and approves maturity-level transitions. B and C are unrelated Kubernetes internals, and D contradicts the CNCF's governed, reviewed process.

---

**Q7.** Which CNCF Landscape category does Istio, Linkerd, and Envoy belong to, per this chapter's category table?
A. Storage
B. Service Mesh
C. Serverless
D. Continuous Delivery/GitOps

**Correct answer: B**
*Explanation:* Istio, Linkerd, and Envoy are listed under Service Mesh (mapping to Chapter 23). A, C, and D map to different categories (Storage → Rook/Longhorn, Serverless → Knative, GitOps → ArgoCD/Flux).

---

**Q8.** Which two projects does this chapter identify as CNCF-hosted container runtimes?
A. Prometheus and Grafana
B. containerd and CRI-O
C. Istio and Linkerd
D. ArgoCD and Flux

**Correct answer: B**
*Explanation:* containerd and CRI-O are the graduated container runtimes referenced (Chapter 05). A is observability tooling, C is service mesh, and D is GitOps tooling.

---

**Q9.** What does this chapter identify as the risk profile of adopting a Sandbox-stage project?
A. Zero risk — Sandbox projects are as safe as Graduated ones
B. Higher risk, since Sandbox is early-stage and may not survive long-term
C. Lower risk than Graduated projects
D. Risk cannot be assessed for Sandbox projects

**Correct answer: B**
*Explanation:* The comparison table explicitly marks Sandbox's risk profile as "Higher (early-stage, may not survive)." A, C, and D contradict this stated risk grading.

---

**Q10.** Per this chapter's common mistakes, what is wrong with assuming CNCF hosting implies official Kubernetes endorsement or built-in integration?
A. Nothing is wrong with that assumption
B. CNCF projects are independently governed, not bundled into Kubernetes itself
C. CNCF hosting means a project is automatically installed with every cluster
D. CNCF hosting means the project replaces kubectl

**Correct answer: B**
*Explanation:* Being CNCF-hosted doesn't mean a project ships with or is endorsed as part of Kubernetes core — each project remains independently governed. A contradicts the chapter's explicit warning, and C/D are fabricated claims.

---

**Q11.** Which project does this chapter call out as the CNCF's second graduated project, cementing it as the de facto cloud native metrics standard?
A. Envoy
B. Prometheus
C. Kubernetes
D. Helm

**Correct answer: B**
*Explanation:* Section 13 explicitly states Prometheus was the CNCF's second graduated project. A is a proxy, C was the first graduated project, and D is a package manager.

---

**Q12.** According to this chapter's best practices, how should CNCF maturity level be used when evaluating a new tool?
A. As the sole, final deciding factor with no other considerations
B. As one signal among several, alongside team needs, community activity, and documentation quality
C. It should be ignored entirely since it's outdated the moment it's published
D. Only Graduated projects should ever be considered, regardless of use case

**Correct answer: B**
*Explanation:* The chapter explicitly recommends treating maturity level as one signal among several, not the only one. A and D overstate its role, and C dismisses a genuinely useful signal.

---

**Q13.** Which category in the CNCF Landscape does Cilium and Calico belong to, per the mapping table in this chapter?
A. Networking
B. Security
C. Observability
D. Orchestration & Scheduling

**Correct answer: A**
*Explanation:* Cilium and Calico are listed under Networking (mapping to Chapter 18). B, C, and D correspond to different categories (Falco/OPA, Prometheus/OpenTelemetry/Fluentd, Kubernetes itself).

---

**Q14.** What is the CNCF Landscape's Continuous Delivery/GitOps category's example projects, and which chapter do they map to?
A. Rook and Longhorn, mapping to Chapter 19
B. ArgoCD and Flux, mapping to Chapter 24
C. Prometheus and OpenTelemetry, mapping to Chapter 22
D. Knative, mapping to Chapter 25

**Correct answer: B**
*Explanation:* ArgoCD and Flux are the example GitOps projects, mapping to Chapter 24. A, C, and D describe other categories (Storage, Observability, Serverless respectively).

---

**Q15.** A team notices a project they use has moved from Incubating to Graduated status. What does this transition most directly signal, per this chapter?
A. The project's source code license has changed
B. The project has demonstrated sustained, broad adoption and met the strictest governance/security requirements
C. The project is now maintained exclusively by the CNCF staff
D. The project has been deprecated

**Correct answer: B**
*Explanation:* Graduation reflects sustained adoption and rigorous governance/security vetting, as described in Sections 4.1 and 5. A, C, and D are unrelated or contradictory claims.

---

**Q16.** Why does this chapter caution against treating the CNCF Landscape as static?
A. Because the landscape website is frequently down
B. Because projects move between maturity levels over time, and some are archived/retired, so memorized snapshots can become outdated
C. Because the CNCF deletes the landscape and rebuilds it annually
D. Because maturity levels are assigned randomly

**Correct answer: B**
*Explanation:* Common Mistakes explicitly warns that projects change maturity level and status over time, so current status should always be verified rather than relying on a memorized snapshot. A, C, and D are fabricated reasons.

---

**Q17.** Which of the following correctly distinguishes the Linux Foundation from the CNCF?
A. They are the same organization under different names
B. The Linux Foundation is a broad umbrella non-profit hosting many unrelated foundations; the CNCF is its cloud-native-focused foundation
C. The CNCF governs the Linux Foundation
D. The Linux Foundation only hosts Kubernetes-related projects

**Correct answer: B**
*Explanation:* The comparison table in Section 17 draws exactly this distinction — Linux Foundation as broad umbrella, CNCF as its cloud-native-specific foundation. A, C, and D misstate the relationship.

---

**Q18.** Per this chapter's memory trick, how should you remember the difference between Sandbox and Graduated projects?
A. "Sandbox is deprecated, Graduated is experimental"
B. Like school accreditation levels — Sandbox is an unranked new school, Graduated is established and trusted
C. Sandbox projects always have more GitHub stars than Graduated ones
D. There's no meaningful difference between them

**Correct answer: B**
*Explanation:* Section 18's memory trick uses the school-accreditation analogy: Sandbox (new, unranked) versus Graduated (established, trusted). A, C, and D misstate or invert the analogy.

---

**Q19.** Which Graduated project does this chapter identify as the proxy underlying Istio and other service mesh implementations?
A. Envoy
B. CoreDNS
C. Helm
D. etcd

**Correct answer: A**
*Explanation:* Section 13 identifies Envoy as the graduated proxy underlying Istio and other meshes, illustrating how landscape categories interlock. B, C, and D serve unrelated roles (DNS, package management, key-value store).

---

**Q20.** A team is deciding whether a tool's CNCF Sandbox status alone should disqualify it from a new internal project. Based on this chapter's guidance, what is the most accurate conclusion?
A. Sandbox status automatically disqualifies any serious consideration
B. Sandbox isn't necessarily bad — many widely-used tools started there — but it does carry more adoption risk that should be weighed consciously
C. Sandbox status means the project is guaranteed to graduate within a year
D. Sandbox and Graduated carry identical risk profiles

**Correct answer: B**
*Explanation:* The chapter explicitly states Sandbox isn't necessarily bad since many top tools started there, but it does carry more adoption risk. A overstates the disqualification, and C/D contradict the stated risk model.

---

## 21. Chapter Summary (One-Page Revision Sheet)

- The **CNCF** (Cloud Native Computing Foundation), under the **Linux Foundation**, is the neutral, multi-vendor home for cloud native projects — including Kubernetes, its original flagship project.
- Projects progress through three **maturity levels**: **Sandbox** (early-stage) → **Incubating** (growing adoption) → **Graduated** (proven, widely adopted, strictest governance).
- The **CNCF Landscape** categorizes projects by function — orchestration, observability, service mesh, GitOps, serverless, networking, storage, security — directly mapping onto Chapters 18-25 of this guide.
- Key Graduated projects to know for KCNA: **Kubernetes, Prometheus, Envoy, containerd, CoreDNS, etcd, Helm** (and others whose status should be verified against the current live landscape, since it evolves).
- Maturity level is a useful, but not sole, signal — always weigh it alongside actual technical fit and real community activity.

---

### Chapter Completion Checklist

1. **Topics covered:** CNCF's role and structure, Linux Foundation relationship, Sandbox/Incubating/Graduated maturity levels, CNCF Landscape categories mapped to prior chapters.
2. **KCNA objectives completed:** Cloud Native Architecture — CNCF Landscape (ties together all Cloud Native Architecture domain chapters).
3. **Remaining objectives:** Production Best Practices — capacity planning, upgrade strategies, cluster hardening (Chapter 27).
4. **Suggested revision checklist:** Recite the three maturity levels in order; name at least one Graduated project per major landscape category; explain the CNCF/Linux Foundation/Kubernetes relationship.
5. **Suggested hands-on exercises:** Complete Lab 1 (browse the live CNCF Landscape) to build real familiarity with current project categorization and status.
6. **Related chapters:** Previous: [25-Serverless](../25-Serverless/README.md). Next: [27-Production-Best-Practices](../27-Production-Best-Practices/README.md) — real-world cluster operation and hardening practices.
