# Production Scenarios & Troubleshooting Drills (Senior Level)

### Scenario 1: Identifying "Orphaned" Cloud Spend
**Problem:** AWS bill is high but usage looks low.
**Fix:** Audit unattached EBS volumes, idle Load Balancers, and unused Elastic IPs. Use **CloudCustodian** for automated "Garbage Collection" of cloud resources.

### Scenario 2: Infrastructure Self-Service with Backstage
**Problem:** Developers wait days for infrastructure.
**Fix:** Create a "Service Template" in **Backstage**. Developers fill a form, and Backstage triggers a GitHub Action that runs Terraform to provision the resource instantly.

### Scenario 3: FinOps - The "Chargeback" Challenge
**Problem:** The Finance team wants to know which team spent $50k on EKS last month.
**Fix:** Implement a strict **Tagging Policy**. Use **KubeCost** to break down EKS costs by Namespace, Label, or Service, and export it to a BI tool like Tableau.

***

## Scenario 1: The "Unattached EBS" Cost Leak
**Symptom:** Your AWS bill shows $5,000 for EBS volumes, but you only have 10 instances.
**Diagnosis:** When EC2 instances are deleted, their EBS volumes are often left behind as "Available" (orphaned).
**Fix:** Use a script or tool (like CloudCustodian) to find and delete unattached EBS volumes.

## Scenario 2: Internal Developer Platform (IDP) "Click Moment"
**Symptom:** Developers are complaining that it takes 2 weeks to get a new S3 bucket.
**Diagnosis:** The process is manual and tickets-based.
**Fix:** Build a "Self-Service" portal using Backstage or a Terraform-based internal module that allows developers to provision standard resources via a simple YAML config.

***

## Scenario 3: Backstage Catalog Showing Stale / Missing Services
**Symptom:** Backstage software catalog shows 150 services, but engineering knows there are 230. Some entries show outdated owners and broken links. Developers have stopped using Backstage because "it's not accurate."

**Diagnosis:**
```bash
# Check entity processor errors
# In Backstage logs (running in k8s)
kubectl logs -n backstage deployment/backstage --tail=200 | grep -i "error\|warn\|catalog"

# Check GitHub integration — is it discovering all repos?
# catalog-info.yaml files may be missing from newer repos
gh api graphql -f query='
{
  organization(login: "myorg") {
    repositories(first: 100) {
      nodes {
        name
        object(expression: "HEAD:catalog-info.yaml") {
          ... on Blob { text }
        }
      }
    }
  }
}'  | jq '[.data.organization.repositories.nodes[] | select(.object == null) | .name]'

# Check processor refresh rate
# Default: 3h. Staleness = delay between repo change and catalog update
```

**Root Causes and Fixes:**

1. **Services don't have `catalog-info.yaml`** — Teams create new repos but don't add the descriptor. Adoption requires active enforcement.
```yaml
# catalog-info.yaml minimum viable
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: payment-service
  annotations:
    github.com/project-slug: myorg/payment-service
    backstage.io/techdocs-ref: dir:.
spec:
  type: service
  lifecycle: production
  owner: group:payments-team
```
Enforcement: add a GitHub Action that fails PRs if `catalog-info.yaml` is missing in new service repos.

2. **GitHub App credentials expired** — Backstage uses a GitHub App token to discover repos. If the app installation token expires or the GitHub App is re-installed, discovery stops silently.
```bash
# Test GitHub integration
curl -H "Authorization: token $BACKSTAGE_GITHUB_TOKEN" \
  https://api.github.com/orgs/myorg/repos?per_page=1
```

3. **Entity refresh too slow** — Default 3h refresh means changes take 3h to appear. For active orgs, reduce the refresh schedule:
```yaml
# app-config.yaml
catalog:
  processingInterval:
    min:
      minutes: 30
    max:
      minutes: 60
```

4. **Stale ownership** — Owner `group:payments-team` referenced but the group entity doesn't exist (team renamed). Add a `catalog-lint` step to CI that validates references exist.

**Prevention:** Add a weekly job that reports orphaned repos (no `catalog-info.yaml`) and broken references. Track Backstage adoption as a DORA-adjacent metric: % of services with up-to-date catalog entries.

***

## Scenario 4: Crossplane Composition Drift — Managed Resources Out of Sync
**Symptom:** An RDS instance provisioned via a Crossplane `PostgreSQLInstance` claim has been manually modified in the AWS Console (instance class changed). Crossplane is continuously reconciling — updating logs show drift corrections every 5 minutes, causing brief RDS parameter group reloads.

**Diagnosis:**
```bash
# Check the managed resource status
kubectl get managed -A | grep rds

# Check reconciliation events
kubectl describe rdsinstance.database.aws.crossplane.io my-db-xyz

# Check the diff Crossplane is seeing
kubectl get rdsinstance.database.aws.crossplane.io my-db-xyz -o jsonpath='{.status.conditions}' | jq .

# Check provider-aws controller logs
kubectl logs -n crossplane-system -l pkg.crossplane.io/revision=provider-aws-xyz --tail=100 | grep "my-db"
```

**Root Causes and Fixes:**

1. **Manual change to a Crossplane-managed resource** — Crossplane is the source of truth. It will revert manual changes. This is by design but causes disruption if the manual change was intentional.
```bash
# Option A: Update the Composition/Claim to match the intended state
kubectl patch postgresqlinstance my-db --type=merge \
  -p '{"spec": {"parameters": {"instanceClass": "db.r6g.xlarge"}}}'

# Option B: Pause reconciliation for emergency changes
kubectl annotate managed rdsinstance.database.aws.crossplane.io my-db-xyz \
  crossplane.io/paused=true
# Make the change, then un-pause
kubectl annotate managed rdsinstance.database.aws.crossplane.io my-db-xyz \
  crossplane.io/paused-
```

2. **Composition doesn't expose the field that was changed** — If `instanceClass` is hardcoded in the Composition rather than exposed as a parameter, teams are forced to make console changes. Fix the Composition to expose it.
```yaml
# In Composition patches
- fromFieldPath: spec.parameters.instanceClass
  toFieldPath: spec.forProvider.instanceClass
```

3. **Drift detection alerting** — Set up an alert when managed resource `Ready` condition is `False` for more than 10 minutes (indicating reconciliation is failing, not just converging).

**Prevention:** Block console access to Crossplane-managed resources using AWS SCP that denies modifications to resources tagged `crossplane-managed: true`. Enforce this tag via the Composition.

***

## Scenario 5: FinOps Anomaly — Unexpected $80k Spike in One Week
**Symptom:** The weekly cost report shows an $80k spike vs the $22k baseline. AWS Cost Explorer shows the increase is in `EC2-Other` under the `us-east-1` region for the `data-platform` cost allocation tag.

**Diagnosis:**
```bash
# Drill into EC2-Other — this line item includes: NAT Gateway, data transfer, EBS snapshots, EIP
aws ce get-cost-and-usage \
  --time-period Start=2024-11-01,End=2024-11-08 \
  --granularity DAILY \
  --filter '{"Tags": {"Key": "team", "Values": ["data-platform"]}}' \
  --group-by Type=DIMENSION,Key=USAGE_TYPE \
  --metrics UnblendedCost \
  --query 'ResultsByTime[*].Groups[*].{Type:Keys[0],Cost:Metrics.UnblendedCost.Amount}' \
  | jq 'flatten | sort_by(-.Cost | tonumber) | .[0:10]'

# Likely culprit: DataTransfer-Out-Bytes
# Find which EC2 instances are generating the most egress
# Use VPC Flow Logs → Athena query
aws athena start-query-execution \
  --query-string "SELECT srcaddr, dstaddr, SUM(bytes) as total_bytes FROM vpc_flow_logs WHERE action='ACCEPT' AND start > 1699834800 GROUP BY srcaddr, dstaddr ORDER BY total_bytes DESC LIMIT 20" \
  --result-configuration OutputLocation=s3://my-athena-results/
```

**Root Causes and Fixes:**

1. **Data platform job writing large intermediate results to S3 across AZs or regions** — AZ-to-AZ data transfer is $0.01/GB; cross-region is $0.09/GB. A Spark job that shuffles 1TB across AZs costs $10k.
```bash
# Check: was a new Spark job or ETL pipeline added that week?
git log --since="2024-10-25" --until="2024-11-01" -- data-platform/ --oneline

# Fix: ensure Spark writes locally within AZ, pin executors to one AZ
# Or use S3 Transfer Acceleration / same-region endpoints
```

2. **EBS snapshot policy misconfigured** — A new backup policy creating hourly snapshots of 20TB volumes. EBS snapshot storage = $0.05/GB-month.
```bash
aws ec2 describe-snapshot-attributes # find excessive snapshots
aws dlm get-lifecycle-policies       # review DLM policies
```

3. **NAT Gateway egress surge** — A debugging log statement added to production was logging full request/response bodies (MB-sized payloads) to an external logging service.

**Prevention:** Set AWS Budget alerts at 10% week-over-week increase. Use Cost Anomaly Detection with `DAILY` granularity and `ABSOLUTE` threshold of $5k. Route anomaly alerts to `#finops-alerts` Slack channel with AWS Cost Explorer deep-link.

***

## Scenario 6: Reserved Instance Coverage Gap After Team Restructuring
**Symptom:** RI utilization drops from 94% to 67% after a team migrates their workloads from `m5.xlarge` to Graviton `m6g.xlarge`. You're paying for unused reserved capacity.

**Diagnosis:**
```bash
# Check RI utilization by instance type
aws ce get-reservation-utilization \
  --time-period Start=2024-11-01,End=2024-11-30 \
  --group-by Type=DIMENSION,Key=INSTANCE_TYPE \
  --query 'Total.UtilizationPercentage'

# Find which RIs are underutilized
aws ec2 describe-reserved-instances \
  --filters Name=state,Values=active \
  --query 'ReservedInstances[*].{Type:InstanceType,Count:InstanceCount,AZ:AvailabilityZone,End:End}'

# Check RI Marketplace — can you sell the unused RIs?
aws ec2 describe-reserved-instances-modifications
```

**Root Causes and Fixes:**

1. **x86 RIs don't cover Graviton instances** — `m5.xlarge` (x86) RIs don't apply to `m6g.xlarge` (ARM). These are different instance families.

2. **Options for unused RIs:**
```bash
# Option A: Sell on RI Marketplace (for 1-year or 3-year term with >1 month remaining)
# Recover 60-90% of remaining value

# Option B: Instance size flexibility — m5 RIs within the same family can cover m5.2xlarge at 50% or m5.large at 200%
# But m5 can't flex to m6g

# Option C: Convert to Compute Savings Plans (more flexible, applies across instance families)
# Purchase new Savings Plans, let RIs expire naturally

# Option D: Modify the RI to a different AZ if the team moved regions
aws ec2 modify-reserved-instances \
  --reserved-instances-ids ri-abc123 \
  --target-configurations AvailabilityZone=us-east-1b,InstanceCount=5
```

3. **Process fix** — Before any infrastructure migration that changes instance family, require a FinOps review. Add a checklist item: "Are we moving RI coverage? Notify FinOps team."

**Prevention:** Set a CloudWatch alarm when RI utilization drops below 80% for any instance family. Prefer Compute Savings Plans over instance-type-specific RIs for workloads that may migrate. Review RI portfolio quarterly with the FinOps team.

***

## Scenario 7: IDP Golden Path Broken — New Team Can't Onboard
**Symptom:** A new team follows the IDP self-service workflow (Backstage → GitHub template → Terraform → ArgoCD), but the pipeline fails at step 3 with "namespace already exists" and step 4 with "AppProject not found."

**Diagnosis:**
```bash
# Reproduce by running the scaffolder workflow dry-run
# Check what the template generates
cat .github/templates/new-service/template.yaml

# Check if the namespace was partially created
kubectl get ns | grep new-team

# Check ArgoCD AppProject
argocd appproject list | grep new-team
kubectl get appproject new-team -n argocd

# Check the GitHub Actions workflow that was triggered
gh run list --workflow=new-service-onboarding.yaml --limit=5
gh run view 12345678 --log
```

**Root Causes and Fixes:**

1. **Namespace was created by a previous failed run, and the Terraform `create_namespace` resource errors on conflict** — The golden path must be idempotent.
```hcl
resource "kubernetes_namespace" "team" {
  metadata { name = var.team_name }
  lifecycle {
    ignore_changes = [metadata[0].annotations, metadata[0].labels]
  }
}
# Or use: terraform import kubernetes_namespace.team new-team
```

2. **ArgoCD AppProject created by a separate Terraform workspace that hasn't run yet** — The onboarding pipeline has implicit sequencing not captured in the template. Make the AppProject creation a dependency.
```yaml
# In the GitHub Actions workflow
jobs:
  provision-namespace:
    runs-on: ubuntu-latest
    steps: [...]
  provision-argocd:
    needs: provision-namespace  # explicit dependency
    steps: [...]
```

3. **Template variable substitution produced invalid Kubernetes resource names** — Team name "My Team" becomes "My Team" (with space) in namespace name. Add input validation to the Backstage template.
```yaml
# In template.yaml parameters
- id: teamName
  title: Team Name
  type: string
  pattern: '^[a-z0-9-]+$'
  description: "Lowercase letters, numbers, and hyphens only"
```

**Prevention:** Write integration tests for the golden path that run nightly in a sandbox environment. Treat the IDP golden path like production code — changes require a PR, review, and the integration test must pass.

***

## Scenario 8: DORA Metrics Showing Deployment Frequency Regression
**Symptom:** DORA dashboard shows deployment frequency dropped from 12/week to 3/week over 6 weeks. Lead time for change increased from 2 days to 8 days. No obvious incidents or process changes were announced.

**Diagnosis:**
```bash
# Pull raw deployment data from your CD system
# (ArgoCD example)
kubectl get applications -n argocd -o json | jq '
  .items[] | {
    app: .metadata.name,
    syncedAt: .status.operationState.finishedAt,
    health: .status.health.status
  }
' | sort_by(.syncedAt)

# Pull PR merge rate from GitHub
gh api graphql -f query='
{
  repository(owner: "myorg", name: "myrepo") {
    pullRequests(states: MERGED, last: 100) {
      nodes {
        mergedAt
        createdAt
        commits { totalCount }
        reviews { totalCount }
      }
    }
  }
}'

# Check CI pipeline duration trend
# If pipelines slowed down, that inflates lead time
gh run list --limit=100 --json startedAt,conclusion,durationMs | \
  jq 'map(select(.conclusion == "success")) | map(.durationMs) | add / length'
```

**Root Causes and Fixes:**

1. **New mandatory approval gates were added without measurement** — A security team added a mandatory AppSec review gate to all PRs. PRs now wait 3-5 days for the AppSec queue.
   - Fix: add AppSec review early (on PR open, async) rather than as a blocking gate before merge. Auto-approve PRs with no security-relevant file changes (e.g., only docs changed).

2. **CI pipeline slowdown** — A new integration test suite was added that takes 45 minutes. Developers batch their PRs to reduce CI wait times, naturally reducing deployment frequency.
   - Fix: run the slow tests only on merge to main, not on every PR. Or parallelize them with `--shard` flags.

3. **Fear of deploying after a recent incident** — Cultural regression — teams are self-censoring deploys after a high-severity incident. No tooling change needed; the fix is a blameless post-mortem + explicit signal from leadership that frequent small deploys reduce risk.

4. **Service owns too many dependencies** — A monolith architecture means any PR requires coordination across 5 teams, inflating lead time.

**Prevention:** Instrument DORA metrics as first-class observability, not a monthly report. Alert when weekly deployment frequency drops >30% vs the 4-week rolling average. Review in the weekly engineering leads meeting.
