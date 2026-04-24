## Medium

**1. You suspect a server is under memory pressure. What do you check?**
1. `free -h` to see total, used, and available memory including swap usage.
2. `/proc/meminfo` for detailed kernel memory counters.
3. `vmstat 1 5` to check swap in/out rates and page faults.
4. `dmesg | grep -i oom` to check for OOM killer events.
5. `ps aux --sort=-%mem | head -20` to identify the top memory consumers.

**2. How do you write an idempotent shell script?**
An idempotent script produces the same result whether run once or multiple times. Techniques:
- Check before acting: `if [ ! -d /opt/myapp ]; then mkdir /opt/myapp; fi`
- Use `set -euo pipefail` to catch errors early.
- For package installs: use the package manager's idempotency (`apt-get install -y` is idempotent).
- For file changes: write the desired final state, not incremental steps.

**3. What is `inotifywait` and how is it used?**
`inotifywait` is a tool that uses Linux inotify to watch for filesystem events. Example — restart a service when a config file changes:

```bash
inotifywait -m -e modify /etc/nginx/nginx.conf | while read; do
  systemctl reload nginx
done
```

**4. Explain Linux load average and when it becomes a problem.**
Load average represents the number of runnable or uninterruptible processes over 1, 5, and 15 minute windows. A load of 1.0 on a single-core system means the CPU is fully utilized. On a 4-core system, 4.0 means full utilization. Load > CPU count means queuing. Sustained load several times the CPU count = performance problem.

**5. How do you diagnose high I/O wait?**
1. `top` or `vmstat` — check `wa` (iowait%) column. >20% sustained is high.
2. `iostat -xz 1` — shows per-device utilization, await, and queue depth.
3. `iotop` — shows per-process I/O usage.
4. `dstat --disk --io` — combined disk and I/O view.

**6. What is `nice` and `renice`?**
`nice` sets the scheduling priority of a new process (range: -20 highest to 19 lowest). `renice` changes the priority of an already-running process. Lower values = higher CPU scheduling priority.

**7. How do you use `trap` in a shell script?**
`trap` registers a command to run when the script receives a signal or exits. Used for cleanup:

```bash
trap 'rm -f /tmp/lock; exit' INT TERM EXIT
```

**8. What is the difference between `set -e`, `set -u`, and `set -o pipefail`?**
- `set -e`: exit on any error (non-zero exit code).
- `set -u`: treat unset variables as errors.
- `set -o pipefail`: if any command in a pipeline fails, the pipeline exit code is non-zero (not just the last command).

**9. How do you securely pass secrets to a shell script?**
Never as command-line arguments (visible in `ps`). Options:
- Environment variables set by the calling process.
- Read from a file with restricted permissions (`chmod 400`).
- Read from a secret manager (Vault, AWS SSM) at runtime.
- Pass via stdin: `echo "$SECRET" | ./script.sh` and read with `read -r`.

**10. What is the difference between a "Hard Link" and a "Soft Link" (Symbolic Link)?**
- **Hard Link:** A new directory entry that points to the same Inode. If the original file is deleted, the hard link still works. Limits: Cannot cross filesystems; cannot link directories.
- **Soft Link:** A separate file that contains the path to the original file. If the original is deleted, the soft link breaks. Can cross filesystems and link directories.

**11. How do you find and replace a string in multiple files at once?**
`grep -rl "old_string" . | xargs sed -i 's/old_string/new_string/g'`

**12. Explain the "Shebang" line in a script.**
The `#!` at the beginning of a script tells the kernel which interpreter to use to execute the file (e.g., `#!/bin/bash`, `#!/usr/bin/python3`).

**13. What is the difference between `su` and `sudo`?**
- `su`: Switches to the root user (requires root's password).
- `sudo`: Executes a command as root (requires the *user's* password). It provides better auditing via `/var/log/auth.log`.

**14. How do you schedule a task to run every day at 3 AM?**
Add a line to `crontab -e`: `0 3 * * * /path/to/script.sh`

**15. What is "Standard Error" (stderr) and how do you redirect it?**
stderr is the stream for error messages (File Descriptor 2). Redirect with `2> error.log`. To redirect both stdout and stderr to the same file: `&> output.log`.

**16. How do you check which processes are consuming the most memory?**
`top` (then press `M`) or `ps aux --sort=-%mem | head`.

**17. What is the difference between `tar` and `zip`?**
- `tar`: Just archives (groups files together). Doesn't compress by itself (needs `-z` for gzip). Preserves Linux permissions.
- `zip`: Archives and compresses in one step. Native to Windows; doesn't always preserve Linux permissions perfectly.

**18. How do you view a file that is too large to open in an editor?**
`less <filename>` (allows paging and searching) or `tail -n 100 <filename>` (view last few lines).

**19. What is "Uptime" and what do the three numbers in Load Average mean?**
Load Average shows the number of processes in the "Runnable" or "Uninterruptible" state over the last 1, 5, and 15 minutes.

**20. How do you search for a file by name?**
`find / -name "filename.txt"` or `locate filename.txt` (faster as it uses a database).

**21. What is a "Pipe" (`|`)?**
It redirects the output of one command to the input of another. Example: `ls | grep "txt"`.

**22. How do you change the owner of a file?**
`chown user:group filename`

**23. What does `chmod 755` mean?**
- 7 (rwx) for User
- 5 (r-x) for Group
- 5 (r-x) for Others

**24. How do you check your current IP address?**
`ip addr` or `ifconfig`.
