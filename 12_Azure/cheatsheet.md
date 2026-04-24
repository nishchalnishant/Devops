# Azure DevOps Cheatsheet

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
