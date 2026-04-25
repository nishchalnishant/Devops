---
description: Git internals — objects, pack files, references, the index, and how Git operations work under the hood for senior engineers.
---

# Git Internals — How Git Works Under the Hood

## The Object Database

Git is fundamentally a **content-addressable key-value store**. Every piece of data (file, directory snapshot, commit) is stored as an object with a SHA-1 hash as its key.

```
.git/
├── objects/
│   ├── a7/
│   │   └── 3bc4d...  ← Object file (first 2 chars = directory)
│   ├── pack/         ← Packed objects (compressed)
│   └── info/
├── refs/
│   ├── heads/        ← Branch pointers
│   │   ├── main
│   │   └── feature/auth
│   ├── tags/
│   │   └── v2.0.0
│   └── remotes/
│       └── origin/
│           └── main
├── HEAD              ← Points to current branch (or commit in detached HEAD)
├── index             ← The staging area
└── config
```

***

## The Four Object Types

### 1. Blob — File Content

```bash
# Create a blob manually
echo "Hello World" | git hash-object -w --stdin
# 557db03de997c86a4a028e1ebd3a1ceb225be238

# Read it back
git cat-file -p 557db03
# Hello World
```

### 2. Tree — Directory Snapshot

```bash
git cat-file -p HEAD^{tree}
# 100644 blob a7b3c4... README.md
# 100644 blob f2d8e1... main.py
# 040000 tree 9c4b2a... src/
```

### 3. Commit — Snapshot + Metadata

```bash
git cat-file -p HEAD
# tree 9c4b2a...
# parent a73bc4...          ← Previous commit SHA
# author John Doe <john@example.com> 1714000000 +0530
# committer John Doe <john@example.com> 1714000000 +0530
#
# Add authentication module
```

### 4. Tag — Annotated Pointer to Commit

```bash
git cat-file -p v2.0.0
# object 9c4b2a...           ← The commit SHA
# type commit
# tag v2.0.0
# tagger John Doe <john@example.com>
#
# Release 2.0.0 — major refactor
```

***

## References — Pointers to Objects

Branches and tags are just files containing a SHA:

```bash
cat .git/refs/heads/main
# a73bc4d8f2e1c...   ← Just a SHA pointing to a commit

cat .git/HEAD
# ref: refs/heads/main   ← Symbolic ref (points to a branch)
# OR
# a73bc4d8f2e1c...       ← Detached HEAD (points to a commit directly)
```

```bash
# What HEAD → branch → commit chain looks like
HEAD → refs/heads/main → a73bc4d (commit) → tree → blobs
```

***

## The Index (Staging Area)

The index is a binary file (`.git/index`) that tracks the next commit. It is the "proposed next tree object."

```bash
# Show what's in the index
git ls-files --stage
# 100644 a7b3c4... 0	README.md
# 100644 f2d8e1... 0	main.py
# Stage number 0 = normal; 1,2,3 = conflict stages (during merge)

# Three-way comparison:
git diff          # Working tree vs Index
git diff --cached # Index vs HEAD (what will be committed)
git diff HEAD     # Working tree vs HEAD
```

***

## How `git merge` Works Internally

```
Before merge:
    A -- B -- C (main)
               \
                D -- E (feature)

Three-way merge finds the common ancestor (B):
  - Changes from B→C (on main)
  - Changes from B→E (on feature)
  - Applies both to create a new commit F

After merge:
    A -- B -- C -- F (main)
               \  /
                D -- E
```

**Fast-forward merge** (no divergence):
```
Before:
  A -- B -- C (main)
             \
              D -- E (feature)

After (main just moves its pointer to E):
  A -- B -- C -- D -- E (main, feature)
```

***

## How `git rebase` Works Internally

```
Before rebase:
    A -- B -- C (main)
         \
          D -- E (feature)

git checkout feature && git rebase main:
  1. Find common ancestor: B
  2. Save D and E as patches
  3. Reset feature to C (tip of main)
  4. Re-apply D as D' (new SHA! different parent)
  5. Re-apply E as E' (new SHA!)

After:
    A -- B -- C (main)
               \
                D' -- E' (feature)
```

> **Key Insight:** `git rebase` **rewrites history** — D and E get new SHAs. This is why rebasing shared branches is dangerous.

***

## Pack Files — Efficient Storage

Over time, Git compresses objects into pack files:

```bash
# Manually trigger garbage collection and pack
git gc --aggressive

# View pack file contents
git verify-pack -v .git/objects/pack/*.idx | sort -k3 -n | tail -10
# Shows objects sorted by size — useful for finding large historic files
```

***

## Useful Plumbing Commands

```bash
# Hash any content without writing
echo "test" | git hash-object --stdin

# Read any object
git cat-file -t SHA   # type: blob, tree, commit, tag
git cat-file -p SHA   # pretty-print content

# Find what object a reference points to
git rev-parse HEAD
git rev-parse HEAD~3   # 3 commits ago
git rev-parse main@{1} # Where main was 1 move ago (reflog)

# Show the tree at HEAD
git ls-tree -r HEAD --name-only

# Show all reachable commits
git rev-list HEAD

# Verify the object store
git fsck --full
```

***

## Logic & Trickiness Table

| Concept | Surface Understanding | Deep Understanding |
|:---|:---|:---|
| **Branch** | "A line of development" | A 41-byte file containing a SHA — extremely lightweight |
| **Commit SHA** | "A unique ID" | SHA-1 of: tree + parent SHA + author + timestamp + message |
| **`git stash`** | "Temporary save" | Creates two commits: one for the index, one for the working tree |
| **Rebase danger** | "Changes history" | New SHAs mean collaborators' branches now diverge from the rewritten history |
| **Merge vs Rebase** | Style preference | Merge preserves true history; Rebase creates a linear history but rewrites SHAs |
| **`git clone --depth 1`** | "Gets latest code" | Only downloads one commit; no object history — can't `git log` or `git bisect` |
