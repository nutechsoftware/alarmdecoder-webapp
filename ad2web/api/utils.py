# -*- coding: utf-8 -*-

import base64
import hashlib
import random

# Based on https://stackoverflow.com/a/24705557
def generate_api_key():
    altchars = random.choice(['bQ', 'rX', 'Fe', 'hU', 'XN', 'yI'])
    apikey = hashlib.sha256(str(random.getrandbits(256))).digest()

    return base64.b64encode(apikey, altchars).rstrip('==')
