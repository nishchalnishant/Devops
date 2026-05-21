# Advanced Helm Patterns

A technical deep-dive into enterprise Helm patterns: OCI-based chart distribution, library/helper chart architectures, and multi-chart orchestration with Helmfile.

---

## 1. OCI-Compliant Chart Distribution

Traditional Helm chart distribution relies on HTTP servers hosting tarballs along with a manually generated `index.yaml` file. This architecture is being deprecated in favor of **OCI (Open Container Initiative) Registry Distribution**, which allows developers to push, pull, and version Helm charts using the exact same registry infrastructure they use for Docker images (e.g. Harbor, AWS ECR, Azure ACR).

### OCI vs. Classic Registries
* **No `index.yaml`**: Standard OCI API searches replace the massive, monolithic index files.
* **Unified Security**: Leverage the same RBAC and vulnerability scanners used for container images.
* **Tagging Alignment**: Docker images and Helm charts can share identical SemVer tags inside the same repository namespace.

### CLI Workflow for OCI Charts
```bash
# 1. Authenticate to the OCI Registry
echo $PASSWORD | helm registry login registry.company.com -u username --password-stdin

# 2. Package the local chart
helm package ./my-app --version 1.4.2

# 3. Push the packaged chart (.tgz) to the OCI registry
helm push my-app-1.4.2.tgz oci://registry.company.com/helm-charts

# 4. Pull and extract the chart locally
helm pull oci://registry.company.com/helm-charts/my-app --version 1.4.2 --untar

# 5. Install the chart directly from the registry
helm install payment-release oci://registry.company.com/helm-charts/my-app --version 1.4.2
```

---

## 2. Library & Helper Charts

In microservice architectures, developers often end up copy-pasting standard Kubernetes files (e.g. Deployment templates, Service definitions, ConfigMaps) across dozens of Helm charts. **Library Charts** solve this by enabling you to define reusable templates once, package them, and reference them across many parent charts.

### Characteristics of a Library Chart:
* Has `type: library` in its `Chart.yaml`.
* Renders no resources on its own (contains no active templates in `templates/`, only named template definitions in files like `templates/_helpers.tpl`).

### Implementation Blueprint

#### A. Creating a Reusable Helper in the Library Chart (`my-library`)
```yaml
# Chart.yaml
apiVersion: v2
name: my-library
version: 1.0.0
type: library
```

Create a common Kubernetes Deployment structure inside the library helper file:
```yaml
# templates/_deployment.yaml
{{- define "my-library.common-deployment" -}}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "my-library.fullname" . }}
  labels:
    app: {{ include "my-library.name" . }}
spec:
  replicas: {{ .Values.replicaCount | default 1 }}
  selector:
    matchLabels:
      app: {{ include "my-library.name" . }}
  template:
    metadata:
      labels:
        app: {{ include "my-library.name" . }}
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          ports:
            - containerPort: {{ .Values.service.port }}
{{- end -}}
```

#### B. Importing and Executing in the Active Service Chart (`payment-service`)
Register the library chart as a dependency:
```yaml
# Chart.yaml
apiVersion: v2
name: payment-service
version: 0.1.0
dependencies:
  - name: my-library
    version: 1.0.0
    repository: "oci://registry.company.com/helm-charts"
```

Simply include the base template inside the parent's deployment structure:
```yaml
# templates/deployment.yaml
{{- include "my-library.common-deployment" . -}}
```
* **Benefit**: The parent chart contains only one line of layout code. If a global compliance policy changes (e.g. injecting a specific sidecar), you update the library chart, bump its version, and update dependencies.

---

## 3. Multi-Chart Orchestration using Helmfile

Managing complex platforms consisting of multiple independent releases (e.g. deploying cert-manager, ingress-nginx, Prometheus, and microservices together) becomes challenging with pure Helm commands. **Helmfile** provides a declarative, GitOps-compliant wrapper to define, order, and deploy multi-chart environments.

### Declaring a Multi-Release Environment (`helmfile.yaml`)
```yaml
# helmfile.yaml
repositories:
  - name: jetstack
    url: https://charts.jetstack.io
  - name: ingress-nginx
    url: https://kubernetes.github.io/ingress-nginx

environments:
  dev:
    values:
      - values/dev.yaml
  prod:
    values:
      - values/prod.yaml

releases:
  # Release 1: Core Networking dependency
  - name: cert-manager
    chart: jetstack/cert-manager
    namespace: kube-system
    version: v1.12.0
    values:
      - installCRDs: true

  # Release 2: Ingress Controller
  - name: ingress-nginx
    chart: ingress-nginx/ingress-nginx
    namespace: ingress-nginx
    version: 4.7.1
    needs:
      - kube-system/cert-manager # Ensures cert-manager is deployed first

  # Release 3: Custom Microservice
  - name: payment-api
    chart: ../charts/payment-api
    namespace: payments
    needs:
      - ingress-nginx/ingress-nginx
    values:
      - image:
          tag: {{ .Values.imageTag }}
      - replicaCount: {{ .Values.replicas }}
```

### CLI Workflow for Helmfile
```bash
# Validate local environment configurations
helmfile -e dev lint

# Check diff to see what will change in the cluster
helmfile -e dev diff

# Synchronize all releases (applies diffs, handles installation order)
helmfile -e dev apply

# Tear down the entire multi-chart platform safely
helmfile -e dev destroy
```

***

**Back to Module:** [Overview](../README.md) | [Cheatsheet](../cheatsheet.md) | [Interview Questions](../interview.md) | [Scenarios & Troubleshooting](../scenarios.md)
