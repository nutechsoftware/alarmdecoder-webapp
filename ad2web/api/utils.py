# -*- coding: utf-8 -*-

import os
import base64

def generate_api_key():
    return base64.b32encode(os.urandom(7)).rstrip('==')
