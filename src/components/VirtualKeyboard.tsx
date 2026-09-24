import React, { useState } from 'react';
import { BaseLayout } from '../types/keyboard';
import { getLayoutByBase } from '../utils/layoutData';
import { KeyButton } from './KeyButton';
import { LongPressPopup } from './LongPressPopup';

interface VirtualKeyboardProps {
  baseLayout: BaseLayout;
  isShift: boolean;
  setIsShift: React.Dispatch<React.SetStateAction<boolean>>;
  isAltGr: boolean;
  setIsAltGr: React.Dispatch<React.SetStateAction<boolean>>;
  isCapsLock: boolean;
  setIsCapsLock: React.Dispatch<React.SetStateAction<boolean>>;
  onKeyInject: (char: string) => void;
  onToggleMode: () => void;
}

export const VirtualKeyboard: React.FC<VirtualKeyboardProps> = ({
  baseLayout,
  isShift,
  setIsShift,
  isAltGr,
  setIsAltGr,
  isCapsLock,
  setIsCapsLock,
  onKeyInject,
  onToggleMode,
}) => {
  const [popupState, setPopupState] = useState<{
    isOpen: boolean;
    variants: string[];
    position: { top: number; left: number };
  }>({
    isOpen: false,
    variants: [],
    position: { top: 0, left: 0 },
  });

  const activeLayout = getLayoutByBase(baseLayout);

  const handleKeyPress = (char: string) => {
    if (char === 'Shift ⇧') {
      setIsShift((prev) => !prev);
      return;
    }

    if (char === 'Caps ⇪') {
      setIsCapsLock((prev) => !prev);
      return;
    }

    if (char.startsWith('AltGr')) {
      setIsAltGr((prev) => !prev);
      return;
    }

    if (char === 'Ctrl+Shift+F') {
      onToggleMode();
      return;
    }

    if (char === 'Espace (Fulfulde)') {
      onKeyInject(' ');
      return;
    }

    if (char === 'Tab ⇥') {
      onKeyInject('\t');
      return;
    }

    if (char === 'Entrée ↵') {
      onKeyInject('\n');
      return;
    }

    if (char === '⌫') {
      onKeyInject('Backspace');
      return;
    }

    // Regular character
    onKeyInject(char);
  };

  const handleOpenVariants = (
    variants: string[],
    position: { top: number; left: number }
  ) => {
    setPopupState({
      isOpen: true,
      variants,
      position,
    });
  };

  const handleSelectVariant = (variant: string) => {
    onKeyInject(variant);
    setPopupState((prev) => ({ ...prev, isOpen: false }));
  };

  return (
    <div className="w-full flex flex-col gap-1.5 p-1 select-none">
      {activeLayout.map((row, rowIndex) => (
        <div key={rowIndex} className="w-full flex items-center gap-1.5">
          {row.map((keyDef) => (
            <KeyButton
              key={keyDef.code}
              keyDef={keyDef}
              isShift={isShift}
              isAltGr={isAltGr}
              isCapsLock={isCapsLock}
              onKeyPress={handleKeyPress}
              onOpenVariants={handleOpenVariants}
            />
          ))}
        </div>
      ))}

      {/* 300ms Long Press Variant Popup */}
      {popupState.isOpen && (
        <LongPressPopup
          variants={popupState.variants}
          position={popupState.position}
          onSelectVariant={handleSelectVariant}
          onClose={() => setPopupState((prev) => ({ ...prev, isOpen: false }))}
        />
      )}
    </div>
  );
};
