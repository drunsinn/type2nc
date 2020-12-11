BEGIN PGM TYPE2NC_DEMO MM
BLK FORM 0.1 Z X+0 Y+0 Z-10
BLK FORM 0.2  X+300  Y+40 Z+0
;
TOOL CALL "GRAVIER" Z S5000 F200
;
QS10 = " ABC abc 123 !%& "
QS10 = QS10 || "(%0x0298 %0x203f %0x0298) "
QS10 = QS10 || "%0x041f%0x0440%0x0438%0x0432%0x0435%0x0442 "
QS10 = QS10 || "%0x043c%0x0438%0x0440 "
QS10 = QS10 || "%0x4f60%0x597d%0x4e16%0x754c "
QS10 = QS10 || "%0x0645%0x0631%0x062d%0x0628%0x0627 "
QS10 = QS10 || "%0x0628%0x0627%0x0644%0x0639%0x0627%0x0644%0x0645 "
;
;
Q1600 = 0 ;surface in Z
Q1601 = - 0.5 ;depth
Q1602 = 5 ;safe height
Q1605 = 6000 ;feedrate
Q1606 = 10 ;aprox. font hight
Q1607 = 5 ;angle
;
;
Q1603 = 10 ;start X
Q1604 = 10 ;start Y
QS1 = "NotoSansDisplay-Regular.H" || QS10
CALL PGM NotoSansDisplay-Regular.H
;
;
M30
;
END PGM TYPE2NC_DEMO MM
