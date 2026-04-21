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
