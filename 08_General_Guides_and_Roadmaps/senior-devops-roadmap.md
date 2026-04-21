# Senior DevOps Engineer Roadmap (7 YOE → Staff / Principal)

This roadmap picks up where the 11-step foundational roadmap ends. Having mastered the core tools (Docker, Kubernetes, Terraform, and CI/CD pipelines), you now shift your mental model from **"deploying things"** to **"designing and governing the systems that deploy things"**.

---

## The Mindset Shift at 7 YOE

| Mid-Level (3-5 YOE) | Senior / Staff (7+ YOE) |
|---|---|
| Writes a CI/CD pipeline for one team | Designs the templated pipeline system used by 50 teams |
| Deploys an AKS cluster | Provisions cluster fleets using Cluster API |
| Configures a Prometheus alert | Designs the SLO framework and burn-rate strategy |
| Fixes a Terraform bug | Designs the state isolation and GitOps governance model |
| Attends post-mortems | Runs post-mortems and identifies systemic process gaps |

---

## Phase A: Platform Engineering

Platform Engineering is the discipline of building an internal product for developers — often called an **Internal Developer Platform (IDP)**. The platform team is not a gatekeeper; it is the enabler.

### What to Master
- **Internal Developer Platforms (IDPs):** Backstage (CNCF project by Spotify). Building a software catalog, service templates (Golden Paths), and self-service portals.
- **Crossplane:** Kubernetes-native infrastructure provisioning. Instead of writing Terraform, platform teams expose custom CRDs (e.g., `kind: PostgresDatabase`) that developers use to request infrastructure without writing a single HCL line.
- **Golden Paths:** Standardized, opinionated starting templates for microservices, CI pipelines, and infrastructure. Engineers can choose to deviate but must explicitly justify it.
- **DORA & SPACE Metrics:** Define what "good" looks like for your platform's customers (the developers):
  - *DORA:* Deployment Frequency, Lead Time for Changes, Change Failure Rate, Time to Restore.
  - *SPACE:* Satisfaction, Performance, Activity, Communication, Efficiency.

### Key Interview Narratives
- "I shifted our team's identity from the team that blocked deployments to the team that made deployments invisible for developers."
- "I reduced our onboarding time for new microservices from 3 weeks to 2 days by building a service template in Backstage."

---

## Phase B: Enterprise Architecture at Scale

### Multi-Region Active-Active
- **Pattern:** Two or more regions simultaneously serve live traffic. There is no "standby" region — all regions are active.
- **Components:** Azure Front Door / AWS Global Accelerator for traffic steering, SQL auto-failover groups, conflict-free replicated data types (CRDTs) for eventually consistent state.
- **The Hard Problem:** Write conflicts in a distributed database. Most architectures accept **read anywhere, write to primary region** rather than true active-active writes for databases.

### Cell-Based Architecture
Replace one large cluster with N smaller "cells", each serving a fixed subset of customers. A failure in Cell 3 only impacts Cell 3's customers (5-10% of traffic), not the entire service.
- Cells share nothing: separate databases, queues, and compute.
- Traffic routing via a "router tier" that maps tenant IDs to cell assignment.

### Zero-Trust Networking
- **Principle:** Every request, internal or external, must be authenticated and authorized. The internal network is not trusted.
- **Implementation:** mTLS between all microservices (via Istio/Linkerd), workload identity (SPIFFE/SPIRE), and deny-all NetworkPolicies with explicit allow rules only.

---

## Phase C: DevSecOps at Enterprise Scale

### Supply Chain Security (SLSA Framework)
The SolarWinds and Log4j attacks were supply chain attacks. SLSA (pronounced "salsa") is a framework of standards to ensure your software hasn't been tampered with anywhere between "developer laptop" and "production cluster".

- **SLSA Level 1:** CI/CD system generates provenance attestations. The build process is scripted.
- **SLSA Level 2:** The build runs on a hosted CI system (not the developer's machine). Provenance is signed.
- **SLSA Level 3:** The CI system has strong security guarantees. Build environment is hermetic (no internet access during build).

### Policy-as-Code at Scale (OPA/Kyverno)
- **Mutation Policies:** Automatically inject security labels, tolerations, and sidecar proxies without requiring developers to know about them.
- **Validation Policies:** Reject pods that run as root, use `latest` image tags, or lack resource limits.
- **Generation Policies:** When a new Namespace is created, automatically provision the `NetworkPolicy`, `LimitRange`, and `RoleBinding` for that namespace's team.

---

## Phase D: FinOps (Cloud Financial Engineering)

At 7 YOE, you own the cloud bill. FinOps is the discipline of making engineering decisions with financial accountability.

### Key Concepts
- **Showback:** Reporting how much each team/service costs, without billing them.
- **Chargeback:** Actually billing internal teams for their cloud spend (requires Kubernetes label-based cost attribution).
- **Spot/Preemptible Fleet Architecture:** Running stateless workloads on Spot Instances (70% cheaper). The architecture must gracefully handle 2-minute eviction notices via the Kubernetes `PodDisruptionBudget` and Spot node draining.
- **Rightsizing via VPA:** Using the Vertical Pod Autoscaler in "Recommendation" mode to identify massively over-provisioned workloads.
- **Graceful Descheduling:** A Kubernetes `Descheduler` job that runs nightly to rebalance pods across nodes, consolidating underutilized nodes and scheduling them for shutdown.

### The Cost Optimisation Narrative
Senior engineers frame cost savings in business terms: "By migrating our batch processing jobs to a Spot fleet and implementing the Descheduler, I reduced our compute bill by $240,000 annually — equivalent to hiring two additional engineers."

---

## Phase E: Advanced Observability

### OpenTelemetry (OTel) First
Design new systems to emit OTel-native traces, metrics, and logs. This vendor-agnostic approach prevents lock-in to Datadog or New Relic.

### SLO Engineering
- Move from "Are we up?" (threshold alerts) to "Are we consuming error budget?" (burn rate alerts).
- Design tiered SLOs: P99 latency for Premium tier, P95 for Standard tier.
- Establish an Error Budget Policy: if budget is exhausted, freeze all feature releases until reliability work is completed.

### Chaos Engineering (GameDays)
Proactively discover failure modes before customers do:
1. Define steady state (normal metrics baseline).
2. Hypothesize: "If we kill one AZ, latency should stay below 300ms."
3. Inject failure (AZ blackhole, pod kill, network partition).
4. Measure: did the steady state hold?
5. Fix any surprises found before the hypothesis validated.

---

## Phase F: Leadership & Influence

7 YOE is also the point where *technical output* is no longer sufficient. You must demonstrate influence.

### Architecture Decision Records (ADRs)
An ADR is a short document (1-2 pages) capturing: the context, the decision, the trade-offs considered, and the consequences. They become the institutional memory of why the architecture is the way it is.

### Running Design Reviews
Structure: Problem statement → Proposed solution → Trade-offs → Alternatives considered → Decision.
- Present to stakeholders at different levels (engineer, manager, CISO, CTO).
- Specifically tailor the risk/cost framing for non-technical audiences.

### Mentorship & On-Call Standards
- Define minimum standards for what constitutes a page-worthy alert.
- Design runbook coverage — every alert must have a linked runbook.
- Lead blameless post-mortems and track action item completion rates.
