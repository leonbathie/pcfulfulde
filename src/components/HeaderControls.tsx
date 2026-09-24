import React from 'react';
import {
  Pin,
  PinOff,
  BarChart2,
  Sliders,
  Minus,
  X,
  Keyboard,
  Move,
  Database
} from 'lucide-react';
import { KeyboardMode, ThemeName, BaseLayout } from '../types/keyboard';
import { ThemeSelector } from './ThemeSelector';

interface HeaderControlsProps {
  mode: KeyboardMode;
  onToggleMode: () => void;
  baseLayout: BaseLayout;
  onToggleBaseLayout: () => void;
  alwaysOnTop: boolean;
  onToggleAlwaysOnTop: () => void;
  opacity: number;
  onChangeOpacity: (opacity: number) => void;
  currentTheme: ThemeName;
  onSelectTheme: (theme: ThemeName) => void;
  onOpenStats: () => void;
  onOpenCorpus?: () => void;
  onMinimize: () => void;
  onClose: () => void;
}

export const HeaderControls: React.FC<HeaderControlsProps> = ({
  mode,
  onToggleMode,
  baseLayout,
  onToggleBaseLayout,
  alwaysOnTop,
  onToggleAlwaysOnTop,
  opacity,
  onChangeOpacity,
  currentTheme,
  onSelectTheme,
  onOpenStats,
  onOpenCorpus,
  onMinimize,
  onClose,
}) => {
  const [showOpacitySlider, setShowOpacitySlider] = React.useState(false);

  return (
    <div
      data-tauri-drag-region
      className="w-full h-10 px-3 flex items-center justify-between bg-slate-950/80 border-b border-slate-800/80 rounded-t-2xl select-none cursor-move"
    >
      {/* Left: App Title & Mode Switcher */}
      <div className="flex items-center gap-2.5">
        <div className="flex items-center gap-1.5 text-fula-400 font-bold text-sm tracking-wide">
          <Move className="w-3.5 h-3.5 text-slate-500" />
          <span className="hidden sm:inline">FULFULDE LATIN</span>
        </div>

        {/* AZERTY / QWERTY Toggle Button */}
        <button
          onClick={onToggleBaseLayout}
          title="Basculer entre la disposition AZERTY et QWERTY"
          className="px-2.5 py-1 rounded-lg text-xs font-bold bg-slate-800 hover:bg-slate-700 text-sky-300 border border-slate-700 transition shadow-sm flex items-center gap-1.5"
        >
          <Keyboard className="w-3.5 h-3.5" />
          <span>{baseLayout}</span>
        </button>

        {/* Direct / AltGr Mode Toggle */}
        <button
          onClick={onToggleMode}
          title="Basculer entre Mode Direct et Mode AltGr"
          className="px-2.5 py-1 rounded-lg text-xs font-semibold bg-fula-600/20 text-fula-300 border border-fula-500/50 shadow-sm transition"
        >
          {mode === 'Direct' ? 'Mode Direct' : 'Mode AltGr'}
        </button>
      </div>

      {/* Center: Themes & Opacity */}
      <div className="hidden sm:flex items-center gap-3">
        <ThemeSelector currentTheme={currentTheme} onSelectTheme={onSelectTheme} />

        {/* Opacity Control */}
        <div className="relative">
          <button
            onClick={() => setShowOpacitySlider(!showOpacitySlider)}
            title="Ajuster la transparence de la fenêtre"
            className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition"
          >
            <Sliders className="w-3.5 h-3.5" />
          </button>

          {showOpacitySlider && (
            <div className="absolute top-8 left-1/2 transform -translate-x-1/2 z-50 p-2.5 bg-slate-900 border border-slate-700 rounded-xl shadow-xl flex items-center gap-2">
              <span className="text-[10px] text-slate-400">Opacité</span>
              <input
                type="range"
                min="0.3"
                max="1.0"
                step="0.05"
                value={opacity}
                onChange={(e) => onChangeOpacity(parseFloat(e.target.value))}
                className="w-24 accent-fula-500 cursor-pointer"
              />
              <span className="text-[11px] font-mono text-slate-300">
                {Math.round(opacity * 100)}%
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Right: Window & Stats Actions */}
      <div className="flex items-center gap-1">
        {/* Corpus & Data Management Button */}
        <button
          onClick={onOpenCorpus}
          title="Gestionnaire de Données & Corpus (Enrichir l'autocomplétion IA)"
          className="p-1.5 text-slate-400 hover:text-fula-400 rounded-lg hover:bg-slate-800 transition"
        >
          <Database className="w-4 h-4" />
        </button>

        {/* Stats Button */}
        <button
          onClick={onOpenStats}
          title="Statistiques de frappe WPM"
          className="p-1.5 text-slate-400 hover:text-fula-400 rounded-lg hover:bg-slate-800 transition"
        >
          <BarChart2 className="w-4 h-4" />
        </button>

        {/* Always on top toggle */}
        <button
          onClick={onToggleAlwaysOnTop}
          title={alwaysOnTop ? "Désactiver Premier Plan" : "Épingler au Premier Plan"}
          className={`p-1.5 rounded-lg transition ${
            alwaysOnTop ? 'text-fula-400 bg-fula-950/60' : 'text-slate-400 hover:text-white hover:bg-slate-800'
          }`}
        >
          {alwaysOnTop ? <Pin className="w-4 h-4" /> : <PinOff className="w-4 h-4" />}
        </button>

        {/* Minimize */}
        <button
          onClick={onMinimize}
          title="Réduire dans la barre des tâches"
          className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition"
        >
          <Minus className="w-4 h-4" />
        </button>

        {/* Close */}
        <button
          onClick={onClose}
          title="Fermer"
          className="p-1.5 text-slate-400 hover:text-rose-400 rounded-lg hover:bg-rose-950/40 transition"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
