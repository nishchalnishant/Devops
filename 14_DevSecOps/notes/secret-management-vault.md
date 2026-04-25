---
description: HashiCorp Vault architecture, secret engines, dynamic secrets, Kubernetes auth, and production secret management patterns.
---

# DevSecOps — Secret Management & HashiCorp Vault

## Why Static Secrets Are a Risk

```
Static secret lifecycle (the dangerous way):
  1. Engineer generates API key → stores in .env file
  2. .env committed to Git (accidentally) → secret leaked
  3. Secret added to CI as environment variable → 50 pipelines share it
  4. Engineer leaves company → secret never rotated (no automation)
  5. 18 months later: breach traced to the old key

Dynamic secret lifecycle (the safe way):
  1. Application authenticates to Vault using its pod identity
  2. Vault generates a unique, short-lived credential for this specific pod
  3. Credential auto-expires in 1 hour
  4. Application renews via lease; on pod death, the credential dies too
  5. No human ever touches the secret
```

***

## Vault Architecture

```
┌─────────────────────────────────────────────┐
│                 Vault Server                 │
│                                             │
│  ┌──────────────┐    ┌───────────────────┐  │
│  │  Auth Methods │    │  Secret Engines   │  │
│  │  (Identity)   │    │  (Storage)        │  │
│  │               │    │                   │  │
│  │  - Kubernetes │    │  - KV v2 (static) │  │
│  │  - JWT/OIDC   │    │  - AWS (dynamic)  │  │
│  │  - AppRole    │    │  - Database       │  │
│  │  - TLS Cert   │    │  - PKI (certs)    │  │
│  └──────┬────────┘    └─────────┬─────────┘  │
│         │                      │             │
│  ┌──────▼──────────────────────▼──────────┐  │
│  │          Policy Engine (ACL)            │  │
│  └─────────────────────────────────────────┘  │
│                                             │
│  Storage Backend: Raft (integrated) / etcd / Consul │
└─────────────────────────────────────────────┘
```

***

## Auth Methods — How Applications Prove Identity

### Kubernetes Auth (Recommended for K8s workloads)

```bash
# Enable Kubernetes auth
vault auth enable kubernetes

# Configure — tell Vault how to verify K8s service account tokens
vault write auth/kubernetes/config \
  kubernetes_host="https://kubernetes.default.svc" \
  kubernetes_ca_cert=@/var/run/secrets/kubernetes.io/serviceaccount/ca.crt

# Create a role binding: pod with SA "api-server" in "production" namespace
# can read secrets at "secret/data/production/*"
vault write auth/kubernetes/role/api-server \
  bound_service_account_names=api-server \
  bound_service_account_namespaces=production \
  policies=api-server-policy \
  ttl=1h
```

**Policy definition:**
```hcl
# api-server-policy.hcl
path "secret/data/production/api-server/*" {
  capabilities = ["read"]
}

path "database/creds/api-server-role" {
  capabilities = ["read"]
}
```

### AppRole Auth (For CI/CD systems)

```bash
# Enable AppRole
vault auth enable approle

# Create role for Jenkins
vault write auth/approle/role/jenkins \
  secret_id_ttl=10m \       # Secret ID expires in 10 min (just enough time for CI)
  token_ttl=1h \
  token_max_ttl=4h \
  policies=jenkins-policy

# Get Role ID (public, embed in pipeline config)
vault read auth/approle/role/jenkins/role-id

# Generate Secret ID (private, one-time use)
vault write -f auth/approle/role/jenkins/secret-id
```

***

## Secret Engines

### KV v2 — Versioned Static Secrets

```bash
# Enable KV v2
vault secrets enable -path=secret kv-v2

# Write a secret
vault kv put secret/production/database \
  host="db.internal.company.com" \
  password="super-secret-123"

# Read
vault kv get secret/production/database

# Read specific version
vault kv get -version=2 secret/production/database

# List versions
vault kv metadata get secret/production/database
```

### Dynamic Database Credentials

```bash
# Enable database engine
vault secrets enable database

# Configure for PostgreSQL
vault write database/config/production-postgres \
  plugin_name=postgresql-database-plugin \
  allowed_roles="api-server-role" \
  connection_url="postgresql://{{username}}:{{password}}@postgres:5432/mydb" \
  username="vault-root-user" \
  password="vault-root-password"

# Define a role — Vault generates this SQL when creds are requested
vault write database/roles/api-server-role \
  db_name=production-postgres \
  creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; GRANT SELECT ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
  default_ttl="1h" \
  max_ttl="24h"

# Application requests credentials — gets a unique user
vault read database/creds/api-server-role
# Key                Value
# username           v-k8s-api-server-abc123
# password           A1B2C3D4-xxxx
# lease_duration     1h          ← Auto-rotates!
```

***

## Vault Agent — Auto-Injecting Secrets into Pods

```yaml
# Add Vault Agent as a sidecar via annotation (no code changes needed)
apiVersion: v1
kind: Pod
metadata:
  annotations:
    vault.hashicorp.com/agent-inject: "true"
    vault.hashicorp.com/role: "api-server"
    vault.hashicorp.com/agent-inject-secret-config.env: "secret/data/production/api-server/config"
    vault.hashicorp.com/agent-inject-template-config.env: |
      {{- with secret "secret/data/production/api-server/config" -}}
      export DATABASE_URL="postgresql://{{ .Data.data.db_user }}:{{ .Data.data.db_pass }}@postgres:5432/mydb"
      {{- end }}
spec:
  serviceAccountName: api-server   # Must match Vault Kubernetes role binding
  containers:
    - name: api
      # Secret injected at /vault/secrets/config.env
      command: ["/bin/sh", "-c"]
      args: ["source /vault/secrets/config.env && ./api-server"]
```

***

## PKI Secret Engine — Dynamic TLS Certificates

```bash
# Enable PKI
vault secrets enable pki
vault secrets tune -max-lease-ttl=87600h pki

# Generate Root CA
vault write pki/root/generate/internal \
  common_name="my-company.com Root CA" \
  ttl=87600h

# Create role for issuing certs
vault write pki/roles/web-servers \
  allowed_domains="internal.company.com" \
  allow_subdomains=true \
  max_ttl=720h       # 30-day certs

# Issue a cert (done by application)
vault write pki/issue/web-servers \
  common_name="api.internal.company.com"
```

***

## Logic & Trickiness Table

| Concept | Junior Thinking | Senior Thinking |
|:---|:---|:---|
| **Static vs Dynamic** | KV for everything | KV for config; Database/AWS engines for credentials that need rotation |
| **Token TTL** | Long TTL for convenience | Short TTL + token renewal; use `token_max_ttl` as a hard ceiling |
| **Vault HA** | Single node | Raft integrated storage with 3-5 nodes; auto-unseal with AWS KMS |
| **Seal/Unseal** | Manual unseal keys | Use Auto-Unseal (AWS KMS, GCP KMS) in production |
| **Audit logs** | Optional | Mandatory in production; enables forensic investigation of every secret access |
| **Lease renewal** | Application handles manually | Use Vault Agent or Vault Sidecar Injector to handle renewal transparently |
