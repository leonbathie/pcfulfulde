# Clavier Pulaar (Fulfulde) pour Windows

> Un clavier pulaar qui se comporte comme ceux de Microsoft : il propose des mots pulaar au-dessus du curseur, corrige les fautes à l'espace et retient vos mots. Toujours actif, comme l'ancien clavier : avec votre clavier habituel (Français, Anglais…), il place lui-même les lettres pulaar (v → ɓ, z → ɗ, q → ŋ, x → ƴ). Uniquement des mots pulaar.

---

## Download

*Télécharger.* Les versions sont publiées dans **[Releases](https://github.com/leonbathie/pcfulfulde/releases)** : téléchargez `Setup_Clavier_Pulaar.exe`. Les installateurs signés le sont par SignPath Foundation : free code signing provided by [SignPath.io](https://about.signpath.io/), certificate by [SignPath Foundation](https://signpath.org/) (voir [Code signing policy](#code-signing-policy)).

---

## 🚀 Installation (une fois)

1. Lancez **`Setup_Clavier_Pulaar.exe`**, choisissez la langue de l'assistant (30 langues, celle de Windows proposée d'office), suivez-le et répondez **Oui** quand Windows demande l'autorisation. Python n'est pas nécessaire : le clavier est installé dans `C:\Program Files\Clavier Pulaar`.
2. Le clavier démarre aussitôt, puis à chaque ouverture de session. Son icône **ɓ** se trouve près de l'horloge.
3. Écrivez avec votre clavier habituel : rien à choisir dans Win + Espace.

Pour tout retirer : **Paramètres > Applications > Clavier Pulaar (Fulfulde) > Désinstaller**.

L'assistant lance `installer_clavier_pulaar.ps1`, qui :
- enregistre le correcteur orthographique pulaar et fait démarrer le clavier avec Windows ;
- retire les claviers « Pulaar (Fulfulde) AZERTY / QWERTY » que les versions 2.0 à 2.2 inscrivaient dans Windows, d'abord de la liste Win + Espace, puis de Windows. Le sélecteur Win + Espace de Windows 11 (`InputSwitch.dll`) plantait sur eux et emportait l'Explorateur ; le moteur n'en a plus besoin ;
- rend à Windows sa disposition Wolof, que les anciens installateurs avaient remplacée.

> `Setup_Clavier_Fulfulde.exe` est l'**ancien** installateur : ne l'utilisez plus. Il remplaçait la disposition Wolof de Windows et réutilisait un *Layout Id* déjà pris, ce qui faisait planter Win + Espace.

### Fabriquer l'installateur

```powershell
powershell -ExecutionPolicy Bypass -File installateur\fabriquer_installateur.ps1
```

Le script transforme le clavier en `ClavierPulaar.exe` avec PyInstaller, puis produit `Setup_Clavier_Pulaar.exe` avec Inno Setup 6 (`installateur\clavier_pulaar.iss`). Il faut Python avec `pynput` et `pyinstaller`, et Inno Setup 6.

### Signer l'installateur (pour le partager)

Sans signature, Windows avertit ceux qui téléchargent l'installateur (« Windows a protégé votre ordinateur »). Une signature reconnue demande un **certificat de signature de code délivré à votre nom** par une autorité, après vérification de votre identité. Par exemple :
- Certum *Open Source Code Signing*, pour les projets libres ;
- SignPath Foundation, gratuit pour les projets libres ; la signature se fait alors dans GitHub Actions ;
- SSL.com ou Sectigo.

Une fois le certificat installé (ou en fichier `.pfx`) :

```powershell
$env:CLAVIER_PULAAR_CERTIFICAT = "<empreinte du certificat>"   # ou CLAVIER_PULAAR_PFX et CLAVIER_PULAAR_PFX_MDP
powershell -ExecutionPolicy Bypass -File installateur\fabriquer_installateur.ps1 -Signer
```

`ClavierPulaar.exe`, l'installateur et son désinstalleur sont alors signés et horodatés (`installateur\signer.ps1`).

Sans installateur, depuis ce dossier : `INSTALLER_LE_CLAVIER.bat` installe la même chose, avec le moteur lancé par Python (`LANCER_CLAVIER.bat`).

---

## ✍️ Utilisation, comme sous Windows 11

Écrivez dans n'importe quelle application (Word, Bloc-notes, Chrome, WhatsApp, Telegram…) avec votre clavier habituel, Français ou Anglais : le moteur place lui-même les lettres pulaar (voir « Les touches » plus bas).

- **Suggestions de texte** : une bulle apparaît au-dessus du curseur. Elle propose le mot en cours, puis, après une espace, le mot suivant. Quand deux mots vont presque toujours ensemble, elle les propose d'un bloc (*hol ko*, *hay so*, *no feewi*).
  - **Sans la souris** : **← →** surlignent une suggestion, **Tab** ou **Entrée** la prennent. La première est surlignée d'office : **Tab** seul la prend, au milieu d'un mot comme après une espace. Un **clic** ou **Alt + 1, 2, 3** marchent aussi.
  - **Échap** ferme la bulle jusqu'au mot suivant. Pour déplacer le curseur avec ← → ou faire une vraie tabulation pendant que la bulle est ouverte : Échap d'abord. Les flèches peuvent aussi être laissées au texte : interrupteur « Choisir les suggestions avec les flèches » dans les paramètres.
  - Pas besoin des lettres à crochet pour chercher : `fulb` propose `fulɓe`, `bern` propose `ɓernde`, et `jaraam` propose `jaaraama` malgré la faute.
- **Correction automatique** : à l'espace ou à la ponctuation, un mot inconnu tout proche d'un mot courant est corrigé (`fulbe` → `fulɓe`, `be` → `ɓe`, `jaraama` → `jaaraama`, `yidi` → `yiɗi`). **Retour arrière juste après** annule la correction, et le mot est ensuite respecté.
- **Mots retenus** : les mots que vous écrivez passent en tête des suggestions, même après un redémarrage.

### Soulignement des fautes (correcteur de Windows)

L'installateur enregistre aussi un **correcteur orthographique pulaar** auprès de Windows (`correcteur_pulaar\correcteur_pulaar.dll`). Les applications qui se servent du correcteur de Windows soulignent alors en rouge les mots pulaar mal écrits, et le clic droit propose la correction (`fulbe` → `fulɓe`, `jaraama` → `jaaraama`, `miido` → `miɗo`).
- **Microsoft Edge** et **Google Chrome** : ajoutez la langue Fulfulde (Pulaar, code `ff`) dans **Paramètres > Langues**, puis activez la vérification orthographique pour cette langue.
- Word et LibreOffice ont leur propre correcteur et ne l'utilisent pas.

Pour recompiler la DLL (chaîne Rust GNU, sans Visual Studio) :

```bash
cd correcteur_pulaar
cargo +stable-x86_64-pc-windows-gnu build --release
cargo +stable-x86_64-pc-windows-gnu run --release --example verifie
```

La seconde commande vérifie le correcteur en passant par le service de Windows, comme le font Edge ou Chrome.

### Paramètres

Cliquez sur l'icône **ɓ** près de l'horloge. Une fenêtre semblable à la page « Saisie » de Windows s'ouvre, avec des interrupteurs pour :
- écrire en pulaar avec tous les claviers (activé d'office) : désactivé, le clavier se met en pause et Français ou Anglais restent intacts, pour écrire en français ;
- les suggestions de texte, et leur choix avec les flèches ;
- la correction automatique ;
- les mots retenus ;
- le démarrage avec Windows.

Un clic droit sur l'icône donne les mêmes interrupteurs et permet de **Quitter**. Tout est rangé dans `%APPDATA%\ClavierPulaar` :
- `parametres.json` : les réglages ;
- `mots_appris.json` : les mots retenus ;
- `journal.txt` : les messages du moteur, jamais le texte tapé (claviers rencontrés, erreurs, crochet clavier reposé).

Pour relancer le moteur à la main : **`LANCER_CLAVIER.bat`** (sans fenêtre noire).

---

## ⌨️ Les touches

Avec votre clavier habituel, AZERTY (Français) comme QWERTY (Anglais), le moteur place les lettres pulaar :

| Touche | Seule | Maj | AltGr |
|---|---|---|---|
| `v` | **ɓ** | **Ɓ** | v |
| `z` | **ɗ** | **Ɗ** | z |
| `q` | **ŋ** | **Ŋ** | q |
| `x` | **ƴ** | **Ƴ** | x |
| à droite de P (`^` ou `[`) | **ñ** | **Ñ** | ^ ou [ |
| `²` (AZERTY) ou `'` (QWERTY) | **’** (hamza) | | |
| `b`, `d`, `n`, `y` | | | **ɓ**, **ɗ**, **ŋ**, **ƴ** |
| `a`, `e`, `u`, `i`, `o` | | | **á**, **é**, **ú**, **í**, **ó** |

AltGr ne remplace que ce que Windows laisse vide : AltGr + E reste € en français. Ctrl et Alt gardent leurs raccourcis (Ctrl + V colle, Alt + F ouvre le menu).

Pour écrire en français : clic droit sur l'icône **ɓ**, puis décochez « Écrire en pulaar avec tous les claviers ». Si FUL (Pulaar) figure dans votre liste Win + Espace avec un clavier de Windows, le moteur agit aussi quand vous le choisissez, même en pause.

**Ctrl + Shift + A** active ou désactive les suggestions.

`generate_klc.py` et `installateur\compiler_dispositions.ps1` fabriquent encore les dispositions Windows `fulffaz.dll` et `fulffqw.dll` (Microsoft Keyboard Layout Creator), mais l'installateur ne les inscrit plus dans Windows : le sélecteur Win + Espace plantait sur elles.

---

## 📚 Le dictionnaire (uniquement du pulaar)

```bash
python construire_dictionnaire.py
```

Le script lit :
- les lexiques du clavier mobile (`Desktop\fulfuldekey\app\src\main\assets\dict`) ;
- les suites de mots comptées du corpus Tappirgal (`Desktop\donnee tappirgal\preprocessed\bigrams.json`) ;
- l'ancien dictionnaire (`sources_dictionnaire\ancien_dict_ff_latin.json`), pour les formules et les mots courants.

Il écarte :
- les formes de `listes_mots\2_mots_rejetes.txt` ;
- ce qui n'est pas du pulaar : lettres absentes de l'alphabet (q, v, x, z, voyelles accentuées), mots plus fréquents en français ou en anglais, syllabes impossibles en pulaar (swahili, bambara, noms étrangers, pulaar écrit « ny » au lieu de « ñ »).

Il applique `listes_mots\3_lectures_corrigees.txt` (`mido` → `miɗo`), puis écrit `dictionary\dict_ff_latin.json` : environ 118 000 mots, 64 000 mots avec leurs suites et 1 700 groupes de deux mots. Il remplace `importer_donnees_tappirgal.py`.

Pour ajouter vos propres textes : **`IMPORTER_CORPUS.bat`**, ou déposez des `.txt` dans `corpus\`.

---

## 🧪 Vérifications

```bash
python test_autocompletion.py
```

---

## 🖥️ Clavier virtuel (Tauri / React)

```bash
npm run build
npm run preview
```

---

## 📖 Sources des données

Le dictionnaire (`dictionary\dict_ff_latin.json`) est tiré de deux sources :
- **les lexiques du clavier mobile Tappirgal Pulaar**, eux-mêmes construits à partir de :
  - *Saggitorde* de Ceerno Abuu Sih ;
  - ARPRIM `pulaar_fulfulde` et `Pulaar_Dictionary` (HuggingFace, **CC-BY-4.0**) ;
  - pulaar.org et goomufulo.com ;
- **le corpus Tappirgal** : livres pulaar numérisés, Wikipédia en fulfulde, pulaar.org, RFI Fulfulde. Seuls des comptes de mots et de suites de mots en sont tirés, jamais de texte.

---

## Code signing policy

*Politique de signature de code.*

Free code signing provided by [SignPath.io](https://about.signpath.io/), certificate by [SignPath Foundation](https://signpath.org/).

- **Committers and reviewers** (auteurs et relecteurs) : [leonbathie](https://github.com/leonbathie), members of this repository with write access.
- **Approvers** (approbateurs) : [leonbathie](https://github.com/leonbathie).

Only the files built by GitHub Actions from this repository (`.github/workflows/installateur.yml`) are signed: `ClavierPulaar.exe`, `correcteur_pulaar.dll` and `Setup_Clavier_Pulaar.exe`. Every signing request is approved by hand. The keyboard layout files `fulffaz.dll` and `fulffqw.dll`, built from `fulffaz.klc` and `fulffqw.klc` with Microsoft Keyboard Layout Creator, are shipped unsigned inside the installer.

Seuls les fichiers fabriqués par GitHub Actions à partir de ce dépôt sont signés, et chaque signature est approuvée à la main. Les dispositions de clavier `fulffaz.dll` et `fulffqw.dll` sont livrées sans signature dans l'installateur.

### Privacy policy

*Vie privée.*

This program will not transfer any information to other networked systems unless specifically requested by the user or the person installing or operating it. The words it learns stay on the computer (`%APPDATA%\ClavierPulaar`).

Ce programme ne transmet aucune information à d'autres systèmes en réseau, sauf demande expresse de l'utilisateur. Les mots qu'il retient restent sur l'ordinateur.

---

## 📄 Licence

Code distribué sous licence **MIT**. Les données du dictionnaire suivent les licences de leurs sources ci-dessus (CC-BY-4.0 pour ARPRIM : citer ses auteurs en cas de réutilisation).
