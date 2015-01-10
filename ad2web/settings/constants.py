# -*- coding: utf-8 -*-

from ..setup.constants import NETWORK_DEVICE, SERIAL_DEVICE
from ..user import User, UserDetail
from ..settings import Setting
from ..certificate import Certificate
from ..notifications import Notification, NotificationSetting
from ..zones import Zone
from ..keypad import KeypadButton
from ..cameras import Camera

HOSTS_FILE = '/etc/hosts'
HOSTNAME_FILE = '/etc/hostname'
NETWORK_FILE = '/etc/network/interfaces'

EXPORT_MAP = {
	'settings.json': Setting,
	'certificates.json': Certificate,
	'notifications.json': Notification,
	'notification_settings.json': NotificationSetting,
	'users.json': User,
	'user_details.json': UserDetail,
	'zones.json': Zone,
    'buttons.json': KeypadButton,
    'cameras.json': Camera
}
