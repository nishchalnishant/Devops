# Azure DevOps Interview Playbook (7 YOE)

Use this file as the main answer framework for Senior Azure DevOps, Azure SRE, and Azure Cloud Operations interviews. Expect the questions to be deep, architectural, and highly specific to the Microsoft ecosystem.

## What Interviewers Are Really Testing at 7 YOE

### 1. Enterprise Scale and Governance
At 7 years of experience, you aren't just asked how to create a pipeline; you're asked how to govern 500 pipelines across 50 project teams securely.
- **Key Concepts:** Azure Policy, Management Groups, Repository Templates, Microsoft Entra ID (formerly Azure AD) Cross-Tenant management, Enterprise-scale Landing Zones.

### 2. Deep Native Azure Integration
Interviewers want to know if you default to generic open-source solutions when a native, fully-managed Azure service makes more sense.
- **Key Comparisons:** Logic Apps vs. Azure Functions. App Gateway vs. Front Door vs. Traffic Manager. Azure Kubernetes Service (AKS) vs. Azure Container Apps (ACA). Azure DevOps (ADO) vs. GitHub Actions.

### 3. Security and Identity Mastery
Microsoft's cloud is heavily identity-driven.
- **Crucial Topics:** Managed Identities (System-assigned vs. User-assigned), Service Principals vs. Workload Identity Federation (OIDC), Azure Key Vault integration with ADO, Private Endpoints, and VNet Integration.

### 4. Advanced Bicep / Terraform on Azure State Management
You must understand the nuances of the `azurerm` provider, how to manage state in Azure Blob Storage with locks, and the transition/differences between ARM templates and Bicep.

---

## A Strong Answer Framework

For architectural scenarios, standard SRE debugging applies, but you must map it to Azure services:

1. **Clarify symptom and blast radius:** Check Application Insights / Log Analytics. Is it a single App Service or the whole VNet?
2. **Review Identity & RBAC:** In Azure, "Access Denied" or "Resource Not Found" is often a Managed Identity missing a specific Data Plane Role Assignment (not just Control Plane).
3. **Verify Networking:** Is it behind a Private Endpoint? Did the NSG or Azure Firewall block the traffic? Check Network Watcher to verify next hops and packet captures.
4. **Mitigate & Automate:** Rollback the ADO release, swap the staging slot on the App Service, or revert the Terraform plan. Long-term fix uses Azure Policy to prevent the misconfiguration.

---

## What You Should Know By Topic

### Azure DevOps Services (ADO)
- **Pipelines:** YAML vs Classic (Classic is legacy; know YAML). Multi-stage pipelines, `dependsOn`, `conditions`, environments (approval gates, checks).
- **Service Connections:** Workload Identity Federation (OIDC) vs. Service Principal with secrets (OIDC is the modern, secure way).
- **Agents:** Microsoft-hosted vs. Self-hosted vs. Virtual Machine Scale Set (VMSS) agents. How to secure self-hosted agents in a VNet.
- **Artifacts:** Upstream sources, artifact promotion, Universal Packages.

### Infrastructure as Code (IaC) on Azure
- **Terraform:** Best practices for `azurerm`. State file stored in storage account (`backend "azurerm"`). Using `depends_on` when networking resources implicitly depend on each other.
- **Bicep:** Why it's better than ARM (cleaner syntax, modules, transparent state). How to decompile ARM to Bicep. Bicep template specs and container registry modules.

### Azure Compute & Kubernetes
- **AKS (Azure Kubernetes Service):** Azure CNI vs. Kubenet. Azure AD Integration (AKS-managed Azure Active Directory integration). Application Gateway Ingress Controller (AGIC).
- **App Services:** Deployment slots (VIP swap), VNet Integration (Regional vs. Gateway required).
- **Azure Container Apps:** Serverless containers, KEDA (Kubernetes Event-driven Autoscaling) under the hood.

### Azure Networking
- **Hub and Spoke:** VNet Peering, User Defined Routes (UDR), sending traffic through Azure Firewall or an NVA (Network Virtual Appliance).
- **App Gateway vs. Front Door:** App Gateway is regional layer-7 load balancer (WAF). Front Door is global layer-7 load balancer (CDN, WAF, anycast routing).
- **Private Link / Private Endpoint:** Bringing Azure PaaS services (SQL, Key Vault, Storage) into your VNet privately. Understanding the DNS zone override requirements.

### Observability & Monitoring
- **Azure Monitor:** Log Analytics Workspaces (LAW). Kusto Query Language (KQL) basics (e.g., `AppRequests | where Success == False`).
- **Application Insights:** Distributed tracing for app map, Live Metrics Stream.
- **Alerts:** Action Groups and integrating them with ITSM/PagerDuty or Logic Apps.

### Security & Identity
- **Entra ID:** App Registrations vs. Enterprise Applications.
- **Managed Identities:** System-assigned (lives with the resource lifecycle) vs. User-assigned (shared across resources).
- **Azure Policy:** `DeployIfNotExists` vs. `Audit` modes.

---

## Must-Know CLI and KQL Commands

### Azure CLI (`az`)
- `az login --identity` (Logging in from a VM with a managed identity)
- `az account set --subscription <id>`
- `az resource list --resource-group <rg-name> --output table`
- `az aks get-credentials --resource-group <rg> --name <cluster>`
- `az deployment group create --resource-group <rg> --template-file main.bicep`

### Azure DevOps CLI (`az pipelines`)
- `az pipelines run --name <pipeline-name>`
- `az pipelines variable-group list`
- `az repos pr create --title "..."`

### Kusto Query Language (KQL) Basics
```kusto
// Find failed requests in App Insights
requests
| where success == false
| summarize count() by name, resultCode
| order by count_ desc

// Find slow queries dependencies
dependencies
| where type == "SQL"
| where duration > 500
| project timestamp, target, data, duration
```

---

## Design Trade-Offs You Should Be Ready To Explain

- **ADO vs. GitHub Actions:** ADO has better enterprise boards and native test plans. GHA is developer-first, massive marketplace, Microsoft's long-term direction, but enterprise features (environments, manual approvals) are catching up.
- **Terraform vs. Bicep:** Terraform is multi-cloud, massive community, state management required. Bicep is Azure-native, day-0 support for new resources, no state file to manage (Azure is the state), but single cloud.
- **Azure CNI vs. Kubenet in AKS:** Azure CNI gives every Pod an IP from the VNet (can exhaust IPs fast, requires careful planning, highest performance). Kubenet gives nodes IPs, Pods get overlay IPs, uses NAT (saves VNet IPs, slightly slower).
- **App Service Environment (ASE) vs. Multitenant App Service with VNet Integration:** ASE is fully isolated, single-tenant, highly secure but very expensive and slow to provision. Multitenant with VNet integration is cheaper, faster, but shares infrastructure at the control plane layer.

---

## Strong Signals In Senior Azure Answers

- You default to **Managed Identities** and **OIDC** instead of generating secrets and storing them.
- You explicitly mention **Private Endpoints** and DNS resolution complexities when securing PaaS.
- You understand that an Azure resource's control plane (ARM) and data plane (e.g., Key Vault secrets) have different RBAC hierarchies.
- You discuss Azure Policy as the ultimate guardrail for enterprise governance.
- You know that swapping an App Service slot triggers a warm-up phase to avoid cold starts.
