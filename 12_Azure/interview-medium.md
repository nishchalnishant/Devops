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

