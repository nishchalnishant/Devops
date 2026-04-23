# DevOps Interview Playbook

Use this file as the main answer framework for DevOps, SRE, platform, and cloud-operations interviews.

## What Interviewers Are Really Testing

### 1. Fundamentals

You should be able to explain how Linux, networking, cloud, CI/CD, containers, and observability fit together. Interviewers usually care less about memorizing a command and more about whether you know when and why to use it.

### 2. Systems Thinking

A strong DevOps engineer thinks in dependencies and blast radius:

- What changed recently?
- Which component is actually failing?
- Which downstream system is causing the symptom?
- What is the fastest safe mitigation?

### 3. Troubleshooting Depth

Good candidates do not jump to a favorite root cause. They narrow the problem with evidence:

- Metrics to understand impact and timing
- Logs and events to find failing components
- Commands to validate a hypothesis
- A rollback or mitigation if the system is still unhealthy

### 4. Automation Mindset

Interviewers look for engineers who reduce manual work. Repeated tasks should turn into scripts, pipelines, modules, templates, dashboards, or runbooks.

### 5. Communication

A senior answer is structured. It explains:

1. What I would check first
2. Why I am checking it
3. What outcome I expect
4. How I would mitigate the issue
5. What I would change long term

## A Strong Answer Framework

Use this structure for most technical questions and incident scenarios:

1. Clarify the symptom and impact.
2. Check whether there was a recent deployment or configuration change.
3. Start with user-facing signals: latency, errors, availability, saturation.
4. Narrow the failing layer: app, container, node, network, database, cloud service, or pipeline.
5. Run the smallest commands that can confirm or reject a hypothesis.
6. Stabilize first, then optimize, then document the long-term fix.

Example:

> I would first confirm scope and timing in Grafana, then check recent deployment history, then inspect pod events and logs. If the service is actively failing, I would prepare a rollback while I validate whether the issue is config, image, dependency, or resource pressure.

## What You Should Know By Topic

### Git And Collaboration

- Branching, pull requests, merge vs rebase, revert vs reset
- How to recover from a bad merge or bad release
- Protected branches, code review, signed commits, secret scanning

### Linux And Shell

- Processes, signals, file permissions, systemd, logs, disk and memory inspection
- Safe shell scripting with `set -euo pipefail`, exit codes, functions, logging, and cron or timers
- How to debug a host that is slow, full, swapping, or refusing connections

### Networking

- TCP vs UDP, DNS, CIDR, routing, NAT, TLS, load balancing
- Connection refused vs timeout
- Basic packet and socket inspection with `ss`, `curl`, `dig`, `tcpdump`, `traceroute`, or `mtr`

### Cloud

- Compute, storage, networking, IAM/RBAC, autoscaling, HA, backups, DR
- Public vs private subnets
- Managed service trade-offs versus self-hosted platforms

### CI/CD

- Build, test, scan, package, publish, deploy, verify, rollback
- Artifact immutability and promotion
- Secrets handling, approval gates, canary or blue-green, smoke tests

### Docker And Kubernetes

- Dockerfile best practices, image layers, registries, networking, volumes
- Pods, Deployments, StatefulSets, Services, Ingress, probes, HPA
- Common failures: CrashLoopBackOff, ImagePullBackOff, Pending, OOMKilled, DNS issues

### Terraform And Ansible

- Providers, modules, state, backends, locking, outputs, drift, `for_each`
- Why Terraform provisions and Ansible configures
- Safe rollout patterns for infrastructure changes

### Observability And SRE

- Metrics, logs, traces
- Four Golden Signals
- SLI, SLO, error budget, alert fatigue
- How to turn symptoms into dashboards and actionable alerts

### Security

- Secrets management, least privilege, image scanning, dependency scanning, SBOMs
- Policy as code, signed artifacts, protected environments, admission controls

## Must-Know Commands

### Git

- `git status`
- `git log --oneline --graph --decorate`
- `git diff`
- `git revert <commit>`
- `git fetch --all --prune`

### Linux

- `top` or `htop`
- `ps aux`
- `journalctl -u <service>`
- `systemctl status <service>`
- `df -h`
- `free -m`
- `ss -tulpn`
- `lsof -i`

### Networking

- `curl -v`
- `dig <name>`
- `nslookup <name>`
- `ip addr`
- `ip route`
- `traceroute <host>` or `mtr <host>`
- `tcpdump -i <iface> port <port>`

### Docker

- `docker ps`
- `docker logs <container>`
- `docker exec -it <container> sh`
- `docker inspect <container>`
- `docker stats`

### Kubernetes

- `kubectl get pods -A`
- `kubectl describe pod <name>`
- `kubectl logs <pod> --previous`
- `kubectl get events --sort-by=.lastTimestamp`
- `kubectl top pod`
- `kubectl get svc,ingress,endpoints`
- `kubectl rollout status deployment/<name>`
- `kubectl describe node <name>`

### Terraform And Ansible

- `terraform init`
- `terraform plan`
- `terraform show`
- `terraform state list`
- `terraform force-unlock <lock-id>`
- `ansible -m ping all`
- `ansible-playbook site.yml --check`

## High-Value Scenarios To Practice

### CrashLoopBackOff

Mention:

- `kubectl describe pod`
- `kubectl logs --previous`
- config and secret validation
- entrypoint failure
- OOM or bad probes
- rollout undo if user impact is active

### ImagePullBackOff

Mention:

- bad image tag
- registry auth or `imagePullSecrets`
- private registry availability
- node egress or DNS problems

### Pending Or FailedScheduling

Mention:

- requests and limits
- taints and tolerations
- node selectors and affinity
- PVC zone binding or storage class issues

### High Latency Even After Scaling

Mention:

- CPU throttling
- connection pool exhaustion
- downstream dependency limits
- DNS latency
- kernel or node bottlenecks such as conntrack

### Terraform Wants To Recreate A Critical Resource

Mention:

- stop before `apply`
- inspect `plan` and changed attributes
- check `ForceNew` behavior and drift
- review state, module changes, and imports
- use `prevent_destroy` for critical resources

### Monitoring Shows No Data

Mention:

- target discovery
- `/metrics` reachability
- exporter health
- service monitor or scrape config
- network policy or label mismatch

## Design Trade-Offs You Should Be Ready To Explain

- Merge vs rebase
- Rolling vs blue-green vs canary deployments
- Deployment vs StatefulSet
- HPA vs VPA
- Terraform module reuse vs environment isolation
- L4 vs L7 load balancer
- Managed Kubernetes vs self-managed cluster
- Prometheus pull model vs push model
- Mutable servers vs immutable infrastructure

## Strong Signals In Senior Answers

- You lead with impact, not guesswork.
- You talk about rollback and mitigation before perfect root cause.
- You call out trade-offs instead of pretending every tool is always the best choice.
- You mention validation after the fix.
- You explain how to prevent recurrence with automation, guardrails, or observability.

## Common Weak Signals

- Jumping straight to one tool or one favorite command
- Saying "restart everything" as the first step
- Confusing symptoms with root causes
- Ignoring rollback, change history, or user impact
- Treating monitoring as CPU and memory graphs only

## Behavioral Interview Preparation

Prepare short stories for these themes:

- A production incident you helped mitigate
- A repetitive manual task you automated
- A pipeline or deployment you improved
- A security or compliance control you introduced
- A disagreement you resolved with developers, QA, or security
- A time you reduced MTTR, cost, failure rate, or deployment time

Use the STAR format, but keep it technical:

- Situation: what was failing or slow
- Task: what you owned
- Action: what you changed, automated, or investigated
- Result: measurable improvement

## Final Revision Checklist

- I can explain the path of a user request from browser to backend and database.
- I can describe how I would debug a broken deployment in Kubernetes.
- I can explain Git rollback options without confusing `reset` and `revert`.
- I can discuss Terraform state, backends, locking, and drift clearly.
- I can explain probes, Services, Ingress, HPA, and common pod failure states.
- I can describe CI/CD safety controls such as artifact immutability, approvals, and rollback.
- I can explain metrics, logs, traces, SLOs, and alert fatigue.
- I can talk through at least two real troubleshooting stories from my own work.

---

## Related Resources

- [Easy Interview Questions](interview-questions-easy.md)
- [Medium Interview Questions](interview-questions-medium.md)
- [Hard Interview Questions](interview-questions-hard.md)
- [General Interview Questions](general-interview-questions.md)
- [Azure DevOps Interview Playbook](azure-devops-interview-playbook.md)
- [Azure Scenario Drills](azure-scenario-based-drills.md)
- [Kubernetes Runbook](../05_Observability_and_Troubleshooting/Troubleshooting/kubernetes-runbook.md)
- [Senior DevOps Learning Path](../06_Advanced_DevOps_and_Architecture/Learning_Path/README.md)
