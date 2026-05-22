# DevSecOps — Interview Prep

---
description: Easy interview questions for DevSecOps, security scanning, and application security fundamentals.
---

```
DevSecOps — Easy Interview Topics
├── Core Concepts
│   ├── DevSecOps definition and shift-left principle
│   ├── SAST vs DAST (when each runs, what each finds)
│   └── CVE, CVSS scoring (0-10 scale, categories)
├── Scanning & Detection
│   ├── Container image scanning (Trivy, Grype)
│   ├── SCA — open-source dependency CVEs
│   ├── Secret scanning (Gitleaks, GitHub push protection)
│   └── Pinned base images (prevent upstream surprises)
├── Access Control
│   ├── Least privilege in CI/CD (no admin tokens in pipelines)
│   └── Kubernetes Secrets (base64, not encrypted by default)
├── Supply Chain Basics
│   ├── Image signing (Cosign + Kyverno admission enforcement)
│   └── Vulnerability vs exploit (EPSS probability score)
└── Network Security
    ├── Network Security Groups / NSGs (inbound + egress)
    └── Kubernetes NetworkPolicy egress rules
```

### First Principles

Security found late is expensive to fix. Shift security left — run checks where developers already work (in CI). Code has vulnerabilities (SAST), dependencies have vulnerabilities (SCA), running apps have vulnerabilities (DAST). Secrets in code are permanent leaks — scan for them. Supply chain: verify what you build is what you ship (SLSA, SBOM, signing).

## Easy

**1. What is DevSecOps?**

DevSecOps integrates security practices into the DevOps process. The goal is to automate and embed security at every stage of the software lifecycle — from design to deployment — rather than treating it as a gate at the end. The term "shift left" describes moving security checks earlier in the pipeline.

**2. What is the difference between SAST and DAST?**

- **SAST (Static Application Security Testing):** A "white-box" method that scans source code or binaries for vulnerabilities without running the code. Runs in CI on every commit. Tools: SonarQube, Semgrep, CodeQL.
- **DAST (Dynamic Application Security Testing):** A "black-box" method that tests the running application by sending crafted requests to find runtime vulnerabilities. Runs against a deployed staging environment. Tools: OWASP ZAP, Burp Suite Enterprise.

**3. What is a CVE and how does it relate to container scanning?**

CVE (Common Vulnerabilities and Exposures) is a publicly catalogued record of a specific software vulnerability (e.g., CVE-2021-44228 is Log4Shell). Container scanning tools (Trivy, Grype, Snyk) analyze image layers, identify installed OS packages and application dependencies, and match them against CVE databases to surface known vulnerabilities.

**4. Why use specific versions for base images instead of `latest`?**

Using `latest` leads to unpredictable builds — the tag can be updated at any time with breaking changes or new vulnerabilities. Pinning to a specific version (`python:3.11.9-slim`) ensures deterministic, reproducible builds where security posture is known at build time.

**5. What is the principle of least privilege in CI/CD?**

The pipeline's service account should have only the minimum permissions necessary — for example, permission to push to a specific container registry or deploy to a specific Kubernetes namespace. This limits blast radius if credentials are compromised or a pipeline is abused.

**6. What is a Kubernetes Secret and what is the problem with the default approach?**

A Kubernetes Secret stores sensitive data as base64-encoded values in etcd. Base64 is encoding, not encryption — anyone with `kubectl get secret` access can decode the values instantly. Mitigations: encrypt etcd at rest, use External Secrets Operator with Vault, enforce RBAC to restrict who can read secrets, and disable automounting of service account tokens in pods that don't need API access.

**7. What is image signing and why does it matter?**

Image signing cryptographically attests that a container image was produced by a trusted source and has not been tampered with since. Tools like Cosign (Sigstore) sign images and attach the signature to an OCI registry. Admission controllers (Kyverno, Gatekeeper) can reject unsigned or unverified images, preventing supply chain attacks where a rogue image is substituted.

**8. What is SCA (Software Composition Analysis)?**

SCA analyzes your application's third-party dependencies (npm packages, pip packages, Maven JARs) and matches them against known vulnerability databases (NVD, OSV). Tools: Snyk, OWASP Dependency-Check, `pip-audit`, `npm audit`. SCA differs from SAST in that it looks at your dependencies, not your own code.

**9. What is secret scanning in the context of source code?**

Secret scanning searches source code, commit history, and CI logs for accidentally committed credentials — API keys, AWS access keys, database passwords, private keys. Tools like Gitleaks and GitHub's native secret scanning can be run as pre-commit hooks, in CI, and as a continuous monitoring background scan on the repository. GitHub Secret Scanning with push protection blocks the push at the server level if a known secret pattern is detected.

**10. What is CVSS and how is it used to prioritize vulnerabilities?**

CVSS (Common Vulnerability Scoring System) is a numerical score (0-10) measuring vulnerability severity based on factors like: exploitability, attack vector (network vs local), required privileges, and impact on confidentiality/integrity/availability. Categories: None (0), Low (0.1–3.9), Medium (4.0–6.9), High (7.0–8.9), Critical (9.0–10.0). Use CVSS as a starting point but consider context: a Critical CVE in a library that's not actually reachable from your code path is lower risk than a High CVE that's directly exploitable.

**11. What is the difference between a vulnerability and an exploit?**

A **vulnerability** is a weakness in software (a bug, misconfiguration, or design flaw). An **exploit** is a working method of taking advantage of that vulnerability. Not all vulnerabilities have public exploits — a High CVE without a known exploit has lower immediate risk than a Medium CVE with an active exploit in the wild. Tools like EPSS (Exploit Prediction Scoring System) estimate the probability that a CVE will be exploited in the next 30 days, helping prioritize remediation.

**12. What is a network security group / firewall and why is egress filtering important?**

Network security groups (AWS: Security Groups; Azure: NSGs) are stateful firewalls controlling inbound and outbound traffic. Most teams configure inbound rules carefully but leave egress wide open. Egress filtering matters because: compromised containers or servers may attempt to exfiltrate data or phone home to attacker-controlled servers. Restricting outbound connections to known good destinations (package registries, APIs) limits the blast radius of a compromise. In Kubernetes, NetworkPolicy egress rules enforce pod-level egress restrictions.

### System Design Perspective

**Policy as Code (OPA/Gatekeeper):** The easy questions cover scanning tools and access control concepts, but enforcement at the Kubernetes API boundary is a critical missing layer. When a developer runs `kubectl apply`, OPA Gatekeeper's validating webhook intercepts the request and runs Rego policies before any resource is created. This catches misconfigurations (missing `runAsNonRoot`, wrong registry, missing resource limits) that scanning might not surface.

**Runtime Security (Falco):** Scanning happens before deployment; Falco watches what processes do after they are running. A container that passes all scans can still be exploited at runtime — Falco detects the behavior (shell spawn, sensitive file read, unexpected outbound connection) and fires an alert. Start with Falco's default rules in audit mode before enforcing.

**Zero-Trust Principles:** Egress filtering (NetworkPolicy) is one piece. Full zero-trust requires: mTLS between all services (Istio/Linkerd), identity-based authorization (not IP-based), short-lived credentials (Vault dynamic secrets), and continuous verification (no implicit trust based on network location).

---
description: Medium-difficulty interview questions for DevSecOps — supply chain security, Vault, policy enforcement, and secure pipelines.
---

```
DevSecOps — Medium Interview Topics
├── Least Privilege CI/CD
│   ├── OIDC federation (IRSA, Workload Identity) — no static creds
│   └── Pipeline role scoped to specific namespace / service
├── Image Scanning + SBOM in Delivery Pipeline
│   ├── Trivy / Grype after docker build (--exit-code 1 on HIGH+)
│   └── Syft SBOM → Dependency-Track continuous monitoring
├── HashiCorp Vault vs Kubernetes Secrets
│   ├── Vault: dynamic creds, TTL, audit log, encrypted storage
│   └── K8s Secrets: base64 in etcd (not encrypted unless configured)
├── mTLS and Service Meshes
│   ├── Standard TLS: server authenticates to client
│   ├── mTLS: both parties present certificates
│   └── Istio / Linkerd automate mTLS without app code changes
├── Software Supply Chain Attacks
│   ├── Dependency confusion, typosquatting, compromised CI
│   └── Defenses: SLSA, Cosign, SBOM, pinned hashes, ephemeral builders
├── Kubernetes Service Account Security
│   ├── Default SA token auto-mounted (exploitable via shell access)
│   └── Mitigations: automountServiceAccountToken: false, projected tokens
├── Policy as Code
│   ├── OPA Gatekeeper (Rego, ConstraintTemplate + Constraint)
│   └── Kyverno (YAML-native, validate/mutate/generate)
├── External Secrets Operator
│   ├── SecretStore (connection + auth to external store)
│   ├── ExternalSecret (maps external key → K8s Secret)
│   └── Only the ESO manifest in Git, not actual secret values
└── Cosign Keyless Signing
    ├── OIDC → Fulcio short-lived cert → sign image digest
    └── Signature in Rekor (public transparency log) — no key storage
```

### First Principles

Security found late is expensive to fix. Shift security left — run checks where developers already work (in CI). Code has vulnerabilities (SAST), dependencies have vulnerabilities (SCA), running apps have vulnerabilities (DAST). Secrets in code are permanent leaks — scan for them. Supply chain: verify what you build is what you ship (SLSA, SBOM, signing).

## Medium

**8. What is least privilege for a CI/CD system in practice?**

The pipeline should have only the permissions needed for its specific job. A build job needs read access to source and write access to the artifact registry. A deploy job needs only the permissions to update the specific service in the target namespace — not cluster-admin. Implement this via IRSA (AWS), Workload Identity (GCP/Azure), or OIDC federation so no static credentials exist.

**9. What does image scanning and SBOM generation look like in a delivery pipeline?**

After `docker build`, run Trivy or Grype against the image. If critical/high CVEs are found matching a policy (e.g., CVSS > 7 with a fix available), fail the pipeline. Generate an SBOM using Syft in CycloneDX or SPDX format and publish it alongside the image in the registry. The SBOM serves as a persistent record for vulnerability tracking — tools like Dependency-Track monitor SBOMs continuously and alert when new CVEs affect already-deployed versions.

**10. What is HashiCorp Vault and how does it improve on Kubernetes Secrets?**

Vault provides: dynamic secrets generated on-demand with TTLs (e.g., short-lived database credentials rotated per request), centralized access control with full audit logging of every secret access, secrets versioning and automatic rotation, and multiple auth methods (Kubernetes, OIDC, AWS IAM). Unlike Kubernetes Secrets (base64-encoded in etcd), Vault encrypts at rest with its own seal key and provides an immutable audit trail showing exactly who accessed which secret and when.

**11. What is mutual TLS (mTLS) and where is it used in Kubernetes?**

Standard TLS authenticates the server to the client. mTLS additionally authenticates the client to the server — both parties present certificates. In Kubernetes, service meshes (Istio, Linkerd, Cilium) enforce mTLS between every pod-to-pod communication automatically, without application code changes. This ensures only pods with valid certificates (issued by the mesh's certificate authority) can communicate — zero-trust at the network layer.

**12. What is the software supply chain and what attacks target it?**

The software supply chain is the path from source code through build, dependency resolution, packaging, and deployment. Supply chain attacks target each stage: compromising a popular npm/PyPI package (dependency confusion, typosquatting), injecting malicious code via a compromised CI runner, hijacking build environment credentials, or tampering with an artifact between build and deployment. Defenses: SLSA framework, artifact signing (Cosign/Sigstore), SBOM generation, pinned dependency hashes, and isolated ephemeral build environments.

**13. What is a Kubernetes Service Account and what are the security risks of the default?**

Every pod runs with a ServiceAccount that determines what the pod can do via RBAC. By default, pods use the `default` service account, which may have accumulated permissions over time. The service account token is auto-mounted inside the pod at `/var/run/secrets/kubernetes.io/serviceaccount/token`. An attacker with shell access to the pod can use this token to call the Kubernetes API. Mitigation: set `automountServiceAccountToken: false` on pods that don't need API access, create dedicated service accounts with minimal RBAC, and use projected token volumes with short TTLs.

**14. What is Policy as Code and how is it implemented in a Kubernetes cluster?**

Policy as Code defines security and compliance requirements as version-controlled, automated policies — not manual review checklists. In Kubernetes:
- **OPA Gatekeeper:** Policies written in Rego; deployed as `ConstraintTemplate` + `Constraint`. Runs as a validating admission webhook.
- **Kyverno:** YAML-native policies for validate, mutate, and generate operations. Simpler for teams unfamiliar with Rego.

Example policies: "All pods must run as non-root," "All images must come from our approved registry," "All Deployments must have resource limits set."

**15. How does the External Secrets Operator work?**

External Secrets Operator (ESO) bridges Kubernetes and external secret stores (Vault, AWS Secrets Manager, Azure Key Vault, GCP Secret Manager):

1. Install ESO in the cluster.
2. Create a `SecretStore` (or `ClusterSecretStore`) that defines the connection to the external secret store and authentication method.
3. Create an `ExternalSecret` resource specifying which external secret to fetch and how to map it to a Kubernetes `Secret`.
4. ESO fetches the secret, creates/updates the Kubernetes `Secret`, and periodically refreshes it.

This keeps secrets out of Git (only the `ExternalSecret` manifest is in Git, not the actual values) while making secrets available to pods as standard Kubernetes Secrets.

**16. What is Cosign and what is keyless signing?**

Cosign (by Sigstore) is a tool for signing and verifying container images and other artifacts. **Keyless signing** (the recommended approach) uses OIDC identity instead of a long-lived private key:

1. The CI pipeline authenticates to Sigstore's Fulcio CA via OIDC (GitHub Actions, GitLab CI, Google).
2. Fulcio issues a short-lived certificate binding the image digest to the CI job's identity (e.g., `https://github.com/org/repo/.github/workflows/release.yml@refs/heads/main`).
3. The signature is stored in Sigstore's public transparency log (Rekor).
4. Verification queries Rekor — no private key storage needed anywhere.

This means: even if your CI/CD system is compromised, the attacker cannot forge signatures for a different repository or workflow.

### System Design Perspective

**Secret Rotation Design:** ESO fetches secrets and the `refreshInterval` controls refresh frequency, but rotation of the underlying secret in Vault or AWS Secrets Manager is a separate concern. For Vault dynamic secrets: the lease TTL drives rotation automatically. For static API keys in AWS Secrets Manager: create a rotation Lambda that calls the external API to generate a new key, updates the secret version, then bumps the ESO `ExternalSecret` annotation to force immediate refresh. Alert via CloudWatch if rotation fails — a failed rotation that goes undetected means credentials expire and services break silently.

**Zero-Trust Depth:** mTLS (covered here) handles the transport layer. Complete zero-trust also requires: (1) Istio `AuthorizationPolicy` to enforce which service can call which HTTP path — not just "can connect" but "can call POST /payments", (2) short-lived workload tokens (SPIFFE/SPIRE) instead of long-lived service account tokens, (3) continuous re-verification (token refresh every 15 minutes rather than once at startup).

**Falco for Runtime Policy:** OPA Gatekeeper enforces policy at admission (before pods run). Falco enforces policy at runtime (while pods are running). The combination provides defense-in-depth: Gatekeeper prevents misconfigured workloads from starting; Falco detects exploits in correctly-configured workloads that slip through.

---
description: Hard interview questions for DevSecOps, supply chain security, Vault, and runtime security.
---

```
DevSecOps — Hard Interview Topics
├── Complete Pipeline Design (commit → prod, zero static secrets)
│   ├── OIDC federation for CI (no long-lived credentials)
│   ├── Stage order: SAST → SCA → Build → Sign → Attest → Scan → Deploy
│   └── Vault Agent / ESO for runtime secret injection
├── Policy as Code
│   ├── OPA Gatekeeper (Rego, ConstraintTemplate, Constraint)
│   ├── Kyverno (YAML-native, validate/mutate/generate)
│   └── failurePolicy, dryrun → warn → deny progression
├── SLSA L2 vs L3
│   ├── L2: hosted build, provenance published
│   └── L3: hardened builder, hermetic, non-falsifiable provenance
├── Runtime Security (Falco)
│   ├── eBPF kernel syscall interception
│   ├── Rule tuning (macro overrides, Falcosidekick routing)
│   └── Alert categories: spawned shell, sensitive file read, outbound
├── SBOM Uses Beyond Generation
│   ├── Dependency-Track continuous CVE monitoring
│   ├── License compliance (GPL in commercial software)
│   ├── Incident response (Log4Shell — find affected services in minutes)
│   └── Regulatory (US EO 14028, EU Cyber Resilience Act)
├── Zero-Trust in Kubernetes
│   ├── Default-deny NetworkPolicy (ingress + egress)
│   ├── mTLS via Istio/Linkerd (SPIFFE SVIDs)
│   ├── JWT AuthorizationPolicy (identity-based, not IP-based)
│   ├── IRSA / Workload Identity (short-lived cloud credentials)
│   └── Egress restriction (proxy allowlist)
└── Compromised CI/CD Detection & Response
    ├── Detect: outbound connections, secret access anomalies, checksum diff
    ├── Respond: revoke secrets, invalidate artifacts, revert commit
    └── Harden: required reviewers for workflow file changes
```

### First Principles

Security found late is expensive to fix. Shift security left — run checks where developers already work (in CI). Code has vulnerabilities (SAST), dependencies have vulnerabilities (SCA), running apps have vulnerabilities (DAST). Secrets in code are permanent leaks — scan for them. Supply chain: verify what you build is what you ship (SLSA, SBOM, signing).

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

### System Design Perspective

**Secret Rotation at Scale:** This file covers zero static secrets at pipeline time, but secret rotation for long-lived application secrets needs explicit design. For database credentials: Vault dynamic secrets rotate per-request (TTL=1h). For API keys that third-party systems require to be static: AWS Secrets Manager rotation Lambda updates the key in the external system, writes the new version, then triggers a rolling restart via `kubectl rollout restart`. Monitor `SecretVersionStage` to detect stale secret versions in use.

**OPA Policy Testing Pipeline:** Before `ConstraintTemplate` policies reach a cluster, test them with `conftest` against known-bad YAML fixtures. Store policies and fixtures in a separate Git repo, run `opa test` in CI, and use ArgoCD/Flux to sync policies to clusters — the same GitOps workflow used for application manifests ensures policy changes are reviewed, tested, and auditable.

---

## Hard (continued) — Supply Chain Internals, Rego Policy Testing, Falco Rules, SPIFFE/SPIRE & Secret Rotation

---

**Q: Explain SLSA build provenance in depth. How does a verifier validate a Level 3 attestation using Sigstore?**

SLSA (Supply chain Levels for Software Artifacts) defines four levels of build integrity guarantees. At Level 3:
- Build platform is hosted (not run by the developer)
- Build is isolated per-build (no shared state between builds)
- Provenance is generated by the build platform itself (not by build scripts the developer controls)
- Provenance is signed with a key the developer cannot access

**Provenance Format (SLSA ProvenanceV1):**

```json
{
  "_type": "https://in-toto.io/Statement/v1",
  "subject": [{
    "name": "pkg:oci/myimage@sha256:abc123",
    "digest": {"sha256": "abc123..."}
  }],
  "predicateType": "https://slsa.dev/provenance/v1",
  "predicate": {
    "buildDefinition": {
      "buildType": "https://github.com/slsa-framework/slsa-github-generator/...@refs/tags/v1.9.0",
      "externalParameters": {
        "workflow": {
          "ref": "refs/heads/main",
          "repository": "https://github.com/myorg/myrepo",
          "path": ".github/workflows/build.yml"
        }
      }
    },
    "runDetails": {
      "builder": {"id": "https://github.com/slsa-framework/slsa-github-generator/.github/workflows/generator_container_slsa3.yml@refs/tags/v1.9.0"},
      "metadata": {
        "invocationId": "https://github.com/myorg/myrepo/actions/runs/1234567890",
        "startedOn": "2026-05-22T10:00:00Z"
      }
    }
  }
}
```

**Generating SLSA Level 3 Provenance in GitHub Actions:**

```yaml
jobs:
  build:
    uses: slsa-framework/slsa-github-generator/.github/workflows/generator_container_slsa3.yml@v1.9.0
    with:
      image: ghcr.io/myorg/myimage
      digest: ${{ needs.build.outputs.digest }}
    secrets:
      registry-username: ${{ github.actor }}
      registry-password: ${{ secrets.GITHUB_TOKEN }}
```

The SLSA GitHub Generator runs in an isolated GitHub-hosted runner. It signs the provenance using **keyless signing via Sigstore Fulcio** (a short-lived certificate tied to the OIDC identity of the GitHub Actions workflow):

1. GitHub Actions workflow presents its OIDC token to **Fulcio** (Sigstore's certificate authority)
2. Fulcio issues a short-lived X.509 certificate binding the certificate to the workflow identity (`https://github.com/myorg/myrepo/.github/workflows/build.yml@refs/heads/main`)
3. The provenance is signed with the ephemeral key
4. The signature + certificate chain is recorded in **Rekor** (Sigstore's transparency log)

**Verification with `cosign` and `slsa-verifier`:**

```bash
# Verify the container image has valid SLSA Level 3 provenance
slsa-verifier verify-image ghcr.io/myorg/myimage@sha256:abc123 \
  --source-uri github.com/myorg/myrepo \
  --source-branch main \
  --builder-id https://github.com/slsa-framework/slsa-github-generator/.github/workflows/generator_container_slsa3.yml@refs/tags/v1.9.0

# What the verifier checks:
# 1. Subject digest matches the image being verified
# 2. Signature is valid against the certificate
# 3. Certificate was issued by Fulcio (trusted CA)
# 4. Certificate identity matches expected builder
# 5. Rekor entry exists (inclusion proof in transparency log)
# 6. Build was triggered from expected source repo/branch

# Also verify via cosign:
cosign verify-attestation --type slsaprovenance \
  --certificate-identity-regexp "https://github.com/slsa-framework/slsa-github-generator" \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com \
  ghcr.io/myorg/myimage@sha256:abc123
```

**VEX Documents:** When a CVE scanner reports a vulnerability in a dependency, VEX (Vulnerability Exploitability eXchange) lets you assert "this vulnerability does not affect this product in this context":

```json
{
  "@context": "https://openvex.dev/ns/v0.2.0",
  "@id": "https://openvex.dev/docs/public/vex-xxx",
  "author": "security-team@myorg.com",
  "timestamp": "2026-05-22T00:00:00Z",
  "statements": [{
    "vulnerability": {"@id": "https://nvd.nist.gov/vuln/detail/CVE-2026-12345"},
    "products": [{"@id": "pkg:oci/myimage@sha256:abc123"}],
    "status": "not_affected",
    "justification": "vulnerable_code_not_in_execute_path",
    "impact_statement": "The vulnerable function in libfoo is only reachable via CLI flag --legacy which is disabled in this image's ENTRYPOINT"
  }]
}
```

Integrate VEX into your CI pipeline: `vexctl attest` attaches the VEX document as an in-toto attestation to the image, allowing downstream scanners to suppress the finding rather than producing a false positive.

---

**Q: Write a Rego policy that enforces Kubernetes pod security (no privileged containers, required labels, non-root). Show how to test it with `opa test`.**

**ConstraintTemplate:**

```yaml
apiVersion: templates.gatekeeper.sh/v1beta1
kind: ConstraintTemplate
metadata:
  name: k8spodsecurity
spec:
  crd:
    spec:
      names:
        kind: K8sPodSecurity
      validation:
        openAPIV3Schema:
          properties:
            requiredLabels:
              type: array
              items:
                type: string
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8spodsecurity

        violation[{"msg": msg}] {
          container := input.review.object.spec.containers[_]
          container.securityContext.privileged == true
          msg := sprintf("container '%v' must not run as privileged", [container.name])
        }

        violation[{"msg": msg}] {
          container := input.review.object.spec.containers[_]
          not container.securityContext.runAsNonRoot
          msg := sprintf("container '%v' must set runAsNonRoot: true", [container.name])
        }

        violation[{"msg": msg}] {
          label := input.parameters.requiredLabels[_]
          not input.review.object.metadata.labels[label]
          msg := sprintf("pod is missing required label '%v'", [label])
        }
```

**Constraint:**

```yaml
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sPodSecurity
metadata:
  name: enforce-pod-security
spec:
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Pod"]
    namespaces: ["production"]
  parameters:
    requiredLabels: ["app", "team", "version"]
```

**Unit Tests with `opa test`:**

```rego
# k8spodsecurity_test.rego
package k8spodsecurity

# Helper: compliant pod input
compliant_pod := {
  "review": {
    "object": {
      "metadata": {
        "labels": {"app": "checkout", "team": "payments", "version": "v1.2.3"}
      },
      "spec": {
        "containers": [{
          "name": "main",
          "image": "checkout:v1.2.3",
          "securityContext": {
            "privileged": false,
            "runAsNonRoot": true
          }
        }]
      }
    }
  },
  "parameters": {"requiredLabels": ["app", "team", "version"]}
}

# Helper: privileged pod
privileged_pod := json.patch(compliant_pod, [
  {"op": "replace", "path": "/review/object/spec/containers/0/securityContext/privileged", "value": true}
])

# Helper: missing label pod
missing_label_pod := json.patch(compliant_pod, [
  {"op": "remove", "path": "/review/object/metadata/labels/team"}
])

test_compliant_pod_has_no_violations {
  count(violation) == 0 with input as compliant_pod
}

test_privileged_container_is_violation {
  violations := violation with input as privileged_pod
  count(violations) == 1
  violations[_].msg == "container 'main' must not run as privileged"
}

test_missing_required_label_is_violation {
  violations := violation with input as missing_label_pod
  count(violations) == 1
  violations[_].msg == "pod is missing required label 'team'"
}
```

```bash
# Run tests
opa test k8spodsecurity.rego k8spodsecurity_test.rego -v

# Test against real YAML fixtures with conftest
conftest test deployment.yaml --policy ./policies/ --namespace main

# Test Gatekeeper constraint locally before applying to cluster
kubectl apply --dry-run=server -f pod.yaml
```

---

**Q: Write a production Falco rule to detect container escape via `nsenter` or `proc` filesystem access. Explain the syscall-based detection model.**

Falco hooks into the Linux kernel via eBPF (or kernel module) to intercept every syscall. Rules are evaluated against a stream of syscall events; when a rule matches, Falco emits an alert.

**Rule Anatomy:**

```yaml
- rule: Container Escape via nsenter
  desc: Detect use of nsenter to escape container namespaces
  condition: >
    spawned_process and
    container and
    proc.name = "nsenter" and
    not proc.pname in (allowed_shell_binaries)
  output: >
    Container escape attempt via nsenter
    (user=%user.name user_uid=%user.uid command=%proc.cmdline
     container_id=%container.id image=%container.image.repository)
  priority: CRITICAL
  tags: [container, escape, mitre_privilege_escalation]

- rule: Proc Filesystem Read Outside Container
  desc: Process inside container reading host /proc entries (potential escape recon)
  condition: >
    open_read and
    container and
    fd.name startswith "/proc/" and
    not fd.name startswith "/proc/self" and
    not fd.name startswith "/proc/thread-self" and
    not proc.name in (allowed_proc_readers)
  output: >
    Suspicious /proc read from container
    (user=%user.name file=%fd.name proc=%proc.name
     container_id=%container.id image=%container.image.repository)
  priority: WARNING
  tags: [container, filesystem, mitre_discovery]

- list: allowed_shell_binaries
  items: [bash, sh, dash, zsh]

- list: allowed_proc_readers
  items: [ps, top, htop, netstat, ss, cat]

- macro: spawned_process
  condition: evt.type = execve and evt.dir = <

- macro: open_read
  condition: >
    evt.type in (open, openat, openat2) and
    evt.dir = < and
    (evt.arg.flags contains O_RDONLY or not evt.arg.flags contains O_WRONLY)
```

**Deploying Falco on Kubernetes:**

```yaml
# values.yaml for Falco Helm chart
falco:
  grpc:
    enabled: true
  grpcOutput:
    enabled: true

driver:
  kind: ebpf          # Preferred over kernel module; no DKMS required

falcosidekick:
  enabled: true
  config:
    slack:
      webhookurl: "https://hooks.slack.com/..."
      minimumpriority: WARNING
    pagerduty:
      routingKey: "xxx"
      minimumpriority: CRITICAL
```

```bash
helm repo add falcosecurity https://falcosecurity.github.io/charts
helm install falco falcosecurity/falco \
  --namespace falco --create-namespace \
  -f values.yaml \
  --set falco.rules_file[0]=/etc/falco/falco_rules.yaml \
  --set falco.rules_file[1]=/etc/falco/custom_rules.yaml
```

**Tuning to Reduce Noise:** Start with `priority: WARNING` rules and monitor FP rate. Add exclusion macros for known-safe processes:

```yaml
- macro: trusted_privileged_containers
  condition: >
    container.image.repository in (
      "prometheus/node-exporter",
      "datadog/agent",
      "newrelic/infrastructure"
    )

# Update rules to exclude trusted containers
condition: ... and not trusted_privileged_containers
```

**eBPF vs Kernel Module trade-off:** eBPF runs in a sandboxed verifier (safe, no kernel crash risk, works on GKE/EKS without special flags). Kernel module has lower overhead but requires DKMS and can crash the node on kernel mismatch.

---

**Q: Implement SPIFFE/SPIRE for workload identity in a Kubernetes + VM hybrid environment.**

SPIFFE (Secure Production Identity Framework for Everyone) defines a standard for workload identity. SPIRE (SPIFFE Runtime Environment) is the reference implementation. Every workload gets a cryptographic identity (SVID — SPIFFE Verifiable Identity Document) without managing long-lived secrets.

**Architecture:**

```
┌─────────────────────────────────────────────────┐
│ SPIRE Server (control plane)                     │
│  - Stores registration entries                   │
│  - Issues SVIDs signed by its CA                 │
│  - Federation with other SPIRE servers           │
└──────────────────┬──────────────────────────────┘
                   │ Attested via node attestation
          ┌────────┴─────────┐
          │                  │
   ┌──────▼──────┐    ┌─────▼──────┐
   │ SPIRE Agent │    │ SPIRE Agent │
   │ (k8s node)  │    │ (VM / EC2)  │
   └──────┬──────┘    └─────┬──────┘
          │                  │
   Pods/workloads           VMs/processes
   get SVIDs via            get SVIDs via
   Unix socket              Unix socket
```

**Kubernetes Deployment:**

```yaml
# SPIRE Server
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: spire-server
  namespace: spire
spec:
  replicas: 1
  template:
    spec:
      containers:
        - name: spire-server
          image: ghcr.io/spiffe/spire-server:1.9.4
          args:
            - -config
            - /run/spire/config/server.conf
          volumeMounts:
            - name: spire-config
              mountPath: /run/spire/config
              readOnly: true
---
# server.conf
server {
  bind_address = "0.0.0.0"
  bind_port = "8081"
  trust_domain = "example.org"
  data_dir = "/run/spire/data"
  log_level = "INFO"
  ca_ttl = "168h"
  default_x509_svid_ttl = "1h"
}

plugins {
  DataStore "sql" {
    plugin_data {
      database_type = "sqlite3"
      connection_string = "/run/spire/data/datastore.sqlite3"
    }
  }
  NodeAttestor "k8s_psat" {
    plugin_data {
      clusters = {
        "prod-cluster" = {
          service_account_allow_list = ["spire:spire-agent"]
        }
      }
    }
  }
  KeyManager "memory" {}
}
```

**Registration Entries:**

```bash
# Register a workload: pod in namespace "payments" with SA "payments-sa"
kubectl exec -n spire spire-server-0 -- \
  /opt/spire/bin/spire-server entry create \
  -spiffeID spiffe://example.org/payments/checkout \
  -parentID spiffe://example.org/ns/payments/sa/payments-sa \
  -selector k8s:ns:payments \
  -selector k8s:sa:payments-sa \
  -ttl 3600

# Register a VM workload (AWS instance attestation)
/opt/spire/bin/spire-server entry create \
  -spiffeID spiffe://example.org/infra/database \
  -parentID spiffe://example.org/agent/aws-iid/prod \
  -selector aws_iid:account_id:123456789 \
  -selector aws_iid:tag:role:database
```

**mTLS with SVID (Envoy + SDS):**

```yaml
# Envoy receives SVID from SPIRE Agent via SDS (Secret Discovery Service)
# No static TLS certificates needed — Envoy fetches and auto-rotates
static_resources:
  clusters:
    - name: upstream_payments
      connect_timeout: 0.25s
      transport_socket:
        name: envoy.transport_sockets.tls
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.transport_sockets.tls.v3.UpstreamTlsContext
          combined_validation_context:
            default_validation_context:
              match_subject_alt_names:
                - exact: "spiffe://example.org/payments/checkout"
          tls_certificate_sds_secret_configs:
            - name: "spiffe://example.org/infra/api"
              sds_config:
                api_config_source:
                  api_type: GRPC
                  grpc_services:
                    - envoy_grpc:
                        cluster_name: spire_agent
```

SVIDs rotate automatically every hour. Zero static secrets anywhere. The SPIRE Agent handles renewal, and Envoy picks up the new certificate via SDS without restart.

---

**Q: Design automated secret rotation for database credentials with zero-downtime application impact.**

The challenge: rotate a PostgreSQL password without dropping active connections or causing authentication failures during the rollover window.

**Strategy: Dual-Version Secret with Rolling Application Restart**

```
Phase 1: Generate new password, write BOTH old+new to secret store
Phase 2: Update database to accept both passwords (temporary dual-auth)
Phase 3: Rolling restart of application (picks up new password from secret store)
Phase 4: Verify all instances using new password
Phase 5: Remove old password from database and secret store
```

**AWS Secrets Manager Rotation Lambda:**

```python
import boto3, psycopg2, json, string, secrets

sm = boto3.client('secretsmanager')

def lambda_handler(event, context):
    arn = event['SecretId']
    token = event['ClientRequestToken']
    step = event['Step']

    if step == 'createSecret':
        create_secret(arn, token)
    elif step == 'setSecret':
        set_secret(arn, token)
    elif step == 'testSecret':
        test_secret(arn, token)
    elif step == 'finishSecret':
        finish_secret(arn, token)

def create_secret(arn, token):
    """Generate new password, store as AWSPENDING version."""
    try:
        sm.get_secret_value(SecretId=arn, VersionStage='AWSPENDING')
        return  # Already created
    except sm.exceptions.ResourceNotFoundException:
        pass

    current = json.loads(sm.get_secret_value(SecretId=arn)['SecretString'])
    new_password = ''.join(secrets.choice(string.ascii_letters + string.digits + '!@#$') for _ in range(32))
    new_secret = {**current, 'password': new_password}

    sm.put_secret_value(
        SecretId=arn,
        ClientRequestToken=token,
        SecretString=json.dumps(new_secret),
        VersionStages=['AWSPENDING'],
    )

def set_secret(arn, token):
    """Apply new password to database."""
    pending = json.loads(sm.get_secret_value(SecretId=arn, VersionStage='AWSPENDING')['SecretString'])
    current = json.loads(sm.get_secret_value(SecretId=arn, VersionStage='AWSCURRENT')['SecretString'])

    # Connect with current password, update to new
    conn = psycopg2.connect(host=current['host'], port=current['port'],
                            database=current['dbname'], user=current['username'],
                            password=current['password'])
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(f"ALTER USER {pending['username']} PASSWORD %s", (pending['password'],))
    conn.close()

def test_secret(arn, token):
    """Verify new password works."""
    pending = json.loads(sm.get_secret_value(SecretId=arn, VersionStage='AWSPENDING')['SecretString'])
    conn = psycopg2.connect(host=pending['host'], port=pending['port'],
                            database=pending['dbname'], user=pending['username'],
                            password=pending['password'])
    conn.close()  # Raises if authentication fails

def finish_secret(arn, token):
    """Promote AWSPENDING to AWSCURRENT."""
    metadata = sm.describe_secret(SecretId=arn)
    current_version = next(v for v, stages in metadata['VersionIdsToStages'].items()
                           if 'AWSCURRENT' in stages)
    if current_version == token:
        return  # Already rotated

    sm.update_secret_version_stage(
        SecretId=arn,
        VersionStage='AWSCURRENT',
        MoveToVersionId=token,
        RemoveFromVersionId=current_version,
    )
```

**Zero-Downtime Application Side:**

Applications must re-fetch the secret on connection failure (not cache credentials indefinitely):

```python
import boto3, json, time

_cache = {}

def get_db_password(secret_arn: str) -> str:
    """Fetch from cache; refresh if older than 55 minutes (secret rotates hourly)."""
    cached = _cache.get(secret_arn)
    if cached and (time.time() - cached['ts']) < 3300:  # 55 min TTL
        return cached['password']
    secret = json.loads(boto3.client('secretsmanager')
                        .get_secret_value(SecretId=secret_arn)['SecretString'])
    _cache[secret_arn] = {'password': secret['password'], 'ts': time.time()}
    return secret['password']

def get_connection(secret_arn: str):
    for attempt in range(2):  # Retry once on auth failure to handle mid-rotation
        try:
            return psycopg2.connect(..., password=get_db_password(secret_arn))
        except psycopg2.OperationalError:
            _cache.pop(secret_arn, None)  # Invalidate cache, retry with fresh secret
    raise
```

Configure rotation schedule:
```bash
aws secretsmanager rotate-secret \
  --secret-id arn:aws:secretsmanager:us-east-1:123456789:secret:prod/db/password \
  --rotation-lambda-arn arn:aws:lambda:us-east-1:123456789:function:rotate-db-password \
  --rotation-rules AutomaticallyAfterDays=30
```
