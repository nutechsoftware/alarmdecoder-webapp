# -*- coding: utf-8 -*-

from functools import wraps

from flask import abort
from flask.ext.login import current_user

from .settings.models import Setting

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def admin_or_first_run_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if current_user.is_anonymous() or not current_user.is_admin():
			if Setting.get_by_name('setup_complete', default=False) == True:
				abort(403)

		return f(*args, **kwargs)
	return decorated_function