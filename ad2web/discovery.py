import os
import socket
import struct
import sys
import threading
import uuid
import fcntl
import time

try:
    import netifaces
    has_netifaces = True
except ImportError:
    has_netifaces = False

from select import select
from httplib import HTTPResponse
from BaseHTTPServer import BaseHTTPRequestHandler
from StringIO import StringIO

from .extensions import db
from .settings.models import Setting


class DiscoveryServer(threading.Thread):
    MCAST_PORT = 1900
    MCAST_ADDRESS = '239.255.255.250'

    RESPONSE_MESSAGE = ('HTTP/1.1 200 OK\r\n' +
                        'CACHE-CONTROL: max-age = %(CACHE_CONTROL)i\r\n' +
                        'EXT:\r\n' +
                        'LOCATION: %(LOCATION)s\r\n' +
                        'SERVER: Linux/1.0 UPnP/1.1 AlarmDecoder/1.0\r\n' +
                        'ST: %(ST)s\r\n' +
                        'USN: %(USN)s\r\n' +
                        '\r\n')

    NOTIFY_MESSAGE = ('NOTIFY * HTTP/1.1\r\n' +
                            'HOST: 239.255.255.250:1900\r\n' +
                            'CACHE-CONTROL: max-age = %(CACHE_CONTROL)i\r\n' +
                            'LOCATION: %(LOCATION)s\r\n' +
                            'NT: %(NT)s\r\n' +
                            'NTS: %(NTS)s\r\n' +
                            'SERVER: Linux/1.0 UPnP/1.1 AlarmDecoder/1.0\r\n' +
                            'USN: %(USN)s\r\n' +
                            '\r\n')

    def __init__(self, decoder):
        threading.Thread.__init__(self)

        self._decoder = decoder
        self._running = False

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        sock.bind((self.MCAST_ADDRESS, self.MCAST_PORT))

        mreq = struct.pack('4sl', socket.inet_aton(self.MCAST_ADDRESS), socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        self._socket = sock
        self._expiration_time = 600
        self._current_port = int(os.getenv('AD_LISTENER_PORT', '5000'))
        self._current_ip_address = self._get_ip_address()
        self._device_uuid = self._get_device_uuid()
        self._announcement_timestamp = 0

        with self._decoder.app.app_context():
            self._decoder.app.logger.info("Discovery running: loc={0}:{1}, uuid={2}".format(self._current_ip_address, self._current_port, self._device_uuid))

    def stop(self):
        """
        Stops the discovery thread.
        """
        self._running = False

    def run(self):
        """
        Main thread loop
        """
        self._running = True

        while self._running:
            with self._decoder.app.app_context():
                try:
                    rl, wl, xl = select([self._socket], [], [])
                    for s in rl:
                        data, addr = s.recvfrom(4096)

                        request = DiscoveryRequest(data)

                        self._handle_request(request, addr)

                        # TODO: Likely needs to be separate from this loop.
                        self._update()
                        
                except Exception, err:
                    self._decoder.app.logger.error('Error in DiscoveryServer: {0}'.format(err), exc_info=True)

    def _handle_request(self, request, addr):
        if request.error_code:
            self._decoder.app.logger.warning('Discovery: Error {0} - {1}'.format(request.error_code, request.error_message))
            return

        if self._match_search_request(request):
            response_message = self._create_discovery_response(request)
            self._send_message(response_message, addr)

    def _update(self):
        address = self._get_ip_address()
        if address != self._current_ip_address:
            # TODO: cancel
            # TODO: notify
            self._current_ip_address = address

        # NOTE: Disabled until I have time to fully implement.  SmartThings doesn't seem to need it, so whatever.
        # if self._announcement_timestamp + self._expiration_time < time.time():
        #     with self._decoder.app.app_context():
        #         self._decoder.app.logger.debug('sending announcement')

        #     notify_messages = self._create_notify_message()
        #     for m in notify_messages:
        #         self._send_message(m, ('239.255.255.250', 1900))

        #     self._announcement_timestamp = time.time()

    def _create_discovery_response(self, request):
        loc = 'http://{0}:{1}/static/device_description.xml'.format(self._current_ip_address, self._current_port)
        usn = 'uuid:{0}'.format(self._device_uuid)

        return self.RESPONSE_MESSAGE % dict(ST=request.headers['ST'], LOCATION=loc, USN=usn, CACHE_CONTROL=self._expiration_time)

    def _create_notify_message(self):
        loc = 'http://{0}:{1}'.format(self._current_ip_address, self._current_port)
        usn = 'uuid:{0}'.format(self._device_uuid)

        msg1 = self.NOTIFY_MESSAGE % dict(NT="upnp:rootdevice", LOCATION=loc, USN=usn + "::upnp:rootdevice", NTS="ssdp:alive", CACHE_CONTROL=self._expiration_time)
        msg2 = self.NOTIFY_MESSAGE % dict(NT=usn, LOCATION=loc, USN=usn, NTS="ssdp:alive", CACHE_CONTROL=self._expiration_time)
        msg3 = self.NOTIFY_MESSAGE % dict(NT="urn:schemas-upnp-org:device:AlarmDecoder:1", LOCATION=loc, USN=usn + "::urn:schemas-upnp-org:device:AlarmDecoder:1", NTS="ssdp:alive", CACHE_CONTROL=self._expiration_time)

        return (msg1, msg2, msg3)

    def _send_message(self, message, addr):
        with self._decoder.app.app_context():
            self._decoder.app.logger.debug('sending message to {0}: {1}'.format(addr, message))

        for i in xrange(2): # NOTE: Sending multiple times due to UDP's unreliability.
            self._socket.sendto(message, addr)
            time.sleep(0.1)

    def _match_search_request(self, request):
        ret = False
        if request.command == 'M-SEARCH' and \
            request.path == '*' and \
            request.headers['MAN'] == '"ssdp:discover"' and \
            ('AlarmDecoder' in request.headers['ST'] or request.headers['ST'].startswith('ssdp:all')):
            ret = True

        return ret

    def _get_device_uuid(self):
        device_uuid = Setting.get_by_name('device_uuid').value

        if not device_uuid:
            with self._decoder.app.app_context():
                self._decoder.app.logger.debug('Generating new UUID..')

            device_uuid = str(uuid.uuid1())

            uuid_setting = Setting(name='device_uuid')
            uuid_setting.value = device_uuid
            db.session.add(uuid_setting)
            db.session.commit()

        return device_uuid

    def _get_ip_address(self):
        address = None
        if has_netifaces:
            gateways = netifaces.gateways()

            default_gateway = gateways['default'][netifaces.AF_INET]
            addresses = netifaces.ifaddresses(default_gateway[1])
            address = addresses[netifaces.AF_INET][0]['addr']

        else:
            ifname = 'eth0' # HACK: how do we work around this?

            # pulled from: https://stackoverflow.com/a/24196955
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            address = socket.inet_ntoa(fcntl.ioctl(
                            s.fileno(),
                            0x8915,  # SIOCGIFADDR
                            struct.pack('256s', ifname[:15])
                        )[20:24])

        return address

class DiscoveryRequest(BaseHTTPRequestHandler):
    def __init__(self, request_text):
        self.rfile = StringIO(request_text)
        self.raw_requestline = self.rfile.readline()
        self.error_code = self.error_message = None
        self.parse_request()

    def send_error(self, code, message):
        self.error_code = code
        self.error_message = message

class DiscoveryResponse(HTTPResponse):
    def __init__(self, response_text):
        self.fp = StringIO(response_text)
        self.debuglevel = 0
        self.strict = 0
        self.msg = None
        self._method = None
        self.begin()
