# Platform Engineering & FinOps

Comprehensive reference for Internal Developer Platforms, self-service infrastructure,
FinOps practices, and organizational engineering productivity.

***

## What Is in This Module

| File | Purpose |
|:---|:---|
| `cheatsheet.md` | IDP tooling commands, Backstage, Crossplane, Kubecost, DORA metrics |
| `interview-easy.md` | Foundational: IDP, Golden Path, Backstage, DORA, FinOps basics |
| `interview-medium.md` | Intermediate: Crossplane Composition, K8s FinOps, platform metrics, architecture |
| `interview-hard.md` | Advanced: IDP at scale, Backstage architecture, multi-cloud FinOps |
| `scenarios.md` | Real-world platform engineering troubleshooting and design scenarios |
| `notes/platform-engineering-idp.md` | Deep dive into IDP architecture and Backstage |
| `notes/finops-cost-optimization.md` | Cloud cost optimization strategies and tooling |

***

## Platform Engineering in Context

```
Without Platform Engineering:
  Developer → reads 50-page wiki → creates 10 tickets → waits 2 weeks → deploys

With a Mature IDP:
  Developer → opens Backstage → clicks "New Service" template → 25 minutes later:
    ✓ GitHub repo created
    ✓ CI/CD pipeline configured
    ✓ Container registry namespace provisioned
    ✓ Kubernetes namespace + RBAC configured
    ✓ ArgoCD Application created
    ✓ PagerDuty service registered
    ✓ Grafana dashboard provisioned
```

***

## DORA Metrics — Elite Performance Benchmarks

| Metric | Low | Medium | High | Elite |
|:---|:---|:---|:---|:---|
| **Deployment Frequency** | Monthly | Weekly | Daily | Multiple/day |
| **Change Lead Time** | 1-6 months | 1 week–1 month | 1 day–1 week | < 1 hour |
| **Change Failure Rate** | 46-60% | 16-30% | 1-15% | < 5% |
| **MTTR** | 1 week+ | 1 day–1 week | < 1 day | < 1 hour |

The platform team's primary goal: **move teams from Medium to High/Elite on all four metrics**.

***

## Interview Focus Areas

| Difficulty | Key Topics |
|:---|:---|
| **Easy** | IDP definition, Golden Path, Backstage, DORA, FinOps, show-back vs chargeback, Crossplane basics |
| **Medium** | Platform team measurement, Crossplane Composition model, K8s FinOps (Kubecost), Backstage build vs buy, platform versioning |
| **Hard** | IDP at scale (200+ teams), Backstage plugin architecture, multi-cloud cost management, unit economics, platform-as-a-product |

***

## Key Tools & Technologies

| Category | Tool | Purpose |
|:---|:---|:---|
| **IDP Portal** | Backstage | Service catalog + scaffolding + TechDocs |
| **IaC Self-Service** | Crossplane | K8s-native cloud resource provisioning |
| **Cost Visibility** | Kubecost / OpenCost | K8s namespace-level cost allocation |
| **Cost Optimization** | Infracost | Pre-commit IaC cost estimation |
| **DORA Metrics** | Sleuth / LinearB / GitLab | Deployment frequency, lead time tracking |
| **Feature Flags** | LaunchDarkly / Flagsmith | Progressive delivery without redeployment |
| **Developer Experience** | Compass / Port | Service scorecard and onboarding maturity |

***

## FinOps at a Glance

```
FinOps Cycle:
  1. INFORM — Who spends what? (tagging, cost allocation, dashboards)
  2. OPTIMIZE — Reduce waste (rightsizing, spot, RIs/Savings Plans)
  3. OPERATE — Set budgets, create accountability, measure unit economics

Key Levers (in order of typical ROI):
  1. Eliminate waste (unattached volumes, idle instances, zombie environments): 20-30% savings
  2. Rightsize over-provisioned instances: 15-25% savings
  3. Spot/preemptible for batch/stateless workloads: 50-70% savings on those workloads
  4. Committed Use (RIs/Savings Plans) for baseline: 30-60% savings vs on-demand
  5. Architectural optimization (serverless, storage tiering): 30-50% on specific workloads
```
