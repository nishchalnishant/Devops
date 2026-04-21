# 2. Programming / Scripting

### A. Python Programming

Python is often considered the "Swiss Army Knife" of DevOps due to its readability and powerful libraries.

#### Basics

* Loops & Conditionals: Essential for controlling the flow of automation scripts, such as iterating through a list of servers or checking if a service is running.
* Functions: Used to write reusable blocks of code, reducing redundancy in large automation projects.
* OOPs (Object-Oriented Programming): Allows you to model real-world infrastructure components (like "Server" or "Database") as objects to build scalable software.
* Exception / File Handling: Crucial for making scripts "robust" by handling errors gracefully and interacting with configuration files or logs.

#### Intermediate

* Boto3: This is the official AWS SDK for Python, used to automate AWS services like launching EC2 instances or managing S3 buckets programmatically.
* Logging: Moving beyond simple "print" statements to track script behavior and troubleshoot issues in production environments.
* Flask: A lightweight web framework used by DevOps engineers to build internal dashboards, REST APIs, or custom webhooks for automation triggers.

***

### B. Shell Scripting

While Python is used for complex logic, Shell Scripting (Bash) is the native language of the Linux terminal and is essential for quick, system-level tasks.

#### Basics

* Automating Backups: Writing scripts to automatically compress and move data to secure storage on a schedule.
* Copying, Moving, and Transferring: Mastering commands to manage files across local and remote directories efficiently.
* User Management / Automation: Automating the creation of users, setting permissions, and managing SSH keys across multiple servers.

#### Intermediate

* Integration with AWS CLI: Using Shell scripts to wrap around AWS Command Line Interface commands for rapid cloud resource management.
* Makefiles: Originally for compiling code, DevOps engineers use Makefiles as a "command runner" to simplify complex multi-step build or deployment processes.
* Integration with Other Tools: Using Shell to "glue" different tools together, such as piping the output of a security scanner into a messaging app notification.



This is Section 2: Programming and Scripting. In a mid-to-senior SRE/DevOps role, you are expected to move beyond simple "automation scripts" and into the realm of Software Engineering for Infrastructure.

You aren't just writing scripts; you are building internal tools, CLI utilities, and automated recovery systems that must be as robust as the production application code.

***

#### 🔹 1. Improved Notes: Engineering the "Glue"

In DevOps, Bash is for system-level operations and "one-liners," while Python (or Go) is for logic-heavy automation and interacting with APIs.

**Bash: The System Interface**

* Idempotency: A senior engineer writes scripts that can be run 10 times and produce the same result. Using `mkdir -p` or checking `if [ ! -f /file ]` is the bare minimum.
* Shell Options (`set` commands): Essential for predictable behavior.
  * `set -e`: Exit immediately if a command fails.
  * `set -o pipefail`: Prevents a pipeline from returning a "success" exit code if a middle command failed.
* Streams & Redirection: Mastering `stderr` (2) vs `stdout` (1). In production, you must redirect logs correctly so they can be captured by logging agents like Fluentbit.

**Python: The Automation Powerhouse**

* SDKs vs. APIs: Understanding how to use Boto3 (AWS), Google Cloud Client Libraries, or Kubernetes Python Client.
* Data Structures for SRE: Using Dictionaries and Sets for fast lookups when comparing infrastructure states (e.g., comparing "desired tags" vs "current tags").
* Concurrency: Using `threading` or `asyncio` to perform tasks in parallel (e.g., rotating passwords for 100 databases simultaneously).

***

#### 🔹 2. Interview View (Q\&A)

Q1: Why is `set -e` or `set -o pipefail` important in a CI/CD pipeline?

* Answer: Without `pipefail`, if a command like `cat config.json | jq .key` fails at the `cat` stage but `jq` succeeds in receiving an empty string, the exit code is `0`. The pipeline continues with a broken config. `pipefail` ensures the entire line fails, stopping the deployment of a corrupted state.

Q2: How do you handle secrets in a Python script meant for production?

* Answer: Never hardcode. I use environment variables or, better yet, a secret manager SDK (AWS Secrets Manager / HashiCorp Vault). I also ensure the script handles the "Secret Not Found" exception gracefully to avoid leaking metadata in logs.

Q3: When would you choose Python over Bash?

* Answer: I use Bash for simple wrappers around CLI tools or quick system tasks. I switch to Python when:
  1. The logic requires complex nested loops/conditionals.
  2. I need to parse complex JSON/YAML (Bash with `jq` becomes unreadable quickly).
  3. I need to interact with multiple Cloud APIs or Databases.
  4. I need unit tests for the automation logic.

***

#### 🔹 3. Architecture & Design: Scripting in SRE

The "Sidecar" and "Init-Container" Pattern:

In Kubernetes, your scripts often live as "Init-containers."

* Design: A Bash script waits for a Database to be ready before the main app starts.
* Trade-off: If the script is too aggressive (no exponential backoff), it can DDoS your own database during a cluster-wide restart.

Scalability Concerns:

A script that works for 10 servers might fail for 1,000 due to:

* Rate Limiting: Cloud APIs will throttle your script if it makes too many requests.
* Memory Exhaustion: Loading a 5GB log file into a Python list will crash the pod. Use Generators or Iterators to process data line-by-line.

***

#### 🔹 4. Commands & Configs (The "Scripting Standard")

**The "Professional" Bash Header**

Every production script should start with this to ensure reliability:

Bash

```
#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# Log function for consistent formatting
log() {
    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: $*"
}

log "Starting backup..."
```

**Python: Robust API Interaction (Retries)**

In production, networks flake. Use the `tenacity` library or a custom retry decorator.

Python

```
import time
from botocore.exceptions import ClientError

def execute_with_retry(func, retries=3):
    for i in range(retries):
        try:
            return func()
        except ClientError as e:
            if i == retries - 1: raise
            time.sleep(2 ** i) # Exponential backoff
```

***

#### 🔹 5. Troubleshooting & Debugging

Common Failure Mode: "It works on my machine" (Environment Mismatch)

* The Fix: Always use `#!/usr/bin/env python3` instead of `#!/usr/bin/python`. Use Virtual Environments (`venv`) or Dockerize your script to bundle dependencies.

Debugging Bash:

* Run with `bash -x script.sh` to see every command as it executes with variables expanded.
* Use `shellcheck` (linter) to catch common bugs like missing quotes around variables (which causes issues with filenames containing spaces).

Debugging Python:

* Use `try...except...finally` blocks to ensure resources (like DB connections) are closed even if the script crashes.
* Utilize the `logging` module instead of `print()` to allow for different log levels (DEBUG vs INFO) in production.

***

#### 🔹 6. Production Best Practices

1. Fail Fast: Validate all input arguments and environment variables at the very beginning of the script.
2. Atomic Operations: If a script is renaming files, try to make it atomic. If it fails halfway, it shouldn't leave the system in a "half-migrated" state.
3. Signal Handling: In SRE, scripts should handle `SIGTERM`. If a Kubernetes pod is terminating, your script should catch the signal and finish its current task or exit cleanly.
4. No "Golden Images": Don't rely on a script being pre-installed on a server. Use Configuration Management (Ansible) to deploy the script and its environment.

***

#### 🔹 Cheat Sheet / Quick Revision

* Bash Logic: `[[ $a == $b ]]` (Modern comparison), `$?` (Last exit code), `2>&1` (Merge stderr into stdout).
* Python Essentials: `os.environ.get()` (Safe env access), `subprocess.run(check=True)` (Running shell commands safely), `json.loads()` (Parsing API responses).
* SRE Logic: Is it Idempotent? Does it have Retries? Does it Log properly? Does it handle Secrets safely?

***

This section transitions from "what DevOps is" to the actual tooling and automation that makes it work. For an SRE, scripting is about moving from manual tasks to repeatable, reliable systems.

***

#### 🟢 Easy: Scripting Basics

_Focus: Syntax and fundamental operations._

1. What is a "Shebang" (`#!`) and why is it important in a script?
   * _Context:_ Explain how the kernel uses it to identify the interpreter (e.g., `#!/bin/bash` vs `#!/usr/bin/env python3`).
2. How do you check the exit status of the last executed command in Bash?
   * _Context:_ Mention `$?` and what a `0` vs. non-zero value represents.
3. In Python, what is the difference between a List and a Dictionary?
   * _Context:_ Focus on when you would use each (e.g., a list for a sequence of server names; a dictionary for server metadata like IP and Role).
4. How do you pass arguments to a script in Bash?
   * _Context:_ Mention positional parameters like `$1`, `$2`, and `$@` for all arguments.

***

#### 🟡 Medium: Logic & System Interaction

_Focus: Error handling and data manipulation._

1. Explain the difference between `soft` and `hard` errors in a script.
   * _Context:_ How do you ensure a script stops immediately if a critical command fails? (Mention `set -e` in Bash or `try...except` in Python).
2. How would you search for a specific string in a file and replace it using only Bash?
   * _Context:_ The interviewer is looking for `sed` or `awk`. Bonus if you explain "in-place" editing (`sed -i`).
3. Why would you use the `subprocess` module in Python instead of `os.system()`?
   * _Context:_ Discuss security (shell injection), capturing output (`stdout/stderr`), and better control over execution.
4. What are "Environment Variables," and how do you access them in both Bash and Python?
   * _Context:_ Bash: `$VAR_NAME`; Python: `os.environ.get('VAR_NAME')`. Why is it better to use environment variables than hardcoding secrets?

***

#### 🔴 Hard: Production Engineering & Robustness

_Focus: Automation at scale and "Defensive Scripting."_

1. How do you implement "Idempotency" in a script? Give a real-world example.
   * _Context:_ A script to create a directory or user should not fail if the directory/user already exists. It should check the state first.
2. Explain the concept of "Exponential Backoff." How would you script this to handle a flaky API?
   * _Context:_ Instead of retrying every 1 second, you wait 1s, 2s, 4s, 8s... to avoid overwhelming a service that is already struggling.
3. Why is `set -o pipefail` critical for CI/CD pipelines?
   * _Context:_ In a pipeline like `command1 | command2`, without `pipefail`, the exit code is determined only by the _last_ command. If `command1` fails, the pipeline might still report success.
4. Scenario: You need to rotate logs on 100 servers. Would you use a Bash loop with SSH or a Python script using an SDK? Explain your choice.
   * _Context:_ This tests your understanding of Parallelism vs. Serial execution. Mention that Python (or Go) handles concurrency and complex error reporting across many nodes much better than raw Bash.

***

***

#### 💡 Pro-Tip for your Interview

When discussing scripting, always mention Testing.

* _Example:_ "I don't just write scripts; I use ShellCheck for my Bash scripts to catch common bugs, and I write basic Unit Tests in Python to ensure my automation logic handles edge cases."

---

## 🔷 Engineering Automation at Scale (7 YOE)

If you are interviewing for a Senior or Staff position, writing simple "backup scripts" is insufficient. You will be evaluated on your ability to build production-grade internal tools and your understanding of cloud-native development in Go.

**Continue your preparation with this advanced module:**

1. `[NEW]` [Engineering Automation at Scale](./engineering-automation-at-scale.md): From scripts to packaged CLI tools (Go/Click), TDD for Infrastructure (Pytest/Moto), Concurrency (Goroutines/Asyncio), and the transition to Platform Engineering.
