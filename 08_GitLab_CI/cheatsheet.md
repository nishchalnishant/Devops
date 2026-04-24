# Content from CheatSheet_GitLab.pdf

## Page 1

Shubham
TrainWith
GitLab_CheatSheet
Cheatsheet for DevOps Engineers
Repositories:
Command
Description
git fetch <remote>
Fetch changes from the remote but do not update
tracking branches.
git fetch --prune <remote>
Delete remote refs removed from the remote repository.
git remote -v
List all remote repositories
git remote set-url origin <new-
repository>
git remote set-url origin <new-repository>
Synchronizing Repositories:
Command
Description
git init
Initialize a new repository
git clone <repository>
Clone a repository to your local machine.
git remote add origin <repository>
Add a remote repository.
git push -u origin <branch>
Push changes to a branch.
git pull
Pull changes from a remote repository.
git status
Check the status of your local repository.
git log
View commit history.
Shubham
TrainWith


---

## Page 2

Command
Description
git branch
List all branches
git branch -a
Show all branches (including remote).
git branch <branch>
Create a new branch.
git checkout <branch>
Switch to a different branch.
git merge <branch>
Merge a branch into the current branch.
git branch -d <branch>
Delete a branch.
git branch -m <old-branch> <new-branch>
Rename a branch.
Shubham
TrainWith
Branches:
Commits:
Command
Description
git add <file>
Add a file to the staging area.
git commit -m "<message>"
Commit changes with a message.
git commit --amend
Amend the last commit.
git reset <file>
Unstage a file.
git reset --hard
Discard all changes.
git diff <file>
Show changes between commits.
git diff --staged <file>
Show changes between the staging area and the
repository.
git blame <file>
Show who made changes to a file.
Shubham
TrainWith


---

## Page 3

Tagging Commits:
Command
Description
git tag
List all tags.
git tag <name> <commit sha>
Create a tag for a specific commit.
git tag -a <name> <commit sha>
Create an annotated tag.
git tag -d <name>
Remove a tag from the local repository.
Stashing Changes:
Command
Description
git stash
Stash current changes.
git stash pop
Apply and clear the latest stash
git stash apply
Apply stashed changes without clearing them.
git stash drop
Delete a specific stash.
Merge Requests:
Command
Description
git merge --no-ff <branch>
Merge with a new commit.
git cherry-pick <commit>
Apply a specific commit to the current branch.
git rebase <branch>
Rebase the current branch onto another.
git rebase -i <commit>
Interactive rebase.
Shubham
TrainWith


---

## Page 4

Issues:
Command
Description
git commit -m "Fixes #<issue-number>"
Link a commit to an issue.
git commit -m "Closes #<issue-number>"
Close an issue with a commit.
git commit -m "Refs #<issue-number>"
Reference an issue with a commit.
git issue list
List all issues
git issue show <issue-number>
Show details of an issue
git issue create
Create a new issue
git issue edit <issue-number>
Edit an issue
git issue close <issue-number>
Close an issue
Wiki Management:
Command
Description
git wiki list
List all wiki pages.
git wiki create <page>
Create a new wiki page.
git wiki edit <page>
Edit a wiki page.
git wiki delete <page>
Delete a wiki page.
git wiki show <page>
Show the contents of a wiki page
Shubham
TrainWith


---

## Page 5

CI/CD:
Command
Description
.gitlab-ci.yml
Configuration file for CI/CD.
gitlab-runner register
Register a runner.
gitlab-runner run
Run a runner.
gitlab-runner exec
Execute a job locally.
gitlab-runner verify
Verify runner configuration.
gitlab-runner uninstall
Uninstall a runner.
gitlab-runner list
List all runners
Groups:
Command
Description
git group list
List all groups
git group show <group>
Show details of a group
git group create <group> 
Create a new group
git group edit <group>
Edit a group
git group delete <group>
 Delete a group
Shubham
TrainWith


---

## Page 6

Settings:
Command
Description
git config --global user.name "<name>"
Set your name
git config --global user.email "<email>" 
Set your email
git config --global core.editor "<editor>" 
Set your default editor
git config --global color.ui true
Enable colored output
git config --global alias.<alias-name> "<command>"
Create an alias for a command
Best Practices:
Shubham
TrainWith
Use meaningful branch names (e.g., feature/login, bugfix/payment-issue).
1.
Write concise and descriptive commit messages.
2.
Regularly pull from the main branch to avoid merge conflicts.
3.
Use ‘.gitignore’ to manage ignored files efficiently.
4.
Leverage CI/CD pipelines for automated testing and deployment.
5.


---

## Page 7

Shubham
TrainWith
stages:
  - build
  - test
  - deploy
build:
  stage: build
  script:
    - echo "Building the application..."
unit_test:
  stage: test
  script:
    - echo "Running unit tests..."
deploy:
  stage: deploy
  script:
    - echo "Deploying the application..."
Example: .gitlab-ci.yml File
Common Errors and Troubleshooting:
Authentication Error:
1.
Ensure SSH keys or access tokens are correctly configured.
Merge Conflicts:
2.
Use git merge --abort to cancel a merge.
Resolve conflicts manually, then git add and git commit.
Detached HEAD:
3.
Use git checkout <branch> to return to a branch.
Security and Permissions:
Set up personal access tokens for secure authentication.
Use role-based access control (RBAC) for managing team permissions.


---

