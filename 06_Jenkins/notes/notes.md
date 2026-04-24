# Jenkins — Deep Theory Notes

## Table of Contents

1. [Architecture](#architecture)
2. [Pipeline Types](#pipeline-types)
3. [Jenkinsfile Structure](#jenkinsfile-structure)
4. [Shared Libraries](#shared-libraries)
5. [Plugin Ecosystem](#plugin-ecosystem)
6. [Distributed Builds](#distributed-builds)
7. [Security Model](#security-model)
8. [Jenkins Configuration as Code (JCasC)](#jenkins-configuration-as-code-jcasc)
9. [Ephemeral Agents](#ephemeral-agents)
10. [High Availability Patterns](#high-availability-patterns)
11. [Backup and Recovery](#backup-and-recovery)

---

## Architecture

### Controller (Master)

The Jenkins controller is the central brain. It performs orchestration — it does not run build workloads itself in production.

**Responsibilities:**
- Stores all job definitions, credentials, plugin configurations, and build history
- Schedules builds and distributes them to agents via the agent protocol
- Serves the web UI on port 8080 and the REST API
- Manages plugin lifecycle (install, update, disable)
- Tracks executor slots: the controller's own executor count should be `0` in production to prevent builds running on the controller process

**Key filesystem paths:**

| Path | Purpose |
|------|---------|
| `/var/lib/jenkins/` | `JENKINS_HOME` root |
| `/var/lib/jenkins/jobs/` | Job configs (`config.xml`) and build history |
| `/var/lib/jenkins/workspace/` | Build workspaces — do not store artifacts long-term here |
| `/var/lib/jenkins/secrets/` | Master key and credential ciphertext |
| `/var/lib/jenkins/nodes/` | Agent configurations |
| `/var/lib/jenkins/plugins/` | Installed plugin `.jpi` files |
| `/var/lib/jenkins/credentials.xml` | Encrypted credential store |
| `/var/lib/jenkins/jenkins.yaml` | JCasC configuration file (if present) |

**Executor slots:** Each executor is one concurrent build slot. A controller with 0 executors plus 10 agents each with 2 executors = 20 concurrent builds. Oversaturation causes build queuing; undersaturation wastes resources.

### Agents (Workers)

Agents execute build steps. They connect to the controller over one of several protocols:

| Connection Mode | Protocol | Best For |
|----------------|----------|----------|
| SSH | SSH | Permanent Linux/macOS agents |
| JNLP / Inbound | WebSocket or TCP 50000 | Windows agents, agents behind NAT |
| Kubernetes Plugin | Kubernetes Pod API | Ephemeral agents in k8s clusters |
| Docker Plugin | Docker API | Containerized builds on Docker hosts |
| EC2 Plugin | AWS API | Dynamically provisioned AWS instances |

**Agent lifecycle (JNLP inbound):**
1. Controller receives a build request, matches it to an agent label
2. If no free executor exists, the build queues
3. The agent JVM initiates outbound connection to the controller WebSocket endpoint
4. Agent registers, controller assigns the build
5. Workspace is created on the agent, steps execute
6. Build completes, workspace optionally cleaned

### Labels and Node Selection

Labels are tags on agents that describe their capabilities. Job agent directives use label expressions:

```groovy
agent { label 'docker && linux && x86_64' }    // AND — both labels required
agent { label 'gpu || high-mem' }               // OR — either label sufficient
agent { label '!windows' }                       // NOT — exclude label
```

Label-based routing enables specialized agents: GPU agents for ML builds, large-memory agents for integration tests, Docker-enabled agents for container builds.

---

## Pipeline Types

### Declarative Pipeline

Introduced in Jenkins Pipeline 2.5. A structured DSL within a mandatory `pipeline {}` block. Validated before execution — syntax errors are caught early without consuming an executor.

**Structure hierarchy:**
```
pipeline
  ├── agent
  ├── environment
  ├── parameters
  ├── options
  ├── triggers
  ├── stages
  │   └── stage
  │       ├── agent (override)
  │       ├── when
  │       └── steps / parallel
  └── post
```

Full annotated Declarative example:

```groovy
pipeline {
    agent { label 'build-agent' }

    environment {
        REGISTRY     = 'registry.example.com'
        IMAGE_TAG    = "${env.GIT_COMMIT[0..7]}"
        SONAR_HOST   = 'https://sonar.example.com'
    }

    parameters {
        string(name: 'TARGET_ENV', defaultValue: 'staging', description: 'Deploy target')
        booleanParam(name: 'SKIP_TESTS', defaultValue: false, description: 'Skip test stage')
        choice(name: 'LOG_LEVEL', choices: ['INFO', 'DEBUG', 'WARN'], description: 'Log verbosity')
    }

    options {
        timeout(time: 45, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '20', artifactNumToKeepStr: '5'))
        disableConcurrentBuilds(abortPrevious: true)
        timestamps()
        ansiColor('xterm')
    }

    triggers {
        pollSCM('H/5 * * * *')
        cron('H 2 * * 1-5')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                sh 'git submodule update --init --recursive'
            }
        }

        stage('Build') {
            steps {
                sh 'docker build -t ${REGISTRY}/myapp:${IMAGE_TAG} --build-arg BUILD_DATE=$(date -u +%Y-%m-%dT%H:%M:%SZ) .'
            }
        }

        stage('Parallel Gates') {
            parallel {
                stage('Unit Tests') {
                    steps { sh 'npm test -- --coverage --ci' }
                    post {
                        always { junit 'test-results/**/*.xml' }
                    }
                }
                stage('Lint') {
                    steps { sh 'npm run lint -- --format junit --output-file lint-results.xml' }
                }
                stage('SAST') {
                    steps { sh 'semgrep --config=auto --junit-xml --output=semgrep.xml .' }
                }
                stage('SCA') {
                    steps { sh 'trivy fs --exit-code 1 --severity HIGH,CRITICAL .' }
                }
            }
        }

        stage('Push Image') {
            when { branch 'main' }
            steps {
                withCredentials([usernamePassword(credentialsId: 'registry-creds',
                                                   usernameVariable: 'REG_USER',
                                                   passwordVariable: 'REG_PASS')]) {
                    sh 'docker login -u $REG_USER -p $REG_PASS ${REGISTRY}'
                    sh 'docker push ${REGISTRY}/myapp:${IMAGE_TAG}'
                }
            }
        }

        stage('Deploy Staging') {
            when { branch 'main' }
            steps {
                sh 'helm upgrade --install myapp ./chart --namespace staging --set image.tag=${IMAGE_TAG}'
                sh './scripts/smoke-test.sh https://staging.example.com'
            }
        }

        stage('Deploy Production') {
            when { branch 'main' }
            steps {
                input message: 'Promote to production?', ok: 'Deploy', submitter: 'release-team'
                sh 'helm upgrade --install myapp ./chart --namespace production --set image.tag=${IMAGE_TAG}'
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'build/**/*.jar,**/test-results/**/*.xml', fingerprint: true
            cleanWs()
        }
        success {
            publishHTML(target: [
                reportDir: 'coverage',
                reportFiles: 'index.html',
                reportName: 'Coverage Report'
            ])
        }
        failure {
            emailext(
                subject: "FAILED: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: "See ${env.BUILD_URL}console",
                to: 'team@example.com'
            )
            slackSend(channel: '#ci-alerts', color: 'danger',
                      message: "Build failed: ${env.JOB_NAME} #${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)")
        }
    }
}
```

### Scripted Pipeline

The original Groovy-based pipeline format. Lives inside a `node {}` block. No enforced schema — full Groovy flexibility.

```groovy
node('linux && docker') {
    def imageTag = ''

    try {
        stage('Checkout') {
            checkout scm
            imageTag = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
        }

        stage('Build') {
            sh "docker build -t myapp:${imageTag} ."
        }

        stage('Test') {
            sh 'pytest --junitxml=results.xml'
            junit 'results.xml'
        }

    } catch (err) {
        currentBuild.result = 'FAILURE'
        slackSend channel: '#ci-alerts', message: "FAILED: ${env.JOB_NAME} — ${err}"
        throw err
    } finally {
        cleanWs()
    }
}
```

**When to use Scripted:** Complex dynamic logic (generating stages from a list), advanced Groovy class usage, or maintaining legacy pipelines not yet migrated to Declarative.

### Multibranch Pipeline

Scans a repository and automatically creates one pipeline job per branch or pull request that contains a `Jenkinsfile`. The job name in Jenkins is the branch name.

**Branch discovery sources:**
- Webhook from GitHub/GitLab/Bitbucket (recommended — immediate)
- Periodic scan (fallback — configurable interval, default 1 day)
- Manual "Scan Repository Now" (on-demand)

**PR pipelines:** With the GitHub Branch Source plugin, pull requests get their own pipeline automatically. Merges trigger the target branch pipeline after merge.

---

## Jenkinsfile Structure

All top-level Declarative pipeline directives:

| Directive | Required | Purpose |
|-----------|----------|---------|
| `agent` | Yes | Where to run — `any`, `none`, `label`, `docker`, `kubernetes` |
| `stages` | Yes | Container for `stage` blocks |
| `environment` | No | Build-wide env vars, credential bindings |
| `parameters` | No | User-facing build inputs |
| `options` | No | Build behavior (timeout, log rotation, concurrency) |
| `triggers` | No | Automatic trigger conditions (cron, pollSCM, upstream) |
| `tools` | No | Auto-install tool versions (JDK, Maven, Node) |
| `post` | No | Cleanup and notification based on build result |

---

## Shared Libraries

Shared libraries let you package pipeline code once and consume it across hundreds of Jenkinsfiles. They live in a separate Git repository and are registered in **Manage Jenkins → System → Global Pipeline Libraries**.

### Repository Layout

```
company-pipeline-lib/
├── vars/
│   ├── buildDockerImage.groovy      # callable as a pipeline step
│   ├── deployToK8s.groovy
│   └── runSonarScan.groovy
├── src/
│   └── com/example/
│       ├── PipelineUtils.groovy     # Groovy class (serializable)
│       └── NotificationService.groovy
└── resources/
    └── templates/
        └── Dockerfile.jinja         # non-Groovy resources loaded via libraryResource()
```

### Defining a Global Variable (vars/)

```groovy
// vars/buildDockerImage.groovy
def call(Map config = [:]) {
    def registry = config.get('registry', 'registry.example.com')
    def name     = config.name     ?: error('buildDockerImage requires config.name')
    def tag      = config.get('tag', env.GIT_COMMIT ? env.GIT_COMMIT[0..7] : 'latest')

    sh "docker build -t ${registry}/${name}:${tag} ."
    sh "docker push ${registry}/${name}:${tag}"
    return "${registry}/${name}:${tag}"
}
```

### Defining a Groovy Class (src/)

```groovy
// src/com/example/NotificationService.groovy
package com.example

class NotificationService implements Serializable {
    private final def script

    NotificationService(script) { this.script = script }

    def notifySlack(String channel, String message, String color = 'good') {
        script.slackSend(channel: channel, color: color, message: message)
    }
}
```

### Consuming in a Jenkinsfile

```groovy
@Library('company-pipeline-lib@v2.3.0') _

import com.example.NotificationService

pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                script {
                    def imageRef = buildDockerImage(
                        name: 'my-service',
                        registry: 'ecr.aws/123456789'
                    )
                    env.IMAGE_REF = imageRef
                }
            }
        }
    }
    post {
        failure {
            script {
                def ns = new NotificationService(this)
                ns.notifySlack('#ci-alerts', "Build failed: ${env.JOB_NAME}", 'danger')
            }
        }
    }
}
```

> [!IMPORTANT]
> Always pin shared library versions to a tag or commit SHA (`@v2.3.0`, `@abc1234`), never to a branch like `@main`. An unversioned branch reference means any breaking change in the library immediately breaks every pipeline that imports it.

### Library Version Management

Use semantic versioning for library releases. Test library changes in a feature branch, reference them via `@Library('company-lib@feature-branch')` in a test Jenkinsfile, then tag a new version and update references in dependent pipelines in a controlled rollout.

---

## Plugin Ecosystem

### Core Plugins

| Plugin | Purpose |
|--------|---------|
| `pipeline` | Declarative and scripted pipeline support |
| `git` | SCM integration |
| `credentials` | Encrypted secret storage and management |
| `credentials-binding` | `withCredentials` DSL |
| `workflow-aggregator` | Pipeline suite meta-package |
| `job-dsl` | Programmatic job creation via Groovy DSL |
| `configuration-as-code` | JCasC YAML-based controller configuration |
| `kubernetes` | Ephemeral pod-based agents |
| `docker-workflow` | `docker.build()`, `docker.withRegistry()` DSL |
| `pipeline-utility-steps` | `readYaml`, `readJSON`, `findFiles`, `zip` |
| `timestamper` | Prefix console output lines with timestamps |
| `ansicolor` | ANSI color codes in console output |
| `blueocean` | Modern visualization UI (feature-frozen 2022) |
| `pipeline-graph-view` | Lightweight Blue Ocean alternative |

### Quality and Security Plugins

| Plugin | Purpose |
|--------|---------|
| `sonarqube` | Quality gates integration |
| `owasp-dependency-check` | Dependency CVE scanning |
| `warnings-ng` | Aggregated static analysis results |
| `anchore-container-scanner` | Container policy enforcement |
| `pipeline-npm` | npm version management |

### Notification Plugins

| Plugin | Purpose |
|--------|---------|
| `slack` | Build status to Slack channels |
| `email-ext` | Rich HTML notification emails |
| `pagerduty` | Trigger/resolve PagerDuty incidents |

### Job DSL — Programmatic Job Creation

```groovy
// jobs/seed.groovy — create multibranch jobs for each service
['payments-api', 'orders-api', 'auth-service'].each { service ->
    multibranchPipelineJob("services/${service}") {
        branchSources {
            github {
                id("${service}-source")
                repoOwner('my-org')
                repository(service)
                credentialsId('github-token')
            }
        }
        orphanedItemStrategy {
            discardOldItems { numToKeep(5) }
        }
    }
}
```

---

## Distributed Builds

### Build Distribution Model

1. Developer pushes code → webhook to Jenkins controller
2. Controller evaluates the pipeline, creates an executor request with a label expression
3. Controller scans available agents for matching label + free executor slot
4. If no slot: build queues (visible in Build Queue panel)
5. Agent slot found → controller sends build plan to agent
6. Agent executes steps; controller streams logs
7. Build completes → agent reports result to controller

### Executor Slot Optimization

- Set controller executors to `0` — no builds on the controller process
- Size agent executors by CPU cores: `executors = vcpus / 2` for CPU-bound builds
- Use `lockable-resources` plugin to limit concurrent access to shared resources (test databases, hardware dongles)

```groovy
lock(resource: 'staging-db', inversePrecedence: true) {
    sh './run-integration-tests.sh'
}
```

### Throttle Concurrent Builds

```groovy
options {
    throttleJobProperty(
        categories: ['deployments'],
        throttleEnabled: true,
        throttleOption: 'category'
    )
}
```

Configure the category max concurrent count in **Manage Jenkins → Throttle Concurrent Builds** to cap how many deploy jobs run simultaneously across the controller.

---

## Security Model

### Authentication

- **Internal database:** Username/password stored in Jenkins. Fine for small teams.
- **LDAP/Active Directory:** Integrate corporate identity. Users authenticate with SSO credentials.
- **SAML/OIDC:** Integrate Okta, Azure AD, Google Workspace.

### Authorization

| Strategy | Use Case |
|----------|---------|
| Logged-in users can do anything | Dev environments only |
| Matrix-based security | Fine-grained per-user permission assignment |
| Project-based matrix | Per-job permissions — used with Folders plugin |
| Role-Based Access Control (RBAC plugin) | Role definitions + assignments — enterprise standard |

### Script Security (Groovy Sandbox)

All Groovy code in pipelines runs in a sandbox that whitelists safe methods. Code that calls non-whitelisted APIs throws `org.jenkinsci.plugins.scriptsecurity.sandbox.RejectedAccessException`.

The `script-security` plugin requires admin approval for new API signatures:

```
# Approve: java.lang.Thread sleep java.lang.long
# Block: hudson.FilePath toURI (too dangerous — filesystem access)
```

> [!CAUTION]
> Approving script signatures grants that code to run on the controller JVM with controller-level permissions. Review every approval request carefully. Reject broad signatures like `new groovy.lang.GroovyShell()` that enable arbitrary code execution bypass.

### Credential Security

- Credentials stored in `$JENKINS_HOME/credentials.xml`, AES-encrypted with the controller's master key (`secrets/master.key`)
- Leaked master.key = all credentials compromised — protect `$JENKINS_HOME/secrets/` with filesystem permissions (`chmod 700`)
- Never pass credentials via pipeline parameters (they appear in build URL/logs) — use `withCredentials` binding
- Credentials are masked in console output as `****` but base64-encoded values of secrets are not automatically masked — avoid `echo $SECRET | base64`

### Agent-Controller Security

- **Agents have read-only controller access** by default — they cannot write to `$JENKINS_HOME`
- Enable "Enable Agent → Controller Security" in Security settings
- Agents from untrusted networks: use JNLP with TLS and credentials

### CSRF Protection

Enabled by default in Jenkins 2.x. Never disable. CSRF tokens (`crumb`) are required for all state-changing API calls:

```bash
# Correct API call with crumb
CRUMB=$(curl -s -u admin:$TOKEN 'http://jenkins/crumbIssuer/api/json' | jq -r '.crumb')
curl -X POST -u admin:$TOKEN -H "Jenkins-Crumb: $CRUMB" 'http://jenkins/job/my-job/build'
```

---

## Jenkins Configuration as Code (JCasC)

JCasC (`configuration-as-code` plugin) manages the entire controller configuration as a versioned YAML file. If the controller is destroyed, provision a new one, install the plugin, and apply the YAML — fully reproduced.

```yaml
# jenkins.yaml
jenkins:
  systemMessage: "Managed by JCasC — do not edit via UI"
  numExecutors: 0
  mode: EXCLUSIVE
  agentProtocols:
    - "JNLP4-connect"
    - "Ping"

  securityRealm:
    ldap:
      configurations:
        - server: "ldap://ldap.example.com"
          rootDN: "dc=example,dc=com"
          managerDN: "cn=jenkins,dc=example,dc=com"
          managerPasswordSecret: "${LDAP_MANAGER_PASSWORD}"

  authorizationStrategy:
    roleBased:
      roles:
        global:
          - name: "admin"
            description: "Jenkins administrators"
            permissions:
              - "Overall/Administer"
            assignments:
              - "jenkins-admins"
          - name: "developer"
            description: "Developers — read and build"
            permissions:
              - "Overall/Read"
              - "Job/Build"
              - "Job/Read"
            assignments:
              - "developers"

  clouds:
    - kubernetes:
        name: "k8s-prod"
        serverUrl: "https://kubernetes.default"
        namespace: "jenkins"
        jenkinsUrl: "http://jenkins.jenkins.svc.cluster.local:8080"
        jenkinsTunnel: "jenkins-agent.jenkins.svc.cluster.local:50000"
        templates:
          - name: "default"
            label: "k8s-agent"
            containers:
              - name: "jnlp"
                image: "jenkins/inbound-agent:3107.v665000b_51092-5"
                resourceRequestCpu: "100m"
                resourceRequestMemory: "256Mi"
                resourceLimitCpu: "500m"
                resourceLimitMemory: "512Mi"
          - name: "docker-builder"
            label: "k8s-docker"
            volumes:
              - hostPathVolume:
                  hostPath: "/var/run/docker.sock"
                  mountPath: "/var/run/docker.sock"
            containers:
              - name: "jnlp"
                image: "jenkins/inbound-agent:3107.v665000b_51092-5"
              - name: "docker"
                image: "docker:24-dind"
                privileged: true

credentials:
  system:
    domainCredentials:
      - credentials:
          - usernamePassword:
              id: "nexus-creds"
              description: "Nexus service account"
              username: "ci-user"
              password: "${NEXUS_PASSWORD}"
              scope: GLOBAL
          - string:
              id: "slack-token"
              secret: "${SLACK_BOT_TOKEN}"
              scope: GLOBAL

tool:
  git:
    installations:
      - name: "Default"
        home: "git"
  maven:
    installations:
      - name: "maven-3.9"
        home: ""
        properties:
          - installSource:
              installers:
                - maven:
                    id: "3.9.6"

unclassified:
  location:
    url: "https://jenkins.example.com/"
    adminAddress: "jenkins-admin@example.com"
  slackNotifier:
    teamDomain: "mycompany"
    tokenCredentialId: "slack-token"
  sonarGlobalConfiguration:
    buildWrapperEnabled: true
    installations:
      - name: "SonarQube"
        serverUrl: "https://sonar.example.com"
        credentialsId: "sonar-token"
```

**Apply JCasC without restart:**
```bash
curl -X POST -u admin:$TOKEN \
  'https://jenkins.example.com/configuration-as-code/reload'
```

### JCasC + GitOps Workflow

1. Store `jenkins.yaml` in a Git repository
2. On merge to `main`, a pipeline pushes the file to the controller and triggers reload
3. All configuration changes go through pull request review — no manual UI clicks
4. If the controller is lost, GitOps pipeline recreates it from the YAML

---

## Ephemeral Agents

### Kubernetes Plugin Agent Lifecycle

1. Pipeline requires `agent { label 'k8s-agent' }`
2. Controller identifies this as a Kubernetes cloud label
3. Plugin submits a Pod spec to the Kubernetes API server
4. Kubernetes scheduler places the Pod on a node with capacity
5. Pod starts; the JNLP container connects back to the controller via WebSocket/TCP
6. Controller assigns the build to this agent
7. Build runs; workspace is inside the Pod's ephemeral container filesystem
8. Build completes; plugin calls `DELETE /api/v1/namespaces/jenkins/pods/<name>`
9. Pod terminated — zero idle cost, fresh environment for next build

**Pod template in Jenkinsfile (inline):**

```groovy
pipeline {
    agent {
        kubernetes {
            yaml '''
apiVersion: v1
kind: Pod
metadata:
  labels:
    job: my-pipeline
spec:
  serviceAccountName: jenkins-agent
  containers:
    - name: jnlp
      image: jenkins/inbound-agent:3107.v665000b_51092-5
      resources:
        requests:
          cpu: 100m
          memory: 256Mi
    - name: maven
      image: maven:3.9-eclipse-temurin-17
      command: [cat]
      tty: true
      resources:
        requests:
          cpu: 500m
          memory: 1Gi
        limits:
          cpu: "2"
          memory: 4Gi
    - name: kaniko
      image: gcr.io/kaniko-project/executor:debug
      command: [cat]
      tty: true
'''
        }
    }
    stages {
        stage('Build') {
            steps {
                container('maven') {
                    sh 'mvn clean package -DskipTests'
                }
            }
        }
        stage('Build Image') {
            steps {
                container('kaniko') {
                    sh '''
                    /kaniko/executor \
                      --context=dir://$(pwd) \
                      --destination=registry.example.com/myapp:${GIT_COMMIT:0:8} \
                      --cache=true \
                      --cache-repo=registry.example.com/myapp/cache
                    '''
                }
            }
        }
    }
}
```

### Docker Agents

Use Docker containers as build environments on a Docker-capable agent:

```groovy
pipeline {
    agent {
        docker {
            image 'node:20-alpine'
            args '-v /var/run/docker.sock:/var/run/docker.sock --group-add $(stat -c %g /var/run/docker.sock)'
        }
    }
    stages {
        stage('Test') {
            steps {
                sh 'npm ci && npm test'
            }
        }
    }
}
```

> [!TIP]
> For Docker-in-Docker builds, mount the host Docker socket (`/var/run/docker.sock`) into the container. Add the container user to the `docker` group using the socket's GID to avoid permission denied errors. Alternatively, use Kaniko for daemonless image builds inside Kubernetes — no socket mount required.

---

## High Availability Patterns

### Single Controller + Persistent Volume (Standard)

Run the Jenkins controller as a Kubernetes Deployment with a PersistentVolumeClaim (EBS, Azure Disk):

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jenkins
  namespace: jenkins
spec:
  replicas: 1   # Only 1 replica — Jenkins controller is not horizontally scalable
  strategy:
    type: Recreate   # Required — ReadWriteOnce PVC cannot mount on 2 pods simultaneously
  selector:
    matchLabels:
      app: jenkins
  template:
    spec:
      securityContext:
        fsGroup: 1000
        runAsUser: 1000
      containers:
        - name: jenkins
          image: jenkins/jenkins:2.452-lts
          ports:
            - containerPort: 8080
            - containerPort: 50000
          volumeMounts:
            - name: jenkins-home
              mountPath: /var/jenkins_home
          readinessProbe:
            httpGet:
              path: /login
              port: 8080
            initialDelaySeconds: 60
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /login
              port: 8080
            initialDelaySeconds: 90
            periodSeconds: 20
      volumes:
        - name: jenkins-home
          persistentVolumeClaim:
            claimName: jenkins-pvc
```

**Recovery:** If the Pod dies, Kubernetes reschedules it on another node and remounts the PVC. RTO (Recovery Time Objective): typically 2–5 minutes.

### High Availability with Operations Center (CloudBees)

CloudBees CI (commercial) offers true active-active HA via Operations Center + Client Controllers. For open-source Jenkins, "HA" means fast failover via Kubernetes + PVC, not active-active.

### Backup Strategy

```bash
# Exclude workspace (large, rebuild from source) and caches (regenerated)
rsync -av \
  --exclude='workspace/' \
  --exclude='caches/' \
  --exclude='*.tmp' \
  /var/jenkins_home/ \
  s3://company-jenkins-backup/$(date +%Y%m%d-%H%M%S)/

# Or with thinBackup plugin: schedule backups from UI
# JENKINS_HOME/thinBackup/
```

**Full reconstruction from code (zero data loss approach):**
1. JCasC YAML in Git → controller configuration
2. Job DSL scripts in Git → job definitions
3. Credentials backed up separately (encrypted) to a secret manager
4. Plugins list in `plugins.txt` → reproduced by `jenkins-plugin-cli`

---

## Backup and Recovery

Full backup script with integrity check:

```bash
#!/bin/bash
set -euo pipefail

JENKINS_HOME="/var/lib/jenkins"
BACKUP_DIR="/backups/jenkins"
DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_PATH="${BACKUP_DIR}/${DATE}"

mkdir -p "${BACKUP_PATH}"

# Backup — exclude volatile dirs
rsync -av \
  --exclude='workspace/' \
  --exclude='caches/' \
  --exclude='*.log' \
  --exclude='*.tmp' \
  "${JENKINS_HOME}/" \
  "${BACKUP_PATH}/"

# Compress
tar -czf "${BACKUP_PATH}.tar.gz" -C "${BACKUP_DIR}" "${DATE}"
rm -rf "${BACKUP_PATH}"

# Upload to S3
aws s3 cp "${BACKUP_PATH}.tar.gz" "s3://my-jenkins-backups/${DATE}.tar.gz"

# Verify upload
aws s3 ls "s3://my-jenkins-backups/${DATE}.tar.gz" | grep -q "${DATE}"
echo "Backup verified: ${DATE}"

# Prune backups older than 30 days
find "${BACKUP_DIR}" -name "*.tar.gz" -mtime +30 -delete
```
# End to End CI/CD pipeline

A CI/CD pipeline automates the software delivery process. The pipeline builds code, runs tests (CI), and safely deploys the new version of the application (CD). The goal is to minimize manual errors and deliver value to users faster and more reliably.

Here's a visual overview of the flow:

***

#### ## 1. Source Stage: Where It All Begins 🧑‍💻

Purpose: This is the trigger for the entire pipeline. It involves managing the application's source code and collaborating with the development team.

* Core Concept: Version Control. Every change is tracked, and the repository acts as the single source of truth.
* Technologies:
  * Git: The de facto standard for distributed version control.
  * SCM Platforms: GitHub, GitLab, Bitbucket. These platforms host Git repositories and provide collaboration tools like pull/merge requests.
* How They Sync:
  * A developer pushes code changes to a specific branch (e.g., `main` or a feature branch) using `git push`.
  * This push event triggers a webhook. A webhook is an automated message (an HTTP POST payload) sent from the SCM platform (e.g., GitHub) to the CI/CD server (e.g., Jenkins). This message says, "Hey, new code is here, start the pipeline!"
* Configuration:
  * Within your GitHub/GitLab repository settings, you navigate to the "Webhooks" section.
  * You add the URL of your CI/CD server's webhook endpoint (e.g., `http://<your-jenkins-server>/github-webhook/`).
  * You configure this webhook to trigger on specific events, most commonly a `push` event.

***

#### ## 2. Build Stage: Forging the Artifact ⚙️

Purpose: To take the raw source code and compile it into an executable or package. If the build fails, the pipeline stops, and the developer is notified immediately. This is the heart of Continuous Integration (CI).

* Core Concept: Compiling code and resolving dependencies.
* Technologies:
  * CI/CD Orchestrator: Jenkins is the classic choice. GitLab CI/CD and GitHub Actions are popular integrated solutions. Others include CircleCI and Travis CI.
  * Build Tools: Maven or Gradle (for Java), npm or Yarn (for Node.js), `go build` (for Golang).
* How They Sync:
  * The CI/CD orchestrator (Jenkins) receives the webhook from the Source stage.
  * It checks out the latest code from the repository using Git.
  * It then executes the build commands defined in its configuration.
* Configuration:
  * This is primarily done via Pipeline as Code. Instead of configuring jobs in a UI, you define the pipeline in a text file that is stored in the Git repository itself.
  *   Jenkins: A file named `Jenkinsfile` (written in Groovy) defines all the stages.

      Groovy

      ```
      pipeline {
          agent any
          stages {
              stage('Build') {
                  steps {
                      // For a Java project
                      sh 'mvn clean package'
                  }
              }
              // Other stages follow...
          }
      }
      ```
  * GitHub Actions: A `.yml` file inside the `.github/workflows/` directory.

***

#### ## 3. Test Stage: Ensuring Quality 🧪

Purpose: To run a suite of automated tests to catch bugs and regressions before they reach users. This stage provides the confidence to deploy automatically.

* Core Concept: Automated quality assurance.
* Technologies:
  * Unit Testing: JUnit (Java), PyTest (Python), Jest (JavaScript). These are typically run by the build tools.
  * Static Code Analysis: SonarQube, ESLint. These tools check for code smells, potential bugs, and security vulnerabilities without executing the code.
  * Integration/API Testing: Postman (Newman), REST Assured.
* How They Sync:
  * This stage is executed by the CI/CD orchestrator (Jenkins) immediately after a successful build.
  * The orchestrator runs the test commands. It can be configured to integrate with tools like SonarQube, sending the test results and code coverage reports for analysis.
  * The pipeline will fail if the code doesn't meet the defined quality gates (e.g., unit test coverage is below 80% or there are critical security issues found by SonarQube).
* Configuration:
  *   In the `Jenkinsfile`, you add a new `stage` for testing.

      Groovy

      ```
      stage('Test') {
          steps {
              // Run unit tests
              sh 'mvn test'
          }
      }
      stage('Code Analysis') {
          steps {
              // Assuming SonarQube is configured in your Jenkins instance
              withSonarQubeEnv('My-SonarQube-Server') {
                  sh 'mvn sonar:sonar'
              }
          }
      }
      ```

***

#### ## 4. Package & Store Stage: Creating the Release 📦

Purpose: To package the validated code into a versioned, immutable artifact and store it in a centralized repository.

* Core Concept: An artifact is a deployable unit. For modern microservices, this is almost always a Docker image.
* Technologies:
  * Containerization: Docker. The `Dockerfile` in the repository defines how to build the application image.
  * Artifact/Container Registries: JFrog Artifactory or Sonatype Nexus (for traditional artifacts like `.jar`, `.war`, `.rpm`). Docker Hub, Amazon ECR, Google GCR, or Azure ACR (for Docker images).
* How They Sync:
  * After the Test stage passes, the CI/CD orchestrator (Jenkins) reads the `Dockerfile`.
  * It runs the `docker build` command to create the image. The image is often tagged with a unique identifier like the Git commit hash or a build number to ensure traceability.
  * It then runs `docker push` to upload this newly created image to the container registry (e.g., Amazon ECR).
* Configuration:
  * You need a `Dockerfile` in your source code repository.
  *   In the `Jenkinsfile`:

      Groovy

      ```
      stage('Package & Push Image') {
          steps {
              script {
                  // Define image name and tag
                  def imageName = "my-registry/my-app:${env.BUILD_ID}"
                  // Build the Docker image
                  docker.build(imageName)
                  // Push the image (credentials must be configured in Jenkins)
                  docker.withRegistry('https://my-registry-url', 'my-registry-credentials') {
                      docker.image(imageName).push()
                  }
              }
          }
      }
      ```

***

#### ## 5. Deploy Stage: Going Live 🚀

Purpose: To deploy the versioned artifact from the registry to a target environment (e.g., Staging, Production). This is the heart of Continuous Deployment/Delivery (CD).

* Core Concept: Automating the release process using infrastructure-as-code and configuration management.
* Technologies:
  * Container Orchestration: Kubernetes (K8s) is the industry standard.
  * Configuration Management: Ansible (agentless, push-based), Puppet (agent-based, pull-based), Chef.
  * Infrastructure as Code (IaC): Terraform, AWS CloudFormation.
* How They Sync:
  * The CI/CD orchestrator (Jenkins) triggers this final stage, often after a manual approval for production deployments (Continuous Delivery).
  * For Kubernetes: Jenkins uses `kubectl` (the K8s command-line tool) to apply a deployment configuration file. This file specifies which Docker image to run. The pipeline's job is to update the image tag in this file to the one it just built and pushed.
  * For Ansible: Jenkins executes an `ansible-playbook` command, targeting the deployment servers. The playbook contains the sequence of steps to deploy the application (e.g., pull the new Docker image, stop the old container, run the new one).
* Configuration:
  * Kubernetes: You'll have a `deployment.yaml` file stored in Git.
  *   In the `Jenkinsfile`, you would use a command to update and apply this file:

      Groovy

      ```
      stage('Deploy to K8s') {
          steps {
              // 'sed' command updates the image tag in the yaml file
              sh "sed -i 's|image: my-registry/my-app:.*|image: my-registry/my-app:${env.BUILD_ID}|g' deployment.yaml"
              // Apply the updated configuration to the cluster
              // Kubeconfig must be set up in Jenkins
              sh "kubectl apply -f deployment.yaml"
          }
      }
      ```

***

#### ## 6. Monitor & Feedback Stage: Closing the Loop 📈

Purpose: To observe the application's performance and health in real-time, collect logs, and provide feedback to the development team.

* Core Concept: Observability. You can't improve what you can't measure.
* Technologies:
  * Monitoring & Alerting: Prometheus (for collecting time-series metrics) and Grafana (for visualizing them in dashboards). Alertmanager handles alerts.
  * Log Aggregation: ELK/EFK Stack (Elasticsearch, Logstash/Fluentd, Kibana) or commercial tools like Splunk.
* How They Sync:
  * This isn't a direct pipeline stage but a continuous process. The deployed application is instrumented to expose metrics (e.g., an `/metrics` endpoint for Prometheus to scrape).
  * It also writes logs to `stdout`, which are collected by agents like Fluentd and shipped to Elasticsearch.
  * If Prometheus detects an issue (e.g., high error rate), it triggers an alert via Alertmanager, which can notify the team on Slack or PagerDuty. This information is crucial for planning the next development sprint.
* Configuration:
  * The application code includes a Prometheus client library.
  * The Kubernetes deployment configuration includes annotations that tell Prometheus to "scrape" the application's metrics endpoint.
  * Alerting rules are defined in Prometheus configuration files.

The concepts become much easier to retain when you map them to one practical, end-to-end example.

Imagine we are building a simple Python web application using the Flask framework. The goal is to take this application from a developer's machine to a live deployment on a Kubernetes cluster, fully automated.

***

#### ## Putting It All Together: A Practical Example (Python Web App)

Here's the scenario: A developer has created a simple "Hello, World!" web app. Our job is to build the CI/CD pipeline that automatically deploys it.

**### The Project Files**

First, let's look at the files the developer would commit to a Git repository (e.g., on GitHub).

Project Structure:

```
/my-python-app
├── app.py              # The Flask application code
├── requirements.txt    # Python dependencies
├── test_app.py         # The unit tests for our app
├── Dockerfile          # Instructions to build the Docker image
├── Jenkinsfile         # The CI/CD pipeline definition for Jenkins
└── k8s-deployment.yaml # The deployment manifest for Kubernetes
```

File Contents:

1.  `app.py` (The Application)

    Python

    ```
    from flask import Flask
    app = Flask(__name__)

    @app.route('/')
    def hello_world():
        return 'Hello, DevOps World!'

    if __name__ == '__main__':
        app.run(host='0.0.0.0', port=5000)
    ```
2.  `requirements.txt` (Dependencies)

    ```
    flask
    pytest
    ```
3.  `test_app.py` (The Unit Test)

    Python

    ```
    import app

    def test_hello():
        client = app.app.test_client()
        response = client.get('/')
        assert response.status_code == 200
        assert b"Hello, DevOps World!" in response.data
    ```
4.  `Dockerfile` (The Container Recipe)

    Dockerfile

    ```
    # Use an official Python runtime as a parent image
    FROM python:3.9-slim

    # Set the working directory in the container
    WORKDIR /app

    # Copy the dependencies file and install them
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt

    # Copy the application code
    COPY app.py .

    # Expose the port the app runs on
    EXPOSE 5000

    # Define the command to run the application
    CMD ["python", "app.py"]
    ```
5.  `Jenkinsfile` (The Pipeline Brains)

    Groovy

    ```
    pipeline {
        agent any
        environment {
            // Use a private Docker Hub account for the image
            // Credentials 'dockerhub-creds' must be stored in Jenkins
            DOCKER_REGISTRY = 'your-dockerhub-username'
            IMAGE_NAME = 'my-python-app'
        }
        stages {
            stage('1. Test') {
                steps {
                    echo "--- Running Unit Tests ---"
                    sh 'pip install -r requirements.txt'
                    sh 'pytest test_app.py'
                }
            }
            stage('2. Build & Push Docker Image') {
                steps {
                    script {
                        echo "--- Building & Pushing Docker Image ---"
                        // The BUILD_ID is a unique Jenkins variable
                        def imageTag = "${env.BUILD_ID}"
                        def fullImageName = "${env.DOCKER_REGISTRY}/${env.IMAGE_NAME}:${imageTag}"

                        // Build the image
                        docker.build(fullImageName)

                        // Push the image
                        docker.withRegistry("https://index.docker.io/v1/", 'dockerhub-creds') {
                            docker.image(fullImageName).push()
                        }
                    }
                }
            }
            stage('3. Deploy to Kubernetes') {
                steps {
                    echo "--- Deploying to Kubernetes Cluster ---"
                    // Credentials 'kube-config' must be stored in Jenkins
                    withKubeConfig([credentialsId: 'kube-config']) {
                        // Dynamically update the deployment file with the new image tag
                        sh "sed -i 's|image: .*|image: ${env.DOCKER_REGISTRY}/${env.IMAGE_NAME}:${env.BUILD_ID}|g' k8s-deployment.yaml"

                        // Apply the updated configuration
                        sh "kubectl apply -f k8s-deployment.yaml"
                    }
                }
            }
        }
    }
    ```
6.  `k8s-deployment.yaml` (The Deployment Instructions)

    YAML

    ```
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: my-python-app-deployment
    spec:
      replicas: 2
      selector:
        matchLabels:
          app: my-python-app
      template:
        metadata:
          labels:
            app: my-python-app
        spec:
          containers:
          - name: python-app-container
            # This 'image' line is a placeholder that Jenkins will update
            image: your-dockerhub-username/my-python-app:latest
            ports:
            - containerPort: 5000
    ```

***

**### The Automated Flow in Action**

1. Source 🧑‍💻: The developer makes a change to `app.py` and runs `git push origin main`.
2. Trigger: GitHub receives the push and immediately sends a webhook to the pre-configured Jenkins server.
3. Initiate: Jenkins receives the webhook, finds the `Jenkinsfile` in the `main` branch of the repository, and starts a new pipeline build (e.g., Build #42).
4. Stage 1: Test 🧪:
   * Jenkins executes the `Test` stage.
   * It runs `pip install -r requirements.txt` to install Flask and Pytest.
   * It then runs `pytest test_app.py`. The test passes. The pipeline proceeds.
5. Stage 2: Package & Store 📦:
   * Jenkins executes the `Build & Push Docker Image` stage.
   * It builds the Docker image using the `Dockerfile`. Let's say the build ID is `42`. The resulting image will be named `your-dockerhub-username/my-python-app:42`.
   * Using the stored credentials, Jenkins logs into Docker Hub and pushes this new image to the registry. The artifact is now stored and versioned.
6. Stage 3: Deploy 🚀:
   * Jenkins moves to the final `Deploy to Kubernetes` stage.
   * It uses the `sed` command to find the `image:` line in `k8s-deployment.yaml` and replaces it with the exact image it just pushed: `image: your-dockerhub-username/my-python-app:42`.
   * Using the Kubernetes config credentials, it runs `kubectl apply -f k8s-deployment.yaml`.
   * Kubernetes receives this instruction. It sees the deployment needs an updated image. It performs a rolling update: it creates new pods with the new `...:42` image and, once they are healthy, terminates the old pods. This ensures zero downtime.
7. Operate & Monitor 📈: The new application pods are now running. Prometheus scrapes their metrics, and Fluentd collects their logs. If the error rate suddenly spikes, the on-call team gets an alert.

Within minutes of the `git push`, the developer's change is tested, packaged, and live in production, all without any manual intervention. This is the power of a fully integrated CI/CD pipeline.


