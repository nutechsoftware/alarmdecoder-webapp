# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm as Form
from wtforms.fields.html5 import URLField, EmailField, TelField
from wtforms import (ValidationError, HiddenField, TextField, HiddenField,
        PasswordField, SubmitField, TextAreaField, IntegerField, RadioField,
        FileField, DecimalField, BooleanField, SelectField, FormField, FieldList)
from wtforms.validators import (Required, Length, EqualTo, Email, NumberRange,
        URL, AnyOf, Optional)
from flask_login import current_user

from ..user import User
from ..utils import PASSWORD_LEN_MIN, PASSWORD_LEN_MAX, AGE_MIN, AGE_MAX, DEPOSIT_MIN, DEPOSIT_MAX

from ..widgets import ButtonField

class ZoneForm(Form):
    zone_id = IntegerField(u'Zone ID', [Required(), NumberRange(1, 65535)])
    name = TextField(u'Name', [Required(), Length(max=32)])
    description = TextField(u'Description', [Length(max=255)])

    submit = SubmitField(u'Save')
    cancel = ButtonField(u'Cancel', onclick="location.href='/settings/zones'")
