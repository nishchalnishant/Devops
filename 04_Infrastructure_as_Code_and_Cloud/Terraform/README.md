# 8. Infrastructure As Code (IaC)

This stage marks the shift from manual "click-ops" to Software-Defined Infrastructure. Infrastructure as Code (IaC) allows you to manage your servers, networks, and cloud resources with the same rigor as application code—using version control, peer reviews, and automated testing.

***

### 8. Infrastructure As Code (IaC)

IaC is divided into two main categories: Provisioning (creating the hardware/infrastructure) and Configuration Management (setting up the software inside that hardware).

#### A. Terraform (The Provisioner)

Terraform is the industry leader for infrastructure provisioning. It is declarative, meaning you describe the _end state_ you want, and Terraform figures out how to build it.

* HCL (HashiCorp Configuration Language):
  * A human-readable, domain-specific language designed specifically for infrastructure.
  * Unlike scripts that run step-by-step, HCL allows you to define "Resources" (like an S3 bucket or a VPC) in any order; Terraform handles the dependency logic.
* Providers:
  * These are plugins that allow Terraform to communicate with different cloud platforms (AWS, Azure, GCP) or services (GitHub, Kubernetes, Cloudflare).
  * Example: The `aws` provider translates your HCL code into AWS API calls.
* Modules:
  * Self-contained packages of Terraform configurations.
  * Why use them? Instead of writing 100 lines of code for every new environment, you can create a "Standard Web Server" module and call it whenever needed, ensuring consistency across Dev, Staging, and Production.
* State Management:
  * Terraform keeps a record of everything it has created in a `terraform.tfstate` file.
  * This file acts as the "Source of Truth," allowing Terraform to know what already exists so it doesn't accidentally create duplicate resources.

***

#### B. Ansible (The Configurator)

While Terraform builds the server, Ansible is usually used to configure it—installing updates, setting up users, and deploying the application.

* Configuration Management:
  * Ansible ensures that the "state" of your server matches your requirements. If a package is already installed, Ansible won't try to install it again (Idempotency).
  * It is agentless, meaning you don't need to install software on your servers; it works entirely over SSH (for Linux) or WinRM (for Windows).
* Playbooks:
  * Written in YAML, these are the blueprints of automation tasks.
  * A Playbook lists a series of "Plays" that map specific tasks to specific groups of servers (e.g., "Update all Web Servers").
* Roles & Templates:
  * Roles: A way to break down complex playbooks into smaller, reusable components. For example, you might have a dedicated `nginx` role that handles everything related to the web server.
  * Templates: Ansible uses the Jinja2 engine to create dynamic configuration files. For example, you can use one template for an Nginx config file and automatically swap out the IP address based on which server it's being deployed to.

***

#### Terraform vs. Ansible: Which one to use?

In a professional DevOps pipeline, these tools are almost always used together:

1. Terraform creates the VPC, Subnets, and EC2 Instances (The "House").
2. Ansible logs into those instances to install the OS patches, Databases, and Apps (The "Furniture").



This is Section 8: Infrastructure as Code (IaC). For a mid-to-senior SRE/DevOps professional, IaC is the "Source of Truth" for the entire platform. At this level, it isn't just about writing a Terraform file; it’s about State Management, Concurrency Control, and Policy as Code.

In production, an error in your IaC can destroy an entire production environment in minutes. Your goal is to build "Guardrails" around the automation.

***

#### 🔹 1. Improved Notes: Provisioning vs. Configuration

**The Two Pillars: Terraform vs. Ansible**

* Terraform (Provisioning - Declarative): You define the "What" (e.g., I want 3 EC2 instances). Terraform figures out how to reach that state. It is Idempotent—running it twice with the same code results in no changes if the infrastructure matches the code.
* Ansible (Configuration - Procedural/Hybrid): You define the "How" (e.g., Install Nginx, then copy this config). While it can be idempotent, it is primarily used to configure the software inside the infrastructure Terraform created.

**State Management: The SRE’s Lifeline**

* The State File (`terraform.tfstate`): This maps your code to real-world resources. In production, never keep this locally. Use a Remote Backend (S3/GCS) with State Locking (DynamoDB) to prevent two engineers from corrupting the state simultaneously.
* Modules: Don't write monolithic code. Create reusable modules (e.g., a "VPC Module") so that every environment (Dev/Prod) uses the exact same architectural pattern.

**Infrastructure Lifecycle (Immutable vs. Mutable)**

* Mutable (Ansible approach): Update a live server. Risks "Configuration Drift" (servers that were once identical become different over time).
* Immutable (Packer + Terraform approach): Instead of updating a server, you burn a new Machine Image (AMI), destroy the old server, and deploy a new one. This is the gold standard for SRE reliability.

***

#### 🔹 2. Interview View (Q\&A)

Q1: What is "Configuration Drift" and how do you solve it?

* Answer: Drift occurs when manual changes (ClickOps) are made to the cloud console, making the real infrastructure different from the IaC code.
* The Fix: 1. Run `terraform plan` regularly to detect changes. 2. Use a GitOps tool like Atlantis or Terraform Cloud that continuously reconciles the state. 3. Strictly enforce "No Manual Changes" via IAM permissions.

Q2: You deleted the Terraform state file by accident. The resources still exist in AWS. How do you recover?

* Answer: You must use the `terraform import` command for every single resource. You write the code first, then run `terraform import <resource_type>.<name> <physical_id>`.
* Senior Twist: Mention that preventing this is better—use S3 Versioning on your state bucket so you can roll back to a previous version of the state.

Q3: Explain the difference between `count` and `for_each` in Terraform.

* Answer: `count` uses an index (0, 1, 2). If you delete the item at index 0, Terraform shifts everything, often causing it to destroy and recreate the wrong resources. `for_each` uses a map or set of keys, making it much safer for managing dynamic lists of resources.

***

#### 🔹 3. Architecture & Design: Scalable IaC

The "Terragrunt" / Workspace Pattern:

When managing multiple environments (Dev, Staging, Prod), you don't want to copy-paste code.

* Terragrunt: A wrapper that keeps your configurations "DRY" (Don't Repeat Yourself).
* Workspaces: Allows you to manage multiple states from a single configuration (useful for testing, but many SREs prefer separate directories for Prod for better isolation).

Trade-offs: Local Exec vs. Cloud-Native

* Local-exec: Running a script on your machine during `terraform apply`. This is an anti-pattern because it's hard to debug and requires local dependencies.
* Better way: Use "Cloud-init" or "User Data" scripts to configure the instance upon boot.

***

#### 🔹 4. Commands & Configs (Production Ready)

**Terraform: Secure Backend Config**

Terraform

```
terraform {
  backend "s3" {
    bucket         = "my-company-tf-state"
    key            = "production/network.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-lock" # Prevents concurrent runs
    encrypt        = true             # Sensitive data in state is encrypted at rest
  }
}
```

**Ansible: Idempotent Playbook**

YAML

```
- name: Setup Nginx
  hosts: webservers
  become: yes
  tasks:
    - name: Ensure nginx is at the latest version
      apt:
        name: nginx
        state: latest
    - name: Copy config (Only restarts if file changes)
      template:
        src: nginx.conf.j2
        dest: /etc/nginx/nginx.conf
      notify: restart nginx

  handlers:
    - name: restart nginx
      service:
        name: nginx
        state: restarted
```

***

#### 🔹 5. Troubleshooting & Debugging

Scenario: `terraform apply` is stuck "Acquiring state lock."

1. Cause: A previous run crashed or another engineer is currently running a plan.
2.  SRE Debugging: Check the DynamoDB lock table. If you are sure no one else is running it, manually release the lock using:

    terraform force-unlock \<LOCK\_ID>

Scenario: Ansible "Unreachable" error.

1. Check SSH: Can you manually `ssh` into the box?
2. Check Key: Is the correct `.pem` key defined in the inventory or `ansible.cfg`?
3. Check Security Groups: Is port 22 open from the Ansible controller to the target?

***

#### 🔹 6. Production Best Practices

* Policy as Code: Use Checkov, TFLint, or Open Policy Agent (OPA) in your CI pipeline to scan for security holes (e.g., "S3 bucket is public") _before_ the code is applied.
* Blast Radius Reduction: Break your code into smaller pieces. Don't put the "Database," "VPC," and "App" in one state file. If the "App" code fails, you don't want it touching the "Database."
* Variable Validation: Use Terraform variable validation to catch typos (e.g., ensuring an instance type is from an approved list).
* Anti-Pattern: Hardcoding IDs (e.g., `ami-12345`). Always use Data Sources to look up the latest IDs dynamically.

***

#### 🔹 Cheat Sheet / Quick Revision

| **Concept**   | **Key SRE Detail**                                                      |
| ------------- | ----------------------------------------------------------------------- |
| Idempotency   | The ability to run a script multiple times without changing the result. |
| State File    | The mapping of code to real infrastructure. Treat it like a secret.     |
| Provider      | The plugin that talks to the Cloud API (AWS, GCP, Azure).               |
| Resource      | A single piece of infrastructure (an EC2 instance, an S3 bucket).       |
| Data Source   | Fetching information from the cloud (e.g., find the latest Ubuntu AMI). |
| Implicit Dep. | Terraform automatically knows to build the VPC before the Subnet.       |

***

This is Section 8: Infrastructure as Code (IaC). In the modern DevOps landscape, "ClickOps" (manually clicking in a console) is a liability. For a senior role, you must demonstrate that you can treat your entire data center like software: versioned, tested, and reproducible.

***

#### 🟢 Easy: Basic Concepts & Tooling

_Focus: Understanding the "What" and the basic roles of different tools._

1. What is Infrastructure as Code (IaC), and why is it better than manual configuration?
   * _Context:_ Focus on speed, cost, and the elimination of human error.
2. Explain the difference between Terraform and Ansible.
   * _Context:_ Define Terraform as a provisioning tool (building the house) and Ansible as a configuration management tool (painting the walls and installing appliances).
3. What is a Terraform "Provider"?
   * _Context:_ How does Terraform talk to different clouds like AWS, Azure, or even GitHub?
4. What is an "Inventory" in Ansible?
   * _Context:_ How does Ansible know which servers to target? Mention static vs. dynamic inventories.

***

#### 🟡 Medium: Logic, State & Reusability

_Focus: How the tools work under the hood and how to organize code._

1. Explain the concept of "Idempotency." Why is it critical for both Terraform and Ansible?
   * _Context:_ If I run the same script 10 times, what should happen? (The state should not change after the first successful run).
2. What is the Terraform "State File" (`.tfstate`), and why is it dangerous to keep it on your local machine?
   * _Context:_ Discuss team collaboration and the risk of "State Locking" or losing the file. Mention Remote Backends (S3, GCS).
3. What are Terraform "Modules," and what are the benefits of using them?
   * _Context:_ Focus on reusability, standardization, and reducing "Copy-Paste" code across Dev, Staging, and Prod.
4. In Ansible, what is the difference between a Playbook and a Role?
   * _Context:_ How do Roles help in organizing complex automation? (Think of them as packages for specific tasks like `db_setup` or `nginx_config`).

***

#### 🔴 Hard: Senior Architecture & Problem Solving

_Focus: Handling failures, state corruption, and scaling automation._

1. Explain the difference between "Declarative" and "Imperative" approaches. Which do Terraform and Ansible follow?
   * _Context:_ Terraform is purely Declarative (describe the end state); Ansible is primarily Imperative/Procedural (describe the steps), though it can behave declaratively.
2. Scenario: You run `terraform plan` and notice it wants to destroy and recreate a production database instead of just modifying it. What could cause this, and how do you prevent it?
   * _Context:_ Discuss immutable vs. mutable changes. Mention the `lifecycle` block (`prevent_destroy`) and how certain attribute changes (like changing a DB name or VPC) force a recreation.
3. What is "Infrastructure Drift," and how do you detect and remediate it?
   * _Context:_ How do you handle a situation where someone manually changed a Security Group in the AWS Console? Mention `terraform plan` and automated reconciliation tools like Atlantis.
4. Explain how you handle sensitive data (passwords, SSH keys) in IaC.
   * _Context:_ The interviewer is looking for Ansible Vault, Terraform sensitive variables, or integration with external managers like HashiCorp Vault or AWS Secrets Manager.
5. What is a "Null Resource" and "Remote-exec" in Terraform? Why are they often considered an anti-pattern?
   * _Context:_ Discuss why we prefer native cloud providers over running arbitrary bash scripts inside our Terraform code.

***

#### 💡 Pro-Tip for your Interview

When discussing IaC, always talk about the "Blast Radius."

* The SRE Answer: "To minimize the blast radius, I never store my entire infrastructure in one massive state file. I break my Terraform code into logical components: Networking, Data, and App. This ensures that a mistake in the App layer doesn't accidentally trigger a deletion of the core VPC or Database."

---

## 🔷 Advanced Infrastructure as Code (7 YOE)

If you are interviewing for a Senior or Staff position, knowing basic Terraform resources is insufficient. You will be evaluated on your ability to scale IaC across an enterprise safely. 

**Continue your preparation with these advanced modules:**

1. `[NEW]` [Advanced Terraform Patterns & State Manipulation](./advanced-terraform-patterns.md): Terragrunt architectures, `state mv`, `state rm`, and dynamic code blocks.
2. `[NEW]` [GitOps & Policy-as-Code](./policy-and-gitops.md): Atlantis PR-driven workflows, infrastructure drift reconciliation, and OPA/Checkov security guardrails.
3. `[NEW]` [Enterprise Landing Zones](../Cloud_Services/enterprise-landing-zones.md): Deep dive into multi-account architectures, Account Vending Machines (AVMs), and Hub-and-Spoke networking at scale.
