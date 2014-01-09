# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, abort, g, request, flash, Response
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

@login_required
@keypad.route('/')
def index():
    return render_template('keypad/index.html')
