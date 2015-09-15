# -*- coding: utf-8 -*-

import json
from flask.ext.wtf import Form
from flask.ext.wtf.html5 import URLField, EmailField, TelField
import wtforms
import ast
from wtforms import (ValidationError, HiddenField, TextField, HiddenField,
        PasswordField, SubmitField, TextAreaField, IntegerField, RadioField,
        FileField, DecimalField, BooleanField, SelectField, FormField, FieldList,
        SelectMultipleField)
from wtforms.validators import (Required, Length, EqualTo, Email, NumberRange,
        URL, AnyOf, Optional)
from wtforms.widgets import ListWidget, CheckboxInput
from .constants import (NOTIFICATIONS, NOTIFICATION_TYPES, SUBSCRIPTIONS, DEFAULT_SUBSCRIPTIONS, EMAIL, GOOGLETALK, PUSHOVER, PUSHOVER_PRIORITIES, 
                        NMA_PRIORITIES, LOWEST, LOW, NORMAL, HIGH, EMERGENCY, PROWL_PRIORITIES, GROWL, GROWL_PRIORITIES, GROWL_TITLE,
                        URLENCODE, JSON, XML, CUSTOM_METHOD_POST, CUSTOM_METHOD_GET_TYPE)
from .models import NotificationSetting
from ..widgets import ButtonField, MultiCheckboxField


class NotificationButtonForm(wtforms.Form):
    cancel = ButtonField(u'Cancel', onclick="location.href='/settings/notifications'")
    submit = SubmitField(u'Save')
    test = SubmitField(u'Save & Test')


class CreateNotificationForm(Form):
    type = SelectField(u'Notification Type', choices=[nt for t, nt in NOTIFICATIONS.iteritems()])

    submit = SubmitField(u'Next')
    cancel = ButtonField(u'Cancel', onclick="location.href='/settings/notifications'")


class EditNotificationMessageForm(Form):
    id = HiddenField()
    text = TextAreaField(u'Message Text', [Required(), Length(max=255)])

    submit = SubmitField(u'Save')
    cancel = ButtonField(u'Cancel', onclick="location.href='/settings/notifications/messages'")


class NotificationReviewForm(Form):
    buttons = FormField(NotificationButtonForm)


class EditNotificationForm(Form):
    type = HiddenField()
    description = TextField(u'Description', [Required(), Length(max=255)], description=u'Brief description of this notification')
    subscriptions = MultiCheckboxField(u'Notify on..', choices=[(str(k), v) for k, v in SUBSCRIPTIONS.iteritems()])

    def populate_settings(self, settings, id=None):
        settings['subscriptions'] = self.populate_setting('subscriptions', json.dumps({str(k): True for k in self.subscriptions.data}))

    def populate_from_settings(self, id):
        subscriptions = self.populate_from_setting(id, 'subscriptions')
        if subscriptions:
            self.subscriptions.data = [k if v == True else False for k, v in json.loads(subscriptions).iteritems()]

    def populate_setting(self, name, value, id=None):
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


class EmailNotificationInternalForm(Form):
    source = TextField(u'Source Address', [Required(), Length(max=255)], default='root@localhost', description=u'Emails will originate from this address')
    destination = TextField(u'Destination Address', [Required(), Length(max=255)], description=u'Emails will be sent to this address')

    subject = TextField(u'Email Subject', [Required(), Length(max=255)], default='AlarmDecoder: Alarm Event', description=u'Emails will contain this text as the subject')

    server = TextField(u'Email Server', [Required(), Length(max=255)], default='localhost')
    port = IntegerField(u'Server Port', [Required(), NumberRange(1, 65535)], default=25)
    tls = BooleanField(u'Use TLS?', default=False)
    authentication_required = BooleanField(u'Authenticate with email server?', default=False)
    username = TextField(u'Username', [Optional(), Length(max=255)])
    password = PasswordField(u'Password', [Optional(), Length(max=255)])

    def __init__(self, *args, **kwargs):
        kwargs['csrf_enabled'] = False
        super(EmailNotificationInternalForm, self).__init__(*args, **kwargs)


class EmailNotificationForm(EditNotificationForm):
    form_field = FormField(EmailNotificationInternalForm, label='HiMom')

    submit = SubmitField(u'Next')
    cancel = ButtonField(u'Cancel', onclick="location.href='/settings/notifications'")

    def populate_settings(self, settings, id=None):
        EditNotificationForm.populate_settings(self, settings, id)

        settings['source'] = self.populate_setting('source', self.form_field.source.data)
        settings['destination'] = self.populate_setting('destination', self.form_field.destination.data)
        settings['subject'] = self.populate_setting('subject', self.form_field.subject.data)
        settings['server'] = self.populate_setting('server', self.form_field.server.data)
        settings['port'] = self.populate_setting('port', self.form_field.port.data)
        settings['tls'] = self.populate_setting('tls', self.form_field.tls.data)
        settings['authentication_required'] = self.populate_setting('authentication_required', self.form_field.authentication_required.data)
        settings['username'] = self.populate_setting('username', self.form_field.username.data)
        settings['password'] = self.populate_setting('password', self.form_field.password.data)

    def populate_from_settings(self, id):
        EditNotificationForm.populate_from_settings(self, id)

        self.form_field.source.data = self.populate_from_setting(id, 'source')
        self.form_field.destination.data = self.populate_from_setting(id, 'destination')
        self.form_field.subject.data = self.populate_from_setting(id, 'subject')
        self.form_field.server.data = self.populate_from_setting(id, 'server')
        self.form_field.tls.data = self.populate_from_setting(id, 'tls')
        self.form_field.port.data = self.populate_from_setting(id, 'port')
        self.form_field.authentication_required.data = self.populate_from_setting(id, 'authentication_required')
        self.form_field.username.data = self.populate_from_setting(id, 'username')
        self.form_field.password.widget.hide_value = False
        self.form_field.password.data = self.populate_from_setting(id, 'password')


class GoogleTalkNotificationInternalForm(Form):
    source = TextField(u'Source Address', [Required(), Length(max=255)], default='root@localhost', description=u'Messages will originate from this address')
    password = PasswordField(u'Password', [Required(), Length(max=255)], description=u'Password for the source account')
    destination = TextField(u'Destination Address', [Required(), Length(max=255)], description=u'Messages will be sent to this address')

    def __init__(self, *args, **kwargs):
        kwargs['csrf_enabled'] = False
        super(GoogleTalkNotificationInternalForm, self).__init__(*args, **kwargs)


class GoogleTalkNotificationForm(EditNotificationForm):
    form_field = FormField(GoogleTalkNotificationInternalForm)

    submit = SubmitField(u'Next')
    cancel = ButtonField(u'Cancel', onclick="location.href='/settings/notifications'")

    def populate_settings(self, settings, id=None):
        EditNotificationForm.populate_settings(self, settings, id)
        settings['source'] = self.populate_setting('source', self.form_field.source.data)
        settings['password'] = self.populate_setting('password', self.form_field.password.data)
        settings['destination'] = self.populate_setting('destination', self.form_field.destination.data)

    def populate_from_settings(self, id):
        EditNotificationForm.populate_from_settings(self, id)
        self.form_field.source.data = self.populate_from_setting(id, 'source')
        self.form_field.password.widget.hide_value = False
        self.form_field.password.data = self.populate_from_setting(id, 'password')
        self.form_field.destination.data = self.populate_from_setting(id, 'destination')


class PushoverNotificationInternalForm(Form):
    token = TextField(u'API Token', [Required(), Length(max=30)], description=u'Your Application\'s API Token')
    user_key = TextField(u'User/Group Key', [Required(), Length(max=30)], description=u'Your user or group key')
    priority = SelectField(u'Message Priority', choices=[PUSHOVER_PRIORITIES[LOWEST], PUSHOVER_PRIORITIES[LOW], PUSHOVER_PRIORITIES[NORMAL], PUSHOVER_PRIORITIES[HIGH], PUSHOVER_PRIORITIES[EMERGENCY]], default=PUSHOVER_PRIORITIES[LOW], description='Pushover message priority', coerce=int)
    title = TextField(u'Title of Message', [Length(max=255)], description=u'Title of Notification Messages')

    def __init__(self, *args, **kwargs):
        kwargs['csrf_enabled'] = False
        super(PushoverNotificationInternalForm, self).__init__(*args, **kwargs)


class PushoverNotificationForm(EditNotificationForm):
    form_field = FormField(PushoverNotificationInternalForm)

    submit = SubmitField(u'Next')
    cancel = ButtonField(u'Cancel', onclick="location.href='/settings/notifications'")

    def populate_settings(self, settings, id=None):
        EditNotificationForm.populate_settings(self, settings, id)
        settings['token'] = self.populate_setting('token', self.form_field.token.data)
        settings['user_key'] = self.populate_setting('user_key', self.form_field.user_key.data)
        settings['priority'] = self.populate_setting('priority', self.form_field.priority.data)
        settings['title'] = self.populate_setting('title', self.form_field.title.data)

    def populate_from_settings(self, id):
        EditNotificationForm.populate_from_settings(self, id)
        self.form_field.token.data = self.populate_from_setting(id, 'token')
        self.form_field.user_key.data = self.populate_from_setting(id, 'user_key')
        self.form_field.priority.data = self.populate_from_setting(id, 'priority')
        self.form_field.title.data = self.populate_from_setting(id, 'title')


class TwilioNotificationInternalForm(Form):
    account_sid = TextField(u'Account SID', [Required(), Length(max=50)], description=u'Your Twilio Account SID')
    auth_token = TextField(u'Auth Token', [Required(), Length(max=50)], description=u'Your Twilio User Auth Token')
    number_to = TextField(u'To', [Required(), Length(max=15)], description=u'Number to send SMS to')
    number_from = TextField(u'From', [Required(), Length(max=15)], description=u'Must Be A Valid Twilio Phone Number')

    def __init__(self, *args, **kwargs):
        kwargs['csrf_enabled'] = False
        super(TwilioNotificationInternalForm, self).__init__(*args, **kwargs)


class TwilioNotificationForm(EditNotificationForm):
    form_field = FormField(TwilioNotificationInternalForm)

    submit = SubmitField(u'Next')
    cancel = ButtonField(u'Cancel', onclick="location.href='/settings/notifications'")

    def populate_settings(self, settings, id=None):
        EditNotificationForm.populate_settings(self, settings, id)
        settings['account_sid'] = self.populate_setting('account_sid', self.form_field.account_sid.data)
        settings['auth_token'] = self.populate_setting('auth_token', self.form_field.auth_token.data)
        settings['number_to'] = self.populate_setting('number_to', self.form_field.number_to.data)
        settings['number_from'] = self.populate_setting('number_from', self.form_field.number_from.data)

    def populate_from_settings(self, id):
        EditNotificationForm.populate_from_settings(self, id)
        self.form_field.account_sid.data = self.populate_from_setting(id, 'account_sid')
        self.form_field.auth_token.data = self.populate_from_setting(id, 'auth_token')
        self.form_field.number_to.data = self.populate_from_setting(id, 'number_to')
        self.form_field.number_from.data = self.populate_from_setting(id, 'number_from')


class NMANotificationInternalForm(Form):
    api_key = TextField(u'API Key', [Required(), Length(max=50)], description=u'Your NotifyMyAndroid API Key')
    app_name = TextField(u'Application Name', [Required(), Length(max=256)], description=u'Application Name to Show in Notifications', default='AlarmDecoder')
    nma_priority = SelectField(u'Message Priority', choices=[NMA_PRIORITIES[LOWEST], NMA_PRIORITIES[LOW], NMA_PRIORITIES[NORMAL], NMA_PRIORITIES[HIGH], NMA_PRIORITIES[EMERGENCY]], default=NMA_PRIORITIES[LOW], description='NotifyMyAndroid message priority', coerce=int)
    
    def __init__(self, *args, **kwargs):
        kwargs['csrf_enabled'] = False
        super(NMANotificationInternalForm, self).__init__(*args, **kwargs)


class NMANotificationForm(EditNotificationForm):
    form_field = FormField(NMANotificationInternalForm)

    submit = SubmitField(u'Next')
    cancel = ButtonField(u'Cancel', onclick="location.href='/settings/notifications'")

    def populate_settings(self, settings, id=None):
        EditNotificationForm.populate_settings(self, settings, id)
        settings['api_key'] = self.populate_setting('api_key', self.form_field.api_key.data)
        settings['app_name'] = self.populate_setting('app_name', self.form_field.app_name.data)
        settings['nma_priority'] = self.populate_setting('nma_priority', self.form_field.nma_priority.data)

    def populate_from_settings(self, id):
        EditNotificationForm.populate_from_settings(self, id)
        self.form_field.api_key.data = self.populate_from_setting(id, 'api_key')
        self.form_field.app_name.data = self.populate_from_setting(id, 'app_name')
        self.form_field.nma_priority.data = self.populate_from_setting(id, 'nma_priority')


class ProwlNotificationInternalForm(Form):
    prowl_api_key = TextField(u'API Key', [Required(), Length(max=50)], description=u'Your Prowl API Key')
    prowl_app_name = TextField(u'Application Name', [Required(), Length(max=256)], description=u'Application Name to Show in Notifications', default='AlarmDecoder')
    prowl_priority = SelectField(u'Message Priority', choices=[PROWL_PRIORITIES[LOWEST], PROWL_PRIORITIES[LOW], PROWL_PRIORITIES[NORMAL], PROWL_PRIORITIES[HIGH], PROWL_PRIORITIES[EMERGENCY]], default=PROWL_PRIORITIES[LOW], description='Prowl message priority', coerce=int)

    def __init__(self, *args, **kwargs):
        kwargs['csrf_enabled'] = False
        super(ProwlNotificationInternalForm, self).__init__(*args, **kwargs)


class ProwlNotificationForm(EditNotificationForm):
    form_field = FormField(ProwlNotificationInternalForm)

    submit = SubmitField(u'Next')
    cancel = ButtonField(u'Cancel', onclick="location.href='/settings/notifications'")

    def populate_settings(self, settings, id=None):
        EditNotificationForm.populate_settings(self, settings, id)

        settings['prowl_api_key'] = self.populate_setting('prowl_api_key', self.form_field.prowl_api_key.data)
        settings['prowl_app_name'] = self.populate_setting('prowl_app_name', self.form_field.prowl_app_name.data)
        settings['prowl_priority'] = self.populate_setting('prowl_priority', self.form_field.prowl_priority.data)

    def populate_from_settings(self, id):
        EditNotificationForm.populate_from_settings(self, id)
        
        self.form_field.prowl_api_key.data = self.populate_from_setting(id, 'prowl_api_key')
        self.form_field.prowl_app_name.data = self.populate_from_setting(id, 'prowl_app_name')
        self.form_field.prowl_priority.data = self.populate_from_setting(id, 'prowl_priority')


class GrowlNotificationInternalForm(Form):
    growl_hostname = TextField(u'Hostname', [Required(), Length(max=255)], description=u'Growl server to send notification to')
    growl_port = TextField(u'Port', [Required(), Length(max=10)], description=u'Growl server port', default=23053)
    growl_password = PasswordField(u'Password', description=u'The password for the growl server') 
    growl_title = TextField(u'Title', [Required(), Length(max=255)], description=u'Notification Title', default=GROWL_TITLE)
    growl_priority = SelectField(u'Message Priority', choices=[GROWL_PRIORITIES[LOWEST], GROWL_PRIORITIES[LOW], GROWL_PRIORITIES[NORMAL], GROWL_PRIORITIES[HIGH], GROWL_PRIORITIES[EMERGENCY]], default=GROWL_PRIORITIES[LOW], description='Growl message priority', coerce=int)

    def __init__(self, *args, **kwargs):
        kwargs['csrf_enabled'] = False
        super(GrowlNotificationInternalForm, self).__init__(*args, **kwargs)


class GrowlNotificationForm(EditNotificationForm):
    form_field = FormField(GrowlNotificationInternalForm)

    submit = SubmitField(u'Next')
    cancel = ButtonField(u'Cancel', onclick="location.href='/settings/notifications'")

    def populate_settings(self, settings, id=None):
        EditNotificationForm.populate_settings(self, settings, id)

        settings['growl_hostname'] = self.populate_setting('growl_hostname', self.form_field.growl_hostname.data)
        settings['growl_port'] = self.populate_setting('growl_port', self.form_field.growl_port.data)
        settings['growl_password'] = self.populate_setting('growl_password', self.form_field.growl_password.data)
        settings['growl_title'] = self.populate_setting('growl_title', self.form_field.growl_title.data)
        settings['growl_priority'] = self.populate_setting('growl_priority', self.form_field.growl_title.data)

    def populate_from_settings(self, id):
        EditNotificationForm.populate_from_settings(self, id)

        self.form_field.growl_hostname.data = self.populate_from_setting(id, 'growl_hostname')
        self.form_field.growl_port.data = self.populate_from_setting(id, 'growl_port')
        self.form_field.growl_password.data = self.populate_from_setting(id, 'growl_password')
        self.form_field.growl_title.data = self.populate_from_setting(id, 'growl_title')
        self.form_field.growl_priority.data = self.populate_from_setting(id, 'growl_priority')


class CustomValueForm(Form):
    custom_key = TextField(label=None)
    custom_value = TextField(label=None)

    def __init__(self, *args, **kwargs):
        kwargs['csrf_enabled'] = False
        super(CustomValueForm, self).__init__(*args, **kwargs)


class CustomPostInternalForm(Form):
    custom_url = TextField(u'URL', [Required(), Length(max=255)], description=u'URL to send data to (ex: www.alarmdecoder.com)')
    custom_path = TextField(u'Path', [Required(), Length(max=255)], description=u'Path to send variables to (ex: /publicapi/add)')
    is_ssl = BooleanField(u'SSL?', default=False, description=u'Is the URL SSL or No?')
    method = RadioField(u'Method', choices=[(CUSTOM_METHOD_POST, 'POST'), (CUSTOM_METHOD_GET_TYPE, 'GET')], default=CUSTOM_METHOD_POST, coerce=int)
    post_type = RadioField(u'Type', choices=[(URLENCODE, 'urlencoded'), (JSON, 'JSON'), (XML, 'XML')], default=URLENCODE, coerce=int)

    custom_values = FieldList(FormField(CustomValueForm), validators=[Optional()], label=None)
    add_field = ButtonField(u'Add Field', onclick='addField();')

    def __init__(self, *args, **kwargs):
        kwargs['csrf_enabled'] = False
        super(CustomPostInternalForm, self).__init__(*args, **kwargs)


class CustomPostForm(EditNotificationForm):
    form_field = FormField(CustomPostInternalForm)

    submit = SubmitField(u'Next')
    cancel = ButtonField(u'Cancel', onclick="location.href='/settings/notifications'")

    def populate_settings(self, settings, id=None):
        EditNotificationForm.populate_settings(self, settings, id)

        settings['custom_url'] = self.populate_setting('custom_url', self.form_field.custom_url.data)
        settings['custom_path'] = self.populate_setting('custom_path', self.form_field.custom_path.data)
        settings['is_ssl'] = self.populate_setting('is_ssl', self.form_field.is_ssl.data)
        settings['method'] = self.populate_setting('method', self.form_field.method.data)
        settings['post_type'] = self.populate_setting('post_type', self.form_field.post_type.data)
        settings['custom_values'] = self.populate_setting('custom_values', self.form_field.custom_values.data)

    def populate_from_settings(self, id):
        EditNotificationForm.populate_from_settings(self, id)

        self.form_field.custom_url.data = self.populate_from_setting(id, 'custom_url')
        self.form_field.custom_path.data = self.populate_from_setting(id, 'custom_path')
        self.form_field.is_ssl.data = self.populate_from_setting(id, 'is_ssl')
        self.form_field.method.data = self.populate_from_setting(id, 'method')
        self.form_field.post_type.data = self.populate_from_setting(id, 'post_type')

        custom = self.populate_from_setting(id, 'custom_values')

        if custom is not None:
            custom = ast.literal_eval(custom)
            custom = dict((str(i['custom_key']), i['custom_value']) for i in custom)

            for key, value in custom.iteritems():
                CVForm = CustomValueForm()
                CVForm.custom_key = key
                CVForm.custom_value = value

                self.form_field.custom_values.append_entry(CVForm)


class ZoneFilterForm(Form):
    zones = SelectMultipleField(choices=[], coerce=str)
    submit = SubmitField(u'Next')
    cancel = ButtonField(u'Cancel', onclick="location.href='/settings/notifications'")

    def populate_settings(self, settings, id=None):
        settings['zone_filter'] = self.populate_setting('zone_filter', json.dumps(self.zones.data))

    def populate_from_settings(self, id):
        zone_filters = self.populate_from_setting(id, 'zone_filter')
        if zone_filters:
            self.zones.data = [str(k) for k in json.loads(zone_filters)]

    def populate_setting(self, name, value, id=None):
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


class ReviewNotificationForm(Form):
    buttons = FormField(NotificationButtonForm)
