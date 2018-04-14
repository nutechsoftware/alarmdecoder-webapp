# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, abort, g, request, flash, Response, url_for, Markup, redirect
from flask import current_app as APP
from flask.ext.login import login_required, current_user

from ..extensions import db
from ..decorators import admin_required
from ..user import User
from ..settings.models import Setting
from alarmdecoder.panels import ADEMCO, DSC
from alarmdecoder import AlarmDecoder
from .forms import KeypadButtonForm
from .models import KeypadButton
from ..cameras import Camera
from .forms import SpecialButtonFormAdemco, SpecialButtonFormDSC
from .constants import FIRE, MEDICAL, POLICE, SPECIAL_4, SPECIAL_CUSTOM, STAY, AWAY, CHIME, RESET, EXIT, SPECIAL_KEY_MAP

keypad = Blueprint('keypad', __name__, url_prefix='/keypad')

@keypad.route('/')
@login_required
def index():
    panel_mode = Setting.get_by_name('panel_mode').value
    custom_buttons = KeypadButton.query.filter_by(user_id=current_user.id).all()
    special_buttons = get_special_buttons()

    if panel_mode is None:
        return render_template('keypad/index.html', buttons=custom_buttons,special_buttons=special_buttons)

    if panel_mode == DSC:
        return render_template('keypad/dsc.html', buttons=custom_buttons,special_buttons=special_buttons)
    else:
        return render_template('keypad/index.html', buttons=custom_buttons,special_buttons=special_buttons)

def get_special_buttons():
    special_buttons = {}
    panel_mode = Setting.get_by_name('panel_mode').value

    special_1 = get_special_setting('special_1',FIRE)
    special_1_key = get_special_setting('special_1_key', SPECIAL_KEY_MAP[FIRE])
    
    special_2 = get_special_setting('special_2', POLICE)
    special_2_key = get_special_setting('special_2_key', SPECIAL_KEY_MAP[POLICE])

    special_3 = get_special_setting('special_3', MEDICAL)
    special_3_key = get_special_setting('special_3_key', SPECIAL_KEY_MAP[MEDICAL])


    special_buttons['special_1'] = special_1
    special_buttons['special_1_key'] = special_1_key
    special_buttons['special_2'] = special_2
    special_buttons['special_2_key'] = special_2_key
    special_buttons['special_3'] = special_3
    special_buttons['special_3_key'] = special_3_key

    if panel_mode == ADEMCO:
        special_4 = get_special_setting('special_4', SPECIAL_4)
        special_4_key = get_special_setting('special_4_key', SPECIAL_KEY_MAP[SPECIAL_4])
        special_buttons['special_4'] = special_4
        special_buttons['special_4_key'] = special_4_key
    else:
        special_4 = get_special_setting('special_4', STAY)
        special_4_key = get_special_setting('special_4_key', SPECIAL_KEY_MAP[STAY])

        special_5 = get_special_setting('special_5',AWAY)
        special_5_key = get_special_setting('special_5_key', SPECIAL_KEY_MAP[AWAY])

        special_6 = get_special_setting('special_6',CHIME)
        special_6_key = get_special_setting('special_6_key', SPECIAL_KEY_MAP[CHIME] )

        special_7 = get_special_setting('special_7',RESET)
        special_7_key = get_special_setting('special_7_key', SPECIAL_KEY_MAP[RESET] )

        special_8 = get_special_setting('special_8',EXIT)
        special_8_key = get_special_setting('special_8_key', SPECIAL_KEY_MAP[EXIT])

        special_buttons['special_4'] = special_4
        special_buttons['special_4_key'] = special_4_key
        special_buttons['special_5'] = special_5
        special_buttons['special_5_key'] = special_5_key
        special_buttons['special_6'] = special_6
        special_buttons['special_6_key'] = special_6_key
        special_buttons['special_7'] = special_7
        special_buttons['special_7_key'] = special_7_key
        special_buttons['special_8'] = special_8
        special_buttons['special_8_key'] = special_8_key

    return special_buttons

def interpret_key(button_data):
    five = chr(5) + chr(5) + chr(5)
    six = chr(6) + chr(6) + chr(6)
    seven = chr(7) + chr(7) + chr(7)
    eight = chr(8) + chr(8) + chr(8)

    if button_data == "<S1>" or button_data == AlarmDecoder.KEY_F1:
        return AlarmDecoder.KEY_F1
    if button_data == "<S2>" or button_data == AlarmDecoder.KEY_F2:
        return AlarmDecoder.KEY_F2
    if button_data == "<S3>" or button_data == AlarmDecoder.KEY_F3:
        return AlarmDecoder.KEY_F3
    if button_data == "<S4>" or button_data == AlarmDecoder.KEY_F4:
        return AlarmDecoder.KEY_F4
    if button_data == "<S5>" or button_data == five:
        return five
    if button_data == "<S6>" or button_data == six:
        return six
    if button_data == "<S7>" or button_data == seven:
        return seven
    if button_data == "<S8>" or button_data == eight:
        return eight

    return button_data

@keypad.route('/legacy')
@login_required
def responsive():
    panel_mode = Setting.get_by_name('panel_mode').value

    custom_buttons = KeypadButton.query.filter_by(user_id=current_user.id).all()

    if panel_mode is None:
        return render_template('keypad/index_legacy.html', buttons=custom_buttons)

    if panel_mode == DSC:
        return render_template('keypad/dsc_legacy.html', buttons=custom_buttons)
    else:
        return render_template('keypad/index_legacy.html', buttons=custom_buttons)

@keypad.route('/button_index')
@login_required
def custom_index():
    buttons = KeypadButton.query.filter_by(user_id=current_user.id).all()
    use_ssl = Setting.get_by_name('use_ssl', default=False).value

    return render_template('keypad/custom_button_index.html', buttons=buttons, active="keypad", ssl=use_ssl)

@keypad.route('/specials', methods=['GET', 'POST'])
@login_required
def special_buttons():
    panel_mode = Setting.get_by_name('panel_mode').value

    form = None

    if panel_mode == DSC:
        form = SpecialButtonFormDSC()
    else:
        form = SpecialButtonFormAdemco()

    if not form.is_submitted():
        buttons = get_special_buttons()

        form.special_1.data = buttons['special_1']
        form.special_1_key.data = buttons['special_1_key']

        form.special_2.data = buttons['special_2']
        form.special_2_key.data = buttons['special_2_key']

        form.special_3.data = buttons['special_3']
        form.special_3_key.data = buttons['special_3_key']

        form.special_4.data = buttons['special_4']
        form.special_4_key.data = buttons['special_4_key']

        if panel_mode == DSC:
            form.special_5.data = buttons['special_5']
            form.special_5_key.data = buttons['special_5_key']

            form.special_6.data = buttons['special_6']
            form.special_6_key.data = buttons['special_6_key']

            form.special_7.data = buttons['special_7']
            form.special_7_key.data = buttons['special_7_key']

            form.special_8.data = buttons['special_8']
            form.special_8_key.data = buttons['special_8_key']
            
    if form.validate_on_submit():

        special_1 = create_special_setting('special_1', form.special_1.data )
        special_1_key = create_special_setting_key(special_1, 'special_1_key', interpret_key(form.special_1_key.data))

        special_2 = create_special_setting('special_2', form.special_2.data )
        special_2_key = create_special_setting_key(special_2, 'special_2_key', interpret_key(form.special_2_key.data ))

        special_3 = create_special_setting('special_3', form.special_3.data )
        special_3_key = create_special_setting_key(special_3, 'special_3_key', interpret_key(form.special_3_key.data ))

        special_4 = create_special_setting('special_4', form.special_4.data )
        special_4_key = create_special_setting_key(special_4, 'special_4_key', interpret_key(form.special_4_key.data ))

        db.session.add(special_1)
        db.session.add(special_1_key)
        db.session.add(special_2)
        db.session.add(special_2_key)
        db.session.add(special_3)
        db.session.add(special_3_key)
        db.session.add(special_4)
        db.session.add(special_4_key)
       
        if panel_mode == DSC:
            special_5 = create_special_setting('special_5', form.special_5.data)
            special_5_key = create_special_setting_key(special_5, 'special_5_key', interpret_key(form.special_5_key.data))
            
            special_6 = create_special_setting('special_6', form.special_6.data )
            special_6_key = create_special_setting_key(special_6, 'special_6_key', interpret_key(form.special_6_key.data))

            special_7 = create_special_setting('special_7', form.special_7.data)
            special_7_key = create_special_setting_key(special_7, 'special_7_key', interpret_key(form.special_7_key.data))

            special_8 = create_special_setting('special_8', form.special_8.data)
            special_8_key = create_special_setting_key(special_8, 'special_8_key', interpret_key(form.special_8_key.data))

            db.session.add(special_5)
            db.session.add(special_5_key)
            db.session.add(special_6)
            db.session.add(special_6_key)
            db.session.add(special_7)
            db.session.add(special_7_key)
            db.session.add(special_8)
            db.session.add(special_8_key)

        db.session.commit()

        return redirect(url_for('keypad.custom_index'))

    return render_template('keypad/special_buttons.html', form=form)

def get_special_setting(key, setting_default):
    special_setting = Setting.get_by_name(key,default=setting_default).value

    return special_setting

def create_special_setting(key_number, key_value):
    special_setting = Setting.get_by_name(key_number)
    special_setting.value = key_value

    return special_setting

def create_special_setting_key(special_setting, key_type, key_value):
    special_setting_key = Setting.get_by_name(key_type)

    if special_setting.value != SPECIAL_CUSTOM:
        special_setting_key.value = SPECIAL_KEY_MAP[special_setting.value]
    else:
        special_setting_key.value = key_value

    return special_setting_key
    
@keypad.route('/create_button', methods=['GET', 'POST'])
@login_required
def create_button():
    form = KeypadButtonForm()

    if form.validate_on_submit():
        button = KeypadButton()
        form.populate_obj(button)
        button.user_id = current_user.id
        button.label = form.text.data    
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
