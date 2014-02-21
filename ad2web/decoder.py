# -*- coding: utf-8 -*-

from gevent import monkey
monkey.patch_all()

import time
import traceback

from socketio import socketio_manage
from socketio.namespace import BaseNamespace
from socketio.mixins import BroadcastMixin
from socketio.server import SocketIOServer

from flask import Blueprint, Response, request, g, current_app
import jsonpickle

from OpenSSL import SSL
from alarmdecoder import AlarmDecoder
from alarmdecoder.devices import SocketDevice, SerialDevice
from alarmdecoder.util import NoDeviceError, CommError

from .log.models import EventLogEntry
from .log.constants import *
from .extensions import db
from .notifications import NotificationFactory
from .zones import Zone
from .settings.models import Setting
from .certificate.models import Certificate

CRITICAL_EVENTS = [POWER_CHANGED, ALARM, BYPASS, ARM, DISARM, ZONE_FAULT, \
                    ZONE_RESTORE, FIRE, PANIC]

EVENTS = {
    ARM: 'on_arm',
    DISARM: 'on_disarm',
    POWER_CHANGED: 'on_power_changed',
    ALARM: 'on_alarm',
    FIRE: 'on_fire',
    BYPASS: 'on_bypass',
    BOOT: 'on_boot',
    CONFIG_RECEIVED: 'on_config_received',
    ZONE_FAULT: 'on_zone_fault',
    ZONE_RESTORE: 'on_zone_restore',
    LOW_BATTERY: 'on_low_battery',
    PANIC: 'on_panic',
    RELAY_CHANGED: 'on_relay_changed'
}

EVENT_MESSAGES = {
    ARM: 'The alarm was armed.',
    DISARM: 'The alarm was disarmed.',
    POWER_CHANGED: 'Power status has changed to {status}.',
    ALARM: 'Alarming!  Oh no!',
    FIRE: 'Fire!  Oh no!',
    BYPASS: '{zone_name} ({zone}) has been bypassed.',
    BOOT: 'The AlarmDecoder has finished booting.',
    CONFIG_RECEIVED: 'AlarmDecoder has been configuratorized.',
    ZONE_FAULT: '{zone_name} ({zone}) has been faulted.',
    ZONE_RESTORE: '{zone_name} ({zone}) has been restored.',
    LOW_BATTERY: 'Low battery detected.  You should probably mount it higher.',
    PANIC: 'Panic!  Ants are invading the pantry!',
    RELAY_CHANGED: 'Some relay or another has changed.'
}

decodersocket = Blueprint('sock', __name__, url_prefix='/socket.io')

def create_decoder_socket(app):
    return SocketIOServer(('', 5000), app, resource="socket.io")

class Decoder(object):
    def __init__(self, app, websocket):
        self.app = app
        self.websocket = websocket
        self.device = None
        self._last_message = None
        self._device_baudrate = 115200
        self._device_type = None
        self._device_location = None

    def open(self):
        self._device_type = Setting.get_by_name('device_type').value
        self._device_location = Setting.get_by_name('device_location').value

        # TODO: make this not ugly.
        interface = ('localhost', 10000)
        use_ssl = False
        devicetype = SocketDevice
        if self._device_location == 'local':
            devicetype = SerialDevice
            interface = Setting.get_by_name('device_path').value
            self._device_baudrate = Setting.get_by_name('device_baudrate').value
        elif self._device_location == 'network':
            interface = (Setting.get_by_name('device_address').value, Setting.get_by_name('device_port').value)

            use_ssl = Setting.get_by_name('use_ssl').value
            if use_ssl is None:
                use_ssl = False

        try:
            device = devicetype(interface=interface)
            if self._device_location == 'network' and use_ssl:
                ca_cert = Certificate.query.filter_by(name='AlarmDecoder CA').one()
                internal_cert = Certificate.query.filter_by(name='AlarmDecoder Internal').one()

                device.ssl = True
                device.ssl_ca = ca_cert.certificate_obj
                device.ssl_certificate = internal_cert.certificate_obj
                device.ssl_key = internal_cert.key_obj

            self.device = AlarmDecoder(device)
            self.bind_events(self.websocket, self.device)
            self.device.open(baudrate=self._device_baudrate)

        except NoDeviceError, err:
            self.app.logger.warning('Open failed: %s', err[0], exc_info=True)

        except SSL.Error, err:
            source, fn, message = err[0][0]
            self.app.logger.warning('SSL connection failed: %s - %s', fn, message, exc_info=True)

    def close(self):
        if self.device is not None:
            self.device.close()

    def bind_events(self, appsocket, decoder):
        build_event_handler = lambda ftype: lambda sender, *args, **kwargs: self._handle_event(ftype, sender, *args, **kwargs)

        self.device.on_message += self._on_message
        self.device.on_lrr_message += self._on_message
        self.device.on_rfx_message += self._on_message
        self.device.on_expander_message += self._on_message

        self.device.on_open += self._on_device_open
        self.device.on_close += self._on_device_close

        # Bind the event handler to all of our events.
        for event, device_event_name in EVENTS.iteritems():
            device_handler = getattr(self.device, device_event_name)
            device_handler += build_event_handler(event)

    def _on_device_open(self, sender):
        self.app.logger.debug('device_open')
        self.broadcast('device_open')

    def _on_device_close(self, sender):
        self.app.logger.debug('device_close')
        self.broadcast('device_close')

        # TODO: try to reopen

    def _on_message(self, sender, *args, **kwargs):
        try:
            self.broadcast('message', kwargs.get('message', None))

        except Exception, err:
            self.app.logger.error('Error while broadcasting message.', exc_info=True)

    def _handle_event(self, ftype, sender, *args, **kwargs):
        try:
            self._last_message = time.time()

            with self.app.app_context():
                if 'zone' in kwargs:
                    zone_name = Zone.get_name(kwargs['zone'])
                    kwargs['zone_name'] = zone_name if zone_name else '<unnamed>'

                event_message = EVENT_MESSAGES[ftype].format(**kwargs)
                if ftype in CRITICAL_EVENTS:
                    for id in NotificationFactory.notifications():
                        notifier = NotificationFactory.create(id)
                        notifier.send('AlarmDecoder Event: {0}'.format(event_message))

                db.session.add(EventLogEntry(type=ftype, message=event_message))
                db.session.commit()

            self.broadcast('event', kwargs)

        except Exception, err:
            self.app.logger.error('Error while broadcasting event.', exc_info=True)

    def broadcast(self, channel, data={}):
        obj = jsonpickle.encode(data, unpicklable=False)
        packet = self._make_packet(channel, obj)

        self._broadcast_packet(packet)

    def _broadcast_packet(self, packet):
        for session, sock in self.websocket.sockets.iteritems():
            sock.send_packet(packet)

    def _make_packet(self, channel, data):
        return dict(type='event', name=channel, args=data, endpoint='/alarmdecoder')

class DecoderNamespace(BaseNamespace, BroadcastMixin):
    def initialize(self):
        self._alarmdecoder = self.request

    def on_keypress(self, key):
        with self._alarmdecoder.app.app_context():
            try:
                if key == 1:
                    self._alarmdecoder.device.send(AlarmDecoder.KEY_F1)
                elif key == 2:
                    self._alarmdecoder.device.send(AlarmDecoder.KEY_F2)
                elif key == 3:
                    self._alarmdecoder.device.send(AlarmDecoder.KEY_F3)
                elif key == 4:
                    self._alarmdecoder.device.send(AlarmDecoder.KEY_F4)
                else:
                    self._alarmdecoder.device.send(key)
            except CommError, err:
                self.app.logger.error('Error sending keypress to device', exc_info=True)

    def on_test(self, *args):
        with self._alarmdecoder.app.app_context():
            def on_config(device):
                self._alarmdecoder.broadcast('test', {'test': 'config', 'results': 'PASS'})
                self._alarmdecoder.device.on_config_received.remove(on_config)

            results = 'FAIL'
            try:
                self._alarmdecoder.close()
                self._alarmdecoder.open()
                results = 'PASS'
            except Exception, err:
                self.app.logger.error('Error while testing device open.', exc_info=True)
            finally:
                self._alarmdecoder.broadcast('test', {'test': 'open', 'results': results})

            try:
                self._alarmdecoder.device.on_config_received += on_config
                self._alarmdecoder.device.send("C\r")
            except Exception, err:
                self.app.logger.error('Error while testing device config.', exc_info=True)
                self._alarmdecoder.broadcast('test', {'test': 'config', 'results': 'FAIL'})

@decodersocket.route('/<path:remaining>')
def handle_socketio(remaining):
    try:
        socketio_manage(request.environ, {'/alarmdecoder': DecoderNamespace}, g.alarmdecoder)

    except Exception, err:
        current_app.logger.error("Exception while handling socketio connection", exc_info=True)

    return Response()
