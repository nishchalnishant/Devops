# Git — Conceptual Notes

## Git Internals: The Content-Addressable Filesystem

Git stores everything as objects in `.git/objects/`. Every object is identified by the SHA-1 hash of its content. The four object types:

| Object | Description |
|--------|-------------|
| **Blob** | Raw file content — no filename, no metadata |
| **Tree** | Directory snapshot — maps names to blob/tree SHA-1s |
| **Commit** | Pointer to a tree + parent commit(s) + author/message |
| **Tag** | Annotated pointer to any object (usually a commit) |

### The DAG (Directed Acyclic Graph)

Commits form a DAG — each commit points to its parent(s). Merges create commits with two parents. This graph is immutable: once written, objects never change. "Rewriting history" means creating new objects and moving refs.

### Refs

Refs are plain text files under `.git/refs/` containing a 40-char SHA-1. Branches, tags, and remote-tracking refs are all refs.

```
.git/
  HEAD              <- pointer to current branch ref (or a SHA-1 in detached state)
  refs/
    heads/main      <- points to latest commit on main
    remotes/origin/main
  ORIG_HEAD         <- set before risky ops (merge, rebase, reset)
  MERGE_HEAD        <- the commit being merged in
```

`HEAD` is a symbolic ref — it normally points to a branch ref, which points to a commit. In detached HEAD state, `HEAD` points directly to a commit SHA-1.

### Pack Files

Loose objects are eventually packed into `.git/objects/pack/` using delta compression. `git gc` triggers this. Large repos benefit significantly from pack files.

---

## Staging Area (Index)

The index (`.git/index`) is a binary file representing the next commit's tree. It is the staging area between the working tree and the object database.

```
Working Tree  --git add-->  Index  --git commit-->  Object DB
```

`git diff` compares working tree vs index. `git diff --staged` compares index vs HEAD.

---

## Branching Strategies

### Trunk-Based Development (TBD)

All engineers commit to a single branch (`main`/`trunk`) at least daily. Short-lived feature branches (< 2 days) are allowed but must integrate back fast.

- **Pros:** No long-lived divergence, true continuous integration, fast feedback, eliminates "merge Wednesdays"
- **Cons:** Requires feature flags for incomplete features, strong test discipline required
- **Where used:** Google, Meta, Amazon — any high-velocity org

Feature flags decouple **deployment** (code goes to prod) from **release** (feature turns on for users). Incomplete features ship behind a flag, fully integrated with main.

### GitFlow

Long-lived branches: `main`, `develop`, `release/*`, `hotfix/*`, `feature/*`.

```
main ────────────────────────────────────> (production)
        ↑ merge                  ↑ merge
develop ──────────────────────────────────>
        ↑                  ↑
  feature/x          release/1.2
```

- **Pros:** Clear structure, supports scheduled releases
- **Cons:** Huge merge conflicts, slow integration, complex branch management
- **Where used:** Projects with fixed release cycles (mobile apps, firmware)

### GitHub Flow

Simplified: `main` is always deployable. Create a feature branch, open a PR, merge to main, deploy.

```
main ──────────────────────────────────────>
       ↑ merged via PR
feature/my-feature ──────────────────────>
```

- **Pros:** Simple, fast, good for web apps
- **Cons:** No staging or release branch concept built in

### Comparison Table

| Factor | Trunk-Based | GitFlow | GitHub Flow |
|--------|-------------|---------|-------------|
| Branch lifespan | < 2 days | Weeks/months | Days |
| Merge conflict risk | Low | High | Medium |
| Release cadence | Continuous | Scheduled | Continuous |
| Feature flags needed | Yes | No | Sometimes |
| CI complexity | Low | High | Low |

---

## Merge vs Rebase vs Squash

### Merge

Creates a new merge commit with two parents. Preserves full history.

```bash
git checkout main
git merge feature/x
# Creates: M (merge commit) with parents C3 and C5
```

```
main:    A──B──C──────M
                \    /
feature:         D──E
```

Use merge when: preserving context of a feature branch matters, in public/shared branches.

### Rebase

Replays commits from one branch on top of another. Rewrites commit SHAs. Creates linear history.

```bash
git checkout feature/x
git rebase main
# Replays D, E on top of C — creates D', E' with new SHAs
```

```
Before:  main: A──B──C
         feat: A──B──D──E

After:   main: A──B──C
         feat: A──B──C──D'──E'
```

**Golden rule:** Never rebase commits that have been pushed to a shared branch. It rewrites history that others may have based work on.

### Squash

Combines multiple commits into one before merging. Keeps `main` history clean.

```bash
git rebase -i HEAD~5   # interactive squash
# Or during merge:
git merge --squash feature/x && git commit
```

Use squash when: the feature branch has many WIP/fixup commits that are noise in the main history.

### Decision Matrix

| Scenario | Strategy |
|----------|----------|
| Local cleanup before PR | Rebase + squash |
| Merging a short-lived feature | Squash merge |
| Merging a long-lived release branch | Merge (preserve history) |
| Syncing feature branch with main | Rebase (local only) |
| Public shared branch update | Merge |

---

## Conflict Resolution

A conflict occurs when the same lines are modified differently in two branches being merged/rebased.

Git marks conflicts with:
```
<<<<<<< HEAD
current branch content
=======
incoming branch content
>>>>>>> feature/x
```

### Resolution Steps

1. `git status` — identify conflicted files
2. Edit each file: choose/combine the content, remove markers
3. `git add <file>` — mark as resolved
4. `git commit` (merge) or `git rebase --continue` (rebase)

### Conflict Tools

```bash
git mergetool              # open configured 3-way merge tool
git checkout --ours <file> # take current branch version
git checkout --theirs <file> # take incoming version
git log --merge            # show commits causing conflict
git diff                   # see current diffs
git merge --abort          # bail out of merge
git rebase --abort         # bail out of rebase
```

---

## Git Hooks

Hooks are scripts in `.git/hooks/` executed at specific lifecycle points. Not tracked by git by default — use a tool like `pre-commit` or store hooks in the repo and symlink.

| Hook | Trigger | Common Use |
|------|---------|------------|
| `pre-commit` | Before commit is created | Lint, format, secret scan |
| `commit-msg` | After commit message is written | Enforce message format |
| `pre-push` | Before push to remote | Run tests |
| `post-merge` | After merge completes | Install dependencies |
| `pre-rebase` | Before rebase starts | Safety checks |
| `post-checkout` | After branch switch | Environment setup |

```bash
# Example pre-commit hook
#!/bin/sh
npm run lint || exit 1
```

Hooks must be executable: `chmod +x .git/hooks/pre-commit`

Shared hooks: store in `.githooks/`, then `git config core.hooksPath .githooks`

---

## Submodules

Submodules embed one git repo inside another. The parent repo stores a pointer (commit SHA) to the submodule repo.

```bash
git submodule add https://github.com/org/lib.git vendor/lib
# Creates .gitmodules and adds submodule entry

git submodule update --init --recursive  # clone submodules after cloning parent
git submodule update --remote            # update to latest upstream commit
```

**Gotchas:**
- `git clone` does not clone submodules by default — use `--recurse-submodules`
- Submodule is pinned to a specific commit; updates must be explicitly committed in parent
- Detached HEAD inside submodule working directory is normal

---

## Subtrees

Git subtrees merge another repo's history directly into a subdirectory. No separate `.gitmodules` — the code is just part of the repo.

```bash
# Add a subtree
git subtree add --prefix=vendor/lib https://github.com/org/lib.git main --squash

# Pull upstream updates
git subtree pull --prefix=vendor/lib https://github.com/org/lib.git main --squash

# Push changes back upstream
git subtree push --prefix=vendor/lib https://github.com/org/lib.git main
```

| | Submodule | Subtree |
|-|-----------|---------|
| Embedded history | No (pointer only) | Yes |
| Clone complexity | High (need `--recurse`) | Low |
| Upstream contribution | Easy | Possible via `subtree push` |
| Repo size | Smaller | Larger |

---

## Signed Commits and GPG

Signed commits prove authorship. GitHub shows a "Verified" badge for signed commits.

```bash
# Generate a GPG key
gpg --full-generate-key

# List keys
gpg --list-secret-keys --keyid-format LONG

# Configure git to use key
git config --global user.signingkey <KEY_ID>
git config --global commit.gpgsign true

# Sign a commit manually
git commit -S -m "signed commit"

# Sign a tag
git tag -s v1.0.0 -m "release v1.0.0"

# Verify a commit
git verify-commit <sha>
git log --show-signature
```

Add your GPG public key to GitHub: Settings > SSH and GPG keys > New GPG key.

SSH signing (Git 2.34+) is an alternative to GPG:
```bash
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_ed25519.pub
```

---

## Monorepo vs Polyrepo

| Strategy | Pros | Cons |
|----------|------|------|
| **Polyrepo** | Team autonomy, smaller repos, independent versioning | Cross-service refactors are painful, dependency hell, duplicated tooling |
| **Monorepo** | Atomic cross-service commits, shared tooling, unified CI standards | Requires tooling (Bazel/Nx/Turborepo), slow naive CI, large clone size |

### Monorepo Tooling

- **Bazel:** Google's build system. Understands dependency graph — only builds/tests what changed.
- **Nx / Turborepo:** JS/TS ecosystem monorepo tools with affected-command support.
- **Sparse Checkout:** `git sparse-checkout` lets engineers clone only the directories they need from a 500GB monorepo.

```bash
git clone --no-checkout https://github.com/org/monorepo.git
cd monorepo
git sparse-checkout init --cone
git sparse-checkout set services/api services/worker
git checkout main
```

---

## Reflog: Git's Safety Net

The reflog records every movement of HEAD and branch tips for 90 days (default). It is local-only and not pushed.

```bash
git reflog                     # show HEAD movement history
git reflog show feature/x      # show branch tip history
git checkout HEAD@{3}          # go to where HEAD was 3 moves ago
git branch recover HEAD@{5}    # create branch from old position
```

Lost commits are recoverable via reflog as long as they haven't been garbage collected.
