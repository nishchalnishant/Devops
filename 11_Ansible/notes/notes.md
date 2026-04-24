# Ansible — Deep Dive Notes

## Architecture Internals

Ansible is agentless — it connects over SSH (Linux) or WinRM (Windows) from the control node, runs modules on the remote node, then tears down the connection.

```
Control Node (ansible-playbook)
    │
    ├── Reads inventory (static file / dynamic plugin)
    ├── Compiles plays into task lists
    ├── Forks N workers (--forks, default 5)
    │       Each fork handles one host
    │
    └── For each task, each fork:
            1. Renders the module as a Python script (or binary)
            2. Copies it to the remote via SFTP/SCP (or pipelining)
            3. Executes it over SSH
            4. Reads stdout JSON result
            5. Removes temp file (unless ANSIBLE_KEEP_REMOTE_FILES=1)
```

**Pipelining** (strongly recommended): skips the copy step by piping the module code over the SSH connection's stdin. Requires `requiretty` disabled in `/etc/sudoers` on the remote.

```ini
# ansible.cfg
[ssh_connection]
pipelining = True
```

### Connection plugins

| Plugin | Transport | Use case |
|--------|-----------|----------|
| `ssh` (default) | OpenSSH | Linux targets |
| `paramiko` | Python SSH | Fallback when OpenSSH unavailable |
| `winrm` | WinRM/HTTP(S) | Windows targets |
| `local` | subprocess | Localhost, CI containers |
| `docker` | docker exec | Docker containers without SSH |
| `kubectl` | kubectl exec | Kubernetes pods |

***

## Inventory Deep Dive

### Static inventory patterns

```ini
# inventory/hosts.ini
[webservers]
web-[01:10].prod.example.com   ansible_user=ubuntu

[databases]
db-primary.prod.example.com   ansible_host=10.0.1.5
db-replica-[1:3].prod.example.com

[prod:children]
webservers
databases

[prod:vars]
ansible_ssh_private_key_file=~/.ssh/prod_key
ansible_python_interpreter=/usr/bin/python3
```

### Dynamic inventory (EC2 example)

```bash
# Install plugin
pip install boto3 botocore

# inventory/aws_ec2.yml
plugin: amazon.aws.aws_ec2
regions: [us-east-1, us-west-2]
filters:
  instance-state-name: running
  tag:Env: production
keyed_groups:
  - prefix: ec2
    key: tags.Role               # creates group ec2_webserver, ec2_database, etc.
  - prefix: az
    key: placement.availability_zone
hostnames:
  - tag:Name
  - private-ip-address          # fallback
compose:
  ansible_host: private_ip_address  # use private IPs
  ansible_user: "'ubuntu'"

# Test
ansible-inventory -i inventory/aws_ec2.yml --list
ansible-inventory -i inventory/aws_ec2.yml --graph
```

### Inventory variable precedence (lowest to highest)

1. `group_vars/all`
2. `group_vars/<group>`
3. `group_vars/<child_group>`
4. `host_vars/<host>`
5. Inventory file vars
6. Connection vars (`ansible_host`, `ansible_user`)
7. Playbook `vars:` block
8. `vars_files:`
9. `set_fact`
10. `--extra-vars` / `-e` (highest)

***

## Role Structure

```
roles/
└── my_app/
    ├── defaults/        # lowest precedence vars (overridable by anything)
    │   └── main.yml
    ├── vars/            # higher precedence vars (not for overriding)
    │   └── main.yml
    ├── tasks/
    │   ├── main.yml
    │   └── setup.yml    # imported by main.yml
    ├── handlers/
    │   └── main.yml
    ├── templates/       # Jinja2 .j2 files
    │   └── nginx.conf.j2
    ├── files/           # static files for copy: module
    ├── meta/
    │   └── main.yml     # dependencies, galaxy info
    └── tests/
        ├── inventory
        └── test.yml
```

**`defaults/` vs `vars/`:** defaults are designed to be overridden by inventory/playbook vars. `vars/` in a role have higher precedence than playbook `vars:` blocks — don't put overridable config there.

***

## Task Execution Model

```yaml
- hosts: webservers
  gather_facts: true     # runs setup module, populates ansible_facts
  become: true           # sudo
  serial: "25%"          # rolling update: 25% of hosts at a time
  max_fail_percentage: 10  # abort if >10% of hosts fail
  any_errors_fatal: false

  pre_tasks:
    - name: check disk space
      assert:
        that: ansible_mounts | selectattr('mount', 'equalto', '/') | map(attribute='size_available') | first > 1073741824
        fail_msg: "Less than 1GB free on /"

  roles:
    - role: my_app
      tags: [deploy]
      vars:
        app_version: "{{ lookup('env', 'APP_VERSION') }}"

  post_tasks:
    - name: verify service
      uri:
        url: "http://{{ ansible_default_ipv4.address }}/health"
        status_code: 200
      retries: 5
      delay: 10

  handlers:
    - name: restart nginx
      service:
        name: nginx
        state: restarted
      listen: "reload web"    # handlers can have a topic name
```

### import vs include

| Keyword | Evaluated | Tags/When | Use when |
|---------|-----------|-----------|----------|
| `import_tasks` | parse time (static) | tags/when on import apply to all children | task list known at write time |
| `include_tasks` | runtime (dynamic) | tags/when on include do NOT propagate | file path depends on a variable |
| `import_role` | parse time | role tags work | standard role inclusion |
| `include_role` | runtime | must tag tasks inside role explicitly | conditional role inclusion |

```yaml
# Critical gotcha: tags on include_tasks don't propagate
- include_tasks: setup.yml
  tags: [setup]              # tasks inside setup.yml are NOT tagged 'setup'

# Workaround: use apply
- include_tasks: setup.yml
  apply:
    tags: [setup]
  tags: [setup]              # need both: one for the include itself, one for children
```

***

## Vault — Encryption Internals

```bash
# Encrypt a file
ansible-vault encrypt group_vars/prod/secrets.yml --vault-password-file .vault_pass

# Encrypt a single value (inline in playbook)
ansible-vault encrypt_string 'my_secret_value' --name 'db_password'
# Outputs:
# db_password: !vault |
#   $ANSIBLE_VAULT;1.1;AES256
#   ...

# Multiple vault IDs (different passwords per environment)
ansible-vault encrypt --vault-id prod@.vault_pass_prod secrets_prod.yml
ansible-vault encrypt --vault-id dev@.vault_pass_dev secrets_dev.yml

# Run with multiple vault IDs
ansible-playbook site.yml --vault-id prod@.vault_pass_prod --vault-id dev@.vault_pass_dev
```

**Vault ID in `ansible.cfg`:**
```ini
[defaults]
vault_identity_list = prod@/run/secrets/vault_pass_prod, dev@.vault_pass_dev
```

***

## Performance Tuning

```ini
# ansible.cfg
[defaults]
forks = 50                  # parallel host workers (default: 5)
gathering = smart           # cache facts; only re-gather if cache expired
fact_caching = jsonfile
fact_caching_connection = /tmp/ansible_facts
fact_caching_timeout = 3600 # 1 hour
host_key_checking = False   # disable for dynamic cloud environments
timeout = 30

[ssh_connection]
pipelining = True
ssh_args = -o ControlMaster=auto -o ControlPersist=60s -o ServerAliveInterval=30
# ControlMaster: reuse SSH connections across tasks (huge speedup)
```

**ControlMaster** multiplexes multiple SSH sessions over one TCP connection. A 50-task playbook on 100 hosts goes from 5000 SSH handshakes to 100 with ControlMaster.

***

## Callback Plugins

```ini
# ansible.cfg
[defaults]
stdout_callback = yaml          # readable output
callbacks_enabled = timer, profile_tasks, mail
# Note: pre-2.9 this was 'callback_whitelist'
```

| Callback | Purpose |
|----------|---------|
| `yaml` | Human-readable output (default is `default`) |
| `json` | Machine-parseable; pipe to `jq` in CI |
| `timer` | Print total playbook duration at end |
| `profile_tasks` | Print per-task duration — find slow tasks |
| `profile_roles` | Per-role duration |
| `mail` | Email on failure |
| `slack` | Post results to Slack |
| `logstash` | Emit to ELK |

```yaml
# Custom callback — save to file (useful in CI)
# ansible.cfg
stdout_callback = json
# In CI:
ansible-playbook site.yml | tee ansible-output.json
```

***

## Parallelism and Concurrency Patterns

```yaml
# serial: rolling update control
- hosts: webservers
  serial: 1                # one at a time
  # serial: "25%"          # 25% of hosts simultaneously
  # serial: [1, 5, "100%"] # ramp: first 1 host, then 5, then all

# throttle: limit concurrency for a specific task (not all tasks)
- name: restart database
  service:
    name: postgresql
    state: restarted
  throttle: 1              # only 1 host at a time for THIS task, regardless of forks

# run_once: run on exactly one host in the group
- name: run database migration
  command: /app/migrate.sh
  run_once: true
  delegate_to: db-primary.prod.example.com   # and specifically this host

# delegate_to: execute on a different host
- name: remove from load balancer
  uri:
    url: "http://lb.internal/api/drain/{{ inventory_hostname }}"
    method: POST
  delegate_to: localhost   # run from control node, targeting this URL
```

***

## Jinja2 Templating — Advanced Patterns

```yaml
# Filter chaining
"{{ my_list | select('match', '^web') | list | sort | first }}"

# Conditional default
"{{ my_var | default('fallback') }}"

# Loop with index
- debug:
    msg: "Item {{ idx }}: {{ item }}"
  loop: "{{ my_list }}"
  loop_control:
    index_var: idx
    label: "{{ item.name }}"   # keep output concise

# Dict iteration
- debug:
    msg: "{{ key }} = {{ value }}"
  loop: "{{ my_dict | dict2items }}"
  loop_control:
    loop_var: kv
  vars:
    key: "{{ kv.key }}"
    value: "{{ kv.value }}"

# Conditionals
- name: configure for RHEL
  include_tasks: rhel.yml
  when:
    - ansible_os_family == "RedHat"
    - ansible_distribution_major_version | int >= 8

# lookup plugins
- name: read a local file
  debug:
    msg: "{{ lookup('file', 'local_config.json') | from_json }}"

- name: fetch a secret from AWS SSM
  set_fact:
    db_pass: "{{ lookup('amazon.aws.aws_ssm', '/prod/db/password', region='us-east-1') }}"
```

***

## AWX / Automation Controller (Tower)

```
AWX Architecture:
┌─────────────────────────────────────────────────┐
│  AWX UI / REST API                              │
│  ┌──────────────┐  ┌──────────────────────────┐ │
│  │  Web (Django)│  │  Task Manager (Celery)   │ │
│  │  + DRF API   │  │  Schedules, workflows    │ │
│  └──────────────┘  └──────────────────────────┘ │
│  ┌──────────────┐  ┌──────────────────────────┐ │
│  │  Redis       │  │  PostgreSQL              │ │
│  │  (task queue)│  │  (jobs, inventory, creds)│ │
│  └──────────────┘  └──────────────────────────┘ │
└─────────────────────────────────────────────────┘
         │
         ▼ launches ansible-playbook process
    Execution Environments (EE)
    OCI container images with Ansible + collections
```

**Execution Environments:** Replace the classic "virtualenv per project" model. Each EE is a container image built with `ansible-builder` that bundles a specific Ansible version + collections + Python dependencies.

```yaml
# execution-environment.yml
version: 1
build_arg_defaults:
  EE_BASE_IMAGE: 'quay.io/ansible/ansible-runner:latest'
dependencies:
  galaxy: requirements.yml
  python: requirements.txt
  system: bindep.txt
```

```bash
ansible-builder build -t myorg/my-ee:1.0 --container-runtime docker
```

### Key AWX concepts

| Concept | Description |
|---------|-------------|
| Inventory | Host groups, synced from dynamic sources |
| Credential | SSH keys, vault passwords, cloud creds — encrypted at rest |
| Job Template | Playbook + inventory + credential bound together |
| Workflow Template | DAG of job templates with success/failure branching |
| Survey | Runtime variable prompts for job templates |
| Schedule | Cron-based job template execution |
| RBAC | Organizations → Teams → Users with granular permissions |

***

## Molecule — Testing Roles

```bash
# Initialize a molecule scenario
molecule init scenario --driver-name docker

# molecule/default/molecule.yml
platforms:
  - name: ubuntu-22
    image: geerlingguy/docker-ubuntu2204-ansible:latest
    command: /lib/systemd/systemd
    volumes:
      - /sys/fs/cgroup:/sys/fs/cgroup:rw
    cgroupns_mode: host
    privileged: true

# Run the full test matrix
molecule test

# Steps: destroy → create → converge → idempotency → verify → destroy
# Idempotency: runs converge twice; fails if second run shows changes
```

```yaml
# molecule/default/verify.yml
- name: verify
  hosts: all
  tasks:
    - name: nginx is running
      service_facts:
    - assert:
        that: "'nginx' in ansible_facts.services"
    - name: nginx serves health endpoint
      uri:
        url: http://localhost/health
        status_code: 200
```

***

## Key Gotchas

| Gotcha | Detail |
|--------|--------|
| `gather_facts: false` breaks many conditions | `ansible_os_family`, `ansible_distribution` etc. are undefined — tasks using them silently skip |
| `changed_when: false` is not `failed_when` | A task with `changed_when: false` always reports OK but still fails on non-zero exit code |
| Handler deduplication | If notified multiple times in a play, a handler runs only once — at the end of the play |
| `import_tasks` tags apply to children | `include_tasks` tags do NOT propagate to child tasks without `apply:` |
| `serial` does not affect handler execution | Handlers still run after each batch, not at the very end of all batches |
| `become: true` with pipelining | Requires `requiretty` disabled in `/etc/sudoers`; otherwise SSH sessions hang |
| Variable type coercion | YAML `"1"` is a string, `1` is an int. `{{ my_port | int }}` prevents `"8080" + 1` = `"80801"` |
| `loop` vs `with_items` | `with_items` flattens one level; `loop` does not. Use `loop` + `flatten(1)` filter for equivalence |
| `when` on `include_tasks` | The `when` condition runs on the control node before inclusion; variables from set_fact inside the include are not yet available |
| Vault-encrypted `defaults/` | Encrypting `defaults/main.yml` works but kills role reusability — prefer `group_vars/prod/secrets.yml` |
