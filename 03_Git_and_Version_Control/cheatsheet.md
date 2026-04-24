# Git — Comprehensive Command Cheatsheet

## Setup and Configuration

```bash
# Identity
git config --global user.name "Your Name"
git config --global user.email "you@example.com"

# Editor and tools
git config --global core.editor "vim"
git config --global merge.tool vimdiff
git config --global diff.tool vimdiff

# Default branch name
git config --global init.defaultBranch main

# Pull behavior
git config --global pull.rebase false        # merge on pull (default)
git config --global pull.rebase true         # rebase on pull
git config --global pull.ff only             # fail if not fast-forward

# Push behavior
git config --global push.default current     # push current branch to same-name remote branch

# Credential helpers
git config --global credential.helper osxkeychain      # macOS
git config --global credential.helper manager-core      # Windows (Git Credential Manager)
git config --global credential.helper 'cache --timeout=3600'  # Linux (in-memory, 1hr)

# Misc
git config --global core.autocrlf input      # normalize CRLF to LF on commit (macOS/Linux)
git config --global core.autocrlf true       # normalize on Windows
git config --global rerere.enabled true      # enable reuse-recorded-resolution
git config --global fetch.prune true         # auto-prune stale remote refs on fetch

# List all config
git config --list
git config --list --show-origin              # show where each setting comes from
git config --global -e                       # open global config in editor
```

---

## Init and Clone

```bash
git init                                     # init repo in current directory
git init <dir>                               # init in new directory
git init --bare <dir.git>                    # init bare repo (no working tree — for remotes)

git clone <url>                              # clone repo
git clone <url> <dir>                        # clone into named directory
git clone --depth 1 <url>                    # shallow clone — latest commit only
git clone --depth 1 --branch v2.0.0 <url>   # shallow clone of a specific tag
git clone --recurse-submodules <url>         # clone with all submodules initialized
git clone --no-checkout <url>                # clone without materializing files
git clone --filter=blob:none <url>           # partial clone — defer blob download
git clone --filter=blob:none --no-checkout <url>  # combine for sparse + partial
git clone --mirror <url>                     # full mirror including all refs
git clone --single-branch --branch main <url>     # only fetch one branch
```

---

## Staging and Committing

```bash
# Status
git status                                   # show working tree status (verbose)
git status -s                                # short format: M=modified, A=added, ??=untracked

# Staging
git add <file>                               # stage specific file
git add .                                    # stage all changes in current directory
git add -A                                   # stage all changes (including deletions) everywhere
git add -p                                   # interactively select hunks to stage
git add -u                                   # stage modified + deleted (not untracked)
git add -N <file>                            # mark untracked file as "intent to add"

# Committing
git commit -m "message"                      # commit staged changes
git commit -am "message"                     # stage all tracked files and commit
git commit --amend -m "new message"          # rewrite last commit message (local only!)
git commit --amend --no-edit                 # add staged changes to last commit, keep message
git commit --allow-empty -m "trigger CI"     # commit with no changes

# File management
git rm <file>                                # remove file from working tree and stage deletion
git rm --cached <file>                       # remove from index only (keep on disk — useful for .gitignore fixes)
git mv <old> <new>                           # rename/move file and stage the change

# Discard changes
git restore <file>                           # discard working tree changes (since Git 2.23)
git restore --staged <file>                  # unstage (keep working tree changes)
git restore --staged --worktree <file>       # unstage and discard working tree changes
git checkout -- <file>                       # legacy syntax for restore
git reset HEAD <file>                        # legacy syntax to unstage
```

---

## Branching

```bash
# Listing
git branch                                   # list local branches
git branch -a                                # list local and remote-tracking branches
git branch -r                                # list remote-tracking branches
git branch -v                                # list branches with last commit
git branch -vv                               # list branches with upstream info
git branch --merged                          # branches merged into HEAD
git branch --no-merged                       # branches NOT merged into HEAD

# Creating
git branch <name>                            # create branch at HEAD
git branch <name> <sha>                      # create branch at specific commit
git branch <name> <tag>                      # create branch at tag

# Switching
git checkout <branch>                        # switch to branch
git checkout -b <branch>                     # create and switch
git checkout -b <branch> origin/<branch>     # create local branch tracking remote
git switch <branch>                          # switch (modern — Git 2.23+)
git switch -c <branch>                       # create and switch (modern)
git switch -c <branch> --track origin/<branch>  # create with explicit upstream

# Renaming
git branch -m <old> <new>                    # rename branch
git branch -m <new>                          # rename current branch

# Deleting
git branch -d <name>                         # delete merged branch (safe)
git branch -D <name>                         # force delete (even if unmerged)
git push origin --delete <name>              # delete remote branch

# Upstream / tracking
git branch --set-upstream-to=origin/<branch> # set upstream for current branch
git branch -u origin/<branch>                # shorthand

# Merging
git merge <branch>                           # merge branch into current
git merge --no-ff <branch>                   # force merge commit (no fast-forward)
git merge --squash <branch>                  # squash all commits into one staged change
git merge --abort                            # abort in-progress merge
git merge -X ours <branch>                   # prefer current branch on conflict
git merge -X theirs <branch>                 # prefer incoming branch on conflict
```

---

## Remote Operations

```bash
# Remote management
git remote -v                                # show remotes with URLs
git remote add origin <url>                  # add remote named origin
git remote add upstream <url>                # add upstream (for forks)
git remote set-url origin <url>              # change remote URL
git remote rename origin upstream            # rename remote
git remote remove origin                     # delete remote

# Fetch
git fetch                                    # fetch all remotes
git fetch origin                             # fetch from origin
git fetch origin <branch>                    # fetch specific branch
git fetch --all                              # fetch from all remotes
git fetch --prune                            # remove stale remote-tracking refs
git fetch --tags                             # fetch all tags

# Pull
git pull                                     # fetch + merge current branch
git pull --rebase                            # fetch + rebase
git pull --ff-only                           # fail if not fast-forwardable
git pull origin <branch>                     # pull specific branch

# Push
git push origin <branch>                     # push branch to remote
git push -u origin <branch>                  # push and set upstream tracking
git push --force-with-lease                  # safe force push (fails if remote moved since last fetch)
git push --force                             # force push — DANGEROUS on shared branches
git push origin --delete <branch>            # delete remote branch
git push origin --tags                       # push all tags
git push origin <tag>                        # push specific tag
git push origin --delete <tag>               # delete remote tag
git push origin HEAD                         # push current branch (regardless of name)
```

---

## History Inspection

```bash
# Basic log
git log                                      # full log
git log --oneline                            # one line per commit
git log --oneline --graph --decorate         # visual branch graph
git log --oneline --graph --decorate --all   # all refs
git log -n 5                                 # last 5 commits
git log -5                                   # shorthand for last 5

# Filtering
git log --author="Alice"                     # filter by author name or email
git log --since="2 weeks ago"                # relative date filter
git log --until="2024-01-01"                 # commits before date
git log --grep="payment"                     # filter by commit message keyword
git log -S "function_name"                   # pickaxe: commits adding/removing string
git log -G "regex_pattern"                   # commits where diff matches regex
git log --merges                             # merge commits only
git log --no-merges                          # exclude merge commits

# File history
git log -p <file>                            # patches (diffs) for a file
git log --follow -p <file>                   # follow through renames
git log --stat <file>                        # changed files summary per commit
git log --diff-filter=D -- <file>            # commits where file was deleted

# Formatting
git log --format="%H %an %ae %s"             # custom format
git log --format="%h %ad %s" --date=short    # short SHA, date, subject
git log --pretty=tformat:"%C(yellow)%h%Creset %s %C(green)%ar%Creset"  # colored

# Diff
git diff                                     # working tree vs index
git diff --staged                            # index vs HEAD
git diff HEAD                                # working tree vs HEAD
git diff <branch1>..<branch2>                # diff between branch tips
git diff <branch1>...<branch2>               # diff from common ancestor to branch2
git diff <sha1> <sha2>                       # diff between two commits
git diff --stat                              # changed files summary only
git diff --name-only                         # only file names
git diff --name-status                       # file names + status (A/M/D)
git diff -w                                  # ignore whitespace changes
git diff --word-diff                         # word-level diff

# Show
git show <sha>                               # commit details and diff
git show <branch>:<file>                     # file content in another branch
git show HEAD~2:<file>                       # file content 2 commits ago

# Blame
git blame <file>                             # who last modified each line
git blame -L 10,20 <file>                    # blame specific line range
git blame -C <file>                          # detect copy-paste between files
git blame -w <file>                          # ignore whitespace when blaming

# Misc
git shortlog -sn                             # commit count by author, sorted
git log --graph --all --oneline              # full repo history graph
```

---

## Rebase and Cherry-Pick

```bash
# Rebase
git rebase <branch>                          # rebase current branch onto branch
git rebase origin/main                       # sync with remote main
git rebase -i HEAD~5                         # interactive rebase of last 5 commits
git rebase -i <sha>                          # interactive from (not including) commit
git rebase --continue                        # continue after resolving conflict
git rebase --abort                           # abort rebase, return to pre-rebase state
git rebase --skip                            # skip current conflicting commit
git rebase --onto <newbase> <oldbase> <branch>  # transplant branch to new base

# Interactive rebase commands (in editor):
# pick   = use commit as-is
# reword = use commit, edit message only
# edit   = use commit, pause to amend files
# squash = meld into previous commit, combine messages
# fixup  = meld into previous commit, discard this message
# drop   = remove commit entirely
# exec   = run shell command at this point

# Cherry-pick
git cherry-pick <sha>                        # apply commit to current branch
git cherry-pick <sha1>..<sha2>               # apply range (exclusive of sha1)
git cherry-pick <sha1>^..<sha2>              # apply range (inclusive of sha1)
git cherry-pick --no-commit <sha>            # apply changes without committing
git cherry-pick -x <sha>                     # append "cherry-picked from" note to message
git cherry-pick --abort                      # abort cherry-pick
git cherry-pick --continue                   # continue after resolving conflict
```

---

## Stash

```bash
git stash                                    # stash working tree and index changes
git stash push -m "description"              # stash with name
git stash push -u                            # include untracked files
git stash push -a                            # include untracked + ignored files
git stash push -p                            # interactively select hunks to stash
git stash push -- <file>                     # stash specific file only

git stash list                               # list all stashes
git stash show                               # show latest stash diff summary
git stash show -p                            # show latest stash full diff
git stash show stash@{2} -p                  # show specific stash full diff

git stash apply                              # apply latest stash (keep stash in list)
git stash apply stash@{2}                    # apply specific stash
git stash pop                                # apply latest stash and remove it
git stash pop stash@{1}                      # pop specific stash

git stash drop                               # delete latest stash
git stash drop stash@{1}                     # delete specific stash
git stash clear                              # delete all stashes

git stash branch <branch>                    # create branch from stash and apply it
```

---

## Tags

```bash
git tag                                      # list all tags
git tag -l "v1.*"                            # list tags matching pattern
git tag -n                                   # list tags with annotation messages

git tag <name>                               # create lightweight tag at HEAD
git tag <name> <sha>                         # create lightweight tag at commit
git tag -a <name> -m "message"               # create annotated tag at HEAD
git tag -a <name> <sha> -m "message"         # annotated tag at specific commit
git tag -s <name> -m "message"               # GPG-signed annotated tag

git push origin <tag>                        # push specific tag
git push origin --tags                       # push all tags
git push origin --follow-tags                # push commits AND their annotated tags

git push origin --delete <tag>               # delete remote tag
git tag -d <name>                            # delete local tag

git checkout <tag>                           # detach HEAD to tag (read-only view)
git checkout -b <branch> <tag>               # create branch from tag
git describe --tags                          # describe current commit relative to nearest tag
git describe --tags --abbrev=0               # show nearest tag only
```

---

## Undo and Reset

```bash
# Unstage
git restore --staged <file>                  # unstage file (keep working tree)
git reset HEAD <file>                        # legacy unstage syntax

# Reset branch pointer
git reset --soft HEAD~1                      # undo last commit, keep staged
git reset --mixed HEAD~1                     # undo last commit, keep in working tree (default)
git reset --hard HEAD~1                      # undo last commit, DISCARD all changes
git reset --hard <sha>                       # reset to specific commit
git reset --hard origin/main                 # reset to match remote main

# Revert (safe for shared branches)
git revert <sha>                             # create new commit reversing a commit
git revert HEAD                              # revert last commit
git revert HEAD~3..HEAD                      # revert last 3 commits
git revert --no-commit <sha>                 # stage revert without committing

# Clean
git clean -n                                 # dry run — show what would be deleted
git clean -f                                 # delete untracked files
git clean -fd                                # delete untracked files and directories
git clean -fdx                               # also delete ignored files
git clean -fdi                               # interactive mode
```

---

## Bisect

```bash
git bisect start                             # begin binary search
git bisect bad                               # mark current commit as bad (broken)
git bisect bad HEAD                          # explicit — same as above
git bisect good <sha>                        # mark a known-good commit
git bisect good v2.0.0                       # use a tag as good point

# After git checks out midpoint: test, then mark:
git bisect bad                               # this revision is broken
git bisect good                              # this revision works
git bisect skip                              # skip this commit (e.g. broken build)
git bisect skip v2.1.0..v2.1.3              # skip a range

git bisect reset                             # exit bisect, return to original HEAD
git bisect log                               # show bisect log (reproducible)

# Automated bisect (script exits 0=good, non-zero=bad, 125=skip)
git bisect run ./ci/test.sh
git bisect run make test
```

---

## Reflog

```bash
git reflog                                   # show HEAD movement history (last 90 days)
git reflog show <branch>                     # show branch tip history
git reflog show --date=iso                   # show with timestamps
git reflog --all                             # show all refs

# Recovery
git checkout HEAD@{3}                        # go to state 3 HEAD moves ago
git reset --hard HEAD@{1}                    # reset to previous HEAD position
git branch recover HEAD@{5}                  # create branch from old HEAD position

# Expire
git reflog expire --expire=now --all         # expire all reflog entries immediately
```

---

## Submodules

```bash
# Adding
git submodule add <url> <path>               # add submodule
git submodule add -b main <url> <path>       # track specific branch

# After cloning a repo that has submodules
git submodule init                           # register submodule paths
git submodule update                         # checkout pinned commits
git submodule update --init                  # init + checkout
git submodule update --init --recursive      # full init + update, all levels

# Updating
git submodule update --remote                # update to upstream HEAD of tracked branch
git submodule update --remote --merge        # update and merge into local submodule
git submodule update --remote vendor/lib     # update specific submodule only
git submodule foreach git pull origin main   # pull all submodules

# Status and info
git submodule status                         # show submodule states
git submodule summary                        # show summary of changes

# Removing a submodule
git submodule deinit -f <path>               # de-register submodule
rm -rf .git/modules/<path>                   # remove git tracking
git rm -f <path>                             # remove from working tree and index

# Clone with submodules
git clone --recurse-submodules <url>
git clone --recurse-submodules --shallow-submodules <url>  # shallow submodule clones
```

---

## Worktrees

Worktrees let you check out multiple branches simultaneously without stashing or cloning.

```bash
git worktree add ../hotfix-1.2 hotfix/1.2   # create worktree for existing branch
git worktree add -b new-feature ../feature  # create worktree with new branch
git worktree list                            # list all worktrees
git worktree remove ../hotfix-1.2           # remove worktree
git worktree prune                           # clean up stale worktree references

# Typical workflow: fix a hotfix without leaving your feature branch
git worktree add ../hotfix main
cd ../hotfix
# Make changes, commit, push
cd -
git worktree remove ../hotfix
```

> [!TIP]
> Worktrees share the same `.git` directory. You cannot check out the same branch in two worktrees simultaneously.

---

## Sparse Checkout

```bash
# Setup for monorepo
git clone --filter=blob:none --no-checkout <url>
cd repo
git sparse-checkout init --cone              # cone mode: faster, directory-prefix based
git sparse-checkout set services/api lib/shared
git checkout main

# Manage paths
git sparse-checkout list                     # show declared paths
git sparse-checkout add services/worker      # add more paths
git sparse-checkout set services/api         # replace with new set of paths
git sparse-checkout disable                  # revert to full checkout

# Non-cone mode (supports glob patterns, slower)
git sparse-checkout init
git sparse-checkout set '/*' '!/docs'        # everything except docs/
```

---

## GPG and SSH Signing

```bash
# GPG setup
gpg --full-generate-key
gpg --list-secret-keys --keyid-format LONG
git config --global user.signingkey <KEY_ID>
git config --global commit.gpgsign true
git commit -S -m "signed commit"
git tag -s v1.0.0 -m "release"
git verify-commit <sha>
git log --show-signature

# SSH signing (Git 2.34+)
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_ed25519.pub
git config --global commit.gpgsign true
```

---

## SSH Setup

```bash
# Generate key
ssh-keygen -t ed25519 -C "you@example.com" -f ~/.ssh/github_ed25519

# Add to agent
ssh-add ~/.ssh/github_ed25519

# ~/.ssh/config
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/github_ed25519
  AddKeysToAgent yes

# Test
ssh -T git@github.com

# Switch remote from HTTPS to SSH
git remote set-url origin git@github.com:org/repo.git
```

---

## Large File Handling

```bash
# Find large objects in history
git rev-list --objects --all | \
  git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | \
  awk '/^blob/ { print $3, $4 }' | sort -rn | head -20

# Find the commit that added a specific file
git log --all --full-history -- path/to/large-file

# Remove file from all history (git-filter-repo — modern approach)
pip install git-filter-repo
git filter-repo --path path/to/large-file --invert-paths

# Git LFS
git lfs install                              # install LFS hooks
git lfs track "*.psd"                        # track file type with LFS
git lfs track "*.bin"
git add .gitattributes
git lfs status                               # show LFS tracked files
git lfs ls-files                             # list all LFS files
git lfs fetch --all                          # fetch all LFS objects
git lfs pull                                 # fetch + checkout LFS files
```

---

## Repository Maintenance

```bash
# Object database
git fsck                                     # check integrity
git fsck --lost-found                        # write dangling objects to .git/lost-found/
git count-objects -vH                        # count objects, show disk usage

# Garbage collection
git gc                                       # pack loose objects, expire old reflog
git gc --aggressive                          # deeper compression (slower, for archival)
git gc --prune=now                           # prune unreachable objects immediately

# Background maintenance (Git 2.29+)
git maintenance start                        # set up automatic background maintenance
git maintenance stop
git maintenance run                          # run all maintenance tasks now
git maintenance run --task=gc                # run specific task

# Pack optimization
git repack -a -d                             # repack all, delete redundant pack files
git repack -a -d -f --delta-depth=250 --window=250  # aggressive repack
```

---

## Useful One-Liners

```bash
# Undo last commit, keep changes staged
git reset --soft HEAD~1

# See what's in the stash
git stash show -p

# List all branches that contain a specific commit
git branch --contains <sha>

# Find which branch a commit is on
git branch --all --contains <sha>

# Show commits that are in branch-A but not in branch-B
git log branch-B..branch-A --oneline

# Show diff between local and remote
git diff origin/main...HEAD

# Delete all local branches that are already merged to main
git branch --merged main | grep -v "^\* main$\|^  main$" | xargs git branch -d

# Squash last N commits into one (N=3 here)
git reset --soft HEAD~3 && git commit -m "squashed commit"

# Show the root commit
git rev-list --max-parents=0 HEAD

# Restore a deleted file from a specific commit
git checkout <sha> -- path/to/deleted-file.txt

# Find commits that touched a specific function
git log -L :function_name:file.py

# Export current tree as tar.gz
git archive --format=tar.gz HEAD > snapshot.tar.gz

# Count lines in the current tree (excluding binary)
git ls-files | xargs wc -l
```

---

## Aliases (Recommended ~/.gitconfig)

```ini
[alias]
    co = checkout
    sw = switch
    br = branch
    ci = commit
    st = status
    lg = log --oneline --graph --decorate --all
    ll = log --oneline --graph --decorate -20
    ld = log --oneline --graph --decorate --all --date=short --format='%C(yellow)%h%Creset %C(green)%ad%Creset %s %C(blue)%an%Creset'
    undo = reset --soft HEAD~1
    unstage = restore --staged
    discard = restore
    wip = commit -am 'WIP: checkpoint'
    aliases = config --get-regexp alias
    whois = log -i -1 --pretty="format:%an <%ae>%n" --author
    conflicts = diff --name-only --diff-filter=U
    recent = branch --sort=-committerdate --format='%(refname:short) %(committerdate:relative)'
    merged = branch --merged HEAD
    root = rev-parse --show-toplevel
    pick = cherry-pick
    rb = rebase
    rbi = rebase -i
    rbo = rebase --onto
```

---

## Log Format Reference

```bash
# Format placeholders
# %H  - full commit hash
# %h  - abbreviated commit hash
# %T  - full tree hash
# %t  - abbreviated tree hash
# %P  - parent hashes
# %an - author name
# %ae - author email
# %ad - author date
# %ar - author date, relative
# %cn - committer name
# %s  - subject (first line of message)
# %b  - body
# %D  - ref names (like --decorate)

# Colorized oneline graph (good for .gitconfig alias)
git log --graph --all \
  --pretty=format:'%C(yellow)%h%Creset %C(cyan)%d%Creset %s %C(dim white)— %an, %ar%Creset'
```
# Content from CheatSheet_Git_GitHub.pdf

## Page 1

Shubham
TrainWith
Shubham
TrainWith
Git & GitHub Cheatsheet
Cheatsheet for DevOps Engineers
Installation & Account Setup :
Git Installation: Use this Blog for Git Installation on different OS
Setting Up a GitHub Account : Read this blog for creating a Github Account
# Git Commands:
Repository Management:
Command
Description
git init
Initialize a new repository
git clone <repo>
Clone an existing repository
git remote -v
View remote repository details
git remote add origin <url>
Link local repo to remote
Adding and Committing:
Command
Description
git add <file>
Stage changes for commit
git add .
Stage all changes
git commit -m "message"
Commit changes with a message
git commit --amend
Edit the last commit
Shubham
TrainWith


---

## Page 2

Shubham
TrainWith
Branching and Merging:
Command
Description
git branch
List branches
git branch <branch>
Create a new branch
git checkout -b <branch>
Create and switch to a new branch
git merge <branch>
Merge a branch into current branch
git branch -d <branch>
Delete a branch
git checkout <branch>
Switch to a branch
Log and History:
Command
Description
git log
View commit history
git log --oneline
View commit history in one line
git diff
View unstaged changes
git diff HEAD
Compare working directory to HEAD
Undo Changes:
Command
Description
git reset <file>
Unstages a file. Changes remain in the working directory.
git restore <file>
Restores a file to its last committed state.
git reset --hard <commit>
Resets the current branch to the specified commit and
discards all local changes.
git revert <commit>
Create a new commit that undoes a previous commit
Shubham
TrainWith


---

## Page 3

Shubham
TrainWith
Pushing and Pulling:
Command
Description
git push origin <branch>
Push changes to the remote repository
git pull origin <branch>
Pull changes from the remote repository
Log Git Config Commands:
Command
Description
git config --global user.name "<name>"
Sets the global username for Git commits.
git config --global user.email "<email>"
Sets the global email for Git commits.
git config --list
Displays the current Git configuration (user
details, editor, etc.).
Git Status Command:
Command
Description
git status
Shows the current status of the working
directory and staging area. Indicates tracked,
modified, untracked, or staged files.
Git Fetch Command:
Command
Description
git fetch
Downloads commits, files, and references
from a remote repository without merging
them into the local branch.
Shubham
TrainWith


---

## Page 4

Shubham
TrainWith
Command
Description
git stash
Save changes to a stash
git stash list
List all stashes
git stash apply
Apply the last stash
git stash drop
Delete the last stash
Command
Description
git rebase <branch_name>
Reapplies commits on top of another base branch. It
rewrites history, so avoid using it on shared branches.
git rebase -i <commit_hash>
Allows you to rebase interactively from a
specific commit.
git rebase --abort
Aborts the rebase process and returns to the
state before starting the rebase.
git rebase --continue
Continues the rebase after resolving conflicts.
git rebase --skip
Skips the current commit during rebase.
git cherry-pick <commit_hash>
Applies a specific commit from another
branch to the current branch.
# Advanced Commands 
Stashing:
Rebase and Cherry-pick:
Shubham
TrainWith


---

## Page 5

Shubham
TrainWith
Command
Description
git tag <tag>
Create a lightweight tag
git tag -a <tag> -m "msg"
Create an annotated tag
git push origin --tags
Push tags to remote
Command
Description
git bisect start
Begins the binary search to find the commit
that introduced a bug.
git bisect bad
Marks the current commit as bad (contains
the bug).
git bisect good <commit>
Marks a known good commit (does not
contain the bug) to start the bisecting
process.
git bisect reset
Ends the bisect process and resets the
repository to the original state.
Tagging:
Git Bisect Command (Debugging to Find Bad Commits):
Shubham
TrainWith
Shubham
TrainWith


---

## Page 6

Shubham
TrainWith
Command
Description
git blame <file>
Shows who modified each line of the file
git shortlog
Summarizes contributions by author
git log --graph
Visualize branch history
git show <commit>
Displays details of a specific commit
git diff --staged
Show differences between staged changes
and the last commit
Collaboration Commands:
# GitHub Push Methods
1. SSH Method
1. Generate an SSH key:
using : `ssh-keygen`
2. Copy the SSH key:
using : ` cat ~/.ssh/<key_name>.pub`
3. Navigate to GitHub > Settings > SSH and GPG keys > New SSH key.
4. Paste the key and save.
5. Verify the SSH connection:
using : `ssh -T git@github.com`
6. Now clone the repo using ssh and do whatever you want and add &
commit the changes
7. Push code:
using : ` git push origin main`


---

## Page 7

Shubham
TrainWith
2. HTTPS Method
1. Firstly Generate a Personal Access Token
2. Use HTTPS URL for your repository:
`git remote set-url origin
https://<Your_PAT>@github.com/<username>/<repository>.git`
3. Add and commit the changes
4. Push code:
`git push origin main/master`
# Helpful GitHub Tips :
Create Pull Request :
1. Push <Your_branch> branch to GitHub.
2. Open the repository on GitHub.
3. Go to the "Pull Requests" tab and click "New Pull Request."
4. Select branches and create PR.
GitHub Fork and Sync Workflow :
1. Fork a Repository:
a. Go to the repository on GitHub and click on Fork.
2. Clone the Fork:
a. `git clone https://github.com/your-username/repo-name.git`
3. Sync Changes from Upstream:
a. git remote add upstream https://github.com/original-
owner/repo-name.git
b. git fetch upstream
c. git merge upstream/main


---

## Page 8

Shubham
TrainWith
Git Aliases :
Speed up your workflow by creating aliases:
1. git config --global alias.co checkout
2. git config --global alias.br branch
3. git config --global alias.ci commit
# GitHub Actions:
• Significance: Automates workflows like testing, building, and deploying code.
• Example:
Description: Runs tests on every push or pull request to the main branch.
# References:
- Git Documentation
- GitHub Docs
Shubham
TrainWith


---

