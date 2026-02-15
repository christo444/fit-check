# TROUBLESHOOTING GUIDE

## ⚠️ Current Issue: Missing Dependencies

The TypeScript/ESLint errors you're seeing are **NORMAL** - they appear because packages haven't been installed yet.

## 🔧 Step-by-Step Setup (DO THIS FIRST)

### 1. Install Prerequisites

**Check if Node.js is installed:**
```powershell
node --version
```

If you see an error, **install Node.js first:**
- Download from: https://nodejs.org/
- Install version 18 or higher (LTS recommended)
- Restart VS Code after installation

**Check if Python is installed:**
```powershell
python --version
```

If you see an error, **install Python first:**
- Download from: https://www.python.org/
- Install version 3.9 or higher
- ✅ **IMPORTANT:** Check "Add Python to PATH" during installation
- Restart VS Code after installation

### 2. Set Up Supabase (REQUIRED)

1. Go to https://supabase.com and create account
2. Create new project (wait 2-3 minutes for it to initialize)
3. Go to **Storage** → Create bucket named `outfits` → Make it **PUBLIC**
4. Go to **SQL Editor** → Run this SQL:

```sql
CREATE TABLE outfits (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id),
  image_url TEXT NOT NULL,
  status TEXT DEFAULT 'pending',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE outfits ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public access for now" ON outfits
  FOR ALL USING (true);
```

5. Go to **Settings** → **API** → Copy:
   - `Project URL` (looks like: https://xxxxx.supabase.co)
   - `anon public` key (for frontend)
   - `service_role` key (for backend - keep this secret!)

### 3. Configure Environment Variables

**Backend (.env):**
```powershell
cd backend
copy .env.example .env
notepad .env
```

Fill in:
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_service_role_key_here
FLASK_ENV=development
FLASK_DEBUG=True
UPLOAD_FOLDER=uploads
FRONTEND_URL=http://localhost:3000
```

**Frontend (.env.local):**
```powershell
cd frontend
copy .env.local.example .env.local
notepad .env.local
```

Fill in:
```
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_public_key_here
NEXT_PUBLIC_API_URL=http://localhost:5000
```

### 4. Install Dependencies

**Backend:**
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Frontend:**
```powershell
cd frontend
npm install
```

This will take 2-5 minutes. **All TypeScript errors will disappear after this.**

### 5. Run the Application

**Terminal 1 - Backend:**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python app.py
```

Should see:
```
==================================================
🚀 FitCheck Backend Server
==================================================
Environment: development
Debug Mode: True
...
 * Running on http://0.0.0.0:5000
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm run dev
```

Should see:
```
  ▲ Next.js 14.2.3
  - Local:        http://localhost:3000
  - Ready in 2.5s
```

### 6. Test It

1. Open http://localhost:3000
2. Click "Upload Your Outfit"
3. Upload an image
4. Should redirect to outfit detail page
5. Check "Wardrobe" to see saved outfits

---

## 🐛 Common Errors & Fixes

### Error: "npm is not recognized"
**Fix:** Node.js not installed or not in PATH
- Install Node.js from https://nodejs.org/
- Restart VS Code
- Open new terminal

### Error: "python is not recognized"
**Fix:** Python not installed or not in PATH
- Install Python from https://www.python.org/
- During installation: ✅ Check "Add Python to PATH"
- Restart VS Code

### Error: "Cannot activate venv"
**Fix:** PowerShell execution policy
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Error: "Missing Supabase environment variables"
**Fix:** Environment files not configured
- Make sure `.env` exists in `backend/` folder
- Make sure `.env.local` exists in `frontend/` folder
- Check that URLs and keys are filled in (not "your_xxx_here")

### Error: "Failed to upload image"
**Fix:** Supabase bucket not configured
- Bucket must be named exactly `outfits`
- Bucket must be set to **PUBLIC**
- Check Storage settings in Supabase dashboard

### Error: "Outfit not found"
**Fix:** Database table not created
- Run the SQL script in Supabase SQL Editor
- Check that `outfits` table exists

### Error: "CORS error" in browser console
**Fix:** Backend not running
- Make sure backend is running on port 5000
- Check terminal for error messages
- Verify `FRONTEND_URL` in backend `.env` is `http://localhost:3000`

### TypeScript errors showing in VS Code
**Fix:** This is normal before `npm install`
- Run `npm install` in frontend folder
- Errors will disappear after installation
- If still showing, try:
  ```powershell
  cd frontend
  rm -r node_modules, .next
  npm install
  ```

---

## 📋 Verification Checklist

Before running the app, verify:

- [ ] Node.js 18+ installed (`node --version`)
- [ ] Python 3.9+ installed (`python --version`)
- [ ] Supabase project created
- [ ] Supabase `outfits` bucket created (PUBLIC)
- [ ] Supabase `outfits` table created (SQL script run)
- [ ] `backend/.env` exists and filled in
- [ ] `frontend/.env.local` exists and filled in
- [ ] Backend dependencies installed (`pip install -r requirements.txt`)
- [ ] Frontend dependencies installed (`npm install`)
- [ ] Backend running on port 5000
- [ ] Frontend running on port 3000

---

## 🔍 Still Having Issues?

Run these diagnostic commands:

```powershell
# Check installations
node --version
python --version
pip --version

# Check backend
cd backend
.\venv\Scripts\Activate.ps1
python -c "import flask; print('Flask OK')"
python -c "from supabase import create_client; print('Supabase OK')"

# Test backend endpoint
curl http://localhost:5000/health

# Check frontend
cd frontend
npm run build
```

---

## 📝 Quick Reference

| Component | Port | URL |
|-----------|------|-----|
| Frontend | 3000 | http://localhost:3000 |
| Backend | 5000 | http://localhost:5000 |
| Health Check | 5000 | http://localhost:5000/health |

| File | Purpose |
|------|---------|
| `backend/.env` | Backend configuration (Supabase service key) |
| `frontend/.env.local` | Frontend configuration (Supabase anon key) |
| `backend/venv/` | Python virtual environment |
| `frontend/node_modules/` | JavaScript dependencies |

---

**Need more help?** Check the main README.md for detailed explanations.
