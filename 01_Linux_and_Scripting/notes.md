# Linux Notes for DevOps Engineers

## History of Linux

Linux emerged from the Unix family as a free, open-source operating system. Linus Torvalds, a student at the University of Helsinki, released Linux 0.01 on September 17, 1991 via the Minix newsgroup. Version 0.02 followed on October 5, 1991. Today Linux powers over 90% of the world's top 500 supercomputers, the majority of cloud infrastructure, and nearly all containers.

Linux is licensed under the GPL v2, meaning modifications must be shared under the same terms. Major distributions (distros) package the kernel with userspace tools: Debian/Ubuntu (APT), RHEL/Fedora/Rocky (DNF/RPM), Arch (Pacman), SUSE (Zypper).

---

## The Linux Kernel

The kernel is the core program that manages hardware resources and provides services to user-space processes. It handles:

- **Process scheduling** — CFS (Completely Fair Scheduler) assigns CPU time slices
- **Memory management** — virtual memory, paging, swapping, OOM killer
- **Device drivers** — interfaces between hardware and software
- **System calls** — the API boundary between user space and kernel space (e.g., `open`, `read`, `write`, `fork`, `exec`)
- **Networking stack** — TCP/IP implementation, socket management
- **VFS (Virtual Filesystem Switch)** — abstraction layer allowing multiple filesystem types

Kernel versions follow `major.minor.patch` numbering. Check with:

```bash
uname -r          # e.g., 6.1.0-21-amd64
uname -a          # full system info
cat /proc/version # kernel build info
```

---

## Filesystem Hierarchy Standard (FHS)

Linux uses a single-rooted, inverted tree structure. Everything is a file — including hardware devices.

| Directory | Purpose |
|-----------|---------|
| `/` | Root — top of the entire hierarchy |
| `/bin` | Essential user binaries (`ls`, `cp`, `mv`) |
| `/sbin` | System administration binaries (`iptables`, `fdisk`, `ifconfig`) |
| `/etc` | System-wide configuration files |
| `/var` | Variable data: logs (`/var/log`), spool, databases (`/var/lib`), mail |
| `/tmp` | Temporary files — cleared on reboot |
| `/home` | User home directories (`/home/username`) |
| `/root` | Home directory for the root superuser |
| `/usr` | User applications and libraries (`/usr/bin`, `/usr/lib`) |
| `/opt` | Third-party optional software |
| `/dev` | Device files (`/dev/sda`, `/dev/tty1`, `/dev/null`) |
| `/proc` | Virtual filesystem exposing kernel and process info |
| `/sys` | Virtual filesystem for kernel subsystem info |
| `/boot` | Bootloader files and kernel images (GRUB) |
| `/mnt` | Temporary mount point for filesystems |
| `/media` | Auto-mounted removable media |
| `/lib` | Shared libraries needed by `/bin` and `/sbin` |
| `/run` | Runtime data (PID files, sockets) — cleared at boot |

Key paths to memorize:
- `/etc/passwd` — user account database
- `/etc/shadow` — hashed passwords
- `/etc/group` — group definitions
- `/etc/fstab` — filesystem mount table
- `/etc/hosts` — static hostname resolution
- `/etc/sudoers` — sudo privilege configuration
- `/proc/cpuinfo` — CPU details
- `/proc/meminfo` — memory stats

---

## Process Management

Every running program is a process identified by a PID (Process ID). The first process is `init` or `systemd` (PID 1), which is the ancestor of all other processes.

### Process States

| State | Symbol | Meaning |
|-------|--------|---------|
| Running | R | Actively using CPU or in run queue |
| Sleeping (interruptible) | S | Waiting for event (I/O, signal) |
| Sleeping (uninterruptible) | D | Waiting on kernel I/O — cannot be killed |
| Zombie | Z | Finished but parent hasn't called `wait()` |
| Stopped | T | Paused by signal (SIGSTOP, SIGTSTP) |

### Viewing Processes

```bash
ps aux                        # all processes, BSD format
ps -ef                        # all processes, full format
ps -eo pid,ppid,user,cmd      # custom columns
top                           # interactive sorted view
htop                          # color-enhanced interactive view (install separately)
pgrep nginx                   # find PIDs by name
```

### Foreground and Background

```bash
command &          # start in background
Ctrl+Z             # suspend foreground process
bg                 # resume suspended job in background
fg                 # bring background job to foreground
jobs               # list background/stopped jobs
nohup command &    # run immune to hangup signals
disown -h %1       # detach job from shell after the fact
```

---

## Signals

Signals are software interrupts sent to processes. Key signals:

| Signal | Number | Default Action | Description |
|--------|--------|---------------|-------------|
| SIGHUP | 1 | Terminate | Hangup — reload config for daemons |
| SIGINT | 2 | Terminate | Interrupt (Ctrl+C) |
| SIGQUIT | 3 | Core dump | Quit |
| SIGKILL | 9 | Terminate | Force kill — cannot be caught or ignored |
| SIGTERM | 15 | Terminate | Graceful termination request (default for `kill`) |
| SIGSTOP | 19 | Stop | Pause process — cannot be caught or ignored |
| SIGCONT | 18 | Continue | Resume stopped process |
| SIGUSR1 | 10 | Terminate | User-defined signal 1 |
| SIGUSR2 | 12 | Terminate | User-defined signal 2 |

```bash
kill -15 <PID>      # graceful stop
kill -9 <PID>       # force kill
kill -1 <PID>       # reload (e.g., nginx -s reload equivalent)
killall nginx       # kill all processes named nginx
pkill -f pattern    # kill by command pattern match
```

---

## Users and Permissions

### User Account Files

- `/etc/passwd` — `username:x:UID:GID:comment:home:shell`
- `/etc/shadow` — hashed password and aging policy
- `/etc/group` — `groupname:x:GID:members`

### User Management Commands

```bash
useradd -m -s /bin/bash alice    # create user with home dir
passwd alice                      # set password
usermod -aG wheel alice           # add to group
userdel -r alice                  # delete user and home dir
id alice                          # show UID/GID/groups
who                               # who is logged in
w                                 # logged-in users + activity
last                              # login history
```

### File Permission Model

Every file has three permission sets for three categories:

```
-rwxr-xr--  1 alice devops 4096 Apr 24 10:00 script.sh
 |||||||||||
 |||||||||└─ others: r--  = 4
 ||||||└────  group:  r-x  = 5
 |||└───────  owner:  rwx  = 7
 |└─────────  type:   - (regular file), d (dir), l (symlink)
```

Octal permission values: read=4, write=2, execute=1

```bash
chmod 755 script.sh           # owner rwx, group rx, others rx
chmod u+x,g-w file            # symbolic mode
chown alice:devops file       # change owner and group
chgrp devops file             # change group only
```

### Special Permissions

| Bit | Octal | Effect on Files | Effect on Directories |
|-----|-------|----------------|----------------------|
| SUID | 4000 | Execute as file owner | No effect |
| SGID | 2000 | Execute as file group | New files inherit group |
| Sticky | 1000 | No effect | Only owner can delete their files |

```bash
chmod 4755 /usr/bin/passwd    # SUID
chmod 2755 /shared/dir        # SGID
chmod 1777 /tmp               # sticky bit
find / -perm -4000 2>/dev/null  # find SUID files
```

### Access Control Lists (ACL)

ACLs provide per-user/per-group permissions beyond the basic owner/group/other model.

```bash
getfacl file                       # view ACL
setfacl -m u:bob:rw file           # grant bob read+write
setfacl -m g:devops:rx dir         # grant group read+execute
setfacl -x u:bob file              # remove bob's ACL entry
setfacl -b file                    # remove all ACLs
setfacl -d -m g:devops:rx dir      # default ACL (inherited by new files)
```

---

## Sudo

`sudo` allows permitted users to run commands as another user (typically root), per `/etc/sudoers`.

```bash
visudo                              # safely edit /etc/sudoers
# User privilege specification:
alice ALL=(ALL:ALL) ALL             # alice can run anything as anyone
bob ALL=(ALL) NOPASSWD: /bin/systemctl restart nginx   # passwordless specific cmd
%wheel ALL=(ALL) ALL                # all members of wheel group
```

Add users to wheel group (RHEL) or sudo group (Debian) for standard admin access:

```bash
usermod -aG wheel alice    # RHEL/CentOS
usermod -aG sudo alice     # Debian/Ubuntu
```

---

## systemd

`systemd` is the init system and service manager (PID 1) on most modern Linux distributions. It manages units: services, sockets, timers, mounts, targets.

### Service Management

```bash
systemctl start nginx
systemctl stop nginx
systemctl restart nginx
systemctl reload nginx          # reload config without restart
systemctl status nginx
systemctl enable nginx          # start at boot
systemctl disable nginx
systemctl is-active nginx
systemctl is-enabled nginx
systemctl list-units --type=service --state=failed
```

### Unit File Structure

Unit files live in `/etc/systemd/system/` (admin) or `/lib/systemd/system/` (packages).

```ini
[Unit]
Description=My Application
After=network.target

[Service]
Type=simple
User=appuser
WorkingDirectory=/opt/myapp
ExecStart=/opt/myapp/bin/server
Restart=on-failure
RestartSec=5s
ProtectSystem=strict
PrivateTmp=true
WatchdogSec=30s
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload            # reload after editing unit files
journalctl -u nginx                # view service logs
journalctl -u nginx -f             # follow logs
journalctl -u nginx --since today
journalctl -p err..emerg           # filter by priority
```

### Targets (Runlevels)

| Target | Equivalent Runlevel |
|--------|-------------------|
| poweroff.target | 0 |
| rescue.target | 1 |
| multi-user.target | 3 |
| graphical.target | 5 |
| reboot.target | 6 |

```bash
systemctl get-default
systemctl set-default multi-user.target
systemctl isolate rescue.target
```

---

## Package Managers

### Debian/Ubuntu (APT)

```bash
apt update                        # refresh package index
apt upgrade                       # upgrade installed packages
apt install nginx                 # install package
apt remove nginx                  # remove package (keep config)
apt purge nginx                   # remove package and config
apt autoremove                    # remove unused dependencies
apt search nginx                  # search packages
apt show nginx                    # show package details
dpkg -l                           # list installed packages
dpkg -i package.deb               # install local .deb file
```

### RHEL/CentOS/Rocky/Fedora (DNF/YUM)

```bash
dnf check-update
dnf upgrade
dnf install nginx
dnf remove nginx
dnf search nginx
dnf info nginx
dnf history                       # transaction history
rpm -qa                           # list all installed RPMs
rpm -qi nginx                     # package info
dnf install package.rpm           # install local RPM
```

---

## SSH Hardening

SSH is the primary remote access method. Default config: `/etc/ssh/sshd_config`.

### Key Hardening Settings

```bash
# /etc/ssh/sshd_config
Port 2222                          # non-default port
Protocol 2                         # force SSH protocol version 2
PermitRootLogin no                 # never allow root login
PasswordAuthentication no          # key-based auth only
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
AllowUsers alice bob               # whitelist specific users
MaxAuthTries 3                     # limit auth attempts
LoginGraceTime 30                  # seconds to authenticate
ClientAliveInterval 300
ClientAliveCountMax 2
X11Forwarding no
AllowTcpForwarding no              # disable if not needed
Banner /etc/issue.net              # display warning banner
```

```bash
systemctl reload sshd              # apply changes
sshd -t                            # test config syntax
```

### Key-Based Authentication Setup

```bash
ssh-keygen -t ed25519 -C "user@host"        # generate key pair
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@host  # deploy public key
# Or manually:
cat ~/.ssh/id_ed25519.pub >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

### SSH Agent and Jump Hosts

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
ssh -J bastion.example.com internal-host    # jump through bastion
# ~/.ssh/config for persistent config:
Host internal
    HostName 10.0.1.50
    User alice
    ProxyJump bastion.example.com
    IdentityFile ~/.ssh/id_ed25519
```

---

## Cron and Job Scheduling

`cron` runs commands on a schedule. Each user has a crontab; system crontabs are in `/etc/cron.d/`.

### Crontab Syntax

```
# MIN HOUR DOM MON DOW COMMAND
  *   *    *   *   *   /path/to/command
  
# Examples:
0 2 * * * /usr/local/bin/backup.sh          # daily at 2 AM
*/5 * * * * /usr/local/bin/healthcheck.sh   # every 5 minutes
0 0 * * 0 /usr/local/bin/weekly.sh          # every Sunday midnight
0 9 1 * * /usr/local/bin/monthly.sh         # 1st of month at 9 AM
```

```bash
crontab -e           # edit current user's crontab
crontab -l           # list crontab
crontab -r           # remove crontab
crontab -u alice -l  # list another user's crontab (root)
```

System cron locations: `/etc/cron.hourly/`, `/etc/cron.daily/`, `/etc/cron.weekly/`, `/etc/cron.monthly/`

### systemd Timers (modern alternative)

```ini
# /etc/systemd/system/backup.timer
[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
```

```bash
systemctl list-timers --all
```
