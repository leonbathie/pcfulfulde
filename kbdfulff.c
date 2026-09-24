/*
 * Clavier Fulfulde (Pulaar) Latin - Disposition Windows Native
 * Fichier source pour compilation en DLL clavier Windows (kbd*.dll)
 * 
 * Caractères spéciaux Fulfulde sur AltGr :
 *   AltGr + b -> ɓ (U+0253)  |  AltGr + Shift + b -> Ɓ (U+0181)
 *   AltGr + d -> ɗ (U+0257)  |  AltGr + Shift + d -> Ɗ (U+018A)
 *   AltGr + n -> ŋ (U+014B)  |  AltGr + Shift + n -> Ŋ (U+014A)
 *   AltGr + y -> ƴ (U+01B4)  |  AltGr + Shift + y -> Ƴ (U+01B3)
 *   AltGr + ' -> ' (U+2019)  hamza / glottale
 *   AltGr + a -> á  |  AltGr + e -> é  |  AltGr + i -> í
 *   AltGr + o -> ó  |  AltGr + u -> ú
 *
 * Base : AZERTY français (KBDFR)
 */

#include <windows.h>

/* ---- Scan code -> Virtual Key table ---- */
/* Standard AZERTY French base */
static USHORT ausVK[] = {
    VK_OEM_7,      // 00: '²'
    '1',           // 02
    '2',           // 03
    '3',           // 04
    '4',           // 05
    '5',           // 06
    '6',           // 07
    '7',           // 08
    '8',           // 09
    '9',           // 0a
    '0',           // 0b
    VK_OEM_4,      // 0c: ')'
    VK_OEM_PLUS,   // 0d: '='
};

/* ---- Character tables ---- */

/* VK_TO_WCHARS: maps virtual key + shift state -> Unicode character */

typedef struct {
    BYTE VirtualKey;
    BYTE Attributes;
    WCHAR wch[5]; /* Normal, Shift, Ctrl, AltGr, AltGr+Shift */
} VK_TO_WCHARS5;

/* 5 columns: Normal | Shift | Ctrl | AltGr | AltGr+Shift */
#define COLS 5
#define WCH_NONE 0xF000
#define WCH_DEAD 0xF001
#define WCH_LGTR 0xF002

static VK_TO_WCHARS5 aVkToWch5[] = {
    /* Letter keys with Fulfulde AltGr mappings */
    { 'A',  1, { 'a',    'A',    WCH_NONE, 0x00E1, 0x00C1 } }, /* AltGr: á Á */
    { 'B',  1, { 'b',    'B',    WCH_NONE, 0x0253, 0x0181 } }, /* AltGr: ɓ Ɓ */
    { 'C',  1, { 'c',    'C',    WCH_NONE, WCH_NONE, WCH_NONE } },
    { 'D',  1, { 'd',    'D',    WCH_NONE, 0x0257, 0x018A } }, /* AltGr: ɗ Ɗ */
    { 'E',  1, { 'e',    'E',    WCH_NONE, 0x00E9, 0x00C9 } }, /* AltGr: é É */
    { 'F',  1, { 'f',    'F',    WCH_NONE, WCH_NONE, WCH_NONE } },
    { 'G',  1, { 'g',    'G',    WCH_NONE, WCH_NONE, WCH_NONE } },
    { 'H',  1, { 'h',    'H',    WCH_NONE, WCH_NONE, WCH_NONE } },
    { 'I',  1, { 'i',    'I',    WCH_NONE, 0x00ED, 0x00CD } }, /* AltGr: í Í */
    { 'J',  1, { 'j',    'J',    WCH_NONE, WCH_NONE, WCH_NONE } },
    { 'K',  1, { 'k',    'K',    WCH_NONE, WCH_NONE, WCH_NONE } },
    { 'L',  1, { 'l',    'L',    WCH_NONE, WCH_NONE, WCH_NONE } },
    { 'M',  1, { 'm',    'M',    WCH_NONE, WCH_NONE, WCH_NONE } },
    { 'N',  1, { 'n',    'N',    WCH_NONE, 0x014B, 0x014A } }, /* AltGr: ŋ Ŋ */
    { 'O',  1, { 'o',    'O',    WCH_NONE, 0x00F3, 0x00D3 } }, /* AltGr: ó Ó */
    { 'P',  1, { 'p',    'P',    WCH_NONE, WCH_NONE, WCH_NONE } },
    { 'Q',  1, { 0x01B4, 0x01B3, WCH_NONE, 0x01B4, 0x01B3 } }, /* Direct: ƴ Ƴ */
    { 'R',  1, { 'r',    'R',    WCH_NONE, WCH_NONE, WCH_NONE } },
    { 'S',  1, { 's',    'S',    WCH_NONE, WCH_NONE, WCH_NONE } },
    { 'T',  1, { 't',    'T',    WCH_NONE, WCH_NONE, WCH_NONE } },
    { 'U',  1, { 'u',    'U',    WCH_NONE, 0x00FA, 0x00DA } }, /* AltGr: ú Ú */
    { 'V',  1, { 'v',    'V',    WCH_NONE, WCH_NONE, WCH_NONE } },
    { 'W',  1, { 'w',    'W',    WCH_NONE, WCH_NONE, WCH_NONE } },
    { 'X',  1, { 'x',    'X',    WCH_NONE, WCH_NONE, WCH_NONE } },
    { 'Y',  1, { 'y',    'Y',    WCH_NONE, 0x01B4, 0x01B3 } }, /* AltGr: ƴ Ƴ */
    { 'Z',  1, { 'z',    'Z',    WCH_NONE, WCH_NONE, WCH_NONE } },

    /* Special keys */
    { VK_OEM_7, 0, { 0x2019, 0x2019, WCH_NONE, 0x2019, WCH_NONE } }, /* ² -> ' hamza */

    /* End of table */
    { 0, 0, { 0, 0, 0, 0, 0 } }
};

/*
 * NOTE: This is a simplified reference source file.
 * A full Windows keyboard layout DLL requires the complete KbdTables
 * structure with all scan code mappings, dead key tables, and the
 * KbdLayerDescriptor export function.
 *
 * To compile into a working DLL, use MSKLC with the .klc files
 * (Fulfulde_AZERTY.klc / Fulfulde_QWERTY.klc) or the Windows DDK
 * kbdutool.exe utility.
 */
