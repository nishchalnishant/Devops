# Jenkins & CI/CD Automation

```
Jenkins & CI/CD Automation
├── Architecture
│   ├── Controller — UI, scheduling, plugin management, no builds
│   ├── Agents — workers (physical, VM, Docker, K8s pod)
│   └── JENKINS_HOME — jobs/, credentials.xml, plugins/
├── Job Types
│   ├── Freestyle — legacy point-and-click, not versioned
│   └── Pipeline — Jenkinsfile in Git (Pipeline as Code)
├── Pipeline Syntax
│   ├── Declarative — structured pipeline{} block, validated
│   └── Scripted — Groovy node{} DSL, full flexibility
├── Shared Libraries
│   ├── vars/ — global steps callable in Jenkinsfiles
│   ├── src/ — Groovy helper classes
│   └── resources/ — non-Groovy files (scripts, templates)
├── Dynamic Agents
│   ├── Docker agents — clean container per build
│   ├── Kubernetes pods — ephemeral, spin up/destroy per job
│   └── EC2 Fleet / AWS — on-demand cloud instances
├── CI/CD Flow
│   ├── Webhook/Poll SCM → Checkout → Build/Test
│   ├── Artifact Storage — Nexus, Artifactory, S3
│   └── Deploy → Staging → Production (with gates)
├── Security & Credentials
│   ├── Credentials Store — withCredentials() binding
│   ├── JCasC — YAML-based controller config in Git
│   └── RBAC — role-based access, folder scoping
├── Troubleshooting
│   ├── JVM Heap — G1GC, -Xms4G -Xmx8G
│   ├── Build history — buildDiscarder logRotator
│   └── Plugin conflicts — test updates in staging
└── Best Practices
    ├── ThinBackup / rsync JENKINS_HOME to S3
    ├── Prometheus + Grafana for build metrics
    └── Blue/Green, Canary deployment patterns
```

## First Principles

- Code changes need to be built and tested consistently — doing it manually by hand is error-prone and slow. You need something watching the repo and reacting automatically.
- A single server running all builds becomes a bottleneck and a single point of failure. Separate the "coordinator" (controller) from the "workers" (agents) so builds scale horizontally.
- Pipelines defined in click-through UIs can't be code-reviewed, versioned, or rolled back. Defining the pipeline in a Jenkinsfile in the repo solves all three.
- Dozens of teams writing their own pipeline logic leads to duplication and inconsistency. Extract common steps (build, scan, deploy) into a Shared Library once, version it, and let teams consume it.
- Static agents sitting idle cost money and accumulate state that causes "works on my machine" failures. Ephemeral agents (Docker/K8s pods) are created fresh per build and destroyed immediately after.
- Credentials hardcoded in pipelines leak into logs and version history. A dedicated Credentials Store with masked injection at runtime is the only safe pattern.

Jenkins is the industry-standard automation server. While newer tools exist, Jenkins remains the most powerful and flexible "Swiss Army Knife" for building, testing, and deploying software.

#### 1. The Jenkins Architecture
Jenkins uses a **Controller-Agent** (formerly Master-Slave) architecture:
*   **Controller:** The central "Brain." It manages the UI, configuration, and coordinates the scheduling of jobs.
*   **Agents:** The "Muscle." These are separate machines (or Docker containers) that actually run the build steps.
*   **Why split?** To ensure the Controller isn't bogged down by heavy builds and to allow builds to run on different OS environments (Linux, Windows, Mac).

#### 2. Types of Jobs
1.  **Freestyle:** Legacy way to build jobs via a point-and-click UI. Hard to version and maintain.
2.  **Pipeline (The Modern Way):** "Pipeline as Code." The entire build process is defined in a `Jenkinsfile`, which lives in your Git repository.

#### 3. Pipeline Syntax
*   **Declarative (Recommended):** A structured, easy-to-read syntax. Great for 90% of use cases.
*   **Scripted:** Uses Groovy script. Highly flexible but complex and harder to maintain.

#### 4. Shared Libraries
For large organizations, you don't want to copy-paste the same code into 100 `Jenkinsfiles`. **Shared Libraries** allow you to write reusable Groovy functions (e.g., "buildDockerImage") once and use them across the entire company.

***

#### 🔹 1. Improved Notes: Enterprise Jenkins
*   **Dynamic Agents:** Instead of keeping servers running 24/7, Jenkins can spin up a Docker container or an AWS EC2 instance only when a build starts, and destroy it when finished. This saves massive amounts of money.
*   **Plugins:** Jenkins' strength is its ecosystem. From Git and Docker to Slack and Jira, there is a plugin for everything. **But beware:** Too many plugins ("Plugin Hell") can make Jenkins slow and unstable.

#### 🔹 2. Interview View (Q&A)
*   **Q:** What is the difference between a `Stage` and a `Step`?
*   **A:** A `Stage` is a logical block of the pipeline (e.g., "Build", "Test", "Deploy"). A `Step` is a single command inside that stage (e.g., `sh 'npm install'`).
*   **Q:** How do you secure credentials in Jenkins?
*   **A:** Never hardcode passwords. Use the **Jenkins Credentials Store**. You can then inject them into your pipeline using the `credentials()` helper, which masks the output in the logs.

***

#### 🔹 3. Architecture & Design: The CI/CD Flow
1.  **Poll SCM / Webhook:** Jenkins detects a change in Git.
2.  **Checkout:** Jenkins pulls the code to an Agent.
3.  **Build & Test:** Unit tests and compilation.
4.  **Artifact Storage:** Store the binary (JAR, Docker Image) in a repository (Nexus, Artifactory).
5.  **Deploy:** Push the change to Staging/Prod.

***

#### 🔹 4. Commands & Configs (Power User)
```groovy
// A simple Declarative Jenkinsfile
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'mvn clean package'
            }
        }
        stage('Test') {
            steps {
                sh 'mvn test'
            }
        }
    }
}
```

***

#### 🔹 5. Troubleshooting & Debugging
*   **Scenario:** Jenkins is slow or "hanging."
*   **Fix:** Check the **Java Heap Memory**. Jenkins runs on the JVM. If the heap is too small, it will spend all its time doing Garbage Collection. Increase `Xmx` settings in the Jenkins config.

***

#### 🔹 6. Production Best Practices
*   **Backup:** Use the `ThinBackup` plugin or simply back up the `JENKINS_HOME` directory.
*   **Infrastructure as Code:** Use **JCasC (Jenkins Configuration as Code)** to manage Jenkins settings in a YAML file.
*   **Monitoring:** Integrate Jenkins with Prometheus and Grafana to track build success rates and queue times.

***

#### 🔹 Cheat Sheet / Quick Revision
| **Concept** | **Purpose** | **DevOps Context** |
| :--- | :--- | :--- |
| `Trigger` | Starts the job | Usually a GitHub Webhook on a code push. |
| `Agent` | Where the work happens | Usually a Docker container to ensure a clean environment. |
| `Artifact` | The output of a build | A ZIP, JAR, or Docker image ready for deployment. |
| `Post` | Actions after build | Sending a Slack notification on failure. |

***

This is Section 6: Jenkins. For a senior role, you should focus on **Blue/Green Deployments**, **Canary Analysis**, and **Pipeline-as-Code** best practices.

## System Design Perspective

**Pipeline scalability:**
- A single Jenkins controller can queue hundreds of jobs but executes none itself. Throughput scales by adding agents, not by upgrading the controller.
- Kubernetes pod agents are the gold standard: each job gets its own Pod with the exact toolchain it needs (Maven container, Docker-in-Docker container, security scanner container). 50 concurrent jobs = 50 Pods.
- Use `disableConcurrentBuilds(abortPrevious: true)` for PR pipelines — cancels the stale run immediately when a new commit pushes, reclaiming executor slots.

**Agent/runner architecture trade-offs:**

| Agent Type | Pros | Cons |
|:---|:---|:---|
| Static VM/physical | Simple, fast startup | Idle cost, state accumulates, hard to scale |
| Docker agent | Clean per build, fast | Requires Docker on agent, layer cache management |
| K8s pod agent | Ephemeral, auto-scales, multi-container | Cold start ~10-30s, requires K8s cluster |
| EC2 Fleet | Scales to cloud capacity | Startup latency 2-5min, cost management |

**Failure recovery:**
- Controller on K8s PersistentVolume: Pod crash → K8s reschedules → remounts volume → Jenkins resumes in seconds.
- JCasC in Git: if the controller is irreversibly lost, provision a fresh controller, install plugins, apply JCasC YAML — fully recovered in minutes without manual click-through.
- Failed builds must not block deploys of other services: use separate pipeline jobs per microservice, not a monolithic pipeline.

**Parallel execution strategies:**
- `parallel {}` block runs stages simultaneously on separate agents. Use for independent workloads: unit tests, integration tests, and linting can all run in parallel.
- Dynamic parallel (Scripted pipeline loop) generates parallel branches at runtime — useful for deploying to N regions simultaneously.
- `failFast true` stops all parallel branches the moment one fails, saving compute on long multi-branch runs.

**Caching strategies:**
- Dependency caches (`~/.m2`, `~/.gradle`, `node_modules`) belong on the agent, not in the workspace. Mount a PVC or use a cache volume shared across pod agents via `ReadWriteMany`.
- `stash`/`unstash` passes build outputs between stages that run on different agents — avoids re-downloading artifacts.
- Docker layer cache: use BuildKit with a registry cache (`--cache-from`, `--cache-to`) so image layers are reused across builds even on ephemeral agents.

**Security boundaries:**
- Controller should have `numExecutors: 0` — it never runs builds, preventing agent-level exploits from reaching the controller filesystem.
- Credentials are stored AES-256 encrypted in `credentials.xml`; the encryption key lives in `master.key`. Back up both together.
- Groovy sandbox restricts pipeline scripts to a safe subset — escalation requires admin approval, preventing arbitrary code from reading controller secrets.