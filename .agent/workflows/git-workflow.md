---
description: Git workflow best practices for ROS 2 development
---

# Git Workflow for ROS 2 Development

This workflow helps you safely manage changes and prevent data loss when working on ROS 2 projects.

## 1. First Time Setup

Create a development branch for your work:
```bash
git checkout -b dev
```

## 2. Daily Workflow

### Before Starting Work

Check your current status:
```bash
git status
git branch
```

### During Development

Commit your changes frequently (every 30-60 minutes or after completing a logical unit of work):

```bash
# Check what changed
git status

# Stage specific files
git add <file1> <file2>
# OR stage all changes
git add .

# Commit with descriptive message
git commit -m "Add: brief description of what you did"
```

**Commit Message Prefixes:**
- `Add:` - New features or files
- `Fix:` - Bug fixes
- `Update:` - Modifications to existing features
- `Remove:` - Deleted files or features
- `Refactor:` - Code restructuring without functionality change
- `WIP:` - Work in progress (incomplete work you want to save)

### End of Day

Always commit your work before ending the day:
```bash
git add .
git commit -m "WIP: end of day checkpoint - <what you were working on>"
```

## 3. Creating Feature Branches

For major new features, create a dedicated branch:

```bash
# From your dev branch
git checkout dev
git checkout -b feature/manipulator-control
```

Work on the feature, commit regularly, then merge back:
```bash
# When feature is complete
git checkout dev
git merge feature/manipulator-control
```

## 4. Safe Experimentation

Before trying something risky:

```bash
# Commit current state
git add .
git commit -m "Checkpoint before experimenting with <description>"

# Create experimental branch
git checkout -b experiment/new-idea

# If experiment fails, easily return to dev
git checkout dev

# If experiment succeeds, merge it
git merge experiment/new-idea
```

## 5. Undoing Changes SAFELY

### Undo uncommitted changes to specific files:
```bash
# Preview what will be discarded
git diff <file>

# Restore specific file to last commit
git checkout -- <file>
```

### Undo all uncommitted changes (CAUTION):
```bash
# First, create a safety commit
git add .
git commit -m "Safety checkpoint before reset"

# Then you can reset if needed
git reset --hard HEAD~1  # Goes back one commit
```

### View and recover from history:
```bash
# See recent commits
git log --oneline -10

# See all actions including resets
git reflog

# Recover to a specific commit
git checkout <commit-hash>
```

## 6. ROS 2 Specific Tips

### Files to Track
Always commit:
- Source code (`.cpp`, `.py`, etc.)
- URDF/Xacro files
- Launch files
- Configuration files (`.yaml`)
- Package files (`package.xml`, `CMakeLists.txt`)
- Custom meshes and assets

### Files to Ignore (add to `.gitignore`)
```
# Build artifacts
build/
install/
log/

# IDE files
.vscode/
.idea/
*.swp

# Python
__pycache__/
*.pyc
```

## 7. Syncing with Remote (GitHub)

### Push your work to GitHub:
```bash
# First time pushing a branch
git push -u origin dev

# Subsequent pushes
git push
```

### Pull latest changes:
```bash
git pull origin dev
```

## 8. Emergency Recovery

If you accidentally run `git reset --hard`:

```bash
# Check reflog immediately
git reflog

# Find the commit before reset (look for timestamp)
# Restore to that commit
git reset --hard HEAD@{1}  # or use commit hash
```

**IMPORTANT:** `git clean -fd` CANNOT be undone - it permanently deletes untracked files!

## 9. Quick Reference

**Save your work NOW:**
```bash
git add . && git commit -m "WIP: <description>"
```

**See what changed:**
```bash
git status
git diff
```

**View commit history:**
```bash
git log --oneline --graph --all -20
```

**Create safety checkpoint:**
```bash
git add . && git commit -m "Checkpoint: <description>"
git tag checkpoint-$(date +%Y%m%d-%H%M%S)
```

---

## Remember:
1. **Commit early, commit often** - At least every hour
2. **Never use `git reset --hard` on uncommitted work**
3. **Always create branches for experiments**
4. **Push to GitHub at end of each day**
5. **Write descriptive commit messages**
