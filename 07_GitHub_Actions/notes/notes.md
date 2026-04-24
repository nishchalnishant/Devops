# GitHub Actions & Modern CI/CD

GitHub Actions has redefined CI/CD by bringing automation directly into the repository. It is event-driven, allowing you to trigger workflows on almost any GitHub event.

#### 1. The Architecture
*   **Workflows:** The top-level YAML file in `.github/workflows`.
*   **Events:** Triggers like `push`, `pull_request`, `schedule` (cron), or `workflow_dispatch` (manual).
*   **Jobs:** A set of steps that run on the same runner. Jobs run in parallel by default.
*   **Steps:** Individual tasks (shell scripts or "Actions").
*   **Runners:** The servers that run the jobs. GitHub-hosted runners are clean VMs, while Self-hosted runners allow you to use your own infrastructure.

#### 2. Advanced Features
*   **Matrix Builds:** Running the same job across multiple versions of an OS or language (e.g., testing on Node 16, 18, and 20 simultaneously).
*   **Environments:** Provide protection rules (like manual approvals) and secret management for specific deployment targets (Dev, Prod).
*   **Reusable Workflows:** DRY (Don't Repeat Yourself) principle. Define a workflow once and call it from other repositories.
*   **Custom Actions:** Write your own automation logic in JavaScript or Docker and share it on the Marketplace.

#### 3. Security & Best Practices
*   **OIDC (OpenID Connect):** Connect GitHub Actions to AWS/Azure without using long-lived secrets/keys.
*   **GitHub Token:** Use the automatic `${{ secrets.GITHUB_TOKEN }}` for repo operations, but always restrict its permissions to `contents: read` unless more is needed.
*   **Caching:** Use `actions/cache` to speed up builds by caching dependencies like `node_modules` or `~/.m2`.