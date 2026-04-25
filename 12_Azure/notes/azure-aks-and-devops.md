---
description: Azure AKS architecture, AKS node pools, Azure DevOps pipelines, and enterprise Azure patterns for senior engineers.
---

# Azure — AKS & Azure DevOps

## AKS Architecture

```
Azure Subscription
└── Resource Group: rg-production
    ├── AKS Cluster: aks-prod
    │   ├── Control Plane (Azure-managed, free)
    │   │   ├── API Server (with Private Endpoint option)
    │   │   ├── etcd
    │   │   └── Scheduler / Controller Manager
    │   │
    │   └── Node Pools (your VMs)
    │       ├── System Node Pool (required: runs CoreDNS, metrics-server)
    │       │   └── Standard_D4s_v3 × 3 nodes
    │       ├── User Node Pool: app-pool
    │       │   └── Standard_D8s_v3 × 5 nodes (auto-scaled 3-10)
    │       └── User Node Pool: gpu-pool
    │           └── Standard_NC6s_v3 × 0-5 nodes (spot instances)
    │
    ├── Azure Container Registry (ACR)
    ├── Azure Key Vault
    └── Virtual Network with CNI-attached subnets
```

***

## AKS Authentication — Azure AD Integration

**Managed Identity** (Recommended — no credential management):

```bash
# Create AKS cluster with managed identity and Azure AD RBAC
az aks create \
  --resource-group rg-production \
  --name aks-prod \
  --enable-managed-identity \
  --enable-azure-rbac \           # Azure AD controls K8s RBAC
  --enable-aad \
  --aad-admin-group-object-ids <GROUP_OBJECT_ID>

# Grant a team access via Azure RBAC (not kubectl)
az role assignment create \
  --role "Azure Kubernetes Service RBAC Reader" \
  --assignee <USER_OR_GROUP_ID> \
  --scope /subscriptions/.../resourceGroups/rg-production/providers/Microsoft.ContainerService/managedClusters/aks-prod
```

**Workload Identity (Pod-level identity — replaces AAD Pod Identity):**

```yaml
# Link K8s ServiceAccount to Azure Managed Identity
apiVersion: v1
kind: ServiceAccount
metadata:
  name: api-server
  namespace: production
  annotations:
    azure.workload.identity/client-id: "MI_CLIENT_ID"

# Pod gets Azure token without any secrets
spec:
  serviceAccountName: api-server
  containers:
    - name: api
      # Uses DefaultAzureCredential() — automatically uses workload identity
```

***

## AKS Node Pools — Advanced Patterns

```bash
# Add a spot node pool for batch workloads (60-80% cheaper)
az aks nodepool add \
  --resource-group rg-production \
  --cluster-name aks-prod \
  --name spotpool \
  --node-vm-size Standard_D4s_v3 \
  --priority Spot \
  --eviction-policy Delete \
  --spot-max-price -1 \            # Use current spot price
  --enable-cluster-autoscaler \
  --min-count 0 \
  --max-count 20 \
  --node-taints "kubernetes.azure.com/scalesetpriority=spot:NoSchedule"
```

**Scheduling pods on spot nodes:**
```yaml
spec:
  tolerations:
    - key: "kubernetes.azure.com/scalesetpriority"
      operator: "Equal"
      value: "spot"
      effect: "NoSchedule"
  affinity:
    nodeAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
        - weight: 100
          preference:
            matchExpressions:
              - key: "kubernetes.azure.com/scalesetpriority"
                operator: In
                values: ["spot"]
```

***

## Azure DevOps — Pipeline Architecture

```yaml
# azure-pipelines.yml
trigger:
  branches:
    include: [main]
  paths:
    exclude: [docs/*, '*.md']    # Don't trigger on doc changes

pool:
  vmImage: 'ubuntu-latest'      # Microsoft-hosted agent

variables:
  - group: production-secrets   # Variable group from Azure Key Vault link
  - name: dockerRegistryServiceConnection
    value: 'acr-connection'

stages:
  - stage: Build
    jobs:
      - job: BuildAndScan
        steps:
          - task: Docker@2
            displayName: Build image
            inputs:
              command: build
              dockerfile: Dockerfile
              containerRegistry: $(dockerRegistryServiceConnection)
              repository: myapp
              tags: $(Build.BuildId)

          - task: AquaSecurityTrivy@1
            displayName: Scan image
            inputs:
              image: myapp:$(Build.BuildId)
              severities: CRITICAL,HIGH
              exitCode: 1

  - stage: DeployStaging
    dependsOn: Build
    condition: succeeded()
    jobs:
      - deployment: DeployToAKS
        environment: staging     # Azure DevOps environment with approvals
        strategy:
          runOnce:
            deploy:
              steps:
                - task: KubernetesManifest@1
                  inputs:
                    action: deploy
                    kubernetesServiceConnection: aks-staging
                    manifests: k8s/*.yml
                    containers: |
                      myacr.azurecr.io/myapp:$(Build.BuildId)

  - stage: DeployProduction
    dependsOn: DeployStaging
    jobs:
      - deployment: DeployToProd
        environment: production  # Has manual approval gate configured
        strategy:
          runOnce:
            deploy:
              steps:
                - task: KubernetesManifest@1
                  inputs:
                    action: deploy
                    kubernetesServiceConnection: aks-prod
                    manifests: k8s/*.yml
```

***

## ACR — Azure Container Registry Integration

```bash
# Attach ACR to AKS (grants AcrPull managed identity permission)
az aks update \
  --resource-group rg-production \
  --name aks-prod \
  --attach-acr mycompanyacr

# Geo-replication for global performance
az acr replication create \
  --registry mycompanyacr \
  --location westeurope

# Enable content trust (image signing)
az acr config content-trust update \
  --registry mycompanyacr \
  --status enabled
```

***

## Logic & Trickiness Table

| Concept | Common Mistake | Senior Understanding |
|:---|:---|:---|
| **AKS auth** | Using `az aks get-credentials` with admin flag | Use `--overwrite-existing` only for break-glass; enforce Azure AD RBAC |
| **Node pools** | One node pool for everything | Separate system + user + spot pools; taints/tolerations for placement |
| **Workload Identity** | AAD Pod Identity (deprecated) | Use Workload Identity Federation (GA since AKS 1.28) |
| **ACR integration** | Storing ACR credentials as K8s secrets | Use managed identity via `az aks update --attach-acr` |
| **Private AKS** | Public API server | Enable private cluster + Private DNS Zone for production |
| **Upgrades** | Upgrade control plane only | Upgrade in order: control plane → system node pool → user node pools |
