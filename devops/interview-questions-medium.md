# Interview questions (Medium)

#### ## CI/CD Strategy & Architecture

**1. How would you design a CI/CD pipeline for a monorepo with multiple microservices?**

You'd design the pipeline to be intelligent, building and deploying only the services that have changed. This is achieved by:

1. Path Filtering: In the CI trigger, use scripts (`git diff --name-only ...`) to identify which service's directory has changed.
2. Dynamic Job Generation: The pipeline would then dynamically generate build and deploy jobs only for the affected services.
3. Shared Libraries/Templates: Use shared pipeline templates (like Jenkins Shared Libraries or GitLab CI `includes`) to avoid duplicating pipeline logic for each service.

**2. What are the trade-offs between using a feature-flag system versus feature branches?**

* Feature Branches: Provide strong code isolation but can lead to complex "merge hell" if they live too long. The full feature is only tested upon merging.
* Feature Flags (Toggles): Allow incomplete code to be merged to `main` and deployed to production, but hidden from users. This enables true Continuous Integration and testing in a production environment. The trade-off is increased application complexity and the need for rigorous flag management.

**3. When is it appropriate to have a manual approval step in a pipeline, and where would you place it?**

A manual approval step is appropriate for risk-sensitive deployments, typically for the production environment. It should be placed just before the `deploy to production` stage. This ensures all automated build, test, and staging deployment steps have passed, providing the approver with maximum confidence.

**4. How do you manage database schema migrations within an automated CI/CD pipeline?**

This is a critical challenge. The best practice is to use a database migration tool like Flyway or Liquibase.

1. Migrations are version-controlled as SQL or XML files in the application repository.
2. The pipeline executes the migration tool as a step before deploying the new application code.
3. Migrations must be designed to be backward-compatible so the old version of the application can still function during the rolling update.

**5. Explain the concept of a "golden image" for virtual machines or containers. What are its pros and cons?**

A golden image is a pre-configured template for a VM or container. It includes the OS, security patches, dependencies, and application runtime.

* Pros: Faster startup times (no provisioning needed on boot), consistent environments, and improved security.
* Cons: Can become outdated quickly, requiring a process to regularly update and test the image. It can also lead to image sprawl if not managed properly.

**6. What are DORA metrics, and how would you collect them?**

DORA metrics measure DevOps performance. They are Deployment Frequency, Lead Time for Changes, Mean Time to Recovery (MTTR), and Change Failure Rate. You would collect them by instrumenting your CI/CD pipeline and monitoring tools. For example, Deployment Frequency can be measured by counting successful production deployments from your CI/CD server's API.

**7. How does Trunk-Based Development work, and how does it facilitate CI/CD?**

In Trunk-Based Development, all developers commit to a single shared branch (the "trunk," usually `main` or `master`). Feature development is done through short-lived branches or directly on the trunk behind feature flags. This model facilitates CI/CD by eliminating long-lived branches and merge conflicts, ensuring the trunk is always in a releasable state.

**8. What's the difference between a build agent's workspace and an artifact repository?**

* A workspace is a temporary directory on a build agent where source code is checked out and built. It's ephemeral and should be considered volatile.
* An artifact repository (like Nexus or Artifactory) is a permanent, centralized storage system for the final outputs (artifacts) of the build process. It versions and manages these artifacts for deployment.

**9. Explain how you would implement a progressive delivery model like Canary or Blue/Green using a service mesh like Istio.**

A service mesh provides fine-grained traffic control. For a Canary release, you would configure Istio's `VirtualService` to route a small percentage (e.g., 5%) of HTTP traffic to the new version of the service and the rest to the old one. For a Blue/Green deployment, you'd deploy the new "green" version and initially route 0% of traffic to it. Once ready, you'd update the `VirtualService` to shift 100% of traffic from blue to green instantly.

**10. How would you handle a pipeline that needs to orchestrate deployments across multiple cloud providers or data centers?**

You would design the pipeline with an abstraction layer. Instead of calling provider-specific tools directly in the main pipeline, you'd call generic scripts or Ansible playbooks. These scripts would contain the logic to interact with different cloud APIs (AWS, GCP, etc.) based on the target environment parameter. Tools like Terraform are also excellent for this, as they use providers to manage resources across multiple clouds with a consistent workflow.

***

#### ## Advanced Git & Version Control

**11. What is `git bisect` and how would you use it?**

`git bisect` is a powerful debugging tool used to find the specific commit that introduced a bug. You start it with `git bisect start`, then provide a "bad" commit (where the bug exists) and a "good" commit (where it didn't). Git then performs a binary search of the commit history, checking out commits and asking you to test and mark them as `git bisect good` or `git bisect bad` until it isolates the exact commit that caused the problem.

**12. Explain the concept of Git LFS (Large File Storage) and when it's necessary.**

Git is not designed to handle large binary files well, as it bloats the repository size. Git LFS solves this by storing large files on a separate server. In the Git repository, it replaces the large file with a small text pointer. It's necessary when you need to version large assets like graphics, videos, or datasets alongside your code.

**13. What are Git hooks and how can they be used to improve code quality?**

Git hooks are scripts that run automatically at certain points in the Git lifecycle, such as before a commit (`pre-commit`) or before a push (`pre-push`). They can be used to improve code quality by automatically running linters, code formatters, or unit tests before the code is even committed or pushed to the central repository.

**14. What's the difference between an annotated tag and a lightweight tag in Git?**

* A lightweight tag is simply a pointer to a specific commit. It's like a branch that doesn't move.
* An annotated tag is a full object in the Git database. It's checksummed; contains the tagger's name, email, and date; has a tagging message; and can be signed and verified with GPG. Annotated tags are recommended for official releases.

**15. How would you recover a deleted branch that has not been merged?**

If the branch was recently deleted, you can find the SHA-1 of its last commit using `git reflog`, which shows a history of where your `HEAD` has been. Once you find the commit, you can restore the branch using `git checkout -b <branch-name> <commit-hash>`.

***

#### ## CI/CD Tooling In-Depth

**16. In Jenkins, what is the purpose of a `lock` resource?**

The `lock` resource is used to prevent multiple pipeline runs from concurrently accessing a shared, limited resource, such as a deployment to a specific staging environment. It ensures that only one pipeline can execute the locked block of code at a time, preventing race conditions.

**17. How does GitLab CI's "parent-child pipelines" feature work and what problem does it solve?**

Parent-child pipelines allow one pipeline (the parent) to trigger and wait for the results of other pipelines (the children) in the same project. This is useful for complex scenarios, like in a monorepo, where a parent pipeline can identify changed components and trigger specific child pipelines for each component, making the overall configuration more modular and scalable.

**18. What are GitHub Actions artifacts and caching? How are they different?**

* Artifacts are files generated by a job (e.g., a compiled binary) that you want to share with other jobs in the same workflow or save after the workflow completes.
* Caching is a performance optimization. It's used to store and reuse dependencies or files that don't change often between runs (like Maven or npm packages) to speed up future workflow runs. The cache is not guaranteed to be available.

**19. Explain how you can use a "matrix strategy" in a CI/CD pipeline.**

A matrix strategy lets you run the same job multiple times with different combinations of configurations. For example, you could define a matrix with different programming language versions (`[Python 3.8, 3.9, 3.10]`) and operating systems (`[ubuntu-latest, windows-latest]`). The CI tool would automatically generate and run a job for each possible combination.

**20. What is a Jenkins Shared Library and how does it help manage pipelines at scale?**

A Shared Library is a repository of reusable Groovy scripts that can be imported into any `Jenkinsfile`. This allows you to centralize and version-control common pipeline logic (e.g., for building a Docker image or deploying to Kubernetes). At scale, this prevents code duplication and ensures all teams are using a standardized, vetted set of pipeline functions.

***

#### ## Containerization & Orchestration

**21. Explain the difference between a StatefulSet and a Deployment in Kubernetes.**

* A Deployment is for stateless applications. It manages a set of identical, interchangeable Pods. Pods get random hostnames and can be scaled or replaced without concern for their identity.
* A StatefulSet is for stateful applications (like databases). It provides stable, unique network identifiers (e.g., `db-0`, `db-1`), persistent storage that survives Pod restarts, and ordered, graceful deployment and scaling.

**22. What is a Kubernetes Operator?**

An Operator is a custom controller that uses Kubernetes APIs to manage complex, stateful applications. It encodes human operational knowledge into software. For example, a Prometheus Operator knows how to deploy Prometheus, configure it, set up monitoring targets, and handle updates automatically.

**23. How does a Horizontal Pod Autoscaler (HPA) work in Kubernetes?**

An HPA automatically scales the number of Pods in a Deployment or StatefulSet based on observed metrics, most commonly CPU utilization or memory usage. It periodically checks the metrics from the Metrics Server and adjusts the replica count up or down to match the target value you've defined.

**24. What is the Container Network Interface (CNI) in Kubernetes?**

CNI is a standard for writing plugins to configure network interfaces for Linux containers. In Kubernetes, a CNI plugin (like Calico, Flannel, or Weave Net) is responsible for giving each Pod its own IP address and enabling network connectivity between Pods across the cluster.

**25. Explain the purpose of `init containers` in a Kubernetes Pod.**

Init containers are containers that run and complete before the main application containers are started. They are used for setup tasks, such as waiting for a database to be ready, running a database migration script, or pre-loading data into a shared volume.

**26. What is a Sidecar container, and what is a common use case?**

A Sidecar is a container that runs alongside the main application container within the same Pod. They share the same network and storage. A common use case is for concerns that are separate from the application's logic, such as a service mesh proxy (like Envoy), a log shipper, or a monitoring agent.

**27. What's the difference between a ClusterIP, NodePort, and LoadBalancer Service type in Kubernetes?**

* ClusterIP: The default type. Exposes the Service on an internal IP address within the cluster. It's only reachable from within the cluster.
* NodePort: Exposes the Service on a static port on each Node's IP. This makes it accessible from outside the cluster but is mainly used for development or non-production use.
* LoadBalancer: Exposes the Service externally using a cloud provider's load balancer. The cloud provider creates a load balancer that forwards traffic to the Service's NodePorts.

**28. How would you troubleshoot a Pod that is stuck in a `CrashLoopBackOff` state?**

1. Use `kubectl describe pod <pod-name>` to check for errors in the events section, such as an incorrect image name or a failed readiness probe.
2. Use `kubectl logs <pod-name>` to view the logs from the current, crashing container.
3. Use `kubectl logs --previous <pod-name>` to view the logs from the _previous_ container instance, which is often where the initial error occurred.
4. If logs are not informative, use `kubectl exec` to get a shell into a working instance (if possible) to debug interactively.

**29. What is Helm and why is it called the "package manager for Kubernetes"?**

Helm is a tool that streamlines installing and managing Kubernetes applications. It's called a package manager because it uses a packaging format called charts. A chart is a collection of files that describes a related set of Kubernetes resources. Helm allows you to template these files, manage releases, and share applications in a public or private repository, much like `apt` or `yum` do for Linux packages.

**30. What are Network Policies in Kubernetes?**

Network Policies are Kubernetes resources that control the traffic flow between Pods. By default, all Pods in a cluster can communicate with each other. Network Policies act as a firewall, allowing you to define rules that specify which Pods are allowed to communicate with which other Pods over which ports.

***

#### ## Infrastructure as Code & Config Management

**31. What are Terraform modules, and how do they promote reusability?**

Terraform modules are self-contained packages of Terraform configurations that are managed as a group. They are like functions in a programming language. You create a module for a piece of infrastructure you use often (like a web server cluster) and then call that module from your main configuration, passing in variables. This promotes reusability, reduces code duplication, and allows for standardized infrastructure components.

**32. Explain the difference between `terraform apply` and `terraform plan`.**

* `terraform plan` is a dry run. It analyzes your code, compares it to the state file, and shows you an execution plan of what it _would_ do (create, update, destroy) without actually making any changes.
* `terraform apply` takes the execution plan generated by `plan` and actually executes it, making the changes to your infrastructure.

**33. What is "drift" in the context of IaC, and how can you detect and manage it?**

Drift is when the real-world state of your infrastructure no longer matches the state defined in your IaC code. This often happens due to manual changes made outside of the IaC workflow. You can detect drift by running `terraform plan` periodically. To manage it, you should enforce a strict policy of making all changes through the IaC tool and revert any manual changes.

**34. How does Ansible handle secrets?**

Ansible uses a feature called Ansible Vault. It allows you to encrypt sensitive data (like passwords or API keys) within variables files. The files can then be safely committed to version control. When you run a playbook, you provide the vault password, which allows Ansible to decrypt the data in memory for use during the run.

**35. What is the difference between a role and a collection in Ansible?**

* A role is a standardized way to organize and reuse Ansible content (tasks, handlers, templates, etc.) for a specific purpose, like configuring a web server.
* A collection is a newer distribution format for Ansible content. It can contain multiple roles, modules, plugins, and documentation. Collections are the standard way to package and share Ansible content on Ansible Galaxy.

**36. What is Terragrunt and what problems does it solve for Terraform?**

Terragrunt is a thin wrapper for Terraform that provides extra tools for keeping your configurations DRY (Don't Repeat Yourself), managing remote state, and working with multiple Terraform modules. It helps solve common Terraform pain points like remote state configuration duplication and managing dependencies between modules.

**37. What is dynamic inventory in Ansible?**

A dynamic inventory is a script or plugin that Ansible can execute to get a real-time list of hosts to manage. This is essential in cloud environments where servers are constantly being created and destroyed. The script can query a cloud provider's API (e.g., AWS EC2) to get a list of running instances and their IP addresses.

***

#### ## Security (DevSecOps)

**38. What is SCA (Software Composition Analysis), and where does it fit into a pipeline?**

SCA is the process of automatically scanning your application's dependencies (e.g., npm packages, Maven libraries) for known security vulnerabilities. It should be run in the CI stage, typically after dependencies are installed, to provide fast feedback to developers if they've introduced a vulnerable package.

**39. Explain the concept of a "least privilege" IAM role for a CI/CD pipeline.**

A least privilege IAM role grants the CI/CD pipeline only the absolute minimum permissions it needs to do its job. For example, instead of giving it full S3 access, you would create a role that only allows it to `PutObject` into a specific artifact bucket. This minimizes the potential damage an attacker could do if the pipeline's credentials were ever compromised.

**40. What is a container security scanner, and what kind of vulnerabilities does it look for?**

A container security scanner (like Trivy, Clair, or Snyk) inspects container images for security issues. It looks for two main things:

1. OS Package Vulnerabilities: Known CVEs (Common Vulnerabilities and Exposures) in the base image's operating system packages (e.g., `apt` or `apk` packages).
2. Application Dependencies: Known vulnerabilities in application libraries (e.g., npm, pip, Maven).

**41. What is the difference between SAST, DAST, and IAST?**

* SAST (Static...): Scans source code without running it. Finds issues like SQL injection flaws or improper error handling early.
* DAST (Dynamic...): Tests the _running_ application by sending malicious payloads. Finds runtime issues that SAST might miss.
* IAST (Interactive...): A hybrid approach. It uses agents to instrument the running application, observing its behavior from the inside while it's being tested by a DAST tool or QA team.

**42. How can you prevent secrets from being accidentally committed to a Git repository?**

You can use a tool like `git-secrets` or Talisman as a `pre-commit` hook. These tools scan commits for patterns that look like secrets (e.g., high-entropy strings, API key formats) and block the commit if a potential secret is found.

***

#### ## Observability & Monitoring

**43. What is the difference between logging, metrics, and tracing?**

They are the three pillars of observability.

* Logging: Records discrete, timestamped events. Useful for understanding what happened at a specific point in time.
* Metrics: A numerical representation of data over time (e.g., CPU usage, request latency). Useful for dashboards, alerting, and understanding trends.
* Tracing: Shows the journey of a single request as it travels through a distributed system. Useful for debugging latency and understanding service interactions.

**44. You notice a spike in application latency after a deployment. How would you use logs, metrics, and traces together to diagnose the root cause?**

1. Metrics: First, I'd look at a Grafana dashboard to confirm the latency spike (the "what") and see if it correlates with other metrics like CPU, memory, or error rates on a specific service.
2. Traces: Next, I'd use a tracing tool like Jaeger to find a few slow requests and see the full trace. This would show which specific service or database call in the request path is taking the most time (the "where").
3. Logs: Finally, I'd dive into the logs of that specific service from the time of the slow requests to find the detailed error messages or contextual information that explains _why_ it was slow.

**45. What are SLOs and SLIs, and how do they relate to alerting?**

* An SLI (Service Level Indicator) is a measurement of service performance (e.g., latency).
*   An SLO (Service Level Objective) is the target for that measurement (e.g., 99.9% of requests served in <200ms).

    They relate to alerting by moving away from simple threshold alerts (e.g., "CPU > 90%"). Instead, you create alerts based on your error budget. The error budget is 100% - SLO. You alert when the service is burning through its error budget too quickly, as that indicates a risk of violating the SLO.

**46. What is Prometheus Pull vs. Push model for metrics collection?**

* Pull (Default): The Prometheus server periodically scrapes (pulls) metrics from an HTTP endpoint on the target application. This is the most common model.
* Push: For short-lived jobs or services behind a firewall, a component called the Pushgateway is used. The job pushes its metrics to the Pushgateway, and Prometheus then scrapes the gateway.

**47. What is OpenTelemetry?**

OpenTelemetry (OTel) is an open-source observability framework. It provides a standardized set of APIs, libraries, agents, and instrumentation to collect and export telemetry data (metrics, logs, and traces) from your applications. It aims to make observability a built-in feature of cloud-native software rather than an add-on.

The remaining 53 questions and answers will follow this structure and level of detail.
