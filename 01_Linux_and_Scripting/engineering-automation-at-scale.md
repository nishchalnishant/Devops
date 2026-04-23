# Engineering Automation at Scale (7 YOE)

At the senior level, the distinction between a "DevOps Engineer" and a "Software Engineer" disappears. You aren't just writing "scripts"; you are writing **Production Systems** that manage other production systems.

---

## 1. From "Scripts" to "Tooling"

### The CLI Evolution
A senior engineer doesn't provide a folder of 20 `.sh` files to a developer. They provide a single, packaged, and tested CLI tool.
- **Python:** Use libraries like `Click` or `Typer` to build professional-grade CLI interfaces with automatic help menus, sub-commands, and type validation.
- **Go:** Use the `Cobra` library (the same library used by `kubectl`, `hugo`, and `docker`). Go is the preferred language for 7+ YOE engineers because it produces a single static binary that "just works" on any Linux server without dependency hell.

---

## 2. Test-Driven Development (TDD) for Infrastructure

If your automation logic manages a $1M production database, you cannot "test in prod."

### Unit Testing Infrastructure Code
- **Pytest + Mock:** Use `unittest.mock` to intercept network calls to cloud APIs.
- **Moto:** A dedicated library for mocking AWS services. "Build" a fake S3 bucket in memory, let your script "delete" it, and assert the script behaved correctly — without ever touching a real AWS account.

### The "Dry Run" Pattern
Every production-grade script must implement a `--dry-run` or `--check` flag.
- **Principle:** The script walks through all logic, calculates exactly what it *would* do, and prints the summary (e.g., "Would delete 42 orphaned snapshots"), then exits without making a single API modification.

---

## 3. High-Performance Concurrency & Parallelism

### The Problem with Bash Loops
```bash
# This is slow and error-prone for 1,000 servers
for server in $(cat list.txt); do 
   ssh $server "systemctl restart nginx"
done
```
If server #5 is down, the loop hangs. If server #100 fails, you won't know until the end.

### The Senior Solution: Goroutines & Asyncio
- **Go (Goroutines):** Launch 1,000 tasks simultaneously in "lightweight threads." Go handles the scheduling and ensures that if one server fails, the others continue.
- **Python (Asyncio):** Use non-blocking I/O to handle thousands of concurrent API requests (e.g., refreshing credentials for 500 databases) in a single-threaded event loop.

---

## 4. Software Engineering Standards for DevOps

### Linting & Formatting
A 7 YOE engineer enforces consistency.
- **Pre-commit Hooks:** Automatically run `black` (Python formatter), `flake8` (linter), and `shellcheck` (Bash linter) every time someone tries to `git commit`. If the code doesn't meet standards, the commit is rejected.
- **Semantic Versioning (SemVer):** Tagging your internal tools with `v1.2.0` so that developers know if an update contains a breaking change.

---

## 5. Defensive Programming & Safety Rails

### Handling "Throttling" (429 Too Many Requests)
Cloud APIs will ban your script if it makes requests too fast.
- **Exponential Backoff with Jitter:** Wait longer and longer between retries, and add a small amount of "randomness" (jitter) to prevent the "Thundering Herd" problem where 100 failed scripts all retry at exactly the same microsecond.

### Atomic Operations
- **Principle:** If a script must perform three steps (e.g., 1. Create User, 2. Add to Group, 3. Generate Key), and step 2 fails, the script should **roll back** (delete the user created in step 1) to prevent a "half-done" state.

---

## 6. The Shift to Internal Developer Platforms (IDPs)

The ultimate goal of a senior engineer is to **automate themselves out of a job**.
- Instead of "I will run this script for you," the answer is "I have built a self-service API that you can call to do this yourself."
- This is the transition from **DevOps (Operations focus)** to **Platform Engineering (Product focus)**.
- **Key Skill:** Building a REST API (using FastAPI or Go Gin) that wraps around your automation scripts.
