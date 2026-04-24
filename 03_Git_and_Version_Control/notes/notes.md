# Git — Deep Theory & Internals

## 1. Git Internals: The Content-Addressable Filesystem

Git is not a delta-diff version control system. It is a **content-addressable key-value store** with a thin version control layer on top. Every piece of data is stored as an object, identified by the SHA-1 (transitioning to SHA-256) hash of its content.

### The Four Object Types

| Object | SHA-1 Input | Description |
|--------|------------|-------------|
| **Blob** | File content only | Raw bytes — no filename, no mode, no metadata |
| **Tree** | List of `(mode, name, sha1)` tuples | Directory snapshot; maps filenames to blob/tree SHAs |
| **Commit** | Tree SHA + parent(s) + author + message | A snapshot in time; points to a root tree and parent commit(s) |
| **Tag** | Object SHA + tagger + message | Annotated pointer, usually to a commit; can be GPG-signed |

```bash
# Inspect any object
git cat-file -t <sha>         # type
git cat-file -p <sha>         # content (pretty-printed)

# Example: read the current commit's tree
git cat-file -p HEAD
# tree a1b2c3...
# parent d4e5f6...
# author  Alice <alice@example.com> 1711000000 +0000
# committer Alice <alice@example.com> 1711000000 +0000
# feat: add payment service

# Walk the tree
git cat-file -p a1b2c3
# 100644 blob 9ab7d8... README.md
# 040000 tree 2c3d4e... src
```

> [!IMPORTANT]
> Identical content always produces the same SHA-1. This means Git **deduplicates** storage automatically. Two files with identical content share one blob object. This is why Git is fast and efficient for large codebases.

### Object Storage Layout

```
.git/objects/
  a1/b2c3d4e5f6...   <- loose object (first 2 hex chars = directory)
  pack/
    pack-abc123.idx   <- index: maps SHA-1 → byte offset in pack
    pack-abc123.pack  <- packed objects with delta compression
  info/
```

Objects start as **loose objects** — one file per object. After accumulation, `git gc` packs them into **pack files**.

---

## 2. The DAG (Directed Acyclic Graph)

Commits form a DAG. Each commit has one or more parents (zero for the initial commit, two for a merge commit, more for an octopus merge). The graph is **immutable** — objects are never modified, only new objects are created.

```
A ← B ← C ← M (merge commit, two parents: C and E)
             ↑
         D ← E (feature branch)
```

"Rewriting history" (rebase, amend, filter-repo) does not mutate existing objects. It creates **new** objects with new SHAs and moves refs to point to them. The old objects remain until garbage collected.

### Refs: The Mutable Layer

Refs are plain text files under `.git/refs/` or packed in `.git/packed-refs`.

```
.git/
  HEAD                        # symbolic ref or detached SHA
  refs/
    heads/
      main                    # local branch — contains SHA of tip commit
      feature/payments
    remotes/
      origin/
        main                  # remote-tracking branch
    tags/
      v1.0.0                  # lightweight tag (just a SHA)
  ORIG_HEAD                   # set before risky ops (merge, rebase, reset)
  MERGE_HEAD                  # the commit being merged in
  CHERRY_PICK_HEAD            # during cherry-pick
  REBASE_HEAD                 # during rebase
```

`HEAD` is a symbolic ref: `ref: refs/heads/main`. In detached HEAD state, it contains a bare SHA-1.

```bash
cat .git/HEAD
# ref: refs/heads/main

cat .git/refs/heads/main
# 7f3a8d91...
```

---

## 3. Pack Files and Delta Compression

Pack files dramatically reduce storage. Git applies **delta compression**: instead of storing full copies, it stores one base object and a sequence of byte-level patches to reconstruct similar objects.

```bash
# Manually trigger pack file creation
git gc                          # standard GC with default thresholds
git gc --aggressive             # deeper compression (slower)

# Inspect pack file contents
git verify-pack -v .git/objects/pack/pack-*.idx | sort -k3 -rn | head -20

# Re-pack explicitly
git repack -a -d --delta-depth=250 --window=250
```

Pack files have two components:
- **`.pack`**: sequential binary data of all packed objects
- **`.idx`**: sorted index of SHA-1 → byte offset, enabling O(log n) lookup

> [!TIP]
> Running `git maintenance start` sets up a background cron/launchd job that automatically runs incremental repack, loose object pruning, commit-graph writes, and prefetch. Essential for repos that grow fast.

### Garbage Collection

```bash
git gc                          # pack loose objects, prune expired reflog entries
git gc --prune=now              # prune all unreachable objects immediately
git count-objects -vH           # show object count and disk usage
git fsck                        # check object database integrity
git fsck --lost-found           # write dangling objects to .git/lost-found/
```

Default reflog expiry: **90 days** for reachable commits, **30 days** for unreachable. Objects with no refs are eligible for GC only after reflog expiry.

---

## 4. Staging Area (Index)

The index (`.git/index`) is a binary file representing the **next commit's tree**. It is the staging area — a prepared state between the working tree and the object database.

```
Working Tree  ──git add──▶  Index  ──git commit──▶  Object DB (HEAD)
```

| Command | Effect |
|---------|--------|
| `git diff` | Working tree vs Index |
| `git diff --staged` | Index vs HEAD |
| `git diff HEAD` | Working tree vs HEAD |
| `git add -p` | Interactively select hunks into Index |
| `git restore --staged <file>` | Remove from Index, keep working tree |

The index also stores file metadata (mode, mtime, size, inode) used to quickly detect which files have changed without rehashing.

---

## 5. Branching Strategies

### Trunk-Based Development (TBD)

All engineers commit to a single branch (`main`/`trunk`) at least daily. Short-lived feature branches (< 2 days) are tolerated but must integrate fast.

```
main: A──B──C──D──E──F──G──H  (multiple engineers per day)
           ↑         ↑
     feature/x   feature/y   (< 2 days, then merged back)
```

**Mechanics:**
- Feature flags decouple **deployment** (code ships to prod) from **release** (feature turns on for users)
- Incomplete features merge behind a flag — fully integrated but invisible
- LGTM + passing CI = immediate merge, no release branch gatekeeping

**Pros:** No long-lived divergence, true CI, eliminates "merge Wednesdays," fast feedback loop, bisect-friendly linear history.

**Cons:** Requires mature feature flag infrastructure, strong test coverage at merge time, developer discipline.

**Where used:** Google (Piper/CitC), Meta, Amazon, Netflix — any high-velocity org.

### GitFlow

Long-lived branches: `main` (production), `develop` (integration), `release/*`, `hotfix/*`, `feature/*`.

```
main ───────────────────────────────────────────────▶ (production tags)
       ↑ merge+tag                     ↑ merge+tag
develop ──────────────────────────────────────────▶
       ↑               ↑ merge       ↑
 feature/x        release/1.2   hotfix/critical
```

**Pros:** Clear structure for scheduled releases, isolates release stabilization from feature work.

**Cons:** Enormous merge conflicts after long divergence, slow integration, complex branch management, long feedback loop.

**Where used:** Mobile apps (App Store gating), firmware, embedded systems, regulated industries with fixed release cadences.

### GitHub Flow

Simplified: `main` is always deployable. Create a short-lived feature branch, open a PR, review, merge to main, deploy immediately.

**Pros:** Simple, fast, good for web SaaS products with continuous deployment.

**Cons:** No staging or release branch concept — requires deploy pipeline maturity to be safe.

### Comparison

| Factor | Trunk-Based | GitFlow | GitHub Flow |
|--------|-------------|---------|-------------|
| Branch lifespan | < 2 days | Weeks/months | Days |
| Merge conflict risk | Low | High | Medium |
| Release cadence | Continuous | Scheduled | Continuous |
| Feature flags required | Yes | No | Sometimes |
| CI complexity | Low | High | Low |
| Best for | High-velocity SaaS | Versioned software | Small teams/SaaS |

---

## 6. Merge vs Rebase vs Squash

### Merge

Creates a new commit with **two parents**. Preserves full branch history and timestamps.

```bash
git checkout main
git merge feature/x           # creates merge commit M
git merge --no-ff feature/x   # force merge commit even if fast-forward is possible
```

```
Before:  main: A──B──C
         feat:      D──E

After:   main: A──B──C──M   (M has parents C and E)
                    \  /
                     D──E
```

**Use when:** The feature has meaningful history worth preserving, or in public/shared branches where rewriting is forbidden.

### Rebase

Replays commits from one branch on top of another. Creates **new SHAs** for every replayed commit.

```bash
git checkout feature/x
git rebase main               # replays D, E on top of current main tip
```

```
Before:  main: A──B──C
         feat: A──B──D──E

After:   main: A──B──C
         feat: A──B──C──D'──E'  (D', E' are new objects with new SHAs)
```

> [!CAUTION]
> **Golden Rule:** Never rebase commits that have been pushed to a shared branch. Teammates who have based work on those commits will have diverged histories, requiring forced reconciliation.

**Use when:** Cleaning up local feature branch history before a PR, syncing a feature branch with main (locally).

### Interactive Rebase

```bash
git rebase -i HEAD~5         # open editor for last 5 commits
```

Editor commands:
```
pick   a1b2c3 feat: add login
reword d4e5f6 fix: typo       # edit commit message
squash 7g8h9i WIP             # meld into previous commit (keep message)
fixup  j1k2l3 WIP             # meld into previous commit (discard message)
drop   m4n5o6 temp debug      # remove commit entirely
edit   p7q8r9 refactor auth   # pause here to amend
```

### Squash

Collapses all commits from a branch into one before merging. The branch history is discarded; only the final state appears in main.

```bash
# During merge:
git merge --squash feature/x
git commit -m "feat: complete payment integration"

# Or via interactive rebase before merging:
git rebase -i HEAD~8          # squash 8 WIP commits
```

**Use when:** Feature branch has many noisy WIP/fixup commits that pollute main's history. Common PR workflow: engineer squashes before merge, main stays bisectable.

### Decision Matrix

| Scenario | Strategy |
|----------|----------|
| Local cleanup before PR review | Interactive rebase + squash |
| Merging a short-lived feature PR | Squash merge |
| Merging a long-lived release branch | Merge (preserve context) |
| Syncing local feature branch with main | Rebase (never push the rebased branch) |
| Shared public branch | Merge only |
| Hotfix cherry-picked to release branch | Cherry-pick |

---

## 7. Monorepo Patterns

### Polyrepo vs Monorepo

| Strategy | Pros | Cons |
|----------|------|------|
| **Polyrepo** | Team autonomy, independent release cadences, smaller clone size | Cross-service refactors painful, dependency hell, duplicated tooling/CI standards |
| **Monorepo** | Atomic cross-service commits, unified tooling, single source of truth, easier large-scale refactors | Requires purpose-built tooling, naive CI becomes slow, large clone size |

### Monorepo Tooling

- **Bazel (Google):** Build system with a hermetic dependency graph. Understands exactly which targets depend on changed files — rebuilds and retests only what's affected.
- **Nx:** JavaScript/TypeScript-focused. Affected command: `nx affected:test` runs tests only for projects that transitively depend on changed files.
- **Turborepo:** Similar to Nx. Remote caching — CI hits a cache if the inputs haven't changed.
- **Pants:** Python-focused. Hermetic builds with fine-grained invalidation.

### Sparse Checkout for Monorepos

```bash
# Clone without materializing any files
git clone --filter=blob:none --no-checkout https://github.com/org/monorepo.git
cd monorepo

# Enable cone mode (faster, path-prefix based)
git sparse-checkout init --cone

# Declare the directories you need
git sparse-checkout set services/api lib/shared infra/k8s

# Materialize
git checkout main
```

Cone mode only allows path prefixes (full directories), not arbitrary patterns. Use non-cone mode for glob patterns (slower).

### Affected-Only CI

```bash
# Find changed top-level service directories vs merge base
CHANGED=$(git diff --name-only origin/main...HEAD | cut -d/ -f1-2 | sort -u)

for dir in $CHANGED; do
  [ -f "$dir/Makefile" ] && make -C "$dir" test
done
```

---

## 8. Signed Commits and Supply Chain Security

### Why Signing Matters

Without signing, anyone can set `git config user.email anyone@company.com` and commit as another person. The author field in a commit is just a string — it carries no authentication. Signed commits provide **cryptographic proof of authorship**.

In supply chain security (SLSA Level 2+), signed commits are an attestation layer: you can enforce that only commits from verified identities reach protected branches.

### GPG Signing

```bash
# Generate key
gpg --full-generate-key       # choose RSA 4096 or Ed25519

# List keys
gpg --list-secret-keys --keyid-format LONG

# Configure Git
git config --global user.signingkey <KEY_ID>
git config --global commit.gpgsign true   # sign all commits automatically

# Sign manually
git commit -S -m "feat: signed commit"

# Sign a tag
git tag -s v1.0.0 -m "release v1.0.0"

# Verify
git verify-commit <sha>
git log --show-signature
```

Upload the public key to GitHub → Settings → SSH and GPG keys → New GPG key.

### SSH Signing (Git 2.34+)

```bash
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_ed25519.pub
git config --global commit.gpgsign true
```

SSH signing is simpler to set up than GPG and integrates with existing SSH infrastructure. GitHub supports SSH signature verification.

### Enforcement

In GitHub, enable "Require signed commits" in branch protection rules. Commits without a verified signature are rejected on push.

---

## 9. Git Hooks Architecture

Hooks are executable scripts in `.git/hooks/` triggered at specific lifecycle events. They are **not tracked by git** — they exist only in the local `.git/` directory.

### Hook Reference

| Hook | Trigger | Typical Use |
|------|---------|-------------|
| `pre-commit` | Before commit object is created | Lint, format, secret scan, unit tests |
| `prepare-commit-msg` | After default message is created, before editor | Inject branch name into message |
| `commit-msg` | After user writes message | Enforce conventional commits format |
| `post-commit` | After commit is created | Notifications, log |
| `pre-rebase` | Before rebase starts | Safety checks on shared branches |
| `pre-push` | Before push is sent to remote | Run integration tests |
| `post-merge` | After merge completes | `npm install`, dependency sync |
| `post-checkout` | After branch switch | Env setup, dependency check |
| `pre-receive` | Server-side: before refs are updated | Policy enforcement (server) |
| `update` | Server-side: per ref being updated | Per-branch policy |
| `post-receive` | Server-side: after all refs updated | CI trigger, deploy |

### Sharing Hooks with the Team

```bash
# Store hooks in a tracked directory
mkdir .githooks
cp .git/hooks/pre-commit .githooks/pre-commit

# Point git to them
git config core.hooksPath .githooks

# Or set project-wide via .git/config during repo init automation
```

### Example Hooks

```bash
# .githooks/commit-msg — enforce conventional commits
#!/bin/sh
commit_msg=$(cat "$1")
pattern="^(feat|fix|chore|docs|style|refactor|perf|test|ci|build|revert)(\(.+\))?: .+"
if ! echo "$commit_msg" | grep -qE "$pattern"; then
  echo "ERROR: Commit message must follow Conventional Commits format"
  echo "  Example: feat(auth): add OAuth2 login"
  exit 1
fi
```

```bash
# .githooks/pre-push — block direct push to main
#!/bin/sh
protected="main master"
current=$(git symbolic-ref HEAD 2>/dev/null | sed 's|refs/heads/||')
for branch in $protected; do
  if [ "$current" = "$branch" ]; then
    echo "ERROR: Direct push to $branch is blocked. Open a PR."
    exit 1
  fi
done
```

> [!TIP]
> Use the `pre-commit` framework (https://pre-commit.com) for multi-language hook management. Define hooks in `.pre-commit-config.yaml` — it handles installation, versioning, and running hooks in isolated environments.

---

## 10. Git Protocols: HTTPS vs SSH vs git://

| Protocol | URL Format | Auth Method | Firewall | Use Case |
|----------|-----------|------------|----------|----------|
| **HTTPS** | `https://github.com/org/repo.git` | PAT / OAuth token | Friendly (port 443) | CI, simple setups, corporate firewalls |
| **SSH** | `git@github.com:org/repo.git` | SSH keypair | Port 22 (may be blocked) | Developer workstations |
| **git://** | `git://github.com/org/repo.git` | None (read-only) | Port 9418 | Anonymous read — deprecated/rare |

> [!CAUTION]
> The `git://` protocol provides **no authentication or encryption**. It is effectively deprecated for anything security-sensitive. GitHub no longer supports it for push operations.

### SSH Setup

```bash
# Generate a key (use ed25519, not RSA if possible)
ssh-keygen -t ed25519 -C "you@example.com" -f ~/.ssh/github_ed25519

# Add to SSH agent
ssh-add ~/.ssh/github_ed25519

# Configure host (~/.ssh/config)
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/github_ed25519
  AddKeysToAgent yes

# Test
ssh -T git@github.com
```

### HTTPS with PAT (CI Pipelines)

```bash
# Embed PAT in remote URL (don't store in shell history — use env var)
git remote set-url origin https://${GITHUB_TOKEN}@github.com/org/repo.git

# Or use credential helper
git config --global credential.helper store   # plain text — use with caution
git config --global credential.helper osxkeychain  # macOS
```

---

## 11. Partial Clones and Shallow Clones

### Shallow Clone

Downloads a truncated history. Objects from before the depth cutoff are not fetched.

```bash
git clone --depth 1 <url>               # only latest commit
git clone --depth 10 <url>              # last 10 commits
git fetch --unshallow                   # convert to full clone later
```

**Use case:** CI pipelines that only need to build the current commit. Saves clone time significantly on repos with long history.

**Limitation:** `git bisect`, `git log --follow`, and history-dependent tools break on shallow clones.

### Partial Clone (Filter)

Downloads the full commit graph but defers fetching blob objects until needed.

```bash
git clone --filter=blob:none <url>      # no blobs initially; fetched on checkout
git clone --filter=tree:0 <url>         # no trees or blobs; maximum deferral
```

Partial clones maintain full history visibility — you can run `git log`, `git bisect`, etc. Blobs are fetched lazily when you access file content.

**Use case:** Monorepos where you only work in a few directories. Combine with sparse-checkout.

### Comparison

| | Shallow `--depth 1` | Partial `--filter=blob:none` | Sparse Checkout |
|-|---------------------|------------------------------|-----------------|
| What is omitted | Old history | Blob objects | Working tree files |
| Full history visible | No | Yes | Yes |
| `git bisect` works | No | Yes | Yes |
| Typical use | CI build speed | Monorepo dev | Monorepo dev |

---

## 12. Git Bundle and git-archive

### git bundle

Bundles a repository (or subset) into a single file for transfer over sneakernet (no network connection to remote).

```bash
# Create a bundle of everything
git bundle create repo.bundle --all

# Create an incremental bundle (since a tag)
git bundle create updates.bundle v1.0.0..HEAD

# Clone from a bundle
git clone repo.bundle -b main my-repo

# Pull from a bundle
git pull /path/to/updates.bundle main
```

**Use case:** Air-gapped environments, offline distribution of repositories, DR scenarios.

### git archive

Export a snapshot of a tree without `.git/` metadata.

```bash
git archive --format=tar.gz --prefix=myapp-1.0/ v1.0.0 | gzip > myapp-1.0.tar.gz
git archive HEAD -- src/ | tar -x -C /tmp/extract
```

---

## 13. rerere — Reuse Recorded Resolution

`rerere` (Reuse Recorded Resolution) records conflict resolutions and replays them automatically when the same conflict recurs.

```bash
git config rerere.enabled true            # enable globally or per-repo

# Conflicts are recorded in .git/rr-cache/
# After resolving a conflict manually, rerere records it
# Next time the same conflict occurs, rerere applies the resolution automatically

git rerere                                # manually trigger rerere
git rerere forget <file>                  # forget the recorded resolution for a file
```

> [!TIP]
> `rerere` is most valuable when a long-lived feature branch is repeatedly rebased onto `main`. The same conflicts appear each rebase. After the first manual resolution, subsequent rebases resolve automatically.
