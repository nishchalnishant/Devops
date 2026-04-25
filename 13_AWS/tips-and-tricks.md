# AWS Tips & Tricks

Production-tested AWS patterns, CLI one-liners, anti-patterns, and gotchas.

***

## IAM — The Most Important Service

### Use the IAM Policy Simulator before deploying
```bash
# Test if a role can perform an action
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::123456789:role/my-role \
  --action-names s3:PutObject \
  --resource-arns arn:aws:s3:::my-bucket/prefix/*

# Also available in the Console: IAM → Policy Simulator
```

### Check what permissions a role actually has (effective policies)
```bash
# List all policies attached to a role
aws iam list-attached-role-policies --role-name my-role

# List inline policies
aws iam list-role-policies --role-name my-role

# Show which policy grants a specific permission
# Use IAM Access Analyzer → Policy Validation in the Console
```

### Generate a least-privilege policy from CloudTrail
```bash
# IAM Access Analyzer generates a policy from actual API usage in CloudTrail
# Console: IAM → Access Analyzer → Generate Policy
# Specify a role + time range → get a policy with only the actions actually called

# This is the fastest way to right-size an over-permissioned role
```

### The DENY always wins — use it for guardrails
```json
{
  "Effect": "Deny",
  "Action": "*",
  "Resource": "*",
  "Condition": {
    "StringNotEquals": {
      "aws:RequestedRegion": ["us-east-1", "eu-west-1"]
    }
  }
}
```
Put this in an SCP or permission boundary — no IAM allow can override it.

***

## EC2 & Compute

### Find expensive unattached resources
```bash
# Unattached EBS volumes (costing money with no value)
aws ec2 describe-volumes \
  --filters "Name=status,Values=available" \
  --query 'Volumes[*].[VolumeId,Size,CreateTime]' \
  --output table

# Stopped instances (still paying for storage + ENI)
aws ec2 describe-instances \
  --filters "Name=instance-state-name,Values=stopped" \
  --query 'Reservations[*].Instances[*].[InstanceId,InstanceType,LaunchTime,Tags[?Key==`Name`].Value|[0]]' \
  --output table

# Unused Elastic IPs (charged when not attached)
aws ec2 describe-addresses \
  --query 'Addresses[?AssociationId==null].[PublicIp,AllocationId]' \
  --output table
```

### IMDSv2 — enforce it
```bash
# Require IMDSv2 token (blocks SSRF attacks from stealing EC2 metadata)
aws ec2 modify-instance-metadata-options \
  --instance-id i-abc123 \
  --http-tokens required \
  --http-endpoint enabled

# Enforce at account level via SCP:
# Deny ec2:RunInstances when aws:RequestTag/imdsv2 != required
```

### User data debugging
```bash
# View user data script that ran on the instance
aws ec2 describe-instance-attribute \
  --instance-id i-abc123 \
  --attribute userData \
  --query 'UserData.Value' --output text | base64 --decode

# View user data execution log on the instance
cat /var/log/cloud-init-output.log
```

***

## S3 — Security Patterns

### Check for public buckets across all regions
```bash
aws s3api list-buckets --query 'Buckets[*].Name' --output text | \
  tr '\t' '\n' | \
  while read bucket; do
    result=$(aws s3api get-bucket-acl --bucket "$bucket" \
      --query 'Grants[?Grantee.URI==`http://acs.amazonaws.com/groups/global/AllUsers`]' \
      --output text 2>/dev/null)
    [ -n "$result" ] && echo "PUBLIC: $bucket"
  done

# Better: Enable S3 Block Public Access at the account level (one-time)
aws s3control put-public-access-block \
  --account-id 123456789 \
  --public-access-block-configuration \
  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
```

### Enforce HTTPS-only access
```json
{
  "Effect": "Deny",
  "Principal": "*",
  "Action": "s3:*",
  "Resource": ["arn:aws:s3:::my-bucket", "arn:aws:s3:::my-bucket/*"],
  "Condition": {"Bool": {"aws:SecureTransport": "false"}}
}
```

### Lifecycle policy to control costs
```bash
aws s3api put-bucket-lifecycle-configuration \
  --bucket my-logs-bucket \
  --lifecycle-configuration '{
    "Rules": [{
      "ID": "log-retention",
      "Status": "Enabled",
      "Filter": {"Prefix": "logs/"},
      "Transitions": [
        {"Days": 30, "StorageClass": "STANDARD_IA"},
        {"Days": 90, "StorageClass": "GLACIER"}
      ],
      "Expiration": {"Days": 365}
    }]
  }'
```

***

## VPC & Networking

### Find which security group is blocking traffic
```bash
# Enable VPC Flow Logs first:
aws ec2 create-flow-logs \
  --resource-type VPC \
  --resource-ids vpc-abc123 \
  --traffic-type REJECT \
  --log-destination-type cloud-watch-logs \
  --log-group-name /aws/vpc/flowlogs

# Then query rejected traffic:
aws logs filter-log-events \
  --log-group-name /aws/vpc/flowlogs \
  --filter-pattern '[version, account, eni, source, destination, srcport, destport, protocol, packets, bytes, windowstart, windowend, action="REJECT", flowlogstatus]' \
  --query 'events[*].message' --output text | head -20
```

### Reachability Analyzer (GUI/API alternative to VPC Flow Logs)
```bash
# Tests network path between two resources — shows exactly where traffic is blocked
aws ec2 create-network-insights-path \
  --source i-source-instance \
  --destination i-destination-instance \
  --protocol TCP \
  --destination-port 443

aws ec2 start-network-insights-analysis \
  --network-insights-path-id nip-abc123

# Result: shows each hop and whether it's reachable
```

### NAT Gateway cost trap
**Problem:** NAT Gateway charges $0.045/GB of data processed + $0.045/hour. A single service streaming 10TB/month through NAT = **$450 in data processing alone**.

**Solutions:**
1. Use S3/DynamoDB VPC Endpoints — traffic to these services bypasses NAT Gateway (free!)
2. Use Interface VPC Endpoints for ECR, Secrets Manager, SSM — required in private subnets anyway
3. For public API calls: consider deploying a PrivateLink endpoint or using AWS Global Accelerator

```bash
# Create S3 gateway endpoint (free, reduces NAT costs significantly)
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-abc123 \
  --service-name com.amazonaws.us-east-1.s3 \
  --route-table-ids rtb-abc123
```

***

## EKS

### Get a token for a cluster (CI/CD)
```bash
aws eks update-kubeconfig --region us-east-1 --name my-cluster
# OR get a raw token (for tools that need it directly)
aws eks get-token --cluster-name my-cluster
```

### Check IRSA is configured correctly
```bash
# Verify OIDC provider is registered
aws eks describe-cluster --name my-cluster \
  --query 'cluster.identity.oidc.issuer' --output text

# Verify the OIDC provider exists in IAM
aws iam list-open-id-connect-providers

# Test a pod can get credentials
kubectl exec -it my-pod -- aws sts get-caller-identity
# Should show the IAM role ARN, not the node's role
```

### Common EKS cost mistakes
- **Fargate for every pod:** Fargate is 35% more expensive than EC2 for steady workloads. Use Fargate only for burst/isolation-requiring workloads.
- **Managed node groups always-on:** Use Karpenter instead — it scales to zero and selects optimal instance types.
- **Default node group in all AZs × 3:** Min size of 1 per AZ = 3 always-on nodes minimum. Set min to 0 where safe.

***

## CloudWatch & Cost

### Avoid CloudWatch Logs as the primary log store at scale
CloudWatch Logs costs ~$0.50/GB ingested + $0.03/GB stored. At 1TB/month ingestion = **$500/month just for ingestion**. Use:
- Fluent Bit → Loki on EC2 (10x cheaper)
- Firehose → S3 → Athena (pay per query, not per ingestion)
- Only ship ERROR+ logs to CloudWatch; DEBUG to S3

### CloudWatch metric filter — extract numeric metrics from logs
```bash
aws logs put-metric-filter \
  --log-group-name /app/api \
  --filter-name "5xx-errors" \
  --filter-pattern '[timestamp, requestId, level="ERROR", message, statusCode=5*]' \
  --metric-transformations \
    metricName=5xxErrors,metricNamespace=MyApp,metricValue=1
# Now you can alert on this custom metric without a separate instrumentation change
```

***

## CLI Productivity

### JMESPath — filter AWS CLI output efficiently
```bash
# Get only running instances with their names
aws ec2 describe-instances \
  --filters "Name=instance-state-name,Values=running" \
  --query 'Reservations[*].Instances[*].{
    ID: InstanceId,
    Type: InstanceType,
    Name: Tags[?Key==`Name`].Value|[0],
    IP: PrivateIpAddress
  }' \
  --output table

# Get all S3 buckets created after a date
aws s3api list-buckets \
  --query 'Buckets[?CreationDate>=`2024-01-01`].Name' \
  --output text
```

### AWS SSO + profiles
```bash
# ~/.aws/config
[profile prod]
sso_start_url = https://my-org.awsapps.com/start
sso_account_id = 123456789012
sso_role_name = DevOpsEngineer
region = us-east-1

# Login
aws sso login --profile prod

# Use
aws s3 ls --profile prod
AWS_PROFILE=prod terraform plan
```

### Assume role inline
```bash
# Assume a role and export credentials to shell
eval $(aws sts assume-role \
  --role-arn arn:aws:iam::123456789:role/prod-deploy \
  --role-session-name deploy-session \
  --query 'Credentials.[join(`=`,["AWS_ACCESS_KEY_ID", AccessKeyId]),
                         join(`=`,["AWS_SECRET_ACCESS_KEY", SecretAccessKey]),
                         join(`=`,["AWS_SESSION_TOKEN", SessionToken])]' \
  --output text | tr '\t' '\n' | sed 's/^/export /')
```
