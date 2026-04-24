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

***

