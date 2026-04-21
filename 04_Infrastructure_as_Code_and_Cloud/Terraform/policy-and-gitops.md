# GitOps & Policy-as-Code for IaC (7 YOE)

Running `terraform apply` from an engineer's laptop is fundamentally insecure. It requires the laptop to hold highly privileged AWS/Azure credentials, it bypasses peer review, and it leaves no audit trail.

A Senior DevOps Engineer enforces a strict **GitOps** pipeline and relies on **Policy-as-Code** for automated security guardrails.

---

## 1. GitOps Workflows (Atlantis / Terraform Cloud)

GitOps dictates that Git is the sole source of truth. If a change is not in Git, it cannot exist in the cloud ecosystem.

### The Atlantis Workflow
Atlantis is an open-source application that listens for webhook events from GitHub/GitLab and runs Terraform commands locally on a remote server.

1. **Developer Open Pull Request (PR):**
   - The developer pushes a branch modifying `main.tf` and opens a PR.
2. **Atlantis Auto-Plans:**
   - Atlantis detects the PR webhooks, pulls the branch, and automatically runs `terraform plan`.
   - The output of the plan is printed directly into the PR comments.
3. **Peer Review:**
   - A Senior Engineer reviews the PR code *and* the Atlantis plan output.
   - If acceptable, the reviewer approves the PR.
4. **Atlantis Apply on Comment:**
   - The developer comments `atlantis apply` on the PR.
   - Atlantis runs the apply, outputs the success to the PR comment, and automatically merges the PR and deletes the branch.

**Security Benefit:** Only the Atlantis server holds cloud credentials. Developers only hold GitHub credentials.

---

## 2. Policy as Code (Automating Security Reviews)

A "blast radius" is the extent of damage a bad Terraform run can cause. The best way to reduce blast radius is to fail the build *before* `terraform plan` is ever applied.

### Open Policy Agent (OPA) / Rego
OPA is a CNCF project that provides a high-level declarative language (Rego) to enforce policies. It can parse the JSON output of a `terraform plan`.

**Example Rego Policy: Prevent Public S3 Buckets**
```rego
package terraform.aws.s3

deny[msg] {
    # Find all resources in the tfplan where the type is aws_s3_bucket_public_access_block
    resource := input.resource_changes[_]
    resource.type == "aws_s3_bucket_public_access_block"
    
    # Check if block_public_acls is explicitly set to false
    resource.change.after.block_public_acls == false

    msg := sprintf("Security Violation: Bucket %v explicitly allows public ACLs", [resource.name])
}
```

### Checkov & tfsec (Static Code Analysis)
If writing Rego is too much overhead, tools like Checkov provide hundreds of out-of-the-box policies. Checkov scans the RAW HCL code (static analysis) without needing to generate a plan JSON first.

```bash
# Run Checkov locally or in a CI Pipeline
checkov -d ./terraform/
```
Output:
```
Failed checks:
  Check: CKV_AWS_20: "S3 Bucket has an ACL defined which allows public READ access."
  File: /storage.tf:12-15
```

---

## 3. Handling Infrastructure Drift

**Drift** occurs when the actual state of the cloud resources differs from the desired state codified in Terraform (often because someone used "Click-Ops" bypassing GitOps).

### Detection
Schedule a cron job in your CI/CD pipeline (e.g., nightly) to run `terraform plan -detailed-exitcode`.
- Exit code `0` = No drift.
- Exit code `2` = Changes detected (Drift!). Send a Slack alert to the team.

### Remediation
1. **Reconciliation (Self-healing):** The CI system automatically runs `terraform apply` to wipe out the manual changes and restore the Git state.
2. **Backporting:** If the manual change was an emergency hotfix (e.g., expanding a database during a Black Friday outage), the engineer must write the Terraform code to match the hotfix, and submit a PR to update the baseline.
