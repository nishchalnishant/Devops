# Git — Production Scenario Drills

## 1. Detached HEAD Recovery

**Situation:** You checked out a tag or commit SHA directly, made changes, and now realize you're in detached HEAD state. Your commits are not on any branch.

```bash
# Confirm detached state
git status
# HEAD detached at a3f9d12

# Option A: Save work to a new branch
git checkout -b rescue/my-work
# Now commits are preserved on the new branch

# Option B: If you already left detached HEAD without branching
git reflog
# Find the SHA of your lost commits, e.g. a3f9d12

git branch rescue/my-work a3f9d12
git checkout rescue/my-work
```

**Prevention:** Never do work in detached HEAD without immediately creating a branch. Always `git checkout -b <name>` before making changes after checking out a tag/SHA.

***

## 2. Force-Push Disaster Recovery

**Situation:** Someone ran `git push --force` on `main` and overwrote 3 commits that others had pulled.

### For the person who force-pushed

```bash
# Find the SHA of the lost commits
git reflog
# e.g., HEAD@{2} is the commit before the force push

# Restore the branch to the old state
git reset --hard HEAD@{2}

# Push again — now you need another force push to fix the damage
# Use --force-with-lease as a habit check, but here --force is needed
git push --force origin main
```

### For teammates who already pulled (their local main now has the bad state)

```bash
# Option A: Reset to match remote after it's been fixed
git fetch origin
git reset --hard origin/main

# Option B: If they had unique local commits on top of the bad state
git fetch origin
git rebase origin/main
```

**Prevention:** Protect `main` with branch protection rules. Require PRs. If force push is needed legitimately, use `git push --force-with-lease` — it fails if the remote tip moved since your last fetch.

***

## 3. Large File Accidentally Committed

**Situation:** A 500MB binary or database dump was committed and pushed. `git rm` is not enough — the object still lives in `.git/objects/`.

### Step 1: Identify the file

```bash
# Find the commit that added the large file
git log --all --full-history -- path/to/large-file.bin

# Or find large objects in history
git rev-list --objects --all | \
  git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | \
  awk '/^blob/ { print $3, $4 }' | sort -rn | head -20
```

### Step 2: Rewrite history with git filter-repo

```bash
# Install: pip install git-filter-repo

git filter-repo --path path/to/large-file.bin --invert-paths
```

This rewrites the entire history, removing the file from all commits. All commit SHAs change.

### Step 3: Force push and coordinate

```bash
git push --force origin main

# Notify all teammates to re-clone or hard-reset:
git fetch origin
git reset --hard origin/main
```

**If it was a secret (key/password):** Rotate the credential immediately — treat it as compromised regardless of history rewrite. If the repo is public, the secret was already scraped.

**BFG Repo-Cleaner** is an alternative to `filter-repo` for simpler cases:
```bash
java -jar bfg.jar --delete-files large-file.bin
git reflog expire --expire=now --all && git gc --prune=now --aggressive
```

***

## 4. Merge Conflict in CI

**Situation:** A CI pipeline fails with merge conflicts during an automated merge (e.g., auto-merge of a release branch into main).

### Diagnosis

```bash
# Reproduce locally
git fetch origin
git checkout main
git merge origin/release/1.4
# CONFLICT (content): Merge conflict in src/config.py

git status              # list all conflicted files
git log --merge         # show commits on both sides causing conflict
git diff                # see conflict markers in conflicted files
```

### Resolution

```bash
# For each conflicted file:
# 1. Open in editor, resolve markers
# 2. Test that the resolution is correct

git add src/config.py   # mark resolved
git commit              # complete merge with auto-generated message
```

### For automated merges in CI

Options when CI can't auto-resolve:
1. Fail the pipeline and notify the team — require human resolution
2. Use `git merge -X ours` or `-X theirs` if the conflict strategy is deterministic (risky)
3. Require feature branches to rebase onto main before the PR can merge

```bash
# Merge with strategy preference (use carefully)
git merge -X ours release/1.4       # prefer current branch on conflict
git merge -X theirs release/1.4     # prefer incoming branch on conflict
```

***

## 5. Lost Commit Recovery via Reflog

**Situation:** You ran `git reset --hard` or deleted a branch and lost commits.

```bash
# See everything HEAD has pointed to in the last 90 days
git reflog
# Example output:
# 7a3c91f HEAD@{0}: reset: moving to HEAD~3
# b4d82e1 HEAD@{1}: commit: add payment module
# 9f1a023 HEAD@{2}: commit: fix checkout bug
# ...

# Identify the commit you lost (e.g. b4d82e1)
git show b4d82e1             # verify it's the right commit

# Option A: Create a branch from the lost commit
git branch recovered b4d82e1

# Option B: Reset current branch back to the lost commit
git reset --hard b4d82e1
```

### Recovering a deleted branch

```bash
# Find the last commit that was on the branch
git reflog | grep "checkout: moving from deleted-branch"
# or
git reflog | grep "deleted-branch"

git branch recovered-branch <sha>
```

### Finding dangling commits (objects with no refs)

```bash
git fsck --lost-found
# Dangling commits appear in .git/lost-found/commit/
```

**Time limit:** Reflog entries expire after 90 days by default. `git gc` removes unreferenced objects. Act quickly.

***

## 6. Monorepo Partial Checkout

**Situation:** The monorepo is 50GB. You only work on `services/api`. Cloning everything wastes disk and time.

```bash
# Step 1: Shallow clone without checking out files
git clone --filter=blob:none --no-checkout https://github.com/org/monorepo.git
cd monorepo

# Step 2: Enable cone-mode sparse checkout
git sparse-checkout init --cone

# Step 3: Set paths you need
git sparse-checkout set services/api lib/shared infra/k8s/api

# Step 4: Checkout
git checkout main

# Verify
git sparse-checkout list
```

### Adding more paths later

```bash
git sparse-checkout add services/payments
```

### Partial clone vs shallow clone

| | Shallow (`--depth 1`) | Partial (`--filter=blob:none`) | Sparse checkout |
|-|-----------------------|-------------------------------|-----------------|
| Reduces | History depth | Blob objects | Working tree files |
| History available | No | Yes (fetched on demand) | Yes |
| Use case | CI pipelines | Monorepos | Monorepos |

### Running affected-only CI in monorepos

```bash
# Find which services changed since last merge base
CHANGED=$(git diff --name-only origin/main...HEAD | cut -d/ -f1-2 | sort -u)
echo "$CHANGED"   # e.g. services/api, lib/shared

# Run tests only for changed services
for svc in $CHANGED; do
  if [ -f "$svc/Makefile" ]; then
    make -C "$svc" test
  fi
done
```

***

## 7. Broken Submodule

**Situation:** After cloning or pulling, a submodule directory is empty or shows a wrong commit. CI fails with "module not found".

### Diagnosis

```bash
git submodule status
# - a1b2c3d vendor/lib  (missing leading space means uninitialized)
# + a1b2c3d vendor/lib  (+ means different commit than recorded in .gitmodules)
# U vendor/lib          (merge conflict in submodule)
```

### Fix: Uninitialized submodule

```bash
git submodule update --init --recursive
```

### Fix: Submodule pointing to wrong commit

```bash
# Option A: Reset submodule to the commit recorded in the parent repo
git submodule update --recursive

# Option B: Update the pinned commit to latest upstream
git submodule update --remote vendor/lib
git add vendor/lib
git commit -m "chore: update lib submodule to latest"
```

### Fix: Submodule URL changed

```bash
# Edit .gitmodules with new URL
git submodule sync
git submodule update --init
```

### Fix: Completely broken — nuke and re-init

```bash
# Remove submodule tracking
git submodule deinit -f vendor/lib
rm -rf .git/modules/vendor/lib
git rm -f vendor/lib

# Re-add fresh
git submodule add <new-url> vendor/lib
git submodule update --init
```

### Prevent CI failures

Always use in CI:
```bash
git clone --recurse-submodules <url>
# Or after clone:
git submodule update --init --recursive
```

***

## 8. Bisect a Regression

**Situation:** Tests pass on `v2.0.0` but fail on `v2.5.0`. The 200-commit range contains the bug. Find the exact commit that introduced it.

### Manual bisect

```bash
git bisect start
git bisect bad                      # current HEAD is broken
git bisect good v2.0.0              # this tag was known good

# Git checks out the midpoint commit (~commit 100)
# Run your test manually:
./test.sh
# If test fails:
git bisect bad
# If test passes:
git bisect good
# Repeat ~8 times (log2(200) ≈ 8 steps)

# Git announces the first bad commit:
# a4f9d12 is the first bad commit

git bisect reset                    # return to original HEAD
```

### Automated bisect with a script

```bash
git bisect start
git bisect bad HEAD
git bisect good v2.0.0

# Script exits 0 if good, non-zero if bad
git bisect run ./ci/regression-test.sh

git bisect reset
```

The test script must:
- Build/compile the project at each commit if needed
- Return exit code 0 for "good" and 125 to skip untestable commits

```bash
# Example bisect script
#!/bin/bash
make build 2>/dev/null || exit 125   # skip if build fails
./test.sh
```

### Skip a commit (e.g., broken build unrelated to the bug)

```bash
git bisect skip
# or skip a range
git bisect skip v2.2.0..v2.2.3
```

### After finding the culprit

```bash
# Inspect the bad commit
git show a4f9d12

# See what files changed
git show --stat a4f9d12

# Find the PR/branch that introduced it
git log --merges --ancestry-path a4f9d12..main | head -5
```

***

## 9. Git Worktrees for Multi-Tasking
**Situation:** You are in the middle of a massive feature branch (`feature/ui-overhaul`) with hundreds of uncommitted changes. Your boss asks for an immediate hotfix on `main`. Stashing and switching is risky and slow.
**Diagnosis:** You need to work on two branches simultaneously in the same repo without context-switching.
**Fix:** 
1. Use **Git Worktrees**: `git worktree add ../hotfix main`.
2. This creates a new folder `../hotfix` that points to the `main` branch.
3. Open a new terminal in `../hotfix`, fix the bug, commit, and push.
4. Go back to your original folder and continue your UI overhaul.
5. Cleanup: `git worktree remove ../hotfix`.

## 10. The "Lost Stash" Recovery
**Situation:** You ran `git stash pop`, it had a conflict, and then you ran `git stash drop` or `git reset` thinking you didn't need it, but you actually lost your work.
**Diagnosis:** `git stash` is just a commit. When "dropped", the commit object still exists in the database for a short time.
**Fix:** 
1. Use `git fsck --unreachable | grep commit | cut -d' ' -f3 | xargs git show`.
2. Look through the output for your lost work.
3. Once found, run `git stash apply <SHA>`.

## 11. Recovering from Internal Object Corruption
**Situation:** `git status` fails with `error: object file .git/objects/xx/xxx is empty`. This usually happens after a sudden power loss.
**Diagnosis:** One or more Git objects are corrupted/empty.
**Fix:** 
1. Identify the broken object via `git fsck`.
2. If it's a blob from another branch, you might be able to find it in the remote: `git fetch origin`.
3. If it's your local uncommitted work, find the file in the index: `git ls-files --stage`.
4. Hard fix: Delete the empty object file and run `git fetch` to pull the object from the remote.

## 12. "git rerere" (Reuse Recorded Resolution)
**Situation:** You have a long-running feature branch that you rebase onto `main` every day. Every time, you have to resolve the same 5 merge conflicts.
**Diagnosis:** You are wasting time repeating the same manual resolutions.
**Fix:** 
1. Enable rerere: `git config --global rerere.enabled true`.
2. The next time you resolve a conflict, Git will "record" how you did it.
3. The *next* time that same conflict occurs during a rebase/merge, Git will automatically apply your previous resolution.

## 13. Solving Slow Commit Times (Pre-commit Bloat)
**Situation:** `git commit` takes 30 seconds because it runs 50 linters and tests via pre-commit hooks.
**Diagnosis:** The pre-commit hooks are running on the entire codebase or are inefficient.
**Fix:** 
1. Use `pre-commit run --files <changed_files>` to only check affected files.
2. If in an emergency, bypass hooks: `git commit -m "hotfix" --no-verify`.
3. Optimize: Use a faster linter (e.g., `ruff` instead of `flake8/pylint`) or run hooks in CI instead of locally.

## 14. Collaborative Rebase (The "Shared Branch" Rebase)
**Situation:** You and a teammate are working on `feature/auth`. You need to rebase it onto `main`, but rebasing changes SHAs and will break your teammate's local copy.
**Diagnosis:** Standard rebase is dangerous for shared branches.
**Fix:** 
1. Coordinate: "Hey, I'm rebasing the auth branch now. Don't push."
2. Run `git rebase main`.
3. Force push with caution: `git push --force-with-lease`.
4. Teammate's fix: `git fetch` followed by `git rebase origin/feature/auth` (NOT `git pull`).

## 15. The "Dirty" Reset Recovery
**Situation:** You had local changes, then ran `git reset --hard origin/main` and lost your uncommitted work.
**Diagnosis:** Uncommitted changes are NOT tracked by `git reflog`. If they weren't `add`ed to the index, they might be gone forever.
**Fix:** 
- If you ran `git add` at any point, use `git fsck --lost-found`. Check `.git/lost-found/other` for files.
- **Prevention habit:** Always `git stash` before a `reset --hard`.


### Scenario 16: Git LFS Quota Exhaustion
**Symptom:** `git push` fails with `LFS: Batch response: Git LFS is disabled for this repository`.
**Diagnosis:** You've reached the storage or bandwidth limit for Large File Storage.
**Fix:** 
1. Clean up old LFS objects: `git lfs prune`.
2. Increase the quota in GitHub/GitLab settings.

### Scenario 17: SSH Key Type Incompatibility
**Symptom:** `git clone` fails with `sign_and_send_pubkey: no mutual signature supported`.
**Diagnosis:** Your local SSH is too new and deprecated `ssh-rsa` (SHA-1), but the server only supports it.
**Fix:** Generate an Ed25519 key: `ssh-keygen -t ed25519`.
