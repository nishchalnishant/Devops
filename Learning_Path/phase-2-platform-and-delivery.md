# Phase 2 - Platform And Delivery Core

```
Phase 2 - Platform And Delivery Core
├── Cloud Platform Basics
│   ├── Compute: VMs, managed instances, autoscaling groups
│   ├── Storage: block, object, shared file — when to use each
│   ├── Networking: VPC, subnets, public vs private, NAT, peering
│   ├── IAM: roles, policies, service accounts, least privilege
│   ├── Managed services vs self-hosted trade-offs
│   └── Availability zones and regions: why placement decisions matter
├── CI/CD
│   ├── Pipeline stages: build → test → scan → package → publish → deploy → verify
│   ├── Artifact immutability: same artifact moves from staging to production
│   ├── Promotion between environments (not rebuild per env)
│   ├── Rollback controls: revision rollback, traffic shift, hotfix path
│   └── Approval gates for high-risk or production deployments
├── Docker
│   ├── Images: layers, layer caching, FROM instruction, .dockerignore
│   ├── Containers: lifecycle, CMD vs ENTRYPOINT, environment variables
│   ├── Multi-stage builds: build stage + minimal runtime image
│   ├── Registries: public (Docker Hub) vs private (ECR, ACR, GCR)
│   └── Networking: bridge, host, overlay; Docker Compose for local dev
├── Kubernetes
│   ├── Pods: smallest deployable unit, shared network and storage
│   ├── Deployments: rolling updates, replica management, rollout undo
│   ├── Services: ClusterIP, NodePort, LoadBalancer
│   ├── Ingress: HTTP routing, TLS termination, host/path rules
│   ├── ConfigMaps and Secrets: decoupling config from images
│   ├── Probes: liveness, readiness, startup — how they affect scheduling and traffic
│   ├── Resource requests and limits: scheduling, QoS, throttling, OOM
│   └── Basic troubleshooting: CrashLoopBackOff, ImagePullBackOff, Pending
├── IaC
│   ├── Terraform: providers, modules, state, remote backends, locking
│   ├── Drift: what it is, how it happens, how to detect and reconcile
│   ├── Click-ops risk: why manual changes create untracked state
│   └── Ansible: post-provision configuration, idempotency, playbooks
├── Hands-On Tasks
│   ├── Containerize app with multi-stage Docker build
│   ├── Build CI pipeline: build + test + publish image
│   ├── Deploy to Kubernetes with health checks
│   ├── Provision environment with Terraform remote backend
│   └── Document release flow from commit to production
└── Exit Criteria
    ├── Explain end-to-end CI/CD flow clearly
    ├── Containerize and deploy app to Kubernetes
    ├── Explain Service, Ingress, probe, rollout behavior
    ├── Describe Terraform state, backends, modules, and drift
    └── Connect cloud architecture decisions to delivery and reliability
```

## First Principles

- **Why build before deploy?** A deployment without a repeatable build is a time bomb. Artifact immutability means the thing you tested is the thing you shipped — that invariant eliminates an entire class of production failures.
- **Why containers before Kubernetes?** Kubernetes is a container scheduler. Understanding what a container is, how its filesystem is layered, and how its process runs inside a namespace is prerequisite to understanding why Kubernetes makes the scheduling decisions it does.
- **Why Terraform state matters fundamentally?** Infrastructure is shared state. Two people applying changes to the same resource without coordination produces race conditions and corruption. State locking is the same problem as a distributed lock on a shared database.
- **Why IaC before cloud console skills?** Any infrastructure touched manually drifts from its declared specification. Every click in a console that is not codified is an undocumented change that future runbooks cannot reproduce.
- **Why CI/CD before deployment strategy?** Deployment strategy is a consequence of pipeline design. Canary and blue-green require artifact promotion, not rebuilds, and they require rollback hooks that must be wired into the pipeline at build time.

This phase is about building the platform layer: cloud resources, pipelines, containers, Kubernetes, and infrastructure as code.

## Goal

By the end of this phase, you should be able to take an application from source code to a repeatable deployment running on cloud infrastructure.

## Study Order

1. `../12_Azure/README.md`
2. `../06_Jenkins/README.md`
3. `../06_Jenkins/scenarios.md`
4. `../05_Kubernetes/notes/containers-orchestration-README.md`
5. `../10_Terraform/README.md`
6. `../07_Interview_Preparation/interview-questions-easy.md`
7. `../07_Interview_Preparation/interview-questions-medium.md`

## What To Master

### Cloud Platform Basics

- compute, storage, networking, IAM, and managed services
- public versus private networking
- why availability zones and regions matter
- when to use managed services versus self-hosted systems

### CI/CD

- build, test, scan, package, publish, deploy, verify
- artifact immutability
- promotion between environments
- rollback and approval controls

### Docker

- images, containers, layers, registries, volumes, and networking
- Dockerfile best practices
- multi-stage builds and small runtime images

### Kubernetes

- pods, deployments, services, ingress, config maps, secrets, probes
- resource requests and limits
- rollout behavior and basic troubleshooting

### IaC

- Terraform providers, modules, state, backends, and locking
- Ansible for post-provision configuration
- drift and why click-ops are risky

## Hands-On Tasks

1. Containerize a small application with a multi-stage Docker build.
2. Create a simple CI pipeline that builds, tests, and publishes an image.
3. Deploy the application to Kubernetes with health checks.
4. Provision the target environment with Terraform using a remote backend.
5. Document the release flow from commit to production.

## Checkpoint Questions

- Why should the same artifact move from staging to production?
- What is the difference between a Deployment and a StatefulSet?
- Why are Terraform state locking and remote backends important?
- When would you use a cloud load balancer versus an ingress controller?
- How do Docker layers affect build performance?

## Exit Criteria

Move to Phase 3 only when you can:

- explain an end-to-end CI/CD flow clearly
- containerize and deploy an app to Kubernetes
- explain Service, Ingress, probe, and rollout behavior
- describe Terraform state, backends, modules, and drift
- connect cloud architecture decisions to delivery and reliability

***

## Related Resources

- [Cloud Services](../12_Azure/README.md)
- [CI/CD Pipelines](../06_Jenkins/README.md)
- [End-to-End Pipeline Example](../06_Jenkins/scenarios.md)
- [Containers and Orchestration](../05_Kubernetes/notes/containers-orchestration-README.md)
- [Terraform](../10_Terraform/README.md)
- [Medium Interview Questions](../07_Interview_Preparation/interview-questions-medium.md)
- [Platform Engineering for CI/CD](../06_Jenkins/notes/platform-engineering-for-cicd.md) (for senior depth)

***

**Previous:** [Phase 1 - Foundations](phase-1-foundations.md) | **Next:** [Phase 3 - SRE and Operations](phase-3-sre-and-operations.md)
