---
description: DevSecOps SAST, DAST, SCA, container image scanning, and shift-left security pipeline patterns for senior engineers.
---

# DevSecOps — SAST, DAST & Shift-Left Security

## The Shift-Left Model

"Shift-Left" means moving security checks earlier in the SDLC — from a quarterly pen test to every single pull request.

```
Traditional:
  Code → Build → Deploy → QA → PEN TEST (1x per quarter)
                                    ↑ expensive, too late

Shift-Left:
  Code → SAST  → Build → SCA  → Container Scan → Deploy → DAST
    ↑             ↑               ↑                         ↑
  IDE plugin    Pre-merge       CI pipeline            Post-deploy
  (instant)     gate            (mandatory)            (scheduled)
```

***

## SAST — Static Application Security Testing

SAST analyzes source code **without executing it**. It finds bugs like SQL injection patterns, hardcoded secrets, and insecure API usage.

### Semgrep (Language-agnostic, Fast)

```yaml
# .github/workflows/sast.yml
- name: Run Semgrep
  uses: returntocorp/semgrep-action@v1
  with:
    config: >-
      p/owasp-top-ten
      p/secrets
      p/python
  env:
    SEMGREP_APP_TOKEN: ${{ secrets.SEMGREP_TOKEN }}
```

**Custom Semgrep Rule:**
```yaml
# rules/no-hardcoded-aws-key.yml
rules:
  - id: hardcoded-aws-access-key
    pattern: |
      $X = "AKIA..."
    message: "Hardcoded AWS Access Key detected at $X"
    languages: [python, javascript, go]
    severity: ERROR
    metadata:
      owasp: A2:2021
```

### SonarQube (Enterprise Gate)

```yaml
# Quality Gate config — block PR if any of these fail
- name: SonarQube Scan
  uses: sonarqube-quality-gate-action@master
  with:
    scanMetadataReportFile: .scannerwork/report-task.txt
  env:
    SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
    SONAR_HOST_URL: https://sonar.company.com
# Fails if: coverage < 80%, new bugs > 0, new vulnerabilities > 0
```

***

## SCA — Software Composition Analysis

SCA scans your **dependencies** (npm packages, pip packages, Maven JARs) for known CVEs.

```yaml
# Snyk in CI — block on HIGH/CRITICAL
- name: Snyk dependency scan
  uses: snyk/actions/python@master
  env:
    SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
  with:
    args: --severity-threshold=high --fail-on=all

# SBOM generation — audit trail of all dependencies
- name: Generate SBOM
  uses: anchore/sbom-action@v0
  with:
    format: spdx-json
    output-file: sbom.spdx.json
```

**OWASP Dependency-Check (Self-hosted):**
```bash
dependency-check.sh \
  --project "my-app" \
  --scan ./src \
  --format HTML \
  --failOnCVSS 7         # Fail if any CVE score >= 7.0
```

***

## Container Image Scanning — Trivy

```yaml
# Trivy in CI — scan image before push
- name: Build image
  run: docker build -t my-app:${{ github.sha }} .

- name: Scan with Trivy
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: my-app:${{ github.sha }}
    format: sarif
    output: trivy-results.sarif
    severity: CRITICAL,HIGH
    exit-code: 1          # Block pipeline on findings

- name: Upload results to GitHub Security
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: trivy-results.sarif
```

**Scan IaC files too:**
```bash
trivy config ./terraform/    # Scan Terraform for misconfigs
trivy config ./k8s/          # Scan K8s manifests
trivy fs .                   # Scan entire repo
```

***

## DAST — Dynamic Application Security Testing

DAST attacks a **running application** to find runtime vulnerabilities (XSS, SQLi, auth bypass) that SAST can't detect.

### OWASP ZAP (Baseline Scan in CI)

```yaml
# Run ZAP against staging after deploy
- name: OWASP ZAP Baseline Scan
  uses: zaproxy/action-baseline@v0.9.0
  with:
    target: 'https://staging.myapp.com'
    rules_file_name: '.zap/rules.tsv'
    cmd_options: '-a -j'    # -a: include ajax, -j: JSON report
    fail_action: warn        # warn|report|error
```

**ZAP Rules File (`.zap/rules.tsv`):**
```
10015  IGNORE  (Cookie Without Secure Flag - expected for http only envs)
10038  IGNORE  (Content Security Policy)
```

***

## Secret Detection — Pre-commit & CI

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks   # Runs on every commit locally
```

```yaml
# CI — Gitleaks scan on every PR
- name: Detect secrets with Gitleaks
  uses: gitleaks/gitleaks-action@v2
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    GITLEAKS_LICENSE: ${{ secrets.GITLEAKS_LICENSE }}
```

***

## Complete DevSecOps Pipeline Pattern

```yaml
# Recommended gate order in CI:
stages:
  - secret-scan      # Fastest — stop at commit
  - sast             # Source code analysis
  - build
  - sca              # Dependency CVE check
  - container-scan   # Image CVE check
  - deploy-staging
  - dast             # Runtime attack simulation
  - promote-prod
```

***

## Logic & Trickiness Table

| Tool Category | Junior Approach | Senior Approach |
|:---|:---|:---|
| **SAST** | Run on full codebase every time | Run incremental scans on changed files only (fast) |
| **False positives** | Block all on any finding | Tune severity thresholds; suppress known FPs with inline annotations |
| **SBOM** | Skip it | Required for SLSA Level 2+; mandated by US EO 14028 |
| **DAST** | Run manually quarterly | Automated baseline in CI against staging on every deploy |
| **Secret scanning** | CI only | Pre-commit hook + CI + repository-level secret scanning (GitHub Advanced Security) |
| **CVE triage** | Fix everything immediately | Triage by CVSS + exploitability + reachability; prioritize Critical in prod |
