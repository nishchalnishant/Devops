---
description: Easy interview questions for Git, branching, and version control fundamentals.
---

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
