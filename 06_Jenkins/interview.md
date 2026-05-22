# Jenkins — Interview Prep

```
Jenkins Interview — Easy
├── Core Concepts
│   ├── Q1 — What is Jenkins / CI/CD automation server
│   ├── Q2 — Jenkinsfile: Pipeline as Code in Git
│   └── Q3 — Declarative vs Scripted pipeline comparison
├── Agents & Architecture
│   ├── Q4 — Agents: physical, VM, Docker, K8s pod
│   ├── Q9 — Controller vs Agent separation (why controller never builds)
│   └── Q10 — agent any vs agent none vs label vs docker
├── Pipeline Structure
│   ├── Q6 — stage: logical phases (Build/Test/Deploy)
│   ├── Q7 — post block: always/success/failure/unstable/changed
│   ├── Q12 — parameters: string/boolean/choice/password/file
│   ├── Q13 — environment block: global vs stage-scoped vars
│   └── Q15 — disableConcurrentBuilds: deployment race prevention
├── Triggers & Execution
│   ├── Q8 — Webhook vs pollSCM trigger
│   ├── Q16 — pollSCM vs webhook: latency/network trade-offs
│   └── Build triggers: webhook, cron, upstream, manual, API
├── Shared Libraries
│   └── Q5 — vars/, src/, resources/ — DRY pipeline code
├── Multibranch Pipelines
│   └── Q11 — auto-creates job per branch with Jenkinsfile
├── Artifacts & Workspace
│   ├── Q11 — artifacts: archiveArtifacts, fingerprint
│   ├── Q12 — workspace: $JENKINS_HOME/workspace, cleanWs()
│   └── Q13 — built-in env vars: BUILD_NUMBER, GIT_COMMIT, NODE_NAME
├── Manual Gates
│   └── Q14 — input() step: submitter, parameters, milestone
└── Plugins & UI
    ├── Q14 — Blue Ocean: visual pipeline UI
    └── Q15 — Plugin ecosystem: JPI/HPI, Plugin Manager
```

### First Principles

- Jenkins exists because manual builds are slow and error-prone. The core problem is: code changes constantly, validation must happen on every change, humans cannot do it reliably at that frequency.
- The controller/agent split exists because builds are CPU/memory-intensive and untrusted. The controller is the "brain" — it must stay healthy. Agents are expendable workers.
- Declarative syntax is preferred because machines should validate pipelines before running them. Schema validation catches typos and missing blocks before a build starts.
- Shared Libraries exist because DRY applies to pipelines too. A deploy step written in 50 Jenkinsfiles creates 50 places to update when the deploy process changes.
- Webhooks are strictly better than pollSCM: polling wastes network calls and introduces latency. Webhooks push the event immediately.

## Easy

**1. What is Jenkins and what is it used for?**

Jenkins is an open-source automation server used to implement CI/CD pipelines. It builds, tests, and deploys code automatically when changes are pushed to a version control system.

**2. What is a Jenkinsfile?**

A Jenkinsfile is a text file, committed to source control, that defines a Jenkins pipeline in either Declarative or Scripted syntax.

**3. What is the difference between Declarative and Scripted pipelines in Jenkins?**

Declarative pipelines use a structured, validated YAML-like syntax with predefined blocks (`pipeline`, `stages`, `steps`). Scripted pipelines use a Groovy DSL with full programming flexibility. Declarative is preferred for most use cases due to readability and validation.

**4. What are Jenkins agents?**

Agents are machines (or containers) that execute pipeline stages. The Jenkins controller distributes work to agents. Agents can be physical machines, VMs, Docker containers, or Kubernetes Pods.

**5. What is a Jenkins Shared Library?**

A Shared Library is a collection of reusable Groovy code (steps, utilities, pipeline templates) stored in a Git repository and imported by Jenkinsfiles across multiple projects.

**6. What is a `stage` in Jenkins?**

A `stage` groups related `steps` together and represents a logical phase of the pipeline (e.g., Build, Test, Deploy). Stages are displayed as columns in the Jenkins Blue Ocean UI.

**7. What is the `post` block in a Declarative pipeline?**

The `post` block defines steps that run after the pipeline or a stage completes, based on the result: `always`, `success`, `failure`, `unstable`, `changed`. Used for notifications and cleanup.

**8. How do you trigger a Jenkins pipeline automatically on a code push?**

Configure a webhook in the SCM (GitHub, GitLab, Bitbucket) to notify Jenkins when a push occurs. In Jenkins, enable "GitHub hook trigger for GITScm polling" or the GitLab/Bitbucket equivalent on the pipeline job.

***


**9. What is the difference between a Jenkins controller and a Jenkins agent?**

The controller (formerly "master") manages the Jenkins UI, job scheduling, plugin management, and build history. It does not run build steps directly — it delegates to agents. Agents are ephemeral or persistent workers that execute pipeline stages. The controller should never execute builds to protect it from resource exhaustion and security exposure.

**10. What does `agent any` mean in a Declarative pipeline?**

It tells Jenkins to run the pipeline on any available agent. Alternatives: `agent none` (no global agent; each stage defines its own), `agent { label 'linux' }` (target agents with a specific label), `agent { docker { image 'node:20' } }` (run inside a Docker container on the agent).

**11. What is a Jenkins multibranch pipeline?**

A multibranch pipeline automatically creates a pipeline job for each branch in a repository that contains a Jenkinsfile. When a branch is created, a job is created; when a branch is deleted, the job is deleted. Used for feature branch CI without manual job creation.

**12. How do you pass parameters to a Jenkins pipeline?**

Declare them in the `parameters` block:

```groovy
parameters {
  string(name: 'ENV', defaultValue: 'staging', description: 'Target environment')
  booleanParam(name: 'SKIP_TESTS', defaultValue: false)
  choice(name: 'REGION', choices: ['us-east-1', 'eu-west-1'])
}
```

Access via `params.ENV` in pipeline steps. Parameters appear as input fields when triggering a build manually.

**13. What is the `environment` block in a Declarative pipeline?**

It sets environment variables available to all steps in that scope:

```groovy
environment {
  IMAGE_NAME = "myapp:${BUILD_NUMBER}"
  AWS_REGION = 'us-east-1'
}
```

Variables defined at `pipeline` level are global; those inside a `stage` are scoped to that stage. Use `credentials()` helper inside `environment` to bind credentials as env vars.

**14. What is Blue Ocean in Jenkins?**

Blue Ocean is a Jenkins UI plugin that provides a visual, modern interface for pipeline visualization. It shows pipeline stages as a graph, highlights failures inline, and makes branch/PR builds easier to navigate. It's largely superseded by the built-in Pipeline UI improvements in Jenkins LTS but is still widely used.

**15. How do Jenkins plugins work?**

Jenkins is plugin-driven — almost every capability (Git integration, Docker, Kubernetes, Slack notifications) is a plugin installed via the Plugin Manager. Plugins are JPI/HPI files. They extend Jenkins extension points (builders, SCM connectors, triggers, etc.). Plugin updates should be tested in staging before applying to production controllers because plugins can introduce breaking changes.

**16. What build triggers are available in Jenkins?**

- **SCM polling**: Jenkins checks VCS at a cron interval (`H/5 * * * *`)  
- **Webhook**: SCM pushes to Jenkins via HTTP (preferred — no polling delay)  
- **Cron schedule**: `triggers { cron('H 2 * * 1-5') }` for nightly builds  
- **Upstream job**: trigger when another job completes successfully  
- **Manual**: user clicks "Build Now"  
- **API trigger**: `curl -X POST http://jenkins/job/<name>/build`

### System Design Perspective

**Pipeline scalability:**
- Scaling Jenkins means adding agents. The controller is not the throughput bottleneck — executor slots are. Each agent provides N executors (threads). 10 agents × 2 executors = 20 concurrent builds.
- Multibranch pipelines auto-create jobs per branch. At scale (100+ branches), this means 100+ jobs in queue simultaneously. Agent auto-scaling (K8s pod agents, EC2 Fleet) is required — static agents will be permanently saturated.

**Agent/runner architecture trade-offs:**
- `agent any` is fine for getting started. In production it causes builds to land on random agents with different tool versions — non-deterministic failures. Label agents by capability (`java17`, `docker`, `gpu`) and target explicitly.
- Ephemeral K8s pod agents give a clean environment per build. The trade-off is ~15-30 second pod startup overhead. For fast feedback loops on PR pipelines, this matters.

**Failure recovery:**
- The Jenkins controller holds all build history and configuration. Without backup, a controller failure loses everything. Back up `JENKINS_HOME` to S3 daily. JCasC lets you reconstruct the controller from scratch in minutes.
- A build that hangs without a `timeout()` holds an executor slot forever. Every hung build reduces available capacity. Always add `timeout(time: 30, unit: 'MINUTES')` in pipeline `options{}`.

**Caching strategies:**
- Ephemeral agents don't cache anything between builds. Maven re-downloads all dependencies on every build unless you mount a shared dependency cache PVC or use a Nexus/Artifactory proxy that caches upstream artifacts.
- Docker layer cache is lost on ephemeral agents. Use BuildKit registry cache (`--cache-to`, `--cache-from`) to persist layers in a registry between builds.

**Security boundaries:**
- The controller must have zero executors. Any code running on the controller can read `credentials.xml` and `master.key` — the entire secrets store. Agents are expendable; the controller is not.
- Secrets injected via `withCredentials` are masked in logs but not in artifacts. Never write secrets to files that are archived or stashed.

```
Jenkins Interview — Medium
├── Controller Configuration
│   ├── Q9 — JCasC: YAML-based controller config in Git, reproducible
│   └── Q16 — JCasC vs Job DSL: controller config vs job/pipeline creation
├── Credentials & Secrets
│   ├── Q10 — withCredentials: usernamePassword, string, sshUserPrivateKey
│   ├── Q10 — Vault/AWS Secrets Manager integration for dynamic creds
│   └── Q19 — Preventing secrets in logs: mask, withCredentials, no echo
├── Parallel Execution
│   └── Q11 — parallel{}: unit/integration/lint simultaneously
├── Artifact Management
│   ├── Q12 — stash/unstash: pass files between agents
│   └── Q13 — Artifact promotion: build once, promote via crane/skopeo
├── Dynamic Agents
│   └── Q15 — K8s plugin: Pod per build, clean isolation, JCasC config
├── Pipeline Flow Control
│   ├── Q14 — input() step: manual approval with submitter restriction
│   ├── Q17 — retry(n), timeout(), exponential backoff with sleep
│   └── Q20 — Promotion pipeline: dev→staging→prod with input gates
├── Shared Libraries
│   └── Q18 — vars/src/resources layout, call() method, @Library import
└── Promotion Strategy
    └── Q20 — Build once, promote: never rebuild per environment
```

### First Principles

- JCasC exists because UI-configured Jenkins is not reproducible. If the controller crashes, a UI-configured system is gone. YAML in Git means the controller can be reconstructed from scratch.
- Credentials belong in a store, not in code, because code is readable by everyone with repo access. Secrets in code also persist forever in Git history even after deletion.
- Parallel stages exist because sequential CI is slow. If unit tests take 5 minutes, integration tests 5 minutes, and linting 2 minutes, sequential = 12 minutes. Parallel = 5 minutes (the slowest).
- `stash`/`unstash` exists because stages on different agents don't share a filesystem. The controller acts as a temporary intermediary to transfer files between agent workspaces.
- Artifact promotion (build once, promote) exists because rebuilding in each environment means the artifact tested in staging is not the artifact deployed to production — a fundamental safety violation.
- `input()` gates exist to introduce human judgment at high-risk transitions (staging → production) without breaking the automation upstream.

## Medium

**9. What is Jenkins Configuration as Code (JCasC) and why is it important?**

JCasC allows managing the entire Jenkins controller configuration (jobs, credentials, plugins, security settings) via a versioned YAML file. Benefits: the controller becomes reproducible from scratch, configuration changes go through code review, and recovery from disaster is automated.

**10. How do you manage credentials in Jenkins securely?**

Store credentials in the Jenkins Credentials Store (never in Jenkinsfiles or environment variables in job configs). Reference them with `withCredentials` binding:

```groovy
withCredentials([usernamePassword(credentialsId: 'my-creds', 
                                   usernameVariable: 'USER', 
                                   passwordVariable: 'PASS')]) {
  sh 'curl -u $USER:$PASS https://api.example.com'
}
```

For production: integrate with HashiCorp Vault or AWS Secrets Manager using Jenkins plugins to fetch dynamic, short-lived credentials.

**11. How do you run Jenkins pipeline stages in parallel?**

Use the `parallel` directive inside a `stage`:

```groovy
stage('Test') {
  parallel {
    stage('Unit Tests') { steps { sh 'pytest tests/unit' } }
    stage('Integration Tests') { steps { sh 'pytest tests/integration' } }
    stage('Lint') { steps { sh 'flake8 src/' } }
  }
}
```

**12. What is the `stash`/`unstash` mechanism in Jenkins?**

`stash` saves files from the current workspace so they can be retrieved in another stage or agent. `unstash` retrieves those files. Used to pass build artifacts between stages that run on different agents.

**13. How do you implement artifact promotion in a Jenkins pipeline?**

Build the artifact once in CI. Use a quality gate (test pass, security scan pass) before promotion. Copy the artifact to a production artifact repository using `crane copy` or `skopeo copy --multi-arch` — not rebuilding. The deployment stage references the immutable image digest, not a mutable tag.

**14. How do you implement a manual approval gate in Jenkins?**

Use `input` step:

```groovy
stage('Deploy to Production') {
  steps {
    input message: 'Deploy to production?', ok: 'Deploy', 
          submitter: 'release-team'
    sh './deploy.sh production'
  }
}
```

The pipeline pauses until an authorized user clicks "Deploy" in the Jenkins UI.

***


**15. How do you implement dynamic agent provisioning using the Kubernetes plugin?**

The Jenkins Kubernetes plugin spins up a Pod as an agent for each build and tears it down when done. Configure in JCasC:

```yaml
jenkins:
  clouds:
  - kubernetes:
      name: k8s
      serverUrl: https://kubernetes.default
      namespace: jenkins
      podTemplates:
      - name: default
        containers:
        - name: jnlp
          image: jenkins/inbound-agent:latest
        - name: docker
          image: docker:24-dind
          privileged: true
```

In Jenkinsfile:
```groovy
agent {
  kubernetes {
    yaml '''
      spec:
        containers:
        - name: maven
          image: maven:3.9-eclipse-temurin-21
          command: [sleep, infinity]
    '''
  }
}
```

Each build gets a clean, isolated Pod. No persistent agent state leaks between builds.

**16. What is Jenkins Configuration as Code (JCasC) and how does it differ from Job DSL?**

JCasC manages the Jenkins **controller configuration**: global settings, security realm, credentials, cloud connectors, tool installations, plugin settings. It's YAML-based and applied on controller startup.

Job DSL manages **jobs and pipelines** — it's a Groovy DSL that generates Jenkins job XML. A "seed job" runs Job DSL scripts to create/update other jobs.

They complement each other: JCasC configures the controller, Job DSL (or multibranch pipelines) creates the jobs. In a GitOps setup: JCasC in a config repo → controller config; Jenkinsfiles in application repos → pipeline definitions.

**17. How do you handle pipeline failures and implement retry logic?**

```groovy
stage('Deploy') {
  steps {
    retry(3) {
      sh './deploy.sh'
    }
  }
  post {
    failure {
      slackSend channel: '#alerts', message: "Deploy failed: ${env.BUILD_URL}"
    }
  }
}
```

`retry(n)` retries the block up to n times on failure. `timeout(time: 10, unit: 'MINUTES')` prevents hung steps. For exponential backoff, use a `script` block with `sleep`:

```groovy
script {
  int attempt = 0
  while (attempt < 3) {
    try { sh './deploy.sh'; break }
    catch (e) { sleep(Math.pow(2, attempt) as int); attempt++ }
  }
}
```

**18. What is a Jenkins shared library and how is it structured?**

A shared library is a Git repo with this layout:
```
vars/          # global pipeline steps (called as steps in Jenkinsfile)
  deployApp.groovy
src/           # Groovy classes (helper logic, utilities)
  org/example/
    DeployHelper.groovy
resources/     # non-Groovy files (shell scripts, templates)
  scripts/deploy.sh
```

`vars/deployApp.groovy` exposes a `call()` method:
```groovy
def call(String env, String image) {
  sh "helm upgrade --install myapp ./chart --set image=${image} --set environment=${env}"
}
```

In Jenkinsfile: `@Library('my-shared-lib') _` then `deployApp('staging', params.IMAGE)`.

**19. How do you prevent secrets from appearing in Jenkins build logs?**

1. Use `withCredentials` — Jenkins automatically masks the bound variable values in console output
2. Set `trimString` on secret environment variables
3. Use `mask-passwords` plugin for ad-hoc masking
4. Never `echo` a secret — even masked output can sometimes be inferred from timing

```groovy
withCredentials([string(credentialsId: 'api-token', variable: 'TOKEN')]) {
  sh 'curl -H "Authorization: Bearer $TOKEN" https://api.example.com'
  // TOKEN is masked in logs as ****
}
```

**20. How do you implement a promotion pipeline (dev → staging → production) in Jenkins?**

Pattern: separate Jenkins pipelines per environment chained by upstream triggers, or a single pipeline with `input` gates:

```groovy
pipeline {
  stages {
    stage('Build & Test') { steps { sh 'make test && make build' } }
    stage('Deploy Dev') { steps { sh './deploy.sh dev' } }
    stage('Deploy Staging') {
      steps {
        input message: 'Promote to staging?', submitter: 'qa-team'
        sh './deploy.sh staging'
      }
    }
    stage('Deploy Production') {
      steps {
        input message: 'Promote to production?', submitter: 'release-managers'
        sh './deploy.sh production'
      }
    }
  }
}
```

The artifact (Docker image, JAR) is built once and promoted — never rebuilt per environment.

### System Design Perspective

**Pipeline scalability:**
- At scale (50+ teams, 200+ pipelines), a single Jenkins controller with static agents becomes a bottleneck. K8s pod agents with JCasC pod templates let the cluster auto-scale agent capacity. The controller coordinates; K8s handles compute.
- `disableConcurrentBuilds(abortPrevious: true)` is critical for PR pipelines — without it, every commit to an active PR stacks builds. With 20 engineers each pushing 10 times a day, this is 200 queued builds from PR activity alone.

**Agent/runner architecture trade-offs:**
- K8s pod agents (Q15) are the correct answer for most teams. Multi-container pods let you combine a build container (Maven, Node) with tool containers (Docker-in-Docker, Trivy, kubectl) in a single Pod — no tool installation required at runtime.
- Trade-off: K8s pod agents require a running cluster and have cold-start latency. For very short jobs (<30s total), the pod startup overhead dominates. Pre-pulling agent images on every node reduces this.

**Failure recovery:**
- `retry(3)` (Q17) handles transient infrastructure failures. Combine with exponential backoff for idempotency: a deploy that retries immediately three times may still hit the same transient state.
- For long-running pipelines with manual `input()` gates (Q14), the pipeline holds a lightweight thread on the controller but releases the agent executor. Ensure the controller has enough memory for queued pipeline threads.

**Caching strategies:**
- Maven dependency cache (`~/.m2`) is lost on every K8s pod agent build. Mount a `ReadWriteMany` PVC shared across pods, or configure a Nexus/Artifactory proxy that caches upstream artifacts centrally.
- `stash`/`unstash` (Q12) is not a cache — it stores files in Jenkins internal storage per-build. Use it for intra-pipeline file transfer, not for cross-build dependency caching.
- For Docker builds: BuildKit registry cache (`--cache-from registry/image:cache`) persists layer cache across ephemeral agents via a registry — no shared volume needed.

**Security boundaries:**
- Credentials in Jenkins Credentials Store are AES-encrypted. The store's key (`master.key`) lives in `JENKINS_HOME`. If `master.key` and `credentials.xml` are both backed up together, secrets are recoverable — but if separated, they are useless individually.
- Folder-scoped credentials limit blast radius: credentials registered at folder level are only accessible to pipelines in that folder, not org-wide.

```
Jenkins Interview — Hard
├── High Availability
│   └── Q15 — Controller on K8s PVC, ephemeral K8s agents, JCasC recovery
├── Migration
│   └── Q16 — Jenkins→GitLab CI: categorize, pilot, document, phased rollout
├── Dynamic Agents
│   └── Q17 — K8s plugin: Pod template, agent registers, job runs, Pod deleted
├── Terraform Integration
│   └── Q18 — local-exec/remote-exec risks: non-idempotent, untracked state
├── DevOps Interview Playbook
│   ├── What Interviewers Test
│   │   ├── Fundamentals — Linux, networking, CI/CD, containers, observability
│   │   ├── Systems Thinking — dependencies, blast radius, recent changes
│   │   ├── Troubleshooting Depth — metrics → logs → hypothesis → mitigate
│   │   ├── Automation Mindset — scripts, pipelines, modules, runbooks
│   │   └── Communication — structured 5-step answer framework
│   ├── Strong Answer Framework
│   │   └── Clarify → recent change → signals → narrow layer → commands → stabilize
│   ├── Must-Know Commands
│   │   ├── Git — status, log, diff, revert, fetch
│   │   ├── Linux — top, ps, journalctl, df, free, ss, lsof
│   │   ├── Networking — curl -v, dig, ip route, tcpdump, mtr
│   │   ├── Docker — ps, logs, exec, inspect, stats
│   │   ├── Kubernetes — get pods -A, describe, logs --previous, events, top
│   │   └── Terraform/Ansible — init, plan, show, state, force-unlock, ping
│   ├── High-Value Scenarios
│   │   ├── CrashLoopBackOff — describe, logs --previous, OOM, probes
│   │   ├── ImagePullBackOff — tag, imagePullSecrets, registry auth
│   │   ├── Pending/FailedScheduling — requests, taints, affinity, PVC zones
│   │   ├── High Latency After Scaling — throttling, pool exhaustion, DNS
│   │   ├── Terraform Recreate Critical Resource — plan, ForceNew, prevent_destroy
│   │   └── Monitoring No Data — target discovery, /metrics, service monitor
│   ├── Design Trade-Offs
│   │   ├── Merge vs rebase
│   │   ├── Rolling vs blue-green vs canary
│   │   ├── HPA vs VPA
│   │   ├── Terraform module reuse vs env isolation
│   │   └── Prometheus pull vs push model
│   └── Behavioral Preparation
│       └── STAR stories: incident, automation, pipeline improvement, security control
```

### First Principles

- Jenkins HA is not true active-active HA — it is fast recovery HA. A single controller on K8s PVC means: when the controller Pod crashes, K8s reschedules it within seconds and remounts the same volume. This achieves ~99.9% availability without the complexity of active-active clustering.
- Migration from Jenkins to GitLab CI is an organizational problem first, a technical problem second. Big-bang migrations fail because teams have no migration support and no time. Phased migration with pilots and documentation lets teams self-serve.
- Dynamic K8s agents solve the "snowflake agent" problem: static agents accumulate state (cached images, leftover files, installed tools) that makes builds non-reproducible. Fresh pods are identical every time by construction.
- `local-exec`/`remote-exec` in Terraform break the declarative model. Terraform state tracks resources, not script side effects. A re-run triggers the script again — the opposite of idempotency.
- Senior DevOps interview answers are structured around impact first: "what is failing for users right now?" before diving into root cause. Triage before diagnosis.

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

***

**1. What is Jenkins and what problem does it solve?**

Jenkins is an open-source automation server written in Java. It solves the problem of manual, error-prone software delivery by automating every step from code commit to production deployment. Jenkins watches a version control system, triggers a pipeline on changes, runs tests, builds artifacts, and deploys — without human intervention.

Key facts:
- Open-source, self-hosted (contrast with GitHub Actions or GitLab CI which are SaaS/integrated)
- ~1,800 plugins making it integrable with almost any tool
- Runs on JVM; requires Java 17 or 21

***

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

***

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

***

**4. What are Jenkins agents and why are they used?**

Agents (also called nodes or workers) are machines that execute build steps on behalf of the Jenkins controller. The controller distributes work to agents instead of running builds itself — this is the controller/agent (master/worker) architecture.

**Reasons to use agents:**
- **Scale:** 20 agents = 20 concurrent builds
- **Isolation:** Each agent runs builds independently; a crashed agent doesn't affect the controller
- **Specialization:** GPU agents for ML, Windows agents for .NET, macOS agents for iOS
- **Clean environments:** Ephemeral agents (Kubernetes pods, Docker containers) get a fresh environment per build

Types: permanent agents (physical/VM), Docker agents, Kubernetes pod agents.

***

**5. What is a Jenkins Shared Library?**

A Shared Library is a collection of reusable Groovy code — steps, utilities, and pipeline templates — stored in a separate Git repository and imported by Jenkinsfiles across projects. It applies the DRY (Don't Repeat Yourself) principle to pipeline code.

```groovy
// Import in Jenkinsfile
@Library('company-lib@v2.1.0') _

// Call a global variable defined in vars/buildAndPush.groovy
buildAndPush(name: 'my-service', registry: 'registry.example.com')
```

***

**6. What is a `stage` in a Jenkins pipeline?**

A `stage` is a named logical division of the pipeline — e.g., Build, Test, Deploy. It groups related `steps` together. Stages appear as columns in the Jenkins pipeline visualization (Blue Ocean / Pipeline Graph View), making it easy to see where a build failed.

```groovy
stages {
    stage('Build')  { steps { sh 'mvn package' } }
    stage('Test')   { steps { sh 'mvn test' } }
    stage('Deploy') { steps { sh './deploy.sh' } }
}
```

***

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

***

**8. How do you trigger a Jenkins pipeline automatically on a code push?**

Configure a webhook in the SCM platform (GitHub, GitLab, Bitbucket) pointing to `https://jenkins.example.com/github-webhook/`. When a push occurs, the SCM calls Jenkins, which triggers the matching job.

Jenkins job configuration:
- Enable **"GitHub hook trigger for GITScm polling"** (GitHub)
- Enable **"Build when a change is pushed to GitLab"** (GitLab plugin)

Alternative: `pollSCM('H/5 * * * *')` polls the SCM every 5 minutes. Less efficient than webhooks but works without network access from SCM to Jenkins.

***

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

***

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

***

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

***

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

***

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

***

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

***

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

***

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

### What Interviewers Are Really Testing

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

### A Strong Answer Framework

Use this structure for most technical questions and incident scenarios:

1. Clarify the symptom and impact.
2. Check whether there was a recent deployment or configuration change.
3. Start with user-facing signals: latency, errors, availability, saturation.
4. Narrow the failing layer: app, container, node, network, database, cloud service, or pipeline.
5. Run the smallest commands that can confirm or reject a hypothesis.
6. Stabilize first, then optimize, then document the long-term fix.

Example:

> I would first confirm scope and timing in Grafana, then check recent deployment history, then inspect pod events and logs. If the service is actively failing, I would prepare a rollback while I validate whether the issue is config, image, dependency, or resource pressure.

### What You Should Know By Topic

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

### Must-Know Commands

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

### High-Value Scenarios To Practice

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

### Design Trade-Offs You Should Be Ready To Explain

- Merge vs rebase
- Rolling vs blue-green vs canary deployments
- Deployment vs StatefulSet
- HPA vs VPA
- Terraform module reuse vs environment isolation
- L4 vs L7 load balancer
- Managed Kubernetes vs self-managed cluster
- Prometheus pull model vs push model
- Mutable servers vs immutable infrastructure

### Strong Signals In Senior Answers

- You lead with impact, not guesswork.
- You talk about rollback and mitigation before perfect root cause.
- You call out trade-offs instead of pretending every tool is always the best choice.
- You mention validation after the fix.
- You explain how to prevent recurrence with automation, guardrails, or observability.

### Common Weak Signals

- Jumping straight to one tool or one favorite command
- Saying "restart everything" as the first step
- Confusing symptoms with root causes
- Ignoring rollback, change history, or user impact
- Treating monitoring as CPU and memory graphs only

### Behavioral Interview Preparation

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

### Final Revision Checklist

- I can explain the path of a user request from browser to backend and database.
- I can describe how I would debug a broken deployment in Kubernetes.
- I can explain Git rollback options without confusing `reset` and `revert`.
- I can discuss Terraform state, backends, locking, and drift clearly.
- I can explain probes, Services, Ingress, HPA, and common pod failure states.
- I can describe CI/CD safety controls such as artifact immutability, approvals, and rollback.
- I can explain metrics, logs, traces, SLOs, and alert fatigue.
- I can talk through at least two real troubleshooting stories from my own work.

***

### Related Resources

- [Easy Interview Questions](interview-questions-easy.md)
- [Medium Interview Questions](interview-questions-medium.md)
- [Hard Interview Questions](interview-questions-hard.md)
- [General Interview Questions](general-interview-questions.md)
- [Azure DevOps Interview Playbook](azure-devops-interview-playbook.md)
- [Azure Scenario Drills](azure-scenario-based-drills.md)
- [Kubernetes Runbook](../05_Kubernetes/troubleshooting.md)
- [Senior DevOps Learning Path](../Learning_Path/README.md)

---

## Hard (continued) — Internals, Security & Platform Engineering

**Q: Explain the Jenkins executor model. What is the difference between controller executors and agent executors? What are flyweight executors and when are they used?**

**A:**

Jenkins uses a distributed executor model. Each executor is one thread slot capable of running a single build step concurrently.

**Controller executors:** Set to `0` in production. Every executor on the controller runs with controller JVM permissions — access to secrets, plugins, `JENKINS_HOME`. Exposing controller executors to build code is a security anti-pattern.

**Agent executors:** Each agent declares N executors (typically 2 per CPU core). Capacity planning:
```
10 agents × 2 executors = 20 concurrent builds
```

**Build queue scheduling:**
1. Label matching: only agents with required labels are candidates
2. Least-busy routing: agent with most free executors wins
3. FIFO by default (Fair Job Scheduling plugin adds priority)

**Flyweight executors:**

Pipeline stages that hold locks without executing code (e.g., `input()` waiting for human approval) use lightweight pseudo-executors that don't consume a real executor slot. Without flyweight behavior:

```
100 pipelines waiting for input × 1 executor each = 100 executors consumed
```

With flyweight: the `input()` step releases the executor while waiting. Only the resume transition consumes a real slot.

```groovy
// Anti-pattern: consumes executor the entire time the human deliberates
stage('Approval') {
  steps {
    input message: 'Approve?'
    sh './deploy.sh'
  }
}

// Pattern: separate stages so approval uses flyweight, deploy gets its own slot
stage('Wait for Approval') {
  steps { input message: 'Approve?' }  // flyweight
}
stage('Deploy') {
  steps { sh './deploy.sh' }           // real executor
}
```

**Observability:** Monitor `jenkins_queue_size_value` and `jenkins_executors_available` via the Prometheus plugin. If queue > 10 and available executors > 0 simultaneously, the cause is label mismatch (jobs restricted to unavailable labels), not capacity.

---

**Q: What is the difference between implicit and explicit shared library loading? How do you prevent a breaking change in a shared library from breaking 300 dependent pipelines?**

**A:**

**Explicit loading (safe):**
```groovy
@Library('company-lib@v2.1.0') _
pipeline {
  stages {
    stage('Build') { steps { myCustomStep() } }
  }
}
```
Each Jenkinsfile declares a pinned version. Breaking changes require each team to opt-in.

**Implicit loading (risky):**
```yaml
# JCasC
unclassified:
  globalLibraries:
    libraries:
    - name: "company-lib"
      implicit: true
      defaultVersion: "main"  # Any commit to main → all 300 pipelines
```

A change to `main` immediately affects every pipeline that uses the implicit library. A signature change like:
```groovy
// OLD
def call(String environment, String image) { ... }

// NEW (breaking)
def call(String cluster, String environment, String image) { ... }
```
breaks all 300 pipelines with no migration path.

**Prevention strategy:**

1. **Pin versions, never use branch names:**
   ```groovy
   @Library('company-lib@v2.3.0') _  // not @main
   ```
   If implicit is required, pin defaultVersion to a semver tag, not a branch.

2. **Backward-compatible signatures (named parameters):**
   ```groovy
   def call(Map config = [:]) {
     def cluster = config.cluster ?: 'default'
     def env    = config.environment ?: error('environment required')
     def image  = config.image      ?: error('image required')
   }
   // Callers: deployApp(environment: 'prod', image: 'img:tag')
   ```

3. **Canary validation before merge:**
   Maintain a test pipeline in the library repo that runs against a real application using the feature branch. Only merge to `main` after the test pipeline passes.

4. **Semantic versioning + CHANGELOG:**
   Increment MAJOR for breaking changes. Require teams to migrate within a sprint with support from the platform team.

5. **vars/ vs src/ distinction:**
   Steps in `vars/` are globally importable and must be serializable. Complex logic belongs in `src/` classes (not subject to Groovy sandbox). Keeping business logic in `src/` makes unit testing possible without a running Jenkins instance.

---

**Q: K8s pod agents take 15–30 s to start. For a 2-minute pipeline, that is 15% overhead. How do you reduce pod startup time? What are the trade-offs?**

**A:**

**Startup breakdown:**
1. K8s API call: ~200 ms
2. Image pull: 5–20 s (dominates)
3. Container init + JNLP agent connect: 3–5 s

**Optimization strategies:**

**1. Pre-pull images on every node (most effective):**
```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: image-puller
spec:
  template:
    spec:
      initContainers:
      - name: puller
        image: docker:24-dind
        command: [sh, -c, "docker pull jenkins/inbound-agent:3261"]
```
First run: 30 s. Subsequent runs: ~2 s (image cached on node).

**2. Internal registry mirror:**
Deploy a Docker registry proxy inside the cluster. Pod agents reference `internal-registry:5000/jenkins/inbound-agent:latest` instead of Docker Hub. Eliminates Internet latency and Hub rate limits.

**3. Smaller base images:**
```
ubuntu:22.04 → 1.2 GB pull
alpine:3.18  → 150 MB pull
```
Build slim CI images with only required tools pre-installed.

**4. Warm pod pool:**
Configure the Kubernetes plugin to maintain N idle agent pods:
```
idleMinutes: 10          # keep warm for 10 min after use
desiredCapacity: 3       # maintain 3 warm pods at all times
```

**Trade-off table:**

| Strategy | Startup Time | Isolation | Cost | Maintenance |
|----------|-------------|-----------|------|-------------|
| Pre-pulled images | 2–3 s | High (fresh pod) | Medium | Medium |
| Warm pool | <1 s | High | High (idle pods) | Low |
| Small images | 5–10 s | High | Low | High |
| Static agents | 0 s | Low (state accumulates) | High | High |

**Recommendation:** Pre-pull images as baseline; warm pool for release pipelines (>10/hour). Avoid static agents for build workloads — they accumulate state that causes "works on my agent" failures.

---

**Q: What does `beforeAgent: true` do in a `when` block? Why does it matter for K8s agents? Show a concrete resource waste example.**

**A:**

Without `beforeAgent: true`, Jenkins allocates an agent before evaluating the `when` condition:

```
Pipeline run → Agent allocated (K8s pod: 25 s startup) → when evaluated → condition false → stage skipped → pod destroyed
```

25 seconds of pod startup wasted for a stage that was never going to run.

**With `beforeAgent: true`:**
```
Pipeline run → when evaluated → condition false → no agent allocated → stage skipped immediately
```

**Example:**
```groovy
// WASTES a K8s pod for non-PR builds
stage('Integration Test') {
  when { changeRequest() }
  agent { kubernetes { yaml '...' } }
  steps { sh './run-integration-tests.sh' }
}

// CORRECT — evaluate condition before pod allocation
stage('Integration Test') {
  when {
    changeRequest()
    beforeAgent true
  }
  agent { kubernetes { yaml '...' } }
  steps { sh './run-integration-tests.sh' }
}
```

**At scale:** 100 builds/hour where 70% are not PRs.
- Without `beforeAgent: true`: 70 wasted pods × 25 s each = ~29 wasted minutes of compute per hour
- With `beforeAgent: true`: 0 wasted pod startups

Always pair `when` + `beforeAgent: true` when using K8s agents.

---

**Q: Explain the Groovy sandbox security model in Jenkins. What methods does it block and why? Show a legitimate use case that the sandbox rejects, and the safe resolution.**

**A:**

The Groovy sandbox whitelists safe method calls. Any method not in the whitelist throws `RejectedAccessException`. This prevents Jenkinsfile code (often written by untrusted developers) from executing dangerous operations.

**Dangerous methods always blocked:**

| Method | Risk |
|--------|------|
| `Runtime.getRuntime().exec()` | Arbitrary OS commands |
| `new GroovyShell().evaluate()` | Arbitrary code eval (sandbox escape) |
| `Field.setAccessible(true)` | Reflection to bypass access control |
| `new File('/var/lib/jenkins/secrets/')` | Read controller secrets |
| `System.exit(1)` | Crash the JVM |

**Legitimate use case blocked:**

```groovy
// Jenkinsfile — decode a base64 manifest from an artifact
stage('Parse') {
  steps {
    script {
      def manifest = readFile('manifest.b64')
      def decoded = manifest.decodeBase64()  // Blocked: not whitelisted
    }
  }
}
```

Error: `Scripts not permitted to use method java.lang.String decodeBase64`

**Wrong fix:** Approve `decodeBase64()` in "In-process Script Approval" UI. Once approved, any pipeline can use it — you've relaxed the sandbox globally for a method that was not previously reviewed.

**Correct fix:** Move logic to a Shared Library class in `src/` (not subject to sandbox, reviewed in Git):

```groovy
// src/com/company/utils/ManifestParser.groovy
package com.company.utils
class ManifestParser implements Serializable {
    def decode(String base64) {
        return base64.decodeBase64()  // No sandbox restriction here
    }
}

// Jenkinsfile — sandbox applies, but only calls into reviewed class
@Library('company-lib') _
import com.company.utils.ManifestParser

pipeline {
  stages {
    stage('Parse') {
      steps {
        script {
          def parser = new ManifestParser()
          def decoded = parser.decode(readFile('manifest.b64'))
        }
      }
    }
  }
}
```

**Policy:** Never approve methods that enable arbitrary execution (`GroovyShell`, `Runtime.exec`, `ProcessBuilder`). For legitimate needs, use Jenkins-provided DSL (`readFile`, `writeFile`, `env.VAR`) or Shared Library classes reviewed through normal Git code review.

---

**Q: How do you measure Jenkins pipeline health using DORA metrics? What metrics should you track, and how do you extract deployment frequency and MTTR from Prometheus?**

**A:**

Install the Prometheus plugin to expose Jenkins metrics on `/prometheus`. Key metrics for DORA:

**Deployment Frequency:**
```promql
# Successful production deploys per day
increase(jenkins_builds_success_build_count_total{job_name=~".*production-deploy.*"}[1d])
```

**Lead Time for Changes (commit → deploy):**

Jenkins does not natively track commit time. Capture it in the pipeline:
```groovy
post {
  success {
    script {
      def commitTime = sh(script: 'git log -1 --format=%ct', returnStdout: true).trim() as Long
      def leadTime   = (System.currentTimeMillis() / 1000) - commitTime
      // Push to Prometheus Pushgateway
      sh """
        curl -X POST http://pushgateway:9091/metrics/job/jenkins/instance/${env.JOB_NAME} \
          --data-binary 'lead_time_seconds ${leadTime}'
      """
    }
  }
}
```

**Change Failure Rate:**
```promql
# % of production deploys that resulted in a failed build
100 * (
  increase(jenkins_builds_failed_build_count_total{job_name=~".*production-deploy.*"}[7d]) /
  increase(jenkins_builds_build_count_total{job_name=~".*production-deploy.*"}[7d])
)
```

**MTTR (recovery time):**
Track PagerDuty incident open → close time correlated with a passing deploy pipeline. Alternatively, measure time between a `FAILURE` build and the next `SUCCESS` build on the production job:
```promql
# Time since last failed prod deploy (proxy for MTTR if next success = recovery)
time() - jenkins_builds_last_unsuccessful_build_timestamp_ms{job_name="production-deploy"} / 1000
```

**DORA benchmark table:**

| Metric | Elite | High | Medium | Low |
|--------|-------|------|--------|-----|
| Deployment Frequency | >1/day | 1/week–1/month | 1–6 months | <6 months |
| Lead Time | <1 hour | 1–7 days | 1–6 months | >6 months |
| MTTR | <1 hour | <1 day | 1–7 days | >1 week |
| Change Failure Rate | 0–15% | 16–30% | — | >30% |

**Actionable pattern:** Track 13-week rolling averages. A stable deployment frequency with rising lead time signals pipeline bottlenecks (slow tests, manual approvals). Rising failure rate signals quality regression. Falling MTTR signals improving incident response.
