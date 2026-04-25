# DevSecOps Tips & Tricks

Production-tested security patterns, common misconfigurations, and gotchas.

***

## Secrets — The #1 Source of Incidents

### The most common secret leak patterns (and how to prevent them)
```bash
# Pattern 1: AWS credentials in ~/.aws/credentials on a developer laptop
# → uploaded to a public repo via a rogue script
# Prevention: use AWS SSO (no long-term credentials on disk)

# Pattern 2: .env file committed to git
echo ".env" >> .gitignore  # But .env was already committed before .gitignore was set
git rm --cached .env        # Remove from tracking without deleting locally

# Pattern 3: Secret in Docker build arg (visible in image history)
docker build --build-arg API_KEY=secret123 .
docker history my-image    # API_KEY is visible here!

# Prevention: use BuildKit secret mounts
docker build --secret id=api_key,src=api_key.txt \
  -f Dockerfile .
# In Dockerfile: RUN --mount=type=secret,id=api_key cat /run/secrets/api_key
```

### Scan commit history for secrets (not just current code)
```bash
# Gitleaks: scans entire git history
gitleaks detect --source . --verbose --report-format json --report-path findings.json

# truffleHog: deep history scan with entropy analysis
trufflehog git file://. --json --only-verified

# If a secret is found in history:
# 1. Rotate the secret IMMEDIATELY (assume it was already seen)
# 2. Remove from history with git-filter-repo (not git filter-branch)
pip install git-filter-repo
git filter-repo --invert-paths --path-glob '*.env' --force
# 3. Force-push and notify all collaborators to reclone
```

### GitHub secret scanning + push protection
```
Enable at: Organization Settings → Code security → Secret scanning
→ Push protection: blocks pushes containing known secret patterns BEFORE they land

Custom patterns: add your organization's API key format
  Pattern: MYAPP-[A-Z0-9]{32}
  Test strings: MYAPP-ABCDEFG12345678901234567890ABCD
```

***

## Container Security

### The CIS Docker Benchmark — most important checks
```bash
# Run the benchmark
docker run --rm -it \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /usr/lib/systemd:/usr/lib/systemd \
  -v /etc:/etc \
  docker/docker-bench-security

# Top findings to fix:
# 2.1: Enable content trust (DOCKER_CONTENT_TRUST=1)
# 4.1: Don't use privileged containers
# 4.5: Don't expose the Docker socket to containers
# 5.3: Restrict Linux capabilities with --cap-drop all
```

### Trivy — what the scan levels mean
```bash
# CRITICAL: Exploit is easy and impact is devastating. Fix immediately.
# HIGH: Exploit exists but requires non-trivial effort. Fix this sprint.
# MEDIUM: Limited exploitability or impact. Fix within 60 days.
# LOW: Unlikely to be exploitable. Track in backlog.

# Useful flags:
trivy image --severity CRITICAL,HIGH --exit-code 1 my-image:latest
# --exit-code 1: fail CI pipeline on HIGH+
# --ignore-unfixed: only flag vulns that have a patch available (reduces noise)
trivy image --ignore-unfixed --severity CRITICAL,HIGH my-image:latest
```

### Distroless images — debugging when you have no shell
```bash
# Standard debug (will fail on distroless)
docker exec -it container_id bash   # Error: no bash

# Option 1: use the debug variant
FROM gcr.io/distroless/base:debug   # Has busybox shell

# Option 2: ephemeral debug container in Kubernetes
kubectl debug -it my-pod \
  --image=busybox \
  --target=my-container \
  -- sh
# Shares PID/net namespace with the main container; has shell tools
```

***

## Vault — Common Gotchas

### Vault is sealed after restart — you need auto-unseal
```bash
# Check if Vault is sealed
vault status | grep Sealed

# Manual unseal (requires 3 of 5 keys by default — terrible for production)
vault operator unseal <key1>
vault operator unseal <key2>
vault operator unseal <key3>

# Production: use AWS KMS auto-unseal
# vault.hcl:
seal "awskms" {
  region     = "us-east-1"
  kms_key_id = "arn:aws:kms:us-east-1:123:key/abc"
}
# Vault unseals automatically on startup — no human needed
```

### Vault lease vs token TTL — two different things
```
Token TTL: how long the authentication token is valid
  - Login token: 8h (human) or 1h (automated)
  - Renewable: token can be extended before expiry

Lease TTL: how long dynamic credentials (DB, AWS) are valid
  - Short (1h): more secure, more Vault calls
  - Long (24h): fewer calls, wider blast radius if leaked
  - Vault agent renews leases automatically

Common mistake: setting a 24h token TTL for a service account
and a 1h lease TTL for DB credentials
→ Credentials expire every hour but the service doesn't re-auth
→ Solution: ensure token TTL >= credential TTL, or use Vault agent
```

### Test that your Vault auth works before deploying
```bash
# Test Kubernetes auth from inside a pod
export VAULT_ADDR=https://vault.internal:8200
export JWT=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
curl -s \
  --request POST \
  --data "{\"jwt\": \"$JWT\", \"role\": \"my-app\"}" \
  $VAULT_ADDR/v1/auth/kubernetes/login | jq .auth.client_token
# Should return a token — if empty, the role or policy is wrong
```

***

## Kubernetes Security Misconfigurations

### The 6 most common Kubernetes security mistakes

1. **Running as root:**
   ```yaml
   securityContext:
     runAsNonRoot: true
     runAsUser: 1000
   ```

2. **No resource limits (allows container breakout via OOM):**
   ```yaml
   resources:
     limits:
       memory: "256Mi"
       cpu: "500m"
   ```

3. **Privileged containers:**
   ```yaml
   securityContext:
     privileged: false        # NEVER true in production
     allowPrivilegeEscalation: false
   ```

4. **Writable root filesystem:**
   ```yaml
   securityContext:
     readOnlyRootFilesystem: true
   # Add tmpfs for writable temp if needed
   volumeMounts:
     - name: tmp
       mountPath: /tmp
   volumes:
     - name: tmp
       emptyDir: {}
   ```

5. **Automounting service account tokens on pods that don't need API access:**
   ```yaml
   automountServiceAccountToken: false
   ```

6. **No NetworkPolicy (all pods can talk to all pods):**
   ```yaml
   # Default deny-all ingress
   kind: NetworkPolicy
   spec:
     podSelector: {}
     policyTypes: [Ingress]
     # No ingress rules = deny all
   ```

### Detect security issues in existing clusters
```bash
# kubesec: score a Kubernetes YAML file
kubesec scan pod.yaml

# kube-bench: CIS Kubernetes Benchmark
kubectl apply -f https://raw.githubusercontent.com/aquasecurity/kube-bench/main/job.yaml
kubectl logs -l app=kube-bench

# popeye: cluster sanitizer (checks misconfigurations)
popeye --save --out html --output-file report.html

# kube-score: YAML linter for best practices
kube-score score deployment.yaml
```

***

## Supply Chain Security

### Verify image signatures in CI before deploying
```bash
# Verify an image is signed (keyless — Sigstore)
cosign verify \
  --certificate-identity "https://github.com/org/repo/.github/workflows/release.yml@refs/heads/main" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  myregistry.io/my-app:v1.2.3

# In Kubernetes: use Kyverno to enforce signature verification on admission
apiVersion: kyverno.io/v1
kind: ClusterPolicy
spec:
  rules:
    - name: verify-image-signature
      match:
        resources:
          kinds: [Pod]
      verifyImages:
        - imageReferences: ["myregistry.io/my-app:*"]
          attestors:
            - entries:
                - keyless:
                    subject: "https://github.com/org/repo/*"
                    issuer: "https://token.actions.githubusercontent.com"
```

### SBOM — quick check for a specific CVE in deployed software
```bash
# Generate SBOM from running image
syft myregistry.io/my-app:v1.2.3 -o spdx-json=sbom.json

# Check SBOM against a specific CVE
grype sbom:./sbom.json | grep CVE-2024-12345

# More powerful: upload to Dependency-Track (continuous monitoring)
# When a new CVE is published, DT alerts you for all affected projects
curl -X POST \
  -H "X-API-Key: $DT_TOKEN" \
  -F "bom=@sbom.json" \
  https://dependencytrack.company.com/api/v1/bom
```
