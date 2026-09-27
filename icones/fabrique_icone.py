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
  chaque échelle d'affichage ;
- installateur/msix/Assets : les logos du paquet du Microsoft Store (menu
  Démarrer, barre des tâches, fiche du Store), à chaque échelle.

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


def logo(largeur, hauteur, part):
    """La touche ɓ centrée sur un fond transparent, occupant `part` du plus petit côté."""
    cote = max(1, round(min(largeur, hauteur) * part))
    im = Image.new("RGBA", (largeur, hauteur), (0, 0, 0, 0))
    im.alpha_composite(dessine(cote), ((largeur - cote) // 2, (hauteur - cote) // 2))
    return im


# Logos du paquet MSIX : (nom, largeur, hauteur de base, part occupée par la touche).
LOGOS_MSIX = [("Square44x44Logo", 44, 44, 1.0), ("Square150x150Logo", 150, 150, 0.66),
              ("StoreLogo", 50, 50, 1.0)]
ECHELLES_MSIX = (100, 125, 150, 200, 400)
TAILLES_CIBLES = (16, 24, 32, 48, 256)


def logos_msix(dossier):
    os.makedirs(dossier, exist_ok=True)
    n = 0
    for nom, l, h, part in LOGOS_MSIX:
        for e in ECHELLES_MSIX:
            logo(round(l * e / 100), round(h * e / 100), part).save(
                os.path.join(dossier, f"{nom}.scale-{e}.png"))
            n += 1
    # Barre des tâches et liste des applications : tailles exactes, avec et sans « plaque ».
    for t in TAILLES_CIBLES:
        for suffixe in ("", "_altform-unplated"):
            logo(t, t, 1.0).save(os.path.join(dossier, f"Square44x44Logo.targetsize-{t}{suffixe}.png"))
            n += 1
    return n


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

    assets = os.path.join(os.path.dirname(ICI), "installateur", "msix", "Assets")
    print(f"Logos du Microsoft Store écrits : {logos_msix(assets)} images ({assets})")
