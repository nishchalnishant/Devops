# Azure Cloud Services

Microsoft Azure is a comprehensive cloud platform that provides over 200 products and cloud services. For a DevOps engineer, Azure offers a deep integration with Microsoft's ecosystem (Active Directory, Office 365) and a robust platform for enterprise-scale workloads.

#### 1. Core Architecture
*   **Regions & Geographies:** Physical locations containing one or more data centers.
*   **Availability Sets:** Ensures your VMs are redundant across power and network failures within a data center.
*   **Resource Groups:** Logical containers for resources. In Azure, every resource *must* belong to exactly one resource group.

#### 2. Key Services (The Pillars)
1.  **Compute:** Azure Virtual Machines, App Service (PaaS), and Azure Kubernetes Service (AKS).
2.  **Storage:** Blob Storage (objects), Azure Files (SMB/NFS), and Managed Disks.
3.  **Networking:** Virtual Networks (VNet), Application Gateway (L7 LB), and Azure Front Door.
4.  **Identity:** Azure Active Directory (now Microsoft Entra ID). The backbone of Azure security.

#### 3. Management & Governance
*   **Azure Resource Manager (ARM):** The deployment and management service.
*   **Bicep:** A domain-specific language (DSL) for deploying Azure resources declaratively (easier than ARM JSON).
*   **Azure Policy:** Enforces rules and effects over your resources for compliance.

***

#### 🔹 1. Improved Notes: Enterprise Azure
*   **Azure Landing Zones:** A multi-subscription architecture that provides a pre-configured environment for hosting workloads.
*   **Hybrid Cloud:** Using **Azure Arc** to manage servers and Kubernetes clusters across on-premises, edge, and multi-cloud environments.
*   **FinOps:** Using Azure Cost Management and Advisor to identify underutilized resources and save money.

#### 🔹 2. Interview View (Q&A)
*   **Q:** What is the difference between an `Availability Set` and an `Availability Zone`?
*   **A:** An Availability Set protects against failures *within* a data center. An Availability Zone protects against the failure of an *entire* data center by distributing resources across separate physical locations in a region.
*   **Q:** What is `Azure App Service`?
*   **A:** It is a Platform-as-a-Service (PaaS) that allows you to host web applications without managing the underlying virtual machines.

***

#### 🔹 3. Architecture & Design: Global Load Balancing
Use **Azure Front Door** for global, high-availability web applications. It uses Anycast and the Microsoft global network to route users to the nearest healthy backend, providing SSL offloading and WAF security at the edge.

***

#### 🔹 4. Commands & Configs (Azure CLI)
```bash
# Login to Azure
az login

# List all resource groups in a table format
az group list --output table

# Create a new Virtual Machine
az vm create --resource-group myRG --name myVM --image Ubuntu2204 --admin-username azureuser

# Show AKS cluster credentials
az aks get-credentials --resource-group myRG --name myAKSCluster
```

***

#### 🔹 5. Troubleshooting & Debugging
*   **Scenario:** A deployment failed with a "Quota Exceeded" error.
*   **Fix:** Check the **Subscription Limits**. You may need to request a quota increase for a specific VM family or region in the Azure portal.
*   **Activity Logs:** The first place to look for failed operations in Azure.

***

#### 🔹 6. Production Best Practices
*   **Use Managed Identities:** Avoid storing secrets in your code. Use Managed Identities to allow Azure resources to authenticate to other Azure services (like Key Vault) securely.
*   **Lock Critical Resources:** Use **Management Locks** (`CanNotDelete` or `ReadOnly`) to prevent accidental deletion of production databases or networks.
*   **Network Security Groups (NSG):** Always restrict traffic using NSGs on a "Deny All" basis, allowing only specific ports and IP ranges.

***

#### 🔹 Cheat Sheet / Quick Revision
| **Service** | **Category** | **DevOps Use Case** |
| :--- | :--- | :--- |
| `Azure DevOps` | CI/CD | Microsoft's all-in-one DevOps platform (Repos, Pipelines, Boards). |
| `Key Vault` | Security | Managing secrets, keys, and certificates. |
| `Log Analytics` | Observability | Querying and analyzing telemetry data using KQL. |
| `Cosmos DB` | Database | Globally distributed, multi-model NoSQL database. |

***

This is Section 12: Azure. For a senior role, you should focus on **Azure Blueprints**, **Governance at Scale**, and **Private Link** architecture.
