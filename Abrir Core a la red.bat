@echo off
rem AI OS Core - abre Core a la red local (con tokens) para que el runner del PC IA lo alcance,
rem y prepara "dist\Conectar runner a Core.bat" para copiarlo a ese PC.
rem Pide permiso de administrador (para el firewall). Para deshacerlo: "Abrir Core a la red.bat" -Deshacer
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\abrir_core_a_la_red.ps1" %*
if errorlevel 1 (
    echo.
    echo Algo ha fallado: el motivo esta encima de esta linea.
    pause
)
