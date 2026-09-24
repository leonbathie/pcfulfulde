#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fabrique icones/clavier_pulaar.ico : la lettre ɓ, blanche sur une touche verte
arrondie, dans toutes les tailles que Windows demande (zone de notification,
barre des tâches, paramètres).

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


if __name__ == "__main__":
    images = [dessine(t) for t in TAILLES]
    chemin = os.path.join(ICI, "clavier_pulaar.ico")
    images[-1].save(chemin, format="ICO", sizes=[(t, t) for t in TAILLES], append_images=images[:-1])
    images[-1].save(os.path.join(ICI, "clavier_pulaar.png"))
    print(f"Icône écrite : {chemin}")
