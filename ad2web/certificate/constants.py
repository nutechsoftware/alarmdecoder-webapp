# -*- coding: utf-8 -*-

# Certificate types
CA = 0
SERVER = 1
CLIENT = 2
INTERNAL = 3

CERTIFICATE_TYPES = {
    CA: 'CA certificate',
    SERVER: 'Server certificate',
    CLIENT: 'Client certificate',
    INTERNAL: 'Internal certificate'
}

# Certificate status
REVOKED = 0
ACTIVE = 1

CERTIFICATE_STATUS = {
    REVOKED: 'revoked',
    ACTIVE: 'active'
}

