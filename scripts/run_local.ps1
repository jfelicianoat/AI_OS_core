# Script de arranque local para AI OS Core en PowerShell
$ErrorActionPreference = "Stop"

Write-Host "Iniciando AI OS Core Service..." -ForegroundColor Cyan

if (-not $env:AI_OS_ENV) { $env:AI_OS_ENV = "development" }
$env:PYTHONPATH = "src"

# Siempre con serve: HTTP sólo en 127.0.0.1 y, si AI_OS_HOST abre a la red, HTTPS con certificado.
# Antes se llamaba a uvicorn con --host $env:AI_OS_HOST: con AI_OS_HOST=0.0.0.0 (lo deja
# «Abrir Core a la red.bat») Core quedaba en HTTP sin cifrar para toda la red, tokens incluidos.
python -m ai_os_core.serve
