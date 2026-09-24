import React from 'react';
import { X, Activity, Zap, Clock, Key } from 'lucide-react';
import { TypingStats } from '../types/keyboard';

interface StatsModalProps {
  stats: TypingStats;
  onClose: () => void;
}

export const StatsModal: React.FC<StatsModalProps> = ({ stats, onClose }) => {
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs < 10 ? '0' : ''}${secs}s`;
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="w-full max-w-md bg-slate-900 border border-slate-700/80 rounded-2xl p-6 shadow-2xl">
        <div className="flex items-center justify-between pb-4 mb-5 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-fula-400" />
            <h2 className="text-lg font-bold text-white">Statistiques de Frappe</h2>
          </div>
          <button
            onClick={onClose}
            className="p-1 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="p-4 bg-slate-800/60 rounded-xl border border-slate-700/50">
            <div className="flex items-center gap-2 text-slate-400 text-xs mb-1">
              <Zap className="w-4 h-4 text-amber-400" />
              <span>Vitesse (WPM)</span>
            </div>
            <div className="text-3xl font-extrabold text-white">
              {stats.words_per_minute}
            </div>
            <span className="text-[11px] text-slate-500">Mots par minute</span>
          </div>

          <div className="p-4 bg-slate-800/60 rounded-xl border border-slate-700/50">
            <div className="flex items-center gap-2 text-slate-400 text-xs mb-1">
              <Key className="w-4 h-4 text-fula-400" />
              <span>Frappes Totales</span>
            </div>
            <div className="text-3xl font-extrabold text-white">
              {stats.total_keystrokes}
            </div>
            <span className="text-[11px] text-slate-500">Caractères saisis</span>
          </div>

          <div className="p-4 bg-slate-800/60 rounded-xl border border-slate-700/50">
            <div className="flex items-center gap-2 text-slate-400 text-xs mb-1">
              <Activity className="w-4 h-4 text-sky-400" />
              <span>Mots Fulfulde</span>
            </div>
            <div className="text-3xl font-extrabold text-white">
              {stats.total_words}
            </div>
            <span className="text-[11px] text-slate-500">Mots validés</span>
          </div>

          <div className="p-4 bg-slate-800/60 rounded-xl border border-slate-700/50">
            <div className="flex items-center gap-2 text-slate-400 text-xs mb-1">
              <Clock className="w-4 h-4 text-purple-400" />
              <span>Session Active</span>
            </div>
            <div className="text-2xl font-bold text-white">
              {formatTime(stats.session_duration_secs)}
            </div>
            <span className="text-[11px] text-slate-500">Temps écoulé</span>
          </div>
        </div>

        <button
          onClick={onClose}
          className="w-full mt-6 py-2.5 bg-fula-600 hover:bg-fula-500 text-white font-medium rounded-xl transition shadow-lg shadow-fula-900/40"
        >
          Fermer
        </button>
      </div>
    </div>
  );
};
