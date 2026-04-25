# Advanced Git Workflows & Monorepos

## Why Understanding Git Internals Matters

Most developers use Git as a black box: `git add`, `git commit`, `git push`. But when things go wrong — corrupted repos, massive merge conflicts, bisecting production issues, or managing monorepos at scale — you need to understand what's happening under the hood.

**Git is not a delta-diff system** (like SVN). It's a **content-addressable key-value store** with a version control layer on top:

```
Every piece of data = SHA-1 hash of its content
Store = .git/objects/ directory (or packed into .pack files)
Lookup = hash → content (not filename → content)
```

**Why this matters:**
- **Deduplication:** Identical files share the same blob object — saves space
- **Integrity:** Changing any content changes the SHA — tampering is detectable
- **Speed:** Hash-based lookups are O(1), not O(n)
- **Immutability:** Objects never change; "rewriting history" creates new objects

This document covers advanced workflows that leverage Git's internal architecture for enterprise-scale development.

***

## Git Internals — Object Model

```
.git/
├── objects/          content-addressable store (SHA-1 keyed)
│   ├── pack/         packfiles (compressed, delta-encoded)
│   └── xx/yyyyyy...  loose objects (first 2 chars = dir)
├── refs/
│   ├── heads/main    text file containing a commit SHA
│   └── tags/v1.0     text file (annotated tags point to tag objects)
├── COMMIT_EDITMSG
├── HEAD              text: "ref: refs/heads/main" or a SHA (detached)
├── index             binary: staging area
└── packed-refs       refs compacted into one file
```

**Four object types:**

| Type | Content | SHA derived from |
|------|---------|-----------------|
| blob | Raw file content | type + size + content |
| tree | List of (mode, name, blob/tree SHA) | type + size + content |
| commit | tree SHA + parent SHA + metadata + message | type + size + content |
| tag | object SHA + tag name + tagger + message | type + size + content |

```bash
# Inspect any object
git cat-file -t <sha>       # type
git cat-file -p <sha>       # pretty-print content
git ls-tree HEAD            # show tree of current commit
git log --format="%T %H"    # tree SHA per commit

# Walk the DAG manually
git rev-list HEAD --count   # total commits reachable from HEAD
git rev-list main..feature  # commits in feature not in main
```

***

## Branching Strategies

### Trunk-Based Development (TBD)

```
main (trunk) — always deployable
    │
    ├── feature/short-lived (< 2 days)
    │       └── merged via PR
    │
    ├── feature flags hide incomplete features
    │       LaunchDarkly, Unleash, Flagsmith
    │
    └── release branches (optional, for coordinated releases)
            release/2024-Q4 — cut from main, hotfixes cherry-picked back
```

**Enforcement in GitHub:**
```bash
# Branch protection via Terraform GitHub provider
resource "github_branch_protection" "main" {
  repository_id = github_repository.myrepo.node_id
  pattern       = "main"

  required_status_checks {
    strict   = true       # require branch to be up-to-date
    contexts = ["ci/build", "ci/test", "ci/security"]
  }
  required_pull_request_reviews {
    required_approving_review_count = 2
    dismiss_stale_reviews           = true
    require_code_owner_reviews      = true
  }
  restrict_pushes {
    push_allowances = ["myorg/platform-team"]  # only platform team can bypass
  }
}
```

### Gitflow (when appropriate)

```
main         ← production, tagged releases only
develop      ← integration branch
feature/*    ← branch from develop, merge back to develop
release/*    ← branch from develop, merge to main + develop
hotfix/*     ← branch from main, merge to main + develop
```

Gitflow is appropriate for: versioned software with discrete releases (libraries, desktop apps, mobile apps). Not appropriate for: SaaS platforms deploying continuously.

***

## Interactive Rebase — Advanced

```bash
# Rewrite the last 5 commits
git rebase -i HEAD~5

# Commands in the rebase editor:
# pick   = use commit as-is
# reword = use commit, edit message
# edit   = use commit, stop to amend (add more changes, split)
# squash = meld into previous commit, combine messages
# fixup  = meld into previous commit, discard this message
# drop   = remove commit entirely
# exec   = run shell command after commit

# Split a commit mid-rebase (when stopped at 'edit'):
git reset HEAD~          # unstage the commit's changes
git add -p               # selectively stage part 1
git commit -m "part 1"
git add .
git commit -m "part 2"
git rebase --continue

# Reorder commits by rearranging lines in the editor
# Change "pick A" "pick B" to "pick B" "pick A"
```

***

## Monorepo Tooling

### Nx (JavaScript/TypeScript monorepos)

```bash
# Create affected task graph
npx nx affected:graph

# Run only tests for changed projects and their dependents
npx nx affected --target=test --base=origin/main

# Cache: tasks are fingerprinted; re-runs skip if inputs unchanged
# Remote cache: Nx Cloud shares cache across CI machines
```

### Turborepo

```json
// turbo.json
{
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],    // build dependencies first
      "outputs": ["dist/**"]
    },
    "test": {
      "dependsOn": ["build"],
      "inputs": ["src/**", "tests/**"]
    },
    "lint": {
      "inputs": ["src/**", ".eslintrc.js"]
    }
  }
}
```

### Bazel (polyglot, Google-scale)

```python
# BUILD file
py_library(
    name = "mylib",
    srcs = ["mylib.py"],
    deps = ["//common:utils"],
)

py_test(
    name = "mylib_test",
    srcs = ["mylib_test.py"],
    deps = [":mylib"],
)
```

```bash
# Build only changed targets
bazel build //...
bazel test //... --test_output=errors

# Query dependency graph
bazel query 'rdeps(//..., //mylib:mylib)'   # who depends on mylib
bazel query 'deps(//services/checkout:all)' # all deps of checkout
```

### Sparse checkout for large monorepos

```bash
# Clone without files (metadata only)
git clone --filter=blob:none --no-checkout https://github.com/myorg/monorepo
cd monorepo

# Enable sparse checkout
git sparse-checkout init --cone

# Set which directories to download
git sparse-checkout set services/payments shared/proto tools/

git checkout main   # now only downloads specified dirs
```

***

## Cherry-pick and Patch Workflows

```bash
# Cherry-pick a commit from another branch (e.g., hotfix)
git cherry-pick abc1234

# Cherry-pick a range (exclusive start)
git cherry-pick abc1234..def5678

# Cherry-pick without committing (stage only)
git cherry-pick --no-commit abc1234

# Generate a patch file (for offline transfer)
git format-patch origin/main --stdout > my-changes.patch

# Apply a patch
git am my-changes.patch

# Apply without committing (like cherry-pick --no-commit)
git apply my-changes.patch
```

***

## History Rewriting — Safety and Tools

```bash
# git filter-repo — remove a file from all history
git filter-repo --path credentials.json --invert-paths

# Remove a directory
git filter-repo --path-glob 'internal/secrets/*' --invert-paths

# Remove all commits by a specific author (GDPR compliance)
git filter-repo --email-callback '
  if email == b"leaver@example.com":
    return b"anonymized@example.com"
  return email
'

# After rewriting: all downstream clones must re-clone or re-fetch
# Force-push is required (coordinate with team before doing this)
git push --force-with-lease origin main
```

**`git reflog` — the undo button:**
```bash
git reflog show HEAD --date=relative   # all HEAD moves with timestamps
git checkout HEAD@{3}                  # go back to where HEAD was 3 moves ago
git branch rescue HEAD@{5}            # create branch at a past HEAD position
```

***

## Commit Message Conventions (Conventional Commits)

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]

Types: feat, fix, docs, style, refactor, perf, test, chore, ci, build
Scope: component or subsystem name

Examples:
feat(auth): add OIDC login support
fix(payments): handle currency rounding for EUR
fix!: drop support for Node 14    # ! = breaking change
```

**Tooling:**
```bash
# Commitlint — enforce conventional commits in CI
npm install -g @commitlint/cli @commitlint/config-conventional
echo "module.exports = { extends: ['@commitlint/config-conventional'] }" > commitlint.config.js

# In GitHub Actions:
npx commitlint --from=origin/main --to=HEAD

# Semantic-release — auto-version and changelog from commit messages
npx semantic-release   # reads commits, bumps semver, creates GitHub release
```

***

## Git Hooks at Scale

```bash
# pre-commit — run before every commit (client-side)
# .pre-commit-config.yaml (manages hooks across the team)
repos:
- repo: https://github.com/pre-commit/pre-commit-hooks
  rev: v4.5.0
  hooks:
  - id: trailing-whitespace
  - id: end-of-file-fixer
  - id: check-yaml
  - id: detect-private-key
- repo: https://github.com/gitleaks/gitleaks
  rev: v8.18.0
  hooks:
  - id: gitleaks

# Install for all developers
pre-commit install

# CI enforcement (even if developer skipped install)
pre-commit run --all-files
```

***

## Key Gotchas

| Gotcha | Detail |
|--------|--------|
| `git pull --rebase` vs `--merge` | `--merge` creates merge commits; `--rebase` replays local commits on top, keeping linear history. Set `pull.rebase=true` globally |
| Octopus merges can't be rebased | A commit with 3+ parents cannot be replayed with rebase; must use `git merge` |
| `git stash` is a stack | `git stash pop` fails if there's a conflict; use `git stash apply` + manual resolve, then `git stash drop` |
| Submodule state is a pinned commit SHA | `git clone --recurse-submodules` is required; `git pull` in parent doesn't update submodules |
| `--force-with-lease` vs `--force` | `--force-with-lease` fails if the remote has commits you haven't fetched — safer than `--force` |
| Shallow clones break some tools | `git clone --depth=1` makes `git log`, `git bisect`, and some monorepo tools fail; use `--unshallow` in CI when needed |
| `git rebase` changes SHAs | All rebased commits get new SHAs — any branches tracking those commits must also be rebased or reset |
| `filter-repo` vs `BFG` | `filter-repo` is the official recommendation; BFG is faster for simple blob removal but less flexible |
