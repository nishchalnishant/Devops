# Interview Questions (Easy)

These questions are aimed at candidates with roughly 2 to 4 years of hands-on CI/CD and DevOps experience.

---

## General CI/CD Concepts

**1. What is CI/CD and why is it important?**

CI/CD stands for Continuous Integration and Continuous Delivery/Deployment. It automates the software build, test, and release process. It allows teams to deliver code changes more frequently and reliably, reducing risk and improving velocity.

**2. Explain the difference between Continuous Integration, Continuous Delivery, and Continuous Deployment.**

- Continuous Integration (CI): Developers merge code into a central repository frequently. Each merge triggers an automated build and test. The goal is to catch integration bugs early.
- Continuous Delivery: Every code change that passes automated tests is automatically packaged and released to a staging environment. The release to production is a manual, one-click step.
- Continuous Deployment: Every change that passes all stages is automatically deployed to production without human intervention.

**3. What are the main benefits of implementing a CI/CD pipeline?**

Faster release cycles, improved reliability, lower risk from smaller deployments, and increased developer productivity through automation.

**4. What is "Pipeline as Code" and why is it a best practice?**

Pipeline as Code defines your CI/CD pipeline in a version-controlled file (like a `Jenkinsfile` or `.gitlab-ci.yml`) that lives in the repository alongside application code. It makes pipelines reproducible, versioned, and reviewable through pull requests.

**5. What does it mean to "shift left" in a DevOps context?**

Shifting left moves testing, security, and quality checks earlier in the development lifecycle. Instead of waiting for a final QA phase, automated security scans and quality checks run in the CI stage, giving developers faster feedback.

**6. How do you handle failures in a pipeline?**

The pipeline should fail fast — stop immediately when a stage fails and notify the developer. Require a fix before new code can be merged, preventing the main branch from staying broken.

**7. What is a build artifact? Provide a few examples.**

A build artifact is the output of a build process. Examples include a Docker image, a Java `.jar` or `.war` file, a compiled C++ executable, or a zipped folder of static HTML/CSS/JS files.

**8. What are DORA metrics and why are they important?**

DORA metrics measure software delivery performance:
1. Deployment Frequency — how often you deploy to production.
2. Lead Time for Changes — how long from commit to production.
3. Mean Time to Recovery (MTTR) — how long to restore service after an incident.
4. Change Failure Rate — percentage of deployments that cause failures.

They provide a balanced view of team velocity and operational stability.

**9. What is a rollback and when would you perform one?**

A rollback reverts a system to its previous state after a failed deployment. Factors to consider: severity of the issue, user impact, and whether MTTR is lower by rolling back than by rolling forward with a hotfix.

**10. What is the "blast radius" and how do deployment strategies like canary help manage it?**

The blast radius is the potential impact a failure can have. A canary deployment significantly reduces the blast radius by exposing a new version to only a small percentage of users first.

---

## Version Control (Git)

**11. What is a webhook and how is it used to trigger a pipeline?**

A webhook is an automated HTTP callback. A Git platform like GitHub sends a webhook to a CI server like Jenkins whenever a specific event occurs (e.g., a `git push`). This tells the CI server to start the pipeline.

**12. Explain the difference between `git merge` and `git rebase`.**

- `git merge` creates a new merge commit combining two branches, preserving the full branch history.
- `git rebase` rewrites history by replaying commits from your feature branch on top of the target branch, creating a linear history. Best used on private feature branches before merging.

**13. What is a popular Git branching strategy?**

GitHub Flow: `main` is always deployable. All new work is done on a descriptive feature branch. When complete, a pull request is opened to merge it back into `main`, triggering a deployment.

**14. What is the purpose of a `.gitignore` file?**

It specifies files and directories Git should ignore — build artifacts, log files, dependencies (`node_modules`), and environment-specific files (`.env`).

**15. What's the difference between `git pull` and `git fetch`?**

- `git fetch` downloads changes from the remote but does not integrate them into your local branch.
- `git pull` is `git fetch` followed by `git merge` — downloads and immediately integrates changes.

**16. How would you revert a commit already pushed to a remote?**

Use `git revert <commit-hash>`. This creates a new commit that undoes the specified commit without rewriting history — the safe way to undo changes on a shared branch.

**17. What is the purpose of `git stash`?**

`git stash` temporarily shelves uncommitted changes, leaving a clean working directory. Useful when you need to switch branches without committing. Re-apply with `git stash pop`.

**18. How do you resolve a merge conflict?**

1. Git marks conflicting files.
2. Open the file and look for conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`).
3. Manually edit to keep the desired changes and remove markers.
4. `git add <filename>` to stage the resolved file.
5. `git commit` to complete the merge.

**19. What does `git cherry-pick` do?**

`git cherry-pick <commit-hash>` applies a specific commit from one branch onto another. Useful when you need only one or two commits from a feature branch instead of merging the entire branch.

**20. Why is `git push --force` dangerous on a shared branch?**

It overwrites the remote branch history with your local history. Team members who have pulled the branch will have their work invalidated. Only use on private feature branches, and even then, with extreme caution.

**21. What is a Git tag and when would you use it?**

A tag is a pointer to a specific commit used to mark release versions (e.g., `v1.4.2`). Unlike branches, tags don't move as new commits are added. CI/CD pipelines often trigger release deployments when a version-matching tag is pushed.

**22. What does it mean to be in a "detached HEAD" state?**

`HEAD` is pointing directly to a specific commit rather than a branch. You can look around and make experimental commits, but they won't belong to any branch and can be lost once you switch back to a branch.

---

## Jenkins

**23. What is a `Jenkinsfile`? What's the difference between Declarative and Scripted pipelines?**

A `Jenkinsfile` defines a Jenkins pipeline.
- Declarative Pipeline: Newer, more structured syntax with pre-defined structure (`pipeline`, `agent`, `stages`, `steps`). Easier to read and maintain.
- Scripted Pipeline: Older, imperative Groovy-based syntax. More flexible but more complex.

**24. What is the role of a Jenkins agent?**

An agent is a worker machine that executes jobs defined in the pipeline. Agents distribute build load, allow parallel runs, and create clean, isolated environments without overloading the main Jenkins server.

**25. What is a multi-branch pipeline and why is it useful?**

A multi-branch pipeline automatically discovers branches in your Git repository and creates a pipeline for each one containing a `Jenkinsfile`. Every feature branch is automatically built and tested without manual job configuration.

**26. What is the purpose of the `post` section in a Declarative Jenkinsfile?**

The `post` section defines actions that run at the end of a pipeline or stage — cleanup tasks, sending notifications, or different logic based on pipeline status (`always`, `success`, `failure`).

**27. What is a shared library in Jenkins?**

A shared library provides reusable Groovy code and pipeline logic shared across multiple Jenkins pipelines. It reduces code duplication and allows teams to centralize and version-control common pipeline tasks.

**28. What's the difference between a `script` block and a `sh` step in a Jenkinsfile?**

A `sh` step executes a shell command. A `script` block is used within a Declarative pipeline to allow more complex scripted pipeline logic (if/else conditions, loops, variable definitions).

---

## GitLab CI

**29. What is the purpose of the `.gitlab-ci.yml` file?**

It is the core of GitLab CI/CD — a YAML file in the root of your repository defining pipeline structure: the stages, jobs, and conditions under which they run.

**30. What is a GitLab Runner?**

A GitLab Runner is a worker process that executes CI/CD jobs. Like Jenkins agents, they separate execution from orchestration, enabling parallel runs and isolated build environments.

**31. How do you manage secrets in GitLab CI?**

Use GitLab CI/CD variables (masked) in project or group settings. For advanced needs, integrate with HashiCorp Vault or cloud secret managers. Never hardcode secrets in `.gitlab-ci.yml`.

---

## GitHub Actions

**32. In GitHub Actions, what is the difference between a workflow, a job, and a step?**

- Workflow: The entire automated process defined in a YAML file.
- Job: A set of steps that execute on the same runner. A workflow can have multiple jobs running in parallel or sequentially.
- Step: An individual task within a job — a shell command or a pre-built Action.

**33. Why might a pipeline run on a self-hosted runner instead of a cloud-provided one?**

To access resources in a private network, use custom hardware (like a GPU), comply with security policies, or reduce costs for high-volume builds.

**34. How do you pass data or artifacts from one stage to another?**

Most CI/CD tools provide an artifact mechanism. In Jenkins, use `stash` and `unstash`. In GitLab CI and GitHub Actions, define `artifacts` in one job for download by subsequent jobs.

---

## Docker

**35. What is a `Dockerfile`? Describe its basic structure.**

A `Dockerfile` is a text file with instructions for building a Docker image. It typically starts with `FROM` (base image), followed by `COPY`/`ADD` (add files), `RUN` (execute commands), `EXPOSE` (document a port), and `CMD`/`ENTRYPOINT` (specify the startup command).

**36. What is the difference between the `COPY` and `ADD` instructions?**

Both copy files into the image. `ADD` can also automatically extract tar archives and fetch remote URLs. Best practice: always use `COPY` unless you specifically need `ADD`'s extra functionality, as `COPY` is more transparent and predictable.

**37. Explain the difference between `CMD` and `ENTRYPOINT`.**

- `ENTRYPOINT` configures the primary executable for the container — not easily overridden.
- `CMD` provides default arguments for `ENTRYPOINT` — easily overridden at runtime.
A common pattern: `ENTRYPOINT` for the command (`python`) and `CMD` for the argument (`app.py`).

**38. What are Docker layers? How does layer caching speed up builds?**

Each instruction in a `Dockerfile` creates a read-only layer. Docker caches layers and reuses them if the instruction hasn't changed. Order instructions from least to most frequently changing to maximize cache hits.

**39. How can you create a smaller, more secure Docker image?**

Use multi-stage builds: compile in a larger build image, then copy only the binary into a minimal final image (`alpine`, `distroless`, `scratch`). Remove build tools and package caches in the same `RUN` layer that installs them.

**40. What's the difference between a Docker image and a Docker container?**

- An image is a read-only template containing the application and its environment — like a class blueprint.
- A container is a runnable instance of an image — like an object instance. Multiple containers can run from the same image.

**41. What is a Docker volume and why is it used?**

A Docker volume persists data generated by containers. Volumes are managed by Docker, exist outside the container's writable layer, and ensure data is not lost when a container is stopped or removed.

**42. What is the purpose of the `.dockerignore` file?**

It lists files and directories excluded from the Docker build context — preventing sensitive files from being copied into the image and speeding up builds by ignoring large files like `.git` or `node_modules`.

**43. What is the difference between `docker stop` and `docker kill`?**

`docker stop` sends `SIGTERM`, waits (default 10 seconds), then sends `SIGKILL` if the process hasn't stopped. `docker kill` sends `SIGKILL` immediately. `docker stop` is the graceful option.

**44. How do Docker volumes differ from bind mounts?**

A bind mount maps a specific host path into the container — convenient for development but tightly coupled to host filesystem layout. A named Docker volume is managed by Docker, stored under `/var/lib/docker/volumes/`, and is the recommended approach for production persistent data.

**45. What is `docker-compose` and what is it typically used for?**

`docker-compose` defines and runs multi-container Docker applications using a YAML file (`docker-compose.yml`). Primarily used for local development and testing environments.

---

## Kubernetes

**46. What is a Kubernetes Pod?**

A Pod is the smallest deployable unit in Kubernetes. It is a wrapper around one or more containers that share the same storage, network resources, and specification for how to run.

**47. What is the difference between a Deployment and a Service in Kubernetes?**

- A Deployment manages the lifecycle of Pods — ensures a specified number of replicas are running and handles rolling updates.
- A Service provides a stable network endpoint (IP and DNS name) to access a group of Pods — acts as a load balancer.

**48. How does Kubernetes handle a rolling update?**

The Deployment incrementally replaces old Pods with new ones, ensuring a minimum number of Pods are always available. It creates a new Pod, waits for it to be ready, then terminates an old one — repeating until all Pods are updated.

**49. What is `kubectl`? Name a few commands you use frequently.**

`kubectl` is the command-line tool for interacting with a Kubernetes cluster. Common commands:
- `kubectl get pods` — list pods
- `kubectl describe pod <name>` — detailed info for troubleshooting
- `kubectl logs <name>` — view container logs
- `kubectl apply -f <file>` — create or update a resource

**50. What is the purpose of a `ConfigMap` and a `Secret` in Kubernetes?**

Both decouple configuration from container images.
- `ConfigMap` stores non-confidential configuration data as key-value pairs.
- `Secret` stores sensitive data like passwords and API keys (base64-encoded).

**51. What is a Namespace in Kubernetes?**

A Namespace creates a virtual cluster inside a physical cluster. Used to isolate resources for different teams, environments (dev, staging), or projects, helping with organization and access control.

**52. What is an Ingress and what problem does it solve?**

An Ingress manages external HTTP/HTTPS access to services, acting as a reverse proxy. It defines routing rules to direct external traffic to different services based on hostname or URL path. It requires an Ingress Controller to actually implement the rules.

**53. What is the difference between a liveness, readiness, and startup probe?**

- Liveness Probe: "Is the container alive?" Failure causes a restart.
- Readiness Probe: "Is the container ready for traffic?" Failure removes the Pod from Service endpoints without restarting.
- Startup Probe: Disables liveness and readiness probes until it succeeds — protects slow-starting containers from premature kills.

**54. What is a DaemonSet? Give a use case.**

A DaemonSet ensures all (or some) nodes run a copy of a Pod. Common use cases: cluster-wide log collectors (Fluentd), monitoring agents (Prometheus Node Exporter), or network plugins.

**55. How can you limit the CPU and memory resources a Pod can consume?**

Set resource requests (guaranteed amount) and limits (maximum allowed) in the Pod spec. Exceeding the memory limit terminates the container.

**56. What is the difference between a Kubernetes Service of type `ClusterIP`, `NodePort`, and `LoadBalancer`?**

- `ClusterIP`: Internal cluster IP only — not reachable from outside.
- `NodePort`: Exposes the service on a static port on each Node's IP — reachable from outside.
- `LoadBalancer`: Provisions a cloud provider load balancer forwarding traffic to the service — standard way to expose services to the internet.

**57. What is a Helm chart and why is it useful?**

Helm is a package manager for Kubernetes. A chart bundles related Kubernetes manifests into a parameterized, versioned package — solving the problem of managing nearly-identical YAML files across environments using a single chart with different values files.

**58. What is the difference between a Deployment and a StatefulSet?**

A Deployment manages stateless pods — each is interchangeable with random names. A StatefulSet manages stateful pods that need stable, unique network identities, stable persistent storage per pod, and ordered startup/shutdown — used for databases and message queues.

**59. What does a Kubernetes `Ingress` do and why do you need an Ingress Controller?**

An Ingress resource defines HTTP/HTTPS routing rules. It is just a configuration object — it does nothing alone. An Ingress Controller (nginx-ingress, Traefik, AWS ALB Ingress Controller) is a pod that watches Ingress resources and configures an actual proxy to implement the rules.

**60. What is the role of the Kubelet?**

The Kubelet is an agent running on every node. It ensures containers described in PodSpecs are running and healthy on its node.

**61. What is the role of etcd in a Kubernetes cluster?**

etcd is the primary datastore — a consistent, highly-available key-value store that holds all cluster data including configuration, state, and metadata. It is the single source of truth for the cluster.

---

## Helm

**62. What is a Helm values file and why is it useful?**

A `values.yaml` file contains default parameters for a Helm chart. Different values files per environment (e.g., `values-dev.yaml`, `values-prod.yaml`) allow deploying the same chart with different configurations without duplicating manifests.

**63. What is the difference between `helm install` and `helm upgrade`?**

`helm install` deploys a chart for the first time, creating a new release. `helm upgrade` updates an existing release with a new chart version or new values. Use `helm upgrade --install` to perform either operation in one command.

---

## Terraform

**64. What is Terraform? How is it different from Ansible?**

Terraform is an IaC tool for provisioning infrastructure. Ansible is a configuration management tool for configuring software on that infrastructure. Terraform provisions the house; Ansible furnishes it. Terraform is declarative; Ansible is more procedural.

**65. What is the purpose of the Terraform state file?**

The state file (`terraform.tfstate`) tracks the resources Terraform manages, mapping configuration to real-world resources. It is essential for planning and applying future changes.

**66. What does `terraform plan` do?**

It creates an execution plan — compares the desired state in your configuration with the current state in the state file and shows exactly what will be created, updated, or destroyed if you run `terraform apply`.

**67. What does `terraform init` do?**

It initializes the working directory — downloads required provider plugins and sets up the backend for state file storage. Always run it first in a new Terraform project.

**68. What is a Terraform provider?**

A provider is a plugin that allows Terraform to interact with a specific API — a cloud platform like AWS, a SaaS provider like Cloudflare, or an on-premise technology like vSphere.

**69. Why is it important to keep the Terraform state file secure?**

The state file can contain sensitive data in plain text (database passwords, private keys). Store it in a secure, encrypted, access-controlled remote backend (like an S3 bucket with encryption).

---

## Ansible

**70. What is Ansible and what is it used for in a CI/CD context?**

Ansible is a configuration management tool for automating application deployment, software provisioning, and system configuration. In CI/CD, it is used in the deploy stage to configure servers and push out new application versions.

**71. What is an Ansible playbook? What is a role?**

- A playbook is a YAML file defining tasks to be executed on remote servers.
- A role is a standardized, reusable way to organize playbooks and related files (templates, handlers) to facilitate sharing and reuse.

**72. Why is Ansible considered agentless?**

Ansible doesn't require special software (an agent) installed on managed nodes. It communicates over SSH for Linux and WinRM for Windows.

**73. What is the difference between Push and Pull configuration management?**

- Push model: A central server initiates and pushes changes to managed nodes (Ansible uses this).
- Pull model: Managed nodes periodically check a central server and pull any changes (Puppet and Chef use this).

**74. What is idempotency and why does it matter for automation?**

Idempotency means running an operation multiple times produces the same result as running it once. Ansible is designed to be idempotent — running a playbook twice only makes changes the first time.

**75. What is a template in Ansible?**

A template is a file containing variables replaced with actual values when a playbook runs, using the Jinja2 templating engine. Useful for creating configuration files customized per host.

**76. In Ansible, what is an inventory file?**

An inventory file (INI or YAML format) defines the list of hosts Ansible will manage. It organizes hosts into groups and can set variables specific to those hosts or groups.

---

## Linux Administration

**77. What does the `top` command show?**

`top` shows a real-time view of running processes. Key fields: CPU%, RES (resident memory in RAM), VIRT (virtual memory allocated), and load average at the top (1, 5, 15-minute averages). Load average above the number of CPU cores means CPU saturation.

**78. What is the difference between a hard link and a symbolic link?**

A hard link is a directory entry pointing directly to an inode — both the original and the link share the same inode; deleting one doesn't remove data until all hard links are gone. A symbolic link is a special file containing a path to another file — it can cross filesystems but breaks if the target is deleted.

**79. How do you check which process is listening on a specific port?**

Use `ss -tlnp | grep :8080` or `lsof -i :8080`. `ss` is the modern replacement for `netstat`.

**80. What is the difference between `ps aux` and `ps -ef`?**

Both display all running processes. `ps aux` uses BSD syntax and shows %CPU, %MEM, VSZ, RSS, and TTY. `ps -ef` uses POSIX syntax and shows UID, PID, PPID (parent PID), and the full command.

**81. How do you find which files are consuming the most disk space?**

Use `du -sh /* 2>/dev/null | sort -rh | head -20` to sort directories by size. For large individual files: `find / -type f -size +1G 2>/dev/null`. The `df -h` command shows disk utilization per mounted filesystem.

**82. What does `chmod 755` mean?**

7 (owner) = read + write + execute, 5 (group) = read + execute, 5 (others) = read + execute. Standard for directories and executable scripts readable by everyone but writable only by the owner.

**83. How do you view and follow a log file in real time?**

Use `tail -f /var/log/syslog`. For rotating log files, use `tail -F` (follows by filename). `journalctl -fu service-name` is the systemd-native equivalent.

**84. What is a process signal and what do `SIGTERM` and `SIGKILL` do?**

Signals are inter-process communication mechanisms. `SIGTERM` (15) is a graceful termination request — the process can catch it and clean up. `SIGKILL` (9) cannot be caught or ignored — the kernel immediately terminates the process. Always try `SIGTERM` first.

**85. What is the `/proc` filesystem?**

`/proc` is a virtual filesystem (not on disk) that exposes kernel and process information as files. `/proc/cpuinfo` shows CPU details, `/proc/meminfo` shows memory statistics, and `/proc/<PID>/status` shows a specific process's state. Tools like `top` and `ps` read from `/proc` internally.

**86. How do you schedule a recurring task on Linux?**

Use `cron`. Edit the crontab with `crontab -e`. Format: `minute hour day-of-month month day-of-week command`. Example: `0 2 * * * /opt/backup.sh` runs a backup every day at 2 AM.

---

## Shell Scripting

**87. What is the difference between `$?` and `$$` in a shell script?**

`$?` holds the exit code of the last executed command (0 = success, non-zero = failure). `$$` holds the PID of the current shell process.

**88. How do you loop over a list of servers and run a command on each?**

```bash
for server in web01 web02 web03; do
  ssh "$server" "systemctl status nginx"
done
```

**89. What does `set -euo pipefail` do and why should you use it?**

- `set -e`: Exit immediately if any command returns a non-zero exit code.
- `set -u`: Treat unset variables as errors.
- `set -o pipefail`: A pipeline fails if any command in it fails.

Together they make a shell script fail fast and loudly — essential for CI pipelines.

**90. How do you pass arguments to a shell script and reference them?**

Arguments are referenced as `$1`, `$2`, `$3`, etc. `$0` is the script name. `$#` is the argument count. `$@` expands to all arguments as separate words.

**91. What is the difference between single quotes and double quotes in bash?**

Single quotes preserve every character literally — no variable expansion, no command substitution. Double quotes allow variable expansion (`$VAR`) and command substitution (`$(cmd)`).

---

## Networking Fundamentals

**92. What is the difference between TCP and UDP?**

TCP is connection-oriented: establishes a three-way handshake, guarantees ordered and reliable delivery, and retransmits lost packets. UDP is connectionless: packets are sent without a connection, with no delivery guarantee. TCP is used for web traffic and SSH. UDP is used for DNS, video streaming, and VoIP.

**93. What happens when you type a URL into a browser and press Enter?**

1. Browser checks local cache and `/etc/hosts`.
2. DNS resolver queries recursively from root to TLD to authoritative nameserver to resolve to an IP.
3. Browser opens a TCP connection (three-way handshake) to the IP on port 443.
4. TLS handshake negotiates cipher and exchanges certificates.
5. HTTP request is sent and server responds with HTML.

**94. What is NAT and why is it used?**

NAT (Network Address Translation) maps private IP addresses to a public IP before packets leave a network. It conserves IPv4 addresses and adds a layer of security by hiding internal topology. In cloud environments, instances in private subnets use NAT Gateways to reach the internet without being directly reachable from it.

**95. What is a subnet mask and what does `/24` mean?**

A subnet mask defines which portion of an IP address identifies the network vs. the host. `/24` (CIDR notation) means 24 bits are the network prefix, leaving 8 bits for hosts — 256 addresses (254 usable). `192.168.1.0/24` covers `192.168.1.1` to `192.168.1.254`.

**96. What is the purpose of SSH and how does key-based authentication work?**

SSH provides encrypted remote command execution. Key-based authentication: the user generates a key pair, places the public key in `~/.ssh/authorized_keys` on the server, keeps the private key locally. The server issues a challenge encrypted with the public key; only the private key holder can respond, proving identity without a password.

**97. What is a load balancer and what are the two main types?**

A load balancer distributes incoming traffic across multiple backend servers. Layer 4 (L4) load balancers route based on IP and port — fast but blind to HTTP content. Layer 7 (L7) load balancers understand HTTP and can route based on URL path, hostname, or headers — enabling sticky sessions, SSL termination, and path-based routing.

**98. What is the difference between a router and a switch?**

A switch operates at Layer 2 (Data Link) and forwards frames based on MAC addresses within the same network. A router operates at Layer 3 (Network) and forwards packets based on IP addresses between different networks.

---

## Monitoring & Observability

**99. What's the difference between monitoring and observability?**

Monitoring watches for pre-defined problems — it tells you _that_ something is wrong. Observability is about having enough data to debug novel, previously unseen problems — it lets you ask arbitrary questions to figure out _why_ something is wrong.

**100. What are the three pillars of observability?**

Metrics (numerical time-series data like request count or CPU usage), Logs (timestamped records of discrete events), and Traces (records of a request's journey through a distributed system showing latency at each hop).

**101. What is Prometheus? How does it collect metrics?**

Prometheus is an open-source monitoring and alerting toolkit. It uses a pull model — periodically scraping HTTP `/metrics` endpoints exposed by applications. The data is stored in its local time-series database and evaluated against alerting rules.

**102. What is Grafana used for?**

Grafana is a visualization and dashboarding platform. It connects to data sources (Prometheus, Loki, Elasticsearch, Azure Monitor) and renders time-series graphs, heatmaps, and alert panels for operational dashboards and SLO tracking.

**103. What is the ELK stack?**

ELK stands for Elasticsearch, Logstash, and Kibana. Logstash (or Filebeat) ships logs to Elasticsearch, which indexes and stores them. Kibana provides a web UI for searching, filtering, and visualizing logs.

**104. What is an SLI and an SLO?**

- SLI (Service Level Indicator): A quantitative measurement of some aspect of your service (e.g., request latency, error rate).
- SLO (Service Level Objective): The target value for an SLI over a period of time (e.g., "99.9% of requests served in under 200ms").

**105. What is distributed tracing?**

Distributed tracing tracks a single request as it flows through all the services it interacts with, providing a complete picture of the request's journey and helping pinpoint performance bottlenecks.

**106. What is a health check or liveness probe in Kubernetes?**

A liveness probe is a check the Kubelet performs periodically to determine if a container is still running. If the probe fails, the Kubelet kills and restarts the container, enabling self-healing.

---

## DevSecOps

**107. What is DevSecOps?**

DevSecOps integrates security practices into the DevOps process. The goal is to automate and embed security at every stage of the software lifecycle — from design to deployment — rather than treating it as an afterthought.

**108. What is the difference between SAST and DAST?**

- SAST (Static Application Security Testing): A "white-box" method that scans source code or binaries for vulnerabilities without running the code.
- DAST (Dynamic Application Security Testing): A "black-box" method that tests the running application by sending malicious requests.

**109. What is a CVE and how does it relate to container scanning?**

CVE (Common Vulnerabilities and Exposures) is a publicly catalogued record of a specific software vulnerability (e.g., CVE-2021-44228). Container scanning tools (Trivy, Grype, Snyk) analyze image layers, identify installed packages, and match them against CVE databases.

**110. Why use specific versions for base images (e.g., `python:3.9.1`) instead of `latest`?**

Using `latest` leads to unpredictable builds — the `latest` tag can be updated at any time with breaking changes or new vulnerabilities. Pinning to a specific version ensures deterministic, reproducible builds.

**111. What is the principle of least privilege in CI/CD?**

The pipeline's service account should only have the minimum permissions necessary — for example, only permission to push to a specific container registry or deploy to a specific Kubernetes namespace.

**112. What is a secret in Kubernetes and what is the problem with the default approach?**

A Kubernetes Secret stores sensitive data as base64-encoded values in etcd. The problem: base64 is encoding, not encryption — anyone with `kubectl get secret` access can read them. Solutions: encrypt etcd at rest, use External Secrets Operator with Vault, and enforce RBAC strictly.

**113. What is image signing and why does it matter?**

Image signing cryptographically attests that a container image was produced by a trusted source and has not been tampered with. Tools like Cosign (Sigstore) sign images. Admission controllers (Kyverno, Gatekeeper) can reject unsigned or unverified images, preventing supply chain attacks.

---

## Artifact & Package Management

**114. Why do we need an artifact repository like JFrog Artifactory or Nexus?**

To store, version, and manage binary outputs of the build process. It acts as a single source of truth for deployable units, caches external dependencies for faster builds, and manages access control and security scanning.

**115. What is semantic versioning?**

Semantic Versioning (SemVer) uses a `MAJOR.MINOR.PATCH` format (e.g., `1.2.5`). MAJOR indicates breaking changes, MINOR adds backward-compatible functionality, and PATCH is for backward-compatible bug fixes.

---

## Azure DevOps & Azure Fundamentals

**116. What is an Azure Service Connection?**

A Service Connection is a secure way to authenticate Azure DevOps to Azure RM or external services. It allows pipelines to deploy resources or access external APIs.

**117. What is the difference between Microsoft-Hosted and Self-Hosted agents?**

- Microsoft-Hosted agents are VMs managed by Microsoft — fresh, clean environment per build but limited software caching and no private VNet access.
- Self-Hosted agents are VMs or containers you manage — faster for incremental builds due to retained layers/packages, and can access private corporate networks.

**118. What is Azure Key Vault?**

Azure Key Vault securely stores and accesses secrets — API keys, passwords, certificates, and cryptographic keys. In DevOps, pipelines fetch credentials from Key Vault rather than storing them in code or plain text variables.

**119. How do you pass variables between different jobs in an Azure YAML Pipeline?**

Output variables from a script using `echo "##vso[task.setvariable variable=myVar;isOutput=true]someValue"`. Subsequent jobs can access this output variable by referencing the specific job's dependencies.

**120. What is Azure Resource Manager (ARM)?**

ARM is the deployment and management service for Azure. It provides a management layer for creating, updating, and deleting resources. ARM templates (and Bicep) use this API declaratively.
