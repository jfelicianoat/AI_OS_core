<#
.SYNOPSIS
    Deja AI OS Core listo para que el runner de Agora del PC IA lo alcance, y prepara para ese
    PC un fichero que lo conecta con un doble clic.

.DESCRIPTION
    1. Tokens: AI_OS_API_TOKEN (director) y, en AI_OS_API_TOKENS, uno para `agora` (el runner) y
       otro para `gestion_tareas`. Respeta los que ya existan y crea solo los que falten.
       Se guardan como variables de entorno de tu usuario (no en ficheros del proyecto).
    2. AI_OS_HOST=0.0.0.0: Core abre ademas HTTPS en el 8443 para la red, con el certificado del
       tablero de Agora (C:\Agora\pki), firmado por la CA en la que el runner ya confia. El 8000
       (HTTP) sigue solo para este equipo: por la red no viajan tokens en claro.
    3. Firewall: abre el puerto 8443 solo a la red local (pide permiso de administrador).
    4. Genera "Conectar runner a Core.bat": copialo al PC IA y haz doble clic.

    -Deshacer quita AI_OS_HOST y la regla del firewall: Core vuelve a escuchar solo aqui.
    -Prueba no toca nada del sistema: solo genera el fichero y dice lo que haria.
#>
[CmdletBinding()]
param(
    [switch]$Deshacer,
    [switch]$Prueba,
    [string]$Salida,
    [string]$PcIa = '192.168.1.52',
    [int]$Puerto = 8443
)
$ErrorActionPreference = 'Stop'
# En Windows PowerShell 5.1 $PSScriptRoot aun esta vacio en los valores por defecto de param()
if (-not $Salida) { $Salida = Join-Path (Split-Path -Parent $PSScriptRoot) 'dist' }
$regla = 'AI OS Core (red local)'

# El firewall necesita administrador: se relanza elevado con los mismos parametros
$admin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $Prueba -and -not $admin) {
    $argumentos = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-NoExit', '-File', "`"$PSCommandPath`"")
    if ($Deshacer) { $argumentos += '-Deshacer' }
    Start-Process powershell -Verb RunAs -ArgumentList $argumentos
    exit 0
}

if ($Deshacer) {
    [Environment]::SetEnvironmentVariable('AI_OS_HOST', $null, 'User')
    Remove-NetFirewallRule -DisplayName $regla -ErrorAction SilentlyContinue
    Write-Host 'Hecho: Core vuelve a escuchar solo en este equipo (los tokens se conservan).' -ForegroundColor Green
    Write-Host 'Cierra la ventana de Core y abrelo de nuevo con "Arrancar AI OS Core.bat".'
    return
}

function Nuevo-Token { $b = New-Object byte[] 32; [Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($b)
    return [Convert]::ToBase64String($b).TrimEnd('=').Replace('+', '-').Replace('/', '_') }

# --- 1. Tokens ---------------------------------------------------------------
$director = [Environment]::GetEnvironmentVariable('AI_OS_API_TOKEN', 'User')
if (-not $director) { $director = Nuevo-Token }
$porApp = [ordered]@{}
foreach ($par in ([Environment]::GetEnvironmentVariable('AI_OS_API_TOKENS', 'User') -split ';')) {
    $app, $resto = $par -split '=', 2
    if ($app -and $resto) { $porApp[$app.Trim()] = $resto.Trim() }
}
foreach ($app in @('agora')) { if (-not $porApp.Contains($app)) { $porApp[$app] = Nuevo-Token } }
$tokens = ($porApp.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join ';'
$tokenAgora = ($porApp['agora'] -split '\|')[0]

# --- 2 y 3. Variables y firewall --------------------------------------------
if ($Prueba) {
    Write-Host '[prueba] no se tocan variables de entorno ni firewall' -ForegroundColor Yellow
} else {
    [Environment]::SetEnvironmentVariable('AI_OS_API_TOKEN', $director, 'User')
    [Environment]::SetEnvironmentVariable('AI_OS_API_TOKENS', $tokens, 'User')
    [Environment]::SetEnvironmentVariable('AI_OS_HOST', '0.0.0.0', 'User')
    # La regla de versiones anteriores abria el 8000 (HTTP): se rehace para el puerto HTTPS
    Remove-NetFirewallRule -DisplayName $regla -ErrorAction SilentlyContinue
    New-NetFirewallRule -DisplayName $regla -Direction Inbound -Protocol TCP -LocalPort $Puerto `
        -RemoteAddress LocalSubnet -Action Allow | Out-Null
    Write-Host "Variables guardadas y puerto $Puerto abierto solo a la red local." -ForegroundColor Green
}

# --- 4. Fichero para el PC IA ------------------------------------------------
$ip = (Find-NetRoute -RemoteIPAddress $PcIa -ErrorAction SilentlyContinue | Where-Object IPAddress | Select-Object -First 1).IPAddress
if (-not $ip) { throw "No encuentro la IP de este equipo en la red del PC IA ($PcIa)." }
$coreUrl = "https://${ip}:$Puerto"
if (-not (Test-Path 'C:\Agora\pki\server.crt')) { throw 'Falta C:\Agora\pki\server.crt: Core lo usa para el HTTPS de la red.' }

$agoraDist = Join-Path (Split-Path -Parent (Split-Path -Parent $PSScriptRoot)) 'Agora\dist'
$base = Get-ChildItem $agoraDist -Filter 'Actualizar runner Agora *.bat' -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $base) { throw "No encuentro 'Actualizar runner Agora <version>.bat' en $agoraDist. Generalo con Agora\scripts\build-runner-package.ps1." }
$contenido = Get-Content $base.FullName -Raw
$orden = 'actualizar-runner.ps1" %*'
if (-not $contenido.Contains($orden)) { throw "El fichero $($base.Name) no tiene la forma esperada." }
$contenido = $contenido.Replace($orden, "actualizar-runner.ps1`" -CoreUrl `"$coreUrl`" -CoreToken `"$tokenAgora`" %*")
$contenido = $contenido.Replace('rem Copia SOLO este fichero al PC IA', "rem Ademas conecta el runner a AI OS Core ($coreUrl). Lleva su token: borralo tras usarlo.`r`nrem Copia SOLO este fichero al PC IA")
New-Item -ItemType Directory -Force -Path $Salida | Out-Null
$destino = Join-Path $Salida 'Conectar runner a Core.bat'
[IO.File]::WriteAllText($destino, $contenido, [Text.Encoding]::ASCII)

Write-Host ''
Write-Host '== Listo. Ahora:' -ForegroundColor Cyan
Write-Host '1. Cierra la ventana de AI OS Core y abrelo otra vez con "Arrancar AI OS Core.bat".'
Write-Host '   El monitor se abre solo, ya con su token.'
Write-Host "2. Copia al PC IA y haz doble clic en:"
Write-Host "      $destino" -ForegroundColor White
Write-Host '   (lleva el token del runner: borra el fichero cuando termine)'
Write-Host '3. Nada mas: las apps de este equipo toman su token de Core solas (no hay que pegar ninguno).'
Write-Host ''
Write-Host 'Para volver atras: "Abrir Core a la red.bat" con -Deshacer (ver README).'
