## Medium

**7. What is an ArgoCD ApplicationSet and when would you use it?**

An ApplicationSet is a controller that generates multiple ArgoCD Applications from a single template, using generators such as List, Git, Matrix, or Cluster. Use it when deploying the same application across multiple clusters or environments without defining a separate Application resource for each. Example: a cluster generator automatically creates an Application per registered cluster, deploying a base monitoring stack to all 200 clusters.

**8. Compare ArgoCD and Flux. What are the key architectural differences?**

- **ArgoCD:** More centralized and opinionated. Has a comprehensive UI, and the `Application` CRD is the central concept. Better for multi-tenant GitOps platforms with rich self-service.
- **Flux:** More modular, following the Unix philosophy. It's a collection of specialized controllers (for sourcing from Git, applying manifests, handling Helm releases) composed together. Lighter weight, no built-in UI, better for organizations that prefer CLI- and Git-driven workflows.

**9. How do you manage secrets in a GitOps workflow where manifests are in a Git repository?**

Use Sealed Secrets or External Secrets Operator:

- **Sealed Secrets (Bitnami):** A controller in the cluster holds a private key. Developers encrypt Secrets with `kubeseal` using the controller's public key. The resulting `SealedSecret` is safe to commit. The controller decrypts it into a real Secret at apply time.
- **External Secrets Operator:** `ExternalSecret` resources reference secrets in Vault, AWS Secrets Manager, or Azure Key Vault by path. The controller fetches and syncs secret values into Kubernetes Secrets. No encrypted data stored in Git.

**10. What is Flagger and how does it enable progressive delivery on top of a service mesh?**

Flagger is a progressive delivery operator that automates canary, A/B, and blue-green deployments:

1. Flagger watches for changes to a `Deployment`.
2. When it sees a new version, it creates a canary Deployment and configures the service mesh (Istio `VirtualService`) to send a small traffic percentage to it.
3. It runs an automated analysis loop querying Prometheus SLIs.
4. If metrics are healthy, it gradually increases traffic to the canary. If not, it automatically rolls back.

**11. What is progressive delivery and how does it improve on blue-green deployments?**

Blue-green is binary: 0% or 100% traffic on the new version. Progressive delivery introduces gradual traffic shifting with automated metric-gated promotion:
- **Canary releases:** 5% → 20% → 50% → 100% with automated promotion criteria.
- **Feature flags:** Enable for 1% of users, then internal employees, then geographic regions.
- **Traffic mirroring:** Copy 100% of live traffic to the new version without serving real responses — test under production load with zero risk.

**12. What is Kustomize and how does it differ from Helm?**

Kustomize applies patch overlays to a base set of Kubernetes YAML files without templating. It uses `kustomization.yaml` to reference a base and layer environment-specific patches on top. Helm is a full package manager with Go templating, versioned charts, and a release lifecycle (`install`, `upgrade`, `rollback`). Kustomize is lighter and better for simple per-environment customization; Helm is better for distributing complex applications with many configurable parameters.

***

