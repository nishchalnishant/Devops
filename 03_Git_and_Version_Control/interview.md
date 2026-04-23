# Git & Version Control — Interview Questions

All difficulty levels combined.

---

## Easy

**1. What is the difference between `git merge` and `git rebase`?**

`git merge` creates a new merge commit preserving the full branch history. `git rebase` replays commits from one branch onto another, creating a linear history. Rebase rewrites commit hashes — never rebase shared/published branches.

**2. What is a Git conflict and how do you resolve it?**

A conflict occurs when two branches have changed the same lines of a file. Git marks the conflict in the file with `<<<<<<<`, `=======`, `>>>>>>>` markers. You edit the file to keep the correct content, then `git add` and complete the merge or rebase.

**3. What is `git stash`?**

`git stash` temporarily saves uncommitted changes (both staged and unstaged) to a stack, restoring a clean working directory. `git stash pop` reapplies the most recent stash and removes it from the stack.

**4. What is the difference between `git reset` and `git revert`?**

`git reset` moves the branch pointer backward, removing commits from history (destructive if already pushed). `git revert` creates a new commit that undoes the changes of a previous commit — safe for shared branches.

**5. What is a Pull Request (PR) / Merge Request (MR)?**

A PR/MR is a code review workflow where a developer proposes merging their feature branch into the main branch. Reviewers can comment, request changes, and approve before the merge is completed.

**6. What is `git cherry-pick`?**

`git cherry-pick <commit-hash>` applies the changes from a specific commit onto the current branch without merging the entire branch.

**7. What is `.gitignore`?**

A file listing patterns of files and directories that Git should not track. Common examples: `node_modules/`, `.env`, `*.log`, `dist/`.

**8. What is the difference between `git fetch` and `git pull`?**

`git fetch` downloads remote changes without integrating them into the working branch. `git pull` fetches and immediately merges (or rebases) into the current branch.

**9. What is a Git tag?**

A tag is a named pointer to a specific commit, typically used to mark release versions (e.g., `v1.0.0`). Lightweight tags are just pointers; annotated tags include metadata and can be signed.

**10. What is `HEAD` in Git?**

`HEAD` is a pointer to the currently checked-out commit or branch tip. It represents "where you are" in the repository history.

---

## Medium

**11. Explain Git's object model: blob, tree, commit, tag.**

Git stores everything as content-addressed objects in `.git/objects/`:
- **Blob:** stores raw file content (no filename).
- **Tree:** stores a directory listing — maps filenames to blob/tree SHA-1 hashes.
- **Commit:** stores a tree pointer (root directory snapshot), parent commit(s), author, timestamp, and message.
- **Tag:** annotated tag object with a pointer to another object, tagger identity, and message.

Each object's SHA-1 is derived from its content — identical content = identical SHA-1 = shared storage (deduplication built in).

**12. How does `git reflog` help in disaster recovery?**

`git reflog` records every position HEAD has been at, including commits that are no longer reachable via any branch. If you accidentally deleted a branch or did a hard reset, the old commit SHA-1 appears in the reflog. You can recover it with `git checkout -b recovered-branch <sha1>`.

**13. What is a Git monorepo and what are its trade-offs?**

A monorepo stores multiple projects/services in a single repository. Trade-offs:
- **Pros:** Atomic cross-service commits, unified CI, easier code sharing and refactoring across boundaries.
- **Cons:** CI must determine which services were affected (requires smart change detection); clone/fetch size grows; requires tooling like Nx, Bazel, or Turborepo for scalable builds and affected-only test runs.

**14. What is `git bisect` and how does it work?**

`git bisect` is a binary search through commit history to find which commit introduced a regression. You start with `git bisect start`, mark the known-good commit with `git bisect good`, and the known-bad commit with `git bisect bad`. Git checks out the midpoint; you test and mark it good or bad. Git narrows the range until it identifies the first bad commit. Can be automated: `git bisect run ./test.sh`.

**15. How do you enforce a linear Git history in a team?**

Configure the repository to require squash merges or rebase merges only — disabling regular merge commits. In GitHub: enable "Require linear history" in branch protection rules. In GitLab: set "Merge method" to "Fast-forward merge" or "Squash and merge." This keeps the main branch history linear and bisectable.

**16. What is commit signing and why does it matter for supply chain security?**

Commit signing uses GPG or SSH keys to cryptographically sign commits, proving they came from the stated author. Without signing, anyone can set `git config user.email` to any address and commit as if they were another person. For supply chain security, signed commits are an input to SLSA — you can enforce that only commits from authenticated identities can be merged to protected branches.

---

## Hard

**17. How do you manage versioning and dependency between dozens of microservices in a CI/CD context?**

1. **Semantic Versioning:** All services and APIs follow SemVer (`MAJOR.MINOR.PATCH`). Breaking API changes require a MAJOR bump.
2. **Consumer-Driven Contract Testing:** Use Pact. Consumer defines expected API contract; provider's CI runs consumer contracts as tests — prevents breaking changes from reaching production.
3. **Centralized Artifact Repository:** JFrog Artifactory or similar stores versioned Docker images. Each build produces an immutable tagged artifact.
4. **Bill of Materials (BOM):** A version-controlled BOM file defines the exact set of service versions known to work together for a release.

**18. Design a Git workflow for a team of 100 engineers with multiple concurrent release trains.**

- **Trunk-Based Development** with short-lived feature branches (<1 day ideally).
- **Feature flags** decouple deployment from feature release — merge incomplete features behind a flag.
- **Release branches** cut from main at release time (`release/2024-Q1`). Only cherry-picked bug fixes go to release branches.
- **Branch protection:** Require PR approval + passing CI before merge to `main`. No direct pushes.
- **Tooling:** Nx/Bazel for affected-only builds in the monorepo. Ship a golden path for branch naming and PR templates. Use conventional commits (`feat:`, `fix:`, `chore:`) for automated changelog generation.

**19. What is a Git `rerere` and when is it useful?**

`rerere` (Reuse Recorded Resolution) records how you resolved a merge conflict and automatically applies the same resolution if the same conflict occurs again. Enable with `git config rerere.enabled true`. This is valuable in workflows where a long-running feature branch is regularly rebased onto main — the same conflicts can appear repeatedly, and `rerere` resolves them automatically after the first manual resolution.
