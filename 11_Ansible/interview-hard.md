## Hard

**15. Compare Ansible and Terraform. When do you use them together?**

- **Terraform (declarative provisioner):** Manages infrastructure lifecycle — provisions and destroys resources. Stateful (tracks resources in state file). Ideal for: VMs, VPCs, Kubernetes clusters, databases, load balancers.
- **Ansible (procedural configuration manager):** Configures software on infrastructure. Generally stateless (no built-in state). Ideal for: package installation, service configuration, application deployment, OS hardening.
- **Together:** Terraform provisions a VM and outputs its IP. A Terraform `null_resource` with `local-exec` or a subsequent CI step calls `ansible-playbook -i <ip>, playbook.yml` against the new instance. Ansible then installs and configures the application.

**16. How do you test Ansible roles before publishing them to a shared repository?**

Use **Molecule** — the standard testing framework for Ansible roles:

1. **Test matrix:** Define drivers (Docker, Podman, Vagrant) and base images (Ubuntu 22.04, RHEL 9) in `molecule.yml`.
2. **Lifecycle:** `dependency` → `lint` → `syntax` → `create` → `prepare` → `converge` (run the role) → `idempotence` (run again, assert no changes) → `verify` → `destroy`.
3. **Verification:** The `verify` step uses Testinfra or Goss to assert that the role configured the system correctly — checking that packages are installed, services are running, and config files contain expected values.

**17. How do you manage a large Ansible project with hundreds of roles across multiple teams?**

1. **Collections:** Package related roles and modules into Ansible Collections — the modern distribution and consumption unit. Store in a private Automation Hub or Galaxy-compatible server.
2. **Requirements.yml:** All external roles and collections version-pinned in `requirements.yml`. CI installs them fresh each run.
3. **Execution Environments:** Container images packaging a specific Ansible Core version, Python, required libraries, and collections. Ensures the playbook runs identically on a developer's laptop and in CI.
4. **AWX/Ansible Tower:** Provides RBAC, inventory management, workflow templates, job scheduling, and audit logging for centralized playbook execution.

**18. What is the difference between an Ansible dynamic inventory and a Smart Inventory in Ansible Tower/AWX?**

- **Dynamic Inventory:** A script or plugin querying a cloud provider API at runtime to get the current host list.
- **Smart Inventory (AWX feature):** An inventory whose hosts are dynamically populated based on a filter query against other existing inventories. Example: "all hosts in the `webservers` group AND tagged `production` AND with a failed job in the last 24 hours." This enables complex targeting without writing custom scripts.

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

**20. How do you handle Ansible performance at scale (1000+ hosts)?**

- **Forks:** Increase `forks = 50` (or higher) in `ansible.cfg` — Ansible runs tasks on this many hosts simultaneously.
- **Pipelining:** Enable `pipelining = True` to reduce SSH round trips by executing multiple modules in a single SSH connection.
- **Mitogen:** Ansible plugin that replaces the default SSH-based transport with a fast multiplexed transport — often 5-10x faster.
- **Pull mode (ansible-pull):** Each host runs `ansible-pull` from a Git repository on a cron, distributing the execution — the controller is not the bottleneck.
- **Fact caching:** Cache `setup` facts in Redis or a JSON file to avoid redundant fact gathering on repeated runs.
