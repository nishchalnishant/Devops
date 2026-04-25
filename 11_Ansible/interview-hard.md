---
description: Hard interview questions for Ansible — custom modules, AWX, performance at scale, and idempotency patterns.
---

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
