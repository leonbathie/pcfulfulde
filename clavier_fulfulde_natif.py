#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moteur du Clavier Fulfulde (Pulaar) Latin pour Windows, comme les claviers de Microsoft :
- Actif seulement quand le clavier « Pulaar » est choisi (Win + Espace) : avec
  Français ou Anglais, il se tait.
- Bulle de suggestions au-dessus du curseur de texte, comme Windows 11 : le mot
  en cours, le mot suivant et les groupes de deux mots (hol ko, hay so).
  Choix : clic, TAB (1re suggestion), Alt+1..3, ou Flèche haut puis ←/→ et Entrée.
- Correction automatique à l'espace (fulbe -> fulɓe), annulée par Retour arrière.
- Seulement des mots pulaar ; les mots que l'on écrit sont retenus d'une session à l'autre.
- Icône près de l'horloge et fenêtre de paramètres ; pas de fenêtre noire (pythonw).
"""

import sys
import os
import time
import json
import math
import bisect
import signal
import threading
import ctypes
from ctypes import wintypes
from pynput import keyboard, mouse
from pynput.keyboard import Key, KeyCode, Controller

import parametres_clavier as pc

# Forcer la sortie UTF-8 sur console Windows pour afficher correctement ɓ, ɗ, ŋ, ƴ, ’
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

controller = Controller()

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DICT_PATH = os.path.join(SCRIPT_DIR, "dictionary", "dict_ff_latin.json")

# Constantes Win32
LLKHF_INJECTED = 0x00000010
VK_TAB = 0x09
VK_BACK = 0x08
VK_RETURN = 0x0D
VK_ESCAPE = 0x1B
VK_SPACE = 0x20
VK_PRIOR = 0x21
VK_NEXT = 0x22
VK_END = 0x23
VK_HOME = 0x24
VK_LEFT = 0x25
VK_UP = 0x26
VK_RIGHT = 0x27
VK_DOWN = 0x28
VK_DELETE = 0x2E
VK_CAPITAL = 0x14
VK_SHIFT = 0x10
VK_CONTROL = 0x11
VK_MENU = 0x12       # Alt
VK_LSHIFT = 0xA0
VK_RSHIFT = 0xA1
VK_LCONTROL = 0xA2
VK_RCONTROL = 0xA3
VK_LMENU = 0xA4      # Left Alt
VK_RMENU = 0xA5      # Right Alt (AltGr)
# Touche sans effet, envoyée pendant Alt+chiffre pour que le relâchement d'Alt
# n'ouvre pas le menu de l'application.
VK_MASQUE = 0xE8

WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_SYSKEYDOWN = 0x0104
WM_SYSKEYUP = 0x0105

# Touches qui déplacent le curseur : le mot en cours n'est plus celui qu'on suit.
TOUCHES_DE_DEPLACEMENT = (VK_LEFT, VK_RIGHT, VK_UP, VK_DOWN, VK_HOME, VK_END,
                          VK_PRIOR, VK_NEXT, VK_DELETE)

VALID_ONE_CHAR_WORDS = {'e', 'a', 'o', 'i'}

# Le clavier Pulaar de Windows : la langue ff-Latn-SN (0x0867), ou l'une de nos dispositions.
LANGUE_PULAAR = 0x0867
NOS_DISPOSITIONS = {"fulffaz.dll", "fulffqw.dll", "kbdfulfa.dll", "kbdfulfq.dll"}

_TRANS_TABLE = str.maketrans({
    'ɓ': 'b', 'Ɓ': 'b',
    'ɗ': 'd', 'Ɗ': 'd',
    'ŋ': 'n', 'Ŋ': 'n',
    'ñ': 'n', 'Ñ': 'n',
    'ƴ': 'y', 'Ƴ': 'y',
    '’': '', '\'': '', '`': '', '‘': '', 'ʼ': '',
    'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
    'Á': 'a', 'É': 'e', 'Í': 'i', 'Ó': 'o', 'Ú': 'u'
})

_APOSTROPHES = str.maketrans({'\'': '’', '`': '’', '‘': '’', 'ʼ': '’'})

# Instance propre : pynput règle ses propres argtypes sur ctypes.windll.user32.
_user32 = ctypes.WinDLL("user32")
_user32.GetForegroundWindow.restype = wintypes.HWND
_user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.c_void_p]
_user32.GetWindowThreadProcessId.restype = wintypes.DWORD
_user32.GetKeyboardLayout.argtypes = [wintypes.DWORD]
_user32.GetKeyboardLayout.restype = ctypes.c_void_p
_user32.ToUnicodeEx.argtypes = [wintypes.UINT, wintypes.UINT, ctypes.POINTER(ctypes.c_ubyte),
                                ctypes.c_wchar_p, ctypes.c_int, wintypes.UINT, ctypes.c_void_p]


def normalize_fulfulde_search(s):
    if not s:
        return ""
    return s.lower().translate(_TRANS_TABLE)


def forme_mot(s):
    """Forme de référence d'un mot : minuscules, hamza en ’."""
    if not s:
        return ""
    return s.strip().lower().translate(_APOSTROPHES)


def _debut_commun(a, b):
    """Nombre de caractères identiques au début de `a` et de `b`."""
    n = 0
    while n < min(len(a), len(b)) and a[n] == b[n]:
        n += 1
    return n


def is_caps_lock_active():
    if sys.platform == 'win32':
        return bool(ctypes.windll.user32.GetKeyState(VK_CAPITAL) & 1)
    return False


def disposition_active():
    """Disposition du clavier (HKL) de la fenêtre au premier plan."""
    thread_id = _user32.GetWindowThreadProcessId(_user32.GetForegroundWindow(), None)
    return _user32.GetKeyboardLayout(thread_id) or 0


_dispositions_connues = {}


def disposition_pulaar(hkl):
    """Vrai si `hkl` est le clavier Pulaar de Windows (choisi par Win + Espace)."""
    if hkl not in _dispositions_connues:
        langue = hkl & 0xFFFF
        appareil = (hkl >> 16) & 0xFFFF
        _dispositions_connues[hkl] = (langue == LANGUE_PULAAR
                                      or _fichier_de_disposition(appareil, langue) in NOS_DISPOSITIONS)
    return _dispositions_connues[hkl]


def _fichier_de_disposition(appareil, langue):
    """Fichier DLL d'une disposition, lu dans le registre (Keyboard Layouts)."""
    try:
        import winreg
        racine = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                r"SYSTEM\CurrentControlSet\Control\Keyboard Layouts")
    except OSError:
        return ""
    with racine:
        try:
            if appareil & 0xF000 != 0xF000:
                with winreg.OpenKey(racine, f"0000{appareil:04x}") as cle:
                    return winreg.QueryValueEx(cle, "Layout File")[0].lower()
            # Disposition « variante » : retrouvée par son Layout Id et sa langue.
            identifiant = f"{appareil & 0x0FFF:04x}"
            i = 0
            while True:
                klid = winreg.EnumKey(racine, i)
                i += 1
                if klid[-4:].lower() != f"{langue:04x}":
                    continue
                with winreg.OpenKey(racine, klid) as cle:
                    try:
                        if winreg.QueryValueEx(cle, "Layout Id")[0].lower() == identifiant:
                            return winreg.QueryValueEx(cle, "Layout File")[0].lower()
                    except OSError:
                        pass
        except OSError:
            return ""


def get_char_from_vk(vk_code, scan_code, shift=False, caps=False, alt_gr=False, layout=None):
    """Caractère produit par une touche dans la disposition de la fenêtre active.

    L'état des modificateurs est reconstruit à la main : GetKeyboardState, lu
    depuis le fil du crochet, ne reflète pas celui de l'application.
    """
    if sys.platform != 'win32':
        return ""
    keyboard_state = (ctypes.c_ubyte * 256)()
    if shift:
        keyboard_state[VK_SHIFT] = 0x80
    if caps:
        keyboard_state[VK_CAPITAL] = 0x01
    if alt_gr:
        keyboard_state[VK_CONTROL] = keyboard_state[VK_LCONTROL] = 0x80
        keyboard_state[VK_MENU] = keyboard_state[VK_RMENU] = 0x80
    if layout is None:
        layout = disposition_active()
    buff = ctypes.create_unicode_buffer(8)
    # Drapeau 0x4 : ne pas toucher à l'état des touches mortes (^, ¨) de Windows.
    res = _user32.ToUnicodeEx(vk_code, scan_code, keyboard_state, buff, 8, 0x4, layout)
    if res > 0:
        return buff.value[:res]
    return ""


class FulfuldeAutoCompleter:
    """Recherche des mots par début de saisie, sur des tableaux triés.

    Les clés sont normalisées (ɓ -> b, ɗ -> d, ’ retiré...) : taper `fulb`
    trouve `fulɓe`. Les débuts de une à trois lettres ouvrent sur des milliers
    de mots : leurs meilleurs candidats sont calculés une fois au chargement.
    """

    TETE_MAX = 3          # longueur des débuts précalculés
    PAR_TETE = 30         # candidats gardés par début court
    PARCOURS_MAX = 3000   # mots lus au plus pour un début plus long
    MAX_SUITES = 8        # suites gardées par mot
    # Lettres des clés normalisées (ɓ, ɗ, ŋ, ñ, ƴ y sont déjà rabattues).
    ALPHABET_DES_CLES = "abcdefghijklmnoprstuwy"
    # La correction automatique ne met à la place de ce qu'on a tapé qu'un mot
    # courant, et seulement quand il se détache nettement d'un autre candidat.
    CORRECTION_FREQUENCE_MIN = 20
    CORRECTION_ECART = 3

    def __init__(self, dict_path=DICT_PATH):
        self.words = {}       # forme -> fréquence
        self.ngrams = {}      # mot -> suites, de la plus fréquente à la plus rare
        self.groupes = {}     # mot -> suite assez fréquente pour être proposée avec lui
        self.appris = {}      # forme -> bonus gagné en l'écrivant
        self.compteurs = {}   # forme -> nombre de fois écrite
        self.suites_apprises = {}  # mot -> suites écrites par l'utilisateur
        self.ignores = set()  # mots gardés tels quels après une correction annulée
        self.modifie = False  # quelque chose de nouveau à retenir
        self._ngrams_origine = {}  # suites du dictionnaire avant apprentissage
        self._cles = []       # clés normalisées, triées
        self._formes = []     # formes, dans l'ordre des clés
        self._tete = {}       # début court -> meilleures formes
        self._cache = {}
        self.load_dictionary(dict_path)

    @staticmethod
    def _est_un_mot(w):
        if not w or not any(c.isalpha() for c in w):
            return False
        return len(w) > 1 or w in VALID_ONE_CHAR_WORDS

    def load_dictionary(self, path):
        if not os.path.exists(path):
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"⚠️ Erreur chargement dictionnaire : {e}")
            return
        for item in data.get("words", []):
            w = forme_mot(item.get("w", ""))
            if self._est_un_mot(w):
                self.words[w] = max(self.words.get(w, 0), item.get("f", 1))
        for cle, suites in data.get("ngrams", {}).items():
            if isinstance(suites, dict):
                suites = sorted(suites, key=suites.get, reverse=True)
            k = forme_mot(cle)
            propres = [s for s in (forme_mot(x) for x in suites) if s in self.words and s != k]
            if propres:
                self.ngrams[k] = propres[:self.MAX_SUITES]
        self.groupes = {forme_mot(k): forme_mot(v) for k, v in data.get("groupes", {}).items()}
        self._indexe()

    def _indexe(self):
        paires = sorted((normalize_fulfulde_search(w), w) for w in self.words)
        self._cles = [c for c, _ in paires]
        self._formes = [w for _, w in paires]
        self._tete = {}
        for w in sorted(self.words, key=self.words.get, reverse=True):
            self._ajoute_en_tete(w)
        self._cache.clear()

    def _ajoute_en_tete(self, w, devant=False):
        cle = normalize_fulfulde_search(w)
        for n in range(1, min(self.TETE_MAX, len(cle)) + 1):
            liste = self._tete.setdefault(cle[:n], [])
            if devant:
                if w in liste:
                    liste.remove(w)
                liste.insert(0, w)
                del liste[self.PAR_TETE:]
            elif len(liste) < self.PAR_TETE:
                liste.append(w)

    def _candidats(self, norm):
        if len(norm) <= self.TETE_MAX:
            return self._tete.get(norm, [])
        i = bisect.bisect_left(self._cles, norm)
        sortie = []
        while i < len(self._cles) and self._cles[i].startswith(norm) and len(sortie) < self.PARCOURS_MAX:
            sortie.append(self._formes[i])
            i += 1
        return sortie

    def _formes_de_cle(self, cle):
        """Les formes dont la clé normalisée est exactement `cle`."""
        i = bisect.bisect_left(self._cles, cle)
        sortie = []
        while i < len(self._cles) and self._cles[i] == cle:
            sortie.append(self._formes[i])
            i += 1
        return sortie

    def _variantes(self, cle):
        """Les clés à une lettre de `cle` : changée, oubliée, en trop ou intervertie."""
        sortie = set()
        for i in range(len(cle)):
            sortie.add(cle[:i] + cle[i + 1:])
            for c in self.ALPHABET_DES_CLES:
                sortie.add(cle[:i] + c + cle[i + 1:])
                sortie.add(cle[:i] + c + cle[i:])
            if i + 1 < len(cle):
                sortie.add(cle[:i] + cle[i + 1] + cle[i] + cle[i + 2:])
        for c in self.ALPHABET_DES_CLES:
            sortie.add(cle + c)
        sortie.discard(cle)
        return sortie

    def _presque(self, norm, limite):
        """Les mots qui commencent presque par `norm` (à une lettre près), les plus courants d'abord.

        Sans cela, la bulle restait vide à la moindre faute de frappe : `jaraam`
        ne proposait rien, alors que `jaaraama` n'est qu'à une lettre.
        """
        trouves = {}
        for v in self._variantes(norm):
            i = bisect.bisect_left(self._cles, v)
            for j in range(i, min(i + 30, len(self._cles))):
                if not self._cles[j].startswith(v):
                    break
                trouves[self._formes[j]] = self.words.get(self._formes[j], 0)
        return [w for w, _ in sorted(trouves.items(), key=lambda x: (-x[1], len(x[0])))[:limite]]

    def predict(self, prefix, previous_word=None, limit=5):
        """Les mots qui complètent `prefix` ; sans préfixe, ceux qui suivent `previous_word`."""
        saisie = forme_mot(prefix)
        avant = forme_mot(previous_word) if previous_word else ""
        cache_key = (saisie, avant, limit)
        if cache_key in self._cache:
            return self._cache[cache_key]

        suites = self.ngrams.get(avant, []) if avant else []
        if not saisie:
            res = suites[:limit]
        else:
            norm = normalize_fulfulde_search(saisie)
            rang = {w: i for i, w in enumerate(suites)}
            candidats = set(self._candidats(norm))
            # Les suites du mot précédent, même hors des meilleurs de ce début.
            candidats.update(w for w in suites if normalize_fulfulde_search(w).startswith(norm))
            notes = []
            for w in candidats:
                if w == saisie:
                    continue
                note = math.log1p(self.words.get(w, 0)) + self.appris.get(w, 0.0)
                if w.startswith(saisie):
                    note += 0.5
                if w in rang:
                    note += 6.0 - 0.4 * rang[w]
                # Dès trois lettres, qui a écrit « ndiy » veut plutôt « ndiyam »
                # que « ndiyanteeje ».
                if len(norm) >= 3:
                    note -= 0.1 * (len(w) - len(saisie))
                notes.append((-note, len(w), w))
            notes.sort()
            ordre = [w for _, _, w in notes]
            # Deux mots de soi au plus passent devant, comme sur le clavier
            # mobile : on les a écrits, le corpus ne les porte pas toujours.
            siens = [w for w in ordre if w in self.appris][:2]
            res = (siens + [w for w in ordre if w not in siens])[:limit]
            if not res and len(norm) >= 4 and saisie not in self.words:
                res = self._presque(norm, limit)

        if len(self._cache) > 4096:
            self._cache.clear()
        self._cache[cache_key] = res
        return res

    def correction(self, word):
        """La forme à mettre à la place d'un mot inconnu, ou None.

        Comme la correction automatique de Windows : seulement quand le mot tapé
        n'existe pas et qu'un mot courant s'en distingue à peine.
        """
        w = forme_mot(word)
        if len(w) < 2 or w in self.words or w in self.ignores:
            return None
        if any(c.isdigit() for c in w):
            return None
        lettres = [c for c in word if c.isalpha()]
        if len(lettres) >= 2 and all(c.isupper() for c in lettres):
            return None  # un sigle
        cle = normalize_fulfulde_search(w)
        # 1. Les mêmes lettres, sans les crochets ni la hamza : fulbe -> fulɓe, be -> ɓe
        memes = [f for f in self._formes_de_cle(cle) if f != w]
        if memes:
            return self._casse(word, max(memes, key=lambda f: self.words.get(f, 0)))
        # 2. Une lettre de différence, à partir de quatre lettres : jaraama -> jaaraama
        if len(cle) < 4:
            return None
        candidats = {}
        for v in self._variantes(cle):
            for f in self._formes_de_cle(v):
                candidats[f] = self.words.get(f, 0)
        if not candidats:
            return None
        classes = sorted(candidats.items(), key=lambda x: -x[1])
        meilleure, frequence = classes[0]
        seconde = classes[1][1] if len(classes) > 1 else 0
        # Deux corrections aussi plausibles : on ne choisit pas à la place de celui qui écrit.
        if frequence >= self.CORRECTION_FREQUENCE_MIN and frequence >= self.CORRECTION_ECART * seconde:
            return self._casse(word, meilleure)
        return None

    def _suite_pour_groupe(self, mot):
        """Le mot qui suit presque toujours `mot` (« hol » -> « ko »), ou None."""
        return self.groupes.get(forme_mot(mot))

    def suggestions(self, prefix, previous_word=None, nombre=3):
        """Ce que montre la bulle, à la manière de Windows 11 :
        [meilleur mot, meilleur mot + sa suite, deuxième mot]."""
        mots = self.predict(prefix, previous_word, limit=nombre + 2)
        if not mots:
            return []
        sortie = [mots[0]]
        suite = self._suite_pour_groupe(mots[0])
        if suite and nombre >= 3:
            sortie.append(f"{mots[0]} {suite}")
        for w in mots[1:]:
            if len(sortie) >= nombre:
                break
            sortie.append(w)
        return [self._casse(prefix, s) for s in sortie]

    @staticmethod
    def _casse(saisie, texte):
        """Reporte la majuscule tapée sur la suggestion (Ja -> Jaaraama, JA -> JAARAAMA)."""
        lettres = [c for c in (saisie or "") if c.isalpha()]
        if len(lettres) >= 2 and all(c.isupper() for c in lettres):
            return texte.upper()
        if lettres and lettres[0].isupper():
            return texte[:1].upper() + texte[1:]
        return texte

    # --- Ce que l'on apprend de celui qui écrit ---------------------------------

    def learn_word(self, word, previous_word=None):
        w = forme_mot(word)
        if len(w) < 2 or not any(c.isalpha() for c in w):
            return
        self._retiens(w, self.compteurs.get(w, 0) + 1)
        prev = forme_mot(previous_word) if previous_word else ""
        if prev and prev != w:
            self._ajoute_suite(prev, w)

    def ignore(self, word):
        """Garder `word` tel quel : la correction automatique ne le touchera plus."""
        w = forme_mot(word)
        if self._est_un_mot(w):
            self.ignores.add(w)
            self._retiens(w, self.compteurs.get(w, 0) + 1)

    def _retiens(self, w, compte):
        self._cache.clear()
        self.modifie = True
        self.compteurs[w] = compte
        self.appris[w] = min(1.5 * compte, 6.0)
        if w not in self.words:
            self.words[w] = 1
            cle = normalize_fulfulde_search(w)
            i = bisect.bisect_left(self._cles, cle)
            self._cles.insert(i, cle)
            self._formes.insert(i, w)
        self._ajoute_en_tete(w, devant=True)

    def _ajoute_suite(self, prev, w):
        if prev not in self._ngrams_origine:
            self._ngrams_origine[prev] = list(self.ngrams[prev]) if prev in self.ngrams else None
        for table in (self.ngrams, self.suites_apprises):
            suites = table.setdefault(prev, [])
            if w in suites:
                suites.remove(w)
            suites.insert(0, w)
            del suites[self.MAX_SUITES:]
        self._cache.clear()
        self.modifie = True

    def exporte_appris(self, maximum=5000):
        """Ce qui mérite d'être gardé d'une session à l'autre : les mots écrits au
        moins deux fois (une coquille ne revient pas), et ceux qu'on a gardés tels quels."""
        gardes = {w: n for w, n in self.compteurs.items() if n >= 2 or w in self.ignores}
        gardes = dict(sorted(gardes.items(), key=lambda x: -x[1])[:maximum])
        suites = {p: l for p, l in self.suites_apprises.items()
                  if p in self.words and any(s in gardes or self.words.get(s, 0) > 1 for s in l)}
        return {"version": 1, "mots": gardes, "suites": dict(list(suites.items())[-maximum:]),
                "ignores": sorted(self.ignores)}

    def importe_appris(self, donnees):
        for w, n in (donnees.get("mots") or {}).items():
            w = forme_mot(w)
            if self._est_un_mot(w) and isinstance(n, int) and n > 0:
                self._retiens(w, n)
        for w in donnees.get("ignores") or []:
            w = forme_mot(w)
            if self._est_un_mot(w):
                self.ignores.add(w)
                if w not in self.compteurs:
                    self._retiens(w, 1)
        for prev, suites in (donnees.get("suites") or {}).items():
            for s in reversed(suites[:self.MAX_SUITES]):
                s = forme_mot(s)
                if self._est_un_mot(s):
                    self._ajoute_suite(forme_mot(prev), s)
        self.modifie = False

    def oublie_appris(self):
        """Oublier tout ce qui a été appris (bouton « Oublier les mots retenus »)."""
        for prev, origine in self._ngrams_origine.items():
            if origine is None:
                self.ngrams.pop(prev, None)
            else:
                self.ngrams[prev] = origine
        self._ngrams_origine.clear()
        self.appris.clear()
        self.compteurs.clear()
        self.suites_apprises.clear()
        self.ignores.clear()
        self._cache.clear()
        self.modifie = False


class FulfuldeEngine:
    def __init__(self):
        self.layout = "AZERTY"  # "AZERTY" ou "QWERTY" (mode sans disposition Windows)
        self.shift_pressed = False
        self.ctrl_pressed = False
        self.alt_pressed = False
        self.alt_gr_pressed = False

        # Réglages par défaut ; run() les remplace par ceux enregistrés.
        self.parametres = dict(pc.PAR_DEFAUT)

        # Moteur d'autocomplétion
        self.autocompleter = FulfuldeAutoCompleter()
        self.current_prefix = ""
        self.previous_word = None       # tel qu'il a été écrit, majuscules comprises
        self.current_suggestions = []
        self.selection = None           # suggestion surlignée après Flèche haut
        self.bubble_dismissed = False   # Échap : plus de bulle jusqu'au mot suivant
        self.pending_alt_choice = None  # Alt+chiffre, appliqué au relâchement d'Alt
        self.last_correction = None     # (tapé, corrigé, séparateur, précédent) : Retour arrière l'annule
        self.listener = None
        self.bubble = None
        self.window = None              # fenêtre où l'on écrit

        # Le crochet clavier, la souris, l'icône et la bulle vivent sur quatre fils.
        self.lock = threading.RLock()
        self.injection_lock = threading.Lock()

        # Clés supprimées à ignorer sur keyup
        self.suppressed_keys = set()

    @property
    def autocomplete_enabled(self):
        return self.parametres["suggestions"]

    def is_capital(self):
        return self.shift_pressed ^ is_caps_lock_active()

    def toggle_layout(self):
        self.layout = "QWERTY" if self.layout == "AZERTY" else "AZERTY"
        print(f"\n>> [DISPOSITION ACTIVÉE] : {self.layout}")

    def toggle_autocompletion(self):
        self.change_setting("suggestions", not self.parametres["suggestions"])
        status = "ACTIVÉE" if self.autocomplete_enabled else "DÉSACTIVÉE"
        print(f"\n>> [AUTOCOMPLÉTION] : {status}")

    # --- Réglages, icône, fenêtre de paramètres ---------------------------------

    def change_setting(self, cle, valeur):
        """Un interrupteur des paramètres, ou du menu de l'icône, a changé."""
        with self.lock:
            self.parametres[cle] = valeur
            self.reset_context()
        fenetre = pc.FenetreParametres.ouverte
        if fenetre is not None and self.bubble:
            self.bubble.execute(fenetre.rafraichit)

    def forget_learned(self):
        with self.lock:
            self.autocompleter.oublie_appris()
            self.reset_context()
        pc.oublie_mots_appris()

    def save_learned(self):
        with self.lock:
            if not self.autocompleter.modifie or not self.parametres["retenir_les_mots"]:
                return
            donnees = self.autocompleter.exporte_appris()
            self.autocompleter.modifie = False
        try:
            pc.ecrit_mots_appris(donnees)
        except OSError as e:
            print(f"[mots appris] {e}", file=sys.stderr)

    def open_settings(self):
        if self.bubble:
            self.bubble.execute(lambda: pc.FenetreParametres.ouvre(self.bubble.root, self))

    def quit(self):
        if self.bubble:
            self.bubble.arrete()

    def tray_menu(self):
        p = self.parametres
        return [
            ("Paramètres du clavier Pulaar…", False, self.open_settings),
            None,
            ("Suggestions de texte", p["suggestions"],
             lambda: self.change_setting("suggestions", not p["suggestions"])),
            ("Correction automatique", p["correction_automatique"],
             lambda: self.change_setting("correction_automatique", not p["correction_automatique"])),
            None,
            ("Quitter le clavier Pulaar", False, self.quit),
        ]

    # --- Suggestions et bulle ---------------------------------------------------

    def update_suggestions(self):
        """Recalcule les suggestions et met la bulle à jour."""
        if (self.autocomplete_enabled and not self.bubble_dismissed
                and (self.current_prefix or self.previous_word)):
            self.current_suggestions = self.autocompleter.suggestions(
                self.current_prefix, self.previous_word
            )
        else:
            self.current_suggestions = []
        self.selection = None
        self.refresh_bubble()

    def refresh_bubble(self):
        if not self.bubble:
            return
        if self.current_suggestions:
            self.bubble.affiche(self.current_suggestions, self.selection)
        else:
            self.bubble.masque()

    def reset_context(self):
        """Le curseur a bougé ou la fenêtre a changé : on ne sait plus ce qui l'entoure."""
        self.current_prefix = ""
        self.previous_word = None
        self.current_suggestions = []
        self.selection = None
        self.bubble_dismissed = False
        self.pending_alt_choice = None
        self.last_correction = None
        self.refresh_bubble()

    def _inject(self, backspaces, to_type, then=None):
        """Efface `backspaces` caractères puis tape `to_type` dans l'application active."""
        def do_inject():
            with self.injection_lock:
                time.sleep(0.005)
                for _ in range(backspaces):
                    controller.tap(Key.backspace)
                    time.sleep(0.002)
                if to_type:
                    controller.type(to_type)
            if then:
                with self.lock:
                    then()

        threading.Thread(target=do_inject, daemon=True).start()

    def end_word(self, vk, separator, keep_context):
        """Espace (keep_context), ponctuation ou Entrée : le mot en cours est fini.

        Avec la correction automatique, un mot inconnu tout proche d'un mot
        courant est remplacé avant que le séparateur n'arrive à l'application.
        """
        word = self.current_prefix
        previous = self.previous_word
        self.current_prefix = ""
        self.bubble_dismissed = False
        correction = None
        if word and self.parametres["correction_automatique"]:
            correction = self.autocompleter.correction(word)

        if not correction:
            if word:
                self.autocompleter.learn_word(word, previous)
            if not keep_context:
                self.previous_word = None
            elif word:
                self.previous_word = word
            self.update_suggestions()
            return True

        self.autocompleter.learn_word(correction, previous)
        self.previous_word = correction if keep_context else None
        self.current_suggestions = []
        self.selection = None
        if self.bubble:
            self.bubble.masque()
        # Retour arrière juste après annule, comme sous Windows (pas après Entrée :
        # le message est peut-être déjà parti).
        if separator != "\n":
            self.last_correction = (word, correction, separator, previous)
        after = self.previous_word

        def then():
            if not self.current_prefix and self.previous_word == after:
                self.update_suggestions()

        common = _debut_commun(word, correction)
        self._inject(len(word) - common, correction[common:] + separator, then)
        return self.suppress(vk)

    def undo_correction(self, undo):
        """Retour arrière juste après une correction : on remet le mot tapé, et on le garde."""
        word, correction, separator, previous = undo
        self.autocompleter.ignore(word)
        self.current_prefix = word
        self.previous_word = previous
        self.current_suggestions = []
        self.selection = None
        if self.bubble:
            self.bubble.masque()

        def then():
            if self.current_prefix == word:
                self.update_suggestions()

        common = _debut_commun(word, correction)
        self._inject(len(correction) - common + len(separator), word[common:], then)

    def apply_completion(self, text):
        """Remplace le mot tapé par la suggestion dans l'application active."""
        if not text:
            return
        typed = self.current_prefix
        previous = self.previous_word
        for word in text.split():
            self.autocompleter.learn_word(word, previous)
            previous = word
        self.previous_word = previous
        self.current_prefix = ""
        self.current_suggestions = []
        self.selection = None
        self.bubble_dismissed = False
        self.last_correction = None
        if self.bubble:
            self.bubble.masque()

        def then():
            # Proposer aussitôt le mot suivant, comme Windows
            if not self.current_prefix and self.previous_word == previous:
                self.update_suggestions()

        # On n'efface que ce qui diffère : taper « jaa » puis choisir
        # « jaaraama » n'envoie que « raama ».
        common = _debut_commun(typed, text)
        self._inject(len(typed) - common, text[common:] + " ", then)

    def choose(self, index):
        """Choix d'une suggestion (clic dans la bulle, Alt+chiffre)."""
        with self.lock:
            if 0 <= index < len(self.current_suggestions):
                self.apply_completion(self.current_suggestions[index])

    def inject_replacement(self, rep_char):
        """Injecte le caractère Fulfulde en remplacement de la touche pressée."""
        def do_type():
            time.sleep(0.002)
            controller.type(rep_char)

        threading.Thread(target=do_type, daemon=True).start()

    def suppress(self, vk):
        """Retire la touche du flux : l'application ne la verra pas (keyup compris)."""
        self.suppressed_keys.add(vk)
        if self.listener:
            self.listener.suppress_event()  # lève une exception : rien ne s'exécute après
        return False

    def watch_foreground(self):
        """Appelé par la bulle à chaque tour : changer de fenêtre fait oublier le contexte."""
        foreground = _user32.GetForegroundWindow()
        if foreground and foreground != self.window and foreground != self.bubble.hwnd:
            with self.lock:
                self.window = foreground
                self.reset_context()

    def on_mouse_click(self, x, y, button, pressed):
        """Un clic ailleurs que dans la bulle déplace le curseur de texte."""
        if not pressed:
            return
        if self.bubble and self.bubble.contient(x, y):
            return
        with self.lock:
            self.reset_context()

    # --- Le crochet clavier -------------------------------------------------------

    def win32_filter(self, msg, data):
        """
        Filtre bas niveau exécuté dans le hook WH_KEYBOARD_LL Windows.
        Permet de supprimer UNIQUEMENT les touches à remplacer sans bloquer le reste.
        """
        # Ne JAMAIS intercepter nos propres frappes injectées
        if data.flags & LLKHF_INJECTED:
            return True
        with self.lock:
            return self._filter(msg, data)

    def _filter(self, msg, data):
        vk = data.vkCode
        is_down = msg in (WM_KEYDOWN, WM_SYSKEYDOWN)
        is_up = msg in (WM_KEYUP, WM_SYSKEYUP)

        # Suivi des touches modificatrices
        if vk in (VK_SHIFT, VK_LSHIFT, VK_RSHIFT):
            self.shift_pressed = is_down
            return True
        elif vk in (VK_CONTROL, VK_LCONTROL, VK_RCONTROL):
            self.ctrl_pressed = is_down
            return True
        elif vk in (VK_MENU, VK_LMENU):
            self.alt_pressed = is_down
            # Alt+chiffre : la suggestion n'est tapée qu'une fois Alt relâché,
            # sans quoi l'application recevrait Alt+lettre.
            if is_up and self.pending_alt_choice is not None:
                index, self.pending_alt_choice = self.pending_alt_choice, None
                threading.Timer(0.02, self.choose, args=(index,)).start()
            return True
        elif vk in (VK_RMENU,):
            self.alt_gr_pressed = is_down
            return True

        # Gestion des keyups pour les touches supprimées sur keydown
        if is_up:
            if vk in self.suppressed_keys:
                self.suppressed_keys.discard(vk)
                if self.listener:
                    self.listener.suppress_event()
                return False
            return True

        # À ce stade, nous sommes sur un keydown (is_down == True)

        # Une autre fenêtre : ce qui était en cours d'écriture ne la concerne pas.
        foreground = _user32.GetForegroundWindow()
        if foreground != self.window:
            self.window = foreground
            self.reset_context()

        # Comme les claviers de Microsoft : le clavier Pulaar n'agit que lorsqu'il
        # est choisi (Win + Espace). Avec Français ou Anglais, il se tait.
        layout = _user32.GetKeyboardLayout(_user32.GetWindowThreadProcessId(foreground, None)) or 0
        pulaar = disposition_pulaar(layout)
        remap = self.parametres["sans_disposition"] and not pulaar
        if not (pulaar or remap):
            if self.current_prefix or self.previous_word or self.current_suggestions:
                self.reset_context()
            return True

        undo = self.last_correction
        self.last_correction = None
        plain = not (self.ctrl_pressed or self.alt_pressed or self.alt_gr_pressed or self.shift_pressed)

        # 1. Raccourcis de contrôle globaux
        # Ctrl + Shift + L : Basculer AZERTY <-> QWERTY (sans disposition Windows seulement)
        if remap and self.ctrl_pressed and self.shift_pressed and vk == 0x4C: # 'L'
            self.toggle_layout()
            return self.suppress(vk)

        # Ctrl + Shift + A : Activer / Désactiver les suggestions
        if self.ctrl_pressed and self.shift_pressed and vk == 0x41: # 'A'
            self.toggle_autocompletion()
            return self.suppress(vk)

        # 2. BULLE : Flèche haut entre dans la bulle, ←/→ choisissent, Entrée ou
        # TAB valident, Échap ou Flèche bas en sortent (comme Windows 11).
        if self.selection is not None:
            if plain and vk in (VK_LEFT, VK_RIGHT):
                step = 1 if vk == VK_RIGHT else -1
                self.selection = (self.selection + step) % len(self.current_suggestions)
                self.refresh_bubble()
                return self.suppress(vk)
            if plain and vk in (VK_RETURN, VK_TAB):
                self.apply_completion(self.current_suggestions[self.selection])
                return self.suppress(vk)
            if vk in (VK_ESCAPE, VK_DOWN, VK_UP):
                if vk != VK_UP:
                    self.selection = None
                    self.refresh_bubble()
                return self.suppress(vk)
            # Toute autre touche quitte la bulle et agit normalement.
            self.selection = None
            self.refresh_bubble()
        elif plain and vk == VK_UP and self.current_suggestions:
            self.selection = 0
            self.refresh_bubble()
            return self.suppress(vk)

        # Échap ferme la bulle jusqu'au mot suivant, et reste vu par l'application.
        if vk == VK_ESCAPE:
            if self.current_suggestions:
                self.bubble_dismissed = True
                self.update_suggestions()
            return True

        # 3. AUTOCOMPLÉTION : Touche TAB pour accepter la suggestion #1 d'un mot commencé
        # (après une espace, TAB garde son rôle : champ suivant, tabulation...)
        if vk == VK_TAB and self.autocomplete_enabled and not (self.ctrl_pressed or self.alt_pressed):
            if self.current_prefix and self.current_suggestions:
                self.apply_completion(self.current_suggestions[0])
                return self.suppress(vk)

        # 4. AUTOCOMPLÉTION : Touches Alt + [1, 2, 3]
        if self.alt_pressed and not self.alt_gr_pressed and not self.ctrl_pressed:
            if vk in (0x31, 0x32, 0x33): # '1', '2', '3'
                idx = vk - 0x31
                if idx < len(self.current_suggestions):
                    self.pending_alt_choice = idx
                    threading.Thread(target=controller.tap, args=(KeyCode.from_vk(VK_MASQUE),),
                                     daemon=True).start()
                    return self.suppress(vk)

        # Si Ctrl standard est pressé (Ctrl+C, Ctrl+V, Ctrl+Retour...) -> le texte a pu changer
        if self.ctrl_pressed and not self.alt_gr_pressed:
            self.reset_context()
            return True

        # Le curseur se déplace : le mot suivi n'est plus sous le curseur
        if vk in TOUCHES_DE_DEPLACEMENT:
            self.reset_context()
            return True

        # Gestion Backspace
        if vk == VK_BACK:
            if undo and not self.alt_pressed:
                # Juste après une correction automatique : on remet le mot tapé.
                self.undo_correction(undo)
                return self.suppress(vk)
            if self.current_prefix:
                self.current_prefix = self.current_prefix[:-1]
                self.update_suggestions()
            elif self.previous_word:
                # L'espace qui suivait le mot précédent vient d'être effacée :
                # on est de nouveau à la fin de ce mot.
                self.current_prefix, self.previous_word = self.previous_word, None
                self.update_suggestions()
            else:
                self.reset_context()
            return True

        # Gestion Espace / Entrée (fin de mot)
        if vk == VK_SPACE:
            return self.end_word(vk, " ", keep_context=True)
        if vk == VK_RETURN:
            return self.end_word(vk, "\n", keep_context=False)

        # 5. REMPLACEMENT DES CARACTÈRES FULFULDE SPÉCIAUX (sans disposition Windows :
        # avec le clavier Pulaar de Windows, c'est lui qui donne ɓ, ɗ, ŋ, ƴ, ñ)
        replacement = None
        is_cap = self.is_capital()

        # A. Mode AltGr (AltGr + touche)
        if not remap:
            pass
        elif self.alt_gr_pressed or (self.ctrl_pressed and self.alt_pressed):
            if vk == 0x42:      # B
                replacement = 'Ɓ' if is_cap else 'ɓ'
            elif vk == 0x44:    # D
                replacement = 'Ɗ' if is_cap else 'ɗ'
            elif vk == 0x4E:    # N
                replacement = 'Ŋ' if is_cap else 'ŋ'
            elif vk == 0x59:    # Y
                replacement = 'Ƴ' if is_cap else 'ƴ'
            elif vk == 0x41:    # A
                replacement = 'Á' if is_cap else 'á'
            elif vk == 0x45:    # E
                replacement = 'É' if is_cap else 'é'
            elif vk == 0x49:    # I
                replacement = 'Í' if is_cap else 'í'
            elif vk == 0x4F:    # O
                replacement = 'Ó' if is_cap else 'ó'
            elif vk == 0x55:    # U
                replacement = 'Ú' if is_cap else 'ú'
            elif vk == 0x5A:    # Z -> z/Z
                replacement = 'Z' if is_cap else 'z'
            elif vk == 0x51:    # Q -> q/Q
                replacement = 'Q' if is_cap else 'q'
            elif vk == 0x58:    # X -> x/X
                replacement = 'X' if is_cap else 'x'
            elif vk == 0x56:    # V -> v/V
                replacement = 'V' if is_cap else 'v'
            elif vk in (0xDD, 0xBA): # ^ -> ^
                replacement = '^'
            elif vk in (0xDE, 0xC0): # Quote / Backtick
                replacement = '’'

        # B. Mode Direct AZERTY (Calqué exactement sur l'interface officielle)
        elif self.layout == "AZERTY":
            if vk == 0x5A:      # Touche 'Z' physique -> ɗ / Ɗ
                replacement = 'Ɗ' if is_cap else 'ɗ'
            elif vk == 0x51:    # Touche 'Q' physique -> ŋ / Ŋ
                replacement = 'Ŋ' if is_cap else 'ŋ'
            elif vk == 0x58:    # Touche 'X' physique -> ƴ / Ƴ
                replacement = 'Ƴ' if is_cap else 'ƴ'
            elif vk == 0x56:    # Touche 'V' physique -> ɓ / Ɓ
                replacement = 'Ɓ' if is_cap else 'ɓ'
            elif vk in (0xDD, 0xBA): # Touche '^ / ¨' (à droite de P) -> ñ / Ñ
                replacement = 'Ñ' if is_cap else 'ñ'
            elif vk in (0xDE, 0xDC, 0xDF): # Touche '²'
                # Vérifier le caractère produit
                char = get_char_from_vk(vk, data.scanCode, self.shift_pressed, layout=layout)
                if char in ('²', '’', "'"):
                    replacement = '’'

        # C. Mode Direct QWERTY
        elif self.layout == "QWERTY":
            if vk == 0xDB:      # [
                replacement = 'Ɓ' if is_cap else 'ɓ'
            elif vk == 0xDD:    # ]
                replacement = 'Ɗ' if is_cap else 'ɗ'
            elif vk == 0xBA:    # ;
                replacement = 'Ŋ' if is_cap else 'ŋ'
            elif vk == 0x51:    # Q
                replacement = 'Ƴ' if is_cap else 'ƴ'
            elif vk == 0xDE:    # '
                replacement = '’'

        # Si un remplacement Fulfulde existe pour cette touche
        if replacement:
            self.current_prefix += replacement
            self.update_suggestions()
            self.inject_replacement(replacement)
            return self.suppress(vk)

        # Si touche normale (laisser passer vers l'application et suivre le mot en cours)
        char = get_char_from_vk(vk, data.scanCode, self.shift_pressed,
                                is_caps_lock_active(), self.alt_gr_pressed, layout=layout)
        if char:
            if char.isalpha() or char in ("'", "’", "-"):
                self.current_prefix += char
                self.update_suggestions()
            elif char in ('.', ',', ';', ':', '!', '?'):
                return self.end_word(vk, char, keep_context=False)
            else:
                # Chiffre ou symbole : plus de mot pulaar en cours
                self.reset_context()

        # Laisser passer la touche originale
        return True

    def on_press(self, key):
        # Ne jamais renvoyer False pour éviter de couper le listener pynput
        return True

    def on_release(self, key):
        # Ne jamais renvoyer False pour éviter de couper le listener pynput
        return True


engine = FulfuldeEngine()

_MUTEX = None


def _seule_instance():
    """Un seul moteur à la fois : deux crochets clavier taperaient tout en double."""
    global _MUTEX
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateMutexW.argtypes = [ctypes.c_void_p, wintypes.BOOL, wintypes.LPCWSTR]
    kernel32.CreateMutexW.restype = wintypes.HANDLE
    _MUTEX = kernel32.CreateMutexW(None, False, "Local\\ClavierPulaar.Moteur")
    return ctypes.get_last_error() != 183  # ERROR_ALREADY_EXISTS


def _journal_si_sans_console():
    """Sous pythonw, pas de console : les messages vont dans journal.txt."""
    if sys.stdout is not None and sys.stderr is not None:
        return
    os.makedirs(pc.DOSSIER, exist_ok=True)
    journal = open(pc.FICHIER_JOURNAL, "a", encoding="utf-8", buffering=1)
    sys.stdout = sys.stderr = journal


def run():
    from bulle_suggestions import BulleSuggestions, active_dpi
    from zone_notification import IconeNotification

    _journal_si_sans_console()
    print(f"--- {time.strftime('%Y-%m-%d %H:%M:%S')} Clavier Pulaar")
    if not _seule_instance():
        print("Le Clavier Pulaar tourne déjà : voir son icône près de l'horloge.")
        return

    # Avant toute fenêtre : coordonnées en pixels réels pour placer la bulle
    active_dpi()
    engine.parametres = pc.Parametres()
    if engine.parametres["retenir_les_mots"]:
        engine.autocompleter.importe_appris(pc.lit_mots_appris())
    engine.bubble = BulleSuggestions(sur_choix=engine.choose, sur_tic=engine.watch_foreground)
    icone = IconeNotification(pc.ICONE, "Clavier Pulaar — suggestions quand « Pulaar » est choisi (Win + Espace)",
                              menu=engine.tray_menu, sur_clic=engine.open_settings)

    print("=" * 68)
    print("      CLAVIER PULAAR (FULFULDE) - MOTEUR ACTIF")
    print("=" * 68)
    print(f"  Dictionnaire : {len(engine.autocompleter.words)} mots pulaar, "
          f"{len(engine.autocompleter.ngrams)} avec leurs suites")
    print("  Le clavier agit quand « Pulaar » est choisi (Win + Espace).")
    print("  Bulle : clic, TAB, Alt + 1..3, ou Flèche haut puis ← → et Entrée ; Échap la ferme.")
    print("  Correction automatique à l'espace ; Retour arrière juste après l'annule.")
    print("  Paramètres et Quitter : icône ɓ près de l'horloge.")
    print("=" * 68)

    listener = keyboard.Listener(
        on_press=engine.on_press,
        on_release=engine.on_release,
        win32_event_filter=engine.win32_filter,
        suppress=False
    )
    engine.listener = listener
    mouse_listener = mouse.Listener(on_click=engine.on_mouse_click)
    listener.start()
    mouse_listener.start()

    def sauvegarde_reguliere():
        engine.save_learned()
        engine.bubble.root.after(60_000, sauvegarde_reguliere)

    engine.bubble.root.after(60_000, sauvegarde_reguliere)
    # Tkinter tient le fil principal : Ctrl+C passe par la bulle pour s'arrêter.
    signal.signal(signal.SIGINT, lambda *_: engine.bubble.arrete())
    if not engine.parametres["sans_disposition"] and not pc.pulaar_dans_la_liste_des_langues():
        # Sans le clavier Pulaar dans Win + Espace, rien n'apparaîtrait : les
        # paramètres s'ouvrent et expliquent quoi faire.
        engine.open_settings()
    try:
        engine.bubble.lance()
    finally:
        listener.stop()
        mouse_listener.stop()
        icone.arrete()
        engine.save_learned()
        print(f"--- {time.strftime('%Y-%m-%d %H:%M:%S')} arrêt")


if __name__ == "__main__":
    run()
