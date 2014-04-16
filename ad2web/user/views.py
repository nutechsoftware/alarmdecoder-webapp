# -*- coding: utf-8 -*-

import os

from flask import Blueprint, render_template, send_from_directory, abort
from flask import current_app as APP
from flask.ext.login import login_required, current_user

from .models import User, UserHistory


user = Blueprint('user', __name__, url_prefix='/user')


@user.route('/')
@login_required
def index():
    if not current_user.is_authenticated():
        abort(403)
    return render_template('user/index.html', user=current_user)


@user.route('/<int:user_id>/profile')
def profile(user_id):
    user = User.get_by_id(user_id)
    return render_template('user/profile.html', user=user)


@user.route('/<int:user_id>/avatar/<path:filename>')
@login_required
def avatar(user_id, filename):
    dir_path = os.path.join(APP.config['UPLOAD_FOLDER'], 'user_%s' % user_id)
    return send_from_directory(dir_path, filename, as_attachment=True)

@user.route('/<int:user_id>/history')
@login_required
def history(user_id):
    if not current_user.is_authenticated():
        abort(403)
    if not current_user.is_admin() or current_user.id != user_id:
        abort(403)

    user = User.get_by_id(user_id)
    user_history = UserHistory.query.filter_by(user_id=user.id).all()
    return render_template('user/history.html', user=user, user_history=user_history)
