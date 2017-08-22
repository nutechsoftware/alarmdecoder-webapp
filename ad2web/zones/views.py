# -*- coding: utf-8 -*-

from datetime import datetime

from flask import Blueprint, render_template, current_app, request, flash, redirect, url_for, jsonify
from flask.ext.login import login_required, current_user

from ..extensions import db
from ..user import User
from ..utils import allowed_file, make_dir
from ..decorators import admin_required
from ..settings import Setting
from .forms import ZoneForm
from .models import Zone
import pprint

zones = Blueprint('zones', __name__, url_prefix='/settings/zones')

@zones.route('/')
@login_required
@admin_required
def index():
    zones = Zone.query.all()
    panel_mode = Setting.get_by_name('panel_mode').value

    use_ssl = Setting.get_by_name('use_ssl', default=False).value

    return render_template('zones/index.html', zones=zones, active="zones", ssl=use_ssl, panel_mode=panel_mode)

@zones.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    form = ZoneForm()

    if form.validate_on_submit():
        zone = Zone()
        form.populate_obj(zone)

        db.session.add(zone)
        db.session.commit()

        flash('Zone created.', 'success')

        return redirect(url_for('zones.index'))

    use_ssl = Setting.get_by_name('use_ssl', default=False).value

    return render_template('zones/create.html', form=form, active="zones", ssl=use_ssl)

@zones.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    zone = Zone.query.filter_by(zone_id=id).first_or_404()
    form = ZoneForm(obj=zone)

    if form.validate_on_submit():
        form.populate_obj(zone)

        db.session.add(zone)
        db.session.commit()

        flash('Zone updated.', 'success')

    use_ssl = Setting.get_by_name('use_ssl', default=False).value

    return render_template('zones/edit.html', form=form, id=id, active="zones", ssl=use_ssl)

@zones.route('/remove/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def remove(id):
    zone = Zone.query.filter_by(zone_id=id).first_or_404()
    db.session.delete(zone)
    db.session.commit();
    
    flash('Zone deleted.', 'success')

    return redirect(url_for('zones.index'))

@zones.route('/import', methods=['GET', 'POST'])
@login_required
@admin_required
def import_zone():
    data = request.get_json()
    numZones = 0
    zones = {}
    
    if len(data) == 0:
        return jsonify(success="Failure to enumerate zones, possibly unsupported")

    delete_all_zones()

    for d in data:
        address = d['address']
        name = d['zone_name']
        description = d['zone_name'] if d['zone_name'] != '' else 'Generated - No Alpha Found'

        if not zone_exists_in_db(address):
            zone = Zone()

            zone.zone_id = address
            zone.name = name
            zone.description = description

            db.session.add(zone)
            z = { 'zone_id': address, 'name': name, 'description': description }
            zones[address] = z
            numZones = numZones + 1

    if numZones > 0:
        db.session.commit()

    if numZones == 0:
        return jsonify(success=numZones)

    return jsonify(success=zones)

def zone_exists_in_db(id):
    zone = Zone.query.filter_by(zone_id=id).first()

    if zone:
        return True

    return False

def delete_all_zones():
    try:
        db.session.query(Zone).delete()
        db.session.commit()
    except:
        db.session.rollback()
