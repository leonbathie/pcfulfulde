import React, { useRef } from 'react';
import { KeyDefinition } from '../types/keyboard';
import { useLongPress } from '../hooks/useLongPress';

interface KeyButtonProps {
  keyDef: KeyDefinition;
  isShift: boolean;
  isAltGr: boolean;
  isCapsLock: boolean;
  onKeyPress: (char: string) => void;
  onOpenVariants: (variants: string[], position: { top: number; left: number }) => void;
}

export const KeyButton: React.FC<KeyButtonProps> = ({
  keyDef,
  isShift,
  isAltGr,
  isCapsLock,
  onKeyPress,
  onOpenVariants,
}) => {
  const buttonRef = useRef<HTMLButtonElement | null>(null);

  // Compute the current active main character
  const getDisplayChar = (): string => {
    if (isAltGr) {
      if (isShift && keyDef.altGrShiftLabel) return keyDef.altGrShiftLabel;
      if (keyDef.altGrLabel) return keyDef.altGrLabel;
    }

    if (isShift || isCapsLock) {
      if (keyDef.shiftLabel) return keyDef.shiftLabel;
    }

    return keyDef.label;
  };

  const currentChar = getDisplayChar();

  const handleShortClick = () => {
    onKeyPress(currentChar);
  };

  const handleLongPress = () => {
    if (keyDef.variants && keyDef.variants.length > 1 && buttonRef.current) {
      const rect = buttonRef.current.getBoundingClientRect();
      onOpenVariants(keyDef.variants, {
        top: rect.top,
        left: rect.left + rect.width / 2,
      });
    } else {
      handleShortClick();
    }
  };

  const longPressEvents = useLongPress({
    threshold: 300,
    onLongPress: handleLongPress,
    onClick: handleShortClick,
  });

  // Calculate width style classes
  const getWidthClass = () => {
    switch (keyDef.width) {
      case 'fn':
        return 'flex-[1.2] min-w-[50px]';
      case 'wide':
        return 'flex-[1.5] min-w-[65px]';
      case 'extra-wide':
        return 'flex-[2] min-w-[85px]';
      case 'space':
        return 'flex-[5] min-w-[200px]';
      default:
        return 'flex-1 min-w-[38px]';
    }
  };

  const isModifierActive =
    (keyDef.code === 'ShiftLeft' || keyDef.code === 'ShiftRight') && isShift ||
    (keyDef.code === 'AltRight' && isAltGr) ||
    (keyDef.code === 'CapsLock' && isCapsLock);

  return (
    <button
      ref={buttonRef}
      {...longPressEvents}
      type="button"
      className={`
        relative h-11 sm:h-12 flex flex-col items-center justify-center rounded-lg transition-all duration-75 select-none
        font-medium text-sm sm:text-base border shadow-sm active:scale-95
        ${getWidthClass()}
        ${
          isModifierActive
            ? 'bg-fula-500 text-white border-fula-400 shadow-fula-500/50 shadow-md ring-2 ring-fula-400'
            : keyDef.isSpecial
            ? 'bg-slate-800/80 text-slate-300 border-slate-700 hover:bg-slate-700/80 hover:text-white'
            : 'bg-slate-800/90 text-slate-100 border-slate-700/60 hover:bg-slate-700/90 hover:border-slate-500/80 hover:shadow-md'
        }
      `}
    >
      {/* Upper Right AltGr Indicator Badge */}
      {keyDef.altGrLabel && !keyDef.isSpecial && (
        <span className="absolute top-0.5 right-1.5 text-[10px] font-bold text-fula-400 group-hover:text-fula-300">
          {isShift && keyDef.altGrShiftLabel ? keyDef.altGrShiftLabel : keyDef.altGrLabel}
        </span>
      )}

      {/* Main Character Label */}
      <span className="leading-none">
        {currentChar}
      </span>
    </button>
  );
};
