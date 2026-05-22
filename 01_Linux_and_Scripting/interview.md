# Linux and Scripting — Interview Prep

## Easy

```
Linux Easy Interview Topics
├── Processes & Threads
│   ├── Process: independent program, own memory space
│   └── Thread: lighter execution unit, shared memory within process
├── File Permissions
│   ├── chmod 755: owner rwx (7), group r-x (5), others r-x (5)
│   ├── chmod 644: owner rw- (6), group r-- (4), others r-- (4)
│   └── chmod vs chown: permissions vs ownership
├── Shell I/O
│   ├── >: redirect stdout, overwrites
│   ├── >>: redirect stdout, appends
│   ├── 2>: redirect stderr
│   └── |: pipe stdout of one command to stdin of next
├── File Operations
│   ├── find / -type f -size +100M: find large files
│   ├── ln -s: symbolic link (breaks if original deleted)
│   ├── ln: hard link (inode pointer, survives original deletion)
│   ├── stat, ls -i: view inode number
│   └── mkdir, cp, mv, rm -rf, touch
├── Process Viewing
│   ├── ps aux: all processes, all users, CPU/MEM/PID/state
│   └── kill (SIGTERM=15) vs kill -9 (SIGKILL=force)
├── Disk & Memory
│   ├── du -sh /path: directory size
│   ├── df -h: filesystem free space
│   └── free -m: RAM and swap usage
├── Resource Limits
│   └── ulimit: max open files, stack size, max memory per process
├── Network
│   ├── ss -tlnp / netstat -tlnp: listening ports with PIDs
│   └── ip addr / ifconfig: current IP address
├── Special Permissions
│   ├── Sticky bit: only file owner can delete (used on /tmp)
│   └── SUID: binary runs as file owner
├── Key Config Files
│   ├── /etc/fstab: filesystems mounted at boot
│   ├── /proc: virtual FS — kernel and process runtime state
│   └── cron / crontab: scheduled task daemon
├── Text Tools
│   ├── awk: field-based text processing and data extraction
│   ├── sed: stream editor — find/replace without opening file
│   └── xargs: pass stdin items as arguments to another command
└── Shell Concepts
    ├── source script.sh: runs in current shell (vars persist)
    ├── ./script.sh: runs in subshell (vars do NOT persist)
    ├── shebang (#!/bin/bash): specifies interpreter
    └── history, clear, exit/Ctrl+D
```

### First Principles

- A **process** is the kernel's unit of isolation — it has its own virtual address space, file descriptor table, and scheduling context. A **thread** shares the address space with its siblings, making communication cheap but mistakes shared too.
- **Permissions** exist because multiple users share one machine. The 3-tier (owner/group/others) model maps to the organizational reality: the file creator, the team, and everyone else.
- **Hard links** are simply multiple names for the same inode — the data is not duplicated. Space is freed only when both the link count hits zero AND no open file descriptors remain.
- **Symbolic links** are separate files that store a path string. The kernel resolves the path at access time — if the target moves, the link breaks. This is a deliberate trade-off: flexibility vs. fragility.
- **ulimit** exists because a misbehaving process (like one leaking file descriptors) should not be able to exhaust kernel resources for other processes on the same system.
- **Pipes** are kernel-managed in-memory buffers. No disk I/O occurs. This is why `ls | grep txt` is instant even on large directories.

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

**20. How do you create a new directory?**
`mkdir directory_name`

**21. How do you delete a non-empty directory?**
`rm -rf directory_name`

**22. How do you rename a file?**
`mv old_name new_name`

**23. How do you copy a file?**
`cp source_file destination_file`

**24. How do you see the last 10 lines of a file?**
`tail filename`

**25. How do you see the first 10 lines of a file?**
`head filename`

**26. How do you search for a word in a file?**
`grep "word" filename`

**27. How do you clear the terminal screen?**
`clear` or `Ctrl+L`

**28. How do you see the history of commands you typed?**
`history`

**29. How do you create a new empty file?**
`touch filename`

**30. How do you change your password?**
`passwd`

**31. How do you exit from the terminal?**
`exit` or `logout` or `Ctrl+D`

**32. How do you list all files including hidden ones?**
`ls -a`

**33. How do you print text to the terminal?**
`echo "hello world"`

**34. What command tells you which directory you are currently in?**
`pwd` (Print Working Directory)

### System Design Perspective

**Scalability**
- Easy-level knowledge covers day-to-day operations but these primitives underpin everything at scale. Permissions misconfigured on a shared service account directory can take down an entire deployment pipeline.
- `ulimit` defaults (often 1024 open files) are set for desktop users. Any service handling more than a few hundred clients simultaneously must raise this before going to production.

**Failure Modes**
- Running services as root (common beginner mistake): if the process is compromised, the attacker has full OS access. Always use a dedicated service account.
- Forgetting `set -e` in scripts means errors are silently swallowed. A half-executed deployment script can leave systems in an inconsistent state.
- Using `>` instead of `>>` in a logging script will truncate the log file on every script restart — all history is lost.

**Trade-offs**
- `kill` (SIGTERM) vs `kill -9` (SIGKILL): SIGTERM allows graceful cleanup (close connections, flush buffers, remove lock files). SIGKILL bypasses all cleanup — use it only when SIGTERM fails and you understand the consequences.
- `source` vs subshell execution: `source` is needed for setting environment variables that the calling shell must see (e.g., loading `.env` files). But sourcing untrusted scripts can modify your current shell's state permanently.

## Medium

```
Linux Medium Interview Topics
├── Memory Pressure Diagnosis
│   ├── free -h: total, used, available, swap
│   ├── /proc/meminfo: kernel-level memory counters
│   ├── vmstat 1 5: swap in/out rates, page faults
│   ├── dmesg | grep -i oom: OOM kill events
│   └── ps aux --sort=-%mem: top memory consumers
├── Idempotent Shell Scripting
│   ├── Check before act: if [ ! -d /path ]; then mkdir; fi
│   ├── set -euo pipefail: catch errors, unset vars, pipe failures
│   ├── Package managers have built-in idempotency (apt-get -y)
│   └── Write desired final state, not incremental steps
├── Filesystem Watching
│   └── inotifywait: uses Linux inotify kernel events, triggers on modify/create/delete
├── Load Average
│   ├── Three numbers: 1-min, 5-min, 15-min averages
│   ├── Includes: Runnable (CPU-waiting) + Uninterruptible (I/O-waiting) processes
│   ├── Load = CPU count means full utilization
│   └── Load >> CPU count means queuing = problem
├── I/O Wait Diagnosis
│   ├── top/vmstat: check %wa column (>20% sustained = high)
│   ├── iostat -xz 1: per-device utilization, await, queue depth
│   ├── iotop: per-process I/O usage
│   └── dstat --disk --io: combined view
├── Process Priority
│   ├── nice: set priority of new process (-20 highest, 19 lowest)
│   └── renice: change priority of running process
├── Signal Handling in Scripts
│   └── trap 'cleanup' INT TERM EXIT: catch signals and clean up temp files
├── set Options
│   ├── set -e: exit on any error
│   ├── set -u: error on unset variable
│   └── set -o pipefail: pipeline fails if any stage fails
├── Secrets Handling
│   ├── Never as CLI args (visible in ps aux)
│   ├── Environment variables set by calling process
│   ├── File with chmod 400
│   ├── Secret manager (Vault, AWS SSM) at runtime
│   └── stdin via read -r
├── Links (Hard vs Soft)
│   ├── Hard: same inode, survives original deletion, no cross-FS
│   └── Soft: path pointer, breaks if original moves, can cross FS
├── Bulk Find/Replace
│   └── grep -rl "old" . | xargs sed -i 's/old/new/g'
├── Shebang
│   └── #!/bin/bash: kernel uses this to select the interpreter
├── su vs sudo
│   ├── su: switch to root (needs root password)
│   └── sudo: run as root (needs user password, audited in /var/log/auth.log)
├── Cron Scheduling
│   └── 0 3 * * * /path/script.sh: run daily at 3 AM
├── I/O Redirection
│   ├── stderr: FD 2, redirect with 2>
│   └── Both streams: &> output.log
├── tar vs zip
│   ├── tar: archives only, needs -z for gzip, preserves Linux permissions
│   └── zip: archives + compresses, Windows-native, may not preserve perms
└── Key Concepts
    ├── less: page through large files (q to quit, /search)
    ├── Pipe (|): stdout of one command to stdin of next, no disk touch
    ├── chown user:group filename: change owner and group
    └── ip addr / ifconfig: current IP address
```

### First Principles

- **Memory pressure is not a single signal.** `free` shows available RAM, but `vmstat` shows whether pages are being swapped (si/so), and `dmesg` shows whether the OOM Killer already acted. You need all three to understand the trajectory.
- **Idempotency is a contract:** a script should be safe to run multiple times. This is the foundational requirement for automation — without it, re-running a failed deployment makes things worse, not better.
- **Load average is a queue length, not CPU percentage.** A system with 32 CPUs and load average 32 is fully utilized. A system with 4 CPUs and load average 32 has 28 processes waiting — that is the bottleneck signal.
- **I/O wait is invisible CPU waste.** The CPU is "idle" from the kernel scheduler's perspective, but processes can't make progress. High `%wa` means the bottleneck is the storage subsystem, not compute.
- **`set -euo pipefail` is the minimal safety harness** for any script that touches production. Without `pipefail`, `false | true` exits 0 — the error is silently swallowed.
- **`trap` exists because cleanup must happen regardless of how a script exits.** Signals, errors, and normal exits all need the same cleanup path. `trap 'cleanup' EXIT` covers all three with one line.

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

### System Design Perspective

**Scalability**
- Idempotent scripts are the foundation of Configuration Management (Ansible, Chef, Puppet). At scale, a script that fails half-way through on 500 servers must be safely re-runnable to bring all nodes to the desired state.
- `inotifywait` uses kernel inotify watches. The default limit is 8192 watches. On large codebases (monorepos, container image layers), this limit is hit quickly — increase `fs.inotify.max_user_watches`.

**Failure Modes**
- Load average trending up over the 15-minute window while 1-minute stays lower means the problem is not a spike — it's chronic. The 1/5/15 trend matters more than any single value.
- `set -e` does not catch all errors. In particular, errors in `if` conditions, `while`/`until` tests, and command lists using `||` are not caught. Use `|| { handle_error; exit 1; }` explicitly.
- Passing secrets as environment variables is better than CLI args, but environment variables can leak via `/proc/PID/environ` readable by the same user. For production, use a secrets manager that injects secrets directly into memory.

**Trade-offs**
- `nice` only affects CPU scheduling priority. It does not affect I/O priority. A "nice 19" backup job will still saturate disk I/O — use `ionice -c 3` for I/O as well.
- `tar` preserves ACLs, SELinux labels, and extended attributes (with `--xattrs`). `zip` does not. For server-to-server backup of Linux filesystems, `tar` is always the correct choice.
- `su` vs `sudo`: sudo provides per-command auditing in `/var/log/auth.log`. In production, all privileged actions should go through sudo so there's an audit trail. The trade-off is the password prompt — solved with NOPASSWD entries for specific commands only.

## Hard

```
Linux Hard Interview Topics
├── Memory Management (Advanced)
│   ├── OOM Killer: oom_score (RSS, child mem, oom_score_adj -1000..+1000)
│   ├── HugePages: 2MB pages reduce TLB misses for large DB memory footprints
│   ├── Transparent Huge Pages: auto, but causes latency spikes in Redis/MongoDB
│   ├── Dirty ratio: vm.dirty_ratio blocks writes; vm.dirty_background_ratio flushes
│   ├── Swappiness: 0–100 aggressiveness; DB = 1–10
│   ├── Memory leak detection: top (RSS growth), valgrind, bcc/memleak, gcore
│   └── Copy-on-Write (CoW): fork() shares pages until a write triggers page copy
├── cgroups v2
│   ├── Unified hierarchy (vs v1 separate hierarchies)
│   ├── Controllers: cpu.max, memory.max, io.max, pids.max
│   ├── Kubernetes: cgroup-driver=systemd delegates to systemd
│   └── Resource isolation for containers
├── Performance Profiling
│   ├── perf record -g: sample call stacks → flame graphs
│   ├── Flame graphs: wide plateau at top = hottest CPU path
│   └── eBPF (bpftrace, BCC): sandboxed kernel probes, near-zero overhead
├── eBPF
│   ├── Runs sandboxed programs in kernel without modules
│   ├── Tools: bpftrace, BCC, Cilium
│   └── Use cases: syscall latency, TCP tracing, function profiling
├── High-Performance Log Pipeline
│   ├── Collection: Fluent Bit / Vector / Promtail (lightweight agents)
│   ├── Transport: Kafka (decouples producers/consumers, handles bursts)
│   ├── Processing: Logstash / Flink / Vector (parse, enrich, route)
│   ├── Storage: OpenSearch (search) vs Loki (label-indexed, high cardinality)
│   └── Backpressure: Kafka buffers; dead letter queues for bad messages
├── LVM Snapshots
│   ├── Copy-on-Write: every write = read old + write to snap + write original
│   ├── 3 I/O ops per write → 50–70% perf drop on write-heavy DBs
│   └── LVM Thin Snapshots: more efficient, but monitor metadata space
├── CPU Scheduling
│   ├── CFS (Completely Fair Scheduler): tracks vruntime via Red-Black Tree
│   ├── Lowest vruntime process runs next
│   ├── Voluntary context switch: process waits on I/O or mutex
│   ├── Involuntary context switch: kernel preempts on time slice expiry
│   └── High involuntary switches = CPU saturation; check pidstat -w
├── Low Latency Tuning
│   ├── isolcpus: remove cores from scheduler for dedicated app use
│   ├── smp_affinity: bind NIC/disk interrupts away from isolated cores
│   ├── Disable C-States: prevent CPU power saving (processor.max_cstate=1)
│   ├── HugePages: avoid page faults
│   └── DPDK / OpenOnload: kernel bypass for network stack
├── Thundering Herd
│   ├── Problem: all waiting processes wake on one event, only one handles it
│   └── Fix: EPOLLEXCLUSIVE flag (Linux 4.5+) wakes only one waiter
├── Zombie vs Orphan
│   ├── Zombie: finished but entry remains for parent to read exit code
│   └── Orphan: parent exited; init (PID 1) adopts and reaps
├── Systemd Watchdog
│   ├── WatchdogSec=30s: requires heartbeat from app every 30s
│   ├── Restart=on-watchdog: systemd kills and restarts if no heartbeat
│   └── App-side: sd_notify("WATCHDOG=1") periodic call
├── Linux Capabilities
│   ├── SUID: grants ALL root powers — dangerous
│   ├── Capabilities: fine-grained (CAP_NET_BIND_SERVICE, CAP_SYS_ADMIN)
│   └── Principle of Least Privilege: give only the capability needed
├── Namespace Isolation (Manual)
│   └── unshare --fork --pid --mount-proc /bin/bash: PID namespace, shell = PID 1
├── Kernel VFS Caches
│   ├── Inode cache: stores file metadata (permissions, size, owner)
│   └── Dentry cache: maps filenames to inode numbers (path lookup acceleration)
├── Hard/Soft Limits
│   ├── Soft limit: current enforced; user can raise up to hard limit
│   └── Hard limit: absolute max; only root can increase
└── Debugging
    ├── Segfault: dmesg → enable core dump → gdb <binary> core.<pid> → bt
    ├── Memory leak: RSS growth check → valgrind / bcc memleak → gcore
    └── strace: trace syscalls to find stuck read()/open()/connect() calls
```

### First Principles

- **Memory is finite.** When physical RAM is exhausted, the kernel must choose: page to swap (slow) or kill a process (disruptive). The OOM Killer's scoring algorithm is a deterministic triage system — not random.
- **CPU scheduling fairness vs. latency:** The CFS scheduler optimizes for fairness across all processes. Latency-sensitive workloads need the opposite — guaranteed CPU time with no preemption. That is why `isolcpus` and real-time scheduling policies exist.
- **eBPF solves the observability dilemma:** to measure something you must instrument it, but instrumentation changes the thing you're measuring. eBPF's sandboxed in-kernel programs add near-zero overhead because there's no context switch into userspace per event.
- **cgroups exist because processes don't self-limit.** In a shared cluster, one runaway process can starve others. cgroups enforce hard boundaries at the kernel level — no application cooperation required.
- **Copy-on-Write is an optimization based on a common pattern:** most `fork()` calls are immediately followed by `exec()`, so copying all parent memory would be pure waste. CoW defers the cost to the first write.
- **Capabilities replace SUID because privilege is not binary.** A process that only needs to bind to port 80 should not have the ability to reboot the machine — SUID grants both. Capabilities surgically grant only the needed power.

**1. How does the Linux kernel's OOM killer select which process to terminate?**
The OOM killer scores each process using `/proc/PID/oom_score`, which factors in: the process's RSS (resident set size), the proportion of physical memory it uses, whether it has CAP_SYS_ADMIN, and the `oom_score_adj` value (tunable per process, range -1000 to +1000). The process with the highest score is killed. You can protect critical processes with `oom_score_adj = -1000` (which sets score to 0, preventing OOM kill) or deprioritize them with positive adjustments.

**2. Explain Linux cgroups v2 and how they are used in containers.**
cgroups v2 is a unified hierarchy for resource control. Unlike v1 (which had separate hierarchies per controller), v2 uses a single tree where each node can have multiple controllers (cpu, memory, io, pids). Containers (Docker, Kubernetes) use cgroups to:
- Enforce memory limits (`memory.max`) and kill containers that exceed them.
- Enforce CPU bandwidth (`cpu.max`, format: `quota period`).
- Limit I/O bandwidth (`io.max`).
- Limit process count (`pids.max`).

Kubernetes uses cgroups v2 when `--cgroup-driver=systemd` is set on the kubelet, which delegates cgroup management to systemd.

**3. How do you debug a performance regression using perf and flame graphs?**
1. Run `perf record -g -p <PID> -- sleep 30` to record call stacks for 30 seconds.
2. Run `perf script` to convert to a text format.
3. Use Brendan Gregg's `flamegraph.pl` to generate a flame graph SVG.
4. The flame graph visualizes where CPU time is spent: wide stacks = hot code paths. Identify the widest plateau at the top of the graph — that function is the hottest path consuming CPU.

**4. What is eBPF and how is it used for performance observability?**
eBPF (extended Berkeley Packet Filter) allows running sandboxed programs in the Linux kernel without modifying kernel source. For performance observability: tools like `bpftrace`, `BCC`, and `Cilium` use eBPF to attach probes to kernel and user-space functions at runtime. You can measure exact latency of system calls, trace TCP connections, profile function call frequency — all with near-zero overhead compared to traditional instrumentation. Example: `bpftrace -e 'tracepoint:syscalls:sys_enter_read { @[comm] = count(); }'` counts read syscalls per process name.

**5. How do you implement a high-performance log pipeline from multiple servers?**
Architecture:
1. **Collection:** Use a lightweight agent (`Fluent Bit`, `Vector`, `Promtail`) on each server — reads from journald/file, parses structured fields, compresses, and forwards.
2. **Transport:** Kafka as a buffer between collectors and processors — decouples producer (servers) from consumer (processing pipeline). Handles burst traffic.
3. **Processing:** Logstash, Flink, or Vector processes the Kafka stream — parses, enriches (GeoIP, service name lookup), and routes.
4. **Storage:** OpenSearch/Elasticsearch for search workloads; Loki for high-cardinality log storage with label indexing only.
5. **Backpressure:** If downstream is slow, Kafka buffers — agents are not blocked. Dead letter queues for unparseable messages.

**6. Explain the performance impact of LVM snapshots on write operations.**
LVM snapshots use **Copy-on-Write (CoW)**. When a snapshot exists, every write to an original block requires:
1. Reading the old block.
2. Writing it to the snapshot area.
3. Overwriting the original block.
This effectively turns every write into **three I/O operations** (1 Read + 2 Writes). In write-heavy databases, this can cause a 50-70% performance drop. Modern solutions use **LVM Thin Snapshots** which are much more efficient but require careful monitoring of metadata space.

**7. What is the difference between Voluntary and Involuntary context switches?**
- **Voluntary:** The process gives up the CPU because it's waiting for something (I/O, a sleep call, or a mutex).
- **Involuntary:** The kernel forces the process off the CPU because its time slice is up or a higher-priority process needs to run.
**SRE Context:** High *involuntary* switches indicate your system is CPU-saturated (too many processes for the cores). High *voluntary* switches often indicate an application bottleneck (waiting on locks or I/O). Check via `pidstat -w`.

**8. How do HugePages improve database performance?**
Standard Linux pages are 4KB. A 128GB database would require 32 million page table entries. The CPU's **TLB cache** cannot fit this, leading to "TLB Misses" and high overhead. By using **HugePages (2MB or 1GB)**, the number of entries drops significantly, fitting the entire mapping into the CPU cache and improving performance by 10-15%.

**9. How do you implement a Systemd Watchdog for a service?**
In the `[Service]` section of the unit file:
1. `WatchdogSec=30s`: The service must send a "heartbeat" to systemd every 30s.
2. `Restart=on-failure`: If the heartbeat stops, systemd kills and restarts the service.
3. **Application Side:** The app must be coded to call `sd_notify("WATCHDOG=1")` periodically. This prevents "Ghost Services" that are technically running but logically deadlocked.

**10. How do you tune the Linux kernel for a "Low Latency" trading application?**
- Use **Isolcpus**: Isolate specific CPU cores from the kernel scheduler so only the app runs there.
- **Interrupt Affinity**: Move hardware interrupts (NIC/Disk) away from those isolated cores using `smp_affinity`.
- **Disable C-States**: Prevent the CPU from entering power-saving modes using `processor.max_cstate=1` in GRUB.
- **HugePages**: Pre-allocate memory to avoid page faults.
- **Kernel Bypass**: Use DPDK or Solarflare OpenOnload for the network stack.

**11. Explain the "Thundering Herd" problem and how the Linux kernel addresses it.**
The thundering herd occurs when many processes wait for an event (like an incoming connection). When the event happens, the kernel wakes them all up, but only one can handle it; the rest go back to sleep, causing massive context switch overhead.
**Kernel Fix:** `EPOLLEXCLUSIVE` flag in `epoll_ctl` (since 4.5) ensures only one waiter is woken up.

**12. What are "Orphan" processes vs. "Zombie" processes?**
- **Zombie:** A process that has finished execution but still has an entry in the process table to allow its parent to read the exit code.
- **Orphan:** A process whose parent has finished or crashed. The `init` (PID 1) process adopts orphans and reaps them.

**13. How does the "Completely Fair Scheduler" (CFS) work?**
CFS doesn't use traditional "time slices". It uses **vruntime** (virtual runtime). It maintains a **Red-Black Tree** of processes. The process with the smallest `vruntime` is at the leftmost node and is chosen to run. When a process runs, its `vruntime` increases. This ensures that every process gets its "fair share" of the CPU over time.

**14. Explain the difference between `soft` and `hard` limits in `/etc/security/limits.conf`.**
- **Soft Limit:** The current limit enforced for the user/process. The user can increase it up to the Hard Limit.
- **Hard Limit:** The absolute maximum limit set by the root user. Non-root users cannot exceed this.

**15. How do you detect and fix "Memory Leak" in a running Linux process?**
1. **Identify:** Use `top` or `ps` to see if `RSS` is growing continuously.
2. **Trace:** Use `valgrind --leak-check=full` (if you can restart it) or `gdb` to attach to a running process.
3. **Advanced:** Use `bcc` tools like `memleak` to trace `malloc` and `free` calls with zero overhead.
4. **Core Dump:** Trigger a core dump with `gcore <PID>` and analyze the heap using `strings` or `visualizers`.

**16. What is the role of `dentry` and `inode` caches in Linux?**
- **Inode Cache:** Stores file metadata (size, owner, permissions).
- **Dentry Cache (Directory Entry):** Maps file names to Inode numbers.
Searching for a file path `/a/b/c` is expensive. The kernel caches these mappings in RAM to avoid repeated disk reads. High "VFS Cache" usage in `free -h` is usually good.

**17. Explain the "Dirty Ratio" and "Dirty Background Ratio" in sysctl.**
- `vm.dirty_background_ratio`: When dirty memory (unsaved changes) reaches this %, the kernel starts `pdflush` to write to disk in the background.
- `vm.dirty_ratio`: When dirty memory reaches this %, the kernel **blocks** all new writes until the data is flushed. This causes the system to "freeze".

**18. How do you implement "Namespace Isolation" manually without Docker?**
Use the `unshare` command.
Example: `unshare --fork --pid --mount-proc /bin/bash` creates a new shell with its own PID namespace. You will see your shell as PID 1.

**19. What is "Copy-on-Write" (CoW) in the context of the `fork()` system call?**
When a process forks, the kernel doesn't copy the memory. Both parent and child point to the **same physical memory pages**. Only when one process tries to *write* to a page does the kernel copy that specific page for that process. This makes `fork()` extremely fast and memory-efficient.

**20. How do you debug a "Segmentation Fault"?**
1. Check `dmesg` for the memory address and the library that caused it.
2. Enable core dumps: `ulimit -c unlimited`.
3. Load the core dump into GDB: `gdb <binary> core.<pid>`.
4. Run `bt` (backtrace) to see the exact line of code that caused the crash.

**21. Explain the difference between "Vertical" and "Horizontal" scaling for a Linux-based database.**
- **Vertical:** Adding more CPU/RAM to the same server. Limits: Hardware ceiling and single point of failure.
- **Horizontal:** Adding more servers (Nodes). Requires load balancing and data sharding/replication.

**22. What is a "Capabilities" in Linux, and why are they better than SUID?**
SUID gives a binary **all** root permissions. Capabilities break down root powers into small pieces (e.g., `CAP_NET_BIND_SERVICE` allows binding to port 80 without being full root). This follows the "Principle of Least Privilege".

**23. How do you find which process is using a specific Port?**
`lsof -i :80` or `netstat -tunlp | grep 80`.

**24. What is the difference between `systemd` and `SysVinit`?**
- **SysVinit:** Executes scripts sequentially (one by one). Slow and lacks dependency management.
- **Systemd:** Executes scripts in parallel, uses sockets and D-Bus for activation, and provides cgroups-based process tracking.

**25. How do you troubleshoot high "I/O Wait" (`%wa`)?**
1. Find the disk: `iostat -xz 1`.
2. Find the process: `iotop -Pa`.
3. Find the file: `lsof -p <PID>`.

**26. Explain "Sticky Bit" on a directory.**
When set (e.g., `/tmp`), it allows any user to write files, but **only the owner** of a file can delete it. This prevents users from deleting each other's files in a shared space.

**27. How do you recover a deleted file that is still open by a process?**
1. Find the PID: `lsof | grep <filename>`.
2. Go to `/proc/<PID>/fd/`.
3. Copy the file descriptor back to a safe location: `cp 4 /tmp/recovered_file`.

**28. What is "Swappiness" and how should it be tuned for a Database?**
`vm.swappiness` (0-100) controls how aggressively the kernel swaps memory to disk. For databases, set it low (e.g., `1` or `10`) to keep the database in physical RAM as much as possible.

**29. How do you automate the rotation of custom application logs?**
Create a config file in `/etc/logrotate.d/myapp`. Define the frequency, rotation count, compression, and `postrotate` scripts (e.g., to signal the app to reopen the log file).

**30. What is the difference between `SIGTERM` (15) and `SIGKILL` (9)?**
- `SIGTERM`: A polite request to stop. The app can catch the signal, finish its current task, and clean up.
- `SIGKILL`: An immediate kill by the kernel. The app cannot catch it and cannot clean up.

**31. How do you implement a "Heartbeat" check in a Bash script?**
Use a `while` loop that pings a service or checks for a lock file, sleeps for X seconds, and sends an alert/restarts the service if the check fails.

### System Design Perspective

**Scalability**
- The OOM Killer is a reactive mechanism. At scale, the correct answer is proactive: set memory limits via cgroups (Kubernetes resource limits use exactly this) so no single process can starve others. OOM killing at scale causes cascading restarts.
- eBPF-based observability scales better than strace/perf because it requires no process restart, no binary recompilation, and has near-zero overhead. At thousands of requests/sec, strace can saturate a CPU just from tracing overhead.
- Log pipelines: without Kafka as a buffer, a slow storage backend causes backpressure all the way to the application. Kafka decouples durably — the critical design choice is at the transport layer.

**Failure Modes**
- **HugePages + THP on Redis:** Transparent Huge Pages cause latency spikes because the kernel may defragment memory asynchronously to create 2MB blocks, causing page faults at unpredictable times. Always disable THP for Redis and MongoDB.
- **CFS vruntime starvation:** A process that is mostly sleeping accumulates very low vruntime. When it wakes up, it gets a burst of CPU that can spike latency for other processes. This is expected CFS behavior, not a bug.
- **oom_score_adj=-1000 abuse:** Protecting too many processes prevents the OOM killer from working at all. If everything is protected, the kernel has nothing to kill and may resort to system-level panic.
- **Thundering herd without EPOLLEXCLUSIVE:** Systems using older `accept()` without `SO_REUSEPORT` or `epoll` with exclusive wakeup will see CPU spikes proportional to the number of waiters on high-concurrency services.

**Trade-offs**
- **LVM snapshots vs. database-native backup:** LVM snapshots are filesystem-consistent but not application-consistent (a DB may have in-flight transactions). For databases, use SIGSTOP + snapshot + SIGCONT, or use the DB's own backup tools.
- **Systemd watchdog vs. external health check:** Watchdog is tightly coupled to the process lifecycle and cannot detect application-level liveness (a deadlocked app can still send `sd_notify`). External health checks (HTTP endpoint, query) catch more failure modes but add network dependency.
- **Vertical vs. horizontal scaling:** Vertical scaling (more RAM/CPU per node) is simpler operationally but has a hardware ceiling and creates a single point of failure. Horizontal scaling requires distributed coordination (consensus, sharding) — complex but resilient.

**Why These Design Choices Were Made**
- The **vruntime Red-Black Tree** in CFS gives O(log n) scheduling decisions. A simple sorted list would be O(n) on process count. At thousands of threads, this matters.
- **Namespaces + cgroups = containers.** Docker did not invent a new technology — it packaged existing kernel primitives (PID namespaces, mount namespaces, cgroups, overlay filesystems) into a usable interface.
- **Dirty ratio two-level design** (`dirty_background_ratio` < `dirty_ratio`) exists to smooth writes: background flush starts early so the hard stop (`dirty_ratio`) is rarely hit. Without the two levels, writes would be smooth until a sudden full stop.

---

## Hard (continued) — Kubernetes, Observability & Production Debugging

**Q: How do Kubernetes QoS classes map to Linux cgroups, and which pod gets evicted first under memory pressure?**

Kubernetes assigns every pod a QoS class based on its resource spec, which directly maps to cgroup configuration on the node:

| QoS Class | Condition | cgroup `memory.limit_in_bytes` |
|---|---|---|
| **Guaranteed** | `requests == limits` for every container | Set to exactly the limit value |
| **Burstable** | `requests < limits` (at least one container) | Set to the limit; requests are a scheduling hint only |
| **BestEffort** | No requests or limits | No cgroup memory limit (can use all available memory) |

**Eviction order** when the kubelet's eviction manager detects pressure (triggered before the kernel OOM killer fires):

1. **BestEffort** pods are evicted first — they hold no cgroup memory reservation.
2. **Burstable** pods are next — evicted in order of how far their usage exceeds their requests.
3. **Guaranteed** pods are evicted last — only if all BestEffort and Burstable pods are already gone.

**Soft vs. hard eviction thresholds:**
- `evictionSoft` (e.g., `memory.available < 500Mi`) — kubelet waits a grace period (`evictionSoftGracePeriod`) before evicting. Pods receive SIGTERM and can drain.
- `evictionHard` (e.g., `memory.available < 100Mi`) — kubelet evicts immediately with no grace period.

**Preventing eviction of critical services:**
```yaml
# Set requests == limits → Guaranteed QoS (never evicted first)
resources:
  requests:
    memory: "512Mi"
  limits:
    memory: "512Mi"
```

```yaml
# PodDisruptionBudget prevents simultaneous eviction
apiVersion: policy/v1
kind: PodDisruptionBudget
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: critical-service
```

**Senior nuance:** The kernel OOM killer fires within the pod's cgroup if a container exceeds its `memory.limit_in_bytes`. The kubelet's eviction manager is a higher-level, proactive mechanism that acts at lower thresholds so the kernel OOM killer should rarely fire in a well-configured cluster.

---

**Q: How would you use `bpftrace` to measure `openat()` syscall latency in production without the overhead of strace?**

**Why strace is unsuitable for production:**
`strace` uses `ptrace(PTRACE_SYSCALL)`, which forces a kernel→user context switch on every syscall entry and exit. On a busy process making 100k syscalls/sec, this adds ~200k context switches — 50–100× CPU overhead. The act of measuring changes the system's behavior (Heisenbug).

**eBPF approach with bpftrace:**

```bash
sudo bpftrace -e '
  tracepoint:syscalls:sys_enter_openat {
    @start[tid] = nsecs;
    @filename[tid] = str(args->filename);
  }
  tracepoint:syscalls:sys_exit_openat /@start[tid]/ {
    @lat[comm, @filename[tid]] = hist(nsecs - @start[tid]);
    delete @start[tid];
    delete @filename[tid];
  }
'
```

**Interpreting the output — distinguishing root cause:**

```
@lat[myapp, /data/db/records.db]:
[1us,   10us)    50  |@@@                        |
[10us, 100us)   200  |@@@@@@@@@@@@               |
[100us,  1ms)  8000  |@@@@@@@@@@@@@@@@@@@@@@@@@@@@| ← modal latency here
[1ms,   10ms)   500  |@@@@@@@@                   |
```

- **Consistent high latency for specific paths** → filesystem metadata (cold inode/dentry cache, NFS round-trip).
- **High latency across all files** → kernel scheduling (process being preempted while waiting for I/O).

**Distinguish scheduling vs. I/O with `pidstat`:**
```bash
pidstat -w -p <pid> 1
# cswch/s   = voluntary context switches (process sleeping for I/O)
# nvcswch/s = involuntary context switches (CPU oversubscribed, preempted)
```

High `nvcswch` → CPU contention. High `cswch` → I/O wait (pages not in page cache).

**Key advantages over strace:**
- Overhead < 1% CPU even at 1M syscalls/sec (eBPF runs in kernel, no context switch per event).
- BPF bytecode is verified by the kernel verifier before loading — cannot crash the kernel.
- Attach to `tracepoint:` (not `kprobe:`) so probes survive function inlining across kernel versions.

---

**Q: A Go service's OS-reported RSS grows from 200 MB to 500 MB over 24 hours while Go's heap stays stable. What are the causes and how do you diagnose a goroutine leak?**

**Why RSS and heap diverge:**

Go's runtime reports heap via `runtime.MemStats.HeapInuse`. RSS (Resident Set Size) is what the OS actually has mapped into physical pages. The gap comes from:

1. **Goroutine stack accumulation** — each goroutine starts with a 2–8 KB stack that grows as needed. 10,000 leaked goroutines = 20–80 MB of stacks invisible to the heap allocator.
2. **cgo allocations** — memory from `C.malloc()` is outside Go's GC; the OS accounts for it in RSS but Go's `MemStats` does not.
3. **Memory-mapped files** — `syscall.Mmap()` appears in RSS but not in Go's heap.
4. **Freed pages not returned to OS** — Go's GC frees objects but the runtime may retain virtual address ranges, returning them to the OS via `MADV_DONTNEED` lazily (controllable with `GOGC` and `runtime/debug.FreeOSMemory()`).

**Diagnosing a goroutine leak:**

Expose the pprof endpoint (standard in any Go service):
```go
import _ "net/http/pprof"
go func() { http.ListenAndServe("localhost:6060", nil) }()
```

```bash
# Capture goroutine profile
curl http://localhost:6060/debug/pprof/goroutine > goroutine.prof
go tool pprof goroutine.prof

(pprof) top
# If you see thousands of goroutines blocked at the same stack frame,
# that is your leak site.
```

**Programmatic monitoring:**
```go
func monitorGoroutines() {
    for range time.Tick(30 * time.Second) {
        n := runtime.NumGoroutine()
        if n > 5000 {
            // Dump stack traces to logs
            buf := make([]byte, 1<<20)
            buf = buf[:runtime.Stack(buf, true)]
            log.Errorf("goroutine leak: %d goroutines\n%s", n, buf)
        }
    }
}
```

**Common leak pattern and fix:**
```go
// BUG: goroutine blocks on conn.Read() forever if client hangs
go func() {
    buf := make([]byte, 4096)
    conn.Read(buf) // never returns if client stalls
}()

// FIX: always propagate context with deadline
go func(ctx context.Context) {
    conn.SetDeadline(time.Now().Add(30 * time.Second))
    buf := make([]byte, 4096)
    select {
    case <-ctx.Done():
        conn.Close()
        return
    default:
        conn.Read(buf)
    }
}(ctx)
```

**Heap profile for memory leaks (In-Use vs. Allocated):**
```bash
curl http://localhost:6060/debug/pprof/heap > heap.prof
go tool pprof heap.prof
(pprof) top -inuse_space   # memory currently held (leak indicator)
(pprof) top -alloc_space   # all memory ever allocated (hotspot indicator)
```

A function with high `inuse_space` that keeps growing over time is holding memory that the GC cannot collect — a memory leak.
