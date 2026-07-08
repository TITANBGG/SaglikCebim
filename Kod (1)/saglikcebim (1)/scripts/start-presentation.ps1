param(
    [int]$ApiPort = 8000,
    [int]$WebPort = 5173,
    [switch]$NoPortClean
)

$ErrorActionPreference = "Stop"
$ErrorActionPreference = "Continue" # Allow non-critical failures
Set-StrictMode -Version Latest

$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$backendDir = Join-Path $root "backend (1)"
$frontendDir = Join-Path $root "frontend"
$runtimeDir = Join-Path $root "(1).runtime"

Write-Host "--- SaglikCebim Sistem Baslatiliyor ---" -ForegroundColor Cyan
Write-Host "Root: $root"
Write-Host "Backend: $backendDir"
Write-Host "Frontend: $frontendDir"
Write-Host "Runtime: $runtimeDir"

New-Item -ItemType Directory -Path $runtimeDir -Force | Out-Null

$backendPidFile = Join-Path $runtimeDir "backend.pid"
$frontendPidFile = Join-Path $runtimeDir "frontend.pid"

function Stop-ProcessSafe {
    param([int]$ProcessId)
    try {
        $p = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
        if ($p) { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue }
    } catch {}
}

function Stop-ByPort {
    param([int]$Port)
    try {
        $ids = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue |
            Select-Object -ExpandProperty OwningProcess -Unique
        foreach ($id in $ids) {
            Stop-ProcessSafe -ProcessId ([int]$id)
        }
    } catch {}
}

function Wait-HttpOk {
    param(
        [string]$Url,
        [int]$TimeoutSec = 40
    )
    $maxAttempts = [Math]::Max(1, [int]($TimeoutSec * 2))
    for ($i = 0; $i -lt $maxAttempts; $i++) {
        try {
            $status = (Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 2).StatusCode
            if ($status -eq 200) {
                return $true
            }
        } catch {}
        Start-Sleep -Milliseconds 500
    }
    return $false
}

function Read-PidFile {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return $null }
    try { return [int](Get-Content $Path -ErrorAction SilentlyContinue) } catch { return $null }
}

# 1) Stop stale processes
$oldBackendPid = Read-PidFile -Path $backendPidFile
if ($null -ne $oldBackendPid) { Stop-ProcessSafe -ProcessId $oldBackendPid }
$oldFrontendPid = Read-PidFile -Path $frontendPidFile
if ($null -ne $oldFrontendPid) { Stop-ProcessSafe -ProcessId $oldFrontendPid }

if (-not $NoPortClean) {
    Stop-ByPort -Port $ApiPort
    Stop-ByPort -Port $WebPort
}

# 2) AI Dependency Check (Ollama for 'Neyim Var?')
Write-Host "Checking AI dependencies (Ollama)..." -ForegroundColor Yellow
try {
    $ollamaCheck = & ollama list 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "UYARI: Ollama bulunamadi. 'Neyim Var?' uygulamasi düzgün çalismayabilir." -ForegroundColor Red
    } else {
        if ($ollamaCheck -like "*llama3*") {
            Write-Host "Ollama ve Llama3 hazir." -ForegroundColor Green
        } else {
            Write-Host "UYARI: Ollama yüklü ama 'llama3' modeli bulunamadi. 'ollama pull llama3' komutu gerekebilir." -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "UYARI: Ollama kontrol edilemedi." -ForegroundColor Red
}

# 3) Start backend
$pythonExe = Join-Path $backendDir "venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    $pythonExe = "python"
}

Write-Host "Backend baslatiliyor ($ApiPort)..." -ForegroundColor Cyan
$backendOut = Join-Path $runtimeDir "backend.out.log"
$backendErr = Join-Path $runtimeDir "backend.err.log"
$backendArgs = @("-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "$ApiPort")

$backendProc = Start-Process `
    -FilePath $pythonExe `
    -ArgumentList $backendArgs `
    -WorkingDirectory $backendDir `
    -RedirectStandardOutput $backendOut `
    -RedirectStandardError $backendErr `
    -WindowStyle Hidden `
    -PassThru

Set-Content -Path $backendPidFile -Value $backendProc.Id

if (-not (Wait-HttpOk -Url "http://127.0.0.1:$ApiPort/health" -TimeoutSec 30)) {
    Write-Host "Backend acilamadi. Log: $backendErr" -ForegroundColor Red
} else {
    Write-Host "Backend hazir." -ForegroundColor Green
}

# 4) Start frontend (Vite Dev Server)
Write-Host "Frontend baslatiliyor ($WebPort)..." -ForegroundColor Cyan
$frontendOut = Join-Path $runtimeDir "frontend.out.log"
$frontendErr = Join-Path $runtimeDir "frontend.err.log"
# Using npm.cmd to avoid PS execution policy issues
$cmdText = "npm.cmd run dev -- --host 127.0.0.1 --port $WebPort"

$frontendProc = Start-Process `
    -FilePath $env:ComSpec `
    -ArgumentList @("/c", $cmdText) `
    -WorkingDirectory $frontendDir `
    -RedirectStandardOutput $frontendOut `
    -RedirectStandardError $frontendErr `
    -WindowStyle Hidden `
    -PassThru

Set-Content -Path $frontendPidFile -Value $frontendProc.Id

if (-not (Wait-HttpOk -Url "http://127.0.0.1:$WebPort" -TimeoutSec 60)) {
    Write-Host "Frontend acilamadi (Vite). Statik server denenebilir." -ForegroundColor Red
} else {
    Write-Host "Frontend hazir." -ForegroundColor Green
}

Write-Output ""
Write-Host "=== SaglikCebim Sistemi Tamamen Hazir ===" -ForegroundColor Green
Write-Output "Frontend : http://127.0.0.1:$WebPort"
Write-Output "Backend  : http://127.0.0.1:$ApiPort"
Write-Output "Neyim Var: http://127.0.0.1:$WebPort/neyim-var"
Write-Output "Loglar   : $runtimeDir"
