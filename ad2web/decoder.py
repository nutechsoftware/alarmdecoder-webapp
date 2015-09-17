# -*- coding: utf-8 -*-

import os
import sys
import time
import traceback
import threading

from socketio import socketio_manage
from socketio.namespace import BaseNamespace
from socketio.mixins import BroadcastMixin
from socketio.server import SocketIOServer
from socketioflaskdebug.debugger import SocketIODebugger

from flask import Blueprint, Response, request, g, current_app
import jsonpickle

from OpenSSL import SSL
from alarmdecoder import AlarmDecoder
from alarmdecoder.devices import SocketDevice, SerialDevice
from alarmdecoder.util import NoDeviceError, CommError

from .extensions import db
from .notifications import NotificationSystem
from .settings.models import Setting
from .certificate.models import Certificate
from .updater import Updater

from .notifications.models import NotificationMessage
from .notifications.constants import (ARM, DISARM, POWER_CHANGED, ALARM, ALARM_RESTORED,
                                        FIRE, BYPASS, BOOT, CONFIG_RECEIVED, ZONE_FAULT,
                                        ZONE_RESTORE, LOW_BATTERY, PANIC, RELAY_CHANGED,
                                        DEFAULT_EVENT_MESSAGES)

from .cameras import CameraSystem
from .cameras.models import Camera


EVENT_MAP = {
    ARM: 'on_arm',
    DISARM: 'on_disarm',
    POWER_CHANGED: 'on_power_changed',
    ALARM: 'on_alarm',
    ALARM_RESTORED: 'on_alarm_restored',
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

decodersocket = Blueprint('sock', __name__, url_prefix='/socket.io')

def create_decoder_socket(app):
    debugged_app = SocketIODebugger(app, namespace=DecoderNamespace)

    return SocketIOServer(('', 5000), debugged_app, resource="socket.io")

class Decoder(object):
    """
    Primary application state
    """

    def __init__(self, app, websocket):
        """
        Constructor

        :param app: The flask application object
        :type app: Flask
        :param websocket: The websocket object
        :type websocket: SocketIOServer
        """
        with app.app_context():
            self.app = app
            self.websocket = websocket
            self.device = None
            self.updater = Updater()
            self.updates = {}
            self.version = ''

            self.trigger_reopen_device = False
            self.trigger_restart = False

            self._last_message = None
            self._device_baudrate = 115200
            self._device_type = None
            self._device_location = None
            self._event_thread = DecoderThread(self)
            self._version_thread = VersionChecker(self)
            self._notifier_system = None
            self._internal_address_mask = 0xFFFFFFFF

    @property
    def internal_address_mask(self):
        return self._internal_address_mask

    @internal_address_mask.setter
    def internal_address_mask(self, mask):
        self._internal_address_mask = int(mask, 16)
        if self.device is not None:
            self.device.internal_address_mask = int(mask, 16)

    def start(self):
        """
        Starts the internal threads.
        """
        self._event_thread.start()
        self._version_thread.start()
        self._camera_thread.start()

    def stop(self, restart=False):
        """
        Closes the device, stops the internal threads, and shuts down.  Optionally
        triggers a restart of the application.

        :param restart: Indicates whether or not the application should be restarted.
        :type restart: bool
        """
        self.app.logger.info('Stopping service..')

        self.close()

        self._event_thread.stop()
        self._version_thread.stop()
        self._camera_thread.stop()

        if restart:
            try:
                self._event_thread.join(5)
                self._version_thread.join(5)
                self._camera_thread.join(5)
            except RuntimeError:
                pass

        self.websocket.stop()

        if restart:
            self.app.logger.info('Restarting service..')
            os.execv(sys.executable, [sys.executable] + sys.argv)

    def init(self):
        """
        Initializes the application by triggering a device open if it's been
        previously configured.
        """
        with self.app.app_context():
            device_type = Setting.get_by_name('device_type').value

            # Add any default event messages that may be missing due to additions.
            for event, message in DEFAULT_EVENT_MESSAGES.iteritems():
                if not NotificationMessage.query.filter_by(id=event).first():
                    db.session.add(NotificationMessage(id=event, text=message))
            db.session.commit()

            self.version = self.updater._components['webapp'].version
            current_app.jinja_env.globals['version'] = self.version

            current_app.logger.info('AlarmDecoder Webapp booting up - v{0}'.format(self.version))

            # HACK: giant hack.. fix when we know this works.
            self.updater._components['webapp']._db_updater.refresh()

            if self.updater._components['webapp']._db_updater.needs_update:
                current_app.logger.debug('Database needs updating!')

                self.updater._components['webapp']._db_updater.update()
            else:
                current_app.logger.debug('Database is good!')

            if device_type:
                self.trigger_reopen_device = True

            self._notifier_system = NotificationSystem()
            self._camera_thread = CameraChecker(self)

    def open(self):
        """
        Opens the AlarmDecoder device.
        """
        with self.app.app_context():
            self._device_type = Setting.get_by_name('device_type').value
            self._device_location = Setting.get_by_name('device_location').value
            self._internal_address_mask = int(Setting.get_by_name('internal_address_mask', 'FFFFFFF').value, 16)

            if self._device_type:
                interface = ('localhost', 10000)
                use_ssl = False
                devicetype = SocketDevice

                # Set up device interfaces based on our location.
                if self._device_location == 'local':
                    devicetype = SerialDevice
                    interface = Setting.get_by_name('device_path').value
                    self._device_baudrate = Setting.get_by_name('device_baudrate').value

                elif self._device_location == 'network':
                    interface = (Setting.get_by_name('device_address').value, Setting.get_by_name('device_port').value)
                    use_ssl = Setting.get_by_name('use_ssl', False).value

                # Create and open the device.
                try:
                    device = devicetype(interface=interface)
                    if use_ssl:
                        ca_cert = Certificate.query.filter_by(name='AlarmDecoder CA').one()
                        internal_cert = Certificate.query.filter_by(name='AlarmDecoder Internal').one()

                        device.ssl = True
                        device.ssl_ca = ca_cert.certificate_obj
                        device.ssl_certificate = internal_cert.certificate_obj
                        device.ssl_key = internal_cert.key_obj

                    self.device = AlarmDecoder(device)
                    self.device.internal_address_mask = self._internal_address_mask

                    self.bind_events()
                    self.device.open(baudrate=self._device_baudrate)

                except NoDeviceError, err:
                    self.app.logger.warning('Open failed: %s', err[0], exc_info=True)
                    raise

                except SSL.Error, err:
                    source, fn, message = err[0][0]
                    self.app.logger.warning('SSL connection failed: %s - %s', fn, message, exc_info=True)
                    raise

    def close(self):
        """
        Closes the AlarmDecoder device.
        """
        if self.device:
            self.device.close()

    def bind_events(self):
        """
        Binds the internal event handlers so that we can handle events from the
        AlarmDecoder library.
        """
        build_event_handler = lambda ftype: lambda sender, **kwargs: self._handle_event(ftype, sender, **kwargs)
        build_message_handler = lambda ftype: lambda sender, **kwargs: self._on_message(ftype, sender, **kwargs)

        self.device.on_message += build_message_handler('panel')
        self.device.on_lrr_message += build_message_handler('lrr')
        self.device.on_rfx_message += build_message_handler('rfx')
        self.device.on_expander_message += build_message_handler('exp')

        self.device.on_open += self._on_device_open
        self.device.on_close += self._on_device_close

        # Bind the event handler to all of our events.
        for event, device_event_name in EVENT_MAP.iteritems():
            try:
                device_handler = getattr(self.device, device_event_name)
                device_handler += build_event_handler(event)

            except AttributeError, ex:
                self.app.logger.warning('Could not bind event "%s": alarmdecoder library is probably out of date.', device_event_name)

    def refresh_notifier(self, id):
        self._notifier_system.refresh_notifier(id)

    def test_notifier(self, id):
        return self._notifier_system.test_notifier(id)

    def _on_device_open(self, sender):
        """
        Internal event handler for when the device opens.

        :param sender: The AlarmDecoder device that sent the open message.
        :type sender: AlarmDecoder
        """
        self.app.logger.info('AlarmDecoder device was opened.')

        self.broadcast('device_open')
        self.trigger_reopen_device = False

    def _on_device_close(self, sender):
        """
        Internal event handler for when the device closes.

        :param sender: The AlarmDecoder device that sent the close message.
        :type sender: AlarmDecoder
        """
        self.app.logger.info('AlarmDecoder device was closed.')

        self.broadcast('device_close')
        self.trigger_reopen_device = True

    def _on_message(self, ftype, sender, **kwargs):
        """
        Internal event handler for when the device receives a message.

        :param ftype: Human-readable message type
        :type ftype: string
        :param sender: The AlarmDecoder device that sent the message.
        :type sender: AlarmDecoder
        :param args: Argument list for the message.
        :type args: list
        :param kwargs: Keyword arguments for the message.
        :type kwargs: dict
        """
        try:
            self.broadcast('message', { 'message': kwargs.get('message', None), 'message_type': ftype } )

        except Exception, err:
            self.app.logger.error('Error while broadcasting message.', exc_info=True)

    def _handle_event(self, ftype, sender, **kwargs):
        """
        Internal event handler for other events from the AlarmDecoder.

        :param ftype: Human-readable message type
        :type ftype: string
        :param sender: The AlarmDecoder device that sent the message.
        :type sender: AlarmDecoder
        :param args: Argument list for the message.
        :type args: list
        :param kwargs: Keyword arguments for the message.
        :type kwargs: dict
        """
        try:
            self._last_message = time.time()

            with self.app.app_context():
                errors = self._notifier_system.send(ftype, **kwargs)
                for e in errors:
                    self.app.logger.error(e)

            self.broadcast('event', kwargs)

        except Exception, err:
            self.app.logger.error('Error while broadcasting event.', exc_info=True)

    def broadcast(self, channel, data={}):
        """
        Broadcasts a message to all of the connected websocket clients.

        :param channel: Websocket channel
        :type channel: string
        :param data: Data to send over the websocket.
        :type data: dict
        """
        obj = jsonpickle.encode(data, unpicklable=False)
        packet = self._make_packet(channel, obj)

        self._broadcast_packet(packet)

    def _broadcast_packet(self, packet):
        """
        Broadcasts the packet to all websocket clients.

        :param packet: SocketIO packet to send.
        :type packet: dict
        """
        for session, sock in self.websocket.sockets.iteritems():
            sock.send_packet(packet)

    def _make_packet(self, channel, data):
        """
        Creates a packet to send over SocketIO.

        :param channel: Websocket channel
        :type channel: string
        :param data: JSON-encoded string to send
        :type data: string
        :returns: A dictionary representing a websocket packet
        """
        return dict(type='event', name=channel, args=data, endpoint='/alarmdecoder')

class DecoderThread(threading.Thread):
    """
    Worker thread for handling device events, specifically device reconnection.
    """

    TIMEOUT = 5
    """Thread sleep time."""

    def __init__(self, decoder):
        """
        Constructor

        :param decoder: Parent decoder object
        :type decoder: Decoder
        """
        threading.Thread.__init__(self)
        self._decoder = decoder
        self._running = False

    def stop(self):
        """
        Stops the running thread.
        """
        self._running = False

    def run(self):
        """
        The thread processing loop.
        """
        self._running = True

        while self._running:
            with self._decoder.app.app_context():
                try:
                    # Handle reopen events
                    if self._decoder.trigger_reopen_device:
                        self._decoder.app.logger.info('Attempting to reconnect to the AlarmDecoder')
                        try:
                            self._decoder.open()
                        except NoDeviceError, err:
                            self._decoder.app.logger.error('Device not found: {0}'.format(err[0]))

                    # Handle service restart events
                    if self._decoder.trigger_restart:
                        self._decoder.updates = {}
                        self._decoder.app.jinja_env.globals['update_available'] = False
                        self._decoder.app.logger.info('Restarting service..')
                        self._decoder.stop(restart=True)

                    time.sleep(self.TIMEOUT)

                except Exception, err:
                    self._decoder.app.logger.error('Error in DecoderThread: {0}'.format(err), exc_info=True)

class VersionChecker(threading.Thread):
    """
    Thread responsible for checking for new software versions.
    """
    TIMEOUT = 60 * 10
    """Version checker sleep time."""

    def __init__(self, decoder):
        """
        Constructor

        :param decoder: Parent decoder object
        :type decoder: Decoder
        """
        threading.Thread.__init__(self)
        self._decoder = decoder
        self._updater = decoder.updater
        self._running = False

    def stop(self):
        """
        Stops the thread.
        """

        self._running = False

    def run(self):
        """
        The thread processing loop.
        """
        self._running = True

        while self._running:
            with self._decoder.app.app_context():
                self._decoder.updates = self._updater.check_updates()
                update_available = not all(not needs_update for component, (needs_update, branch, revision, new_revision, status) in self._decoder.updates.iteritems())

                current_app.jinja_env.globals['update_available'] = update_available

            time.sleep(self.TIMEOUT)

class CameraChecker(threading.Thread):
    """
    Thread responsible for polling camera streams.
    """
    TIMEOUT = 1
    """Camera checker thread sleep time."""

    def __init__(self, decoder):
        """
        Constructor
        :param decoder: Parent decoder object
        :type decoder: Decoder
        """
        threading.Thread.__init__(self)
        self._decoder = decoder
        self._running = False
        self._cameras = CameraSystem()

    def stop(self):
        """
        Stops the thread.
        """
        self._running = False

    def run(self):
        """
        The thread processing loop.
        """
        self._running = True

        while self._running:
            with self._decoder.app.app_context():
                self._cameras.refresh_camera_ids()
                for n in self._cameras.get_camera_ids():
                    self._cameras.write_image(n)

            time.sleep(self.TIMEOUT)
        
class DecoderNamespace(BaseNamespace, BroadcastMixin):
    """
    Socket.IO namespace
    """

    def initialize(self):
        """
        Initializes the namespace.
        """
        self._alarmdecoder = self.request

    def on_keypress(self, key):
        """
        Handles websocket keypress events.

        :param key: The key that was pressed.
        :type key: int or string
        """
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
                elif key == 5:
                    self._alarmdecoder.device.send(AlarmDecoder.KEY_PANIC)
                else:
                    self._alarmdecoder.device.send(key)

            except (CommError, AttributeError), err:
                self._alarmdecoder.app.logger.error('Error sending keypress to device', exc_info=True)

    def on_test(self, *args):
        """
        Handles test start events.

        :param args: Test arguments
        :type args: list
        """
        with self._alarmdecoder.app.app_context():
            try:
                self._test_open()
                time.sleep(0.5)
                self._test_config()
                self._test_send()
                self._test_receive()

            except Exception:
                current_app.logger.error('Error running device tests.', exc_info=True)

    def _test_open(self):
        """
        Tests opening the AlarmDecoder device.
        """
        results, details = 'PASS', ''

        try:
            self._alarmdecoder.close()
            self._alarmdecoder.open()

        except NoDeviceError, err:
            results, details = 'FAIL', '{0}: {1}'.format(err[0], err[1][1])
            current_app.logger.error('Error while testing device open.', exc_info=True)

        except Exception, err:
            results, details = 'FAIL', 'Failed to open the device: {0}'.format(err)
            current_app.logger.error('Error while testing device open.', exc_info=True)

        finally:
            self._alarmdecoder.broadcast('test', {'test': 'open', 'results': results, 'details': details})

    def _test_config(self):
        """
        Tests retrieving and saving the AlarmDecoder configuration.
        """
        def on_config_received(device):
            """Internal config event handler"""
            timer.cancel()
            self._alarmdecoder.broadcast('test', {'test': 'config', 'results': 'PASS', 'details': ''})
            if on_config_received in self._alarmdecoder.device.on_config_received:
                self._alarmdecoder.device.on_config_received.remove(on_config_received)

        def on_timeout():
            """Internal timeout handler for the configuration message"""
            self._alarmdecoder.broadcast('test', {'test': 'config', 'results': 'TIMEOUT', 'details': 'Test timed out.'})
            if on_config_received in self._alarmdecoder.device.on_config_received:
                self._alarmdecoder.device.on_config_received.remove(on_config_received)

        timer = threading.Timer(10, on_timeout)
        timer.start()

        try:
            panel_mode = Setting.get_by_name('panel_mode')
            keypad_address = Setting.get_by_name('keypad_address')
            address_mask = Setting.get_by_name('address_mask')
            lrr_enabled = Setting.get_by_name('lrr_enabled')
            zone_expanders = Setting.get_by_name('emulate_zone_expanders')
            relay_expanders = Setting.get_by_name('emulate_relay_expanders')
            deduplicate = Setting.get_by_name('deduplicate')

            zx = [x == u'True' for x in zone_expanders.value.split(',')]
            rx = [x == u'True' for x in relay_expanders.value.split(',')]

            self._alarmdecoder.device.mode = panel_mode.value
            self._alarmdecoder.device.address = keypad_address.value
            self._alarmdecoder.device.address_mask = int(address_mask.value, 16)
            self._alarmdecoder.device.emulate_zone = zx
            self._alarmdecoder.device.emulate_relay = rx
            self._alarmdecoder.device.emulate_lrr = lrr_enabled.value
            self._alarmdecoder.device.deduplicate = deduplicate.value

            self._alarmdecoder.device.on_config_received += on_config_received
            self._alarmdecoder.device.save_config()

        except Exception, err:
            timer.cancel()
            if on_config_received in self._alarmdecoder.device.on_config_received:
                self._alarmdecoder.device.on_config_received.remove(on_config_received)

            self._alarmdecoder.broadcast('test', {'test': 'config', 'results': 'FAIL', 'details': 'There was an error sending the command to the device.'})
            current_app.logger.error('Error while testing device config.', exc_info=True)

    def _test_send(self):
        """
        Tests keypress sending functionality.
        """
        def on_sending_received(device, status, message):
            """Internal event handler for key send events"""
            timer.cancel()
            if on_sending_received in self._alarmdecoder.device.on_sending_received:
                self._alarmdecoder.device.on_sending_received.remove(on_sending_received)

            results, details = 'PASS', ''
            if status != True:
                results, details = 'FAIL', 'Check wiring and that the correct keypad address is being used.'

            self._alarmdecoder.broadcast('test', {'test': 'send', 'results': results, 'details': details})

        def on_timeout():
            """Internal timeout for key send events"""
            self._alarmdecoder.broadcast('test', {'test': 'send', 'results': 'TIMEOUT', 'details': 'Test timed out.'})
            if on_sending_received in self._alarmdecoder.device.on_sending_received:
                self._alarmdecoder.device.on_sending_received.remove(on_sending_received)

        timer = threading.Timer(10, on_timeout)
        timer.start()

        try:
            self._alarmdecoder.device.on_sending_received += on_sending_received
            self._alarmdecoder.device.send("*\r")

        except Exception, err:
            timer.cancel()
            if on_sending_received in self._alarmdecoder.device.on_sending_received:
                self._alarmdecoder.device.on_sending_received.remove(on_sending_received)

            self._alarmdecoder.broadcast('test', {'test': 'send', 'results': 'FAIL', 'details': 'There was an error sending the command to the device.'})
            current_app.logger.error('Error while testing keypad communication.', exc_info=True)

    def _test_receive(self):
        """
        Tests message received events.
        """
        def on_message(device, message):
            """Internal event handler for message events"""
            timer.cancel()
            if on_message in self._alarmdecoder.device.on_message:
                self._alarmdecoder.device.on_message.remove(on_message)

            self._alarmdecoder.broadcast('test', {'test': 'recv', 'results': 'PASS', 'details': ''})

        def on_timeout():
            """Internal timeout for message events"""
            self._alarmdecoder.broadcast('test', {'test': 'recv', 'results': 'TIMEOUT', 'details': 'Test timed out.'})
            if on_message in self._alarmdecoder.device.on_message:
                self._alarmdecoder.device.on_message.remove(on_message)

        timer = threading.Timer(10, on_timeout)
        timer.start()

        try:
            self._alarmdecoder.device.on_message += on_message
            self._alarmdecoder.device.send("*\r")

        except Exception, err:
            timer.cancel()
            if on_message in self._alarmdecoder.device.on_message:
                self._alarmdecoder.device.on_message.remove(on_message)

            self._alarmdecoder.broadcast('test', {'test': 'recv', 'results': 'FAIL', 'details': 'There was an error sending the command to the device.'})
            current_app.logger.error('Error while testing keypad communication.', exc_info=True)

@decodersocket.route('/<path:remaining>')
def handle_socketio(remaining):
    """Socket.IO route"""
    try:
        socketio_manage(request.environ, {'/alarmdecoder': DecoderNamespace}, g.alarmdecoder)

    except Exception, err:
        current_app.logger.error("Exception while handling socketio connection", exc_info=True)

    return Response()
