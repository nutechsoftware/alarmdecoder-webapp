# -*- coding: utf-8 -*-

import os
import hashlib

from datetime import datetime

from flask import Blueprint, render_template, current_app, request, flash
from flask.ext.login import login_required, current_user

from ..extensions import db
from ..user import User
from ..utils import allowed_file, make_dir
from ..decorators import admin_required
from .forms import ProfileForm, PasswordForm, DeviceSettingsForm


settings = Blueprint('settings', __name__, url_prefix='/settings')


#@settings.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.filter_by(name=current_user.name).first_or_404()
    form = ProfileForm(obj=user.user_detail,
            email=current_user.email,
            role_code=current_user.role_code,
            status_code=current_user.status_code,
            next=request.args.get('next'))

    if form.validate_on_submit():

        if form.avatar_file.data:
            upload_file = request.files[form.avatar_file.name]
            if upload_file and allowed_file(upload_file.filename):
                # Don't trust any input, we use a random string as filename.
                # or use secure_filename:
                # http://flask.pocoo.org/docs/patterns/fileuploads/

                user_upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], "user_%s" % user.id)
                current_app.logger.debug(user_upload_dir)

                make_dir(user_upload_dir)
                root, ext = os.path.splitext(upload_file.filename)
                today = datetime.now().strftime('_%Y-%m-%d')
                # Hash file content as filename.
                hash_filename = hashlib.sha1(upload_file.read()).hexdigest() + "_" + today + ext
                user.avatar = hash_filename

                avatar_ab_path = os.path.join(user_upload_dir, user.avatar)
                # Reset file curso since we used read()
                upload_file.seek(0)
                upload_file.save(avatar_ab_path)

        form.populate_obj(user)
        form.populate_obj(user.user_detail)

        db.session.add(user)
        db.session.commit()

        flash('Public profile updated.', 'success')

    return render_template('settings/profile.html', user=user,
            active="profile", form=form)


@settings.route('/password', methods=['GET', 'POST'])
@login_required
def password():
    user = User.query.filter_by(name=current_user.name).first_or_404()
    form = PasswordForm(next=request.args.get('next'))

    if form.validate_on_submit():
        form.populate_obj(user)
        user.password = form.new_password.data

        db.session.add(user)
        db.session.commit()

        flash('Password updated.', 'success')

    return render_template('settings/password.html', user=user,
            active="password", form=form)

@settings.route('/device', methods=['GET', 'POST'])
@login_required
@admin_required
def device():
    form = DeviceSettingsForm()

    if form.validate_on_submit():
        device_type = Setting.get_by_name('device_type')
        device_type.value = form.device_type.data

        device_path = Setting.get_by_name('device_path')
        device_path.value = form.device_path.data

        device_address = Setting.get_by_name('device_address')
        device_address.value = form.device_address.data

        device_port = Setting.get_by_name('device_port')
        device_port.value = form.device_port.data

        baudrate = Setting.get_by_name('baudrate')
        baudrate.value = form.baudrate.data

        ssl = Setting.get_by_name('use_ssl')
        ssl.value = form.ssl.data

        db.session.add(device_type)
        db.session.add(device_path)
        db.session.add(device_address)
        db.session.add(device_port)
        db.session.add(baudrate)
        db.session.add(ssl)
        db.session.commit()

        flash('Settings saved.', 'success')

    return render_template('settings/device.html', form=form, active='device')
