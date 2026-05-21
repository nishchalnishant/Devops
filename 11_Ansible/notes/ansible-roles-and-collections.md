---
description: Ansible roles, collections, Galaxy, and enterprise-scale automation patterns for senior engineers.
---

# Ansible — Roles, Collections & Enterprise Patterns

```
Ansible Roles, Collections & Enterprise Patterns
├── Problem with Large Playbooks
│   ├── Impossible to test in isolation
│   ├── Cannot be reused across projects
│   ├── Variables and tasks in one file → naming collisions
│   └── Solution: roles (structured, testable, reusable units)
├── Role Structure
│   ├── defaults/main.yml  → lowest-precedence defaults (document here)
│   ├── vars/main.yml      → high-precedence internal variables
│   ├── tasks/main.yml     → entry point, imports sub-task files
│   ├── handlers/main.yml  → triggered-only-on-change tasks
│   ├── templates/         → Jinja2 .j2 config file templates
│   ├── files/             → static files (copy, not template)
│   └── meta/main.yml      → Galaxy metadata + role dependencies
├── Using Roles in Playbooks
│   ├── roles: [common, nginx, app]  → classic syntax
│   ├── include_role: → dynamic (runtime), no tag propagation
│   └── import_role: → static (parse time), tags propagate
├── Ansible Collections
│   ├── Bundle: modules + plugins + roles + playbooks
│   ├── Namespace: community.general, amazon.aws, kubernetes.core
│   ├── Install: ansible-galaxy collection install -r requirements.yml
│   ├── Version pin: version: "7.5.0" in requirements.yml
│   └── Execution Environment: collections pre-bundled in container
├── Molecule Testing
│   ├── molecule init scenario → scaffold test structure
│   ├── molecule converge → run playbook against container/VM
│   ├── molecule idempotency → run again, assert no changes
│   ├── molecule verify → run assertions (testinfra/ansible asserts)
│   └── molecule destroy → clean up instances
├── Mitogen Strategy Plugin
│   ├── Replaces SSH transport with multiplexed Python connection
│   ├── config: strategy_plugins = /path/to/mitogen + strategy = mitogen_linear
│   └── Effect: 3-10x faster playbook execution (no SSH per task)
└── Logic & Trickiness
    ├── defaults vs vars: defaults are overridable, vars are not (easily)
    ├── meta/dependencies run before role tasks (not after)
    ├── handlers in role are scoped to that role unless flushed
    └── Collection module names: FQCN required (amazon.aws.ec2_instance)
```

## First Principles

- A role is a module in the software engineering sense: it has a defined interface (variables in `defaults/main.yml`), an implementation (tasks), and side effects controlled through handlers. Callers don't care how nginx is configured — they just include the `nginx` role and pass variables.
- `defaults/main.yml` is the documentation of a role's API. Every variable the role supports should be declared here with a sensible default and a comment explaining its purpose. This file is the contract between the role author and the role consumer.
- Collections are the packaging unit for Ansible content distribution. A collection namespace (`amazon.aws`) ensures module names don't collide across vendors. FQCN (`amazon.aws.ec2_instance`) disambiguates module calls — critical in large playbooks that use multiple collections.
- Molecule tests a role in isolation: it creates a fresh container, runs the role against it, verifies the expected state, and destroys it. This is the unit test equivalent for infrastructure configuration. Idempotency testing (run twice, assert no changes on second run) catches non-idempotent tasks before they reach production.
- Mitogen works by establishing a persistent Python interpreter on each target at connection time and sending bytecode to it. This bypasses the per-task SSH handshake overhead — the dominant cost in Ansible's default transport.

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

***

## System Design Perspective

**Private role/collection registry as an internal platform:**
- Platform teams publish shared roles (`common`, `hardening`, `monitoring-agent`) to a private Ansible Galaxy (Automation Hub) or a Git monorepo with semantic version tags.
- Application teams pin versions in `requirements.yml`: `version: 2.3.1`. This creates the same versioned dependency model as Python packages or Terraform modules. Breaking changes bump the major version; consumers opt in to upgrades.
- The platform team owns `defaults/main.yml` (the API contract). Application teams own their `group_vars` overrides. Neither team needs to understand the other's internals.

**Execution Environments as reproducible runtimes:**
- Without EEs: the AWX control node's Python environment accumulates conflicting collection versions over time. Job A needs `kubernetes.core: 2.3`, Job B needs `kubernetes.core: 3.1`. Both can't coexist in the same Python env.
- With EEs: each job template specifies an OCI container image. `ansible-builder` packages the exact Ansible version, collections, and Python packages into the image. The image is pinned by digest in AWX. No dependency conflicts, fully reproducible, upgradeable without affecting other job templates.

**Molecule in CI pipeline:**
- PR → `molecule test` (full: lint → create → converge → idempotency → verify → destroy) → merge gate.
- Linting: `ansible-lint` catches style and correctness issues (deprecated modules, missing `name:`, `changed_when` missing on shell tasks).
- Idempotency: second converge run must produce zero `changed` tasks. This is the automated check that replaces "trust the author."
- The `verify` stage runs assertions against the converged instance: `package nginx is installed`, `port 80 is listening`, `nginx.conf contains expected line`. These are functional tests, not just "did the playbook run without errors."

**Collection FQCN as namespace governance:**
- Using FQCN (`amazon.aws.ec2_instance` instead of `ec2_instance`) prevents module name collisions when multiple collections provide similarly-named modules. It also makes `ansible-doc amazon.aws.ec2_instance` work correctly.
- In large organizations with custom collections, namespace them: `myorg.platform.register_service`. This distinguishes internal modules from community modules and prevents naming conflicts as the community collection ecosystem grows.
