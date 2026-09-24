import React from 'react';
import { Sparkles, Database } from 'lucide-react';

interface SuggestionBarProps {
  suggestions: string[];
  onSelectSuggestion: (word: string) => void;
  onOpenCorpus?: () => void;
  currentPrefix?: string;
}

export const SuggestionBar: React.FC<SuggestionBarProps> = ({
  suggestions,
  onSelectSuggestion,
  onOpenCorpus,
  currentPrefix,
}) => {
  return (
    <div className="w-full h-11 px-2.5 mb-2 flex items-center justify-between gap-2 bg-slate-900/80 border border-slate-700/60 rounded-xl backdrop-blur-md shadow-lg">
      {/* Label & Corpus Quick Access */}
      <div className="flex items-center gap-1.5 shrink-0">
        <button
          onClick={onOpenCorpus}
          title="Ouvrir le gestionnaire de données & corpus pour enrichir l'autocomplétion"
          className="flex items-center gap-1.5 text-fula-400 hover:text-fula-300 bg-slate-800/60 hover:bg-slate-800 px-2 py-1 rounded-lg border border-slate-700/50 transition cursor-pointer select-none group"
        >
          <Sparkles className="w-3.5 h-3.5 text-fula-400 group-hover:scale-110 transition-transform" />
          <span className="text-xs font-bold uppercase tracking-wider hidden sm:inline">IA Fulfulde</span>
          <Database className="w-3 h-3 text-slate-400 group-hover:text-fula-300 ml-0.5" />
        </button>
      </div>

      {/* Suggestion Chips */}
      <div className="flex-1 flex items-center justify-center gap-1.5 sm:gap-2 overflow-x-auto no-scrollbar py-0.5">
        {suggestions.length > 0 ? (
          suggestions.map((word, index) => {
            const isFirst = index === 0;
            return (
              <button
                key={index}
                onClick={() => onSelectSuggestion(word)}
                title={`Compléter "${word}" (Raccourci: Alt+${index + 1}${isFirst ? ' ou Tab' : ''})`}
                className={`group px-3 py-1 min-w-[70px] sm:min-w-[95px] max-w-[170px] flex items-center justify-center gap-1.5 sm:gap-2 text-xs sm:text-sm font-medium rounded-lg border transition-all duration-150 transform active:scale-95 shadow-sm ${
                  isFirst
                    ? 'bg-fula-950/60 hover:bg-fula-600 text-fula-200 hover:text-white border-fula-500/50 hover:border-fula-400'
                    : 'bg-slate-800/80 hover:bg-fula-600 text-slate-200 hover:text-white border-slate-700/70'
                }`}
              >
                <span
                  className={`text-[10px] font-bold px-1.5 py-0.5 rounded transition ${
                    isFirst
                      ? 'text-fula-300 group-hover:text-white bg-fula-900/60 group-hover:bg-fula-700'
                      : 'text-slate-400 group-hover:text-white bg-slate-950/50'
                  }`}
                >
                  {isFirst ? 'Tab / 1' : index + 1}
                </span>
                <span className="truncate">{word}</span>
              </button>
            );
          })
        ) : (
          <span className="text-xs text-slate-400 italic">
            {currentPrefix ? `Aucun mot pour "${currentPrefix}"` : 'Tapez pour afficher les suggestions'}
          </span>
        )}
      </div>

      {/* Current buffer indicator */}
      {currentPrefix && (
        <div className="hidden md:flex items-center text-[11px] text-slate-400 bg-slate-950/60 px-2 py-0.5 rounded border border-slate-800 font-mono">
          <span className="text-fula-400 mr-1">&gt;</span>
          <span className="truncate max-w-[80px]">{currentPrefix}</span>
        </div>
      )}
    </div>
  );
};
