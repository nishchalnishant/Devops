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
