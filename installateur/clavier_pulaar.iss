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
ShowLanguageDialog=yes
LanguageDetectionMethod=uilanguage
; Signature : fabriquer_installateur.ps1 -Signer (voir installateur\signer.ps1).
#ifdef Signer
SignTool=signature
SignedUninstaller=yes
#endif

[Languages]
;  Toutes les langues fournies avec Inno Setup : l'assistant demande la sienne
;  en premier, celle de Windows proposee d'office.
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "arabic"; MessagesFile: "compiler:Languages\Arabic.isl"
Name: "armenian"; MessagesFile: "compiler:Languages\Armenian.isl"
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
Name: "bulgarian"; MessagesFile: "compiler:Languages\Bulgarian.isl"
Name: "catalan"; MessagesFile: "compiler:Languages\Catalan.isl"
Name: "corsican"; MessagesFile: "compiler:Languages\Corsican.isl"
Name: "czech"; MessagesFile: "compiler:Languages\Czech.isl"
Name: "danish"; MessagesFile: "compiler:Languages\Danish.isl"
Name: "dutch"; MessagesFile: "compiler:Languages\Dutch.isl"
Name: "finnish"; MessagesFile: "compiler:Languages\Finnish.isl"
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"
Name: "hebrew"; MessagesFile: "compiler:Languages\Hebrew.isl"
Name: "hungarian"; MessagesFile: "compiler:Languages\Hungarian.isl"
Name: "italian"; MessagesFile: "compiler:Languages\Italian.isl"
Name: "japanese"; MessagesFile: "compiler:Languages\Japanese.isl"
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"
Name: "norwegian"; MessagesFile: "compiler:Languages\Norwegian.isl"
Name: "polish"; MessagesFile: "compiler:Languages\Polish.isl"
Name: "portuguese"; MessagesFile: "compiler:Languages\Portuguese.isl"
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"
Name: "slovak"; MessagesFile: "compiler:Languages\Slovak.isl"
Name: "slovenian"; MessagesFile: "compiler:Languages\Slovenian.isl"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "swedish"; MessagesFile: "compiler:Languages\Swedish.isl"
Name: "tamil"; MessagesFile: "compiler:Languages\Tamil.isl"
Name: "thai"; MessagesFile: "compiler:Languages\Thai.isl"
Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"
Name: "ukrainian"; MessagesFile: "compiler:Languages\Ukrainian.isl"

; Messages propres au Clavier Pulaar : en anglais pour toutes les langues, en
; français pour le français.
[Messages]
FinishedLabel=The Pulaar Keyboard is installed.%n%nPress Win + Space and choose "Pulaar (Fulfulde) AZERTY". As you type, suggestions appear above the cursor: Tab takes the highlighted one, ← → highlight another.%n%nSettings are behind the ɓ icon, next to the clock.
french.FinishedLabel=Le Clavier Pulaar est installé.%n%nAppuyez sur Win + Espace et choisissez « Pulaar (Fulfulde) AZERTY ». En écrivant, les suggestions apparaissent au-dessus du curseur : Tab prend la suggestion en surbrillance, ← → en surlignent une autre.%n%nLes réglages sont derrière l'icône ɓ, près de l'horloge.

[CustomMessages]
AjoutClaviers=Adding the Pulaar keyboards to Windows...
french.AjoutClaviers=Ajout des claviers Pulaar à Windows...
PulaarWinEspace=Pulaar in Win + Space, spell checker and suggestions...
french.PulaarWinEspace=Pulaar dans Win + Espace, correcteur et suggestions...
Commentaire=Pulaar word suggestions and corrections
french.Commentaire=Suggestions et correction en pulaar

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
Name: "{autoprograms}\Clavier Pulaar"; Filename: "{app}\ClavierPulaar.exe"; Comment: "{cm:Commentaire}"

[Run]
Filename: "powershell.exe"; Parameters: "-NoProfile -ExecutionPolicy Bypass -File ""{app}\installer_clavier_pulaar.ps1"" -MachineOnly"; StatusMsg: "{cm:AjoutClaviers}"; Flags: runhidden waituntilterminated
Filename: "powershell.exe"; Parameters: "-NoProfile -ExecutionPolicy Bypass -File ""{app}\installer_clavier_pulaar.ps1"" -UtilisateurSeulement"; StatusMsg: "{cm:PulaarWinEspace}"; Flags: runhidden waituntilterminated runasoriginaluser

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
