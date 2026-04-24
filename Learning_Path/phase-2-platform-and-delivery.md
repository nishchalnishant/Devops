# Phase 2 - Platform And Delivery Core

This phase is about building the platform layer: cloud resources, pipelines, containers, Kubernetes, and infrastructure as code.

## Goal

By the end of this phase, you should be able to take an application from source code to a repeatable deployment running on cloud infrastructure.

## Study Order

1. `../../04_Infrastructure_as_Code_and_Cloud/Cloud_Services/README.md`
2. `../../02_Version_Control_and_CI_CD/Jenkins_CICD/README.md`
3. `../../02_Version_Control_and_CI_CD/Jenkins_CICD/end-to-end-ci-cd-pipeline.md`
4. `../../03_Containers_and_Orchestration/README.md`
5. `../../04_Infrastructure_as_Code_and_Cloud/Terraform/README.md`
6. `../../07_Interview_Preparation/interview-questions-easy.md`
7. `../../07_Interview_Preparation/interview-questions-medium.md`

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

- [Cloud Services](../../04_Infrastructure_as_Code_and_Cloud/Cloud_Services/README.md)
- [CI/CD Pipelines](../../02_Version_Control_and_CI_CD/Jenkins_CICD/README.md)
- [End-to-End Pipeline Example](../../02_Version_Control_and_CI_CD/Jenkins_CICD/end-to-end-ci-cd-pipeline.md)
- [Containers and Orchestration](../../03_Containers_and_Orchestration/README.md)
- [Terraform](../../04_Infrastructure_as_Code_and_Cloud/Terraform/README.md)
- [Medium Interview Questions](../../07_Interview_Preparation/interview-questions-medium.md)
- [Platform Engineering for CI/CD](../../02_Version_Control_and_CI_CD/Jenkins_CICD/platform-engineering-for-cicd.md) (for senior depth)

***

**Previous:** [Phase 1 - Foundations](phase-1-foundations.md) | **Next:** [Phase 3 - SRE and Operations](phase-3-sre-and-operations.md)
