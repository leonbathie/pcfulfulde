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
- **Propriétés** : catégorie *Utilitaires et outils* (ou *Productivité*). Politique de confidentialité : `https://leonbathie.github.io/pcfulfulde/privacy.html`. Dans **Support info**, cocher **Use different details for this app**, puis : site web `https://leonbathie.github.io/pcfulfulde/`, contact d'assistance `https://github.com/leonbathie/pcfulfulde/issues`. Le rapport de certification du 30/09/2026 réclamait ce contact.
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
> Au premier lancement, le bouton « Ajouter FUL à Win + Espace » ajoute la langue pulaar avec votre clavier Français (AZERTY) ou Anglais (QWERTY) de Windows. Tout reste sur votre ordinateur : rien n'est envoyé sur Internet.

### Fonctionnalités (une par ligne)

- Lettres pulaar ɓ ɗ ŋ ƴ ñ sur un clavier AZERTY ou QWERTY
- Suggestions de mots pulaar au-dessus du curseur, choisies avec Tab ou les flèches
- Correction automatique des fautes, annulée par Retour arrière
- Correcteur orthographique pulaar pour Edge et Chrome
- Français et Anglais inchangés
- Aucune donnée envoyée sur Internet

### Mots-clés

`pulaar`, `fulfulde`, `fula`, `clavier`, `keyboard`, `Sénégal`, `ɓ ɗ ŋ ƴ`

## 4. Capacité restreinte : texte à coller (en anglais, pour l'équipe de certification)

Le paquet ne déclare qu'une capacité restreinte, **runFullTrust**, à justifier dans la page **Submission options** (500 caractères au plus ; ce texte en fait 468) :

> **runFullTrust**: Fulfulde Keyboard is a Win32 desktop keyboard helper for the Pulaar (Fulfulde) language. It needs full trust for a low-level keyboard hook and SendInput, to type the Pulaar letters (ɓ ɗ ŋ ƴ ñ) and insert the word suggestions the user picks, plus a suggestion window, a tray icon and a startup task. It acts only while the user has selected the Fulfulde (FUL) input language. Keystrokes are processed locally, never stored or sent; the app makes no network connections.

La version 2.6.2 demandait aussi **unvirtualizedResources**, refusée le 30/09/2026 (politique 10.6.3). Depuis la 2.6.3, le programme est déclaré `win32App` dans le manifeste : Windows ne virtualise pas ses écritures, et « Ajouter FUL à Win + Espace » marche sans cette capacité (vérifié avec un paquet d'essai : registre HKCU, processus enfants et AppData arrivent tous au vrai emplacement).

### Notes pour la certification (en anglais)

Dans **Submission options > Notes for certification** (822 caractères). Les rapports du 01/10/2026 (10.1.2.10, « Text suggestions », puis « Provide suggestions for letter changes ») venaient de FUL (Français, AZERTY) sur le clavier QWERTY d'un Surface Laptop : « jaa » y devenait « jŋŋ ». Depuis la 2.6.5, FUL prend les claviers de l'utilisateur (Anglais seul sur un Windows anglais), et les notes font taper « hol » et « fulb », pareils en AZERTY et en QWERTY.

```
HOW TO TEST TEXT SUGGESTIONS. They only appear while the Pulaar input language (FUL) is selected; with English or any other input language, the app intentionally changes nothing.
1. Launch Fulfulde Keyboard from Start. Its settings window opens (in English on an English Windows; the app also has a ɓ icon in the notification area).
2. Click "Add FUL to Win + Space" and wait for the "Done." message (a few seconds). On an English Windows, FUL gets the US keyboard.
3. Open Notepad and click in the text area.
4. Press Win + Space and select FUL (Fulah/Pulaar).
5. Type hol: a bubble with Pulaar words (holi, holi ko, holli) appears above the cursor. Press Tab: the highlighted word is inserted.
6. Type fulb: the bubble suggests fulɓe. Type fulbe then Space: it is corrected to fulɓe. The keys v, z, q, x type ɓ, ɗ, ŋ, ƴ.
```

## Après l'installation depuis le Store

- Désinstaller l'application ne retire pas FUL de Win + Espace, ni le correcteur. Windows ne le permet pas à un paquet du Store. On retire FUL dans **Paramètres > Heure et langue > Langue et région**.
- Le démarrage avec Windows se règle dans **Paramètres > Applications > Démarrage**.
