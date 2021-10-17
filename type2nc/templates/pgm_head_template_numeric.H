;
;Usage: set the following Q-Parameters to the desired values
;QS500 is the text
;Q200 is the safe distance for pre positioning
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
QL100 = 32 ; ASCII-Code fuer Leerzeichen
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_space"
;
QS3 = "!"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_33"
QL100 = 33
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_33"
;
QS3 = "#"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_35"
QL100 = 35
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_35"
;
QS3 = "$"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_36"
QL100 = 36
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_36"
;
QS3 = "%"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_37"
QL100 = 37
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_37"
;
QS3 = "&"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_38"
QL100 = 38
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_38"
;
QS3 = "'"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_39"
QL100 = 39
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_39"
;
QS3 = "("
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_40"
QL100 = 40
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_40"
;
QS3 = ")"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_41"
QL100 = 41
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_41"
;
QS3 = "*"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_42"
QL100 = 42
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_42"
;
QS3 = "+"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_43"
QL100 = 43
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_43"
;
QS3 = ","
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_44"
QL100 = 44
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_44"
;
QS3 = "-"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_45"
QL100 = 45
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_45"
;
QS3 = "."
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_46"
QL100 = 46
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_46"
;
QS3 = "/"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_47"
QL100 = 47
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_47"
;
QS3 = "0"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_48"
QL100 = 48
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_48"
;
QS3 = "1"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_49"
QL100 = 49
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_49"
;
QS3 = "2"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_50"
QL100 = 50
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_50"
;
QS3 = "3"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_51"
QL100 = 51
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_51"
;
QS3 = "4"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_52"
QL100 = 52
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_52"
;
QS3 = "5"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_53"
QL100 = 53
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_53"
;
QS3 = "6"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_54"
QL100 = 54
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_54"
;
QS3 = "7"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_55"
QL100 = 55
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_55"
;
QS3 = "8"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_56"
QL100 = 56
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_56"
;
QS3 = "9"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_57"
QL100 = 57
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_57"
;
QS3 = ":"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_58"
QL100 = 58
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_58"
;
QS3 = ";"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_59"
QL100 = 59
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_59"
;
QS3 = "<"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_60"
QL100 = 60
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_60"
;
QS3 = "="
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_61"
QL100 = 61
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_61"
;
QS3 = ">"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_62"
QL100 = 62
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_62"
;
QS3 = "?"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_63"
QL100 = 63
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_63"
;
QS3 = "@"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_64"
QL100 = 64
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_64"
;
QS3 = "A"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_65"
QL100 = 65
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_65"
;
QS3 = "B"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_66"
QL100 = 66
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_66"
;
QS3 = "C"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_67"
QL100 = 67
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_67"
;
QS3 = "D"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_68"
QL100 = 68
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_68"
;
QS3 = "E"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_69"
QL100 = 69
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_69"
;
QS3 = "F"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_70"
QL100 = 70
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_70"
;
QS3 = "G"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_71"
QL100 = 71
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_71"
;
QS3 = "H"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_72"
QL100 = 72
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_72"
;
QS3 = "I"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_73"
QL100 = 73
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_73"
;
QS3 = "J"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_74"
QL100 = 74
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_74"
;
QS3 = "K"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_75"
QL100 = 75
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_75"
;
QS3 = "L"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_76"
QL100 = 76
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_76"
;
QS3 = "M"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_77"
QL100 = 77
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_77"
;
QS3 = "N"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_78"
QL100 = 78
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_78"
;
QS3 = "O"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_79"
QL100 = 79
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_79"
;
QS3 = "P"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_80"
QL100 = 80
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_80"
;
QS3 = "Q"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_81"
QL100 = 81
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_81"
;
QS3 = "R"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_82"
QL100 = 82
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_82"
;
QS3 = "S"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_83"
QL100 = 83
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_83"
;
QS3 = "T"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_84"
QL100 = 84
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_84"
;
QS3 = "U"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_85"
QL100 = 85
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_85"
;
QS3 = "V"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_86"
QL100 = 86
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_86"
;
QS3 = "W"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_87"
QL100 = 87
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_87"
;
QS3 = "X"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_88"
QL100 = 88
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_88"
;
QS3 = "Y"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_89"
QL100 = 89
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_89"
;
QS3 = "Z"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_90"
QL100 = 90
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_90"
;
QS3 = "["
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_91"
QL100 = 91
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_91"
;
QS3 = "\"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_92"
QL100 = 92
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_92"
;
QS3 = "]"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_93"
QL100 = 93
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_93"
;
QS3 = "^"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_94"
QL100 = 94
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_94"
;
QS3 = "_"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_95"
QL100 = 95
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_95"
;
QS3 = "`"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_96"
QL100 = 96
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_96"
;
QS3 = "a"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_97"
QL100 = 97
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_97"
;
QS3 = "b"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_98"
QL100 = 98
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_98"
;
QS3 = "c"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_99"
QL100 = 99
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_99"
;
QS3 = "d"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_100"
QL100 = 100
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_100"
;
QS3 = "e"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_101"
QL100 = 101
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_101"
;
QS3 = "f"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_102"
QL100 = 102
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_102"
;
QS3 = "g"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_103"
QL100 = 103
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_103"
;
QS3 = "h"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_104"
QL100 = 104
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_104"
;
QS3 = "i"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_105"
QL100 = 105
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_105"
;
QS3 = "j"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_106"
QL100 = 106
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_106"
;
QS3 = "k"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_107"
QL100 = 107
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_107"
;
QS3 = "l"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_108"
QL100 = 108
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_108"
;
QS3 = "m"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_109"
QL100 = 109
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_109"
;
QS3 = "n"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_110"
QL100 = 110
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_110"
;
QS3 = "o"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_111"
QL100 = 111
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_111"
;
QS3 = "p"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_112"
QL100 = 112
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_112"
;
QS3 = "q"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_113"
QL100 = 113
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_113"
;
QS3 = "r"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_114"
QL100 = 114
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_114"
;
QS3 = "s"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_115"
QL100 = 115
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_115"
;
QS3 = "t"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_116"
QL100 = 116
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_116"
;
QS3 = "u"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_117"
QL100 = 117
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_117"
;
QS3 = "v"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_118"
QL100 = 118
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_118"
;
QS3 = "w"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_119"
QL100 = 119
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_119"
;
QS3 = "x"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_120"
QL100 = 120
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_120"
;
QS3 = "y"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_121"
QL100 = 121
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_121"
;
QS3 = "z"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_122"
QL100 = 122
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_122"
;
QS3 = "{"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_123"
QL100 = 123
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_123"
;
QS3 = "|"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_124"
QL100 = 124
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_124"
;
QS3 = "}"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_125"
QL100 = 125
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_125"
;
QS3 = "~"
QL21 = STRCOMP( SRC_QS3 SEA_QS2 )
FN 10: IF +QL21 NE +0 GOTO LBL "not_126"
QL100 = 126
FN 9: IF +1 EQU +1 GOTO LBL "cont"
LBL "not_126"
;
;
LBL "cont"
L FQ207
CALL LBL QL100
;
QL10 = QL10 + 1 ;advance counter
QL13 = QL20 * Q514 ;save X-Advance
FN 12: IF +QL10 LT +QL11 GOTO LBL "start"
;
CALL LBL "end"
;
* - begin of character data
