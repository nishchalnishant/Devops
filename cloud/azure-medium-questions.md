# Azure medium questions

Of course. Here are 100 medium-difficulty Azure interview questions and answers, designed for a DevOps or SRE role with around 3 years of experience. These questions require a deeper understanding of practical application and trade-offs.

***

#### ## Azure Core Concepts & Governance

**### 1. Compare and contrast Azure Policy and Azure RBAC.**

* Azure RBAC (Role-Based Access Control) focuses on who can do what. It's about granting permissions to users, groups, or service principals to perform actions like creating or deleting resources.
* Azure Policy focuses on what conditions resources must meet. It's about enforcing rules and compliance on the properties of resources, such as requiring specific tags or disallowing public IPs on VMs. They work together: RBAC grants permissions to deploy, while Policy ensures the deployed resource is compliant.

**### 2. What is the difference between a custom RBAC role and Azure Policy?**

You would create a custom RBAC role when you need a specific set of permissions that isn't covered by the built-in roles (e.g., a role that can restart VMs but not delete them). You use Azure Policy when you need to enforce rules on the resources themselves, regardless of who is creating them.

**### 3. What is an Azure Blueprint and how does it differ from a set of ARM templates?**

An Azure Blueprint is a package that bundles together ARM templates, RBAC assignments, and Policy assignments into a single, repeatable definition. While ARM templates deploy resources, a Blueprint orchestrates the deployment of a fully governed environment, including the ongoing governance controls (policies and roles). A key difference is that the relationship between the Blueprint definition and its assignments is preserved, allowing for easier updates and tracking of governed environments.

**### 4. How would you enforce a tagging strategy across your organization's Azure subscriptions?**

The best way is to use Azure Policy. You would create a policy initiative (a collection of policies) that includes:

1. A policy with the `modify` effect to automatically add default tags (like `Environment=Production`) if they are missing.
2. A policy with the `deny` effect to prevent the creation of resources that are missing mandatory tags (like `CostCenter`).
3. You would then assign this initiative at a high-level scope, like a Management Group, to ensure it applies to all subscriptions.

**### 5. What is a "break-glass" account and what is a best practice for managing it in Azure?**

A "break-glass" account is a highly privileged, emergency-use-only account (e.g., Global Administrator) that is kept separate from daily-use accounts.

* Best Practice: The account should be a cloud-only account (not synced from on-prem), have a very long and complex password stored securely (e.g., in a physical safe), and have Multi-Factor Authentication (MFA) enabled. Its usage should trigger high-priority alerts to the security team.

**### 6. Explain the purpose of Azure Resource Locks.**

Resource Locks are used to prevent accidental deletion or modification of critical Azure resources. There are two types:

* `CanNotDelete`: Authorized users can still read and modify the resource, but they cannot delete it.
* `ReadOnly`: Authorized users can only read the resource; they cannot delete or update it.

**### 7. How can you get a consolidated view of costs from multiple subscriptions belonging to different departments?**

The best way is to use Management Groups to structure your subscriptions according to your organizational hierarchy (e.g., by department). You can then view cost analysis and set budgets at the management group scope in Azure Cost Management. Using a consistent tagging strategy (e.g., a `Department` tag) is also crucial for filtering and grouping costs.

**### 8. What is the principle of least privilege in the context of Azure?**

It means that any user, application, or service principal should only be granted the absolute minimum permissions required to perform its specific function, for the shortest possible time. In Azure, this is implemented by assigning highly specific roles (or creating custom roles) at the narrowest possible scope (e.g., at a Resource Group level instead of the Subscription level).

**### 9. What is Azure AD Privileged Identity Management (PIM)?**

PIM is an Azure AD service that enables you to manage, control, and monitor access to important resources. It provides just-in-time (JIT) privileged access, meaning users must request to activate their role for a limited time. It helps mitigate the risks of excessive permissions by requiring an approval workflow and providing a full audit history of all activations.

**### 10. You need to provide a third-party vendor with access to a specific resource group for a limited time. What is the most secure way to do this?**

Use Azure AD B2B (Business-to-Business) to invite the vendor as a guest user into your Azure AD tenant. Then, use Azure PIM (Privileged Identity Management) to make them eligible for a specific role (e.g., "Contributor") on the specific resource group. They can then activate this role on-demand for a set period, and their access will automatically expire.

***

#### ## Azure Compute & Serverless

**### 11. What are the key differences between Azure App Service and Service Fabric?**

* Azure App Service: A fully managed PaaS for web apps and APIs. It's an opinionated platform optimized for simplicity and rapid development. You don't manage the underlying OS or VMs.
* Azure Service Fabric: A distributed systems platform for building complex, scalable, and reliable microservices. It gives you much more control over the underlying infrastructure and is suitable for both stateless and stateful services. It's more complex to manage than App Service.

**### 12. A web app in an App Service needs to securely access a SQL database that is not exposed to the public internet. How would you achieve this?**

The best practice is to use VNet Integration for the App Service and a Private Endpoint for the SQL database.

1. Enable VNet Integration on the App Service, which allows it to make outbound calls into a specified subnet in your Virtual Network.
2. Create a Private Endpoint for the Azure SQL database, which gives the database a private IP address within a different subnet of the same VNet.
3. The App Service can then connect to the SQL database using its private IP address, and all traffic remains on the secure Azure backbone network.

**### 13. What is the difference between the Consumption and Premium plans for Azure Functions?**

* Consumption Plan: Truly serverless. It automatically scales based on events, and you only pay for the exact time your code runs. It can suffer from "cold starts" where the first request after a period of inactivity might have higher latency.
* Premium Plan: Provides "pre-warmed" instances that are always on, eliminating cold starts. It offers more powerful compute instances and VNet integration. You pay for the reserved instances, not just the execution time. It's a hybrid between serverless and dedicated hosting.

**### 14. What is the purpose of the `host.json` file in Azure Functions?**

The `host.json` file contains global configuration options that affect all functions in a function app. It's where you configure things like logging, application-level binding settings (like queue message batch sizes), and health monitoring.

**### 15. How do you manage application settings and connection strings for an Azure App Service?**

They should be managed as Application Settings and Connection Strings in the App Service's configuration blade in the Azure Portal or defined in your IaC template. These are injected as environment variables into the application at runtime. This practice avoids storing secrets in your source code. For higher security, these settings can reference secrets stored in Azure Key Vault.

**### 16. What is the Kudu console in Azure App Service?**

Kudu is the advanced tools engine behind an App Service. It provides a web-based interface that gives you access to a debug console, process explorer, deployment logs, and the underlying file system of your App Service, which is invaluable for troubleshooting.

**### 17. How does autoscaling work in a Virtual Machine Scale Set (VMSS)?**

You configure autoscaling rules based on metrics (e.g., "if average CPU utilization is > 75% for 5 minutes, add one VM instance") or on a schedule (e.g., "scale up to 10 instances every weekday at 9 AM and scale down to 2 instances at 5 PM").

**### 18. You need to run a custom script on a VM every time it is created. How would you do this?**

You would use the Custom Script Extension. This is a VM extension that downloads and executes a script on an Azure VM after it is provisioned. You can specify the script file (e.g., from Azure Storage) and any arguments in your ARM/Bicep template or via the Azure CLI.

**### 19. What are the trade-offs of using Windows vs. Linux VMs on Azure?**

* Linux VMs: Generally cheaper, have a smaller footprint, and are the standard for open-source applications and containers. They are managed via SSH.
* Windows VMs: Required for applications that depend on the Windows ecosystem (e.g., .NET Framework, IIS, SQL Server). They have licensing costs included in the VM price (unless you use Hybrid Benefit) and are managed via RDP.

**### 20. What is a "cold start" in the context of serverless functions, and how can you mitigate it?**

A cold start is the latency associated with the first request to a function that hasn't been used recently. The platform needs to allocate a server, load your code, and initialize the runtime. You can mitigate this by:

1. Using an Azure Functions Premium Plan, which keeps instances pre-warmed and ready.
2. Keeping the function package size small and minimizing dependencies.
3. For Consumption plans, you can have a simple timer-triggered function that "pings" your main HTTP function every few minutes to keep it warm, though this is a workaround and has a small cost.

***

#### ## Azure Networking & Security

**### 21. Explain the purpose of an Application Security Group (ASG) and how it differs from an NSG.**

An NSG (Network Security Group) filters traffic based on IP addresses and ports (Layer 4). An ASG (Application Security Group) is a logical grouping tag. You can apply an ASG tag to VMs (e.g., `asg-webservers`). Then, in your NSG rules, you can specify the ASG as the source or destination instead of explicit IP addresses. This simplifies rule management, as you don't need to update IP addresses in the NSG every time you add or remove a VM from the group.

**### 22. You have a hub-spoke network topology. How do you ensure that all traffic from the spokes to the internet is routed through a central firewall in the hub?**

You would use User-Defined Routes (UDRs).

1. Place a central firewall appliance (like Azure Firewall) in the hub VNet.
2. On each subnet in the spoke VNets, create a Route Table.
3. In the Route Table, add a UDR for the address prefix `0.0.0.0/0` (representing all internet-bound traffic).
4. Set the "next hop type" for this route to "Virtual Appliance" and provide the private IP address of the firewall in the hub VNet.

**### 23. What is Azure Private Link, and what problem does it solve?**

Azure Private Link is a service that allows you to access Azure PaaS services (like Azure Storage, SQL Database) and your own services over a Private Endpoint in your VNet. It solves the problem of data exfiltration and secure connectivity by essentially bringing the PaaS service into your private network, so all traffic flows over the Microsoft backbone and is never exposed to the public internet.

**### 24. What is the Web Application Firewall (WAF) in Azure?**

The WAF is a feature of Azure Application Gateway and Azure Front Door. It provides centralized protection for your web applications from common exploits and vulnerabilities, such as SQL injection and cross-site scripting. It uses rules from the Open Web Application Security Project (OWASP) core rule sets.

**### 25. What is the difference between Azure Front Door and Application Gateway?**

* Application Gateway: A regional Layer 7 load balancer. It's designed to manage traffic to web applications within a single region.
* Azure Front Door: A global Layer 7 load balancer and web accelerator. It operates at the edge of Microsoft's global network and uses anycast to route users to the closest and best-performing application backend anywhere in the world. It's ideal for globally distributed applications.

**### 26. How would you provide DNS resolution between two peered VNets?**

By default, peered VNets don't automatically resolve DNS names. You need to either:

1. Use Azure Private DNS Zones. You create a private zone (e.g., `internal.contoso.com`), link it to both VNets, and Azure will handle the automatic registration and resolution of VM hostnames. This is the modern, recommended approach.
2. Deploy your own custom DNS servers in a central VNet and configure all other VNets to use them for DNS resolution.

**### 27. What is Azure DDoS Protection?**

Azure DDoS Protection is a service that protects your Azure resources from Distributed Denial of Service (DDoS) attacks. The Basic tier is enabled by default, but the Standard tier provides advanced mitigation capabilities, attack analytics, and alerting specifically tailored to your VNet resources.

**### 28. What is Azure Key Vault?**

Azure Key Vault is a secure cloud service for storing and managing secrets, encryption keys, and TLS/SSL certificates. It provides hardware security modules (HSMs) for protection and allows you to tightly control and audit access to your secrets.

**### 29. A developer needs to access a secret from Key Vault in their web app. What is the most secure way to grant this access?**

Use a Managed Identity.

1. Enable a system-assigned or user-assigned Managed Identity on the Azure resource (e.g., the App Service or VM).
2. In the Key Vault's Access Policies, grant that Managed Identity's service principal `get` permissions for secrets.
3. The application code can then use the Azure Identity SDK to authenticate to Key Vault using its managed identity token and retrieve the secret. This completely removes the need for storing any connection strings or credentials in the application's configuration.

**### 30. What is Just-In-Time (JIT) VM Access in Microsoft Defender for Cloud?**

JIT VM Access is a security feature that locks down inbound traffic to your Azure VMs by closing management ports (like RDP and SSH) by default. When a user needs access, they make a request through Defender for Cloud. If they are authorized (via RBAC), JIT creates a temporary NSG rule to open the port for a specific source IP address for a limited amount of time. This significantly reduces the attack surface of your VMs.

***

#### ## Azure Storage & Data

**### 31. What are the performance trade-offs between Standard and Premium SSDs for VM disks?**

* Standard SSDs: A cost-effective option for workloads that require consistent performance at lower IOPS/throughput, such as web servers or lightly used applications.
* Premium SSDs: High-performance, low-latency disks for I/O-intensive workloads like production databases (SQL Server, Oracle) and big data applications. They provide provisioned IOPS and throughput, guaranteeing performance.

**### 32. What is Blob Storage Lifecycle Management?**

It's a rule-based policy you can create in a storage account to automate the process of moving blobs between access tiers (e.g., "move any blob that hasn't been accessed in 30 days from the Hot tier to the Cool tier") or deleting old blobs. This is a key tool for optimizing storage costs.

**### 33. What is Azure Blob object replication?**

Object replication is a feature that asynchronously copies blobs between a source and a destination storage account. This is different from GRS because it's configured at the container level, giving you more granular control. It's often used to minimize latency for read requests by keeping data closer to users in different regions.

**### 34. How would you enable cross-origin resource sharing (CORS) for a storage account?**

You would configure a CORS rule in the storage account's settings. In the rule, you specify the allowed origins (domains), the allowed HTTP methods (GET, PUT, etc.), and other headers. This tells the storage account to include the necessary CORS headers in its responses, allowing a web application running on a different domain to make requests to your storage account.

**### 35. You need to upload a 2TB data file to Azure Blob Storage. What tool would you use for the most reliable transfer?**

For very large files, the best tool is AzCopy. It's a command-line utility optimized for high-performance, resumable data transfers. It can handle large files by splitting them into chunks and uploading them in parallel. If the transfer is interrupted, it can resume from where it left off.

***

#### ## Azure DevOps & CI/CD (Continued)

**### 36. What is the difference between a build pipeline and a release pipeline in the classic editor of Azure DevOps?**

* Build Pipeline (CI): Its primary purpose is to produce an artifact. It triggers from a code commit, compiles the code, runs tests, and publishes the resulting artifact (e.g., a `.zip` file or Docker image).
*   Release Pipeline (CD): Its primary purpose is to deploy an artifact to an environment. It triggers upon the creation of a new build artifact and orchestrates the deployment through various stages (e.g., Dev, Staging, Prod), often including approval gates.

    In modern YAML, these two concepts are combined into a single multi-stage pipeline.

**### 37. What are pipeline decorators?**

Pipeline decorators are a way to automatically inject steps into all jobs in an organization. For example, a security team could use a decorator to automatically add a vulnerability scanning step to the beginning or end of every single CI job without developers having to add it to their YAML files manually.

**### 38. How would you design a pipeline that deploys to multiple regions simultaneously?**

In your YAML pipeline, you would define a single `stage` for production deployment. Within that stage, you would define multiple `jobs`, one for each region (e.g., `deploy-eastus`, `deploy-westus`). By default, jobs within a stage run in parallel. Each job would have its own steps to deploy the application to its specific regional infrastructure.

**### 39. What is the purpose of an agent pool?**

An agent pool is a collection of CI/CD agents. When you run a pipeline, you specify which pool it should use. This allows you to create separate pools of agents for different purposes, such as a pool of Windows agents with Visual Studio for .NET builds and a separate pool of Linux agents for Docker builds.

**### 40. What are pipeline triggers and how would you configure a pipeline to only run on pull requests to the `main` branch?**

Triggers define what causes a pipeline to run. In your `azure-pipelines.yml`, you would configure the trigger like this:

YAML

```
trigger: none # Disable CI triggers on pushes

pr:
  branches:
    include:
    - main
  paths:
    include:
    - 'src/*' # Only trigger if files in the 'src' folder change
```

This configuration disables the normal CI trigger for pushes and explicitly enables a pull request trigger that only fires for PRs targeting the `main` branch.

***

#### ## Containers on Azure (AKS & ACR) (Continued)

**### 41. What are the trade-offs between using Azure CNI and Kubenet for an AKS cluster?**

* Kubenet (Basic): Simpler to configure. Nodes get an IP from the VNet, but Pods get IPs from a separate, logically different address space. This requires NAT (Network Address Translation) for pods to communicate with resources outside the cluster, which adds a slight overhead. It conserves VNet IP address space.
* Azure CNI (Advanced): More performant. Every Pod gets a full IP address from the VNet subnet, making them directly routable. This eliminates the need for NAT. The downside is that it consumes a large number of IP addresses from your VNet, which requires careful IP planning.

**### 42. How does an Ingress Controller work in AKS?**

An Ingress Controller (like NGINX or AGIC) is a piece of software running inside your AKS cluster that fulfills the routing rules defined in your `Ingress` resources.

1. You create a Kubernetes `Service` of type `LoadBalancer`, which provisions an external Azure Load Balancer with a public IP. This Load Balancer directs traffic to the Ingress Controller pods.
2. You then create `Ingress` resources that define rules like "requests for `app.contoso.com/api` should go to the `api-service`."
3. The Ingress Controller watches for these Ingress resources and automatically configures its internal proxy (e.g., NGINX) to route traffic accordingly.

**### 43. What is the AKS Cluster Autoscaler, and how does it decide when to add or remove nodes?**

The Cluster Autoscaler is a Kubernetes component that automatically adjusts the number of nodes in your cluster.

* Scale-up: It checks for Pods in a `Pending` state that cannot be scheduled due to insufficient CPU or memory. If it finds such Pods, it will add a new node to the node pool.
* Scale-down: It periodically checks for nodes that are underutilized for a certain period. If it finds a node where all of its Pods could be rescheduled to other nodes, it will cordon and drain the node, then remove it from the scale set.

**### 44. You need to provide persistent storage for a stateful application in AKS. What are your options?**

1. Azure Disk: The most common option. You create a `PersistentVolumeClaim` with a `StorageClass` of `managed-premium`. This dynamically provisions an Azure Premium SSD that is mounted to a single Pod. It's `ReadWriteOnce` (RWO).
2. Azure Files: Used when you need storage that can be mounted by multiple Pods simultaneously (`ReadWriteMany` - RWX). You create a `PersistentVolumeClaim` with an Azure Files `StorageClass`.
3. Container Native Storage (CNS): For high-performance stateful applications like databases, you can use a CNS solution like Portworx or Rook/Ceph, which you install into the cluster.

**### 45. What is the Azure Key Vault Provider for Secrets Store CSI Driver?**

This is the modern, recommended way to integrate AKS with Key Vault. It allows you to mount secrets, keys, and certificates from Key Vault directly into your Pods as a volume. The application can then read them directly from the file system. This is more secure than syncing secrets as native Kubernetes `Secret` objects and provides a rotation mechanism.



Of course. Here is the final set of 55 medium-difficulty questions and answers to complete your list of 100, continuing from number 45.

***

#### ## Azure DevOps & CI/CD (Continued)

**### 46. What is a YAML template in Azure Pipelines and why is it useful?**

A YAML template allows you to define reusable content, logic, and parameters that can be shared across multiple pipelines. This is useful for standardizing stages, jobs, or steps (like a security scan or a deployment process), which reduces code duplication and makes pipelines easier to manage at scale.

**### 47. What is the difference between a `stage`, a `job`, and a `step` in a YAML pipeline?**

* Stage: The highest-level division, representing a major phase like `Build`, `Test`, or `DeployProd`. Stages run sequentially by default.
* Job: A collection of steps that run on a single agent. Jobs within a stage run in parallel by default.
* Step: The smallest unit of work, like a script command or a pre-defined task. Steps within a job run sequentially.

**### 48. How would you implement a manual approval gate before a production deployment in a YAML pipeline?**

You would define an environment in Azure DevOps and add an approval check to it. In your YAML pipeline, you would create a `deployment` job that targets this environment. The pipeline will automatically pause before executing this job and wait for the required users to manually approve the deployment in the Azure DevOps UI.

**### 49. What is the purpose of an agent pool and when would you create a new one?**

An agent pool is a collection of agents that can be targeted by your pipelines. You would create a new agent pool to isolate agents for specific purposes. For example, you might have one pool of general-purpose Linux agents and a separate, more secure pool of self-hosted agents that have access to a private VNet for production deployments.

**### 50. How do you pass variables from one stage to a subsequent stage in a multi-stage pipeline?**

You need to declare the variable as an output variable from a specific job. In the first stage's job, you use a special logging command to set the variable (e.g., `echo "##vso[task.setvariable variable=myVar;isOutput=true]someValue"`). In the second stage, you declare a dependency on the first stage's job and can then access the variable using the syntax `$[stageDependencies.FirstStage.FirstJob.outputs['myVar']]`.

**### 51. What is a "deployment strategy" in an Azure Pipelines deployment job?**

A deployment strategy defines how the deployment is rolled out. Azure Pipelines provides built-in strategies like:

* `runOnce`: The default, runs the deployment steps once.
* `canary`: Deploys the new version to a small subset of targets, waits for a manual intervention or a delay, and then completes the rollout.
* `rolling`: Deploys the new version to a subset of targets (e.g., 20% at a time) in a rolling fashion.

**### 52. How do you secure a service connection in Azure DevOps?**

You should use pipeline permissions and approvals & checks. Restrict which pipelines are allowed to use a specific service connection. For production-critical service connections, add an approval check that requires a manual sign-off from a specific user or group before a pipeline can use it to deploy.

**### 53. What is the difference between `script`, `bash`, and `pwsh` tasks in a YAML pipeline?**

* `script`: A generic shortcut that runs a single line command. It uses the default shell of the agent (`bash` on Linux, `cmd` on Windows).
* `bash`: Explicitly runs a script using the Bash shell. It provides more control over options and error handling. It's the standard for Linux agents.
* `pwsh`: Runs a script using PowerShell Core. It's cross-platform and is useful if you want to run the same script logic on both Windows and Linux agents.

**### 54. What are pipeline artifacts and how are they used?**

Pipeline artifacts are the files or packages that are the output of your build (CI) process. You use the `PublishPipelineArtifact` task to upload these files from the agent to Azure Pipelines storage. A later stage in the pipeline (like a deployment stage) can then use the `DownloadPipelineArtifact` task to download these files to the agent for deployment.

**### 55. How can you trigger a pipeline upon the completion of another pipeline?**

You use a pipeline resource trigger. In your `azure-pipelines.yml` file, you define a `resources` block that specifies the source pipeline. The `trigger` block can then be configured to start your pipeline whenever a run of the source pipeline completes. This is useful for chaining related pipelines together.

***

#### ## Containers on Azure (AKS & ACR) (Continued)

**### 56. What is a node pool in AKS and why would you use multiple node pools?**

A node pool is a group of nodes within an AKS cluster that have the same configuration (VM size, OS, etc.). You would use multiple node pools to support different types of workloads. For example, you could have:

* A default node pool with general-purpose VMs for most applications.
* A second node pool with GPU-enabled VMs for machine learning workloads.
* A third node pool using Spot VMs for cost-effective, interruptible batch jobs.

**### 57. What is Azure AD-integrated authentication for AKS?**

This feature integrates your AKS cluster's authentication with Azure Active Directory. It allows you to use your standard Azure AD users and groups to control access to the Kubernetes API using Kubernetes RBAC. This centralizes identity management and avoids having to manage separate cluster credentials.

**### 58. How do you perform a node image upgrade in an AKS cluster?**

You run the command `az aks nodepool upgrade --name <nodepool-name> ...`. AKS performs a cordon and drain operation. It isolates one node at a time, safely drains the workloads to other nodes, upgrades the node to the new image version, and then uncordons it before moving to the next node. This ensures the upgrade happens with zero application downtime.

**### 59. What is a Pod Disruption Budget (PDB) and why is it important for AKS upgrades?**

A Pod Disruption Budget (PDB) is a Kubernetes object that limits the number of pods of a specific application that can be voluntarily disrupted at one time. It's critical for AKS upgrades and other maintenance operations. By setting a PDB, you tell Kubernetes "you can drain my nodes, but please ensure at least 80% of my web server pods are running at all times." This prevents the upgrade process from taking down your entire application.

**### 60. What is ACR Geo-replication?**

Geo-replication is a feature of ACR Premium that allows you to replicate your container registry to multiple Azure regions. This provides two key benefits:

1. Network-close deployments: You can pull images from a local, replicated registry in the same region as your AKS cluster, which is much faster.
2. Disaster Recovery: It provides redundancy for your images if one Azure region becomes unavailable.

**### 61. What is AKS Pod Identity and when would you use it?**

AKS Pod Identity allows you to assign an Azure Managed Identity to a specific pod or application running in AKS. The application can then use this identity to access other Azure resources (like Key Vault or Blob Storage) without needing any credentials or connection strings stored as Kubernetes secrets. It's a more granular and secure alternative to assigning identities at the node level.

**### 62. What is the AKS Ingress Controller with Application Gateway (AGIC)?**

AGIC is an Ingress Controller that uses a dedicated Azure Application Gateway to expose your AKS services to the internet. Instead of provisioning an Azure Load Balancer, AGIC configures the Application Gateway directly based on the `Ingress` resources in your cluster. This allows you to use the advanced Layer 7 features of the Application Gateway, like its Web Application Firewall (WAF), natively with AKS.

**### 63. How can you control egress (outbound) traffic from your AKS cluster?**

You can use a feature called Outbound Type `UserDefinedRouting` (UDR). This allows you to route all outbound traffic from your AKS cluster through a dedicated network appliance, such as an Azure Firewall. This gives you a single point to monitor, inspect, and apply security rules to all traffic leaving your cluster.

**### 64. What is the difference between a ClusterIP, NodePort, and LoadBalancer service in AKS?**

* ClusterIP: Exposes the service on an internal IP only. It's only reachable from within the cluster. (Default)
* NodePort: Exposes the service on a static port on each worker node's IP. Used for development or when you need to expose a service without a cloud load balancer.
* LoadBalancer: Exposes the service externally using an Azure Load Balancer. This is the standard way to expose a production service to the internet.

**### 65. What is ACR Tasks used for?**

ACR Tasks is a suite of features within Azure Container Registry for building and maintaining container images in the cloud. You can use it for:

* Quick, one-off builds using `az acr build`.
* Automated builds triggered by Git commits.
* Automated patching of base images; it can detect when a base image (like `ubuntu:20.04`) is updated and automatically trigger a rebuild of your application image.

***

#### ## Azure Monitoring & SRE Practices

**### 66. What are the key components of Azure Monitor?**

Azure Monitor is a unified platform consisting of Metrics, Logs (Log Analytics), Traces (Application Insights), and Alerts. It collects data from all your Azure resources and provides a suite of tools to analyze, visualize, and act on that data.

**### 67. How would you write a KQL query to find the top 10 most frequent errors in your application logs over the last 24 hours?**

You would query the `requests` or `exceptions` table in your Application Insights or Log Analytics workspace.

Code snippet

```
// For failed requests
requests
| where timestamp > ago(24h)
| where success == false
| summarize count() by resultCode
| top 10 by count_

// For exceptions
exceptions
| where timestamp > ago(24h)
| summarize count() by problemId
| top 10 by count_
```

**### 68. What is the Application Map in Application Insights?**

The Application Map is a visual tool that automatically discovers and maps the topology of your distributed application. It shows the components of your application, their dependencies, and key performance indicators like request volume, duration, and failure rates. It's an excellent tool for identifying performance bottlenecks and understanding failure points.

**### 69. What is a "log-based metric" in Azure Monitor?**

A log-based metric is a metric that is created by running a KQL query against your log data on a schedule. For example, if your application logs a custom event for every user login, you could create a log-based metric that runs a query every minute to count these events, allowing you to plot the user login rate as a metric and create alerts on it.

**### 70. How would you design an alert rule to notify you if your web app's availability drops below 99.5% over a 1-hour period?**

You would create a metric alert rule in Azure Monitor.

* Resource: Target your Application Insights resource.
* Condition: Use the `Availability` metric. Set the aggregation to `Average`, the operator to `LessThan`, and the threshold to `99.5`.
* Evaluation: Set the lookback period to `1 hour` and the frequency to `5 minutes`.
* Action Group: Link an action group to send a notification (e.g., email or SMS) when the alert is triggered.

**### 71. What is Azure Monitor for Containers?**

It's a feature designed to monitor the performance of container workloads deployed to Azure Kubernetes Service (AKS). It collects memory and processor metrics from controllers, nodes, and containers. It also collects container logs and provides visualizations of the cluster's health and performance.

**### 72. What are Azure Workbooks?**

Azure Workbooks provide a flexible canvas for data analysis and the creation of rich visual reports within the Azure portal. They allow you to combine text, KQL queries, metrics, and parameters into a single interactive document. They are often used to create detailed troubleshooting guides or service health dashboards.

**### 73. Explain the purpose of a "Correlation ID" in the context of distributed systems and observability.**

A Correlation ID is a unique identifier that is passed through every service involved in processing a single request. In your logs, you would include this ID in every log message. This allows you to use a tool like Log Analytics to easily filter and see all the logs from all the different services that are related to that one specific user request, which is invaluable for debugging. Application Insights handles this automatically with its `operation_Id`.

**### 74. What is the difference between a diagnostic setting and the Azure Monitor Agent?**

* A Diagnostic Setting is a configuration on an Azure resource itself that tells it to push its platform logs and metrics to a destination (like a Log Analytics Workspace). It's primarily for Azure platform telemetry.
* The Azure Monitor Agent (AMA) is an agent that you install inside a virtual machine (or on-premise server). It's used to pull more detailed guest OS performance data, events, and logs from inside the VM.

**### 75. How can you monitor your CI/CD pipeline's health and performance?**

While Azure DevOps has its own analytics, you can achieve deeper monitoring by:

1. Sending pipeline logs to a Log Analytics Workspace using a custom script and the Azure CLI.
2. Using a webhook to send pipeline events to an Azure Function, which can then parse the data and create custom metrics in Azure Monitor for things like pipeline duration, failure rate per stage, etc.
3. This allows you to create dashboards and alerts on your DevOps processes just like you would for your production applications.

***

#### ## Infrastructure as Code (IaC) (Continued)

**### 76. What are Bicep Modules and how do they help organize your code?**

Bicep Modules are self-contained Bicep files that can be called from another Bicep file. They are the primary way to break down a complex deployment into smaller, more manageable, and reusable components. For example, you could have a module to deploy a virtual network and another to deploy a storage account, and then compose them together in a main `main.bicep` file.

**### 77. What is the `what-if` operation in Bicep/ARM deployments used for?**

The `what-if` operation is a "dry run" or "preview" of your deployment. It compares the state defined in your IaC file with the current state of your resources in Azure and shows you a detailed report of what resources will be created, updated, or deleted if you were to proceed with the deployment. It's the equivalent of `terraform plan`.

**### 78. How do you handle secrets when deploying infrastructure with Bicep?**

You should never store secrets directly in your Bicep files or parameter files. The best practice is to store the secret in Azure Key Vault. Then, in your Bicep file, you can create a parameter for the secret, but in the deployment pipeline, you fetch the secret from Key Vault at runtime and pass it to the Bicep deployment command.

**### 79. What is a deployment script resource in Bicep/ARM?**

A deployment script (`Microsoft.Resources/deploymentScripts`) is a special resource that allows you to run a PowerShell or Azure CLI script as part of your deployment. This is useful for performing custom actions that can't be done with native Bicep/ARM resources, such as creating an Active Directory group or calling an external API.

**### 80. How would you structure a large Bicep project for multiple environments (Dev, QA, Prod)?**

1. Use Modules: Decompose your infrastructure into reusable modules (e.g., `vnet.bicep`, `appservice.bicep`).
2. Environment-Specific Parameter Files: Create separate parameter files for each environment (e.g., `dev.bicepparam`, `prod.bicepparam`). These files will contain the environment-specific values like VM sizes, resource names, and network ranges.
3. Main Deployment File: Have a main Bicep file (`main.bicep`) that calls all the necessary modules.
4. CI/CD Pipeline: Your deployment pipeline would accept an environment name as a parameter and then execute the deployment using the `main.bicep` file along with the corresponding parameter file (e.g., `az deployment group create --template-file main.bicep --parameters dev.bicepparam`).

***

#### ## Azure Security & Identity

**### 81. What is Microsoft Defender for Cloud?**

Microsoft Defender for Cloud is a comprehensive cloud security posture management (CSPM) and cloud workload protection platform (CWPP). It provides a "Secure Score" to assess your security posture, gives recommendations to harden your resources, and offers threat protection for your VMs, containers, databases, and other services.

**### 82. What is the difference between a system-assigned and a user-assigned Managed Identity?**

* System-Assigned: Tied to a specific Azure resource (like a VM or App Service). Its lifecycle is a part of that resource; if you delete the resource, the identity is also deleted. It can't be shared.
* User-Assigned: A standalone Azure resource. You can create it independently and assign it to one or more Azure resources. This is useful when you want to grant a set of permissions to a group of resources or when you need the identity's lifecycle to be managed separately.

**### 83. What is Azure Sentinel?**

Azure Sentinel is a cloud-native SIEM (Security Information and Event Management) and SOAR (Security Orchestration, Automation, and Response) solution. It collects security data from across your entire enterprise (Azure, M365, on-prem), uses AI to detect threats, and allows you to automate responses to security incidents using playbooks.

**### 84. How does Azure AD Conditional Access work?**

Conditional Access is the tool used by Azure AD to bring signals together, to make decisions, and to enforce organizational policies. It acts as a gatekeeper for authentication. You can create policies like: "To access the Azure Portal, a user must be coming from a compliant device AND must use MFA, but if they are on the corporate network, MFA is not required."

**### 85. What is the purpose of Azure Private DNS zones?**

Azure Private DNS Zones provide a reliable and secure DNS service for your virtual networks. They allow you to use your own custom domain names rather than the Azure-provided names, and they work across peered VNets without you having to manage custom DNS servers.

**### 86. How would you prevent a storage account key from ever being used to access data, forcing all access through RBAC?**

In the storage account's configuration, you can set the `allowSharedKeyAccess` property to `false`. This completely disables access via shared keys and SAS tokens that use the shared key. All access must then be authenticated through Azure AD and authorized using Azure RBAC roles (like "Storage Blob Data Reader").

**### 87. What is Azure Application Proxy?**

Azure Application Proxy is a feature of Azure AD that allows you to publish on-premises web applications so they can be securely accessed by remote users. It acts as a reverse proxy, allowing users to access the on-prem app without needing a VPN.

**### 88. What is the "secure score" in Microsoft Defender for Cloud?**

The secure score is an assessment of your security posture. Defender for Cloud continuously analyzes your resources against security best practices and gives you a score based on how many of the recommendations you have implemented. It provides a prioritized list of actions you can take to improve your score and harden your environment.

**### 89. What is Azure Bastion used for?**

Azure Bastion is a fully managed PaaS service that provides secure and seamless RDP and SSH connectivity to your virtual machines directly from the Azure portal. It removes the need to expose your VMs with public IP addresses for management, significantly reducing the attack surface.

**### 90. What is the difference between authentication and authorization?**

* Authentication is the process of proving you are who you say you are. (Are you User A?) This is typically done with a username/password, MFA, or a certificate. In Azure, this is handled by Azure AD.
* Authorization is the process of verifying that you have permission to do what you are trying to do. (Is User A allowed to delete this VM?) In Azure, this is handled by RBAC.

***

#### ## Data & Storage (Continued)

**### 91. What is the difference between Azure SQL Database and SQL Managed Instance?**

* Azure SQL Database: A fully managed PaaS database engine. It's highly compatible with SQL Server, but you don't get OS-level access. It's ideal for new, cloud-native applications.
* SQL Managed Instance: A fully managed PaaS offering that is designed for "lift-and-shift" migrations of on-premises SQL Server workloads. It provides near-100% compatibility with on-prem SQL Server, including features like SQL Agent and VNet-native placement, making migration much easier.

**### 92. What is Azure Cosmos DB?**

Azure Cosmos DB is a globally distributed, multi-model NoSQL database service. It's designed for applications that need extremely low latency (single-digit millisecond) and high availability anywhere in the world. It supports multiple APIs, including SQL (Core), MongoDB, Cassandra, and Gremlin.

**### 93. What is Read-Access Geo-Redundant Storage (RA-GRS)?**

RA-GRS builds on top of GRS (Geo-Redundant Storage). Like GRS, it replicates your data to a secondary region. However, RA-GRS also provides read-only access to the data in the secondary region. This is useful for both disaster recovery (you can read data even if the primary region is down) and for improving read performance for users located closer to the secondary region.

**### 94. You need to store user-uploaded images for a web application. Which Azure service is the most cost-effective and scalable choice?**

Azure Blob Storage is the ideal choice. It's designed for storing large amounts of unstructured object data, is extremely cost-effective, and provides massive scalability. The web application can generate a SAS token to allow the user's browser to upload the image directly and securely to the blob container.

**### 95. What is the purpose of an Azure Data Factory?**

Azure Data Factory (ADF) is a cloud-based ETL (Extract, Transform, Load) and data integration service. It allows you to create, schedule, and orchestrate data-driven workflows (called pipelines) to move and transform data from various sources to various destinations.

**### 96. What is the Azure CDN (Content Delivery Network)?**

Azure CDN is a global network of servers that caches static content (like images, CSS, and JavaScript files) closer to your users. When a user requests a file, it's served from the nearest "edge" location, which reduces latency and improves the performance of your web application.

**### 97. What is an access policy for a storage container?**

An access policy provides an additional level of control over Shared Access Signatures (SAS). Instead of defining the permissions and expiry time on each SAS token individually, you can define them in a stored access policy on the container. You can then create SAS tokens that inherit their constraints from this policy. The key benefit is that you can easily revoke the policy, which instantly invalidates all SAS tokens associated with it.

**### 98. How would you choose between Premium SSD, Standard SSD, and Standard HDD for your VM disks?**

* Premium SSD: Use for production and performance-sensitive workloads, especially databases (e.g., SQL Server, Oracle).
* Standard SSD: Use for web servers, dev/test environments, and lightly used applications that need consistent performance but not the high IOPS of Premium.
* Standard HDD: Use for backup, archival, or infrequent access workloads where low cost is the primary concern and performance is not critical.

**### 99. What is Azure Cache for Redis?**

Azure Cache for Redis is a fully managed, in-memory data store based on the popular open-source Redis. It's used as a distributed cache to improve the performance and scalability of applications by reducing the load on backend databases.

**### 100. What are the consistency levels in Azure Cosmos DB?**

Cosmos DB offers five well-defined consistency levels, which is a key differentiator. From strongest to weakest, they are:

1. Strong: Reads are guaranteed to return the most recent committed version of an item (linearizability).
2. Bounded Staleness: Reads might lag behind writes by a configured amount of time or number of versions.
3. Session: Guarantees that within a single client session, reads will be consistent with previous writes (read-your-own-writes). This is the most popular level.
4. Consistent Prefix: Guarantees that reads never see out-of-order writes.
5.  Eventual: The weakest level. Reads have no order guarantee, but given enough time, all replicas will eventually converge.

    This allows developers to make a fine-grained trade-off between consistency, availability, and latency.
