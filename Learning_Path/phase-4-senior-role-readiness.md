# Phase 4 - Senior Role Readiness

```
Phase 4 - Senior Role Readiness
├── 1. Enterprise Architecture And Trade-Offs
│   ├── Active-Active vs Active-Passive multi-region deployments
│   ├── Cell-based architecture vs monolithic cluster scaling
│   ├── Hub-and-spoke enterprise landing zones vs peered networks
│   ├── Zero-Trust networking (mTLS via service mesh) vs perimeter security
│   ├── Managed service vs self-hosted platform trade-offs
│   └── Push vs pull telemetry (Prometheus pull vs agent push)
├── 2. Reliability Engineering
│   ├── Blast radius: scope of failure if this component breaks
│   ├── Rollback paths: what exists, how fast, what are the side effects
│   ├── Graceful degradation: disabling features under load instead of failing hard
│   ├── SLO and error-budget thinking: gates between reliability and feature work
│   └── Recovery time and failure isolation: MTTR, partial vs full outage
├── 3. Platform Engineering
│   ├── Internal Developer Platforms (Backstage, Service Catalog)
│   ├── Golden Paths: standardized CI/CD templates, repo templates
│   ├── DORA metrics: deployment frequency, lead time, MTTR, change failure rate
│   ├── SPACE metrics: satisfaction, performance, activity, communication, efficiency
│   └── Cognitive load reduction: abstractions that let product teams move without friction
├── 4. Change Management And Migration
│   ├── Migrating CI/CD platforms (Jenkins to GitHub Actions or GitLab)
│   ├── Introducing breaking Terraform module changes safely
│   ├── Adopting GitOps in an existing push-based environment
│   ├── VM to containers to Kubernetes migration path
│   └── Splitting monolith state into safer infrastructure boundaries
├── 5. Incident Leadership
│   ├── Keep response calm and structured, assign roles
│   ├── Communicate impact and mitigation clearly to stakeholders
│   ├── Choose safe stabilization before perfect root cause
│   └── Capture timeline, contributing factors, and prevention items in RCA
├── 6. Governance, Security, And FinOps
│   ├── Policy-as-code: Kyverno, OPA, Azure Policy, AWS SCPs
│   ├── Supply chain security: SLSA framework, Sigstore, SBOMs
│   ├── FinOps: showback/chargeback, spot fleet, VPA, rightsizing
│   └── Organizational RBAC and Just-In-Time (JIT) access
├── 7. Mentoring And Standards
│   ├── Review designs for blast radius, reliability, and operability
│   ├── Improve runbooks so any on-call can follow them
│   ├── Teach debugging habits: check metrics and logs before guessing
│   ├── Reduce repetitive toil by automating or removing it
│   └── Create documentation others can actually rely on
└── 8. ML Specialization (for ML platform roles)
    ├── Reproducibility across code, data, features, model versions
    ├── Feature store consistency and training-serving skew prevention
    ├── Model registry promotion and rollback procedures
    ├── Drift monitoring and retraining trigger design
    └── GPU scheduling, inference latency targets, serving cost analysis
```

## First Principles

- **Why does seniority require trade-off thinking?** Junior engineers follow established patterns. Senior engineers choose between patterns based on context. The ability to articulate why one design is better than another for a given set of constraints is what seniority actually means.
- **Why blast radius as a mental model?** Every change is a bet. The blast radius tells you the maximum downside of that bet. Senior engineers bound that downside before executing, not after.
- **Why platform engineering as a phase 4 skill?** Mid-level engineers operate within platforms. Senior engineers design platforms that multiply the velocity of other engineers. That leverage effect is the economic reason senior engineers are paid more.
- **Why incident leadership, not just incident resolution?** In a multi-person incident, coordination overhead is often the bottleneck. A calm, structured incident lead reduces confusion and decision latency. That skill is rare and directly reduces MTTR.
- **Why governance at senior level?** Senior engineers affect teams and organizations, not just services. Policy as code, FinOps controls, and JIT access are the mechanisms by which individuals affect organizational behavior at scale without requiring manual oversight of every decision.

This phase focuses on the skills that separate a senior DevOps engineer from a mid-level implementer.

## What Changes At Senior Level

A senior DevOps engineer is expected to do more than operate tools. The role expands into architecture, reliability strategy, operational decision-making, standards, and communication.

## Senior Capability Areas (7 YOE Focus)

### 1. Enterprise Architecture And Trade-Offs

You should be able to compare options and design systems for catastrophic failures at massive scale:

- Active-Active vs. Active-Passive multi-region deployments
- Cell-Based architecture vs. Monolithic cluster scaling
- Hub-and-Spoke enterprise landing zones vs. Peered networks
- Zero-Trust networking (mTLS via Service Mesh) vs. Perimeter security
- managed service versus self-hosted platform
- push versus pull telemetry

### 2. Reliability Engineering

Senior answers should include:

- blast radius
- rollback paths
- graceful degradation
- SLO and error-budget thinking
- recovery time and failure isolation

### 3. Platform Engineering

Senior engineers build platforms for other engineers, treating internal developers as their primary customers:

- Internal Developer Platforms (Backstage)
- Golden Paths (standardized CI/CD, Git repository templates)
- Measuring Developer Velocity (DORA and SPACE metrics)
- Abstracting cognitive load away from product developers

### 4. Change Management And Migration

You should be ready to discuss:

- migrating CI/CD platforms
- introducing breaking Terraform module changes
- adopting GitOps
- moving from VMs to containers or Kubernetes
- splitting monolith state and infrastructure into safer boundaries

### 5. Incident Leadership

A senior engineer:

- keeps the response calm and structured
- communicates impact and mitigation clearly
- chooses safe stabilization actions
- captures timeline, contributing factors, and prevention items

### 6. Governance, Security, And FinOps

At the senior level, you are also expected to think about organizational controls and financials:

- policy-as-code (Kyverno, OPA, Azure Policy, AWS SCPs)
- supply chain security (SLSA framework, Sigstore, SBOMs)
- FinOps mapping (Showback/Chargeback models, spot fleet architecture, VPA/rightsizing)
- organizational RBAC and Just-In-Time (JIT) access

### 7. Mentoring And Standards

Senior engineers improve the team, not only the system:

- review designs
- improve runbooks
- teach debugging habits
- reduce repetitive toil
- create documentation others can rely on

### 8. Specialization Depth

For senior roles with ML platform or AI infrastructure scope, you should also be able to discuss:

- reproducibility across code, data, features, and model versions
- feature-store consistency and training-serving skew
- model registry promotion and rollback
- drift monitoring and retraining triggers
- GPU scheduling, inference latency, and serving cost

## What To Study In This Repository For Senior Prep

1. `../07_Interview_Preparation/devops-interview-playbook.md`
2. `../12_Azure/scenarios.md`
3. `../07_Interview_Preparation/general-interview-questions.md`
4. `../07_Interview_Preparation/interview-questions-hard.md`
5. `../Career_and_Community.md`
6. `../system-design.md`
7. `../16_Platform_Engineering_and_FinOps/README.md`
8. `../17_MLOps/interview.md`

## Senior Practice Tasks

1. Design a multi-environment deployment platform and explain the trade-offs.
2. Write a migration plan from Jenkins to GitHub Actions or GitLab CI.
3. Produce an RCA with technical and process follow-up items.
4. Define a golden path for a new microservice team.
5. Review one capstone project through reliability, security, and cost lenses.

## Senior Interview Signals

You sound senior when you:

- explain trade-offs without pretending there is one perfect answer
- mention rollback and blast radius early
- talk about standards, not only scripts
- connect technical decisions to reliability, speed, and business impact
- communicate clearly under uncertainty

## Exit Criteria

You are senior-ready when you can:

- answer system design and incident questions with structure and trade-off awareness
- explain how to standardize delivery and operations across teams
- discuss reliability, security, governance, and cost in one answer
- provide examples of ownership, automation, and operational leadership

***

## Related Resources

- [DevOps Interview Playbook](../07_Interview_Preparation/devops-interview-playbook.md)
- [Azure DevOps Interview Playbook](../12_Azure/scenarios.md)
- [Career and Community](../Career_and_Community.md)
- [Enterprise Scale Architecture](../system-design.md)
- [Platform Engineering and FinOps](../16_Platform_Engineering_and_FinOps/README.md)
- [Hard Interview Questions](../07_Interview_Preparation/interview-questions-hard.md)
- [MLOps Interview Playbook](../17_MLOps/interview.md) (for ML specialization)
- [Capstone Projects](capstone-projects.md)

***

**Previous:** [Phase 3 - SRE and Operations](phase-3-sre-and-operations.md) | **Next:** [Capstone Projects](capstone-projects.md)

---

## Job Readiness Track: Interview Preparation Integration

### Interview Preparation By Role

After Phase 4, translate study into interview performance. Each role has distinct signals interviewers look for.

**Senior DevOps Engineer**
- System design: multi-region deployment, Kubernetes for 500+ engineers
- Incident: specific outage you mitigated with RCA and prevention
- Platform design: how you standardized CI/CD across multiple teams
- Reliability: SLO/error budget reasoning, speed vs. stability trade-offs

**Senior Platform Engineer**
- Developer experience: what friction you eliminated for engineers
- Golden paths: enforcing standards without blocking innovation
- DORA metrics: what you track and how you improved deployment frequency
- Scaling: handling 10x growth in team count without proportional platform headcount

**Senior SRE**
- SLO strategy: how you define SLOs for different service types
- Failure: worst incident you handled and what you changed afterward
- Observability: instrumentation for 99.99% uptime target
- Trade-offs: cost vs. reliability, automation vs. operational simplicity

**Senior DevSecOps**
- Supply chain: how you think about artifact provenance and SLSA levels
- Policy-as-code: design a policy framework for a 50-engineer organization
- Compliance: how you automate SOC2 or PCI-DSS controls
- Shift left: detecting security issues before production without blocking developers

### Resume Translation: Capstone → Interview Bullets

**Formula:**
```
[Action verb] [what you built] across [scope] using [tools], achieving [metric]:
- Specific measurable outcome
- Secondary outcome (reliability, cost, or velocity)
```

**Capstone 1 example:**

Weak: "Built a CI/CD pipeline"

Strong: "Designed a Kubernetes-native CI/CD platform using ArgoCD and GitHub Actions, reducing deployment time from 30 minutes to 2 minutes. Enabled 12 feature teams to self-serve deployments, reducing on-call burden by 40%. Implemented canary rollouts, reducing production incidents from deployments by 60%."

**Capstone 3 example:**

Weak: "Set up monitoring"

Strong: "Established SLO framework (99.5% availability) with Prometheus and Grafana; symptom-based alerting reduced MTTR from 15 minutes to 5 minutes. Authored runbooks enabling any on-call engineer to self-resolve 80% of CrashLoopBackOff incidents without escalation."

### 6-Week Interview Sprint (After Completing Phase 4)

**Weeks 1–2:** Finish one capstone. Practice explaining it in 15 minutes (record yourself). Write one post-mortem for a real or simulated incident. Translate capstone into 3–5 resume bullets.

**Weeks 3–4:** Practice system design — "design a CI/CD platform for 100 engineers." Practice incident response role-play with a peer. Answer 5–7 hard interview questions out loud. Revise resume against the [interview question files](../Interview_Prep/).

**Weeks 5–6:** Two or three mock interviews with peers or mentors. Prepare your "failure and learning" story. Prepare your "hard trade-off decision" story. Research target company engineering blog; identify one architectural choice to ask about.
