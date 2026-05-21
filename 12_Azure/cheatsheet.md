# Azure DevOps Cheatsheet

```
Azure DevOps Cheatsheet
├── Azure CLI Authentication
│   ├── az login (interactive browser)
│   ├── az login --service-principal (CI/CD)
│   ├── az account set --subscription (switch context)
│   └── az configure --defaults (set default RG/location)
├── Resource Management
│   ├── Resource Groups (az group create/list/delete)
│   ├── ARM/Bicep Deployments (az deployment group create)
│   ├── what-if mode (--what-if flag before applying)
│   └── Deployment modes: Incremental vs Complete
├── AKS Operations
│   ├── Cluster create/get-credentials/upgrade
│   ├── Node pool add/scale/upgrade
│   ├── kubectl commands via az aks command invoke
│   └── Managed Identity + OIDC issuer configuration
├── ACR (Azure Container Registry)
│   ├── az acr build (build in cloud, no local Docker)
│   ├── az acr login / docker push/pull
│   └── ACR attach to AKS (managed identity pull)
├── Key Vault
│   ├── az keyvault create / secret set / secret show
│   ├── RBAC assignment to identity for KV access
│   └── Private endpoint for KV (disable public access)
├── Managed Identity
│   ├── System-assigned (lifecycle tied to resource)
│   ├── User-assigned (shareable across resources)
│   └── az identity create / role assignment
├── Storage
│   ├── az storage account create (LRS/GRS/ZRS)
│   ├── az storage blob upload/download/list
│   └── SAS tokens (delegated short-lived access)
├── VNet & Networking
│   ├── az network vnet create / subnet create
│   ├── NSG rules: az network nsg rule create
│   ├── Private Endpoint: az network private-endpoint create
│   └── Private DNS zone link to VNet
├── Bicep & Terraform
│   ├── Bicep: param, var, resource, module, output
│   ├── az bicep build (transpile to ARM JSON)
│   └── Terraform azurerm backend (blob state storage)
├── Azure DevOps Pipelines
│   ├── YAML pipeline: trigger, pool, stages, jobs, steps
│   ├── Environments + approval checks
│   ├── Service connections (OIDC preferred, no secrets)
│   └── Variable groups + Azure Key Vault integration
├── Workload Identity Federation
│   ├── az ad app federated-credential create
│   ├── Bind to K8s ServiceAccount + namespace
│   └── No static client secret — OIDC token exchange
├── AKS Troubleshooting
│   ├── kubectl describe / logs / events
│   ├── az aks check-acr (pull permission validation)
│   └── az network watcher (connectivity tests)
├── Identity Concept Table
│   ├── Service Principal vs Managed Identity vs Workload Identity
│   └── When to use each (SP: legacy; MI: Azure resources; WI: K8s pods)
├── Policy Effects Table
│   ├── Deny (block at ARM level)
│   ├── Audit (log non-compliant, allow)
│   ├── DeployIfNotExists (auto-remediate)
│   └── Modify / Append (mutate resource properties)
├── Hub-and-Spoke Topology
│   ├── Hub VNet: Firewall, Bastion, VPN/ExpressRoute GW
│   ├── Spoke VNets: peered to hub (non-transitive by default)
│   └── UDRs (force traffic through hub firewall)
└── Key Gotchas
    ├── VNet peering is non-transitive (need Route Server or NVA for transit)
    ├── Private DNS zone must be linked to VNet for resolution
    ├── ACR pull fails if Managed Identity lacks AcrPull role
    └── Workload Identity requires OIDC issuer enabled on AKS cluster
```

## First Principles

Compute needs identity (AAD), network isolation (VNet), storage, and managed services. AKS = Kubernetes control plane managed by Azure. Azure DevOps = hosted CI/CD. Azure Policy = guardrails enforced at API level. Cost comes from consumption — control it with budgets and tagging.

## Azure CLI — Core Commands

```bash
# Auth
az login
az login --service-principal -u $CLIENT_ID -p $CLIENT_SECRET --tenant $TENANT_ID
az account list --output table
az account set --subscription "my-subscription-id"

# Resource groups
az group create --name myRG --location eastus
az group list --output table
az group delete --name myRG --yes --no-wait

# Resources
az resource list --resource-group myRG --output table
az resource show --ids /subscriptions/.../resourceGroups/myRG/providers/...
az resource tag --tags Env=prod Team=platform -g myRG -n myResource \
  --resource-type Microsoft.Compute/virtualMachines

# Deployments (ARM/Bicep)
az deployment group create \
  --resource-group myRG \
  --template-file main.bicep \
  --parameters @params.prod.json

az deployment group what-if \
  --resource-group myRG \
  --template-file main.bicep

# AKS
az aks create \
  --resource-group myRG \
  --name myAKS \
  --node-count 3 \
  --node-vm-size Standard_D4s_v3 \
  --enable-oidc-issuer \
  --enable-workload-identity \
  --enable-managed-identity \
  --network-plugin azure \
  --network-policy calico \
  --zones 1 2 3

az aks get-credentials --resource-group myRG --name myAKS
az aks nodepool add --cluster-name myAKS -g myRG --name gpupool \
  --node-vm-size Standard_NC6s_v3 --node-count 2 \
  --node-taints sku=gpu:NoSchedule

az aks upgrade --resource-group myRG --name myAKS --kubernetes-version 1.30.0

# ACR
az acr create --name myRegistry --resource-group myRG --sku Premium
az acr login --name myRegistry
az acr build --registry myRegistry --image myapp:v1.0 .
az acr repository list --name myRegistry --output table
az aks update --name myAKS -g myRG --attach-acr myRegistry

# Key Vault
az keyvault create --name myKV --resource-group myRG --location eastus
az keyvault secret set --vault-name myKV --name db-password --value "secret123"
az keyvault secret show --vault-name myKV --name db-password --query value -o tsv

# Managed Identity
az identity create --name myIdentity --resource-group myRG
az role assignment create \
  --assignee <principal-id> \
  --role "Key Vault Secrets User" \
  --scope /subscriptions/.../resourceGroups/myRG/providers/Microsoft.KeyVault/vaults/myKV

# Storage
az storage account create \
  --name mystorageacct \
  --resource-group myRG \
  --sku Standard_GRS \
  --kind StorageV2 \
  --https-only true \
  --min-tls-version TLS1_2

az storage container create --name tfstate --account-name mystorageacct
```

## Azure Networking Quick Reference

```bash
# VNet
az network vnet create \
  --name myVNet --resource-group myRG \
  --address-prefix 10.0.0.0/16 \
  --subnet-name default --subnet-prefix 10.0.0.0/24

# NSG
az network nsg create --name myNSG -g myRG
az network nsg rule create --nsg-name myNSG -g myRG \
  --name AllowHTTPS --priority 100 \
  --protocol Tcp --destination-port-ranges 443 --access Allow

# Private Endpoint
az network private-endpoint create \
  --name myPE --resource-group myRG \
  --vnet-name myVNet --subnet default \
  --private-connection-resource-id <resource-id> \
  --group-id blob \
  --connection-name myPEConnection

# Private DNS Zone (required for Private Endpoints)
az network private-dns zone create -g myRG -n "privatelink.blob.core.windows.net"
az network private-dns link vnet create -g myRG \
  -n myDNSLink \
  -z "privatelink.blob.core.windows.net" \
  -v myVNet --registration-enabled false
```

## Bicep Quick Reference

```bicep
// main.bicep — deploy a storage account with all best practices
param location string = resourceGroup().location
param environment string
param storageAccountName string

var tags = {
  Environment: environment
  ManagedBy: 'bicep'
}

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageAccountName
  location: location
  tags: tags
  sku: {
    name: 'Standard_GRS'
  }
  kind: 'StorageV2'
  properties: {
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
    allowBlobPublicAccess: false
    networkAcls: {
      defaultAction: 'Deny'
      bypass: 'AzureServices'
    }
  }
}

output storageAccountId string = storageAccount.id
output storageAccountName string = storageAccount.name
```

```bicep
// Module call
module storage './modules/storage.bicep' = {
  name: 'storageDeployment'
  params: {
    environment: environment
    storageAccountName: 'st${environment}${uniqueString(resourceGroup().id)}'
  }
}
```

```bash
# Bicep build / lint
bicep build main.bicep          # compile to ARM JSON
bicep lint main.bicep           # check for issues
bicep decompile main.json       # ARM JSON → Bicep (reverse)
```

## Terraform azurerm Backend

```hcl
terraform {
  backend "azurerm" {
    resource_group_name  = "tfstate-rg"
    storage_account_name = "tfstateprod"
    container_name       = "tfstate"
    key                  = "prod/aks/terraform.tfstate"
    use_oidc             = true   # authenticate via federated identity (no client secret)
  }

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.100"
    }
  }
}

provider "azurerm" {
  features {}
  use_oidc = true   # GitHub Actions OIDC / Workload Identity
}
```

## Azure Workload Identity Setup (AKS)

```bash
# 1. Get OIDC issuer URL
ISSUER=$(az aks show -n myAKS -g myRG --query oidcIssuerProfile.issuerUrl -o tsv)

# 2. Create Managed Identity
az identity create --name myWorkloadId --resource-group myRG

CLIENT_ID=$(az identity show --name myWorkloadId -g myRG --query clientId -o tsv)

# 3. Create federated credential
az identity federated-credential create \
  --name myFedCred \
  --identity-name myWorkloadId \
  --resource-group myRG \
  --issuer $ISSUER \
  --subject "system:serviceaccount:my-namespace:my-serviceaccount" \
  --audience api://AzureADTokenExchange

# 4. Annotate Kubernetes ServiceAccount
kubectl annotate serviceaccount my-serviceaccount \
  -n my-namespace \
  azure.workload.identity/client-id=$CLIENT_ID
```

```yaml
# Pod spec
metadata:
  labels:
    azure.workload.identity/use: "true"
spec:
  serviceAccountName: my-serviceaccount
```

## Azure DevOps Pipeline — Key Patterns

```yaml
# OIDC auth to Azure (no stored secrets)
- task: AzureCLI@2
  inputs:
    azureSubscription: 'my-service-connection'
    scriptType: bash
    scriptLocation: inlineScript
    inlineScript: |
      az aks get-credentials -n myAKS -g myRG
      kubectl apply -f manifests/

# Pass output variable between jobs
jobs:
- job: Build
  steps:
  - bash: echo "##vso[task.setvariable variable=IMAGE_TAG;isOutput=true]$(Build.BuildId)"
    name: setTag

- job: Deploy
  dependsOn: Build
  variables:
    IMAGE_TAG: $[ dependencies.Build.outputs['setTag.IMAGE_TAG'] ]
  steps:
  - bash: echo "Deploying image tag $(IMAGE_TAG)"

# Deployment environment with approvals
- stage: Production
  jobs:
  - deployment: DeployProd
    environment: production   # requires approval in ADO UI
    strategy:
      runOnce:
        deploy:
          steps:
          - bash: helm upgrade --install myapp ./chart --set image.tag=$(IMAGE_TAG)

# Conditional stage
- stage: Integration
  condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
```

## AKS Troubleshooting Commands

```bash
# Node / pod health
kubectl get nodes -o wide
kubectl describe node <node-name>
kubectl top nodes
kubectl top pods -A --sort-by=memory

# Pod issues
kubectl describe pod <pod> -n <ns>
kubectl logs <pod> -n <ns> --previous
kubectl exec -it <pod> -n <ns> -- bash

# Network connectivity test
kubectl run nettest --rm -it --image=nicolaka/netshoot -- bash
# inside: curl -v http://my-service.namespace.svc.cluster.local
# inside: nslookup my-service.namespace.svc.cluster.local

# AKS diagnostics
az aks check-acr --name myAKS --resource-group myRG --acr myRegistry
az aks show -n myAKS -g myRG --query agentPoolProfiles[].{name:name,count:count,vmSize:vmSize}

# Node pool operations
az aks nodepool scale --cluster-name myAKS -g myRG --name nodepool1 --node-count 5
az aks nodepool upgrade --cluster-name myAKS -g myRG --name nodepool1 --kubernetes-version 1.30.0

# Drain / cordon
kubectl cordon <node>
kubectl drain <node> --ignore-daemonsets --delete-emptydir-data
kubectl uncordon <node>
```

## Identity and Access — Key Concepts

| Concept | Description | When to Use |
|---------|-------------|-------------|
| System-Assigned MI | Identity tied to a resource's lifecycle | Single resource, disposable |
| User-Assigned MI | Standalone identity, reusable | Multiple resources sharing the same identity |
| Service Principal | App identity with explicit secret/cert | CI/CD when MI not available |
| Azure Workload Identity | Federated K8s ServiceAccount → MI | AKS pods accessing Azure services |
| PIM (Privileged Identity Management) | Just-in-time role activation | Human operators needing elevated access |
| Conditional Access | Enforce MFA, location, device compliance | Protecting management plane access |

## Azure Policy — Effect Reference

| Effect | Behavior |
|--------|----------|
| `Deny` | Block resource creation/update if non-compliant |
| `Audit` | Log non-compliance, allow operation |
| `AuditIfNotExists` | Audit if a related resource doesn't exist |
| `DeployIfNotExists` | Auto-deploy a remediation resource |
| `Modify` | Add/replace/remove tags or properties |
| `Append` | Add fields to the resource being created |
| `Disabled` | No effect — used to turn off a policy temporarily |

## Hub-and-Spoke Networking Reference

```
Internet
    │
    ▼
Azure Front Door (global WAF, CDN, anycast)
    │
    ▼
HUB VNet (per region)
├── Azure Firewall        ← all spoke egress forced through here (UDR)
├── Application Gateway   ← regional WAF + L7 LB
├── Azure Bastion         ← secure RDP/SSH without public IPs
└── VPN/ExpressRoute GW   ← on-premises connectivity

SPOKE VNets (peered to Hub, no spoke-to-spoke peering)
├── Spoke A: AKS cluster  ← internal LB only, private cluster
├── Spoke B: App Service  ← VNet integration
└── Spoke C: Data         ← private endpoints for SQL, Storage
```

UDR to force egress through firewall:
```bash
az network route-table create --name spoke-udr -g myRG
az network route-table route create \
  --route-table-name spoke-udr -g myRG \
  --name DefaultToFirewall \
  --address-prefix 0.0.0.0/0 \
  --next-hop-type VirtualAppliance \
  --next-hop-ip-address 10.0.0.4  # Azure Firewall private IP
```

## Key Gotchas

| Gotcha | Detail |
|--------|--------|
| Slot settings don't always swap | App settings marked "Deployment slot setting" stay with the slot |
| Private Endpoint requires Private DNS Zone | Without DNS zone link, resolves to public IP — firewall blocks it |
| AKS upgrade node pool ≠ control plane upgrade | Must upgrade control plane first, then each node pool separately |
| Managed Identity per slot | System-assigned MIs are slot-specific — grant access to each slot's identity |
| ACR Premium required for Private Link | Basic/Standard tiers don't support private endpoints |
| NSG on subnet + NIC are AND'd | Traffic must pass both the subnet NSG and NIC NSG |
| `az aks get-credentials` overwrites kubeconfig | Use `--file` or `KUBECONFIG` env var to preserve existing contexts |
| OIDC issuer must be enabled at cluster creation | Cannot enable retroactively without recreation |
| ARM template `what-if` != `terraform plan` | `what-if` may show noise from read-only diffs |
| Resource lock blocks delete | `CanNotDelete` lock must be removed before `az group delete` |

## System Design Perspective

**VNet Peering vs Transit Gateway (Azure Route Server):** VNet peering is direct, non-transitive, and best for 2-5 VNets. For hub-and-spoke at scale, Azure Route Server enables BGP-based transit through an NVA without UDR maintenance on every spoke. ExpressRoute Gateway Transit allows peered VNets to share a single ER circuit.

**Identity Federation (OIDC/SAML):** Workload Identity Federation eliminates static client secrets by exchanging a short-lived OIDC token from the identity provider (GitHub Actions, AKS) for an Azure access token. Entra ID validates the issuer, audience, and subject claims before granting access. SAML 2.0 is used for SSO to legacy enterprise apps; OIDC is preferred for everything modern.

**Cross-Region DR:** For RTO less than 15 min: Azure Front Door routes traffic globally, paired regions share disaster recovery SLAs, geo-redundant storage (GRS/GZRS) replicates data asynchronously. Use Azure Site Recovery for VM-level replication. IaC (Bicep/Terraform) is mandatory — manual re-creation cannot meet aggressive RTOs.

**Cost Allocation Tagging Strategy:** Enforce mandatory tags (CostCenter, Environment, Team, Owner) via Azure Policy with Deny or Append effect at the Management Group level. Use Azure Cost Management to filter spending by tag. Automate tag inheritance from Resource Group to resources using the Inherit Tags built-in initiative.

**Managed Identity vs Service Principals:** Managed Identities are the default choice for any Azure resource accessing other Azure services — zero credential management, auto-rotation. Use Service Principals only for external systems (on-prem, third-party) that cannot use Managed Identity. Workload Identity Federation is the bridge for Kubernetes pods and CI/CD pipelines.

**Azure Policy vs AWS Organizations SCPs:** Azure Policy enforces guardrails at the ARM layer with effects including Deny, Audit, and DeployIfNotExists (auto-remediation). AWS SCPs define the maximum permissions ceiling per OU/account — they cannot grant permissions and act before IAM evaluation. Both use top-down policy inheritance through a hierarchy (Management Group in Azure; Root/OU/Account in AWS).
