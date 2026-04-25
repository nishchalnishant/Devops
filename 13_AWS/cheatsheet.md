# AWS Cheatsheet

Quick reference for AWS CLI commands, IAM, EC2, S3, EKS, and common patterns.

***

## AWS CLI Configuration

```bash
# Configure credentials
aws configure                              # Interactive setup
aws configure --profile prod               # Named profile
aws configure list                         # Show current config
aws configure list-profiles                # Show all profiles

# Use profile
aws s3 ls --profile prod
export AWS_PROFILE=prod                    # Set default for session

# Use IAM role (assume role)
aws sts assume-role \
  --role-arn arn:aws:iam::123456789:role/MyRole \
  --role-session-name my-session

# Verify identity
aws sts get-caller-identity
```

***

## IAM

```bash
# Users
aws iam list-users
aws iam create-user --user-name alice
aws iam delete-user --user-name alice
aws iam create-access-key --user-name alice
aws iam list-access-keys --user-name alice
aws iam delete-access-key --user-name alice --access-key-id AKIA...

# Groups
aws iam create-group --group-name developers
aws iam add-user-to-group --user-name alice --group-name developers
aws iam list-groups-for-user --user-name alice

# Roles
aws iam create-role --role-name MyRole --assume-role-policy-document file://trust.json
aws iam list-roles
aws iam get-role --role-name MyRole
aws iam attach-role-policy --role-name MyRole --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess

# Policies
aws iam list-policies --scope Local                     # Custom policies
aws iam get-policy --policy-arn arn:aws:iam::123:policy/MyPolicy
aws iam get-policy-version --policy-arn arn:... --version-id v1

# Simulate permissions
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::123:user/alice \
  --action-names s3:GetObject \
  --resource-arns arn:aws:s3:::my-bucket/*
```

***

## EC2

```bash
# Instances
aws ec2 describe-instances                                    # All instances
aws ec2 describe-instances --filters "Name=tag:env,Values=production"  # Filter
aws ec2 describe-instances --query 'Reservations[].Instances[].[InstanceId,State.Name,PublicIpAddress]' --output table

aws ec2 start-instances --instance-ids i-0abc123
aws ec2 stop-instances --instance-ids i-0abc123
aws ec2 terminate-instances --instance-ids i-0abc123
aws ec2 reboot-instances --instance-ids i-0abc123

# Launch instance
aws ec2 run-instances \
  --image-id ami-0abcdef1234567890 \
  --instance-type t3.micro \
  --key-name my-key \
  --security-group-ids sg-0abc123 \
  --subnet-id subnet-0abc123 \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=my-server},{Key=env,Value=prod}]'

# Key pairs
aws ec2 create-key-pair --key-name my-key --query 'KeyMaterial' --output text > my-key.pem
aws ec2 describe-key-pairs
aws ec2 delete-key-pair --key-name my-key

# Security Groups
aws ec2 describe-security-groups
aws ec2 create-security-group --group-name my-sg --description "My SG" --vpc-id vpc-0abc123
aws ec2 authorize-security-group-ingress \
  --group-id sg-0abc123 \
  --protocol tcp --port 443 --cidr 0.0.0.0/0

# AMIs
aws ec2 describe-images --owners self
aws ec2 create-image --instance-id i-0abc123 --name "my-ami-$(date +%F)"

# EBS Volumes
aws ec2 describe-volumes
aws ec2 describe-volumes --filters "Name=status,Values=available"     # Unattached (waste!)
aws ec2 create-volume --size 100 --volume-type gp3 --availability-zone us-east-1a
aws ec2 attach-volume --volume-id vol-0abc123 --instance-id i-0abc123 --device /dev/sdf
aws ec2 delete-volume --volume-id vol-0abc123

# Elastic IPs
aws ec2 describe-addresses
aws ec2 describe-addresses --query 'Addresses[?AssociationId==null]'  # Unattached (charged!)
aws ec2 allocate-address --domain vpc
aws ec2 release-address --allocation-id eipalloc-0abc123
```

***

## S3

```bash
# Bucket operations
aws s3 ls                                     # List buckets
aws s3 ls s3://my-bucket                      # List bucket contents
aws s3 ls s3://my-bucket/prefix/ --recursive  # List recursively
aws s3 mb s3://my-new-bucket --region us-east-1  # Create bucket
aws s3 rb s3://my-bucket --force              # Delete bucket + all contents

# Object operations
aws s3 cp file.txt s3://my-bucket/file.txt                # Upload
aws s3 cp s3://my-bucket/file.txt ./file.txt              # Download
aws s3 cp s3://my-bucket/ . --recursive                   # Download all
aws s3 mv s3://my-bucket/old.txt s3://my-bucket/new.txt   # Move/rename
aws s3 rm s3://my-bucket/file.txt                         # Delete
aws s3 rm s3://my-bucket/ --recursive                     # Delete all

# Sync (efficient for large sets)
aws s3 sync ./dist s3://my-bucket/                        # Upload directory
aws s3 sync s3://my-bucket/backup ./backup                # Download
aws s3 sync s3://source s3://dest                         # Bucket to bucket
aws s3 sync ./dist s3://my-bucket/ --delete               # Mirror (delete extras)
aws s3 sync ./dist s3://my-bucket/ --exclude "*.log"      # Exclude pattern

# Presigned URLs
aws s3 presign s3://my-bucket/file.txt --expires-in 3600  # 1-hour link

# Bucket policies
aws s3api get-bucket-policy --bucket my-bucket
aws s3api put-bucket-policy --bucket my-bucket --policy file://policy.json
aws s3api get-bucket-acl --bucket my-bucket
aws s3api put-bucket-versioning --bucket my-bucket \
  --versioning-configuration Status=Enabled

# Static website
aws s3 website s3://my-bucket --index-document index.html --error-document 404.html
```

***

## VPC & Networking

```bash
# VPCs
aws ec2 describe-vpcs
aws ec2 create-vpc --cidr-block 10.0.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=my-vpc}]'

# Subnets
aws ec2 describe-subnets --filters "Name=vpc-id,Values=vpc-0abc123"
aws ec2 create-subnet --vpc-id vpc-0abc123 --cidr-block 10.0.1.0/24 --availability-zone us-east-1a

# Route Tables
aws ec2 describe-route-tables
aws ec2 create-route-table --vpc-id vpc-0abc123
aws ec2 create-route --route-table-id rtb-0abc123 --destination-cidr-block 0.0.0.0/0 --gateway-id igw-0abc123
aws ec2 associate-route-table --route-table-id rtb-0abc123 --subnet-id subnet-0abc123

# Internet Gateways
aws ec2 create-internet-gateway
aws ec2 attach-internet-gateway --internet-gateway-id igw-0abc123 --vpc-id vpc-0abc123

# NAT Gateways
aws ec2 create-nat-gateway --subnet-id subnet-0abc123 --allocation-id eipalloc-0abc123

# VPC Endpoints
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-0abc123 \
  --service-name com.amazonaws.us-east-1.s3 \
  --route-table-ids rtb-0abc123
```

***

## EKS

```bash
# Clusters
aws eks list-clusters
aws eks describe-cluster --name my-cluster
aws eks create-cluster --name my-cluster --role-arn arn:... --resources-vpc-config subnetIds=...,securityGroupIds=...
aws eks delete-cluster --name my-cluster

# Update kubeconfig
aws eks update-kubeconfig --name my-cluster --region us-east-1
aws eks update-kubeconfig --name my-cluster --profile prod --alias my-cluster-prod

# Node Groups
aws eks list-nodegroups --cluster-name my-cluster
aws eks describe-nodegroup --cluster-name my-cluster --nodegroup-name my-nodegroup
aws eks create-nodegroup \
  --cluster-name my-cluster \
  --nodegroup-name app-nodes \
  --node-role arn:aws:iam::123:role/NodeRole \
  --subnets subnet-0abc subnet-0def \
  --instance-types t3.xlarge \
  --scaling-config minSize=2,maxSize=10,desiredSize=3

# Fargate Profiles
aws eks create-fargate-profile \
  --cluster-name my-cluster \
  --fargate-profile-name my-profile \
  --pod-execution-role-arn arn:... \
  --selectors namespace=production

# Add-ons
aws eks list-addons --cluster-name my-cluster
aws eks describe-addon --cluster-name my-cluster --addon-name vpc-cni
aws eks create-addon --cluster-name my-cluster --addon-name aws-ebs-csi-driver
```

***

## Lambda

```bash
# Functions
aws lambda list-functions
aws lambda get-function --function-name my-function
aws lambda invoke --function-name my-function --payload '{"key":"value"}' output.json
aws lambda invoke --function-name my-function --log-type Tail output.json | jq -r '.LogResult' | base64 -d

# Deploy
aws lambda update-function-code \
  --function-name my-function \
  --zip-file fileb://function.zip

aws lambda update-function-configuration \
  --function-name my-function \
  --timeout 30 \
  --memory-size 512 \
  --environment "Variables={DB_HOST=prod-db.internal}"

# Logs
aws logs tail /aws/lambda/my-function --follow
aws logs tail /aws/lambda/my-function --since 1h
```

***

## ECR — Container Registry

```bash
# Login
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com

# Repositories
aws ecr describe-repositories
aws ecr create-repository --repository-name my-app
aws ecr delete-repository --repository-name my-app --force

# Images
aws ecr list-images --repository-name my-app
aws ecr describe-images --repository-name my-app \
  --query 'imageDetails | sort_by(@, &imagePushedAt) | reverse(@)[:5]'

# Build, tag, push
docker build -t my-app:latest .
docker tag my-app:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/my-app:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/my-app:latest

# Image scanning
aws ecr start-image-scan --repository-name my-app --image-id imageTag=latest
aws ecr describe-image-scan-findings --repository-name my-app --image-id imageTag=latest
```

***

## Secrets Manager & SSM

```bash
# Secrets Manager
aws secretsmanager list-secrets
aws secretsmanager get-secret-value --secret-id prod/db/password
aws secretsmanager create-secret --name prod/db/password --secret-string '{"password":"abc123"}'
aws secretsmanager update-secret --secret-id prod/db/password --secret-string '{"password":"new123"}'
aws secretsmanager rotate-secret --secret-id prod/db/password

# SSM Parameter Store
aws ssm get-parameter --name /prod/db/password --with-decryption
aws ssm get-parameters-by-path --path /prod/ --with-decryption --recursive
aws ssm put-parameter --name /prod/db/password --value "abc123" --type SecureString --overwrite
aws ssm delete-parameter --name /prod/db/password

# SSM Session Manager (no SSH needed)
aws ssm start-session --target i-0abc123
aws ssm start-session --target i-0abc123 \
  --document-name AWS-StartPortForwardingSession \
  --parameters '{"portNumber":["5432"],"localPortNumber":["5432"]}'  # Port forward to RDS
```

***

## CloudWatch

```bash
# Logs
aws logs describe-log-groups
aws logs tail /var/log/myapp --follow
aws logs filter-log-events \
  --log-group-name /aws/lambda/my-fn \
  --filter-pattern "ERROR" \
  --start-time $(date -d '1 hour ago' +%s000)

# Metrics
aws cloudwatch list-metrics --namespace AWS/EC2
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=InstanceId,Value=i-0abc123 \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-01T01:00:00Z \
  --period 300 \
  --statistics Average

# Alarms
aws cloudwatch describe-alarms
aws cloudwatch put-metric-alarm \
  --alarm-name "High-CPU" \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --alarm-actions arn:aws:sns:us-east-1:123:my-topic
```

***

## Cost & Billing

```bash
# Cost Explorer (requires Cost Explorer enabled)
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-02-01 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=TAG,Key=team

# Budgets
aws budgets describe-budgets --account-id 123456789
aws budgets describe-budget-notifications --account-id 123456789 --budget-name my-budget

# Trusted Advisor
aws support describe-trusted-advisor-checks --language en
aws support describe-trusted-advisor-check-result --check-id Pfx0RwqBli --language en
```

***

## Useful Output Filters

```bash
# JMESPath query examples
aws ec2 describe-instances \
  --query 'Reservations[].Instances[].[InstanceId,InstanceType,State.Name,Tags[?Key==`Name`].Value|[0]]' \
  --output table

aws ec2 describe-volumes \
  --query 'Volumes[?State==`available`].[VolumeId,Size,CreateTime]' \
  --output table

# jq alternatives
aws iam list-roles --output json | jq -r '.Roles[] | select(.RoleName | contains("eks")) | .RoleName'
aws ec2 describe-instances --output json | jq -r '.Reservations[].Instances[] | select(.State.Name == "running") | .InstanceId'
```
