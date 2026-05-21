---
description: Internal Developer Platforms (IDP), Backstage, self-service infrastructure, and golden paths for senior platform engineers.
---

# Platform Engineering — Internal Developer Platforms (IDP)

```
Internal Developer Platform (IDP) — Deep Dive
├── The Core Problem
│   ├── Without platform: every team re-invents CI/CD, secrets, K8s networking
│   ├── With IDP: platform builds once, all teams consume
│   └── Goal: "right way" = "easy way" — the Golden Path
├── Golden Path Architecture
│   ├── Developer portal: Backstage (form → template → automated provisioning)
│   ├── GitOps layer: ArgoCD reconciles Crossplane Claims + app manifests
│   ├── IaC: Crossplane for team-level resources; Terraform for platform infra
│   └── Observability: Grafana dashboards + PagerDuty provisioned by template
├── Backstage Deep Dive
│   ├── Software Catalog: YAML entity definitions in each repo
│   ├── Software Templates: wizard → scaffold repo + register entity + trigger CI
│   ├── TechDocs: mkdocs-material in repo → auto-published to Backstage
│   └── Plugins: K8s, GitHub Actions, Grafana, Kubecost, PagerDuty
├── Crossplane Architecture
│   ├── XRD: CompositeResourceDefinition — defines developer-facing API schema
│   ├── Composition: maps XRD fields to actual Provider resources (RDS, GCS)
│   ├── Claim: developer creates XRC → Crossplane creates cloud resource
│   ├── Provider: AWS, GCP, Azure plugins (authenticate via IRSA/Workload Identity)
│   └── Composite resource: internal resource wiring multiple provider resources
├── Self-Service Maturity Model
│   ├── L0: manual tickets, 2-week wait
│   ├── L1: documented runbooks, humans execute
│   ├── L2: scripts exist, requires knowledge
│   ├── L3: self-service portal (Backstage), no expertise required
│   └── L4: invisible — infra appears automatically in developer workflow
├── Platform Team Operating Model
│   ├── Platform-as-a-product: roadmap, backlog, quarterly OKRs
│   ├── Measure outcomes: DORA, Internal NPS, onboarding time
│   ├── Design for 80% case: escape hatches for edge cases
│   └── Deprecation policy: 3-month notice + migration guide for breaking changes
└── Logic & Trickiness
    ├── Crossplane vs Terraform: Crossplane for team self-service; Terraform for platform infra
    ├── Backstage adoption: start with catalog (immediate value), add templates later
    ├── Paved road: build 80% well, leave escape hatches for edge cases
    └── Platform metrics: measure developer experience, not platform team output
```

## First Principles

- An IDP exists because developer teams repeat the same infra work — abstract it once so every team benefits automatically.
- The platform team is a product team: their customers are developers; their product is the IDP; their north star is developer productivity, not platform complexity.
- Backstage Software Catalog is the foundation — you cannot build discoverability, TechDocs, or templates without knowing what services exist and who owns them.
- Crossplane abstracts the "what" (PostgreSQL) from the "how" (RDS Multi-AZ in us-east-1 with encrypted storage) — developers should never need to know the "how."
- Self-service maturity is a journey: L3 is the goal for 80% of use cases; L4 is aspirational for the most common workflows.

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

***

## System Design Perspective

**IDP Bootstrapping Sequence (New Organization)**
1. Start with Software Catalog: import all existing services from GitHub/GitLab — get discoverability first.
2. Add TechDocs: link existing runbooks and ADRs to catalog entities.
3. Build one golden path template for the most common service type (e.g., Node.js REST API); validate with 3–5 pilot teams.
4. Add Crossplane for database provisioning — the highest-toil infrastructure request in most orgs.
5. Add cost plugin (Kubecost integration) to the catalog entity page — developers see their service's cost inline.

**Backstage Plugin Architecture for Enterprise**
- Core plugins managed by platform team (catalog, scaffolder, TechDocs, K8s, Grafana).
- Team-contributed plugins via a Plugin Registry pattern: teams submit plugins for review; platform team approves and hosts; prevents plugin sprawl.
- Authentication: OAuth2 via Okta/Azure AD; RBAC enforced at catalog entity level (only owners can modify their entity's metadata).

**Crossplane Upgrade Strategy**
- Provider upgrades: test new provider version in a staging control plane; run a suite of synthetic Claims to validate behavior before promoting to production.
- Composition breaking changes: create a new Composition version (v2); add a migration period where both v1 and v2 are supported; automate PR creation to teams on v1 with migration instructions; deprecate v1 after 90 days.
