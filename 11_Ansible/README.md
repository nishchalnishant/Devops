# Configuration Management (Ansible)

Ansible is the most widely-used agentless configuration management and automation tool. It uses SSH to connect to target machines, executes tasks defined in YAML playbooks, and is idempotent by design.

***

## What Is in This Module

| File | Purpose |
|:---|:---|
| `notes/ansible-playbooks.md` | Playbooks, roles, variables, templates, handlers |
| `notes/ansible-advanced.md` | Dynamic inventory, Vault, callbacks, AWX/Automation Platform |
| `cheatsheet.md` | Module reference, CLI commands, common patterns, Jinja2 |
| `interview-easy.md` | Foundational: agentless, idempotency, inventory, modules, playbooks |
| `interview-medium.md` | Intermediate: roles, variables precedence, Vault, dynamic inventory |
| `interview-hard.md` | Advanced: custom modules, AWX, performance at scale, rolling updates |
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
