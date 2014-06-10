# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, abort, g, request, flash, Response, url_for, Markup
from flask import current_app as APP
from flask.ext.login import login_required, current_user

from ..extensions import db
from ..decorators import admin_required
from ..settings.models import Setting
from alarmdecoder.panels import ADEMCO, DSC

keypad = Blueprint('keypad', __name__, url_prefix='/keypad')

@keypad.route('/')
@login_required
def index():
    if current_user.is_admin():
        if not all(not needs_update for component, (needs_update, branch, revision, new_revision, status) in APP.decoder.updates.iteritems()):
            flash(Markup('There is a <a href="{0}">software update</a> available.'.format(url_for('update.index'))), 'warning')

    panel_mode = Setting.get_by_name('panel_mode').value

    if panel_mode is None:
        return render_template('keypad/index.html')

    if panel_mode == DSC:
        return render_template('keypad/dsc.html')
    else:
        return render_template('keypad/index.html')
