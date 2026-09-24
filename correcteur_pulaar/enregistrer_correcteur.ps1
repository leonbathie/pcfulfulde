# ============================================================
#  Enregistre le correcteur orthographique pulaar aupres de Windows
# ============================================================
#  Pour l'utilisateur courant, sans droits d'administrateur. Ensuite Edge,
#  Chrome, le Bloc-notes et les autres applications qui se servent du
#  correcteur de Windows soulignent les fautes en pulaar et proposent leurs
#  corrections (clic droit). Word garde son propre correcteur.
#
#  -Retirer : desenregistre le correcteur.
param([switch]$Retirer)

$ErrorActionPreference = 'Stop'
$ici = Split-Path -Parent $PSCommandPath
$racine = Split-Path -Parent $ici
$clsid = '{BA4F4FD0-8BB2-49E2-9B55-B3350BC1A5B5}'
$dossier = Join-Path $env:LOCALAPPDATA 'ClavierPulaar\correcteur'
$cleClasse = "HKCU:\Software\Classes\CLSID\$clsid"
$cleCorrecteur = 'HKCU:\Software\Microsoft\Spelling\Spellers\ClavierPulaar'

if ($Retirer) {
    Remove-Item $cleCorrecteur -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item $cleClasse -Recurse -Force -ErrorAction SilentlyContinue
    # Windows peut encore tenir la DLL ouverte : elle part au prochain redemarrage.
    Remove-Item $dossier -Recurse -Force -ErrorAction SilentlyContinue
    return
}

New-Item -ItemType Directory -Force $dossier | Out-Null
Remove-Item "$dossier\*.ancienne" -Force -ErrorAction SilentlyContinue
$dll = Join-Path $dossier 'correcteur_pulaar.dll'
if (Test-Path $dll) {
    # Une DLL chargee par Windows ne s'ecrase pas, mais se renomme.
    Move-Item $dll "$dll.$(Get-Date -Format yyyyMMddHHmmss).ancienne" -Force
}
Copy-Item (Join-Path $ici 'correcteur_pulaar.dll') $dll -Force
Copy-Item (Join-Path $racine 'dictionary\mots_pulaar.txt') $dossier -Force

# Windows fait tourner les correcteurs sous une identite restreinte : les
# applications empaquetees (ALL APPLICATION PACKAGES et ALL RESTRICTED
# APPLICATION PACKAGES) doivent pouvoir lire le dossier.
& icacls $dossier /grant '*S-1-15-2-1:(OI)(CI)RX' '*S-1-15-2-2:(OI)(CI)RX' /T /Q | Out-Null

New-Item -Path "$cleClasse\InprocServer32" -Force | Out-Null
Set-Item -Path $cleClasse -Value 'Correcteur pulaar (Clavier Pulaar)'
Set-Item -Path "$cleClasse\InprocServer32" -Value $dll
Set-ItemProperty -Path "$cleClasse\InprocServer32" -Name 'ThreadingModel' -Value 'Both'
New-Item -Path "$cleClasse\Version" -Force | Out-Null
Set-Item -Path "$cleClasse\Version" -Value '1.0'
Set-ItemProperty -Path "$cleClasse\Version" -Name 'Version' -Value '1.0'
New-Item -Path $cleCorrecteur -Force | Out-Null
Set-ItemProperty -Path $cleCorrecteur -Name 'CLSID' -Value $clsid
Write-Host "      Correcteur pulaar enregistre ($dossier)." -ForegroundColor Green
