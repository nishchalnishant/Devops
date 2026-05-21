---
description: Cloud FinOps, cost allocation, rightsizing, Kubernetes cost management, and unit economics for senior engineers.
---

# Platform Engineering — FinOps & Cloud Cost Optimization

```
FinOps & Cloud Cost Optimization
├── FinOps Lifecycle
│   ├── INFORM: allocate costs, build dashboards, establish tagging
│   ├── OPTIMIZE: rightsizing, Reserved Instances, Spot, autoscaling
│   └── OPERATE: budgets + alerts, chargeback/showback, anomaly detection
├── Cost Allocation Foundations
│   ├── Tagging strategy: team, environment, service, cost-center tags
│   ├── AWS Cost Allocation Tags: activate in Billing Console
│   ├── Kubernetes: Kubecost / OpenCost for namespace-level attribution
│   └── FOCUS spec: multi-cloud billing normalization schema
├── Rightsizing
│   ├── AWS Compute Optimizer: ML-based instance size recommendations
│   ├── CloudWatch metrics: CPU < 10% sustained = overprovisioned
│   ├── Memory sizing: requires CloudWatch agent or container metrics
│   └── Approach: downsize in staging first, validate, then prod
├── Reserved Capacity
│   ├── Reserved Instances: commit to specific instance type, 30-60% savings
│   ├── Savings Plans: flexible commitment (Compute SP), 20-50% savings
│   ├── Spot Instances: 60-90% savings; suitable for stateless/batch
│   └── Committed Use Discounts (GCP), Azure Reservations: same concept
├── Kubernetes FinOps
│   ├── Kubecost: per-namespace, per-label, per-workload cost
│   ├── Idle cost: requested but unused CPU/memory
│   ├── Efficiency score: actual usage / requested resources
│   ├── VPA: Vertical Pod Autoscaler for right-sized requests/limits
│   └── HPA + KEDA: scale to zero for low-utilization workloads
├── Waste Elimination
│   ├── Orphaned volumes: EBS/PD left after instance deletion
│   ├── Idle load balancers: ALBs with no healthy targets
│   ├── Zombie environments: dev/staging running 24/7 unnecessarily
│   ├── Oversized RDS: CloudWatch DatabaseConnections = 0 → downsize
│   └── CloudCustodian: automated policy-based resource garbage collection
├── Unit Economics
│   ├── Cost per API request = monthly spend / monthly requests
│   ├── Cost per active user = monthly spend / monthly active users
│   ├── Track trend: cost should decrease as scale increases (efficiency)
│   └── Use for capacity planning and ROI conversations with leadership
└── FinOps Tooling
    ├── AWS Cost Explorer: usage trends, RI recommendations
    ├── Infracost: pre-commit IaC cost estimation in CI/CD
    ├── Kubecost / OpenCost: K8s namespace cost
    ├── CloudHealth / Apptio Cloudability: enterprise multi-cloud FinOps
    └── CloudCustodian: automated governance policies for cost control
```

## First Principles

- Cloud cost is variable and invisible by default — it must be made visible before it can be managed.
- Tagging is the foundation: without consistent tags, cost cannot be allocated, accountability cannot exist, and optimization is guesswork.
- FinOps is not about minimizing spend — it is about maximizing value per dollar; sometimes the right answer is to spend more on a service that generates more revenue.
- Rightsizing beats reserved capacity as the first optimization lever: you can't get a discount on waste.
- Unit economics bridges engineering and business: "cost per transaction" is a language that both engineers and executives understand.

## The FinOps Model

FinOps (Financial Operations) is the practice of bringing financial accountability to cloud spending. The goal is not to minimize spend — it's to maximize **value per dollar**.

```
FinOps Lifecycle:

  INFORM                  OPTIMIZE               OPERATE
  ──────                  ────────               ───────
  Allocate costs      →   Rightsizing        →   Budgets + alerts
  Dashboards              Reserved instances      Chargeback
  Unit economics          Spot instances          Anomaly detection
  Tagging strategy        Autoscaling             Engineering culture
```

***

## Cost Allocation — The Foundation

Without proper tagging, you cannot allocate costs to teams or services.

### Tagging Strategy

```hcl
# Enforce these tags on ALL resources via Terraform
locals {
  mandatory_tags = {
    team        = var.team_name          # "payments", "search"
    service     = var.service_name       # "checkout-api"
    environment = var.environment        # "production", "staging"
    cost_center = var.cost_center        # "eng-123"
    managed_by  = "terraform"
  }
}

resource "aws_instance" "web" {
  tags = merge(local.mandatory_tags, {
    Name = "${var.service_name}-web"
  })
}
```

### AWS Cost Allocation Tags

```bash
# Activate tags for cost allocation in AWS Cost Explorer
aws ce update-cost-allocation-tags-status \
  --cost-allocation-tags-status \
    TagKey=team,Status=Active \
    TagKey=service,Status=Active
```

***

## The "Cost Killer" Checklist

### 1. Idle Resources

```bash
# Find unattached EBS volumes (pure waste)
aws ec2 describe-volumes \
  --filters Name=status,Values=available \
  --query 'Volumes[*].[VolumeId,Size,CreateTime]'

# Find unused Elastic IPs (charged when not attached to running instance)
aws ec2 describe-addresses \
  --query 'Addresses[?AssociationId==null].[PublicIp,AllocationId]'

# Find old untagged snapshots
aws ec2 describe-snapshots --owner-ids self \
  --query 'Snapshots[?Tags==null].[SnapshotId,StartTime,VolumeSize]'
```

### 2. Rightsizing EC2

```bash
# Use AWS Compute Optimizer recommendations
aws compute-optimizer get-ec2-instance-recommendations \
  --filters name=Finding,values=Overprovisioned \
  --query 'instanceRecommendations[*].[instanceArn,finding,recommendationOptions[0].instanceType]'
```

### 3. Savings Plans vs Reserved Instances

| Option | Flexibility | Savings | Commitment |
|:---|:---|:---|:---|
| **On-Demand** | Maximum | 0% | None |
| **Savings Plans (Compute)** | High (any instance, region, OS) | ~66% | 1 or 3 year |
| **Savings Plans (EC2)** | Medium (family + region) | ~72% | 1 or 3 year |
| **Reserved Instances** | Low (fixed instance type) | ~75% | 1 or 3 year |
| **Spot Instances** | Low (can be interrupted) | ~90% | None |

**Senior Strategy:** Buy Savings Plans for baseline (always-on) workloads. Use Spot for batch and stateless workloads. On-demand for burst and new services.

***

## Kubernetes Cost Management

### Per-Team Namespace Cost Allocation with Kubecost

```yaml
# Install Kubecost via Helm
helm install kubecost cost-analyzer \
  --repo https://kubecost.github.io/cost-analyzer/ \
  --namespace kubecost \
  --set prometheus.enabled=true

# Kubecost provides:
# - Cost per namespace / label / deployment
# - Efficiency score (requested vs used)
# - Savings recommendations
```

### Request vs. Limit Right-Sizing

```
Pod requests:  CPU=100m,  Memory=128Mi
Pod limits:    CPU=2000m, Memory=2Gi
Actual usage:  CPU=50m,   Memory=100Mi

Node is ALLOCATED for: 2000m CPU, 2Gi RAM
Node ACTUALLY USES:    50m CPU,   100Mi RAM

→ Efficiency: 2.5% CPU, 5% Memory  ← Extreme waste!

Fix: Use VPA (recommendation mode) to right-size requests
```

### Spot Instances for Non-Critical Workloads

```yaml
# EKS Node Group with Spot Instances
resource "aws_eks_node_group" "batch" {
  instance_types = [
    "m5.xlarge",
    "m5a.xlarge",   # Multiple types = higher Spot availability
    "m4.xlarge",
  ]
  capacity_type = "SPOT"

  # Pod scheduling: tolerate Spot interruptions
  # Add taint to Spot nodes and toleration to batch pods
}
```

***

## Unit Economics — The Senior Metric

Unit economics translates cloud cost into business value:

```
Cost per API request    = Monthly cloud cost / Monthly API requests
Cost per user           = Monthly cloud cost / Monthly active users
Cost per GB processed   = Monthly cloud cost / GB of data processed
Cost per deployment     = CI/CD costs / Number of deployments

Target: Drive unit cost DOWN as usage grows (economies of scale)
Alert: If unit cost RISES as usage grows → architectural inefficiency
```

***

## FinOps Culture & Chargeback

| Model | Description | When to Use |
|:---|:---|:---|
| **Show-back** | Teams see their costs but not charged | Starting out; build awareness |
| **Chargeback** | Teams are billed for their costs | Mature org; drives accountability |
| **Budgets + Alerts** | Alert when team exceeds budget | All stages |

**AWS Budgets for Team Accountability:**
```bash
aws budgets create-budget \
  --account-id $ACCOUNT_ID \
  --budget '{
    "BudgetName": "payments-team-monthly",
    "BudgetLimit": {"Amount": "5000", "Unit": "USD"},
    "TimeUnit": "MONTHLY",
    "BudgetType": "COST",
    "CostFilters": {
      "TagKeyValue": ["team$payments"]
    }
  }' \
  --notifications-with-subscribers '[{
    "Notification": {"NotificationType": "ACTUAL", "ComparisonOperator": "GREATER_THAN", "Threshold": 80},
    "Subscribers": [{"SubscriptionType": "EMAIL", "Address": "payments-team@company.com"}]
  }]'
```

***

## Logic & Trickiness Table

| Pattern | Junior Thinking | Senior Thinking |
|:---|:---|:---|
| **Cost reduction** | "Shut down non-prod on weekends" | Map cost to unit economics first; then find the highest-value optimization |
| **Reserved Instances** | Buy 3-year for everything | Buy for stable baseline only; never commit to instance types that might change |
| **Spot Instances** | Too risky for production | Safe for stateless, batch, or K8s with proper interruption handling |
| **K8s efficiency** | Maximize bin-packing | Set requests accurately first; over-packing causes OOM and poor QoS |
| **Tagging** | "We'll add tags later" | Tag from day 1 in IaC; retroactive tagging is nearly impossible |
| **Savings** | Focus on infra discounts only | Data transfer costs (cross-AZ, internet) are often the hidden largest bill |

***

## System Design Perspective

**Enterprise FinOps Platform Architecture**
- Data pipeline: AWS Cost and Usage Report (CUR) → S3 → Glue crawler → Athena → Grafana; run daily; partition by account, service, and tag.
- Multi-cloud normalization: adopt FOCUS spec schema; write ETL to map AWS CUR + Azure Cost Management + GCP Billing Export into a unified schema before loading to the data warehouse.
- Showback automation: weekly Lambda that queries Athena, computes per-team deltas vs prior week, and posts a formatted Slack message to each team's channel — zero manual effort.

**Kubernetes Cost Optimization Architecture**
- Deploy Kubecost in-cluster with Prometheus integration; expose Grafana dashboards per namespace.
- VPA in recommendation mode first (observe for 2 weeks) → apply resource request adjustments without disruption.
- KEDA for event-driven workloads: scale to zero consumer pods when SQS queue is empty — eliminates idle cost for async workloads.
- Node autoscaler (Karpenter): provision right-sized nodes for actual pod requests; consolidate under-utilized nodes automatically.

**FinOps Governance Integration with IDP**
- Every Backstage template enforces required cost tags at provisioning time — no resource can be created without team, environment, and service tags.
- Infracost CI gate: if a PR increases estimated monthly cost by > $500, require a platform team approval before merge.
- Budget alerts routed to team channels (not a central finance inbox) — teams own their spend and are notified first.
