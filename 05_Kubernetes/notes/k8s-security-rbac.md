---
description: Kubernetes RBAC, Pod Security, OPA/Gatekeeper, Secrets management, and supply chain security for senior engineers.
---

# Kubernetes — Security, RBAC & Policy

## RBAC Architecture

RBAC controls **what** authenticated identities can **do** in Kubernetes. It is always enabled in production clusters.

```
Subject (Who?)          Verb (What?)          Resource (On What?)
  │                          │                        │
  ▼                          ▼                        ▼
User / Group /           get, list,             pods, deployments,
ServiceAccount           create, delete         secrets, configmaps
        │
        └── Bound via RoleBinding or ClusterRoleBinding
```

***

## Roles vs ClusterRoles

```yaml
# Role — scoped to a single namespace
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: production
rules:
  - apiGroups: [""]
    resources: ["pods", "pods/log"]
    verbs: ["get", "list", "watch"]
  - apiGroups: ["apps"]
    resources: ["deployments"]
    verbs: ["get", "list"]

# ClusterRole — cluster-wide scope
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: node-reader
rules:
  - apiGroups: [""]
    resources: ["nodes"]
    verbs: ["get", "list", "watch"]
```

```yaml
# Bind a ClusterRole to a namespace (namespace-scoped access!)
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: dev-team-pods
  namespace: production
subjects:
  - kind: Group
    name: "dev-team"
    apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: pod-reader     # Using ClusterRole but binding is namespace-scoped
  apiGroup: rbac.authorization.k8s.io
```

***

## ServiceAccount — Pod Identity

```yaml
# Create a dedicated SA for each workload
apiVersion: v1
kind: ServiceAccount
metadata:
  name: api-server
  namespace: production
  annotations:
    # AWS IRSA: bind SA to IAM role for pod-level cloud permissions
    eks.amazonaws.com/role-arn: arn:aws:iam::ACCOUNT:role/api-s3-read

# Use in Pod
spec:
  serviceAccountName: api-server
  automountServiceAccountToken: false   # Disable unless needed
```

***

## Secrets Management

### The Problem with K8s Secrets

```bash
# K8s Secrets are base64 encoded, NOT encrypted
kubectl get secret my-secret -o jsonpath='{.data.password}' | base64 -d
# password123   ← Anyone with secret access can read this
```

### Encryption at Rest

```yaml
# /etc/kubernetes/encryption-config.yaml (on API server)
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
  - resources:
      - secrets
    providers:
      - aescbc:
          keys:
            - name: key1
              secret: BASE64_ENCODED_32_BYTE_KEY
      - identity: {}    # Fallback for unencrypted secrets
```

### External Secrets Operator (Recommended)

```yaml
# Sync secrets from AWS Secrets Manager into K8s
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: db-credentials
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager
    kind: ClusterSecretStore
  target:
    name: db-credentials      # Name of the K8s Secret to create
  data:
    - secretKey: password     # K8s Secret key
      remoteRef:
        key: prod/db          # AWS Secrets Manager key
        property: password
```

***

## Pod Security Standards (PSS)

Replaces the deprecated PodSecurityPolicy. Applied at the namespace level via labels.

```yaml
# Apply security standard to a namespace
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    pod-security.kubernetes.io/enforce: restricted  # Enforce strict policy
    pod-security.kubernetes.io/warn: restricted
    pod-security.kubernetes.io/audit: restricted
```

| Level | What It Blocks |
|:---|:---|
| `privileged` | Unrestricted (allows everything) |
| `baseline` | Blocks privileged containers, host networking/ports, most capabilities |
| `restricted` | Heavily restricted — requires non-root, read-only FS, drops all capabilities |

***

## OPA / Gatekeeper — Policy as Code

```yaml
# ConstraintTemplate: defines the policy schema
apiVersion: templates.gatekeeper.sh/v1beta1
kind: ConstraintTemplate
metadata:
  name: k8srequiredlabels
spec:
  crd:
    spec:
      names:
        kind: K8sRequiredLabels
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8srequiredlabels
        violation[{"msg": msg}] {
          provided := {label | input.review.object.metadata.labels[label]}
          required := {label | label := input.parameters.labels[_]}
          missing := required - provided
          count(missing) > 0
          msg := sprintf("Missing required labels: %v", [missing])
        }

# Constraint: enforce the policy
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sRequiredLabels
metadata:
  name: require-team-label
spec:
  match:
    kinds:
      - apiGroups: ["apps"]
        kinds: ["Deployment"]
  parameters:
    labels: ["team", "env", "version"]
```

***

## Logic & Trickiness Table

| Concept | Common Mistake | Senior Understanding |
|:---|:---|:---|
| **RBAC deny** | Looking for Deny rules | RBAC is allow-only. Any unmatched request is implicitly denied. |
| **`cluster-admin`** | Bind it to service accounts "for convenience" | `cluster-admin` bypasses all RBAC — treat it like root |
| **SA token mounting** | Leave `automountServiceAccountToken: true` | Disable on pods that don't call the K8s API; reduces blast radius |
| **Secrets base64** | Think it's encryption | base64 is encoding, not encryption. Always encrypt at rest + use ESO |
| **PSP deprecation** | Still using PSP on K8s 1.25+ | Use Pod Security Standards + OPA/Gatekeeper |
| **Audit logging** | Not enabled | Enable API server audit logging to track who did what and when |
