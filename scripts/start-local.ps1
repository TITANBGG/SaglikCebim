param(
    [int]$ApiPort = 8000,
    [int]$WebPort = 5173,
    [int]$DbPort = 5433
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$backendDir = Join-Path $root "backend (1)"
$frontendDir = Join-Path $root "frontend"
$runtimeDir = Join-Path $root "(1).runtime"

$backendPidFile = Join-Path $runtimeDir "backend.pid"
$frontendPidFile = Join-Path $runtimeDir "frontend.pid"
$backendOut = Join-Path $runtimeDir "backend.out.log"
$backendErr = Join-Path $runtimeDir "backend.err.log"
$frontendOut = Join-Path $runtimeDir "frontend.out.log"
$frontendErr = Join-Path $runtimeDir "frontend.err.log"

function Stop-ProcessSafe {
    param([int]$ProcessId)
    try {
        $p = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
        if ($p) {
            Stop-Process -Id $ProcessId -Force -ErrorAction SilentlyContinue
        }
    } catch {}
}

function Read-PidFile {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return $null }
    try {
        return [int](Get-Content $Path -ErrorAction SilentlyContinue)
    } catch {
        return $null
    }
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

function Wait-Http200 {
    param(
        [string]$Url,
        [int]$TimeoutSec = 45
    )
    $max = [Math]::Max(1, [int]($TimeoutSec * 2))
    for ($i = 0; $i -lt $max; $i++) {
        try {
            $res = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 2
            if ($res.StatusCode -eq 200) { return $true }
        } catch {}
        Start-Sleep -Milliseconds 500
    }
    return $false
}

Write-Host "=== SaglikCebim local start ===" -ForegroundColor Cyan
Write-Host "Root: $root"

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "docker komutu bulunamadi. Docker Desktop acik olmali."
}
if (-not (Get-Command npm.cmd -ErrorAction SilentlyContinue)) {
    throw "npm.cmd bulunamadi. Node.js kurulumu kontrol edilmeli."
}

if (-not (Test-Path $backendDir)) { throw "Backend klasoru bulunamadi: $backendDir" }
if (-not (Test-Path $frontendDir)) { throw "Frontend klasoru bulunamadi: $frontendDir" }

New-Item -ItemType Directory -Path $runtimeDir -Force | Out-Null

# 1) Eski local processleri kapat
$oldBackend = Read-PidFile -Path $backendPidFile
if ($null -ne $oldBackend) { Stop-ProcessSafe -ProcessId $oldBackend }
$oldFrontend = Read-PidFile -Path $frontendPidFile
if ($null -ne $oldFrontend) { Stop-ProcessSafe -ProcessId $oldFrontend }

# Port temizligi
Stop-ByPort -Port $ApiPort
Stop-ByPort -Port $WebPort

# 2) Sadece DB konteynerini ac, docker backend/frontend kapat
Set-Location $root
docker compose up -d db | Out-Null
docker stop saglikcebim_backend 2>$null | Out-Null
docker stop saglikcebim_frontend 2>$null | Out-Null

# 3) Backend local
$pythonExe = Join-Path $backendDir "venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    throw "Python venv bulunamadi: $pythonExe"
}

$backendArgs = @("-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "$ApiPort")
$backendProc = Start-Process -FilePath $pythonExe `
    -ArgumentList $backendArgs `
    -WorkingDirectory $backendDir `
    -RedirectStandardOutput $backendOut `
    -RedirectStandardError $backendErr `
    -WindowStyle Hidden `
    -PassThru
Set-Content -Path $backendPidFile -Value $backendProc.Id

if (-not (Wait-Http200 -Url "http://127.0.0.1:$ApiPort/health" -TimeoutSec 35)) {
    throw "Backend ayaga kalkmadi. Log: $backendErr"
}

# 4) Frontend local (node_modules yoksa install)
if (-not (Test-Path (Join-Path $frontendDir "node_modules"))) {
    Push-Location $frontendDir
    npm.cmd install
    Pop-Location
}

$frontendCmd = "npm.cmd run dev -- --host 127.0.0.1 --port $WebPort"
$frontendProc = Start-Process -FilePath $env:ComSpec `
    -ArgumentList @("/c", $frontendCmd) `
    -WorkingDirectory $frontendDir `
    -RedirectStandardOutput $frontendOut `
    -RedirectStandardError $frontendErr `
    -WindowStyle Hidden `
    -PassThru
Set-Content -Path $frontendPidFile -Value $frontendProc.Id

if (-not (Wait-Http200 -Url "http://127.0.0.1:$WebPort" -TimeoutSec 60)) {
    throw "Frontend ayaga kalkmadi. Log: $frontendErr"
}

# 5) Ollama bilgilendirme
try {
    $ollamaRes = Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 3
    if ($ollamaRes.StatusCode -eq 200) {
        Write-Host "Ollama: hazir (11434)" -ForegroundColor Green
    }
} catch {
    Write-Host "UYARI: Ollama erisilemiyor. Chat/AI ozellikleri etkilenebilir." -ForegroundColor Yellow
}

Write-Host "" 
Write-Host "=== Sistem Hazir ===" -ForegroundColor Green
Write-Host "Frontend : http://127.0.0.1:$WebPort"
Write-Host "Backend  : http://127.0.0.1:$ApiPort"
Write-Host "DB Port  : $DbPort"
Write-Host "Loglar   : $runtimeDir"
