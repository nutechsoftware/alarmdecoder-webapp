# -*- coding: utf-8 -*-

from flask.ext.wtf import Form
from flask.ext.wtf.html5 import URLField, EmailField, TelField
from wtforms import (ValidationError, HiddenField, TextField, HiddenField,
        PasswordField, SubmitField, TextAreaField, IntegerField, RadioField,
        FileField, DecimalField, SelectField, BooleanField)
from wtforms.validators import (Required, Length, EqualTo, Email, NumberRange,
        URL, AnyOf, Optional)
from ..settings.forms import NetworkDeviceForm, SerialDeviceForm
from ..settings.constants import NETWORK_DEVICE, SERIAL_DEVICE

class DeviceTypeForm(Form):
    device_type = SelectField(u'Device Type', choices=[('AD2USB', u'AD2USB'), ('AD2PI', u'AD2PI'), ('AD2SERIAL', u'AD2SERIAL')], default='AD2USB')

    submit = SubmitField(u'Next')

class DeviceLocationForm(Form):
    device_location = SelectField(u'Device Location', choices=[('local', 'Local Device'), ('network', 'Network')], default='local')

    submit = SubmitField(u'Next')

class SSLForm(Form):
    cert = FileField(u'Certificate')

    submit = SubmitField(u'Next')

class SSLHostForm(Form):
    host = BooleanField(u'Would you like us to make the device available over your network?')

    submit = SubmitField(u'Next')
