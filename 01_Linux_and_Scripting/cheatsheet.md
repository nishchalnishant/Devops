# Linux Command Cheatsheet — Comprehensive Quick Reference

All commands, flags, one-liners, and quick-reference tables for DevOps/SRE engineers.

---

## File and Directory Operations

| Command | Description |
|---------|-------------|
| `ls` | List files in current directory |
| `ls -la` | Long format with hidden files |
| `ls -lt` | Sort by modification time (newest first) |
| `ls -lh` | Human-readable file sizes |
| `ls -lS` | Sort by size (largest first) |
| `ls -R` | Recursive listing |
| `ls -d */` | List only directories |
| `pwd` | Print working directory |
| `cd /path` | Change to absolute path |
| `cd ..` | Move up one directory |
| `cd -` | Return to previous directory |
| `cd ~` | Go to home directory |
| `mkdir dir` | Create directory |
| `mkdir -p a/b/c` | Create nested directories (no error if exists) |
| `touch file` | Create empty file or update timestamps |
| `cp src dst` | Copy file |
| `cp -r src/ dst/` | Copy directory recursively |
| `cp -p src dst` | Preserve permissions and timestamps |
| `cp -a src/ dst/` | Archive copy (recursive + preserve everything) |
| `mv src dst` | Move or rename |
| `rm file` | Delete file |
| `rm -rf dir/` | Force-delete directory recursively |
| `rmdir dir` | Remove empty directory only |
| `ln -s target link` | Create symbolic link |
| `ln target hardlink` | Create hard link |
| `stat file` | Detailed file metadata (inode, timestamps, links) |
| `file file` | Detect file type |
| `readlink -f symlink` | Resolve full path of symlink |
| `tree -L 2` | Directory tree, 2 levels deep |
| `du -sh /path` | Total size of path |
| `du -ah /path` | Size of each file and directory |
| `du -sh * \| sort -rh \| head` | Largest items in current dir |

---

## Find and Locate

| Command | Description |
|---------|-------------|
| `find /path -name "*.log"` | Find files by name pattern |
| `find / -name "*.sh" -type f` | Find only regular files |
| `find /home -type d -name "config"` | Find only directories |
| `find / -perm -4000` | Find SUID files |
| `find / -perm -2000` | Find SGID files |
| `find /home -size +100M` | Files larger than 100MB |
| `find . -mtime -7` | Files modified in last 7 days |
| `find . -mtime +30 -delete` | Delete files older than 30 days |
| `find . -newer reference_file` | Files newer than reference |
| `find . -user alice` | Files owned by alice |
| `find . -empty` | Empty files or directories |
| `find . -type f -exec chmod 644 {} \;` | Execute command on each result |
| `find . -type f -print0 \| xargs -0 grep "pattern"` | Safe grep across many files |
| `locate filename` | Fast name-based search (uses mlocate db) |
| `updatedb` | Update locate database |
| `which command` | Path of command in PATH |
| `whereis command` | Binary, source, and manual locations |
| `type command` | Shell built-in, alias, or file |

---

## Text Processing

| Command | Description |
|---------|-------------|
| `cat file` | Print file contents |
| `cat -n file` | With line numbers |
| `less file` | Paginate through file (q to quit) |
| `head -n 20 file` | First 20 lines |
| `tail -n 20 file` | Last 20 lines |
| `tail -f file` | Follow file in real-time |
| `tail -F file` | Follow file, handle rotation |
| `wc -l file` | Count lines |
| `wc -w file` | Count words |
| `wc -c file` | Count bytes |
| `sort file` | Sort alphabetically |
| `sort -n file` | Sort numerically |
| `sort -rn file` | Sort numerically, reversed |
| `sort -k2 file` | Sort by second field |
| `sort -t: -k3 -n /etc/passwd` | Sort passwd by UID |
| `uniq file` | Remove adjacent duplicates |
| `uniq -c file` | Count occurrences |
| `uniq -d file` | Show only duplicate lines |
| `cut -d: -f1 /etc/passwd` | Cut field 1, colon delimiter |
| `cut -c1-10 file` | Cut characters 1-10 |
| `tr 'a-z' 'A-Z'` | Translate characters |
| `tr -d '\r'` | Remove carriage returns |
| `tr -s ' '` | Squeeze repeated spaces |
| `paste file1 file2` | Merge files side by side |
| `join file1 file2` | Join files on common field |
| `tee file` | Write to stdout and file simultaneously |
| `tee -a file` | Append to file |
| `column -t file` | Align columns |
| `fold -w 80` | Wrap long lines |
| `rev` | Reverse each line |
| `strings binary` | Extract printable strings from binary |
| `xxd file` | Hex dump |

---

## grep, sed, awk

### grep

| Command | Description |
|---------|-------------|
| `grep pattern file` | Search for pattern |
| `grep -r pattern /dir` | Recursive search |
| `grep -i pattern file` | Case-insensitive |
| `grep -v pattern file` | Invert match (lines NOT matching) |
| `grep -l pattern /dir/*` | Only list matching filenames |
| `grep -L pattern /dir/*` | Files NOT containing pattern |
| `grep -n pattern file` | Show line numbers |
| `grep -c pattern file` | Count matching lines |
| `grep -w "word" file` | Whole-word match |
| `grep -A 3 pattern file` | 3 lines after match |
| `grep -B 3 pattern file` | 3 lines before match |
| `grep -C 3 pattern file` | 3 lines before and after |
| `grep -E 'pat1\|pat2' file` | Extended regex (ERE) |
| `grep -P '\d+' file` | Perl regex |
| `grep -o pattern file` | Print only matching part |
| `grep -q pattern file` | Quiet — exit code only |

### sed

| Command | Description |
|---------|-------------|
| `sed 's/old/new/' file` | Replace first occurrence per line |
| `sed 's/old/new/g' file` | Replace all occurrences |
| `sed -i 's/old/new/g' file` | In-place edit |
| `sed -i.bak 's/old/new/g' file` | In-place edit with backup |
| `sed -n '5,10p' file` | Print lines 5-10 |
| `sed '5,10d' file` | Delete lines 5-10 |
| `sed '/pattern/d' file` | Delete matching lines |
| `sed -n '/pattern/p' file` | Print only matching lines |
| `sed '1d' file` | Delete first line |
| `sed '$d' file` | Delete last line |
| `sed 's/^/PREFIX/' file` | Add prefix to each line |
| `sed 's/$/ SUFFIX/' file` | Add suffix to each line |
| `sed '/pattern/a New line after' file` | Append line after match |
| `sed '/pattern/i New line before' file` | Insert line before match |
| `sed -e 's/a/A/' -e 's/b/B/' file` | Multiple operations |

### awk

| Command | Description |
|---------|-------------|
| `awk '{print $1}' file` | Print first field (space delimited) |
| `awk -F: '{print $1}' /etc/passwd` | Custom field separator |
| `awk '{print NR, $0}' file` | Print line numbers |
| `awk 'NR==5' file` | Print line 5 |
| `awk 'NR>=5 && NR<=10' file` | Print lines 5-10 |
| `awk '/pattern/ {print}' file` | Print matching lines |
| `awk '{sum+=$1} END{print sum}' file` | Sum first column |
| `awk '{print $NF}' file` | Print last field |
| `awk 'length > 80' file` | Lines longer than 80 chars |
| `awk '!seen[$0]++' file` | Remove duplicate lines (unsorted) |
| `awk -F: '$3 >= 1000 {print $1}' /etc/passwd` | Regular users |
| `ps aux \| awk '$3 > 10 {print $0}'` | Processes using >10% CPU |
| `df -h \| awk 'NR>1 {print $5, $6}'` | Disk usage percentages |

---

## Process Management

| Command | Description |
|---------|-------------|
| `ps aux` | All processes, BSD format |
| `ps -ef` | All processes, UNIX format |
| `ps -eo pid,ppid,user,stat,cmd` | Custom column output |
| `ps aux --sort=-%cpu \| head` | Top CPU consuming processes |
| `ps aux --sort=-%mem \| head` | Top memory consuming processes |
| `ps -u alice` | All processes owned by alice |
| `pgrep nginx` | Find PID(s) by process name |
| `pgrep -a nginx` | Find PID(s) with full command |
| `pstree` | Process tree |
| `pstree -p` | Process tree with PIDs |
| `top` | Interactive process viewer |
| `htop` | Enhanced interactive viewer |
| `atop` | Detailed process and hardware viewer |
| `kill PID` | Send SIGTERM |
| `kill -9 PID` | Send SIGKILL (force) |
| `kill -1 PID` | Send SIGHUP (reload) |
| `kill -SIGSTOP PID` | Pause process |
| `kill -SIGCONT PID` | Resume process |
| `killall nginx` | Kill all processes named nginx |
| `pkill -f "pattern"` | Kill by full command pattern |
| `pkill -u alice` | Kill all processes of user alice |
| `nice -n 10 cmd` | Start with lower priority (nice 10) |
| `renice 10 -p PID` | Change priority of running process |
| `renice -n -5 -u alice` | Reprioritize all alice's processes |
| `nohup cmd &` | Run immune to hangup signals |
| `disown -h %1` | Detach job from shell |
| `jobs` | List background/stopped jobs |
| `fg %1` | Bring job 1 to foreground |
| `bg %1` | Resume job 1 in background |
| `wait` | Wait for all background jobs |

---

## System Monitoring

| Command | Description |
|---------|-------------|
| `top` | CPU, memory, processes overview |
| `top -b -n 1` | Batch mode, single snapshot |
| `htop` | Color-enhanced top |
| `uptime` | Load average and uptime |
| `vmstat 1 5` | VM stats, 1-second interval, 5 samples |
| `iostat -xz 1` | Disk I/O stats per device |
| `iotop` | Per-process disk I/O |
| `mpstat -P ALL 1` | Per-CPU statistics |
| `sar -u 1 10` | CPU utilization, 10 samples |
| `sar -r 1 10` | Memory utilization |
| `sar -n DEV 1` | Network interface stats |
| `sar -d 1` | Disk activity |
| `pidstat 1` | Per-process statistics |
| `dstat` | Combined system stats |
| `perf stat cmd` | Hardware counter stats |
| `perf top -p PID` | Live CPU profiling |
| `perf record -g -p PID` | Record call stacks |
| `strace -p PID` | Trace system calls of running process |
| `strace -e trace=file cmd` | Trace file-related syscalls |
| `ltrace cmd` | Trace library calls |
| `lsof` | List all open files |
| `lsof -p PID` | Files opened by PID |
| `lsof -i :80` | Process using port 80 |
| `lsof -u alice` | Files opened by alice |
| `lsof +D /path` | Files opened in directory |
| `lsof \| grep deleted` | Deleted files still open |
| `watch -n 2 df -h` | Update df every 2 seconds |

### top Interactive Keys

| Key | Action |
|-----|--------|
| `1` | Toggle per-CPU breakdown |
| `M` | Sort by memory |
| `P` | Sort by CPU |
| `T` | Sort by time |
| `k` | Kill a process |
| `r` | Renice a process |
| `u` | Filter by user |
| `q` | Quit |
| `H` | Toggle thread display |

---

## Memory

| Command | Description |
|---------|-------------|
| `free -h` | Memory usage in human-readable |
| `free -m` | Memory in megabytes |
| `cat /proc/meminfo` | Detailed kernel memory stats |
| `swapon -s` | Swap usage |
| `vmstat -s` | Memory statistics summary |
| `cat /proc/PID/status` | Process memory: VmRSS, VmSwap |
| `pmap PID` | Memory map of process |
| `pmap -x PID` | Extended memory map |
| `cat /proc/PID/smaps` | Detailed per-region memory map |
| `valgrind --leak-check=full cmd` | Memory leak detection |

---

## Disk and Filesystem

| Command | Description |
|---------|-------------|
| `df -h` | Disk space per filesystem |
| `df -i` | Inode usage |
| `df -Th` | With filesystem type |
| `du -sh /path` | Total size |
| `du -ah --max-depth=1 /path` | Size per subdirectory (one level) |
| `lsblk` | Block device tree |
| `lsblk -f` | With filesystem type and UUID |
| `fdisk -l` | Partition table |
| `gdisk /dev/sdb` | GPT partition editor |
| `parted -l` | List partitions |
| `blkid` | Block device UUIDs and types |
| `mount` | Show mounted filesystems |
| `mount /dev/sdb1 /mnt` | Mount device |
| `mount -o remount,rw /` | Remount root read-write |
| `umount /mnt` | Unmount |
| `cat /etc/fstab` | Persistent mount config |
| `fsck /dev/sdb1` | Check filesystem (must be unmounted) |
| `e2fsck -f /dev/sdb1` | Force ext4 check |
| `mkfs.ext4 /dev/sdb1` | Format as ext4 |
| `mkfs.xfs /dev/sdb1` | Format as XFS |
| `tune2fs -l /dev/sda1` | Show ext4 filesystem info |
| `xfs_info /dev/sda1` | Show XFS filesystem info |
| `badblocks -sv /dev/sda` | Scan for bad blocks |
| `hdparm -tT /dev/sda` | Disk read speed test |
| `iostat -xz 1` | Per-device I/O stats |
| `ioping /dev/sda` | I/O latency measurement |

### Archive and Compression

| Command | Description |
|---------|-------------|
| `tar -czf archive.tar.gz dir/` | Create gzip tarball |
| `tar -xzf archive.tar.gz` | Extract gzip tarball |
| `tar -xzf archive.tar.gz -C /dest/` | Extract to specific dir |
| `tar -cjf archive.tar.bz2 dir/` | Create bzip2 tarball |
| `tar -xjf archive.tar.bz2` | Extract bzip2 tarball |
| `tar -cJf archive.tar.xz dir/` | Create xz tarball |
| `tar -tf archive.tar.gz` | List contents without extracting |
| `tar -czf - dir/ \| ssh host "tar -xzf - -C /dest/"` | Stream tar over SSH |
| `gzip file` | Compress to file.gz |
| `gzip -d file.gz` | Decompress |
| `gzip -9 file` | Maximum compression |
| `gunzip file.gz` | Decompress (alias) |
| `zip -r archive.zip dir/` | Zip directory |
| `unzip archive.zip` | Unzip |
| `unzip -l archive.zip` | List zip contents |
| `zcat file.gz` | View gzipped file without extracting |
| `zgrep pattern file.gz` | Grep inside gzipped file |

---

## Network Commands

| Command | Description |
|---------|-------------|
| `ip a` | Show all interfaces and IPs |
| `ip r` | Routing table |
| `ip r add default via 10.0.0.1` | Add default route |
| `ip link set eth0 up` | Bring interface up |
| `ip link set eth0 down` | Bring interface down |
| `ip addr add 10.0.0.2/24 dev eth0` | Add IP to interface |
| `ip addr del 10.0.0.2/24 dev eth0` | Remove IP |
| `ip neigh` | ARP table |
| `ip -s link` | Interface statistics (TX/RX, errors) |
| `ifconfig` | Legacy interface info |
| `ss -tulnp` | TCP/UDP listening with PIDs |
| `ss -s` | Socket summary |
| `ss -tp state established` | Established TCP connections |
| `ss -o state time-wait` | TIME_WAIT sockets |
| `netstat -tulnp` | Legacy listening ports |
| `netstat -s` | Protocol statistics |
| `ping -c 4 host` | ICMP reachability |
| `ping -I eth0 host` | Ping via specific interface |
| `traceroute host` | Trace network path |
| `traceroute -T -p 80 host` | TCP traceroute on port 80 |
| `mtr host` | Combined ping+traceroute |
| `dig domain` | DNS lookup |
| `dig +short domain` | Short answer |
| `dig @8.8.8.8 domain` | Query specific DNS server |
| `dig -x 1.2.3.4` | Reverse DNS lookup |
| `dig +trace domain` | Full delegation trace |
| `nslookup domain` | DNS lookup (legacy) |
| `host domain` | Simple DNS lookup |
| `curl -I https://host` | HTTP headers only |
| `curl -v https://host` | Verbose (show TLS handshake) |
| `curl -o file https://url` | Download to file |
| `curl -L https://url` | Follow redirects |
| `curl -w "%{http_code}" -s -o /dev/null url` | Get HTTP status code |
| `curl -X POST -H "Content-Type: application/json" -d '{}' url` | POST JSON |
| `curl --resolve host:443:IP https://host` | Override DNS for testing |
| `wget -q https://url` | Download file |
| `nc -zv host 80` | Test TCP port connectivity |
| `nc -l 8080` | Listen on port (simple server) |
| `tcpdump -i eth0 port 80` | Capture HTTP traffic |
| `tcpdump -i eth0 -w capture.pcap` | Write to file |
| `tcpdump -r capture.pcap` | Read capture file |
| `tcpdump -i eth0 'host 10.0.0.5 and tcp'` | Filtered capture |
| `nmap -sV host` | Port scan with service detection |
| `nmap -sS -O host` | SYN scan + OS detection |
| `iptables -L -n -v --line-numbers` | List firewall rules |
| `iptables -A INPUT -p tcp --dport 22 -j ACCEPT` | Allow SSH |
| `iptables -D INPUT 3` | Delete rule by line number |
| `iptables-save > /etc/iptables/rules.v4` | Persist rules |
| `iptables-restore < /etc/iptables/rules.v4` | Restore rules |
| `ufw status` | UFW status |
| `ufw allow 22/tcp` | Allow SSH |
| `ufw deny 23` | Deny telnet |
| `ufw enable` | Enable firewall |
| `nmcli con show` | NetworkManager connections |
| `nmcli con up ens3` | Activate connection |
| `ethtool eth0` | NIC driver and hardware info |

### SSH and File Transfer

| Command | Description |
|---------|-------------|
| `ssh user@host` | Connect to host |
| `ssh -p 2222 user@host` | Custom port |
| `ssh -i ~/.ssh/key user@host` | Specific identity file |
| `ssh -J bastion user@internal` | Jump through bastion |
| `ssh -L 8080:localhost:80 user@host` | Local port forward |
| `ssh -R 9090:localhost:80 user@host` | Remote port forward |
| `ssh -N -f -L 5432:db:5432 user@host` | Background tunnel |
| `ssh-keygen -t ed25519 -C "user@host"` | Generate ED25519 keypair |
| `ssh-keygen -t rsa -b 4096` | Generate RSA keypair |
| `ssh-copy-id user@host` | Deploy public key |
| `ssh-add ~/.ssh/id_ed25519` | Add key to agent |
| `eval "$(ssh-agent -s)"` | Start SSH agent |
| `scp file user@host:/path/` | Copy to remote |
| `scp user@host:/path/file .` | Copy from remote |
| `scp -r dir/ user@host:/path/` | Recursive copy |
| `rsync -avz src/ user@host:/dst/` | Sync with compression |
| `rsync -avz --delete src/ dst/` | Mirror (delete extra at dest) |
| `rsync --dry-run -avz src/ dst/` | Preview without changes |
| `rsync -avz --exclude='*.log' src/ dst/` | Exclude pattern |
| `sftp user@host` | Interactive file transfer |

---

## User and Permission Management

| Command | Description |
|---------|-------------|
| `useradd -m alice` | Create user with home directory |
| `useradd -m -s /bin/bash -G wheel,docker alice` | With shell and groups |
| `useradd -r -s /sbin/nologin svcuser` | System account (no login) |
| `passwd alice` | Set password |
| `passwd -l alice` | Lock account (disable password) |
| `passwd -u alice` | Unlock account |
| `usermod -aG docker alice` | Add to group |
| `usermod -s /sbin/nologin alice` | Disable login shell |
| `usermod -L alice` | Lock account |
| `usermod -U alice` | Unlock account |
| `usermod -e 2025-12-31 alice` | Set account expiry |
| `userdel alice` | Delete user (keep home) |
| `userdel -r alice` | Delete user and home directory |
| `groupadd devops` | Create group |
| `groupdel devops` | Delete group |
| `gpasswd -a alice devops` | Add alice to devops |
| `gpasswd -d alice devops` | Remove alice from devops |
| `id alice` | Show UID, GID, groups |
| `groups alice` | Show group memberships |
| `who` | Currently logged-in users |
| `w` | Logged-in users and activity |
| `last` | Login history |
| `lastb` | Failed login attempts |
| `chage -l alice` | Password aging info |
| `chage -M 90 alice` | Set max password age (90 days) |
| `chage -E 2025-12-31 alice` | Set account expiry |

### Permissions

| Command | Description |
|---------|-------------|
| `chmod 755 file` | rwxr-xr-x |
| `chmod 644 file` | rw-r--r-- |
| `chmod 600 file` | rw------- (private) |
| `chmod 400 file` | r-------- (read-only) |
| `chmod +x script.sh` | Add execute for all |
| `chmod u+x,g-w,o= file` | Symbolic mode |
| `chmod -R 755 dir/` | Recursive |
| `chown alice file` | Change owner |
| `chown alice:devops file` | Change owner and group |
| `chgrp devops file` | Change group only |
| `chown -R alice:devops dir/` | Recursive |
| `chmod 4755 file` | SUID |
| `chmod 2755 dir/` | SGID |
| `chmod 1777 /tmp` | Sticky bit |
| `umask` | Show current umask |
| `umask 022` | Set umask (new files get 644) |

### Octal Permission Reference

| Octal | Symbolic | Description |
|-------|----------|-------------|
| 0 | `---` | No permissions |
| 1 | `--x` | Execute only |
| 2 | `-w-` | Write only |
| 3 | `-wx` | Write and execute |
| 4 | `r--` | Read only |
| 5 | `r-x` | Read and execute |
| 6 | `rw-` | Read and write |
| 7 | `rwx` | All permissions |

### Access Control Lists (ACL)

| Command | Description |
|---------|-------------|
| `getfacl file` | View ACL |
| `setfacl -m u:bob:rw file` | Grant bob read+write |
| `setfacl -m g:devops:rx dir` | Grant group read+execute |
| `setfacl -x u:bob file` | Remove bob's ACL entry |
| `setfacl -b file` | Remove all ACLs |
| `setfacl -d -m g:devops:rx dir` | Default ACL (inherited by new files) |
| `setfacl -R -m u:bob:rx dir/` | Recursive ACL |

---

## systemd

| Command | Description |
|---------|-------------|
| `systemctl start nginx` | Start service |
| `systemctl stop nginx` | Stop service |
| `systemctl restart nginx` | Restart service |
| `systemctl reload nginx` | Reload config (SIGHUP) |
| `systemctl status nginx` | Service status |
| `systemctl enable nginx` | Enable at boot |
| `systemctl disable nginx` | Disable at boot |
| `systemctl is-active nginx` | Check if active |
| `systemctl is-enabled nginx` | Check if enabled |
| `systemctl daemon-reload` | Reload unit files after edit |
| `systemctl list-units --type=service` | All services |
| `systemctl list-units --state=failed` | Failed units |
| `systemctl list-dependencies nginx` | Dependency tree |
| `systemctl mask nginx` | Prevent service from starting |
| `systemctl unmask nginx` | Remove mask |
| `systemctl isolate rescue.target` | Switch to rescue mode |
| `systemctl set-default multi-user.target` | Set default target |
| `systemctl get-default` | Show default target |
| `systemd-analyze` | Boot time summary |
| `systemd-analyze blame` | Per-unit boot time |
| `systemd-analyze critical-chain` | Critical path to default target |
| `journalctl -u nginx` | Service logs |
| `journalctl -u nginx -f` | Follow logs |
| `journalctl -u nginx --since "1 hour ago"` | Time filter |
| `journalctl -u nginx -n 50` | Last 50 lines |
| `journalctl -p err..emerg` | Filter by priority |
| `journalctl --since "2025-01-01"` | Date filter |
| `journalctl -b -1` | Logs from previous boot |
| `journalctl --disk-usage` | Journal storage size |
| `journalctl --vacuum-time=7d` | Delete old entries |

---

## Package Management

| Action | Debian/Ubuntu | RHEL/Rocky/Fedora | Arch |
|--------|--------------|-------------------|------|
| Update index | `apt update` | `dnf check-update` | `pacman -Sy` |
| Upgrade all | `apt upgrade` | `dnf upgrade` | `pacman -Syu` |
| Full upgrade | `apt full-upgrade` | `dnf distro-sync` | `pacman -Syu` |
| Install | `apt install pkg` | `dnf install pkg` | `pacman -S pkg` |
| Remove | `apt remove pkg` | `dnf remove pkg` | `pacman -R pkg` |
| Purge | `apt purge pkg` | `dnf erase pkg` | `pacman -Rns pkg` |
| Search | `apt search kw` | `dnf search kw` | `pacman -Ss kw` |
| Info | `apt show pkg` | `dnf info pkg` | `pacman -Si pkg` |
| List installed | `dpkg -l` | `rpm -qa` | `pacman -Q` |
| Which pkg owns file | `dpkg -S /path/file` | `rpm -qf /path/file` | `pacman -Qo /path/file` |
| List files in pkg | `dpkg -L pkg` | `rpm -ql pkg` | `pacman -Ql pkg` |
| Install local | `dpkg -i pkg.deb` | `dnf install pkg.rpm` | `pacman -U pkg.tar.zst` |
| Autoremove | `apt autoremove` | `dnf autoremove` | `pacman -Rns $(pacman -Qtdq)` |
| History | `apt history` | `dnf history` | n/a |
| Clean cache | `apt clean` | `dnf clean all` | `pacman -Sc` |

---

## Bash Scripting Quick Reference

### Variables

```bash
VAR="value"
echo "$VAR"                      # always quote variables
echo "${VAR}_suffix"             # brace to delimit variable name
echo "${VAR:-default}"           # use default if unset/empty
echo "${VAR:?Error message}"     # abort if unset/empty
echo "${VAR:+alternate}"         # use alternate if set
echo "${#VAR}"                   # string length
echo "${VAR^^}"                  # uppercase
echo "${VAR,,}"                  # lowercase
echo "${VAR/old/new}"            # replace first occurrence
echo "${VAR//old/new}"           # replace all occurrences
echo "${VAR#prefix}"             # strip shortest prefix match
echo "${VAR##prefix}"            # strip longest prefix match
echo "${VAR%suffix}"             # strip shortest suffix match
echo "${VAR%%suffix}"            # strip longest suffix match

ARRAY=(a b c d)
echo "${ARRAY[0]}"               # first element
echo "${ARRAY[@]}"               # all elements
echo "${#ARRAY[@]}"              # array length
echo "${ARRAY[@]:1:2}"           # slice: elements 1 and 2
```

### Conditionals and Tests

```bash
# File tests
[ -f file ]      # exists and is regular file
[ -d dir ]       # exists and is directory
[ -e path ]      # exists (any type)
[ -r file ]      # readable
[ -w file ]      # writable
[ -x file ]      # executable
[ -s file ]      # exists and not empty
[ -L link ]      # is a symbolic link
[ file1 -nt file2 ]  # file1 newer than file2

# String tests
[ -z "$VAR" ]    # empty string
[ -n "$VAR" ]    # non-empty string
[ "$a" = "$b" ]  # string equality
[ "$a" != "$b" ] # string inequality
[[ "$a" == pat* ]]   # glob match (double brackets only)
[[ "$a" =~ regex ]]  # regex match (double brackets only)

# Numeric comparisons
[ "$a" -eq "$b" ]    # equal
[ "$a" -ne "$b" ]    # not equal
[ "$a" -lt "$b" ]    # less than
[ "$a" -le "$b" ]    # less than or equal
[ "$a" -gt "$b" ]    # greater than
[ "$a" -ge "$b" ]    # greater than or equal
(( a > b ))          # arithmetic evaluation

# Compound tests
[ "$a" -gt 0 ] && [ "$a" -lt 10 ]  # AND
[[ "$a" -gt 0 && "$a" -lt 10 ]]    # AND (double brackets)
[ "$a" -gt 0 ] || [ "$b" -gt 0 ]   # OR
```

### Loops

```bash
# For over list
for item in a b c; do echo "$item"; done

# For over array
for item in "${ARRAY[@]}"; do echo "$item"; done

# For over files
for file in /etc/*.conf; do echo "$file"; done

# C-style for
for ((i=0; i<10; i++)); do echo "$i"; done

# While loop
while read -r line; do
    echo "$line"
done < file.txt

# While with condition
while [ "$COUNT" -lt 10 ]; do
    ((COUNT++))
done

# Until loop
until ping -c1 host &>/dev/null; do sleep 5; done
```

### Functions

```bash
my_func() {
    local arg1="$1"
    local arg2="${2:-default}"
    echo "Args: $arg1 $arg2"
    return 0
}

# Call and capture output
result=$(my_func "hello" "world")
echo "Exit: $?   Result: $result"
```

### Special Variables

| Variable | Meaning |
|----------|---------|
| `$0` | Script name |
| `$1`, `$2`, ... | Positional arguments |
| `$@` | All arguments (preserves quoting) |
| `$*` | All arguments as one word |
| `$#` | Argument count |
| `$?` | Exit code of last command |
| `$$` | Current script PID |
| `$!` | PID of last background command |
| `$_` | Last argument of previous command |
| `$LINENO` | Current line number |
| `$FUNCNAME` | Current function name |
| `$BASH_SOURCE` | Script filename (works with sourcing) |

### I/O Redirection

| Syntax | Meaning |
|--------|---------|
| `cmd > file` | Redirect stdout, overwrite |
| `cmd >> file` | Redirect stdout, append |
| `cmd 2> file` | Redirect stderr |
| `cmd 2>&1` | Redirect stderr to stdout |
| `cmd &> file` | Redirect both stdout and stderr |
| `cmd > /dev/null 2>&1` | Suppress all output |
| `cmd < file` | Feed file as stdin |
| `cmd1 \| cmd2` | Pipe stdout of cmd1 to stdin of cmd2 |
| `cmd1 \|& cmd2` | Pipe stdout+stderr |
| `cmd <<EOF ... EOF` | Here document |
| `cmd <<< "string"` | Here string |

---

## Kernel and Performance Tuning

### sysctl Quick Reference

```bash
sysctl -a                           # show all parameters
sysctl net.ipv4.ip_forward          # show specific parameter
sysctl -w net.ipv4.ip_forward=1     # set (temporary)
sysctl -p /etc/sysctl.conf          # apply persistent config

# Key parameters:
net.core.somaxconn = 65535          # connection backlog
net.ipv4.ip_local_port_range = 1024 65535
net.ipv4.tcp_syncookies = 1         # SYN flood protection
net.ipv4.tcp_tw_reuse = 1           # reuse TIME_WAIT sockets
vm.swappiness = 10                  # reduce swap for databases
vm.dirty_ratio = 40                 # write cache before flush
fs.file-max = 2097152               # system-wide file descriptors
kernel.pid_max = 4194304            # max PIDs
kernel.randomize_va_space = 2       # ASLR
```

### Resource Limits (ulimit)

```bash
ulimit -a                  # show all limits
ulimit -n 65536            # set open files (soft limit)
ulimit -n unlimited        # remove soft limit

# /etc/security/limits.conf — persistent per-user limits:
* soft nofile 65536
* hard nofile 131072
nginx soft nofile 65536
nginx hard nofile 131072
root soft nofile unlimited
```

### CPU and NUMA

```bash
nproc                              # number of logical CPUs
lscpu                              # CPU architecture detail
lstopo                             # hardware topology
numactl --hardware                 # NUMA topology
numactl --membind=0 --cpunodebind=0 cmd  # bind to NUMA node 0
taskset -c 0,1 cmd                 # bind to CPUs 0 and 1
taskset -c 0,1 -p PID              # bind running process
chrt -f 50 cmd                     # real-time FIFO scheduling
```

---

## Cron Scheduling

```
# MIN HOUR DAY-OF-MONTH MONTH DAY-OF-WEEK COMMAND
  0   2    *     *       *     /usr/local/bin/backup.sh   # daily 2 AM
  */5 *    *     *       *     /usr/local/bin/health.sh   # every 5 min
  0   9    1     *       *     /usr/local/bin/monthly.sh  # 1st of month 9 AM
  0   0    *     *       0     /usr/local/bin/weekly.sh   # every Sunday midnight
  0   8-17 *     *       1-5   /usr/local/bin/workday.sh  # weekdays 8-17
  @reboot /usr/local/bin/init.sh                          # on boot
  @daily /usr/local/bin/daily.sh                          # daily alias
```

```bash
crontab -e           # edit current user's crontab
crontab -l           # list crontab
crontab -r           # remove crontab
crontab -u alice -e  # edit alice's crontab (root)
```

---

## Useful One-Liners

```bash
# Find the top 10 largest files in /var
find /var -type f -printf '%s %p\n' | sort -rn | head -10

# Watch live network connections grouped by state
watch -n 1 "ss -s"

# Find processes with the most open file descriptors
ls -1 /proc/*/fd | cut -d/ -f3 | sort -n | uniq -c | sort -rn | head

# Kill all processes of a specific user
pkill -9 -u baduser

# Stream system log with ISO timestamps
journalctl -f -o short-iso

# Show listening ports in a clean table
ss -tulnp | column -t

# Check which package a file belongs to (Debian)
dpkg -S $(which nginx)

# Recursively find and replace string in files
grep -rl "old_string" /path/ | xargs sed -i 's/old_string/new_string/g'

---

## 🏗️ LVM Management (Logical Volume Manager)

| Command | Description |
|---------|-------------|
| `pvs`, `pvdisplay` | View Physical Volumes |
| `vgs`, `vgdisplay` | View Volume Groups |
| `lvs`, `lvdisplay` | View Logical Volumes |
| `pvcreate /dev/sdb1` | Initialize disk for LVM |
| `vgcreate my_vg /dev/sdb1` | Create volume group |
| `lvcreate -L 10G -n my_lv my_vg` | Create 10GB logical volume |
| `lvextend -L +5G /dev/my_vg/my_lv` | Extend LV by 5GB |
| `resize2fs /dev/my_vg/my_lv` | Resize filesystem after LV extend |
| `lvcreate -s -L 1G -n my_snap /dev/my_vg/my_lv` | Create a snapshot |

---

## ⚡ Performance Profiling (eBPF & Trace)

| Command | Description |
|---------|-------------|
| `bpftrace -e 'tracepoint:syscalls:sys_enter_open { printf("%s %s\n", comm, str(args->filename)); }'` | Trace file opens globally |
| `bpftrace -e 'kprobe:vfs_read { @[comm] = count(); }'` | Count VFS reads per process |
| `perf top -g` | Real-time CPU profiling with call graphs |
| `perf stat -p PID` | Hardware/Kernel event counters for a PID |
| `strace -c -p PID` | Summary of syscalls (count, time, errors) |
| `strace -e trace=network -p PID` | Trace only network-related syscalls |

---

## 🚦 Linux Signals Reference

| Signal | Name | Action | SRE Use Case |
|--------|------|--------|--------------|
| 1 | SIGHUP | Reload | Restart service config without killing process |
| 2 | SIGINT | Interrupt | `Ctrl+C` — Graceful stop |
| 3 | SIGQUIT | Quit | Graceful stop + Core Dump |
| 9 | SIGKILL | Kill | Immediate termination (Kernel level, no cleanup) |
| 15 | SIGTERM | Terminate | Standard `kill` — request graceful shutdown |
| 17/19 | SIGSTOP | Stop | Pause process execution |
| 18/25 | SIGCONT | Continue | Resume paused process |

---

# Show memory usage per process sorted by RSS
ps -eo pid,comm,rss --sort=-rss | head -20 | awk '{printf "%s\t%s\t%.1fMB\n", $1,$2,$3/1024}'

# Tail last 50 lines of systemd journal for a service
journalctl -u myservice -n 50 --no-pager

# Watch disk I/O in real-time
iostat -xz 1

# Decode a base64-encoded secret
echo "SGVsbG8=" | base64 -d

# Count TCP connections by state
ss -tan | awk 'NR>1 {print $1}' | sort | uniq -c | sort -rn

# Find files modified in the last 10 minutes
find / -type f -mmin -10 2>/dev/null

# Show all open ports and the service name
ss -tlnp | awk 'NR>1 {print $4, $6}' | sort

# Test if a remote port is open
timeout 3 bash -c "echo >/dev/tcp/host/port" && echo "open" || echo "closed"

# Generate a random 32-char password
openssl rand -base64 32

# Monitor directory for file changes
inotifywait -m -r -e create,modify,delete /path/to/dir

# Show disk usage by directory, sorted
du -h --max-depth=1 / 2>/dev/null | sort -rh | head -20
```
