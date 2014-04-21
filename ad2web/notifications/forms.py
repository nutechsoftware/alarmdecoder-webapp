# -*- coding: utf-8 -*-

from flask.ext.wtf import Form
from flask.ext.wtf.html5 import URLField, EmailField, TelField
from wtforms import (ValidationError, HiddenField, TextField, HiddenField,
        PasswordField, SubmitField, TextAreaField, IntegerField, RadioField,
        FileField, DecimalField, BooleanField, SelectField, FormField, FieldList)
from wtforms.validators import (Required, Length, EqualTo, Email, NumberRange,
        URL, AnyOf, Optional)

from .constants import (NOTIFICATIONS, NOTIFICATION_TYPES, EMAIL, GOOGLETALK, POWER_CHANGED,
         ALARM, BYPASS, ARM, DISARM, ZONE_FAULT, ZONE_RESTORE, FIRE, PANIC, LRR, EXP, REL,
         RFX, AUI, KPE, ALARM_EXIT_ERROR, TROUBLE, BYPASS, ACLOSS, LOWBAT, TEST_CALL, OPEN,
         ARM_AWAY, RFLOWBAT, CANCEL, RESTORE, TROUBLE_RESTORE, BYPASS_RESTORE, AC_RESTORE,
         LOWBAT_RESTORE, RFLOWBAT_RESTORE, TEST_RESTORE, ALARM_PANIC, ALARM_FIRE, ALARM_ENTRY,
         ALARM_AUX, ALARM_AUDIBLE, ALARM_SILENT, ALARM_PERIMETER, CUSTOM_NOTIFICATION_EVENTS_TYPES, LRR_EVENTS_TYPES,
         CUSTOM_NOTIFICATION_EVENTS, LRR_EVENTS)

from .models import NotificationSetting, CustomNotification, CustomNotificationSetting

class AppendMixin(object):
    @classmethod
    def append_field(cls, name, field):
        setattr(cls, name, field)
        return cls


class CreateNotificationForm(Form):
    type = SelectField(u'Notification Type', choices=[nt for t, nt in NOTIFICATIONS.iteritems()])

    submit = SubmitField(u'Next')

class EditNotificationForm(Form):
    type = HiddenField()
    description = TextField(u'Description', [Required(), Length(max=255)], description=u'Brief description of this notification')

    def populate_settings(self, obj, id=None):
        raise NotImplementedError()

    def populate_from_settings(self, id):
        raise NotImplementedError()

    def populate_setting(self, name, value, id=None):
        # NOTE: Can we do this better with a session.merge?
        if id is not None:
            setting = NotificationSetting.query.filter_by(notification_id=id, name=name).first()
        else:
            setting = NotificationSetting(name=name)

        setting.value = value

        return setting

    def populate_from_setting(self, id, name, default=None):
        ret = default

        setting = NotificationSetting.query.filter_by(notification_id=id, name=name).first()
        if setting is not None:
            ret = setting.value

        return ret

class EmailNotificationForm(EditNotificationForm):
    source = TextField(u'Source Address', [Required(), Length(max=255)], default='root@localhost', description=u'Emails will originate from this address')
    destination = TextField(u'Destination Address', [Required(), Length(max=255)], description=u'Emails will be sent to this address')

    server = TextField(u'Email Server', [Required(), Length(max=255)], default='localhost', description=u'Email server to use for sending')
    username = TextField(u'Username', [Optional(), Length(max=255)], description=u'Optional: Username for the email server')
    password = PasswordField(u'Password', [Optional(), Length(max=255)], description=u'Optional: Password for the email server')

    submit = SubmitField(u'Save')

    def populate_settings(self, settings, id=None):
        settings['source'] = self.populate_setting('source', self.source.data)
        settings['destination'] = self.populate_setting('destination', self.destination.data)
        settings['server'] = self.populate_setting('server', self.server.data)
        settings['username'] = self.populate_setting('username', self.username.data)
        settings['password'] = self.populate_setting('password', self.password.data)

    def populate_from_settings(self, id):
        self.source.data = self.populate_from_setting(id, 'source')
        self.destination.data = self.populate_from_setting(id, 'destination')
        self.server.data = self.populate_from_setting(id, 'server')
        self.username.data = self.populate_from_setting(id, 'username')
        self.password.data = self.populate_from_setting(id, 'password')

class GoogleTalkNotificationForm(EditNotificationForm):
    source = TextField(u'Source Address', [Required(), Length(max=255)], default='root@localhost', description=u'Messages will originate from this address')
    password = PasswordField(u'Password', [Required(), Length(max=255)], description=u'Password for the source account')
    destination = TextField(u'Destination Address', [Required(), Length(max=255)], description=u'Messages will be sent to this address')

    submit = SubmitField(u'Save')

    def populate_settings(self, settings, id=None):
        settings['source'] = self.populate_setting('source', self.source.data)
        settings['password'] = self.populate_setting('password', self.password.data)
        settings['destination'] = self.populate_setting('destination', self.destination.data)

    def populate_from_settings(self, id):
        self.source.data = self.populate_from_setting(id, 'source')
        self.password.data = self.populate_from_setting(id, 'password')
        self.destination.data = self.populate_from_setting(id, 'destination')

class CreateCustomNotificationForm(Form):
    notification_event = SelectField(u'Event Type', choices=[nt for t, nt in CUSTOM_NOTIFICATION_EVENTS.iteritems()])

    submit = SubmitField(u'Next')

class PowerChangedNotificationForm(Form):
    message = TextField(u'Alert Message', [Required(), Length(max=255)], default='The Alarm has had a power changed event', description=u'Message you want sent in an alert')
    submit = SubmitField(u'Save')

    notification_event = ''

class AlarmNotificationForm(Form):
    notification_event = ''

class BypassNotificationForm(Form):
    zone = TextField(u'Zone', [Required(), Length(max=4)], description=u'The Zone you want to be notified on bypass.')
    message = TextField(u'Alert Message', [Required(), Length(max=255)], default=u'The Alarm has had a zone bypassed.', description=u'Message you want sent in an alert')

    submit = SubmitField(u'Save')
    notification_event = ''

class ArmNotificationForm(Form):
    notification_event = ''

class DisarmNotificationForm(Form):
    notification_event = ''

class ZoneFaultNotificationForm(Form):
    notification_event = ''

class ZoneRestoreNotificationForm(Form):
    notification_event = ''

class FireNotificationForm(Form):
    notification_event = ''

class PanicNotificationForm(Form):
    notification_event = ''

class LRRNotificationForm(Form):
    notification_event = ''

class EXPNotificationForm(Form):
    notification_event = ''

class RELNotificationForm(Form):
    notification_event = ''

class RFXNotificationForm(Form):
    notification_event = ''

class AUINotificationForm(Form):
    notification_event = ''

class KPENotificationForm(Form):
    notification_event = ''
