# -*- coding: utf-8 -*-

import os

from flask import Blueprint, render_template, abort, g, request, flash, Response, redirect, url_for
from flask import current_app
from flask.ext.login import login_required, current_user

from ..extensions import db
from ..decorators import admin_required
from ..settings.models import Setting
from ..certificate.models import Certificate
from ..certificate.constants import CA, SERVER, CLIENT, INTERNAL, ACTIVE
from .forms import (DeviceTypeForm, NetworkDeviceForm, LocalDeviceForm,
                   SSLForm, SSLHostForm, DeviceForm, TestDeviceForm)
from .constants import (STAGES, SETUP_TYPE, SETUP_LOCATION, SETUP_NETWORK,
                    SETUP_LOCAL, SETUP_DEVICE, SETUP_COMPLETE, BAUDRATES,
                    DEFAULT_BAUDRATES)
from ..ser2sock import ser2sock

setup = Blueprint('setup', __name__, url_prefix='/setup')

def set_stage(stage):
    setup_stage = Setting.get_by_name('setup_stage')
    setup_stage.value = stage
    db.session.add(setup_stage)

@setup.context_processor
def setup_context_processor():
    return { }

@setup.route('/')
def index():
    return render_template('setup/index.html')

@setup.route('/type', methods=['GET', 'POST'])
def type():
    form = DeviceTypeForm()
    if form.validate_on_submit():
        device_type = Setting.get_by_name('device_type')
        device_type.value = form.device_type.data
        db.session.add(device_type)

        device_location = Setting.get_by_name('device_location')
        device_location.value = form.device_location.data
        db.session.add(device_location)

        set_stage(SETUP_TYPE)

        db.session.commit()

        return redirect(url_for('setup.{0}'.format(device_location.value)))

    return render_template('setup/type.html', form=form)

@setup.route('/local', methods=['GET', 'POST'])
def local():
    form = LocalDeviceForm()
    if not form.is_submitted():
        form.baudrate.data = DEFAULT_BAUDRATES[Setting.get_by_name('device_type').value]

    if form.validate_on_submit():
        device_path = Setting.get_by_name('device_path')
        baudrate = Setting.get_by_name('device_baudrate')

        device_path.value = form.device_path.data
        baudrate.value = form.baudrate.data

        db.session.add(device_path)
        db.session.add(baudrate)

        set_stage(SETUP_LOCAL)
        db.session.commit()

        return redirect(url_for('setup.test'))

    return render_template('setup/local.html', form=form)

@setup.route('/network', methods=['GET', 'POST'])
def network():
    form = NetworkDeviceForm()
    if form.validate_on_submit():
        device_address = Setting.get_by_name('device_address')
        device_port = Setting.get_by_name('device_port')
        ssl = Setting.get_by_name('use_ssl')
        local = Setting.get_by_name('local_ser2sock')

        device_address.value = form.device_address.data
        device_port.value = form.device_port.data
        ssl.value = form.ssl.data
        local.value = form.local.data

        db.session.add(device_address)
        db.session.add(device_port)
        db.session.add(ssl)
        db.session.add(local)

        set_stage(SETUP_NETWORK)
        db.session.commit()

        if form.local.data == True:
            return redirect(url_for('setup.sslserver'))
        else:
            if form.ssl.data == True:
                return redirect(url_for('setup.sslclient'))
            else:
                return redirect(url_for('setup.test'))

    return render_template('setup/network.html', form=form)

@setup.route('/sslclient', methods=['GET', 'POST'])
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
        db.session.commit()

        return redirect(url_for('setup.test'))

    return render_template('setup/sslclient.html', form=form)

@setup.route('/sslserver', methods=['GET', 'POST'])
def sslserver():
    form = SSLHostForm()
    if form.validate_on_submit():
        if form.confirm_management.data == True:
            ca_cert = Certificate(
                        name="AlarmDecoder CA",
                        description='CA certificate used for authenticating others.',
                        status=ACTIVE,
                        type=CA)
            ca_cert.generate(common_name='AlarmDecoder CA')
            db.session.add(ca_cert)

            server_cert = Certificate(
                    name="AlarmDecoder Server",
                    description='Server certificate used by ser2sock.',
                    status=ACTIVE,
                    type=SERVER)
            server_cert.generate(common_name='AlarmDecoder Server', parent=ca_cert)
            db.session.add(server_cert)

            internal_cert = Certificate(
                    name="AlarmDecoder Internal",
                    description='Internal certificate used to communicate with ser2sock.',
                    status=ACTIVE,
                    type=INTERNAL)
            internal_cert.generate(common_name='AlarmDecoder Internal', parent=ca_cert)
            db.session.add(internal_cert)

            use_ssl = Setting.get_by_name('use_ssl')
            use_ssl.value = True
            db.session.add(use_ssl)

            config_path = Setting.get_by_name('ser2sock_config_path')
            config_path.value = form.config_path.data
            db.session.add(config_path)

            manage_ser2sock = Setting.get_by_name('manage_ser2sock')
            manage_ser2sock.value = True
            db.session.add(manage_ser2sock)

            db.session.commit()

            _update_ser2sock_config(config_path.value)

        return redirect(url_for('setup.test'))

    return render_template('setup/ssl.html', form=form)

def _update_ser2sock_config(path):
    config = ser2sock.read_config(os.path.join(path, 'ser2sock.conf'))

    config_values = {}
    for k, v in config.items('ser2sock'):
        config_values[k] = v

    config_values['device'] = Setting.get_by_name('device_path').value
    config_values['baudrate'] = Setting.get_by_name('device_baudrate').value
    config_values['port'] = Setting.get_by_name('device_port').value
    config_values['encrypted'] = Setting.get_by_name('use_ssl').value
    if config_values['encrypted'] == 1:
        ca = Certificate.query.filter_by(type=CA).first()
        server_cert = Certificate.query.filter_by(type=SERVER).first()

        ca.export(os.path.join(path, 'certs'))
        server_cert.export(os.path.join(path, 'certs'))

        config_values['ca_certificate'] = os.path.join(path, 'certs', '{0}.pem'.format(ca.name))
        config_values['ssl_certificate'] = os.path.join(path, 'certs', '{0}.pem'.format(server_cert.name))
        config_values['ssl_key'] = os.path.join(path, 'certs', '{0}.key'.format(server_cert.name))

    ser2sock.save_config(os.path.join(path, 'ser2sock.conf'), config_values)
    ser2sock.save_certificate_index(path)
    ser2sock.save_revocation_list(path)
    ser2sock.hup()

@setup.route('/test', methods=['GET', 'POST'])
def test():
    form = TestDeviceForm()

    if not form.is_submitted():
        set_stage(SETUP_DEVICE)
        db.session.commit()
    else:
        return redirect(url_for('setup.device'))

    return render_template('setup/test.html', form=form)

@setup.route('/device', methods=['GET', 'POST'])
def device():
    form = DeviceForm()
    if not form.is_submitted():
        form.device_address.data = current_app.decoder.device.address
        form.address_mask.data = '{0:x}'.format(current_app.decoder.device.address_mask)
        form.lrr_enabled.data = current_app.decoder.device.emulate_lrr
        form.deduplicate.data = current_app.decoder.device.deduplicate
        form.zone_expanders.data = [str(idx + 1) if value == True else None for idx, value in enumerate(current_app.decoder.device.emulate_zone)]
        form.relay_expanders.data = [str(idx + 1) if value == True else None for idx, value in enumerate(current_app.decoder.device.emulate_relay)]
    else:
        if form.validate_on_submit():
            device_address = Setting.get_by_name('device_address')
            address_mask = Setting.get_by_name('address_mask')
            lrr_enabled = Setting.get_by_name('lrr_enabled')
            zone_expanders = Setting.get_by_name('emulate_zone_expanders')
            relay_expanders = Setting.get_by_name('emulate_relay_expanders')
            deduplicate = Setting.get_by_name('deduplicate')

            zx = [True if str(x) in form.zone_expanders.data else False for x in xrange(1, 6)]
            rx = [True if str(x) in form.relay_expanders.data else False for x in xrange(1, 5)]

            device_address.value = form.device_address.data
            address_mask.value = form.address_mask.data
            lrr_enabled.value = form.lrr_enabled.data
            zone_expanders.value = ','.join([str(x) for x in zx])
            relay_expanders.value = ','.join([str(x) for x in rx])
            deduplicate.value = form.deduplicate.data

            db.session.add(device_address)
            db.session.add(address_mask)
            db.session.add(lrr_enabled)
            db.session.add(zone_expanders)
            db.session.add(relay_expanders)
            db.session.add(deduplicate)

            current_app.decoder.device.address = device_address.value
            current_app.decoder.device.address_mask = int(address_mask.value, 16)
            current_app.decoder.device.emulate_zone = zx
            current_app.decoder.device.emulate_relay = rx
            current_app.decoder.device.emulate_lrr = lrr_enabled.value
            current_app.decoder.device.deduplicate = deduplicate.value
            current_app.decoder.device.save_config()

            set_stage(SETUP_COMPLETE)
            db.session.commit()

            flash('Setup complete!', 'success')
            return redirect(url_for('setup.complete'))

    return render_template('setup/device.html', form=form)

@setup.route('/complete', methods=['GET'])
def complete():
    return render_template('setup/complete.html')