---
description: GitHub Actions reusable workflows, composite actions, and matrix strategy patterns for enterprise CI/CD.
---

# GitHub Actions — Reusable Workflows & Advanced Patterns

```
Reusable Workflows & Advanced Patterns
├── Why Reusable Workflows
│   ├── Problem: 50 repos copy-pasting same workflow
│   ├── Solution: platform-workflows repo → service repos call it
│   └── Benefit: one change propagates to all callers
├── Architecture
│   ├── platform-workflows repo — owns called workflows
│   └── service-repo — has caller.yml with uses: org/platform-workflows/.github/workflows/build.yml@main
├── Defining a Called Workflow
│   ├── on: workflow_call: — trigger type
│   ├── inputs: — typed parameters (string, boolean, number, choice)
│   ├── secrets: — named secrets from caller (or secrets: inherit)
│   └── outputs: — values returned to caller
├── Calling a Reusable Workflow
│   ├── uses: org/repo/.github/workflows/file.yml@ref
│   ├── with: — pass inputs
│   ├── secrets: inherit — pass all caller secrets
│   └── secrets: MY_SECRET: ${{ secrets.MY_SECRET }} — explicit passing
├── Composite Actions
│   ├── .github/actions/name/action.yml
│   ├── using: composite — not Docker, not JavaScript
│   ├── inputs: — typed parameters with defaults
│   ├── steps: — must include shell: bash on each run: step
│   └── Usage: uses: ./.github/actions/setup-app
├── Matrix Strategy
│   ├── strategy.matrix — declare axes (os, python-version)
│   ├── fail-fast: false — see all results before failing
│   ├── max-parallel: N — cap simultaneous jobs
│   ├── exclude: — remove specific combinations
│   └── include: — add extra variables to specific combinations
└── Junior vs Senior Patterns
    ├── Code reuse: copy-paste → reusable workflow
    ├── Secrets: hardcoded → OIDC preferred
    ├── Build matrix: single OS → multi-OS via matrix
    └── Actions pinning: @v4 tag → @sha (immutable)
```

## First Principles

- Reusable workflows are the organizational scaling mechanism for CI/CD. Copy-paste workflows are fine for one repo; they become a maintenance liability at 10 repos and a security risk at 50 (one vulnerability in 50 separate files).
- The `on: workflow_call:` trigger separates the definition from the invocation. The called workflow is a contract: inputs it accepts, secrets it needs, outputs it produces. The caller is isolated from implementation details.
- `secrets: inherit` is the "pass everything" shortcut that violates least privilege. An explicit `secrets: MY_SECRET: ${{ secrets.MY_SECRET }}` forces the caller to declare which secrets the called workflow needs — auditable and constrained.
- Composite actions encapsulate a sequence of steps into a reusable unit. They run in the caller's job on the caller's runner — they're syntactic grouping, not a separate execution environment. No startup overhead.
- Matrix `fail-fast: false` is almost always the right choice in CI. If you're testing 9 OS/version combinations and one fails, you want to see all 9 results to know if it's OS-specific or universal. Aborting the other 8 loses that information.

## Why Reusable Workflows

In large organizations, teams copy-paste the same `build-and-push` workflow across 50 repositories. When a security team mandates a new SAST scan step, someone has to update 50 files. Reusable workflows solve this.

> **Core Insight:** Reusable workflows are the "shared library" equivalent in GitHub Actions. They enforce enterprise standards without taking away team autonomy.

***

## Reusable Workflow Architecture

```
org/platform-workflows/.github/workflows/
    build-and-scan.yml      ← Called workflow (the "library")
    deploy-to-k8s.yml
    security-gate.yml

service-repo/.github/workflows/
    ci.yml                  ← Caller workflow (the "consumer")
```

### Defining a Reusable Workflow (Called Workflow)

```yaml
# org/platform-workflows/.github/workflows/build-and-scan.yml
name: Build, Scan & Push

on:
  workflow_call:
    inputs:
      image-name:
        required: true
        type: string
      dockerfile-path:
        required: false
        type: string
        default: './Dockerfile'
    secrets:
      REGISTRY_TOKEN:
        required: true
    outputs:
      image-digest:
        description: "The SHA digest of the pushed image"
        value: ${{ jobs.build.outputs.digest }}

jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      digest: ${{ steps.push.outputs.digest }}
    steps:
      - uses: actions/checkout@v4

      - name: Build image
        run: docker build -f ${{ inputs.dockerfile-path }} -t ${{ inputs.image-name }} .

      - name: Scan with Trivy
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ inputs.image-name }}
          exit-code: '1'
          severity: 'CRITICAL,HIGH'

      - name: Push image
        id: push
        run: |
          docker push ${{ inputs.image-name }}
          echo "digest=$(docker inspect --format='{{index .RepoDigests 0}}' ${{ inputs.image-name }})" >> $GITHUB_OUTPUT
```

### Calling the Reusable Workflow

```yaml
# service-repo/.github/workflows/ci.yml
name: CI Pipeline

on: [push]

jobs:
  build:
    uses: org/platform-workflows/.github/workflows/build-and-scan.yml@main
    with:
      image-name: "my-registry.io/my-service:${{ github.sha }}"
    secrets:
      REGISTRY_TOKEN: ${{ secrets.REGISTRY_TOKEN }}

  deploy:
    needs: build
    uses: org/platform-workflows/.github/workflows/deploy-to-k8s.yml@main
    with:
      image-digest: ${{ needs.build.outputs.image-digest }}
    secrets: inherit   # Pass ALL caller secrets to the called workflow
```

***

## Composite Actions

Composite actions are like reusable workflow *steps* (not full jobs). Use them to group 3–5 related steps into a single named action.

```yaml
# .github/actions/setup-python-env/action.yml
name: 'Setup Python Environment'
description: 'Installs Python, dependencies, and configures cache'
inputs:
  python-version:
    description: 'Python version to use'
    required: false
    default: '3.11'

runs:
  using: "composite"
  steps:
    - uses: actions/setup-python@v5
      with:
        python-version: ${{ inputs.python-version }}
        cache: 'pip'

    - name: Install dependencies
      run: pip install -r requirements.txt
      shell: bash
```

**Usage in any workflow:**
```yaml
- uses: ./.github/actions/setup-python-env
  with:
    python-version: '3.12'
```

***

## Matrix Strategy (Parallel Testing)

```yaml
jobs:
  test:
    strategy:
      fail-fast: false       # Don't cancel other jobs if one fails
      max-parallel: 4        # Max concurrent jobs
      matrix:
        os: [ubuntu-latest, macos-latest]
        node: [18, 20, 22]
        exclude:
          - os: macos-latest
            node: 18         # Skip this specific combination
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
      - run: npm test
```

***

## Logic & Trickiness Table

| Pattern | Junior Approach | Senior Approach |
|:---|:---|:---|
| **Sharing secrets** | Hardcode secrets in each repo | Use `secrets: inherit` or org-level secrets |
| **Versioning reusable workflows** | Point to `@main` | Pin to a tag `@v2.1.0` for stability |
| **Composite vs Reusable** | Use reusable workflows for everything | Composites for steps, Reusables for full jobs |
| **Matrix explosion** | Test every combination | Use `exclude` and `max-parallel` to bound cost |
| **Artifact sharing** | Re-build in every job | Upload in `build`, download in `deploy` |

## System Design Perspective

**Pipeline scalability:**
- Reusable workflows enable a platform team to maintain CI/CD for the entire org from a single repository. 100 service repos call the same build/deploy workflow. When the platform team adds a new security scan, it automatically applies to all 100 repos on the next PR.
- Matrix strategy scales test coverage horizontally. A 3×3 matrix (3 OS × 3 Python versions) runs 9 parallel jobs. Total test time = slowest job, not sum of all 9. This is free horizontal scaling with no infrastructure management.
- GitHub Required Workflows (Enterprise) enforce mandatory workflows org-wide. Even if a service team's workflow doesn't include the platform security scan, the Required Workflow runs anyway on every PR.

**Runner architecture trade-offs:**
- Composite actions run on the caller's runner — no additional runner provisioning overhead. They're the right choice when you just need to group steps and reduce repetition within a single job.
- Reusable workflows can define their own `runs-on`. A platform team's deploy workflow can specify `runs-on: [self-hosted, production-runners]` — callers don't need to know which runner pool production deploys use. Runner routing is encapsulated.
- `max-parallel` in matrix prevents overwhelming self-hosted runner pools or downstream staging environments that cannot handle N concurrent deploys.

**Failure recovery:**
- A reusable workflow failure fails the caller's job. The caller can use `if: failure()` or `continue-on-error: true` to handle the failure gracefully and send notifications.
- Versioning reusable workflows (`@v2.1.0` not `@main`) means a breaking change in the called workflow doesn't break all callers simultaneously. Teams opt into upgrades at their own pace. This is the `semver` principle applied to CI/CD.
- If a matrix job fails with `fail-fast: false`, only the failing combination is retried when you click "Re-run failed jobs." The successful combinations don't re-run — saving time and compute.

**Caching strategies:**
- Composite actions share the caller's runner workspace and cache. `actions/cache` in a composite action uses the caller's job cache context — the same cache key namespace.
- Reusable workflows run in their own job context. Caches from the caller's job are not automatically available. The called workflow must configure its own `actions/cache` or use `upload-artifact`/`download-artifact` to share built artifacts.

**Security boundaries:**
- `secrets: inherit` passes all caller secrets to the called workflow. If the called workflow is in an external repo, this is especially dangerous — you're giving a third-party workflow all your secrets. Always prefer explicit secret passing for cross-repo calls.
- Pinning reusable workflows to a tag (`@v2.1.0`) or SHA (`@abc123`) prevents the called workflow from being updated under you. A `@main` ref means any change to the platform workflow immediately affects all callers — good for patches, dangerous for breaking changes.
