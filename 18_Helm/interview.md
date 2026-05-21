# Helm — Interview Prep

---
description: Easy, Medium, and Hard interview questions for Helm — Kubernetes package management.
---

```
Helm Interview — Easy through Hard
├── Easy: Foundations (Q1–12)
│   ├── What is Helm and what problem does it solve (templating + lifecycle)
│   ├── Chart: blueprint (Chart.yaml, values.yaml, templates/)
│   ├── Release: running instance tracked as K8s Secret
│   ├── values.yaml: defaults; override with --values or --set (--set wins)
│   ├── helm install vs helm upgrade --install (idempotent CI/CD pattern)
│   ├── --dry-run: render + API validate, no apply; use for preview/debug
│   ├── Helm template functions: quote, default, required, toYaml, indent
│   ├── helm rollback: restores previous revision from Secret history
│   ├── Subcharts: dependency charts; values prefixed by subchart name
│   ├── Helm repositories: classic (index.yaml) vs OCI (registry protocol)
│   ├── helm lint: validate chart structure and template syntax
│   └── helm show values: display chart defaults before installing
├── Hard: Advanced Patterns (Q21–26)
│   ├── Operators vs Helm: Helm is YAML lifecycle; Operators are reconciliation loops
│   ├── chart-testing (ct): lint + install + upgrade test in CI
│   ├── Helmfile: multi-release orchestration with needs: ordering
│   ├── Library charts: type:library; provide named templates, no rendered output
│   ├── kind + helm: local multi-node cluster for chart integration tests
│   └── lookup function: queries live cluster at render time; breaks offline rendering
└── Key Gotchas
    ├── ArgoCD ignores Helm hooks: use sync waves instead
    ├── CRDs not upgraded on helm upgrade: use separate job or Flux crds: CreateReplace
    ├── --set escaping: commas/braces need backslash; prefer --values for complex values
    └── lookup breaks GitOps: non-deterministic rendering; use sparingly
```

### First Principles

- Kubernetes YAML is repetitive across environments. Helm = templating engine + package manager for K8s. Chart = versioned package. Values = environment-specific overrides. Release = deployed instance of a chart. Hooks = lifecycle actions (pre-install, post-upgrade).
- `helm upgrade --install` is the CI/CD idiom: idempotent, no pre-check needed.
- ArgoCD uses `helm template` not `helm install` — Helm hooks are ignored in GitOps mode; use ArgoCD sync waves instead.
- CRD upgrade limitation: Helm installs CRDs only on `helm install`, never on `helm upgrade`. Plan CRD migrations separately.

## Easy

**1. What is Helm and what problem does it solve?**

Helm is the package manager for Kubernetes. Without Helm, deploying an application requires writing and applying 5-10 separate YAML files (Deployment, Service, ConfigMap, Ingress, etc.) manually. Helm bundles these into a "chart" — a versioned, distributable package with templating. A single `helm install` deploys the complete application; `helm upgrade` updates it; `helm rollback` reverts it. This gives Kubernetes deployments the lifecycle management (install, upgrade, rollback, test) that `apt`, `brew`, and `npm` provide for software packages.

**2. What is a Helm chart?**

A Helm chart is a directory containing: `Chart.yaml` (name, version, dependencies), `values.yaml` (default configuration), and `templates/` (Go-templated Kubernetes YAML files). The chart is the "blueprint"; a release is a running instance of the chart in a cluster. Charts can be packaged as `.tgz` archives and stored in Helm repositories or OCI registries.

**3. What is a Helm release?**

A release is a specific installation of a chart in a Kubernetes cluster, identified by a name and namespace. Running `helm install my-app ./chart` creates a release named `my-app`. The same chart can be installed as multiple releases in the same cluster (e.g., `my-app-blue` and `my-app-green` for blue-green deployments). Helm stores release metadata in Kubernetes Secrets in the target namespace.

**4. What is `values.yaml` and how do you override it?**

`values.yaml` contains the default configuration for a chart's templates. You override values via: `--values another-file.yaml` (file override) or `--set image.tag=v2.0` (flag override). Multiple `--values` files are merged left to right. `--set` flags have the highest priority and override everything. `helm show values my-chart` displays the defaults.

**5. What is the difference between `helm install` and `helm upgrade --install`?**

`helm install` fails if a release with that name already exists. `helm upgrade --install` is idempotent — it installs the release if it doesn't exist, or upgrades it if it does. Use `helm upgrade --install` in CI/CD pipelines where you don't know the initial state. This is the recommended pattern for GitOps-style deployments.

**6. What does `--dry-run` do in Helm?**

`helm install my-app ./chart --dry-run` renders the templates and validates them against the Kubernetes API (schema validation) but does not apply anything to the cluster. It outputs the rendered YAML to stdout. Use it to: preview what will be deployed, debug template rendering errors, and validate values before a real install.

**7. How do you roll back a Helm release?**

```bash
helm history my-app           # Shows all revisions
helm rollback my-app          # Roll back to previous revision
helm rollback my-app 3        # Roll back to specific revision 3
```
Helm stores each revision's manifest in a Kubernetes Secret. Rollback applies the stored manifests for that revision, creating a new (higher) revision number. It does not undo database migrations or other side effects.

**8. What is `helm lint` and when do you run it?**

`helm lint ./mychart` checks the chart for syntax errors, missing required fields, and common template mistakes. Run it in CI before packaging or deploying. It catches obvious errors like missing `Chart.yaml` fields, invalid YAML in templates, or missing values that templates depend on. Use `helm lint --strict` to treat warnings as errors.

**9. How does Helm manage secrets?**

Helm itself does not manage secrets — it renders whatever is in the template, including `Secret` resources. The `helm-secrets` plugin (using SOPS or Vault) encrypts values files so secrets can be committed to Git. Decryption happens at render time, never touching disk. Alternatively: don't put secrets in Helm at all — use the External Secrets Operator to create Kubernetes Secrets from Vault/AWS Secrets Manager, and Helm only deploys the application that consumes them.

**10. What is a Helm repository and how do you use it?**

A Helm repository is an HTTP server hosting an `index.yaml` file and `.tgz` chart archives. Commands:
```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update               # Refresh index from all added repos
helm search repo bitnami/redis # Search for a chart
helm install my-redis bitnami/redis --version 18.6.4
```
Modern repositories use OCI (Open Container Initiative) instead of the legacy HTTP format — charts are stored in container registries alongside Docker images.

**11. What is the difference between `helm template` and `helm install --dry-run`?**

Both render templates without applying them, but:
- `helm template` renders locally without connecting to the cluster — no API validation, no cluster context needed. Useful in CI when a cluster isn't available.
- `helm install --dry-run` connects to the cluster, performs server-side API validation, and simulates the full install including admission webhook calls. More accurate but requires cluster access.

**12. How does Helm know what version of a chart to install?**

You specify it explicitly with `--version` flag or `version` in Chart.yaml dependencies. Without `--version`, Helm installs the latest version from the repository. In production, always pin to an exact version. The `.helmignore` file and `.helm-lock` (Helmfile) ensure reproducible installations.

***

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
# OCI workflow
helm push mychart-1.0.0.tgz oci://registry.io/charts
helm install my-app oci://registry.io/charts/mychart --version 1.0.0
```

**18. How does ArgoCD deploy Helm charts and what's different from `helm install`?**

ArgoCD renders Helm charts using `helm template` — it does NOT use `helm install`. This means:
- Helm release Secrets are not created in the cluster (ArgoCD manages state itself)
- Lifecycle hooks (`pre-install`, `post-install`) are managed by ArgoCD's sync phases and sync hooks, not Helm hooks
- `helm.sh/hook` annotations are generally ignored by ArgoCD (use ArgoCD's `argocd.argoproj.io/hook` instead)
- Values are provided via the Application spec `helm.values` or `helm.valueFiles`

**19. What is the Helm test framework?**

`helm test my-app` runs all Pods/Jobs annotated with `helm.sh/hook: test`. These tests verify the release is working correctly after installation — they test connectivity, configuration loading, and basic functionality. Tests return success (exit 0) or failure (exit non-0). Add `helm.sh/hook-delete-policy: hook-succeeded` to clean up test pods after success.

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

***

## Hard

**21. How would you design a Helm chart strategy for a company with 50 microservices?**

**Option A: Generic application chart (recommended for homogeneous services)**
- One chart parameterized for all services: `mycompany/app`
- Services differ only in values: image, resources, replicas, ingress config
- All services share the same chart version — upgrades are centralized
- Pro: one place to add sidecars, security contexts, labels
- Con: complex charts become hard to maintain; escaping the template for unusual services is painful

**Option B: Per-service charts (for heterogeneous services)**
- Each service has its own chart tailored to its needs (e.g., a stateful ML service is very different from a stateless API)
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

**Example:** Deploy PostgreSQL with Helm (simple, known lifecycle). Deploy PostgreSQL for a production multi-replica HA setup with automatic failover → use the CloudNativePG operator. The operator knows how to handle primary failure, replication lag, and backup scheduling automatically.

**23. How do you handle Helm chart upgrades for CRDs?**

Helm has a fundamental limitation with CRDs: it installs CRDs from the `crds/` directory on initial install only, and does NOT upgrade them. Upgrading CRDs with Helm is manual:

```bash
# Option 1: Apply CRDs directly before helm upgrade
kubectl apply -f crds/

# Option 2: Use a separate chart for CRDs (ArgoCD sync wave pattern)
# Wave 0: Install CRD chart
# Wave 1: Install application chart that depends on the CRDs

# Option 3: Use a pre-upgrade hook (for simple cases)
# Pre-upgrade hook Job that runs: kubectl apply -f /crds/
# (requires the hook container to have kubectl and RBAC to update CRDs)
```

This is a known rough edge of Helm — many operators use their own CRD management to work around it.

**24. What is Helmfile and how does it improve on `helm upgrade --install` for complex environments?**

`helm upgrade --install` is single-chart; Helmfile orchestrates multiple releases as a declarative spec:

```yaml
# Helmfile solves:
# 1. Ordering: deploy postgresql before my-app (needs: postgresql)
# 2. Environment management: different values per environment
# 3. Selective updates: helmfile apply --selector app=my-app
# 4. Diff across all charts: helmfile diff (shows what would change)
# 5. State management: helmfile knows what's already deployed
```

Helmfile enables a "GitOps-lite" workflow without ArgoCD — the CI pipeline runs `helmfile apply` on merge. For full GitOps with drift detection, ArgoCD is preferred.

**25. How do you test Helm charts in a CI pipeline?**

```yaml
# GitHub Actions Helm CI pipeline
- name: Lint
  run: helm lint ./chart --values values-test.yaml

- name: Unit tests (helm-unittest)
  run: |
    helm plugin install https://github.com/helm-unittest/helm-unittest
    helm unittest ./chart

- name: Render and validate
  run: |
    helm template my-app ./chart --values values-test.yaml > rendered.yaml
    kubeval rendered.yaml --kubernetes-version 1.29.0   # Schema validation
    # OR
    kubeconform rendered.yaml -kubernetes-version 1.29.0

- name: Integration test (kind cluster)
  run: |
    kind create cluster
    helm install my-app ./chart --wait --timeout 5m
    helm test my-app --timeout 3m
    kind delete cluster
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
- Couples the Helm chart to existing cluster state — breaks GitOps purity
- Can expose sensitive data if the rendered template is logged

**Use `lookup` sparingly** — only for cases where you genuinely need to read existing cluster state (e.g., checking if a resource already exists before deciding how to create it).

***

### System Design Perspective

**Helm in a Multi-Environment Pipeline**
- Dev → Staging → Production: same chart, three value files. CI runs `helm lint` + `helm template | kubeval` on PR; CD runs `helm upgrade --install --atomic` per environment gate.
- `--atomic` flag: rolls back automatically if any resource fails to become Ready within `--timeout`. Safe default for production pipelines — prevents partial upgrades.

**Library Chart for Microservices Monorepo**
- Problem: 20 services each have nearly identical Deployment + Service + HPA + PodDisruptionBudget templates.
- Solution: one library chart (`type: library`) in `charts/common/` that defines `{{- define "common.deployment" }}`. Each service chart has a single-line include + its own values.yaml.
- Benefit: change the Deployment template once in the library; all 20 services pick it up in the next chart bump.

**Operator vs Helm Decision**
- Use Helm when: deploying a stateless app or a well-understood stateful app with a known lifecycle (install, upgrade, rollback, uninstall).
- Use an Operator when: the resource requires domain-specific reconciliation logic (e.g., a database cluster that needs to coordinate leader election, schema migrations, and backup rotation continuously — not just at install/upgrade time).

---
description: Medium-difficulty interview questions for Helm — lifecycle hooks, subcharts, OCI registries, and ArgoCD integration.
---

```
Helm Medium Interview (Q13–20)
├── Lifecycle Hooks (Q13–14)
│   ├── Hook: K8s Job with helm.sh/hook annotation
│   ├── Common uses: pre-upgrade DB migration, post-upgrade smoke test, pre-delete drain
│   ├── Hook failure: release fails; use hook-delete-policy: hook-succeeded for cleanup
│   └── hook-weight: ascending order execution; negative weights allowed
├── Library Charts (Q15)
│   ├── type: library in Chart.yaml; no rendered resources; only named templates
│   ├── Other charts declare it as a dependency; use include "lib.helper" .
│   └── Purpose: share company-wide boilerplate (labels, RBAC, resource limits)
├── Subchart Dependencies (Q16)
│   ├── Declared in Chart.yaml dependencies:; fetched with helm dependency update
│   ├── Placed in charts/ directory; parent passes values prefixed by subchart name
│   ├── Condition: subchart-name.enabled: false disables a subchart
│   └── Global values: .Values.global available across parent + all subcharts
├── OCI Registries (Q17)
│   ├── helm push ./chart-1.0.0.tgz oci://registry.io/charts
│   ├── helm pull oci://registry.io/charts/app --version 1.0.0
│   ├── No index.yaml needed; reuses container registry auth (helm registry login)
│   └── Advantage: single registry for container images + charts
├── ArgoCD + Helm Integration (Q18)
│   ├── ArgoCD uses helm template (not helm install); owns release state itself
│   ├── Helm hooks are silently ignored by ArgoCD
│   ├── Use ArgoCD sync waves (argocd.argoproj.io/sync-wave) instead of hooks
│   └── values files: ArgoCD Application spec references values files in Git
├── helm test (Q19)
│   ├── Jobs with helm.sh/hook: test annotation; run with helm test <release>
│   ├── Test examples: HTTP endpoint check, DB connection validation
│   └── Exit code 0 = pass; non-zero = test failure reported by Helm
└── Chart Upgrade Safety (Q20)
    ├── helm diff upgrade: preview changes before applying (helm-diff plugin)
    ├── --atomic: auto-rollback on timeout or resource failure
    ├── CRD schema changes: apply kubectl apply -f crds/ before helm upgrade
    └── Breaking value renames: use helm show values to diff old vs new defaults
```

### First Principles

- Kubernetes YAML is repetitive across environments. Helm = templating engine + package manager for K8s. At medium level, the questions test lifecycle understanding: hooks are Jobs with annotations, not new primitives.
- Hooks = lifecycle actions. Hook weight controls execution order within a phase. `hook-delete-policy: hook-succeeded` prevents stale Job accumulation.
- ArgoCD uses `helm template` not `helm install`. Helm hooks are ignored. Migration to ArgoCD requires replacing pre-upgrade hooks with sync waves.
- Subcharts: values are namespaced by chart name. Global values (`.Values.global`) cross all subchart boundaries.

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

***

### System Design Perspective

**Hook-Based Database Migration Pattern**
- pre-upgrade hook Job: runs `alembic upgrade head` (or Flyway) before any new pods start. Hook weight -5 (runs first). `hook-delete-policy: before-hook-creation` removes the previous run's Job before creating a new one (prevents name conflict).
- If migration fails: Helm marks the release failed and rolls back new pods — old pods remain. The DB schema is at the old version; rollback is safe.
- Caveat: this only works for backward-compatible schema changes. For destructive schema changes (column drop), use expand-contract pattern across multiple releases.

**Global Values for Platform-Wide Configuration**
```yaml
# Parent values.yaml
global:
  imageRegistry: "registry.mycompany.com"
  imagePullSecrets: ["regcred"]
  monitoring:
    enabled: true
    namespace: monitoring
```
- All subcharts read `.Values.global.imageRegistry` — change it once in the parent, all subcharts use the new registry.
- Pattern used by Bitnami charts for consistent multi-component deployment (Redis + PostgreSQL + app all in one parent chart).

**OCI Registry as Single Source of Truth**
- Push chart + container image to the same registry (AWS ECR, Harbor). Helm chart version and app version are co-located.
- Release process: `docker push` → `helm package` → `helm push` (OCI) → PR to update helmfile.yaml chart version → ArgoCD applies. Single registry auth, single retention policy, single audit log.

---
description: Hard interview questions for Helm — chart architecture, Operators vs Helm, CRD management, Helmfile, and enterprise patterns.
---

```
Helm Hard Interview (Q21–27)
├── Chart Strategy for 50 Microservices (Q21)
│   ├── Option A: Generic app chart — one chart, all services differ by values
│   ├── Option B: Per-service charts + library chart for shared named templates
│   └── Recommendation: generic chart for 80%; specialized for DB/ML/jobs
├── Helm vs Operators (Q22)
│   ├── Helm: static resources; install/upgrade/rollback lifecycle; event-driven by CI/CD
│   ├── Operator: reconciliation loop; domain-specific logic; CRD + controller
│   ├── Use Helm for: stateless apps, known lifecycle
│   └── Use Operator for: databases, distributed systems needing continuous reconciliation
├── CRD Management (Q23)
│   ├── Helm installs CRDs from crds/ only on helm install (not helm upgrade)
│   ├── Upgrading CRDs requires manual kubectl apply or separate job
│   ├── Flux HelmRelease: crds: CreateReplace option for safe CRD upgrades
│   └── Never delete CRDs accidentally — irreversible data loss
├── Helmfile Multi-Chart Orchestration (Q24)
│   ├── helmfile.yaml: lists releases with chart, values, namespace
│   ├── needs: field: dependency ordering (cert-manager before ingress-nginx)
│   ├── environments: block: per-env value overlays
│   └── helmfile diff / sync / apply: preview and deploy all releases
├── Chart Testing (Q25)
│   ├── helm lint: validate chart structure and template syntax
│   ├── chart-testing (ct): lint + install + upgrade test in kind cluster
│   ├── helm-unittest: unit test templates without a cluster (Go template assertions)
│   └── kind: local multi-node K8s cluster for integration test
├── lookup Function Risks (Q26)
│   ├── Queries live cluster at render time → non-deterministic output
│   ├── Breaks helm template offline rendering → breaks GitOps pipelines
│   └── Exposes cluster state in rendered templates → security risk
└── Secrets Management (Q27)
    ├── --set from CLI: secrets visible in shell history → avoid in production
    ├── helm-secrets + SOPS: encrypted values.yaml in Git; decrypt at deploy time
    └── External Secrets Operator: best practice; chart deploys ExternalSecret CRD only
```

### First Principles

- Kubernetes YAML is repetitive across environments. Helm = templating engine + package manager for K8s. At the hard level, the questions test architecture decisions: one generic chart vs many specialized, Operator vs Helm, secret management patterns.
- Operators extend Kubernetes with domain logic. Helm manages known lifecycles. The decision boundary: if the resource needs a reconciliation loop that runs continuously (not just on deploy), use an Operator.
- CRD upgrade limitation is a known Helm design limitation — not a bug. Plan CRD migrations as a separate operational step, not part of `helm upgrade`.
- Secrets management: External Secrets Operator is the production best practice. `--set` with secret values in CI/CD is the worst practice (secrets in logs).

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

***

### System Design Perspective

**Enterprise Chart Governance**
- Chart versioning SLA: patch for value changes, minor for new optional features, major for breaking template changes. Enforce via CI lint rule: chart version must be bumped in every PR that changes a template.
- Centralized chart registry: all internal charts pushed to Harbor or AWS ECR OCI. Services pin chart version in helmfile.yaml — no floating `latest`. Dependabot or Renovate bot opens PRs for chart version bumps.

**Multi-Environment Helmfile Architecture**
```
helmfile.yaml         ← base: all releases, chart refs, namespace
values/
  base/               ← shared values (labels, resource defaults)
  dev/                ← dev overrides (low resource requests, debug=true)
  staging/            ← staging overrides (prod-like sizing, staging secrets)
  prod/               ← prod overrides (HPA, PDB, anti-affinity, prod secrets)
```
- `helmfile -e prod sync` applies prod environment values across all releases.

**Helm in a Zero-Trust Platform**
- Every chart deployment goes through OPA/Gatekeeper admission: pod must have security context (runAsNonRoot, readOnlyRootFilesystem), resource limits, and team label.
- Helm chart CI gate: `helm template | conftest test --policy ./policies/` validates OPA policies before the chart reaches the cluster.
- Release RBAC: service accounts scoped to namespace; Helm release Secret only readable by the CI/CD principal — not developers.
