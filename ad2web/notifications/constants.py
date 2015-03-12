# -*- coding: utf-8 -*-

from collections import OrderedDict
import chump

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

CRITICAL_EVENTS = [POWER_CHANGED, ALARM, BYPASS, ARM, DISARM, ZONE_FAULT, \
                    ZONE_RESTORE, FIRE, PANIC]

DEFAULT_EVENT_MESSAGES = {
    ARM: 'The alarm system has been armed.',
    DISARM: 'The alarm system has been disarmed.',
    POWER_CHANGED: 'Power status has changed to {status}.',
    ALARM: 'The alarm system has been triggered on zone {zone_name} ({zone})!',
    ALARM_RESTORED: 'The alarm system has stopped signaling the alarm for zone {zone_name} ({zone}).',
    FIRE: 'There is a fire!',
    BYPASS: 'A zone has been bypassed.',
    BOOT: 'The AlarmDecoder has finished booting.',
    #CONFIG_RECEIVED: 'AlarmDecoder has been configured.',
    ZONE_FAULT: 'Zone {zone_name} ({zone}) has been faulted.',
    ZONE_RESTORE: 'Zone {zone_name} ({zone}) has been restored.',
    LOW_BATTERY: 'Low battery detected.',
    PANIC: 'Panic!',
    RELAY_CHANGED: 'A relay has changed.'
}

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

EMAIL = 0
GOOGLETALK = 1
PUSHOVER = 2
TWILIO = 3

NOTIFICATION_TYPES = {
    EMAIL: 'email',
    GOOGLETALK: 'googletalk',
    PUSHOVER: 'pushover',
    TWILIO: 'twilio',
}

NOTIFICATIONS = {
    EMAIL: ('email', u'Email'),
    GOOGLETALK: ('googletalk', u'Google Talk'),
    PUSHOVER: ('pushover', u'Pushover.net'),
    TWILIO: ('twilio', u'Twilio'),
}

DEFAULT_SUBSCRIPTIONS = [ALARM, PANIC, FIRE, ARM, DISARM]

SUBSCRIPTIONS = OrderedDict([
    (ALARM, 'Alarm system is triggered?'),
    (ALARM_RESTORED, 'Alarm system stops signaling?'),
    (PANIC, 'A panic has been detected?'),
    (FIRE, 'A fire is detected?'),
    (ARM, 'Alarm system is armed?'),
    (DISARM, 'Alarm system is disarmed?'),
    (ZONE_FAULT, 'A zone has faulted?'),
    (ZONE_RESTORE, 'A zone has been restored?'),
    (BYPASS, 'A zone has been bypassed?'),
    (POWER_CHANGED, 'Power status has changed?'),
    (LOW_BATTERY, 'A low battery has been detected?'),
    (BOOT, 'The AlarmDecoder has rebooted?'),
    (RELAY_CHANGED, 'A relay has been changed?'),
])

PUSHOVER_URL = "api.pushover.net:443"
PUSHOVER_PATH = "/1/messages.json"

LOWEST = 0
LOW = 1
NORMAL = 2
HIGH = 3
EMERGENCY = 4

PUSHOVER_PRIORITIES = {
    LOWEST: (chump.LOWEST, u'LOWEST'),
    LOW: (chump.LOW, u'LOW'),
    NORMAL: (chump.NORMAL, u'NORMAL'),
    HIGH: (chump.HIGH, u'HIGH'),
    EMERGENCY: (chump.EMERGENCY, u'EMERGENCY')
}
