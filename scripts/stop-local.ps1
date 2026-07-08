param(
    [int]$ApiPort = 8000,
    [int]$WebPort = 5173,
    [switch]$StopDb
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$runtimeDir = Join-Path $root "(1).runtime"
$backendPidFile = Join-Path $runtimeDir "backend.pid"
$frontendPidFile = Join-Path $runtimeDir "frontend.pid"

function Stop-ProcessSafe {
    param([int]$ProcessId)
    try {
        $p = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
        if ($p) {
            Stop-Process -Id $ProcessId -Force -ErrorAction SilentlyContinue
            return $true
        }
    } catch {}
    return $false
}

function Stop-ByPidFile {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return $false }
    try {
        $pid = [int](Get-Content $Path -ErrorAction SilentlyContinue)
        $ok = Stop-ProcessSafe -ProcessId $pid
        Remove-Item $Path -Force -ErrorAction SilentlyContinue
        return $ok
    } catch {
        Remove-Item $Path -Force -ErrorAction SilentlyContinue
        return $false
    }
}

function Stop-ByPort {
    param([int]$Port)
    $stopped = $false
    try {
        $ids = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue |
            Select-Object -ExpandProperty OwningProcess -Unique
        foreach ($id in $ids) {
            if (Stop-ProcessSafe -ProcessId ([int]$id)) {
                $stopped = $true
            }
        }
    } catch {}
    return $stopped
}

Write-Host "=== SaglikCebim local stop ===" -ForegroundColor Cyan

$backendByFile = Stop-ByPidFile -Path $backendPidFile
$frontendByFile = Stop-ByPidFile -Path $frontendPidFile
$backendByPort = Stop-ByPort -Port $ApiPort
$frontendByPort = Stop-ByPort -Port $WebPort

if ($StopDb) {
    docker stop saglikcebim_db 2>$null | Out-Null
}

Write-Host "Backend (pid) : $backendByFile"
Write-Host "Frontend (pid): $frontendByFile"
Write-Host "Backend (port): $backendByPort"
Write-Host "Frontend(port): $frontendByPort"
Write-Host "DB stop       : $StopDb"
