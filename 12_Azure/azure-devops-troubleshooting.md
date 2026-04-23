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
