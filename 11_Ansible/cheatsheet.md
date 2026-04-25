# Ansible Cheatsheet

Quick reference for Ansible commands, playbook patterns, and configuration.

***

## Core Commands

```bash
# Inventory & connectivity
ansible all -i inventory.ini -m ping                  # Test connectivity to all hosts
ansible webservers -i inventory.ini -m ping           # Ping a specific group
ansible-inventory -i inventory.ini --list             # Show inventory as JSON
ansible-inventory -i inventory.ini --graph            # Show inventory tree

# Ad-hoc commands
ansible all -i inventory.ini -m shell -a "uptime"                   # Run shell command
ansible all -i inventory.ini -m command -a "hostname"               # Run command (no shell features)
ansible webservers -i inventory.ini -m copy -a "src=file.conf dest=/etc/app/" -b  # Copy file (become root)
ansible all -i inventory.ini -m package -a "name=nginx state=present" -b          # Install package
ansible all -i inventory.ini -m service -a "name=nginx state=restarted" -b        # Restart service
ansible all -i inventory.ini -m user -a "name=deploy state=present" -b            # Ensure user exists

# Playbooks
ansible-playbook site.yml                             # Run playbook
ansible-playbook site.yml -i production/             # With specific inventory
ansible-playbook site.yml --limit webservers          # Limit to group
ansible-playbook site.yml --limit "web01,web02"       # Limit to specific hosts
ansible-playbook site.yml --tags "deploy"             # Run only tagged tasks
ansible-playbook site.yml --skip-tags "notify"        # Skip tagged tasks
ansible-playbook site.yml --start-at-task "Configure nginx"  # Start from specific task
ansible-playbook site.yml -e "env=production"         # Pass extra variables
ansible-playbook site.yml -e @vars/prod.yml           # Load vars from file
ansible-playbook site.yml --check                     # Dry run (no changes)
ansible-playbook site.yml --diff                      # Show file diffs
ansible-playbook site.yml --check --diff              # Dry run + show diffs
ansible-playbook site.yml -v                          # Verbose (-vvvv for max)
```

***

## Inventory

### Static Inventory (INI format)

```ini
# inventory.ini
[webservers]
web01 ansible_host=10.0.1.10 ansible_user=ubuntu
web02 ansible_host=10.0.1.11

[dbservers]
db01 ansible_host=10.0.2.10 ansible_user=ec2-user ansible_ssh_private_key_file=~/.ssh/prod.pem

[production:children]
webservers
dbservers

[all:vars]
ansible_python_interpreter=/usr/bin/python3
```

### Dynamic Inventory (AWS EC2)

```bash
# Install AWS collection
ansible-galaxy collection install amazon.aws

# Use dynamic inventory
ansible all -i aws_ec2.yaml -m ping

# aws_ec2.yaml
plugin: amazon.aws.aws_ec2
regions: [us-east-1]
filters:
  tag:env: production
keyed_groups:
  - key: tags.role
    prefix: role
```

***

## Playbook Structure

```yaml
---
- name: Configure web servers
  hosts: webservers
  become: yes              # sudo
  gather_facts: yes        # collect system info

  vars:
    nginx_port: 80
    app_user: deploy

  vars_files:
    - vars/secrets.yml     # ansible-vault encrypted

  pre_tasks:
    - name: Update apt cache
      apt:
        update_cache: yes
        cache_valid_time: 3600

  roles:
    - common
    - nginx

  tasks:
    - name: Ensure app directory exists
      file:
        path: /opt/app
        state: directory
        owner: "{{ app_user }}"
        mode: '0755'

    - name: Deploy config
      template:
        src: app.conf.j2
        dest: /etc/app/app.conf
      notify: Restart app

  handlers:
    - name: Restart app
      service:
        name: myapp
        state: restarted

  post_tasks:
    - name: Verify app is running
      uri:
        url: "http://localhost:{{ app_user }}/healthz"
        status_code: 200
```

***

## Key Modules Reference

```yaml
# File operations
- file: path=/tmp/dir state=directory mode='0755'
- copy: src=local.conf dest=/etc/app.conf owner=root mode='0644'
- template: src=nginx.j2 dest=/etc/nginx/nginx.conf
- fetch: src=/etc/hostname dest=./hosts/ flat=yes
- lineinfile: path=/etc/hosts line="10.0.0.1 myhost" state=present
- blockinfile: path=/etc/sysctl.conf block: |
    net.ipv4.tcp_tw_reuse=1

# Packages
- apt: name=nginx state=present update_cache=yes
- yum: name=httpd state=latest
- package: name=git state=present          # OS-agnostic
- pip: name=flask version=2.3.0 virtualenv=/opt/venv

# Services
- service: name=nginx state=started enabled=yes
- systemd: name=myapp state=restarted daemon_reload=yes

# Commands
- command: /usr/bin/myapp --init            # No shell; fails if no change
- shell: "echo $HOME | tee /tmp/home.txt"  # Full shell; use sparingly
- raw: apt-get install -y python3           # No Python needed on remote

# Users & Groups
- user: name=deploy groups=sudo append=yes shell=/bin/bash create_home=yes
- authorized_key: user=deploy key="{{ lookup('file', '~/.ssh/id_rsa.pub') }}"

# Git
- git: repo=https://github.com/org/app.git dest=/opt/app version=main force=yes

# Archives
- unarchive: src=app.tar.gz dest=/opt/app remote_src=yes

# URI / API calls
- uri:
    url: https://api.example.com/deploy
    method: POST
    body_format: json
    body: '{"env": "production"}'
    status_code: [200, 201]
```

***

## Vault — Encrypted Secrets

```bash
# Create encrypted file
ansible-vault create vars/secrets.yml

# Edit encrypted file
ansible-vault edit vars/secrets.yml

# Encrypt existing file
ansible-vault encrypt vars/secrets.yml

# Decrypt to view
ansible-vault view vars/secrets.yml

# Encrypt a single string value
ansible-vault encrypt_string 'my-secret-password' --name 'db_password'

# Run playbook with vault password
ansible-playbook site.yml --ask-vault-pass
ansible-playbook site.yml --vault-password-file ~/.vault_pass
```

***

## Loops & Conditionals

```yaml
# Loop over list
- name: Install packages
  apt:
    name: "{{ item }}"
    state: present
  loop:
    - nginx
    - curl
    - git

# Loop with dict
- name: Create users
  user:
    name: "{{ item.name }}"
    groups: "{{ item.groups }}"
  loop:
    - { name: alice, groups: sudo }
    - { name: bob, groups: www-data }

# Conditional
- name: Install on Debian only
  apt:
    name: nginx
  when: ansible_os_family == "Debian"

- name: Only run in production
  include_tasks: deploy.yml
  when: env == "production"

# Register and use output
- name: Check if config exists
  stat:
    path: /etc/app/config.yml
  register: config_file

- name: Deploy config if missing
  copy:
    src: config.yml
    dest: /etc/app/config.yml
  when: not config_file.stat.exists
```

***

## Error Handling

```yaml
# Ignore errors (continue playbook)
- name: Try to stop old service
  service:
    name: old-app
    state: stopped
  ignore_errors: yes

# Fail on specific condition
- name: Check disk space
  command: df -h /
  register: disk_info
  failed_when: "'100%' in disk_info.stdout"

# Block / Rescue / Always
- block:
    - name: Risky operation
      command: ./deploy.sh
  rescue:
    - name: Rollback on failure
      command: ./rollback.sh
  always:
    - name: Send notification
      uri:
        url: https://hooks.slack.com/...
        method: POST
```

***

## ansible.cfg Reference

```ini
[defaults]
inventory          = ./inventory
remote_user        = ubuntu
private_key_file   = ~/.ssh/id_rsa
host_key_checking  = False
forks              = 20                  # Parallel hosts (default 5)
timeout            = 30
retry_files_enabled = False
stdout_callback    = yaml                # Prettier output
interpreter_python = auto_silent

[privilege_escalation]
become             = True
become_method      = sudo
become_user        = root

[ssh_connection]
pipelining         = True               # Faster SSH (requires requiretty disabled)
ssh_args           = -C -o ControlMaster=auto -o ControlPersist=60s
```

***

## Roles Quick Reference

```bash
# Create role structure
ansible-galaxy role init my-role

# Install roles from Galaxy
ansible-galaxy install geerlingguy.docker
ansible-galaxy install -r requirements.yml

# List installed roles
ansible-galaxy role list
```

```
my-role/
├── defaults/main.yml    # Default variables (lowest precedence)
├── vars/main.yml        # Role variables (high precedence)
├── tasks/main.yml       # Tasks (entry point)
├── handlers/main.yml    # Handlers
├── templates/           # Jinja2 templates (.j2)
├── files/               # Static files
├── meta/main.yml        # Role metadata & dependencies
└── tests/               # Molecule tests
```

***

## Variable Precedence (Lowest → Highest)

```
1. role defaults
2. inventory file vars
3. inventory group_vars/all
4. inventory group_vars/<group>
5. inventory host_vars/<host>
6. playbook group_vars/all
7. playbook group_vars/<group>
8. playbook host_vars/<host>
9. host facts
10. play vars
11. role vars
12. block vars
13. task vars
14. extra vars (-e)    ← HIGHEST
```
