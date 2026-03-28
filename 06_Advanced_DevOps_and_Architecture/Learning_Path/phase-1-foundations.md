# Phase 1 - Foundations

This phase builds the base layer for senior DevOps learning. If Linux, Git, scripting, and networking are weak, everything else will feel harder than it needs to.

## Goal

By the end of this phase, you should be able to explain how code moves from a developer workstation to a running service, and how the host and network underneath it behave.

## Study Order

1. `../../08_General_Guides_and_Roadmaps/1.-devops-terms.md`
2. `../../01_Prerequisites_and_Fundamentals/Linux/README.md`
3. `../../01_Prerequisites_and_Fundamentals/Scripting/README.md`
4. `../../01_Prerequisites_and_Fundamentals/Networking/README.md`
5. `../../02_Version_Control_and_CI_CD/Git_GitHub/Notes_Git_GitHub.pdf`
6. `../../07_Interview_Preparation/interview-questions-easy.md`

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
