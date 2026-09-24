pub mod mapping;
pub mod hook;

pub use mapping::{FulfuldeMapper, KeyboardMode, MappingRule};
pub use hook::{init_hook, set_hook_enabled, set_hook_mode, toggle_hook_mode, inject_unicode_string};
