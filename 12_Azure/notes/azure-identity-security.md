# Azure Identity & Security — Deep Dive

## Table of Contents

1. [Entra ID Architecture](#1-entra-id-architecture)
2. [Service Principals & Applications](#2-service-principals--applications)
3. [Managed Identities](#3-managed-identities)
4. [Workload Identity Federation](#4-workload-identity-federation)
5. [RBAC & Authorization](#5-rbac--authorization)
6. [Azure Key Vault](#6-azure-key-vault)
7. [Azure Policy & Governance](#7-azure-policy--governance)
8. [Security Center & Defender](#8-security-center--defender)
9. [Network Security Integration](#9-network-security-integration)
10. [Identity Security Best Practices](#10-identity-security-best-practices)

***

## 1. Entra ID Architecture

### Tenant Hierarchy

```
Entra ID Tenant (organization boundary)
├── Users (employees, contractors, guests)
├── Groups (security, Microsoft 365, dynamic)
├── Applications (app registrations)
├── Service Principals (identity for apps/resources)
├── Managed Identities (Azure resource identities)
├── Devices (Azure AD Join, Hybrid Join)
└── Roles (built-in + custom)
```

**Tenant Properties:**
- Each tenant is isolated — no cross-tenant access by default
- Tenant ID is a GUID (e.g., `72f988bf-86f1-41af-91ab-2d7cd011db47`)
- Primary domain: `tenant.onmicrosoft.com` (can add custom domains)
- A subscription can only be associated with ONE tenant

### Authentication Flow

```
User/Application
      │
      │ 1. Authentication Request
      ▼
Entra ID
      │
      ├── 2. Validate credentials
      ├── 3. MFA challenge (if required)
      ├── 4. Conditional Access check
      │
      │ 5. Issue tokens (access token + ID token)
      ▼
Resource (Azure API, Graph API, SaaS)
      │
      │ 6. Validate token signature + claims
      ▼
Access Granted
```

**Token Types:**
| Token | Purpose | Lifetime |
|-------|---------|----------|
| ID Token | User identity (OIDC) | 1 hour |
| Access Token | Resource access (OAuth 2.0) | 1 hour |
| Refresh Token | Get new access token | 14-90 days |

### Conditional Access Policies

```
Policy Structure:
┌─────────────────────────────────────────┐
│  IF (Conditions)                        │
│  ├── Users/Groups                       │
│  ├── Cloud Apps                         │
│  └── Conditions (location, device, etc) │
│                                         │
│  THEN (Controls)                        │
│  ├── Grant access                       │
│  │   └── Require MFA                    │
│  │   └── Require compliant device       │
│  │   └── Require approved client app    │
│  └── Block access                       │
└─────────────────────────────────────────┘
```

```bash
# Example: Require MFA for all users accessing Azure Portal
# (Created via Graph API or Portal — no CLI support)

{
  "displayName": "Require MFA for Azure Portal",
  "state": "enabled",
  "conditions": {
    "users": {
      "includeUsers": ["All"]
    },
    "applications": {
      "includeApplications": ["797f4846-ba00-4fd7-ba43-dac1f8f63013"]  # Azure Portal app ID
    },
    "locations": {
      "includeLocations": ["All"]
    }
  },
  "grantControls": {
    "operator": "OR",
    "builtInControls": ["mfa"]
  }
}
```

### Privileged Identity Management (PIM)

**Just-In-Time Access:**
- Eligible roles (not active by default)
- Require approval for activation
- Time-bound access (1-8 hours)
- Audit trail of all activations

```bash
# PIM requires Graph API calls (no Azure CLI support)
# Check eligible role assignments
GET https://graph.microsoft.com/v1.0/roleManagement/directory/roleEligibilityScheduleInstances

# Activate a role (user-initiated)
POST https://graph.microsoft.com/v1.0/identityGovernance/privilegedAccess/myEntitlements/roleEligibilityScheduleRequests
```

***

## 2. Service Principals & Applications

### App Registration vs Service Principal

```
Tenant A (Home)              Tenant B (Resource)
┌─────────────────┐          ┌─────────────────┐
│  App            │          │  Service        │
│  Registration   │─────────►│  Principal      │
│  (identity)     │  Trust   │  (projection)   │
└─────────────────┘          └─────────────────┘
      │                            │
      │ Credentials:               │ Permissions:
      │ - Client secret            │ - RBAC roles
      │ - Certificate              │ - API permissions
      │ - Federated (OIDC)         │ - Resource access
```

**App Registration:** The identity definition in the home tenant
**Service Principal:** The instance of that identity in a resource tenant

### Creating Service Principals

```bash
# Create app registration + SP with secret
az ad sp create-for-rbac \
  --name my-app \
  --role Contributor \
  --scopes /subscriptions/<sub-id>/resourceGroups/myRG \
  --sdk-auth

# Output:
{
  "clientId": "xxx",
  "clientSecret": "xxx",  # ⚠️ Store in Key Vault immediately
  "subscriptionId": "xxx",
  "tenantId": "xxx"
}

# Create SP with certificate (more secure)
az ad sp create-for-rbac \
  --name my-app \
  --role Contributor \
  --scopes /subscriptions/<sub-id> \
  --cert @./certificate.pem \
  --keyvault myKV \
  --keyvault-certificate-name myCert
```

### Secret Rotation

```bash
# List credentials
az ad app credential list \
  --id <app-id> \
  --query "[].{keyId:keyId,endDateTime:endDateTime,type:type}"

# Add new secret
az ad app credential reset \
  --id <app-id> \
  --display-name "new-secret" \
  --years 1

# Output contains new secret — rotate in all consumers

# Delete old secret
az ad app credential delete \
  --id <app-id> \
  --key-id <old-key-id>
```

### Certificate-Based Authentication

```bash
# Generate self-signed cert
openssl req -x509 -newkey rsa:4096 \
  -keyout key.pem -out cert.pem \
  -days 365 -nodes \
  -subj "/CN=my-app"

# Convert to PFX (for Azure DevOps)
openssl pkcs12 -export \
  -out cert.pfx \
  -inkey key.pem \
  -in cert.pem

# Upload cert to Key Vault
az keyvault certificate import \
  --vault-name myKV \
  --name myAppCert \
  --file cert.pfx

# Create SP using cert from Key Vault
az ad sp create-for-rbac \
  --name my-app \
  --role Contributor \
  --scopes /subscriptions/<sub-id> \
  --cert @./cert.pem \
  --keyvault myKV \
  --keyvault-certificate-name myAppCert
```

***

## 3. Managed Identities

### System-Assigned vs User-Assigned

```
System-Assigned Managed Identity:
┌─────────────────────────────────────┐
│  Azure Resource (VM, App Service)   │
│  ┌───────────────────────────────┐  │
│  │ Managed Identity (embedded)   │  │
│  │ - Created automatically       │  │
│  │ - Deleted with resource       │  │
│  │ - Cannot be shared            │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘

User-Assigned Managed Identity:
┌─────────────────────────────────────┐
│  Managed Identity (standalone)      │
│  - Created independently            │
│  │
│  ├──► Resource A (VM)               │
│  ├──► Resource B (App Service)      │
│  └──► Resource C (Function)         │
│                                     │
│  - Survives resource deletion       │
│  - Can be shared across resources   │
└─────────────────────────────────────┘
```

### System-Assigned MI Usage

```bash
# Enable on existing VM
az vm identity assign \
  --name myVM \
  --resource-group myRG \
  --identity-type SystemAssigned

# Get the SP object ID (for RBAC)
az vm identity show \
  --name myVM \
  --resource-group myRG \
  --query principalId -o tsv

# Grant Key Vault access
az role assignment create \
  --assignee <principal-id> \
  --role "Key Vault Secrets User" \
  --scope /subscriptions/.../vaults/myKV
```

**VM Access Token Flow:**
```bash
# From inside VM (no credentials needed)
curl 'http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://vault.azure.net' \
  -H "Metadata: true"

# Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJh...",
  "token_type": "Bearer",
  "expires_in": 86399
}

# Use token to access Key Vault
curl -H "Authorization: Bearer <token>" \
  https://myKV.vault.azure.net/secrets/mySecret?api-version=7.4
```

### User-Assigned MI Usage

```bash
# Create identity
az identity create \
  --name myManagedIdentity \
  --resource-group myRG \
  --location eastus

# Get identity properties
IDENTITY_CLIENT_ID=$(az identity show \
  --name myManagedIdentity \
  --resource-group myRG \
  --query clientId -o tsv)

IDENTITY_PRINCIPAL_ID=$(az identity show \
  --name myManagedIdentity \
  --resource-group myRG \
  --query principalId -o tsv)

# Assign to multiple resources
az vm identity assign \
  --name vm1 \
  --resource-group myRG \
  --identities /subscriptions/.../resourceGroups/myRG/providers/Microsoft.ManagedIdentity/userAssignedIdentities/myManagedIdentity

az functionapp identity assign \
  --name myFunction \
  --resource-group myRG \
  --identities /subscriptions/.../myManagedIdentity

# Grant RBAC to the identity
az role assignment create \
  --assignee $IDENTITY_PRINCIPAL_ID \
  --role "Storage Blob Data Contributor" \
  --scope /subscriptions/.../resourceGroups/myRG
```

***

## 4. Workload Identity Federation

### Architecture Overview

```
Kubernetes Cluster (AKS)
┌─────────────────────────────────────────┐
│  Namespace: production                  │
│  ┌─────────────────────────────────┐    │
│  │  Pod                            │    │
│  │  ┌───────────────────────────┐  │    │
│  │  │  ServiceAccount           │  │    │
│  │  │  - Annotation:            │  │    │
│  │  │    azure.workload.identity/ │  │    │
│  │  │    client-id: <MI-ID>     │  │    │
│  │  └───────────────────────────┘  │    │
│  │         │                        │    │
│  │         │ Projected token        │    │
│  │         ▼                        │    │
│  │  ┌───────────────────────────┐  │    │
│  │  │  Azure SDK                │  │    │
│  │  │  - Reads token file       │  │    │
│  │  └───────────────────────────┘  │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
              │
              │ OIDC Token Exchange
              │ (JWT signed by AKS OIDC issuer)
              ▼
Entra ID
┌─────────────────────────────────────────┐
│  Federated Credential                   │
│  - Issuer: <AKS OIDC URL>               │
│  - Subject: system:serviceaccount:ns:sa │
│  - Audience: api://AzureADTokenExchange │
│                                         │
│  Managed Identity                       │
│  - Client ID: <MI-ID>                   │
│  - Linked to Federated Credential       │
└─────────────────────────────────────────┘
              │
              │ Access Token
              ▼
Azure Resource (Key Vault, Storage, SQL)
```

### Setup Steps

```bash
# 1. Enable OIDC issuer on AKS (must be at creation or recreate)
az aks create \
  --resource-group myRG \
  --name myAKS \
  --enable-oidc-issuer \
  --enable-workload-identity \
  --network-plugin azure \
  --network-policy calico

# Get OIDC issuer URL
AKS_OIDC_ISSUER=$(az aks show \
  --resource-group myRG \
  --name myAKS \
  --query oidcIssuerProfile.issuerUrl \
  -o tsv)

echo "OIDC Issuer: $AKS_OIDC_ISSUER"
# Output: https://eastus.oide.issuer.azure.net/9b98a00f-xxxx-xxxx-xxxx-xxx/

# 2. Create User-Assigned Managed Identity
az identity create \
  --name myWorkloadId \
  --resource-group myRG \
  --location eastus

IDENTITY_CLIENT_ID=$(az identity show \
  --name myWorkloadId \
  --resource-group myRG \
  --query clientId -o tsv)

IDENTITY_OBJECT_ID=$(az identity show \
  --name myWorkloadId \
  --resource-group myRG \
  --query principalId -o tsv)

# 3. Create Federated Credential
az identity federated-credential create \
  --name myFedCred \
  --identity-name myWorkloadId \
  --resource-group myRG \
  --issuer $AKS_OIDC_ISSUER \
  --subject "system:serviceaccount:production:my-serviceaccount" \
  --audience api://AzureADTokenExchange

# 4. Grant MI access to Key Vault
az role assignment create \
  --assignee $IDENTITY_OBJECT_ID \
  --role "Key Vault Secrets User" \
  --scope /subscriptions/.../vaults/myKV
```

### Kubernetes Configuration

```yaml
# ServiceAccount with Workload Identity annotation
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-serviceaccount
  namespace: production
  annotations:
    azure.workload.identity/client-id: "<managed-identity-client-id>"
---
# Pod using Workload Identity
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
  namespace: production
  labels:
    azure.workload.identity/use: "true"  # Required for webhook injection
spec:
  serviceAccountName: my-serviceaccount
  containers:
    - name: my-app
      image: myregistry.azurecr.io/my-app:v1
      env:
        # SDK automatically picks up these injected env vars:
        # AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_FEDERATED_TOKEN_FILE
        - name: KEY_VAULT_URL
          value: "https://myKV.vault.azure.net/"
```

### Python SDK Usage

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# DefaultAzureCredential automatically uses Workload Identity
# when running in AKS with federated identity
credential = DefaultAzureCredential()

secret_client = SecretClient(
    vault_url="https://myKV.vault.azure.net/",
    credential=credential
)

secret = secret_client.get_secret("database-password")
print(f"Secret value: {secret.value}")
```

### Federated Credential Options

```bash
# Single namespace, single SA (most restrictive)
az identity federated-credential create \
  --name cred1 \
  --subject "system:serviceaccount:production:my-sa"

# All SAs in a namespace
az identity federated-credential create \
  --name cred2 \
  --subject "system:serviceaccount:production:*"

# All SAs in cluster (least restrictive - not recommended)
az identity federated-credential create \
  --name cred3 \
  --subject "system:serviceaccount:*:*"

# Multiple subjects (for multiple namespaces/clusters)
az identity federated-credential create \
  --name cred4 \
  --subject "system:serviceaccount:production:*,system:serviceaccount:staging:*"
```

***

## 5. RBAC & Authorization

### Built-in Roles

| Role | Permissions | Typical Use |
|------|-------------|-------------|
| Owner | Full access + RBAC delegation | Subscription admins |
| Contributor | Full access (no RBAC) | DevOps engineers |
| Reader | Read-only | Auditors, support |
| Network Contributor | Network resources only | Network engineers |
| Storage Blob Data Contributor | Blob read/write/delete | Data engineers |
| Storage Blob Data Reader | Blob read only | Analysts |
| Key Vault Secrets User | Secret read only | Applications |
| Key Vault Secrets Officer | Secret CRUD | Security admins |
| Kubernetes Cluster User | AKS read + kubectl access | Developers |
| Kubernetes Cluster Admin | AKS full control | Platform engineers |

### Custom Roles

```json
// custom-role.json
{
  "Name": "AKS Namespace Admin",
  "Id": null,
  "IsCustom": true,
  "Description": "Can manage resources in specific AKS namespaces",
  "Actions": [
    "Microsoft.ContainerService/managedClusters/read",
    "Microsoft.ContainerService/managedClusters/listClusterUserCredential/action",
    "Microsoft.ContainerService/managedClusters/accessProfiles/read"
  ],
  "NotActions": [],
  "DataActions": [
    "Microsoft.ContainerService/managedClusters/user/listClusterUserCredential/action"
  ],
  "NotDataActions": [],
  "AssignableScopes": [
    "/subscriptions/<sub-id>/resourceGroups/myRG"
  ]
}
```

```bash
# Create custom role
az role definition create --role-definition custom-role.json

# Assign custom role
az role assignment create \
  --assignee user@company.com \
  --role "AKS Namespace Admin" \
  --scope /subscriptions/.../resourceGroups/myRG
```

### Azure AD Pod Identity (Deprecated) → Workload Identity Migration

```bash
# Old AAD Pod Identity (deprecated)
apiVersion: v1
kind: Pod
metadata:
  annotations:
    aadpodidentity/binding: my-binding  # ❌ Deprecated
spec:
  containers: [...]

# New Workload Identity (recommended)
apiVersion: v1
kind: Pod
metadata:
  labels:
    azure.workload.identity/use: "true"  # ✅ Current
spec:
  serviceAccountName: my-sa
  containers: [...]
```

***

## 6. Azure Key Vault

### Key Vault Architecture

```
Key Vault
├── Keys (HSM-backed or software)
│   ├── RSA/EC keys for encryption
│   └── Certificate keys for TLS
│
├── Secrets (strings, passwords, connection strings)
│   ├── Versioned (each update creates new version)
│   └── Content-type hints
│
└── Certificates (X.509 certificates)
    ├── Auto-renewal policies
    └── Integrated with Key Vault Keys
```

**Access Policies vs RBAC:**
| Feature | Access Policies | RBAC |
|---------|----------------|------|
| Granularity | Key/Secret/Certificate level | Vault level |
| Scope | Single vault | Subscription-wide |
| Azure AD integration | Limited | Full |
| Recommendation | Legacy | **Recommended** |

### Access Control (RBAC)

```bash
# Grant secret read access
az role assignment create \
  --assignee <sp-object-id> \
  --role "Key Vault Secrets User" \
  --scope /subscriptions/.../vaults/myKV

# Grant secret CRUD + management
az role assignment create \
  --assignee <sp-object-id> \
  --role "Key Vault Secrets Officer" \
  --scope /subscriptions/.../vaults/myKV

# Grant key operations (encrypt/decrypt/sign)
az role assignment create \
  --assignee <sp-object-id> \
  --role "Key Vault Crypto Officer" \
  --scope /subscriptions/.../vaults/myKV
```

### Secret Management

```bash
# Create secret
az keyvault secret set \
  --vault-name myKV \
  --name database-password \
  --value "SuperSecret123!"

# Create secret from file
az keyvault secret set \
  --vault-name myKV \
  --name tls-private-key \
  --file ./private.key

# Get secret value
az keyvault secret show \
  --vault-name myKV \
  --name database-password \
  --query value -o tsv

# Get all versions
az keyvault secret version list \
  --vault-name myKV \
  --name database-password

# Recover deleted secret (soft delete)
az keyvault secret recover \
  --vault-name myKV \
  --name database-password
```

### Key Vault Networking

```bash
# Create Key Vault with private endpoint only
az keyvault create \
  --name myKV \
  --resource-group myRG \
  --location eastus \
  --sku premium \
  --network-acls default-action=Deny \
  --bypass AzureServices

# Enable private endpoint
az network private-endpoint create \
  --name pe-keyvault \
  --resource-group myRG \
  --vnet-name myVNet \
  --subnet private-endpoints \
  --private-connection-resource-id /subscriptions/.../vaults/myKV \
  --group-id vault \
  --connection-name kv-connection

# Create Private DNS Zone
az network private-dns zone create \
  --resource-group myRG \
  --name "privatelink.vaultcore.azure.net"

az network private-dns link vnet create \
  --resource-group myRG \
  --name myvnet-link \
  --zone-name "privatelink.vaultcore.azure.net" \
  --vnet-name myVNet \
  --registration-enabled false
```

### Key Vault Managed HSM

```bash
# Create Managed HSM (dedicated HSM hardware)
az keyvault create \
  --name myHSM \
  --resource-group myRG \
  --location eastus \
  --sku Premium \
  --administrators <admin-object-id> \
  --enable-purge-protection true \
  --soft-delete-retention 90

# Managed HSM features:
# - FIPS 140-2 Level 3 validated
# - Single-tenant hardware
# - RBAC only (no access policies)
# - Purge protection (cannot be bypassed)
```

***

## 7. Azure Policy & Governance

### Policy Initiative Structure

```
Management Group
    │
    ├── Policy Initiative: Azure Security Benchmark
    │   ├── Policy: Require encryption at rest
    │   ├── Policy: Deny public endpoints
    │   └── Policy: Enable diagnostic logging
    │
    └── Policy Initiative: AKS Security Baseline
        ├── Policy: Deny privileged containers
        ├── Policy: Require network policies
        └── Policy: Enable Azure Defender
```

### Built-in AKS Policies

```bash
# Assign built-in AKS security baseline
az policy assignment create \
  --name "aks-security-baseline" \
  --scope /subscriptions/<sub-id> \
  --policy-set-definition "a8640138-9b0a-4a28-b8cb-1666c838647d"

# Common AKS policies:
# - Deny privileged containers
# - Require read-only root filesystem
# - Restrict host network access
# - Enable Azure Defender for Kubernetes
```

### Custom Policy for Kubernetes (Gatekeeper)

```json
// deny-privileged-containers.json
{
  "mode": "Microsoft.Kubernetes.Data",
  "policyRule": {
    "if": {
      "allOf": [
        {
          "field": "type",
          "equals": "Microsoft.Kubernetes.Data/pods"
        },
        {
          "field": "Microsoft.Kubernetes.Data/pods.spec.containers[*].securityContext.privileged",
          "equals": true
        }
      ]
    },
    "then": {
      "effect": "deny"
    }
  },
  "parameters": {}
}
```

```bash
# Create custom policy
az policy definition create \
  --name "deny-privileged-containers" \
  --mode "Microsoft.Kubernetes.Data" \
  --rules @deny-privileged-containers.json \
  --category "Kubernetes"

# Assign to subscription
az policy assignment create \
  --name "no-privileged-containers" \
  --scope /subscriptions/<sub-id> \
  --policy "deny-privileged-containers"
```

### Policy Effects Reference

| Effect | Behavior | Use Case |
|--------|----------|----------|
| `Deny` | Block creation/update | Security requirements |
| `Audit` | Log violation, allow | Compliance monitoring |
| `DeployIfNotExists` | Auto-deploy remediation | Enable diagnostic settings |
| `Modify` | Add/update/remove properties | Add tags, enable encryption |
| `Append` | Add fields during creation | Add required tags |
| `Disabled` | No effect | Temporarily disable policy |

***

## 8. Security Center & Defender

### Microsoft Defender for Cloud Tiers

| Tier | Features | Cost |
|------|----------|------|
| Free | CSPM, secure score, recommendations | $0 |
| Defender for Servers | Threat detection, vulnerability scanning | $15/server/month |
| Defender for Containers | Runtime threat detection, image scanning | $2/cluster/day |
| Defender for SQL | SQL vulnerability assessment | 15% of SQL cost |
| Defender for Key Vault | Malicious access detection | $0.03/vault/day |

### Enable Defender for Containers

```bash
# Enable at subscription level
az security pricing create \
  --name KubernetesService \
  --pricing-tier Standard \
  --subscription <sub-id>

# Check pricing tier
az security pricing show \
  --name KubernetesService

# View secure score
az security secure-score control list \
  --subscription <sub-id>
```

### Security Alerts

```bash
# List active alerts
az security alert list \
  --subscription <sub-id>

# Dismiss false positive
az security alert update \
  --name "Alert_GUID" \
  --subscription <sub-id> \
  --status Dismissed \
  --dismissal-reason "False positive" \
  --dismissal-text "Verified as legitimate admin activity"
```

***

## 9. Network Security Integration

### Private Link Security Pattern

```
Internet → Front Door → Application Gateway → Private Endpoint → PaaS Service
                                                      │
                                                      ▼
                                              VNet: 10.0.0.0/16
                                              ┌─────────────────┐
                                              │ Private DNS Zone│
                                              │ privatelink.*   │
                                              └─────────────────┘
```

**Security Benefits:**
- Traffic stays on Microsoft backbone (no public internet)
- PaaS service appears as private IP in VNet
- NSG can control access to Private Endpoint subnet
- Service endpoints not needed (Private Link provides isolation)

### Azure Firewall IDPS

```bash
# Enable IDPS in Premium Firewall
az network firewall policy create \
  --name myFwPolicy \
  --resource-group hub-rg \
  --sku Premium \
  --mode Alert  # or Deny

# IDPS signatures cover:
# - Known malware
# - Exploit attempts
# - Command & control traffic
# - Vulnerability scanning
```

***

## 10. Identity Security Best Practices

### Service Principal Security

| Practice | Implementation |
|----------|----------------|
| Use certificates over secrets | `az ad sp create-for-rbac --cert @cert.pem` |
| Rotate secrets every 90 days | Automate with Key Vault + Logic Apps |
| Scope permissions minimally | `--scopes /subscriptions/.../resourceGroups/myRG` |
| Use Managed Identity when possible | No credentials to manage |
| Store secrets in Key Vault | Never in code or environment variables |

### Workload Identity Checklist

- [ ] OIDC issuer enabled on AKS cluster
- [ ] ServiceAccount annotated with client ID
- [ ] Pod labeled with `azure.workload.identity/use: "true"`
- [ ] Federated credential created in Entra ID
- [ ] Managed Identity has required RBAC roles
- [ ] Subject claim matches namespace and SA name
- [ ] No static credentials in code or config files

### Key Vault Security Checklist

- [ ] RBAC enabled (not access policies)
- [ ] Private endpoint configured (no public access)
- [ ] Private DNS Zone linked to VNet
- [ ] Soft delete enabled (90-day retention)
- [ ] Purge protection enabled (production)
- [ ] Diagnostic logging to Log Analytics
- [ ] Firewall rules restrict access
- [ ] Secrets versioned and recoverable

***

## Key Gotchas

| Gotcha | Detail |
|--------|--------|
| Service Principal secret in output | Store in Key Vault immediately after `create-for-rbac` |
| Federated credential subject mismatch | Must exactly match `system:serviceaccount:namespace:name` |
| Key Vault RBAC vs Access Policy | RBAC is recommended; access policies are legacy |
| Managed Identity is regional | User-assigned MI should be in same region as resource |
| OIDC issuer URL is case-sensitive | Copy exactly from `az aks show --query oidcIssuerProfile.issuerUrl` |
| Private Endpoint needs DNS configuration | Without Private DNS Zone, resolves to public IP |
| PIM requires Azure AD Premium P2 | Not available in Free or P1 tiers |
| Custom policy mode for Kubernetes | Must use `Microsoft.Kubernetes.Data` mode |
| Defender pricing is per-resource | Clusters, VMs, SQL databases billed separately |
| Workload Identity requires Azure SDK | Application must use `DefaultAzureCredential` or similar |
