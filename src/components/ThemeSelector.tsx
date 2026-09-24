import React from 'react';
import { ThemeName } from '../types/keyboard';

interface ThemeSelectorProps {
  currentTheme: ThemeName;
  onSelectTheme: (theme: ThemeName) => void;
}

const THEMES: { id: ThemeName; label: string; color: string }[] = [
  { id: 'midnight', label: 'Midnight Glass', color: 'bg-slate-900 border-slate-700' },
  { id: 'pulaar-indigo', label: 'Pulaar Indigo', color: 'bg-indigo-950 border-indigo-700' },
  { id: 'emerald', label: 'Emerald Forest', color: 'bg-emerald-950 border-emerald-700' },
  { id: 'solar-gold', label: 'Solar Gold', color: 'bg-amber-950 border-amber-700' },
  { id: 'clean-light', label: 'Clean Light', color: 'bg-slate-100 border-slate-300' },
];

export const ThemeSelector: React.FC<ThemeSelectorProps> = ({
  currentTheme,
  onSelectTheme,
}) => {
  return (
    <div className="flex items-center gap-1.5 p-1 bg-slate-900/80 rounded-lg border border-slate-700/60">
      {THEMES.map((theme) => (
        <button
          key={theme.id}
          title={theme.label}
          onClick={() => onSelectTheme(theme.id)}
          className={`w-5 h-5 rounded-full border transition-all ${theme.color} ${
            currentTheme === theme.id ? 'ring-2 ring-fula-400 scale-110' : 'opacity-70 hover:opacity-100'
          }`}
        />
      ))}
    </div>
  );
};
