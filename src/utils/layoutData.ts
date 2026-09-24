import { KeyDefinition, BaseLayout } from '../types/keyboard';

export const QWERTY_LAYOUT: KeyDefinition[][] = [
  // Row 1: Numbers & Dead key
  [
    { code: 'Backquote', label: '`', shiftLabel: '~', altGrLabel: '`', variants: ['`', '~', '’', 'ʔ'] },
    { code: 'Digit1', label: '1', shiftLabel: '!', variants: ['1', '!', '¹'] },
    { code: 'Digit2', label: '2', shiftLabel: '@', variants: ['2', '@', '²'] },
    { code: 'Digit3', label: '3', shiftLabel: '#', variants: ['3', '#', '³'] },
    { code: 'Digit4', label: '4', shiftLabel: '$', variants: ['4', '$', '€'] },
    { code: 'Digit5', label: '5', shiftLabel: '%', variants: ['5', '%', '‰'] },
    { code: 'Digit6', label: '6', shiftLabel: '^', variants: ['6', '^'] },
    { code: 'Digit7', label: '7', shiftLabel: '&', variants: ['7', '&'] },
    { code: 'Digit8', label: '8', shiftLabel: '*', variants: ['8', '*', '×'] },
    { code: 'Digit9', label: '9', shiftLabel: '(', variants: ['9', '('] },
    { code: 'Digit0', label: '0', shiftLabel: ')', variants: ['0', ')'] },
    { code: 'Minus', label: '-', shiftLabel: '_', variants: ['-', '_', '—', '–'] },
    { code: 'Equal', label: '=', shiftLabel: '+', variants: ['=', '+', '±', '≠'] },
    { code: 'Backspace', label: '⌫', width: 'wide', isSpecial: true },
  ],

  // Row 2: QWERTY
  [
    { code: 'Tab', label: 'Tab ⇥', width: 'fn', isSpecial: true },
    { code: 'KeyQ', label: 'q', shiftLabel: 'Q', altGrLabel: 'ƴ', altGrShiftLabel: 'Ƴ', variants: ['q', 'Q', 'ƴ', 'Ƴ'] },
    { code: 'KeyW', label: 'w', shiftLabel: 'W', variants: ['w', 'W'] },
    { code: 'KeyE', label: 'e', shiftLabel: 'E', altGrLabel: 'é', altGrShiftLabel: 'É', variants: ['e', 'é', 'è', 'ê', 'ë', 'ē', 'E', 'É', 'È'] },
    { code: 'KeyR', label: 'r', shiftLabel: 'R', variants: ['r', 'R'] },
    { code: 'KeyT', label: 't', shiftLabel: 'T', variants: ['t', 'T'] },
    { code: 'KeyY', label: 'y', shiftLabel: 'Y', altGrLabel: 'ƴ', altGrShiftLabel: 'Ƴ', variants: ['y', 'ƴ', 'Y', 'Ƴ'] },
    { code: 'KeyU', label: 'u', shiftLabel: 'U', altGrLabel: 'ú', altGrShiftLabel: 'Ú', variants: ['u', 'ú', 'ù', 'û', 'ü', 'ū', 'U', 'Ú', 'Ù'] },
    { code: 'KeyI', label: 'i', shiftLabel: 'I', altGrLabel: 'í', altGrShiftLabel: 'Í', variants: ['i', 'í', 'ì', 'î', 'ï', 'ī', 'I', 'Í', 'Ì'] },
    { code: 'KeyO', label: 'o', shiftLabel: 'O', altGrLabel: 'ó', altGrShiftLabel: 'Ó', variants: ['o', 'ó', 'ò', 'ô', 'ö', 'ō', 'O', 'Ó', 'Ò'] },
    { code: 'KeyP', label: 'p', shiftLabel: 'P', variants: ['p', 'P'] },
    { code: 'BracketLeft', label: '[', shiftLabel: '{', altGrLabel: 'ɓ', altGrShiftLabel: 'Ɓ', variants: ['[', '{', 'ɓ', 'Ɓ'] },
    { code: 'BracketRight', label: ']', shiftLabel: '}', altGrLabel: 'ɗ', altGrShiftLabel: 'Ɗ', variants: [']', '}', 'ɗ', 'Ɗ'] },
    { code: 'Backslash', label: '\\', shiftLabel: '|', variants: ['\\', '|'] },
  ],

  // Row 3: ASDF
  [
    { code: 'CapsLock', label: 'Caps ⇪', width: 'wide', isSpecial: true },
    { code: 'KeyA', label: 'a', shiftLabel: 'A', altGrLabel: 'á', altGrShiftLabel: 'Á', variants: ['a', 'á', 'à', 'â', 'ä', 'ā', 'A', 'Á', 'À'] },
    { code: 'KeyS', label: 's', shiftLabel: 'S', variants: ['s', 'S', 'ß', '§'] },
    { code: 'KeyD', label: 'd', shiftLabel: 'D', altGrLabel: 'ɗ', altGrShiftLabel: 'Ɗ', variants: ['d', 'ɗ', 'D', 'Ɗ'] },
    { code: 'KeyF', label: 'f', shiftLabel: 'F', variants: ['f', 'F'] },
    { code: 'KeyG', label: 'g', shiftLabel: 'G', variants: ['g', 'G'] },
    { code: 'KeyH', label: 'h', shiftLabel: 'H', variants: ['h', 'H'] },
    { code: 'KeyJ', label: 'j', shiftLabel: 'J', variants: ['j', 'J'] },
    { code: 'KeyK', label: 'k', shiftLabel: 'K', variants: ['k', 'K'] },
    { code: 'KeyL', label: 'l', shiftLabel: 'L', variants: ['l', 'L'] },
    { code: 'Semicolon', label: ';', shiftLabel: ':', altGrLabel: 'ŋ', altGrShiftLabel: 'Ŋ', variants: [';', ':', 'ŋ', 'Ŋ'] },
    { code: 'Quote', label: '\'', shiftLabel: '"', altGrLabel: '’', variants: ['\'', '’', '"', 'ʔ'] },
    { code: 'Enter', label: 'Entrée ↵', width: 'wide', isSpecial: true },
  ],

  // Row 4: ZXCV
  [
    { code: 'ShiftLeft', label: 'Shift ⇧', width: 'extra-wide', isSpecial: true },
    { code: 'KeyZ', label: 'z', shiftLabel: 'Z', variants: ['z', 'Z'] },
    { code: 'KeyX', label: 'x', shiftLabel: 'X', variants: ['x', 'X'] },
    { code: 'KeyC', label: 'c', shiftLabel: 'C', variants: ['c', 'C', 'ç', 'Ç'] },
    { code: 'KeyV', label: 'v', shiftLabel: 'V', variants: ['v', 'V'] },
    { code: 'KeyB', label: 'b', shiftLabel: 'B', altGrLabel: 'ɓ', altGrShiftLabel: 'Ɓ', variants: ['b', 'ɓ', 'B', 'Ɓ'] },
    { code: 'KeyN', label: 'n', shiftLabel: 'N', altGrLabel: 'ŋ', altGrShiftLabel: 'Ŋ', variants: ['n', 'ŋ', 'N', 'Ŋ'] },
    { code: 'KeyM', label: 'm', shiftLabel: 'M', variants: ['m', 'M'] },
    { code: 'Comma', label: ',', shiftLabel: '<', variants: [',', '<', '«'] },
    { code: 'Period', label: '.', shiftLabel: '>', variants: ['.', '>', '»', '…'] },
    { code: 'Slash', label: '/', shiftLabel: '?', variants: ['/', '?', '¿'] },
    { code: 'ShiftRight', label: 'Shift ⇧', width: 'extra-wide', isSpecial: true },
  ],

  // Row 5: Space & Modifiers
  [
    { code: 'ControlLeft', label: 'Ctrl', width: 'fn', isSpecial: true },
    { code: 'AltLeft', label: 'Alt', width: 'fn', isSpecial: true },
    { code: 'Space', label: 'Espace (Fulfulde)', width: 'space', isSpecial: true },
    { code: 'AltRight', label: 'AltGr (Fulfulde ɓ/ɗ/ŋ/ƴ)', width: 'wide', isSpecial: true },
    { code: 'ControlRight', label: 'Ctrl', width: 'fn', isSpecial: true },
  ]
];

export const AZERTY_LAYOUT: KeyDefinition[][] = [
  // Row 1: Numbers & Accents AZERTY
  [
    { code: 'Backquote', label: '²', shiftLabel: '’', altGrLabel: '’', variants: ['²', '’', 'ʔ'] },
    { code: 'Digit1', label: '&', shiftLabel: '1', altGrLabel: '¹', variants: ['&', '1', '¹'] },
    { code: 'Digit2', label: 'é', shiftLabel: '2', altGrLabel: '~', variants: ['é', '2', 'É'] },
    { code: 'Digit3', label: '"', shiftLabel: '3', altGrLabel: '#', variants: ['"', '3', '#'] },
    { code: 'Digit4', label: '\'', shiftLabel: '4', altGrLabel: '{', variants: ['\'', '4', '{'] },
    { code: 'Digit5', label: '(', shiftLabel: '5', altGrLabel: '[', variants: ['(', '5', '['] },
    { code: 'Digit6', label: '-', shiftLabel: '6', altGrLabel: '|', variants: ['-', '6', '|'] },
    { code: 'Digit7', label: 'è', shiftLabel: '7', altGrLabel: '`', variants: ['è', '7', 'È'] },
    { code: 'Digit8', label: '_', shiftLabel: '8', altGrLabel: '\\', variants: ['_', '8', '\\'] },
    { code: 'Digit9', label: 'ç', shiftLabel: '9', altGrLabel: '^', variants: ['ç', '9', 'Ç'] },
    { code: 'Digit0', label: 'à', shiftLabel: '0', altGrLabel: '@', variants: ['à', '0', 'À'] },
    { code: 'Minus', label: ')', shiftLabel: '°', altGrLabel: ']', variants: [')', '°', ']'] },
    { code: 'Equal', label: '=', shiftLabel: '+', altGrLabel: '}', variants: ['=', '+', '}'] },
    { code: 'Backspace', label: '⌫', width: 'wide', isSpecial: true },
  ],

  // Row 2: AZERTY (Calqué exactement sur l'interface officielle)
  [
    { code: 'Tab', label: 'Tab ⇥', width: 'fn', isSpecial: true },
    { code: 'KeyA', label: 'a', shiftLabel: 'A', altGrLabel: 'á', altGrShiftLabel: 'Á', variants: ['a', 'A', 'á', 'Á', 'à', 'â'] },
    { code: 'KeyZ', label: 'ɗ', shiftLabel: 'Ɗ', altGrLabel: 'z', altGrShiftLabel: 'Z', variants: ['ɗ', 'Ɗ', 'z', 'Z'] },
    { code: 'KeyE', label: 'e', shiftLabel: 'E', altGrLabel: '€', variants: ['e', 'E', '€', 'é', 'è', 'ê'] },
    { code: 'KeyR', label: 'r', shiftLabel: 'R', variants: ['r', 'R'] },
    { code: 'KeyT', label: 't', shiftLabel: 'T', variants: ['t', 'T'] },
    { code: 'KeyY', label: 'y', shiftLabel: 'Y', variants: ['y', 'Y'] },
    { code: 'KeyU', label: 'u', shiftLabel: 'U', altGrLabel: 'ú', altGrShiftLabel: 'Ú', variants: ['u', 'U', 'ú', 'ù', 'û'] },
    { code: 'KeyI', label: 'i', shiftLabel: 'I', altGrLabel: 'í', altGrShiftLabel: 'Í', variants: ['i', 'I', 'í', 'ì', 'î'] },
    { code: 'KeyO', label: 'o', shiftLabel: 'O', altGrLabel: 'ó', altGrShiftLabel: 'Ó', variants: ['o', 'O', 'ó', 'ò', 'ô'] },
    { code: 'KeyP', label: 'p', shiftLabel: 'P', variants: ['p', 'P'] },
    { code: 'BracketLeft', label: 'ñ', shiftLabel: 'Ñ', altGrLabel: '^', altGrShiftLabel: '¨', variants: ['ñ', 'Ñ', '^', '¨'] },
    { code: 'BracketRight', label: '$', shiftLabel: '£', altGrLabel: '¤', variants: ['$', '£', '¤'] },
    { code: 'Backslash', label: '*', shiftLabel: 'µ', variants: ['*', 'µ'] },
  ],

  // Row 3: QSDFGHJKLM
  [
    { code: 'CapsLock', label: 'Caps ⇪', width: 'wide', isSpecial: true },
    { code: 'KeyQ', label: 'ŋ', shiftLabel: 'Ŋ', altGrLabel: 'q', altGrShiftLabel: 'Q', variants: ['ŋ', 'Ŋ', 'q', 'Q'] },
    { code: 'KeyS', label: 's', shiftLabel: 'S', variants: ['s', 'S', 'ß'] },
    { code: 'KeyD', label: 'd', shiftLabel: 'D', altGrLabel: 'ɗ', altGrShiftLabel: 'Ɗ', variants: ['d', 'D', 'ɗ', 'Ɗ'] },
    { code: 'KeyF', label: 'f', shiftLabel: 'F', variants: ['f', 'F'] },
    { code: 'KeyG', label: 'g', shiftLabel: 'G', variants: ['g', 'G'] },
    { code: 'KeyH', label: 'h', shiftLabel: 'H', variants: ['h', 'H'] },
    { code: 'KeyJ', label: 'j', shiftLabel: 'J', variants: ['j', 'J'] },
    { code: 'KeyK', label: 'k', shiftLabel: 'K', variants: ['k', 'K'] },
    { code: 'KeyL', label: 'l', shiftLabel: 'L', variants: ['l', 'L'] },
    { code: 'KeyM', label: 'm', shiftLabel: 'M', variants: ['m', 'M'] },
    { code: 'Semicolon', label: 'ù', shiftLabel: '%', variants: ['ù', '%'] },
    { code: 'Enter', label: 'Entrée ↵', width: 'wide', isSpecial: true },
  ],

  // Row 4: WXCVBN
  [
    { code: 'ShiftLeft', label: 'Shift ⇧', width: 'extra-wide', isSpecial: true },
    { code: 'KeyW', label: 'w', shiftLabel: 'W', variants: ['w', 'W'] },
    { code: 'KeyX', label: 'ƴ', shiftLabel: 'Ƴ', altGrLabel: 'x', altGrShiftLabel: 'X', variants: ['ƴ', 'Ƴ', 'x', 'X'] },
    { code: 'KeyC', label: 'c', shiftLabel: 'C', variants: ['c', 'C', 'ç', 'Ç'] },
    { code: 'KeyV', label: 'ɓ', shiftLabel: 'Ɓ', altGrLabel: 'v', altGrShiftLabel: 'V', variants: ['ɓ', 'Ɓ', 'v', 'V'] },
    { code: 'KeyB', label: 'b', shiftLabel: 'B', altGrLabel: 'ɓ', altGrShiftLabel: 'Ɓ', variants: ['b', 'B', 'ɓ', 'Ɓ'] },
    { code: 'KeyN', label: 'n', shiftLabel: 'N', altGrLabel: 'ŋ', altGrShiftLabel: 'Ŋ', variants: ['n', 'N', 'ŋ', 'Ŋ'] },
    { code: 'Comma', label: ',', shiftLabel: '?', variants: [',', '?'] },
    { code: 'Period', label: ';', shiftLabel: '.', variants: [';', '.'] },
    { code: 'Slash', label: ':', shiftLabel: '/', variants: [':', '/'] },
    { code: 'Equal', label: '!', shiftLabel: '§', variants: ['!', '§'] },
    { code: 'ShiftRight', label: 'Shift ⇧', width: 'extra-wide', isSpecial: true },
  ],

  // Row 5: Space & Modifiers
  [
    { code: 'ControlLeft', label: 'Ctrl', width: 'fn', isSpecial: true },
    { code: 'AltLeft', label: 'Alt', width: 'fn', isSpecial: true },
    { code: 'Space', label: 'Espace (Fulfulde)', width: 'space', isSpecial: true },
    { code: 'AltRight', label: 'AltGr (Fulfulde ɓ/ɗ/ŋ/ƴ)', width: 'wide', isSpecial: true },
    { code: 'ControlRight', label: 'Ctrl', width: 'fn', isSpecial: true },
  ]
];

export const KEYBOARD_LAYOUT = QWERTY_LAYOUT;

export function getLayoutByBase(base: BaseLayout): KeyDefinition[][] {
  return base === 'AZERTY' ? AZERTY_LAYOUT : QWERTY_LAYOUT;
}
