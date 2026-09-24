//! Correcteur orthographique pulaar pour Windows.
//!
//! Un fournisseur de la « Spell Checking API » de Windows : une fois
//! enregistré, Edge, Chrome, le Bloc-notes et les autres applications qui se
//! servent du correcteur de Windows soulignent les mots pulaar mal écrits et
//! proposent leurs corrections, comme pour le français ou l'anglais.
//!
//! Windows charge cette DLL dans son propre processus, sous une identité
//! restreinte : elle doit se trouver, avec `mots_pulaar.txt`, dans un dossier
//! lisible par « ALL APPLICATION PACKAGES ».

#![allow(non_snake_case)]

use std::cmp::Reverse;
use std::collections::{HashMap, HashSet};
use std::ffi::c_void;
use std::path::PathBuf;
use std::sync::{Arc, Mutex, MutexGuard, OnceLock, RwLock};

use windows::core::{implement, Error, IUnknown, Interface, Result, GUID, HRESULT, PCWSTR, PWSTR};
use windows::Win32::Foundation::{
    BOOL, CLASS_E_CLASSNOTAVAILABLE, CLASS_E_NOAGGREGATION, E_INVALIDARG, E_OUTOFMEMORY, E_POINTER, HINSTANCE, S_FALSE,
    S_OK,
};
use windows::Win32::Globalization::{
    IEnumSpellingError, IEnumSpellingError_Impl, IOptionDescription, ISpellCheckProvider, ISpellCheckProviderFactory,
    ISpellCheckProviderFactory_Impl, ISpellCheckProvider_Impl, ISpellingError, ISpellingError_Impl, CORRECTIVE_ACTION,
    CORRECTIVE_ACTION_GET_SUGGESTIONS, CORRECTIVE_ACTION_REPLACE, WORDLIST_TYPE, WORDLIST_TYPE_ADD,
    WORDLIST_TYPE_AUTOCORRECT, WORDLIST_TYPE_EXCLUDE, WORDLIST_TYPE_IGNORE,
};
use windows::Win32::System::Com::{CoTaskMemAlloc, CoTaskMemFree, IClassFactory, IClassFactory_Impl, IEnumString, IEnumString_Impl};
use windows::Win32::System::LibraryLoader::{
    GetModuleFileNameW, GetModuleHandleExW, GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS,
    GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
};

/// CLSID du correcteur : le registre le relie à cette DLL.
pub const CLSID_CORRECTEUR_PULAAR: GUID = GUID::from_u128(0xba4f4fd0_8bb2_49e2_9b55_b3350bc1a5b5);

const IDENTIFIANT: &str = "ClavierPulaar";
const NOM: &str = "Correcteur pulaar (Clavier Pulaar)";
/// Langues annoncées à Windows : le pulaar du Sénégal, et le peul en général.
const LANGUES: [&str; 4] = ["ff-Latn-SN", "ff-SN", "ff-Latn", "ff"];
/// Lettres des clés normalisées : ɓ, ɗ, ŋ, ñ, ƴ y sont déjà rabattues.
const ALPHABET: &str = "abcdefghijklmnoprstuwy";
const APOSTROPHES: [char; 5] = ['’', '\'', '`', '‘', 'ʼ'];
const SUGGESTIONS_MAX: usize = 6;
/// HRESULT_FROM_WIN32(ERROR_FILE_NOT_FOUND) : mots_pulaar.txt introuvable.
const FICHIER_INTROUVABLE: HRESULT = HRESULT(0x8007_0002_u32 as i32);

static DICTIONNAIRE: OnceLock<Option<Arc<Dictionnaire>>> = OnceLock::new();

fn langue_prise(tag: &str) -> bool {
    let tag = tag.to_ascii_lowercase();
    tag == "ff" || tag.starts_with("ff-")
}

/// Forme de référence d'un mot : minuscules, hamza en ’.
fn forme(mot: &str) -> String {
    mot.chars()
        .flat_map(char::to_lowercase)
        .map(|c| if APOSTROPHES.contains(&c) { '’' } else { c })
        .collect()
}

/// Clé de recherche, sans crochets, hamza ni accents : fulɓe -> fulbe.
fn cle(mot: &str) -> String {
    let mut sortie = String::with_capacity(mot.len());
    for c in mot.chars().flat_map(char::to_lowercase) {
        match c {
            'ɓ' => sortie.push('b'),
            'ɗ' => sortie.push('d'),
            'ŋ' | 'ñ' | 'ɲ' => sortie.push('n'),
            'ƴ' => sortie.push('y'),
            'á' | 'à' | 'â' | 'ä' => sortie.push('a'),
            'é' | 'è' | 'ê' | 'ë' => sortie.push('e'),
            'í' | 'ì' | 'î' | 'ï' => sortie.push('i'),
            'ó' | 'ò' | 'ô' | 'ö' => sortie.push('o'),
            'ú' | 'ù' | 'û' | 'ü' => sortie.push('u'),
            c if APOSTROPHES.contains(&c) => {}
            c => sortie.push(c),
        }
    }
    sortie
}

/// Les clés à une lettre de `cle` : changée, oubliée, en trop ou intervertie.
fn variantes(cle: &str) -> HashSet<String> {
    let lettres: Vec<char> = cle.chars().collect();
    let mut sortie = HashSet::new();
    for i in 0..=lettres.len() {
        for c in ALPHABET.chars() {
            let mut v = lettres.clone();
            v.insert(i, c);
            sortie.insert(v.into_iter().collect());
        }
        if i < lettres.len() {
            let mut v = lettres.clone();
            v.remove(i);
            sortie.insert(v.into_iter().collect());
            for c in ALPHABET.chars() {
                let mut v = lettres.clone();
                v[i] = c;
                sortie.insert(v.into_iter().collect());
            }
            if i + 1 < lettres.len() {
                let mut v = lettres.clone();
                v.swap(i, i + 1);
                sortie.insert(v.into_iter().collect());
            }
        }
    }
    sortie.remove(cle);
    sortie
}

/// Reporte la majuscule du mot tapé sur la suggestion (Fulbe -> Fulɓe).
fn casse(modele: &str, mot: &str) -> String {
    let lettres: Vec<char> = modele.chars().filter(|c| c.is_alphabetic()).collect();
    if lettres.len() >= 2 && lettres.iter().all(|c| c.is_uppercase()) {
        return mot.to_uppercase();
    }
    if lettres.first().is_some_and(|c| c.is_uppercase()) {
        let mut reste = mot.chars();
        if let Some(premiere) = reste.next() {
            return premiere.to_uppercase().chain(reste).collect();
        }
    }
    mot.to_string()
}

fn verrou<T>(m: &Mutex<T>) -> MutexGuard<'_, T> {
    m.lock().unwrap_or_else(|empoisonne| empoisonne.into_inner())
}

/// Chaîne allouée pour COM : c'est l'appelant qui la libère (CoTaskMemFree).
fn chaine_com(texte: &str) -> Result<PWSTR> {
    let large: Vec<u16> = texte.encode_utf16().chain(std::iter::once(0)).collect();
    unsafe {
        let p = CoTaskMemAlloc(large.len() * 2) as *mut u16;
        if p.is_null() {
            return Err(E_OUTOFMEMORY.into());
        }
        std::ptr::copy_nonoverlapping(large.as_ptr(), p, large.len());
        Ok(PWSTR(p))
    }
}

fn lit(texte: &PCWSTR) -> Result<String> {
    if texte.is_null() {
        return Err(E_POINTER.into());
    }
    unsafe { texte.to_string() }.map_err(|_| Error::from(E_INVALIDARG))
}

fn lit_liste(liste: &IEnumString) -> Vec<String> {
    let mut sortie = Vec::new();
    loop {
        let mut element = [PWSTR(std::ptr::null_mut())];
        let mut lus = 0u32;
        let hr = unsafe { liste.Next(&mut element, &mut lus) };
        if lus == 0 || element[0].is_null() {
            break;
        }
        unsafe {
            if let Ok(mot) = element[0].to_string() {
                sortie.push(mot);
            }
            CoTaskMemFree(element[0].0 as *const c_void);
        }
        if hr != S_OK {
            break;
        }
    }
    sortie
}

/// Le dossier de cette DLL : `mots_pulaar.txt` y est rangé à côté.
fn dossier_de_la_dll() -> Option<PathBuf> {
    let mut module = HINSTANCE::default();
    let trouve = unsafe {
        GetModuleHandleExW(
            GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS | GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
            PCWSTR(dossier_de_la_dll as *const u16),
            &mut module,
        )
    };
    if !trouve.as_bool() {
        return None;
    }
    let mut tampon = vec![0u16; 2048];
    let n = unsafe { GetModuleFileNameW(module, &mut tampon) } as usize;
    if n == 0 || n >= tampon.len() {
        return None;
    }
    PathBuf::from(String::from_utf16_lossy(&tampon[..n])).parent().map(PathBuf::from)
}

// --- Le dictionnaire -------------------------------------------------------

struct Dictionnaire {
    frequences: HashMap<String, u32>,
    par_cle: HashMap<String, Vec<String>>,
}

#[derive(Default)]
struct Listes {
    ajoutes: HashSet<String>,
    exclus: HashSet<String>,
    ignores: HashSet<String>,
    autocorrect: HashMap<String, String>,
}

#[derive(Clone)]
struct ErreurTrouvee {
    debut: u32,
    longueur: u32,
    action: CORRECTIVE_ACTION,
    remplacement: String,
}

fn fait_partie_d_un_mot(c: char) -> bool {
    c.is_alphabetic() || APOSTROPHES.contains(&c) || c == '-'
}

impl Dictionnaire {
    fn depuis_texte(texte: &str) -> Dictionnaire {
        let mut frequences = HashMap::new();
        let mut par_cle: HashMap<String, Vec<String>> = HashMap::new();
        for ligne in texte.lines() {
            if ligne.starts_with('#') {
                continue;
            }
            let mut colonnes = ligne.split('\t');
            let Some(mot) = colonnes.next().filter(|m| !m.is_empty()) else { continue };
            let frequence = colonnes.next().and_then(|f| f.trim().parse().ok()).unwrap_or(1);
            let mot = forme(mot);
            par_cle.entry(cle(&mot)).or_default().push(mot.clone());
            frequences.insert(mot, frequence);
        }
        Dictionnaire { frequences, par_cle }
    }

    fn charge() -> Option<Dictionnaire> {
        let texte = std::fs::read_to_string(dossier_de_la_dll()?.join("mots_pulaar.txt")).ok()?;
        Some(Dictionnaire::depuis_texte(&texte))
    }

    fn frequence(&self, mot: &str) -> u32 {
        self.frequences.get(mot).copied().unwrap_or(0)
    }

    fn connait(&self, forme: &str) -> bool {
        self.frequences.contains_key(forme)
    }

    /// Les corrections d'un mot, les plus courantes d'abord.
    fn suggestions(&self, mot: &str) -> Vec<String> {
        let f = forme(mot);
        let k = cle(&f);
        let mut sortie: Vec<String> = Vec::new();
        // 1. Les mêmes lettres, avec les crochets ou la hamza : fulbe -> fulɓe
        let mut memes: Vec<&String> =
            self.par_cle.get(&k).map(|v| v.iter().filter(|m| **m != f).collect()).unwrap_or_default();
        memes.sort_by_key(|m| Reverse(self.frequence(m)));
        sortie.extend(memes.into_iter().cloned());
        // 2. Une lettre de différence : jaraama -> jaaraama
        if k.chars().count() >= 3 {
            let mut proches: Vec<(&String, u32)> = variantes(&k)
                .iter()
                .filter_map(|v| self.par_cle.get(v))
                .flatten()
                .map(|m| (m, self.frequence(m)))
                .collect();
            proches.sort_by(|a, b| b.1.cmp(&a.1).then_with(|| a.0.cmp(b.0)));
            for (m, _) in proches {
                if !sortie.contains(m) {
                    sortie.push(m.clone());
                }
            }
        }
        sortie.truncate(SUGGESTIONS_MAX);
        sortie.iter().map(|s| casse(mot, s)).collect()
    }

    /// Les mots inconnus de `texte`, avec leur place en caractères UTF-16.
    fn erreurs(&self, texte: &[u16], listes: &Listes) -> Vec<ErreurTrouvee> {
        let mut sortie = Vec::new();
        let mut mot = String::new();
        let mut debut = 0usize;
        let mut position = 0usize;
        for c in char::decode_utf16(texte.iter().copied()).map(|r| r.unwrap_or(char::REPLACEMENT_CHARACTER)) {
            if fait_partie_d_un_mot(c) {
                if mot.is_empty() {
                    debut = position;
                }
                mot.push(c);
            } else if !mot.is_empty() {
                self.examine(&mot, debut, listes, &mut sortie);
                mot.clear();
            }
            position += c.len_utf16();
        }
        if !mot.is_empty() {
            self.examine(&mot, debut, listes, &mut sortie);
        }
        sortie
    }

    fn examine(&self, brut: &str, debut: usize, listes: &Listes, sortie: &mut Vec<ErreurTrouvee>) {
        // Apostrophes et tirets au bord du mot sont de la ponctuation.
        let bord = |c: char| APOSTROPHES.contains(&c) || c == '-';
        let avant: usize = brut.chars().take_while(|c| bord(*c)).map(char::len_utf16).sum();
        let mot = brut.trim_matches(bord);
        if mot.chars().count() < 2 {
            return;
        }
        // Les sigles (ONU, RFI) ne sont pas des mots à corriger.
        let lettres: Vec<char> = mot.chars().filter(|c| c.is_alphabetic()).collect();
        if lettres.len() >= 2 && lettres.iter().all(|c| c.is_uppercase()) {
            return;
        }
        let f = forme(mot);
        let exclu = listes.exclus.contains(&f);
        let accepte = |m: &str| self.connait(m) || listes.ajoutes.contains(m) || listes.ignores.contains(m);
        if !exclu && accepte(&f) {
            return;
        }
        // Un mot composé dont chaque partie est connue : haal-pulaar
        if !exclu && f.contains('-') && f.split('-').all(|p| p.is_empty() || accepte(p)) {
            return;
        }
        let (action, remplacement) = match listes.autocorrect.get(&f) {
            Some(r) => (CORRECTIVE_ACTION_REPLACE, casse(mot, r)),
            None => (CORRECTIVE_ACTION_GET_SUGGESTIONS, String::new()),
        };
        sortie.push(ErreurTrouvee {
            debut: (debut + avant) as u32,
            longueur: mot.encode_utf16().count() as u32,
            action,
            remplacement,
        });
    }
}

// --- Les objets COM que Windows interroge ----------------------------------

#[implement(ISpellingError)]
struct Erreur {
    erreur: ErreurTrouvee,
}

impl ISpellingError_Impl for Erreur {
    fn StartIndex(&self) -> Result<u32> {
        Ok(self.erreur.debut)
    }

    fn Length(&self) -> Result<u32> {
        Ok(self.erreur.longueur)
    }

    fn CorrectiveAction(&self) -> Result<CORRECTIVE_ACTION> {
        Ok(self.erreur.action)
    }

    fn Replacement(&self) -> Result<PWSTR> {
        chaine_com(&self.erreur.remplacement)
    }
}

#[implement(IEnumSpellingError)]
struct Erreurs {
    liste: Vec<ErreurTrouvee>,
    suivant: Mutex<usize>,
}

impl IEnumSpellingError_Impl for Erreurs {
    /// S_FALSE une fois toutes les erreurs rendues.
    fn Next(&self) -> Result<ISpellingError> {
        let mut suivant = verrou(&self.suivant);
        let Some(erreur) = self.liste.get(*suivant).cloned() else {
            return Err(S_FALSE.into());
        };
        *suivant += 1;
        Ok(Erreur { erreur }.into())
    }
}

#[implement(IEnumString)]
struct Chaines {
    liste: Arc<Vec<String>>,
    suivant: Mutex<usize>,
}

impl Chaines {
    fn nouvelles(liste: Vec<String>) -> IEnumString {
        Chaines { liste: Arc::new(liste), suivant: Mutex::new(0) }.into()
    }
}

impl IEnumString_Impl for Chaines {
    fn Next(&self, celt: u32, rgelt: *mut PWSTR, pceltfetched: *mut u32) -> HRESULT {
        if rgelt.is_null() {
            return E_POINTER;
        }
        let mut suivant = verrou(&self.suivant);
        let mut n = 0u32;
        while n < celt && *suivant < self.liste.len() {
            match chaine_com(&self.liste[*suivant]) {
                Ok(p) => unsafe { *rgelt.add(n as usize) = p },
                Err(e) => return e.code(),
            }
            *suivant += 1;
            n += 1;
        }
        if !pceltfetched.is_null() {
            unsafe { *pceltfetched = n };
        }
        if n == celt {
            S_OK
        } else {
            S_FALSE
        }
    }

    fn Skip(&self, celt: u32) -> HRESULT {
        let mut suivant = verrou(&self.suivant);
        let cible = *suivant + celt as usize;
        *suivant = cible.min(self.liste.len());
        if cible <= self.liste.len() {
            S_OK
        } else {
            S_FALSE
        }
    }

    fn Reset(&self) -> Result<()> {
        *verrou(&self.suivant) = 0;
        Ok(())
    }

    fn Clone(&self) -> Result<IEnumString> {
        let position = *verrou(&self.suivant);
        Ok(Chaines { liste: self.liste.clone(), suivant: Mutex::new(position) }.into())
    }
}

#[implement(ISpellCheckProvider)]
struct Fournisseur {
    langue: String,
    dictionnaire: Arc<Dictionnaire>,
    listes: RwLock<Listes>,
}

impl ISpellCheckProvider_Impl for Fournisseur {
    fn LanguageTag(&self) -> Result<PWSTR> {
        chaine_com(&self.langue)
    }

    fn Check(&self, text: &PCWSTR) -> Result<IEnumSpellingError> {
        if text.is_null() {
            return Err(E_POINTER.into());
        }
        let texte = unsafe { text.as_wide() };
        let listes = self.listes.read().unwrap_or_else(|e| e.into_inner());
        let liste = self.dictionnaire.erreurs(texte, &listes);
        Ok(Erreurs { liste, suivant: Mutex::new(0) }.into())
    }

    fn Suggest(&self, word: &PCWSTR) -> Result<IEnumString> {
        let mot = lit(word)?;
        let listes = self.listes.read().unwrap_or_else(|e| e.into_inner());
        let mut suggestions = Vec::new();
        if let Some(remplacement) = listes.autocorrect.get(&forme(&mot)) {
            suggestions.push(casse(&mot, remplacement));
        }
        for s in self.dictionnaire.suggestions(&mot) {
            if !suggestions.contains(&s) {
                suggestions.push(s);
            }
        }
        suggestions.truncate(SUGGESTIONS_MAX);
        Ok(Chaines::nouvelles(suggestions))
    }

    fn GetOptionValue(&self, _optionid: &PCWSTR) -> Result<u8> {
        Err(E_INVALIDARG.into())
    }

    fn SetOptionValue(&self, _optionid: &PCWSTR, _value: u8) -> Result<()> {
        Err(E_INVALIDARG.into())
    }

    fn OptionIds(&self) -> Result<IEnumString> {
        Ok(Chaines::nouvelles(Vec::new()))
    }

    fn Id(&self) -> Result<PWSTR> {
        chaine_com(IDENTIFIANT)
    }

    fn LocalizedName(&self) -> Result<PWSTR> {
        chaine_com(NOM)
    }

    fn GetOptionDescription(&self, _optionid: &PCWSTR) -> Result<IOptionDescription> {
        Err(E_INVALIDARG.into())
    }

    fn InitializeWordlist(&self, wordlisttype: WORDLIST_TYPE, words: &Option<IEnumString>) -> Result<()> {
        let mots = words.as_ref().map(lit_liste).unwrap_or_default();
        let ensemble = || mots.iter().map(|m| forme(m)).collect::<HashSet<_>>();
        let mut listes = self.listes.write().unwrap_or_else(|e| e.into_inner());
        match wordlisttype {
            WORDLIST_TYPE_ADD => listes.ajoutes = ensemble(),
            WORDLIST_TYPE_EXCLUDE => listes.exclus = ensemble(),
            WORDLIST_TYPE_IGNORE => listes.ignores = ensemble(),
            WORDLIST_TYPE_AUTOCORRECT => {
                listes.autocorrect = mots
                    .iter()
                    .filter_map(|m| m.split_once(['|', '\t']))
                    .map(|(faute, bon)| (forme(faute.trim()), bon.trim().to_string()))
                    .collect();
            }
            _ => {}
        }
        Ok(())
    }
}

#[implement(ISpellCheckProviderFactory)]
struct FabriqueDeFournisseurs;

impl ISpellCheckProviderFactory_Impl for FabriqueDeFournisseurs {
    fn SupportedLanguages(&self) -> Result<IEnumString> {
        Ok(Chaines::nouvelles(LANGUES.iter().map(|l| l.to_string()).collect()))
    }

    fn IsSupported(&self, languagetag: &PCWSTR) -> Result<BOOL> {
        Ok(langue_prise(&lit(languagetag)?).into())
    }

    fn CreateSpellCheckProvider(&self, languagetag: &PCWSTR) -> Result<ISpellCheckProvider> {
        let langue = lit(languagetag)?;
        if !langue_prise(&langue) {
            return Err(E_INVALIDARG.into());
        }
        let dictionnaire = DICTIONNAIRE
            .get_or_init(|| Dictionnaire::charge().map(Arc::new))
            .clone()
            .ok_or_else(|| Error::from(FICHIER_INTROUVABLE))?;
        Ok(Fournisseur { langue, dictionnaire, listes: RwLock::new(Listes::default()) }.into())
    }
}

#[implement(IClassFactory)]
struct Fabrique;

impl IClassFactory_Impl for Fabrique {
    fn CreateInstance(&self, punkouter: &Option<IUnknown>, riid: *const GUID, ppvobject: *mut *mut c_void) -> Result<()> {
        if ppvobject.is_null() || riid.is_null() {
            return Err(E_POINTER.into());
        }
        unsafe { *ppvobject = std::ptr::null_mut() };
        if punkouter.is_some() {
            return Err(CLASS_E_NOAGGREGATION.into());
        }
        let fabrique: ISpellCheckProviderFactory = FabriqueDeFournisseurs.into();
        unsafe { fabrique.query(&*riid, ppvobject as *mut *const c_void).ok() }
    }

    fn LockServer(&self, _flock: BOOL) -> Result<()> {
        Ok(())
    }
}

/// Point d'entrée COM : Windows demande ici la fabrique du correcteur.
///
/// # Safety
/// Appelée par COM avec des pointeurs valides.
#[no_mangle]
pub unsafe extern "system" fn DllGetClassObject(rclsid: *const GUID, riid: *const GUID, ppv: *mut *mut c_void) -> HRESULT {
    if ppv.is_null() || riid.is_null() {
        return E_POINTER;
    }
    *ppv = std::ptr::null_mut();
    if rclsid.is_null() || *rclsid != CLSID_CORRECTEUR_PULAAR {
        return CLASS_E_CLASSNOTAVAILABLE;
    }
    let fabrique: IClassFactory = Fabrique.into();
    fabrique.query(&*riid, ppv as *mut *const c_void)
}

/// Le correcteur reste chargé tant que le service de Windows le garde.
#[no_mangle]
pub extern "system" fn DllCanUnloadNow() -> HRESULT {
    S_FALSE
}

#[cfg(test)]
mod tests {
    use super::*;

    fn dictionnaire() -> Dictionnaire {
        Dictionnaire::depuis_texte("# test\nfulɓe\t362\nɓe\t9021\njaaraama\t236\nmiɗo\t500\nhaal-pulaar\t3\nko\t51513\n")
    }

    fn mots_fautifs(texte: &str) -> Vec<String> {
        let large: Vec<u16> = texte.encode_utf16().collect();
        dictionnaire()
            .erreurs(&large, &Listes::default())
            .iter()
            .map(|e| String::from_utf16_lossy(&large[e.debut as usize..(e.debut + e.longueur) as usize]))
            .collect()
    }

    #[test]
    fn souligne_les_mots_inconnus_et_laisse_les_autres() {
        assert_eq!(mots_fautifs("Fulɓe ko jaaraama, fulbe jaraama."), vec!["fulbe", "jaraama"]);
    }

    #[test]
    fn respecte_sigles_composes_et_apostrophes_de_bord() {
        assert!(mots_fautifs("ONU haal-pulaar ‘ko’ miɗo").is_empty());
    }

    #[test]
    fn propose_les_crochets_puis_une_lettre_pres() {
        let d = dictionnaire();
        assert_eq!(d.suggestions("fulbe")[0], "fulɓe");
        assert_eq!(d.suggestions("Fulbe")[0], "Fulɓe");
        assert_eq!(d.suggestions("jaraama")[0], "jaaraama");
        assert_eq!(d.suggestions("be")[0], "ɓe");
    }
}
