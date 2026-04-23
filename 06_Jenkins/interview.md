# Jenkins — Interview Questions

All difficulty levels combined.

---

## Easy

**1. What is Jenkins and what is it used for?**

Jenkins is an open-source automation server used to implement CI/CD pipelines. It builds, tests, and deploys code automatically when changes are pushed to a version control system.

**2. What is a Jenkinsfile?**

A Jenkinsfile is a text file, committed to source control, that defines a Jenkins pipeline in either Declarative or Scripted syntax.

**3. What is the difference between Declarative and Scripted pipelines in Jenkins?**

Declarative pipelines use a structured, validated YAML-like syntax with predefined blocks (`pipeline`, `stages`, `steps`). Scripted pipelines use a Groovy DSL with full programming flexibility. Declarative is preferred for most use cases due to readability and validation.

**4. What are Jenkins agents?**

Agents are machines (or containers) that execute pipeline stages. The Jenkins controller distributes work to agents. Agents can be physical machines, VMs, Docker containers, or Kubernetes Pods.

**5. What is a Jenkins Shared Library?**

A Shared Library is a collection of reusable Groovy code (steps, utilities, pipeline templates) stored in a Git repository and imported by Jenkinsfiles across multiple projects.

**6. What is a `stage` in Jenkins?**

A `stage` groups related `steps` together and represents a logical phase of the pipeline (e.g., Build, Test, Deploy). Stages are displayed as columns in the Jenkins Blue Ocean UI.

**7. What is the `post` block in a Declarative pipeline?**

The `post` block defines steps that run after the pipeline or a stage completes, based on the result: `always`, `success`, `failure`, `unstable`, `changed`. Used for notifications and cleanup.

**8. How do you trigger a Jenkins pipeline automatically on a code push?**

Configure a webhook in the SCM (GitHub, GitLab, Bitbucket) to notify Jenkins when a push occurs. In Jenkins, enable "GitHub hook trigger for GITScm polling" or the GitLab/Bitbucket equivalent on the pipeline job.

---

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

## Hard

**15. How do you design a highly available Jenkins controller?**

1. **Controller HA:** Run Jenkins controller in Kubernetes on a PersistentVolume (EBS/Azure Disk) — if the Pod dies, Kubernetes reschedules it on another node and remounts the volume. Use a readiness probe.
2. **Agent architecture:** Use ephemeral Kubernetes agents via the Jenkins Kubernetes Plugin — agents are created per job and destroyed after completion. No idle cost, clean environment per build.
3. **Backup:** Schedule regular backups of the Jenkins home directory (`jobs/`, `credentials.xml`, `plugins/`) to object storage. Test restores monthly.
4. **JCasC:** Store all configuration in Git. If the controller is lost, provision a new one, install plugins, and apply JCasC YAML — fully reproduced in minutes.

**16. How do you migrate 100 Jenkins pipelines to GitLab CI?**

A big-bang migration is too risky. Phased approach:

1. **Categorize:** Group the 100 pipelines by complexity and pattern. Identify 5-10 representative pilots.
2. **Pilot:** Convert pilots to `.gitlab-ci.yml`. Create GitLab CI `include:` templates replicating Jenkins Shared Library functions.
3. **Document:** Write upgrade guides and run workshops.
4. **Phased rollout:** Onboard teams in waves, simplest pipelines first. New projects start on GitLab CI.
5. **Decommission:** Archive Jenkins data, shut down servers after all pipelines are migrated.

**17. How do you design dynamic, on-demand Jenkins agents on Kubernetes?**

1. Install the Jenkins Kubernetes Plugin and configure it with the cluster endpoint and credentials.
2. Define Pod templates in Jenkins (or JCasC YAML) specifying the agent container image, resource requests/limits, volumes, and workspace.
3. When a pipeline job is triggered, the plugin creates a new Pod in Kubernetes matching the Pod template. The agent container connects back to the Jenkins controller and runs the job.
4. After the job completes, the plugin deletes the Pod — zero idle agent cost, fresh environment per build.
5. Scale: with 50 concurrent jobs, 50 Pods are created simultaneously. The Kubernetes scheduler distributes them across nodes.

**18. What are the risks of using the `local-exec` and `remote-exec` provisioners in a Jenkins-triggered Terraform pipeline?**

- **Not idempotent:** Re-running `terraform apply` re-runs the script, which may have unintended side effects.
- **Untracked state:** Actions performed by scripts are not in Terraform state — Terraform doesn't know about them.
- **Tight coupling:** Pipeline behavior depends on the script's side effects, not infrastructure declarations.

Alternatives: Packer for golden image baking, Ansible for post-provisioning configuration, or Cloud-Init user data for startup scripts. Keep Terraform declarative — provision infrastructure, not configuration.
