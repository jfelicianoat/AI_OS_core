# Script para ejecución de pruebas unitarias e integración en PowerShell
$ErrorActionPreference = "Stop"

Write-Host "Ejecutando suite de pruebas de AI OS Core (M0)..." -ForegroundColor Cyan

$env:PYTHONPATH = "src"

# Ejecutar con el runner de unittest estándar
python -m unittest discover -s tests -v

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nTodas las pruebas han pasado satisfactoriamente." -ForegroundColor Green
} else {
    Write-Host "`nHubo fallos en las pruebas." -ForegroundColor Red
}
