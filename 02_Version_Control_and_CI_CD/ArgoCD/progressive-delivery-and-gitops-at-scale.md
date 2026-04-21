# Progressive Delivery & GitOps at Scale (7 YOE)

GitOps is the industry-standard way to manage Kubernetes states. For a 7 YOE engineer, the focus moves from "managing one app" to "managing a fleet of clusters" and automating the verification of canary deployments.

---

## 1. Multi-Cluster GitOps (ApplicationSets)

Managing 50 clusters manually in the ArgoCD UI is impossible. You must use the **App-of-Apps pattern** or **ArgoCD ApplicationSets**.

### ApplicationSets
An ApplicationSet is a generator that creates multiple ArgoCD `Application` objects automatically based on a source of truth.
- **Cluster Generator:** Whenever a new cluster is added to the enterprise (e.g., in AWS/Azure), the ApplicationSet automatically deploys the "Standard Platform Stack" (Logging, Monitoring, Security) to that cluster.
- **Git Generator:** It scans your repository for directories. If you add a new subfolder `apps/gateway`, ArgoCD automatically detects it and creates a new Deployment.

---

## 2. Progressive Delivery (Argo Rollouts)

A 7 YOE engineer never accepts a standard "Rolling Update" for critical production apps. A rolling update replaces old pods with new ones blindly—if the new code has a 200ms latency spike, the rolling update will still finish 100%, and you will have a production incident.

### The Argo Rollouts Canary
Argo Rollouts replaces the standard Kubernetes `Deployment`. It allows you to:
1. Deploy v2 to 5% of traffic.
2. **Analysis Stage:** It automatically queries Prometheus. "Is the 5xx error rate > 1%?" or "Is the P99 latency > 300ms?"
3. **Automated Promotion:** If the metrics are healthy for 10 minutes, it automatically scales to 20%, then 50%, then 100%.
4. **Automated Rollback:** If the metrics fail, it flips the traffic back to v1 instantly before the human engineers even receive the Slack alert.

---

## 3. The GitOps Secret Problem

You cannot store plain-text secrets in Git. A 7 YOE engineer uses **External Secrets Operator (ESO)**.

### The ESO Workflow
1. The SRE/Security team stores the secret in a dedicated vault (HashiCorp Vault, AWS Secrets Manager, or Azure Key Vault).
2. The Git repo contains a `SecretStore` and an `ExternalSecret` YAML (public, non-sensitive).
3. The External Secret Operator running inside the Kubernetes cluster "pulls" the secret from the Vault and injects it as a standard native Kubernetes Secret.
4. **Benefit:** The secret is never in Git, and the developer never touches the production password.

---

## 4. GitOps vs. Infrastructure (Crossplane)

The final evolution of GitOps. Why use Terraform for infra and ArgoCD for apps? 
A Senior Engineer uses **Crossplane** to manage both in one place.
- **HCL-less Infra:** You define your Database as a Kubernetes YAML (`kind: RDSInstance`). 
- ArgoCD manages that YAML. 
- If you change the `storage_size` in Git, ArgoCD syncs the YAML, and Crossplane automatically resizes the real cloud database.
- Everything—infrastructure and application—lives in one GitOps control loop.
