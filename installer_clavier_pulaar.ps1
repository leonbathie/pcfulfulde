# ============================================================
#  Installe Fulfulde Keyboard (clavier pulaar)
# ============================================================
#  FUL (Pulaar, ff-Latn-SN) apparait dans Win + Espace avec deux claviers de
#  Windows : Francais (AZERTY) et Anglais (QWERTY). Quand FUL est choisi, le
#  moteur place lui-meme les lettres pulaar (v -> ɓ, z -> ɗ, q -> ŋ, x -> ƴ).
#  Avec Francais ou Anglais, rien ne change.
#
#  Aucune disposition n'est inscrite dans Windows. Celles des versions
#  precedentes (00000867, a0010867, « Pulaar (Fulfulde) AZERTY / QWERTY ») faisaient
#  planter le selecteur Win + Espace (InputSwitch.dll, dans l'Explorateur) :
#  depuis Windows 11 24H2, il ne connait que les dispositions de Windows.
#
#  Trois parties, dans cet ordre (le Setup les appelle l'une apres l'autre) :
#  1. -Preparation (utilisateur) : si FUL renvoie a ces anciennes
#     dispositions, il quitte la liste Win + Espace et la session, avant
#     qu'elles ne soient effacees ;
#  2. -MachineOnly (administrateur) : efface ces dispositions et leurs
#     fichiers, rend a Windows sa disposition Wolof, retire l'ancien Setup ;
#  3. -UtilisateurSeulement (utilisateur) : ajoute FUL a Win + Espace,
#     enregistre le correcteur orthographique, lance le moteur et le fait
#     demarrer avec Windows (sauf avec -SansMoteur).
param(
    [switch]$Preparation,
    [switch]$MachineOnly,
    [switch]$UtilisateurSeulement,
    [switch]$SansMoteur
)

$ErrorActionPreference = 'Stop'
$ici = Split-Path -Parent $PSCommandPath
$exe = Join-Path $ici 'FulfuldeKeyboard.exe'
$empaquete = Test-Path $exe
$base = 'HKLM:\SYSTEM\CurrentControlSet\Control\Keyboard Layouts'
# Les claviers de FUL : ceux de Windows, Francais (AZERTY) et Anglais (QWERTY).
$claviersFul = @('0867:0000040C', '0867:00000409')
# Les anciennes dispositions : 00000867 (AZERTY), a0010867 (QWERTY), a0000867.
$anciennesDispositions = @('00000867', 'a0010867', 'a0000867')
$anciensFichiers = @('fulffaz.dll', 'fulffqw.dll', 'kbdfulfa.dll', 'kbdfulfq.dll')
$cleDesinstallation = 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\ClavierPulaar'
$ancienSetup = 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{9F3B96A1-7F2D-4D3C-8A3E-91B2D3E4F5A6}_is1'

function Test-Administrateur {
    ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
        [Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Test-Ancienne($klid) {
    # L'un de nos anciens fichiers, ou l'un de nos noms : jamais une disposition de Windows.
    $v = Get-ItemProperty (Join-Path $base $klid) -ErrorAction SilentlyContinue
    if (-not $v) { return $false }
    ($anciensFichiers -contains ([string]$v.'Layout File').ToLower()) -or ([string]$v.'Layout Text' -like 'Pulaar (Fulfulde)*')
}

function Install-Preparation {
    $liste = Get-WinUserLanguageList
    $change = $false
    foreach ($langue in @($liste | Where-Object { $_.LanguageTag -like 'ff-Latn*' })) {
        foreach ($tip in @($langue.InputMethodTips | Where-Object { $anciennesDispositions -contains ($_ -split ':')[-1].ToLower() })) {
            [void]$langue.InputMethodTips.Remove($tip)
            $change = $true
        }
        if ($langue.InputMethodTips.Count -eq 0) { [void]$liste.Remove($langue) }
    }
    if (-not $change) { return }
    Write-Host '[1/3] Anciens claviers Pulaar retires de Win + Espace...' -ForegroundColor Yellow
    Set-WinUserLanguageList $liste -Force

    # Ceux encore charges dans la session, et la trace qu'en garde l'ordre de Win + Espace
    Add-Type -Namespace ClavierPulaar -Name Dispositions -MemberDefinition @'
[DllImport("user32.dll")] public static extern int GetKeyboardLayoutList(int n, IntPtr[] liste);
[DllImport("user32.dll")] public static extern bool UnloadKeyboardLayout(IntPtr hkl);
'@
    $n = [ClavierPulaar.Dispositions]::GetKeyboardLayoutList(0, $null)
    $hkls = New-Object IntPtr[] $n
    [void][ClavierPulaar.Dispositions]::GetKeyboardLayoutList($n, $hkls)
    foreach ($hkl in $hkls) {
        # 08670867 et Fxxx0867 : les anciennes dispositions ; 040C0867 et 04090867
        # (claviers de Windows sous FUL) restent.
        $langue = $hkl.ToInt64() -band 0xFFFF
        $appareil = ($hkl.ToInt64() -shr 16) -band 0xFFFF
        if ($langue -eq 0x0867 -and $appareil -ne 0x040C -and $appareil -ne 0x0409) {
            [void][ClavierPulaar.Dispositions]::UnloadKeyboardLayout($hkl)
        }
    }
    Remove-Item 'HKCU:\Software\Microsoft\CTF\SortOrder\AssemblyItem\0x00000867' -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host '      Retires.' -ForegroundColor Green
}

function Install-Machine {
    Write-Host '[2/3] Anciennes dispositions Pulaar effacees...' -ForegroundColor Yellow
    foreach ($klid in $anciennesDispositions) {
        if (Test-Ancienne $klid) {
            Remove-Item (Join-Path $base $klid) -Recurse -Force
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
    $fichier = ([string](Get-ItemProperty $wolof -ErrorAction SilentlyContinue).'Layout File').ToLower()
    if ($anciensFichiers -contains $fichier) {
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
    Set-ItemProperty $cleDesinstallation -Name 'DisplayName' -Value 'Fulfulde Keyboard'
    Set-ItemProperty $cleDesinstallation -Name 'DisplayVersion' -Value '2.5.1'
    Set-ItemProperty $cleDesinstallation -Name 'Publisher' -Value 'Tarolearning'
    Set-ItemProperty $cleDesinstallation -Name 'DisplayIcon' -Value "$ici\icones\clavier_pulaar.ico"
    Set-ItemProperty $cleDesinstallation -Name 'InstallLocation' -Value $ici
    Set-ItemProperty $cleDesinstallation -Name 'UninstallString' -Value $desinstaller
    Set-ItemProperty $cleDesinstallation -Name 'NoModify' -Value 1 -Type DWord
    Set-ItemProperty $cleDesinstallation -Name 'NoRepair' -Value 1 -Type DWord
}

function Install-Utilisateur {
    Write-Host '[3/3] FUL (Pulaar) dans Win + Espace...' -ForegroundColor Yellow
    $liste = Get-WinUserLanguageList
    $pulaar = $liste | Where-Object { $_.LanguageTag -like 'ff-Latn*' } | Select-Object -First 1
    if (-not $pulaar) {
        $liste.Add('ff-Latn-SN')
        $pulaar = $liste | Where-Object { $_.LanguageTag -like 'ff-Latn*' } | Select-Object -First 1
    }
    # La langue arrive avec le clavier Wolof de Windows : Francais (AZERTY) et
    # Anglais (QWERTY) a sa place, ceux que l'on a deja sous les doigts.
    $pulaar.InputMethodTips.Clear()
    foreach ($tip in $claviersFul) { $pulaar.InputMethodTips.Add($tip) }
    Set-WinUserLanguageList $liste -Force

    # Get-WinUserLanguageList rend la liste d'un bloc : foreach la parcourt langue par langue.
    $verifie = foreach ($langue in (Get-WinUserLanguageList)) { if ($langue.LanguageTag -like 'ff-Latn*') { $langue } }
    if ($verifie -and $verifie.InputMethodTips.Count -gt 0) {
        Write-Host "      FUL : $($verifie.InputMethodTips -join ', ')" -ForegroundColor Green
    } else {
        Write-Host '      Windows n a pas garde FUL (Pulaar) : ouvrez Parametres > Heure et langue.' -ForegroundColor Red
    }

    Write-Host '      Correcteur orthographique pulaar (Edge, Chrome...)...' -ForegroundColor Yellow
    try {
        & (Join-Path $ici 'correcteur_pulaar\enregistrer_correcteur.ps1')
    } catch {
        Write-Host "      Correcteur non enregistre : $_" -ForegroundColor Red
    }

    if ($SansMoteur) { return }
    Write-Host '      Moteur (lettres pulaar et suggestions)...' -ForegroundColor Yellow
    $demarrage = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run'
    # L'ancien nom (versions 2.4.1 et avant) quitte les applications de demarrage.
    Remove-ItemProperty $demarrage -Name 'ClavierPulaar' -ErrorAction SilentlyContinue
    if ($empaquete) {
        Set-ItemProperty $demarrage -Name 'FulfuldeKeyboard' -Value "`"$exe`""
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
    Set-ItemProperty $demarrage -Name 'FulfuldeKeyboard' -Value "`"$pythonw`" `"$script`""
    Start-Process $pythonw -ArgumentList "`"$script`""
    Write-Host '      Lance, et demarrera avec Windows (icone pres de l horloge).' -ForegroundColor Green
}

if ($Preparation) {
    Install-Preparation
    exit 0
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
Write-Host '   INSTALLATION DE FULFULDE KEYBOARD' -ForegroundColor Green
Write-Host '============================================================' -ForegroundColor Cyan
Install-Preparation
if (Test-Administrateur) {
    Install-Machine
} else {
    # La partie machine demande les droits d'administrateur ; la liste des
    # langues, elle, se change dans la session de l'utilisateur.
    $p = Start-Process powershell.exe -Verb RunAs -Wait -PassThru -ArgumentList @(
        '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', "`"$PSCommandPath`"", '-MachineOnly')
    if ($p.ExitCode -ne 0) { throw 'La partie administrateur a echoue.' }
}
Install-Utilisateur
Write-Host ''
Write-Host 'Termine. Win + Espace : choisissez FUL, puis v donne ɓ, z ɗ, q ŋ, x ƴ.' -ForegroundColor Cyan
