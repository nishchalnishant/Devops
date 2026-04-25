---
description: GitHub Actions reusable workflows, composite actions, and matrix strategy patterns for enterprise CI/CD.
---

# GitHub Actions — Reusable Workflows & Advanced Patterns

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
