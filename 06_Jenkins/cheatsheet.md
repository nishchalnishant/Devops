# Jenkins Cheatsheet

## Pipeline DSL Quick Reference

### Top-Level Blocks

```groovy
pipeline {
    agent { label 'linux && docker' }   // Required: where to run
    environment { KEY = 'value' }        // Build-wide env vars
    parameters { ... }                   // UI-exposed inputs
    options { ... }                      // Build behavior settings
    triggers { ... }                     // Automatic build triggers
    tools { maven 'maven-3.9' }         // Auto-install tools
    stages { ... }                       // Required: stage containers
    post { ... }                         // Post-build actions
}
```

### agent Variants

```groovy
agent any                               // Any available executor
agent none                              // Declare per-stage
agent { label 'gpu && linux' }         // Label expression
agent {
    docker { image 'node:20-alpine' }   // Docker container
}
agent {
    kubernetes {                        // Kubernetes pod
        yaml '''
spec:
  containers:
  - name: jnlp
    image: jenkins/inbound-agent:latest
'''
    }
}
```

### Stage and Steps

```groovy
stage('Name') {
    agent { ... }           // Override agent for this stage
    when { ... }            // Conditional execution
    options {
        timeout(time: 10, unit: 'MINUTES')
        retry(3)
    }
    steps {
        sh 'echo hello'
        bat 'echo hello'    // Windows
        script { ... }      // Groovy scripting block inside Declarative
    }
    post { ... }            // Stage-level post
}
```

### Common Steps

```groovy
sh 'command'                            // Shell command
sh(script: 'cmd', returnStdout: true)  // Capture output
bat 'command'                           // Windows command
echo 'message'                          // Print message
error 'message'                         // Fail the build
checkout scm                            // Checkout from configured SCM
git url: 'https://...', branch: 'main' // Explicit git checkout
dir('/path') { sh '...' }             // Change directory for steps
withEnv(['VAR=val']) { ... }           // Scoped env override
timeout(time: 5, unit: 'MINUTES') { } // Timeout block
retry(3) { sh 'flaky-command' }        // Retry on failure
sleep(time: 30, unit: 'SECONDS')       // Wait
input(message: 'Proceed?', ok: 'Yes') // Manual gate
readFile('path/to/file')               // Read file content
writeFile(file: 'out.txt', text: '..') // Write file
stash(name: 'artifacts', includes: 'build/**/*')  // Save files
unstash('artifacts')                    // Restore saved files
archiveArtifacts(artifacts: 'build/**/*.jar', fingerprint: true)
junit('**/test-results/**/*.xml')
publishHTML([reportDir: 'coverage', reportFiles: 'index.html', reportName: 'Coverage'])
cleanWs()                               // Clean workspace
```

### post Block Conditions

```groovy
post {
    always   { }    // Always runs
    success  { }    // Only on SUCCESS
    failure  { }    // Only on FAILURE
    unstable { }    // Only on UNSTABLE (test failures)
    changed  { }    // When status changes from previous build
    fixed    { }    // Previous FAILURE, now SUCCESS
    regression { }  // Previous SUCCESS, now FAILURE
    aborted  { }    // Build was cancelled
    cleanup  { }    // Runs last, after all other post conditions
}
```

### when Conditions

```groovy
when {
    branch 'main'                           // Branch name match
    branch pattern: 'release/*', comparator: 'GLOB'
    tag 'v*'                                // Tag match
    environment name: 'ENV', value: 'prod' // Env var value
    expression { params.DEPLOY == true }    // Groovy expression
    not { branch 'main' }                   // Negate
    allOf {                                 // AND
        branch 'main'
        environment name: 'CI', value: 'true'
    }
    anyOf {                                 // OR
        branch 'main'
        branch 'release/*'
    }
    changeRequest()                         // PR/change request build
    triggeredBy 'TimerTrigger'             // Triggered by cron
}
```

### parameters Types

```groovy
parameters {
    string(name: 'VERSION', defaultValue: '1.0.0', description: 'Release version')
    booleanParam(name: 'SKIP_TESTS', defaultValue: false, description: 'Skip tests')
    choice(name: 'ENV', choices: ['dev', 'staging', 'prod'], description: 'Target env')
    text(name: 'RELEASE_NOTES', defaultValue: '', description: 'Changelog')
    password(name: 'API_KEY', defaultValue: '', description: 'External API key')
    file(name: 'CONFIG', description: 'Upload config file')
}

// Access in pipeline:
params.VERSION
params.SKIP_TESTS
```

### options Catalog

```groovy
options {
    timeout(time: 30, unit: 'MINUTES')
    retry(3)
    buildDiscarder(logRotator(numToKeepStr: '20', artifactNumToKeepStr: '5'))
    disableConcurrentBuilds(abortPrevious: true)
    skipDefaultCheckout()
    timestamps()
    ansiColor('xterm')
    parallelsAlwaysFailFast()           // failFast for all parallel stages
    skipStagesAfterUnstable()           // Stop on unstable
    preserveStashes(buildCount: 5)      // Keep stashes for n builds
}
```

### triggers

```groovy
triggers {
    pollSCM('H/5 * * * *')         // Poll SCM every 5 min (H = hash spread)
    cron('H 2 * * 1-5')            // Nightly Mon-Fri around 2am
    upstream(upstreamProjects: 'other-job', threshold: hudson.model.Result.SUCCESS)
}
```

### environment — Credentials Binding

```groovy
environment {
    // Bind username/password as env vars
    DOCKER_CREDS = credentials('dockerhub-creds')
    // Expands to: DOCKER_CREDS_USR, DOCKER_CREDS_PSW
}
```

---

## Credentials Usage

### withCredentials Binding Types

```groovy
withCredentials([
    // Username + password
    usernamePassword(
        credentialsId: 'nexus-creds',
        usernameVariable: 'NEXUS_USER',
        passwordVariable: 'NEXUS_PASS'
    ),
    // Secret text / API token
    string(credentialsId: 'slack-token', variable: 'SLACK_TOKEN'),
    // SSH private key
    sshUserPrivateKey(
        credentialsId: 'deploy-key',
        keyFileVariable: 'SSH_KEY',
        usernameVariable: 'SSH_USER'
    ),
    // Secret file (e.g., kubeconfig)
    file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG'),
    // Certificate (JKS/PFX)
    certificate(
        credentialsId: 'tls-cert',
        keystoreVariable: 'KS_FILE',
        passwordVariable: 'KS_PASS'
    )
]) {
    sh 'docker login -u $NEXUS_USER -p $NEXUS_PASS registry.example.com'
    sh 'kubectl --kubeconfig=$KUBECONFIG apply -f deploy.yaml'
}
```

### HashiCorp Vault

```groovy
withVault(
    configuration: [vaultUrl: 'https://vault.example.com', vaultCredentialId: 'vault-approle'],
    vaultSecrets: [
        [path: 'secret/myapp/db', secretValues: [
            [envVar: 'DB_PASSWORD', vaultKey: 'password'],
            [envVar: 'DB_HOST',     vaultKey: 'host']
        ]]
    ]
) {
    sh 'psql -h $DB_HOST -U myapp -c "SELECT 1"'
}
```

---

## Parallel Stages

### Basic Parallel

```groovy
stage('Parallel Tests') {
    parallel {
        stage('Unit') {
            steps { sh 'pytest tests/unit' }
        }
        stage('Integration') {
            steps { sh 'pytest tests/integration' }
        }
        stage('E2E') {
            agent { label 'e2e-agent' }
            steps { sh 'npx playwright test' }
        }
    }
}
```

### failFast — Stop All on First Failure

```groovy
stage('Parallel Tests') {
    failFast true
    parallel {
        stage('Unit')        { steps { sh 'npm run test:unit' } }
        stage('Integration') { steps { sh 'npm run test:int' } }
    }
}
```

### Dynamic Parallel (Scripted)

```groovy
def parallelBranches = [:]
['us-east-1', 'eu-west-1', 'ap-southeast-1'].each { region ->
    parallelBranches["Deploy ${region}"] = {
        sh "helm upgrade --install myapp ./chart --set region=${region}"
    }
}
parallel parallelBranches
```

---

## Shared Library Import

```groovy
// Load from global library (registered in Jenkins)
@Library('company-lib') _

// Load specific version (tag/commit)
@Library('company-lib@v2.1.0') _

// Load multiple libraries
@Library(['company-lib@v2.1.0', 'security-lib@v1.0.0']) _

// Load from a specific Git repo inline (useful for testing)
library identifier: 'local-lib@main',
        retriever: modernSCM([$class: 'GitSCMSource',
                               remote: 'https://github.com/org/jenkins-lib.git',
                               credentialsId: 'github-token'])
```

---

## Useful Groovy Snippets

### Capture Shell Output

```groovy
script {
    def version = sh(script: 'cat VERSION', returnStdout: true).trim()
    def gitHash  = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
    def exitCode = sh(script: 'test -f Dockerfile', returnStatus: true)
    if (exitCode != 0) { error 'Dockerfile not found' }
    env.VERSION  = version
    env.GIT_HASH = gitHash
}
```

### Read/Write Files

```groovy
script {
    def config = readYaml(file: 'config.yaml')
    def tag    = config.image.tag
    writeYaml(file: 'deploy.yaml', data: [image: [tag: tag]])

    def pkgJson = readJSON(file: 'package.json')
    echo "Building version: ${pkgJson.version}"
}
```

### HTTP Requests

```groovy
script {
    def response = httpRequest(
        url: 'https://api.example.com/deploy',
        httpMode: 'POST',
        contentType: 'APPLICATION_JSON',
        requestBody: """{"version": "${env.VERSION}"}""",
        authentication: 'api-creds'
    )
    if (response.status != 200) { error "Deploy API returned ${response.status}" }
}
```

### Conditional Failure

```groovy
script {
    def result = sh(script: './run-tests.sh', returnStatus: true)
    if (result != 0) {
        currentBuild.result = 'UNSTABLE'
        // Don't throw — continue to post block for reports
    }
}
```

---

## Jenkinsfile Templates

### Multi-Branch Pipeline Template

```groovy
@Library('company-lib@v2.0.0') _

pipeline {
    agent { label 'k8s-agent' }

    options {
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '20'))
        disableConcurrentBuilds(abortPrevious: true)
        timestamps()
    }

    environment {
        IMAGE_TAG = "${env.BRANCH_NAME}-${env.GIT_COMMIT[0..7]}"
        REGISTRY  = 'registry.example.com'
    }

    stages {
        stage('CI') {
            parallel {
                stage('Test')  { steps { sh 'make test' } }
                stage('Lint')  { steps { sh 'make lint' } }
                stage('Build') { steps { sh 'make build' } }
            }
        }

        stage('Push') {
            when { anyOf { branch 'main'; branch 'release/*' } }
            steps {
                withCredentials([usernamePassword(credentialsId: 'registry-creds',
                                                   usernameVariable: 'U', passwordVariable: 'P')]) {
                    sh 'docker login -u $U -p $P $REGISTRY'
                    sh 'docker push $REGISTRY/myapp:$IMAGE_TAG'
                }
            }
        }

        stage('Deploy') {
            when { branch 'main' }
            steps {
                input message: 'Deploy to production?', submitter: 'release-team'
                sh 'helm upgrade --install myapp ./chart --set image.tag=$IMAGE_TAG'
            }
        }
    }

    post {
        failure {
            slackSend channel: '#ci-alerts', color: 'danger',
                      message: "FAILED: ${env.JOB_NAME} ${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)"
        }
        always { cleanWs() }
    }
}
```

### PR-Triggered Pipeline Template

```groovy
pipeline {
    agent { label 'k8s-agent' }

    options {
        timeout(time: 20, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '5'))
    }

    triggers {
        // GitHub: configure webhook to send pull_request events
        // GitLab: configure webhook for merge_request events
    }

    stages {
        stage('Validate PR') {
            steps {
                sh 'make test lint'
            }
        }

        stage('Security Scan') {
            steps {
                sh 'trivy fs --exit-code 1 --severity HIGH,CRITICAL .'
                sh 'semgrep --config=auto --error .'
            }
        }

        stage('Comment Results') {
            steps {
                script {
                    // Post test results as a PR comment via API
                    def prNumber = env.CHANGE_ID
                    sh """
                    curl -s -X POST -H 'Authorization: token \$GITHUB_TOKEN' \
                      https://api.github.com/repos/org/repo/issues/${prNumber}/comments \
                      -d '{"body": "CI passed: ${env.BUILD_URL}"}'
                    """
                }
            }
        }
    }
}
```

### Release Pipeline Template

```groovy
@Library('company-lib@v2.0.0') _

pipeline {
    agent { label 'k8s-agent' }

    parameters {
        string(name: 'VERSION', description: 'Release version (e.g. 1.2.3)')
        choice(name: 'TARGET', choices: ['staging', 'production'])
    }

    stages {
        stage('Validate') {
            steps {
                script {
                    if (!params.VERSION.matches(/\d+\.\d+\.\d+/)) {
                        error "VERSION must be semver format (1.2.3), got: ${params.VERSION}"
                    }
                }
            }
        }

        stage('Tag') {
            steps {
                sh "git tag -a v${params.VERSION} -m 'Release ${params.VERSION}'"
                sh "git push origin v${params.VERSION}"
            }
        }

        stage('Build & Scan') {
            steps {
                sh "docker build -t registry.example.com/myapp:${params.VERSION} ."
                sh "trivy image --exit-code 1 --severity HIGH,CRITICAL registry.example.com/myapp:${params.VERSION}"
                sh "cosign sign registry.example.com/myapp:${params.VERSION}"
                sh "docker push registry.example.com/myapp:${params.VERSION}"
            }
        }

        stage('Deploy') {
            steps {
                input message: "Deploy v${params.VERSION} to ${params.TARGET}?", submitter: 'release-team'
                sh "helm upgrade --install myapp ./chart --namespace ${params.TARGET} --set image.tag=${params.VERSION}"
                sh "./scripts/smoke-test.sh https://${params.TARGET}.example.com"
            }
        }

        stage('Release Notes') {
            steps {
                sh "gh release create v${params.VERSION} --generate-notes --title 'v${params.VERSION}'"
            }
        }
    }

    post {
        failure {
            slackSend channel: '#releases', color: 'danger',
                      message: "Release v${params.VERSION} FAILED: <${env.BUILD_URL}|Build>"
        }
        success {
            slackSend channel: '#releases', color: 'good',
                      message: "Released v${params.VERSION} to ${params.TARGET} :rocket:"
        }
    }
}
```

---

## Quick Reference Table

| Task | Snippet |
|------|---------|
| Get git short SHA | `sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()` |
| Skip build on `[ci skip]` | `when { not { changeRequest() }; expression { !currentBuild.rawBuild.getCause(hudson.model.Cause$UserIdCause) } }` |
| Set build name | `currentBuild.displayName = "#${BUILD_NUMBER} - v${VERSION}"` |
| Set build description | `currentBuild.description = "Deployed to ${TARGET_ENV}"` |
| Mark unstable (not failed) | `currentBuild.result = 'UNSTABLE'` |
| Read env variable | `env.BRANCH_NAME`, `env.BUILD_NUMBER`, `env.GIT_COMMIT` |
| Lock resource | `lock(resource: 'staging-db') { sh '...' }` |
| Replay last build | Jenkins UI → Build → Replay (editable Groovy) |
| Script console | **Manage Jenkins → Script Console** |
| Validate Jenkinsfile | `curl -X POST -F "jenkinsfile=<Jenkinsfile" https://jenkins/pipeline-model-converter/validate` |

## Built-in Environment Variables

| Variable | Value |
|----------|-------|
| `BUILD_NUMBER` | Build number (integer string) |
| `BUILD_URL` | Full URL of the build |
| `JOB_NAME` | Job name (folder/job) |
| `WORKSPACE` | Absolute path to workspace |
| `BRANCH_NAME` | Branch (multibranch pipelines) |
| `CHANGE_ID` | PR/MR number (multibranch PR builds) |
| `GIT_COMMIT` | Full git SHA |
| `GIT_BRANCH` | Branch name with remote prefix |
| `NODE_NAME` | Agent name running the build |
| `EXECUTOR_NUMBER` | Executor slot number on the agent |
# Content from CheatSheet_Jenkins.pdf

## Page 1

Command
Description
sudo apt install openjdk-17-jre
Installs OpenJDK 17 runtime environment.
java -version
Verifies the installation of Java.
Shubham
TrainWith
Jenkins-Cheatsheet
Cheatsheet for DevOps Engineers
Jenkins Installaton and Setup:
1.1 Install Java:
Jenkins requires Java to run. Install OpenJDK 17:
1.2 Install Jenkins:
Command
Description
sudo apt-get install -y ca-certificates curl gnupg
Installs dependencies for Jenkins.
curl -fsSL
https://pkg.jenkins.io/debian/jenkins.io-
2023.key | sudo tee /usr/share/keyrings/jenkins-
keyring.asc >
/dev/null
Downloads the Jenkins GPG key and saves
it to the system's keyring for package
verification.
echo deb [signed-
by=/usr/share/keyrings/jenkins-
keyring.asc] https://pkg.jenkins.io/debian binary/
| sudo tee /etc/apt/sources.list.d/jenkins.list >
/dev/null
Adds the Jenkins package repository to
APT sources, enabling Jenkins installation
via APT.
sudo apt-get update
Updates the package list.
sudo apt-get install jenkins
Installs Jenkins.
sudo systemctl enable jenkins
Enables Jenkins to start at boot.
sudo systemctl start jenkins
Starts Jenkins.
sudo systemctl status jenkins
Checks Jenkins service status.
Shubham
TrainWith
Shubham
TrainWith


---

## Page 2

Shubham
TrainWith
Shubham
TrainWith
1.3 Access Jenkins in a Browser:
Jenkins runs on port 8080.
Modify your EC2 instance’s security group to allow inbound traffic on port 8080.
Access Jenkins at http://<instance-public-ip>:8080.
1.4 Unlock Jenkins:
Command
Description
sudo cat
/var/lib/jenkins/secrets/initialAdminPassword
Retrieves the initial admin password.
1.5 Install Suggested Plugins:
After unlocking Jenkins, select "Install Suggested Plugins" for essential tools.
1.6 Create an Admin User:
Set a username and password for the admin account during the setup process.
Jenkins Common Commands:
Command
Description
sudo systemctl start jenkins
Starts Jenkins.
sudo systemctl stop jenkins
Stops Jenkins.
sudo systemctl restart jenkins
Restarts Jenkins.
sudo systemctl status jenkins
Displays Jenkins service status.
sudo systemctl enable jenkins
Enables Jenkins to start at boot.
sudo systemctl disable jenkins
Disables Jenkins from starting at boot.
tail -f /var/log/jenkins/jenkins.log
Views Jenkins logs in real-time.
jenkins --version
Displays Jenkins version.


---

## Page 3

Shubham
TrainWith
Jenkins Pipeline Syntax & Examples:
Declarative Pipeline Example
 pipeline {
     agent any
     stages {
         stage('Build') {
             steps {
                 sh 'echo "Building the project..."'
             }
         }
         stage('Test') {
             steps {
                 sh 'echo "Running tests..."'
             }
         }
         stage('Deploy') {
             steps {
                 sh 'echo "Deploying the application..."'
             }
         }
     }
 }
Key Pipeline Commands:
Command
Description
pipeline {}
Declares a Jenkins pipeline.
node
Defines where the pipeline runs.
stage {}
Defines a pipeline stage.
sh "command"
Executes shell commands in the pipeline.


---

## Page 4

Shubham
TrainWith
Command
Description
checkout scm
Checks out source code.
archiveArtifacts
Archives build artifacts.
input
Pauses pipeline for manual input.
when
Adds conditional steps to stages.
parallel
Executes stages in parallel.
Jenkins Security Configuration:
Step
Description
Enable CSRF Protection
Protect against cross-site request forgery.
Set Authorization
Use matrix-based or project-based security.
Authentication
Use Jenkins’ user database or external
providers like LDAP.
Jenkins Plugins:
Plugin
Description
Git Plugin
Integrates Git repositories with Jenkins.
Docker Plugin
Manages Docker builds and deployments.
Pipeline Plugin
Enables Jenkins pipeline syntax.
GitHub Plugin
Integrates with GitHub for webhooks and PRs.
Maven Plugin
Automates Maven builds and deployments.
SonarQube Plugin
Integrates code quality checks.
Slack Notification Plugin
Sends build notifications to Slack channels.
Shubham
TrainWith
Shubham
TrainWith


---

## Page 5

Shubham
TrainWith
6. Backup & Restore:
Step
Description
Backup Jenkins
Copy /var/lib/jenkins to a backup location.
Restore Jenkins
Copy the backup back to /var/lib/jenkins.
Best Practices:
Keep Jenkins Updated: Regularly update Jenkins to avoid vulnerabilities.
1.
Use Declarative Pipelines: Improve readability and maintainability.
2.
Limit Plugins: Install only necessary plugins to reduce performance overhead.
3.
Version Control Pipelines: Store Jenkinsfile in repositories.
4.
Automate Backups: Schedule regular backups of configuration and jobs.
5.
Secure Credentials: Use the Jenkins credentials store for secrets
management.
6.
Troubleshooting:
Term
Description
Pipeline Failure
Check logs and use sh "echo ..." to debug.
Agent Not Connecting
Verify SSH keys, network settings, and agent
configurations.
Permission Denied
Ensure Jenkins has access to required
directories and files.


---

