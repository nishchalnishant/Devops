# GitLab CI/CD Cheatsheet

Quick reference for `.gitlab-ci.yml`, runner commands, CI/CD patterns, and GitLab API.

***

## `.gitlab-ci.yml` Structure

```yaml
# Global defaults (applied to all jobs unless overridden)
default:
  image: alpine:3.18
  before_script:
    - echo "Starting job..."
  retry: 2
  timeout: 30 minutes
  interruptible: true           # Allow newer pipeline to cancel this one

variables:
  DEPLOY_ENV: production
  FF_USE_FASTZIP: "true"        # Feature flags
  GIT_DEPTH: "10"               # Shallow clone (faster)

stages:
  - build
  - test
  - security
  - deploy
```

***

## Job Keywords Reference

```yaml
my-job:
  stage: test
  image: python:3.11-slim

  # Trigger conditions
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
      when: always
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
      when: always
    - when: never                 # Skip in all other cases

  # OR use only/except (older, simpler)
  # only: [main, merge_requests]
  # except: [schedules]

  # Environment variables
  variables:
    PYTEST_OPTS: "--tb=short -v"

  # Dependencies (don't download artifacts from these jobs)
  needs: []                       # Run immediately, don't wait for stages

  # OR with artifacts
  needs:
    - job: build
      artifacts: true

  # Script phases
  before_script:
    - pip install -r requirements.txt
  script:
    - pytest $PYTEST_OPTS src/
  after_script:
    - echo "Always runs, even on failure"

  # Artifacts
  artifacts:
    paths:
      - dist/
      - coverage.xml
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
      junit: test-results.xml     # Shows test results in MR UI
    expire_in: 7 days
    when: always                  # always | on_success | on_failure

  # Caching
  cache:
    key: $CI_COMMIT_REF_SLUG
    paths:
      - .pip-cache/
    policy: pull-push             # pull = download only, push = upload only

  # Services (sidecar containers)
  services:
    - postgres:15
    - redis:7-alpine

  # Manual approval
  when: manual
  allow_failure: false            # Block next stage if not approved

  # Retry on failure
  retry:
    max: 2
    when:
      - runner_system_failure
      - stuck_or_timeout_failure

  # Resource limits
  timeout: 10 minutes
  tags:
    - docker
    - production                  # Target specific runners
```

***

## DAG Pipelines (`needs:`)

```yaml
# Without DAG: all test jobs must finish before any deploy job
# With DAG: deploy-frontend starts as soon as test-frontend finishes

build-frontend:
  stage: build
  script: npm run build

build-backend:
  stage: build
  script: go build ./...

test-frontend:
  stage: test
  needs: [build-frontend]         # Only waits for frontend build

test-backend:
  stage: test
  needs: [build-backend]          # Only waits for backend build

deploy-frontend:
  stage: deploy
  needs: [test-frontend]          # Skips waiting for backend test!
  script: kubectl apply -f frontend/

deploy-backend:
  stage: deploy
  needs: [test-backend, deploy-frontend]  # Waits for both
```

***

## Rules — Conditional Execution

```yaml
# Common rule patterns
rules:
  # Run on pushes to main only
  - if: $CI_COMMIT_BRANCH == "main"

  # Run on MRs only
  - if: $CI_PIPELINE_SOURCE == "merge_request_event"

  # Run on schedule only
  - if: $CI_PIPELINE_SOURCE == "schedule"

  # Run on tags only (e.g. v1.2.3)
  - if: $CI_COMMIT_TAG =~ /^v\d+\.\d+\.\d+$/

  # Skip if commit message contains [skip ci]
  - if: $CI_COMMIT_MESSAGE =~ /\[skip ci\]/
    when: never

  # Run only if specific files changed
  - changes:
      - src/**/*
      - requirements.txt

  # Combine conditions
  - if: $CI_COMMIT_BRANCH == "main"
    changes:
      - Dockerfile
    when: manual                  # Only manual trigger if Dockerfile changed on main
```

***

## Environments & Deployments

```yaml
deploy-staging:
  stage: deploy
  environment:
    name: staging
    url: https://staging.myapp.com
    on_stop: stop-staging          # Job to run when env is stopped
  script:
    - ./deploy.sh staging

stop-staging:
  stage: deploy
  environment:
    name: staging
    action: stop
  when: manual
  script:
    - ./teardown.sh staging

deploy-production:
  stage: deploy
  environment:
    name: production
    url: https://myapp.com
    deployment_tier: production    # Tracked in GitLab DORA metrics
  script:
    - ./deploy.sh production
  when: manual                     # Manual approval gate
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
```

***

## Includes — DRY Pipelines

```yaml
# Include shared templates
include:
  # From same repo
  - local: '.gitlab/ci/test.yml'
  - local: '.gitlab/ci/docker.yml'

  # From another repo (component)
  - project: 'org/platform/ci-templates'
    ref: 'v1.0'
    file: '/templates/security-scan.yml'

  # From GitLab template library
  - template: 'Security/SAST.gitlab-ci.yml'
  - template: 'Jobs/DAST.gitlab-ci.yml'

  # Remote URL
  - remote: 'https://example.com/ci/template.yml'
```

***

## Cache vs Artifacts

| | Cache | Artifacts |
|:---|:---|:---|
| **Purpose** | Speed up builds (deps, compiled files) | Pass files between jobs |
| **Scope** | Per-runner, per-project | Per-pipeline, then archived |
| **Storage** | Runner-local or distributed | GitLab server |
| **Cross-pipeline** | Yes | No (by default) |
| **Key** | Configurable (`$CI_COMMIT_REF_SLUG`) | Per-job |

```yaml
# Optimal cache setup for Python
cache:
  key:
    files:
      - requirements.txt          # Bust cache only when requirements change
  paths:
    - .pip-cache/
  policy: pull-push

# Then in script:
script:
  - pip install --cache-dir .pip-cache -r requirements.txt
```

***

## GitLab Runner Commands

```bash
# Installation (Linux)
curl -L "https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh" | sudo bash
sudo apt-get install gitlab-runner

# Registration
gitlab-runner register                                    # Interactive
gitlab-runner register \
  --non-interactive \
  --url https://gitlab.com \
  --registration-token $RUNNER_TOKEN \
  --executor docker \
  --docker-image alpine:latest \
  --tag-list "docker,production" \
  --description "my-runner"

# Management
gitlab-runner list                                        # List registered runners
gitlab-runner status                                      # Runner service status
gitlab-runner start / stop / restart
gitlab-runner verify                                      # Verify connectivity

# Run job locally (debugging)
gitlab-runner exec docker my-job-name                    # Run specific job locally

# Config file location
cat /etc/gitlab-runner/config.toml

# Force runner to update
gitlab-runner stop && gitlab-runner start
```

***

## Predefined CI/CD Variables

```bash
CI_COMMIT_SHA           # Full commit SHA
CI_COMMIT_SHORT_SHA     # First 8 chars
CI_COMMIT_BRANCH        # Branch name (not set for tags)
CI_COMMIT_TAG           # Tag name (only set on tag pipelines)
CI_COMMIT_MESSAGE       # Commit message
CI_COMMIT_AUTHOR        # Author name <email>

CI_PIPELINE_ID          # Unique pipeline ID
CI_PIPELINE_SOURCE      # push | merge_request_event | schedule | web
CI_JOB_ID               # Unique job ID
CI_JOB_NAME             # Job name (e.g. "test")
CI_JOB_STAGE            # Stage name (e.g. "test")
CI_JOB_TOKEN            # Token for GitLab API (scoped to job)

CI_PROJECT_ID           # GitLab project ID
CI_PROJECT_NAME         # Project name
CI_PROJECT_PATH         # namespace/project-name
CI_PROJECT_URL          # https://gitlab.com/namespace/project
CI_DEFAULT_BRANCH       # "main"

CI_REGISTRY             # registry.gitlab.com
CI_REGISTRY_IMAGE       # Full image path (registry.gitlab.com/namespace/project)
CI_REGISTRY_USER        # Login for GitLab Container Registry
CI_REGISTRY_PASSWORD    # Password (=CI_JOB_TOKEN)

GITLAB_USER_EMAIL       # Email of user who triggered the pipeline
GITLAB_USER_NAME        # Name of user who triggered
```

***

## Container Registry (Built-in)

```yaml
build-and-push:
  stage: build
  image: docker:24
  services:
    - docker:24-dind
  variables:
    DOCKER_TLS_CERTDIR: "/certs"
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA .
    - docker build -t $CI_REGISTRY_IMAGE:latest .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA
    - docker push $CI_REGISTRY_IMAGE:latest
```

***

## Security Scanning (Auto DevOps Templates)

```yaml
include:
  - template: Security/SAST.gitlab-ci.yml       # Static analysis
  - template: Security/Secret-Detection.gitlab-ci.yml
  - template: Security/Dependency-Scanning.gitlab-ci.yml
  - template: Security/Container-Scanning.gitlab-ci.yml
  - template: Security/DAST.gitlab-ci.yml

variables:
  SAST_EXCLUDED_PATHS: "tests, vendor"
  DS_EXCLUDED_PATHS: "tests"
  DAST_WEBSITE: https://staging.myapp.com
  CS_IMAGE: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA
```

***

## Multi-Project Pipelines

```yaml
# Trigger a pipeline in another project
trigger-deploy:
  stage: deploy
  trigger:
    project: org/platform/deploy-repo
    branch: main
    strategy: depend              # Wait for triggered pipeline to finish
  variables:
    IMAGE_TAG: $CI_COMMIT_SHORT_SHA
    ENVIRONMENT: production
```

***

## GitLab API Quick Reference

```bash
GITLAB_URL="https://gitlab.com"
TOKEN="$GITLAB_TOKEN"
PROJECT_ID="123"

# Pipelines
curl "$GITLAB_URL/api/v4/projects/$PROJECT_ID/pipelines" -H "PRIVATE-TOKEN: $TOKEN"

# Trigger pipeline
curl -X POST "$GITLAB_URL/api/v4/projects/$PROJECT_ID/pipeline" \
  -H "PRIVATE-TOKEN: $TOKEN" \
  -F "ref=main" \
  -F "variables[DEPLOY_ENV]=production"

# Cancel pipeline
curl -X POST "$GITLAB_URL/api/v4/projects/$PROJECT_ID/pipelines/456/cancel" \
  -H "PRIVATE-TOKEN: $TOKEN"

# List MRs
curl "$GITLAB_URL/api/v4/projects/$PROJECT_ID/merge_requests?state=opened" \
  -H "PRIVATE-TOKEN: $TOKEN" | jq '.[].title'

# Create MR
curl -X POST "$GITLAB_URL/api/v4/projects/$PROJECT_ID/merge_requests" \
  -H "PRIVATE-TOKEN: $TOKEN" \
  -d "source_branch=feature/my-feature&target_branch=main&title=My Feature"

# Get project variables
curl "$GITLAB_URL/api/v4/projects/$PROJECT_ID/variables" -H "PRIVATE-TOKEN: $TOKEN"

# Create/update variable
curl -X POST "$GITLAB_URL/api/v4/projects/$PROJECT_ID/variables" \
  -H "PRIVATE-TOKEN: $TOKEN" \
  -F "key=MY_VAR" -F "value=my-value" -F "protected=true" -F "masked=true"
```
