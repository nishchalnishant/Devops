# Senior DevOps Learning Path

```
Senior DevOps Learning Path
├── Learning Model (4-step pattern per phase)
│   ├── 1. Learn concepts from roadmap and reference docs
│   ├── 2. Reinforce with cheat-sheets and command practice
│   ├── 3. Validate with interview questions
│   └── 4. Apply in labs, scenarios, and capstones
├── Phase 1 - Foundations (Weeks 1-3)
│   ├── DevOps / Systems thinking
│   ├── Git hygiene and pull request flow
│   ├── Linux administration (fs, processes, systemd, packages)
│   ├── Shell scripting (loops, conditions, exit codes, safety)
│   └── Networking (CIDR, TCP, DNS, TLS, load balancing)
├── Phase 2 - Platform And Delivery Core (Weeks 4-6)
│   ├── Complete CI/CD lifecycle — `ci-cd-lifecycle.md`
│   ├── Cloud platform basics (compute, storage, networking, IAM)
│   ├── CI/CD (build → test → scan → package → publish → deploy → verify)
│   ├── Docker (images, layers, multi-stage builds, registries)
│   ├── Kubernetes (pods, deployments, services, ingress, probes, HPA)
│   └── IaC (Terraform state + backends, Ansible configuration)
├── Phase 3 - SRE And Operations (Weeks 7-9)
│   ├── Observability (metrics, logs, traces, Prometheus, Grafana)
│   ├── SLI / SLO / error budget thinking
│   ├── Troubleshooting (Kubernetes, Terraform, host-level)
│   ├── Reliability (rollback, canary, graceful degradation)
│   ├── Security hygiene (secrets, least privilege, image scanning)
│   └── Cost and capacity (autoscaling, rightsizing, waste)
├── Phase 4 - Senior Role Readiness (Weeks 10-12)
│   ├── Enterprise architecture and trade-offs
│   ├── Reliability engineering at scale
│   ├── Platform engineering (Backstage, golden paths, DORA)
│   ├── Change management and migrations
│   ├── Incident leadership and communication
│   ├── Governance, security, and FinOps
│   └── Mentoring, standards, and documentation
├── Capstones
│   ├── Capstone 1: Single-service delivery platform
│   ├── Capstone 2: Environment provisioning with IaC
│   ├── Capstone 3: Senior operations pack (SLO + RCA + runbook)
│   └── Stretch: Internal Developer Platform lite
└── Specialization Track (after Phase 4)
    └── MLOps: feature stores, CT pipelines, model serving, LLMOps
```

## First Principles

- **Why phase sequencing?** You cannot troubleshoot Kubernetes if you do not understand Linux processes and networking. Foundations must precede platform work, which must precede reliability thinking.
- **Why exit criteria instead of time-boxes?** Competency is not linear. Exit criteria force honest self-assessment rather than calendar-based advancement through material that has not been internalized.
- **Why interview questions after each phase?** Articulation is distinct from comprehension. Being able to explain a concept under question pressure is proof of depth, not reading.
- **Why capstone projects at the end?** Senior engineers are hired on judgment and ownership, not recall. Projects generate real stories, artifacts, and measurable outcomes.
- **Why a 12-week track and a 4-week sprint separately?** The same content must serve two different learners: someone building from scratch and someone preparing quickly from a mid-level baseline.
- **Why ground rules?** The most common failure modes in self-directed learning are skipping fundamentals for trendy tools and stopping at deployment without learning operations.

This folder turns the repository into an incremental curriculum. Follow the phases in order unless you already meet the exit criteria for a phase.

## Learning Model

Each phase follows the same pattern:

1. Learn the concepts from the roadmap and reference docs.
2. Reinforce them with cheat-sheet sources and command practice.
3. Validate understanding with interview questions.
4. Apply the knowledge in labs, scenarios, and capstones.

## Phase Map

| Phase | Goal | Main sources | Exit outcome |
| --- | --- | --- | --- |
| [Phase 1 - Foundations](phase-1-foundations.md) | Build the base operating model | `01_` fundamentals, `02_` Git and CI/CD notes, `08_` guides, easy questions | You can explain DevOps fundamentals and work comfortably in Linux, Git, and networking basics |
| [Phase 2 - Platform And Delivery Core](phase-2-platform-and-delivery.md) | Learn how software is built, packaged, deployed, and provisioned | `02_`, `03_`, `04_`, cloud track, delivery guide | You can design and operate a simple delivery platform |
| [Phase 3 - SRE And Operations](phase-3-sre-and-operations.md) | Learn to run systems in production | `05_`, scenario drills, medium and hard interview banks | You can monitor, troubleshoot, and stabilize services under failure |
| [Phase 4 - Senior Role Readiness](phase-4-senior-role-readiness.md) | Think like a senior DevOps or SRE engineer | hard questions, playbook, career section, cloud hard track | You can explain trade-offs, architecture, reliability, governance, and incident leadership |
| [Capstones](capstone-projects.md) | Turn study into proof | phase docs plus existing repo references | You have real projects, runbooks, and stories for interviews |

## Specialization Track

After Phase 4, use the MLOps specialization if your target role includes ML platforms, training pipelines, model serving, or GPU-aware infrastructure:

- `../17_MLOps/notes/MLOps.md`
- `../07_Interview_Preparation/mlops-interview-playbook.md`
- `../07_Interview_Preparation/mlops-interview-questions-easy.md`
- `../07_Interview_Preparation/mlops-interview-questions-medium.md`
- `../07_Interview_Preparation/mlops-interview-questions-hard.md`
- `../07_Interview_Preparation/mlops-scenario-based-interview-drills.md`

## Suggested 12-Week Deep Track

### Weeks 1-3

- Complete Phase 1
- Practice shell, Git, Linux, and networking commands daily
- Answer easy questions only after the notes make sense

### Weeks 4-6

- Complete Phase 2
- Containerize an application
- Build a simple CI/CD flow
- Provision infrastructure with Terraform

### Weeks 7-9

- Complete Phase 3
- Build dashboards and alerts
- Practice failure drills from the scenario file
- Write one small runbook and one RCA

### Weeks 10-12

- Complete Phase 4
- Do one capstone project
- Practice architecture and incident interviews out loud
- Tighten resume and project evidence

## Suggested 4-Week Interview Sprint

If you are already mid-level and preparing quickly:

1. Read `REPO-AUDIT.md`
2. Do Phase 1 fast and confirm the exit criteria
3. Focus heavily on Phases 2, 3, and 4
4. Use `07_Interview_Preparation/devops-interview-playbook.md` and `07_Interview_Preparation/general-interview-questions.md` every week
5. Finish with at least one capstone and one mock incident walkthrough

## Ground Rules For Incremental Learning

- Do not memorize interview answers before understanding the system.
- Do not skip Linux, networking, or IaC foundations because Kubernetes is trendy.
- Do not stop at deployment; senior roles are about operations, reliability, and trade-offs.
- Do not treat Azure, AWS, or Kubernetes as isolated tools. Always connect them to delivery, observability, and failure handling.

***

## Quick Navigation

| Phase | Focus | Duration |
|-------|-------|----------|
| [Phase 1](phase-1-foundations.md) | Linux, Git, Scripting, Networking | Weeks 1-3 |
| [Phase 2](phase-2-platform-and-delivery.md) | Cloud, CI/CD, Containers, Kubernetes, Terraform | Weeks 4-6 |
| [Phase 2.5](phase-2.5-gitops-integration.md) | GitOps, ArgoCD, Flux, multi-environment promotion | 1-2 weeks |
| [Phase 3](phase-3-sre-and-operations.md) | Observability, Troubleshooting, Reliability | Weeks 7-9 |
| [Phase 4](phase-4-senior-role-readiness.md) | Architecture, Leadership, Governance, Job Readiness | Weeks 10-12 |
| [Capstones](capstone-projects.md) | Hands-on Projects | Ongoing |
| [Certification Guide](certification-and-tool-progression.md) | Cert roadmap, tool sequence, timelines | Reference |

***

## Related Resources

- [DevOps Interview Playbook](../07_Interview_Preparation/devops-interview-playbook.md)
- [General Interview Questions](../07_Interview_Preparation/general-interview-questions.md)
- [Career and Community](../Career_and_Community.md)
