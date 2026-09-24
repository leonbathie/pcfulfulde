import React, { useState, useEffect, useRef } from 'react';
import {
  X,
  Database,
  Upload,
  Download,
  RotateCcw,
  Sparkles,
  CheckCircle2,
  FileText,
  Search,
  BookOpen
} from 'lucide-react';
import { predictionEngine } from '../utils/predictionEngine';

interface CorpusModalProps {
  isOpen: boolean;
  onClose: () => void;
  onDictionaryUpdated?: () => void;
}

export const CorpusModal: React.FC<CorpusModalProps> = ({
  isOpen,
  onClose,
  onDictionaryUpdated,
}) => {
  const [stats, setStats] = useState({ totalWords: 0, totalNgrams: 0, customWordsCount: 0 });
  const [inputText, setInputText] = useState('');
  const [testPrefix, setTestPrefix] = useState('');
  const [testContext, setTestContext] = useState('');
  const [testResults, setTestResults] = useState<string[]>([]);
  const [notification, setNotification] = useState<{ type: 'success' | 'error' | 'info'; message: string } | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const refreshStats = () => {
    const s = predictionEngine.getStats();
    setStats(s);
  };

  useEffect(() => {
    if (isOpen) {
      refreshStats();
      setNotification(null);
    }
  }, [isOpen]);

  useEffect(() => {
    if (testPrefix || testContext) {
      const results = predictionEngine.predict(testPrefix, testContext || undefined, 5);
      setTestResults(results);
    } else {
      setTestResults(predictionEngine.predict('', undefined, 5));
    }
  }, [testPrefix, testContext]);

  if (!isOpen) return null;

  const handleLearnFromText = () => {
    if (!inputText.trim()) {
      setNotification({ type: 'error', message: 'Veuillez saisir ou coller du texte Fulfulde.' });
      return;
    }

    setIsProcessing(true);
    setTimeout(() => {
      try {
        const res = predictionEngine.importTextCorpus(inputText);
        refreshStats();
        setInputText('');
        setNotification({
          type: 'success',
          message: `Apprentissage réussi ! ${res.newWords} nouveaux mots et ${res.newNgrams} n-grammes ajoutés. Total : ${res.totalWords} mots actifs.`,
        });
        if (onDictionaryUpdated) onDictionaryUpdated();
      } catch (err: any) {
        setNotification({ type: 'error', message: `Erreur : ${err?.message || 'Échec de traitement'}` });
      } finally {
        setIsProcessing(false);
      }
    }, 50);
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsProcessing(true);
    const reader = new FileReader();

    reader.onload = (event) => {
      const content = event.target?.result as string;
      if (!content) {
        setIsProcessing(false);
        return;
      }

      try {
        if (file.name.endsWith('.json')) {
          const res = predictionEngine.importJsonDictionary(content);
          if (res.success) {
            setNotification({
              type: 'success',
              message: `Fichier JSON importé avec succès ! ${res.wordsCount} mots intégrés.`,
            });
          } else {
            setNotification({ type: 'error', message: `Erreur JSON : ${res.error}` });
          }
        } else {
          // Fichier texte (.txt, .csv)
          const res = predictionEngine.importTextCorpus(content);
          setNotification({
            type: 'success',
            message: `Fichier texte importé ! ${res.newWords} nouveaux mots appris (${res.totalWords} au total).`,
          });
        }
        refreshStats();
        if (onDictionaryUpdated) onDictionaryUpdated();
      } catch (err: any) {
        setNotification({ type: 'error', message: `Erreur lors de la lecture : ${err?.message}` });
      } finally {
        setIsProcessing(false);
        if (fileInputRef.current) fileInputRef.current.value = '';
      }
    };

    reader.onerror = () => {
      setIsProcessing(false);
      setNotification({ type: 'error', message: 'Erreur lors de la lecture du fichier.' });
    };

    reader.readAsText(file);
  };

  const handleExport = () => {
    try {
      const jsonStr = predictionEngine.exportDictionary();
      const blob = new Blob([jsonStr], { type: 'application/json;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `dictionnaire_fulfulde_enrichi_${new Date().toISOString().slice(0, 10)}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      setNotification({ type: 'success', message: 'Dictionnaire exporté au format JSON !' });
    } catch (e: any) {
      setNotification({ type: 'error', message: `Erreur d'export : ${e?.message}` });
    }
  };

  const handleReset = () => {
    if (window.confirm('Voulez-vous vraiment réinitialiser le dictionnaire au contenu de base ? Vos mots personnalisés seront effacés.')) {
      predictionEngine.resetToDefault();
      refreshStats();
      setNotification({ type: 'info', message: 'Dictionnaire réinitialisé aux valeurs de base.' });
      if (onDictionaryUpdated) onDictionaryUpdated();
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-slate-950/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="w-full max-w-2xl max-h-[90vh] bg-slate-900 border border-slate-700/80 rounded-2xl shadow-2xl flex flex-col overflow-hidden">
        
        {/* Header */}
        <div className="px-5 py-3.5 border-b border-slate-800 flex items-center justify-between bg-slate-950/40">
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-fula-600/20 text-fula-400 rounded-xl border border-fula-500/30">
              <Database className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white leading-tight">
                Gestionnaire de Données & Corpus Fulfulde
              </h2>
              <p className="text-xs text-slate-400">
                Alimentez l'IA avec vos textes pour enrichir l'autocomplétion en temps réel
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-5 space-y-4 no-scrollbar">

          {/* Stats Bar */}
          <div className="grid grid-cols-3 gap-3">
            <div className="p-3 bg-slate-800/70 border border-slate-700/60 rounded-xl">
              <div className="flex items-center gap-1.5 text-slate-400 text-xs mb-1">
                <BookOpen className="w-3.5 h-3.5 text-fula-400" />
                <span>Mots Actifs</span>
              </div>
              <div className="text-xl font-bold text-white">{stats.totalWords.toLocaleString()}</div>
              <div className="text-[10px] text-slate-400">Vocabulaire total</div>
            </div>

            <div className="p-3 bg-slate-800/70 border border-slate-700/60 rounded-xl">
              <div className="flex items-center gap-1.5 text-slate-400 text-xs mb-1">
                <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                <span>N-Grammes (Contexte)</span>
              </div>
              <div className="text-xl font-bold text-white">{stats.totalNgrams.toLocaleString()}</div>
              <div className="text-[10px] text-slate-400">Associations de mots</div>
            </div>

            <div className="p-3 bg-slate-800/70 border border-slate-700/60 rounded-xl">
              <div className="flex items-center gap-1.5 text-slate-400 text-xs mb-1">
                <FileText className="w-3.5 h-3.5 text-sky-400" />
                <span>Mots Appris</span>
              </div>
              <div className="text-xl font-bold text-sky-300">+{stats.customWordsCount.toLocaleString()}</div>
              <div className="text-[10px] text-slate-400">Ajoutés par vous</div>
            </div>
          </div>

          {/* Notification */}
          {notification && (
            <div
              className={`p-3 rounded-xl text-xs font-medium flex items-center gap-2 border ${
                notification.type === 'success'
                  ? 'bg-emerald-950/40 border-emerald-600/50 text-emerald-300'
                  : notification.type === 'error'
                  ? 'bg-rose-950/40 border-rose-600/50 text-rose-300'
                  : 'bg-sky-950/40 border-sky-600/50 text-sky-300'
              }`}
            >
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              <span>{notification.message}</span>
            </div>
          )}

          {/* Section: Importer / Apprendre de nouvelles données */}
          <div className="p-4 bg-slate-800/50 border border-slate-700/60 rounded-xl space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-fula-300 flex items-center gap-1.5">
                <Upload className="w-3.5 h-3.5" />
                Nourrir l'autocomplétion avec vos données
              </span>
              <button
                onClick={() => fileInputRef.current?.click()}
                disabled={isProcessing}
                className="px-2.5 py-1 text-xs font-medium text-slate-200 bg-slate-700 hover:bg-slate-600 rounded-lg transition flex items-center gap-1.5"
              >
                <FileText className="w-3.5 h-3.5 text-fula-400" />
                <span>Importer un fichier (.txt, .json)</span>
              </button>
              <input
                ref={fileInputRef}
                type="file"
                accept=".txt,.json,.csv"
                onChange={handleFileUpload}
                className="hidden"
              />
            </div>

            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Collez ici vos phrases, livres, articles ou listes de mots en Fulfulde (Pulaar)... L'algorithme apprend automatiquement le vocabulaire et les tournures de phrases !"
              rows={4}
              className="w-full p-2.5 bg-slate-900/90 border border-slate-700 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-fula-500 transition font-sans"
            />

            <div className="flex items-center justify-between">
              <span className="text-[11px] text-slate-400">
                {inputText.length > 0 ? `${inputText.trim().split(/\s+/).length} mots détectés` : 'Prend en charge ɓ, ɗ, ŋ, ƴ, ’ et les accents'}
              </span>
              <button
                onClick={handleLearnFromText}
                disabled={isProcessing || !inputText.trim()}
                className="px-4 py-1.5 bg-fula-600 hover:bg-fula-500 disabled:opacity-50 text-white text-xs font-semibold rounded-lg transition flex items-center gap-1.5 shadow-md shadow-fula-950"
              >
                <Sparkles className="w-3.5 h-3.5" />
                <span>{isProcessing ? 'Analyse en cours...' : 'Apprendre ce texte'}</span>
              </button>
            </div>
          </div>

          {/* Section: Testeur d'autocomplétion en direct */}
          <div className="p-4 bg-slate-800/50 border border-slate-700/60 rounded-xl space-y-3">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
              <Search className="w-3.5 h-3.5 text-fula-400" />
              Tester l'autocomplétion en temps réel
            </span>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Mot précédent (contexte N-gramme) :</label>
                <input
                  type="text"
                  value={testContext}
                  onChange={(e) => setTestContext(e.target.value)}
                  placeholder="Ex: jam, mido, fulɓe..."
                  className="w-full px-2.5 py-1.5 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white focus:outline-none focus:border-fula-500"
                />
              </div>

              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Préfixe en cours de frappe :</label>
                <input
                  type="text"
                  value={testPrefix}
                  onChange={(e) => setTestPrefix(e.target.value)}
                  placeholder="Ex: fulb (pour fulɓe), bid (pour ɓiɗɗo)..."
                  className="w-full px-2.5 py-1.5 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white focus:outline-none focus:border-fula-500"
                />
              </div>
            </div>

            {/* Suggestions preview */}
            <div className="p-2.5 bg-slate-950/70 border border-slate-800 rounded-xl flex items-center gap-2 overflow-x-auto">
              <span className="text-[11px] font-semibold text-fula-400 uppercase tracking-wider pl-1">
                Suggestions :
              </span>
              {testResults.length > 0 ? (
                testResults.map((w, idx) => (
                  <span
                    key={idx}
                    className="px-2.5 py-1 bg-slate-800 border border-slate-700 text-slate-200 text-xs font-medium rounded-lg flex items-center gap-1.5"
                  >
                    <span className="text-[10px] text-fula-400 font-bold bg-slate-900 px-1 py-0.5 rounded">
                      {idx + 1}
                    </span>
                    <span>{w}</span>
                  </span>
                ))
              ) : (
                <span className="text-xs text-slate-500 italic">Aucune suggestion trouvée</span>
              )}
            </div>
          </div>

        </div>

        {/* Footer Actions */}
        <div className="px-5 py-3 border-t border-slate-800 flex items-center justify-between bg-slate-950/50">
          <div className="flex items-center gap-2">
            <button
              onClick={handleExport}
              title="Télécharger une sauvegarde JSON de votre dictionnaire enrichi"
              className="px-3 py-1.5 text-xs font-medium text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg transition flex items-center gap-1.5"
            >
              <Download className="w-3.5 h-3.5 text-fula-400" />
              <span>Exporter (JSON)</span>
            </button>

            <button
              onClick={handleReset}
              title="Réinitialiser le dictionnaire par défaut"
              className="px-3 py-1.5 text-xs font-medium text-rose-300 hover:text-rose-200 bg-rose-950/30 hover:bg-rose-950/60 border border-rose-800/40 rounded-lg transition flex items-center gap-1.5"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Réinitialiser</span>
            </button>
          </div>

          <button
            onClick={onClose}
            className="px-4 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium text-xs rounded-lg transition"
          >
            Fermer
          </button>
        </div>

      </div>
    </div>
  );
};
