# Ansible — Interview Prep

```
Ansible Fundamentals (Interview: Easy)
├── What & Why
│   ├── Agentless configuration management + automation tool
│   ├── Uses SSH — no agent installation on managed nodes
│   ├── YAML playbooks — human-readable, version-controllable
│   └── Sits after Terraform: TF provisions infra, Ansible configures it
├── Playbook vs Role
│   ├── Playbook: ordered list of tasks for a host group (a script)
│   └── Role: reusable, structured bundle of tasks/vars/handlers/templates
├── Agentless Architecture
│   ├── Control node: has Ansible + SSH client + Python
│   ├── Managed nodes: only need SSH daemon + Python
│   └── No persistent daemon on targets — SSH on demand
├── Idempotency
│   ├── Same playbook run N times → same end state
│   ├── Modules check current state before acting
│   ├── apt: checks if package installed → skips if yes
│   └── shell/command: NOT idempotent (use modules instead)
├── Templates (Jinja2)
│   ├── .j2 files with {{ variable }} and {% if %} logic
│   ├── template module renders + copies to managed node
│   └── Use for: nginx.conf, application.properties, systemd units
├── Inventory
│   ├── Static: INI or YAML file listing hosts + groups
│   ├── Dynamic: plugin queries cloud API (aws_ec2, azure_rm)
│   └── group_vars / host_vars: directory-based variable overrides
└── Push vs Pull
    ├── Push (Ansible default): control node SSHes out, runs tasks
    ├── Pull (ansible-pull): managed node crons + pulls from Git
    └── Pull use case: auto-scaling groups, air-gapped environments
```

### First Principles

- Ansible assumes SSH connectivity already exists (standard on every Linux server). It uploads a Python script (the module) to the target, executes it, captures the JSON output, and removes the script. No persistent state on the target.
- A playbook is a declaration of desired state expressed as an ordered sequence of idempotent tasks. The order matters for dependencies (install before configure, configure before start). But each individual task is self-contained and safe to re-run.
- The distinction between `playbook` and `role` mirrors the distinction between a script and a library function. A playbook is the entry point; a role is a reusable component that a playbook includes. You would not put nginx configuration logic directly in `site.yml` — you'd put it in a `nginx` role.
- Dynamic inventory is not magic: it's a plugin that calls a cloud API and returns JSON in the Ansible inventory format. The `aws_ec2` plugin calls `ec2:DescribeInstances` and groups results by tags, region, instance type — whatever you configure.

## Easy

**1. What is Ansible and what is it used for?**

Ansible is an agentless configuration management and automation tool. In a DevOps context, it automates application deployment, software provisioning, system configuration, and orchestration tasks — typically as the configuration layer on top of infrastructure provisioned by Terraform.

**2. What is an Ansible playbook and what is a role?**

- A **playbook** is a YAML file defining an ordered list of tasks to execute on remote hosts.
- A **role** is a structured, reusable directory layout (`tasks/`, `handlers/`, `defaults/`, `templates/`, `files/`) that encapsulates a unit of configuration. Roles are shareable via Ansible Galaxy.

**3. Why is Ansible considered agentless?**

Ansible communicates over SSH for Linux and WinRM for Windows. No special agent software is required on managed nodes — only Python (which is pre-installed on most Linux distributions).

**4. What is idempotency in Ansible?**

Idempotency means running an operation multiple times produces the same result as running it once. Ansible modules are designed to check existing state before making changes — the `apt` module checks whether a package is already installed before installing it. A properly written playbook can be run repeatedly without side effects.

**5. What is a template in Ansible?**

A template is a file containing variables replaced at runtime by the Jinja2 templating engine. Used with the `template` module to create configuration files customized per host or group:

```yaml
- name: Deploy nginx config
  template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
```

**6. What is an Ansible inventory file?**

An inventory file (INI or YAML format) defines the hosts Ansible manages. It organizes hosts into groups and can set host-specific or group-specific variables:

```ini
[webservers]
web1.example.com
web2.example.com

[dbservers]
db1.example.com
```

**7. What is the difference between push and pull configuration management?**

- **Push model:** A central server initiates and pushes changes to managed nodes. Ansible uses this — you run `ansible-playbook` and it SSHes to each target.
- **Pull model:** Managed nodes periodically pull configuration from a central server. Puppet and Chef use this model.

***

### System Design Perspective

**Push vs pull at scale:** Push works well up to a few hundred hosts. Beyond that, the control node becomes a bottleneck (SSH fan-out). Pull mode (ansible-pull) distributes execution — each host runs on its own schedule, pulling from Git. The tradeoff: pull mode is harder to audit (no central execution log) and harder to coordinate (no guaranteed simultaneous convergence).

**Ansible in a Terraform workflow:** Terraform provisions the EC2 instance (or VM, or container), outputs the IP address, and Ansible uses that IP as dynamic inventory. The handoff: Terraform outputs `instance_ip` → Ansible inventory uses it via `terraform_state` lookup or passed as `--inventory`. Each tool does what it does best: Terraform manages infrastructure lifecycle, Ansible manages software configuration.

**Idempotency as operational safety:** An idempotent playbook can be run by CI on every merge without fear. A non-idempotent playbook (using `shell` to append to a file) causes config drift on every run. The operational implication: only idempotent playbooks can be safely run on a schedule (nightly convergence runs), which is the pattern for drift correction at scale.


```
Ansible Intermediate Concepts (Interview: Medium)
├── Terraform + Ansible Workflow
│   ├── Terraform: provision EC2, VPC, SGs, RDS → infrastructure lifecycle
│   ├── Ansible: install packages, configure services, deploy code
│   └── Handoff: Terraform outputs IP → Ansible dynamic inventory
├── Idempotency Maintenance
│   ├── Use modules (apt, copy, file) → idempotent by design
│   ├── Avoid shell/command for state changes → not idempotent
│   ├── state: latest on packages → breaks idempotency (upgrades each run)
│   └── restarted vs reloaded on service → restarted always changes
├── Variable Precedence
│   ├── defaults/main.yml → lowest: intended to be overridden
│   ├── vars/main.yml → high: not meant to be overridden easily
│   ├── group_vars/ → per-group overrides (production vs staging)
│   ├── host_vars/ → per-host overrides
│   └── extra vars (-e) → always wins (operator escape hatch)
├── Ansible Vault
│   ├── Encrypts file or inline string with AES-256
│   ├── encrypt_string → embed encrypted value directly in playbook YAML
│   ├── vault-password-file → CI-friendly, avoids interactive prompt
│   └── Multiple vault IDs → different passwords for different secrets
├── Dynamic Inventory
│   ├── aws_ec2 plugin → queries EC2 DescribeInstances
│   ├── keyed_groups → group by tag, region, instance type
│   ├── filters → limit to specific env tag (env: production)
│   └── ansible-inventory --graph → visualize dynamic inventory tree
├── Role Dependencies
│   ├── meta/main.yml dependencies: [] → pulled in before this role runs
│   ├── requirements.yml → install Galaxy/Git roles before playbook run
│   └── Pinned versions: version: 2.1.0 in requirements.yml
├── Handlers
│   ├── Triggered by notify: in a task
│   ├── Run at end of play (not immediately)
│   ├── Deduplicated: 10 notifications → 1 handler execution
│   ├── flush_handlers: → force immediate execution mid-play
│   └── Only run if notifying task reported changed
└── import_tasks vs include_tasks
    ├── import_tasks: static → parsed at playbook load time, tags propagate
    └── include_tasks: dynamic → evaluated at runtime, tags don't propagate
```

### First Principles

- The Terraform + Ansible handoff separates concerns cleanly: Terraform is declarative and manages infrastructure lifecycle (create, update, destroy). Ansible is procedural and manages software lifecycle (install, configure, restart). Neither tool does the other's job well.
- Variable precedence exists because different actors have different authority. Role defaults are suggestions. Group vars are environment-specific settings. Extra vars are operator overrides. The precedence chain encodes organizational authority.
- Handlers exist because side effects should be reactive, not proactive. Restarting nginx because its config changed is correct. Restarting nginx even when nothing changed (a naive `service: state=restarted` in tasks) is wasteful and potentially disruptive. The `notify` mechanism ensures the side effect fires only when the triggering change actually occurred.
- `import_tasks` resolves at parse time — the tasks become part of the playbook before execution. This means `--tags` works across imported tasks. `include_tasks` resolves at runtime — tags specified on the `include_tasks` task don't propagate to the included tasks. This is a common source of confusion.

## Medium

**8. When would you use Ansible after Terraform in the same platform?**

Terraform provisions the infrastructure (EC2 instance, security groups, networking). Once the instance is running, Ansible configures the software: installing packages, deploying application code, setting up systemd services, and applying security hardening. Use this pattern when cloud-init/user-data is insufficient or when you need to re-run configuration without reprovisioning the instance.

**9. What makes an Ansible playbook idempotent and what breaks idempotency?**

Idempotency is maintained when tasks use Ansible modules (which check state before changing it). It is broken by `command:` and `shell:` tasks that are not guarded with `creates:`, `removes:`, or `changed_when:`/`when:` conditions. Raw commands like `echo "line" >> /etc/file` always report changed and always modify the file.

**10. What are `vars`, `defaults`, and `group_vars` and how does Ansible variable precedence work?**

`defaults/main.yml` in a role has the lowest precedence — easily overridden. `vars/main.yml` in a role has higher precedence than defaults. `group_vars/` files apply to hosts in a specific inventory group. `host_vars/` apply to individual hosts. Extra vars (`-e`) have the highest precedence. Understanding this hierarchy prevents unexpected variable overrides.

**11. How does Ansible handle secrets and sensitive data?**

Ansible Vault encrypts files or individual string variables using AES-256:

```bash
# Encrypt an entire file
ansible-vault encrypt vars/secrets.yml

# Inline encrypted value in a vars file
db_password: !vault |
  $ANSIBLE_VAULT;1.1;AES256
  ...
```

The vault password is provided at runtime via `--vault-password-file` or the `ANSIBLE_VAULT_PASSWORD_FILE` environment variable. In production, vault passwords come from a secrets manager or CI/CD secret store — not hardcoded.

**12. What is an Ansible dynamic inventory?**

A dynamic inventory is a script or plugin that queries a source of truth (AWS EC2 API, GCP Compute, Azure, a CMDB) at runtime to get the current list of hosts. Instead of a static file, Ansible calls the script at execution time — hosts appear and disappear automatically as infrastructure changes. AWS uses the `aws_ec2` inventory plugin; GCP uses `gcp_compute`.

**13. How do you manage role dependencies?**

Define dependencies in `meta/main.yml`:

```yaml
dependencies:
  - role: common
    vars:
      some_parameter: value
  - role: geerlingguy.ntp
    vars:
      ntp_timezone: UTC
```

For external roles from Galaxy, use `requirements.yml`:

```yaml
roles:
  - name: geerlingguy.ntp
    version: 2.3.2
```

Install with `ansible-galaxy install -r requirements.yml`. Version-pinning is essential for reproducible builds.

**14. What are Ansible handlers and when do you use them?**

Handlers are tasks triggered by `notify:` only when the notifying task reports `changed`. They run at the end of the play (or `flush_handlers`), deduplicated — even if five tasks notify the same handler, it runs once:

```yaml
tasks:
  - name: Update nginx config
    template:
      src: nginx.conf.j2
      dest: /etc/nginx/nginx.conf
    notify: Reload nginx

handlers:
  - name: Reload nginx
    service:
      name: nginx
      state: reloaded
```

***

### System Design Perspective

**Variable precedence as organizational governance:** In a multi-team environment, role defaults define the platform standard (e.g., `nginx_worker_processes: auto`). Team-specific overrides live in `group_vars/team-payments/vars.yml`. Production-specific overrides live in `group_vars/production/vars.yml`. This hierarchy mirrors the organizational authority: platform team sets defaults, application teams override for their service, operators override for specific environments.

**Dynamic inventory as the source of truth for ephemeral infra:** In auto-scaling environments, the host list changes constantly. Static inventory becomes stale within minutes. The `aws_ec2` plugin queries EC2 in real time — every `ansible-playbook` run sees the current host list. Combined with `keyed_groups` (group by `tag:role`), you get `webservers`, `dbservers`, `cacheservers` groups that always reflect reality.

**Handler deduplication as a safety mechanism:** In a large playbook where 15 different tasks might change nginx configuration (main config, virtual host files, SSL certificates, upstream definitions), naive "restart on every change" would restart nginx 15 times, briefly dropping connections each time. Handler deduplication ensures nginx restarts exactly once at the end of the play — all changes applied, one clean restart.

**Vault in multi-team setups:** Use multiple vault IDs (vault-id per team or per environment). Each team encrypts their own secrets with their own vault password. The platform team's vault password is not shared with application teams. In AWX, each team's vault password is stored as a separate Vault Credential, and job templates are configured with only the credentials they need.


---
description: Hard interview questions for Ansible — custom modules, AWX, performance at scale, and idempotency patterns.
---

```
Ansible Advanced Patterns (Interview: Hard)
├── Custom Module Development
│   ├── When: built-in modules don't support proprietary API or app commands
│   ├── Structure: Python script using AnsibleModule(argument_spec=...)
│   ├── Returns: exit_json(changed=True/False) or fail_json(msg=...)
│   ├── Placement: library/ in playbook dir or role → auto-discovered
│   └── Best practice: check current state → only act if needed (idempotent)
├── AWX / Automation Platform
│   ├── RBAC: team-scoped access to job templates (not global SSH access)
│   ├── Audit trail: persistent job log with user + timestamp + inventory
│   ├── Dynamic inventory: GUI-configured cloud sources, auto-synced
│   ├── Scheduling: built-in scheduler with job dependencies
│   ├── Credentials: encrypted vault, tokens never exposed to users
│   ├── Notifications: email/Slack/PagerDuty on job success/failure
│   ├── Workflow templates: visual if-success-then / if-fail-then chains
│   └── Execution Environments: containerized Ansible runtime (reproducible)
├── Performance at Scale (1000+ hosts)
│   ├── Forks: forks = 50 → parallel SSH connections (default 5)
│   ├── Pipelining: True → batch module steps in one SSH connection
│   ├── Mitogen: strategy plugin → 3-10x faster via multiplexed transport
│   ├── ansible-pull: hosts self-configure from Git (control node not bottleneck)
│   └── Fact caching: Redis/JSON → skip setup module on repeat runs
├── Rolling Updates (zero-downtime)
│   ├── serial: "25%" → process 25% of hosts at a time
│   ├── max_fail_percentage: 0 → stop on any host failure
│   ├── Steps: remove from LB → deploy → smoke test → add back to LB
│   └── Combined: safe progressive rollout with automatic abort
├── Inventory Types in AWX
│   ├── Static: fixed host list, manually maintained
│   ├── Dynamic: cloud plugin, synced at runtime
│   └── Smart: filter query over existing inventories (complex targeting)
├── Secrets Management (maturity levels)
│   ├── Ansible Vault → encrypt vars file or inline string (small teams)
│   ├── HashiCorp Vault lookup → short-lived tokens, nothing at rest in Ansible
│   ├── AWS SSM / Secrets Manager lookup → IAM-authenticated at runtime
│   └── AWX Vault Credentials → injected as env vars, never visible to authors
├── Idempotency Patterns
│   ├── Use modules over shell/command
│   ├── shell with creates: / removes: → conditional execution
│   ├── lineinfile / blockinfile → idempotent file editing
│   └── changed_when: false → mark read-only commands as never changed
└── Large Org Structure (20+ teams, 10+ environments)
    ├── inventories/ → per-environment with group_vars
    ├── roles/       → shared roles published to private Galaxy
    ├── playbooks/   → entry points per tier
    ├── collections/requirements.yml → pinned external collections
    └── AWX RBAC: team A templates only visible/runnable by team A
```

### First Principles

- A custom module is a Python function that receives structured arguments and returns structured JSON. The `AnsibleModule` wrapper handles argument parsing, error handling, and diff mode. The module author is responsible for making it idempotent — check current state, only change if needed, report `changed=True` only when a change occurred.
- AWX/Automation Platform is Ansible with organizational controls bolted on. The core execution is identical — it still SSHes to targets and runs playbooks. AWX adds: who can run what, when, against which inventory, with which credentials, and keeps a permanent record.
- Rolling updates with `serial` turn a simultaneous "stop the world" update into a controlled batch progression. The key insight: never update all hosts at once (zero capacity during update) and never update hosts faster than you can verify each batch is healthy.
- Mitogen replaces the SSH transport with a Python-based multiplexed connection. Instead of a new SSH process per task, Mitogen keeps a persistent Python interpreter on each target and sends bytecode to it. This eliminates SSH handshake overhead — the dominant cost in large playbooks.
- Fact caching separates fact gathering (slow, per-host setup module) from task execution (fast, per-task operations). Cache facts in Redis for 8 hours. Subsequent runs skip the setup phase entirely — dramatic speedup for frequent runs.

## Hard

**16. How do you write a custom Ansible module and when should you?**

Write a custom module when built-in modules don't support your use case (proprietary API, custom application commands) and `command`/`shell` would be non-idempotent.

A custom module is a Python script that:
1. Reads arguments via `AnsibleModule(argument_spec=...)`
2. Performs the action
3. Returns `module.exit_json(changed=True/False, ...)` or `module.fail_json(msg=...)`

```python
#!/usr/bin/python
from ansible.module_utils.basic import AnsibleModule

def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=True),
            state=dict(type='str', choices=['present', 'absent'], default='present'),
        )
    )
    name = module.params['name']
    # Check current state
    exists = check_resource(name)
    if module.params['state'] == 'present' and not exists:
        create_resource(name)
        module.exit_json(changed=True, msg=f"Created {name}")
    else:
        module.exit_json(changed=False, msg="Already present")

if __name__ == '__main__':
    main()
```

Place in `library/` in the playbook directory or role — Ansible discovers it automatically.

**17. How does AWX/Ansible Controller differ from running Ansible directly and what problems does it solve?**

AWX (open-source) / Ansible Automation Platform (commercial) adds an enterprise control plane on top of Ansible:

| Feature | ansible-playbook CLI | AWX/Controller |
|:---|:---|:---|
| **RBAC** | No access control — anyone who can SSH can run | Role-based — users get access to specific job templates |
| **Audit trail** | Terminal output | Persistent job log, user, timestamp, inventory used |
| **Dynamic inventory** | Manual scripting | GUI-configured inventory sources syncing from AWS, GCP, etc. |
| **Scheduling** | Cron on a host | Built-in scheduler with dependencies |
| **Credentials** | SSH keys in files | Encrypted credential vault; tokens never exposed to users |
| **Notifications** | Manual | Email, Slack, PagerDuty on job success/failure |
| **Workflow templates** | Manual chaining | Visual workflow builder: if job A succeeds → job B, else job C |

AWX is required when: multiple teams run Ansible across many environments, audit compliance is needed, or you want to give non-engineers the ability to trigger pre-approved playbooks.

**18. How do you handle Ansible performance at scale (1000+ hosts)?**

- **Forks:** Increase `forks = 50` (or higher) in `ansible.cfg` — Ansible runs tasks on this many hosts simultaneously.
- **Pipelining:** Enable `pipelining = True` to reduce SSH round trips by executing multiple modules in a single SSH connection.
- **Mitogen:** Ansible plugin that replaces the default SSH-based transport with a fast multiplexed transport — often 5-10x faster.
- **Pull mode (ansible-pull):** Each host runs `ansible-pull` from a Git repository on a cron, distributing the execution — the controller is not the bottleneck.
- **Fact caching:** Cache `setup` facts in Redis or a JSON file to avoid redundant fact gathering on repeated runs.

**19. How do you implement a rolling update with Ansible for zero-downtime deployments?**

Use `serial` to control how many hosts Ansible processes at once:

```yaml
- hosts: webservers
  serial: "25%"  # update 25% of hosts at a time
  tasks:
    - name: Remove from load balancer
      # deregister from LB
    - name: Deploy new application version
      # deploy steps
    - name: Run smoke tests
      # validate
    - name: Add back to load balancer
      # re-register
```

Combined with `max_fail_percentage: 0`, if any host in the batch fails, the play stops and remaining hosts are not updated — limiting blast radius.

**20. What is the difference between `static` and `smart` inventory in AWX?**

- **Static Inventory:** A fixed list of hosts and groups defined manually in AWX or imported from a file. Does not update automatically.
- **Dynamic Inventory:** A script or plugin querying a cloud provider API at runtime to get the current host list.
- **Smart Inventory (AWX feature):** An inventory whose hosts are dynamically populated based on a filter query against other existing inventories. Example: "all hosts in the `webservers` group AND tagged `production` AND with a failed job in the last 24 hours." This enables complex targeting without writing custom scripts.

**21. How do you manage secrets in Ansible without hardcoding them in variables?**

Multiple approaches in order of maturity:

1. **Ansible Vault:** Encrypts variables files or individual values with a password. `ansible-vault encrypt_string 'my_password'` embeds an encrypted string in a playbook. The vault password is provided at run time via `--vault-password-file` or `ANSIBLE_VAULT_PASSWORD_FILE`. Good for small teams.

2. **HashiCorp Vault lookup:** Use the `community.hashi_vault.hashi_vault` lookup plugin:
   ```yaml
   db_password: "{{ lookup('community.hashi_vault.hashi_vault', 'secret/db password') }}"
   ```
   Vault issues short-lived tokens; no secrets stored in Ansible at rest.

3. **AWS Secrets Manager / Parameter Store lookup:** Use `aws_ssm` or `aws_secret` lookup plugins to fetch values at runtime from AWS. Works well if your Ansible control node already has IAM credentials.

4. **External variable injection:** In AWX/Controller, define credentials as Vault Credentials — they inject values as environment variables at job runtime; playbook authors never see the raw values.

**22. Explain how Ansible handles idempotency and what makes a task non-idempotent.**

Idempotency means running the same playbook multiple times produces the same end state, with no unnecessary changes. Ansible modules handle this: the `apt` module checks if a package is installed before installing; `copy` compares file checksums before copying; `file` checks the current permissions before changing.

**Non-idempotent patterns to avoid:**
```yaml
# BAD: always runs, always reports changed
- shell: echo "hello" >> /tmp/log.txt

# BETTER: check state first
- shell: echo "hello" >> /tmp/log.txt
  args:
    creates: /tmp/log.txt   # skip if file exists

# BEST: use a module that handles state
- lineinfile:
    path: /tmp/log.txt
    line: "hello"
    create: yes
```

Custom `command`/`shell` tasks with `changed_when: false` tell Ansible the task never causes a change — use when the command is genuinely read-only.

**23. How do you structure Ansible for a large organization with 20+ teams and 10+ environments?**

Repository and role structure:
```
ansible/
├── inventories/
│   ├── production/
│   │   ├── hosts.yml         # Or dynamic inventory script
│   │   └── group_vars/
│   │       ├── all.yml
│   │       └── webservers.yml
│   └── staging/
│       └── ...
├── roles/
│   ├── common/               # Applied to all hosts
│   ├── webserver/            # Applied to web tier
│   └── database/
├── playbooks/
│   ├── site.yml              # Full stack deployment
│   ├── webservers.yml        # Web tier only
│   └── rolling-update.yml
└── collections/
    └── requirements.yml      # External collections to install
```

Governance:
- Shared roles published to a private Ansible Galaxy or Automation Hub.
- Teams consume shared roles via `collections/requirements.yml` with pinned versions.
- Each team manages their own `group_vars` for environment-specific overrides.
- AWX template permissions: team A can only run templates for their services.

***

### System Design Perspective

**Custom modules as a platform abstraction layer:** Platform teams write custom modules for internal systems (internal deployment API, proprietary monitoring registration, custom DNS). Application teams use `- my_org.platform.register_service:` without knowing the API details. This is the Ansible equivalent of a Terraform provider — a typed, idempotent interface to a system that doesn't have a built-in module.

**AWX Execution Environments as the reproducibility solution:** Different playbooks require different Python packages and Ansible collection versions. Without Execution Environments, the AWX control node accumulates conflicting dependencies over time. With EEs: each job template specifies an OCI container image with its exact Ansible version, collections, and Python packages. Build EEs with `ansible-builder`, publish to a registry, pin the image tag in AWX.

**Rolling updates as progressive delivery for configuration changes:** The `serial: "25%"` pattern is Ansible's version of a canary deployment. If the smoke test fails for the first 25% batch, `max_fail_percentage: 0` stops the play — 75% of hosts are still on the old version. This limits blast radius to 25% of capacity, not 100%. The same pattern applies to OS patching, certificate rotation, and configuration changes.

**Ansible-pull for ASG environments:** In an AWS ASG, new instances appear without warning. ansible-push (control node SSHes out) requires knowing the IP of the new instance. ansible-pull solves this: cloud-init on the new instance runs `ansible-pull -U <git-repo>` at boot. The instance configures itself. The control node never needs to initiate contact. The tradeoff: no central audit log of what ran on which instance, and convergence timing is controlled by the instance's cron interval, not the operator.

**Fact caching architecture at scale:** With 5000 hosts, fact gathering alone takes 10+ minutes (even with forks=100). Cache facts in Redis with an 8-hour TTL. First run of the day: gather facts and populate cache. Subsequent runs: `gather_facts: false` globally, load from cache with `cache_plugin: redis`. This reduces a 4-hour playbook to under 30 minutes for subsequent runs.
