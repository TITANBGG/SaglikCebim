# SaglikCebim - Backend Launcher
# Run this from backend directory: .\start.ps1

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗"
Write-Host "║                   🏥 SaglikCebim Backend                       ║"
Write-Host "║                     Starting...                               ║"
Write-Host "╚════════════════════════════════════════════════════════════════╝"
Write-Host ""

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Check venv
if (-not (Test-Path "venv")) {
    Write-Host "⚠️  Creating virtual environment..."
    & python -m venv venv
    Write-Host "✅ venv created"
}

Write-Host ""
Write-Host "✅ Starting API Server..."
Write-Host ""
Write-Host "🌐 Access points:"
Write-Host "   - API:    http://127.0.0.1:8000"
Write-Host "   - Docs:   http://127.0.0.1:8000/docs"
Write-Host "   - ReDoc:  http://127.0.0.1:8000/redoc"
Write-Host ""
Write-Host "⌚ Press CTRL+C to stop the server"
Write-Host ""
Write-Host "════════════════════════════════════════════════════════════════"
Write-Host ""

try {
    & .\venv\Scripts\python.exe run.py
}
catch {
    Write-Host "❌ Error: $_"
    exit 1
}
