# -*- coding: utf-8 -*-

EMAIL = 0
GOOGLETALK = 1

# Alarm Event/Message Types
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

# LRR Event Types
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
    POWER_CHANGED: 'powerchanged',
    ALARM: 'alarm',
    BYPASS: 'bypass',
    ARM: 'arm',
    DISARM: 'disarm',
    ZONE_FAULT: 'zonefault',
    ZONE_RESTORE: 'zonerestore',
    FIRE: 'fire',
    PANIC: 'panic',
    LRR: 'lrrmessage',
    EXP: 'expmessage',
    REL: 'relmessage',
    RFX: 'rfxmessage',
    AUI: 'auimessage',
    KPE: 'keypressevent',
}

CUSTOM_NOTIFICATION_EVENTS = {
    POWER_CHANGED: ('powerchanged', u'Power Changed'),
    ALARM: ('alarm', u'Alarm'),
    BYPASS: ('bypass', u'Bypass'),
    ARM: ('arm', u'Arm'),
    DISARM: ('disarm', u'Disarm'),
    ZONE_FAULT: ('zonefault', u'Zone Fault'),
    ZONE_RESTORE: ('zonerestore', u'Zone Restore'),
    FIRE: ('fire', u'Fire'),
    PANIC: ('panic', u'Panic'),
    LRR: ('lrrmessage', u'LRR Message'),
    EXP: ('expmessage', u'EXP Message'),
    REL: ('relmessage', u'REL Message'),
    RFX: ('rfxmessage', u'RFX Message'),
    AUI: ('auimessage', u'AUI Message'),
    KPE: ('keypressevent', u'Keypress Event'),
}

LRR_EVENTS_TYPES = {
    ALARM_EXIT_ERROR: 'alarmexiterror',
    TROUBLE: 'trouble',
    BYPASS: 'bypass',
    ACLOSS: 'acloss',
    LOWBAT: 'lowbattery',
    TEST_CALL: 'testcall',
    OPEN: 'open',
    ARM_AWAY: 'armaway',
    RFLOWBAT: 'rflowbat',
    CANCEL: 'cancel',
    RESTORE: 'restore',
    TROUBLE_RESTORE: 'troublerestore',
    BYPASS_RESTORE: 'bypassrestore',
    AC_RESTORE: 'acrestore',
    LOWBAT_RESTORE: 'lowbatrestore',
    RFLOWBAT_RESTORE: 'rflowbatrestore',
    TEST_RESTORE: 'testrestore',
    ALARM_PANIC: 'alarmpanic',
    ALARM_FIRE: 'alarmfire',
    ALARM_ENTRY: 'alarmentry',
    ALARM_AUX: 'alarmaux',
    ALARM_AUDIBLE: 'alarmaudible',
    ALARM_SILENT: 'alarmsilent',
    ALARM_PERIMETER: 'alarmperimeter',
}

LRR_EVENTS = {
    ALARM_EXIT_ERROR: ('alarmexiterror', u'Alarm Exit Error'),
    TROUBLE: ('trouble', u'Trouble'),
    BYPASS: ('bypass', u'Bypass'),
    ACLOSS: ('acloss', u'AC Loss'),
    LOWBAT: ('lowbattery' u'Low Battery'),
    TEST_CALL: ('testcall', u'Test Call'),
    OPEN: ('open', u'Open'),
    ARM_AWAY: ('armaway', u'Arm Away'),
    RFLOWBAT: ('rflowbat', u'RF Low Battery'),
    CANCEL: ('cancel', u'Cancelled'),
    RESTORE: ('restore', u'Restored'),
    TROUBLE_RESTORE: ('troublerestore', u'Trouble Event Restore'),
    BYPASS_RESTORE: ('bypassrestore', u'Bypassed Zone Restore'),
    AC_RESTORE: ('acrestore', u'AC Power Restore'),
    LOWBAT_RESTORE: ('lowbatrestore', u'Low Battery Restore'),
    RFLOWBAT_RESTORE: ('rflowbatrestore', u'RF Low Battery Restore'),
    TEST_RESTORE: ('testrestore', u'Test Mode Zone Restore'),
    ALARM_PANIC: ('alarmpanic', u'Panic'),
    ALARM_FIRE: ('alarmfire', u'Fire'),
    ALARM_ENTRY: ('alarmentry', u'Entry'),
    ALARM_AUX: ('alarmaux', u'Aux'),
    ALARM_AUDIBLE: ('alarmaudible', u'Audible Alarm'),
    ALARM_SILENT: ('alarmsilent', u'Silent Alarm'),
    ALARM_PERIMETER: ('alarmperimeter', u'Perimeter Alarm'),
}

