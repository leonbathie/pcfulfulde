# ============================================================
#  Desinstalle le Clavier Pulaar (Fulfulde)
# ============================================================
#  Retire les claviers Pulaar de la liste Win + Espace et le demarrage
#  automatique (utilisateur), puis les dispositions et l'entree des
#  applications installees (administrateur). La disposition Wolof de Windows
#  et les autres langues ne sont pas touchees.
param([switch]$MachineOnly)

$ErrorActionPreference = 'Stop'
$base = 'HKLM:\SYSTEM\CurrentControlSet\Control\Keyboard Layouts'
# 00000867 : l'AZERTY, disposition principale de la langue peule ; a0010867 :
# le QWERTY ; a0000867 : l'ancienne inscription de l'AZERTY.
$klids = @('00000867', 'a0010867', 'a0000867')
$nosDll = @('fulffaz.dll', 'fulffqw.dll', 'kbdfulfa.dll', 'kbdfulfq.dll')

function Test-Administrateur {
    ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
        [Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Uninstall-Machine {
    foreach ($klid in $klids) {
        $cle = Join-Path $base $klid
        $fichier = (Get-ItemProperty $cle -ErrorAction SilentlyContinue).'Layout File'
        # Seulement nos dispositions, jamais une disposition de Windows.
        if ($fichier -and ($nosDll -contains $fichier.ToLower())) { Remove-Item $cle -Recurse -Force }
    }
    # Un fichier encore ouvert par une application reste en place : il ne sert
    # plus a rien une fois les cles retirees.
    foreach ($dll in 'fulffaz.dll', 'fulffqw.dll') {
        foreach ($dossier in "$env:SystemRoot\System32", "$env:SystemRoot\SysWOW64") {
            Remove-Item (Join-Path $dossier $dll) -Force -ErrorAction SilentlyContinue
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
Remove-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' -Name 'ClavierPulaar' -ErrorAction SilentlyContinue
& (Join-Path (Split-Path -Parent $PSCommandPath) 'correcteur_pulaar\enregistrer_correcteur.ps1') -Retirer

$liste = Get-WinUserLanguageList
foreach ($langue in @($liste | Where-Object { $_.LanguageTag -like 'ff-Latn*' })) {
    foreach ($klid in $klids) {
        foreach ($tip in @($langue.InputMethodTips | Where-Object { $_ -like "*:$klid" })) {
            [void]$langue.InputMethodTips.Remove($tip)
        }
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
Write-Host 'Clavier Pulaar desinstalle.' -ForegroundColor Green
