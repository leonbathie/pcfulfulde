#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Construit dictionary/dict_ff_latin.json, le dictionnaire d'autocompletion du
Clavier Fulfulde (Pulaar) Latin, a partir de trois sources :

1. Les lexiques du clavier mobile (fulfuldekey/app/src/main/assets/dict) :
   words_ff.txt (mots et frequences, formes rejetees deja retirees) et
   bigrams_ff.txt (trois suites au plus par mot).
2. Le corpus Tappirgal (donnee tappirgal) : preprocessed/bigrams.json pour les
   suites de mots comptees, listes_mots/2_mots_rejetes.txt pour les formes
   jugees fausses et listes_mots/3_lectures_corrigees.txt pour les lectures OCR
   a rattacher a leur vrai mot.
3. L'ancien dictionnaire (sources_dictionnaire/ancien_dict_ff_latin.json, la
   version 2.0 figee) : il porte des mots courants que les lexiques mobiles
   n'ont pas (e, o, a, mido, mbadaa...) et les formules de salutation.

Le fichier produit garde le format que lisent les trois moteurs du projet
(Python, Rust et React) : "words" = [{"w", "f"}], "ngrams" = {mot: [suites]}.
Il y ajoute "groupes" = {mot: suite}, les groupes de deux mots que la bulle
propose d'un bloc ; les moteurs qui ne le connaissent pas l'ignorent.

Usage : python construire_dictionnaire.py
"""

import os
import sys
import re
import json
from collections import defaultdict

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DESKTOP = os.path.join(os.path.expanduser("~"), "Desktop")
FULFULDEKEY_DICT = os.path.join(DESKTOP, "fulfuldekey", "app", "src", "main", "assets", "dict")
TAPPIRGAL_DIR = os.path.join(DESKTOP, "donnee tappirgal")
ANCIEN_DICT = os.path.join(SCRIPT_DIR, "sources_dictionnaire", "ancien_dict_ff_latin.json")
DEST_DICT = os.path.join(SCRIPT_DIR, "dictionary", "dict_ff_latin.json")

# Nombre de suites gardees par mot : la bulle en montre trois, les autres
# servent quand le debut du mot suivant ecarte les premieres.
MAX_SUITES = 8
# Un enchainement vu une seule fois dans le corpus est trop souvent une coquille.
MIN_COMPTE_SUITE = 2
# Groupe de deux mots propose d'un bloc (« hol ko », « hay so », « no feewi ») :
# seulement si le second suit le premier au moins 15 % du temps, et 20 fois.
GROUPE_PROBA_MIN = 0.15
GROUPE_COMPTE_MIN = 20

# Seuil au-dessus duquel un mot de l'ancien dictionnaire est repris : 10 et 50
# y sont des frequences par defaut, donnees a des formes vues une fois ou deux.
ANCIENNE_FREQUENCE_MIN = 50

APOSTROPHES = re.compile(r"['`‘ʼ]")
# L'alphabet pulaar : ni q, v, x, z, ni voyelles accentuees. Ce qui en sort vient
# des pages en francais ou en anglais melees au corpus.
MOT_VALIDE = re.compile(r"^[abcdefghijklmnoprstuwyɓɗŋñƴ’\-]+$")
DIGRAMMES_ETRANGERS = re.compile(r"th|sh|ph|ck|gh|ch")

# La syllabe pulaar : un mot commence par une consonne seule ou par une
# prenasale (mb, nd, ng, nj), et trois consonnes ne se suivent que devant une
# prenasale (janngo, ñaamnde). Le reste vient du swahili (mwenye, kwa), du
# bambara (npalanninw), du francais ou de l'anglais (londres, awards), ou du
# peul ecrit sans ñ (nyiiri).
PRENASALES = ("mb", "nd", "ng", "nj")
GRAPPE_DE_CONSONNES = re.compile(r"[^aeiou\-]+")
LETTRE_TRIPLEE = re.compile(r"(.)\1\1")
TROIS_VOYELLES = re.compile(r"[aeiou]{3,}")


def syllabes_pulaar(w):
    """Vrai si `w` suit la syllabe pulaar."""
    debut = GRAPPE_DE_CONSONNES.match(w)
    if debut and len(debut.group(0)) > 1 and debut.group(0) not in PRENASALES:
        return False
    for grappe in GRAPPE_DE_CONSONNES.findall(w):
        if len(grappe) >= 4 or (len(grappe) == 3 and grappe[1:] not in PRENASALES):
            return False
    if LETTRE_TRIPLEE.search(w):
        return False
    # Voyelles longues (aa, ee...) oui ; trois voyelles differentes a la suite, non.
    for voyelles in TROIS_VOYELLES.findall(w):
        if not re.search(r"([aeiou])\1", voyelles):
            return False
    return True


def nettoie(forme):
    """Forme de reference d'un mot : minuscules, hamza en ’, ɲ en ñ."""
    if not forme:
        return ""
    w = APOSTROPHES.sub("’", forme.strip()).lower().replace("ɲ", "ñ")
    w = w.strip("’-")
    if not w or len(w) > 30 or not MOT_VALIDE.match(w) or DIGRAMMES_ETRANGERS.search(w):
        return ""
    # Un mot pulaar porte toujours une voyelle : cd, ft, ml sont des abreviations.
    if not any(v in w for v in "aeiou"):
        return ""
    if not syllabes_pulaar(w):
        return ""
    return w


def lit_colonnes(chemin):
    """Lignes d'un fichier TSV, commentaires (#) ignores."""
    if not os.path.exists(chemin):
        print(f"  [absent] {chemin}")
        return
    with open(chemin, encoding="utf-8-sig") as f:
        for ligne in f:
            if ligne.startswith("#"):
                continue
            colonnes = ligne.rstrip("\r\n").split("\t")
            if colonnes and colonnes[0]:
                yield colonnes


def charge_rejetes():
    rejetes = set()
    for col in lit_colonnes(os.path.join(TAPPIRGAL_DIR, "listes_mots", "2_mots_rejetes.txt")):
        w = nettoie(col[0])
        if w:
            rejetes.add(w)
    return rejetes


def charge_frequences(nom):
    """Frequences d'une liste words_xx.txt de fulfuldekey (cle, forme, compte)."""
    frequences = {}
    for col in lit_colonnes(os.path.join(FULFULDEKEY_DICT, nom)):
        if len(col) >= 3:
            w = col[1].strip().lower()
            frequences[w] = max(frequences.get(w, 0), int(col[2] or 0))
    return frequences


def retire_mots_etrangers(mots):
    """Retire les mots plus frequents en francais ou en anglais qu'en pulaar.

    Seulement a partir de quatre lettres : no, so, to, on, en, ma, ne... sont
    des mots pulaar courants que les listes etrangeres portent aussi.
    """
    total = sum(mots.values())
    retires = 0
    for nom in ("words_fr.txt", "words_en.txt"):
        etrangers = charge_frequences(nom)
        total_etranger = sum(etrangers.values()) or 1
        for w in [w for w in mots if len(w) >= 4 and w in etrangers]:
            if mots[w] / total < etrangers[w] / total_etranger:
                del mots[w]
                retires += 1
    return retires


def charge_corrections():
    corrections = {}
    for col in lit_colonnes(os.path.join(TAPPIRGAL_DIR, "listes_mots", "3_lectures_corrigees.txt")):
        if len(col) >= 2:
            lue, retenue = nettoie(col[0]), nettoie(col[1])
            if lue and retenue and lue != retenue:
                corrections[lue] = retenue
    return corrections


def construit():
    print("Construction du dictionnaire Fulfulde...")
    rejetes = charge_rejetes()
    corrections = charge_corrections()
    print(f"  formes rejetees : {len(rejetes)}, lectures corrigees : {len(corrections)}")

    def forme(brut):
        w = nettoie(brut)
        w = corrections.get(w, w)
        return "" if w in rejetes else w

    # 1. Mots des lexiques mobiles
    mots = {}
    for col in lit_colonnes(os.path.join(FULFULDEKEY_DICT, "words_ff.txt")):
        if len(col) < 3:
            continue
        w = forme(col[1])
        if w:
            mots[w] = max(mots.get(w, 0), int(col[2] or 0))
    print(f"  mots fulfuldekey : {len(mots)}")
    print(f"  mots francais ou anglais retires : {retire_mots_etrangers(mots)}")

    # 2. Mots de l'ancien dictionnaire absents des lexiques mobiles : seulement
    # ceux qui y avaient une vraie frequence (formules, mots courants).
    ancien = {}
    if os.path.exists(ANCIEN_DICT):
        with open(ANCIEN_DICT, encoding="utf-8") as f:
            ancien = json.load(f)
    anciens_mots = {}
    for item in ancien.get("words", []):
        w = forme(item.get("w", ""))
        if w:
            anciens_mots[w] = max(anciens_mots.get(w, 0), item.get("f", 0))

    ajoutes = 0
    for w, f in anciens_mots.items():
        if w not in mots and f > ANCIENNE_FREQUENCE_MIN:
            mots[w] = f
            ajoutes += 1
    print(f"  mots repris de l'ancien dictionnaire : {ajoutes}")

    # 3. Suites de mots : comptes du corpus Tappirgal + ancien dictionnaire
    comptes = defaultdict(lambda: defaultdict(float))
    groupes = {}  # mot -> (proba, suite)
    chemin_bigrammes = os.path.join(TAPPIRGAL_DIR, "preprocessed", "bigrams.json")
    if os.path.exists(chemin_bigrammes):
        print("  lecture de bigrams.json (quelques secondes)...")
        with open(chemin_bigrammes, encoding="utf-8") as f:
            corpus = json.load(f)
        for cle, suites in corpus.items():
            k = forme(cle)
            if k not in mots:
                continue
            for s in suites:
                w = forme(s.get("word", ""))
                if w in mots and w != k:
                    comptes[k][w] += s.get("count", 0)
                    proba = s.get("prob", 0)
                    if (len(w) > 1 and proba >= GROUPE_PROBA_MIN and s.get("count", 0) >= GROUPE_COMPTE_MIN
                            and proba > groupes.get(k, (0, ""))[0]):
                        groupes[k] = (proba, w)
        del corpus
    else:
        print(f"  [absent] {chemin_bigrammes}")

    for cle, suites in ancien.get("ngrams", {}).items():
        k = forme(cle)
        if k not in mots:
            continue
        paires = suites.items() if isinstance(suites, dict) else ((s, 1) for s in suites)
        for s, c in paires:
            w = forme(s)
            if w in mots and w != k:
                comptes[k][w] += c

    # Les suites des lexiques mobiles completent, sans passer devant un compte.
    for col in lit_colonnes(os.path.join(FULFULDEKEY_DICT, "bigrams_ff.txt")):
        if len(col) < 2:
            continue
        k = forme(col[0])
        if k not in mots:
            continue
        for rang, s in enumerate(col[1].split()):
            w = forme(s)
            if w in mots and w != k and w not in comptes[k]:
                comptes[k][w] = MIN_COMPTE_SUITE - rang * 0.1

    ngrams = {}
    for k, suites in comptes.items():
        gardees = [w for w, c in sorted(suites.items(), key=lambda x: -x[1]) if c >= MIN_COMPTE_SUITE - 0.5]
        if gardees:
            ngrams[k] = gardees[:MAX_SUITES]
    print(f"  mots ayant des suites : {len(ngrams)}, groupes de deux mots : {len(groupes)}")

    liste = sorted(mots.items(), key=lambda x: (-x[1], x[0]))
    sortie = {
        "version": "3.0-fulfuldekey-tappirgal",
        "language": "ff-Latn",
        "description": "Pulaar/Fulfulde : lexiques fulfuldekey + corpus Tappirgal, formes rejetees retirees",
        "total_words": len(liste),
        "total_ngrams": len(ngrams),
        "words": [{"w": w, "f": f} for w, f in liste],
        "ngrams": ngrams,
        "groupes": {k: w for k, (_, w) in sorted(groupes.items())},
    }
    with open(DEST_DICT, "w", encoding="utf-8") as f:
        json.dump(sortie, f, ensure_ascii=False, separators=(",", ":"))
    taille = os.path.getsize(DEST_DICT) / 2**20
    print(f"Termine : {len(liste)} mots, {len(ngrams)} mots avec suites -> {DEST_DICT} ({taille:.1f} Mo)")


if __name__ == "__main__":
    construit()
