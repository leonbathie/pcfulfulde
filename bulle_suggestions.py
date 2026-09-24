#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bulle de suggestions flottante du Clavier Fulfulde (Pulaar), affichee juste
au-dessus du curseur de texte de l'application active, comme les suggestions
de texte de Windows 11.

- La fenetre ne prend jamais le focus (WS_EX_NOACTIVATE) : cliquer une
  suggestion laisse la main a l'application ou l'on ecrit.
- Le curseur de texte est trouve par GetGUIThreadInfo (Bloc-notes, Word...),
  puis par l'accessibilite MSAA (Chrome, Edge, Firefox...).
- Tkinter doit tourner sur le fil principal. Les autres fils (crochet clavier,
  souris) n'appellent que `affiche` et `masque`, qui deposent une demande dans
  une file lue par la boucle Tk.
"""

import sys
import time
import queue
import ctypes
from ctypes import wintypes
import tkinter as tk
import tkinter.font as tkfont

try:
    import winreg
except ImportError:  # hors Windows
    winreg = None

# Instances propres a ce module : pynput regle ses propres argtypes sur
# ctypes.windll.user32, il ne faut pas les ecraser.
user32 = ctypes.WinDLL("user32", use_last_error=True)
oleacc = ctypes.WinDLL("oleacc")
ole32 = ctypes.WinDLL("ole32")
try:
    dwmapi = ctypes.WinDLL("dwmapi")
except OSError:
    dwmapi = None

LONG_PTR = ctypes.c_ssize_t

GWL_EXSTYLE = -20
GCL_STYLE = -26
WS_EX_TOPMOST = 0x00000008
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_NOACTIVATE = 0x08000000
CS_DROPSHADOW = 0x00020000
SW_HIDE = 0
SW_SHOWNOACTIVATE = 4
HWND_TOPMOST = wintypes.HWND(-1)
SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_NOACTIVATE = 0x0010
SWP_FRAMECHANGED = 0x0020
MONITOR_DEFAULTTONEAREST = 2
OBJID_CARET = 0xFFFFFFF8
VT_I4 = 3
DWMWA_WINDOW_CORNER_PREFERENCE = 33
DWMWCP_ROUND = 2

# Nombre maximal de suggestions montrees, comme Windows.
NOMBRE_MAX = 3


class GUITHREADINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("hwndActive", wintypes.HWND),
        ("hwndFocus", wintypes.HWND),
        ("hwndCapture", wintypes.HWND),
        ("hwndMenuOwner", wintypes.HWND),
        ("hwndMoveSize", wintypes.HWND),
        ("hwndCaret", wintypes.HWND),
        ("rcCaret", wintypes.RECT),
    ]


class MONITORINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("rcMonitor", wintypes.RECT),
        ("rcWork", wintypes.RECT),
        ("dwFlags", wintypes.DWORD),
    ]


class GUID(ctypes.Structure):
    _fields_ = [
        ("Data1", wintypes.DWORD),
        ("Data2", wintypes.WORD),
        ("Data3", wintypes.WORD),
        ("Data4", ctypes.c_ubyte * 8),
    ]


class VARIANT(ctypes.Structure):
    # Seul VT_I4 sert ici ; la taille doit rester celle d'un vrai VARIANT
    # (24 octets en 64 bits, 16 en 32 bits) car il est passe par valeur.
    _fields_ = [
        ("vt", ctypes.c_ushort),
        ("r1", ctypes.c_ushort),
        ("r2", ctypes.c_ushort),
        ("r3", ctypes.c_ushort),
        ("lVal", ctypes.c_long),
        ("pad", ctypes.c_byte * (ctypes.sizeof(ctypes.c_void_p) * 2 - 4)),
    ]


# IID_IAccessible {618736E0-3C3D-11CF-810C-00AA00389B71}
IID_IAccessible = GUID(0x618736E0, 0x3C3D, 0x11CF,
                       (ctypes.c_ubyte * 8)(0x81, 0x0C, 0x00, 0xAA, 0x00, 0x38, 0x9B, 0x71))

# Methodes de IAccessible appelees par leur rang dans la vtable :
# IUnknown (0-2), IDispatch (3-6), puis accParent (7) ... accLocation (22).
_RELEASE = ctypes.WINFUNCTYPE(ctypes.c_ulong, ctypes.c_void_p)
_ACC_LOCATION = ctypes.WINFUNCTYPE(
    ctypes.c_long, ctypes.c_void_p,
    ctypes.POINTER(ctypes.c_long), ctypes.POINTER(ctypes.c_long),
    ctypes.POINTER(ctypes.c_long), ctypes.POINTER(ctypes.c_long),
    VARIANT,
)

user32.GetForegroundWindow.restype = wintypes.HWND
user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
user32.GetWindowThreadProcessId.restype = wintypes.DWORD
user32.GetGUIThreadInfo.argtypes = [wintypes.DWORD, ctypes.POINTER(GUITHREADINFO)]
user32.ClientToScreen.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.POINT)]
user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
user32.GetParent.argtypes = [wintypes.HWND]
user32.GetParent.restype = wintypes.HWND
user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
user32.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                ctypes.c_int, ctypes.c_int, wintypes.UINT]
user32.MonitorFromPoint.argtypes = [wintypes.POINT, wintypes.DWORD]
user32.MonitorFromPoint.restype = wintypes.HMONITOR
user32.GetMonitorInfoW.argtypes = [wintypes.HMONITOR, ctypes.POINTER(MONITORINFO)]
oleacc.AccessibleObjectFromWindow.argtypes = [wintypes.HWND, wintypes.DWORD,
                                              ctypes.POINTER(GUID), ctypes.POINTER(ctypes.c_void_p)]
oleacc.AccessibleObjectFromWindow.restype = ctypes.c_long

if ctypes.sizeof(ctypes.c_void_p) == 8:
    _GetWindowLong = user32.GetWindowLongPtrW
    _SetWindowLong = user32.SetWindowLongPtrW
    _GetClassLong = user32.GetClassLongPtrW
    _SetClassLong = user32.SetClassLongPtrW
else:
    _GetWindowLong = user32.GetWindowLongW
    _SetWindowLong = user32.SetWindowLongW
    _GetClassLong = user32.GetClassLongW
    _SetClassLong = user32.SetClassLongW
for _f in (_GetWindowLong, _GetClassLong):
    _f.argtypes = [wintypes.HWND, ctypes.c_int]
    _f.restype = LONG_PTR
for _f in (_SetWindowLong, _SetClassLong):
    _f.argtypes = [wintypes.HWND, ctypes.c_int, LONG_PTR]
    _f.restype = LONG_PTR


def active_dpi():
    """Coordonnees en pixels reels sur tous les ecrans, pour placer la bulle au pixel pres."""
    try:
        user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))  # PER_MONITOR_AWARE_V2
        return
    except Exception:
        pass
    try:
        ctypes.WinDLL("shcore").SetProcessDpiAwareness(2)
    except Exception:
        pass


def fenetre_active():
    return user32.GetForegroundWindow()


def _curseur_gui(tid):
    """Curseur systeme de l'application : (x, haut, bas) a l'ecran, ou None."""
    info = GUITHREADINFO()
    info.cbSize = ctypes.sizeof(GUITHREADINFO)
    if not user32.GetGUIThreadInfo(tid, ctypes.byref(info)) or not info.hwndCaret:
        return None, info
    rc = info.rcCaret
    if rc.bottom - rc.top <= 0:
        return None, info
    haut = wintypes.POINT(rc.left, rc.top)
    bas = wintypes.POINT(rc.left, rc.bottom)
    user32.ClientToScreen(info.hwndCaret, ctypes.byref(haut))
    user32.ClientToScreen(info.hwndCaret, ctypes.byref(bas))
    return (haut.x, haut.y, bas.y), info


def _curseur_msaa(hwnd):
    """Curseur donne par l'accessibilite (Chrome, Edge, Firefox...), ou None."""
    if not hwnd:
        return None
    acc = ctypes.c_void_p()
    hr = oleacc.AccessibleObjectFromWindow(hwnd, OBJID_CARET, ctypes.byref(IID_IAccessible),
                                           ctypes.byref(acc))
    if hr != 0 or not acc.value:
        return None
    vtable = ctypes.cast(acc, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
    try:
        x, y, l, h = (ctypes.c_long() for _ in range(4))
        soi = VARIANT()
        soi.vt = VT_I4
        soi.lVal = 0  # CHILDID_SELF
        hr = _ACC_LOCATION(vtable[22])(acc, ctypes.byref(x), ctypes.byref(y),
                                       ctypes.byref(l), ctypes.byref(h), soi)
        if hr != 0 or h.value <= 0 or (x.value == 0 and y.value == 0):
            return None
        return x.value, y.value, y.value + h.value
    finally:
        _RELEASE(vtable[2])(acc)


def position_du_curseur():
    """Position du curseur de texte de l'application active : (x, haut, bas) ou None."""
    hwnd = fenetre_active()
    if not hwnd:
        return None
    tid = user32.GetWindowThreadProcessId(hwnd, None)
    position, info = _curseur_gui(tid)
    if position:
        return position
    try:
        return _curseur_msaa(info.hwndFocus or hwnd)
    except OSError:
        return None


def _theme_sombre():
    if winreg is None:
        return False
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize") as cle:
            return winreg.QueryValueEx(cle, "AppsUseLightTheme")[0] == 0
    except OSError:
        return False


# Couleurs des menus volants de Windows 11. « tab » : la suggestion que prend
# la touche Tab ; « choisi » : celle choisie avec les flèches.
THEME_CLAIR = {"fond": "#FFFFFF", "bord": "#D9D9D9", "texte": "#1A1A1A", "indice": "#8A8A8A",
               "survol": "#F0F0F0", "tab": "#E8F0FB", "choisi": "#CCE0F8"}
THEME_SOMBRE = {"fond": "#2C2C2C", "bord": "#454545", "texte": "#FFFFFF", "indice": "#9A9A9A",
                "survol": "#3A3A3A", "tab": "#2F3B48", "choisi": "#3D5A78"}


class BulleSuggestions:
    """La bulle elle-meme. Construite et animee sur le fil principal."""

    def __init__(self, sur_choix, sur_tic=None):
        """
        sur_choix(index) : appele (fil Tk) quand on clique une suggestion.
        sur_tic()        : appele (fil Tk) a chaque tour de boucle, ~15 ms.
        """
        self.sur_choix = sur_choix
        self.sur_tic = sur_tic
        self._file = queue.Queue()
        self._demande = None          # derniere demande (suggestions, selection)
        self._demande_a = 0.0
        self._essais = 0              # relectures du curseur pour la demande en cours
        self._montree = []            # suggestions affichees
        self._selection = None
        self._survol = None
        self._visible = False
        self.rectangle = None         # (g, h, d, b) a l'ecran quand visible
        self._derniere_position = None

        ole32.CoInitialize(None)      # pour l'accessibilite MSAA
        self.couleurs = THEME_SOMBRE if _theme_sombre() else THEME_CLAIR

        self.root = tk.Tk()
        self.root.withdraw()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg=self.couleurs["bord"])

        familles = set(tkfont.families(self.root))
        famille = "Segoe UI Variable Text" if "Segoe UI Variable Text" in familles else "Segoe UI"
        self.police = tkfont.Font(family=famille, size=11)

        self.cadre = tk.Frame(self.root, bg=self.couleurs["fond"], padx=4, pady=4)
        self.cadre.pack(padx=1, pady=1)
        self.etiquettes = []
        for i in range(NOMBRE_MAX):
            e = tk.Label(self.cadre, text="", font=self.police, bg=self.couleurs["fond"],
                         fg=self.couleurs["texte"], padx=12, pady=5, cursor="hand2")
            e.bind("<Button-1>", lambda _ev, i=i: self._clic(i))
            e.bind("<Enter>", lambda _ev, i=i: self._survole(i))
            e.bind("<Leave>", lambda _ev: self._survole(None))
            self.etiquettes.append(e)
        # Repère discret : Tab prend la suggestion en surbrillance.
        self.indice = tk.Label(self.cadre, text="Tab ⇥", font=tkfont.Font(family=famille, size=8),
                               bg=self.couleurs["fond"], fg=self.couleurs["indice"], padx=8)

        # Premiere apparition hors de l'ecran, invisible, pour que Windows cree
        # la fenetre ; on regle alors ses styles avant de la montrer vraiment.
        self.root.attributes("-alpha", 0.0)
        self.root.geometry("+-32000+-32000")
        self.root.deiconify()
        self.root.update()
        self.hwnd = user32.GetParent(self.root.winfo_id()) or self.root.winfo_id()
        style = _GetWindowLong(self.hwnd, GWL_EXSTYLE)
        _SetWindowLong(self.hwnd, GWL_EXSTYLE,
                       style | WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW | WS_EX_TOPMOST)
        _SetClassLong(self.hwnd, GCL_STYLE, _GetClassLong(self.hwnd, GCL_STYLE) | CS_DROPSHADOW)
        user32.SetWindowPos(self.hwnd, HWND_TOPMOST, 0, 0, 0, 0,
                            SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_FRAMECHANGED)
        if dwmapi is not None:
            coin = ctypes.c_int(DWMWCP_ROUND)
            if dwmapi.DwmSetWindowAttribute(wintypes.HWND(self.hwnd), DWMWA_WINDOW_CORNER_PREFERENCE,
                                            ctypes.byref(coin), ctypes.sizeof(coin)) == 0:
                # Windows 11 arrondit et borde lui-meme la fenetre.
                self.root.configure(bg=self.couleurs["fond"])
        user32.ShowWindow(self.hwnd, SW_HIDE)
        self.root.attributes("-alpha", 1.0)

        self.root.after(15, self._boucle)

    # --- Appels possibles depuis n'importe quel fil -------------------------

    def affiche(self, suggestions, selection=None):
        self._file.put(("affiche", list(suggestions[:NOMBRE_MAX]), selection))

    def masque(self):
        self._file.put(("masque", None, None))

    def arrete(self):
        self._file.put(("arrete", None, None))

    def execute(self, fonction):
        """Fait tourner `fonction` sur le fil Tk (fenetre de reglages, par exemple)."""
        self._file.put(("execute", fonction, None))

    def contient(self, x, y):
        r = self.rectangle
        return bool(r) and r[0] <= x < r[2] and r[1] <= y < r[3]

    # --- Fil Tk ---------------------------------------------------------------

    def lance(self):
        self.root.mainloop()

    def _boucle(self):
        try:
            while True:
                action, suggestions, selection = self._file.get_nowait()
                if action == "arrete":
                    self.root.quit()
                    return
                if action == "execute":
                    try:
                        suggestions()
                    except Exception as e:
                        print(f"[bulle] {e}", file=sys.stderr)
                elif action == "masque":
                    self._demande = None
                    self._cache()
                else:
                    self._demande = (suggestions, selection)
                    self._demande_a = time.monotonic()
                    self._essais = 0
        except queue.Empty:
            pass

        # On laisse ~30 ms a l'application pour afficher la lettre et deplacer
        # son curseur avant de lire sa position.
        if self._demande is not None and time.monotonic() - self._demande_a >= 0.03:
            suggestions, selection = self._demande
            self._demande = None
            if not suggestions:
                self._cache()
            else:
                position = position_du_curseur()
                if position is None and self._essais < 3:
                    # Chrome et Edge donnent parfois leur curseur un instant plus tard.
                    self._essais += 1
                    self._demande = (suggestions, selection)
                    self._demande_a = time.monotonic() + 0.03
                else:
                    self._montre(suggestions, selection, position)

        if self.sur_tic:
            try:
                self.sur_tic()
            except Exception as e:
                print(f"[bulle] {e}", file=sys.stderr)
        self.root.after(15, self._boucle)

    def _couleur(self, i):
        if i == self._selection:
            return self.couleurs["choisi"]
        if i == self._survol:
            return self.couleurs["survol"]
        if self._selection is None and i == 0:
            return self.couleurs["tab"]
        return self.couleurs["fond"]

    def _peint(self):
        for i, e in enumerate(self.etiquettes):
            e.configure(bg=self._couleur(i))

    def _montre(self, suggestions, selection, position):
        if position is None:
            position = self._position_de_secours()
        if position is None:
            self._cache()
            return

        if suggestions != self._montree:
            self.indice.pack_forget()
            for i, e in enumerate(self.etiquettes):
                e.pack_forget()
                if i < len(suggestions):
                    e.configure(text=suggestions[i])
                    e.pack(side="left", padx=(0 if i == 0 else 2, 0))
            self.indice.pack(side="left")
            self._montree = list(suggestions)
            self._survol = None
        self._selection = selection
        self._peint()

        self.root.update_idletasks()
        largeur = self.root.winfo_reqwidth()
        hauteur = self.root.winfo_reqheight()
        x, haut, bas = position
        x -= 16
        y = haut - hauteur - 6

        travail = self._zone_de_travail(x, haut)
        if travail:
            g, h, d, b = travail
            if y < h:  # pas la place au-dessus : sous la ligne
                y = bas + 6
            x = max(g, min(x, d - largeur))
            y = max(h, min(y, b - hauteur))

        self.root.geometry(f"+{x}+{y}")
        self.root.update_idletasks()
        user32.ShowWindow(self.hwnd, SW_SHOWNOACTIVATE)
        user32.SetWindowPos(self.hwnd, HWND_TOPMOST, 0, 0, 0, 0,
                            SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE)
        self._visible = True
        self._derniere_position = (position, fenetre_active())
        self.rectangle = (x, y, x + largeur, y + hauteur)

    def _position_de_secours(self):
        """Sans curseur lisible : derniere position connue dans la meme fenetre,
        sinon le bas de la fenetre active."""
        hwnd = fenetre_active()
        if self._derniere_position and self._derniere_position[1] == hwnd:
            return self._derniere_position[0]
        rect = wintypes.RECT()
        if not hwnd or not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
            return None
        x = (rect.left + rect.right) // 2 - 100
        return x, rect.bottom - 60, rect.bottom - 40

    def _zone_de_travail(self, x, y):
        moniteur = user32.MonitorFromPoint(wintypes.POINT(x, y), MONITOR_DEFAULTTONEAREST)
        info = MONITORINFO()
        info.cbSize = ctypes.sizeof(MONITORINFO)
        if not moniteur or not user32.GetMonitorInfoW(moniteur, ctypes.byref(info)):
            return None
        r = info.rcWork
        return r.left, r.top, r.right, r.bottom

    def _cache(self):
        if self._visible:
            user32.ShowWindow(self.hwnd, SW_HIDE)
        self._visible = False
        self._montree = []
        self._selection = None
        self.rectangle = None

    def _survole(self, i):
        self._survol = i
        self._peint()

    def _clic(self, i):
        if i < len(self._montree):
            self.sur_choix(i)
