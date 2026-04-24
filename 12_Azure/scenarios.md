# Azure Scenario-Based DevOps Interview Drills

Use these scenarios for final-round technical interviews for Senior/Lead Azure DevOps positions. They are designed to test your mental model of Azure's control/data planes, networking, and CI/CD pipelines.

## Scenario 1: The App Service Slot Swap Disaster

### Prompt
Your team uses Azure App Service. Every release, they deploy the new code to a `staging` slot and perform a VIP swap to `production`. Today, immediately after the swap, the production application started throwing `500 Internal Server Error` connecting to the Azure SQL Database. The team quickly swapped back, but they need you to find the root cause.

### What A Strong Answer Should Cover
- Distinguish between slot-specific (sticky) settings and settings that swap.
- Mention Managed Identities or VNet Integration nuances during swaps.

### Likely Root Causes
1. **Managed Identity Context:** The `staging` slot has its own System-Assigned Managed Identity, distinct from the `production` slot. If the app uses Managed Identities to authenticate to Azure SQL, the staging identity likely wasn't granted database access. When the code swapped, it assumed the production slot's identity, but perhaps the connection strings or token retrieval logic failed to handle the transition correctly, OR the new code deployment modified the connection logic.
2. **VNet Integration Configuration:** VNet integration configurations *do not* automatically swap by default. If the Azure SQL database is behind a Private Endpoint, the staging slot might not be VNet integrated, meaning it could never reach the database during warm-up.
3. **Sticky App Settings:** There might be a connection string or App Setting marked as "Deployment slot setting" (sticky) in the Staging slot that has a bad value or points to a non-existent dev database.

### Strong Mitigation & Prevention
- Always use a User-Assigned Managed Identity, assign it to *both* slots, and grant that identity access to the database.
- Ensure VNet Integration is properly mapped to both slots if accessing private resources.
- Utilize the `Application Initialization` module to ensure the app is fully warmed up and capable of DB connectivity *before* the swap completes (Azure's "auto swap with warm-up" feature).

---

## Scenario 2: Pipeline Timing Out on Microsoft-Hosted Agents

### Prompt
You have a multi-stage YAML pipeline in Azure DevOps. The "Build" stage uses a `ubuntu-latest` Microsoft-hosted agent. Normally it takes 5 minutes. Today, it fails consistently after exactly 60 minutes with a timeout error. No code or pipeline changes were merged recently. 

### What A Strong Answer Should Cover
- Understanding the limits of Microsoft-hosted agents (60 min default timeout for public/private projects on free tier without parallelism paid, though paid parallel jobs can go longer, the default single job timeout is often 60 mins).
- Investigating external dependencies and network egress from the agent.

### Likely Root Causes
1. **External External Dependency Outage:** The agent is hanging trying to download a package from NPM, PyPI, or a Maven repository that is experiencing an outage or severe latency. Since it's a Microsoft-hosted agent, it might be hitting throttling limits.
2. **Silent Prompt/Hanging Process:** A script step recently downloaded an updated third-party tool that is now waiting indefinitely for interactive user input (e.g., a "Do you accept the terms? [y/N]" prompt) because a `--silent` flag was missing.
3. **Resource Exhaustion:** The build process is silently running out of memory (OOM) on the standard Microsoft-hosted agent (which only has 7GB RAM and 2 cores) and thrashing swap indefinitely until the 1-hour timeout hits.

### Strong Mitigation & Prevention
- Review the pipeline logs to see exactly which step is hanging.
- Set explicit, shorter `timeoutInMinutes` on individual steps and jobs so it fails fast (e.g., 10 minutes instead of waiting 60).
- Move to a Self-Hosted Agent or a VMSS Agent Pool if the build requires more RAM, heavy caching, or dedicated network paths.
- Use Azure Artifacts as a proxy/cache upstream for public packages to avoid external registry rate limits.

---

## Scenario 3: Terraform Plan Destruction Loop

### Prompt
Your IaC pipeline uses Terraform (`azurerm` provider) to manage an AKS cluster and its node pools. An engineer added a seemingly harmless tag to the `azurerm_kubernetes_cluster_node_pool` resource. The `terraform plan` in the PR shows that the entire node pool will be *destroyed and recreated*. The engineer is confused why a tag would destroy a node pool.

### What A Strong Answer Should Cover
- Understanding Terraform provider behaviors, `ForceNew` attributes in Azure API.
- Recognizing the blast radius: recreating a node pool destroys all pods running on it.

### Likely Root Causes
- Some attributes in Azure resource manager APIs cannot be updated in-place. While the AKS API *does* support updating tags natively, historically or in certain Terraform provider versions, changes to certain attributes inside node pools (like `node_count` outside of autoscaling, or certain OS configurations) trigger a replacement.
- If it's pure tags: The engineer might have triggered a change on a property that is `ForceNew` by accident while editing the block.
- Alternatively, if `ignore_changes` was managing scaling, the plan might be seeing drift between the state file and the actual Azure API and deciding a replacement is needed.

### Strong Mitigation & Prevention
1. **Never Apply:** Do not approve the PR.
2. **Use Azure Native Tagging or `ignore_changes`:** Implement `lifecycle { ignore_changes = [tags] }` if you prefer to manage tags via Azure Policy.
3. **Zero Downtime Updates:** If a node pool *must* be recreated, use a blue/green node pool strategy: Create a new node pool via code, taint/cordon the old one, let the pods migrate, then delete the old node pool.
4. **Guardrails:** Implement `prevent_destroy = true` on critical stateful resources and strictly control the CI/CD pipeline's ability to run destructive actions against production clusters.

---

## Scenario 4: "Access Denied" Inside an AKS Cluster

### Prompt
A Pod inside your AKS cluster (which has Azure AD Pod Identity or Workload Identity enabled) needs to read secrets from Azure Key Vault. It keeps getting `403 Forbidden` errors. When you test `az keyvault secret show` locally using your Azure AD credentials, it works perfectly.

### What A Strong Answer Should Cover
- The distinction between Control Plane (Reader) and Data Plane (Secrets User) RBAC in Azure.
- Troubleshooting Managed Identities attached to Pods.

### Likely Root Causes
1. **RBAC vs. Access Policies:** The Key Vault might be using the "Azure role-based access control" permission model, but the identity attached to the Pod was only granted "Reader" (a control plane role) instead of "Key Vault Secrets User" (a data plane role).
2. **Wrong Identity Attached:** If using Workload Identity Federation (the modern approach), the Service Account in Kubernetes might not be properly annotated with the `azure.workload.identity/client-id`, or the Entra ID App Registration doesn't trust the AKS cluster's OIDC issuer URL.
3. **Network Firewall:** The Key Vault's networking firewall is set to "Allow selected networks". The AKS Pod's outbound IP (or the AKS VNet/Subnet) is not whitelisted, resulting in a 403.

### Strong Mitigation & Prevention
- Inspect the Key Vault audit logs via Log Analytics. It will tell you exactly which Object ID attempted the access and if it was denied by RBAC or by the Network Firewall.
- Verify the AKS Workload Identity OIDC trust relationship.
- Convert from older Pod Identity to modern Workload Identity, as it relies on Kubernetes native service accounts and OIDC federation rather than intercepting IMDS calls, making it much more reliable.
# Azure DevOps Troubleshooting Guide (7 YOE)

Azure introduces a unique set of failure modes tied closely to its identity model (Entra ID), private networking (Private Endpoints, VNet Integration), and its managed services. This guide covers the most common Azure-specific troubleshooting scenarios a senior engineer will face.

---

## Golden Rule: Azure Identity and Networking First

90% of Azure-specific failures fall into two root cause categories:

1. **Identity/RBAC** — The resource doesn't have the right role assignment, or the identity isn't the one you think it is.
2. **Private Networking/DNS** — The resource is behind a Private Endpoint and either the NSG blocks the traffic, or DNS resolves to the wrong IP.

Always check these two dimensions before digging into application logs.

---

## Scenario 1: Azure DevOps Pipeline — OIDC / Service Connection Failure

### Symptoms
- Pipeline fails at an Azure task (`AzureCLI@2`, `AzureWebApp@1`, `AzureRmWebAppDeployment@4`) with:
  - `AADSTS7000215: Invalid client secret is provided.`
  - `Failed to obtain OIDC token.`
  - `ClientSecretCredential: authentication failed.`

### Triage

**Step 1 — Identify the Service Connection type:**
```
ADO → Project Settings → Service Connections → [your connection] → Edit
Check: Authentication Method = "Workload Identity Federation" OR "Service Principal (manual)"
```

**Step 2a — If Service Principal (manual) with a secret:**

The secret has expired. Service principal secrets in Entra ID have a hard expiry (1 year default).

```bash
# Find expiry date of the app registration's credentials
az ad app credential list --id <app-registration-id> --query "[].{id:keyId,endDate:endDateTime}" -o table
```

**Fix:** Generate a new client secret in Entra ID App Registration → Certificates & secrets, then update the Service Connection in ADO with the new secret value.

**Step 3b — If Workload Identity Federation (OIDC):**

The Federated Credential trust between the ADO project and the Entra ID App Registration has been deleted or modified.

```bash
# List federated credentials on the app registration
az ad app federated-credential list --id <app-registration-id> -o table

# Expected output should show:
# Issuer: https://vstoken.dev.azure.com/<your-org-id>
# Subject: sc://<your-org>/<your-project>/<your-service-connection-name>
```

**Fix:** If the federated credential is missing or the subject doesn't match, recreate it from ADO Project Settings → Service Connections → `Manage Service Principal` → `Federated credentials`.

**Long-Term Recommendation:** Always use Workload Identity Federation (OIDC). It eliminates secret expiry entirely and is currently the Microsoft-recommended approach.

---

## Scenario 2: AKS Pod Cannot Reach Azure SQL / Key Vault / Storage Behind Private Endpoint

### Symptoms
- Pods get `connection refused` or `NXDOMAIN` when connecting to `mydb.database.windows.net`.
- The connection works from a developer's laptop (which uses public IP) but fails from inside the cluster.

### Triage

**Confirming it's a DNS resolution issue:**
```bash
# Run a debug pod in the same namespace
kubectl run dnstest --image=busybox --restart=Never --rm -it -- nslookup mydb.database.windows.net

# If it returns a PUBLIC IP (e.g. 52.x.x.x) → DNS is NOT resolving via Private Endpoint
# If it returns a PRIVATE IP (e.g. 10.x.x.x) → DNS is correct, issue is NSG/Firewall
```

### Root Causes and Fixes

**Root Cause A: VNet not linked to Private DNS Zone**

When the Private Endpoint was created, a Private DNS Zone (e.g., `privatelink.database.windows.net`) was provisioned. This zone must be **linked to the AKS VNet**.

```bash
# Check which VNets are linked to the private DNS zone
az network private-dns link vnet list \
  --resource-group <rg> \
  --zone-name privatelink.database.windows.net \
  -o table

# If the AKS VNet is not listed, create the link
az network private-dns link vnet create \
  --resource-group <rg> \
  --zone-name privatelink.database.windows.net \
  --name aks-vnet-link \
  --virtual-network <aks-vnet-id> \
  --registration-enabled false
```

**Root Cause B: Custom DNS server on VNet not forwarding to Azure resolver**

If the AKS VNet uses a custom DNS server (e.g., an on-premise DNS or Azure Private DNS Resolver), it must **forward** queries for `*.database.windows.net` to `168.63.129.16` (Azure's magic internal DNS resolver IP).

Without this conditional forwarding rule, the custom DNS will attempt to resolve the name externally and return the public IP, bypassing the Private Endpoint entirely.

**Fix:** Add a conditional forwarder on your DNS server:
- Zone: `database.windows.net`
- Forwarder IP: `168.63.129.16`

**Root Cause C: NSG blocking the Private Endpoint subnet**

```bash
# Check NSG rules on the private endpoint subnet
az network nsg rule list \
  --resource-group <rg> \
  --nsg-name <nsg-name> \
  -o table

# Ensure inbound traffic from AKS subnet CIDR to Private Endpoint subnet on port 1433 (SQL) or 443 (Key Vault/Storage) is ALLOWED
```

---

## Scenario 3: Azure Container Registry (ACR) Pull Failures in AKS

### Symptoms
- Pods stuck in `ImagePullBackOff`
- Events: `unauthorized: authentication required` or `403 Forbidden`

### Triage

```bash
kubectl describe pod <pod-name>
# Events section → "Failed to pull image" with 401 or 403
```

### Root Causes and Fixes

**Root Cause A: AKS Managed Identity missing `AcrPull` role**

AKS clusters with managed identity authentication use the **kubelet's managed identity** (not the cluster identity) to pull from ACR.

```bash
# Get the kubelet identity (client ID)
az aks show --resource-group <rg> --name <cluster> \
  --query "identityProfile.kubeletidentity.clientId" -o tsv

# Get the ACR resource ID
az acr show --resource-group <rg> --name <registry> --query id -o tsv

# Assign AcrPull role — this is the fix
az role assignment create \
  --assignee <kubelet-client-id> \
  --role AcrPull \
  --scope <acr-resource-id>
```

**Root Cause B: ACR is network-restricted and AKS egress is blocked**

If ACR has "Selected networks" enabled and the AKS egress IP is not whitelisted:

```bash
# Find AKS outbound IPs
az aks show --resource-group <rg> --name <cluster> \
  --query "networkProfile.loadBalancerProfile.effectiveOutboundIPs[].id" -o tsv | \
  xargs -I{} az network public-ip show --ids {} --query ipAddress -o tsv

# Add these IPs to ACR's allowed network list
az acr network-rule add \
  --resource-group <rg> \
  --name <registry> \
  --ip-address <aks-egress-ip>
```

**Long-Term Fix:** Use ACR with a **Private Endpoint** inside the AKS VNet. This eliminates public IP dependency entirely.

---

## Scenario 4: App Service VNet Integration — Service Unreachable

### Symptoms
- App Service returns `502 Bad Gateway` or `System.Net.SocketException` when connecting to internal services.
- The target service is inside the VNet (e.g., an internal API or a database behind Private Endpoint).

### Triage

**Step 1 — Verify VNet Integration is enabled:**
```
Azure Portal → App Service → Networking → VNet Integration
Status should show: "Connected to <vnet-name>"
```

**Step 2 — Use Kudu to test connectivity from inside the App Service:**
```
https://<your-app>.scm.azurewebsites.net/DebugConsole

# Test TCP connectivity
tcpping <internal-service-hostname> <port>

# Test DNS resolution
nameresolver <internal-service-hostname>
```

### Root Causes and Fixes

**Root Cause A: `WEBSITE_VNET_ROUTE_ALL` not set to `1`**

By default, VNet Integration only routes RFC 1918 private addresses through the VNet. Public DNS names (even if they map to private IPs via Private Endpoint) may be routed outside the VNet.

```bash
az webapp config appsettings set \
  --resource-group <rg> \
  --name <app-name> \
  --settings WEBSITE_VNET_ROUTE_ALL=1
```

**Root Cause B: Private DNS Zone not linked to the Integration subnet's VNet**

The same root cause as AKS (Scenario 2B). The Private DNS Zone for the target service must be linked to the VNet that the App Service uses for integration.

---

## Scenario 5: Azure Firewall Blocking AKS Egress

### Symptoms
- AKS pods cannot reach external services (e.g., `apt-get` fails, container image pulls from Docker Hub fail).
- Clusters deployed in a Hub-and-Spoke topology with a UDR routing `0.0.0.0/0` to Azure Firewall as the next hop.

### Triage

**Step 1 — Check Azure Firewall logs in Log Analytics:**
```kusto
AzureDiagnostics
| where Category == "AzureFirewallNetworkRule" or Category == "AzureFirewallApplicationRule"
| where Action_s == "Deny"
| project TimeGenerated, SourceIP_s, DestinationIP_s, DestinationPort_d, Protocol_s, Action_s
| order by TimeGenerated desc
| take 50
```

**Step 2 — Common required FQDN rules for AKS:**

Azure publishes the required FQDNs for AKS clusters to function. The most critical:

| FQDN | Port | Purpose |
|---|---|---|
| `*.hcp.<region>.azmk8s.io` | 443 | AKS API Server |
| `mcr.microsoft.com` | 443 | Microsoft Container Registry |
| `*.data.mcr.microsoft.com` | 443 | MCR data |
| `management.azure.com` | 443 | Azure management API |
| `login.microsoftonline.com` | 443 | Entra ID auth |
| `packages.microsoft.com` | 443 | Linux package updates |

**Fix:** Add Application Rules in Azure Firewall policy for the required FQDNs. Use Azure Firewall's built-in `AzureKubernetesService` FQDN tag which pre-populates all required AKS FQDNs.

```bash
az network firewall policy rule-collection-group collection add-filter-collection \
  --resource-group <rg> \
  --policy-name <firewall-policy> \
  --rcg-name <rule-collection-group> \
  --name "AKS-Required-FQDNs" \
  --collection-priority 100 \
  --action Allow \
  --rule-name "aks-fqdn-tag" \
  --rule-type ApplicationRule \
  --source-addresses "10.0.0.0/8" \
  --protocols Https=443 \
  --fqdn-tags AzureKubernetesService
```

---

## Scenario 6: Azure Pipelines — Agent Queue Delays / Self-Hosted Agent Not Picking Up Jobs

### Symptoms
- Pipeline jobs sit in `Queued` state for minutes or indefinitely.
- A job that ran in 5 minutes now takes 35 minutes before it even starts.

### Triage

**Step 1 — Check agent pool capacity:**
```
ADO → Organization Settings → Agent Pools → [your pool] → Agents tab
Look for: Agents in "Offline" status, or all agents showing as "Busy"
```

**Step 2 — Check agent capability mismatch:**

If a pipeline demands a specific capability (e.g., `Agent.OS=Linux`) but all available agents are Windows, the job will queue indefinitely.

```
ADO → Agent Pool → [agent] → Capabilities
Compare against: Pipeline → [job] → demands
```

**Step 3 — If self-hosted agent stopped responding:**
```bash
# On the agent VM — check the agent service
sudo systemctl status vsts.agent.*
sudo journalctl -u vsts.agent.* -f

# Common fix: restart the agent service
sudo ./svc.sh stop
sudo ./svc.sh start
```

**Root Cause — Agent inside VNet cannot reach ADO (firewall blocking outbound):**

Self-hosted agents in a private VNet must be able to reach ADO endpoints outbound:
- `dev.azure.com` → port 443
- `*.vsassets.io` → port 443
- `*.vsblob.visualstudio.com` → port 443

Verify this is allowed in the NSG and Azure Firewall application rules.
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
