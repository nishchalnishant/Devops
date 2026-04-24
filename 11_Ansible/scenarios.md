# Production Scenarios & Troubleshooting Drills (Senior Level)

### Scenario 1: Performance at Scale (1000+ Hosts)
**Problem:** Playbook takes 4 hours to run.
**Fix:** Enable **SSH Pipelining**, increase **Forks** to 100, and use the `mitogen` strategy plugin for 3x speed.

### Scenario 2: Idempotency Testing with Molecule
**Problem:** You aren't sure if your playbook is truly idempotent (it might change something every time).
**Fix:** Use **Molecule** to run the playbook twice in a test container. The second run should report `changed=0`.

### Scenario 3: Ansible-Pull for Auto-Scaling
**Problem:** You have an Auto Scaling Group; how do you configure new instances as they spin up?
**Fix:** Use `ansible-pull` in the UserData. Each instance pulls the latest playbook from Git and runs it locally on itself.

---

## Scenario 1: SSH Fingerprint Verification Failure
**Symptom:** Ansible fails to connect to 100 new servers with "Host key verification failed".
**Diagnosis:** The new servers are not in the `known_hosts` file of the Ansible controller.
**Fix:** 
1. Set `export ANSIBLE_HOST_KEY_CHECKING=False` (Only for initial provisioning).
2. Use a dynamic inventory that handles key updates.

## Scenario 2: Non-Idempotent Playbook causing Downtime
**Symptom:** Running the playbook again restarts Nginx even when no config changed.
**Diagnosis:** The `template` task is using a variable that changes every time (like a timestamp), or the `command` task is not using `creates:`.
**Fix:** Ensure tasks are idempotent. Use `notify` and `handlers` for restarts so they only trigger on change.


### Scenario 3: Ansible "Fork" exhaustion
**Symptom:** Running a playbook on 1000 nodes takes forever.
**Diagnosis:** The default `forks=5` means Ansible only talks to 5 nodes at a time.
**Fix:** Increase forks in `ansible.cfg`: `forks = 50`. Use the `mitogen` strategy for faster execution.

---

### Scenario 4: Idempotency Broken — Role Re-Installs Package on Every Run

**Problem:** An Ansible role that installs and configures nginx is run nightly by a scheduled job. Every run reports `changed: [host]` for the nginx service restart handler, triggering a 10-second service interruption on production hosts.

**Diagnosis:**
```yaml
# Problematic task
- name: Install nginx
  apt:
    name: nginx
    state: latest   # "latest" always checks for updates — nearly always reports "changed"

- name: Copy nginx config
  template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
  notify: Restart nginx

# Handler
- name: Restart nginx
  service:
    name: nginx
    state: restarted   # "restarted" always restarts, even if not notified
```

**Fixes:**

1. **`state: present` instead of `state: latest`** — only installs if not present; no change if already installed:
```yaml
- name: Install nginx
  apt:
    name: nginx=1.24.*   # pin version for reproducibility
    state: present
```

2. **Use `reloaded` instead of `restarted` in handlers** — nginx reload applies config without dropping connections:
```yaml
handlers:
  - name: Reload nginx
    service:
      name: nginx
      state: reloaded   # graceful — no dropped connections
```

3. **Template checksum validation** — only notify if the config actually changed (this is what `notify` already does correctly — the handler only fires if the template task reports `changed`). Ensure the template is deterministic (no `{{ now() }}` or random values).

4. **Validate config before reload:**
```yaml
- name: Validate nginx config
  command: nginx -t
  changed_when: false
  notify: Reload nginx
```

---

### Scenario 5: Ansible Vault Password Not Available in CI — Pipeline Fails on Encrypted Variables

**Problem:** A GitLab CI pipeline runs an Ansible playbook that uses `ansible-vault` encrypted variables. It fails with `ERROR! Attempting to decrypt but no vault secrets found`.

**Root cause:** The CI runner doesn't have access to the vault password. Locally, developers use `--ask-vault-pass` or `~/.vault_pass`.

**Fix — pass vault password via environment variable in CI:**
```yaml
# .gitlab-ci.yml
deploy:
  script:
    - echo "$ANSIBLE_VAULT_PASSWORD" > /tmp/vault_pass
    - chmod 600 /tmp/vault_pass
    - ansible-playbook site.yml --vault-password-file /tmp/vault_pass
    - rm -f /tmp/vault_pass
  after_script:
    - rm -f /tmp/vault_pass   # cleanup even on failure
```

**Better — use `ANSIBLE_VAULT_PASSWORD_FILE` env var:**
```yaml
variables:
  ANSIBLE_VAULT_PASSWORD_FILE: "/tmp/.vault_pass"

before_script:
  - echo "$ANSIBLE_VAULT_PASSWORD" > "$ANSIBLE_VAULT_PASSWORD_FILE"
  - chmod 600 "$ANSIBLE_VAULT_PASSWORD_FILE"
```

**Best practice — avoid vault for CI entirely. Use CI-native secrets instead:**

Re-encrypt CI-specific secrets using ansible-vault, but for the CI case, use environment variable lookup:
```yaml
# In group_vars/all/vault.yml
vault_db_password: "{{ lookup('env', 'DB_PASSWORD') | default(vault_db_password_encrypted) }}"
```

The `lookup('env', ...)` reads from the CI environment; the encrypted fallback is used only when the env var is absent (local dev with vault).

---

### Scenario 6: Playbook Runs Successfully on First Host, Fails on All Others — Variable Hoisting Bug

**Problem:** An Ansible playbook runs against 50 hosts. The first host completes successfully. The remaining 49 fail with "undefined variable: `db_primary_ip`."

**Root cause — `set_fact` with `run_once` and variable scoping:**
```yaml
- name: Get primary DB IP
  command: get-primary-db-ip.sh
  register: db_ip_result
  run_once: true

- name: Set DB IP fact
  set_fact:
    db_primary_ip: "{{ db_ip_result.stdout }}"
  run_once: true   # BUG: set_fact with run_once only sets the fact on the FIRST host
```

**Fix — explicitly delegate and share the fact:**
```yaml
- name: Get primary DB IP
  command: get-primary-db-ip.sh
  register: db_ip_result
  run_once: true
  delegate_to: "{{ groups['db'][0] }}"

- name: Set DB IP fact on ALL hosts
  set_fact:
    db_primary_ip: "{{ hostvars[groups['app'][0]]['db_ip_result']['stdout'] }}"
  # No run_once — runs on every host, reads the result from the host that ran the command
```

**Alternative — use a dummy host to collect facts:**
```yaml
- hosts: db_primary
  tasks:
    - command: get-primary-db-ip.sh
      register: db_ip_result

- hosts: app_servers
  tasks:
    - set_fact:
        db_primary_ip: "{{ hostvars[groups['db_primary'][0]]['db_ip_result']['stdout'] }}"
```

---

### Scenario 7: Ansible Handler Not Firing After Task Change — `flush_handlers` Required

**Problem:** An Ansible playbook updates a systemd service unit file and notifies a handler to restart the service. During testing, the unit file is updated but the service is not restarted within the play — it only restarts at the very end of the entire playbook, causing a subsequent task that depends on the running service to fail.

**Root cause:** Handlers in Ansible run at the end of the play by default, not immediately after the notifying task. If subsequent tasks depend on the service being restarted, they run before the handler fires.

**Fix — `flush_handlers` meta task:**
```yaml
tasks:
  - name: Update systemd unit file
    template:
      src: myservice.service.j2
      dest: /etc/systemd/system/myservice.service
    notify:
      - Reload systemd
      - Restart myservice

  - name: Flush handlers now (before dependent tasks)
    meta: flush_handlers

  - name: Wait for service to be ready
    wait_for:
      port: 8080
      delay: 2
      timeout: 30
    # This now runs AFTER the handler restarts the service
```

**Handler order within a flush:**
```yaml
handlers:
  - name: Reload systemd
    systemd:
      daemon_reload: yes

  - name: Restart myservice
    service:
      name: myservice
      state: restarted
    listen: Restart myservice   # handlers execute in DEFINITION order, not notification order
```

Handlers are executed in the order they are defined in the handlers section, not the order they were notified. Use `listen` topics to group related handlers and control execution order.

---

### Scenario 8: Ansible Tower / AWX Job Template Runs But Inventory Is Stale

**Problem:** An AWX job template shows hosts that were decommissioned 3 weeks ago. The Ansible playbook tries to SSH into those non-existent IPs and hangs, causing the job to run for hours before timing out.

**Diagnosis:**
- Check the inventory source: `AWX → Inventories → [inventory] → Sources`
- Check the last sync time: if "Sync" hasn't run recently, the inventory is cached

**Root causes:**

1. **Dynamic inventory source not syncing:** The cloud provider inventory (AWS EC2 plugin, Azure RM plugin) is configured but `Update on launch` is not checked:
```
AWX → Inventory Source → Edit → Update options: ✅ Update on launch
```

2. **Inventory sync succeeds but returns cached data:** AWS API is returning stale instance data from a regional endpoint. Add `--no-paginate` and check the inventory plugin config:
```ini
# aws_ec2.yml
plugin: amazon.aws.aws_ec2
regions:
  - us-east-1
filters:
  instance-state-name: running   # CRITICAL: filter out stopped/terminated instances
```

3. **Terminated instances not filtered:**
```ini
filters:
  "instance-state-name":
    - running           # only include running instances
# NOT: "tag:Environment": "prod"  — terminated instances also have tags
```

**Prevent SSH hangs:** Set aggressive SSH timeouts in `ansible.cfg`:
```ini
[defaults]
timeout = 10           # SSH connection timeout in seconds
gather_timeout = 20    # fact gathering timeout

[ssh_connection]
ssh_args = -o ConnectTimeout=5 -o ServerAliveInterval=10 -o ServerAliveCountMax=3
```

With a 5-second connection timeout, unreachable hosts fail fast rather than hanging for minutes.

---

## Scenario 9: Role Dependency Resolution Failure in Ansible Galaxy
**Symptom:** `ansible-playbook site.yml` fails with `ERROR! the role 'geerlingguy.mysql' was not found`. The role is listed in `requirements.yml` and was installed previously. Other engineers on the team can run the playbook fine.

**Diagnosis:**
```bash
# Check if the role is actually installed
ansible-galaxy role list | grep mysql

# Check the roles path
ansible-config dump | grep ROLES_PATH
# Default: ~/.ansible/roles:/etc/ansible/roles:/usr/share/ansible/roles

# Check requirements.yml
cat requirements.yml

# Verify the role exists in the expected path
ls ~/.ansible/roles/ | grep mysql

# Confirm ansible.cfg roles_path setting
grep -i roles_path ansible.cfg
```

**Root Causes and Fixes:**

1. **Roles installed to a different path than Ansible searches** — If `ansible.cfg` defines `roles_path = roles/` (project-local), but `ansible-galaxy install` wrote to `~/.ansible/roles/`, the role isn't found.
```bash
# Install to the project-local roles directory
ansible-galaxy install -r requirements.yml -p roles/

# Or set roles_path in ansible.cfg
[defaults]
roles_path = roles/:~/.ansible/roles
```

2. **requirements.yml version pinning mismatch** — One engineer has a newer cached version; a fresh install resolves a different version.
```yaml
# requirements.yml — always pin versions
roles:
  - name: geerlingguy.mysql
    version: 3.4.0
  - name: geerlingguy.nginx
    version: 3.1.0
collections:
  - name: community.mysql
    version: ">=3.8.0,<4.0.0"
```

3. **Galaxy API rate limiting in CI** — Anonymous `ansible-galaxy install` calls are rate-limited. Authenticate or cache:
```bash
# Cache galaxy installs in CI
cache:
  key: ansible-galaxy-${{ hashFiles('requirements.yml') }}
  paths:
    - ~/.ansible/roles
    - ~/.ansible/collections

# Only install if cache miss
- name: Install roles
  run: ansible-galaxy install -r requirements.yml --force-with-deps
```

**Prevention:** Commit installed roles to the repo (`roles/` directory, excluding `.git` subdirs) for air-gapped environments or reproducible installs. Use `molecule` in CI to test roles in isolation.

---

## Scenario 10: Ansible Parallelism Causing Race on Shared Resource
**Symptom:** A playbook that deploys a schema migration to a database runs fine with `--forks 1` but corrupts data when run with the default `--forks 5`. Multiple app servers are in the inventory, and the migration task runs on all of them simultaneously.

**Diagnosis:**
```bash
# Reproduce: run with forks=1 (works) vs forks=5 (fails)
ansible-playbook site.yml --forks 1 -v
ansible-playbook site.yml --forks 5 -v

# Check the task that mutates shared state
grep -n "migrate\|schema\|flyway\|alembic\|django.*migrate" roles/app/tasks/main.yml
```

**Root Causes and Fixes:**

1. **Migration task runs on all hosts in parallel** — Database migrations must run exactly once. Use `run_once: true` combined with a dedicated migration play:
```yaml
# In playbook: separate migration play runs before app deployment
- name: Run DB migrations
  hosts: app_servers[0]   # target only the first host
  tasks:
    - name: Apply schema migrations
      command: python manage.py migrate
      run_once: true        # belt-and-suspenders: also limit to one execution

- name: Deploy application
  hosts: app_servers        # now deploy to all
  tasks:
    - name: Restart app
      service: name=myapp state=restarted
```

2. **File-based locking between Ansible forks** — For tasks that must be serialized but run on all hosts, use `throttle`:
```yaml
- name: Reload nginx config
  command: nginx -s reload
  throttle: 1   # only 1 host at a time, regardless of --forks
```

3. **Serial deployment to limit blast radius** — For rolling deployments, use `serial` at the play level:
```yaml
- name: Deploy app
  hosts: app_servers
  serial: "25%"   # deploy to 25% of hosts at a time
  max_fail_percentage: 10   # abort if >10% of hosts fail
  tasks:
    - include_role: name=app
```

**Prevention:** Mark all tasks that touch shared state (DB, shared filesystem, load balancer registration) with `throttle: 1` or `run_once: true`. Document which plays are safe to run in parallel in a `RUNBOOK.md`.

---

## Scenario 11: Ansible Callback Plugin Breaking CI Output
**Symptom:** After adding the `community.general.json` callback plugin to format output, the CI pipeline shows all tasks as failed even though the playbook exits 0. The log parser is misreading the JSON output.

**Diagnosis:**
```bash
# Check active callback plugins
ansible-config dump | grep CALLBACK

# Check ansible.cfg
grep -A5 "\[defaults\]" ansible.cfg | grep callback

# Run with stdout_callback=yaml to see clean output
ANSIBLE_STDOUT_CALLBACK=yaml ansible-playbook site.yml

# Check what the CI log parser expects
# Jenkins / GitHub Actions parse specific patterns
```

**Root Causes and Fixes:**

1. **`stdout_callback` changes the entire output format** — JSON callback outputs one JSON blob at the end, not per-task lines. CI log parsers that look for `PLAY RECAP` or `ok=X` strings find nothing.
```ini
# ansible.cfg — use yaml for human-readable CI output
[defaults]
stdout_callback = yaml
# For JSON artifacts, use a separate callback:
callback_whitelist = community.general.json
# This writes to a separate file, not stdout
```

2. **Multiple callbacks writing to stdout conflict** — Only one `stdout_callback` is active at a time. Additional callbacks go to `callback_whitelist` (or `callbacks_enabled` in Ansible 2.10+).
```ini
[defaults]
stdout_callback = yaml
callbacks_enabled = profile_tasks, timer   # additional callbacks, not stdout replacements
```

3. **JSON output breaks `--check` mode parsing** — In dry-run (`--check`) mode, some JSON callbacks emit partial output if tasks are skipped. Add explicit handling:
```bash
# In CI, use yaml callback + tee to capture structured output separately
ANSIBLE_STDOUT_CALLBACK=yaml ansible-playbook site.yml 2>&1 | tee playbook.log
# Parse playbook.log for PLAY RECAP section
```

**Prevention:** Test callback plugin changes in CI before merging. Add a smoke test job that runs a trivial playbook and asserts the log contains `PLAY RECAP`.

---

## Scenario 12: Tags Not Limiting Execution as Expected
**Symptom:** Running `ansible-playbook site.yml --tags deploy` still runs tasks tagged `config` and `always`. The deploy takes 20 minutes when it should take 2.

**Diagnosis:**
```bash
# List all tags in the playbook
ansible-playbook site.yml --list-tags

# List which tasks would run with --tags deploy
ansible-playbook site.yml --tags deploy --list-tasks

# Check for tasks with multiple tags
grep -n "tags:" roles/app/tasks/main.yml

# Check for `always` tagged tasks
grep -rn "always" roles/ --include="*.yml"
```

**Root Causes and Fixes:**

1. **Tasks tagged `always` run regardless of `--tags`** — `always` is a special Ansible tag. Any task with `tags: always` runs even when other tags are specified.
```yaml
# This task ALWAYS runs, even with --tags deploy
- name: Gather facts
  setup:
  tags: always

# Fix: use --skip-tags always to explicitly exclude it
ansible-playbook site.yml --tags deploy --skip-tags always
```

2. **Role includes don't propagate tags correctly** — When including a role with `tags: deploy`, the tag applies to the role's `include_role` task, not necessarily to tasks inside the role.
```yaml
# This does NOT tag the tasks inside the role:
- include_role:
    name: myapp
  tags: deploy

# Fix: use `apply` to push tags into the role's tasks
- include_role:
    name: myapp
    apply:
      tags: deploy
  tags: deploy   # needed on the include AND apply
```

3. **`import_tasks` vs `include_tasks` tag inheritance** — Static imports (`import_tasks`) inherit tags from the parent; dynamic includes (`include_tasks`) do not. For tag-based task selection, prefer `import_tasks`.
```yaml
# Tags propagate into imported tasks
- import_tasks: deploy_tasks.yml
  tags: deploy

# Tags do NOT propagate into included tasks at parse time
- include_tasks: deploy_tasks.yml
  tags: deploy   # only tags the include statement itself
```

**Prevention:** After adding new roles or tasks, run `--list-tasks --tags <tag>` to verify exactly which tasks are selected. Add this as a CI check on playbook changes.
