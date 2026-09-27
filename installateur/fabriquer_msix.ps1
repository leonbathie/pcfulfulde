# ============================================================
#  Fabrique le paquet MSIX de Fulfulde Keyboard pour le Microsoft Store
# ============================================================
#  Le Store signe lui-meme les paquets MSIX : pas de certificat a acheter.
#  Le paquet contient FulfuldeKeyboard.exe (PyInstaller), le script qui ajoute
#  FUL a Win + Espace et enregistre le correcteur, le correcteur, les logos et
#  le manifeste (installateur\msix\AppxManifest.xml).
#
#  -Nom, -Editeur, -EditeurAffiche : l'identite du produit donnee par l'Espace
#   partenaires (Produit > Gestion du produit > Identite du produit) :
#   Package/Identity/Name, Package/Identity/Publisher (CN=...) et
#   Package/Properties/PublisherDisplayName. Par defaut : une identite d'essai.
#  -Essai : signe aussi une copie avec un certificat d'essai de ce PC, pour
#   l'installer ici avant de l'envoyer au Store (le certificat doit etre
#   approuve une fois : voir le message a la fin).
#  -SansProgramme : reprend FulfuldeKeyboard.exe deja fabrique.
#
#  Outils : makeappx, makepri et signtool du SDK Windows, ou du paquet NuGet
#  Microsoft.Windows.SDK.BuildTools, telecharge une fois dans construction\outils.
param(
    [string]$Nom = 'Tarolearning.FulfuldeKeyboard',
    [string]$Editeur = 'CN=Tarolearning',
    [string]$EditeurAffiche = 'Tarolearning',
    [switch]$Essai,
    [switch]$SansProgramme
)

$ErrorActionPreference = 'Stop'
$racine = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
$construction = Join-Path $racine 'construction'
$travail = Join-Path $construction 'msix'

function Get-Outil($nom) {
    $sdk = Get-ChildItem "${env:ProgramFiles(x86)}\Windows Kits\10\bin" -Recurse -Filter $nom -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -match '\\x64\\' } | Sort-Object FullName -Descending | Select-Object -First 1
    if ($sdk) { return $sdk.FullName }
    $outils = Join-Path $construction 'outils\buildtools'
    if (-not (Test-Path $outils)) {
        Write-Host '      Telechargement de Microsoft.Windows.SDK.BuildTools (nuget.org)...' -ForegroundColor Yellow
        New-Item -ItemType Directory -Force (Split-Path $outils) | Out-Null
        $zip = "$outils.zip"
        $ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest 'https://www.nuget.org/api/v2/package/Microsoft.Windows.SDK.BuildTools' -OutFile $zip -UseBasicParsing
        Expand-Archive $zip -DestinationPath $outils -Force
    }
    $outil = Get-ChildItem $outils -Recurse -Filter $nom | Where-Object { $_.FullName -match '\\x64\\' } |
        Sort-Object FullName -Descending | Select-Object -First 1
    if (-not $outil) { throw "$nom introuvable." }
    $outil.FullName
}

# La version de l'installateur (2.5.1), en quatre nombres pour le Store (2.5.1.0).
$version = [regex]::Match((Get-Content "$racine\installateur\clavier_pulaar.iss" -Raw), '#define Version "([\d.]+)"').Groups[1].Value
$version4 = (($version -split '\.') + @('0', '0', '0'))[0..2] -join '.'
$version4 = "$version4.0"

Write-Host "[1/4] Programme FulfuldeKeyboard.exe..." -ForegroundColor Yellow
$programme = Join-Path $construction 'dist\FulfuldeKeyboard'
if (-not $SansProgramme -or -not (Test-Path "$programme\FulfuldeKeyboard.exe")) {
    & (Join-Path $racine 'installateur\fabriquer_installateur.ps1') -Etape programme
}

Write-Host "[2/4] Contenu du paquet..." -ForegroundColor Yellow
$paquet = Join-Path $travail 'paquet'
Remove-Item $paquet -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force $paquet | Out-Null
Copy-Item "$programme\*" $paquet -Recurse
Copy-Item "$racine\installer_clavier_pulaar.ps1" $paquet
New-Item -ItemType Directory -Force "$paquet\correcteur_pulaar", "$paquet\dictionary" | Out-Null
Copy-Item "$racine\correcteur_pulaar\correcteur_pulaar.dll", "$racine\correcteur_pulaar\enregistrer_correcteur.ps1" "$paquet\correcteur_pulaar"
Copy-Item "$racine\dictionary\mots_pulaar.txt" "$paquet\dictionary"
Copy-Item "$racine\installateur\msix\Assets" "$paquet\Assets" -Recurse

$manifeste = (Get-Content "$racine\installateur\msix\AppxManifest.xml" -Raw -Encoding UTF8).
    Replace('{{NOM}}', $Nom).Replace('{{EDITEUR}}', $Editeur).
    Replace('{{EDITEUR_AFFICHE}}', [Security.SecurityElement]::Escape($EditeurAffiche)).Replace('{{VERSION}}', $version4)
[IO.File]::WriteAllText("$paquet\AppxManifest.xml", $manifeste, (New-Object Text.UTF8Encoding $false))

# Les logos a chaque echelle : resources.pri dit a Windows lequel prendre.
# Seul le dossier Assets est indexe (pas les milliers de fichiers du programme).
$makepri = Get-Outil 'makepri.exe'
$index = Join-Path $travail 'index'
Remove-Item $index -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force $index | Out-Null
Copy-Item "$racine\installateur\msix\Assets" "$index\Assets" -Recurse
Copy-Item "$paquet\AppxManifest.xml" $index
& $makepri createconfig /cf "$travail\priconfig.xml" /dq fr-FR /pv 10.0.0 /o | Out-Null
& $makepri new /pr $index /cf "$travail\priconfig.xml" /mn "$index\AppxManifest.xml" /of "$paquet\resources.pri" /o | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'makepri a echoue.' }

Write-Host "[3/4] Paquet MSIX (version $version4)..." -ForegroundColor Yellow
$makeappx = Get-Outil 'makeappx.exe'
$sortie = Join-Path $travail "FulfuldeKeyboard_$($version4)_x64.msix"
& $makeappx pack /d $paquet /p $sortie /o | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'makeappx a echoue.' }
Write-Host "      Pour le Store : $sortie" -ForegroundColor Green

if ($Essai) {
    Write-Host "[4/4] Copie signee pour un essai sur ce PC..." -ForegroundColor Yellow
    $cert = Get-ChildItem Cert:\CurrentUser\My | Where-Object {
        $_.Subject -eq $Editeur -and $_.EnhancedKeyUsageList.ObjectId -contains '1.3.6.1.5.5.7.3.3' -and $_.NotAfter -gt (Get-Date) } |
        Select-Object -First 1
    if (-not $cert) {
        $cert = New-SelfSignedCertificate -Type Custom -Subject $Editeur -KeyUsage DigitalSignature `
            -FriendlyName 'Fulfulde Keyboard (essai du paquet MSIX)' -CertStoreLocation Cert:\CurrentUser\My `
            -TextExtension @('2.5.29.37={text}1.3.6.1.5.5.7.3.3', '2.5.29.19={text}')
    }
    $copieEssai = Join-Path $travail "FulfuldeKeyboard_$($version4)_x64_essai.msix"
    Copy-Item $sortie $copieEssai -Force
    $signtool = Get-Outil 'signtool.exe'
    & $signtool sign /fd SHA256 /sha1 $cert.Thumbprint $copieEssai | Out-Null
    if ($LASTEXITCODE -ne 0) { throw 'signtool a echoue.' }
    $cer = Join-Path $travail 'certificat_essai.cer'
    Export-Certificate -Cert $cert -FilePath $cer | Out-Null
    Write-Host "      Paquet d'essai : $copieEssai" -ForegroundColor Green
    Write-Host "      Une fois, en administrateur : Import-Certificate '$cer' -CertStoreLocation Cert:\LocalMachine\TrustedPeople" -ForegroundColor Cyan
    Write-Host "      Puis : Add-AppxPackage '$copieEssai'" -ForegroundColor Cyan
}
