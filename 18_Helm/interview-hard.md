---
description: Hard interview questions for Helm — chart architecture, Operators vs Helm, CRD management, Helmfile, and enterprise patterns.
---

## Hard

**21. How would you design a Helm chart strategy for a company with 50 microservices?**

**Option A: Generic application chart (recommended for homogeneous services)**
- One chart parameterized for all services: `mycompany/app`
- Services differ only in values: image, resources, replicas, ingress config
- All services share the same chart version — upgrades are centralized
- Pro: one place to add sidecars, security contexts, labels
- Con: complex charts become hard to maintain; escaping the template for unusual services is painful

**Option B: Per-service charts (for heterogeneous services)**
- Each service has its own chart tailored to its needs
- Library chart provides shared named templates to avoid duplication
- Pro: flexibility; each team owns their chart
- Con: 50 charts to maintain; inconsistency creeps in

**Recommendation:** Start with a generic chart for 80% of services. Create specialized charts for services with fundamentally different requirements (databases, ML workloads, jobs). Use a library chart for shared labels, RBAC, security contexts.

**22. How does Helm differ from Kubernetes Operators and when do you use each?**

Both manage Kubernetes resources, but at different levels of abstraction:

**Helm:**
- Manages the initial deployment and upgrades of known, static resources
- Lifecycle: install, upgrade, rollback — triggered manually or by CI/CD
- No ongoing reconciliation loop — Helm doesn't watch for drift
- Good for: deploying applications that don't need complex operational logic

**Operators:**
- A custom controller running in the cluster, continuously reconciling desired vs actual state
- Encodes operational knowledge: "if the primary database pod fails, elect a new primary and update all secondary connection strings"
- Good for: stateful, complex systems where lifecycle management needs automated responses to runtime events

**Rule:** Deploy PostgreSQL with Helm for simple cases. For production HA PostgreSQL with automatic failover → use the CloudNativePG operator. The operator knows how to handle primary failure, replication lag, and backup scheduling automatically — Helm does not.

**23. How do you handle Helm chart upgrades for CRDs?**

Helm has a fundamental limitation with CRDs: it installs CRDs from the `crds/` directory on initial install only, and does NOT upgrade them. Upgrading CRDs with Helm is manual:

```bash
# Option 1: Apply CRDs directly before helm upgrade
kubectl apply -f crds/

# Option 2: Use a separate chart for CRDs (ArgoCD sync wave pattern)
# Wave 0: Install CRD chart
# Wave 1: Install application chart that depends on the CRDs

# Option 3: Use a pre-upgrade hook Job
# Hook container applies CRDs using kubectl
# Requires the hook container to have kubectl and RBAC to update CRDs
```

This is a known rough edge of Helm — many operators use their own CRD management to work around it.

**24. What is Helmfile and how does it improve on `helm upgrade --install`?**

`helm upgrade --install` is single-chart; Helmfile orchestrates multiple releases declaratively:

```yaml
# helmfile.yaml
releases:
  - name: postgresql
    namespace: database
    chart: bitnami/postgresql
    version: "13.4.4"

  - name: my-app
    namespace: application
    chart: ./charts/my-app
    needs:
      - database/postgresql     # Deploy postgresql first
    values:
      - values/{{ .Environment.Name }}.yaml
```

```bash
helmfile -e staging apply    # Deploy all to staging
helmfile -e production diff  # Diff against production
helmfile -e staging destroy  # Destroy all
```

Helmfile solves: multi-chart ordering, environment-specific values, selective updates, and diff-before-apply across all releases. For full GitOps with drift detection, ArgoCD is preferred over Helmfile.

**25. How do you test Helm charts in a CI pipeline?**

```yaml
# Complete Helm CI pipeline
- name: Lint
  run: helm lint ./chart --strict --values values-test.yaml

- name: Unit tests (helm-unittest)
  run: helm unittest ./chart

- name: Render and validate
  run: |
    helm template my-app ./chart --values values-test.yaml > rendered.yaml
    kubeconform -kubernetes-version 1.29.0 rendered.yaml

- name: Integration test (kind cluster)
  run: |
    kind create cluster --name ci-test
    helm install my-app ./chart --wait --timeout 5m
    helm test my-app --timeout 3m --logs
    kind delete cluster --name ci-test
```

**26. What is the `lookup` function in Helm and what are its risks?**

`lookup` queries the Kubernetes API at template render time:
```yaml
{{- $secret := lookup "v1" "Secret" "default" "my-secret" }}
{{- if $secret }}
password: {{ index $secret.data "password" | b64dec | quote }}
{{- end }}
```

**Risks:**
- Template output becomes non-deterministic (depends on current cluster state)
- Makes `helm template` (offline rendering) impossible — requires live cluster access
- Couples the chart to existing cluster state — breaks GitOps purity
- Sensitive data may be exposed if the rendered template is logged

**Use `lookup` sparingly** — only when you genuinely need to read existing cluster state. For most use cases, External Secrets Operator is a better pattern.

**27. How do you manage Helm chart secrets without storing them in Git?**

Three approaches in order of maturity:

1. **Inject values at deploy time (simplest):**
   ```bash
   helm upgrade my-app ./chart \
     --set db.password=$(aws secretsmanager get-secret-value --secret-id prod/db --query SecretString --output text | jq -r .password)
   ```
   Con: secrets visible in shell history and CI logs.

2. **helm-secrets plugin with SOPS:**
   ```bash
   helm secrets enc secrets.yaml          # Encrypt with AWS KMS or GPG
   helm secrets upgrade my-app ./chart -f secrets.yaml  # Decrypt at deploy time
   ```
   Encrypted values stored in Git; decryption key is in AWS KMS.

3. **External Secrets Operator (best practice):**
   - Helm only deploys the application and an `ExternalSecret` resource
   - ESO fetches real values from Vault/AWS Secrets Manager
   - No secrets in Helm values at all — fully separated concerns
