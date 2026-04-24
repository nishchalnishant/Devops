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
