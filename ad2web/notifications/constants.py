# -*- coding: utf-8 -*-

from collections import OrderedDict

EMAIL = 0
GOOGLETALK = 1

NOTIFICATION_TYPES = {
    EMAIL: 'email',
    GOOGLETALK: 'googletalk',
}

NOTIFICATIONS = {
    EMAIL: ('email', u'Email'),
    GOOGLETALK: ('googletalk', u'Google Talk'),
}

SUBSCRIPTIONS = OrderedDict([
    ('on_arm', 'Alarm system is armed?'),
    ('on_disarm', 'Alarm system is disarmed?'),
    ('on_power_changed', 'Power status has changed?'),
    ('on_alarm', 'Alarm system is triggered?'),
    ('on_fire', 'A fire is detected?'),
    ('on_bypass', 'A zone has been bypassed?'),
    ('on_boot', 'The AlarmDecoder has rebooted?'),
    ('on_zone_fault', 'A zone has faulted?'),
    ('on_zone_restore', 'A zone has been restored?'),
    ('on_low_battery', 'A low battery has been detected?'),
    ('on_panic', 'A panic has been detected?'),
    ('on_relay_changed', 'A relay has been changed?'),
])
