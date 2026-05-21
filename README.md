# DevOps Interview Handbook & Senior Learning Roadmap

```
DevOps Interview Handbook & Senior Learning Roadmap
├── Tool Directories (19 topic areas)
│   ├── 01_Linux_and_Scripting       ── Linux admin, shell scripting, performance hardening
│   ├── 02_Networking                ── TCP/IP, DNS, TLS, load balancing, VPNs
│   ├── 03_Git_and_Version_Control   ── workflows, branching strategies, monorepos
│   ├── 04_Docker                    ── fundamentals, networking, runtimes, security
│   ├── 05_Kubernetes                ── cluster ops, RBAC, networking, troubleshooting
│   ├── 06_Jenkins                   ── pipeline design, shared libraries, CI/CD patterns
│   ├── 07_GitHub_Actions            ── workflows, OIDC, reusable actions
│   ├── 08_GitLab_CI                 ── pipelines, runners, security scanning
│   ├── 09_ArgoCD_and_GitOps         ── GitOps patterns, progressive delivery, ApplicationSets
│   ├── 10_Terraform                 ── IaC patterns, state management, modules, Sentinel
│   ├── 11_Ansible                   ── configuration management, playbooks, roles
│   ├── 12_Azure                     ── AKS, Azure Policy, networking, identity, pipelines
│   ├── 13_AWS                       ── EKS, IAM, multi-account Organizations, serverless
│   ├── 14_DevSecOps                 ── SAST/DAST, SLSA, SBOM, OPA, Falco, supply chain
│   ├── 15_Observability_and_SRE     ── SLO/SLI, Prometheus, tracing, chaos engineering
│   ├── 16_Platform_Engineering_and_FinOps ── IDP, Backstage, Crossplane, DORA, cost optimization
│   ├── 17_MLOps                     ── feature stores, CT pipelines, model serving, LLMOps
│   ├── 18_Helm                      ── Helm fundamentals, charts, package management
│   └── 19_Kong                      ── API gateway, plugin architecture, routing, hybrid topology
├── Learning_Path/
│   ├── README.md                    ── 4-phase curriculum overview, 12-week track
│   ├── phase-1-foundations.md       ── Linux, Git, scripting, networking
│   ├── phase-2-platform-and-delivery.md ── cloud, CI/CD, containers, Kubernetes, Terraform
│   ├── phase-3-sre-and-operations.md ── observability, troubleshooting, reliability
│   ├── phase-4-senior-role-readiness.md ── architecture, leadership, governance
│   └── capstone-projects.md         ── 3 capstones + IDP stretch project
├── Interview Prep (per-tool interview.md files)
│   ├── Easy / Medium / Hard sections in each tool directory
│   └── Supporting playbooks, scenario drills, STAR guides
└── Supporting Guides
    ├── system-design.md             ── 10 design problems with mindmap + first principles
    ├── behavioral.md                ── STAR stories, leadership anchors, 90-day framework
    └── SUMMARY.md                   ── GitBook-style table of contents
```

## First Principles

- **Why a structured knowledge base?** Tool knowledge is shallow without connection to systems thinking. Grouping by tool forces coverage of every domain, so gaps become visible.
- **Why merge easy/medium/hard into one file per tool?** Real interviews escalate in the same conversation. Having all levels in one file trains the habit of knowing when to go deeper.
- **Why a learning path on top of reference material?** Reference material answers "what." A learning path answers "what next" — the sequencing is the pedagogy.
- **Why capstone projects?** Employers hire on demonstrated judgment, not memorized answers. A capstone converts reading into a concrete story with outcomes.
- **Why cross-reference maintenance (SUMMARY.md, README.md)?** Knowledge bases decay when links break. A navigable index forces discipline on structure as content grows.
- **Why separate behavioral and system-design files?** These require different practice modes — behavioral needs narrative rehearsal, system design needs whiteboard structure. Splitting them makes deliberate practice possible.

Tool-specific knowledge base for DevOps, SRE, Platform Engineering, and MLOps. Each folder contains a comprehensive `interview.md` covering all difficulty levels plus supporting reference material.

## Directory Structure

| # | Directory | Focus |
|---|-----------|-------|
| 01 | `01_Linux_and_Scripting/` | Linux administration, shell scripting, performance |
| 02 | `02_Networking/` | TCP/IP, DNS, TLS, load balancing, VPNs |
| 03 | `03_Git_and_Version_Control/` | Git workflows, branching strategies, monorepos |
| 04 | `04_Docker/` | Container fundamentals, networking, security, runtimes |
| 05 | `05_Kubernetes/` | Cluster operations, networking, RBAC, troubleshooting |
| 06 | `06_Jenkins/` | Pipeline design, CI/CD patterns, shared libraries |
| 07 | `07_GitHub_Actions/` | Workflows, OIDC, reusable actions |
| 08 | `08_GitLab_CI/` | GitLab pipelines, runners, security scanning |
| 09 | `09_ArgoCD_and_GitOps/` | GitOps patterns, progressive delivery, ApplicationSets |
| 10 | `10_Terraform/` | IaC patterns, state management, modules, Sentinel |
| 11 | `11_Ansible/` | Configuration management, playbooks, roles |
| 12 | `12_Azure/` | AKS, Azure Policy, networking, identity, pipelines |
| 13 | `13_AWS/` | EKS, IAM, multi-account Organizations, serverless |
| 14 | `14_DevSecOps/` | SAST/DAST, supply chain, SLSA, OPA, Falco, SBOM |
| 15 | `15_Observability_and_SRE/` | SLO/SLI, Prometheus, tracing, chaos engineering |
| 16 | `16_Platform_Engineering_and_FinOps/` | IDP, Backstage, Crossplane, DORA metrics, cost optimization |
| 17 | `17_MLOps/` | Feature stores, CT pipelines, model serving, LLMOps |
| 18 | `18_Helm/` | Helm charts, package management, templates, releases |
| 19 | `19_Kong/` | API gateway, plugin architecture, routing, hybrid CP/DP topology |
| — | `Learning_Path/` | 4-phase structured curriculum from foundations to senior |

## Interview Prep Quick Reference

| Topic | Interview File |
|-------|---------------|
| Linux & Scripting | [01_Linux_and_Scripting/interview.md](01_Linux_and_Scripting/interview.md) |
| Networking | [02_Networking/interview.md](02_Networking/interview.md) |
| Git | [03_Git_and_Version_Control/interview.md](03_Git_and_Version_Control/interview.md) |
| Docker | [04_Docker/interview.md](04_Docker/interview.md) |
| Kubernetes | [05_Kubernetes/interview.md](05_Kubernetes/interview.md) |
| Jenkins / CI | [06_Jenkins/interview.md](06_Jenkins/interview.md) |
| GitHub Actions | [07_GitHub_Actions/interview.md](07_GitHub_Actions/interview.md) |
| GitLab CI | [08_GitLab_CI/interview.md](08_GitLab_CI/interview.md) |
| ArgoCD / GitOps | [09_ArgoCD_and_GitOps/interview.md](09_ArgoCD_and_GitOps/interview.md) |
| Terraform | [10_Terraform/interview.md](10_Terraform/interview.md) |
| Ansible | [11_Ansible/interview.md](11_Ansible/interview.md) |
| Azure | [12_Azure/interview.md](12_Azure/interview.md) |
| AWS | [13_AWS/interview.md](13_AWS/interview.md) |
| DevSecOps | [14_DevSecOps/interview.md](14_DevSecOps/interview.md) |
| Observability & SRE | [15_Observability_and_SRE/interview.md](15_Observability_and_SRE/interview.md) |
| Platform Engineering & FinOps | [16_Platform_Engineering_and_FinOps/interview.md](16_Platform_Engineering_and_FinOps/interview.md) |
| MLOps | [17_MLOps/interview.md](17_MLOps/interview.md) |
| Helm | [18_Helm/interview.md](18_Helm/interview.md) |
| Kong | [19_Kong/interview.md](19_Kong/interview.md) |
