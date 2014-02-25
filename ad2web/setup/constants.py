# -*- coding: utf-8 -*-

SETUP_TYPE = 0
SETUP_LOCATION = 1
SETUP_NETWORK = 2
SETUP_LOCAL = 3
SETUP_DEVICE = 4
SETUP_COMPLETE = 100

STAGES = {
	SETUP_TYPE: 'device_type',
	SETUP_LOCATION: 'device_location',
	SETUP_NETWORK: 'network_device_settings',
	SETUP_LOCAL: 'local_device_settings',
	SETUP_DEVICE: 'alarmdecoder_settings',

	SETUP_COMPLETE: 'setup_complete'
}

NETWORK_DEVICE = 0
SERIAL_DEVICE = 1

BAUDRATES = [115200, 19200]

DEFAULT_PATHS = {
	None: '/dev/ttyUSB0',
	'AD2USB': '/dev/ttyUSB0',
	'AD2PI': '/dev/ttyAMA0',
	'AD2SERIAL': '/dev/ttyS0'
}

DEFAULT_BAUDRATES = {
	None: 115200,
	'AD2USB': 115200,
	'AD2PI': 115200,
	'AD2SERIAL': 19200
}