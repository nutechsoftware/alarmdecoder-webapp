# -*- coding: utf-8 -*-

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from flask_mail import Mail
mail = Mail()

# Load older cache extension if new caching  module is not available.
# Flash Cache is EOL and is being replaced with caching
try:
    ## New
    from flask_caching import Cache
except ImportError:
    ## Old remove 2022?
    from flask_cache import Cache
cache = Cache()

from flask_login import LoginManager
login_manager = LoginManager()

from flask_openid import OpenID
oid = OpenID()
