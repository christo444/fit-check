# Quick Start Commands

## First Time Setup
1. Run setup script:
   ```powershell
   .\setup.ps1
   ```

2. Configure Supabase:
   - Create project at https://supabase.com
   - Create storage bucket named "outfits" (make it PUBLIC)
   - Run SQL from README.md

3. Add credentials:
   - Edit `backend/.env` with your Supabase credentials
   - Edit `frontend/.env.local` with your Supabase credentials

## Running the App

### Terminal 1 - Backend
```powershell
cd backend
.\venv\Scripts\activate
python app.py
```

### Terminal 2 - Frontend
```powershell
cd frontend
npm run dev
```

## Quick Test
1. Go to http://localhost:3000
2. Click "Upload Your Outfit"
3. Upload an image
4. View in Wardrobe

## Troubleshooting

### Backend Issues
```powershell
# Reinstall dependencies
cd backend
.\venv\Scripts\activate
pip install -r requirements.txt --upgrade
```

### Frontend Issues
```powershell
# Clear and reinstall
cd frontend
Remove-Item -Recurse -Force node_modules, .next
npm install
```

### Check Backend Health
```powershell
curl http://localhost:5000/health
```

## Supabase SQL (Run in SQL Editor)

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
