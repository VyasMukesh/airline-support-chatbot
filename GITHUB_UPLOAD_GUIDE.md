# 🚀 GitHub Upload Guide

## Step-by-Step Instructions to Upload Your Project to GitHub

### Prerequisites
- Git installed on your computer
- GitHub account created

---

## Method 1: Using Git Command Line (Recommended)

### Step 1: Initialize Git Repository
Open PowerShell in your project folder:
```powershell
cd c:\Users\Dell\OneDrive\Desktop\asapp
git init
```

### Step 2: Add Files to Git
```powershell
git add .
```

### Step 3: Create Initial Commit
```powershell
git commit -m "Initial commit: Airline Support Chatbot with BERT"
```

### Step 4: Create Repository on GitHub
1. Go to https://github.com
2. Click "+" in top right → "New repository"
3. Name it: `airline-support-chatbot`
4. Description: "AI-powered airline support chatbot with BERT intent classification"
5. Choose "Public" or "Private"
6. **DO NOT** initialize with README (we already have one)
7. Click "Create repository"

### Step 5: Connect Local Repo to GitHub
Replace `YOUR_USERNAME` with your GitHub username:
```powershell
git remote add origin https://github.com/YOUR_USERNAME/airline-support-chatbot.git
git branch -M main
git push -u origin main
```

### Step 6: Enter Credentials
- Enter your GitHub username
- For password, use a **Personal Access Token** (not your account password)
  
To create a token:
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token (classic)
3. Select scopes: `repo` (all)
4. Copy the token and use it as password

---

## Method 2: Using GitHub Desktop (Easier for Beginners)

### Step 1: Install GitHub Desktop
Download from: https://desktop.github.com/

### Step 2: Sign In
1. Open GitHub Desktop
2. File → Options → Sign in to GitHub.com
3. Enter credentials

### Step 3: Add Repository
1. File → Add local repository
2. Choose folder: `c:\Users\Dell\OneDrive\Desktop\asapp`
3. Click "create a repository" if prompted
4. Fill in:
   - Name: `airline-support-chatbot`
   - Description: "AI-powered airline support chatbot"
   - Git Ignore: Python
   - License: MIT

### Step 4: Make Initial Commit
1. Check all files in the left panel
2. Summary: "Initial commit: Airline Support Chatbot with BERT"
3. Click "Commit to main"

### Step 5: Publish to GitHub
1. Click "Publish repository" in top bar
2. Uncheck "Keep this code private" if you want it public
3. Click "Publish repository"

---

## Method 3: Upload Files Directly (Simplest)

### Step 1: Create Repository on GitHub
1. Go to https://github.com
2. Click "+" → "New repository"
3. Name: `airline-support-chatbot`
4. Choose Public/Private
5. Click "Create repository"

### Step 2: Upload Files
1. Click "uploading an existing file"
2. Drag and drop your project folder OR click "choose your files"
3. Select all files from: `c:\Users\Dell\OneDrive\Desktop\asapp`
4. Commit message: "Initial commit: Airline Support Chatbot"
5. Click "Commit changes"

---

## After Upload: Update README

### Update Your Information
Edit `README.md` on GitHub:
1. Replace `[Your Name]` with your actual name
2. Replace `YOUR_USERNAME` with your GitHub username
3. Replace `your.email@example.com` with your email

### Add Project Link
In the README, update:
```markdown
git clone https://github.com/YOUR_ACTUAL_USERNAME/airline-support-chatbot.git
```

---

## Optional: Add Repository Topics

On your GitHub repository page:
1. Click ⚙️ (settings icon) next to "About"
2. Add topics: `django`, `chatbot`, `bert`, `ai`, `nlp`, `python`, `machine-learning`, `airline`, `customer-support`
3. Save changes

---

## Files Created for GitHub

✅ `README.md` - Comprehensive documentation
✅ `.gitignore` - Ignore unnecessary files
✅ `requirements.txt` - Python dependencies
✅ `CONTRIBUTING.md` - Contribution guidelines
✅ `LICENSE` - MIT License

---

## What NOT to Upload

The `.gitignore` file excludes:
- ❌ `.venv/` - Virtual environment (too large)
- ❌ `db.sqlite3` - Database with test data
- ❌ `__pycache__/` - Python cache files
- ❌ `.env` - Secret keys and credentials

---

## Verify Upload

After uploading, check:
1. All source code files are present
2. README displays properly
3. No sensitive data uploaded
4. Requirements.txt is complete

---

## Make Repository Attractive

### Add a Description
Repository → Settings → About section:
- Description: "AI-powered airline support chatbot with BERT intent classification and Django backend"
- Website: Your demo URL (if deployed)
- Topics: Add relevant tags

### Create a Nice README
Your README already includes:
- ✅ Badges
- ✅ Features list
- ✅ Installation guide
- ✅ Usage examples
- ✅ Architecture diagram
- ✅ API documentation

### Add Screenshots
1. Take screenshots of your chatbot
2. Upload to repository: Create `screenshots/` folder
3. Add to README:
```markdown
![Chat Interface](screenshots/chat.png)
![Booking Management](screenshots/bookings.png)
```

---

## Share Your Project

After upload, share the link:
```
https://github.com/YOUR_USERNAME/airline-support-chatbot
```

Add it to:
- LinkedIn profile
- Resume/Portfolio
- Twitter/Social media

---

## Need Help?

If you encounter issues:
1. Check Git is installed: `git --version`
2. Verify GitHub credentials
3. Try GitHub Desktop if command line fails
4. Contact GitHub Support

---

**Good luck with your upload! 🎉**
