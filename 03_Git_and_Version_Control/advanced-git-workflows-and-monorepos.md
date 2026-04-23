# Advanced Git Workflows & Monorepos (7 YOE)

At the senior level, Git is more than `add`, `commit`, and `push`. It is about managing the **velocity** of 100+ engineers without causing merge-conflict hell and ensuring every commit is a deployable unit.

---

## 1. Trunk-Based Development (TBD) vs. GitFlow

Most junior teams use GitFlow (Long-lived `develop`, `release`, and `production` branches). **7 YOE Senior Engineers in High-Velocity companies (Google, Meta, Amazon) use Trunk-Based Development.**

### Why Trunk-Based Development Wins
- **Continuous Integration (The real kind):** In GitFlow, code in a `feature-branch` isn't integrated with other features for weeks. In TBD, features are merged to `main` (the trunk) daily.
- **Merge Conflict Reduction:** Small, frequent merges are trivial to resolve. Massive "Merge Wednesdays" from GitFlow are eliminated.
- **Dependency on Feature Flags:** If you merge a half-finished feature to `main`, you hide it behind a **Feature Flag**. This decouples **Deployment** (moving code to prod) from **Release** (turning the feature on for users).

---

## 2. Monorepo vs. Polyrepo (The Great Debate)

| Strategy | Definition | Senior Perspective (7 YOE) |
|---|---|---|
| **Polyrepo** | One Git repo per microservice. | Good for team autonomy, but terrible for cross-service refactors. Causes "Dependency Hell" where Service A needs v2 of a library but Service B is stuck on v1. |
| **Monorepo** | One massive Git repo for the entire company. | Hard to manage (requires tools like Bazel/Nx/Turborepo). However, it ensures atomic commits across services and centralizes all tooling/CI standards. |

### Monorepo Tooling at Scale
- **Bazel (Google):** A build system that only builds and tests what changed (incremental builds). If you change `service-a`, Bazel knows it doesn't need to retest `service-b`.
- **Sparse Checkout:** When the repo is 500GB, engineers use `git sparse-checkout` to only download the folders they are actually working on.

---

## 3. Advanced Git Mastery: Solving "The Impossible"

### Interactive Rebase (`git rebase -i`)
Never push 10 "wip" commits to a PR. Use interactive rebase to **squash** them into a single, clean, semantic commit before requesting a review.
```bash
# Clean up the last 5 commits
git rebase -i HEAD~5
# Mark commits as 'pick', 'squash', or 'fixup'
```

### The "Detached HEAD" Rescue
If you end up in a detached HEAD state, don't panic. You are just on a commit without a branch name.
```bash
# Save your work to a new branch
git checkout -b rescue-branch
```

### History Cleaning (`git filter-repo`)
If a developer accidentally pushes a 1GB database file or a secret into the history, `git rm` is not enough—it's still in the `.git` folder.
- **Tool:** `git filter-repo` (the modern replacement for BFG Repo-Cleaner). It rewrites the entire history to purge the file permanently from all past commits.

---

## 4. Git Internals: The Content Addressable Filesystem

If a junior asks "How does Git work?", a 7 YOE engineer explains the underlying objects:
1. **Blobs:** The content of your files.
2. **Trees:** The directory structure (pointers to blobs or other trees).
3. **Commits:** A pointer to a tree, plus a message and a parent pointer.
4. **Refs:** Just a text file containing a 40-character SHA-1 (Branches are just moving pointers).

**Why this matters:** Understanding that "Everything in Git is immutable" allows you to recover almost anything using `git reflog`—the "undo history" of every move your HEAD has made in the last 90 days.
