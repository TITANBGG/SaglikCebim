param(
    [int]$ApiPort = 8001,
    [int]$WebPort = 5173
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$runtimeDir = Join-Path $root ".runtime"
$backendPidFile = Join-Path $runtimeDir "backend.pid"
$frontendPidFile = Join-Path $runtimeDir "frontend.pid"

function Stop-ProcessSafe {
    param([int]$ProcessId)
    try {
        Stop-Process -Id $ProcessId -Force -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

function Stop-ByPidFile {
    param([string]$Path)
    if (-not (Test-Path $Path)) {
        return $false
    }
    try {
        $pidVal = [int](Get-Content $Path -ErrorAction Stop)
        $stopped = Stop-ProcessSafe -ProcessId $pidVal
        Remove-Item $Path -Force -ErrorAction SilentlyContinue
        return $stopped
    } catch {
        Remove-Item $Path -Force -ErrorAction SilentlyContinue
        return $false
    }
}

function Stop-ByPort {
    param([int]$Port)
    $stoppedAny = $false
    try {
        $ids = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction Stop |
            Select-Object -ExpandProperty OwningProcess -Unique
        foreach ($id in $ids) {
            if (Stop-ProcessSafe -ProcessId ([int]$id)) {
                $stoppedAny = $true
            }
        }
    } catch {
    }
    return $stoppedAny
}

$backendStopped = Stop-ByPidFile -Path $backendPidFile
$frontendStopped = Stop-ByPidFile -Path $frontendPidFile

# Fallback cleanup in case pid files were stale.
$backendPortStopped = Stop-ByPort -Port $ApiPort
$frontendPortStopped = Stop-ByPort -Port $WebPort

Write-Host "Stop sonucu:"
Write-Host "Backend pid-file stop: $backendStopped"
Write-Host "Frontend pid-file stop: $frontendStopped"
Write-Host "Backend port cleanup : $backendPortStopped"
Write-Host "Frontend port cleanup: $frontendPortStopped"
