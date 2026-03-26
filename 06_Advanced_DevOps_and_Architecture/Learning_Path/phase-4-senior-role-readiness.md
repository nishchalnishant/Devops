# Phase 4 - Senior Role Readiness

This phase focuses on the skills that separate a senior DevOps engineer from a mid-level implementer.

## What Changes At Senior Level

A senior DevOps engineer is expected to do more than operate tools. The role expands into architecture, reliability strategy, operational decision-making, standards, and communication.

## Senior Capability Areas

### 1. Architecture And Trade-Offs

You should be able to compare options instead of describing a single favorite tool:

- rolling versus blue-green versus canary
- managed service versus self-hosted platform
- deployment versus StatefulSet
- HPA versus VPA
- monolith versus microservices
- push versus pull telemetry

### 2. Reliability Engineering

Senior answers should include:

- blast radius
- rollback paths
- graceful degradation
- SLO and error-budget thinking
- recovery time and failure isolation

### 3. Platform Engineering

Senior engineers build reusable systems, not one-off fixes:

- pipeline templates
- Terraform modules
- standard deployment patterns
- golden paths for teams
- guardrails for security and compliance

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

### 6. Governance, Security, And Cost

At senior level, you are also expected to think about:

- least privilege
- policy as code
- supply chain security
- auditability
- cloud spend and efficiency
- data protection and compliance impact

### 7. Mentoring And Standards

Senior engineers improve the team, not only the system:

- review designs
- improve runbooks
- teach debugging habits
- reduce repetitive toil
- create documentation others can rely on

## What To Study In This Repository For Senior Prep

1. `../devops/devops-interview-playbook.md`
2. `../interview-questions.md`
3. `../devops/interview-questions-hard.md`
4. `../cloud/azure-hard-questions.md`
5. `../roadmap/11.-real-world-test-career-and-community.md`
6. `../REPO-AUDIT.md`

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
