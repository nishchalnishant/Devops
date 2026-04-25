# Incident Management & On-Call Excellence

A structured approach to incident response is one of the highest-leverage investments an engineering organization can make. This note covers the complete incident lifecycle — detection, declaration, response, communication, and postmortem.

***

## 1. Incident Severity Levels

Define severity levels consistently so everyone knows what response is expected:

| Severity | Impact | Response Time | Who Is Notified |
|:---|:---|:---|:---|
| **Sev-1 (Critical)** | Revenue impact; all users affected; SLA breach imminent | Immediate (< 5 min) | On-call + manager + VP |
| **Sev-2 (High)** | Significant degradation; > 20% users affected | < 15 minutes | On-call + team lead |
| **Sev-3 (Medium)** | Partial degradation; workaround exists; < 20% users | < 1 hour | On-call |
| **Sev-4 (Low)** | Minor issue; no user impact; cosmetic | Next business day | Ticket only |

**Key rule:** When in doubt, escalate severity. It is far better to over-page and downgrade than to under-page and miss a Sev-1.

***

## 2. Incident Response Roles

Assign roles within the first 5 minutes to prevent chaos:

| Role | Responsibility |
|:---|:---|
| **Incident Commander (IC)** | Coordinates the response, makes decisions, owns communication cadence |
| **Technical Lead** | Drives diagnosis and remediation; focuses on the problem |
| **Scribe** | Documents all actions, timeline, and findings in real time |
| **Communications Lead** | Updates status page, stakeholders, and executives |
| **SME (Subject Matter Expert)** | Called in to provide domain expertise on demand |

**The IC does NOT fix the problem.** The IC coordinates people, ensures information flows, makes escalation decisions, and keeps the response organized. The Technical Lead focuses entirely on diagnosis.

***

## 3. The 5-Phase Response Framework

### Phase 1: Detect (< 5 min)
```
Alert fires → On-call acknowledges in PagerDuty
  → Confirm: is this a real issue or a false alarm?
  → Real: open incident Slack channel #inc-YYYY-MM-DD-service-name
  → Real: declare severity based on initial impact assessment
  → Real: announce IC and Technical Lead in channel
```

### Phase 2: Investigate (minutes → hour)
```
Triage checklist (in this order):
  1. What's the blast radius? (how many users/services affected?)
  2. Is it getting worse, stable, or improving?
  3. What changed recently? (deploy, config, cron, external dependency)
  4. What does the data say? (metrics, logs, traces — in that order)
  5. Can we mitigate before we diagnose? (rollback, feature flag, traffic shift)
```

```bash
# Standard diagnostic commands during investigation
kubectl get pods -n production -w          # Watch pod state changes
kubectl describe pod <failing-pod>         # Events and resource info
kubectl logs <pod> --previous --tail=100   # Logs from crashed container
kubectl top pod -n production             # Resource usage
kubectl get events --sort-by='.lastTimestamp' -n production

# For AWS issues
aws cloudtrail lookup-events --lookup-attributes AttributeKey=ResourceName,AttributeValue=my-service
```

### Phase 3: Mitigate (priority over diagnosis)
```
Mitigation goal: restore service as fast as possible, even if you don't understand why

Common mitigations (in order of risk):
  LOW risk:    rollback recent deployment
               toggle a feature flag off
               increase pod replicas (if resource-constrained)
  MEDIUM risk: restart a stuck pod or service
               shift traffic away from a failing region/AZ
  HIGH risk:   scale down a dependency (may cause other issues)
               restore from backup
```

### Phase 4: Resolve
```
Service is restored → maintain at least 15 minutes of monitoring to confirm stable
  → Declare incident resolved in PagerDuty
  → Update status page: "Resolved — we are monitoring"
  → Send final stakeholder communication:
    "As of HH:MM UTC, service has been fully restored.
    X% of users were affected for Y minutes.
    We will publish a full postmortem within 5 business days."
```

### Phase 5: Postmortem
See Section 7 below.

***

## 4. Communication Templates

### Status Page Updates (every 10-15 minutes during Sev-1)

```
[INVESTIGATING] We are investigating reports of [service] degradation.
Impact: [X% of requests failing / all users in region X affected]
We will update every 15 minutes.
— 14:32 UTC

[UPDATE] We have identified the cause and are implementing a fix.
Impact: [current state]
ETA: [estimated resolution or "unknown — we'll update at 15:00 UTC"]
— 14:47 UTC

[RESOLVED] Service has been fully restored.
Duration: 23 minutes (14:09 - 14:32 UTC)
We will publish a full postmortem within 5 business days.
— 14:55 UTC
```

### Executive Update (Sev-1, every 20 minutes)
```
[INCIDENT UPDATE - 14:45 UTC]
Service: Payment API
Status: DEGRADED — team actively working on resolution
Impact: ~15% of checkout requests failing; $X revenue at risk per minute
Root cause: Identified as Redis connection pool exhaustion (investigating cause)
Mitigation: Scaling up Redis replicas — 50% recovery expected in 10 minutes
Next update: 15:05 UTC or when resolved
Incident Commander: [name]
```

***

## 5. Runbook Design

A runbook is a documented procedure for responding to a specific alert. A good runbook answers:

```markdown
# Alert: HighPaymentAPIErrorRate

## Summary
Payment API error rate exceeds 1% for 5 minutes.

## Impact
Users cannot complete checkout. Each minute of downtime = ~$12k revenue loss.

## Triage (< 2 minutes)
1. Check: Is this a spike or sustained?
   → LogQL: `{app="payment-api"} | json | level="error" | rate([2m])`
   → Grafana: [link to dashboard]

2. Check: What changed recently?
   → `kubectl rollout history deployment/payment-api -n production`
   → Recent deployments: [link to CI/CD]

## Common Causes & Fixes

### Cause 1: Recent bad deployment
Signal: Error rate started when deployment N-1 completed
Fix: `helm rollback payment-api -n production --wait`

### Cause 2: Database connection pool exhaustion  
Signal: Logs show "could not obtain connection from pool"
Fix:
  1. `kubectl scale deployment/payment-api --replicas=2 -n production` (reduce app instances)
  2. OR: `kubectl exec -it <pgbouncer-pod> -- psql -c "RELOAD"` (reload pgbouncer config)

### Cause 3: Downstream dependency (fraud-service) is down
Signal: Logs show timeout errors calling fraud-service
Fix: Check fraud-service health: `kubectl get pods -n fraud-detection`
     If unhealthy: notify fraud-detection on-call via PagerDuty
     Temporary: enable `SKIP_FRAUD_CHECK=true` feature flag in LaunchDarkly

## Escalation
If not resolved in 20 minutes: page [team lead name] via PagerDuty

## Postmortem Trigger
Any Sev-1 or any incident lasting > 30 minutes.
```

***

## 6. On-Call Health & Sustainability

### The On-Call Alerting Targets
```
GOOD on-call week:
  - < 5 actionable alerts per shift
  - MTTD (detection to acknowledge): < 5 minutes
  - No alert fires outside business hours that isn't Sev-1 or Sev-2
  - Every alert has a runbook

BAD on-call week (alert fatigue):
  - > 25 alerts per shift
  - > 30% of alerts are "informational" or require no action
  - Same alert fires 3+ times with no permanent fix between occurrences
```

### Reducing Alert Fatigue
1. **Delete noisy alerts** — if a team ignores an alert 3 times in a row, delete it
2. **Tune thresholds** — alerts that fire at 3am for things that fix themselves are the worst
3. **Blameless postmortems for on-call escalations** — if an alert wakes someone up for a non-issue, spend 30 minutes improving the alert
4. **Alert on symptoms, not causes** — CPU 90% is a cause; P99 latency 500ms is a symptom

***

## 7. Blameless Postmortem Template

```markdown
# Incident Postmortem — [Service]: [Brief Description]

**Date:** [YYYY-MM-DD]  
**Severity:** [Sev-1/2/3]  
**Duration:** [HH:MM] (detected [time UTC] → resolved [time UTC])  
**Impact:** [% of users affected], [user-facing description of what failed]  
**Authors:** [names]

---

## Timeline (UTC)

| Time | Event |
|:---|:---|
| 14:09 | First alert fires: PaymentAPIErrorRate |
| 14:12 | On-call acknowledges; incident channel opened |
| 14:18 | Root cause identified: Redis connection exhaustion |
| 14:22 | Mitigation applied: Redis scaled from 1 to 3 replicas |
| 14:32 | Error rate returns to baseline |
| 14:47 | Incident declared resolved |

---

## Root Cause Analysis

[Describe what actually caused the incident, in clear, non-blaming language]

**5 Whys:**
1. Why did the payment API return errors? → Redis connection pool was exhausted
2. Why was the pool exhausted? → Spike of 3x normal traffic during flash sale
3. Why was the pool sized for normal traffic? → Capacity planning didn't account for flash sales
4. Why wasn't this tested? → Load tests don't simulate flash sale traffic patterns
5. Why don't load tests simulate flash sales? → No documented process for pre-event capacity review

---

## What Went Well
- Alert fired within 3 minutes of issue start (MTTD = 3 min)
- On-call ran the runbook correctly; no guesswork
- Status page updated within 10 minutes

## What Went Poorly
- MTTR was 23 minutes — Redis scaling should be a 2-minute automated action
- No flash sale capacity review happened despite event being scheduled in the calendar

---

## Action Items

| Action | Owner | Due Date | Priority |
|:---|:---|:---|:---|
| Add Redis auto-scaling rule triggered by connection pool > 80% | Platform team | 2 weeks | P1 |
| Create "pre-event capacity review" runbook | SRE lead | 1 week | P1 |
| Add flash-sale traffic pattern to load test suite | Performance team | 4 weeks | P2 |
| Update Redis pool size default from 20 to 50 | Payments team | 3 days | P1 |
```

***

## 8. MTTD and MTTR Reduction Strategies

### Reducing MTTD (Mean Time To Detect)
- **Multi-window SLO alerting** — detect budget burn rate before it becomes critical
- **Synthetic monitoring** — probe endpoints externally; detects issues before internal metrics do
- **Log-based alerting** — Loki alerting on ERROR rate spike = faster detection than metric scrape lag
- **Shorter Prometheus scrape intervals** (15s → 10s) for critical services

### Reducing MTTR (Mean Time To Recover)
- **Automated rollback** — Flagger automatically rolls back on SLO breach during canary
- **Feature flag killswitches** — disable a feature in 30 seconds without a deployment
- **Runbook automation** — common mitigations executable via a Slack bot (`/fix redis-scale-up`)
- **Blast radius reduction** — if only one AZ is affected, immediately route traffic to other AZs
- **Pre-approved change list** — mitigations that don't require change management approval during incidents
