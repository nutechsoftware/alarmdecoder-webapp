# -*- coding: utf-8 -*-

from flask.ext.wtf import Form
from flask.ext.wtf.html5 import URLField, EmailField, TelField
from wtforms import (ValidationError, HiddenField, TextField, HiddenField,
        PasswordField, SubmitField, TextAreaField, IntegerField, RadioField,
        FileField, DecimalField, BooleanField, SelectField, FormField, FieldList)
from wtforms.validators import (Required, Length, EqualTo, Email, NumberRange, URL, AnyOf, Optional)
from flask.ext.login import current_user

from ..user import User
from ..utils import PASSWORD_LEN_MIN, PASSWORD_LEN_MAX, AGE_MIN, AGE_MAX, DEPOSIT_MIN, DEPOSIT_MAX

from ..widgets import ButtonField
from .constants import FIRE, MEDICAL, POLICE, SPECIAL_4, SPECIAL_CUSTOM, STAY, AWAY, CHIME, RESET, EXIT

from alarmdecoder import AlarmDecoder

class KeypadButtonForm(Form):
    text = TextField(u'Label', [Required(), Length(max=32)])
    code = TextField(u'Code', [Required(), Length(max=32)])

    submit = SubmitField(u'Save')
    cancel = ButtonField(u'Cancel', onclick="location.href='/keypad/button_index'")

class SpecialButtonFormAdemco(Form):
    special_1 = SelectField(u'Special Button 1', choices=[(FIRE, u'Fire'), (POLICE, u'Police'), (MEDICAL, u'Medical'), (SPECIAL_4, u'Panel Default'), (SPECIAL_CUSTOM, u'Custom')], default=FIRE, coerce=int)
    special_1_key = TextField(u'Key Code', [Optional(), Length(max=5)], default="<S1>")

    special_2 = SelectField(u'Special Button 2', choices=[(FIRE, u'Fire'), (POLICE, u'Police'), (MEDICAL, u'Medical'), (SPECIAL_4, u'Panel Default'), (SPECIAL_CUSTOM, u'Custom')], default=POLICE, coerce=int)
    special_2_key = TextField(u'Key Code', [Optional(), Length(max=5)], default="<S2>")

    special_3 = SelectField(u'Special Button 3', choices=[(FIRE, u'Fire'), (POLICE, u'Police'), (MEDICAL, u'Medical'), (SPECIAL_4, u'Panel Default'), (SPECIAL_CUSTOM, u'Custom')], default=MEDICAL, coerce=int)
    special_3_key = TextField(u'Key Code', [Optional(), Length(max=5)], default="<S3>")

    special_4 = SelectField(u'Special Button 4', choices=[(FIRE, u'Fire'), (POLICE, u'Police'), (MEDICAL, u'Medical'), (SPECIAL_4, u'Panel Default'), (SPECIAL_CUSTOM, u'Custom')], default=SPECIAL_4, coerce=int)
    special_4_key = TextField(u'Key Code', [Optional(), Length(max=5)], default="<S4>")

    submit = SubmitField(u'Save')
    cancel = ButtonField(u'Cancel', onclick="location.href='/keypad/button_index'")

class SpecialButtonFormDSC(Form):
    special_1 = SelectField(u'Special Button 1', choices=[(FIRE, u'Fire'), (POLICE, u'Police'), (MEDICAL, u'Medical'), (STAY, u'Stay'), (AWAY, u'Away'), (CHIME, u'Chime'), (RESET, u'Reset'), (EXIT, u'Exit')], default=FIRE, coerce=int)
    special_1_key = TextField(u'Key Code', [Optional(), Length(max=5)], default=AlarmDecoder.KEY_F1)

    special_2 = SelectField(u'Special Button 2', choices=[(FIRE, u'Fire'), (POLICE, u'Police'), (MEDICAL, u'Medical'), (STAY, u'Stay'), (AWAY, u'Away'), (CHIME, u'Chime'), (RESET, u'Reset'), (EXIT, u'Exit')], default=POLICE, coerce=int)
    special_2_key = TextField(u'Key Code', [Optional(), Length(max=5)], default=AlarmDecoder.KEY_F2)

    special_3 = SelectField(u'Special Button 3', choices=[(FIRE, u'Fire'), (POLICE, u'Police'), (MEDICAL, u'Medical'), (STAY, u'Stay'), (AWAY, u'Away'), (CHIME, u'Chime'), (RESET, u'Reset'), (EXIT, u'Exit')], default=MEDICAL, coerce=int)
    special_3_key = TextField(u'Key Code', [Optional(), Length(max=5)], default=AlarmDecoder.KEY_F3)

    special_4 = SelectField(u'Special Button 4', choices=[(FIRE, u'Fire'), (POLICE, u'Police'), (MEDICAL, u'Medical'), (STAY, u'Stay'), (AWAY, u'Away'), (CHIME, u'Chime'), (RESET, u'Reset'), (EXIT, u'Exit')], default=STAY, coerce=int)
    special_4_key = TextField(u'Key Code', [Optional(), Length(max=5)], default=AlarmDecoder.KEY_F4)

    special_5 = SelectField(u'Special Button 5', choices=[(FIRE, u'Fire'), (POLICE, u'Police'), (MEDICAL, u'Medical'), (STAY, u'Stay'), (AWAY, u'Away'), (CHIME, u'Chime'), (RESET, u'Reset'), (EXIT, u'Exit')], default=AWAY, coerce=int)
    special_5_key = TextField(u'Key Code', [Optional(), Length(max=5)], default=chr(5) + chr(5) + chr(5))

    special_6 = SelectField(u'Special Button 6', choices=[(FIRE, u'Fire'), (POLICE, u'Police'), (MEDICAL, u'Medical'), (STAY, u'Stay'), (AWAY, u'Away'), (CHIME, u'Chime'), (RESET, u'Reset'), (EXIT, u'Exit')], default=CHIME, coerce=int)
    special_6_key = TextField(u'Key Code', [Optional(), Length(max=5)], default=chr(6) + chr(6) + chr(6))

    special_7 = SelectField(u'Special Button 7', choices=[(FIRE, u'Fire'), (POLICE, u'Police'), (MEDICAL, u'Medical'), (STAY, u'Stay'), (AWAY, u'Away'), (CHIME, u'Chime'), (RESET, u'Reset'), (EXIT, u'Exit')], default=RESET, coerce=int)
    special_7_key = TextField(u'Key Code', [Optional(), Length(max=5)], default=chr(7) + chr(7) + chr(7))

    special_8 = SelectField(u'Special Button 8', choices=[(FIRE, u'Fire'), (POLICE, u'Police'), (MEDICAL, u'Medical'), (STAY, u'Stay'), (AWAY, u'Away'), (CHIME, u'Chime'), (RESET, u'Reset'), (EXIT, u'Exit')], default=EXIT, coerce=int)
    special_8_key = TextField(u'Key Code', [Optional(), Length(max=5)], default=chr(8) + chr(8) + chr(8))

    submit = SubmitField(u'Save')
    cancel = ButtonField(u'Cancel', onclick="location.href='/keypad/button_index'")
