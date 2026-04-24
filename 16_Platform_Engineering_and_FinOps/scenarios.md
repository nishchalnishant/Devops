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

---

## Scenario 1: The "Unattached EBS" Cost Leak
**Symptom:** Your AWS bill shows $5,000 for EBS volumes, but you only have 10 instances.
**Diagnosis:** When EC2 instances are deleted, their EBS volumes are often left behind as "Available" (orphaned).
**Fix:** Use a script or tool (like CloudCustodian) to find and delete unattached EBS volumes.

## Scenario 2: Internal Developer Platform (IDP) "Click Moment"
**Symptom:** Developers are complaining that it takes 2 weeks to get a new S3 bucket.
**Diagnosis:** The process is manual and tickets-based.
**Fix:** Build a "Self-Service" portal using Backstage or a Terraform-based internal module that allows developers to provision standard resources via a simple YAML config.
