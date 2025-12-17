# Git Usage Guide - Everyday Workflow

This guide covers the essential Git commands and workflows you'll use daily when working on projects.

## Table of Contents
- [Initial Setup](#initial-setup)
- [Daily Workflow](#daily-workflow)
- [Checking Status](#checking-status)
- [Committing Changes](#committing-changes)
- [Pushing to GitHub](#pushing-to-github)
- [Pulling Updates](#pulling-updates)
- [Branching](#branching)
- [Pull Requests](#pull-requests)
- [Common Commands Cheat Sheet](#common-commands-cheat-sheet)
- [Troubleshooting](#troubleshooting)

---

## Initial Setup

### First Time Setup (One-time per machine)

```bash
# Configure your identity
git config --global user.name "Your Name"
git config --global user.email "your_email@example.com"
```

### Initialize a Repository

```bash
# If starting a new project
git init

# If cloning an existing repository
git clone https://github.com/username/repository.git
```

### Connect Local Repository to GitHub

```bash
# Add remote repository (if not already added)
git remote add origin https://github.com/username/repository.git

# Or if using SSH
git remote add origin git@github.com:username/repository.git

# Verify remote is set correctly
git remote -v

# Update existing remote URL (if needed)
git remote set-url origin https://github.com/username/repository.git
```

### First Push

```bash
# Stage all files
git add .

# Make initial commit
git commit -m "Initial commit"

# Push to GitHub (first time)
git branch -M main
git push -u origin main
```

---

## Daily Workflow

The typical day-to-day workflow follows this pattern:

1. **Check what changed** → `git status`, `git diff`
2. **Stage your changes** → `git add .` or `git add <file>`
3. **Commit your changes** → `git commit -m "message"`
4. **Push to GitHub** → `git push`

---

## Checking Status

### See What Files Changed

```bash
# See modified, staged, and untracked files
git status

# See detailed changes in modified files (not yet staged)
git diff

# See changes in staged files
git diff --staged

# See commit history
git log --oneline --graph --decorate --all
```

---

## Committing Changes

### Stage Files

```bash
# Stage all changed files
git add .

# Stage specific file(s)
git add main_get_jobs.py
git add file1.py file2.py

# Stage all files in a directory
git add job_search/

# Unstage a file (if you staged it by mistake)
git reset HEAD <file>
```

### Commit Changes

```bash
# Commit with a message
git commit -m "Add new job filtering feature"

# Commit with a detailed message
git commit -m "Add new job filtering feature

- Implemented salary range filter
- Added location-based filtering
- Updated logging for better debugging"
```

**Good Commit Messages:**
- Be descriptive and specific
- Use present tense ("Add feature" not "Added feature")
- Keep first line under 50 characters if possible
- Add details in body if needed

**Examples:**
- ✅ `"Fix bug in job search CSV parsing"`
- ✅ `"Update logging configuration in main_get_jobs.py"`
- ✅ `"Add error handling for missing job titles"`
- ❌ `"fix stuff"`
- ❌ `"updates"`

---

## Pushing to GitHub

### Push Your Commits

```bash
# Push to main branch (after first push)
git push

# Push to main branch (first time, sets upstream)
git push -u origin main

# Push to a different branch
git push -u origin feature-branch-name
```

### Force Push (Use with Caution!)

```bash
# Only use if you've rewritten history (amended commits, rebased, etc.)
# ⚠️ WARNING: This overwrites remote history
git push --force

# Safer alternative (fails if remote has changes you don't have)
git push --force-with-lease
```

---

## Pulling Updates

### Get Latest Changes from GitHub

```bash
# Pull latest changes (fetch + merge)
git pull

# Pull from specific branch
git pull origin main

# Fetch changes without merging (inspect first)
git fetch
git merge origin/main
```

### Handling Merge Conflicts

If `git pull` results in conflicts:

1. Git will mark conflicted files
2. Open the files and look for conflict markers:
   ```
   <<<<<<< HEAD
   Your local changes
   =======
   Changes from remote
   >>>>>>> branch-name
   ```
3. Edit the file to resolve conflicts (remove markers, keep desired code)
4. Stage the resolved file:
   ```bash
   git add <resolved-file>
   ```
5. Complete the merge:
   ```bash
   git commit
   ```

---

## Branching

### Create and Switch to New Branch

```bash
# Create and switch to new branch
git checkout -b feature/job-filtering

# Or using newer syntax
git switch -c feature/job-filtering

# Switch to existing branch
git checkout main
git switch main

# List all branches
git branch

# List all branches (including remote)
git branch -a
```

### Work on a Branch

```bash
# Create branch
git checkout -b feature/new-feature

# Make changes, commit them
git add .
git commit -m "Add new feature"

# Push branch to GitHub
git push -u origin feature/new-feature
```

### Delete a Branch

```bash
# Delete local branch (after switching away from it)
git branch -d feature/old-feature

# Force delete (if branch has unmerged changes)
git branch -D feature/old-feature

# Delete remote branch
git push origin --delete feature/old-feature
```

---

## Pull Requests

### Creating a Pull Request

1. **Push your branch to GitHub:**
   ```bash
   git push -u origin feature/my-feature
   ```

2. **On GitHub:**
   - Go to your repository
   - You'll see a banner: "Compare & pull request"
   - Click it, add a description, and create the PR

3. **After PR is merged:**
   ```bash
   # Switch back to main
   git checkout main
   
   # Pull the merged changes
   git pull
   
   # Optionally delete local feature branch
   git branch -d feature/my-feature
   ```

---

## Common Commands Cheat Sheet

### Quick Reference

```bash
# Status & Inspection
git status              # See what changed
git diff                # See unstaged changes
git log --oneline       # See commit history

# Staging & Committing
git add .               # Stage all changes
git add <file>          # Stage specific file
git commit -m "msg"     # Commit with message

# Pushing & Pulling
git push                # Push to remote
git pull                # Pull from remote
git fetch               # Fetch without merging

# Branching
git checkout -b <name>  # Create & switch to branch
git checkout <name>     # Switch to branch
git branch              # List branches
git branch -d <name>    # Delete branch

# Remote Management
git remote -v           # List remotes
git remote set-url origin <url>  # Update remote URL
```

---

## Troubleshooting

### Common Issues

#### "Remote origin already exists"
```bash
# Update existing remote instead
git remote set-url origin <new-url>
```

#### "Permission denied (publickey)" (SSH)
```bash
# Switch to HTTPS instead
git remote set-url origin https://github.com/username/repo.git
```

#### "Push protection: secrets detected"
- Remove secrets from your code
- Use environment variables instead
- Update `.gitignore` to exclude secret files
- Remove secret from Git history:
  ```bash
  git rm --cached <file-with-secret>
  git commit --amend -m "Remove secret"
  git push --force
  ```

#### "Your branch is behind 'origin/main'"
```bash
# Pull latest changes first
git pull

# Resolve any conflicts, then push
git push
```

#### "Uncommitted changes" when switching branches
```bash
# Option 1: Commit your changes first
git add .
git commit -m "WIP: save current work"
git checkout other-branch

# Option 2: Stash changes temporarily
git stash
git checkout other-branch
# Later, get stashed changes back:
git stash pop
```

### Undoing Changes

```bash
# Unstage a file (keep changes in working directory)
git reset HEAD <file>

# Discard changes in working directory (⚠️ irreversible)
git checkout -- <file>
# Or newer syntax:
git restore <file>

# Undo last commit (keep changes staged)
git reset --soft HEAD~1

# Undo last commit (keep changes unstaged)
git reset HEAD~1

# Undo last commit (discard changes) ⚠️
git reset --hard HEAD~1
```

---

## Best Practices

1. **Commit Often**: Make small, logical commits rather than one large commit
2. **Write Good Messages**: Clear commit messages help you and others understand changes
3. **Pull Before Push**: Always `git pull` before `git push` to avoid conflicts
4. **Use Branches**: Create feature branches for new work, keep `main` stable
5. **Never Commit Secrets**: Use environment variables and `.gitignore`
6. **Review Before Committing**: Use `git diff` to review changes before committing

---

## Additional Resources

- [Git Official Documentation](https://git-scm.com/doc)
- [GitHub Guides](https://guides.github.com/)
- [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)

---

*Last updated: 2024*

