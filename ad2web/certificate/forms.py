# -*- coding: utf-8 -*-

from flask_wtf import Form
from flask_wtf.html5 import URLField, EmailField, TelField
from wtforms import (ValidationError, HiddenField, TextField, HiddenField,
        PasswordField, SubmitField, TextAreaField, IntegerField, RadioField,
        FileField, DecimalField)
from wtforms.validators import (Required, Length, EqualTo, Email, NumberRange,
        URL, AnyOf, Optional)

class GenerateCertificateForm(Form):
    next = HiddenField()
    name = TextField(u'Name', [Required(), Length(max=32)])
    description = TextField(u'Description', [Length(max=255)])

    submit = SubmitField(u'Generate')
