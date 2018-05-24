# -*- coding: utf-8 -*-

import os
import sys
import time
import datetime
import traceback
import threading
import binascii

try:
    import miniupnpc
    has_upnp = True
except ImportError:
    has_upnp = False

from socketio import socketio_manage
from socketio.namespace import BaseNamespace
from socketio.mixins import BroadcastMixin
from socketio.server import SocketIOServer
from socketioflaskdebug.debugger import SocketIODebugger

from sqlalchemy.orm.exc import NoResultFound

from flask import Blueprint, Response, request, g, current_app
import jsonpickle

from OpenSSL import SSL
from alarmdecoder import AlarmDecoder
from alarmdecoder.devices import SocketDevice, SerialDevice
from alarmdecoder.util import NoDeviceError, CommError

from flask import flash
from .extensions import db, mail
from .notifications import NotificationSystem, NotificationThread
from .settings.models import Setting
from .certificate.models import Certificate
from .updater import Updater
from .updater.models import FirmwareUpdater

from .notifications.models import NotificationMessage
from .notifications.constants import (ARM, DISARM, POWER_CHANGED, ALARM, ALARM_RESTORED,
                                        FIRE, BYPASS, BOOT, LRR, CONFIG_RECEIVED, ZONE_FAULT,
                                        ZONE_RESTORE, LOW_BATTERY, PANIC, RELAY_CHANGED,
                                        LRR, READY, CHIME, DEFAULT_EVENT_MESSAGES)

from .cameras import CameraSystem
from .cameras.models import Camera
from .discovery import DiscoveryServer
from .upnp import UPNPThread

from .setup.constants import SETUP_COMPLETE

from .utils import user_is_authenticated, INSTANCE_FOLDER_PATH
from .mailer import Mailer
from .exporter import Exporter

EVENT_MAP = {
    ARM: 'on_arm',
    DISARM: 'on_disarm',
    POWER_CHANGED: 'on_power_changed',
    ALARM: 'on_alarm',
    ALARM_RESTORED: 'on_alarm_restored',
    FIRE: 'on_fire',
    BYPASS: 'on_bypass',
    BOOT: 'on_boot',
    LRR: 'on_lrr_message',
    READY: 'on_ready_changed',
    CHIME: 'on_chime_changed',
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

    return SocketIOServer(('', int(os.getenv('AD_LISTENER_PORT', '5000'))), debugged_app, resource="socket.io")

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
            self.firmware_file = None
            self.firmware_length = -1

            self.trigger_reopen_device = False
            self.trigger_restart = False

            self._last_message = None
            self._device_baudrate = 115200
            self._device_type = None
            self._device_location = None
            self._event_thread = DecoderThread(self)
            self._discovery_thread = None
            self._notification_thread = None
            self._notifier_system = None
            self._upnp_thread = None
            self._internal_address_mask = 0xFFFFFFFF
            self.last_message_received = None

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
        self._discovery_thread.start()
        self._notification_thread.start()
        self._exporter_thread.start()
        if has_upnp:
            self._upnp_thread.start()

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
        self._discovery_thread.stop()
        self._notification_thread.stop()
        self._exporter_thread.stop()
        if has_upnp:
            self._upnp_thread.stop()

        if restart:
            try:
                self._event_thread.join(5)
                self._version_thread.join(5)
                self._camera_thread.join(5)
                self._discovery_thread.join(5)
                self._notification_thread.join(5)
                self._exporter_thread.join(5)
                if has_upnp:
                    self._upnp_thread.join(5)

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

            current_app.config['MAIL_SERVER'] = Setting.get_by_name('system_email_server',default='localhost').value
            current_app.config['MAIL_PORT'] = Setting.get_by_name('system_email_port',default=25).value
            current_app.config['MAIL_USE_TLS'] = Setting.get_by_name('system_email_tls',default=False).value
            current_app.config['MAIL_USERNAME'] = Setting.get_by_name('system_email_username',default='').value
            current_app.config['MAIL_PASSWORD'] = Setting.get_by_name('system_email_password',default='').value
            current_app.config['MAIL_DEFAULT_SENDER'] = Setting.get_by_name('system_email_from',default='youremail@example.com').value

            mail.init_app(current_app)

            # Generate a new session key if it doesn't exist.
            secret_key = Setting.get_by_name('secret_key')
            if secret_key.value is None:
                secret_key.value = binascii.hexlify(os.urandom(24))
                db.session.add(secret_key)
                db.session.commit()

            current_app.secret_key = secret_key.value

            self.version = self.updater._components['AlarmDecoderWebapp'].version
            current_app.jinja_env.globals['version'] = self.version
            current_app.logger.info('AlarmDecoder Webapp booting up - v{0}'.format(self.version))

            # Expose wrapped is_authenticated to jinja.
            current_app.jinja_env.globals['user_is_authenticated'] = user_is_authenticated

            # HACK: giant hack.. fix when we know this works.
            self.updater._components['AlarmDecoderWebapp']._db_updater.refresh()

            if self.updater._components['AlarmDecoderWebapp']._db_updater.needs_update:
                current_app.logger.debug('Database needs updating!')

                self.updater._components['AlarmDecoderWebapp']._db_updater.update()
            else:
                current_app.logger.debug('Database is good!')

            if device_type:
                self.trigger_reopen_device = True

            self._notifier_system = NotificationSystem()
            self._camera_thread = CameraChecker(self)
            self._discovery_thread = DiscoveryServer(self)
            self._notification_thread = NotificationThread(self)
            self._exporter_thread = ExportChecker(self)
            self._version_thread = VersionChecker(self)

            if has_upnp:
                self._upnp_thread = UPNPThread(self)

    def open(self, no_reader_thread=False):
        """
        Opens the AlarmDecoder device.
        """
        with self.app.app_context():
            self._device_type = Setting.get_by_name('device_type').value
            self._device_location = Setting.get_by_name('device_location').value
            self._internal_address_mask = int(Setting.get_by_name('internal_address_mask', 'FFFFFFFF').value, 16)

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
                        try:
                            ca_cert = Certificate.query.filter_by(name='AlarmDecoder CA').one()
                            internal_cert = Certificate.query.filter_by(name='AlarmDecoder Internal').one()

                            device.ssl = True
                            device.ssl_ca = ca_cert.certificate_obj
                            device.ssl_certificate = internal_cert.certificate_obj
                            device.ssl_key = internal_cert.key_obj
                        except NoResultFound, err:
                            self.app.logger.warning('No certificates found: %s', err[0], exc_info=True)
                            raise

                    self.device = AlarmDecoder(device)
                    self.device.internal_address_mask = self._internal_address_mask

                    self.bind_events()
                    self.device.open(baudrate=self._device_baudrate, no_reader_thread=no_reader_thread)

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
            self.remove_events()
            self.device.close()
            del self.device

    def bind_events(self):
        """
        Binds the internal event handlers so that we can handle events from the
        AlarmDecoder library.
        """
        build_event_handler = lambda ftype: lambda sender, **kwargs: self._handle_event(ftype, sender, **kwargs)
        build_message_handler = lambda ftype: lambda sender, **kwargs: self._on_message(ftype, sender, **kwargs)

        self.device.on_message += build_message_handler('panel')
        self.device.on_lrr_message += build_message_handler('lrr')
        self.device.on_ready_changed += build_message_handler('ready')
        self.device.on_chime_changed += build_message_handler('chime')
        self.device.on_rfx_message += build_message_handler('rfx')
        try:
            self.device.on_aui_message += build_message_handler('aui')
        except AttributeError, ex:
            self.app.logger.warning('Could not bind event "on_aui_message": alarmdecoder library is probably out of date.')

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

    def remove_events(self):
        """
        Clear the internal event handlers so that we don't run into any issues.
        """
        try:
            self.device.on_message.clear()
            self.device.on_lrr_message.clear()
            self.device.on_ready_changed.clear()
            self.device.on_chime_changed.clear()
            self.device.on_rfx_message.clear()
            try:
                self.device.on_aui_message.clear()
            except AttributeError, ex:
                self.app.logger.warning('Could not remove event "on_aui_message": alarmdecoder library is probably out of date.')
    
            self.device.on_expander_message.clear()
    
            self.device.on_open.clear()
            self.device.on_close.clear()
    
            # Clear mapped events.
            for event, device_event_name in EVENT_MAP.iteritems():
                try:
                    device_handler = getattr(self.device, device_event_name)
                    device_handler.clear()
    
                except AttributeError, ex:
                    self.app.logger.warning('Could not clear event "%s": alarmdecoder library is probably out of date.', device_event_name)
    
        except AttributeError, ex:
            self.app.logger.warning("Could not clear events: alarmdecoder library is probably out of date.")

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
            message = str(kwargs.get('message', None))

            if ftype == 'panel':
                self.last_message_received = message

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
            authenticated = sock.session.get('authenticated', False)

            if authenticated:
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
    TIMEOUT = 60
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
        self.last_check_time = float(Setting.get_by_name('version_checker_last_check_time', default=0).value)
        self.version_checker_timeout = int(Setting.get_by_name('version_checker_timeout', default=600).value)
        self.disable_version_checker = Setting.get_by_name('version_checker_disable', default=False).value

    def stop(self):
        """
        Stops the thread.
        """

        self._running = False

    def setTimeout(self, timeout):
        """
        Sets the thread sleep time.
        """

        self._decoder.app.logger.info('Updating version check thread timeout to: {0} seconds'.format(timeout))
        self.version_checker_timeout = int(timeout)

    def setDisable(self, disable):
        """
        Sets the disable flag of the thread.
        """

        self._decoder.app.logger.info('Updating version check enable/disable to: {0}'.format("Enabled" if not disable else "Disabled"))
        self.disable_version_checker = disable

    def run(self):
        """
        The thread processing loop.
        """
        self._running = True

        while self._running:
            with self._decoder.app.app_context():
                if not self.disable_version_checker:
                    try:
                        check_time = time.time()
                        if check_time > self.last_check_time + self.version_checker_timeout:
                            self._decoder.app.logger.info('Checking for version updates - last check at: {0}'.format(datetime.datetime.fromtimestamp(self.last_check_time).strftime('%m-%d-%Y %H:%M:%S')))
                            self._decoder.updates = self._updater.check_updates()
                            update_available = not all(not needs_update for component, (needs_update, branch, revision, new_revision, status, project_url) in self._decoder.updates.iteritems())

                            current_app.jinja_env.globals['update_available'] = update_available
                            current_app.jinja_env.globals['firmware_update_available'] = self._updater.check_firmware()

                            self.last_check_time = check_time
                            version_checker_last_check_time = Setting.get_by_name('version_checker_last_check_time')
                            version_checker_last_check_time.value = int(self.last_check_time)

                            db.session.add(version_checker_last_check_time)
                            db.session.commit()


                    except Exception, err:
                        self._decoder.app.logger.error('Error in VersionChecker: {0}'.format(err), exc_info=True)

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
                try:
                    self._cameras.refresh_camera_ids()
                    for n in self._cameras.get_camera_ids():
                        self._cameras.write_image(n)

                except Exception, err:
                    self._decoder.app.logger.error('Error in CameraChecker: {0}'.format(err), exc_info=True)

            time.sleep(self.TIMEOUT)

class ExportChecker(threading.Thread):
    """
    Thread responsible for sending out scheduled system exports
    """

    TIMEOUT = 600

    def __init__(self, decoder):
        threading.Thread.__init__(self)
        self._decoder = decoder
        self._running = False
        self.first_run = True
        self.local_storage = None
        self.prepParams()
        

    def prepParams(self):
        self.server = Setting.get_by_name('system_email_server', default='localhost').value
        self.port = Setting.get_by_name('system_email_port', default=25).value
        self.tls = Setting.get_by_name('system_email_tls', default=False).value
        self.auth_required = Setting.get_by_name('system_email_auth',default=False).value
        self.username = Setting.get_by_name('system_email_username', default=None).value
        self.password = Setting.get_by_name('system_email_password', default=None).value
        self.send_from = Setting.get_by_name('system_email_from',default='root@alarmdecoder').value
        self.subject = "AlarmDecoder Settings Database Backup"
        self.body = "AlarmDecoder Settings Database Backup\r\n"
        self.to = []
        self.to.append(Setting.get_by_name('export_mailer_to', default=None).value)

        self._mailer = Mailer(self.server, self.port, self.tls, self.auth_required, self.username, self.password)
        self._exporter = Exporter()

        self.export_frequency = Setting.get_by_name('export_frequency', default=0).value
        self.local_storage = Setting.get_by_name('enable_local_file_storage', default=False).value
        self.local_path = Setting.get_by_name('export_local_path', default=os.path.join(INSTANCE_FOLDER_PATH, 'exports')).value
        self.email_enable = Setting.get_by_name('export_email_enable', default=False).value
        self.days_to_keep = Setting.get_by_name('days_to_keep', default=7).value
        self.last_check_time = int(Setting.get_by_name('export_last_check_time', default=0).value)

        self._decoder.app.logger.info('Set export parameters to:  server {0} port {1} tls {2} auth {3} from {4} frequency {5} store files {6} storage path {7} days to keep files {8} email enable {9}'.format(self.server, self.port, self.tls, self.auth_required, self.send_from, self.export_frequency, self.local_storage, self.local_path, self.days_to_keep, self.email_enable))

    def stop(self):
        """
        Stops the thread.
        """

        self._running = False

    def updateFrequency(self, frequency):
        self.export_frequency = frequency

    def addTo(self, to):
        self.to.append(to)

    def updateUsername(self, username):
        self._mailer.updateUsername(username)

    def updatePassword(self, password):
        self._mailer.updatePassword(password)

    def updateFrom(self, email_from):
        self.send_from = email_from

    def updateServer(self, server):
        self._mailer.updateServer(server)

    def updatePort(self, port):
        self._mailer.updatePort(port)

    def updateTls(self, tls):
        self._mailer.updateTls(tls)

    def updateAuth(self, auth):
        self._mailer.updateAuth(auth)

    def updateSubject(self, subject):
        self.subject = subject

    def updateBody(self, body):
        self.body = body

    def run(self):
        """
        The thread processing loop.
        """
        self._running = True

        while self._running:
            with self._decoder.app.app_context():
                if self.export_frequency > 0:
                    try:
                        check_time = time.time()
                        if check_time > self.last_check_time + self.export_frequency:
                            self._decoder.app.logger.info('Checking if we need to export settings.')
                            if not self.first_run:
                                self._exporter.exportSettings()
                                full_path = self._exporter.writeFile()

                                files = []
                                files.append(full_path)
                                if self.email_enable and full_path is not None:
                                    self._decoder.app.logger.info('Sending export email: {0} - {1}'.format(self.to, files))
                                    self._mailer.send_mail(self.send_from, self.to, self.subject, self.body, files)

                                if not self.local_storage:
                                    self._decoder.app.logger.info('Not keeping export on disk - {0}'.format(full_path))
                                    self._exporter.removeFile()

                                self.last_check_time = check_time
                                export_last_check_time = Setting.get_by_name('export_last_check_time')
                                export_last_check_time.value = int(self.last_check_time)

                                db.session.add(export_last_check_time)
                                db.session.commit()
                            else:
                                self.first_run = False
                            
                            self._exporter.removeOldFiles(self.days_to_keep)
                    
                    except Exception, err:
                        self._decoder.app.logger.error('Error in ExportChecker: {0}'.format(err), exc_info=True)

            time.sleep(self.TIMEOUT)

class DecoderNamespace(BaseNamespace, BroadcastMixin):
    """
    Socket.IO namespace
    """

    def initialize(self):
        """
        Initializes the namespace.
        """
        self._alarmdecoder = self.request.get('alarmdecoder', None)
        self._request = self.request.get('request', None)

    def get_initial_acl(self):
        return ['recv_connect']

    def recv_connect(self):
        with self._alarmdecoder.app.app_context():
            try:
                with self._alarmdecoder.app.request_context(self.environ):

                    session_interface = self._alarmdecoder.app.session_interface
                    session = session_interface.open_session(self._alarmdecoder.app, self._request)
                    user_id = session.get('user_id', None)

                    # check setup complete
                    setup_stage = Setting.get_by_name('setup_stage').value

                    if (setup_stage and setup_stage != SETUP_COMPLETE) or user_id:
                        self.add_acl_method('on_keypress')
                        self.add_acl_method('on_firmwareupload')
                        self.add_acl_method('on_test')

                        self.socket.session['authenticated'] = True

            except Exception, err:
                self._alarmdecoder.app.logger.error('Websocket connection failed: {0}'.format(err))

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

    def on_firmwareupload(self, *args):
        with self._alarmdecoder.app.app_context():
            reopen_with_reader = False

            try:
                # Save the original configuration for newer versions of the library.
                enable_reconfiguring = False
                orig_config_string = ''
                if callable(getattr(self._alarmdecoder.device, 'get_config_string', None)):
                    enable_reconfiguring = True
                    orig_config_string = self._alarmdecoder.device.get_config_string()

                current_app.logger.info('Beginning firmware upload - filename=%s', self._alarmdecoder.firmware_file)
                firmware_updater = FirmwareUpdater(filename=self._alarmdecoder.firmware_file, length=self._alarmdecoder.firmware_length)
                firmware_updater.update()

                if firmware_updater.completed:
                    if enable_reconfiguring:
                        # Make sure our previous config gets reset since the firmware update will clear it.
                        self._alarmdecoder.broadcast('firmwareupload', { 'stage': 'STAGE_CONFIGURE' });
                        time.sleep(10)
                        self._alarmdecoder.device.send("C{0}\r".format(orig_config_string))
                        time.sleep(5)
                        current_app.jinja_env.globals['firmware_update_available'] = False

                    self._alarmdecoder.broadcast('firmwareupload', { 'stage': 'STAGE_FINISHED' });

                    self._alarmdecoder.firmware_file = None
                    self._alarmdecoder.firmware_length = -1
                    reopen_with_reader = True

            except Exception, err:
                current_app.logger.error('Error uploading firmware: %s', err)

                self._alarmdecoder.broadcast('firmwareupload', { 'stage': 'STAGE_ERROR', 'error': 'Error uploading firmware.' })

            finally:
                self._alarmdecoder.close()
                self._alarmdecoder.open(no_reader_thread=not reopen_with_reader)

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
        socketio_manage(request.environ, {'/alarmdecoder': DecoderNamespace}, { "alarmdecoder": g.alarmdecoder, "request": request})

    except Exception, err:
        current_app.logger.error("Exception while handling socketio connection", exc_info=True)

    return Response()
