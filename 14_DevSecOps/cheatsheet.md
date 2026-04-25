# DevSecOps Cheatsheet

Quick reference for security scanning, secret management, SBOM, and supply chain commands.

***

## Secret Detection

```bash
# Gitleaks — detect secrets in repo history
gitleaks detect --source . --verbose                     # Scan working directory
gitleaks detect --source . --log-opts="HEAD~50..HEAD"   # Last 50 commits
gitleaks detect --source . -r report.json --exit-code 0 # JSON report
gitleaks protect --staged                                 # Scan staged files (pre-commit)

# truffleHog — deep history scan
trufflehog git file://. --json                           # Scan local repo
trufflehog github --repo https://github.com/org/repo    # Scan remote
trufflehog s3 --bucket my-bucket                        # Scan S3 bucket

# detect-secrets (Yelp)
detect-secrets scan > .secrets.baseline                  # Create baseline
detect-secrets audit .secrets.baseline                   # Audit interactively
detect-secrets scan --update .secrets.baseline            # Update baseline
```

***

## SAST — Static Analysis

```bash
# Semgrep
semgrep --config=p/owasp-top-ten .                      # OWASP rules
semgrep --config=p/secrets .                             # Secret rules
semgrep --config=p/python .                              # Language rules
semgrep --config=auto .                                  # Auto-select rules
semgrep --json --output=results.json .                   # JSON output for CI
semgrep --severity=ERROR .                               # Only errors

# Bandit (Python)
bandit -r src/                                           # Scan Python code
bandit -r src/ -f json -o bandit.json                   # JSON output
bandit -r src/ -ll                                       # Only high severity
bandit -r src/ --skip B101,B105                         # Skip test rules

# Gosec (Go)
gosec ./...
gosec -fmt json -out gosec.json ./...
gosec -severity high ./...

# NodeJsScan (Node.js)
nodejsscan -d ./src -o report.json
```

***

## SCA — Dependency Scanning

```bash
# Snyk
snyk auth                                                # Authenticate
snyk test                                                # Scan dependencies
snyk test --severity-threshold=high                      # High+ only
snyk test --json > snyk-results.json                    # JSON output
snyk monitor                                             # Monitor in Snyk UI
snyk container test my-image:latest                      # Scan container image
snyk iac test ./terraform/                               # Scan IaC

# OWASP Dependency-Check
dependency-check --project "my-app" --scan ./          # Basic scan
dependency-check --project "my-app" --scan ./ \
  --format HTML --format JSON \
  --failOnCVSS 7                                         # Fail on CVE score 7+

# pip-audit (Python)
pip-audit                                               # Scan venv
pip-audit -r requirements.txt                           # Scan requirements file
pip-audit --format json --output audit.json             # JSON output

# npm audit (Node.js)
npm audit                                               # Basic scan
npm audit --audit-level=high                            # Only high+
npm audit --json > audit.json                           # JSON output
npm audit fix                                           # Auto-fix
npm audit fix --force                                   # Force fix (may break)

# govulncheck (Go)
govulncheck ./...                                       # Scan Go modules
govulncheck -json ./...                                 # JSON output
```

***

## Container Image Scanning — Trivy

```bash
# Image scanning
trivy image nginx:latest                                 # Scan from registry
trivy image --severity CRITICAL,HIGH nginx:latest       # Filter severity
trivy image --exit-code 1 --severity CRITICAL my-app:latest  # Fail on Critical
trivy image --format json --output results.json my-app  # JSON output
trivy image --format sarif --output results.sarif my-app # SARIF (GitHub upload)
trivy image --ignore-unfixed nginx:latest               # Only patched vulns

# Filesystem scanning
trivy fs .                                              # Scan current directory
trivy fs --security-checks vuln,secret,config .        # All check types

# IaC scanning
trivy config ./terraform/                               # Terraform misconfigs
trivy config ./k8s/                                     # Kubernetes manifests
trivy config --exit-code 1 --severity HIGH ./           # Fail on HIGH

# SBOM generation
trivy image --format spdx-json --output sbom.json my-app
trivy image --format cyclonedx --output sbom.xml my-app

# Repository scanning
trivy repo https://github.com/org/repo
```

***

## DAST — Dynamic Testing

```bash
# OWASP ZAP
# Baseline scan (passive only — safe for prod)
docker run -t owasp/zap2docker-stable zap-baseline.py \
  -t https://myapp.com \
  -r zap-report.html

# Full active scan (only against staging!)
docker run -t owasp/zap2docker-stable zap-full-scan.py \
  -t https://staging.myapp.com \
  -r zap-report.html \
  -J zap-report.json

# API scan (OpenAPI spec)
docker run -t owasp/zap2docker-stable zap-api-scan.py \
  -t https://staging.myapp.com/openapi.json \
  -f openapi \
  -r api-scan.html

# nikto (web server scanner)
nikto -h https://staging.myapp.com
nikto -h https://staging.myapp.com -Format json -output nikto.json
```

***

## HashiCorp Vault

```bash
# Start dev server (testing only)
vault server -dev &
export VAULT_ADDR='http://127.0.0.1:8200'
export VAULT_TOKEN='root'

# Authentication
vault login                                              # Interactive (token)
vault login -method=ldap username=alice                  # LDAP
vault login -method=aws                                  # AWS IAM auth
vault token lookup                                       # Inspect current token
vault token renew                                        # Renew token

# KV Secrets Engine
vault kv put secret/myapp db_url="postgres://..."       # Write secret
vault kv get secret/myapp                               # Read secret
vault kv get -field=db_url secret/myapp                 # Read single field
vault kv get -format=json secret/myapp                  # JSON output
vault kv list secret/                                   # List secrets
vault kv delete secret/myapp                            # Soft delete (latest)
vault kv destroy -versions=1,2 secret/myapp             # Hard delete versions
vault kv metadata get secret/myapp                      # Show all versions
vault kv rollback -version=1 secret/myapp               # Restore version

# Dynamic Secrets
vault read database/creds/my-role                       # Get dynamic DB creds
vault read aws/creds/my-role                            # Get dynamic AWS creds
vault lease renew <lease-id>                            # Renew a lease
vault lease revoke <lease-id>                           # Revoke credentials now
vault lease revoke -prefix database/creds/              # Revoke all DB creds

# PKI
vault write pki/issue/web-servers \
  common_name="api.internal.company.com" \
  ttl="24h"

# Audit
vault audit list
vault audit enable file file_path=/var/log/vault/audit.log

# Operator
vault status                                            # Cluster status
vault operator seal                                     # Seal the vault
vault operator unseal <unseal-key>                     # Unseal
vault operator key-status                               # Encryption key info
vault operator rotate                                   # Rotate encryption key

# Policies
vault policy list
vault policy read default
vault policy write my-policy policy.hcl
vault policy delete my-policy
```

***

## Image Signing — Cosign (Sigstore)

```bash
# Generate key pair
cosign generate-key-pair

# Sign an image (with key)
cosign sign --key cosign.key myregistry.io/my-app:v1.0

# Sign with OIDC (keyless — GitHub Actions)
cosign sign myregistry.io/my-app:v1.0

# Verify signature
cosign verify --key cosign.pub myregistry.io/my-app:v1.0
cosign verify --certificate-identity "https://github.com/org/repo/.github/workflows/release.yml@refs/heads/main" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  myregistry.io/my-app:v1.0

# Attach SBOM
cosign attach sbom --sbom sbom.spdx.json myregistry.io/my-app:v1.0
cosign download sbom myregistry.io/my-app:v1.0

# Attest (attach arbitrary metadata)
cosign attest --key cosign.key --type spdx --predicate sbom.spdx.json myregistry.io/my-app:v1.0
```

***

## SBOM Generation

```bash
# Syft — generate SBOM from image or directory
syft myregistry.io/my-app:latest -o spdx-json=sbom.spdx.json
syft myregistry.io/my-app:latest -o cyclonedx-xml=sbom.xml
syft dir:./src -o spdx-json=sbom.spdx.json

# Grype — vulnerability scan from SBOM
grype myregistry.io/my-app:latest                       # Scan image
grype sbom:./sbom.spdx.json                             # Scan from SBOM
grype myregistry.io/my-app --fail-on high               # Fail on HIGH
grype myregistry.io/my-app -o json > grype-results.json

# Verify SBOM
syft convert sbom.spdx.json -o table                    # Human-readable table
```

***

## SSL/TLS Certificate Management

```bash
# openssl — inspect certificates
openssl s_client -connect mysite.com:443 -servername mysite.com  # Check live cert
openssl x509 -in cert.pem -text -noout                           # Inspect cert file
openssl x509 -in cert.pem -enddate -noout                        # Show expiry
openssl verify -CAfile ca.pem cert.pem                           # Verify chain

# Check cert expiry on live host
echo | openssl s_client -connect mysite.com:443 2>/dev/null | \
  openssl x509 -noout -enddate

# Generate self-signed cert (testing)
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem \
  -days 365 -nodes -subj '/CN=localhost'

# cert-manager (K8s)
kubectl get certificates -A
kubectl get certificaterequests -A
kubectl describe certificate my-cert -n production
kubectl get secret my-cert-tls -n production -o jsonpath='{.data.tls\.crt}' | \
  base64 -d | openssl x509 -noout -enddate
```

***

## Network Security Scanning

```bash
# nmap — port scanning
nmap -sV -p 1-1000 target.com                           # Service detection
nmap -sV --script=vuln target.com                        # Vulnerability scripts
nmap -p 22,80,443,8080 10.0.0.0/24                      # Scan subnet
nmap -sn 10.0.0.0/24                                    # Host discovery only

# OWASP Amass — attack surface mapping
amass enum -d company.com                               # Enumerate subdomains
amass intel -d company.com -whois                        # WHOIS intel

# sslyze — SSL/TLS auditing
sslyze mysite.com                                       # Full TLS audit
sslyze mysite.com --json_out=results.json               # JSON output
```

***

## Pre-commit Security Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks

  - repo: https://github.com/Lucas-C/pre-commit-hooks-safety
    rev: v1.3.1
    hooks:
      - id: python-safety-dependencies-check

  - repo: https://github.com/pycqa/bandit
    rev: 1.7.6
    hooks:
      - id: bandit
        args: ["-ll"]

  - repo: https://github.com/antonbabenko/pre-commit-terraform
    rev: v1.86.0
    hooks:
      - id: terraform_tflint
      - id: terraform_trivy
```

```bash
# pre-commit usage
pre-commit install                                      # Install hooks
pre-commit run --all-files                              # Run all hooks
pre-commit run gitleaks                                 # Run specific hook
pre-commit autoupdate                                   # Update hook versions
```
