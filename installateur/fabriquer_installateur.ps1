# ============================================================
#  Fabrique Setup_Fulfulde_Keyboard.exe
# ============================================================
#  1. « programme » : FulfuldeKeyboard.exe avec PyInstaller
#     (construction\dist\FulfuldeKeyboard), le clavier sans Python sur le PC de
#     destination ; son nom et sa version (ceux de clavier_pulaar.iss) sont
#     ceux qu'affichent le Gestionnaire des taches et les applications de
#     demarrage ;
#  2. « installateur » : l'assistant d'installation avec Inno Setup
#     (installateur\clavier_pulaar.iss), dans toutes les langues fournies avec
#     Inno Setup.
#
#  -Etape programme | installateur : une seule des deux (GitHub Actions fait
#  signer le programme par SignPath entre les deux, voir
#  .github\workflows\installateur.yml). Sans -Etape : les deux.
#
#  -Signer : signe FulfuldeKeyboard.exe, l'installateur et son desinstalleur avec
#  un certificat de ce PC (voir installateur\signer.ps1).
#
#  Il faut : Python avec pynput et pyinstaller (pip install pynput pyinstaller),
#  et Inno Setup 6 (https://jrsoftware.org/isdl.php).
param(
    [switch]$Signer,
    [ValidateSet('tout', 'programme', 'installateur')][string]$Etape = 'tout'
)

$ErrorActionPreference = 'Stop'
$racine = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
$construction = Join-Path $racine 'construction'
$signeur = Join-Path $racine 'installateur\signer.ps1'

if ($Etape -ne 'installateur') {
    # Nom et version de l'exe : ceux de l'installateur (#define Version).
    $version = [regex]::Match((Get-Content "$racine\installateur\clavier_pulaar.iss" -Raw), '#define Version "([\d.]+)"').Groups[1].Value
    $chiffres = (($version -split '\.') + @('0', '0', '0', '0'))[0..3] -join ', '
    New-Item -ItemType Directory -Force $construction | Out-Null
    $fichierVersion = Join-Path $construction 'version_programme.txt'
    @"
VSVersionInfo(
  ffi=FixedFileInfo(filevers=($chiffres), prodvers=($chiffres), mask=0x3f, flags=0x0, OS=0x40004,
                    fileType=0x1, subtype=0x0, date=(0, 0)),
  kids=[
    StringFileInfo([StringTable('040904B0', [
      StringStruct('CompanyName', 'Fulfulde Community'),
      StringStruct('FileDescription', 'Fulfulde Keyboard'),
      StringStruct('FileVersion', '$version'),
      StringStruct('InternalName', 'FulfuldeKeyboard'),
      StringStruct('OriginalFilename', 'FulfuldeKeyboard.exe'),
      StringStruct('ProductName', 'Fulfulde Keyboard'),
      StringStruct('ProductVersion', '$version')])]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
"@ | Set-Content -Path $fichierVersion -Encoding ASCII

    # Pillow ne sert qu'a fabriquer les images (icones\fabrique_icone.py), et le
    # clavier ne va jamais sur Internet : ni l'un ni SSL ne sont embarques.
    python -m PyInstaller --noconfirm --clean --windowed --name FulfuldeKeyboard `
        --version-file $fichierVersion `
        --icon "$racine\icones\clavier_pulaar.ico" `
        --add-data "$racine\dictionary\dict_ff_latin.json;dictionary" `
        --add-data "$racine\icones\clavier_pulaar.ico;icones" `
        --add-data "$racine\icones\interrupteur_*.png;icones" `
        --exclude-module PIL --exclude-module ssl --exclude-module _ssl --exclude-module _hashlib `
        --distpath "$construction\dist" --workpath "$construction\build" --specpath $construction `
        "$racine\clavier_fulfulde_natif.py"
    if ($LASTEXITCODE -ne 0) { throw 'PyInstaller a echoue.' }
    if ($Signer) { & $signeur -Fichier "$construction\dist\FulfuldeKeyboard\FulfuldeKeyboard.exe" }
}

if ($Etape -ne 'programme') {
    $iscc = @(
        "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe",
        "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
        "$env:ProgramFiles\Inno Setup 6\ISCC.exe"
    ) | Where-Object { Test-Path $_ } | Select-Object -First 1
    if (-not $iscc) { throw 'Inno Setup 6 est introuvable : https://jrsoftware.org/isdl.php' }

    $options = @()
    if ($Signer) {
        # Inno Setup signe lui-meme l'installateur et le desinstalleur ($f : le
        # fichier, $q : un guillemet).
        $options = @('/DSigner', "/Ssignature=powershell.exe -NoProfile -ExecutionPolicy Bypass -File `$q$signeur`$q -Fichier `$f")
    }
    & $iscc @options "$racine\installateur\clavier_pulaar.iss"
    if ($LASTEXITCODE -ne 0) { throw 'Inno Setup a echoue.' }
    Write-Host "Installateur : $racine\Setup_Fulfulde_Keyboard.exe" -ForegroundColor Green
}
