# Production Scenarios & Troubleshooting Drills (Senior Level)

### Scenario 1: IAM Permission Boundary Issues
**Problem:** You gave a user `AdministratorAccess`, but they still can't create an IAM Role.
**Diagnosis:** Check for an **IAM Permission Boundary**. It acts as a "max ceiling" for permissions. If it's not allowed in the boundary, the user can't do it.

### Scenario 2: Cross-Account Role Access
**Problem:** App in Account-A needs to read an S3 bucket in Account-B.
**Fix:** Create a Role in Account-B with a **Trust Policy** allowing Account-A. The App in Account-A must then call `sts:AssumeRole`.

### Scenario 3: Transit Gateway Routing Complexity
**Problem:** You have 10 VPCs connected via TGW, but VPC-A can't talk to VPC-J.
**Diagnosis:** Check the **TGW Route Tables**. TGW is not transitive by default; you must explicitly associate and propagate routes between attachments.

***

## Scenario 1: S3 Bucket Policy "Lockout"
**Symptom:** Even the Admin user cannot access an S3 bucket.
**Diagnosis:** A `Deny` policy was applied to `*` principals without excluding the current user.
**Fix:** Log in as the AWS Root account (which bypasses IAM policies) to delete the restrictive policy.

## Scenario 2: EBS Volume "Stuck" in Attaching
**Symptom:** EC2 instance hangs on boot; EBS volume shows `Attaching` state forever.
**Diagnosis:** The kernel on the EC2 instance failed to mount the drive, or there is a mismatch between the Xen and Nitro hypervisor device names.
**Fix:** Force-detach the volume and re-attach. Check `dmesg` for disk errors.


### Scenario 3: IAM Role "Trust Policy" failure
**Symptom:** An EC2 instance cannot assume a role, even though it has the policy attached.
**Diagnosis:** The Role's **Trust Relationship** does not allow the `ec2.amazonaws.com` service to assume it.
**Fix:** Update the Trust Policy to include the EC2 service principal.

### Scenario 4: Lambda "Cold Start" Latency
**Symptom:** First request to a Java Lambda takes 10 seconds.
**Diagnosis:** JVM initialization and class loading overhead.
**Fix:** Use **Provisioned Concurrency** or switch to a lighter runtime like Go or Python.

***

## Scenario 5: EKS IRSA Token Not Working
**Symptom:** Pod logs show `AccessDenied` when calling S3, even though the IAM role has `s3:GetObject`. The pod has a service account annotation pointing to the role ARN.

**Diagnosis:**
```bash
# Check the service account annotation
kubectl get sa my-sa -n my-ns -o jsonpath='{.metadata.annotations}'
# Should show: eks.amazonaws.com/role-arn: arn:aws:iam::123456789:role/my-role

# Check the pod — it must use the annotated service account
kubectl get pod my-pod -n my-ns -o jsonpath='{.spec.serviceAccountName}'

# Check mounted token
kubectl exec my-pod -n my-ns -- ls /var/run/secrets/eks.amazonaws.com/serviceaccount/
# Should contain: token

# Decode and inspect the token audience
kubectl exec my-pod -n my-ns -- cat /var/run/secrets/eks.amazonaws.com/serviceaccount/token | \
  cut -d. -f2 | base64 -d 2>/dev/null | python3 -m json.tool
# aud must be: sts.amazonaws.com
# sub must match: system:serviceaccount:my-ns:my-sa

# Check OIDC provider association
aws eks describe-cluster --name my-cluster --query cluster.identity.oidc.issuer
# Verify it matches an OIDC provider in IAM
aws iam list-open-id-connect-providers
```

**Root Causes and Fixes:**

1. **OIDC provider not registered in IAM** — IRSA is a two-part setup: the cluster has an OIDC issuer, but you must also register it as a provider in IAM.
```bash
eksctl utils associate-iam-oidc-provider \
  --cluster my-cluster --region us-east-1 --approve
```

2. **Trust policy condition mismatch** — The role trust policy must reference the correct OIDC issuer URL and the exact `sub` claim.
```json
{
  "Effect": "Allow",
  "Principal": {
    "Federated": "arn:aws:iam::123456789:oidc-provider/oidc.eks.us-east-1.amazonaws.com/id/EXAMPLED539D4633E53DE1B71EXAMPLE"
  },
  "Action": "sts:AssumeRoleWithWebIdentity",
  "Condition": {
    "StringEquals": {
      "oidc.eks.us-east-1.amazonaws.com/id/EXAMPLED539D4633E53DE1B71EXAMPLE:aud": "sts.amazonaws.com",
      "oidc.eks.us-east-1.amazonaws.com/id/EXAMPLED539D4633E53DE1B71EXAMPLE:sub": "system:serviceaccount:my-ns:my-sa"
    }
  }
}
```

3. **Pod not using the annotated service account** — Check `spec.serviceAccountName` in the pod spec.

4. **aws-sdk version too old** — Older SDKs don't read the `AWS_WEB_IDENTITY_TOKEN_FILE` env var injected by the mutating webhook. Upgrade the SDK.

**Prevention:** Use `eksctl create iamserviceaccount` which handles the OIDC provider, IAM role trust policy, and SA annotation atomically.

***

## Scenario 6: VPC Endpoint Routing — S3 Traffic Still Leaving via NAT
**Symptom:** After adding an S3 Gateway Endpoint, NAT Gateway data-processing charges haven't dropped. CloudTrail shows S3 calls still originating from the NAT Gateway IP.

**Diagnosis:**
```bash
# Confirm the endpoint exists and is associated
aws ec2 describe-vpc-endpoints --filters Name=service-name,Values=com.amazonaws.us-east-1.s3

# Check route table associations — endpoint must be associated with ALL private subnets
aws ec2 describe-route-tables --filters Name=vpc-id,Values=vpc-abc123 \
  --query 'RouteTables[*].{ID:RouteTableId,Routes:Routes[?GatewayId!=null]}'

# Is the application using the right bucket region?
# S3 Gateway Endpoints are region-specific — cross-region calls still go to internet
```

**Root Causes and Fixes:**

1. **Endpoint not associated with the correct route table** — Gateway endpoints add a route prefix list entry (`pl-xxxxx`) to route tables. If a private subnet's route table is not associated, traffic bypasses the endpoint.
```bash
aws ec2 modify-vpc-endpoint \
  --vpc-endpoint-id vpce-xxxxxx \
  --add-route-table-ids rtb-private-a rtb-private-b rtb-private-c
```

2. **Cross-region S3 access** — Gateway endpoints only cover the same-region S3 service. Cross-region calls go to the internet. Use Interface Endpoints with PrivateLink for cross-region, or replicate data to same-region buckets.

3. **S3 bucket endpoint policy blocking the endpoint principal** — If the bucket has a policy with `aws:SourceVpce` condition, ensure the endpoint ID is listed.

4. **DNS resolution not routing through endpoint** — For Interface endpoints (not Gateway), `enableDnsSupport` must be true in the VPC, and private DNS names must be enabled on the endpoint.

**Prevention:** After creating any VPC endpoint, run a 30-minute after-check on NAT Gateway `BytesProcessed` metric to validate traffic shifted.

***

## Scenario 7: Multi-Account SCP Silently Blocking Deployments
**Symptom:** A CI pipeline in a child account runs `terraform apply` successfully (exit 0), but the resources are never created. CloudTrail shows the API calls were made but no `CreateBucket` event exists.

**Diagnosis:**
```bash
# Check CloudTrail for implicit deny events
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=EventName,AttributeValue=CreateBucket \
  --start-time 2024-01-01T10:00:00Z

# If the event is missing entirely, the SCP prevented the request before it hit the service
# Check SCPs attached to the account's OU
aws organizations list-policies-for-target \
  --target-id ou-xxxx-yyyyyyyy \
  --filter SERVICE_CONTROL_POLICY

# Simulate the permission (requires Organizations master account)
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::CHILD_ACCOUNT:role/terraform-role \
  --action-names s3:CreateBucket \
  --resource-arns "arn:aws:s3:::my-bucket" \
  --context-entries Key=aws:RequestedRegion,Type=string,Values=eu-west-1
```

**Root Causes and Fixes:**

1. **SCP denies the service or region** — Common org-wide policies deny all services except allowed regions. Terraform applies succeed because Terraform itself doesn't error — only the AWS API call is rejected silently.
```json
{
  "Effect": "Deny",
  "Action": "*",
  "Resource": "*",
  "Condition": {
    "StringNotEquals": {
      "aws:RequestedRegion": ["us-east-1", "us-west-2"]
    }
  }
}
```
Fix: Add `eu-west-1` to the approved regions list in the SCP, or deploy to an approved region.

2. **SCP attached at OU level, not account level** — Moving the account to a different OU resolves the conflict as a workaround, but the real fix is amending the SCP.

3. **SCP requires specific tag conditions** — Some organizations require resources to have a `CostCenter` tag on creation. S3 CreateBucket doesn't support tag-on-create in all SDKs — add `aws_s3_bucket_tag` as a separate resource and accept it's a two-step create.

**Prevention:** Add SCP simulation to the CI plan stage using `aws iam simulate-principal-policy` as a pre-flight check. Maintain an SCP test harness in the management account.

***

## Scenario 8: ECS Task Role Credentials Expiring Mid-Request
**Symptom:** Long-running ECS tasks (batch jobs) fail with `ExpiredTokenException` after 1-6 hours. The task IAM role is correct and works at startup.

**Diagnosis:**
```bash
# In the task, inspect the credential source
curl -s http://169.254.170.2$AWS_CONTAINER_CREDENTIALS_RELATIVE_URI | python3 -m json.tool
# Shows: Expiration field — STS tokens are valid for 6h max from ECS agent

# Check if the application is caching credentials beyond their TTL
# Look for boto3 session being created once at startup vs per-call
grep -r "boto3.Session()" src/ | grep -v "def "
```

**Root Causes and Fixes:**

1. **Application caches the boto3 session/client at startup** — AWS SDKs refresh credentials automatically if you don't serialize them. The bug is calling `.get_credentials()` and caching the raw key/secret/token instead of letting the SDK refresh.
```python
# Wrong — snapshots the short-lived token
session = boto3.Session()
creds = session.get_credentials().get_frozen_credentials()
ACCESS_KEY = creds.access_key  # cached forever

# Right — SDK refreshes automatically
s3_client = boto3.client('s3')  # create per-operation or use the session directly
```

2. **Custom credential provider bypasses ECS metadata endpoint** — If `AWS_ACCESS_KEY_ID` is set as a hardcoded env var, it takes precedence over the ECS task role credential chain. Remove the hardcoded env vars.

3. **Cross-account assume-role inside the task with a 1-hour TTL** — If the task role assumes another role, the assumed-role credentials expire in 1h. Use `DurationSeconds=43200` (12h max for roles without session policies) and re-assume before expiry.

**Prevention:** Test with a task that immediately calls `aws sts get-caller-identity` on a cron every 5 minutes for 8 hours in a staging environment. Alert on `ExpiredTokenException` in CloudWatch Logs Insights.

***

## Scenario 9: RDS IAM Authentication Failing in Production
**Symptom:** Application can connect to RDS with a static password but fails when switched to IAM authentication. Error: `PAM authentication failed for user "app_user"`.

**Diagnosis:**
```bash
# Confirm IAM auth is enabled on the RDS instance
aws rds describe-db-instances \
  --db-instance-identifier my-db \
  --query 'DBInstances[0].IAMDatabaseAuthenticationEnabled'

# Confirm the IAM policy allows rds-db:connect
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::123456789:role/app-role \
  --action-names rds-db:connect \
  --resource-arns "arn:aws:rds-db:us-east-1:123456789:dbuser:db-ABCD1234/app_user"

# Generate an auth token (expires in 15 minutes)
TOKEN=$(aws rds generate-db-auth-token \
  --hostname my-db.us-east-1.rds.amazonaws.com \
  --port 5432 \
  --region us-east-1 \
  --username app_user)

# Test connection directly
PGPASSWORD=$TOKEN psql -h my-db.us-east-1.rds.amazonaws.com \
  -U app_user -d mydb \
  --set=sslmode=require
```

**Root Causes and Fixes:**

1. **Database user not created with `rds_iam` role** — IAM auth requires the DB user to be created with the special role.
```sql
-- PostgreSQL
CREATE USER app_user;
GRANT rds_iam TO app_user;
```

2. **Token used without SSL** — RDS IAM auth tokens are only valid over SSL connections. The token is effectively an SSL certificate replacement. Ensure `sslmode=require` (or `verify-full` with the RDS CA cert).

3. **Clock skew** — Auth tokens are time-limited (15 min). If the EC2/ECS instance clock is skewed, tokens are rejected. Verify with `chronyc tracking`.

4. **Resource ARN in IAM policy uses wrong DB instance ID** — The resource ARN must use the `DbiResourceId` (not the DB identifier). Find it:
```bash
aws rds describe-db-instances --db-instance-identifier my-db \
  --query 'DBInstances[0].DbiResourceId'
# Use in IAM policy: arn:aws:rds-db:us-east-1:123456789:dbuser:db-ABCD1234/app_user
```

**Prevention:** Add `psql ... -c "SELECT 1"` with token generation to the ECS task health check. Set a CloudWatch alarm on RDS `FailedConnections` metric.

***

## Scenario 10: EKS Node Group Upgrade Leaves Nodes NotReady
**Symptom:** After upgrading the EKS managed node group from 1.28 to 1.29, several nodes enter `NotReady` state. Running pods are evicted, and some are stuck in `Terminating`.

**Diagnosis:**
```bash
# Check node conditions
kubectl describe node ip-10-0-1-50.us-east-1.compute.internal | grep -A10 Conditions

# Common: KubeletNotReady due to CNI plugin version mismatch
kubectl get pods -n kube-system -l k8s-app=aws-node

# Check VPC CNI version vs required version for k8s 1.29
kubectl describe daemonset aws-node -n kube-system | grep Image

# Check terminating pods
kubectl get pods -A --field-selector status.phase=Failed

# Force-delete only if the node is confirmed terminated
kubectl delete node ip-10-0-1-50.us-east-1.compute.internal
kubectl delete pod stuck-pod -n my-ns --grace-period=0 --force
```

**Root Causes and Fixes:**

1. **VPC CNI (aws-node) version incompatible with new kubelet** — EKS requires specific minimum VPC CNI versions per Kubernetes version. Upgrade before or during the node group upgrade.
```bash
# Check current version
kubectl describe daemonset aws-node -n kube-system | grep 602401143452.dkr.ecr

# Upgrade to latest recommended
kubectl apply -f https://raw.githubusercontent.com/aws/amazon-vpc-cni-k8s/v1.18.0/config/master/aws-k8s-cni.yaml
```

2. **Max unavailable too high causing thundering herd** — Default max unavailable for managed node groups is 1. If the group had a custom setting of 33%, nodes drain faster than pods can reschedule.
```bash
aws eks update-nodegroup-config \
  --cluster-name my-cluster \
  --nodegroup-name my-ng \
  --update-config maxUnavailable=1
```

3. **PodDisruptionBudget blocking drain** — If PDBs have `maxUnavailable: 0` or `minAvailable: 100%`, the node drain stalls. The upgrade waits, times out, and marks nodes `NotReady`.
```bash
kubectl get pdb -A
# Temporarily relax PDB for the upgrade, then restore
kubectl patch pdb my-pdb -n my-ns --type=json \
  -p='[{"op": "replace", "path": "/spec/maxUnavailable", "value": 1}]'
```

**Prevention:** Stage node group upgrades: upgrade one AZ at a time (`max_unavailable=1`). Run `kubectl get nodes` watch during the upgrade and set a CloudWatch alarm on `node_status_condition` metric for `NotReady`.

***

## Scenario 11: Lambda Concurrency Limit Causing API Gateway 502s
**Symptom:** During a traffic spike, API Gateway returns 502 errors. Lambda logs show `TooManyRequestsException`. The function has a 1000ms timeout and p99 is 200ms — so it's not timing out.

**Diagnosis:**
```bash
# Check account-level and function-level concurrency limits
aws lambda get-account-settings
# ConcurrentExecutions limit (default 1000 per account per region)

aws lambda get-function-concurrency --function-name my-function
# If not set, function uses the shared pool

# Check CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Throttles \
  --dimensions Name=FunctionName,Value=my-function \
  --start-time 2024-01-01T10:00:00Z \
  --end-time 2024-01-01T11:00:00Z \
  --period 60 --statistics Sum

# Check if other functions are consuming the pool
aws lambda list-functions --query 'Functions[*].{Name:FunctionName}' | xargs -I{} \
  aws lambda get-function-concurrency --function-name {}
```

**Root Causes and Fixes:**

1. **Account concurrency limit hit by multiple functions** — Default 1000 concurrent executions per region shared across all functions. A bursty function can starve others.
```bash
# Request a limit increase
aws service-quotas request-service-quota-increase \
  --service-code lambda \
  --quota-code L-B99A9384 \
  --desired-value 3000
```

2. **No reserved concurrency set** — Without reserved concurrency, a spike on one function starves others. Set reserved concurrency to guarantee capacity.
```bash
aws lambda put-function-concurrency \
  --function-name my-function \
  --reserved-concurrent-executions 500
```

3. **API Gateway integration timeout is 29s but Lambda hits concurrency before then** — Add SQS as a buffer between API Gateway and Lambda for workloads that can be async. Return `202 Accepted` immediately.

4. **Burst limit** — Lambda can burst to 3000 concurrent executions in the first minute, then adds 500/minute. If traffic spikes faster, throttles occur before the burst ceiling.

**Prevention:** Set `ReservedConcurrentExecutions` on critical functions. Use Provisioned Concurrency for latency-sensitive functions. Set CloudWatch alarm on `Throttles > 0` for production functions.
