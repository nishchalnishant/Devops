# Linux Processes and Memory Management

## Process Lifecycle

Every process originates from `fork()` (which clones the parent) followed by `exec()` (which replaces the process image). The chain starts at PID 1 (systemd/init).

```
BIOS → GRUB → kernel → [PID 1: systemd] → service processes → user shells → application processes
```

**Copy-On-Write (COW):** `fork()` does not immediately copy memory pages. Both parent and child share pages marked read-only. A write triggers a page fault, the kernel copies that page, and the write proceeds. This makes `fork()` efficient.

## Process States

| State | `ps` Code | Description |
|-------|-----------|-------------|
| Running | R | On CPU or in run queue |
| Interruptible sleep | S | Waiting for event (I/O, signal, timer) |
| Uninterruptible sleep | D | Blocked on kernel I/O — cannot be killed |
| Zombie | Z | Exited but parent hasn't called `wait()` |
| Stopped | T | Paused by SIGSTOP or SIGTSTP |
| Tracing stop | t | Paused by a debugger |

> **D-state (uninterruptible sleep)** processes cannot be killed with `kill -9`. They are waiting for a kernel I/O operation to complete. High D-state process counts indicate I/O subsystem problems (NFS hangs, dying disk).

## Zombie Processes

A zombie holds a slot in the process table but consumes no CPU or memory (its stack and heap are freed). It persists until the parent calls `wait()`. If the parent exits, zombies are reparented to PID 1 (systemd), which immediately reaps them.

```bash
# Find zombies
ps aux | awk '$8 == "Z"'

# Reap: Send SIGCHLD to parent, or kill the parent
```

## Signals

Signals are asynchronous software interrupts.

| Signal | Number | Description |
|--------|--------|-------------|
| SIGHUP | 1 | Hangup — daemons use this to reload config |
| SIGINT | 2 | Ctrl+C — interrupt from terminal |
| SIGQUIT | 3 | Ctrl+\ — quit with core dump |
| SIGKILL | 9 | Force termination — cannot be caught, blocked, or ignored |
| SIGTERM | 15 | Polite termination — default `kill` signal |
| SIGSTOP | 19 | Pause — cannot be caught or ignored |
| SIGCONT | 18 | Resume stopped process |
| SIGCHLD | 17 | Child process state change notification |
| SIGUSR1/2 | 10/12 | User-defined; application-specific |

```bash
kill -15 PID      # Graceful termination
kill -9 PID       # Force kill
kill -1 PID       # Reload config (SIGHUP)
killall nginx     # Kill by name
pkill -f pattern  # Kill by pattern
```

## CPU Scheduling: CFS

The **Completely Fair Scheduler (CFS)** tracks each process's **virtual runtime** (vruntime) — a time value weighted by priority. The scheduler always picks the process with the lowest vruntime.

**Nice values** (range -20 to +19, default 0) control priority. Lower nice = higher priority. Only root can set negative nice values.

```bash
nice -n 10 cmd              # Start with nice 10
renice -n 5 -p PID          # Change running process priority
chrt -f 50 cmd              # Set real-time FIFO policy, priority 50
```

**Real-time scheduling policies:**
- `SCHED_FIFO` — First-in-first-out, preempts normal processes
- `SCHED_RR` — Round-robin variant
- `SCHED_DEADLINE` — Periodic task guarantees

***

## Memory Management

### Virtual Memory

Each process has an isolated **virtual address space** (typically 128 TB on x86-64). The kernel maintains a **page table** that maps virtual pages to physical frames.

**Memory regions:**

| Region | Purpose |
|--------|---------|
| Text | Executable code (read-only, shared) |
| Data/BSS | Initialized and uninitialized global variables |
| Heap | Dynamically allocated memory (malloc/brk/mmap) |
| Stack | Function call frames, local variables (grows downward) |
| Memory-mapped | Shared libraries, file-backed mappings |

### Page Faults

| Type | Description |
|------|-------------|
| Minor page fault | Page is in memory but not yet mapped (COW page first access) |
| Major page fault | Requires reading from disk (page not in RAM) |

High major fault rates indicate memory pressure.

```bash
/proc/PID/smaps              # Detailed memory map
/proc/PID/status             # VmRSS, VmSwap
perf stat -e page-faults cmd # Count page faults
```

### Swap

When physical RAM is exhausted, the kernel moves **anonymous pages** (heap/stack) to the swap partition/file. Excessive swapping causes **thrashing** — system spends more time moving pages than doing work.

**vm.swappiness** (default 60) controls swap aggressiveness:
- `0` = avoid swapping unless absolutely necessary
- `100` = swap aggressively
- Recommended for databases: `10`

```bash
swapon -s                    # Show swap usage
vmstat 1                     # si/so = swap in/out pages per second
cat /proc/meminfo            # SwapTotal, SwapFree, SwapCached
```

### The OOM Killer

When RAM + swap are exhausted, the kernel invokes the **Out of Memory (OOM) killer**. It scores each process using `/proc/PID/oom_score` (0–1000) based on:
- Resident memory usage relative to total memory
- Child process memory
- Elapsed time (long-running processes penalized less)
- `oom_score_adj` (operator-settable, -1000 to +1000)

```bash
# Protect critical process
echo -1000 > /proc/$(pgrep sshd)/oom_score_adj   # Never kill sshd

# Prefer killing myapp
echo 500 > /proc/$(pgrep myapp)/oom_score_adj

# Check OOM events
dmesg | grep -i "oom\|killed process"
```

### Huge Pages

Standard pages are 4 KB. **Huge pages** (2 MB on x86-64) reduce TLB pressure for workloads with large memory footprints (databases, JVMs).

| Type | Description |
|------|-------------|
| Explicit huge pages | Pre-allocated via `/proc/sys/vm/nr_hugepages`; mapped with `MAP_HUGETLB` |
| Transparent Huge Pages (THP) | Kernel automatically promotes aligned 4KB pages to 2MB |

> **Warning:** THP can cause latency spikes for databases. Disable for Redis, MongoDB:
> ```bash
> echo never > /sys/kernel/mm/transparent_hugepage/enabled
> ```

***

## The Linux Boot Process

```
1. BIOS/UEFI
   ├── Power-on self-test (POST), detect hardware
   └── Select boot device, load bootloader from disk

2. GRUB (Grand Unified Bootloader)
   ├── Loads kernel image (vmlinuz) and initramfs into RAM
   └── Passes kernel command line parameters

3. Kernel Initialization
   ├── Decompresses itself
   ├── Initializes CPU, memory management, device drivers
   ├── Mounts initramfs (temporary root filesystem with drivers)
   ├── Mounts real root filesystem
   └── Starts PID 1

4. systemd (PID 1)
   ├── Reads unit files and target dependencies
   ├── Starts services in parallel based on dependency graph
   ├── Activates default target (multi-user.target or graphical.target)
   └── System is ready
```

### GRUB Configuration

```bash
# /etc/default/grub
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"
GRUB_CMDLINE_LINUX="rd.lvm.lv=rhel/root rhgb quiet"

# After editing, regenerate:
update-grub                          # Debian/Ubuntu
grub2-mkconfig -o /boot/grub2/grub.cfg  # RHEL
```

**Single-user / rescue mode:** Add `single` or `rd.break` to kernel command line in GRUB.

***

## Inodes

An **inode** is the data structure stored on disk that records file metadata: permissions, owner, timestamps, size, and block pointers. The filename is stored in the **directory entry** (dentry), which maps a name to an inode number.

**Consequences:**
- A file can have multiple hard links (multiple dentries → same inode)
- Symbolic links store the target path as file content; they have their own inode
- You can run out of inodes even with free disk space (`df -i` to check)
- Deleting a file decrements the inode's **link count** — space is freed only when count reaches zero AND no open file descriptors remain

```bash
stat file               # Show inode number, link count, timestamps
ls -i file              # Show inode number
df -i /                 # Inode usage on filesystem
```

***

## Summary: Key Takeaways

| Concept | Key Point |
|---------|-----------|
| fork()/exec() | Process creation: COW clone then replace image |
| Process states | R, S, D (uninterruptible), Z (zombie), T (stopped) |
| Zombie processes | Exited but not reaped; consumes process table slot |
| Signals | SIGHUP (reload), SIGTERM (polite), SIGKILL (force) |
| CFS scheduler | Fair CPU distribution via virtual runtime |
| Page faults | Minor (in memory), Major (disk read needed) |
| Swap | vm.swappiness controls aggressiveness |
| OOM killer | Kills highest-score process when memory exhausted |
| Huge pages | 2MB pages reduce TLB pressure for large workloads |
| Inodes | File metadata; separate from filename (dentry) |
