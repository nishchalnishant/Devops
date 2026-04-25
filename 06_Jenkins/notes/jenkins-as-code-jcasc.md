---
description: Jenkins Configuration as Code (JCasC), Declarative Pipeline patterns, shared libraries, and enterprise CI/CD architecture for senior engineers.
---

# Jenkins — JCasC & Pipeline Architecture Patterns

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
