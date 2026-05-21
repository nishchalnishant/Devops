# Kong Gateway Cheatsheet

A quick reference for the Kong Admin API, decK declarative CLI, configuration parameters, and common plugin overrides.

---

## 1. CLI Commands & Port Mappings

### Gateway Management
```bash
# Start/Stop/Restart Kong Gateway
kong start -c /etc/kong/kong.conf
kong stop
kong restart
kong reload      # Reloads NGINX without dropping connections

# Check status and configuration
kong health
kong version
```

### Port Allocations
* `8000`: HTTP Proxy port (client traffic)
* `8443`: HTTPS Proxy port (client traffic with TLS)
* `8001`: HTTP Admin API (internal control plane CRUD ops)
* `8444`: HTTPS Admin API (internal control plane CRUD with TLS)
* `8100`: Status API (liveness and readiness probes)
* `8002`: GUI Manager portal (Kong Enterprise)

---

## 2. Admin API Operations (cURL)

### Managing Services & Routes
```bash
# Create a Service (points to backend)
curl -i -X POST http://localhost:8001/services \
  --data name=payment-service \
  --data url=http://payment-backend.internal:8080

# Create a Route (rules that direct to a service)
curl -i -X POST http://localhost:8001/services/payment-service/routes \
  --data name=payment-route \
  --data paths[]=/v1/payments \
  --data methods[]=POST

# Create an Upstream and Target (load balancer setup)
curl -i -X POST http://localhost:8001/upstreams --data name=payment-upstream
curl -i -X POST http://localhost:8001/upstreams/payment-upstream/targets --data target=10.0.0.5:8080
curl -i -X POST http://localhost:8001/upstreams/payment-upstream/targets --data target=10.0.0.6:8080
```

### Managing Consumers & Credentials
```bash
# Create a Consumer (an API user/app)
curl -i -X POST http://localhost:8001/consumers --data username=mobile-app-client

# Add API Key credentials to a consumer
curl -i -X POST http://localhost:8001/consumers/mobile-app-client/key-auth \
  --data key=super-secret-api-key-123
```

### Attaching Plugins
```bash
# Enable Key-Auth globally
curl -i -X POST http://localhost:8001/plugins \
  --data name=key-auth

# Enable Rate-Limiting on a specific Service
curl -i -X POST http://localhost:8001/services/payment-service/plugins \
  --data name=rate-limiting \
  --data config.second=5 \
  --data config.hour=1000 \
  --data config.policy=local
```

---

## 3. decK Declarative Operations (GitOps)

Use `decK` to manage gateway config files without making direct Admin API calls in production.

```bash
# Export active configuration from Kong to a file
deck dump --output-file kong.yml

# Validate the local YAML configuration structure
deck validate --state kong.yml

# Compare the local file to the active Kong configuration
deck diff --state kong.yml

# Apply the declarative configuration to Kong
deck sync --state kong.yml

# Back up config before applying changes
deck sync --state kong.yml --backup-file kong-backup.yml
```

---

## 4. Declarative Configuration File (`kong.yml`)

A standard declarative configuration file used for DB-less modes and decK pipelines.

```yaml
_format_version: "1.1"
_transform: true

services:
  - name: billing-service
    url: http://billing-app.internal:8080
    connect_timeout: 60000
    write_timeout: 60000
    read_timeout: 60000
    routes:
      - name: billing-route
        paths:
          - /v1/billing
        methods:
          - GET
          - POST
        strip_path: true
    plugins:
      - name: rate-limiting
        config:
          minute: 60
          policy: local

consumers:
  - username: customer-portal
    keyauth_credentials:
      - key: portal-api-token-xyz
```

---

## 5. High-Impact Plugin Overrides

### Rate Limiting (Redis Policy)
Avoids counter discrepancies across multi-pod deployments.
```yaml
plugins:
  - name: rate-limiting
    config:
      minute: 100
      policy: redis
      redis_host: "redis-cluster.internal"
      redis_port: 6379
      redis_timeout: 2000
```

### CORS Configuration
Allow cross-origin resource requests for client-facing domains.
```yaml
plugins:
  - name: cors
    config:
      origins:
        - "https://app.example.com"
      methods:
        - GET
        - POST
        - OPTIONS
      headers:
        - Content-Type
        - Authorization
      credentials: true
      max_age: 3600
```

### Request Transformer
Transform payloads, add custom headers, or strip headers before forwarding to targets.
```yaml
plugins:
  - name: request-transformer
    config:
      add:
        headers:
          - "x-transaction-id:headers.x-request-id"
      remove:
        headers:
          - "x-internal-token"
```

***

**Back to Module:** [Overview](README.md) | [Detailed Notes](notes/kong-architecture-and-plugins.md) | [Interview Questions](interview.md) | [Scenarios & Troubleshooting](scenarios.md)
