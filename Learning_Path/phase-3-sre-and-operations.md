# Phase 3 - SRE And Operations

```
Phase 3 - SRE And Operations
├── Observability
│   ├── Three pillars: metrics (time series), logs (events), traces (request path)
│   ├── Prometheus: pull model, scrape configs, exporters, /metrics endpoints
│   ├── Grafana: dashboards, panels, alert rules, data sources
│   ├── SLI: what you measure (latency, error rate, availability)
│   ├── SLO: the target threshold over a time window
│   ├── Error budget: allowed unreliability — gates feature work vs reliability work
│   ├── Four Golden Signals: latency, traffic, errors, saturation
│   └── Risks: high-cardinality labels, alert fatigue, noisy scrapes
├── Troubleshooting
│   ├── Start with metrics: scope the blast radius and timing
│   ├── Use events, logs, rollout history before guessing cause
│   ├── Kubernetes failures: CrashLoopBackOff, Pending, ImagePullBackOff, OOMKilled
│   ├── Terraform failures: state lock, ForceNew, drift, import mismatch
│   ├── Host failures: CPU, memory, disk, swap, socket exhaustion
│   └── Distinguish app issues from infrastructure issues with evidence
├── Reliability
│   ├── Rollback strategy: revision rollback vs traffic shift vs hotfix
│   ├── Canary: small % of traffic, observe SLOs, promote or abort
│   ├── Blue-green: full environment swap, instant rollback possible
│   ├── Rolling: incremental pod replacement, always-on availability
│   ├── Graceful degradation: shedding non-critical functionality under load
│   └── Load shedding: rate limiting, queue depth limits, circuit breakers
├── Security And Operational Hygiene
│   ├── Secrets handling: Vault, Secrets Manager, never in code or logs
│   ├── Least privilege: RBAC for people, service accounts, and pipelines
│   ├── Image scanning: CVE detection before promotion
│   ├── Dependency scanning: SCA tools in CI
│   ├── Policy as code: OPA Gatekeeper, Kyverno, admission controllers
│   └── Runtime controls: Falco for syscall-level anomaly detection
├── Cost And Capacity
│   ├── Overprovisioning vs reliability margin: balancing safety and spend
│   ├── HPA: scale on CPU/memory, custom metrics, external metrics
│   ├── VPA: right-size resource requests based on actual usage
│   ├── Rightsizing: match requests/limits to actual resource consumption
│   └── Idle resources: unattached disks, stopped VMs, zombie load balancers
├── Hands-On Tasks
│   ├── Build Grafana dashboard + define one actionable alert
│   ├── Simulate failing deployment and practice rollback
│   ├── Debug CrashLoopBackOff or Pending pod in a lab
│   ├── Write short runbook for a high-latency service
│   └── Write short RCA for a deployment or config incident
└── Exit Criteria
    ├── Explain SLO-based thinking clearly
    ├── Investigate production-style issue in structured way
    ├── Name commands for Kubernetes and host troubleshooting
    ├── Describe safe rollback strategy
    └── Talk about monitoring, security, and cost as one operating model
```

## First Principles

- **Why observability before troubleshooting?** You cannot debug what you cannot see. The instinct to immediately run commands is slower and riskier than first understanding scope, timing, and recent change history from dashboards.
- **Why error budgets change behavior?** Error budgets turn reliability into a resource that is spent or conserved. Without that framing, reliability work competes with feature work on sentiment rather than data. Error budgets make the trade-off legible.
- **Why distinguish mitigation from root cause?** In a live incident, making users whole is more important than being right about cause. The fastest safe mitigation (usually rollback) should happen before the investigation, not after.
- **Why policy as code?** Manual security reviews at deploy time are too slow, inconsistent, and missable. Machine-enforced policies applied to every admission request catch violations before they reach production.
- **Why include cost in an operations phase?** Capacity decisions and reliability decisions are the same decision. An undersized cluster fails under load. An oversized cluster wastes money. Operating a service means balancing both simultaneously.

This phase shifts from "how to deploy" to "how to run production systems safely."

## Goal

By the end of this phase, you should be able to detect issues early, troubleshoot methodically, stabilize production systems, and explain the reasoning behind your actions.

## Study Order

1. `../15_Observability_and_SRE/README.md`
2. `../07_Interview_Preparation/devops-interview-playbook.md`
3. `../07_Interview_Preparation/general-interview-questions.md`
4. `../07_Interview_Preparation/interview-questions-medium.md`
5. `../07_Interview_Preparation/interview-questions-hard.md`
6. `../12_Azure/interview.md`
7. `../12_Azure/interview.md`

## What To Master

### Observability

- metrics, logs, and traces
- Prometheus, Grafana, and alerting
- SLI, SLO, SLA, and error budgets
- high-cardinality risks and noisy alerts

### Troubleshooting

- using metrics before guessing
- events, logs, rollout history, and node inspection
- common Kubernetes and Terraform failure states
- how to distinguish app issues from infrastructure issues

### Reliability

- rollback strategy
- canary, blue-green, and rolling trade-offs
- graceful degradation and load shedding
- incident mitigation versus long-term prevention

### Security And Operational Hygiene

- secrets handling
- least privilege
- image and dependency scanning
- policy as code and runtime controls

### Cost And Capacity

- overprovisioning versus reliability margin
- autoscaling logic
- rightsizing
- cloud waste and idle resources

## Hands-On Tasks

1. Build a Grafana dashboard and define one actionable alert.
2. Simulate a failing deployment and practice rollback.
3. Debug a `CrashLoopBackOff` or `Pending` pod in a lab.
4. Write a short runbook for a high-latency service.
5. Write a short RCA for a deployment or config incident.

## Checkpoint Questions

- How do logs, metrics, and traces work together during an outage?
- Why is symptom-based alerting better than paging on every CPU spike?
- What do you check first in `CrashLoopBackOff`?
- If HPA scales pods but latency stays high, what does that imply?
- What is the difference between immediate mitigation and permanent fix?

## Exit Criteria

Move to Phase 4 only when you can:

- explain SLO-based thinking clearly
- investigate a production-style issue in a structured way
- name the commands you would use for Kubernetes and host troubleshooting
- describe a safe rollback strategy
- talk about monitoring, security, and cost as one operating model rather than separate topics

***

## Related Resources

- [Monitoring and Observability](../15_Observability_and_SRE/README.md)
- [Kubernetes Runbook](../05_Kubernetes/troubleshooting.md)
- [Incident Response Runbook](../15_Observability_and_SRE/notes/troubleshooting_guide.md)
- [DevOps Interview Playbook](../07_Interview_Preparation/devops-interview-playbook.md)
- [Hard Interview Questions](../07_Interview_Preparation/interview-questions-hard.md)
- [Azure Troubleshooting](../12_Azure/scenarios.md) (Azure-specific)

***

**Previous:** [Phase 2 - Platform and Delivery](phase-2-platform-and-delivery.md) | **Next:** [Phase 4 - Senior Role Readiness](phase-4-senior-role-readiness.md)
