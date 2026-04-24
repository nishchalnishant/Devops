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


**9. What is the difference between a Jenkins controller and a Jenkins agent?**

The controller (formerly "master") manages the Jenkins UI, job scheduling, plugin management, and build history. It does not run build steps directly — it delegates to agents. Agents are ephemeral or persistent workers that execute pipeline stages. The controller should never execute builds to protect it from resource exhaustion and security exposure.

**10. What does `agent any` mean in a Declarative pipeline?**

It tells Jenkins to run the pipeline on any available agent. Alternatives: `agent none` (no global agent; each stage defines its own), `agent { label 'linux' }` (target agents with a specific label), `agent { docker { image 'node:20' } }` (run inside a Docker container on the agent).

**11. What is a Jenkins multibranch pipeline?**

A multibranch pipeline automatically creates a pipeline job for each branch in a repository that contains a Jenkinsfile. When a branch is created, a job is created; when a branch is deleted, the job is deleted. Used for feature branch CI without manual job creation.

**12. How do you pass parameters to a Jenkins pipeline?**

Declare them in the `parameters` block:

```groovy
parameters {
  string(name: 'ENV', defaultValue: 'staging', description: 'Target environment')
  booleanParam(name: 'SKIP_TESTS', defaultValue: false)
  choice(name: 'REGION', choices: ['us-east-1', 'eu-west-1'])
}
```

Access via `params.ENV` in pipeline steps. Parameters appear as input fields when triggering a build manually.

**13. What is the `environment` block in a Declarative pipeline?**

It sets environment variables available to all steps in that scope:

```groovy
environment {
  IMAGE_NAME = "myapp:${BUILD_NUMBER}"
  AWS_REGION = 'us-east-1'
}
```

Variables defined at `pipeline` level are global; those inside a `stage` are scoped to that stage. Use `credentials()` helper inside `environment` to bind credentials as env vars.

**14. What is Blue Ocean in Jenkins?**

Blue Ocean is a Jenkins UI plugin that provides a visual, modern interface for pipeline visualization. It shows pipeline stages as a graph, highlights failures inline, and makes branch/PR builds easier to navigate. It's largely superseded by the built-in Pipeline UI improvements in Jenkins LTS but is still widely used.

**15. How do Jenkins plugins work?**

Jenkins is plugin-driven — almost every capability (Git integration, Docker, Kubernetes, Slack notifications) is a plugin installed via the Plugin Manager. Plugins are JPI/HPI files. They extend Jenkins extension points (builders, SCM connectors, triggers, etc.). Plugin updates should be tested in staging before applying to production controllers because plugins can introduce breaking changes.

**16. What build triggers are available in Jenkins?**

- **SCM polling**: Jenkins checks VCS at a cron interval (`H/5 * * * *`)  
- **Webhook**: SCM pushes to Jenkins via HTTP (preferred — no polling delay)  
- **Cron schedule**: `triggers { cron('H 2 * * 1-5') }` for nightly builds  
- **Upstream job**: trigger when another job completes successfully  
- **Manual**: user clicks "Build Now"  
- **API trigger**: `curl -X POST http://jenkins/job/<name>/build`
