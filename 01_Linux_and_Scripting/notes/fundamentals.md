# Linux Fundamentals

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
