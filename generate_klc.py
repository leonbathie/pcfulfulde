# -*- coding: utf-8 -*-
"""
Generateur de fichiers KLC conformes Microsoft MSKLC pour Fulfulde (AZERTY et QWERTY).
Disposition AZERTY calquée exactement sur l'interface officielle :
- Touche Z -> ɗ / Ɗ (AltGr: z / Z)
- Touche Q -> ŋ / Ŋ (AltGr: q / Q)
- Touche X -> ƴ / Ƴ (AltGr: x / X)
- Touche V -> ɓ / Ɓ (AltGr: v / V)
- Touche ^ -> ñ / Ñ (AltGr: ^ / ¨)
"""

klc_azerty = """KBD\tfulffaz\t"Fulfulde (Pulaar) AZERTY"

COPYRIGHT\t"MIT License - Clavier Fulfulde"

COMPANY\t"Fulfulde Community"

LOCALENAME\t"ff-Latn-SN"

LOCALEID\t"00000867"

VERSION\t"1.0"

SHIFTSTATE
0\t// Normal
1\t// Shift
2\t// Ctrl
6\t// AltGr
7\t// Shift + AltGr

LAYOUT
// SC\tVK_\tCap\t0\t1\t2\t6\t7
// -----------------------------------------------------------------------------------------
02\t1\t0\t0026\t1\t-1\t00b9\t-1\t\t// & 1 ¹
03\t2\t0\t00e9\t2\t-1\t007e\t-1\t\t// é 2 ~
04\t3\t0\t0022\t3\t-1\t0023\t-1\t\t// " 3 #
05\t4\t0\t0027\t4\t-1\t007b\t-1\t\t// ' 4 {
06\t5\t0\t0028\t5\t-1\t005b\t-1\t\t// ( 5 [
07\t6\t0\t002d\t6\t-1\t007c\t-1\t\t// - 6 |
08\t7\t0\t00e8\t7\t-1\t0060\t-1\t\t// è 7 `
09\t8\t0\t005f\t8\t-1\t005c\t-1\t\t// _ 8 \\
0a\t9\t0\t00e7\t9\t-1\t005e\t-1\t\t// ç 9 ^
0b\t0\t0\t00e0\t0\t-1\t0040\t-1\t\t// à 0 @
0c\tOEM_4\t0\t0029\t00b0\t-1\t005d\t-1\t\t// ) ° ]
0d\tOEM_PLUS\t0\t003d\t002b\t-1\t007d\t-1\t\t// = + }

// Rangee AZERTY
10\tA\t1\ta\tA\t-1\t00e1\t00c1\t\t// a A -> á Á
11\tZ\t1\t0257\t018a\t-1\t007a\t005a\t\t// ɗ Ɗ direct, AltGr: z Z
12\tE\t1\te\tE\t-1\t20ac\t-1\t\t// e E -> €
13\tR\t1\tr\tR\t-1\t-1\t-1\t\t// r R
14\tT\t1\tt\tT\t-1\t-1\t-1\t\t// t T
15\tY\t1\ty\tY\t-1\t-1\t-1\t\t// y Y
16\tU\t1\tu\tU\t-1\t00fa\t00da\t\t// u U -> ú Ú
17\tI\t1\ti\tI\t-1\t00ed\t00cd\t\t// i I -> í Í
18\tO\t1\to\tO\t-1\t00f3\t00d3\t\t// o O -> ó Ó
19\tP\t1\tp\tP\t-1\t-1\t-1\t\t// p P
1a\tOEM_6\t1\t00f1\t00d1\t-1\t005e\t00a8\t\t// ñ Ñ direct, AltGr: ^ ¨
1b\tOEM_1\t0\t0024\t00a3\t-1\t00a4\t-1\t\t// $ £ ¤
2b\tOEM_5\t0\t002a\t00b5\t-1\t-1\t-1\t\t// * µ

// Rangee QSDFGHJKLM
1e\tQ\t1\t014b\t014a\t-1\t0071\t0051\t\t// ŋ Ŋ direct, AltGr: q Q
1f\tS\t1\ts\tS\t-1\t-1\t-1\t\t// s S
20\tD\t1\td\tD\t-1\t0257\t018a\t\t// d D -> ɗ Ɗ
21\tF\t1\tf\tF\t-1\t-1\t-1\t\t// f F
22\tG\t1\tg\tG\t-1\t-1\t-1\t\t// g G
23\tH\t1\th\tH\t-1\t-1\t-1\t\t// h H
24\tJ\t1\tj\tJ\t-1\t-1\t-1\t\t// j J
25\tK\t1\tk\tK\t-1\t-1\t-1\t\t// k K
26\tL\t1\tl\tL\t-1\t-1\t-1\t\t// l L
27\tM\t1\tm\tM\t-1\t-1\t-1\t\t// m M
28\tOEM_3\t0\t00f9\t0025\t-1\t-1\t-1\t\t// ù %
29\tOEM_7\t0\t00b2\t2019\t-1\t-1\t-1\t\t// ² ’ (hamza)

// Rangee WXCVBN
2c\tW\t1\tw\tW\t-1\t-1\t-1\t\t// w W
2d\tX\t1\t01b4\t01b3\t-1\t0078\t0058\t\t// ƴ Ƴ direct, AltGr: x X
2e\tC\t1\tc\tC\t-1\t-1\t-1\t\t// c C
2f\tV\t1\t0253\t0181\t-1\t0076\t0056\t\t// ɓ Ɓ direct, AltGr: v V
30\tB\t1\tb\tB\t-1\t0253\t0181\t\t// b B -> ɓ Ɓ
31\tN\t1\tn\tN\t-1\t014b\t014a\t\t// n N -> ŋ Ŋ
32\tOEM_COMMA\t0\t002c\t003f\t-1\t-1\t-1\t\t// , ?
33\tOEM_PERIOD\t0\t003b\t002e\t-1\t-1\t-1\t\t// ; .
34\tOEM_2\t0\t003a\t002f\t-1\t-1\t-1\t\t// : /
35\tOEM_8\t0\t0021\t00a7\t-1\t-1\t-1\t\t// ! §
39\tSPACE\t0\t0020\t0020\t0020\t-1\t-1\t\t// Espace
56\tOEM_102\t0\t003c\t003e\t-1\t-1\t-1\t\t// < >

DESCRIPTIONS
040c\tFulfulde (Pulaar) AZERTY
0867\tFulfulde (Pulaar) AZERTY
0409\tFulfulde (Pulaar) AZERTY

LANGUAGENAMES
040c\tFrench (France)
0867\tFulah (Senegal)
0409\tEnglish (United States)

ENDKBD
"""

klc_qwerty = """KBD\tfulffqw\t"Fulfulde (Pulaar) QWERTY"

COPYRIGHT\t"MIT License - Clavier Fulfulde"

COMPANY\t"Fulfulde Community"

LOCALENAME\t"ff-Latn-SN"

LOCALEID\t"00000867"

VERSION\t"1.0"

SHIFTSTATE
0\t// Normal
1\t// Shift
2\t// Ctrl
6\t// AltGr
7\t// Shift + AltGr

LAYOUT
// SC\tVK_\tCap\t0\t1\t2\t6\t7
// -----------------------------------------------------------------------------------------
02\t1\t0\t1\t0021\t-1\t-1\t-1\t\t// 1 !
03\t2\t0\t2\t0040\t-1\t-1\t-1\t\t// 2 @
04\t3\t0\t3\t0023\t-1\t-1\t-1\t\t// 3 #
05\t4\t0\t4\t0024\t-1\t00a4\t-1\t\t// 4 $
06\t5\t0\t5\t0025\t-1\t20ac\t-1\t\t// 5 % €
07\t6\t0\t6\t005e\t-1\t-1\t-1\t\t// 6 ^
08\t7\t0\t7\t0026\t-1\t-1\t-1\t\t// 7 &
09\t8\t0\t8\t002a\t-1\t-1\t-1\t\t// 8 *
0a\t9\t0\t9\t0028\t-1\t-1\t-1\t\t// 9 (
0b\t0\t0\t0\t0029\t-1\t-1\t-1\t\t// 0 )
0c\tOEM_MINUS\t0\t002d\t005f\t-1\t-1\t-1\t\t// - _
0d\tOEM_PLUS\t0\t003d\t002b\t-1\t-1\t-1\t\t// = +

// Rangee QWERTY
10\tQ\t1\t01b4\t01b3\t-1\tq\tQ\t\t// ƴ Ƴ direct, AltGr q Q
11\tW\t1\tw\tW\t-1\t-1\t-1\t\t// w W
12\tE\t1\te\tE\t-1\t00e9\t00c9\t\t// e E -> é É
13\tR\t1\tr\tR\t-1\t-1\t-1\t\t// r R
14\tT\t1\tt\tT\t-1\t-1\t-1\t\t// t T
15\tY\t1\ty\tY\t-1\t01b4\t01b3\t\t// y Y -> ƴ Ƴ
16\tU\t1\tu\tU\t-1\t00fa\t00da\t\t// u U -> ú Ú
17\tI\t1\ti\tI\t-1\t00ed\t00cd\t\t// i I -> í Í
18\tO\t1\to\tO\t-1\t00f3\t00d3\t\t// o O -> ó Ó
19\tP\t1\tp\tP\t-1\t-1\t-1\t\t// p P
1a\tOEM_4\t0\t0253\t0181\t001b\t005b\t007b\t// [ { -> ɓ Ɓ
1b\tOEM_6\t0\t0257\t018a\t001d\t005d\t007d\t// ] } -> ɗ Ɗ

// Rangee ASDFGHJKL
1e\tA\t1\ta\tA\t-1\t00e1\t00c1\t\t// a A -> á Á
1f\tS\t1\ts\tS\t-1\t-1\t-1\t\t// s S
20\tD\t1\td\tD\t-1\t0257\t018a\t\t// d D -> ɗ Ɗ
21\tF\t1\tf\tF\t-1\t-1\t-1\t\t// f F
22\tG\t1\tg\tG\t-1\t-1\t-1\t\t// g G
23\tH\t1\th\tH\t-1\t-1\t-1\t\t// h H
24\tJ\t1\tj\tJ\t-1\t-1\t-1\t\t// j J
25\tK\t1\tk\tK\t-1\t-1\t-1\t\t// k K
26\tL\t1\tl\tL\t-1\t-1\t-1\t\t// l L
27\tOEM_1\t0\t014b\t014a\t-1\t003b\t003a\t// ; : -> ŋ Ŋ
28\tOEM_7\t0\t2019\t0022\t-1\t0027\t0022\t// ' " -> ’ (hamza)

// Rangee ZXCVBNM
29\tOEM_3\t0\t0060\t007e\t-1\t-1\t-1\t\t// ` ~
2b\tOEM_5\t0\t005c\t007c\t001c\t-1\t-1\t\t// \\ |
2c\tZ\t1\tz\tZ\t-1\t-1\t-1\t\t// z Z
2d\tX\t1\tx\tX\t-1\t-1\t-1\t\t// x X
2e\tC\t1\tc\tC\t-1\t-1\t-1\t\t// c C
2f\tV\t1\tv\tV\t-1\t-1\t-1\t\t// v V
30\tB\t1\tb\tB\t-1\t0253\t0181\t\t// b B -> ɓ Ɓ
31\tN\t1\tn\tN\t-1\t014b\t014a\t\t// n N -> ŋ Ŋ
32\tM\t1\tm\tM\t-1\t-1\t-1\t\t// m M
33\tOEM_COMMA\t0\t002c\t003c\t-1\t-1\t-1\t\t// , <
34\tOEM_PERIOD\t0\t002e\t003e\t-1\t-1\t-1\t\t// . >
35\tOEM_2\t0\t002f\t003f\t-1\t-1\t-1\t\t// / ?
39\tSPACE\t0\t0020\t0020\t0020\t-1\t-1\t\t// Espace

DESCRIPTIONS
040c\tFulfulde (Pulaar) QWERTY
0867\tFulfulde (Pulaar) QWERTY
0409\tFulfulde (Pulaar) QWERTY

LANGUAGENAMES
040c\tFrench (France)
0867\tFulah (Senegal)
0409\tEnglish (United States)

ENDKBD
"""

with open("fulffaz.klc", "w", encoding="utf-16") as f:
    f.write(klc_azerty)

with open("fulffqw.klc", "w", encoding="utf-16") as f:
    f.write(klc_qwerty)

print("Fichiers fulffaz.klc et fulffqw.klc generes en UTF-16 LE avec succes.")
