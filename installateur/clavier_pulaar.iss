; ============================================================
;  Installateur du Clavier Pulaar (Fulfulde)
; ============================================================
;  Produit Setup_Clavier_Pulaar.exe (installateur\fabriquer_installateur.ps1).
;  L'assistant copie le clavier dans Program Files, puis lance
;  installer_clavier_pulaar.ps1 : les dispositions Pulaar dans Windows (partie
;  administrateur), puis la langue Peul dans Win + Espace, le correcteur
;  orthographique et le moteur de suggestions (partie utilisateur).

#define Nom "Clavier Pulaar (Fulfulde)"
#define Version "2.0"
#define Racine ".."

[Setup]
AppId={{6D3F8A2E-5B7C-4E19-A0D4-2C8E1F9B7A35}
AppName={#Nom}
AppVersion={#Version}
AppVerName={#Nom} {#Version}
AppPublisher=Fulfulde Community
AppPublisherURL=https://github.com/leonbathie/pcfulfulde
AppSupportURL=https://github.com/leonbathie/pcfulfulde
DefaultDirName={autopf}\Clavier Pulaar
DisableProgramGroupPage=yes
OutputDir={#Racine}
OutputBaseFilename=Setup_Clavier_Pulaar
SetupIconFile={#Racine}\icones\clavier_pulaar.ico
UninstallDisplayIcon={app}\ClavierPulaar.exe
UninstallDisplayName={#Nom}
Compression=lzma2/ultra64
SolidCompression=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=admin
WizardStyle=modern
MinVersion=10.0
; Le moteur tient ses fichiers ouverts : l'assistant l'arrête lui-même (PrepareToInstall).
CloseApplications=no

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Messages]
french.FinishedLabel=Le Clavier Pulaar est installé.%n%nAppuyez sur Win + Espace et choisissez « Pulaar (Fulfulde) AZERTY ». En écrivant, les suggestions apparaissent au-dessus du curseur : Tab prend la suggestion en surbrillance.%n%nLes réglages sont derrière l'icône ɓ, près de l'horloge.

[Files]
Source: "{#Racine}\construction\dist\ClavierPulaar\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#Racine}\fulffaz_amd64.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#Racine}\fulffaz_x86.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#Racine}\fulffqw_amd64.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#Racine}\fulffqw_x86.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#Racine}\installer_clavier_pulaar.ps1"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#Racine}\desinstaller_clavier_pulaar.ps1"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#Racine}\correcteur_pulaar\correcteur_pulaar.dll"; DestDir: "{app}\correcteur_pulaar"; Flags: ignoreversion
Source: "{#Racine}\correcteur_pulaar\enregistrer_correcteur.ps1"; DestDir: "{app}\correcteur_pulaar"; Flags: ignoreversion
Source: "{#Racine}\dictionary\mots_pulaar.txt"; DestDir: "{app}\dictionary"; Flags: ignoreversion
Source: "{#Racine}\icones\clavier_pulaar.ico"; DestDir: "{app}\icones"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\Clavier Pulaar"; Filename: "{app}\ClavierPulaar.exe"; Comment: "Suggestions et correction en pulaar"

[Run]
Filename: "powershell.exe"; Parameters: "-NoProfile -ExecutionPolicy Bypass -File ""{app}\installer_clavier_pulaar.ps1"" -MachineOnly"; StatusMsg: "Ajout des claviers Pulaar à Windows..."; Flags: runhidden waituntilterminated
Filename: "powershell.exe"; Parameters: "-NoProfile -ExecutionPolicy Bypass -File ""{app}\installer_clavier_pulaar.ps1"" -UtilisateurSeulement"; StatusMsg: "Pulaar dans Win + Espace, correcteur et suggestions..."; Flags: runhidden waituntilterminated runasoriginaluser

[UninstallRun]
Filename: "powershell.exe"; Parameters: "-NoProfile -ExecutionPolicy Bypass -File ""{app}\desinstaller_clavier_pulaar.ps1"""; Flags: runhidden waituntilterminated; RunOnceId: "RetireClavierPulaar"

[Code]
{ Le moteur, installé ou lancé depuis le dossier du projet : ses fichiers
  seraient verrouillés pendant la copie ou la désinstallation. }
procedure ArreteLeMoteur;
var
  Code: Integer;
begin
  Exec(ExpandConstant('{sys}\taskkill.exe'), '/F /IM ClavierPulaar.exe', '', SW_HIDE, ewWaitUntilTerminated, Code);
  Exec('powershell.exe', '-NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like ''*clavier_fulfulde_natif*'' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }"', '', SW_HIDE, ewWaitUntilTerminated, Code);
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
begin
  ArreteLeMoteur;
  Result := '';
end;

function InitializeUninstall(): Boolean;
begin
  ArreteLeMoteur;
  Result := True;
end;
