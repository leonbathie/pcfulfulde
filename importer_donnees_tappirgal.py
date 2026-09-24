# -*- coding: utf-8 -*-
"""
Script d'importation massive et de fusion des donnees de 'C:\\Users\\cheik\\Desktop\\donnee tappirgal'
vers le dictionnaire d'autocompletion du Clavier Fulfulde (Pulaar) Latin.
"""

import os
import sys
import re
import json
from collections import Counter, defaultdict

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEST_DICT = os.path.join(SCRIPT_DIR, "dictionary", "dict_ff_latin.json")
SRC_DIR = r"C:\Users\cheik\Desktop\donnee tappirgal"

# Regex pour mots Fulfulde authentiques
HAMZA_REGEX = re.compile(r"['`’‘ʼ]")
FULFULDE_WORD_REGEX = re.compile(r"[a-zA-ZɓƁɗƊŋŊƴƳñÑ’áéíóúÁÉÍÓÚ\-]+", re.UNICODE)

VALID_SINGLE_LETTERS = {'e', 'a', 'o', 'i'}

def clean_word(token):
    if not token or '?' in token: # Exclure les caracteres corrompus par OCR
        return None
    w = HAMZA_REGEX.sub("’", token.strip()).lower()
    w = re.sub(r"^[’\-]+|[’\-]+$", "", w)
    if not w:
        return None
    # Si longueur 1, seulement voyelles grammaticales
    if len(w) == 1 and w not in VALID_SINGLE_LETTERS:
        return None
    # Ne doit contenir que des lettres Fulfulde valides
    if not re.match(r"^[a-zɓɗŋƴñ’áéíóú\-]+$", w):
        return None
    # Eviter les tirets repetitifs
    if "--" in w:
        return None
    return w

def run_import():
    print("=" * 65)
    print("  IMPORTATION MASSIVE DES DONNEES TAPPIRGAL DANS L'AUTOCOMPLETION")
    print("=" * 65)

    words_counter = Counter()
    bigrams = defaultdict(Counter)

    # 1. Lexique de base a priorite absolue (Pulaar, Fulfulde, salutations, etc.)
    print("[1/5] Ingestion du lexique fondamental Pulaar...")
    from apprendre_corpus import BASE_FULFULDE_LEXICON
    for word, score in BASE_FULFULDE_LEXICON:
        w = clean_word(word)
        if w:
            words_counter[w] += score * 50 # Poids prioritaire absolu
    words_counter["biddo"] += 35000
    words_counter["bibbe"] += 35000
    print(f"  -> {len(BASE_FULFULDE_LEXICON)} mots fondamentaux charges en priorite absolue.")

    # N-grammes de base essentiels (salutations et formules)
    core_ngrams = {
        "jam": {"tan": 5000, "waali": 4000, "ñalli": 3500, "hiiri": 3000, "e": 2500},
        "on": {"jaaraama": 4000, "jarama": 3500},
        "a": {"jaaraama": 4000, "jarama": 3500},
        "ko": {"hono": 3000, "anndiraa": 2500, "woni": 2500},
        "e": {"nder": 5000, "leydi": 4000, "hitaande": 3500}
    }
    for prev, nxt_dict in core_ngrams.items():
        for nxt, cnt in nxt_dict.items():
            bigrams[prev][nxt] += cnt

    # 2. Importer le Saggitorde (dictionnaire de reference, 14 748 entrees)
    saggitorde_path = os.path.join(SRC_DIR, "preprocessed", "saggitorde_entries.json")
    if os.path.exists(saggitorde_path):
        print("[2/5] Ingestion du Saggitorde (lexique officiel)...")
        try:
            with open(saggitorde_path, "r", encoding="utf-8") as f:
                entries = json.load(f)
                added_sag = 0
                for entry in entries:
                    hw = entry.get("headword_lower", "")
                    cleaned = clean_word(hw)
                    if cleaned:
                        words_counter[cleaned] += 1200 # Score eleve pour vocabulaire de reference
                        added_sag += 1
                print(f"  -> {added_sag} entrees Saggitorde ingerees avec priorite elevee.")
        except Exception as e:
            print("  [WARN] Erreur Saggitorde :", e)

    # 3. Importer les listes de mots valides
    listes_dir = os.path.join(SRC_DIR, "listes_mots")
    if os.path.exists(listes_dir):
        print("[3/5] Ingestion des listes lexicales corrigees...")
        for fname in ["1_mots_neufs_admis.txt", "3_lectures_corrigees.txt", "4_fulfulde_est_lexique.txt"]:
            fpath = os.path.join(listes_dir, fname)
            if os.path.exists(fpath):
                cnt = 0
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        parts = line.split("\t")
                        w = clean_word(parts[0])
                        if w:
                            score = 500
                            if len(parts) > 1 and parts[1].isdigit():
                                score = max(50, min(1000, int(parts[1])))
                            words_counter[w] += score
                            cnt += 1
                print(f"  -> {fname} : {cnt} mots ajoutes.")

    # 4. Ingestion de corpus de texte pur (Pulaar.org, VoiceStudio, Benin, RFI)
    prep_dir = os.path.join(SRC_DIR, "preprocessed")
    corpus_files = [
        "corpus_pulaar_org_clean.txt",
        "corpus_voicestudio_clean.txt",
        "corpus_fulfuldebenin_clean.txt",
        "corpus_rfi_clean.txt",
    ]
    print("[4/5] Analyse des textes et calcul des transitions (Bigrammes)...")
    total_tokens = 0
    for cfile in corpus_files:
        cpath = os.path.join(prep_dir, cfile)
        if os.path.exists(cpath):
            print(f"  -> Traitement de {cfile}...")
            with open(cpath, "r", encoding="utf-8", errors="ignore") as f:
                prev_w = None
                for line in f:
                    tokens = FULFULDE_WORD_REGEX.findall(line)
                    for tok in tokens:
                        w = clean_word(tok)
                        if w:
                            words_counter[w] += 1
                            total_tokens += 1
                            if prev_w:
                                bigrams[prev_w][w] += 1
                            prev_w = w
                        else:
                            prev_w = None
    print(f"  -> {total_tokens:,} tokens traites.")

    # 5. Normalisation des scores et exportation du dictionnaire final
    print("[5/5] Structuration et compilation du dictionnaire d'autocompletion...")
    
    # Conserver les mots avec frequence >= 2 ou presents dans le dictionnaire de reference
    sorted_words = []
    max_freq = max(words_counter.values()) if words_counter else 1
    
    for word, raw_f in words_counter.most_common():
        # Score normalise entre 10 et 1000
        norm_score = max(10, min(1000, int((raw_f / max_freq) * 1000))) if raw_f > 1 else 50
        sorted_words.append({"w": word, "f": norm_score})

    # Filtrer et compacter les bigrammes pour garder les plus pertinents
    compact_ngrams = {}
    for prev, nxt_counter in bigrams.items():
        if words_counter[prev] >= 2:
            top_next = {}
            for nxt, cnt in nxt_counter.most_common(12):
                if cnt >= 2:
                    top_next[nxt] = cnt
            if top_next:
                compact_ngrams[prev] = top_next

    final_payload = {
        "version": "2.0-tappirgal-extended",
        "total_words": len(sorted_words),
        "total_ngrams": len(compact_ngrams),
        "words": sorted_words,
        "ngrams": compact_ngrams
    }

    os.makedirs(os.path.dirname(DEST_DICT), exist_ok=True)
    with open(DEST_DICT, "w", encoding="utf-8") as f:
        json.dump(final_payload, f, ensure_ascii=False, indent=2)

    # Copier egalement dans src/dictionary/ pour le frontend React
    src_dict = os.path.join(SCRIPT_DIR, "src", "dictionary", "dict_ff_latin.json")
    os.makedirs(os.path.dirname(src_dict), exist_ok=True)
    with open(src_dict, "w", encoding="utf-8") as f:
        json.dump(final_payload, f, ensure_ascii=False, indent=2)

    print("=" * 65)
    print("  IMPORTATION REUSSIE AVEC SUCCES !")
    print(f"  Total mots uniques dans le dictionnaire : {len(sorted_words):,}")
    print(f"  Total contextes N-grammes (associations) : {len(compact_ngrams):,}")
    print(f"  Enregistre dans : {DEST_DICT}")
    print(f"  Enregistre dans : {src_dict}")
    print("=" * 65)

if __name__ == "__main__":
    run_import()
