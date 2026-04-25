---
description: Kubernetes networking internals — CNI, Services, Ingress, NetworkPolicy, and eBPF-based networking for senior engineers.
---

# Kubernetes — Networking Deep Dive

## The Kubernetes Networking Model

K8s enforces three fundamental rules:
1. **Every pod gets its own IP** (no port sharing between pods on same node)
2. **All pods can communicate with all other pods without NAT**
3. **Agents on a node can communicate with all pods on that node**

This is implemented by the **CNI (Container Network Interface)** plugin.

***

## CNI Plugin Internals

```
Pod Created by kubelet
        │
        │ kubelet calls CNI binary
        ▼
    CNI Plugin (Calico / Cilium / Flannel)
        │
        ├── Creates virtual ethernet pair (veth)
        │   ├── One end in the pod namespace (eth0)
        │   └── One end in the host namespace (cali.xxxxx)
        │
        ├── Assigns IP from the node's pod CIDR
        │
        └── Programs routing rules (iptables or eBPF)
                Pod A (10.244.1.5) → Pod B (10.244.2.7)
                  └── Node A routes to Node B via overlay or direct routing
```

### CNI Comparison

| CNI | Routing | Data Plane | Key Feature |
|:---|:---|:---|:---|
| **Flannel** | VXLAN overlay | iptables | Simplest, no network policy |
| **Calico** | BGP (direct) or VXLAN | iptables / eBPF | Full NetworkPolicy, high performance |
| **Cilium** | eBPF | eBPF only | L7 network policy, Hubble observability, Envoy integration |
| **Weave** | VXLAN | iptables | Simple, auto-discovery |

***

## Services — The Stable Network Identity

Pods are ephemeral (IPs change on restart). Services provide a stable virtual IP (ClusterIP) that load-balances to healthy pod endpoints.

```
Client Pod
    │
    │  Sends to Service IP: 10.96.45.12:80
    ▼
kube-proxy (or Cilium) intercepts the packet
    │  DNAT: 10.96.45.12:80 → Pod IP: 10.244.2.7:8080
    ▼
Target Pod
```

### Service Types

```yaml
# ClusterIP (default) — internal only
apiVersion: v1
kind: Service
metadata:
  name: my-api
spec:
  selector:
    app: my-api
  ports:
    - port: 80
      targetPort: 8080
  type: ClusterIP

# NodePort — exposes on every node's IP at a static port
  type: NodePort
  # ports.nodePort: 30080  (30000-32767)

# LoadBalancer — provisions a cloud LB (ELB/ALB)
  type: LoadBalancer
  # annotations for AWS, GCP, Azure specific behavior

# ExternalName — DNS alias (no proxying)
  type: ExternalName
  externalName: my-database.us-east-1.rds.amazonaws.com
```

***

## Ingress — L7 HTTP Routing

```
External Traffic
    │
    ▼
LoadBalancer Service (one cloud LB for all services!)
    │
    ▼
Ingress Controller (nginx / traefik / AWS ALB)
    │
    ├── Host: api.company.com → Service: api-service:80
    ├── Host: app.company.com → Service: frontend-service:80
    └── Path: /admin          → Service: admin-service:8080
```

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - api.company.com
      secretName: api-tls-cert
  rules:
    - host: api.company.com
      http:
        paths:
          - path: /v1
            pathType: Prefix
            backend:
              service:
                name: api-v1-service
                port:
                  number: 80
```

***

## NetworkPolicy — Kubernetes Firewall

**By default, all pods can communicate with all other pods.** NetworkPolicy changes this to a whitelist model. **Requires a CNI that supports it (Calico, Cilium, Weave).**

```yaml
# Allow: only pods with label app=frontend can call app=backend on port 8080
# Deny: everything else to app=backend
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-backend
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: frontend
        - namespaceSelector:
            matchLabels:
              env: production
      ports:
        - protocol: TCP
          port: 8080
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: postgres
      ports:
        - protocol: TCP
          port: 5432
    - to:          # Allow DNS
        - namespaceSelector: {}
      ports:
        - protocol: UDP
          port: 53
```

***

## DNS in Kubernetes — CoreDNS

```
Pod does: curl http://my-api
              │
              │ Pod resolves: my-api.production.svc.cluster.local
              ▼
        CoreDNS (kube-dns service: 10.96.0.10)
              │
              │ Returns ClusterIP for my-api Service
              ▼
        kube-proxy translates ClusterIP → Pod IP
```

**FQDN Format:** `<service>.<namespace>.svc.<cluster-domain>`

***

## Logic & Trickiness Table

| Concept | Common Mistake | Senior Understanding |
|:---|:---|:---|
| **kube-proxy modes** | Assume iptables always | `ipvs` mode scales better; Cilium replaces kube-proxy entirely with eBPF |
| **NetworkPolicy** | Think it's enforced by default | Requires a NetworkPolicy-capable CNI; CNIs like Flannel ignore policies |
| **Service DNS** | Use IP addresses | Always use DNS names; IPs change after svc delete/recreate |
| **Ingress vs Gateway API** | Use only Ingress | Gateway API is the future — supports L4+L7, multi-team tenancy |
| **LoadBalancer cost** | One LB per service | Use a single Ingress controller with one LB for all HTTP services |
| **MTU** | Ignore it | VXLAN adds 50 bytes overhead; set CNI MTU to 1450 on 1500 networks |
