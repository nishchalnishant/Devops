# Production Scenarios & Troubleshooting Drills (Senior Level)

### Scenario 1: SCA "Vulnerability Overload"
**Problem:** 500 CVEs found in a scan.
**Fix:** Prioritize by `Critical` + `Fix Available` + `Network Reachable`. Use "Vulnerability Reachability" tools to see if the buggy code is even reachable by an attacker.

### Scenario 2: Supply Chain Security with Sigstore
**Problem:** How do you prove the image in Prod is the same one built in CI?
**Fix:** Use **Cosign** to sign the image in the CI pipeline using OIDC. Use a Kubernetes admission controller (**Kyverno** or **Policy Reporter**) to block any unsigned images.

### Scenario 3: Runtime Security with Falco
**Problem:** An attacker achieved a shell in your container. How do you know?
**Fix:** Deploy **Falco**. It monitors system calls and sends an alert if a shell is spawned or if a sensitive file (like `/etc/shadow`) is touched.
