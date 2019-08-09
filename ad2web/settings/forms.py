# -*- coding: utf-8 -*-

import os
import string
import random
from flask_wtf import FlaskForm as Form
from wtforms.fields.html5 import URLField, EmailField, TelField
from wtforms import (ValidationError, HiddenField, TextField, HiddenField,
        PasswordField, SubmitField, TextAreaField, IntegerField, RadioField,
        FileField, DecimalField, BooleanField, SelectField, FormField, FieldList)
from wtforms.validators import (Required, Length, EqualTo, Email, NumberRange,
        URL, AnyOf, Optional, IPAddress)
from flask_login import current_user

from ..user import User
from ..utils import PASSWORD_LEN_MIN, PASSWORD_LEN_MAX, AGE_MIN, AGE_MAX, DEPOSIT_MIN, DEPOSIT_MAX
from ..utils import allowed_file, ALLOWED_AVATAR_EXTENSIONS, INSTANCE_FOLDER_PATH
from ..utils import SEX_TYPE

from ..widgets import ButtonField
from ..settings import Setting
from .constants import DAILY, WEEKLY, MONTHLY, NONE

class ProfileForm(Form):
    multipart = True
    next = HiddenField()
    email = EmailField(u'Email', [Required(), Email()])
    # Don't use the same name as model because we are going to use populate_obj().
    avatar_file = FileField(u"Avatar", [Optional()])
    sex_code = RadioField(u"Sex", [AnyOf([str(val) for val in SEX_TYPE.keys()])], choices=[(str(val), label) for val, label in SEX_TYPE.items()])
    age = IntegerField(u'Age', [Optional(), NumberRange(AGE_MIN, AGE_MAX)])
    phone = TelField(u'Phone', [Length(max=64)])
    url = URLField(u'URL', [Optional(), URL()])
    deposit = DecimalField(u'Deposit', [Optional(), NumberRange(DEPOSIT_MIN, DEPOSIT_MAX)])
    location = TextField(u'Location', [Length(max=64)])
    bio = TextAreaField(u'Bio', [Length(max=1024)])
    submit = SubmitField(u'Save')

    def validate_name(form, field):
        user = User.get_by_id(current_user.id)
        if not user.check_name(field.data):
            raise ValidationError("Please pick another name.")

    def validate_avatar_file(form, field):
        if field.data and not allowed_file(field.data.filename):
            raise ValidationError("Please upload files with extensions: %s" % "/".join(ALLOWED_AVATAR_EXTENSIONS))


class PasswordForm(Form):
    next = HiddenField()
    password = PasswordField('Current password', [Required()])
    new_password = PasswordField('New password', [Required(), Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX)])
    password_again = PasswordField('Password again', [Required(), Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX), EqualTo('new_password')])
    submit = SubmitField(u'Save')
    cancel = ButtonField(u'Cancel', onclick="location.href='/settings'")

    def validate_password(form, field):
        user = User.get_by_id(current_user.id)
        if not user.check_password(field.data):
            raise ValidationError("Password is wrong.")

class ImportSettingsForm(Form):
    import_file = FileField(u'Settings Archive', [Required()])

    submit = SubmitField(u'Import')

class HostSettingsForm(Form):
    hostname = TextField(u'Hostname', [Required(), Length(max=63)])
    submit = SubmitField(u'Save')
    cancel = ButtonField(u'Cancel', onclick="location.href='/settings/host'")

    def validate_hostname(form, field):
        invalid = " !'\"?;:,@#$%^&*()+<>/|\\{}[]_"
        message = "Hostname must be between 1 and 63 characters long, not contain ( " + invalid + " ), or start and end with punctuation."

        invalid_set = set(invalid)
        h = field.data and len(field.data) or 0
        if h < 1 or h > 63:
            raise ValidationError(message)

        if field.data[0] in string.punctuation:
            raise ValidationError(message)
        if field.data[-1] in string.punctuation:
            raise ValidationError(message)
        if any((c in invalid_set) for c in field.data):
            raise ValidationError("Invalid characters found - Please remove any of the following: " + invalid)

class EthernetSelectionForm(Form):
    ethernet_devices =  SelectField(u'Network Device', choices=[('eth0', u'eth0')], default='eth0', coerce=str)
    submit = SubmitField(u'Configure')

class EthernetConfigureForm(Form):
    ethernet_device = HiddenField()
    connection_type = RadioField(u'Connection Type', choices=[('static', 'Static'), ('dhcp', 'DHCP')], default='dhcp', coerce=str)
    ip_address = TextField('IP Address', [IPAddress('Invalid IP Address')])
    gateway = TextField('Default Gateway', [IPAddress('Invalid Gateway IP Format')])
    netmask = TextField('Subnet Mask', [IPAddress('Invalid Subnet IP Format')])
    submit = SubmitField(u'Save')
    cancel = ButtonField(u'Cancel', onclick="location.href='/settings/host'")

class SwitchBranchForm(Form):
    remotes_web = SelectField(u'Origin alarmdecoder-webapp', coerce=str)
    branches_web = SelectField(u'Branch', coerce=str)
    remotes_api = SelectField(u'Origin alarmdecoder api', coerce=str)
    branches_api = SelectField(u'Branch', coerce=str)
    submit = SubmitField(u'Checkout')

class EmailConfigureForm(Form):
    mail_server = TextField(u'Email Server', [Required(), Length(max=255)], description=u'ex: smtp.gmail.com')
    port = IntegerField(u'Server Port', [Required(), NumberRange(1, 65535)], description=u'ex: 25 for normal or 587 for TLS')
    tls = BooleanField(u'Use TLS?', default=False)
    auth_required = BooleanField(u'Authentication Required?',default=False)
    username = TextField(u'Username', [Optional(), Length(max=255)], description=u'Email Username')
    password = PasswordField(u'Password', [Optional(), Length(max=255)], description=u'Email Password')
    default_sender = TextField(u'From Email', [Required(), Length(max=255)], default='root@alarmdecoder', description=u'Emails will come from this address')
    submit = SubmitField(u'Save')

class UPNPForm(Form):
    internal_port = IntegerField(u'Internal Port', [Required()], default=443, description=u'Internal Port to Forward To')
    external_port = IntegerField(u'External Port', [Required()], default=random.randint(1200,60000), description=u'External Port to map to Internal Port')

    submit = SubmitField(u'Save')

class VersionCheckerForm(Form):
    version_checker_timeout = IntegerField(u'Timeout in Seconds', [Required(), NumberRange(600)], default=600, description=u'How often to check for version updates')
    version_checker_disable = BooleanField(u'Disable?', default=False)

    submit = SubmitField(u'Save')

class ExportConfigureForm(Form):
    frequency = SelectField(u'Frequency', choices=[(NONE, u'None'), (DAILY, u'Daily'), (WEEKLY, u'Weekly'), (MONTHLY, u'Monthly')], default=NONE, description=u'Frequency of Automatic Export', coerce=int)
    email = BooleanField(u'Email Export?', default=True)
    email_address = TextField(u'Email Address', [Optional(), Length(max=255)], description=u'Email Address to Send Export to')
    local_file = BooleanField(u'Save to Local File?', default=True)
    local_file_path = TextField(u'Path to Save file', [Optional(), Length(max=255)], default=os.path.join(INSTANCE_FOLDER_PATH, 'exports'), description='Path on AlarmDecoder to Save Export')
    days_to_keep = IntegerField(u'Days to Keep Exports on Disk?', [Optional(), NumberRange(1, 255)],default=7)

    submit = SubmitField(u'Save')
