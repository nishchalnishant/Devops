# Interview Questions (Medium)

These questions are aimed at engineers who already know the basics and now need to show practical depth, trade-off awareness, and troubleshooting ability across the full DevOps stack.

## Version Control (Git)

**1. Which branching strategy would you recommend for a small team shipping multiple times per day?**

Trunk-based development or a light GitHub Flow model is usually best. It keeps branches short-lived, reduces merge pain, and works well with CI/CD and feature flags.

**2. When would you choose `git rebase` over `git merge`?**

Use `rebase` to keep a private feature branch up to date with `main` and preserve a cleaner history. Use `merge` when you want to preserve branch context or avoid rewriting shared history.

**3. How do you safely undo a bad commit that has already reached `main`?**

Use `git revert` so the history stays intact and the fix is auditable. Avoid `reset --hard` on shared branches because it rewrites history and can disrupt teammates.

**4. What controls would you place on the main branch of a production repository?**

Require pull requests, status checks, code review, and signed commits if possible. I would also block force pushes, enable secret scanning, and require passing CI before merge.

**5. How do you handle repeated merge conflicts in the same files across teams?**

That usually points to poor ownership boundaries or long-lived branches. I would shorten branch lifetime, refactor conflicting areas, or adopt feature flags so integration happens earlier.

**6. When is Git LFS worth introducing?**

Use Git LFS when a repository must track large binary files such as installers, media, or model artifacts. It avoids bloating the normal Git history and keeps clone times more manageable.

## Linux & Shell Scripting

**7. A Linux server is running out of disk space. How do you investigate it?**

I would start with `df -h` for filesystem usage, then `du -sh /*` or targeted paths like `/var/log` and `/var/lib`. After locating the hot path, I would check whether logs, container layers, package caches, or orphaned files are responsible.

**8. What is the difference between an orphan process and a zombie process?**

An orphan process is still running but its parent exited, so it gets adopted by PID 1 or `systemd`. A zombie has already finished execution but still has an entry in the process table because the parent has not reaped it.

**9. Why does `systemd` matter in DevOps interviews?**

Because many production services are managed with `systemd`, and interviewers want to know whether you can inspect service state, restarts, logs, and boot behavior. Knowing `systemctl` and `journalctl` is often expected.

**10. What makes a Bash script production-safe?**

A safe script handles failure explicitly, logs clearly, and avoids silent surprises. I usually mention `set -euo pipefail`, input validation, functions, useful exit codes, and tools like ShellCheck.

**11. How do you identify which process is listening on a port?**

Use `ss -tulpn` or `lsof -i :<port>`. That tells you which PID or service owns the socket so you can check whether the binding is expected.

**12. If load average is high but CPU usage is low, what does that suggest?**

It often suggests processes are blocked on I/O rather than actively using CPU. I would inspect disk, network, and possibly lock contention using tools like `iostat`, `vmstat`, and service-specific logs.

**13. Why is log rotation important on Linux hosts?**

Without rotation, logs can consume disk, degrade performance, and even take down services. Proper rotation also keeps retention predictable and helps with compliance and incident response.

**14. When would you choose `systemd` timers over cron?**

`systemd` timers are better when you want native dependency handling, service integration, structured logs, and easier introspection. Cron is simpler, but timers are often easier to manage in modern Linux environments.

**15. How do you troubleshoot high CPU usage on a Linux host?**

1. `top` or `htop` to identify the PID with highest CPU%.
2. `ps aux --sort=-%cpu | head -10` for a snapshot.
3. `perf top -p <PID>` to see which functions are consuming CPU cycles.
4. `strace -c -p <PID>` to see if high CPU is driven by system calls.
5. Check if it is kernel CPU (`us` vs `sy` in `top`'s CPU line) — high `sy` means kernel work.
6. Check `/proc/<PID>/status` for thread count and context switches.

**16. What is `strace` and when would you use it?**

`strace` traces system calls made by a process — it shows every interaction between user-space code and the kernel (file opens, network connects, memory allocations, signal deliveries). Use it when an application fails silently and you can't see why from logs, you suspect a missing file or permission issue, or you need to find what network connections an application is making. Example: `strace -p <PID> -e trace=network` watches only network system calls.

## Networking & Cloud

**17. Why does CIDR planning matter for Kubernetes or cloud growth?**

If your VPC or subnet range is too small, you can run out of IPs for nodes, pods, or load balancers. Fixing bad address planning later is painful, especially across peering, hybrid, or multi-region setups.

**18. What is the difference between "connection refused" and "connection timed out"?**

`Connection refused` usually means you reached the host, but nothing was listening on that port or the service sent a reset. `Connection timed out` suggests packets were dropped, filtered, or never got a response.

**19. When do you choose an L4 load balancer versus an L7 load balancer?**

Choose L4 when you need fast transport-level forwarding for TCP or UDP. Choose L7 when you need host-based or path-based routing, TLS termination, header inspection, or application-aware traffic control.

**20. How would you explain DNS resolution inside Kubernetes?**

Pods usually query CoreDNS through cluster DNS configuration, and Services resolve to stable virtual names. I would also mention that DNS issues can come from CoreDNS itself, bad service selectors, or search domain behavior like `ndots`.

**21. Why keep databases in private subnets?**

Private subnets reduce direct internet exposure and enforce controlled access paths through app tiers, bastions, or VPN links. That improves security posture and makes traffic flow easier to reason about.

**22. What is the difference between a security group and a network ACL in cloud networking?**

A security group is typically stateful and attached to an instance or interface. A network ACL is usually stateless and operates at the subnet boundary, so return traffic rules must be handled explicitly.

**23. What are the trade-offs of terminating TLS at the load balancer?**

It reduces certificate management overhead on backend services and can improve application simplicity. The trade-off is that traffic behind the load balancer may be unencrypted unless you re-encrypt internally.

**24. How would you investigate intermittent network latency between services?**

I would check metrics first for scope and timing, then test DNS, endpoints, retries, and service-level error rates. After that, I would use tools like `curl`, `mtr`, `ss`, or `tcpdump` depending on where the failure seems to live.

**25. When would you recommend a read replica, and when would you recommend a cache?**

Use a read replica when the bottleneck is database read capacity and consistency rules still fit. Use a cache when the same expensive reads repeat frequently and you can tolerate cache invalidation complexity.

**26. How do you analyze network latency issues between two services?**

Start with `ping` for basic ICMP reachability and RTT. Use `traceroute` (or `mtr` for continuous path tracking) to see each hop and where latency is introduced. For TCP-level analysis, use `ss -ti` to see detailed socket statistics. For application-level HTTP, use `curl -w "@curl-format.txt"` to break down DNS resolution time, TCP connect time, TLS handshake time, and TTFB.

**27. What is `iptables` and how does Kubernetes use it?**

`iptables` is the Linux kernel's packet filtering framework, organized into tables (`filter`, `nat`, `mangle`) and chains (`INPUT`, `OUTPUT`, `FORWARD`, `PREROUTING`, `POSTROUTING`). Kubernetes uses iptables via `kube-proxy` to implement Services: when a packet targets a ClusterIP, an iptables DNAT rule in `PREROUTING` rewrites the destination to a selected pod IP using probability-based load balancing. On large clusters (>1000 services), this creates thousands of rules with O(n) traversal — IPVS mode or Cilium eBPF avoids this scalability problem.

## CI/CD & Release Engineering

**28. What stages do you expect in a healthy CI/CD pipeline?**

At minimum: checkout, build, test, security checks, package, publish artifact, deploy, and verify. Mature pipelines also include rollback hooks, approvals where needed, and post-deploy smoke tests.

**29. Why do teams use an artifact repository instead of rebuilding every time they deploy?**

An artifact repository makes releases reproducible and auditable. It supports the "build once, deploy everywhere" model and prevents different environments from using slightly different binaries.

**30. What does "build once, deploy everywhere" really mean?**

It means the exact same tested artifact moves through staging and production, rather than rebuilding per environment. That removes a whole class of environment drift and "it worked in staging" failures.

**31. What is your rollback strategy when a deployment causes customer impact?**

I prefer a fast, well-tested rollback path such as deployment revision rollback, traffic shift reversal, or previous artifact promotion. The exact choice depends on whether the problem is code, config, schema, or infrastructure.

**32. How should secrets be handled in CI/CD pipelines?**

Secrets should never live in source control or plain pipeline files. They should come from the CI platform's secret store or an external manager such as Vault, AWS Secrets Manager, or Azure Key Vault.

**33. A pipeline takes too long and blocks developers. What do you optimize first?**

I start by measuring stage timing to find the real bottleneck. Then I look at parallelization, dependency caching, Docker layer caching, test splitting, and whether expensive jobs are running unnecessarily.

**34. When is a matrix build strategy useful?**

It is useful when the same code must be tested across multiple OS, runtime, or language versions. It gives fast coverage for compatibility risks without duplicating pipeline definitions.

**35. When is a manual approval step justified?**

It is justified for high-risk environments, compliance-sensitive releases, or destructive infrastructure changes. I place it after automated validation but before the final production action.

**36. What is `semantic versioning` and how does it integrate with CI/CD?**

Semantic versioning uses `MAJOR.MINOR.PATCH` format. MAJOR: breaking changes. MINOR: new backward-compatible features. PATCH: bug fixes. In CI/CD, tools like `semantic-release` analyze commit messages using Conventional Commits (`feat:`, `fix:`, `BREAKING CHANGE:`) to automatically determine the next version, generate a changelog, tag the Git commit, and publish the release artifact.

**37. What is a canary deployment and how do you measure whether it is working?**

A canary deployment routes a small percentage of production traffic (e.g., 5%) to the new version while the majority stays on the old version. You compare error rates, latency percentiles (P50, P95, P99), and business metrics between the canary and the baseline. If the canary shows worse metrics, you rollback. Tools: Argo Rollouts, Flagger with Prometheus metrics gates, AWS CodeDeploy, Istio VirtualService weights.

**38. What does idempotency mean in infrastructure provisioning?**

Idempotency means running the same operation multiple times produces the same result. `terraform apply` is idempotent — re-running it on infrastructure that already matches the configuration makes no changes. `kubectl apply` is idempotent — applying the same manifest twice is safe. Non-idempotent scripts that append to files or create users without checking existence break this property.

## Jenkins

**39. Why do Jenkins agents or runners matter in scaling CI/CD?**

They separate execution from orchestration, which lets you run jobs in parallel and isolate build environments. That improves throughput and avoids overloading the controller.

**40. What is the difference between a Declarative and a Scripted Jenkinsfile?**

Declarative uses a structured `pipeline {}` block with predefined sections (`stages`, `steps`, `post`) that are easier to read and validate. Scripted uses Groovy code directly with `node {}` blocks and gives full flexibility at the cost of complexity and readability.

**41. What are Jenkins shared libraries and why do teams use them?**

Shared libraries are versioned Groovy code stored in a separate repository and loaded into Jenkinsfiles with `@Library`. Teams use them to share common pipeline logic — build utilities, notification steps, security checks — across many repositories without copying code into every Jenkinsfile.

**42. How does a multi-branch pipeline in Jenkins work?**

Jenkins scans a repository for branches with a `Jenkinsfile` and automatically creates a pipeline job for each one. When a new branch is pushed or a PR is opened, Jenkins detects it and runs the pipeline. Stale branch jobs are cleaned up when branches are deleted.

## GitLab CI

**43. What is a GitLab Environment and how does it support deployment tracking?**

A GitLab Environment is a named deployment target (staging, production). Pipelines that deploy to it reference `environment: name: production`, which creates an audit trail in GitLab's Deployments section. You can see which commit is deployed where, roll back to a previous deployment, require manual approval with `when: manual`, and track environment-specific variables. It also powers GitLab's DORA metrics.

**44. How do you implement approval gates in a GitLab CI pipeline?**

Use `when: manual` on a job — a human must click a button in the GitLab UI to allow that stage to proceed. For regulated environments, combine this with protected environments and required approvers so only authorized users can promote to production. The audit log captures who approved, when, and what commit was approved.

**45. What is the difference between GitLab Runners and GitHub Actions runners?**

GitLab Runners are agents registered to a GitLab instance that poll for jobs. They can be shared across projects or dedicated to a group or project. GitHub Actions runners are also agents but are registered to a repository or organization and receive jobs via a webhook-push model. Both support self-hosted options for custom hardware, network access, or cost control.

## GitHub Actions

**46. How does OIDC authentication work for GitHub Actions and why is it better than long-lived secrets?**

OIDC allows GitHub Actions to request short-lived tokens from a cloud provider (AWS, Azure, GCP) without storing any static credentials. The CI job presents a JWT token signed by GitHub, and the cloud IAM service verifies it against a trusted OIDC provider configuration, issuing a short-lived access token. Benefits: no secrets to rotate or leak, tokens expire automatically within minutes, and access is scoped to the specific repository and branch by claims in the JWT.

**47. What is a reusable workflow in GitHub Actions?**

A reusable workflow is a workflow file that can be called from other workflows using the `uses:` keyword with a repository path. It lets teams share standardized pipeline logic — security scans, build steps, deployment processes — across many repositories without duplication. The caller passes inputs and secrets; the reusable workflow runs in its own context.

**48. How do you handle secrets in GitHub Actions securely?**

Secrets are stored in the repository or organization settings and injected into workflow steps as environment variables (`${{ secrets.MY_SECRET }}`). GitHub masks secret values in log output. For cloud access, prefer OIDC over static secrets. Never print secrets with `echo`, and avoid passing secrets between jobs unless absolutely necessary.

## Docker

**49. Why are multi-stage Docker builds useful?**

They keep the final image smaller by separating build tools from runtime dependencies. That reduces image size, speeds up pulls, and lowers the attack surface.

**50. Distroless versus Alpine: how do you choose?**

Distroless images are great for minimal runtime attack surface but can be harder to debug. Alpine is small and convenient, but compatibility and debugging needs may make a fuller base image more practical.

**51. What is the difference between `CMD` and `ENTRYPOINT`?**

`ENTRYPOINT` defines the main executable, while `CMD` usually supplies default arguments. Combined correctly, they make containers predictable but still overridable when needed.

**52. When do Docker networking modes actually matter?**

They matter when you need to reason about isolation, performance, and service reachability. Bridge mode is the normal default, host mode removes network namespace isolation, and overlay networks matter in multi-host setups.

**53. How do you reduce Docker image size in a CI/CD pipeline?**

Use multi-stage builds to discard build tools, use a minimal base image (Alpine or distroless), combine `RUN` commands to reduce layers, use `.dockerignore` to exclude test files and documentation, and avoid installing debug tools in production images.

**54. What is the difference between a Docker volume and a bind mount?**

A volume is managed by Docker and stored in Docker's data directory — it persists across container restarts and is portable. A bind mount maps a host path directly into the container — it is useful for development but ties the container to the host's directory structure and ownership.

## Kubernetes

**55. When should you use a Kubernetes StatefulSet instead of a Deployment?**

Use a StatefulSet when identity, ordered rollout, and stable persistent storage matter, such as for databases or clustered stateful systems. Use a Deployment for stateless, interchangeable workloads.

**56. How do liveness, readiness, and startup probes differ?**

- **livenessProbe:** Checks if the container is still running. Failure triggers a container restart. Use it to detect deadlocks.
- **readinessProbe:** Checks if the container is ready to receive traffic. Failure removes the pod's IP from Service endpoints — traffic stops routing to it, but the container is not restarted.
- **startupProbe:** Checks if the container has started. While it is failing, liveness and readiness probes are disabled. Use it for slow-starting applications to prevent premature liveness probe failures.

**57. Why do `requests` and `limits` matter beyond scheduling?**

Requests influence placement and cluster capacity planning. Limits influence runtime behavior, QoS, and whether a noisy container can starve the node or get throttled and OOM-killed.

**58. How do you explain the different Service types in Kubernetes?**

`ClusterIP` is internal-only, `NodePort` exposes a fixed port on every node, and `LoadBalancer` integrates with the cloud provider for external access. Ingress sits above Services for HTTP routing.

**59. What is your first response to `CrashLoopBackOff`?**

1. `kubectl describe pod <pod>` — look at Events for OOMKilled, failed mounts, missing configmaps/secrets, or failed probes.
2. `kubectl logs <pod> --previous` — logs from the last crashed container instance.
3. Check resource limits with `kubectl top pod <pod>`.
4. Override the entrypoint temporarily with `command: ["sleep", "3600"]` to exec inside the container.
5. Verify the image tag exists and the registry is accessible.
6. Check if `ConfigMap` or `Secret` mounts exist.

**60. What do you check when a pod is `Pending` for too long?**

Scheduling constraints, resource requests, taints, affinity, storage, and quotas. The `kubectl describe pod` output usually points directly at why the scheduler or kubelet cannot move forward.

**61. If HPA scales pods but latency is still bad, what does that tell you?**

It suggests the bottleneck is not simply replica count. I would look at CPU throttling, database or cache saturation, connection pools, downstream dependencies, and node or network constraints.

**62. Why are NetworkPolicies important in Kubernetes?**

They let you enforce least-privilege traffic flow between pods instead of assuming all east-west traffic is safe. They are especially important in shared clusters and regulated environments.

**63. Explain Kubernetes RBAC. What is the difference between a Role and a ClusterRole?**

RBAC controls who can do what on which Kubernetes resources. A `Role` is namespace-scoped and grants permissions within a specific namespace. A `ClusterRole` is cluster-scoped and grants permissions across all namespaces, or on cluster-level resources like nodes and persistent volumes. `RoleBinding` binds a Role or ClusterRole to subjects within a namespace; `ClusterRoleBinding` binds a ClusterRole cluster-wide. Best practice: use namespace-scoped Roles wherever possible, never give ClusterAdmin to application service accounts.

**64. What is a Kubernetes NetworkPolicy and how does it work?**

A NetworkPolicy is a namespaced resource that defines L3/L4 rules controlling which pods can communicate with each other and with external endpoints. By default, Kubernetes allows all pod-to-pod communication. Once you apply any NetworkPolicy selecting a pod, only traffic explicitly allowed by that policy is permitted — all else is dropped. Enforcement is implemented by the CNI plugin (Calico, Cilium, Weave) — without a supporting CNI, NetworkPolicies are written but have no effect.

**65. What is Pod Security Admission (PSA) and why did it replace PodSecurityPolicy?**

PSA is the built-in Kubernetes (v1.25+) replacement for the deprecated PodSecurityPolicy. It operates at the namespace level using labels: `pod-security.kubernetes.io/enforce: restricted` rejects non-compliant pods; `audit` logs violations; `warn` sends user-facing warnings. PSP was complex, error-prone, and required deep RBAC knowledge. PSA simplifies this with three predefined levels: `privileged`, `baseline`, and `restricted`.

**66. What is a Kubernetes `HorizontalPodAutoscaler` and what does it require to work?**

HPA automatically scales the number of pod replicas based on observed metrics (CPU, memory, or custom/external metrics). The Metrics Server must be installed in the cluster to provide CPU/memory data to the Kubernetes API. For custom metrics, the Prometheus Adapter or KEDA is needed. HPA checks metrics every 15 seconds by default and respects scale-up/scale-down stabilization windows to prevent thrashing.

**67. How does Kubernetes schedule a pod and what happens if no node satisfies the requirements?**

The scheduler filters nodes using Predicates (hard constraints: node selectors, taints/tolerations, resource requests, affinity rules) then ranks remaining nodes using Priority functions (soft preferences: pod/node affinity, resource availability). The pod is bound to the highest-scoring node. If no node passes Predicates, the pod enters `Pending` state. The Cluster Autoscaler (if installed) detects the pending pod and provisions a new node.

**68. What is a Kubernetes Operator and when would you use one?**

An Operator is a custom controller that encodes operational knowledge for a specific application. It watches a Custom Resource Definition (CRD) and takes actions to reconcile the actual state to the desired state — for example, a database Operator manages creating replicas, running backups, and handling failover. Use an Operator when your application has lifecycle complexity beyond what Deployments, StatefulSets, and Services can express natively.

**69. How do you perform a zero-downtime rolling update in Kubernetes?**

Set `strategy.type: RollingUpdate` with `maxUnavailable: 0` and `maxSurge: 1`. This ensures one new pod is created and becomes ready before one old pod is terminated. The readinessProbe is critical — until it passes, the new pod does not receive traffic and the rollout does not proceed. Combine with `minReadySeconds` to catch flaky startup failures.

## Terraform

**70. Why use a remote backend and state locking in Terraform?**

Remote state supports team collaboration, backup, and access control. Locking prevents two people or pipelines from corrupting the same state by applying changes at the same time.

**71. How do modules help in Terraform, and where do they go wrong?**

Modules improve reuse, standardization, and consistency across environments. They go wrong when they become too generic, hide important decisions, or introduce breaking changes without version discipline.

**72. What is infrastructure drift, and how do you deal with it?**

Drift happens when real infrastructure no longer matches Terraform code, usually due to manual console changes. I detect it with `terraform plan`, restrict manual access, and reconcile changes back through code.

**73. Why is `for_each` often safer than `count`?**

`for_each` keys resources by stable names, which reduces accidental churn when list order changes. `count` is index-based and can force surprising destroy-and-recreate behavior when elements move.

**74. Why use `prevent_destroy` on some Terraform resources?**

It is a safety rail for critical resources such as production databases or foundational networking. It forces a deliberate workflow instead of allowing an accidental deletion from a bad plan.

**75. How do you introduce a breaking change in a shared Terraform module?**

Version it as a major release, publish a migration guide, and support the previous major version for a transition period. Downstream teams need notice, examples, and validation time.

**76. What is Terraform state and why is remote state important for teams?**

Terraform state is a JSON file mapping configuration resources to real-world infrastructure objects. It tracks IDs, current attributes, and dependencies. Remote state (e.g., S3 + DynamoDB, Azure Blob) prevents two people running `terraform apply` simultaneously and corrupting state, stores state durably outside developer laptops, and enables `terraform_remote_state` data sources for cross-module references.

**77. What is the difference between `terraform plan` and `terraform apply -auto-approve`?**

`terraform plan` computes the diff between desired configuration and current state, printing what would be created, changed, or destroyed — no changes are made. `terraform apply` executes the plan after user confirmation. `-auto-approve` skips the prompt. In CI/CD: `plan` in PR for review, `apply` in main/merge with `-auto-approve`. Never use `-auto-approve` without a preceding explicit plan review in sensitive environments.

**78. What is the `terraform import` command and when do you need it?**

`terraform import` brings an existing real-world resource under Terraform management without recreating it. It populates state with the resource's current attributes. You use it when infrastructure was created manually and needs to be managed as code going forward, or when migrating from one Terraform organization or workspace to another.

**79. How do you handle secrets in Terraform without storing them in state?**

Use data sources to retrieve secrets at apply time from Vault or a cloud secret manager. Use `sensitive = true` in variables and outputs to redact values in plan/apply output (though they are still written to state). Encrypt state at rest (Azure Blob with encryption, S3 SSE). The cleanest pattern: provision the secret's container via Terraform, but store and rotate the secret value externally via Vault or AWS Secrets Manager.

## Ansible

**80. When would you use Ansible after Terraform in the same platform?**

Terraform is best for provisioning infrastructure, while Ansible is useful for configuring the software inside it. I use them together when image baking is not enough or host configuration still needs orchestration.

**81. What makes an Ansible playbook idempotent?**

Each task uses modules that check existing state before making changes. For example, the `apt` module checks whether a package is already installed before installing it. Avoid using `command` or `shell` for tasks that modules can handle, since raw commands do not check for existing state.

**82. What is an Ansible role and why use roles over a flat playbook?**

A role is a structured directory layout (`tasks/`, `handlers/`, `defaults/`, `templates/`, `files/`) that encapsulates a reusable unit of configuration. Roles separate concerns, allow reuse across playbooks, and are shareable through Ansible Galaxy. A flat playbook that grows beyond a few dozen tasks becomes hard to maintain.

**83. What is the difference between `vars`, `defaults`, and `group_vars` in Ansible?**

`defaults` are the lowest-priority variable definitions in a role — easily overridden. `vars` in a role or playbook have higher priority than defaults. `group_vars` are per-group variables defined in files alongside the inventory and apply to all hosts in that group. Understanding variable precedence prevents unexpected overrides.

**84. How does Ansible handle secrets and sensitive data?**

Ansible Vault encrypts files or individual string variables. You can encrypt an entire vars file (`ansible-vault encrypt vars/secrets.yml`) or inline a single value with `!vault` syntax. The vault password is provided at runtime via `--vault-password-file` or an environment variable. For production, vault passwords themselves should come from a secrets manager or CI/CD secret store.

## GitOps

**85. What is the GitOps pull model and how is it different from traditional CI/CD push?**

In a push model, a CI pipeline connects directly to the cluster and runs `kubectl apply` or `helm upgrade` after a build — the pipeline has cluster credentials and pushes changes. In a pull model, an agent (ArgoCD, Flux) running inside the cluster continuously polls a Git repository. When it detects a difference between Git state and cluster state, it reconciles by applying the Git state. The cluster never exposes external access — credentials never leave the cluster, improving auditability and security.

**86. What is ArgoCD and how does it implement GitOps?**

ArgoCD is a declarative GitOps tool for Kubernetes. It monitors Git repositories for changes to Kubernetes manifests and automatically (or on demand) applies them to the cluster. It provides a UI and CLI showing the sync status of every application, drift detection when the live state diverges from Git, and rollback by reverting the Git commit. ArgoCD supports Helm, Kustomize, jsonnet, and raw YAML.

**87. What is an ArgoCD ApplicationSet and when would you use it?**

An ApplicationSet is a controller that generates multiple ArgoCD Applications from a single template, using generators such as List, Git, Matrix, or Cluster. Use it when you want to deploy the same application across multiple clusters or environments without defining a separate Application resource for each one — for example, deploying a microservice to all regions using a cluster generator.

## Observability & SRE

**88. What are the Four Golden Signals, and why do they matter?**

Latency, traffic, errors, and saturation are a simple but powerful way to judge service health. They keep monitoring focused on real user impact rather than random low-value metrics.

**89. What is high-cardinality telemetry, and why is it risky?**

It means labels create too many unique time series, such as using `user_id` or request IDs in metrics. That can blow up memory usage, slow down queries, and make monitoring systems unstable.

**90. How do SLI, SLO, and error budget relate to each other?**

An SLI is what you measure, an SLO is the target, and the error budget is how much failure you can spend before reliability work must take priority. This turns reliability into an engineering trade-off instead of guesswork.

**91. How do logs, metrics, and traces work together during incident response?**

Metrics tell me that something is wrong and help with scope, traces tell me where time is spent across services, and logs explain the detailed failure. I use them together rather than relying on only one signal.

**92. What is an SLI, SLO, and SLA? Give concrete examples for a web API.**

- **SLI:** A quantitative measure of service behavior. Example: the ratio of successful HTTP requests (status < 500) to total requests in a 1-minute window.
- **SLO:** A target threshold for an SLI. Example: availability SLI >= 99.9% over a rolling 30-day window.
- **SLA:** A contractual commitment with financial penalties for breach. Example: we guarantee 99.9% availability; if we miss it, customers receive service credits.
SLOs are internal targets; SLAs are external commitments. Design SLOs tighter than your SLA to maintain a buffer.

**93. What is an error budget and what does "burning the error budget" mean?**

An error budget is the allowed downtime derived from an SLO: `error budget = (1 - SLO) × window`. For 99.9% over 30 days: `0.001 × 43,200 minutes = 43.2 minutes`. When an incident causes downtime or elevated errors, those minutes are burned from the budget. If the budget is consumed, the team must freeze feature releases and focus on reliability. This creates a data-driven conversation between product and engineering.

**94. What is distributed tracing and what is the OpenTelemetry standard?**

Distributed tracing tracks a single request as it flows through multiple microservices, capturing the start/end time and metadata at each hop (a "span"). Spans are grouped into a trace by a shared `trace-id`. OpenTelemetry (OTel) is a vendor-neutral CNCF standard providing SDKs and APIs for instrumenting applications to emit traces, metrics, and logs in a common format. OTel data is exported to backends like Jaeger, Zipkin, Tempo, Datadog, or Honeycomb.

**95. What is a Prometheus `recording rule` and when would you create one?**

A recording rule pre-computes expensive or frequently-queried PromQL expressions and stores the result as a new time series. Example: computing the 99th percentile request latency across all pods is expensive to calculate on every dashboard load — a recording rule computes it every minute and stores it as `job:request_latency_seconds:p99`. Dashboards query the result instead of re-computing it. Recording rules also simplify complex expressions referenced in alerting rules.

**96. What is the difference between black-box monitoring and white-box monitoring?**

Black-box monitoring tests the system from the outside, as a user would experience it — probing external endpoints for availability and correctness. It catches user-facing outages regardless of internal implementation. White-box monitoring instruments the application internals — exposing metrics from inside the process (request queue depth, GC pause time, database connection pool). Together they give complete visibility: white-box catches degradation early, black-box catches user-visible failures.

**97. What is your incident response sequence when a critical service is failing?**

Confirm impact, stabilize, check recent changes, gather telemetry, narrow the failing layer, and execute the safest mitigation. After recovery, capture root cause, timeline, and prevention actions in an RCA.

## Security & Secrets Management

**98. What does least privilege mean for a CI/CD system?**

The pipeline should have only the permissions needed for its job, such as pushing to one registry or deploying to one namespace. That limits blast radius if credentials leak or a pipeline is abused.

**99. Where do image scanning and SBOMs fit into the delivery process?**

Image scanning belongs after image build and before promotion, while SBOM generation helps track what is inside the artifact over time. Together they improve vulnerability response and supply chain visibility.

**100. What is HashiCorp Vault and how does it improve secrets management over Kubernetes Secrets?**

Vault is a secrets management platform that provides: dynamic secrets (generated on-demand with TTLs — e.g., short-lived database credentials), centralized access control with audit logging, secrets versioning and rotation, and multiple authentication methods (Kubernetes, OIDC, AWS IAM). Unlike Kubernetes Secrets (which are base64-encoded in etcd), Vault encrypts at rest with its own seal key, supports automatic rotation, and provides a full audit trail of every secret access.

**101. What is mutual TLS (mTLS) and where is it used in Kubernetes?**

Standard TLS authenticates the server to the client. mTLS additionally authenticates the client to the server — both parties present certificates. In Kubernetes, service meshes (Istio, Linkerd, Cilium) enforce mTLS between every pod-to-pod communication automatically, without application code changes. This ensures only pods with valid certificates (issued by the mesh's CA) can communicate.

**102. What is the Software Supply Chain and what attacks target it?**

The software supply chain is the path from source code through build, test, dependency resolution, packaging, and deployment. Supply chain attacks target this path: compromising a popular npm/PyPI package (dependency confusion, typosquatting), injecting malicious code into a build environment, hijacking CI runner credentials, or tampering with an artifact between build and deployment. Defenses: SLSA framework, artifact signing (Cosign/Sigstore), SBOM generation, pinned dependency hashes, and isolated build environments.

**103. What is a Service Account in Kubernetes and what are the security risks of the default service account?**

Every pod runs with a Kubernetes ServiceAccount that determines what the pod can do via RBAC. By default, pods use the `default` service account in their namespace, which may have accumulated permissions over time. The service account token is automatically mounted inside the pod at `/var/run/secrets/kubernetes.io/serviceaccount/token`. If an attacker gains shell access to the pod, they can use this token to call the Kubernetes API. Mitigation: set `automountServiceAccountToken: false` on pods that don't need API access, create dedicated service accounts with minimal RBAC, and use projected token volumes with shorter TTLs.

## Azure Infrastructure & CI/CD

**104. What is the difference between an Azure Managed Identity and a Service Principal?**

A Service Principal is an identity created for use with applications, hosted services, and automated tools to access Azure resources — requiring you to explicitly manage and rotate its secret or certificate. A Managed Identity is a feature of Microsoft Entra ID that provides an automatically managed identity in Azure. You don't manage credentials; Azure handles the lifecycle of the identity, especially System-Assigned ones which die when the resource is deleted.

**105. How do you securely manage Terraform state for Azure infrastructure?**

Terraform state should be managed in an Azure Storage Account Blob container using the `azurerm` backend. To secure it: lock down the Storage Account's network access, use RBAC to restrict access to the state blob to the pipeline's identity, enable Soft Delete and point-in-time restore, and ensure the state file is locked during runs using Azure blob leases to prevent concurrent state corruption.

**106. What are the pros and cons of using Azure Logic Apps vs. Azure Functions?**

Azure Functions is a code-first serverless compute service — better for complex, custom logic, high-performance data processing, and developers who prefer coding in C#, Python, or Node.js. Azure Logic Apps is a designer-first, visual orchestration service — it excels at workflow automation and connecting third-party systems using hundreds of pre-built connectors. Great for low-code integrations but can become visually unwieldy for highly complex nested programming logic.

**107. Explain how you would implement a Blue-Green deployment for an Azure App Service.**

Azure App Service provides Deployment Slots. You create a second slot (e.g., `staging`) identical to `production`. The CI/CD pipeline deploys the new code to the `staging` slot. Once the staging slot passes smoke tests, you perform a "Swap" operation in Azure. Azure routes production traffic to the new instances, and what was production becomes staging. If an issue occurs, you instantly swap back.

**108. Why is Bicep gaining popularity over ARM templates?**

ARM templates are JSON-based, verbose, and difficult to comprehend at scale without extensive tooling. Bicep is a DSL created by Microsoft specifically for deploying Azure resources. It offers a much cleaner, easier-to-read syntax, transparent compilation into standard ARM JSON, modularity via the `module` block, and day-zero support for new Azure features without waiting for an external provider update.

**109. What is Azure Key Vault and how do you integrate it with a Kubernetes workload?**

Azure Key Vault is a managed service for storing secrets, certificates, and keys. To integrate with Kubernetes, use the Secrets Store CSI Driver with the Azure Key Vault provider — it mounts secrets from Key Vault directly into pods as volume files or environment variables. Combined with a Managed Identity for the pod (via Azure Workload Identity or AAD Pod Identity), the pod authenticates to Key Vault without any stored credentials.

**110. What is the difference between Azure DevOps Service Connections and GitHub OIDC?**

An Azure DevOps Service Connection stores credentials (Service Principal client secret or certificate) in Azure DevOps to authenticate to external resources. GitHub OIDC, by contrast, uses federated identity — no stored credentials at all. The GitHub Actions workflow requests a short-lived token from the cloud provider by presenting a JWT signed by GitHub's OIDC endpoint. OIDC is the preferred modern approach because credentials cannot leak if there is nothing stored.
