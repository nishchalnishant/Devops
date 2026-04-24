## Hard

**15. How do you design a highly available Jenkins controller?**

1. **Controller HA:** Run Jenkins controller in Kubernetes on a PersistentVolume (EBS/Azure Disk) — if the Pod dies, Kubernetes reschedules it on another node and remounts the volume. Use a readiness probe.
2. **Agent architecture:** Use ephemeral Kubernetes agents via the Jenkins Kubernetes Plugin — agents are created per job and destroyed after completion. No idle cost, clean environment per build.
3. **Backup:** Schedule regular backups of the Jenkins home directory (`jobs/`, `credentials.xml`, `plugins/`) to object storage. Test restores monthly.
4. **JCasC:** Store all configuration in Git. If the controller is lost, provision a new one, install plugins, and apply JCasC YAML — fully reproduced in minutes.

**16. How do you migrate 100 Jenkins pipelines to GitLab CI?**

A big-bang migration is too risky. Phased approach:

1. **Categorize:** Group the 100 pipelines by complexity and pattern. Identify 5-10 representative pilots.
2. **Pilot:** Convert pilots to `.gitlab-ci.yml`. Create GitLab CI `include:` templates replicating Jenkins Shared Library functions.
3. **Document:** Write upgrade guides and run workshops.
4. **Phased rollout:** Onboard teams in waves, simplest pipelines first. New projects start on GitLab CI.
5. **Decommission:** Archive Jenkins data, shut down servers after all pipelines are migrated.

**17. How do you design dynamic, on-demand Jenkins agents on Kubernetes?**

1. Install the Jenkins Kubernetes Plugin and configure it with the cluster endpoint and credentials.
2. Define Pod templates in Jenkins (or JCasC YAML) specifying the agent container image, resource requests/limits, volumes, and workspace.
3. When a pipeline job is triggered, the plugin creates a new Pod in Kubernetes matching the Pod template. The agent container connects back to the Jenkins controller and runs the job.
4. After the job completes, the plugin deletes the Pod — zero idle agent cost, fresh environment per build.
5. Scale: with 50 concurrent jobs, 50 Pods are created simultaneously. The Kubernetes scheduler distributes them across nodes.

**18. What are the risks of using the `local-exec` and `remote-exec` provisioners in a Jenkins-triggered Terraform pipeline?**

- **Not idempotent:** Re-running `terraform apply` re-runs the script, which may have unintended side effects.
- **Untracked state:** Actions performed by scripts are not in Terraform state — Terraform doesn't know about them.
- **Tight coupling:** Pipeline behavior depends on the script's side effects, not infrastructure declarations.

Alternatives: Packer for golden image baking, Ansible for post-provisioning configuration, or Cloud-Init user data for startup scripts. Keep Terraform declarative — provision infrastructure, not configuration.
# Jenkins — Easy Interview Questions

---

**1. What is Jenkins and what problem does it solve?**

Jenkins is an open-source automation server written in Java. It solves the problem of manual, error-prone software delivery by automating every step from code commit to production deployment. Jenkins watches a version control system, triggers a pipeline on changes, runs tests, builds artifacts, and deploys — without human intervention.

Key facts:
- Open-source, self-hosted (contrast with GitHub Actions or GitLab CI which are SaaS/integrated)
- ~1,800 plugins making it integrable with almost any tool
- Runs on JVM; requires Java 17 or 21

---

**2. What is a Jenkinsfile?**

A Jenkinsfile is a text file committed to the root of a source repository that defines the CI/CD pipeline. It follows Pipeline as Code — the pipeline definition is versioned alongside the application code, enabling code review, history, and rollback of pipeline changes.

```groovy
// Minimal Jenkinsfile
pipeline {
    agent any
    stages {
        stage('Build') {
            steps { sh 'make build' }
        }
        stage('Test') {
            steps { sh 'make test' }
        }
    }
}
```

---

**3. What is the difference between a Declarative and a Scripted pipeline?**

| Aspect | Declarative | Scripted |
|--------|-------------|---------|
| Syntax | Structured `pipeline {}` block | Free-form Groovy `node {}` |
| Validation | Schema-validated before running | Fails at runtime |
| Learning curve | Low — beginner-friendly | Higher — requires Groovy knowledge |
| Flexibility | Limited by DSL structure | Full Groovy expressiveness |
| `post` block | Built-in | Manual try/catch/finally |
| Recommended for | Most pipelines | Complex dynamic logic only |

```groovy
// Declarative
pipeline {
    agent any
    stages {
        stage('Build') { steps { sh 'make build' } }
    }
}

// Scripted equivalent
node {
    stage('Build') { sh 'make build' }
}
```

---

**4. What are Jenkins agents and why are they used?**

Agents (also called nodes or workers) are machines that execute build steps on behalf of the Jenkins controller. The controller distributes work to agents instead of running builds itself — this is the controller/agent (master/worker) architecture.

**Reasons to use agents:**
- **Scale:** 20 agents = 20 concurrent builds
- **Isolation:** Each agent runs builds independently; a crashed agent doesn't affect the controller
- **Specialization:** GPU agents for ML, Windows agents for .NET, macOS agents for iOS
- **Clean environments:** Ephemeral agents (Kubernetes pods, Docker containers) get a fresh environment per build

Types: permanent agents (physical/VM), Docker agents, Kubernetes pod agents.

---

**5. What is a Jenkins Shared Library?**

A Shared Library is a collection of reusable Groovy code — steps, utilities, and pipeline templates — stored in a separate Git repository and imported by Jenkinsfiles across projects. It applies the DRY (Don't Repeat Yourself) principle to pipeline code.

```groovy
// Import in Jenkinsfile
@Library('company-lib@v2.1.0') _

// Call a global variable defined in vars/buildAndPush.groovy
buildAndPush(name: 'my-service', registry: 'registry.example.com')
```

---

**6. What is a `stage` in a Jenkins pipeline?**

A `stage` is a named logical division of the pipeline — e.g., Build, Test, Deploy. It groups related `steps` together. Stages appear as columns in the Jenkins pipeline visualization (Blue Ocean / Pipeline Graph View), making it easy to see where a build failed.

```groovy
stages {
    stage('Build')  { steps { sh 'mvn package' } }
    stage('Test')   { steps { sh 'mvn test' } }
    stage('Deploy') { steps { sh './deploy.sh' } }
}
```

---

**7. What is the `post` block used for?**

The `post` block defines steps that run after the pipeline (or stage) completes, conditional on the build result:

```groovy
post {
    always  { cleanWs() }                   // Always runs — cleanup
    success { slackSend message: 'Passed' } // Only on green
    failure { emailext to: 'team@company.com', subject: 'Build failed' }
    changed { echo 'Status changed from last build' }
}
```

It ensures cleanup and notifications happen regardless of the build outcome.

---

**8. How do you trigger a Jenkins pipeline automatically on a code push?**

Configure a webhook in the SCM platform (GitHub, GitLab, Bitbucket) pointing to `https://jenkins.example.com/github-webhook/`. When a push occurs, the SCM calls Jenkins, which triggers the matching job.

Jenkins job configuration:
- Enable **"GitHub hook trigger for GITScm polling"** (GitHub)
- Enable **"Build when a change is pushed to GitLab"** (GitLab plugin)

Alternative: `pollSCM('H/5 * * * *')` polls the SCM every 5 minutes. Less efficient than webhooks but works without network access from SCM to Jenkins.

---

**9. What build triggers are available in Jenkins?**

| Trigger | Description |
|---------|-------------|
| SCM webhook | Immediate — SCM calls Jenkins on push |
| `pollSCM` | Periodic polling of SCM for changes |
| `cron` | Schedule-based (e.g., nightly builds) |
| Upstream job | Trigger when another job succeeds |
| Manual (`Build Now`) | User-initiated via UI or API |
| `workflow_dispatch` equivalent | `input` step for human gate |
| Gerrit/GitHub PR event | Trigger on pull request open/update |

---

**10. How do you pass parameters to a Jenkins pipeline?**

Declare parameters in the `parameters` block. They appear as form fields when "Build with Parameters" is used:

```groovy
parameters {
    string(name: 'TARGET_ENV', defaultValue: 'staging')
    booleanParam(name: 'SKIP_TESTS', defaultValue: false)
    choice(name: 'LOG_LEVEL', choices: ['INFO', 'DEBUG', 'WARN'])
}

// Access in steps:
sh "deploy.sh --env=${params.TARGET_ENV}"
```

Via API:
```bash
curl -X POST 'https://jenkins.example.com/job/my-job/buildWithParameters' \
  --data 'TARGET_ENV=production&SKIP_TESTS=false'
```

---

**11. What are Jenkins artifacts and how do you archive them?**

Artifacts are files produced by a build (JARs, WARs, Docker images, test reports) that Jenkins stores and makes available for download from the build page.

```groovy
post {
    always {
        archiveArtifacts artifacts: 'build/**/*.jar', fingerprint: true
        archiveArtifacts artifacts: 'reports/**/*.html', allowEmptyArchive: true
    }
}
```

`fingerprint: true` enables artifact tracking across jobs — you can see which jobs consumed a given artifact. For long-term storage, push artifacts to Nexus, Artifactory, or S3 — Jenkins artifact storage is not designed for large binaries.

---

**12. What is the Jenkins workspace?**

The workspace is the local directory on the agent where Jenkins checks out the source code and runs build steps. Default location: `$JENKINS_HOME/workspace/<job-name>` on permanent agents, or a temporary directory on ephemeral agents.

```groovy
stage('Build') {
    steps {
        echo "Workspace is: ${env.WORKSPACE}"
        sh 'ls -la'                    // Lists workspace contents
        dir('subdirectory') {
            sh 'make build'            // Run in subdirectory
        }
    }
}
```

`cleanWs()` in the `post` block deletes the workspace after the build — important for disk management on permanent agents.

---

**13. What important built-in environment variables does Jenkins provide?**

| Variable | Value |
|----------|-------|
| `BUILD_NUMBER` | Incrementing build integer |
| `BUILD_URL` | Full URL: `https://jenkins.example.com/job/my-job/42/` |
| `JOB_NAME` | Job path: `team-a/my-service` |
| `WORKSPACE` | Absolute path of the workspace directory |
| `BRANCH_NAME` | Git branch (multibranch pipelines only) |
| `GIT_COMMIT` | Full SHA of the checked-out commit |
| `NODE_NAME` | Name of the agent running the build |

```groovy
sh "docker build -t myapp:${env.GIT_COMMIT[0..7]} ."
echo "Build URL: ${env.BUILD_URL}"
```

---

**14. How do you implement a manual approval gate in a Jenkins pipeline?**

Use the `input` step to pause the pipeline until an authorized user approves:

```groovy
stage('Deploy to Production') {
    steps {
        input(
            message: 'Deploy v${params.VERSION} to production?',
            ok: 'Deploy',
            submitter: 'release-team,ops-leads',    // Only these users/groups can approve
            parameters: [
                choice(name: 'STRATEGY', choices: ['rolling', 'blue-green'])
            ]
        )
        sh './deploy.sh production'
    }
}
```

The pipeline holds an executor slot while waiting. To avoid wasting executors on long-waiting approvals, use a `milestone` and an `input` step outside of agent blocks.

---

**15. What does `disableConcurrentBuilds()` do and when should you use it?**

`disableConcurrentBuilds()` prevents multiple builds of the same job from running simultaneously. Use it for:

- **Deployment pipelines:** Two deploys running at the same time causes race conditions
- **Integration tests:** Tests that use a shared database or staging environment
- **Release pipelines:** Never release the same service twice simultaneously

```groovy
options {
    disableConcurrentBuilds(abortPrevious: true)  // Cancel in-progress build when new one starts
}
```

Without `abortPrevious: true`, the new build queues behind the running one. With it, the running build is cancelled immediately — useful for PR pipelines where only the latest commit matters.

---

**16. What is `pollSCM` and how does it differ from a webhook?**

`pollSCM` is a cron-like schedule that instructs Jenkins to periodically check the SCM for new commits:

```groovy
triggers {
    pollSCM('H/5 * * * *')   // Check every ~5 minutes (H spreads load)
}
```

| Aspect | pollSCM | Webhook |
|--------|---------|---------|
| Latency | Up to 5 min delay | Near-instant |
| Network | Jenkins polls outbound | SCM calls Jenkins inbound |
| Setup | None (just cron expression) | Requires SCM webhook config |
| Reliability | Works even without SCM network access to Jenkins | Requires network path from SCM to Jenkins |

Prefer webhooks for immediate feedback; use `pollSCM` as a fallback or in air-gapped environments.
# DevOps Interview Playbook

Use this file as the main answer framework for DevOps, SRE, platform, and cloud-operations interviews.

## What Interviewers Are Really Testing

### 1. Fundamentals

You should be able to explain how Linux, networking, cloud, CI/CD, containers, and observability fit together. Interviewers usually care less about memorizing a command and more about whether you know when and why to use it.

### 2. Systems Thinking

A strong DevOps engineer thinks in dependencies and blast radius:

- What changed recently?
- Which component is actually failing?
- Which downstream system is causing the symptom?
- What is the fastest safe mitigation?

### 3. Troubleshooting Depth

Good candidates do not jump to a favorite root cause. They narrow the problem with evidence:

- Metrics to understand impact and timing
- Logs and events to find failing components
- Commands to validate a hypothesis
- A rollback or mitigation if the system is still unhealthy

### 4. Automation Mindset

Interviewers look for engineers who reduce manual work. Repeated tasks should turn into scripts, pipelines, modules, templates, dashboards, or runbooks.

### 5. Communication

A senior answer is structured. It explains:

1. What I would check first
2. Why I am checking it
3. What outcome I expect
4. How I would mitigate the issue
5. What I would change long term

## A Strong Answer Framework

Use this structure for most technical questions and incident scenarios:

1. Clarify the symptom and impact.
2. Check whether there was a recent deployment or configuration change.
3. Start with user-facing signals: latency, errors, availability, saturation.
4. Narrow the failing layer: app, container, node, network, database, cloud service, or pipeline.
5. Run the smallest commands that can confirm or reject a hypothesis.
6. Stabilize first, then optimize, then document the long-term fix.

Example:

> I would first confirm scope and timing in Grafana, then check recent deployment history, then inspect pod events and logs. If the service is actively failing, I would prepare a rollback while I validate whether the issue is config, image, dependency, or resource pressure.

## What You Should Know By Topic

### Git And Collaboration

- Branching, pull requests, merge vs rebase, revert vs reset
- How to recover from a bad merge or bad release
- Protected branches, code review, signed commits, secret scanning

### Linux And Shell

- Processes, signals, file permissions, systemd, logs, disk and memory inspection
- Safe shell scripting with `set -euo pipefail`, exit codes, functions, logging, and cron or timers
- How to debug a host that is slow, full, swapping, or refusing connections

### Networking

- TCP vs UDP, DNS, CIDR, routing, NAT, TLS, load balancing
- Connection refused vs timeout
- Basic packet and socket inspection with `ss`, `curl`, `dig`, `tcpdump`, `traceroute`, or `mtr`

### Cloud

- Compute, storage, networking, IAM/RBAC, autoscaling, HA, backups, DR
- Public vs private subnets
- Managed service trade-offs versus self-hosted platforms

### CI/CD

- Build, test, scan, package, publish, deploy, verify, rollback
- Artifact immutability and promotion
- Secrets handling, approval gates, canary or blue-green, smoke tests

### Docker And Kubernetes

- Dockerfile best practices, image layers, registries, networking, volumes
- Pods, Deployments, StatefulSets, Services, Ingress, probes, HPA
- Common failures: CrashLoopBackOff, ImagePullBackOff, Pending, OOMKilled, DNS issues

### Terraform And Ansible

- Providers, modules, state, backends, locking, outputs, drift, `for_each`
- Why Terraform provisions and Ansible configures
- Safe rollout patterns for infrastructure changes

### Observability And SRE

- Metrics, logs, traces
- Four Golden Signals
- SLI, SLO, error budget, alert fatigue
- How to turn symptoms into dashboards and actionable alerts

### Security

- Secrets management, least privilege, image scanning, dependency scanning, SBOMs
- Policy as code, signed artifacts, protected environments, admission controls

## Must-Know Commands

### Git

- `git status`
- `git log --oneline --graph --decorate`
- `git diff`
- `git revert <commit>`
- `git fetch --all --prune`

### Linux

- `top` or `htop`
- `ps aux`
- `journalctl -u <service>`
- `systemctl status <service>`
- `df -h`
- `free -m`
- `ss -tulpn`
- `lsof -i`

### Networking

- `curl -v`
- `dig <name>`
- `nslookup <name>`
- `ip addr`
- `ip route`
- `traceroute <host>` or `mtr <host>`
- `tcpdump -i <iface> port <port>`

### Docker

- `docker ps`
- `docker logs <container>`
- `docker exec -it <container> sh`
- `docker inspect <container>`
- `docker stats`

### Kubernetes

- `kubectl get pods -A`
- `kubectl describe pod <name>`
- `kubectl logs <pod> --previous`
- `kubectl get events --sort-by=.lastTimestamp`
- `kubectl top pod`
- `kubectl get svc,ingress,endpoints`
- `kubectl rollout status deployment/<name>`
- `kubectl describe node <name>`

### Terraform And Ansible

- `terraform init`
- `terraform plan`
- `terraform show`
- `terraform state list`
- `terraform force-unlock <lock-id>`
- `ansible -m ping all`
- `ansible-playbook site.yml --check`

## High-Value Scenarios To Practice

### CrashLoopBackOff

Mention:

- `kubectl describe pod`
- `kubectl logs --previous`
- config and secret validation
- entrypoint failure
- OOM or bad probes
- rollout undo if user impact is active

### ImagePullBackOff

Mention:

- bad image tag
- registry auth or `imagePullSecrets`
- private registry availability
- node egress or DNS problems

### Pending Or FailedScheduling

Mention:

- requests and limits
- taints and tolerations
- node selectors and affinity
- PVC zone binding or storage class issues

### High Latency Even After Scaling

Mention:

- CPU throttling
- connection pool exhaustion
- downstream dependency limits
- DNS latency
- kernel or node bottlenecks such as conntrack

### Terraform Wants To Recreate A Critical Resource

Mention:

- stop before `apply`
- inspect `plan` and changed attributes
- check `ForceNew` behavior and drift
- review state, module changes, and imports
- use `prevent_destroy` for critical resources

### Monitoring Shows No Data

Mention:

- target discovery
- `/metrics` reachability
- exporter health
- service monitor or scrape config
- network policy or label mismatch

## Design Trade-Offs You Should Be Ready To Explain

- Merge vs rebase
- Rolling vs blue-green vs canary deployments
- Deployment vs StatefulSet
- HPA vs VPA
- Terraform module reuse vs environment isolation
- L4 vs L7 load balancer
- Managed Kubernetes vs self-managed cluster
- Prometheus pull model vs push model
- Mutable servers vs immutable infrastructure

## Strong Signals In Senior Answers

- You lead with impact, not guesswork.
- You talk about rollback and mitigation before perfect root cause.
- You call out trade-offs instead of pretending every tool is always the best choice.
- You mention validation after the fix.
- You explain how to prevent recurrence with automation, guardrails, or observability.

## Common Weak Signals

- Jumping straight to one tool or one favorite command
- Saying "restart everything" as the first step
- Confusing symptoms with root causes
- Ignoring rollback, change history, or user impact
- Treating monitoring as CPU and memory graphs only

## Behavioral Interview Preparation

Prepare short stories for these themes:

- A production incident you helped mitigate
- A repetitive manual task you automated
- A pipeline or deployment you improved
- A security or compliance control you introduced
- A disagreement you resolved with developers, QA, or security
- A time you reduced MTTR, cost, failure rate, or deployment time

Use the STAR format, but keep it technical:

- Situation: what was failing or slow
- Task: what you owned
- Action: what you changed, automated, or investigated
- Result: measurable improvement

## Final Revision Checklist

- I can explain the path of a user request from browser to backend and database.
- I can describe how I would debug a broken deployment in Kubernetes.
- I can explain Git rollback options without confusing `reset` and `revert`.
- I can discuss Terraform state, backends, locking, and drift clearly.
- I can explain probes, Services, Ingress, HPA, and common pod failure states.
- I can describe CI/CD safety controls such as artifact immutability, approvals, and rollback.
- I can explain metrics, logs, traces, SLOs, and alert fatigue.
- I can talk through at least two real troubleshooting stories from my own work.

---

## Related Resources

- [Easy Interview Questions](interview-questions-easy.md)
- [Medium Interview Questions](interview-questions-medium.md)
- [Hard Interview Questions](interview-questions-hard.md)
- [General Interview Questions](general-interview-questions.md)
- [Azure DevOps Interview Playbook](azure-devops-interview-playbook.md)
- [Azure Scenario Drills](azure-scenario-based-drills.md)
- [Kubernetes Runbook](../05_Observability_and_Troubleshooting/Troubleshooting/kubernetes-runbook.md)
- [Senior DevOps Learning Path](../06_Advanced_DevOps_and_Architecture/Learning_Path/README.md)
