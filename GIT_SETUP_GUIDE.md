# 🚀 AgriVerse - Git Setup & Push Guide

## ⚠️ IMPORTANT: Protect Your Secret Keys!

Your `.env` file contains **sensitive API keys** that should NEVER be pushed to git! The `.gitignore` file prevents this.

---

## ✅ **Quick Start - Push to Git Safely**

### **Step 1: Initialize Git (if not already done)**
```bash
cd c:\Users\vishnu\OneDrive\Desktop\AgriVerse
git init
```

### **Step 2: Configure Git User (first time only)**
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### **Step 3: Add Remote Repository**
```bash
# If pushing to GitHub, create repo first at github.com
# Then add the remote:
git remote add origin https://github.com/your-username/agriverse.git

# Verify it's added:
git remote -v
```

### **Step 4: Create Initial Commit**
```bash
# Stage all files (respecting .gitignore)
git add .

# Create commit
git commit -m "Initial AgriVerse commit - AI Farming Advisory System"

# Push to remote (first time)
git branch -M main
git push -u origin main
```

### **Step 5: Regular Updates**
```bash
# Make changes...

# Check what will be committed:
git status

# Stage changes:
git add .

# Or stage specific files:
git add frontend/src/components/OrganicFarmingForm.jsx
git add backend/app/services/disease_detector.py

# Commit with message:
git commit -m "Describe your changes here"

# Push to GitHub:
git push origin main
```

---

## 📋 **What Gets Pushed vs. Ignored**

### **✅ PUSHED (in git repository)**
```
✅ All source code (.jsx, .py, .js, .css, .html, .json)
✅ README.md, documentation
✅ requirements.txt (Python dependencies list)
✅ package.json (Node dependencies list)
✅ .gitignore (this file)
✅ .env.example (template with no real values)
✅ Configuration files (except secrets)
```

### **❌ IGNORED (NOT pushed)**
```
❌ venv/ (Python virtual environment)
❌ node_modules/ (JavaScript packages)
❌ __pycache__/ (Python cache)
❌ .env (actual secrets and API keys)
❌ *.h5 (trained model files - too large)
❌ archive/dataset/ (training data - too large)
❌ *.mp3, *.wav (audio files)
❌ logs/, tmp/, __pycache__/
```

---

## 🔒 **Handling .env Files Safely**

### **For You (Local Development)**
1. Copy `.env.example` from backend folder to `.env`:
   ```bash
   cd backend
   cp .env.example .env
   ```

2. Fill in your actual API keys in `.env`:
   ```bash
   # backend/.env
   GEMINI_API_KEY=AIzaSyD83eE0xpSnxazoyxVJEcJ6BBDEi50IVDk  # Your real key
   ```

3. Never commit `backend/.env` - it's in `.gitignore` ✅

### **For Others Cloning Your Repository**
They will:
1. Clone your repo (without `backend/.env`)
2. Copy the template:
   ```bash
   cd backend
   cp .env.example .env
   ```
3. Fill in their own API keys
4. Everything works! ✅

---

## 🆘 **If You Already Committed Secrets**

### ⛔ **DANGER: You exposed API keys!**
Anyone with access to git history can see them.

### **Fix It:**
```bash
# 1. Remove .env from git history
git rm --cached backend/.env

# 2. Commit the removal
git commit -m "Remove .env with secrets from git history"

# 3. Push to update remote
git push origin main

# 4. ⚠️ REGENERATE API KEYS! (Your old key is exposed)
# Go to https://aistudio.google.com/app/apikeys
# Delete the old key, create a new one
# Update your local .env with new key
```

---

## 📦 **Python Dependencies - requirements.txt**

### **How it works:**
1. When you install packages:
   ```bash
   pip install flask pandas numpy
   ```

2. Python installs them to `venv/lib/site-packages/` (ignored)

3. To save them to `requirements.txt`:
   ```bash
   pip freeze > requirements.txt
   ```

4. Others can install from requirements.txt:
   ```bash
   pip install -r requirements.txt
   ```

### **✅ Always commit `requirements.txt`** (but not `venv/`)

---

## 🚀 **Node Dependencies - package.json**

### **How it works:**
1. When you install packages:
   ```bash
   npm install axios react-hot-toast
   ```

2. Node installs them to `node_modules/` (ignored)

3. Dependencies saved to `package.json` (committed)

4. Others can install:
   ```bash
   npm install
   ```

### **✅ Always commit `package.json`** (but not `node_modules/`)

---

## ✍️ **Good Git Workflow**

```bash
# 1. Make changes
# 2. Test everything locally
# 3. Check status
git status

# 4. Review changes
git diff

# 5. Stage specific files (not everything)
git add src/MyNewComponent.jsx
git add backend/services/my_service.py

# 6. Commit with clear message
git commit -m "Add user authentication to admin panel

- Implement JWT token validation
- Add password hashing with bcrypt
- Add login endpoint"

# 7. Push to remote
git push origin main

# 8. Check it's on GitHub
open https://github.com/your-username/agriverse
```

---

## 📝 **Commit Message Examples**

**Good:**
```
Add playback speed controls to audio player
Fix disease detection model loading timeout
Optimize backend response time by 5x
```

**Bad:**
```
update
fix bugs
made changes
```

---

## 🔍 **Check What Will Be Pushed**

Before committing, verify nothing sensitive sneaks in:

```bash
# See what's staged (will be committed)
git diff --cached

# See what's modified but not staged
git diff

# See status of all files
git status
```

---

## 🎯 **Quick Reference**

```bash
# Clone someone's repo
git clone https://github.com/username/agriverse.git

# Check current branch
git branch

# See commit history
git log --oneline

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1

# Create new branch
git checkout -b feature/my-feature

# Switch branch
git checkout main

# Merge branch to main
git checkout main
git merge feature/my-feature
```

---

## ✨ **Summary**

| Task | Command |
|------|---------|
| First push | `git add . && git commit -m "Initial" && git push -u origin main` |
| Regular push | `git add . && git commit -m "describe" && git push` |
| Check status | `git status` |
| View changes | `git diff` |
| Undo last commit | `git reset --soft HEAD~1` |
| See history | `git log --oneline` |

---

## 🎓 **Learn More**

- [GitHub Docs](https://docs.github.com)
- [Git Cheat Sheet](https://github.github.com/training-kit/downloads/github-git-cheat-sheet.pdf)
- [Protecting Secrets](https://docs.github.com/en/code-security/secret-scanning)

---

**💡 TIP**: Always use `.gitignore` for local files, `.env.example` for templates, and check `git status` before pushing!
