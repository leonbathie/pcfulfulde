#include <windows.h>
#include <string.h>

#define SHFT_INVALID 0x0F
#define KBD_TYPE 4

#define KBDSHIFT     0x0001
#define KBDCTRL      0x0002
#define KBDALT       0x0004
#define KBDKLLF_ALTGR 0x0008

#define TYPEDEF_VK_TO_WCHARS(n) \
typedef struct _VK_TO_WCHARS##n { \
    BYTE  VirtualKey; \
    BYTE  Attributes; \
    WCHAR wch[n]; \
} VK_TO_WCHARS##n, *PVK_TO_WCHARS##n;

TYPEDEF_VK_TO_WCHARS(1)
TYPEDEF_VK_TO_WCHARS(2)
TYPEDEF_VK_TO_WCHARS(3)
TYPEDEF_VK_TO_WCHARS(4)
TYPEDEF_VK_TO_WCHARS(5)
TYPEDEF_VK_TO_WCHARS(6)

typedef struct _VK_TO_WCHAR_TABLE {
    PVK_TO_WCHARS1 pVkToWchars;
    BYTE           nModifications;
    BYTE           cbSize;
} VK_TO_WCHAR_TABLE, *PVK_TO_WCHAR_TABLE;

typedef struct _MODIFIERS {
    PVK_TO_WCHARS1 pVkToWchars;
    WORD           wMaxModBits;
    BYTE           ModNumber[8];
} MODIFIERS, *PMODIFIERS;

typedef struct _VSC_LPWSTR {
    BYTE   vsc;
    LPWSTR pwsz;
} VSC_LPWSTR, *PVSC_LPWSTR;

typedef struct _VSC_VK {
    BYTE  Vsc;
    USHORT Vk;
} VSC_VK, *PVSC_VK;

typedef struct _DEADKEY {
    DWORD dwBoth;
    WCHAR wchComposed;
    USHORT uFlags;
} DEADKEY, *PDEADKEY;

typedef struct _KBDTABLES {
    PMODIFIERS         pCharModifiers;
    PVK_TO_WCHAR_TABLE pVkToWcharTable;
    PDEADKEY           pDeadKey;
    PVSC_LPWSTR        pKeyNames;
    PVSC_LPWSTR        pKeyNamesExt;
    LPWSTR            *pKeyNamesDead;
    USHORT            *pusVSCtoVK;
    BYTE               bMaxVSCtoVK;
    PVSC_VK            pVSCtoVK_E0;
    PVSC_VK            pVSCtoVK_E1;
    DWORD              fLocaleFlags;
    BYTE               nLgMax;
    BYTE               cbLgEntry;
    PVOID              pLigature;
    DWORD              dwType;
    DWORD              dwSubType;
} KBDTABLES, *PKBDTABLES;

#define CAPLOK      0x01
#define SGCAPS      0x02
#define CAPLOKALTGR 0x04
#define WCH_NONE    0xF000
#define KLLF_ALTGR  0x0001

static VK_TO_WCHARS1 aVkToBits[] = {
    { VK_SHIFT,   0, { KBDSHIFT } },
    { VK_CONTROL, 0, { KBDCTRL } },
    { VK_MENU,    0, { KBDALT } },
    { 0,          0, { 0 } }
};

static BYTE aModNumber[] = {
    0,            /* 0: Normal */
    1,            /* 1: Shift */
    2,            /* 2: Ctrl */
    SHFT_INVALID, /* 3: Ctrl + Shift */
    SHFT_INVALID, /* 4: Alt */
    SHFT_INVALID, /* 5: Alt + Shift */
    3,            /* 6: Ctrl + Alt (AltGr) */
    4             /* 7: Ctrl + Alt + Shift (AltGr + Shift) */
};

static MODIFIERS CharModifiers = {
    (PVK_TO_WCHARS1)aVkToBits,
    7,
    { 0 }
};

/* Fulfulde QWERTY character table */
/* Columns: Normal | Shift | Ctrl | AltGr | AltGr+Shift */
static VK_TO_WCHARS5 aVkToWch5[] = {
    { 'A',       CAPLOK, { 'a',    'A',    0x01,     0x00E1, 0x00C1 } }, /* AltGr: á / Á */
    { 'B',       CAPLOK, { 'b',    'B',    0x02,     0x0253, 0x0181 } }, /* AltGr: ɓ / Ɓ */
    { 'C',       CAPLOK, { 'c',    'C',    0x03,     WCH_NONE, WCH_NONE } },
    { 'D',       CAPLOK, { 'd',    'D',    0x04,     0x0257, 0x018A } }, /* AltGr: ɗ / Ɗ */
    { 'E',       CAPLOK, { 'e',    'E',    0x05,     0x00E9, 0x00C9 } }, /* AltGr: é / É */
    { 'F',       CAPLOK, { 'f',    'F',    0x06,     WCH_NONE, WCH_NONE } },
    { 'G',       CAPLOK, { 'g',    'G',    0x07,     WCH_NONE, WCH_NONE } },
    { 'H',       CAPLOK, { 'h',    'H',    0x08,     WCH_NONE, WCH_NONE } },
    { 'I',       CAPLOK, { 'i',    'I',    0x09,     0x00ED, 0x00CD } }, /* AltGr: í / Í */
    { 'J',       CAPLOK, { 'j',    'J',    0x0A,     WCH_NONE, WCH_NONE } },
    { 'K',       CAPLOK, { 'k',    'K',    0x0B,     WCH_NONE, WCH_NONE } },
    { 'L',       CAPLOK, { 'l',    'L',    0x0C,     WCH_NONE, WCH_NONE } },
    { 'M',       CAPLOK, { 'm',    'M',    0x0D,     WCH_NONE, WCH_NONE } },
    { 'N',       CAPLOK, { 'n',    'N',    0x0E,     0x014B, 0x014A } }, /* AltGr: ŋ / Ŋ */
    { 'O',       CAPLOK, { 'o',    'O',    0x0F,     0x00F3, 0x00D3 } }, /* AltGr: ó / Ó */
    { 'P',       CAPLOK, { 'p',    'P',    0x10,     WCH_NONE, WCH_NONE } },
    { 'Q',       CAPLOK, { 0x01B4, 0x01B3, 0x11,     'q',    'Q' } },    /* Direct: ƴ / Ƴ */
    { 'R',       CAPLOK, { 'r',    'R',    0x12,     WCH_NONE, WCH_NONE } },
    { 'S',       CAPLOK, { 's',    'S',    0x13,     WCH_NONE, WCH_NONE } },
    { 'T',       CAPLOK, { 't',    'T',    0x14,     WCH_NONE, WCH_NONE } },
    { 'U',       CAPLOK, { 'u',    'U',    0x15,     0x00FA, 0x00DA } }, /* AltGr: ú / Ú */
    { 'V',       CAPLOK, { 'v',    'V',    0x16,     WCH_NONE, WCH_NONE } },
    { 'W',       CAPLOK, { 'w',    'W',    0x17,     WCH_NONE, WCH_NONE } },
    { 'X',       CAPLOK, { 'x',    'X',    0x18,     WCH_NONE, WCH_NONE } },
    { 'Y',       CAPLOK, { 'y',    'Y',    0x19,     0x01B4, 0x01B3 } }, /* AltGr: ƴ / Ƴ */
    { 'Z',       CAPLOK, { 'z',    'Z',    0x1A,     WCH_NONE, WCH_NONE } },

    /* Number row */
    { '1',       0,      { '1',    '!',    WCH_NONE, WCH_NONE, WCH_NONE } },
    { '2',       0,      { '2',    '@',    WCH_NONE, WCH_NONE, WCH_NONE } },
    { '3',       0,      { '3',    '#',    WCH_NONE, WCH_NONE, WCH_NONE } },
    { '4',       0,      { '4',    '$',    WCH_NONE, 0x00A4,   WCH_NONE } },
    { '5',       0,      { '5',    '%',    WCH_NONE, 0x20AC,   WCH_NONE } },
    { '6',       0,      { '6',    '^',    WCH_NONE, WCH_NONE, WCH_NONE } },
    { '7',       0,      { '7',    '&',    WCH_NONE, WCH_NONE, WCH_NONE } },
    { '8',       0,      { '8',    '*',    WCH_NONE, WCH_NONE, WCH_NONE } },
    { '9',       0,      { '9',    '(',    WCH_NONE, WCH_NONE, WCH_NONE } },
    { '0',       0,      { '0',    ')',    WCH_NONE, WCH_NONE, WCH_NONE } },

    /* QWERTY special mappings for Fulfulde */
    { VK_OEM_4,  0,      { 0x0253, 0x0181, 0x1B,     '[',    '{' } },    /* Key [ -> ɓ / Ɓ */
    { VK_OEM_6,  0,      { 0x0257, 0x018A, 0x1D,     ']',    '}' } },    /* Key ] -> ɗ / Ɗ */
    { VK_OEM_1,  0,      { 0x014B, 0x014A, WCH_NONE, ';',    ':' } },    /* Key ; -> ŋ / Ŋ */
    { VK_OEM_7,  0,      { 0x2019, '"',    WCH_NONE, '\'',   '"' } },    /* Key ' -> ’ (hamza) */

    /* Standard punctuation */
    { VK_OEM_3,  0,      { '`',    '~',    WCH_NONE, WCH_NONE, WCH_NONE } },
    { VK_OEM_MINUS, 0,   { '-',    '_',    WCH_NONE, WCH_NONE, WCH_NONE } },
    { VK_OEM_PLUS, 0,    { '=',    '+',    WCH_NONE, WCH_NONE, WCH_NONE } },
    { VK_OEM_5,  0,      { '\\',   '|',    0x1C,     WCH_NONE, WCH_NONE } },
    { VK_OEM_COMMA, 0,   { ',',    '<',    WCH_NONE, WCH_NONE, WCH_NONE } },
    { VK_OEM_PERIOD, 0,  { '.',    '>',    WCH_NONE, WCH_NONE, WCH_NONE } },
    { VK_OEM_2,  0,      { '/',    '?',    WCH_NONE, WCH_NONE, WCH_NONE } },
    { VK_SPACE,  0,      { ' ',    ' ',    ' ',      ' ',      ' ' } },
    { 0,         0,      { 0,      0,      0,        0,        0 } }
};

static VK_TO_WCHAR_TABLE aVkToWcharTable[] = {
    { (PVK_TO_WCHARS1)aVkToWch5, 5, sizeof(aVkToWch5[0]) },
    { NULL, 0, 0 }
};

/* Standard US QWERTY ScanCode to Virtual Key mapping */
static USHORT ausVSCtoVK[] = {
    0,            /* 0x00 */
    VK_ESCAPE,    /* 0x01 */
    '1',          /* 0x02 */
    '2',          /* 0x03 */
    '3',          /* 0x04 */
    '4',          /* 0x05 */
    '5',          /* 0x06 */
    '6',          /* 0x07 */
    '7',          /* 0x08 */
    '8',          /* 0x09 */
    '9',          /* 0x0A */
    '0',          /* 0x0B */
    VK_OEM_MINUS, /* 0x0C */
    VK_OEM_PLUS,  /* 0x0D */
    VK_BACK,      /* 0x0E */
    VK_TAB,       /* 0x0F */
    'Q',          /* 0x10 */
    'W',          /* 0x11 */
    'E',          /* 0x12 */
    'R',          /* 0x13 */
    'T',          /* 0x14 */
    'Y',          /* 0x15 */
    'U',          /* 0x16 */
    'I',          /* 0x17 */
    'O',          /* 0x18 */
    'P',          /* 0x19 */
    VK_OEM_4,     /* 0x1A - [ (ɓ) */
    VK_OEM_6,     /* 0x1B - ] (ɗ) */
    VK_RETURN,    /* 0x1C */
    VK_LCONTROL,  /* 0x1D */
    'A',          /* 0x1E */
    'S',          /* 0x1F */
    'D',          /* 0x20 */
    'F',          /* 0x21 */
    'G',          /* 0x22 */
    'H',          /* 0x23 */
    'J',          /* 0x24 */
    'K',          /* 0x25 */
    'L',          /* 0x26 */
    VK_OEM_1,     /* 0x27 - ; (ŋ) */
    VK_OEM_7,     /* 0x28 - ' (hamza) */
    VK_OEM_3,     /* 0x29 - ` */
    VK_LSHIFT,    /* 0x2A */
    VK_OEM_5,     /* 0x2B - \ */
    'Z',          /* 0x2C */
    'X',          /* 0x2D */
    'C',          /* 0x2E */
    'V',          /* 0x2F */
    'B',          /* 0x30 */
    'N',          /* 0x31 */
    'M',          /* 0x32 */
    VK_OEM_COMMA, /* 0x33 */
    VK_OEM_PERIOD,/* 0x34 */
    VK_OEM_2,     /* 0x35 */
    VK_RSHIFT,    /* 0x36 */
    VK_MULTIPLY,  /* 0x37 */
    VK_LMENU,     /* 0x38 */
    VK_SPACE,     /* 0x39 */
    VK_CAPITAL,   /* 0x3A */
    VK_F1,        /* 0x3B */
    VK_F2,        /* 0x3C */
    VK_F3,        /* 0x3D */
    VK_F4,        /* 0x3E */
    VK_F5,        /* 0x3F */
    VK_F6,        /* 0x40 */
    VK_F7,        /* 0x41 */
    VK_F8,        /* 0x42 */
    VK_F9,        /* 0x43 */
    VK_F10,       /* 0x44 */
    VK_NUMLOCK,   /* 0x45 */
    VK_SCROLL,    /* 0x46 */
    VK_NUMPAD7,   /* 0x47 */
    VK_NUMPAD8,   /* 0x48 */
    VK_NUMPAD9,   /* 0x49 */
    VK_SUBTRACT,  /* 0x4A */
    VK_NUMPAD4,   /* 0x4B */
    VK_NUMPAD5,   /* 0x4C */
    VK_NUMPAD6,   /* 0x4D */
    VK_ADD,       /* 0x4E */
    VK_NUMPAD1,   /* 0x4F */
    VK_NUMPAD2,   /* 0x50 */
    VK_NUMPAD3,   /* 0x51 */
    VK_NUMPAD0,   /* 0x52 */
    VK_DECIMAL,   /* 0x53 */
    0,            /* 0x54 */
    0,            /* 0x55 */
    VK_OEM_102,   /* 0x56 */
    VK_F11,       /* 0x57 */
    VK_F12        /* 0x58 */
};

static VSC_VK aE0VscToVk[] = {
    { 0x1C, VK_RETURN },
    { 0x1D, VK_RCONTROL },
    { 0x35, VK_DIVIDE },
    { 0x37, VK_SNAPSHOT },
    { 0x38, VK_RMENU },
    { 0x47, VK_HOME },
    { 0x48, VK_UP },
    { 0x49, VK_PRIOR },
    { 0x4B, VK_LEFT },
    { 0x4D, VK_RIGHT },
    { 0x4F, VK_END },
    { 0x50, VK_DOWN },
    { 0x51, VK_NEXT },
    { 0x52, VK_INSERT },
    { 0x53, VK_DELETE },
    { 0x5B, VK_LWIN },
    { 0x5C, VK_RWIN },
    { 0x5D, VK_APPS },
    { 0, 0 }
};

static VSC_VK aE1VscToVk[] = {
    { 0x1D, VK_PAUSE },
    { 0, 0 }
};

static VSC_LPWSTR aKeyNames[] = {
    { 0x01, L"Esc" },
    { 0x0E, L"Backspace" },
    { 0x0F, L"Tab" },
    { 0x1C, L"Enter" },
    { 0x1D, L"Ctrl" },
    { 0x2A, L"Shift" },
    { 0x36, L"Right Shift" },
    { 0x37, L"Num *" },
    { 0x38, L"Alt" },
    { 0x39, L"Space" },
    { 0x3A, L"Caps Lock" },
    { 0x3B, L"F1" },
    { 0x3C, L"F2" },
    { 0x3D, L"F3" },
    { 0x3E, L"F4" },
    { 0x3F, L"F5" },
    { 0x40, L"F6" },
    { 0x41, L"F7" },
    { 0x42, L"F8" },
    { 0x43, L"F9" },
    { 0x44, L"F10" },
    { 0x45, L"Pause" },
    { 0x46, L"Scroll Lock" },
    { 0x57, L"F11" },
    { 0x58, L"F12" },
    { 0, NULL }
};

static VSC_LPWSTR aKeyNamesExt[] = {
    { 0x1C, L"Num Enter" },
    { 0x1D, L"Right Ctrl" },
    { 0x35, L"Num /" },
    { 0x37, L"Prnt Scrn" },
    { 0x38, L"Right Alt" },
    { 0x45, L"Num Lock" },
    { 0x46, L"Break" },
    { 0x47, L"Home" },
    { 0x48, L"Up" },
    { 0x49, L"Page Up" },
    { 0x4B, L"Left" },
    { 0x4D, L"Right" },
    { 0x4F, L"End" },
    { 0x50, L"Down" },
    { 0x51, L"Page Down" },
    { 0x52, L"Insert" },
    { 0x53, L"Delete" },
    { 0x5B, L"Left Windows" },
    { 0x5C, L"Right Windows" },
    { 0x5D, L"Application" },
    { 0, NULL }
};

static KBDTABLES KbdTables = {
    &CharModifiers,
    aVkToWcharTable,
    NULL,
    aKeyNames,
    aKeyNamesExt,
    NULL,
    ausVSCtoVK,
    sizeof(ausVSCtoVK) / sizeof(ausVSCtoVK[0]),
    aE0VscToVk,
    aE1VscToVk,
    KLLF_ALTGR,
    0,
    0,
    NULL,
    0,
    0
};

__declspec(dllexport) PKBDTABLES KbdLayerDescriptor(VOID) {
    CharModifiers.pVkToWchars = (PVK_TO_WCHARS1)aVkToBits;
    CharModifiers.wMaxModBits = 7;
    memcpy(CharModifiers.ModNumber, aModNumber, sizeof(aModNumber));
    return &KbdTables;
}

BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpvReserved) {
    return TRUE;
}
