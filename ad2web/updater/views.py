# -*- coding: utf-8 -*-

import os
import json
import urllib
import zipfile

from flask import Blueprint, render_template, abort, g, request, flash, Response, redirect, url_for, jsonify
from flask import current_app as APP
from flask.ext.login import login_required, current_user

from werkzeug import secure_filename

from ..extensions import db
from ..decorators import admin_required

from .forms import UpdateFirmwareForm, UpdateFirmwareJSONForm
from .models import FirmwareUpdater
from .constants import FIRMWARE_JSON_URL

updater = Blueprint('update', __name__, url_prefix='/update')

@updater.context_processor
def keypad_context_processor():
    return { }

@updater.route('/')
@login_required
@admin_required
def index():
    return render_template('updater/index.html', updates=APP.decoder.updates)

@updater.route('/update', methods=['POST'])
@login_required
@admin_required
def update():
    ret = { 'status': 'FAIL' }

    component = request.json.get('component', None)
    if component is not None:
        ret = APP.decoder.updater.update(component)

    return json.dumps(ret);

@updater.route('/restart', methods=['POST'])
@login_required
@admin_required
def restart():
    APP.decoder.trigger_restart = True

    return json.dumps({ 'status': 'PASS' })

@updater.route('/checkavailable', methods=['GET'])
def checkavailable():
    return json.dumps({ 'status': 'PASS' })

@updater.route('/check_for_updates', methods=['GET'])
@login_required
@admin_required
def check_for_updates():
    APP.decoder.updates = APP.decoder.updater.check_updates()
    update_available = not all(not needs_update for component, (needs_update, branch, revision, new_revision, status, project_url) in APP.decoder.updates.iteritems())
    APP.jinja_env.globals['update_available'] = update_available

    return redirect(url_for('update.index'))

@updater.route('/update_firmware', methods=['GET', 'POST'] )
@login_required
@admin_required
def update_firmware():
    current_firmware = APP.decoder.device.version_number
    all_ok = "true"
    form = UpdateFirmwareJSONForm()
    form2 = UpdateFirmwareForm()
    form2.multipart = True
    form.firmware_file_json.choices = []
    data = None
    try:
        response = urllib.urlopen(FIRMWARE_JSON_URL)
    except IOError:
        flash('Cannot connect to alarmdecoder server', 'error')
        all_ok = "false"

    if all_ok is "true":
        data = json.loads(response.read())

        counter = 0
        for firmware in data['firmware']:
            form.firmware_file_json.choices.insert(counter,(firmware['file'], firmware['version']))
            counter = counter + 1

    if form.validate_on_submit():
        file_name = form.firmware_file_json.data
        zip, headers = urllib.urlretrieve(file_name)
        return_data = {}

        with zipfile.ZipFile(zip) as zf:
            files = [name for name in zf.namelist() if name.endswith('.hex')]
            for filename in files:
                file_path = os.path.join('/tmp', secure_filename(filename))
                file_data = zf.open(filename, 'r').read()
                return_data['uploading'] = filename
                if not os.path.isfile(file_path):
                    open(file_path, 'w').write(file_data)

                APP.decoder.firmware_file = file_path
                APP.decoder.firmware_length = len(filter(lambda x: x[0] == ':', file_data) )

            zf.close()
        return jsonify(return_data);

    if form2.is_submitted():
        uploaded_file = request.files.getlist('file')
        return_data = {}
        try:
            file_data = uploaded_file[0].read()
        except IndexError:
            return_data['error'] = "NOFILE"
            return jsonify(return_data)

        return_data['uploading'] =  uploaded_file[0].filename
        file_path = os.path.join('/tmp', secure_filename(uploaded_file[0].filename))
        open(file_path, 'w').write(file_data)

        APP.decoder.firmware_file = file_path
        APP.decoder.firmware_length = len(filter(lambda x: x[0] == ':', file_data) )

        return jsonify(return_data)

    return render_template('updater/firmware_json.html', current_firmware=current_firmware, form=form, form2=form2, firmwarejson=data, all_ok=all_ok);

@updater.route('/firmware', methods=['GET', 'POST'])
@login_required
@admin_required
def firmware():
    form = UpdateFirmwareForm()
    form.multipart = True
    if form.validate_on_submit():
        uploaded_file = request.files[form.firmware_file.name]
        data = uploaded_file.read()
        file_path = os.path.join('/tmp', secure_filename(uploaded_file.filename))
        open(file_path, 'w').write(data)

        APP.decoder.firmware_file = file_path
        APP.decoder.firmware_length = len(filter(lambda x: x[0] == ':', data))

        return render_template('updater/firmware_upload.html')

    return render_template('updater/firmware.html', form=form)
