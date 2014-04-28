# -*- coding: utf-8 -*-

import json

from flask import Blueprint, render_template, abort, g, request, flash, Response
from flask import current_app as APP
from flask.ext.login import login_required, current_user

from ..extensions import db
from ..decorators import admin_required

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