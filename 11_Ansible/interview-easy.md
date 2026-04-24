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

---

