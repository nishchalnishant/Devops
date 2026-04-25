---
description: Easy interview questions for DevSecOps, security scanning, and application security fundamentals.
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
