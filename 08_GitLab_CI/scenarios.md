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
