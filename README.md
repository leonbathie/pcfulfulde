# Fulfulde Keyboard pour Windows

> **Fulfulde Keyboard** (éditeur : Taro Learning), un clavier pulaar qui se comporte comme ceux de Microsoft : il se choisit avec **Win + Espace** (FUL), donne les lettres pulaar (v → ɓ, z → ɗ, q → ŋ, x → ƴ), propose des mots pulaar au-dessus du curseur, corrige les fautes à l'espace et retient vos mots. Avec Français ou Anglais, rien ne change. Uniquement des mots pulaar.

---

## Download

*Télécharger.* Les versions sont publiées dans **[Releases](https://github.com/leonbathie/pcfulfulde/releases)** : téléchargez `Fulfulde_Keyboard.exe`. Les installateurs signés le sont par SignPath Foundation : free code signing provided by [SignPath.io](https://about.signpath.io/), certificate by [SignPath Foundation](https://signpath.org/) (voir [Code signing policy](#code-signing-policy)).

---

## 🚀 Installation (une fois)

1. Lancez **`Fulfulde_Keyboard.exe`**, choisissez la langue de l'assistant (30 langues, celle de Windows proposée d'office), suivez-le et répondez **Oui** quand Windows demande l'autorisation. Python n'est pas nécessaire : le clavier est installé dans `C:\Program Files\Fulfulde Keyboard`. Une version précédente (« Clavier Pulaar ») est remplacée, avec ses réglages et vos mots retenus.
2. Appuyez sur **Win + Espace** : **FUL** apparaît à côté de FRA et ENG, deux fois, avec le clavier Français (AZERTY) et avec le clavier Anglais (QWERTY) de Windows. Choisissez celui qui correspond à votre clavier.
3. Le clavier démarre aussitôt, puis à chaque ouverture de session. Son icône **ɓ** se trouve près de l'horloge.

Pour tout retirer : **Paramètres > Applications > Fulfulde Keyboard > Désinstaller**.

L'assistant lance `installer_clavier_pulaar.ps1`, en trois parties :
- les claviers « Pulaar (Fulfulde) AZERTY / QWERTY » des versions précédentes quittent d'abord la liste Win + Espace. Le sélecteur Win + Espace de Windows 11 (`InputSwitch.dll`) plantait sur eux et emportait l'Explorateur : depuis la version 24H2, il ne connaît que les dispositions de Windows ;
- (administrateur) leurs dispositions (`00000867`, `a0010867`) et leurs fichiers (`fulffaz.dll`, `fulffqw.dll`) sont effacés, et la disposition Wolof de Windows, que les anciens installateurs avaient remplacée, est rendue ;
- FUL (Pulaar, `ff-Latn-SN`) revient dans Win + Espace avec les claviers Français et Anglais de Windows ; c'est le moteur qui place les lettres pulaar. Le correcteur orthographique est enregistré et le clavier démarre avec Windows.

> `Setup_Clavier_Fulfulde.exe` est l'**ancien** installateur : ne l'utilisez plus. Il remplaçait la disposition Wolof de Windows et réutilisait un *Layout Id* déjà pris, ce qui faisait planter Win + Espace.

### Fabriquer l'installateur

```powershell
powershell -ExecutionPolicy Bypass -File installateur\fabriquer_installateur.ps1
```

Le script transforme le clavier en `FulfuldeKeyboard.exe` avec PyInstaller, puis produit `Fulfulde_Keyboard.exe` avec Inno Setup 6 (`installateur\clavier_pulaar.iss`). Il faut Python avec `pynput` et `pyinstaller`, et Inno Setup 6.

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

`FulfuldeKeyboard.exe`, l'installateur et son désinstalleur sont alors signés et horodatés (`installateur\signer.ps1`).

Sans installateur, depuis ce dossier : `INSTALLER_LE_CLAVIER.bat` installe la même chose, avec le moteur lancé par Python (`LANCER_CLAVIER.bat`).

### Microsoft Store

`installateur\fabriquer_msix.ps1` fabrique le paquet MSIX du Store, que Microsoft signe lui-même. Le programme y ajoute FUL à Win + Espace depuis sa fenêtre de paramètres, au premier lancement. Les étapes de publication, et les textes à coller dans l'Espace partenaires : [installateur/msix/MICROSOFT_STORE.md](installateur/msix/MICROSOFT_STORE.md).

---

## ✍️ Utilisation, comme sous Windows 11

Choisissez **FUL (Pulaar)** avec Win + Espace, puis écrivez dans n'importe quelle application (Word, Bloc-notes, Chrome, WhatsApp, Telegram…) : le moteur place les lettres pulaar (voir « Les touches » plus bas). Avec Français ou Anglais, votre clavier ne change pas.

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

Cliquez sur l'icône **ɓ** près de l'horloge. Une fenêtre semblable à la page « Saisie » de Windows s'ouvre ; elle rappelle en tête qu'il faut choisir FUL avec Win + Espace. Elle est en français si Windows l'est, en anglais sinon (comme le menu de l'icône). Elle a des interrupteurs pour :
- les suggestions de texte, et leur choix avec les flèches ;
- la correction automatique ;
- les mots retenus ;
- le démarrage avec Windows.

Un clic droit sur l'icône donne les mêmes interrupteurs et permet de **Quitter**. Tout est rangé dans `%APPDATA%\FulfuldeKeyboard` :
- `parametres.json` : les réglages ;
- `mots_appris.json` : les mots retenus ;
- `journal.txt` : les messages du moteur, jamais le texte tapé (claviers rencontrés, erreurs, crochet clavier reposé).

Pour relancer le moteur à la main : **`LANCER_CLAVIER.bat`** (sans fenêtre noire).

---

## ⌨️ Les touches

Quand **FUL (Pulaar)** est choisi dans Win + Espace, le moteur place les lettres pulaar, sur les mêmes touches en AZERTY et en QWERTY :

| Touche | Seule | Maj | AltGr |
|---|---|---|---|
| `v` | **ɓ** | **Ɓ** | v |
| `z` | **ɗ** | **Ɗ** | z |
| `q` | **ŋ** | **Ŋ** | q |
| `x` | **ƴ** | **Ƴ** | x |
| à droite de P (`^` ou `[`) | **ñ** | **Ñ** | ^ ou [ |
| `²` (AZERTY) | ² | **’** (hamza) | |
| `'` (QWERTY) | **’** (hamza) | " | ' |
| `b`, `d`, `n`, `y` | | | **ɓ**, **ɗ**, **ŋ**, **ƴ** |
| `a`, `e`, `u`, `i`, `o` | | | **á**, **é**, **ú**, **í**, **ó** |

AltGr ne remplace que ce que Windows laisse vide : AltGr + E reste € en français. Ctrl et Alt gardent leurs raccourcis (Ctrl + V colle, Alt + F ouvre le menu).

Avec Français ou Anglais, les touches restent toujours celles de Windows (v donne v) : aucun réglage n'y met les lettres pulaar.

**Ctrl + Shift + A** active ou désactive les suggestions.

Dans Win + Espace, FUL utilise les claviers Français et Anglais de Windows. `generate_klc.py` et `installateur\compiler_dispositions.ps1` fabriquent encore les anciennes dispositions `fulffaz.dll` et `fulffqw.dll` (Microsoft Keyboard Layout Creator), mais l'installateur ne les inscrit plus : le sélecteur Win + Espace de Windows 11 plantait sur elles.

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

Only the files built by GitHub Actions from this repository (`.github/workflows/installateur.yml`) are signed: `FulfuldeKeyboard.exe`, `correcteur_pulaar.dll` and `Fulfulde_Keyboard.exe`. Every signing request is approved by hand.

Seuls les fichiers fabriqués par GitHub Actions à partir de ce dépôt sont signés, et chaque signature est approuvée à la main.

### Privacy policy

*Vie privée.*

This program will not transfer any information to other networked systems unless specifically requested by the user or the person installing or operating it. The words it learns stay on the computer (`%APPDATA%\FulfuldeKeyboard`).

Ce programme ne transmet aucune information à d'autres systèmes en réseau, sauf demande expresse de l'utilisateur. Les mots qu'il retient restent sur l'ordinateur.

Full policy / politique complète : https://leonbathie.github.io/pcfulfulde/privacy.html

---

## 📄 Licence

Code distribué sous licence **MIT**. Les données du dictionnaire suivent les licences de leurs sources ci-dessus (CC-BY-4.0 pour ARPRIM : citer ses auteurs en cas de réutilisation).
