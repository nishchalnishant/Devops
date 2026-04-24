## Medium

**20. You suspect a server is under memory pressure. What do you check?**

1. `free -h` to see total, used, and available memory including swap usage.
2. `/proc/meminfo` for detailed kernel memory counters.
3. `vmstat 1 5` to check swap in/out rates and page faults.
4. `dmesg | grep -i oom` to check for OOM killer events.
5. `ps aux --sort=-%mem | head -20` to identify the top memory consumers.

**21. How do you write an idempotent shell script?**

An idempotent script produces the same result whether run once or multiple times. Techniques:
- Check before acting: `if [ ! -d /opt/myapp ]; then mkdir /opt/myapp; fi`
- Use `set -euo pipefail` to catch errors early.
- For package installs: use the package manager's idempotency (`apt-get install -y` is idempotent).
- For file changes: write the desired final state, not incremental steps.

**22. What is `inotifywait` and how is it used?**

`inotifywait` is a tool that uses Linux inotify to watch for filesystem events. Example — restart a service when a config file changes:

```bash
inotifywait -m -e modify /etc/nginx/nginx.conf | while read; do
  systemctl reload nginx
done
```

**23. Explain Linux load average and when it becomes a problem.**

Load average represents the number of runnable or uninterruptible processes over 1, 5, and 15 minute windows. A load of 1.0 on a single-core system means the CPU is fully utilized. On a 4-core system, 4.0 means full utilization. Load > CPU count means queuing. Sustained load several times the CPU count = performance problem.

**24. How do you diagnose high I/O wait?**

1. `top` or `vmstat` — check `wa` (iowait%) column. >20% sustained is high.
2. `iostat -xz 1` — shows per-device utilization, await, and queue depth.
3. `iotop` — shows per-process I/O usage.
4. `dstat --disk --io` — combined disk and I/O view.

**25. What is `nice` and `renice`?**

`nice` sets the scheduling priority of a new process (range: -20 highest to 19 lowest). `renice` changes the priority of an already-running process. Lower values = higher CPU scheduling priority.

**26. How do you use `trap` in a shell script?**

`trap` registers a command to run when the script receives a signal or exits. Used for cleanup:

```bash
trap 'rm -f /tmp/lock; exit' INT TERM EXIT
```

**27. What is the difference between `set -e`, `set -u`, and `set -o pipefail`?**

- `set -e`: exit on any error (non-zero exit code).
- `set -u`: treat unset variables as errors.
- `set -o pipefail`: if any command in a pipeline fails, the pipeline exit code is non-zero (not just the last command).

**28. How do you securely pass secrets to a shell script?**

Never as command-line arguments (visible in `ps`). Options:
- Environment variables set by the calling process.
- Read from a file with restricted permissions (`chmod 400`).
- Read from a secret manager (Vault, AWS SSM) at runtime.
- Pass via stdin: `echo "$SECRET" | ./script.sh` and read with `read -r`.

---

