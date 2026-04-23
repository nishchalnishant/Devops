# Linux & Shell Scripting — Interview Questions

All difficulty levels combined.

---

## Easy

**1. What is the difference between a process and a thread?**

A process is an independent program with its own memory space. A thread is a lighter unit of execution within a process that shares the same memory space with other threads in that process.

**2. What does `chmod 755` do?**

It sets permissions so the owner has read, write, and execute (7), and group and others have read and execute (5).

**3. What is the difference between `>` and `>>` in shell?**

`>` redirects output to a file and overwrites it. `>>` appends output to the end of the file.

**4. How do you find all files larger than 100MB in Linux?**

```bash
find / -type f -size +100M
```

**5. What is a symbolic link vs a hard link?**

A hard link points directly to the same inode (data blocks). A symbolic link points to a path. Deleting the original file breaks a symlink but not a hard link.

**6. What does `ps aux` show?**

It lists all running processes for all users with CPU, memory, PID, command, and state information.

**7. How do you check disk usage per directory?**

```bash
du -sh /path/to/dir
```

**8. What is `ulimit` used for?**

`ulimit` sets per-process resource limits such as maximum open files, stack size, and maximum memory.

**9. What is the difference between `kill` and `kill -9`?**

`kill` sends SIGTERM (15) which allows the process to clean up. `kill -9` sends SIGKILL which the kernel terminates immediately with no cleanup.

**10. How do you check which port a process is listening on?**

```bash
ss -tlnp
# or
netstat -tlnp
```

**11. What is the sticky bit?**

A permission flag on directories that allows only the file owner to delete or rename their own files within the directory. Used on `/tmp`.

**12. What does `/etc/fstab` do?**

It defines filesystems and their mount options that are automatically mounted at boot.

**13. What is a cron job?**

A cron job is a scheduled task defined in a crontab that the cron daemon runs at specified intervals.

**14. How do you view running services in systemd?**

```bash
systemctl list-units --type=service --state=running
```

**15. What is the purpose of `/proc`?**

`/proc` is a virtual filesystem exposing kernel and process information as files. `/proc/cpuinfo`, `/proc/meminfo`, `/proc/PID/` are common examples.

**16. What does `awk` do?**

`awk` is a text processing tool that reads line by line, splits fields by delimiter, and applies expressions. Used for data extraction and transformation.

**17. What is `sed` used for?**

`sed` is a stream editor for filtering and transforming text — find/replace, deletion, insertion — without opening the file.

**18. What is `xargs`?**

`xargs` reads items from stdin and passes them as arguments to another command. Example: `find . -name "*.log" | xargs rm`.

**19. What is the difference between `source` and executing a script?**

`source script.sh` runs the script in the current shell, so variable assignments persist. Executing `./script.sh` runs it in a subshell — changes don't affect the parent.

---

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

## Hard

**29. How does the Linux kernel's OOM killer select which process to terminate?**

The OOM killer scores each process using `/proc/PID/oom_score`, which factors in: the process's RSS (resident set size), the proportion of physical memory it uses, whether it has CAP_SYS_ADMIN, and the `oom_score_adj` value (tunable per process, range -1000 to +1000). The process with the highest score is killed. You can protect critical processes with `oom_score_adj = -1000` (which sets score to 0, preventing OOM kill) or deprioritize them with positive adjustments.

**30. Explain Linux cgroups v2 and how they are used in containers.**

cgroups v2 is a unified hierarchy for resource control. Unlike v1 (which had separate hierarchies per controller), v2 uses a single tree where each node can have multiple controllers (cpu, memory, io, pids). Containers (Docker, Kubernetes) use cgroups to:
- Enforce memory limits (`memory.max`) and kill containers that exceed them.
- Enforce CPU bandwidth (`cpu.max`, format: `quota period`).
- Limit I/O bandwidth (`io.max`).
- Limit process count (`pids.max`).

Kubernetes uses cgroups v2 when `--cgroup-driver=systemd` is set on the kubelet, which delegates cgroup management to systemd.

**31. How do you debug a performance regression using perf and flame graphs?**

1. Run `perf record -g -p <PID> -- sleep 30` to record call stacks for 30 seconds.
2. Run `perf script` to convert to a text format.
3. Use Brendan Gregg's `flamegraph.pl` to generate a flame graph SVG.
4. The flame graph visualizes where CPU time is spent: wide stacks = hot code paths. Identify the widest plateau at the top of the graph — that function is the hottest path consuming CPU.

**32. What is eBPF and how is it used for performance observability?**

eBPF (extended Berkeley Packet Filter) allows running sandboxed programs in the Linux kernel without modifying kernel source. For performance observability: tools like `bpftrace`, `BCC`, and `Cilium` use eBPF to attach probes to kernel and user-space functions at runtime. You can measure exact latency of system calls, trace TCP connections, profile function call frequency — all with near-zero overhead compared to traditional instrumentation. Example: `bpftrace -e 'tracepoint:syscalls:sys_enter_read { @[comm] = count(); }'` counts read syscalls per process name.

**33. How do you implement a high-performance log pipeline from multiple servers?**

Architecture:
1. **Collection:** Use a lightweight agent (`Fluent Bit`, `Vector`, `Promtail`) on each server — reads from journald/file, parses structured fields, compresses, and forwards.
2. **Transport:** Kafka as a buffer between collectors and processors — decouples producer (servers) from consumer (processing pipeline). Handles burst traffic.
3. **Processing:** Logstash, Flink, or Vector processes the Kafka stream — parses, enriches (GeoIP, service name lookup), and routes.
4. **Storage:** OpenSearch/Elasticsearch for search workloads; Loki for high-cardinality log storage with label indexing only.
5. **Backpressure:** If downstream is slow, Kafka buffers — agents are not blocked. Dead letter queues for unparseable messages.
