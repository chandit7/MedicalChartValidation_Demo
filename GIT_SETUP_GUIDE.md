# Git Setup & Push to Remote Repository

## 📋 Prerequisites

- Git installed on your system
- GitHub/GitLab/Bitbucket account
- Terminal/Command Prompt access

## 🚀 Step-by-Step Guide

### Step 1: Verify Git Installation

```bash
git --version
```

If not installed, download from: https://git-scm.com/downloads

---

### Step 2: Configure Git (First Time Only)

```bash
# Set your name
git config --global user.name "Your Name"

# Set your email
git config --global user.email "your.email@example.com"

# Verify configuration
git config --list
```

---

### Step 3: Initialize Local Repository

```bash
# Navigate to your project directory
cd c:/Ramesh_Learning/Agentic_AI_Demo_Challenge

# Initialize git repository
git init

# Verify initialization
git status
```

**Expected output:**
```
Initialized empty Git repository in c:/Ramesh_Learning/Agentic_AI_Demo_Challenge/.git/
```

---

### Step 4: Add Files to Staging

```bash
# Add all files (respects .gitignore)
git add .

# Or add specific files
git add README.md
git add .gitignore
git add medchart_demo/

# Check what will be committed
git status
```

**What gets added:**
- ✅ All Python files (.py)
- ✅ Documentation (.md)
- ✅ Sample data files
- ✅ Requirements.txt
- ❌ Virtual environment (venv/)
- ❌ Database files (.db)
- ❌ Cache files (__pycache__)
- ❌ IDE files (.vscode/)

---

### Step 5: Create Initial Commit

```bash
# Commit with descriptive message
git commit -m "Initial commit: Medical Chart Validation System

- Implemented 4-agent validation pipeline
- Added Streamlit UI with 3 tabs
- Created 5 test cases
- Added comprehensive documentation
- Zero-LLM deterministic decision engine"

# Verify commit
git log --oneline
```

---

### Step 6: Create Remote Repository

#### Option A: GitHub (Recommended)

1. Go to https://github.com
2. Click "+" → "New repository"
3. Repository name: `medical-chart-validation` (or your choice)
4. Description: "Zero-LLM medical chart validation system"
5. Choose: **Public** or **Private**
6. **DO NOT** initialize with README (we already have one)
7. Click "Create repository"

#### Option B: GitLab

1. Go to https://gitlab.com
2. Click "New project" → "Create blank project"
3. Fill in details similar to GitHub
4. Click "Create project"

#### Option C: Bitbucket

1. Go to https://bitbucket.org
2. Click "Create" → "Repository"
3. Fill in details
4. Click "Create repository"

---

### Step 7: Connect Local to Remote

**Copy the remote URL from your repository page, then:**

```bash
# Add remote repository (replace with your URL)
git remote add origin https://github.com/YOUR_USERNAME/medical-chart-validation.git

# Verify remote
git remote -v
```

**Expected output:**
```
origin  https://github.com/YOUR_USERNAME/medical-chart-validation.git (fetch)
origin  https://github.com/YOUR_USERNAME/medical-chart-validation.git (push)
```

---

### Step 8: Push to Remote

```bash
# Push to main branch (or master, depending on your setup)
git push -u origin main

# If you get an error about 'main' not existing, try:
git branch -M main
git push -u origin main

# Or if your default branch is 'master':
git push -u origin master
```

**First time push may ask for credentials:**
- Username: Your GitHub/GitLab username
- Password: Use **Personal Access Token** (not your account password)

---

### Step 9: Verify Push

1. Go to your repository URL in browser
2. Refresh the page
3. You should see all your files!

---

## 🔐 Authentication Setup

### GitHub Personal Access Token (Recommended)

1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Name: "Medical Chart Validation"
4. Expiration: Choose duration
5. Scopes: Select **repo** (full control)
6. Click "Generate token"
7. **COPY THE TOKEN** (you won't see it again!)
8. Use this token as password when pushing

### SSH Key (Alternative)

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your.email@example.com"

# Copy public key
cat ~/.ssh/id_ed25519.pub

# Add to GitHub: Settings → SSH and GPG keys → New SSH key
# Paste the key and save

# Change remote to SSH
git remote set-url origin git@github.com:YOUR_USERNAME/medical-chart-validation.git
```

---

## 📝 Common Git Commands

### Daily Workflow

```bash
# Check status
git status

# Add changes
git add .

# Commit changes
git commit -m "Description of changes"

# Push to remote
git push

# Pull latest changes
git pull

# View commit history
git log --oneline --graph
```

### Branching

```bash
# Create new branch
git checkout -b feature/new-feature

# Switch branches
git checkout main

# Merge branch
git merge feature/new-feature

# Delete branch
git branch -d feature/new-feature
```

### Undo Changes

```bash
# Discard changes in working directory
git checkout -- filename

# Unstage file
git reset HEAD filename

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1
```

---

## 🎯 Recommended Workflow

### For New Features

```bash
# 1. Create feature branch
git checkout -b feature/llm-analytics

# 2. Make changes
# ... edit files ...

# 3. Stage and commit
git add .
git commit -m "Add LLM analytics module"

# 4. Push feature branch
git push -u origin feature/llm-analytics

# 5. Create Pull Request on GitHub
# 6. After review, merge to main
# 7. Delete feature branch
git branch -d feature/llm-analytics
```

### For Bug Fixes

```bash
# 1. Create bugfix branch
git checkout -b bugfix/fix-date-validation

# 2. Fix the bug
# ... edit files ...

# 3. Commit with descriptive message
git commit -m "Fix: Correct date validation logic for leap years"

# 4. Push and create PR
git push -u origin bugfix/fix-date-validation
```

---

## 🔍 Verify Your Repository

After pushing, check that these files are visible on GitHub:

```
✅ README.md
✅ .gitignore
✅ GIT_SETUP_GUIDE.md
✅ medchart_demo/
   ✅ app.py
   ✅ db.py
   ✅ agents.py
   ✅ check_db.py
   ✅ requirements.txt
   ✅ FLOW_DIAGRAM.md
   ✅ LLM_ANALYTICS_PLAN.md
   ✅ TEST_CASES.md
   ✅ sample_data/
      ✅ gap_report.csv
      ✅ chart_MBR001.txt
      ✅ chart_MBR002.txt
      ✅ chart_MBR003.txt
      ✅ chart_MBR004.txt
      ✅ chart_MBR005.txt
✅ MedicalChartAgentFlow/
   ✅ IMPLEMENTATION_GUIDE.md
   ✅ QUICK_START.md
   ✅ TROUBLESHOOTING.md

❌ venv/ (ignored)
❌ __pycache__/ (ignored)
❌ *.db (ignored)
❌ .vscode/ (ignored)
```

---

## 🐛 Troubleshooting

### Error: "fatal: not a git repository"
```bash
# Solution: Initialize git
git init
```

### Error: "remote origin already exists"
```bash
# Solution: Remove and re-add
git remote remove origin
git remote add origin YOUR_URL
```

### Error: "failed to push some refs"
```bash
# Solution: Pull first, then push
git pull origin main --rebase
git push origin main
```

### Error: "Permission denied (publickey)"
```bash
# Solution: Use HTTPS instead of SSH
git remote set-url origin https://github.com/YOUR_USERNAME/REPO.git
```

### Large files warning
```bash
# If you accidentally added large files:
git rm --cached large_file.db
echo "large_file.db" >> .gitignore
git commit -m "Remove large file from tracking"
```

---

## 📊 Repository Best Practices

### Commit Messages

**Good:**
```
✅ "Add: LLM analytics module with trend analysis"
✅ "Fix: Date validation for edge cases"
✅ "Update: README with installation instructions"
✅ "Refactor: Simplify agent pipeline logic"
```

**Bad:**
```
❌ "update"
❌ "fix bug"
❌ "changes"
❌ "asdf"
```

### Commit Frequency

- Commit after completing a logical unit of work
- Don't commit broken code to main branch
- Use feature branches for experimental work

### .gitignore Maintenance

- Keep .gitignore updated
- Never commit sensitive data (API keys, passwords)
- Never commit large binary files
- Never commit generated files (databases, caches)

---

## 🎉 Success Checklist

- [ ] Git installed and configured
- [ ] Local repository initialized
- [ ] All files added and committed
- [ ] Remote repository created
- [ ] Local connected to remote
- [ ] Successfully pushed to remote
- [ ] Repository visible on GitHub/GitLab
- [ ] README displays correctly
- [ ] .gitignore working (venv/ not pushed)

---

## 📚 Additional Resources

- **Git Documentation**: https://git-scm.com/doc
- **GitHub Guides**: https://guides.github.com
- **Git Cheat Sheet**: https://education.github.com/git-cheat-sheet-education.pdf
- **Interactive Git Tutorial**: https://learngitbranching.js.org

---

## 🆘 Need Help?

If you encounter issues:

1. Check error message carefully
2. Search on Stack Overflow
3. Consult Git documentation
4. Ask in GitHub Community forums

---

**Your repository is now ready for collaboration!** 🚀