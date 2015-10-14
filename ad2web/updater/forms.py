# -*- coding: utf-8 -*-

from flask.ext.wtf import Form
from wtforms import (ValidationError, HiddenField, TextField, HiddenField,
        PasswordField, SubmitField, TextAreaField, IntegerField, RadioField,
        FileField, DecimalField, BooleanField, SelectField, FormField, FieldList)
from wtforms.validators import (Required, Length, EqualTo, Email, NumberRange,
        URL, AnyOf, Optional, Regexp)

from ..widgets import ButtonField

class UpdateFirmwareForm(Form):
    firmware_file = FileField(u'Firmware File', [Required()])

    submit = SubmitField(u'Upload')
    cancel = ButtonField(u'Cancel', onclick="location.href='/settings'")
