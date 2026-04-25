---
description: Hard interview questions for DevSecOps, supply chain security, Vault, and runtime security.
---

## Hard

**14. How would you implement a complete DevSecOps pipeline from commit to production with zero static secrets?**

End-to-end design:

1. **Commit:** `git push` triggers pre-commit hooks (Gitleaks, detect-secrets). GitHub push protection blocks known secret patterns at the SCM layer.
2. **PR:** GitHub Actions runs SAST (Semgrep), SCA (Snyk), and secret scanning (Gitleaks on full diff). SonarQube quality gate blocks merge on new critical findings.
3. **Build:** Docker image built with BuildKit. Trivy scans image — pipeline fails on Critical/High CVEs with available fixes. Syft generates SBOM in SPDX format.
4. **Sign:** Cosign signs the image using OIDC keyless signing (no stored key). Signature and SBOM attached to the image in OCI registry.
5. **Staging deploy:** ArgoCD syncs; Kyverno admission webhook verifies image is signed before allowing it to be scheduled.
6. **DAST:** OWASP ZAP baseline scan against staging. Results uploaded as SARIF to GitHub Security.
7. **Production:** ArgoCD auto-promotes only after DAST passes and staging smoke tests succeed.
8. **Runtime:** Falco monitors for anomalous syscalls (shell spawned in API container, unexpected file write). Alert routes to PagerDuty.

**No static secrets anywhere:** OIDC replaces CI cloud credentials, Vault dynamic secrets replace DB passwords, Kubernetes Workload Identity eliminates pod credentials.

**15. What is OPA Gatekeeper and how does it differ from Kyverno? When would you choose each?**

Both are Kubernetes admission controllers that enforce policy as code.

**OPA Gatekeeper:**
- Uses Rego (a declarative logic language) to write policies as `ConstraintTemplate` + `Constraint` pairs.
- Runs as a validating admission webhook — blocking non-compliant resources.
- Pro: Extremely expressive; can enforce complex cross-object policies.
- Con: Rego has a steep learning curve; debugging is harder.

**Kyverno:**
- Uses YAML-native policy language — no separate DSL to learn.
- Supports validate, mutate, generate, and verify image operations in one tool.
- Pro: Low barrier to entry; mutation (auto-adding labels, sidecars) is first-class.
- Con: Complex cross-resource logic is less expressive than Rego.

**Choose OPA/Gatekeeper** when you have a dedicated security team that can invest in Rego and need complex cross-resource policy logic or already use OPA for other policy needs (e.g., Terraform Sentinel). **Choose Kyverno** when developer experience matters, you need mutation policies, or your team prefers YAML over a separate language.

**16. What is SLSA and what does Level 2 vs Level 3 mean in practice?**

SLSA (Supply chain Levels for Software Artifacts) is a framework for supply chain integrity:

| Level | Key Requirement | What it Means in Practice |
|:---|:---|:---|
| L1 | Build provenance exists | CI generates a signed attestation of how the artifact was built |
| L2 | Hosted build, signed provenance | Provenance is signed by the CI platform (GitHub Actions OIDC); not just self-signed |
| L3 | Hardened build, non-falsifiable | Build runs in an isolated, hermetic environment; no network access during build; provenance cannot be forged even by a malicious insider |
| L4 | Two-party review, hermetic build | Every dependency is fully auditable; requires binary-identical, reproducible builds |

**L2 in practice (common for regulated industries):**
- Use GitHub Actions provenance generation (`slsa-framework/slsa-github-generator`)
- Sign with OIDC-backed Sigstore/Cosign
- Verify in admission controller: Kyverno checks that all pods reference images with valid SLSA L2 attestation

**L3** requires hermetic builds — no external network calls during build, all dependencies pinned and verified. Requires containerized builds with network policy blocking egress.

**17. How does Falco detect runtime threats and how do you tune it for low false positives?**

Falco is a runtime security tool that uses the Linux kernel's eBPF or kernel module to observe syscalls in real time and match them against rules.

**How it works:**
```
App runs in container → spawns /bin/bash → Falco sees execve() syscall → 
matches rule: "Shell spawned in container with web server process" → Alert
```

**Tuning for production:**
1. Start in `--dry-run` mode — log matches without alerting to understand baseline.
2. **Macros for exclusions:** Create macros to exclude known-good patterns:
   ```yaml
   - macro: allowed_init_containers
     condition: k8s.ns.name = "kube-system" and container.image startswith "registry.k8s.io"
   ```
3. **Priority thresholds:** Only alert on `WARNING` and above; log `NOTICE` to a cold storage bucket.
4. **Custom rules for your environment:** Write rules matching your specific risk model (e.g., alert on `aws configure` in any container — likely credential theft).
5. **Route alerts by severity:** Critical → PagerDuty, Warning → Slack, Notice → Elasticsearch.

**18. What is SBOM and how is it used beyond just generating the file?**

An SBOM (Software Bill of Materials) is a machine-readable inventory of all components in a software artifact — OS packages, language dependencies, transitive dependencies, and their versions.

**Beyond generation — how it's actually used:**

1. **Continuous vulnerability monitoring:** Upload SBOM to Dependency-Track (OWASP). When a new CVE is published, Dependency-Track matches it against all SBOMs in its database and alerts — without re-scanning images. You learn about vulnerabilities in already-deployed software within minutes.
2. **License compliance:** Identify GPL-licensed dependencies in a commercial product. Block dependencies with restricted licenses via policy.
3. **Incident response:** When Log4Shell dropped, organizations with SBOMs queried them in minutes to find affected services. Those without SBOMs spent days doing manual inventory.
4. **Regulatory compliance:** US Executive Order 14028 requires SBOMs for software sold to the US government. EU Cyber Resilience Act similarly mandates them.
5. **Supply chain verification:** Combine SBOM with attestation (Cosign `attest`) to cryptographically prove the SBOM is accurate and was produced by your trusted CI pipeline.

**19. How do you implement zero-trust network security in Kubernetes?**

Zero-trust: "never trust, always verify" — no implicit trust based on network location.

1. **Default-deny NetworkPolicy:** Apply a deny-all ingress and egress policy to every namespace. Then explicitly allow only required flows.
   ```yaml
   kind: NetworkPolicy
   spec:
     podSelector: {}
     policyTypes: [Ingress, Egress]
     # No ingress or egress rules = deny all
   ```
2. **mTLS via service mesh:** Istio or Linkerd enforce mutual TLS on all pod-to-pod communication. Only pods with valid certificates issued by the mesh CA can communicate — no reliance on IP-based trust.
3. **JWT-based authorization policy:** Istio `AuthorizationPolicy` requires a valid JWT signed by your identity provider before a request is forwarded to a service.
4. **Workload Identity:** Pods authenticate to cloud services (AWS, GCP) via IRSA/Workload Identity — short-lived tokens scoped to the specific workload.
5. **Egress restriction:** Block all internet egress from production namespaces. Only allow specific endpoints (package registries, APIs) via egress NetworkPolicy or a proxy allowlist.

**20. How do you detect and respond to a compromised CI/CD pipeline?**

Threat model: a malicious PR merges code that exfiltrates secrets or injects backdoors into the build artifact.

**Detection:**
- Monitor for unusual outbound connections from build runners (egress network policy + DNS logging).
- Alert on jobs that access secrets not declared in their manifest.
- Monitor for build artifacts that differ from prior versions in unexpected ways (diff artifact checksums).
- Audit OIDC token issuance — every token request is logged; unusual patterns (midnight builds, unfamiliar repos) trigger alerts.

**Response:**
1. Revoke all secrets that were accessible to the compromised job immediately.
2. Invalidate all artifacts produced during the window of compromise.
3. Trigger a re-scan of all images built during the window with updated CVE databases.
4. Identify the exact commit that caused compromise and revert.
5. Strengthen: require code review from security team on changes to CI workflow files (`.github/workflows/*.yml`); use GitHub's "required reviewers for workflow changes" setting.
