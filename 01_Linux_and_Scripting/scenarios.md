# Production Scenarios & Troubleshooting Drills (Senior Level)

```
Production Scenarios
├── Level 1: System Internals & Process Management
│   ├── Zombie processes: parent not calling wait(), fix by killing parent
│   ├── Ghost disk space: df vs du discrepancy, file held open post-delete
│   └── CPU 10% but Load 20: D-state processes, I/O wait, iostat -xz
├── Level 2: SRE & Kernel Tuning
│   ├── systemd 203/EXEC: wrong shebang, no +x, CRLF line endings
│   ├── OOM thrashing: dmesg | grep oom, oom_score_adj for protection
│   ├── TCP SYN flood: somaxconn, tcp_max_syn_backlog tuning
│   ├── eBPF profiling: biolatency, periodic cron causing disk saturation
│   └── HugePages for PostgreSQL: TLB miss reduction, sys CPU spike
├── Level 3: Platform Engineering & Deep Troubleshooting
│   ├── CPU steal time (%st): hypervisor taking cycles, migrate instance
│   ├── "Too many open files" vs file-max: ulimit vs kernel-wide limit
│   ├── D-state deadlock: NFS hang, umount -f, cannot kill with -9
│   ├── NIC ring buffer drops: ethtool -G, softirq saturation /proc/softirqs
│   ├── Dirty page writeback freeze: vm.dirty_ratio, lower background ratio
│   ├── Rootkit detection: busybox ps, /proc/ direct check, chkrootkit/rkhunter
│   ├── Clock skew: JWT/Kerberos auth failures, chronyd/ntpd sync
│   ├── Inode exhaustion: df -h ok, df -i full, millions of tiny files
│   ├── Shared memory segment leak: /dev/shm, ipcs -m, ipcrm -m
│   ├── eBPF overhead: detach from high-frequency events, use sampling
│   ├── SSH hang at motd: /etc/profile.d/ script calling unreachable host
│   ├── Kernel panic: /var/log/kdump, stack trace, RIP, driver update
│   ├── AppArmor/SELinux deny: dmesg | grep deny, audit2allow
│   ├── Heavy SAN/NFS user: iotop -Pa, ionice -c 3
│   ├── Journal space: journalctl --vacuum-time / SystemMaxUse
│   ├── Memory fragmentation: /proc/buddyinfo, compact_memory
│   ├── Executable /tmp: mount -o remount,noexec, /etc/fstab
│   ├── Soft lockup (NMI watchdog): CPU stuck in kernel loop, driver issue
│   └── systemd-oomd wrong target: kills cgroup, not largest process
├── Level 4: Advanced Networking & Storage
│   ├── Silent packet drops: socket buffer, NIC ring buffer, softirq
│   │   ├── ss -s: RcvbufErrors
│   │   ├── ethtool -S: miss/drop/overflow
│   │   └── Fix: rmem_max, netdev_max_backlog, RSS queues
│   ├── D-state disk stalls: ext4 journal contention, SSD scheduler (none)
│   │   ├── iostat -x: %await > 50ms, %util 100%
│   │   └── Fix: echo none > scheduler, increase nr_requests, XFS for parallel writes
│   ├── Midnight CPU spike: hidden cron sources, systemd timers
│   │   ├── /etc/cron.d, /etc/crontab, systemctl list-timers
│   │   └── Fix: stagger with RandomizedDelaySec, anacron offsets
│   └── Bash daemon memory leak: fd leak, zombie accumulation, tmp files
│       ├── Diagnose: /proc/PID/fd count, ps aux awk $8==Z
│       └── Fix: trap cleanup EXIT, wait -n for background jobs
├── Level 5: Security & Hardening
│   ├── SSH brute force: fail2ban, PasswordAuthentication no, iptables rate-limit
│   │   ├── grep "Failed password" /var/log/auth.log
│   │   └── Check: new authorized_keys, SUID binaries, cron persistence
│   └── /var full cascade: du -sh /var/*, lsof +L1 for ghost space
│       ├── Fix: truncate rotated logs, restart holding process, apt clean
│       └── Prevent: separate /var partition, logrotate, journald SystemMaxUse
└── Level 6: Performance Tuning
    ├── 10Gbps NIC underperforming: TCP buffer, window scaling, BBR, RSS
    │   ├── Diagnose: sysctl rmem/wmem, ethtool -k (offloads), /proc/interrupts
    │   └── Fix: rmem_max=128M, tcp_congestion_control=bbr, ethtool -L combined
    └── inotify watch limit: IDE/webpack registering too many watches
        ├── Diagnose: /proc/sys/fs/inotify/max_user_watches, per-pid count
        └── Fix: sysctl max_user_watches=524288, exclude node_modules/.git
```

## First Principles

- **Every incident has a bottleneck resource.** CPU, memory, disk I/O, network I/O, or file descriptors — only one is the primary constraint. The USE Method (Utilization, Saturation, Errors) applied to each resource reveals which one.
- **"The disk is full" has three distinct causes:** actual space exhaustion, inode exhaustion, and deleted-but-open files. They look the same from the application's perspective but require completely different fixes.
- **D-state processes cannot be killed because the kernel itself is blocking them.** `kill -9` is a user-space signal; a process in uninterruptible sleep is deep inside a kernel code path that hasn't reached a signal-check point.
- **Security incidents follow a pattern:** initial access → persistence → privilege escalation. Checking for new SUID binaries, cron entries, and authorized_keys covers persistence. The attacker's goal is to survive reboots.
- **Brute force protection is layered:** fail2ban (rate-limiting), key-only auth (no password to guess), `AllowUsers` (no lateral movement), and iptables rate-limiting (hardware-level drop). No single layer is sufficient.
- **Performance problems at midnight are predictable.** Every system has scheduled maintenance tasks. The design error is not staggering them — they all align at 00:00 because that is the default cron "daily" time.

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

## Level 3: Platform Engineering & Deep Troubleshooting

### Scenario 9: The "Hidden" CPU Steal
**Symptom:** Application latency is spiking, but `%user` and `%sys` are low.
**Diagnosis:** Check `%st` (Steal Time) in `top` or `vmstat`.
**Reason:** In a virtualized environment (AWS/GCP), the hypervisor is taking CPU cycles for other VMs on the same physical host.
**Fix:** Migrate to a non-burstable instance type or a different physical host.

### Scenario 10: "Too Many Open Files" - The Kernel Limit
**Symptom:** `ulimit -n` is set to 65535, but the app still fails with "Too many open files".
**Diagnosis:** Check the system-wide limit in `/proc/sys/fs/file-max`.
**Fix:** Increase the kernel limit using `sysctl -w fs.file-max=2097152`.

### Scenario 11: The "D" State Deadlock
**Symptom:** A process cannot be killed even with `kill -9`.
**Diagnosis:** Process is in `D` state (Uninterruptible Sleep), waiting on NFS or a failing Disk.
**Fix:** You cannot kill a `D` state process. You must fix the underlying I/O (e.g., `umount -f` the NFS share) or reboot.

### Scenario 12: Network Packet Drops at the Ring Buffer
**Symptom:** High network throughput, but high packet loss. `netstat -i` shows drops.
**Diagnosis:** The NIC's ring buffer is full. The CPU isn't pulling packets fast enough.
**Fix:** Increase ring buffer size with `ethtool -G eth0 rx 4096`. Check for "SoftIRQ" saturation in `/proc/softirqs`.

### Scenario 13: Dirty Page Writeback Latency
**Symptom:** Database writes are fast for 10 seconds, then freeze for 2 seconds.
**Diagnosis:** `vm.dirty_ratio` is reached, and the kernel is forcing synchronous writeback to disk.
**Fix:** Lower `vm.dirty_background_ratio` to start background writeback sooner and prevent a massive "blocking" write event.

### Scenario 14: Identifying a Rootkit
**Symptom:** `ps` shows normal processes, but `netstat` shows connections to a strange IP.
**Diagnosis:** The `ps` binary might be compromised. Use `busybox ps` or check `/proc/` directly.
**Tool:** Run `chkrootkit` or `rkhunter`. Compare file hashes with `debsums` or `rpm -V`.

### Scenario 15: Clock Skew in Distributed Systems
**Symptom:** Auth tokens (JWT/Kerberos) are failing across servers.
**Diagnosis:** Check time drift with `timedatectl`.
**Fix:** Ensure `chronyd` or `ntpd` is running and synced. In AWS, use the Amazon Time Sync Service (`169.254.169.123`).

### Scenario 16: Inode Exhaustion
**Symptom:** `df -h` shows 50% free, but `touch file` fails with "No space left on device".
**Diagnosis:** Check `df -i`. You've run out of Inodes (likely millions of tiny session/cache files).
**Fix:** Find the directory with the most files using `find / -xdev -type d -exec sh -c "echo -n '{}: '; ls -1 '{}' | wc -l" \; | sort -n` and delete them.

### Scenario 17: Shared Memory Segment Leak
**Symptom:** Application fails to start with "Cannot allocate memory", but `free -h` shows plenty of RAM.
**Diagnosis:** Check `/dev/shm` or `ipcs -m`. A crashed process didn't clean up its Shared Memory segments.
**Fix:** Remove segments with `ipcrm -m <shmid>`.

### Scenario 18: Pathological Systemtap/eBPF overhead
**Symptom:** Enabling a monitoring tool causes a 30% performance drop.
**Diagnosis:** The eBPF program is attached to a "high-frequency" event (like every packet or every `malloc`).
**Fix:** Move to "Sampling" or attach to less frequent tracepoints.

### Scenario 19: The "No Terminal" SSH Hang
**Symptom:** SSH into a server hangs after password entry.
**Diagnosis:** `/etc/motd` or a script in `/etc/profile.d/` is trying to reach a network resource that is down.
**Fix:** SSH with `ssh -t user@host /bin/bash --noprofile` to bypass the hung script.

### Scenario 20: Kernel Panic Analysis
**Symptom:** Server rebooted unexpectedly.
**Diagnosis:** Check `/var/log/messages` or `/var/log/kdump/`. Look for a "Stack Trace" or "RIP" (Instruction Pointer).
**Fix:** Analyze the trace. If it's in a third-party driver (e.g., `nvidia`), update the driver.

### Scenario 21: AppArmor/SELinux Blocking
**Symptom:** Process has root permissions but cannot read a file in `/data`.
**Diagnosis:** Check `dmesg | grep -i deny`.
**Fix:** Create a custom SELinux policy using `audit2allow` or update the AppArmor profile.

### Scenario 22: Identifying the "Heavy" User of a Shared Disk
**Symptom:** Shared SAN/NFS is slow for everyone.
**Diagnosis:** Use `iotop -Pa` to see total disk I/O per process over time.
**Fix:** Identify the process and apply `ionice -c 3` (Idle priority).

### Scenario 23: Taming the Systemd Journal
**Symptom:** `/var/log` is taking up 40GB.
**Diagnosis:** `journalctl --disk-usage`.
**Fix:** `journalctl --vacuum-time=7d` or set `SystemMaxUse=500M` in `/etc/systemd/journald.conf`.

### Scenario 24: Memory Fragmentation
**Symptom:** Large memory allocation fails, but `free` shows enough total RAM.
**Diagnosis:** Check `/proc/buddyinfo`. If all numbers are in the low-order columns (4K/8K), there are no large contiguous blocks.
**Fix:** Trigger compaction with `echo 1 > /proc/sys/vm/compact_memory`.

### Scenario 25: The "Executable" /tmp Risk
**Symptom:** Security audit flags that `/tmp` allows execution.
**Fix:** Remount with `noexec` flag: `mount -o remount,noexec /tmp`. Ensure this is in `/etc/fstab`.


### Scenario 26: The "Soft Lockup" Kernel Hang
**Symptom:** Console shows `NMI watchdog: BUG: soft lockup - CPU#2 stuck for 22s!`.
**Diagnosis:** A kernel-space process or driver is hogging the CPU in a loop without yielding.
**Fix:** Identify the driver (often NVIDIA or a network driver). Update kernel/driver. If it's a specific app, check for spinlocks.

### Scenario 27: Massive /proc/sys/fs/file-nr usage
**Symptom:** System is slow, but `lsof` doesn't show many files.
**Diagnosis:** Many files are being opened and closed so fast that `lsof` can't catch them, but the kernel file-handle table is full.
**Fix:** Use `sysdig` or `ebpf` to capture the "Open/Close" rate per process.

### Scenario 28: Systemd-OOMD killing the wrong process
**Symptom:** Critical service killed, but it wasn't the one leaking memory.
**Diagnosis:** `systemd-oomd` (on modern distros) kills the entire cgroup with the highest memory pressure, not necessarily the largest process.
**Fix:** Configure `OOMScoreAdjust` in the service file or exclude the cgroup from `systemd-oomd`.

***

## Level 4: Advanced Networking & Storage

### Scenario 13: Application Silently Dropping Packets Under Load

**Prompt:** A high-throughput service processes 100k requests/sec. Under load tests, roughly 0.5% of packets are silently dropped with no application errors logged. The OS and NIC look healthy.

**Diagnosis path:**
```bash
# Check socket receive buffer overflows
ss -s
# Look for: RcvbufErrors increasing

# Check kernel network drop counters
netstat -s | grep -E "packet receive errors|receive buffer errors|dropped"

# Check NIC ring buffer drops
ethtool -S eth0 | grep -i "miss\|drop\|overflow"

# Check softirq processing backlog
cat /proc/net/softnet_stat
# Column 2 = total dropped (backlog full), Column 3 = time squeeze (budget exhausted)
```

**Root causes and fixes:**

1. **Socket receive buffer too small:** The kernel drops incoming packets when the socket's receive buffer fills faster than the application reads:
```bash
# Increase default and max socket receive buffers
sysctl -w net.core.rmem_default=134217728
sysctl -w net.core.rmem_max=134217728
sysctl -w net.core.netdev_max_backlog=250000
```

2. **NIC ring buffer undersized:**
```bash
ethtool -G eth0 rx 4096   # increase ring buffer size
```

3. **Softirq CPU starvation — insufficient RSS queues:**
```bash
# Check if NIC has multiple queues
ethtool -l eth0
# Set queues to match CPU count
ethtool -L eth0 combined $(nproc)
# Enable receive side scaling
echo "32768" > /proc/irq/<irq-num>/smp_affinity
```

**Prevention:** Set `net.core.rmem_default`, `rmem_max`, and `netdev_max_backlog` in `/etc/sysctl.d/` before the service goes to production. Run `netstat -s` as a standard metric in your monitoring stack.

***

### Scenario 14: Disk I/O Causes Process Stalls — "D State" Processes

**Prompt:** The system load average spikes to 80 on a 32-core machine, but `top` shows CPU only at 15%. Dozens of processes are in `D` (uninterruptible sleep) state. The machine is not swapping.

**Diagnosis:**
```bash
# Confirm I/O wait
iostat -x 1 5
# Look for: %await > 50ms, %util approaching 100%

# Find which device is saturated
iostat -xd 1 | grep -v "^$\|Device"

# Find which processes are waiting on I/O
ps aux | awk '$8 ~ /D/ {print $0}'

# Trace which files D-state processes are accessing
for pid in $(ps -eo pid,stat | awk '$2~/D/{print $1}'); do
  ls -la /proc/$pid/fd 2>/dev/null | tail -3
done

# Check block device queue depth
cat /sys/block/sda/queue/nr_requests
cat /sys/block/sda/queue/scheduler
```

**Root causes:**

1. **ext4 journal commit contention:** When many processes fsync simultaneously, they all wait on the journal commit. Switch to `noatime` mount, or use `data=writeback` for non-critical data.
2. **Single-queue HDD behind RAID:** The I/O scheduler (`mq-deadline`, `bfq`) is serializing requests. For SSDs/NVMe, use the `none` (noop) scheduler:
```bash
echo none > /sys/block/nvme0n1/queue/scheduler
```
3. **NFS server overloaded:** If files are on NFS, D-state processes are waiting on the NFS server. Check `nfsstat -c` and server-side queue depth.

**Fix:** For SSDs, set scheduler to `none`. Increase `nr_requests`. For NFS, increase `nfsd` thread count on the server. For ext4 journal contention, use `nobarrier` (only on batteries-backed storage) or switch to XFS which handles parallel journal commits better.

***

### Scenario 15: Cron Job Causing Midnight CPU Spike

**Prompt:** Every night at midnight the monitoring system shows a 5-minute CPU spike that degrades user-facing API latency. The ops team suspects a cron job but `crontab -l` shows nothing unusual.

**Diagnosis:**
```bash
# Check all cron sources — not just user crontabs
crontab -l                          # current user
sudo crontab -l                     # root
cat /etc/cron.d/*                   # system cron.d directory
cat /etc/crontab                    # /etc/crontab
ls /etc/cron.daily/ /etc/cron.weekly/ /etc/cron.monthly/

# Check systemd timers (modern replacement for cron)
systemctl list-timers --all

# Find what ran at midnight in syslog
grep "CRON" /var/log/syslog | grep "00:00"
# Or in journald
journalctl _COMM=cron --since "today 00:00" --until "today 00:05"

# Check what processes ran at midnight via accounting
lastcomm --user root | grep "00:"   # requires acct package
```

**Common culprits at midnight:**

1. `logrotate` with `postrotate` scripts that restart services
2. `updatedb` (mlocate database rebuild) — scans entire filesystem
3. `aide` or `tripwire` integrity check — CPU and I/O intensive
4. `apt daily` or `yum makecache` scheduled via `systemd-timer` (not cron)

**Fix:** Stagger all heavy cron jobs using `anacron` offsets or `sleep $((RANDOM % 3600))` prefixes. Move logrotate to 2am, updatedb to 3am. For systemd timers, set `RandomizedDelaySec=3600` to spread the execution window:

```ini
[Timer]
OnCalendar=daily
RandomizedDelaySec=3600
```

***

### Scenario 16: Memory Leak in a Long-Running Shell Script

**Prompt:** A bash script runs as a daemon processing files from a queue directory. After running for 48 hours, the system's free memory drops to near zero and the OOM killer starts firing.

**Diagnosis:**
```bash
# Track the script's RSS over time
while true; do
  ps -o pid,rss,vsz,cmd -p <pid> >> /tmp/mem_trace.log
  sleep 60
done

# Check if subprocesses are leaking (zombie accumulation)
ps aux | awk '$8=="Z"'

# Check open file descriptors — descriptor leak
ls /proc/<pid>/fd | wc -l
# If this grows unboundedly, fd leak confirmed

# Check if temp files accumulate
ls -lt /tmp/ | head -20
lsof +D /tmp | grep <script-name>
```

**Common bash memory/resource leaks:**

1. **Unclosed file descriptors in loops:** `while read line < file` — if the loop contains early `continue` calls, the FD from `< file` may not be closed. Use `{ while read...; done } < file` instead.
2. **Accumulating background jobs:** `&` inside a loop without `wait` or `disown` creates zombie children that accumulate.
3. **Temp files not cleaned up on signal:** Add `trap 'rm -f $TMPFILE; exit' INT TERM EXIT` at the top of every script that creates temp files.
4. **Subshell cache from `$()` with large output:** `output=$(cmd_with_huge_output)` — the entire output is stored in a bash variable in memory.

**Fix template:**
```bash
#!/bin/bash
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"; kill $(jobs -p) 2>/dev/null; exit' INT TERM EXIT

# Process queue with controlled parallelism
MAX_JOBS=4
while true; do
  for item in "$QUEUE_DIR"/*; do
    [[ -f "$item" ]] || continue
    process_item "$item" &
    # Reap when at max
    while [[ $(jobs -r | wc -l) -ge $MAX_JOBS ]]; do
      wait -n 2>/dev/null || wait
    done
  done
  sleep 5
done
```

***

## Level 5: Security & Hardening Scenarios

### Scenario 17: Detecting and Responding to an SSH Brute Force

**Prompt:** Your security team alerts you that a server is receiving 10,000 SSH login attempts per hour from rotating IPs. No successful logins yet, but you need to harden immediately without breaking legitimate access.

**Immediate mitigation:**
```bash
# Check current attack rate
grep "Failed password" /var/log/auth.log | awk '{print $NF}' | sort | uniq -c | sort -rn | head -20

# Install and configure fail2ban (if not present)
apt-get install -y fail2ban

cat > /etc/fail2ban/jail.local << 'FAIL2BAN'
[sshd]
enabled  = true
port     = ssh
filter   = sshd
logpath  = /var/log/auth.log
maxretry = 3
bantime  = 3600
findtime = 600
FAIL2BAN

systemctl enable --now fail2ban
fail2ban-client status sshd
```

**Structural hardening:**
```bash
# Disable password auth entirely — key-only
sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/^#\?MaxAuthTries.*/MaxAuthTries 3/' /etc/ssh/sshd_config
echo "AllowUsers deploy admin" >> /etc/ssh/sshd_config
systemctl reload sshd

# Move SSH to non-standard port (security by obscurity — add, not replace real fixes)
# sed -i 's/^#\?Port 22/Port 2222/' /etc/ssh/sshd_config

# Rate-limit SSH at iptables level
iptables -A INPUT -p tcp --dport 22 -m state --state NEW -m recent --set
iptables -A INPUT -p tcp --dport 22 -m state --state NEW -m recent --update --seconds 60 --hitcount 4 -j DROP
```

**Detection for successful compromise:**
```bash
# Check for new authorized_keys additions in last 24h
find /home /root -name "authorized_keys" -newer /tmp/.marker -ls

# Check for new user accounts
grep "useradd\|adduser" /var/log/auth.log | tail -20

# Check for cron persistence
diff <(sort /etc/cron.d/*) <(sort /var/backup/cron.d.bak)

# Check for SUID binaries added recently
find / -perm -4000 -newer /tmp/.marker -ls 2>/dev/null
```

***

### Scenario 18: `/var` Partition Full — Service Degradation Cascade

**Prompt:** Multiple services start failing simultaneously. Logs show "no space left on device." `df -h` confirms `/var` is at 100%. The system is in production and cannot be rebooted.

**Immediate triage — identify what's filling `/var`:**
```bash
# Top consumers
du -sh /var/* | sort -rh | head -10
du -sh /var/log/* | sort -rh | head -10

# Find large files
find /var -size +100M -ls 2>/dev/null | sort -k7 -rn

# Check for deleted files still held open (not reflected in du)
lsof +L1 | grep /var | awk '{print $1, $2, $7}' | sort -k3 -rn | head -20
```

**Quick recovery actions (in order of safety):**

1. **Truncate rotated logs still held open:**
```bash
# Truncate (not delete) the file so the inode remains valid for open FDs
> /var/log/application/old.log.1
```

2. **Free deleted-but-open file space by restarting the holding process:**
```bash
lsof +L1 | grep /var/log
# Identify PID holding the deleted file
kill -HUP <pid>   # SIGHUP causes most services to reopen log files
```

3. **Clear package manager cache:**
```bash
apt-get clean      # clears /var/cache/apt/archives
yum clean all      # clears /var/cache/yum
```

4. **Truncate journald if it's grown too large:**
```bash
journalctl --disk-usage
journalctl --vacuum-size=500M
```

**Prevention:**
- `logrotate` with `compress`, `delaycompress`, `size 100M` for all application logs
- `journald` `SystemMaxUse=2G` in `/etc/systemd/journald.conf`
- Alert at 80% disk usage — never at 95% (recovery is already hard)
- Separate `/var/log` onto its own partition so a runaway log cannot fill root

***

## Level 6: Performance Tuning Scenarios

### Scenario 19: Kernel Network Stack Tuning for 10Gbps Throughput

**Prompt:** A new 10Gbps NIC is installed. `iperf3` achieves only 3Gbps. The NIC driver reports no errors. How do you tune the kernel to saturate the link?

**Diagnosis:**
```bash
# Check current TCP buffer sizes
sysctl net.core.rmem_default net.core.wmem_default net.core.rmem_max net.core.wmem_max

# Check if TCP window scaling is enabled
sysctl net.ipv4.tcp_window_scaling   # should be 1

# Check NIC offload settings
ethtool -k eth0 | grep -E "scatter|checksum|segmentation"

# Verify NIC ring buffer sizes
ethtool -g eth0

# Check IRQ affinity — is all traffic landing on one CPU?
cat /proc/interrupts | grep eth0
```

**Full tuning playbook for 10Gbps:**
```bash
cat >> /etc/sysctl.d/10-network-performance.conf << 'SYSCTL'
# TCP buffer sizes (min/default/max in bytes)
net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
net.core.rmem_default = 33554432
net.core.wmem_default = 33554432
net.ipv4.tcp_rmem = 4096 33554432 134217728
net.ipv4.tcp_wmem = 4096 33554432 134217728

# Increase socket backlog
net.core.netdev_max_backlog = 300000
net.core.somaxconn = 65535

# TCP performance
net.ipv4.tcp_window_scaling = 1
net.ipv4.tcp_timestamps = 1
net.ipv4.tcp_sack = 1
net.ipv4.tcp_congestion_control = bbr   # BBR outperforms CUBIC on high-BDP paths

# Reduce TIME_WAIT accumulation
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_fin_timeout = 15
SYSCTL

sysctl --system

# Enable NIC hardware offloads
ethtool -K eth0 tso on gso on gro on
ethtool -G eth0 rx 4096 tx 4096

# Spread IRQs across all CPUs (enable RSS)
ethtool -L eth0 combined $(nproc)
```

**Result:** With properly tuned buffers, window scaling, BBR, and RSS, 10Gbps should be achievable on a single stream. Multi-stream via `iperf3 -P 4` typically reveals the headroom.

***

### Scenario 20: Runaway `inotify` — "Too Many Open Files" Across the System

**Prompt:** Multiple unrelated processes start failing with "Too many open files" even though `ulimit -n` shows 1048576. `lsof` counts look normal. The kernel logs show `inotify_add_watch: inotify watch limit reached`.

**Diagnosis:**
```bash
# Check current inotify limits
cat /proc/sys/fs/inotify/max_user_watches    # default: 8192
cat /proc/sys/fs/inotify/max_user_instances  # default: 128
cat /proc/sys/fs/inotify/max_queued_events   # default: 16384

# Find who holds the most inotify watches
find /proc/*/fd -type l 2>/dev/null | xargs -I{} readlink {} 2>/dev/null | grep inotify | wc -l

# Per-process inotify watch count
for pid in /proc/[0-9]*/; do
  watches=$(find "$pid/fd" -type l 2>/dev/null | xargs readlink 2>/dev/null | grep -c inotify)
  [[ $watches -gt 0 ]] && echo "$watches $(cat "$pid/comm" 2>/dev/null) (PID: ${pid//[^0-9]/})"
done | sort -rn | head -10
```

**Root cause:** Typically a file watcher tool (IDE like VS Code's LSP server, `gulp`, `webpack`, a deployment agent, or Prometheus node-exporter on a massive filesystem) registering watches on every file in a large directory tree.

**Immediate fix:**
```bash
sysctl -w fs.inotify.max_user_watches=524288
sysctl -w fs.inotify.max_user_instances=512
echo "fs.inotify.max_user_watches=524288" >> /etc/sysctl.d/10-inotify.conf
echo "fs.inotify.max_user_instances=512"  >> /etc/sysctl.d/10-inotify.conf
```

**Structural fix:** Identify and configure the offending watcher to exclude large directories (e.g., `node_modules`, `.git`, build artifacts). In VS Code: `files.watcherExclude` setting. For webpack: `watchOptions.ignored`. This prevents the limit from being hit again after the increase.

## System Design Perspective

**Scalability**
- All kernel tunables (`somaxconn`, `rmem_max`, `file-max`) have conservative defaults designed for low-spec general-purpose machines. Production systems at any meaningful scale require a sysctl baseline applied at boot via `/etc/sysctl.d/`.
- The correct level to stop a brute-force attack is at the network perimeter (firewall/WAF), before traffic reaches the SSH daemon. fail2ban is a last-resort defense — the connection cost of 10k attempts/hour still consumes resources.
- Midnight maintenance windows are an anti-pattern at scale. Use `RandomizedDelaySec` on systemd timers and `anacron` for cron to spread load. At 1000 servers all running `logrotate` at 00:00 simultaneously, the shared NFS/SAN takes a write spike every night.

**Failure Modes**
- **Ghost disk space cascade:** A service writes to a log file. Logrotate renames and compresses it. The service still writes to the original inode via an open fd. The compressed file takes up space AND the old inode bytes are still counted. Fix: send SIGHUP to force log reopen.
- **Clock skew auth failures are non-obvious:** JWT/Kerberos tokens are time-bounded. A 5-second skew breaks authentication across all services. This is often misdiagnosed as a "misconfiguration" — the real cause is a stopped NTP daemon.
- **systemd-oomd kills at the cgroup level:** it evaluates memory pressure per cgroup (slice), not per process. A single leaking child process in a cgroup causes the entire cgroup (including healthy siblings) to be killed. Design: isolate leaky services in their own slice.
- **ext4 journal contention under parallel fsync:** multiple writers simultaneously waiting on the journal commit is a correctness/consistency design — ext4 cannot safely skip it. The fix is not to disable journaling but to use XFS (which handles concurrent transactions better) or switch to a filesystem better suited for write-heavy parallel workloads.

**Trade-offs**
- **nobarrier mount option:** disables write barrier which ensures data hits persistent storage before acknowledging writes. Improves performance by 10–30% but risks data corruption on power loss. Only acceptable on storage with battery-backed write cache.
- **Killing parent to reap zombies:** fixes the zombie leak but may bring down a healthy service. Evaluate whether the parent can be signaled (SIGCHLD) to call `wait()` instead — many daemons respond to SIGCHLD by reaping children.
- **inotify limit increase vs. structural fix:** raising `max_user_watches` is immediate relief but masks the real problem. A tool watching every file in `node_modules` (200k+ files) is architecturally broken. The real fix is exclusion lists, not a bigger limit.
- **BBR vs CUBIC congestion control:** BBR (Bottleneck Bandwidth and RTT) outperforms CUBIC on high-latency, high-bandwidth paths (cross-datacenter, satellite links). On local LAN or same-DC links, the difference is negligible and CUBIC is the safer known quantity.
