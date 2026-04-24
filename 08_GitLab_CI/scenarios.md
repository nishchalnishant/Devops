# Production Scenarios & Troubleshooting Drills (Senior Level)

### Scenario 1: Shared Runner Exhaustion
**Problem:** Builds are stuck in "Pending" on GitLab.com.
**Fix:** Register a private runner on an EC2 instance and use Tags to route your jobs to it.

### Scenario 2: DAG (Directed Acyclic Graph)
**Problem:** Stage 3 is waiting for Stage 2 to finish completely.
**Fix:** Use the `needs` keyword to allow jobs to start as soon as their specific dependency is done, ignoring stage boundaries.

### Scenario 3: Dynamic Pipeline Generation
**Problem:** You have 100 microservices in a monorepo; you don't want a 5000-line `.gitlab-ci.yml`.
**Fix:** Use a "Trigger Job" that runs a script to generate a YAML file, then uses `trigger:include:artifact` to run the generated pipeline.

---

## Scenario 1: Runner Tag Mismatch
**Symptom:** Job is stuck in `pending` state with "This job is stuck because the project doesn't have any runners online with any of these tags".
**Diagnosis:** The job is tagged with `production-deploy` but no runner has that tag assigned.
**Fix:** Assign the correct tag to the GitLab Runner in settings or update the `.gitlab-ci.yml`.

## Scenario 2: Artifact Expiry causing Deployment Failure
**Symptom:** The `deploy` job fails because it cannot find the build artifacts from the `build` job.
**Diagnosis:** The `expire_in` setting for the build job is too short (e.g., 10 mins), and the manual deploy job was triggered after the artifact was deleted.
**Fix:** Increase `expire_in: 1 week` or use `dependencies:` to ensure the artifact is passed.

---

### Scenario 2: Pipeline Passes but Docker Image Not Pushed — Silent Registry Authentication Failure

**Problem:** A GitLab CI pipeline shows all stages green including the `docker push` step. But when developers pull the image from the GitLab Container Registry, they get "manifest not found." The image was never actually pushed.

**Diagnosis:**
```bash
# Check if the docker login step succeeded
# In .gitlab-ci.yml
docker login -u "$CI_REGISTRY_USER" -p "$CI_REGISTRY_PASSWORD" "$CI_REGISTRY"

# The issue: $CI_REGISTRY_PASSWORD is empty when:
# 1. Pipeline triggered by an external webhook that doesn't inherit CI variables
# 2. The job has deploy_freeze or protected variable scope mismatch
# 3. The runner is using a custom executor that doesn't inject CI variables

# Verify in the job log
echo "Registry: $CI_REGISTRY"
echo "User set: $([ -n "$CI_REGISTRY_USER" ] && echo yes || echo NO)"
echo "Password set: $([ -n "$CI_REGISTRY_PASSWORD" ] && echo yes || echo NO)"
```

**Root causes and fixes:**

1. **Protected variable + unprotected branch:** `CI_REGISTRY_PASSWORD` marked as `Protected` in project settings. Pipeline running on a non-protected branch can't access it. Fix: use `CI_JOB_TOKEN` which is always available:
```yaml
build:
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_JOB_TOKEN $CI_REGISTRY
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
```

2. **`docker push` exit code suppressed by `|| true`:** A previous engineer added `|| true` to ignore errors — `docker push` failure no longer fails the job. Audit the script for error suppression.

3. **Using buildah/kaniko without registry config:** Kaniko doesn't use the Docker daemon; it needs explicit registry credentials in `/kaniko/.docker/config.json`:
```yaml
build:
  image:
    name: gcr.io/kaniko-project/executor:v1.23.0
    entrypoint: [""]
  script:
    - mkdir -p /kaniko/.docker
    - echo "{\"auths\":{\"$CI_REGISTRY\":{\"auth\":\"$(echo -n $CI_REGISTRY_USER:$CI_JOB_TOKEN | base64)\"}}}" > /kaniko/.docker/config.json
    - /kaniko/executor --context $CI_PROJECT_DIR --dockerfile $CI_PROJECT_DIR/Dockerfile --destination $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
```

---

### Scenario 3: GitLab Runner Hangs on Git Clone — Large Repository Timeout

**Problem:** A monorepo of 15GB (large binary assets committed without Git LFS) causes the `git clone` step in every pipeline to take 20+ minutes. Pipelines randomly timeout. The runner's disk fills up.

**Diagnosis:**
```yaml
# Default GitLab clone behavior — full clone every time
# Check what's eating space
GIT_STRATEGY: clone   # this is the default — clones fresh every time
```

**Fix — use shallow clones with `GIT_DEPTH`:**
```yaml
variables:
  GIT_DEPTH: "1"           # only fetch the latest commit — no history
  GIT_STRATEGY: fetch      # reuse the runner's local repo (incremental fetch)

# For jobs that need full history (e.g., git log for changelog generation)
changelog:
  variables:
    GIT_DEPTH: "0"         # full history for this one job
  script:
    - git log --oneline HEAD~50..HEAD
```

**For truly large binary files — migrate to Git LFS:**
```bash
git lfs install
git lfs track "*.psd" "*.bin" "*.zip"
git add .gitattributes
git commit -m "Track binaries with LFS"
```

Then in CI, configure the runner to skip LFS where not needed:
```yaml
variables:
  GIT_LFS_SKIP_SMUDGE: "1"   # don't download LFS files unless explicitly needed
```

**Persistent caching between pipeline runs:**
```yaml
cache:
  key: $CI_COMMIT_REF_SLUG
  paths:
    - .git/       # CAUTION: caching .git can cause corruption; test carefully
    # Better: cache build artifacts, not the git dir itself
    - node_modules/
    - vendor/
```

---

### Scenario 4: Downstream Pipeline Trigger Not Firing After Merge

**Problem:** A monorepo has a parent pipeline that triggers downstream child pipelines for affected services. After a recent GitLab upgrade (16.x), the downstream triggers stopped firing silently — no error, the trigger job just completes immediately.

**Diagnosis:**
```yaml
# Check the trigger job
trigger-service-a:
  trigger:
    project: myorg/service-a
    branch: main
    strategy: depend   # wait for downstream to complete
```

**Root cause — GitLab 16.x changed `trigger` job behavior:**

In GitLab 16, trigger jobs no longer automatically pass `CI_JOB_TOKEN` permissions to downstream projects unless explicitly configured. The downstream pipeline starts but immediately fails on `git clone` with a 403, which the upstream doesn't surface as an error.

**Fix — grant token access:**

In the downstream project: `Settings → CI/CD → Token Access → Allow CI job tokens from the following projects` → add the parent project.

Or use a project access token instead of `CI_JOB_TOKEN`:
```yaml
trigger-service-a:
  trigger:
    project: myorg/service-a
    branch: $CI_COMMIT_REF_NAME
  variables:
    PARENT_PIPELINE_ID: $CI_PIPELINE_ID
```

**Debugging downstream trigger failures:**
```yaml
trigger-service-a:
  trigger:
    project: myorg/service-a
    strategy: depend   # surfaces downstream failure as upstream failure
  allow_failure: false
```

With `strategy: depend`, if the downstream pipeline fails, the trigger job fails — making the problem visible instead of silent.

---

### Scenario 5: Environment-Specific Variables Not Applied — Wrong Scope

**Problem:** A pipeline deploys to `staging` and `production` environments. Production deployment uses the staging database URL despite having a separate `PRODUCTION_DB_URL` variable configured.

**Diagnosis:**
```yaml
deploy-prod:
  stage: deploy
  environment:
    name: production
  script:
    - echo $DB_URL    # prints staging value
```

**Root cause:** Variable scope hierarchy in GitLab CI:

1. Instance variables (lowest priority)
2. Group variables
3. Project variables — **scope matters: "All environments" vs. specific environment**
4. `.gitlab-ci.yml` variables (highest priority for YAML-defined vars)

The `PRODUCTION_DB_URL` was defined in project settings with `Environment scope: production` but the job's `environment: name: production` string doesn't exactly match the scope pattern.

**Check the exact scope:** In `Settings → CI/CD → Variables`, the scope field uses wildcard matching. A scope of `prod*` matches `production`, but `production` scope does NOT match `production-eu` (no wildcards unless explicitly set).

**Verify variable injection in a job:**
```yaml
debug-vars:
  stage: .pre
  environment:
    name: production
  script:
    - env | grep -i db | sed 's/=.*/=[REDACTED]/'   # print var names without values
```

**Explicit environment scope in YAML (overrides all):**
```yaml
variables:
  DB_URL: "postgresql://staging-host/db"   # default

deploy-prod:
  environment:
    name: production
  variables:
    DB_URL: "postgresql://prod-host/db"   # job-level override — highest priority
```

---

### Scenario 6: GitLab SAST Scanner Floods MRs with Hundreds of False Positives

**Problem:** After enabling GitLab SAST, every merge request gets 200+ security warnings. Developers start ignoring all security feedback, defeating the purpose of the scanner.

**Root cause:** Default SAST configuration scans test files, vendored dependencies, and generated code alongside application code.

**Fix — configure SAST exclusions:**
```yaml
include:
  - template: Security/SAST.gitlab-ci.yml

variables:
  SAST_EXCLUDED_PATHS: "spec,test,tests,tmp,vendor,node_modules,.bundle,*.generated.*"
  SAST_EXCLUDED_ANALYZERS: "bandit"   # disable noisy analyzer (python) if not a Python project
  SEARCH_MAX_DEPTH: "5"               # prevent deep scan of nested directories

semgrep-sast:
  variables:
    SEMGREP_TIMEOUT: "300"
```

**Triage existing findings before enforcing:**
```bash
# Export all findings to a baseline file
# MR-level: only report NEW findings vs. the baseline
```

Use GitLab's `SAST_EXCLUDED_PATHS` and review the SAST ruleset — disable rules that generate false positives for your stack (e.g., SQL injection rules firing on ORM query builders that are parameterized by design).

**Process fix:** Configure SAST to block only `Critical` and `High` severity with `allow_failure: false`. Leave `Medium` and `Low` as informational (`allow_failure: true`). Give teams a 30-day window to address existing high-severity findings before enforcing the gate.

---

### Scenario 7: Pipeline Uses `only/except` Rules and Misses Scheduled Pipeline Runs

**Problem:** A nightly scheduled pipeline (configured under `Schedules` in GitLab) should run integration tests. The pipeline runs but all jobs are skipped. The pipeline shows as "passed" with 0 jobs.

**Root cause:** Jobs using the legacy `only` keyword:
```yaml
integration-tests:
  only:
    - merge_requests   # only runs on MR pipelines
    - main             # or on the main branch push
```

Scheduled pipelines in GitLab create a `pipeline_source == schedule` event — not a push or MR event. The `only` rules don't match it.

**Fix — use `rules:` instead of `only/except`:**
```yaml
integration-tests:
  rules:
    - if: $CI_PIPELINE_SOURCE == "schedule"
      when: always
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
      when: always
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
      when: always
    - when: never   # explicitly skip everything else
```

**Quick test — add a debug job to verify pipeline source:**
```yaml
debug-source:
  script:
    - echo "Pipeline source: $CI_PIPELINE_SOURCE"
    - echo "Schedule: $CI_PIPELINE_SCHEDULE"
  rules:
    - when: always   # always run this debug job
```

The variable `$CI_PIPELINE_SOURCE` takes values: `push`, `merge_request_event`, `schedule`, `api`, `trigger`, `pipeline`, `web` — use it explicitly in `rules` conditions for predictable behavior.
