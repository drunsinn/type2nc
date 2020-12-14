;
;Usage: set the following Q-Parameters to the desired values
;QS500 is the text
;Q200 is the sage distance
;Q203 is the Z-coordinate of the surface
;Q201 is the depth
;Q204 is the safe Z-coordinate for traversing between cuts
;Q206 is the plunging feed rate
;Q207 is the feed rate while miling
;Q513 is the approximate height of the text
;Q374 is start angle
;
;Local Q-Parameters for temporary use
;QL10 is the counter for keeping track of the current character
;QL11 is the length of the input string QS1
;QL13 is the incremental value for the x advance
;QL14 is the incremental value for the y advance, currently not in use
;QL15 is the end value for the z movement
;QL16 is the scale factor for x and y
;QL20 is the width of the character plus the necessary advance. only valid after the character was machined
;QL21 is a temp value for string comparison, STRCOMP
;QL22 temp value, contains the remaining length of the text-string
;QL23 temp value, contains the starting position of the unicode-pattern
;QL24 temp value, contains the length of the test-string with special characters, STRLEN
;QL25 temp value, contains the result of INSTR
;QL26 is the X-coordinate of the lower left corner of the text, and the start position
;QL27 is the Y-coordinate of the lower left corner of the text, and the start position
;QL28 is the active X-coordinate NPV
;QL29 is the active Y-coordinate NPV
;QL30 is the active rotation
;QL31 is the newly calculated rotation
;QL32 calculated safe height for first positioning
;QS1 is the transported value from QS500
;QS2 is the current character
;QS3 is a temporary string for holding special characters for testing
; a space character. this seems to be necessary because a string parameter can't be a single space
;
QS1 = QS500 ; give value from QS500 to QS1
; read the active NPV
FN 18: SYSREAD QL28 = ID220 NR2 IDX1
FN 18: SYSREAD QL29 = ID220 NR2 IDX2
;
; read the active position in X and Y
FN 18: SYSREAD QL26 = ID270 NR1 IDX1
FN 18: SYSREAD QL27 = ID270 NR1 IDX2
;
; read active rotation
FN 18: SYSREAD QL30 = ID210 NR2
;
QL10 = 0 ;loop counter
QL11 = STRLEN( SRC_QS1 ) ;string length
QL13 = 0 ;start in X
QL14 = 0 ;start in Y
QL15 = Q201 + Q203 ;final Z coordinate
;
QL16 = Q513 / 10
;
CYCL DEF 7.0 NULLPUNKT
CYCL DEF 7.1  X+QL26
CYCL DEF 7.2  Y+QL27
;
; calculate new rotation
QL31 = Q374 + QL30
CYCL DEF 10.0 DREHUNG
CYCL DEF 10.1  ROT+QL31
;
CYCL DEF 26.0 MASSFAKTOR ACHSSPEZ.
CYCL DEF 26.1 X+QL16 Y+QL16
;
; calculate new safe height for first positioning
QL32 = Q200 + Q203
L Z+QL32 FMAX
;
LBL "start"
QS2 = SUBSTR( SRC_QS1 BEGQL10 LEN1 )
CYCL DEF 7.0 NULLPUNKT
CYCL DEF 7.1 IX+QL13
CYCL DEF 7.2 IY+QL14
;
; check if character is a space
QS3 = "1 1" ;temp string for space character
QS3 = SUBSTR( SRC_QS3 BEG1 LEN1 )
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_space"
QS2 = "space" ;space character
FN 9: IF +10 EQU +10 GOTO LBL "cont" ;skip to lbl call
;
LBL "not_space"
;
;Check if remaining string is long enough for unicode
QS3 = "%0x" ;temp string for unicode character
QL22 = QL11 - QL10
FN 12: IF +QL22 LT +7 GOTO LBL "not_unicode"
;check if remaining string starts with unicode token
QL25 = INSTR( SRC_QS1 SEA_QS3 BEGQL10 )
;check if pattern starts at the beginning of the remaining string. if not, wait for later
QL23 = QL25 - QL10
FN 10: IF +QL23 NE +0 GOTO LBL "not_unicode"
;extract pattern from string, ignoring the % character
QL25 = QL25 + 1
QS2 = SUBSTR( SRC_QS1 BEGQL25 LEN6 )
;advance counter to position after pattern
QL10 = QL10 + 6
FN 9: IF +10 EQU +10 GOTO LBL "cont" ;skip to lbl call
;
LBL "not_unicode"
;
;check if charkter is one for with an illegal label name;
QS3 = ";'\/.,][`!@#$%^&*()_+:?><"
QL24 = STRLEN( SRC_QS3 )
QL25 = INSTR( SRC_QS3 SEA_QS2 BEG0 )
FN 9: IF +QL25 EQU +QL24 GOTO LBL "not_illegal" ;skip to lbl call
CALL LBL "check_char"
FN 9: IF +10 EQU +10 GOTO LBL "cont" ;skip to lbl call
;
LBL "not_illegal"
;
LBL "cont"
L FQ207
CALL LBL QS2
;
QL10 = QL10 + 1 ;advance counter
QL13 = QL20 ;save X-Advance
FN 12: IF +QL10 LT +QL11 GOTO LBL "start"
;
CALL LBL "end"
;
LBL "check_char"
;not all characters are allowed for label names. therefore they have to be translated manually
QS3 = "!"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_exclamation_mark"
QS2 = "exclamation_mark"
FN 9: IF +10 EQU +10 GOTO LBL "check_cahr_end"
LBL "not_exclamation_mark"
;
QS3 = "'"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_apostrophe"
QS2 = "apostrophe"
FN 9: IF +10 EQU +10 GOTO LBL "check_cahr_end"
LBL "not_apostrophe"
;
QS3 = "("
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_opening_parenthese"
QS2 = "opening_parenthese"
FN 9: IF +10 EQU +10 GOTO LBL "check_cahr_end"
LBL "not_opening_parenthese"
;
QS3 = ")"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_closing_parenthese"
QS2 = "closing_parenthese"
FN 9: IF +10 EQU +10 GOTO LBL "check_cahr_end"
LBL "not_closing_parenthese"
;
QS3 = "*"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_asterisk"
QS2 = "asterisk"
FN 9: IF +10 EQU +10 GOTO LBL "check_cahr_end"
LBL "not_asterisk"
;
QS3 = "+"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_plus"
QS2 = "plus"
FN 9: IF +10 EQU +10 GOTO LBL "check_cahr_end"
LBL "not_plus"
;
QS3 = "/"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_slash"
QS2 = "slash"
FN 9: IF +10 EQU +10 GOTO LBL "check_cahr_end"
LBL "not_slash"
;
QS3 = "\"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_backslash"
QS2 = "backslash"
FN 9: IF +10 EQU +10 GOTO LBL "check_cahr_end"
LBL "not_backslash"
;
QS3 = ":"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_colon"
QS2 = "colon"
FN 9: IF +10 EQU +10 GOTO LBL "check_cahr_end"
LBL "not_colon"
;
QS3 = ";"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_semicolon"
QS2 = "semicolon"
FN 9: IF +10 EQU +10 GOTO LBL "check_cahr_end"
LBL "not_semicolon"
;
QS3 = "]"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_closing_square_brackets"
QS2 = "closing_square_brackets"
FN 9: IF +10 EQU +10 GOTO LBL "check_cahr_end"
LBL "not_closing_square_brackets"
;
QS3 = "["
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_opening_square_brackets"
QS2 = "opening_square_brackets"
FN 9: IF +10 EQU +10 GOTO LBL "check_cahr_end"
LBL "not_opening_square_brackets"
;
QS3 = "`"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_prime"
QS2 = "prime"
FN 9: IF +10 EQU +10 GOTO LBL "check_cahr_end"
LBL "not_prime"
;
QS3 = "@"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_at"
QS2 = "at"
FN 9: IF +10 EQU +10 GOTO LBL "check_cahr_end"
LBL "not_at"
;
QS3 = "^"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_caret"
QS2 = "caret"
FN 9: IF +10 EQU +10 GOTO LBL "check_cahr_end"
LBL "not_caret"
;
QS3 = "?"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_question_mark"
QS2 = "question_mark"
FN 9: IF +10 EQU +10 GOTO LBL "check_cahr_end"
LBL "not_question_mark"
;
QS3 = "<"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_less_than"
QS2 = "less_than"
FN 9: IF +10 EQU +10 GOTO LBL "check_cahr_end"
LBL "not_less_than"
;
QS3 = ">"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_greater_than"
QS2 = "greater_than"
FN 9: IF +10 EQU +10 GOTO LBL "check_cahr_end"
LBL "not_greater_than"
;
LBL "check_cahr_end"
LBL 0
;
* - begin of character data
