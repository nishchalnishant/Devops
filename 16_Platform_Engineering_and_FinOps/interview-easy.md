---
description: Easy interview questions for Platform Engineering, IDP, FinOps, and DevEx fundamentals.
---

## Easy

**1. What is Platform Engineering?**

Platform Engineering is the discipline of building and maintaining internal tools, platforms, and infrastructure that enable development teams to ship software faster and more reliably. A platform engineer reduces the cognitive load on developers by providing self-service capabilities — provisioning infrastructure, setting up CI/CD, managing security baselines — without requiring deep operational expertise from every team.

**2. What is an Internal Developer Platform (IDP)?**

An Internal Developer Platform is a layer of tooling and automation that abstracts infrastructure complexity from developers. Instead of opening tickets to provision resources or configure CI/CD, developers interact with a portal, CLI, or API. The platform team builds and maintains the IDP; application teams consume it. Key components: a self-service portal (often Backstage), infrastructure automation (Terraform/Crossplane), and a deployment system (ArgoCD).

**3. What is the Golden Path?**

The Golden Path is the recommended, pre-built, fully-supported way to do common development tasks in an organization — create a new service, set up CI/CD, provision a database. The platform team invests in making the golden path easy and opinionated. Crucially, it's not mandatory — teams can deviate, but they own the support burden. The goal is that the "right way" is also the "easy way."

**4. What is Backstage and what problem does it solve?**

Backstage (by Spotify, now CNCF) is an open-source framework for building Internal Developer Platforms. It provides:
- **Software Catalog:** A searchable registry of all services, APIs, libraries, and their owners.
- **Software Templates (Scaffolding):** Wizards that let developers create a new service with proper CI/CD, infra, and registry registration in one click.
- **TechDocs:** Documentation-as-code, auto-generated and co-located with service source code.
- **Plugin ecosystem:** Integrations with GitHub, Kubernetes, PagerDuty, CI/CD tools, and cost platforms.

**5. What are DORA metrics?**

DORA (DevOps Research and Assessment) metrics are four key measures of software delivery performance:
- **Deployment Frequency:** How often code is deployed to production (elite = multiple times/day).
- **Change Lead Time:** Time from commit to production deployment (elite = < 1 hour).
- **Change Failure Rate:** Percentage of deployments that cause incidents (elite = < 5%).
- **Mean Time to Recover (MTTR):** Time to restore service after an incident (elite = < 1 hour).

High performers on all four metrics are 2x more likely to exceed organizational goals compared to low performers.

**6. What is FinOps?**

FinOps (Financial Operations) is a cloud financial management practice that brings financial accountability to cloud spending. The goal is not to minimize spend — it's to maximize business value per dollar. It involves three phases: **Inform** (understand who spends what), **Optimize** (reduce waste, use commitments), and **Operate** (set budgets, create accountability culture). FinOps is typically a cross-functional effort between Engineering, Finance, and Business teams.

**7. What is cloud cost allocation and why is tagging critical?**

Cost allocation is the process of attributing cloud spend to specific teams, services, or cost centers. Without tagging, all cloud costs appear as one large bill with no visibility into who spent what. Tagging resources (e.g., `team=payments`, `environment=production`, `service=checkout-api`) enables cost reports filtered by these dimensions. AWS Cost Explorer, Azure Cost Management, and GCP Billing can group costs by tag — but only for tags marked as cost allocation tags.

**8. What is the difference between show-back and chargeback?**

- **Show-back:** Teams can see their cloud costs in a report, but the costs are not actually deducted from their budget. Good for raising awareness without creating friction.
- **Chargeback:** Teams are actually billed for their cloud usage against their team budget. Creates strong accountability but requires mature cost attribution and clear ownership.

Most organizations start with show-back to build the tagging and reporting foundation, then graduate to chargeback.

**9. What is a Reserved Instance (RI) vs a Savings Plan in AWS?**

Both offer discounts on cloud spend in exchange for a commitment:
- **Reserved Instance:** Commit to a specific instance type in a specific region for 1 or 3 years. Highest discount (~75%) but least flexible.
- **Savings Plan (Compute):** Commit to a dollar amount of EC2 usage per hour for 1 or 3 years. Applies across any instance type, region, or OS. ~66% discount with much more flexibility.

Best practice: use Compute Savings Plans for your stable baseline workload. Use On-Demand for burst. Use Spot for batch and stateless workloads.

**10. What is Crossplane?**

Crossplane is a CNCF project that extends Kubernetes with CRDs for cloud resources. It allows teams to provision and manage AWS, GCP, and Azure resources using `kubectl apply` — the same workflow as deploying applications. The platform team defines "Compositions" (opinionated, pre-approved resource templates); developers create "Claims" against these Compositions without needing cloud console access. This enables self-service infrastructure that adheres to organizational standards automatically.

**11. What is a self-service maturity model for a platform team?**

| Level | Description |
|:---|:---|
| L0 — Manual | Manual tickets, week-long wait for resources |
| L1 — Documented | Runbooks exist, humans execute them |
| L2 — Automated | Scripts exist but require knowledge to run |
| L3 — Self-Service | Portal or API, no specialized knowledge needed |
| L4 — Invisible | Fully embedded in developer workflow; infrastructure appears automatically |

Most organizations sit between L1 and L2; the platform team's goal is to reach L3+ for their most common use cases.

**12. What is cognitive load in the context of platform engineering?**

Cognitive load is the mental effort required for a developer to do their job. Platform engineering aims to reduce cognitive load by hiding operational complexity — a developer shouldn't need to understand Kubernetes networking to deploy an application or know IAM policy syntax to provision a database. Tools like Backstage, Helm charts, and Crossplane Compositions are "load-reducing abstractions." High cognitive load correlates with slower delivery, more errors, and developer burnout.
