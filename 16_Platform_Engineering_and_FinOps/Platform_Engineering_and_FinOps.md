# Platform Engineering and FinOps (7 YOE)

If Senior Engineers build architectures, Staff and Lead Engineers build the platforms that enable other teams to build architectures.

This document bridges the gap between infrastructure automation and organizational scale. 

## 1. Platform Engineering & Internal Developer Platforms (IDPs)

DevOps was originally "You build it, you run it." However, forcing product developers to master Kubernetes, Terraform, Prometheus, and Helm led to massive cognitive load and reduced feature velocity.

- **Platform Engineering:** Treating your internal developers as your customers. Your product is the internal platform.
- **Internal Developer Platform (IDP):** A self-service portal (often built on tools like Backstage by Spotify). A developer logs in, clicks "Create New Go Microservice," and the platform automatically:
  1. Stamps out a Git repository from a template.
  2. Sets up a CI/CD pipeline.
  3. Provisions the Dev/Staging/Prod Kubernetes namespaces.
  4. Wraps the service in organizational required security tools (SonarQube, Trivy).
  5. Registers the service in the central service catalog.
- **Golden Paths (Paved Roads):** You don't force developers to use the IDP. You make the IDP so good, secure, and easy to use that they *want* to use it. If they leave the paved road to build their own bespoke Terraform, they assume full operational responsibility for it.

## 2. Platform Metrics (DORA and SPACE)

Platform Engineers do not guess if their platform is successful; they measure it.

### DORA Metrics
1. **Deployment Frequency:** How often does the organization deploy to production? (Goal: On Demand / Multiple times a day).
2. **Lead Time for Changes:** Time from commit to running in production. (Goal: Less than one hour).
3. **Change Failure Rate:** What percentage of deployments cause an incident? (Goal: 0-15%).
4. **Mean Time To Recovery (MTTR):** How quickly can we restore service? (Goal: Less than one hour).

### SPACE Framework
DORA only measures velocity and stability. SPACE measures holistic developer productivity:
- **S**atisfaction and well-being
- **P**erformance
- **A**ctivity
- **C**ommunication and collaboration
- **E**fficiency and flow

## 3. FinOps (Cloud Financial Management)

At 7 YOE, cost is an architectural dimension equivalent to latency or security. 

### The FinOps Lifecycle
1. **Inform:** Visibility and allocation. Tagging everything. Who spent what? (Showback and Chargeback models).
2. **Optimize:** Reducing waste and lowering rates.
3. **Operate:** Continuous improvement. Aligning engineering speeds with financial goals.

### Optimization Strategies Senior Engineers Must Know

#### Rate Optimization
- **Reserved Instances (RIs) / Savings Plans:** Committing to 1 or 3-year usage terms for up to 72% discounts.
- **Spot Instances / Preemptible VMs:** Bidding on spare cloud capacity for up to 90% discounts. Must be used for stateless, fault-tolerant workloads (batch processing, data workers, specific k8s node pools) paired with Spot Termination Handlers to drain pods before the node disappears.

#### Usage Optimization (Right-Sizing)
- **VPA (Vertical Pod Autoscaler):** Analyzing historical memory/CPU usage of pods to automatically recommend or enforce correct `requests` and `limits`. Constantly requesting 4GB of RAM but only using 200MB across 1,000 pods wastes millions of dollars.
- **Descheduling / Cluster Autoscaling:** Scaling the cluster down at night. If Dev and Staging environments aren't used on weekends, scale their replicasets to 0 and let the Cluster Autoscaler remove the underlying expensive VM nodes.
- **Storage Lifecycle Policies:** Moving logs from hot S3/Blob storage to Glacier/Cold storage after 30 days.

## 4. Organizational Governance (Policy-as-Code)

You cannot manually enforce rules across 1,500 engineers. Governance must be automated.

- **Checkov, OPA (Open Policy Agent), or Kyverno:** Analyzing Terraform plans or Kubernetes manifests *before* they are applied.
  - "Does this workload run as root?" -> REJECT.
  - "Does this S3 bucket have public read access?" -> REJECT.
- **Cloud Native Policies:** AWS Service Control Policies (SCPs) and Azure Policy dynamically block or audit resources that drift from compliance.

## 5. Site Reliability Engineering (SRE) Culture

- **Error Budgets:** If your SLO says 99.9% uptime, you have an error budget of 43 minutes of downtime per month. If you burn through that budget, *all feature feature deployments stop*. The team is legally bound to work on reliability until the month resets.
- **Blameless Post-Mortems:** When the database goes down, we do not ask "Why did Bob delete the table?" We ask "Why did the system allow a standard operator portage to delete a production table without a secondary approval lock?" Human error is a system failure.
