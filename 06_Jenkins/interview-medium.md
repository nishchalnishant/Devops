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

