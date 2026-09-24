import React from 'react';

interface LongPressPopupProps {
  variants: string[];
  onSelectVariant: (variant: string) => void;
  onClose: () => void;
  position: { top: number; left: number };
}

export const LongPressPopup: React.FC<LongPressPopupProps> = ({
  variants,
  onSelectVariant,
  onClose,
  position,
}) => {
  return (
    <>
      {/* Backdrop to capture outside clicks */}
      <div
        className="fixed inset-0 z-40 bg-transparent"
        onClick={onClose}
      />

      {/* Floating Variants Toolbar */}
      <div
        style={{ top: `${position.top - 62}px`, left: `${position.left}px` }}
        className="fixed z-50 transform -translate-x-1/2 flex items-center gap-1.5 p-1.5 bg-slate-900/95 border border-fula-400/40 rounded-xl shadow-2xl backdrop-blur-md animate-in fade-in zoom-in-95 duration-150"
      >
        {variants.map((v, idx) => (
          <button
            key={idx}
            onClick={(e) => {
              e.stopPropagation();
              onSelectVariant(v);
            }}
            className="min-w-[42px] h-11 px-3 flex items-center justify-center text-lg font-semibold text-white bg-slate-800/90 hover:bg-fula-600 hover:text-white rounded-lg transition-all transform active:scale-95 shadow-md border border-slate-700/60"
          >
            {v}
          </button>
        ))}
      </div>
    </>
  );
};
