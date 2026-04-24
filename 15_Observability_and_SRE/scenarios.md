# Content from devops_errors_and_troubleshooting.pdf

## Page 1

1

***

## Page 2

2

DevOps Shack
DevOps Error Troubleshooting Guide
Introduction
This guide, "DevOps Troubleshooting: A Comprehensive Guide," is designed to
be your go-to resource for addressing the most common and challenging errors
across a wide array of DevOps tools. Structured tool by tool, the book explores
the top 10 errors for each major technology, providing detailed explanations,
root causes, and actionable solutions to help you overcome these challenges
with confidence.
By learning from these errors, you’ll not only become adept at troubleshooting
but also gain insights into building more resilient, automated, and efficient
systems. As you dive into this book, remember: every error is an opportunity to
learn, innovate, and enhance your expertise in the ever-evolving world of
DevOps.
Welcome to the journey of mastering DevOps troubleshooting—let’s get
started!

***

## Page 3

3

Table of Contents

1. Git Errors
   1.1 "fatal: not a git repository (or any of the parent directories): .git"
   1.2 "error: failed to push some refs"
   1.3 "Permission denied (publickey)"
   1.4 "Merge conflict in [file]"
   1.5 "Detached HEAD state"
   1.6 "fatal: remote origin already exists"
   1.7 "Large file exceeds limit"
   1.8 "Submodule update failed"
   1.9 "fatal: cannot lock ref"
   1.10 "Untracked files prevent switching branches"

2. Jenkins Errors
   2.1 "Jenkins service not starting"
   2.2 "Build stuck in the queue"
   2.3 "Plugins fail to load"
   2.4 "Pipeline script syntax error"
   2.5 "Build fails due to missing environment variables"
   2.6 "Unauthorized webhook trigger"
   2.7 "Job not found after restart"
   2.8 "Out of disk space"
   2.9 "Build artifacts not archiving"
   2.10 "Node disconnected unexpectedly"

3. Docker Errors
   3.1 "Cannot connect to the Docker daemon"
   3.2 "Port is already in use"
   3.3 "No space left on device"
   3.4 "ImagePullBackOff" in Kubernetes

***

## Page 4

4

3.5 "Permission denied on bind mount"
3.6 "Container restart loop"
3.7 "Failed to build Docker image"
3.8 "Error response from daemon: conflict"
3.9 "Docker network not reachable"
3.10 "Volume mount not working"

4. Kubernetes Errors
   4.1 "ImagePullBackOff"
   4.2 "CrashLoopBackOff"
   4.3 "Node Not Ready"
   4.4 "PersistentVolumeClaim Pending"
   4.5 "Pod is stuck in Pending state"
   4.6 "RBAC: Access Denied"
   4.7 Service Unreachable
   4.8 "Resource Quota Exceeded"
   4.9 "Evicted Pods"
   4.10 Deployment Rollout Fails

5. Ansible Errors
   5.1 "Host unreachable"
   5.2 "Syntax error in playbook"
   5.3 "Undefined variable"
   5.4 "Command not found on target node"
   5.5 "Permission denied"
   5.6 Module not found
   5.7 "Failed to find group_vars"
   5.8 Playbook runs indefinitely
   5.9 "Handler not triggered"
   5.10 Dynamic inventory script failure

6. Terraform Errors
   6.1 "Provider plugin not found"
   6.2 "State file lock error"

***

## Page 5

5

6.3 "Error acquiring the state lock"
6.4 Resource already exists
6.5 "Plan does not match changes"
6.6 "Invalid index" in Terraform output
6.7 "Module not found"
6.8 Authentication failure
6.9 "Timeout waiting for resource"
6.10 "Remote backend configuration error"

7. Prometheus Errors
   7.1 "No targets found"
   7.2 "Prometheus not scraping data"
   7.3 "High cardinality in metrics"
   7.4 "Prometheus service not starting"
   7.5 "Query taking too long"
   7.6 "Prometheus out of storage space"
   7.7 "Prometheus alert not firing"
   7.8 "Prometheus crash due to OOM (Out of Memory)"
   7.9 "Scraped data is incomplete"
   7.10 "Failed to reload configuration"

8. ELK Stack Errors
   8.1 Elasticsearch: "Cluster health is red"
   8.2 Elasticsearch: "Java heap space error"
   8.3 Logstash: "Pipeline aborted due to error"
   8.4 Logstash: "Connection refused to Elasticsearch"
   8.5 Kibana: "Kibana server is not ready yet"
   8.6 "Index pattern not found in Kibana"
   8.7 "Logstash not processing logs"
   8.8 Elasticsearch: "Index not found"
   8.9 Kibana: "Dashboard is empty"
   8.10 Logstash: "Filebeat logs not received"

***

## Page 6

6

9. AWS DevOps Tools Errors
   9.1 EC2: "Instance not reachable"
   9.2 S3: "Access Denied"
   9.3 CodePipeline: "Failed to deploy"
   9.4 RDS: "Cannot connect to the database"
   9.5 CloudFormation: "Stack creation failed"
   9.6 IAM: "Policy not authorized"
   9.7 ECS: "Task failed to start"
   9.8 Lambda: "Execution failed"
   9.9 Route 53: "DNS record not resolving"
   9.10 CloudWatch: "Metrics not visible"

10. Azure DevOps Tools Errors
    10.1 Pipelines: "Build agent unavailable"
    10.2 "Resource group deployment failed"
    10.3 "Release failed in Azure DevOps"
    10.4 Repos: "Merge conflict during pull request"
    10.5 "Pipeline YAML syntax error"
    10.6 "Artifacts not found"
    10.7 "Access denied to the Azure subscription"
    10.8 "Cannot connect to Azure Kubernetes Service (AKS)"
    10.9 Boards: "Work item cannot be updated"
    10.10 "Failed to publish test results"

11. CI/CD Pipeline Errors
    11.1 "Pipeline stuck in pending state"
    11.2 "Build fails due to dependency issues"
    11.3 "Environment variable not found"
    11.4 "Permission denied during deployment"
    11.5 "Timeout in build or deployment stage"
    11.6 "Pipeline fails only on specific branches"
    11.7 "Docker image not found in the pipeline"
    11.8 "Failed to upload artifacts"

***

## Page 7

7

11.9 "Parallel jobs failing intermittently"
11.10 "Webhook not triggering pipeline"

12. Monitoring Tools Errors
    12.1 "Metrics not visible in Grafana"
    12.2 "Prometheus data missing from dashboards"
    12.3 "Logs not visible in ELK Stack"
    12.4 "High load on monitoring servers"
    12.5 "Alerts not firing in Prometheus"
    12.6 "Outdated Grafana dashboards"
    12.7 "Log ingestion delay in ELK Stack"
    12.8 "Scraped data is incomplete"
    12.9 "Too many false-positive alerts"
    12.10 "Dashboard panels showing no data"

***

## Page 8

8

1. Git Errors
   1.1 "fatal: not a git repository (or any of the parent directories): .git"
   • Cause: The command is executed outside a Git repository or the
   repository is corrupted.
   • Solution:
1. Verify you're in the correct directory: pwd.
1. Navigate to the repository: cd <repository-path>.
1. If missing, reinitialize the repository: git init.
   1.2 "error: failed to push some refs"
   • Cause: Local branch is out of sync with the remote branch.
   • Solution:
1. Pull latest changes with rebase: git pull --rebase origin <branch>.
1. Resolve conflicts if prompted, then commit and push.
   1.3 "Permission denied (publickey)"
   • Cause: SSH key is missing or not recognized by the remote repository.
   • Solution:
1. Generate a key pair: ssh-keygen -t rsa -b 4096.
1. Add the private key to the agent: ssh-add ~/.ssh/id_rsa.
1. Add the public key to the repository settings.
   1.4 "Merge conflict in [file]"
   • Cause: Simultaneous changes to the same part of a file.
   • Solution:
1. Open the conflicting file to resolve changes.
1. Use markers like <<<<<<< and >>>>>>> to identify conflicts.
1. After resolution, commit: git add <file> && git commit.
   1.5 "Detached HEAD state"

***

## Page 9

9

• Cause: A specific commit is checked out instead of a branch.
• Solution:

1. Create a branch from the detached state: git checkout -b <new-
   branch>.
2. Continue working or merge with another branch.
   1.6 "fatal: remote origin already exists"
   • Cause: Adding a remote repository that already exists.
   • Solution:
3. Update the existing remote: git remote set-url origin <new-URL>.
   1.7 "Large file exceeds limit"
   • Cause: Attempt to push a file exceeding the repository limit (e.g.,
   GitHub's 100MB limit).
   • Solution:
4. Use Git Large File Storage (LFS): git lfs track "<file-pattern>".
   1.8 "Submodule update failed"
   • Cause: Incorrect or inaccessible submodule configuration.
   • Solution:
5. Update submodules: git submodule update --init --recursive.
   1.9 "fatal: cannot lock ref"
   • Cause: A .lock file is preventing operations due to an interrupted
   process.
   • Solution:
6. Remove the .lock file: rm -f .git/index.lock.
   1.10 "Untracked files prevent switching branches"
   • Cause: Untracked changes conflict with the branch switch.
   • Solution:
7. Stash changes: git stash.

***

## Page 10

10

2. Switch branches: git checkout <branch>.

***

## Page 11

11

2. Jenkins Errors
   2.1 "Jenkins service not starting"
   • Cause: Corrupted configuration or missing Java installation.
   • Solution:
1. Check logs: sudo journalctl -u jenkins.
1. Verify Java installation: java -version.
   2.2 "Build stuck in the queue"
   • Cause: No available executors or agents.
   • Solution:
1. Ensure the Jenkins agent is running and connected.
1. Increase executor count under "Manage Jenkins."
   2.3 "Plugins fail to load"
   • Cause: Outdated Jenkins version or missing dependencies.
   • Solution:
1. Update Jenkins to the latest version.
1. Reinstall failing plugins.
   2.4 "Pipeline script syntax error"
   • Cause: Incorrect Groovy syntax.
   • Solution:
1. Validate the script using the pipeline syntax generator.
1. Debug syntax errors with Jenkins logs.
   2.5 "Build fails due to missing environment variables"
   • Cause: Environment variables not set in the job configuration.
   • Solution:
1. Define variables in "Build Environment" or as parameters.
1. Use env.VARIABLE_NAME in the pipeline script.

***

## Page 12

12

2.6 "Unauthorized webhook trigger"
• Cause: Incorrect webhook configuration or missing credentials.
• Solution:

1. Verify the webhook URL in the source control settings.
2. Add proper credentials in Jenkins.
   2.7 "Job not found after restart"
   • Cause: Corrupted job configurations.
   • Solution:
3. Check for backups in /var/lib/jenkins/jobs.
4. Recreate the job manually if backups are unavailable.
   2.8 "Out of disk space"
   • Cause: Jenkins workspace consumes too much space.
   • Solution:
5. Clean old builds: Manage Jenkins > Workspace Cleanup Plugin.
6. Automate workspace cleanup post-build.
   2.9 "Build artifacts not archiving"
   • Cause: Incorrect artifact path configuration.
   • Solution:
7. Ensure correct file paths in "Archive the artifacts" step.
   2.10 "Node disconnected unexpectedly"
   • Cause: Network or agent-side issues.
   • Solution:
8. Verify agent logs and network connectivity.

***

## Page 13

13

3. Docker Errors
   3.1 "Cannot connect to the Docker daemon"
   • Cause: Docker service is not running or user lacks permissions.
   • Solution:
1. Start the Docker service: sudo systemctl start docker.
1. Add the user to the Docker group: sudo usermod -aG docker
   $USER.
   3.2 "Port is already in use"
   • Cause: Another process is bound to the same port.
   • Solution:
1. Stop the conflicting container: docker stop <container-id>.
1. Change the container's port mapping.
   3.3 "No space left on device"
   • Cause: Disk space is exhausted by Docker images and containers.
   • Solution:
1. Remove unused resources: docker system prune -a.
   3.4 "ImagePullBackOff" in Kubernetes
   • Cause: Invalid image tag or registry issues.
   • Solution:
1. Verify the image name and registry credentials.
   3.5 "Permission denied on bind mount"
   • Cause: Host directory permissions are restrictive.
   • Solution:
1. Update directory permissions: chmod 777 <directory>.

***

## Page 14

14

4. Kubernetes Errors
   4.1 "ImagePullBackOff"
   • Cause: The Kubernetes node cannot pull the specified container image
   due to an invalid image name, tag, or lack of access.
   • Solution:
1. Verify the image name and tag.
1. If the image is private, check the ImagePullSecret or use kubectl
   create secret.
   4.2 "CrashLoopBackOff"
   • Cause: The container crashes repeatedly, often due to application-level
   errors.
   • Solution:
1. Check container logs using kubectl logs <pod-name>.
1. Fix the underlying issue causing the crash.
   4.3 "Node Not Ready"
   • Cause: A Kubernetes node is unhealthy or cannot join the cluster.
   • Solution:
1. Use kubectl get nodes to check node status.
1. Restart the kubelet service and verify resource availability.
   4.4 PersistentVolumeClaim Pending
   • Cause: No PersistentVolume matches the claim's requirements.
   • Solution:
1. Check storage class and create a matching PersistentVolume.
   4.5 "Pod is stuck in Pending state"
   • Cause: Insufficient resources or unschedulable conditions.
   • Solution:
1. Check node capacity: kubectl describe pod <pod-name>.

***

## Page 15

15

2. Scale up resources or adjust pod resource requests.
   4.6 "RBAC: Access Denied"
   • Cause: Role-based access control prevents the action.
   • Solution:
1. Grant proper permissions using Role/ClusterRole and RoleBinding.
   4.7 Service Unreachable
   • Cause: Service or ingress misconfiguration.
   • Solution:
1. Verify Service type, selectors, and target port.
1. Check the ingress rules if applicable.
   4.8 "Resource Quota Exceeded"
   • Cause: The namespace has hit resource limits.
   • Solution:
1. Increase the resource quota or optimize usage.
   4.9 "Evicted Pods"
   • Cause: Nodes lack sufficient resources.
   • Solution:
1. Check events with kubectl describe pod.
1. Add resources or reschedule workloads.
   4.10 Deployment Rollout Fails
   • Cause: Health checks fail for new pods.
   • Solution:
1. Check logs and events of failed pods.
1. Roll back using kubectl rollout undo.

***

## Page 16

16

5. Ansible Errors
   5.1 "Host unreachable"
   • Cause: SSH connection fails.
   • Solution:
1. Verify SSH keys and access.
1. Ensure the inventory file has the correct IP addresses.
   5.2 "Syntax error in playbook"
   • Cause: Incorrect YAML formatting.
   • Solution:
1. Validate YAML with a linter or ansible-playbook --syntax-check.
   5.3 "Undefined variable"
   • Cause: Variable is not defined in the playbook or inventory.
   • Solution:
1. Define the variable in vars, group_vars, or the inventory file.
   5.4 "Command not found" on target node
   • Cause: Required packages are missing.
   • Solution:
1. Install missing packages using a task in the playbook.
   5.5 "Permission denied"
   • Cause: User lacks required permissions on the target machine.
   • Solution:
1. Use become: true in the playbook to execute as a superuser.
   5.6 Module not found
   • Cause: The Ansible module is not installed.
   • Solution:
1. Ensure Ansible and its dependencies are up-to-date.

***

## Page 17

17

5.7 "Failed to find group_vars"
• Cause: Incorrect directory structure.
• Solution:

1. Place group_vars and host_vars in the same directory as the
   inventory file.
   5.8 Playbook runs indefinitely
   • Cause: Task stuck in a loop or waiting for an unavailable service.
   • Solution:
1. Add timeout options and validate tasks.
   5.9 "Handler not triggered"
   • Cause: No task notifies the handler.
   • Solution:
1. Add notify: <handler-name> to the appropriate task.
   5.10 Dynamic inventory script failure
   • Cause: Errors in the inventory script.
   • Solution:
1. Debug the script manually or use --list to validate.

***

## Page 18

18

6. Terraform Errors
   6.1 "Provider plugin not found"
   • Cause: Missing or outdated provider plugin.
   • Solution:
1. Run terraform init to download required plugins.
   6.2 "State file lock error"
   • Cause: Concurrent Terraform runs.
   • Solution:
1. Unlock the state file: terraform force-unlock <lock-id>.
   6.3 "Error acquiring the state lock"
   • Cause: Network issues when using remote state.
   • Solution:
1. Retry after ensuring stable connectivity.
   6.4 Resource already exists
   • Cause: Attempting to create a resource that already exists.
   • Solution:
1. Use terraform import to manage existing resources.
   6.5 "Plan does not match changes"
   • Cause: Drift in the state file.
   • Solution:
1. Refresh state: terraform refresh.
   6.6 "Invalid index" in Terraform output
   • Cause: Incorrect usage of lists or maps.
   • Solution:
1. Validate variable types and indices.
   6.7 "Module not found"

***

## Page 19

19

• Cause: Incorrect module path.
• Solution:

1. Ensure module paths are correct and run terraform get.
   6.8 Authentication failure
   • Cause: Missing or invalid credentials.
   • Solution:
1. Set proper environment variables or credentials files.
   6.9 "Timeout waiting for resource"
   • Cause: Resource creation takes too long.
   • Solution:
1. Increase timeout settings in the resource block.
   6.10 "Remote backend configuration error"
   • Cause: Incorrect backend configuration.
   • Solution:
1. Check and fix the backend block in the Terraform configuration.

***

## Page 20

20

7. Prometheus Errors
   7.1 "No targets found"
   • Cause: Prometheus is not configured to scrape any endpoints.
   • Solution:
1. Check prometheus.yml for scrape configurations.
1. Ensure that target endpoints are reachable.
   7.2 "Prometheus not scraping data"
   • Cause: Target endpoints are misconfigured or not reachable.
   • Solution:
1. Verify the status of targets in the Prometheus UI under Status >
   Targets.
1. Fix any endpoint issues or configurations.
   7.3 "High cardinality in metrics"
   • Cause: Too many unique label combinations in metrics.
   • Solution:
1. Optimize label usage in your metric definitions.
1. Use relabeling rules to filter out unnecessary labels.
   7.4 "Prometheus service not starting"
   • Cause: Misconfiguration in prometheus.yml or insufficient resources.
   • Solution:
1. Validate the configuration file: promtool check config
   prometheus.yml.
1. Check system resources and allocate more CPU/memory if
   needed.
   7.5 "Query taking too long"
   • Cause: Large datasets or inefficient queries.
   • Solution:

***

## Page 21

21

1. Optimize your PromQL queries by limiting time ranges or labels.
2. Enable query caching for better performance.
   7.6 "Prometheus out of storage space"
   • Cause: Retention period or data volume exceeds available disk space.
   • Solution:
3. Reduce the data retention period: --
   storage.tsdb.retention.time=<duration>.
4. Add more storage or clean old data manually.
   7.7 "Prometheus alert not firing"
   • Cause: Misconfigured alert rules.
   • Solution:
5. Validate alert rules using promtool check rules.
6. Ensure the alert expression is correct and matches expected data.
   7.8 "Prometheus crash due to OOM (Out of Memory)"
   • Cause: Too many metrics or insufficient memory allocation.
   • Solution:
7. Increase memory allocation to the Prometheus server.
8. Reduce the number of metrics being scraped by filtering them.
   7.9 "Scraped data is incomplete"
   • Cause: Targets are partially down or network issues.
   • Solution:
9. Check the health of scrape targets.
10. Monitor network connections between Prometheus and
    endpoints.
    7.10 "Failed to reload configuration"
    • Cause: Syntax errors in prometheus.yml.
    • Solution:

***

## Page 22

22

1. Validate the configuration file with promtool.
2. Fix any syntax issues before reloading.

***

## Page 23

23

8. ELK Stack Errors (Elasticsearch, Logstash, and Kibana)
   8.1 Elasticsearch: "Cluster health is red"
   • Cause: Some nodes or shards are unavailable.
   • Solution:
1. Check node status: curl -X GET <ES_HOST>/\_cat/nodes.
1. Reallocate shards: POST \_cluster/reroute.
   8.2 Elasticsearch: "Java heap space error"
   • Cause: Insufficient heap memory for Elasticsearch.
   • Solution:
1. Increase heap size in jvm.options.
1. Use Xms and Xmx values not exceeding 50% of available memory.
   8.3 Logstash: "Pipeline aborted due to error"
   • Cause: Syntax error or incorrect configuration in logstash.conf.
   • Solution:
1. Validate the configuration: logstash -t -f logstash.conf.
1. Fix the error based on logs.
   8.4 Logstash: "Connection refused to Elasticsearch"
   • Cause: Incorrect Elasticsearch endpoint in Logstash configuration.
   • Solution:
1. Update output { elasticsearch { hosts => ["<ES_HOST>"] }}.
   8.5 Kibana: "Kibana server is not ready yet"
   • Cause: Elasticsearch cluster is not reachable.
   • Solution:
1. Verify Elasticsearch connectivity.
1. Restart Kibana after Elasticsearch is ready.
   8.6 "Index pattern not found in Kibana"

***

## Page 24

24

• Cause: No matching indices in Elasticsearch.
• Solution:

1. Ensure data is being sent to Elasticsearch.
2. Recreate the index pattern in Kibana.
   8.7 "Logstash not processing logs"
   • Cause: Input or filter misconfiguration.
   • Solution:
3. Check input sources and logs for issues.
4. Validate filters with small datasets.
   8.8 Elasticsearch: "Index not found"
   • Cause: Querying an index that doesn’t exist.
   • Solution:
5. Check available indices: curl -X GET <ES_HOST>/\_cat/indices.
   8.9 Kibana: "Dashboard is empty"
   • Cause: Missing or misconfigured visualizations.
   • Solution:
6. Verify data sources for visualizations.
7. Check time filters on the dashboard.
   8.10 Logstash: "Filebeat logs not received"
   • Cause: Incorrect Filebeat-to-Logstash configuration.
   • Solution:
8. Check Filebeat output.logstash configuration.
9. Ensure the correct port and protocol.

***

## Page 25

25

9. AWS DevOps Tools Errors
   9.1 EC2: "Instance not reachable"
   • Cause: Incorrect security group or network ACL configuration.
   • Solution:
1. Verify inbound rules for SSH/HTTP access.
1. Check VPC and subnet configuration.
   9.2 S3: "Access Denied"
   • Cause: Missing permissions for the S3 bucket.
   • Solution:
1. Update bucket policies to allow access.
1. Attach proper IAM roles or policies.
   9.3 CodePipeline: "Failed to deploy"
   • Cause: Deployment stage error.
   • Solution:
1. Check deployment logs for details.
1. Verify IAM permissions for CodePipeline and CodeDeploy.
   9.4 RDS: "Cannot connect to the database"
   • Cause: Firewall or networking issues.
   • Solution:
1. Add the correct inbound rules to the RDS security group.
1. Check database credentials.
   9.5 CloudFormation: "Stack creation failed"
   • Cause: Misconfigured templates or resource dependencies.
   • Solution:
1. Review the stack events for specific errors.
1. Validate the template: aws cloudformation validate-template.

***

## Page 26

26

9.6 IAM: "Policy not authorized"
• Cause: Insufficient permissions in the policy.
• Solution:

1. Modify the policy to include the required actions.
   9.7 ECS: "Task failed to start"
   • Cause: Resource limitations or misconfigured task definitions.
   • Solution:
1. Check task logs in CloudWatch.
1. Ensure sufficient memory and CPU allocation.
   9.8 Lambda: "Execution failed"
   • Cause: Errors in the Lambda function code.
   • Solution:
1. Review CloudWatch logs for detailed errors.
1. Update the function code to fix issues.
   9.9 Route 53: "DNS record not resolving"
   • Cause: Incorrect record type or misconfigured TTL.
   • Solution:
1. Verify DNS records in the Route 53 console.
1. Check domain delegation settings.
   9.10 CloudWatch: "Metrics not visible"
   • Cause: Missing or misconfigured monitoring agents.
   • Solution:
1. Ensure the CloudWatch agent is running.
1. Verify configuration files.

***

## Page 27

27

10. Azure DevOps Tools Errors
    10.1 Pipelines: "Build agent unavailable"
    • Cause: The agent is offline or misconfigured.
    • Solution:
1. Restart the agent service.
1. Verify agent registration in Azure DevOps.
   10.2 "Resource group deployment failed"
   • Cause: Incorrect ARM template.
   • Solution:
1. Validate the ARM template before deployment.
   10.3 "Release failed in Azure DevOps"
   • Cause: Deployment script errors.
   • Solution:
1. Check logs for failed tasks.
1. Fix script errors and re-run.
   10.4 Repos: "Merge conflict during pull request"
   • Cause: Simultaneous changes to the same files.
   • Solution:
1. Resolve conflicts using the web editor or locally.
   10.5 "Pipeline YAML syntax error"
   • Cause: Incorrect YAML configuration.
   • Solution:
1. Use the Azure DevOps YAML validator.
   10.6 "Artifacts not found"
   • Cause: Missing build artifacts in the pipeline.
   • Solution:

***

## Page 28

28

1. Ensure the correct artifact paths are defined in the build stage.
   10.7 "Access denied to the Azure subscription"
   • Cause: Missing role assignments.
   • Solution:
1. Assign proper roles to the service principal.
   10.8 "Cannot connect to Azure Kubernetes Service (AKS)"
   • Cause: Misconfigured kubeconfig or network rules.
   • Solution:
1. Regenerate kubeconfig using the Azure CLI: az aks get-credentials.
   10.9 Boards: "Work item cannot be updated"
   • Cause: Permission issues.
   • Solution:
1. Update user permissions in the project settings.
   10.10 "Failed to publish test results"
   • Cause: Incorrect test result path.
   • Solution:
1. Verify the test result files in the pipeline logs.

***

## Page 29

29

11. CI/CD Pipeline Errors
    11.1 "Pipeline stuck in pending state"
    • Cause: No available runners or agents.
    • Solution:
1. Ensure runners or agents are properly registered and running.
1. Check tags and runner configurations to match the job
   requirements.
   11.2 "Build fails due to dependency issues"
   • Cause: Missing, outdated, or incorrect dependencies.
   • Solution:
1. Update dependency files like requirements.txt, package.json, or
   pom.xml.
1. Cache dependencies to reduce build times and errors.
   11.3 "Environment variable not found"
   • Cause: Undefined or incorrectly set environment variables.
   • Solution:
1. Add the variable in the CI/CD tool's settings.
1. Use .env files or secret managers for sensitive variables.
   11.4 "Permission denied during deployment"
   • Cause: User lacks required permissions on the target server.
   • Solution:
1. Ensure proper SSH keys or access tokens are configured.
1. Use a service account with deployment privileges.
   11.5 "Timeout in build or deployment stage"
   • Cause: Long-running processes exceed the timeout threshold.
   • Solution:
1. Optimize pipeline stages for efficiency.

***

## Page 30

30

2. Increase timeout values in the pipeline configuration.
   11.6 "Pipeline fails only on specific branches"
   • Cause: Branch-specific settings or missing configurations.
   • Solution:
1. Verify branch-specific variables and scripts.
1. Use conditional logic to apply configurations only for certain
   branches.
   11.7 "Docker image not found in the pipeline"
   • Cause: Incorrect image name, tag, or lack of authentication.
   • Solution:
1. Check and update the image name and tag.
1. Authenticate with the Docker registry using proper credentials.
   11.8 "Failed to upload artifacts"
   • Cause: Incorrect artifact paths or permissions.
   • Solution:
1. Validate the artifact paths defined in the pipeline.
1. Ensure proper permissions to upload files to storage services.
   11.9 "Parallel jobs failing intermittently"
   • Cause: Shared resources causing conflicts between parallel jobs.
   • Solution:
1. Use isolation mechanisms like resource locks.
1. Clean up shared resources after each job.
   11.10 "Webhook not triggering pipeline"
   • Cause: Misconfigured webhook or restricted access.
   • Solution:
1. Verify the webhook URL and payload.
1. Check firewall or network restrictions blocking the webhook.

***

## Page 31

31

12. Monitoring Tools Errors
    12.1 "Metrics not visible in Grafana"
    • Cause: Incorrect data source configuration or no metrics collected.
    • Solution:
1. Verify data source settings in Grafana.
1. Check Prometheus targets or other metrics sources for proper
   data collection.
   12.2 "Prometheus data missing from dashboards"
   • Cause: Misconfigured PromQL queries or data source issues.
   • Solution:
1. Test PromQL queries in Prometheus before using them in Grafana.
1. Check and fix Grafana queries for the correct metrics and labels.
   12.3 "Logs not visible in ELK Stack"
   • Cause: Filebeat, Logstash, or Elasticsearch misconfiguration.
   • Solution:
1. Check Filebeat logs for input/output errors.
1. Validate Logstash pipeline and ensure Elasticsearch indices are
   configured correctly.
   12.4 "High load on monitoring servers"
   • Cause: Excessive data ingestion or high cardinality metrics.
   • Solution:
1. Optimize metrics collection by reducing labels and unnecessary
   data.
1. Scale monitoring servers horizontally.
   12.5 "Alerts not firing in Prometheus"
   • Cause: Incorrect alert rules or expression issues.
   • Solution:

***

## Page 32

32

1. Verify and test alert rules in Prometheus.
2. Use promtool to validate the alert configuration.
   12.6 "Outdated Grafana dashboards"
   • Cause: Data caching or lack of auto-refresh.
   • Solution:
3. Enable auto-refresh for dashboards.
4. Clear cached data and reload the dashboard.
   12.7 "Log ingestion delay in ELK Stack"
   • Cause: Network bottlenecks or overloaded Logstash instances.
   • Solution:
5. Check network latency between Filebeat and Logstash.
6. Scale Logstash horizontally or increase processing threads.
   12.8 "Scraped data is incomplete"
   • Cause: Partial scrape failures due to unreachable targets.
   • Solution:
7. Verify target status in Prometheus under Status > Targets.
8. Fix any issues with endpoints or networking.
   12.9 "Too many false-positive alerts"
   • Cause: Overly sensitive alert thresholds.
   • Solution:
9. Adjust alert thresholds to reduce noise.
10. Use deadband or hysteresis to filter transient anomalies.
    12.10 "Dashboard panels showing no data"
    •
    Cause: Incorrect queries or invalid time range.
    •
    Solution:
11. Verify the query syntax and metrics used in the panels.
12. Ensure the selected time range matches the data availability.

***

## Page 33

33

Conclusion
The world of DevOps is inherently dynamic, with multiple tools and
technologies working together to streamline software delivery and
infrastructure management. Despite the power and flexibility of these tools,
errors and issues are inevitable, especially in complex environments. This guide
aims to provide a practical and comprehensive resource for DevOps
practitioners to troubleshoot and resolve common errors across a wide array of
tools, including Git, Jenkins, Docker, Kubernetes, Ansible, Terraform, ELK
Stack, AWS, Azure, and more.
From configuration errors and syntax issues to network connectivity and
resource limitations, the errors outlined in this guide represent challenges
faced by DevOps teams daily. Each problem is paired with actionable solutions,
empowering you to identify and fix issues efficiently, ensuring smoother
operations and fewer disruptions.
The key to successful troubleshooting lies not only in resolving issues but in
learning from them. By identifying patterns in failures, implementing proactive
monitoring, and adhering to best practices, you can build more resilient and
robust systems. DevOps is as much about fostering collaboration and
automation as it is about continuous improvement and problem-solving.
As you navigate the evolving landscape of DevOps, remember that errors are
opportunities to learn, optimize, and innovate. This guide is just a starting
point, and as you gain experience, your understanding of these tools will
deepen, enabling you to tackle even the most complex challenges with
confidence.
Keep experimenting, keep learning, and most importantly, keep building. The
road to DevOps mastery is paved with errors, but each error brings you one
step closer to excellence.

***

# Content from devops_real_time_troubleshooting.pdf

## Page 1

DevOps Real Time Troubleshooting’s

1. Issue: Jenkins Master Fails to Start
   o
   Resolution: Check Jenkins logs (/var/log/jenkins/jenkins.log). Look for any
   error messages indicating startup failures. Common issues include port conflicts,
   insufficient permissions, or corrupted configurations. Resolve these issues and restart
   Jenkins.
2. Issue: Out of Memory Error
   o
   Resolution: Increase the Java heap space allocated to Jenkins. Edit the Jenkins
   startup script or configuration file to set the JAVA_ARGS parameter with a higher
   heap size, e.g., -Xmx2g. Monitor system resources to ensure sufficient RAM is
   available.
3. Issue: Plugin Compatibility
   o
   Resolution: Check Jenkins plugin versions for compatibility with the Jenkins master
   version. Outdated or incompatible plugins can cause crashes. Update plugins to
   versions compatible with your Jenkins master.
4. Issue: Disk Space Exhaustion
   o
   Resolution: Inspect disk space on the server hosting Jenkins. Jenkins may crash if it
   runs out of disk space. Clean up unnecessary files, logs, and artifacts. Consider
   expanding the disk space if needed.
5. Issue: Corrupted Configuration Files
   o
   Resolution: Review Jenkins configuration files, such as config.xml. Manually
   inspect or restore from a backup if corruption is detected. Ensure proper syntax and
   configuration settings.
6. Issue: Database Connection Problems
   o
   Resolution: If Jenkins uses an external database, verify the database connection
   settings in Jenkins configurations. Check the database server for issues. Repair or
   reconfigure the database connection settings in Jenkins if necessary.
7. Issue: Java Compatibility
   o
   Resolution: Ensure Jenkins is using a supported version of Java. Check the Java
   version compatibility with the Jenkins version. Update Java if needed and restart
   Jenkins.
8. Issue: Permission Problems
   o
   Resolution: Verify that the Jenkins process has the necessary permissions to access
   its home directory and required resources. Ensure proper ownership and permissions
   for Jenkins files and directories.
9. Issue: Overloaded Jenkins Master
   o
   Resolution: Analyze Jenkins load and resource usage. If the Jenkins master is
   overloaded with jobs, consider distributing the workload by using Jenkins agents.
   Scale your Jenkins infrastructure horizontally if needed.

***

## Page 2

Roles and Responsibilities for Kubernetes Cluster Management:

1. Cluster Administrator:
   o
   Responsible for overall cluster health and performance.
   o
   Manages node resources and ensures proper scaling.
   o
   Implements security policies and access controls.
2. Deployment Engineer:
   o
   Handles application deployment on Kubernetes clusters.
   o
   Ensures proper configuration of pods, services, and other resources.
   o
   Monitors and troubleshoots application issues.
3. Security Specialist:
   o
   Implements and monitors security measures for the cluster.
   o
   Manages network policies, RBAC (Role-Based Access Control), and secrets.
   o
   Conducts regular security audits.
4. Monitoring and Logging Expert:
   o
   Implements monitoring tools to track cluster performance.
   o
   Configures logging for cluster and application components.
   o
   Analyzes logs and metrics to identify issues.
5. Networking Specialist:
   o
   Manages cluster networking, including services, ingress, and egress.
   o
   Resolves network-related issues and ensures proper communication between pods.
   o
   Configures and maintains network policies.
6. Storage Administrator:
   o
   Handles storage configuration for persistent data in Kubernetes.
   o
   Manages storage classes, persistent volumes, and persistent volume claims.
   o
   Ensures data persistence and availability.
7. Backup and Recovery Specialist:
   o
   Implements backup strategies for critical data and configurations.
   o
   Designs and tests recovery procedures in case of data loss or cluster failure.
   o
   Monitors backup health and performs periodic recovery drills.
8. Upgradation and Patching Coordinator:
   o
   Plans and executes Kubernetes version upgrades.
   o
   Ensures timely application of security patches.
   o
   Tests upgrades in a controlled environment before production.
9. Capacity Planner:
   o
   Monitors resource utilization and forecasts capacity requirements.
   o
   Plans for scaling operations based on usage patterns.
   o
   Optimizes resource allocation for cost efficiency.
10. Compliance Manager:
    o
    Ensures cluster compliance with organizational and regulatory policies.
    o
    Conducts audits to verify adherence to security and operational standards.
    o
    Implements corrective actions for any compliance violations.

***

## Page 3

Real-Time Troubleshooting for Kubernetes Cluster

1. Issue: Pod CrashLoopBackOff
   o
   Resolution: Check pod logs for error messages, review pod configuration, and fix any
   misconfigurations. Verify resource constraints and adjust accordingly.
2. Issue: Network Communication Failure Between Pods
   o
   Resolution: Examine network policies, check for firewall rules, and ensure correct
   service and pod configurations. Use tools like traceroute to identify network issues.
3. Issue: Node Resource Exhaustion
   o
   Resolution: Monitor node resources using tools like Prometheus. Scale nodes or
   adjust resource requests/limits for pods. Identify and optimize resource-hungry
   applications.
4. Issue: Unauthorized Access
   o
   Resolution: Review RBAC settings, ensure proper user roles, and update access
   controls. Implement network policies to restrict unauthorized access.
5. Issue: Persistent Volume Mount Failures
   o
   Resolution: Check persistent volume and persistent volume claim configurations.
   Verify storage class availability, fix storage backend issues, and ensure correct access
   modes.
6. Issue: Ingress Misconfiguration
   o
   Resolution: Validate Ingress YAML, check backend service configurations, and ensure
   DNS resolution. Use kubectl describe to inspect Ingress objects for errors.
7. Issue: Slow Application Performance
   o
   Resolution: Analyze application and cluster metrics using tools like Grafana.
   Optimize application code, adjust resource limits, and scale if necessary.
8. Issue: Node Not Ready
   o
   Resolution: Investigate node status using kubectl get nodes. Check system logs
   for any issues. Resolve networking problems, disk space issues, or other system-level
   problems.
9. Issue: Image Pull Errors
   o
   Resolution: Verify image availability, check registry credentials, and ensure correct
   image names in pod specifications. Troubleshoot network connectivity to the image
   registry.
10. Issue: Cluster-wide Outage
    o
    Resolution: Examine system-wide issues such as etcd failures, control plane
    problems, or network partitioning. Use tools like kubectl get events and logs to
    identify root causes. Implement disaster recovery procedures if needed.

***

## Page 4

AWS Real Time Troubleshooting’s

1. EC2: Instance Unreachable
   o
   Symptoms: Unable to connect to an EC2 instance.
   o
   Resolution: Check security group rules and Network ACLs to ensure correct inbound
   and outbound traffic. Verify the instance state and system logs for any issues. Update
   security groups if necessary.
2. Auto Scaling: Scaling Issues
   o
   Symptoms: Auto Scaling fails to launch or terminate instances.
   o
   Resolution: Review Auto Scaling group configuration, launch configurations, and
   health checks. Check instance termination protection settings. Investigate
   CloudWatch alarms for triggers and adjust policies accordingly.
3. Load Balancer: Unhealthy Instances
   o
   Symptoms: Load balancer reports instances as unhealthy.
   o
   Resolution: Inspect CloudWatch metrics for instances, troubleshoot application
   health checks, and ensure instances are registered with the correct load balancer.
   Check security group settings and troubleshoot application health.
4. Route 53: DNS Resolution Issues
   o
   Symptoms: Domain not resolving or pointing to the wrong IP address.
   o
   Resolution: Verify Route 53 records for accuracy. Check DNS propagation and TTL
   settings. Confirm the health of associated resources (e.g., Load Balancer, EC2
   instances). Investigate any issues reported in Route 53 health checks.
5. CloudWatch: Alarm Triggering Incorrectly
   o
   Symptoms: CloudWatch alarms triggering when they shouldn’t or not triggering
   when expected.
   o
   Resolution: Review alarm configurations, thresholds, and evaluation periods. Check
   associated metrics for accuracy. Verify the underlying issue causing the alarm
   condition.
6. SSL: Certificate Expiry
   o
   Symptoms: SSL certificate expired or causing browser warnings.
   o
   Resolution: Renew or replace the SSL certificate. Update the certificate in the
   associated AWS services (e.g., Load Balancer, CloudFront). Monitor certificate expiry
   using AWS Certificate Manager (ACM) or other tools.
7. Cloud Front: Content Not Updating
   o
   Symptoms: Changes in the origin not reflected in CloudFront distribution.
   o
   Resolution: Invalidate CloudFront cache for updated content. Check CloudFront
   distribution settings, origin configurations, and TTL settings. Ensure that the origin is
   serving the latest content.
8. Elastic Cache: Cache Node Issues
   o
   Symptoms: High latency or cache node failures in Elastic Cache.
   o
   Resolution: Monitor CloudWatch metrics for Elastic Cache. Investigate and resolve
   issues such as memory pressure, evictions, or network problems. Consider scaling the
   cache cluster if needed.
9. RDS: Database Performance Degradation
   o
   Symptoms: Slow queries or high database latency.

***

## Page 5

o
Resolution: Analyze CloudWatch metrics for RDS. Optimize database queries, adjust
instance size, or consider scaling read replicas. Monitor storage capacity and perform
database maintenance tasks. 10. IAM User: Access Denied
o
Symptoms: IAM user unable to perform expected actions.
o
Resolution: Review IAM user policies and roles. Ensure the user has the necessary
permissions for the intended actions. Check for any explicit "Deny" policies that
might override "Allow" policies. 11. Deployment: Application Rollback
o
Symptoms: Deployment of an application version introduces issues.
o
Resolution: Implement a rollback mechanism in your deployment strategy.
Investigate logs and metrics to identify the problematic version. Rollback to the
previous stable version and analyze the root cause of the issue before attempting a
re-deployment. 12. CloudFormation: Stack Creation Failure
o
Symptoms: CloudFormation stack creation fails.
o
Resolution: Check CloudFormation events and logs for error messages. Validate the
template syntax. Review IAM roles and permissions. Identify and resolve resource
dependencies. Use AWS CloudFormation StackSets for multiple accounts/regions.

***

# Incident Response Runbook (7 YOE)

A senior DevOps or SRE engineer is expected to **lead** an incident, not just debug it. This means structured communication, fast mitigation, and systematic review — even under pressure.

***

## The Incident Lifecycle

```
Detect → Triage → Declare → Mitigate → Resolve → Review
```

***

## Phase 1: Detect

An incident starts when an alert fires, a customer reports it, or a team member notices anomalous behaviour. The first goal is **not** to find the root cause — it is to determine **scope and user impact**.

### Initial Triage Questions (answer in < 5 minutes)

1. **What is broken?** (which service/area)
2. **Who is affected?** (all users, specific region, specific tenant?)
3. **How severe?** (complete outage, degraded performance, data integrity risk?)
4. **When did it start?** (correlates with deployments, changes, traffic spikes)
5. **Is it still happening?** (could be a transient blip)

### Signal Sources

| Signal              | Azure                                 | Generic                                   |
| ------------------- | ------------------------------------- | ----------------------------------------- |
| Latency/Error spike | Application Insights → Failures blade | Grafana → Error Rate panel                |
| Infra anomaly       | Azure Monitor → Metrics Explorer      | Prometheus → `kube_node_status_condition` |
| Log errors          | Log Analytics → KQL                   | Kibana / Loki                             |
| Synthetic health    | Azure Monitor availability tests      | Blackbox Exporter                         |

***

## Phase 2: Declare

If the incident exceeds a severity threshold (see below), **declare it**. Do not wait until you know the root cause. Declaration gates proper communication and ensures the right people are engaged.

### Severity Levels

| Severity          | Definition                                                   | Response SLA                                     |
| ----------------- | ------------------------------------------------------------ | ------------------------------------------------ |
| **P0 — Critical** | Complete service outage. Revenue or data integrity impacted. | Immediate — wake up on-call + incident commander |
| **P1 — High**     | Major feature broken. Significant user impact.               | 15 minutes                                       |
| **P2 — Medium**   | Partial degradation. Workarounds exist.                      | 1 hour                                           |
| **P3 — Low**      | Minor issue. Small % of users.                               | Next business day                                |

### Declare in the Incident Channel (template)

```
🚨 INCIDENT DECLARED — P[X]
Time: 2026-04-21 14:32 UTC
Summary: [checkout-service] returning 503 errors for 40% of users in eu-west-1
Impact: Customers cannot complete orders. Revenue impact ~$X/min.
Incident Commander: @alice
Lead Engineer: @bob
Status Page: [link] — Updated to "Investigating"
Zoom Bridge: [link]
```

***

## Phase 3: Triage and Mitigate

The goal of mitigation is to **reduce user impact as fast as possible**, even if you don't know the root cause yet. Stabilize first. Investigate second.

### Mitigation Strategies (in order of speed)

1. **Feature flag / toggle off** the broken feature (fastest — zero risk).
2. **Rollback** the most recent deployment: `kubectl rollout undo deployment/<name>`.
3. **Traffic shift** — route away from the broken region or pod set.
4. **Scale up** replicas if the issue is load-related.
5. **Restart affected pods** as a last resort (this does not fix root cause but may buy time).
6. **Manual failover** to secondary region or backup database replica.

### Communication Every 15–30 Minutes

Even if you have no new findings, send a status update:

```
UPDATE 14:47 UTC
Progress: Identified the issue is in the auth-service, not checkout.
Action: Rolling back auth-service to v2.3.1. ETA: 5 minutes.
Current impact: Same as initial report.
Next update: 15:00 UTC
```

***

## Phase 4: Resolve

The incident is resolved when:

- User-facing metrics (error rate, latency) return to normal SLO levels.
- A root cause hypothesis has been confirmed (even if a permanent fix is not yet deployed).
- The on-call rotation is stood down.

### Resolve Template

```
✅ INCIDENT RESOLVED — P[X]
Time: 2026-04-21 15:02 UTC
Duration: 30 minutes
Root Cause (preliminary): auth-service v2.4.0 introduced a misconfigured JWT signing key path, causing all token validation to fail.
Mitigation: Rolled back to auth-service v2.3.1.
Status Page: Updated to "Resolved"
Post-Mortem: Scheduled for 2026-04-22 10:00 UTC
```

***

## Phase 5: Post-Mortem (Blameless)

A blameless post-mortem looks for **systemic failures**, not individual mistakes. The output is a set of concrete action items that prevent the same class of failure recurring.

### Post-Mortem Document Structure

```markdown
# Post-Mortem: [Incident Title]

**Date:** 2026-04-21  
**Duration:** 30 minutes  
**Severity:** P1  
**Authors:** @alice, @bob  
**Status:** Action Items In Progress

## Summary

One sentence: what broke, why it broke, and what the impact was.

## Timeline

| Time (UTC) | Event                                                     |
| ---------- | --------------------------------------------------------- |
| 14:30      | First error alert fired: auth-service 503 rate > 10%      |
| 14:32      | On-call engineer acknowledged                             |
| 14:38      | Root cause narrowed to auth-service after log correlation |
| 14:50      | Rollback to v2.3.1 initiated                              |
| 15:02      | Error rate returned to < 0.1%                             |

## Root Cause Analysis (5 Whys)

- **Why** did users get 503 errors? → auth-service was rejecting all JWT tokens.
- **Why** was it rejecting all tokens? → The signing key path was wrong in the config.
- **Why** was the config wrong? → A new environment variable name was introduced in v2.4.0 but the deployment ConfigMap was not updated.
- **Why** was the ConfigMap not updated? → The deploy step ran before the ConfigMap update step in the pipeline (ordering bug).
- **Why** wasn't this caught in staging? → Staging ConfigMaps are managed separately and were already updated manually.

## What Went Well

- Alert fired within 2 minutes of degradation start.
- Rollback procedure was documented and ran cleanly in under 10 minutes.
- Communication was regular and clear throughout.

## What Went Poorly

- Staging and production ConfigMaps diverged without detection.
- Initial triage looked at the wrong service (checkout) for 6 minutes.

## Action Items (SMART format)

| Action                                                                                    | Owner    | Due Date   | Priority |
| ----------------------------------------------------------------------------------------- | -------- | ---------- | -------- |
| Add pipeline step that validates ConfigMap key names match the app environment definition | @bob     | 2026-04-28 | P0       |
| Create automated diff check between staging and production ConfigMaps on every deploy     | @alice   | 2026-05-02 | P1       |
| Add a synthetic canary test that validates a full auth token round-trip post-deploy       | @charlie | 2026-05-05 | P1       |
```

***

## SLO Burn Rate Alerting

A **burn rate** measures how fast you are consuming your error budget relative to the rate that would exhaust it exactly by the end of the SLO window.

Burn rate of **1** = consuming budget at exactly the sustainable rate (you exhaust it at month-end).
Burn rate of **14** = consuming budget 14× faster (you exhaust a 30-day budget in ~2 days).

### Multi-Window, Multi-Burn-Rate Alerting (Google SRE Workbook approach)

| Alert                | Short Window | Long Window | Burn Rate | Priority           | Action                  |
| -------------------- | ------------ | ----------- | --------- | ------------------ | ----------------------- |
| Fast burn (critical) | 5m           | 1h          | 14×       | Page immediately   | Immediate investigation |
| Slow burn (warning)  | 30m          | 6h          | 3×        | Slack notification | Investigate this sprint |

### PromQL for 14× Burn Rate (1h window)

```promql
# Example: 30-day SLO = 99.9% → error budget = 0.1%
# 14x burn rate over 1h window:
(
  sum(rate(http_requests_total{status=~"5.."}[1h]))
  /
  sum(rate(http_requests_total[1h]))
) > (14 * 0.001)
```

### Azure Monitor equivalent (KQL)

```kusto
let slo_threshold = 0.001; // 99.9% SLO error budget
let burn_rate = 14.0;
requests
| where timestamp > ago(1h)
| summarize
    total = count(),
    failed = countif(success == false)
  by bin(timestamp, 5m)
| extend error_rate = toreal(failed) / toreal(total)
| where error_rate > (burn_rate * slo_threshold)
```

***

## Communication Best Practices

### Say this — not that

| ❌ Don't Say                     | ✅ Do Say                                                                                               |
| -------------------------------- | ------------------------------------------------------------------------------------------------------- |
| "I think the database is down."  | "Metrics show db query latency exceeding 5s. I'm confirming if it's the primary or replica."            |
| "Restarting everything."         | "I'm restarting the auth-service pods as a mitigation while I continue investigating the config issue." |
| "Bob shouldn't have done that."  | "The system allowed the config to be deployed without validation. We'll add a check."                   |
| "I don't know what's happening." | "I've ruled out the database and network. I'm now investigating the application layer."                 |

***

## On-Call Rotation and Escalation Policy

### Healthy On-Call Design

1. **Rotation:** Each engineer is on-call for at most 1 week, with at least 5 weeks off between stints.
2. **Shadowing:** Junior engineers shadow before taking solo on-call.
3. **Runbook coverage:** Every alert must have a linked runbook. If no runbook exists, the alert should not be paging.
4. **Escalation chain:** Every primary on-call has a named secondary who auto-escalates after **10 minutes** of no acknowledgement.

### Alert Quality Standards

An alert is worth paging an engineer at 3 AM **only if** it meets all three criteria:

1. **Urgent** — delayed response will make it worse.
2. **Actionable** — the on-call engineer can do something specific right now.
3. **Customer-impacting** — there is measurable user harm, not just an internal metric anomaly.

If an alert does not meet all three, it belongs in a Slack channel or a Jira ticket, not a phone call.

***

## Scenario 1: Prometheus "Cardinality Explosion"
**Symptom:** Prometheus is OOMing and slow. Memory usage spiked suddenly.
**Diagnosis:** A new metric was introduced with a "high cardinality" label (e.g., `user_id` or `timestamp` in a label).
**Fix:** 
1. Identify the metric: `topk(10, count by (__name__) ({__name__=~".+"}))`.
2. Remove the high-cardinality label in the application code or use Prometheus `relabel_configs` to drop it.

## Scenario 2: Grafana Dashboard "Data Gap"
**Symptom:** Graphs show gaps or "No Data" during high traffic.
**Diagnosis:** Prometheus is "throttling" scrapes or the target is too slow to respond, causing a timeout.
**Fix:** 
1. Increase the `scrape_timeout` in Prometheus config.
2. Optimize the `/metrics` endpoint of the application (e.g., pre-calculate metrics).


### Scenario 3: Prometheus "Target Scrape Latency"
**Symptom:** Metrics are "choppy" and alerts are flapping.
**Diagnosis:** The `/metrics` endpoint takes 15s to respond, but the scrape interval is 15s.
**Fix:** Increase the scrape interval or optimize the metrics generation logic (e.g., use a cache).
