# Kong Gateway — Interview Prep

```
Kong Gateway
├── Core Architecture
│   ├── API Gateway: single entry point for all client requests
│   ├── Built on: NGINX + OpenResty (Lua); lives at nginx layer — not application code
│   ├── Service: pointer to backend (URL + protocol)
│   ├── Route: inbound matching rule (path, host, method, header) → maps to Service
│   ├── Plugin: feature attached to Route/Service/Consumer/Global (auth, rate limit, log)
│   ├── Consumer: entity (user/app) with credentials and rate limit policies
│   └── Upstream: load-balanced pool of backend targets behind a Service
├── Configuration Modes
│   ├── DB mode (Postgres): multiple Kong nodes share one DB; Admin API changes immediate
│   ├── DB-less (declarative): YAML/JSON kong.yml; no DB; reload required for changes
│   └── Hybrid mode: Control Plane (config) + Data Plane (proxying) separated
├── Plugin Architecture
│   ├── Plugin phases: init_worker → certificate → rewrite → access → header_filter → body_filter → log
│   ├── Plugin precedence: Consumer > Route > Service > Global (most specific wins)
│   ├── Built-in: rate-limiting, key-auth, jwt, oauth2, acl, cors, proxy-cache, request-transformer
│   ├── Custom plugin: handler.lua (phase logic) + schema.lua (config validation)
│   └── Plugin hub: 60+ official + community plugins
├── Kong in Kubernetes (KIC)
│   ├── Kong Ingress Controller: watches K8s API; pushes config to data plane pods
│   ├── CRDs: KongPlugin, KongConsumer, KongIngress, KongClusterPlugin
│   ├── Ingress resource: standard K8s Ingress + Kong annotations for plugins
│   └── DB-less mode typical in K8s; config derived from K8s objects (no Postgres needed)
├── Traffic Management
│   ├── Load balancing: round-robin, consistent-hash, least-connections on Upstream targets
│   ├── Active health checks: Kong polls backend; marks unhealthy on failures
│   ├── Passive health checks: circuit breaker; marks unhealthy on real request failures
│   ├── Canary routing: route plugin with request header/percentage split
│   └── Rate limiting: local (in-memory) or cluster (Redis); sliding vs fixed window
├── Admin API & decK
│   ├── Admin API: :8001 (HTTP) / :8444 (HTTPS); CRUD for all Kong entities
│   ├── Proxy port: :8000 (HTTP) / :8443 (HTTPS)
│   ├── decK CLI: dump → diff → sync → validate (GitOps for Kong config)
│   └── deck diff: shows what will change before applying — safe production workflow
├── Security
│   ├── Key auth: API key per Consumer; attached to Route or Service
│   ├── JWT: Consumer holds public key; Kong validates signature
│   ├── OAuth2: authorization code / client credentials / implicit flows
│   ├── mTLS: mutual TLS between Kong and upstream; client certificate validation
│   └── Vault integration: plugin config secrets fetched from Vault at runtime
└── Observability
    ├── Prometheus plugin: exposes /metrics; Kong request count, latency, upstream health
    ├── Zipkin / OpenTelemetry plugin: distributed trace propagation
    ├── File log / HTTP log / TCP log plugins: forward access logs to ELK/Splunk
    └── Status API: :8100/status — liveness; :8100/ready — readiness probe endpoint
```

## First Principles

- API Gateway is the single entry point for all client requests. Without a gateway, every service reimplements auth, rate limiting, and logging — N services × M cross-cutting concerns = N×M maintenance burden.
- Kong: reverse proxy + plugin architecture. Plugins add auth, rate limiting, logging, transformations without touching services. Cross-cutting concerns belong in the gateway, not in application code.
- Declarative config (decK) = GitOps for Kong. Every Kong entity (Service, Route, Plugin, Consumer) is version-controlled. `deck diff` before `deck sync` = safe, reviewable changes.
- Plugin precedence: Consumer > Route > Service > Global. More specific scope overrides less specific. This hierarchy enables per-user, per-endpoint, per-service, and global policies from one plugin system.
- Hybrid mode separates concerns: Control Plane manages config (Admin API); Data Plane handles proxying (Proxy port). Scale Data Planes independently for traffic without touching Control Plane.

## Overview

Think of Kong as a **security guard + traffic cop** that sits in front of all your backend services. Every API request from any client (mobile app, browser, another service) hits Kong first — Kong decides whether to let it through, rate-limit it, add auth headers, log it, and then forward it to the right backend.

**The short version:**
- You have 10 microservices. Without Kong, every service handles its own auth, rate limiting, logging, and routing.
- With Kong, those cross-cutting concerns move out of your services and into Kong. Your services just do their actual job.

**How it works internally:**

```
Client → Kong (Plugins run here) → Your Service → Response back through Kong → Client
```

Kong is built on top of **NGINX + OpenResty (Lua)**. It's extremely fast because it lives at the nginx layer — not in application code. Configuration is stored in **PostgreSQL or Cassandra** (DB mode) or in declarative YAML files (DB-less mode, common in Kubernetes).

**Key concepts:**
| Term | Plain English |
|------|---------------|
| Service | A pointer to your backend (URL + protocol) |
| Route | The rule that maps an incoming request to a Service (by path, host, method, header) |
| Plugin | A feature you attach to a Route or Service (auth, rate limit, logging, etc.) |
| Consumer | An entity (user/app) that calls your API — you attach credentials and rate limits to them |
| Upstream | A load-balanced pool of backend targets behind a Service |
| Gateway (Control Plane) | Manages config — the "brain" |
| Data Plane | The actual proxy that forwards traffic — can be scaled independently |

**DB-less vs DB mode:**
- **DB mode**: Kong reads config from Postgres. Multiple Kong nodes share one DB. Config changes via Admin API are immediate.
- **DB-less (declarative)**: Config lives in a YAML/JSON file (`kong.yml`). No database needed. Used in Kubernetes with Kong Ingress Controller (KIC). Changes require a config reload.

**Kong in Kubernetes:**
Kong runs as an Ingress Controller (`Kong Ingress Controller` / KIC). You define routes using standard Kubernetes `Ingress` objects or Kong-specific CRDs (`KongPlugin`, `KongConsumer`, `KongIngress`). The control plane watches the K8s API and pushes config to the data plane pods.

---

## Easy

**1. What is Kong Gateway and why would you use it instead of letting each service handle its own auth and routing?**

Kong is an API gateway — a reverse proxy that sits in front of your services. Instead of each service implementing rate limiting, authentication, and logging independently (duplicated code, inconsistent behavior), you centralize those concerns in Kong. Services stay lean; Kong handles the cross-cutting concerns.

**2. What are Services and Routes in Kong? How do they relate to each other?**

A **Service** defines where your backend is — the upstream URL (e.g., `http://user-service:8080`). A **Route** defines the inbound matching rule (e.g., path `/api/users`, host `api.example.com`). A Route is attached to a Service — when a request matches a Route's rules, Kong forwards it to that Route's Service.

**3. What is a Kong Plugin? Give two examples.**

A plugin is middleware that runs on requests/responses passing through Kong. Examples:
- `rate-limiting`: caps requests per consumer per minute/hour
- `key-auth`: requires clients to pass an API key in a header before the request goes through

**4. What is a Consumer in Kong?**

A Consumer represents a client that calls your API — a mobile app, a third-party partner, an internal service. You attach credentials (API keys, JWTs) and policies (rate limits) to Consumers, so different callers can have different access levels.

**5. What is the difference between the Admin API and the Proxy (runtime) port in Kong?**

- **Admin API** (default `:8001`): used to configure Kong — add Services, Routes, Plugins. Should never be public.
- **Proxy port** (default `:8000` HTTP, `:8443` HTTPS): the actual gateway that client traffic hits.

**6. How does Kong handle load balancing?**

Kong uses **Upstreams** — a named pool of backend **Targets** (host:port + weight). You point a Service at an Upstream name instead of a direct URL. Kong distributes requests across Targets using round-robin, consistent hashing, or least-connections, and can health-check Targets automatically.

**7. What is DB-less mode? When would you use it?**

DB-less mode runs Kong without a database — config is loaded from a declarative YAML file. It's preferred in Kubernetes (with Kong Ingress Controller) because you manage config through K8s manifests rather than API calls, making it GitOps-friendly and stateless.

**8. What is the Kong Ingress Controller (KIC)?**

KIC is a Kubernetes Ingress Controller that uses Kong as the underlying proxy. It watches Kubernetes `Ingress` objects and Kong-specific CRDs, translates them into Kong config, and applies them to the Kong data plane pods — so you manage routing through `kubectl` like any other K8s resource.

**9. How would you apply a rate limit of 100 requests/minute to a specific route?**

Attach the `rate-limiting` plugin to that Route:
```bash
curl -X POST http://localhost:8001/routes/{route_id}/plugins \
  --data name=rate-limiting \
  --data config.minute=100 \
  --data config.policy=local
```
Kong returns `429 Too Many Requests` once the limit is hit.

**10. What does the `key-auth` plugin do and how does a consumer use it?**

`key-auth` requires an API key on every request. After enabling the plugin on a Service/Route, you create a Consumer and generate a key credential for them. The consumer sends the key in a header (`apikey: <key>`) or query param. Kong validates it before forwarding the request.

---

## Medium

**1. Explain the Kong plugin execution lifecycle — what phases does a plugin run in?**

Kong plugins can hook into these phases:
- `init_worker`: runs once when the worker starts
- `certificate`: TLS cert selection (stream/HTTPS)
- `rewrite`: before routing decision — can rewrite the request
- `access`: main phase — auth checks, rate limiting, request transformation
- `header_filter`: modify response headers before sending to client
- `body_filter`: modify response body (chunked)
- `log`: async logging after response is sent — does not block the client

Most plugins primarily use `access` and `log`.

**2. What is the difference between applying a plugin globally vs. on a Service vs. on a Route vs. on a Consumer?**

Scope controls who it applies to:
- **Global**: every request through Kong
- **Service**: every request to a specific backend service
- **Route**: only requests matching that route
- **Consumer**: applies when that specific consumer is authenticated, regardless of route

Precedence (most specific wins): Consumer > Route > Service > Global. This lets you override a global rate limit with a higher limit for a premium consumer.

**3. How does Kong handle health checks for upstream targets?**

Two modes:
- **Active**: Kong periodically sends probes (HTTP GET to a health endpoint) to each Target and marks it healthy/unhealthy based on response codes and timeouts.
- **Passive (circuit breaker)**: Kong monitors actual traffic. If a target returns too many failures (5xx, timeouts), Kong marks it unhealthy automatically and stops routing to it. No extra probe traffic.

**4. How would you implement JWT authentication in Kong?**

1. Enable the `jwt` plugin on a Service or Route.
2. Create a Consumer.
3. Add a JWT credential to the Consumer (RS256 or HS256, provide the secret/public key).
4. Clients include the JWT in `Authorization: Bearer <token>`.
Kong validates signature, expiry (`exp`), and the `iss` claim matches the credential's key. If valid, the request proceeds; if not, Kong returns 401.

**5. What is Kong's control plane / data plane split and why does it matter in production?**

In **hybrid mode**, the control plane (CP) holds configuration and the Admin API — it never touches client traffic. Data planes (DP) handle actual proxying. They connect to the CP over a secure TLS WebSocket and receive config updates.

Why it matters: you can scale DPs independently across regions without touching the CP. A DP outage doesn't lose config (it caches locally). A CP outage doesn't drop traffic — DPs keep running on their last-known config.

**6. How do you do canary deployments with Kong?**

Use the `traffic-splitter` approach with an Upstream:
- Add two Targets to an Upstream: `service-v1` at weight 90, `service-v2` at weight 10.
- Kong distributes 10% of traffic to v2 automatically based on weights.
- Gradually shift weights as confidence grows.

Alternatively, use the `canary` plugin (Kong Enterprise) which can split by header, consumer group, or percentage without needing multiple targets.

**7. What is a Kong Declarative Config file (`kong.yml`) and what does it contain?**

A YAML file that describes all Kong entities — Services, Routes, Plugins, Consumers, Upstreams, Targets, Certificates — in one place. It's loaded at startup in DB-less mode or applied with `deck sync`. This enables GitOps: config lives in a repo, CI/CD applies it.

```yaml
_format_version: "3.0"
services:
  - name: user-service
    url: http://user-svc:8080
    routes:
      - name: users-route
        paths:
          - /api/users
    plugins:
      - name: rate-limiting
        config:
          minute: 200
```

**8. How does `decK` work and why is it useful?**

`decK` is a CLI tool to manage Kong config declaratively. It:
- **dumps** current Kong state to YAML
- **diffs** local YAML against live Kong state
- **syncs** local YAML to Kong (creates/updates/deletes entities to match)
- **validates** config before applying

This makes Kong config version-controllable and CI/CD deployable — you can treat Kong config like Terraform: plan (diff), apply (sync).

**9. How would you troubleshoot a 502 Bad Gateway returned by Kong?**

1. Check Kong error logs (`/usr/local/kong/logs/error.log`) for upstream connection errors.
2. Verify the Service URL is correct and reachable from Kong's network namespace.
3. Check Upstream health — are Targets healthy? (`GET /upstreams/{name}/health`).
4. Check if a plugin (e.g., `proxy-cache`) is caching a stale bad response.
5. Test the backend directly bypassing Kong to isolate whether it's Kong or the service.
6. Check timeouts — `connect_timeout`, `read_timeout`, `write_timeout` on the Service.

**10. What is the difference between `rewrite` and `request-transformer` plugins?**

- `rewrite` is a phase in the lifecycle, not a plugin — it runs before routing and is used internally.
- `request-transformer` is a plugin that modifies request headers, body, and query params in the `access` phase after routing. Use it to add/remove/rename headers (e.g., inject `X-Consumer-ID` into the upstream request, strip auth headers before forwarding).

---

## Hard

**1. How does Kong achieve microsecond-level latency at high throughput internally?**

Kong runs on **NGINX worker processes** using **OpenResty** (LuaJIT + `lua-nginx-module`). Lua code runs inside nginx's event loop — non-blocking, no threads, no GC pressure at the nginx layer. Plugin logic executes as Lua coroutines within the same process handling the HTTP connection, so there's no inter-process overhead. The shared memory zone (`ngx.shared.DICT`) is used for rate limiting counters without Redis for `policy=local`. Connection pooling to upstreams is handled by nginx's keepalive directives — persistent connections avoid TCP/TLS handshake cost per request.

**2. How would you design a multi-region Kong deployment with consistent config and low-latency routing?**

Use **hybrid mode** with one global Control Plane (or active-passive CP pair) and regional Data Plane clusters:
- CP deployed in a central region or as a managed Kong Konnect control plane.
- DP clusters deployed in each region (`us-east`, `eu-west`, `ap-south`) close to users.
- DPs pull config from CP over TLS; they cache config locally so a CP outage doesn't affect traffic.
- DNS or a global load balancer (Cloudflare, AWS Route 53 latency routing) directs clients to the nearest DP cluster.
- Backend services are also regional — Kong routes within-region to avoid cross-region backend calls.

**3. How would you implement fine-grained authorization in Kong beyond simple API key auth?**

Several approaches:
- **OPA plugin**: Kong calls an OPA sidecar with request context (path, method, consumer, headers). OPA evaluates Rego policy and returns allow/deny. Zero auth logic in services.
- **JWT + claims**: Use the `jwt` plugin with custom claim validation via a Lua custom plugin — inspect `role` or `scope` claims and reject requests that don't match the route's required permission.
- **Consumer Groups** (Kong Enterprise): group consumers, attach plugins per group (e.g., group `premium` gets 10k req/min, group `free` gets 100 req/min).
- **ACL plugin**: attach ACL groups to consumers and whitelist those groups on specific routes.

**4. How do you design and write a high-performance custom Kong plugin that integrates with external systems? Detail the phase restrictions, PDK cosocket limitations, and caching architecture.**

To build a high-performance custom Kong plugin (such as an external auth validator or dynamic router), you must structure the plugin as a Lua module consisting of at least `schema.lua` (configuration structure and field validation rules) and `handler.lua` (phase callback logic). 

When designing for production scale, you must address three major technical constraints:

### 1. The PDK Cosocket Barrier & Phase Restrictions
OpenResty handles concurrent connection scaling via non-blocking cosockets. However, NGINX only supports active cosocket networking inside specific lifecycle phases:
- **Allowed Phases**: `init_worker` (for background loops/timers), `certificate` (limited), `access` (fully supported).
- **Prohibited Phases**: `rewrite`, `header_filter`, `body_filter`, `log`.
If you attempt to perform a Redis lookup, a SQL query, or an outbound HTTP request using libraries like `resty.http` in `header_filter` or `body_filter`, OpenResty will throw a runtime exception ("no request found" or "API disabled"). Any external network call must execute in the `access` phase, and the resulting metadata should be shared with subsequent phases using the transaction context (`kong.ctx.shared`).

### 2. Implementation of a Two-Tier Caching Architecture
To protect external databases or auth services from connection pool exhaustion under high traffic, you must implement a hybrid caching strategy inside `handler.lua`:
- **Layer 1: Local Shared Memory (`ngx.shared.DICT`)**: Store validation flags directly in the worker process memory namespace (e.g., `kong_cache`). This is extremely fast (zero I/O overhead) and serves as the immediate hot cache.
- **Layer 2: External Distributed Cache (Redis)**: If the token is not present in local memory, establish a non-blocking connection to Redis over a cosocket to verify the token. 
- **Connection Pooling**: Always return the Redis connection back to the OpenResty socket pool using `red:set_keepalive(timeout, pool_size)` instead of calling `red:close()`, preserving pre-established TCP sessions.
- **Cache Fallback & Degradation**: If Redis is unreachable, design a fail-safe fallback (e.g., allow the request to pass with a degraded status header, or gracefully reject with a structured `403` exit using `kong.response.exit()`).

### 3. Structural Blueprint & PDK API Hook:
```lua
-- handler.lua
local redis = require "resty.redis"
local CustomAuthRouter = {
  PRIORITY = 1050, -- Runs early, before rate limiting
  VERSION = "1.0.0",
}

function CustomAuthRouter:access(config)
  local token = kong.request.get_header(config.header_name)
  if not token then
    return kong.response.exit(401, { message = "Missing Token" })
  end

  -- 1. Query Local SHM Cache
  local shm = ngx.shared.kong_cache
  local cached_status = shm:get("tok:" .. token)
  if cached_status == "VALID" then
    return -- Fast path
  elseif cached_status == "INVALID" then
    return kong.response.exit(403, { message = "Unauthorized Token" })
  end

  -- 2. Query Redis Cluster (Fallback)
  local red = redis:new()
  local ok, err = red:connect(config.redis_host, config.redis_port)
  if not ok then
    kong.log.err("Redis connection failure: ", err)
    kong.response.set_header("X-Cache-Degraded", "true")
    return
  end

  local res, err = red:get("auth:" .. token)
  if not res or res == ngx.null then
    shm:set("tok:" .. token, "INVALID", config.cache_ttl)
    red:set_keepalive(10000, 100)
    return kong.response.exit(403, { message = "Invalid Token Signature" })
  end

  shm:set("tok:" .. token, "VALID", config.cache_ttl)
  red:set_keepalive(10000, 100) -- Return to keepalive pool

  -- 3. Dynamic Service Override Hook
  local target_service = kong.request.get_header("X-Route-Target")
  if target_service then
    kong.service.set_upstream(target_service) -- Rewrites upstream destination
  end
end

return CustomAuthRouter
```

### 4. Unit and Integration Testing Strategy
Custom plugins should never be deployed without comprehensive test coverages:
- **Unit Testing**: Use the **Busted** test runner. Mock the global `kong` PDK table and assert that handler callbacks return the correct status codes (e.g. mock `kong.request.get_header` to return a value and verify `kong.response.exit` triggers as expected).
- **Integration Testing**: Use Kong’s official `spec.helpers` framework to spawn an ephemeral database-less Kong container, apply the plugin, send actual HTTP requests, and inspect returned response headers and upstream forwarding latencies.


**5. Explain Kong's approach to secret management — how do you avoid hardcoding credentials in plugin config?**

Kong supports **Vaults** — external secret backends that plugin configs can reference instead of raw values. Supported backends: HashiCorp Vault, AWS Secrets Manager, GCP Secret Manager, Azure Key Vault, environment variables.

Reference syntax in plugin config:
```yaml
config:
  secret: "{vault://aws/my-secret/api-key}"
```

Kong resolves the reference at runtime, caches the value with a configurable TTL, and re-fetches on rotation. This means secrets never appear in the Admin API response or in declarative config files committed to git.

**6. How does Kong handle TLS termination and mTLS between Kong and upstreams?**

**Client → Kong (TLS termination):** Kong terminates TLS using Certificates stored in its database. SNI objects map hostnames to Certificate entities. You can automate cert provisioning with the `acme` plugin (Let's Encrypt).

**Kong → Upstream (mTLS):** Set the Service's `tls_verify=true` and provide the upstream's CA cert. For client certificate auth, attach a `tls_metadata_headers` config or use the `mtls-auth` plugin — Kong presents a client cert to the upstream, proving its identity. This is common in zero-trust internal networks.

**7. How do you implement request/response transformation without writing a custom plugin?**

Use built-in transformation plugins in combination:
- `request-transformer`: add/remove/rename headers, body fields, query params on the way in.
- `response-transformer`: modify response headers and body fields.
- `jq` plugin (Enterprise): apply jq expressions to JSON request/response bodies for complex reshaping.
- `pre-function` / `post-function` plugins: run arbitrary Lua snippets in the `access` or `header_filter` phase without building a full plugin — useful for one-off logic that doesn't justify a plugin.

**8. How would you implement a circuit breaker pattern using Kong?**

Kong's **passive health checks** act as a circuit breaker on the upstream pool:
- Configure thresholds on the Upstream: e.g., if 5 consecutive failures or 50% of requests in a 10-second window return 5xx or time out, mark the target unhealthy.
- Kong stops routing to that target (opens the circuit).
- After `unhealthy.timeouts` period, Kong probes the target again (half-open). On success, it re-enters the pool.

For service-level (not just target-level) circuit breaking, combine with the `proxy-cache` plugin to serve cached responses during an outage, or use a `pre-function` plugin to check a shared dict flag and return a cached error response rather than letting requests queue up against a failing upstream.

**9. How do you manage Kong config across environments (dev/staging/prod) in a GitOps workflow?**

Structure:
```
kong/
  base/
    kong.yml          # shared Services, Routes, Consumers
  overlays/
    dev/values.yml    # env-specific: URLs pointing to dev backends, relaxed rate limits
    prod/values.yml   # prod URLs, strict limits, prod certs
```

Use `decK` with `--state` referencing the merged config per environment. In CI:
1. `deck diff --state kong/overlays/prod/kong.yml` — shows what will change, fails pipeline if drift detected.
2. On merge to main: `deck sync` applies changes to prod Kong.

Secrets (API keys, cert private keys) never go in the YAML — they're referenced via Vault or injected as env vars at sync time using `deck convert` with variable substitution.

**10. Kong is returning 504 Gateway Timeout intermittently under high load. Walk through your complete diagnosis.**

**Step 1 — Isolate where time is spent:**
- Enable the `zipkin` or `opentelemetry` plugin to get traces. Compare `kong.upstream_latency` vs `kong.proxy_latency` in logs. High `upstream_latency` = backend slow. High `proxy_latency` = Kong itself is the bottleneck.

**Step 2 — Upstream side:**
- Check active/passive health of targets: `GET /upstreams/{name}/health`. Any targets flapping?
- Check backend service metrics — CPU, memory, thread pool exhaustion.
- Increase `read_timeout` on the Service if the backend is legitimately slow (but this is a band-aid).

**Step 3 — Kong side:**
- Check `nginx worker_processes` — should match CPU count.
- Check `kong.conf` connection pool settings: `upstream_keepalive_pool_size`, `upstream_keepalive_max_requests`.
- If using DB mode, check Postgres query latency — slow config reads can block workers.
- Check if a plugin (e.g., `oauth2` with DB lookups) is adding per-request latency.

**Step 4 — Network:**
- TCP connection queue full? Check `netstat -s` for dropped connections on Kong hosts.
- DNS resolution latency? Kong caches DNS but with a TTL — if upstream hostnames churn, Kong may be hitting DNS on hot paths.

**Step 5 — Fix:**
- Scale DP pods horizontally.
- Move to local rate-limiting policy (no Redis round-trip per request).
- Pin upstreams to IPs instead of DNS names if DNS latency is the issue.
- Enable `proxy-cache` plugin for idempotent endpoints to reduce upstream load.

***

## System Design Perspective

**Kong as an Enterprise API Gateway**
- Multi-team governance: Global plugins (rate-limiting, logging) applied org-wide; Route/Service plugins for team-specific policies. Each team owns their Service + Route + Consumer definitions via decK; platform team owns Global plugins.
- decK GitOps workflow: developers PR changes to `kong.yml`; CI runs `deck validate` + `deck diff`; on merge, CD pipeline runs `deck sync`. Full audit trail in Git.
- Separation of planes in production: Control Plane (Admin API) in a private subnet; Data Plane in public-facing subnet. Data Plane nodes only need outbound to CP — never expose Admin API to internet.

**Kong Rate Limiting Design**
```
Local policy: in-memory counter per Kong pod
  → Fastest (no network round-trip)
  → Inaccurate in multi-pod deployments (each pod has own counter)

Redis policy: shared counter in Redis cluster
  → Accurate across all pods
  → Adds ~1ms Redis round-trip per request
  → Redis becomes a critical dependency — deploy Redis Sentinel or Cluster

Recommendation:
  - < 5 Kong pods: local policy acceptable
  - >= 5 pods or strict limits: Redis policy required
```

**Kong in a Service Mesh (Kong + Istio)**
- Kong handles North-South traffic (external clients → services): auth, rate limiting, API key management.
- Istio handles East-West traffic (service → service): mTLS, traffic splitting, circuit breaking.
- Complementary, not competing. Kong at the ingress; Istio sidecar-to-sidecar inside the mesh.
- KIC + Istio: Kong pod has Istio sidecar injected; Kong→upstream traffic is mTLS within the mesh; external→Kong traffic is standard TLS terminated at Kong.
