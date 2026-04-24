# Configuration Management (Ansible)

Ansible is an open-source automation tool used for configuration management, application deployment, and task automation. Unlike Terraform (which creates the servers), Ansible is primarily used to "configure" the software inside those servers.

#### 1. Agentless Architecture
One of Ansible's biggest advantages is that it is **Agentless**. You don't need to install any software on the target servers.
*   **How it works:** Ansible uses **SSH** (for Linux) or **WinRM** (for Windows) to connect to servers, push small programs called "Ansible Modules," execute them, and then remove them.
*   **Prerequisites:** All you need is Python installed on the target machine.

#### 2. Idempotency: The Golden Rule
An automation tool is **Idempotent** if running it multiple times has the same effect as running it once.
*   **Example:** If you tell Ansible to "Install Nginx," it first checks if Nginx is already installed. If it is, Ansible does nothing. This ensures your servers stay in the "Desired State" without causing errors or restarts.

#### 3. Core Components
1.  **Inventory:** A list of the servers you want to manage (IP addresses or hostnames).
2.  **Modules:** The "tools in the toolbox." (e.g., `apt` for packages, `copy` for files, `service` for managing processes).
3.  **Playbooks:** YAML files that define the sequence of tasks to be performed.
4.  **Roles:** A way to group Playbooks and variables into a reusable structure (e.g., a "Database Role" or "Web Server Role").

#### 4. Variables & Templates
*   **Variables:** Allow you to use the same Playbook for different environments (e.g., different passwords for Dev and Prod).
*   **Jinja2 Templates:** Allow you to create configuration files dynamically (e.g., writing the server's IP address into an Nginx config file).

***

