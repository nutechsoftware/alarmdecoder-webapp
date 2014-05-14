# -*- coding: utf-8 -*-

from flask import current_app
import smtplib
from email.mime.text import MIMEText
import sleekxmpp
import json

from .constants import EMAIL, GOOGLETALK, DEFAULT_EVENT_MESSAGES
from .models import Notification, NotificationSetting, NotificationMessage
from ..extensions import db
from ..log.models import EventLogEntry
from ..zones import Zone

class NotificationSystem(object):
    def __init__(self):
        self._notifiers = []
        self._messages = DEFAULT_EVENT_MESSAGES

        self._init_notifiers()
        self._init_messages()

    def send(self, type, **kwargs):
        for n in self._notifiers:
            if n.subscribes_to(type):
                message = self._build_message(type, **kwargs)

                if message:
                    n.send(type, message)

    def _init_notifiers(self):
        self._notifiers = [LogNotification()]   # Force LogNotification to always be present

        for n in Notification.query.all():
            self._notifiers.append(TYPE_MAP[n.type](n))

    def _init_messages(self):
        messages = NotificationMessage.query.all()

        for m in messages:
            self._messages[m.id] = m.text

    def _build_message(self, type, **kwargs):
        message = self._messages.get(type, None)

        if 'zone' in kwargs:
            zone_name = Zone.get_name(kwargs['zone'])
            kwargs['zone_name'] = zone_name if zone_name else '<unnamed>'

        if message:
            message = message.format(**kwargs)

        return message

class BaseNotification(object):
    def __init__(self, obj):
        if 'subscriptions' in obj.settings.keys():
            self._subscriptions = {int(k): v for k, v in json.loads(obj.settings['subscriptions'].value).iteritems()}
        else:
            self._subscriptions = {}

    def subscribes_to(self, type, value=None):
        if type in self._subscriptions.keys():
            return True

        return False

class LogNotification(object):
    def __init__(self):
        pass

    def subscribes_to(self, type):
        return True

    def send(self, type, text):
        with current_app.app_context():
            current_app.logger.info('Event: {0}'.format(text))

        db.session.add(EventLogEntry(type=type, message=text))
        db.session.commit()

class EmailNotification(BaseNotification):
    def __init__(self, obj):
        BaseNotification.__init__(self, obj)

        self.id = obj.id
        self.description = obj.description
        self.source = obj.settings['source'].value
        self.destination = obj.settings['destination'].value
        self.server = obj.settings['server'].value
        self.username = obj.settings['username'].value
        self.password = obj.settings['password'].value

    def send(self, type, text):
        try:
            msg = MIMEText(text)

            msg['Subject'] = 'AlarmDecoder: Alarm Event'
            msg['From'] = self.source
            msg['To'] = self.destination #', '.join(self.destination)

            s = smtplib.SMTP(self.server)

            if self.username != '':
                s.login(self.username, self.password)

            s.sendmail(self.source, self.destination, msg.as_string())
            s.quit()
        except smtplib.SMTPException, err:
            import traceback
            traceback.print_exc()

class GoogleTalkNotification(BaseNotification):
    def __init__(self, obj):
        BaseNotification.__init__(self)

        self.id = obj.id
        self.description = obj.description
        self.source = obj.settings['source'].value
        self.password = obj.settings['password'].value
        self.destination = obj.settings['destination'].value
        self.client = None

    def send(self, type, text):
        self.msg_to_send = text
        try:
            self.client = sleekxmpp.ClientXMPP(self.source, self.password)
            self.client.add_event_handler("session_start", self._send)

            self.client.connect(('talk.google.com', 5222))
            self.client.process(block=True)

        except Exception, err:
            import traceback
            traceback.print_exc()

    def _send(self, event):
        try:
            self.client.send_presence()
            self.client.get_roster()

            self.client.send_message(mto=self.destination, mbody=self.msg_to_send)

            self.client.disconnect(wait=True)

        except Exception, err:
            import traceback
            traceback.print_exc()

TYPE_MAP = {
    EMAIL: EmailNotification,
    GOOGLETALK: GoogleTalkNotification
}
