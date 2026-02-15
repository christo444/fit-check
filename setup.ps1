# FitCheck Setup Script

Write-Host "================================" -ForegroundColor Cyan
Write-Host "   FitCheck - Initial Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the correct directory
if (-Not (Test-Path "frontend") -or -Not (Test-Path "backend")) {
    Write-Host "❌ Error: Please run this script from the fit-check root directory" -ForegroundColor Red
    exit 1
}

Write-Host "🔍 Checking prerequisites..." -ForegroundColor Yellow
Write-Host ""

# Check Node.js
Write-Host "Checking Node.js..."
try {
    $nodeVersion = node --version 2>&1
    if ($LASTEXITCODE -ne 0) { throw }
    Write-Host "✅ Node.js $nodeVersion installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js is NOT installed" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Node.js 18+ from https://nodejs.org/" -ForegroundColor Yellow
    Write-Host "Then restart VS Code and run this script again." -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# Check Python
Write-Host "Checking Python..."
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) { throw }
    Write-Host "✅ $pythonVersion installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Python is NOT installed" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Python 3.9+ from https://www.python.org/" -ForegroundColor Yellow
    Write-Host "IMPORTANT: Check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    Write-Host "Then restart VS Code and run this script again." -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

Write-Host ""

Write-Host "📦 Setting up Backend..." -ForegroundColor Yellow
Write-Host ""

# Backend setup
Set-Location backend

# Create virtual environment
Write-Host "Creating Python virtual environment..."
if (Test-Path "venv") {
    Write-Host "⚠️  venv already exists, skipping..." -ForegroundColor Yellow
} else {
    try {
        python -m venv venv
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to create virtual environment"
        }
        Write-Host "✅ Virtual environment created" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
        Write-Host "Error: $_" -ForegroundColor Yellow
        Set-Location ..
        exit 1
    }
}

# Activate virtual environment and install dependencies
Write-Host "Installing backend dependencies (this may take 1-2 minutes)..."
try {
    & .\venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        throw "pip install failed"
    }
    Write-Host "✅ Backend dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install backend dependencies" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "If you see 'Activate.ps1 cannot be loaded', run this command:" -ForegroundColor Yellow
    Write-Host "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Cyan
    Set-Location ..
    exit 1
}

# Create .env if doesn't exist
if (-Not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "✅ Created .env file - PLEASE EDIT IT WITH YOUR CREDENTIALS" -ForegroundColor Yellow
} else {
    Write-Host "⚠️  .env already exists, skipping..." -ForegroundColor Yellow
}

# Create uploads folder
if (-Not (Test-Path "uploads")) {
    New-Item -ItemType Directory -Path "uploads" | Out-Null
    Write-Host "✅ Created uploads folder" -ForegroundColor Green
}

Set-Location ..

Write-Host ""
Write-Host "📦 Setting up Frontend..." -ForegroundColor Yellow
Write-Host ""

# Frontend setup
Set-Location frontend

# Install dependencies
Write-Host "Installing frontend dependencies (this may take 2-5 minutes)..."
try {
    npm install
    if ($LASTEXITCODE -ne 0) {
        throw "npm install failed"
    }
    Write-Host "✅ Frontend dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install frontend dependencies" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Yellow
    Set-Location ..
    exit 1
}

# Create .env.local if doesn't exist
if (-Not (Test-Path ".env.local")) {
    Copy-Item ".env.local.example" ".env.local"
    Write-Host "✅ Created .env.local file - PLEASE EDIT IT WITH YOUR CREDENTIALS" -ForegroundColor Yellow
} else {
    Write-Host "⚠️  .env.local already exists, skipping..." -ForegroundColor Yellow
}

Set-Location ..

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "   ✅ Setup Complete!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📝 Next Steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Set up Supabase:" -ForegroundColor White
Write-Host "   - Create project at https://supabase.com" -ForegroundColor Gray
Write-Host "   - Create 'outfits' storage bucket (make it public)" -ForegroundColor Gray
Write-Host "   - Run the SQL from TROUBLESHOOTING.md to create the table" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Add your credentials:" -ForegroundColor White
Write-Host "   - Edit backend/.env with Supabase URL and SERVICE_ROLE_KEY" -ForegroundColor Gray
Write-Host "   - Edit frontend/.env.local with Supabase URL and ANON_KEY" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Start the servers:" -ForegroundColor White
Write-Host "   Terminal 1: cd backend; .\venv\Scripts\Activate.ps1; python app.py" -ForegroundColor Gray
Write-Host "   Terminal 2: cd frontend; npm run dev" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Open http://localhost:3000 in your browser" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  Having issues? Read TROUBLESHOOTING.md for detailed help" -ForegroundColor Yellow
Write-Host "📖 Full documentation in README.md" -ForegroundColor Cyan
Write-Host ""
