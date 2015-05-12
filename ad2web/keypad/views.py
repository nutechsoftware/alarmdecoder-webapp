# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, abort, g, request, flash, Response, url_for, Markup, redirect
from flask import current_app as APP
from flask.ext.login import login_required, current_user

from ..extensions import db
from ..decorators import admin_required
from ..user import User
from ..settings.models import Setting
from alarmdecoder.panels import ADEMCO, DSC
from .forms import KeypadButtonForm
from .models import KeypadButton
from ..cameras import Camera

keypad = Blueprint('keypad', __name__, url_prefix='/keypad')

@keypad.route('/')
@login_required
def index():
    panel_mode = Setting.get_by_name('panel_mode').value
    custom_buttons = KeypadButton.query.filter_by(user_id=current_user.id).all()

    if panel_mode is None:
        return render_template('keypad/index.html', buttons=custom_buttons)

    if panel_mode == DSC:
        return render_template('keypad/dsc.html', buttons=custom_buttons)
    else:
        return render_template('keypad/index.html', buttons=custom_buttons)

@keypad.route('/button_index')
@login_required
def custom_index():
    buttons = KeypadButton.query.filter_by(user_id=current_user.id).all()
    use_ssl = Setting.get_by_name('use_ssl', default=False).value

    return render_template('keypad/custom_button_index.html', buttons=buttons, active="keypad", ssl=use_ssl)

@keypad.route('/create_button', methods=['GET', 'POST'])
@login_required
def create_button():
    form = KeypadButtonForm()

    if form.validate_on_submit():
        button = KeypadButton()
        form.populate_obj(button)
        button.user_id = current_user.id
        
        db.session.add(button)
        db.session.commit()

        flash('Keypad Button Created', 'success')
        return redirect(url_for('keypad.custom_index'))

    use_ssl = Setting.get_by_name('use_ssl', default=False).value
    return render_template('keypad/create.html', form=form, active="keypad", ssl=use_ssl)

@keypad.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_button(id):
    button = KeypadButton.query.filter_by(button_id=id).first_or_404()
    form = KeypadButtonForm(obj=button)

    if form.validate_on_submit():
        form.populate_obj(button)
        button.user_id = current_user.id

        db.session.add(button)
        db.session.commit()

        flash('Keypad Button Updated', 'success')

    use_ssl = Setting.get_by_name('use_ssl', default=False).value
    return render_template('keypad/edit.html', form=form, id=id, active="keypad", ssl=use_ssl)


@keypad.route('/remove/<int:id>', methods=['GET', 'POST'])
@login_required
def remove_button(id):
    button = KeypadButton.query.filter_by(button_id=id).first_or_404()
    db.session.delete(button)
    db.session.commit();

    flash('Keypad Button deleted', 'success')
    return redirect(url_for('keypad.custom_index'))
