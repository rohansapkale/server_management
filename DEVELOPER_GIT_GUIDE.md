# 📋 Server & Website Management Platform
## Git & GitHub Team Development & Branching Workflow Standard

**App Name:** `server_management`  
**Platform:** Frappe Framework v16  
**Developers:** Rohan & Roshni  
**Date:** September 2026  
**Status:** Live & Synchronized on GitHub  

---

## 1. Branching Strategy & Architecture

To ensure clean collaboration without code conflicts or unreviewed production changes, our team follows a strict 4-branch Git architecture:

| Branch Name | Role / Target | Policy & Usage |
| :--- | :--- | :--- |
| **`main`** | Production Release | **Protected Branch.** Contains only tested, production-ready code. Never push directly. |
| **`development`** | Integration & Staging | **Shared Team Branch.** Rohan and Roshni merge their tested feature work here via PRs. |
| **`rohan`** | Private Developer Branch | Dedicated workspace for Rohan to develop, test, and push daily commits. |
| **`roshni`** | Private Developer Branch | Dedicated workspace for Roshni to develop, test, and push daily commits. |

---

## 2. Developer Daily Workflow Guide

### 👨‍💻 Workflow A: Developer Rohan (`rohan` branch)

```bash
# 1. Navigate to the app directory
cd /home/frappe/frappe-bench-v16/apps/server_management

# 2. Switch to your branch and pull latest changes
git checkout rohan
git pull origin rohan

# 3. (Recommended) Sync with latest team updates from development
git pull origin development

# 4. Make your code edits in VS Code / IDE...

# 5. Check modified files and status
git status

# 6. Stage and commit with a standard message
git add .
git commit -m "feat: implement Server controller validations in server.py"

# 7. Push ONLY to your own branch on GitHub
git push origin rohan
```

---

### 👩‍💻 Workflow B: Developer Roshni (`roshni` branch)

```bash
# 1. Navigate to the app directory
cd /home/frappe/frappe-bench-v16/apps/server_management

# 2. Switch to your branch and pull latest changes
git checkout roshni
git pull origin roshni

# 3. (Recommended) Sync with latest team updates from development
git pull origin development

# 4. Make your code edits in VS Code / IDE...

# 5. Check modified files and status
git status

# 6. Stage and commit with a standard message
git add .
git commit -m "feat: add Website DocType schema and client script"

# 7. Push ONLY to your own branch on GitHub
git push origin roshni
```

---

## 3. Merging Changes into `development` (Pull Requests)

When a module or feature is completed and tested on your branch, merge it into the shared `development` branch via GitHub Pull Request:

1. Open the GitHub repository: **[https://github.com/rohansapkale/server_management](https://github.com/rohansapkale/server_management)**
2. Click **"Pull requests"** &rarr; **"New pull request"**.
3. Set **Base:** `development` &larr; **Compare:** `rohan` (or `roshni`).
4. Review the green/red line diffs to verify your changes.
5. Click **"Create pull request"**, add a summary of changes, and request code review.
6. Once reviewed and approved, click **"Merge pull request"** &rarr; **"Confirm merge"**.

---

## 4. Conventional Commit Standards

| Prefix | Purpose | Example Commit Message |
| :--- | :--- | :--- |
| `feat:` | New feature or DocType implementation | `feat: add Domain expiry calculation logic` |
| `fix:` | Bug fix or validation error patch | `fix: prevent deployment to offline servers` |
| `refactor:` | Code reorganization with no behavior change | `refactor: simplify server status helper method` |
| `docs:` | Documentation or README updates | `docs: update developer onboarding instructions` |
| `test:` | Adding or updating unit test cases | `test: add automated test for backup expiry date` |

---

## 5. Conflict Resolution Runbook

If two developers edit the same line of code in the same file, Git will highlight a conflict during merge:

1. Open the conflicted file in your IDE. You will see markers:
   ```python
   <<<<<<< HEAD (current branch)
   self.validate_server()
   =======
   self.validate_domain()
   >>>>>>> roshni (incoming branch)
   ```
2. Keep both or edit to the correct combined logic:
   ```python
   self.validate_server()
   self.validate_domain()
   ```
3. Save the file, stage, and complete the merge:
   ```bash
   git add .
   git commit -m "fix: resolve merge conflict in website.py"
   git push origin development
   ```

---

## 6. Quick Command Reference & Safety Cheat Sheet

| Action / Task | Git Command |
| :--- | :--- |
| Check current branch & modified files | `git status` |
| List all local branches | `git branch` |
| Switch to another branch | `git checkout <branch_name>` |
| Pull latest commits from remote | `git pull origin <branch_name>` |
| Stage all modified files | `git add .` |
| Commit staged changes | `git commit -m "feat: description"` |
| Push commits to remote branch | `git push origin <branch_name>` |
| Discard uncommitted changes in a specific file | `git checkout -- <file_path>` |
| Temporarily stash uncommitted changes | `git stash` (restore with `git stash pop`) |
| View recent commit log | `git log --oneline -n 10` |
