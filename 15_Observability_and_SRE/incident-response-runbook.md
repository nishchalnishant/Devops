# Incident Response Runbook (7 YOE)

A senior DevOps or SRE engineer is expected to **lead** an incident, not just debug it. This means structured communication, fast mitigation, and systematic review — even under pressure.

---

## The Incident Lifecycle

```
Detect → Triage → Declare → Mitigate → Resolve → Review
```

---

## Phase 1: Detect

An incident starts when an alert fires, a customer reports it, or a team member notices anomalous behaviour. The first goal is **not** to find the root cause — it is to determine **scope and user impact**.

### Initial Triage Questions (answer in < 5 minutes)

1. **What is broken?** (which service/area)
2. **Who is affected?** (all users, specific region, specific tenant?)
3. **How severe?** (complete outage, degraded performance, data integrity risk?)
4. **When did it start?** (correlates with deployments, changes, traffic spikes)
5. **Is it still happening?** (could be a transient blip)

### Signal Sources

| Signal | Azure | Generic |
|---|---|---|
| Latency/Error spike | Application Insights → Failures blade | Grafana → Error Rate panel |
| Infra anomaly | Azure Monitor → Metrics Explorer | Prometheus → `kube_node_status_condition` |
| Log errors | Log Analytics → KQL | Kibana / Loki |
| Synthetic health | Azure Monitor availability tests | Blackbox Exporter |

---

## Phase 2: Declare

If the incident exceeds a severity threshold (see below), **declare it**. Do not wait until you know the root cause. Declaration gates proper communication and ensures the right people are engaged.

### Severity Levels

| Severity | Definition | Response SLA |
|---|---|---|
| **P0 — Critical** | Complete service outage. Revenue or data integrity impacted. | Immediate — wake up on-call + incident commander |
| **P1 — High** | Major feature broken. Significant user impact. | 15 minutes |
| **P2 — Medium** | Partial degradation. Workarounds exist. | 1 hour |
| **P3 — Low** | Minor issue. Small % of users. | Next business day |

### Declare in the Incident Channel (template)

```
🚨 INCIDENT DECLARED — P[X]
Time: 2026-04-21 14:32 UTC
Summary: [checkout-service] returning 503 errors for 40% of users in eu-west-1
Impact: Customers cannot complete orders. Revenue impact ~$X/min.
Incident Commander: @alice
Lead Engineer: @bob
Status Page: [link] — Updated to "Investigating"
Zoom Bridge: [link]
```

---

## Phase 3: Triage and Mitigate

The goal of mitigation is to **reduce user impact as fast as possible**, even if you don't know the root cause yet. Stabilize first. Investigate second.

### Mitigation Strategies (in order of speed)

1. **Feature flag / toggle off** the broken feature (fastest — zero risk).
2. **Rollback** the most recent deployment: `kubectl rollout undo deployment/<name>`.
3. **Traffic shift** — route away from the broken region or pod set.
4. **Scale up** replicas if the issue is load-related.
5. **Restart affected pods** as a last resort (this does not fix root cause but may buy time).
6. **Manual failover** to secondary region or backup database replica.

### Communication Every 15–30 Minutes

Even if you have no new findings, send a status update:

```
UPDATE 14:47 UTC
Progress: Identified the issue is in the auth-service, not checkout.
Action: Rolling back auth-service to v2.3.1. ETA: 5 minutes.
Current impact: Same as initial report.
Next update: 15:00 UTC
```

---

## Phase 4: Resolve

The incident is resolved when:
- User-facing metrics (error rate, latency) return to normal SLO levels.
- A root cause hypothesis has been confirmed (even if a permanent fix is not yet deployed).
- The on-call rotation is stood down.

### Resolve Template

```
✅ INCIDENT RESOLVED — P[X]
Time: 2026-04-21 15:02 UTC
Duration: 30 minutes
Root Cause (preliminary): auth-service v2.4.0 introduced a misconfigured JWT signing key path, causing all token validation to fail.
Mitigation: Rolled back to auth-service v2.3.1.
Status Page: Updated to "Resolved"
Post-Mortem: Scheduled for 2026-04-22 10:00 UTC
```

---

## Phase 5: Post-Mortem (Blameless)

A blameless post-mortem looks for **systemic failures**, not individual mistakes. The output is a set of concrete action items that prevent the same class of failure recurring.

### Post-Mortem Document Structure

```markdown
# Post-Mortem: [Incident Title]

**Date:** 2026-04-21  
**Duration:** 30 minutes  
**Severity:** P1  
**Authors:** @alice, @bob  
**Status:** Action Items In Progress

## Summary
One sentence: what broke, why it broke, and what the impact was.

## Timeline

| Time (UTC) | Event |
|---|---|
| 14:30 | First error alert fired: auth-service 503 rate > 10% |
| 14:32 | On-call engineer acknowledged |
| 14:38 | Root cause narrowed to auth-service after log correlation |
| 14:50 | Rollback to v2.3.1 initiated |
| 15:02 | Error rate returned to < 0.1% |

## Root Cause Analysis (5 Whys)

- **Why** did users get 503 errors? → auth-service was rejecting all JWT tokens.
- **Why** was it rejecting all tokens? → The signing key path was wrong in the config.
- **Why** was the config wrong? → A new environment variable name was introduced in v2.4.0 but the deployment ConfigMap was not updated.
- **Why** was the ConfigMap not updated? → The deploy step ran before the ConfigMap update step in the pipeline (ordering bug).
- **Why** wasn't this caught in staging? → Staging ConfigMaps are managed separately and were already updated manually.

## What Went Well
- Alert fired within 2 minutes of degradation start.
- Rollback procedure was documented and ran cleanly in under 10 minutes.
- Communication was regular and clear throughout.

## What Went Poorly
- Staging and production ConfigMaps diverged without detection.
- Initial triage looked at the wrong service (checkout) for 6 minutes.

## Action Items (SMART format)

| Action | Owner | Due Date | Priority |
|---|---|---|---|
| Add pipeline step that validates ConfigMap key names match the app environment definition | @bob | 2026-04-28 | P0 |
| Create automated diff check between staging and production ConfigMaps on every deploy | @alice | 2026-05-02 | P1 |
| Add a synthetic canary test that validates a full auth token round-trip post-deploy | @charlie | 2026-05-05 | P1 |
```

---

## SLO Burn Rate Alerting

A **burn rate** measures how fast you are consuming your error budget relative to the rate that would exhaust it exactly by the end of the SLO window.

Burn rate of **1** = consuming budget at exactly the sustainable rate (you exhaust it at month-end).
Burn rate of **14** = consuming budget 14× faster (you exhaust a 30-day budget in ~2 days).

### Multi-Window, Multi-Burn-Rate Alerting (Google SRE Workbook approach)

| Alert | Short Window | Long Window | Burn Rate | Priority | Action |
|---|---|---|---|---|---|
| Fast burn (critical) | 5m | 1h | 14× | Page immediately | Immediate investigation |
| Slow burn (warning) | 30m | 6h | 3× | Slack notification | Investigate this sprint |

### PromQL for 14× Burn Rate (1h window)

```promql
# Example: 30-day SLO = 99.9% → error budget = 0.1%
# 14x burn rate over 1h window:
(
  sum(rate(http_requests_total{status=~"5.."}[1h]))
  /
  sum(rate(http_requests_total[1h]))
) > (14 * 0.001)
```

### Azure Monitor equivalent (KQL)

```kusto
let slo_threshold = 0.001; // 99.9% SLO error budget
let burn_rate = 14.0;
requests
| where timestamp > ago(1h)
| summarize
    total = count(),
    failed = countif(success == false)
  by bin(timestamp, 5m)
| extend error_rate = toreal(failed) / toreal(total)
| where error_rate > (burn_rate * slo_threshold)
```

---

## Communication Best Practices

### Say this — not that

| ❌ Don't Say | ✅ Do Say |
|---|---|
| "I think the database is down." | "Metrics show db query latency exceeding 5s. I'm confirming if it's the primary or replica." |
| "Restarting everything." | "I'm restarting the auth-service pods as a mitigation while I continue investigating the config issue." |
| "Bob shouldn't have done that." | "The system allowed the config to be deployed without validation. We'll add a check." |
| "I don't know what's happening." | "I've ruled out the database and network. I'm now investigating the application layer." |

---

## On-Call Rotation and Escalation Policy

### Healthy On-Call Design

1. **Rotation:** Each engineer is on-call for at most 1 week, with at least 5 weeks off between stints.
2. **Shadowing:** Junior engineers shadow before taking solo on-call.
3. **Runbook coverage:** Every alert must have a linked runbook. If no runbook exists, the alert should not be paging.
4. **Escalation chain:** Every primary on-call has a named secondary who auto-escalates after **10 minutes** of no acknowledgement.

### Alert Quality Standards

An alert is worth paging an engineer at 3 AM **only if** it meets all three criteria:

1. **Urgent** — delayed response will make it worse.
2. **Actionable** — the on-call engineer can do something specific right now.
3. **Customer-impacting** — there is measurable user harm, not just an internal metric anomaly.

If an alert does not meet all three, it belongs in a Slack channel or a Jira ticket, not a phone call.
