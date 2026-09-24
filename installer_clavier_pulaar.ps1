# ============================================================
#  Installe le Clavier Pulaar dans Windows, comme un clavier de Microsoft
# ============================================================
#  1. (administrateur) copie fulffaz.dll et fulffqw.dll dans Windows et les
#     enregistre avec des Layout Id libres (00a1 etait deja pris par le
#     clavier lituanien) ; rend a Windows sa disposition Wolof (00000488),
#     que les anciens installateurs avaient remplacee ; inscrit le clavier
#     dans « Applications installees » ;
#  2. (utilisateur) ajoute la langue Peul (ff-Latn-SN) avec les claviers
#     Pulaar AZERTY et QWERTY a la liste Win + Espace ;
#  3. (utilisateur) lance le moteur de suggestions et le fait demarrer avec
#     Windows (sauf avec -SansMoteur).
param(
    [switch]$MachineOnly,
    [switch]$SansMoteur
)

$ErrorActionPreference = 'Stop'
$ici = Split-Path -Parent $PSCommandPath
$base = 'HKLM:\SYSTEM\CurrentControlSet\Control\Keyboard Layouts'
$dispositions = @(
    @{ Klid = 'a0000867'; Dll = 'fulffaz.dll'; Texte = 'Pulaar (Fulfulde) AZERTY' },
    @{ Klid = 'a0010867'; Dll = 'fulffqw.dll'; Texte = 'Pulaar (Fulfulde) QWERTY' }
)
$nosDll = @('fulffaz.dll', 'fulffqw.dll', 'kbdfulfa.dll', 'kbdfulfq.dll')
$cleDesinstallation = 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\ClavierPulaar'
$ancienSetup = 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{9F3B96A1-7F2D-4D3C-8A3E-91B2D3E4F5A6}_is1'

function Test-Administrateur {
    ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
        [Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Copy-SiDifferent($source, $destination) {
    if (-not (Test-Path $source)) { throw "Fichier manquant : $source" }
    if ((Test-Path $destination) -and
        (Get-FileHash $source).Hash -eq (Get-FileHash $destination).Hash) { return }
    Copy-Item $source $destination -Force
}

function Install-Machine {
    Write-Host '[1/3] Dispositions Pulaar dans Windows...' -ForegroundColor Yellow

    # Les fichiers : 64 bits dans System32, 32 bits dans SysWOW64
    foreach ($d in $dispositions) {
        $nom = [IO.Path]::GetFileNameWithoutExtension($d.Dll)
        if ([Environment]::Is64BitOperatingSystem) {
            Copy-SiDifferent "$ici\${nom}_amd64.dll" "$env:SystemRoot\System32\$($d.Dll)"
            Copy-SiDifferent "$ici\${nom}_x86.dll" "$env:SystemRoot\SysWOW64\$($d.Dll)"
        } else {
            Copy-SiDifferent "$ici\${nom}_x86.dll" "$env:SystemRoot\System32\$($d.Dll)"
        }
    }

    # Un Layout Id par disposition, que personne d'autre n'utilise : deux
    # dispositions au meme Layout Id, et Windows peut charger la mauvaise.
    $pris = @{}
    foreach ($cle in Get-ChildItem $base) {
        $id = (Get-ItemProperty $cle.PSPath).'Layout Id'
        if ($id -and ($dispositions.Klid -notcontains $cle.PSChildName)) { $pris[$id.ToLower()] = $cle.PSChildName }
    }
    $prochain = 0x00f0
    foreach ($d in $dispositions) {
        $cle = Join-Path $base $d.Klid
        if (-not (Test-Path $cle)) { New-Item -Path $cle -Force | Out-Null }
        $id = (Get-ItemProperty $cle).'Layout Id'
        if (-not $id -or $pris.ContainsKey($id.ToLower())) {
            while ($pris.ContainsKey(('{0:x4}' -f $prochain))) { $prochain++ }
            $id = '{0:x4}' -f $prochain
        }
        $pris[$id.ToLower()] = $d.Klid
        Set-ItemProperty $cle -Name 'Layout File' -Value $d.Dll
        Set-ItemProperty $cle -Name 'Layout Text' -Value $d.Texte
        Set-ItemProperty $cle -Name 'Layout Display Name' -Value $d.Texte
        Set-ItemProperty $cle -Name 'Layout Id' -Value $id
        Write-Host "      $($d.Texte) : $($d.Klid), Layout Id $id" -ForegroundColor Green
    }

    # La disposition Wolof de Windows, remplacee par les anciens installateurs
    $wolof = Join-Path $base '00000488'
    $fichier = (Get-ItemProperty $wolof -ErrorAction SilentlyContinue).'Layout File'
    if ($fichier -and ($nosDll -contains $fichier.ToLower())) {
        $type = (Get-Item (Join-Path $base '00000432')).GetValueKind('Layout Display Name')
        New-ItemProperty $wolof -Name 'Layout File' -Value 'KBDWOL.DLL' -PropertyType String -Force | Out-Null
        New-ItemProperty $wolof -Name 'Layout Text' -Value 'Wolof' -PropertyType String -Force | Out-Null
        New-ItemProperty $wolof -Name 'Layout Display Name' -Value '@%SystemRoot%\system32\input.dll,-5190' `
            -PropertyType $type -Force | Out-Null
        Write-Host '      Disposition Wolof de Windows restauree.' -ForegroundColor Green
    }

    # L'ancien Setup : sa desinstallation effacerait la disposition Wolof ; on
    # le retire, le nouveau clavier a sa propre entree dans les applications.
    if (Test-Path $ancienSetup) {
        Remove-Item $ancienSetup -Recurse -Force
        Remove-Item "$env:ProgramFiles\ClavierFulfulde" -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host '      Ancien Setup « Clavier Fulfulde (Pulaar) Latin » retire.' -ForegroundColor Green
    }

    # Une entree dans Parametres > Applications > Applications installees
    if (-not (Test-Path $cleDesinstallation)) { New-Item -Path $cleDesinstallation -Force | Out-Null }
    $desinstaller = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$ici\desinstaller_clavier_pulaar.ps1`""
    Set-ItemProperty $cleDesinstallation -Name 'DisplayName' -Value 'Clavier Pulaar (Fulfulde)'
    Set-ItemProperty $cleDesinstallation -Name 'DisplayVersion' -Value '2.0'
    Set-ItemProperty $cleDesinstallation -Name 'Publisher' -Value 'Fulfulde Community'
    Set-ItemProperty $cleDesinstallation -Name 'DisplayIcon' -Value "$ici\icones\clavier_pulaar.ico"
    Set-ItemProperty $cleDesinstallation -Name 'InstallLocation' -Value $ici
    Set-ItemProperty $cleDesinstallation -Name 'UninstallString' -Value $desinstaller
    Set-ItemProperty $cleDesinstallation -Name 'NoModify' -Value 1 -Type DWord
    Set-ItemProperty $cleDesinstallation -Name 'NoRepair' -Value 1 -Type DWord
}

function Install-Utilisateur {
    Write-Host '[2/3] Pulaar dans la liste Win + Espace...' -ForegroundColor Yellow
    $liste = Get-WinUserLanguageList
    $pulaar = $liste | Where-Object { $_.LanguageTag -like 'ff-Latn*' } | Select-Object -First 1
    if (-not $pulaar) {
        $liste.Add('ff-Latn-SN')
        $pulaar = $liste | Where-Object { $_.LanguageTag -like 'ff-Latn*' } | Select-Object -First 1
    }
    # La langue arrive avec le clavier Wolof par defaut : on met les notres a la place.
    $pulaar.InputMethodTips.Clear()
    foreach ($d in $dispositions) { $pulaar.InputMethodTips.Add("0867:$($d.Klid.ToUpper())") }
    Set-WinUserLanguageList $liste -Force

    # Get-WinUserLanguageList rend la liste d'un bloc : foreach la parcourt langue par langue.
    $verifie = foreach ($langue in (Get-WinUserLanguageList)) { if ($langue.LanguageTag -like 'ff-Latn*') { $langue } }
    if ($verifie -and $verifie.InputMethodTips.Count -gt 0) {
        Write-Host "      $($verifie.LocalizedName) : $($verifie.InputMethodTips -join ', ')" -ForegroundColor Green
    } else {
        Write-Host '      Windows n a pas garde la langue Peul : ouvrez Parametres > Heure et langue.' -ForegroundColor Red
    }

    if ($SansMoteur) { return }
    Write-Host '[3/3] Moteur de suggestions...' -ForegroundColor Yellow
    $pythonw = (Get-Command pythonw.exe -ErrorAction SilentlyContinue).Source
    if (-not $pythonw) {
        Write-Host '      Python est introuvable : installez-le depuis python.org, puis relancez.' -ForegroundColor Red
        return
    }
    $python = Join-Path (Split-Path $pythonw) 'python.exe'
    & $python -c 'import pynput' 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host '      Installation de pynput...' -ForegroundColor Yellow
        & $python -m pip install --user pynput
    }
    $script = Join-Path $ici 'clavier_fulfulde_natif.py'
    Set-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' -Name 'ClavierPulaar' `
        -Value "`"$pythonw`" `"$script`""
    Start-Process $pythonw -ArgumentList "`"$script`""
    Write-Host '      Lance, et demarrera avec Windows (icone pres de l horloge).' -ForegroundColor Green
}

if ($MachineOnly) {
    if (-not (Test-Administrateur)) { throw 'La partie machine doit tourner en administrateur.' }
    Install-Machine
    exit 0
}

Write-Host '============================================================' -ForegroundColor Cyan
Write-Host '   INSTALLATION DU CLAVIER PULAAR (FULFULDE)' -ForegroundColor Green
Write-Host '============================================================' -ForegroundColor Cyan
if (Test-Administrateur) {
    Install-Machine
} else {
    # La partie machine demande les droits d'administrateur ; la liste des
    # langues, elle, doit etre changee dans la session de l'utilisateur.
    $p = Start-Process powershell.exe -Verb RunAs -Wait -PassThru -ArgumentList @(
        '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', "`"$PSCommandPath`"", '-MachineOnly')
    if ($p.ExitCode -ne 0) { throw 'La partie administrateur a echoue.' }
}
Install-Utilisateur
Write-Host ''
Write-Host 'Termine. Appuyez sur Win + Espace et choisissez « Pulaar (Fulfulde) AZERTY ».' -ForegroundColor Cyan
