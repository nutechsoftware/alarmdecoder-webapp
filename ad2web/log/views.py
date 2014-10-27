# -*- coding: utf-8 -*-

import os

from flask import Blueprint, render_template, abort, g, request, flash, Response, url_for, redirect
from flask import current_app as APP
from flask.ext.login import login_required, current_user

from ..extensions import db
from ..decorators import admin_required
from .constants import ARM, DISARM, POWER_CHANGED, ALARM, FIRE, BYPASS, BOOT, \
                        CONFIG_RECEIVED, ZONE_FAULT, ZONE_RESTORE, LOW_BATTERY, \
                        PANIC, RELAY_CHANGED, EVENT_TYPES
from .models import EventLogEntry
from ..logwatch import LogWatcher
from ..utils import INSTANCE_FOLDER_PATH

import json
import collections

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
#    event_log = None #EventLogEntry.query.order_by(EventLogEntry.timestamp.desc()).limit(50)

    return render_template('log/events.html', active="events")

@log.route('/live')
@login_required
@admin_required
def live():
    return render_template('log/live.html', active='live')

@log.route('/delete')
@login_required
@admin_required
def delete():
    events = EventLogEntry.query.delete()
    db.session.commit()
    return redirect(url_for('log.events'))

@log.route('/alarmdecoder')
@login_required
@admin_required
def alarmdecoder_logfile():
    return render_template('log/alarmdecoder.html', active='AlarmDecoder')

@log.route('/alarmdecoder/get_data/<int:lines>', methods=['GET'])
@login_required
@admin_required
def get_log_data(lines):
    log_file = os.path.join(INSTANCE_FOLDER_PATH, 'logs', 'info.log')

    try:
        log_text = LogWatcher.tail(log_file, lines)
    except IOError, err:
        return json.dumps([str(err)])

    return json.dumps(log_text)

#XHR for retrieving event log data server side
@log.route('/retrieve_events_paging_data')
@login_required
def get_events_paging_data():

    #get results from datatable via XHR
    results = DataTablesServer(request).output_result()

    return json.dumps(results)

class DataTablesServer:
    def __init__( self, request ):
        #values specified by datatable for filtering, sorting, paging etc
        self.request_values = request.values
        self.result_data = None

        #total in table unfiltered
        self.cardinality = 0
        #total in table after filter
        self.cardinality_filtered = 0
        
        self.run_queries()

    def output_result(self):
        output = {}
        output['sEcho'] = str(int(self.request_values['sEcho']))
        output['iTotalRecords'] = int(self.cardinality);
        output['iTotalDisplayRecords'] = int(self.cardinality);

        aaData_rows = []

        #iterate the result and append data rows
        for row in self.result_data:
            aaData_row = []
            aaData_row.append(str(row.timestamp))
            aaData_row.append(EVENT_TYPES[row.type])
            aaData_row.append(row.message)

            aaData_rows.append(aaData_row)

        output['aaData'] = aaData_rows
        return output

    def run_queries(self):
        pages = self.paging()
        filter = self.filtering()

        #page to start on
        start = 0
        #number of records to return
        limit = 10

        #non-default values chosen from the UI
        if pages.start is not None:
            start = pages.start
        if pages.length is not None:
            limit = pages.length

        #if filtered, cardinality based off filter, otherwise all rows
        if filter is not None:
            self.result_data = EventLogEntry.query.filter(EventLogEntry.message.like('%' + filter + '%')).order_by(EventLogEntry.timestamp.desc()).limit(limit).offset(start)
            self.cardinality_filtered = self.result_data.count()
            self.cardinality = EventLogEntry.query.filter(EventLogEntry.message.like('%' + filter + '%')).count()
        else:
            self.result_data = EventLogEntry.query.order_by(EventLogEntry.timestamp.desc()).limit(limit).offset(start)
            self.cardinality_filtered = self.result_data.count()
            self.cardinality = EventLogEntry.query.order_by(EventLogEntry.timestamp.desc()).count()

    #here we determine the filter value for the search box and apply to the queries
    def filtering(self):
        filter = None
        if( self.request_values.has_key('sSearch')) and (self.request_values['sSearch'] != "" ):
            filter = self.request_values['sSearch']

        return filter

    #determine what page we're on, as well as how many to show per page
    def paging(self):
        pages = collections.namedtuple('pages', ['start', 'length'])
        if( self.request_values['iDisplayStart'] != "" ) and (self.request_values['iDisplayLength'] != -1 ):
            pages.start = int(self.request_values['iDisplayStart'])
            pages.length = int(self.request_values['iDisplayLength'])

        return pages;
