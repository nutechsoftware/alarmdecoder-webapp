# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, abort, g, request, flash, Response
from flask import current_app as APP
from flask.ext.login import login_required, current_user

from ..extensions import db
from ..decorators import admin_required
from .constants import ARM, DISARM, POWER_CHANGED, ALARM, FIRE, BYPASS, BOOT, \
                        CONFIG_RECEIVED, ZONE_FAULT, ZONE_RESTORE, LOW_BATTERY, \
                        PANIC, RELAY_CHANGED, EVENT_TYPES
from .models import EventLogEntry

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

@log.route('/')
@login_required
def events():
    event_log = EventLogEntry.query.order_by(EventLogEntry.timestamp.desc()).all()

    return render_template('log/events.html', event_log=event_log, active='events')

@log.route('/live')
@login_required
@admin_required
def live():
    return render_template('log/live.html', active='live')
