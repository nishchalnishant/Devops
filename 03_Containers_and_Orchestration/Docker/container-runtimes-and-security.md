# Container Runtimes & Supply Chain Security (7 YOE)

Mid-level engineers write Dockerfiles. Senior and Staff engineers ensure that the resulting images are cryptographically secure, minimal, and run in highly isolated sandboxes. 

---

## 1. Beyond Docker: The Container Runtime Architecture

Docker is a monolithic tool. In modern Kubernetes (versions 1.24+), the `dockershim` was removed. Kubernetes no longer uses Docker. It uses the Container Runtime Interface (CRI) to talk to modern, lightweight runtimes.

### The Stack Explained
- **OCI (Open Container Initiative):** The standard governing image formats and how containers run.
- **`runc`:** The low-level runtime. It actually creates the Linux namespaces and cgroups. (Docker, containerd, and CRI-O all use `runc` under the hood).
- **`containerd` / `CRI-O`:** The high-level runtimes. They manage image pulling from registries, networking (via CNI), and instructing `runc` to start the process. Kubernetes talks directly to these via the CRI API.

### Secure Sandboxing (gVisor & Kata Containers)
Standard containers (runc) share the host kernel. A vulnerability in the Linux kernel can allow container escape (e.g., CVE-2022-0185). In multi-tenant environments (SaaS platforms), this is an unacceptable risk.

- **gVisor (Google):** Runs containers in a user-space kernel (written in Go) that intercepts and filters syscalls before they reach the host OS. This severely restricts the attack surface.
- **Kata Containers:** Wraps each container in a highly optimized, lightweight hardware Virtual Machine (VM). It provides VM-level isolation with container-level speed.

**Deployment Pattern:** Use a `RuntimeClass` in Kubernetes to run untrusted/tenant workloads in `kata` while internal trusted workloads run in standard `runc`.

---

## 2. Minimal Attack Surface: Distroless & Scratch Architecture

The number of CVEs in an image is directly proportional to the number of OS packages installed.

### The Problem with Alpine
`alpine` is small but relies on `musl` libc instead of standard `glibc`. This causes obscure runtime bugs in C-bound languages (Python, Node) and performance regressions in JVM/Go networking.

### The 7 YOE Solution: Distroless & Scratch
Distroless images (maintained by Google/Chainguard) contain *only* your application and its runtime dependencies. They do not contain package managers, shells (`/bin/sh`), or any other OS utilities.

- **Security Benefit:** If an attacker achieves Remote Code Execution (RCE) in a distroless container, they cannot run commands, download malware (`curl/wget`), or pivot to other systems.
- **Scratch (Go/Rust):** Statically compiled binaries (like Go) do not even need a runtime environment. You can build `FROM scratch` to create an image containing literally nothing but your single binary.

---

## 3. Supply Chain Cryptography (SLSA Framework)

The Software Supply Chain is the #1 vector for modern cyber-attacks (e.g., SolarWinds, Log4j). You must prove mathematically that the image running in Prod is exactly the image approved in CI.

### Generating Software Bill of Materials (SBOMs)
An SBOM is an exhaustive list (in formats like SPDX or CycloneDX) of every dependency, library, and package buried inside your Docker image.
```bash
# Using Trivy to generate a CycloneDX SBOM
trivy image --format cyclonedx --output sbom.json myapp:v1.2
```

### Image Signing with Sigstore (Cosign)
Previously, signing images required complex KMS key management. **Sigstore/Cosign** uses OpenID Connect (OIDC) to issue short-lived certificates linked to your CI/CD pipeline identity (e.g., GitHub Actions).

**The Workflow:**
1. CI pipeline builds the Docker image.
2. CI pipeline logs into Cosign using its OIDC token.
3. Cosign signs the image digest and pushes the signature to the registry (ACR/ECR) alongside the image.
4. Kubernetes Admission Controller (Kyverno) intercepts the Pod creation request. It verifies the cryptographic signature before allowing the pod to run.

---

## 4. Workload Hardening: The `securityContext`

At the senior level, deploying a Pod running as `root` is an immediate failure in Code Review.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secured-api
spec:
  securityContext:
    runAsUser: 1000            # Explicitly non-root
    runAsGroup: 3000
    fsGroup: 2000              # Allows the user to read mounted volumes
  containers:
  - name: api
    image: my-company/api:v2
    securityContext:
      allowPrivilegeEscalation: false # Prevents 'sudo' or setuid attacks
      readOnlyRootFilesystem: true    # Container cannot write to its own OS
      capabilities:
        drop:
        - ALL                         # Drop all Linux elevated permissions
        add:
        - NET_BIND_SERVICE            # Only add back exactly what is needed (e.g. port 80)
```
