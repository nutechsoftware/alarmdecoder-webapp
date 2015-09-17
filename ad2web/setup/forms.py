# -*- coding: utf-8 -*-

from flask import Markup
from flask.ext.wtf import Form
from flask.ext.wtf.html5 import URLField, EmailField, TelField
import wtforms
from wtforms import (Field, ValidationError, HiddenField, TextField, HiddenField,
        PasswordField, SubmitField, TextAreaField, IntegerField, RadioField,
        FileField, DecimalField, SelectField, BooleanField, SelectMultipleField,
        FormField)
from wtforms.validators import (Required, Length, EqualTo, Email, NumberRange,
        URL, AnyOf, Optional)
from .constants import NETWORK_DEVICE, SERIAL_DEVICE, BAUDRATES, DEFAULT_BAUDRATES
from ..validators import PathExists, Hex
from ..utils import STRING_LEN, PASSWORD_LEN_MIN, PASSWORD_LEN_MAX
from ..widgets import ButtonField, MultiCheckboxField
from alarmdecoder.panels import ADEMCO, DSC


class SetupButtonForm(wtforms.Form):
    previous = ButtonField(u'Previous', onclick='history.go(-1);')
    next = SubmitField(u'Next')

class DeviceTypeForm(Form):
    device_type = SelectField(u'Device Type', choices=[('AD2USB', u'AD2USB'), ('AD2PI', u'AD2PI'), ('AD2SERIAL', u'AD2SERIAL')], default='AD2USB')
    device_location = SelectField(u'Device Location', choices=[('local', 'Local Device'), ('network', 'Network')], default='local')

    buttons = FormField(SetupButtonForm)

class NetworkDeviceForm(Form):
    device_address = TextField(u'Address', [Required(), Length(max=255)], description=u'Hostname or IP address', default='localhost')
    device_port = IntegerField(u'Port', [Required(), NumberRange(1024, 65535)], description=u'', default=10000)
    ssl = BooleanField(u'Use SSL?')

    buttons = FormField(SetupButtonForm)

class SSLForm(Form):
    ca_cert = FileField(u'CA Certificate', [Required()], description=u'CA certificate created for the AlarmDecoder to authorize clients.')
    cert = FileField(u'Certificate', [Required()], description=u'Client certificate used by this webapp.')
    key = FileField(u'Key', [Required()], description=u'Client certificate key used by this webapp.')

    buttons = FormField(SetupButtonForm)

class SSLHostForm(Form):
    config_path = TextField(u'SER2SOCK Configuration Path', [Required(), PathExists()], default='/etc/ser2sock')
    device_address = TextField(u'Address', [Required(), Length(max=255)], description=u'Hostname or IP address', default='localhost')
    device_port = IntegerField(u'Port', [Required(), NumberRange(1024, 65535)], description=u'', default=10000)
    ssl = BooleanField(u'Use SSL?')

    buttons = FormField(SetupButtonForm)

class LocalDeviceForm(Form):
    device_path = TextField(u'Path', [Required(), Length(max=255), PathExists()], description=u'Filesystem path to your AlarmDecoder.', default='/dev/ttyAMA0')
    baudrate = SelectField(u'Baudrate', choices=[(baudrate, str(baudrate)) for baudrate in BAUDRATES], default=115200, coerce=int)
    confirm_management = BooleanField(u'Share AlarmDecoder on your network?', description='This setting serves the AlarmDecoder on your network with ser2sock and allows other software (Software keypad, etc.) to use it in conjunction with this webapp.')

    buttons = FormField(SetupButtonForm)

class LocalDeviceFormUSB(Form):
    device_path = SelectField(u'Path', choices=[('/dev/ttyUSB0', u'/dev/ttyUSB0')], default='/dev/ttyUSB0', coerce=str)
    baudrate = SelectField(u'Baudrate', choices=[(baudrate, str(baudrate)) for baudrate in BAUDRATES], default=115200, coerce=int)
    confirm_management = BooleanField(u'Share AlarmDecoder on your network?', description='This setting serves the AlarmDecoder on your network with ser2sock and allows other software (Software keypad, etc.) to use it in conjunction with this webapp.')

    buttons = FormField(SetupButtonForm)

class TestDeviceForm(Form):
    # NOTE: Not using SetupButtonForm because of excess padding with no actual form elements.
    previous = ButtonField(u'Previous', onclick='history.go(-1);')
    next = SubmitField(u'Next')

class DeviceForm(Form):
    panel_mode = RadioField(u'Panel Type', choices=[(ADEMCO, 'Honeywell/Ademco'), (DSC, 'DSC')], default=ADEMCO, coerce=int)
    keypad_address = IntegerField(u'Keypad Address', [Required(), NumberRange(1, 99)], default=18)
    address_mask = TextField(u'AlarmDecoder Address Mask', [Required(), Length(max=8), Hex()], default=u'FFFFFFFF')
    internal_address_mask = TextField(u'Webapp Address Mask', [Required(), Length(max=8), Hex()], default=u'FFFFFFFF')
    zone_expanders = MultiCheckboxField(u'Zone Expanders', choices=[('1', 'Emulate zone expander #1?'), ('2', 'Emulate zone expander #2?'), ('3', 'Emulate zone expander #3?'), ('4', 'Emulate zone expander #4?'), ('5', 'Emulate zone expander #5?')])
    relay_expanders = MultiCheckboxField(u'Relay Expanders', choices=[('1', 'Emulate relay expander #1?'), ('2', 'Emulate relay expander #2?'), ('3', 'Emulate relay expander #3?'), ('4', 'Emulate relay expander #4?')])
    lrr_enabled = BooleanField(u'Emulate Long Range Radio?')
    deduplicate = BooleanField(u'Deduplicate messages?')

    buttons = FormField(SetupButtonForm)

class CreateAccountForm(Form):
    name = TextField(u'Username', [Required(), Length(max=STRING_LEN)], default=u'admin')
    email = TextField(u'Email Address', [Required(), Length(max=STRING_LEN), Email()], default=u'admin@example.com')
    password = PasswordField('New password', [Required(), Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX)])
    password_again = PasswordField('Password again', [Required(), Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX), EqualTo('password')])

    save = SubmitField(u'Save')
