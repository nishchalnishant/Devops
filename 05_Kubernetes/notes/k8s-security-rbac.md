---
description: Kubernetes RBAC, Pod Security, OPA/Gatekeeper, Secrets management, and supply chain security for senior engineers.
---

# Kubernetes — Security, RBAC & Policy

```
Kubernetes Security, RBAC & Policy
├── RBAC Architecture
│   ├── Who? — User / Group / ServiceAccount (subjects)
│   ├── What? — get, list, watch, create, update, patch, delete (verbs)
│   ├── On what? — pods, deployments, secrets, configmaps (resources)
│   ├── Role — namespace-scoped rules
│   ├── ClusterRole — cluster-wide rules (also reusable in RoleBinding)
│   ├── RoleBinding — binds Role/ClusterRole to subjects within a namespace
│   └── ClusterRoleBinding — binds ClusterRole cluster-wide
├── RBAC Key Properties
│   ├── Allow-only — no Deny rules; unmatched requests implicitly denied
│   ├── cluster-admin = root — bypasses all RBAC; treat like a root key
│   └── Prefer RoleBinding over ClusterRoleBinding for namespace-scoped access
├── ServiceAccount — Pod Identity
│   ├── Dedicated SA per workload (not the default SA)
│   ├── automountServiceAccountToken: false — disable unless pod calls K8s API
│   └── IRSA/Workload Identity — OIDC annotation → short-lived IAM credentials
├── Secrets Management
│   ├── K8s Secrets — base64 encoded (NOT encrypted); anyone with etcd access reads all
│   ├── Encryption at Rest — EncryptionConfiguration on API server (AES-GCM / KMS)
│   ├── External Secrets Operator (ESO) — sync from AWS SM / Vault / Azure KV
│   └── Best practice: don't put real secrets in K8s Secrets at all; use ESO + Vault
├── Pod Security Standards (PSS)
│   ├── Replaces deprecated PodSecurityPolicy (removed K8s 1.25)
│   ├── Applied via namespace labels (pod-security.kubernetes.io/enforce)
│   ├── privileged — unrestricted; allows everything
│   ├── baseline — blocks privileged containers, hostNetwork/ports, most caps
│   └── restricted — requires non-root, read-only FS, drops ALL capabilities
├── OPA / Gatekeeper — Policy as Code
│   ├── ConstraintTemplate — defines Rego policy schema as a CRD
│   ├── Constraint — instantiates policy with match rules + parameters
│   ├── Use cases: require labels, block :latest, enforce approved registries
│   └── failurePolicy: Fail — webhook unavailability blocks all pod creation
└── Audit & Compliance
    ├── API server audit logging — requestObject + user identity + timestamp
    ├── kubectl auth can-i --list — audit what a SA can do
    └── clusterrolebindings audit — find who has cluster-admin binding
```

## First Principles

- You need to control who can do what in the cluster — **RBAC** is an allow-only model; every unmatched request is implicitly denied; there are no explicit Deny rules.
- Pods need to call the Kubernetes API (operators, monitoring agents) — **ServiceAccounts** provide in-cluster identity; the JWT token is auto-mounted and used for authentication.
- Secrets stored in etcd are readable by anyone with etcd access — **encryption at rest** and **External Secrets Operator** (pulling from Vault/AWS SM) are the production-grade solutions.
- You need to enforce policy on what's inside objects, not just who creates them — **admission webhooks** (OPA Gatekeeper, Kyverno) run before objects are persisted to etcd and can block or mutate non-compliant resources.
- Zero-trust at the workload level — **IRSA/Workload Identity** binds a ServiceAccount to a cloud IAM role via OIDC; the pod receives short-lived, auto-rotating credentials instead of long-lived access keys.

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

## System Design Perspective

- **RBAC is not the whole security story:** RBAC controls who can create/modify objects, but it doesn't control what's inside those objects. A developer with `create pods` permission can create a privileged container with `hostNetwork: true` and bypass NetworkPolicy. **Pod Security Standards** (at the namespace level) and **OPA Gatekeeper/Kyverno** (at the admission webhook level) are complementary controls that restrict object content. Defense in depth requires all three layers: RBAC + PSS + admission policy.
- **ServiceAccount token blast radius:** The auto-mounted JWT token in every pod (`/var/run/secrets/kubernetes.io/serviceaccount/token`) is valid for the lifetime of the pod and has the permissions of the ServiceAccount. If an application is compromised, the attacker can use this token to enumerate cluster resources, read Secrets (if RBAC allows), and potentially escalate privileges. `automountServiceAccountToken: false` + dedicated minimal-permission ServiceAccounts limits this to only what the workload genuinely needs.
- **ESO sync interval is a security trade-off:** External Secrets Operator syncs from Vault/AWS SM on a `refreshInterval`. A 1-hour interval means a rotated secret takes up to 1 hour to reach pods. A 1-minute interval creates 1440 Vault/SM API calls per day per secret. Production recommendation: 15-30 minute refresh for most secrets; on-demand refresh (ESO `refreshInterval: 0` + manual annotation) for emergency rotation.
- **OPA Gatekeeper `failurePolicy: Fail` is a cluster availability risk:** If the Gatekeeper webhook is unavailable (pod crash, network partition), all resource creation/updates that match the webhook's rules will fail. This includes pod creation during node scale-up, breaking the cluster's ability to recover. Always configure webhook `namespaceSelector` to exclude `kube-system`, and run 2+ Gatekeeper replicas with a PDB.
- **OIDC group claims and RBAC scale:** Binding RBAC roles to OIDC groups (instead of individual users) means adding/removing a developer from a group in your IdP (Okta, Azure AD) immediately changes their cluster access without any Kubernetes change. This is the correct model at scale — Kubernetes RBAC becomes the policy layer, the IdP is the identity source of truth. Audit RBAC bindings for direct user subjects (not groups) as a compliance signal.
