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

---

