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

---

## Scenario 3: Compromised Base Image in Supply Chain
**Symptom:** Security team gets an alert from Prisma Cloud that a container running in production is making outbound connections to an unknown IP on port 4444. The image was pulled from Docker Hub.

**Diagnosis:**
```bash
# Identify the running image
kubectl get pods -A -o jsonpath='{range .items[*]}{.metadata.namespace}{"\t"}{.metadata.name}{"\t"}{.spec.containers[*].image}{"\n"}{end}' | grep suspicious-image

# Pull the image and scan it
docker pull node:18-alpine
trivy image node:18-alpine --severity CRITICAL,HIGH

# Inspect the image layers for embedded binaries or cron jobs
docker run --rm node:18-alpine find / -name "*.sh" -newer /etc/passwd 2>/dev/null
docker history node:18-alpine --no-trunc

# Check image digest vs what CI originally pulled
docker inspect node:18-alpine --format '{{.Id}}'
# Compare with CI artifact metadata

# Runtime: check what the process is doing
kubectl exec -it suspicious-pod -n prod -- ps aux
kubectl exec -it suspicious-pod -n prod -- ss -tnp
```

**Root Causes and Fixes:**

1. **Mutable tag (`:18-alpine`) re-tagged to a malicious image on Docker Hub** — Always pin images to digest, not tag.
```dockerfile
# Wrong
FROM node:18-alpine

# Right
FROM node@sha256:4a55b5b2b0b3c7e8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2
```

2. **No admission control to enforce trusted registries** — Block all images not from your private registry.
```yaml
# Kyverno ClusterPolicy
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: restrict-image-registries
spec:
  validationFailureAction: Enforce
  rules:
  - name: allow-only-private-registry
    match:
      resources:
        kinds: [Pod]
    validate:
      message: "Images must come from 123456789.dkr.ecr.us-east-1.amazonaws.com"
      pattern:
        spec:
          containers:
          - image: "123456789.dkr.ecr.us-east-1.amazonaws.com/*"
```

3. **Remediation:** Immediately terminate the compromised pods, rotate any secrets they had access to, and audit CloudTrail/VPC Flow Logs for the timeframe the image was running.

**Prevention:** Mirror all upstream images to your private registry. Verify digests in your CI pipeline with `cosign verify --key cosign.pub`. Enable Falco rules for `outbound_conn` to unknown CIDRs.

---

## Scenario 4: OPA Gatekeeper Policy Conflict Blocks All Deployments
**Symptom:** After a Gatekeeper policy update, all deployments to production fail with `admission webhook ... denied the request`. Even rollbacks fail.

**Diagnosis:**
```bash
# Check which constraints are failing
kubectl get constraints -A
kubectl describe constraint require-resource-limits

# Test a specific manifest against policies
cat deployment.yaml | kubectl apply --dry-run=server -f -
# Error message will name the constraint

# Check Gatekeeper controller health
kubectl get pods -n gatekeeper-system
kubectl logs -n gatekeeper-system -l control-plane=controller-manager --tail=50

# Emergency: check if webhook has a failure policy
kubectl get validatingwebhookconfiguration gatekeeper-validating-webhook-configuration \
  -o jsonpath='{.webhooks[*].failurePolicy}'
```

**Root Causes and Fixes:**

1. **`failurePolicy: Fail` on the webhook with Gatekeeper pods crashing** — If the webhook endpoint is unreachable, `Fail` rejects all requests. Change to `Ignore` as an emergency measure.
```bash
kubectl patch validatingwebhookconfiguration gatekeeper-validating-webhook-configuration \
  --type='json' \
  -p='[{"op":"replace","path":"/webhooks/0/failurePolicy","value":"Ignore"}]'
```
Restore to `Fail` after the Gatekeeper pod issue is resolved.

2. **New constraint has overly broad match scope** — A ConstraintTemplate that matches `kinds: [Pod]` without excluding `kube-system` or Gatekeeper's own namespace blocks system operations.
```yaml
spec:
  match:
    excludedNamespaces: ["kube-system", "gatekeeper-system", "cert-manager"]
```

3. **Constraint in `warn` vs `deny` enforcement** — Promote new policies through enforcement actions: `dryrun` → `warn` → `deny`. This catches conflicts before they block production.
```yaml
spec:
  enforcementAction: warn  # start here, promote to deny after validation
```

**Prevention:** Gate Gatekeeper policy changes with a canary namespace where all `EnforcementAction: deny` rules are tested first. Use `gator verify` in CI to validate ConstraintTemplates against test cases before merging.

---

## Scenario 5: SAST False Positives Blocking Pipeline at Scale
**Symptom:** After enabling SAST with Semgrep in all pipelines, 40% of PRs are blocked by findings that developers identify as false positives. Merge velocity drops 60%.

**Diagnosis:**
```bash
# Identify the highest-volume false positive rule IDs
cat semgrep-output.json | jq '[.results[] | .check_id] | group_by(.) | map({rule: .[0], count: length}) | sort_by(-.count) | .[0:10]'

# Check severity distribution
cat semgrep-output.json | jq '[.results[].extra.severity] | group_by(.) | map({sev: .[0], count: length})'

# Review the specific rule causing the most noise
semgrep --config "p/security-audit" --test path/to/code/

# Check false positive rate per rule
# (false_positives / total_findings_for_rule)
```

**Root Causes and Fixes:**

1. **Running full ruleset including `audit` level rules in blocking mode** — Semgrep has `security-audit` (high FP, informational) and `r2c-security-audit` (lower FP). Only block on confirmed-vulnerability rules.
```yaml
# .semgrep.yml — tiered approach
rules:
  # Block these
  - id: sql-injection
    severity: ERROR
  # Warn only (don't fail pipeline)  
  - id: weak-crypto-usage
    severity: WARNING
```

```bash
# In CI: only fail on ERROR severity
semgrep --config .semgrep.yml --severity ERROR --error
```

2. **No suppression mechanism** — Teams have no way to mark intentional patterns. Add `nosemgrep` inline comments with mandatory justification tracked in a spreadsheet.
```python
user_input = request.args.get('q')  # nosemgrep: direct-use-of-get — sanitized 3 lines below by validate_input()
```

3. **Rule tuning** — For rules with >30% FP rate across the codebase, write path exclusions or custom patterns:
```yaml
paths:
  exclude:
    - "tests/**"
    - "**/*_test.py"
    - "vendor/**"
```

**Prevention:** Measure FP rate per rule quarterly. Any rule with >20% FP rate gets downgraded from `block` to `warn`. Run SAST findings through a JIRA backlog for team triage rather than blocking the PR gate.

---

## Scenario 6: Trivy Blocking on Unfixable CVEs
**Symptom:** CI pipeline fails on `trivy image --exit-code 1 --severity CRITICAL`. The blocking CVE is in OpenSSL embedded in a distroless base image. The CVE has no fix available upstream.

**Diagnosis:**
```bash
# Identify the specific CVE and its fixability
trivy image --severity CRITICAL myapp:v1.2.3 --format json | \
  jq '.Results[].Vulnerabilities[] | select(.Severity=="CRITICAL") | {ID: .VulnerabilityID, Package: .PkgName, FixedVersion: .FixedVersion, Status: .Status}'

# Status: "will_not_fix" or "fix_deferred" = no upstream patch
# Status: "" with empty FixedVersion = no fix yet

# Check if the vulnerability is actually reachable
# Distroless images don't have a shell, so attack surface is minimal
docker inspect myapp:v1.2.3 --format '{{.Config.Entrypoint}}'
```

**Root Causes and Fixes:**

1. **Blocking on unfixable CVEs creates dependency on upstream release timing** — Use `--ignore-unfixed` flag for base image vulnerabilities while still blocking on fixable ones.
```bash
trivy image --severity CRITICAL,HIGH \
  --exit-code 1 \
  --ignore-unfixed \
  myapp:v1.2.3
```

2. **Maintain a `.trivyignore` with justified suppressions** — For CVEs your security team has reviewed and accepted as risk:
```
# .trivyignore
# CVE-2024-XXXXX — OpenSSL in distroless base, no fix available upstream
# Risk accepted 2024-11-01, reviewed by security@company.com, re-review 2025-02-01
CVE-2024-XXXXX
```

3. **Use Chainguard Wolfi-based images** — These update packages daily and have near-zero CVE counts. Often resolves the base image problem entirely.
```dockerfile
FROM cgr.dev/chainguard/python:latest-dev AS builder
FROM cgr.dev/chainguard/python:latest
```

4. **Time-bounded suppression** — Set a calendar reminder for suppressed CVEs. When a fix becomes available, the `.trivyignore` entry should be removed and the image rebuilt.

**Prevention:** Separate the "build fails if there's a fixable critical CVE" gate from "report unfixable CVEs to security dashboard." Fixable = pipeline gate. Unfixable = Jira ticket for review.

---

## Scenario 7: Cosign Verification Failure in Kubernetes Admission
**Symptom:** After enabling Sigstore/Cosign verification via a Kyverno policy, a deployment from CI fails with `image signature verification failed`. The image was signed in the same CI pipeline 10 minutes ago.

**Diagnosis:**
```bash
# Manually verify the signature outside of Kubernetes
cosign verify \
  --certificate-identity-regexp "https://github.com/myorg/myrepo" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  myregistry.azurecr.io/myapp:sha256-abc123.sig

# Check what identities the signature was created with
cosign triangulate myregistry.azurecr.io/myapp:v1.2.3
cosign verify-blob --bundle cosign.bundle --certificate-identity ...

# Check Kyverno policy conditions
kubectl describe clusterpolicy verify-image-signature
kubectl get clusterpolicy verify-image-signature -o yaml | grep -A20 verifyImages
```

**Root Causes and Fixes:**

1. **Certificate identity regexp mismatch** — Keyless signing embeds the GitHub Actions workflow URL in the certificate SAN. The Kyverno policy regexp must match exactly.
```yaml
verifyImages:
- image: "myregistry.azurecr.io/myapp*"
  attestors:
  - entries:
    - keyless:
        subject: "https://github.com/myorg/myrepo/.github/workflows/build.yaml@refs/heads/main"
        issuer: "https://token.actions.githubusercontent.com"
        # Use rekor.sigstore.dev for transparency log verification
        rekor:
          url: https://rekor.sigstore.dev
```
If CI runs on a branch PR, the subject will be `refs/pull/*/merge` not `refs/heads/main`. Use a regexp:
```yaml
subject: "https://github.com/myorg/myrepo/.github/workflows/build.yaml@refs/*"
```

2. **Image re-tagged after signing** — Cosign signs the digest. If the image is re-tagged (same content, different tag), the signature is still valid. If the image is re-pushed with the same tag but different content (new digest), the signature is invalid. Always sign and deploy by digest.
```bash
# In CI: sign by digest, deploy by digest
DIGEST=$(docker buildx build --push --format '{{.Digest}}' .)
cosign sign myregistry.azurecr.io/myapp@$DIGEST
# Kubernetes manifest uses: myregistry.azurecr.io/myapp@sha256:...
```

3. **Rekor transparency log unreachable from cluster** — Keyless verification requires internet access to `rekor.sigstore.dev`. In air-gapped or private clusters, deploy a self-hosted Rekor instance.

**Prevention:** Add `cosign verify` as a final step in the CI pipeline to validate the signature is verifiable before reporting success. This catches signing misconfigurations before they reach admission control.

---

## Scenario 8: SBOM Gap — Critical Package Not in Inventory
**Symptom:** A CVE for a transitive dependency (`libexpat`) is announced. Security team searches the SBOM inventory and finds no affected services. But manual inspection of one service's container reveals `libexpat` is present.

**Diagnosis:**
```bash
# Generate SBOM from the running image (more complete than build-time)
syft myapp:v1.2.3 -o syclone-format-json > sbom.json

# Check if libexpat appears
jq '.artifacts[] | select(.name | contains("libexpat"))' sbom.json

# Compare with what was submitted to the inventory
# If missing, the SBOM generation was incomplete

# Check what generated the gap — OS packages vs language packages
syft myapp:v1.2.3 -o table | grep -E "(deb|rpm|apk)" | head -20

# Trivy also generates SBOMs
trivy image --format spdx-json -o sbom-trivy.json myapp:v1.2.3
```

**Root Causes and Fixes:**

1. **SBOM generated from source code, not the final container image** — Source-code SBOM tools (like `npm audit`, `pip-audit`) miss OS-level packages installed by the Dockerfile. Always generate the SBOM from the built image.
```bash
# In CI, generate SBOM after docker build, before push
syft packages docker:myapp:v1.2.3 -o spdx-json > sbom.spdx.json

# Attach SBOM to the image with cosign
cosign attach sbom --sbom sbom.spdx.json myregistry.azurecr.io/myapp:v1.2.3
```

2. **Multi-stage build — SBOM only scanned the build stage** — The final stage (e.g., `FROM gcr.io/distroless/base`) still has OS packages. Ensure SBOM is generated from the final stage image tag, not the builder.

3. **SBOM not updated on base image pull** — If you `FROM node:18-alpine` and Alpine updates libexpat in a patch release, re-pulling with the same tag gives a different binary. Re-generate and re-publish the SBOM on every image rebuild, even if source code didn't change.

**Prevention:** Automate nightly SBOM regeneration for all production images. Index SBOMs in Dependency Track or Grype DB and set alerts when a new CVE matches any package in any SBOM.
