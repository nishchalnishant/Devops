# DevOps Interview Handbook & Senior Learning Roadmap

This repository is now structured as an incremental senior DevOps learning system. It combines audit notes, a phased learning path, long-form topic references, interview preparation, scenario drills, and capstone-style project guidance, integrating numerous vital cheat sheets for direct reference.

## Start Here

1. [General Guides and Roadmaps](08_General_Guides_and_Roadmaps/1.-devops-terms.md) for overarching topics, roadmaps, and foundational DevOps concepts.
2. [Senior DevOps Learning Path](06_Advanced_DevOps_and_Architecture/Learning_Path/README.md) for the structured 4-phase curriculum from foundations to senior readiness.
3. [DevOps Interview Playbook](07_Interview_Preparation/devops-interview-playbook.md) for answer frameworks, command anchors, and senior interview signals.
4. [MLOps Interview Playbook](07_Interview_Preparation/mlops-interview-playbook.md) for ML platform, model-serving, and MLOps interview preparation.

## Incremental Directory Structure

1. **01 Prerequisites and Fundamentals:** Linux administration, shell scripting, and core networking principles. Contains detailed notes and networking cheat sheets.
2. **02 Version Control and CI/CD:** GitLab, GitHub notes, Jenkins, and GitOps workflows including an end-to-end pipeline example.
3. **03 Containers and Orchestration:** Comprehensive Docker and Kubernetes cheat sheets, operations guides, and networking.
4. **04 Infrastructure as Code and Cloud:** Terraform guidelines and Cloud Services reference (Azure AWS comparisons).
5. **05 Observability and Troubleshooting:** Core principles of monitoring, logging, and real-time environment troubleshooting.
6. **06 Advanced DevOps and Architecture:** SRE operations, MLOps specialization, capstone projects, and the complete 4-phase learning path.
7. **07 Interview Preparation:** Scenario-based drills, targeted questions categorized by difficulty, and specialized tool interview questions.
8. **08 General Guides and Roadmaps:** General DevOps terms, PDFs and eBook guides.

## Core Interview Coverage

- Git and collaboration workflows
- Linux administration and shell scripting
- Networking, DNS, TLS, and load balancing
- Cloud fundamentals across compute, storage, networking, IAM, and Kubernetes
- CI/CD design, artifact management, deployment safety, and rollback
- Docker, Kubernetes, and production troubleshooting
- Terraform, Ansible, state management, and infrastructure drift
- Monitoring, logging, tracing, SLI/SLO thinking, and incident response
- DevSecOps fundamentals such as secrets, least privilege, image scanning, and policy controls
- MLOps fundamentals such as data and model versioning, feature stores, training pipelines, serving patterns, drift, and GPU-aware operations

## Quick Reference

| Topic | Entry Point | Interview Prep |
|-------|-------------|----------------|
| Linux & Scripting | [Linux README](01_Prerequisites_and_Fundamentals/Linux/README.md) | [Easy Questions](07_Interview_Preparation/interview-questions-easy.md) |
| Networking | [Networking README](01_Prerequisites_and_Fundamentals/Networking/README.md) | [Medium Questions](07_Interview_Preparation/interview-questions-medium.md) |
| CI/CD | [Jenkins README](02_Version_Control_and_CI_CD/Jenkins_CICD/README.md) | [Medium Questions](07_Interview_Preparation/interview-questions-medium.md) |
| Containers/K8s | [Containers README](03_Containers_and_Orchestration/README.md) | [Hard Questions](07_Interview_Preparation/interview-questions-hard.md) |
| Terraform/IaC | [Terraform README](04_Infrastructure_as_Code_and_Cloud/Terraform/README.md) | [Hard Questions](07_Interview_Preparation/interview-questions-hard.md) |
| Monitoring | [Monitoring README](05_Observability_and_Troubleshooting/Monitoring/README.md) | [Playbook](07_Interview_Preparation/devops-interview-playbook.md) |
| Troubleshooting | [K8s Runbook](05_Observability_and_Troubleshooting/Troubleshooting/kubernetes-runbook.md) | [Scenario Drills](07_Interview_Preparation/azure-scenario-based-drills.md) |

## Repository Notes

- The strongest indexed source material (including Kubernetes, Docker, Terraform, Linux, networking, monitoring, troubleshooting, Azure, and shell scripting PDFs) has now been neatly arranged alongside corresponding concepts in each numbered roadmap folder.
- Previous `cheat sheet`, `learning-path`, `roadmap`, `devops`, and `cloud` folders have been successfully integrated.
- All content follows a consistent structure: fundamentals → platform engineering → operations → senior readiness.
