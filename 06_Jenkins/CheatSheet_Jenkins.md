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

