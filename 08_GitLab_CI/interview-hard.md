## Hard

**15. How do you govern a multi-tenant GitLab CI environment where hundreds of teams create their own pipelines?**

1. **Pipeline templates:** Disable classic CI and mandate that all pipelines use `extends:` or `include:` to inherit from central templates. Ensure mandatory security scans (credential scanning, SAST, container scanning) run on every pipeline.
2. **GitLab Environments with protected environments:** Require environment declarations for all production deployments. Protected environments restrict which roles can trigger deploys and require designated approvers.
3. **DORA Metrics:** GitLab's built-in DORA metrics (deployment frequency, change failure rate, lead time, MTTR) are tracked automatically per project. Used to measure platform health across teams.
4. **Runner isolation:** Use dedicated GitLab Runners with appropriate tags for different workloads (GPU runners for ML, high-memory for builds). Prevent privilege escalation with `--security-opt=no-new-privileges` on Docker executors.

**16. How do you migrate 100 Jenkins pipelines to GitLab CI?**

A big-bang migration is too risky. Phased approach:

1. **Categorize:** Group the 100 pipelines by complexity and pattern. Identify 5-10 representative pilots.
2. **Pilot:** Convert pilots to `.gitlab-ci.yml`. Create GitLab CI `include:` templates that replicate Jenkins Shared Library functions.
3. **Tooling and documentation:** Build a conversion guide mapping `Jenkinsfile` constructs to GitLab CI equivalents. Run workshops for developers.
4. **Phased rollout:** Onboard teams in waves, simplest pipelines first. New projects start on GitLab CI only.
5. **Decommission:** Archive Jenkins data, shut down servers after all pipelines are migrated and validated.

**17. How do you design a security scanning pipeline that blocks vulnerable code from reaching production?**

Multi-layer approach using GitLab's built-in security features:

1. **SAST:** Runs on every MR, scans source code for vulnerability patterns. Results appear in the MR widget.
2. **SCA / Dependency Scanning:** Detects known CVEs in third-party libraries. Fail the pipeline if a critical severity CVE is found.
3. **Container scanning:** Scans the built Docker image against Trivy or Grype. Blocks promotion if high/critical CVEs present in OS packages.
4. **Secret detection:** Gitleaks scans the diff for committed secrets on every push.
5. **DAST:** Runs against a deployed staging environment for runtime vulnerability detection.
6. **Policy gates:** GitLab Security Policies (MR approval policies) require security team sign-off when scanning reports new critical findings.

**18. What is GitLab's Dependency Proxy and why is it useful in CI pipelines?**

The Dependency Proxy is GitLab's pull-through cache for Docker Hub images. Instead of each CI job pulling `python:3.11` from Docker Hub (subject to rate limits and slow external pulls), jobs pull from `registry.gitlab.com/group/dependency_proxy/containers/python:3.11`. GitLab caches the image internally. Benefits: eliminates Docker Hub rate limit failures in CI, reduces external network egress, and speeds up job startup time.
