# 7. CICD Pipelines

The CI/CD (Continuous Integration / Continuous Deployment) stage is the "engine room" of DevOps. It automates the transition of code from a developer's machine to the production environment, ensuring speed, reliability, and security.

***

### 7. CI/CD Pipelines

This section covers the most popular tools used to automate the software delivery lifecycle.

#### A. Jenkins

Jenkins is the industry standard for open-source automation servers. It is highly flexible and relies on a massive plugin ecosystem.

* Declarative Pipelines: The modern way to write "Pipeline as Code." It uses a structured syntax (inside a `Jenkinsfile`) that is easier to read and allows for pre-execution syntax checking.
* Shared Libraries: Reusable code blocks stored in a separate Git repository. This allows you to define a standard build process once and share it across hundreds of different projects (DRY principle).
* Tools & Plugins: Jenkins can integrate with almost anything (Docker, Slack, SonarQube, AWS) via its 1,800+ plugins.
* Agents (Nodes): To handle high workloads, Jenkins uses a "Controller-Agent" architecture. The Controller manages the UI/logic, while "Agents" (separate servers) do the actual heavy lifting of building and testing code.
* Email Alerts: Automated notifications that inform the team immediately if a build fails, preventing "broken" code from sitting in the repository.

#### B. GitLab

GitLab is an "all-in-one" platform that includes everything from code hosting to security and deployment.

* GitLab CI Pipelines: Managed via a `.gitlab-ci.yml` file. It is native to the platform, meaning you don't need to set up a separate server like Jenkins.
* Self-hosted Runners: Small agent programs you install on your own servers to run GitLab CI jobs. This gives you full control over the build environment and can save costs compared to using cloud-hosted runners.

#### C. GitHub

GitHub has evolved from a simple code hosting site into a powerful automation platform.

* Repositories & SCM: The "Source of Truth" for your code and version history.
* GitHub Actions: A built-in automation engine that allows you to create workflows triggered by events (like a code push, a pull request, or a specific schedule). It uses a huge "Marketplace" of pre-built actions.
* Webhooks: A way for GitHub to "call" other services. For example, when code is pushed, a Webhook can tell a chat app to send a message or trigger an external deployment tool.

#### D. ArgoCD (The GitOps Approach)

ArgoCD is a specialized Continuous Delivery (CD) tool designed specifically for Kubernetes.

* GitOps: A practice where Git is the single source of truth for your infrastructure. If you want to change something in your cluster, you change the code in Git, and ArgoCD makes it happen.
* K8s Deployments: ArgoCD uses a "Pull-based" model. It constantly monitors your Git repo and "pulls" changes into the Kubernetes cluster if they don't match.
* ArgoCD CLI & Workflows: Allows engineers to manage applications, trigger manual syncs, and visualize the "health" of their Kubernetes resources through a powerful dashboard.



This is Section 7: CI/CD Pipelines. For a mid-to-senior DevOps/SRE, CI/CD is the "heart" of the operation. At this level, it’s not just about getting code from A to B; it’s about Supply Chain Security, Deployment Strategies, and Developer Experience (DevEx).

You are expected to build pipelines that are not only fast but also resilient and secure.

***

#### 🔹 1. Improved Notes: The Continuous Delivery Engine

**The CI/CD Philosophy**

* Continuous Integration (CI): Developers merge code frequently. The focus is on automated testing (Unit, Integration) and building immutable artifacts (Docker images). If the build fails, the pipeline stops.
* Continuous Delivery (CD): The artifact is automatically deployed to staging/testing environments, but the final push to Production requires a human "approval" gate.
* Continuous Deployment: Every change that passes the automated tests is deployed to Production automatically. This requires extremely high confidence in your test suite.

**Key Advanced Concepts**

* Build Once, Deploy Everywhere: Never rebuild an image for different environments. Build it once in CI, tag it, and promote that _exact same_ image through Staging to Production. This ensures what you tested is what you deployed.
* Shift-Left Security: Integrating security scans into the pipeline early.
  * SAST (Static Application Security Testing): Scans code for vulnerabilities (e.g., SonarQube).
  * SCA (Software Composition Analysis): Scans dependencies/libraries for known CVEs (e.g., Snyk, Trivy).
* Artifact Management: Using registries (JFrog Artifactory, AWS ECR) to version and store your builds with metadata/provenance.

***

#### 🔹 2. Interview View (Q\&A)

Q1: What is the difference between Blue/Green and Canary deployments?

* Answer: \* Blue/Green: You have two identical environments. You deploy the new version (Green) while the old (Blue) is still live. Once tested, you flip the traffic (usually via Load Balancer). It’s fast but doubles infrastructure costs.
  * Canary: You deploy the new version to a small subset of users (e.g., 5%). You monitor health metrics. If successful, you gradually rollout to 100%. It’s safer for detecting performance regressions under real load.

Q2: How do you handle a "Flaky Test" in a CI pipeline?

* Answer: Flaky tests (tests that pass/fail inconsistently) erode trust in the pipeline. An SRE approach is to:
  1. Quarantine the test (don't let it fail the build).
  2. Use a "Retries" mechanism (max 2-3 times) as a temporary fix.
  3. Analyze logs/traces to fix the underlying race condition or environment dependency.

Q3: Explain "GitOps" and how it differs from traditional CI/CD.

* Answer: In traditional CI/CD, the CI tool "pushes" changes to the cluster. In GitOps (e.g., ArgoCD), a controller inside the cluster "pulls" changes from Git. Git becomes the Single Source of Truth. If someone manually changes a setting in the cluster, GitOps automatically reverts it back to what is defined in Git (Self-healing).

***

#### 🔹 3. Architecture & Design: Deployment Strategies

SRE Trade-off: Speed vs. Safety

* Optimizing Build Speed: Use Layer Caching in Docker and Parallel Job Execution. A pipeline taking >15 minutes is a bottleneck for developers.
* Ensuring Safety: Implement Automated Rollbacks. If the 5xx error rate spikes or latency increases after a deployment, the pipeline should automatically revert to the last known "Good" version.

***

#### 🔹 4. Commands & Configs (The Pipeline Logic)

**GitHub Actions Example (The Modern Standard)**

Focusing on security and caching.

YAML

```
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      # Use caching to speed up builds
      - name: Cache dependencies
        uses: actions/cache@v3
        with:
          path: ~/.npm
          key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}

      # Security Scan
      - name: Run Snyk to check for vulnerabilities
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}

      # Build and Push with specific tag (No :latest)
      - name: Build and push
        run: |
          docker build -t my-app:${{ github.sha }} .
          docker push my-app:${{ github.sha }}
```

***

#### 🔹 5. Troubleshooting & Debugging

Scenario: The pipeline succeeded, but the application is returning 500 errors in Production.

1. Check Artifact Integrity: Was the correct image tag deployed? (Check the K8s deployment spec vs. the CI logs).
2. Environment Variables: Did a secret or config change in Prod but not in Staging? (Check ConfigMaps/Secrets).
3. Database Migration: Did the pipeline run the DB migration? If the code changed but the schema didn't, the app will fail.
4. Networking/Firewall: Is the new version trying to hit a new internal service that hasn't had its Security Group updated?

Scenario: Jenkins/GitHub Runner is stuck.

1. Resource Exhaustion: Is the runner out of disk space (Docker images piling up)?
2. Zombie Processes: Is a previous test run still hanging in the background?
3. Docker Socket: If using "Docker-in-Docker," is the socket correctly mounted?

***

#### 🔹 6. Production Best Practices

* Immutable Tagging: Never use `latest`. Use Git SHAs or Semantic Versioning (v1.2.3).
* Secrets Management: Never store passwords in the pipeline YAML. Use Environment Secrets (GitHub) or pull from Vault at runtime.
* Pre-Deployment Testing: Run "Smoke Tests" (basic health checks) immediately after deployment before clearing the old version.
* Anti-Pattern: "The Mega-Pipeline": Avoid putting everything in one giant script. Use modular, reusable templates (GitHub Action Composed Actions or Jenkins Shared Libraries).
* Supply Chain Security: Generate an SBOM (Software Bill of Materials) for every build so you know exactly what is inside your container.

***

#### 🔹 Cheat Sheet / Quick Revision

| **Concept**    | **Key SRE Detail**                                           |
| -------------- | ------------------------------------------------------------ |
| Artifact       | Must be immutable (Build once).                              |
| Pipeline State | Should be stateless; use caches for speed.                   |
| Rollback       | Should be faster than the deployment itself.                 |
| Webhook        | The trigger mechanism from Git to CI.                        |
| Approval Gate  | A manual check before hitting sensitive environments.        |
| Promotion      | The process of moving an artifact from Dev -> Stage -> Prod. |

***

This is Section 7: CI/CD Pipelines. In a modern DevOps environment, the pipeline is the "assembly line" of software. For a senior role, the focus shifts from simply "making the build pass" to security, speed, and reliability of the release process.

***

#### 🟢 Easy: Core Concepts & Definitions

_Focus: Understanding the purpose and basic flow of a pipeline._

1. What is the fundamental difference between Continuous Delivery and Continuous Deployment?
   * _Context:_ Focus on the manual vs. automated "Production" gate.
2. What is a "Build Artifact" and why should you store it in a Registry (like Docker Hub or Nexus)?
   * _Context:_ Explain why we don't just use the source code for every environment.
3. What is a "Webhook" in the context of Git and CI/CD?
   * _Context:_ How does the CI tool (Jenkins/GitHub Actions) know when a developer has pushed code?
4. Why are automated Unit Tests a mandatory part of any CI pipeline?
   * _Context:_ Catching bugs as early as possible (Shift-Left).

***

#### 🟡 Medium: Deployment Strategies & Optimization

_Focus: How we release code and make the process faster._

1. Explain the "Rolling Update" strategy in Kubernetes. What happens if a new version is buggy?
   * _Context:_ Discuss how K8s replaces old pods with new ones and how `maxUnavailable` and `maxSurge` control the flow.
2. Compare Blue-Green Deployment and Canary Deployment. When would you choose one over the other?
   * _Context:_ Blue-Green is all-or-nothing; Canary is a gradual traffic shift.
3. How do you handle secrets (API keys, DB passwords) in a CI/CD pipeline without hardcoding them?
   * _Context:_ Mention Jenkins Credentials, GitHub Actions Secrets, or HashiCorp Vault.
4. What are "Self-Hosted Runners" (or Jenkins Agents), and why would a company use them instead of managed runners?
   * _Context:_ Security, VPC access, and cost for large build jobs.

***

#### 🔴 Hard: Advanced Engineering & DevSecOps

_Focus: Scale, security, and GitOps._

1. What is "GitOps," and how does it change the traditional CI/CD "Push" model to a "Pull" model?
   * _Context:_ The interviewer is looking for mention of tools like ArgoCD or Flux and the concept of Git as the single source of truth.
2. Explain "Pipeline as Code." How do Shared Libraries (in Jenkins) or Composite Actions (in GitHub) help manage 100+ microservice pipelines?
   * _Context:_ Avoiding "Copy-Paste" pipelines; maintaining a single standard across the organization.
3. How do you integrate Security into a CI/CD pipeline (DevSecOps)?
   * _Context:_ Mention SAST (Static Analysis), SCA (Dependency Scanning for CVEs), and DAST (Dynamic Analysis).
4. Scenario: Your build time has increased from 5 minutes to 30 minutes. What steps would you take to optimize the pipeline?
   * _Context:_ Discuss Docker Layer Caching, Parallel testing, shallow clones (`git clone --depth 1`), and optimizing the size of the base image.
5. What is a "Semantic Versioning" (SemVer), and how can you automate it in a pipeline?
   * _Context:_ Using Git tags and automated release notes based on commit messages (e.g., conventional commits).

***

***

#### 💡 Pro-Tip for your Interview

When discussing CI/CD, always emphasize "Immutability."

* The SRE Answer: "The most important principle I follow is Build Once, Deploy Everywhere. I build the Docker image in the CI stage, scan it, and tag it with the Git SHA. That _exact same binary_ is then promoted through Staging to Production. This eliminates the 'it worked in dev but not in prod' problem caused by environment differences."

---

## 🔷 Advanced Version Control & CI/CD (7 YOE)

For Senior and Staff positions, the focus shifts from "writing a pipeline" to **building a Software Delivery Platform**. You are evaluated on your ability to scale delivery across hundreds of teams securely.

**Continue your preparation with these advanced architectural modules:**

1. `[NEW]` [Advanced Git Workflows & Monorepos](../Git_GitHub/advanced-git-workflows-and-monorepos.md): Trunk-Based Development, Monorepo scaling (Bazel), and Git internals (`git filter-repo`, `reflog`).
2. `[NEW]` [Platform Engineering for CI/CD](./platform-engineering-for-cicd.md): Jenkins as Code (JCasC), Shared Library templates, ephemeral Kubernetes agents, and OIDC secret injection.
3. `[NEW]` [Progressive Delivery & GitOps at Scale](../ArgoCD/progressive-delivery-and-gitops-at-scale.md): Multi-cluster ArgoCD (ApplicationSets), Automated Canary deployments (Argo Rollouts), and External Secrets Operator (ESO).
4. `[NEW]` [Supply Chain Security & SLSA](../DevSecOps/supply-chain-security-and-slsa.md): Achieving SLSA Level 3, generating/scanning SBOMs, and cryptographic image signing with Cosign.
