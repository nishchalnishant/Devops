# GitLab CI/CD & Auto DevOps

GitLab provides a single application for the entire DevOps lifecycle. Its CI/CD is known for its tight integration with the repository and its powerful "Auto DevOps" features.

#### 1. Core Concepts
*   **.gitlab-ci.yml:** The single configuration file that defines your pipeline.
*   **Runners:** The agents that execute the jobs. They use "Executors" (Docker, Shell, VirtualBox).
*   **Stages:** Define the execution order (e.g., `.pre`, `build`, `test`, `deploy`, `.post`).
*   **Artifacts:** Files passed between stages (e.g., a compiled binary from `build` to `test`).
*   **Dependencies:** Control which artifacts a specific job needs to download.

#### 2. Advanced Pipeline Patterns
*   **DAG (Directed Acyclic Graph):** Using the `needs` keyword to allow jobs to start as soon as their dependencies are ready, without waiting for the entire previous stage to finish.
*   **Child/Parent Pipelines:** Triggering separate pipeline files for different parts of a monorepo.
*   **Dynamic Pipelines:** Generating the CI configuration file on the fly during the pipeline execution.
*   **Environments & Canary:** Built-in support for tracking deployments and performing incremental rollouts.

#### 3. Security & Optimization
*   **Protected Variables:** Ensure secrets are only exposed to protected branches (like `main`).
*   **Masked Variables:** Prevent secrets from appearing in the job logs.
*   **Docker-in-Docker (DinD):** Running Docker commands inside a GitLab runner (requires privileged mode).
*   **Cache vs. Artifacts:** Use `cache` for project dependencies (speed) and `artifacts` for build outputs (integrity).