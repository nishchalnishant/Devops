# Helm Cheatsheet

Quick reference for Helm CLI commands, template functions, and production patterns.

***

## CLI Reference

### Installation and Repository Management
```bash
# Install Helm (macOS)
brew install helm

# Repository management
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update                              # Refresh all repo indexes
helm repo list                                # List added repositories
helm repo remove bitnami                      # Remove a repository
helm search repo nginx --versions             # List all versions of a chart
helm search hub nginx                         # Search Artifact Hub
```

### Release Lifecycle
```bash
# Install
helm install my-app ./chart                   # Install from local chart
helm install my-app bitnami/nginx             # Install from repository
helm install my-app oci://registry.io/charts/app --version 1.2.3  # OCI
helm install my-app ./chart -f values-prod.yaml --set image.tag=v2.0.0
helm install my-app ./chart --namespace production --create-namespace
helm install my-app ./chart --dry-run --debug  # Preview without installing

# Upgrade
helm upgrade my-app ./chart                   # Upgrade existing release
helm upgrade --install my-app ./chart         # Install if not exists; upgrade if exists
helm upgrade my-app ./chart --atomic --timeout 10m --wait

# Rollback
helm rollback my-app                          # Roll back to previous revision
helm rollback my-app 3                        # Roll back to specific revision

# Uninstall
helm uninstall my-app --namespace production
helm uninstall my-app --keep-history          # Keep release history after uninstall

# Status and history
helm status my-app --namespace production
helm history my-app --namespace production
helm list --all-namespaces                    # List all releases
helm list --namespace production --failed     # List failed releases only
```

### Inspection and Debugging
```bash
# Inspect chart
helm show chart bitnami/redis                 # Chart.yaml
helm show values bitnami/redis                # Default values.yaml
helm show all bitnami/redis                   # Everything

# Template rendering (dry run)
helm template my-app ./chart -f values-prod.yaml  # Render to stdout
helm template my-app ./chart --output-dir ./rendered  # Write to files

# Get deployed release info
helm get values my-app --namespace production          # Values used in release
helm get manifest my-app --namespace production        # Rendered YAML applied to cluster
helm get hooks my-app                                  # Hook resources
helm get all my-app                                    # Everything

# Diff (requires helm-diff plugin)
helm diff upgrade my-app ./chart -f values-prod.yaml
```

### Plugins
```bash
helm plugin list
helm plugin install https://github.com/databus23/helm-diff
helm plugin install https://github.com/helm-unittest/helm-unittest
helm plugin install https://github.com/jkroepke/helm-secrets  # Secrets management
```

***

## Template Function Quick Reference

### String Functions
```yaml
{{ .Values.name | lower }}                         # lowercase
{{ .Values.name | upper }}                         # UPPERCASE
{{ .Values.name | title }}                         # Title Case
{{ .Values.name | trim }}                          # Remove whitespace
{{ .Values.name | trimSuffix "-" }}               # Remove suffix
{{ .Values.name | trunc 63 }}                     # Truncate to 63 chars
{{ printf "%s-%s" .Release.Name .Chart.Name }}    # String formatting
{{ .Values.name | replace "-" "_" }}              # Replace characters
{{ .Values.name | b64enc }}                       # Base64 encode (for secrets)
{{ .Values.secret | b64dec }}                     # Base64 decode
{{ .Values.name | sha256sum }}                    # SHA256 hash
{{ .Values.name | quote }}                        # Wrap in double quotes
{{ .Values.name | squote }}                       # Wrap in single quotes
{{ .Values.name | nospace }}                      # Remove all spaces
```

### Type Conversion and Validation
```yaml
{{ .Values.port | int }}                          # Convert to integer
{{ .Values.enabled | toString }}                  # Convert to string
{{ .Values.port | toString | quote }}             # Convert then quote

# Required — fails rendering if empty
{{ required "image.repository must be set" .Values.image.repository }}

# Default value
{{ .Values.replicas | default 1 }}
{{ .Values.tag | default .Chart.AppVersion }}

# Check if key exists
{{- if hasKey .Values "serviceAccount" }}
# ...
{{- end }}
```

### Collections
```yaml
# List operations
{{ list "a" "b" "c" | join "," }}               # "a,b,c"
{{ .Values.tags | toStrings | join " " }}

# Dict operations  
{{ dict "key" "value" | toYaml }}
{{ .Values.annotations | toYaml | nindent 4 }}  # Render as YAML, indent 4 spaces

# Merge dicts
{{ merge .Values.labels (dict "app" .Release.Name) | toYaml | nindent 4 }}
```

### Indentation (Critical!)
```yaml
# nindent: adds newline + N spaces of indentation (use for blocks)
spec:
  containers:
    - name: app
      resources:
        {{- toYaml .Values.resources | nindent 8 }}    # Correct: 8 spaces

# indent: N spaces, no leading newline (use for inline)
annotations:
  config: |
    {{- .Values.config | indent 4 }}
```

***

## Conditional Patterns

```yaml
# Simple if/else
replicas: {{ if eq .Values.env "production" }}3{{ else }}1{{ end }}

# Multi-line block (note whitespace trimming with -)
{{- if .Values.ingress.enabled }}
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{ .Release.Name }}-ingress
  {{- with .Values.ingress.annotations }}
  annotations:
    {{- toYaml . | nindent 4 }}
  {{- end }}
{{- end }}

# Checking multiple conditions
{{- if and .Values.persistence.enabled (not .Values.persistence.existingClaim) }}
# Create a new PVC
{{- end }}

# Ternary
{{ ternary "enabled" "disabled" .Values.feature.enabled }}
```

***

## Iteration Patterns

```yaml
# Iterate over a list
env:
{{- range .Values.extraEnv }}
  - name: {{ .name }}
    value: {{ .value | quote }}
{{- end }}

# Iterate over a dict (sorted by key for reproducibility)
{{- range $key, $val := .Values.labels }}
  {{ $key }}: {{ $val | quote }}
{{- end }}

# Range with index
{{- range $i, $svc := .Values.services }}
  - name: svc-{{ $i }}
    port: {{ $svc.port }}
{{- end }}
```

***

## Named Templates Pattern

```yaml
# _helpers.tpl — define reusable templates
{{- define "app.fullname" -}}
{{- printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "app.labels" -}}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
app.kubernetes.io/name: {{ include "app.fullname" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "app.selectorLabels" -}}
app.kubernetes.io/name: {{ include "app.fullname" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

# Usage in deployment.yaml
metadata:
  name: {{ include "app.fullname" . }}
  labels:
    {{- include "app.labels" . | nindent 4 }}
spec:
  selector:
    matchLabels:
      {{- include "app.selectorLabels" . | nindent 6 }}
```

***

## Common values.yaml Patterns

```yaml
# Image pattern (with digest support)
image:
  repository: myregistry.io/app
  tag: ""                        # Defaults to .Chart.AppVersion
  digest: ""                     # If set, overrides tag: sha256:abc123
  pullPolicy: IfNotPresent

# RBAC pattern
serviceAccount:
  create: true
  automount: false
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::123:role/my-role  # IRSA
  name: ""                       # Auto-generated if empty

# Resources pattern (always set both requests and limits)
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 256Mi

# Probes pattern
livenessProbe:
  httpGet:
    path: /healthz
    port: http
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /ready
    port: http
  initialDelaySeconds: 5
  periodSeconds: 5

# HPA pattern
autoscaling:
  enabled: false
  minReplicas: 2
  maxReplicas: 20
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80

# Ingress pattern
ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: api.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: api-tls
      hosts:
        - api.example.com
```

***

## Common Issues & Fixes

| Issue | Cause | Fix |
|:---|:---|:---|
| `Error: INSTALLATION FAILED: cannot re-use a name` | Release already exists | Use `helm upgrade --install` |
| Rendering produces extra blank lines | Missing `{{-` / `-}}` whitespace trimming | Add `-` to trim surrounding whitespace |
| `Error: chart requires kubeVersion: >= 1.25` | Cluster version too old | Upgrade cluster or use older chart version |
| Values not overriding subchart defaults | Incorrect key prefix | Prefix with subchart name: `redis.auth.password` |
| Hook job keeps running | Previous hook job not cleaned up | Add `helm.sh/hook-delete-policy: hook-succeeded` |
| `helm upgrade` hangs | Resource stuck in non-ready state | `kubectl describe` the resource; check events |
| NOTES.txt not showing | Template rendering error | `helm template` to debug |
