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
