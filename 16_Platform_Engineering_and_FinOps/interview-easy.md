## Easy

**1. What is Platform Engineering?**

Platform Engineering builds and maintains the internal tools, infrastructure, and workflows that enable development teams to deliver software efficiently and reliably. A platform team owns the shared infrastructure, CI/CD systems, observability stack, and developer tooling — abstracting operational complexity so application teams focus on product features rather than infrastructure management.

**2. What is a golden path in software delivery?**

A golden path is the recommended, pre-approved route for building and deploying a service — a set of opinionated defaults (framework, CI pipeline, observability, security scanning, deployment model) that are pre-configured and known to be compliant. Teams are free to deviate but are not supported when they do. Golden paths reduce cognitive load and enforce standards without mandating them.

**3. What is FinOps?**

FinOps (Financial Operations) is a cloud financial management discipline where engineering, finance, and business teams collaborate to optimize cloud spend. The core practice is making cost visibility data-driven and assigning cost accountability to the teams that generate it — rather than treating cloud bills as a central overhead.

**4. What is a DORA metric?**

DORA (DevOps Research and Assessment) identified four metrics that predict high software delivery performance: Deployment Frequency (how often to production), Lead Time for Changes (commit to production), Change Failure Rate (% of deployments causing incidents), and Mean Time to Restore (MTTR from incident to recovery). Elite performers deploy multiple times per day with lead times under an hour.

**5. What is an Internal Developer Platform (IDP)?**

An IDP is a self-service layer that abstracts platform infrastructure behind a developer-facing interface. Developers declare what they need ("a Python service with PostgreSQL in staging") and the IDP provisions the full stack using pre-approved templates. Tools: Backstage (portal), Crossplane (infrastructure API), Port, Humanitec.

***

