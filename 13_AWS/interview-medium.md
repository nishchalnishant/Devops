---
description: Medium-difficulty interview questions for AWS IAM, networking, EKS, Lambda, and cost management.
---

## Medium

**13. What is IAM Policy Evaluation Logic and what happens when multiple policies conflict?**

AWS IAM evaluates policies in this order:
1. **Explicit Deny** — if any policy (identity-based, resource-based, SCP, permissions boundary) explicitly denies the action, it is denied. Period.
2. **Explicit Allow** — if no explicit deny, any explicit allow grants access.
3. **Implicit Deny (default)** — if there's neither an allow nor a deny, access is denied.

SCPs (Service Control Policies) act as a ceiling — even if an IAM policy grants access, an SCP that doesn't allow the action prevents it. Permissions boundaries work the same way: an identity cannot exceed its boundary even with an explicit allow.

**14. What is IRSA (IAM Roles for Service Accounts) in EKS?**

IRSA allows Kubernetes pods to assume IAM roles without needing to store access keys anywhere. It works via OIDC federation:

1. EKS exposes an OIDC provider URL.
2. AWS IAM is configured to trust that OIDC provider.
3. Each Kubernetes ServiceAccount is annotated with an IAM role ARN.
4. When a pod starts, the EKS token webhook injects a projected service account token into the pod.
5. The AWS SDK calls `sts:AssumeRoleWithWebIdentity` using this token to get temporary credentials.

The IAM role's trust policy restricts which namespace and service account name can assume it — preventing lateral movement between services.

**15. Explain VPC peering vs Transit Gateway. When do you use each?**

**VPC Peering:** Direct one-to-one connection between two VPCs. Traffic stays on the AWS backbone (no internet). Non-transitive — if VPC A is peered with VPC B, and B is peered with C, A cannot reach C. CIDR ranges must not overlap. Good for 2-5 VPCs.

**Transit Gateway (TGW):** A hub-and-spoke network transit hub that connects VPCs, VPNs, and Direct Connect. Fully transitive — A can reach C via the TGW. Supports thousands of VPCs. Supports inter-region peering. Required for large-scale multi-VPC architectures. More expensive but necessary for scale.

**16. What is AWS Systems Manager Session Manager and why is it preferred over SSH?**

Session Manager provides a browser or CLI-based shell to EC2 instances without opening inbound port 22. The SSM Agent running on the instance initiates an outbound connection to the Systems Manager service — no inbound firewall rules needed. Benefits: no SSH key management, full session logging to CloudWatch/S3, access controlled via IAM (not server-side authorized_keys), and works even in private subnets with no internet access (via VPC endpoints).

**17. What is AWS Lambda's execution model and what are cold start considerations?**

Lambda functions run in isolated microVMs (Firecracker). On first invocation (or after a period of inactivity), Lambda provisions a new execution environment — this initialization takes 100ms-1s+ depending on runtime and package size. This is a "cold start." Subsequent invocations reuse the warm environment.

Mitigations:
- Use Provisioned Concurrency to pre-warm N instances continuously (costs money).
- Use ARM64 (`graviton2`) architecture — faster cold starts and cheaper.
- Minimize deployment package size — `node` starts faster than `python` which is faster than JVM.
- Move global initializations outside the handler (DB connections, SDK clients) — they persist across warm invocations.

**18. What is the difference between ECS and EKS for container orchestration on AWS?**

| Aspect | ECS | EKS |
|:---|:---|:---|
| **Control plane** | AWS-managed, proprietary | AWS-managed Kubernetes |
| **Learning curve** | Lower | Higher (requires K8s knowledge) |
| **Lock-in** | AWS-specific | Portable (standard K8s) |
| **Networking** | awsvpc mode = one ENI per task | VPC CNI = one IP per pod |
| **Scheduling** | Task definitions, Services | Pods, Deployments |
| **Ecosystem** | AWS-only integrations | Full K8s ecosystem |
| **Cost** | Free control plane | $0.10/hr per cluster |

Choose ECS if: simple containerization, team is AWS-native, minimal K8s experience. Choose EKS if: need portability, using K8s ecosystem tools (Helm, Argo, Istio), or existing K8s expertise.

**19. What are AWS Service Control Policies (SCPs) and how are they different from IAM policies?**

SCPs are policies attached to AWS Organizations OUs or accounts that define the maximum permissions available. They don't grant permissions — they restrict what can be granted. Even account root users cannot exceed an SCP.

Common SCP use cases:
- Deny creation of resources outside specific regions: `"Condition": {"StringNotEquals": {"aws:RequestedRegion": ["us-east-1", "eu-west-1"]}}`
- Deny deletion of CloudTrail logs: `"Action": "cloudtrail:DeleteTrail", "Effect": "Deny"`
- Require tags on resource creation
- Prevent IAM modification by non-privileged roles

**20. What is AWS ALB vs NLB and when do you use each?**

**Application Load Balancer (ALB):** Layer 7 (HTTP/HTTPS). Content-based routing: route by URL path, HTTP header, query string, or host header. Supports WebSockets, gRPC, and HTTP/2. Terminates SSL. Required for Kubernetes Ingress-style routing.

**Network Load Balancer (NLB):** Layer 4 (TCP/UDP/TLS). Extremely low latency, static IP per AZ, preserves source IP. Handles millions of requests per second. Cannot route by HTTP content. Use NLB for: TCP/UDP protocols, static IPs for whitelisting, gaming, IoT, VPN endpoints, or when performance is critical.

**21. How does AWS Auto Scaling decide when to scale?**

Auto Scaling policies:
- **Target tracking (recommended):** Specify a target metric value (e.g., "keep CPU at 60%"). ASG automatically adds/removes instances to maintain the target.
- **Step scaling:** Define alarms at multiple thresholds with different scaling responses (e.g., +2 instances at 70%, +5 instances at 90%).
- **Scheduled scaling:** Scale at specific times (pre-scale for known traffic spikes).

Scale-in protection: mark specific instances as protected to prevent scale-in (useful for instances doing long-running jobs). Cooldown period prevents scaling too rapidly — default 300 seconds between scale events.
