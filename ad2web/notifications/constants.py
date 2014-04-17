# -*- coding: utf-8 -*-

EMAIL = 0
GOOGLETALK = 1

"""Alarm Event/Message Types"""
POWER_CHANGED = 0
ALARM = 1
BYPASS = 2
ARM = 3
DISARM = 4
ZONE_FAULT = 5
ZONE_RESTORE = 6
FIRE = 7
PANIC = 8
LRR = 9
EXP = 10
REL = 11
RFX = 12
AUI = 13
KPE = 14

"""LRR Event Types"""
ALARM_EXIT_ERROR = 0
TROUBLE = 1
BYPASS = 2
ACLOSS = 3
LOWBAT = 4
TEST_CALL = 5
OPEN = 6
ARM_AWAY = 7
RFLOWBAT = 8
CANCEL = 9
RESTORE = 10
TROUBLE_RESTORE = 11
BYPASS_RESTORE = 12
AC_RESTORE = 13
LOWBAT_RESTORE = 14
RFLOWBAT_RESTORE = 15
TEST_RESTORE = 16
ALARM_PANIC = 17
ALARM_FIRE = 18
ALARM_ENTRY = 19
ALARM_AUX = 20
ALARM_AUDIBLE = 21
ALARM_SILENT = 22
ALARM_PERIMETER = 23

NOTIFICATION_TYPES = {
    EMAIL: 'email',
    GOOGLETALK: 'googletalk',
}

NOTIFICATIONS = {
    EMAIL: ('email', u'Email'),
    GOOGLETALK: ('googletalk', u'Google Talk'),
}


CUSTOM_NOTIFICATION_EVENTS_TYPES = {
    POWER_CHANGED: u'Power Changed',
    ALARM: u'Alarm',
    BYPASS: u'Bypass',
    ARM: u'Arm',
    DISARM: u'Disarm',
    ZONE_FAULT: u'Zone Fault',
    ZONE_RESTORE: u'Zone Restore',
    FIRE: u'Fire',
    PANIC: u'Panic',
    LRR: u'LRR Message',
    EXP: u'EXP Message',
    REL: u'REL Message',
    RFX: u'RFX Message',
    AUI: u'AUI Message',
    KPE: u'Keypress Event',
}

LRR_EVENTS_TYPES = {
    ALARM_EXIT_ERROR: u'Alarm Exit Error',
    TROUBLE: u'Trouble',
    BYPASS: u'Bypass',
    ACLOSS: u'AC Loss',
    LOWBAT: u'Low Battery',
    TEST_CALL: u'Test Call',
    OPEN: u'Open',
    ARM_AWAY: u'Arm Away',
    RFLOWBAT: u'RF Low Battery',
    CANCEL: u'Cancelled',
    RESTORE: u'Restored',
    TROUBLE_RESTORE: u'Trouble Event Restore',
    BYPASS_RESTORE: u'Bypassed Zone Restore',
    AC_RESTORE: u'AC Power Restore',
    LOWBAT_RESTORE: u'Low Battery Restore',
    RFLOWBAT_RESTORE: u'RF Low Battery Restore',
    TEST_RESTORE: u'Test Mode Zone Restore',
    ALARM_PANIC: u'Panic',
    ALARM_FIRE: u'Fire',
    ALARM_ENTRY: u'Entry',
    ALARM_AUX: u'Aux',
    ALARM_AUDIBLE: u'Audible Alarm',
    ALARM_SILENT: u'Silent Alarm',
    ALARM_PERIMETER: u'Perimeter Alarm',
}
