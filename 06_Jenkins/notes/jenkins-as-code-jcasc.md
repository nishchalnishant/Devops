---
description: Jenkins Configuration as Code (JCasC), Declarative Pipeline patterns, shared libraries, and enterprise CI/CD architecture for senior engineers.
---

# Jenkins — JCasC & Pipeline Architecture Patterns

```
JCasC & Pipeline Architecture Patterns
├── Jenkins Configuration as Code (JCasC)
│   ├── jenkins.yaml — single source of truth for controller config
│   ├── systemMessage, numExecutors: 0 — no builds on controller
│   ├── securityRealm — LDAP server, rootDN, groupSearchBase
│   ├── authorizationStrategy — roleBased: admin/developer roles
│   ├── clouds.kubernetes — cluster URL, namespace, pod templates
│   │   └── templates: name, label, containers (jnlp + resource limits)
│   ├── credentials — usernamePassword with env var injection (${GITHUB_TOKEN})
│   └── globalLibraries — Git remote, defaultVersion, credentialsId
├── Declarative Pipeline — Enterprise Template
│   ├── @Library('company-shared-lib@main') _ — shared lib import
│   ├── agent.kubernetes — multi-container pod (build + docker DinD)
│   ├── options — buildDiscarder, timeout, disableConcurrentBuilds, ansiColor
│   ├── environment — IMAGE_NAME, IMAGE_TAG (GIT_COMMIT[0..7]), SONAR_TOKEN
│   ├── stages
│   │   ├── Test — container('build'), junit, jacoco post
│   │   ├── SAST — SonarQube withSonarQubeEnv
│   │   ├── Quality Gate — waitForQualityGate abortPipeline: true
│   │   ├── Build & Push — when: branch 'main', docker build/push
│   │   ├── Deploy Staging — deployToKubernetes() shared lib step
│   │   ├── Integration Tests — smoke test against staging URL
│   │   └── Deploy Production — input: submitter='senior-engineers'
│   └── post — slackSend failure/success, cleanWs() always
├── Shared Library — Enterprise Reuse
│   ├── vars/ — deployToKubernetes.groovy: call(Map config)
│   │   └── withKubeConfig → kubectl set image → kubectl rollout status
│   ├── src/com/company/jenkins/ — DockerUtils, KubernetesClient
│   └── resources/pod-templates/ — gradle-agent.yaml
└── Junior vs Senior Patterns
    ├── Config: click UI → JCasC YAML in Git
    ├── Agents: static VMs → K8s ephemeral pod agents
    ├── Shared code: copy Jenkinsfile → Shared Library versioned tags
    ├── Parallel: sequential stages → parallel{} block
    ├── Credentials: global creds → folder-scoped, rotated via JCasC
    └── Build cleanup: unlimited history → buildDiscarder logRotator
```

## First Principles

- JCasC solves the "snowflake Jenkins" problem. Without it, every Jenkins controller is a unique, hand-configured system that cannot be reproduced after failure. With JCasC, the controller config is a YAML file in Git — it can be reconstructed on a new controller in minutes.
- Setting `numExecutors: 0` on the controller is a security requirement, not an option. Code running on the controller has filesystem access to `master.key` and `credentials.xml`. Agents are expendable; the controller must be protected.
- The enterprise pipeline template (Test → SAST → Quality Gate → Build → Staging → Integration → Production) represents the principle: validate before promoting, never build again after the first artifact.
- `waitForQualityGate abortPipeline: true` is a hard stop, not a soft warning. Code that fails SonarQube quality gates cannot advance to build or deploy stages. This enforces the quality gate as a mandatory control, not a suggestion.
- Shared library `call(Map config)` pattern with defaults (`config.cluster ?: 'staging'`) gives a good DX: callers only specify what differs from defaults. Missing required arguments use `error('image is required')` to fail loudly rather than silently doing the wrong thing.

## Jenkins Configuration as Code (JCasC)

JCasC allows the entire Jenkins configuration to be defined in a YAML file and version-controlled. UI changes are ephemeral — only YAML changes persist.

```yaml
# jenkins.yaml — Complete Jenkins configuration as code
jenkins:
  systemMessage: "Production Jenkins — All changes must go through Git"
  numExecutors: 0              # No builds on controller (security best practice)
  mode: EXCLUSIVE
  
  securityRealm:
    ldap:
      server: "ldap://ldap.company.com"
      rootDN: "dc=company,dc=com"
      groupSearchBase: "ou=groups"
  
  authorizationStrategy:
    roleBased:
      roles:
        global:
          - name: "admin"
            permissions:
              - "Overall/Administer"
            assignments:
              - "jenkins-admins"
          - name: "developer"
            permissions:
              - "Overall/Read"
              - "Job/Build"
              - "Job/Read"
            assignments:
              - "all-developers"

  clouds:
    - kubernetes:
        name: "kubernetes"
        serverUrl: "https://kubernetes.default.svc"
        namespace: "jenkins"
        jenkinsUrl: "http://jenkins.jenkins.svc.cluster.local:8080"
        jenkinsTunnel: "jenkins.jenkins.svc.cluster.local:50000"
        templates:
          - name: "default"
            label: "k8s-agent"
            containers:
              - name: "jnlp"
                image: "jenkins/inbound-agent:latest"
                resourceRequestCpu: "200m"
                resourceRequestMemory: "256Mi"
                resourceLimitCpu: "500m"
                resourceLimitMemory: "512Mi"

credentials:
  system:
    domainCredentials:
      - credentials:
          - usernamePassword:
              scope: GLOBAL
              id: "github-credentials"
              username: "jenkins-bot"
              password: "${GITHUB_TOKEN}"   # Injected from K8s secret

unclassified:
  location:
    url: "https://jenkins.company.com/"
  
  globalLibraries:
    libraries:
      - name: "company-shared-lib"
        defaultVersion: "main"
        retriever:
          modernSCM:
            scm:
              git:
                remote: "https://github.com/company/jenkins-shared-lib.git"
                credentialsId: "github-credentials"
```

***

## Declarative Pipeline — Production Patterns

### Full Enterprise Pipeline Template

```groovy
// Jenkinsfile
@Library('company-shared-lib@main') _  // Load shared library

pipeline {
  agent {
    kubernetes {
      yaml '''
        apiVersion: v1
        kind: Pod
        spec:
          containers:
          - name: build
            image: gradle:8.5-jdk21
            command: [sleep]
            args: [infinity]
            resources:
              requests:
                cpu: "500m"
                memory: "1Gi"
          - name: docker
            image: docker:24-dind
            securityContext:
              privileged: true
      '''
    }
  }

  options {
    buildDiscarder(logRotator(numToKeepStr: '20'))
    timeout(time: 30, unit: 'MINUTES')
    disableConcurrentBuilds(abortPrevious: true)   // Cancel older PR builds
    ansiColor('xterm')
  }

  environment {
    IMAGE_NAME    = "myregistry.io/my-service"
    IMAGE_TAG     = "${env.GIT_COMMIT[0..7]}"
    SONAR_TOKEN   = credentials('sonar-token')
  }

  stages {
    stage('Test') {
      steps {
        container('build') {
          sh './gradlew test jacocoTestReport'
        }
      }
      post {
        always {
          junit '**/build/test-results/**/*.xml'
          jacoco execPattern: '**/build/jacoco/*.exec'
        }
      }
    }

    stage('SAST') {
      steps {
        container('build') {
          withSonarQubeEnv('SonarQube') {
            sh './gradlew sonarqube'
          }
        }
      }
    }

    stage('Quality Gate') {
      steps {
        timeout(time: 5, unit: 'MINUTES') {
          waitForQualityGate abortPipeline: true   // Block if SonarQube fails
        }
      }
    }

    stage('Build & Push') {
      when { branch 'main' }
      steps {
        container('docker') {
          sh """
            docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
            docker push ${IMAGE_NAME}:${IMAGE_TAG}
          """
        }
      }
    }

    stage('Deploy Staging') {
      when { branch 'main' }
      steps {
        deployToKubernetes(  // Custom step from shared library
          cluster: 'staging',
          image: "${IMAGE_NAME}:${IMAGE_TAG}"
        )
      }
    }

    stage('Integration Tests') {
      when { branch 'main' }
      steps {
        sh './scripts/run-integration-tests.sh https://staging.company.com'
      }
    }

    stage('Deploy Production') {
      when { branch 'main' }
      input {
        message "Deploy to Production?"
        ok "Deploy"
        submitter "senior-engineers,release-managers"
      }
      steps {
        deployToKubernetes(
          cluster: 'production',
          image: "${IMAGE_NAME}:${IMAGE_TAG}"
        )
      }
    }
  }

  post {
    failure {
      slackSend(
        channel: '#ci-failures',
        color: 'danger',
        message: "Pipeline failed: ${env.JOB_NAME} #${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)"
      )
    }
    success {
      slackSend(channel: '#deployments', color: 'good',
        message: "Deployed ${IMAGE_NAME}:${IMAGE_TAG} to production")
    }
    always {
      cleanWs()  // Delete workspace after build
    }
  }
}
```

***

## Shared Library — Enterprise Reuse

```
jenkins-shared-lib/
├── vars/
│   ├── deployToKubernetes.groovy   ← Global variable (callable as step)
│   ├── runSecurityScan.groovy
│   └── notifySlack.groovy
├── src/
│   └── com/company/jenkins/
│       ├── DockerUtils.groovy      ← Helper classes
│       └── KubernetesClient.groovy
└── resources/
    └── pod-templates/
        └── gradle-agent.yaml       ← Reusable agent YAML
```

**`vars/deployToKubernetes.groovy`:**
```groovy
def call(Map config) {
  def cluster   = config.cluster  ?: 'staging'
  def image     = config.image    ?: error('image is required')
  def namespace = config.namespace ?: 'production'

  withKubeConfig(credentialsId: "kubeconfig-${cluster}") {
    sh """
      kubectl set image deployment/my-service \
        my-service=${image} \
        -n ${namespace}
      kubectl rollout status deployment/my-service \
        -n ${namespace} \
        --timeout=5m
    """
  }
}
```

***

## Logic & Trickiness Table

| Pattern | Junior Approach | Senior Approach |
|:---|:---|:---|
| **Jenkins config** | Click in UI | JCasC — all config in `jenkins.yaml` in Git |
| **Agents** | Static VMs | Kubernetes dynamic pod agents (ephemeral, clean) |
| **Shared code** | Copy Jenkinsfile across repos | Shared Library with versioned tags |
| **Parallel stages** | Sequential stages | Use `parallel {}` block for independent stages (e.g., unit test + SAST) |
| **Credentials** | Hardcode or use global creds | Scoped credentials per folder; rotate via JCasC |
| **Build cleanup** | Unlimited build history | `buildDiscarder(logRotator(numToKeepStr: '20'))` in options |

## System Design Perspective

**Pipeline scalability:**
- The enterprise pipeline template uses `disableConcurrentBuilds(abortPrevious: true)` — essential for PR pipelines. Without it, every push stacks a new build. With it, only the latest commit's build runs, freeing executors for other jobs.
- Multi-container K8s pods (build container + DinD) scale horizontally. The K8s scheduler places pods across nodes. 100 concurrent builds = 100 pods distributed across the cluster's available nodes automatically.

**Agent/runner architecture trade-offs:**
- K8s pod agents defined via JCasC pod templates give consistent, reproducible environments. The image versions are pinned in the YAML. Drift between agent environments is impossible.
- Multi-container pods (jnlp + build + docker) eliminate the need for Docker-on-host. The DinD container runs its own Docker daemon — privileged, but contained within the pod and destroyed after the build.

**Failure recovery:**
- `waitForQualityGate abortPipeline: true` protects the entire delivery chain. If SonarQube is down, the pipeline blocks until it responds (up to the configured timeout). Set a reasonable timeout to prevent indefinite blocking.
- `cleanWs()` in `post { always {} }` is mandatory. Without it, K8s persistent volumes accumulate workspace data from previous builds. On ephemeral pods, the workspace is lost anyway, but on persistent agents, this causes disk exhaustion.
- The shared library's `kubectl rollout status --timeout=5m` ensures deployment verification. If the rollout doesn't complete in 5 minutes, the pipeline fails and the on-call team is alerted via Slack.

**Caching strategies:**
- Gradle and Maven dependency caches are not preserved in the enterprise template as shown. In production, add a shared cache PVC mounted at `~/.gradle` or `~/.m2`, or configure a Gradle remote build cache / Nexus proxy.
- Docker layer caching in DinD: layers are lost when the pod is destroyed. Add `--cache-from` with a registry-hosted image to preserve build cache between pipeline runs.

**Security boundaries:**
- Credentials injected via `${GITHUB_TOKEN}` from a K8s Secret (not hardcoded in JCasC) means the JCasC YAML can be committed to Git without exposing the token value. The K8s Secret holds the actual value; JCasC YAML holds the reference.
- `submitter: 'senior-engineers,release-managers'` on the production deploy input gate enforces a mandatory human approval by a specific group — cannot be bypassed by the pipeline itself or by non-authorized users.
