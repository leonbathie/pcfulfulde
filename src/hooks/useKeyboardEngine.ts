import { useState, useEffect, useCallback } from 'react';
import { KeyboardMode, TypingStats } from '../types/keyboard';
import { predictionEngine } from '../utils/predictionEngine';

// Check if running inside Tauri
const isTauri = typeof window !== 'undefined' && '__TAURI__' in window;

export function useKeyboardEngine() {
  const [mode, setModeState] = useState<KeyboardMode>('Direct');
  const [isShiftActive, setIsShiftActive] = useState(false);
  const [isAltGrActive, setIsAltGrActive] = useState(false);
  const [isCapsLockActive, setIsCapsLockActive] = useState(false);
  const [currentWord, setCurrentWord] = useState('');
  const [previousWord, setPreviousWord] = useState<string | undefined>(undefined);
  const [suggestions, setSuggestions] = useState<string[]>(['jam', 'noy', 'waali', 'ñalli', 'hiiri']);
  const [stats, setStats] = useState<TypingStats>({
    total_keystrokes: 0,
    total_words: 0,
    words_per_minute: 0,
    session_duration_secs: 0,
  });

  // Call Tauri invoke safely
  const invokeTauri = useCallback(async (cmd: string, args?: Record<string, unknown>) => {
    if (isTauri) {
      try {
        const { invoke } = await import('@tauri-apps/api/tauri');
        return await invoke(cmd, args);
      } catch (err) {
        console.warn(`Tauri invoke error for [${cmd}]:`, err);
      }
    }
    return null;
  }, []);

  // Sync mode with Tauri
  const setMode = useCallback((newMode: KeyboardMode) => {
    setModeState(newMode);
    invokeTauri('set_keyboard_mode', { mode: newMode });
  }, [invokeTauri]);

  const toggleMode = useCallback(() => {
    setModeState((prev) => {
      const next = prev === 'Direct' ? 'Latin' : 'Direct';
      invokeTauri('set_keyboard_mode', { mode: next });
      return next;
    });
  }, [invokeTauri]);

  // Inject text character or control key
  const injectText = useCallback((text: string) => {
    if (isTauri) {
      invokeTauri('inject_text', { text });
    } else {
      console.log(`[Simulated Input]: ${text}`);
    }

    // Update current word buffer for suggestion engine
    if (text === ' ' || text === '\n' || text === '\t') {
      const trimmed = currentWord.trim();
      if (trimmed.length > 0) {
        // Apprendre le mot et la séquence n-gramme
        predictionEngine.recordTypedWord(trimmed, previousWord);
        setPreviousWord(trimmed);
        invokeTauri('record_word');
      }
      setCurrentWord('');
    } else if (text === '⌫' || text === 'Backspace') {
      setCurrentWord((prev) => prev.slice(0, -1));
    } else if (text.length === 1) {
      setCurrentWord((prev) => prev + text);
    } else {
      // Insertion d'un mot complet
      const trimmed = text.trim();
      predictionEngine.recordTypedWord(trimmed, previousWord);
      setPreviousWord(trimmed);
      setCurrentWord('');
      invokeTauri('record_word');
    }

    // Deactivate temporary Shift after character press
    if (isShiftActive && !isCapsLockActive) {
      setIsShiftActive(false);
    }
  }, [currentWord, previousWord, invokeTauri, isCapsLockActive, isShiftActive]);

  // Appliquer une suggestion d'autocomplétion (remplace proprement le préfixe actuel)
  const applySuggestion = useCallback(async (word: string) => {
    if (!word) return;

    if (isTauri) {
      // Effacer le préfixe déjà tapé dans l'application externe cible
      const prefixLen = currentWord.length;
      for (let i = 0; i < prefixLen; i++) {
        await invokeTauri('inject_text', { text: '\b' });
      }
      // Injecter le mot complété avec une espace de séparation
      await invokeTauri('inject_text', { text: word + ' ' });
    } else {
      console.log(`[Autocomplétion appliquée]: "${word}" (remplaçant: "${currentWord}")`);
    }

    // Enregistrer l'apprentissage du mot et du contexte
    predictionEngine.recordTypedWord(word, previousWord);
    invokeTauri('record_word');

    setPreviousWord(word);
    setCurrentWord('');
  }, [currentWord, previousWord, invokeTauri]);

  // Actualiser les prédictions
  const updatePredictions = useCallback(async () => {
    // 1. Obtenir les suggestions du moteur local haute performance (0ms de latence)
    const localMatches = predictionEngine.predict(currentWord, previousWord, 5);

    // 2. Si Tauri est actif, interroger le backend en parallèle
    if (isTauri) {
      try {
        const res = await invokeTauri('get_predictions', {
          prefix: currentWord,
          previousWord: previousWord || null,
        }) as string[] | null;

        if (res && res.length > 0) {
          // Fusionner intelligemment en éliminant les doublons
          const combined = Array.from(new Set([...res, ...localMatches])).slice(0, 5);
          setSuggestions(combined);
          return;
        }
      } catch {
        // En cas d'erreur de communication, utiliser le résultat local
      }
    }

    setSuggestions(localMatches);
  }, [currentWord, previousWord, invokeTauri]);

  // Recalculer les prédictions à chaque frappe ou changement de mot
  useEffect(() => {
    updatePredictions();
  }, [currentWord, previousWord, updatePredictions]);

  // Polling stats every 2 seconds
  useEffect(() => {
    const interval = setInterval(async () => {
      if (isTauri) {
        const s = await invokeTauri('get_typing_stats') as TypingStats | null;
        if (s) {
          setStats(s);
        }
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [invokeTauri]);

  // Listen for mode changes from backend tray/hotkey
  useEffect(() => {
    let unlisten: (() => void) | undefined;
    if (isTauri) {
      import('@tauri-apps/api/event').then(({ listen }) => {
        listen<string>('mode_changed', (event) => {
          if (event.payload === 'Direct' || event.payload === 'Latin' || event.payload === 'Qwerty') {
            setModeState(event.payload as KeyboardMode);
          }
        }).then((fn) => {
          unlisten = fn;
        });
      });
    }

    return () => {
      if (unlisten) unlisten();
    };
  }, []);

  // Synchroniser le préfixe et le mot de contexte directement (ex: depuis la zone de texte)
  const syncCurrentInput = useCallback((prefix: string, prevWord?: string) => {
    setCurrentWord(prefix);
    setPreviousWord(prevWord);
  }, []);

  return {
    mode,
    setMode,
    toggleMode,
    isShiftActive,
    setIsShiftActive,
    isAltGrActive,
    setIsAltGrActive,
    isCapsLockActive,
    setIsCapsLockActive,
    currentWord,
    setCurrentWord,
    previousWord,
    setPreviousWord,
    syncCurrentInput,
    suggestions,
    stats,
    injectText,
    applySuggestion,
    updatePredictions,
  };
}
