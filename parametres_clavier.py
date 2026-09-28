#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Réglages de Fulfulde Keyboard, présentés comme la page « Saisie » des
paramètres de Windows 11, et ce que le clavier retient d'une session à l'autre.

Tout est rangé dans %APPDATA%\\FulfuldeKeyboard :
- parametres.json  : les interrupteurs de la fenêtre de réglages ;
- mots_appris.json : les mots que l'on écrit, proposés en premier ;
- journal.txt      : les messages du moteur quand il tourne sans console.
"""

import os
import sys
import json
import shutil
import ctypes
import threading
import subprocess
import tkinter as tk
import tkinter.font as tkfont

try:
    import winreg
except ImportError:  # hors Windows
    winreg = None

NOM = "Fulfulde Keyboard"
_APPDATA = os.environ.get("APPDATA") or os.path.expanduser("~")
DOSSIER = os.path.join(_APPDATA, "FulfuldeKeyboard")
# Le dossier des versions 2.4.1 et avant, quand le clavier s'appelait « Clavier Pulaar »
ANCIEN_DOSSIER = os.path.join(_APPDATA, "ClavierPulaar")
FICHIER_PARAMETRES = os.path.join(DOSSIER, "parametres.json")
FICHIER_MOTS_APPRIS = os.path.join(DOSSIER, "mots_appris.json")
FICHIER_JOURNAL = os.path.join(DOSSIER, "journal.txt")
ICONE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icones", "clavier_pulaar.ico")

CLE_DEMARRAGE = r"Software\Microsoft\Windows\CurrentVersion\Run"
NOM_DEMARRAGE = "FulfuldeKeyboard"
ANCIEN_NOM_DEMARRAGE = "ClavierPulaar"
CLE_LANGUES = r"Control Panel\International\User Profile"
# Le dossier du programme : à côté de FulfuldeKeyboard.exe (installé, ou dans
# le paquet du Microsoft Store), ou celui des sources.
DOSSIER_PROGRAMME = (os.path.dirname(sys.executable) if getattr(sys, "frozen", False)
                     else os.path.dirname(os.path.abspath(__file__)))
APPMODEL_ERROR_NO_PACKAGE = 15700


def en_paquet():
    """Vrai quand le clavier tourne depuis son paquet du Microsoft Store."""
    if sys.platform != "win32":
        return False
    try:
        taille = ctypes.c_uint32(0)
        return (ctypes.windll.kernel32.GetCurrentPackageFullName(ctypes.byref(taille), None)
                != APPMODEL_ERROR_NO_PACKAGE)
    except AttributeError:  # avant Windows 8
        return False


def ful_dans_win_espace():
    """Vrai si FUL (une langue ff-…) figure dans la liste Win + Espace."""
    if winreg is None:
        return False
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, CLE_LANGUES) as cle:
            langues = winreg.QueryValueEx(cle, "Languages")[0]
    except OSError:
        return False
    return any(langue.lower().startswith("ff") for langue in langues)


def ajoute_ful():
    """Ajoute FUL (Pulaar) à Win + Espace, avec les claviers Français et Anglais
    de Windows, et enregistre le correcteur orthographique : la partie
    utilisateur de l'installateur, sans relancer le moteur. Sert à la version du
    Microsoft Store, qui n'a pas d'installateur. Rend vrai si FUL y est ensuite."""
    script = os.path.join(DOSSIER_PROGRAMME, "installer_clavier_pulaar.ps1")
    if not os.path.exists(script):
        return False
    try:
        subprocess.run(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", script,
                        "-UtilisateurSeulement", "-SansMoteur"],
                       creationflags=0x08000000, timeout=180,  # CREATE_NO_WINDOW
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError) as e:
        print(f"[FUL] {e}", file=sys.stderr)
    return ful_dans_win_espace()


def reprend_ancien_dossier():
    """Les réglages, les mots retenus et le journal de « Clavier Pulaar » passent
    dans le dossier de Fulfulde Keyboard, une fois."""
    if os.path.exists(DOSSIER) or not os.path.isdir(ANCIEN_DOSSIER):
        return
    try:
        os.rename(ANCIEN_DOSSIER, DOSSIER)
    except OSError:
        # Un fichier encore ouvert (l'ancien moteur qui s'arrête) : on copie.
        os.makedirs(DOSSIER, exist_ok=True)
        for nom in ("parametres.json", "mots_appris.json", "journal.txt"):
            try:
                shutil.copy2(os.path.join(ANCIEN_DOSSIER, nom), os.path.join(DOSSIER, nom))
            except OSError:
                pass

PAR_DEFAUT = {
    "suggestions": True,             # la bulle au-dessus du curseur
    "correction_automatique": True,  # fulbe -> fulɓe à l'espace
    "fleches": True,                 # ← → choisissent dans la bulle
    "retenir_les_mots": True,        # mots_appris.json
    "ful_propose": False,            # la fenêtre a déjà proposé d'ajouter FUL à Win + Espace
}

# 4 : le réglage « Écrire en pulaar avec tous les claviers » (sans_disposition)
# n'existe plus : les lettres pulaar seulement quand FUL est choisi dans
# Win + Espace, Français et Anglais toujours intacts. Une valeur enregistrée
# par une version précédente est ignorée (seules les clés de PAR_DEFAUT sont lues).
VERSION_PARAMETRES = 4


def _ecrit_json(chemin, donnees):
    os.makedirs(DOSSIER, exist_ok=True)
    provisoire = chemin + ".tmp"
    with open(provisoire, "w", encoding="utf-8") as f:
        json.dump(donnees, f, ensure_ascii=False, indent=1)
    os.replace(provisoire, chemin)


def _lit_json(chemin):
    try:
        with open(chemin, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


class Parametres:
    """Les réglages, relus au démarrage et enregistrés à chaque changement."""

    def __init__(self):
        self.valeurs = dict(PAR_DEFAUT)
        lus = _lit_json(FICHIER_PARAMETRES)
        if isinstance(lus, dict):
            for cle, defaut in PAR_DEFAUT.items():
                if isinstance(lus.get(cle), type(defaut)):
                    self.valeurs[cle] = lus[cle]
            # Le fichier d'une version précédente est réécrit tout de suite : une
            # ancienne version relancée n'y retrouve plus « sans_disposition ».
            if lus.get("version") != VERSION_PARAMETRES or set(lus) - set(PAR_DEFAUT) - {"version"}:
                self._enregistre()

    def __getitem__(self, cle):
        return self.valeurs[cle]

    def __setitem__(self, cle, valeur):
        self.valeurs[cle] = valeur
        self._enregistre()

    def _enregistre(self):
        try:
            _ecrit_json(FICHIER_PARAMETRES, {"version": VERSION_PARAMETRES, **self.valeurs})
        except OSError as e:
            print(f"[parametres] {e}", file=sys.stderr)


def lit_mots_appris():
    donnees = _lit_json(FICHIER_MOTS_APPRIS)
    return donnees if isinstance(donnees, dict) else {}


def ecrit_mots_appris(donnees):
    _ecrit_json(FICHIER_MOTS_APPRIS, donnees)


def oublie_mots_appris():
    try:
        os.remove(FICHIER_MOTS_APPRIS)
    except OSError:
        pass


def commande_de_demarrage():
    """Le clavier démarre sans fenêtre noire : FulfuldeKeyboard.exe une fois installé, pythonw sinon."""
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'
    pythonw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    if not os.path.exists(pythonw):
        pythonw = sys.executable
    script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "clavier_fulfulde_natif.py")
    return f'"{pythonw}" "{script}"'


def demarre_avec_windows():
    if winreg is None:
        return False
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, CLE_DEMARRAGE) as cle:
            winreg.QueryValueEx(cle, NOM_DEMARRAGE)
            return True
    except OSError:
        return False


def regle_demarrage(actif):
    if winreg is None:
        return
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, CLE_DEMARRAGE, 0, winreg.KEY_SET_VALUE) as cle:
        try:
            winreg.DeleteValue(cle, ANCIEN_NOM_DEMARRAGE)
        except FileNotFoundError:
            pass
        if actif:
            winreg.SetValueEx(cle, NOM_DEMARRAGE, 0, winreg.REG_SZ, commande_de_demarrage())
        else:
            try:
                winreg.DeleteValue(cle, NOM_DEMARRAGE)
            except FileNotFoundError:
                pass


def _theme_sombre():
    if winreg is None:
        return False
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize") as cle:
            return winreg.QueryValueEx(cle, "AppsUseLightTheme")[0] == 0
    except OSError:
        return False


# Couleurs de la page « Saisie » des paramètres de Windows 11.
CLAIR = {"fond": "#F3F3F3", "carte": "#FBFBFB", "bord": "#E5E5E5", "texte": "#1A1A1A",
         "detail": "#5F5F5F", "accent": "#005FB8", "eteint": "#6E6E6E", "pastille": "#FFFFFF",
         "lien": "#005FB8", "alerte": "#9D5D00"}
SOMBRE = {"fond": "#202020", "carte": "#2B2B2B", "bord": "#1D1D1D", "texte": "#FFFFFF",
          "detail": "#CFCFCF", "accent": "#4CC2FF", "eteint": "#CFCFCF", "pastille": "#000000",
          "lien": "#4CC2FF", "alerte": "#FCE100"}


# Échelles d'affichage de Windows pour lesquelles l'interrupteur est dessiné
# (icones/fabrique_icone.py fabrique les images).
ECHELLES_INTERRUPTEUR = (100, 125, 150, 175, 200, 250, 300)


def image_interrupteur(theme, actif, echelle):
    """Chemin de l'image d'un interrupteur : theme « clair » ou « sombre »."""
    dossier = os.path.dirname(ICONE)
    return os.path.join(dossier, f"interrupteur_{theme}_{int(actif)}_{echelle}.png")


def _images_interrupteur(theme, facteur):
    """Les deux images (désactivé, activé) de l'interrupteur de Windows 11, à
    l'échelle la plus proche de celle de l'écran. Tk lit le PNG lui-même."""
    echelle = min(ECHELLES_INTERRUPTEUR, key=lambda e: abs(e - facteur * 100))
    return [tk.PhotoImage(file=image_interrupteur(theme, actif, echelle)) for actif in (False, True)]


class Interrupteur:
    """Un interrupteur « Activé / Désactivé », comme dans les paramètres de Windows."""

    def __init__(self, parent, couleurs, police, images, valeur, sur_changement):
        self.images = images
        self.valeur = valeur
        self.sur_changement = sur_changement
        self.etat = tk.Label(parent, font=police, bg=couleurs["carte"], fg=couleurs["texte"])
        if images:
            self.bouton = tk.Label(parent, bg=couleurs["carte"], cursor="hand2")
        else:  # sans Pillow : une simple case à cocher
            self.var = tk.BooleanVar(value=valeur)
            self.bouton = tk.Checkbutton(parent, variable=self.var, bg=couleurs["carte"],
                                         activebackground=couleurs["carte"], command=self._bascule)
        self.bouton.pack(side="right", padx=(10, 18))
        self.etat.pack(side="right")
        for w in (self.bouton, self.etat):
            if images:
                w.bind("<Button-1>", lambda _e: self._bascule())
        self._dessine()

    def _dessine(self):
        self.etat.configure(text="Activé" if self.valeur else "Désactivé")
        if self.images:
            self.bouton.configure(image=self.images[1 if self.valeur else 0])
        else:
            self.var.set(self.valeur)

    def _bascule(self):
        self.valeur = not self.valeur
        self._dessine()
        self.sur_changement(self.valeur)

    def regle(self, valeur):
        if valeur != self.valeur:
            self.valeur = valeur
            self._dessine()


class FenetreParametres:
    """La fenêtre « Fulfulde Keyboard — Paramètres ». Une seule à la fois."""

    ouverte = None

    @classmethod
    def ouvre(cls, root, moteur):
        if cls.ouverte is not None:
            cls.ouverte.fenetre.deiconify()
            cls.ouverte.fenetre.lift()
            cls.ouverte.fenetre.focus_force()
            return cls.ouverte
        cls.ouverte = cls(root, moteur)
        return cls.ouverte

    def __init__(self, root, moteur):
        self.moteur = moteur
        c = self.couleurs = SOMBRE if _theme_sombre() else CLAIR
        facteur = root.winfo_fpixels("1i") / 96.0

        f = self.fenetre = tk.Toplevel(root)
        f.title(f"{NOM} — Paramètres")
        f.configure(bg=c["fond"])
        f.resizable(False, False)
        f.protocol("WM_DELETE_WINDOW", self.ferme)
        if os.path.exists(ICONE):
            try:
                f.iconbitmap(ICONE)
            except tk.TclError:
                pass

        familles = set(tkfont.families(root))
        famille = "Segoe UI Variable Text" if "Segoe UI Variable Text" in familles else "Segoe UI"
        titre = "Segoe UI Variable Display" if "Segoe UI Variable Display" in familles else famille
        self.police = tkfont.Font(root=root, family=famille, size=10)
        self.police_detail = tkfont.Font(root=root, family=famille, size=9)
        police_titre = tkfont.Font(root=root, family=titre, size=20, weight="bold")
        police_section = tkfont.Font(root=root, family=famille, size=10, weight="bold")

        try:
            self.images = _images_interrupteur("sombre" if c is SOMBRE else "clair", facteur)
        except Exception:
            self.images = None

        corps = tk.Frame(f, bg=c["fond"], padx=round(28 * facteur), pady=round(20 * facteur))
        corps.pack(fill="both", expand=True)
        self.largeur_texte = round(430 * facteur)

        tk.Label(corps, text="Saisie", font=police_titre, bg=c["fond"], fg=c["texte"],
                 anchor="w").pack(fill="x")
        tk.Label(corps, text=f"{NOM} — seulement des mots pulaar",
                 font=self.police_detail, bg=c["fond"], fg=c["detail"], anchor="w").pack(fill="x", pady=(0, 14))

        self.interrupteurs = {}
        self.carte_ful = None
        if not ful_dans_win_espace():
            tk.Label(corps, text="Win + Espace", font=police_section, bg=c["fond"],
                     fg=c["texte"], anchor="w").pack(fill="x", pady=(0, 6))
            self.carte_ful = self._carte(
                corps, None, "FUL (Pulaar) n'est pas encore dans Win + Espace",
                "Ajoutez-le pour écrire en pulaar : FUL, avec les claviers Français (AZERTY) et "
                "Anglais (QWERTY) de Windows, et le correcteur orthographique pulaar.",
                lien=("Ajouter FUL à Win + Espace", self._ajoute_ful))
        tk.Label(corps, text="Clavier", font=police_section, bg=c["fond"],
                 fg=c["texte"], anchor="w").pack(fill="x", pady=(14 if self.carte_ful else 0, 6))
        self._carte(corps, None, "Lettres pulaar avec FUL",
                    "Quand FUL (Pulaar) est choisi dans Win + Espace : v → ɓ, z → ɗ, q → ŋ, x → ƴ, "
                    "^ ou [ → ñ, et les suggestions. Avec Français ou Anglais, le clavier ne change pas.")

        tk.Label(corps, text="Suggestions et corrections", font=police_section, bg=c["fond"],
                 fg=c["texte"], anchor="w").pack(fill="x", pady=(14, 6))
        self._carte(corps, "suggestions",
                    "Afficher les suggestions de texte lors de la frappe",
                    "Des mots pulaar dans une bulle au-dessus du curseur. Tab prend la suggestion "
                    "en surbrillance ; clic, Alt + 1, 2, 3 ou Flèche haut pour une autre.")
        self._carte(corps, "fleches",
                    "Choisir les suggestions avec les flèches ← →",
                    "Sans la souris : ← → surlignent une suggestion, Tab ou Entrée la prennent. "
                    "Pour déplacer le curseur dans le texte pendant que la bulle est ouverte : Échap d'abord.")
        self._carte(corps, "correction_automatique",
                    "Corriger automatiquement les fautes d'orthographe",
                    "À l'espace, fulbe devient fulɓe et jaraama devient jaaraama. "
                    "Retour arrière juste après annule la correction.")
        self._carte(corps, "retenir_les_mots",
                    "Retenir les mots que j'écris",
                    "Ils sont proposés en premier, même après avoir redémarré l'ordinateur.",
                    lien=("Oublier les mots retenus", self._oublie))

        tk.Label(corps, text="Démarrage", font=police_section, bg=c["fond"], fg=c["texte"],
                 anchor="w").pack(fill="x", pady=(14, 6))
        if en_paquet():
            # Version du Microsoft Store : Windows règle lui-même son démarrage.
            self._carte(corps, None, "Démarrer avec Windows",
                        f"{NOM} se lance tout seul à l'ouverture de la session ; Windows le règle "
                        "dans Paramètres > Applications > Démarrage.",
                        lien=("Ouvrir les applications de démarrage",
                              lambda: os.startfile("ms-settings:startupapps")))
        else:
            self._carte(corps, None, "Démarrer avec Windows",
                        f"{NOM} se lance tout seul à l'ouverture de la session.",
                        valeur=demarre_avec_windows(), action=self._demarrage)

        self.message = tk.Label(corps, text="", font=self.police_detail, bg=c["fond"], fg=c["detail"],
                                anchor="w")
        self.message.pack(fill="x", pady=(10, 0))

        f.update_idletasks()
        self._barre_de_titre_sombre(f, c is SOMBRE)
        x = (f.winfo_screenwidth() - f.winfo_reqwidth()) // 2
        y = (f.winfo_screenheight() - f.winfo_reqheight()) // 3
        f.geometry(f"+{x}+{y}")
        f.lift()
        f.focus_force()

    def _carte(self, parent, cle, titre, detail, valeur=None, action=None, lien=None):
        c = self.couleurs
        carte = tk.Frame(parent, bg=c["carte"], highlightbackground=c["bord"],
                         highlightcolor=c["bord"], highlightthickness=1)
        carte.pack(fill="x", pady=(0, 4))
        textes = tk.Frame(carte, bg=c["carte"])
        textes.pack(side="left", fill="x", expand=True, padx=(18, 8), pady=12)
        tk.Label(textes, text=titre, font=self.police, bg=c["carte"], fg=c["texte"], anchor="w",
                 justify="left", wraplength=self.largeur_texte).pack(fill="x")
        tk.Label(textes, text=detail, font=self.police_detail, bg=c["carte"], fg=c["detail"],
                 anchor="w", justify="left", wraplength=self.largeur_texte).pack(fill="x")
        if lien:
            texte, commande = lien
            l = tk.Label(textes, text=texte, font=self.police_detail, bg=c["carte"], fg=c["lien"],
                         anchor="w", cursor="hand2")
            l.pack(fill="x", pady=(4, 0))
            l.bind("<Button-1>", lambda _e: commande())

        if cle is None and action is None:
            return carte  # une carte sans interrupteur, avec son seul lien
        if cle is not None:
            valeur = self.moteur.parametres[cle]
            action = lambda v, cle=cle: self.moteur.change_setting(cle, v)
        interrupteur = Interrupteur(carte, c, self.police, self.images, valeur, action)
        if cle is not None:
            self.interrupteurs[cle] = interrupteur
        return carte

    def _ajoute_ful(self):
        """Lien « Ajouter FUL à Win + Espace » : PowerShell travaille à part, la fenêtre attend."""
        if getattr(self, "_ajout_en_cours", False):
            return
        self._ajout_en_cours = True
        self.message.configure(text="Ajout de FUL à Win + Espace…")
        resultat = []
        threading.Thread(target=lambda: resultat.append(ajoute_ful()), daemon=True).start()

        def attend():
            if not resultat:
                self.fenetre.after(200, attend)
                return
            self._ajout_en_cours = False
            if resultat[0]:
                self.message.configure(text="FUL est dans Win + Espace : choisissez-le pour écrire en pulaar.")
                if self.carte_ful is not None:
                    self.carte_ful.destroy()
                    self.carte_ful = None
            else:
                self.message.configure(text="FUL n'a pas pu être ajouté : Paramètres > Heure et langue "
                                            "> Langue et région > Ajouter une langue.")
        attend()

    def rafraichit(self):
        """Remet les interrupteurs à jour (changement fait depuis l'icône)."""
        for cle, interrupteur in self.interrupteurs.items():
            interrupteur.regle(self.moteur.parametres[cle])

    def _demarrage(self, actif):
        try:
            regle_demarrage(actif)
            self.message.configure(text="Le clavier démarrera avec Windows." if actif
                                   else "Le clavier ne démarrera plus avec Windows.")
        except OSError as e:
            self.message.configure(text=f"Impossible de changer le démarrage : {e}")

    def _oublie(self):
        self.moteur.forget_learned()
        self.message.configure(text="Les mots retenus ont été oubliés.")

    @staticmethod
    def _barre_de_titre_sombre(fenetre, sombre):
        if not sombre:
            return
        try:
            hwnd = ctypes.windll.user32.GetParent(fenetre.winfo_id())
            valeur = ctypes.c_int(1)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(valeur), ctypes.sizeof(valeur))
        except Exception:
            pass

    def ferme(self):
        FenetreParametres.ouverte = None
        self.fenetre.destroy()
