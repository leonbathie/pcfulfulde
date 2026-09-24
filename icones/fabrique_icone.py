#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fabrique les images du Clavier Pulaar, une fois pour toutes (Pillow n'est
nécessaire qu'ici : le clavier lui-même n'en a pas besoin) :
- clavier_pulaar.ico : la lettre ɓ, blanche sur une touche verte arrondie, dans
  toutes les tailles que Windows demande (zone de notification, barre des
  tâches, paramètres) ;
- interrupteur_<thème>_<0|1>_<échelle>.png : l'interrupteur de Windows 11 de
  la fenêtre de paramètres, désactivé et activé, en thème clair et sombre, pour
  chaque échelle d'affichage.

Usage : python icones/fabrique_icone.py
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(ICI))
from parametres_clavier import CLAIR, SOMBRE, ECHELLES_INTERRUPTEUR, image_interrupteur  # noqa: E402

TAILLES = [16, 20, 24, 32, 40, 48, 64, 256]
VERT = (0, 133, 63)
POLICE = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", "segoeuib.ttf")


def dessine(taille):
    # Suréchantillonné puis réduit : des bords nets même en 16 × 16.
    s = 8 if taille < 64 else 2
    t = taille * s
    im = Image.new("RGBA", (t, t), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    marge = round(t * 0.04)
    d.rounded_rectangle((marge, marge, t - marge, t - marge), radius=round(t * 0.22), fill=VERT)
    police = ImageFont.truetype(POLICE, round(t * 0.78))
    d.text((t / 2, t / 2 - t * 0.02), "ɓ", font=police, fill="white", anchor="mm")
    return im.resize((taille, taille), Image.LANCZOS)


def interrupteur(couleurs, actif, facteur):
    """L'interrupteur de Windows 11 : une pilule bleue quand il est activé."""
    largeur, hauteur = round(40 * facteur), round(20 * facteur)
    s = 4  # suréchantillonnage, pour des bords lisses
    im = Image.new("RGBA", (largeur * s, hauteur * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rayon = hauteur * s // 2
    boite = (0, 0, largeur * s - 1, hauteur * s - 1)
    if actif:
        d.rounded_rectangle(boite, radius=rayon, fill=couleurs["accent"])
        cx, r, couleur = largeur * s - rayon, int(rayon * 0.55), couleurs["pastille"]
    else:
        d.rounded_rectangle(boite, radius=rayon, fill=couleurs["carte"],
                            outline=couleurs["eteint"], width=max(s, round(facteur * s)))
        cx, r, couleur = rayon, int(rayon * 0.45), couleurs["eteint"]
    cy = hauteur * s // 2
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=couleur)
    return im.resize((largeur, hauteur), Image.LANCZOS)


if __name__ == "__main__":
    images = [dessine(t) for t in TAILLES]
    chemin = os.path.join(ICI, "clavier_pulaar.ico")
    images[-1].save(chemin, format="ICO", sizes=[(t, t) for t in TAILLES], append_images=images[:-1])
    images[-1].save(os.path.join(ICI, "clavier_pulaar.png"))
    print(f"Icône écrite : {chemin}")

    for theme, couleurs in (("clair", CLAIR), ("sombre", SOMBRE)):
        for echelle in ECHELLES_INTERRUPTEUR:
            for actif in (False, True):
                interrupteur(couleurs, actif, echelle / 100).save(image_interrupteur(theme, actif, echelle))
    print(f"Interrupteurs écrits : {2 * 2 * len(ECHELLES_INTERRUPTEUR)} images")
