# Scenario-Based DevOps Interview Drills

```
Scenario-Based DevOps Interview Drills
├── Answer Structure For Every Scenario
│   ├── 1. Confirm impact and scope
│   ├── 2. Check recent changes (deploy, config, infra)
│   ├── 3. Look at user-facing metrics first
│   ├── 4. Narrow to app / container / node / network / database / pipeline
│   ├── 5. Run smallest commands that prove or reject hypothesis
│   ├── 6. Stabilize before chasing perfect root cause
│   └── 7. End with long-term fix and prevention
├── Scenario 1: Flash Sale Meltdown On Kubernetes
│   ├── Prompt: 10k → 150k RPS, 504s, HPA scaled to 100 pods, DB not saturated
│   ├── Blast radius check: Grafana latency/error rate, is it isolated to checkout?
│   ├── Commands: kubectl top pod, describe deploy, logs, get svc/ingress/endpoints, describe node
│   ├── Root causes: CPU throttling, connection pool exhaustion, upstream bottleneck, conntrack, LB timeout mismatch
│   └── Mitigations: right-size limits, increase pool, rate limit / load shed, shift non-critical traffic, rollback recent change
├── Scenario 2: CrashLoopBackOff After Deployment
│   ├── Prompt: new version deployed, pods immediately crash, health checks fail
│   ├── Separate startup failure from readiness failure
│   ├── Commands: describe pod, logs --previous, get events --sort-by=.lastTimestamp, rollout history, rollout undo
│   ├── Root causes: bad env var / secret, wrong entrypoint, dependency change, probe misconfiguration, OOMKilled at startup
│   └── Mitigations: rollback if impact is active, inspect diff vs last good release, add startup probe, add CI smoke tests
├── Scenario 3: Pod Stuck In Pending Or FailedScheduling
│   ├── Prompt: critical workload stuck, replica count below desired
│   ├── Scheduling based on requests, constraints, storage placement
│   ├── Commands: describe pod, get nodes, describe node, get pvc/pv, get events
│   ├── Root causes: requests exceed allocatable, taint/toleration mismatch, affinity rule wrong, PVC zone mismatch, quota limit
│   └── Mitigations: reduce oversized requests, add node capacity, fix constraints and storage class, reserve dedicated nodes
├── Scenario 4: CI Pipeline Succeeds But Production Is Broken
│   ├── Prompt: pipeline passed, deployed, production broken, staging looked fine
│   ├── Pipeline success ≠ runtime health
│   ├── Checks: compare image digest staging vs prod, rollout status, describe configmap/secret, probe + smoke test coverage
│   ├── Root causes: different runtime config or secret, missing migration, staging data unlike prod, feature flag mismatch, different artifact deployed than tested
│   └── Mitigations: rollback, enforce build-once-deploy-everywhere, add post-deploy smoke tests, treat config as versioned code
├── Scenario 5: Terraform Plan Wants To Recreate Production Database
│   ├── Prompt: terraform plan shows destroy+recreate for a prod DB, supposed to be a small update
│   ├── Stop before apply — inspect ForceNew, state drift, module changes, imports
│   ├── Commands: terraform plan, show, state show <resource>, git diff; check provider docs for ForceNew attributes
│   ├── Root causes: changed immutable attribute, manual drift, refactored module path, mismatched import
│   └── Mitigations: prevent_destroy lifecycle, split state so app changes can't touch DB, review plans in CI, backup state before risky changes
├── Scenario 6: DNS Or Service-To-Service Connectivity Failure
│   ├── Prompt: microservice can't reach another inside K8s, destination pods look healthy
│   ├── Distinguish: DNS failure vs Service/endpoint failure vs NetworkPolicy failure
│   ├── Commands: get svc/endpoints, exec nslookup, exec curl, get networkpolicy, logs kube-system kube-dns
│   ├── Root causes: selector doesn't match pods, no ready endpoints, CoreDNS issue, NetworkPolicy blocking east-west, port mismatch
│   └── Mitigations: fix selectors and ports, restart CoreDNS only if DNS is confirmed issue, add synthetic connectivity checks, document dependency map
├── Scenario 7: Monitoring Shows No Data Or Too Many Alerts
│   ├── Prompt: Grafana shows "No Data" for one service, or team flooded with useless alerts
│   ├── Check target discovery before blaming dashboards
│   ├── Checks: Prometheus /targets page, curl pod-ip/metrics, logs for Prometheus/exporter/Alertmanager, review alert rules and label routes
│   ├── Root causes: bad ServiceMonitor or scrape config, metrics endpoint changed, NetworkPolicy blocking scrape, high-cardinality labels, alerting on causes not symptoms
│   └── Mitigations: restore scrape reachability, reduce noisy alerts by severity, use SLO/symptom-based paging alerts, standardize labels (service, env, version)
├── Scenario 8: Kong API Gateway 502/504 Meltdown Under High Concurrency
│   ├── Prompt: intermittent 502/504 on DP nodes under spikes; upstreams look healthy, low node CPU/Mem
│   ├── Checks: inspect PDK socket boundaries, downstream connections, upstream keepalive thresholds, fd limits
│   ├── Root causes: keepalive pool starvation, socket descriptor exhaustion (ulimit -n), dns resolver latency in Lua VMs
│   └── Mitigations: scale keepalive pool sizes, increase dynamic file descriptor limits, inject ngx.shared local caching
├── Scenario 9: eBPF-Based Cilium CNI Packet Drops & S2S Latency
│   ├── Prompt: inter-service packet loss, simple pings succeed, but TLS handshakes timeout
│   ├── Checks: check identity/conntrack map size, debug drop types using cilium monitor
│   ├── Root causes: strict BPF verifier rejection, BPF map overflows, MTU size mismatch (encapsulation overhead)
│   └── Mitigations: trace drop flows via Hubble, adjust MTU sizes in Agent DaemonSet, scale BPF map sizes
└── Scenario 10: Kubernetes Custom Operator Hot-Loop CPU Exhaustion
    ├── Prompt: custom reconciler operator consuming 100% CPU on master nodes, APIServer timeouts
    ├── Checks: check reconciler events, watch custom resource versions, trace API Server audit logs
    ├── Root causes: infinite reconciliation loops (updating spec/status without predicates), workqueue starvation
    └── Mitigations: enforce metadata.generation filters, use dedicated status subresources, implement rate-limiting workqueue
```

## First Principles

- **Why scenarios, not just Q&A?** Interview scenarios test judgment under pressure, not recall. A scenario requires you to sequence actions, name commands, and explain why each step matters — that sequence is the actual skill being evaluated.
- **Why start with scope before commands?** Running commands without knowing the blast radius risks making things worse. Understanding whether the failure is isolated to one pod, one service, or the whole cluster determines which commands are even worth running.
- **Why rollback before root cause in multiple scenarios?** The purpose of incident response is to restore user service. Rollback is often the fastest path. Root cause investigation is important but is a second-order priority while users are impacted.
- **Why focus on distinguishing error types?** CrashLoopBackOff, ImagePullBackOff, and Pending all look like "pod not working" but have completely different causes and different fix paths. Inability to distinguish them signals surface-level knowledge.
- **Why end every scenario with prevention?** Mitigation fixes the current instance. Prevention fixes the class of problem. Senior engineers are expected to close the loop with automation, guardrails, or observability improvements so the same type of failure cannot recur.

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

## Scenario 8: Kong API Gateway 502/504 Meltdown Under High Concurrency

### Prompt

Kong Hybrid deployment Data Plane (DP) nodes are returning intermittent `502 Bad Gateway` and `504 Gateway Timeout` errors under a sudden traffic burst (e.g., 20k concurrent connections). Upstream backend service pods look healthy (CPU/Memory are low, response latency from backends is normal), and the DP nodes themselves are running below 40% CPU and memory saturation.

### What A Strong Answer Should Cover

- Trace the failure to either edge networking, internal Lua PDK cosocket limitations, or file-descriptor constraints on the proxy rather than the upstream backends.
- Understand that OpenResty's PDK cannot perform non-blocking cosocket networking in early phases like `rewrite`, `certificate`, or `header_filter` without stalling execution or failing, and identify phase transitions as prime candidates for socket issues.
- Explain the significance of connection pooling bottlenecks between the proxy and dynamic upstream destinations.

### Commands And Checks You Can Name

- Check proxy logs: `tail -f /usr/local/kong/logs/error.log` for lines containing `socket leak`, `cannot create socket`, `no free connection`, or `host not found`.
- Check open file descriptor constraints on the system: `ulimit -n` and `sysctl fs.file-max`.
- Verify proxy connection states using `netstat -an | grep TIME_WAIT` or `ss -s` to detect socket accumulation.

### Likely Root Causes

- **Keepalive Pool Starvation:** Upstream keepalive parameters (`upstream_keepalive_max_requests` or `upstream_keepalive_pool_size`) are too small, forcing Kong to close and recreate TCP connections on every few requests, depleting local ephemeral ports under concurrency.
- **File Descriptor Exhaustion:** The OS `ulimit -n` limit on Kong DP pods/processes is set too low (e.g., default 1024), resulting in "too many open files" errors under concurrency.
- **Dynamic Lua Cosocket DNS Latency:** Custom Lua plugins resolving dynamic upstreams on the fly inside the `access` phase are choking due to slow or blocking DNS lookups in the internal Lua virtual machine resolver.

### Strong Mitigation Ideas

- Increase the Kong configuration upstream keepalive settings: raise `upstream_keepalive_pool_size` (e.g., from 60 to 512) and `upstream_keepalive_max_requests` (e.g., to 10000+).
- Scale up the file-descriptor limits by setting `ulimit -n 65535` or using container security contexts to raise `nofile` limits.
- Optimize custom plugins: utilize OpenResty dynamic shared dictionary memory (`ngx.shared.DICT`) as a Layer 1 cache for dynamic routing decisions to reduce overhead in the critical path.

## Scenario 9: eBPF-Based Cilium CNI Packet Drops & S2S Latency

### Prompt

A Kubernetes cluster running with Cilium CNI (and `kube-proxy` completely disabled via eBPF host routing) begins experiencing intermittent inter-service network failure. Simple ICMP `ping` between container endpoints succeeds, but application-level TCP/TLS handshakes timeout or drop packets.

### What A Strong Answer Should Cover

- Highlight the distinction between basic IP-level routing and eBPF-based socket/packet-level filters.
- Recognize that Cilium uses eBPF maps for connection tracking, endpoint identities, and load-balancing, and map overflow or misconfiguration directly causes packet silence.
- Explain how packet encapsulation overhead (VXLAN/Geneve) interacts with standard MTU (Maximum Transmission Unit) sizes on host network interfaces.

### Commands And Checks You Can Name

- Run Cilium diagnostics: `cilium status` and check for errors or map capacity warnings.
- Monitor drop events in real-time: `cilium monitor --type drop` to capture eBPF drop reasons (e.g., `DROP_INVALID_SYN`, `DROP_POLICY`).
- Inspect Cilium connection tracking maps: `cilium bpf ct list global` and identity maps: `cilium bpf identity list`.
- Test MTU size boundaries using `ping -M do -s 1450 <dest-ip>`.

### Likely Root Causes

- **Connection Tracking Map Overflow:** The eBPF connection tracking (`ct`) map has filled to capacity because the cluster scale or connection count exceeded the default limits, causing the kernel to drop new TCP SYN packets.
- **MTU Mismatch (Path MTU Discovery failure):** VXLAN or Geneve encapsulation adds overlay header bytes (50 bytes for VXLAN). If host interfaces have an MTU of 1500 and the pod interfaces are also set to 1500, packet fragmentation or silent drops occur on larger payloads (like TLS certificates).
- **Stale Identity Mapping:** Out-of-sync dynamic security identities in the Cilium agent causing eBPF programs to enforce policy drops on valid cross-namespace connections.

### Strong Mitigation Ideas

- Increase map limits in the Cilium Helm values config (e.g., increase `bpf-map-dynamic-size-ratio` or manually scale `bpf.mapLimits.conntrack`).
- Adjust MTU configurations: decrease the pod interface MTU (e.g., set `mtu: 1450` in Cilium's ConfigMap) to account for encapsulation overhead, matching host constraints.
- Utilize Hubble (`hubble observe`) to trace flow details and pinpoint the exact policy rule or map block causing drops.

## Scenario 10: Kubernetes Custom Operator Hot-Loop CPU Exhaustion

### Prompt

You receive alert notifications that the Kubernetes master nodes are experiencing high CPU load (100% core saturation), resulting in control-plane API latency. A custom Kubernetes operator built using `controller-runtime` (managing a custom resource `AppService`) is running in a hot loop, triggering massive APIServer write loads.

### What A Strong Answer Should Cover

- Explain the mechanics of level-triggered reconcilers and how dynamic loops form if they are not guarded by idempotency.
- Explain why direct reconciliation modifications of the resource `Spec` or `Status` can trigger endless circular loops if event filters are not configured.
- Separate Lister cache reads from APIServer writes, identifying redundant writes as the key bottleneck.

### Commands And Checks You Can Name

- Watch resource version updates in real-time: `kubectl get appservices -w` to see if `resourceVersion` is incrementing multiple times per second.
- Inspect the custom operator's log files: `kubectl logs deployment/custom-operator -n operators --tail=500` for rapid recurring reconciling triggers on the same object.
- Review APIServer write metrics inside Prometheus: `apiserver_request_total{verb="PUT"}` or check API server audit logs to isolate the client IP causing write load.

### Likely Root Causes

- **Circular Reconciler Updates:** The reconciler is modifying the resource's `Spec` during execution without checking if the desired state already matches the actual state. Every write triggers a new event, queuing another reconcile loop indefinitely.
- **Status Update Churn without Filters:** The reconciler updates the custom resource's status subresource on every pass but does not register update predicates (`event.Filter` or `generationChangedPredicate`) to ignore status updates, causing status writes to trigger new reconciliation triggers.
- **Starved Workqueue Rate Limiting:** The operator's workqueue does not implement exponential backoff rate-limiting, causing failing reconciles (e.g., due to temporary external service unavailability) to be retried instantly without cooling off.

### Strong Mitigation Ideas

- **Implement Idempotency Guards:** Before issuing a `client.Update()` or `client.Status().Update()` call, always check if the in-memory object actually differs from the database/cache state.
- **Enforce Generation Changed Predicates:** Configure the controller builder with predicates to only watch Spec changes:
  ```go
  Builder.ControllerManagedBy(mgr).
      For(&v1alpha1.AppService{}, builder.WithPredicates(predicate.GenerationChangedPredicate{})).
      Complete(r)
  ```
- **Use Status Subresources:** Ensure the CRD uses a `/status` subresource and update it with `client.Status().Update()` instead of writing to the main resource, keeping Spec and Status updates strictly segregated.

## Short Answer Pattern For Final Rounds

If you get stuck, use this fallback structure:

> I would first confirm user impact and timing, then check recent deployments or config changes. Next I would inspect metrics, logs, and events to narrow the issue to the app, container, node, network, or dependency layer. If production is unhealthy, I would stabilize with rollback, traffic reduction, or feature degradation before driving to permanent root cause.

## What Makes A Candidate Sound Senior

- You say which commands you would run.
- You explain why each command matters.
- You separate immediate mitigation from deep investigation.
- You talk about blast radius, rollback, and prevention.
- You avoid guessing a root cause without evidence.
