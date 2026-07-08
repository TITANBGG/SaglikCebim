# ============================================
# SaglikCebim Backend Setup - Windows
# ============================================

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "  SaglikCebim Backend Setup" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# ============================================
# STEP 1: Virtual Environment
# ============================================
Write-Host "Step 1/6: Virtual Environment" -ForegroundColor Yellow
if (-not (Test-Path "venv")) {
    Write-Host "   Creating..." -ForegroundColor Gray
    python -m venv venv
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   [OK] Created" -ForegroundColor Green
    } else {
        Write-Host "   [ERROR] venv creation failed" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "   [OK] Already exists" -ForegroundColor Green
}

# ============================================
# STEP 2: Activate venv
# ============================================
Write-Host ""
Write-Host "Step 2/6: Activate venv" -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1
Write-Host "   [OK] Activated" -ForegroundColor Green

# ============================================
# STEP 3: Install dependencies
# ============================================
Write-Host ""
Write-Host "Step 3/6: Installing dependencies" -ForegroundColor Yellow
Write-Host "   This may take a moment..." -ForegroundColor Gray
pip install -q -r requirements.txt 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "   [OK] Installed (20+ packages)" -ForegroundColor Green
} else {
    Write-Host "   [ERROR] pip install failed" -ForegroundColor Red
    Write-Host "   Run manually: pip install -r requirements.txt" -ForegroundColor Gray
    exit 1
}

# ============================================
# STEP 4: Environment config
# ============================================
Write-Host ""
Write-Host "Step 4/6: Environment configuration" -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Write-Host "   Creating .env from template..." -ForegroundColor Gray
    Copy-Item .env.example .env -Force
    Write-Host "   [OK] .env created" -ForegroundColor Green
    Write-Host ""
    Write-Host "   [WARNING] Please edit .env file!" -ForegroundColor Yellow
    Write-Host "   Location: $PWD\.env" -ForegroundColor Gray
    Write-Host "   Required: DATABASE_URL, SECRET_KEY, VAPID_KEYS" -ForegroundColor Gray
} else {
    Write-Host "   [OK] .env already exists" -ForegroundColor Green
}

# ============================================
# STEP 5: Database migrations
# ============================================
Write-Host ""
Write-Host "Step 5/6: Database migrations" -ForegroundColor Yellow
Write-Host "   Running..." -ForegroundColor Gray
$output = alembic upgrade head 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   [OK] Migrations completed" -ForegroundColor Green
} else {
    Write-Host "   [WARNING] Migration failed" -ForegroundColor Yellow
    Write-Host "   Run manually: alembic upgrade head" -ForegroundColor Gray
}

# ============================================
# STEP 6: Create directories
# ============================================
Write-Host ""
Write-Host "Step 6/6: Create directories" -ForegroundColor Yellow
if (-not (Test-Path "uploads")) {
    New-Item -ItemType Directory -Path "uploads" | Out-Null
    Write-Host "   [OK] uploads/ created" -ForegroundColor Green
} else {
    Write-Host "   [OK] uploads/ exists" -ForegroundColor Green
}

# ============================================
# SUCCESS
# ============================================
Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Next steps:" -ForegroundColor White
Write-Host ""
Write-Host "1. Start backend:" -ForegroundColor Cyan
Write-Host "   uvicorn app.main:app --reload" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. Test:" -ForegroundColor Cyan
Write-Host "   - Browser: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "   - curl: curl http://localhost:8000/health" -ForegroundColor Yellow
Write-Host ""
Write-Host "3. Start frontend (new terminal):" -ForegroundColor Cyan
Write-Host "   cd ../frontend && npm install && npm run dev" -ForegroundColor Yellow
Write-Host ""
