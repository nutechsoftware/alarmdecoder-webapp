# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, abort, g, request, flash, Response, url_for, Markup
from flask import current_app as APP
from flask.ext.login import login_required, current_user

from ..extensions import db
from ..decorators import admin_required
#from .constants import ACTIVE, CLIENT, CA, PACKAGE_TYPE_LOOKUP, CERTIFICATE_TYPES, CERTIFICATE_STATUS

keypad = Blueprint('keypad', __name__, url_prefix='/keypad')

@keypad.context_processor
def keypad_context_processor():
    return {

    }

@keypad.route('/')
@login_required
def index():
    if current_user.is_admin():
        if len(APP.decoder.updates):
            flash(Markup('There is a <a href="{0}">software update</a> available.'.format(url_for('update.index'))), 'warning')

    return render_template('keypad/index.html')
