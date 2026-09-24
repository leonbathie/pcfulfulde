import baseDictData from '../../dictionary/dict_ff_latin.json';

export interface WordEntry {
  w: string;
  f: number;
}

export interface DictionaryData {
  version: string;
  language: string;
  description?: string;
  total_words?: number;
  words: WordEntry[];
  ngrams: Record<string, string[]>;
}

export interface AutocompleteSuggestion {
  word: string;
  score: number;
  isNgram: boolean;
  isExactPrefix: boolean;
}

// Nettoyage et normalisation phonétique pour tolérance clavier AZERTY/QWERTY standard
export function normalizeFulfuldeSearch(str: string): string {
  if (!str) return '';
  return str
    .toLowerCase()
    .trim()
    .replace(/ɓ/g, 'b')
    .replace(/ɗ/g, 'd')
    .replace(/ƴ/g, 'y')
    .replace(/ŋ/g, 'n')
    .replace(/ñ/g, 'n')
    .replace(/[’'`‘ʼ]/g, '')
    .replace(/[áàâäā]/g, 'a')
    .replace(/[éèêëē]/g, 'e')
    .replace(/[íìîïī]/g, 'i')
    .replace(/[óòôöō]/g, 'o')
    .replace(/[úùûüū]/g, 'u');
}

export function cleanFulfuldeWord(word: string): string {
  if (!word) return '';
  const w = word
    .trim()
    .replace(/['`‘ʼ]/g, '’')
    .replace(/^[.,;:!?"()\[\]{}«»_~*^\-'’`‘ʼ]+|[.,;:!?"()\[\]{}«»_~*^\-'’`‘ʼ]+$/g, '')
    .toLowerCase();
  if (!w) return '';
  // Filtrer les caractères isolés non-mots
  if (w.length === 1 && !['e', 'a', 'o', 'i'].includes(w)) return '';
  if (!/[a-zɓɗŋñƴáéíóú]/i.test(w)) return '';
  return w;
}

class TrieNode {
  children: Map<string, TrieNode> = new Map();
  // Permet de stocker plusieurs mots avec leurs fréquences à un même nœud (tolérance aux collisions)
  words: Map<string, number> = new Map();
}

export class FulfuldePredictionEngine {
  private exactRoot = new TrieNode();
  private normalizedRoot = new TrieNode();
  private wordMap: Map<string, number> = new Map();
  private ngrams: Map<string, string[]> = new Map();
  private customWords: Set<string> = new Set();
  private customNgrams: Map<string, Set<string>> = new Map();

  constructor() {
    this.loadBaseDictionary();
    this.loadFromStorage();
  }

  private loadBaseDictionary() {
    try {
      const data = baseDictData as unknown as DictionaryData;
      if (data && Array.isArray(data.words)) {
        for (const item of data.words) {
          if (item && item.w) {
            this.insertWord(item.w, item.f || 100, false);
          }
        }
      }
      if (data && data.ngrams) {
        for (const [key, nextWords] of Object.entries(data.ngrams)) {
          const cleanKey = cleanFulfuldeWord(key);
          if (cleanKey) {
            const cleanedNext = nextWords.map(cleanFulfuldeWord).filter(Boolean);
            this.ngrams.set(cleanKey, cleanedNext);
          }
        }
      }
    } catch (err) {
      console.error('Erreur lors du chargement du dictionnaire Fulfulde de base:', err);
    }
  }

  private insertWord(word: string, frequency: number, isCustom = false) {
    const cleanWord = cleanFulfuldeWord(word);
    if (!cleanWord || cleanWord.length < 1) return;

    // Stocker la fréquence maximale
    const currentFreq = this.wordMap.get(cleanWord) || 0;
    const finalFreq = Math.max(currentFreq, frequency);
    this.wordMap.set(cleanWord, finalFreq);

    if (isCustom) {
      this.customWords.add(cleanWord);
    }

    // 1. Insertion dans l'arbre exact
    let node = this.exactRoot;
    for (const ch of cleanWord) {
      if (!node.children.has(ch)) {
        node.children.set(ch, new TrieNode());
      }
      node = node.children.get(ch)!;
    }
    node.words.set(cleanWord, finalFreq);

    // 2. Insertion dans l'arbre normalisé (permet de taper 'b' pour 'ɓ', 'd' pour 'ɗ', etc.)
    const norm = normalizeFulfuldeSearch(cleanWord);
    let normNode = this.normalizedRoot;
    for (const ch of norm) {
      if (!normNode.children.has(ch)) {
        normNode.children.set(ch, new TrieNode());
      }
      normNode = normNode.children.get(ch)!;
    }
    normNode.words.set(cleanWord, finalFreq);
  }

  public predict(currentPrefix: string, previousWord?: string, limit: number = 5): string[] {
    const cleanPrefix = cleanFulfuldeWord(currentPrefix);
    const cleanPrev = previousWord ? cleanFulfuldeWord(previousWord) : undefined;

    // CAS 1: Préfixe vide -> Prédictions contextuelles basées sur le mot précédent (N-grammes)
    if (!cleanPrefix) {
      if (cleanPrev) {
        const nextWords = this.getNgramNextWords(cleanPrev);
        if (nextWords && nextWords.length > 0) {
          return nextWords.slice(0, limit);
        }
      }
      // Suggestions par défaut de salutation si aucun mot précédent
      const defaultGreetings = ['jam', 'noy', 'waali', 'ñalli', 'hiiri', 'pulaar', 'fulfulde'];
      return defaultGreetings.slice(0, limit);
    }

    const candidates = new Map<string, AutocompleteSuggestion>();
    const prevNgrams = cleanPrev ? new Set(this.getNgramNextWords(cleanPrev)) : new Set<string>();

    // 1. Recherche par préfixe exact
    const exactMatches = this.searchInTrie(this.exactRoot, cleanPrefix);
    for (const { word, frequency } of exactMatches) {
      const isNgram = prevNgrams.has(word);
      // Calcul du score avec boost N-gramme
      let score = frequency * 2.0;
      if (isNgram) score += 500;
      if (word.startsWith(cleanPrefix)) score += 100;
      if (word === cleanPrefix) score += 50;

      candidates.set(word, {
        word,
        score,
        isNgram,
        isExactPrefix: true,
      });
    }

    // 2. Recherche par préfixe normalisé (tolérance phonétique latine)
    const normPrefix = normalizeFulfuldeSearch(cleanPrefix);
    const normMatches = this.searchInTrie(this.normalizedRoot, normPrefix);
    for (const { word, frequency } of normMatches) {
      if (!candidates.has(word)) {
        const isNgram = prevNgrams.has(word);
        let score = frequency * 1.2;
        if (isNgram) score += 400;

        candidates.set(word, {
          word,
          score,
          isNgram,
          isExactPrefix: false,
        });
      }
    }

    // Si le mot de contexte précédent possède des N-grammes commençant par le préfixe
    for (const nextW of prevNgrams) {
      if (
        nextW.startsWith(cleanPrefix) ||
        normalizeFulfuldeSearch(nextW).startsWith(normPrefix)
      ) {
        const existing = candidates.get(nextW);
        const freq = this.wordMap.get(nextW) || 500;
        const newScore = (existing ? existing.score : freq) + 600;
        candidates.set(nextW, {
          word: nextW,
          score: newScore,
          isNgram: true,
          isExactPrefix: nextW.startsWith(cleanPrefix),
        });
      }
    }

    // Trier les candidats par score décroissant
    const sorted = Array.from(candidates.values())
      .sort((a, b) => {
        if (b.score !== a.score) return b.score - a.score;
        // En cas d'égalité, favoriser le mot le plus court (plus proche de la frappe)
        return a.word.length - b.word.length;
      })
      .map((c) => c.word);

    // Fallback si rien n'est trouvé : proposer des terminaisons usuelles Fulfulde
    if (sorted.length === 0) {
      return [cleanPrefix + 'de', cleanPrefix + 'o', cleanPrefix + 'am', cleanPrefix + 'i'].slice(0, limit);
    }

    return sorted.slice(0, limit);
  }

  private searchInTrie(root: TrieNode, prefix: string): { word: string; frequency: number }[] {
    let node = root;
    for (const ch of prefix) {
      if (!node.children.has(ch)) {
        return [];
      }
      node = node.children.get(ch)!;
    }

    const results: { word: string; frequency: number }[] = [];
    this.collectTrieWords(node, results);
    return results;
  }

  private collectTrieWords(node: TrieNode, results: { word: string; frequency: number }[]) {
    for (const [word, frequency] of node.words.entries()) {
      results.push({ word, frequency });
    }
    for (const child of node.children.values()) {
      this.collectTrieWords(child, results);
    }
  }

  private getNgramNextWords(prevWord: string): string[] {
    const list1 = this.ngrams.get(prevWord) || [];
    const list2 = this.customNgrams.has(prevWord)
      ? Array.from(this.customNgrams.get(prevWord)!)
      : [];
    const combined = [...new Set([...list2, ...list1])];
    return combined;
  }

  // Apprentissage d'un mot lors de la frappe
  public recordTypedWord(word: string, previousWord?: string) {
    const cleanW = cleanFulfuldeWord(word);
    if (!cleanW || cleanW.length < 2) return;

    // Augmenter la fréquence du mot
    const currentFreq = this.wordMap.get(cleanW) || 100;
    const newFreq = Math.min(1000, currentFreq + 15);
    this.insertWord(cleanW, newFreq, true);

    // Enregistrer la paire N-gramme
    if (previousWord) {
      const cleanPrev = cleanFulfuldeWord(previousWord);
      if (cleanPrev && cleanPrev.length >= 1) {
        if (!this.customNgrams.has(cleanPrev)) {
          this.customNgrams.set(cleanPrev, new Set());
        }
        this.customNgrams.get(cleanPrev)!.add(cleanW);
      }
    }

    this.saveToStorage();
  }

  // Apprentissage de corpus volumineux (texte brut collé ou importé)
  public importTextCorpus(rawText: string): { newWords: number; newNgrams: number; totalWords: number } {
    if (!rawText) return { newWords: 0, newNgrams: 0, totalWords: this.wordMap.size };

    const wordRegex = /[a-zA-ZɓƁɗƊŋŊƴƳñÑ’áéíóúÁÉÍÓÚ\-]+/g;
    const sentences = rawText.split(/[\.\n\?!;:]+/);

    let newWordsCount = 0;
    let newNgramsCount = 0;

    for (const sentence of sentences) {
      const matches = sentence.match(wordRegex);
      if (!matches) continue;

      const tokens = matches.map(cleanFulfuldeWord).filter((t) => t.length > 0);
      for (let i = 0; i < tokens.length; i++) {
        const token = tokens[i];
        if (!this.wordMap.has(token)) {
          newWordsCount++;
        }
        const currentFreq = this.wordMap.get(token) || 50;
        this.insertWord(token, Math.min(950, currentFreq + 25), true);

        if (i > 0) {
          const prev = tokens[i - 1];
          if (!this.customNgrams.has(prev)) {
            this.customNgrams.set(prev, new Set());
          }
          if (!this.customNgrams.get(prev)!.has(token)) {
            this.customNgrams.get(prev)!.add(token);
            newNgramsCount++;
          }
        }
      }
    }

    this.saveToStorage();
    return {
      newWords: newWordsCount,
      newNgrams: newNgramsCount,
      totalWords: this.wordMap.size,
    };
  }

  // Import d'un dictionnaire JSON structuré
  public importJsonDictionary(jsonString: string): { success: boolean; wordsCount: number; error?: string } {
    try {
      const parsed = JSON.parse(jsonString);
      let count = 0;

      // Format 1: { words: [{w, f}], ngrams: {...} }
      if (parsed.words && Array.isArray(parsed.words)) {
        for (const item of parsed.words) {
          if (item.w) {
            this.insertWord(item.w, Number(item.f) || 200, true);
            count++;
          }
        }
        if (parsed.ngrams && typeof parsed.ngrams === 'object') {
          for (const [prev, nextList] of Object.entries(parsed.ngrams)) {
            if (Array.isArray(nextList)) {
              if (!this.customNgrams.has(prev)) {
                this.customNgrams.set(prev, new Set());
              }
              for (const n of nextList) {
                this.customNgrams.get(prev)!.add(cleanFulfuldeWord(n));
              }
            }
          }
        }
      } else if (Array.isArray(parsed)) {
        // Format 2: ["mot1", "mot2"] ou [{w, f}]
        for (const item of parsed) {
          if (typeof item === 'string') {
            this.insertWord(item, 250, true);
            count++;
          } else if (item && item.w) {
            this.insertWord(item.w, Number(item.f) || 200, true);
            count++;
          }
        }
      }

      this.saveToStorage();
      return { success: true, wordsCount: count };
    } catch (e: any) {
      return { success: false, wordsCount: 0, error: e?.message || 'Format JSON invalide' };
    }
  }

  // Exporter le dictionnaire enrichi au format JSON téléchargeable
  public exportDictionary(): string {
    const wordsList = Array.from(this.wordMap.entries()).map(([w, f]) => ({ w, f }));
    wordsList.sort((a, b) => b.f - a.f);

    const ngramsObj: Record<string, string[]> = {};
    for (const [key, nextWords] of this.ngrams.entries()) {
      ngramsObj[key] = [...nextWords];
    }
    for (const [key, set] of this.customNgrams.entries()) {
      if (!ngramsObj[key]) {
        ngramsObj[key] = [];
      }
      for (const w of set) {
        if (!ngramsObj[key].includes(w)) {
          ngramsObj[key].push(w);
        }
      }
    }

    const payload: DictionaryData = {
      version: '2.0.0',
      language: 'ff-Latn',
      description: 'Dictionnaire Fulfulde enrichi avec corpus utilisateur',
      total_words: wordsList.length,
      words: wordsList,
      ngrams: ngramsObj,
    };

    return JSON.stringify(payload, null, 2);
  }

  // Réinitialiser au dictionnaire de base
  public resetToDefault() {
    this.exactRoot = new TrieNode();
    this.normalizedRoot = new TrieNode();
    this.wordMap.clear();
    this.ngrams.clear();
    this.customWords.clear();
    this.customNgrams.clear();

    if (typeof localStorage !== 'undefined') {
      localStorage.removeItem('fulfulde_custom_corpus');
      localStorage.removeItem('fulfulde_custom_ngrams');
    }

    this.loadBaseDictionary();
  }

  public getStats() {
    let ngramsCount = this.ngrams.size;
    for (const set of this.customNgrams.values()) {
      ngramsCount += set.size;
    }

    return {
      totalWords: this.wordMap.size,
      totalNgrams: ngramsCount,
      customWordsCount: this.customWords.size,
    };
  }

  private saveToStorage() {
    if (typeof localStorage === 'undefined') return;
    try {
      const customWordsArr = Array.from(this.customWords).map((w) => ({
        w,
        f: this.wordMap.get(w) || 100,
      }));
      localStorage.setItem('fulfulde_custom_corpus', JSON.stringify(customWordsArr));

      const ngramsObj: Record<string, string[]> = {};
      for (const [k, set] of this.customNgrams.entries()) {
        ngramsObj[k] = Array.from(set);
      }
      localStorage.setItem('fulfulde_custom_ngrams', JSON.stringify(ngramsObj));
    } catch (e) {
      console.warn('Impossible de sauvegarder le corpus personnalisé dans localStorage:', e);
    }
  }

  private loadFromStorage() {
    if (typeof localStorage === 'undefined') return;
    try {
      const saved = localStorage.getItem('fulfulde_custom_corpus');
      if (saved) {
        const words: WordEntry[] = JSON.parse(saved);
        for (const item of words) {
          if (item && item.w) {
            this.insertWord(item.w, item.f || 150, true);
          }
        }
      }

      const savedNgrams = localStorage.getItem('fulfulde_custom_ngrams');
      if (savedNgrams) {
        const ngramsObj: Record<string, string[]> = JSON.parse(savedNgrams);
        for (const [k, arr] of Object.entries(ngramsObj)) {
          if (Array.isArray(arr)) {
            this.customNgrams.set(k, new Set(arr));
          }
        }
      }
    } catch (e) {
      console.warn('Erreur lors de la lecture du corpus personnalisé depuis localStorage:', e);
    }
  }
}

// Singleton global de prédiction pour l'application frontend
export const predictionEngine = new FulfuldePredictionEngine();
