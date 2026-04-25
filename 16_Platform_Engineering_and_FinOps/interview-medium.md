---
description: Medium-difficulty interview questions for Platform Engineering, IDP architecture, and FinOps strategy.
---

## Medium

**13. How do you measure the success of a platform team?**

Platform teams are often measured on:

1. **DORA metrics improvement:** Track baseline vs post-platform adoption. Did deployment frequency increase? Did lead time decrease?
2. **Developer satisfaction (Internal NPS):** Regular surveys asking "How easy is it to deploy a new service?" / "How confident are you in the reliability of the platform?"
3. **Self-service adoption rate:** What % of developers use the golden path vs manual approaches?
4. **Onboarding time:** How long does it take a new engineer to deploy their first production service?
5. **Incident rate attributable to platform:** Track whether platform-provisioned infrastructure causes fewer incidents than manually configured infrastructure.

Avoid measuring platform teams purely on output (number of features shipped) — measure impact on developer productivity.

**14. What is the "paved road" philosophy and how does it avoid becoming a bottleneck?**

A paved road is a well-maintained, opinionated path that makes doing things correctly the default. The key to not being a bottleneck:
- **Make the recommended path easier, not mandatory.** Teams can deviate, but they own the support burden.
- **Design for 80% of use cases.** Provide escape hatches (raw Terraform, direct K8s access) for edge cases — don't force everything through the platform.
- **Self-service by default.** A platform that requires the platform team to be involved in every provisioning request is not self-service — it's a faster ticket system.
- **Treat developers as customers.** Run user research, gather feedback, prioritize based on impact.

**15. How does Crossplane's Composition model work?**

Crossplane uses a two-layer model:

1. **Composite Resource Definition (XRD):** The platform team defines a high-level API (e.g., `PostgreSQLInstance`) with a simple set of fields (`storageGB`, `version`, `region`).
2. **Composition:** The platform team defines how a `PostgreSQLInstance` maps to real cloud resources — an RDS instance, a parameter group, a subnet group, security groups, and a SecretsManager secret. Developers never see these details.
3. **Claim:** A developer creates a `PostgreSQLInstance` claim in their namespace. Crossplane's controller provisions all the underlying resources. Connection details are written back as a Kubernetes Secret.

This gives developers a self-service, cloud-agnostic API that automatically enforces organizational standards (encryption, backup retention, tagging).

**16. How do you implement FinOps for Kubernetes workloads specifically?**

Kubernetes cost management requires additional tooling beyond cloud billing:

1. **Cost attribution by namespace/label:** Install Kubecost or OpenCost. They calculate per-pod cost by allocating node costs proportionally to CPU/memory requests.
2. **Efficiency reporting:** Identify pods where requested resources >> actual usage. Efficiency = (actual usage / requested). Efficiency below 40% indicates right-sizing opportunity.
3. **Chargeback by team:** Map namespaces to teams via labels. Export per-namespace cost to a shared dashboard accessible to each team.
4. **VPA recommendations:** Use VPA in recommendation mode (`--dry-run`) to suggest right-sized resource requests without automatically changing them.
5. **Spot instance pools:** Run dev/staging and stateless production workloads on Spot nodes. Tag workloads with `workload-type: batch` to allow scheduling on Spot with proper tolerations.

**17. What are the risks of building your own IDP from scratch vs using Backstage?**

**Build from scratch:**
- Pro: Perfectly tailored to your organization's specific tools and workflows.
- Con: Requires significant ongoing engineering investment; you become responsible for all maintenance, security, and feature development. Most organizations underestimate the true cost.

**Backstage:**
- Pro: Large community, 200+ plugins, established patterns for software catalog and scaffolding.
- Con: Backstage is a framework, not a product — it requires significant customization and hosting. Initial setup is non-trivial.

Reality check: Most organizations spend 6-12 months customizing Backstage to be genuinely useful. The catalog is the highest ROI starting point — just getting service ownership documented provides immediate value.

**18. How do you handle infrastructure versioning and upgrades across hundreds of teams using a shared platform?**

**Semantic versioning for platform components:**
- Platform team publishes versioned Terraform modules, Helm charts, and Backstage templates with a changelog.
- Teams pin to a specific version: `source = "terraform-modules/vpc?ref=v3.2.0"`.

**Upgrade strategy:**
1. Publish a new version; announce breaking changes in the changelog.
2. Update the platform's "recommended version" in the catalog.
3. Create automated PRs across all consumer repos via a tool like Renovate or a custom script that opens PRs bumping module versions.
4. Run a compatibility test matrix — test new module versions against common consumer configurations.
5. Deprecation window: support N-1 versions; provide a migration guide for each major version.

**19. What is platform engineering's relationship with SRE?**

These are often confused but distinct:
- **SRE** is responsible for the reliability of production services — incident response, SLO management, postmortems, and capacity planning.
- **Platform Engineering** is responsible for building the tools, infrastructure, and APIs that developers and SREs use.

The platform team creates the paved road; the SRE team uses and maintains that road for critical services. In many organizations, platform engineers embed reliability practices (SLO templates, runbook generators) into the platform itself — reducing the burden on each individual SRE.

**20. How do you calculate and act on cloud unit economics?**

Unit economics connects cloud spend to business value:

```
Cost per API request = Monthly cloud cost / Monthly API requests
Cost per user       = Monthly cloud cost / Monthly active users
```

**How to use it:**
1. Set up cost and usage data in a data warehouse (Athena + CUR in AWS).
2. Join with product metrics from your analytics platform.
3. Track the trend: if cost per user decreases as users grow = efficient scaling. If it increases = architectural inefficiency.
4. Set alerts: if cost per request rises above a threshold → trigger an architecture review.
5. Use for capacity planning: "We expect 5x user growth → project cloud cost" rather than guessing.
