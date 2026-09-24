use std::sync::atomic::{AtomicU64, Ordering};
use std::time::Instant;
use serde::{Deserialize, Serialize};
use lazy_static::lazy_static;

lazy_static! {
    pub static ref TOTAL_KEYSTROKES: AtomicU64 = AtomicU64::new(0);
    pub static ref TOTAL_WORDS: AtomicU64 = AtomicU64::new(0);
    pub static ref SESSION_START: Instant = Instant::now();
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TypingStats {
    pub total_keystrokes: u64,
    pub total_words: u64,
    pub words_per_minute: f64,
    pub session_duration_secs: u64,
}

pub struct StatsTracker;

impl StatsTracker {
    pub fn record_keystroke() {
        TOTAL_KEYSTROKES.fetch_add(1, Ordering::Relaxed);
    }

    pub fn record_word() {
        TOTAL_WORDS.fetch_add(1, Ordering::Relaxed);
    }

    pub fn get_stats() -> TypingStats {
        let strokes = TOTAL_KEYSTROKES.load(Ordering::Relaxed);
        let words = TOTAL_WORDS.load(Ordering::Relaxed);
        let elapsed = SESSION_START.elapsed().as_secs();

        let wpm = if elapsed > 0 {
            let minutes = (elapsed as f64) / 60.0;
            // Standard typing WPM: (keystrokes / 5) / minutes
            ((strokes as f64) / 5.0) / minutes
        } else {
            0.0
        };

        TypingStats {
            total_keystrokes: strokes,
            total_words: words,
            words_per_minute: (wpm * 10.0).round() / 10.0,
            session_duration_secs: elapsed,
        }
    }
}
