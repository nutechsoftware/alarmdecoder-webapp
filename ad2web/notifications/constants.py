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

DEFAULT_SUBSCRIPTIONS = ['on_alarm', 'on_panic', 'on_fire', 'on_arm', 'on_disarm']

SUBSCRIPTIONS = OrderedDict([
    ('on_alarm', 'Alarm system is triggered?'),
    ('on_panic', 'A panic has been detected?'),
    ('on_fire', 'A fire is detected?'),
    ('on_arm', 'Alarm system is armed?'),
    ('on_disarm', 'Alarm system is disarmed?'),
    ('on_zone_fault', 'A zone has faulted?'),
    ('on_zone_restore', 'A zone has been restored?'),
    ('on_bypass', 'A zone has been bypassed?'),
    ('on_power_changed', 'Power status has changed?'),
    ('on_low_battery', 'A low battery has been detected?'),
    ('on_boot', 'The AlarmDecoder has rebooted?'),
    ('on_relay_changed', 'A relay has been changed?'),
])
