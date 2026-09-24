import { useState, useCallback, useEffect, useRef } from 'react';
import { useKeyboardEngine } from './hooks/useKeyboardEngine';
import { HeaderControls } from './components/HeaderControls';
import { SuggestionBar } from './components/SuggestionBar';
import { VirtualKeyboard } from './components/VirtualKeyboard';
import { StatsModal } from './components/StatsModal';
import { CorpusModal } from './components/CorpusModal';
import { ThemeName, BaseLayout } from './types/keyboard';
import { Copy, Trash2, Edit3, ChevronUp, ChevronDown, Check } from 'lucide-react';

export function App() {
  const {
    mode,
    toggleMode,
    isShiftActive,
    setIsShiftActive,
    isAltGrActive,
    setIsAltGrActive,
    isCapsLockActive,
    setIsCapsLockActive,
    currentWord,
    suggestions,
    stats,
    injectText,
    applySuggestion,
    syncCurrentInput,
    updatePredictions,
  } = useKeyboardEngine();

  const [baseLayout, setBaseLayout] = useState<BaseLayout>('AZERTY');
  const [alwaysOnTop, setAlwaysOnTop] = useState(true);
  const [opacity, setOpacity] = useState(0.96);
  const [theme, setTheme] = useState<ThemeName>('midnight');
  const [showStatsModal, setShowStatsModal] = useState(false);
  const [showCorpusModal, setShowCorpusModal] = useState(false);

  // Zone de saisie rapide intégrée (Notepad / Playground)
  const [showNotepad, setShowNotepad] = useState(true);
  const [editorText, setEditorText] = useState('');
  const [copied, setCopied] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Synchroniser le préfixe et le contexte N-gramme selon la position du curseur
  const syncFromEditor = useCallback((text: string, cursorPos?: number) => {
    const pos = cursorPos !== undefined ? cursorPos : text.length;
    const before = text.slice(0, pos);
    const matches = before.match(/[a-zA-ZɓƁɗƊŋŊƴƳñÑ’áéíóúÁÉÍÓÚ\-]+/g) || [];
    const endsWithWordChar = /[a-zA-ZɓƁɗƊŋŊƴƳñÑ’áéíóúÁÉÍÓÚ\-]/.test(before.slice(-1));

    if (endsWithWordChar && matches.length > 0) {
      const prefix = matches[matches.length - 1];
      const prev = matches.length > 1 ? matches[matches.length - 2] : undefined;
      syncCurrentInput(prefix, prev);
    } else {
      const prev = matches.length > 0 ? matches[matches.length - 1] : undefined;
      syncCurrentInput('', prev);
    }
  }, [syncCurrentInput]);

  const toggleBaseLayout = useCallback(() => {
    setBaseLayout((prev) => (prev === 'AZERTY' ? 'QWERTY' : 'AZERTY'));
  }, []);

  // Tauri window actions
  const handleToggleAlwaysOnTop = useCallback(async () => {
    const nextState = !alwaysOnTop;
    setAlwaysOnTop(nextState);
    if (typeof window !== 'undefined' && '__TAURI__' in window) {
      try {
        const { appWindow } = await import('@tauri-apps/api/window');
        await appWindow.setAlwaysOnTop(nextState);
      } catch (err) {
        console.warn('Tauri window error:', err);
      }
    }
  }, [alwaysOnTop]);

  const handleMinimize = useCallback(async () => {
    if (typeof window !== 'undefined' && '__TAURI__' in window) {
      try {
        const { appWindow } = await import('@tauri-apps/api/window');
        await appWindow.minimize();
      } catch (err) {
        console.warn('Tauri minimize error:', err);
      }
    }
  }, []);

  const handleClose = useCallback(async () => {
    if (typeof window !== 'undefined' && '__TAURI__' in window) {
      try {
        const { appWindow } = await import('@tauri-apps/api/window');
        await appWindow.close();
      } catch (err) {
        console.warn('Tauri close error:', err);
      }
    }
  }, []);

  // Gestion des frappes venant du clavier virtuel
  const handleKeyInject = useCallback((text: string) => {
    // 1. Injection système (Tauri / OS)
    injectText(text);

    // 2. Mise à jour de la zone de saisie locale si active
    if (showNotepad) {
      const textarea = textareaRef.current;
      const start = textarea?.selectionStart ?? editorText.length;
      const end = textarea?.selectionEnd ?? editorText.length;
      let newText = editorText;
      let newCursor = start;

      if (text === 'Backspace' || text === '⌫') {
        if (start === end && start > 0) {
          newText = editorText.slice(0, start - 1) + editorText.slice(start);
          newCursor = start - 1;
        } else if (start !== end) {
          newText = editorText.slice(0, start) + editorText.slice(end);
          newCursor = start;
        }
      } else if (text === '\t') {
        newText = editorText.slice(0, start) + '    ' + editorText.slice(end);
        newCursor = start + 4;
      } else {
        newText = editorText.slice(0, start) + text + editorText.slice(end);
        newCursor = start + text.length;
      }

      setEditorText(newText);
      syncFromEditor(newText, newCursor);
      setTimeout(() => {
        if (textareaRef.current) {
          textareaRef.current.selectionStart = textareaRef.current.selectionEnd = newCursor;
        }
      }, 0);
    }
  }, [injectText, showNotepad, editorText, syncFromEditor]);

  // Sélection d'une suggestion d'autocomplétion
  const handleSelectSuggestion = useCallback((word: string) => {
    if (!word) return;

    // Remplacement précis au curseur dans la zone de texte locale
    if (showNotepad) {
      const textarea = textareaRef.current;
      const pos = textarea ? textarea.selectionStart : editorText.length;
      const before = editorText.slice(0, pos);
      const after = editorText.slice(pos);

      let newBefore = before;
      if (currentWord && before.endsWith(currentWord)) {
        newBefore = before.slice(0, -currentWord.length) + word + ' ';
      } else {
        newBefore = (before ? before + (before.endsWith(' ') ? '' : ' ') : '') + word + ' ';
      }

      const newText = newBefore + after;
      const newCursor = newBefore.length;
      setEditorText(newText);
      syncFromEditor(newText, newCursor);

      setTimeout(() => {
        if (textareaRef.current) {
          textareaRef.current.selectionStart = textareaRef.current.selectionEnd = newCursor;
          textareaRef.current.focus();
        }
      }, 0);
    }

    // Remplacement système et apprentissage
    applySuggestion(word);
  }, [applySuggestion, currentWord, showNotepad, editorText, syncFromEditor]);

  // Copier le texte saisi dans le presse-papier
  const handleCopyText = useCallback(() => {
    if (!editorText) return;
    navigator.clipboard.writeText(editorText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }, [editorText]);

  // Effacer le texte du bloc-notes
  const handleClearText = useCallback(() => {
    setEditorText('');
    syncCurrentInput('', undefined);
  }, [syncCurrentInput]);

  // Support du clavier physique lorsque la fenêtre est active
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Bascule de disposition AZERTY / QWERTY avec Ctrl+Shift+L
      if (e.ctrlKey && e.shiftKey && (e.key === 'L' || e.key === 'l')) {
        e.preventDefault();
        toggleBaseLayout();
        return;
      }

      // Bascule Mode Direct <-> AltGr avec Ctrl+Shift+F
      if (e.ctrlKey && e.shiftKey && (e.key === 'F' || e.key === 'f')) {
        e.preventDefault();
        toggleMode();
        return;
      }

      // Raccourci TAB pour accepter la première suggestion d'autocomplétion
      if (e.key === 'Tab' && suggestions.length > 0) {
        e.preventDefault();
        handleSelectSuggestion(suggestions[0]);
        return;
      }

      // Raccourcis Alt + [1..5] pour sélectionner une suggestion
      if (e.altKey && ['1', '2', '3', '4', '5'].includes(e.key)) {
        e.preventDefault();
        const index = parseInt(e.key, 10) - 1;
        if (suggestions[index]) {
          handleSelectSuggestion(suggestions[index]);
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [suggestions, handleSelectSuggestion, toggleMode, toggleBaseLayout]);

  return (
    <div
      style={{ opacity }}
      className={`w-screen h-screen flex flex-col p-2 transition-opacity duration-150 glass-panel theme-${theme}`}
    >
      <div className="w-full h-full flex flex-col justify-between bg-slate-950/75 border border-slate-700/60 rounded-2xl p-2 shadow-2xl backdrop-blur-xl overflow-hidden">
        
        {/* Header Bar */}
        <HeaderControls
          mode={mode}
          onToggleMode={toggleMode}
          baseLayout={baseLayout}
          onToggleBaseLayout={toggleBaseLayout}
          alwaysOnTop={alwaysOnTop}
          onToggleAlwaysOnTop={handleToggleAlwaysOnTop}
          opacity={opacity}
          onChangeOpacity={setOpacity}
          currentTheme={theme}
          onSelectTheme={setTheme}
          onOpenStats={() => setShowStatsModal(true)}
          onOpenCorpus={() => setShowCorpusModal(true)}
          onMinimize={handleMinimize}
          onClose={handleClose}
        />

        {/* Suggestion Bar (IA Fulfulde Autocomplétion) */}
        <div className="mt-1.5">
          <SuggestionBar
            suggestions={suggestions}
            onSelectSuggestion={handleSelectSuggestion}
            onOpenCorpus={() => setShowCorpusModal(true)}
            currentPrefix={currentWord}
          />
        </div>

        {/* Zone de saisie rapide / Bloc-notes testeur (dépliable) */}
        {showNotepad && (
          <div className="mb-1.5 px-2 py-1.5 bg-slate-900/90 border border-slate-700/60 rounded-xl flex flex-col gap-1 shadow-inner animate-in fade-in duration-150">
            <div className="flex items-center justify-between text-[11px] text-slate-400">
              <div className="flex items-center gap-1.5 text-fula-400 font-semibold">
                <Edit3 className="w-3 h-3" />
                <span>Zone de saisie rapide Fulfulde</span>
                <span className="text-[10px] text-slate-500 font-normal">
                  ({editorText ? editorText.trim().split(/\s+/).filter(Boolean).length : 0} mots)
                </span>
              </div>

              <div className="flex items-center gap-1">
                <button
                  onClick={handleCopyText}
                  disabled={!editorText}
                  title="Copier le texte dans le presse-papier"
                  className="px-2 py-0.5 rounded text-[10px] font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 disabled:opacity-40 transition flex items-center gap-1"
                >
                  {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                  <span>{copied ? 'Copié !' : 'Copier'}</span>
                </button>

                <button
                  onClick={handleClearText}
                  disabled={!editorText}
                  title="Effacer le texte"
                  className="p-1 rounded text-slate-400 hover:text-rose-400 hover:bg-slate-800 disabled:opacity-40 transition"
                >
                  <Trash2 className="w-3 h-3" />
                </button>

                <button
                  onClick={() => setShowNotepad(false)}
                  title="Masquer le bloc-notes"
                  className="p-1 rounded text-slate-400 hover:text-white hover:bg-slate-800 transition"
                >
                  <ChevronUp className="w-3 h-3" />
                </button>
              </div>
            </div>

            <textarea
              ref={textareaRef}
              value={editorText}
              onChange={(e) => {
                const val = e.target.value;
                setEditorText(val);
                syncFromEditor(val, e.target.selectionStart);
              }}
              onKeyUp={(e) => {
                const target = e.target as HTMLTextAreaElement;
                syncFromEditor(target.value, target.selectionStart);
              }}
              onClick={(e) => {
                const target = e.target as HTMLTextAreaElement;
                syncFromEditor(target.value, target.selectionStart);
              }}
              onSelect={(e) => {
                const target = e.target as HTMLTextAreaElement;
                syncFromEditor(target.value, target.selectionStart);
              }}
              placeholder="Tapez ici avec le clavier virtuel ou physique... Testez l'autocomplétion (Tab ou Alt+1..5 pour valider) !"
              rows={2}
              className="w-full px-2 py-1 bg-slate-950/60 border border-slate-800 rounded-lg text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-fula-500 resize-none font-sans"
            />
          </div>
        )}

        {/* Bouton pour réafficher le bloc-notes si masqué */}
        {!showNotepad && (
          <div className="flex justify-end mb-1 px-1">
            <button
              onClick={() => setShowNotepad(true)}
              className="px-2 py-0.5 text-[10px] text-slate-400 hover:text-fula-400 bg-slate-900 border border-slate-800 rounded-lg transition flex items-center gap-1"
            >
              <Edit3 className="w-3 h-3" />
              <span>Afficher bloc-notes</span>
              <ChevronDown className="w-3 h-3" />
            </button>
          </div>
        )}

        {/* Virtual Keyboard Grid */}
        <div className="flex-1 flex items-center justify-center min-h-0">
          <VirtualKeyboard
            baseLayout={baseLayout}
            isShift={isShiftActive}
            setIsShift={setIsShiftActive}
            isAltGr={isAltGrActive}
            setIsAltGr={setIsAltGrActive}
            isCapsLock={isCapsLockActive}
            setIsCapsLock={setIsCapsLockActive}
            onKeyInject={handleKeyInject}
            onToggleMode={toggleMode}
          />
        </div>
      </div>

      {/* Typing Stats Modal */}
      {showStatsModal && (
        <StatsModal
          stats={stats}
          onClose={() => setShowStatsModal(false)}
        />
      )}

      {/* Corpus Management & Data Ingestion Modal */}
      <CorpusModal
        isOpen={showCorpusModal}
        onClose={() => setShowCorpusModal(false)}
        onDictionaryUpdated={updatePredictions}
      />
    </div>
  );
}

export default App;
