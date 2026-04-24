#### 🔹 1. Improved Notes: Advanced Terraform
*   **Workspaces:** Allow you to manage multiple environments (Dev, Test, Prod) using the same code but separate state files.
*   **Provisioners:** Commands that run on a server after it's created (e.g., running a shell script). **Avoid these** if possible; use Ansible or UserData instead.
*   **Data Sources:** Allow you to fetch information from resources that were *not* created by Terraform (e.g., looking up an existing VPC ID).

#### 🔹 2. Interview View (Q&A)
*   **Q:** What is the difference between `terraform plan` and `terraform apply`?
*   **A:** `plan` is a "dry run" that shows the execution plan. `apply` actually executes those changes.
*   **Q:** What happens if you delete the `terraform.tfstate` file?
*   **A:** Terraform will lose its memory. It won't know that it already created those 10 servers and will try to create them again, leading to "Resource already exists" errors.

***

#### 🔹 3. Architecture & Design: Dependency Graph
Terraform builds a "Dependency Graph" of your resources. If a Database depends on a VPC, Terraform knows it must create the VPC first. It also uses this graph to create unrelated resources in parallel, making it extremely fast.

***

#### 🔹 4. Commands & Configs (Power User)
```bash
# Format your code to the standard style
terraform fmt

# Validate your code for syntax errors
terraform validate

# Remove a specific resource from the state (without deleting it in the cloud)
terraform state rm aws_instance.my_app

# Import an existing resource into Terraform management
terraform import aws_instance.manual_server i-1234567890
```

***

#### 🔹 5. Troubleshooting & Debugging
*   **Scenario:** Terraform is stuck in a "State Lock."
*   **Fix:** Usually happens if a previous `apply` crashed. Use `terraform force-unlock <LOCK_ID>` to release it (be very careful!).

***

#### 🔹 6. Production Best Practices
*   **Version Pinning:** Always pin the versions of Terraform and your Providers to prevent breaking changes.
*   **Terraform Cloud / Atlantis:** Use automation tools to run `terraform plan` and `apply` inside a pull request rather than from a developer's laptop.
*   **Variable Files:** Use `terraform.tfvars` to separate your configuration logic from your actual data (IPs, region names, etc.).

***

#### 🔹 Cheat Sheet / Quick Revision
| **Command** | **Purpose** | **DevOps Context** |
| :--- | :--- | :--- |
| `terraform output` | Show created info | Getting the Load Balancer DNS name for the next CI step. |
| `terraform destroy` | Delete everything | Tearing down a temporary testing environment. |
| `terraform refresh` | Update state file | Syncing the state with changes made manually in the console. |
| `terraform graph` | Visual dependency | Generating a diagram of your architecture. |

***

This is Section 10: Terraform. At a senior level, you should focus on **Terragrunt**, **Sentinel (Policy as Code)**, and **Module Versioning** strategies.
