#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Icône du Clavier Pulaar dans la zone de notification, près de l'horloge.

Clic : ouvre les paramètres. Clic droit : menu (Paramètres, Suggestions,
Correction automatique, Quitter).

L'icône vit sur son propre fil, avec une fenêtre cachée et sa boucle de
messages Windows. Les actions du menu sont des fonctions fournies par le
moteur : c'est à lui de les faire passer sur le bon fil.
"""

import sys
import ctypes
import threading
from ctypes import wintypes

user32 = ctypes.WinDLL("user32", use_last_error=True)
shell32 = ctypes.WinDLL("shell32")
kernel32 = ctypes.WinDLL("kernel32")

LRESULT = ctypes.c_ssize_t
WNDPROC = ctypes.WINFUNCTYPE(LRESULT, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)

WM_NULL = 0x0000
WM_DESTROY = 0x0002
WM_CLOSE = 0x0010
WM_CONTEXTMENU = 0x007B
WM_LBUTTONUP = 0x0202
WM_RBUTTONUP = 0x0205
WM_APP_ICONE = 0x8000 + 1
NIM_ADD, NIM_MODIFY, NIM_DELETE = 0, 1, 2
NIF_MESSAGE, NIF_ICON, NIF_TIP = 0x1, 0x2, 0x4
MF_STRING, MF_CHECKED, MF_SEPARATOR = 0x0, 0x8, 0x800
TPM_RIGHTBUTTON, TPM_NONOTIFY, TPM_RETURNCMD = 0x2, 0x80, 0x100
IMAGE_ICON = 1
LR_LOADFROMFILE = 0x10
LR_DEFAULTSIZE = 0x40
SM_CXSMICON, SM_CYSMICON = 49, 50
IDI_APPLICATION = 32512


class WNDCLASSEXW(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.UINT), ("style", wintypes.UINT), ("lpfnWndProc", WNDPROC),
        ("cbClsExtra", ctypes.c_int), ("cbWndExtra", ctypes.c_int), ("hInstance", wintypes.HINSTANCE),
        ("hIcon", wintypes.HICON), ("hCursor", wintypes.HANDLE), ("hbrBackground", wintypes.HBRUSH),
        ("lpszMenuName", wintypes.LPCWSTR), ("lpszClassName", wintypes.LPCWSTR), ("hIconSm", wintypes.HICON),
    ]


class NOTIFYICONDATAW(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD), ("hWnd", wintypes.HWND), ("uID", wintypes.UINT),
        ("uFlags", wintypes.UINT), ("uCallbackMessage", wintypes.UINT), ("hIcon", wintypes.HICON),
        ("szTip", wintypes.WCHAR * 128), ("dwState", wintypes.DWORD), ("dwStateMask", wintypes.DWORD),
        ("szInfo", wintypes.WCHAR * 256), ("uVersion", wintypes.UINT), ("szInfoTitle", wintypes.WCHAR * 64),
        ("dwInfoFlags", wintypes.DWORD), ("guidItem", ctypes.c_byte * 16), ("hBalloonIcon", wintypes.HICON),
    ]


user32.RegisterClassExW.argtypes = [ctypes.POINTER(WNDCLASSEXW)]
user32.RegisterClassExW.restype = wintypes.ATOM
user32.CreateWindowExW.argtypes = [wintypes.DWORD, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD,
                                   ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                   wintypes.HWND, wintypes.HMENU, wintypes.HINSTANCE, wintypes.LPVOID]
user32.CreateWindowExW.restype = wintypes.HWND
user32.DefWindowProcW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.DefWindowProcW.restype = LRESULT
user32.GetMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT]
user32.TranslateMessage.argtypes = [ctypes.POINTER(wintypes.MSG)]
user32.DispatchMessageW.argtypes = [ctypes.POINTER(wintypes.MSG)]
user32.DispatchMessageW.restype = LRESULT
user32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.DestroyWindow.argtypes = [wintypes.HWND]
user32.RegisterWindowMessageW.argtypes = [wintypes.LPCWSTR]
user32.RegisterWindowMessageW.restype = wintypes.UINT
user32.LoadImageW.argtypes = [wintypes.HINSTANCE, wintypes.LPCWSTR, wintypes.UINT,
                              ctypes.c_int, ctypes.c_int, wintypes.UINT]
user32.LoadImageW.restype = wintypes.HANDLE
user32.LoadIconW.argtypes = [wintypes.HINSTANCE, wintypes.LPVOID]
user32.LoadIconW.restype = wintypes.HICON
user32.CreatePopupMenu.restype = wintypes.HMENU
user32.AppendMenuW.argtypes = [wintypes.HMENU, wintypes.UINT, ctypes.c_size_t, wintypes.LPCWSTR]
user32.SetMenuDefaultItem.argtypes = [wintypes.HMENU, wintypes.UINT, wintypes.UINT]
user32.TrackPopupMenu.argtypes = [wintypes.HMENU, wintypes.UINT, ctypes.c_int, ctypes.c_int,
                                  ctypes.c_int, wintypes.HWND, wintypes.LPVOID]
user32.DestroyMenu.argtypes = [wintypes.HMENU]
user32.SetForegroundWindow.argtypes = [wintypes.HWND]
user32.GetCursorPos.argtypes = [ctypes.POINTER(wintypes.POINT)]
shell32.Shell_NotifyIconW.argtypes = [wintypes.DWORD, ctypes.POINTER(NOTIFYICONDATAW)]
kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
kernel32.GetModuleHandleW.restype = wintypes.HMODULE


class IconeNotification:
    """L'icône près de l'horloge et son menu."""

    def __init__(self, chemin_icone, info_bulle, menu, sur_clic):
        """
        menu()     -> liste de (texte, coché, action), ou None pour un séparateur ;
        sur_clic() -> appelé au clic gauche sur l'icône.
        """
        self.chemin_icone = chemin_icone
        self.info_bulle = info_bulle
        self.menu = menu
        self.sur_clic = sur_clic
        self.hwnd = None
        # Windows envoie déjà des messages pendant CreateWindowExW, avant que la
        # boucle n'ait tout préparé.
        self._barre_recreee = None
        self._icone = None
        self._pret = threading.Event()
        self._fil = threading.Thread(target=self._boucle, name="icone-notification", daemon=True)
        self._fil.start()
        self._pret.wait(5)

    def arrete(self):
        if self.hwnd:
            user32.PostMessageW(self.hwnd, WM_CLOSE, 0, 0)
            self._fil.join(2)

    # --- Fil de l'icône --------------------------------------------------------

    def _boucle(self):
        instance = kernel32.GetModuleHandleW(None)
        self._wndproc = WNDPROC(self._procedure)  # gardée : sinon le ramasse-miettes la libère
        classe = WNDCLASSEXW()
        classe.cbSize = ctypes.sizeof(WNDCLASSEXW)
        classe.lpfnWndProc = self._wndproc
        classe.hInstance = instance
        classe.lpszClassName = "ClavierPulaarNotification"
        user32.RegisterClassExW(ctypes.byref(classe))
        self.hwnd = user32.CreateWindowExW(0, classe.lpszClassName, "Clavier Pulaar", 0,
                                           0, 0, 0, 0, None, None, instance, None)
        # Explorer redémarré : la barre des tâches renaît vide, on y remet l'icône.
        self._barre_recreee = user32.RegisterWindowMessageW("TaskbarCreated")
        self._icone = self._charge_icone()
        self._notifie(NIM_ADD)
        self._pret.set()

        message = wintypes.MSG()
        while user32.GetMessageW(ctypes.byref(message), None, 0, 0) > 0:
            user32.TranslateMessage(ctypes.byref(message))
            user32.DispatchMessageW(ctypes.byref(message))

    def _charge_icone(self):
        cx, cy = user32.GetSystemMetrics(SM_CXSMICON), user32.GetSystemMetrics(SM_CYSMICON)
        icone = user32.LoadImageW(None, self.chemin_icone, IMAGE_ICON, cx, cy, LR_LOADFROMFILE)
        return icone or user32.LoadIconW(None, ctypes.c_void_p(IDI_APPLICATION))

    def _donnees(self, drapeaux):
        d = NOTIFYICONDATAW()
        d.cbSize = ctypes.sizeof(NOTIFYICONDATAW)
        d.hWnd = self.hwnd
        d.uID = 1
        d.uFlags = drapeaux
        d.uCallbackMessage = WM_APP_ICONE
        d.hIcon = self._icone
        d.szTip = self.info_bulle[:127]
        return d

    def _notifie(self, operation):
        d = self._donnees(NIF_MESSAGE | NIF_ICON | NIF_TIP)
        shell32.Shell_NotifyIconW(operation, ctypes.byref(d))

    def _procedure(self, hwnd, message, wparam, lparam):
        try:
            if message == WM_APP_ICONE:
                evenement = lparam & 0xFFFF
                if evenement == WM_LBUTTONUP:
                    self.sur_clic()
                elif evenement in (WM_RBUTTONUP, WM_CONTEXTMENU):
                    self._montre_menu()
                return 0
            if message == self._barre_recreee:
                self._notifie(NIM_ADD)
                return 0
            if message == WM_CLOSE:
                user32.DestroyWindow(hwnd)
                return 0
            if message == WM_DESTROY:
                self._notifie(NIM_DELETE)
                user32.PostQuitMessage(0)
                return 0
        except Exception as e:
            print(f"[icone] {e}", file=sys.stderr)
        return user32.DefWindowProcW(hwnd, message, wparam, lparam)

    def _montre_menu(self):
        entrees = self.menu()
        hmenu = user32.CreatePopupMenu()
        for numero, entree in enumerate(entrees, start=1):
            if entree is None:
                user32.AppendMenuW(hmenu, MF_SEPARATOR, 0, None)
            else:
                texte, coche, _action = entree
                user32.AppendMenuW(hmenu, MF_STRING | (MF_CHECKED if coche else 0), numero, texte)
        user32.SetMenuDefaultItem(hmenu, 1, 0)
        position = wintypes.POINT()
        user32.GetCursorPos(ctypes.byref(position))
        # Sans cela, le menu ne se ferme pas quand on clique ailleurs.
        user32.SetForegroundWindow(self.hwnd)
        choix = user32.TrackPopupMenu(hmenu, TPM_RIGHTBUTTON | TPM_NONOTIFY | TPM_RETURNCMD,
                                      position.x, position.y, 0, self.hwnd, None)
        user32.PostMessageW(self.hwnd, WM_NULL, 0, 0)
        user32.DestroyMenu(hmenu)
        if choix and entrees[choix - 1] is not None:
            entrees[choix - 1][2]()
