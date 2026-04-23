# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

Pure documentation knowledge-base — no build system, no tests, no runnable code. All content is Markdown. Tasks are authoring, editing, cross-referencing, and restructuring documentation.

## Content Architecture

Tool-specific top-level directories, each containing an `interview.md` (all difficulty levels merged) plus supporting reference material. Learning path content lives in a separate top-level directory.

| Dir | Purpose |
|-----|---------|
| `01_Linux_and_Scripting/` | Linux admin, shell scripting, performance hardening |
| `02_Networking/` | TCP/IP, DNS, TLS, load balancing, VPNs |
| `03_Git_and_Version_Control/` | Git workflows, branching, monorepos |
| `04_Docker/` | Container fundamentals, networking, runtimes, security |
| `05_Kubernetes/` | Cluster ops, networking, RBAC, troubleshooting |
| `06_Jenkins/` | Pipeline design, shared libraries, CI/CD patterns |
| `07_GitHub_Actions/` | Workflows, OIDC, reusable actions |
| `08_GitLab_CI/` | GitLab pipelines, runners, security scanning |
| `09_ArgoCD_and_GitOps/` | GitOps patterns, progressive delivery, ApplicationSets |
| `10_Terraform/` | IaC patterns, state management, modules, Sentinel |
| `11_Ansible/` | Configuration management, playbooks, roles |
| `12_Azure/` | AKS, Azure Policy, networking, identity, pipelines |
| `13_AWS/` | EKS, IAM, multi-account Organizations, serverless |
| `14_DevSecOps/` | SAST/DAST, SLSA, SBOM, OPA, Falco, supply chain |
| `15_Observability_and_SRE/` | SLO/SLI, Prometheus, tracing, chaos engineering |
| `16_Platform_Engineering_and_FinOps/` | IDP, Backstage, Crossplane, DORA, cost optimization |
| `17_MLOps/` | Feature stores, CT pipelines, model serving, LLMOps |
| `Learning_Path/` | 4-phase structured curriculum, capstone projects |

**`SUMMARY.md`** is the GitBook-style table of contents — keep it in sync when files are added, moved, or renamed.

## Interview File Convention

Every tool directory has a single `interview.md` with three sections: `## Easy`, `## Medium`, `## Hard`. All difficulty levels are merged into this one file. Do not split by difficulty into separate files.

## Cross-Reference Maintenance

When adding or modifying content:
1. Update `SUMMARY.md` with the new file path and title
2. Update `README.md` Quick Reference table if the topic is a top-level tool

## Searching Content

Use `rg` to find topics across the repo rather than reading full files:
```
rg -l "eBPF" .
rg -n "feature store" 17_MLOps/
rg -n "SLO" 15_Observability_and_SRE/
rg -n "IRSA" 13_AWS/
```
