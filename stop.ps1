param(
    [ValidateSet("local", "docker")]
    [string]$Mode = "local"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Set-Location $PSScriptRoot

function Stop-LocalMode {
    Write-Host "Stopping local mode..." -ForegroundColor Cyan
    & powershell -ExecutionPolicy Bypass -File ".\scripts\stop-presentation.ps1"
    exit $LASTEXITCODE
}

function Stop-DockerMode {
    Write-Host "Stopping docker mode..." -ForegroundColor Cyan
    & docker compose -f docker-compose.prod.yml down
    exit $LASTEXITCODE
}

switch ($Mode) {
    "local" {
        Stop-LocalMode
    }
    "docker" {
        Stop-DockerMode
    }
}
