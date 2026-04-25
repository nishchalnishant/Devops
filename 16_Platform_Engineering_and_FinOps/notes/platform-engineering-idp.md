---
description: Internal Developer Platforms (IDP), Backstage, self-service infrastructure, and golden paths for senior platform engineers.
---

# Platform Engineering — Internal Developer Platforms (IDP)

## The Core Problem Platform Engineering Solves

Without a platform team, every developer team re-invents the same wheel:
- Writing their own CI/CD pipeline YAML from scratch
- Figuring out how to provision S3 buckets securely
- Managing their own secrets rotation
- Debugging Kubernetes networking from zero

A Platform Engineer's job is to make the **"right way" the easy way** — the Golden Path.

***

## The Golden Path Architecture

```
Developer (Portal/CLI/API)
        │
        │ "Give me a new microservice"
        ▼
    Backstage (IDP Portal)
        │
        ├── Creates GitHub repo from template
        ├── Registers service in Service Catalog
        └── Triggers Terraform / Crossplane to provision:
                ├── ECR image registry
                ├── IAM roles (least privilege)
                ├── ArgoCD Application object
                └── PagerDuty service + alert routing

Day 2: Developer pushes code → CI/CD is already configured → Deployed automatically
```

***

## Backstage — The Platform Portal

Backstage (by Spotify, CNCF) is the most widely adopted IDP framework. It provides:

1. **Software Catalog:** Central registry of all services, APIs, resources with ownership metadata
2. **TechDocs:** Documentation-as-code, auto-generated from repos
3. **Software Templates (Scaffolding):** "Create a new service" wizard that provisions everything via code
4. **Plugins:** Integrate with GitHub, Kubernetes, PagerDuty, CI/CD, cost tools

### Backstage Software Template (Scaffolding)

```yaml
# template.yaml — Creates a new Python microservice
apiVersion: scaffolder.backstage.io/v1beta3
kind: Template
metadata:
  name: python-microservice
  title: Python Microservice
  tags: [python, recommended]
spec:
  owner: platform-team
  type: service
  
  parameters:
    - title: Service Info
      required: [serviceName, owner]
      properties:
        serviceName:
          type: string
          title: Service Name
        owner:
          type: string
          title: Owner Team
        includeDatabase:
          type: boolean
          default: false
          title: Include PostgreSQL?

  steps:
    - id: fetch-template
      name: Fetch template
      action: fetch:template
      input:
        url: ./skeleton    # Template directory
        values:
          serviceName: ${{ parameters.serviceName }}
          owner: ${{ parameters.owner }}

    - id: publish
      name: Create GitHub repo
      action: publish:github
      input:
        repoUrl: github.com?owner=my-org&repo=${{ parameters.serviceName }}

    - id: create-argocd-app
      name: Register in ArgoCD
      action: argocd:create-resources
      input:
        appName: ${{ parameters.serviceName }}
        
    - id: register
      name: Register in Catalog
      action: catalog:register
      input:
        repoContentsUrl: ${{ steps.publish.output.repoContentsUrl }}
```

***

## Crossplane — Kubernetes-Native Infrastructure Provisioning

Crossplane extends Kubernetes with CRDs for cloud resources, allowing teams to provision AWS/GCP/Azure infrastructure the same way they deploy apps — via `kubectl apply`.

```yaml
# Developer creates this YAML; Crossplane provisions a real RDS instance
apiVersion: database.example.org/v1alpha1
kind: PostgreSQLInstance
metadata:
  name: my-service-db
  namespace: my-team
spec:
  parameters:
    storageGB: 20
    version: "14"
    region: us-east-1
  compositionRef:
    name: postgresql-aws        # Platform team defines the composition
  writeConnectionSecretToRef:
    name: db-connection         # Connection string stored as K8s Secret
```

***

## Self-Service Maturity Model

| Level | Description | Example |
|:---|:---|:---|
| **L0 — No Platform** | Manual tickets, 2-week lead time | "Open a JIRA to get an S3 bucket" |
| **L1 — Documentation** | Runbooks exist, manual execution | Copy-paste Terraform commands |
| **L2 — Automation** | Scripts exist, but require knowledge | `./provision-bucket.sh my-bucket` |
| **L3 — Self-Service** | Portal/API, no knowledge required | Click "New Service" in Backstage |
| **L4 — Cognitive Load Zero** | Fully embedded in developer workflow | `git push` provisions everything |

***

## Developer Experience Metrics

Platform teams should measure the impact of their work:

```
Deployment Frequency     → How often can a team deploy to production?
Change Lead Time         → From commit to production — how long?
Change Failure Rate      → % of deployments causing incidents
MTTR                     → Mean time to restore after incident

Internal NPS (developer survey):
  "How easy is it to deploy a new service?" 1-10
  "How easy is it to debug a production issue?" 1-10
```

***

## Logic & Trickiness Table

| Pattern | Junior Thinking | Senior Thinking |
|:---|:---|:---|
| **Golden Path** | Enforce one standard way | Make the recommended way easier, not mandatory |
| **Backstage adoption** | Build features no one asked for | Start with Software Catalog — it gives immediate value |
| **Crossplane vs Terraform** | Pick one | Crossplane for team self-service; Terraform for platform-level infra |
| **Platform metrics** | Count PRs merged | Measure developer experience: lead time, failure rate, MTTR |
| **Paved road** | Build everything | Build the 80% case well; leave escape hatches for edge cases |
