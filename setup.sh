#!/bin/bash

echo "================================"
echo "   FitCheck - Initial Setup"
echo "================================"
echo ""

# Check if we're in the correct directory
if [ ! -d "frontend" ] || [ ! -d "backend" ]; then
    echo "❌ Error: Please run this script from the fit-check root directory"
    exit 1
fi

echo "🔍 Checking prerequisites..."
echo ""

# Check Node.js
echo "Checking Node.js..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✅ Node.js $NODE_VERSION installed"
else
    echo "❌ Node.js is NOT installed"
    echo "   Download from: https://nodejs.org/"
    exit 1
fi

# Check Python
echo "Checking Python..."
if command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    echo "✅ $PYTHON_VERSION installed"
else
    echo "❌ Python is NOT installed"
    echo "   Download from: https://www.python.org/"
    exit 1
fi

echo ""
echo "📦 Setting up Backend..."
echo ""

# Backend setup
cd backend

# Create virtual environment
echo "Creating Python virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  venv already exists, skipping..."
else
    python -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Git Bash on Windows
    source venv/Scripts/activate
else
    # WSL/Linux/Mac
    source venv/bin/activate
fi

# Install dependencies
echo "Installing backend dependencies (this may take 1-2 minutes)..."
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✅ Backend dependencies installed"
else
    echo "❌ Failed to install backend dependencies"
    exit 1
fi

# Create .env if doesn't exist
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ Created .env file - PLEASE EDIT IT WITH YOUR CREDENTIALS"
else
    echo "⚠️  .env already exists, skipping..."
fi

# Create uploads folder
mkdir -p uploads
echo "✅ Created uploads folder"

cd ..

echo ""
echo "📦 Setting up Frontend..."
echo ""

# Frontend setup
cd frontend

# Install dependencies
echo "Installing frontend dependencies (this may take 2-5 minutes)..."
npm install
if [ $? -eq 0 ]; then
    echo "✅ Frontend dependencies installed"
else
    echo "❌ Failed to install frontend dependencies"
    exit 1
fi

# Create .env.local if doesn't exist
if [ ! -f ".env.local" ]; then
    cp .env.local.example .env.local
    echo "✅ Created .env.local file - PLEASE EDIT IT WITH YOUR CREDENTIALS"
else
    echo "⚠️  .env.local already exists, skipping..."
fi

cd ..

echo ""
echo "================================"
echo "   ✅ Setup Complete!"
echo "================================"
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Set up Supabase:"
echo "   - Create project at https://supabase.com"
echo "   - Create 'outfits' storage bucket (make it public)"
echo "   - Run the SQL from TROUBLESHOOTING.md to create the table"
echo ""
echo "2. Add your credentials:"
echo "   - Edit backend/.env with Supabase URL and SERVICE_ROLE_KEY"
echo "   - Edit frontend/.env.local with Supabase URL and ANON_KEY"
echo ""
echo "3. Start the servers:"
echo "   Terminal 1: cd backend && source venv/Scripts/activate && python app.py"
echo "   Terminal 2: cd frontend && npm run dev"
echo ""
echo "4. Open http://localhost:3000 in your browser"
echo ""
echo "⚠️  Having issues? Read TROUBLESHOOTING.md for detailed help"
echo ""
