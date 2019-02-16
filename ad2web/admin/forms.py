# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm as Form
from wtforms import HiddenField, SubmitField, RadioField, DateField, TextField, PasswordField
from wtforms.validators import (Required, Length, EqualTo, Email, NumberRange,
        URL, AnyOf, Optional)

from ..user import USER_ROLE, USER_STATUS, USER, ACTIVE
from ..utils import PASSWORD_LEN_MIN, PASSWORD_LEN_MAX

from ..widgets import ButtonField

class UserForm(Form):
    next = HiddenField()
    name = TextField(u'Username', [Required()])
    email = TextField(u'Email', [Required()])
    password = PasswordField(u'Password', [Required(), Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX)])
    password_again = PasswordField(u'Confirm Password', [Required(), Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX), EqualTo('password')])
    role_code = RadioField(u"Role", [AnyOf([str(val) for val in USER_ROLE.keys()])],
            choices=[(str(val), label) for val, label in USER_ROLE.items()], default=USER)
    status_code = RadioField(u"Status", [AnyOf([str(val) for val in USER_STATUS.keys()])],
            choices=[(str(val), label) for val, label in USER_STATUS.items()], default=ACTIVE)

    submit = SubmitField(u'Save')
    cancel = ButtonField(u'Cancel', onclick="location.href='/settings/users'")
