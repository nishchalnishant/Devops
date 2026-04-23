# Enterprise Landing Zones & Cloud Foundation (7 YOE)

Mid-level engineers deploy virtual machines to an existing VPC. Senior and Staff engineers design the **Landing Zone**—the macro-level framework that determines how an enterprise scales across hundreds of cloud accounts securely.

Whether using **AWS Control Tower** or the **Azure Cloud Adoption Framework (CAF)**, the underlying principles are identical.

---

## 1. The Multi-Account / Multi-Subscription Strategy

A single large cloud account is an unmanageable failure domain. If a compromised credential has "Owner" access to a single monolithic account, the attacker destroys production, staging, and billing data simultaneously.

### The Best Practice: One Workload = One Environment = One Account
Instead of segmenting by Resource Groups or VPCs, you segment by the highest level: the Cloud Account (AWS) or Subscription (Azure).

- **Billing Separation:** Chargebacks are trivial when HR Production uses Account A, and Marketing Production uses Account B.
- **Micro-Blast Radius:** A compromised credential in the Marketing Dev Account cannot view, edit, or delete resources in the HR Prod Account, regardless of how badly RBAC was misconfigured in Dev.
- **Quota Management:** Many cloud quotas (e.g., maximum number of load balancers) are per-account. Spreading workloads across accounts prevents noisy-neighbor quota exhaustion.

---

## 2. Organization Design & Vending Machines

When operating 50+ accounts, you cannot create them manually in the console.

### Management Groups (Azure) / OUs (AWS)
Accounts are grouped hierarchically to apply policies downward.
```text
Root
 ├── Infrastructure (Shared Services, Networking, Identity)
 ├── Security (Log Archive, SOC Tooling)
 ├── Workloads (The actual applications)
 │   ├── Dev
 │   └── Prod
 └── Sandboxes (Isolated developer playgrounds; internet access only)
```

### The Account Vending Machine (AVM)
An AVM is an automated Terraform/API pipeline that provisions a new ready-to-use cloud account within minutes.

**What an AVM does when triggered:**
1. Calls the Cloud Provider API to create a new underlying Account/Subscription.
2. Attaches the account to the correct Management Group / OU (e.g., Workloads/Dev).
3. Connects Identity: Maps Enterprise SSO (Entra ID / Okta) roles to the new account.
4. provisions networking (e.g., creates VPC and attaches it to the Transit Gateway).
5. Deploys mandatory guardrails (e.g., Sentinel/Checkov blocks internet gateways).

---

## 3. Network Topologies for Scale

### The Hub-and-Spoke Model
The most common enterprise architecture.

- **The Hub (Shared Services Account):** Contains the central egress firewall, ExpressRoute/DirectConnect to On-Premises, and central DNS resolvers. 
- **The Spokes (Workload Accounts):** Each spoke VPC contains the actual application infrastructure.
- **Routing:** Spokes *cannot* communicate with each other directly by default. All traffic traversing the cloud must route up to the Hub, through the central firewall, and back down to the destination Spoke.

### Cloud Native Networking Services
- **AWS Transit Gateway (TGW):** A central router that interconnects thousands of VPCs and on-premises networks. Replaces complex VPC Peering meshes.
- **Azure Virtual WAN (vWAN):** A networking service that brings networking, security, and routing functionalities together to provide a single operational interface.

---

## 4. Centralized Security and Governance

### Policy Enforcement Layer
Policies must be enforced at the organization root, overriding local account admin privileges.
- **AWS Service Control Policies (SCPs):** JSON rules assigned to an OU. E.g., An SCP preventing `ec2:RunInstances` without encrypted EBS volumes will stop the deployment, even if the user is the Root Admin of the child account.
- **Azure Policy:** Enforces compliance across Management Groups. E.g., Automatically deploys the Log Analytics agent to every new Virtual Machine.

### The Immutable Log Archive
Regulatory compliance requires tamper-proof audit trails.
- **Design:** CloudTrail (AWS) or Activity Logs (Azure) from all 50+ child accounts stream directly to a central, highly restricted `Security-Log-Archive` Account.
- **Immutability:** The central S3 bucket / Storage Account has WORM (Write-Once-Read-Many) lock enabled or immutability policies applied. Even a compromised Global Administrator cannot delete the logs to cover their tracks.
