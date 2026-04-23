# DevSecOps — Interview Questions

All difficulty levels combined.

---

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

---

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

---

## Hard

**14. How would you design a CI/CD pipeline that builds an SBOM and uses it for ongoing vulnerability management?**

1. **Generation:** After installing dependencies and building the image, run a Software Composition Analysis tool (Syft, CycloneDX) to produce a machine-readable SBOM in CycloneDX or SPDX format covering both application dependencies and OS packages.
2. **Storage:** Publish the SBOM as a versioned artifact attached to the image in the OCI registry (using Cosign's `attach sbom` command) so it travels with the image through promotion.
3. **Continuous monitoring:** Push the SBOM to Dependency-Track. Dependency-Track continuously correlates all components against NVD, OSV, and GitHub Advisory databases — when a new CVE is published affecting a component in a deployed SBOM, it automatically creates a Jira ticket for the owning team.
4. **Pipeline gate:** At deploy time, query Dependency-Track's API for critical findings on the SBOM. If unmitigated critical vulnerabilities exist, block promotion to production.

**15. Explain the secure software supply chain and three controls to implement in a CI/CD pipeline.**

1. **Source integrity:** Enforce signed commits via GPG or SSH signing. Configure GitHub/GitLab branch protection to require signed commits so the author of every change is cryptographically verified.
2. **Build integrity:** Run builds in hermetic, ephemeral environments (fresh containers per build with no persistent state). After the build, sign the resulting image with Cosign/Sigstore — the signature attests the image was built from a specific commit by the official build system.
3. **Deployment integrity:** Configure an admission controller (Kyverno or OPA Gatekeeper) in Kubernetes enforcing "only images signed by our trusted build system are allowed to run." This prevents rogue or tampered images from reaching production even if someone has `kubectl` access.

**16. What are the SLSA framework levels and what does Level 3 require?**

SLSA (Supply-chain Levels for Software Artifacts) is a graduated security framework:

- **Level 1:** Build is scripted/automated and generates provenance (metadata: source repo, commit hash, builder ID).
- **Level 2:** Build uses a hosted, version-controlled build service; provenance is authenticated by the build platform.
- **Level 3:** Build is isolated — no persistent credentials, no network access during build, hermetic environment. Provenance is generated by the platform itself (not the build script) and is unforgeable. GitHub Actions with SLSA Generator achieves this.
- **Level 4:** Two-person review for all changes, hermetic and reproducible builds.

**17. What CI/CD practices are required for PCI DSS compliance?**

1. **Segregation of duties:** Developers commit and view build logs; only authorized Release Managers can approve or trigger deployments to the Cardholder Data Environment. Enforced via RBAC in the CI system and protected environments.
2. **Immutable artifacts:** Every artifact is versioned and stored in a secure artifact repository. Direct changes to production servers are prohibited — every change must produce a new auditable artifact via the pipeline.
3. **Audit trail:** Every CI/CD action is logged — who triggered, what commit, who approved, success/failure. Logs are shipped to a centralized, tamper-proof SIEM and retained per compliance requirements.
4. **Secret management:** All secrets stored in a dedicated vault with strict access policies and full audit logging. No plaintext secrets in pipeline YAML or environment variables.
5. **Vulnerability scanning:** Every build includes SAST, SCA (dependency scanning), and container scanning. Critical findings block deployment.

**18. What is OPA Gatekeeper and how do you use it to enforce policies across the pipeline and the cluster?**

OPA Gatekeeper is a Kubernetes admission controller that enforces policies written in Rego. It operates at two points:

1. **CI time (shift left):** Use `conftest` CLI to test Kubernetes manifests against the same Rego policies before applying them. A manifest attempting to run a container as root fails the CI pipeline before any `kubectl apply`.
2. **Admission time:** Gatekeeper intercepts every API server request. If a Helm release or `kubectl apply` produces a resource violating a policy (no `securityContext`, missing required labels, privileged container), Gatekeeper rejects the request with a clear violation message.

Example Rego policy — all S3 buckets must have encryption:
```rego
deny[msg] {
  input.resource_changes[_].type == "aws_s3_bucket"
  not input.resource_changes[_].change.after.server_side_encryption_configuration
  msg := "S3 buckets must have server-side encryption enabled"
}
```
Run via `conftest test --policy policy.rego plan.json` after `terraform plan -out=plan.tfplan && terraform show -json plan.tfplan > plan.json`.

**19. How do you eliminate long-lived static credentials from a CI/CD pipeline using OIDC?**

1. **Configure OIDC provider:** Register GitHub Actions (or GitLab CI) as an OIDC identity provider in AWS IAM, Azure AD, or GCP.
2. **Create a trust relationship:** In AWS, create an IAM Role with a trust policy scoped to the OIDC provider with conditions matching the specific repository and branch (`token.actions.githubusercontent.com:sub == "repo:org/service:ref:refs/heads/main"`).
3. **CI job flow:** The CI job requests a signed JWT from the platform's OIDC endpoint. The job calls `sts:AssumeRoleWithWebIdentity` (AWS) or `az login --federated-token` (Azure), presenting the JWT. The cloud provider validates it and returns temporary credentials that expire after the job. No access keys, no rotation, no leakage risk.

**20. How does Falco use eBPF for runtime threat detection?**

1. **eBPF probe:** Falco loads a sandboxed eBPF program into the Linux kernel — it cannot crash the kernel and is verified by the kernel's eBPF verifier before loading.
2. **Syscall hooking:** The eBPF program attaches to system call entry points (`openat`, `execve`, `connect`, `clone`). Every process syscall triggers the probe.
3. **Data streaming:** The probe collects event data (process name, PID, arguments, file paths, network addresses) and passes it from kernel space to Falco's user-space daemon via a perf ring buffer.
4. **Rule evaluation:** Falco evaluates the event stream against its rule set. Example rule: "alert if a container writes to `/etc/passwd`" or "alert if a process spawns a shell inside a container." Violations trigger alerts to Slack, Falco Sidekick, or a SIEM.

**21. Design an auditable break-glass procedure for emergency access to a production Kubernetes cluster.**

1. **Access broker:** Teleport or a similar tool acting as the access gateway, integrating with an identity provider (Okta, Entra ID).
2. **Request workflow:** Engineer submits a request via Slack bot or Jira with a mandatory reason, expected duration, and scope (namespace or cluster-wide).
3. **Approval gate:** Request requires approval from at least one authorized on-call manager or security team member.
4. **JIT credentials:** Upon approval, the system issues a short-lived kubeconfig (15-60 minute TTL) — no permanent credentials. The role granted is the minimum required (e.g., read-only plus targeted exec on the specific deployment).
5. **Session recording:** Teleport records the entire terminal session. All `kubectl` commands are logged and shipped to an immutable audit log in S3 with object lock.
6. **Automatic revocation:** Credentials expire automatically. Post-incident review compares session recording against the stated reason and flags any out-of-scope actions.
