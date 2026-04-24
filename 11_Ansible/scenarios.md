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
