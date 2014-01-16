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
from ..settings import Setting
from .forms import ProfileForm, PasswordForm, DeviceTypeForm, SerialDeviceForm, NetworkDeviceForm
from .constants import NETWORK_DEVICE, SERIAL_DEVICE

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
    # This is ugly.. better way to do this?

    type_form = DeviceTypeForm(prefix="type")
    network_form = NetworkDeviceForm(prefix="network")
    serial_form = SerialDeviceForm(prefix="serial")
    current_form, form_type = type_form, 'type'

    if type_form.submit.data:
        if type_form.validate_on_submit():
            # Save type settings.
            device_type = Setting.get_by_name('device_type')
            device_type.value = type_form.device_type.data

            db.session.add(device_type)
            db.session.commit()

            # Type form done.. populate network/serial forms.
            if device_type.value == NETWORK_DEVICE:
                network_form.device_address.data = Setting.get_by_name('device_address', network_form.device_address.default).value
                network_form.device_port.data = Setting.get_by_name('device_port', network_form.device_port.default).value
                network_form.ssl.data = Setting.get_by_name('use_ssl', network_form.ssl.default).value
                current_form, form_type = network_form, 'network'

            elif device_type.value == SERIAL_DEVICE:
                serial_form.device_path.data = Setting.get_by_name('device_path', serial_form.device_path.default).value
                serial_form.baudrate.data = Setting.get_by_name('baudrate', serial_form.baudrate.default).value
                current_form, form_type = serial_form, 'serial'

    elif network_form.submit.data:
        current_form, form_type = network_form, 'network'
        if network_form.validate_on_submit():
            # Save network device settings
            device_address = Setting.get_by_name('device_address')
            device_address.value = network_form.device_address.data

            device_port = Setting.get_by_name('device_port')
            device_port.value = network_form.device_port.data

            ssl = Setting.get_by_name('use_ssl')
            ssl.value = network_form.ssl.data

            db.session.add(device_address)
            db.session.add(device_port)
            db.session.add(ssl)
            db.session.commit()

            flash('Device settings saved.', 'success')

    elif serial_form.submit.data:
        current_form, form_type = serial_form, 'serial'
        if serial_form.validate_on_submit():
            # Save serial device settings.
            device_path = Setting.get_by_name('device_path')
            device_path.value = serial_form.device_path.data

            baudrate = Setting.get_by_name('baudrate')
            baudrate.value = serial_form.baudrate.data

            db.session.add(device_path)
            db.session.add(baudrate)
            db.session.commit()

            flash('Device settings saved.', 'success')

    else:
        # Populate saved device type if this is a fresh page load.
        type_form.device_type.data = Setting.get_by_name('device_type', type_form.device_type.default).value

    return render_template('settings/device.html', form=current_form, active='device', form_type=form_type)
