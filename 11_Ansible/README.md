# Configuration Management (Ansible)

```
Ansible Configuration Management
├── Core Philosophy
│   ├── Agentless: uses SSH — no software to install on targets
│   ├── Push-based: control node sends tasks to managed nodes
│   ├── Idempotent: running same playbook N times = same result
│   └── YAML: human-readable task definitions (playbooks)
├── Architecture
│   ├── Control Node → runs ansible-playbook, has Python + SSH client
│   ├── Managed Nodes → only need Python (+ SSH daemon)
│   ├── Inventory → list of hosts grouped by role
│   └── SSH → transport layer (no agent, no daemon on targets)
├── Key Concepts
│   ├── Inventory   → host list: static (.ini/.yml) or dynamic (plugin)
│   ├── Module      → idempotent unit of work (apt, copy, service, file)
│   ├── Task        → one module call with arguments
│   ├── Playbook    → ordered list of tasks mapped to host groups
│   ├── Role        → reusable, structured group of tasks + vars + handlers
│   ├── Handler     → task triggered only when notified (e.g., restart nginx)
│   ├── Variable    → parameterization (group_vars, host_vars, extra vars)
│   ├── Jinja2      → template engine for dynamic config files
│   ├── Vault       → AES-256 encryption of secrets in playbooks
│   └── Galaxy      → community role registry
├── Idempotency
│   ├── Modules check state before acting (apt checks if installed)
│   ├── shell/command are NOT idempotent by default
│   ├── Use creates: / removes: args on shell to add idempotency
│   └── Use lineinfile/blockinfile instead of shell >> file
├── Interview Focus Areas
│   ├── Easy   → agentless, idempotency, inventory, modules, playbooks, push vs pull
│   ├── Medium → roles, variable precedence, Vault, dynamic inventory, handlers
│   └── Hard   → custom modules, AWX, performance at scale, rolling updates
├── Variable Precedence (highest → lowest)
│   ├── extra vars (-e flag) → always wins
│   ├── task vars / block vars / role vars / set_facts
│   ├── host facts, playbook vars, host_vars, group_vars
│   └── role defaults (defaults/main.yml) → always loses
└── Ansible vs Alternatives
    ├── Puppet     → agent-based, declarative DSL, pull model
    ├── Chef       → agent-based, Ruby DSL, procedural
    ├── SaltStack  → agent or agentless, event-driven, high speed
    └── Terraform  → IaC (complementary: TF provisions, Ansible configures)
```

## First Principles

- You need to configure many servers consistently. SSH already exists on every Linux server — no new protocol or agent required. Ansible exploits this: the control node SSHes out and runs Python on the target.
- Describing desired state as YAML tasks that check-before-act (idempotent) means you can safely re-run playbooks without fear of breaking already-configured systems. This is the opposite of shell scripts that blindly execute.
- Grouping servers by role (webservers, dbservers) in inventory lets you write one playbook that applies to all members of a group. Adding a new server to the group automatically enrolls it in all associated playbooks.
- Roles are reusable packages of configuration. A `webserver` role knows how to install nginx, configure it, and set up a systemd service. Any playbook that needs a web server just includes the role — no copy-paste.
- Push-based means the control node is the single source of truth and the executor. Pull-based (ansible-pull, Puppet, Chef) distributes execution to the targets — better at very high scale (10,000+ nodes) but requires agents.

Ansible is the most widely-used agentless configuration management and automation tool. It uses SSH to connect to target machines, executes tasks defined in YAML playbooks, and is idempotent by design.

***

## What Is in This Module

| File | Purpose |
|:---|:---|
| `notes/ansible-playbooks.md` | Playbooks, roles, variables, templates, handlers |
| `notes/ansible-advanced.md` | Dynamic inventory, Vault, callbacks, AWX/Automation Platform |
| `cheatsheet.md` | Module reference, CLI commands, common patterns, Jinja2 |
| `interview.md` | Consolidated Interview Questions: Easy, Medium, and Hard levels |
| `scenarios.md` | Real-world troubleshooting and automation design scenarios |

***

## Architecture — How Ansible Works

```
Control Node (your laptop or CI server)
    │
    ├── Reads: inventory.yml (or dynamic inventory script)
    ├── Reads: playbook.yml
    │
    ├── SSH connection ──► Target: web-server-01 (192.168.1.10)
    │       │                       └── Python (only requirement)
    │       ├── Upload module (Python script)
    │       ├── Execute module
    │       └── Remove module + return JSON result
    │
    ├── SSH connection ──► Target: web-server-02 (192.168.1.11)
    └── SSH connection ──► Target: db-server-01  (192.168.1.20)

No agent installed. No daemon running. Pure SSH.
```

***

## Key Concepts Reference

| Concept | Purpose | Example |
|:---|:---|:---|
| **Inventory** | List of target hosts grouped logically | `[webservers]` group with 5 IPs |
| **Module** | Idempotent unit of work | `apt`, `copy`, `service`, `file`, `template` |
| **Task** | Single module execution with args | `- name: Install nginx\n  apt: name=nginx` |
| **Playbook** | Ordered list of tasks for a host group | `site.yml` — maps `webservers` to tasks |
| **Role** | Reusable, structured group of tasks | `roles/webserver/` with tasks, vars, handlers |
| **Handler** | Task triggered only when notified | Restart nginx only when config changes |
| **Variable** | Parameterization across environments | `group_vars/production/vars.yml` |
| **Jinja2 template** | Dynamic config file generation | `nginx.conf.j2` → renders with host-specific vars |
| **Vault** | Encrypted secrets in playbooks | `ansible-vault encrypt vars/secrets.yml` |
| **Galaxy** | Community role registry | `ansible-galaxy install geerlingguy.docker` |

***

## Idempotency — The Golden Rule

Idempotency means running the same playbook multiple times produces the same result:

```yaml
# IDEMPOTENT (use modules):
- name: Ensure nginx is installed
  apt:
    name: nginx
    state: present    # Check first; install only if not present

# NOT IDEMPOTENT (avoid shell/command unless necessary):
- name: Install nginx
  shell: apt-get install nginx   # Runs every time; "already installed" is an error
```

**When you must use `shell` or `command`:**
```yaml
- name: Check if app is initialized
  command: /opt/app/bin/check-init
  register: init_result
  changed_when: false           # Never mark this task as "changed"
  failed_when: init_result.rc > 1

- name: Initialize app (only if needed)
  command: /opt/app/bin/init
  when: init_result.rc == 1
```

***

## Interview Focus Areas

| Difficulty | Key Topics |
|:---|:---|
| **Easy** | Agentless via SSH, idempotency, inventory, modules, playbooks, ad-hoc commands |
| **Medium** | Roles structure, variable precedence (18 levels!), dynamic inventory (AWS/GCP), Ansible Vault, handlers, `when` conditionals |
| **Hard** | Custom module development (Python), AWX/Automation Platform vs CLI, performance (Mitogen, pipelining, forks), rolling updates with `serial`, fact caching |

***

## Variable Precedence (high → low)

```
1.  Extra vars (-e flag)               ← Highest — overrides everything
2.  Task vars (within a task)
3.  Block vars
4.  Role vars (vars/main.yml)
5.  Include vars
6.  Set_facts
7.  Registered vars
8.  Host facts (gathered by setup)
9.  Playbook vars
10. Host vars
11. Group vars (children)
12. Group vars (all)
13. Role defaults (defaults/main.yml)   ← Lowest — easily overridden
```

This ordering is one of the most common exam and interview questions. Remember: `extra vars` win always; `role defaults` lose always.

***

## Ansible vs Alternatives

| Tool | Paradigm | Best For |
|:---|:---|:---|
| **Ansible** | Agentless, push-based, YAML | General-purpose config management; no agent install possible |
| **Puppet** | Agent-based, declarative (Puppet DSL) | Large Windows + Linux fleets with strict compliance |
| **Chef** | Agent-based, procedural (Ruby DSL) | Development-heavy orgs; complex logic |
| **SaltStack** | Agent or agentless, event-driven | High-speed at scale; real-time event response |
| **Terraform** | IaC, declarative | Provisioning infrastructure (complementary to Ansible) |

***

## System Design Perspective

**Ansible at scale (1000+ hosts):**
- Forks (default 5): increase to 50-100. Ansible runs tasks on `forks` hosts simultaneously. Higher forks = faster execution, higher SSH connection overhead.
- Pipelining: runs multiple module steps in a single SSH connection rather than creating a new connection per task. Requires `requiretty` disabled in sudoers.
- Mitogen strategy plugin: replaces the SSH transport with a multiplexed connection that reuses a single process per target. Typically 3-10x faster than default.
- Fact caching (Redis or JSON files): avoids re-running the `setup` module (fact gathering) on every run. Facts are gathered once and cached for N hours.

**ansible-pull for auto-scaling environments:**
- In AWS Auto Scaling Groups, new instances appear and disappear dynamically. Running `ansible-pull` at boot (via cloud-init/user-data) lets each instance configure itself by pulling playbooks from Git — no push from a control node required.
- The tradeoff: pull mode is harder to debug (no central execution log) and requires Git access from each instance. AWX with dynamic inventory is usually preferable for large ASGs.

**AWX/Automation Platform as an enterprise control plane:**
- RBAC: team A can only run templates for their services. Team B cannot accidentally apply team A's playbooks.
- Execution Environments (EEs): containers with a specific Ansible version, collections, and Python packages. Reproducible execution regardless of where the job runs.
- Smart inventory: dynamically filter hosts from existing inventories using complex criteria (group + tag + last job status). Enables targeted re-runs without custom scripts.