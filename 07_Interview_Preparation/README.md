# Interview Preparation Hub

> [!IMPORTANT]
> This is the master navigation center for all interview preparation content. Every file in this repository with interview-relevant material is linked and categorized here. Start here, not in individual files.

## How To Use This Hub

1. **Identify your target role** using the Role Map below.
2. **Pick your difficulty tier** based on your experience level.
3. **Use the Three-Pillar system** — for every topic, practice Theoretical, Practical, and Scenario-based questions.
4. **Run the Final Drill** checklist before any interview.

---

## Role Map: Where To Focus

| Target Role | Primary Focus Areas | Start Here |
|---|---|---|
| DevOps Engineer (3-5 YOE) | CI/CD, Containers, IaC, Linux | [Easy](interview-questions-easy.md) → [Medium](interview-questions-medium.md) |
| Senior DevOps / SRE (5-7 YOE) | K8s Architecture, Observability, GitOps, Security | [Medium](interview-questions-medium.md) → [Hard](interview-questions-hard.md) |
| Staff / Principal DevOps (7+ YOE) | Platform Eng, FinOps, Distributed Systems, Trade-offs | [Hard](interview-questions-hard.md) → [Playbook](devops-interview-playbook.md) |
| MLOps Engineer (3-5 YOE) | ML Lifecycle, Feature Stores, Model Serving | [MLOps Easy](mlops-interview-questions-easy.md) |
| Senior MLOps / ML Platform (5-7 YOE) | CT Pipelines, Drift, GPU Scheduling, LLMOps | [MLOps Medium](mlops-interview-questions-medium.md) → [MLOps Hard](mlops-interview-questions-hard.md) |
| Azure Specialist | AKS, Azure Policy, Entra ID, ADO | [Azure Playbook](azure-devops-interview-playbook.md) → [Azure Scenarios](azure-scenario-based-drills.md) |
| Cloud Engineer (TCS / Product) | Multi-cloud, Cost, Landing Zones | [TCS Prep](tcs-cloud-engineer-interview-prep.md) |

---

## The Three-Pillar Interview System

Every topic in this repository is covered across three question types. Never prepare only one type.

```
┌─────────────────────────────────────────────────────────────────┐
│                    THREE-PILLAR SYSTEM                          │
├─────────────────┬──────────────────────┬────────────────────────┤
│  THEORETICAL    │     PRACTICAL        │    SCENARIO-BASED      │
│                 │                      │                        │
│ "What is X?"    │ "Write a command     │ "Production is down.   │
│ "Explain Y"     │  that does X"        │  What do you do?"      │
│ "Compare A & B" │ "Debug this YAML"    │ "Scale this design     │
│                 │ "Fix this pipeline"  │  to 10x traffic"       │
├─────────────────┴──────────────────────┴────────────────────────┤
│  WHERE TO FIND EACH TYPE                                        │
│  Theoretical → Difficulty files (Easy/Medium/Hard)              │
│  Practical   → Playbooks + Runbooks                             │
│  Scenario    → Scenario Drill files                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## DevOps Interview Files

### By Difficulty

| File | Tier | Topics Covered | Best For |
|---|---|---|---|
| [interview-questions-easy.md](interview-questions-easy.md) | Easy | Linux, Git, Docker basics, CI/CD intro | 0-3 YOE warm-up |
| [interview-questions-medium.md](interview-questions-medium.md) | Medium | K8s operations, Terraform, IaC, Monitoring | 3-5 YOE core |
| [interview-questions-hard.md](interview-questions-hard.md) | Hard | Architecture, SRE, GitOps, eBPF, Service Mesh, FinOps | 7+ YOE target |

### By Topic (Advanced Files)

| File | Topics | Difficulty |
|---|---|---|
| [devops-interview-playbook.md](devops-interview-playbook.md) | Answer frameworks, command anchors, senior signals | Medium → Hard |
| [general-interview-questions.md](general-interview-questions.md) | Scenario drills, cross-domain reasoning | Medium → Hard |
| [azure-devops-interview-playbook.md](azure-devops-interview-playbook.md) | AKS, ADO, Azure Policy, Entra ID, FinOps | Medium → Hard |
| [azure-scenario-based-drills.md](azure-scenario-based-drills.md) | Azure production failure scenarios | Hard |
| [tcs-cloud-engineer-interview-prep.md](tcs-cloud-engineer-interview-prep.md) | Cloud foundations, multi-cloud, cost | Easy → Medium |

---

## MLOps Interview Files

> [!IMPORTANT]
> MLOps interviews test infrastructure + ML knowledge simultaneously. Read the [MLOps Playbook](mlops-interview-playbook.md) before tackling the question banks.

| File | Tier | Topics Covered |
|---|---|---|
| [mlops-interview-playbook.md](mlops-interview-playbook.md) | All | Answer framework, what interviewers test, revision checklist |
| [mlops-interview-questions-easy.md](mlops-interview-questions-easy.md) | Easy | ML lifecycle, model serving basics, DVC, Feature Stores intro |
| [mlops-interview-questions-medium.md](mlops-interview-questions-medium.md) | Medium | Feature Stores, drift detection, CT pipelines, shadow deploy |
| [mlops-interview-questions-hard.md](mlops-interview-questions-hard.md) | Hard | Multi-region inference, LLMOps, GPU architecture, governance |
| [mlops-scenario-based-interview-drills.md](mlops-scenario-based-interview-drills.md) | Hard | Production failure scenarios specific to ML systems |

---

## Advanced Topic Deep-Dives (Theory + Interview)

These files contain full theory sections followed by interview Q&A. Use them for topic-specific preparation.

### MLOps Deep-Dives

| File | Topics | Status |
|---|---|---|
| [../06_Advanced_DevOps_and_Architecture/MLOps.md](../06_Advanced_DevOps_and_Architecture/MLOps.md) | KubeFlow, MLflow, Serving, Drift, GPU Scheduling | Available |
| [mlops-feature-stores-and-pipelines.md](mlops-feature-stores-and-pipelines.md) | Feature Stores (Feast/Hopsworks), ML Pipeline Orchestration, CT Triggers | Available |
| [mlops-llmops-and-advanced-serving.md](mlops-llmops-and-advanced-serving.md) | LLMOps, RAG pipelines, vLLM, Triton, Model Governance | Available |

### Advanced DevOps Deep-Dives

| File | Topics | Status |
|---|---|---|
| [../06_Advanced_DevOps_and_Architecture/Platform_Engineering_and_FinOps.md](../06_Advanced_DevOps_and_Architecture/Platform_Engineering_and_FinOps.md) | IDPs, DORA, FinOps lifecycle, Policy-as-Code | Available |
| [../06_Advanced_DevOps_and_Architecture/Enterprise_Scale_Architecture.md](../06_Advanced_DevOps_and_Architecture/Enterprise_Scale_Architecture.md) | Multi-region, SRE culture, chaos engineering | Available |
| [advanced-ebpf-and-service-mesh.md](advanced-ebpf-and-service-mesh.md) | eBPF internals, Cilium, Istio at scale, ambient mesh | Available |
| [gitops-at-scale-and-finops.md](gitops-at-scale-and-finops.md) | Fleet management, ArgoCD ApplicationSets, Flux multi-tenancy, Kubecost | Available |

---

## Cross-Reference: Topic → File Map

Use this table when you know your interview topic but not which file covers it best.

| Topic | Theory File | Interview Q&A |
|---|---|---|
| Linux Performance & Security | [Advanced Linux](../01_Prerequisites_and_Fundamentals/Linux/advanced-linux-performance-and-hardening.md) | [Easy Q&A](interview-questions-easy.md) |
| Networking (BGP, eBPF, CNI) | [Enterprise Networking](../01_Prerequisites_and_Fundamentals/Networking/enterprise-networking-and-protocols.md) | [Hard Q&A](interview-questions-hard.md) |
| Shell Scripting & Automation | [Engineering Automation](../01_Prerequisites_and_Fundamentals/Scripting/engineering-automation-at-scale.md) | [Easy Q&A](interview-questions-easy.md) |
| Git & Monorepos | [Advanced Git](../02_Version_Control_and_CI_CD/Git_GitHub/advanced-git-workflows-and-monorepos.md) | [Medium Q&A](interview-questions-medium.md) |
| CI/CD & Platform Engineering | [Platform Engineering for CI/CD](../02_Version_Control_and_CI_CD/Jenkins_CICD/platform-engineering-for-cicd.md) | [Hard Q&A](interview-questions-hard.md) |
| GitOps & ArgoCD | [Progressive Delivery](../02_Version_Control_and_CI_CD/ArgoCD/progressive-delivery-and-gitops-at-scale.md) | [Hard Q&A](interview-questions-hard.md) |
| Supply Chain Security / SLSA | [Supply Chain Security](../02_Version_Control_and_CI_CD/DevSecOps/supply-chain-security-and-slsa.md) | [Hard Q&A](interview-questions-hard.md) |
| Docker & Container Runtimes | [Container Runtimes & Security](../03_Containers_and_Orchestration/Docker/container-runtimes-and-security.md) | [Medium Q&A](interview-questions-medium.md) |
| Kubernetes Architecture | [Enterprise K8s Architecture](../03_Containers_and_Orchestration/Kubernetes/enterprise-kubernetes-architecture.md) | [Hard Q&A](interview-questions-hard.md) |
| Kubernetes Networking & Security | [Advanced K8s Networking](../03_Containers_and_Orchestration/Kubernetes/advanced-networking-and-security.md) | [Hard Q&A](interview-questions-hard.md) |
| Terraform & IaC | [Advanced Terraform](../04_Infrastructure_as_Code_and_Cloud/Terraform/advanced-terraform-patterns.md) | [Hard Q&A](interview-questions-hard.md) |
| Cloud Landing Zones | [Enterprise Landing Zones](../04_Infrastructure_as_Code_and_Cloud/Cloud_Services/enterprise-landing-zones.md) | [Azure Hard](../04_Infrastructure_as_Code_and_Cloud/Cloud_Services/azure-hard-questions.md) |
| Observability & SRE | [Monitoring README](../05_Observability_and_Troubleshooting/Monitoring/README.md) | [DevOps Playbook](devops-interview-playbook.md) |
| Incident Response | [Incident Runbook](../05_Observability_and_Troubleshooting/Troubleshooting/incident-response-runbook.md) | [Scenario Drills](general-interview-questions.md) |
| MLOps Fundamentals | [MLOps.md](../06_Advanced_DevOps_and_Architecture/MLOps.md) | [MLOps Playbook](mlops-interview-playbook.md) |
| Feature Stores & CT Pipelines | [Feature Stores & Pipelines](mlops-feature-stores-and-pipelines.md) | [MLOps Medium](mlops-interview-questions-medium.md) |
| LLMOps & Advanced Serving | [LLMOps Deep-Dive](mlops-llmops-and-advanced-serving.md) | [MLOps Hard](mlops-interview-questions-hard.md) |
| eBPF & Service Mesh | [eBPF & Service Mesh](advanced-ebpf-and-service-mesh.md) | [Hard Q&A](interview-questions-hard.md) |
| FinOps & GitOps at Scale | [GitOps & FinOps](gitops-at-scale-and-finops.md) | [Hard Q&A](interview-questions-hard.md) |
| Platform Engineering | [Platform Engineering & FinOps](../06_Advanced_DevOps_and_Architecture/Platform_Engineering_and_FinOps.md) | [Hard Q&A](interview-questions-hard.md) |

---

## Difficulty Tier Definitions

> [!TIP]
> These definitions are strict. Calibrate yourself honestly before deciding which tier to focus on.

### Easy — Junior / Mid-Level (0-3 YOE)
- Tool usage, syntax, and basic workflows
- "What is X?", "How do you do Y in Z tool?"
- Expected to know commands cold, not just concepts
- **Signal:** Can use the tool. Cannot yet design systems with it.

### Medium — Senior-Level (3-6 YOE)
- Integration, security, troubleshooting, and operational depth
- "How does X work under the hood?", "What breaks when Y fails?"
- Expected to have production debugging experience
- **Signal:** Has broken things in production and fixed them. Understands why.

### Hard — Staff / Architect-Level (7+ YOE)
- Scale, distributed systems, trade-offs, cost, and governance
- "Design a system that does X at 100x scale with 99.99% SLO"
- "What would you change about this architecture and why?"
- Expected to drive decisions, not just execute them
- **Signal:** Has opinions backed by evidence. Can defend trade-offs against pushback.

---

## The Pre-Interview Final Drill

Run through this checklist 24-48 hours before any senior DevOps or MLOps interview.

### DevOps Checklist

- [ ] Can explain the Kubernetes control loop and reconciliation model from memory
- [ ] Can design a zero-downtime multi-region deployment with automated rollback
- [ ] Can trace a request from DNS resolution through an Ingress Controller to a Pod
- [ ] Can debug a `CrashLoopBackOff` with no logs available
- [ ] Can explain error budgets and SLO burn rate alerting without prompting
- [ ] Can design a GitOps workflow including secret management strategy
- [ ] Can describe eBPF and why it matters for observability and networking
- [ ] Can compare Istio and Cilium mesh architectures and their trade-offs
- [ ] Can design a FinOps tagging and chargeback model for a 50-team org
- [ ] Can explain SLSA levels and what achieving Level 3 requires in a pipeline

### MLOps Checklist

- [ ] Can distinguish platform health from model quality in a production incident
- [ ] Can explain training-serving skew and name three ways it enters a system
- [ ] Can design a Feature Store with both online and offline serving paths
- [ ] Can describe a Continuous Training trigger and the validation gates before promotion
- [ ] Can explain data drift vs. concept drift and the delayed-label problem
- [ ] Can design a shadow deployment workflow including metric collection
- [ ] Can explain GPU scheduling in Kubernetes including taints and MIG
- [ ] Can describe what makes LLMOps different from standard MLOps
- [ ] Can walk through a RAG pipeline and identify failure modes at each stage
- [ ] Can design a model governance process for a regulated environment

---

## Interview Anti-Patterns to Avoid

> [!CAUTION]
> These are the most common signals that tank senior DevOps and MLOps interviews. Read each one.

| Anti-Pattern | Why It Fails | Better Signal |
|---|---|---|
| Listing tools without explaining trade-offs | Shows surface knowledge, not depth | "I chose X over Y because at our scale, Z constraint mattered most" |
| "We just used Kubernetes for everything" | No architectural judgment | Explain when Kubernetes is wrong for a problem |
| Treating `200 OK` as model health | Fundamental MLOps gap | Distinguish infrastructure health from model quality |
| Starting with the solution before the diagnosis | Skips evidence-gathering | Always confirm scope and recent changes first |
| Saying "I would retrain the model" without a trigger | No production discipline | Define what measurement triggers a retrain |
| Ignoring cost in architecture discussions | Not thinking at Staff level | Every architecture decision has a cost dimension |
| No mention of rollback in deployment designs | Incomplete thinking | Every deployment design needs an explicit rollback path |
| Describing chaos engineering as "breaking things" | Misses the scientific method | A chaos experiment has a hypothesis, a steady state, and a blast radius |

---

## Quick Scenario Framework

For any scenario question, use this structure before answering:

```
1. SCOPE    → What is the blast radius? Who is affected?
2. RECENT   → What changed in the last 24 hours?
3. SYMPTOMS → What are the user-facing signals (latency, errors, wrong output)?
4. LAYER    → Is this app, container, node, network, data, or model?
5. EVIDENCE → Name two specific commands or metrics you would check first
6. STABILIZE → What is the fastest path to restore service?
7. ROOT CAUSE → What permanent fix prevents recurrence?
```

---

*This hub is maintained alongside the main repository. When new content is added, update the Cross-Reference table and the Role Map.*
