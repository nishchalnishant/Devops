## Medium

**9. What is the difference between an Azure Managed Identity and a Service Principal?**

A Service Principal is an identity created for use with applications, hosted services, and automated tools to access Azure resources — requiring you to explicitly manage and rotate its secret or certificate. A Managed Identity is a feature of Microsoft Entra ID that provides an automatically managed identity in Azure. You don't manage credentials; Azure handles the lifecycle of the identity. System-Assigned Managed Identities die when the resource is deleted; User-Assigned ones persist and can be shared across multiple resources.

**10. How do you securely manage Terraform state for Azure infrastructure?**

Terraform state should be managed in an Azure Storage Account Blob container using the `azurerm` backend. To secure it: lock down the Storage Account's network access with private endpoints, use RBAC to restrict access to the state blob to the pipeline's Managed Identity, enable Soft Delete and point-in-time restore for recovery, and rely on Azure blob leases to prevent concurrent state corruption.

**11. What are the pros and cons of using Azure Logic Apps vs. Azure Functions?**

Azure Functions is a code-first serverless compute service — better for complex, custom logic, high-performance data processing, and developers preferring C#, Python, or Node.js. Azure Logic Apps is a designer-first, visual orchestration service — it excels at workflow automation and connecting third-party systems using hundreds of pre-built connectors. Logic Apps becomes unwieldy for highly complex nested programming logic; Functions require more development effort for simple integrations.

**12. How would you implement a Blue-Green deployment for an Azure App Service?**

Azure App Service provides Deployment Slots. Create a `staging` slot identical to `production`. The CI/CD pipeline deploys new code to `staging`. Once staging passes smoke tests, perform a Swap operation in Azure — Azure routes production traffic to the new instances, and the old production becomes the staging slot. If an issue occurs, swap back instantly. Traffic routing percentages can also be used for canary-style gradual shifts.

**13. Why is Bicep gaining popularity over ARM templates?**

ARM templates are JSON-based, verbose, and difficult to read at scale without extensive tooling. Bicep is a DSL created by Microsoft specifically for Azure. It offers cleaner syntax, transparent compilation into standard ARM JSON, modularity via the `module` block, strong type checking, and day-zero support for new Azure features without waiting for an external provider update. Bicep is the recommended path for new Azure IaC development.

**14. What is Azure Key Vault and how do you integrate it with a Kubernetes workload?**

Azure Key Vault stores secrets, certificates, and keys. To integrate with Kubernetes, use the Secrets Store CSI Driver with the Azure Key Vault provider — it mounts secrets from Key Vault directly into pods as volume files or environment variables. Combined with Azure Workload Identity, the pod authenticates to Key Vault via a federated Kubernetes ServiceAccount token, eliminating stored credentials entirely.

**15. What is the difference between Azure DevOps Service Connections and GitHub OIDC?**

An Azure DevOps Service Connection stores credentials (Service Principal client secret or certificate) in Azure DevOps to authenticate to external resources. GitHub OIDC uses federated identity — no stored credentials at all. The GitHub Actions workflow requests a short-lived token from Azure by presenting a JWT signed by GitHub's OIDC endpoint. OIDC is preferred because credentials cannot leak when there is nothing stored, and tokens expire automatically after the job completes.

**16. What is Azure Policy and how does it enforce compliance?**

Azure Policy evaluates resources against defined rules and effects. Effects include `Deny` (block non-compliant resource creation), `Audit` (log non-compliance without blocking), `DeployIfNotExists` (automatically remediate by deploying a resource), and `Modify` (add or update tags). Policies are assigned to scopes (management group, subscription, resource group) and evaluated at creation time and during compliance scans. Policy initiatives bundle multiple policies for standards like CIS benchmarks.

***


**17. Walk through the Azure Workload Identity flow for a pod accessing Key Vault.**

1. AKS cluster is created with `--enable-oidc-issuer` and `--enable-workload-identity`. The cluster exposes an OIDC discovery endpoint.
2. A User-Assigned Managed Identity is created in Azure. An Entra ID Federated Credential is added to it: `issuer = <cluster OIDC URL>`, `subject = system:serviceaccount:<namespace>:<sa-name>`.
3. The Kubernetes ServiceAccount is annotated with `azure.workload.identity/client-id: <managed-identity-client-id>`.
4. The pod spec includes the label `azure.workload.identity/use: "true"`. The webhook injects `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_FEDERATED_TOKEN_FILE` env vars and mounts a projected service account token.
5. At runtime, the Azure SDK reads the projected token file, exchanges it at the Entra ID token endpoint for an Azure access token, and presents it to Key Vault. Key Vault validates RBAC: the Managed Identity must have `Key Vault Secrets User` on the vault.

No static credentials stored anywhere in this flow.

**18. Compare Azure CNI and Azure CNI Overlay networking in AKS.**

| Dimension | Azure CNI (classic) | Azure CNI Overlay |
|-----------|--------------------|--------------------|
| Pod IP source | VNet subnet — real IPs consumed | Overlay network — CIDR not from VNet |
| VNet IP consumption | High — nodes × max_pods IPs reserved | Low — only node IPs from VNet |
| Pod reachability from VNet | Direct (Private Endpoints, VMs see pods) | Requires explicit NAT or routes |
| Windows pools | Supported | Supported (AKS 1.28+) |
| Network policy | Calico, Azure NPM | Calico, Azure NPM |
| Use case | Strict private pod connectivity, Azure Firewall inspection of pod traffic | Large clusters where IP exhaustion is a concern |

Azure CNI Overlay is the recommended default for most new clusters — it avoids VNet IP exhaustion while preserving enterprise networking.

**19. What are the AKS upgrade strategies and what is the recommended order?**

AKS Kubernetes version upgrades must follow a strict order:

1. **Control plane first:** `az aks upgrade --kubernetes-version X.Y` upgrades the API server, etcd, and controller manager. The cluster remains available during this phase.
2. **Node pools individually:** Each node pool can then be upgraded separately, allowing you to upgrade system node pools before application node pools, and to test workloads between upgrades.
3. **Upgrade behavior:** Node surge during upgrade: AKS creates a new node (`max-surge` configurable, default 1), cordons and drains an old node, then deletes it. Set `--max-surge` to a higher value (e.g., 33%) for faster upgrades at the cost of temporary over-provisioning.
4. **Node image upgrades:** Separate from Kubernetes version — OS security patches via `az aks nodepool upgrade --node-image-only` without changing Kubernetes version. Can be automated with `--enable-auto-upgrade` set to `node-image`.

Attempting to upgrade node pools past the control plane version will fail — Azure enforces n-2 skew maximum.

**20. How do you implement zero-downtime blue-green node pool upgrades in AKS?**

Instead of in-place node pool upgrades, provision a second "green" node pool at the target Kubernetes version and node image:

```bash
az aks nodepool add \
  --cluster-name myAKS -g myRG \
  --name greenpool \
  --kubernetes-version 1.30.0 \
  --node-count 5 \
  --node-vm-size Standard_D4s_v3
```

Cordon the old "blue" pool: `kubectl cordon <old-node>`. Rescheduling drains workloads naturally as the HPA or deployment controller places new pods on green nodes. Once all pods are running on green, drain the blue pool completely and delete it. This gives complete rollback capability: if green is unstable, uncordon blue nodes and the scheduler fills them again.

**21. What is the Application Gateway Ingress Controller (AGIC) and when would you use it over nginx-ingress?**

AGIC is an AKS add-on that uses an Azure Application Gateway as the L7 ingress controller. Benefits: native Azure WAF integration, TLS termination with Key Vault certificate references, native Azure DDoS protection, and no extra VMs to manage. Limitations: single Application Gateway per AGIC instance, higher cost than nginx, slower policy propagation than in-cluster controllers.

Use nginx-ingress (or Traefik) when: cost sensitivity is high, you need advanced ingress features (canary weights, custom Lua), or multi-cluster ingress routing. Use AGIC when: enterprise WAF compliance is required, you want native Azure WAF policies without maintaining WAF rules in nginx annotations, and you're already in Azure's networking stack.

**22. How do Azure DevOps Environments and Approval Gates work?**

An ADO Environment is a deployment target (Kubernetes namespace, virtual machines, or abstract). Pipelines reference environments in `deployment` jobs. You configure checks on environments:
- **Manual approval:** One or more designated users must approve before the deployment job starts.
- **Branch control:** Only pipelines running from specific branches can deploy.
- **Invoke Azure Function / REST API:** Pre-deployment automated quality gate.
- **Business hours:** Only allow deployments during specified time windows.

The environment maintains a deployment history and links to commit SHA, making it auditable. This is how you gate production deployments without injecting approval logic into pipeline YAML.

**23. How would you structure a multi-stage Azure DevOps pipeline for prod with mandatory approvals?**

```yaml
stages:
- stage: Build
  jobs:
  - job: BuildAndTest
    steps:
    - script: dotnet test

- stage: Deploy_Staging
  dependsOn: Build
  jobs:
  - deployment: DeployStaging
    environment: staging
    strategy:
      runOnce:
        deploy:
          steps:
          - task: AzureWebApp@1
            inputs:
              azureSubscription: 'staging-sc'
              appName: 'myapp-staging'

- stage: Deploy_Production
  dependsOn: Deploy_Staging
  condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
  jobs:
  - deployment: DeployProd
    environment: production     # manual approval gate configured in ADO UI
    strategy:
      runOnce:
        deploy:
          steps:
          - task: AzureWebApp@1
            inputs:
              azureSubscription: 'prod-sc'
              appName: 'myapp-prod'
```

The `production` environment has a manual approval check — the pipeline pauses and notifies approvers before `DeployProd` starts.

**24. What is Azure Container Apps and how does it compare to AKS?**

| Dimension | Azure Container Apps (ACA) | AKS |
|-----------|---------------------------|-----|
| Abstraction level | Serverless — no node management | Full Kubernetes cluster management |
| Scaling | KEDA built-in, scale-to-zero supported | KEDA add-on, cluster autoscaler separate |
| Kubernetes access | None (fully abstracted) | Full `kubectl` access |
| Networking | Managed VNet integration | Full CNI control |
| Cost model | Consumption-based | Node VMs always running |
| Use case | Stateless microservices, event-driven apps | Complex workloads, stateful apps, custom admission, multi-tenant |

ACA is appropriate when you want container hosting without cluster operations overhead. AKS is appropriate when you need Kubernetes primitives: StatefulSets, custom operators, admission webhooks, or complex networking.

**25. How do you implement Azure Policy to enforce AKS security baselines?**

Use the built-in AKS policy initiative (Azure Security Benchmark or CIS AKS) and assign it at the management group scope. Key individual policies:

```bash
# Assign built-in AKS security initiative
az policy assignment create \
  --name "aks-security-baseline" \
  --scope /subscriptions/<sub-id> \
  --policy-set-definition /providers/Microsoft.Authorization/policySetDefinitions/a8640138-9b0a-4a28-b8cb-1666c838647d

# Custom: deny privileged containers
az policy definition create \
  --name "deny-privileged-containers" \
  --mode Microsoft.Kubernetes.Data \
  --rules @deny-privileged.json \
  --params @deny-privileged-params.json
```

For custom policies, mode `Microsoft.Kubernetes.Data` applies Gatekeeper-style OPA policies at the Kubernetes admission level — evaluated at pod creation inside the cluster, not just at ARM deployment time.

**26. What is Azure Managed Prometheus and how does it integrate with AKS?**

Azure Monitor managed service for Prometheus stores metrics in an Azure Monitor workspace (a Prometheus-compatible remote write endpoint). Enable it on AKS:

```bash
az aks update --name myAKS -g myRG \
  --enable-azure-monitor-metrics \
  --azure-monitor-workspace-resource-id <workspace-id>
```

This deploys the metrics addon (a DaemonSet and replica set) that scrapes cluster metrics and remote-writes to the workspace. Grafana (Azure Managed Grafana or self-hosted) queries the workspace via the Prometheus-compatible API. Managed Prometheus eliminates the need to run and scale your own Prometheus instance while retaining PromQL compatibility.

**27. How does Azure Cost Management work with AKS multi-tenant clusters?**

AKS exposes cost at the node pool / cluster level via Azure Cost Management — it does not natively attribute cost per namespace or per team. Patterns for chargeback:

1. **Dedicated node pools per team** with node labels → Cost Management tags on node pool VMs → allocate by tag.
2. **Kubecost** (OSS or Azure sponsored): runs inside the cluster, computes per-namespace/pod cost based on request allocations and Azure pricing API.
3. **Azure Monitor Container Insights cost analysis** (preview): namespace-level CPU/memory allocation data from Log Analytics, correlated with Azure pricing.

Tag all Azure resources (node pools, disks, load balancers) with `team` and `cost-center` tags enforced via Azure Policy to enable reliable cost attribution.

**28. What is Azure Private DNS Resolver and when is it needed?**

Azure Private DNS Resolver is a managed DNS forwarder running inside your VNet. You need it when:

1. **Custom DNS servers exist** (on-premises DNS via ExpressRoute/VPN) that need to resolve Azure Private DNS Zone names (e.g., `privatelink.blob.core.windows.net`). The on-premises DNS cannot resolve Azure Private DNS Zones directly — you configure conditional forwarders on the on-premises DNS pointing to the Private DNS Resolver inbound endpoint IP.
2. **Hub-and-Spoke with shared DNS**: DNS Resolver in the Hub resolves Private DNS Zones linked to the Hub VNet, and spoke VNets use the Resolver as their DNS server — avoiding the need to link every Private DNS Zone to every spoke VNet individually.

Without it, the workaround is manual conditional forwarding rules on each custom DNS server — brittle at scale.
