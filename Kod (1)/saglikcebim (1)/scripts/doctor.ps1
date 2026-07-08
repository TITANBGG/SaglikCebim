param(
    [int]$ApiPort = 8000,
    [int]$WebPort = 5173
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Check-Url {
    param([string]$Url)
    try {
        $status = (Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 3).StatusCode
        return "$status"
    } catch {
        return "DOWN"
    }
}

$backendHealth = Check-Url -Url "http://127.0.0.1:$ApiPort/health"
$frontendHealth = Check-Url -Url "http://127.0.0.1:$WebPort"

Write-Host "Health check:"
Write-Host "Backend http://127.0.0.1:$ApiPort/health -> $backendHealth"
Write-Host "Frontend http://127.0.0.1:$WebPort -> $frontendHealth"

if ($backendHealth -ne "200") {
    exit 1
}

try {
    $openapi = Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:$ApiPort/openapi.json" -TimeoutSec 5
    $paths = $openapi.paths.PSObject.Properties.Name
    $daily = $paths -contains "/articles/daily"
    $search = $paths -contains "/articles/search"
    $chat = $paths -contains "/articles/chat"
    Write-Host "Articles endpoints:"
    Write-Host "/articles/daily -> $daily"
    Write-Host "/articles/search -> $search"
    Write-Host "/articles/chat -> $chat"
    if ((-not $daily) -or (-not $search) -or (-not $chat)) {
        exit 2
    }
} catch {
    Write-Host "OpenAPI kontrolu basarisiz: $($_.Exception.Message)"
    exit 3
}
