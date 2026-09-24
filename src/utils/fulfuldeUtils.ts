// Utilitaires pour le Fulfulde (Pulaar) Latin

export function isFulfuldeSpecialChar(char: string): boolean {
  const specials = ['ɓ', 'Ɓ', 'ɗ', 'Ɗ', 'ŋ', 'Ŋ', 'ƴ', 'Ƴ', 'ñ', 'Ñ', '’'];
  return specials.includes(char);
}

export function normalizeFulfuldeText(text: string): string {
  return text.trim();
}
