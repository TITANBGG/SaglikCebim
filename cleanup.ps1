# SaglikCebim - Temizleme Script'i
# Yuksek boyutlu dosyaları ve cache'i sil

Write-Host "=== Proje Temizleme ===" -ForegroundColor Yellow

$foldersToClean = @(
    "backend/node_modules",
    "backend/__pycache__",
    "backend/.pytest_cache",
    "backend/uploads",
    "frontend/node_modules",
    "frontend/dist",
    "frontend/dev-dist",
    "frontend/.vite"
)

$totalSize = 0

foreach ($folder in $foldersToClean) {
    if (Test-Path $folder) {
        $folderSize = (Get-ChildItem -Path $folder -Recurse -Force | Measure-Object -Property Length -Sum).Sum / 1MB
        Write-Host "Siliniyor: $folder (~${folderSize}MB)" -ForegroundColor Cyan
        Remove-Item -Recurse -Force $folder -ErrorAction SilentlyContinue
        $totalSize += $folderSize
    }
}

Write-Host ""
Write-Host "[OK] Temizlik tamamlandi. Silinen boyut: ~${totalSize}MB" -ForegroundColor Green
Write-Host ""
Write-Host "Docker cache silebilirsiniz (opsiyonel):" -ForegroundColor Cyan
Write-Host "docker builder prune" -ForegroundColor Gray
