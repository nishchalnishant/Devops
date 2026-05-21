# Roadmap

```
Roadmap
├── 1. DevOps Terms
│   ├── What is DevOps: culture + automation + measurement + sharing
│   ├── Core vocabulary: infrastructure, scaling, monitoring, automation
│   ├── Career alignment: is DevOps the right path
│   └── The DevOps feedback loop: plan → code → build → test → release → deploy → operate → monitor
├── 2. Programming And Scripting
│   ├── Python
│   │   ├── Variables, data types, control flow, functions
│   │   ├── File I/O, JSON, YAML parsing
│   │   ├── Requests library for HTTP APIs
│   │   └── Automation scripts for DevOps tasks
│   └── Shell Scripting
│       ├── Bash fundamentals: variables, loops, conditionals
│       ├── Safe scripting: set -euo pipefail, exit codes
│       ├── Cron and systemd timers for scheduling
│       └── Text processing: grep, awk, sed, jq
├── 3. Networking
│   ├── OSI model and TCP/IP stack
│   ├── DNS resolution chain
│   ├── CIDR, subnets, routing tables
│   ├── NAT, firewall rules, security groups
│   ├── TLS/HTTPS: certificates, handshake, termination
│   └── Load balancing: L4 vs L7 trade-offs
├── 4. Cloud Services
│   ├── Compute: VMs, managed containers, serverless functions
│   ├── Storage: object, block, file storage trade-offs
│   ├── Networking: VPC, subnets, peering, VPN, PrivateLink
│   ├── IAM: roles, policies, least privilege, OIDC federation
│   ├── Autoscaling and availability zones
│   └── Managed services vs self-hosted trade-offs
├── 5. Linux OS
│   ├── Filesystem hierarchy and permissions
│   ├── Process management: ps, top, signals, systemd
│   ├── Disk and memory: df, free, lsof, swap
│   ├── Network tools: ss, curl, dig, tcpdump
│   └── Package management: apt, yum, dnf
├── 6. Containers And Orchestration
│   ├── Docker
│   │   ├── Image layers and Dockerfile best practices
│   │   ├── Multi-stage builds
│   │   ├── Container networking and volumes
│   │   └── Registry push/pull and tagging
│   └── Kubernetes
│       ├── Pods, Deployments, Services, Ingress
│       ├── ConfigMaps, Secrets, RBAC
│       ├── Probes, HPA, resource requests and limits
│       └── Common failures: CrashLoopBackOff, Pending, OOMKilled
├── 7. CI/CD Pipelines
│   ├── Pipeline stages: build → test → scan → package → deploy → verify
│   ├── Artifact immutability and promotion
│   ├── Secrets handling in pipelines
│   ├── Deployment strategies: rolling, blue-green, canary
│   └── Rollback and post-deploy smoke tests
├── 8. Infrastructure As Code
│   ├── Terraform
│   │   ├── Providers, resources, variables, outputs
│   │   ├── State, backends, locking, and drift
│   │   ├── Modules and reuse across environments
│   │   └── Plan inspection before apply
│   └── Ansible
│       ├── Inventory, playbooks, roles, handlers
│       ├── Idempotency and check mode
│       └── When to use Ansible vs Terraform
├── 9. Monitoring And Observability
│   ├── Four Golden Signals: latency, traffic, errors, saturation
│   ├── Prometheus metrics and Grafana dashboards
│   ├── Log aggregation and structured logging
│   ├── Distributed tracing
│   └── SLI, SLO, error budgets, and alert design
├── 10. MLOps
│   ├── ML lifecycle: data → features → train → evaluate → deploy → monitor
│   ├── Feature stores and training-serving skew prevention
│   ├── Model registry and version management
│   ├── Drift monitoring and retraining triggers
│   └── LLMOps: prompt versioning, RAG pipelines, guardrails
└── 11. Real-World Test
    ├── End-to-end project: Git → CI → image → registry → infra → K8s → monitoring
    ├── Portfolio: CI/CD on K8s, Terraform stack, observability drill
    ├── Resume formula: Action + Tooling + Scale + Result
    └── Interview readiness: scenarios, trade-offs, behavioral STAR stories
```

## First Principles

- **Why order topics this way?** Each layer depends on the one before it. You cannot understand Kubernetes networking without TCP/IP fundamentals. You cannot debug CI pipelines without understanding Linux processes and shell. The sequence is not arbitrary — it reflects real dependency chains.
- **Why scripting before cloud?** Cloud APIs, Terraform, and CI pipelines all assume comfort with code. A DevOps engineer who cannot write a shell script or a Python automation is blocked the moment a tool does not have a GUI button for the task needed.
- **Why Linux before containers?** Containers are Linux namespaces and cgroups with a packaging convention on top. An engineer who does not understand Linux process management, file permissions, and networking cannot debug container failures below the `docker logs` level.
- **Why include MLOps in a DevOps roadmap?** ML systems are deployed, monitored, and operated by platform and infrastructure teams. The same principles apply — artifact versioning, deployment safety, observability, rollback — but the artifact is a model and the failure mode is silent degradation rather than a crash.
- **Why Real-World Test as the final section?** Knowing topics in isolation does not prove you can connect them under pressure. A full delivery chain project forces the integration of every layer and produces something you can explain, defend, and demonstrate in an interview.

Use this folder as the reference syllabus. If you want the recommended order for incremental learning, start with `learning-path/README.md` and come back here for topic depth.

### 1. DevOps Terms

This section covers the foundational concepts and terminology essential for understanding the field.

* Introduction to DevOps: What is DevOps?
* Career Alignment: Is DevOps Good For Me?
* Core Concepts: Familiarization with terms like:
  * Infrastructure
  * Scaling
  * Monitoring
  * Automation

### 2. Programming / Scripting

This branch is divided into two primary languages: Python and Shell Scripting, categorized by difficulty levels.

#### A. Python Programming

* Basics:
  * Loops
  * Conditionals
  * Functions
  * OOPs (Object-Oriented Programming)
  * Exception / File Handling
* Intermediate:
  * Boto3 (AWS SDK for Python)
  * Logging
  * Flask (Web Framework)

#### B. Shell Scripting

* Basics:
  * Automating Backups
  * Copying, Moving, and Transferring Code/Files
  * User Management and Automation
* Intermediate:
  * Integration with AWS CLI
  * Makefiles
  * Integration with other Tools & Services

### 3. Networking

This section focuses on the connectivity and security protocols required to manage infrastructure.

* OSI Model (Theoretical framework for networking)
* Network Protocols (TCP/IP, HTTP, etc.)
* Subnets / CIDR (IP addressing and network segmentation)
* SSH / SCP (Secure remote access and file transfer)
* SSL / HTTPS (Encryption and secure web traffic)
* Network Troubleshooting (Diagnosing connectivity issues)
* DNS (Domain Name System)



### 4. Cloud Services

This section focuses on mastering major providers like AWS, Azure, or GCP to manage infrastructure.

* Compute Servers: Managing virtual machines and instances.
* Database Servers: Handling managed and self-hosted database solutions.
* VPCs & Networking: Designing virtual private clouds and network isolation.
* Managed Services: Utilizing platform-specific automated tools.
* IAM / RBAC: Identity and Access Management and Role-Based Access Control for security.

### 5. Linux Operating System

A deep dive into the environment where most DevOps tools and servers operate.

* Installation / Setup: Basic OS configuration.
* Command Line Interface (CLI): Mastery of the terminal.
* Filesystem / Storage / User Permissions: Understanding directory structures and security.
* Package Management: Using tools like apt or yum.
* Virtualization: Concepts and practical application.
* Utilities & Tools: Power tools like grep, find, awk, and sed.

### 6. Containers / Orchestration

Focuses on packaging applications and managing them at scale.

#### A. Docker

* Dockerfiles, Images, Containers: Building and running portable apps.
* Volumes, Networks: Data persistence and inter-container communication.
* Compose, Scout, Init: Multi-container orchestration and environment setup.

#### B. Kubernetes

* Pods, Deployment, Services, Ingress: Core building blocks of a cluster.
* Storage, PersistentVolumes: Handling stateful data in a cluster.
* Networking Policies: Controlling traffic between services.
* Role Based Access Control (RBAC): Fine-grained cluster security.
* HELM, Kustomize: Package management and configuration for K8s.
* Istio: Advanced service mesh for traffic and security management.

### 7. CICD Pipelines

Tools and platforms used to automate the build, test, and deployment process.

* Jenkins:
  * Declarative Pipelines
  * Shared Libraries
  * Tools & Plugins
  * Agents
  * Email Alerts
* GitLab:
  * GitLab CI Pipelines
  * Self-hosted Runners
* GitHub:
  * Repositories & Source Code Management
  * GitHub Actions for automation
  * Webhooks for event-driven tasks
* ArgoCD:
  * K8s Deployments (GitOps approach)
  * Workflows and ArgoCD CLI

### 8. Infrastructure As Code (IaC)

This section focuses on automating the provisioning and configuration of infrastructure through code.

* Terraform:
  * HCL (HashiCorp Configuration Language)
  * Providers (Plugins to interact with cloud APIs)
  * Modules (Containers for multiple resources)
  * State Management (Tracking the current state of infrastructure)
* Ansible:
  * Configuration Management
  * Playbooks (YAML files for task automation)
  * Roles & Templates

### 9. Monitoring

Essential for maintaining system health, observability, and performance tracking.

* Grafana:
  * Dashboards and Visualization
  * k6 Load Testing (Performance testing tool)
* Prometheus:
  * Metrics collection
  * Alerting (Notification systems)
* ELK Stack:
  * Elasticsearch (Search and analytics engine)
  * Logstash (Server-side data processing pipeline)
  * Kibana Dashboards (Data visualization for Elasticsearch)

### 10. MLOps

The intersection of Machine Learning, DevOps, and Data Engineering to manage the ML lifecycle.

* KubeFlow: A machine learning toolkit for Kubernetes.
* MLFlow: An open-source platform for managing the end-to-end ML lifecycle.

### 11. Real World Test (Career & Community)

Practical steps to translate technical skills into professional opportunities.

* LinkedIn:
  * SSI Score (Social Selling Index)
  * Profile Optimisation
  * Posting, Commenting, and Networking
* Resume:
  * ATS Friendly formatting
  * Keywords, Projects, and Best Practices
* Community:
  * Learn In Public
  * Meetups and Events
  * Challenges and Hackathons
* Generative AI tools:
  * Leveraging ChatGPT, Gemini, and Dall-e for productivity and learning.