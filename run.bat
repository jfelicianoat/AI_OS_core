@echo off
setlocal enabledelayedexpansion
title AI OS Core - Launcher

cd /d "%~dp0"
set "PYTHONPATH=%~dp0src"
rem Donde escucha Core. Por defecto solo este equipo; para que llegue el runner del PC IA:
rem   setx AI_OS_HOST 0.0.0.0  (y entonces, tokens: AI_OS_API_TOKEN y AI_OS_API_TOKENS)
if not defined AI_OS_HOST set "AI_OS_HOST=127.0.0.1"
if not "%AI_OS_HOST%"=="127.0.0.1" if not defined AI_OS_API_TOKEN (
    echo AI_OS_HOST=%AI_OS_HOST% abre Core a la red: define antes AI_OS_API_TOKEN ^(y AI_OS_API_TOKENS^).
    echo Sin token cualquiera en la red podria cambiar politicas. No se arranca.
    pause
    exit /b 1
)

if exist "%~dp0.venv\Scripts\activate.bat" (
    call "%~dp0.venv\Scripts\activate.bat"
) else if exist "%~dp0venv\Scripts\activate.bat" (
    call "%~dp0venv\Scripts\activate.bat"
)

if not "%~1"=="" (
    set "CHOICE=%~1"
    goto EXECUTE_COMMAND
)

:MENU
cls
echo =====================================================================
echo                AI OS CORE - CONTROL PLANE LAUNCHER
echo =====================================================================
echo.
echo  [1] Arrancar Servicio API Completo (FastAPI + Uvicorn)
echo  [2] Ejecutar Suite de Pruebas Automatizadas (pytest / unittest)
echo  [3] Aplicar Migraciones de Base de Datos SQLite (Bootstrap)
echo  [4] Ejecutar Smoke Tests de Endpoints
echo  [5] Abrir Documentacion Interactiva de la API (Swagger UI)
echo  [6] Salir
echo.
echo =====================================================================
set /p CHOICE="Selecciona una opcion (1-6): "

:EXECUTE_COMMAND
if /i "%CHOICE%"=="1" goto START_APP
if /i "%CHOICE%"=="app" goto START_APP
if /i "%CHOICE%"=="api" goto START_APP

if /i "%CHOICE%"=="2" goto RUN_TESTS
if /i "%CHOICE%"=="test" goto RUN_TESTS
if /i "%CHOICE%"=="tests" goto RUN_TESTS

if /i "%CHOICE%"=="3" goto RUN_MIGRATIONS
if /i "%CHOICE%"=="migrate" goto RUN_MIGRATIONS
if /i "%CHOICE%"=="bootstrap" goto RUN_MIGRATIONS

if /i "%CHOICE%"=="4" goto RUN_SMOKE
if /i "%CHOICE%"=="smoke" goto RUN_SMOKE

if /i "%CHOICE%"=="5" goto OPEN_DOCS
if /i "%CHOICE%"=="docs" goto OPEN_DOCS

if /i "%CHOICE%"=="6" goto EXIT_SCRIPT
if /i "%CHOICE%"=="exit" goto EXIT_SCRIPT

echo Opcion invalida: %CHOICE%
timeout /t 2 >nul
goto MENU

:START_APP
cls
echo =====================================================================
echo  Iniciando AI OS Core Service en http://127.0.0.1:8000
echo =====================================================================
echo  Monitor visual:           http://127.0.0.1:8000/monitor
echo  Swagger UI disponible en: http://127.0.0.1:8000/docs
echo  Presiona Ctrl+C para detener el servicio.
echo =====================================================================
rem El monitor reintenta solo hasta que Core responde: se puede abrir antes de arrancar
start "" http://127.0.0.1:8000/monitor
python -m uvicorn ai_os_core.app:app --host %AI_OS_HOST% --port 8000 --reload
if not "%~1"=="" goto EXIT_SCRIPT
pause
goto MENU

:RUN_TESTS
cls
echo =====================================================================
echo  Ejecutando Suite de Pruebas de AI OS Core
echo =====================================================================
python -m pytest -v
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Pytest no disponible o con fallos. Intentando con unittest...
    python -m unittest discover -s tests -v
)
echo.
if not "%~1"=="" goto EXIT_SCRIPT
pause
goto MENU

:RUN_MIGRATIONS
cls
echo =====================================================================
echo  Aplicando Migraciones SQL Forward-Only en SQLite
echo =====================================================================
python -c "from ai_os_core.bootstrap import bootstrap_database; applied = bootstrap_database(); print('Migraciones completadas. Versiones aplicadas:', applied)"
echo.
if not "%~1"=="" goto EXIT_SCRIPT
pause
goto MENU

:RUN_SMOKE
cls
echo =====================================================================
echo  Ejecutando Smoke Tests de Endpoints REST
echo =====================================================================
python -m unittest tests/integration/test_api_smoke.py -v
echo.
if not "%~1"=="" goto EXIT_SCRIPT
pause
goto MENU

:OPEN_DOCS
cls
echo =====================================================================
echo  Abriendo Swagger UI en el navegador y arrancando servidor...
echo =====================================================================
start http://127.0.0.1:8000/docs
python -m uvicorn ai_os_core.app:app --host %AI_OS_HOST% --port 8000 --reload
if not "%~1"=="" goto EXIT_SCRIPT
pause
goto MENU

:EXIT_SCRIPT
echo Saliendo...
endlocal
exit /b 0
