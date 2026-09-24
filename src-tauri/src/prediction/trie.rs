use std::collections::HashMap;
use serde::{Deserialize, Serialize};

pub fn normalize_fulfulde(s: &str) -> String {
    s.chars()
        .map(|c| match c {
            'ɓ' | 'Ɓ' => 'b',
            'ɗ' | 'Ɗ' => 'd',
            'ŋ' | 'Ŋ' => 'n',
            'ñ' | 'Ñ' => 'n',
            'ƴ' | 'Ƴ' => 'y',
            '’' | '\'' | '`' | '‘' | 'ʼ' => '\0',
            'á' | 'Á' => 'a',
            'é' | 'É' => 'e',
            'í' | 'Í' => 'i',
            'ó' | 'Ó' => 'o',
            'ú' | 'Ú' => 'u',
            other => other.to_ascii_lowercase(),
        })
        .filter(|&c| c != '\0')
        .collect()
}

#[derive(Default, Debug, Clone, Serialize, Deserialize)]
pub struct TrieNode {
    pub words: Vec<(String, u32)>,
    pub children: HashMap<char, TrieNode>,
}

#[derive(Default, Debug, Clone, Serialize, Deserialize)]
pub struct FulfuldeTrie {
    pub exact_root: TrieNode,
    pub norm_root: TrieNode,
}

impl FulfuldeTrie {
    pub fn new() -> Self {
        Self {
            exact_root: TrieNode::default(),
            norm_root: TrieNode::default(),
        }
    }

    /// Insert a Fulfulde word with its empirical frequency
    pub fn insert(&mut self, word: &str, frequency: u32) {
        let clean = word.trim().to_lowercase();
        if clean.is_empty() {
            return;
        }

        // 1. Insert into exact trie
        let mut current = &mut self.exact_root;
        for ch in clean.chars() {
            current = current.children.entry(ch).or_default();
        }
        if let Some(pos) = current.words.iter().position(|(w, _)| w == &clean) {
            current.words[pos].1 = frequency.max(current.words[pos].1);
        } else {
            current.words.push((clean.clone(), frequency));
        }

        // 2. Insert into normalized phonetic trie
        let norm = normalize_fulfulde(&clean);
        let mut norm_curr = &mut self.norm_root;
        for ch in norm.chars() {
            norm_curr = norm_curr.children.entry(ch).or_default();
        }
        if let Some(pos) = norm_curr.words.iter().position(|(w, _)| w == &clean) {
            norm_curr.words[pos].1 = frequency.max(norm_curr.words[pos].1);
        } else {
            norm_curr.words.push((clean, frequency));
        }
    }

    /// Retrieve top matching words for prefix with phonetic and exact tolerance
    pub fn search_prefix(&self, prefix: &str, limit: usize) -> Vec<(String, u32)> {
        let clean_prefix = prefix.trim().to_lowercase();
        let norm_prefix = normalize_fulfulde(&clean_prefix);

        let mut matches: HashMap<String, u32> = HashMap::new();

        // 1. Exact trie search
        let mut curr = &self.exact_root;
        let mut found_exact = true;
        for ch in clean_prefix.chars() {
            if let Some(next) = curr.children.get(&ch) {
                curr = next;
            } else {
                found_exact = false;
                break;
            }
        }
        if found_exact {
            let mut exact_results = Vec::new();
            self.collect_words(curr, &mut exact_results);
            for (w, f) in exact_results {
                matches.insert(w, f * 2); // Exact matches get frequency boost
            }
        }

        // 2. Phonetic normalized search (b -> ɓ, d -> ɗ, etc.)
        if !norm_prefix.is_empty() {
            let mut norm_curr = &self.norm_root;
            let mut found_norm = true;
            for ch in norm_prefix.chars() {
                if let Some(next) = norm_curr.children.get(&ch) {
                    norm_curr = next;
                } else {
                    found_norm = false;
                    break;
                }
            }
            if found_norm {
                let mut norm_results = Vec::new();
                self.collect_words(norm_curr, &mut norm_results);
                for (w, f) in norm_results {
                    matches.entry(w).or_insert(f);
                }
            }
        }

        let mut sorted: Vec<(String, u32)> = matches.into_iter().collect();
        sorted.sort_by(|a, b| b.1.cmp(&a.1));
        sorted.truncate(limit);
        sorted
    }

    fn collect_words(&self, node: &TrieNode, results: &mut Vec<(String, u32)>) {
        for (w, f) in &node.words {
            results.push((w.clone(), *f));
        }

        for child in node.children.values() {
            self.collect_words(child, results);
        }
    }
}
