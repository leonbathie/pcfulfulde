//! Vérifie le correcteur pulaar tel que les applications le voient : par le
//! service de correction de Windows (ISpellCheckerFactory), comme Edge ou le
//! Bloc-notes. Le correcteur doit d'abord être enregistré
//! (installer_clavier_pulaar.ps1).
//!
//!     cargo +stable-x86_64-pc-windows-gnu run --release --example verifie

use std::ffi::c_void;

use windows::core::{Interface, PCWSTR, PWSTR};
use windows::Win32::Foundation::S_OK;
use windows::Win32::Globalization::{ISpellCheckerFactory, ISpellingError, SpellCheckerFactory};
use windows::Win32::System::Com::{
    CoCreateInstance, CoInitializeEx, CoTaskMemFree, IEnumString, CLSCTX_INPROC_SERVER, COINIT_MULTITHREADED,
};

fn large(texte: &str) -> Vec<u16> {
    texte.encode_utf16().chain(std::iter::once(0)).collect()
}

unsafe fn chaines(liste: &IEnumString) -> Vec<String> {
    let mut sortie = Vec::new();
    loop {
        let mut element = [PWSTR(std::ptr::null_mut())];
        let mut lus = 0u32;
        let hr = liste.Next(&mut element, &mut lus);
        if lus == 0 || element[0].is_null() {
            break;
        }
        sortie.push(element[0].to_string().unwrap_or_default());
        CoTaskMemFree(element[0].0 as *const c_void);
        if hr != S_OK {
            break;
        }
    }
    sortie
}

fn main() -> windows::core::Result<()> {
    unsafe {
        CoInitializeEx(std::ptr::null(), COINIT_MULTITHREADED)?;
        let fabrique: ISpellCheckerFactory = CoCreateInstance(&SpellCheckerFactory, None, CLSCTX_INPROC_SERVER)?;
        for langue in ["ff-Latn-SN", "ff", "fr-FR"] {
            let l = large(langue);
            println!("{langue:<11} pris en charge : {}", fabrique.IsSupported(PCWSTR(l.as_ptr()))?.as_bool());
        }

        let langue = large("ff-Latn-SN");
        let correcteur = fabrique.CreateSpellChecker(PCWSTR(langue.as_ptr()))?;
        let texte = "Mi yiɗi fulbe e jaraama, ko ɓernde am. ONU haal-pulaar Fulbe miido.";
        println!("\nTexte : {texte}");
        let unites: Vec<u16> = texte.encode_utf16().collect();
        let t = large(texte);
        let erreurs = correcteur.Check(PCWSTR(t.as_ptr()))?;
        loop {
            // Next est appelé à la main : l'enveloppe de windows 0.39 prend
            // S_FALSE (plus d'erreur) pour un succès avec un pointeur nul.
            let mut brut: *mut c_void = std::ptr::null_mut();
            let hr = (Interface::vtable(&erreurs).Next)(Interface::as_raw(&erreurs), &mut brut);
            if hr != S_OK || brut.is_null() {
                break;
            }
            let erreur: ISpellingError = std::mem::transmute(brut);
            let debut = erreur.StartIndex()? as usize;
            let longueur = erreur.Length()? as usize;
            let mot = String::from_utf16_lossy(&unites[debut..debut + longueur]);
            let m = large(&mot);
            let suggestions = chaines(&correcteur.Suggest(PCWSTR(m.as_ptr()))?);
            println!("  souligné : {mot:<10} -> {}", suggestions.join(", "));
        }
    }
    Ok(())
}
