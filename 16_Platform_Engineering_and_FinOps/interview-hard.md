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
# Scenario-Based DevOps Interview Drills

Use this file for final-round preparation. These scenarios are designed to test how you think under pressure, how you use evidence, and how clearly you can explain mitigation and prevention.

## How To Answer Scenario Questions

For each scenario, structure your answer like this:

1. Confirm impact and scope.
2. Check recent changes.
3. Look at user-facing metrics first.
4. Narrow the problem to app, container, node, network, database, or pipeline.
5. Run the smallest commands that can prove or reject your hypothesis.
6. Stabilize the system before chasing perfect root cause.
7. End with the long-term fix.

## Scenario 1: Flash Sale Meltdown On Kubernetes

### Prompt

Traffic jumped from 10k RPS to 150k RPS during a flash sale. The `checkout-service` is returning intermittent `504 Gateway Timeout` responses. The HPA has already scaled from 10 to 100 pods, but latency is still high. The database is not saturated.

### What A Strong Answer Should Cover

- Confirm the blast radius in Grafana: latency, error rate, request volume, and whether the issue is isolated to checkout.
- Check whether the problem is inside the pods, between services, or at the node or network layer.
- Explain why "pods scaled" does not mean "service is healthy."

### Commands You Can Name

- `kubectl top pod -l app=checkout-service`
- `kubectl describe deploy checkout-service`
- `kubectl logs -l app=checkout-service --tail=200`
- `kubectl get svc,ingress,endpoints`
- `kubectl describe node <node-name>`

### Likely Root Causes

- CPU throttling because limits are too low
- Application connection pool exhaustion
- Upstream dependency bottleneck such as Redis, queue, or payment provider
- Node-level networking pressure such as conntrack saturation
- Load balancer timeout mismatch

### Strong Mitigation Ideas

- Raise or right-size requests and limits if throttling is confirmed
- Increase pool size or reduce expensive query paths
- Enable rate limiting or load shedding
- Shift non-critical traffic away from the hot path
- Roll back a recent config or deployment if this started after a change

## Scenario 2: CrashLoopBackOff After Deployment

### Prompt

A new application version was deployed to Kubernetes. The new pods immediately enter `CrashLoopBackOff`, and the service has started failing health checks.

### What A Strong Answer Should Cover

- Separate startup failure from readiness failure.
- Inspect pod events before guessing.
- Check whether the issue is image, command, config, secret, probe, or resource related.

### Commands You Can Name

- `kubectl describe pod <pod-name>`
- `kubectl logs <pod-name> --previous`
- `kubectl get events --sort-by=.lastTimestamp`
- `kubectl rollout history deployment/<name>`
- `kubectl rollout undo deployment/<name>`

### Likely Root Causes

- Bad environment variable or secret reference
- Wrong entrypoint or command
- Dependency endpoint changed
- Probe misconfiguration
- OOMKilled during startup

### Strong Mitigation Ideas

- Roll back if the deployment is actively impacting users
- Disable the broken rollout and inspect diff against the last good release
- Add startup probes for slow-starting services
- Add config validation and smoke tests in CI/CD

## Scenario 3: Pod Stuck In Pending Or FailedScheduling

### Prompt

A critical workload is stuck in `Pending`. No new replica becomes ready, and the deployment is below the desired replica count.

### What A Strong Answer Should Cover

- Show that you know scheduling is based on requests, constraints, and storage placement.
- Mention node resources, taints, affinity rules, and persistent volumes.

### Commands You Can Name

- `kubectl describe pod <pod-name>`
- `kubectl get nodes`
- `kubectl describe node <node-name>`
- `kubectl get pvc,pv`
- `kubectl get events --sort-by=.lastTimestamp`

### Likely Root Causes

- Requests exceed allocatable CPU or memory
- Taints and tolerations do not match
- Wrong node selector or affinity rules
- PVC cannot bind or volume is tied to another zone
- Quota or limit range restriction

### Strong Mitigation Ideas

- Reduce requests only if they are clearly oversized
- Add capacity or autoscale the node pool
- Fix scheduling constraints and storage class design
- Reserve dedicated nodes for critical workloads if needed

## Scenario 4: CI Pipeline Succeeds But Production Is Broken

### Prompt

The pipeline passed, the image was deployed, but the application is broken in production. Staging looked fine.

### What A Strong Answer Should Cover

- Explain that pipeline success does not prove runtime health.
- Check artifact immutability, environment drift, config differences, and verification gaps.

### Commands And Checks You Can Name

- Compare image tag or digest between staging and production
- `kubectl rollout status deployment/<name>`
- `kubectl describe configmap <name>`
- `kubectl describe secret <name>`
- Check deployment logs, readiness probes, and smoke-test coverage

### Likely Root Causes

- Different runtime configuration or secret value
- Missing migration step
- Staging data shape is unlike production data
- Feature flag mismatch
- The pipeline deployed a different artifact than the one tested

### Strong Mitigation Ideas

- Roll back to the previous working revision
- Enforce build-once-deploy-everywhere
- Add post-deploy smoke tests and synthetic checks
- Treat config as versioned, reviewed code

## Scenario 5: Terraform Plan Wants To Recreate A Production Database

### Prompt

You run `terraform plan` and see that a production database will be destroyed and recreated. The change was supposed to be a small update.

### What A Strong Answer Should Cover

- Stop before `apply`.
- Explain `ForceNew` behavior, state drift, module changes, or bad imports.
- Show that you understand blast radius and safe change control.

### Commands You Can Name

- `terraform plan`
- `terraform show`
- `terraform state show <resource>`
- `git diff`
- Check provider docs for arguments that force replacement

### Likely Root Causes

- Changed an immutable attribute
- Manual drift in the cloud console
- Refactored module path or resource address incorrectly
- Imported state does not match configuration

### Strong Mitigation Ideas

- Protect critical resources with `lifecycle { prevent_destroy = true }`
- Split state so app changes cannot accidentally touch databases
- Review plans in CI before apply
- Back up state and data before risky changes

## Scenario 6: DNS Or Service-To-Service Connectivity Failure

### Prompt

One microservice cannot reach another inside Kubernetes. Users see intermittent timeouts, but the destination pods look healthy.

### What A Strong Answer Should Cover

- Distinguish DNS failure, Service or endpoint failure, and NetworkPolicy failure.
- Mention that app health is not the same as service reachability.

### Commands You Can Name

- `kubectl get svc,endpoints -n <namespace>`
- `kubectl exec -it <pod> -- nslookup <service-name>`
- `kubectl exec -it <pod> -- curl -v http://<service-name>:<port>`
- `kubectl get networkpolicy -A`
- `kubectl logs -n kube-system -l k8s-app=kube-dns`

### Likely Root Causes

- Service selector does not match pods
- No ready endpoints
- CoreDNS issue
- NetworkPolicy blocking east-west traffic
- Port mismatch between container, Service, and app

### Strong Mitigation Ideas

- Fix selectors and ports first
- Scale or restart CoreDNS only if DNS is the actual issue
- Add synthetic connectivity checks for critical services
- Document the dependency map between services

## Scenario 7: Monitoring Shows No Data Or Too Many Alerts

### Prompt

Grafana dashboards show "No Data" for one service, or the team is getting flooded with useless alerts.

### What A Strong Answer Should Cover

- Check target discovery before blaming dashboards.
- Explain the difference between scrape failures, exporter failures, label mismatch, and alert design problems.

### Commands And Checks You Can Name

- Prometheus `/targets` page
- `curl http://<pod-ip>:<port>/metrics`
- `kubectl logs` for Prometheus, exporter, or Alertmanager
- Review alert rules, labels, routes, and silences

### Likely Root Causes

- Bad service monitor or scrape config
- Metrics endpoint changed
- NetworkPolicy blocking scrape traffic
- High-cardinality labels making queries expensive and noisy
- Alerting on causes instead of user-facing symptoms

### Strong Mitigation Ideas

- Restore scrape reachability first
- Reduce noisy alerts and route them by severity
- Use SLO or symptom-based alerts for paging
- Standardize labels such as `service`, `env`, and `version`

## Short Answer Pattern For Final Rounds

If you get stuck, use this fallback structure:

> I would first confirm user impact and timing, then check recent deployments or config changes. Next I would inspect metrics, logs, and events to narrow the issue to the app, container, node, network, or dependency layer. If production is unhealthy, I would stabilize with rollback, traffic reduction, or feature degradation before driving to permanent root cause.

## What Makes A Candidate Sound Senior

- You say which commands you would run.
- You explain why each command matters.
- You separate immediate mitigation from deep investigation.
- You talk about blast radius, rollback, and prevention.
- You avoid guessing a root cause without evidence.

***

## Scenario 8: Azure DevOps Pipeline OIDC/Managed Identity Authentication Failure (Azure Specific)

### Prompt

A pipeline that has been deploying to an Azure Kubernetes Service (AKS) cluster for the last 6 months suddenly fails today at the `AzureCLI@2` deployment step. The error is "AADSTS7000215: Invalid client secret provided" or a failure to obtain an OIDC token. No code or pipeline definition changes have occurred in the last week.

### What A Strong Answer Should Cover

- Understanding of Service Principal / Managed Identity lifecycles in Azure.
- Troubleshooting ADO Service Connections (Workload Identity Federation vs. Secret).

### Commands And Checks You Can Name

- Go to ADO Project Settings -> Service Connections.
- `az ad sp credential list --id <app-id>`
- Check the Enterprise Application / App Registration sign-in logs in Entra ID.

### Likely Root Causes

- **Service Principal Secret Expiration:** The service connection was built using an App Registration (Service Principal) with a client secret that was set to expire in 6 months, and it just expired today.
- **OIDC Federation Issue:** If using Workload Identity Federation, perhaps the trust between the ADO Project/Repo and the Entra ID app was accidentally deleted or modified by an Entra ID admin.

### Strong Mitigation Ideas

- **Immediate Fix:** Generate a new client secret in Entra ID, update the Service Connection in ADO, and re-run the pipeline.
- **Long Term Fix (Best Practice):** Convert the Service Connection from using a static Client Secret to using Workload Identity Federation (OIDC). OIDC eliminates the need for managing expiring secrets entirely, as Azure DevOps and Entra ID negotiate short-lived tokens automatically.

## Scenario 9: Application Gateway 502 Bad Gateway to AKS (Azure Specific)

### Prompt

You have an AKS cluster behind an Azure Application Gateway (AGIC). Users are reporting intermittent `502 Bad Gateway` errors during peak hours. The Kubernetes pods themselves show no restarts and seem healthy.

### What A Strong Answer Should Cover

- The relationship between App Gateway health probes and Kubernetes readiness probes.
- Understanding SNAT port exhaustion or backend timeout limits.

### Commands And Checks You Can Name

- Check Application Gateway "Backend Health" in the Azure Portal.
- Look at Azure Monitor metrics for App Gateway: `Failed Requests`, `Backend Connect Time`, `Healthy Host Count`.
- `kubectl get events` and `kubectl describe ingress`

### Likely Root Causes

- **Health Probe Mismatch:** The App Gateway's custom health probe timeout is too short, or the backend pod is taking too long to respond to the probe during peak load. The App Gateway marks the pod (backend pool member) as unhealthy and drops the connection with a 502.
- **NSG Blocking Probes:** A Network Security Group on the AKS subnet is blocking the App Gateway's specific health probe IP range (`65.52.0.0/14` or `168.63.129.16`), causing intermittent probe failures.
- **SNAT Exhaustion:** If the pods are making massive amounts of outbound connections through a public load balancer instead of NAT Gateway, SNAT ports get exhausted.

### Strong Mitigation Ideas

- Align the Kubernetes Readiness Probe timeout/thresholds with the Application Gateway Health Probe settings to ensure they agree on what constitutes a "healthy" pod.
- Ensure NSGs allow traffic from the App Gateway Subnet to the AKS Subnet.
- Scale out the App Gateway minimum instances to handle the peak concurrent connection load.
# Staff Engineering & Platform Leadership (7 YOE+)

Being a Staff-level DevOps Engineer or SRE is no longer about being the best individual contributor in the room. It is about multiplying the output of **every engineer around you**.

***

## 1. Architecture Decision Records (ADRs)

An ADR is the primary written artifact of a senior engineer. When you make a large technical decision — choosing between Thanos and Azure Managed Prometheus, or between vcluster and namespace isolation — you document it.

### Why ADRs Matter
- Without ADRs, engineers 2 years from now will ask "Why did we do it this way?" and there will be no answer.
- ADRs create psychological safety — a junior engineer has confidence to make a decision and document it, rather than being paralyzed by uncertainty.

### ADR Template

```markdown
# ADR-0042: Migrate from Istio Sidecars to Istio Ambient Mesh

**Date:** 2026-03-15  
**Status:** Accepted  
**Deciders:** Platform Team, Head of Infrastructure

## Context
Our current 3,000-pod cluster runs Istio in sidecar mode. Envoy sidecars 
consume 300MB RAM per pod = 900GB total reserved overhead just for proxies.
Pod startup times have increased 40% due to sidecar injection.

## Decision
Migrate to Istio Ambient Mesh, which eliminates per-pod sidecars in favor 
of a per-node ztunnel DaemonSet for L4 security and a per-namespace Waypoint 
Proxy for L7 policy.

## Consequences
**Positive:**
- Estimated 70% reduction in proxy RAM overhead (~$85k annualized savings).
- No more injection webhooks slowing pod startup.

**Negative:**
- Istio Ambient is GA only as of 1.22. Requires cluster upgrade.
- Team training required on the new ztunnel debugging workflow.

## Alternatives Considered
- Cilium Service Mesh: More performant at L4, but less mature L7 policy 
  authoring compared to Istio.
- Status quo: Not viable — the RAM overhead is blocking cluster autoscaler efficiency.
```

***

## 2. DORA & SPACE Metrics: Measuring Engineering Velocity

Senior engineers do not manage people; they manage systems. DORA metrics let you measure the health of your software delivery system.

### DORA (DevOps Research and Assessment) — 4 Key Metrics

| Metric | Elite Performance | How to Measure |
|---|---|---|
| **Deployment Frequency** | Multiple times/day | Count deploys per service per day |
| **Lead Time for Changes** | < 1 hour | Time from code commit → production |
| **Change Failure Rate** | < 5% | % of deploys causing incidents |
| **Time to Restore Service** | < 1 hour | MTTR from alert firing to resolution |

### SPACE (Developer Satisfaction, well-being, and velocity)
DORA measures the system. SPACE measures the humans.
- **S**atisfaction — Developer NPS and survey scores.
- **P**erformance — Quality of output (bugs escaped, reliability).
- **A**ctivity — Volume of PRs, deployments, code reviews (leading indicator, not a goal).
- **C**ommunication — Documentation quality, async reviews completed on time.
- **E**fficiency — Time wasted on toil, CI wait times, flaky test rates.

### The Staff Engineer Narrative
"I presented DORA metrics to our VP of Engineering every quarter. When our Lead Time for Changes climbed from 45 minutes to 4 hours, I used the trend to justify a $30k investment in a faster ephemeral testing environment. Lead times returned to 50 minutes within 6 weeks."

***

## 3. Chaos Engineering & GameDays

Chaos Engineering is the practice of intentionally introducing failures into a system to discover weaknesses before customers do.

### The Steady-State Hypothesis
Before injecting any failure, define and measure your steady state:
- Error rate < 0.1%
- P99 latency < 300ms
- All Kubernetes pods are Running with no restarts

### Running a GameDay (Step-by-Step)
1. **Announce and scope** — Inform all stakeholders. Define the blast radius (e.g., "this GameDay only affects our staging cluster").
2. **Choose a hypothesis** — "If a single AZ goes offline, our auto-failover will activate within 5 minutes and error rate will stay below 0.5%."
3. **Inject the failure** — Use tools like Chaos Monkey, Chaos Mesh, or AWS Fault Injection Simulator (FIS) to inject the AZ blackhole.
4. **Observe** — Monitor dashboards. Is the steady state maintained?
5. **Abort condition** — Define a hard stop: if error rate exceeds 5%, stop the experiment immediately.
6. **Document findings** — Track all surprises in a "Chaos Journal". Each surprise is a gap worth fixing.

### Common Chaos Experiments
| Experiment | What It Tests |
|---|---|
| Kill random pods | Pod disruption budget + cluster self-healing |
| Fill a node's disk to 95% | Disk pressure eviction policies |
| Block DNS from within a pod | DNS fallback and timeout handling |
| Inject 500ms network latency | Downstream timeout configuration |
| Kill the database primary | Auto-failover correctness |

***

## 4. Developer Experience (DevEx): From Gatekeeper to Enabler

The most common failure mode of platform teams is becoming a bottleneck. The platform team must think of *developers as their customers*.

### The Golden Path Principle
A Golden Path is an opinionated, fully supported path for how to build and deploy software at your organization. It is:
- **Not mandatory** — developers can deviate, but deviation means losing platform support.
- **Not a prison** — the path evolves based on developer feedback.
- **Documented and automated** — one command or one click to get a new service running with CI, observability, and IaC already wired in.

### Measuring DevEx: Platform NPS
Run quarterly surveys asking developers:
1. "How satisfied are you with the deployment pipeline?" (1-10)
2. "What is your biggest time-waster this quarter?"
3. "What would make you 2x more productive?"

Track the trend. If Platform NPS is dropping, the platform is becoming a blocker.

### The Internal Product Manager Mindset
The platform team must:
- Maintain a **public backlog** — any developer can see what features are planned.
- Run a **monthly demo** — showcase new platform capabilities.
- Issue **deprecation notices with runways** — never remove a capability without 60+ days of warning.

***

## 5. Value Stream Mapping

Value Stream Mapping (VSM) is the process of visually mapping every step from a developer committing code to that code running in production, including wait times.

### A Typical VSM for a 3-Week Lead Time

```
Developer commits → 15 min → CI passes
CI passes → 3 days waiting → Security scan approved
Security scan → 1 day waiting → Change Advisory Board (CAB) review
CAB approved → 1 week waiting → Next release window
Release window → 2 days → Manual testing
Manual testing → 2 days operating → Deployment
```

The 3-week lead time contains less than 1 hour of *actual work*. The rest is **waste (wait time)**.

### The Senior Engineer's Job
Identify and eliminate the largest wait time steps. In this example:
1. Replace manual security CAB with automated Policy-as-Code (Checkov/OPA).
2. Replace quarterly release windows with continuous delivery.
3. Replace manual testing with automated integration test suites.

Result: 3-week → 45-minute lead time.

***

## 6. The Stakeholder Communication Model

Technical work that is not communicated to leadership does not advance your career or your team's headcount.

### The "So What?" Framework for Executive Communication
When presenting any technical outcome, apply the "So What?" test three times:

> "We migrated to Cilium."
> *So what?*
> "iptables latency dropped by 30% under load."
> *So what?*
> "P99 latency dropped from 420ms to 290ms for our checkout service."
> *So what?*
> "Checkout completion rate improved by 1.2%, generating an estimated $180k/year in recovered revenue."

That last sentence is what goes in the slide deck for the VP.

### The Engineering Proposal (for Headcount or Budget)
Structure:
1. **Current state** — quantify the pain (hours of toil, number of incidents).
2. **Proposed solution** — specific tools, timeline, team size.
3. **Expected outcome** — in business terms (reliability, cost, developer velocity).
4. **Risk of doing nothing** — what gets worse if you don't act.
