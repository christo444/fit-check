# FitCheck - AI Fashion Detection & Outfit Recommendation

An AI-powered web application for analyzing outfit photos, detecting clothing items, estimating fit, and providing personalized style recommendations.

## 🏗️ Tech Stack

### Frontend
- **Next.js 14** (App Router)
- **TypeScript**
- **TailwindCSS** for styling
- **ShadCN UI** components
- **React Query** for API state management

### Backend
- **Flask** (Python)
- **REST API** architecture
- **Supabase** for database, auth, and storage

### AI/ML (Future Phases)
- YOLOv8 for clothing detection
- OpenCV for color extraction
- MediaPipe for pose estimation
- LLM integration for style recommendations

## 📁 Project Structure

```
fit-check/
├── frontend/                 # Next.js frontend
│   ├── app/                 # App router pages
│   │   ├── layout.tsx       # Root layout
│   │   ├── page.tsx         # Home page
│   │   ├── upload/          # Upload page
│   │   ├── outfit/[id]/     # Outfit detail page
│   │   └── wardrobe/        # Wardrobe gallery
│   ├── components/          # React components
│   │   └── UploadBox.tsx    # Image upload component
│   └── lib/                 # Utilities
│       ├── supabase.ts      # Supabase client
│       ├── api.ts           # API functions
│       └── utils.ts         # Helper functions
│
└── backend/                 # Flask backend
    ├── app.py               # Main Flask application
    ├── config.py            # Configuration
    ├── routes/              # API routes
    │   ├── health.py        # Health check
    │   ├── upload.py        # Image upload
    │   └── outfit.py        # Outfit endpoints
    └── services/            # Business logic
        └── storage_service.py  # Supabase operations
```

## 🚀 Phase 1 Setup (Current)

Phase 1 includes:
- ✅ Project structure
- ✅ Image upload functionality
- ✅ Backend API connection
- ✅ Supabase integration
- ✅ Basic UI pages

## 📋 Prerequisites

- **Node.js** 18+ and npm/yarn
- **Python** 3.9+
- **Supabase** account (free tier works)

## 🔧 Setup Instructions

### 1. Supabase Setup

1. Create a new project at [supabase.com](https://supabase.com)
2. Go to **Storage** and create a bucket named `outfits` (make it public)
3. Go to **SQL Editor** and run this SQL:

```sql
CREATE TABLE outfits (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id),
  image_url TEXT NOT NULL,
  status TEXT DEFAULT 'pending',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE outfits ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (will restrict by user later)
CREATE POLICY "Public access for now" ON outfits
  FOR ALL USING (true);
```

4. Get your credentials from **Settings > API**:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY` (for frontend)
   - `SUPABASE_SERVICE_ROLE_KEY` (for backend)

### 2. Backend Setup

```powershell
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from example
copy .env.example .env

# Edit .env and add your Supabase credentials
notepad .env
```

Update `.env` with:
```
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_service_role_key
FLASK_ENV=development
FLASK_DEBUG=True
```

### 3. Frontend Setup

```powershell
# Open new terminal and navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create .env.local from example
copy .env.local.example .env.local

# Edit .env.local and add your Supabase credentials
notepad .env.local
```

Update `.env.local` with:
```
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
NEXT_PUBLIC_API_URL=http://localhost:5000
```

## ▶️ Running the Application

### Start Backend (Terminal 1)

```powershell
cd backend
.\venv\Scripts\activate
python app.py
```

Backend will run on `http://localhost:5000`

### Start Frontend (Terminal 2)

```powershell
cd frontend
npm run dev
```

Frontend will run on `http://localhost:3000`

## 🧪 Testing Phase 1

1. Open browser to `http://localhost:3000`
2. Click "Upload Your Outfit"
3. Upload an image
4. Check that it saves and redirects to outfit detail page
5. Navigate to "Wardrobe" to see saved outfits

## 📝 API Endpoints (Phase 1)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/upload` | Upload outfit image |
| GET | `/api/outfit/:id` | Get outfit by ID |
| GET | `/api/outfits` | Get all outfits |

## 🛣️ Next Phases

- **Phase 2**: YOLOv8 clothing detection + bounding boxes
- **Phase 3**: Color and pattern extraction
- **Phase 4**: Pose estimation + fit calculation
- **Phase 5**: LLM style reasoning
- **Phase 6**: Product search integration
- **Phase 7**: Wardrobe dashboard + analytics

## 🐛 Troubleshooting

**Backend won't start:**
- Check Python version: `python --version` (needs 3.9+)
- Verify virtual environment is activated
- Check `.env` file exists with valid Supabase credentials

**Frontend won't start:**
- Check Node version: `node --version` (needs 18+)
- Delete `node_modules` and run `npm install` again
- Verify `.env.local` exists with correct values

**Upload fails:**
- Check Supabase bucket named `outfits` exists
- Verify bucket is set to PUBLIC
- Check backend logs for detailed error messages

**Images don't appear:**
- Verify image URL in database starts with your Supabase project URL
- Check browser console for CORS errors
- Ensure bucket is public in Supabase Storage settings

## 📄 License

MIT License - This is a personal project for learning purposes.
