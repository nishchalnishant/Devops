# Azure — Deep Dive Notes

## Table of Contents

1. [Azure Architecture & Core Concepts](#1-azure-architecture--core-concepts)
2. [Azure Resource Manager (ARM)](#2-azure-resource-manager-arm)
3. [Compute Services](#3-compute-services)
4. [Storage Services](#4-storage-services)
5. [Networking Fundamentals](#5-networking-fundamentals)
6. [Identity & Access Management](#6-identity--access-management)
7. [Governance & Compliance](#7-governance--compliance)
8. [Infrastructure as Code](#8-infrastructure-as-code)
9. [Monitoring & Observability](#9-monitoring--observability)
10. [Cost Management](#10-cost-management)

***

## 1. Azure Architecture & Core Concepts

### Global Infrastructure

```
Azure Cloud
├── Geography (e.g., North America, Europe)
│   └── Region (e.g., East US, West Europe)
│       ├── Availability Zone 1 (physically separate datacenter)
│       ├── Availability Zone 2 (independent power, cooling, networking)
│       └── Availability Zone 3 (optional, region-dependent)
│
└── Azure Global Network (fiber-optic backbone, 100+ Gbps per link)
```

**Regions**
- Geographic areas where Azure has datacenters
- Each region is independent — failure in one doesn't affect others
- Some regions support **Availability Zones** (AZs), others are zone-redundant only

**Availability Zones**
- Physically separate datacenters within a region
- Each AZ has independent power, cooling, and networking
- Connected via high-speed private fiber (< 2ms latency)
- Zone-redundant services replicate across 3+ AZs automatically

**Region Pairs**
- Each region is paired with another region in the same geography (e.g., East US ↔ West US)
- Azure updates regions in pairs to minimize downtime
- Data residency: paired regions are in the same legal/tax geography

***

## 2. Azure Resource Manager (ARM)

### Deployment Model

```
Request Flow:
User/CLI/Portal → ARM API → Authorization (Azure RBAC) → Validation → Provider (Microsoft.Compute, etc.) → Resource Creation
```

**Key Concepts:**
- **Resource Provider:** A service that exposes Azure resources (e.g., `Microsoft.Compute`, `Microsoft.Storage`)
- **Resource Type:** Specific resource within a provider (e.g., `Microsoft.Compute/virtualMachines`)
- **API Version:** Each resource type has versioned APIs (e.g., `2024-03-01`)

### Resource Group Internals

- Logical container — not a physical boundary
- Resources can communicate across resource groups freely
- RBAC and locks applied at RG level inherit to all child resources
- **Critical:** Deleting an RG deletes ALL resources within it — no soft delete for RGs

### Deployment Modes

```bash
# Incremental (default) — adds/updates resources, leaves extras untouched
az deployment group create \
  --resource-group myRG \
  --template-file main.bicep \
  --mode Incremental

# Complete — deletes resources not in template (DANGEROUS in production)
az deployment group create \
  --resource-group myRG \
  --template-file main.bicep \
  --mode Complete
```

### What-If Operation

```bash
az deployment group what-if \
  --resource-group myRG \
  --template-file main.bicep \
  --exclude-changeTypes Ignore NoChange

# Output shows:
#   ~ Modify (property changed)
#   + Create (new resource)
#   - Delete (resource will be removed)
#   * NoChange (detected but ignored)
```

***

## 3. Compute Services

### Compute Decision Tree

```
Need full OS control?
├── Yes → Azure Virtual Machines (IaaS)
│
└── No → Need to manage runtime/dependencies?
    ├── Yes → Azure App Service (PaaS)
    │   └── Need container support?
    │       ├── Yes → Azure Container Apps (serverless containers)
    │       └── No → App Service (web apps, APIs)
    │
    └── No → Need Kubernetes orchestration?
        ├── Yes → Azure Kubernetes Service (AKS)
        └── No → Azure Functions (event-driven, serverless)
```

### Azure Virtual Machines

**VM Sizing Convention:**
```
Standard_D4s_v3
│       │ │  └── Generation (v3 = 3rd gen hardware)
│       │ └──── Specialized (s = premium storage support)
│       └────── VCPU count (4 vCPUs)
└────────────── Category (D = general purpose)
```

**Categories:**
| Prefix | Category | Use Case |
|--------|----------|----------|
| `B` | Burstable | Dev/test, low baseline CPU with burst capability |
| `D` | General Purpose | Balanced CPU/memory — web servers, small DBs |
| `E` | Memory Optimized | In-memory databases, analytics |
| `F` | Compute Optimized | Batch processing, gaming servers |
| `M` | Memory Extreme | SAP HANA, large in-memory workloads |
| `N` | GPU | ML training, video encoding, CAD |

**Availability Options:**
```bash
# Availability Set (same datacenter, different racks/power)
az vm availability-set create --name myAVSet --resource-group myRG

# Availability Zone (different datacenters in same region)
az vm create \
  --name myVM \
  --resource-group myRG \
  --image Ubuntu2204 \
  --zone 1  # or "1 2 3" for multiple VMs across zones
```

### Azure App Service

**App Service Plan Tiers:**
| Tier | vCPU | RAM | Scaling | SLA |
|------|------|-----|---------|-----|
| Free (F1) | Shared | Shared | None | None |
| Shared (D1) | Shared | Shared | None | None |
| Basic (B1) | Dedicated | 1.75 GB | Manual | 99.9% |
| Standard (S1) | Dedicated | 3.5 GB | Auto-scale | 99.95% |
| Premium (P1v3) | Dedicated | 8 GB | Auto-scale | 99.95% |
| Isolated (I1v2) | Dedicated | 16 GB | Auto-scale | 99.99% |

**Deployment Slots:**
```bash
# Create staging slot
az webapp deployment slot create \
  --name myapp \
  --resource-group myRG \
  --slot staging \
  --configuration-source myapp/production

# Swap staging to production (zero downtime)
az webapp deployment slot swap \
  --name myapp \
  --resource-group myRG \
  --slot staging \
  --target-slot production

# Swap with preview (test before full traffic shift)
az webapp deployment slot swap \
  --name myapp \
  --slot staging \
  --preserve-vnet-content
```

### Azure Kubernetes Service (AKS)

**Control Plane (Azure-managed, free):**
- API server, etcd, scheduler, controller manager
- Automated patching and upgrades
- Multi-AZ deployment option

**Node Pools (customer-managed, pay for VMs):**
```bash
# System pool (critical add-ons: CoreDNS, metrics-server, CNI)
az aks nodepool add \
  --cluster-name myAKS \
  --resource-group myRG \
  --name systempool \
  --mode System \
  --node-count 3 \
  --zones 1 2 3

# User pool (application workloads)
az aks nodepool add \
  --cluster-name myAKS \
  --resource-group myRG \
  --name apppool \
  --mode User \
  --enable-cluster-autoscaler \
  --min-count 3 \
  --max-count 10 \
  --zones 1 2 3
```

### Azure Functions

**Hosting Plans:**
| Plan | Scaling | Cold Start | Max Execution | Pricing |
|------|---------|------------|---------------|---------|
| Consumption | Instant, scale to zero | Yes (2-5s) | 10 min (60 min preview) | Per execution |
| Premium | Pre-warmed instances | No | Unlimited | Per core-second |
| App Service | Manual/auto-scale | No | Unlimited | Per VM |
| Container Apps | KEDA-based | Configurable | Unlimited | Per vCPU/memory |

**Triggers & Bindings:**
```python
# function.json equivalent in Python
import azure.functions as func

def main(req: func.HttpRequest, inputdoc: str, outputQueueItem: func.Out[str]) -> func.HttpResponse:
    # inputdoc is bound to Cosmos DB input
    # outputQueueItem is bound to Queue Storage output
    outputQueueItem.set("processed")
    return func.HttpResponse("OK")
```

***

## 4. Storage Services

### Azure Blob Storage

**Storage Account Tiers:**
| Tier | Latency | Use Case | Min Retention |
|------|---------|----------|---------------|
| Hot | Milliseconds | Frequent access, active data | None |
| Cool | Milliseconds | Infrequent access (monthly) | 30 days |
| Archive | Hours (rehydrate) | Rare access, archival | 180 days |

**Redundancy Options:**
```
LRS (Locally Redundant)     — 3 copies in 1 datacenter
ZRS (Zone Redundant)        — 3 copies across 3 AZs
GRS (Geo Redundant)         — LRS + 3 copies in paired region
RA-GRS (Read Access GRS)    — GRS + read access to secondary
```

**Access Tiers & Lifecycle Management:**
```json
{
  "rules": [
    {
      "name": "MoveToCool",
      "type": "Lifecycle",
      "enabled": true,
      "filters": {
        "blobTypes": ["blockBlob"],
        "prefixMatch": ["logs/"]
      },
      "actions": {
        "baseBlob": {
          "tierToCool": {
            "daysAfterModificationGreaterThan": 30
          }
        }
      }
    },
    {
      "name": "DeleteOldLogs",
      "actions": {
        "baseBlob": {
          "delete": {
            "daysAfterModificationGreaterThan": 365
          }
        }
      }
    }
  ]
}
```

### Azure Files

**Tiers:**
| Tier | IOPS (per share) | Latency | Use Case |
|------|------------------|---------|----------|
| Premium | 100-40,000 | < 10ms | Production, databases |
| Transaction Optimized | High IOPS | Variable | Log aggregation |
| Hot | Standard | Standard | General purpose |
| Cool | Lower | Standard | Archival, backup |

**SMB vs NFS:**
- **SMB:** Windows authentication, AD integration, Windows/Linux clients
- **NFS 4.1:** Linux native, root squash, no AD integration

### Azure Disk Storage

**Disk Types:**
| Type | Max IOPS | Max Throughput | Use Case |
|------|----------|----------------|----------|
| Ultra Disk | 160,000 | 2,000 MB/s | SAP HANA, SQL Server |
| Premium SSD | 75,000 | 900 MB/s | Production VMs |
| Standard SSD | 6,000 | 750 MB/s | Dev/test, light workloads |
| Standard HDD | 500 | 60 MB/s | Backup, cold storage |

**Disk Encryption:**
- **Server-side encryption (SSE):** Enabled by default, Microsoft-managed keys
- **Customer-managed keys (CMK):** Store keys in Azure Key Vault, full control
- **Azure Disk Encryption (ADE):** OS-level encryption using BitLocker (Windows) or DM-Crypt (Linux)

***

## 5. Networking Fundamentals

### Virtual Network (VNet) Architecture

```
VNet: 10.0.0.0/16
├── Subnet: 10.0.1.0/24 (Web tier)
│   ├── NSG: allow 80/443 from internet
│   └── VMs/App Service VNet Integration
├── Subnet: 10.0.2.0/24 (App tier)
│   ├── NSG: allow from Web subnet only
│   └── VMs/Internal Load Balancer
└── Subnet: 10.0.3.0/24 (Data tier)
    ├── NSG: deny all from internet
    └── Private Endpoints (Storage, SQL)
```

**VNet Properties:**
- Address space cannot overlap with peered VNets
- Subnets cannot be resized after creation (must delete/recreate)
- First 4 and last 1 IP in each subnet are reserved by Azure

### Network Security Groups (NSGs)

```bash
# Create NSG
az network nsg create --name web-nsg --resource-group myRG

# Add rules (processed by priority, lowest first)
az network nsg rule create \
  --nsg-name web-nsg \
  --resource-group myRG \
  --name AllowHTTPS \
  --priority 100 \
  --direction Inbound \
  --access Allow \
  --protocol Tcp \
  --destination-port-ranges 443 \
  --source-address-prefixes Internet

az network nsg rule create \
  --nsg-name web-nsg \
  --resource-group myRG \
  --name AllowSSH \
  --priority 110 \
  --direction Inbound \
  --access Allow \
  --protocol Tcp \
  --destination-port-ranges 22 \
  --source-address-prefixes 10.0.0.0/8  # Corporate network only
```

**Default NSG Rules:**
- Inbound: Allow VNet, Allow Azure Load Balancer, Deny All
- Outbound: Allow VNet, Allow Internet, Deny All

***

## 6. Identity & Access Management

### Azure AD (Entra ID) Architecture

```
Tenant (organization boundary)
├── Users (employees, contractors)
├── Groups (security, Microsoft 365)
├── Service Principals (application identities)
├── Managed Identities (Azure resource identities)
└── Applications (app registrations)
```

**Authentication Flow:**
```
User → Azure AD → MFA (if required) → Token → Resource (with RBAC check)
```

### RBAC Role Assignment

```bash
# Built-in roles
az role assignment create \
  --assignee user@company.com \
  --role "Contributor" \
  --scope /subscriptions/<sub-id>/resourceGroups/myRG

# Custom role
az role definition create --role-definition @custom-role.json
```

**Built-in Roles:**
| Role | Permissions | Use Case |
|------|-------------|----------|
| Owner | Full access + RBAC delegation | Subscription admins |
| Contributor | Full access (no RBAC) | DevOps engineers |
| Reader | Read-only | Auditors |
| Network Contributor | Network resources only | Network engineers |
| Storage Blob Data Contributor | Blob read/write | Data engineers |

### Managed Identities

**System-Assigned:**
```bash
# Enabled on VM creation
az vm create \
  --name myVM \
  --resource-group myRG \
  --identity [system]

# VM gets a service principal automatically
# Deleted when VM is deleted
```

**User-Assigned:**
```bash
# Create standalone identity
az identity create \
  --name myManagedIdentity \
  --resource-group myRG

# Assign to multiple resources
az vm identity assign \
  --name myVM \
  --resource-group myRG \
  --identities /subscriptions/.../resourceGroups/myRG/providers/Microsoft.ManagedIdentity/userAssignedIdentities/myManagedIdentity
```

***

## 7. Governance & Compliance

### Management Groups

```
Root Management Group
├── Management Group: Production
│   ├── Subscription: prod-us-east
│   └── Subscription: prod-eu-west
├── Management Group: Non-Production
│   ├── Subscription: dev
│   └── Subscription: test
└── Management Group: Sandbox
    └── Subscription: experimentation
```

### Azure Policy

**Policy Effects:**
| Effect | Behavior |
|--------|----------|
| `Deny` | Block non-compliant resource creation |
| `Audit` | Log violation, allow resource |
| `DeployIfNotExists` | Auto-deploy remediation resource |
| `Modify` | Add/update/remove properties (e.g., tags) |
| `Append` | Add fields during creation |

**Common Policies:**
```bash
# Deny public storage accounts
az policy assignment create \
  --name "deny-public-storage" \
  --scope /subscriptions/<sub-id> \
  --policy "https://raw.githubusercontent.com/Azure/azure-policy/master/built-in-policies/policySetDefinitions/Storage/StorageAccounts_PublicAccess.json"

# Require tags on all resources
az policy assignment create \
  --name "require-tags" \
  --scope /subscriptions/<sub-id> \
  --policy "https://raw.githubusercontent.com/Azure/azure-policy/master/built-in-policies/policyDefinitions/Tags/RequireTag.json"
```

***

## 8. Infrastructure as Code

### Bicep vs ARM vs Terraform

| Feature | ARM JSON | Bicep | Terraform |
|---------|----------|-------|-----------|
| Syntax | Verbose JSON | Clean DSL | HCL |
| State | None (declarative) | None (declarative) | State file required |
| Modularity | Linked templates | Native modules | Modules |
| Provider ecosystem | Azure only | Azure only | Multi-cloud |
| What-if | Native | Native | `terraform plan` |

### Bicep Module Pattern

```bicep
// modules/storage.bicep
param location string = resourceGroup().location
param environment string

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'st${environment}${uniqueString(resourceGroup().id)}'
  location: location
  sku: {
    name: 'Standard_GRS'
  }
  kind: 'StorageV2'
  properties: {
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
    allowBlobPublicAccess: false
  }
}

output storageAccountId string = storageAccount.id
```

```bicep
// main.bicep
param environment string = 'prod'

module storage './modules/storage.bicep' = {
  name: 'storageDeployment'
  params: {
    environment: environment
  }
}

resource appService 'Microsoft.Web/sites@2023-01-01' = {
  name: 'app-${environment}'
  location: resourceGroup().location
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      appSettings: [
        {
          name: 'STORAGE_CONNECTION_STRING'
          value: storage.outputs.storageAccountId
        }
      ]
    }
  }
}
```

***

## 9. Monitoring & Observability

### Azure Monitor Architecture

```
Resources (VMs, AKS, App Service)
    │
    ▼
Diagnostic Settings / Agents
    │
    ▼
Log Analytics Workspace (LAW)
    ├── KQL Queries
    ├── Alerts
    └── Workbooks
    │
    ▼
Azure Monitor Metrics (time-series database)
```

### KQL Query Patterns

```kusto
// Find failed requests in last hour
AppRequests
| where timestamp > ago(1h)
| where success == false
| summarize count() by name, cloud_RoleName

// Top 10 CPU-consuming pods
ContainerInventory
| where TimeGenerated > ago(1h)
| summarize avg(CPUUsage) by ContainerName, Namespace
| top 10 by avg_CPUUsage

// Detect anomaly in error rate
AppExceptions
| where timestamp > ago(24h)
| make-series exceptionCount = count() default = 0 on timestamp from ago(24h) to now() step 1h
| extend (anomalies, score, baseline) = series_decompose_anomalies(exceptionCount)
```

### Alert Rules

```bash
# Create metric alert
az monitor metrics alert create \
  --name "high-cpu-alert" \
  --resource-group myRG \
  --scopes /subscriptions/.../resourceGroups/myRG/providers/Microsoft.Compute/virtualMachines/myVM \
  --condition "avg Percentage CPU > 80" \
  --evaluation-interval PT5M \
  --window-size PT15M \
  --action /subscriptions/.../resourceGroups/myRG/providers/Microsoft.Insights/actionGroups/myActionGroup
```

***

## 10. Cost Management

### Cost Optimization Levers

| Lever | Description | Savings Potential |
|-------|-------------|-------------------|
| Reserved Instances | 1-3 year commitment | 40-70% |
| Spot VMs | Unused capacity auction | 60-90% |
| Right-sizing | Match VM to actual usage | 20-40% |
| Auto-shutdown | Dev/test VMs off nights/weekends | 30-50% |
| Hybrid Benefit | Use existing Windows/SQL licenses | 40% |

### Azure Hybrid Benefit

```bash
# Enable AHB on existing VM (bring your own Windows Server license)
az vm update \
  --name myVM \
  --resource-group myRG \
  --license-type Windows_Server

# Savings: ~40% vs pay-as-you-go Windows VM
```

### Tag-Based Cost Allocation

```bash
# Query costs by tag
az consumption usage list \
  --start-date 2024-01-01 \
  --end-date 2024-01-31 \
  --query "[?tags.environment=='prod']" \
  --output table

# Enforce required tags via policy
az policy assignment create \
  --name "require-cost-center-tag" \
  --scope /subscriptions/<sub-id> \
  --policy "RequireTag" \
  --params '{"tagName": {"value": "cost-center"}}'
```

***

## Key Gotchas

| Gotcha | Detail |
|--------|--------|
| Resource Group delete is permanent | No soft delete — all resources are gone immediately |
| VNet peering is non-transitive | A↔B and B↔C doesn't mean A↔C (need UDRs or Transit VNet) |
| NSG rules are stateful | Return traffic is automatically allowed |
| Private Endpoint needs Private DNS Zone | Without it, resolves to public IP and gets blocked |
| Managed Identity is regional | User-assigned MI must be in same region as resource for best performance |
| AKS node pool upgrade ≠ control plane | Must upgrade control plane first, then node pools |
| Storage account name is global | Must be unique across all of Azure |
| App Service slot settings | Settings marked "Deployment slot setting" don't swap — stay with slot |
