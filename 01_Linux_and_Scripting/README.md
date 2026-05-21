# Linux Operating System

```
Linux Operating System
├── Installation & Setup
│   ├── Distro choice: Ubuntu/Debian (dev) vs RHEL/Rocky (enterprise)
│   ├── Initial config: hostname, timezone (timedatectl), networking (nmcli)
│   └── Security first: disable root SSH, firewall (ufw/firewalld)
├── Command Line Interface (CLI)
│   ├── Navigation: pwd, ls -la, cd
│   ├── System monitoring: top, htop, df -h, free -m
│   └── Process management: ps aux | grep, kill -9 <PID>
├── Filesystem & Permissions
│   ├── FHS: /etc (configs), /var/log (logs), /bin & /sbin (binaries)
│   ├── Permissions: rwx = read(4), write(2), execute(1)
│   ├── chmod/chown: User, Group, Others (e.g., 755, 644)
│   ├── Hard links: point to inode, survive original deletion
│   └── Soft links: point to filename path, break on deletion
├── Package Management
│   ├── APT (Debian/Ubuntu): apt update, apt install
│   ├── YUM/DNF (RHEL/CentOS): yum install, dnf upgrade
│   └── Used inside Dockerfiles and Ansible Playbooks
├── Virtualization
│   ├── Type 1 hypervisor: VMware ESXi, KVM (bare metal)
│   ├── Type 2 hypervisor: VirtualBox (hosted)
│   └── VMs vs Containers: full OS vs application layer only
├── Text Processing Power Tools
│   ├── grep: search strings in files/logs
│   ├── find: locate files by name, size, date
│   ├── sed: stream editor — in-place find/replace
│   └── awk: column-based data processing
├── System Internals (SRE Level)
│   ├── Kernel: bridge between software and hardware
│   ├── Syscalls: open(), read(), write(), fork()
│   ├── VFS: everything is a file (/proc, /sys)
│   ├── Process parent/child: fork(), PID 1 = systemd
│   ├── Zombie processes: child exited, parent not reaped
│   ├── Orphan processes: parent died, adopted by PID 1
│   └── OOM Killer: oom_score decides which process dies
├── Boot Process
│   ├── BIOS/UEFI → GRUB → Kernel → systemd (PID 1)
│   └── systemd: parallel service startup, replaces SysVinit
├── Advanced Debugging
│   ├── strace -p <pid>: trace system calls
│   ├── tcpdump -i eth0: capture network packets
│   ├── df -i: check inode exhaustion
│   └── lsof | grep deleted: find open-but-deleted files
├── SRE Power Tools (Quick Reference)
│   ├── iostat: disk I/O statistics
│   ├── ss / netstat: socket and network stats
│   ├── journalctl -u <svc>: service logs via systemd
│   ├── lsof: open files and ports
│   └── nice / renice: CPU priority management
├── Troubleshooting Workflow
│   ├── Sluggish server: check top, %wa (I/O wait), free -m (swap)
│   ├── dmesg -T: kernel messages (OOM, TCP drops, hardware errors)
│   └── ps aux | grep 'Z': zombie process count
└── Production Best Practices
    ├── No manual SSH in prod: use Ansible or AWS SSM
    ├── Log rotation: logrotate to prevent disk fill
    ├── Kernel hardening: SELinux/AppArmor, disable unused services
    └── Anti-pattern: running services as root
```

## First Principles

- A computer has hardware (CPU, RAM, disk, network) that needs a manager — that is the **kernel**.
- Multiple programs running simultaneously cannot be allowed to stomp on each other's memory — the kernel enforces **process isolation** via virtual address spaces.
- Programs cannot directly control hardware (that would be chaos) — they must ask the kernel politely via **system calls** (`open()`, `read()`, `write()`, `fork()`).
- Users need protection from each other on shared systems — the kernel enforces **permissions** (rwx for owner/group/others) and **user IDs**.
- Executing arbitrary programs is risky — the kernel separates **Kernel Space** (ring 0, full hardware access) from **User Space** (ring 3, restricted), and crossing the boundary costs a context switch.
- "Where are my files?" needs a consistent answer regardless of disk type — the **Virtual File System (VFS)** provides a unified interface; everything (hardware, processes, sockets) is exposed as a file.
- When RAM is full, the system must not crash — the kernel uses **swap** as overflow, and the **OOM Killer** as a last resort with a scoring algorithm.
- Service management must be deterministic and recoverable — **systemd** (PID 1) manages dependencies, parallelizes startup, and restarts failed services.

Linux is the "natural habitat" of a DevOps engineer. These notes cover the transition from a casual user to a system power-user.

#### 1. Installation / Setup

Before a server can host an application, it must be properly initialized.

* Distro Choice: Most DevOps environments use Ubuntu/Debian (popular for developers) or RHEL/CentOS/Rocky Linux (enterprise standard).
* Initial Config: Includes setting the hostname, configuring the timezone (`timedatectl`), and setting up basic networking (`ip addr`, `nmcli`).
* Security First: The first step after installation is usually disabling root SSH login and setting up a firewall (like `ufw` or `firewalld`).

#### 2. Command Line Interface (CLI)

The CLI is where speed and automation happen.

* Navigation: `pwd` (where am I?), `ls -la` (show all files), `cd` (change directory).
* System Monitoring: `top` or `htop` to see CPU/RAM usage in real-time, `df -h` to check disk space, and `free -m` for memory status.
* Process Management: Finding a "stuck" process with `ps aux | grep app_name` and stopping it with `kill -9 <PID>`.

#### 3. Filesystem / Storage / User Permissions

Linux treats everything as a file, and who can touch those files is strictly controlled.

* Filesystem Hierarchy (FHS):
  * `/etc`: The "Nerve Center" where all configuration files live (e.g., Nginx or SSH configs).
  * `/var/log`: Where applications write their history—essential for troubleshooting.
  * `/bin` & `/sbin`: Where the system's executable tools are stored.
* Permissions (chmod/chown):
  * rwx: Read (4), Write (2), Execute (1).
  * Structure: Permissions are set for the User, Group, and Others. (e.g., `chmod 755` means the owner can do everything, others can only read and execute).

#### 4. Package Management

Instead of downloading `.exe` files, Linux uses package managers to handle software and their "dependencies."

* APT (Advanced Package Tool): Used in Ubuntu/Debian. Commands: `apt update`, `apt install nginx`.
* YUM/DNF: Used in RHEL/CentOS. Commands: `yum install git`, `dnf upgrade`.
* Why it matters: In DevOps, we use these commands inside Dockerfiles or Ansible Playbooks to automate software setup across thousands of servers.

#### 5. Virtualization

Virtualization allows you to run multiple "virtual" computers on a single physical machine.

* Hypervisors:
  * Type 1 (Bare Metal): Runs directly on hardware (e.g., VMware ESXi, KVM).
  * Type 2 (Hosted): Runs on top of an OS (e.g., VirtualBox).
* VMs vs. Containers: While a VM virtualizes the entire hardware (including a full OS), a container only virtualizes the application layer, making it much faster and lighter.

#### 6. Utilities & Tools (The "Power Tools")

These are the text-processing "Big Four" used to parse logs and automate configuration changes.

* grep: The "Search" tool. Used to find specific strings in massive log files (e.g., `grep "ERROR" /var/log/syslog`).
* find: Used to locate files based on attributes like name, size, or modification date.
* sed (Stream Editor): Used to find and replace text _without_ opening the file. Essential for automation (e.g., `sed -i 's/80/8080/g' config.conf`).
* awk: A powerful language for processing data in columns. If you need to "get the second word of every line in this log," you use `awk`.



This is Section 5: Linux Operating System. At a mid-to-senior SRE level, Linux is not just about "knowing commands"—it is about understanding how the Kernel manages hardware resources and how User Space applications interact with those resources.

In an interview, you are expected to explain what happens "under the hood" when a system is under pressure.

***

#### 🔹 1. Improved Notes: System Internals

**The Linux Kernel & The Shell**

The Kernel is the bridge between software and hardware. It manages CPU scheduling, memory allocation, and device I/O.

* System Calls (Syscalls): This is how an application asks the Kernel to do something (e.g., `open()`, `read()`, `write()`, `fork()`). If an app is slow, an SRE looks at syscall latency.
* Virtual File System (VFS): Linux treats everything as a file (Hardware, Sockets, Processes). These are represented in `/proc` (process info) and `/sys` (kernel/hardware info).

**Process Management: Life & Death**

* Parent/Child Relationship: Every process (except `PID 1`) is created by a parent using `fork()`.
* Zombie Processes: A process that has finished (sent `SIGCHLD`) but its parent hasn't acknowledged it. They take up space in the Process Table.
* Orphan Processes: A process whose parent died. `systemd` (PID 1) "adopts" these and reaps them.

**Memory & The OOM Killer**

When the system runs out of physical RAM and Swap, the Out of Memory (OOM) Killer is triggered. It uses a scoring system (`oom_score`) to decide which process to kill to save the OS.

***

#### 🔹 2. Interview View (Q\&A)

Q1: What exactly is "Load Average" in the `top` command?

* Answer: It is the average number of processes in a "runnable" or "uninterruptible" state.
  * Runnable: Waiting for CPU.
  * Uninterruptible: Waiting for I/O (Disk or Network).
* Senior Twist: If Load Average is high but CPU usage is low, the system is bottlenecked on Disk I/O.

Q2: You have deleted a large log file, but `df -h` shows the disk is still full. Why?

* Answer: A process still has an open File Descriptor to that file. Linux won't actually free the blocks on the disk until the process closes the file or the process is killed.
* Follow-up: "How do you find which process is holding it?" -> Use `lsof | grep deleted`.

Q3: Explain the difference between `soft link` and `hard link`.

* Answer: A Hard Link is a direct pointer to the Inode (the actual data on disk). If you delete the original file, the hard link still works. A Soft Link (Symbolic) is a pointer to the _filename_. If the original file is moved or deleted, the link breaks.

***

#### 🔹 3. Architecture & Design: The Boot Process

Understanding how a server comes to life is vital for debugging "unreachable" nodes.

1. BIOS/UEFI: Hardware initialization.
2. GRUB: The bootloader that loads the Kernel into memory.
3. Kernel: Initializes drivers and mounts the root filesystem.
4. Systemd (PID 1): The mother of all processes. It starts services (Targets) in parallel, significantly faster than the old SysVinit.

***

#### 🔹 4. Commands & Configs (The "SRE Power Tools")

**Advanced Debugging**

Bash

```
# See every system call a process makes (Great for "Permission Denied" mysteries)
strace -p <pid>

# Trace network packets at the kernel level
tcpdump -i eth0

# Check Inode usage (sometimes disk is "full" because you ran out of Inodes, not space)
df -i
```

**System Limits (`/etc/security/limits.conf`)**

For high-traffic apps (databases/proxies), you must increase the number of allowed open files.

Plaintext

```
* soft nofile 65535
* hard nofile 65535
```

***

#### 🔹 5. Troubleshooting & Debugging

Scenario: A server is "sluggish" and unresponsive to SSH.

1. Isolate the resource: Use `top` or `htop`. Look for %wa (I/O Wait). If high, the disk is the bottleneck.
2. Check Memory: Use `free -m`. Is Swap being used? If the system is "thrashing" (constantly moving data between RAM and Swap), performance will tank.
3. Check Dmesg: Run `dmesg -T | tail -n 50`. Look for "Out of memory", "TCP segments dropped", or "Hardware Error".
4. Check Zombie PIDs: Use `ps aux | grep 'Z'`. A massive amount of zombies indicates a buggy application failing to close child processes.

***

#### 🔹 6. Production Best Practices

* No SSH in Production: Use Configuration Management (Ansible) or Systems Manager (AWS SSM). Manual changes are "Snowflake Servers."
* Log Rotation: Always configure `logrotate`. A common "SRE 1:00 AM incident" is a disk filling up because an app was logging in `DEBUG` mode.
* Kernel Hardening: Disable unused services and use SELinux or AppArmor to restrict what processes can do, even if they are breached.
* Anti-Pattern: Running a process as `root`. If the app is compromised, the attacker has full control of the OS. Always use a dedicated service user.

***

#### 🔹 Cheat Sheet / Quick Revision

| **Command**           | **Purpose**      | **SRE Context**                             |
| --------------------- | ---------------- | ------------------------------------------- |
| `top` / `htop`        | Process monitor  | Check CPU/Load/Memory.                      |
| `iostat`              | Disk I/O stats   | Identify disk bottlenecks.                  |
| `netstat` / `ss`      | Network stats    | Check for socket exhaustion.                |
| `journalctl -u <svc>` | View Logs        | Standard way to debug `systemd` services.   |
| `lsof`                | List open files  | Find which process is using a port or file. |
| `nice` / `renice`     | Process priority | Give critical processes more CPU priority.  |

***

This is Section 5: Linux Operating System. For a senior-level role, Linux knowledge isn't about knowing how to list files; it's about understanding how the OS handles resource contention, kernel-level operations, and system performance.

***

#### 🟢 Easy: Basic Operations & File Systems

_Focus: Day-to-day command usage and basic permissions._

1. What is the difference between `chmod` and `chown`?
   * _Context:_ Focus on "Permissions" vs. "Ownership."
2. How do you find which process is using a specific port (e.g., port 8080)?
   * _Context:_ The interviewer is looking for `netstat -tulpn` or `ss -tulpn`.
3. What is the purpose of the `/etc/hosts` file?
   * _Context:_ Local DNS resolution before hitting external DNS servers.
4. Explain the basic Linux file permissions (rwx) and what the numbers 755 or 644 mean.
   * _Context:_ Understanding User, Group, and Others bitmasks.

***

#### 🟡 Medium: System Internals & Process Management

_Focus: How the OS manages tasks and resources._

1. Explain the three numbers in the "Load Average" output of the `uptime` command.
   * _Context:_ They represent the 1, 5, and 15-minute averages. Mention that this includes processes waiting for CPU _and_ processes in uninterruptible sleep (I/O wait).
2. What is a "Zombie" process and how do you "kill" it?
   * _Context:_ A zombie is already dead; you can't kill it. You must kill the parent process so the zombie is "reaped" by `init` (PID 1).
3. What is an Inode? What happens if a system runs out of Inodes but still has disk space?
   * _Context:_ An Inode stores metadata about a file. If you run out, you cannot create new files, even if you have 100GB of space left. This happens with many small files (e.g., session files or tiny logs).
4. Describe the difference between a Hard Link and a Soft (Symbolic) Link.
   * _Context:_ A Hard link points to the Inode; a Soft link points to the file path.

***

#### 🔴 Hard: SRE-Level Debugging & Kernel Concepts

_Focus: High-pressure troubleshooting and kernel-space behavior._

1. Scenario: You deleted a 10GB log file to free up space, but `df -h` still shows the disk is 100% full. Why, and how do you fix it without a reboot?
   * _Context:_ A process still has an open File Descriptor to that file. The space isn't freed until the process closes the file. Use `lsof | grep deleted` to find the PID and restart that service.
2. What is the OOM (Out of Memory) Killer? How does it decide which process to kill first?
   * _Context:_ Mention the `oom_score`. Factors include memory usage, process age, and `oom_score_adj`. SREs often protect critical processes (like `sshd` or `databases`) by lowering their score.
3. How would you use `strace` to debug a running application that is hanging or "stuck"?
   * _Context:_ `strace` intercepts System Calls. You can see if the app is stuck on a `read()` (waiting for network) or an `open()` (waiting for a file lock).
4. Explain the difference between User Space and Kernel Space.
   * _Context:_ Focus on security and stability. Applications run in User Space and must use Syscalls to request the Kernel to perform hardware tasks (Disk, Network, RAM).

***

***

#### 💡 Pro-Tip for your Interview

When answering Linux questions, mention "Everything is a file."

* The SRE Answer: "In Linux, everything is a file—from the hardware and network sockets to the processes listed in `/proc`. If I see a 'Too many open files' error, I know I'm hitting the `ulimit` or the kernel-wide file descriptor limit, which I can tune in `sysctl.conf`."

***

## System Design Perspective

**Scalability**
- Linux kernel defaults are tuned for general-purpose workloads, not high-scale production. `net.core.somaxconn`, `fs.file-max`, and `ulimit -n` must be raised before a proxy or database hits thousands of concurrent connections.
- The kernel scheduler (CFS) distributes CPU fairly across all processes. For latency-sensitive workloads, CPU pinning (`taskset`) and isolated cores (`isolcpus`) remove scheduler interference.

**Failure Modes**
- **Disk full (inode exhaustion):** Disk space is free but `touch` fails — you've run out of inodes. Common with millions of tiny cache/session files. Fix: `df -i`, then find and delete offending directories.
- **Deleted-file ghost space:** A process holds an open file descriptor to a deleted file. `df` still shows it used. Fix: `lsof +L1`, then restart the holding process.
- **OOM cascade:** OOM Killer terminates the highest-score process, which may be the wrong one. Protect critical services with `oom_score_adj=-1000`.
- **D-state deadlock:** A process in uninterruptible sleep (waiting on NFS or failing disk) cannot be killed even with `kill -9`. Fix requires resolving the underlying I/O, not the process.
- **Load average vs CPU:** High load + low CPU = I/O bottleneck, not CPU. Treating them as equivalent is a common diagnosis mistake.

**Trade-offs**
- **Swap:** Having swap prevents OOM kills but causes thrashing if heavily used. Databases should set `vm.swappiness=1–10` to keep data in RAM; the trade-off is faster OOM kill over slow thrash.
- **systemd vs SysVinit:** systemd parallelizes boot and provides cgroup-based resource tracking. The trade-off: more complexity, harder to debug, but dramatically faster startup and better dependency management.
- **Permissions granularity:** POSIX permissions (rwx owner/group/other) are simple but coarse. ACLs add per-user/group entries at the cost of complexity. SELinux/AppArmor add mandatory access control — much more secure but operationally harder.
- **Huge Pages:** Reduce TLB misses for large databases (PostgreSQL, Oracle) by using 2MB pages. Trade-off: pre-allocated huge pages cannot be used for other workloads; THP (Transparent Huge Pages) automates this but introduces latency spikes — disable for Redis and MongoDB.

**Why These Design Choices Were Made**
- The **single-rooted filesystem** (`/`) was designed for simplicity: one namespace, predictable paths, trivial to mount network filesystems at any subtree.
- **"Everything is a file"** was a deliberate Unix design decision so the same `read()`/`write()` interface works for disks, sockets, processes (`/proc`), and devices — reducing API surface area dramatically.
- **Copy-on-Write for fork()** solves the problem that most forks are immediately followed by `exec()` — copying all pages would be wasteful. COW defers the cost to the first write.
- **PID 1 adopts orphans** prevents zombie accumulation when parent processes die unexpectedly — a safety net for process table cleanliness.
