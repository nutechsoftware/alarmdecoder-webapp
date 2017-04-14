# -*- coding: utf-8 -*-

SETUP_INDEX = None
SETUP_TYPE = 0
SETUP_LOCATION = 1
SETUP_NETWORK = 2
SETUP_LOCAL = 3
SETUP_SSLCLIENT = 4
SETUP_SSLSERVER = 5
SETUP_DEVICE = 6
SETUP_TEST = 7
SETUP_ACCOUNT = 8
SETUP_COMPLETE = 100

SETUP_STAGE_ENDPOINT = {
    SETUP_INDEX: 'setup.index',
    SETUP_TYPE: 'setup.type',
    SETUP_LOCATION: 'setup.location',
    SETUP_NETWORK: 'setup.network',
    SETUP_SSLCLIENT: 'setup.sslclient',
    SETUP_SSLSERVER: 'setup.sslserver',
    SETUP_LOCAL: 'setup.local',
    SETUP_DEVICE: 'setup.device',
    SETUP_TEST: 'setup.test',
    SETUP_ACCOUNT: 'setup.account',
    SETUP_COMPLETE: 'frontend.index'
}

SETUP_ENDPOINT_STAGE = {
    None: SETUP_INDEX,
    'setup.index': SETUP_INDEX,
    'setup.type': SETUP_TYPE,
    'setup.location': SETUP_LOCATION,
    'setup.network': SETUP_NETWORK,
    'setup.sslclient': SETUP_SSLCLIENT,
    'setup.sslserver': SETUP_SSLSERVER,
    'setup.local': SETUP_LOCAL,
    'setup.device': SETUP_DEVICE,
    'setup.test': SETUP_TEST,
    'setup.account': SETUP_ACCOUNT,
    'frontend.index': SETUP_COMPLETE
}

NETWORK_DEVICE = 0
SERIAL_DEVICE = 1

BAUDRATES = [115200, 19200]

DEFAULT_PATHS = {
    None: '/dev/ttyUSB0',
    'AD2USB': '/dev/ttyUSB0',
    'AD2PI': '/dev/serial0',
    'AD2SERIAL': '/dev/ttyS0'
}

DEFAULT_BAUDRATES = {
    None: 115200,
    'AD2USB': 115200,
    'AD2PI': 115200,
    'AD2SERIAL': 19200
}
