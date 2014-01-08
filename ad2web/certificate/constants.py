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

# Certificate package types
TGZ = 0
PKCS12 = 1
BKS = 2

PACKAGE_TYPES = {
    TGZ: 'tgz',
    PKCS12: 'pkcs12',
    BKS: 'bks'
}

PACKAGE_TYPE_LOOKUP = {
    'tgz': TGZ,
    'pkcs12': PKCS12,
    'bks': BKS
}
