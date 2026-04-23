# Platform Engineering for CI/CD (7 YOE)

At the senior level, your job is not to build one pipeline. It is to build the **Platform** that thousands of developers use to build their *own* pipelines safely.

---

## 1. The Enterprise Pipeline Pattern

If you have 100 teams, you do not want 100 different `Jenkinsfile`s.

### Pattern: The "Template" Library
Develop a **Shared Library** (Jenkins) or **Reusable Workflows** (GitHub Actions) that defines the corporate "Golden Path" for builds.

- **Developer UI:** The developer uses a single-line YAML or Groovy call: `standardNodePipeline(name: 'my-app', team: 'finance')`.
- **Under the Hood:** The platform team's library automatically handles:
  1. Docker layer caching.
  2. Security scans (Trivy/SonarQube).
  3. Artifact signing (Cosign).
  4. Deployment to the correct Kubernetes cluster based on the `team` parameter.

---

## 2. Infrastructure as Code for CI/CD

Managing the Jenkins server or GitHub organization via the UI is an anti-pattern. 

### Jenkins Configuration as Code (JCasC)
Senior engineers manage Jenkins via YAML.
- **JCasC:** A single YAML file defines everything: plugins, credentials, nodes, and global security settings. If the Jenkins server dies, you can recreate an identical copy in 5 minutes by applying the YAML.

### GitHub Terraform Provider
Manage your GitHub Organization using Terraform.
- Automatic creation of repositories.
- Standardized branch protection rules (e.g., "Require 2 approvals", "Require signed commits").
- Mapping LDAP/Okta groups to GitHub Teams.

---

## 3. Scaling CI Agents at Scale

### Ephemeral Agents on Kubernetes
Running static "Worker Nodes" is expensive and unreliable.
- **Auto-provisioning:** Use the **Kubernetes Cloud Plugin** for Jenkins. When a job starts, Jenkins requests a new pod from the K8s API. The pod runs exactly one build and is instantly deleted when finished.
- **Binary Stability:** Every build runs in a clean, identical environment defined by a Docker image. No "it failed because the node had v12 of Node.js instead of v14" errors.

### Cost Optimization with Spot Instances
CI workloads are the perfect candidate for **Cloud Spot Instances** (AWS Spot / Azure Preemptible).
- Since CI jobs are naturally resumable/retriable, using Spot instances can reduce your monthly runner bill by 70-90%.

---

## 4. Sophisticated Secret Management

"Secrets in the CI logs" is the most common senior-level failure.

### Secrets Injection Patterns
1. **Never use Environment Variables for long-lived secrets:** If a script crashes and prints the environment, your secret is leaked.
2. **File Injection:** Mount the secret as a temporary file in `/tmp/` that is deleted immediately after the job finishes.
3. **Short-lived Credentials (OIDC):** For GitHub Actions or GitLab, use **Workload Identity Federation**. 
   - GitHub creates a short-lived OIDC token.
   - AWS/Azure trusts that token and grants the CI runner a 1-hour IAM role.
   - **Result:** You never store a permanent `AWS_SECRET_ACCESS_KEY` in GitHub. It's impossible to "steal" the secret because it expires in minutes.

---

## 5. Pipeline Observability & DORA Metrics

If you can't measure your pipelines, you can't improve them.
- **Build Durations:** Plotting the "Time to Build" over the last 90 days. If the trend is upwards, your platform is slowing down the company.
- **Pipeline Failure Rate:** Identifying "Flaky" stages.
- **Tracing CI:** Using OpenTelemetry (OTel) to trace a pipeline's execution. You can see exactly which shell script or test suite took 80% of the build time.
