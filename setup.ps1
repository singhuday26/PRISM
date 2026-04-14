# PRISM Windows Setup Script
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   🌐 PRISM - Windows Quick Setup" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# 1. Check for Python
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Python not found. Please install Python 3.11+." -ForegroundColor Red
    exit
}

# 2. Setup Virtual Environment if missing
if (!(Test-Path ".venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
}

# 3. Install Dependencies
Write-Host "📦 Installing dependencies from requirements.txt..." -ForegroundColor Yellow
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt

# 4. Check .env
if (!(Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Write-Host "⚠️  Creating .env from .env.example..." -ForegroundColor Yellow
        Copy-Item ".env.example" ".env"
    }
}

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host "To start PRISM, run:" -ForegroundColor White
Write-Host "    python prism.py start" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
