# Production Scenarios & Troubleshooting Drills (Senior Level)

## Level 1: System Internals & Process Management

### Scenario 1: The "Zombies" Are Coming
**Symptom:** Hundreds of processes in state `Z`.
**Diagnosis:** Identify the parent (`ps -o ppid= -p <zombie_pid>`). Zombies occur when a child finishes but the parent hasn't acknowledged it.
**Fix:** Kill the parent process. The zombies will be inherited by `init` (PID 1) and reaped.

### Scenario 2: The "Ghost" Disk Space
**Symptom:** `df -h` shows 100% full, but `du -sh` shows only 10% used.
**Diagnosis:** Deleted files are still open by a process.
**Fix:** Find them with `lsof +L1` or `lsof | grep deleted`. Restart the service holding the file handle.

### Scenario 3: CPU 10% but Load Average 20
**Symptom:** System is extremely slow, but CPU usage is low.
**Diagnosis:** Check `%wa` (I/O Wait). Processes are stuck in "Uninterruptible Sleep" (State `D`), waiting for Disk or Network I/O.
**Fix:** Use `iostat -xz 1` to find the bottlenecked disk.

## Level 2: SRE & Kernel Tuning

### Scenario 4: The Systemd "203/EXEC" Mystery
**Symptom:** Service fails with `status=203/EXEC`.
**Diagnosis:** Systemd found the file but couldn't execute it. 
**Checklist:** 
- Wrong Shebang (e.g., `#!/bin/bash` missing).
- No execute permissions (`chmod +x`).
- Windows Line Endings (CRLF) in script. Use `dos2unix`.

### Scenario 5: OOM (Out of Memory) Thrashing
**Symptom:** System is unresponsive; SSH times out.
**Diagnosis:** `dmesg | grep -i oom`. If Swap is 100% full, the system is thrashing.
**Fix:** Increase `vm.swappiness` or add RAM. In production, protect critical services using `oom_score_adj`.

### Scenario 6: TCP Stack Tuning for High Traffic
**Symptom:** Nginx dropping connections under load.
**Diagnosis:** `dmesg` shows "TCP: Possible SYN flooding on port 80. Sending cookies."
**Fix:** Increase `net.core.somaxconn` (max listen queue) and `net.ipv4.tcp_max_syn_backlog`.

### Scenario 7: eBPF Performance Profiling
**Symptom:** Database latency spike every 60 seconds.
**Diagnosis:** Use `biolatency` (from BCC tools) to see disk latency distribution.
**Discovery:** Found that a periodic cron job (backup) is causing disk saturation.
**Fix:** Use `ionice` to lower the I/O priority of the backup job.

### Scenario 8: Linux Hugepages and Database Performance
**Symptom:** A large PostgreSQL instance is slow despite having 256GB RAM.
**Diagnosis:** High CPU usage in `sys` mode due to Page Table management overhead.
**Fix:** Configure **Transparent Hugepages (THP)** or explicit Hugepages to reduce TLB misses.
