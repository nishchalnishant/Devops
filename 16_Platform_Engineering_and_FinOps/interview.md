# Platform Engineering & FinOps — Interview Questions

All difficulty levels combined.

---

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

---

## Medium

**6. What is the difference between an IDP and a CI/CD pipeline?**

A CI/CD pipeline is a workflow for building, testing, and deploying a single service. An IDP abstracts all platform complexity — compute, networking, secrets, databases, monitoring, environments — behind a developer-facing interface. The IDP coordinates CI/CD, GitOps, and infrastructure provisioning as an integrated workflow, automating what currently requires manual tickets and handoffs between teams.

**7. How do you enforce cloud resource tagging across 50 engineering teams?**

Tagging taxonomy (minimum required tags):
```
team: payments
environment: production
project: checkout-v2
managed-by: terraform
owner: john.doe@co.com
```

Enforcement:
- **OPA/Gatekeeper ConstraintTemplate:** Block Kubernetes resources without required labels.
- **Azure Policy / AWS SCP:** Deny resource creation without mandatory tags at the subscription/account level.
- **Terraform Sentinel:** Fail `terraform apply` if a planned resource is missing required tags.
- **Weekly audit:** Run Kubecost/Infracost to generate a "tag debt" report and publish a team compliance leaderboard.

**8. How do you reduce Kubernetes compute costs by 40% without degrading reliability?**

Multi-lever approach:
1. **Right-size requests:** `kubectl top pod` reveals pods requesting 4 CPU but using 200m. Set requests to P95 of actual usage with 20% headroom. Use VPA in recommendation mode to surface suggestions.
2. **Spot/preemptible nodes:** Move stateless workloads (web, workers) to spot node pools. Use PodDisruptionBudgets for graceful eviction.
3. **Node bin-packing:** Ensure all pods have resource requests set (Cluster Autoscaler needs them). Use topology spread constraints to pack small pods onto fewer nodes.
4. **Off-hours scaling:** Scale dev/staging clusters to zero using KEDA cron scaler or scheduled scale-down.
5. **Reserved capacity:** Commit 1-year Savings Plans/Reserved Instances for the baseline on-demand floor (~60-70% of baseline cost at 30-40% discount).
6. **Cleanup:** Remove Helm releases for unused services, PVCs without active pods, load balancers without backends.

**9. What is Backstage and what problem does it solve?**

Backstage (CNCF) is an open-source developer portal framework originally built at Spotify. It solves the "cognitive load" problem — as an organization grows, engineers spend increasing time finding documentation, understanding service ownership, onboarding to new services, and navigating disparate tooling. Backstage provides a centralized software catalog (all services, APIs, and infrastructure), Software Templates for self-service scaffolding, and a plugin system that brings CI/CD status, cloud costs, on-call rotations, and tech docs into a single pane of glass.

**10. What is Crossplane and how does it enable platform engineering?**

Crossplane is a Kubernetes-native control plane for infrastructure. It lets platform teams define Composite Resource Definitions (XRDs) that abstract cloud resources — a team creates a `DatabaseClaim` Kubernetes resource and Crossplane provisions an actual RDS/Azure SQL instance, configures networking, and creates the Kubernetes Secret with connection details. Infrastructure becomes a Kubernetes API — developers provision resources using `kubectl apply` or GitOps, with the same interface they use for applications.

---

## Hard

**11. Design a golden path template system for 50 development teams using Backstage and Crossplane.**

Architecture:

- **Backstage Software Templates:** Define the developer-facing form (service name, language, database type, environment targets). The template scaffolds a Git repo from a standard project layout, registers the entity in Backstage's catalog, and creates the necessary Crossplane claims via GitOps.
- **Crossplane XRCs:** A `DatabaseClaim` triggers Crossplane's Composite Resource which provisions RDS/Azure SQL, creates a Kubernetes Secret with connection details, and registers the resource in Backstage.
- **GitOps layer:** Backstage templates write ArgoCD ApplicationSet configs into the platform GitOps repo; ArgoCD detects and deploys automatically.
- **Governance:** OPA Gatekeeper validates that claims reference only approved regions and sizes. FinOps tags are injected automatically from team metadata in Backstage's catalog.
- **Observability:** Grafana dashboards and PagerDuty on-call routes are provisioned by the template and linked in the Backstage entity page.

**12. How do you measure platform engineering ROI with DORA metrics?**

Collect baselines before IDP adoption and compare 6-12 months after:

- **Deployment Frequency:** Track deployment event records in CI/CD. Elite: multiple deploys/day per service. Before/after comparison shows reduced manual handoffs.
- **Lead Time for Changes:** Commit to production timestamp delta. Self-service environments reduce wait time for provisioning.
- **Change Failure Rate:** Correlate deployments with incident creation in PagerDuty/Jira. Golden paths bake in compliance and testing, reducing defect rate.
- **MTTR:** Incident creation to resolution time. Standardized runbooks and self-service rollback reduce restoration time.

Present as: "Before IDP: weekly deploy frequency, 5-day lead time. After: daily deploys, 2-day lead time, 30% fewer rollbacks." Supplement with DevEx surveys measuring cognitive load reduction and time saved on toil.

**13. What is platform toil and how do you engineer it away?**

Toil is repetitive, manual, automatable work that scales linearly with service count: creating environments, rotating credentials, onboarding services to monitoring, renewing SSL certificates. Platform engineering quantifies and eliminates it:

- **Self-service environments via IDP templates:** Eliminates environment provisioning toil.
- **External Secrets Operator:** Automatic secret sync from Vault eliminates credential rotation toil.
- **Automated catalog registration via CI hooks:** Eliminates service onboarding toil.
- **cert-manager:** Automatic TLS certificate issuance and renewal eliminates certificate toil.

Measure: track engineer-hours spent on toil before and after. If automation reduces it below 10% of engineering time, the investment is justified. Target: SRE teams spend < 50% of time on toil per Google's SRE book guidance.

**14. Design a cost-effective and resilient Kubernetes cluster using EC2 Spot Instances.**

1. **Diversified node pools:** Use Karpenter with multiple `NodePool` resources targeting diverse instance families (m5, m5a, c5, c5a) across all AZs. Diversification reduces interruption risk — if one type's Spot capacity is reclaimed, others absorb the workload.
2. **AWS Node Termination Handler:** DaemonSet watching for Spot interruption notices from the EC2 metadata service — gracefully cordons and drains the node within the 2-minute window.
3. **Workload design:** Stateless workloads (web, workers) on Spot; stateful workloads (databases) on On-Demand nodes with taints.
4. **PodDisruptionBudgets:** Every production Deployment has a PDB maintaining minimum available replicas during drains.
5. **On-demand floor:** Maintain a small on-demand pool (10-20% of capacity) so Spot interruptions don't drain the cluster below minimum. Cover this baseline with Savings Plans at 30-40% discount.

**15. What is the FOCUS spec and why does it matter for multi-cloud cost attribution?**

FOCUS (FinOps Open Cost and Usage Specification) is a vendor-neutral billing data schema standardizing how cloud providers expose cost data. Each provider uses different field names: AWS has `BlendedCost` and `UnblendedCost`; Azure has `PreTaxCost`; GCP has `cost` plus a separate `credits` array. FOCUS defines canonical fields: `BilledCost` (actual payment), `EffectiveCost` (amortized including reservations), `ResourceId`, `ServiceName`, `ProviderName`. When all cloud bills are normalized to FOCUS, a single query in BigQuery or Databricks shows cross-cloud spend by team or service without per-provider parsing logic — enabling true multi-cloud cost governance.

**16. How do you achieve zero-downtime database schema migrations?**

Direct `ALTER TABLE` on large tables causes long locks. Safe patterns:

1. **Expand-contract:** (1) Add column as `NULL` — fast, no lock. (2) Backfill in batches (1000 rows per transaction with sleep between batches). (3) Add `NOT NULL` constraint with `NOT VALID` in PostgreSQL — validates new writes without scanning old rows. (4) `VALIDATE CONSTRAINT` during off-peak hours. (5) Future migration drops the old column.
2. **Online schema change tools:** `gh-ost` (MySQL) creates a shadow table, applies ongoing binlog changes, cuts over with a brief lock. `pg_repack` for PostgreSQL.
3. **Dual-write:** Application writes to both old and new schema during migration, enabling rollback by reverting application code without data loss.

**17. What is PgBouncer and how does it solve the "too many connections" problem?**

Each PostgreSQL connection spawns a backend process consuming ~5-10MB RAM. With 1000 pods each opening 10 connections, that's 10,000 Postgres backends — far beyond `max_connections`. PgBouncer is a connection pooler: applications connect to PgBouncer (which handles thousands of application connections), and PgBouncer maintains a smaller real pool (e.g., 100 connections) to PostgreSQL. In transaction pooling mode, a database connection is assigned to a client only during an active transaction and returned to the pool immediately after — enabling thousands of application connections to share tens of database connections.
