# Azure Cloud Services

```
Azure Cloud Services
├── Core Architecture
│   ├── Management Groups → Subscriptions → Resource Groups → Resources
│   ├── Regions (paired regions for HA/DR)
│   ├── Availability Zones (independent datacenters per region)
│   └── Azure Resource Manager (ARM) — control plane for all operations
├── Identity & Access (Entra ID)
│   ├── Tenants, Users, Groups, Service Principals
│   ├── Managed Identities (system-assigned / user-assigned)
│   ├── Workload Identity Federation (OIDC, no static credentials)
│   ├── RBAC (Owner, Contributor, Reader, custom roles)
│   └── Conditional Access + PIM (Just-in-Time)
├── Compute
│   ├── Virtual Machines (VM sizes: B/D/E/F/N series)
│   ├── App Service (PaaS web hosting, deployment slots)
│   ├── Azure Kubernetes Service (AKS)
│   ├── Azure Container Apps (managed K8s abstraction)
│   └── Azure Functions (serverless, consumption / premium plan)
├── Storage
│   ├── Blob Storage (Hot / Cool / Archive tiers)
│   ├── Azure Files (SMB/NFS managed file shares)
│   ├── Managed Disks (Premium SSD / Ultra / Standard)
│   └── Data Lake Storage Gen2 (hierarchical namespace on Blob)
├── Networking
│   ├── VNet (isolated network), Subnets, NSGs, Route Tables
│   ├── VNet Peering (regional / global, non-transitive)
│   ├── Azure Firewall / NVA (hub-and-spoke with UDRs)
│   ├── Private Endpoints + Private DNS Zones
│   ├── Azure Front Door (global CDN + WAF + load balancing)
│   ├── Application Gateway v2 (regional L7 + WAF)
│   ├── Azure Load Balancer (L4, regional)
│   ├── VPN Gateway / ExpressRoute (hybrid connectivity)
│   └── NAT Gateway (managed outbound SNAT)
├── Security & Governance
│   ├── Azure Policy (Deny / Audit / DeployIfNotExists / Modify)
│   ├── Azure Key Vault (secrets, keys, certs; RBAC vs access policies)
│   ├── Microsoft Defender for Cloud (threat detection, posture)
│   └── Service Control via Management Group hierarchy
├── Observability
│   ├── Azure Monitor (metrics, logs, alerts)
│   ├── Log Analytics Workspace (KQL queries)
│   ├── Application Insights (APM, distributed tracing)
│   └── Azure Managed Prometheus + Grafana
├── DevOps & CI/CD
│   ├── Azure DevOps (Pipelines, Repos, Boards, Artifacts)
│   ├── GitHub Actions with Azure OIDC (no long-lived secrets)
│   └── Azure Container Registry (ACR)
├── IaC
│   ├── ARM Templates (JSON, verbose)
│   ├── Bicep (ARM DSL, concise)
│   └── Terraform azurerm provider (azurerm backend for state)
├── Cost Management
│   ├── Azure Cost Management + Budgets + Alerts
│   ├── Reserved Instances / Savings Plans / Spot VMs
│   └── Tag-based cost allocation strategy
└── Key Services Quick Reference
    ├── AKS, ACR, Key Vault, App Service, Functions
    ├── Storage Account, VNet, NSG, Private Endpoint
    └── Azure DevOps, Entra ID, Azure Policy
```

## First Principles

Compute needs identity (AAD), network isolation (VNet), storage, and managed services. AKS = Kubernetes control plane managed by Azure. Azure DevOps = hosted CI/CD. Azure Policy = guardrails enforced at API level. Cost comes from consumption — control it with budgets and tagging.

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

## System Design Perspective

**VNet Peering vs Transit Gateway (Azure Route Server):** VNet peering is direct, non-transitive, and best for 2-5 VNets. For hub-and-spoke at scale, Azure Route Server enables BGP-based transit through an NVA without UDR maintenance on every spoke. ExpressRoute Gateway Transit allows peered VNets to share a single ER circuit.

**Identity Federation (OIDC/SAML):** Workload Identity Federation eliminates static client secrets by exchanging a short-lived OIDC token from the identity provider (GitHub Actions, AKS) for an Azure access token. Entra ID validates the issuer, audience, and subject claims before granting access. SAML 2.0 is used for SSO to legacy enterprise apps; OIDC is preferred for everything modern.

**Cross-Region DR:** For RTO less than 15 min: Azure Front Door routes traffic globally (DNS + Anycast), paired regions share disaster recovery SLAs, geo-redundant storage (GRS/GZRS) replicates data asynchronously. Use Azure Site Recovery for VM-level replication. IaC (Bicep/Terraform) is mandatory — manual re-creation cannot meet aggressive RTOs.

**Cost Allocation Tagging Strategy:** Enforce mandatory tags (CostCenter, Environment, Team, Owner) via Azure Policy with Deny or Append effect at the Management Group level. Use Azure Cost Management to filter spending by tag. Automate tag inheritance from Resource Group to resources using the Inherit Tags built-in initiative.

**Managed Identity vs Service Principals:** Managed Identities are the default choice for any Azure resource accessing other Azure services — zero credential management, auto-rotation. Use Service Principals only for external systems (on-prem, third-party) that cannot use Managed Identity. Workload Identity Federation is the bridge for Kubernetes pods and CI/CD pipelines.

**Azure Policy vs AWS Organizations SCPs:** Azure Policy enforces guardrails at the ARM layer with effects including Deny, Audit, and DeployIfNotExists (auto-remediation). AWS SCPs define the maximum permissions ceiling per OU/account — they cannot grant permissions and act before IAM evaluation. Both use top-down policy inheritance through a hierarchy (Management Group in Azure; Root/OU/Account in AWS).