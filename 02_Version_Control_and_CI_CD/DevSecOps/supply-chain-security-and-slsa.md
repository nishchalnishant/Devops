# Supply Chain Security & SLSA (7 YOE)

A Senior Engineer's job isn't just to "scan for vulnerabilities." It is to ensure that the code running in Production is **cryptographically verified** and follows the **SLSA (Supply Chain Levels for Software Artifacts)** framework.

---

## 1. The SLSA Framework (S-L-S-A)

SLSA is the security standard for the software supply chain. In a 7 YOE interview, you are expected to know how to achieve **SLSA Level 3**.

- **Level 1:** Documented build process (scripted build).
- **Level 2:** Build runs on a hosted service (e.g., GitHub Actions, Jenkins) rather than a developer's machine. The build generates a signed **Provenance** attestation.
- **Level 3:** The build environment is **Source-Verified** and **Hermetic** (it has no network access during the build, preventing a malicious package from reaching out to a C2 server).

---

## 2. Software Bill of Materials (SBOM)

You cannot secure what you cannot see. Every build must generate an SBOM—a machine-readable list of every library and dependency inside your Docker image.

- **Tools:** Use `Trivy` or `Syft` to generate SBOMs in **CycloneDX** or **SPDX** format.
- **Governance:** Use a tool like **Dependency-Track** to continuously monitor your SBOMs for newly discovered vulnerabilities (Day-0 vulnerabilities) even after the code has been deployed.

```bash
# Generating an SBOM with Syft
syft image-name:v1.0 -o cyclonedx-json > sbom.json
```

---

## 3. Cryptographic Signing (Sigstore & Cosign)

Simply pushing an image to a registry is insecure—what if an attacker compromises the registry and replaces your image with a malicious one?

### The Cosign Workflow
1. CI builds the image.
2. CI uses **Cosign** to sign the image digest using OIDC (OpenID Connect).
3. The signature is pushed to the registry alongside the image.
4. **The Gatekeeper:** A Kubernetes Admission Controller (like **Kyverno** or **Policy Reporter**) checks the signature before anyone can `kubectl run` the image. If the signature is missing or invalid, the deployment is blocked.

---

## 4. Shift-Left Security Scanners

| Stage | Tool | Mission |
|---|---|---|
| **Secret Scanning** | Gitleaks / TruffleHog | Fail the build if a developer accidentally commits a private key or API token. |
| **SAST** | SonarQube / Snyk Code | Analyze raw source code for logic errors (e.g., SQL Injection, unhandled exceptions). |
| **SCA** | Trivy / Snyk OpenSource | Analyze the SBOM for known CVEs in third-party libraries. |
| **IaC Scanning** | Checkov / tfsec | Fail the build if the Terraform code creates a public S3 bucket or unencrypted database. |

---

## 5. Defensive Build Architectures

### Hermetic Builds
A hermetic build ensures that identical source inputs always produce identical binary outputs (reproducible builds). 
- All dependencies are pre-fetched and stored in a local cache or private mirror (Artifactory/Nexus).
- If the build attempts to talk to the public internet (NPM, PyPI, Maven), it is blocked. This prevents "Dependency Substitution" attacks.

### Single-Purpose Runners
Use ephemeral, hardened runners for sensitive builds. 
- The runner that builds the frontend assets should not have the same IAM permissions as the runner that manages production infrastructure. 
- Use **Runner Groups** to segregate high-trust vs. low-trust automation.
