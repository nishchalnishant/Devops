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

