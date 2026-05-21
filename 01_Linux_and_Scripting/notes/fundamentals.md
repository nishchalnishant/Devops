# Linux Fundamentals

```
Linux Fundamentals
├── History & Overview
│   ├── Unix family descendant — free, open-source
│   ├── Linus Torvalds, 1991, University of Helsinki
│   ├── Linux 0.01 posted Sept 17, 1991 on Minix newsgroup
│   └── Today: 90% of top 500 supercomputers run Linux
├── Filesystem Hierarchy (FHS)
│   ├── Single-rooted, inverted tree — root = /
│   ├── /: root of all directories
│   ├── /bin, /sbin: user and system binaries (ls, cp, iptables, reboot)
│   ├── /dev: device files (hardware as files)
│   ├── /etc: all configuration files (nerve center)
│   ├── /home: user home directories
│   ├── /var: variable data (logs, databases, emails)
│   ├── /var/log: application and OS log files
│   ├── /tmp: cleared on reboot (session temp files)
│   ├── /var/tmp: persists across reboots
│   ├── /proc: virtual FS — kernel/process runtime state
│   ├── /sys: virtual FS — hardware/driver model attributes
│   ├── /usr: user programs and shared data
│   ├── /boot: kernel images, initrd, GRUB config
│   ├── /opt: optional third-party software
│   └── /mnt, /media: temporary and auto-mounted filesystems
├── Key Config Files
│   ├── /etc/passwd: user account database (world-readable)
│   ├── /etc/shadow: hashed passwords (root only, 600)
│   ├── /etc/group: group definitions
│   ├── /etc/sudoers: sudo privilege specification
│   ├── /etc/ssh/sshd_config: SSH server configuration
│   ├── /etc/fstab: filesystem mount table (persistent)
│   ├── /etc/hosts: static hostname-to-IP resolution
│   └── /etc/resolv.conf: DNS resolver configuration
├── Kernel Architecture
│   ├── Kernel Space (Ring 0): full hardware access
│   ├── User Space (Ring 3): restricted, cannot directly access hardware
│   ├── System call crossing: expensive — saves registers, validates args
│   └── Syscall minimization techniques
│       ├── io_uring: ring buffer, no per-op syscall
│       ├── vDSO: kernel code mapped into user space (gettimeofday)
│       └── mmap: file/device mapped into user address space
├── Key System Calls
│   ├── fork(): COW clone child process
│   ├── exec(): replace process image with new program
│   ├── open() / read() / write(): file descriptor I/O
│   ├── mmap() / munmap(): map memory regions
│   ├── clone(): create threads / lightweight processes (containers)
│   ├── wait() / waitpid(): reap zombies, retrieve exit status
│   ├── epoll_wait(): efficient I/O event multiplexing
│   └── sendfile(): zero-copy file-to-socket transfer
├── Virtual Filesystem (VFS)
│   ├── Unified interface regardless of filesystem type
│   ├── proc: /proc — process and kernel runtime state
│   ├── sysfs: /sys — device and driver attributes
│   ├── tmpfs: /tmp, /dev/shm — RAM-backed ephemeral storage
│   ├── cgroupfs: /sys/fs/cgroup — control group hierarchy
│   ├── devtmpfs: /dev — device nodes managed by kernel
│   └── securityfs: /sys/kernel/security — LSM policy files
├── Process Management
│   ├── States: R (running), S (interruptible sleep), D (uninterruptible), Z (zombie), T (stopped)
│   ├── Creation: fork() (COW) → exec() (image replace) → wait() (reap)
│   ├── D state: cannot be killed, waiting on kernel I/O, indicates I/O subsystem issue
│   └── Signals: SIGTERM (15, graceful), SIGKILL (9, force), SIGHUP (1, reload)
├── User & Group Management
│   ├── /etc/passwd format: username:x:UID:GID:GECOS:home:shell
│   ├── UID: 0=root, 1-999=system, 1000+=regular users
│   ├── useradd, usermod -aG, userdel, passwd, chfn
│   └── sudo: visudo, NOPASSWD entries, per-command grants
├── File Permissions
│   ├── Types: read (r=4), write (w=2), execute (x=1)
│   ├── Tiers: owner / group / others
│   ├── Notation: -rwxr-xr-- = 754
│   ├── chmod: numeric (755) and symbolic (u+x, g-w, o=r)
│   ├── chown / chgrp: change ownership
│   └── Special permissions
│       ├── SetUID (s on owner): runs as file owner (e.g., /usr/bin/passwd)
│       ├── SetGID (s on group): files inherit group; dirs too
│       └── Sticky bit (t): only owner can delete files (e.g., /tmp)
├── Disk & Storage Management
│   ├── df -h: disk space per filesystem; df -i: inode usage
│   ├── du -sh: directory size; du -ah: per-file
│   ├── lsblk: block device tree; fdisk/parted: partition management
│   ├── mount / umount; /etc/fstab for persistent mounts
│   └── fsck: filesystem check (must be unmounted)
└── Package Management
    ├── APT (Debian/Ubuntu): apt update, install, remove, purge, search, list
    └── DNF/YUM (RHEL/CentOS): dnf check-update, upgrade, install, remove
```

## First Principles

- Hardware exists but programs cannot safely talk to it directly — you need a **kernel** as a trusted intermediary. Without it, two programs could write to the same disk sector simultaneously and corrupt data.
- Multiple programs must run without seeing each other's data — the kernel creates a **virtual address space** per process. Each process believes it owns all of RAM; the kernel maps this illusion to real physical pages.
- Crossing from user space to kernel space (a **system call**) is intentionally expensive because it's a privilege elevation. The kernel must validate every argument before granting access to hardware. This cost is why techniques like `io_uring` exist — to batch many operations through a single crossing.
- Files are the universal abstraction because **"everything is a file"** means the same `read()`/`write()` interface works for disks, network sockets, hardware devices (`/dev`), and even kernel state (`/proc`). One API for everything reduces complexity dramatically.
- Permissions exist because **multi-user systems predate personal computers**. Unix was designed for university timesharing — professors and students sharing one expensive machine. The rwx owner/group/other model maps directly to "file creator / their department / everyone else."
- SetUID exists because some programs **need temporary root privilege** for a single operation (e.g., `passwd` must write to `/etc/shadow`). Rather than making users root, the program runs with the file owner's (root's) privileges for that one task, then drops them.

## Linux History and Overview

Linux came from a Unix family. It is a free and open-source operating system developed by Linus Torvalds in September 1991.

**Timeline:**
- **1991:** Linus Torvalds was a student at the University of Helsinki, Finland
- **September 17, 1991:** Posted Linux 0.01 on the Minix newsgroup
- **October 5, 1991:** Released first "official" version Linux 0.02
- **Today:** 90% of the top 500 fastest supercomputers run on Linux variants, including the top 10

## Linux File System Hierarchy

In Linux, everything is represented as a file (including hardware and programs). Files are stored in directories, and every directory contains a file with a tree structure — this is called the File System Hierarchy.

Linux uses a **single-rooted, inverted tree-like structure**. The **Root Directory** is represented by `/` (forward slash) and is the top-level directory in Linux.

### Key Directories

| Directory | Purpose | Examples |
|-----------|---------|----------|
| `/` | Root of the hierarchy — starting point of FSH | Base of all directories |
| `/root` | Home directory for the root user (superuser) | Admin files |
| `/bin` | User binaries — common Linux commands | `ls`, `cp`, `mv`, `bash` |
| `/sbin` | System binaries — system administrator commands | `iptables`, `reboot`, `fdisk`, `ifconfig`, `swapon` |
| `/dev` | Device files — hardware device files | `/dev/tty1`, `/dev/usbmon0`, USB devices |
| `/var` | Variable files — data that grows over time | Logs, databases, emails |
| `/var/log` | System log files | OS and application logs |
| `/var/lib` | Database and package files | Persistent application state |
| `/var/mail` | Emails | User mailboxes |
| `/var/tmp` | Temporary files needed for reboot | Persistent temp files |
| `/tmp` | Temporary files — cleared on reboot | Session temp files |
| `/etc` | Configuration files | System-wide settings |
| `/home` | User home directories | `/home/alice`, `/home/bob` |
| `/usr` | User programs and data | `/usr/bin`, `/usr/lib`, `/usr/share` |
| `/proc` | Process and kernel information (virtual) | `/proc/cpuinfo`, `/proc/meminfo` |
| `/sys` | System hardware information (virtual) | Device and driver info |
| `/boot` | Boot loader files | Kernel images, initrd |
| `/opt` | Optional third-party software | Commercial applications |
| `/mnt` | Temporary mount point | Manual mounts |
| `/media` | Auto-mounted removable media | USB drives, CDs |

### Important Configuration Files

```
/etc/passwd          — User account database
/etc/shadow          — Hashed passwords and aging policy
/etc/group           — Group definitions
/etc/sudoers         — Sudo privilege specification
/etc/ssh/sshd_config — SSH server configuration
/etc/fstab           — Filesystem mount table
/etc/hosts           — Static hostname-to-IP resolution
/etc/resolv.conf     — DNS resolver configuration
/etc/hostname        — System hostname
```

***

## Linux Kernel Architecture

The kernel is the privileged program that manages hardware resources and exports a stable API (system calls) to user-space processes.

### Kernel Space vs. User Space

The CPU operates in two privilege rings:
- **Ring 0 (Kernel Mode):** Full hardware access
- **Ring 3 (User Mode):** Restricted access, cannot directly access hardware or other processes' memory

Crossing the boundary (a **system call**) is expensive — it triggers a context switch, saves CPU registers, validates arguments, and runs kernel code.

### High-Performance Syscall Minimization

High-performance systems minimize syscall frequency through:

| Technique | Description |
|-----------|-------------|
| **io_uring** | Submit and reap I/O via shared ring buffers without per-operation syscalls |
| **vDSO** | Maps kernel code into user space (`gettimeofday()` executes without full syscall) |
| **mmap** | Maps files/devices into user address space for direct read/write |

### Key System Calls

| Syscall | Purpose |
|---------|---------|
| `fork()` | Create child process (copy-on-write clone) |
| `exec()` | Replace process image with new program |
| `open()` / `read()` / `write()` | File descriptor I/O |
| `mmap()` / `munmap()` | Map memory regions |
| `clone()` | Create threads or lightweight processes (containers use this) |
| `wait()` / `waitpid()` | Reap zombie child processes |
| `ioctl()` | Device-specific control |
| `epoll_wait()` | Efficient I/O event multiplexing |
| `sendfile()` | Zero-copy file-to-socket transfer |

***

## Virtual Filesystem (VFS)

VFS is the abstraction layer that presents a unified file interface regardless of the underlying filesystem type (ext4, xfs, tmpfs, procfs, sysfs).

### Important Virtual Filesystems

| Filesystem | Mount Point | Purpose |
|------------|-------------|---------|
| `proc` | `/proc` | Process and kernel runtime state |
| `sysfs` | `/sys` | Device and driver model attributes |
| `tmpfs` | `/tmp`, `/dev/shm` | RAM-backed ephemeral storage |
| `cgroupfs` | `/sys/fs/cgroup` | Control group hierarchy |
| `devtmpfs` | `/dev` | Device nodes managed by kernel |
| `securityfs` | `/sys/kernel/security` | LSM policy files |

***

## Process Management

### Process States

| State | Code | Description |
|-------|------|-------------|
| Running | R | Executing or ready to run |
| Interruptible Sleep | S | Waiting for event (I/O, signal) |
| Uninterruptible Sleep | D | Waiting for I/O — cannot be killed |
| Stopped | T | Stopped by signal (SIGSTOP, Ctrl+Z) |
| Zombie | Z | Terminated but not reaped by parent |

### Process Creation

```
fork() → Creates child process (COW - Copy on Write)
  │
  ├─ Child continues with return value 0
  └─ Parent receives child PID
  
exec() → Replaces process image with new program
  │
  └─ New program starts execution
  
wait() → Parent waits for child to terminate
  │
  └─ Reaps zombie, retrieves exit status
```

### Viewing Processes

```bash
ps aux                    # All processes
ps -ef                    # Full format listing
ps -eo pid,ppid,cmd,%mem,%cpu  # Custom columns
top                       # Interactive process viewer
htop                      # Enhanced top (if installed)
pgrep nginx               # Find PIDs by name
pstree                    # Process tree view
```

### Process Signals

| Signal | Number | Description |
|--------|--------|-------------|
| SIGINT | 2 | Interrupt from keyboard (Ctrl+C) |
| SIGQUIT | 3 | Quit from keyboard |
| SIGKILL | 9 | Kill signal (cannot be caught) |
| SIGTERM | 15 | Termination signal (default for `kill`) |
| SIGSTOP | 17,19,23 | Stop process |
| SIGCONT | 18,19,23 | Continue stopped process |
| SIGHUP | 1 | Hangup (reload config for daemons) |

```bash
kill -9 <PID>             # Force kill (SIGKILL)
kill -15 <PID>            # Graceful termination (SIGTERM)
kill -1 <PID>             # Reload config (SIGHUP)
killall nginx             # Kill by process name
pkill -f pattern          # Kill by pattern
```

***

## User and Group Management

### User Files

| File | Purpose | Permissions |
|------|---------|-------------|
| `/etc/passwd` | User account database | World-readable |
| `/etc/shadow` | Hashed passwords | Root only (600) |
| `/etc/group` | Group definitions | World-readable |
| `/etc/gshadow` | Group passwords | Root only |

### `/etc/passwd` Format

```
username:x:UID:GID:GECOS:home_directory:login_shell
```

- **x:** Password placeholder (actual hash in `/etc/shadow`)
- **UID:** User ID (0=root, 1-999=system, 1000+=regular users)
- **GID:** Primary group ID
- **GECOS:** Comment field (full name, phone, etc.)

### User Management Commands

```bash
useradd -m -s /bin/bash alice    # Create user with home dir
usermod -aG sudo alice           # Add user to sudo group
userdel -r alice                 # Delete user and home dir
passwd alice                     # Set/change password
chfn alice                       # Change GECOS info
```

### Group Management

```bash
groupadd developers              # Create group
groupmod -n devs developers      # Rename group
groupdel developers              # Delete group
gpasswd -a alice developers      # Add user to group
gpasswd -d alice developers      # Remove user from group
```

### Sudo Configuration

```bash
# Edit sudoers safely (syntax check)
visudo

# Grant user full sudo access
alice ALL=(ALL:ALL) ALL

# Grant group passwordless sudo for specific commands
%developers ALL=(ALL) NOPASSWD: /usr/bin/systemctl, /usr/bin/docker
```

***

## File Permissions

### Permission Types

| Type | Symbol | Octal | Description |
|------|--------|-------|-------------|
| Read | r | 4 | View file contents / list directory |
| Write | w | 2 | Modify file / create/delete in directory |
| Execute | x | 1 | Run as program / enter directory |

### Permission Notation

```
-rwxr-xr--  1 root root  4096 Jan 15 10:30 script.sh
│││││││││
││││││││└── Others: read (4)
│││││││└───── Others: no write
││││││└────── Others: no execute
│││││└──────── Group: read (4) + execute (1) = 5
││││└───────── Group: no write
│││└────────── Group: read (4) + execute (1) = 5
││└─────────── Owner: read (4) + write (2) + execute (1) = 7
│└──────────── File type (- = regular, d = directory, l = symlink)
└───────────── Special bits (s = setuid/setgid, t = sticky)
```

### Permission Commands

```bash
chmod 755 script.sh          # rwxr-xr-x
chmod +x script.sh           # Add execute for all
chmod u+w file.txt           # Add write for owner
chmod g-w file.txt           # Remove write for group
chmod o=r file.txt           # Set others to read-only

chown alice:developers file  # Change owner and group
chgrp developers file        # Change group only
```

### Special Permissions

| Permission | Symbol | Effect |
|------------|--------|--------|
| SetUID | s (owner) | Executable runs as file owner |
| SetGID | s (group) | Executable runs as group owner; new files inherit group |
| Sticky Bit | t | Only owner can delete files in directory |

```bash
chmod u+s /usr/bin/passwd    # SetUID (passwd runs as root)
chmod g+s /shared/dir        # SetGID (files inherit group)
chmod +t /tmp                # Sticky bit (prevent deletion)
```

***

## Disk and Storage Management

### Viewing Disk Usage

```bash
df -h                        # Disk space (human-readable)
df -i                        # Inode usage
du -sh /var/log              # Directory size
du -ah /var/log | sort -rh   # All files sorted by size
ncdu                         # Interactive disk usage analyzer
```

### Partition Management

```bash
lsblk                        # List block devices
fdisk -l                     # List partitions (MBR)
parted -l                    # List partitions (GPT)
blkid                        # Show UUID and filesystem type
```

### Mounting Filesystems

```bash
mount                        # Show mounted filesystems
mount /dev/sda1 /mnt/data    # Mount device
mount -a                     # Mount all from /etc/fstab
umount /mnt/data             # Unmount
```

### /etc/fstab Format

```
<device>  <mount_point>  <filesystem_type>  <options>  <dump>  <pass>
/dev/sda1  /             ext4               defaults     0      1
UUID=abc123 /data         xfs                defaults     0      2
```

***

## Package Management

### Debian/Ubuntu (APT)

```bash
apt update                   # Refresh package lists
apt upgrade                  # Upgrade installed packages
apt install nginx            # Install package
apt remove nginx             # Remove package (keep config)
apt purge nginx              # Remove package + config
apt search keyword           # Search packages
apt show nginx               # Show package details
apt list --installed         # List installed packages
```

### RHEL/CentOS (DNF/YUM)

```bash
dnf check-update             # Check available updates
dnf upgrade                  # Upgrade packages
dnf install nginx            # Install package
dnf remove nginx             # Remove package
dnf search keyword           # Search packages
dnf info nginx               # Show package details
```

***

## Key Takeaways

| Concept | Key Point |
|---------|-----------|
| Everything is a file | Hardware, processes, sockets all represented as files |
| Single-rooted hierarchy | All paths start from `/` |
| Kernel space vs user space | Separation via privilege rings (0 and 3) |
| Syscalls are expensive | Techniques like io_uring, vDSO minimize crossings |
| Process states | R (running), S (sleeping), D (uninterruptible), Z (zombie) |
| Permissions | rwx for owner/group/others (octal 421) |
| SetUID/SetGID | Run executable as owner/group |
| Sticky bit | Prevent deletion in shared directories |

## System Design Perspective

**Scalability**
- The `/proc` virtual filesystem is the kernel's self-reporting mechanism. Monitoring tools (Prometheus node-exporter, Datadog agent, `top`) all read `/proc` to get metrics — no separate instrumentation needed. This scales to thousands of nodes because it's in-kernel with zero added overhead.
- The single-rooted filesystem (`/`) enables any subtree to be a network mount (NFS, CIFS), RAM filesystem (tmpfs), or another disk. This is how container overlay filesystems work: each layer is stacked at mount time, transparent to the process.
- User IDs are integers, not strings. At scale, LDAP/Active Directory maps usernames to UIDs and distributes these mappings. The kernel only ever checks UID numbers — name resolution is a user-space concern.

**Failure Modes**
- **UID collision:** If two systems have different users with the same UID (e.g., UID 1001 is `alice` on one host and `bob` on another), NFS mounts will map files incorrectly. This is why centralized identity (LDAP, SSSD) matters in multi-server environments.
- **`/tmp` filling up:** `/tmp` is often on the root filesystem. If it fills, the entire root FS appears full — system calls start failing everywhere. Use `tmpfs` with size limits: `tmpfs /tmp tmpfs defaults,size=2G 0 0` in `/etc/fstab`.
- **`/etc/fstab` error on boot:** A typo in `/etc/fstab` (wrong UUID, missing device) causes boot to drop into emergency mode. Always test with `mount -a` before rebooting.
- **Fork bomb:** `:(){ :|:& };:` — a function that calls itself twice in the background, exponentially consuming process table slots. Prevented by `ulimit -u` (max user processes) in `/etc/security/limits.conf`.

**Trade-offs**
- **Separate partitions (`/var`, `/tmp`, `/home`):** Isolates filesystem failures — a full `/var/log` doesn't fill root. The trade-off is fixed partition sizes that need manual resizing (LVM solves this). In containers, separate partitions are replaced by volume mounts.
- **`/etc/shadow` existence:** Password hashes are separated from the world-readable `/etc/passwd` specifically because `/etc/passwd` must be readable by all processes (e.g., `ls -la` needs to resolve UIDs to names). If hashes lived in `/etc/passwd`, any local user could run offline dictionary attacks. `/etc/shadow` is the security separation point.
- **io_uring vs traditional syscalls:** io_uring's ring buffer approach eliminates per-operation kernel crossings, yielding huge throughput gains for I/O-intensive applications. The trade-off: more complex programming model and potential security surface (io_uring has had several CVEs). Many distros disable it for containers by default.

**Why These Design Choices Were Made**
- **The `/usr` and `/bin` split** (now merged on modern distros) historically separated tools needed for single-user rescue mode (`/bin`) from tools only needed after `/usr` was mounted from a network share. This solved a bootstrap problem in diskless workstations.
- **`clone()` for containers:** Docker doesn't use `fork()` — it uses `clone()` with flags for new namespaces (PID, mount, network, UTS, IPC). `clone()` was added specifically to support containers and lightweight process isolation without the overhead of a full VM.
- **`epoll` replaced `select`/`poll`** because `select` has O(n) complexity per wakeup — you must scan all fd's to find which one fired. `epoll` is O(1) — the kernel tells you exactly which fd is ready. This is why Nginx/Node.js can handle thousands of concurrent connections efficiently.
