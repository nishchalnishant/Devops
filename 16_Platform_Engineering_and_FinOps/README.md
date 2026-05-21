# Platform Engineering & FinOps

```
Platform Engineering & FinOps
├── Internal Developer Platform (IDP)
│   ├── Definition: self-service layer abstracting infra complexity
│   ├── Without IDP: ticket → wait 2 weeks → deploy
│   ├── With IDP: Backstage template → 25 min → full stack provisioned
│   └── Self-service maturity: L0 (manual) → L4 (invisible)
├── Backstage
│   ├── Software Catalog: searchable registry of services + owners
│   ├── Software Templates (Scaffolding): one-click service creation
│   ├── TechDocs: docs-as-code co-located with source
│   └── Plugin ecosystem: GitHub, K8s, PagerDuty, Grafana, cost
├── Golden Path
│   ├── Opinionated, pre-built, fully-supported way to deploy
│   ├── Makes correct path the easy path (not mandatory)
│   └── Teams can deviate but own the support burden
├── Crossplane
│   ├── K8s CRDs for cloud resources (AWS, GCP, Azure)
│   ├── XRD: platform-defined high-level API (PostgreSQLInstance)
│   ├── Composition: maps XRD to real cloud resources
│   └── Claim: developer request that triggers provisioning
├── DORA Metrics
│   ├── Deployment Frequency (elite: multiple/day)
│   ├── Change Lead Time (elite: < 1 hour)
│   ├── Change Failure Rate (elite: < 5%)
│   └── MTTR (elite: < 1 hour)
├── FinOps
│   ├── Inform: tagging, cost allocation, dashboards
│   ├── Optimize: rightsizing, spot, RIs/Savings Plans
│   └── Operate: budgets, accountability, unit economics
└── Key Tools
    ├── Backstage (IDP portal)
    ├── Crossplane (K8s-native IaC)
    ├── Kubecost / OpenCost (K8s cost)
    ├── Infracost (pre-commit IaC cost)
    └── Sleuth / LinearB (DORA tracking)
```

## First Principles

- Developers repeat the same infra setup across every new service — abstract it into a self-service platform (IDP) so the platform team builds once and every developer benefits.
- Golden paths reduce cognitive load: the recommended way must also be the easiest way, or developers will route around it.
- Backstage is a portal for discoverability — it answers "who owns this service?" and "how do I create a new one?" without opening a ticket.
- Crossplane provisions infra via Kubernetes CRDs — treat cloud resources the same way you treat Pods: declare desired state, let a controller reconcile.
- FinOps: cloud cost is variable and invisible by default — tie cost to value by tagging every resource and tracking spend per team, service, and product.
- The platform team is not a ticket system — if developers still need the platform team for every provisioning request, the platform has not achieved self-service.

Comprehensive reference for Internal Developer Platforms, self-service infrastructure,
FinOps practices, and organizational engineering productivity.

***

## What Is in This Module

| File | Purpose |
|:---|:---|
| `cheatsheet.md` | IDP tooling commands, Backstage, Crossplane, Kubecost, DORA metrics |
| `interview.md` | Consolidated Interview Questions: Easy, Medium, and Hard levels |
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

***

## System Design Perspective

**VPC Peering vs Transit Gateway:** VPC Peering is direct, non-transitive, and suited for 2-5 VPCs with non-overlapping CIDRs. Transit Gateway is a managed cloud router that enables transitive routing, scales to thousands of VPCs, supports VPN and Direct Connect attachments, and allows inter-region peering. Cost: TGW charges per attachment plus per GB processed; use VPC Endpoints alongside TGW to keep S3/DynamoDB traffic off the TGW.

**Identity Federation (OIDC/SAML):** IRSA (IAM Roles for Service Accounts) uses OIDC federation — the EKS cluster's OIDC issuer is registered in IAM, and pods exchange a projected ServiceAccount JWT for temporary STS credentials via sts:AssumeRoleWithWebIdentity. GitHub Actions and GitLab CI use the same pattern to assume IAM roles without storing access keys. SAML 2.0 is used for AWS SSO federation with enterprise IdPs (Okta, Azure AD).

**Cross-Region DR:** Strategy selection depends on RTO/RPO targets. Backup and Restore (hours RTO, cheapest) uses S3 CRR plus RDS snapshots. Pilot Light (30 min RTO) keeps minimal standby infra running. Warm Standby (minutes RTO) runs a reduced-scale active stack. Active-Active (near-zero RTO) uses Route 53 latency routing plus Aurora Global Database with less than 1s replication lag. All strategies require IaC — without it, failover cannot meet aggressive RTOs.

**Cost Allocation Tagging Strategy:** Enforce mandatory tags (Environment, Team, CostCenter, Owner) via AWS Config Rules or SCPs requiring tags on resource creation. Use AWS Cost Explorer grouped by tag to produce per-team cost reports. Activate cost allocation tags in the Billing Console. Use Tag Policies in AWS Organizations to standardize tag key formats across accounts.

**Managed Identity vs Service Principals (AWS context):** IAM Roles are the equivalent of Managed Identities — they provide temporary credentials without stored secrets. Long-term access keys (equivalent to Service Principals with secrets) should only exist for external systems that cannot assume roles. IRSA and ECS task roles are the pod/task-level equivalent of Azure Workload Identity.

**AWS Organizations SCPs vs Azure Policy:** SCPs define the maximum permissions ceiling per OU/account — they cannot grant permissions, act before IAM evaluation, and even the root user cannot exceed them. Azure Policy enforces at the ARM API layer with richer effects (Deny, Audit, DeployIfNotExists, Modify). Both use hierarchical policy inheritance but differ in execution layer: SCPs block at the IAM authorization step; Azure Policy intercepts at the resource provider level and supports auto-remediation.