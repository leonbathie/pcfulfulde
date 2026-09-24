; ============================================================
; Script Inno Setup Officiel pour Clavier Fulfulde Latin
; Produit un installateur Setup.exe complet identique a Microsoft
; ============================================================

[Setup]
AppId={{9F3B96A1-7F2D-4D3C-8A3E-91B2D3E4F5A6}
AppName=Clavier Fulfulde Latin
AppVersion=1.0
AppPublisher=Fulfulde Community
DefaultDirName={autopf}\ClavierFulfulde
DefaultGroupName=Clavier Fulfulde
OutputDir=.
OutputBaseFilename=Setup_Clavier_Fulfulde
Compression=lzma2/ultra64
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=admin
WizardStyle=modern
UninstallDisplayIcon={sys}\fulffaz.dll
UninstallDisplayName=Clavier Fulfulde Latin
DisableWelcomePage=no
DisableDirPage=yes
DisableProgramGroupPage=yes

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Messages]
french.BeveledLabel=Clavier Fulfulde Latin pour Windows

[Files]
; 1. Pilotes 64-bit compiles avec Microsoft KbdTool (installes dans System32 sur x64)
Source: "fulffaz_amd64.dll"; DestDir: "{sys}"; DestName: "fulffaz.dll"; Check: Is64BitInstallMode; Flags: restartreplace uninsrestartdelete
Source: "fulffqw_amd64.dll"; DestDir: "{sys}"; DestName: "fulffqw.dll"; Check: Is64BitInstallMode; Flags: restartreplace uninsrestartdelete

; 2. Pilotes 32-bit compiles avec Microsoft KbdTool (installes dans SysWOW64 sur x64 pour compatibilite 32-bit)
Source: "fulffaz_x86.dll"; DestDir: "{syswow64}"; DestName: "fulffaz.dll"; Check: Is64BitInstallMode; Flags: restartreplace uninsrestartdelete
Source: "fulffqw_x86.dll"; DestDir: "{syswow64}"; DestName: "fulffqw.dll"; Check: Is64BitInstallMode; Flags: restartreplace uninsrestartdelete

; 3. Cas Windows 32-bit pur
Source: "fulffaz_x86.dll"; DestDir: "{sys}"; DestName: "fulffaz.dll"; Check: not Is64BitInstallMode; Flags: restartreplace uninsrestartdelete
Source: "fulffqw_x86.dll"; DestDir: "{sys}"; DestName: "fulffqw.dll"; Check: not Is64BitInstallMode; Flags: restartreplace uninsrestartdelete

[Registry]
; Disposition AZERTY : la disposition principale de la langue peule (00000867),
; sans Layout Id, comme les claviers de Microsoft pour leurs langues. Windows
; n'en livre aucune pour 0867 : inscrit seulement en variante (a0000867), le
; premier clavier de la langue renvoyait a une disposition 00000867 absente,
; et le selecteur Win + Espace faisait planter l'Explorateur (InputSwitch.dll).
Root: HKLM; Subkey: "SYSTEM\CurrentControlSet\Control\Keyboard Layouts\00000867"; ValueType: string; ValueName: "Layout File"; ValueData: "fulffaz.dll"; Flags: uninsdeletekey
Root: HKLM; Subkey: "SYSTEM\CurrentControlSet\Control\Keyboard Layouts\00000867"; ValueType: string; ValueName: "Layout Text"; ValueData: "Pulaar (Fulfulde) AZERTY"; Flags: uninsdeletekey
Root: HKLM; Subkey: "SYSTEM\CurrentControlSet\Control\Keyboard Layouts\00000867"; ValueType: string; ValueName: "Layout Display Name"; ValueData: "Pulaar (Fulfulde) AZERTY"; Flags: uninsdeletekey

; Disposition QWERTY : une variante. Son Layout Id ne doit etre celui d'aucune
; autre disposition (00a1 est celui du Lituanien standard) : deux dispositions
; au meme Layout Id, et Windows peut charger la mauvaise. Windows 11 s'arrete
; a 00d5.
Root: HKLM; Subkey: "SYSTEM\CurrentControlSet\Control\Keyboard Layouts\a0010867"; ValueType: string; ValueName: "Layout File"; ValueData: "fulffqw.dll"; Flags: uninsdeletekey
Root: HKLM; Subkey: "SYSTEM\CurrentControlSet\Control\Keyboard Layouts\a0010867"; ValueType: string; ValueName: "Layout Text"; ValueData: "Pulaar (Fulfulde) QWERTY"; Flags: uninsdeletekey
Root: HKLM; Subkey: "SYSTEM\CurrentControlSet\Control\Keyboard Layouts\a0010867"; ValueType: string; ValueName: "Layout Display Name"; ValueData: "Pulaar (Fulfulde) QWERTY"; Flags: uninsdeletekey
Root: HKLM; Subkey: "SYSTEM\CurrentControlSet\Control\Keyboard Layouts\a0010867"; ValueType: string; ValueName: "Layout Id"; ValueData: "00f1"; Flags: uninsdeletekey

; La disposition Wolof de Windows (00000488) n'est plus remplacee : sa
; desinstallation effacait son fichier et laissait Wolof sans clavier.

[Run]
; Activation automatique des dispositions Fulfulde AZERTY et QWERTY dans les Parametres Windows et la barre des langues
Filename: "powershell.exe"; Parameters: "-NoProfile -ExecutionPolicy Bypass -Command ""$l = Get-WinUserLanguageList; $p = $l | Where-Object {{ $_.LanguageTag -eq 'ff-Latn-SN' }}; if (!$p) {{ $l.Add('ff-Latn-SN'); $p = $l | Where-Object {{ $_.LanguageTag -eq 'ff-Latn-SN' }} }}; if ($p) {{ $p.InputMethodTips.Clear(); $p.InputMethodTips.Add('0867:00000867'); $p.InputMethodTips.Add('0867:a0010867'); Set-WinUserLanguageList $l -Force }};"""; StatusMsg: "Activation de la langue Peul dans Windows..."; Flags: runhidden runasoriginaluser
