# Shell Scripting for DevOps

```
Shell Scripting for DevOps
├── Why Shell Scripting in DevOps
│   ├── Automate server setup (install packages, configure services)
│   ├── Write deployment pipelines
│   ├── Manage logs and backups
│   ├── Monitor system resources
│   └── Integrate: Docker, Jenkins, Kubernetes
├── Script Structure
│   ├── Shebang: #!/bin/bash — tells kernel which interpreter to use
│   └── Comments: # explain the why, not the what
├── Essential DevOps Scripts
│   ├── 1. Package installation (apt update && apt install -y)
│   ├── 2. Disk usage report (df -h > file)
│   ├── 3. Timestamped backup (tar -czf backup_$(date +%F).tar.gz)
│   ├── 4. Jenkins job trigger (curl -X POST with auth token)
│   ├── 5. Docker container health check (docker ps | grep -q)
│   ├── 6. System health report (uptime, free -m, df -h, ps top procs)
│   ├── 7. Service auto-restart (systemctl is-active + systemctl start)
│   ├── 8. Log rotation (find + mtime +7, mv to archive, gzip)
│   ├── 9. Git auto pull (git pull origin main via cron)
│   ├── 10. Docker cleanup (prune containers, images, volumes)
│   ├── 11. PostgreSQL backup (pg_dump with date in filename)
│   ├── 12. Kubernetes non-running pod check (kubectl get pods | grep -v Running)
│   ├── 13. Jenkins job trigger with token (curl parameterized)
│   ├── 14. Port availability check (lsof -i:PORT)
│   └── 15. CI build pipeline (set -e + npm install/build/test)
├── Idempotent Scripting
│   ├── Check before act: if [ ! -d /path ]; then mkdir; fi
│   ├── id -u devuser &>/dev/null || useradd devuser
│   └── Package managers: apt-get install -y is idempotent
├── Tool Selection: When to Use What
│   ├── Bash: zero deps, best for bootstrap, poor at complex logic
│   ├── Python: rich libraries (boto3, k8s), best for complex logic/APIs
│   └── Go: single static binary, best for distribution, goroutines for concurrency
├── Script Best Practices
│   ├── Error Handling
│   │   ├── set -e: exit on any error
│   │   ├── set -u: treat unset variables as errors
│   │   ├── set -o pipefail: fail pipeline if any stage fails
│   │   └── trap 'echo "Error on line $LINENO"' ERR
│   ├── Logging
│   │   ├── exec 1>>"$LOG_FILE" 2>&1: redirect all output to log
│   │   └── Timestamped messages: [$(date '+%Y-%m-%d %H:%M:%S')]
│   ├── Functions
│   │   ├── log(), cleanup() as named functions
│   │   └── trap cleanup EXIT: always clean up on exit
│   └── Configuration Variables
│       ├── Define at top of script, grouped
│       └── Validate with: : "${VAR:?VAR must be set}"
└── Advanced Patterns
    ├── Parallel Execution
    │   ├── ssh "$server" "cmd" & (background) + wait (rejoin)
    │   └── Controlled parallelism: while [[ $(jobs -r | wc -l) -ge $MAX ]]
    ├── Retry Logic
    │   ├── for loop with max retries + sleep delay
    │   └── Exponential backoff: sleep $((2**attempt)) + jitter
    └── Color Output
        ├── RED='\033[0;31m', GREEN='\033[0;32m', NC='\033[0m'
        └── log_error, log_success, log_warn functions
```

## First Principles

- **A shell script is a series of system calls, not magic.** Every command in a script (`apt install`, `mkdir`, `cp`) is a program that ultimately calls the kernel via syscalls. Understanding this explains why scripts can fail with "Permission denied" or "Too many open files" — the underlying syscall failed.
- **`set -euo pipefail` exists because bash defaults to permissiveness.** By default, bash continues after errors, ignores unset variables (treating them as empty strings), and returns the last command's exit code for pipelines. None of these defaults are safe for automation. The flags explicitly opt into strict mode.
- **Idempotency is a guarantee, not a feature.** In configuration management and deployment automation, a script may be run dozens of times (retries, convergence runs, dry-runs). If it's not idempotent, each run has unpredictable side effects. The design principle: describe the desired final state, not the steps to get there.
- **`trap` is the exception handler for shell scripts.** Without it, a script that creates temp files and then fails halfway through leaves those files behind forever. `trap 'cleanup' EXIT` runs the cleanup function in all exit cases — success, error, or signal.
- **Parallel execution with `&` and `wait` is the shell's concurrency primitive.** It's not threads — each `&` forks a new child process. The trade-off: isolation (crashes don't propagate) but higher memory and startup overhead than threads.
- **Tool selection is a trade-off between startup cost and capability.** Bash has zero dependencies — it exists on every Linux system. Python needs an interpreter. Go needs compilation but produces a self-contained binary. The right tool depends on the execution environment and complexity of the logic.

## Why Shell Scripting in DevOps

Shell scripting is essential for DevOps engineers to automate repetitive tasks and create reliable, reproducible processes.

**Key Use Cases:**
- Automate server setups (install packages, configure services)
- Write deployment scripts
- Manage logs and backups
- Monitor system resources
- Integrate with tools like Docker, Jenkins, Kubernetes

***

## Basic Shell Script Structure

```bash
#!/bin/bash

# This is a comment
echo "Hello, DevOps!"
```

The shebang (`#!/bin/bash`) tells the system which interpreter to use.

***

## Essential DevOps Scripts

### 1. Install Packages

```bash
#!/bin/bash
sudo apt update && sudo apt install -y nginx
```

**Purpose:** Updates system package info and installs NGINX web server.

### 2. Monitor Disk Usage

```bash
#!/bin/bash
df -h > disk_usage_report.txt
```

**Purpose:** Saves disk space usage to a file for review later.

### 3. Backup Files

```bash
#!/bin/bash
tar -czf backup_$(date +%F).tar.gz /path/to/directory
```

**Purpose:** Compresses a directory into a `.tar.gz` backup file with the current date.

### 4. Jenkins Job Trigger

```bash
#!/bin/bash
curl -X POST http://jenkins.local/job/your-job-name/build \
  --user your-user:your-api-token
```

**Purpose:** Triggers a Jenkins CI job remotely using a POST request and authentication.

### 5. Docker Container Health Check

```bash
#!/bin/bash
if docker ps | grep -q my_container; then
  echo "Container is running"
else
  echo "Container is down"
fi
```

**Purpose:** Checks if a specific Docker container (`my_container`) is running.

### 6. System Health Check

```bash
#!/bin/bash
echo "CPU Load:"; uptime
echo -e "\nMemory Usage:"; free -m
echo -e "\nDisk Usage:"; df -h
echo -e "\nTop 5 Memory Consuming Processes:"; ps aux --sort=-%mem | head -n 6
```

**Purpose:** Shows system metrics like CPU load, memory, disk, and top memory-consuming processes.

### 7. Service Restart on Failure

```bash
#!/bin/bash
SERVICE="nginx"
if ! systemctl is-active --quiet $SERVICE; then
  echo "$SERVICE is down. Restarting..."
  systemctl start $SERVICE
else
  echo "$SERVICE is running"
fi
```

**Purpose:** Checks if a service is down and restarts it automatically.

### 8. Log Rotation Script

```bash
#!/bin/bash
LOG_DIR="/var/log/myapp"
ARCHIVE_DIR="/var/log/myapp/archive"
mkdir -p $ARCHIVE_DIR
find $LOG_DIR/*.log -mtime +7 -exec mv {} $ARCHIVE_DIR \;
gzip $ARCHIVE_DIR/*.log
```

**Purpose:** Moves logs older than 7 days to an archive and compresses them.

### 9. Git Auto Pull

```bash
#!/bin/bash
cd /home/ubuntu/my-repo
git pull origin main
```

**Purpose:** Automatically pulls the latest code from GitHub (useful with cron jobs).

### 10. Docker Cleanup Script

```bash
#!/bin/bash
docker container prune -f
docker image prune -f
docker volume prune -f
```

**Purpose:** Frees disk space by removing unused Docker containers, images, and volumes.

### 11. PostgreSQL Database Backup

```bash
#!/bin/bash
BACKUP_DIR="/backups"
DB_NAME="mydb"
USER="postgres"
mkdir -p $BACKUP_DIR
pg_dump -U $USER $DB_NAME > $BACKUP_DIR/${DB_NAME}_$(date +%F).sql
```

**Purpose:** Creates a daily backup of a PostgreSQL database.

### 12. Kubernetes Pod Status Checker

```bash
#!/bin/bash
NAMESPACE="default"
kubectl get pods -n $NAMESPACE | grep -v Running
```

**Purpose:** Lists non-running pods in a Kubernetes namespace.

### 13. Jenkins Job Trigger with Token

```bash
#!/bin/bash
JENKINS_URL="http://jenkins.local"
JOB_NAME="my-job"
USER="your-user"
API_TOKEN="your-token"
curl -X POST "$JENKINS_URL/job/$JOB_NAME/build" --user $USER:$API_TOKEN
```

**Purpose:** Triggers a Jenkins job using username + token for security.

### 14. Check Port Availability

```bash
#!/bin/bash
PORT=8080
if lsof -i:$PORT > /dev/null; then
  echo "Port $PORT is in use."
else
  echo "Port $PORT is free."
fi
```

**Purpose:** Checks if a specific port is being used by any process.

### 15. Simple CI Build Script

```bash
#!/bin/bash
set -e  # Exit on error

echo "Starting build..."
npm install
npm run build
npm test
echo "Build completed successfully"
```

**Purpose:** Runs a typical CI build pipeline with error handling.

***

## 3. Advanced Pattern: Idempotent Scripting

In DevOps, a script should be **Idempotent**—running it multiple times results in the same state without errors.

```bash
#!/bin/bash

# Anti-Pattern: Failing if directory exists
# mkdir /data/logs

# Idempotent Pattern: Check before act
if [ ! -d "/data/logs" ]; then
  mkdir -p /data/logs
fi

# Idempotent Pattern: User management
id -u devuser &>/dev/null || useradd devuser

# Idempotent Pattern: Apt install (Built-in idempotency)
sudo apt-get install -y nginx
```

### Senior Logic & Trickiness: Tool Selection
| Feature | Shell (Bash) | Python | Go |
| :--- | :--- | :--- | :--- |
| **Bootstrap** | Best (Zero deps) | Moderate (Needs interpreter) | Hard (Needs compilation) |
| **Logic** | Poor (String-heavy) | Best (Rich libraries) | Moderate (Strict typing) |
| **Concurrency** | Hacky (`&`, `wait`) | Good (AsyncIO/Threads) | **Best (Goroutines)** |
| **Distribution** | Single file | Venv/Pip dependency hell | **Best (Static Binary)** |

***

## Script Best Practices

### 1. Error Handling

```bash
#!/bin/bash
set -e          # Exit immediately on error
set -u          # Treat unset variables as errors
set -o pipefail # Pipeline fails if any command fails

trap 'echo "Error on line $LINENO"' ERR
```

### 2. Logging

```bash
#!/bin/bash
LOG_FILE="/var/log/myscript.log"
exec 1>>"$LOG_FILE" 2>&1  # Redirect stdout and stderr to log
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Script started"
```

### 3. Functions

```bash
#!/bin/bash

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

cleanup() {
  log "Cleaning up temporary files..."
  rm -rf /tmp/myapp/*
}

trap cleanup EXIT
```

### 4. Configuration Variables

```bash
#!/bin/bash

# Configuration section
APP_NAME="myapp"
APP_DIR="/opt/$APP_NAME"
LOG_DIR="/var/log/$APP_NAME"
BACKUP_RETENTION_DAYS=7

# Validate required variables
: "${APP_NAME:?APP_NAME must be set}"
: "${APP_DIR:?APP_DIR must be set}"
```

***

## Advanced Scripting Patterns

### Parallel Execution

```bash
#!/bin/bash

# Run tasks in parallel, wait for all to complete
for server in server1 server2 server3; do
  ssh "$server" "systemctl restart nginx" &
done
wait  # Wait for all background jobs
```

### Retry Logic

```bash
#!/bin/bash

retry() {
  local max=$1
  local delay=$2
  local cmd=$3
  
  for ((i=1; i<=max; i++)); do
    if eval "$cmd"; then
      return 0
    fi
    echo "Attempt $i failed, retrying in $delay seconds..."
    sleep $delay
  done
  return 1
}

# Usage: retry 3 5 "curl -f http://api.example.com"
```

### Color Output

```bash
#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_error()   { echo -e "${RED}ERROR: $1${NC}"; }
log_success() { echo -e "${GREEN}SUCCESS: $1${NC}"; }
log_warn()    { echo -e "${YELLOW}WARN: $1${NC}"; }
```

***

## Summary: Key Takeaways

| Concept | Key Point |
|---------|-----------|
| Shebang | `#!/bin/bash` specifies interpreter |
| Error handling | `set -e`, `set -u`, `set -o pipefail` |
| Functions | Reusable code blocks with local variables |
| Trap | Handle cleanup on EXIT, ERR, or signals |
| Parallel execution | Use `&` and `wait` for concurrent tasks |
| Retry logic | Exponential backoff for transient failures |
| Logging | Timestamp all output, separate stdout/stderr |
