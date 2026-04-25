---
description: Medium-difficulty interview questions for Git workflows, branching strategies, and version control.
---

## Medium

**13. What is Git Flow and when should you NOT use it?**

Git Flow uses two permanent branches (`main`, `develop`) and three types of temporary branches (`feature/`, `release/`, `hotfix/`). The workflow: features merge into `develop`; when ready to release, a `release/` branch is cut from `develop` and merged into both `main` and `develop`; hotfixes branch from `main` and merge into both.

**Don't use Git Flow when:**
- You deploy continuously (multiple times a day). Git Flow's release branches create batching that delays delivery.
- Your team is small. The overhead of maintaining two permanent branches and strict merge rules slows down small teams.
- You practice trunk-based development. Git Flow and TBD are fundamentally incompatible philosophies.

**Use Git Flow** for software with explicit versioned releases (mobile apps, firmware, libraries) where multiple versions coexist in production.

**14. What is trunk-based development and what practices enable it?**

Trunk-based development (TBD) has all developers commit directly to `main` (the "trunk") or use very short-lived feature branches (< 1-2 days). This eliminates long-running branches and merge conflicts.

Enabling practices:
- **Feature flags:** Incomplete features are deployed but disabled in production. Developers merge daily; the feature is toggled on when ready.
- **Branch by abstraction:** For large refactors, create an abstraction layer, route existing code through it, then migrate to the new implementation behind the abstraction.
- **CI quality gate:** Every commit to main triggers a full test suite. A failing test blocks the next developer — culture of keeping main green.
- **Small PRs:** PRs reviewed and merged within hours, not days.

**15. What is an interactive rebase and what can it do?**

`git rebase -i HEAD~5` opens an editor listing the last 5 commits with commands:
- `pick` — keep commit as-is
- `reword` — change the commit message
- `edit` — stop and amend the commit
- `squash` (`s`) — combine with the previous commit, merge messages
- `fixup` (`f`) — combine with the previous commit, discard this message
- `drop` — delete the commit

Use cases: squash WIP commits before merging a PR, reorder commits for logical clarity, edit a message in the middle of history, or drop a commit that introduced a problem.

**16. What is `git worktree` and when is it useful?**

`git worktree add <path> <branch>` creates a second working directory linked to the same repository, checked out to a different branch. You can work on two branches simultaneously without `git stash` or cloning twice. Use case: you're mid-feature on branch A; a critical hotfix needs to be applied to `main`. Instead of stashing your work, `git worktree add ../hotfix main` gives you a fresh working directory for the hotfix while your feature branch is untouched.

**17. What is `git blame` and how do you use it for debugging?**

`git blame <file>` annotates every line with the last commit that modified it, including the author, timestamp, and SHA. Useful for understanding why a line exists — not to "blame" but to find context. `git blame -L 20,35 src/main.py` restricts output to lines 20-35. `git log -p -S "function_name"` (pickaxe search) finds commits that added or removed a specific string — more powerful for tracing when a function was introduced or deleted.

**18. How do you enforce commit message standards across a team?**

Using a `commit-msg` hook with a regex:
```bash
# .git/hooks/commit-msg
if ! grep -qE "^(feat|fix|docs|chore|refactor|test)(\(.+\))?: .{10,}" "$1"; then
  echo "ERROR: Commit must follow Conventional Commits format"
  exit 1
fi
```

At the CI level: use `commitlint` in a pre-merge check. In GitHub, use `semantic-pull-request` action to enforce PR title format (which becomes the squash commit message). Use `husky` to install the hook automatically when developers run `npm install`.

**19. How does `git submodule` work and what are the pitfalls?**

A submodule is a reference from a parent repository to a specific commit in another repository. The parent stores the submodule URL and the pinned commit SHA. `git submodule update --init --recursive` fetches and checks out the pinned commits.

**Pitfalls:**
- `git clone` does not initialize submodules — must use `--recursive` or run `git submodule update`.
- Forgetting to commit the submodule pointer update causes CI to use a stale submodule version.
- Hard to diff across submodule updates.
- Alternatives: Git subtree (simpler, no `.gitmodules`), or just vendoring dependencies.

**20. What is a monorepo and what tooling enables it at scale?**

A monorepo stores multiple projects (services, libraries, tools) in a single repository. Benefits: atomic cross-project changes, shared tooling, easier dependency management.

At scale, a monorepo requires:
- **Selective CI:** Only run tests/builds for the parts that changed. Tools: Nx, Turborepo, Bazel, `git diff --name-only`.
- **Workspace tooling:** npm workspaces, Yarn Berry, pnpm workspaces, or Cargo workspaces for package management.
- **Code ownership:** `CODEOWNERS` files per directory to enforce review requirements per team.
- **Trunk-based development:** Monorepos almost always pair with TBD; long-lived feature branches in monorepos cause massive merge conflicts.

**21. How do you handle large binary files in Git?**

Git is designed for text; storing large binaries (ML models, videos, compiled artifacts) bloats `.git/` and makes clone/fetch slow.

Solutions:
- **Git LFS (Large File Storage):** Files tracked by LFS are replaced with pointers in Git; the actual content is stored in an LFS server. `git lfs track "*.bin"` adds the pattern to `.gitattributes`. Clone fetches only the LFS pointers; `git lfs pull` downloads content on demand.
- **External artifact stores:** Don't store large artifacts in Git at all. Store in S3/GCS/Artifactory and reference by URL + checksum in code.
- **`.gitattributes` delta compression:** For moderately-sized assets that change infrequently, mark them as `binary` in `.gitattributes` to prevent Git from wasting time trying to diff them.
