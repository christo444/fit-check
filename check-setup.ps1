# Installation Check Script
# Run this to verify your setup is correct

Write-Host "================================" -ForegroundColor Cyan
Write-Host "   FitCheck Installation Check" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

$errors = 0

# Check Node.js
Write-Host "Checking Node.js..." -NoNewline
try {
    $nodeVersion = node --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host " ✅ $nodeVersion" -ForegroundColor Green
    } else {
        throw
    }
} catch {
    Write-Host " ❌ NOT FOUND" -ForegroundColor Red
    Write-Host "   Install from: https://nodejs.org/" -ForegroundColor Yellow
    $errors++
}

# Check Python
Write-Host "Checking Python..." -NoNewline
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host " ✅ $pythonVersion" -ForegroundColor Green
    } else {
        throw
    }
} catch {
    Write-Host " ❌ NOT FOUND" -ForegroundColor Red
    Write-Host "   Install from: https://www.python.org/" -ForegroundColor Yellow
    $errors++
}

# Check pip
Write-Host "Checking pip..." -NoNewline
try {
    $pipVersion = pip --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host " ✅ Installed" -ForegroundColor Green
    } else {
        throw
    }
} catch {
    Write-Host " ❌ NOT FOUND" -ForegroundColor Red
    $errors++
}

Write-Host ""
Write-Host "Checking project structure..." -ForegroundColor Cyan

# Check backend structure
Write-Host "Backend folder..." -NoNewline
if (Test-Path "backend") {
    Write-Host " ✅" -ForegroundColor Green
} else {
    Write-Host " ❌ MISSING" -ForegroundColor Red
    $errors++
}

Write-Host "Backend venv..." -NoNewline
if (Test-Path "backend/venv") {
    Write-Host " ✅" -ForegroundColor Green
} else {
    Write-Host " ⚠️  NOT CREATED" -ForegroundColor Yellow
    Write-Host "   Run: cd backend; python -m venv venv" -ForegroundColor Gray
}

Write-Host "Backend .env..." -NoNewline
if (Test-Path "backend/.env") {
    Write-Host " ✅" -ForegroundColor Green
    # Check if it has actual values
    $envContent = Get-Content "backend/.env" -Raw
    if ($envContent -match "your_.*_here") {
        Write-Host "   ⚠️  WARNING: .env contains placeholder values" -ForegroundColor Yellow
        Write-Host "   Update with your actual Supabase credentials" -ForegroundColor Gray
    }
} else {
    Write-Host " ❌ MISSING" -ForegroundColor Red
    Write-Host "   Run: cd backend; copy .env.example .env" -ForegroundColor Gray
    $errors++
}

Write-Host "Backend requirements..." -NoNewline
if (Test-Path "backend/requirements.txt") {
    Write-Host " ✅" -ForegroundColor Green
} else {
    Write-Host " ❌ MISSING" -ForegroundColor Red
    $errors++
}

# Check frontend structure
Write-Host "Frontend folder..." -NoNewline
if (Test-Path "frontend") {
    Write-Host " ✅" -ForegroundColor Green
} else {
    Write-Host " ❌ MISSING" -ForegroundColor Red
    $errors++
}

Write-Host "Frontend node_modules..." -NoNewline
if (Test-Path "frontend/node_modules") {
    Write-Host " ✅" -ForegroundColor Green
} else {
    Write-Host " ⚠️  NOT INSTALLED" -ForegroundColor Yellow
    Write-Host "   Run: cd frontend; npm install" -ForegroundColor Gray
}

Write-Host "Frontend .env.local..." -NoNewline
if (Test-Path "frontend/.env.local") {
    Write-Host " ✅" -ForegroundColor Green
    # Check if it has actual values
    $envContent = Get-Content "frontend/.env.local" -Raw
    if ($envContent -match "your_.*_here") {
        Write-Host "   ⚠️  WARNING: .env.local contains placeholder values" -ForegroundColor Yellow
        Write-Host "   Update with your actual Supabase credentials" -ForegroundColor Gray
    }
} else {
    Write-Host " ❌ MISSING" -ForegroundColor Red
    Write-Host "   Run: cd frontend; copy .env.local.example .env.local" -ForegroundColor Gray
    $errors++
}

Write-Host "Frontend package.json..." -NoNewline
if (Test-Path "frontend/package.json") {
    Write-Host " ✅" -ForegroundColor Green
} else {
    Write-Host " ❌ MISSING" -ForegroundColor Red
    $errors++
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan

if ($errors -eq 0) {
    Write-Host "✅ All checks passed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Make sure Supabase is configured (see TROUBLESHOOTING.md)" -ForegroundColor Gray
    Write-Host "2. Start backend: cd backend; .\venv\Scripts\Activate.ps1; python app.py" -ForegroundColor Gray
    Write-Host "3. Start frontend: cd frontend; npm run dev" -ForegroundColor Gray
} else {
    Write-Host "❌ Found $errors error(s)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Fix the errors above, then run:" -ForegroundColor Yellow
    Write-Host "  .\setup.ps1" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "For detailed help, see TROUBLESHOOTING.md" -ForegroundColor Gray
}

Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
