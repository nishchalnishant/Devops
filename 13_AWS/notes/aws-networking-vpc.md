---
description: AWS VPC networking internals, subnets, routing, security groups, NACLs, and connectivity patterns for senior engineers.
---

# AWS — Networking & VPC Deep Dive

## VPC Architecture

A VPC is a logically isolated network within AWS. Understanding its internals is essential for debugging connectivity issues.

```
AWS Region: us-east-1
└── VPC: 10.0.0.0/16
    ├── AZ: us-east-1a
    │   ├── Public Subnet: 10.0.1.0/24   ← Has route to Internet Gateway
    │   └── Private Subnet: 10.0.2.0/24  ← Has route to NAT Gateway
    ├── AZ: us-east-1b
    │   ├── Public Subnet: 10.0.3.0/24
    │   └── Private Subnet: 10.0.4.0/24
    │
    ├── Internet Gateway (IGW)            ← Allows public internet access
    ├── NAT Gateway (in public subnet)    ← Allows private → internet egress only
    ├── Route Tables                      ← Define packet routing rules
    └── VPC Endpoints                     ← Private access to AWS services
```

***

## Route Tables — The Traffic Director

Every subnet is associated with exactly one Route Table. AWS evaluates routes from most-specific to least-specific (Longest Prefix Match).

### Public Subnet Route Table

| Destination | Target | Meaning |
|:---|:---|:---|
| `10.0.0.0/16` | `local` | All VPC traffic stays internal |
| `0.0.0.0/0` | `igw-xxxxxxxx` | All other traffic → Internet Gateway |

### Private Subnet Route Table

| Destination | Target | Meaning |
|:---|:---|:---|
| `10.0.0.0/16` | `local` | VPC-internal traffic |
| `0.0.0.0/0` | `nat-xxxxxxxx` | Outbound-only internet via NAT |

### VPN/Direct Connect Route Table

| Destination | Target | Meaning |
|:---|:---|:---|
| `10.0.0.0/16` | `local` | VPC traffic |
| `192.168.0.0/16` | `vgw-xxxxxxxx` | On-premises traffic via Virtual Private Gateway |
| `0.0.0.0/0` | `nat-xxxxxxxx` | Internet traffic |

***

## Security Groups vs. NACLs

| | Security Groups | Network ACLs |
|:---|:---|:---|
| **Level** | Instance level (ENI) | Subnet level |
| **State** | Stateful (return traffic auto-allowed) | Stateless (must allow inbound AND outbound) |
| **Rules** | Allow only | Allow + Deny |
| **Evaluation** | All rules evaluated | Rules evaluated in order (lowest number first) |
| **Default** | Deny all inbound, allow all outbound | Allow all traffic |

**Senior Insight:** Security groups are almost always sufficient. NACLs are for blunt-force network-level blocking (e.g., block a specific IP range after a DDoS attack).

***

## VPC Connectivity Patterns

### VPC Peering

```
VPC-A (10.0.0.0/16) ←──── Peering ────→ VPC-B (172.16.0.0/16)
```

- **Non-transitive:** If A peers B and B peers C, A cannot reach C.
- Requires updating route tables on BOTH sides.
- **Cost:** Data transfer across AZs charged; same-AZ free.

### AWS Transit Gateway (TGW)

```
VPC-A ──┐
VPC-B ──┤── Transit Gateway ──── On-Premises VPN
VPC-C ──┘
```

- **Transitive routing**: A can reach C through TGW.
- Scales to thousands of VPCs.
- Acts as a cloud router with its own route tables.

### VPC Endpoints

```
EC2 Instance (private subnet)
        │
        │  No IGW or NAT required!
        ▼
    S3 Gateway Endpoint (free)       ← For S3 and DynamoDB only
    SSM Interface Endpoint ($0.01/hr) ← For all other AWS services
```

- **Gateway Endpoints:** S3 and DynamoDB. Free. Added to route table.
- **Interface Endpoints (PrivateLink):** All other AWS services. Creates an ENI in your subnet. Costs money but allows completely private communication.

***

## IP Address Planning for Enterprise

```
10.0.0.0/8    ← Reserved for enterprise (RFC 1918)

Hierarchy:
  10.0.0.0/8       ← All of company
  10.{region}.0.0/16  ← One per AWS region
  10.1.{az}.0/24   ← One per AZ per purpose

Example:
  10.1.0.0/16   ← us-east-1 Production VPC
    10.1.1.0/24 ← us-east-1a Public
    10.1.2.0/24 ← us-east-1a Private
    10.1.3.0/24 ← us-east-1b Public
    10.1.4.0/24 ← us-east-1b Private
  
  10.2.0.0/16   ← us-west-2 Production VPC
  10.3.0.0/16   ← eu-west-1 Production VPC
  10.100.0.0/16 ← Staging
  10.200.0.0/16 ← Development
```

***

## Logic & Trickiness Table

| Concept | Common Mistake | Senior Understanding |
|:---|:---|:---|
| **Subnet "public"** | "It has a public IP" | It has a route to IGW AND `map_public_ip_on_launch=true` |
| **NAT Gateway HA** | One NAT for all AZs (saves $) | One NAT per AZ; cross-AZ NAT traffic costs money and adds latency |
| **Security Groups** | Over-permissive CIDR ranges | Reference SGs by ID, not CIDR, for internal service-to-service rules |
| **NACLs** | Complex rules in NACLs | Use SGs; NACLs only for subnet-level emergency blocks |
| **VPC Peering scale** | Peer everything | Use Transit Gateway when more than 5 VPCs need to communicate |
| **DNS** | Default VPC DNS works | Enable `enableDnsSupport` and `enableDnsHostnames` for private hosted zones |
