@echo off
rem Cambia la URL del AI Broker a https:// en todas las apps, solo si el Broker ya sirve HTTPS.
rem Para deshacerlo: "Pasar apps a Broker HTTPS.bat" -Revertir
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\pasar-broker-a-https.ps1" %*
pause
