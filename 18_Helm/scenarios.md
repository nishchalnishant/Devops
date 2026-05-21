---
description: Helm scenarios — real-world troubleshooting, chart design, and upgrade challenges.
---

# Helm Scenarios & Troubleshooting

```
Helm Scenarios & Troubleshooting
├── Scenario 1: Upgrade Stuck in pending-upgrade
│   ├── Cause: pipeline lost connectivity mid-upgrade; Helm Secret left in pending state
│   ├── Diagnosis: helm history → find pending revision; kubectl get secrets
│   ├── Fix: helm rollback (clears pending) or helm uninstall + reinstall (last resort)
│   └── Prevention: --atomic flag auto-rolls back on failure/timeout
├── Scenario 2: Image Pull Error After Upgrade
│   ├── Cause: wrong image tag in values; tag doesn't exist in registry; pull secret missing
│   ├── Diagnosis: kubectl describe pod → Events: ImagePullBackOff + error message
│   ├── Fix: helm rollback to last good revision immediately; then fix values
│   └── Prevention: validate image exists in registry in CI before helm upgrade
├── Scenario 3: Subchart Values Not Applied
│   ├── Cause: missing subchart name prefix in parent values.yaml
│   ├── Diagnosis: helm get values <release> → compare effective vs expected values
│   ├── Fix: prefix values with subchart name (redis.auth.password not auth.password)
│   └── Global values: .Values.global bypasses prefix and propagates to all subcharts
├── Scenario 4: Hook Job Not Cleaning Up
│   ├── Cause: hook-delete-policy not set; completed Jobs accumulate
│   ├── Fix: add helm.sh/hook-delete-policy: hook-succeeded annotation to hook Job
│   └── Or before-hook-creation: removes old Job before each upgrade
├── Scenario 5: CRD Not Updated After Chart Upgrade
│   ├── Cause: Helm only installs CRDs on helm install; never updates on helm upgrade
│   ├── Fix: kubectl apply -f crds/ manually before helm upgrade
│   └── Long-term: use Flux HelmRelease with crds: CreateReplace for managed CRD upgrades
├── Scenario 6: ArgoCD Ignoring Helm Hooks
│   ├── Cause: ArgoCD uses helm template; hook annotations are ignored in GitOps mode
│   ├── Fix: replace Helm hooks with ArgoCD sync waves (argocd.argoproj.io/sync-wave)
│   └── Pre-upgrade DB migration: move to a Job with sync-wave: "-1" in ArgoCD
└── Scenario 7: Template Rendering Debugging Workflow
    ├── Step 1: helm template ./chart --values vals.yaml --debug (local render)
    ├── Step 2: kubectl apply --dry-run=server (API validation without cluster apply)
    ├── Step 3: helm install --dry-run --debug (show USER-SUPPLIED VALUES + computed values)
    └── Step 4: kubeconform for K8s schema version validation
```

## First Principles

- Kubernetes YAML is repetitive across environments. Helm = templating engine + package manager for K8s. Scenarios test operational knowledge: how to diagnose stuck releases, failed hooks, and misconfigured values.
- `--atomic` prevents stuck states. `helm rollback` restores previous working state from the release Secret. These two commands are the first response to any failed upgrade.
- ArgoCD uses `helm template` not `helm install` — Helm hooks are ignored. Operational teams migrating to ArgoCD must audit all hooks and replace them with sync waves.
- CRD upgrade limitation is a production surprise. Document the manual `kubectl apply -f crds/` step in runbooks whenever a chart version bump includes CRD changes.

***

## Scenario 1: Helm Upgrade Stuck in `pending-upgrade` State

**Situation:** A CI/CD pipeline ran `helm upgrade my-app ./chart` but lost connectivity mid-upgrade. The next pipeline run fails with: `Error: UPGRADE FAILED: another operation (install/upgrade/rollback) is in progress`.

**Diagnosis:**
```bash
helm history my-app --namespace production
# Shows a revision with status "pending-upgrade" or "pending-install"

kubectl get secrets --namespace production | grep my-app
# Shows: sh.helm.release.v1.my-app.v7 with "pending-upgrade"
```

**Resolution:**
```bash
# Option 1: Roll back to last good revision
helm rollback my-app --namespace production --wait
# This clears the pending state and restores the previous revision

# Option 2: Force a fresh install (last resort — causes downtime)
helm uninstall my-app --namespace production
helm install my-app ./chart --namespace production --wait
```

**Prevention:** Use `--atomic` flag in CI — if the upgrade fails or times out, Helm automatically rolls back, preventing stuck states. Ensure pipeline timeouts are longer than Helm's `--timeout`.

***

## Scenario 2: Chart Upgrade Causes Image Pull Error

**Situation:** After `helm upgrade`, all pods are in `ImagePullBackOff`. Previous version was healthy.

**Diagnosis:**
```bash
# Check what image tag was deployed
kubectl get deployment my-app -o jsonpath='{.spec.template.spec.containers[0].image}'
# Output: myregistry.io/my-app:       ← Empty tag!

# Check values that were applied
helm get values my-app --revision 7
# image:
#   tag: ""     ← The CI pipeline didn't pass --set image.tag
```

**Root cause:** CI ran `helm upgrade my-app ./chart` without `--set image.tag=${IMAGE_TAG}`. The chart defaulted to an empty string, resulting in `myregistry.io/my-app:` — an invalid image reference.

**Resolution:**
```bash
helm rollback my-app --namespace production --wait
# Then fix the CI pipeline to always pass --set image.tag=${IMAGE_TAG}
```

**Prevention:**
```yaml
# In chart template: fail fast if tag is not set
image: {{ required "image.tag must be set" .Values.image.tag | quote }}

# In values.schema.json:
"image": {
  "required": ["tag"],
  "properties": {
    "tag": {"type": "string", "minLength": 1}
  }
}
```

***

## Scenario 3: Pre-Upgrade Database Migration Hook Failing Silently

**Situation:** The team runs a `pre-upgrade` hook Job for database migrations. The Job completes with exit code 0 (success), but the database schema is not updated. The application starts but crashes due to missing columns.

**Diagnosis:**
```bash
# Check hook job logs
kubectl get jobs --namespace production | grep migrate
kubectl logs job/my-app-db-migrate --namespace production --previous

# The logs show: "Skipping migrations — no pending migrations found"
# But the schema IS out of date...
```

**Root cause:** The migration job is pulling `latest` (or the same old image). The image was not updated. The migration code that should have run is in the new application image, not the old one.

**Fix:**
```yaml
# templates/job-db-migrate.yaml
containers:
  - name: migrate
    image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"  # SAME tag as the app
    # NOT a hardcoded old version or "latest"
```

**Prevention:** Always use the same image tag for migration jobs as the application deployment. Add a `helm test` that verifies the schema version matches the expected version.

***

## Scenario 4: Values Are Not Being Passed to a Subchart

**Situation:** The parent chart has `redis.auth.password: mypass` in its values, but the Redis subchart is using the default password (empty string). Authentication is failing.

**Diagnosis:**
```bash
# Render templates to see what's actually being set
helm template my-app ./chart --values values-prod.yaml | grep -A5 "kind: Secret" | grep -i password

# Check the subchart name
helm show chart charts/redis/Chart.yaml | grep name
# name: redis  ← subchart is named "redis"

# Check parent values
cat values-prod.yaml
# redis:
#   auth:
#     Password: mypass    ← Capital 'P'!
```

**Root cause:** YAML keys are case-sensitive. `Password` ≠ `password`. The correct key for the Bitnami Redis chart is `auth.password` (lowercase).

**Fix:**
```yaml
# values-prod.yaml — correct casing
redis:
  auth:
    password: mypass    # lowercase 'p'
```

**Debugging technique:** `helm show values charts/redis/` to see the exact key names required.

***

## Scenario 5: Designing a Chart for Multi-Environment Deployment

**Challenge:** Design a Helm chart structure for a payment API that deploys to dev, staging, and production with the following differences:
- **Dev:** 1 replica, 100m CPU, auto-generated SSL certificate, debug logging, no HPA
- **Staging:** 2 replicas, 500m CPU, Let's Encrypt certificate, info logging, no HPA
- **Production:** 3+ replicas (HPA), 1000m CPU, real certificate, warn logging, PDB required

**Solution:**

```yaml
# values.yaml (shared defaults)
replicaCount: 1
logLevel: info
resources:
  requests:
    cpu: 100m
    memory: 128Mi
autoscaling:
  enabled: false
ingress:
  certIssuer: "dev-issuer"
pdb:
  enabled: false

# values-staging.yaml
replicaCount: 2
resources:
  requests:
    cpu: 500m
    memory: 256Mi
ingress:
  certIssuer: "letsencrypt-staging"

# values-production.yaml
logLevel: warn
resources:
  requests:
    cpu: 1000m
    memory: 512Mi
autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 20
ingress:
  certIssuer: "letsencrypt-prod"
pdb:
  enabled: true
  minAvailable: 2
```

```bash
# Deployment commands per environment
helm upgrade --install payment-api ./chart \
  --values values-staging.yaml \
  --set image.tag=${IMAGE_TAG} \
  --namespace staging

helm upgrade --install payment-api ./chart \
  --values values-production.yaml \
  --set image.tag=${IMAGE_TAG} \
  --atomic --wait \
  --namespace production
```

***

## Scenario 6: Helm Release History Cleanup in Production

**Situation:** `kubectl get secrets --namespace production | grep helm` shows 47 release secrets. Performance is degraded — kubectl operations are slow. You need to clean up old revisions.

**Diagnosis:**
Helm keeps all revision history by default (configurable via `--history-max`). 47 secrets = 47 revisions stored. Each secret contains the full rendered manifest of that revision.

**Resolution:**
```bash
# Set max history for future upgrades
helm upgrade my-app ./chart --history-max 10

# Clean up existing old revisions (no built-in command — use this approach)
# Keep last 10 revisions:
KEEP=10
helm history my-app --namespace production --max 1000 | \
  awk 'NR>1{print $1}' | \
  head -n -$KEEP | \
  while read rev; do
    kubectl delete secret "sh.helm.release.v1.my-app.v${rev}" --namespace production
  done
```

**Prevention:** Set `--history-max 10` in all `helm upgrade` commands in CI pipelines, or configure it globally in `helm` config.

***

## Scenario 7: Helm Chart Templating — Common Debugging Steps

When `helm template` or `helm install` produces unexpected output:

```bash
# Step 1: Render and inspect
helm template debug-release ./chart --values my-values.yaml > rendered.yaml
cat rendered.yaml | grep -A 20 "kind: Deployment"

# Step 2: Check specific template in isolation
helm template debug-release ./chart \
  --values my-values.yaml \
  --show-only templates/deployment.yaml

# Step 3: Validate against Kubernetes API
kubectl apply --dry-run=server -f rendered.yaml

# Step 4: Check what values are actually being used
helm install debug-release ./chart \
  --values my-values.yaml \
  --dry-run --debug 2>&1 | grep -A 100 "USER-SUPPLIED VALUES"

# Step 5: kubeconform for schema validation
kubeconform -kubernetes-version 1.29.0 rendered.yaml
```

***

## System Design Perspective

**Upgrade Safety Runbook**
1. `helm diff upgrade` — review all resource changes before applying.
2. For DB schema changes: run pre-upgrade hook Job manually (`kubectl apply -f migration-job.yaml`) and verify completion before `helm upgrade`.
3. `helm upgrade --install --atomic --timeout 10m --wait` — atomic ensures auto-rollback.
4. Post-upgrade: `helm test <release>` to run smoke tests; monitor error rate for 10 minutes.
5. Rollback: `helm rollback <release> <revision>` — instant restore from Secret history.

**Multi-Chart Upgrade Ordering**
- Infrastructure layer (cert-manager, ingress-nginx, external-secrets) upgrades before application layer.
- Use Helmfile `needs:` to enforce this ordering. Upgrades without `needs:` can run in parallel.
- Never upgrade cert-manager and applications that use it simultaneously — certificate reconciliation may interrupt mid-deploy.

**Helm in a Regulated Environment**
- Every `helm upgrade` must be traceable: log the chart version, values hash, git SHA, and operator identity to an audit trail (CloudTrail, Azure Monitor).
- Immutable releases: push chart versions to OCI as immutable artifacts (disable overwrite in Harbor/ECR). No mutable `latest` tag in production.
- Change approval: `helm diff upgrade` output is attached to the change ticket; reviewer approves the diff, not the chart.
