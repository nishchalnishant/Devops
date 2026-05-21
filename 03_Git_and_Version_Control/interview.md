# Git and Version Control — Interview Prep

---
description: Easy interview questions for Git, branching, and version control fundamentals.
---

```
Git Interview — Easy
├── Remote Operations
│   ├── fetch vs pull (download only vs download+merge)
│   └── pull --rebase (avoid merge commit noise)
├── History Rewriting
│   ├── merge vs rebase (preserves history vs linearizes + new SHAs)
│   ├── cherry-pick (single commit backport)
│   └── reset --hard (dangerous: discards working tree)
├── Workflow Tools
│   ├── git stash (save/restore uncommitted work)
│   ├── git bisect (O(log N) binary search for regression)
│   └── git reflog (90-day safety net for all HEAD movements)
├── Repository State
│   ├── docker ps vs docker ps -a → git ps vs git ps -a analogy (running vs all containers)
│   ├── detached HEAD (HEAD points to SHA, not a branch name)
│   └── .gitignore patterns (glob, negation with !, directory anchoring)
├── Tags
│   ├── lightweight (pointer only — just a file with SHA)
│   └── annotated (full object: tagger, timestamp, message, signable)
└── Clone Strategies
    ├── full clone (all history — needed for bisect/blame)
    └── shallow --depth 1 (CI speed, no history)
```

### First Principles

- **Why fetch before pull?** Pulling immediately merges remote changes into your current branch. Fetch first lets you inspect what changed with `git log origin/main` before merging — safer in production workflows.
- **Why does rebase create new SHAs?** A commit SHA is a hash of its content AND its parent SHA. When you rebase, the parent changes, so the SHA changes. Same code, different identity — this breaks teammates' branches.
- **Why does `git stash` exist?** Your working tree and index are tied to the current branch. When you need to switch branches urgently (hotfix), stash temporarily shelves those changes without a commit.
- **Why is detached HEAD dangerous?** Any commits made in detached HEAD state belong to no branch. When you switch branches, Git's garbage collector can eventually delete those commits. Always attach to a branch with `git checkout -b`.
- **Why use annotated tags for releases?** Annotated tags are Git objects — they have their own SHA, author, timestamp, and message. They can be GPG-signed for supply chain verification. `git describe` only considers annotated tags.

## Easy

**1. What is the difference between `git fetch` and `git pull`?**

`git fetch` downloads changes from the remote into your remote-tracking branches (e.g., `origin/main`) but does not update your local working branch. `git pull` is `git fetch` + `git merge` — it fetches and immediately merges the remote changes into your current branch. Use `git fetch` when you want to inspect changes before merging; use `git pull --rebase` to avoid unnecessary merge commits.

**2. What is the difference between `git merge` and `git rebase`?**

`git merge` creates a merge commit that joins two branch histories — the history is preserved as-is, showing exactly when branches diverged and merged. `git rebase` re-applies your commits on top of another branch, rewriting them with new SHAs — the result is a linear history as if your work always started from the tip of the target branch. Merge is safer on shared branches; rebase is preferred for local feature branches before pushing.

**3. What is `git stash` and when do you use it?**

`git stash` temporarily saves uncommitted changes (both staged and unstaged) in a stack, restoring the working directory to `HEAD`. Use it when you need to switch branches urgently but aren't ready to commit your current work. `git stash pop` applies and removes the latest stash; `git stash apply` applies without removing. Stashes can be listed (`git stash list`), applied by name (`git stash apply stash@{2}`), or dropped (`git stash drop`).

**4. What does `git reset --hard` do and why is it dangerous?**

`git reset --hard HEAD~1` moves the current branch pointer back one commit AND discards all changes in the working directory and staging area. It's dangerous because the discarded changes are unrecoverable (unless you remember the old commit SHA and use `git reflog`). Use `git revert` instead for shared branches — it creates a new commit that undoes changes without rewriting history.

**5. What is the difference between `git cherry-pick` and `git rebase`?**

`git cherry-pick <commit>` applies a single specific commit to the current branch, creating a new commit with the same changes but a different SHA. `git rebase` replays a range of commits. Cherry-pick is used for backporting a specific bug fix to a release branch; rebase is used to keep a feature branch up to date with the target branch.

**6. What is a `.gitignore` file and what are common patterns?**

`.gitignore` tells Git which files to ignore (not track). Patterns:
```
*.log              # ignore all .log files
/dist/             # ignore dist directory at root only
**/__pycache__/    # ignore pycache anywhere
!important.log     # exception — track this file even if *.log is ignored
```
`git check-ignore -v myfile` tells you which `.gitignore` rule is causing a file to be ignored.

**7. What is a detached HEAD state and how do you recover from it?**

A detached HEAD means `HEAD` points directly to a commit SHA instead of a branch name. It happens when you `git checkout <commit>` or `git checkout v1.0.0`. Any commits made in this state are "floating" — not attached to any branch and at risk of being garbage-collected. To recover: `git checkout -b my-recovery-branch` to capture the commits on a new branch, or `git checkout main` to discard the floating commits.

**8. What is the difference between a lightweight and an annotated tag?**

A lightweight tag is just a pointer to a commit (like a branch that doesn't move): `git tag v1.0`. An annotated tag is a full Git object with its own SHA, tagger identity, timestamp, and message: `git tag -a v1.0 -m "Release 1.0"`. Annotated tags are preferred for releases because they carry metadata and can be signed (`-s`). `git describe` only considers annotated tags.

**9. How do you undo the last commit without losing the changes?**

`git reset HEAD~1` (or `git reset --soft HEAD~1`) moves the branch pointer back one commit while keeping all changes in the staging area, ready to recommit. `git reset HEAD~1` (mixed mode, the default) keeps changes in the working directory but unstages them. Both are safe for local commits not yet pushed. For commits already pushed to a shared branch, use `git revert HEAD` instead.

**10. What is `git bisect` and when is it useful?**

`git bisect` is a binary search tool that helps find which commit introduced a bug. You tell it a known-bad commit and a known-good commit; it checks out the midpoint; you test and tell it `good` or `bad`. It narrows down the range in O(log N) steps. `git bisect run ./test.sh` automates the process — the script's exit code determines good/bad.

**11. What is the difference between `git clone --depth 1` and a full clone?**

A shallow clone (`--depth 1`) downloads only the latest commit, not the full history. Build time is dramatically reduced (useful in CI). However, shallow clones can't run `git log` with full history, `git blame` may be incomplete, and `git bisect` won't work without fetching more history. For production use, `--depth 1` is appropriate in CI; avoid it for developer machines where history is needed.

**12. What is `git reflog` and when does it save you?**

`git reflog` records every position `HEAD` has been at — including commits that no longer appear in `git log` (after reset, amend, or rebase). It's the safety net after accidental `git reset --hard` or `git rebase` that rewrote commits you needed. `git reflog` shows the SHA of the previous state; `git checkout -b recovery <sha>` restores it. Reflog entries expire after 90 days by default.

---
description: Medium-difficulty interview questions for Git workflows, branching strategies, and version control.
---

```
Git Interview — Medium
├── Branching Strategies
│   ├── Git Flow — develop/release/hotfix for versioned software
│   │   └── When NOT to use: continuous deployment, small teams
│   └── Trunk-Based Development — short branches (<2 days), feature flags
│       ├── Enabling: CI quality gate, small PRs, branch by abstraction
│       └── Where used: Google, Meta, Netflix
├── History Manipulation
│   ├── Interactive rebase (pick/reword/edit/squash/fixup/drop)
│   └── git worktree — two branches checked out simultaneously
├── Debugging Tools
│   ├── git blame -L (line range) — why does this line exist?
│   └── git log -S "pattern" (pickaxe) — when was this string added/removed?
├── Standards & Enforcement
│   ├── Conventional Commits (feat/fix/docs/chore/refactor/test)
│   ├── commit-msg hook (regex enforcement)
│   ├── commitlint in CI (pre-merge check)
│   └── husky for automatic hook installation
├── Submodules
│   ├── How it works: parent stores URL + pinned commit SHA
│   ├── Pitfalls: clone --recursive, forgetting to commit pointer update
│   └── Alternatives: subtree, vendoring
├── Monorepo at Scale
│   ├── Selective CI: only build what changed (Nx, Turborepo, Bazel)
│   ├── Workspace tooling: npm/yarn/pnpm workspaces
│   ├── CODEOWNERS for per-directory review enforcement
│   └── Trunk-based dev pairs well with monorepos
└── Large Binary Files
    ├── Git LFS — pointer in repo, content in LFS server
    └── External stores — S3/GCS/Artifactory by URL + checksum
```

### First Principles

- **Why Git Flow fails at CD?** Continuous deployment requires every commit to potentially be releasable. Git Flow batches features in `develop`, creating a release queue that delays delivery. The branching overhead adds toil without benefit when you deploy multiple times per day.
- **Why feature flags enable TBD?** Incomplete code merged to main would break users. Feature flags separate deployment (code is live) from release (feature is visible). This decouples the two concerns — developers merge freely, product team controls exposure.
- **Why interactive rebase before PR?** Your commit history during development is a draft. The PR reviewer should see logical units of change, not `WIP`, `fix typo`, `fix typo 2`. `git rebase -i` lets you clean up before review without losing any actual work.
- **Why are submodules painful?** A submodule is a Git-within-Git. The parent repo doesn't track the submodule's files — only a pointer (URL + SHA). Every workflow step must account for this: `clone --recursive`, `pull --recurse-submodules`. Forgetting any of these causes stale or broken submodules.
- **Why do monorepos need affected-only CI?** In a 500-package monorepo, running all tests on every commit is prohibitive (hours of CI time). Tools like Nx and Turborepo build a dependency graph — only packages that changed or depend on changed packages are rebuilt. This is why TBD works at scale: small changes → small CI scope.

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

```
Git Interview — Hard
├── Microservices Versioning
│   ├── SemVer (MAJOR.MINOR.PATCH) per service and API
│   ├── Consumer-Driven Contract Testing (Pact) — prevent breaking changes
│   ├── Centralized artifact repository (JFrog Artifactory)
│   └── Bill of Materials (BOM) — pinned version set for a release
├── Large Team Workflow Design (100+ engineers)
│   ├── Trunk-Based Development as foundation
│   ├── Feature flags for incomplete work
│   ├── Short-lived release branches (cut from main, merge back with cherry-pick)
│   ├── CODEOWNERS for mandatory review routing
│   ├── Branch protection rules (required CI, signed commits)
│   └── Tooling: commitlint, semantic-release, renovate for dep updates
├── Git Rerere
│   ├── Reuse Recorded Resolution — remembers how you resolved a conflict
│   ├── git config rerere.enabled true
│   └── Useful in long-lived branches or repeated rebase operations
├── Git Fundamentals (Easy-level coverage in this file)
│   ├── CVCS vs DVCS
│   ├── Three states: working / staging / repository
│   ├── Core commands: init, clone, add, commit, push, pull, fetch
│   ├── Branching, merge, rebase, cherry-pick
│   └── Conflict resolution workflow
└── Advanced Concepts
    ├── Partial clone vs shallow clone
    ├── Signed commits (GPG, SSH) — SLSA supply chain
    └── Hooks: pre-commit, commit-msg, pre-push, pre-receive
```

### First Principles

- **Why SemVer for microservices?** In a distributed system, services evolve independently. Without a versioning contract, a consumer has no way to know if an upgrade is safe. SemVer provides a machine-readable signal: MAJOR = breaking, MINOR = additive, PATCH = bugfix.
- **Why contract testing over integration testing?** Integration tests require all services to be available simultaneously — expensive and slow. Pact tests each service in isolation against its consumer contracts. This scales linearly with service count, not exponentially.
- **Why rerere?** During long rebase chains or cherry-pick flows (common in release branch workflows), the same conflict appears repeatedly. Rerere eliminates the manual re-resolution for each iteration — Git remembers the resolution and applies it automatically.
- **Why branch protection + CODEOWNERS for 100 engineers?** At scale, code review discipline degrades without enforcement. CODEOWNERS ensures domain experts always review changes in their area. Required CI prevents merging broken code. Together, they encode review standards into the system, not culture.
- **Why feature flags over long branches?** Long feature branches diverge from main. The longer the branch, the more painful the merge. Feature flags allow daily merges while keeping incomplete features invisible — turning "merge day" from a multi-hour conflict resolution exercise into a normal commit.

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
# Git Interview Questions — Easy

***

**1. What is Git and why is it used?**

Git is a distributed version control system (DVCS) that tracks changes to files over time. Unlike centralized systems (like SVN), every developer has a full copy of the repository including complete history. It enables collaboration, rollback, branching, and a complete audit trail of every change. DevOps pipelines depend on Git as the source of truth that triggers CI/CD.

***

**2. What is the difference between `git init` and `git clone`?**

`git init` creates a new, empty repository in the current directory (or a specified directory). `git clone` copies an existing remote repository — including all commits, branches, and tags — to your local machine and sets up the remote tracking automatically.

```bash
git init                            # new empty repo
git init my-project                 # new repo inside my-project/

git clone https://github.com/org/repo.git         # clone from URL
git clone https://github.com/org/repo.git mydir   # clone into named dir
```

***

**3. Explain the three areas of Git: working tree, staging area (index), and repository.**

| Area | Description |
|------|-------------|
| **Working Tree** | Your local filesystem — files you see and edit |
| **Staging Area (Index)** | A preparation zone: `git add` copies changes here before they are committed |
| **Repository (.git/)** | The object database — permanent, immutable history |

```bash
# Flow
edit file.txt           # working tree
git add file.txt        # moves to staging area (index)
git commit -m "msg"     # writes index snapshot to repository as a commit object
```

`git diff` shows working tree vs index. `git diff --staged` shows index vs last commit.

***

**4. What does `git add` do? What is the difference between `git add .` and `git add -p`?**

`git add` stages changes — it copies content from the working tree into the index (staging area) in preparation for a commit.

- `git add .` — stages all changes (new files, modifications, deletions) in the current directory and below
- `git add -p` — interactively selects individual **hunks** (chunks of changes) to stage, letting you craft a precise commit from messy working tree changes

```bash
git add README.md           # stage one file
git add src/                # stage entire directory
git add .                   # stage everything
git add -p                  # hunk-by-hunk interactive staging
```

***

**5. What is a commit? What information does it contain?**

A commit is a snapshot of the staging area at a point in time, stored as an immutable object in Git's object database. Each commit contains:

- A pointer to the root **tree** object (the directory snapshot)
- The **parent commit SHA** (or two parents for a merge commit)
- **Author** name, email, and timestamp
- **Committer** name, email, and timestamp
- The **commit message**
- A **SHA-1 hash** (the commit's unique ID, derived from all the above)

```bash
git commit -m "feat: add user authentication"
git show HEAD               # see all commit fields
```

***

**6. What is `git status` and what does it show?**

`git status` shows the current state of the working tree and staging area relative to HEAD:

- Files staged for the next commit (green)
- Files modified but not staged (red)
- Files that are untracked (not in the index at all)
- The current branch name and how it relates to the upstream

```bash
git status
git status -s               # short format: M=modified, A=added, ??=untracked
```

***

**7. What is the difference between `git push` and `git pull`?**

- `git push` uploads your local commits to the remote repository. It sends new commits, moving the remote branch pointer forward.
- `git pull` downloads changes from the remote and integrates them into your local branch (fetch + merge by default, or fetch + rebase with `--rebase`).

```bash
git push origin main                # push local main to remote
git pull origin main                # fetch + merge remote main into local main
git pull --rebase origin main       # fetch + rebase instead of merge
```

***

**8. What is the difference between `git fetch` and `git pull`?**

`git fetch` downloads remote commits and updates remote-tracking refs (`origin/main`) but does **not** modify your working tree or current branch. You then decide how to integrate the changes.

`git pull` is `git fetch` followed immediately by `git merge` (or `git rebase`) into the current branch.

```bash
git fetch origin            # safe: download but don't integrate
git log origin/main         # inspect what changed
git merge origin/main       # integrate when ready

# vs
git pull origin main        # fetch + merge in one command
```

> [!TIP]
> In automated pipelines and when you want to inspect changes before integrating, prefer `git fetch` + `git merge`/`git rebase` explicitly over `git pull`.

***

**9. How do you create and switch to a new branch?**

```bash
# Create a branch (does not switch)
git branch feature/login

# Switch to an existing branch
git checkout feature/login
git switch feature/login            # modern syntax (Git 2.23+)

# Create and switch in one command
git checkout -b feature/login
git switch -c feature/login         # modern syntax

# Create branch tracking a remote branch
git checkout -b feature/login origin/feature/login
```

***

**10. What is a merge conflict and how do you resolve it?**

A merge conflict occurs when two branches have modified the same lines of the same file differently. Git cannot determine which change to keep and marks the conflict in the file.

```
<<<<<<< HEAD
current branch content
=======
incoming branch content
>>>>>>> feature/login
```

Resolution steps:
1. `git status` — identify all conflicted files
2. Open each conflicted file, edit to keep the correct content, remove all conflict markers
3. `git add <file>` — mark each file as resolved
4. `git commit` (for merge) or `git rebase --continue` (for rebase)

```bash
git merge feature/login         # conflict occurs
git status                      # see which files conflict
# edit conflicted files
git add src/auth.py
git commit                      # complete the merge
```

***

**11. What is `.gitignore` and how does it work?**

`.gitignore` is a plain text file listing patterns of paths that Git should not track. Untracked files matching the patterns are invisible to `git status` and `git add`.

```gitignore
# Dependencies
node_modules/
vendor/

# Build output
dist/
*.class
*.pyc

# Secrets and env
.env
.env.local
*.pem

# OS artifacts
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/

# Logs
*.log
logs/
```

Rules:
- Patterns are matched relative to the `.gitignore` file's location
- A leading `/` anchors the pattern to the directory
- A trailing `/` matches only directories
- `!` negates a pattern (re-include something previously ignored)
- Already-tracked files are **not** ignored even if added to `.gitignore` — use `git rm --cached`

***

**12. What is a remote repository? What is `origin`?**

A remote is a named reference to a repository hosted elsewhere (GitHub, GitLab, Bitbucket, a server). `origin` is the conventional default name given to the remote you cloned from.

```bash
git remote -v                           # list remotes and their URLs
git remote add origin <url>             # add a remote named origin
git remote add upstream <url>           # common for forks: the original source
git remote set-url origin <new-url>     # change the URL
```

Remote-tracking refs like `origin/main` are local read-only copies of what you last fetched from the remote.

***

**13. What is the difference between a local branch and a remote-tracking branch?**

- **Local branch** (`main`, `feature/login`): exists in your `.git/refs/heads/`. You check it out and commit to it.
- **Remote-tracking branch** (`origin/main`, `origin/feature/login`): a read-only snapshot of the remote branch, updated by `git fetch`. You cannot commit to it directly.

```bash
git branch -r                           # list remote-tracking branches
git branch -a                           # list local + remote-tracking

# Create a local branch from a remote-tracking one
git checkout -b feature/login origin/feature/login
```

***

**14. What is a Git tag? What is the difference between a lightweight tag and an annotated tag?**

A tag is a named pointer to a specific commit, commonly used to mark release versions.

- **Lightweight tag**: just a ref pointing to a commit — no additional metadata. Like a branch that never moves.
- **Annotated tag**: a full Git object with tagger name, email, date, message, and optionally a GPG signature. Recommended for releases.

```bash
git tag v1.0.0                              # lightweight tag at HEAD
git tag -a v1.0.0 -m "Release v1.0.0"      # annotated tag at HEAD
git tag -a v1.0.0 abc1234 -m "Release"     # annotated tag at specific commit
git tag -l                                  # list all tags
git push origin --tags                      # push all tags to remote
git push origin v1.0.0                      # push a specific tag
```

***

**15. What is `HEAD` in Git?**

`HEAD` is a pointer to the currently checked-out commit or branch. It represents "where you are right now" in repository history.

- **Attached HEAD**: `HEAD` points to a branch ref (`ref: refs/heads/main`). Committing advances the branch.
- **Detached HEAD**: `HEAD` points directly to a commit SHA. Commits are made but belong to no branch — they'll be garbage collected unless you create a branch.

```bash
cat .git/HEAD               # see what HEAD points to
git log -1 HEAD             # show current commit
git checkout main           # reattach HEAD to main branch
git checkout abc1234        # detach HEAD to a specific commit
```

***

**16. How do you undo the last commit without losing your changes?**

```bash
# Undo last commit, keep changes staged (ready to re-commit)
git reset --soft HEAD~1

# Undo last commit, keep changes in working tree (unstaged)
git reset --mixed HEAD~1    # or just: git reset HEAD~1

# Undo last commit AND discard all changes (destructive)
git reset --hard HEAD~1
```

> [!CAUTION]
> Never use `git reset` to undo commits that have already been pushed to a shared branch. Use `git revert` instead, which creates a new commit that reverses the changes — safe for shared history.

```bash
git revert HEAD             # create a new commit that undoes the last commit
git revert abc1234          # create a new commit that undoes a specific commit
```

***

**17. What is `git stash` and when would you use it?**

`git stash` temporarily saves your uncommitted changes (both staged and unstaged) to an internal stack and restores a clean working directory. Use it when you need to switch context quickly without committing half-done work.

```bash
git stash                           # save current changes
git stash push -m "WIP: login form" # save with a description
git stash list                      # see all stashed items
git stash pop                       # apply most recent stash and remove it
git stash apply stash@{1}           # apply a specific stash (keep it in list)
git stash drop                      # delete most recent stash
git stash clear                     # delete all stashes
```

**Common scenario:** You're mid-feature when a critical bug comes in on `main`. Stash your work, switch to main, fix and push the bug, come back, and `git stash pop`.
# Git Interview Questions — Medium

***

**1. Explain Git's object model: blob, tree, commit, tag.**

Git is a content-addressable store. Every object is identified by the SHA-1 hash of its content.

| Object | Stores | Key Property |
|--------|--------|-------------|
| **Blob** | Raw file content | No filename, no mode — content only |
| **Tree** | Directory listing: `(mode, name, sha)` tuples | Snapshot of a directory |
| **Commit** | Tree SHA + parent SHA(s) + author + message | A point-in-time snapshot |
| **Tag** | Pointer + tagger metadata + optional signature | Annotated alias for an object |

```bash
# Inspect any object
git cat-file -t <sha>         # type: blob, tree, commit, tag
git cat-file -p HEAD          # content of current commit
git cat-file -p HEAD:src/     # content of a tree
git cat-file -p HEAD:main.py  # content of a blob
```

Identical content always produces the same SHA-1 — Git deduplicates storage automatically. Two commits touching the same unchanged file share that file's blob object.

***

**2. What is `git rebase -i` and how do you use it to clean up commits before a PR?**

`git rebase -i` (interactive rebase) opens an editor showing the last N commits as a list of commands. You reorder, combine, edit, or drop commits before they become part of the shared history.

```bash
git rebase -i HEAD~5          # edit the last 5 commits
```

Editor commands:
```
pick   a1b2c3 feat: add auth module
squash b4d5e6 WIP
fixup  c7d8e9 fix typo
reword d1e2f3 add tests       # will prompt you for a new message
drop   e4f5g6 debug logging   # remove entirely
```

Workflow for PR cleanup:
1. `git rebase -i HEAD~<N>` where N is the number of commits on your feature branch
2. Mark `squash` or `fixup` on WIP commits, `reword` on poorly-named ones, `drop` on debug-only commits
3. Save and exit — Git replays the commits
4. Force-push the clean branch: `git push --force-with-lease origin feature/my-feature`

> [!CAUTION]
> Interactive rebase rewrites history. Only use it on commits that **haven't been pushed**, or on your own feature branch where you control the force-push. Never on `main`.

***

**3. What is `git cherry-pick` and when would you use it?**

`git cherry-pick <sha>` applies the diff introduced by a specific commit to the current branch, creating a new commit with a new SHA.

```bash
git cherry-pick abc1234                    # apply a single commit
git cherry-pick abc1234^..def5678          # apply a range (inclusive)
git cherry-pick --no-commit abc1234        # apply without committing (stage only)
git cherry-pick -x abc1234                 # append "cherry-picked from" to message
```

**Use cases:**
- A bug fix was committed to `main` and you need it on a `release/1.x` branch
- A commit was made to the wrong branch — cherry-pick it to the correct one, then revert or drop the original
- A feature in an abandoned branch has one useful commit you want to salvage

> [!IMPORTANT]
> Cherry-pick copies the diff, not the commit itself. If the original commit is later included via a merge, Git usually handles it cleanly, but duplicate content can cause conflicts in some cases. Prefer full merges or rebases when moving substantial amounts of work.

***

**4. How does `git bisect` work? Walk through an example.**

`git bisect` performs a binary search through commit history to find the first commit that introduced a regression. With N commits in the range, it takes at most `log₂(N)` steps.

```bash
# Manual bisect session
git bisect start
git bisect bad HEAD                        # HEAD is currently broken
git bisect good v2.0.0                     # known-good tag

# Git checks out the midpoint commit
./run-tests.sh
git bisect bad                             # midpoint is also broken

# Git checks out the next midpoint
./run-tests.sh
git bisect good                            # this one works

# ... repeat until Git announces:
# abc1234 is the first bad commit

git bisect reset                           # return to original HEAD
```

**Automated bisect:**
```bash
git bisect start
git bisect bad HEAD
git bisect good v2.0.0
git bisect run ./ci/regression-test.sh    # exits 0=good, non-zero=bad, 125=skip

git bisect reset
```

The script should handle build failures by exiting 125 (skip):
```bash
#!/bin/bash
make build 2>/dev/null || exit 125        # can't test if build fails
./test.sh
```

***

**5. What is the reflog and how do you use it for disaster recovery?**

`git reflog` records every position `HEAD` (and branch tips) has been at for the last 90 days, even if those commits are no longer reachable from any branch.

```bash
git reflog
# 7a3c91f HEAD@{0}: reset: moving to HEAD~3
# b4d82e1 HEAD@{1}: commit: add payment module
# 9f1a023 HEAD@{2}: commit: fix checkout bug
# ...

git show b4d82e1                           # verify it's the commit you want
git branch recovered b4d82e1              # create a branch from the lost commit
git reset --hard HEAD@{1}                 # reset current branch to a previous position
```

**Scenarios where reflog saves you:**
- `git reset --hard` went too far
- Deleted a branch that wasn't merged
- Detached HEAD commits that were never branched
- A bad `git rebase` that you want to undo

> [!IMPORTANT]
> Reflog is **local only** — it is never pushed or fetched. If a colleague does the damage, they need to use their own reflog. Also, `git gc` prunes unreachable objects after the reflog expiry (90 days reachable, 30 days unreachable by default).

***

**6. Compare GitFlow vs trunk-based development. Which would you choose and why?**

| Factor | GitFlow | Trunk-Based |
|--------|---------|-------------|
| Branch lifespan | Weeks/months | < 2 days |
| Merge conflict risk | High | Low |
| Integration frequency | Low | Daily+ |
| Release mechanism | Release branch | Feature flags + tags |
| CI complexity | High (multiple branch pipelines) | Low (single pipeline) |
| Best for | Versioned software (mobile, firmware) | SaaS, high-velocity web |

**GitFlow** makes sense when: you have fixed release cadences (App Store releases, quarterly deploys), need strict release stabilization, or operate in a regulated environment requiring release sign-off.

**Trunk-Based Development** makes sense when: you deploy continuously, have a mature test suite, and can use feature flags for incomplete work. It forces true Continuous Integration — code is integrated daily, not at the end of a feature.

At scale (Google, Meta), trunk-based development combined with feature flags is the standard. GitFlow "merge Wednesdays" are a well-known scaling failure mode.

***

**7. What are Git hooks and how do you share them with your team?**

Hooks are scripts in `.git/hooks/` that execute at lifecycle events. By default, `.git/` is not tracked, so hooks are not shared.

**Sharing strategies:**

Option A — `core.hooksPath` (recommended):
```bash
mkdir .githooks
cp my-hooks/* .githooks/
git config core.hooksPath .githooks      # local only
# Or automate via setup script that runs after clone
```

Option B — `pre-commit` framework:
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: detect-private-key
  - repo: local
    hooks:
      - id: conventional-commits
        name: Conventional Commits
        entry: .githooks/commit-msg
        language: script
        stages: [commit-msg]
```

```bash
pip install pre-commit
pre-commit install            # installs hooks into .git/hooks/
```

**Common hooks:**
- `pre-commit`: lint, format, secret scanning
- `commit-msg`: enforce conventional commits format
- `pre-push`: run tests before pushing (gate quality at the source)

***

**8. What is the difference between a monorepo and polyrepo strategy? What tooling does monorepo require?**

| | Polyrepo | Monorepo |
|-|----------|---------|
| Repo structure | One repo per service/library | All services in one repo |
| Cross-service refactors | Painful (multiple PRs, sequencing) | Atomic (single commit) |
| CI | Independent per repo | Must be change-aware (affected-only) |
| Dependency management | Explicit versioning between repos | Shared (risk of implicit coupling) |
| Clone size | Small | Large (mitigated by sparse-checkout) |
| Tooling required | Minimal | Bazel, Nx, Turborepo, or Pants |

**Monorepo CI pattern — affected-only builds:**
```bash
# Find which top-level service directories changed vs main
CHANGED=$(git diff --name-only origin/main...HEAD | cut -d/ -f1-2 | sort -u)

for dir in $CHANGED; do
  [ -f "$dir/Makefile" ] && make -C "$dir" test
done
```

**Tooling:**
- **Bazel**: hermetic builds with fine-grained dependency graph (Google, DropBox)
- **Nx**: JS/TS `nx affected:test` only tests projects that transitively depend on changed files
- **Turborepo**: similar to Nx, with remote caching

***

**9. What is commit signing and why does it matter for supply chain security?**

Without signing, the `user.name` and `user.email` in a commit are just strings — anyone can impersonate anyone. Commit signing uses GPG or SSH keys to cryptographically prove that the commit was made by the holder of a private key.

```bash
# Setup GPG signing
gpg --full-generate-key
git config --global user.signingkey <KEY_ID>
git config --global commit.gpgsign true      # sign all commits
git verify-commit <sha>
git log --show-signature

# SSH signing (simpler, Git 2.34+)
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_ed25519.pub
```

**Supply chain context:** SLSA (Supply-chain Levels for Software Artifacts) Level 2 requires that build inputs are authenticated. Signed commits are evidence that only authorized identities contributed code. Combined with protected branch rules ("require signed commits"), you create a verifiable chain from developer → commit → build artifact.

GitHub shows a "Verified" badge on signed commits. Enforce signing via branch protection: Settings → Branches → Require signed commits.

***

**10. How do you handle large binary files in Git? What is Git LFS?**

Git stores a complete copy of every version of every file. Binary files (images, videos, compiled artifacts) don't delta-compress well, causing rapid repository bloat.

**Git LFS (Large File Storage):**
- LFS stores large files on a separate LFS server (GitHub/GitLab maintain one)
- In the repo, a small text pointer replaces the actual file content
- On checkout, the pointer is resolved and the actual file is downloaded

```bash
git lfs install                             # one-time LFS setup
git lfs track "*.psd"                       # track PSD files with LFS
git lfs track "*.bin"
git add .gitattributes                      # commit the tracking config
git add design.psd
git commit -m "add design assets"
git push origin main                        # LFS files uploaded to LFS server
git lfs ls-files                            # list LFS-tracked files
```

**Alternative for removing large files from history:**
```bash
# git-filter-repo (modern, faster than BFG)
pip install git-filter-repo
git filter-repo --path path/to/large.bin --invert-paths

# After rewriting history, force push and notify team
git push --force origin main
```

***

**11. What is `git submodule` vs `git subtree`? When would you use each?**

Both allow embedding one repo inside another.

| | Submodule | Subtree |
|-|-----------|---------|
| Mechanism | Pointer (`.gitmodules` + detached checkout) | Code merged into repo history |
| Clone behavior | Submodule dirs empty until `--recurse-submodules` | Transparent — just files |
| Upstream contribution | Easy | Via `git subtree push` |
| History isolation | Separate history | Merged into parent history |
| Complexity | High (common footguns) | Lower for consumers |

```bash
# Submodule
git submodule add https://github.com/org/lib.git vendor/lib
git clone --recurse-submodules <url>
git submodule update --init --recursive

# Subtree
git subtree add --prefix=vendor/lib https://github.com/org/lib.git main --squash
git subtree pull --prefix=vendor/lib https://github.com/org/lib.git main --squash
```

**Use submodule when:** the embedded repo needs to be a fully independent project that the team also develops separately. The pointer model is explicit.

**Use subtree when:** you want to embed third-party code without the operational burden of submodule init/update workflows. Better for libraries you rarely update and don't contribute back to.

***

**12. How do you recover commits after an accidental `git reset --hard`?**

```bash
# Step 1: Check reflog — HEAD movements are recorded for 90 days
git reflog
# 7a3c91f HEAD@{0}: reset: moving to HEAD~3   <- where you are now
# b4d82e1 HEAD@{1}: commit: add payment service  <- what you lost

# Step 2: Verify the commit you want to recover
git show b4d82e1

# Step 3: Recover
# Option A: Create a branch pointing to the lost commit
git branch recover/payments b4d82e1

# Option B: Reset current branch back to it
git reset --hard b4d82e1
```

If the commit isn't in reflog (old or GC'd):
```bash
git fsck --lost-found
# Objects are written to .git/lost-found/commit/
ls .git/lost-found/commit/
git show .git/lost-found/commit/<sha>
```

***

**13. What is `--force-with-lease` and why is it safer than `--force`?**

`git push --force` overwrites the remote branch regardless of what's there. If a teammate pushed commits since your last fetch, their work is silently lost.

`git push --force-with-lease` first checks that the remote tip matches what you last fetched. If the remote has moved (someone else pushed), the force-push is rejected — preventing accidental data loss.

```bash
git push --force-with-lease origin feature/my-feature   # safe
git push --force origin feature/my-feature              # dangerous

# --force-with-lease with explicit SHA for maximum safety
git push --force-with-lease=feature/my-feature:<sha> origin feature/my-feature
```

**Always use `--force-with-lease`** when force-pushing is genuinely necessary (after interactive rebase on your own feature branch). Never force-push to `main` or shared branches.

***

**14. What is a merge strategy and what are the common ones?**

A merge strategy determines how Git combines histories. Pass with `-s <strategy>`.

| Strategy | Description | Use Case |
|----------|-------------|----------|
| `ort` | Default (since Git 2.34). Handles renames, better than `recursive` | Standard merges |
| `recursive` | Old default. Three-way merge | Standard merges (older Git) |
| `resolve` | Simpler three-way, no rename detection | Legacy |
| `octopus` | Merges more than two branches | Merging many feature branches at once |
| `ours` | Result is always current branch — incoming changes discarded | Retiring a branch without its changes |
| `subtree` | Like recursive but adjusts tree paths | Merging subtree-based repos |

```bash
git merge -s ours obsolete-branch           # merge branch, but keep only our code
git merge -X ours feature/x                 # strategy option: prefer ours on conflict
git merge -X theirs feature/x              # strategy option: prefer theirs on conflict
git merge -X ignore-space-change feature/x  # ignore whitespace in conflict detection
```

***

**15. How do you enforce a commit message format across a team?**

**Local enforcement via `commit-msg` hook:**
```bash
# .githooks/commit-msg
#!/bin/sh
pattern="^(feat|fix|chore|docs|style|refactor|perf|test|ci|build|revert)(\(.+\))?: .{1,72}"
if ! grep -qE "$pattern" "$1"; then
  echo "ERROR: Commit message must follow Conventional Commits:"
  echo "  <type>(<scope>): <description>"
  echo "  Types: feat, fix, chore, docs, style, refactor, perf, test, ci, build, revert"
  exit 1
fi
```

**Server-side enforcement via pre-receive hook** (GitHub: rulesets; GitLab: push rules):
```bash
# GitHub Actions check on PR
- name: Check commit messages
  run: |
    git log origin/main..HEAD --pretty=format:"%s" | \
      grep -vE "^(feat|fix|chore|docs)(\(.+\))?: " && exit 1 || true
```

**Tool-based:** `commitlint` (npm) integrates with `husky` for JavaScript projects.

```bash
npm install --save-dev @commitlint/cli @commitlint/config-conventional husky
npx husky add .husky/commit-msg 'npx --no -- commitlint --edit "$1"'
```
