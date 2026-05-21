# Git & Version Control

```
Git & Version Control
├── Core Model
│   ├── Content-addressable filesystem (SHA-1 keyed object store)
│   ├── DAG (Directed Acyclic Graph) — commits point to parents
│   └── Three areas: working directory → staging (index) → repository (.git)
├── Four Object Types
│   ├── Blob — raw file content
│   ├── Tree — directory snapshot (maps names → blobs/trees)
│   ├── Commit — tree + parent SHA + author + message
│   └── Tag — annotated pointer to a commit
├── Branching & Merging
│   ├── Branch = 40-byte file containing a commit SHA (cheap!)
│   ├── Merge — joins two histories (preserves full graph)
│   ├── Rebase — re-applies commits on new base (linear, rewrites SHAs)
│   └── Fast-forward — pointer moves, no new commit created
├── Git at Scale
│   ├── Monorepo vs Polyrepo — trade-offs of co-location vs autonomy
│   ├── Trunk-Based Development — merge to main daily + feature flags
│   ├── GitFlow — develop/release/hotfix branches for versioned releases
│   └── Partial clone, sparse checkout — scale for large repos
├── Power User Commands
│   ├── git bisect — binary search for regression
│   ├── git reflog — safety net for all HEAD movements
│   ├── git stash — temporary work save
│   └── git worktree — multiple working dirs from one repo
├── Troubleshooting
│   ├── Detached HEAD recovery
│   ├── Force-push disaster recovery
│   └── Large file removal (filter-repo / BFG)
└── Best Practices
    ├── Conventional Commits format
    ├── Signed commits (GPG / SSH) for supply chain
    └── Hooks (pre-commit, commit-msg, pre-push)
```

## First Principles

- **Why track changes at all?** Software evolves — you need to know what changed, when, and why. Without history, bugs are impossible to bisect and rollbacks require guesswork.
- **Why content-addressing?** Hash the content, not the filename. If two files are identical, they produce the same SHA — zero duplication. If anything changes, the hash changes — tamper-evident by construction.
- **Why a DAG, not a linear list?** Multiple people work in parallel on branches. A DAG naturally models concurrent histories that later merge back together. Linear lists cannot represent divergence.
- **Why three areas (working/staging/repo)?** Granular control. You want to commit only part of your edits, or review a "draft" before making it permanent. The staging area is the draft.
- **Why branches are cheap?** A branch is a 41-byte file. Creating a branch costs O(1). In older VCS (SVN), branching copied the entire directory — O(n). Git's model enables feature-branch workflows at no cost.
- **Why rebase is dangerous on shared branches?** Rebase rewrites commit SHAs. If a teammate already has commit D and you rebase it to D', their branch diverges from yours. The fix is force-push, which risks data loss for them.

Git is not just a tool for saving code; it is a **Directed Acyclic Graph (DAG)** that serves as the "ledger" of all engineering decisions. In DevOps, Git is the trigger for every CI/CD pipeline.

#### 1. The Core Philosophy
Git is a **content-addressable filesystem**. Every file and every change is stored as an object identified by its SHA-1 hash. If you change a single comma, the hash changes, ensuring perfect data integrity.

#### 2. The Three States
Understanding Git requires mastering the movement of data between these three areas:
*   **Working Directory:** Where you edit your files physically.
*   **Staging Area (Index):** A "draft" area where you prepare the next snapshot.
*   **Repository (.git):** Where Git stores the compressed snapshots (commits) permanently.

#### 3. Branching & Merging
Branches in Git are incredibly "cheap"—they are just 40-character files containing a pointer to a commit.
*   **Merge:** Combines two histories. It's safe but can create messy "railroad tracks" in your history.
*   **Rebase:** Rewrites history to make it linear. It looks cleaner but can be dangerous if used on shared branches.

#### 4. Git Internals (The Objects)
Every `.git` folder contains four types of objects:
1.  **Blobs:** The raw data of your files.
2.  **Trees:** The "folders" that link filenames to Blobs.
3.  **Commits:** The snapshots that point to a Tree and a Parent commit.
4.  **Tags:** Pointers to specific commits (usually for releases).

***

#### 🔹 1. Improved Notes: Git at Scale
*   **Monorepo vs. Polyrepo:** Large orgs like Google and Meta use one giant repo (Monorepo) to ensure atomic changes across services, while others prefer many small repos (Polyrepo) for team autonomy.
*   **Trunk-Based Development:** The "Gold Standard" for DevOps. Engineers merge small, frequent changes to `main` daily, using Feature Flags to hide incomplete work. This eliminates "Merge Hell."

#### 🔹 2. Interview View (Q&A)
*   **Q:** What is a "Detached HEAD"?
*   **A:** It means you have checked out a specific commit rather than a branch. Any changes you make will be lost unless you create a new branch from that point.
*   **Q:** Explain `git squash`.
*   **A:** It takes multiple commits and collapses them into one. We use this before merging a feature branch to keep the main history clean and readable.

***

#### 🔹 3. Architecture & Design: The Git Workflow
1.  **Feature Branching:** Create a branch for every task.
2.  **Pull Request (PR):** Peer review and automated tests (CI) run here.
3.  **Merge to Main:** Once approved, the code moves to the source of truth.

***

#### 🔹 4. Commands & Configs (Power User)
```bash
# See a beautiful, graphical version of your history
git log --graph --oneline --all

# Fix the last commit (if you forgot to add a file)
git add .
git commit --amend --no-edit

# Search the entire history for a specific string
git log -S "API_KEY"
```

***

#### 🔹 5. Troubleshooting & Debugging
*   **Scenario:** You accidentally committed a 500MB database file.
*   **Fix:** Use `git filter-repo` or `bfg-repo-cleaner` to scrub the file from the entire history. Simply deleting it in a new commit won't work because it's still in the `.git` objects.

***

#### 🔹 6. Production Best Practices
*   **Conventional Commits:** Use a standard format like `feat:`, `fix:`, `docs:` to allow for automated changelog generation.
*   **Protected Branches:** Never allow direct pushes to `main`. Require PRs and status checks.
*   **Signed Commits:** Use GPG keys to sign your commits, ensuring that no one can impersonate you in the repository.

***

#### 🔹 Cheat Sheet / Quick Revision
| **Command** | **Purpose** | **DevOps Context** |
| :--- | :--- | :--- |
| `git clone` | Copy a repository | The start of every Jenkins/GitHub Actions job. |
| `git stash` | Save uncommitted work | Useful when you need to switch branches mid-task. |
| `git reset --hard` | Wipe local changes | Resets the environment to a known clean state. |
| `git cherry-pick` | Apply a specific commit | Porting a single hotfix from `main` to a `release` branch. |
| `git rev-parse` | Get commit SHA | Used in CI/CD scripts to tag Docker images. |

***

This is Section 3: Git & Version Control. For a senior role, Git is the "Source of Truth" for Infrastructure as Code and GitOps. You must understand how to manage complex merge conflicts and keep the history bisectable.