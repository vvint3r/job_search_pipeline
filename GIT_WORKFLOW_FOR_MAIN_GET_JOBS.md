# Git Workflow for Iterating on `main_get_jobs.py`

This guide provides a tailored Git workflow specifically for developing and iterating on your job search pipeline, particularly when working on `main_get_jobs.py`.

## Quick Start: Daily Iteration Workflow

When you're actively developing and testing changes to `main_get_jobs.py`:

```bash
# 1. Check what you've changed
git status
git diff main_get_jobs.py

# 2. Test your changes
./run_get_jobs.sh
# or
python3 main_get_jobs.py

# 3. If it works, commit
git add main_get_jobs.py
git commit -m "Improve error handling in pipeline orchestration"

# 4. Push when ready
git push
```

---

## Recommended Workflow Patterns

### Pattern 1: Feature Branch for Significant Changes

Use this when making substantial changes or new features:

```bash
# Create a feature branch
git checkout -b feature/improve-pipeline-logging

# Make your changes to main_get_jobs.py
# ... edit the file ...

# Test your changes
./run_get_jobs.sh

# Commit
git add main_get_jobs.py
git commit -m "Add detailed logging for each pipeline stage"

# Push branch
git push -u origin feature/improve-pipeline-logging

# Create Pull Request on GitHub (optional, for review)
# After merging, switch back to main
git checkout main
git pull
```

### Pattern 2: Quick Iterations on Main Branch

For small, quick fixes and iterations:

```bash
# Make small changes
# ... edit main_get_jobs.py ...

# Test immediately
python3 main_get_jobs.py

# If it works, commit and push
git add main_get_jobs.py
git commit -m "Fix CSV file path handling"
git push
```

### Pattern 3: Experimental Changes (WIP)

For trying things out without committing broken code:

```bash
# Make experimental changes
# ... edit main_get_jobs.py ...

# Test (if it breaks, you can easily discard)
python3 main_get_jobs.py

# If it works, commit
git add main_get_jobs.py
git commit -m "WIP: Experiment with async pipeline execution"

# If it doesn't work, discard changes
git checkout -- main_get_jobs.py
```

---

## Workflow for Different Types of Changes

### Small Bug Fixes

```bash
# 1. Fix the bug in main_get_jobs.py
# 2. Test it
./run_get_jobs.sh
# 3. Commit and push
git add main_get_jobs.py
git commit -m "Fix: Handle missing jobs_ran.csv gracefully"
git push
```

### Adding New Pipeline Features

```bash
# 1. Create feature branch
git checkout -b feature/add-pipeline-4-aggregation

# 2. Add your feature
# ... edit main_get_jobs.py to add run_job_aggregation_pipeline() ...

# 3. Test thoroughly
./run_get_jobs.sh

# 4. Commit
git add main_get_jobs.py
git commit -m "Add Pipeline 4: Job aggregation step"

# 5. Push and optionally create PR
git push -u origin feature/add-pipeline-4-aggregation
```

### Refactoring Code

```bash
# 1. Create refactor branch
git checkout -b refactor/simplify-pipeline-orchestration

# 2. Refactor main_get_jobs.py
# ... restructure code ...

# 3. Test to ensure same functionality
./run_get_jobs.sh

# 4. Commit
git add main_get_jobs.py
git commit -m "Refactor: Extract pipeline steps into separate functions"

# 5. Push
git push -u origin refactor/simplify-pipeline-orchestration
```

---

## Testing Before Committing

### Quick Test Script

Create a simple test workflow:

```bash
# Test your changes before committing
python3 main_get_jobs.py

# If successful, proceed with commit
# If failed, fix and test again
```

### Check What You're About to Commit

```bash
# See exactly what changed
git diff main_get_jobs.py

# See what's staged
git diff --staged main_get_jobs.py

# Review the full file context
git diff HEAD main_get_jobs.py
```

---

## Commit Message Guidelines for `main_get_jobs.py`

### Good Commit Messages

```bash
# Feature additions
git commit -m "Add pipeline status tracking to main_get_jobs.py"
git commit -m "Implement error recovery in job search pipeline"

# Bug fixes
git commit -m "Fix: Handle empty job title input gracefully"
git commit -m "Fix: Correct CSV file path resolution in find_latest_csv()"

# Improvements
git commit -m "Improve logging messages in pipeline orchestration"
git commit -m "Enhance error messages for better debugging"

# Refactoring
git commit -m "Refactor: Extract pipeline steps into separate functions"
git commit -m "Clean up: Remove duplicate code in pipeline execution"
```

### Avoid Vague Messages

```bash
# ❌ Bad
git commit -m "updates"
git commit -m "fix stuff"
git commit -m "changes"

# ✅ Good
git commit -m "Fix: Handle FileNotFoundError in find_latest_csv()"
git commit -m "Add retry logic for failed pipeline steps"
```

---

## Handling Multiple Files

When `main_get_jobs.py` changes require updates to other files:

```bash
# Stage related files together
git add main_get_jobs.py
git add job_search/job_extraction/job_search.py
git commit -m "Update pipeline to handle new job search parameters"

# Or stage all related changes
git add main_get_jobs.py job_search/
git commit -m "Refactor pipeline to use new job extraction API"
```

---

## Undoing Changes During Iteration

### Discard Uncommitted Changes

```bash
# If your changes broke something and you want to start over
git checkout -- main_get_jobs.py

# Or discard all uncommitted changes (⚠️ be careful!)
git checkout -- .
```

### Undo Last Commit (Keep Changes)

```bash
# Undo commit but keep your changes staged
git reset --soft HEAD~1

# Undo commit and unstage changes
git reset HEAD~1

# Now you can edit and recommit
```

### Undo Last Commit (Discard Changes) ⚠️

```bash
# Only if you're sure you want to lose the changes
git reset --hard HEAD~1
```

---

## Branching Strategy for Pipeline Development

### Main Branch (`main`)
- **Purpose**: Stable, working code
- **Rule**: Only merge tested, working code
- **Use**: Production-ready pipeline

### Feature Branches (`feature/*`)
- **Purpose**: New features, enhancements
- **Examples**: 
  - `feature/add-pipeline-5`
  - `feature/improve-error-handling`
  - `feature/add-retry-logic`

### Fix Branches (`fix/*` or `bugfix/*`)
- **Purpose**: Bug fixes
- **Examples**:
  - `fix/csv-parsing-error`
  - `fix/missing-log-file-handling`

### Refactor Branches (`refactor/*`)
- **Purpose**: Code improvements without changing functionality
- **Examples**:
  - `refactor/simplify-pipeline-orchestration`
  - `refactor/extract-helper-functions`

---

## Example: Complete Development Cycle

Here's a complete example of developing a new feature:

```bash
# 1. Start from latest main
git checkout main
git pull

# 2. Create feature branch
git checkout -b feature/add-pipeline-status-tracking

# 3. Make changes to main_get_jobs.py
# ... edit the file ...

# 4. Test your changes
./run_get_jobs.sh

# 5. Check what changed
git diff main_get_jobs.py

# 6. Stage and commit
git add main_get_jobs.py
git commit -m "Add pipeline status tracking to main_get_jobs.py

- Track status of each pipeline stage
- Log completion times
- Add error status reporting"

# 7. Push branch
git push -u origin feature/add-pipeline-status-tracking

# 8. (Optional) Create Pull Request on GitHub for review

# 9. After PR is merged, clean up
git checkout main
git pull
git branch -d feature/add-pipeline-status-tracking
```

---

## Quick Reference Commands

### Most Common Commands for `main_get_jobs.py` Development

```bash
# See what changed
git diff main_get_jobs.py

# Stage and commit
git add main_get_jobs.py
git commit -m "Your message here"

# Push
git push

# Create feature branch
git checkout -b feature/your-feature-name

# Switch back to main
git checkout main

# Discard uncommitted changes
git checkout -- main_get_jobs.py

# See commit history for this file
git log --oneline main_get_jobs.py
```

---

## Tips for Efficient Iteration

1. **Test Before Committing**: Always run `./run_get_jobs.sh` or `python3 main_get_jobs.py` before committing
2. **Small, Frequent Commits**: Commit working changes often rather than one large commit
3. **Use Branches for Experiments**: Create a branch when trying something risky
4. **Review Your Diffs**: Use `git diff` to review changes before committing
5. **Write Clear Messages**: Future you will thank present you for clear commit messages

---

## Troubleshooting Common Scenarios

### "I made changes but the pipeline broke"

```bash
# Option 1: Fix the issue
# ... fix main_get_jobs.py ...
./run_get_jobs.sh  # test
git add main_get_jobs.py
git commit -m "Fix: Correct pipeline execution order"

# Option 2: Discard and start over
git checkout -- main_get_jobs.py
```

### "I want to try something experimental"

```bash
# Create experimental branch
git checkout -b experiment/async-pipeline

# Make changes
# ... edit main_get_jobs.py ...

# Test
./run_get_jobs.sh

# If it works, commit; if not, discard
git checkout main
git branch -D experiment/async-pipeline
```

### "I committed but want to add more changes"

```bash
# Make additional changes
# ... edit main_get_jobs.py ...

# Add to previous commit
git add main_get_jobs.py
git commit --amend -m "Updated commit message with new changes"
```

---

*This workflow is tailored for iterative development on `main_get_jobs.py`. Adjust as needed for your specific development style.*

# Add these to your ~/.gitconfig or run:
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.unstage 'reset HEAD --'
git config --global alias.last 'log -1 HEAD'
git config --global alias.visual '!gitk'