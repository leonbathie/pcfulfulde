# ============================================================
#  Desinstalle Fulfulde Keyboard (clavier pulaar)
# ============================================================
#  Retire FUL (Pulaar) de la liste Win + Espace et le demarrage automatique
#  (utilisateur), puis les anciennes dispositions et l'entree des applications
#  installees (administrateur). Les claviers de Windows, la disposition Wolof
#  et les autres langues ne sont pas touches.
param([switch]$MachineOnly)

$ErrorActionPreference = 'Stop'
$base = 'HKLM:\SYSTEM\CurrentControlSet\Control\Keyboard Layouts'
# Les anciennes dispositions (versions precedentes) : 00000867, l'AZERTY,
# disposition principale de la langue pulaar (ff-Latn-SN) ; a0010867, le
# QWERTY ; a0000867, l'ancienne inscription de l'AZERTY.
$klids = @('00000867', 'a0010867', 'a0000867')
# Sous FUL, Fulfulde Keyboard met aussi les claviers Francais et Anglais de
# Windows : ils partent de la liste avec lui, mais restent dans Windows.
$claviersFul = $klids + @('0000040c', '00000409')
$nosDll = @('fulffaz.dll', 'fulffqw.dll', 'kbdfulfa.dll', 'kbdfulfq.dll')

function Test-Administrateur {
    ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
        [Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Uninstall-Machine {
    foreach ($klid in $klids) {
        $cle = Join-Path $base $klid
        $v = Get-ItemProperty $cle -ErrorAction SilentlyContinue
        # Seulement nos anciennes dispositions : l'un de nos anciens fichiers,
        # ou l'un de nos noms. Jamais une disposition de Windows.
        if ($v -and (($nosDll -contains ([string]$v.'Layout File').ToLower()) -or
                     ([string]$v.'Layout Text' -like 'Pulaar (Fulfulde)*'))) {
            Remove-Item $cle -Recurse -Force
        }
    }
    # Nos anciens fichiers seulement, jamais ceux de Windows (KBDFR.DLL, KBDUS.DLL).
    # Un fichier encore ouvert reste en place : il ne sert plus a rien une fois
    # les cles retirees.
    foreach ($dossier in "$env:SystemRoot\System32", "$env:SystemRoot\SysWOW64") {
        foreach ($motif in 'fulffaz.dll', 'fulffqw.dll', 'fulff*.dll.*.ancienne') {
            Remove-Item (Join-Path $dossier $motif) -Force -ErrorAction SilentlyContinue
        }
    }
    Remove-Item 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\ClavierPulaar' -Recurse -Force -ErrorAction SilentlyContinue
}

if ($MachineOnly) {
    if (-not (Test-Administrateur)) { throw 'La partie machine doit tourner en administrateur.' }
    Uninstall-Machine
    exit 0
}

# Utilisateur : arret du moteur, demarrage automatique, correcteur, liste des langues
Get-CimInstance Win32_Process -Filter "Name = 'pythonw.exe' OR Name = 'python.exe'" |
    Where-Object { $_.CommandLine -like '*clavier_fulfulde_natif.py*' } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
# Le programme et son demarrage automatique, sous le nom actuel et l'ancien (2.4.1 et avant)
Get-Process -Name 'FulfuldeKeyboard', 'ClavierPulaar' -ErrorAction SilentlyContinue | Stop-Process -Force
foreach ($nom in 'FulfuldeKeyboard', 'ClavierPulaar') {
    Remove-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' -Name $nom -ErrorAction SilentlyContinue
}
& (Join-Path (Split-Path -Parent $PSCommandPath) 'correcteur_pulaar\enregistrer_correcteur.ps1') -Retirer

$liste = Get-WinUserLanguageList
foreach ($langue in @($liste | Where-Object { $_.LanguageTag -like 'ff-Latn*' })) {
    foreach ($tip in @($langue.InputMethodTips | Where-Object { $claviersFul -contains ($_ -split ':')[-1].ToLower() })) {
        [void]$langue.InputMethodTips.Remove($tip)
    }
    if ($langue.InputMethodTips.Count -eq 0) { [void]$liste.Remove($langue) }
}
Set-WinUserLanguageList $liste -Force

if (Test-Administrateur) {
    Uninstall-Machine
} else {
    Start-Process powershell.exe -Verb RunAs -Wait -ArgumentList @(
        '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', "`"$PSCommandPath`"", '-MachineOnly')
}
Write-Host 'Fulfulde Keyboard desinstalle.' -ForegroundColor Green
