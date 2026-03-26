# Azure easy qeustions

#### ## Azure Fundamentals & Core Concepts

**1. What is a Resource Group in Azure?**

A Resource Group is a logical container for grouping related Azure resources. It helps in managing the lifecycle of resources together; for example, deleting a resource group deletes all the resources within it.

**2. What is the relationship between a Subscription, a Resource Group, and a Resource?**

* Subscription: The top-level billing and management boundary. All resources are created within a subscription.
* Resource Group: A container within a subscription that holds related resources. A resource must belong to exactly one resource group.
* Resource: An individual service instance, like a virtual machine, a storage account, or a database.

**3. What are Azure Regions and Availability Zones (AZs)?**

* Region: A specific geographical location in the world containing one or more datacenters (e.g., "East US", "West Europe").
* Availability Zone (AZ): A physically separate datacenter within a single Azure region. Each AZ has independent power, cooling, and networking. Using multiple AZs allows you to build highly available applications that are resilient to datacenter-level failures.

**4. What is Azure Resource Manager (ARM)?**

Azure Resource Manager (ARM) is the deployment and management service for Azure. It provides a consistent management layer that enables you to create, update, and delete resources in your Azure account. All tools, from the Azure Portal to the CLI and SDKs, use the ARM API.

**5. What is Azure Policy?**

Azure Policy is a service that allows you to create, assign, and manage policies to enforce organizational standards and compliance. For example, you can create a policy to allow only certain VM sizes to be deployed or to require that all storage accounts are encrypted.

**6. What is Azure Role-Based Access Control (RBAC)?**

RBAC is the system used to manage access to Azure resources. You assign roles (like "Owner", "Contributor", "Reader") to users, groups, or service principals at a specific scope (like a subscription or resource group) to grant them the necessary permissions.

**7. What is a Service Principal in Azure?**

A Service Principal is an identity created for use with applications, hosted services, and automated tools to access Azure resources. It's like a "user identity" but for a script or an application. It is the recommended way to grant CI/CD pipelines access to Azure.

**8. What are Azure Management Groups?**

Management Groups are containers that help you manage access, policy, and compliance across multiple subscriptions. You can apply policies or RBAC roles to a management group, and they will be inherited by all subscriptions within it.

**9. What is the Azure CLI?**

The Azure CLI is a cross-platform command-line tool for managing Azure resources. It's used for creating and managing resources from the command line or in automation scripts.

**10. What is the purpose of tags in Azure?**

Tags are key-value pairs that you can apply to Azure resources to logically organize them. They are crucial for cost management and billing (e.g., tagging resources by department or project) and for automation.

**11. What is the Azure Portal?**

The Azure Portal is a web-based, unified console that provides a graphical user interface to manage your Azure resources.

**12. What is Azure Advisor?**

Azure Advisor is a personalized cloud consultant that analyzes your resource configuration and usage telemetry to provide recommendations for improving high availability, security, performance, and cost-effectiveness.

**13. What is the Azure Marketplace?**

The Azure Marketplace is an online store that offers thousands of applications and services from Microsoft and third-party partners that are certified to run on Azure, such as virtual machine images, application templates, and SaaS apps.

**14. What is Azure Cost Management?**

Azure Cost Management + Billing is a suite of tools that helps you monitor, control, and optimize your Azure spending. You can set budgets, get cost analysis reports, and receive recommendations to reduce costs.

**15. What is Azure Active Directory (Azure AD)?**

Azure AD is Microsoft's cloud-based identity and access management service. It provides user authentication, single sign-on (SSO), and multi-factor authentication (MFA). It is the identity backbone for Azure and Microsoft 365.

***

#### ## Azure Compute

**16. What are Azure Virtual Machines (VMs)?**

Azure VMs are on-demand, scalable computing resources that provide the flexibility of virtualization without having to buy and maintain the physical hardware. They are the IaaS (Infrastructure as a Service) offering.

**17. What is an Azure App Service?**

Azure App Service is a fully managed PaaS (Platform as a Service) for building, deploying, and scaling web apps and APIs. It handles the underlying infrastructure (OS, patching, web servers), allowing developers to focus on their code.

**18. What is an App Service Plan?**

An App Service Plan defines the set of compute resources your web app runs on. It's like the server farm for your App Service. It determines the region, number of VM instances, VM size (CPU/memory), and pricing tier (Free, Shared, Basic, Standard, Premium). Multiple apps can run on the same App Service Plan.

**19. What are Azure Functions?**

Azure Functions is a serverless compute service that lets you run event-triggered code without having to provision or manage infrastructure. You only pay for the compute time you consume.

**20. When would you use Azure Functions instead of Azure App Service?**

You would use Azure Functions for small, event-driven tasks that run for a short duration, like processing a file upload, running a scheduled job, or responding to an API call. You would use Azure App Service for hosting larger, more traditional web applications or APIs that need to be "always on."

**21. What is a Virtual Machine Scale Set (VMSS)?**

A VMSS lets you create and manage a group of load-balanced, identical VMs. The number of VM instances can automatically increase or decrease in response to demand or a defined schedule (autoscaling).

**22. What is an availability set in Azure?**

An Availability Set is a logical grouping of VMs within a single datacenter that allows Azure to understand how your application is built to provide redundancy. It spreads your VMs across different Fault Domains (racks with common power/network) and Update Domains (groups of VMs that may be rebooted at the same time for maintenance).

**23. What's the difference between an Availability Set and Availability Zones?**

* Availability Set: Protects against failures within a single datacenter (e.g., rack failure, host maintenance).
* Availability Zones: Protects against failures of an entire datacenter. It offers a higher level of availability.

**24. What is a deployment slot in Azure App Service?**

Deployment slots are live web apps with their own hostnames. They allow you to deploy a new version of your app to a non-production "staging" slot, validate it, and then instantly "swap" it with the production slot with zero downtime. This is used for blue-green deployments.

**### 25. What is Azure Batch used for?**

Azure Batch is a service for running large-scale parallel and high-performance computing (HPC) batch jobs efficiently in the cloud.

**26. What are the different ways to connect to an Azure VM?**

For a Windows VM, you use RDP (Remote Desktop Protocol). For a Linux VM, you use SSH (Secure Shell). Azure Bastion can also be used for secure access through the portal.

**27. What is Azure Reserved Virtual Machine Instances (RIs)?**

Reserved Instances allow you to get a significant discount (up to 72%) on VM costs by committing to a one- or three-year term for a specific VM type in a specific region.

**28. What is Azure Hybrid Benefit?**

The Azure Hybrid Benefit is a licensing offer that helps you reduce the costs of running workloads in the cloud by letting you use your on-premises Software Assurance-enabled Windows Server and SQL Server licenses on Azure.

**29. What is Azure Dedicated Host?**

Azure Dedicated Host provides physical servers that host one or more Azure virtual machines, dedicated to a single Azure subscription. It's used to meet specific compliance or regulatory requirements that demand physical isolation.

**30. What is Azure Spot Virtual Machines?**

Azure Spot VMs allow you to access unused Azure compute capacity at a very large discount. They are ideal for workloads that can be interrupted, as Azure can reclaim the capacity at any time with short notice.

***

#### ## Azure Storage

**31. What are the three main types of storage in an Azure Storage Account?**

The three main types are Blob Storage, File Storage, and Queue Storage. (Table Storage is also available).

**32. What is Azure Blob Storage used for?**

Blob Storage is optimized for storing massive amounts of unstructured object data, such as text, images, videos, and application binaries. It's commonly used for serving images directly to a browser, storing data for backup/restore, and as a data lake for analytics.

**33. What is the difference between Hot, Cool, and Archive access tiers for Blob Storage?**

* Hot: Optimized for frequently accessed data. Has higher storage costs but lower access costs.
* Cool: Optimized for infrequently accessed data that is stored for at least 30 days. Has lower storage costs but higher access costs.
* Archive: Optimized for rarely accessed data that is stored for at least 180 days, with flexible latency requirements (on the order of hours). It has the lowest storage cost but the highest retrieval cost.

**34. What is Azure Files?**

Azure Files offers fully managed file shares in the cloud that are accessible via the standard Server Message Block (SMB) and Network File System (NFS) protocols. It's like a traditional file server in the cloud and is often used for "lift and shift" migrations.

**35. What is a Shared Access Signature (SAS) token?**

A SAS token is a string containing a set of query parameters that can be appended to a storage resource URI. It provides secure, delegated access to resources in your storage account with specific permissions (e.g., read-only) for a specified period of time, without sharing your account keys.

**36. What are the different types of disks for Azure VMs?**

The main types are Standard HDD, Standard SSD, and Premium SSD. For high-performance workloads, there is also Ultra Disk Storage.

**37. What is Azure Data Lake Storage (ADLS)?**

ADLS is a set of capabilities built on top of Azure Blob Storage, designed for big data analytics. It provides a hierarchical namespace (like a file system), which is crucial for the performance of analytics jobs.

**38. How do you host a static website on Azure?**

You can enable the static website feature on an Azure Storage Account. This automatically creates a special container named `$web`. You upload your HTML, CSS, and JavaScript files to this container, and Azure provides an endpoint to serve the content.

**39. What is Azure Storage Explorer?**

Azure Storage Explorer is a standalone app from Microsoft that provides a graphical interface for managing the contents of your Azure storage accounts on Windows, macOS, and Linux.

**40. What is storage account replication (LRS, GRS, ZRS)?**

* LRS (Locally-Redundant Storage): Replicates your data three times within a single datacenter.
* ZRS (Zone-Redundant Storage): Replicates your data across three different Availability Zones within a single region.
* GRS (Geo-Redundant Storage): Replicates your data to a secondary region hundreds of miles away.

***

#### ## Azure Networking

**41. What is an Azure Virtual Network (VNet)?**

A VNet is the fundamental building block for your private network in Azure. It is a logically isolated section of the Azure cloud where you can launch your Azure resources, like VMs.

**42. What is a Subnet?**

A subnet is a range of IP addresses within a VNet. You can divide a VNet into multiple subnets to organize and secure your resources. For example, you might have a public-facing subnet for web servers and a private subnet for backend databases.

**43. What is a Network Security Group (NSG)?**

An NSG acts as a basic, stateful firewall. It contains a list of security rules that allow or deny network traffic to resources connected to Azure VNets. You can associate an NSG with a subnet or a specific network interface.

**44. What is the difference between Azure Load Balancer and Application Gateway?**

* Azure Load Balancer: A Layer 4 (TCP, UDP) load balancer. It distributes traffic based on source IP, port, destination IP, and protocol. It doesn't understand HTTP.
* Application Gateway: A Layer 7 (HTTP/HTTPS) load balancer and Web Application Firewall (WAF). It can make routing decisions based on HTTP attributes like URL path or host headers. It can also handle SSL termination.

**45. What is Azure DNS?**

Azure DNS is a hosting service for DNS domains that provides name resolution using Microsoft Azure infrastructure. You can manage your DNS records for your domains within Azure.

**46. What is VNet Peering?**

VNet Peering allows you to seamlessly connect two or more Azure Virtual Networks. Once peered, the VNets appear as one for connectivity purposes, and traffic between them uses the Microsoft backbone network.

**47. What is Azure VPN Gateway?**

A VPN Gateway is a specific type of virtual network gateway that is used to send encrypted traffic between an Azure VNet and an on-premises location over the public internet.

**48. What is Azure ExpressRoute?**

Azure ExpressRoute lets you create private connections between Azure datacenters and your on-premises infrastructure. These connections don't go over the public internet and offer higher reliability, faster speeds, and lower latencies.

**49. What is Azure Firewall?**

Azure Firewall is a managed, cloud-based network security service that protects your Azure VNet resources. It's a fully stateful firewall as a service with built-in high availability and unrestricted cloud scalab<sup>1</sup>ility.

**50. What is Azure Bastion?**

Azure Bastion is a fully managed PaaS service that you provision inside your VNet. It provides secure and seamless RDP and SSH access to your virtual machines directly through the Azure Portal over SSL, without needing to expose your VMs to the public internet with a public IP.

**51. What is a Private Endpoint?**

A Private Endpoint is a network interface that uses a private IP address from your VNet. It connects you privately and securely to an Azure PaaS service (like Azure Storage or SQL Database) using Azure Private Link, effectively bringing the service into your VNet.

**52. What is a Service Endpoint?**

A VNet Service Endpoint provides secure and direct connectivity to Azure services over an optimized route on the Azure backbone network. It allows you to secure your PaaS resources to only your VNet.

**53. What is the difference between a Private Endpoint and a Service Endpoint?**

* Service Endpoint: Secures the PaaS service to your subnet. The PaaS resource still has a public IP, but access is restricted at the service level.
* Private Endpoint: Maps a PaaS service to a private IP address _within_ your VNet. The service is no longer accessible over the public internet at all. Private Endpoints are generally considered more secure.

**54. What is Azure Traffic Manager?**

Azure Traffic Manager is a DNS-based traffic load balancer that enables you to distribute traffic to your public-facing applications across different Azure regions or even external endpoints. It uses DNS to direct clients to the appropriate endpoint based on a traffic-routing method (e.g., performance, geographic, weighted).

**55. What is a User-Defined Route (UDR)?**

A UDR allows you to override Azure's default system routes and define a custom route for traffic leaving a subnet. This is commonly used to force traffic through a Network Virtual Appliance (NVA) or a firewall for inspection.

***

#### ## Azure DevOps & CI/CD

**56. What is Azure DevOps?**

Azure DevOps is a suite of services that provides an end-to-end solution for planning work, collaborating on code development, and building and deploying applications.

**57. What are the five main services within Azure DevOps?**

1. Azure Boards: For agile planning and work item tracking.
2. Azure Repos: Provides private Git repositories for source control.
3. Azure Pipelines: The CI/CD service for building and deploying code.
4. Azure Test Plans: For manual and exploratory testing.
5. Azure Artifacts: A package manager for hosting artifacts like Maven, npm, and NuGet packages.

**58. What is the `azure-pipelines.yml` file?**

It is the YAML file that defines your build and release pipeline as code in Azure Pipelines. It specifies the triggers, stages, jobs, and steps for your CI/CD process.

**59. What is a stage in Azure Pipelines?**

A stage is a major logical division in a pipeline, such as "Build", "Test", "Deploy to Staging", or "Deploy to Prod". Each stage contains one or more jobs.

**60. What is the difference between a job and a step?**

* Job: A collection of steps that run together sequentially on the same agent.
* Step: The smallest building block of a pipeline. It can be a script, a shell command, or a pre-defined task (like "DotNetCoreCLI@2").

**61. What is an Azure Pipelines Agent?**

An agent is the compute infrastructure (a VM or container) that runs the jobs in your pipeline. You can use Microsoft-hosted agents (managed by Microsoft) or self-hosted agents (machines that you manage yourself).

**62. When would you use a self-hosted agent instead of a Microsoft-hosted agent?**

You would use a self-hosted agent when you need more control over the build environment, require specific software to be installed, need to access resources in a private network, or have large builds that would be expensive on hosted agents.

**63. What is a task group in Azure Pipelines?**

A task group allows you to encapsulate a sequence of tasks that you use repeatedly in multiple pipelines into a single, reusable task.

**64. What is a variable group?**

A variable group is a collection of variables that can be shared across multiple pipelines. They are often used to store secrets and other configuration values that are linked to an Azure Key Vault.

**### 65. What is an environment in Azure Pipelines?**

An environment represents a deployment target, such as a Kubernetes cluster, a VM, or a web app. You can define approvals and checks on an environment to control deployments.

**### 66. What are approvals and checks?**

Approvals and checks are security gates that you can add to an environment. An approval requires one or more users to manually approve a deployment before it can proceed. Checks can be automated conditions, like ensuring the code is on a specific branch or invoking an Azure Function.

**### 67. What is Azure Repos?**

Azure Repos is a set of version control tools hosted by Azure DevOps. It provides unlimited private Git repositories and supports Team Foundation Version Control (TFVC).

**### 68. What is Azure Artifacts?**

Azure Artifacts is a package management service that allows you to create and share Maven, npm, NuGet, and Python package feeds from public and private sources. It's used to manage your dependencies and store the artifacts produced by your pipelines.

**### 69. How do you handle secrets in Azure Pipelines?**

You should store secrets in Azure Key Vault. You can then link the Key Vault to a Variable Group in Azure DevOps and reference the secrets in your pipeline, where they will be masked in logs.

**### 70. What is a multi-stage pipeline?**

A multi-stage pipeline is a YAML pipeline that defines your entire CI and CD process, from code to production, in a single file. It allows you to see the entire workflow and manage it as code.

***

#### ## Containers on Azure

**### 71. What is Azure Container Registry (ACR)?**

ACR is a managed, private Docker registry service based on the open-source Docker Registry 2.0. It's used to build, store, and manage your private container images.

**### 72. What is Azure Container Instances (ACI)?**

ACI is a serverless container service. It offers the fastest and simplest way to run a single container in Azure without having to manage any virtual machines or adopt a higher-level orchestrator.

**### 73. What is Azure Kubernetes Service (AKS)?**

AKS is a fully managed Kubernetes service. It simplifies deploying, managing, and scaling containerized applications using Kubernetes by offloading the operational overhead of the control plane to Azure.

**### 74. What is the difference between ACI and AKS?**

* ACI: For running single, simple containers or short-lived tasks where you don't need a full orchestration platform. It's serverless and per-second billing.
* AKS: A full-blown container orchestrator for managing complex, multi-container microservices applications. It provides advanced features like service discovery, load balancing, and automated scaling.

**### 75. What is the AKS control plane? Is it free?**

The AKS control plane consists of the core Kubernetes components (like the API server, scheduler, etcd) that Azure manages for you. Yes, the control plane is provided at no cost; you only pay for the worker nodes that run your containers.

**### 76. What is the Azure CNI plugin for AKS?**

The Azure CNI (Container Network Interface) plugin is a networking model for AKS where every pod gets an IP address directly from the subnet, making them first-class citizens on the VNet. This allows them to be directly reachable from other VNet resources.

**### 77. How do you scale applications in AKS?**

You can scale applications horizontally by changing the `replicas` count in a Deployment. For automatic scaling, you can use the Horizontal Pod Autoscaler (HPA), which scales the number of pods based on metrics like CPU usage.

**### 78. How do you scale the number of nodes in an AKS cluster?**

You use the Cluster Autoscaler. This component watches for pods that can't be scheduled due to resource constraints and automatically adds new nodes to the cluster. It also removes underutilized nodes to save costs.

**### 79. What is Azure Service Fabric?**

Azure Service Fabric is a distributed systems platform for packaging, deploying, and managing scalable and reliable microservices and containers. It's an alternative to Kubernetes, often used for stateful services.

**### 80. How can you build container images directly within Azure without a Docker desktop?**

You can use ACR Tasks. `az acr build` is a command that allows you to build a Docker image in the cloud from your source code. ACR Tasks can also be configured to automatically rebuild an image when the base image is updated or when code is pushed to a Git repository.

***

#### ## Azure Monitoring & Observability

**### 81. What is Azure Monitor?**

Azure Monitor is the central platform for collecting, analyzing, and acting on telemetry data from your Azure and on-premises environments. It collects two fundamental types of data: Metrics and Logs.

**### 82. What is the difference between Metrics and Logs in Azure Monitor?**

* Metrics: Numerical values that describe some aspect of a system at a point in time (e.g., CPU percentage, network in). They are lightweight and capable of supporting near real-time scenarios.
* Logs: Contain different kinds of data organized into records with different sets of properties for each type. They are useful for deep analysis and diagnostics.

**### 83. What is a Log Analytics Workspace?**

A Log Analytics Workspace is the primary environment in Azure for storing and querying log data collected by Azure Monitor. It's a container where log data is aggregated from various sources.

**### 84. What is the Kusto Query Language (KQL)?**

KQL is the powerful query language used to query log data in a Log Analytics Workspace and Application Insights. It's a read-only language designed for querying large datasets.

**### 85. What is Application Insights?**

Application Insights is a feature of Azure Monitor. It is an extensible Application Performance Management (APM) service for developers and DevOps professionals. It's used to monitor your live applications, automatically detect performance anomalies, and includes powerful analytics tools to help you diagnose issues.

**### 86. What is a metric alert in Azure Monitor?**

A metric alert is an alert rule that triggers when a specified metric value crosses a threshold. For example, you can create an alert to notify you when "Percentage CPU" on a VM is greater than 90% for 5 minutes.

**### 87. What is an action group?**

An action group is a collection of notification preferences and actions that can be triggered by an alert. You can configure it to send an email, an SMS, make a webhook call, or trigger an Azure Function or Logic App.

**### 88. What is Azure Service Health?**

Azure Service Health provides personalized alerts and guidance when Azure service issues, planned maintenance, or health advisories affect your resources.

**### 89. How can you monitor the performance of your Azure VMs?**

You can use Azure Monitor for VMs (VM Insights), which analyzes the performance and health of your Windows and Linux VMs. It monitors key performance indicators (KPIs) and can map discovered application components running on the VMs.

**### 90. What is a diagnostic setting in Azure?**

A diagnostic setting defines how and where to export platform logs and metrics for a specific Azure resource. For example, you can create a diagnostic setting on an NSG to send all its logs to a Log Analytics Workspace for analysis.

***

#### ## Infrastructure as Code (IaC) & Automation

**### 91. What is an ARM Template?**

An ARM (Azure Resource Manager) template is a JSON file that defines the infrastructure and configuration for your project. It uses a declarative syntax to specify the resources you want to deploy without having to write the sequence of programming commands to create them.

**### 92. What is Bicep?**

Bicep is a domain-specific language (DSL) that uses a simpler, declarative syntax to deploy Azure resources. It's an abstraction on top of ARM templates. Bicep files are transpiled into standard ARM JSON files before deployment, but they are much easier to write and read.

**### 93. What is the difference between ARM templates and Bicep?**

Bicep offers a cleaner and less verbose syntax than ARM JSON. It provides better type safety, modularity, and a better authoring experience with tooling like the VS Code extension. It is the recommended IaC language for Azure.

**### 94. What does it mean for an IaC deployment to be idempotent?**

Idempotency means that deploying the same template multiple times will result in the same resource state. If you deploy a template to create a VM and then run the same deployment again, it will recognize that the VM already exists and make no changes.

**### 95. What is the "what-if" operation in ARM template deployments?**

The what-if operation is Azure's equivalent of `terraform plan`. It allows you to preview the changes that will happen to your environment if you deploy a template, without actually applying those changes.

**### 96. What is Azure Automation?**

Azure Automation is a cloud-based automation and configuration service that allows you to automate frequent, time-consuming, and error-prone cloud management tasks using "runbooks" based on PowerShell or Python.

**### 97. What is Azure PowerShell?**

Azure PowerShell is a module that provides cmdlets to manage Azure resources directly from the PowerShell command line. It's an alternative to the Azure CLI.

**### 98. How would you store the state for Terraform when working with Azure?**

The recommended approach is to use an Azure Storage Account as the remote backend. This allows multiple team members to work on the same infrastructure code and ensures the state file is stored securely and reliably.

**### 99. What is the `az` command?**

`az` is the command that invokes the Azure CLI. For example, `az group create` creates a resource group, and `az vm list` lists your virtual machines.

**### 100. What is a "desired state" in the context of declarative IaC?**

The desired state is the final configuration of your environment that you define in your IaC file (like a Bicep or Terraform file). The IaC tool is responsible for comparing this desired state with the actual current state and making the necessary changes to bring them into alignment.
