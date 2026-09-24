# Clavier Pulaar (Fulfulde) pour Windows

> Un clavier pulaar qui se comporte comme ceux de Microsoft : il se choisit avec **Win + Espace**, propose des mots pulaar au-dessus du curseur, corrige les fautes à l'espace et retient vos mots. Uniquement du pulaar : avec le clavier Français ou Anglais, il se tait.

---

## 🚀 Installation (une fois)

1. Double-cliquez sur **`INSTALLER_LE_CLAVIER.bat`** et répondez **Oui** quand Windows demande l'autorisation.
2. Appuyez sur **Win + Espace** : la langue peule apparaît avec **Pulaar (Fulfulde) AZERTY** et **Pulaar (Fulfulde) QWERTY**, à côté de Français et Anglais.
3. Le moteur de suggestions démarre aussitôt, puis à chaque ouverture de session. Son icône **ɓ** se trouve près de l'horloge.

Le script `installer_clavier_pulaar.ps1` fait tout cela :
- il enregistre `fulffaz.dll` comme **disposition principale de la langue peule** (`00000867`), comme Microsoft le fait pour ses langues, et `fulffqw.dll` en variante, avec un *Layout Id* libre (l'ancien `00a1` était déjà celui du clavier lituanien). Windows ne livre aucun clavier `00000867` : inscrit seulement en variante, le premier clavier Pulaar renvoyait à une disposition absente, et le sélecteur Win + Espace faisait planter l'Explorateur ;
- il rend à Windows sa disposition Wolof, que les anciens installateurs avaient remplacée ;
- il inscrit le clavier dans **Paramètres > Applications > Applications installées**.

Pour tout retirer : **Paramètres > Applications**, ou `desinstaller_clavier_pulaar.ps1`.

> `Setup_Clavier_Fulfulde.exe` est l'ancien installateur : ne l'utilisez plus. Il remplaçait la disposition Wolof de Windows et réutilisait un *Layout Id* déjà pris.

---

## ✍️ Utilisation, comme sous Windows 11

Choisissez **Pulaar** avec Win + Espace, puis écrivez dans n'importe quelle application (Word, Bloc-notes, Chrome, WhatsApp…).

- **Suggestions de texte** : une bulle apparaît au-dessus du curseur. Elle propose le mot en cours, puis, après une espace, le mot suivant. Quand deux mots vont presque toujours ensemble, elle les propose d'un bloc (*hol ko*, *hay so*, *no feewi*).
  - **Choisir** : un **clic** ; **TAB** pour la 1re suggestion d'un mot commencé ; **Alt + 1, 2, 3** ; ou **Flèche haut**, puis **← →** et **Entrée**.
  - **Échap** ferme la bulle jusqu'au mot suivant.
  - Pas besoin des lettres à crochet pour chercher : `fulb` propose `fulɓe`, `bern` propose `ɓernde`, et `jaraam` propose `jaaraama` malgré la faute.
- **Correction automatique** : à l'espace ou à la ponctuation, un mot inconnu tout proche d'un mot courant est corrigé (`fulbe` → `fulɓe`, `be` → `ɓe`, `jaraama` → `jaaraama`, `yidi` → `yiɗi`). **Retour arrière juste après** annule la correction, et le mot est ensuite respecté.
- **Mots retenus** : les mots que vous écrivez passent en tête des suggestions, même après un redémarrage.

### Soulignement des fautes (correcteur de Windows)

L'installateur enregistre aussi un **correcteur orthographique pulaar** auprès de Windows (`correcteur_pulaar\correcteur_pulaar.dll`). Les applications qui se servent du correcteur de Windows soulignent alors en rouge les mots pulaar mal écrits, et le clic droit propose la correction (`fulbe` → `fulɓe`, `jaraama` → `jaaraama`, `miido` → `miɗo`).
- **Microsoft Edge** et **Google Chrome** : ajoutez « Peul » dans **Paramètres > Langues**, puis activez la vérification orthographique pour cette langue.
- Les autres applications le font lorsqu'elles vérifient l'orthographe dans la langue du clavier choisi.
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
- les suggestions de texte ;
- la correction automatique ;
- les mots retenus ;
- le démarrage avec Windows.

Un clic droit sur l'icône permet de **Quitter**. Tout est rangé dans `%APPDATA%\ClavierPulaar` :
- `parametres.json` : les réglages ;
- `mots_appris.json` : les mots retenus ;
- `journal.txt` : les messages du moteur.

Pour relancer le moteur à la main : **`LANCER_CLAVIER.bat`** (sans fenêtre noire).

---

## ⌨️ Les touches

### Pulaar (Fulfulde) AZERTY
| Touche | Seule | Maj | AltGr |
|---|---|---|---|
| `v` | **ɓ** | **Ɓ** | v |
| `z` | **ɗ** | **Ɗ** | z |
| `q` | **ŋ** | **Ŋ** | q |
| `x` | **ƴ** | **Ƴ** | x |
| `^` (à droite de P) | **ñ** | **Ñ** | ^ |
| `²` | ² | **’** (hamza) | |
| `b`, `d`, `n` | b, d, n | | **ɓ**, **ɗ**, **ŋ** |
| `a`, `u`, `i`, `o` | | | **á**, **ú**, **í**, **ó** |

### Pulaar (Fulfulde) QWERTY
| Touche | Seule | Maj | AltGr |
|---|---|---|---|
| `[` | **ɓ** | **Ɓ** | [ |
| `]` | **ɗ** | **Ɗ** | ] |
| `;` | **ŋ** | **Ŋ** | ; |
| `q` | **ƴ** | **Ƴ** | q |
| `'` | **’** (hamza) | " | ' |
| `b`, `d`, `n`, `y` | | | **ɓ**, **ɗ**, **ŋ**, **ƴ** |
| `a`, `e`, `u`, `i`, `o` | | | **á**, **é**, **ú**, **í**, **ó** |

Sans le clavier Pulaar de Windows, le moteur peut encore remplacer les touches lui-même (interrupteur « Remplacer les touches sans le clavier Pulaar de Windows »). C'est l'ancien mode : **Ctrl + Shift + L** y bascule entre AZERTY et QWERTY.

**Ctrl + Shift + A** active ou désactive les suggestions.

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
- ce qui n'est pas du pulaar : lettres absentes de l'alphabet (q, v, x, z, voyelles accentuées), mots plus fréquents en français ou en anglais, syllabes impossibles en pulaar (swahili, bambara, noms étrangers, peul écrit « ny » au lieu de « ñ »).

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
- **le corpus Tappirgal** : livres pulaar numérisés, Wikipédia en peul, pulaar.org, RFI Fulfulde. Seuls des comptes de mots et de suites de mots en sont tirés, jamais de texte.

---

## 📄 Licence

Code distribué sous licence **MIT**. Les données du dictionnaire suivent les licences de leurs sources ci-dessus (CC-BY-4.0 pour ARPRIM : citer ses auteurs en cas de réutilisation).
