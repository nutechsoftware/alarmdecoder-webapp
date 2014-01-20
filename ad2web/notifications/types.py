# -*- coding: utf-8 -*-

import smtplib
from email.mime.text import MIMEText
import sleekxmpp

from .constants import EMAIL, GOOGLETALK
from .models import Notification, NotificationSetting

class NotificationFactory(object):
    @classmethod
    def create(cls, id):
        db_object = Notification.query.filter_by(id=id).first()

        return TYPE_MAP[db_object.type](db_object)

    @classmethod
    def notifications(cls):
        return [obj.id for obj in Notification.query.all()]

class EmailNotification(object):
    def __init__(self, obj):
        self.id = obj.id
        self.description = obj.description
        self.source = obj.settings['source'].value
        self.destination = obj.settings['destination'].value
        self.server = obj.settings['server'].value
        self.username = obj.settings['username'].value
        self.password = obj.settings['password'].value

    def send(self, text):
        try:
            msg = MIMEText(text)

            msg['Subject'] = 'Test'
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

class GoogleTalkNotification(object):
    def __init__(self, obj):
        self.id = obj.id
        self.description = obj.description
        self.source = obj.settings['source'].value
        self.password = obj.settings['password'].value
        self.destination = obj.settings['destination'].value
        self.client = None

    def send(self, text):
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
