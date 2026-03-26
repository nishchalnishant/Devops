# Interview Questions (Medium)

These questions are aimed at engineers who already know the basics and now need to show practical depth, trade-off awareness, and troubleshooting ability across the full DevOps stack.

## Git And Collaboration

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

## Linux And Shell

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

## Networking And Cloud

**15. Why does CIDR planning matter for Kubernetes or cloud growth?**

If your VPC or subnet range is too small, you can run out of IPs for nodes, pods, or load balancers. Fixing bad address planning later is painful, especially across peering, hybrid, or multi-region setups.

**16. What is the difference between "connection refused" and "connection timed out"?**

`Connection refused` usually means you reached the host, but nothing was listening on that port or the service sent a reset. `Connection timed out` suggests packets were dropped, filtered, or never got a response.

**17. When do you choose an L4 load balancer versus an L7 load balancer?**

Choose L4 when you need fast transport-level forwarding for TCP or UDP. Choose L7 when you need host-based or path-based routing, TLS termination, header inspection, or application-aware traffic control.

**18. How would you explain DNS resolution inside Kubernetes?**

Pods usually query CoreDNS through cluster DNS configuration, and Services resolve to stable virtual names. I would also mention that DNS issues can come from CoreDNS itself, bad service selectors, or search domain behavior like `ndots`.

**19. Why keep databases in private subnets?**

Private subnets reduce direct internet exposure and enforce controlled access paths through app tiers, bastions, or VPN links. That improves security posture and makes traffic flow easier to reason about.

**20. What is the difference between a security group and a network ACL in cloud networking?**

A security group is typically stateful and attached to an instance or interface. A network ACL is usually stateless and operates at the subnet boundary, so return traffic rules must be handled explicitly.

**21. What are the trade-offs of terminating TLS at the load balancer?**

It reduces certificate management overhead on backend services and can improve application simplicity. The trade-off is that traffic behind the load balancer may be unencrypted unless you re-encrypt internally.

**22. How would you investigate intermittent network latency between services?**

I would check metrics first for scope and timing, then test DNS, endpoints, retries, and service-level error rates. After that, I would use tools like `curl`, `mtr`, `ss`, or `tcpdump` depending on where the failure seems to live.

**23. When would you recommend a read replica, and when would you recommend a cache?**

Use a read replica when the bottleneck is database read capacity and consistency rules still fit. Use a cache when the same expensive reads repeat frequently and you can tolerate cache invalidation complexity.

**24. What makes a cloud design interview answer strong?**

A strong answer mentions availability, security, observability, cost, and rollback or recovery. I also like to call out blast radius, multi-AZ deployment, IAM boundaries, and failure testing.

## CI/CD And Release Engineering

**25. What stages do you expect in a healthy CI/CD pipeline?**

At minimum: checkout, build, test, security checks, package, publish artifact, deploy, and verify. Mature pipelines also include rollback hooks, approvals where needed, and post-deploy smoke tests.

**26. Why do teams use an artifact repository instead of rebuilding every time they deploy?**

An artifact repository makes releases reproducible and auditable. It supports the "build once, deploy everywhere" model and prevents different environments from using slightly different binaries.

**27. What does "build once, deploy everywhere" really mean?**

It means the exact same tested artifact moves through staging and production, rather than rebuilding per environment. That removes a whole class of environment drift and "it worked in staging" failures.

**28. What is your rollback strategy when a deployment causes customer impact?**

I prefer a fast, well-tested rollback path such as deployment revision rollback, traffic shift reversal, or previous artifact promotion. The exact choice depends on whether the problem is code, config, schema, or infrastructure.

**29. How should secrets be handled in CI/CD pipelines?**

Secrets should never live in source control or plain pipeline files. They should come from the CI platform's secret store or an external manager such as Vault, AWS Secrets Manager, or Azure Key Vault.

**30. A pipeline takes too long and blocks developers. What do you optimize first?**

I start by measuring stage timing to find the real bottleneck. Then I look at parallelization, dependency caching, Docker layer caching, test splitting, and whether expensive jobs are running unnecessarily.

**31. When is a matrix build strategy useful?**

It is useful when the same code must be tested across multiple OS, runtime, or language versions. It gives fast coverage for compatibility risks without duplicating pipeline definitions.

**32. Why do Jenkins agents or runners matter in scaling CI/CD?**

They separate execution from orchestration, which lets you run jobs in parallel and isolate build environments. That improves throughput and avoids overloading the controller.

**33. When is a manual approval step justified?**

It is justified for high-risk environments, compliance-sensitive releases, or destructive infrastructure changes. I place it after automated validation but before the final production action.

## Docker And Kubernetes

**34. Why are multi-stage Docker builds useful?**

They keep the final image smaller by separating build tools from runtime dependencies. That reduces image size, speeds up pulls, and lowers the attack surface.

**35. Distroless versus Alpine: how do you choose?**

Distroless images are great for minimal runtime attack surface but can be harder to debug. Alpine is small and convenient, but compatibility and debugging needs may make a fuller base image more practical.

**36. What is the difference between `CMD` and `ENTRYPOINT`?**

`ENTRYPOINT` defines the main executable, while `CMD` usually supplies default arguments. Combined correctly, they make containers predictable but still overridable when needed.

**37. When do Docker networking modes actually matter?**

They matter when you need to reason about isolation, performance, and service reachability. Bridge mode is the normal default, host mode removes network namespace isolation, and overlay networks matter in multi-host setups.

**38. When should you use a Kubernetes StatefulSet instead of a Deployment?**

Use a StatefulSet when identity, ordered rollout, and stable persistent storage matter, such as for databases or clustered stateful systems. Use a Deployment for stateless, interchangeable workloads.

**39. How do liveness, readiness, and startup probes differ?**

Liveness decides whether Kubernetes should restart the container. Readiness decides whether traffic should be sent to it. Startup probes protect slow-starting applications from being killed too early.

**40. Why do `requests` and `limits` matter beyond scheduling?**

Requests influence placement and cluster capacity planning. Limits influence runtime behavior, QoS, and whether a noisy container can starve the node or get throttled and OOM-killed.

**41. How do you explain the different Service types in Kubernetes?**

`ClusterIP` is internal-only, `NodePort` exposes a fixed port on every node, and `LoadBalancer` integrates with the cloud provider for external access. I also mention that Ingress sits above Services for HTTP routing.

**42. What is your first response to `CrashLoopBackOff`?**

I check `kubectl describe pod`, then logs from the current and previous container, then events and rollout history. I want to know whether the failure is startup logic, config, image, dependency, probe, or resources.

**43. What do you check when a pod is `Pending` for too long?**

Scheduling constraints, resource requests, taints, affinity, storage, and quotas. The `describe` output usually points directly at why the scheduler or kubelet cannot move forward.

**44. If HPA scales pods but latency is still bad, what does that tell you?**

It suggests the bottleneck is not simply replica count. I would look at CPU throttling, database or cache saturation, connection pools, downstream dependencies, and node or network constraints.

**45. Why are NetworkPolicies important in Kubernetes?**

They let you enforce least-privilege traffic flow between pods instead of assuming all east-west traffic is safe. They are especially important in shared clusters and regulated environments.

## Terraform And Configuration Management

**46. Why use a remote backend and state locking in Terraform?**

Remote state supports team collaboration, backup, and access control. Locking prevents two people or pipelines from corrupting the same state by applying changes at the same time.

**47. How do modules help in Terraform, and where do they go wrong?**

Modules improve reuse, standardization, and consistency across environments. They go wrong when they become too generic, hide important decisions, or introduce breaking changes without version discipline.

**48. What is infrastructure drift, and how do you deal with it?**

Drift happens when real infrastructure no longer matches Terraform code, usually due to manual console changes. I detect it with `terraform plan`, restrict manual access, and reconcile changes back through code.

**49. Why is `for_each` often safer than `count`?**

`for_each` keys resources by stable names, which reduces accidental churn when list order changes. `count` is index-based and can force surprising destroy-and-recreate behavior when elements move.

**50. When would you use Ansible after Terraform in the same platform?**

Terraform is best for provisioning infrastructure, while Ansible is useful for configuring the software inside it. I use them together when image baking is not enough or host configuration still needs orchestration.

**51. Why use `prevent_destroy` on some Terraform resources?**

It is a safety rail for critical resources such as production databases or foundational networking. It forces a deliberate workflow instead of allowing an accidental deletion from a bad plan.

**52. How do you introduce a breaking change in a shared Terraform module?**

Version it as a major release, publish a migration guide, and support the previous major version for a transition period. Downstream teams need notice, examples, and validation time.

## Observability, Security, And SRE

**53. What are the Four Golden Signals, and why do they matter?**

Latency, traffic, errors, and saturation are a simple but powerful way to judge service health. They keep monitoring focused on real user impact rather than random low-value metrics.

**54. What is high-cardinality telemetry, and why is it risky?**

It means labels create too many unique time series, such as using `user_id` or request IDs in metrics. That can blow up memory usage, slow down queries, and make monitoring systems unstable.

**55. How do SLI, SLO, and error budget relate to each other?**

An SLI is what you measure, an SLO is the target, and the error budget is how much failure you can spend before reliability work must take priority. This turns reliability into an engineering trade-off instead of guesswork.

**56. How do logs, metrics, and traces work together during incident response?**

Metrics tell me that something is wrong and help with scope, traces tell me where time is spent across services, and logs explain the detailed failure. I use them together rather than relying on only one signal.

**57. What does least privilege mean for a CI/CD system?**

The pipeline should have only the permissions needed for its job, such as pushing to one registry or deploying to one namespace. That limits blast radius if credentials leak or a pipeline is abused.

**58. Where do image scanning and SBOMs fit into the delivery process?**

Image scanning belongs after image build and before promotion, while SBOM generation helps track what is inside the artifact over time. Together they improve vulnerability response and supply chain visibility.

**59. What is your incident response sequence when a critical service is failing?**

Confirm impact, stabilize, check recent changes, gather telemetry, narrow the failing layer, and execute the safest mitigation. After recovery, capture root cause, timeline, and prevention actions in an RCA.

**60. How do you answer a design trade-off question well in a DevOps interview?**

State the goal and constraints first, compare at least two viable options, explain trade-offs in reliability, security, cost, and operability, and finish with why your choice fits the workload. A strong answer sounds reasoned, not absolute.
