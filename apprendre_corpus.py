#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Outil d'apprentissage et d'enrichissement de corpus pour le Clavier Fulfulde (Pulaar) Latin.
Permet d'extraire automatiquement le vocabulaire, les fréquences et les n-grammes (bigrammes)
à partir de textes bruts, de listes de mots ou de fichiers volumineux (.txt, .json, .csv).
"""

import os
import sys
import re
import json
from collections import Counter, defaultdict

# Forcer la sortie UTF-8 sur Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Normalisation des apostrophes glottales Fulfulde
HAMZA_REGEX = re.compile(r"['`’‘ʼ]")
FULFULDE_WORD_REGEX = re.compile(r"[a-zA-ZɓƁɗƊŋŊƴƳñÑ’áéíóúÁÉÍÓÚ\-]+", re.UNICODE)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DICT_PATH = os.path.join(SCRIPT_DIR, "dictionary", "dict_ff_latin.json")
CUSTOM_DICT_PATH = os.path.join(SCRIPT_DIR, "dictionary", "custom_dict.json")
CORPUS_DIR = os.path.join(SCRIPT_DIR, "corpus")

# Base de vocabulaire Fulfulde / Pulaar étendu de référence (littéraire, parlé, tous dialectes)
BASE_FULFULDE_LEXICON = [
    # Formules, salutations et civilités
    ("jam", 1000), ("tan", 950), ("waali", 940), ("ñalli", 930), ("hiiri", 920),
    ("noy", 980), ("mbadaa", 850), ("waadi", 860), ("jaaraama", 920), ("njarama", 900),
    ("belɗo", 870), ("a jaraama", 890), ("on jaaraama", 910), ("barke", 840), ("kori", 830),
    ("foof", 790), ("ko", 960), ("e", 950), ("en", 920), ("on", 910), ("min", 905),
    
    # Pronoms et indices de personne
    ("miin", 880), ("aan", 875), ("kanko", 890), ("kamɓe", 885), ("minon", 830), ("onon", 840),
    ("enɗon", 820), ("mido", 870), ("aɗa", 865), ("oɗo", 860), ("eɓe", 855), ("eden", 850),
    ("odon", 820), ("mi", 940), ("a", 930), ("o", 920), ("ɓe", 915), ("men", 890), ("maa", 880),
    ("makko", 875), ("maɓɓe", 870), ("amen", 850), ("mon", 845),
    
    # Pulaar / Identité / Culture
    ("pulaar", 995), ("fulfulde", 998), ("fulɓe", 990), ("pullo", 985), ("haalpulaar", 940),
    ("fuuta", 920), ("tooro", 910), ("jallon", 890), ("maasina", 880), ("adamawa", 870),
    ("demngal", 930), ("ɗemngal", 940), ("gandal", 920), ("gannde", 890), ("deftere", 910),
    ("defte", 880), ("tariika", 860), ("daartol", 870), ("aada", 890), ("pine", 840),
    
    # Famille et société
    ("ɓiɗɗo", 950), ("ɓiɓɓe", 940), ("baaba", 930), ("neene", 925), ("inna", 910),
    ("mawɗo", 920), ("mawɓe", 915), ("debbo", 940), ("rewɓe", 935), ("gorko", 940),
    ("worɓe", 935), ("suka", 910), ("sukaaɓe", 905), ("kodo", 860), ("hoɓɓe", 850),
    ("almuudo", 870), ("almuuɓe", 860), ("moodibo", 880), ("moodiɓɓe", 870), ("sehil", 880),
    ("sehilaaɓe", 870), ("musidɗo", 860), ("musidɓe", 850), ("banndiraawo", 890),
    ("banndiraaɓe", 885), ("koreeji", 840), ("jom-galle", 860), ("jom-suudu", 850),
    ("inna-galle", 840), ("taaniiko", 830), ("taaniraaɓe", 825), ("kaaw", 810),
    ("bappaño", 805), ("yaaye", 820), ("goggo", 815),
    
    # Habitat et quotidien
    ("wuro", 930), ("gure", 900), ("galle", 920), ("galleeji", 880), ("saare", 890),
    ("ca'e", 860), ("suudu", 910), ("cuuɗi", 890), ("damal", 860), ("dammugal", 855),
    ("falanteere", 820), ("leeso", 840), ("leese", 810), ("luumo", 890), ("luume", 870),
    ("laawol", 920), ("laabi", 890), ("loonde", 800), ("laɓi", 830), ("faynde", 810),
    ("barme", 790), ("mbottaari", 840), ("hiraande", 850), ("kacitaari", 830),
    ("nyaamdu", 890), ("ñamri", 880), ("kosam", 910), ("biraaɗam", 870), ("kaadam", 860),
    ("nebbam", 850), ("ndiyam", 940), ("tii", 820), ("kafe", 810), ("sukkar", 830),
    ("maaro", 870), ("gawri", 860), ("baske", 800), ("teew", 880), ("liingu", 870),
    ("liɗɗi", 860),
    
    # Animaux et nature
    ("nagge", 950), ("na'i", 945), ("mbeewa", 890), ("be'i", 880), ("baali", 890),
    ("mbaalu", 885), ("puccu", 900), ("pucci", 895), ("mbabba", 840), ("bamɗi", 830),
    ("gelooɓa", 850), ("gelooɗi", 840), ("ndoondi", 820), ("henndu", 910), ("kene", 860),
    ("leydi", 940), ("leyɗe", 890), ("asamaan", 910), ("naange", 930), ("lewru", 920),
    ("koode", 880), ("ladde", 900), ("lekki", 910), ("leɗɗe", 890), ("ngesa", 890),
    ("gese", 880), ("huɗo", 870), ("dabbaaji", 860), ("colli", 850), ("sundu", 820),
    ("ɓowngii", 780), ("ngilngu", 770), ("mboodi", 830), ("booli", 810), ("rawaandu", 850),
    ("dawaaɗi", 840), ("ullundu", 820),
    
    # Corps et santé
    ("hoore", 930), ("kooɗe", 860), ("yeeso", 920), ("gite", 930), ("yitere", 910),
    ("nofru", 890), ("noppi", 885), ("hunuko", 900), ("ñiiye", 870), ("daande", 910),
    ("ɓernde", 940), ("ɓerɗe", 890), ("jungo", 930), ("juuɗe", 925), ("koyngal", 920),
    ("koyɗe", 915), ("reedu", 890), ("ɓanndu", 910), ("ƴiiƴam", 900), ("cellal", 930),
    ("ñawu", 870), ("ñawɗo", 860), ("lekki-ñaw", 840), ("loktor", 820),
    
    # Verbes et actions très fréquents (formes de base et conjuguées)
    ("yiɗde", 950), ("yiɗi", 960), ("ngiɗi", 910), ("yiɗaa", 890),
    ("anndude", 940), ("anndi", 950), ("nganndi", 920), ("anndaa", 910),
    ("yahde", 940), ("yahi", 945), ("njahi", 910), ("yaaha", 900), ("yaahu", 880),
    ("warde", 930), ("wari", 935), ("ngari", 915), ("wonaa", 920),
    ("arde", 930), ("ari", 940), ("ar", 900), ("ngaree", 890),
    ("wonde", 950), ("woni", 960), ("ngoni", 920), ("wonande", 880),
    ("waɗde", 940), ("waɗi", 945), ("mbaɗi", 910), ("waɗude", 890),
    ("haalde", 930), ("haali", 935), ("kaali", 900), ("haala", 920),
    ("janngude", 940), ("janngi", 945), ("njanngi", 905), ("janngoowo", 880),
    ("winndude", 930), ("winndi", 935), ("mbinndi", 890), ("windude", 870),
    ("heɗaade", 900), ("heɗii", 895), ("keɗii", 870), ("nannde", 920), ("nani", 930),
    ("yi'de", 920), ("yi'i", 925), ("ji'i", 890), ("heɓde", 930), ("heɓi", 935), ("keɓi", 905),
    ("jooɗaade", 910), ("jooɗii", 915), ("njooɗii", 890), ("jooɗo", 880),
    ("ummaade", 900), ("ummii", 905), ("ngummii", 880),
    ("hootde", 890), ("hooti", 895), ("kooti", 870),
    ("remde", 900), ("remi", 905), ("demoowo", 880), ("remooɓe", 870),
    ("soodde", 910), ("soodi", 915), ("coodi", 880),
    ("yeeyde", 890), ("yeeyi", 895), ("geeyi", 870),
    ("gollude", 920), ("golli", 925), ("ngolli", 900), ("golle", 930), ("gollal", 890),
    ("doggude", 870), ("doggi", 875),
    ("ñaamde", 930), ("ñaami", 935), ("ñami", 900), ("ñamde", 880),
    ("yarde", 920), ("yari", 925), ("njari", 890),
    ("wallude", 910), ("walli", 915), ("mballi", 885), ("ballal", 900),
    ("sellude", 900), ("selli", 910), ("sellitii", 880),
    ("tiiɗnude", 870), ("tiiɗnaade", 865), ("jaɓde", 890), ("jaɓi", 895),
    ("suuɗde", 850), ("suuɗi", 855), ("fiyde", 840), ("fiyi", 845),
    ("durngol", 860), ("durde", 870), ("gaynaako", 890), ("faynude", 830),
    ("tinndinde", 850), ("heblude", 860), ("weltinde", 870), ("weltaare", 910),
    ("yaafude", 880), ("yaafaade", 875), ("humpitaade", 860), ("tintinde", 850),
    ("resde", 860), ("hakkilude", 880), ("hakkille", 920),
    
    # Adjectifs et qualificatifs
    ("moƴƴi", 950), ("moƴƴo", 940), ("moƴƴere", 910), ("bonɗo", 890), ("boni", 885),
    ("bonannde", 860), ("mawɗo", 930), ("mawni", 920), ("famɗo", 900), ("famɗi", 895),
    ("heewi", 940), ("keewɗo", 900), ("ɓuri", 950), ("ɓurde", 920),
    ("keso", 910), ("hesɗi", 890), ("kiɗɗo", 880), ("hiɗɗi", 870),
    ("ɗanewol", 880), ("ɗaneejo", 890), ("ɓaleewol", 870), ("ɓaleejo", 880),
    ("boɗewol", 860), ("boɗeejo", 870), ("sayee", 850),
    ("wodɗi", 880), ("ɓadii", 890), ("yaawi", 900), ("leeli", 860),
    ("tiiɗi", 910), ("newii", 880), ("weli", 920), ("kalluɗum", 870),
    
    # Nombres et repères temporels
    ("go'o", 950), ("ɗiɗi", 940), ("tati", 930), ("nai", 920), ("jowi", 910),
    ("jeego'o", 890), ("jeeɗiɗi", 885), ("jeetati", 880), ("jeenay", 875),
    ("sappo", 930), ("noogay", 910), ("capanɗe", 890), ("teemedere", 900),
    ("ujunere", 890), ("miliyoŋ", 850),
    ("hannde", 950), ("jaŋngo", 930), ("janngo", 925), ("haŋki", 910),
    ("hecci-haŋki", 860), ("fajiri", 900), ("kikiiɗe", 880), ("jemma", 910),
    ("ñalawma", 920), ("ñalnde", 930), ("hitaande", 920), ("duuɓi", 910),
    ("yontere", 900), ("lewru", 920), ("saa'a", 910), ("waktu", 900),
    
    # Mots outils, adverbes, connecteurs
    ("ɗon", 960), ("ɗoo", 950), ("to", 940), ("haa", 950), ("nde", 930),
    ("kono", 920), ("so", 910), ("sabu", 890), ("ngam", 930), ("hono", 900),
    ("nih", 880), ("noon", 920), ("ni", 890), ("kadi", 940), ("tigi", 910),
    ("kasen", 870), ("woni", 940), ("gila", 900), ("fof", 940), ("fuu", 935),
    ("kala", 930), ("seedɗa", 890), ("buy", 880), ("heewde", 890),
    ("ɗum", 960), ("ngol", 920), ("ka", 900), ("ki", 880), ("ndeerewol", 850),
    
    # Vocabulaire contemporain, éducation, sciences et institutions
    ("ordinatör", 830), ("ordinateer", 840), ("laylaytol", 860), ("enternet", 850),
    ("geese", 840), ("duɗal", 910), ("duɗe", 890), ("janngirde", 900), ("jannginoowo", 910),
    ("jannginooɓe", 900), ("karallaagal", 880), ("kesam-hesaagu", 850), ("jaaɓi-haaɗtirde", 870),
    ("porogaraam", 840), ("binndol", 900), ("binndanɗe", 880), ("alkule", 890),
    ("kelme", 880), ("konngol", 910), ("konnguɗi", 890), ("bolle", 880),
    ("pinal", 910), ("pine", 880), ("ñeeñal", 890), ("ñeeñe", 860),
    ("laamu", 930), ("laamɗo", 920), ("laamɓe", 900), ("dental", 910),
    ("dente", 880), ("fedde", 900), ("pelle", 880), ("kawral", 890),
    ("ngootaagu", 890), ("deeƴre", 880), ("jamfa", 820), ("jaambaro", 870),
    ("jaambareeɓe", 860), ("jaaynde", 890), ("jaayndeeji", 870), ("kabaaru", 910),
    ("habaruuji", 890), ("rajo", 860), ("tele", 850), ("kaye", 860),
    ("binndirgal", 880), ("binndirɗe", 860), ("semmbe", 900), ("doole", 910),
    ("ƴellitaare", 920), ("ƴellitde", 900), ("fannu", 880), ("geɗe", 890),
    ("batte", 880), ("sawru", 870), ("cabbi", 850), ("waylude", 880),
    ("waylo-waylo", 870), ("sella", 890), ("bawgal", 890), ("baawɗo", 880),
    ("baawɓe", 870), ("senegaal", 900), ("ginne", 890), ("maali", 890),
    ("moritani", 880), ("naajeeriya", 890), ("kamerun", 870), ("nijer", 870),
    ("gambi", 860), ("burkina", 850), ("afrik", 910), ("aduna", 930)
]

# N-grammes de contexte riches (précédent -> suivants fréquents)
BASE_NGRAMS = {
    "jam": ["tan", "waali", "ñalli", "hiiri", "e", "kalluɗum", "kori", "wonaa", "duumi"],
    "noy": ["mbadaa", "waadi", "innde", "wuro", "galle", "golle", "kori", "feere", "cellal"],
    "ko": ["honi", "heewi", "woni", "ngol", "ɗum", "moƴƴi", "kanko", "aan", "miin", "baaba", "neene", "gonga"],
    "on": ["jaaraama", "belɗo", "njarama", "jaraama", "ngonii", "mbelaama", "ngettiima", "keɓii"],
    "en": ["ngarii", "njahii", "mbelii", "ngoni", "kori", "njaaraama", "ndendii", "njanngii"],
    "mido": ["yiɗi", "anndi", "janga", "wondi", "yaaha", "waawi", "yidi", "heɗoo", "remude"],
    "aɗa": ["anndi", "yidi", "heewi", "sellitii", "waawi", "wondi", "haala", "jannga"],
    "oɗo": ["wondi", "yaaha", "woni", "heewi", "yidi", "haala", "remude", "selli"],
    "eɓe": ["ngoni", "njaha", "ngara", "njaaraama", "njannga", "mballa"],
    "fulɓe": ["na'i", "leydi", "pulaar", "gure", "ladde", "aduna", "fuuta", "men"],
    "pullo": ["moƴƴo", "mawɗo", "kala", "gorko", "debbo", "gandal"],
    "pulaar": ["fulfulde", "yoo", "heewi", "ko", "demngal", "e", "men", "neene"],
    "fulfulde": ["latin", "adlam", "demngal", "men", "ko", "e", "leydi"],
    "demngal": ["pulaar", "fulfulde", "men", "baaba", "neene", "ngal"],
    "ɗemngal": ["pulaar", "fulfulde", "men", "baaba", "neene", "ngal"],
    "gandal": ["ngal", "kesal", "deftere", "aduna", "fulɓe", "men"],
    "deftere": ["nde", "aduna", "ndeerewol", "tariika", "mawnde", "qur'aana"],
    "leydi": ["men", "senegaal", "ginne", "maali", "moritani", "naajeeriya", "fuuta"],
    "wuro": ["ngo", "men", "mawngo", "fulɓe", "laamɗo"],
    "galle": ["o", "men", "mawɗo", "baaba", "neene"],
    "suudu": ["ndu", "men", "mawndu", "cuuɗi", "janngirde"],
    "nagge": ["nge", "biraange", "mawnge", "na'i"],
    "ɓiɗɗo": ["pullo", "gorko", "debbo", "am", "maa", "makko", "moƴƴo"],
    "baaba": ["am", "maa", "makko", "men", "kanko", "mawɗo"],
    "neene": ["am", "maa", "makko", "men", "moƴƴo"],
    "kori": ["jam", "tan", "cellal", "aɗa", "oɗo"],
    "hannde": ["ko", "jam", "e", "min", "kamɓe", "kanko"],
    "janngo": ["subaka", "e", "so", "alla", "jaɓii", "min"],
    "alla": ["yoo", "hokku", "jaaraama", "wallu", "barkin", "toowɗo"],
    "yo": ["alla", "jam", "duumo", "wurdu", "barkin"],
    "moƴƴi": ["sabu", "ko", "sanme", "kadi", "no", "feewi"],
    "ɗon": ["e", "to", "haa", "woni", "kono"],
    "ɗum": ["ɗoo", "ko", "gonga", "moƴƴi", "heewi"],
    "ngam": ["alla", "gandal", "heɓde", "anndude", "pulaar"],
    "haa": ["hannde", "janngo", "laawol", "wuro", "yaha"],
    "so": ["alla", "jaɓii", "a", "o", "en", "tawi"],
    "kono": ["ko", "o", "min", "kamɓe", "aɗa"]
}

VALID_SINGLE_LETTER_WORDS = {'e', 'a', 'o', 'i'}

def clean_fulfulde_word(raw_word):
    """Nettoie et normalise un mot Fulfulde."""
    if not raw_word:
        return ""
    # Remplacer les variantes d'apostrophes par ’
    w = HAMZA_REGEX.sub("’", raw_word.strip())
    # Supprimer ponctuations et séparateurs résiduels en début/fin
    w = w.strip(".,;:!?\"()[]{}/\\<>«»_~*^'’`‘ʼ-").lower()
    if not w:
        return ""
    # Filtrer les lettres isolées qui ne sont pas de véritables mots
    if len(w) == 1 and w not in VALID_SINGLE_LETTER_WORDS:
        return ""
    # Le mot doit contenir au moins une lettre alphabétique
    if not any(c.isalpha() for c in w):
        return ""
    return w

def extract_corpus_from_text(text):
    """
    Extrait les mots, leurs fréquences et les bigrammes à partir d'un texte Fulfulde.
    Prend en compte les lettres spéciales Fulfulde (ɓ, ɗ, ŋ, ƴ, ñ, ’).
    """
    words_counter = Counter()
    bigrams = defaultdict(Counter)
    
    # Découpage par phrases/lignes pour éviter les faux n-grammes inter-phrases
    sentences = re.split(r'[\.\n\?!;:]+', text)
    
    for sentence in sentences:
        tokens = FULFULDE_WORD_REGEX.findall(sentence)
        cleaned_tokens = [clean_fulfulde_word(t) for t in tokens if len(clean_fulfulde_word(t)) > 0]
        
        for i, word in enumerate(cleaned_tokens):
            words_counter[word] += 1
            if i > 0:
                prev_word = cleaned_tokens[i - 1]
                bigrams[prev_word][word] += 1
                
    return words_counter, bigrams

def merge_with_base_dictionary(new_words_counter, new_bigrams, output_path=DICT_PATH):
    """
    Fusionne un nouveau corpus avec le dictionnaire existant.
    """
    # 1. Charger ou initialiser le dictionnaire de base
    existing_words = {}
    existing_ngrams = {}
    existing_groupes = {}
    
    if os.path.exists(output_path):
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data.get("words", []):
                    existing_words[item["w"]] = item["f"]
                existing_ngrams = data.get("ngrams", {})
                existing_groupes = data.get("groupes", {})
        except Exception as e:
            print(f"⚠️ Avertissement lors du chargement de {output_path}: {e}")

    # 2. Intégrer le lexique étendu de base
    for w, f in BASE_FULFULDE_LEXICON:
        cw = clean_fulfulde_word(w)
        if cw not in existing_words or existing_words[cw] < f:
            existing_words[cw] = f
            
    for prev, next_list in BASE_NGRAMS.items():
        p_clean = clean_fulfulde_word(prev)
        if p_clean not in existing_ngrams:
            existing_ngrams[p_clean] = []
        for n in next_list:
            n_clean = clean_fulfulde_word(n)
            if n_clean not in existing_ngrams[p_clean]:
                existing_ngrams[p_clean].append(n_clean)

    # 3. Fusionner les nouvelles fréquences du corpus utilisateur
    max_input_freq = max(new_words_counter.values()) if new_words_counter else 1
    for word, count in new_words_counter.items():
        # Normaliser le boost de fréquence entre 20 et 900
        relative_boost = min(900, int((count / max_input_freq) * 700) + 100)
        if word in existing_words:
            # Jamais de baisse : les mots courants du dictionnaire depassent 1000.
            existing_words[word] = max(existing_words[word],
                                       min(1000, existing_words[word] + relative_boost // 2))
        else:
            existing_words[word] = relative_boost

    # 4. Fusionner les nouveaux bigrammes
    for prev, next_counter in new_bigrams.items():
        if prev not in existing_ngrams:
            existing_ngrams[prev] = []
        
        # Obtenir les mots suivants triés par fréquence
        sorted_next = [w for w, _ in next_counter.most_common(10)]
        for w in sorted_next:
            if w not in existing_ngrams[prev]:
                existing_ngrams[prev].append(w)
        # Limiter à 10 suggestions par mot de contexte
        existing_ngrams[prev] = existing_ngrams[prev][:10]

    # 5. Trier les mots par fréquence décroissante
    sorted_words = sorted(
        [{"w": w, "f": f} for w, f in existing_words.items() if len(w) > 0],
        key=lambda x: x["f"],
        reverse=True
    )

    result_payload = {
        "version": "2.0.0",
        "language": "ff-Latn",
        "description": "Dictionnaire de fréquence enrichi et modèle n-gramme pour le Fulfulde (Pulaar/Fulfulde) Latin",
        "total_words": len(sorted_words),
        "words": sorted_words,
        "ngrams": existing_ngrams,
        "groupes": existing_groupes
    }

    # Sauvegarder
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result_payload, f, ensure_ascii=False, indent=2)

    print(f"[OK] Dictionnaire mis a jour avec succes : {output_path}")
    print(f"[STATS] Total mots uniques : {len(sorted_words)}")
    print(f"[STATS] Mots de contexte N-Grammes : {len(existing_ngrams)}")
    return result_payload

def learn_from_file_or_directory(path):
    """Lit un fichier ou un dossier complet et apprend tous les mots."""
    all_text = []
    direct_words = Counter()
    direct_bigrams = defaultdict(Counter)
    
    def process_file(filepath):
        lower_name = filepath.lower()
        if lower_name.endswith('.json'):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and 'words' in data:
                        # Dictionnaire structuré
                        for item in data.get('words', []):
                            w = clean_fulfulde_word(item.get('w', ''))
                            if w:
                                direct_words[w] += item.get('f', 100)
                        for prev, next_list in data.get('ngrams', {}).items():
                            p_clean = clean_fulfulde_word(prev)
                            if p_clean and isinstance(next_list, list):
                                for n in next_list:
                                    n_clean = clean_fulfulde_word(n)
                                    if n_clean:
                                        direct_bigrams[p_clean][n_clean] += 1
                        print(f"  + JSON structuré intégré : {os.path.basename(filepath)}")
                        return
                    elif isinstance(data, list):
                        for item in data:
                            if isinstance(item, str):
                                w = clean_fulfulde_word(item)
                                if w:
                                    direct_words[w] += 100
                            elif isinstance(item, dict) and 'w' in item:
                                w = clean_fulfulde_word(item['w'])
                                if w:
                                    direct_words[w] += item.get('f', 100)
                        print(f"  + Liste JSON intégrée : {os.path.basename(filepath)}")
                        return
            except Exception as e:
                print(f"  - Erreur parsing JSON {filepath} : {e}")

        # Fichier texte brut (.txt, .csv, etc.)
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                all_text.append(f.read())
                print(f"  + Inclus : {os.path.basename(filepath)}")
        except Exception as e:
            print(f"  - Erreur {filepath} : {e}")

    if os.path.isfile(path):
        print(f"[INFO] Analyse du fichier : {path}")
        process_file(path)
    elif os.path.isdir(path):
        print(f"[INFO] Analyse du dossier de corpus : {path}")
        for root, _, files in os.walk(path):
            for file in files:
                if file.lower().endswith((".txt", ".json", ".csv", ".tsv")):
                    process_file(os.path.join(root, file))
    else:
        print(f"[ERREUR] Chemin introuvable : {path}")
        return

    full_corpus = "\n".join(all_text)
    words_counter, bigrams = extract_corpus_from_text(full_corpus)
    
    # Fusionner avec les mots directs issus des JSON
    for w, count in direct_words.items():
        words_counter[w] += count
    for prev, next_counter in direct_bigrams.items():
        for n, count in next_counter.items():
            bigrams[prev][n] += count

    print(f"[INFO] Mots bruts extraits : {sum(words_counter.values())} (uniques : {len(words_counter)})")
    print(f"[INFO] Paires de bigrammes identifiees : {len(bigrams)}")
    
    merge_with_base_dictionary(words_counter, bigrams)

def main():
    print("=" * 65)
    print("  GESTIONNAIRE DE CORPUS ET AUTOCOMPLÉTION FULFULDE (PULAAR)")
    print("=" * 65)
    
    if len(sys.argv) > 1:
        target = sys.argv[1]
        learn_from_file_or_directory(target)
        return

    # Si aucun argument n'est fourni, vérifier si le dossier corpus existe
    if os.path.exists(CORPUS_DIR) and len(os.listdir(CORPUS_DIR)) > 0:
        print(f"Dossier 'corpus/' détecté. Traitement automatique...")
        learn_from_file_or_directory(CORPUS_DIR)
    else:
        print("Initialisation et régénération du grand corpus Fulfulde de base...")
        os.makedirs(CORPUS_DIR, exist_ok=True)
        # Générer le dictionnaire étendu de base
        merge_with_base_dictionary(Counter(), defaultdict(Counter))
        print("\nAstuce : Vous pouvez placer vos fichiers textes (.txt) dans le dossier 'corpus/'")
        print("puis relancer ce script pour enrichir instantanément l'autocomplétion !")

if __name__ == "__main__":
    main()
