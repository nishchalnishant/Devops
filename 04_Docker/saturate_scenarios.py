import os

def saturate_scenarios(base_path, content):
    scenario_path = os.path.join(base_path, "scenarios.md")
    # If file is very small or doesn't exist, populate it
    if not os.path.exists(scenario_path) or os.path.getsize(scenario_path) < 100:
        with open(scenario_path, 'w') as f:
            f.write(content)
        print(f"Saturated scenarios in {base_path}")

repo_root = "/Users/nishchalnishant/Documents/GitHub/Devops"

scenarios_data = {
    "01_Linux_and_Scripting": """# Linux Troubleshooting Scenarios

### Scenario 1: The "Zombies" Are Coming
**Problem:** A user reports that they cannot start any new processes. You run `ps aux` and see hundreds of processes in state `Z`.
**Diagnosis:** 
1. Check if the parent process is still alive. Zombies occur when a child finishes but the parent doesn't `wait()` for the exit code.
2. Identify the parent: `ps -o ppid= -p <zombie_pid>`.
3. If the parent is stuck, you must kill the parent. The zombies will then be inherited by `init` (PID 1) and reaped automatically.

### Scenario 2: The "Ghost" Disk Space
**Problem:** `df -h` shows `/var/log` is 100% full. You delete 5GB of log files, but `df -h` still says it's 100% full.
**Diagnosis:** 
1. A process still has an open file descriptor to the deleted file.
2. Run `lsof +L1` or `lsof | grep deleted` to find the process.
3. Restart the service (e.g., `systemctl restart nginx`) to release the file handle and free the space.

### Scenario 3: CPU is 10%, but Load Average is 20
**Problem:** The system feels extremely sluggish. `top` shows CPU usage is low, but the Load Average is high.
**Diagnosis:** 
1. High Load Average without high CPU means processes are stuck in "Uninterruptible Sleep" (State `D`).
2. This is almost always caused by Disk I/O or Network I/O (NFS) bottlenecks.
3. Check `%wa` (I/O Wait) in `top`. Run `iostat -xz 1` to see which disk is bottlenecked.
""",
    "03_Git_and_Version_Control": """# Git Production Scenarios

### Scenario 1: The Accidental Forced Push
**Problem:** A developer accidentally force-pushed to the `main` branch, overwriting 10 commits from other team members.
**Solution:**
1. Do not panic. Git is an immutable ledger.
2. On a local machine that had the latest `main`, find the previous SHA: `git reflog`.
3. Reset your local `main` to the correct SHA: `git reset --hard <correct_sha>`.
4. Force push the correct history back: `git push origin main --force`.

### Scenario 2: The Secret Leak
**Problem:** An AWS Access Key was committed and pushed to a public repository 5 commits ago.
**Solution:**
1. **Immediate:** Rotate the AWS key. The secret is compromised; deleting it from Git doesn't make it safe.
2. Use `git filter-repo` or `BFG Repo-Cleaner` to scrub the string from the entire history.
3. Force push the cleaned history.
4. Notify the team to delete their local clones and re-clone to avoid re-introducing the secret.

### Scenario 3: Resolving the "Impossible" Merge Conflict
**Problem:** Two major feature branches have diverged so much that `git merge` results in 50+ conflicting files.
**Solution:**
1. Use `git rerere` (Reuse Recorded Resolution) to help if you have to do this merge multiple times.
2. Instead of one giant merge, merge `main` into the feature branch frequently.
3. If it's too late, use `git mergetool` with a 3-way merge editor like `Meld` or `KDiff3`.
""",
    "04_Docker": """# Docker Production Scenarios

### Scenario 1: "Too Many Open Files"
**Problem:** Your high-traffic Nginx container starts failing with `socket: too many open files`.
**Diagnosis:**
1. The container is hitting the `ulimit`.
2. Fix it in the `docker run` command using `--ulimit nofile=65535:65535` or in `docker-compose.yml`.
3. Check the host's `/etc/security/limits.conf` as well.

### Scenario 2: The Bloated Image
**Problem:** Your CI/CD pipeline is taking 20 minutes because your Docker image is 5GB.
**Solution:**
1. Use **Multi-Stage Builds** to keep compilers out of the final image.
2. Use a smaller base image (e.g., `python:3.9-slim` or `alpine`).
3. Combine `RUN` commands to reduce the number of layers.
4. Use `.dockerignore` to exclude large, unnecessary files like `.git` or `node_modules`.

### Scenario 3: Container Escape Protection
**Problem:** You are running untrusted code in a container and want to ensure it cannot touch the host OS.
**Solution:**
1. Use the `--read-only` flag to make the container's root filesystem read-only.
2. Use `--cap-drop=ALL` to remove all Linux capabilities.
3. Run the container as a non-root user (`USER 1000`).
4. Use **AppArmor** or **SELinux** profiles to restrict system calls.
""",
    "05_Kubernetes": """# Kubernetes Production Scenarios

### Scenario 1: The `CrashLoopBackOff` Mystery
**Problem:** A pod is stuck in `CrashLoopBackOff`.
**Diagnosis:**
1. Run `kubectl logs <pod_name>`. If it's empty, try `kubectl logs <pod_name> --previous`.
2. Check `kubectl describe pod <pod_name>`. Look for exit codes.
    - Exit Code 137: OOMKilled (Increase memory limits).
    - Exit Code 1: Application error (Check config/DB connection).

### Scenario 2: The "Stuck" Namespace
**Problem:** You ran `kubectl delete namespace prod`, but it's stuck in `Terminating` state forever.
**Diagnosis:**
1. K8s is waiting for some resources (like Finalizers) to be cleaned up.
2. Check for leftover resources: `kubectl get all -n prod`.
3. Check for stuck custom resources: `kubectl api-resources --verbs=list --namespaced -o name | xargs -n 1 kubectl get -n prod`.
4. If desperate, patch the namespace to remove finalizers: `kubectl patch ns prod -p '{"spec":{"finalizers":null}}' --type=merge`.

### Scenario 3: Sudden Latency in Microservices
**Problem:** App A talks to App B via a K8s Service. Suddenly, latency jumps from 10ms to 500ms.
**Diagnosis:**
1. Check **Kube-proxy** logs. Is it failing to update IPTables?
2. Check **CoreDNS** performance. Is the service name resolution slow?
3. Check for **Network Policy** overhead or CNI (e.g., Calico/Cilium) issues.
4. Check if the Pod is hitting its CPU `limit`. K8s "throttles" processes that exceed limits, causing massive latency spikes.
""",
    "10_Terraform": """# Terraform Production Scenarios

### Scenario 1: The "Manual Change" Disaster
**Problem:** Someone logged into the AWS console and manually deleted a Load Balancer that Terraform manages.
**Solution:**
1. Run `terraform plan`. Terraform will detect that the resource is missing from the real world but exists in the state.
2. It will propose to "Create" it again.
3. Run `terraform apply` to restore the desired state.

### Scenario 2: The Stuck State Lock
**Problem:** You try to run `terraform apply`, but it fails with "Error: Error acquiring the state lock". No one else is running Terraform.
**Solution:**
1. Usually happens if a previous run crashed.
2. Find the Lock ID in the error message.
3. Run `terraform force-unlock <LOCK_ID>`.
4. Ensure you communicate with the team before doing this!

### Scenario 3: Version Mismatch
**Problem:** You upgraded Terraform to v1.5, but your teammate is on v1.0. The state file is now incompatible.
**Solution:**
1. Use a tool like `tfenv` to manage Terraform versions.
2. Add a `required_version` block in your `provider.tf` to enforce a specific version for the whole team.
""",
    "15_Observability_and_SRE": """# SRE Incident Scenarios

### Scenario 1: The 5xx Spike at 2 AM
**Problem:** Your dashboard shows a sudden spike in 502 Bad Gateway errors.
**Resolution:**
1. Check the Load Balancer logs: Is it a "Backend Connection Refused"?
2. Check the App logs: Is the service crashing? Is it a Database timeout?
3. Check for recent deployments: Was there a change in the last 15 minutes? If yes, **Roll back first, ask questions later.**

### Scenario 2: Alert Fatigue
**Problem:** The SRE team is receiving 500 Slack alerts a day. Most are ignored.
**Resolution:**
1. Audit all alerts. If an alert doesn't require a human to take action immediately, demote it to a "Warning" or a dashboard-only metric.
2. Implement **Symptom-based Alerting**. Don't alert on "High CPU"; alert on "High Latency" or "High Error Rate" (the symptoms users feel).

### Scenario 3: The "Cascading Failure"
**Problem:** Service A fails, causing Service B to retry aggressively, which then crashes Service C.
**Resolution:**
1. Implement **Circuit Breakers** (using a Service Mesh like Istio). If Service A is failing, stop sending requests to it immediately to give it room to recover.
2. Use **Exponential Backoff with Jitter** for retries to avoid "Thundering Herd" problems.
"""
}

for folder, content in scenarios_data.items():
    saturate_scenarios(os.path.join(repo_root, folder), content)
