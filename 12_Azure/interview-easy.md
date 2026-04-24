## Easy

**1. What is an Azure Service Connection?**

A Service Connection is a secure way to authenticate Azure DevOps to Azure Resource Manager or external services. It allows pipelines to deploy resources or access external APIs without embedding credentials in pipeline YAML.

**2. What is the difference between Microsoft-Hosted and Self-Hosted agents?**

- Microsoft-Hosted agents are VMs managed by Microsoft — fresh, clean environment per build but limited software caching and no private VNet access.
- Self-Hosted agents are VMs or containers you manage — faster for incremental builds due to retained layers/packages, and can access private corporate networks.

**3. What is Azure Key Vault?**

Azure Key Vault securely stores and accesses secrets — API keys, passwords, certificates, and cryptographic keys. In DevOps, pipelines fetch credentials from Key Vault rather than storing them in code or plain text variables.

**4. How do you pass variables between different jobs in an Azure YAML Pipeline?**

Output variables from a script using `echo "##vso[task.setvariable variable=myVar;isOutput=true]someValue"`. Subsequent jobs access this output variable by referencing the specific job's dependencies with `$[ dependencies.JobName.outputs['StepName.myVar'] ]`.

**5. What is Azure Resource Manager (ARM)?**

ARM is the deployment and management service for Azure. It provides a management layer for creating, updating, and deleting resources. ARM templates (and Bicep) use this API declaratively to provision infrastructure as code.

**6. What is an Azure Resource Group?**

A resource group is a logical container for Azure resources that share the same lifecycle. Resources in the same group can be deployed, updated, and deleted together. Resource groups also serve as a scope for RBAC and cost management.

**7. What is the difference between Azure Regions and Availability Zones?**

- **Regions:** Independent geographic areas (e.g., East US, West Europe), each containing one or more data centers. Choosing a region affects latency, compliance, and data residency.
- **Availability Zones:** Physically separate data centers within a single region, each with independent power, cooling, and networking. Deploying across zones protects against single-datacenter failures.

**8. What is Azure AKS?**

Azure Kubernetes Service (AKS) is a managed Kubernetes offering. Azure manages the control plane (API server, etcd, scheduler) at no cost; you pay only for worker nodes. It integrates with Azure AD, Azure CNI networking, Azure Monitor, and managed node pools for simplified cluster lifecycle management.

***


**9. What is an Azure Container Registry (ACR)?**

ACR is a managed Docker-compatible registry for storing private container images and Helm charts. It integrates natively with AKS (via `AcrPull` role assignment on the kubelet managed identity), Azure DevOps pipelines, and Azure Container Apps, eliminating the need for DockerHub or self-hosted registries in Azure workloads.

**10. What is the difference between Azure CNI and Kubenet networking in AKS?**

- **Azure CNI:** Every pod receives a real IP from the VNet subnet. Enables direct pod connectivity from other VNet resources and Private Endpoints. Requires pre-allocating IP address space — can exhaust IPs fast in large clusters. Required for Windows node pools and advanced network policies.
- **Kubenet:** Only nodes get VNet IPs; pods use an overlay network with NAT. Conserves VNet address space. Pods are not directly reachable from outside the cluster without extra routing. Simpler but less capable networking model.

**11. What is a Deployment Slot in Azure App Service?**

Deployment slots are independent live environments within an App Service (e.g., `staging`, `production`). You deploy new code to `staging`, run smoke tests, then perform a **slot swap** — Azure routes production traffic to the new instances with near-zero downtime. If something breaks, swap back instantly. App settings can be marked "sticky" (slot-specific) so they don't cross the swap boundary.

**12. What is a Managed Identity and why is it preferred over a Service Principal with a secret?**

A Managed Identity is an Entra ID identity whose lifecycle Azure manages automatically — no credentials to create, store, rotate, or expire. You assign Azure RBAC roles to the identity, and the resource authenticates using the Azure Instance Metadata Service (IMDS). A Service Principal with a secret requires manual credential rotation and creates a secret sprawl risk. Managed Identities eliminate both: no secret = no leak surface.

**13. What is Azure Monitor and how does it relate to Log Analytics?**

Azure Monitor is the umbrella observability platform. Log Analytics Workspace (LAW) is the storage backend where Azure Monitor sends logs and metrics. Resources emit diagnostic data to a LAW; you query it with KQL. Application Insights (for application-level tracing) and Container Insights (for AKS) are both built on top of the same LAW infrastructure.

**14. What is an Azure Private Endpoint?**

A Private Endpoint projects a PaaS service (Storage, Key Vault, SQL, ACR) into your VNet as a private IP address. Traffic to the service stays on the Microsoft backbone — it never traverses the public internet. Requires a corresponding Azure Private DNS Zone so that the service's public hostname resolves to the private IP inside the VNet.

**15. What are the three tiers of Azure Blob Storage access?**

- **Hot:** Optimized for frequent reads/writes. Higher storage cost, lower access cost.
- **Cool:** For infrequently accessed data (monthly). Lower storage cost, higher access cost. Minimum 30-day retention.
- **Archive:** Offline storage for rarely accessed data. Cheapest storage cost, highest retrieval cost and latency (hours to rehydrate).

**16. What is Bicep and how does it relate to ARM templates?**

Bicep is Microsoft's domain-specific language for Azure infrastructure-as-code. It compiles directly to ARM JSON templates — there is no separate runtime; the Azure Resource Manager API only ever receives ARM JSON. Bicep provides cleaner syntax, modules, strong type-checking, and day-zero support for new Azure resource types. `bicep build` compiles to ARM; `bicep decompile` converts ARM JSON back to Bicep.

**17. What is a VNet peering in Azure?**

VNet peering connects two Azure Virtual Networks so that resources in each VNet can communicate using private IP addresses. Traffic routes over the Microsoft backbone, not the public internet. Peering is non-transitive — if VNet A peers with Hub, and Hub peers with VNet B, VNet A cannot reach VNet B directly without additional UDRs (the basis of Hub-and-Spoke architecture).

**18. What is Azure Kubernetes Service (AKS) — what does Azure manage vs. what you manage?**

Azure manages the control plane: the API server, etcd, controller manager, scheduler — all at no cost. You manage the worker nodes (agent pools): VM size selection, node pool scaling, OS patching (via node image upgrades), and application workloads. AKS reduces operational burden by automating control plane upgrades, health monitoring, and integration with Azure networking, identity, and monitoring.

**19. What is a SAS token in Azure Storage?**

A Shared Access Signature (SAS) is a URI that grants restricted, time-limited access to Azure Storage resources without exposing account keys. You specify allowed operations (read, write, delete), resource scope (account, container, blob), and expiry time. Types: Account SAS (broad), Service SAS (single service), User Delegation SAS (recommended — signed by Entra ID credentials, not the account key).

**20. What are Azure Resource Tags and why are they important in enterprise environments?**

Tags are name-value metadata pairs attached to any Azure resource. They enable cost allocation by business unit or project (Azure Cost Management filters by tag), operational queries (`az resource list --tag env=prod`), compliance reporting, and automation targeting. Azure Policy can enforce required tags via `Deny` or `Modify` effects, ensuring every resource is tagged at creation time.
