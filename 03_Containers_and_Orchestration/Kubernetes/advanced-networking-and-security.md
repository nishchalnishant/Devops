# Advanced Networking & Security (7 YOE)

Mid-level engineers configure Ingress resources to expose web apps. Senior engineers replace the entire internal networking stack of Kubernetes to enforce zero-trust, kernel-level fast paths, and global policy controls.

---

## 1. The eBPF Networking Revolution (Cilium)

By default, Kubernetes uses `kube-proxy` combined with Linux `iptables` to route traffic to Services. 
- **The Problem:** `iptables` was designed in the 1990s as a firewall, not a dynamic load balancer. When a cluster has 10,000 services, `kube-proxy` must evaluate massive sequential rule lists for every packet, causing massive CPU overhead and tail latency spikes.

### The Cilium Solution
Cilium is the modern CNI (Container Network Interface) standard replacing `kube-proxy` entirely. It is built on **eBPF (Extended Berkeley Packet Filter)**.
- eBPF allows safe programs to run inside the Linux kernel on network events. 
- Instead of using slow `iptables` routing, Cilium injects a hash-map lookup directly into the kernel's network socket layer. 
- A packet leaving Pod A destined for Pod B does not traverse the host's standard TCP/IP stack; eBPF routes it optimally and instantaneously.

**Security Benefit:** Standard NetworkPolicies only filter at Layer 3/4 (IP/Port). Cilium Network Policies understand Layer 7 (HTTP/gRPC/Kafka). You can create a policy: *“Pod A can only make HTTP GET requests to Pod B on path `/api/data`, and all POST requests are dropped.”*

---

## 2. Ingress vs. Gateway API

The `Ingress` object is dying. It was primarily designed for simple HTTP/HTTPS host path routing and forced vendors to use confusing, non-standard annotations (e.g., `nginx.ingress.kubernetes.io/rewrite-target`) for advanced routing.

### The Kubernetes Gateway API
The Gateway API is the successor to Ingress. It is expressive, extensible, and—most importantly—**Role-Oriented**.

It divorces the management of the infrastructure from the developer routes:
1. **Infrastructure Provider:** Deploys underlying Load Balancers in the Cloud.
2. **Cluster Operator:** Creates the `GatewayClass` (selecting the implementation like Istio/Nginx) and `Gateway` (binding the IP/port).
3. **Application Developer:** Creates an `HTTPRoute` detailing the path matching, traffic splitting (canary weights), and header manipulations. They attach these routes to the central `Gateway`.

---

## 3. The Evolution of the Service Mesh

A Service Mesh provides mutual TLS (mTLS), circuit breaking, and telemetry across all microservices without changing application code. 

### Generation 1: The Sidecar Proxy (Istio / Linkerd)
- The mesh injects a reverse proxy (Envoy) into every single Pod forming the cluster data plane.
- **Problem:** If you have 5,000 pods, you now have 5,000 Envoy proxies continually scraping CPU and RAM. It creates massive operational overhead and drastically impacts cluster startup times.

### Generation 2: Ambient Mesh / Sidecarless (Istio Ambient / Cilium)
Modern multi-tenant architectures are shifting to **Sidecarless** Service Meshes.
- It uses a per-node proxy (a DaemonSet running Envoy) rather than a per-pod sidecar. 
- Traffic leaving a pod is intercepted at the kernel level (via eBPF/ztunnel) and redirected securely to the node-level proxy for L7 telemetry and L4 mTLS encryption.
- **Benefit:** Reduces resource consumption by 70+%. You do not have to restart application pods to inject/upgrade sidecars.

---

## 4. Policy as Code: Admission Controllers

RBAC restricts *who* can create objects in Kubernetes, but **Admission Controllers** restrict *what* can be inside those objects. 

### OPA Gatekeeper vs. Kyverno
Before a resource (like a Pod) is saved to `etcd`, the API Server sends a request to a Mutating/Validating Webhook to ask if the resource complies with company policy.

- **OPA Gatekeeper:** Uses Rego, a declarative query language. Extremely powerful but notoriously complex to write and maintain. 
- **Kyverno:** Kubernetes-native policy management. Policies are written in standard YAML. 

**Senior Engineer Use Cases for Kyverno:**
1. **Validation:** Reject any Pod that runs as `root`.
2. **Mutation:** Automatically inject a sidecar container or specific tolerations into a pod manifest based on its namespace.
3. **Generation:** Whenever a new developer namespace is created, automatically generate standard `NetworkPolicies`, `RoleBindings`, and `ResourceQuotas` explicitly for that namespace.
