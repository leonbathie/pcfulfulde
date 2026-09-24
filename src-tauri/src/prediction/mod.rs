pub mod trie;

use std::collections::HashMap;
use serde::{Deserialize, Serialize};
use trie::FulfuldeTrie;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WordEntry {
    pub w: String,
    pub f: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DictionaryPayload {
    pub version: String,
    pub language: String,
    pub words: Vec<WordEntry>,
    #[serde(default)]
    pub ngrams: HashMap<String, Vec<String>>,
}

pub struct PredictionEngine {
    pub trie: FulfuldeTrie,
    pub ngrams: HashMap<String, Vec<String>>,
}

impl Default for PredictionEngine {
    fn default() -> Self {
        let mut engine = Self {
            trie: FulfuldeTrie::new(),
            ngrams: HashMap::new(),
        };

        // Load built-in embedded dictionary
        let dict_data = include_str!("../../../dictionary/dict_ff_latin.json");
        if let Ok(parsed) = serde_json::from_str::<DictionaryPayload>(dict_data) {
            for entry in parsed.words {
                engine.trie.insert(&entry.w, entry.f);
            }
            engine.ngrams = parsed.ngrams;
        }

        engine
    }
}

impl PredictionEngine {
    pub fn new() -> Self {
        Self::default()
    }

    /// Apprendre un mot et sa liaison contextuelle
    pub fn learn_word(&mut self, word: &str, previous_word: Option<&str>) {
        let clean = word.trim().to_lowercase();
        if clean.len() < 2 {
            return;
        }
        self.trie.insert(&clean, 300);

        if let Some(prev) = previous_word {
            let prev_clean = prev.trim().to_lowercase();
            if !prev_clean.is_empty() {
                let entry = self.ngrams.entry(prev_clean).or_default();
                if !entry.contains(&clean) {
                    entry.insert(0, clean);
                    if entry.len() > 10 {
                        entry.truncate(10);
                    }
                }
            }
        }
    }

    /// Return top word suggestions based on prefix and context
    pub fn predict(&self, current_prefix: &str, previous_word: Option<&str>) -> Vec<String> {
        let clean_prefix = current_prefix.trim().to_lowercase();
        let limit = 5;

        if clean_prefix.is_empty() {
            // Context-based bigram prediction when prefix is empty
            if let Some(prev) = previous_word {
                let prev_clean = prev.trim().to_lowercase();
                if let Some(next_words) = self.ngrams.get(&prev_clean) {
                    let mut suggestions = next_words.clone();
                    suggestions.truncate(limit);
                    return suggestions;
                }
            }
            return vec![
                "jam".into(),
                "noy".into(),
                "waali".into(),
                "ñalli".into(),
                "hiiri".into(),
            ];
        }

        let matches = self.trie.search_prefix(&clean_prefix, 8);
        let mut result = Vec::new();

        // If previous word exists, check if any matches are predicted bigrams and boost them
        if let Some(prev) = previous_word {
            let prev_clean = prev.trim().to_lowercase();
            if let Some(next_words) = self.ngrams.get(&prev_clean) {
                for next_w in next_words {
                    if matches.iter().any(|(m, _)| m == next_w) && !result.contains(next_w) {
                        result.push(next_w.clone());
                    }
                }
            }
        }

        // Add prefix matches
        for (w, _) in matches {
            if !result.contains(&w) {
                result.push(w);
            }
            if result.len() >= limit {
                break;
            }
        }

        // Fallback bigrams if prefix matches nothing
        if result.is_empty() {
            if let Some(prev) = previous_word {
                if let Some(next_words) = self.ngrams.get(&prev.to_lowercase()) {
                    let mut fallbacks = next_words.clone();
                    fallbacks.truncate(limit);
                    return fallbacks;
                }
            }
        }

        result.truncate(limit);
        result
    }
}
