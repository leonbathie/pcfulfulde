# ============================================================
#  Fabrique Setup_Clavier_Pulaar.exe
# ============================================================
#  1. ClavierPulaar.exe avec PyInstaller (construction\dist\ClavierPulaar) :
#     le clavier sans Python sur le PC de destination ;
#  2. l'assistant d'installation avec Inno Setup (installateur\clavier_pulaar.iss),
#     dans toutes les langues fournies avec Inno Setup.
#
#  -Signer : signe ClavierPulaar.exe, l'installateur et son desinstalleur avec
#  le certificat de signature de code (voir installateur\signer.ps1).
#
#  Il faut : Python avec pynput et pyinstaller (pip install pynput pyinstaller),
#  et Inno Setup 6 (https://jrsoftware.org/isdl.php).
param([switch]$Signer)

$ErrorActionPreference = 'Stop'
$racine = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
$construction = Join-Path $racine 'construction'
$signeur = Join-Path $racine 'installateur\signer.ps1'

# Pillow ne sert qu'a fabriquer les images (icones\fabrique_icone.py), et le
# clavier ne va jamais sur Internet : ni l'un ni SSL ne sont embarques.
python -m PyInstaller --noconfirm --clean --windowed --name ClavierPulaar `
    --icon "$racine\icones\clavier_pulaar.ico" `
    --add-data "$racine\dictionary\dict_ff_latin.json;dictionary" `
    --add-data "$racine\icones\clavier_pulaar.ico;icones" `
    --add-data "$racine\icones\interrupteur_*.png;icones" `
    --exclude-module PIL --exclude-module ssl --exclude-module _ssl --exclude-module _hashlib `
    --distpath "$construction\dist" --workpath "$construction\build" --specpath $construction `
    "$racine\clavier_fulfulde_natif.py"
if ($LASTEXITCODE -ne 0) { throw 'PyInstaller a echoue.' }

$iscc = @(
    "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe",
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
    "$env:ProgramFiles\Inno Setup 6\ISCC.exe"
) | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $iscc) { throw 'Inno Setup 6 est introuvable : https://jrsoftware.org/isdl.php' }

$options = @()
if ($Signer) {
    & $signeur -Fichier "$construction\dist\ClavierPulaar\ClavierPulaar.exe"
    # Inno Setup signe lui-meme l'installateur et le desinstalleur ($f : le
    # fichier, $q : un guillemet).
    $options = @('/DSigner', "/Ssignature=powershell.exe -NoProfile -ExecutionPolicy Bypass -File `$q$signeur`$q -Fichier `$f")
}
& $iscc @options "$racine\installateur\clavier_pulaar.iss"
if ($LASTEXITCODE -ne 0) { throw 'Inno Setup a echoue.' }
Write-Host "Installateur : $racine\Setup_Clavier_Pulaar.exe" -ForegroundColor Green
