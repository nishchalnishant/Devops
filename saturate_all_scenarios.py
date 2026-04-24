import os

def update_scenario(base_path, content, overwrite=False):
    scenario_path = os.path.join(base_path, "scenarios.md")
    if os.path.exists(scenario_path) and not overwrite:
        # If it's the 43 byte version, overwrite it
        if os.path.getsize(scenario_path) > 100:
            with open(scenario_path, 'a') as f:
                f.write("\n\n" + content)
            print(f"Appended to scenarios in {base_path}")
            return
            
    with open(scenario_path, 'w') as f:
        f.write("# Production Scenarios & Troubleshooting Drills\n\n" + content)
    print(f"Saturated scenarios in {base_path}")

repo_root = "/Users/nishchalnishant/Documents/GitHub/Devops"

scenarios_update = {
    "01_Linux_and_Scripting": """### Scenario 4: The Systemd "203/EXEC" Failure
**Problem:** You created a new service, but it fails to start with `status=203/EXEC`.
**Diagnosis:**
1. This error means systemd found the file but couldn't execute it.
2. Check the **Shebang** (e.g., `#!/bin/bash`). If it's missing or pointing to a non-existent path, it fails.
3. Check **Permissions**: Ensure the script is executable (`chmod +x`).
4. Check **Line Endings**: If the script was edited on Windows, it might have `\r\n` (CRLF), which Linux cannot execute. Use `dos2unix`.

### Scenario 5: High Syscall Latency (eBPF)
**Problem:** A database is slow, but CPU and Disk I/O look normal.
**Diagnosis:**
1. Use `syscount` or `bpftrace` to monitor system calls.
2. You might find a massive number of `futex()` calls, indicating lock contention between threads.
3. Solution: Tune the application's thread pool or optimize the database locking strategy.
""",
    "04_Docker": """### Scenario 4: "Container A cannot talk to Container B"
**Problem:** You have two containers on the same host, but they can't ping each other.
**Diagnosis:**
1. Check if they are on the same **Docker Network**. Containers on the default `bridge` can't use DNS; they must use IP addresses.
2. Recommendation: Use a **User-Defined Bridge Network**. This enables automatic Service Discovery (DNS by container name).
3. Check **Host Firewall**: Ensure `iptables` or `ufw` isn't blocking internal Docker traffic.

### Scenario 5: Dangling Layers & Disk Exhaustion
**Problem:** `docker build` fails with `No space left on device`, but `df -h` shows the disk is 50% free.
**Diagnosis:**
1. You might be out of **Inodes** if you have millions of tiny files in your build context.
2. Or, you have massive amounts of **Dangling Images** and **Unused Build Cache**.
3. Fix: Run `docker system prune -a --volumes` to reclaim space.
""",
    "06_Jenkins": """### Scenario 1: The "Zombie" Jenkins Build
**Problem:** A build is running for 24 hours and won't stop, even when you click the "Abort" (red X) button.
**Solution:**
1. Access the **Jenkins Script Console** (`Manage Jenkins > Script Console`).
2. Run this Groovy script to force-kill the thread:
   ```groovy
   Jenkins.instance.getItemByFullName("JobName").getBuildByNumber(123).finish(
       hudson.model.Result.ABORTED, 
       new java.io.IOException("Aborting build manually")
   );
   ```

### Scenario 2: Agent Disconnected Intermittently
**Problem:** Builds fail randomly because the "Agent disconnected during build."
**Diagnosis:**
1. Check the **Java Heap Space** on the Agent. If it's too low, the JVM crashes under load.
2. Check **SSH Timeouts**: In the Agent configuration, increase the "Connection Timeout."
3. Check **Clock Skew**: If the Master and Agent have different system times, the SSH handshake might fail. Use NTP to sync clocks.

### Scenario 3: Shared Library Versioning Disaster
**Problem:** You updated a global Shared Library, and now 50 pipelines are failing.
**Solution:**
1. **Never** point all pipelines to the `master` branch of a library.
2. Use **Versions/Tags**. In the `Jenkinsfile`, specify the version: `@Library('my-shared-lib@v1.2.0')`.
3. Roll back by changing the version in the failing pipelines.
""",
    "07_GitHub_Actions": """### Scenario 1: OIDC Trust Policy Failure
**Problem:** Your GitHub Action fails to assume an AWS IAM Role via OIDC.
**Diagnosis:**
1. Check the **Trust Policy** in AWS. It must exactly match the GitHub repo and organization name.
2. Check the **Audience (aud)**: It must be `sts.amazonaws.com`.
3. Check the **Subject (sub)**: It should follow the pattern `repo:org/repo:ref:refs/heads/main`.

### Scenario 2: Runner Security - Secret Leakage from PRs
**Problem:** A contributor submits a PR that prints `${{ secrets.PROD_KEY }}` in the logs.
**Solution:**
1. GitHub Actions automatically masks secrets in logs, but attackers can use `base64` or `split` to bypass this.
2. **Best Practice:** Never run workflows on `pull_request_target` from untrusted forks if they have access to secrets.
3. Use **Environments** with "Required Reviewers" for any job that uses production secrets.
""",
    "08_GitLab_CI": """### Scenario 1: Shared Runner Exhaustion
**Problem:** Your builds are stuck in "Pending" for 30 minutes because the shared runners are busy.
**Solution:**
1. Set up a **Local/Private Runner**. Install the `gitlab-runner` binary on an EC2 instance.
2. Register it with your project using the Registration Token.
3. Use **Tags** in your `.gitlab-ci.yml` to ensure jobs only run on your fast, private runner.

### Scenario 2: DAG (Directed Acyclic Graph) Optimization
**Problem:** Your pipeline is slow because the `deploy` stage waits for ALL `test` jobs to finish, even if the one it depends on is done.
**Solution:**
1. Use the `needs` keyword:
   ```yaml
   deploy_app:
     stage: deploy
     needs: ["build_app"] # Starts as soon as build_app finishes
   ```
2. This eliminates stage bottlenecks and can shave minutes off your CI time.
""",
    "10_Terraform": """### Scenario 4: The "State Drift" Mystery
**Problem:** You changed a Security Group in the AWS console. `terraform plan` says "No changes", but you know it's different.
**Diagnosis:**
1. Terraform only tracks what is in its **State File**. If you manually add a tag or a rule that Terraform doesn't manage, it might ignore it.
2. Use `terraform plan -refresh-only` to sync the state with reality without making changes.
3. Recommendation: Always use **drift detection** tools like `Driftctl`.

### Scenario 5: `Terraform Apply` Timeout
**Problem:** Creating an RDS cluster takes 20 minutes, and Terraform fails with a "Timeout" error, leaving the state in a mess.
**Solution:**
1. Increase the `timeouts` block in the resource definition:
   ```hcl
   resource "aws_db_instance" "default" {
     timeouts {
       create = "60m"
       delete = "2h"
     }
   }
   ```
2. If it still fails, use `terraform refresh` to see if the resource eventually finished creating, then `terraform import` if needed.
""",
    "11_Ansible": """### Scenario 1: Privilege Escalation (Become) Failure
**Problem:** Ansible fails with `Missing sudo password` even though you have SSH access.
**Solution:**
1. Use `become: yes` in your task.
2. Pass the password via `--ask-become-pass` or better, use **Ansible Vault** to store the `ansible_become_password`.
3. Ensure the user on the target host is in the `sudoers` file with `NOPASSWD`.

### Scenario 2: Performance Bottleneck on 500+ Hosts
**Problem:** Running a playbook on 500 servers takes 2 hours.
**Solution:**
1. Enable **SSH Pipelining** in `ansible.cfg` to reduce the number of SSH connections.
2. Increase the `forks` (default is 5). Set it to 50 or 100 depending on your control node's CPU.
3. Use `strategy: free` to allow each host to run tasks as fast as they can without waiting for others.
""",
    "13_AWS": """### Scenario 1: VPC Peering Routing Issue
**Problem:** You peered VPC-A and VPC-B, but they can't talk.
**Diagnosis:**
1. **Peering Connection:** Is it in the `Active` state?
2. **Route Tables:** Did you add the route for the CIDR of VPC-B in VPC-A's route table (and vice-versa)?
3. **Security Groups:** Does the SG in VPC-B allow traffic from the CIDR of VPC-A?

### Scenario 2: S3 "Access Denied" Paradox
**Problem:** A user has `s3:FullAccess` in IAM, but still gets "Access Denied" when reading a bucket.
**Diagnosis:**
1. Check the **S3 Bucket Policy**. Explicit `Deny` always wins over an `Allow`.
2. Check for **Service Control Policies (SCPs)** at the AWS Organizations level.
3. Check for **VPC Endpoint Policies** if the user is accessing S3 from inside a VPC.
""",
    "14_DevSecOps": """### Scenario 1: SCA "Vulnerability Overload"
**Problem:** A scan shows 500 vulnerabilities in your Node.js app. The developers are overwhelmed.
**Solution:**
1. **Prioritize:** Filter by `Severity: Critical` and `Fix Available: Yes`.
2. **Contextual Analysis:** Check if the vulnerable function is actually used in your code.
3. **Policy:** Set a "Breaking Threshold". Fail the build only for `Critical` CVEs with an exploit score > 9.0.

### Scenario 2: The Secret Scan False Positive
**Problem:** Gitleaks blocks a PR because it found a "Secret", but it's just a test API key for a sandbox.
**Solution:**
1. Do not ignore it manually every time.
2. Add the fingerprint to `.gitleaksignore` or use the `allowlist` section in your config.
3. **Better:** Use environment variables for all keys, even for testing, to maintain a "No Secrets in Code" culture.
""",
    "16_Platform_Engineering_and_FinOps": """### Scenario 1: Identifying "Orphaned" Cloud Spend
**Problem:** Your AWS bill jumped by $2000, but you haven't deployed anything new.
**Solution:**
1. Use **AWS Cost Explorer** with "Group By: Service."
2. Look for **Unattached EBS Volumes**: When you delete an EC2 instance, the disk often stays behind.
3. Look for **Idle Load Balancers** and **Elastic IPs** that aren't attached to anything (AWS charges for idle IPs!).
4. Automate cleanup with a tool like **CloudCustodian**.

### Scenario 2: The "Self-Service" Bottleneck
**Problem:** Developers complain that it takes 3 days to get a new S3 bucket because they have to wait for DevOps.
**Solution:**
1. Build a **Self-Service Catalog** using Terraform Modules.
2. Let developers submit a YAML file (or use Backstage) to request a bucket.
3. Use a CI/CD pipeline to validate the request (naming conventions, encryption) and auto-apply the Terraform.
"""
}

for folder, content in scenarios_update.items():
    update_scenario(os.path.join(repo_root, folder), content)
