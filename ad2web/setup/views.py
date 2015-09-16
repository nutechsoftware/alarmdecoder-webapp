# -*- coding: utf-8 -*-

import os
import glob
import platform

from flask import Blueprint, render_template, abort, g, request, flash, Response, redirect, url_for
from flask import current_app
from flask.ext.login import login_required, current_user

from ..extensions import db
from ..decorators import admin_required, admin_or_first_run_required
from ..settings.models import Setting
from ..certificate.models import Certificate
from ..certificate.constants import CA, SERVER, CLIENT, INTERNAL, ACTIVE as CERT_ACTIVE
from .forms import (DeviceTypeForm, NetworkDeviceForm, LocalDeviceForm,
                   SSLForm, SSLHostForm, DeviceForm, TestDeviceForm, CreateAccountForm, LocalDeviceFormUSB)
from .constants import (SETUP_TYPE, SETUP_LOCATION, SETUP_NETWORK,
                    SETUP_LOCAL, SETUP_DEVICE, SETUP_TEST, SETUP_COMPLETE, BAUDRATES,
                    DEFAULT_BAUDRATES, DEFAULT_PATHS, SETUP_ENDPOINT_STAGE)
from ..ser2sock import ser2sock
from ..user.models import User
from ..user.constants import ADMIN as USER_ADMIN, ACTIVE as USER_ACTIVE

setup = Blueprint('setup', __name__, url_prefix='/setup')

def set_stage(stage):
    setup_stage = Setting.get_by_name('setup_stage')
    setup_stage.value = stage
    db.session.add(setup_stage)

@setup.context_processor
def setup_context_processor():
    return {}

@setup.route('/')
@admin_or_first_run_required
def index():
    return render_template('setup/index.html')

@setup.route('/type', methods=['GET', 'POST'])
def type():
    form = DeviceTypeForm()
    if not form.is_submitted():
        device_type = Setting.get_by_name('device_type').value
        if device_type:
            form.device_type.data = device_type

        device_location = Setting.get_by_name('device_location').value
        if device_location:
            managed_ser2sock = Setting.get_by_name('managed_ser2sock', default=False).value
            if managed_ser2sock:
                form.device_location.data = 'local'
            else:
                form.device_location.data = device_location

    if form.validate_on_submit():
        device_type = Setting.get_by_name('device_type')
        device_type.value = form.device_type.data
        db.session.add(device_type)

        device_location = Setting.get_by_name('device_location')
        device_location.value = form.device_location.data
        db.session.add(device_location)

        next_stage = 'setup.{0}'.format(device_location.value)
        set_stage(SETUP_ENDPOINT_STAGE[next_stage])

        db.session.commit()

        return redirect(url_for(next_stage))

    return render_template('setup/type.html', form=form)

@setup.route('/local', methods=['GET', 'POST'])
@admin_or_first_run_required
def local():
    operating_system = platform.system()
    device_search_path = None

    if operating_system != 'Darwin' and operating_system != 'Windows':
        device_search_path = '/dev/ttyUSB*'
    else:
        device_search_path = '/dev/tty.usb*'

    device_type = Setting.get_by_name('device_type').value

    form = None

    if device_type != 'AD2USB':
        form = LocalDeviceForm()
    else:
        form = LocalDeviceFormUSB()
        usb_devices = _iterate_usb(device_search_path)
        if not usb_devices:
            flash('No devices found - please make sure your AD2USB is plugged into a USB Port and refresh the page.', 'error')

        form.device_path.choices = [(usb_devices[i], usb_devices[i]) for i in usb_devices]

    if not form.is_submitted():
        if device_type != 'AD2USB':
            device_path = Setting.get_by_name('device_path').value
            if device_path:
                form.device_path.data = device_path
            else:
                form.device_path.data = DEFAULT_PATHS[device_type]
        else:
            usb_devices = _iterate_usb(device_search_path)
            device_path = Setting.get_by_name('device_path').value
            form.device_path.choices = [(usb_devices[i], usb_devices[i]) for i in usb_devices]
            if device_path:
                form.device_path.default = device_path
            else:
                form.device_path.default = DEFAULT_PATHS[device_type]

        baudrate = Setting.get_by_name('device_baudrate').value
        if baudrate:
            form.baudrate.data = baudrate
        else:
            form.baudrate.data = DEFAULT_BAUDRATES[device_type]

        if ser2sock.exists():
            managed = Setting.get_by_name('managed_ser2sock').value
            if managed:
                form.confirm_management.data = managed
        else:
            del form.confirm_management

    if form.validate_on_submit():
        device_path = Setting.get_by_name('device_path')

        if device_type == 'AD2USB':
            usb_devices = _iterate_usb(device_search_path)
            form.device_path.choices = [(usb_devices[i], usb_devices[i]) for i in usb_devices]

        baudrate = Setting.get_by_name('device_baudrate')
        managed = Setting.get_by_name('managed_ser2sock')
        device_path.value = form.device_path.data
        baudrate.value = form.baudrate.data
        managed.value = form.confirm_management.data

        db.session.add(device_path)
        db.session.add(baudrate)
        db.session.add(managed)

        next_stage = 'setup.device'
        if form.confirm_management.data == True:
            next_stage = 'setup.sslserver'
        else:
            if ser2sock.exists():
                try:
                    ser2sock.stop()
                except OSError:
                    flash("We've detected that ser2sock is running and failed to stop it.  There may be communication issues unless it is killed manually.", 'warning')

        set_stage(SETUP_ENDPOINT_STAGE[next_stage])
        db.session.commit()

        return redirect(url_for(next_stage))

    return render_template('setup/local.html', form=form)

def _iterate_usb(device_path):
    ports = glob.glob(device_path)
    ports.sort()
    devices = {}

    for port in ports:
        port_path = os.path.join('/dev', port.split('/')[-1])
        devices[port_path] = port_path

    return devices

@setup.route('/network', methods=['GET', 'POST'])
@admin_or_first_run_required
def network():
    form = NetworkDeviceForm()
    if not form.is_submitted():
        device_address = Setting.get_by_name('device_address').value
        if device_address:
            form.device_address.data = device_address

        device_port = Setting.get_by_name('device_port').value
        if device_port:
            form.device_port.data = device_port

        use_ssl = Setting.get_by_name('use_ssl').value
        if use_ssl is not None:
            form.ssl.data = use_ssl

    if form.validate_on_submit():
        device_address = Setting.get_by_name('device_address')
        device_port = Setting.get_by_name('device_port')
        ssl = Setting.get_by_name('use_ssl')

        device_address.value = form.device_address.data
        device_port.value = form.device_port.data
        ssl.value = form.ssl.data

        db.session.add(device_address)
        db.session.add(device_port)
        db.session.add(ssl)

        next_stage = 'setup.device'
        if form.ssl.data == True:
            next_stage = 'setup.sslclient'

        set_stage(SETUP_ENDPOINT_STAGE[next_stage])
        db.session.commit()

        return redirect(url_for(next_stage))

    return render_template('setup/network.html', form=form)

@setup.route('/sslclient', methods=['GET', 'POST'])
@admin_or_first_run_required
def sslclient():
    form = SSLForm()
    form.multipart = True
    if form.validate_on_submit():
        ca_cert_data = form.ca_cert.data.stream.read()
        cert_data = form.cert.data.stream.read()
        key_data = form.key.data.stream.read()

        # TODO: Fix one()
        ca_cert = Certificate.query.filter_by(name='AlarmDecoder CA').one()
        ca_cert.certificate = ca_cert_data
        ca_cert.key = ''
        db.session.add(ca_cert)

        # TODO: Fix one()
        internal_cert = Certificate.query.filter_by(name='AlarmDecoder Internal').one()
        internal_cert.certificate = cert_data
        internal_cert.key = key_data
        db.session.add(internal_cert)

        use_ssl = Setting.get_by_name('use_ssl')
        use_ssl.value = True
        db.session.add(use_ssl)

        next_stage = 'setup.device'
        set_stage(SETUP_ENDPOINT_STAGE[next_stage])
        db.session.commit()

        return redirect(url_for(next_stage))

    return render_template('setup/sslclient.html', form=form)

@setup.route('/sslserver', methods=['GET', 'POST'])
@admin_or_first_run_required
def sslserver():
    form = SSLHostForm()
    if not form.is_submitted():
        use_ssl = Setting.get_by_name('use_ssl').value
        if use_ssl is not None:
            form.ssl.data = use_ssl

        config_path = Setting.get_by_name('ser2sock_config_path').value
        if config_path:
            form.config_path.data = config_path

        device_address = Setting.get_by_name('device_address').value
        if device_address:
            form.device_address.data = device_address

        device_port = Setting.get_by_name('device_port').value
        if device_port:
            form.device_port.data = device_port

    if form.validate_on_submit():
        manage_ser2sock = Setting.get_by_name('manage_ser2sock')
        use_ssl = Setting.get_by_name('use_ssl')
        config_path = Setting.get_by_name('ser2sock_config_path')
        device_address = Setting.get_by_name('device_address')
        device_port = Setting.get_by_name('device_port')
        device_location = Setting.get_by_name('device_location')

        manage_ser2sock.value = True
        use_ssl.value = form.ssl.data
        config_path.value = form.config_path.data
        device_address.value = form.device_address.data
        device_port.value = form.device_port.data
        device_location.value = 'network'

        db.session.add(manage_ser2sock)
        db.session.add(use_ssl)
        db.session.add(config_path)
        db.session.add(device_address)
        db.session.add(device_port)
        db.session.add(device_location)

        next_stage = 'setup.device'
        set_stage(SETUP_ENDPOINT_STAGE[next_stage])
        db.session.commit()

        try:
            if form.ssl.data == True:
                _generate_certs()

            ca = Certificate.query.filter_by(type=CA).first()
            server_cert = Certificate.query.filter_by(type=SERVER).first()

            config_settings = {
                'device_path': Setting.get_by_name('device_path').value,
                'device_port': device_port.value,
                'device_baudrate': Setting.get_by_name('device_baudrate').value,
                'device_port': device_port.value,
                'raw_device_mode': 1,
                'use_ssl': use_ssl.value,
                'ca_cert': ca,
                'server_cert': server_cert
            }

            db.session.commit()
            ser2sock.update_config(config_path.value, **config_settings)
            db.session.commit()

        except RuntimeError, err:
            flash("{0}".format(err), 'error')

        except ser2sock.HupFailed, err:
            flash("We had an issue restarting ser2sock: {0}".format(err), 'error')

        except ser2sock.NotFound, err:
            flash("We weren't able to find ser2sock on your system.", 'error')            

        except Exception, err:
            flash("Unexpected Error: {0}".format(err), 'error')

        else:
            return redirect(url_for(next_stage))

    return render_template('setup/ssl.html', form=form)

def _generate_certs():
    if Certificate.query.filter_by(type=CA).first() is None:
        ca_cert = Certificate(
                    name="AlarmDecoder CA",
                    description='CA certificate used for authenticating others.',
                    status=CERT_ACTIVE,
                    type=CA)
        ca_cert.generate(common_name='AlarmDecoder CA')
        db.session.add(ca_cert)
        db.session.commit()

        server_cert = Certificate(
                name="AlarmDecoder Server",
                description='Server certificate used by ser2sock.',
                status=CERT_ACTIVE,
                type=SERVER,
                ca_id=ca_cert.id)
        server_cert.generate(common_name='AlarmDecoder Server', parent=ca_cert)
        db.session.add(server_cert)

        internal_cert = Certificate(
                name="AlarmDecoder Internal",
                description='Internal certificate used to communicate with ser2sock.',
                status=CERT_ACTIVE,
                type=INTERNAL,
                ca_id=ca_cert.id)
        internal_cert.generate(common_name='AlarmDecoder Internal', parent=ca_cert)
        db.session.add(internal_cert)
        db.session.commit()

@setup.route('/test', methods=['GET', 'POST'])
@admin_or_first_run_required
def test():
    form = TestDeviceForm()

    if not form.is_submitted():
        set_stage(SETUP_TEST)
        db.session.commit()
    else:
        setup_complete = Setting.get_by_name('setup_complete', default=False)

        next_stage = 'setup.account'
        if setup_complete.value:
            next_stage = 'frontend.index'
            flash('Setup complete!', 'success')

        set_stage(SETUP_ENDPOINT_STAGE[next_stage])
        db.session.commit()

        return redirect(url_for(next_stage))

    return render_template('setup/test.html', form=form)

@setup.route('/account', methods=['GET', 'POST'])
@admin_or_first_run_required
def account():
    form = CreateAccountForm()

    if form.validate_on_submit():
        user = User(role_code=USER_ADMIN, status_code=USER_ACTIVE)
        form.populate_obj(user)
        db.session.add(user)

        setup_complete = Setting.get_by_name('setup_complete', default=False)
        setup_complete.value = True
        db.session.add(setup_complete)

        next_stage = 'frontend.index'
        set_stage(SETUP_ENDPOINT_STAGE[next_stage])
        db.session.commit()

        flash('Setup complete!', 'success')

        return redirect(url_for(next_stage))

    return render_template('setup/account.html', form=form)

@setup.route('/device', methods=['GET', 'POST'])
@admin_or_first_run_required
def device():
    form = DeviceForm()
    if not form.is_submitted():
        if current_app.decoder.device is not None:
            form.panel_mode.data = current_app.decoder.device.mode
            form.keypad_address.data = current_app.decoder.device.address
            form.address_mask.data = '{0:x}'.format(current_app.decoder.device.address_mask)
            form.internal_address_mask.data = '{0:x}'.format(current_app.decoder.internal_address_mask)
            form.lrr_enabled.data = current_app.decoder.device.emulate_lrr
            form.deduplicate.data = current_app.decoder.device.deduplicate
            form.zone_expanders.data = [str(idx + 1) if value == True else None for idx, value in enumerate(current_app.decoder.device.emulate_zone)]
            form.relay_expanders.data = [str(idx + 1) if value == True else None for idx, value in enumerate(current_app.decoder.device.emulate_relay)]
        else:
            panel_mode = Setting.get_by_name('panel_mode').value
            if panel_mode is not None:
                form.panel_mode.data = panel_mode

            keypad_address = Setting.get_by_name('keypad_address').value
            if keypad_address:
                form.keypad_address.data = keypad_address

            address_mask = Setting.get_by_name('address_mask').value
            if address_mask is not None:
                form.address_mask.data = address_mask

            internal_address_mask = Setting.get_by_name('internal_address_mask').value
            if internal_address_mask is not None:
                form.internal_address_mask.data = internal_address_mask

            lrr_enabled = Setting.get_by_name('lrr_enabled').value
            if lrr_enabled is not None:
                form.lrr_enabled.data = lrr_enabled

            zone_expanders = Setting.get_by_name('emulate_zone_expanders').value
            if zone_expanders is not None:
                form.zone_expanders.data = [str(idx + 1) if value == True else None for idx, value in enumerate([v == 'True' for v in zone_expanders.split(',')])]

            relay_expanders = Setting.get_by_name('emulate_relay_expanders').value
            if relay_expanders is not None:
                form.relay_expanders.data = [str(idx + 1) if value == True else None for idx, value in enumerate([v == 'True' for v in relay_expanders.split(',')])]

            deduplicate = Setting.get_by_name('deduplicate').value
            if deduplicate is not None:
                form.deduplicate.data = deduplicate

    else:
        if form.validate_on_submit():
            panel_mode = Setting.get_by_name('panel_mode')
            keypad_address = Setting.get_by_name('keypad_address')
            address_mask = Setting.get_by_name('address_mask')
            internal_address_mask = Setting.get_by_name('internal_address_mask')
            lrr_enabled = Setting.get_by_name('lrr_enabled')
            zone_expanders = Setting.get_by_name('emulate_zone_expanders')
            relay_expanders = Setting.get_by_name('emulate_relay_expanders')
            deduplicate = Setting.get_by_name('deduplicate')

            zx = [True if str(x) in form.zone_expanders.data else False for x in xrange(1, 6)]
            rx = [True if str(x) in form.relay_expanders.data else False for x in xrange(1, 5)]

            panel_mode.value = form.panel_mode.data
            keypad_address.value = form.keypad_address.data
            address_mask.value = form.address_mask.data
            internal_address_mask.value = form.internal_address_mask.data
            lrr_enabled.value = form.lrr_enabled.data
            zone_expanders.value = ','.join([str(x) for x in zx])
            relay_expanders.value = ','.join([str(x) for x in rx])
            deduplicate.value = form.deduplicate.data

            set_stage(SETUP_TEST)

            db.session.add(panel_mode)
            db.session.add(keypad_address)
            db.session.add(address_mask)
            db.session.add(internal_address_mask)
            db.session.add(lrr_enabled)
            db.session.add(zone_expanders)
            db.session.add(relay_expanders)
            db.session.add(deduplicate)

            db.session.commit()

            return redirect(url_for('setup.test'))

    return render_template('setup/device.html', form=form)

@setup.route('/complete', methods=['GET'])
def complete():
    return render_template('setup/complete.html')
