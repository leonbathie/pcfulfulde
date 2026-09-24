#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

mod engine;
mod prediction;
mod stats;

use std::sync::Mutex;
use tauri::{
    CustomMenuItem, GlobalShortcutManager, Manager, SystemTray, SystemTrayEvent,
    SystemTrayMenu, SystemTrayMenuItem, Window,
};

use engine::{
    init_hook, inject_unicode_string, set_hook_enabled as set_hook_active,
    set_hook_mode, toggle_hook_mode, KeyboardMode,
};
use prediction::PredictionEngine;
use stats::{StatsTracker, TypingStats};

struct AppState {
    pub prediction_engine: Mutex<PredictionEngine>,
}

#[tauri::command]
fn get_keyboard_mode() -> String {
    if let Ok(mapper) = engine::hook::ENGINE_MAPPER.lock() {
        match mapper.mode {
            KeyboardMode::FulfuldeDirect => "Direct".into(),
            KeyboardMode::FulfuldeLatin => "Latin".into(),
            KeyboardMode::StandardQwerty => "Qwerty".into(),
        }
    } else {
        "Direct".into()
    }
}

#[tauri::command]
fn set_keyboard_mode(mode: String) -> String {
    let km = match mode.as_str() {
        "Latin" => KeyboardMode::FulfuldeLatin,
        "Qwerty" => KeyboardMode::StandardQwerty,
        _ => KeyboardMode::FulfuldeDirect,
    };
    set_hook_mode(km);
    mode
}

#[tauri::command]
fn toggle_keyboard_mode() -> String {
    let mode = toggle_hook_mode();
    match mode {
        KeyboardMode::FulfuldeDirect => "Direct".into(),
        KeyboardMode::FulfuldeLatin => "Latin".into(),
        KeyboardMode::StandardQwerty => "Qwerty".into(),
    }
}

#[tauri::command]
fn set_system_hook_enabled(enabled: bool) {
    set_hook_active(enabled);
}

#[tauri::command]
fn inject_text(text: String) {
    StatsTracker::record_keystroke();
    inject_unicode_string(&text);
}

#[tauri::command]
fn get_predictions(
    prefix: String,
    previous_word: Option<String>,
    state: tauri::State<AppState>,
) -> Vec<String> {
    if let Ok(engine) = state.prediction_engine.lock() {
        engine.predict(&prefix, previous_word.as_deref())
    } else {
        vec!["jam".into(), "noy".into(), "waali".into()]
    }
}

#[tauri::command]
fn get_typing_stats() -> TypingStats {
    StatsTracker::get_stats()
}

#[tauri::command]
fn record_keystroke() {
    StatsTracker::record_keystroke();
}

#[tauri::command]
fn record_word() {
    StatsTracker::record_word();
}

#[tauri::command]
fn toggle_always_on_top(window: Window, always_on_top: bool) -> Result<(), String> {
    window
        .set_always_on_top(always_on_top)
        .map_err(|e| e.to_string())
}

#[tauri::command]
fn close_window(window: Window) -> Result<(), String> {
    window.close().map_err(|e| e.to_string())
}

#[tauri::command]
fn minimize_window(window: Window) -> Result<(), String> {
    window.minimize().map_err(|e| e.to_string())
}

fn create_tray_menu() -> SystemTray {
    let toggle_view = CustomMenuItem::new("toggle_visibility".to_string(), "Afficher/Masquer le Clavier");
    let mode_direct = CustomMenuItem::new("mode_direct".to_string(), "Mode Fulfulde Direct");
    let mode_latin = CustomMenuItem::new("mode_latin".to_string(), "Mode Fulfulde AltGr");
    let quit = CustomMenuItem::new("quit".to_string(), "Quitter Clavier Fulfulde");

    let tray_menu = SystemTrayMenu::new()
        .add_item(toggle_view)
        .add_native_item(SystemTrayMenuItem::Separator)
        .add_item(mode_direct)
        .add_item(mode_latin)
        .add_native_item(SystemTrayMenuItem::Separator)
        .add_item(quit);

    SystemTray::new().with_menu(tray_menu)
}

fn main() {
    // Start native OS low-level interceptor
    init_hook();

    let state = AppState {
        prediction_engine: Mutex::new(PredictionEngine::new()),
    };

    tauri::Builder::default()
        .manage(state)
        .system_tray(create_tray_menu())
        .on_system_tray_event(|app, event| match event {
            SystemTrayEvent::MenuItemClick { id, .. } => match id.as_str() {
                "toggle_visibility" => {
                    if let Some(window) = app.get_window("main") {
                        if window.is_visible().unwrap_or(false) {
                            let _ = window.hide();
                        } else {
                            let _ = window.show();
                            let _ = window.set_focus();
                        }
                    }
                }
                "mode_direct" => {
                    set_hook_mode(KeyboardMode::FulfuldeDirect);
                    let _ = app.emit_all("mode_changed", "Direct");
                }
                "mode_latin" => {
                    set_hook_mode(KeyboardMode::FulfuldeLatin);
                    let _ = app.emit_all("mode_changed", "Latin");
                }
                "quit" => {
                    std::process::exit(0);
                }
                _ => {}
            },
            _ => {}
        })
        .setup(|app| {
            let mut shortcut_manager = app.global_shortcut_manager();
            let app_handle = app.handle();

            // Global shortcut Ctrl+Shift+L to toggle Direct <-> AltGr mode
            let _ = shortcut_manager.register("CommandOrControl+Shift+L", move || {
                let new_mode = toggle_hook_mode();
                let mode_str = match new_mode {
                    KeyboardMode::FulfuldeDirect => "Direct",
                    KeyboardMode::FulfuldeLatin => "Latin",
                    KeyboardMode::StandardQwerty => "Qwerty",
                };
                let _ = app_handle.emit_all("mode_changed", mode_str);
            });

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            get_keyboard_mode,
            set_keyboard_mode,
            toggle_keyboard_mode,
            set_system_hook_enabled,
            inject_text,
            get_predictions,
            get_typing_stats,
            record_keystroke,
            record_word,
            toggle_always_on_top,
            close_window,
            minimize_window
        ])
        .run(tauri::generate_context!())
        .expect("Erreur lors de l'exécution de l'application Clavier Fulfulde");
}
