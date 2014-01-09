# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, abort, g, request, flash, Response
from flask import current_app as APP
from flask.ext.login import login_required, current_user

from ..extensions import db
from ..decorators import admin_required
from .constants import ARM, DISARM, POWER_CHANGED, ALARM, FIRE, BYPASS, BOOT, \
                        CONFIG_RECEIVED, ZONE_FAULT, ZONE_RESTORE, LOW_BATTERY, \
                        PANIC, RELAY_CHANGED, EVENT_TYPES
from .models import EventLogEntry, PanelLogEntry

log = Blueprint('log', __name__, url_prefix='/log')

@log.context_processor
def log_context_processor():
    return {
        'ARM': ARM,
        'DISARM': DISARM,
        'POWER_CHANGED': POWER_CHANGED,
        'ALARM': ALARM,
        'FIRE': FIRE,
        'BYPASS': BYPASS,
        'BOOT': BOOT,
        'CONFIG_RECEIVED': CONFIG_RECEIVED,
        'ZONE_FAULT': ZONE_FAULT,
        'ZONE_RESTORE': ZONE_RESTORE,
        'LOW_BATTERY': LOW_BATTERY,
        'PANIC': PANIC,
        'RELAY_CHANGED': RELAY_CHANGED,
        'TYPES': EVENT_TYPES
    }

@login_required
@admin_required
@log.route('/')
def events():
    event_log = EventLogEntry.query.all()

    return render_template('log/events.html', event_log=event_log, active='events')

@login_required
@admin_required
@log.route('/panel')
def panel():
    panel_log = PanelLogEntry.query.all()

    return render_template('log/panel.html', panel_log=panel_log, active='panel')
