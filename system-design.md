# System Design for DevOps & SRE Interviews

Senior DevOps/SRE interviews include open-ended system design problems. Each problem below
follows the same structure: **Clarify → Estimate → Design → Deep Dive → Trade-offs**.

***

## Problem 1: Design a Global CI/CD System

**Prompt:** "Design a CI/CD system that serves 500 engineering teams across 3 geographic
regions, with 99.9% uptime and sub-10-minute build times."

### Clarify
- Scale: 500 teams, ~10k developers, ~5k pipeline runs/day
- Workloads: polyglot (Go, Python, Node, Java), Docker, Kubernetes
- Regions: US-East, EU-West, AP-South
- Compliance: SOC2, GDPR data residency

### Core Components

```
Developer Push
    │
    ▼
SCM (GitHub Enterprise) — webhook
    │
    ▼
CI Orchestrator (GitLab CI / GitHub Actions / Tekton)
    │
    ├── Build Workers (Ephemeral, per-region)
    │       └── Kaniko / BuildKit (rootless image builds)
    │
    ├── Artifact Registry (per-region, mirrored)
    │       └── Harbor / ECR / Artifact Registry
    │
    ├── Security Scanning (in-pipeline)
    │       └── Trivy, Semgrep, Gitleaks, Cosign sign
    │
    └── CD (ArgoCD, per-cluster)
            └── Pull model — no credentials leave the cluster
```

### Regional Design
- **Active-Active CI workers** per region — builds run in the closest region to the dev team
- **Artifact replication**: after build, push to primary registry → async replicate to other regions (< 2 min lag)
- **Control plane in one primary region** (active) with read replicas in others — fails over automatically
- **Cache sharing**: distributed cache (S3 + CloudFront or GCS + CDN) so a `node_modules` cache built in US is reused by EU builds

### Critical Trade-offs

| Decision | Option A | Option B | Choice |
|:---|:---|:---|:---|
| CI engine | Jenkins (self-managed) | GitHub Actions / GitLab CI (SaaS/self-hosted) | GitLab CI self-hosted (control + ecosystem) |
| Build isolation | Shared runners | Ephemeral runners (1 job → 1 pod → destroy) | Ephemeral (security + reproducibility) |
| Artifact storage | Per-team registries | Central registry with namespacing | Central + team namespaces (simpler management) |
| Secret distribution | Static credentials | OIDC (keyless) | OIDC — no stored secrets |

### Reliability
- **Build worker autoscaling**: Karpenter on EKS scales worker nodes in <90 seconds on burst
- **Queue depth alert**: if queue > 200 jobs for > 5 minutes → PagerDuty (CI throughput SLO)
- **Circuit breaker**: if artifact registry is unreachable, pipeline fails fast (no silent failures)
- **Disaster recovery**: if US-East is down, EU-West can serve US teams at degraded performance; RTO < 15 min

***

## Problem 2: Design a Multi-Tenant Kubernetes Platform for 200 Teams

**Prompt:** "Your company is migrating to Kubernetes. Design a platform that lets 200
product teams deploy independently with full isolation, self-service, and a $0 operations
model from the platform team for common use cases."

### Clarify
- Teams: 200, ranging from 2 to 50 engineers
- Workloads: microservices, ML training, batch jobs, stateful databases
- Compliance: PCI for 10 teams, GDPR for all
- Self-service SLA: provision a new service in < 30 minutes without a ticket

### Architecture

```
Developer → Backstage Portal (IDP) → Terraform / Crossplane → K8s Cluster(s)
                │                         │
                ▼                         ▼
        Scaffolding Template          Namespace + RBAC + NetworkPolicy
        (service, CI/CD, registry)    + ResourceQuota + LimitRange
```

### Namespace Isolation Model
```yaml
# Per-team namespace with hard limits
apiVersion: v1
kind: ResourceQuota
metadata:
  name: team-payments-quota
  namespace: team-payments
spec:
  hard:
    requests.cpu: "20"
    requests.memory: "40Gi"
    limits.cpu: "40"
    limits.memory: "80Gi"
    persistentvolumeclaims: "10"
    services.loadbalancers: "2"
```

- **RBAC**: teams are `admin` in their namespace, `view` in others they've declared dependencies on
- **NetworkPolicy**: default-deny-all per namespace; explicit allow for known dependencies (service mesh optional)
- **OPA Gatekeeper**: cluster-wide policies teams cannot override (require non-root, image allowlist, resource limits mandatory)

### Cluster Topology
- **Shared clusters** for dev/staging (cost efficiency, weaker isolation)
- **Dedicated clusters** for PCI-scoped teams (hard compliance isolation)
- **Cluster API / EKS Managed Node Groups**: new cluster in < 15 minutes for PCI onboarding

### Self-Service Flow (Backstage → Production in 25 minutes)
1. Developer opens Backstage → "New Service" template
2. Template creates: GitHub repo + CI pipeline + ECR namespace + K8s namespace + ArgoCD Application + PagerDuty service
3. Developer pushes code → auto-builds → deploys to dev namespace
4. Developer promotes to staging via PR → ArgoCD syncs
5. Production gate: Platform-enforced security scan must pass; no manual approval for non-PCI

### Reliability & Cost
- **VPA** in recommendation mode: right-size resource requests every sprint cycle
- **Karpenter** with spot pools for dev/staging (70% cost reduction)
- **Kubecost** show-back: teams see their weekly spend on Backstage homepage
- **PDB** enforced by policy: all Deployments with replicas > 1 must have a PodDisruptionBudget

***

## Problem 3: Design an Observability Stack for 500 Microservices

**Prompt:** "Design an observability platform for a 500-service microservices architecture
that handles 100k requests/second with a < 5-minute MTTD (mean time to detect) SLO."

### Clarify
- 500 services, 2000 pods, 10 teams
- 100k RPS peak, 10M time series (estimate)
- Budget: minimize storage cost (logs are expensive)
- Existing: CloudWatch + some Datadog — want open-source or cost-predictable

### Architecture

```
Services
  │
  ├── Metrics ──────► Prometheus (per-cluster) ──► Thanos (global query + long-term storage)
  │                                                       └── S3/GCS (cheap long-term)
  │
  ├── Logs ──────────► Promtail / Fluent Bit ──► Loki (index-free, label-based)
  │                                                       └── S3 (object storage)
  │
  └── Traces ─────────► OpenTelemetry Collector ──► Tempo (trace store)
                                                           └── S3
                                          │
                                          ▼
                                  Grafana (unified UI)
```

### Scale Design

**Prometheus → Thanos (for 10M series):**
- Each cluster runs a Prometheus with 2M series max (horizontal sharding via `prometheus-operator`)
- Thanos Sidecar uploads TSDB blocks to S3 every 2 hours
- Thanos Querier federates queries across all Prometheus instances globally
- Thanos Compactor handles downsampling (5m resolution after 30d, 1h after 1 year)
- Result: 2-year retention at ~$500/month (vs $15k/month for Datadog at this scale)

**Loki (for structured logs):**
- Logs are expensive at scale — aggressive filtering: only retain logs at WARNING+ for 30 days; ERROR+ for 90 days; all logs for 24h
- Structured JSON logging enforced by policy — enables LogQL filtering without regex on unstructured text
- Loki's label schema: `{namespace, pod, service, env}` — minimal cardinality to avoid Loki OOM

**Tail Sampling for Traces:**
- Only trace 100% of errors; sample 0.1% of successful requests (cost control)
- OpenTelemetry Collector runs tail sampling processor — waits 10 seconds, evaluates full trace, decides to keep or drop

### Alert Design (< 5-minute MTTD)
- Prometheus scrape interval: 15s
- Alert evaluation: every 30s
- Alertmanager routes critical alerts in < 30s to PagerDuty
- Multi-window/multi-burn-rate SLO alerts:
  - 5m window, 14.4x burn rate → page immediately (budget exhausted in 1h)
  - 1h window, 6x burn rate → urgent ticket (budget exhausted in 5 days)

### Cost Breakdown (estimated for 500 services)
| Component | Storage/Compute | Monthly Cost |
|:---|:---|:---|
| Thanos + S3 (metrics) | 5TB | ~$115 |
| Loki + S3 (logs) | 10TB | ~$230 |
| Tempo + S3 (traces, sampled) | 2TB | ~$46 |
| Compute (Querier, Compactor) | 8 vCPU / 32GB | ~$200 |
| **Total** | | **~$591/month** |

***

## Problem 4: Design a Zero-Downtime Blue/Green Deployment for a Stateful Application

**Prompt:** "Design a deployment strategy for a payments API backed by PostgreSQL that
requires < 10ms P99 latency, zero dropped requests during deployments, and instant rollback."

### Clarify
- Traffic: 5k RPS, P99 < 10ms
- Database: PostgreSQL with 10M rows, active writes during deployment
- Constraint: cannot break database schema compatibility between blue and green versions

### Strategy: Expand/Contract (a.k.a. Parallel-Change Pattern)

Phase 1 — **Expand** (deploy new schema alongside old, backward compatible):
```sql
-- Safe: adding column with default, not removing old column
ALTER TABLE payments ADD COLUMN idempotency_key VARCHAR(64) DEFAULT '';
```
Both old (blue) and new (green) code can work with this schema.

Phase 2 — **Traffic shift** (no code breakage since schema is compatible):
- AWS: weighted target group — shift 10% → 50% → 100% over 20 minutes
- Kubernetes: `spec.strategy.type: RollingUpdate` with `maxSurge: 1, maxUnavailable: 0`
- Monitor: P99 latency alert at 8ms → auto-rollback (Flagger or custom controller)

Phase 3 — **Contract** (after 100% traffic on new version for 24h+):
```sql
-- Now safe to clean up old column
ALTER TABLE payments DROP COLUMN old_column;
```

### Zero Dropped Requests
- **Connection draining**: 30-second drain on pods being terminated (`terminationGracePeriodSeconds: 30`)
- **Pre-stop hook**: pod sends `HTTP /drain` to itself, stops accepting new connections, drains in-flight requests
- **PodDisruptionBudget**: `maxUnavailable: 0` ensures at least one pod is always running during node drain

### Rollback
- Instant: shift traffic back to blue (AWS: weight 100/0)
- Schema rollback: if contract phase hasn't run, schema is still backward compatible — no schema rollback needed
- Database point-in-time recovery: RDS PITR provides 5-minute RPO if a bad migration is detected late

***

## Problem 5: Design a Cloud Cost Management System (FinOps at Scale)

**Prompt:** "Design a system that gives each of 150 engineering teams real-time visibility
into their cloud spend, generates automatic right-sizing recommendations, and enforces
budget guardrails."

### Components

```
AWS Cost & Usage Report (CUR) → S3
    │
    ▼
AWS Athena (SQL on CUR) + Kubecost (K8s allocation)
    │
    ▼
Data pipeline (Airflow/Glue) → Cost Data Warehouse (Redshift/BigQuery)
    │
    ▼
    ├── Grafana dashboards (team-level cost views)
    ├── Slack bot (daily cost digest per team)
    └── Budget enforcement (Lambda → SNS → Slack/PagerDuty)
```

### Tagging Governance (Foundation)
Without consistent tags, cost attribution is impossible:
- **Mandatory tags** enforced by AWS Config rule + SCP: `team`, `service`, `environment`, `cost-center`
- **Drift detection**: Lambda runs nightly, identifies untagged resources, emails the owning team
- **New resource gate**: Kyverno blocks untagged K8s resources; SCP blocks EC2 launch without tags

### Right-sizing Recommendations
- **EC2**: AWS Compute Optimizer + custom analysis of CloudWatch utilization data
- **Kubernetes**: VPA + Goldilocks controller generates `--requests` / `--limits` recommendations per Deployment
- **RDS**: CloudWatch DB metrics → if average CPU < 20% for 30 days → recommend instance class down

### Budget Guardrails
```
Team budget: $10,000/month
  │
  ├── 80% ($8,000) → Slack warning to team lead
  ├── 90% ($9,000) → Slack + Email to VP Engineering
  └── 100% ($10,000) → Auto-scale-down non-prod resources + PagerDuty
```

### Unit Economics Dashboard
```sql
-- Cost per API request
SELECT
  date_trunc('day', usage_date) AS day,
  SUM(unblended_cost) / SUM(api_requests) AS cost_per_request
FROM aws_costs
JOIN api_metrics USING (service_tag, day)
WHERE service_tag = 'payments-api'
GROUP BY 1
ORDER BY 1;
```

***

## Problem 6: Design a Self-Healing Infrastructure System

**Prompt:** "Design a system that automatically detects and remediates common infrastructure
failures without human intervention, targeting 80% of incidents auto-resolved."

### Detection Layers
```
1. Synthetic monitoring (Blackbox Exporter) — probe endpoints every 30s
2. Prometheus alerts — metric-based anomaly detection
3. Kubernetes liveness/readiness probes — pod-level health
4. CloudWatch alarms — AWS resource health
5. Log-based alerts (Loki) — error rate spikes in log stream
```

### Remediation Runbook Library

| Failure | Auto-Remediation | Trigger |
|:---|:---|:---|
| Pod CrashLoopBackOff | K8s restarts automatically (backoff policy) | Native Kubernetes |
| Node NotReady | Drain node + terminate + ASG replaces | Node problem detector → Lambda |
| High memory on EC2 | Kill OOM process + alert | CloudWatch alarm → SSM Run Command |
| Certificate expiry < 14 days | Renew via cert-manager + ACME | cert-manager automatic |
| Disk > 85% | Clean up old Docker images + log rotation | Prometheus → AlertManager → webhook → SSM |
| DB connection pool exhausted | Restart PgBouncer | Alert → Lambda → ECS task restart |
| 5xx spike (> 1% for 5 min) | Rollback to previous deployment | Flagger abort → ArgoCD rollback |
| DNS resolution failure | Flush CoreDNS cache + restart CoreDNS pod | Alert → Kubernetes Job |

### Auto-Remediation Architecture
```
Alert fires in Alertmanager
    │
    ▼
Alertmanager webhook → Remediation Router (Lambda/Argo Events)
    │
    ├── Matches known failure signature?
    │       YES → Execute pre-approved runbook
    │       NO  → Page on-call + create incident ticket
    │
    ▼
Execute remediation (SSM, kubectl, AWS API)
    │
    ▼
Verify health (re-check probe)
    │
    ├── Healthy → Close alert, log action, update runbook metrics
    └── Still unhealthy → Escalate to on-call
```

### Guardrails
- Auto-remediation only touches non-production automatically; production requires on-call approval via Slack button
- All automated actions logged to CloudTrail and incident ticket for postmortem review
- Rate limiting: max 3 automated remediations of the same type per hour (prevents remediation loops)

***

## Problem 7: Design a Secrets Management Platform for a 500-Person Engineering Org

**Prompt:** "Design a centralized secrets management system that handles 50k secret reads/day,
supports multiple cloud providers, provides full audit logging, and requires zero developer
credential management."

### Architecture

```
Vault Cluster (3-node HA, Raft storage backend)
    │
    ├── Auth Methods
    │       ├── Kubernetes (for pods): projected service account tokens
    │       ├── AWS IAM (for Lambda, EC2): instance identity documents
    │       ├── GitHub OIDC (for CI/CD): keyless, no stored tokens
    │       └── LDAP/OIDC (for humans): SSO via Okta
    │
    ├── Secret Engines
    │       ├── KV v2 (static secrets with versioning)
    │       ├── Database (dynamic PostgreSQL/MySQL credentials)
    │       ├── PKI (internal CA, auto-issuing TLS certs)
    │       └── AWS/GCP (dynamic cloud credentials)
    │
    └── Audit Backend → CloudWatch Logs / S3
```

### Dynamic Credentials Pattern (eliminates 90% of static secrets)
```
Pod starts → reads IRSA token → Vault Kubernetes auth
    │
    ▼
Vault issues: db_user=vault-myapp-abc123, password=<random>, TTL=1h
    │
    ▼
Pod uses credentials for 1 hour
    │
    ▼
Vault auto-revokes credentials after TTL
    │
    ▼
Vault agent sidecar renews before expiry (transparent to application)
```

### Namespace/Team Isolation
```hcl
# Policy per team — payments team can only read their secrets
path "secret/data/payments/*" {
  capabilities = ["read", "list"]
}
path "database/creds/payments-readonly" {
  capabilities = ["read"]
}
# Explicit deny for other teams' paths
path "secret/data/engineering/*" {
  capabilities = ["deny"]
}
```

### High Availability & DR
- **3-node Raft cluster** — leader election, 2/3 quorum required for writes
- **Auto-unseal via AWS KMS** — no human required to unseal after restart
- **Cross-region standby**: Vault Enterprise replication to a DR cluster in a second region; RTO < 5 minutes
- **Backup**: daily snapshot to S3, tested monthly (restore drill)

***

## Problem 8: Design a Multi-Cloud Networking Architecture

**Prompt:** "Your company uses AWS for primary workloads and Azure for ML training.
Design a network architecture that connects both clouds with consistent security policies
and < 10ms latency between them."

### Requirements
- AWS (primary): 20 VPCs, 10k workloads
- Azure (ML): 5 VNets, GPU clusters
- Latency budget: < 10ms cross-cloud (limited — must minimize hops)
- Security: all traffic encrypted, mutual authentication between workloads

### Connectivity Options

| Option | Latency | Cost | Security |
|:---|:---|:---|:---|
| Public internet + VPN | 20-100ms | Low | Medium (IPSec) |
| AWS DirectConnect + Azure ExpressRoute (via co-location) | 5-10ms | High | High (private fiber) |
| Megaport/Equinix Fabric | 3-8ms | Medium | High (dedicated layer 2) |

**Chosen:** Megaport Cloud Router at a shared co-location facility — provides a layer 2 circuit from AWS Direct Connect gateway → Megaport → Azure ExpressRoute, achieving < 8ms with no internet exposure.

### Architecture
```
AWS VPC (us-east-1)          Azure VNet (eastus)
    │                              │
AWS Direct Connect             Azure ExpressRoute
    │                              │
    └──────── Megaport ────────────┘
              Cloud Router
```

### Security
- **mTLS** between all cross-cloud service calls (Istio federation or mutual cert pinning)
- **AWS PrivateLink / Azure Private Endpoint** for services that must be consumed from the other cloud
- **Centralized firewall** (AWS Network Firewall or Palo Alto in transit VPC) inspects all cross-cloud traffic
- **DNS**: Route 53 Resolver + Azure Private DNS Zones — unified FQDN resolution across both clouds

### CIDR Planning
- AWS: `10.0.0.0/8` → `/16` per VPC
- Azure: `172.16.0.0/12` → `/16` per VNet
- No CIDR overlap — enables direct routing without NAT

***

## Problem 9: Design an ML Model Serving Platform (MLOps)

**Prompt:** "Design an ML model serving platform that handles 10k inference requests/second
with P99 < 100ms, supports A/B testing, and enables data scientists to deploy new models
in < 30 minutes without needing DevOps help."

### Components

```
Data Scientist
    │
    ├── Model Registry (MLflow / Vertex AI Model Registry)
    │       └── Stores model artifact + metadata + evaluation metrics
    │
    ▼
Self-Service Deploy Portal (Backstage template / CLI)
    │
    ▼
Model Serving Infrastructure
    ├── Inference Server: Triton / TorchServe / vLLM (for LLMs)
    ├── Orchestration: Kubernetes + KServe (model CRD)
    └── Traffic management: Istio VirtualService (A/B, canary, shadow)
```

### Traffic Patterns
```yaml
# A/B test: 90% model-v1, 10% model-v2
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
spec:
  http:
    - route:
        - destination: {host: model-v1, port: 8080}
          weight: 90
        - destination: {host: model-v2, port: 8080}
          weight: 10
```

### Autoscaling for Spiky Inference
- **KEDA**: scale Triton server replicas based on GPU queue depth (custom metric)
- **GPU node pools**: Karpenter provisions GPU nodes on demand (< 3 minutes), scales to zero at night
- **Request batching**: Triton's dynamic batching accumulates requests for 2ms, batches GPU inference — increases throughput 10x vs single-request mode

### Model Versioning & Rollback
- Every deployed model is tagged with a Git commit SHA, training run ID, and evaluation score
- Rollback: `kubectl patch inferenceservice my-model --patch '{"spec":{"predictor":{"model":{"storageUri":"s3://models/v2/"}}}}'`
- Shadow mode: new model receives 100% of traffic as shadow (requests copied, responses discarded) for 24h validation before any real traffic

### P99 < 100ms Optimization
- Model warm-up: pre-load models on pod start; first-request cold start avoided
- Connection pooling: gRPC persistent connections from client pool to Triton
- Model quantization: INT8 over FP32 — 3-4x inference speedup, < 1% accuracy loss for most models
- Regional caching: KV-cache for LLMs via vLLM's prefix caching

***

## Problem 10: Design a Chaos Engineering Practice for Production

**Prompt:** "Design a chaos engineering program for a 200-service platform. The goal is
to proactively find weaknesses before incidents do."

### Maturity Stages

| Stage | Focus | Tools |
|:---|:---|:---|
| 1 — Game Days | Manual chaos, learning | Any (kill a pod manually) |
| 2 — Automated in Staging | Schedule experiments, verify hypothesis | Chaos Monkey, Litmus |
| 3 — Automated in Production | Controlled blast radius, SLO guardrails | Chaos Mesh, Gremlin |
| 4 — Continuous | Chaos runs 24/7 in prod within safety bounds | Steady State Hypothesis as CI gate |

### Experiment Design
```
1. Define Steady State (what does "normal" look like?)
   → P99 latency < 200ms, error rate < 0.1%, throughput > 8000 RPS

2. Hypothesis
   → "If we kill 1 of 3 API replicas, the service remains within steady state"

3. Inject Fault
   → Terminate random pod every 5 minutes for 1 hour

4. Observe
   → Monitor SLIs in Grafana during experiment

5. Conclusion
   → If steady state held: confidence in resilience
   → If not: file reliability debt ticket, fix before next experiment
```

### Common Chaos Experiments

| Experiment | What It Tests |
|:---|:---|
| Kill random pod | Kubernetes self-healing, PDB effectiveness |
| Inject 500ms latency | Timeout configuration, retry storms |
| Exhaust CPU on one node | Cluster autoscaler, HPA responsiveness |
| Partition network between services | Circuit breaker, fallback behavior |
| Delete a Kubernetes Secret | Error handling for missing config |
| Inject DNS failures | DNS caching, fallback resolution |
| Fill disk on a worker node | Log rotation, disk pressure handling |
| Kill the database primary | Failover time, connection retry logic |

### Guardrails
- **SLO gate**: if error budget consumption rate > 5x during experiment → auto-abort
- **Blast radius**: experiments scoped to < 5% of traffic in production
- **Business hours only**: no chaos during peak traffic, on-call only experiments at night
- **Runbook**: every experiment has a documented abort procedure
