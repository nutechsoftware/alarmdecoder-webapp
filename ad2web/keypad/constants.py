# -*- coding: utf-8 -*-

from alarmdecoder import AlarmDecoder

FIRE = 0
POLICE = 1
MEDICAL = 2
SPECIAL_4 = 3
SPECIAL_CUSTOM = 5
STAY = 6
AWAY = 7
CHIME = 8
RESET = 9
EXIT = 10

SPECIAL_KEY_MAP = {
    FIRE: AlarmDecoder.KEY_F1,
    POLICE: AlarmDecoder.KEY_F2,
    MEDICAL: AlarmDecoder.KEY_F3,
    SPECIAL_4: AlarmDecoder.KEY_F4,
#DSC Only
    STAY: AlarmDecoder.KEY_F4,
    AWAY: chr(5) + chr(5) + chr(5),
    CHIME: chr(6) + chr(6) + chr(6),
    RESET: chr(7) + chr(7) + chr(7),
    EXIT: chr(8) + chr(8) + chr(8)
}
