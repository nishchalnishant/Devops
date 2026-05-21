# Capstone Projects

```
Capstone Projects
├── Capstone 1 - Single-Service Delivery Platform
│   ├── Scope
│   │   ├── Source code in Git
│   │   ├── Dockerfile
│   │   ├── CI pipeline (test + image build)
│   │   ├── Registry publish
│   │   ├── Kubernetes deployment
│   │   └── One dashboard + one alert
│   ├── Deliverables
│   │   ├── Architecture diagram
│   │   ├── Pipeline file
│   │   ├── K8s manifests or Helm chart
│   │   ├── Deployment runbook
│   │   └── Rollback procedure
│   └── Proves: Git workflow, CI/CD fundamentals, containerization, K8s basics, observability basics
├── Capstone 2 - Environment Provisioning With IaC
│   ├── Scope
│   │   ├── Terraform modules (network, compute, IAM, storage)
│   │   ├── Remote backend + state locking
│   │   ├── Separate dev and prod environments
│   │   └── Ansible bootstrap or configuration step
│   ├── Deliverables
│   │   ├── Module structure
│   │   ├── Backend configuration
│   │   ├── Environment layout
│   │   ├── Drift prevention example (prevent_destroy)
│   │   └── Blast radius explanation
│   └── Proves: IaC maturity, state strategy, reproducibility, operational safety
├── Capstone 3 - Senior Operations Pack
│   ├── Scope
│   │   ├── Define SLIs and SLOs
│   │   ├── Create alerting policy
│   │   ├── Simulate one failure drill
│   │   ├── Capture runbook
│   │   ├── Capture RCA
│   │   └── Include cost and security control
│   ├── Suggested failure drills
│   │   ├── CrashLoopBackOff
│   │   ├── Bad deployment with rollback
│   │   ├── Terraform drift or unsafe plan
│   │   ├── High latency after scaling
│   │   └── Prometheus no-data or noisy-alert problem
│   ├── Deliverables
│   │   ├── SLO document
│   │   ├── Alert definitions
│   │   ├── Failure drill notes
│   │   ├── Runbook
│   │   ├── RCA
│   │   └── Improvement backlog
│   └── Proves: Production operations mindset, incident handling, reliability engineering, communication quality
└── Stretch Project - Internal Developer Platform Lite
    ├── One reusable application template
    ├── One standard pipeline
    ├── One Terraform module set
    ├── One deployment template
    ├── One dashboard pack
    └── One onboarding guide
```

## First Principles

- **Why hands-on capstones matter?** Reading documentation builds recognition, not recall. Building something and then debugging it under failure conditions forces the internalization that interviews actually test.
- **Why three progressively scoped capstones?** The first proves you can ship. The second proves you can provision safely. The third proves you can operate under failure. Each layer assumes and extends the previous.
- **Why a runbook and RCA in Capstone 3?** Senior engineers are judged partly on written communication. A runbook that someone else can follow and an RCA that captures prevention steps are evidence of operational maturity.
- **Why a stretch IDP project?** Platform engineers are not just skilled operators — they multiply team velocity by removing friction. An IDP lite demonstrates platform thinking, which is the highest leverage skill at senior level.
- **Why architecture diagrams as deliverables?** You will almost certainly be asked to walk through a system design in a senior interview. A capstone diagram gives you a real artifact to discuss, not a hypothetical.

Use these projects to turn the repository from theory into senior-level interview evidence.

## Capstone 1 - Single-Service Delivery Platform

### Goal

Prove that you can build a basic but professional delivery path for one application.

### Scope

- source code in Git
- Dockerfile
- CI pipeline with test and image build
- registry publish
- Kubernetes deployment
- one dashboard and one alert

### Deliverables

- architecture diagram
- pipeline file
- Kubernetes manifests or Helm chart
- short deployment runbook
- short rollback procedure

### What It Proves

- Git workflow understanding
- CI/CD fundamentals
- containerization
- Kubernetes basics
- observability basics

## Capstone 2 - Environment Provisioning With IaC

### Goal

Prove that you can provision and manage the delivery platform safely.

### Scope

- Terraform modules for network, compute, IAM, and storage
- remote backend and state locking
- separate dev and prod environments
- optional Ansible bootstrap or configuration step

### Deliverables

- module structure
- backend configuration
- environment layout
- one example of drift prevention or protection such as `prevent_destroy`
- short explanation of why the structure minimizes blast radius

### What It Proves

- infrastructure as code maturity
- state and environment strategy
- reproducibility
- operational safety

## Capstone 3 - Senior Operations Pack

### Goal

Prove that you can operate the platform like a senior engineer.

### Scope

- define SLIs and SLOs
- create an alerting policy
- simulate one failure drill
- capture a runbook
- capture an RCA
- include at least one cost and one security control

### Suggested Failure Drills

- `CrashLoopBackOff`
- bad deployment with rollback
- Terraform drift or unsafe plan
- high latency after scaling
- Prometheus no-data or noisy-alert problem

### Deliverables

- SLO document
- alert definitions
- failure drill notes
- runbook
- RCA
- improvement backlog

### What It Proves

- production operations mindset
- incident handling
- reliability engineering
- communication quality

## Stretch Project - Internal Developer Platform Lite

If you want a project that signals strong senior potential, build a small paved road:

- one reusable application template
- one standard pipeline
- one Terraform module set
- one deployment template
- one dashboard pack
- one onboarding guide

This project demonstrates platform thinking, standardization, and team enablement rather than isolated tooling knowledge.

***

## Related Resources

- [Career and Community](../Career_and_Community.md) - Resume guidance and interview prep
- [DevOps Interview Playbook](../07_Interview_Preparation/devops-interview-playbook.md)
- [Kubernetes Runbook](../05_Kubernetes/troubleshooting.md)
- [Enterprise Scale Architecture](../system-design.md)
- [Platform Engineering and FinOps](../16_Platform_Engineering_and_FinOps/README.md)

***

**Previous:** [Phase 4 - Senior Role Readiness](phase-4-senior-role-readiness.md) | **Back to:** [Learning Path Overview](README.md)
