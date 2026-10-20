<#
.SYNOPSIS
    Cambia la URL del AI Broker de http:// a https:// en todas las apps de este PC.

.DESCRIPTION
    Se ejecuta UNA vez, cuando el programador del PC IA ya sirve el Broker en HTTPS con el
    certificado de la AI Broker CA. Antes de tocar nada comprueba que el Broker contesta por
    HTTPS y que su certificado lo firma esa CA; si no, no cambia nada.

    Las apps ya confian en C:\Agora\pki-broker\ca.crt solo para el Broker (AI_BROKER_CA_CERT la
    cambia). Este script solo cambia la URL guardada en cada sitio:
      - Athena, Gestion Tareas IA, Knowledge Orchestrator, Trading AI (cada workspace):
        sus settings de usuario.
      - Model_Drift (model_drift.yaml), ChatyGPT (Arrancar ChatyGPT.bat y su .ps1) y el
        monitor de AI OS Core (config\apps.json).
    Cada fichero cambiado deja una copia <fichero>.antes-https.bak.
    Local AI Lab guarda la URL en su propia ventana (Broker): se cambia alli una vez.
    -Revertir hace el cambio contrario (https -> http).
#>
param(
    [string]$BrokerHost = "192.168.1.52:8765",
    [string]$CaPath = $(if ($env:AI_BROKER_CA_CERT) { $env:AI_BROKER_CA_CERT } else { "C:\Agora\pki-broker\ca.crt" }),
    [string]$Proyectos = "D:\Desarrollo\Proyectos TFM",
    [string]$KoRoot = "I:\KO-datos",
    [switch]$Revertir,
    [switch]$SinComprobar
)
$ErrorActionPreference = 'Stop'

$desde = if ($Revertir) { "https://$BrokerHost" } else { "http://$BrokerHost" }
$hacia = if ($Revertir) { "http://$BrokerHost" } else { "https://$BrokerHost" }

# -- 1. El Broker ya sirve HTTPS con la AI Broker CA? --------------------------
if (-not $Revertir -and -not $SinComprobar) {
    if (-not (Test-Path -LiteralPath $CaPath)) { throw "No encuentro la CA del Broker en $CaPath" }
    [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
    if (-not ('BrokerCaTrust' -as [type])) {
        Add-Type -TypeDefinition @'
using System.Net;
using System.Net.Security;
using System.Security.Cryptography.X509Certificates;
public static class BrokerCaTrust {
    static X509Certificate2 Ca;
    public static void Enable(string path) {
        Ca = new X509Certificate2(path);
        ServicePointManager.ServerCertificateValidationCallback = Check;
    }
    static bool Check(object sender, X509Certificate certificate, X509Chain chain, SslPolicyErrors errors) {
        if (errors == SslPolicyErrors.None) return true;
        if (errors != SslPolicyErrors.RemoteCertificateChainErrors) return false;
        using (var own = new X509Chain()) {
            own.ChainPolicy.RevocationMode = X509RevocationMode.NoCheck;
            own.ChainPolicy.VerificationFlags = X509VerificationFlags.AllowUnknownCertificateAuthority;
            own.ChainPolicy.ExtraStore.Add(Ca);
            if (!own.Build(new X509Certificate2(certificate))) return false;
            return own.ChainElements[own.ChainElements.Count - 1].Certificate.Thumbprint == Ca.Thumbprint;
        }
    }
}
'@
    }
    [BrokerCaTrust]::Enable($CaPath)
    try {
        $salud = Invoke-RestMethod -UseBasicParsing -Uri "$hacia/health" -TimeoutSec 10
        Write-Host "Broker en HTTPS con certificado de la AI Broker CA: $($salud.status)" -ForegroundColor Green
    }
    catch {
        throw "El Broker no contesta en $hacia con un certificado de la AI Broker CA ($($_.Exception.Message)). No cambio nada."
    }
}

# -- 2. Ficheros donde vive la URL ---------------------------------------------
$ficheros = @(
    (Join-Path $env:LOCALAPPDATA "Athena\settings.json"),
    (Join-Path $env:LOCALAPPDATA "GestionTareasIA\settings.json"),
    (Join-Path $KoRoot "state\broker_connection.json"),
    (Join-Path $Proyectos "Model_Drift\model_drift.yaml"),
    (Join-Path $Proyectos "ChatyGPT\Arrancar ChatyGPT.bat"),
    (Join-Path $Proyectos "ChatyGPT\scripts\Start-ChatyGPT.ps1"),
    (Join-Path $Proyectos "AI_OS_core\config\apps.json")
)
$registro = Join-Path $env:LOCALAPPDATA "TradingAI\config\workspaces.json"
if (Test-Path -LiteralPath $registro) {
    foreach ($ws in (Get-Content -LiteralPath $registro -Raw | ConvertFrom-Json).workspaces) {
        if ($ws.path) { $ficheros += (Join-Path $ws.path "config\settings.json") }
    }
}

$cambiados = 0
foreach ($fichero in $ficheros) {
    if (-not (Test-Path -LiteralPath $fichero)) { continue }
    $bytes = [IO.File]::ReadAllBytes($fichero)
    $bom = $bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF
    $texto = (New-Object Text.UTF8Encoding($false)).GetString($bytes, $(if ($bom) { 3 } else { 0 }), $bytes.Length - $(if ($bom) { 3 } else { 0 }))
    if (-not $texto.Contains($desde)) { continue }
    Copy-Item -LiteralPath $fichero -Destination "$fichero.antes-https.bak" -Force
    [IO.File]::WriteAllText($fichero, $texto.Replace($desde, $hacia), (New-Object Text.UTF8Encoding($bom)))
    Write-Host "  cambiado: $fichero"
    $cambiados++
}
Write-Host ""
Write-Host "$cambiados fichero(s) pasan de $desde a $hacia." -ForegroundColor Green
Write-Host "Reinicia las apps abiertas. Variables *_BROKER_URL fijadas a mano mandan sobre esto."
