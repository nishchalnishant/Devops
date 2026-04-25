# Supply Chain Security & SLSA

## The Software Supply Chain Problem

Modern software is built from dozens or hundreds of open-source dependencies. Each dependency is a potential attack vector:

**Real-World Supply Chain Attacks:**
- **SolarWinds (2020):** Build system compromised, malicious code injected into Orion updates → 18,000+ organizations affected
- **CodeCov (2021):** CI/CD script modified, credentials stolen from build environment
- **Log4Shell (2021):** Single dependency in deep transitive chain → global vulnerability
- **XZ Utils (2024):** Backdoor inserted into compression library used by SSH

**The Attack Surface:**
```
Developer Code → Dependencies → Build System → CI/CD Pipeline → Registry → Production
     │              │              │              │              │         │
     │              │              │              │              │         └─ Runtime attacks
     │              │              │              │              └─ Registry poisoning
     │              │              │              └─ Credential theft, malicious steps
     │              │              └─ Compromised build server, injected code
     │              └─ Typosquatting, vulnerable versions
     └─ Insider threats, compromised accounts
```

**Supply Chain Security Goals:**
1. **Integrity:** Ensure code hasn't been tampered with from commit to deployment
2. **Provenance:** Know exactly what built the software, when, and from which source
3. **Verification:** Cryptographically verify artifacts before deployment
4. **Transparency:** Public audit logs of all builds and attestations

SLSA (Supply-chain Levels for Software Artifacts) and Sigstore provide the frameworks and tools to achieve these goals.

***

## SLSA Framework — Technical Requirements

```
SLSA Level 0: No guarantees
SLSA Level 1: Scripted build (documented process, provenance generated but unsigned)
SLSA Level 2: Build service (hosted CI/CD, signed provenance, version controlled)
SLSA Level 3: Hardened build (ephemeral isolated build env, hermetic, no network)
SLSA Level 4: Two-person review + hermetic reproducible build (rarely achieved)
```

### Provenance — What it Contains

SLSA provenance is a signed DSSE (Dead Simple Signing Envelope) attestation:

```json
{
  "_type": "https://in-toto.io/Statement/v0.1",
  "subject": [{
    "name": "myregistry.io/myapp",
    "digest": {"sha256": "abc123..."}
  }],
  "predicateType": "https://slsa.dev/provenance/v0.2",
  "predicate": {
    "builder": {"id": "https://github.com/actions/runner"},
    "buildType": "https://github.com/slsa-framework/slsa-github-generator/container@v1",
    "invocation": {
      "configSource": {
        "uri": "git+https://github.com/myorg/myrepo@refs/heads/main",
        "digest": {"sha1": "def456..."},
        "entryPoint": ".github/workflows/build.yaml"
      },
      "parameters": {}
    },
    "materials": [{
      "uri": "git+https://github.com/myorg/myrepo",
      "digest": {"sha1": "def456..."}
    }]
  }
}
```

### SLSA Level 3 in GitHub Actions

```yaml
# .github/workflows/build.yaml
jobs:
  build:
    permissions:
      id-token: write    # OIDC token for Sigstore
      contents: read
      packages: write
    uses: slsa-framework/slsa-github-generator/.github/workflows/container_workflow.yml@v1.9.0
    with:
      image: ghcr.io/myorg/myapp
      digest: ${{ needs.build-image.outputs.digest }}
```

***

## Sigstore / Cosign — Technical Deep Dive

### Keyless signing (OIDC-based)

```
CI job                    Sigstore Fulcio (CA)        Rekor (transparency log)
    │                           │                           │
    ├── Request OIDC token       │                           │
    │   from GitHub/GitLab       │                           │
    │                           │                           │
    ├── Generate ephemeral       │                           │
    │   key pair                │                           │
    │                           │                           │
    ├── POST OIDC token ────────►│                           │
    │   + public key            │                           │
    │                   ├── Verify OIDC token              │
    │                   ├── Issue short-lived cert         │
    │                   │   (cert embeds OIDC claims       │
    │                   │    in SAN: workflow URL)         │
    │◄── Certificate ───┤                                  │
    │                           │                           │
    ├── Sign image digest with private key                  │
    ├── POST signature + cert ─────────────────────────────►│
    │                                              ├── Write to append-only log
    │◄── Rekor log entry (transparency proof) ─────┤
    │
    └── Push signature to registry (OCI artifact)
```

```bash
# Sign in CI (keyless, using OIDC)
cosign sign \
  --yes \
  --oidc-issuer https://token.actions.githubusercontent.com \
  myregistry.io/myapp@sha256:abc123

# Verify (checks Rekor, validates cert chain)
cosign verify \
  --certificate-identity-regexp "https://github.com/myorg/myrepo" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  myregistry.io/myapp:latest

# Verify and output signing metadata
cosign verify \
  --certificate-identity-regexp "https://github.com/myorg/myrepo" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  myregistry.io/myapp:latest | jq '.[0].optional'

# Attach SBOM as an attestation
cosign attest \
  --yes \
  --predicate sbom.spdx.json \
  --type spdxjson \
  myregistry.io/myapp@sha256:abc123

# Verify attestation
cosign verify-attestation \
  --type spdxjson \
  --certificate-identity-regexp "https://github.com/myorg/myrepo" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  myregistry.io/myapp:latest | jq '.payload | @base64d | fromjson'
```

***

## SBOM — Generation and Governance

### Syft vs Trivy SBOM generation

```bash
# Syft — more complete OS + language package detection
syft myregistry.io/myapp:latest -o spdx-json > sbom.spdx.json
syft myregistry.io/myapp:latest -o cyclonedx-json > sbom.cyclonedx.json
syft myregistry.io/myapp:latest -o table   # human-readable

# Trivy — integrated scanning + SBOM in one tool
trivy image --format spdx-json \
  --output sbom-trivy.spdx.json \
  myregistry.io/myapp:latest

# Generate SBOM from filesystem (for non-container artifacts)
syft dir:. -o cyclonedx-json > sbom.json

# Scan a SBOM for CVEs (decouple scanning from generation)
grype sbom:./sbom.spdx.json --fail-on critical
```

### SBOM formats

| Format | Standard Body | Machine Readable | Use Case |
|--------|--------------|-----------------|----------|
| SPDX | Linux Foundation | JSON, YAML, RDF | Government/compliance (CISA mandate) |
| CycloneDX | OWASP | JSON, XML | Security tooling (Dependency Track) |
| SWID | ISO/IEC 19770 | XML | Enterprise software asset management |

### Dependency Track — continuous SBOM monitoring

```bash
# Upload SBOM to Dependency Track via API
curl -X PUT \
  -H "X-Api-Key: $DT_API_KEY" \
  -H "Content-Type: multipart/form-data" \
  -F "projectName=myapp" \
  -F "projectVersion=v1.2.3" \
  -F "autoCreate=true" \
  -F "bom=@sbom.cyclonedx.json" \
  https://dependencytrack.company.com/api/v1/bom

# Dependency Track then:
# - Correlates packages against NVD, OSV, GitHub Advisory DB
# - Alerts on new CVEs matching packages in any submitted SBOM
# - Generates policy violations for license conflicts
```

***

## Shift-Left Security — Tool Chain Integration

### Secret scanning

```bash
# Gitleaks — scan git history
gitleaks detect --source . --log-level warn

# Scan a specific commit range (CI: only new commits in PR)
gitleaks detect --source . --log-opts "origin/main..HEAD"

# .gitleaks.toml — custom rules and allowlists
[allowlist]
  description = "global allowlists"
  commits = ["abc1234"]   # known false positive commit
  regexes = ['''test-password''']
  paths = ['''(.*)?_test\.go''']

[[rules]]
  id = "my-custom-secret"
  description = "Detect internal API keys"
  regex = '''MYCO-[A-Z0-9]{32}'''
  tags = ["api-key", "internal"]
```

### IaC scanning

```bash
# Checkov — Terraform, Helm, K8s manifests, Dockerfiles
checkov -d . --framework terraform --check CKV_AWS_18,CKV_AWS_19

# Output SARIF for GitHub Security tab integration
checkov -d . --output sarif --output-file checkov.sarif

# tfsec — fast Terraform static analysis
tfsec . --minimum-severity HIGH

# Trivy also scans IaC
trivy config ./terraform-dir --severity HIGH,CRITICAL
trivy config kubernetes-manifests/ --severity HIGH
```

### SAST integration in GitHub Actions

```yaml
- name: Run Semgrep SAST
  uses: returntocorp/semgrep-action@v1
  with:
    config: >-
      p/ci
      p/owasp-top-ten
      p/python
  env:
    SEMGREP_APP_TOKEN: ${{ secrets.SEMGREP_APP_TOKEN }}

- name: Upload SARIF results
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: semgrep.sarif
  if: always()  # upload even if semgrep fails (shows findings in Security tab)
```

***

## Hermetic Builds — Implementation

```dockerfile
# Stage 1: dependency fetch (can hit the internet)
FROM python:3.12-slim AS deps
WORKDIR /deps
COPY requirements.txt .
RUN pip download -r requirements.txt -d /deps/packages

# Stage 2: hermetic build (no internet access)
FROM python:3.12-slim AS build
WORKDIR /app
COPY --from=deps /deps/packages /deps/packages
COPY . .
# Install from pre-downloaded packages only
RUN pip install --no-index --find-links=/deps/packages -r requirements.txt
RUN python -m compileall .

# Stage 3: minimal runtime image
FROM gcr.io/distroless/python3:nonroot
COPY --from=build /app /app
COPY --from=build /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
USER nonroot
ENTRYPOINT ["/app/main.py"]
```

```yaml
# GitHub Actions: disable outbound network during build stage
- name: Build (hermetic)
  run: docker build --network=none -t myapp:${{ github.sha }} .
  # --network=none: container has no network interface during build
```

***

## Admission Control — Policy as Code

```yaml
# Kyverno ClusterPolicy — enforce signed images + trusted registry
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: verify-image-integrity
spec:
  validationFailureAction: Enforce
  background: false
  rules:
  - name: verify-signature
    match:
      any:
      - resources:
          kinds: [Pod]
          namespaces: ["production", "staging"]
    verifyImages:
    - image: "myregistry.io/*"
      mutateDigest: true        # replace tag with digest for immutability
      verifyDigest: true
      required: true
      attestors:
      - entries:
        - keyless:
            subject: "https://github.com/myorg/*/workflows/build.yaml@refs/heads/main"
            issuer: "https://token.actions.githubusercontent.com"
            rekor:
              url: https://rekor.sigstore.dev
      attestations:
      - predicateType: https://spdx.dev/Document   # require SBOM attestation
        conditions:
        - all:
          - key: "{{element.spdxVersion}}"
            operator: StartsWith
            value: "SPDX-"

  - name: restrict-registries
    match:
      any:
      - resources:
          kinds: [Pod]
    validate:
      message: "Images must come from myregistry.io"
      pattern:
        spec:
          containers:
          - image: "myregistry.io/*"
          initContainers:
          - image: "myregistry.io/*"
```

***

## Key Gotchas

| Gotcha | Detail |
|--------|--------|
| SLSA provenance is useless without verification | Generating provenance without a verification step at deploy time is security theater |
| Cosign `--yes` required in non-interactive CI | Without `--yes`, cosign prompts for confirmation and hangs |
| Fulcio certificate TTL is 10 minutes | The ephemeral cert used for keyless signing expires; verification uses Rekor log (permanent) not the cert |
| Rekor is append-only | Once a signature is logged, it can't be deleted — don't accidentally sign test/dev images with prod identity |
| `mutateDigest: true` in Kyverno | Without this, `image:latest` can be re-pointed to malicious content; digest pinning is essential |
| SBOM from source ≠ SBOM from image | Source-level tools miss OS packages installed by Dockerfile; always generate from the built image |
| Gitleaks pre-commit vs CI | Pre-commit can be bypassed with `--no-verify`; CI enforcement is mandatory |
| CycloneDX vs SPDX tooling support | Not all tools support both; check Dependency Track and your SIEM before choosing format |
