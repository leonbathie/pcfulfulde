#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests unitaires rigoureux pour l'autocomplétion Fulfulde :
- Teste directement la classe FulfuldeAutoCompleter de clavier_fulfulde_natif.py
- Vérifie la tolérance phonétique (b->ɓ, d->ɗ, y->ƴ, n->ŋ/ñ, ’ et accents)
- Vérifie la gestion sans perte des collisions multiples (ex: 'biddo' et 'ɓiɗɗo')
- Vérifie le boost contextuel N-gramme (avec et sans préfixe)
- Vérifie l'apprentissage dynamique et la vitesse O(k) de recherche Trie
- Vérifie le rejet strict des caractères isolés ou corrompus
"""

import sys
import os
import time

# Forcer UTF-8 sur Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Importer directement depuis clavier_fulfulde_natif
from clavier_fulfulde_natif import FulfuldeAutoCompleter, normalize_fulfulde_search

def run_tests():
    print("=" * 65)
    print("  SUITE DE TESTS - MOTEUR D'AUTOCOMPLÉTION FULFULDE / PULAAR")
    print("=" * 65)

    completer = FulfuldeAutoCompleter()
    print(f"[INIT] Dictionnaire chargé : {len(completer.words)} mots uniques, {len(completer.ngrams)} contextes N-Grammes")
    assert len(completer.words) >= 600, f"Dictionnaire trop petit ({len(completer.words)} mots)"

    # Test 1: Préfixe standard exact
    p1 = completer.predict("pula")
    print("Test 1 ('pula') :", p1)
    assert any("pulaar" in w for w in p1), "Devrait contenir 'pulaar'"

    # Test 2: Tolérance phonétique b -> ɓ
    p2 = completer.predict("fulb")
    print("Test 2 ('fulb' pour 'fulɓe') :", p2)
    assert any("fulɓe" in w for w in p2), "Devrait trouver 'fulɓe' même en tapant 'b' standard"

    # Test 3: Tolérance aux collisions multiples (biddo et ɓiɗɗo doivent tous deux exister !)
    # 'biddo' n'est plus dans le dictionnaire (lecture OCR rattachée à 'ɓiɗɗo') :
    # on l'apprend, et les deux formes de même clé doivent rester proposées.
    completer.learn_word("biddo")
    p3 = completer.predict("bid")
    print("Test 3 ('bid' - gestion des collisions) :", p3)
    assert "ɓiɗɗo" in p3, "Devrait contenir 'ɓiɗɗo'"
    assert "biddo" in p3, "Devrait AUSSI contenir 'biddo' sans écrasement par la collision"

    # Test 4: Tolérance phonétique d -> ɗ & b -> ɓ ('bib' pour 'ɓiɓɓe')
    p4 = completer.predict("bib")
    print("Test 4 ('bib' pour 'ɓiɓɓe') :", p4)
    assert any("ɓiɓɓe" in w for w in p4), "Devrait trouver 'ɓiɓɓe' en tapant 'bib'"

    # Test 5: Tolérance phonétique y -> ƴ
    p5 = completer.predict("yid")
    print("Test 5 ('yid' pour 'yiɗde' / 'yiɗi') :", p5)
    assert any("yiɗ" in w for w in p5), "Devrait trouver 'yiɗde' ou 'yiɗi'"

    # Test 6: Hamza / Apostrophe glottale ('saa' pour 'saa'a')
    p6 = completer.predict("saa")
    print("Test 6 ('saa' pour 'saa'a') :", p6)
    assert any("saa'a" in w or "saare" in w for w in p6), "Devrait trouver 'saa'a' ou 'saare'"

    # Test 7: Contexte N-Gramme sans préfixe
    p7 = completer.predict("", previous_word="jam")
    print("Test 7 (Après 'jam' sans préfixe) :", p7)
    assert "tan" in p7 or "waali" in p7, "Devrait suggérer 'tan' ou 'waali' après 'jam'"

    # Test 8: Contexte N-Gramme avec préfixe boosté
    p8 = completer.predict("w", previous_word="jam")
    print("Test 8 ('w' après 'jam' -> boost contextuel) :", p8)
    assert p8[0] == "waali", f"Devrait booster 'waali' en 1ère position, obtenu : {p8[0]}"

    # Test 9: Rejet strict des caractères isolés ou corrompus
    bad_chars = ['’', 'ɓ', 'ɗ', 'ŋ', 'ƴ', '-']
    for bad in bad_chars:
        assert bad not in completer.words, f"Le caractère isolé '{bad}' ne doit PAS être un mot du dictionnaire !"
    print("Test 9 (Filtrage des caractères non-mots) : VALIDÉ")

    # Test 10: Apprentissage continu en temps réel
    new_test_word = "karallaagal-kesal"
    completer.learn_word(new_test_word, previous_word="pulaar")
    learned = completer.predict("karal", previous_word="pulaar")
    print("Test 10 (Apprentissage 'karallaagal-kesal') :", learned)
    assert new_test_word in learned, "Le mot nouvellement appris doit être suggéré immédiatement"

    # Test 11: Benchmark de performance de recherche Trie (10 000 requêtes)
    start_time = time.perf_counter()
    queries = ["ful", "jam", "pula", "bid", "dem", "moƴ", "w", "ñ", "rew", "gor"]
    iterations = 1000
    for _ in range(iterations):
        for q in queries:
            completer.predict(q)
    total_time = time.perf_counter() - start_time
    total_queries = iterations * len(queries)
    avg_us = (total_time / total_queries) * 1_000_000
    print(f"Test 11 (Benchmark performance) : {total_queries} requêtes exécutées en {total_time:.3f}s ({avg_us:.1f} µs/requête)")
    assert avg_us < 500, f"La recherche est trop lente : {avg_us:.1f} µs (devrait être < 500 µs)"

    print("\n" + "=" * 65)
    print("  [SUCCÈS] TOUS LES 11 TESTS UNITAIRES ONT ÉTÉ VALIDÉS AVEC SUCCÈS !")
    print("=" * 65)

if __name__ == "__main__":
    run_tests()
