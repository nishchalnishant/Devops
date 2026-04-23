# DevOps Terms and Concepts

### 1. What is DevOps?

DevOps is not just a job title or a tool; it is a cultural shift and a set of practices that combine Software Development (Dev) and Information Technology Operations (Ops).

* Core Goal: Its primary objective is to shorten the systems development life cycle and provide continuous delivery with high software quality.
* Collaboration: It breaks down the "silos" between developers who write code and the operations teams who maintain the servers, encouraging shared responsibility.
* The Infinite Loop: It is often visualized as an infinity symbol representing a continuous cycle of planning, coding, building, testing, releasing, deploying, operating, and monitoring.

***

### 2. Is DevOps Good For Me?

The roadmap suggests evaluating career alignment before diving into technical tools. You might find DevOps a good fit if:

* You enjoy Problem Solving: You like figuring out why a system crashed or how to make a process 10x faster.
* You like Variety: The role requires a "T-shaped" skill set—deep knowledge in one area (like Linux) and broad knowledge across many others (like networking, security, and coding).
* You have an Automation Mindset: If you find yourself wanting to script a task because doing it manually twice feels like a waste of time, you have the right temperament for DevOps.

***

### 3. Core Concepts & Definitions

These are the foundational "building blocks" mentioned in your roadmap that every DevOps engineer must understand:

#### A. Infrastructure

In DevOps, we often talk about Infrastructure as Code (IaC). This refers to the underlying foundation—the servers, storage, and networks—required to run applications. Instead of manually plugging in cables or clicking buttons in a dashboard, we manage this foundation using configuration files.

#### B. Scaling

Scaling is the ability of a system to handle increases in load (more users or more data).

* Vertical Scaling: Adding more "power" (CPU, RAM) to an existing server.
* Horizontal Scaling: Adding _more servers_ to work together as a single system.

#### C. Monitoring

Monitoring involves the continuous observation of systems to ensure they are healthy.

* Health Checks: Is the website up?
* Performance: How fast is the page loading?
* Alerting: Automatically notifying an engineer if something breaks so they can fix it before the user notices.

#### D. Automation

Automation is the "heart" of DevOps. It involves using technology to perform tasks with reduced human assistance.

* Why automate? It removes human error, ensures tasks are repeatable, and allows teams to deploy software hundreds of times a day instead of once a month.



This is an excellent starting point. Since you provided the Roadmap as Section 1, we will treat this as the Foundational Architecture & System Internals phase. For a mid-to-senior SRE/DevOps role, the "Roadmap" isn't just a list of tools; it is a mental map of how data flows from a user's browser to the kernel of a server.

Here is the refined, industry-grade expansion of Section 1: Foundations, Linux Internals, and Networking.

***

#### 🔹 1. Improved Notes: The SRE Foundation

**The Linux Kernel & User Space**

In production, you aren't just "using Linux"; you are managing resources.

* Namespaces & Cgroups: These are the bedrock of Docker/Kubernetes. Namespaces provide isolation (what a process can see: PID, Net, Mount), while Cgroups provide restriction (how much it can consume: CPU, Memory, I/O).
* The Boot Process & Systemd: Understanding `systemd` is critical for managing services, targets, and logging (`journalctl`). You must understand how a service lifecycle (Restart=always, OOMScoreAdjust) affects reliability.
* File Descriptors (FD): In Linux, "everything is a file." High-traffic applications often fail because they hit the `ulimit` (max open files). An SRE must know how to tune `sysctl.conf`.

**Networking: The Data Plane**

* The TCP/IP Stack & Three-Way Handshake: Beyond the basics, you must understand TCP States (TIME\_WAIT, CLOSE\_WAIT). A "connection leak" usually manifests here.
* DNS Resolution: It’s almost always DNS. Understand the difference between Recursive and Authoritative servers, and how `nscd` or `CoreDNS` caches records.
* Load Balancing (L4 vs L7): L4 (TCP/UDP) is fast and handles routing based on IP/Port. L7 (HTTP/HTTPS) is "intelligent" and routes based on headers, cookies, or paths.

***

#### 🔹 2. Interview View (Q\&A)

Q1: What is the difference between "Load Average" and "CPU Utilization"?

* Answer: CPU Utilization is the percentage of time the CPU was busy. Load Average (from `uptime`) includes processes using the CPU, processes _waiting_ for the CPU, and processes blocked by I/O (Uninterruptible sleep).
* Follow-up: "If Load is 10 but CPU is 10%, what's happening?" -> The system is likely bottlenecked on Disk I/O or Network I/O, not compute.

Q2: Describe the "Happy Path" of a request hitting a server.

* Answer: DNS Resolution -> TCP Handshake -> TLS Negotiation (SNI) -> Load Balancer (L7) -> Reverse Proxy (Nginx/Envoy) -> Application Pod -> Database/Cache.
* Senior Twist: Mention Connection Pooling and Keep-Alive timeouts to show you understand latency optimization.

Q3: How does a container actually limit memory?

* Answer: Through the Memory Cgroup. When a process exceeds the `memory.limit_in_bytes`, the Linux Kernel triggers the OOM (Out Of Memory) Killer, which selects a process to terminate (usually the one consuming the most memory) to save the system.

***

#### 🔹 3. Architecture & Design: The Production Stack

Design Concern: Scalability vs. Availability

* Horizontal Scaling: Adding more nodes (stateless).
* Vertical Scaling: Adding more RAM/CPU (limited by hardware).
* SRE Trade-off: When designing a system, you must consider the Blast Radius. If you have one massive Load Balancer, it’s a Single Point of Failure (SPOF). You must design for Multi-AZ (Availability Zone) redundancy.

Failure Scenarios:

* Zombie Processes: Processes that have finished execution but remain in the process table because the parent didn't "reap" them. Too many can exhaust the PID limit.
* Split Brain: In a high-availability cluster, if the network link between two nodes breaks, both might think they are the "Leader," leading to data corruption.

***

#### 🔹 4. Commands & Configs (The "SRE Toolbelt")

**System Debugging**

Bash

```
# Check open files by a specific process
lsof -p <pid>

# Monitor real-time network connections (replaces netstat)
ss -tulpn

# Check kernel logs for OOM kills or hardware errors
dmesg -T | grep -i "oom"

# Find which process is causing high Disk I/O
iotop -o
```

**Kernel Tuning (`/etc/sysctl.conf`)**

Bash

```
# Increase max open files for high-concurrency servers
fs.file-max = 2097152

# Reduce the time a connection stays in TIME_WAIT
net.ipv4.tcp_fin_timeout = 30
```

***

#### 🔹 5. Troubleshooting & Debugging

Scenario: A web server is "Up" but users are getting "504 Gateway Timeout".

1. Check Connectivity: Can the Load Balancer talk to the Web Server? (`telnet` or `nc` to the port).
2. Check Resources: Is the Web Server at 100% CPU or out of Memory? (`top`, `free -m`).
3. Check Logs: Look at Nginx/Apache error logs. If you see "upstream timed out," the backend application (Python/Java/Go) is taking too long to respond.
4. Check External Dependencies: Is the Database locked? Is a 3rd party API down?
5. Check Network: Use `mtr <ip>` to see if there is packet loss at a specific hop.

***

#### 🔹 6. Production Best Practices

* Immutable Infrastructure: Never `ssh` into a server to fix a config manually. Fix it in code (Terraform/Ansible) and redeploy.
* Least Privilege: Never run applications as `root`. Use `sudo` or specific service accounts.
* Monitoring over Alerting: Don't alert on "CPU is 80%." Alert on "User Latency is > 500ms." (Symptoms vs. Causes).
* Anti-Pattern: Hardcoding IP addresses in configs. Always use DNS or Service Discovery (Consul/K8s Service).

***

#### 🔹 Cheat Sheet / Quick Revision

* Linux: Namespaces (Isolation), Cgroups (Limits), Inodes (File metadata), Systemd (Process management).
* Networking: ARP (IP to MAC), DNS (Name to IP), TCP (Reliable), UDP (Fast), MTU (Packet size).
* Performance: `top` (CPU), `iostat` (Disk), `vmstat` (Memory/Swap), `sar` (Historical stats).
* SRE Mantra: "If you have to do it more than twice, automate it."

***

This section focuses on the mindset, culture, and core terminology that defines the DevOps and SRE movement. For a mid-to-senior role, the interviewer isn't looking for a dictionary definition; they want to see if you understand the business value and architectural impact of these terms.

***

#### 🟢 Easy: Foundations & Definitions

_Focus: Can you define the basic building blocks?_

1. What is the "DevOps Loop" or "Infinity Loop," and why is it represented that way?
   * _Context:_ Focus on the continuous feedback between Development (Plan, Code, Build, Test) and Operations (Release, Deploy, Operate, Monitor).
2. Explain the difference between a Monolithic and Microservices architecture.
   * _Context:_ Discuss deployment speed, scaling individual components, and the "blast radius" of a failure.
3. What does "Fail Fast" mean in a DevOps context?
   * _Context:_ The importance of short feedback loops (automated tests/CI) to catch errors before they reach production.
4. Define Scalability vs. Availability.
   * _Context:_ Scalability is the ability to handle more load; Availability is the percentage of time the system is operational.

***

#### 🟡 Medium: Core Principles & SDLC

_Focus: Can you explain the "How" and "Why"?_

1. Explain the CAMS Model (Culture, Automation, Measurement, Sharing). Which pillar is the hardest to implement in a legacy company?
   * _Context:_ Usually, Culture is the answer. You can automate tools, but changing human behavior and breaking silos is the real SRE challenge.
2. What is the difference between Continuous Delivery (CD) and Continuous Deployment (CD)?
   * _Context:_ The "Manual Approval" gate. Delivery means code is _ready_ for production; Deployment means it _goes_ to production automatically.
3. What is "Infrastructure as Code" (IaC) and why is "versioning" your infrastructure important?
   * _Context:_ Discuss audit trails, reproducibility, and the ability to roll back the entire environment to a known good state.
4. Explain the "Shift-Left" concept.
   * _Context:_ Moving security, testing, and performance analysis earlier into the development process rather than treating them as an afterthought.

***

#### 🔴 Hard: Architecture & SRE Nuances

_Focus: Can you handle trade-offs and senior-level decision-making?_

1. "SRE is an implementation of DevOps." Explain this statement. How does an SRE’s day-to-day differ from a DevOps Engineer’s?
   * _Context:_ DevOps is the "philosophy" (the interface); SRE is the "implementation" (the class). SREs focus heavily on reliability engineering and toil reduction through code.
2. How do you calculate "Availability" and what do the "Nines" mean?
   *   Context: Availability is calculated as:

       \$$Availability = \frac{\text{MTBF\}}{\text{MTBF} + \text{MTTR\}}\$$

       (Where MTBF is Mean Time Between Failures and MTTR is Mean Time To Repair). Explain that "Five Nines" (99.999%) allows only 5.26 minutes of downtime per year.
3. Explain the "CAP Theorem" and how it influences your choice of a database in a distributed microservices environment.
   * _Context:_ Consistency, Availability, Partition Tolerance. You can only pick two. An SRE must decide which to sacrifice based on the business use case (e.g., Banking needs Consistency; Social Media needs Availability).
4. What is "Technical Debt" and how does a "Toil Budget" help manage it?
   * _Context:_ Toil is manual, repetitive work. SREs aim to keep toil below 50%. If it exceeds that, the team stops feature work to automate the debt away.

***

#### 💡 Pro-Tip for your Interview

When answering these questions, always use the phrase "The Blast Radius."

* _Example:_ "We moved from a Monolith to Microservices not just for speed, but to reduce the blast radius. If the Payment service fails, it shouldn't take down the Login service."

---

## 🔷 Staff/Principal SRE Dictionary (7 YOE)

The following terms are the vocabulary of Senior and Staff engineers. In an interview, using these naturally signals you are operating at the right level.

| Term | Definition | Interview Signal |
|---|---|---|
| **Golden Path** | An opinionated, supported template for how to build and deploy services. Developers can deviate but lose platform support. | "We built a Backstage template that gave developers a running microservice with CI, observability, and IaC wired in within 10 minutes." |
| **Guardrails** | Automated policies (OPA/Kyverno) that prevent engineers from making dangerous choices without blocking them from working. | "Instead of saying 'no', our guardrails automatically block public S3 buckets in CI before the infrastructure is ever applied." |
| **Error Budget Burn Rate** | The rate at which you are consuming your reliability allowance. 14× burn rate means you'd exhaust a 30-day error budget in ~2 days. | "We use multi-window burn rate alerts — a 14× burn rate pages immediately; a 3× burn rate creates a Jira ticket for the sprint." |
| **Value Stream Mapping** | A visual map of every step and wait time from code commit to production. Identifies waste in the delivery pipeline. | "Our VSM revealed that 95% of our 3-week lead time was waiting for manual approvals. Automating them cut lead time to 45 minutes." |
| **Architecture Decision Record (ADR)** | A short document capturing a technical decision: context, decision made, alternatives considered, and consequences. | "I write ADRs for every major platform decision so that future engineers understand the reasoning, not just the outcome." |
| **DORA Metrics** | 4 key KPIs for software delivery: Deployment Frequency, Lead Time for Changes, Change Failure Rate, Time to Restore. | "We use DORA metrics to measure our platform's impact on developer velocity. When Lead Time increased, I used it to justify investment in CI improvements." |
| **Showback / Chargeback** | FinOps models where cloud costs are reported (Showback) or billed back (Chargeback) to individual teams based on consumption. | "I implemented Kubernetes label-based cost attribution with Kubecost to give each team a monthly cloud spend report." |
| **Toil Budget** | The formal cap (typically 50%) of operational toil (manual, repetitive work) allowed per sprint. Exceeding it triggers mandatory automation work. | "When our toil exceeded 60%, I suspended new feature work and ran a 2-week automation sprint that freed up 8 hours per engineer per week." |
| **Platform NPS** | Net Promoter Score for internal developer experience. Measures how satisfied developers are with platform tools. | "I ran quarterly platform NPS surveys. A 15-point drop in satisfaction led us to rewrite our deployment CLI interface." |
| **Hermetic Build** | A build process with zero internet access at build time. All dependencies are pre-resolved and frozen into a private cache, ensuring reproducibility and supply chain safety. | "Our SLSA Level 3 compliance required hermetic builds. We pre-mirror all npm/pip packages to our internal Artifact Registry." |
| **SPIFFE/SPIRE** | Standards and implementations for cryptographic workload identity in a Zero-Trust environment. Eliminates static secrets between services. | "We replaced shared API keys between services with SPIFFE SVIDs. Services prove their identity cryptographically, not with a password." |
| **GameDay** | A structured chaos engineering exercise where failures are intentionally injected to validate resilience before customers encounter them. | "We run monthly GameDays. Killing a random AZ in staging revealed our auto-failover DNS TTL was 5 minutes, not 30 seconds as designed." |

---

## Related Resources

- [Senior DevOps Learning Path](../06_Advanced_DevOps_and_Architecture/Learning_Path/README.md)
- [DevOps Interview Playbook](../07_Interview_Preparation/devops-interview-playbook.md)
- [Linux Fundamentals](../01_Prerequisites_and_Fundamentals/Linux/README.md)
- [Networking Fundamentals](../01_Prerequisites_and_Fundamentals/Networking/README.md)
- [Senior DevOps Roadmap](senior-devops-roadmap.md)
