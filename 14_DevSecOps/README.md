# DevSecOps (Security in DevOps)

DevSecOps is the practice of integrating security into every stage of the software development lifecycle (SDLC). It shifts security from a "final gate" at the end to a continuous process that begins as soon as a developer writes the first line of code.

#### 1. Shift Left Security
The core principle of DevSecOps is **"Shift Left"**.
*   **Traditional:** Security testing happens just before release. If a bug is found, it's expensive to fix and delays the project.
*   **DevSecOps:** Security testing (scanning) happens in the IDE and during every Git commit. Finding a bug early costs 10x less than finding it in production.

#### 2. The Security Testing Pillars
1.  **SCA (Software Composition Analysis):** Scans your third-party libraries (npm, pip, maven) for known vulnerabilities. (e.g., Snyk, Trivy).
2.  **SAST (Static Application Security Testing):** Scans your source code for "bad coding patterns" (e.g., hardcoded passwords, SQL injection). (e.g., SonarQube, Semgrep).
3.  **DAST (Dynamic Application Security Testing):** Attacks your *running* application from the outside to find vulnerabilities like Cross-Site Scripting (XSS). (e.g., OWASP ZAP).
4.  **Secret Scanning:** Scans your Git history for leaked API keys, passwords, or certificates. (e.g., Gitleaks, TruffleHog).

#### 3. Container & Infrastructure Security
*   **Image Scanning:** Every Docker image must be scanned for OS-level vulnerabilities before being pushed to a registry.
*   **IaC Scanning:** Tools like `Checkov` or `Tfsec` scan your Terraform/CloudFormation code for misconfigurations (e.g., an S3 bucket that is open to the public).

#### 4. Compliance as Code
In regulated industries (Banking, Healthcare), you must prove your systems are compliant (SOC2, HIPAA). DevSecOps uses automated audits to ensure that every change meets security standards before it is deployed.

***

#### 🔹 1. Improved Notes: Advanced DevSecOps
*   **SLSA (Supply-chain Levels for Software Artifacts):** A security framework to prevent tampering and improve the integrity of the software supply chain.
*   **SBOM (Software Bill of Materials):** An exhaustive list of every library and component in your software. Think of it as a "nutrition label" for your code.
*   **Zero Trust Architecture:** The mindset that "the network is always compromised." Every service must verify the identity of any other service before talking to it (using mTLS).

#### 🔹 2. Interview View (Q&A)
*   **Q:** What is the difference between SAST and DAST?
*   **A:** SAST is "White Box" testing (scans the code without running it). DAST is "Black Box" testing (attacks the running app without knowing how the code works).
*   **Q:** How do you handle secrets in a CI/CD pipeline?
*   **A:** Never use environment variables or hardcoded strings. Use a specialized **Vault** (like HashiCorp Vault or AWS Secrets Manager) and inject secrets dynamically at runtime.

***

#### 🔹 3. Architecture & Design: The Secure CI/CD Pipeline
1.  **Pre-commit:** Linting and Secret Scanning.
2.  **Build:** SAST and SCA scanning.
3.  **Registry:** Image signing and vulnerability scanning.
4.  **Deploy:** Admission controllers in K8s verify the image signature.
5.  **Monitor:** Runtime security (e.g., Falco) detects suspicious behavior in production.

***

#### 🔹 4. Commands & Configs (Security Tools)
```bash
# Scan a Docker image for vulnerabilities
trivy image nginx:latest

# Scan a Terraform directory for misconfigurations
checkov -d .

# Search for secrets in a Git repository
gitleaks detect --source . -v
```

***

#### 🔹 5. Troubleshooting & Debugging
*   **Scenario:** A developer says the "Security Scan is blocking the build" but it's a False Positive.
*   **Fix:** Use a `.snyk` or `.trivyignore` file to explicitly ignore a specific CVE, but always document *why* it's safe to ignore (e.g., "This library is only used for dev-testing, not in the final binary").

***

#### 🔹 6. Production Best Practices
*   **Immutable Infrastructure:** Never "patch" a server in production. Rebuild it from a fresh, scanned image.
*   **Principle of Least Privilege:** Every container and service should have the minimum permissions needed to function.
*   **Audit Everything:** Log every access attempt and every configuration change.

***

#### 🔹 Cheat Sheet / Quick Revision
| **Concept** | **Purpose** | **DevOps Context** |
| :--- | :--- | :--- |
| `CVE` | Vulnerability ID | Common Vulnerabilities and Exposures (e.g., Log4j). |
| `CVSS` | Severity Score | A 0-10 scale. Usually, Critical (9+) blocks the build. |
| `Vault` | Secret storage | Storing DB passwords and SSL keys securely. |
| `mTLS` | Auth between services | Ensuring Service A and Service B trust each other. |

***

This is Section 14: DevSecOps. For a senior role, you should focus on **Software Supply Chain Security**, **Sigstore / Cosign**, and **Runtime Security Monitoring**.
