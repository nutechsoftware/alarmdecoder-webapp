# -*- coding: utf-8 -*-

ARM = 0
DISARM = 1
POWER_CHANGED = 2
ALARM = 3
FIRE = 4
BYPASS = 5
BOOT = 6
CONFIG_RECEIVED = 7
ZONE_FAULT = 8
ZONE_RESTORE = 9
LOW_BATTERY = 10
PANIC = 11
RELAY_CHANGED = 12
ALARM_RESTORED = 13

EVENT_TYPES = {
    ARM: 'arm',
    DISARM: 'disarm',
    POWER_CHANGED: 'power changed',
    ALARM: 'alarm',
    FIRE: 'fire',
    BYPASS: 'bypass',
    BOOT: 'boot',
    CONFIG_RECEIVED: 'config received',
    ZONE_FAULT: 'zone fault',
    ZONE_RESTORE: 'zone restore',
    LOW_BATTERY: 'low battery',
    PANIC: 'panic',
    RELAY_CHANGED: 'relay changed',
    ALARM_RESTORED: 'alarm restored'
}
