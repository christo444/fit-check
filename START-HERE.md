# ⚠️ SEEING ERRORS? START HERE

## The errors you're seeing are NORMAL!

TypeScript and ESLint errors appear **before** you install dependencies. This is expected behavior.

## Quick Fix (3 steps):

### 1️⃣ Check Prerequisites
Run this to check what's installed:
```powershell
.\check-setup.ps1
```

### 2️⃣ Install Everything
If Node.js and Python are installed, run:
```powershell
.\setup.ps1
```

This will:
- ✅ Create Python virtual environment
- ✅ Install Python packages
- ✅ Install Node.js packages
- ✅ Create environment file templates

**All TypeScript/ESLint errors will disappear after this!**

### 3️⃣ Configure Supabase
See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for step-by-step Supabase setup.

---

## Prerequisites Not Installed?

### Install Node.js
1. Download from https://nodejs.org/ (version 18+)
2. Run installer
3. Restart VS Code
4. Run `.\check-setup.ps1` again

### Install Python  
1. Download from https://www.python.org/ (version 3.9+)
2. ⚠️ **CHECK "Add Python to PATH"** during installation
3. Run installer
4. Restart VS Code
5. Run `.\check-setup.ps1` again

---

## Files Overview

| File | Purpose |
|------|---------|
| `check-setup.ps1` | Verify installation status |
| `setup.ps1` | Install all dependencies |
| `TROUBLESHOOTING.md` | Detailed troubleshooting guide |
| `README.md` | Full project documentation |
| `QUICKSTART.md` | Quick command reference |

---

## Still Stuck?

Read the full [TROUBLESHOOTING.md](TROUBLESHOOTING.md) guide.
