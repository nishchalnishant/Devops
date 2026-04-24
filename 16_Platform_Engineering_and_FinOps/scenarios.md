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
