# Production Scenarios & Troubleshooting Drills (Senior Level)

### Scenario 1: The "Zombie" Jenkins Build
**Problem:** A build won't stop even when aborted.
**Fix:** Use the Jenkins Script Console to find the thread and force-kill it via Groovy.

### Scenario 2: Shared Library Versioning Disaster
**Problem:** A global library update broke 50 pipelines.
**Fix:** Always tag shared libraries. Use `@Library('my-lib@v1.2.0')` in the Jenkinsfile to pin versions.

### Scenario 3: Jenkins-as-Code (JCasC) Synchronization
**Problem:** You changed a setting in the UI, but it disappeared after a restart.
**Fix:** You are using JCasC. UI changes are ephemeral. You must update the `jenkins.yaml` configuration file and reload it to make changes permanent.

### Scenario 4: Master Node OOM (Java Heap)
**Problem:** Jenkins UI is slow or crashing under heavy load.
**Diagnosis:** Check JVM heap usage. Jenkins is likely running out of memory because it's storing too much build history.
**Fix:** Set "Discard Old Builds" on all jobs and increase `Xmx` in `/etc/default/jenkins`.

## Scenario 1: Pipeline Hangs Indefinitely on a Build Step

**Situation**: A Jenkins pipeline has been "Running" for 4 hours on the `sh 'mvn package'` step. The build should take 10 minutes.

**Diagnosis**:
```bash
# In Jenkins UI: check the console output for the hung step
# Look for: Maven waiting for user input, network timeout, deadlock

# On the agent node:
ps aux | grep mvn          # is the process running or zombie?
lsof -p <pid> | grep LISTEN  # waiting on a port?
strace -p <pid>            # what syscall is it blocking on?
```

**Resolution**:
1. Add `timeout` to the stage to auto-fail hung builds:
```groovy
stage('Build') {
  options { timeout(time: 20, unit: 'MINUTES') }
  steps { sh 'mvn package -B' }  # -B = batch mode (no interactive prompts)
}
```
2. Add `-B` (batch mode) to Maven — it prevents interactive prompts that hang CI
3. Check if the agent lost connectivity to a remote resource (Nexus, artifact repo) — add retry logic

---

## Scenario 2: Jenkins Controller Out of Disk Space

**Situation**: Builds start failing with "No space left on device". The Jenkins controller disk is full.

**Diagnosis**:
```bash
df -h /var/jenkins_home
du -sh /var/jenkins_home/jobs/*/builds/* | sort -rh | head -20
```

**Resolution**:
1. **Immediate**: Clean up old build history
```groovy
// Add to pipeline to auto-discard old builds
options {
  buildDiscarder(logRotator(numToKeepStr: '20', artifactNumToKeepStr: '5'))
}
```
2. **Workspace cleanup**: Use `cleanWs()` in `post { always { cleanWs() } }` to delete workspaces after build
3. **Long-term**: Move Jenkins home to a larger volume; configure build discarder globally via JCasC

---

## Scenario 3: Flaky Tests Causing Pipeline Instability

**Situation**: The pipeline fails ~20% of builds due to intermittent test failures, not real bugs.

**Resolution strategy**:
1. **Identify flaky tests**: `junit testResults: '**/test-results/*.xml'` with trend view shows which tests flip
2. **Quarantine**: Move known-flaky tests to a separate suite tagged `@Flaky`; run that suite separately and don't fail the pipeline on it
3. **Retry at test level**: Use pytest-retry, JUnit RerunFailingTestsCount, or retry the full test stage once:
```groovy
stage('Test') {
  steps {
    retry(2) { sh 'pytest tests/ --tb=short' }
  }
}
```
4. **Root cause**: Most flakiness is timing-dependent (async tests, sleep-based assertions) or environment-dependent (port conflicts on shared agents). Switch to dedicated K8s pod agents to eliminate shared state.

---

## Scenario 4: Shared Library Change Breaks All Pipelines

**Situation**: A developer updated the shared library's `vars/deployApp.groovy` and it broke the `deployApp()` call in 50 pipelines.

**Prevention**:
1. **Version pin libraries**: `@Library('my-shared-lib@v1.2.0') _` — pin to a tag, not `main`
2. **Separate test pipeline**: Have a pipeline that runs against a `dev` branch of the library and validates it against a canary application before merging
3. **Semantic versioning**: Treat the shared library as a package — breaking changes increment major version

**Recovery**:
```groovy
// Immediately revert the library to previous tag
// Then all pipelines that pin to a version are unaffected
// Pipelines using @main are affected — this is why pinning is mandatory
```

---

## Scenario 5: Agent Pods Not Starting in Kubernetes

**Situation**: Jenkins jobs queue up but Kubernetes agent pods never start. Jobs show "Waiting for next available executor".

**Diagnosis**:
```bash
kubectl get pods -n jenkins
kubectl describe pod <jenkins-agent-pod> -n jenkins
# Common: ImagePullBackOff, Insufficient cpu, PVC not bound
kubectl get events -n jenkins --sort-by=.lastTimestamp
```

**Resolution by cause**:
- **ImagePullBackOff**: Fix image name/tag in Kubernetes plugin pod template; add `imagePullSecrets` for private registries
- **Insufficient resources**: Reduce agent container CPU/memory requests; add nodes to cluster
- **JNLP connection refused**: Ensure the agent can reach the Jenkins controller on port 50000 (JNLP port); check NetworkPolicy
- **Plugin version mismatch**: `jenkins/inbound-agent` image version must match Jenkins controller version

---

## Scenario 6: Pipeline Runs Correctly Locally but Fails in Jenkins

**Situation**: `./gradlew build` works on a developer's machine but fails in the Jenkins pipeline with "JAVA_HOME not set".

**Root cause pattern**: Agents have different environments than developer machines. Missing: tool installations, PATH configuration, environment variables.

**Resolution**:
```groovy
pipeline {
  tools {
    jdk 'jdk-21'    // references a JDK configured in Jenkins Global Tool Configuration
    maven 'mvn-3.9'
  }
  environment {
    // Explicitly set anything the build needs
    GRADLE_OPTS = '-Xmx2g -Dfile.encoding=UTF-8'
  }
}
```

Or use Docker agents to make the build environment completely explicit:
```groovy
agent {
  docker { image 'gradle:8.5-jdk21' }
}
```

Docker agents eliminate "works on my machine" — the build environment is the same everywhere.

---

## Scenario 7: Build Queue Congestion
**Symptom:** Jenkins has 500 jobs in the queue, but plenty of idle agents.
**Diagnosis:** 
1. Check "Label" mismatch. The jobs are restricted to a label that has no agents.
2. Check the "Max concurrent builds" limit on the jobs.
3. Check the "Node provisioning" rate in the Cloud plugin (e.g., EC2/K8s).
**Fix:** Correct the labels or increase the cloud provisioning throughput.

## Scenario 8: The "Sandbox" Security Breach
**Symptom:** A pipeline fails with `Scripts not permitted to use method ...`.
**Diagnosis:** Jenkins script security sandbox is blocking an insecure Groovy method call in a shared library or Jenkinsfile.
**Fix:** 
1. Use an approved alternative method.
2. An admin can approve the script in "Manage Jenkins" -> "In-process Script Approval" (Use with extreme caution).

## Scenario 9: GitHub Webhook "Trigger Storm"
**Symptom:** Jenkins freezes or CPU spikes to 100% after a large PR with many commits is merged.
**Diagnosis:** The GitHub webhook is triggering a build for every commit or every branch update, overloading the controller's indexing thread.
**Fix:** 
1. Use "GitHub Organization Folder" with "Suppress automatic SCM triggering".
2. Use "Generic Webhook Trigger" with filters to only trigger on specific events (e.g., PR opened/merged).

---

### Scenario 4: Shared Library Version Drift Breaks All Pipelines

**Problem:** A Jenkins shared library used by 300 pipelines is updated. The next day, 60 pipelines that ran overnight are broken. The change was supposedly backward-compatible.

**Diagnosis:**
```groovy
// Pipelines using implicit latest version — no version pin
@Library('my-shared-lib') _   // pulls from default branch — dangerous

// Check which library version ran in a build
// Jenkins Build → Replay → shows the version used
```

**Root cause:** The shared library `@Library('my-shared-lib')` without `@version` annotation pulls from the default branch. An update to `vars/deploy.groovy` changed a parameter name — any pipeline passing the old parameter name silently ignored it, causing silent failures rather than errors.

**Fix:**

1. **Pin library versions in pipelines:**
```groovy
@Library('my-shared-lib@v2.3.1') _
```

2. **Use semantic versioning with Git tags on the shared library repo.**

3. **Implement a library compatibility contract — don't remove parameters, only add with defaults:**
```groovy
def deploy(Map config = [:]) {
    def target   = config.target   ?: config.environment  // backward compat alias
    def image    = config.image    ?: error("image is required")
}
```

4. **Canary-test library changes:** Create a `library-testing` Jenkins folder that always pulls from the library's feature branch, using a single test pipeline. Only merge to main after that test passes.

---

### Scenario 5: Jenkins Agents Running Out of Disk During Docker Builds

**Problem:** Jenkins agents fail intermittently with "no space left on device" during Docker builds. The problem gets worse each week.

**Diagnosis:**
```bash
# On the agent VM
df -h /var/jenkins/workspace
docker system df
docker images --filter dangling=true | wc -l
```

**Root causes:**
1. Docker build cache accumulating on agents — every pipeline build adds layers
2. Jenkins workspaces not cleaned after builds (`deleteDir()` not called)
3. Docker volumes from test containers not removed after test stage

**Fix — comprehensive cleanup pipeline step:**
```groovy
pipeline {
    agent any
    options {
        // Auto-delete workspace after build
        skipDefaultCheckout(false)
    }
    post {
        always {
            // Clean workspace
            cleanWs()
            // Clean Docker artifacts
            sh '''
                docker system prune -f --filter "until=24h"
                docker volume prune -f
            '''
        }
    }
}
```

**Proactive agent maintenance — scheduled Groovy script in Jenkins Script Console:**
```groovy
// Run via "Manage Jenkins → Script Console" or a scheduled job
Jenkins.instance.nodes.each { node ->
    node.createLauncher(TaskListener.NULL).launch()
}
```

**Long-term:** Use ephemeral cloud agents (Kubernetes plugin or EC2 plugin). Each build gets a fresh agent pod/VM; disk state doesn't persist between builds. No disk management needed.

---

### Scenario 6: Pipeline Succeeds but Deployment Never Happens — Silent Skip

**Problem:** A multi-stage pipeline passes all stages and shows green. But the production deployment didn't happen. No errors anywhere.

**Diagnosis:**
```groovy
// Check the `when` conditions on the deploy stage
stage('Deploy to Production') {
    when {
        branch 'main'
        // If the branch name doesn't exactly match, this stage is SKIPPED (not failed)
    }
}
```

**Common silent-skip causes:**

1. **Branch condition mismatch:** Pipeline triggered from a PR branch (`feature/xyz`) but `when { branch 'main' }` only matches the literal string `main`. PRs run against `CHANGE_BRANCH`, not `BRANCH_NAME`. Use `when { branch pattern: 'main', comparator: 'EQUALS' }` or check both:
```groovy
when {
    anyOf {
        branch 'main'
        environment name: 'DEPLOY_OVERRIDE', value: 'true'
    }
}
```

2. **`expression` returning null instead of false:**
```groovy
when {
    expression { return env.RUN_DEPLOY == 'true' }
    // If RUN_DEPLOY is unset, env.RUN_DEPLOY is null — null is truthy in Groovy, not false!
    // Fix:
    expression { return env.RUN_DEPLOY?.toBoolean() }
}
```

3. **Stage wrapped in a condition that's never true:** Add explicit logging:
```groovy
stage('Deploy') {
    steps {
        echo "Branch: ${env.BRANCH_NAME}, RUN_DEPLOY: ${env.RUN_DEPLOY}"
        sh './deploy.sh'
    }
}
```

---

### Scenario 7: Parallel Stage Causing Intermittent Build Failures — Race Condition

**Problem:** A pipeline with `parallel` stages that run integration tests fails randomly — sometimes on `test-suite-1`, sometimes `test-suite-2`. Running either suite alone always passes.

**Diagnosis:**
```groovy
parallel {
    'test-suite-1': {
        sh 'pytest tests/suite1/'
    },
    'test-suite-2': {
        sh 'pytest tests/suite2/'
    }
}
```

**Root causes:**

1. **Shared database — test isolation failure:** Both suites write to the same database (same schema, same test fixtures). Suite 1's teardown deletes rows that Suite 2 is reading. Fix: each suite uses an isolated DB or schema:
```groovy
'test-suite-1': {
    sh 'DATABASE_URL=postgresql://localhost/test_suite1 pytest tests/suite1/'
},
```

2. **Shared port — both suites start a test server on port 8080:**
```groovy
'test-suite-1': {
    sh 'TEST_PORT=8081 pytest tests/suite1/'
},
'test-suite-2': {
    sh 'TEST_PORT=8082 pytest tests/suite2/'
},
```

3. **Shared temp directory — file name collisions:**
```groovy
'test-suite-1': {
    sh 'TMPDIR=$(mktemp -d) pytest tests/suite1/'
},
```

4. **Workspace contention (both on same agent):** Force parallel stages onto separate agents:
```groovy
parallel {
    'test-suite-1': {
        node('test-agent') { sh 'pytest tests/suite1/' }
    },
    'test-suite-2': {
        node('test-agent') { sh 'pytest tests/suite2/' }
    }
}
```

---

### Scenario 8: Jenkins Build History Grows Unboundedly — Controller Runs Out of Memory

**Problem:** The Jenkins controller becomes sluggish and eventually unresponsive. Heap dumps show millions of objects related to build records. The Jenkins home directory is 500GB.

**Diagnosis:**
```groovy
// Script Console — find top jobs by build count
Jenkins.instance.allItems(hudson.model.Job.class).each { job ->
    def count = job.builds.size()
    if (count > 1000) println "${count} builds: ${job.fullName}"
}
```

**Immediate relief — configure build discarder:**
```groovy
// In pipeline
options {
    buildDiscarder(logRotator(numToKeepStr: '30', artifactNumToKeepStr: '10'))
}
```

**Bulk-configure via Script Console:**
```groovy
Jenkins.instance.allItems(hudson.model.Job.class).each { job ->
    if (job instanceof hudson.model.AbstractProject) {
        job.setBuildDiscarder(
            new hudson.tasks.LogRotator(30, 30, 5, 5)  // daysToKeep, numToKeep, artifactDays, artifactNum
        )
        job.save()
    }
}
```

**JVM heap tuning for Jenkins controller:**
```bash
# /etc/default/jenkins or JAVA_OPTS in Jenkins startup script
JAVA_OPTS="-Xms2g -Xmx8g -XX:+UseG1GC -XX:MaxGCPauseMillis=500 \
  -Djava.awt.headless=true \
  -XX:+ExplicitGCInvokesConcurrent"
```

**Long-term:** Enable the Jenkins Prometheus plugin — track `jenkins_builds_available_executors`, `jenkins_queue_size_value`, and JVM heap metrics. Alert when heap > 80% sustained for 5 minutes.
