# ============================================================
#  Compile les dispositions Pulaar AZERTY et QWERTY
# ============================================================
#  1. generate_klc.py ecrit fulffaz.klc et fulffqw.klc (la source des touches) ;
#  2. kbdutool, l'outil de Microsoft Keyboard Layout Creator, en fait les DLL :
#     *_amd64.dll pour System32, *_wow64.dll pour SysWOW64 (les applications
#     32 bits d'un Windows 64 bits), comme les installe Microsoft.
#
#  -Kbdutool : chemin de kbdutool.exe, s'il n'est pas a l'un des endroits connus.
param([string]$Kbdutool)

$ErrorActionPreference = 'Stop'
$racine = Split-Path -Parent (Split-Path -Parent $PSCommandPath)

if (-not $Kbdutool) {
    $Kbdutool = @(
        "$env:USERPROFILE\Desktop\msklc_out\bin\i386\kbdutool.exe",
        "${env:ProgramFiles(x86)}\Microsoft Keyboard Layout Creator 1.4\bin\i386\kbdutool.exe"
    ) | Where-Object { Test-Path $_ } | Select-Object -First 1
}
if (-not $Kbdutool -or -not (Test-Path $Kbdutool)) {
    throw 'kbdutool.exe introuvable : installez Microsoft Keyboard Layout Creator 1.4, ou passez -Kbdutool.'
}

Push-Location $racine
try {
    python generate_klc.py
    if ($LASTEXITCODE -ne 0) { throw 'generate_klc.py a echoue.' }
} finally {
    Pop-Location
}

$travail = Join-Path ([IO.Path]::GetTempPath()) "dispositions_pulaar_$PID"
foreach ($nom in 'fulffaz', 'fulffqw') {
    foreach ($cible in @(@{ Option = '-m'; Suffixe = 'amd64' }, @{ Option = '-o'; Suffixe = 'wow64' })) {
        $dossier = Join-Path $travail "$nom-$($cible.Suffixe)"
        New-Item -ItemType Directory -Force $dossier | Out-Null
        Copy-Item (Join-Path $racine "$nom.klc") $dossier
        Push-Location $dossier
        try {
            & $Kbdutool -n -u $cible.Option "$nom.klc"
            if ($LASTEXITCODE -ne 0 -or -not (Test-Path "$nom.dll")) { throw "kbdutool a echoue pour $nom ($($cible.Suffixe))." }
        } finally {
            Pop-Location
        }
        Copy-Item (Join-Path $dossier "$nom.dll") (Join-Path $racine "$($nom)_$($cible.Suffixe).dll") -Force
        Write-Host "      $($nom)_$($cible.Suffixe).dll" -ForegroundColor Green
    }
}
Remove-Item $travail -Recurse -Force -ErrorAction SilentlyContinue
