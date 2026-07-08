param(
    [ValidateSet("local", "docker")]
    [string]$Mode = "local",
    [switch]$Rebuild,
    [int]$BackendPort = 8000,
    [int]$FrontendPort = 80,
    [int]$TimeoutSec = 180
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Set-Location $PSScriptRoot

function Wait-HttpOk {
    param(
        [string]$Url,
        [int]$TimeoutSec = 60
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSec)
    while ((Get-Date) -lt $deadline) {
        try {
            $status = (Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 3).StatusCode
            if ($status -eq 200) {
                return $true
            }
        } catch {
        }
        Start-Sleep -Seconds 2
    }

    return $false
}

function Invoke-DockerCommand {
    param(
        [string[]]$Args,
        [switch]$AllowFailure
    )

    & docker @Args
    $exitCode = $LASTEXITCODE
    if (($exitCode -ne 0) -and (-not $AllowFailure)) {
        throw "docker $($Args -join ' ') failed with exit code $exitCode"
    }
    return $exitCode
}

function Ensure-DockerAccess {
    try {
        Invoke-DockerCommand -Args @("version") | Out-Null
    } catch {
        Write-Host "Docker access failed." -ForegroundColor Red
        Write-Host "Check these items:" -ForegroundColor Yellow
        Write-Host "  1. Docker Desktop is running." -ForegroundColor Gray
        Write-Host "  2. Your user can access the Docker engine." -ForegroundColor Gray
        Write-Host "  3. If needed, open PowerShell as Administrator once or add your user to docker-users." -ForegroundColor Gray
        exit 1
    }
}

function Ensure-ComposeEnv {
    if (Test-Path ".env") {
        return
    }

    $randomSecret = [Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Maximum 256 }))
    $randomPass = [Guid]::NewGuid().ToString("N")
    @"
POSTGRES_DB=saglikcebim
POSTGRES_USER=saglikcebim_user
POSTGRES_PASSWORD=$randomPass
SECRET_KEY=$randomSecret
"@ | Out-File -Encoding ascii ".env"
}

function Start-LocalMode {
    Write-Host "Local mode starting..." -ForegroundColor Cyan
    Write-Host "Frontend will run on http://127.0.0.1:5173" -ForegroundColor Gray
    Write-Host "Backend will run on http://127.0.0.1:8000" -ForegroundColor Gray
    Write-Host ""

    & powershell -ExecutionPolicy Bypass -File ".\scripts\start-presentation.ps1"
    exit $LASTEXITCODE
}

function Start-DockerMode {
    $composeArgs = @("compose", "-f", "docker-compose.prod.yml")

    Write-Host "Docker mode starting..." -ForegroundColor Cyan
    Write-Host "Rebuild: $Rebuild" -ForegroundColor Gray
    Write-Host ""

    Ensure-DockerAccess
    Ensure-ComposeEnv

    $upArgs = $composeArgs + @("up", "-d")
    if ($Rebuild) {
        $upArgs += "--build"
    }

    Invoke-DockerCommand -Args $upArgs | Out-Null

    Write-Host "Waiting for backend health..." -ForegroundColor Yellow
    if (-not (Wait-HttpOk -Url "http://127.0.0.1:$BackendPort/health" -TimeoutSec $TimeoutSec)) {
        Write-Host "Backend did not become healthy in time." -ForegroundColor Red
        Invoke-DockerCommand -Args ($composeArgs + @("ps")) -AllowFailure | Out-Null
        exit 1
    }

    $migrationOk = $false
    for ($attempt = 1; $attempt -le 5; $attempt++) {
        $exitCode = Invoke-DockerCommand -Args ($composeArgs + @("exec", "-T", "backend", "alembic", "upgrade", "head")) -AllowFailure
        if ($exitCode -eq 0) {
            $migrationOk = $true
            break
        }

        Write-Host "Migration attempt $attempt/5 failed, retrying..." -ForegroundColor Yellow
        Start-Sleep -Seconds 3
    }

    if (-not $migrationOk) {
        Write-Host "Database migrations failed." -ForegroundColor Red
        Invoke-DockerCommand -Args ($composeArgs + @("logs", "--tail", "80", "backend")) -AllowFailure | Out-Null
        exit 1
    }

    Write-Host "Waiting for frontend..." -ForegroundColor Yellow
    if (-not (Wait-HttpOk -Url "http://127.0.0.1:$FrontendPort" -TimeoutSec $TimeoutSec)) {
        Write-Host "Frontend did not become healthy in time." -ForegroundColor Red
        Invoke-DockerCommand -Args ($composeArgs + @("ps")) -AllowFailure | Out-Null
        exit 1
    }

    Write-Host ""
    Write-Host "SaglikCebim is ready." -ForegroundColor Green
    Write-Host "Frontend: http://localhost" -ForegroundColor Yellow
    Write-Host "Backend : http://localhost:$BackendPort" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Daily use:" -ForegroundColor Cyan
    Write-Host "  .\\setup.ps1" -ForegroundColor Gray
    Write-Host "Docker full stack:" -ForegroundColor Cyan
    Write-Host "  .\\setup.ps1 -Mode docker" -ForegroundColor Gray
    Write-Host "Rebuild images:" -ForegroundColor Cyan
    Write-Host "  .\\setup.ps1 -Mode docker -Rebuild" -ForegroundColor Gray
}

Write-Host "================================" -ForegroundColor Cyan
Write-Host "  SaglikCebim Startup" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

switch ($Mode) {
    "local" {
        Start-LocalMode
    }
    "docker" {
        Start-DockerMode
    }
}
