---
description: Medium-difficulty interview questions for DevSecOps — supply chain security, Vault, policy enforcement, and secure pipelines.
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
