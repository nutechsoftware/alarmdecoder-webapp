# -*- coding: utf-8 -*-

from flask import current_app
import smtplib
from email.mime.text import MIMEText
import sleekxmpp
import json
import re
try:
    from chump import Application
    have_chump = True
except ImportError:
    have_chump = False

try:
    import twilio
    from twilio.rest import TwilioRestClient

    have_twilio = True
except ImportError:
    have_twilio = False

import time

from xml.dom.minidom import parseString
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import tostring
import ast

#https connection support - used for nma and prowl, also future POST to custom url
try:
    from http.client import HTTPSConnection
except ImportError:
    from httplib import HTTPSConnection


#normal http connection support (future POST to custom url)
try:
    from http.client import HTTPConnection
except ImportError:
    from httplib import HTTPConnection

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

import logging
try:
    import gntp.notifier
    have_gntp = True
except ImportError:
    have_gntp = False

from .constants import (EMAIL, GOOGLETALK, DEFAULT_EVENT_MESSAGES, PUSHOVER, TWILIO, NMA, NMA_URL, NMA_PATH, NMA_EVENT, NMA_METHOD,
                        NMA_CONTENT_TYPE, NMA_HEADER_CONTENT_TYPE, NMA_USER_AGENT, PROWL, PROWL_URL, PROWL_PATH, PROWL_EVENT, PROWL_METHOD,
                        PROWL_CONTENT_TYPE, PROWL_HEADER_CONTENT_TYPE, PROWL_USER_AGENT, GROWL_APP_NAME, GROWL_DEFAULT_NOTIFICATIONS,
                        GROWL_PRIORITIES, GROWL, CUSTOM, URLENCODE, JSON, XML, CUSTOM_CONTENT_TYPES, CUSTOM_USER_AGENT, CUSTOM_METHOD,
                        ZONE_FAULT, ZONE_RESTORE, BYPASS, CUSTOM_METHOD_GET, CUSTOM_METHOD_POST, CUSTOM_METHOD_GET_TYPE )

from .models import Notification, NotificationSetting, NotificationMessage
from ..extensions import db
from ..log.models import EventLogEntry
from ..zones import Zone


class NotificationSystem(object):
    def __init__(self):
        self._notifiers = {}
        self._messages = DEFAULT_EVENT_MESSAGES

        self._init_notifiers()

    def send(self, type, **kwargs):
        errors = []

        for id, n in self._notifiers.iteritems():
            if n and n.subscribes_to(type, **kwargs):
                try:
                    message = self._build_message(type, **kwargs)

                    if message:
                        n.send(type, message)

                except Exception, err:
                    errors.append('Error sending notification for {0}: {1}'.format(n.description, str(err)))

        return errors

    def refresh_notifier(self, id):
        n = Notification.query.filter_by(id=id).first()
        if n:
            self._notifiers[id] = TYPE_MAP[n.type](n)
        else:
            try:
                del self._notifiers[id]
            except KeyError:
                pass

    def test_notifier(self, id):
        try:
            n = self._notifiers.get(id)
            if n:
                n.send(None, 'Test Notification')

        except Exception, err:
            return str(err)
        else:
            return None

    def _init_notifiers(self):
        self._notifiers = {-1: LogNotification()}   # Force LogNotification to always be present

        for n in Notification.query.all():
            self._notifiers[n.id] = TYPE_MAP[n.type](n)

    def _build_message(self, type, **kwargs):
        message = NotificationMessage.query.filter_by(id=type).first()
        if message:
            message = message.text

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

        if 'zone_filter' in obj.settings.keys():
            self._zone_filters = [int(k) for k in json.loads(obj.settings['zone_filter'].value)]
        else:
            self._zone_filters = []

    def subscribes_to(self, type, **kwargs):
        if type in self._subscriptions.keys():
            if type in (ZONE_FAULT, ZONE_RESTORE, BYPASS):
                if int(kwargs.get('zone', -1)) in self._zone_filters:
                    return True
                else:
                    return False

            return True

        return False

class LogNotification(object):
    def __init__(self):
        self.description = 'Logger'

    def subscribes_to(self, type, **kwargs):
        return True

    def send(self, type, text):
        with current_app.app_context():
            if type == ZONE_RESTORE or type == ZONE_FAULT or type == BYPASS:
                current_app.logger.debug('Event: {0}'.format(text))
            else:
                current_app.logger.info('Event: {0}'.format(text))

        db.session.add(EventLogEntry(type=type, message=text))
        db.session.commit()

class EmailNotification(BaseNotification):
    def __init__(self, obj):
        BaseNotification.__init__(self, obj)

        self.id = obj.id
        self.description = obj.description
        self.source = obj.get_setting('source')
        self.destination = obj.get_setting('destination')
        self.subject = obj.get_setting('subject')
        self.server = obj.get_setting('server')
        self.port = obj.get_setting('port', default=25)
        self.tls = obj.get_setting('tls', default=False)
        self.authentication_required = obj.get_setting('authentication_required', default=False)
        self.username = obj.get_setting('username')
        self.password = obj.get_setting('password')

    def send(self, type, text):
        message_timestamp = time.ctime(time.time())
        text = text + " Message Sent at: " + message_timestamp

        msg = MIMEText(text)

        msg['Subject'] = self.subject
        msg['From'] = self.source
        recipients = re.split('\s*;\s*|\s*,\s*', self.destination)
        msg['To'] = ', '.join(recipients)

        s = smtplib.SMTP(self.server, self.port)
        if self.tls:
            s.starttls()

        if self.authentication_required:
            s.login(str(self.username), str(self.password))

        s.sendmail(self.source, recipients, msg.as_string())
        s.quit()


class GoogleTalkNotification(BaseNotification):
    def __init__(self, obj):
        BaseNotification.__init__(self, obj)

        self.id = obj.id
        self.description = obj.description
        self.source = obj.get_setting('source')
        self.password = obj.get_setting('password')
        self.destination = obj.get_setting('destination')
        self.client = None

    def send(self, type, text):
        message_timestamp = time.ctime(time.time())
        self.msg_to_send = text + " Message Sent at: " + message_timestamp
        self.client = sleekxmpp.ClientXMPP(self.source, self.password)
        self.client.add_event_handler("session_start", self._send)

        self.client.connect(('talk.google.com', 5222))
        self.client.process(block=True)

    def _send(self, event):
        self.client.send_presence()
        self.client.get_roster()

        self.client.send_message(mto=self.destination, mbody=self.msg_to_send)
        self.client.disconnect(wait=True)

class PushoverNotification(BaseNotification):
    def __init__(self, obj):
        BaseNotification.__init__(self, obj)

        self.id = obj.id
        self.description = obj.description
        self.token = obj.get_setting('token')
        self.user_key = obj.get_setting('user_key')
        self.priority = obj.get_setting('priority')
        self.title = obj.get_setting('title')

    def send(self, type, text):
        self.msg_to_send = text

        if not have_chump:
            raise Exception('Missing Pushover library: chump')

        app = Application(self.token)
        if app.is_authenticated:
            user = app.get_user(self.user_key)

            if user.is_authenticated:
                message = user.create_message(
                    title=self.title,
                    message=self.msg_to_send,
                    html=True,
                    priority=self.priority,
                    timestamp=int(time.time())
                )

                is_sent = message.send()

                if is_sent != True:
                    current_app.logger.info("Pushover Notification Failed")
                    raise Exception('Pushover Notification Failed')
            else:
                current_app.logger.info("Pushover Notification Failed - bad user key: " + self.user_key)
                raise Exception("Pushover Notification Failed - bad user key: " + self.user_key)

        else:
            current_app.logger.info("Pushover Notification Failed - bad application token: " + self.token)
            raise Exception("Pushover Notification Failed - bad application token: " + self.token)


class TwilioNotification(BaseNotification):
    def __init__(self, obj):
        BaseNotification.__init__(self, obj)

        self.id = obj.id
        self.description = obj.description
        self.account_sid = obj.get_setting('account_sid')
        self.auth_token = obj.get_setting('auth_token')
        self.number_to = obj.get_setting('number_to')
        self.number_from = obj.get_setting('number_from')

    def send(self, type, text):
        message_timestamp = time.ctime(time.time())
        self.msg_to_send = text + " Message Sent at: " + message_timestamp

        if have_twilio == False:
            raise Exception('Missing Twilio library: twilio')

        try:
            client = TwilioRestClient(self.account_sid, self.auth_token)
            message = client.messages.create(to=self.number_to, from_=self.number_from, body=self.msg_to_send)
        except twilio.TwilioRestException as e:
            current_app.logger.info('Event Twilio Notification Failed: {0}' . format(e))
            raise Exception('Twilio Notification Failed: {0}' . format(e))

class NMANotification(BaseNotification):
    def __init__(self, obj):
        BaseNotification.__init__(self, obj)
        self.id = obj.id
        self.description = obj.description
        self.api_key = obj.get_setting('api_key')
        self.app_name = obj.get_setting('app_name')
        self.priority = obj.get_setting('nma_priority')

    def send(self, type, text):
        message_timestamp = time.ctime(time.time())
        self.msg_to_send = text[:10000].encode('utf8') + " Message Sent at: " + message_timestamp
        self.event = NMA_EVENT.encode('utf8')
        self.content_type = NMA_CONTENT_TYPE

        notify_data = {
            'application': self.app_name,
            'description': self.msg_to_send,
            'event': self.event,
            'priority': self.priority,
            'content-type': self.content_type,
            'apikey': self.api_key
        }

        headers = { 'User-Agent': NMA_USER_AGENT }
        headers['Content-type'] = NMA_HEADER_CONTENT_TYPE
        http_handler = HTTPSConnection(NMA_URL)
        http_handler.request(NMA_METHOD, NMA_PATH, urlencode(notify_data), headers)

        http_response = http_handler.getresponse()

        try:
            res = self._parse_response(http_response.read())
        except Exception as e:
            res = {
                'type': 'NMA Notify Error',
                'code': 800,
                'message': str(e)
            }
            current_app.logger.info('Event NotifyMyAndroid Notification Failed: {0}'.format(str(e)))
            raise Exception('NotifyMyAndroid Failed: {0}' . format(str(e)))

    def _parse_response(self, response):
        root = parseString(response).firstChild

        for elem in root.childNodes:
            if elem.nodeType == elem.TEXT_NODE: continue
            if elem.tagName == 'success':
                res = dict(list(elem.attributes.items()))
                res['message'] = ""
                res['type'] = elem.tagName

                return res

            if elem.tagName == 'error':
                res = dict(list(elem.attributes.items()))
                res['message'] = elem.firstChild.nodeValue
                res['type'] = elem.tagName
                current_app.logger.info('Event NotifyMyAndroid Notification Failed: {0}'.format(res['message']))
                raise Exception(res['message'])

class ProwlNotification(BaseNotification):
    def __init__(self, obj):
        BaseNotification.__init__(self, obj)
        self.id = obj.id
        self.description = obj.description
        self.api_key = obj.get_setting('prowl_api_key')
        self.app_name = obj.get_setting('prowl_app_name')[:256].encode('utf8')
        self.priority = obj.get_setting('prowl_priority')
        self.event = PROWL_EVENT[:1024].encode('utf8')
        self.content_type = PROWL_CONTENT_TYPE
        self.headers = {
            'User-Agent': PROWL_USER_AGENT,
            'Content-type': PROWL_HEADER_CONTENT_TYPE
        }

    def send(self, type, text):
        message_timestamp = time.ctime(time.time())
        self.msg_to_send = text[:10000].encode('utf8') + " Message Sent at: " + message_timestamp

        notify_data = {
            'apikey': self.api_key,
            'application': self.app_name,
            'event': self.event,
            'description': self.msg_to_send,
            'priority': self.priority
        }

        http_handler = HTTPSConnection(PROWL_URL)
        http_handler.request(PROWL_METHOD, PROWL_PATH, headers=self.headers,body=urlencode(notify_data))

        http_response = http_handler.getresponse()

        if http_response.status == 200:
            return True
        else:
            current_app.logger.info('Event Prowl Notification Failed: {0}'. format(http_response.reason))
            raise Exception('Prowl Notification Failed: {0}' . format(http_response.reason))

class GrowlNotification(BaseNotification):
    def __init__(self, obj):
        BaseNotification.__init__(self, obj)
        self.id = obj.id
        self.description = obj.description
        self.priority = obj.get_setting('growl_priority')
        self.hostname = obj.get_setting('growl_hostname')
        self.port = obj.get_setting('growl_port')
        self.password = obj.get_setting('growl_password')

        if self.password == '':
            self.password = None

        self.title = obj.get_setting('growl_title')

        if have_gntp:
            self.growl = gntp.notifier.GrowlNotifier(
                applicationName = GROWL_APP_NAME,
                notifications = GROWL_DEFAULT_NOTIFICATIONS,
                defaultNotifications = GROWL_DEFAULT_NOTIFICATIONS,
                hostname = self.hostname,
                password = self.password
            )
        else:
            self.growl = None
        
    def send(self, type, text):
        message_timestamp = time.ctime(time.time())
        self.msg_to_send = text + " Message Sent at: " + message_timestamp

        if not have_gntp:
            raise Exception('Missing Growl library: gntp')

        growl_status = self.growl.register()
        if growl_status == True:
            growl_notify_status = self.growl.notify(
                noteType = GROWL_DEFAULT_NOTIFICATIONS[0],
                title = self.title,
                description = self.msg_to_send,
                priority = self.priority,
                sticky = False
            )
            if growl_notify_status != True:
                current_app.logger.info('Event Growl Notification Failed: {0}' . format(growl_notify_status))
                raise Exception('Growl Notification Failed: {0}' . format(growl_notify_status))

        else:
            current_app.logger.info('Event Growl Notification Failed: {0}' . format(growl_status))
            raise Exception('Growl Notification Failed: {0}' . format(growl_status))

class CustomNotification(BaseNotification):
    def __init__(self, obj):
        BaseNotification.__init__(self, obj)
        self.id = obj.id
        self.description = obj.description
        self.url = obj.get_setting('custom_url')
        self.path = obj.get_setting('custom_path')
        self.is_ssl = obj.get_setting('is_ssl')
        self.post_type = obj.get_setting('post_type')
        self.custom_values = obj.get_setting('custom_values')
        self.content_type = CUSTOM_CONTENT_TYPES[self.post_type]
        self.method = obj.get_setting('method')

        self.headers = {
            'User-Agent': CUSTOM_USER_AGENT,
            'Content-type': self.content_type
        }

    def _dict_to_xml(self,tag, d):
        el = Element(tag)
        for key, val in d.items():
            child = Element(key)
            child.text = str(val)
            el.append(child)

        return tostring(el)

    def _dict_to_json(self, d):
        return json.dumps(d)

    def _do_post(self, data):
        if self.is_ssl:
            http_handler = HTTPSConnection(self.url)
        else:
            http_handler = HTTPConnection(self.url)

        http_handler.request(CUSTOM_METHOD, self.path, headers=self.headers, body=data)
        http_response = http_handler.getresponse()

        if http_response.status == 200:
            return True
        else:
            current_app.logger.info('Event Custom Notification Failed')
            raise Exception('Custom Notification Failed')

    def _do_get(self, data):
        if self.is_ssl:
            http_handler = HTTPSConnection(self.url)
        else:
            http_handler = HTTPConnection(self.url)

        get_path = self.path + '?' + data
        http_handler.request(CUSTOM_METHOD_GET, get_path, headers=self.headers)
        http_response = http_handler.getresponse()

        if http_response.status == 200:
            return True
        else:
            current_app.logger.info('Event Custom Notification Failed on GET method')
            raise Exception('Custom Notification Failed')

    def send(self, type, text):
        self.msg_to_send = text

        notify_data = {}
        if self.custom_values is not None:
            if self.custom_values:
                try:
                    self.custom_values = ast.literal_eval(self.custom_values)
                except ValueError:
                    pass

                notify_data = dict((str(i['custom_key']), i['custom_value']) for i in self.custom_values)

        result = False

        if self.method == CUSTOM_METHOD_POST:
            if self.post_type == URLENCODE:
               result =  self._do_post(urlencode(notify_data))

            if self.post_type == XML:
               result =  self._do_post(self._dict_to_xml('notification', notify_data))

            if self.post_type == JSON:
                result = self._do_post(self._dict_to_json(notify_data) )

        if self.method == CUSTOM_METHOD_GET_TYPE:
            if self.post_type == URLENCODE:
                result = self._do_get(urlencode(notify_data))

            #only allow urlencoding on GET requests
            if self.post_type == XML:
                return False

            if self.post_type == JSON:
                return False

        return result

TYPE_MAP = {
    EMAIL: EmailNotification,
    GOOGLETALK: GoogleTalkNotification,
    PUSHOVER: PushoverNotification,
    TWILIO: TwilioNotification,
    NMA: NMANotification,
    PROWL: ProwlNotification,
    GROWL: GrowlNotification,
    CUSTOM: CustomNotification
}
