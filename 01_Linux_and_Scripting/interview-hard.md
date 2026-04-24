## Hard

**29. How does the Linux kernel's OOM killer select which process to terminate?**

The OOM killer scores each process using `/proc/PID/oom_score`, which factors in: the process's RSS (resident set size), the proportion of physical memory it uses, whether it has CAP_SYS_ADMIN, and the `oom_score_adj` value (tunable per process, range -1000 to +1000). The process with the highest score is killed. You can protect critical processes with `oom_score_adj = -1000` (which sets score to 0, preventing OOM kill) or deprioritize them with positive adjustments.

**30. Explain Linux cgroups v2 and how they are used in containers.**

cgroups v2 is a unified hierarchy for resource control. Unlike v1 (which had separate hierarchies per controller), v2 uses a single tree where each node can have multiple controllers (cpu, memory, io, pids). Containers (Docker, Kubernetes) use cgroups to:
- Enforce memory limits (`memory.max`) and kill containers that exceed them.
- Enforce CPU bandwidth (`cpu.max`, format: `quota period`).
- Limit I/O bandwidth (`io.max`).
- Limit process count (`pids.max`).

Kubernetes uses cgroups v2 when `--cgroup-driver=systemd` is set on the kubelet, which delegates cgroup management to systemd.

**31. How do you debug a performance regression using perf and flame graphs?**

1. Run `perf record -g -p <PID> -- sleep 30` to record call stacks for 30 seconds.
2. Run `perf script` to convert to a text format.
3. Use Brendan Gregg's `flamegraph.pl` to generate a flame graph SVG.
4. The flame graph visualizes where CPU time is spent: wide stacks = hot code paths. Identify the widest plateau at the top of the graph — that function is the hottest path consuming CPU.

**32. What is eBPF and how is it used for performance observability?**

eBPF (extended Berkeley Packet Filter) allows running sandboxed programs in the Linux kernel without modifying kernel source. For performance observability: tools like `bpftrace`, `BCC`, and `Cilium` use eBPF to attach probes to kernel and user-space functions at runtime. You can measure exact latency of system calls, trace TCP connections, profile function call frequency — all with near-zero overhead compared to traditional instrumentation. Example: `bpftrace -e 'tracepoint:syscalls:sys_enter_read { @[comm] = count(); }'` counts read syscalls per process name.

**33. How do you implement a high-performance log pipeline from multiple servers?**

Architecture:
1. **Collection:** Use a lightweight agent (`Fluent Bit`, `Vector`, `Promtail`) on each server — reads from journald/file, parses structured fields, compresses, and forwards.
2. **Transport:** Kafka as a buffer between collectors and processors — decouples producer (servers) from consumer (processing pipeline). Handles burst traffic.
3. **Processing:** Logstash, Flink, or Vector processes the Kafka stream — parses, enriches (GeoIP, service name lookup), and routes.
4. **Storage:** OpenSearch/Elasticsearch for search workloads; Loki for high-cardinality log storage with label indexing only.
5. **Backpressure:** If downstream is slow, Kafka buffers — agents are not blocked. Dead letter queues for unparseable messages.

---

## Staff/Senior Level (7+ YOE)

**34. Explain the performance impact of LVM snapshots on write operations.**

LVM snapshots use **Copy-on-Write (CoW)**. When a snapshot exists, every write to an original block requires:
1. Reading the old block.
2. Writing it to the snapshot area.
3. Overwriting the original block.
This effectively turns every write into **three I/O operations** (1 Read + 2 Writes). In write-heavy databases, this can cause a 50-70% performance drop. Modern solutions use **LVM Thin Snapshots** which are much more efficient but require careful monitoring of metadata space.

**35. What is the difference between Voluntary and Involuntary context switches?**

- **Voluntary:** The process gives up the CPU because it's waiting for something (I/O, a sleep call, or a mutex).
- **Involuntary:** The kernel forces the process off the CPU because its time slice is up or a higher-priority process needs to run.
**SRE Context:** High *involuntary* switches indicate your system is CPU-saturated (too many processes for the cores). High *voluntary* switches often indicate an application bottleneck (waiting on locks or I/O). Check via `pidstat -w`.

**36. How do HugePages improve database performance?**

Standard Linux pages are 4KB. A 128GB database would require 32 million page table entries. The CPU's **TLB cache** cannot fit this, leading to "TLB Misses" and high overhead. By using **HugePages (2MB or 1GB)**, the number of entries drops significantly, fitting the entire mapping into the CPU cache and improving performance by 10-15%.

**37. How do you implement a Systemd Watchdog for a service?**

In the `[Service]` section of the unit file:
1. `WatchdogSec=30s`: The service must send a "heartbeat" to systemd every 30s.
2. `Restart=on-failure`: If the heartbeat stops, systemd kills and restarts the service.
3. **Application Side:** The app must be coded to call `sd_notify("WATCHDOG=1")` periodically. This prevents "Ghost Services" that are technically running but logically deadlocked.
