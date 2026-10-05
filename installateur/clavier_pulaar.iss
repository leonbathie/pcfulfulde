; ============================================================
;  Installateur de Fulfulde Keyboard (clavier pulaar)
; ============================================================
;  Produit Fulfulde_Keyboard.exe (installateur\fabriquer_installateur.ps1).
;  L'assistant copie le clavier dans Program Files, puis lance
;  installer_clavier_pulaar.ps1 en trois parties : retrait des anciens claviers
;  Pulaar de Win + Espace, effacement de leurs dispositions (administrateur),
;  puis FUL (Pulaar) dans Win + Espace avec les claviers Français ou Anglais de
;  Windows, le correcteur orthographique et le moteur, qui place lui-même les
;  lettres pulaar quand FUL est choisi.

#define Nom "Fulfulde Keyboard"
#define Version "2.6.6"
#define Racine ".."

[Setup]
AppId={{6D3F8A2E-5B7C-4E19-A0D4-2C8E1F9B7A35}
AppName={#Nom}
AppVersion={#Version}
AppVerName={#Nom} {#Version}
AppPublisher=Taro Learning
AppPublisherURL=https://github.com/leonbathie/pcfulfulde
AppSupportURL=https://github.com/leonbathie/pcfulfulde
DefaultDirName={autopf}\Fulfulde Keyboard
; Les versions 2.4.1 et avant s'installaient dans « Clavier Pulaar » : la mise
; à jour va dans le nouveau dossier, et [InstallDelete] retire l'ancien.
UsePreviousAppDir=no
DisableProgramGroupPage=yes
OutputDir={#Racine}
OutputBaseFilename=Fulfulde_Keyboard
SetupIconFile={#Racine}\icones\clavier_pulaar.ico
UninstallDisplayIcon={app}\FulfuldeKeyboard.exe
UninstallDisplayName={#Nom}
Compression=lzma2/ultra64
; 32 Mo au lieu de 64 : les ~26 Mo de fichiers y tiennent (même taille finale),
; et la compression demande moitié moins de mémoire (PC de 4 Go).
LZMADictionarySize=32768
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

; Messages propres à Fulfulde Keyboard : en anglais pour toutes les langues, en
; français pour le français.
[Messages]
FinishedLabel=Fulfulde Keyboard is installed.%n%nPress Win + Space and choose FUL, with the French (AZERTY) or English (QWERTY) keyboard: v gives ɓ, z gives ɗ, q gives ŋ, x gives ƴ, and suggestions appear above the cursor: Tab takes the highlighted one, ← → highlight another. With French or English, your keyboard does not change.%n%nSettings are behind the ɓ icon, next to the clock.
french.FinishedLabel=Fulfulde Keyboard est installé.%n%nAppuyez sur Win + Espace et choisissez FUL, avec le clavier Français (AZERTY) ou Anglais (QWERTY) : v donne ɓ, z donne ɗ, q donne ŋ, x donne ƴ, et les suggestions apparaissent au-dessus du curseur : Tab prend la suggestion en surbrillance, ← → en surlignent une autre. Avec Français ou Anglais, votre clavier ne change pas.%n%nLes réglages sont derrière l'icône ɓ, près de l'horloge.

[CustomMessages]
Preparation=Preparing the Pulaar keyboards...
french.Preparation=Préparation des claviers Pulaar...
RetraitAnciensClaviers=Removing the old Pulaar keyboards from Windows...
french.RetraitAnciensClaviers=Retrait des anciens claviers Pulaar de Windows...
PulaarWinEspace=FUL (Pulaar) in Win + Space, spell checker and suggestions...
french.PulaarWinEspace=FUL (Pulaar) dans Win + Espace, correcteur et suggestions...
Commentaire=Pulaar word suggestions and corrections
french.Commentaire=Suggestions et correction en pulaar

[InstallDelete]
; L'ancien nom (versions 2.4.1 et avant) : le dossier et le raccourci
; « Clavier Pulaar ». Le moteur est déjà arrêté (PrepareToInstall).
Type: filesandordirs; Name: "{autopf}\Clavier Pulaar"
Type: files; Name: "{autoprograms}\Clavier Pulaar.lnk"

[Files]
Source: "{#Racine}\construction\dist\FulfuldeKeyboard\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#Racine}\installer_clavier_pulaar.ps1"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#Racine}\desinstaller_clavier_pulaar.ps1"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#Racine}\correcteur_pulaar\correcteur_pulaar.dll"; DestDir: "{app}\correcteur_pulaar"; Flags: ignoreversion
Source: "{#Racine}\correcteur_pulaar\enregistrer_correcteur.ps1"; DestDir: "{app}\correcteur_pulaar"; Flags: ignoreversion
Source: "{#Racine}\dictionary\mots_pulaar.txt"; DestDir: "{app}\dictionary"; Flags: ignoreversion
Source: "{#Racine}\icones\clavier_pulaar.ico"; DestDir: "{app}\icones"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\Fulfulde Keyboard"; Filename: "{app}\FulfuldeKeyboard.exe"; Comment: "{cm:Commentaire}"

[Run]
; Dans cet ordre : les anciens claviers Pulaar quittent la liste Win + Espace
; (utilisateur), puis leurs dispositions sont effacées (administrateur), puis
; FUL (Pulaar) revient dans Win + Espace avec les claviers de Windows
; (utilisateur). Une langue qui renvoie à une disposition effacée fait planter
; le sélecteur Win + Espace.
Filename: "powershell.exe"; Parameters: "-NoProfile -ExecutionPolicy Bypass -File ""{app}\installer_clavier_pulaar.ps1"" -Preparation"; StatusMsg: "{cm:Preparation}"; Flags: runhidden waituntilterminated runasoriginaluser
Filename: "powershell.exe"; Parameters: "-NoProfile -ExecutionPolicy Bypass -File ""{app}\installer_clavier_pulaar.ps1"" -MachineOnly"; StatusMsg: "{cm:RetraitAnciensClaviers}"; Flags: runhidden waituntilterminated
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
  Exec(ExpandConstant('{sys}\taskkill.exe'), '/F /IM FulfuldeKeyboard.exe /IM ClavierPulaar.exe', '', SW_HIDE, ewWaitUntilTerminated, Code);
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
