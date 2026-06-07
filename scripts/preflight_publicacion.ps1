param(
    [switch]$SkipTests
)

$ErrorActionPreference = "Stop"

Write-Host "== Somatocarta preflight de publicacion =="

$status = git status --short
$blockedPatterns = @(
    "^\?\? \.env$",
    "^ M \.env$",
    "^A  \.env$",
    "Respaldo.*\.zip$",
    "src/backend/static/uploads/.*\.(jpg|jpeg|png)$",
    "\.log$"
)

$blocked = @()
foreach ($line in $status) {
    foreach ($pattern in $blockedPatterns) {
        if ($line -match $pattern) {
            $blocked += $line
            break
        }
    }
}

if ($blocked.Count -gt 0) {
    Write-Host ""
    Write-Host "Archivos que requieren revision antes de publicar:" -ForegroundColor Yellow
    $blocked | ForEach-Object { Write-Host "  $_" -ForegroundColor Yellow }
    Write-Host ""
    Write-Host "No se modifico nada. Revisa docs/publicacion.md antes de hacer commit." -ForegroundColor Yellow
} else {
    Write-Host "No se detectaron archivos bloqueantes en git status."
}

if (-not $SkipTests) {
    Write-Host ""
    Write-Host "Ejecutando pruebas..."
    .\.venv\Scripts\python.exe -m pytest -v
}

Write-Host ""
Write-Host "Preflight terminado."
