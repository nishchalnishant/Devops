# Kong Gateway — API Gateway & Service Control

```
Kong Gateway
├── Core Architecture
│   ├── Reverse Proxy: built on NGINX + OpenResty (Lua)
│   ├── Service: points to backend (URL, protocol, port)
│   ├── Route: matching rule (path, host, method, headers) → maps to Service
│   ├── Consumer: user or application making requests
│   └── Upstream: load-balanced pool of backend targets
├── Deployment & Modes
│   ├── DB Mode (Postgres): immediate config distribution via Admin API
│   ├── DB-less Mode: declarative YAML configuration (`kong.yml`)
│   └── Hybrid Mode: Control Plane (Admin API) + Data Plane (Proxying) split
└── Kubernetes Ingress
    ├── Kong Ingress Controller (KIC): watches K8s API; updates Data Planes
    └── CRDs: KongPlugin, KongConsumer, KongIngress, KongClusterPlugin
```

## First Principles

* **Decoupled Concerns**: Centralize all cross-cutting infrastructure concerns (authentication, rate limiting, logging, header transformations) at the gateway layer. Services focus entirely on business logic rather than security boilerplate.
* **Lua-Powered Extensibility**: OpenResty/Lua integration allows Kong to run code directly inside the NGINX event loop. This enables sub-millisecond proxy latencies even with dozens of plugins enabled.
* **Separation of Planes (Hybrid Mode)**: The Control Plane (managing configuration and APIs) and the Data Plane (forwarding traffic) operate independently. If the Control Plane goes down, the Data Plane continues serving traffic uninterrupted.
* **GitOps Configuration**: Treat gateway configuration like code. Using `decK`, declarative state files (`kong.yml`) are version-controlled, verified with `deck diff`, and applied in CI/CD pipelines.

---

## The Core Mental Model

```
       [ Client Request ]
               │
               ▼
   ┌───────────────────────┐
   │     Kong Gateway      │
   │  (Plugins: Auth, RL)  │
   └───────────┬───────────┘
               │ (Match Route)
               ▼
   ┌───────────────────────┐
   │     Kong Service      │
   └───────────┬───────────┘
               │ (Load Balance)
               ▼
   ┌───────────────────────┐
   │     Kong Upstream     │
   │  ┌───────┬───────┐    │
   │  │ Pod 1 │ Pod 2 │    │
   └──┴───────┴───────┴────┘
```

1. **Route** defines *where* requests come from (e.g., path `/v1/payments`, host `api.domain.com`).
2. **Service** defines *where* the request goes (e.g., `http://payments-service.internal:8080`).
3. **Plugins** execute at various proxy phases (e.g., validating JWT in the `access` phase, stripping headers in the `header_filter` phase).
4. **Upstream** balances traffic between multiple backend instances (targets) with active/passive health checks.

---

## Overview

Kong Gateway is a lightweight, fast, and highly extensible API gateway built on NGINX and OpenResty. It acts as a single point of entry for all incoming client requests, executing security, rate-limiting, and routing rules before proxying traffic to your backend microservices.

### DB Mode vs. DB-less Mode
* **DB Mode**: Config is stored in a PostgreSQL database. Config updates are pushed immediately via the Kong Admin API on port `8001`. Multiple gateway instances read from the same database.
* **DB-less Mode**: Config is loaded from a single declarative YAML file (`kong.yml`). There is no database. Any change requires reloading the configuration (`kong reload` or decK sync). This is standard practice in Kubernetes.

---

## API Gateway Comparison Matrix

| Feature | Kong Gateway | Apigee | KrakenD | Envoy Proxy |
|:---|:---|:---|:---|:---|
| **Core Architecture** | NGINX + OpenResty (Lua) | Java-based (Enterprise) | Go (Stateless Engine) | C++ (Service Mesh Focus) |
| **Performance** | Extremely High (~1-2ms overhead) | Moderate (Higher Latency) | High | Extremely High |
| **Configuration** | REST API, decK, K8s CRDs | Web UI, XML, API | Declarative JSON/YAML | gRPC xDS APIs, YAML |
| **Extensibility** | Lua Plugins, Go/JS Coprocessors | Java Callouts, JS policy | Go plugins, C++ custom | WASM Filters, Lua |
| **Best Used For** | Cloud-native microservices, K8s | Enterprise API management | Stateless gateway aggregation | Service Mesh ingress, sidecar |

---

## What is in This Module

| File | Purpose |
|:---|:---|
| `notes/kong-architecture-and-plugins.md` | Hybrid mode architecture, NGINX phases, custom Lua plugins |
| `cheatsheet.md` | Kong Admin API commands, decK operations, and plugin configs |
| `interview.md` | Consolidated Interview Questions: Easy, Medium, and Hard levels |
| `scenarios.md` | Real-world troubleshooting: latency isolation, hybrid mode sync |

***

**Next:** [Detailed Notes](notes/kong-architecture-and-plugins.md) | [Cheatsheet](cheatsheet.md) | [Interview Questions](interview.md) | [Scenarios & Troubleshooting](scenarios.md)
