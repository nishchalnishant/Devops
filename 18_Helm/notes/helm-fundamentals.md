# Helm Fundamentals

Deep dive into Helm chart structure, templating, values, hooks, repositories, and production patterns.

***

## 1. Chart Structure

```
mychart/
├── Chart.yaml          # Chart metadata
├── .helmignore         # Files to ignore when packaging
├── values.yaml         # Default values
├── values.schema.json  # Optional: JSON Schema for values validation
├── charts/             # Subchart dependencies (populated by helm dependency update)
├── templates/
│   ├── NOTES.txt       # Shown to user after install
│   ├── _helpers.tpl    # Named templates (not rendered as K8s objects)
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   └── hpa.yaml
└── crds/               # CRDs installed before other templates (no lifecycle management)
```

### Chart.yaml Fields
```yaml
apiVersion: v2               # Helm 3 only
name: my-application
description: "A web API with Redis cache"
type: application            # 'application' or 'library'
version: 1.5.0               # Chart version (SemVer) — increment when chart changes
appVersion: "2.3.1"          # Upstream app version (informational only)
dependencies:
  - name: redis
    version: "18.x.x"
    repository: "https://charts.bitnami.com/bitnami"
    condition: redis.enabled   # Only include if values.redis.enabled = true
```

***

## 2. Templating — Go Templates + Sprig

Helm templates use Go's `text/template` with the [Sprig](http://masterminds.github.io/sprig/) function library.

### Built-in Objects
```yaml
{{ .Values.image.tag }}        # From values.yaml or --set flags
{{ .Release.Name }}            # Release name (helm install my-app ...)
{{ .Release.Namespace }}       # Target namespace
{{ .Release.IsInstall }}       # true on install, false on upgrade
{{ .Chart.Name }}              # Chart name from Chart.yaml
{{ .Chart.Version }}           # Chart version
{{ .Capabilities.KubeVersion.GitVersion }}  # Kubernetes version
```

### Template Functions (most used)
```yaml
# String manipulation
{{ .Values.name | lower | replace "-" "_" }}
{{ printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" }}

# Defaults
{{ .Values.replicas | default 1 }}
{{ .Values.image.tag | default .Chart.AppVersion | quote }}

# Conditionals
{{- if .Values.ingress.enabled }}
# ... ingress manifest
{{- end }}

{{- if eq .Values.environment "production" }}
replicas: 3
{{- else }}
replicas: 1
{{- end }}

# Iteration
{{- range .Values.env }}
- name: {{ .name }}
  value: {{ .value | quote }}
{{- end }}

# Dict iteration
{{- range $key, $value := .Values.labels }}
{{ $key }}: {{ $value | quote }}
{{- end }}

# Required — fails template rendering if value is not set
{{ required "image.repository is required" .Values.image.repository }}

# toYaml — serialize a values block as YAML
resources:
  {{- toYaml .Values.resources | nindent 2 }}
```

### Named Templates (`_helpers.tpl`)
```yaml
{{/*
Common labels applied to all resources
*/}}
{{- define "mychart.labels" -}}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

# Usage in deployment.yaml:
metadata:
  labels:
    {{- include "mychart.labels" . | nindent 4 }}
```

***

## 3. Values — Merging and Overriding

Helm merges values in this order (last wins):
```
1. values.yaml defaults (in chart)
2. --values / -f flag files (left to right)
3. --set flags (highest priority)
```

### Structured Values Pattern
```yaml
# values.yaml
image:
  repository: myregistry.io/my-app
  tag: ""               # Empty = use .Chart.AppVersion
  pullPolicy: IfNotPresent

resources:
  requests:
    cpu: "100m"
    memory: "128Mi"
  limits:
    cpu: "500m"
    memory: "256Mi"

autoscaling:
  enabled: false
  minReplicas: 1
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80

serviceAccount:
  create: true
  annotations: {}        # For IRSA: eks.amazonaws.com/role-arn: arn:...
  name: ""
```

### Environment-specific overrides
```bash
# Staging override file: values-staging.yaml
helm upgrade --install my-app ./chart \
  --values values-staging.yaml \
  --set image.tag=${IMAGE_TAG} \
  --namespace staging

# Production: more replicas, larger resources, monitoring enabled
helm upgrade --install my-app ./chart \
  --values values-production.yaml \
  --set image.tag=${IMAGE_TAG} \
  --namespace production
```

### Values Schema Validation
```json
// values.schema.json — validates values before rendering
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "replicaCount": {
      "type": "integer",
      "minimum": 1,
      "maximum": 100
    },
    "image": {
      "type": "object",
      "required": ["repository"],
      "properties": {
        "repository": {"type": "string"},
        "tag": {"type": "string"}
      }
    }
  }
}
```

***

## 4. Lifecycle Hooks

Hooks run Kubernetes Jobs at specific lifecycle points:

| Hook Annotation | When It Runs |
|:---|:---|
| `pre-install` | Before any resources are installed |
| `post-install` | After all resources are installed |
| `pre-upgrade` | Before upgrade begins |
| `post-upgrade` | After upgrade completes |
| `pre-rollback` | Before rollback begins |
| `post-rollback` | After rollback completes |
| `pre-delete` | Before deletion begins |
| `post-delete` | After deletion completes |
| `test` | When `helm test` is run |

### Database Migration Hook Example
```yaml
# templates/job-db-migrate.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ .Release.Name }}-db-migrate
  annotations:
    "helm.sh/hook": pre-upgrade,pre-install
    "helm.sh/hook-weight": "-5"          # Lower = runs first
    "helm.sh/hook-delete-policy": hook-succeeded   # Clean up after success
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: migrate
          image: {{ .Values.image.repository }}:{{ .Values.image.tag }}
          command: ["python", "manage.py", "migrate"]
```

**Hook ordering with weights:** Multiple hooks of the same type run in weight order (ascending). A hook Job must complete successfully before Helm considers the phase done.

***

## 5. Repositories and OCI Registries

### Classic Helm Repository (index.yaml-based)
```bash
# Add a repository
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add stable https://charts.helm.sh/stable
helm repo update

# Search
helm search repo bitnami/redis --versions

# Pull chart locally for inspection
helm pull bitnami/redis --version 18.6.4 --untar
```

### OCI Registry (modern, recommended)
```bash
# Login
helm registry login registry.io --username myuser --password-stdin

# Push a chart
helm package ./mychart
helm push mychart-1.5.0.tgz oci://registry.io/charts

# Install from OCI
helm install my-app oci://registry.io/charts/mychart --version 1.5.0

# Pull for inspection
helm pull oci://registry.io/charts/mychart --version 1.5.0 --untar
```

***

## 6. Subcharts and Dependencies

```yaml
# Chart.yaml
dependencies:
  - name: postgresql
    version: "13.x.x"
    repository: "oci://registry-1.docker.io/bitnamicharts"
    condition: postgresql.enabled    # Only deploy if .Values.postgresql.enabled = true
    tags: [database]                 # Can enable/disable by tag group

  - name: redis
    version: "18.x.x"
    repository: "oci://registry-1.docker.io/bitnamicharts"
    condition: redis.enabled
```

```bash
# Fetch dependencies into charts/ directory
helm dependency update ./mychart

# Override subchart values with parent's values.yaml:
# Prefix the subchart name:
postgresql:
  auth:
    password: "mypassword"
  primary:
    persistence:
      size: "20Gi"
```

***

## 7. Helmfile — Multi-Chart Orchestration

Helmfile is a declarative spec for deploying multiple Helm releases with correct ordering and environment management:

```yaml
# helmfile.yaml
repositories:
  - name: bitnami
    url: https://charts.bitnami.com/bitnami

environments:
  staging:
    values:
      - environments/staging.yaml
  production:
    values:
      - environments/production.yaml

releases:
  - name: postgresql
    namespace: database
    chart: bitnami/postgresql
    version: "13.4.4"
    values:
      - postgresql/values.yaml
      - postgresql/values.{{ .Environment.Name }}.yaml

  - name: redis
    namespace: cache
    chart: bitnami/redis
    version: "18.6.4"
    needs:
      - database/postgresql     # Deploy postgresql first

  - name: my-app
    namespace: application
    chart: ./charts/my-app
    values:
      - my-app/values.{{ .Environment.Name }}.yaml
    needs:
      - cache/redis
      - database/postgresql
```

```bash
# Deploy all releases to staging
helmfile -e staging apply

# Diff before applying
helmfile -e production diff

# Destroy all
helmfile -e staging destroy
```

***

## 8. Testing Charts

### Helm Test Hook
```yaml
# templates/test-connection.yaml
apiVersion: v1
kind: Pod
metadata:
  name: "{{ .Release.Name }}-test"
  annotations:
    "helm.sh/hook": test
    "helm.sh/hook-delete-policy": hook-succeeded
spec:
  restartPolicy: Never
  containers:
    - name: test-curl
      image: curlimages/curl:8.1.0
      command:
        - curl
        - -s
        - -o
        - /dev/null
        - -w
        - "%{http_code}"
        - "http://{{ .Release.Name }}:{{ .Values.service.port }}/health"
```

```bash
helm test my-app --namespace production --logs
```

### Chart Linting and Unit Testing
```bash
# Lint chart for template errors
helm lint ./mychart
helm lint ./mychart --values values-staging.yaml

# Render templates locally without installing
helm template my-release ./mychart --values values-production.yaml

# Unit testing with helm-unittest plugin
helm plugin install https://github.com/helm-unittest/helm-unittest
helm unittest ./mychart
```

```yaml
# tests/deployment_test.yaml (helm-unittest)
suite: Deployment tests
templates:
  - templates/deployment.yaml
tests:
  - it: should set the correct image
    set:
      image.repository: myregistry.io/myapp
      image.tag: v2.0.0
    asserts:
      - equal:
          path: spec.template.spec.containers[0].image
          value: myregistry.io/myapp:v2.0.0
  
  - it: should default to 1 replica
    asserts:
      - equal:
          path: spec.replicas
          value: 1
```

***

## 9. Production Patterns

### Atomic Upgrades (all-or-nothing)
```bash
# --atomic: if any resource fails, automatically rollback
helm upgrade --install my-app ./chart \
  --atomic \
  --timeout 10m \
  --wait \           # Wait for all resources to be ready
  --cleanup-on-fail  # Delete new resources if upgrade fails
```

### Rollback
```bash
helm history my-app --namespace production  # List all revisions
helm rollback my-app 3 --namespace production --wait  # Roll back to revision 3
```

### Diff before upgrade (requires helm-diff plugin)
```bash
helm plugin install https://github.com/databus23/helm-diff
helm diff upgrade my-app ./chart --values values-production.yaml
# Shows exactly what would change before applying
```

### Chart Signing (Provenance)
```bash
# Sign chart with GPG key
helm package --sign --key 'My Company' --keyring ~/.gnupg/secring.gpg ./mychart
# Produces: mychart-1.5.0.tgz + mychart-1.5.0.tgz.prov

# Verify before install
helm install my-app mychart-1.5.0.tgz --verify
```
