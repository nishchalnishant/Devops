# Production Scenarios & Troubleshooting Drills (Senior Level)

### Scenario 1: IAM Permission Boundary Issues
**Problem:** You gave a user `AdministratorAccess`, but they still can't create an IAM Role.
**Diagnosis:** Check for an **IAM Permission Boundary**. It acts as a "max ceiling" for permissions. If it's not allowed in the boundary, the user can't do it.

### Scenario 2: Cross-Account Role Access
**Problem:** App in Account-A needs to read an S3 bucket in Account-B.
**Fix:** Create a Role in Account-B with a **Trust Policy** allowing Account-A. The App in Account-A must then call `sts:AssumeRole`.

### Scenario 3: Transit Gateway Routing Complexity
**Problem:** You have 10 VPCs connected via TGW, but VPC-A can't talk to VPC-J.
**Diagnosis:** Check the **TGW Route Tables**. TGW is not transitive by default; you must explicitly associate and propagate routes between attachments.

---

## Scenario 1: S3 Bucket Policy "Lockout"
**Symptom:** Even the Admin user cannot access an S3 bucket.
**Diagnosis:** A `Deny` policy was applied to `*` principals without excluding the current user.
**Fix:** Log in as the AWS Root account (which bypasses IAM policies) to delete the restrictive policy.

## Scenario 2: EBS Volume "Stuck" in Attaching
**Symptom:** EC2 instance hangs on boot; EBS volume shows `Attaching` state forever.
**Diagnosis:** The kernel on the EC2 instance failed to mount the drive, or there is a mismatch between the Xen and Nitro hypervisor device names.
**Fix:** Force-detach the volume and re-attach. Check `dmesg` for disk errors.


### Scenario 3: IAM Role "Trust Policy" failure
**Symptom:** An EC2 instance cannot assume a role, even though it has the policy attached.
**Diagnosis:** The Role's **Trust Relationship** does not allow the `ec2.amazonaws.com` service to assume it.
**Fix:** Update the Trust Policy to include the EC2 service principal.

### Scenario 4: Lambda "Cold Start" Latency
**Symptom:** First request to a Java Lambda takes 10 seconds.
**Diagnosis:** JVM initialization and class loading overhead.
**Fix:** Use **Provisioned Concurrency** or switch to a lighter runtime like Go or Python.
