# Script de arranque local para AI OS Core en PowerShell
$ErrorActionPreference = "Stop"

Write-Host "Iniciando AI OS Core Service..." -ForegroundColor Cyan

# Definir variables de entorno locales si no existen
if (-not $env:AI_OS_ENV) { $env:AI_OS_ENV = "development" }
if (-not $env:AI_OS_HOST) { $env:AI_OS_HOST = "127.0.0.1" }
if (-not $env:AI_OS_PORT) { $env:AI_OS_PORT = "8000" }

# Asegurar PYTHONPATH
$env:PYTHONPATH = "src"

# Ejecutar con uvicorn
python -m uvicorn ai_os_core.app:app --host $env:AI_OS_HOST --port $env:AI_OS_PORT --reload
