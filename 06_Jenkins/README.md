# Jenkins & CI/CD Automation

Jenkins is the industry-standard automation server. While newer tools exist, Jenkins remains the most powerful and flexible "Swiss Army Knife" for building, testing, and deploying software.

#### 1. The Jenkins Architecture
Jenkins uses a **Controller-Agent** (formerly Master-Slave) architecture:
*   **Controller:** The central "Brain." It manages the UI, configuration, and coordinates the scheduling of jobs.
*   **Agents:** The "Muscle." These are separate machines (or Docker containers) that actually run the build steps.
*   **Why split?** To ensure the Controller isn't bogged down by heavy builds and to allow builds to run on different OS environments (Linux, Windows, Mac).

#### 2. Types of Jobs
1.  **Freestyle:** Legacy way to build jobs via a point-and-click UI. Hard to version and maintain.
2.  **Pipeline (The Modern Way):** "Pipeline as Code." The entire build process is defined in a `Jenkinsfile`, which lives in your Git repository.

#### 3. Pipeline Syntax
*   **Declarative (Recommended):** A structured, easy-to-read syntax. Great for 90% of use cases.
*   **Scripted:** Uses Groovy script. Highly flexible but complex and harder to maintain.

#### 4. Shared Libraries
For large organizations, you don't want to copy-paste the same code into 100 `Jenkinsfiles`. **Shared Libraries** allow you to write reusable Groovy functions (e.g., "buildDockerImage") once and use them across the entire company.

***

#### 🔹 1. Improved Notes: Enterprise Jenkins
*   **Dynamic Agents:** Instead of keeping servers running 24/7, Jenkins can spin up a Docker container or an AWS EC2 instance only when a build starts, and destroy it when finished. This saves massive amounts of money.
*   **Plugins:** Jenkins' strength is its ecosystem. From Git and Docker to Slack and Jira, there is a plugin for everything. **But beware:** Too many plugins ("Plugin Hell") can make Jenkins slow and unstable.

#### 🔹 2. Interview View (Q&A)
*   **Q:** What is the difference between a `Stage` and a `Step`?
*   **A:** A `Stage` is a logical block of the pipeline (e.g., "Build", "Test", "Deploy"). A `Step` is a single command inside that stage (e.g., `sh 'npm install'`).
*   **Q:** How do you secure credentials in Jenkins?
*   **A:** Never hardcode passwords. Use the **Jenkins Credentials Store**. You can then inject them into your pipeline using the `credentials()` helper, which masks the output in the logs.

***

#### 🔹 3. Architecture & Design: The CI/CD Flow
1.  **Poll SCM / Webhook:** Jenkins detects a change in Git.
2.  **Checkout:** Jenkins pulls the code to an Agent.
3.  **Build & Test:** Unit tests and compilation.
4.  **Artifact Storage:** Store the binary (JAR, Docker Image) in a repository (Nexus, Artifactory).
5.  **Deploy:** Push the change to Staging/Prod.

***

#### 🔹 4. Commands & Configs (Power User)
```groovy
// A simple Declarative Jenkinsfile
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'mvn clean package'
            }
        }
        stage('Test') {
            steps {
                sh 'mvn test'
            }
        }
    }
}
```

***

#### 🔹 5. Troubleshooting & Debugging
*   **Scenario:** Jenkins is slow or "hanging."
*   **Fix:** Check the **Java Heap Memory**. Jenkins runs on the JVM. If the heap is too small, it will spend all its time doing Garbage Collection. Increase `Xmx` settings in the Jenkins config.

***

#### 🔹 6. Production Best Practices
*   **Backup:** Use the `ThinBackup` plugin or simply back up the `JENKINS_HOME` directory.
*   **Infrastructure as Code:** Use **JCasC (Jenkins Configuration as Code)** to manage Jenkins settings in a YAML file.
*   **Monitoring:** Integrate Jenkins with Prometheus and Grafana to track build success rates and queue times.

***

#### 🔹 Cheat Sheet / Quick Revision
| **Concept** | **Purpose** | **DevOps Context** |
| :--- | :--- | :--- |
| `Trigger` | Starts the job | Usually a GitHub Webhook on a code push. |
| `Agent` | Where the work happens | Usually a Docker container to ensure a clean environment. |
| `Artifact` | The output of a build | A ZIP, JAR, or Docker image ready for deployment. |
| `Post` | Actions after build | Sending a Slack notification on failure. |

***

This is Section 6: Jenkins. For a senior role, you should focus on **Blue/Green Deployments**, **Canary Analysis**, and **Pipeline-as-Code** best practices.
