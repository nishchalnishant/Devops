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

---

## Scenario 1: Secret Leaked in Git History
**Symptom:** A developer accidentally pushed an AWS Access Key to a public repo.
**Diagnosis:** The key is now compromised. Deleting it from the latest commit is not enough.
**Fix:** 
1. **Invalidate** the key in AWS immediately.
2. Use `git-filter-repo` or BFG to scrub the key from history.
3. Check logs to see if the key was used by an attacker.

## Scenario 2: Vulnerable Dependency (Log4Shell style)
**Symptom:** A 0-day vulnerability is announced for a library used in 100 microservices.
**Diagnosis:** You need to identify which services are affected and patch them immediately.
**Fix:** 
1. Run a SCA scan (e.g., Snyk, Trivy) across all repos.
2. Use an automated PR tool (e.g., Dependabot, Renovate) to push the fix.
3. If patching is impossible, use a WAF rule to block the exploit pattern.
