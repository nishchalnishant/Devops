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

***

