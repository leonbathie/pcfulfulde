# ============================================================
#  Installe le Clavier Pulaar (Fulfulde)
# ============================================================
#  Le moteur place lui-meme les lettres pulaar (v -> ɓ, z -> ɗ, q -> ŋ...)
#  avec n'importe quel clavier de Windows : il n'inscrit plus de disposition
#  dans Windows. Les claviers « Pulaar (Fulfulde) AZERTY / QWERTY » des
#  versions 2.0 a 2.2 faisaient planter le selecteur Win + Espace
#  (InputSwitch.dll, dans l'Explorateur) : ils sont retires.
#
#  1. (utilisateur) retire ces claviers de la liste Win + Espace, et la langue
#     FUL (Pulaar) s'ils y etaient seuls ; enregistre le correcteur orthographique
#     pulaar ; lance le moteur et le fait demarrer avec Windows (sauf avec
#     -SansMoteur) ;
#  2. (administrateur) efface les dispositions et leurs fichiers ; rend a
#     Windows sa disposition Wolof, que les anciens installateurs avaient
#     remplacee ; retire l'ancien Setup.
#
#  La partie utilisateur passe d'abord : une langue qui renverrait a une
#  disposition deja effacee ferait planter Win + Espace. Installe par
#  Setup_Clavier_Pulaar.exe, le script est a cote de ClavierPulaar.exe ;
#  -UtilisateurSeulement et -MachineOnly font l'une ou l'autre partie (le
#  Setup appelle les deux, dans cet ordre).
param(
    [switch]$MachineOnly,
    [switch]$UtilisateurSeulement,
    [switch]$SansMoteur
)

$ErrorActionPreference = 'Stop'
$ici = Split-Path -Parent $PSCommandPath
$exe = Join-Path $ici 'ClavierPulaar.exe'
$empaquete = Test-Path $exe
$base = 'HKLM:\SYSTEM\CurrentControlSet\Control\Keyboard Layouts'
# 00000867 : l'AZERTY (disposition principale de la langue pulaar, ff-Latn-SN) ; a0010867 :
# le QWERTY ; a0000867 : l'ancienne inscription de l'AZERTY.
$klids = @('00000867', 'a0010867', 'a0000867')
$nosDll = @('fulffaz.dll', 'fulffqw.dll', 'kbdfulfa.dll', 'kbdfulfq.dll')
$cleDesinstallation = 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\ClavierPulaar'
$ancienSetup = 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{9F3B96A1-7F2D-4D3C-8A3E-91B2D3E4F5A6}_is1'

function Test-Administrateur {
    ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
        [Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Remove-ClaviersDeLaListe {
    Write-Host '[1/3] Anciens claviers Pulaar retires de Win + Espace...' -ForegroundColor Yellow
    $liste = Get-WinUserLanguageList
    $change = $false
    foreach ($langue in @($liste | Where-Object { $_.LanguageTag -like 'ff-Latn*' })) {
        foreach ($tip in @($langue.InputMethodTips | Where-Object { $klids -contains ($_ -split ':')[-1].ToLower() })) {
            [void]$langue.InputMethodTips.Remove($tip)
            $change = $true
        }
        if ($langue.InputMethodTips.Count -eq 0) {
            [void]$liste.Remove($langue)
            $change = $true
        }
    }
    if ($change) {
        Set-WinUserLanguageList $liste -Force
        Write-Host '      Claviers retires.' -ForegroundColor Green
    }

    # Get-WinUserLanguageList rend la liste d'un bloc : foreach la parcourt langue par langue.
    $ful = foreach ($langue in (Get-WinUserLanguageList)) {
        if (@($langue.InputMethodTips | Where-Object { $_ -like '0867:*' }).Count) { $langue }
    }
    if ($ful) { return }
    # Plus aucun clavier FUL (Pulaar) : ceux encore charges dans la session, et la trace
    # qu'en garde l'ordre de Win + Espace, partent aussi.
    Add-Type -Namespace ClavierPulaar -Name Dispositions -MemberDefinition @'
[DllImport("user32.dll")] public static extern int GetKeyboardLayoutList(int n, IntPtr[] liste);
[DllImport("user32.dll")] public static extern bool UnloadKeyboardLayout(IntPtr hkl);
'@
    $n = [ClavierPulaar.Dispositions]::GetKeyboardLayoutList(0, $null)
    $hkls = New-Object IntPtr[] $n
    [void][ClavierPulaar.Dispositions]::GetKeyboardLayoutList($n, $hkls)
    foreach ($hkl in $hkls) {
        if (($hkl.ToInt64() -band 0xFFFF) -eq 0x0867) { [void][ClavierPulaar.Dispositions]::UnloadKeyboardLayout($hkl) }
    }
    Remove-Item 'HKCU:\Software\Microsoft\CTF\SortOrder\AssemblyItem\0x00000867' -Recurse -Force -ErrorAction SilentlyContinue
}

function Install-Utilisateur {
    Remove-ClaviersDeLaListe

    Write-Host '[2/3] Correcteur orthographique pulaar (Edge, Chrome...)...' -ForegroundColor Yellow
    try {
        & (Join-Path $ici 'correcteur_pulaar\enregistrer_correcteur.ps1')
    } catch {
        Write-Host "      Correcteur non enregistre : $_" -ForegroundColor Red
    }

    if ($SansMoteur) { return }
    Write-Host '[3/3] Moteur (lettres pulaar et suggestions)...' -ForegroundColor Yellow
    $demarrage = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run'
    if ($empaquete) {
        Set-ItemProperty $demarrage -Name 'ClavierPulaar' -Value "`"$exe`""
        Start-Process $exe
        Write-Host '      Lance, et demarrera avec Windows (icone pres de l horloge).' -ForegroundColor Green
        return
    }
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
    Set-ItemProperty $demarrage -Name 'ClavierPulaar' -Value "`"$pythonw`" `"$script`""
    Start-Process $pythonw -ArgumentList "`"$script`""
    Write-Host '      Lance, et demarrera avec Windows (icone pres de l horloge).' -ForegroundColor Green
}

function Install-Machine {
    Write-Host '[Administrateur] Anciennes dispositions Pulaar effacees...' -ForegroundColor Yellow
    foreach ($klid in $klids) {
        $cle = Join-Path $base $klid
        $fichier = (Get-ItemProperty $cle -ErrorAction SilentlyContinue).'Layout File'
        # Seulement nos dispositions, jamais une disposition de Windows.
        if ($fichier -and ($nosDll -contains $fichier.ToLower())) {
            Remove-Item $cle -Recurse -Force
            Write-Host "      $klid retiree." -ForegroundColor Green
        }
    }
    # Un fichier encore ouvert reste en place : il ne sert plus a rien une fois
    # les cles retirees, et partira a la prochaine installation.
    foreach ($dossier in "$env:SystemRoot\System32", "$env:SystemRoot\SysWOW64") {
        foreach ($motif in 'fulffaz.dll', 'fulffqw.dll', 'fulff*.dll.*.ancienne') {
            Remove-Item (Join-Path $dossier $motif) -Force -ErrorAction SilentlyContinue
        }
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

    # Une entree dans Parametres > Applications > Applications installees.
    # Installe par le Setup, c'est la sienne : l'ancienne entree du dossier de
    # developpement est retiree, pour ne pas figurer deux fois.
    if ($empaquete) {
        Remove-Item $cleDesinstallation -Recurse -Force -ErrorAction SilentlyContinue
        return
    }
    if (-not (Test-Path $cleDesinstallation)) { New-Item -Path $cleDesinstallation -Force | Out-Null }
    $desinstaller = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$ici\desinstaller_clavier_pulaar.ps1`""
    Set-ItemProperty $cleDesinstallation -Name 'DisplayName' -Value 'Clavier Pulaar (Fulfulde)'
    Set-ItemProperty $cleDesinstallation -Name 'DisplayVersion' -Value '2.3'
    Set-ItemProperty $cleDesinstallation -Name 'Publisher' -Value 'Fulfulde Community'
    Set-ItemProperty $cleDesinstallation -Name 'DisplayIcon' -Value "$ici\icones\clavier_pulaar.ico"
    Set-ItemProperty $cleDesinstallation -Name 'InstallLocation' -Value $ici
    Set-ItemProperty $cleDesinstallation -Name 'UninstallString' -Value $desinstaller
    Set-ItemProperty $cleDesinstallation -Name 'NoModify' -Value 1 -Type DWord
    Set-ItemProperty $cleDesinstallation -Name 'NoRepair' -Value 1 -Type DWord
}

if ($MachineOnly) {
    if (-not (Test-Administrateur)) { throw 'La partie machine doit tourner en administrateur.' }
    Install-Machine
    exit 0
}
if ($UtilisateurSeulement) {
    Install-Utilisateur
    exit 0
}

Write-Host '============================================================' -ForegroundColor Cyan
Write-Host '   INSTALLATION DU CLAVIER PULAAR (FULFULDE)' -ForegroundColor Green
Write-Host '============================================================' -ForegroundColor Cyan
Install-Utilisateur
if (Test-Administrateur) {
    Install-Machine
} else {
    # La partie machine demande les droits d'administrateur ; la liste des
    # langues, elle, se change dans la session de l'utilisateur (fait plus haut).
    $p = Start-Process powershell.exe -Verb RunAs -Wait -PassThru -ArgumentList @(
        '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', "`"$PSCommandPath`"", '-MachineOnly')
    if ($p.ExitCode -ne 0) { throw 'La partie administrateur a echoue.' }
}
Write-Host ''
Write-Host 'Termine. Ecrivez avec votre clavier habituel : v donne ɓ, z ɗ, q ŋ, x ƴ.' -ForegroundColor Cyan
