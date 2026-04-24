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

