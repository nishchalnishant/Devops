# TCS Cloud Engineer Interview Preparation (4+ YOE)

Based on the job description, this guide prioritizes the topics you need to master for the TCS Cloud Engineer role. The core focus of this role is multi-cloud infrastructure, Terraform automation, and overall operational reliability.

## Priority 1: Core Cloud Infrastructure & IaC (High Yield)
*These topics are the primary foundation of the role. Expect deep-dive questions here.*

### 1. Cloud Platforms (AWS / Azure / GCP)
*The JD emphasizes multi-cloud but specifically calls out deep knowledge in at least one.*
- **Compute:** EC2 (AWS), Virtual Machines (Azure), Compute Engine (GCP). Understand provisioning, instance types, auto-scaling groups, and lifecycle.
- **Storage:** S3 (AWS), Blob Storage (Azure). Understand storage classes, object vs. block storage, lifecycle policies, and security (encryption, access controls).
- **Serverless (If AWS focused):** Lambda basics, event-driven architecture.
- **High Availability (HA) & Disaster Recovery (DR):** Multi-AZ deployments, regions, backup strategies.

**Reference Material:**

- [Cloud Services Overview](../04_Infrastructure_as_Code_and_Cloud/Cloud_Services/README.md)
- [Enterprise Landing Zones](../04_Infrastructure_as_Code_and_Cloud/Cloud_Services/enterprise-landing-zones.md)
- [Azure to AWS Similarities](../04_Infrastructure_as_Code_and_Cloud/Cloud_Services/azure-aws-similarities.md)
- [Azure Interview Questions (Easy)](../04_Infrastructure_as_Code_and_Cloud/Cloud_Services/azure-easy-qeustions.md) | [Medium](../04_Infrastructure_as_Code_and_Cloud/Cloud_Services/azure-medium-questions.md) | [Hard](../04_Infrastructure_as_Code_and_Cloud/Cloud_Services/azure-hard-questions.md)

### 2. Infrastructure as Code (Terraform)
*Terraform is explicitly listed as the preferred IaC tool.*
- **Core Concepts:** State files (`.tfstate`), providers, modules, resources, and data sources.
- **State Management:** Remote state backends (e.g., S3 + DynamoDB for locking), state drift resolution.
- **Best Practices:** Modularization, `tfvars`, handling secrets, DRY principles.
- **Commands:** `init`, `plan`, `apply`, `destroy`, `import`.

**Reference Material:**

- [Terraform Fundamentals](../04_Infrastructure_as_Code_and_Cloud/Terraform/README.md)
- [Advanced Terraform Patterns](../04_Infrastructure_as_Code_and_Cloud/Terraform/advanced-terraform-patterns.md)
- [Terraform Interview Questions PDF](./terraform%20interview%20questions.pdf)

---

## Priority 2: Automation & Orchestration (Crucial)
*Connecting infrastructure with development workflows.*

### 3. CI/CD Pipelines
*Jenkins, GitHub Actions, Azure DevOps.*
- **Pipeline Architecture:** Building multi-stage pipelines (Build, Test, Deploy).
- **Integration:** Triggering Terraform runs from pipelines, managing credentials securely within CI/CD.
- **Deployment Strategies:** Blue/Green, Canary, and Rolling updates.

**Reference Material:**

- [Jenkins & CI/CD Pipelines Overview](../02_Version_Control_and_CI_CD/Jenkins_CICD/README.md)
- [Platform Engineering for CI/CD](../02_Version_Control_and_CI_CD/Jenkins_CICD/platform-engineering-for-cicd.md)
- [End-to-End Pipeline Example](../02_Version_Control_and_CI_CD/Jenkins_CICD/end-to-end-ci-cd-pipeline.md)

### 4. Containerization (Docker & Kubernetes)
*Familiarity is required, so focus on the architecture and basic operations.*
- **Docker:** Writing efficient Dockerfiles, image layer optimization, networking, volumes.
- **Kubernetes (K8s):** Architecture (Control Plane vs. Worker Nodes), Pods, Deployments, Services, ConfigMaps, and Secrets.
- **Troubleshooting:** Diagnosing `CrashLoopBackOff`, `ImagePullBackOff`, `Pending` pods.

**Reference Material:**

- [Containers and Orchestration Overview](../03_Containers_and_Orchestration/README.md)
- [Docker & Runtimes Security](../03_Containers_and_Orchestration/Docker/container-runtimes-and-security.md)
- [Enterprise K8s Architecture](../03_Containers_and_Orchestration/Kubernetes/enterprise-kubernetes-architecture.md)
- [Kubernetes Runbook](../05_Observability_and_Troubleshooting/Troubleshooting/kubernetes-runbook.md)
- PDFs: [Docker](./docker%20interview%20questions.pdf) | [Kubernetes](./kubernetes%20interview%20questions.pdf) | [K8s Scenarios](./kubernetes%20scenario%20based%20questions.pdf)

---

## Priority 3: Networking, Security, & Monitoring (Essential Operations)
*Ensuring the infrastructure is connected, secure, and observable.*

### 5. Networking Concepts
- **VPC / VNet:** Subnetting (Public vs. Private), Route Tables, Internet Gateways, NAT Gateways.
- **Traffic Management:** Load Balancers (L4 vs L7), DNS (Route53, Azure DNS).
- **Security perimeters:** Security Groups, Network ACLs, Firewalls, VPNs (Site-to-Site, Client).

**Reference Material:**

- [Networking Overview](../01_Prerequisites_and_Fundamentals/Networking/README.md)
- [Enterprise Networking & Protocols](../01_Prerequisites_and_Fundamentals/Networking/enterprise-networking-and-protocols.md)
- [Advanced K8s Networking](../03_Containers_and_Orchestration/Kubernetes/advanced-networking-and-security.md)

### 6. Monitoring & Logging
*CloudWatch, Azure Monitor, Stackdriver.*
- **Metrics vs. Logs:** How to use both for troubleshooting.
- **Alerting:** Setting up thresholds, notifications, avoiding alert fatigue.
- **Log Aggregation:** Centralized logging strategies to resolve issues in a timely manner.

**Reference Material:**

- [Monitoring & Observability Fundamentals](../05_Observability_and_Troubleshooting/Monitoring/README.md)

### 7. Security & Compliance
- **Identity & Access Management (IAM / RBAC):** Least privilege principle, roles, policies.
- **Data Protection:** Encryption at rest and in transit (KMS, TLS/SSL).
- **Governance:** AWS Organizations, Azure Policies, ensuring infrastructure meets compliance standards.

**Reference Material:**

- [Supply Chain Security (SLSA)](../02_Version_Control_and_CI_CD/DevSecOps/supply-chain-security-and-slsa.md)
- [IaC Policy & GitOps](../04_Infrastructure_as_Code_and_Cloud/Terraform/policy-and-gitops.md)

---

## Priority 4: Scripting & Day-to-Day Operations (Supporting Skills)
*Automating the "glue" and maintaining the systems.*

### 8. Scripting (Python, Bash, or PowerShell)
- **Automation:** Writing scripts to automate routine tasks (backups, cleanup, API polling).
- **Bash:** Text manipulation (`grep`, `awk`, `sed`), basic system troubleshooting scripts.
- **Python:** `boto3` (for AWS) or equivalent SDKs, interacting with REST APIs.

**Reference Material:**

- [Scripting Overview](../01_Prerequisites_and_Fundamentals/Scripting/README.md)
- [Engineering Automation at Scale](../01_Prerequisites_and_Fundamentals/Scripting/engineering-automation-at-scale.md)

### 9. Systems Operations & Maintenance
- **Linux Fundamentals:** Process management, file systems, permissions.
- **Patch Management:** Strategies for zero-downtime OS upgrades and patching.
- **Troubleshooting Methodology:** Methodical approach to resolving "cloud-related issues in a timely manner" (Logs -> Metrics -> Hypothesize -> Fix -> Document).

**Reference Material:**

- [Linux OS Fundamentals](../01_Prerequisites_and_Fundamentals/Linux/README.md)
- [Advanced Linux Performance & Hardening](../01_Prerequisites_and_Fundamentals/Linux/advanced-linux-performance-and-hardening.md)
- [Incident Response Protocol](../05_Observability_and_Troubleshooting/Troubleshooting/incident-response-runbook.md)

---

## Preparation Strategy for the Interview

1. **Prepare the "Tell me about yourself" pitch:** Highlight your 4+ years of experience emphasizing Cloud, Terraform, and CI/CD.
2. **STAR Method for Troubleshooting:** Have 2-3 real-world examples ready of complex cloud issues you resolved. (Situation, Task, Action, Result).
3. **Architecture Discussion:** Be prepared to whiteboard (verbally or literally) a highly available web application architecture on your preferred cloud platform using Terraform and CI/CD.

**Core Interview Playbooks to Read:**
- [DevOps Interview Playbook](./devops-interview-playbook.md)
- [Azure DevOps Interview Playbook](./azure-devops-interview-playbook.md)
- [Azure Scenario Drills](./azure-scenario-based-drills.md)
- [General Interview Questions](./general-interview-questions.md)
- [Interview Questions (Easy)](./interview-questions-easy.md) | [Medium](./interview-questions-medium.md) | [Hard](./interview-questions-hard.md)
