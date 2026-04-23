# Staff Engineering & Platform Leadership (7 YOE+)

Being a Staff-level DevOps Engineer or SRE is no longer about being the best individual contributor in the room. It is about multiplying the output of **every engineer around you**.

---

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

---

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

---

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

---

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

---

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

---

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
