# Phase 1 - Foundations

```
Phase 1 - Foundations
├── DevOps And Systems Thinking
│   ├── DevOps as collaboration, automation, feedback, shared ownership
│   ├── Scalability versus availability distinction
│   ├── Why observability precedes troubleshooting
│   └── Why toil reduction defines senior contribution
├── Git And Delivery Hygiene
│   ├── Core commands: clone, branch, commit, merge, rebase, fetch, pull, revert
│   ├── Pull request flow and protected branches
│   └── Safe rollback (revert) versus destructive history rewrite (reset)
├── Linux
│   ├── Filesystems: structure, permissions, ownership, sudo
│   ├── Process inspection: signals, top, ps, kill, /proc
│   ├── Open ports: ss, lsof, netstat
│   ├── Memory and disk: free, df, du, iostat
│   ├── systemd: systemctl, journalctl, service management
│   └── Package management and CLI fluency
├── Shell Scripting
│   ├── Variables, loops, conditions, functions, exit codes
│   ├── Writing safe Bash: set -euo pipefail, ShellCheck
│   └── Automating repeated operational tasks
├── Networking
│   ├── IP addressing, CIDR notation, routing, ports
│   ├── TCP versus UDP behavior differences
│   ├── DNS resolution: query path, TTL, troubleshooting with dig/nslookup
│   ├── Connection error types: refused vs timed out vs reset
│   ├── TLS basics: handshake, certificates, trust chains
│   └── Load balancing: L4 vs L7, round robin vs least connections
├── Hands-On Tasks
│   ├── Shell script: basic host health check
│   ├── systemctl + journalctl: inspect a running service
│   ├── ss, curl, dig, ip route: live host investigation
│   ├── Git repo: merge, rebase, revert, branch cleanup practice
│   └── Explain full browser-to-backend request path in your own words
└── Exit Criteria
    ├── Work comfortably in terminal without guessing
    ├── Explain basic Git collaboration flow
    ├── Inspect Linux host for CPU, memory, disk, port issues
    ├── Explain DNS, TCP, CIDR, and TLS at practical level
    └── Automate a simple operational task with a script
```

## First Principles

- **Why Linux before everything else?** Every container runs on Linux. Every Kubernetes node is Linux. Debugging a production issue without understanding processes, namespaces, signals, and file descriptors is guesswork.
- **Why Git hygiene before CI/CD tools?** CI/CD tools are wrappers around Git events. If the branching model and merge strategy are unclear, the pipeline design will reflect that confusion.
- **Why scripting before cloud platforms?** Cloud platforms expose APIs, and scripts call those APIs. A script that fails silently or lacks error handling will corrupt state in any environment — local, staging, or production.
- **Why networking fundamentals before Kubernetes networking?** Kubernetes networking is standard IP networking with labels on top. CNI plugins, Services, and Ingress all become tractable once DNS, routing, and connection semantics are clear.
- **Why checkpoint questions, not just reading?** Passive reading creates familiarity, not recall. The checkpoint questions simulate the live pressure of an interview and reveal the difference between recognition and true understanding.

This phase builds the base layer for senior DevOps learning. If Linux, Git, scripting, and networking are weak, everything else will feel harder than it needs to.

## Goal

By the end of this phase, you should be able to explain how code moves from a developer workstation to a running service, and how the host and network underneath it behave.

## Study Order

1. `../08_General_Guides_and_Roadmaps/roadmap_README.md`
2. `../01_Linux_and_Scripting/README.md`
3. `../01_Linux_and_Scripting/README.md`
4. `../02_Networking/README.md`
5. `../03_Git_and_Version_Control/notes/Notes_Git_GitHub.md`
6. `../07_Interview_Preparation/interview-questions-easy.md`

## What To Master

### DevOps And Systems Thinking

- DevOps as collaboration, automation, feedback, and shared ownership
- Scalability versus availability
- Why observability matters before troubleshooting
- Why toil reduction matters in senior roles

### Git And Delivery Hygiene

- clone, branch, commit, merge, rebase, fetch, pull, revert
- pull request flow and protected branches
- the difference between safe rollback and destructive history changes

### Linux

- filesystems, permissions, ownership, and `sudo`
- process inspection, signals, open ports, memory, and disk usage
- `systemd`, logs, and service management
- package management and CLI fluency

### Shell Scripting

- variables, loops, conditions, functions, exit codes
- writing safe Bash scripts
- automating repeated operational tasks

### Networking

- IP addressing, CIDR, routing, ports, TCP, UDP
- DNS resolution and troubleshooting
- the difference between timeout, reset, and refused connections
- TLS basics and load balancing

## Hands-On Tasks

1. Write a shell script that performs a basic host health check.
2. Use `systemctl` and `journalctl` to inspect a running service.
3. Use `ss`, `curl`, `dig`, and `ip route` on a local or lab machine.
4. Create a small Git repo and practice merge, rebase, revert, and branch cleanup.
5. Explain the full path of a browser request to a backend service in your own words.

## Checkpoint Questions

- What is the difference between `git revert` and `git reset`?
- How do you identify which process is listening on a port?
- What is the difference between CPU usage and load average?
- What happens during DNS resolution?
- Why does a DevOps engineer need scripting, not just commands?

## Exit Criteria

Move to Phase 2 only when you can:

- work comfortably in the terminal without guessing
- explain basic Git collaboration flow
- inspect a Linux host for CPU, memory, disk, and port issues
- explain DNS, TCP, CIDR, and TLS at a practical level
- automate a simple operational task with a script

***

## Related Resources

- [DevOps Terms and Concepts](../08_General_Guides_and_Roadmaps/roadmap_README.md)
- [Linux Fundamentals](../01_Linux_and_Scripting/README.md)
- [Scripting Basics](../01_Linux_and_Scripting/README.md)
- [Networking Fundamentals](../02_Networking/README.md)
- [Easy Interview Questions](../07_Interview_Preparation/interview-questions-easy.md)
- [Advanced Linux Performance](../01_Linux_and_Scripting/notes/advanced-linux.md) (for senior depth)

***

**Next:** [Phase 2 - Platform and Delivery](phase-2-platform-and-delivery.md)
