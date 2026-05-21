# Platform Engineering for CI/CD

```
Platform Engineering for CI/CD
├── Architecture Internals
│   ├── Controller — UI, scheduling, plugin management
│   ├── Agent types
│   │   ├── JNLP (inbound) — agent initiates TCP to controller:50000
│   │   ├── SSH — controller initiates SSH to agent
│   │   └── K8s pods — plugin creates/destroys pods per job
│   └── Multi-container pods — jnlp + build + docker DinD
├── JCasC Full Configuration
│   ├── SAML securityRealm — enterprise SSO
│   ├── RBAC authorizationStrategy — admin, developer, readonly roles
│   ├── K8s cloud — containerCap, podRetention: never
│   └── Pod templates — security context, nodeSelector, tolerations
├── Shared Libraries — standardPipeline.groovy
│   ├── Full pipeline template — test, ECR build, push, deploy
│   ├── withCredentials ECR login
│   ├── kubectl/helm deploy step
│   └── Slack notification on failure
├── K8s Pod Templates
│   ├── Security context — runAsNonRoot: true, readOnlyRootFilesystem
│   ├── Containers — jnlp (inbound-agent), build (openjdk), docker (DinD)
│   ├── Resource requests/limits — CPU 200m/1, memory 256Mi/2Gi
│   ├── Tolerations — spot-instance node pools
│   └── nodeSelector — workload type targeting
├── Pipeline Observability
│   ├── OpenTelemetry config — OTLP endpoint, traces per stage
│   ├── Grafana Tempo — distributed trace visualization
│   └── PromQL — build duration P99, failure rate by job
├── Cost Optimization
│   ├── Spot instance agents via JCasC — 60-80% cost reduction
│   ├── containerCap — limit max concurrent pods
│   └── podRetention: never — destroy immediately after job
├── OIDC / Keyless Auth
│   ├── WebIdentityTokenCredentialsBinding — AWS STS
│   └── No static AWS credentials in Jenkins
├── GitHub Organization Management
│   └── Terraform GitHub provider — org repos, branch protection, webhooks
└── Key Gotchas
    ├── DinD requires privileged: true (security trade-off)
    ├── Workspace PVC sharing → race conditions
    ├── JNLP container must be named 'jnlp' exactly
    └── K8s API rate limiting on pod create/delete bursts
```

## First Principles

- Platform Engineering for CI/CD means treating Jenkins itself as a product consumed by developer teams. The platform team owns the controller, pod templates, shared libraries, and observability. Dev teams only own their Jenkinsfiles (and ideally just call `standardPipeline()`).
- Spot instance agents (via JCasC K8s cloud with appropriate tolerations) reduce compute cost by 60-80%. The trade-off is interruption risk. Jenkins handles this gracefully — a spot interruption causes the build to fail and retry; it doesn't corrupt the controller.
- OIDC (WebIdentityToken) eliminates static AWS credentials entirely. Jenkins requests a token from the AWS STS, which is bound to the IAM role trust policy. No secret to rotate, no risk of a leaked credential living forever.
- Pipeline Observability (OpenTelemetry traces per stage) makes CI/CD measurable. You can see which stage is the slowest across all pipelines, identify flaky stages by trace error rate, and correlate pipeline slowdowns with infrastructure events.
- `podRetention: never` ensures K8s pod agents are always deleted after the job. This prevents state accumulation, eliminates the risk of a compromised pod being reused, and ensures disk on agent nodes is reclaimed immediately.

## Jenkins Architecture Internals

```
Jenkins Controller (master)
    │
    ├── Job scheduling + orchestration
    ├── Stores build history, artifacts metadata
    ├── Manages agent pool (SSH, JNLP, Kubernetes)
    ├── Web UI + REST API
    └── Plugin ecosystem (~1800 plugins)

Agents (workers)
    │
    ├── JNLP agents: agent initiates outbound TCP to controller
    │       Good for agents behind NAT/firewall
    │
    ├── SSH agents: controller initiates SSH to agent
    │       Good for static, trusted VMs
    │
    └── Kubernetes Pod agents: ephemeral pods per build
            Kubernetes Cloud Plugin provisions pods on demand
            Deleted immediately after build finishes

Workspace:
    $JENKINS_HOME/workspace/<job-name>/   (controller or agent filesystem)
```

***

## Jenkins Configuration as Code (JCasC)

```yaml
# jenkins.yaml — complete declarative configuration
jenkins:
  systemMessage: "Platform Team Managed Jenkins"
  numExecutors: 0    # 0 on controller — all work goes to agents
  
  securityRealm:
    saml:
      idpMetadataUrl: https://sso.company.com/saml/metadata
      displayNameAttributeName: displayName
      groupsAttributeName: groups

  authorizationStrategy:
    roleBased:
      roles:
        global:
        - name: admin
          permissions:
          - Overall/Administer
          assignments:
          - platform-team
        - name: developer
          permissions:
          - Job/Build
          - Job/Read
          - View/Read
          assignments:
          - developers

  clouds:
  - kubernetes:
      name: "kubernetes"
      serverUrl: ""   # empty = use in-cluster config
      namespace: "jenkins-agents"
      jenkinsTunnel: "jenkins-agent.jenkins.svc:50000"
      jenkinsUrl: "http://jenkins.jenkins.svc:8080"
      containerCap: 20
      podRetention: "never"

unclassified:
  globalLibraries:
    libraries:
    - name: "platform-library"
      retriever:
        modernSCM:
          scm:
            git:
              remote: "https://github.com/myorg/jenkins-shared-library"
              credentialsId: "github-app-credentials"
      defaultVersion: "main"
      implicit: true    # auto-import without @Library annotation
```

```bash
# Apply JCasC configuration
kubectl create configmap jenkins-casc \
  --from-file=jenkins.yaml \
  -n jenkins \
  --dry-run=client -o yaml | kubectl apply -f -

# Trigger reload (or enable auto-reload via plugin)
curl -X POST http://jenkins:8080/reload-configuration-as-code/ \
  -u admin:$TOKEN
```

***

## Shared Libraries — Structure and Patterns

```
vars/                     # Global variables and pipeline steps
├── standardPipeline.groovy
├── dockerBuild.groovy
└── deployToKubernetes.groovy

src/                      # Groovy classes
└── com/myorg/ci/
    ├── ImageBuilder.groovy
    └── SlackNotifier.groovy

resources/                # Non-Groovy files (scripts, templates)
└── deploy-template.yaml
```

```groovy
// vars/standardPipeline.groovy — call as standardPipeline(config) in Jenkinsfile
def call(Map config = [:]) {
    def defaults = [
        image:       "ubuntu:22.04",
        runTests:    true,
        pushToECR:   true,
        environment: "staging"
    ]
    config = defaults + config   // caller overrides defaults

    pipeline {
        agent {
            kubernetes {
                yaml """
apiVersion: v1
kind: Pod
spec:
  serviceAccountName: jenkins-agent
  containers:
  - name: docker
    image: docker:24-dind
    securityContext:
      privileged: true
  - name: kubectl
    image: bitnami/kubectl:1.30
    command: [cat]
    tty: true
"""
            }
        }

        environment {
            AWS_REGION  = 'us-east-1'
            ECR_REPO    = "${config.ecrRepo}"
            IMAGE_TAG   = "${env.GIT_COMMIT[0..7]}"
        }

        stages {
            stage('Build') {
                steps {
                    container('docker') {
                        sh """
                            docker buildx build \
                              --cache-from ${ECR_REPO}:cache \
                              --cache-to type=registry,ref=${ECR_REPO}:cache,mode=max \
                              -t ${ECR_REPO}:${IMAGE_TAG} .
                        """
                    }
                }
            }

            stage('Test') {
                when { expression { config.runTests } }
                steps {
                    container('docker') {
                        sh "docker run --rm ${ECR_REPO}:${IMAGE_TAG} pytest tests/ --junitxml=results.xml"
                    }
                }
                post {
                    always {
                        junit 'results.xml'
                    }
                }
            }

            stage('Push') {
                when {
                    expression { config.pushToECR && env.BRANCH_NAME == 'main' }
                }
                steps {
                    container('docker') {
                        withAWS(credentials: 'ecr-credentials', region: AWS_REGION) {
                            sh """
                                aws ecr get-login-password | docker login --username AWS \
                                  --password-stdin ${ECR_REPO}
                                docker push ${ECR_REPO}:${IMAGE_TAG}
                            """
                        }
                    }
                }
            }

            stage('Deploy') {
                steps {
                    container('kubectl') {
                        withKubeConfig([credentialsId: "k8s-${config.environment}"]) {
                            sh "kubectl set image deployment/${config.appName} app=${ECR_REPO}:${IMAGE_TAG} -n ${config.environment}"
                            sh "kubectl rollout status deployment/${config.appName} -n ${config.environment} --timeout=300s"
                        }
                    }
                }
            }
        }

        post {
            failure {
                slackSend(
                    channel: "#builds-${config.team}",
                    color: 'danger',
                    message: "Build failed: ${env.JOB_NAME} #${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)"
                )
            }
        }
    }
}
```

```groovy
// Jenkinsfile — developer's view (3 lines)
@Library('platform-library') _

standardPipeline(
    ecrRepo:    '123456789012.dkr.ecr.us-east-1.amazonaws.com/checkout',
    appName:    'checkout-service',
    team:       'payments',
    environment: 'staging'
)
```

***

## Kubernetes Pod Templates for Agents

```yaml
# PodTemplate YAML used in Kubernetes Cloud plugin
apiVersion: v1
kind: Pod
metadata:
  labels:
    jenkins-agent: "true"
spec:
  serviceAccountName: jenkins-agent
  automountServiceAccountToken: true
  
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 1000

  containers:
  - name: jnlp                          # ALWAYS required — Jenkins JNLP agent
    image: jenkins/inbound-agent:3261.v9c670a_4748a_9
    resources:
      requests: {cpu: "100m", memory: "256Mi"}
      limits: {cpu: "500m", memory: "512Mi"}

  - name: build
    image: ubuntu:22.04
    command: [cat]
    tty: true
    resources:
      requests: {cpu: "500m", memory: "1Gi"}
      limits: {cpu: "2", memory: "4Gi"}
    env:
    - name: HOME
      value: /home/jenkins

  - name: docker
    image: docker:24-dind
    securityContext:
      privileged: true                   # required for Docker-in-Docker
    env:
    - name: DOCKER_TLS_CERTDIR
      value: ""
    volumeMounts:
    - name: docker-sock
      mountPath: /var/run/docker.sock

  volumes:
  - name: docker-sock
    emptyDir: {}

  tolerations:
  - key: "jenkins-agent"
    operator: "Exists"
    effect: "NoSchedule"               # run on dedicated agent node pool

  nodeSelector:
    node-role: ci-agents
```

***

## Pipeline Observability — OpenTelemetry

```groovy
// Emit pipeline traces to OpenTelemetry Collector
// Plugin: opentelemetry-plugin

// jenkins.yaml config
unclassified:
  openTelemetry:
    endpoint: "http://otel-collector.observability.svc:4317"
    exporterType: OTLP
    serviceName: jenkins
    exportInterval: 60
    ignoredSteps:
      - "echo"
      - "sh"                    # don't trace every shell command
```

```bash
# Query build traces in Grafana Tempo
# Trace structure:
#   Pipeline run (root span)
#     └── Stage: Build (child span)
#           └── sh: docker build (leaf span, duration 3m20s)
#     └── Stage: Test
#           └── sh: pytest (leaf span, duration 8m12s)

# PromQL — track build duration trends
histogram_quantile(0.95,
  sum by (le, job_name) (
    rate(jenkins_pipeline_run_duration_seconds_bucket[7d])
  )
)
```

***

## OIDC Authentication — No Stored Secrets

```groovy
// AWS OIDC (GitHub-style, but for Jenkins with AWS credentials plugin)
// Use the AWS Credentials Binding with role assumption

stage('Deploy to Production') {
    steps {
        withCredentials([[
            $class: 'WebIdentityTokenCredentialsBinding',
            credentialsId: 'aws-oidc-prod',
            variable: 'AWS_WEB_IDENTITY_TOKEN_FILE'
        ]]) {
            withEnv([
                'AWS_ROLE_ARN=arn:aws:iam::123456789012:role/jenkins-prod',
                'AWS_REGION=us-east-1'
            ]) {
                sh 'aws sts get-caller-identity'
                sh 'kubectl apply -f manifests/'
            }
        }
    }
}
```

***

## Cost Optimization — Spot Instance Agents

```yaml
# AWS Spot instance for Jenkins agents via EC2 Fleet Plugin
# In JCasC:
clouds:
- amazonEC2:
    name: "spot-agents"
    region: "us-east-1"
    templates:
    - ami: "ami-ubuntu-22-04-jenkins"
      instanceType: "m5.2xlarge"
      spotConfig:
        spotBlockReservation: 0    # no block, pure spot
        useBidPrice: false         # use on-demand as max bid
      numExecutors: 4
      labelString: "spot-linux"
      initScript: |
        #!/bin/bash
        apt-get update -q
        apt-get install -y docker.io
        usermod -aG docker jenkins
      stopOnTermination: true     # gracefully stop build on spot interruption
      idleTerminationMinutes: 5   # terminate idle agents after 5 minutes
```

***

## GitHub Organization Terraform Provider

```hcl
resource "github_repository" "service" {
  for_each    = var.services
  name        = each.key
  description = each.value.description
  visibility  = "private"
  auto_init   = true

  template {
    owner      = "myorg"
    repository = "service-template"
  }
}

resource "github_branch_protection" "main" {
  for_each      = var.services
  repository_id = github_repository.service[each.key].node_id
  pattern       = "main"

  required_status_checks {
    strict   = true
    contexts = ["ci/build", "ci/test", "ci/security-scan"]
  }

  required_pull_request_reviews {
    required_approving_review_count = 2
    dismiss_stale_reviews           = true
    require_code_owner_reviews      = true
  }
}

resource "github_team_repository" "owners" {
  for_each   = var.services
  team_id    = github_team.service_teams[each.key].id
  repository = github_repository.service[each.key].name
  permission = "push"
}
```

***

## Key Gotchas

| Gotcha | Detail |
|--------|--------|
| Shared library `@Library` version | Without `@main` suffix, Jenkins uses the defaultVersion from the library config — pin to a tag in production |
| Kubernetes Pod agent `jnlp` container | Must always be present and match the Jenkins inbound-agent version; version mismatch = agent won't connect |
| `container('name')` scope | The `container()` block only applies within that closure — subsequent `sh` steps outside run in `jnlp` container |
| Spot instance interruption during build | EC2 Fleet/Spot plugin sends SIGTERM but Jenkins doesn't checkpoint — build is lost; use idempotent scripts |
| JCasC reload wipes unsaved UI config | Any config done in the Jenkins UI (not in JCasC YAML) is overwritten on reload — JCasC must be the single source of truth |
| Pipeline `when` on `agent none` | `when` conditions are evaluated before `agent` allocation; use `beforeAgent: true` to skip agent spin-up |
| Parallel branches share workspace | In `parallel {}`, all branches run on the same agent workspace unless `agent` is specified per branch |
| `withCredentials` leaks to subprocesses | Jenkins masks credentials in logs but they ARE visible in `/proc/<pid>/environ` — use vault sidecar for high-sensitivity builds |
