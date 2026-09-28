# Publier Fulfulde Keyboard dans le Microsoft Store

Le Store reçoit un paquet **MSIX** et le signe lui-même : aucun certificat à acheter. Le paquet contient le même programme que l'installateur `Fulfulde_Keyboard.exe`.

## 1. Réserver le nom et relever l'identité du produit

C'est fait. Le nom est réservé, avec l'identifiant Store `9PP6JXXL9HS4` : la page sera https://apps.microsoft.com/detail/9PP6JXXL9HS4 une fois l'application publiée. L'identité est `TaroLearning.FulfuldeKeyboard`, l'éditeur `CN=CFD237ED-B8B2-44F1-9175-9C8D66388F0B`, le nom affiché **Taro Learning**. Ce sont les valeurs par défaut du script.

Pour mémoire, dans l'[Espace partenaires](https://partner.microsoft.com/dashboard/apps-and-games/overview) : **Applications et jeux > Nouveau produit > Application MSIX ou PWA**, nom **Fulfulde Keyboard**.

Puis **Gestion du produit > Identité du produit** donne trois valeurs :

| Dans l'Espace partenaires | Option du script |
|---|---|
| `Package/Identity/Name` | `-Nom` |
| `Package/Identity/Publisher` (commence par `CN=`) | `-Editeur` |
| `Package/Properties/PublisherDisplayName` (Taro Learning) | `-EditeurAffiche` |

## 2. Fabriquer le paquet

```powershell
powershell -ExecutionPolicy Bypass -File installateur\fabriquer_msix.ps1
```

Le paquet à envoyer : `construction\msix\FulfuldeKeyboard_<version>_x64.msix`. Pour chaque nouvelle version, augmenter `#define Version` dans `installateur\clavier_pulaar.iss`.

Pour l'essayer sur un PC avant l'envoi : ajouter `-Essai`, puis suivre les deux commandes affichées à la fin (certificat d'essai, puis `Add-AppxPackage`). Retirer ensuite la version d'essai avant d'installer celle du Store :

```powershell
Get-AppxPackage *.FulfuldeKeyboard | Remove-AppxPackage
```

## 3. Soumission

- **Tarification et disponibilité** : gratuit, tous les marchés.
- **Propriétés** : catégorie *Utilitaires et outils* (ou *Productivité*). Politique de confidentialité : `https://leonbathie.github.io/pcfulfulde/privacy.html`. Site web : `https://leonbathie.github.io/pcfulfulde/`. Assistance : `https://github.com/leonbathie/pcfulfulde/issues`.
- **Classification par âge** : questionnaire ; aucune violence, aucun achat, aucun échange entre utilisateurs.
- **Packages** : déposer le `.msix`.
- **Description dans le Store (français)** : le texte ci-dessous, et au moins une capture d'écran de 1366 × 768 ou plus (la bulle de suggestions dans Word ou le Bloc-notes, la fenêtre de paramètres).

### Description

> Fulfulde Keyboard est un clavier pulaar (fulfulde) pour Windows.
>
> Choisissez FUL avec Win + Espace : les touches donnent les lettres pulaar (v → ɓ, z → ɗ, q → ŋ, x → ƴ, ^ ou [ → ñ). Une bulle propose des mots pulaar au-dessus du curseur : Tab prend la suggestion, ← → en choisissent une autre. Les fautes sont corrigées à l'espace (fulbe → fulɓe) et les mots que vous écrivez sont retenus.
>
> Avec Français ou Anglais, votre clavier ne change pas. Fonctionne dans Word, Chrome, Edge, WhatsApp, Telegram, le Bloc-notes… Le correcteur orthographique pulaar souligne les fautes dans Edge et Chrome.
>
> Au premier lancement, le bouton « Ajouter FUL à Win + Espace » ajoute la langue pulaar avec les claviers Français (AZERTY) et Anglais (QWERTY) de Windows. Tout reste sur votre ordinateur : rien n'est envoyé sur Internet.

### Fonctionnalités (une par ligne)

- Lettres pulaar ɓ ɗ ŋ ƴ ñ sur un clavier AZERTY ou QWERTY
- Suggestions de mots pulaar au-dessus du curseur, choisies avec Tab ou les flèches
- Correction automatique des fautes, annulée par Retour arrière
- Correcteur orthographique pulaar pour Edge et Chrome
- Français et Anglais inchangés
- Aucune donnée envoyée sur Internet

### Mots-clés

`pulaar`, `fulfulde`, `fula`, `clavier`, `keyboard`, `Sénégal`, `ɓ ɗ ŋ ƴ`

## 4. Capacités restreintes : texte à coller (en anglais, pour l'équipe de certification)

Le paquet déclare deux capacités restreintes, que Microsoft demande de justifier, dans la page **Submission options**. Chaque case accepte 500 caractères au plus : ces textes en font 468 et 480.

> **runFullTrust**: Fulfulde Keyboard is a Win32 desktop keyboard helper for the Pulaar (Fulfulde) language. It needs full trust for a low-level keyboard hook and SendInput, to type the Pulaar letters (ɓ ɗ ŋ ƴ ñ) and insert the word suggestions the user picks, plus a suggestion window, a tray icon and a startup task. It acts only while the user has selected the Fulfulde (FUL) input language. Keystrokes are processed locally, never stored or sent; the app makes no network connections.
>
> **unvirtualizedResources**: At the user's request (a link in the app's settings), the app adds the Fulfulde (ff-Latn-SN) input language, with the built-in French and US keyboards, to the user's Windows language list so FUL appears in Win + Space, and registers a Pulaar spell checker for other apps (Edge, Chrome). These per-user settings must be visible to Windows, so only HKCU Control Panel\International, Keyboard Layout, Software\Microsoft\CTF, Input, Spelling and the checker's CLSID are unvirtualized.

### Notes pour la certification (en anglais)

> To test: launch Fulfulde Keyboard; its settings window opens. Click "Ajouter FUL à Win + Espace". Press Win + Space and choose FUL (French keyboard). In Notepad, type "fulbe " (with the space): it becomes "fulɓe". Type "jaa": a suggestion bubble appears above the cursor; press Tab to take it. With FRA or ENG selected, the keyboard is unchanged.

## Après l'installation depuis le Store

- Désinstaller l'application ne retire pas FUL de Win + Espace, ni le correcteur. Windows ne le permet pas à un paquet du Store. On retire FUL dans **Paramètres > Heure et langue > Langue et région**.
- Le démarrage avec Windows se règle dans **Paramètres > Applications > Démarrage**.
