# Azure — Interview Questions

All difficulty levels combined.

---

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

## Medium

**9. What is the difference between an Azure Managed Identity and a Service Principal?**

A Service Principal is an identity created for use with applications, hosted services, and automated tools to access Azure resources — requiring you to explicitly manage and rotate its secret or certificate. A Managed Identity is a feature of Microsoft Entra ID that provides an automatically managed identity in Azure. You don't manage credentials; Azure handles the lifecycle of the identity. System-Assigned Managed Identities die when the resource is deleted; User-Assigned ones persist and can be shared across multiple resources.

**10. How do you securely manage Terraform state for Azure infrastructure?**

Terraform state should be managed in an Azure Storage Account Blob container using the `azurerm` backend. To secure it: lock down the Storage Account's network access with private endpoints, use RBAC to restrict access to the state blob to the pipeline's Managed Identity, enable Soft Delete and point-in-time restore for recovery, and rely on Azure blob leases to prevent concurrent state corruption.

**11. What are the pros and cons of using Azure Logic Apps vs. Azure Functions?**

Azure Functions is a code-first serverless compute service — better for complex, custom logic, high-performance data processing, and developers preferring C#, Python, or Node.js. Azure Logic Apps is a designer-first, visual orchestration service — it excels at workflow automation and connecting third-party systems using hundreds of pre-built connectors. Logic Apps becomes unwieldy for highly complex nested programming logic; Functions require more development effort for simple integrations.

**12. How would you implement a Blue-Green deployment for an Azure App Service?**

Azure App Service provides Deployment Slots. Create a `staging` slot identical to `production`. The CI/CD pipeline deploys new code to `staging`. Once staging passes smoke tests, perform a Swap operation in Azure — Azure routes production traffic to the new instances, and the old production becomes the staging slot. If an issue occurs, swap back instantly. Traffic routing percentages can also be used for canary-style gradual shifts.

**13. Why is Bicep gaining popularity over ARM templates?**

ARM templates are JSON-based, verbose, and difficult to read at scale without extensive tooling. Bicep is a DSL created by Microsoft specifically for Azure. It offers cleaner syntax, transparent compilation into standard ARM JSON, modularity via the `module` block, strong type checking, and day-zero support for new Azure features without waiting for an external provider update. Bicep is the recommended path for new Azure IaC development.

**14. What is Azure Key Vault and how do you integrate it with a Kubernetes workload?**

Azure Key Vault stores secrets, certificates, and keys. To integrate with Kubernetes, use the Secrets Store CSI Driver with the Azure Key Vault provider — it mounts secrets from Key Vault directly into pods as volume files or environment variables. Combined with Azure Workload Identity, the pod authenticates to Key Vault via a federated Kubernetes ServiceAccount token, eliminating stored credentials entirely.

**15. What is the difference between Azure DevOps Service Connections and GitHub OIDC?**

An Azure DevOps Service Connection stores credentials (Service Principal client secret or certificate) in Azure DevOps to authenticate to external resources. GitHub OIDC uses federated identity — no stored credentials at all. The GitHub Actions workflow requests a short-lived token from Azure by presenting a JWT signed by GitHub's OIDC endpoint. OIDC is preferred because credentials cannot leak when there is nothing stored, and tokens expire automatically after the job completes.

**16. What is Azure Policy and how does it enforce compliance?**

Azure Policy evaluates resources against defined rules and effects. Effects include `Deny` (block non-compliant resource creation), `Audit` (log non-compliance without blocking), `DeployIfNotExists` (automatically remediate by deploying a resource), and `Modify` (add or update tags). Policies are assigned to scopes (management group, subscription, resource group) and evaluated at creation time and during compliance scans. Policy initiatives bundle multiple policies for standards like CIS benchmarks.

---

## Hard

**17. Design an enterprise Hub-and-Spoke networking architecture for an AKS deployment, detailing the security controls.**

Architecture:

- **Hub:** Houses Azure Firewall (or NVAs like Palo Alto), Azure App Gateway with WAF, and Azure Bastion for secure node access. Azure Route Server may be used for BGP routing.
- **Spokes:** The AKS cluster lives in a Spoke VNet, using an internal load balancer so it is never exposed directly to the internet.
- **Routing:** User Defined Routes (UDR) in the Spoke force all outbound traffic from AKS through the Azure Firewall in the Hub for inspection (`0.0.0.0/0` → Firewall Private IP). Firewall rules allow only known egress destinations (container registries, Azure APIs, OS update repos).
- **Ingress:** External traffic hits the App Gateway in the Hub, which terminates TLS and inspects via WAF, then routes traffic over VNet peering to the AKS internal ingress controller.
- **Control plane security:** Private cluster mode so the Kubernetes API server is only accessible within the VNet or via Private Link. Entra ID integration for RBAC.

**18. How do you govern a multi-tenant Azure AD (Entra ID) CI/CD environment where hundreds of teams create their own pipelines?**

Governance must be baked in at the control plane level:

- **Azure Policy:** Enforce `DeployIfNotExists` or `Deny` policies preventing teams from creating public endpoints, forcing deployment to specific regions, or mandating required tags.
- **ADO Governance:** Disable classic release pipelines and mandate YAML. Use ADO Repository Templates and require `extends` templates so every pipeline inherits a baseline security structure with non-bypassable security scans.
- **Identity:** Strict RBAC via Entra ID groups scoped to subscriptions. Azure AD Privileged Identity Management (PIM) for Just-In-Time access to production subscriptions, reducing standing privileges for both pipelines and human operators.
- **Service Connection scope:** Lock Service Connections to specific resource groups — prevent pipelines from accessing subscriptions outside their designated scope.

**19. Compare Azure Front Door and Azure Application Gateway. When would you use both together?**

- **Azure Front Door:** A global, anycast layer-7 load balancer with integrated CDN and WAF. Routes traffic to the closest healthy regional backend. Operates at the global edge.
- **Application Gateway:** A regional layer-7 load balancer with WAF, primarily for VNet injection and routing to private resources like an internal AKS cluster.
- **Using both:** In a highly secure, globally distributed application. Front Door acts as the global entry point — terminating user TLS, blocking global DDoS/WAF attacks, and serving static content at the edge. Front Door forwards dynamic traffic to regional Application Gateways using Private Link service (or verifying the `X-Azure-FDID` header to block direct access). The App Gateway routes traffic securely into the VNet to AKS.

**20. An Azure App Service using VNet Integration to access an Azure SQL Database behind a Private Endpoint has intermittent DNS-related connection failures. What is happening?**

Azure Private Endpoints rely on Azure Private DNS Zones. When the App Service queries `mydb.database.windows.net`, VNet integration forces the DNS query into the VNet. If the VNet is not linked to the `privatelink.database.windows.net` Private DNS Zone, the App Service resolves the public IP instead of the private IP — and the SQL DB firewall blocks public IPs.

If it's intermittent, the likely cause is a custom DNS server on the VNet (e.g., pointing to on-premises DNS) that fails to forward the query to Azure's internal resolver `168.63.129.16`. You must ensure conditional forwarding from your custom DNS server to `168.63.129.16` for the `privatelink.database.windows.net` zone. Also verify the Private DNS Zone is linked to every VNet that needs to resolve the endpoint.

**21. How do you implement zero-trust network security for an AKS workload in Azure?**

Zero-trust assumes no implicit trust inside the network:

1. **Network policies:** Use Calico or Azure CNI with Network Policies to enforce pod-to-pod communication rules. Default-deny all ingress/egress; explicitly allow only required paths.
2. **Workload Identity:** Replace static Service Principal credentials with Azure Workload Identity (federated tokens). Pods authenticate to Azure services (Key Vault, Storage) without any stored secrets.
3. **Private cluster + Private Endpoints:** AKS API server and all dependent services (ACR, Key Vault, SQL) behind Private Endpoints — no public IPs.
4. **mTLS:** Service mesh (Istio on AKS or Azure Service Mesh) enforces mTLS between all pods, ensuring only authenticated workloads communicate.
5. **Admission control:** OPA Gatekeeper or Kyverno enforces policies — no privileged containers, required labels, approved base images from ACR only.
6. **Microsoft Defender for Containers:** Runtime threat detection and vulnerability scanning.
