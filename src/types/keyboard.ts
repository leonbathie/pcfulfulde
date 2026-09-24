export type KeyboardMode = 'Latin' | 'Direct' | 'Qwerty';

export type BaseLayout = 'AZERTY' | 'QWERTY';

export type ThemeName = 'midnight' | 'pulaar-indigo' | 'emerald' | 'solar-gold' | 'clean-light';

export interface KeyDefinition {
  code: string;
  label: string;
  shiftLabel?: string;
  altGrLabel?: string;
  altGrShiftLabel?: string;
  variants?: string[];
  width?: 'normal' | 'wide' | 'extra-wide' | 'space' | 'fn';
  isSpecial?: boolean;
}

export interface TypingStats {
  total_keystrokes: number;
  total_words: number;
  words_per_minute: number;
  session_duration_secs: number;
}

export interface KeyboardState {
  mode: KeyboardMode;
  baseLayout: BaseLayout;
  isShiftActive: boolean;
  isAltGrActive: boolean;
  isCapsLockActive: boolean;
  opacity: number;
  alwaysOnTop: boolean;
  theme: ThemeName;
  soundEnabled: boolean;
}
