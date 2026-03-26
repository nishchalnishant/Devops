# Phase 3 - SRE And Operations

This phase shifts from "how to deploy" to "how to run production systems safely."

## Goal

By the end of this phase, you should be able to detect issues early, troubleshoot methodically, stabilize production systems, and explain the reasoning behind your actions.

## Study Order

1. `../roadmap/9.-monitoring.md`
2. `../devops/devops-interview-playbook.md`
3. `../interview-questions.md`
4. `../devops/interview-questions-medium.md`
5. `../devops/interview-questions-hard.md`
6. `../cloud/azure-medium-questions.md`
7. `../cloud/azure-hard-questions.md`

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
