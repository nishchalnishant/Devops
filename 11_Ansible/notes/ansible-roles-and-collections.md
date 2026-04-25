---
description: Ansible roles, collections, Galaxy, and enterprise-scale automation patterns for senior engineers.
---

# Ansible — Roles, Collections & Enterprise Patterns

## The Problem with Large Playbooks

A 2,000-line monolithic playbook is:
- **Impossible to test** in isolation
- **Dangerous to reuse** across teams
- **Slow to execute** (no parallelism granularity)
- **Hard to maintain** (no versioning per component)

**Roles** solve this by enforcing a standard directory structure.

***

## Role Structure

```
roles/
└── nginx/
    ├── defaults/
    │   └── main.yml      ← Default variable values (lowest precedence)
    ├── vars/
    │   └── main.yml      ← Role-specific vars (high precedence, not overridable)
    ├── tasks/
    │   └── main.yml      ← The actual tasks (entry point)
    ├── handlers/
    │   └── main.yml      ← Handlers (e.g., restart nginx)
    ├── templates/
    │   └── nginx.conf.j2 ← Jinja2 templates
    ├── files/
    │   └── ssl_cert.pem  ← Static files to copy
    ├── meta/
    │   └── main.yml      ← Role metadata (dependencies, author)
    └── tests/
        └── test.yml      ← Molecule test playbook
```

### `tasks/main.yml`
```yaml
---
- name: Install nginx
  package:
    name: nginx
    state: present

- name: Configure nginx
  template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
    mode: '0644'
  notify: Restart nginx          # Trigger handler only if this task changes

- name: Ensure nginx is running
  service:
    name: nginx
    state: started
    enabled: yes
```

### `handlers/main.yml`
```yaml
---
- name: Restart nginx
  service:
    name: nginx
    state: restarted
  listen: "Restart nginx"        # Can be notified by name or listen label
```

### `defaults/main.yml`
```yaml
---
nginx_worker_processes: auto
nginx_worker_connections: 1024
nginx_keepalive_timeout: 65
nginx_log_format: combined
```

***

## Using Roles in a Playbook

```yaml
# site.yml
---
- name: Configure web servers
  hosts: webservers
  become: yes

  roles:
    - role: common           # Apply base OS hardening role first
    - role: nginx
      vars:
        nginx_worker_processes: 4   # Override role default
    - role: certbot
      when: ansible_os_family == "Debian"
```

***

## Ansible Collections

Collections are the packaging format for distributing multiple roles, modules, and plugins together.

```bash
# Install a collection from Ansible Galaxy
ansible-galaxy collection install community.kubernetes

# Install from requirements file (pin versions!)
ansible-galaxy collection install -r requirements.yml
```

**`requirements.yml`:**
```yaml
---
collections:
  - name: community.kubernetes
    version: ">=2.4.0,<3.0.0"
  - name: amazon.aws
    version: "6.0.0"
  - name: https://github.com/org/my-private-collection.git
    type: git
    version: main

roles:
  - name: geerlingguy.docker
    version: "6.1.0"
```

**Using a collection module:**
```yaml
- name: Deploy app to Kubernetes
  kubernetes.core.k8s:       # collection.namespace.module
    state: present
    definition:
      apiVersion: apps/v1
      kind: Deployment
      # ...
```

***

## Molecule — Testing Roles

Molecule is the standard framework for testing Ansible roles in isolated containers or VMs.

```bash
# Initialize molecule in an existing role
cd roles/nginx
molecule init scenario --driver-name docker

# Test cycle
molecule create      # Create test container
molecule converge    # Run the role
molecule verify      # Run assertion tests (testinfra or ansible)
molecule destroy     # Tear down
molecule test        # Full test cycle (all above)
```

**`molecule/default/verify.yml`:**
```yaml
---
- name: Verify nginx is installed and running
  hosts: all
  tasks:
    - name: Check nginx service is running
      service_facts:
    
    - name: Assert nginx is active
      assert:
        that:
          - "'nginx' in services"
          - "services['nginx'].state == 'running'"
    
    - name: Check nginx port 80 is listening
      wait_for:
        port: 80
        timeout: 5
```

***

## Performance: Mitogen Strategy

**Default Ansible SSH:** 50 hosts × 10 tasks = 500 SSH connections. Slow.

**Mitogen:** Establishes one SSH connection per host, runs all tasks over that connection using Python RPC. **3-7x faster.**

```ini
# ansible.cfg
[defaults]
strategy_plugins = /path/to/mitogen/ansible_mitogen/plugins/strategy
strategy         = mitogen_linear
```

***

## Logic & Trickiness Table

| Pattern | Junior Approach | Senior Approach |
|:---|:---|:---|
| **Variable precedence** | Put vars everywhere | Know the 22-level precedence order; use `defaults/` for tunables, `vars/` for constants |
| **Idempotency** | Assume tasks are idempotent | Test with `molecule`; use `creates:`, `removes:`, `check_mode:` |
| **Secrets** | Plaintext in vars files | `ansible-vault encrypt_string` or Vault lookup plugin |
| **Large inventories** | Static INI file | Dynamic inventory plugin (AWS EC2, GCP, K8s) |
| **Performance** | Default forks=5 | Increase forks, use `mitogen`, use `async` for long tasks |
| **Error handling** | Let playbook fail | `ignore_errors: yes` for non-critical, `block/rescue/always` for complex flows |
