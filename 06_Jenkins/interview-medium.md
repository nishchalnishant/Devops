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

---


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
