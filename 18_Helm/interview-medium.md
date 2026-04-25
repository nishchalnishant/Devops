---
description: Medium-difficulty interview questions for Helm — lifecycle hooks, subcharts, OCI registries, and ArgoCD integration.
---

## Medium

**13. What is a Helm hook and what are the most common use cases?**

A Helm hook is a Kubernetes resource (usually a Job) that runs at a specific lifecycle phase, controlled by the `helm.sh/hook` annotation. Common hooks:
- `pre-install`, `pre-upgrade`: Run database migrations before the new application version starts
- `post-install`, `post-upgrade`: Run smoke tests or send a Slack notification after deploy
- `pre-delete`: Drain connections or archive data before a service is removed

Hook jobs must complete successfully for Helm to consider the phase successful. If a hook fails, the release fails.

**14. What is `helm.sh/hook-weight` and why is it needed?**

Multiple hooks of the same type run in order of weight (ascending). Without weights, multiple `pre-upgrade` hooks run in arbitrary order. Example: a hook that backs up the database (weight: -10) must run before a hook that runs migrations (weight: 5) during `pre-upgrade`. Weights can be negative.

**15. What are Helm library charts?**

A library chart (`type: library` in `Chart.yaml`) contains only named templates — no Kubernetes resources. It cannot be installed directly. Other charts depend on it to share common template logic. Example: a company-wide library chart defines `company.labels`, `company.serviceAccount`, and `company.resources` templates. All product charts depend on it and call `include "company.labels" .` rather than duplicating the boilerplate.

**16. How does Helm handle subchart dependencies?**

Subcharts are declared in `Chart.yaml` under `dependencies:` and fetched with `helm dependency update`. They are placed in `charts/`. The parent chart passes values to subcharts by prefixing with the subchart name:
```yaml
# Parent's values.yaml
redis:              # This prefix targets the 'redis' subchart
  auth:
    password: "mypass"
  architecture: standalone
```
Subcharts can be conditionally enabled via `condition: redis.enabled` — if `redis.enabled: false`, the subchart is skipped.

**17. What are OCI-based Helm registries and how do they differ from classic repositories?**

Classic repositories use an `index.yaml` file served over HTTP. OCI repositories store charts as OCI artifacts in container registries (ECR, GAR, Docker Hub, Harbor). OCI is now the recommended standard:
- Charts and images share the same registry (simpler infrastructure)
- No separate `helm repo add` required — pull directly by URL
- Authentication uses the same mechanism as Docker image pulls
- Better immutability guarantees (content-addressed by digest)

```bash
helm push mychart-1.0.0.tgz oci://registry.io/charts
helm install my-app oci://registry.io/charts/mychart --version 1.0.0
```

**18. How does ArgoCD deploy Helm charts and what's different from `helm install`?**

ArgoCD renders Helm charts using `helm template` — it does NOT use `helm install`. This means:
- Helm release Secrets are not created in the cluster (ArgoCD manages state itself)
- `helm.sh/hook` annotations are ignored by ArgoCD — use ArgoCD's `argocd.argoproj.io/hook` instead
- Values are provided via the Application spec `helm.values` or `helm.valueFiles`
- Rollback is via ArgoCD revision history, not `helm rollback`

**19. What is the Helm test framework?**

`helm test my-app` runs all Pods/Jobs annotated with `helm.sh/hook: test`. These tests verify the release is working correctly after installation — connectivity, configuration loading, and basic functionality. Tests return success (exit 0) or failure (exit non-0). Add `helm.sh/hook-delete-policy: hook-succeeded` to clean up test pods after success.

**20. How do you upgrade a chart with a breaking change in values schema?**

```bash
# 1. Inspect what changed
helm show values new-chart-version > new-defaults.yaml
diff old-defaults.yaml new-defaults.yaml

# 2. Update your values override files to match new schema

# 3. Dry-run to verify rendering
helm upgrade my-app ./chart --values updated-values.yaml --dry-run

# 4. If the upgrade changes CRDs, upgrade CRDs manually first
kubectl apply -f crds/

# 5. Apply with atomic flag for safety
helm upgrade my-app ./chart --values updated-values.yaml --atomic --timeout 10m
```
