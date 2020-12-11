* - End of character data
;
LBL "end"
;reset rotation
CYCL DEF 10.0 DREHUNG
CYCL DEF 10.1  ROT+0
;
;reset offset
QL13 = - 1 * (QL13 + Q1603)
QL14 = - 1 * (QL14 + Q1604)
CYCL DEF 7.0 NULLPUNKT
CYCL DEF 7.1  IX+QL13
CYCL DEF 7.2  IY+QL14
;
;reset scale factor
CYCL DEF 26.0 MASSFAKTOR ACHSSPEZ.
CYCL DEF 26.1 X1 Y1
