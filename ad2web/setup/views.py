# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, abort, g, request, flash, Response, redirect, url_for
from flask import current_app as APP
from flask.ext.login import login_required, current_user

from ..extensions import db
from ..decorators import admin_required
#from .constants import ACTIVE, CLIENT, CA, PACKAGE_TYPE_LOOKUP, CERTIFICATE_TYPES, CERTIFICATE_STATUS
from ..settings.models import Setting
from .forms import (DeviceTypeForm, NetworkDeviceForm, SerialDeviceForm,
                   DeviceLocationForm, SSLForm, SSLHostForm)

setup = Blueprint('setup', __name__, url_prefix='/setup')

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
        # do stuff
        #

        device_type = Setting.get_by_name('device_type')
        device_type.value = form.device_type.data
        db.session.add(device_type)

        setup_stage = Setting.get_by_name('setup_stage')
        setup_stage.value = 'type'
        db.session.add(setup_stage)

        db.session.commit()

        return redirect(url_for('setup.location'))

    return render_template('setup/type.html', form=form)

@setup.route('/location', methods=['GET', 'POST'])
def location():
    form = DeviceLocationForm()
    if form.validate_on_submit():
        # do stuff
        #

        target = form.device_location.data

        setup_stage = Setting.get_by_name('setup_stage')
        setup_stage.value = 'location'
        db.session.add(setup_stage)
        db.session.commit()

        return redirect(url_for('setup.{0}'.format(target)))

    return render_template('setup/location.html', form=form)

@setup.route('/network', methods=['GET', 'POST'])
def network():
    form = NetworkDeviceForm()
    if form.validate_on_submit():
        # do stuff
        #

        device_address = Setting.get_by_name('device_address')
        device_port = Setting.get_by_name('device_port')
        ssl = Setting.get_by_name('use_ssl')

        device_address.value = form.device_address.data
        device_port.value = form.device_port.data
        ssl.value = form.ssl.data

        db.session.add(device_address)
        db.session.add(device_port)
        db.session.add(ssl)

        setup_stage = Setting.get_by_name('setup_stage')
        setup_stage.value = 'network'
        db.session.add(setup_stage)
        db.session.commit()

        return redirect(url_for('setup.test'))

    return render_template('setup/network.html', form=form)

@setup.route('/local', methods=['GET', 'POST'])
def local():
    form = SerialDeviceForm()
    if form.validate_on_submit():
        # do stuff
        #

        device_path = Setting.get_by_name('device_path')
        baudrate = Setting.get_by_name('baudrate')

        device_path.value = form.device_path.data
        baudrate.value = form.baudrate.data

        db.session.add(device_path)
        db.session.add(baudrate)

        setup_stage = Setting.get_by_name('setup_stage')
        setup_stage.value = 'local'
        db.session.add(setup_stage)
        db.session.commit()

        return redirect(url_for('setup.test'))

    return render_template('setup/local.html', form=form)

@setup.route('/test', methods=['GET', 'POST'])
def test():
        # setup_stage = Setting.get_by_name('setup_stage')
        # setup_stage.value = 'type'
        # db.session.add(setup_stage)

    return render_template('setup/test.html', form=None)

@setup.route('/ssl', methods=['GET', 'POST'])
def ssl():
    form = SSLHostForm()
    if form.validate_on_submit():
        # do stuff
        #

        setup_stage = Setting.get_by_name('setup_stage')
        setup_stage.value = 'complete'
        db.session.add(setup_stage)
        db.session.commit()

        return redirect(url_for('keypad.index'))

    return render_template('setup/ssl.html', form=form)
