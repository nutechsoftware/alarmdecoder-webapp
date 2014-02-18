# -*- coding: utf-8 -*-

from ..settings.constants import BAUDRATES, DEFAULT_BAUDRATES

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