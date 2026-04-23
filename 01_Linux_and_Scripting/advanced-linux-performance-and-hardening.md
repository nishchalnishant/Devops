# Advanced Linux Performance & Hardening (7 YOE)

At the senior level, Linux knowledge moves from "running commands" to "tuning the subsystem." You are expected to diagnose why a kernel-space operation is causing a performance bottleneck and how to harden the OS against enterprise-level threats.

---

## 1. Advanced Performance Profiling: The USE Method

For 7 YOE roles, simple "CPU at 80%" alerts are insufficient. You must use the **USE Method** (Utilization, Saturation, Errors) for every system resource.

| Resource | Utilization | Saturation | Errors |
|---|---|---|---|
| **CPU** | % Busy | Load Average / Run Queue | Processor Errors |
| **Memory** | % Used | Swap Activity / OOM Events | Correctable ECC Errors |
| **Disk** | % Device Busy | I/O Wait / Queue Length | Device/Driver Errors |
| **Network** | % Bandwidth | Dropped Packets | TCP Retransmissions |

### The eBPF Revolution
eBPF (Extended Berkeley Packet Filter) allows you to run sandboxed programs in the Linux kernel without changing kernel source code or loading modules.
- **Tools to Know:** `bpftrace`, `bcc-tools`.
- **Use Case:** "Show me which process is causing the highest disk latency right now" or "Trace all `open()` syscalls that are failing with `ENOENT`."

```bash
# Using bpftrace to see disk latency distribution
sudo biolatency.bt
```

---

## 2. Kernel Tuning for High-Scale Workloads

The default Linux kernel settings are for general purpose use. For a high-throughput proxy (Nginx) or a heavy database (Postgres), you must tune `/etc/sysctl.conf`.

### TCP Stack Tuning (for Proxies/API Gateways)
```bash
# Increase the max number of open files
fs.file-max = 2097152

# Increase the backlog of connections waiting to be accepted
net.core.somaxconn = 65535

# Increase the range of ephemeral ports to avoid socket exhaustion
net.ipv4.ip_local_port_range = 1024 65535

# Enable TCP Fast Open to reduce handshake latency
net.ipv4.tcp_fastopen = 3
```

### Virtual Memory Tuning (for Databases)
```bash
# Reduce the 'swapiness' to keep data in physical RAM
vm.swappiness = 10

# Increase the 'dirty_ratio' to allow more data in the write cache before flushing to disk
vm.dirty_ratio = 40
vm.dirty_background_ratio = 10
```

---

## 3. Enterprise Hardening & Security

A senior engineer ensures the OS follows the **CIS Benchmarks** (Center for Internet Security).

### Kernel Self-Protection (KSPP)
- **Disable Kernel Module Loading:** Once a server is running, disabling module loading (`sysctl -w kernel.modules_disabled=1`) prevents attackers from inserting malicious rootkits into the kernel.
- **ASLR (Address Space Layout Randomization):** Ensures internal memory locations are random, making "Buffer Overflow" attacks significantly harder.

### Linux Security Modules (LSM)
- **SELinux (RHEL/CentOS):** Label-based security. "Can process X touch file Y?"
- **AppArmor (Ubuntu/Debian):** Path-based security. "Can `/usr/sbin/nginx` read `/etc/shadow`?" (The answer is no, even if Nginx is hacked).

### CIS Hardening Checklist (Senior Level)
1. **Partitioning:** Keep `/tmp`, `/var`, and `/home` on separate partitions with `nodev`, `nosuid`, and `noexec` flags to prevent execution of malicious binaries.
2. **SSH Hardening:** Disable `PermitRootLogin`, force `Protocol 2`, and use `AllowUsers` to whitelist exactly who can log in.
3. **Auditd:** Configure the Linux Auditing System to track every command run by a user and every modification to sensitive files (like `/etc/passwd`).

---

## 4. Advanced Process Debugging

### CPU Affinity & Cgroups
In multi-core systems, a process jumping between CPUs causes cache misses.
- **CPU Pinning:** Use `taskset` to bind a critical process (like a DB) to specific physical cores.
- **Cgroups v2:** Move beyond "limiting" resources to "protecting" them. Use `memory.low` or `cpu.weight` to guarantee resources for critical system agents even during a massive application spike.

### The Init System (Systemd) Advanced Features
- **Watchdogs:** Use `WatchdogSec=` to automatically restart a service if it stops "kicking" the systemd watchdog timer (detects deadlocks).
- **Hardening in Systemd:** Use `ProtectSystem=strict` and `PrivateTmp=true` directly in the `.service` file to sandbox the application at the unit level.
