---
description: Azure AKS architecture, AKS node pools, Azure DevOps pipelines, and enterprise Azure patterns for senior engineers.
---

# Azure — AKS & Azure DevOps

```
AKS & Azure DevOps
├── AKS Architecture
│   ├── Control Plane (Azure-managed, in Azure tenant)
│   │   ├── kube-apiserver (HA, private or public endpoint)
│   │   ├── etcd (managed, encrypted at rest)
│   │   ├── kube-scheduler + controller-manager
│   │   └── OIDC issuer (for Workload Identity)
│   ├── Node Pools (in your subscription)
│   │   ├── System pool (critical system pods: CoreDNS, metrics-server)
│   │   ├── User pools (workload pods)
│   │   ├── Spot pools (cost savings, evictable)
│   │   └── Windows pools (Windows Server containers)
│   ├── Networking
│   │   ├── Azure CNI (VNet IPs per pod)
│   │   ├── Azure CNI Overlay (private CIDR, NAT at node)
│   │   └── Kubenet (pod CIDR, UDRs required for routing)
│   └── Integrations
│       ├── ACR (AcrPull role on kubelet MI)
│       ├── Key Vault (CSI driver + Workload Identity)
│       ├── Azure Monitor / Managed Prometheus
│       └── Azure Load Balancer / App Gateway (AGIC)
├── AKS Authentication Model
│   ├── Control plane access: Entra ID + Kubernetes RBAC
│   ├── Managed Identity: kubelet identity for Azure API calls
│   ├── Workload Identity: per-pod OIDC token exchange (IRSA equivalent)
│   └── aws-auth equivalent: azure-identity-binding (deprecated AAD Pod Identity) → Workload Identity
├── AKS Node Pools
│   ├── Spot pool: eviction policy, taint node.kubernetes.io/spot
│   ├── Scheduling: nodeSelector / tolerations / affinity
│   └── Blue-green pool upgrade: add new pool, cordon+drain old, delete
├── Azure DevOps Pipelines
│   ├── YAML structure: trigger, pool, stages, jobs, steps
│   ├── Build stage: Docker build + push to ACR
│   ├── Deploy Staging: helm upgrade, environment approval gate
│   ├── Deploy Production: manual approval check, production environment
│   ├── Service connections: OIDC (no secrets) preferred over SP
│   └── Variable groups: link to Azure Key Vault for secret injection
└── Logic & Trickiness Table
    ├── Managed Identity vs Workload Identity (resource-level vs pod-level)
    ├── AGIC vs nginx-ingress (Azure WAF integration vs more control)
    ├── System pool taint (CriticalAddonsOnly) prevents user workloads
    └── OIDC issuer must be enabled before creating federated credentials
```

## First Principles

Compute needs identity (AAD), network isolation (VNet), storage, and managed services. AKS = Kubernetes control plane managed by Azure. Azure DevOps = hosted CI/CD. Azure Policy = guardrails enforced at API level. Cost comes from consumption — control it with budgets and tagging.

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

## System Design Perspective

**VNet Peering vs Transit Gateway (Azure Route Server):** VNet peering is direct, non-transitive, and best for 2-5 VNets. For hub-and-spoke at scale, Azure Route Server enables BGP-based transit through an NVA without UDR maintenance on every spoke. ExpressRoute Gateway Transit allows peered VNets to share a single ER circuit.

**Identity Federation (OIDC/SAML):** Workload Identity Federation eliminates static client secrets by exchanging a short-lived OIDC token from the identity provider (GitHub Actions, AKS) for an Azure access token. Entra ID validates the issuer, audience, and subject claims before granting access. SAML 2.0 is used for SSO to legacy enterprise apps; OIDC is preferred for everything modern.

**Cross-Region DR:** For RTO less than 15 min: Azure Front Door routes traffic globally, paired regions share disaster recovery SLAs, geo-redundant storage (GRS/GZRS) replicates data asynchronously. Use Azure Site Recovery for VM-level replication. IaC (Bicep/Terraform) is mandatory — manual re-creation cannot meet aggressive RTOs.

**Cost Allocation Tagging Strategy:** Enforce mandatory tags (CostCenter, Environment, Team, Owner) via Azure Policy with Deny or Append effect at the Management Group level. Use Azure Cost Management to filter spending by tag. Automate tag inheritance from Resource Group to resources using the Inherit Tags built-in initiative.

**Managed Identity vs Service Principals:** Managed Identities are the default choice for any Azure resource accessing other Azure services — zero credential management, auto-rotation. Use Service Principals only for external systems (on-prem, third-party) that cannot use Managed Identity. Workload Identity Federation is the bridge for Kubernetes pods and CI/CD pipelines.

**Azure Policy vs AWS Organizations SCPs:** Azure Policy enforces guardrails at the ARM layer with effects including Deny, Audit, and DeployIfNotExists (auto-remediation). AWS SCPs define the maximum permissions ceiling per OU/account — they cannot grant permissions and act before IAM evaluation. Both use top-down policy inheritance through a hierarchy (Management Group in Azure; Root/OU/Account in AWS).
