# DevSecOps — Deep Theory Notes

## Shift-Left Security Philosophy

Shift-left means moving security testing earlier in the software development lifecycle — from a final gate before release to an integrated practice at every commit, PR, and build. The core insight is that a vulnerability found in code review costs $1 to fix; the same vulnerability found in production costs $100+.

The shift-left model requires:
- Security checks running automatically in every CI pipeline (no human gates)
- Developers receiving immediate, actionable feedback (not a report weeks later)
- Security teams transitioning from auditors to platform engineers building security tooling

> [!IMPORTANT]
> Shift-left is not about removing security reviews — it is about making security continuous and automated so that reviews focus on architectural decisions, not routine checklist items.

---

## SAST / DAST / IAST / RASP

### SAST — Static Application Security Testing

SAST analyzes source code or compiled bytecode without executing the application. It is "white-box" testing — it has full visibility into the code.

- **When:** Every commit/PR, integrated into CI
- **Tools:** Semgrep (fast, rule-based, open source), SonarQube (full SAST + code quality), CodeQL (GitHub-native, semantic analysis), Checkmarx, Veracode
- **Finds:** SQL injection patterns, hardcoded secrets, path traversal, insecure deserialization, dangerous function calls
- **Limitation:** High false-positive rate; does not understand runtime behavior or business logic

```yaml
# Semgrep in CI (GitHub Actions)
- name: SAST scan with Semgrep
  uses: returntocorp/semgrep-action@v1
  with:
    config: >-
      p/owasp-top-ten
      p/secrets
      p/dockerfile
```

### DAST — Dynamic Application Security Testing

DAST tests the running application from outside, like an attacker would. It is "black-box" testing — no access to source code.

- **When:** Against deployed staging/review environments, not in the main build
- **Tools:** OWASP ZAP (open source, CI-friendly), Burp Suite Enterprise, Nuclei, Nikto
- **Finds:** XSS, CSRF, authentication flaws, open redirects, server misconfigurations, exposed APIs
- **Limitation:** Slower; misses logic bugs only visible in source; can trigger side effects in stateful apps

```bash
# OWASP ZAP API scan
docker run -t owasp/zap2docker-stable zap-api-scan.py \
  -t https://staging.example.com/openapi.json \
  -f openapi \
  -r zap-report.html \
  -x zap-report.xml
```

### IAST — Interactive Application Security Testing

IAST instruments the application at runtime — typically via an agent or library — and observes real code execution paths during functional testing. It combines the accuracy of SAST with the runtime context of DAST.

- **When:** During automated integration or QA tests against a running application
- **Tools:** Contrast Security, Seeker, Hdiv Detection
- **Advantage:** Very low false positive rate because it only flags vulnerabilities in code paths that were actually exercised
- **Limitation:** Requires agent installation; often commercial; adds overhead to test runtime

### RASP — Runtime Application Self-Protection

RASP embeds security logic inside the application process itself. Instead of sitting outside, it intercepts application calls at runtime and blocks malicious behavior in real time — even in production.

- **When:** Production (complementary to other controls, not a replacement)
- **Tools:** Sqreen, Hdiv, OpenRASP
- **Advantage:** Blocks zero-day exploitation of known vulnerability classes
- **Limitation:** Performance overhead; risk of false positives blocking legitimate traffic; adds deployment complexity

| Tool Type | Environment | Source Access | Runs In |
|-----------|-------------|---------------|---------|
| SAST | CI on every commit | Yes | Pipeline |
| DAST | Against running app | No | Pipeline / scheduled |
| IAST | During functional tests | No | QA / staging runtime |
| RASP | Production | No | Production runtime |

---

## SCA — Software Composition Analysis

SCA analyzes an application's dependencies (third-party libraries and transitive dependencies) to identify known vulnerabilities (CVEs) and license compliance issues.

Modern applications are 70-90% open-source code by volume. SCA is how you manage inherited risk in your dependency tree.

**SCA in the pipeline:**

```yaml
# Snyk SCA in GitHub Actions
- name: Run Snyk to check for vulnerabilities
  uses: snyk/actions/node@master
  env:
    SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
  with:
    args: --severity-threshold=high --all-projects
```

**Key SCA tools:**

| Tool | Strength | License |
|------|----------|---------|
| Trivy | Images + filesystem + IaC + SBOMs | Open source |
| Grype | Fast image + SBOM scanning | Open source |
| Snyk | Developer-friendly, PR comments, license check | Commercial + free tier |
| Dependency-Track | Continuous SBOM monitoring, dashboard | Open source (OWASP) |
| FOSSA | License compliance at enterprise scale | Commercial |

---

## Container Image Scanning

Container images bundle OS packages and application dependencies — both of which carry CVEs. Image scanning is mandatory before any image enters production.

### Trivy

Trivy is the most complete open-source scanner: OS packages, application dependencies (Go, Python, Java, Node, Ruby), IaC files, Kubernetes manifests, and SBOM generation.

```bash
# Scan image and fail on HIGH or CRITICAL CVEs
trivy image \
  --severity HIGH,CRITICAL \
  --exit-code 1 \
  --ignore-unfixed \
  myapp:v1.2.0

# Scan with JSON output for CI processing
trivy image --format json --output trivy-results.json myapp:v1.2.0

# Scan Kubernetes cluster for vulnerabilities
trivy k8s --report=all cluster

# Generate SBOM from image
trivy image --format cyclonedx --output sbom.cdx.json myapp:v1.2.0

# Use a .trivyignore file to acknowledge accepted risks
cat .trivyignore
# CVE-2023-12345  # Accepted risk: no fix available, not exploitable in our config
```

### Grype

Grype (Anchore) is optimized for speed and SBOM-first workflows:

```bash
# Scan image
grype myapp:v1.2.0

# Scan with SBOM as input (faster, repeatable)
syft myapp:v1.2.0 -o cyclonedx-json > sbom.json
grype sbom:./sbom.json

# Update vulnerability database
grype db update

# Only high/critical
grype myapp:v1.2.0 --fail-on high
```

### Clair

Clair (Quay) is an API-driven scanner used in container registry integrations. It is less common in new deployments but widely used in enterprise registry setups (Quay, Harbor). It uses a PostgreSQL database and scans layers via its REST API.

### In-Pipeline Pattern

```yaml
# Multi-stage: build → scan → sign → push
build-and-scan:
  steps:
    - docker build -t myapp:${{ github.sha }} .
    - trivy image --exit-code 1 --severity HIGH,CRITICAL myapp:${{ github.sha }}
    - syft myapp:${{ github.sha }} -o cyclonedx-json > sbom.json
    - cosign sign --key cosign.key myapp:${{ github.sha }}
    - docker push myapp:${{ github.sha }}
```

---

## SBOM — Software Bill of Materials

An SBOM is a machine-readable inventory of all components in a software artifact: OS packages, application libraries, transitive dependencies, with their versions and license identifiers.

SBOMs serve as the source of truth for:
1. **Vulnerability management:** When Log4Shell drops, you query all SBOMs to find affected services in minutes, not weeks
2. **License compliance:** Ensure no GPL-licensed code is embedded in commercial products
3. **Regulatory compliance:** Required by US Executive Order 14028, FDA for medical devices

### CycloneDX vs SPDX

| Dimension | CycloneDX | SPDX |
|-----------|-----------|------|
| Governance | OWASP | Linux Foundation |
| Primary focus | Security / vulnerability context | License compliance |
| Formats | JSON, XML | JSON, YAML, RDF, TV |
| Tooling | Syft, cdxgen, Trivy | SPDX-sbom-generator, FOSSID |
| VEX support | Yes (Vulnerability Exploitability eXchange) | Limited |
| Use in industry | OWASP Dependency-Track, Grype | SPDX spec widely adopted in legal teams |

**Generate SBOMs:**

```bash
# CycloneDX with Syft
syft myapp:v1.2.0 -o cyclonedx-json > sbom.cdx.json

# CycloneDX with cdxgen (multi-language)
cdxgen -t python -o sbom.json .

# Attach SBOM to OCI image (travels with the image)
cosign attach sbom --sbom sbom.cdx.json myapp:v1.2.0

# Retrieve SBOM from image
cosign download sbom myapp:v1.2.0
```

---

## SLSA Framework (Supply-chain Levels for Software Artifacts)

SLSA is a graduated security framework for hardening the software supply chain. Each level adds requirements that make it progressively harder for an attacker to tamper with the build process or artifacts.

### SLSA Levels

**Level 1 — Build scripted, provenance generated**
- Build is automated (no manual `make && upload` from dev laptops)
- Build generates provenance: metadata documenting what was built, from which source commit, by which builder
- Provenance is not authenticated — it could be self-attested and forged

**Level 2 — Hosted build platform, signed provenance**
- Build must run on a hosted CI service (GitHub Actions, GitLab CI, Google Cloud Build)
- Provenance is signed by the build platform itself — not by the build script
- Prevents individual attacker from fabricating provenance without compromising the CI platform

**Level 3 — Hardened builds, unforgeable provenance**
- Build environment is isolated and ephemeral — no persistent credentials
- Builds are hermetic: no network access during build (dependencies pre-fetched)
- The build service generates provenance, not the user-written pipeline script
- GitHub Actions with the SLSA GitHub Generator achieves this

**Level 4 — Two-person review + reproducible builds**
- All source changes require two-person review
- Builds are reproducible: the same inputs always produce bit-for-bit identical outputs
- Currently aspirational for most organizations; hermetic, deterministic builds are very hard at scale

### SLSA Provenance Attestation

```bash
# GitHub Actions SLSA Level 3 using the official SLSA generator
- uses: slsa-framework/slsa-github-generator/.github/workflows/generator_generic_slsa3.yml@v1.9.0
  with:
    base64-subjects: "${{ needs.build.outputs.hashes }}"

# Verify SLSA provenance with slsa-verifier
slsa-verifier verify-artifact myapp-v1.2.0.tar.gz \
  --provenance-path provenance.intoto.jsonl \
  --source-uri github.com/myorg/myapp \
  --source-tag v1.2.0
```

---

## Sigstore / Cosign for Image Signing

Sigstore is an open-source project providing a PKI-free approach to software signing using short-lived certificates tied to OIDC identities (GitHub, Google, Microsoft).

### How Cosign Works

1. Developer/CI pipeline authenticates via OIDC (e.g., GitHub Actions OIDC token)
2. Fulcio (Sigstore CA) issues a short-lived X.509 certificate tied to the OIDC identity (`workflow:myorg/myapp@refs/heads/main`)
3. Cosign signs the image digest using the ephemeral key
4. The signature + certificate are pushed to the OCI registry alongside the image
5. The signing event is recorded in Rekor (Sigstore's transparency log) — immutable, append-only

```bash
# Keyless signing (uses OIDC — no long-lived keys)
cosign sign myregistry.io/myapp:v1.2.0

# Verify a signed image
cosign verify \
  --certificate-identity "https://github.com/myorg/myapp/.github/workflows/build.yml@refs/heads/main" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  myregistry.io/myapp:v1.2.0

# Sign with an explicit key pair (enterprise key management)
cosign generate-key-pair --kms gcpkms://projects/my-project/locations/global/keyRings/cosign/cryptoKeys/cosign-key
cosign sign --key gcpkms://projects/... myregistry.io/myapp:v1.2.0

# Verify with a public key
cosign verify --key cosign.pub myregistry.io/myapp:v1.2.0
```

### Rekor — Transparency Log

Rekor is the append-only, cryptographically verifiable log of all signing events in the Sigstore ecosystem. Every signing event produces an entry in Rekor. Anyone can:
1. Verify an entry exists (the artifact was signed)
2. Detect if entries are retroactively removed (tampering evidence)

```bash
# Look up Rekor entry for a signed artifact
rekor-cli search --sha $(cosign triangulate myregistry.io/myapp:v1.2.0)

# Get specific Rekor entry
rekor-cli get --uuid <entry-uuid> --format json
```

---

## in-toto Attestations

in-toto is a framework for creating verifiable attestations about each step in a supply chain. Unlike Cosign (which attests "this image exists and was signed"), in-toto attestations can record arbitrary facts: "this image was built from commit X", "these tests passed", "this image was scanned and has no critical CVEs".

```json
// in-toto attestation (SLSA Provenance format)
{
  "_type": "https://in-toto.io/Statement/v0.1",
  "predicateType": "https://slsa.dev/provenance/v0.2",
  "subject": [{"name": "myapp:v1.2.0", "digest": {"sha256": "abc123..."}}],
  "predicate": {
    "builder": {"id": "https://github.com/actions/runner"},
    "buildType": "https://github.com/slsa-framework/slsa-github-generator",
    "invocation": {
      "configSource": {
        "uri": "git+https://github.com/myorg/myapp@refs/heads/main",
        "digest": {"sha1": "def456..."}
      }
    }
  }
}
```

---

## OPA (Open Policy Agent) and Gatekeeper

OPA is a general-purpose policy engine using the Rego language. It evaluates structured data against declarative policies, returning allow/deny decisions.

### Rego Language Fundamentals

```rego
package kubernetes.admission

# Deny pods running as root
deny[msg] {
  input.request.kind.kind == "Pod"
  container := input.request.object.spec.containers[_]
  container.securityContext.runAsNonRoot != true
  msg := sprintf("Container '%v' must set runAsNonRoot: true", [container.name])
}

# Deny images using the 'latest' tag
deny[msg] {
  input.request.kind.kind == "Pod"
  container := input.request.object.spec.containers[_]
  endswith(container.image, ":latest")
  msg := sprintf("Container '%v' uses 'latest' tag — pin to a specific digest", [container.name])
}

# Require specific labels on all Deployments
deny[msg] {
  input.request.kind.kind == "Deployment"
  required := {"team", "environment", "owner"}
  provided := {label | input.request.object.metadata.labels[label]}
  missing := required - provided
  count(missing) > 0
  msg := sprintf("Deployment missing required labels: %v", [missing])
}
```

### Gatekeeper ConstraintTemplate

```yaml
# Define the constraint type
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8srequiredlabels
spec:
  crd:
    spec:
      names:
        kind: K8sRequiredLabels
      validation:
        openAPIV3Schema:
          properties:
            labels:
              type: array
              items:
                type: string
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8srequiredlabels
        violation[{"msg": msg}] {
          provided := {label | input.review.object.metadata.labels[label]}
          required := {label | label := input.parameters.labels[_]}
          missing := required - provided
          count(missing) > 0
          msg := sprintf("Missing required labels: %v", [missing])
        }
---
# Instantiate the constraint
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sRequiredLabels
metadata:
  name: require-team-label
spec:
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Namespace"]
  parameters:
    labels: ["team", "environment"]
```

### conftest for CI-time Policy Testing

```bash
# Test Kubernetes manifests before apply
conftest test deployment.yaml --policy policy/

# Test Terraform plans
terraform plan -out tfplan.binary
terraform show -json tfplan.binary > tfplan.json
conftest test tfplan.json --policy policy/terraform/

# Test Dockerfile
conftest test Dockerfile --policy policy/docker/

# Test with specific namespace
conftest test deployment.yaml --policy policy/ --namespace kubernetes.admission
```

---

## Falco Runtime Security

Falco uses eBPF (or kernel module) to observe system calls at the kernel level and detect anomalous behavior based on declarative rules.

### Falco Architecture

```
Container Process → Syscall → eBPF Probe (kernel) → Falco Daemon (userspace) → Rule Engine → Alert
```

Falco attaches eBPF programs to `tracepoint/syscalls/*` events. The probe collects: PID, process name, container ID, Kubernetes pod/namespace metadata, syscall arguments, file paths, network addresses. This stream flows from kernel to Falco via a perf ring buffer.

### Falco Rule Syntax

```yaml
# rules/custom.yaml

# Detect shell execution in containers
- rule: Terminal shell in container
  desc: A shell was spawned in a container
  condition: >
    spawned_process
    and container
    and shell_procs
    and not container.image.repository in (allowed_shells)
  output: >
    Shell spawned in container (user=%user.name user_loginuid=%user.loginuid
    container_id=%container.id container_name=%container.name
    shell=%proc.name parent=%proc.pname cmdline=%proc.cmdline
    k8s_ns=%k8s.ns.name k8s_pod=%k8s.pod.name)
  priority: WARNING
  tags: [container, shell, mitre_execution]

# Detect privilege escalation
- rule: Sudo or su invocation in container
  desc: A process is attempting to escalate privileges via sudo or su
  condition: >
    spawned_process
    and container
    and (proc.name = "sudo" or proc.name = "su")
  output: >
    Privilege escalation attempt (user=%user.name proc=%proc.name
    container_id=%container.id k8s_pod=%k8s.pod.name)
  priority: CRITICAL

# Custom macro for sensitive file access
- macro: sensitive_files
  condition: >
    fd.name in (/etc/shadow, /etc/sudoers, /etc/passwd, /.aws/credentials)
    or (fd.directory in (/etc/ssl, /etc/pki) and fd.name endswith ".key")

- rule: Sensitive file access
  desc: Sensitive credential or key file opened
  condition: open_read and sensitive_files and not proc.name in (trusted_readers)
  output: "Sensitive file read (file=%fd.name user=%user.name container=%container.id)"
  priority: ERROR
```

### Falco Alert Pipeline

```bash
# Falcosidekick routes alerts to multiple destinations
helm install falco falcosecurity/falco \
  --set driver.kind=ebpf \
  --set falcosidekick.enabled=true \
  --set falcosidekick.config.slack.webhookurl=$SLACK_WEBHOOK \
  --set falcosidekick.config.pagerduty.routingKey=$PD_KEY \
  --set falcosidekick.config.elasticsearch.hostport=http://es:9200
```

---

## Secret Scanning

### Gitleaks

```bash
# Scan entire git history
gitleaks detect --source . --report-format json --report-path gitleaks-report.json

# Scan staged changes only (pre-commit hook)
gitleaks protect --staged

# CI pre-commit hook
gitleaks protect --source . --staged --no-git

# Custom rules
cat .gitleaks.toml
[[rules]]
description = "Custom API Token"
regex = '''mycompany_[a-z0-9]{32}'''
tags = ["key", "internal"]
```

### detect-secrets

```bash
# Initialize baseline (audit current state)
detect-secrets scan --baseline .secrets.baseline

# Pre-commit hook: detect new secrets vs baseline
detect-secrets-hook --baseline .secrets.baseline

# Audit baseline (mark known false positives)
detect-secrets audit .secrets.baseline
```

---

## mTLS and Zero-Trust in Kubernetes

Standard TLS authenticates the server to the client. mTLS (mutual TLS) adds client authentication — both parties present X.509 certificates and verify each other.

In Kubernetes zero-trust:
1. **Identity:** Every workload has a SPIFFE identity: `spiffe://cluster.local/ns/<namespace>/sa/<serviceaccount>`
2. **Certificate issuance:** SPIRE or the service mesh CA issues short-lived certificates (1-24 hours) tied to the workload identity
3. **Enforcement:** Istio, Linkerd, or Cilium enforce mTLS for all pod-to-pod communication; an unencrypted connection or a connection from an unknown identity is dropped

```yaml
# Istio PeerAuthentication: enforce mTLS in strict mode for a namespace
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: production
spec:
  mtls:
    mode: STRICT  # Reject all non-mTLS traffic

---
# Istio AuthorizationPolicy: service-to-service allow-list
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: payments-allow-checkout
  namespace: production
spec:
  selector:
    matchLabels:
      app: payments-service
  action: ALLOW
  rules:
    - from:
        - source:
            principals: ["cluster.local/ns/production/sa/checkout-service"]
      to:
        - operation:
            methods: ["POST"]
            paths: ["/api/v1/charge"]
```

---

## Kubernetes Security Controls

### Pod Security Admission (PSA)

PSA replaced Pod Security Policies (PodSecurityPolicy was deprecated in 1.21, removed in 1.25). PSA enforces three built-in security profiles at the namespace level.

```yaml
# Label namespace to enforce restricted profile
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/enforce-version: latest
    pod-security.kubernetes.io/warn: restricted
    pod-security.kubernetes.io/audit: restricted
```

| Profile | Restrictions |
|---------|-------------|
| `privileged` | Unrestricted (avoid in production) |
| `baseline` | Prevents known privilege escalations. No hostNetwork, hostPID, hostIPC |
| `restricted` | Hardened: non-root, read-only root filesystem, dropped capabilities, seccomp |

### RBAC

```yaml
# Minimal role for a CI/CD service account
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: production
  name: deployer
rules:
  - apiGroups: ["apps"]
    resources: ["deployments"]
    verbs: ["get", "list", "update", "patch"]
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["get", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: deployer-binding
  namespace: production
subjects:
  - kind: ServiceAccount
    name: ci-deployer
    namespace: ci-system
roleRef:
  kind: Role
  name: deployer
  apiGroup: rbac.authorization.k8s.io
```

### Kubernetes Audit Logs

Audit logs record every request to the Kubernetes API server with: who (user/service account), what (verb + resource), when, outcome, and source IP.

```yaml
# Audit policy: log sensitive operations
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
  # Log all secret access at metadata level (no secret values)
  - level: Metadata
    resources:
      - group: ""
        resources: ["secrets"]
  # Log pod exec/attach (interactive sessions)
  - level: Request
    verbs: ["create"]
    resources:
      - group: ""
        resources: ["pods/exec", "pods/attach", "pods/portforward"]
  # Log RBAC changes
  - level: RequestResponse
    resources:
      - group: "rbac.authorization.k8s.io"
        resources: ["roles", "rolebindings", "clusterroles", "clusterrolebindings"]
```

---

## Compliance Frameworks

### SOC 2

SOC 2 is an auditing framework for service organizations covering Security, Availability, Processing Integrity, Confidentiality, and Privacy. The Trust Services Criteria most relevant to DevSecOps:

- **CC6.6 (Logical Access):** RBAC, MFA, SSO, access reviews
- **CC7.2 (Anomaly Detection):** SIEM, Falco, audit logs
- **CC8.1 (Change Management):** CI/CD with peer review, immutable artifacts, rollback capability
- **A1.2 (Availability):** SLOs, chaos engineering, multi-region, runbooks

### PCI-DSS

Relevant for cardholder data environments:
- **Req 6.3:** Identify and protect vulnerabilities — SAST/DAST/SCA in every pipeline
- **Req 7:** Restrict access to system components — RBAC, least privilege
- **Req 8:** Identify users and authenticate access — No shared accounts, MFA
- **Req 10:** Log and monitor all access — Audit logs, SIEM, 90-day retention
- **Req 11.3:** Penetration testing annually

### CIS Benchmarks

CIS provides hardened configuration baselines for Kubernetes, Docker, Linux, and cloud platforms. `kube-bench` automates CIS Kubernetes benchmark checks:

```bash
kube-bench run --targets master,node,etcd,policies
```

Key Kubernetes CIS controls:
- Disable anonymous API access (`--anonymous-auth=false`)
- Enable audit logging on the API server
- Use RBAC authorization (`--authorization-mode=RBAC`)
- Restrict etcd access (client cert auth only)
- Disable the default ServiceAccount token auto-mounting
