use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum KeyboardMode {
    FulfuldeLatin,
    FulfuldeDirect,
    StandardQwerty,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MappingRule {
    pub key: char,
    pub alt_gr: Option<char>,
    pub alt_gr_shift: Option<char>,
    pub shift: Option<char>,
    pub dead_key_acute: Option<char>,
    pub dead_key_grave: Option<char>,
}

pub struct FulfuldeMapper {
    pub mode: KeyboardMode,
    pub dead_key_active_acute: bool,
    pub dead_key_grave: bool,
    pub last_char: Option<char>,
}

impl Default for FulfuldeMapper {
    fn default() -> Self {
        Self {
            mode: KeyboardMode::FulfuldeDirect,
            dead_key_active_acute: false,
            dead_key_grave: false,
            last_char: None,
        }
    }
}

impl FulfuldeMapper {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn set_mode(&mut self, mode: KeyboardMode) {
        self.mode = mode;
        self.reset_dead_keys();
    }

    pub fn toggle_mode(&mut self) -> KeyboardMode {
        self.mode = match self.mode {
            KeyboardMode::FulfuldeDirect => KeyboardMode::FulfuldeLatin,
            KeyboardMode::FulfuldeLatin => KeyboardMode::FulfuldeDirect,
            KeyboardMode::StandardQwerty => KeyboardMode::FulfuldeDirect,
        };
        self.reset_dead_keys();
        self.mode
    }

    pub fn reset_dead_keys(&mut self) {
        self.dead_key_active_acute = false;
        self.dead_key_grave = false;
        self.last_char = None;
    }

    /// Process a key press with modifier states and return the resulting Unicode string/char if handled
    pub fn map_key(
        &mut self,
        c: char,
        shift: bool,
        alt_gr: bool,
        ctrl: bool,
    ) -> Option<String> {
        // If standard Ctrl is held (and not AltGr), don't intercept standard shortcuts like Ctrl+C
        if ctrl && !alt_gr {
            return None;
        }

        match self.mode {
            KeyboardMode::StandardQwerty => None,

            KeyboardMode::FulfuldeDirect => {
                // Touches directes SANS utiliser Ctrl, Alt ou AltGr
                let direct_char = match (c, shift) {
                    ('[', false) => Some('ɓ'),
                    ('[', true)  => Some('Ɓ'),
                    (']', false) => Some('ɗ'),
                    (']', true)  => Some('Ɗ'),
                    (';', false) => Some('ŋ'),
                    (';', true)  => Some('Ŋ'),
                    ('\'', false) => Some('’'),
                    ('q', false) if !alt_gr => Some('ƴ'),
                    ('q', true)  if !alt_gr => Some('Ƴ'),
                    _ => None,
                };

                if let Some(ch) = direct_char {
                    return Some(ch.to_string());
                }

                // Support AltGr en complément
                if alt_gr {
                    return self.map_alt_gr(c, shift);
                }

                None
            }

            KeyboardMode::FulfuldeLatin => {
                if (c == '`' || c == '~') && alt_gr {
                    self.dead_key_grave = true;
                    return Some("".to_string());
                }

                if self.dead_key_grave {
                    self.dead_key_grave = false;
                    if let Some(accented) = self.get_grave_accent(c, shift) {
                        return Some(accented.to_string());
                    }
                }

                if alt_gr {
                    return self.map_alt_gr(c, shift);
                }

                None
            }
        }
    }

    pub fn map_alt_gr(&self, c: char, shift: bool) -> Option<String> {
        let mapped = match (c.to_ascii_lowercase(), shift) {
            ('b', false) => Some('ɓ'),
            ('b', true)  => Some('Ɓ'),
            ('d', false) => Some('ɗ'),
            ('d', true)  => Some('Ɗ'),
            ('n', false) => Some('ŋ'),
            ('n', true)  => Some('Ŋ'),
            ('y', false) => Some('ƴ'),
            ('y', true)  => Some('Ƴ'),
            ('a', false) => Some('á'),
            ('a', true)  => Some('Á'),
            ('e', false) => Some('é'),
            ('e', true)  => Some('É'),
            ('i', false) => Some('í'),
            ('i', true)  => Some('Í'),
            ('o', false) => Some('ó'),
            ('o', true)  => Some('Ó'),
            ('u', false) => Some('ú'),
            ('u', true)  => Some('Ú'),
            ('\'', _)    => Some('’'),
            _ => None,
        };

        mapped.map(|ch| ch.to_string())
    }

    fn get_acute_accent(&self, c: char, shift: bool) -> Option<char> {
        match (c.to_ascii_lowercase(), shift) {
            ('a', false) => Some('á'),
            ('a', true)  => Some('Á'),
            ('e', false) => Some('é'),
            ('e', true)  => Some('É'),
            ('i', false) => Some('í'),
            ('i', true)  => Some('Í'),
            ('o', false) => Some('ó'),
            ('o', true)  => Some('Ó'),
            ('u', false) => Some('ú'),
            ('u', true)  => Some('Ú'),
            _ => None,
        }
    }

    fn get_grave_accent(&self, c: char, shift: bool) -> Option<char> {
        match (c.to_ascii_lowercase(), shift) {
            ('a', false) => Some('à'),
            ('a', true)  => Some('À'),
            ('e', false) => Some('è'),
            ('e', true)  => Some('È'),
            ('i', false) => Some('ì'),
            ('i', true)  => Some('Ì'),
            ('o', false) => Some('ò'),
            ('o', true)  => Some('Ò'),
            ('u', false) => Some('ù'),
            ('u', true)  => Some('Ù'),
            _ => None,
        }
    }
}
