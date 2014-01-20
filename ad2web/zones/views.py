# -*- coding: utf-8 -*-

from datetime import datetime

from flask import Blueprint, render_template, current_app, request, flash, redirect, url_for
from flask.ext.login import login_required, current_user

from ..extensions import db
from ..user import User
from ..utils import allowed_file, make_dir
from ..decorators import admin_required
from ..settings import Setting
from .forms import ZoneForm
from .models import Zone

zones = Blueprint('zones', __name__, url_prefix='/zones')

@zones.route('/')
@login_required
@admin_required
def index():
    zones = Zone.query.all()

    return render_template('zones/index.html', zones=zones, active="zones")

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

        return redirect(url_for('zones.edit', id=zone.zone_id))

    return render_template('zones/create.html', form=form, active="zones")

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

    return render_template('zones/edit.html', form=form, id=id, active="zones")
