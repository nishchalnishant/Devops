## Hard

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
