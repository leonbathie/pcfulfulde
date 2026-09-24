use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Mutex};
use lazy_static::lazy_static;
use super::mapping::{FulfuldeMapper, KeyboardMode};

lazy_static! {
    pub static ref HOOK_ENABLED: AtomicBool = AtomicBool::new(true);
    pub static ref IS_INJECTING: AtomicBool = AtomicBool::new(false);
    pub static ref ENGINE_MAPPER: Arc<Mutex<FulfuldeMapper>> = Arc::new(Mutex::new(FulfuldeMapper::new()));
}

/// Start the low-level OS keyboard interceptor hook
pub fn init_hook() {
    #[cfg(windows)]
    {
        std::thread::spawn(|| {
            unsafe {
                windows_hook_loop();
            }
        });
    }
    #[cfg(not(windows))]
    {
        // For non-Windows platforms (macOS / Linux), the virtual keyboard and frontend injection are active
        println!("Native OS hook initialized in fallback mode for macOS/Linux.");
    }
}

pub fn set_hook_mode(mode: KeyboardMode) {
    if let Ok(mut mapper) = ENGINE_MAPPER.lock() {
        mapper.set_mode(mode);
    }
}

pub fn toggle_hook_mode() -> KeyboardMode {
    if let Ok(mut mapper) = ENGINE_MAPPER.lock() {
        mapper.toggle_mode()
    } else {
        KeyboardMode::FulfuldeLatin
    }
}

pub fn set_hook_enabled(enabled: bool) {
    HOOK_ENABLED.store(enabled, Ordering::SeqCst);
}

/// Direct programmatic Unicode text injection (e.g. from Virtual Keyboard click or suggestion bar)
pub fn inject_unicode_string(text: &str) {
    #[cfg(windows)]
    unsafe {
        use winapi::um::winuser::{SendInput, INPUT, INPUT_KEYBOARD, KEYEVENTF_KEYUP, KEYEVENTF_UNICODE, KEYBDINPUT};
        
        IS_INJECTING.store(true, Ordering::SeqCst);

        let utf16: Vec<u16> = text.encode_utf16().collect();
        let mut inputs: Vec<INPUT> = Vec::with_capacity(utf16.len() * 2);

        for &c in &utf16 {
            let mut input_down: INPUT = std::mem::zeroed();
            input_down.type_ = INPUT_KEYBOARD;
            let mut kb_down: KEYBDINPUT = std::mem::zeroed();
            kb_down.wScan = c;
            kb_down.dwFlags = KEYEVENTF_UNICODE;
            *input_down.u.ki_mut() = kb_down;
            inputs.push(input_down);

            let mut input_up: INPUT = std::mem::zeroed();
            input_up.type_ = INPUT_KEYBOARD;
            let mut kb_up: KEYBDINPUT = std::mem::zeroed();
            kb_up.wScan = c;
            kb_up.dwFlags = KEYEVENTF_UNICODE | KEYEVENTF_KEYUP;
            *input_up.u.ki_mut() = kb_up;
            inputs.push(input_up);
        }

        if !inputs.is_empty() {
            SendInput(
                inputs.len() as u32,
                inputs.as_mut_ptr(),
                std::mem::size_of::<INPUT>() as i32,
            );
        }

        IS_INJECTING.store(false, Ordering::SeqCst);
    }

    #[cfg(not(windows))]
    {
        println!("Injecting unicode string on non-windows: {}", text);
    }
}

#[cfg(windows)]
unsafe fn windows_hook_loop() {
    use winapi::shared::minwindef::{LPARAM, LRESULT, WPARAM};
    use winapi::um::libloaderapi::GetModuleHandleW;
    use winapi::um::winuser::{
        CallNextHookEx, GetAsyncKeyState, GetMessageW, SetWindowsHookExW,
        KBDLLHOOKSTRUCT, MSG, VK_CONTROL, VK_LCONTROL, VK_LMENU, VK_MENU,
        VK_RCONTROL, VK_RMENU, VK_SHIFT, WH_KEYBOARD_LL, WM_KEYDOWN, WM_SYSKEYDOWN,
    };

    unsafe extern "system" fn hook_callback(
        n_code: i32,
        w_param: WPARAM,
        l_param: LPARAM,
    ) -> LRESULT {
        if n_code >= 0 && (w_param == WM_KEYDOWN as WPARAM || w_param == WM_SYSKEYDOWN as WPARAM) {
            if !IS_INJECTING.load(Ordering::SeqCst) && HOOK_ENABLED.load(Ordering::SeqCst) {
                let kbd = *(l_param as *const KBDLLHOOKSTRUCT);
                let vk_code = kbd.vkCode as i32;

                // Check modifier states
                let shift_down = (GetAsyncKeyState(VK_SHIFT) as u16 & 0x8000) != 0;
                let ctrl_down = (GetAsyncKeyState(VK_CONTROL) as u16 & 0x8000) != 0
                    || (GetAsyncKeyState(VK_LCONTROL) as u16 & 0x8000) != 0;
                let alt_down = (GetAsyncKeyState(VK_MENU) as u16 & 0x8000) != 0
                    || (GetAsyncKeyState(VK_LMENU) as u16 & 0x8000) != 0;
                let r_alt_down = (GetAsyncKeyState(VK_RMENU) as u16 & 0x8000) != 0;
                let r_ctrl_down = (GetAsyncKeyState(VK_RCONTROL) as u16 & 0x8000) != 0;

                // AltGr is equivalent to Right Alt or (Ctrl + Alt)
                let is_alt_gr = r_alt_down || (ctrl_down && alt_down) || (r_ctrl_down && r_alt_down);

                // Convert virtual key to ASCII character if alphanumeric or punctuation
                let char_candidate = match vk_code {
                    0x41..=0x5A => {
                        let base = (b'a' + (vk_code - 0x41) as u8) as char;
                        Some(base)
                    }
                    0x30..=0x39 => {
                        let base = (b'0' + (vk_code - 0x30) as u8) as char;
                        Some(base)
                    }
                    0xC0 => Some('`'), // VK_OEM_3 (tilde / grave)
                    0xDE => Some('\''), // VK_OEM_7 (single quote)
                    _ => None,
                };

                if let Some(c) = char_candidate {
                    if let Ok(mut mapper) = ENGINE_MAPPER.lock() {
                        if let Some(replacement) = mapper.map_key(c, shift_down, is_alt_gr, ctrl_down && !is_alt_gr) {
                            if !replacement.is_empty() {
                                inject_unicode_string(&replacement);
                            }
                            return 1; // Suppress original keystroke
                        }
                    }
                }
            }
        }

        CallNextHookEx(std::ptr::null_mut(), n_code, w_param, l_param)
    }

    let h_instance = GetModuleHandleW(std::ptr::null());
    let hook = SetWindowsHookExW(WH_KEYBOARD_LL, Some(hook_callback), h_instance, 0);

    if hook.is_null() {
        eprintln!("Failed to install low-level keyboard hook.");
        return;
    }

    let mut msg: MSG = std::mem::zeroed();
    while GetMessageW(&mut msg, std::ptr::null_mut(), 0, 0) > 0 {
        // Message loop runs on dedicated thread
    }
}
