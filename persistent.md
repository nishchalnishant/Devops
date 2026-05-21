# Persistent Interview Prep — Kong Competency Role

Simple explanations with real-world analogies. Written to understand the concept first, then the technical detail.

---

## 1. API Gateway Internals & Kong Deep-Dive

---

### Kong plugin execution lifecycle (access, header_filter, body_filter, log phases)

**Simple version:** When a request comes into Kong, it passes through multiple checkpoints in a fixed order — like a package going through customs, security, packaging, and then a shipping receipt.

The phases in order:
1. `init_worker` — Kong worker starts up, loads things into memory (happens once, not per request)
2. `certificate` — TLS handshake: Kong picks the right SSL certificate for the domain
3. `rewrite` — Kong can change the URL before deciding where to send the request
4. `access` — **The main checkpoint.** This is where auth happens, rate limiting is checked, and request transformations are applied. Think of this as the security gate.
5. `header_filter` — After the upstream (your backend) responds, Kong can modify the response headers
6. `body_filter` — Kong can modify the actual response body (e.g., mask sensitive fields)
7. `log` — After the response is sent to the client, Kong logs the request details. This never delays the user.

If you have multiple plugins, the one with the **higher priority number runs first** within each phase.

---

### Rate limiting: local vs. Redis-backed, sliding vs. fixed windows

**Simple version:** Rate limiting is like a bouncer at a club — only letting X people in per hour.

- **Local counters:** Each Kong worker keeps its own count. If you have 4 workers and the limit is 100 req/min, each worker allows 100 — so actually 400 get through. Good for single-node setups only.
- **Redis-backed:** All workers share one counter in Redis. Accurate across the whole cluster. Adds a tiny bit of latency (~1ms) per request. Use this in production.

- **Fixed window:** Counter resets at the top of every minute. Problem: someone can send 100 requests at 11:59 PM and 100 more at 12:00 AM — 200 requests in 2 seconds.
- **Sliding window:** The window moves with every request. Smooths out that burst problem. More accurate but more complex.

---

### Kong DB-less mode vs. traditional (PostgreSQL) mode

**Simple version:** Think of it like two ways to configure a router — either by plugging in a USB config file (DB-less) or by having a central admin dashboard (traditional with DB).

| | DB-less | Traditional (PostgreSQL) |
|---|---|---|
| How config is loaded | From a YAML/JSON file | From a database |
| Can you make live changes via API? | No (read-only) | Yes |
| Good for | Kubernetes, GitOps, automated deployments | Legacy setups, Kong Manager UI |
| Consistency | Each node loads its own file | All nodes share the DB |

**DB-less is the modern, preferred approach for Kubernetes.** The Kong Ingress Controller (KIC) uses DB-less mode by default.

---

### Declarative config with `deck`

**Simple version:** `deck` is like Git for your Kong configuration. You describe what Kong should look like in a file, and `deck` makes it happen.

Key commands:
- `deck dump` — export current Kong config to a file (like `git pull`)
- `deck diff` — show what would change if you applied your file (like `git diff`)
- `deck sync` — apply the file, making Kong match it (like `git push`)
- `deck validate` — check your file for errors without touching Kong

**CI/CD pattern:**
- On a PR: run `deck diff` and post the output as a comment so reviewers can see exactly what will change in Kong
- On merge: run `deck sync` to apply it
- On a schedule: run `deck diff` daily — if there's a diff, someone manually changed Kong and you want to know about it

---

### mTLS between upstream services and Kong

**Simple version:** Normally Kong acts as a client when calling your backend (upstream). mTLS means both sides show their ID card — Kong shows a certificate to the backend, and the backend shows one back. This proves both parties are who they say they are.

- Kong presents a certificate to the upstream → configured via the `client_certificate` field on the Service object
- Kong validates the upstream's certificate → set `tls_verify: true` on the Service
- You define which CA certificates Kong trusts for this verification

---

### Custom plugin development in Lua or Go

**Simple version:** Kong lets you write your own plugins if the built-in ones don't do what you need. Like writing a custom browser extension.

Lua plugin structure (two files):
- `handler.lua` — the logic (what happens at each phase)
- `schema.lua` — defines what config options your plugin accepts

Key tools you get (PDK — Plugin Development Kit):
- `kong.request` — read the incoming request
- `kong.response` — modify the response
- `kong.service.request` — modify what gets sent to the upstream
- `kong.log` — write structured logs
- `kong.ctx.shared` — share data between plugins in the same request

Go plugins also work but run as a separate process — useful if your team doesn't know Lua, but slightly slower.

---

### Kong Mesh / Kuma integration for east-west traffic

**Simple version:**
- **Kong Gateway** = the front door. Handles traffic coming in from the internet (north-south).
- **Kong Mesh (built on Kuma)** = the internal hallways. Handles traffic between services inside your cluster (east-west).

They work together: Kong Gateway handles the external request and passes it into the mesh. Inside, the mesh secures and observes service-to-service calls automatically (mTLS, retries, traffic policies) without changing application code.

---

### JWT validation at gateway vs. OIDC plugin

**Simple version:** Two ways to check if a user's token is valid.

- **JWT plugin (basic):** Kong checks the token locally using a key it already has. Fast — no network call. Problem: if a token is stolen and you revoke it at the IdP, Kong doesn't know until the token expires naturally.
- **OpenID Connect plugin (Kong Enterprise):** Kong calls the identity provider (Okta, Azure AD, etc.) to verify the token in real time. Supports full login flows, token refresh, and revocation. Slower (one extra network call) but more secure.

**Rule of thumb:** Use OIDC for user-facing APIs where revocation matters. Use JWT for service-to-service calls with short-lived tokens (e.g., 15-minute expiry).

---

### API versioning strategies at the gateway layer

**Simple version:** When you update an API, old clients break if the API changes. Versioning lets old and new clients coexist.

Options:
1. **URL path** — `/v1/users` goes to the old service, `/v2/users` goes to the new one. Easiest to implement and understand.
2. **Header** — Client sends `Accept: application/vnd.api+json;version=2`. Kong routes based on the header. Cleaner URLs but less visible.
3. **Query param** — `/users?version=2`. Easy to test in a browser.
4. **Subdomain** — `v2.api.example.com`. Each version is a separate hostname.

**Deprecation:** Add a `Deprecation: true` header to old route responses so clients know it's going away. Log who's still using the old route before removing it.

---

### Kong Admin API security — RBAC, workspace isolation

**Simple version:** You don't want every team to be able to change every part of Kong. Workspaces and RBAC are how you fence teams off from each other.

- **Workspaces:** Like separate folders in Kong. Team A's routes and services live in their workspace; they can't see or touch Team B's.
- **RBAC:** Each admin gets a role that limits which Kong endpoints they can call and what they can do (read-only vs. full control).
- **Security rule:** Never expose the Kong Admin API to the internet. Keep it on a private network, behind a VPN, or protected with mTLS.

---

## 2. Service Mesh & Networking

---

### Service mesh vs. API gateway — and when to use both

**Simple version:**
- **API Gateway** = the security guard at the building entrance. Checks who's coming in, enforces access rules, and directs them to the right floor.
- **Service Mesh** = the internal security system between floors. Controls who inside the building can talk to whom, encrypts internal conversations, and monitors internal traffic.

You need both when:
- External clients need API management (auth, rate limiting, routing) → **Gateway**
- Internal services need secure, observable communication → **Mesh**

Avoid applying the same policy in both places (e.g., rate limiting at the gateway AND the mesh) — pick one owner per concern.

---

### Envoy proxy internals: xDS APIs (CDS, EDS, LDS, RDS)

**Simple version:** Envoy is the actual proxy inside each pod in a service mesh. It's like a smart post office inside your service. The control plane (Istio's brain) tells Envoy how to route traffic through a set of APIs collectively called xDS.

- **LDS** — "What ports should I listen on?" (Listener Discovery)
- **RDS** — "For requests on this port, where should I send them?" (Route Discovery)
- **CDS** — "What groups of backends exist?" (Cluster Discovery)
- **EDS** — "What are the actual IP addresses of those backends?" (Endpoint Discovery)

When you change a Kubernetes Service or an Istio VirtualService, the control plane pushes updated xDS config to all Envoy proxies instantly — no restarts needed.

---

### Traffic management: canary, circuit breaking, retries, timeouts

**Simple version:** These are safety mechanisms so one bad service doesn't take everything down.

- **Canary:** Send 10% of traffic to the new version, 90% to the old. If the new version looks good, gradually increase to 100%. Like a pilot episode — don't commit to the full season until you know it's good.
- **Circuit breaker:** If a backend starts returning errors, stop sending traffic to it temporarily. Like flipping a circuit breaker at home — better to cut power to one room than burn down the house.
- **Retries:** If a request fails, try again automatically. Only safe for operations that can be repeated without side effects (e.g., GET requests, not payments).
- **Timeouts:** Don't wait forever for a slow backend. Set a maximum wait time. If the timeout fires before a response arrives, fail fast and let the caller handle it.

**Key rule:** Gateway timeout should be slightly longer than the mesh timeout, so the mesh gets a chance to retry before the gateway gives up.

---

### mTLS across namespaces in Kubernetes

**Simple version:** With Istio installed, all pods automatically get an identity (like a corporate badge). mTLS means two services show each other their badge before talking. This works across namespaces automatically.

`AuthorizationPolicy` is how you say "only the `frontend` service in the `web` namespace is allowed to call the `checkout` service in the `payments` namespace." Without this, any service in the cluster could call any other.

---

### NetworkPolicy design — default-deny posture

**Simple version:** By default in Kubernetes, every pod can talk to every other pod — like an office with no locked doors. Default-deny is like locking every door and only giving specific people keys.

Step 1: Apply a policy that blocks all traffic to all pods in the namespace.
Step 2: Add specific allow rules only for traffic that should be allowed.

**Common mistake:** Forgetting to allow DNS traffic (port 53 to CoreDNS). If DNS is blocked, pods can't resolve hostnames — everything breaks even if the destination port is open.

---

### DNS resolution inside Kubernetes (CoreDNS, ndots, search domains)

**Simple version:** Inside a Kubernetes cluster, there's a built-in DNS server (CoreDNS). When a pod tries to reach `my-service`, CoreDNS resolves it to a ClusterIP.

Every pod gets automatic DNS config:
- It knows to ask CoreDNS for answers
- It automatically tries appending the namespace and cluster domain (so `my-service` becomes `my-service.my-namespace.svc.cluster.local`)

**The `ndots:5` gotcha:** If a name has fewer than 5 dots, the pod tries all the search domains first before treating it as an external address. So `google.com` (1 dot) triggers 4 failed lookups before resolving correctly. This adds latency. Fix: use `google.com.` (trailing dot) to tell DNS it's already a full name.

---

### Ingress vs. Gateway API (HTTPRoute, GRPCRoute)

**Simple version:** Ingress is the old way to expose services in Kubernetes. Gateway API is the newer, more powerful replacement.

**Ingress problems:**
- Only does HTTP/HTTPS
- No traffic splitting built-in
- Controller-specific annotations (nginx annotations don't work on Kong, etc.)

**Gateway API advantages:**
- Role separation: infra team manages the Gateway (the listener), app team manages the HTTPRoute (the routing rules)
- Native traffic splitting (no annotations needed)
- Works for HTTP, gRPC, TCP
- Portable across controllers

**Migration:** Most controllers support both at the same time. You can migrate namespace by namespace without a big-bang change.

---

## 3. Security & Zero Trust

---

### OAuth2 flows: Authorization Code + PKCE, Client Credentials, Token Exchange

**Simple version:** OAuth2 is the system for securely giving applications permission to access resources on behalf of users (or other systems). Different situations need different flows.

- **Authorization Code + PKCE** — For when a *user* logs in via a browser or mobile app. The app generates a secret, sends a hashed version to the login server, then proves it knows the original secret when exchanging the login code for a token. This prevents someone intercepting the code from using it.
- **Client Credentials** — For when one *service* needs to talk to another service with no user involved. Like a nightly batch job authenticating itself: it sends its ID and secret and gets a token.
- **Token Exchange (RFC 8693)** — Service A gets a request from User X and needs to call Service B on User X's behalf. It exchanges User X's token for a new token scoped to Service B. This preserves the user's identity through a chain of services.

---

### JWT structure, validation, and common vulnerabilities

**Simple version:** A JWT (JSON Web Token) is like a tamper-proof wristband at a concert. The wristband has your name, what you're allowed to do, and when it expires. The bouncer checks the wristband, not a central database.

Structure: three base64-encoded parts separated by dots: `header.payload.signature`
- Header: what algorithm was used to sign it
- Payload: the claims (who you are, expiry, audience)
- Signature: proves the header and payload weren't tampered with

**What to always verify:**
- Signature is valid
- Token hasn't expired (`exp`)
- Issuer is who you expect (`iss`)
- This token was meant for your service (`aud`)

**Common attacks:**
- **`alg: none`** — attacker sets the algorithm to "none" and removes the signature. Fix: never accept `none` as an algorithm.
- **Algorithm confusion** — server is tricked into using the public key as an HMAC secret. Fix: hardcode which algorithm you expect server-side.
- **Missing `aud` check** — a token for Service A is accepted by Service B. Always check the audience.

---

### API security: OWASP API Top 10 — BOLA, mass assignment, BFLA

**Simple version:** The most common API vulnerabilities — things attackers exploit most.

- **BOLA (Broken Object Level Authorization)** — API1: You call `GET /orders/123` and get back someone else's order because the server doesn't check if order 123 belongs to you. The most common API vulnerability. Fix: always verify ownership in business logic.
- **Mass Assignment** — API6: You send `{"balance": 1000000}` in a request and the server blindly saves all fields to the database. Fix: explicitly define which fields are allowed in each request — never auto-bind everything.
- **BFLA (Broken Function Level Authorization)** — API5: An admin-only delete endpoint isn't shown in the UI but exists and isn't protected. Any user who discovers the URL can call it. Fix: check permissions on every endpoint, don't rely on hiding things.

---

### mTLS certificate lifecycle management (cert-manager, Vault PKI)

**Simple version:** Certificates expire. cert-manager automates the "get a cert, renew it before it expires" process so you don't manually manage SSL certificates.

**cert-manager workflow:**
1. You define where to get certs from (Let's Encrypt, your own CA, Vault)
2. You create a `Certificate` resource saying "I need a cert for this domain"
3. cert-manager gets the cert and stores it in a Kubernetes Secret
4. cert-manager automatically renews it before expiry

**Vault PKI:** Instead of a public CA (Let's Encrypt), Vault acts as your own internal certificate authority. Advantage: you can issue very short-lived certs (e.g., 24 hours). A stolen cert is only valid for 24 hours, massively reducing blast radius.

---

### Secrets management: Vault Agent Injector vs. CSI driver vs. ESO

**Simple version:** Three ways to get secrets (passwords, API keys) into your pods without hardcoding them.

- **Vault Agent Injector:** A sidecar container runs next to your app, fetches secrets from Vault, and writes them as files. Also auto-renews dynamic secrets (e.g., a database password that changes every hour). Most powerful but adds a sidecar to every pod.
- **Vault CSI Driver:** Mounts secrets as a volume (files) into the pod. No sidecar — slightly lighter weight. Still requires Vault.
- **External Secrets Operator (ESO):** Watches your secret store (AWS Secrets Manager, Azure Key Vault, GCP Secret Manager, Vault, etc.) and creates standard Kubernetes Secrets from them. The simplest approach and works with any cloud provider — not just Vault.

**Which to use:** ESO for most teams. Vault Agent Injector if you need truly dynamic, frequently-rotating secrets.

---

### RBAC in Kubernetes — least-privilege, aggregated ClusterRoles

**Simple version:** RBAC is about who is allowed to do what. Least-privilege means giving only the minimum permissions needed — nothing extra.

- **Role:** permissions within one namespace (e.g., `get` and `list` pods in the `payments` namespace)
- **ClusterRole:** permissions across all namespaces (use sparingly)
- **RoleBinding:** attaches a Role to a user or service account
- **ServiceAccount:** the identity of a running pod (use these, not human user accounts, for apps)

**Aggregated ClusterRoles:** You can create ClusterRoles that automatically include permissions from other ClusterRoles by label. This lets teams add permissions to the standard `view`/`edit` roles without editing those roles directly.

**Quick audit:** `kubectl auth can-i --list --as system:serviceaccount:mynamespace:mysa` — shows all permissions a pod has.

---

### Pod Security Standards / OPA Gatekeeper / Kyverno

**Simple version:** Policies that prevent insecure pods from running in your cluster. Like building code inspectors who won't let you skip safety requirements.

**Pod Security Standards (PSS):** Three levels:
- `privileged`: no restrictions (only for system components)
- `baseline`: blocks the most common privilege escalation attacks (no host PID, no privileged containers)
- `restricted`: enforces best practices (must run as non-root, read-only filesystem, drop all Linux capabilities)

Apply by adding a label to the namespace: `pod-security.kubernetes.io/enforce: restricted`

**OPA Gatekeeper:** Write policies in Rego (a policy language). Very powerful and flexible, but Rego has a learning curve.
**Kyverno:** Write policies in YAML. Much easier to learn. Can validate, mutate (auto-fix), and generate resources. Better choice for most teams starting out.

---

### Supply chain security: Cosign, SBOM, SLSA

**Simple version:** How do you know the Docker image you're running is actually the one you built and not a tampered version?

- **Cosign:** Signs a container image with a cryptographic signature. Attackers who compromise your registry can't replace the image without invalidating the signature. You verify the signature before deploying.
- **SBOM (Software Bill of Materials):** A list of every package and dependency inside your container image. Like an ingredients list. You scan this list for known vulnerabilities.
- **SLSA levels:** A security maturity model for your build process.
  - Level 1: You document your build process
  - Level 2: Your build is automated and produces a signed provenance record
  - Level 3: Your build is hermetic (can't be influenced from outside), provenance is unforgeable

---

### Audit logging strategy across gateway, Kubernetes, and cloud

**Simple version:** Three layers of "who did what" logs that you want to collect and correlate.

- **Kong:** Log every request — who called what API, from which consumer, what the response was. Use the `file-log` or `http-log` plugin.
- **Kubernetes:** Log API server actions — who created/deleted/modified resources. Especially important for Secrets and RBAC changes.
- **Cloud provider:** Log IAM changes, resource creation/deletion, sensitive data access.

**The trick to correlation:** Inject a unique `X-Request-ID` header at the Kong gateway. Pass it through the mesh to every service. Include it in every application log line. Now you can trace one user request across all three layers in your log aggregation tool.

---

## 4. Kubernetes Advanced Operations

---

### Cluster upgrade strategy — node drain, PodDisruptionBudgets

**Simple version:** Upgrading a Kubernetes cluster is like renovating a building while people are still working in it. You do it one floor at a time.

Order:
1. Upgrade the control plane first (API server, scheduler, controller-manager). Managed Kubernetes (EKS, AKS, GKE) handles this for you.
2. For each node group: cordon the node (mark it unschedulable — no new pods land here), drain it (evict existing pods gracefully to other nodes), replace the node with a new version.

**PodDisruptionBudget (PDB):** Tells Kubernetes "never have fewer than N replicas running at once." During drain, if evicting a pod would violate the PDB, the drain command waits. Set `maxUnavailable: 1` so only one pod is down at a time.

**Don't forget:** Upgrade CoreDNS, kube-proxy, and your CNI plugin to compatible versions after each Kubernetes version bump.

---

### HPA vs. KEDA — event-driven autoscaling

**Simple version:** Both scale your pods up and down automatically. KEDA can do what HPA can't.

- **HPA (Horizontal Pod Autoscaler):** Built into Kubernetes. Scales based on CPU, memory, or custom metrics from the metrics API. Minimum 1 replica.
- **KEDA:** More powerful. Can scale based on queue depth (how many messages are waiting in SQS/Kafka/RabbitMQ), scheduled times, Prometheus query results, or any external metric. Can scale all the way down to **zero** pods when there's nothing to process (saves cost).

**KEDA actually manages HPA under the hood** — it just adds more trigger sources. Use KEDA when you have event-driven workloads or want scale-to-zero.

---

### VPA — risks, recommendations mode vs. auto mode

**Simple version:** VPA (Vertical Pod Autoscaler) adjusts how much CPU and memory your pods request. Think of it as someone watching your app's actual usage and saying "you asked for 4GB RAM but you only use 512MB — let me adjust that."

Modes:
- `Off` — just observes, does nothing
- `Initial` — sets resources when a pod is first created, never changes it after
- `Recommendation` — shows what it would set, but doesn't do it (safest — use this in production to review before acting)
- `Auto` — automatically evicts and recreates pods with new resource settings

**Risk of Auto mode:** VPA evicts pods to apply new settings. This causes disruption. Also, don't run VPA and HPA on the same metric at the same time — they'll fight each other.

---

### Resource requests/limits — OOMKill and CPU throttling

**Simple version:** You tell Kubernetes how much CPU and memory your container needs (requests) and the maximum it can use (limits).

- **OOMKill:** If your container uses more memory than its limit, Linux kills it immediately. You'll see `OOMKilled` in `kubectl describe pod`. Fix: increase the limit, or fix the memory leak.
- **CPU throttling:** Unlike memory, CPU isn't "kill and restart" — it's "slow down." If your app uses more CPU than its limit, the scheduler throttles it. The app stays running but gets slower. This shows up as latency spikes, not crashes. Check `container_cpu_throttled_seconds_total` in Prometheus.
- **Requests vs. limits:** Set requests to your typical steady-state usage (this determines which node you land on). Set limits to how much you'd allow in a burst.

---

### Persistent storage: CSI drivers, reclaim policies, ReadWriteMany

**Simple version:** Kubernetes pods are ephemeral — when a pod dies, its data is gone. Persistent Volumes (PVs) are how you keep data across pod restarts.

- **CSI drivers:** Plugins that connect Kubernetes to cloud storage (AWS EBS, Azure Disk, Google Filestore, etc.). Each cloud has its own CSI driver.
- **Reclaim policy:**
  - `Retain` — when you delete the PVC, the disk stays. You have to manually clean up. Good for important data.
  - `Delete` — when you delete the PVC, the disk is also deleted automatically. Good for temporary data.
- **Access modes:**
  - `ReadWriteOnce` — one node mounts the volume at a time (block storage like EBS)
  - `ReadWriteMany` — multiple nodes mount simultaneously (needs a network filesystem like NFS or EFS)

---

### Multi-tenancy patterns: namespaces, vCluster, separate clusters

**Simple version:** How to let multiple teams share infrastructure without stepping on each other.

- **Namespaces:** Cheapest option. Teams are separated by naming and permissions, but they share the same control plane and physical nodes. Like open-plan offices with name placards — partial separation.
- **Virtual clusters (vCluster):** Each team gets what looks like a full Kubernetes cluster but actually runs inside a namespace on the shared cluster. Stronger isolation, still cheaper than real separate clusters. Like private offices inside a shared building.
- **Separate clusters:** Total isolation. Each team has their own everything. Most expensive to operate but required for strict compliance or teams that need very different configurations.

---

### CRDs and operators — when to write one vs. using Helm

**Simple version:** Helm packages and deploys apps. Operators manage apps over their entire lifetime, like a human administrator would.

- **Helm:** Good for deploying a well-understood app (nginx, Prometheus). You define the chart, `helm install` and done. Upgrades and rollbacks are manual.
- **Operator:** Good for apps with complex lifecycle needs — databases that need failover logic, apps that need complex upgrade sequences, anything where "deploy and forget" isn't enough. The operator watches the cluster state and takes action to maintain desired state.

**Rule:** Use an existing operator from OperatorHub.io before writing your own. Only write a custom operator when existing ones don't cover your specific use case, as it's a significant investment.

---

### Kubernetes API Priority and Fairness (APF)

**Simple version:** The Kubernetes API server can get overwhelmed if many things (controllers, CI pipelines, humans) all send requests at once. APF is a traffic management system built into the API server that ensures critical requests (kubelet heartbeats, controller reconciliations) always get processed even when the API is busy.

It classifies requests into priority lanes. Think of it like airport security lanes — fast track for crew, normal lane for passengers. If a CI pipeline floods the API with `kubectl apply` calls, the kubelet lane is unaffected.

**Symptom:** If you see 429 errors or timeouts when running `kubectl` commands during high load, APF is throttling you. Fix: rate-limit the source of the flood.

---

### etcd backup and restore

**Simple version:** etcd is the database that stores all Kubernetes state. If etcd is lost or corrupted, your entire cluster state is gone. Back it up.

**Backup:**
```
etcdctl snapshot save /backup/etcd-snapshot.db
```
Run this as an automated cron job. Ship the snapshot to S3 or blob storage immediately.

**Restore:**
1. Stop the API server
2. Restore the snapshot to a new directory
3. Point etcd at the restored data directory
4. Restart etcd and the API server

**Important:** Practice your restore procedure. The worst time to discover it's broken is during an actual disaster.

---

### Node affinity, taints/tolerations, topology spread constraints

**Simple version:** Three tools for controlling which node your pods land on.

- **Node affinity:** "I want this pod to run on nodes with GPU hardware" or "I prefer nodes in zone us-east-1a." Like telling a taxi app "I prefer an SUV."
- **Taints and tolerations:** Taints mark nodes as "not for general use." Only pods that explicitly tolerate the taint can land there. Used to dedicate nodes for specific workloads (e.g., GPU nodes only run GPU jobs). Like a VIP lounge — only those with the right pass get in.
- **Topology spread constraints:** "Spread my pods evenly across availability zones, no more than 1 pod difference between zones." Prevents all your pods from landing in one zone and losing everything when that zone goes down.

---

## 5. CI/CD & GitOps

---

### GitOps: pull vs. push model, why pull wins

**Simple version:**
- **Push model:** Your CI pipeline reaches into the cluster and makes changes (`kubectl apply`). The cluster doesn't know about the change after it happens — it has no way to detect if someone manually changed something.
- **Pull model:** An agent (ArgoCD, Flux) *inside* the cluster constantly watches Git. It detects when the cluster drifts from what Git says it should be and auto-corrects. The cluster is always self-healing toward the Git state.

**Why pull wins:** Someone manually changes a deployment in prod. Push model: never detected. Pull model: ArgoCD detects the drift within minutes and reverts it (or alerts you). Git is the single source of truth.

---

### ArgoCD vs. Flux — multi-cluster fleet management

**Simple version:** Both are GitOps tools. Choose based on your team's preference.

- **ArgoCD:** Has a web UI. Stronger multi-tenancy with Projects. `ApplicationSet` lets you write one template and automatically create one Application per cluster or environment.
- **Flux:** No built-in UI (use Weave GitOps for one). More composable primitives, preferred by teams who want everything-as-code. Better for complex setups.

**Multi-cluster with ArgoCD:** One central ArgoCD instance manages N clusters. ApplicationSet generates one Application per cluster from a list.

**Multi-cluster with Flux:** A "hub" management cluster bootstraps Flux onto spoke clusters. Each spoke manages itself after bootstrapping.

---

### Deployment strategies: RollingUpdate, Blue/Green, Canary

**Simple version:** Three strategies for deploying a new version without downtime.

- **RollingUpdate:** Kubernetes default. Replaces old pods with new ones gradually (e.g., 1 at a time). Zero-downtime but during the rollout, both old and new versions serve traffic — they must be compatible.
- **Blue/Green:** Run two complete copies (blue = current, green = new). Test green fully, then flip a switch (update the Service selector) to send all traffic to green. Rollback = flip back. Needs double the resources during the switch.
- **Canary (via Argo Rollouts):** Send 10% of traffic to the new version. Automatically measure error rate. If it's good, increase to 25%, 50%, 100%. If error rate spikes, auto-rollback to the old version. Most sophisticated and safest for production.

---

### Secret handling in CI — OIDC keyless auth

**Simple version:** Old way: store AWS credentials as a GitHub Actions secret. Problem: long-lived credentials that can be leaked.

New way: OIDC. GitHub Actions gets a short-lived token that proves "I am this repo, this branch, this workflow." AWS/Azure/GCP trusts that token and issues a temporary cloud credential (valid for ~1 hour). No secrets stored anywhere — they're generated on demand and expire automatically.

Steps:
1. GitHub Actions fetches an OIDC token from GitHub
2. Sends it to AWS (or Azure/GCP)
3. AWS validates the token (is it really from this repo/branch?) and returns temporary credentials
4. Job uses those credentials, they expire when the job ends

---

### Pipeline observability — DORA metrics

**Simple version:** DORA metrics measure how good your engineering team is at delivering software. Four metrics:

1. **Deployment frequency:** How often do you deploy to production? (Daily is good, multiple times per day is elite)
2. **Lead time for changes:** From first commit to live in production, how long does it take? (Less than 1 hour is elite)
3. **Change failure rate:** What % of deployments cause a problem requiring rollback or hotfix? (< 5% is elite)
4. **MTTR (Mean Time to Restore):** When something breaks, how fast do you fix it? (< 1 hour is elite)

Collect these from your CI/CD pipeline events and display in a Grafana dashboard.

---

### Artifact provenance and promotion: image tags vs. digests

**Simple version:** A Docker image tag like `myapp:latest` is like a sticky note — someone can peel it off and stick it on a different image. A digest like `myapp@sha256:abc123` is like a fingerprint — it uniquely and permanently identifies exactly one image.

**Golden rule:** Never use mutable tags in production manifests. Always pin to a digest.

**Promotion pattern:**
1. Build the image in CI → push to dev registry with git SHA tag
2. Run all tests against this exact image
3. On success, copy (promote) the same image by digest to the prod registry — don't rebuild
4. Deploy using the digest

What was tested is exactly what runs in production.

---

### Renovate vs. Dependabot — dependency update automation

**Simple version:** Both automatically create PRs to update your dependencies (npm packages, Docker base images, Helm charts, Terraform modules).

- **Dependabot:** Built into GitHub. Easy to enable, limited configuration. Creates one PR per dependency update — can flood you with PRs.
- **Renovate:** More configurable. Can group all patch updates into a single PR (less noise), supports monorepos, updates Helm charts and Terraform modules (not just code dependencies). Requires more initial setup.

**Best practice for both:** Auto-merge patch version updates if tests pass. Require manual review for major version bumps. This keeps dependencies current without constant manual effort.

---

### Monorepo CI optimization

**Simple version:** In a monorepo with 50 services, you don't want to rebuild and test all 50 services every time one file changes.

- **Path filtering:** "Only run the payments service pipeline when files under `services/payments/` change." GitHub Actions supports this natively with `on.push.paths`.
- **Affected module detection:** Tools like `nx` or `Turborepo` understand the dependency graph. If `payments` depends on `common-auth` and you change `common-auth`, only `payments` (and other dependents) need to rebuild — not the other 48 services.
- **Caching:** Cache your build dependencies (node_modules, Maven cache, Docker layer cache) so subsequent builds reuse what hasn't changed. A cache hit on node_modules saves 2-5 minutes per pipeline.

---

### Rollback strategy — Helm, ArgoCD, database migrations

**Simple version:** Code rollback is easy. Database rollback is the hard part.

- **Helm rollback:** `helm rollback myapp 3` — restores Kubernetes resources to revision 3. One command.
- **ArgoCD rollback:** In the ArgoCD UI, sync to a previous Git commit. ArgoCD redeploys the previous state.
- **Database migrations:** This is where it gets hard. If your new code ran a migration that drops a column, rolling back the code doesn't bring the column back.

**Solutions:**
- Write **backward-compatible migrations** — additive only. Add new columns, never delete old ones (until all code that uses them is gone). Old code still works with the new schema.
- **Expand-contract pattern:** Add the new column, deploy new code that uses both old and new columns, then later remove the old column. Never break old code during the migration.
- The key insight: **plan for rollback before you deploy**, not after.

---

## 6. Observability & SRE

---

### Four Golden Signals vs. RED vs. USE

**Simple version:** Different lenses for looking at system health. Use the right one for the right layer.

- **Four Golden Signals** (Google SRE Book) — works for any service:
  - Latency: how long does it take?
  - Traffic: how much is happening?
  - Errors: how much is failing?
  - Saturation: how full is the system?

- **RED** — for microservices and APIs:
  - Rate: requests per second
  - Errors: error rate
  - Duration: response time

- **USE** — for infrastructure (nodes, disks, CPUs):
  - Utilization: how busy is the resource?
  - Saturation: is there a queue building up?
  - Errors: are there device-level errors?

**Simple rule:** Use RED for your services. Use USE for your servers.

---

### SLO/SLI/Error Budget — burn-rate alerts

**Simple version:**
- **SLI (Service Level Indicator):** The actual measurement. E.g., "95% of requests completed in under 200ms."
- **SLO (Service Level Objective):** The target. E.g., "99.9% of requests must complete in under 200ms over 30 days."
- **Error Budget:** The wiggle room. 99.9% SLO means 0.1% can fail — that's about 43 minutes of downtime per month.

**Burn-rate alert:** If you're burning through your error budget faster than normal, you'll run out before the month ends. Instead of alerting on "error rate is high right now," you alert on "we're consuming our monthly budget at 14x the normal rate."

Two alert types:
- **Fast burn** (14x rate over 1 hour): page someone now — budget exhausted in 2 hours
- **Slow burn** (3x rate over 6 hours): create a ticket — budget exhausted in 10 days

---

### Prometheus data model — cardinality explosion

**Simple version:** Prometheus stores a separate time series for each unique combination of label values. Labels are like tags on your metrics.

**The problem:** If you add a label with many possible values (like `user_id` or `request_id`), you create millions of time series. Prometheus keeps all active series in memory. Too many series = Prometheus runs out of memory and crashes.

**Rule:** Only use labels with a small, bounded set of values (e.g., `env=prod`, `method=GET`, `status=200`). Never use IDs, usernames, or request IDs as label values.

**How to check:** `prometheus_tsdb_head_series` — the count of active time series. If this is in the millions, investigate.

---

### PromQL: `rate` vs. `irate`, `histogram_quantile`

**Simple version:**

- **`rate(metric[5m])`** — average requests per second over the last 5 minutes. Smooth and stable. Use for dashboards and alerts.
- **`irate(metric[5m])`** — instantaneous rate, based only on the last 2 data points. Very spiky, very sensitive. Use only if you specifically need to detect instantaneous spikes.

**`histogram_quantile` pitfalls:**
- You use it to calculate percentile latencies (e.g., p99)
- If your actual latency exceeds your highest bucket, the result is `+Inf` (useless). Make sure your buckets cover your actual latency range.
- Always apply `rate()` to the `_bucket` metric first before calling `histogram_quantile`

---

### Distributed tracing: W3C TraceContext, sampling strategies

**Simple version:** A single user request might go through 10 different services. Distributed tracing connects all those individual logs and spans into one trace — a timeline of the full request journey.

**W3C TraceContext:** Standard HTTP headers (`traceparent`) that carry the trace ID and span ID. Every service reads these headers from incoming requests and adds them to outgoing requests. This chains all services together under one trace ID.

**Sampling:** You can't store traces for every single request at high volume.
- **Head-based:** Decide at the first service whether to trace this request. Simple but you might miss the one-in-a-million error that gets sampled out.
- **Tail-based:** Buffer all spans, wait until the trace is complete, then decide. Can preferentially keep error traces. More complex.
- **Probabilistic:** Keep X% of all requests randomly.

---

### OpenTelemetry: collector pipeline, auto-instrumentation

**Simple version:** OpenTelemetry is an open standard for collecting telemetry (metrics, logs, traces) from your applications without being locked into one vendor.

**Collector pipeline:** `Receivers → Processors → Exporters`
- Receivers: accept incoming telemetry (from your app, or scraped from Prometheus)
- Processors: filter, batch, sample, enrich the data
- Exporters: send to your backend (Datadog, Jaeger, Grafana Tempo, etc.)

**Auto-instrumentation:** Install a language agent (Java agent, Python middleware) and your app automatically emits traces for HTTP calls, database queries, and message queues — with zero code changes. In Kubernetes, the OpenTelemetry Operator injects this agent via a pod annotation.

---

### Log aggregation — structured logging and trace correlation

**Simple version:** Logs are most useful when they're in a consistent format that machines can query, and when you can link them to traces.

**Structured logging:** Emit JSON logs. Every log line has the same fields: timestamp, log level, service name, trace ID, message, and whatever context is relevant. Never use unformatted print statements in production code.

**The stack:** App writes JSON to stdout → Fluent Bit (DaemonSet on each node) collects stdout → ships to Loki or Elasticsearch → query in Grafana.

**Trace correlation:** Include the active trace ID in every log line. In Grafana, you can click a log line and jump directly to the distributed trace for that request. This is how you go from "I see an error in the logs" to "here's the full picture of what happened."

---

### Alertmanager: inhibition rules, routing trees, silences

**Simple version:** Alertmanager handles what happens when Prometheus fires an alert — who gets notified and how.

- **Routing tree:** Rules that match alerts and send them to the right receiver (PagerDuty, Slack, email). Group related alerts together so you get one notification, not 100.
- **Inhibition rules:** Suppress lower-priority alerts when a higher-priority alert is already firing. Example: if the entire cluster is down, suppress all the "service X is down" alerts — they're all caused by the cluster outage. Reduces noise so you can focus on the root cause.
- **Silences vs. fixes:** A silence mutes an alert temporarily (e.g., during planned maintenance). It doesn't fix anything. Never silence a real problem without creating a ticket to fix it.

---

### Grafana: data source federation, Loki LogQL, Tempo integration

**Simple version:** Grafana is your observability dashboard — it connects to multiple data sources (Prometheus, Loki, Tempo) and shows everything in one place.

**Data source federation:** One Grafana dashboard can pull from your Prometheus in AWS, your Prometheus in Azure, and your Loki cluster all at once. Use dashboard variables to switch between environments.

**Loki LogQL (log query language):**
- Select logs: `{app="kong", env="prod"}` — find all Kong prod logs
- Filter: `{app="kong"} |= "error"` — find logs containing "error"
- Metric: `rate({app="kong"} |= "error" [5m])` — turn log errors into a rate metric

**Tempo integration:** Configure Grafana to link from a log line (in Loki) to the full trace (in Tempo) using the trace ID field. One click goes from "I see an error" to "here's the full distributed trace."

---

### Chaos engineering: steady-state hypothesis, blast radius

**Simple version:** Deliberately break things in a controlled way to find weaknesses before they cause real outages.

**Steady-state hypothesis:** Before you inject any failure, define what "normal" looks like with specific numbers (e.g., error rate < 0.1%, p99 latency < 200ms). After the experiment, verify the system returned to normal.

**Process:**
1. Define steady-state
2. Inject failure (kill a pod, add 500ms latency, fill up a disk)
3. Watch — does the system self-heal? Do alerts fire correctly?
4. Stop the experiment
5. Fix any weaknesses found

**Blast radius containment:** Start in staging. In production, limit the scope (one service, one region). Always have a kill switch that automatically stops the experiment if metrics go past a threshold.

---

## 7. Multi-Cloud & Platform Engineering

---

### Identity federation: AWS IRSA, Azure Workload Identity, GCP WIF

**Simple version:** The old way to give a Kubernetes pod access to cloud resources was to put cloud credentials (access keys) in a Kubernetes Secret. This is risky — credentials can be stolen, they don't expire, and they're hard to rotate.

The new way: the pod gets a Kubernetes identity token, exchanges it with the cloud provider for a short-lived credential, and uses that. No long-lived secrets anywhere.

- **AWS IRSA:** Pod's service account token → exchanged at AWS STS → temporary AWS credentials. Configure an IAM role that trusts the EKS cluster's OIDC issuer.
- **Azure Workload Identity:** Pod token → exchanged at Azure AD → temporary Azure credentials. Configure a Federated Identity Credential on a Managed Identity.
- **GCP Workload Identity Federation:** Pod token → exchanged at GCP STS → temporary GCP credentials.

All three: credentials last ~1 hour, scoped to the specific workload, no secrets to store or rotate.

---

### Cross-cloud networking: VPC peering vs. Transit Gateway vs. Interconnect

**Simple version:** Different ways to privately connect networks.

- **VPC Peering:** Direct private connection between two VPCs. Like a direct road between two neighborhoods. Non-transitive — if A connects to B and B connects to C, A still can't reach C. Simple and cheap for a small number of VPCs.
- **Transit Gateway (AWS):** A central hub that all VPCs connect to. Like a highway interchange — everyone connects to the hub and can reach everyone else through it. Scales to thousands of VPCs.
- **Cloud Interconnect / ExpressRoute / Direct Connect:** A dedicated physical cable from your data center to the cloud. Used when you need guaranteed bandwidth and low latency for large data transfers, or when compliance requires a private (non-internet) connection.
- **Multi-cloud private networking:** No built-in solution between AWS and Azure. Use a third-party service (Megaport, Equinix) or site-to-site VPN.

---

### Cost governance: tagging, rightsizing, FinOps

**Simple version:** Cloud costs can spiral fast if nobody owns them. Cost governance is the process of tracking, attributing, and optimizing cloud spend.

- **Tagging:** Every resource must have tags (`team`, `environment`, `service`, `cost-center`). Without consistent tags, you can't tell which team is responsible for a $50,000 monthly bill. Enforce mandatory tags via policy (AWS SCPs, Azure Policy).
- **Rightsizing:** Most cloud resources are over-provisioned. Look at actual CPU/memory usage over 2 weeks. If you're at 10% utilization, downsize the instance. Cloud providers have tools for this (AWS Compute Optimizer, Azure Advisor).
- **Showback vs. chargeback:** Showback = "here's what your team spent" (raises awareness). Chargeback = "we're billing your team's budget" (drives behavior change).

---

### Landing zone design — account vending, guardrails

**Simple version:** A landing zone is a pre-configured, secure foundation that every new team or project starts from — so you don't start from a blank, insecure slate every time.

Think of it like a company office template: network cabling pre-installed, security cameras pre-configured, fire exits labeled, compliance posters on the wall. Teams move in and start working without setting up the basics.

**Account vending:** Automating the creation of new AWS accounts or Azure subscriptions with all the baseline config already applied (logging enabled, security tools enrolled, networking configured, mandatory tags enforced).

**Guardrails:**
- **AWS SCPs:** Applied to the entire Organization or an OU. Prevent specific actions regardless of what IAM allows. E.g., "nobody can disable CloudTrail" or "resources can only be created in approved regions."
- **Azure Policy:** Enforce and audit compliance at scale. E.g., "every VM must have a backup policy applied."

---

### Internal Developer Platform — Backstage, self-service, golden paths

**Simple version:** An IDP is a self-service portal that lets developers spin up infrastructure, create new services, and run deployments without needing to understand the underlying infrastructure complexity.

**Backstage (by Spotify):** Open-source IDP framework:
- **Software catalog:** A searchable directory of all your services, who owns them, their documentation, and their current health.
- **Scaffolder:** Fill out a form → a new service repository is created with CI/CD, monitoring, and a Kubernetes namespace already configured.
- **TechDocs:** Documentation lives in the same repo as the code, rendered in Backstage.

**Golden path:** The opinionated, pre-configured, supported way to build a service. Teams follow it by default and get security, compliance, and observability for free. They can deviate but they're on their own if they do.

---

### OpenShift specifics: SCC, Route vs. Ingress, OperatorHub

**Simple version:** OpenShift is Red Hat's Kubernetes distribution with extra enterprise features and stricter security defaults.

- **SCCs (Security Context Constraints):** OpenShift's version of Pod Security Standards. Stricter by default — pods run as a random non-root UID unless you grant them `anyuid`. If a third-party Helm chart fails on OpenShift, it's usually because it assumes root and needs an SCC adjustment.
- **Route vs. Ingress:** OpenShift has its own `Route` resource that predates Kubernetes Ingress. Both work on OpenShift. Use `Route` for OpenShift-specific features; use Ingress for portability.
- **OperatorHub:** OpenShift's built-in marketplace for operators. Operators are managed by OLM (Operator Lifecycle Manager), which handles installation and upgrades.

---

## 8. Infrastructure as Code

---

### Terraform state locking, remote backends, workspace vs. directory isolation

**Simple version:** Terraform tracks the current state of your infrastructure in a state file. If two people run `terraform apply` at the same time, they'll corrupt each other's state.

- **State locking:** Before making changes, Terraform acquires a lock (like a "do not disturb" sign). If the lock is taken, the second `terraform apply` waits or fails. On AWS, this uses a DynamoDB table.
- **Remote backends:** Store the state file in S3/GCS/Azure Blob — not on your laptop. This lets the whole team share state and enables locking. Never commit `.tfstate` to Git.

**Environment isolation:**
- **Workspaces:** One codebase, separate state files per workspace. Simple but risky — the same code applies to dev and prod, and a mistake in the code affects both.
- **Directory-based:** Separate folders for each environment (`environments/dev/`, `environments/prod/`), each with their own state file. More files to maintain but clearer separation and harder to accidentally blast prod when working on dev.

---

### Module versioning and the registry pattern

**Simple version:** Terraform modules are reusable infrastructure components. Like npm packages for infrastructure.

Pin your module versions: instead of `source = "git::github.com/my-org/modules//vpc"` (always latest), use `source = "git::github.com/my-org/modules//vpc?ref=v2.1.0"`. This means a module author can update the module without breaking your infrastructure.

**Good module design:**
- Does one thing well (a VPC module makes a VPC, not a VPC + 3 services + a database)
- Has sensible defaults so most callers don't need to pass many variables
- Outputs the things callers need (IDs, ARNs, endpoints)

---

### `terraform plan` in CI — PR comments, drift detection

**Simple version:** You want engineers to see what Terraform would change before it changes it — especially deletions.

**PR workflow:**
1. `terraform plan` runs on PR creation
2. The plan output is posted as a PR comment ("will create 2 resources, modify 1, **delete 1**")
3. Reviewer approves the plan
4. On merge, `terraform apply` applies that exact same plan

**Drift detection:** Run `terraform plan` on a schedule (e.g., nightly). If the output is non-empty, someone changed infrastructure manually outside of Terraform. Alert the team. This catches "quick fixes" that never got committed back to Git.

---

### Sentinel / OPA policies on Terraform plans

**Simple version:** A policy layer that sits between `terraform plan` and `terraform apply`. The policy reviews the plan and can block it if it violates rules.

Examples:
- "Block any apply that would delete a production database"
- "All resources must have required tags"
- "Only approved instance types are allowed"

- **Sentinel:** HashiCorp's built-in policy engine for Terraform Cloud/Enterprise. Policy as code but in a custom language.
- **OPA:** Run `terraform show -json plan.json` then evaluate it with a Rego policy. Works in any CI system, not just Terraform Cloud. More setup but more flexibility.

---

### Pulumi vs. Terraform — when imperative IaC makes sense

**Simple version:** Terraform uses a declarative language (HCL) — you describe what you want, Terraform figures out how to get there. Pulumi lets you use real programming languages (TypeScript, Python, Go) to define infrastructure.

**Use Pulumi when:**
- Your logic is complex enough that HCL becomes awkward (nested loops, API calls during plan)
- Your team knows Python/TypeScript well and doesn't want to learn HCL
- You want to unit test your infrastructure code

**Use Terraform when:**
- Your team already knows it
- The ecosystem and module library matters to you (Terraform has more community modules)

Most teams should start with Terraform and only switch to Pulumi when HCL's limitations genuinely hurt them.

---

### Ansible idempotency — `changed` vs. `ok`, handler deduplication

**Simple version:** Idempotency means running a playbook 10 times produces the same result as running it once. The first run might install a package; runs 2-10 see it's already installed and do nothing.

- **`ok`:** The system was already in the desired state. Nothing changed.
- **`changed`:** Something was modified. This is what triggers handlers.

**Handlers:** Tasks that run when notified by another task (e.g., restart nginx after a config file changes). **Key behavior:** if 5 tasks all notify the `restart nginx` handler, nginx only restarts once (at the end of the play), not 5 times. This prevents unnecessary restarts.

**`changed_when: false`:** For tasks that always report changed but are safe to run repeatedly (e.g., a script that queries status). Marking them as never-changed prevents unnecessary handler triggers.

---

### Configuration drift detection at scale

**Simple version:** Drift is when what's actually running in your environment no longer matches what your IaC says it should be. Someone logged into a server and made a change. Someone used the AWS console instead of Terraform. This is how "it works on my machine" becomes a production incident.

Detection options:
- **Terraform:** scheduled `plan` in CI — if plan is non-empty, you have drift
- **Ansible:** run in `--check` mode on a schedule — reports what would change
- **AWS Config / Azure Policy:** continuously checks resource compliance against rules

**Remediation:** Don't auto-apply blindly. Alert on drift, let a human review, then apply the fix. Exception: for critical security violations (e.g., public S3 bucket), auto-remediation is worth the risk.

---

## 9. Behavioral / System Design

---

### Design an API platform for 50 internal teams

**The question behind the question:** How do you give 50 teams self-service without losing control of security, consistency, and reliability?

**Answer framework:**

1. **Kong Gateway as the central entry point.** Use workspaces to isolate teams. Each team manages their own routes and services within their workspace.

2. **Self-service developer portal.** Teams register their APIs by submitting an OpenAPI spec to Git. The portal (Backstage or Kong Dev Portal) shows API docs automatically. Teams can create their own API keys/credentials.

3. **Governance pipeline.** Every OpenAPI spec change goes through CI: lint for naming conventions, check for breaking changes (adding required fields, removing endpoints), validate security requirements. Only then gets deployed to Kong via `deck sync`.

4. **Versioning discipline.** URL path versioning (`/v1/`, `/v2/`). New major version = new route. Old version gets a sunset header warning 6 months before removal.

5. **Deprecation process.** Query Kong access logs to find who still calls deprecated routes. Notify them 3 months before removal. Block new credentials from registering for deprecated routes.

6. **Observability per team.** Each team has a Grafana dashboard for their API routes. SLO targets are set per API. Teams can see their own consumers' usage.

---

### Gateway outage causing downstream failures at 3 AM

**The question behind the question:** Do you panic, or do you follow a structured process?

**Answer framework:**

1. **Confirm the blast radius first.** Is it all of Kong or one service? Check Kong's health endpoint, upstream connectivity, DNS.

2. **Check for recent changes.** Was there a deployment in the last hour? A config change via `deck sync`? 80% of incidents are caused by recent changes.

3. **Mitigation before root cause.** If a config change broke it, revert: `deck sync` the last good config from Git. If infrastructure, fail over to a standby instance or redirect to a maintenance page. Restore service first, understand why second.

4. **Communicate continuously.** Update the status page immediately. Set a cadence (every 15 minutes) to post updates in the incident channel even if there's no new information.

5. **After it's resolved:** Root cause analysis, add a test or alert that would have caught this earlier, update the runbook.

---

### Enforcing security policies without blocking developer velocity

**The question behind the question:** How do you not become the "department of no"?

**Answer framework:**

1. **Shift left.** Enforce in CI (on PR), not at deploy time. A failing deploy is a blocker; a failing PR check is feedback. Same fix, very different developer experience.

2. **Make the secure path the easy path.** Service templates that include mTLS, non-root containers, and RBAC by default. Developers don't have to know the security details to comply.

3. **Warn before block.** New policies start in audit mode. Teams see violations in a dashboard and have a grace period. Only switch to enforce after the fix rate is high. Surprise enforcement destroys trust.

4. **Fast exception process.** If a team has a legitimate reason to deviate, they can get an exception approved in 24 hours. Document it. Plan to remove it. Teams don't bypass controls when the alternative is fast and reasonable.

5. **Make security visible, not punitive.** Publish compliance rates by team. Teams don't like being last on a public list. Pair low-scoring teams with a security champion rather than threatening them.

---

### Multi-region active-active API deployment

**The question behind the question:** How do you handle global scale and regional failures gracefully?

**Answer framework:**

1. **Kong in each region.** DB-less mode, config deployed simultaneously to all regions via CI. Each region is independently functional — no cross-region dependency for serving traffic.

2. **Global load balancer.** AWS Global Accelerator, Azure Front Door, or Cloudflare routes users to the nearest healthy region based on latency + health checks. Health checks run every 30 seconds.

3. **Failover.** When a region fails, the health check fails, and the global LB routes all traffic to healthy regions automatically within ~30-60 seconds.

4. **Stateless services:** Easy — run in all regions, no coordination needed.

5. **Stateful services:** Hard. Use a globally distributed database (CockroachDB, DynamoDB Global Tables, Cosmos DB multi-region). The challenge is write conflicts when two regions write the same data simultaneously. Solve with:
   - Last-writer-wins (simple, can lose data)
   - CRDTs (complex, no data loss)
   - Regional write ownership (user X always writes to region A — no conflict)

---

### Secrets rotation without downtime

**The question behind the question:** Zero-downtime rotation is harder than it sounds. What's your strategy?

**Answer framework:**

1. **Support two valid secrets during rotation.** During the transition, both old and new secrets are accepted. New instances use the new secret; old instances still work with the old one. Once all instances have updated, invalidate the old secret.

2. **Dynamic secrets (Vault).** Vault issues short-lived database credentials (e.g., 1-hour TTL). The app renews automatically before expiry. Rotation is continuous and invisible — no rotation event, credentials just flow.

3. **Rolling restart.** Update the secret in your secrets manager. Trigger a rolling restart of pods (they pick up the new secret on startup). Zero downtime because the rolling restart keeps a minimum number of old pods running until new ones are ready and healthy.

4. **ESO with auto-restart.** External Secrets Operator detects when a secret version changes in AWS/Azure/GCP and updates the Kubernetes Secret. A `Reloader` sidecar or annotation watches the Secret and triggers a pod rolling restart.

---

### Incident response process

**The question behind the question:** Do you have a structured, repeatable process, or do you improvise every time?

**Answer framework:**

1. **Detection.** Alert fires (PagerDuty) or user reports. Verify it's real, not a flapping sensor.

2. **Triage.** Assign a severity (P1 = full outage, P2 = degraded). Assign an incident commander — one person drives, others investigate. Update the status page immediately (even "we're investigating").

3. **Investigation.** Check the four golden signals first (is it latency, errors, or traffic?). Check for recent deployments. Check dependencies. Post updates every 10-15 minutes in the incident channel.

4. **Mitigation.** Restore service first — rollback, scale up, disable a feature flag, enable a circuit breaker. Root cause is secondary to restoring the service.

5. **Resolution.** Verify metrics return to baseline. Declare the incident resolved. Update the status page.

6. **Postmortem.** Within 48 hours. Blameless — the goal is to fix the system, not find someone to blame. Timeline, root cause, contributing factors, action items with owners and due dates. Share broadly. Follow up on action items.

---

## 10. Quick Conceptual Checks

---

### Kubernetes service types: ClusterIP, NodePort, LoadBalancer, ExternalName

**Simple version:** Four ways to expose a service — each one builds on the last.

- **ClusterIP:** The service gets a virtual IP that only works inside the cluster. Other pods reach it by name (`my-service.my-namespace`). The default and most common type.
- **NodePort:** Opens a port (e.g., 31234) on every single node in the cluster. External traffic hits any node's IP on that port. Rough-and-ready, not production-grade on its own.
- **LoadBalancer:** Creates a cloud load balancer (like an AWS NLB) that distributes traffic across your nodes. This is how you actually expose services to the internet in production. Built on top of NodePort under the hood.
- **ExternalName:** Doesn't route traffic — it's just a DNS alias. `kubectl get service my-db` resolves to `prod.database.example.com`. Useful for abstracting external services behind a Kubernetes name.

---

### Why `kubectl exec` works but the app can't reach an external URL

**Simple version:** The exec shell and the app use different network paths. The exec command goes through the Kubernetes API, which is always allowed. The app's outbound traffic goes through the node's network, which might be blocked.

Most common causes:
1. **Egress NetworkPolicy:** A "block all outbound traffic" policy with no exception for the destination. Fix: add an egress rule allowing the specific destination port/CIDR.
2. **DNS is blocked:** The egress policy allows the destination port but not DNS (port 53). The hostname never resolves even if the destination would be reachable. Fix: add an egress rule allowing UDP/TCP port 53 to CoreDNS.
3. **No NAT gateway:** The node has no route to the internet. All pod traffic stays inside the VPC.

**Debug inside the pod:** `nslookup google.com` — if this fails, it's DNS. `curl -v http://google.com` — if DNS works but curl hangs, it's a connectivity/firewall issue.

---

### Pod eviction vs. pod deletion

**Simple version:**

- **Deletion** (`kubectl delete pod`): you explicitly asked for it. The pod gets a SIGTERM signal and 30 seconds (default) to shut down gracefully. Then SIGKILL. The Deployment immediately creates a replacement.
- **Eviction (node pressure):** The node is running out of memory or disk. kubelet starts evicting pods to free resources. Who gets evicted first? Pods with no resource requests (BestEffort) first, then pods exceeding their requests (Burstable), then pods whose requests equal their limits (Guaranteed) last.
- **Drain eviction** (`kubectl drain`): Uses the Eviction API which respects PodDisruptionBudgets. If evicting would leave fewer replicas than the PDB allows, the drain waits.

---

### `imagePullPolicy: Always` with digest-pinned images

**Simple version:** Tags are mutable (`:latest` changes). Digests are immutable (`@sha256:abc123` always means the same image).

With `imagePullPolicy: Always` + a tag: kubelet always asks the registry "what image is behind this tag?" and pulls the latest version of that tag. Risky.

With `imagePullPolicy: Always` + a digest: kubelet asks the registry to verify the manifest hash. If your local cache already has the exact same image, no data is downloaded (just a quick check). Safe — the digest guarantees you never run a different image.

**Best practice in production:** Use digest-pinned images + `IfNotPresent`. The digest already guarantees immutability; `Always` just adds a registry round-trip on every pod start without adding safety.

---

### Deployment rollout pause vs. HPA scale-down cooldown

**Simple version:** They sound similar but are completely different.

- **Rollout pause** (`kubectl rollout pause deployment/x`): Freezes a rolling update mid-flight. New pods stop being created from the new template. Existing pods (both old and new) keep running. Use this when you want to manually validate a partial canary before continuing the rollout. Resume with `kubectl rollout resume`.

- **HPA scale-down cooldown** (default 5 minutes): After traffic drops, HPA waits 5 minutes before actually reducing replica count. This prevents the HPA from scaling down during a brief traffic dip and then immediately scaling back up when traffic returns. The pods keep running for 5 minutes after the metric says they're not needed.

One is about deployment progression. The other is about autoscaling stability.

---

### How Kong handles plugin ordering with multiple plugins on one route

**Simple version:** Each Kong plugin has a priority number. Within each phase (like `access`), plugins with higher priority numbers run first.

Example priorities: `bot-detection` (2500), `jwt` (1005), `rate-limiting` (910), `request-transformer` (801).

So if a route has all four of these plugins, in the `access` phase they run in this order:
1. bot-detection (2500)
2. jwt auth (1005)
3. rate-limiting (910)
4. request-transformer (801)

This makes sense: check if it's a bot first, then authenticate, then rate-limit authenticated users, then transform the request.

If you write a custom plugin and want it to run before rate-limiting, set its priority to anything above 910.

---

### `deck diff` vs. `deck sync` — when to use each in a pipeline

**Simple version:**

- `deck diff` — shows what *would* change. Makes no changes. Like `terraform plan`. Exits with code 2 if there are differences (useful for failing a CI check if there's unexpected drift).
- `deck sync` — applies the changes. Actually modifies Kong. Like `terraform apply`.

**Rule:** Always run `deck diff` first in CI so reviewers can see exactly what Kong changes are coming. Only run `deck sync` after the change is approved and merged.

**Important:** `deck sync` will **delete** Kong objects that are in Kong but not in your config file. This is intentional (it maintains exact config match) but dangerous if you manage a shared Kong instance. Use `--select-tag` to scope operations to only the objects your team owns — so your sync doesn't delete another team's routes.
