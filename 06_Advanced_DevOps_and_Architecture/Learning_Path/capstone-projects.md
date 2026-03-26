# Capstone Projects

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
