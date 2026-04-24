# AWS — Deep Dive Notes

## IAM Internals

### Policy evaluation logic

```
Request arrives (principal, action, resource, conditions)
    │
    ├── 1. Explicit Deny in any policy? → DENY (always wins)
    │
    ├── 2. SCP allows? (if Organizations account)
    │       SCP does NOT grant permissions — it only restricts
    │       Management account is NOT restricted by SCPs
    │
    ├── 3. Resource-based policy allows + principal is same account? → ALLOW
    │
    ├── 4. Identity-based policy allows? → ALLOW
    │
    ├── 5. Session policy allows? (for assumed roles)
    │
    └── Default: IMPLICIT DENY
```

### Trust policy vs permission policy

```json
// Trust policy: WHO can assume this role
{
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "Service": "lambda.amazonaws.com",
      "AWS": "arn:aws:iam::123456789012:role/ci-role"
    },
    "Action": "sts:AssumeRole",
    "Condition": {
      "StringEquals": {
        "sts:ExternalId": "my-external-id"
      }
    }
  }]
}

// Permission policy: WHAT the role can do
{
  "Statement": [{
    "Effect": "Allow",
    "Action": ["s3:GetObject", "s3:PutObject"],
    "Resource": "arn:aws:s3:::my-bucket/*",
    "Condition": {
      "StringEquals": {"s3:prefix": "uploads/"}
    }
  }]
}
```

### IRSA (IAM Roles for Service Accounts)

```bash
# 1. Associate OIDC provider with EKS cluster
eksctl utils associate-iam-oidc-provider \
  --cluster my-cluster --approve

OIDC_ISSUER=$(aws eks describe-cluster \
  --name my-cluster \
  --query "cluster.identity.oidc.issuer" \
  --output text)

# 2. Create role with trust policy referencing the OIDC provider
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

cat > trust.json <<EOF
{
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "Federated": "arn:aws:iam::${ACCOUNT_ID}:oidc-provider/${OIDC_ISSUER#https://}"
    },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": {
        "${OIDC_ISSUER#https://}:sub": "system:serviceaccount:my-namespace:my-sa",
        "${OIDC_ISSUER#https://}:aud": "sts.amazonaws.com"
      }
    }
  }]
}
EOF

aws iam create-role --role-name my-app-role --assume-role-policy-document file://trust.json

# 3. Annotate the Kubernetes ServiceAccount
kubectl annotate serviceaccount my-sa \
  -n my-namespace \
  eks.amazonaws.com/role-arn=arn:aws:iam::${ACCOUNT_ID}:role/my-app-role
```

How it works: The pod's ServiceAccount token is projected into the pod at `AWS_WEB_IDENTITY_TOKEN_FILE`. The AWS SDK calls `sts:AssumeRoleWithWebIdentity` with this JWT. The trust policy validates the `sub` claim matches the serviceaccount.

***

## VPC Architecture

### Subnet types and routing

```
Internet Gateway (IGW)
    │
    ▼
Public Subnet (has route 0.0.0.0/0 → IGW)
│   EC2 with public IP ← can receive inbound internet traffic
│   ALB
│
NAT Gateway (in public subnet, has Elastic IP)
    │
    ▼
Private Subnet (has route 0.0.0.0/0 → NAT GW)
│   EKS nodes, EC2 app servers
│   No inbound from internet
│   Outbound only (package downloads, API calls)
│
Isolated Subnet (no 0.0.0.0/0 route at all)
    RDS, ElastiCache
    Can only be reached from within VPC
```

### VPC Endpoints

```bash
# Gateway endpoint (S3 and DynamoDB only — free, no NIC)
# Adds an entry to route tables — traffic stays on AWS backbone
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-abc123 \
  --service-name com.amazonaws.us-east-1.s3 \
  --route-table-ids rtb-abc123 rtb-def456 \  # must add to each route table
  --vpc-endpoint-type Gateway

# Interface endpoint (all other services — costs $0.01/hr/AZ)
# Creates an ENI in your subnet with a private IP
# Requires private DNS enabled so service DNS resolves to private IP
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-abc123 \
  --service-name com.amazonaws.us-east-1.ecr.dkr \
  --vpc-endpoint-type Interface \
  --subnet-ids subnet-abc123 subnet-def456 \
  --security-group-ids sg-abc123 \
  --private-dns-enabled

# Required endpoints for EKS nodes in private cluster:
# com.amazonaws.region.ecr.dkr
# com.amazonaws.region.ecr.api
# com.amazonaws.region.s3 (Gateway)
# com.amazonaws.region.eks
# com.amazonaws.region.sts
# com.amazonaws.region.ec2
```

### Security Groups vs NACLs

| | Security Groups | Network ACLs |
|-|----------------|--------------|
| Level | Instance (ENI) | Subnet |
| State | Stateful (return traffic auto-allowed) | Stateless (must allow both directions) |
| Rules | Allow only | Allow + Deny |
| Evaluation | All rules evaluated | Rules evaluated in order (lowest number first) |
| Default | Deny all inbound, allow all outbound | Allow all inbound and outbound |

***

## EKS — Architecture and Operations

### Control plane vs data plane

```
EKS Control Plane (managed by AWS, in AWS VPC)
    ├── kube-apiserver (HA, multi-AZ)
    ├── etcd (HA, encrypted at rest with KMS)
    ├── kube-scheduler
    └── kube-controller-manager

EKS Data Plane (your VPC)
    ├── Managed Node Groups (EC2 with auto-scaling)
    ├── Fargate Profiles (serverless, per-pod isolation)
    └── Self-managed nodes

Cross-plane communication:
    └── Nodes → API server via cluster endpoint
            Either public (internet) or private (VPC endpoint)
            Private cluster: need VPC endpoint for eks service
```

### Node group operations

```bash
# Check add-on versions before upgrading
aws eks describe-addon-versions --kubernetes-version 1.30 \
  --addon-name vpc-cni \
  --query 'addons[0].addonVersions[0].addonVersion'

# Upgrade add-ons before or after node upgrade (depends on add-on)
# VPC CNI: upgrade BEFORE nodes (new version supports old+new k8s)
aws eks update-addon --cluster-name my-cluster \
  --addon-name vpc-cni \
  --addon-version v1.18.0-eksbuild.1 \
  --resolve-conflicts OVERWRITE

# Upgrade node group
aws eks update-nodegroup-version \
  --cluster-name my-cluster \
  --nodegroup-name ng-1 \
  --kubernetes-version 1.30
# Uses maxUnavailable from the update config
# Respects PodDisruptionBudgets — drain blocks if PDB violated

# Check upgrade progress
aws eks describe-update \
  --cluster-name my-cluster \
  --nodegroup-name ng-1 \
  --update-id <update-id>
```

### EKS Networking — VPC CNI internals

```
Each pod gets a real VPC IP address (no overlay network)
    │
    ├── Secondary IPs pre-allocated on each ENI (warm pool)
    │       WARM_ENI_TARGET: how many ENIs to keep ready
    │       WARM_IP_TARGET: how many IPs to keep ready
    │
    ├── Pod starts → IP assigned from warm pool → instant
    ├── Warm pool drains → new ENI attached → ~10s delay
    │
    └── Max pods per node = (max ENIs × IPs per ENI) - 1
            m5.xlarge: 3 ENIs × 15 IPs - 1 = 44 pods max
```

```bash
# Check current IP allocations
kubectl describe daemonset aws-node -n kube-system | grep -E "WARM|MAX"

# Increase max pods with prefix delegation (supports 110 pods on m5.xlarge)
aws eks update-addon --cluster-name my-cluster \
  --addon-name vpc-cni \
  --configuration-values '{"env":{"ENABLE_PREFIX_DELEGATION":"true","WARM_PREFIX_TARGET":"1"}}'
```

***

## S3 — Internals and Operations

### Consistency model

Since December 2020, S3 provides **strong read-after-write consistency** for all operations. Previously, eventual consistency meant a PUT followed immediately by a GET could return a stale version.

### Storage classes and lifecycle

```
S3 Standard (millisecond access, 11 nines durability)
    │
    ├── S3 Intelligent-Tiering (auto-tiers based on access patterns)
    │
    ├── S3 Standard-IA (30-day minimum, retrieval fee)
    │
    ├── S3 One Zone-IA (single AZ, 20% cheaper, can be lost on AZ failure)
    │
    ├── S3 Glacier Instant Retrieval (milliseconds, 90-day min)
    ├── S3 Glacier Flexible Retrieval (minutes to hours, 90-day min)
    └── S3 Glacier Deep Archive (12-48 hours, 180-day min, cheapest)
```

```json
// Lifecycle policy: move to IA after 30d, Glacier after 90d, delete after 365d
{
  "Rules": [{
    "Status": "Enabled",
    "Filter": {"Prefix": "logs/"},
    "Transitions": [
      {"Days": 30, "StorageClass": "STANDARD_IA"},
      {"Days": 90, "StorageClass": "GLACIER_IR"}
    ],
    "Expiration": {"Days": 365},
    "NoncurrentVersionExpiration": {"NoncurrentDays": 30}
  }]
}
```

### S3 security patterns

```bash
# Block all public access (account level — overrides bucket policies)
aws s3control put-public-access-block \
  --account-id $ACCOUNT_ID \
  --public-access-block-configuration \
    BlockPublicAcls=true,IgnorePublicAcls=true,\
    BlockPublicPolicy=true,RestrictPublicBuckets=true

# Enforce encryption at rest (bucket policy)
aws s3api put-bucket-policy --bucket my-bucket --policy '{
  "Statement": [{
    "Sid": "DenyUnencryptedObjectUploads",
    "Effect": "Deny",
    "Principal": "*",
    "Action": "s3:PutObject",
    "Resource": "arn:aws:s3:::my-bucket/*",
    "Condition": {
      "StringNotEquals": {
        "s3:x-amz-server-side-encryption": "aws:kms"
      }
    }
  }]
}'

# Enforce HTTPS only
"Condition": {"Bool": {"aws:SecureTransport": "false"}}  # → Deny HTTP
```

***

## Lambda — Concurrency and Performance

### Concurrency model

```
Account concurrency limit (default 1000 per region)
    │
    ├── Reserved concurrency: dedicated to a function, blocks others
    │       aws lambda put-function-concurrency --reserved-concurrent-executions 200
    │
    ├── Provisioned concurrency: pre-initialized environments (no cold start)
    │       aws lambda put-provisioned-concurrency-config \
    │         --function-name myFunc --qualifier prod \
    │         --provisioned-concurrent-executions 50
    │
    └── Burst limit: 3000 initial burst, then +500/min until account limit

Cold start:
    New execution environment → Download code + layer → Initialize runtime → Run handler
    Mitigation: provisioned concurrency, keep-warm pings (anti-pattern), smaller deployment package
```

### Lambda + SQS pattern (serverless queue consumer)

```python
def handler(event, context):
    batch_item_failures = []
    
    for record in event['Records']:
        try:
            process(json.loads(record['body']))
        except Exception as e:
            # Report this specific message as failed
            # SQS will retry it (up to maxReceiveCount before DLQ)
            batch_item_failures.append({
                "itemIdentifier": record['messageId']
            })
    
    # Return partial failures — other messages are considered success
    # Requires FunctionResponseTypes: ReportBatchItemFailures on the event source mapping
    return {"batchItemFailures": batch_item_failures}
```

***

## Multi-Account Organization Architecture

```
Management Account (root — never deploy workloads here)
    │
    ├── Security OU
    │   ├── Log Archive account (CloudTrail, Config, VPC Flow Logs)
    │   └── Security Tooling account (GuardDuty delegated admin, Security Hub)
    │
    ├── Infrastructure OU
    │   ├── Network account (Transit Gateway, shared VPCs, Direct Connect)
    │   └── Tooling account (CI/CD, ECR, Artifactory)
    │
    ├── Workloads OU
    │   ├── Production OU
    │   │   ├── prod-us-east-1 account
    │   │   └── prod-eu-west-1 account
    │   └── Non-Production OU
    │       ├── staging account
    │       └── dev account
    │
    └── Sandbox OU (developer experimentation, SCPs allow self-cleanup)
```

### SCPs — key patterns

```json
// Deny all actions outside approved regions
{
  "Sid": "DenyNonApprovedRegions",
  "Effect": "Deny",
  "NotAction": [
    "iam:*",           // IAM is global
    "sts:*",
    "cloudfront:*",
    "route53:*",
    "support:*",
    "trustedadvisor:*"
  ],
  "Resource": "*",
  "Condition": {
    "StringNotEquals": {
      "aws:RequestedRegion": ["us-east-1", "us-west-2", "eu-west-1"]
    }
  }
}

// Deny leaving the Organization
{
  "Sid": "DenyLeaveOrganization",
  "Effect": "Deny",
  "Action": "organizations:LeaveOrganization",
  "Resource": "*"
}

// Protect critical roles from being modified
{
  "Sid": "ProtectFoundationRoles",
  "Effect": "Deny",
  "Action": ["iam:Delete*", "iam:Put*", "iam:Attach*", "iam:Detach*", "iam:Update*"],
  "Resource": [
    "arn:aws:iam::*:role/OrganizationAccountAccessRole",
    "arn:aws:iam::*:role/SecurityAuditRole"
  ]
}
```

***

## CloudWatch — Advanced Patterns

```bash
# Container Insights for EKS (install add-on)
aws eks create-addon \
  --cluster-name my-cluster \
  --addon-name amazon-cloudwatch-observability

# Metric Insights query (SQL-like, cross-account)
aws cloudwatch get-metric-data \
  --metric-data-queries '[{
    "Id": "m1",
    "Expression": "SELECT AVG(CPUUtilization) FROM \"AWS/EC2\" GROUP BY InstanceId",
    "Period": 300
  }]' \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-01T01:00:00Z

# Log Insights query — find Lambda cold starts
aws logs start-query \
  --log-group-name /aws/lambda/my-function \
  --start-time $(date -v-1H +%s) \
  --end-time $(date +%s) \
  --query-string 'filter @type = "REPORT"
    | stats avg(@initDuration) as avgColdStart,
            count(@initDuration) as coldStarts,
            count(*) as total
    | sort total desc'
```

***

## Key Gotchas

| Gotcha | Detail |
|--------|--------|
| SCP denies don't appear in CloudTrail as Deny | The request never reaches the service — CloudTrail shows nothing; use `simulate-principal-policy` to debug |
| IAM policy `NotAction` in Allow | "Allow everything except these actions" — easy to accidentally grant broad permissions |
| S3 ACLs are legacy | Object-level ACLs are disabled by default for new buckets since April 2023; use bucket policies |
| EBS volume AZ lock | An EBS volume can only be attached to an instance in the same AZ; snapshots are needed to move AZs |
| NAT Gateway AZ cost | One NAT GW serves an AZ; cross-AZ traffic to NAT GW costs $0.01/GB — deploy one per AZ |
| RDS parameter group requires reboot | Dynamic parameters apply immediately; static parameters only apply after instance reboot |
| Secrets Manager rotation Lambda VPC | If RDS is in a private subnet, the rotation Lambda must also be in the VPC with a route to RDS |
| EKS managed node group uses Launch Template | Customizations (userData, ami, tags) require a custom launch template — not all fields are modifiable after creation |
| `aws:SourceIp` doesn't work with VPC endpoints | Use `aws:SourceVpce` or `aws:SourceVpc` conditions for VPC endpoint-sourced requests |
| CloudFormation drift detection is eventual | Drift detection job takes time; it doesn't block deployments of drifted stacks automatically |
