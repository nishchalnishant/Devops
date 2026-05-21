# Kong Gateway Architecture & Custom Plugins

An in-depth look at Kong’s enterprise runtime architecture, execution phases, and step-by-step custom plugin design.

---

## 1. Hybrid Mode (Control Plane / Data Plane Separation)

In high-traffic enterprise environments, Kong is deployed in **Hybrid Mode**. This pattern separates configuration management from real-time client proxying to minimize latency, eliminate single points of failure, and enforce absolute security boundaries.

```
       Admin API / decK
              │
              ▼
   ┌─────────────────────┐
   │    Control Plane    │ (Private Subnet)
   │  (Manages Postgres) │
   └──────────┬──────────┘
              │
              │ mTLS (Port 8005)
              │ Config Sync Push (JSON/Protobuf)
              ▼
   ┌─────────────────────┐
   │    Data Plane Node  │ (Public DMZ Subnet)
   │ (Runs purely in-mem)│
   └──────────┬──────────┘
              │
              ▼
       [ Client Traffic ]
```

### Key Operational Characteristics:
* **In-Memory Operation**: Data Plane (DP) nodes run entirely stateless. They store no database credentials and perform no local database lookups. Configurations are stored entirely in local memory (RAM).
* **Communication Isolation**: DPs and the Control Plane (CP) communicate strictly over mutual TLS (mTLS) via ports `8005` (configuration push) and `8006` (status checks).
* **High Availability**: If the CP node fails or is disconnected, all DP nodes continue to serve inbound traffic without interruption using their cached in-memory configuration state.

---

## 2. NGINX & OpenResty Execution Phases

Kong leverages OpenResty to hook custom Lua scripts directly into NGINX's request-response lifecycle. When a request hits the gateway, it progresses through a strict sequence of execution phases. Knowing these phases is vital for designing high-performance custom plugins.

```
[ Client Request ]
       │
       ▼
 1. init_worker  ──► Runs once when NGINX worker starts (background tasks)
       │
       ▼
 2. certificate  ──► SSL/TLS handshake phase; dynamic SSL cert association
       │
       ▼
 3. rewrite      ──► Path rewrites, header injection (before routing)
       │
       ▼
 4. access       ──► Core auth, rate-limiting, IP restrictions (pre-proxy)
       │
       ▼
[ Forwarded to Upstream Target ]
       │
       ▼
 5. header_filt  ──► Inspects/adds/removes headers from upstream response
       │
       ▼
 6. body_filter  ──► Modifies response payload (canary payload changes)
       │
       ▼
 7. log          ──► Asynchronous logging phase (no client block)
```

| Phase | Kong Plugin Function | Ideal Use Cases |
|:---|:---|:---|
| **init_worker** | `init_worker()` | Instantiating timers, background cache syncs, connection pools. |
| **certificate** | `certificate()` | Selecting SSL certificates dynamically based on SNI headers. |
| **rewrite** | `rewrite()` | Rewriting URI paths, executing basic redirects before route matching. |
| **access** | `access()` | **Most active phase**: executing JWT/OAuth authentication, checking rate limits. |
| **header_filter**| `header_filter()` | Stripping internal headers, injecting correlation IDs, configuring CORS headers. |
| **body_filter** | `body_filter()` | Buffering and transforming JSON bodies, injecting scripts into responses. |
| **log** | `log()` | Streaming metrics to Prometheus, pushing logs asynchronously to Syslog/Splunk. |

---

## 3. Developing Custom Lua Plugins

A Kong custom plugin is a self-contained Lua package that extends the gateway's core functionality. To achieve production-grade performance and security, a developer must master the OpenResty execution contexts, PDK (Plugin Development Kit) restrictions, caching mechanisms, and testing strategies.

### A. Core Architecture & Lifecycle Callback Mechanics

Every callback in a Kong plugin executes inside a distinct NGINX worker context. Designing custom plugins requires an understanding of what NGINX APIs and resources are accessible during each phase.

```
       Worker Lifecycle (Phase Hook Diagram)
       ┌──────────────────────────────────────┐
       │             init_worker              │  <-- Executes once per worker process.
       └──────────────────┬───────────────────┘      Ideal for long-running cron timers.
                          │
                  Dynamic DNS/TLS
       ┌──────────────────▼───────────────────┐
       │             certificate              │  <-- Terminates SSL handshakes.
       └──────────────────┬───────────────────┘      No cosockets allowed here!
                          │
                  Pre-Routing Logic
       ┌──────────────────▼───────────────────┐
       │               rewrite                │  <-- Path/domain rewrite prior to router.
       └──────────────────┬───────────────────┘      Strict PDK constraints.
                          │
                 Inbound Interception
       ┌──────────────────▼───────────────────┐
       │                access                │  <-- Auth, rate limiting, service routing.
       └──────────────────┬───────────────────┘      **Cosockets fully open (e.g. Redis/HTTP)**.
                          │
                    [ Upstream ]
                          │
                 Outbound Formatting
       ┌──────────────────▼───────────────────┐
       │            header_filter             │  <-- Modify response HTTP headers.
       └──────────────────┬───────────────────┘      No body reading or cosockets.
                          │
       ┌──────────────────▼───────────────────┐
       │             body_filter              │  <-- Dynamic streaming payload body changes.
       └──────────────────┬───────────────────┘      Invoked in chunks. Very strict RAM budget.
                          │
                    Post-Response
       ┌──────────────────▼───────────────────┐
       │                 log                  │  <-- Non-blocking analytics / stream logs.
       └──────────────────────────────────────┘      Client has disconnected. Must use ngx.timer.
```

> [!WARNING]
> **The Cosocket Barrier**: You cannot perform active networking block operations (like Redis queries, database lookups, or outbound HTTP requests) inside `rewrite`, `certificate`, `header_filter`, or `body_filter` phases. Doing so will throw a runtime panic because NGINX does not support non-blocking cosocket I/O during these phases. Any remote dependency must be resolved during the `access` phase and shared via NGINX context variables (`kong.ctx.shared`).

---

### B. Production-Grade Custom Plugin: `custom-header-auth-router`

This plugin intercepts inbound requests, validates a signature token using a Redis cache (with fallback to an API endpoint), caches the result locally in the OpenResty shared dict memory (`ngx.shared`), and dynamically overrides the upstream routing destination based on a payload parameter.

#### 1. Configuration Validation Schema (`schema.lua`)
A robust schema enforces type-safety and field validation at the Admin API interface, avoiding runtime parser exceptions.

```lua
-- schema.lua
local typedefs = require "kong.db.schema.typedefs"

return {
  name = "custom-header-auth-router",
  fields = {
    {
      config = {
        type = "record",
        fields = {
          {
            header_name = {
              type = "string",
              default = "X-Enterprise-Token",
              required = true,
            },
          },
          {
            redis_host = {
              type = "string",
              default = "127.0.0.1",
              required = true,
            },
          },
          {
            redis_port = {
              type = "number",
              default = 6379,
              required = true,
            },
          },
          {
            cache_ttl = {
              type = "number",
              default = 60, -- 1-minute local cache TTL
              required = true,
            },
          },
          {
            dynamic_routing_header = {
              type = "string",
              default = "X-Route-Target",
              required = true,
            },
          },
        },
      },
    },
  },
}
```

#### 2. Execution logic (`handler.lua`)
The handler implements high-performance, non-blocking connection pooling and dynamic service rewriting.

```lua
-- handler.lua
local redis = require "resty.redis"
local kong = kong

local CustomRouterHandler = {
  PRIORITY = 1050, -- Runs BEFORE default rate-limiting (900) but AFTER IP restriction (1900)
  VERSION = "1.0.0",
}

-- Resolve token using shared dict local cache (Layer 1) before querying Redis (Layer 2)
local function get_cached_token_status(token, ttl)
  local shm = ngx.shared.kong_cache
  if not shm then
    return nil
  end

  local val, err = shm:get("auth_tok:" .. token)
  if val then
    return val -- Returns "VALID" or "INVALID"
  end
  return nil
end

local function set_cached_token_status(token, status, ttl)
  local shm = ngx.shared.kong_cache
  if shm then
    shm:set("auth_tok:" .. token, status, ttl)
  end
end

-- Access phase callback logic
function CustomRouterHandler:access(config)
  local token = kong.request.get_header(config.header_name)

  if not token then
    return kong.response.exit(401, { message = "Unauthorized: Missing dynamic security token" })
  end

  -- Check Layer 1 Local Cache
  local cached_status = get_cached_token_status(token, config.cache_ttl)
  if cached_status == "INVALID" then
    return kong.response.exit(403, { message = "Forbidden: Invalid authorization credentials (Cached)" })
  end

  if not cached_status then
    -- Layer 2: Query Redis over non-blocking cosocket
    local red = redis:new()
    red:set_timeouts(1000, 1000, 1000) -- Connect, send, read timeouts (1s)
    
    local ok, err = red:connect(config.redis_host, config.redis_port)
    if not ok then
      kong.log.err("Failed to connect to Redis cluster: ", err)
      -- Graceful degradation: Fall back to downstream target under audit logs
      kong.response.set_header("X-Auth-Degraded", "true")
    else
      -- Check key existence
      local res, err = red:get("auth:" .. token)
      if not res or res == ngx.null then
        set_cached_token_status(token, "INVALID", config.cache_ttl)
        red:close()
        return kong.response.exit(403, { message = "Forbidden: Token signature validation failed" })
      end

      -- Token is valid! Cache locally to prevent CPU/IO throttling
      set_cached_token_status(token, "VALID", config.cache_ttl)
      
      -- Close or return to pool (highly recommended)
      red:set_keepalive(10000, 100) -- Max idle 10s, pool size 100
    end
  end

  -- Dynamic Routing Resolution Phase
  local route_target = kong.request.get_header(config.dynamic_routing_header)
  if route_target then
    -- Overrides the current Service target with a dynamic upstream
    local ok, err = kong.service.set_upstream(route_target)
    if not ok then
      kong.log.err("Failed to route request dynamically to upstream [", route_target, "]: ", err)
      return kong.response.exit(502, { message = "Bad Gateway: Dynamic route resolution failed" })
    end
    kong.log.info("Request dynamically routed to upstream: ", route_target)
  end
end

-- Asynchronous Logging Phase (Non-blocking)
function CustomRouterHandler:log(config)
  local ctx = kong.ctx.shared
  -- Perform stats buffering or telemetry streams without blocking downstream client response
end

return CustomRouterHandler
```

---

### C. Testing Custom Plugins (Busted Framework)

To verify custom plugin stability and guard against memory leaks, use the `busted` unit testing framework. We mock the `kong` PDK globals and assert behaviors under different execution phases.

```lua
-- spec/custom-header-auth-router/01-unit_spec.lua
local schema = require "kong.plugins.custom-header-auth-router.schema"
local handler = require "kong.plugins.custom-header-auth-router.handler"
local v = require "spec.helpers"

describe("Plugin: custom-header-auth-router (Unit)", function()
  setup(function()
    _G.kong = {
      request = {
        get_header = function(name)
          if name == "X-Enterprise-Token" then
            return "valid_test_token"
          end
          return nil
        end
      },
      response = {
        exit = function(status, body)
          return { status = status, body = body }
        end
      },
      log = {
        err = function(...) end,
        info = function(...) end,
      }
    }
  end)

  it("should fail validation if X-Enterprise-Token header is missing", function()
    -- Temporarily patch get_header to return nil
    local original_header = _G.kong.request.get_header
    _G.kong.request.get_header = function() return nil end

    local conf = { header_name = "X-Enterprise-Token" }
    local res = handler:access(conf)

    assert.is_table(res)
    assert.equal(401, res.status)

    _G.kong.request.get_header = original_header
  end)
end)
```

### D. Packaging & Deployment inside Kubernetes (GitOps Pipeline)

For enterprise high-availability platforms, custom plugins are compiled as standard rocks and baked into the base image.

1. **Write a Luarocks Spec (`kong-plugin-custom-header-auth-router-1.0.0-1.rockspec`)**:
   ```lua
   package = "kong-plugin-custom-header-auth-router"
   version = "1.0.0-1"
   supported_platforms = {"linux", "macosx"}
   source = {
     url = "git://github.com/enterprise/kong-custom-plugins.git"
   }
   description = {
     summary = "Custom token validation and dynamic upstream routing plugin.",
   }
   dependencies = {
     "lua >= 5.1"
   }
   build = {
     type = "builtin",
     modules = {
       ["kong.plugins.custom-header-auth-router.handler"] = "kong/plugins/custom-header-auth-router/handler.lua",
       ["kong.plugins.custom-header-auth-router.schema"] = "kong/plugins/custom-header-auth-router/schema.lua",
     }
   }
   ```
2. **Compile and Bake into Dockerfile**:
   ```dockerfile
   FROM kong/kong-gateway:3.4
   USER root
   RUN apk add --no-cache git build-base
   COPY . /tmp/custom-plugin
   WORKDIR /tmp/custom-plugin
   RUN luarocks make
   USER kong
   ENV KONG_PLUGINS=bundled,custom-header-auth-router
   ```
3. **Register in Kubernetes Custom Resource Definitions (CRDs)**:
   ```yaml
   apiVersion: configuration.konghq.com/v1
   kind: KongPlugin
   metadata:
     name: enterprise-dynamic-router
     namespace: production
   plugin: custom-header-auth-router
   config:
     header_name: "X-Enterprise-Token"
     redis_host: "redis-cluster.cache.local"
     redis_port: 6379
     cache_ttl: 120
     dynamic_routing_header: "X-Target-Upstream"
   ```

***

**Back to Module:** [Overview](../README.md) | [Cheatsheet](../cheatsheet.md) | [Interview Questions](../interview.md) | [Scenarios & Troubleshooting](../scenarios.md)
