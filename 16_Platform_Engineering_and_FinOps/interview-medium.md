## Medium

**6. What is the difference between an IDP and a CI/CD pipeline?**

A CI/CD pipeline is a workflow for building, testing, and deploying a single service. An IDP abstracts all platform complexity — compute, networking, secrets, databases, monitoring, environments — behind a developer-facing interface. The IDP coordinates CI/CD, GitOps, and infrastructure provisioning as an integrated workflow, automating what currently requires manual tickets and handoffs between teams.

**7. How do you enforce cloud resource tagging across 50 engineering teams?**

Tagging taxonomy (minimum required tags):
```
team: payments
environment: production
project: checkout-v2
managed-by: terraform
owner: john.doe@co.com
```

Enforcement:
- **OPA/Gatekeeper ConstraintTemplate:** Block Kubernetes resources without required labels.
- **Azure Policy / AWS SCP:** Deny resource creation without mandatory tags at the subscription/account level.
- **Terraform Sentinel:** Fail `terraform apply` if a planned resource is missing required tags.
- **Weekly audit:** Run Kubecost/Infracost to generate a "tag debt" report and publish a team compliance leaderboard.

**8. How do you reduce Kubernetes compute costs by 40% without degrading reliability?**

Multi-lever approach:
1. **Right-size requests:** `kubectl top pod` reveals pods requesting 4 CPU but using 200m. Set requests to P95 of actual usage with 20% headroom. Use VPA in recommendation mode to surface suggestions.
2. **Spot/preemptible nodes:** Move stateless workloads (web, workers) to spot node pools. Use PodDisruptionBudgets for graceful eviction.
3. **Node bin-packing:** Ensure all pods have resource requests set (Cluster Autoscaler needs them). Use topology spread constraints to pack small pods onto fewer nodes.
4. **Off-hours scaling:** Scale dev/staging clusters to zero using KEDA cron scaler or scheduled scale-down.
5. **Reserved capacity:** Commit 1-year Savings Plans/Reserved Instances for the baseline on-demand floor (~60-70% of baseline cost at 30-40% discount).
6. **Cleanup:** Remove Helm releases for unused services, PVCs without active pods, load balancers without backends.

**9. What is Backstage and what problem does it solve?**

Backstage (CNCF) is an open-source developer portal framework originally built at Spotify. It solves the "cognitive load" problem — as an organization grows, engineers spend increasing time finding documentation, understanding service ownership, onboarding to new services, and navigating disparate tooling. Backstage provides a centralized software catalog (all services, APIs, and infrastructure), Software Templates for self-service scaffolding, and a plugin system that brings CI/CD status, cloud costs, on-call rotations, and tech docs into a single pane of glass.

**10. What is Crossplane and how does it enable platform engineering?**

Crossplane is a Kubernetes-native control plane for infrastructure. It lets platform teams define Composite Resource Definitions (XRDs) that abstract cloud resources — a team creates a `DatabaseClaim` Kubernetes resource and Crossplane provisions an actual RDS/Azure SQL instance, configures networking, and creates the Kubernetes Secret with connection details. Infrastructure becomes a Kubernetes API — developers provision resources using `kubectl apply` or GitOps, with the same interface they use for applications.

---

