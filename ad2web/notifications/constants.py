# -*- coding: utf-8 -*-

from collections import OrderedDict

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
LRR = 14
READY = 15
CHIME = 16

CRITICAL_EVENTS = [POWER_CHANGED, ALARM, BYPASS, ARM, DISARM, ZONE_FAULT, \
                    ZONE_RESTORE, FIRE, PANIC]

DEFAULT_EVENT_MESSAGES = {
    ARM: 'The alarm system has been armed {arm_type}.',
    DISARM: 'The alarm system has been disarmed.',
    POWER_CHANGED: 'Power status has changed to {status}.',
    ALARM: 'The alarm system has been triggered on zone {zone_name} ({zone})!',
    ALARM_RESTORED: 'The alarm system has stopped signaling the alarm for zone {zone_name} ({zone}).',
    FIRE: 'Fire status has changed to {status}',
    BYPASS: 'A zone has been bypassed.',
    BOOT: 'The AlarmDecoder has finished booting.',
    #CONFIG_RECEIVED: 'AlarmDecoder has been configured.',
    ZONE_FAULT: 'Zone {zone_name} ({zone}) has been faulted.',
    ZONE_RESTORE: 'Zone {zone_name} ({zone}) has been restored.',
    LOW_BATTERY: 'Low battery detected.',
    PANIC: 'Panic!',
    LRR: 'Received LRR / Contact ID event',
    READY: 'Ready status has changed to {status}',
    CHIME: 'Chime status has changed to {status}',
    RELAY_CHANGED: 'A relay at {address}:{channel} has changed to {status}.'
}

EVENT_TYPES = {
    ARM: 'arm',
    DISARM: 'disarm',
    POWER_CHANGED: 'power changed',
    ALARM: 'alarm',
    FIRE: 'fire changed',
    BYPASS: 'bypass',
    BOOT: 'boot',
    CONFIG_RECEIVED: 'config received',
    ZONE_FAULT: 'zone fault',
    ZONE_RESTORE: 'zone restore',
    LOW_BATTERY: 'low battery',
    PANIC: 'panic',
    RELAY_CHANGED: 'relay changed',
    LRR: 'lrr',
    READY: 'ready changed',
    CHIME: 'chime changed',
    ALARM_RESTORED: 'alarm restored'
}

EMAIL = 0
GOOGLETALK = 1
PUSHOVER = 2
TWILIO = 3
NMA = 4
PROWL = 5
GROWL = 6
CUSTOM = 7
TWIML = 8
SMARTTHINGS = 9
UPNPPUSH = 10

NOTIFICATION_TYPES = {
    EMAIL: 'email',
#    GOOGLETALK: 'googletalk',
    PUSHOVER: 'pushover',
    TWILIO: 'twilio',
    NMA: 'NMA',
    PROWL: 'prowl',
    GROWL: 'growl',
    CUSTOM: 'custom',
    TWIML: 'twiml',
    UPNPPUSH: 'upnppush',
    SMARTTHINGS: 'smartthings'
}

NOTIFICATIONS = {
    EMAIL: ('email', u'Email'),
#    GOOGLETALK: ('googletalk', u'Google Talk'),
    PUSHOVER: ('pushover', u'Pushover.net'),
    TWILIO: ('twilio', u'Twilio'),
    NMA: ('NMA', u'NotifyMyAndroid'),
    PROWL: ('prowl', u'Prowl'),
    GROWL: ('growl', u'Growl'),
    CUSTOM: ('custom', u'Custom'),
    TWIML: ('twiml', u'TwiML'),
    UPNPPUSH: ('upnppush', u'UPNP Push'),
    SMARTTHINGS: ('smartthings', u'SmartThings Integration')
}

DEFAULT_SUBSCRIPTIONS = [ALARM, PANIC, FIRE, ARM, DISARM]

SUBSCRIPTIONS = OrderedDict([
    (ALARM, 'Alarm system is triggered'),
    (ALARM_RESTORED, 'Alarm system stops signaling'),
    (PANIC, 'A panic has been detected'),
    (FIRE, 'The fire state has changed'),
    (ARM, 'Alarm system is armed'),
    (DISARM, 'Alarm system is disarmed'),
    (ZONE_FAULT, 'A zone has faulted'),
    (ZONE_RESTORE, 'A zone has been restored'),
    (BYPASS, 'A zone has been bypassed'),
    (POWER_CHANGED, 'Power status has changed'),
    (LOW_BATTERY, 'A low battery has been detected'),
    (BOOT, 'The AlarmDecoder has rebooted'),
    (RELAY_CHANGED, 'A relay has been changed'),
    (LRR, 'A LRR event was detected'),
    (READY, 'A READY event was detected'),
    (CHIME, 'A CHIME event was detected'),
])

PUSHOVER_URL = "api.pushover.net:443"
PUSHOVER_PATH = "/1/messages.json"

LOWEST = 0
LOW = 1
NORMAL = 2
HIGH = 3
EMERGENCY = 4

PUSHOVER_PRIORITIES = {
    LOWEST: (-2, u'LOWEST'),
    LOW: (-1, u'LOW'),
    NORMAL: (0, u'NORMAL'),
    HIGH: (1, u'HIGH'),
    EMERGENCY: (2, u'EMERGENCY')
}

NMA_URL = "www.notifymyandroid.com"
NMA_PATH = "/publicapi/notify"

NMA_USER_AGENT = "NMA/v1.0"
NMA_EVENT = "AlarmDecoder: Alarm Event"
NMA_METHOD = "POST"
NMA_CONTENT_TYPE = "text/html"
NMA_HEADER_CONTENT_TYPE = "application/x-www-form-urlencoded"

NMA_PRIORITIES = {
    LOWEST: (-2, u'VERY LOW'),
    LOW: (-1, u'MODERATE'),
    NORMAL: (0, u'NORMAL'),
    HIGH: (1, u'HIGH'),
    EMERGENCY: (2, u'EMERGENCY')
}

PROWL_URL = "api.prowlapp.com"
PROWL_PATH = "/publicapi/add"

PROWL_USER_AGENT = "PROWL/v1.0"
PROWL_EVENT = "AlarmDecoder: Alarm Event"
PROWL_METHOD = "POST"
PROWL_CONTENT_TYPE = "text/html"
PROWL_HEADER_CONTENT_TYPE = "application/x-www-form-urlencoded"

PROWL_PRIORITIES = {
    LOWEST: (-2, u'VERY LOW'),
    LOW: (-1, u'MODERATE'),
    NORMAL: (0, u'NORMAL'),
    HIGH: (1, u'HIGH'),
    EMERGENCY: (2, u'EMERGENCY')
}

GROWL_APP_NAME = 'AlarmDecoder'
GROWL_TITLE = 'AlarmDecoder: Alarm Event'
GROWL_DEFAULT_NOTIFICATIONS = ["AlarmDecoder", "AlarmDecoder: Alarm Event"]

GROWL_PRIORITIES = {
    LOWEST: (-2, u'VERY LOW'),
    LOW: (-1, u'MODERATE'),
    NORMAL: (0, u'NORMAL'),
    HIGH: (1, u'HIGH'),
    EMERGENCY: (2, u'EMERGENCY')
}

URLENCODE = 0
JSON = 1
XML = 2

CUSTOM_USER_AGENT = "AlarmDecoder/v1.0"
CUSTOM_METHOD = "POST"
CUSTOM_METHOD_GET = "GET"
CUSTOM_METHOD_POST = 0
CUSTOM_METHOD_GET_TYPE = 1

CUSTOM_CONTENT_TYPES = {
    URLENCODE: "application/x-www-form-urlencoded",
    JSON: "application/json",
    XML: "application/xml"
}

CUSTOM_TIMESTAMP = 0
CUSTOM_MESSAGE = 1

CUSTOM_REPLACER_SEARCH = {
    CUSTOM_TIMESTAMP: "{{timestamp}}",
    CUSTOM_MESSAGE: "{{message}}"
}

TIME_MULTIPLIER = {
    "Seconds": 1,
    "Minutes": 60,
    "Hours": 3600,
    "Days": 86400
}

XML_EVENT_TEMPLATE = """<e:propertyset xmlns:e="urn:schemas-upnp-org:service:AlarmDecoder:1">
{0}{1}{2}{3}{4}
</e:propertyset>"""

XML_EVENT_PROPERTY = """  <e:property>
    <{0}>{1}</{0}>
  </e:property>
"""
